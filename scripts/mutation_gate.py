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

mutate4py exits 0 even when mutants survive, so pass/fail is parsed from the
"Survivors:" report section. Baseline keys exclude line numbers on purpose:
`<relpath>::<func-id>::<mutation>` stays stable across unrelated edits.
Always invokes mutate4py with --manifest-file (sidecar); the embedded manifest
mode writes into production source files and is never acceptable here.
"""

from __future__ import annotations

import argparse
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
    relpath: str, lcov: str, extra: list[str], max_workers: int
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
    # check=False deliberate: mutate4py exits 0 even with survivors, so the caller
    # must inspect returncode itself rather than rely on an exception -- a mutate4py
    # invocation that aborts (case-3 test-context disagreement, case-4 no test ran)
    # also exits non-zero with NO "Survivors:" section, and is otherwise
    # indistinguishable from a clean module with zero survivors. Returning the
    # code (not raising) keeps that distinction visible to both call sites, which
    # decide separately what a failed module means for their mode.
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, check=False)
    sys.stderr.write(proc.stderr)
    return proc.stdout, proc.returncode


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
        code = int(exit_path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None
    if code != 0:
        return None
    try:
        return stdout_path.read_text(encoding="utf-8")
    except OSError:
        return None


def _write_record(out_dir: Path, module: str, out: str, code: int) -> None:
    # stdout first, exit second: a run killed between the two writes leaves the
    # .exit file missing, which _cached_stdout treats as no record at all --
    # never as a false success or a false failure.
    stdout_path, exit_path = _record_paths(out_dir, module)
    stdout_path.write_text(out, encoding="utf-8")
    exit_path.write_text(str(code), encoding="utf-8")


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
    args = parser.parse_args()

    extra = ["--test-contexts", args.test_contexts] if args.test_contexts else []
    baseline_path = Path(args.baseline)

    if args.update_baseline:
        out_dir = Path(args.out_dir) if args.out_dir else None
        if out_dir is not None:
            out_dir.mkdir(parents=True, exist_ok=True)
        keys: set[str] = set()
        failed: list[str] = []
        for module in _all_modules():
            cached = _cached_stdout(out_dir, module) if out_dir is not None else None
            if cached is not None:
                print(f"[baseline] {module} (cached)", flush=True)
                out, code = cached, 0
            else:
                print(f"[baseline] {module}", flush=True)
                out, code = _run_mutate(
                    module, args.lcov, [*extra, "--mutate-all"], args.max_workers
                )
                if out_dir is not None:
                    _write_record(out_dir, module, out, code)
            if code != 0:
                # A non-zero exit here means mutate4py aborted before ever printing
                # a "Survivors:" section (e.g. a test-context/coverage disagreement)
                # -- parse_survivors would silently return an empty set, identical
                # to a module that genuinely has zero survivors. Recording that
                # would write a baseline with an undetectable hole in it, so this
                # module's (empty, meaningless) contribution is refused outright
                # rather than merged in.
                print(f"[baseline] FAIL {module}: mutate4py exited {code}")
                failed.append(module)
                continue
            keys |= parse_survivors(module, out)
        if failed:
            print(
                f"[baseline] refusing to write {baseline_path}: "
                f"{len(failed)} module(s) failed and were excluded: {', '.join(failed)}"
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
    failed_modules: list[str] = []
    for module in modules:
        print(f"[gate] {module}", flush=True)
        out, code = _run_mutate(module, args.lcov, extra, args.max_workers)
        print(out)
        if code != 0:
            # Same reasoning as --update-baseline: an aborted run produces no
            # "Survivors:" section, which parse_survivors cannot tell apart from
            # a clean pass. Treat it as a gate failure rather than silently
            # passing a module the tool never actually finished checking.
            print(f"[gate] FAIL {module}: mutate4py exited {code}")
            failed_modules.append(module)
            continue
        fresh |= new_survivors(parse_survivors(module, out), baseline)
    if failed_modules:
        print(
            f"[gate] FAIL — {len(failed_modules)} module(s) errored: {', '.join(failed_modules)}"
        )
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
