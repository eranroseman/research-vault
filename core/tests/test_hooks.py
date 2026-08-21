import importlib.util
import io
import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "posttooluse_lint.py"


def _make_hook_vault(vault: Path) -> None:
    (vault / ".harness").mkdir(exist_ok=True)


def _run_hook(cwd: Path, payload: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HOOK)],
        cwd=cwd,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )


def _payload(path: Path, cwd: Path) -> dict:
    return {
        "cwd": str(cwd),
        "tool_name": "Edit",
        "tool_input": {"file_path": str(path)},
    }


def _load_hook():
    spec = importlib.util.spec_from_file_location("posttooluse_lint", HOOK)
    assert spec is not None
    assert spec.loader is not None
    hook = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hook)
    return hook


def _vault_state(vault: Path) -> tuple[tuple[str, int, bytes], ...]:
    return tuple(
        sorted(
            (
                str(path.relative_to(vault)),
                stat.S_IMODE(path.stat().st_mode),
                path.read_bytes(),
            )
            for path in vault.rglob("*")
            if path.is_file() and ".git" not in path.parts
        )
    )


def _warning(result: subprocess.CompletedProcess[str]) -> str:
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert set(output) == {"hookSpecificOutput"}
    specific = output["hookSpecificOutput"]
    assert set(specific) == {"hookEventName", "additionalContext"}
    assert specific["hookEventName"] == "PostToolUse"
    assert isinstance(specific["additionalContext"], str)
    return specific["additionalContext"]


def test_posttooluse_is_silent_outside_a_vault(tmp_path):
    note = tmp_path / "outside.md"
    note.write_text("# Outside\n")

    result = _run_hook(tmp_path, _payload(note, tmp_path))

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def test_posttooluse_is_silent_for_clean_synthesis_edit(fixture_vault):
    _make_hook_vault(fixture_vault)
    note = fixture_vault / "synthesis" / "clean.md"
    note.write_text("# Clean synthesis\n")

    result = _run_hook(fixture_vault, _payload(note, fixture_vault))

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


@pytest.mark.parametrize(
    "relative",
    [
        Path("literatures") / "clean.md",
        Path("literatures") / "nested space" / "naïve.md",
    ],
)
def test_posttooluse_warns_for_every_literature_touch(fixture_vault, relative):
    _make_hook_vault(fixture_vault)
    note = fixture_vault / relative
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text("# Clean literature note\n")

    result = _run_hook(fixture_vault, _payload(note, fixture_vault))

    context = _warning(result)
    assert "evidence-layer" in context
    assert result.stderr == ""


def test_posttooluse_reports_non_evidence_file_findings(fixture_vault):
    _make_hook_vault(fixture_vault)
    note = fixture_vault / "projects" / "brief" / "draft.md"

    result = _run_hook(fixture_vault, _payload(note, fixture_vault))

    context = _warning(result)
    assert "citekey" in context
    assert "fabricated2020" in context


def test_posttooluse_accepts_write_tool_identity(fixture_vault):
    _make_hook_vault(fixture_vault)
    note = fixture_vault / "literatures" / "clean.md"
    note.write_text("# Clean literature note\n")
    payload = _payload(note, fixture_vault)
    payload["tool_name"] = "Write"

    result = _run_hook(fixture_vault, payload)

    assert "evidence-layer" in _warning(result)


def test_posttooluse_runs_read_only_checks_without_vault_mutation(fixture_vault):
    _make_hook_vault(fixture_vault)
    note = fixture_vault / "projects" / "brief" / "draft.md"
    before = _vault_state(fixture_vault)
    status_before = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=fixture_vault,
        text=True,
        capture_output=True,
        check=True,
    ).stdout

    result = _run_hook(fixture_vault, _payload(note, fixture_vault))

    _warning(result)
    status_after = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=fixture_vault,
        text=True,
        capture_output=True,
        check=True,
    ).stdout
    assert _vault_state(fixture_vault) == before
    assert status_after == status_before


def test_posttooluse_handles_paths_with_spaces_and_non_ascii(fixture_vault):
    _make_hook_vault(fixture_vault)
    note = fixture_vault / "synthesis" / "space é" / "clean file.md"
    note.parent.mkdir()
    note.write_text("# Clean synthesis\n")

    result = _run_hook(fixture_vault, _payload(note, fixture_vault))

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def test_posttooluse_is_silent_for_malformed_input(tmp_path):
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        cwd=tmp_path,
        input="{",
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


@pytest.mark.parametrize(
    "mutate",
    [
        lambda payload: payload.pop("tool_name"),
        lambda payload: payload.__setitem__("tool_name", "Bash"),
        lambda payload: payload.__setitem__("tool_name", 1),
        lambda payload: payload["tool_input"].pop("file_path"),
        lambda payload: payload["tool_input"].__setitem__("file_path", 1),
    ],
)
def test_posttooluse_silences_non_edit_write_or_malformed_tool_fields(
    fixture_vault, mutate
):
    _make_hook_vault(fixture_vault)
    note = fixture_vault / "projects" / "brief" / "draft.md"
    payload = _payload(note, fixture_vault)
    mutate(payload)

    result = _run_hook(fixture_vault, payload)

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def test_posttooluse_uses_payload_cwd_for_walkup_and_relative_file_path(
    fixture_vault, tmp_path
):
    _make_hook_vault(fixture_vault)
    cwd = fixture_vault / "projects" / "brief"
    payload = _payload(Path("draft.md"), cwd)

    result = _run_hook(tmp_path, payload)

    context = _warning(result)
    assert "fabricated2020" in context


@pytest.mark.parametrize(
    "relative",
    [
        Path("literatures-old") / "note.md",
        Path("log") / "note.md",
        Path("inbox") / "note.md",
    ],
)
def test_posttooluse_is_silent_outside_concept_roots(fixture_vault, relative):
    _make_hook_vault(fixture_vault)
    note = fixture_vault / relative
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text("# Not a concept note\n")

    result = _run_hook(fixture_vault, _payload(note, fixture_vault))

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def test_posttooluse_silences_outside_symlink_and_symlinked_vault_marker(
    fixture_vault, tmp_path
):
    _make_hook_vault(fixture_vault)
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\n")
    escaped = fixture_vault / "synthesis" / "escaped.md"
    escaped.symlink_to(outside)

    result = _run_hook(fixture_vault, _payload(escaped, fixture_vault))

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""
    outside_dir = tmp_path / "outside-dir"
    outside_dir.mkdir()
    (outside_dir / "component.md").write_text("# Outside component\n")
    escaped_dir = fixture_vault / "synthesis" / "escaped-dir"
    escaped_dir.symlink_to(outside_dir, target_is_directory=True)

    result = _run_hook(
        fixture_vault,
        _payload(escaped_dir / "component.md", fixture_vault),
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""
    (fixture_vault / ".harness").rmdir()
    marker = tmp_path / "marker"
    marker.mkdir()
    (fixture_vault / ".harness").symlink_to(marker)
    note = fixture_vault / "projects" / "brief" / "draft.md"

    result = _run_hook(fixture_vault, _payload(note, fixture_vault))

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def test_posttooluse_silences_dependency_import_failure(tmp_path):
    plugin = tmp_path / "plugin"
    hooks = plugin / "hooks"
    hooks.mkdir(parents=True)
    copied_hook = hooks / "posttooluse_lint.py"
    shutil.copyfile(HOOK, copied_hook)
    vault = tmp_path / "vault"
    vault.mkdir()
    _make_hook_vault(vault)
    note = vault / "synthesis" / "note.md"
    note.parent.mkdir()
    note.write_text("# Note\n")

    result = subprocess.run(
        [sys.executable, str(copied_hook)],
        cwd=tmp_path,
        input=json.dumps(_payload(note, vault)),
        text=True,
        capture_output=True,
        check=False,
        env={"PATH": os.environ["PATH"], "PYTHONPATH": ""},
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def test_posttooluse_silences_checker_exceptions(fixture_vault, monkeypatch, capsys):
    _make_hook_vault(fixture_vault)
    note = fixture_vault / "synthesis" / "clean.md"
    note.write_text("# Clean synthesis\n")
    hook = _load_hook()

    def explode(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(hook, "_file_outcomes", explode)
    monkeypatch.setattr(
        sys, "stdin", io.StringIO(json.dumps(_payload(note, fixture_vault)))
    )

    assert hook.main() == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_posttooluse_warns_for_literature_even_if_checkers_fail(
    fixture_vault, monkeypatch, capsys
):
    _make_hook_vault(fixture_vault)
    note = fixture_vault / "literatures" / "clean.md"
    note.write_text("# Literature\n")
    hook = _load_hook()

    def explode(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(hook, "_file_outcomes", explode)
    monkeypatch.setattr(
        sys, "stdin", io.StringIO(json.dumps(_payload(note, fixture_vault)))
    )

    assert hook.main() == 0
    output = json.loads(capsys.readouterr().out)
    assert "evidence-layer" in output["hookSpecificOutput"]["additionalContext"]


def test_posttooluse_warns_for_unreachable_per_file_check(fixture_vault):
    _make_hook_vault(fixture_vault)
    note = fixture_vault / "projects" / "brief" / "unreachable.md"
    note.write_text(
        "- (quote) Missing source [@unknown, p. 1] ^c-12345678\n"
        "  > Missing source quote\n"
    )

    result = _run_hook(fixture_vault, _payload(note, fixture_vault))

    context = _warning(result)
    assert "UNREACHABLE quote" in context
