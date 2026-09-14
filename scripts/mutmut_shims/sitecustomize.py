"""Shim working around mutmut 3.7.0's import-time config load.

Stock mutmut 3.7.0 loads its config at IMPORT time (mutmut/utils/
safe_setproctitle.py line 15 calls Config.get() at module level, pulled in by
the trampoline import every mutated module performs). Any subprocess that
imports a mutated module from a cwd without a discoverable mutmut config --
this suite's fail-open hooks run with cwd set to a tmp fixture vault -- dies
with FileNotFoundError at import. That aborts the stats phase and, in the
mutant phase, silently empties hook output, producing FALSE KILLS.

When the process is part of a mutmut run (MUTANT_UNDER_TEST present in the
environment, including set to ""), and normal config discovery fails, seed a
benign in-memory Config so import succeeds and trampoline dispatch works.
Never chdir; never touch processes outside mutmut runs.

Provenance: "mutmut pilot -- knowledge-harness (pre-registered data
collection)", 2026-08-23, /home/eranr/kh-mutmut-pilot-report.md ("The
blocking defect found in stock mutmut 3.7.0" and "Workaround files"
sections); upstream defect draft filed in-repo at
docs/research/2026-08-23-mutmut-defect-reports.md.

Activated in this repo via PYTHONPATH=scripts/mutmut_shims on mutmut
invocations only -- never installed into the venv or imported outside a
mutmut run.
"""

# ruff: noqa: S110

import os

try:
    if "MUTANT_UNDER_TEST" in os.environ:
        import mutmut.configuration as _mc

        try:
            _mc.Config.ensure_loaded()
        except Exception:
            _mc._config = _mc.Config(
                also_copy=[],
                only_mutate=[],
                do_not_mutate=[],
                do_not_mutate_patterns=[],
                max_stack_depth=-1,
                debug=False,
                source_paths=[],
                resolved_mutated_source_paths=[],
                pytest_add_cli_args=[],
                pytest_add_cli_args_test_selection=[],
                mutate_only_covered_lines=False,
                timeout_multiplier=15.0,
                timeout_constant=1.0,
                type_check_command=[],
                use_setproctitle=False,
                track_dependencies=False,
                dependency_tracking_depth=-1,
                cache_invalidation_files=[],
                cache_invalidation_exclude=[],
                on_dependency_change="warn",
                use_git_change_detection=False,
            )
except Exception:
    pass
