"""Fail-open PostToolUse warnings for markdown concept notes."""

from __future__ import annotations

import json
import os
import sys
from contextlib import suppress
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CONCEPT_ROOTS = frozenset({"synthesis", "projects"})


def _core_path() -> None:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))


def _load_bibliography(vault: Path):
    _core_path()
    from knowledge_harness import bibliography

    return bibliography.load(vault)


def _file_outcomes(vault: Path, path: Path, bibliography_universe):
    _core_path()
    from knowledge_harness.verify import file_outcomes as collect

    return collect(vault, path, bibliography_universe)


def _encode_repo_path(raw: bytes) -> str:
    _core_path()
    from knowledge_harness.pathcodec import encode_repo_path

    return encode_repo_path(raw)


def _vault_from_cwd(cwd: str) -> Path | None:
    """Find the nearest vault, including cwd itself."""
    current = Path(cwd).resolve()
    for candidate in (current, *current.parents):
        marker = candidate / ".harness"
        if marker.is_dir() and not marker.is_symlink():
            return candidate
    return None


def _warning(context: str) -> None:
    sys.stdout.write(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": context,
                }
            }
        )
    )


def _render_outcome(outcome) -> str:
    return f"{outcome.result.value} {outcome.check} {outcome.target} — {outcome.reason}"


def _handle(payload: object) -> None:
    if not isinstance(payload, dict):
        return
    cwd = payload.get("cwd")
    tool_name = payload.get("tool_name")
    tool_input = payload.get("tool_input")
    if (
        not isinstance(cwd, str)
        or tool_name not in {"Edit", "Write"}
        or not isinstance(tool_input, dict)
    ):
        return
    file_path = tool_input.get("file_path")
    if not isinstance(file_path, str):
        return
    vault = _vault_from_cwd(cwd)
    if vault is None:
        return
    path = Path(file_path)
    if not path.is_absolute():
        path = Path(cwd) / path
    path = path.resolve()
    try:
        relative = path.relative_to(vault)
    except ValueError:
        return
    if not relative.parts:
        return
    if relative.parts[0] == "literatures":
        _warning(
            "UNMATCHED evidence-layer "
            f"{_encode_repo_path(os.fsencode(relative))} — "
            "LLM edit touched literature evidence"
        )
        return
    if relative.parts[0] not in CONCEPT_ROOTS or path.suffix != ".md":
        return
    bibliography_universe = _load_bibliography(vault)
    findings = [
        outcome
        for outcome in _file_outcomes(vault, path, bibliography_universe)
        if outcome.extra.get("synthetic_offline") is not True
        and outcome.result.value not in {"MATCHED", "SKIPPED"}
    ]
    if findings:
        _warning("PostToolUse warnings:\n" + "\n".join(map(_render_outcome, findings)))


def main() -> int:
    """Run the warning surface without ever interrupting a Claude session."""
    with suppress(Exception):
        _handle(json.load(sys.stdin))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
