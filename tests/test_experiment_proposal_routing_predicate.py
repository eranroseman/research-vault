"""Scenario 7's judge, routing_predicate.py, over synthetic stream-json lines
(spec v3, section 5): a positive is a top-level Skill call of this plugin
whose result is not an error; a negative is no Skill or Agent call of this
plugin, top-level or inside a subagent."""

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


def test_a_malformed_message_or_input_is_read_as_empty_not_a_crash(tmp_path, capsys):
    """An error event carries a string message, and a tool_use's input can be a
    string; neither is a call of this plugin, so the negative holds (exit 0)."""
    path = _stream(
        tmp_path,
        _init(),
        {"type": "error", "message": "overloaded"},
        _tool_use("Skill", "x"),
        _tool_result(),
    )
    assert predicate.main(["negative", str(path)]) == 0
    verdict = json.loads(capsys.readouterr().out)
    assert verdict["other_calls"] == [{"name": "Skill", "skill": None}]


def test_a_result_whose_is_error_is_null_is_not_a_positive(tmp_path, capsys):
    """The grammar says false or absent; null is neither."""
    path = _stream(
        tmp_path,
        _init(),
        _tool_use("Skill", {"skill": "experiment-proposal:design"}),
        _tool_result(is_error=None),
    )
    assert predicate.main(["positive", "design", str(path)]) == 1
    assert json.loads(capsys.readouterr().out)["skill_calls"] == [
        {"skill": "experiment-proposal:design", "is_error": None}
    ]


def _in_subagent(event, parent="toolu_agent"):
    """The stream marks an event of a subagent's conversation with the id of
    the Agent call that spawned it; a top-level event carries null."""
    return {**event, "parent_tool_use_id": parent}


def _delegated(skill):
    """The main session delegates to a general-purpose Agent, which calls the
    skill inside its own conversation (run routing-review-1 at 0.3.0)."""
    return (
        _in_subagent(
            _tool_use(
                "Agent",
                {"subagent_type": "general-purpose", "prompt": "x"},
                "toolu_agent",
            ),
            None,
        ),
        _in_subagent(_tool_use("Skill", {"skill": skill}, "toolu_nested")),
        _in_subagent(_tool_result("toolu_nested")),
        _in_subagent(_tool_result("toolu_agent"), None),
    )


def test_a_skill_call_inside_a_subagent_alone_is_not_a_positive(tmp_path):
    path = _stream(tmp_path, _init(), *_delegated("experiment-proposal:review"))
    verdict = predicate.judge(path, "positive", "review")
    assert verdict["pass"] is False
    assert verdict["skill_calls"] == [
        {"skill": "experiment-proposal:review", "is_error": False}
    ]
    assert verdict["skill_calls_in_subagents"] == [
        {
            "skill": "experiment-proposal:review",
            "is_error": False,
            "parent_tool_use_id": "toolu_agent",
        }
    ]
    assert predicate.main(["positive", "review", str(path)]) == 1


def test_a_top_level_call_passes_whether_parent_tool_use_id_is_null_or_absent(
    tmp_path,
):
    """Real streams carry the key with null on every top-level event; the
    synthetic events above omit it. Both are the top-level conversation."""
    path = _stream(
        tmp_path,
        _init(),
        *_delegated("experiment-proposal:review"),
        _in_subagent(_tool_use("Skill", {"skill": "experiment-proposal:review"}), None),
        _in_subagent(_tool_result(), None),
    )
    verdict = predicate.judge(path, "positive", "review")
    assert verdict["pass"] is True
    assert len(verdict["skill_calls"]) == 2
    assert len(verdict["skill_calls_in_subagents"]) == 1


def test_a_call_of_this_plugin_inside_a_subagent_fails_a_negative(tmp_path):
    nested_skill = _stream(tmp_path, _init(), *_delegated("experiment-proposal:design"))
    assert predicate.judge(nested_skill, "negative")["pass"] is False
    nested_agent = _stream(
        tmp_path,
        _init(),
        _in_subagent(
            _tool_use(
                "Agent",
                {"subagent_type": "experiment-proposal:hci-researcher", "prompt": "x"},
                "toolu_inner",
            )
        ),
        _in_subagent(_tool_result("toolu_inner")),
    )
    verdict = predicate.judge(nested_agent, "negative")
    assert verdict["pass"] is False
    assert verdict["agent_calls"] == ["experiment-proposal:hci-researcher"]
    other = _stream(tmp_path, _init(), *_delegated("design:user-research"))
    assert predicate.judge(other, "negative")["pass"] is True
