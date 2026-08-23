# mutate4py 0.1.4 — three defects, two on the parallel worker path, plus a one-line off-by-one

## Summary

Adopting mutate4py 0.1.4 as a pinned mutation-testing dependency surfaced four
distinct defects over two working sessions. They are reported together
because they interact: an observability gap (defect 2) is what made an
intermittent failure (eventually traced to defect 1) take a full working day
to diagnose, and defects 1 and 3 share the same code path
(`--max-workers >= 2` worker provisioning). This document covers all four so
a maintainer reads one account of the tool's session rather than four
unrelated issues.

1. **Memory leak on the parallel path.** `--max-workers >= 2` leaks memory
   inside the worker processes themselves (not by spawning more of them) at
   a measured rate on the order of ~195 MB/s once workers are running,
   exhausting a 23 GB RAM + 6 GB swap host in about 3.5 minutes. This killed
   the host VM outright, repeatedly, before it was diagnosed. `--max-workers
   1` (serial) is memory-stable.
2. **Pytest output destroyed at the instant of failure.** Every mutant's
   pytest stdout/stderr is sent to `os.devnull` (forking path) or captured
   and then discarded (subprocess path) unconditionally, and the per-run
   worker tree is deleted in a `finally` clause at the same moment a failure
   is reported. When a mutant run fails, nothing that could explain why
   survives long enough to be read.
3. **`uv` required for parallel worker provisioning, with no fallback.**
   `uv venv` + `uv sync` provision every worker whenever `--max-workers >=
   2`, but `uv` is not a declared dependency, is absent from GitHub's
   `ubuntu-24.04` runner image, and a missing `uv` surfaces as an uncaught
   `FileNotFoundError` during provisioning rather than a diagnosable error
   or a serial fallback.
4. **One-character off-by-one in `_numbits_to_lines`.** `--test-contexts`
   test selection reads one line off from what coverage.py's own numbits
   encoding stores, at every covered line, causing false "line not covered"
   results and narrowing test selection incorrectly.

Two of the four (2 and 4) have a venv-local source patch already applied and
verified in this project's environment, documented in full below — that is
the part a maintainer can verify fastest, since the fix is a one- or
two-line diff against the same file this report quotes. Defects 1 and 3 have
no source-level mitigation recorded here; they were worked around
operationally (a memory cap plus a serial fallback pass, and pinning
`--max-workers 1` in CI, respectively).

## Environment

- Python 3.12.3
- mutate4py 0.1.4 (`pip show mutate4py`: `Requires:` empty; package
  METADATA carries no `Requires-Dist` line at all; `Requires-Python:
  >=3.11`)
- coverage.py 7.15.4
- WSL2, kernel `6.6.87.2-microsoft-standard-WSL2`
- 12 cores (`nproc`)
- `.wslconfig`: `memory=25165824000` (~23.4 GiB), `swap=6291456000` (~5.9
  GiB), `networkingMode=mirrored`. The sampler below records
  `mem_total_mb=23465` (~22.9 GiB) and a swap ceiling of 6000 MB, consistent
  with that config.

## Defect 1 — memory leak on the parallel path (`--max-workers >= 2`)

### The curve

Evidence: `.mutate4py/memlog.tsv`, a memory sampler at a 2-second interval,
columns `iso, mem_total_mb, mem_avail_mb, swap_free_mb, py_rss_mb, py_procs,
load1`. The file holds roughly 54 minutes of pre-run idle sampling
(`01:00:03` to `01:54:01`) — during that stretch `py_procs` is 3 almost the
entire time (1,063 of 1,515 samples), briefly rising to 5-9 during unrelated
background activity, and `py_rss_mb` stays in the tens of MB apart from one
brief excursion to 314 MB. A marker line, `COLDRUN_START 01:54:01`, records
the start of a mutate4py run launched against a fully wiped
worker/forkserver/manifest state. `--max-workers 4` and no cgroup cap: the
process count settles at 9 for the duration of the climb (1 coordinator + 4
workers × 2 processes each), and RSS goes on to pass 8 GB with swap draining
to zero — both signatures of an uncapped run, not asserted independently of
the data below.

After the marker:

- `01:54:03` (RSS 80 MB, 6 procs) through `01:55:31` (RSS 88 MB, 6 procs):
  roughly flat for the first ~90 s — collection/baseline work, not yet
  mutant execution.
- `01:55:37`: process count jumps to 9, briefly overshoots to 13, and
  settles.
- `01:55:49` onward: process count is **exactly 9 for every sample** through
  the last line in the file — verified by taking the distinct set of
  `py_procs` values across that whole window, which is `{9}`.
- `01:55:49` (RSS 2,263 MB) to `01:57:26` (RSS 21,192 MB, the last line in
  the file): 97 seconds, RSS growth of 18,929 MB — **~195 MB/s**, with
  process count constant. This is growth inside existing processes, not
  proliferation of new ones.
- Over the whole visible run, `01:54:03` (RSS 80 MB) to `01:57:26` (RSS
  21,192 MB): 203 s, average ~104 MB/s — lower than the steady-state rate
  because the first ~90 s is flat, not because the growth itself is
  sub-linear once workers are running.
- `mem_avail_mb` fell from 17,063 MB (`01:54:03`) to 215 MB (`01:57:26`).
- `swap_free_mb` held near its 6,000 MB ceiling until `01:56:48` (5,996 MB
  free), then drained to 0 by `01:57:26` — 38 seconds to exhaust ~6 GB of
  swap.
- The file's last line is `01:57:26`; there is no further sample. That is
  consistent with the host VM dying at or immediately after that point — no
  `dmesg` record survives a VM restart to pin the exact death instant, and
  the sampler (reopen-per-write, specifically so a kill could not take the
  tail of the curve) simply never got to write another line.
- Total elapsed from `COLDRUN_START` to the last sample: 3 min 25 s.

### The A/B/C isolation

Once a safe way to reproduce this was needed, all further runs went under a
cgroup memory cap (WSL2 here runs systemd with cgroup v2's memory
controller):

```
systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=0 --quiet -- <command>
```

The guard was proven against a deliberate allocator first: killed at ~490 MB
under a 512 MB cap, exit 137, host VM survived. Every run below used it, and
the VM survived all of them.

Three runs, all on `knowledge_harness/selectors.py` (71 total mutation
sites, 54 covered/selected — from each run's own header, identical across
all three), all under the same 8 GB cap:

- **A** — this project's patched venv (diagnostic-capture patch from defect
  2 active), `--max-workers 4`: SIGTERM at the cap after 126 s. Log
  (`.mutate4py/runA_patched.log`) records 40 of 54 mutants — independently
  re-counted directly from the file (`grep -c '^\['` = 40; indices reach as
  high as 53 because parallel workers report completion out of dispatch
  order).
- **B** — same patched venv, diagnostic-capture code path disabled,
  `--max-workers 4`: SIGTERM at the cap after 123 s. Log
  (`.mutate4py/runB_unpatched.log`) also records exactly 40 of 54 mutants,
  same index range up to 53. **A and B behave identically**, which rules out
  this project's own diagnostic-capture patch as the leak's cause — that
  patch is fd-based (one file descriptor per `pytest.main()` call, `dup2`'d
  and closed) and holds nothing in memory.
- **C** — same patched venv, `--max-workers 1` (serial), same 8 GB cap: no
  crash. Exceeded 10 minutes at 21 of 54 mutants (`.mutate4py/runC_serial.log`
  holds exactly 21 sequential entries, `[1/54]` through `[21/54]`,
  independently re-counted). Memory was reported flat over that span: 18.1
  GB available, 5.4 GB used, zero growth (recorded in the working ledger at
  the time of the run; the raw log itself carries no memory readings, only
  mutant results — flagged here so this figure's provenance is explicit).
  Per-mutant throughput: ~28 s/mutant serial vs. ~3 s/mutant parallel, i.e.
  serial is about 9x slower — the cost of avoiding the leak by this route.

**A vs. B** acquits this project's own diagnostic patch. **A vs. C**
isolates the leak to the parallel (`--max-workers >= 2`) code path
specifically: serial is memory-stable, parallel is not, on the same file,
same coverage, same host.

### What this leak retroactively explains

Before it was identified, the same host had already lost several long
mutation-testing runs to what looked like a background-process lifetime
cap (~35 minutes), an intermittent `mutate4py` exit 4 (pytest "usage error —
before collecting any test", rising in frequency with cumulative work
across a run), and three outright WSL VM crashes. All of it is consistent
with one mechanism: memory accumulates until the VM dies, with the visible
symptom depending on exactly when in that climb the host gave out. Short,
isolated reproductions of the exit-4 case never triggered it because a
single module run from a cold tree never reaches the ceiling.

### Mitigation status

No source-level fix is recorded in this project's venv for this defect —
the leak was not isolated below "the parallel worker-provisioning/execution
path" (worker copy provisioning plus the forking executor together), so
there was nothing to patch with confidence. It was contained operationally
in the consuming project's own script: run the parallel path under the
cgroup cap above, and re-run (serially) whatever module the cap kills.

## Defect 2 — pytest output destroyed at the instant of failure

### How this was found

The intermittent exit-4 above was investigated for roughly a full working
day before the memory leak was identified. Six independent attempts to
reproduce it in isolation all came back negative: pytest via subprocess with
individual node ids; pytest via subprocess with the full covering node-id
list; the real `ForkingExecutor.run()` after `prime()`; the already-bounded
per-module worker lifetime (mutate4py already runs one fresh process per
module, so cross-module accumulation was ruled out directly, not inferred);
complete `tests/` tree diffs on two sampled worker copies; and a file-count
discrepancy between worker copies that turned out to be asynchronous
`.pyc` generation, not a missing source file.

Two probes then established why none of that worked:

- **Probe 1** — read pytest's own error text for which selector failed to
  resolve. No data: the log held no pytest stderr at all, even though the
  code forwards it (`run_argv`'s `subprocess.run(..., capture_output=True)`
  does capture it). The output was being suppressed before it could reach
  anywhere a human could read it.
- **Probe 2** — preserve a worker tree at the moment of an exit-4. Not
  achievable by polling: a snapshot catcher armed at a 2-second interval,
  then re-armed at 0.2 seconds, both times captured only stale directories
  from a prior run — the failing module's worker tree was already gone by
  the time the error line became visible. mutate4py's stdout reaches a
  caller's log at or after process exit (pipe flush), so by the time the
  error is externally visible, the process has already exited and its
  worker tree has already been removed. The evidence is destroyed
  synchronously with the evidence of the evidence; no polling rate fixes
  this from outside the process.

### Source confirmation

Two mechanisms combine to produce this. First, in `_forking_executor.py`,
`_run_pytest_output_suppressed` (the path an actual `--max-workers`-driven
run uses) redirected every mutant's pytest stdout/stderr to
`os.devnull` unconditionally, on every exit code. Second, in `_cmd.py`,
`run_argv` (the subprocess-executor path) called
`subprocess.run(argv, cwd=cwd, capture_output=True, timeout=timeout)` and
then discarded `result.stdout`/`result.stderr` entirely regardless of
`result.returncode`:

```python
# _cmd.py, run_argv, before the patch below existed
result = subprocess.run(argv, cwd=cwd, capture_output=True, timeout=timeout)
...
return classify_exit_code(result.returncode)   # stdout/stderr never read
```

Separately, `_workers.py::run_parallel` removes the whole per-run worker
tree in a `finally` clause the same instant a run concludes — success or
failure alike:

```python
    finally:
        shutil.rmtree(run_root, ignore_errors=True)
```

So even writing something to disk under a worker's own `cwd` would not have
survived to be inspected afterward; the tree is gone by the time an error
is reported to the caller.

### The patch applied in this venv (2026-08-23, diagnostic-only)

Both sites were patched to capture pytest's output to a durable location
under the *calling* venv's own repo root (derived from `sys.prefix`, not
`cwd`, specifically because `cwd` may be a per-worker tree the `finally`
clause above is about to delete) rather than changing what runs, what is
selected, or how a mutant is classified.

`_forking_executor.py`:

```python
def _diagnostic_capture_dir() -> str:
    """This venv's repo root .mutate4py/pytest-output/ -- derived from
    sys.prefix rather than `cwd`, since `cwd` here may be a per-Worker tree
    copy that _workers.run_parallel deletes in its `finally` clause; see the
    PATCHED note on `_run_pytest_output_suppressed` below."""
    return os.path.join(os.path.dirname(sys.prefix), ".mutate4py", "pytest-output")


def _open_diagnostic_capture_fd(args: list[str], cwd: str) -> int:
    """Best-effort: open a fresh capture file for one pytest.main() call,
    keyed by pid + monotonic_ns (each forked child gets a fresh pid, so
    concurrent mutants across Workers never collide), with a one-line
    argv/cwd header. Falls back to the original devnull fd on any failure --
    a diagnostic-capture failure must never turn a real run into a failed
    one (note: this covers open failures, not a mid-run ENOSPC on the
    already-dup2'd fd, which would surface inside pytest same as it would
    for any other full disk).
    """
    try:
        diag_dir = _diagnostic_capture_dir()
        os.makedirs(diag_dir, exist_ok=True)
        path = os.path.join(diag_dir, f"pytest-{os.getpid()}-{time.monotonic_ns()}.log")
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
        os.write(fd, f"# argv: {args!r}\n# cwd: {cwd!r}\n".encode())
        return fd
    except OSError:
        return os.open(os.devnull, os.O_WRONLY)


def _run_pytest_output_suppressed(pytest_module, args: list[str], cwd: str) -> int:
    """Run pytest.main(args) with cwd set and stdout/stderr redirected to devnull.
    ...
    PATCHED 2026-08-23 (local venv only, not upstream, diagnostic-only):
    this function sent every mutant's pytest stdout/stderr to os.devnull
    unconditionally -- the reason six independent attempts to reproduce an
    intermittent `mutate4py` exit 4 under --test-contexts --max-workers 4
    found nothing: pytest's own words about the abort were destroyed the
    instant it happened, and _workers.run_parallel additionally rmtree's the
    whole per-run Worker tree in its `finally` clause the same instant an
    error is reported, so nothing written under `cwd` would have survived
    either. Those bytes now land in a file under this venv's repo root
    (see _diagnostic_capture_dir) instead, with an argv/cwd header and an
    exit-code footer. Capture-only: same pytest.main() call, same return
    value, same fd-restore sequence; any capture failure falls back to
    devnull exactly as before this patch.
    """
    prev_cwd = os.getcwd()
    capture_fd = _open_diagnostic_capture_fd(args, cwd)
    saved_stdout = os.dup(1)
    saved_stderr = os.dup(2)
    try:
        os.chdir(cwd)
        os.dup2(capture_fd, 1)
        os.dup2(capture_fd, 2)
        exit_code = int(pytest_module.main(args))
        sys.stdout.flush()
        # ... (fd restore continues unchanged below this point)
```

`_cmd.py`:

```python
def _diagnostic_capture_dir() -> str:
    """This venv's repo root .mutate4py/pytest-output/ -- same location and
    derivation as _forking_executor._diagnostic_capture_dir (duplicated
    rather than imported to keep this diagnostic patch self-contained per
    file; see that module's PATCHED note for the full rationale)."""
    return os.path.join(os.path.dirname(sys.prefix), ".mutate4py", "pytest-output")


def _write_diagnostic_capture(argv: list[str], cwd: str, result: "subprocess.CompletedProcess") -> None:
    """Best-effort: dump argv/cwd/returncode plus both captured streams to a
    file under this venv's repo root. Any failure (permissions, disk full,
    sys.prefix not a venv) is swallowed -- a diagnostic-capture failure must
    never turn a real run into a failed one.

    PATCHED 2026-08-23 (local venv only, not upstream, diagnostic-only):
    run_argv already called subprocess.run(capture_output=True) but then
    discarded result.stdout/result.stderr entirely, on every exit code --
    the SubprocessExecutor path's share of the same swallowed-output problem
    _forking_executor._run_pytest_output_suppressed's matching patch
    describes for the forking path (six independent attempts to reproduce
    an intermittent `mutate4py` exit 4 under --test-contexts --max-workers 4
    found nothing, because pytest's own words were never kept anywhere).
    Capture-only: the classification `run_argv` returns is unchanged.
    """
    try:
        diag_dir = _diagnostic_capture_dir()
        os.makedirs(diag_dir, exist_ok=True)
        path = os.path.join(diag_dir, f"pytest-{os.getpid()}-{time.monotonic_ns()}.log")
        with open(path, "wb") as f:
            f.write(f"# argv: {argv!r}\n# cwd: {cwd!r}\n# returncode: {result.returncode}\n".encode())
            if result.stdout:
                f.write(result.stdout)
            if result.stderr:
                f.write(result.stderr)
    except OSError:
        pass


def run_argv(argv: list[str], cwd: str, timeout: float) -> str:
    ...
    try:
        result = subprocess.run(argv, cwd=cwd, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "timeout"
    except OSError:
        return "killed"
    _write_diagnostic_capture(argv, cwd, result)
    return classify_exit_code(result.returncode)
```

Both writes happen on every run, not only on failure — filtering on
`returncode` risked excluding the very case the patch exists for, at a cost
of a few thousand small files against roughly 0.6 s per mutant.

This dovetails with mutate4py's own existing design: `_cmd.py` already
distinguishes exit codes 4 and 5 ("usage-error", "no-tests-collected") from
an ordinary "killed" outcome in `classify_exit_code`. The classification
already exists; only the diagnostic text behind *why* a given run landed in
that category was missing.

### Consequence

When a mutant run fails, the tool destroys the only artifact that could
explain it (pytest's own stdout/stderr), synchronously with reporting the
failure — both by design (the devnull redirect / discarded
`capture_output`) and incidentally (the worker-tree `rmtree` in
`run_parallel`'s `finally` clause, which would also remove anything written
under the worker's own `cwd`). This is framed as an observability defect,
not a correctness bug — nothing about mutant classification is wrong
because of it — but it is the one that made defect 1 expensive to find: six
negative reproductions and roughly a working day passed before a memory
sampler, independent of pytest's own output, finally explained the
intermittent failures as memory exhaustion under the parallel path.

### Mitigation status

**Venv-patched**, 2026-08-23, both sites quoted above in full. Diagnostic
only — verified to never change what runs, what gets selected, or how a
mutant is classified; every failure inside the capture path itself is
swallowed so a diagnostic-capture failure can never turn a real run into a
failed one.

## Defect 3 — `uv` required for parallel worker provisioning, no fallback

### The code

`_workers.py::_provision_worker` provisions every worker whenever
`--max-workers >= 2`:

```python
def _provision_worker(worker_root: str) -> None:
    """Run uv venv + uv sync to provision a worker copy."""
    subprocess.run(
        ["uv", "venv"],
        cwd=worker_root,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["uv", "sync"],
        cwd=worker_root,
        capture_output=True,
        check=True,
    )
```

Neither call is wrapped in a `try`/`except`. `subprocess.run` raises
`FileNotFoundError` when `argv[0]` cannot be resolved on `PATH`; nothing in
`_provision_worker` or its caller (`run_parallel`, via
`_provision_workers`) catches that specific error, so a missing `uv`
propagates as an uncaught Python exception during provisioning — before any
mutant has run, so the tool appears to have simply crashed rather than
reporting a missing-dependency condition.

### Why it matters

- `uv` is not a declared dependency: `pip show mutate4py` in this project's
  venv reports `Requires:` empty, and the package's METADATA has no
  `Requires-Dist` line at all (the README's own "Develop" section confirms
  the intent — "stdlib `ast`, zero runtime deps" — which is accurate for
  running mutate4py itself, but `uv` is still a hard runtime requirement of
  the `--max-workers >= 2` path specifically).
- `uv` is absent from GitHub's `ubuntu-24.04` runner image by default —
  established directly in this project's own CI setup work (a parallel
  finding, "D3", from a related task in the same session): the mutation
  gate could never have run in CI as configured, because the parallel path
  it invoked would hit exactly this `FileNotFoundError`.
- There is no serial fallback. `--max-workers 1` avoids the `uv`
  dependency entirely (worker provisioning is only reached at `>= 2`), but
  that must be chosen by the caller in advance — mutate4py does not detect
  `uv`'s absence and drop to serial itself, nor does it surface a clear
  "install uv" error before attempting provisioning.

### Related packaging friction, same code path

When the *consuming* project's own `pyproject.toml` declares a
`requires-python` range wider than mutate4py's own `>=3.11` (for example
`>=3.10`), `uv sync` fails to resolve a worker environment for it. This
project had to raise its own `requires-python` floor to `>=3.11`
specifically to make `--max-workers >= 2` resolve at all — a constraint
that ripples into the consuming project's own supported-Python floor,
driven entirely by mutate4py's worker-provisioning path rather than by
anything the consuming project's own code requires.

This is the same worker-provisioning code path implicated in defect 1 (the
memory leak) — both live in parallel-worker provisioning/execution, worth
carrying as one upstream note rather than two.

### Mitigation status

No source-level fix is recorded here — this is an architectural gap (a
missing dependency declaration and a missing fallback), not a one-line
patch. It was worked around operationally: CI now pins `--max-workers 1`.

## Defect 4 — off-by-one in `_numbits_to_lines` (cross-linked, already prepared for filing)

This defect was found and patched in an earlier stage of the same session
and is folded in here rather than filed separately, per the instruction
that a maintainer should read one coherent account of this tool's session.

### The defect

`_test_selection.py::_numbits_to_lines` decodes a coverage.py numbits blob
into a set of covered line numbers, to drive `--test-contexts` selection.
coverage.py's own encoder, `nums_to_numbits` in `coverage/numbits.py`
(independently confirmed against this project's installed coverage.py
7.15.4):

```python
b[num // 8] |= 1 << num % 8
```

and its own decoder, `numbits_to_nums` in the same file (also independently
confirmed):

```python
nums.append(byte_i * 8 + bit_i)
```

— i.e. line number = `byte_index * 8 + bit_index`, no offset. Shipped
mutate4py 0.1.4 decoded it as:

```python
lines.add(byte_idx * 8 + bit_idx + 1)
```

one line off from every real coverage.py numbits consumer. Every
`tests_for_line(path, N)` call therefore actually checked line `N - 1`, so
any covered site immediately preceded by a comment or blank line resolved
to an *uncovered* line and false-positived into an incorrect selection
result.

Verified against the real shipped function before the fix:
`tests_for_line(__main__.py, 63)` returned `('line-absent', [])` against a
line independently confirmed covered (via `coverage.numbits.numbits_to_nums`
directly, and via a standalone isolated single-test coverage run).
Monkeypatching out the `+ 1` changed the same call to `('narrowed', 16
tests)`; a second case, `appendlog.py:37`, went from `('line-absent', [])`
to `('narrowed', 215 tests)`.

### The patch applied in this venv

`_test_selection.py`:

```python
def _numbits_to_lines(numbits: bytes) -> set[int]:
    """Decode a coverage.py numbits blob into a set of 1-based line numbers.

    byte N bit B → line N*8 + B (coverage.py's actual packing, verified against
    coverage/numbits.py's nums_to_numbits: `b[num // 8] |= 1 << num % 8`).

    PATCHED 2026-08-22 (local venv only, not upstream): shipped mutate4py 0.1.4
    added a spurious `+ 1` here, one line off from every real coverage.py numbits
    consumer. Verified live: TestContextDB.tests_for_line() returned
    ("line-absent", []) for two lines directly confirmed covered by
    coverage.numbits.numbits_to_nums (the stdlib decoder) and by a standalone
    isolated single-test coverage run; with this fix, the same lookups return
    ("narrowed", [...]) with the correct covering-test counts (16 and 215 in the
    two verified cases). See mutation-baseline.txt's adjacent note and this
    task's report for the full writeup; upstream issue pending.
    """
    lines: set[int] = set()
    for byte_idx, byte_val in enumerate(numbits):
        for bit_idx in range(8):
            if byte_val & (1 << bit_idx):
                lines.add(byte_idx * 8 + bit_idx)
    return lines
```

The only functional change is dropping the trailing `+ 1` in the final
`lines.add(...)` call; the docstring was rewritten in place to cite the
correct formula and its source.

### Mitigation status

**Venv-patched**, 2026-08-22, one line, quoted in full above. Applies only
under `--test-contexts`; the tool's default (no test-context db) coverage
path does not use this function.

## Reproduction recipe

All four defects can be reproduced from a project that already has a
coverage-instrumented lcov file (`pytest --cov --cov-branch
--cov-report=lcov:lcov.info`) and a module with a non-trivial number of
covered mutation sites. This project used `knowledge_harness/selectors.py`:
71 total mutation sites, 54 covered/selected.

### Defect 1 (memory leak) — reproduce only under a memory cap

**Without a hard memory cap, this reproduction will kill the host.** On
this machine it killed the WSL2 guest VM outright three times — taking
every other process on it down with it — before the cap below was adopted.
Do not run `--max-workers >= 2` against an uncapped host to reproduce this.

This WSL2 guest runs systemd with cgroup v2's memory controller, so:

```
systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=0 --quiet -- \
  mutate4py path/to/module.py --max-workers 4 --lcov lcov.info
```

(On a host without systemd/cgroup v2, substitute an equivalent hard cap —
a container memory limit or `ulimit`-based bound — but use one; the point
of the cap is that the reproduction fails loud and contained instead of
taking the host down.)

Confirm the guard itself works before trusting it on a real run: launch a
deliberate memory-hog script under the same `systemd-run` invocation and
confirm it is killed at the cap (exit 137) rather than the host dying —
this project's guard was proven that way first, killed at ~490 MB under a
512 MB test cap.

Steps:

1. Run the command above with `--max-workers 4` (or any value `>= 2`) on a
   module with enough covered sites to run for a couple of minutes. Expect
   `SIGTERM` at the cap — this project saw it at 123-126 s on a 54-site
   module under an 8 GB cap.
2. Re-run the identical command with `--max-workers 1`. Expect it to run
   past ten minutes with memory flat, if the cap is large enough to let it
   complete (or simply to not be killed).
3. Optional, to see the mechanism directly rather than just the outcome:
   sample the mutate4py process tree's RSS and process count at a short
   fixed interval (2 s was used here) while running step 1. Expect process
   count to hold constant while RSS climbs at roughly the rate reported
   above (~195 MB/s once workers are actively running mutants, on this
   host/workload).

### Defect 2 (observability) — reproduce the destruction, not the trigger

Any pytest-side failure during a mutant run (not just this project's
still-unexplained-in-isolation exit-4) demonstrates the defect: run a
module under `--max-workers >= 1` and confirm that (a) no pytest
stdout/stderr for any individual mutant reaches any log the caller can
read, and (b) if the run is `--max-workers >= 2`, the worker directory for
a given mutant is already gone by the time any external poll can observe
it — even at a 0.2 s poll interval, confirmed here twice.

### Defect 3 (`uv` dependency) — reproduce in an environment without `uv`

Run in any environment that genuinely has no `uv` on `PATH` — a fresh
`python:3.12` container with mutate4py `pip install`ed and nothing else, or
a stock `ubuntu-24.04` GitHub Actions runner (where its absence was
established directly, in this project's own CI setup work):

```
mutate4py path/to/module.py --max-workers 2 --lcov lcov.info
```

Removing `uv` from `PATH` on a workstation that already has it installed is
not a reliable substitute — `uv` commonly lives under `~/.local/bin` or
`~/.cargo/bin`, both ahead of most `PATH`-stripping one-liners, so a
naive attempt to hide it can silently fail to reproduce. The point is that
`uv venv` inside `_provision_worker` then raises `FileNotFoundError`,
uncaught, before any mutant runs.

### Defect 4 (off-by-one) — reproduce with `--test-contexts`

Build a test-context db (`--build-test-contexts`), then compare
`TestContextDB.tests_for_line()` for any covered line immediately preceded
by a comment or blank line against `coverage.numbits.numbits_to_nums()` for
the same source file's numbits blob. The tool's answer will read one line
lower than what the blob actually contains, and will report the real line
as uncovered (`'line-absent'`) when it is not.

## Which defects have a venv-side mitigation recorded here

|  # | Defect | Venv-patched? | Where |
|---|---|---|---|
| 1 | Memory leak, parallel path | No — contained operationally (cgroup cap + serial fallback in the calling project) | — |
| 2 | Pytest output destroyed at failure | **Yes**, 2026-08-23, diagnostic-only | `_forking_executor.py::_run_pytest_output_suppressed` / `_open_diagnostic_capture_fd`; `_cmd.py::run_argv` / `_write_diagnostic_capture` |
| 3 | `uv` required, no fallback | No — worked around operationally (`--max-workers 1` in CI) | — |
| 4 | Off-by-one in `_numbits_to_lines` | **Yes**, 2026-08-22, one-line fix | `_test_selection.py::_numbits_to_lines` |

Defects 2 and 4 are the fastest for a maintainer to verify independently:
each patch is a small, self-contained diff against a single function, with
its rationale recorded inline in the function's own docstring in the
patched file.

## What could not be sourced from the evidence on hand

- The exact allocation site of the leak inside mutate4py's worker or
  forking-executor code was not isolated — only that it is confined to the
  `--max-workers >= 2` path (A vs. C) and is not caused by this project's
  own diagnostic-capture patch (A vs. B). Narrowing it further would need
  memory instrumentation inside mutate4py itself (e.g. `tracemalloc` across
  a worker's lifetime), which was not attempted.
- The precise instant the WSL2 VM died during the uncapped run recorded in
  `memlog.tsv` is not known — `01:57:26` is the sampler's last written line,
  not a confirmed death timestamp, and no OS-level crash record survives a
  VM restart (`dmesg` is cleared).
- Whether every historical intermittent exit-4 this project saw is fully
  explained by the memory leak, or whether a residual, distinct cause
  remains, was not re-verified after the leak was identified. The six
  negative reproductions recorded above were all performed and interpreted
  before the leak was found, and the leak was accepted as a sufficient
  explanation for the observed pattern (rising failure frequency with
  cumulative work, moving stop-site, all six isolated reproductions passing
  clean) without re-running each prior negative case to confirm the leak
  specifically, rather than something else, was responsible for each one.
