"""Fail-closed PreToolUse deny guard for vault machine surfaces."""

from __future__ import annotations

import json
import os
import stat
import sys
from pathlib import Path

MACHINE_SURFACE_DIR_NAMES = frozenset({"literatures", "log", "wiki", "fulltext"})
# Root-only exact match: a deeper `log.md` (e.g. inside a project) or
# `search-log.md` (searchlog.py writes `projects/<name>/search-log.md`) is
# a different file and is not on this list.
MACHINE_SURFACE_FILES = frozenset(
    {
        Path("log.md"),
        Path("inbox/review-queue.md"),
        Path("system/bibliography.json"),
    }
)
TOOL_PATH_KEYS = ("file_path", "notebook_path")

DENY_REASON = (
    "machine surface; the CLI writes this — use the matching verb "
    "(`finding`, `ack`, `capture`, …)"
)
FAIL_CLOSED_REASON = (
    "Machine-surface guard failed closed; resolve the fault before retrying this edit."
)


def _candidate_paths(tool_input: dict) -> list[str]:
    return [
        value for key in TOOL_PATH_KEYS if isinstance(value := tool_input.get(key), str)
    ]


def _resolve_candidate(raw: str, cwd: str | None) -> Path | None:
    """Absolutize a relative candidate against `cwd`, then fully resolve it.

    A bare `Path(cwd)` prefix is not trusted as an anchor: `cwd` is used only
    to complete a relative path, never to locate the vault (see
    `_vault_from_target`), so a relative-path candidate with no usable `cwd`
    is unresolvable rather than silently anchored to the wrong directory.
    """
    candidate = Path(raw)
    if not candidate.is_absolute():
        if cwd is None or not Path(cwd).is_absolute():
            return None
        candidate = Path(cwd) / candidate
    return candidate.resolve()


def _vault_from_target(target: Path) -> Path | None:
    """Find the nearest vault by walking up from the target's own directory.

    Anchored on the resolved write target, not on `cwd` — a `cd` elsewhere
    followed by an absolute-path write into a vault must still be caught.
    """
    for candidate in (target.parent, *target.parent.parents):
        marker = candidate / ".research-vault"
        try:
            marker_stat = os.lstat(marker)
        except OSError:
            continue
        if stat.S_ISDIR(marker_stat.st_mode):
            return candidate
    return None


def _is_machine_surface(relative: Path) -> bool:
    if relative in MACHINE_SURFACE_FILES:
        return True
    # `relative.parts` is empty only in the degenerate case where the
    # resolved target IS the vault root (`target.parent == target`, true
    # only for the filesystem root, `/`, with a real `.research-vault` there too).
    # No `bool(...)` guard here: that guard's only reachable-in-principle
    # act would be to ALLOW the one write this hook exists to refuse.
    # `relative.parts[0]` raising `IndexError` instead routes the same
    # case into `main()`'s fail-closed deny, which is the correct outcome.
    return relative.parts[0] in MACHINE_SURFACE_DIR_NAMES


def _deny(reason: str) -> None:
    sys.stdout.write(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


def _handle(payload: object) -> None:
    if not isinstance(payload, dict):
        return
    if payload.get("tool_name") not in {"Edit", "Write", "NotebookEdit"}:
        return
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return
    cwd = payload.get("cwd")
    cwd = cwd if isinstance(cwd, str) else None
    for raw in _candidate_paths(tool_input):
        resolved = _resolve_candidate(raw, cwd)
        if resolved is None:
            continue
        vault = _vault_from_target(resolved)
        if vault is None:
            continue
        # `vault` is always drawn from `resolved`'s own parents (see
        # `_vault_from_target`), so it is always a prefix of `resolved` —
        # `relative_to` cannot raise `ValueError` here.
        relative = resolved.relative_to(vault)
        if _is_machine_surface(relative):
            _deny(DENY_REASON)
            return


def main() -> int:
    """Deny known machine-surface writes; fail closed on any other fault.

    Unparsable stdin cannot be attributed to a real Edit/Write/NotebookEdit
    call (Claude Code always sends well-formed JSON for a matched tool), so
    it is inert rather than a guard failure. Once the payload parses, any
    further exception means the guard could not prove the write was safe —
    that must deny, not silently allow (a swallowed exception ending in
    "allow" reports protection this hook is not providing).
    """
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    try:
        _handle(payload)
    except Exception:
        _deny(FAIL_CLOSED_REASON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
