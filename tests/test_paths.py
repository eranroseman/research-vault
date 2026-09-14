import json
import subprocess
from pathlib import Path

import pytest

from research_vault import paths


@pytest.fixture
def vault_with_map(tmp_vault):
    h = tmp_vault / ".research-vault"
    h.mkdir()
    (h / "machine.json").write_text(
        json.dumps({"path_map": {"D:\\Zotero\\": "/mnt/d/Zotero/"}})
    )
    return tmp_vault


def test_prefix_map(vault_with_map):
    p = paths.to_local("D:\\Zotero\\storage\\AB\\x.pdf", vault_with_map)
    assert p == Path("/mnt/d/Zotero/storage/AB/x.pdf")


def test_prefix_map_case_insensitive(vault_with_map):
    p = paths.to_local("d:\\zotero\\storage\\AB\\x.pdf", vault_with_map)
    assert p == Path("/mnt/d/Zotero/storage/AB/x.pdf")


def test_wslpath_fallback(tmp_vault, monkeypatch):
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess(
            a, 0, stdout="/mnt/d/Zotero/storage/AB/x.pdf\n"
        ),
    )
    p = paths.to_local("D:\\Zotero\\storage\\AB\\x.pdf", tmp_vault)
    assert p == Path("/mnt/d/Zotero/storage/AB/x.pdf")


def test_unresolvable_raises(tmp_vault, monkeypatch):
    def boom(*a, **k):
        raise FileNotFoundError("wslpath missing")

    monkeypatch.setattr(subprocess, "run", boom)
    with pytest.raises(paths.PathError):
        paths.to_local("D:\\x.pdf", tmp_vault)


def test_wslpath_is_run_captured_as_text_and_unchecked_and_both_answers_must_hold(
    tmp_vault, monkeypatch
):
    """wslpath is invoked with its output captured as text and never `check`ed
    (a non-zero exit is the fallback's own signal, not an exception), and only
    exit 0 WITH a non-empty answer resolves: exit 0 with nothing, or an answer
    under a failing exit, is unresolvable."""
    seen: list[dict] = []
    answers = iter([(0, ""), (1, "/mnt/d/x.pdf\n")])

    def fake_run(command, **kwargs):
        seen.append({"command": command, **kwargs})
        code, out = next(answers)
        return subprocess.CompletedProcess(command, code, stdout=out)

    monkeypatch.setattr(paths.subprocess, "run", fake_run)
    for _ in range(2):
        with pytest.raises(paths.PathError):
            paths.to_local("D:\\x.pdf", tmp_vault)
    assert (
        seen
        == [
            {
                "command": ["wslpath", "-u", "D:\\x.pdf"],
                "capture_output": True,
                "text": True,
                "check": False,
            }
        ]
        * 2
    )


def test_bbt_host_target_is_the_native_absolute_path_off_wsl(monkeypatch):
    monkeypatch.setattr(paths, "_running_in_wsl", lambda: False)

    assert paths.to_bbt_host("relative-vault/system/bibliography.json") == str(
        Path("relative-vault/system/bibliography.json").absolute()
    )


def test_bbt_host_target_translates_through_wslpath_on_wsl(monkeypatch):
    monkeypatch.setattr(paths, "_running_in_wsl", lambda: True)

    def translate(command, **kwargs):
        assert command == ["wslpath", "-w", "/vault/system/bibliography.json"]
        assert kwargs == {"capture_output": True, "text": True, "check": False}
        return subprocess.CompletedProcess(
            command, 0, stdout="C:\\vault\\system\\bibliography.json\n"
        )

    monkeypatch.setattr(paths.subprocess, "run", translate)

    assert (
        paths.to_bbt_host("/vault/system/bibliography.json")
        == "C:\\vault\\system\\bibliography.json"
    )


@pytest.mark.parametrize(("returncode", "stdout"), [(1, "ignored"), (0, "")])
def test_bbt_host_translation_refuses_failed_wslpath_output(
    monkeypatch, returncode, stdout
):
    monkeypatch.setattr(paths, "_running_in_wsl", lambda: True)
    monkeypatch.setattr(
        paths.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args, returncode, stdout=stdout, stderr="translation failed"
        ),
    )

    with pytest.raises(paths.PathError):
        paths.to_bbt_host("/vault/system/bibliography.json")


def test_bbt_host_translation_refuses_a_wslpath_that_cannot_launch(monkeypatch):
    monkeypatch.setattr(paths, "_running_in_wsl", lambda: True)

    def unavailable(*args, **kwargs):
        raise FileNotFoundError("wslpath missing")

    monkeypatch.setattr(paths.subprocess, "run", unavailable)

    with pytest.raises(paths.PathError):
        paths.to_bbt_host("/vault/system/bibliography.json")


def test_wsl_detection_uses_environment_or_kernel_release(monkeypatch):
    monkeypatch.delenv("WSL_INTEROP", raising=False)
    monkeypatch.delenv("WSL_DISTRO_NAME", raising=False)
    monkeypatch.setattr(paths.platform, "release", lambda: "ordinary-linux")
    assert paths._running_in_wsl() is False

    monkeypatch.setenv("WSL_INTEROP", "/run/WSL/1_interop")
    assert paths._running_in_wsl() is True
    monkeypatch.delenv("WSL_INTEROP")

    monkeypatch.setattr(
        paths.platform, "release", lambda: "6.6.87.2-microsoft-standard-WSL2"
    )
    assert paths._running_in_wsl() is True
