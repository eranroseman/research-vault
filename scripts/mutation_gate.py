"""No-new-survivors mutation gate over mutmut 3.7.0.

Invoked explicitly as `python scripts/mutation_gate.py` — no shebang on purpose
(EXE001 fires on a shebang in a non-executable file, and nothing execs this directly).

Gate mode (default): mutation-test the research_vault modules changed since
--base, fail (exit 1) on any survivor whose key is absent from the committed
baseline. --update-baseline: measure every research_vault module and rewrite the
baseline file with every current survivor; REFUSES to write if any module did
not measure cleanly (a module mutmut did not finish has no survivor list, and an
empty contribution is not a clean one -- writing it would put an undetectable
hole in the baseline).

--out-dir (update-baseline only): per-module records (stdout, the derived
survivor keys and counts as JSON, exit code + class) written as each module
finishes, so a blanket run killed partway through resumes instead of restarting.
A recorded "0 ok" is reused without re-running; anything else -- no record, an
unparseable exit file, a recorded failure, or a record whose own body lists
mutants without a verdict -- re-runs and overwrites. The
baseline is assembled from the RECORDS, not from mutants/: mutmut's mutant ids
renumber on any edit and mutants/ regenerates, so only the derived keys are
durable. --only RELPATH (repeatable, update-baseline only) narrows which modules
this invocation runs; the write still requires every module to hold a usable
record, and names the ones that do not. A recorded ok still wins over --only:
to redo such a module, delete its .exit record first. Gate mode ignores
--out-dir.

Every module gets a class: "ok" (mutmut exited 0 and every selected mutant has
a verdict) or "error" (a non-zero exit, no mutants/<relpath>.meta afterwards, or
any mutant WITHOUT a verdict: "not checked" / "interrupted" -- mutmut swallows
a KeyboardInterrupt and still exits 0, leaving null codes behind -- and
"suspicious" / "segfault", which are the absence of a verdict rather than one:
suspicious is mutmut's fallback for an exit code it cannot classify, e.g.
pytest's usage-error 4, the node-id re-escaping defect's signature; segfault is
-9, the SIGKILL an OOM killer sends, or -11). An error is never zero survivors:
it fails the gate and blocks the baseline write, and the module's class line
names the offending mutant ids so the module can be redone with --only once
the cause is fixed.

How mutmut is driven. Each module is one invocation of
scripts/mutmut_shims/run_mutmut.py (the launcher; see its header) with the name
pattern `research_vault.<stem>.*` and --max-children passed through, cwd at the
repo root because mutmut reads [tool.mutmut] from pyproject.toml in the cwd.
mutmut copies source_paths + tests/ + pyproject.toml + also_copy into mutants/,
generates every module's mutants there (once; cached by mtime), runs the whole
suite in-process from mutants/ to learn which tests reach which function (the
stats phase, cached in mutants/mutmut-stats.json), then forks one child per
selected mutant running only the tests that reached that function. Results land
in mutants/<relpath>.meta as `exit_code_by_key` and are classified through
mutmut's own status_by_exit_code (0 survived; 1/3 killed; 5/33 no tests; 34
skipped; 24/152/255/-24/36 timeout; 37 caught by type check; -9/-11 segfault;
2 interrupted; null not checked; any other code suspicious). A timeout or a
type-check catch is a verdict the mutant caused: counted and reported by name
(mutmut id and key), never a survivor, never folded into killed, and no change
to the exit code in either mode. Suspicious and segfault are not verdicts and
class the module error (above), which fails the gate and blocks the write.

Two mutmut cache limits to know. (1) The stats cache re-collects only for NEW
test names: an edited test body does not refresh which functions it reaches,
so a test that starts covering a function keeps reading "no tests" for that
function's mutants until mutants/ is deleted. (2) Non-.py files under
source_paths are copied once; research_vault/templates is therefore listed in
also_copy so it refreshes every invocation, but a deleted file lingers.
`rm -rf mutants/` is the reset for both; CI starts from nothing.

Known measurement limit: coverage exercised only through a subprocess (a test
running `python -m research_vault ...`, or a hook script) is invisible to the
in-process stats phase, so those mutants read "no tests" -- never "survived".
The per-module line and the end-of-run summary carry the "no tests" count so
that gap stays visible rather than reading as strength.

Stale-bytecode guard. PYTHONDONTWRITEBYTECODE=1 blocks WRITING a pyc, not
loading one: CPython validates a timestamp pyc on (mtime, size) alone, and a
same-length edit inside one mtime second reuses the previous bytecode. So
before every invocation this sweeps __pycache__ under research_vault/, tests/
and mutants/, and keeps the env var as belt. mutmut never edits the source
(schemata live in mutants/), and the gate proves it: research_vault/ and tests/
are hashed before and after every invocation and a difference aborts the run.

Baseline keys exclude line numbers and mutmut's positional mutant ids on
purpose: `<relpath>::func/<name>::<mutation>` stays stable across unrelated
edits, where <name> is the function (or `<Class>.<method>`) from mutmut's
orig_function_and_class_names_from_key, and <mutation> is the `-`/`+` lines of
mutmut's get_diff_for_mutant unified diff -- file and hunk headers and context
dropped, each line verbatim with its marker, joined by a literal backslash-n so
a multi-line hunk is still one baseline line. What such a key can answer:
"no NEW survivor" -- a survivor whose text was already baselined is not news.
What it cannot answer: "the rewrite fixed the old ones" -- a function rewritten
on a branch that still admits a baselined mutation text reads ok, and a
baselined key whose function no longer exists stays in the file unnoticed until
the next --update-baseline. mutmut does not mutate module scope, so the
mutate4py-era `<relpath>::module::<mutation>` keys can no longer be produced;
baseline_keys() still tolerates them as lines. A written baseline starts with a
`#` header line; baseline_keys() skips comment and blank lines.

Per-child address-space cap. --child-address-space (default 4GiB; a plain byte
count, or a decimal with a MiB or GiB suffix) is applied to the mutmut process
through resource.setrlimit(RLIMIT_AS) in a preexec_fn, and mutmut forks its
per-mutant children from that process, so every child inherits it. Why: a
cgroup MemoryMax bounds the SUM over the children, so a runaway-allocation
mutant (measured 2026-09-14 in selectors.py: one child at 2.0 GB, then five at
1.6-2.2 GB) takes the whole run down by OOM-kill; under a per-process cap the
same mutant raises MemoryError, pytest exits 1, and the mutant counts as
killed. Sizing: children x cap under the machine's memory bound is the
guarantee that the OOM killer never fires; a looser product only holds while
at most one child runs away at a time. False-kill cost: only a test that
genuinely needs more than the cap, and the suite runs in under 1 GB.

Git isolation. Measured 2026-09-14T02:13Z: a scaffold.py mutant with its vault
argument mutated to a non-vault ran the vault-hook install with cwd inside
mutants/, `git rev-parse --git-path hooks/pre-commit` walked up to this
repository, and the vault pre-commit template landed in the shared .git/hooks
-- killed as a mutant, escaped as a side effect, and blocked every commit until
removed by hand. So before every invocation the gate makes mutants/ its own
git repository (`git init --template=` when mutants/.git is absent; the empty
template keeps a user's init.templateDir from seeding hooks into it) and
exports GIT_CEILING_DIRECTORIES=<repo root> to the mutmut process: discovery
from anywhere under mutants/ stops at mutants/.git, and from anywhere else
under the root it fails loudly instead of reaching this repository (the root
itself is not below the ceiling, so mutmut's own git calls from the root still
work, and tmp_path repositories are outside it). A core.hooksPath override for
every child was measured and rejected: it sends the hook the UNMUTATED
scaffold tests install to one shared directory, 9 of them fail on the hook's
location, and that hook would then run on every commit any child makes.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import resource
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import ModuleType

ROOT = Path(__file__).resolve().parent.parent  # repo root
SHIMS = ROOT / "scripts" / "mutmut_shims"
LAUNCHER = SHIMS / "run_mutmut.py"
# The trees mutmut must leave alone (hashed) and where stale bytecode could
# hide (swept, together with mutants/).
SOURCE_TREES = ("research_vault", "tests")
# The absence of a verdict, not a mutant outcome: any of these makes the
# module an error (see the header).
NO_VERDICT_STATUSES = (
    "not checked",
    "check was interrupted by user",
    "suspicious",
    "segfault",
)
# Verdicts the mutant caused, reported by name and never a survivor.
BY_NAME_STATUSES = ("timeout", "caught by type check")
DEFAULT_ADDRESS_SPACE = "4GiB"
_SIZE_UNITS = {"MiB": 1 << 20, "GiB": 1 << 30}


class SourceTreeChangedError(RuntimeError):
    """research_vault/ or tests/ differed after a mutmut invocation."""


@dataclass
class ModuleResult:
    survivors: set[str]
    counts: dict[str, int]
    # (status, mutmut id, key) for every BY_NAME_STATUSES verdict.
    flagged: list[tuple[str, str, str]] = field(default_factory=list)
    # (status, mutmut id) for every NO_VERDICT_STATUSES code: the module is an error.
    no_verdict: list[tuple[str, str]] = field(default_factory=list)


def _mutmut(root: Path) -> ModuleType:
    # Imported lazily and from the repo root: mutmut 3.7.0 loads its config at
    # import time from pyproject.toml in the CWD, and every reader in it
    # resolves mutants/ relative to the cwd too.
    with contextlib.chdir(root):
        import mutmut.__main__ as mm
    return mm


def mutation_text(diff: str) -> str:
    lines = diff.splitlines()
    # unified_diff's two file-header lines (`--- path`, `+++ path`) come first
    # and are dropped by position, so a removed code line that itself begins
    # with "--" inside a hunk is never mistaken for one.
    if lines[:1] and lines[0].startswith("---"):
        lines = lines[1:]
    if lines[:1] and lines[0].startswith("+++"):
        lines = lines[1:]
    body = [
        line.rstrip()
        for line in lines
        if line[:1] in ("-", "+") and not line.startswith("@@")
    ]
    return "\\n".join(body)


def mutation_key(relpath: str, mutant_name: str, diff: str) -> str:
    mm = _mutmut(ROOT)
    func, cls = mm.orig_function_and_class_names_from_key(mutant_name)
    name = f"{cls}.{func}" if cls else func
    return f"{relpath}::func/{name}::{mutation_text(diff)}"


def read_module_results(relpath: str, root: Path = ROOT) -> ModuleResult:
    """Everything the gate needs from mutants/<relpath>.meta, keyed durably.
    Raises FileNotFoundError when there is no .meta: no measurement must never
    read as zero survivors."""
    meta_path = root / "mutants" / f"{relpath}.meta"
    exit_code_by_key: dict[str, int | None] = json.loads(
        meta_path.read_text(encoding="utf-8")
    )["exit_code_by_key"]
    mm = _mutmut(root)
    result = ModuleResult(survivors=set(), counts={})
    with contextlib.chdir(root):
        for name, code in exit_code_by_key.items():
            status = mm.status_by_exit_code[code]
            result.counts[status] = result.counts.get(status, 0) + 1
            if status in NO_VERDICT_STATUSES:
                result.no_verdict.append((status, name))
                continue
            if status not in ("survived", *BY_NAME_STATUSES):
                continue
            key = mutation_key(
                relpath, name, mm.get_diff_for_mutant(name, path=relpath)
            )
            if status == "survived":
                result.survivors.add(key)
            else:
                result.flagged.append((status, name, key))
    return result


def new_survivors(found: set[str], baseline: set[str]) -> set[str]:
    return found - baseline


def baseline_keys(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    }


def changed_modules(base: str, cwd: Path = ROOT) -> list[str]:
    # --relative + a cwd-relative pathspec, both resolved from the repo root: a
    # stale core/-prefixed pathspec here matches nothing and kills the gate silently.
    diff = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "--relative",
            f"{base}...HEAD",
            "--",
            "research_vault/*.py",
        ],
        capture_output=True,
        text=True,
        check=True,
        cwd=cwd,
    ).stdout.split()
    return sorted(
        p
        for p in diff
        if p.endswith(".py") and not p.endswith("__init__.py") and (cwd / p).exists()
    )


def _all_modules() -> list[str]:
    return sorted(
        f"research_vault/{p.name}"
        for p in (ROOT / "research_vault").glob("*.py")
        if p.name != "__init__.py"
    )


def _sweep_pycache(root: Path) -> None:
    for tree in (*SOURCE_TREES, "mutants"):
        for cache in (root / tree).rglob("__pycache__"):
            shutil.rmtree(cache, ignore_errors=True)


def _tree_digest(root: Path) -> dict[str, str]:
    """Per-file content hash of the source trees, __pycache__ excluded."""
    digest: dict[str, str] = {}
    for tree in SOURCE_TREES:
        for path in sorted((root / tree).rglob("*")):
            if "__pycache__" in path.parts or not path.is_file():
                continue
            digest[str(path.relative_to(root))] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    return digest


def parse_size(text: str) -> int:
    """A byte count: plain digits, or a decimal with a MiB or GiB suffix."""
    value = 0
    if text.isdigit():
        value = int(text)
    else:
        for unit, factor in _SIZE_UNITS.items():
            if text.endswith(unit):
                try:
                    value = round(float(text[: -len(unit)]) * factor)
                except ValueError:
                    value = 0
    if value <= 0:
        raise argparse.ArgumentTypeError(
            f"{text!r}: expected a positive byte count, or a decimal with a MiB "
            "or GiB suffix (e.g. 4GiB, 2.5GiB, 512MiB)"
        )
    return value


def _address_space_limiter(cap: int) -> Callable[[], None]:
    """The preexec_fn: caps the mutmut process (and, inherited, every child it
    forks) at `cap` bytes of address space -- see the header."""

    def limit() -> None:
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))

    return limit


def _isolate_git(root: Path) -> dict[str, str]:
    """mutants/ becomes its own repository and the root is git's ceiling --
    see the header. Returns the env entries the mutmut process gets."""
    mutants = root / "mutants"
    mutants.mkdir(exist_ok=True)
    if not (mutants / ".git").exists():
        subprocess.run(
            ["git", "init", "-q", "--template=", str(mutants)],
            capture_output=True,
            text=True,
            check=True,
        )
    return {"GIT_CEILING_DIRECTORIES": str(root)}


def _run_mutmut(
    relpath: str,
    max_children: int,
    root: Path = ROOT,
    address_space: int = parse_size(DEFAULT_ADDRESS_SPACE),
) -> tuple[str, int]:
    pattern = relpath[: -len(".py")].replace("/", ".") + ".*"
    cmd = [
        sys.executable,
        str(LAUNCHER),
        pattern,
        "--max-children",
        str(max_children),
    ]
    # sitecustomize.py in SHIMS must be found by every process of the run,
    # including test subprocesses that chdir away: absolute, and prepended so
    # it wins over anything already on PYTHONPATH.
    inherited = os.environ.get("PYTHONPATH")
    pythonpath = f"{SHIMS}{os.pathsep}{inherited}" if inherited else str(SHIMS)
    _sweep_pycache(root)
    before = _tree_digest(root)
    # The isolation's git init runs inside the hashed window: nothing it does
    # may touch the source trees either.
    env = {
        **os.environ,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": pythonpath,
        **_isolate_git(root),
    }
    # check=False deliberate: the exit code is the module's class, decided by
    # the caller, and a non-zero exit must reach it as data, not an exception.
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=root,
        check=False,
        env=env,
        preexec_fn=_address_space_limiter(address_space),
    )
    after = _tree_digest(root)
    sys.stderr.write(proc.stderr)
    if after != before:
        changed = sorted(
            path
            for path in before.keys() | after.keys()
            if before.get(path) != after.get(path)
        )
        raise SourceTreeChangedError(
            f"{relpath}: the source tree changed during the mutmut invocation: "
            + ", ".join(changed)
        )
    return proc.stdout, proc.returncode


def _measure(
    module: str, max_children: int, address_space: int
) -> tuple[str, int, str, ModuleResult | None]:
    """One module, start to finish: (stdout, exit code, class, result)."""
    # ROOT passed explicitly (not left to the parameter defaults, which bind at
    # definition time) so a monkeypatched ROOT reaches every reader.
    out, code = _run_mutmut(module, max_children, ROOT, address_space)
    if code != 0:
        return out, code, "error", None
    try:
        result = read_module_results(module, ROOT)
    except FileNotFoundError:
        return out, code, "error", None
    if result.no_verdict:
        return out, code, "error", result
    return out, code, "ok", result


def _describe(result: ModuleResult) -> str:
    counts = dict(result.counts)
    parts = [
        f"{status} {counts.pop(status, 0)}"
        for status in ("killed", "survived", "no tests")
    ]
    parts += [f"{status} {n}" for status, n in sorted(counts.items())]
    return ", ".join(parts)


def _report(
    prefix: str, module: str, cls: str, code: int, result: ModuleResult | None
) -> None:
    # Printed once the module's outcome is known -- cached or freshly run, ok
    # or error -- so the class and the counts are visible per module, not only
    # in the end-of-run summary.
    if result is None:
        print(f"{prefix} {module}: {cls} (mutmut exited {code}; no result read)")
        return
    line = f"{prefix} {module}: {cls} ({_describe(result)})"
    if result.no_verdict:
        # The ids ride on the class line itself: the operator's next move is
        # `mutmut show <id>` and a redo with --only once the cause is fixed.
        line += " -- no verdict: " + ", ".join(
            f"{status} {name}" for status, name in result.no_verdict
        )
    print(line)
    for status, name, key in result.flagged:
        print(f"{prefix}   {status} {name}  {key}")


def _record_paths(out_dir: Path, module: str) -> tuple[Path, Path, Path]:
    # "/" -> "__" (not "_") so a nested module can't collide with a differently
    # -nested module that happens to share a basename.
    stem = module.replace("/", "__")
    return (
        out_dir / f"{stem}.stdout",
        out_dir / f"{stem}.result.json",
        out_dir / f"{stem}.exit",
    )


def _cached_result(out_dir: Path, module: str) -> ModuleResult | None:
    # The .exit file is the completion marker (written last by _write_record),
    # so its absence or an unparseable body means no usable record -- a run
    # killed mid-write left the set incomplete. Only "0 ok" is a cache hit:
    # the class token is required because exit 0 no longer implies ok (an
    # interrupted run records "0 error" with mutants lacking a verdict), and a
    # record whose own body lists such mutants is refused as belt. Anything else
    # is a recorded *failure*, and the caller re-runs it.
    _stdout_path, result_path, exit_path = _record_paths(out_dir, module)
    try:
        code, cls = exit_path.read_text(encoding="utf-8").split()[:2]
        if (code, cls) != ("0", "ok"):
            return None
        data = json.loads(result_path.read_text(encoding="utf-8"))
        result = ModuleResult(
            survivors=set(data["survivors"]),
            counts=data["counts"],
            flagged=[(s, n, k) for s, n, k in data["flagged"]],
            no_verdict=[(s, n) for s, n in data["no_verdict"]],
        )
    except (OSError, ValueError, KeyError):
        return None
    return None if result.no_verdict else result


def _write_record(
    out_dir: Path,
    module: str,
    out: str,
    code: int,
    cls: str,
    result: ModuleResult | None,
) -> None:
    # stdout and result first, exit+class last: a run killed between the
    # writes leaves the .exit file missing, which _cached_result treats as no
    # record at all -- never as a false success or a false failure.
    stdout_path, result_path, exit_path = _record_paths(out_dir, module)
    stdout_path.write_text(out, encoding="utf-8")
    if result is not None:
        data = asdict(result)
        data["survivors"] = sorted(result.survivors)
        result_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    else:
        result_path.unlink(missing_ok=True)
    exit_path.write_text(f"{code} {cls}", encoding="utf-8")


def _update_baseline(
    baseline_path: Path,
    out_dir: Path | None,
    only: list[str],
    max_children: int,
    address_space: int,
) -> int:
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
    keys: set[str] = set()
    failed: list[str] = []
    unmeasured: list[str] = []
    no_tests: dict[str, int] = {}
    for module in _all_modules():
        cached = _cached_result(out_dir, module) if out_dir is not None else None
        if cached is not None:
            _report("[baseline]", module, "ok (cached)", 0, cached)
            result = cached
        elif only and module not in only:
            unmeasured.append(module)
            continue
        else:
            print(f"[baseline] {module}", flush=True)
            out, code, cls, measured = _measure(module, max_children, address_space)
            if out_dir is not None:
                _write_record(out_dir, module, out, code, cls, measured)
            _report("[baseline]", module, cls, code, measured)
            if cls != "ok" or measured is None:
                print(f"[baseline] FAIL {module}: mutmut exited {code} [{cls}]")
                failed.append(module)
                continue
            result = measured
        keys |= result.survivors
        if result.counts.get("no tests"):
            no_tests[module] = result.counts["no tests"]
    if failed or unmeasured:
        print(
            f"[baseline] refusing to write {baseline_path}: "
            f"{len(failed)} module(s) failed, {len(unmeasured)} not measured"
        )
        if failed:
            print(f"[baseline]   error ({len(failed)}): {', '.join(failed)}")
        if unmeasured:
            print(
                f"[baseline]   not measured ({len(unmeasured)}): {', '.join(unmeasured)}"
            )
        return 1
    header = (
        "# mutation-baseline.txt -- every research_vault module measured by "
        "scripts/mutation_gate.py --update-baseline over mutmut; one survivor "
        "key per line, format in the script header\n"
    )
    baseline_path.write_text(header + "\n".join(sorted(keys)) + "\n", encoding="utf-8")
    print(f"[baseline] {len(keys)} survivors written to {baseline_path}")
    _summarise_no_tests("[baseline]", no_tests)
    return 0


def _summarise_no_tests(prefix: str, no_tests: dict[str, int]) -> None:
    total = sum(no_tests.values())
    print(
        f"{prefix} no tests: {total} mutant(s) in {len(no_tests)} module(s) -- "
        "coverage reached only through subprocesses is invisible to mutmut's "
        "stats, so these are unmeasured, not killed"
    )
    for module, n in sorted(no_tests.items()):
        print(f"{prefix}   {module}: {n}")


def _gate(baseline_path: Path, base: str, max_children: int, address_space: int) -> int:
    modules = changed_modules(base)
    if not modules:
        print("[gate] no changed research_vault modules; pass")
        return 0
    baseline = baseline_keys(baseline_path)
    fresh: set[str] = set()
    failed: list[str] = []
    no_tests: dict[str, int] = {}
    for module in modules:
        print(f"[gate] {module}", flush=True)
        out, code, cls, result = _measure(module, max_children, address_space)
        print(out)
        _report("[gate]", module, cls, code, result)
        if cls != "ok" or result is None:
            print(f"[gate] FAIL {module}: mutmut exited {code} [{cls}]")
            failed.append(module)
            continue
        fresh |= new_survivors(result.survivors, baseline)
        if result.counts.get("no tests"):
            no_tests[module] = result.counts["no tests"]
    _summarise_no_tests("[gate]", no_tests)
    if failed:
        print(f"[gate] FAIL — {len(failed)} module(s) errored:")
        print(f"[gate]   error ({len(failed)}): {', '.join(failed)}")
        return 1
    if fresh:
        print(f"[gate] FAIL — {len(fresh)} new survivor(s):")
        for key in sorted(fresh):
            print(f"  {key}")
        return 1
    print("[gate] pass — no new survivors")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base", default="origin/main", help="gate mode: diff base ref"
    )
    parser.add_argument("--baseline", default=str(ROOT / "mutation-baseline.txt"))
    parser.add_argument("--update-baseline", action="store_true")
    parser.add_argument(
        "--max-children", type=int, default=4, help="passed through to mutmut run"
    )
    parser.add_argument(
        "--child-address-space",
        type=parse_size,
        default=DEFAULT_ADDRESS_SPACE,
        metavar="BYTES",
        help="RLIMIT_AS for the mutmut process and every child it forks: plain "
        "bytes, or a decimal with a MiB/GiB suffix (default %(default)s); size "
        "it so --max-children x this fits the machine's memory bound",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="--update-baseline only: per-module records, for resuming a killed "
        "blanket run instead of restarting it",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        metavar="RELPATH",
        help="--update-baseline only: run just this module (repeatable); the "
        "baseline is still written only once every module holds a record, and "
        "a recorded ok is reused -- delete its .exit record to redo it",
    )
    args = parser.parse_args()
    if args.only and not args.update_baseline:
        parser.error("--only requires --update-baseline")
    unknown = sorted(set(args.only) - set(_all_modules()))
    if unknown:
        parser.error(f"--only names no research_vault module: {', '.join(unknown)}")
    baseline_path = Path(args.baseline)
    try:
        if args.update_baseline:
            out_dir = Path(args.out_dir) if args.out_dir else None
            return _update_baseline(
                baseline_path,
                out_dir,
                args.only,
                args.max_children,
                args.child_address_space,
            )
        return _gate(
            baseline_path, args.base, args.max_children, args.child_address_space
        )
    except SourceTreeChangedError as error:
        prefix = "[baseline]" if args.update_baseline else "[gate]"
        print(f"{prefix} ABORT: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
