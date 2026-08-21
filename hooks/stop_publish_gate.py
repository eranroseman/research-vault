"""Bounded, explicitly armed Stop gate for publish verification."""

from __future__ import annotations

import json
import os
import stat
import sys
import tempfile
from pathlib import Path

CORE = Path(__file__).resolve().parents[1] / "core"
FLAG_NAME = "publish-pending.json"
MAX_ACTIVE_BLOCKS = 8
FAIL_CLOSED_REASON = (
    "Publish verification unavailable; resolve the gate or use its audited bypass."
)
BOUND_MESSAGE = (
    "Publish gate reached the eight-block safety bound; the pending flag remains "
    "for human follow-up."
)


class FlagChanged(RuntimeError):
    """The armed flag changed after this invocation read it."""


class ArmedFlag:
    __slots__ = (
        "path",
        "vault",
        "project",
        "blocks",
        "bypass",
        "state",
        "expected_bytes",
        "identity",
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
    __slots__ = ("raw", "effective", "warning_effective")

    def __init__(self, raw, effective, warning_effective) -> None:
        self.raw = raw
        self.effective = effective
        self.warning_effective = warning_effective


def _core_path() -> None:
    if str(CORE) not in sys.path:
        sys.path.insert(0, str(CORE))


def _verify_publish(vault: Path) -> PublishState:
    """Run the production network-capable verification transaction."""
    _core_path()
    from harness_core.__main__ import _verify_state

    report, effective, _hashes, warning_effective = _verify_state(
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
    from harness_core.__main__ import _surface_decision

    return _surface_decision(
        "publish",
        state.effective,
        state.warning_effective,
    )


def _append_bypass(vault: Path, project: str, reason: str) -> None:
    _core_path()
    from harness_core import Result, inbox
    from harness_core.pathcodec import encode_repo_path

    inbox.append_entry(
        vault,
        "publish-gate",
        encode_repo_path(os.fsencode(project)),
        Result.UNMATCHED,
        f"manual — publish-gate bypass: {reason}",
        actor="human:publish-bypass",
        target_kind="repo-path",
    )


def _vault_from_cwd(cwd: str) -> Path | None:
    """Find the nearest real vault marker, including cwd itself."""
    try:
        current = Path(cwd).resolve(strict=True)
    except (OSError, RuntimeError):
        return None
    if not current.is_dir():
        return None
    for candidate in (current, *current.parents):
        marker = candidate / ".harness"
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


def _load_flag(vault: Path) -> ArmedFlag | None:
    path = vault / ".harness" / FLAG_NAME
    try:
        encoded, identity = _read_regular(path)
        state = json.loads(encoded)
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
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


def _restore_claimed(claimed: Path, path: Path) -> None:
    try:
        os.link(claimed, path)
    except FileExistsError:
        return
    claimed.unlink()


def _claim_flag(armed: ArmedFlag) -> Path:
    descriptor, claimed_name = tempfile.mkstemp(
        dir=armed.path.parent,
        prefix=f".{armed.path.name}.claimed.",
    )
    os.close(descriptor)
    claimed = Path(claimed_name)
    claimed.unlink()
    try:
        os.replace(armed.path, claimed)
        current_bytes, current_identity = _read_regular(claimed)
    except Exception:
        if claimed.exists():
            _restore_claimed(claimed, armed.path)
        raise
    if current_identity != armed.identity or current_bytes != armed.expected_bytes:
        _restore_claimed(claimed, armed.path)
        raise FlagChanged("publish flag changed before claim")
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
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        claimed = _claim_flag(armed)
        try:
            os.link(temporary, armed.path)
        except Exception:
            claimed.unlink(missing_ok=True)
            raise
        claimed.unlink()
        claimed = None
    finally:
        temporary.unlink(missing_ok=True)
        if claimed is not None:
            claimed.unlink(missing_ok=True)


def _clear_flag(armed: ArmedFlag) -> None:
    claimed = _claim_flag(armed)
    claimed.unlink()


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
        _append_bypass(armed.vault, armed.project, armed.bypass)
        _clear_flag(armed)
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
    armed = _load_flag(vault)
    if armed is None:
        return
    active = payload.get("stop_hook_active") is True
    try:
        _process(payload, armed)
    except Exception:
        _bounded_block(armed, active, FAIL_CLOSED_REASON)


def main() -> int:
    """Process one Stop payload without leaking failures or tracebacks."""
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    try:
        _handle(payload)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
