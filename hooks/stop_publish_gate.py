"""Bounded, explicitly armed Stop gate for publish verification."""

from __future__ import annotations

import datetime
import json
import os
import stat
import sys
import tempfile
from contextlib import suppress
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLAG_NAME = "publish-pending.json"
MAX_ACTIVE_BLOCKS = 8
FAIL_CLOSED_REASON = (
    "Publish verification unavailable; resolve the gate or use its audited bypass."
)
BOUND_MESSAGE = (
    "Publish gate reached the eight-block safety bound; the pending flag remains "
    "for human follow-up."
)


class FlagChangedError(RuntimeError):
    """The armed flag changed after this invocation read it."""


class ClaimRecoveryPendingError(RuntimeError):
    """A valid private claim could not yet be restored to the public path."""


class BypassFailureError(RuntimeError):
    """The audited bypass did not durably complete."""


class ArmedFlag:
    __slots__ = (
        "blocks",
        "bypass",
        "expected_bytes",
        "identity",
        "path",
        "project",
        "state",
        "vault",
    )

    def __init__(
        self,
        path: Path,
        vault: Path,
        project: str,
        blocks: int,
        bypass: str | None,
        state: dict[str, object],
        expected_bytes: bytes,
        identity: tuple[int, int],
    ) -> None:
        self.path = path
        self.vault = vault
        self.project = project
        self.blocks = blocks
        self.bypass = bypass
        self.state = state
        self.expected_bytes = expected_bytes
        self.identity = identity


class PublishState:
    __slots__ = ("effective", "raw", "warning_effective")

    def __init__(self, raw, effective, warning_effective) -> None:
        self.raw = raw
        self.effective = effective
        self.warning_effective = warning_effective


def _core_path() -> None:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))


def _verify_publish(vault: Path) -> PublishState:
    """Run the production network-capable verification transaction."""
    _core_path()
    from research_vault.verify import verify_state

    report, effective, _hashes, warning_effective = verify_state(
        vault,
        network=True,
    )
    return PublishState(
        tuple(report["outcomes"]),
        tuple(effective),
        warning_effective,
    )


def _publish_decision(state: PublishState) -> tuple[int, tuple[str, ...]]:
    _core_path()
    from research_vault.verify import surface_decision

    return surface_decision(
        "publish",
        state.effective,
        state.warning_effective,
    )


def _append_bypass(vault: Path, project: str, reason: str) -> None:
    """Record this bypass exactly once; a retry must not duplicate its finding."""
    _core_path()
    from research_vault import Result, inbox
    from research_vault.pathcodec import encode_repo_path

    target = encode_repo_path(os.fsencode(project))
    date = datetime.datetime.now(datetime.UTC).date().isoformat()
    recorded_reason = f"manual — publish-gate bypass: {reason}"
    # A publish-gate finding id carries a reason discriminator, so a retry of
    # THIS bypass collapses to one row while a genuinely distinct bypass of the
    # same project on the same day still records and stays acknowledgeable.
    for entry in inbox.load(vault):
        if (
            entry.ack_of is None
            and entry.check == "publish-gate"
            and entry.target == target
            and entry.date == date
            and entry.reason == recorded_reason
        ):
            return
    inbox.append_entry(
        vault,
        "publish-gate",
        target,
        Result.UNMATCHED,
        recorded_reason,
        actor="human:publish-bypass",
        date=date,
        target_kind="repo-path",
        durable=True,
    )


def _vault_from_cwd(cwd: str) -> Path | None:
    """Find the nearest real vault marker, including cwd itself."""
    if not Path(cwd).is_absolute() or "\0" in cwd:
        return None
    current = Path(os.path.sep)
    try:
        for component in cwd.split(os.path.sep)[1:]:
            if not component:
                continue
            if component in {".", ".."}:
                return None
            current /= component
            metadata = os.lstat(current)
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
                return None
        resolved = current.resolve(strict=True)
    except (OSError, RuntimeError):
        return None
    if resolved != current:
        return None
    current = resolved
    for candidate in (current, *current.parents):
        marker = candidate / ".research-vault"
        try:
            marker_stat = os.lstat(marker)
        except OSError:
            continue
        if stat.S_ISDIR(marker_stat.st_mode):
            return candidate
    return None


def _read_regular(path: Path) -> tuple[bytes, tuple[int, int]]:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError("flag is not a regular file")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            data = stream.read()
    finally:
        os.close(descriptor)
    return data, (metadata.st_dev, metadata.st_ino)


def _safe_project(vault: Path, project: object) -> str | None:
    if (
        type(project) is not str
        or not project
        or any(character in project for character in "\r\n\0")
    ):
        return None
    components = project.split("/")
    if (
        len(components) < 2
        or components[0] != "projects"
        or any(component in {"", ".", ".."} for component in components)
    ):
        return None
    current = vault
    for index, component in enumerate(components):
        current /= component
        try:
            metadata = os.lstat(current)
        except OSError:
            return None
        if stat.S_ISLNK(metadata.st_mode):
            return None
        if not stat.S_ISDIR(metadata.st_mode):
            return None
        if index == len(components) - 1:
            try:
                current.resolve(strict=True).relative_to(vault)
            except (OSError, RuntimeError, ValueError):
                return None
    return project


def _single_line(value: object) -> str | None:
    if (
        type(value) is not str
        or not value.strip()
        or any(character in value for character in "\r\n\0")
    ):
        return None
    return value.strip()


def _decode_flag(
    vault: Path,
    path: Path,
    encoded: bytes,
    identity: tuple[int, int],
) -> ArmedFlag | None:
    try:
        state = json.loads(encoded)
    except (UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        return None
    allowed = {"project", "vault", "blocks"}
    if not isinstance(state, dict):
        return None
    keys = set(state)
    if keys != allowed and keys != allowed | {"bypass"}:
        return None
    vault_value = state["vault"]
    if (
        type(vault_value) is not str
        or not Path(vault_value).is_absolute()
        or vault_value != str(vault)
    ):
        return None
    try:
        if Path(vault_value).resolve(strict=True) != vault:
            return None
    except (OSError, RuntimeError):
        return None
    project = _safe_project(vault, state["project"])
    blocks = state["blocks"]
    if project is None or type(blocks) is not int or blocks < 0:
        return None
    bypass = None
    if "bypass" in state:
        bypass = _single_line(state["bypass"])
        if bypass is None:
            return None
    return ArmedFlag(
        path,
        vault,
        project,
        blocks,
        bypass,
        state,
        encoded,
        identity,
    )


def _read_flag(vault: Path, path: Path) -> ArmedFlag | None:
    try:
        encoded, identity = _read_regular(path)
    except (OSError, ValueError):
        return None
    return _decode_flag(vault, path, encoded, identity)


def _unlink_owned(path: Path, identity: tuple[int, int]) -> None:
    metadata = os.lstat(path)
    if not stat.S_ISREG(metadata.st_mode):
        raise FlagChangedError("private flag artifact changed type")
    if (metadata.st_dev, metadata.st_ino) != identity:
        raise FlagChangedError("private flag artifact changed identity")
    path.unlink()


def _restore_owned_claim(
    vault: Path,
    claimed: Path,
    path: Path,
    expected_bytes: bytes,
    identity: tuple[int, int],
) -> None:
    current_bytes, current_identity = _read_regular(claimed)
    if current_identity != identity or current_bytes != expected_bytes:
        raise FlagChangedError("private flag claim changed before restore")
    try:
        os.link(claimed, path)
    except Exception as error:
        successor = _read_flag(vault, path)
        if successor is None:
            raise error
    installed_bytes, installed_identity = _read_regular(path)
    if installed_identity != identity or installed_bytes != expected_bytes:
        successor = _decode_flag(vault, path, installed_bytes, installed_identity)
        if successor is None:
            raise FlagChangedError("public flag is not a valid successor")
    _unlink_owned(claimed, identity)


def _recover_claimed_flag(vault: Path, path: Path) -> ArmedFlag | None:
    prefix = f".{path.name}.claimed."
    try:
        candidates = tuple(
            candidate
            for candidate in path.parent.iterdir()
            if candidate.name.startswith(prefix)
        )
    except OSError:
        return None
    valid: list[tuple[Path, ArmedFlag]] = []
    for candidate in candidates:
        try:
            encoded, identity = _read_regular(candidate)
        except (OSError, ValueError):
            continue
        armed = _decode_flag(vault, path, encoded, identity)
        if armed is not None:
            valid.append((candidate, armed))
    if not valid:
        return None
    if len(valid) != 1:
        raise ClaimRecoveryPendingError("multiple valid private flag claims")
    claimed, armed = valid[0]
    try:
        _restore_owned_claim(
            vault,
            claimed,
            path,
            armed.expected_bytes,
            armed.identity,
        )
    except Exception as error:
        successor = _read_flag(vault, path)
        if successor is not None:
            return successor
        raise ClaimRecoveryPendingError("private flag claim restore failed") from error
    restored = _read_flag(vault, path)
    if restored is None:
        raise ClaimRecoveryPendingError("restored flag could not be validated")
    return restored


def _load_flag(vault: Path) -> ArmedFlag | None:
    path = vault / ".research-vault" / FLAG_NAME
    try:
        encoded, identity = _read_regular(path)
    except FileNotFoundError:
        return _recover_claimed_flag(vault, path)
    except (OSError, ValueError):
        return _recover_claimed_flag(vault, path)
    armed = _decode_flag(vault, path, encoded, identity)
    return armed if armed is not None else _recover_claimed_flag(vault, path)


def _claim_flag(armed: ArmedFlag) -> Path:
    descriptor, claimed_name = tempfile.mkstemp(
        dir=armed.path.parent,
        prefix=f".{armed.path.name}.claimed.",
    )
    os.close(descriptor)
    claimed = Path(claimed_name)
    claimed.unlink()
    moved = False
    try:
        armed.path.replace(claimed)
        moved = True
        current_bytes, current_identity = _read_regular(claimed)
    except Exception:
        if moved:
            try:
                current_bytes, current_identity = _read_regular(claimed)
                _restore_owned_claim(
                    armed.vault,
                    claimed,
                    armed.path,
                    current_bytes,
                    current_identity,
                )
            # Swallowing here is deliberate, and is NOT the fail-open doctrine.
            # This is best-effort recovery while an exception is already unwinding,
            # and the bare `raise` below re-raises the ORIGINAL failure. Letting a
            # restore error escape here would replace the real cause with a less
            # informative one and lose it forever. Swallowing is the correct and
            # only safe behaviour; the flag stays for human follow-up either way.
            except Exception:  # noqa: S110
                pass
        raise
    if current_identity != armed.identity or current_bytes != armed.expected_bytes:
        _restore_owned_claim(
            armed.vault,
            claimed,
            armed.path,
            current_bytes,
            current_identity,
        )
        raise FlagChangedError("publish flag changed before claim")
    return claimed


def _write_blocks(armed: ArmedFlag, blocks: int) -> None:
    state = dict(armed.state)
    state["blocks"] = blocks
    encoded = json.dumps(state, sort_keys=True, separators=(",", ":")).encode()
    descriptor, temporary_name = tempfile.mkstemp(
        dir=armed.path.parent,
        prefix=f".{armed.path.name}.",
    )
    temporary = Path(temporary_name)
    claimed = None
    temporary_identity = None
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            metadata = os.fstat(stream.fileno())
            temporary_identity = (metadata.st_dev, metadata.st_ino)
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        claimed = _claim_flag(armed)
        try:
            os.link(temporary, armed.path)
        except Exception:
            try:
                _restore_owned_claim(
                    armed.vault,
                    claimed,
                    armed.path,
                    armed.expected_bytes,
                    armed.identity,
                )
                claimed = None
            # Swallowing here is deliberate, and is NOT the fail-open doctrine.
            # This is best-effort recovery while an exception is already unwinding,
            # and the bare `raise` below re-raises the ORIGINAL failure. Letting a
            # restore error escape here would replace the real cause with a less
            # informative one and lose it forever. Swallowing is the correct and
            # only safe behaviour; the flag stays for human follow-up either way.
            except Exception:  # noqa: S110
                pass
            raise
        installed_bytes, installed_identity = _read_regular(armed.path)
        if (
            temporary_identity is None
            or installed_identity != temporary_identity
            or installed_bytes != encoded
        ):
            successor = _decode_flag(
                armed.vault,
                armed.path,
                installed_bytes,
                installed_identity,
            )
            if successor is None:
                raise FlagChangedError("counter install did not retain a valid flag")
            _unlink_owned(claimed, armed.identity)
            claimed = None
            raise FlagChangedError("counter install was replaced by a valid successor")
        _unlink_owned(claimed, armed.identity)
        claimed = None
    finally:
        if temporary_identity is not None:
            with suppress(FileNotFoundError, FlagChangedError):
                _unlink_owned(temporary, temporary_identity)


def _clear_flag(armed: ArmedFlag) -> None:
    claimed = _claim_flag(armed)
    _unlink_owned(claimed, armed.identity)


def _json_output(output: dict[str, str]) -> None:
    sys.stdout.write(json.dumps(output, sort_keys=True))


def _bounded_block(armed: ArmedFlag, active: bool, reason: str) -> None:
    next_blocks = armed.blocks + 1 if active else 1
    try:
        _write_blocks(armed, next_blocks)
    except Exception:
        _json_output({"decision": "block", "reason": FAIL_CLOSED_REASON})
        return
    if next_blocks >= MAX_ACTIVE_BLOCKS:
        _json_output({"systemMessage": BOUND_MESSAGE})
    else:
        _json_output({"decision": "block", "reason": reason})


def _has_synthetic_offline(state: PublishState) -> bool:
    return any(outcome.extra.get("synthetic_offline") is True for outcome in state.raw)


def _process(payload: dict[str, object], armed: ArmedFlag) -> None:
    active = payload.get("stop_hook_active")
    if type(active) is not bool:
        raise ValueError("stop_hook_active must be a boolean")
    if armed.bypass is not None:
        try:
            _append_bypass(armed.vault, armed.project, armed.bypass)
            _clear_flag(armed)
        except Exception as error:
            raise BypassFailureError("audited bypass did not complete") from error
        return
    state = _verify_publish(armed.vault)
    decision, blockers = _publish_decision(state)
    if decision:
        reason = "Publish gate blocked:\n" + "\n".join(blockers)
        _bounded_block(armed, active, reason)
        return
    if _has_synthetic_offline(state):
        return
    _clear_flag(armed)


def _handle(payload: object) -> None:
    if not isinstance(payload, dict):
        return
    cwd = payload.get("cwd")
    if type(cwd) is not str:
        return
    vault = _vault_from_cwd(cwd)
    if vault is None:
        return
    try:
        armed = _load_flag(vault)
    except ClaimRecoveryPendingError:
        _json_output({"decision": "block", "reason": FAIL_CLOSED_REASON})
        return
    if armed is None:
        return
    active = payload.get("stop_hook_active") is True
    try:
        _process(payload, armed)
    except BypassFailureError:
        _json_output({"decision": "block", "reason": FAIL_CLOSED_REASON})
    except Exception:
        _bounded_block(armed, active, FAIL_CLOSED_REASON)


def main() -> int:
    """Process one Stop payload without leaking failures or tracebacks."""
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    with suppress(Exception):
        _handle(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
