# mutmut / pytest defect reports

Two defects met adopting mutmut 3.7.0 against a real Python test suite; `scripts/mutmut_shims/`
works around both. Not filed upstream (#67, closed 2026-09-16).

## Report 1: configuration loaded at import time breaks subprocess imports from a foreign cwd

**Project:** mutmut. **Versions:** mutmut 3.7.0, pytest 9.1.1, Python 3.12.

### Reproduction

1. Configure mutmut normally for a project (a `[tool.mutmut]` section in `pyproject.toml` with
   `source_paths` pointing at the package to mutate).
2. Include, anywhere in the covering test suite, a test that launches a subprocess (for example
   `subprocess.run([sys.executable, ...], cwd=some_other_dir)`) whose working directory is not the
   project root — a temporary fixture directory is enough — and have that subprocess import one of
   the mutated modules.
3. Run `mutmut run`.
4. Separately, run bare `mutmut --help` in a directory that has no mutmut configuration at all.

### Observed vs. expected

Observed: every mutated module imports `mutmut.mutation.trampoline`, which imports
`mutmut.__main__`, which imports `mutmut/utils/safe_setproctitle.py`; line 15 of that file calls
`Config.get()` at module level. `Config.get()` discovers configuration by searching
`pyproject.toml` / `setup.cfg` starting from the current working directory. Any process — including
a subprocess spawned by a test, with a working directory the test chose for its own reasons and
with no relation to config discovery — that imports a mutated module from a directory without a
discoverable mutmut config dies with `FileNotFoundError` at import time, before any of its own code
runs. The same defect is visible even with no test suite involved: `mutmut --help` in an
unconfigured directory crashes with the identical traceback instead of printing help text.

Expected: importing a module that mutmut has instrumented should not require ambient, cwd-relative
discovery of a project config file. At minimum, requesting help text, or importing a mutated module
from a subprocess whose working directory has nothing to do with the mutation run, should not raise.

### Impact

- **Aborted runs.** If the affected subprocess is exercised during mutmut's "collect stats" phase,
  the whole run aborts (observed as the stats phase failing with a nonzero return and the run
  refusing to proceed to mutant execution).
- **False kills.** If stats happen to pass despite the defect, the same import-time crash recurs
  identically under every mutant, so any test assertion that depends on that subprocess's output
  fails for a reason unrelated to the mutant — inflating the "killed" count with false positives
  rather than real detections.

### Workaround

A `sitecustomize.py` module, activated via `PYTHONPATH` on mutmut invocations only, that detects
it is running inside a mutmut process (`MUTANT_UNDER_TEST` present in the environment) and, only
when normal config discovery fails, seeds a benign in-memory `Config` so that import succeeds and
trampoline dispatch works correctly. It never changes the working directory and never touches any
process outside a mutmut run. See `scripts/mutmut_shims/sitecustomize.py` in this repository for
the full, working implementation.

## Report 2: auto-generated parametrize ids are re-escaped on repeated in-process collection

**Project:** most plausibly pytest (see attribution note below); files against mutmut because that
is where the failure surfaces. **Versions:** pytest 9.1.1, mutmut 3.7.0, Python 3.12.

### Reproduction

1. Parametrize a test with a raw value that pytest must escape to build a display id — for example
   a string containing a literal control character such as `\n` — and let pytest auto-generate the
   id from that value rather than supplying an explicit id string.
2. In a single process, call `pytest.main()` (or otherwise trigger collection) once. The item
   collects under an id such as `test_name[<escaped-once>]`.
3. In the same process, call `pytest.main()` a second time in a way that re-collects the same test
   (mutmut does this: once during its "clean" run and once per mutant, both inside the parent
   process or in forked children that inherit the parent's already-collected state).
4. The item now collects under a *different* id — the parameter value has been escaped again,
   compounding the first pass's escaping — for the identical underlying test.

### Observed vs. expected

Observed: the node id pytest generates for a given parametrized test is not stable across repeated
collection passes within one process; each additional in-process collection re-escapes an id that
was already escaped by the previous pass. A node id recorded from an earlier collection can no
longer be used to select that exact item in a later one. Only ids that are auto-generated from raw
values containing control characters are affected; ids supplied as an explicit, already-escaped
string are stable across repeated collection.

Expected (mutmut's operating assumption): a parametrize id generated for a given test/parameter pair
is a stable identifier that can be recorded once and reused later, including in a forked child
process that inherited the parent's collection state.

### Impact

mutmut records node ids for each test's covering set during its stats phase and re-selects those
exact ids to run the covering tests against each mutant. When an id is one of the unstable,
auto-generated kind, re-selection fails: pytest exits with code 4 ("usage error" / not found),
and mutmut surfaces this as `BadTestExecutionCommandsException`, aborting the run for any module
whose covering set includes such a test.

### Workaround

A launcher that wraps mutmut's CLI entry point and monkeypatches its pytest-argument builder:
before handing a list of recorded test ids to pytest, any id whose parametrize bracket contains a
backslash — the signature of an auto-generated, control-character-bearing id — is widened to the
whole test function, dropping the specific parameter selector. This is semantics-preserving: sibling
parameter values that never execute the mutated code still pass regardless of which mutant is
active, at the cost of inflating the covering set (and therefore wall-clock time) for affected
tests. See `scripts/mutmut_shims/run_mutmut.py` in this repository for the full implementation.

### Attribution note

The mechanism at fault — pytest generating a fresh, more-escaped id on each collection pass within
one process, rather than a stable one — sits in pytest's own id-generation code, not in mutmut, so
this report is best read as a pytest defect. The caveat worth keeping in the same conversation:
pytest's own guidance around calling `pytest.main()` more than once in a single process is that this
usage pattern carries known sharp edges, so pytest's position may be that in-process re-collection
is not a fully supported scenario in the first place. If so, the more durable fix may sit on the
mutmut side regardless of pytest's stance — for example, not depending on cross-call id stability
when re-selecting tests in-process, or re-collecting fresh rather than reusing ids across calls.
Both projects have reason to see this report.
