"""Unit tests for the no-new-survivors mutation gate (parsing + comparison only;
no subprocess — the mutate4py invocation itself is exercised by the baseline run)."""

import sys
from pathlib import Path

import scripts.mutation_gate as mutation_gate
from scripts.mutation_gate import (
    baseline_keys,
    changed_modules,
    new_survivors,
    parse_survivors,
)

SAMPLE_OUTPUT = """\
Mutation run: knowledge_harness/selectors.py
Total mutation sites: 71
Covered mutation sites: 54
Uncovered mutation sites: 17
Mutation workers: 4

Mutation Report
===============
Killed: 35
Survived: 3
Uncovered: 17
Per-Mutant overhead: 0.33s

Survivors:
  line 79 char == "-" -> char != "-" func/_norm_with_map
  line 119 position < 0 -> position <= 0 func/find_context
  line 123 end < len(text) -> end <= len(text) func/find_context
"""


def test_parse_survivors_extracts_file_func_and_mutation():
    keys = parse_survivors("knowledge_harness/selectors.py", SAMPLE_OUTPUT)
    assert keys == {
        'knowledge_harness/selectors.py::func/_norm_with_map::char == "-" -> char != "-"',
        "knowledge_harness/selectors.py::func/find_context::position < 0 -> position <= 0",
        "knowledge_harness/selectors.py::func/find_context::end < len(text) -> end <= len(text)",
    }


def test_parse_survivors_empty_when_no_survivors_section():
    assert (
        parse_survivors("knowledge_harness/paths.py", "Killed: 5\nSurvived: 0\n")
        == set()
    )


def test_new_survivors_ignores_baselined_keys():
    baseline = {
        'knowledge_harness/selectors.py::func/_norm_with_map::char == "-" -> char != "-"',
    }
    found = parse_survivors("knowledge_harness/selectors.py", SAMPLE_OUTPUT)
    fresh = new_survivors(found, baseline)
    assert fresh == {
        "knowledge_harness/selectors.py::func/find_context::position < 0 -> position <= 0",
        "knowledge_harness/selectors.py::func/find_context::end < len(text) -> end <= len(text)",
    }


def test_baseline_round_trip(tmp_path: Path):
    path = tmp_path / "mutation-baseline.txt"
    keys = {"b::func/x::1 -> 0", "a::func/y::True -> False"}
    path.write_text("\n".join(sorted(keys)) + "\n", encoding="utf-8")
    assert baseline_keys(path) == keys


def test_baseline_missing_file_is_empty(tmp_path: Path):
    assert baseline_keys(tmp_path / "absent.txt") == set()


def test_changed_modules_lists_modified_core_files(tmp_path: Path):
    """The one function deciding whether the gate ever runs must be proven live:
    a wrong pathspec makes the diff silently empty and the gate passes forever."""
    import subprocess

    repo = tmp_path / "repo"
    (repo / "knowledge_harness").mkdir(parents=True)

    def git(*argv: str) -> None:
        subprocess.run(["git", *argv], cwd=repo, check=True, capture_output=True)

    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@example.invalid")
    git("config", "user.name", "t")
    (repo / "knowledge_harness" / "x.py").write_text("A = 1\n", encoding="utf-8")
    (repo / "knowledge_harness" / "__init__.py").write_text("", encoding="utf-8")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    git("checkout", "-q", "-b", "feature")
    (repo / "knowledge_harness" / "x.py").write_text("A = 2\n", encoding="utf-8")
    (repo / "knowledge_harness" / "__init__.py").write_text("B = 1\n", encoding="utf-8")
    git("commit", "-q", "-a", "-m", "change")

    assert changed_modules("main", cwd=repo) == ["knowledge_harness/x.py"]


def _run_baseline(monkeypatch, tmp_path: Path, out_dir: Path) -> Path:
    """Shared argv wiring for the --out-dir tests below: --lcov's value is never
    read (the fake _run_mutate ignores it), so any placeholder string does."""
    baseline_path = tmp_path / "mutation-baseline.txt"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "mutation_gate.py",
            "--update-baseline",
            "--lcov",
            "unused.info",
            "--baseline",
            str(baseline_path),
            "--out-dir",
            str(out_dir),
        ],
    )
    return baseline_path


def test_out_dir_skips_module_with_recorded_success(tmp_path: Path, monkeypatch):
    """The whole point of --out-dir: a resumed run must not redo work a prior
    run already finished and recorded."""
    out_dir = tmp_path / "records"
    out_dir.mkdir()
    module = "knowledge_harness/selectors.py"
    (out_dir / "knowledge_harness__selectors.py.stdout").write_text(
        SAMPLE_OUTPUT, encoding="utf-8"
    )
    (out_dir / "knowledge_harness__selectors.py.exit").write_text("0", encoding="utf-8")

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("a recorded success must not be re-run")

    monkeypatch.setattr(mutation_gate, "_run_mutate", fail_if_called)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [module])
    baseline_path = _run_baseline(monkeypatch, tmp_path, out_dir)

    assert mutation_gate.main() == 0
    # Assembled from the *recorded* stdout, not a fresh run -- proves the baseline
    # is built by reading records back, not merely that _run_mutate was skipped.
    assert baseline_keys(baseline_path) == parse_survivors(module, SAMPLE_OUTPUT)


def test_out_dir_reruns_module_with_recorded_failure(tmp_path: Path, monkeypatch):
    out_dir = tmp_path / "records"
    out_dir.mkdir()
    module = "knowledge_harness/selectors.py"
    (out_dir / "knowledge_harness__selectors.py.stdout").write_text(
        "", encoding="utf-8"
    )
    (out_dir / "knowledge_harness__selectors.py.exit").write_text("4", encoding="utf-8")

    calls: list[str] = []

    def fake_run_mutate(relpath, lcov, extra, max_workers):
        calls.append(relpath)
        return SAMPLE_OUTPUT, 0

    monkeypatch.setattr(mutation_gate, "_run_mutate", fake_run_mutate)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [module])
    baseline_path = _run_baseline(monkeypatch, tmp_path, out_dir)

    assert mutation_gate.main() == 0
    assert calls == [module]
    assert (out_dir / "knowledge_harness__selectors.py.exit").read_text(
        encoding="utf-8"
    ) == "0"
    assert baseline_keys(baseline_path) == parse_survivors(module, SAMPLE_OUTPUT)


def test_out_dir_writes_no_baseline_when_a_module_still_fails(
    tmp_path: Path, monkeypatch
):
    """The refusal policy is load-bearing: a partial --out-dir pass must never
    yield a written baseline, same as without --out-dir."""
    out_dir = tmp_path / "records"
    out_dir.mkdir()
    modules = ["knowledge_harness/a.py", "knowledge_harness/b.py"]

    def fake_run_mutate(relpath, lcov, extra, max_workers):
        if relpath == "knowledge_harness/a.py":
            return "", 4
        return SAMPLE_OUTPUT, 0

    monkeypatch.setattr(mutation_gate, "_run_mutate", fake_run_mutate)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: modules)
    baseline_path = _run_baseline(monkeypatch, tmp_path, out_dir)

    assert mutation_gate.main() == 1
    assert not baseline_path.exists()
