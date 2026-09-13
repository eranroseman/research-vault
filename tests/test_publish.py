"""The publish surface: gate-flag verbs, dispositions, and the ack verb (spec §6).

Every vault built here is deliberately bibliography-free, so the publish gate
runs its real network-capable transaction without ever leaving the machine:
absent `system/bibliography.json` means no bibliography entries to route
through Crossref. The disposition verbs therefore need no ``--offline``
escape hatch — spec §6 forbids synthetic offline outcomes from minting
trust, and one does not exist to be misused.
"""

import datetime as datetime_lib
import importlib.util
import io
import json
import re
import subprocess
import sys
import types
from pathlib import Path

import pytest

from research_vault import Result, events, frontmatter, inbox, lints, publish
from research_vault.__main__ import main
from research_vault.outcome import Outcome
from research_vault.verify import _projection_identity

REPO = Path(__file__).resolve().parents[1]
STOP_HOOK = REPO / "hooks" / "stop_publish_gate.py"
PUBLISH_SKILL = REPO / "skills" / "publish" / "SKILL.md"
FLAG = Path(".research-vault") / "publish-pending.json"

PROJECT_FRONTMATTER = """---
title: "Evidence brief"
type: "project"
status: "draft"
generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}
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


def _tag_clock(monkeypatch, *times: str) -> None:
    """Pin the whole UTC clock to named ``HHMMSS`` times, one read per disposition.

    The *clock* is pinned, not the time half of the tag: a helper that stubbed
    only the time could not see the date half coming from somewhere else,
    which is exactly how a local-day/UTC-time mismatch hid once already.
    Popping from a list makes an unexpected extra read raise rather than
    silently reuse an instant and mint a colliding tag.
    """
    remaining = [
        datetime_lib.datetime.strptime(stamp, "%H%M%S").replace(
            year=2026, month=1, day=1, tzinfo=datetime_lib.UTC
        )
        for stamp in times
    ]
    monkeypatch.setattr(publish, "_utc_now", lambda: remaining.pop(0))


def _note(vault: Path, project: str = "brief") -> Path:
    return vault / "projects" / project / "draft.md"


def _status(vault: Path, project: str = "brief") -> str:
    data, _ = frontmatter.parse(_note(vault, project).read_text())
    return data["status"]


def _build_vault(
    root: Path, claim: str, bibliography=None, name: str = "brief"
) -> Path:
    for folder in (
        "inbox",
        "literatures",
        "wiki",
        "log",
        "projects",
        "system",
        "system/templates",
        "system/bases",
    ):
        (root / folder).mkdir()
    (root / "index.md").write_text('---\nokf_version: "0.2"\n---\n# Knowledge bundle\n')
    (root / "log.md").write_text("# Log\n")
    (root / "wiki" / "index.md").write_text("# Wiki index\n")
    (root / "inbox" / "review-queue.md").write_text('---\ntype: "review-queue"\n---\n')
    if bibliography is not None:
        (root / "system" / "bibliography.json").write_text(json.dumps(bibliography))
    project = root / "projects" / name
    project.mkdir()
    (project / "draft.md").write_text(PROJECT_FRONTMATTER + claim)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "project vault"], cwd=root, check=True)
    (root / ".research-vault").mkdir()
    return root


@pytest.fixture
def green_vault(tmp_path):
    """A vault whose publish surface is green with no network traffic at all."""
    return _build_vault(tmp_path, UNCITED_CLAIM)


@pytest.fixture
def blocked_vault(tmp_path):
    """A vault blocked by a closing check: a citation key outside the bibliography."""
    return _build_vault(tmp_path, GHOST_CLAIM)


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

    assert "UNMATCHED citation-key ghost2020" in capsys.readouterr().out
    assert _status(blocked_vault) == "draft"
    assert _tags(blocked_vault) == []
    assert _head(blocked_vault) == before
    assert (blocked_vault / FLAG).exists()


def test_mark_published_proceeds_once_a_blocking_entry_carries_a_standing_ack(
    blocked_vault,
):
    # verify hashes the target before it projects (candidate-bound), so the
    # finding it files carries the draft as the author left it; the stamp is
    # verify's own write, and `ack` clears it (open point 09), restoring the
    # very state the ack is scoped to. The gate run inside `mark-published`
    # files a second row over the stamped draft — acknowledge the first.
    assert main(["verify", "--vault", str(blocked_vault), "--surface", "publish"]) == 1
    assert main(["mark-published", "brief", "--vault", str(blocked_vault)]) == 1
    standing = next(
        entry
        for entry in inbox.open_entries(blocked_vault)
        if entry.check == "citation-key" and entry.result == "UNMATCHED"
    )

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
    # Non-markdown: structure.check_note_frontmatter only sweeps *.md, and any
    # *.md under projects/<name>/ must itself carry type: "project" (folder
    # derivation) — a second one would instead trip project_note()'s
    # exactly-one-project-note rule before this gate is ever reached.
    (green_vault / "projects" / "brief" / "appendix.txt").write_text("Appendix\n")
    before = _head(green_vault)

    assert main(["mark-published", "brief", "--vault", str(green_vault)]) == 2

    assert "projects/brief/appendix.txt" in capsys.readouterr().err
    assert _status(green_vault) == "draft"
    assert _tags(green_vault) == []
    assert _head(green_vault) == before


def test_an_empty_directory_is_clean_to_both_the_publisher_and_the_drift_lint(
    green_vault, monkeypatch
):
    """One definition of "clean", on both sides of the same moment.

    Git tracks no directory of its own, so a bare empty folder under a project
    carries no content. `_require_clean_project` already read it that way and
    published; `_project_differs` counted it as a difference and reported the
    fresh tag as drifted the instant it was minted — a project the publisher
    called clean and the lint called dirty, seconds apart.
    """
    _tag_clock(monkeypatch, "120000")
    (green_vault / "projects" / "brief" / "scratch").mkdir()

    outcome = publish.mark_published(green_vault, "brief", date="2026-08-01")

    assert outcome.tag == "published/brief-2026-08-01-120000"
    assert lints.lint_published_drift(green_vault) == []


# --- mark-parked, correction, withdrawal -----------------------------------


def test_mark_parked_sets_status_parked_and_nothing_else(green_vault):
    before = _head(green_vault)

    assert main(["mark-parked", "brief", "--vault", str(green_vault)]) == 0

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


def test_mark_corrected_mints_a_new_event_and_tag_and_keeps_the_original(
    green_vault, monkeypatch
):
    _tag_clock(monkeypatch, "090000", "140000")
    first = publish.mark_published(green_vault, "brief", date="2026-08-01")
    assert first.tag == "published/brief-2026-08-01-090000"

    second = publish.mark_corrected(green_vault, "brief", date="2026-08-09")

    assert second.status == "corrected"
    assert second.tag == "published/brief-2026-08-09-140000"
    text = _note(green_vault).read_text()
    assert frontmatter.parse(text)[0]["status"] == "corrected"
    assert [event["at"] for event in events.verified_checks(text)] == [
        "2026-08-01",
        "2026-08-09",
    ]
    assert _tags(green_vault) == [
        "published/brief-2026-08-01-090000",
        "published/brief-2026-08-09-140000",
    ]
    first_commit = _git(
        green_vault, "rev-parse", "published/brief-2026-08-01-090000^{commit}"
    ).strip()
    assert _git(green_vault, "rev-parse", "HEAD^").strip() == first_commit


def test_a_corrected_project_stays_watched_across_the_whole_lifecycle(
    green_vault, monkeypatch
):
    """A correction must not end drift watching (acceptance finding F-2).

    `lint_published_drift` keyed on `status == "published"`, and
    `mark-corrected` writes `corrected` — so the lint stopped watching the
    project at the moment a corrections regime needs it watched most, while
    this skill refuses post-publication `mark-parked` precisely because that flip
    blinds the lint. The comparison basis is each project's *newest* tag: the
    original tag survives (ADR 0003) and the corrected tree differs from it by
    construction, so comparing against it would report every legitimate
    correction as drift.
    """
    _tag_clock(monkeypatch, "090000", "140000", "173000")
    publish.mark_published(green_vault, "brief", date="2026-08-01")
    publish.mark_corrected(green_vault, "brief", date="2026-08-09")

    assert _status(green_vault) == "corrected"
    assert _tags(green_vault) == [
        "published/brief-2026-08-01-090000",
        "published/brief-2026-08-09-140000",
    ]
    # Clean against the newest tag, and the surviving original raises nothing.
    assert lints.lint_published_drift(green_vault) == []

    note = _note(green_vault)
    note.write_text(note.read_text() + "\nEdited after the correction.\n")

    assert [out.target for out in lints.lint_published_drift(green_vault)] == [
        "path-bytes:projects/brief"
    ]

    # Correcting again re-bases the comparison on the newest tag, so the drift
    # the lint just reported is closed by a correction rather than by silence.
    _git(green_vault, "add", "-A")
    _git(green_vault, "commit", "-q", "-m", "edit after correction")
    publish.mark_corrected(green_vault, "brief", date="2026-08-20")

    assert _tags(green_vault)[-1] == "published/brief-2026-08-20-173000"
    assert lints.lint_published_drift(green_vault) == []


def test_mark_corrected_refuses_a_tag_that_already_exists(green_vault, monkeypatch):
    """The guard stays, and now fires only on a genuine collision.

    Before the tag carried a time, this refusal was every same-day correction.
    It now takes two dispositions landing on the identical second — or a tag
    written by hand — and it must still refuse rather than move an existing
    tag, which ADR 0003 forbids.
    """
    _tag_clock(monkeypatch, "090000", "090000")
    publish.mark_published(green_vault, "brief", date="2026-08-01")

    with pytest.raises(publish.PublishError, match="published/brief-2026-08-01-090000"):
        publish.mark_corrected(green_vault, "brief", date="2026-08-01")

    assert _status(green_vault) == "published"
    assert _tags(green_vault) == ["published/brief-2026-08-01-090000"]


def test_a_project_publishes_and_corrects_n_times_on_one_day(green_vault, monkeypatch):
    """The scenario the time component exists for: a morning publication, an
    afternoon correction when a retraction notice lands, and another that
    evening — all on one calendar day, all standing, none deleted (ADR 0003),
    and the drift lint comparing against the newest of them.
    """
    _tag_clock(monkeypatch, "090000", "141500", "203000")

    first = publish.mark_published(green_vault, "brief", date="2026-08-01")
    second = publish.mark_corrected(green_vault, "brief", date="2026-08-01")
    third = publish.mark_corrected(green_vault, "brief", date="2026-08-01")

    assert [first.status, second.status, third.status] == [
        "published",
        "corrected",
        "corrected",
    ]
    minted = [first.tag, second.tag, third.tag]
    assert minted == [
        "published/brief-2026-08-01-090000",
        "published/brief-2026-08-01-141500",
        "published/brief-2026-08-01-203000",
    ]
    # Every tag survives, and plain lexicographic order is chronological order
    # within the day — which is what `_newest_published_tags` relies on.
    assert _tags(green_vault) == minted
    assert sorted(minted) == minted
    assert lints._newest_published_tags(green_vault) == {
        "brief": "published/brief-2026-08-01-203000"
    }
    assert lints.lint_published_drift(green_vault) == []
    assert [
        event["at"] for event in events.verified_checks(_note(green_vault).read_text())
    ] == ["2026-08-01", "2026-08-01", "2026-08-01"]


def test_the_tag_pattern_still_yields_the_project_name_as_group_one():
    """`published_tags` and `_newest_published_tags` both key on `group(1)`.
    The trailing time gives the greedy `.+` one more thing to swallow, so a
    project whose own name ends in something date-shaped is the case that
    would misattribute every tag it owns."""
    simple = lints.PUBLISHED_TAG.match("published/brief-2026-08-01-090000")
    nested = lints.PUBLISHED_TAG.match(
        "published/brief-2026-08-01-090000-2026-08-02-141500"
    )

    assert simple is not None
    assert simple.group(1) == "brief"
    assert nested is not None
    assert nested.group(1) == "brief-2026-08-01-090000"
    assert lints.PUBLISHED_TAG.match("published/brief-2026-08-01") is None


def test_newest_published_tag_discriminates_within_one_day(green_vault):
    """F-2's ordering, regraded for the time component: `max` over a plain
    lexicographic sort has to pick the later of two tags minted on one day, or
    the drift lint compares a corrected project against a superseded tree and
    reports every correction as drift."""
    for stamp in ("2026-08-01-090000", "2026-08-01-203000", "2026-07-31-235959"):
        _git(green_vault, "tag", f"published/brief-{stamp}")

    assert lints._newest_published_tags(green_vault) == {
        "brief": "published/brief-2026-08-01-203000"
    }


def test_the_cli_passes_date_through_to_every_dated_disposition(
    green_vault, monkeypatch
):
    """F-3: with no `--date`, the CLI could only ever name today, so a project
    published and then corrected on one day was unrepairable — the correction's
    tag collided with the publication's and no flag could name another day. The
    date rides as the tag's own ISO suffix, never as an extra suffix appended to
    it, which is what keeps `PUBLISHED_TAG` and the newest-tag ordering intact.
    """
    _tag_clock(monkeypatch, "090000", "140000", "203000")
    published = main(
        ["mark-published", "brief", "--vault", str(green_vault), "--date", "2026-08-01"]
    )
    corrected = main(
        ["mark-corrected", "brief", "--vault", str(green_vault), "--date", "2026-08-02"]
    )
    withdrawn = main(
        ["mark-withdrawn", "brief", "--vault", str(green_vault), "--date", "2026-08-03"]
    )

    assert (published, corrected, withdrawn) == (0, 0, 0)
    assert _tags(green_vault) == [
        "published/brief-2026-08-01-090000",
        "published/brief-2026-08-02-140000",
    ]
    text = _note(green_vault).read_text()
    assert [event["at"] for event in events.verified_checks(text)] == [
        "2026-08-01",
        "2026-08-02",
    ]
    assert (green_vault / "log" / "2026-08-03.md").is_file()


@pytest.mark.parametrize("verb", ["mark-published", "mark-corrected", "mark-withdrawn"])
@pytest.mark.parametrize("supplied", ["20260801", "2026-13-01", "../../escape"])
def test_a_dated_disposition_refuses_a_bad_date_before_writing_anything(
    green_vault, capsys, verb, supplied
):
    """The date names a tag suffix, a `verified` event stamp, and a `log/` day
    file, so an unchecked one could mint a tag `PUBLISHED_TAG` cannot order or
    write a day file outside `log/`.

    Every dated verb, because exit 2's documented meaning is that the CLI
    carried the disposition out *not at all*. `mark-withdrawn` validated its
    date only once `_append_log` reached it — after the status write — so a
    refused withdrawal still flipped the note to `withdrawn`, the one status
    `lint_published_drift` deliberately stops watching, and nothing said so.
    """
    expected_status, expected_tags = "draft", []
    if verb != "mark-published":
        expected_tags = [publish.mark_published(green_vault, "brief").tag]
        expected_status = "published"
    capsys.readouterr()

    code = main([verb, "brief", "--vault", str(green_vault), "--date", supplied])

    assert code == 2
    assert "YYYY-MM-DD" in capsys.readouterr().err
    assert _status(green_vault) == expected_status
    assert _tags(green_vault) == expected_tags
    assert sorted((green_vault / "log").glob("*.md")) == []


def test_a_publication_tag_takes_both_halves_from_one_utc_clock_read(
    green_vault, monkeypatch
):
    """The tag's date and time must come from ONE timezone-aware UTC read.

    A local calendar day beside a UTC time inverts same-day ordering on any
    machine off UTC: at UTC+10 a 09:00 publication tags `...-230000` and a
    12:00 correction tags `...-020000`, so `max()` returns the superseded tag
    and `lint_published_drift` reports every legitimate correction as drift —
    the F-2 failure the uniform time component exists to prevent.

    This test pins the clock rather than the tag string, which is the whole
    point: helpers that stub the time half cannot see where the date half came
    from, and that is how the mismatch survived a green suite.

    The fake replaces `publish`'s own `datetime` name binding (not the shared
    `datetime` module — patching that leaks into every other module's `.now()`
    calls active during the same test and inflates the read count past 1,
    confirmed live 2026-08-22), so only `_publish`'s own clock read is
    intercepted. It carries both `.timezone` and `.UTC`: this test's original
    fake had only `.timezone`, which broke the moment production code was
    rewritten from `datetime.timezone.utc` to the 3.11 `datetime.UTC` alias
    (target-version bump, requires-python >=3.11) — the property under test is
    the UTC read itself, not which spelling names it.
    """
    reads = []
    instant = datetime_lib.datetime(2026, 8, 1, 23, 0, 0, tzinfo=datetime_lib.UTC)

    def one_utc_read(tz=None):
        reads.append(tz)
        return instant

    def no_local_day():
        raise AssertionError("the local calendar day must never reach a tag")

    monkeypatch.setattr(
        publish,
        "datetime",
        types.SimpleNamespace(
            datetime=types.SimpleNamespace(now=one_utc_read),
            date=types.SimpleNamespace(
                today=no_local_day, fromisoformat=datetime_lib.date.fromisoformat
            ),
            timezone=datetime_lib.timezone,
            UTC=datetime_lib.UTC,
        ),
    )

    outcome = publish.mark_published(green_vault, "brief")

    # Exactly one read, and it named an explicit, UTC-equivalent tzinfo -- not
    # None (naive local time), not a local-offset tzinfo, whichever spelling
    # production code uses to name it.
    assert len(reads) == 1
    assert reads[0] is not None
    assert reads[0].utcoffset(None) == datetime_lib.timedelta(0)
    assert outcome.tag == "published/brief-2026-08-01-230000"


def test_mark_parked_refuses_a_date_flag_rather_than_discarding_it(green_vault):
    """Parking writes a status and nothing dated, so `--date` is not its flag —
    and a flag a verb would silently discard is its own defect."""
    with pytest.raises(SystemExit):
        main(
            [
                "mark-parked",
                "brief",
                "--vault",
                str(green_vault),
                "--date",
                "2026-08-01",
            ]
        )


def test_mark_withdrawn_writes_status_and_logs_without_deleting_the_tag(
    green_vault, monkeypatch
):
    _tag_clock(monkeypatch, "090000", "140000")
    publish.mark_published(green_vault, "brief", date="2026-08-01")
    head = _head(green_vault)

    assert main(["mark-withdrawn", "brief", "--vault", str(green_vault)]) == 0

    text = _note(green_vault).read_text()
    assert frontmatter.parse(text)[0]["status"] == "withdrawn"
    assert _tags(green_vault) == ["published/brief-2026-08-01-090000"]
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
        if entry.check == "citation-key" and entry.result == "UNMATCHED"
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
        ("research_vault/0.1.0", "manual — the CLI cannot consent for a human"),
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
        "mark-parked",
        "ack",
        "MATCHED",
        "UNMATCHED",
        "UNREACHABLE",
        "SKIPPED",
        "keep-draft",
        "discard",
    ):
        assert token in text, f"publish/SKILL.md never mentions {token!r}"


def test_publish_skill_announces_the_armed_gate_before_the_first_command():
    """The intro must warn that this flow runs through a Stop-hook gate, and
    must not say the gate is armed: it is inert until `arm-publish` sets the
    flag. Drop the warning and a person meets the hook at their first refusal;
    claim an armed gate up front and the skill describes state the vault does
    not have at that moment.
    """
    text = PUBLISH_SKILL.read_text(encoding="utf-8")
    intro = text[: text.index("## Orient")]

    assert "Say this before the first command" in intro
    assert "runs through an armed gate" in intro
    assert "`arm-publish` sets a state flag the Stop hook reads" in intro
    # The false-state half of the rule, which no presence check can enforce.
    assert "the gate is armed" not in intro


def test_publish_skill_answers_the_disposition_rationalizations():
    """The two seeded rows name this skill's live consent failures: spoken
    assent mistaken for a written `ack`, and an outage mistaken for a pass.
    Both are excuses that arrive immediately before an irreversible act, so a
    table missing either row no longer answers the rationalization it exists
    to catch. The answering cells are pinned too — a row whose answer drifts
    is worse than an absent row, because it still reads as a ruling.
    """
    text = PUBLISH_SKILL.read_text(encoding="utf-8")

    assert "## Rationalizations, answered" in text
    # The two ported seed rows, verbatim from the survey.
    assert "They said go ahead so the ack is covered." in text
    assert "UNREACHABLE is basically fine." in text
    # Each row answers with a rule this skill already enforces, never a new one.
    assert "Consent spoken in conversation writes nothing." in text
    assert "It holds the gate." in text


def test_publish_skill_states_the_tag_grammar_and_that_same_day_corrections_work():
    """The tag shape is a contract a person reads back off this skill, and the
    grammar carries a UTC time precisely so a same-day correction is no longer
    a refusal — prose still implying it was would send people away for a day.
    """
    text = PUBLISH_SKILL.read_text(encoding="utf-8")

    assert "`published/<project>-<date>-<time>`" in text
    assert "A correction on the day of publication just works" in text
    assert "`--date` never supplies the time" in text


def _minting_check_ids() -> set[str]:
    """The check ids `verify` actually mints a `verified` event for, from itself.

    Derived rather than transcribed: a prose claim about durable state is only
    worth testing against the code that writes it, and `_projection_identity`
    is that code (`verify._apply_state_transitions`).
    """
    minting = set()
    for check in inbox.CHECK_IDS:
        # A per-claim quote outcome needs an anchored target and a comparison
        # target; every other check id projects on its bare target or not at all.
        target = "smith2020#^c-88888888" if check == "quote" else "smith2020"
        outcome = Outcome(
            check, target, Result.MATCHED, "matched", {"target": "managed-region"}
        )
        if _projection_identity(outcome) is not None:
            minting.add(check)
    return minting


def test_publish_skill_promises_an_event_only_for_the_check_ids_that_mint_one():
    """The MATCHED row promised a `verified` event for every check that passes.

    False for two of this surface's own closing checks: `citation-key` and
    `evidence-layer` mint nothing, so a person told "the CLI appends a
    `verified` event" would go looking for durable proof that was never
    written — the "no skill promises verification it didn't run" constraint,
    and the correction `verify-citations` already carries.
    """
    text = PUBLISH_SKILL.read_text(encoding="utf-8")
    # Padding-tolerant: mdformat owns skills/ and pads table cells to align
    # columns, so an exact-prefix match would break on the next reflow. The row's
    # CONTENT is what this test is about, and every assertion below still reads it.
    row = next(
        line for line in text.splitlines() if re.match(r"\|\s*MATCHED\s*\|", line)
    )

    assert _minting_check_ids() == {"update-notice", "quote"}
    for check in sorted(_minting_check_ids()):
        assert f"`{check}`" in row, f"the MATCHED row never names minting id {check!r}"
    # The publish surface's other two closing checks mint nothing, and the row
    # has to say so rather than leaving a blanket promise standing.
    for check in ("citation-key", "evidence-layer"):
        assert f"`{check}`" in row, f"the MATCHED row never names {check!r}"
    assert "mint nothing" in row
    assert "Passes; the CLI appends a `verified` event." not in text
    # The project-level event `mark-published`/`mark-corrected` mint is real and
    # distinct from the per-check ones; the row must not collapse the two.
    assert "`publish`" in row


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
    citation_key_lines = [line for line in lines[1:] if "ghost2020" in line]
    assert len(citation_key_lines) == 1
    finding_id = citation_key_lines[0].split()[0]
    assert finding_id.startswith("citation-key/")

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


@pytest.mark.parametrize("verb", ["mark-published", "mark-parked"])
def test_the_day_one_menu_refuses_an_already_published_project(
    green_vault, capsys, monkeypatch, verb
):
    """§6's day-one menu is the pre-publication menu: after publication the only
    dispositions are corrected and withdrawn. Re-publishing would mint a second
    tag and event that permanently record a correction as a first publication;
    parking would flip `status` off `published` and silence the drift lint for
    the surviving tag."""
    _tag_clock(monkeypatch, "090000")
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
    assert _tags(green_vault) == ["published/brief-2026-08-01-090000"]
    assert _head(green_vault) == head


_STATUS_NOTE = '---\ntitle: "Evidence brief"\nstatus: "draft"\n---\nbody\n'


@pytest.mark.parametrize(
    ("note_text", "refusal"),
    [
        ("no frontmatter at all\n", "has no frontmatter"),
        ("", "has no frontmatter"),
        ('---\ntitle: "Evidence brief"\nstatus: "draft"\n', "unterminated"),
        ('---\ntitle: "Evidence brief"\n---\nbody\n', "found 0"),
        ('---\nstatus: "draft"\nstatus: "parked"\n---\nbody\n', "found 2"),
    ],
    ids=["no-frontmatter", "empty", "unterminated", "no-status", "two-statuses"],
)
def test_set_status_refuses_a_note_it_cannot_rewrite_in_place(note_text, refusal):
    """A disposition rewrites one line, so it must first prove that line exists.

    ``_set_status`` is the only writer of a project's ``status``, and it edits by
    line index rather than by re-serializing the frontmatter — the way it keeps
    every other byte of a human-authored note intact. That makes an absent,
    unterminated, missing or duplicated ``status`` an unwritable note, not a
    note to guess at: guessing would either move the status out of the
    frontmatter or leave a second one behind to contradict it.
    """
    with pytest.raises(publish.PublishError, match=refusal):
        publish._set_status(note_text, "published")


def test_set_status_refuses_a_status_its_own_quoting_would_corrupt():
    """The writer does not escape, so it verifies instead.

    ``_set_status`` emits ``status: "<value>"`` verbatim, which is exact for
    every disposition the module actually files. A backslash-bearing value would
    be unescaped again on read and come back as a different string, so the
    guard re-parses what it wrote and refuses rather than persist a status the
    vault would read as something else.
    """
    assert '\nstatus: "published"\n' in publish._set_status(_STATUS_NOTE, "published")

    with pytest.raises(publish.PublishError, match="did not round-trip"):
        publish._set_status(_STATUS_NOTE, r"back\\slash")


def test_retraction_ack_field_has_one_definition_site():
    from research_vault import publish

    skill = (
        REPO / "skills" / "evidence-conventions" / "SKILL.md"
    ).read_text()  # tests/test_publish.py names the root REPO
    assert f"[{publish.RETRACTION_ACK_FIELD}:: <code>" in skill
    assert publish.RETRACTION_ACK_FIELD == "retraction-ack"
