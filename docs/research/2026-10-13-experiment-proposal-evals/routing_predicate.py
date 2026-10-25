#!/usr/bin/env python3
"""Judge one `claude -p --output-format stream-json --verbose` stream for
scenario 7 of the experiment-proposal evals (spec v3, section 5).

Usage:
    routing_predicate.py positive <skill> <stream.jsonl>
    routing_predicate.py negative <stream.jsonl>

A positive for <skill> holds when at least one Skill tool_use names
experiment-proposal:<skill> and has a tool_result that is not an error; a
call with no tool_result reads is_error null and is not a positive. A negative
holds when no Skill tool_use names an experiment-proposal skill and no Agent
tool_use names experiment-proposal:hci-researcher; other plugins' calls are
listed under other_calls and not barred. Prints one JSON object with the
verdict, the calls, the init event's plugins, skills, agents and model, and
the models that served assistant turns. Exit 0 pass, 1 fail, 2 unreadable.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

PLUGIN = "experiment-proposal:"
SUBAGENT = "experiment-proposal:hci-researcher"


def events_of(path: Path) -> list[dict]:
    events: list[dict] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{number}: not JSON ({exc.msg})") from exc
        if isinstance(event, dict):
            events.append(event)
    return events


def judge(path: Path, mode: str, skill: str | None = None) -> dict:
    events = events_of(path)
    init: dict = {}
    uses: dict[str, dict] = {}
    order: list[str] = []
    results: dict[str, bool] = {}
    served: list[str] = []
    for event in events:
        if event.get("type") == "system" and event.get("subtype") == "init":
            init = {
                "model": event.get("model"),
                "plugins": [
                    p.get("name") if isinstance(p, dict) else p
                    for p in event.get("plugins") or []
                ],
                "skills": list(event.get("skills") or []),
                "agents": list(event.get("agents") or []),
            }
        message = event.get("message") or {}
        if event.get("type") == "assistant":
            model = message.get("model")
            if model and model not in served:
                served.append(model)
        for block in message.get("content") or []:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use":
                uses[block.get("id", f"anon-{len(order)}")] = block
                order.append(block.get("id", f"anon-{len(order)}"))
            elif block.get("type") == "tool_result":
                results[block.get("tool_use_id", "")] = bool(
                    block.get("is_error", False)
                )
    skill_calls: list[dict] = []
    agent_calls: list[str] = []
    other_calls: list[dict] = []
    for tool_id in order:
        block = uses[tool_id]
        name, tool_input = block.get("name"), block.get("input") or {}
        if name == "Skill" and str(tool_input.get("skill", "")).startswith(PLUGIN):
            skill_calls.append(
                {"skill": tool_input["skill"], "is_error": results.get(tool_id)}
            )
        elif name == "Agent" and tool_input.get("subagent_type") == SUBAGENT:
            agent_calls.append(SUBAGENT)
        elif name == "Skill":
            other_calls.append({"name": "Skill", "skill": tool_input.get("skill")})
        else:
            other_calls.append({"name": name})
    if mode == "positive":
        passed = any(
            c["skill"] == f"{PLUGIN}{skill}" and c["is_error"] is False
            for c in skill_calls
        )
    else:
        passed = not skill_calls and not agent_calls
    return {
        "mode": mode,
        "skill": skill,
        "pass": passed,
        "skill_calls": skill_calls,
        "agent_calls": agent_calls,
        "other_calls": other_calls,
        "init": init,
        "served_models": served,
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) == 3 and args[0] == "positive":
        mode, skill, path = args[0], args[1], Path(args[2])
    elif len(args) == 2 and args[0] == "negative":
        mode, skill, path = args[0], None, Path(args[1])
    else:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        verdict = judge(path, mode, skill)
    except (OSError, ValueError) as error:
        print(f"{path}: cannot judge: {error}", file=sys.stderr)
        return 2
    print(json.dumps(verdict, indent=2))
    return 0 if verdict["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
