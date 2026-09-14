"""The `finding` verb: the review-record writer (spec §3, §6 factored-verification).

`finding` is a thin CLI wrapper over ``inbox.append_entry`` — the mechanism
factcheck-draft's adjudicated findings write through, so prose never touches
the review queue directly.
"""

from pathlib import Path

import pytest

from research_vault import AGENT_ACTOR, inbox
from research_vault.__main__ import main

REPO = Path(__file__).resolve().parents[1]
VERIFY_CITATIONS_SKILL = REPO / "skills" / "verify-citations" / "SKILL.md"
FACTCHECK_DRAFT_SKILL = REPO / "skills" / "factcheck-draft" / "SKILL.md"


def _queue_bytes(vault):
    return (
        (vault / inbox.INBOX_PATH).read_bytes()
        if (vault / inbox.INBOX_PATH).exists()
        else b""
    )


def test_finding_appends_an_open_entry_and_prints_its_id(tmp_vault):
    code = main(
        [
            "finding",
            "factcheck",
            "smith2020#^c-11111111",
            "UNMATCHED",
            "mismatch — paraphrase overstates the cited effect size",
            "--vault",
            str(tmp_vault),
        ]
    )

    assert code == 0
    entries = inbox.open_entries(tmp_vault)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.check == "factcheck"
    assert entry.target == "smith2020#^c-11111111"
    assert entry.result == "UNMATCHED"
    assert entry.reason == "mismatch — paraphrase overstates the cited effect size"
    assert entry.actor == AGENT_ACTOR


def test_finding_accepts_an_explicit_actor_and_date(tmp_vault):
    code = main(
        [
            "finding",
            "factcheck",
            "smith2020#^c-11111111",
            "SKIPPED",
            "no-identifier — cited managed region absent",
            "--vault",
            str(tmp_vault),
            "--actor",
            "human:eran",
            "--date",
            "2026-08-19",
        ]
    )

    assert code == 0
    entry = inbox.open_entries(tmp_vault)[0]
    assert entry.actor == "human:eran"
    assert entry.date == "2026-08-19"


def test_finding_refuses_an_unregistered_check_id(tmp_vault, capsys):
    code = main(
        [
            "finding",
            "bogus-check",
            "smith2020",
            "UNMATCHED",
            "mismatch",
            "--vault",
            str(tmp_vault),
        ]
    )

    assert code == 2
    assert "check" in capsys.readouterr().err
    assert _queue_bytes(tmp_vault) == b""


def test_finding_refuses_an_unregistered_reason_code(tmp_vault, capsys):
    code = main(
        [
            "finding",
            "factcheck",
            "smith2020#^c-11111111",
            "UNMATCHED",
            "invented-code — not in the registry",
            "--vault",
            str(tmp_vault),
        ]
    )

    assert code == 2
    assert capsys.readouterr().err
    assert _queue_bytes(tmp_vault) == b""


def test_finding_refuses_a_malformed_date(tmp_vault, capsys):
    code = main(
        [
            "finding",
            "factcheck",
            "smith2020#^c-11111111",
            "UNMATCHED",
            "mismatch",
            "--vault",
            str(tmp_vault),
            "--date",
            "not-a-date",
        ]
    )

    assert code == 2
    assert capsys.readouterr().err
    assert _queue_bytes(tmp_vault) == b""


def test_finding_rejects_an_out_of_vocabulary_result(tmp_vault):
    with pytest.raises(SystemExit):
        main(
            [
                "finding",
                "factcheck",
                "smith2020#^c-11111111",
                "MAYBE",
                "mismatch",
                "--vault",
                str(tmp_vault),
            ]
        )


def test_finding_rejects_matched_for_any_check_id(tmp_vault):
    """No caller ever legitimately writes MATCHED through this verb — only a
    genuine deterministic check mints a `verified` event, and factcheck's own
    doctrine (factcheck-draft/SKILL.md) is that a clean adjudication writes
    nothing. Excluded from argparse's own `choices`, so this is a SystemExit,
    the same shape as any other out-of-vocabulary result."""
    with pytest.raises(SystemExit):
        main(
            [
                "finding",
                "factcheck",
                "smith2020#^c-11111111",
                "MATCHED",
                "matched",
                "--vault",
                str(tmp_vault),
            ]
        )
    assert _queue_bytes(tmp_vault) == b""


def test_finding_refuses_skipped_for_a_deterministic_check_id(tmp_vault, capsys):
    """SKIPPED is spec §6's automatic-only result for the deterministic
    checks — never agent- or prose-settable. Only `factcheck`'s own
    budget-cap bookkeeping may write it through this verb."""
    code = main(
        [
            "finding",
            "quote",
            "smith2020#^c-11111111",
            "SKIPPED",
            "no-identifier — no extractable source text",
            "--vault",
            str(tmp_vault),
        ]
    )

    assert code == 2
    assert "SKIPPED" in capsys.readouterr().err
    assert _queue_bytes(tmp_vault) == b""


def test_finding_still_allows_skipped_for_factcheck(tmp_vault):
    """The per-check-id guard must not be blanket — factcheck's skipped-set
    record is spec-required and has no other mechanism that could write it."""
    code = main(
        [
            "finding",
            "factcheck",
            "projects/brief",
            "SKIPPED",
            "budget-cap — 1 claim deferred: smith2020#^c-1",
            "--vault",
            str(tmp_vault),
        ]
    )

    assert code == 0
    assert inbox.open_entries(tmp_vault)[0].result == "SKIPPED"


def test_finding_refuses_a_same_day_retry_with_a_different_result(tmp_vault, capsys):
    """Reproduces the reviewed defect exactly, through the CLI, using the
    sequence factcheck-draft/SKILL.md itself would produce: a claim that was
    UNREACHABLE on one pass and UNMATCHED on a same-day retry. Because
    ``inbox.finding_id`` does not fold `result` into the id, the two calls
    would otherwise compute an identical id, leaving both rows permanently
    unacknowledgeable (``append_ack`` refuses whenever more than one open
    finding row shares an id). The second call must refuse instead of
    silently colliding, and the first entry must stay genuinely ackable."""
    claim = "smith2020#^c-11111111"
    first = main(
        [
            "finding",
            "factcheck",
            claim,
            "UNREACHABLE",
            "outage — network unavailable",
            "--vault",
            str(tmp_vault),
            "--date",
            "2026-08-21",
        ]
    )
    assert first == 0
    before = inbox.open_entries(tmp_vault)
    assert len(before) == 1
    first_id = before[0].id

    second = main(
        [
            "finding",
            "factcheck",
            claim,
            "UNMATCHED",
            "mismatch — overstates the cited effect",
            "--vault",
            str(tmp_vault),
            "--date",
            "2026-08-21",
        ]
    )

    assert second == 2
    assert "already recorded" in capsys.readouterr().err
    entries = inbox.open_entries(tmp_vault)
    assert len(entries) == 1
    assert entries[0].id == first_id
    assert entries[0].result == "UNREACHABLE"

    # The surviving entry must remain genuinely ackable -- the defect this
    # reproduces is that a silent second row would make it refuse forever.
    ack_code = main(
        [
            "ack",
            first_id,
            "--vault",
            str(tmp_vault),
            "--reason",
            "manual — outage resolved, rechecked by hand",
            "--actor",
            "human:eran",
        ]
    )
    assert ack_code == 0
    assert inbox.open_entries(tmp_vault) == []


def test_record_finding_refuses_with_exit_2_and_a_retry_must_match_on_every_field(
    tmp_vault,
):
    """Every refusal answers 2 (never another code): MATCHED, SKIPPED outside
    factcheck, and a same-id retry whose RESULT differs while the reason and
    everything else match -- that is the collision the id cannot carry, not
    a duplicate."""
    from research_vault import Result
    from research_vault.__main__ import record_finding

    code, detail = record_finding(
        tmp_vault, "quote", "smith2020", Result.MATCHED, "matched"
    )
    assert code == 2
    assert detail.startswith("MATCHED never files a finding")
    code, detail = record_finding(
        tmp_vault, "quote", "smith2020", Result.SKIPPED, "no-identifier — nothing"
    )
    assert code == 2
    assert detail.startswith("SKIPPED is automatic-only for 'quote'")
    first = record_finding(
        tmp_vault,
        "factcheck",
        "smith2020#^c-11111111",
        Result.UNREACHABLE,
        "outage — network unavailable",
        date="2026-08-21",
    )
    assert first[0] == 0
    code, detail = record_finding(
        tmp_vault,
        "factcheck",
        "smith2020#^c-11111111",
        Result.UNMATCHED,
        "outage — network unavailable",
        date="2026-08-21",
    )
    assert code == 2
    assert "already recorded with different content" in detail
    assert len(inbox.open_entries(tmp_vault)) == 1
    code, detail = record_finding(
        tmp_vault, "quote", "smith2020", Result.UNMATCHED, "mismatch — x", date="soon"
    )
    assert (code, detail) == (2, "date must be a YYYY-MM-DD calendar date")


def test_finding_retry_with_the_same_target_hash_is_idempotent(tmp_vault):
    args = [
        "finding",
        "factcheck",
        "projects/brief",
        "SKIPPED",
        "budget-cap — 2 claims deferred: smith2020#^c-1, smith2020#^c-2",
        "--vault",
        str(tmp_vault),
        "--target-hash",
        "aa11bb22",
    ]

    first = main(args)
    second = main(args)

    assert first == 0 == second
    entries = inbox.open_entries(tmp_vault)
    assert len(entries) == 1


def test_finding_refiles_when_the_target_hash_changes(tmp_vault):
    base = [
        "finding",
        "factcheck",
        "projects/brief",
        "SKIPPED",
        "budget-cap — 1 claim deferred: smith2020#^c-1",
        "--vault",
        str(tmp_vault),
    ]

    main([*base, "--target-hash", "aa11"])
    main([*base, "--target-hash", "bb22"])

    entries = inbox.open_entries(tmp_vault)
    assert {entry.target_hash for entry in entries} == {"aa11", "bb22"}
    assert len(entries) == 2


def test_two_distinct_skipped_sets_same_day_stay_separately_acknowledgeable(tmp_vault):
    """The sha256-as-target-hash design exists so two genuinely different
    skipped sets, filed on the same target on the same day, get distinct
    finding ids (``finding_id`` appends ``/scope-<hash>`` whenever a target
    hash is supplied) — proving the ack-ambiguity defect a same-day,
    same-target rerun would otherwise hit is actually closed, not merely
    assumed closed by design."""
    base = [
        "finding",
        "factcheck",
        "projects/brief",
        "SKIPPED",
        "budget-cap — claims deferred this pass",
        "--vault",
        str(tmp_vault),
    ]
    first_id = None
    for target_hash in ("sha256-aaaa", "sha256-bbbb"):
        code = main([*base, "--target-hash", target_hash])
        assert code == 0
        if first_id is None:
            first_id = inbox.open_entries(tmp_vault)[0].id

    entries = inbox.open_entries(tmp_vault)
    assert len(entries) == 2
    assert len({entry.id for entry in entries}) == 2

    ack_code = main(
        [
            "ack",
            first_id,
            "--vault",
            str(tmp_vault),
            "--reason",
            "manual — reviewed the first pass's skipped set",
            "--actor",
            "human:eran",
        ]
    )

    assert ack_code == 0
    remaining = inbox.open_entries(tmp_vault)
    assert len(remaining) == 1
    assert remaining[0].target_hash == "sha256-bbbb"


def test_finding_prints_an_id_the_ack_verb_can_reference(tmp_vault):
    code = main(
        [
            "finding",
            "factcheck",
            "smith2020#^c-11111111",
            "UNMATCHED",
            "mismatch",
            "--vault",
            str(tmp_vault),
        ]
    )
    assert code == 0
    entry = inbox.open_entries(tmp_vault)[0]

    ack_code = main(
        [
            "ack",
            entry.id,
            "--vault",
            str(tmp_vault),
            "--reason",
            "manual — accepted, wording will be tightened next revision",
            "--actor",
            "human:eran",
        ]
    )

    assert ack_code == 0
    assert inbox.open_entries(tmp_vault) == []


# --- skill content -----------------------------------------------------


def test_verify_citations_skill_routes_every_mechanical_act_through_a_verb():
    text = VERIFY_CITATIONS_SKILL.read_text(encoding="utf-8")
    for token in (
        "research_vault verify",
        "--surface",
        "MATCHED",
        "UNMATCHED",
        "UNREACHABLE",
        "SKIPPED",
        "outage",
    ):
        assert token in text, f"verify-citations/SKILL.md never mentions {token!r}"


def test_factcheck_draft_skill_names_its_bounds_and_never_blocks():
    text = FACTCHECK_DRAFT_SKILL.read_text(encoding="utf-8")
    for token in (
        "research_vault factcheck",
        "30",
        "--cap",
        "finding",
        "never block",
        "MATCHED",
        "UNMATCHED",
        "UNREACHABLE",
        "SKIPPED",
        "budget-cap",
        # Each of the three below occurs exactly once in the skill, so deleting
        # the paragraph it belongs to fails here. Every token above it recurs
        # elsewhere in the file and so pins vocabulary, not any one paragraph.
        "role separation is not independent error processes",
        "SKIPPED applied to reading",
        "validates declarations, not their truth",
    ):
        assert token in text, f"factcheck-draft/SKILL.md never mentions {token!r}"
