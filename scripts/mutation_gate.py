"""No-new-survivors mutation gate over mutmut 3.7.0.

Invoked explicitly as `python scripts/mutation_gate.py` — no shebang on purpose
(EXE001 fires on a shebang in a non-executable file, and nothing execs this directly).

Gate mode (default): mutation-test the research_vault modules changed since
--base, fail (exit 1) on any survivor whose key is absent from the committed
baseline. The gate SELECTS from commits (`<base>...HEAD`) and MEASURES the
working tree (mutmut copies it; _tree_digest hashes it), so both modes refuse
a dirty research_vault/ or tests/ tree up front -- an uncommitted edit would
otherwise measure nothing and read as a pass (#133).
--update-baseline: measure every research_vault module and rewrite the
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
durable. --only RELPATH (repeatable, update-baseline only, and only with
--out-dir -- without records the other modules have nowhere to be read from,
so argparse refuses the pair up front) narrows which modules this invocation
runs; the write still requires every module to hold a usable record, and
names the ones that do not. A recorded ok still wins over --only: to redo
such a module, delete its .exit record first. Gate mode ignores --out-dir.

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
baseline_keys() still tolerates them as lines.

A written baseline starts with two `#` header lines; baseline_keys() skips
comment and blank lines. A `# reason: <text>` line immediately above a key
records why that survivor is accepted (baseline_reasons() pairs them and
refuses a dangling one); --update-baseline re-emits each reason above the
same key, drops it with a key the run killed, and reports on stderr `[baseline]
reason not re-attached: <key>` for a key no mutant of the run produced -- the
case a cut or rename leaves when the reason sits above the old spelling.

Per-child address-space cap. --child-address-space (default 4GiB; a plain byte
count, or a decimal with a MiB or GiB suffix) is applied to the mutmut process
through resource.setrlimit(RLIMIT_AS) in a preexec_fn, and mutmut forks its
per-mutant children from that process, so every child inherits it. Why: a
cgroup MemoryMax bounds the SUM over the children, so a runaway-allocation
mutant (measured 2026-09-14 in selectors.py: one child at 2.0 GB, then five at
1.6-2.2 GB) takes the whole run down by OOM-kill; under a per-process cap the
same mutant raises MemoryError, pytest exits 1, and the mutant counts as
killed. Sizing: the strict bound is (children + 1 + concurrent test
subprocesses) x cap -- the mutmut parent and every subprocess a test spawns
carry the same cap -- so children x cap under the machine's memory bound is
a bound on the OOM killer, not a guarantee, and a looser product only holds
while at most one child runs away at a time. False-kill cost: only a test that
genuinely needs more than the cap, and the suite runs in under 1 GB. A cap
the process may not set -- the inherited hard limit is already below it --
is checked before the launch and aborts the run with the gate's own
`[...] ABORT:` line and exit 1; a preexec that still fails is caught at the
launch and reported the same way, never as a traceback. That read goes
through one seam (_getrlimit) because the gate's own tests run inside
mutmut's stats phase under the enclosing gate's cap (measured 2026-09-14 on
CI: a 3 GiB cap made every test launching with the 4 GiB default read as a
nested over-cap, and all ten modules errored); the tests patch the seam, and
a real nested over-cap is still refused.

Two CI budgets, in this order. (1) --max-mutants N (gate mode only; default:
no budget). A GitHub job dies at its timeout, and the whole-branch integration
case -- a diff touching most of the 38 modules, ~17,000 mutants at the
runner's two children -- does not fit that with headroom: without a budget it
would time out, and a timed-out check reads as a failure it never measured.
So before mutating anything the gate counts the mutants the changed set would
run and, over the budget, prints exactly one qualified line -- `[gate] not
measured: <count> mutants across <M> changed modules exceed the CI budget of
<N>; run the gate locally` -- plus the per-module counts, and exits 0 without
launching mutmut or reading the baseline (the four-state rule: an unrun check
reads unmeasured, never pass or fail). The count is mutmut's own generator run
in memory over each changed module's source (mutate_file_contents: the same
operator set and pragma handling the run applies, so it equals the run's
count -- checked 2026-09-14 against the blanket run's cached .meta for all
modules, 17,151 of 17,151), writing nothing under mutants/ and running no
test. (2) --time-budget SECONDS (gate mode only; default: none). A slow
multi-module set can fit the count budget and still exceed the job timeout.
No single module approaches it (the largest is under seventy minutes at the
slowest measured rate), so the first changed module is always measured; then
the remaining modules are estimated from the stats file that run left behind
(mutants/mutmut-stats.json: `duration_by_test` and
`tests_by_mangled_function_name`) -- each module's mutants mapped to the tests
that reach their functions, the durations summed, divided by --max-children,
plus FIXED_MODULE_SECONDS per module -- and compared with the budget minus the
gate's own elapsed time. Over it: the first module's verdict, then `[gate] not
measured: estimated <m> min for <k> remaining modules exceeds the <n> min left
of the time budget`, and the exit code the first module earned. quality.yml
computes the budget from the job's start and its timeout variable, so the gate
never reads the environment; an estimate that cannot be read (no stats file,
a malformed one) is reported on one line and the run continues.

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
work, and tmp_path repositories are outside it). Two things the ceiling alone
does not cover, so the gate does them too: the four git LOCATION variables
(GIT_DIR, GIT_WORK_TREE, GIT_COMMON_DIR, GIT_INDEX_FILE) are dropped from the
child environment -- any one of them inherited names a repository outright and
discovery, ceiling included, never runs -- and an existing mutants/.git is not
trusted: before every invocation `git -C mutants rev-parse --git-common-dir`
must resolve to mutants/.git itself, and a gitfile pointing elsewhere, a
symlink, or a directory git no longer reads as a repository is removed and the
repository initialised afresh (measured: `git init` over a directory whose
HEAD is garbage leaves the garbage in place). That removal never follows a
symlink: a mutants/ that is itself a symlink (or a file) aborts the run before
anything is touched, because mkdir(exist_ok=True) accepts a symlink to a
directory and the removal would then land wherever it points -- the root's own
gitfile, if it pointed at the root. A core.hooksPath override for
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
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from libcst import ParserSyntaxError

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
# The fixed cost of one module's measurement beyond its mutants: mutant
# generation, the stats phase and the clean run, ≈5 min (runs 34822363722 and
# 34827110718, 2026-09-14; quality.yml's gate comment).
FIXED_MODULE_SECONDS = 300
STATS_FILE = Path("mutants") / "mutmut-stats.json"
_SIZE_UNITS = {"MiB": 1 << 20, "GiB": 1 << 30}
# The pre-check's one read of the inherited limit, a seam so the gate's own
# tests do not depend on it: mutmut's stats phase runs them in-process under
# whatever cap the enclosing gate set (measured 2026-09-14, CI run 34822363722:
# the 3 GiB cap quality.yml passes made every test that launches with the
# 4 GiB default read as a nested over-cap and errored all ten modules).
_getrlimit = resource.getrlimit
# Inherited, any one of these names a repository outright and git's discovery
# (the ceiling with it) never runs -- see the header.
GIT_LOCATION_VARS = ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE")


class GateAbortError(RuntimeError):
    """The run cannot continue; main() prints it as the gate's ABORT line."""


class SourceTreeChangedError(GateAbortError):
    """research_vault/ or tests/ differed after a mutmut invocation."""


class ChildLimitError(GateAbortError):
    """The per-child address-space cap cannot be applied."""


class MutantsTreeError(GateAbortError):
    """mutants/ is not a real directory the gate may own (a symlink, a file)."""


class GitCommandError(GateAbortError):
    """A git command the gate runs for itself failed -- the diff against
    --base, the init of mutants/: the command, its exit code and its stderr."""


class DirtyTreeError(GateAbortError):
    """research_vault/ or tests/ carries an uncommitted change. Gate mode
    selects modules from `<base>...HEAD` while mutmut copies and _tree_digest
    hashes the working tree, so an uncommitted edit measures nothing and would
    read as a pass; --update-baseline has the same exposure (#133)."""


class ModuleParseError(GateAbortError):
    """A module's source does not parse for mutmut's generator (a syntax
    error, a malformed `# pragma: no mutate` context): the file and the
    parser's message. Nothing is counted or run for a module it cannot read."""


class MetaReadError(ValueError):
    """mutants/<relpath>.meta exists but is not mutmut's record (truncated
    JSON, no exit_code_by_key, a mutant its readers cannot resolve): the
    module is an error naming the file and the fault, never a silent ok."""


@dataclass
class ModuleResult:
    survivors: set[str]
    counts: dict[str, int]
    # (status, mutmut id, key) for every BY_NAME_STATUSES verdict.
    flagged: list[tuple[str, str, str]] = field(default_factory=list)
    # (status, mutmut id) for every NO_VERDICT_STATUSES code: the module is an error.
    no_verdict: list[tuple[str, str]] = field(default_factory=list)
    # Every key of every mutant that has a verdict, survivors included: what
    # the baseline writer needs to tell a reason whose key was killed from one
    # whose key no mutant of the run produced.
    generated: set[str] = field(default_factory=set)


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


def mutation_key(relpath: str, mutant_name: str, diff: str, root: Path = ROOT) -> str:
    mm = _mutmut(root)
    func, cls = mm.orig_function_and_class_names_from_key(mutant_name)
    name = f"{cls}.{func}" if cls else func
    return f"{relpath}::func/{name}::{mutation_text(diff)}"


def read_module_results(relpath: str, root: Path = ROOT) -> ModuleResult:
    """Everything the gate needs from mutants/<relpath>.meta, keyed durably.
    Raises FileNotFoundError when there is no .meta (no measurement must never
    read as zero survivors) and MetaReadError when there is one the gate
    cannot read as mutmut's record -- either way the module is an error."""
    meta_path = root / "mutants" / f"{relpath}.meta"
    text = meta_path.read_text(encoding="utf-8")
    try:
        exit_code_by_key: dict[str, int | None] = json.loads(text)["exit_code_by_key"]
        items = list(exit_code_by_key.items())
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        raise MetaReadError(f"{meta_path}: not mutmut's record ({error})") from error
    mm = _mutmut(root)
    result = ModuleResult(survivors=set(), counts={})
    with contextlib.chdir(root):
        for name, code in items:
            try:
                status = mm.status_by_exit_code[code]
            except TypeError as error:  # an unhashable code: not an exit code
                raise MetaReadError(
                    f"{meta_path}: {name}: exit code {code!r} is not one"
                ) from error
            result.counts[status] = result.counts.get(status, 0) + 1
            if status in NO_VERDICT_STATUSES:
                result.no_verdict.append((status, name))
                continue
            # Whatever mutmut's readers raise for this name -- an assertion on
            # a name without `__mutmut_`, a function the schemata lacks -- is
            # the record's fault, not the gate's: named, classed error.
            try:
                diff = mm.get_diff_for_mutant(name, path=relpath)
                key = mutation_key(relpath, name, diff, root)
            except Exception as error:
                raise MetaReadError(
                    f"{meta_path}: mutant {name!r} cannot be read back "
                    f"({type(error).__name__}: {error})"
                ) from error
            result.generated.add(key)
            if status == "survived":
                result.survivors.add(key)
            elif status in BY_NAME_STATUSES:
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


REASON_PREFIX = "# reason: "


class BaselineFormatError(GateAbortError):
    """A `# reason:` line with no key beneath it: the file's format is the
    contract Task 26's triage and the writer share, and a reason that pairs
    with nothing would be dropped silently."""


def baseline_reasons(path: Path) -> dict[str, str]:
    """`# reason: <text>` immediately above a key records why that survivor is
    accepted; the pairing is positional, so a reason followed by a blank
    line, a comment, another reason or the end of the file is an error."""
    if not path.exists():
        return {}
    reasons: dict[str, str] = {}
    pending: tuple[int, str] | None = None
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith(REASON_PREFIX):
            if pending is not None:
                raise BaselineFormatError(
                    f"{path}:{pending[0]}: reason line has no key beneath it"
                )
            pending = (number, line[len(REASON_PREFIX) :].strip())
            continue
        if pending is None:
            continue
        if not line or line.startswith("#"):
            raise BaselineFormatError(
                f"{path}:{pending[0]}: reason line has no key beneath it"
            )
        reasons[line] = pending[1]
        pending = None
    if pending is not None:
        raise BaselineFormatError(
            f"{path}:{pending[0]}: reason line has no key beneath it"
        )
    return reasons


def _git_failure(error: subprocess.CalledProcessError) -> GitCommandError:
    """The abort for a git command the gate ran with check=True: what was run,
    how it exited and what git said -- never the CalledProcessError's own
    traceback."""
    stderr = " ".join((error.stderr or "").split()) or "(no stderr)"
    return GitCommandError(
        f"`{' '.join(map(str, error.cmd))}` exited {error.returncode}: {stderr}"
    )


def _refuse_dirty_tree(cwd: Path) -> None:
    """Both modes, before anything is selected or measured: any status line
    under the source trees is a refusal naming the paths. `--untracked-files=
    all` because plain `git status` honours `status.showUntrackedFiles=no`, a
    large-repo performance setting a user may carry in `~/.gitconfig`: without
    the option an untracked module prints no status line and the gate proceeds,
    while mutmut copies that file into `mutants/` and measures against it. A
    command line option is the one spelling a configuration cannot reach."""
    try:
        status = subprocess.run(
            [
                "git",
                "status",
                "--porcelain",
                "--untracked-files=all",
                "--",
                *SOURCE_TREES,
            ],
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd,
        ).stdout
    except subprocess.CalledProcessError as error:
        raise _git_failure(error) from error
    dirty = [line[3:] for line in status.splitlines() if line.strip()]
    if dirty:
        trees = " and ".join(f"{tree}/" for tree in SOURCE_TREES)
        raise DirtyTreeError(
            f"uncommitted changes under {trees}: {', '.join(dirty)} -- commit "
            "first: the gate selects modules from <base>...HEAD and measures "
            "the working tree"
        )


def changed_modules(base: str, cwd: Path = ROOT) -> list[str]:
    # --relative + a cwd-relative pathspec, both resolved from the repo root: a
    # stale core/-prefixed pathspec here matches nothing and kills the gate silently.
    _refuse_dirty_tree(cwd)
    try:
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
    except subprocess.CalledProcessError as error:
        # A --base that does not resolve (a shallow clone without origin/main)
        # is the usual cause; the abort names the ref through the command.
        raise _git_failure(error) from error
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


def _mutant_names(mm: ModuleType, root: Path, relpath: str) -> list[str]:
    """The mutant names mutmut's generator would produce for one module, in
    memory -- shared by count_mutants and _estimate_seconds so both read the
    same generator and fail the same way (ModuleParseError) on a module it
    cannot parse."""
    # Imported after _mutmut, for the reason _mutmut exists (config at import).
    from mutmut.mutation.pragma_handling import PragmaParseError

    source = (root / relpath).read_text(encoding="utf-8")
    try:
        with contextlib.chdir(root):
            return mm.mutate_file_contents(relpath, source).mutant_names
    except (ParserSyntaxError, PragmaParseError) as error:
        message = " ".join(str(error).split())
        raise ModuleParseError(
            f"{relpath}: mutmut's generator cannot parse it "
            f"({type(error).__name__}: {message})"
        ) from error


def count_mutants(relpath: str, root: Path = ROOT) -> int:
    """How many mutants mutmut would generate for the module: its own
    generator over the source, in memory -- see the header's budget
    paragraph. Nothing is written and no test runs."""
    mm = _mutmut(root)  # loads mutmut's config from root: pragma patterns
    return len(_mutant_names(mm, root, relpath))


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


def _positive(noun: str) -> Callable[[str], int]:
    """An argparse type: a positive integer, named by `noun` in the refusal."""

    def parse(text: str) -> int:
        if not text.isdigit() or int(text) < 1:
            raise argparse.ArgumentTypeError(f"{text!r}: expected a positive {noun}")
        return int(text)

    return parse


parse_budget = _positive("mutant count")  # --max-mutants
parse_seconds = _positive("number of seconds")  # --time-budget


def _address_space_limiter(cap: int) -> Callable[[], None]:
    """The preexec_fn: caps the mutmut process (and, inherited, every child it
    forks) at `cap` bytes of address space -- see the header."""

    def limit() -> None:
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))

    return limit


def _check_address_space_cap(cap: int) -> None:
    """A cap above the inherited hard limit is one setrlimit would refuse in
    the child, where the failure is only a preexec traceback: refuse it here,
    as the gate's own abort, before anything is launched."""
    _soft, hard = _getrlimit(resource.RLIMIT_AS)
    if hard != resource.RLIM_INFINITY and hard < cap:
        raise ChildLimitError(
            f"--child-address-space {cap} exceeds this process's RLIMIT_AS hard "
            f"limit of {hard} bytes; the cap cannot be applied to the mutmut "
            "children (lower it, or raise the hard limit)"
        )


def _git_env(root: Path) -> dict[str, str]:
    """The environment every git-touching process under the gate gets: the
    inherited one minus the location variables, plus the ceiling."""
    env = {k: v for k, v in os.environ.items() if k not in GIT_LOCATION_VARS}
    env["GIT_CEILING_DIRECTORIES"] = str(root)
    return env


def _is_own_repository(mutants: Path, env: dict[str, str]) -> bool:
    """Whether mutants/.git is a directory git reads as a repository whose
    common dir is that very directory -- not a gitfile or symlink pointing
    elsewhere, not a directory git no longer accepts."""
    dot_git = mutants / ".git"
    if dot_git.is_symlink() or not dot_git.is_dir():
        return False
    probe = subprocess.run(
        ["git", "-C", str(mutants), "rev-parse", "--git-common-dir"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if probe.returncode != 0:
        return False
    return (mutants / probe.stdout.strip()).resolve() == dot_git.resolve()


def _real_mutants_dir(root: Path) -> Path:
    """root/mutants, refused unless absent or a real directory. The gate
    sweeps, removes and initialises under it: a symlink there
    (mkdir(exist_ok=True) accepts one, and is_symlink() on `.git` inspects
    only the last component) would send all of that to whatever it points at
    -- the root's own gitfile, if it pointed at the root. Touch nothing."""
    mutants = root / "mutants"
    if mutants.is_symlink() or (mutants.exists() and not mutants.is_dir()):
        raise MutantsTreeError(
            f"{mutants} is not a real directory (a symlink or a file); the gate "
            "owns mutants/ and will not sweep, remove or initialise through it "
            "-- move it aside and rerun"
        )
    return mutants


def _isolate_git(root: Path) -> dict[str, str]:
    """mutants/ becomes its own repository and the root is git's ceiling --
    see the header. An existing mutants/.git is verified, never trusted.
    Returns the env entries the mutmut process gets."""
    mutants = _real_mutants_dir(root)
    mutants.mkdir(exist_ok=True)
    env = _git_env(root)
    dot_git = mutants / ".git"
    present = dot_git.exists() or dot_git.is_symlink()
    if present and not _is_own_repository(mutants, env):
        if dot_git.is_dir() and not dot_git.is_symlink():
            shutil.rmtree(dot_git)
        else:
            dot_git.unlink()
        present = False
    if not present:
        try:
            subprocess.run(
                ["git", "init", "-q", "--template=", str(mutants)],
                env=env,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as error:
            raise _git_failure(error) from error
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
    _check_address_space_cap(address_space)
    _real_mutants_dir(root)  # before the sweep: it walks mutants/ too
    _sweep_pycache(root)
    before = _tree_digest(root)
    # The isolation's git init runs inside the hashed window: nothing it does
    # may touch the source trees either. _git_env drops the inherited git
    # location variables; the ceiling comes from _isolate_git.
    env = {
        **_git_env(root),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": pythonpath,
        **_isolate_git(root),
    }
    # check=False deliberate: the exit code is the module's class, decided by
    # the caller, and a non-zero exit must reach it as data, not an exception.
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=root,
            check=False,
            env=env,
            preexec_fn=_address_space_limiter(address_space),
        )
    except subprocess.SubprocessError as error:
        # A preexec_fn that raises (setrlimit refused) surfaces here, as
        # "Exception occurred in preexec_fn": the gate's abort, not a traceback.
        raise ChildLimitError(
            f"{relpath}: launching mutmut under --child-address-space "
            f"{address_space} failed: {error}"
        ) from error
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
) -> tuple[str, int, str, ModuleResult | None, str | None]:
    """One module, start to finish: (stdout, exit code, class, result, and
    -- when no result could be read -- what stopped the read)."""
    # ROOT passed explicitly (not left to the parameter defaults, which bind at
    # definition time) so a monkeypatched ROOT reaches every reader.
    out, code = _run_mutmut(module, max_children, ROOT, address_space)
    if code != 0:
        return out, code, "error", None, None
    try:
        result = read_module_results(module, ROOT)
    except FileNotFoundError as error:
        return out, code, "error", None, f"no {error.filename or error}"
    except MetaReadError as error:
        return out, code, "error", None, str(error)
    if result.no_verdict:
        return out, code, "error", result, None
    return out, code, "ok", result, None


def _describe(result: ModuleResult) -> str:
    counts = dict(result.counts)
    parts = [
        f"{status} {counts.pop(status, 0)}"
        for status in ("killed", "survived", "no tests")
    ]
    parts += [f"{status} {n}" for status, n in sorted(counts.items())]
    return ", ".join(parts)


def _report(
    prefix: str,
    module: str,
    cls: str,
    code: int,
    result: ModuleResult | None,
    note: str | None = None,
) -> None:
    # Printed once the module's outcome is known -- cached or freshly run, ok
    # or error -- so the class and the counts are visible per module, not only
    # in the end-of-run summary. `note` names what stopped a result read (a
    # missing or malformed .meta), so the offender is on its own class line.
    if result is None:
        why = f"; no result read: {note}" if note else "; no result read"
        print(f"{prefix} {module}: {cls} (mutmut exited {code}{why})")
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
            generated=set(data["generated"]),
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
        data["generated"] = sorted(result.generated)
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
    _refuse_dirty_tree(ROOT)
    reasons = baseline_reasons(baseline_path)
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
    keys: set[str] = set()
    generated: set[str] = set()
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
            out, code, cls, measured, note = _measure(
                module, max_children, address_space
            )
            if out_dir is not None:
                _write_record(out_dir, module, out, code, cls, measured)
            _report("[baseline]", module, cls, code, measured, note)
            if cls != "ok" or measured is None:
                print(f"[baseline] FAIL {module}: mutmut exited {code} [{cls}]")
                failed.append(module)
                continue
            result = measured
        keys |= result.survivors
        generated |= result.generated
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
        # The gap is reported on every run that measured anything, refused or
        # not -- the same block gate mode prints unconditionally.
        _summarise_no_tests("[baseline]", no_tests)
        return 1
    header = (
        "# mutation-baseline.txt -- every survivor of the research_vault modules "
        "measured by scripts/mutation_gate.py --update-baseline over mutmut; one "
        "survivor key per line, format in the script header\n"
        "# a `# reason: <text>` line immediately above a key records why that "
        "survivor is accepted; the writer re-emits it above the same key and "
        "reports on stderr any reason whose key no mutant of the run produced\n"
    )
    lines: list[str] = []
    for key in sorted(keys):
        if key in reasons:
            lines.append(f"{REASON_PREFIX}{reasons[key]}")
        lines.append(key)
    baseline_path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")
    for key in sorted(set(reasons) - keys):
        if key not in generated:
            print(f"[baseline] reason not re-attached: {key}", file=sys.stderr)
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


def _over_budget(modules: list[str], max_mutants: int) -> bool:
    """Count what the changed set would run and say so; over the budget the
    diff is reported as unmeasured (see the header) and the caller stops."""
    counts = {module: count_mutants(module, ROOT) for module in modules}
    total = sum(counts.values())
    over = total > max_mutants
    changed = f"{len(modules)} changed module" + ("" if len(modules) == 1 else "s")
    if over:
        print(
            f"[gate] not measured: {total} mutants across {changed} exceed the "
            f"CI budget of {max_mutants}; run the gate locally"
        )
    else:
        print(
            f"[gate] {total} mutants across {changed}, within the CI budget of "
            f"{max_mutants}"
        )
    for module, n in counts.items():
        print(f"[gate]   {module}: {n}")
    return over


def _estimate_seconds(modules: list[str], root: Path, max_children: int) -> float:
    """What the remaining changed modules would cost, from the stats file the
    first module's run left behind (see the header's budget paragraph): each
    module's mutants mapped to the tests that reach their functions, the
    durations summed and divided by the child count, plus the fixed cost."""
    stats = json.loads((root / STATS_FILE).read_text(encoding="utf-8"))
    tests_by_function: dict[str, list[str]] = stats["tests_by_mangled_function_name"]
    duration_by_test: dict[str, float] = stats["duration_by_test"]
    mm = _mutmut(root)
    total = 0.0
    for relpath in modules:
        dotted = relpath[: -len(".py")].replace("/", ".")
        names = _mutant_names(mm, root, relpath)
        seconds = 0.0
        for name in names:
            function = f"{dotted}.{mm.mangled_name_from_mutant_name(name)}"
            seconds += sum(
                duration_by_test.get(test, 0.0)
                for test in tests_by_function.get(function, ())
            )
        total += seconds / max_children + FIXED_MODULE_SECONDS
    return total


def _minutes(seconds: float) -> int:
    return round(seconds / 60)


def _gate(
    baseline_path: Path,
    base: str,
    max_children: int,
    address_space: int,
    max_mutants: int | None = None,
    time_budget: int | None = None,
) -> int:
    started = time.monotonic()
    modules = changed_modules(base, cwd=ROOT)
    if not modules:
        print("[gate] no changed research_vault modules; pass")
        return 0
    # The count budget is first: it refuses before anything is generated.
    if max_mutants is not None and _over_budget(modules, max_mutants):
        return 0
    baseline = baseline_keys(baseline_path)
    fresh: set[str] = set()
    failed: list[str] = []
    no_tests: dict[str, int] = {}
    unmeasured: str | None = None
    for index, module in enumerate(modules):
        print(f"[gate] {module}", flush=True)
        out, code, cls, result, note = _measure(module, max_children, address_space)
        print(out)
        _report("[gate]", module, cls, code, result, note)
        if cls != "ok" or result is None:
            print(f"[gate] FAIL {module}: mutmut exited {code} [{cls}]")
            failed.append(module)
        else:
            fresh |= new_survivors(result.survivors, baseline)
            if result.counts.get("no tests"):
                no_tests[module] = result.counts["no tests"]
        remaining = modules[index + 1 :]
        if index == 0 and time_budget is not None and remaining:
            # Nothing gate-side can see an estimate before the first module
            # is measured (the stats file is that run's); the first module is
            # measured regardless and the rest are budgeted from it.
            try:
                estimate = _estimate_seconds(remaining, ROOT, max_children)
            except (OSError, ValueError, KeyError, TypeError) as error:
                print(f"[gate] time budget not applied: {STATS_FILE}: {error}")
                continue
            left = time_budget - (time.monotonic() - started)
            if estimate > left:
                count = f"{len(remaining)} remaining module" + (
                    "" if len(remaining) == 1 else "s"
                )
                unmeasured = (
                    f"[gate] not measured: estimated {_minutes(estimate)} min for "
                    f"{count} exceeds the {_minutes(left)} min left of the time budget"
                )
                break
    _summarise_no_tests("[gate]", no_tests)
    if failed:
        print(f"[gate] FAIL — {len(failed)} module(s) errored:")
        print(f"[gate]   error ({len(failed)}): {', '.join(failed)}")
        code = 1
    elif fresh:
        print(f"[gate] FAIL — {len(fresh)} new survivor(s):")
        for key in sorted(fresh):
            print(f"  {key}")
        code = 1
    else:
        print("[gate] pass — no new survivors")
        code = 0
    if unmeasured is not None:
        print(unmeasured)
    return code


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
        "--max-mutants",
        type=parse_budget,
        default=None,
        metavar="N",
        help="gate mode only: the CI mutant budget; a changed set that would run "
        "more than N mutants is reported as not measured (exit 0) instead of "
        "run -- see the header",
    )
    parser.add_argument(
        "--time-budget",
        type=parse_seconds,
        default=None,
        metavar="SECONDS",
        help="gate mode only: after the first changed module is measured, the "
        "remaining modules are estimated from mutmut's stats file and reported "
        "as not measured when the estimate exceeds what is left of this budget "
        "-- see the header",
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
    if args.only and not args.out_dir:
        # Without records the other modules have nowhere to be read from, so
        # the write would refuse every time: say so before a run that cannot
        # succeed.
        parser.error(
            "--only requires --out-dir: the baseline is written only once every "
            "module holds a record, and only the records carry the others"
        )
    if args.max_mutants is not None and args.update_baseline:
        parser.error("--max-mutants is a gate-mode budget; not with --update-baseline")
    if args.time_budget is not None and args.update_baseline:
        parser.error("--time-budget is a gate-mode budget; not with --update-baseline")
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
            baseline_path,
            args.base,
            args.max_children,
            args.child_address_space,
            args.max_mutants,
            args.time_budget,
        )
    except GateAbortError as error:
        prefix = "[baseline]" if args.update_baseline else "[gate]"
        print(f"{prefix} ABORT: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
