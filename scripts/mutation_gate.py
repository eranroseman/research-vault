"""No-new-survivors mutation gate over mutate4py.

Invoked explicitly as `python scripts/mutation_gate.py` — no shebang on purpose
(EXE001 fires on a shebang in a non-executable file, and nothing execs this directly).

Gate mode (default): mutation-test the knowledge_harness files changed since --base,
fail (exit 1) on any survivor whose key is absent from the committed baseline.
--update-baseline: blanket-run every knowledge_harness module (--mutate-all) and
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

mutate4py exits 0 even when mutants survive, so pass/fail is parsed from the
"Survivors:" report section. Baseline keys exclude line numbers on purpose:
`<relpath>::<func-id>::<mutation>` stays stable across unrelated edits.
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
SURVIVOR_RE = re.compile(r"^\s+line \d+ (?P<mutation>.+) (?P<func>func/\S+)$")


def parse_survivors(relpath: str, output: str) -> set[str]:
    keys: set[str] = set()
    in_section = False
    for line in output.splitlines():
        if line.startswith("Survivors:"):
            in_section = True
            continue
        if in_section:
            match = SURVIVOR_RE.match(line)
            if match is None:
                if line.strip():
                    in_section = False
                continue
            keys.add(f"{relpath}::{match['func']}::{match['mutation']}")
    return keys


def new_survivors(found: set[str], baseline: set[str]) -> set[str]:
    return found - baseline


def baseline_keys(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {line for line in path.read_text(encoding="utf-8").splitlines() if line}


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
            "knowledge_harness/*.py",
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
        f"knowledge_harness/{p.name}"
        for p in (ROOT / "knowledge_harness").glob("*.py")
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
    sys.stderr.write(proc.stderr)
    return proc.stdout, proc.returncode


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

    if args.update_baseline:
        out_dir = Path(args.out_dir) if args.out_dir else None
        if out_dir is not None:
            out_dir.mkdir(parents=True, exist_ok=True)
        keys: set[str] = set()
        failed: list[tuple[str, str]] = []
        for module in _all_modules():
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
        baseline_path.write_text("\n".join(sorted(keys)) + "\n", encoding="utf-8")
        print(f"[baseline] {len(keys)} survivors written to {baseline_path}")
        return 0

    modules = changed_modules(args.base)
    if not modules:
        print("[gate] no changed knowledge_harness modules; pass")
        return 0
    baseline = baseline_keys(baseline_path)
    fresh: set[str] = set()
    failed_modules: list[tuple[str, str]] = []
    for module in modules:
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
    print("[gate] pass — no new survivors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
