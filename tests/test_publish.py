"""The publish surface: gate-flag verbs, dispositions, and the ack verb (spec §6).

Every vault built here is deliberately bibliography-free (or points its
Zotero base at a dead port), so the publish gate runs its real
network-capable transaction without ever leaving the machine: absent
`system/bibliography.json` means no staleness probe and no bibliography
entries to route through Crossref. The disposition verbs therefore need no
``--offline`` escape hatch — spec §6 forbids synthetic offline outcomes from
minting trust, and one does not exist to be misused.
"""

import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

from knowledge_harness import events, frontmatter, inbox, lints, publish
from knowledge_harness.__main__ import main

REPO = Path(__file__).resolve().parents[1]
STOP_HOOK = REPO / "hooks" / "stop_publish_gate.py"
PUBLISH_SKILL = REPO / "skills" / "publish" / "SKILL.md"
FLAG = Path(".harness") / "publish-pending.json"

PROJECT_FRONTMATTER = """---
title: "Evidence brief"
type: "project"
status: "draft"
generated: {by: "knowledge_harness/0.1.0", at: "2026-08-16T09:00:00Z"}
---
"""
UNCITED_CLAIM = "- (open-question) Does this replicate? ^c-88888888\n"
GHOST_CLAIM = "- (inference) It replicates [@ghost2020] ^c-88888888\n"


def _load_stop_hook():
    """Load the shipped Stop hook so flag shapes are judged by its own decoder."""
    spec = importlib.util.spec_from_file_location("stop_publish_gate", STOP_HOOK)
    assert spec is not None
    assert spec.loader is not None
    hook = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hook)
    return hook


def _git(vault: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=vault, capture_output=True, text=True, check=True
    ).stdout


def _head(vault: Path) -> str:
    return _git(vault, "rev-parse", "HEAD").strip()


def _tags(vault: Path) -> list[str]:
    return _git(vault, "tag", "--list").split()


def _note(vault: Path, project: str = "brief") -> Path:
    return vault / "projects" / project / "draft.md"


def _status(vault: Path, project: str = "brief") -> str:
    data, _ = frontmatter.parse(_note(vault, project).read_text())
    return data["status"]


def _build_vault(
    root: Path, claim: str, bibliography=None, name: str = "brief"
) -> Path:
    for folder in ("inbox", "literatures", "synthesis", "log", "projects", "system"):
        (root / folder).mkdir()
    (root / "index.md").write_text('---\nokf_version: "0.2"\n---\n# Knowledge bundle\n')
    (root / "log.md").write_text("# Log\n")
    (root / "synthesis" / "index.md").write_text("# Synthesis index\n")
    (root / "inbox" / "review-queue.md").write_text('---\ntype: "review-queue"\n---\n')
    if bibliography is not None:
        (root / "system" / "bibliography.json").write_text(json.dumps(bibliography))
    project = root / "projects" / name
    project.mkdir()
    (project / "draft.md").write_text(PROJECT_FRONTMATTER + claim)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "project vault"], cwd=root, check=True)
    (root / ".harness").mkdir()
    return root


@pytest.fixture
def green_vault(tmp_path):
    """A vault whose publish surface is green with no network traffic at all."""
    return _build_vault(tmp_path, UNCITED_CLAIM)


@pytest.fixture
def blocked_vault(tmp_path):
    """A vault blocked by a closing check: a citekey outside the bibliography."""
    return _build_vault(tmp_path, GHOST_CLAIM)


@pytest.fixture
def unreachable_vault(tmp_path):
    """A vault whose only non-MATCHED result is an outage — publishing waits."""
    return _build_vault(tmp_path, UNCITED_CLAIM, bibliography=[])


DEAD_BASE = "http://127.0.0.1:1/"


# --- gate flag -------------------------------------------------------------


def test_arm_publish_writes_a_flag_the_stop_hook_decodes(green_vault):
    assert main(["arm-publish", "brief", "--vault", str(green_vault)]) == 0

    flag = green_vault / FLAG
    assert set(json.loads(flag.read_text())) == {"project", "vault", "blocks"}
    armed = _load_stop_hook()._load_flag(green_vault.resolve())
    assert armed is not None
    assert (armed.project, armed.blocks, armed.bypass) == ("projects/brief", 0, None)


def test_arm_publish_records_a_consented_bypass_token(green_vault):
    assert (
        main(
            [
                "arm-publish",
                "brief",
                "--vault",
                str(green_vault),
                "--bypass",
                "deadline waiver",
            ]
        )
        == 0
    )

    flag = green_vault / FLAG
    assert set(json.loads(flag.read_text())) == {"project", "vault", "blocks", "bypass"}
    armed = _load_stop_hook()._load_flag(green_vault.resolve())
    assert armed is not None
    assert armed.bypass == "deadline waiver"


@pytest.mark.parametrize(
    "mutation",
    [
        {"project": None, "project_path": "projects/brief"},
        {"blocks": True},
        {"blocks": "0"},
        {"blocks": -1},
        {"extra": "field"},
        {"vault": None},
        {"bypass": "two\nlines"},
    ],
    ids=[
        "renamed-key",
        "boolean-blocks",
        "string-blocks",
        "negative-blocks",
        "extra-key",
        "missing-vault",
        "multiline-bypass",
    ],
)
def test_a_wrong_shaped_flag_leaves_the_vault_unarmed(
    green_vault, monkeypatch, capsys, mutation
):
    """Anything off-schema is silently inert at HEAD — assert that against the
    hook's own decoder, never against a re-implementation of it."""
    assert main(["arm-publish", "brief", "--vault", str(green_vault)]) == 0
    flag = green_vault / FLAG
    state = json.loads(flag.read_text())
    state.update(mutation)
    flag.write_text(json.dumps({k: v for k, v in state.items() if v is not None}))
    before = flag.read_bytes()
    hook = _load_stop_hook()
    monkeypatch.setattr(
        hook,
        "_verify_publish",
        lambda _vault: pytest.fail("a wrong-shaped flag must stay unarmed"),
    )

    assert hook._load_flag(green_vault.resolve()) is None

    payload = {
        "cwd": str(green_vault),
        "hook_event_name": "Stop",
        "stop_hook_active": False,
    }
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    capsys.readouterr()
    assert hook.main() == 0
    captured = capsys.readouterr()
    assert (captured.out, captured.err) == ("", "")
    assert flag.read_bytes() == before


def test_disarm_publish_removes_the_flag_and_tolerates_an_unarmed_vault(green_vault):
    assert main(["arm-publish", "brief", "--vault", str(green_vault)]) == 0

    assert main(["disarm-publish", "--vault", str(green_vault)]) == 0
    assert not (green_vault / FLAG).exists()
    assert main(["disarm-publish", "--vault", str(green_vault)]) == 0


def test_arm_publish_refuses_a_project_the_hook_would_reject(green_vault, capsys):
    assert main(["arm-publish", "missing", "--vault", str(green_vault)]) == 2
    assert main(["arm-publish", "projects/brief", "--vault", str(green_vault)]) == 2

    assert not (green_vault / FLAG).exists()
    assert capsys.readouterr().out == ""


# --- mark-published --------------------------------------------------------


def test_mark_published_writes_status_event_commit_and_tag_then_disarms(green_vault):
    assert main(["arm-publish", "brief", "--vault", str(green_vault)]) == 0
    before = _head(green_vault)

    assert main(["mark-published", "brief", "--vault", str(green_vault)]) == 0

    text = _note(green_vault).read_text()
    data, _ = frontmatter.parse(text)
    assert data["status"] == "published"
    assert [event["check"] for event in events.verified_checks(text)] == ["publish"]

    head = _head(green_vault)
    assert _git(green_vault, "rev-parse", "HEAD^").strip() == before
    changed = _git(
        green_vault, "diff-tree", "--no-commit-id", "--name-only", "-r", head
    ).split()
    assert changed == ["projects/brief/draft.md"]

    assert len(_tags(green_vault)) == 1
    tag = _tags(green_vault)[0]
    match = lints.PUBLISHED_TAG.match(tag)
    assert match is not None
    assert match.group(1) == "brief"
    assert _git(green_vault, "rev-parse", f"{tag}^{{commit}}").strip() == head
    assert lints.lint_published_drift(green_vault) == []
    assert not (green_vault / FLAG).exists()


def test_mark_published_refuses_a_blocked_gate_and_leaves_the_gate_armed(
    blocked_vault, capsys
):
    assert main(["arm-publish", "brief", "--vault", str(blocked_vault)]) == 0
    before = _head(blocked_vault)

    assert main(["mark-published", "brief", "--vault", str(blocked_vault)]) == 1

    assert "UNMATCHED citekey ghost2020" in capsys.readouterr().out
    assert _status(blocked_vault) == "draft"
    assert _tags(blocked_vault) == []
    assert _head(blocked_vault) == before
    assert (blocked_vault / FLAG).exists()


def test_mark_published_waits_when_the_gate_is_unreachable(unreachable_vault, capsys):
    code = main(
        [
            "mark-published",
            "brief",
            "--vault",
            str(unreachable_vault),
            "--base",
            DEAD_BASE,
        ]
    )

    assert code == 3
    assert "UNREACHABLE staleness" in capsys.readouterr().out
    assert _status(unreachable_vault) == "draft"
    assert _tags(unreachable_vault) == []


def test_mark_published_proceeds_once_a_blocking_entry_carries_a_standing_ack(
    blocked_vault,
):
    # The first gate run stamps the failing claim, so run it twice before
    # acknowledging: an ack is hash-scoped, and the second run's finding
    # carries the note's settled hash.
    assert main(["verify", "--vault", str(blocked_vault), "--surface", "publish"]) == 1
    assert main(["mark-published", "brief", "--vault", str(blocked_vault)]) == 1
    standing = [
        entry
        for entry in inbox.open_entries(blocked_vault)
        if entry.check == "citekey" and entry.result == "UNMATCHED"
    ][-1]

    assert (
        main(
            [
                "ack",
                standing.id,
                "--vault",
                str(blocked_vault),
                "--reason",
                "manual — cited only to discuss its own withdrawal",
                "--actor",
                "human:eran",
            ]
        )
        == 0
    )
    assert main(["mark-published", "brief", "--vault", str(blocked_vault)]) == 0
    assert _status(blocked_vault) == "published"


def test_mark_published_refuses_an_uncommitted_project_file(green_vault, capsys):
    (green_vault / "projects" / "brief" / "appendix.md").write_text("# Appendix\n")
    before = _head(green_vault)

    assert main(["mark-published", "brief", "--vault", str(green_vault)]) == 2

    assert "projects/brief/appendix.md" in capsys.readouterr().err
    assert _status(green_vault) == "draft"
    assert _tags(green_vault) == []
    assert _head(green_vault) == before


# --- park, correction, withdrawal ------------------------------------------


def test_park_sets_status_parked_and_nothing_else(green_vault):
    before = _head(green_vault)

    assert main(["park", "brief", "--vault", str(green_vault)]) == 0

    text = _note(green_vault).read_text()
    assert frontmatter.parse(text)[0]["status"] == "parked"
    assert events.verified_checks(text) == []
    assert _head(green_vault) == before
    assert _tags(green_vault) == []


@pytest.mark.parametrize("verb", ["mark-corrected", "mark-withdrawn"])
def test_corrections_refuse_before_any_publication(green_vault, capsys, verb):
    before = _head(green_vault)

    assert main([verb, "brief", "--vault", str(green_vault)]) == 2

    assert "published" in capsys.readouterr().err
    assert _status(green_vault) == "draft"
    assert _head(green_vault) == before


def test_mark_corrected_mints_a_new_event_and_tag_and_keeps_the_original(green_vault):
    first = publish.mark_published(green_vault, "brief", date="2026-08-01")
    assert first.tag == "published/brief-2026-08-01"

    second = publish.mark_corrected(green_vault, "brief", date="2026-08-09")

    assert second.status == "corrected"
    assert second.tag == "published/brief-2026-08-09"
    text = _note(green_vault).read_text()
    assert frontmatter.parse(text)[0]["status"] == "corrected"
    assert [event["at"] for event in events.verified_checks(text)] == [
        "2026-08-01",
        "2026-08-09",
    ]
    assert _tags(green_vault) == [
        "published/brief-2026-08-01",
        "published/brief-2026-08-09",
    ]
    first_commit = _git(
        green_vault, "rev-parse", "published/brief-2026-08-01^{commit}"
    ).strip()
    assert _git(green_vault, "rev-parse", "HEAD^").strip() == first_commit


def test_mark_corrected_refuses_a_tag_that_already_exists(green_vault):
    publish.mark_published(green_vault, "brief", date="2026-08-01")

    with pytest.raises(publish.PublishError, match="published/brief-2026-08-01"):
        publish.mark_corrected(green_vault, "brief", date="2026-08-01")

    assert _status(green_vault) == "published"


def test_mark_withdrawn_writes_status_and_logs_without_deleting_the_tag(green_vault):
    publish.mark_published(green_vault, "brief", date="2026-08-01")
    head = _head(green_vault)

    assert main(["mark-withdrawn", "brief", "--vault", str(green_vault)]) == 0

    text = _note(green_vault).read_text()
    assert frontmatter.parse(text)[0]["status"] == "withdrawn"
    assert _tags(green_vault) == ["published/brief-2026-08-01"]
    assert _head(green_vault) == head
    day_files = sorted((green_vault / "log").glob("*.md"))
    assert len(day_files) == 1
    logged = day_files[0].read_text()
    assert frontmatter.parse(logged)[0] == {"type": "daily"}
    assert "withdrew projects/brief" in logged
    assert "withdrew projects/brief" in (green_vault / "log.md").read_text()


# --- ack -------------------------------------------------------------------


def test_ack_closes_an_open_finding(blocked_vault):
    assert main(["verify", "--vault", str(blocked_vault), "--surface", "publish"]) == 1
    standing = [
        entry
        for entry in inbox.open_entries(blocked_vault)
        if entry.check == "citekey" and entry.result == "UNMATCHED"
    ][-1]

    code = main(
        [
            "ack",
            standing.id,
            "--vault",
            str(blocked_vault),
            "--reason",
            "manual — cited only to discuss its own withdrawal",
            "--actor",
            "human:eran",
        ]
    )

    assert code == 0
    assert standing.id not in {entry.id for entry in inbox.open_entries(blocked_vault)}


@pytest.mark.parametrize(
    ("actor", "reason"),
    [
        ("knowledge_harness/0.1.0", "manual — the CLI cannot consent for a human"),
        ("human:eran", "invented-code — not in the registry"),
    ],
    ids=["non-human-actor", "unregistered-reason"],
)
def test_ack_refuses_an_unacceptable_actor_or_reason(blocked_vault, actor, reason):
    assert main(["verify", "--vault", str(blocked_vault), "--surface", "publish"]) == 1
    queue = blocked_vault / inbox.INBOX_PATH
    before = queue.read_bytes()
    standing = inbox.open_entries(blocked_vault)[-1]

    code = main(
        [
            "ack",
            standing.id,
            "--vault",
            str(blocked_vault),
            "--reason",
            reason,
            "--actor",
            actor,
        ]
    )

    assert code == 2
    assert queue.read_bytes() == before


# --- skill -----------------------------------------------------------------


def test_publish_skill_routes_every_mechanical_act_through_a_verb():
    text = PUBLISH_SKILL.read_text(encoding="utf-8")
    for token in (
        "verify --surface publish",
        "arm-publish",
        "disarm-publish",
        "mark-published",
        "mark-corrected",
        "mark-withdrawn",
        "park",
        "ack",
        "MATCHED",
        "UNMATCHED",
        "UNREACHABLE",
        "SKIPPED",
        "keep-draft",
        "discard",
    ):
        assert token in text, f"publish/SKILL.md never mentions {token!r}"


# --- review findings, round 1 ----------------------------------------------


def test_a_project_git_cannot_tag_is_refused_before_anything_is_written(
    tmp_path, capsys
):
    """`PUBLISHED_TAG`'s `.+` admits spaces; git's ref rules do not. Refusing
    late would commit a `published` project that can never be tagged, and so
    can never be corrected or withdrawn either."""
    vault = _build_vault(tmp_path, UNCITED_CLAIM, name="my brief")
    queue = (vault / inbox.INBOX_PATH).read_bytes()
    before = _head(vault)

    assert main(["arm-publish", "my brief", "--vault", str(vault)]) == 2
    assert not (vault / FLAG).exists()

    assert main(["mark-published", "my brief", "--vault", str(vault)]) == 2

    assert "tag" in capsys.readouterr().err
    # An untouched review queue proves the refusal landed before the gate ran.
    assert (vault / inbox.INBOX_PATH).read_bytes() == queue
    assert _status(vault, "my brief") == "draft"
    assert events.verified_checks(_note(vault, "my brief").read_text()) == []
    assert _tags(vault) == []
    assert _head(vault) == before


def test_inbox_prints_the_finding_id_the_ack_verb_needs(blocked_vault, capsys):
    """The skill sends the person to `inbox` for the id `ack` requires, so the
    id has to be on that surface — not only inside the queue file."""
    assert main(["verify", "--vault", str(blocked_vault), "--surface", "publish"]) == 1
    capsys.readouterr()

    assert main(["inbox", "--vault", str(blocked_vault)]) == 0

    lines = capsys.readouterr().out.splitlines()
    citekey_lines = [line for line in lines[1:] if "ghost2020" in line]
    assert len(citekey_lines) == 1
    finding_id = citekey_lines[0].split()[0]
    assert finding_id.startswith("citekey/")

    code = main(
        [
            "ack",
            finding_id,
            "--vault",
            str(blocked_vault),
            "--reason",
            "manual — cited only to discuss its own withdrawal",
            "--actor",
            "human:eran",
        ]
    )

    assert code == 0
    assert finding_id not in {entry.id for entry in inbox.open_entries(blocked_vault)}


@pytest.mark.parametrize("verb", ["mark-published", "park"])
def test_the_day_one_menu_refuses_an_already_published_project(
    green_vault, capsys, verb
):
    """§6's day-one menu is the pre-publication menu: after publication the only
    dispositions are corrected and withdrawn. Re-publishing would mint a second
    tag and event that permanently record a correction as a first publication;
    parking would flip `status` off `published` and silence the drift lint for
    the surviving tag."""
    publish.mark_published(green_vault, "brief", date="2026-08-01")
    head = _head(green_vault)
    capsys.readouterr()

    assert main([verb, "brief", "--vault", str(green_vault)]) == 2

    error = capsys.readouterr().err
    assert "mark-corrected" in error
    assert "mark-withdrawn" in error
    assert _status(green_vault) == "published"
    events_at = [
        event["at"] for event in events.verified_checks(_note(green_vault).read_text())
    ]
    assert events_at == ["2026-08-01"]
    assert _tags(green_vault) == ["published/brief-2026-08-01"]
    assert _head(green_vault) == head
