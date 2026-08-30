"""Unit tests for the no-new-survivors mutation gate (parsing + comparison only;
no subprocess — the mutate4py invocation itself is exercised by the baseline run)."""

import subprocess
import sys
from pathlib import Path

import pytest

import scripts.mutation_gate as mutation_gate
from scripts.mutation_gate import (
    baseline_keys,
    changed_modules,
    new_survivors,
    parse_survivors,
)

SAMPLE_OUTPUT = """\
Mutation run: research_vault/selectors.py
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
    keys = parse_survivors("research_vault/selectors.py", SAMPLE_OUTPUT)
    assert keys == {
        'research_vault/selectors.py::func/_norm_with_map::char == "-" -> char != "-"',
        "research_vault/selectors.py::func/find_context::position < 0 -> position <= 0",
        "research_vault/selectors.py::func/find_context::end < len(text) -> end <= len(text)",
    }


def test_parse_survivors_empty_when_no_survivors_section():
    assert (
        parse_survivors("research_vault/paths.py", "Killed: 5\nSurvived: 0\n") == set()
    )


# Byte-for-byte excerpt of real mutate4py 0.1.4 stdout for research_vault/inbox.py
# (see .mutate4py/baseline-run/research_vault__inbox.py.stdout), trimmed from 9
# survivors to 3. Unlike SAMPLE_OUTPUT above (hand-written, a func/ id on every
# line, which is exactly why the drop-everything-after-a-module-level-survivor bug
# went uncaught), this reproduces the real shape: a module-level survivor with no
# func id (line 115) followed by function-level survivors, plus a genuine
# multi-line-wrapped mutation description (line 611).
REALISTIC_OUTPUT = """\
Mutation run: research_vault/inbox.py
Total mutation sites: 129
Covered mutation sites: 58
Uncovered mutation sites: 71
Mutation workers: 4

Mutation Report
===============
Killed: 49
Survived: 3
Uncovered: 71
Per-Mutant overhead: 0.60s

Survivors:
  line 115 True -> False
  line 195 notice_date is not None or detection_date is not None -> notice_date is not None and detection_date is not None func/_validate_notice_fingerprint
  line 611 len(colliding) == 1 and any(
            ack.ack_of == finding.id
            and ack.actor.startswith("human:")
            and ack.target_hash == finding.target_hash
            and ack.notice_class is None
            for ack in entries
        ) -> len(colliding) == 1 or any(
            ack.ack_of == finding.id
            and ack.actor.startswith("human:")
            and ack.target_hash == finding.target_hash
            and ack.notice_class is None
            for ack in entries
        ) func/_scope_acknowledged
"""


def test_parse_survivors_handles_module_level_and_wrapped_entries():
    """Regression for the drop bug: a module-level survivor (no func/ id) must
    key as `::module::`, not be discarded -- and must not truncate the
    function-level survivors and the wrapped multi-line entry that follow it."""
    keys = parse_survivors("research_vault/inbox.py", REALISTIC_OUTPUT)
    assert keys == {
        "research_vault/inbox.py::module::True -> False",
        "research_vault/inbox.py::func/_validate_notice_fingerprint::"
        "notice_date is not None or detection_date is not None -> "
        "notice_date is not None and detection_date is not None",
        "research_vault/inbox.py::func/_scope_acknowledged::"
        "len(colliding) == 1 and any( ack.ack_of == finding.id and "
        'ack.actor.startswith("human:") and ack.target_hash == '
        "finding.target_hash and ack.notice_class is None for ack in entries "
        ") -> len(colliding) == 1 or any( ack.ack_of == finding.id and "
        'ack.actor.startswith("human:") and ack.target_hash == '
        "finding.target_hash and ack.notice_class is None for ack in entries )",
    }


def test_parse_survivors_raises_on_genuinely_unparseable_entry():
    """The other half of the inversion: an indented line that is neither a
    module-level survivor nor a wrapped continuation must raise, not silently
    read as zero survivors (same doctrine as a non-zero mutate4py exit)."""
    bad_output = "Survivors:\n  this is not a survivor line at all\n"
    with pytest.raises(ValueError, match="unparseable"):
        parse_survivors("research_vault/paths.py", bad_output)


def test_new_survivors_ignores_baselined_keys():
    baseline = {
        'research_vault/selectors.py::func/_norm_with_map::char == "-" -> char != "-"',
    }
    found = parse_survivors("research_vault/selectors.py", SAMPLE_OUTPUT)
    fresh = new_survivors(found, baseline)
    assert fresh == {
        "research_vault/selectors.py::func/find_context::position < 0 -> position <= 0",
        "research_vault/selectors.py::func/find_context::end < len(text) -> end <= len(text)",
    }


def test_baseline_round_trip(tmp_path: Path):
    path = tmp_path / "mutation-baseline.txt"
    keys = {"b::func/x::1 -> 0", "a::func/y::True -> False"}
    path.write_text("\n".join(sorted(keys)) + "\n", encoding="utf-8")
    assert baseline_keys(path) == keys


def test_baseline_missing_file_is_empty(tmp_path: Path):
    assert baseline_keys(tmp_path / "absent.txt") == set()


def test_baseline_keys_skips_comment_header(tmp_path: Path):
    """A written baseline may start with a '#' exclusion header (see
    _baseline_header) -- it must round-trip as metadata, never as a key."""
    path = tmp_path / "mutation-baseline.txt"
    keys = {"b::func/x::1 -> 0", "a::func/y::True -> False"}
    header = (
        "# mutation-baseline.txt -- 1 module(s) excluded (see "
        "mutation-exclusions.txt), not represented below: "
        "research_vault/gitstate.py\n"
    )
    path.write_text(header + "\n" + "\n".join(sorted(keys)) + "\n", encoding="utf-8")
    assert baseline_keys(path) == keys


def test_changed_modules_lists_modified_core_files(tmp_path: Path):
    """The one function deciding whether the gate ever runs must be proven live:
    a wrong pathspec makes the diff silently empty and the gate passes forever."""
    import subprocess

    repo = tmp_path / "repo"
    (repo / "research_vault").mkdir(parents=True)

    def git(*argv: str) -> None:
        subprocess.run(["git", *argv], cwd=repo, check=True, capture_output=True)

    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@example.invalid")
    git("config", "user.name", "t")
    (repo / "research_vault" / "x.py").write_text("A = 1\n", encoding="utf-8")
    (repo / "research_vault" / "__init__.py").write_text("", encoding="utf-8")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    git("checkout", "-q", "-b", "feature")
    (repo / "research_vault" / "x.py").write_text("A = 2\n", encoding="utf-8")
    (repo / "research_vault" / "__init__.py").write_text("B = 1\n", encoding="utf-8")
    git("commit", "-q", "-a", "-m", "change")

    assert changed_modules("main", cwd=repo) == ["research_vault/x.py"]


def _run_baseline(
    monkeypatch,
    tmp_path: Path,
    out_dir: Path,
    memory_cap: str | None = None,
    exclusions_path: Path | None = None,
) -> Path:
    """Shared argv wiring for the --out-dir tests below: --lcov's value is never
    read (the fake _run_mutate ignores it), so any placeholder string does.

    --exclusions defaults to a tmp_path file that is never created, so these
    tests stay isolated from the real, committed mutation-exclusions.txt at the
    repo root -- without this override, a fake module name that happens to
    collide with a genuinely excluded one (e.g. "research_vault/selectors.py",
    used as the sample module throughout this file) would be silently skipped
    instead of exercising the code path each test means to hit.
    """
    baseline_path = tmp_path / "mutation-baseline.txt"
    if exclusions_path is None:
        exclusions_path = tmp_path / "absent-exclusions.txt"
    argv = [
        "mutation_gate.py",
        "--update-baseline",
        "--lcov",
        "unused.info",
        "--baseline",
        str(baseline_path),
        "--out-dir",
        str(out_dir),
        "--exclusions",
        str(exclusions_path),
    ]
    if memory_cap is not None:
        argv += ["--memory-cap", memory_cap]
    monkeypatch.setattr(sys, "argv", argv)
    return baseline_path


def _run_gate(monkeypatch, tmp_path: Path, exclusions_path: Path | None = None) -> Path:
    """Gate-mode counterpart to _run_baseline, same --exclusions isolation
    rationale. baseline_path is returned unwritten (a missing baseline means
    "empty", per baseline_keys()) unless a test writes to it first."""
    baseline_path = tmp_path / "mutation-baseline.txt"
    if exclusions_path is None:
        exclusions_path = tmp_path / "absent-exclusions.txt"
    argv = [
        "mutation_gate.py",
        "--lcov",
        "unused.info",
        "--baseline",
        str(baseline_path),
        "--exclusions",
        str(exclusions_path),
    ]
    monkeypatch.setattr(sys, "argv", argv)
    return baseline_path


def test_out_dir_skips_module_with_recorded_success(tmp_path: Path, monkeypatch):
    """The whole point of --out-dir: a resumed run must not redo work a prior
    run already finished and recorded."""
    out_dir = tmp_path / "records"
    out_dir.mkdir()
    module = "research_vault/selectors.py"
    (out_dir / "research_vault__selectors.py.stdout").write_text(
        SAMPLE_OUTPUT, encoding="utf-8"
    )
    (out_dir / "research_vault__selectors.py.exit").write_text("0", encoding="utf-8")

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
    module = "research_vault/selectors.py"
    (out_dir / "research_vault__selectors.py.stdout").write_text("", encoding="utf-8")
    (out_dir / "research_vault__selectors.py.exit").write_text("4", encoding="utf-8")

    calls: list[str] = []

    def fake_run_mutate(relpath, lcov, extra, max_workers, memory_cap=None):
        calls.append(relpath)
        return SAMPLE_OUTPUT, 0

    monkeypatch.setattr(mutation_gate, "_run_mutate", fake_run_mutate)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [module])
    baseline_path = _run_baseline(monkeypatch, tmp_path, out_dir)

    assert mutation_gate.main() == 0
    assert calls == [module]
    # Rewritten record now carries the class alongside the code -- proves a
    # rerun's record isn't just overwritten, but overwritten in the new format.
    assert (out_dir / "research_vault__selectors.py.exit").read_text(
        encoding="utf-8"
    ) == "0 ok"
    assert baseline_keys(baseline_path) == parse_survivors(module, SAMPLE_OUTPUT)


def test_out_dir_writes_no_baseline_when_a_module_still_fails(
    tmp_path: Path, monkeypatch
):
    """The refusal policy is load-bearing: a partial --out-dir pass must never
    yield a written baseline, same as without --out-dir."""
    out_dir = tmp_path / "records"
    out_dir.mkdir()
    modules = ["research_vault/a.py", "research_vault/b.py"]

    def fake_run_mutate(relpath, lcov, extra, max_workers, memory_cap=None):
        if relpath == "research_vault/a.py":
            return "", 4
        return SAMPLE_OUTPUT, 0

    monkeypatch.setattr(mutation_gate, "_run_mutate", fake_run_mutate)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: modules)
    baseline_path = _run_baseline(monkeypatch, tmp_path, out_dir)

    assert mutation_gate.main() == 1
    assert not baseline_path.exists()


def test_cap_kill_exit_code_classified_memcap_when_cap_in_effect(
    tmp_path: Path, monkeypatch, capsys
):
    """The load-bearing distinction: a signal-death exit code under an active
    --memory-cap is a memcap kill, not a generic error."""
    out_dir = tmp_path / "records"
    out_dir.mkdir()
    module = "research_vault/selectors.py"

    def fake_run_mutate(relpath, lcov, extra, max_workers, memory_cap=None):
        assert memory_cap == "8G"
        return "", 137

    monkeypatch.setattr(mutation_gate, "_run_mutate", fake_run_mutate)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [module])
    baseline_path = _run_baseline(monkeypatch, tmp_path, out_dir, memory_cap="8G")

    assert mutation_gate.main() == 1
    assert not baseline_path.exists()
    # The record on disk carries the class, not just the raw exit code.
    assert (out_dir / "research_vault__selectors.py.exit").read_text(
        encoding="utf-8"
    ) == "137 memcap"
    out = capsys.readouterr().out
    assert "memcap" in out
    assert "[baseline]   memcap (1)" in out


def test_same_exit_code_classified_error_when_no_cap_in_effect(
    tmp_path: Path, monkeypatch, capsys
):
    """Without --memory-cap, 137/143 carry no special meaning -- they must land
    in the same unexplained-error bucket as exit 4, not be mislabelled memcap."""
    out_dir = tmp_path / "records"
    out_dir.mkdir()
    module = "research_vault/selectors.py"

    def fake_run_mutate(relpath, lcov, extra, max_workers, memory_cap=None):
        assert memory_cap is None
        return "", 137

    monkeypatch.setattr(mutation_gate, "_run_mutate", fake_run_mutate)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [module])
    baseline_path = _run_baseline(monkeypatch, tmp_path, out_dir)

    assert mutation_gate.main() == 1
    assert not baseline_path.exists()
    assert (out_dir / "research_vault__selectors.py.exit").read_text(
        encoding="utf-8"
    ) == "137 error"
    out = capsys.readouterr().out
    assert "[baseline]   error (1)" in out
    assert "memcap" not in out


def test_summary_reports_memcap_and_error_separately(
    tmp_path: Path, monkeypatch, capsys
):
    """Two failure classes in one run must be counted and listed on separate
    summary lines, never blended into a single failure count."""
    out_dir = tmp_path / "records"
    out_dir.mkdir()
    modules = ["research_vault/a.py", "research_vault/b.py"]

    def fake_run_mutate(relpath, lcov, extra, max_workers, memory_cap=None):
        if relpath == "research_vault/a.py":
            return "", 137  # memcap, under an active cap
        return "", 4  # unrelated error

    monkeypatch.setattr(mutation_gate, "_run_mutate", fake_run_mutate)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: modules)
    baseline_path = _run_baseline(monkeypatch, tmp_path, out_dir, memory_cap="512M")

    assert mutation_gate.main() == 1
    assert not baseline_path.exists()
    out = capsys.readouterr().out
    assert "[baseline]   memcap (1): research_vault/a.py" in out
    assert "[baseline]   error (1): research_vault/b.py" in out


def test_memory_cap_wraps_invocation_in_systemd_run_scope(monkeypatch):
    """--memory-cap must actually change the invoked command -- without this,
    the classification logic above would be trusting a flag that does nothing."""
    captured: list[list[str]] = []

    class FakeCompletedProcess:
        stdout = ""
        stderr = ""
        returncode = 0

    def fake_subprocess_run(cmd, **kwargs):
        captured.append(cmd)
        return FakeCompletedProcess()

    monkeypatch.setattr(mutation_gate.subprocess, "run", fake_subprocess_run)

    mutation_gate._run_mutate("research_vault/x.py", "lcov.info", [], 4, "8G")
    assert captured[-1][:6] == [
        "systemd-run",
        "--user",
        "--scope",
        "-p",
        "MemoryMax=8G",
        "-p",
    ]
    assert "MemorySwapMax=0" in captured[-1]
    assert sys.executable in captured[-1]

    mutation_gate._run_mutate("research_vault/x.py", "lcov.info", [], 4)
    assert captured[-1][0] == sys.executable


def test_run_mutate_disables_bytecode_writing(monkeypatch):
    """Removes a false-SURVIVOR window, which is worse than any abort.

    A timestamp-based .pyc is validated on (mtime, size) alone, and the common
    mutations are same-length token swaps (`==` -> `!=`). A .pyc written and a
    mutant applied inside one filesystem-timestamp tick collide on both fields,
    so the child imports stale bytecode, never exercises the mutant, and records
    it as survived. This is pinned by a test because an env var that stops being
    passed fails silently -- and its failure mode is a quietly wrong baseline,
    not a crash.
    """
    seen: dict[str, str] = {}

    def fake_run(cmd, **kwargs):
        seen.update(kwargs.get("env") or {})
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    mutation_gate._run_mutate("research_vault/x.py", "lcov.info", [], 4)
    assert seen.get("PYTHONDONTWRITEBYTECODE") == "1"
    # Inherited, not replaced: mutate4py resolves its own interpreter and tools
    # through the ambient environment.
    assert "PATH" in seen


# --- mutation-exclusions.txt: parsing --------------------------------------


def test_parse_exclusions_missing_file_is_empty_with_warning(tmp_path, capsys):
    """Absent file (bad --exclusions path, or a checkout predating this
    feature) degrades to zero exclusions rather than aborting either mode --
    but never silently: a warning is printed, not just an empty dict returned."""
    result = mutation_gate.parse_exclusions(tmp_path / "absent.txt")
    assert result == {}
    assert "WARNING" in capsys.readouterr().out


def test_parse_exclusions_tolerates_comments_and_blank_lines(tmp_path: Path):
    path = tmp_path / "mutation-exclusions.txt"
    path.write_text(
        "# header comment\n"
        "\n"
        "research_vault/gitstate.py::B::module import breaks\n"
        "\n"
        "# trailing comment\n",
        encoding="utf-8",
    )
    assert mutation_gate.parse_exclusions(path) == {
        "research_vault/gitstate.py": ("B", "module import breaks"),
    }


def test_parse_exclusions_malformed_line_raises(tmp_path: Path):
    """A corrupt committed file could silently drop a module's excluded status
    -- exactly the undetectable hole the list exists to close -- so a line that
    doesn't split into three '::'-separated fields fails loudly instead."""
    path = tmp_path / "mutation-exclusions.txt"
    path.write_text("research_vault/gitstate.py::B\n", encoding="utf-8")
    with pytest.raises(ValueError, match="malformed"):
        mutation_gate.parse_exclusions(path)


def test_committed_exclusions_file_parses_and_names_the_known_six():
    """Sanity check on the real, repo-root mutation-exclusions.txt (not a
    fixture): it must parse cleanly under the same parser the gate uses, and
    must still list the six modules established by investigation -- catches
    a hand-edit that breaks the format or silently drops an entry."""
    exclusions = mutation_gate.parse_exclusions(
        mutation_gate.ROOT / "mutation-exclusions.txt"
    )
    assert set(exclusions) == {
        "research_vault/events.py",
        "research_vault/frontmatter.py",
        "research_vault/gitstate.py",
        "research_vault/outcome.py",
        "research_vault/pathcodec.py",
        "research_vault/selectors.py",
    }


# --- mutation-exclusions.txt: --update-baseline -----------------------------


def test_excluded_module_is_skipped_and_does_not_block_write(
    tmp_path: Path, monkeypatch
):
    """The whole point of the exclusion list: a module known to be
    unmeasurable must not be run, and must not count as a failure that blocks
    the write."""
    out_dir = tmp_path / "records"
    out_dir.mkdir()
    exclusions_path = tmp_path / "mutation-exclusions.txt"
    exclusions_path.write_text(
        "research_vault/a.py::A::collection-time reacher, reproduced in isolation\n",
        encoding="utf-8",
    )
    modules = ["research_vault/a.py", "research_vault/b.py"]

    def fake_run_mutate(relpath, lcov, extra, max_workers, memory_cap=None):
        assert relpath != "research_vault/a.py", "excluded module must not run"
        return SAMPLE_OUTPUT, 0

    monkeypatch.setattr(mutation_gate, "_run_mutate", fake_run_mutate)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: modules)
    baseline_path = _run_baseline(
        monkeypatch, tmp_path, out_dir, exclusions_path=exclusions_path
    )

    assert mutation_gate.main() == 0
    written = baseline_path.read_text(encoding="utf-8")
    # Excluded module never contributed keys -- only b's SAMPLE_OUTPUT did.
    assert baseline_keys(baseline_path) == parse_survivors(
        "research_vault/b.py", SAMPLE_OUTPUT
    )
    # The exclusion travels into the baseline file itself, not just stdout.
    assert "research_vault/a.py" in written.splitlines()[0]


def test_excluded_module_skip_does_not_mask_a_real_failure(tmp_path: Path, monkeypatch):
    """Exclusions must not become a general-purpose escape hatch: a module NOT
    on the list that still fails must block the write exactly as before."""
    out_dir = tmp_path / "records"
    out_dir.mkdir()
    exclusions_path = tmp_path / "mutation-exclusions.txt"
    exclusions_path.write_text("research_vault/a.py::A::reason\n", encoding="utf-8")
    modules = ["research_vault/a.py", "research_vault/b.py"]

    def fake_run_mutate(relpath, lcov, extra, max_workers, memory_cap=None):
        assert relpath == "research_vault/b.py"
        return "", 4

    monkeypatch.setattr(mutation_gate, "_run_mutate", fake_run_mutate)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: modules)
    baseline_path = _run_baseline(
        monkeypatch, tmp_path, out_dir, exclusions_path=exclusions_path
    )

    assert mutation_gate.main() == 1
    assert not baseline_path.exists()


def test_exclusion_inventory_prints_even_when_empty(
    tmp_path: Path, monkeypatch, capsys
):
    """The announcement is unconditional: it must appear even at zero
    exclusions, so it can never be read only when there happens to be news."""
    out_dir = tmp_path / "records"
    out_dir.mkdir()
    exclusions_path = tmp_path / "mutation-exclusions.txt"
    exclusions_path.write_text("# nothing excluded yet\n", encoding="utf-8")
    module = "research_vault/selectors.py"

    def fake_run_mutate(relpath, lcov, extra, max_workers, memory_cap=None):
        return SAMPLE_OUTPUT, 0

    monkeypatch.setattr(mutation_gate, "_run_mutate", fake_run_mutate)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [module])
    _run_baseline(monkeypatch, tmp_path, out_dir, exclusions_path=exclusions_path)

    assert mutation_gate.main() == 0
    assert "[baseline] 0 module(s) excluded" in capsys.readouterr().out


# --- mutation-exclusions.txt: gate mode -------------------------------------


def test_gate_reports_excluded_changed_module_without_failing(
    tmp_path: Path, monkeypatch, capsys
):
    """Exit-code decision for the advisory lane: an excluded changed module
    must not fail the gate by itself (the tooling defect isn't the change's
    fault), but the pass line must name it -- never the bare, unqualified
    "pass — no new survivors" that would read as a clean verification."""
    exclusions_path = tmp_path / "mutation-exclusions.txt"
    exclusions_path.write_text(
        "research_vault/selectors.py::unexplained::reason\n", encoding="utf-8"
    )
    module = "research_vault/selectors.py"

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("excluded module must not be run in gate mode either")

    monkeypatch.setattr(mutation_gate, "_run_mutate", fail_if_called)
    monkeypatch.setattr(mutation_gate, "changed_modules", lambda base: [module])
    _run_gate(monkeypatch, tmp_path, exclusions_path=exclusions_path)

    assert mutation_gate.main() == 0
    out = capsys.readouterr().out
    lines = out.splitlines()
    assert f"[gate] {module}: excluded [unexplained] -- reason" in lines
    assert "[gate] pass — no new survivors" not in lines
    assert any(
        line.startswith("[gate] pass") and "NOT MEASURED" in line for line in lines
    )


def test_gate_still_fails_on_a_fresh_survivor_alongside_an_excluded_module(
    tmp_path: Path, monkeypatch
):
    """Exclusion of one changed module must not blanket-pass the run: a fresh
    survivor in a different changed, non-excluded module still fails the gate."""
    exclusions_path = tmp_path / "mutation-exclusions.txt"
    exclusions_path.write_text(
        "research_vault/selectors.py::unexplained::reason\n", encoding="utf-8"
    )
    excluded = "research_vault/selectors.py"
    changed = "research_vault/other.py"

    def fake_run_mutate(relpath, lcov, extra, max_workers, memory_cap=None):
        assert relpath == changed, "excluded module must not run"
        return SAMPLE_OUTPUT.replace("research_vault/selectors.py", changed), 0

    monkeypatch.setattr(mutation_gate, "_run_mutate", fake_run_mutate)
    monkeypatch.setattr(
        mutation_gate, "changed_modules", lambda base: [changed, excluded]
    )
    _run_gate(monkeypatch, tmp_path, exclusions_path=exclusions_path)

    assert mutation_gate.main() == 1


def test_restore_if_left_mutated_undoes_an_interrupted_runs_mutation(
    tmp_path, monkeypatch
):
    """A signal-killed mutate4py leaves production source MUTATED.

    This is not defensive coding: a timeout-killed run left `index += 1` ->
    `index += 0` in selectors._norm_with_map, and the next ordinary pytest run
    allocated until the VM died. The .bak is mutate4py's own pre-mutation copy,
    so restoring from it -- rather than from git -- cannot destroy legitimate
    uncommitted edits.
    """
    monkeypatch.setattr(mutation_gate, "ROOT", tmp_path)
    (tmp_path / "research_vault").mkdir()
    source = tmp_path / "research_vault" / "x.py"
    source.write_text("index += 0\n", encoding="utf-8")  # the mutant left behind
    (tmp_path / "research_vault" / "x.py.bak").write_text(
        "index += 1\n", encoding="utf-8"
    )

    assert mutation_gate._restore_if_left_mutated("research_vault/x.py") is True
    assert source.read_text(encoding="utf-8") == "index += 1\n"
    assert not (tmp_path / "research_vault" / "x.py.bak").exists()


def test_restore_if_left_mutated_is_a_noop_after_a_clean_run(tmp_path, monkeypatch):
    """mutate4py removes the .bak when a module finishes, so no .bak means the
    source was never left mutated -- and an untouched file must stay untouched."""
    monkeypatch.setattr(mutation_gate, "ROOT", tmp_path)
    (tmp_path / "research_vault").mkdir()
    source = tmp_path / "research_vault" / "x.py"
    source.write_text("index += 1\n", encoding="utf-8")

    assert mutation_gate._restore_if_left_mutated("research_vault/x.py") is False
    assert source.read_text(encoding="utf-8") == "index += 1\n"
