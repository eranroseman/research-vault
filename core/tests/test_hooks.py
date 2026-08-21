import importlib.util
import io
import json
import os
import shlex
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from harness_core import Result, inbox
from harness_core.checks import Outcome

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "posttooluse_lint.py"
STOP_HOOK = REPO / "hooks" / "stop_publish_gate.py"
HOOKS_MANIFEST = REPO / "hooks" / "hooks.json"


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


def _load_stop_hook():
    spec = importlib.util.spec_from_file_location("stop_publish_gate", STOP_HOOK)
    assert spec is not None
    assert spec.loader is not None
    hook = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hook)
    return hook


def _stop_payload(vault: Path, *, active: bool = False) -> dict:
    return {
        "cwd": str(vault),
        "hook_event_name": "Stop",
        "stop_hook_active": active,
    }


def _arm_publish(
    vault: Path,
    *,
    project: str = "projects/brief",
    blocks: int = 0,
    bypass: str | None = None,
) -> Path:
    harness = vault / ".harness"
    harness.mkdir(exist_ok=True)
    flag = harness / "publish-pending.json"
    state = {"project": project, "vault": str(vault), "blocks": blocks}
    if bypass is not None:
        state["bypass"] = bypass
    flag.write_text(json.dumps(state))
    return flag


def _private_publish_files(flag: Path) -> list[Path]:
    return sorted(
        path for path in flag.parent.iterdir() if path.name.startswith(f".{flag.name}.")
    )


def _publish_state(
    *effective: Outcome,
    raw: tuple[Outcome, ...] | None = None,
    warning_effective: dict | None = None,
):
    return SimpleNamespace(
        raw=tuple(effective) if raw is None else raw,
        effective=effective,
        warning_effective={} if warning_effective is None else warning_effective,
    )


def _invoke_stop(hook, monkeypatch, capsys, payload: object) -> str:
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    assert hook.main() == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    return captured.out


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


def test_stop_hooks_manifest_registers_posttooluse_and_stop_commands():
    assert json.loads(HOOKS_MANIFEST.read_text()) == {
        "description": "Knowledge-harness verification hooks",
        "hooks": {
            "PostToolUse": [
                {
                    "matcher": "Edit|Write",
                    "hooks": [
                        {
                            "type": "command",
                            "command": (
                                'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/'
                                'posttooluse_lint.py"'
                            ),
                        }
                    ],
                }
            ],
            "Stop": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": (
                                'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/'
                                'stop_publish_gate.py"'
                            ),
                        }
                    ]
                }
            ],
        },
    }


def test_stop_gate_is_inert_without_flag_before_importing_core(tmp_path):
    plugin = tmp_path / "plugin"
    hooks = plugin / "hooks"
    hooks.mkdir(parents=True)
    copied_hook = hooks / "stop_publish_gate.py"
    shutil.copyfile(STOP_HOOK, copied_hook)
    vault = tmp_path / "vault"
    vault.mkdir()
    _make_hook_vault(vault)

    result = subprocess.run(
        [sys.executable, str(copied_hook)],
        cwd=tmp_path,
        input=json.dumps(_stop_payload(vault)),
        text=True,
        capture_output=True,
        check=False,
        env={"PATH": os.environ["PATH"], "PYTHONPATH": ""},
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def test_stop_gate_is_inert_for_malformed_payload_without_flag(tmp_path):
    result = subprocess.run(
        [sys.executable, str(STOP_HOOK)],
        cwd=tmp_path,
        input="{",
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


@pytest.mark.parametrize("nested", [False, True], ids=["direct", "nested"])
def test_stop_gate_rejects_symlinked_payload_cwd_before_importing_core(
    tmp_path, nested
):
    plugin = tmp_path / "plugin"
    hooks = plugin / "hooks"
    hooks.mkdir(parents=True)
    copied_hook = hooks / "stop_publish_gate.py"
    shutil.copyfile(STOP_HOOK, copied_hook)
    vault = tmp_path / "vault"
    (vault / "projects" / "brief").mkdir(parents=True)
    flag = _arm_publish(vault)
    before = flag.read_bytes()
    alias_parent = tmp_path / "alias-parent"
    alias_parent.mkdir()
    alias = alias_parent / "vault-alias" if nested else tmp_path / "vault-alias"
    alias.symlink_to(vault, target_is_directory=True)
    cwd = alias / "projects" / "brief" if nested else alias

    result = subprocess.run(
        [sys.executable, str(copied_hook)],
        cwd=tmp_path,
        input=json.dumps(_stop_payload(cwd)),
        text=True,
        capture_output=True,
        check=False,
        env={"PATH": os.environ["PATH"], "PYTHONPATH": ""},
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""
    assert flag.read_bytes() == before


def test_stop_gate_pass_clears_flag(fixture_vault, monkeypatch, capsys):
    flag = _arm_publish(fixture_vault)
    hook = _load_stop_hook()
    seen = []

    def verify(vault):
        seen.append(vault)
        return _publish_state(
            Outcome("quote", "smith2020#^c-11111111", Result.MATCHED, "matched")
        )

    monkeypatch.setattr(hook, "_verify_publish", verify)

    assert _invoke_stop(hook, monkeypatch, capsys, _stop_payload(fixture_vault)) == ""
    assert seen == [fixture_vault]
    assert not flag.exists()


@pytest.mark.parametrize(
    "outcome",
    [
        Outcome(
            "quote",
            "smith2020#^c-11111111",
            Result.UNMATCHED,
            "mismatch — quote differs",
        ),
        Outcome(
            "web-archive",
            "https://example.test/archive",
            Result.UNREACHABLE,
            "outage — archive unavailable",
        ),
    ],
)
def test_stop_gate_blocks_publish_closing_unmatched_or_genuine_unreachable(
    fixture_vault, monkeypatch, capsys, outcome
):
    flag = _arm_publish(fixture_vault)
    hook = _load_stop_hook()
    monkeypatch.setattr(hook, "_verify_publish", lambda _vault: _publish_state(outcome))

    output = json.loads(
        _invoke_stop(hook, monkeypatch, capsys, _stop_payload(fixture_vault))
    )

    assert set(output) == {"decision", "reason"}
    assert output["decision"] == "block"
    assert outcome.check in output["reason"]
    assert json.loads(flag.read_text()) == {
        "project": "projects/brief",
        "vault": str(fixture_vault),
        "blocks": 1,
    }


def test_stop_gate_uses_effective_publish_state_for_acknowledged_failure(
    fixture_vault, monkeypatch, capsys
):
    raw = Outcome(
        "quote",
        "smith2020#^c-11111111",
        Result.UNMATCHED,
        "mismatch — acknowledged quote",
    )
    flag = _arm_publish(fixture_vault)
    hook = _load_stop_hook()
    monkeypatch.setattr(
        hook,
        "_verify_publish",
        lambda _vault: _publish_state(raw=(raw,)),
    )

    assert _invoke_stop(hook, monkeypatch, capsys, _stop_payload(fixture_vault)) == ""
    assert not flag.exists()


def test_stop_gate_blocks_effective_publish_warning(fixture_vault, monkeypatch, capsys):
    warning = {"type": "correction", "notice_date": "2026-08-20"}
    outcome = Outcome(
        "update-notice",
        "smith2020",
        Result.MATCHED,
        "matched",
        {"warn_notices": [warning]},
    )
    hook = _load_stop_hook()
    _arm_publish(fixture_vault)
    monkeypatch.setattr(
        hook,
        "_verify_publish",
        lambda _vault: _publish_state(
            outcome,
            warning_effective={(id(outcome), 0): True},
        ),
    )

    output = json.loads(
        _invoke_stop(hook, monkeypatch, capsys, _stop_payload(fixture_vault))
    )

    assert output["decision"] == "block"
    assert "correction" in output["reason"]


def test_stop_gate_synthetic_offline_outcome_never_blocks_or_mutates(
    fixture_vault, monkeypatch, capsys
):
    synthetic = Outcome(
        "doi",
        "smith2020",
        Result.UNREACHABLE,
        "outage — network disabled",
        {"synthetic_offline": True},
    )
    flag = _arm_publish(fixture_vault, blocks=4)
    before = flag.read_bytes()
    hook = _load_stop_hook()
    monkeypatch.setattr(
        hook,
        "_verify_publish",
        lambda _vault: _publish_state(raw=(synthetic,)),
    )

    assert _invoke_stop(hook, monkeypatch, capsys, _stop_payload(fixture_vault)) == ""
    assert flag.read_bytes() == before


def test_stop_gate_bypass_appends_exact_human_record_and_clears_flag(
    fixture_vault, monkeypatch, capsys
):
    flag = _arm_publish(fixture_vault, bypass="source checked by hand")
    hook = _load_stop_hook()

    def should_not_verify(_vault):
        raise AssertionError("bypass must precede verification")

    monkeypatch.setattr(hook, "_verify_publish", should_not_verify)

    assert _invoke_stop(hook, monkeypatch, capsys, _stop_payload(fixture_vault)) == ""
    assert not flag.exists()
    entries = inbox.load(fixture_vault)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.check == "publish-gate"
    assert entry.target == "path-bytes:projects/brief"
    assert entry.target_kind == "repo-path"
    assert entry.result == "UNMATCHED"
    assert entry.actor == "human:publish-bypass"
    assert entry.reason == "manual — publish-gate bypass: source checked by hand"


def test_stop_gate_exception_fails_closed_while_armed(
    fixture_vault, monkeypatch, capsys
):
    flag = _arm_publish(fixture_vault)
    hook = _load_stop_hook()

    def explode(_vault):
        raise RuntimeError("boom")

    monkeypatch.setattr(hook, "_verify_publish", explode)

    output = json.loads(
        _invoke_stop(hook, monkeypatch, capsys, _stop_payload(fixture_vault))
    )

    assert output["decision"] == "block"
    assert "verification unavailable" in output["reason"]
    assert json.loads(flag.read_text())["blocks"] == 1


@pytest.mark.parametrize(
    "state",
    [
        {"project_path": "projects/brief", "blocks": 0},
        {"project": "projects/../outside", "blocks": 0},
        {"project": "/projects/brief", "blocks": 0},
        {"project": "projects/brief", "blocks": True},
        {"project": "projects/brief", "blocks": -1},
        {"project": "projects/brief", "blocks": 0, "unknown": "field"},
        {"project": "projects/brief", "blocks": 0, "bypass": "two\nlines"},
    ],
)
def test_stop_gate_rejects_malformed_project_key_path_or_blocks(
    fixture_vault, monkeypatch, capsys, state
):
    harness = fixture_vault / ".harness"
    harness.mkdir(exist_ok=True)
    flag = harness / "publish-pending.json"
    state["vault"] = str(fixture_vault)
    flag.write_text(json.dumps(state))
    before = flag.read_bytes()
    hook = _load_stop_hook()

    def should_not_verify(_vault):
        raise AssertionError("malformed flag must stay unarmed")

    monkeypatch.setattr(hook, "_verify_publish", should_not_verify)

    assert _invoke_stop(hook, monkeypatch, capsys, _stop_payload(fixture_vault)) == ""
    assert flag.read_bytes() == before


def test_stop_gate_rejects_mismatched_vault_and_escaped_project_symlink(
    fixture_vault, tmp_path, monkeypatch, capsys
):
    outside = tmp_path / "outside"
    outside.mkdir()
    escaped = fixture_vault / "projects" / "escaped"
    escaped.symlink_to(outside, target_is_directory=True)
    hook = _load_stop_hook()
    monkeypatch.setattr(
        hook,
        "_verify_publish",
        lambda _vault: pytest.fail("unsafe flag must stay unarmed"),
    )
    flag = _arm_publish(fixture_vault, project="projects/escaped")
    before = flag.read_bytes()

    assert _invoke_stop(hook, monkeypatch, capsys, _stop_payload(fixture_vault)) == ""
    assert flag.read_bytes() == before

    flag.write_text(
        json.dumps(
            {
                "project": "projects/brief",
                "vault": str(fixture_vault.parent),
                "blocks": 0,
            }
        )
    )
    before = flag.read_bytes()

    assert _invoke_stop(hook, monkeypatch, capsys, _stop_payload(fixture_vault)) == ""
    assert flag.read_bytes() == before


def test_stop_gate_blocks_seven_times_then_warns_visibly_on_eighth(
    fixture_vault, monkeypatch, capsys
):
    outcome = Outcome(
        "quote",
        "smith2020#^c-11111111",
        Result.UNMATCHED,
        "mismatch — quote differs",
    )
    hook = _load_stop_hook()
    monkeypatch.setattr(hook, "_verify_publish", lambda _vault: _publish_state(outcome))
    flag = _arm_publish(fixture_vault, blocks=6)

    seventh = json.loads(
        _invoke_stop(
            hook,
            monkeypatch,
            capsys,
            _stop_payload(fixture_vault, active=True),
        )
    )

    assert seventh["decision"] == "block"
    assert json.loads(flag.read_text())["blocks"] == 7

    eighth = json.loads(
        _invoke_stop(
            hook,
            monkeypatch,
            capsys,
            _stop_payload(fixture_vault, active=True),
        )
    )

    assert set(eighth) == {"systemMessage"}
    assert "eight" in eighth["systemMessage"]
    assert flag.exists()
    assert json.loads(flag.read_text())["blocks"] == 8


def test_stop_gate_inactive_payload_resets_consecutive_blocks(
    fixture_vault, monkeypatch, capsys
):
    outcome = Outcome(
        "quote",
        "smith2020#^c-11111111",
        Result.UNMATCHED,
        "mismatch — quote differs",
    )
    hook = _load_stop_hook()
    monkeypatch.setattr(hook, "_verify_publish", lambda _vault: _publish_state(outcome))
    flag = _arm_publish(fixture_vault, blocks=7)

    output = json.loads(
        _invoke_stop(
            hook,
            monkeypatch,
            capsys,
            _stop_payload(fixture_vault, active=False),
        )
    )

    assert output["decision"] == "block"
    assert json.loads(flag.read_text())["blocks"] == 1


def test_stop_hook_manifest_commands_execute_from_plugin_path_with_spaces(tmp_path):
    plugin = tmp_path / "plugin with spaces"
    shutil.copytree(REPO / "hooks", plugin / "hooks")
    vault = tmp_path / "vault"
    vault.mkdir()
    _make_hook_vault(vault)
    payloads = {
        "PostToolUse": {},
        "Stop": _stop_payload(vault),
    }
    manifest = json.loads((plugin / "hooks" / "hooks.json").read_text())

    for event, payload in payloads.items():
        command = manifest["hooks"][event][0]["hooks"][0]["command"]
        command = command.replace("${CLAUDE_PLUGIN_ROOT}", str(plugin))
        result = subprocess.run(
            shlex.split(command),
            cwd=tmp_path,
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
            env={"PATH": os.environ["PATH"], "PYTHONPATH": ""},
        )

        assert result.returncode == 0
        assert result.stdout == ""
        assert result.stderr == ""


def test_stop_gate_armed_missing_core_fails_closed(tmp_path):
    plugin = tmp_path / "plugin"
    hooks = plugin / "hooks"
    hooks.mkdir(parents=True)
    copied_hook = hooks / "stop_publish_gate.py"
    shutil.copyfile(STOP_HOOK, copied_hook)
    vault = tmp_path / "vault"
    (vault / "projects" / "brief").mkdir(parents=True)
    flag = _arm_publish(vault)

    result = subprocess.run(
        [sys.executable, str(copied_hook)],
        cwd=tmp_path,
        input=json.dumps(_stop_payload(vault)),
        text=True,
        capture_output=True,
        check=False,
        env={"PATH": os.environ["PATH"], "PYTHONPATH": ""},
    )

    assert result.returncode == 0
    assert result.stderr == ""
    output = json.loads(result.stdout)
    assert set(output) == {"decision", "reason"}
    assert output["decision"] == "block"
    assert "verification unavailable" in output["reason"]
    assert json.loads(flag.read_text())["blocks"] == 1


def test_stop_gate_rejects_symlinked_harness_and_flag(tmp_path, monkeypatch, capsys):
    hook = _load_stop_hook()
    vault = tmp_path / "vault"
    vault.mkdir()
    outside_harness = tmp_path / "outside-harness"
    outside_harness.mkdir()
    (vault / ".harness").symlink_to(outside_harness, target_is_directory=True)
    monkeypatch.setattr(
        hook,
        "_verify_publish",
        lambda _vault: pytest.fail("symlinked harness must stay unarmed"),
    )

    assert _invoke_stop(hook, monkeypatch, capsys, _stop_payload(vault)) == ""

    (vault / ".harness").unlink()
    (vault / ".harness").mkdir()
    outside_flag = tmp_path / "outside-flag.json"
    outside_flag.write_text(
        json.dumps({"project": "projects/brief", "vault": str(vault), "blocks": 0})
    )
    (vault / ".harness" / "publish-pending.json").symlink_to(outside_flag)

    assert _invoke_stop(hook, monkeypatch, capsys, _stop_payload(vault)) == ""
    assert json.loads(outside_flag.read_text())["blocks"] == 0


@pytest.mark.parametrize("active", [None, 1, "true"])
def test_stop_gate_requires_boolean_stop_hook_active_while_armed(
    fixture_vault, monkeypatch, capsys, active
):
    flag = _arm_publish(fixture_vault, blocks=5)
    hook = _load_stop_hook()
    monkeypatch.setattr(
        hook,
        "_verify_publish",
        lambda _vault: pytest.fail(
            "malformed Stop input must fail before verification"
        ),
    )
    payload = _stop_payload(fixture_vault)
    if active is None:
        payload.pop("stop_hook_active")
    else:
        payload["stop_hook_active"] = active

    output = json.loads(_invoke_stop(hook, monkeypatch, capsys, payload))

    assert output["decision"] == "block"
    assert json.loads(flag.read_text())["blocks"] == 1


def test_stop_gate_counter_update_failure_blocks_and_retains_flag(
    fixture_vault, monkeypatch, capsys
):
    flag = _arm_publish(fixture_vault, blocks=2)
    before = flag.read_bytes()
    hook = _load_stop_hook()
    outcome = Outcome(
        "quote",
        "smith2020#^c-11111111",
        Result.UNMATCHED,
        "mismatch — quote differs",
    )
    monkeypatch.setattr(hook, "_verify_publish", lambda _vault: _publish_state(outcome))
    monkeypatch.setattr(
        hook,
        "_write_blocks",
        lambda *_args: (_ for _ in ()).throw(OSError("write failed")),
    )

    output = json.loads(
        _invoke_stop(hook, monkeypatch, capsys, _stop_payload(fixture_vault))
    )

    assert set(output) == {"decision", "reason"}
    assert output["decision"] == "block"
    assert flag.read_bytes() == before


def test_stop_gate_does_not_clear_concurrently_rearmed_flag(
    fixture_vault, monkeypatch, capsys
):
    flag = _arm_publish(fixture_vault)
    hook = _load_stop_hook()
    replacement = {
        "project": "projects/brief",
        "vault": str(fixture_vault),
        "blocks": 5,
    }

    def verify(_vault):
        flag.unlink()
        flag.write_text(json.dumps(replacement))
        return _publish_state(
            Outcome("quote", "smith2020#^c-11111111", Result.MATCHED, "matched")
        )

    monkeypatch.setattr(hook, "_verify_publish", verify)

    output = json.loads(
        _invoke_stop(hook, monkeypatch, capsys, _stop_payload(fixture_vault))
    )

    assert output["decision"] == "block"
    assert json.loads(flag.read_text()) == replacement


def test_stop_gate_counter_install_never_clobbers_last_moment_rearm(
    fixture_vault, monkeypatch, capsys
):
    flag = _arm_publish(fixture_vault)
    hook = _load_stop_hook()
    outcome = Outcome(
        "quote",
        "smith2020#^c-11111111",
        Result.UNMATCHED,
        "mismatch — quote differs",
    )
    replacement = {
        "project": "projects/brief",
        "vault": str(fixture_vault),
        "blocks": 6,
    }
    original_replace = hook.os.replace
    original_link = hook.os.link
    raced = False

    def rearm() -> None:
        nonlocal raced
        if raced:
            return
        raced = True
        flag.unlink(missing_ok=True)
        flag.write_text(json.dumps(replacement))

    def replace(source, destination):
        if Path(destination) == flag:
            rearm()
        return original_replace(source, destination)

    def link(source, destination):
        if Path(destination) == flag:
            rearm()
        return original_link(source, destination)

    monkeypatch.setattr(hook, "_verify_publish", lambda _vault: _publish_state(outcome))
    monkeypatch.setattr(hook.os, "replace", replace)
    monkeypatch.setattr(hook.os, "link", link)

    output = json.loads(
        _invoke_stop(hook, monkeypatch, capsys, _stop_payload(fixture_vault))
    )

    assert raced is True
    assert output["decision"] == "block"
    assert json.loads(flag.read_text()) == replacement


def test_stop_gate_counter_install_failure_restores_exact_claim_without_stale_files(
    fixture_vault, monkeypatch, capsys
):
    flag = _arm_publish(fixture_vault, blocks=2)
    before = flag.read_bytes()
    hook = _load_stop_hook()
    outcome = Outcome(
        "quote",
        "smith2020#^c-11111111",
        Result.UNMATCHED,
        "mismatch — quote differs",
    )
    original_link = hook.os.link

    def fail_install(source, destination):
        source = Path(source)
        if Path(destination) == flag and ".claimed." not in source.name:
            raise OSError("counter install failed")
        return original_link(source, destination)

    monkeypatch.setattr(hook, "_verify_publish", lambda _vault: _publish_state(outcome))
    monkeypatch.setattr(hook.os, "link", fail_install)

    output = json.loads(
        _invoke_stop(hook, monkeypatch, capsys, _stop_payload(fixture_vault))
    )

    assert output == {
        "decision": "block",
        "reason": hook.FAIL_CLOSED_REASON,
    }
    assert flag.read_bytes() == before
    assert _private_publish_files(flag) == []


def test_stop_gate_counter_install_failure_preserves_concurrent_successor(
    fixture_vault, monkeypatch, capsys
):
    flag = _arm_publish(fixture_vault)
    hook = _load_stop_hook()
    outcome = Outcome(
        "quote",
        "smith2020#^c-11111111",
        Result.UNMATCHED,
        "mismatch — quote differs",
    )
    replacement = {
        "project": "projects/brief",
        "vault": str(fixture_vault),
        "blocks": 6,
    }
    original_link = hook.os.link
    installed = False

    def install_successor_then_fail(source, destination):
        nonlocal installed
        source = Path(source)
        if (
            Path(destination) == flag
            and ".claimed." not in source.name
            and not installed
        ):
            installed = True
            flag.write_text(json.dumps(replacement))
            raise FileExistsError("concurrent successor")
        return original_link(source, destination)

    monkeypatch.setattr(hook, "_verify_publish", lambda _vault: _publish_state(outcome))
    monkeypatch.setattr(hook.os, "link", install_successor_then_fail)

    output = json.loads(
        _invoke_stop(hook, monkeypatch, capsys, _stop_payload(fixture_vault))
    )

    assert output == {
        "decision": "block",
        "reason": hook.FAIL_CLOSED_REASON,
    }
    assert json.loads(flag.read_text()) == replacement
    assert _private_publish_files(flag) == []


def test_stop_gate_recovers_retained_claim_after_install_and_restore_failures(
    fixture_vault, monkeypatch, capsys
):
    flag = _arm_publish(fixture_vault, blocks=2)
    before = flag.read_bytes()
    hook = _load_stop_hook()
    outcome = Outcome(
        "quote",
        "smith2020#^c-11111111",
        Result.UNMATCHED,
        "mismatch — quote differs",
    )
    original_link = hook.os.link

    def fail_install_and_restore(source, destination):
        if Path(destination) == flag:
            raise OSError("link unavailable")
        return original_link(source, destination)

    monkeypatch.setattr(hook, "_verify_publish", lambda _vault: _publish_state(outcome))
    monkeypatch.setattr(hook.os, "link", fail_install_and_restore)

    first = json.loads(
        _invoke_stop(
            hook,
            monkeypatch,
            capsys,
            _stop_payload(fixture_vault, active=True),
        )
    )

    assert first == {
        "decision": "block",
        "reason": hook.FAIL_CLOSED_REASON,
    }
    assert not flag.exists()
    claims = _private_publish_files(flag)
    assert len(claims) == 1
    assert ".claimed." in claims[0].name
    assert claims[0].read_bytes() == before

    monkeypatch.setattr(hook.os, "link", original_link)

    second = json.loads(
        _invoke_stop(
            hook,
            monkeypatch,
            capsys,
            _stop_payload(fixture_vault, active=True),
        )
    )

    assert second["decision"] == "block"
    assert json.loads(flag.read_text())["blocks"] == 3
    assert _private_publish_files(flag) == []


def test_stop_gate_bypass_inbox_failure_blocks_and_retains_flag(
    fixture_vault, monkeypatch, capsys
):
    flag = _arm_publish(fixture_vault, bypass="checked by hand")
    before = flag.read_bytes()
    hook = _load_stop_hook()
    monkeypatch.setattr(
        hook,
        "_append_bypass",
        lambda *_args: (_ for _ in ()).throw(OSError("inbox unavailable")),
    )

    output = json.loads(
        _invoke_stop(hook, monkeypatch, capsys, _stop_payload(fixture_vault))
    )

    assert output["decision"] == "block"
    assert flag.read_bytes() == before
    assert inbox.load(fixture_vault) == []


def test_stop_gate_bypass_durable_append_finishes_before_flag_clear(
    fixture_vault, monkeypatch, capsys
):
    flag = _arm_publish(fixture_vault, bypass="checked by hand")
    hook = _load_stop_hook()
    events = []
    original_append = inbox.append_entry
    original_fsync = os.fsync
    original_clear = hook._clear_flag
    queue = fixture_vault / inbox.INBOX_PATH

    def fsync(descriptor):
        if stat.S_ISREG(os.fstat(descriptor).st_mode):
            assert "manual — publish-gate bypass".encode() in queue.read_bytes()
            events.append("file-synced")
        return original_fsync(descriptor)

    def append(*args, **kwargs):
        assert kwargs["durable"] is True
        return original_append(*args, **kwargs)

    def clear(armed):
        events.append("clear")
        return original_clear(armed)

    monkeypatch.setattr(os, "fsync", fsync)
    monkeypatch.setattr(inbox, "append_entry", append)
    monkeypatch.setattr(hook, "_clear_flag", clear)

    assert _invoke_stop(hook, monkeypatch, capsys, _stop_payload(fixture_vault)) == ""
    assert events == ["file-synced", "clear"]
    assert not flag.exists()


def test_stop_gate_bypass_flush_failure_blocks_and_retains_exact_flag(
    fixture_vault, monkeypatch, capsys
):
    flag = _arm_publish(fixture_vault, bypass="checked by hand")
    before = flag.read_bytes()
    hook = _load_stop_hook()
    queue = fixture_vault / inbox.INBOX_PATH
    original_open = Path.open

    class FlushFailure:
        def __init__(self, stream):
            self.stream = stream

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            self.stream.close()

        def write(self, value):
            return self.stream.write(value)

        def flush(self):
            raise OSError("flush failed")

        def fileno(self):
            return self.stream.fileno()

    def open_path(path, *args, **kwargs):
        stream = original_open(path, *args, **kwargs)
        if Path(path) == queue and args and args[0] == "a":
            return FlushFailure(stream)
        return stream

    monkeypatch.setattr(Path, "open", open_path)

    output = json.loads(
        _invoke_stop(hook, monkeypatch, capsys, _stop_payload(fixture_vault))
    )

    assert output == {
        "decision": "block",
        "reason": hook.FAIL_CLOSED_REASON,
    }
    assert flag.read_bytes() == before


@pytest.mark.parametrize("failure", ["file", "directory"])
def test_stop_gate_bypass_sync_failure_blocks_and_retains_exact_flag(
    fixture_vault, monkeypatch, capsys, failure
):
    queue = fixture_vault / inbox.INBOX_PATH
    if failure == "directory":
        queue.unlink()
    flag = _arm_publish(fixture_vault, bypass="checked by hand")
    before = flag.read_bytes()
    hook = _load_stop_hook()
    original_fsync = os.fsync

    def fsync(descriptor):
        mode = os.fstat(descriptor).st_mode
        if failure == "file" and stat.S_ISREG(mode):
            raise OSError("file sync failed")
        if failure == "directory" and stat.S_ISDIR(mode):
            raise OSError("directory sync failed")
        return original_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", fsync)

    output = json.loads(
        _invoke_stop(hook, monkeypatch, capsys, _stop_payload(fixture_vault))
    )

    assert output == {
        "decision": "block",
        "reason": hook.FAIL_CLOSED_REASON,
    }
    assert flag.read_bytes() == before


def test_stop_gate_bypass_clear_race_blocks_and_preserves_rearmed_flag(
    fixture_vault, monkeypatch, capsys
):
    flag = _arm_publish(fixture_vault, bypass="checked by hand")
    hook = _load_stop_hook()
    append = hook._append_bypass
    replacement = {
        "project": "projects/brief",
        "vault": str(fixture_vault),
        "blocks": 4,
    }

    def append_then_rearm(vault, project, reason):
        append(vault, project, reason)
        flag.unlink()
        flag.write_text(json.dumps(replacement))

    monkeypatch.setattr(hook, "_append_bypass", append_then_rearm)

    output = json.loads(
        _invoke_stop(hook, monkeypatch, capsys, _stop_payload(fixture_vault))
    )

    assert output["decision"] == "block"
    assert json.loads(flag.read_text()) == replacement
    assert len(inbox.load(fixture_vault)) == 1


def test_stop_gate_bypass_retry_after_a_failed_clear_keeps_one_ackable_record(
    fixture_vault, monkeypatch, capsys
):
    """Letting a retried bypass duplicate its finding id must fail."""
    flag = _arm_publish(fixture_vault, bypass="checked by hand")
    hook = _load_stop_hook()
    original_clear = hook._clear_flag

    monkeypatch.setattr(
        hook,
        "_clear_flag",
        lambda _armed: (_ for _ in ()).throw(OSError("flag clear failed")),
    )

    first = json.loads(
        _invoke_stop(hook, monkeypatch, capsys, _stop_payload(fixture_vault))
    )

    assert first == {"decision": "block", "reason": hook.FAIL_CLOSED_REASON}
    assert flag.exists()
    assert len(inbox.load(fixture_vault)) == 1

    monkeypatch.setattr(hook, "_clear_flag", original_clear)

    assert (
        _invoke_stop(
            hook,
            monkeypatch,
            capsys,
            _stop_payload(fixture_vault, active=True),
        )
        == ""
    )
    assert not flag.exists()
    entries = inbox.load(fixture_vault)
    assert len(entries) == 1
    assert entries[0].reason == "manual — publish-gate bypass: checked by hand"
    acknowledged = inbox.append_ack(
        fixture_vault,
        entries[0].id,
        "manual — bypass reviewed",
        "human:reviewer",
    )
    assert acknowledged.ack_of == entries[0].id
    assert inbox.open_entries(fixture_vault) == []


def test_stop_gate_matches_direct_publish_state_and_effects(
    fixture_vault, tmp_path_factory, monkeypatch, capsys
):
    from harness_core import verify

    root = tmp_path_factory.mktemp("stop-publish-integration")
    direct_vault = shutil.copytree(fixture_vault, root / "direct")
    hook_vault = shutil.copytree(fixture_vault, root / "hook")
    monkeypatch.setattr(
        verify.bibliography,
        "staleness",
        lambda *_args, **_kwargs: Result.MATCHED,
    )
    monkeypatch.setattr(verify, "_network_outcomes", lambda *_args: [])
    monkeypatch.setattr(verify, "_archive_outcomes", lambda *_args: [])

    _report, effective, _hashes, warning_effective = verify.verify_state(
        direct_vault,
        network=True,
    )
    direct_code, direct_reasons = verify.surface_decision(
        "publish", effective, warning_effective
    )
    _arm_publish(hook_vault)
    hook = _load_stop_hook()

    output = json.loads(
        _invoke_stop(hook, monkeypatch, capsys, _stop_payload(hook_vault))
    )

    def projected_state(vault):
        return tuple(
            (str(path.relative_to(vault)), path.read_bytes())
            for root_name in ("inbox", "literatures", "projects")
            for path in sorted((vault / root_name).rglob("*"))
            if path.is_file()
        )

    assert direct_code == 1
    assert output["decision"] == "block"
    assert all(reason in output["reason"] for reason in direct_reasons)
    assert projected_state(hook_vault) == projected_state(direct_vault)
