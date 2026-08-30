"""No-new-survivors mutation gate over mutate4py.

Invoked explicitly as `python scripts/mutation_gate.py` — no shebang on purpose
(EXE001 fires on a shebang in a non-executable file, and nothing execs this directly).

Gate mode (default): mutation-test the research_vault files changed since --base,
fail (exit 1) on any survivor whose key is absent from the committed baseline.
--update-baseline: blanket-run every research_vault module (--mutate-all) and
rewrite the baseline file with every current survivor.

--out-dir (update-baseline only): per-module stdout+exit-code records written as
each module finishes, so a blanket run killed partway through can resume instead
of restarting from zero. A recorded exit 0 is reused without re-running; anything
else -- no record, an unparseable exit file, or a recorded failure -- re-runs and
overwrites both files. Gate mode ignores this flag.

--memory-cap SIZE (either mode): wraps every mutate4py invocation in
`systemd-run --user --scope -p MemoryMax=SIZE -p MemorySwapMax=0`, so the kernel
kills a runaway invocation instead of the whole VM. Measured cause: mutate4py
0.1.4's parallel path (--max-workers >= 2) leaks ~199 MB/s monotonically and has
taken down this machine's VM before Linux's OOM-killer could react; the serial
path (--max-workers 1) is memory-stable but ~9x slower. SIZE is passed through
verbatim to MemoryMax= -- systemd owns that size grammar, not this script.

Every module gets a failure class, not just a pass/fail bit: "ok" (exit 0),
"memcap" (killed by the cap -- exit 137/143, and ONLY when --memory-cap was
actually in effect for that invocation, since those same codes mean something
else without one), or "error" (any other non-zero exit -- where the
still-unexplained mutate4py exit-4 cases live). Keeping memcap out of that
error bucket is deliberate: blending the two would contaminate a clean
inventory with kills that already have a known cause. The class is recorded
per module (out-dir record, progress line, end-of-run summary) but nothing
here retries or falls back automatically -- --out-dir's existing resume rule
already re-runs a recorded failure, so rerunning the same command with
--max-workers 1 serially re-runs exactly the cap-killed modules.

--exclusions PATH (either mode, default mutation-exclusions.txt at the repo
root): modules mutate4py 0.1.4 cannot measure AT ALL -- it aborts them
identically at every worker count, so their "no Survivors: section" is a true
absence of data, not a report of zero survivors. --update-baseline skips a
listed module outright (never invoked, no wasted minutes) and still writes the
baseline from everything else; a non-listed module that fails still blocks the
write exactly as before -- the list narrows what gets measured, it does not
loosen the refusal. Gate mode skips a listed CHANGED module the same way,
rather than let it land in the error bucket above and fail every PR that
merely touches one of these six for a cause outside the change -- but the skip
is reported by name and the final "pass" line is qualified when it happens, so
it can never read as a clean pass. The full exclusion set -- file, class,
reason -- prints once near the start of every invocation of either mode,
regardless of whether this run's modules intersect it: a gap you see every
time stays a gap; a gap in a file becomes furniture.

mutate4py exits 0 even when mutants survive, so pass/fail is parsed from the
"Survivors:" report section. Baseline keys exclude line numbers on purpose:
`<relpath>::<func-id>::<mutation>` stays stable across unrelated edits. A
module-level site (mutate4py's `function_id` is "" for these -- no enclosing
function) has no func-id to put there, so it keys as `<relpath>::module::
<mutation>` instead: still stable, and the literal "module" can never collide
with a real func-id, which is always `func/<name>`. A written baseline may
start with a `#`-prefixed line recording which modules were excluded when it
was built, so the file is self-describing on its own; baseline_keys() skips
comment and blank lines so that header is never mistaken for a key.
Always invokes mutate4py with --manifest-file (sidecar); the embedded manifest
mode writes into production source files and is never acceptable here.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # repo root
# func is OPTIONAL: mutate4py 0.1.4 omits the trailing " func/<name>" entirely
# for a module-level (import-time) site (_discovery.Site.function_id is ""
# there), so a survivor there prints as "  line 38 True -> False" with
# nothing after the mutation text. mutation is non-greedy so it yields the
# shortest text for which the rest of the line matches "func/<name>" exactly
# to end-of-string -- that is what makes the split land on the real boundary
# instead of swallowing part of a func id, or a func id swallowing part of
# the mutation text.
SURVIVOR_RE = re.compile(r"^\s+line \d+ (?P<mutation>.+?)(?: (?P<func>func/\S+))?$")
_ENTRY_START_RE = re.compile(r"^\s+line \d+ ")


def parse_survivors(relpath: str, output: str) -> set[str]:
    keys: set[str] = set()
    in_section = False
    pending: list[str] = []  # physical lines of the survivor entry in progress

    def flush() -> None:
        # A long s.desc wraps across further-indented continuation lines (see
        # the module docstring and the multi-line fixture in
        # tests/test_mutation_gate.py) -- folded here into one logical entry
        # by stripping each continuation and rejoining with a space, so the
        # anchored SURVIVOR_RE (which only ever sees single-line text) still
        # applies unchanged.
        if not pending:
            return
        text = pending[0]
        if len(pending) > 1:
            text += " " + " ".join(part.strip() for part in pending[1:])
        match = SURVIVOR_RE.match(text)
        if match is None:
            # Genuinely unparseable -- not module-level (func is optional
            # above) and not a wrapped continuation (folded above). Same
            # doctrine this script already applies to a non-zero mutate4py
            # exit: an unreadable measurement must never read as zero
            # survivors, so this raises instead of silently dropping the
            # entry and everything after it.
            raise ValueError(f"{relpath}: unparseable survivor entry: {text!r}")
        func = match["func"] or "module"
        keys.add(f"{relpath}::{func}::{match['mutation']}")

    for line in output.splitlines():
        if line.startswith("Survivors:"):
            in_section = True
            continue
        if not in_section:
            continue
        if not line[:1].isspace():
            # The section ends ONLY on a non-indented line (a blank line
            # qualifies too: line[:1] on "" is "" and .isspace() on that is
            # False) -- never on an indented line SURVIVOR_RE fails to match
            # standalone, since that shape is exactly a wrapped continuation,
            # not the end of the section.
            flush()
            pending.clear()
            in_section = False
            continue
        if pending and _ENTRY_START_RE.match(line):
            flush()
            pending.clear()
        pending.append(line)
    flush()  # a Survivors: section may run to EOF with no trailing blank line
    return keys


def new_survivors(found: set[str], baseline: set[str]) -> set[str]:
    return found - baseline


def baseline_keys(path: Path) -> set[str]:
    if not path.exists():
        return set()
    # "#" is the exclusion-header prefix _baseline_header writes -- skipped here
    # so a written baseline's own self-description never parses back as a key.
    return {
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    }


def parse_exclusions(path: Path) -> dict[str, tuple[str, str]]:
    """module -> (trigger class, one-line reason), read from mutation-exclusions.txt.
    Comment ('#') and blank lines are tolerated by design -- the file is meant to be
    read by a human without a guide. A missing file returns {} (nothing known to be
    unmeasurable) rather than erroring: a bad --exclusions path or a checkout that
    predates this file should degrade to "measure everything", not abort the gate --
    but that is never silent, since it prints a warning here rather than just
    returning quietly. A malformed line, by contrast, DOES raise: silently dropping
    an entry would put back exactly the undetectable hole this whole list exists to
    close, and a corrupt committed file is a bug worth failing loudly on."""
    if not path.exists():
        print(f"[exclusions] WARNING: {path} not found; treating as zero exclusions")
        return {}
    exclusions: dict[str, tuple[str, str]] = {}
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("::", 2)
        if len(parts) != 3:
            raise ValueError(
                f"{path}:{lineno}: malformed exclusion line (want "
                f"<module>::<class>::<reason>): {raw!r}"
            )
        module, cls, reason = parts
        exclusions[module] = (cls, reason)
    return exclusions


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


def _run_mutate(
    relpath: str,
    lcov: str,
    extra: list[str],
    max_workers: int,
    memory_cap: str | None = None,
) -> tuple[str, int]:
    cmd = [
        sys.executable,
        "-m",
        "mutate4py",
        relpath,
        "--lcov",
        lcov,
        "--manifest-file",
        "--max-workers",
        str(max_workers),
        *extra,
    ]
    if memory_cap is not None:
        # A systemd-run --user --scope cgroup makes the KERNEL enforce the
        # ceiling, so a leaking invocation gets SIGKILLed on its own instead
        # of exhausting host RAM+swap and taking the whole VM down with it
        # (measured: ~155 MB/s leak, VM dead in ~3.5 minutes, unmitigated).
        # MemorySwapMax=0 forbids paging near the limit -- letting it swap
        # would just trade a fast kill for a slow one without fixing anything.
        cmd = [
            "systemd-run",
            "--user",
            "--scope",
            "-p",
            f"MemoryMax={memory_cap}",
            "-p",
            "MemorySwapMax=0",
            "--quiet",
            "--",
            *cmd,
        ]
    # check=False deliberate: mutate4py exits 0 even with survivors, so the caller
    # must inspect returncode itself rather than rely on an exception -- a mutate4py
    # invocation that aborts (case-3 test-context disagreement, case-4 no test ran)
    # also exits non-zero with NO "Survivors:" section, and is otherwise
    # indistinguishable from a clean module with zero survivors. Returning the
    # code (not raising) keeps that distinction visible to both call sites, which
    # decide separately what a failed module means for their mode.
    # PYTHONDONTWRITEBYTECODE removes a false-SURVIVOR window, which is worse than
    # any abort: a timestamp-based .pyc is validated on (mtime, size) alone, and the
    # common mutations are same-length token swaps (== -> !=, + -> -, < -> >). A .pyc
    # written and a mutant applied inside the same filesystem-timestamp tick therefore
    # collide on both fields, so the child imports the STALE bytecode, never exercises
    # the mutant, and records it as survived. mutate4py's forking executor guards this
    # itself (_invalidate_bytecode_cache + sys.dont_write_bytecode); its subprocess
    # fallback does not, and that fallback is silent. Writing no bytecode at all costs
    # a recompile per run and removes the window on every path.
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    proc = subprocess.run(
        cmd, capture_output=True, text=True, cwd=ROOT, check=False, env=env
    )
    _restore_if_left_mutated(relpath)
    sys.stderr.write(proc.stderr)
    return proc.stdout, proc.returncode


def _restore_if_left_mutated(relpath: str) -> bool:
    """Undo a mutation mutate4py did not live long enough to undo. Returns True
    if it had to act.

    mutate4py writes `<module>.py.bak` before applying a mutant and removes it
    once the module finishes, so a surviving .bak means the run died mid-mutant
    and the PRODUCTION SOURCE IS STILL MUTATED. That has already cost this repo a
    machine: a timeout-killed run left `index += 1` -> `index += 0` in
    selectors._norm_with_map -- an infinite loop appending to a list -- and the
    next ordinary `pytest` invocation allocated until the VM died.

    Restores from the .bak rather than from git ON PURPOSE: the .bak is the exact
    pre-run content whatever it was, so this cannot destroy legitimate uncommitted
    edits the way `git checkout --` would. Nothing here is silent: an interrupted
    run that mutated production source is reported every time, because the same
    condition also means whatever ran in between saw mutated code.
    """
    bak = ROOT / f"{relpath}.bak"
    if not bak.exists():
        return False
    target = ROOT / relpath
    print(
        f"[restore] {relpath} was left MUTATED by an interrupted run; "
        f"restoring from {bak.name}",
        flush=True,
    )
    target.write_bytes(bak.read_bytes())
    bak.unlink()
    return True


def _classify(code: int, memory_cap: str | None) -> str:
    # 137 (SIGKILL) / 143 (SIGTERM) mean "the memory cap killed this" only
    # when a cap was actually wrapping the invocation -- without one those
    # are ordinary signal deaths and belong with the rest of the unexplained
    # non-zero exits (exit 4 among them), not mislabelled as a cap kill.
    if code == 0:
        return "ok"
    if memory_cap is not None and code in (137, 143):
        return "memcap"
    return "error"


def _print_exclusions(
    prefix: str, exclusions: dict[str, tuple[str, str]], path: Path
) -> None:
    # Unconditional -- called once per invocation regardless of mode, regardless
    # of whether this run's modules intersect the list, and even at zero
    # exclusions: "a gap you see every time stays a gap; a gap in a file becomes
    # furniture." A reader scanning CI output for this run sees the measurement
    # gap without having to go open mutation-exclusions.txt separately.
    print(
        f"{prefix} {len(exclusions)} module(s) excluded (unmeasurable by "
        f"mutate4py 0.1.4; see {path}):"
    )
    for module in sorted(exclusions):
        cls, reason = exclusions[module]
        print(f"{prefix}   {module} [{cls}]: {reason}")


def _baseline_header(exclusions: dict[str, tuple[str, str]]) -> str:
    # Written into mutation-baseline.txt itself, not only stdout -- a reader with
    # only the baseline file open (no run log, no mutation-exclusions.txt beside
    # it) still cannot mistake a partial baseline for whole-tree coverage. Always
    # present, even at zero exclusions, so a clean baseline states its own
    # completeness rather than leaving it to be inferred from an absent header.
    names = ", ".join(sorted(exclusions)) if exclusions else "none"
    return (
        f"# mutation-baseline.txt -- {len(exclusions)} module(s) excluded (see "
        f"mutation-exclusions.txt), not represented below: {names}\n"
    )


def _record_paths(out_dir: Path, module: str) -> tuple[Path, Path]:
    # "/" -> "__" (not "_") so a nested module can't collide with a differently
    # -nested module that happens to share a basename.
    stem = module.replace("/", "__")
    return out_dir / f"{stem}.stdout", out_dir / f"{stem}.exit"


def _cached_stdout(out_dir: Path, module: str) -> str | None:
    # The .exit file is the completion marker (written last by _write_record), so
    # its absence or an unparseable body means no usable record -- a run killed
    # mid-write left this pair incomplete. A parseable but non-zero exit is a
    # recorded *failure*, not a cache hit: it is deliberately not returned here,
    # so the caller re-runs it and _write_record overwrites both files.
    stdout_path, exit_path = _record_paths(out_dir, module)
    try:
        # Split rather than a bare int(): a pre-classification record ("0")
        # and a classed one ("0 ok") both parse this way -- only the leading
        # code decides cache-hit, so an old record needs no migration.
        code = int(exit_path.read_text(encoding="utf-8").strip().split()[0])
    except (OSError, ValueError, IndexError):
        return None
    if code != 0:
        return None
    try:
        return stdout_path.read_text(encoding="utf-8")
    except OSError:
        return None


def _write_record(out_dir: Path, module: str, out: str, code: int, cls: str) -> None:
    # stdout first, exit+class second: a run killed between the two writes leaves
    # the .exit file missing, which _cached_stdout treats as no record at all --
    # never as a false success or a false failure.
    stdout_path, exit_path = _record_paths(out_dir, module)
    stdout_path.write_text(out, encoding="utf-8")
    exit_path.write_text(f"{code} {cls}", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lcov", required=True, help="pre-generated branch-coverage LCOV"
    )
    parser.add_argument(
        "--base", default="origin/main", help="gate mode: diff base ref"
    )
    parser.add_argument("--baseline", default=str(ROOT / "mutation-baseline.txt"))
    parser.add_argument(
        "--exclusions",
        default=str(ROOT / "mutation-exclusions.txt"),
        help="modules mutate4py 0.1.4 cannot measure at all; skipped in both "
        "modes rather than treated as zero survivors",
    )
    parser.add_argument("--update-baseline", action="store_true")
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument(
        "--test-contexts", default=None, help="optional contexts db for narrowing"
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="--update-baseline only: per-module stdout+exit records, for resuming "
        "a killed blanket run instead of restarting it",
    )
    parser.add_argument(
        "--memory-cap",
        default=None,
        help="wrap every mutate4py invocation in a systemd-run --user --scope "
        "cgroup with MemoryMax=<this value>, verbatim (systemd's size grammar, "
        "not parsed here); mutate4py's parallel path leaks memory unboundedly "
        "without it",
    )
    args = parser.parse_args()

    extra = ["--test-contexts", args.test_contexts] if args.test_contexts else []
    baseline_path = Path(args.baseline)
    exclusions_path = Path(args.exclusions)
    exclusions = parse_exclusions(exclusions_path)
    prefix = "[baseline]" if args.update_baseline else "[gate]"
    _print_exclusions(prefix, exclusions, exclusions_path)

    if args.update_baseline:
        out_dir = Path(args.out_dir) if args.out_dir else None
        if out_dir is not None:
            out_dir.mkdir(parents=True, exist_ok=True)
        keys: set[str] = set()
        failed: list[tuple[str, str]] = []
        for module in _all_modules():
            if module in exclusions:
                # Known-unmeasurable (mutation-exclusions.txt) -- skipped before
                # ever invoking mutate4py, not merely excluded from the result:
                # the refusal below exists to catch modules the tool silently
                # couldn't check, not ones already known and explained not to be
                # checkable. Contributes nothing to `keys` and nothing to `failed`.
                cls, reason = exclusions[module]
                print(f"[baseline] {module}: excluded [{cls}] -- {reason}")
                continue
            cached = _cached_stdout(out_dir, module) if out_dir is not None else None
            if cached is not None:
                out, code, cls = cached, 0, "ok"
            else:
                print(f"[baseline] {module}", flush=True)
                out, code = _run_mutate(
                    module,
                    args.lcov,
                    [*extra, "--mutate-all"],
                    args.max_workers,
                    args.memory_cap,
                )
                cls = _classify(code, args.memory_cap)
                if out_dir is not None:
                    _write_record(out_dir, module, out, code, cls)
            # Printed once the module's outcome is known -- cached or freshly
            # run, ok/memcap/error alike -- so the class is visible per module,
            # not only in the end-of-run summary below.
            suffix = " (cached)" if cached is not None else ""
            print(f"[baseline] {module}: {cls}{suffix}")
            if cls != "ok":
                # A non-ok exit here means mutate4py aborted before ever printing
                # a "Survivors:" section (e.g. a test-context/coverage disagreement,
                # or a memory-cap kill) -- parse_survivors would silently return an
                # empty set, identical to a module that genuinely has zero
                # survivors. Recording that would write a baseline with an
                # undetectable hole in it, so this module's (empty, meaningless)
                # contribution is refused outright rather than merged in.
                print(f"[baseline] FAIL {module}: mutate4py exited {code} [{cls}]")
                failed.append((module, cls))
                continue
            keys |= parse_survivors(module, out)
        if failed:
            memcap_failed = [m for m, c in failed if c == "memcap"]
            error_failed = [m for m, c in failed if c == "error"]
            print(
                f"[baseline] refusing to write {baseline_path}: "
                f"{len(failed)} module(s) failed and were excluded"
            )
            # Reported as two separate classes, not one blended count: a
            # memory-cap kill has a known cause (rerun serially), an error
            # does not (it's the still-open exit-4 mystery) -- merging them
            # would make the summary useless for deciding what to do next.
            if memcap_failed:
                print(
                    f"[baseline]   memcap ({len(memcap_failed)}): "
                    f"{', '.join(memcap_failed)}"
                )
            if error_failed:
                print(
                    f"[baseline]   error ({len(error_failed)}): "
                    f"{', '.join(error_failed)}"
                )
            return 1
        baseline_path.write_text(
            _baseline_header(exclusions) + "\n".join(sorted(keys)) + "\n",
            encoding="utf-8",
        )
        print(
            f"[baseline] {len(keys)} survivors written to {baseline_path} "
            f"({len(exclusions)} module(s) excluded, not measured)"
        )
        return 0

    modules = changed_modules(args.base)
    if not modules:
        print("[gate] no changed research_vault modules; pass")
        return 0
    baseline = baseline_keys(baseline_path)
    fresh: set[str] = set()
    failed_modules: list[tuple[str, str]] = []
    excluded_changed: list[str] = []
    for module in modules:
        if module in exclusions:
            # Known-unmeasurable module touched by this change. Running mutate4py
            # on it would only reproduce the same deterministic abort recorded in
            # mutation-exclusions.txt -- and land it in failed_modules below,
            # which would fail every PR that so much as touches one of these six
            # for a cause outside the change (an explicitly rejected policy; see
            # the --exclusions docstring paragraph). Skipped, but named here and
            # again below so the run can never be misread as having verified it.
            cls, reason = exclusions[module]
            print(f"[gate] {module}: excluded [{cls}] -- {reason}")
            excluded_changed.append(module)
            continue
        print(f"[gate] {module}", flush=True)
        out, code = _run_mutate(
            module, args.lcov, extra, args.max_workers, args.memory_cap
        )
        print(out)
        cls = _classify(code, args.memory_cap)
        # Printed once the module's outcome is known, ok/memcap/error alike --
        # the class is visible per module, not only in the end-of-run summary.
        print(f"[gate] {module}: {cls}")
        if cls != "ok":
            # Same reasoning as --update-baseline: an aborted run produces no
            # "Survivors:" section, which parse_survivors cannot tell apart from
            # a clean pass. Treat it as a gate failure rather than silently
            # passing a module the tool never actually finished checking.
            print(f"[gate] FAIL {module}: mutate4py exited {code} [{cls}]")
            failed_modules.append((module, cls))
            continue
        fresh |= new_survivors(parse_survivors(module, out), baseline)
    if failed_modules:
        memcap_failed = [m for m, c in failed_modules if c == "memcap"]
        error_failed = [m for m, c in failed_modules if c == "error"]
        print(f"[gate] FAIL — {len(failed_modules)} module(s) errored:")
        # Reported as two separate classes -- see --update-baseline for why
        # blending them would contaminate the still-open exit-4 inventory.
        if memcap_failed:
            print(f"[gate]   memcap ({len(memcap_failed)}): {', '.join(memcap_failed)}")
        if error_failed:
            print(f"[gate]   error ({len(error_failed)}): {', '.join(error_failed)}")
        return 1
    if fresh:
        print(f"[gate] FAIL — {len(fresh)} new survivor(s):")
        for key in sorted(fresh):
            print(f"  {key}")
        return 1
    if excluded_changed:
        # Exit-code decision for an advisory lane: neither "fail every PR that
        # touches these six" (the tooling defect isn't the change's fault) nor
        # "pass silently" (that would hide a real coverage gap) is acceptable, so
        # this exits 0 -- but the pass line itself is never the bare, unqualified
        # "[gate] pass — no new survivors"; it must name what wasn't measured, so
        # grepping CI output for a plain pass can't mistake this run for a full one.
        print(
            f"[gate] pass — no new survivors, but {len(excluded_changed)} "
            f"changed module(s) NOT MEASURED (see mutation-exclusions.txt): "
            f"{', '.join(excluded_changed)}"
        )
        return 0
    print("[gate] pass — no new survivors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
