"""Launcher working around a mutmut 3.7.0 / pytest 9.1.1 re-selection defect.

pytest 9.1.1 re-escapes auto-generated parametrize ids containing control
characters on EVERY in-process re-collection (verified: call 1 collects
``['\\n'-actor]``, call 2 collects ``['\\\\n'-actor]`` for the same item).
mutmut records ids during stats (single-escaped) and re-selects them in later
in-process pytest.main calls (clean run) and in forked children (per-mutant
runs) -- all re-collections, so the recorded ids are never found: pytest exit
4, BadTestExecutionCommandsException, aborted run / false kills.

Fix applied here, at launcher level only: when building pytest args, widen any
test id whose param part contains a backslash to the whole test function
(``path::test[param]`` -> ``path::test``). Sibling params that never execute
the mutated function pass regardless of the mutant, so the widening is
semantics-preserving; only wall-clock inflates.

Provenance: "mutmut pilot -- knowledge-harness (pre-registered data
collection)", 2026-08-23, /home/eranr/kh-mutmut-pilot-report.md (operational
friction log, item 6); upstream defect draft filed in-repo at
docs/research/2026-08-23-mutmut-defect-reports.md.

Usage: python scripts/mutmut_shims/run_mutmut.py <mutant-name-pattern>
[mutmut run options]. Activated in this repo via
PYTHONPATH=scripts/mutmut_shims on mutmut invocations only.
"""

# ruff: noqa: PLW2901

import sys

from mutmut import __main__ as mm

_orig = mm.PytestRunner._pytest_args_regular_run


def _widened(tests):
    fixed = []
    seen = set()
    for t in tests:
        head, bracket, param = t.partition("[")
        if bracket and "\\" in param:
            t = head
        if t not in seen:
            seen.add(t)
            fixed.append(t)
    return fixed


def patched(self, tests):
    return _orig(self, _widened(list(tests)))


mm.PytestRunner._pytest_args_regular_run = patched

sys.argv = ["mutmut", "run", *sys.argv[1:]]
mm.cli()
