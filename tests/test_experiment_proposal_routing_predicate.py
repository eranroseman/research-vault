"""Scenario 7's judge, routing_predicate.py, over synthetic stream-json lines
(spec v3, section 5): a positive is a Skill call of this plugin whose result
is not an error; a negative is no Skill or Agent call of this plugin."""

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "docs"
    / "research"
    / "2026-10-13-experiment-proposal-evals"
    / "routing_predicate.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("routing_predicate", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


predicate = _load()


def _init():
    return {
        "type": "system",
        "subtype": "init",
        "model": "claude-opus-5",
        "plugins": [
            {"name": "experiment-proposal", "path": "/x/plugins/experiment-proposal"}
        ],
        "skills": ["experiment-proposal:design", "experiment-proposal:review"],
        "agents": ["experiment-proposal:hci-researcher"],
    }


def _tool_use(name, tool_input, tool_id="toolu_1", model="claude-opus-5-20261001"):
    return {
        "type": "assistant",
        "message": {
            "model": model,
            "content": [
                {"type": "tool_use", "id": tool_id, "name": name, "input": tool_input}
            ],
        },
    }


def _tool_result(tool_id="toolu_1", is_error=False):
    return {
        "type": "user",
        "message": {
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": "ok",
                    "is_error": is_error,
                }
            ]
        },
    }


def _stream(tmp_path, *events):
    path = tmp_path / "run.jsonl"
    path.write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")
    return path


def test_a_positive_needs_a_successful_skill_call_of_the_named_skill(tmp_path):
    path = _stream(
        tmp_path,
        _init(),
        _tool_use(
            "Skill", {"skill": "experiment-proposal:design", "args": "material.md"}
        ),
        _tool_result(),
    )
    verdict = predicate.judge(path, "positive", "design")
    assert verdict["pass"] is True
    assert verdict["skill_calls"] == [
        {"skill": "experiment-proposal:design", "is_error": False}
    ]
    assert verdict["init"]["model"] == "claude-opus-5"
    assert verdict["init"]["plugins"] == ["experiment-proposal"]
    assert verdict["served_models"] == ["claude-opus-5-20261001"]
    assert predicate.judge(path, "positive", "review")["pass"] is False
    errored = _stream(
        tmp_path,
        _init(),
        _tool_use("Skill", {"skill": "experiment-proposal:design"}),
        _tool_result(is_error=True),
    )
    assert predicate.judge(errored, "positive", "design")["pass"] is False
    assert (
        predicate.judge(_stream(tmp_path, _init()), "positive", "design")["pass"]
        is False
    )


def test_a_positive_needs_a_result_whose_is_error_is_false_or_absent(tmp_path):
    path = _stream(
        tmp_path, _init(), _tool_use("Skill", {"skill": "experiment-proposal:design"})
    )
    verdict = predicate.judge(path, "positive", "design")
    assert verdict["pass"] is False
    assert verdict["skill_calls"] == [
        {"skill": "experiment-proposal:design", "is_error": None}
    ]
    assert predicate.judge(path, "negative")["pass"] is False
    result = _tool_result()
    del result["message"]["content"][0]["is_error"]
    path = _stream(
        tmp_path,
        _init(),
        _tool_use("Skill", {"skill": "experiment-proposal:design"}),
        result,
    )
    assert predicate.judge(path, "positive", "design")["pass"] is True


def test_a_negative_bars_this_plugins_skills_and_subagent_only(tmp_path):
    clean = _stream(
        tmp_path,
        _init(),
        _tool_use("Skill", {"skill": "design:user-research"}),
        _tool_result(),
        _tool_use("Bash", {"command": "ls"}, "toolu_2"),
        _tool_result("toolu_2"),
    )
    verdict = predicate.judge(clean, "negative")
    assert verdict["pass"] is True
    assert verdict["other_calls"] == [
        {"name": "Skill", "skill": "design:user-research"},
        {"name": "Bash"},
    ]
    leaked_skill = _stream(
        tmp_path,
        _init(),
        _tool_use("Skill", {"skill": "experiment-proposal:review"}),
        _tool_result(is_error=True),
    )
    assert predicate.judge(leaked_skill, "negative")["pass"] is False
    leaked_agent = _stream(
        tmp_path,
        _init(),
        _tool_use(
            "Agent",
            {"subagent_type": "experiment-proposal:hci-researcher", "prompt": "x"},
        ),
        _tool_result(),
    )
    verdict = predicate.judge(leaked_agent, "negative")
    assert verdict["pass"] is False
    assert verdict["agent_calls"] == ["experiment-proposal:hci-researcher"]
    other_agent = _stream(
        tmp_path,
        _init(),
        _tool_use("Agent", {"subagent_type": "Explore", "prompt": "x"}),
        _tool_result(),
    )
    assert predicate.judge(other_agent, "negative")["pass"] is True


def test_the_cli_exits_0_on_pass_1_on_fail_2_on_an_unreadable_stream(tmp_path, capsys):
    path = _stream(
        tmp_path,
        _init(),
        _tool_use("Skill", {"skill": "experiment-proposal:lit-search"}),
        _tool_result(),
    )
    assert predicate.main(["positive", "lit-search", str(path)]) == 0
    assert json.loads(capsys.readouterr().out)["pass"] is True
    assert predicate.main(["negative", str(path)]) == 1
    capsys.readouterr()
    assert predicate.main(["negative", str(tmp_path / "missing.jsonl")]) == 2
    broken = tmp_path / "broken.jsonl"
    broken.write_text("not json\n", encoding="utf-8")
    assert predicate.main(["negative", str(broken)]) == 2
