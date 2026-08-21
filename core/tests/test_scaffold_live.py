import argparse
import contextlib
import io
import json
import os
import shlex
import shutil
import stat
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

import pytest

import harness_core.__main__ as cli
from harness_core import Result, notes, paths, scaffold
from harness_core.zotero import ZoteroClient

REPO = Path(__file__).resolve().parents[2]
CREATE_ENV = "HARNESS_LIVE_BBT_REGISTER"
CONFIRMED_ENV = "HARNESS_LIVE_AUTOEXPORT_REMOVED"
VAULT_ENV = "HARNESS_LIVE_SCAFFOLD_VAULT"
OFFLINE_HOST_TARGET = r"C:\live\x\bibliography.json"
BASE_STATE_KEYS = (
    "schema",
    "phase",
    "vault",
    "st_dev",
    "st_ino",
    "target",
    "host_target",
)


class LiveDrillConsentError(ValueError):
    pass


class StateDurabilityError(OSError):
    def __init__(self, message, *, installed):
        super().__init__(message)
        self.installed = installed


class LiveDrillConfig(NamedTuple):
    vault: Path
    state: Path
    precreated: bool
    assignment_printed: bool


def _state_artifact_stat(path: Path, error_type=RuntimeError):
    try:
        artifact_stat = os.lstat(path)
    except FileNotFoundError:
        return None
    except OSError as error:
        raise error_type("live drill recovery state cannot be inspected") from error
    if not stat.S_ISREG(artifact_stat.st_mode):
        raise error_type("live drill recovery state must be a regular non-symlink file")
    return artifact_stat


def _valid_utc_z_timestamp(value) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return False
    return parsed.strftime("%Y-%m-%dT%H:%M:%SZ") == value


def _validate_state(config, state) -> dict:
    invalid = "live drill recovery state has invalid schema-1 phase shape"
    if not isinstance(state, dict):
        raise RuntimeError(invalid)
    phase = state.get("phase")
    base = set(BASE_STATE_KEYS)
    cleanup = {
        "human_removal_confirmed_at",
        "quarantine_container",
        "quarantine",
    }
    shapes = {
        "prepared": (base, set()),
        "manual-removal-check-required": (base | {"interruption"}, set()),
        "manual-removal-required": (base, set()),
        "cleanup-confirmed-removal-pending": (base | cleanup, {"cleanup_error"}),
        "cleanup-refused": (
            base | cleanup | {"cleanup_error", "claimed_st_dev", "claimed_st_ino"},
            set(),
        ),
        "cleanup-confirmed": (
            base | cleanup,
            {"quarantine_container_cleanup_error"},
        ),
    }
    if not isinstance(phase, str) or phase not in shapes:
        raise RuntimeError(invalid)
    required, optional = shapes[phase]
    if not required.issubset(state) or set(state) - required - optional:
        raise RuntimeError(invalid)
    expected_target = config.vault / "x" / "bibliography.json"
    if (
        type(state["schema"]) is not int
        or state["schema"] != 1
        or state["vault"] != str(config.vault)
        or state["target"] != str(expected_target)
        or type(state["st_dev"]) is not int
        or type(state["st_ino"]) is not int
        or not isinstance(state["host_target"], str)
        or not state["host_target"]
    ):
        raise RuntimeError(invalid)
    if phase == "manual-removal-check-required" and (
        not isinstance(state["interruption"], str) or not state["interruption"]
    ):
        raise RuntimeError(invalid)
    if phase.startswith("cleanup-"):
        container_value = state["quarantine_container"]
        quarantine_value = state["quarantine"]
        if (
            not _valid_utc_z_timestamp(state["human_removal_confirmed_at"])
            or not isinstance(container_value, str)
            or not isinstance(quarantine_value, str)
        ):
            raise RuntimeError(invalid)
        container = Path(container_value)
        quarantine = Path(quarantine_value)
        prefix = f".{config.vault.name}.cleanup-"
        if (
            not container.is_absolute()
            or str(container) != container_value
            or container.parent != config.vault.parent
            or not container.name.startswith(prefix)
            or len(container.name) == len(prefix)
            or not quarantine.is_absolute()
            or str(quarantine) != quarantine_value
            or quarantine != container / "vault"
        ):
            raise RuntimeError(invalid)
    for error_field in ("cleanup_error", "quarantine_container_cleanup_error"):
        if error_field in state and (
            not isinstance(state[error_field], str) or not state[error_field]
        ):
            raise RuntimeError(invalid)
    if phase == "cleanup-refused" and (
        type(state["claimed_st_dev"]) is not int
        or type(state["claimed_st_ino"]) is not int
    ):
        raise RuntimeError(invalid)
    return state


def _drill_config(environ) -> LiveDrillConfig:
    raw_vault = environ.get(VAULT_ENV, "")
    if not raw_vault:
        if environ.get(CREATE_ENV) != "1":
            raise LiveDrillConsentError(f"set {CREATE_ENV}=1 to authorize creation")
        vault = Path(tempfile.mkdtemp(prefix="knowledge-harness-live-")).resolve()
        print(f"{VAULT_ENV}={shlex.quote(str(vault))}", flush=True)
        return LiveDrillConfig(
            vault=vault,
            state=vault.with_name(f".{vault.name}.state.json"),
            precreated=True,
            assignment_printed=True,
        )
    vault = Path(raw_vault)
    if not vault.is_absolute():
        raise LiveDrillConsentError(
            f"set {VAULT_ENV} to an absolute temporary vault path"
        )
    vault = vault.resolve(strict=False)
    temporary_root = Path(tempfile.gettempdir()).resolve()
    try:
        vault.relative_to(temporary_root)
    except ValueError as error:
        raise LiveDrillConsentError(
            f"{VAULT_ENV} must be under {temporary_root}"
        ) from error
    if not vault.name.startswith("knowledge-harness-live-"):
        raise LiveDrillConsentError(
            f"{VAULT_ENV} basename must start with knowledge-harness-live-"
        )
    config = LiveDrillConfig(
        vault=vault,
        state=vault.with_name(f".{vault.name}.state.json"),
        precreated=False,
        assignment_printed=False,
    )
    state_stat = _state_artifact_stat(config.state, LiveDrillConsentError)
    if state_stat is None and environ.get(CREATE_ENV) != "1":
        raise LiveDrillConsentError(f"set {CREATE_ENV}=1 to authorize creation")
    return config


def _read_state_bytes(path: Path, expected_stat=None) -> bytes:
    descriptor = None
    try:
        descriptor = os.open(
            path,
            os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0),
        )
        opened_stat = os.fstat(descriptor)
        if not stat.S_ISREG(opened_stat.st_mode) or (
            expected_stat is not None
            and (opened_stat.st_dev, opened_stat.st_ino)
            != (expected_stat.st_dev, expected_stat.st_ino)
        ):
            raise RuntimeError(
                "live drill recovery state must be a stable regular non-symlink file"
            )
        chunks = []
        while chunk := os.read(descriptor, 65536):
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _write_replacement(path: Path, payload: bytes) -> Path:
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return temporary


def _fsync_parent(path: Path) -> None:
    descriptor = os.open(
        path.parent,
        os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_CLOEXEC", 0),
    )
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_state(config, state: dict) -> None:
    state = _validate_state(config, state)
    path = config.state
    payload = (json.dumps(state, indent=2, sort_keys=True) + "\n").encode("utf-8")
    original_stat = _state_artifact_stat(path)
    original_payload = (
        _read_state_bytes(path, original_stat) if original_stat is not None else None
    )
    temporary = _write_replacement(path, payload)
    try:
        current_stat = _state_artifact_stat(path)
        if (original_stat is None) != (current_stat is None) or (
            original_stat is not None
            and current_stat is not None
            and (original_stat.st_dev, original_stat.st_ino)
            != (current_stat.st_dev, current_stat.st_ino)
        ):
            raise RuntimeError("live drill recovery state changed during write")
        os.replace(temporary, path)
        try:
            _fsync_parent(path)
        except OSError as error:
            installed = True
            if original_payload is not None:
                rollback = _write_replacement(path, original_payload)
                try:
                    if _state_artifact_stat(path) is None:
                        raise RuntimeError(
                            "live drill recovery state disappeared before rollback"
                        )
                    os.replace(rollback, path)
                    installed = False
                finally:
                    rollback.unlink(missing_ok=True)
            raise StateDurabilityError(str(error), installed=installed) from error
    finally:
        temporary.unlink(missing_ok=True)


def _run_retaining_state(config, *, target, host_target, operation):
    if _state_artifact_stat(config.state) is not None:
        raise RuntimeError(f"live drill recovery state already exists: {config.state}")
    if config.precreated and (
        not config.vault.is_dir()
        or config.vault.is_symlink()
        or any(config.vault.iterdir())
    ):
        raise RuntimeError("generated live drill vault is absent, unsafe, or non-empty")
    if not config.precreated and config.vault.exists():
        raise RuntimeError(f"live drill vault already exists: {config.vault}")
    if not config.precreated:
        config.vault.mkdir(mode=0o700)
    vault_stat = os.lstat(config.vault)
    if not stat.S_ISDIR(vault_stat.st_mode):
        raise RuntimeError("live drill vault is not an owned directory")
    target = Path(target).absolute()
    expected_target = config.vault / "x" / "bibliography.json"
    if target != expected_target:
        raise RuntimeError("live drill target is not the exact bibliography path")
    state = {
        "schema": 1,
        "phase": "prepared",
        "vault": str(config.vault),
        "st_dev": vault_stat.st_dev,
        "st_ino": vault_stat.st_ino,
        "target": str(target),
        "host_target": host_target,
    }
    _write_state(config, state)
    if not config.assignment_printed:
        print(f"{VAULT_ENV}={shlex.quote(str(config.vault))}", flush=True)
    try:
        result = operation()
    except BaseException as error:
        state["phase"] = "manual-removal-check-required"
        state["interruption"] = type(error).__name__
        _write_state(config, state)
        raise
    state["phase"] = "manual-removal-required"
    state.pop("interruption", None)
    _write_state(config, state)
    return result


def _load_state(config) -> dict:
    artifact_stat = _state_artifact_stat(config.state)
    if artifact_stat is None:
        raise RuntimeError("live drill recovery state is absent")
    try:
        state = json.loads(
            _read_state_bytes(config.state, artifact_stat).decode("utf-8")
        )
    except (OSError, UnicodeError, ValueError) as error:
        raise RuntimeError(
            f"live drill recovery state is unreadable: {error}"
        ) from error
    state = _validate_state(config, state)
    expected_target = config.vault / "x" / "bibliography.json"
    try:
        expected_host_target = paths.to_bbt_host(expected_target)
    except paths.PathError as error:
        raise RuntimeError(
            "live drill recovery host target cannot be validated"
        ) from error
    if (
        not isinstance(expected_host_target, str)
        or not expected_host_target
        or state["host_target"] != expected_host_target
    ):
        raise RuntimeError("live drill recovery state host target does not match")
    return state


def _vault_stat(path: Path, detail: str):
    try:
        path_stat = os.lstat(path)
    except OSError as error:
        raise RuntimeError(detail) from error
    if not stat.S_ISDIR(path_stat.st_mode):
        raise RuntimeError(detail)
    return path_stat


def _identity_matches(path_stat, state) -> bool:
    return (path_stat.st_dev, path_stat.st_ino) == (state["st_dev"], state["st_ino"])


def _quarantine_paths(config, state):
    try:
        container = Path(state["quarantine_container"])
        quarantine = Path(state["quarantine"])
    except (KeyError, TypeError) as error:
        raise RuntimeError("live drill quarantine state is malformed") from error
    if (
        not container.is_absolute()
        or container.parent != config.vault.parent
        or not container.name.startswith(f".{config.vault.name}.cleanup-")
        or quarantine != container / "vault"
    ):
        raise RuntimeError("live drill quarantine state is malformed")
    container_stat = _vault_stat(
        container,
        "pending live drill cleanup cannot be reconciled: recorded quarantine "
        "container is absent or unsafe; refusing to infer removal",
    )
    if stat.S_IMODE(container_stat.st_mode) != 0o700:
        raise RuntimeError("live drill quarantine permissions changed")
    return container, quarantine


def _finish_quarantined_cleanup(config, state) -> None:
    container, quarantine = _quarantine_paths(config, state)
    if not os.path.lexists(quarantine):
        try:
            original_stat = _vault_stat(
                config.vault, "recorded live drill vault is absent or unsafe"
            )
        except RuntimeError as error:
            raise RuntimeError(
                "pending live drill cleanup cannot be reconciled: the recorded "
                "vault and quarantine are absent or unsafe; refusing to infer removal"
            ) from error
        if not _identity_matches(original_stat, state):
            raise RuntimeError(
                "pending live drill cleanup cannot be reconciled: the original "
                "path identity changed while quarantine is absent; successor preserved"
            )
        try:
            os.rename(config.vault, quarantine)
        except OSError as error:
            detail = str(error) or type(error).__name__
            state["cleanup_error"] = f"quarantine claim failed: {detail}"
            _write_state(config, state)
            raise RuntimeError("live drill quarantine claim failed") from error

    claimed_stat = _vault_stat(
        quarantine, "claimed live drill quarantine is absent or unsafe"
    )
    if not _identity_matches(claimed_stat, state):
        state["phase"] = "cleanup-refused"
        state["cleanup_error"] = "claimed vault identity changed"
        state["claimed_st_dev"] = claimed_stat.st_dev
        state["claimed_st_ino"] = claimed_stat.st_ino
        _write_state(config, state)
        raise RuntimeError(f"claimed vault identity changed; preserved at {quarantine}")
    try:
        shutil.rmtree(quarantine)
    except OSError as error:
        detail = str(error) or type(error).__name__
        state["cleanup_error"] = f"quarantine removal failed: {detail}"
        _write_state(config, state)
        raise RuntimeError(
            f"quarantined live drill vault retained at {quarantine}"
        ) from error
    try:
        container.rmdir()
    except OSError as error:
        state["quarantine_container_cleanup_error"] = str(error) or type(error).__name__
    state["phase"] = "cleanup-confirmed"
    state.pop("cleanup_error", None)
    _write_state(config, state)


def _confirm_and_remove(config, environ, *, confirmed_at=None) -> None:
    if environ.get(CONFIRMED_ENV) != "1":
        raise LiveDrillConsentError(
            f"set {CONFIRMED_ENV}=1 only after removing the exact target in BBT Preferences"
        )
    state = _load_state(config)
    if state.get("phase") not in {
        "prepared",
        "manual-removal-check-required",
        "manual-removal-required",
        "cleanup-confirmed-removal-pending",
    }:
        raise RuntimeError(f"live drill state cannot be cleaned: {state.get('phase')}")
    if state["phase"] == "cleanup-confirmed-removal-pending":
        _finish_quarantined_cleanup(config, state)
        return
    vault_stat = _vault_stat(
        config.vault, "recorded live drill vault is absent or unsafe"
    )
    if not _identity_matches(vault_stat, state):
        raise RuntimeError("recorded live drill vault identity changed")
    stamp = confirmed_at
    if stamp is None:
        stamp = (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )
    if not _valid_utc_z_timestamp(stamp):
        raise RuntimeError("live drill recovery state has invalid schema-1 phase shape")
    # A random mode-0700 sibling is sufficient for this repository's solo-local,
    # trusted-same-UID model; hostile same-UID swaps are intentionally out of scope.
    container = Path(
        tempfile.mkdtemp(
            dir=config.vault.parent,
            prefix=f".{config.vault.name}.cleanup-",
        )
    )
    quarantine = container / "vault"
    state = {key: state[key] for key in BASE_STATE_KEYS}
    state.update(
        {
            "phase": "cleanup-confirmed-removal-pending",
            "human_removal_confirmed_at": stamp,
            "quarantine_container": str(container),
            "quarantine": str(quarantine),
        }
    )
    try:
        _write_state(config, state)
    except StateDurabilityError as error:
        if error.installed:
            raise
        try:
            container.rmdir()
        except OSError as cleanup_error:
            raise RuntimeError(
                f"unpersisted live drill quarantine retained at {container}"
            ) from cleanup_error
        raise
    except BaseException:
        try:
            container.rmdir()
        except OSError as cleanup_error:
            raise RuntimeError(
                f"unpersisted live drill quarantine retained at {container}"
            ) from cleanup_error
        raise
    _finish_quarantined_cleanup(config, state)


def _select_safe_citekey(client, vault) -> str:
    items = client.export_csl(None)
    candidates = sorted(
        item.get("id")
        for item in items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    )
    for citekey in candidates:
        try:
            notes.note_path(vault, citekey)
        except notes.InvalidCitekeyError:
            continue
        if any(
            isinstance(item, dict) and item.get("citekey") == citekey
            for item in client.search(citekey)
        ):
            return citekey
    raise RuntimeError("live library has no safely importable citekey")


def _prepare_live_vault(config) -> None:
    if config.vault.exists():
        if (
            not config.vault.is_dir()
            or config.vault.is_symlink()
            or any(config.vault.iterdir())
        ):
            raise RuntimeError("live drill vault is not the owned empty directory")
    else:
        config.vault.mkdir(mode=0o700)
    subprocess.run(
        ["git", "init", "-q"],
        cwd=config.vault,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "--local", "user.name", "knowledge-harness-live-drill"],
        cwd=config.vault,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "--local", "user.email", "live-drill@example.invalid"],
        cwd=config.vault,
        check=True,
        capture_output=True,
        text=True,
    )


def _live_config_or_skip(environ):
    try:
        return _drill_config(environ)
    except LiveDrillConsentError as error:
        pytest.skip(str(error))


def _cleanup_instruction(config, state=None) -> str:
    if state is None:
        state = _load_state(config)
    if state["phase"] == "cleanup-confirmed":
        raise RuntimeError("live drill cleanup is already complete")
    if state["phase"] == "cleanup-refused":
        raise RuntimeError("live drill cleanup was refused; inspect the recovery state")
    if state["phase"] == "cleanup-confirmed-removal-pending":
        return (
            "cleanup retry required for retained recovery state; run `"
            f"HARNESS_LIVE=1 {VAULT_ENV}={shlex.quote(str(config.vault))} "
            f"{CONFIRMED_ENV}=1 python -m pytest tests/test_scaffold_live.py -v`"
        )
    return (
        "manual cleanup required: remove the exact auto-export target "
        f"{state['host_target']!r} in BBT Preferences, retain {config.vault}, then "
        "run `"
        f"HARNESS_LIVE=1 {VAULT_ENV}={shlex.quote(str(config.vault))} "
        f"{CONFIRMED_ENV}=1 python -m pytest tests/test_scaffold_live.py -v`; "
        f"{CREATE_ENV} is not needed for cleanup"
    )


def _completed_drill(tmp_path, name):
    vault = tmp_path / name
    config = _drill_config({CREATE_ENV: "1", VAULT_ENV: str(vault)})
    target = vault / "x" / "bibliography.json"

    def completed_operation():
        target.parent.mkdir(parents=True)
        target.write_text("[]")

    _run_retaining_state(
        config,
        target=target,
        host_target=OFFLINE_HOST_TARGET,
        operation=completed_operation,
    )
    return config, target


def _pin_offline_host_target(monkeypatch, target):
    def translate(path):
        assert Path(path).absolute() == target
        return OFFLINE_HOST_TARGET

    monkeypatch.setattr(paths, "to_bbt_host", translate)


def test_live_drill_requires_separate_creation_consent(tmp_path):
    vault = tmp_path / "knowledge-harness-live-consent"

    with pytest.raises(LiveDrillConsentError, match=CREATE_ENV):
        _drill_config({VAULT_ENV: str(vault)})


def test_live_drill_requires_an_explicit_absolute_temporary_vault(tmp_path):
    with pytest.raises(LiveDrillConsentError, match=VAULT_ENV):
        _drill_config({CREATE_ENV: "1", VAULT_ENV: "relative-vault"})

    vault = tmp_path / "knowledge-harness-live-explicit"
    config = _drill_config({CREATE_ENV: "1", VAULT_ENV: str(vault)})

    assert config.vault == vault
    assert config.state == vault.with_name(f".{vault.name}.state.json")


@pytest.mark.parametrize("artifact", ["directory", "dangling-symlink"])
def test_live_drill_config_refuses_nonregular_state_artifacts(tmp_path, artifact):
    vault = tmp_path / f"knowledge-harness-live-state-{artifact}"
    state = vault.with_name(f".{vault.name}.state.json")
    if artifact == "directory":
        state.mkdir()
    else:
        state.symlink_to(tmp_path / "missing-state.json")

    with pytest.raises(LiveDrillConsentError, match="regular non-symlink"):
        _drill_config({CREATE_ENV: "1", VAULT_ENV: str(vault)})

    assert not vault.exists()


def test_state_artifact_created_after_config_is_not_overwritten(tmp_path):
    vault = tmp_path / "knowledge-harness-live-state-race"
    config = _drill_config({CREATE_ENV: "1", VAULT_ENV: str(vault)})
    missing = tmp_path / "missing-state.json"
    config.state.symlink_to(missing)
    operation_calls = []

    with pytest.raises(RuntimeError, match="regular non-symlink"):
        _run_retaining_state(
            config,
            target=vault / "x" / "bibliography.json",
            host_target=OFFLINE_HOST_TARGET,
            operation=lambda: operation_calls.append("called"),
        )

    assert operation_calls == []
    assert not vault.exists()
    assert config.state.is_symlink()
    assert not config.state.exists()


def test_live_drill_creates_a_persistent_temp_vault_when_path_is_omitted(
    tmp_path, monkeypatch, capsys
):
    real_mkdtemp = tempfile.mkdtemp

    def under_test_tmp(**kwargs):
        return real_mkdtemp(dir=tmp_path, **kwargs)

    monkeypatch.setattr(tempfile, "mkdtemp", under_test_tmp)

    config = _drill_config({CREATE_ENV: "1"})
    assert f"{VAULT_ENV}={shlex.quote(str(config.vault))}" in capsys.readouterr().out
    target = config.vault / "x" / "bibliography.json"

    def completed_operation():
        target.parent.mkdir(parents=True)
        target.write_text("[]")

    _run_retaining_state(
        config,
        target=target,
        host_target=r"C:\live\x\bibliography.json",
        operation=completed_operation,
    )

    assert config.vault.is_dir()
    assert config.vault.name.startswith("knowledge-harness-live-")
    assert config.precreated is True


def test_existing_recovery_state_enters_cleanup_without_creation_consent(tmp_path):
    vault = tmp_path / "knowledge-harness-live-existing"
    initial = _drill_config({CREATE_ENV: "1", VAULT_ENV: str(vault)})
    target = vault / "x" / "bibliography.json"

    def completed_operation():
        target.parent.mkdir(parents=True)
        target.write_text("[]")

    _run_retaining_state(
        initial,
        target=target,
        host_target=r"C:\live\x\bibliography.json",
        operation=completed_operation,
    )

    resumed = _drill_config({VAULT_ENV: str(vault)})

    assert resumed.vault == initial.vault
    assert resumed.state == initial.state


def test_live_vault_uses_hermetic_synthetic_git_identity(tmp_path):
    vault = tmp_path / "knowledge-harness-live-identity"
    config = _drill_config({CREATE_ENV: "1", VAULT_ENV: str(vault)})

    _prepare_live_vault(config)
    scaffold.scaffold_vault(vault)

    identity = subprocess.run(
        ["git", "log", "-1", "--format=%an <%ae>"],
        cwd=vault,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert identity == "knowledge-harness-live-drill <live-drill@example.invalid>"


def test_failed_creation_phase_retains_exact_vault_and_recovery_state(tmp_path):
    vault = tmp_path / "knowledge-harness-live-recovery"
    config = _drill_config({CREATE_ENV: "1", VAULT_ENV: str(vault)})
    target = vault / "x" / "bibliography.json"

    def interrupted_operation():
        (vault / "evidence.txt").write_text("retain me")
        raise RuntimeError("doctor interrupted")

    with pytest.raises(RuntimeError, match="doctor interrupted"):
        _run_retaining_state(
            config,
            target=target,
            host_target=r"C:\live\x\bibliography.json",
            operation=interrupted_operation,
        )

    state = json.loads(config.state.read_text())
    assert (vault / "evidence.txt").read_text() == "retain me"
    assert state["phase"] == "manual-removal-check-required"
    assert state["vault"] == str(vault)
    assert type(state["st_dev"]) is int
    assert type(state["st_ino"]) is int
    assert state["target"] == str(target)
    assert state["host_target"] == r"C:\live\x\bibliography.json"


def test_recovery_state_write_preserves_unrelated_sibling_temp_file(tmp_path):
    vault = tmp_path / "knowledge-harness-live-state-write"
    config = _drill_config({CREATE_ENV: "1", VAULT_ENV: str(vault)})
    target = vault / "x" / "bibliography.json"
    unrelated = config.state.with_name(f".{config.state.name}.tmp")
    unrelated.write_text("unrelated")

    def completed_operation():
        target.parent.mkdir(parents=True)
        target.write_text("[]")

    _run_retaining_state(
        config,
        target=target,
        host_target=r"C:\live\x\bibliography.json",
        operation=completed_operation,
    )

    assert unrelated.read_text() == "unrelated"


def test_parent_directory_fsync_failure_stops_before_live_operation(
    tmp_path, monkeypatch
):
    vault = tmp_path / "knowledge-harness-live-state-durability"
    config = _drill_config({CREATE_ENV: "1", VAULT_ENV: str(vault)})
    target = vault / "x" / "bibliography.json"
    real_fsync = os.fsync
    operation_calls = []

    def fail_directory_fsync(descriptor):
        if stat.S_ISDIR(os.fstat(descriptor).st_mode):
            raise OSError("directory fsync unavailable")
        return real_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", fail_directory_fsync)

    with pytest.raises(OSError, match="directory fsync unavailable"):
        _run_retaining_state(
            config,
            target=target,
            host_target=OFFLINE_HOST_TARGET,
            operation=lambda: operation_calls.append("called"),
        )

    assert operation_calls == []
    assert json.loads(config.state.read_text())["phase"] == "prepared"


def test_recovery_assignment_prints_before_the_live_operation(tmp_path, capsys):
    vault = tmp_path / "knowledge-harness-live-recovery-output"
    config = _drill_config({CREATE_ENV: "1", VAULT_ENV: str(vault)})
    target = vault / "x" / "bibliography.json"

    def observe_output_before_operation():
        assert f"{VAULT_ENV}={shlex.quote(str(vault))}" in capsys.readouterr().out
        target.parent.mkdir(parents=True)
        target.write_text("[]")

    _run_retaining_state(
        config,
        target=target,
        host_target=r"C:\live\x\bibliography.json",
        operation=observe_output_before_operation,
    )


def test_one_translation_value_drives_recovery_state_and_autoexport_rpc(
    tmp_path, monkeypatch
):
    vault = tmp_path / "knowledge-harness-live-pinned-target"
    config = _drill_config({CREATE_ENV: "1", VAULT_ENV: str(vault)})
    target = vault / "x" / "bibliography.json"
    real_translation_calls = []

    def translate_once(path):
        real_translation_calls.append(Path(path).absolute())
        return OFFLINE_HOST_TARGET

    monkeypatch.setattr(paths, "to_bbt_host", translate_once)
    host_target = paths.to_bbt_host(target)

    def pinned_translation(path):
        assert Path(path).absolute() == target
        return host_target

    monkeypatch.setattr(paths, "to_bbt_host", pinned_translation)
    client = ZoteroClient()
    rpc_calls = []

    def rpc(method, params):
        rpc_calls.append((method, params))
        return {"id": 7}

    monkeypatch.setattr(client, "_rpc", rpc)

    def register():
        target.parent.mkdir(parents=True)
        target.write_text("[]")
        client.register_autoexport(str(target))

    _run_retaining_state(
        config,
        target=target,
        host_target=host_target,
        operation=register,
    )

    state = json.loads(config.state.read_text())
    assert real_translation_calls == [target]
    assert state["host_target"] == OFFLINE_HOST_TARGET
    assert rpc_calls == [
        ("autoexport.add", ["//", "Better CSL JSON", OFFLINE_HOST_TARGET])
    ]


def test_implicit_vault_is_printed_and_retained_when_host_translation_fails(
    tmp_path, monkeypatch, capsys
):
    real_mkdtemp = tempfile.mkdtemp
    generated = []

    def under_test_tmp(**kwargs):
        vault = Path(real_mkdtemp(dir=tmp_path, **kwargs))
        generated.append(vault)
        return str(vault)

    def translation_failure(path):
        raise paths.PathError(f"cannot translate {path}")

    def forbidden(*args, **kwargs):
        raise AssertionError("translation failure reached Git or BBT")

    monkeypatch.setattr(tempfile, "mkdtemp", under_test_tmp)
    monkeypatch.setattr(paths, "to_bbt_host", translation_failure)
    monkeypatch.setattr(scaffold, "scaffold_vault", forbidden)
    monkeypatch.setenv(CREATE_ENV, "1")
    monkeypatch.delenv(VAULT_ENV, raising=False)
    monkeypatch.delenv(CONFIRMED_ENV, raising=False)

    with pytest.raises(paths.PathError, match="cannot translate"):
        test_live_scaffold_doctor_import_noop_with_manual_cleanup(monkeypatch)

    vault = generated[0]
    assert f"{VAULT_ENV}={shlex.quote(str(vault))}" in capsys.readouterr().out
    assert vault.is_dir()
    assert list(vault.iterdir()) == []
    assert not vault.with_name(f".{vault.name}.state.json").exists()


def test_confirmed_cleanup_removes_only_recorded_vault_and_retains_audit_state(
    tmp_path, monkeypatch
):
    sibling = tmp_path / "unrelated"
    sibling.mkdir()
    (sibling / "keep.txt").write_text("untouched")
    config, target = _completed_drill(tmp_path, "knowledge-harness-live-cleanup")
    _pin_offline_host_target(monkeypatch, target)
    resumed = _drill_config({VAULT_ENV: str(config.vault)})
    _confirm_and_remove(
        resumed,
        {CONFIRMED_ENV: "1"},
        confirmed_at="2026-08-20T21:00:00Z",
    )

    state = json.loads(config.state.read_text())
    assert not config.vault.exists()
    assert (sibling / "keep.txt").read_text() == "untouched"
    assert state["phase"] == "cleanup-confirmed"
    assert state["human_removal_confirmed_at"] == "2026-08-20T21:00:00Z"


def test_cleanup_discards_an_unpersisted_empty_quarantine_container(
    tmp_path, monkeypatch
):
    config, target = _completed_drill(
        tmp_path, "knowledge-harness-live-unpersisted-quarantine"
    )
    _pin_offline_host_target(monkeypatch, target)
    real_write_state = _write_state
    unpersisted = []

    def fail_pending_state(path, state):
        if state.get("phase") == "cleanup-confirmed-removal-pending":
            unpersisted.append(Path(state["quarantine_container"]))
            raise OSError("state write unavailable")
        return real_write_state(path, state)

    monkeypatch.setitem(
        _confirm_and_remove.__globals__, "_write_state", fail_pending_state
    )

    with pytest.raises(OSError, match="state write unavailable"):
        _confirm_and_remove(config, {CONFIRMED_ENV: "1"})

    assert len(unpersisted) == 1
    assert not unpersisted[0].exists()
    assert target.is_file()
    assert json.loads(config.state.read_text())["phase"] == "manual-removal-required"


def test_invalid_confirmation_timestamp_precedes_quarantine_creation(
    tmp_path, monkeypatch
):
    config, target = _completed_drill(
        tmp_path, "knowledge-harness-live-invalid-confirmation-time"
    )
    _pin_offline_host_target(monkeypatch, target)

    def forbidden_quarantine(*args, **kwargs):
        raise AssertionError("invalid timestamp reached quarantine creation")

    monkeypatch.setattr(tempfile, "mkdtemp", forbidden_quarantine)

    with pytest.raises(RuntimeError, match="schema-1 phase shape"):
        _confirm_and_remove(
            config,
            {CONFIRMED_ENV: "1"},
            confirmed_at="invalid",
        )

    assert target.is_file()


def test_pending_state_directory_fsync_failure_precedes_quarantine_claim(
    tmp_path, monkeypatch
):
    config, target = _completed_drill(
        tmp_path, "knowledge-harness-live-pending-durability"
    )
    _pin_offline_host_target(monkeypatch, target)
    real_fsync = os.fsync
    rename_calls = []

    def fail_directory_fsync(descriptor):
        if stat.S_ISDIR(os.fstat(descriptor).st_mode):
            raise OSError("directory fsync unavailable")
        return real_fsync(descriptor)

    def forbidden_rename(source, destination):
        rename_calls.append((source, destination))
        raise AssertionError("cleanup claimed the vault before state durability")

    monkeypatch.setattr(os, "fsync", fail_directory_fsync)
    monkeypatch.setattr(os, "rename", forbidden_rename)

    with pytest.raises(OSError, match="directory fsync unavailable"):
        _confirm_and_remove(config, {CONFIRMED_ENV: "1"})

    assert rename_calls == []
    assert target.is_file()
    assert json.loads(config.state.read_text())["phase"] == "manual-removal-required"
    assert list(config.vault.parent.glob(f".{config.vault.name}.cleanup-*")) == []


def test_confirmed_cleanup_refuses_a_replacement_at_the_recorded_path(
    tmp_path, monkeypatch
):
    displaced = tmp_path / "original-live-vault"
    config, target = _completed_drill(tmp_path, "knowledge-harness-live-replaced")
    vault = config.vault
    _pin_offline_host_target(monkeypatch, target)
    vault.rename(displaced)
    vault.mkdir()
    (vault / "replacement.txt").write_text("must survive")

    def forbidden_removal(path):
        raise AssertionError(f"replacement reached deletion: {path}")

    monkeypatch.setattr(shutil, "rmtree", forbidden_removal)

    with pytest.raises(RuntimeError, match="identity changed"):
        _confirm_and_remove(config, {CONFIRMED_ENV: "1"})

    assert (vault / "replacement.txt").read_text() == "must survive"
    assert (displaced / "x" / "bibliography.json").is_file()


def test_cleanup_claim_revalidates_and_preserves_a_racing_successor(
    tmp_path, monkeypatch
):
    displaced = tmp_path / "original-live-vault"
    successor = tmp_path / "successor-live-vault"
    successor.mkdir()
    (successor / "successor.txt").write_text("must survive")
    config, target = _completed_drill(tmp_path, "knowledge-harness-live-racing-cleanup")
    vault = config.vault
    _pin_offline_host_target(monkeypatch, target)
    real_rename = os.rename
    real_rmtree = shutil.rmtree
    swapped = False
    removal_calls = []

    def swap_once():
        nonlocal swapped
        if swapped:
            return
        swapped = True
        real_rename(vault, displaced)
        real_rename(successor, vault)

    def racing_rename(source, destination):
        if Path(source) == vault:
            swap_once()
        return real_rename(source, destination)

    def racing_rmtree(path):
        removal_calls.append(Path(path))
        if Path(path) == vault:
            swap_once()
        return real_rmtree(path)

    monkeypatch.setattr(os, "rename", racing_rename)
    monkeypatch.setattr(shutil, "rmtree", racing_rmtree)

    with pytest.raises(RuntimeError, match="claimed vault identity changed"):
        _confirm_and_remove(config, {CONFIRMED_ENV: "1"})

    state = json.loads(config.state.read_text())
    quarantine = Path(state["quarantine"])
    assert removal_calls == []
    assert state["phase"] == "cleanup-refused"
    assert state["cleanup_error"] == "claimed vault identity changed"
    assert (quarantine / "successor.txt").read_text() == "must survive"
    assert (displaced / "x" / "bibliography.json").is_file()


def test_cleanup_resumes_a_matching_private_quarantine_after_rmtree_failure(
    tmp_path, monkeypatch
):
    config, target = _completed_drill(tmp_path, "knowledge-harness-live-cleanup-retry")
    vault = config.vault
    _pin_offline_host_target(monkeypatch, target)
    real_rmtree = shutil.rmtree
    attempts = 0

    def fail_once(path):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise OSError("transient removal failure")
        return real_rmtree(path)

    monkeypatch.setattr(shutil, "rmtree", fail_once)

    with pytest.raises(RuntimeError, match="retained"):
        _confirm_and_remove(config, {CONFIRMED_ENV: "1"})

    pending = json.loads(config.state.read_text())
    quarantine = Path(pending["quarantine"])
    container = quarantine.parent
    assert pending["phase"] == "cleanup-confirmed-removal-pending"
    assert quarantine.name == "vault"
    assert container.parent == vault.parent
    assert stat.S_IMODE(os.lstat(container).st_mode) == 0o700
    assert (quarantine / "x" / "bibliography.json").is_file()

    resumed = _drill_config({VAULT_ENV: str(vault)})
    _confirm_and_remove(resumed, {CONFIRMED_ENV: "1"})

    complete = json.loads(config.state.read_text())
    assert attempts == 2
    assert complete["phase"] == "cleanup-confirmed"
    assert not quarantine.exists()
    assert not container.exists()


def test_cleanup_refuses_to_infer_removal_after_final_state_write_failure(
    tmp_path, monkeypatch
):
    config, target = _completed_drill(
        tmp_path, "knowledge-harness-live-ambiguous-removal"
    )
    _pin_offline_host_target(monkeypatch, target)
    real_write_state = _write_state

    def fail_completed_state(path, state):
        if state.get("phase") == "cleanup-confirmed":
            raise OSError("final state write unavailable")
        return real_write_state(path, state)

    monkeypatch.setitem(
        _confirm_and_remove.__globals__, "_write_state", fail_completed_state
    )

    with pytest.raises(OSError, match="final state write unavailable"):
        _confirm_and_remove(config, {CONFIRMED_ENV: "1"})

    monkeypatch.setitem(
        _confirm_and_remove.__globals__, "_write_state", real_write_state
    )
    config.vault.mkdir()
    (config.vault / "successor.txt").write_text("must survive")

    with pytest.raises(RuntimeError, match="cannot be reconciled"):
        _confirm_and_remove(config, {CONFIRMED_ENV: "1"})

    assert (config.vault / "successor.txt").read_text() == "must survive"
    assert (
        json.loads(config.state.read_text())["phase"]
        == "cleanup-confirmed-removal-pending"
    )


def test_final_directory_fsync_failure_retains_pending_fail_closed_state(
    tmp_path, monkeypatch
):
    config, target = _completed_drill(
        tmp_path, "knowledge-harness-live-final-durability"
    )
    _pin_offline_host_target(monkeypatch, target)
    real_fsync = os.fsync
    directory_fsyncs = 0

    def fail_second_directory_fsync(descriptor):
        nonlocal directory_fsyncs
        if stat.S_ISDIR(os.fstat(descriptor).st_mode):
            directory_fsyncs += 1
            if directory_fsyncs == 2:
                raise OSError("final directory fsync unavailable")
        return real_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", fail_second_directory_fsync)

    with pytest.raises(OSError, match="final directory fsync unavailable"):
        _confirm_and_remove(config, {CONFIRMED_ENV: "1"})

    assert directory_fsyncs == 2
    assert json.loads(config.state.read_text())["phase"] == (
        "cleanup-confirmed-removal-pending"
    )
    assert not config.vault.exists()


def test_successor_created_after_quarantine_claim_survives_cleanup(
    tmp_path, monkeypatch
):
    config, target = _completed_drill(
        tmp_path, "knowledge-harness-live-postclaim-successor"
    )
    vault = config.vault
    _pin_offline_host_target(monkeypatch, target)
    real_rmtree = shutil.rmtree

    def create_successor_then_remove(path):
        vault.mkdir()
        (vault / "successor.txt").write_text("must survive")
        return real_rmtree(path)

    monkeypatch.setattr(shutil, "rmtree", create_successor_then_remove)

    _confirm_and_remove(config, {CONFIRMED_ENV: "1"})

    assert (vault / "successor.txt").read_text() == "must survive"
    state = json.loads(config.state.read_text())
    assert state["phase"] == "cleanup-confirmed"


def test_confirmed_cleanup_refuses_a_symlink_successor(tmp_path, monkeypatch):
    displaced = tmp_path / "original-live-vault"
    config, target = _completed_drill(tmp_path, "knowledge-harness-live-symlink")
    vault = config.vault
    _pin_offline_host_target(monkeypatch, target)
    vault.rename(displaced)
    vault.symlink_to(displaced, target_is_directory=True)

    with pytest.raises(RuntimeError, match="absent or unsafe"):
        _confirm_and_remove(config, {CONFIRMED_ENV: "1"})

    assert vault.is_symlink()
    assert (displaced / "x" / "bibliography.json").is_file()


@pytest.mark.parametrize("payload", ["{", "{}"])
def test_confirmed_cleanup_refuses_corrupt_or_mismatched_state(tmp_path, payload):
    vault = tmp_path / "knowledge-harness-live-corrupt-state"
    vault.mkdir()
    (vault / "keep.txt").write_text("keep")
    state = vault.with_name(f".{vault.name}.state.json")
    state.write_text(payload)
    config = _drill_config({VAULT_ENV: str(vault)})

    with pytest.raises(RuntimeError, match="recovery state"):
        _confirm_and_remove(config, {CONFIRMED_ENV: "1"})

    assert (vault / "keep.txt").read_text() == "keep"


def test_symlinked_recovery_state_cannot_authorize_cleanup(tmp_path, monkeypatch):
    config, target = _completed_drill(
        tmp_path, "knowledge-harness-live-symlinked-state"
    )
    backing = tmp_path / "backing-state.json"
    config.state.rename(backing)
    config.state.symlink_to(backing)
    _pin_offline_host_target(monkeypatch, target)

    def forbidden_mutation(*args, **kwargs):
        raise AssertionError("symlinked state authorized cleanup mutation")

    monkeypatch.setattr(tempfile, "mkdtemp", forbidden_mutation)

    with pytest.raises(RuntimeError, match="regular non-symlink"):
        _confirm_and_remove(config, {CONFIRMED_ENV: "1"})

    assert target.is_file()
    assert config.state.is_symlink()
    assert backing.is_file()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema", True),
        ("phase", []),
        ("host_target", ""),
        ("host_target", r"C:\wrong"),
    ],
)
def test_recovery_instruction_rejects_noncanonical_state(
    tmp_path, monkeypatch, field, value
):
    config, target = _completed_drill(
        tmp_path,
        f"knowledge-harness-live-state-{field}-{value!s}".replace("\\", "-"),
    )
    state = json.loads(config.state.read_text())
    state[field] = value
    config.state.write_text(json.dumps(state))
    _pin_offline_host_target(monkeypatch, target)

    with pytest.raises(RuntimeError, match="recovery state"):
        _cleanup_instruction(config)

    assert target.is_file()


def test_recovery_instruction_fails_closed_when_host_target_cannot_be_recomputed(
    tmp_path, monkeypatch
):
    vault = tmp_path / "knowledge-harness-live-state-translation"
    config = _drill_config({CREATE_ENV: "1", VAULT_ENV: str(vault)})
    target = vault / "x" / "bibliography.json"

    def completed_operation():
        target.parent.mkdir(parents=True)
        target.write_text("[]")

    _run_retaining_state(
        config,
        target=target,
        host_target=r"C:\live\x\bibliography.json",
        operation=completed_operation,
    )

    def unavailable(path):
        raise paths.PathError(f"cannot translate {path}")

    monkeypatch.setattr(paths, "to_bbt_host", unavailable)

    with pytest.raises(RuntimeError, match="host target"):
        _cleanup_instruction(config)

    assert target.is_file()


@pytest.mark.parametrize(
    "defect",
    [
        "pending-missing-timestamp",
        "pending-invalid-timestamp",
        "pending-unexpected-field",
        "pending-relative-container",
        "manual-check-empty-interruption",
        "manual-required-stale-interruption",
        "refused-missing-claimed-inode",
        "confirmed-stale-cleanup-error",
    ],
)
def test_recovery_rejects_invalid_schema_one_phase_shapes(
    tmp_path, monkeypatch, defect
):
    config, target = _completed_drill(
        tmp_path, f"knowledge-harness-live-schema-{defect}"
    )
    state = json.loads(config.state.read_text())
    container = config.vault.with_name(f".{config.vault.name}.cleanup-fixed")
    state.update(
        {
            "phase": "cleanup-confirmed-removal-pending",
            "human_removal_confirmed_at": "2026-08-20T21:00:00Z",
            "quarantine_container": str(container),
            "quarantine": str(container / "vault"),
        }
    )
    if defect == "pending-missing-timestamp":
        state.pop("human_removal_confirmed_at")
    elif defect == "pending-invalid-timestamp":
        state["human_removal_confirmed_at"] = "2026-08-20"
    elif defect == "pending-unexpected-field":
        state["unexpected"] = "stale"
    elif defect == "pending-relative-container":
        state["quarantine_container"] = "relative-container"
        state["quarantine"] = "relative-container/vault"
    elif defect == "manual-check-empty-interruption":
        state = {
            key: value
            for key, value in state.items()
            if key
            not in {
                "human_removal_confirmed_at",
                "quarantine_container",
                "quarantine",
            }
        }
        state["phase"] = "manual-removal-check-required"
        state["interruption"] = ""
    elif defect == "manual-required-stale-interruption":
        state = {
            key: value
            for key, value in state.items()
            if key
            not in {
                "human_removal_confirmed_at",
                "quarantine_container",
                "quarantine",
            }
        }
        state["phase"] = "manual-removal-required"
        state["interruption"] = "RuntimeError"
    elif defect == "refused-missing-claimed-inode":
        state["phase"] = "cleanup-refused"
        state["cleanup_error"] = "claimed vault identity changed"
        state["claimed_st_dev"] = 1
    elif defect == "confirmed-stale-cleanup-error":
        state["phase"] = "cleanup-confirmed"
        state["cleanup_error"] = "stale failure"
    config.state.write_text(json.dumps(state))
    _pin_offline_host_target(monkeypatch, target)

    with pytest.raises(RuntimeError, match="schema-1 phase shape"):
        _load_state(config)

    assert target.is_file()


def test_state_writer_validates_phase_shape_before_temp_creation(tmp_path, monkeypatch):
    config, target = _completed_drill(
        tmp_path, "knowledge-harness-live-write-validation"
    )
    state = json.loads(config.state.read_text())
    state["unexpected"] = "stale"

    def forbidden_temp(*args, **kwargs):
        raise AssertionError("invalid state reached temporary-file creation")

    monkeypatch.setattr(tempfile, "mkstemp", forbidden_temp)

    with pytest.raises(RuntimeError, match="schema-1 phase shape"):
        _write_state(config, state)

    assert target.is_file()
    assert "unexpected" not in json.loads(config.state.read_text())


def test_completed_cleanup_state_produces_no_new_removal_instruction(
    tmp_path, monkeypatch
):
    config, target = _completed_drill(
        tmp_path, "knowledge-harness-live-completed-instruction"
    )
    _pin_offline_host_target(monkeypatch, target)
    _confirm_and_remove(
        config,
        {CONFIRMED_ENV: "1"},
        confirmed_at="2026-08-20T21:00:00Z",
    )

    with pytest.raises(RuntimeError, match="already complete"):
        _cleanup_instruction(config)


def test_completed_cleanup_state_is_terminal_in_live_dispatch(tmp_path, monkeypatch):
    config, target = _completed_drill(
        tmp_path, "knowledge-harness-live-completed-dispatch"
    )
    _pin_offline_host_target(monkeypatch, target)
    _confirm_and_remove(
        config,
        {CONFIRMED_ENV: "1"},
        confirmed_at="2026-08-20T21:00:00Z",
    )
    monkeypatch.setenv(VAULT_ENV, str(config.vault))
    monkeypatch.delenv(CREATE_ENV, raising=False)
    monkeypatch.delenv(CONFIRMED_ENV, raising=False)

    assert (
        test_live_scaffold_doctor_import_noop_with_manual_cleanup(monkeypatch) is None
    )


def test_safe_item_choice_skips_unsafe_and_unresolvable_citekeys(tmp_path):
    class Library:
        def export_csl(self, citekeys):
            assert citekeys is None
            return [
                {"id": "../escape", "title": "unsafe"},
                {"id": "missing2026", "title": "not searchable"},
                {"id": "usable2026", "title": "safe"},
            ]

        def search(self, citekey):
            if citekey == "usable2026":
                return [{"citekey": "usable2026", "title": "safe"}]
            return []

    assert _select_safe_citekey(Library(), tmp_path) == "usable2026"
    assert notes.note_path(tmp_path, "usable2026").parent == tmp_path / "literatures"


def test_environment_records_live_observed_bbt_autoexport_surface():
    environment = (REPO / "docs" / "environment.md").read_text()

    assert (
        "| BBT auto-export JSON-RPC surface | BBT 9.0.55 JSON-RPC exposes "
        "`autoexport.add` only; `.list`/`.remove`/`.delete`/`.get` live-probed "
        "`-32601 METHOD_NOT_FOUND`. | 2026-08-20 |"
    ) in environment


def test_pending_cleanup_never_contacts_bbt_or_creates_another_vault(
    tmp_path, monkeypatch
):
    initial, target = _completed_drill(tmp_path, "knowledge-harness-live-pending")
    monkeypatch.setenv(VAULT_ENV, str(initial.vault))
    monkeypatch.delenv(CREATE_ENV, raising=False)
    monkeypatch.delenv(CONFIRMED_ENV, raising=False)

    def forbidden(*args, **kwargs):
        raise AssertionError("cleanup phase contacted BBT or created another vault")

    _pin_offline_host_target(monkeypatch, target)
    monkeypatch.setattr(tempfile, "mkdtemp", forbidden)

    with pytest.raises(
        pytest.skip.Exception, match="manual cleanup required"
    ) as skipped:
        test_live_scaffold_doctor_import_noop_with_manual_cleanup(monkeypatch)

    instruction = str(skipped.value)
    assert "HARNESS_LIVE=1" in instruction
    assert f"{VAULT_ENV}={shlex.quote(str(initial.vault))}" in instruction
    assert f"{CONFIRMED_ENV}=1" in instruction
    assert "python -m pytest tests/test_scaffold_live.py -v" in instruction


@pytest.mark.live
def test_live_scaffold_doctor_import_noop_with_manual_cleanup(monkeypatch):
    config = _live_config_or_skip(os.environ)
    if _state_artifact_stat(config.state) is not None:
        if os.environ.get(CONFIRMED_ENV) == "1":
            _confirm_and_remove(config, os.environ)
            return
        state = _load_state(config)
        if state["phase"] == "cleanup-confirmed":
            return
        pytest.skip(_cleanup_instruction(config, state))

    target = config.vault / "x" / "bibliography.json"
    host_target = paths.to_bbt_host(target)

    def pinned_host_target(path):
        if Path(path).absolute() != target:
            raise AssertionError("observer translated a different local target")
        return host_target

    monkeypatch.setattr(paths, "to_bbt_host", pinned_host_target)

    def exercise():
        _prepare_live_vault(config)
        scaffold.scaffold_vault(config.vault)
        machine = config.vault / ".harness" / "machine.json"
        machine.write_text(
            json.dumps(
                {
                    "mailto": "live-drill@example.invalid",
                    "zotero_backup": "temporary live drill; no evidence stored",
                }
            )
        )

        class RecordingClient(ZoteroClient):
            def __init__(self):
                super().__init__()
                self.rpc_methods = []

            def _rpc(self, method, params):
                self.rpc_methods.append(method)
                return super()._rpc(method, params)

        client = RecordingClient()
        citekey = _select_safe_citekey(client, config.vault)
        probes = {probe.name: probe for probe in scaffold.doctor(config.vault, client)}
        assert probes["autoexport"].result is Result.MATCHED
        assert probes["staleness"].result is Result.MATCHED
        assert target.is_file()

        monkeypatch.setattr(cli, "ZoteroClient", lambda base: client)
        arguments = argparse.Namespace(
            citekey=citekey,
            vault=str(config.vault),
            base="http://localhost:23119",
        )
        with contextlib.redirect_stdout(io.StringIO()) as imported_output:
            assert cli.cmd_import_note(arguments) == 0
        note = notes.note_path(config.vault, citekey)
        assert note.is_file()
        bibliography = json.loads(target.read_text())
        assert any(item.get("id") == citekey for item in bibliography)
        with contextlib.redirect_stdout(io.StringIO()) as rerun_output:
            assert cli.cmd_import_note(arguments) == 0
        assert rerun_output.getvalue().strip() == "NOOP"
        assert imported_output.getvalue().strip() == str(note)
        assert client.rpc_methods.count("autoexport.add") == 1
        assert not {
            "autoexport.list",
            "autoexport.remove",
            "autoexport.delete",
            "autoexport.get",
        }.intersection(client.rpc_methods)

    _run_retaining_state(
        config,
        target=target,
        host_target=host_target,
        operation=exercise,
    )
    pytest.skip(_cleanup_instruction(config))
