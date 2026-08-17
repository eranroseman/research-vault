import pytest

from harness_core import Result, inbox


def test_append_and_load(fixture_vault):
    inbox.append_entry(
        fixture_vault,
        "doi",
        "smith2020",
        Result.UNMATCHED,
        "mismatch — title differs",
        date="2026-08-16",
    )

    entries = inbox.load(fixture_vault)

    assert entries[-1].id == "doi/smith2020/2026-08-16"
    assert entries[-1].result == "UNMATCHED"
    assert entries[-1].reason.startswith("mismatch")
    line = (fixture_vault / "+" / "review-queue.md").read_text().splitlines()[-1]
    assert line.startswith("- [id:: doi/smith2020/2026-08-16]")


def test_entry_round_trips_bitemporal_dates(fixture_vault):
    inbox.append_entry(
        fixture_vault,
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "retracted — publisher notice found",
        date="2026-08-16",
        target_hash="aa11",
        notice_date="2025-03-04",
        detection_date="2026-08-16",
    )

    entry = inbox.load(fixture_vault)[-1]

    assert entry.target_hash == "aa11"
    assert entry.notice_date == "2025-03-04"
    assert entry.detection_date == "2026-08-16"


def test_entry_round_trips_brackets_field_like_text_and_literal_backslashes(
    fixture_vault,
):
    reason = "mismatch — found ] beside [actor:: human:other] in C:\\vault"
    inbox.append_entry(
        fixture_vault,
        "doi",
        "smith2020",
        Result.UNMATCHED,
        reason,
        date="2026-08-16",
    )

    entry = inbox.load(fixture_vault)[-1]

    assert entry.reason == reason


@pytest.mark.parametrize("reason", ["mismatched title", "manuality", "unknown"])
def test_append_entry_rejects_invalid_reason_prefix(fixture_vault, reason):
    with pytest.raises(ValueError, match="reason"):
        inbox.append_entry(
            fixture_vault,
            "doi",
            "smith2020",
            Result.UNMATCHED,
            reason,
            date="2026-08-16",
        )


def test_ack_requires_human_and_valid_reason(fixture_vault):
    entry = inbox.append_entry(
        fixture_vault,
        "doi",
        "smith2020",
        Result.UNMATCHED,
        "mismatch",
        date="2026-08-16",
    )

    with pytest.raises(ValueError, match="acknowledgment requires a human"):
        inbox.append_ack(
            fixture_vault,
            entry.id,
            "manual — verified by hand",
            actor="harness_core/0.1.0",
        )
    with pytest.raises(ValueError, match="reason"):
        inbox.append_ack(
            fixture_vault,
            entry.id,
            "manualized check",
            actor="human:eran",
        )

    inbox.append_ack(
        fixture_vault,
        entry.id,
        "manual — verified by hand",
        actor="human:eran",
    )

    assert inbox.is_acknowledged(fixture_vault, "doi", "smith2020")


def test_load_rejects_handwritten_finding_with_invalid_reason(fixture_vault):
    queue = fixture_vault / "+" / "review-queue.md"
    queue.write_text(
        "- [id:: doi/smith2020/2026-08-16] [check:: doi] "
        "[target:: smith2020] [result:: UNMATCHED] [date:: 2026-08-16] "
        "[actor:: harness_core/0.1.0] [reason:: invented]\n"
    )

    with pytest.raises(inbox.InboxError, match="line 1"):
        inbox.load(fixture_vault)


def test_load_rejects_handwritten_human_ack_with_invalid_reason(fixture_vault):
    queue = fixture_vault / "+" / "review-queue.md"
    queue.write_text(
        "- [ack:: doi/smith2020/2026-08-16] [actor:: human:eran] "
        "[reason:: manualized]\n"
    )

    with pytest.raises(inbox.InboxError, match="line 1"):
        inbox.load(fixture_vault)


def test_ack_scope_invalidated_by_hash_change(fixture_vault):
    entry = inbox.append_entry(
        fixture_vault,
        "quote",
        "smith2020#^c-11111111",
        Result.UNMATCHED,
        "fuzzy-quote",
        date="2026-08-16",
        target_hash="aa11",
    )
    inbox.append_ack(
        fixture_vault,
        entry.id,
        "manual — manual check ok",
        actor="human:eran",
        target_hash="aa11",
    )

    assert inbox.is_acknowledged(
        fixture_vault,
        "quote",
        "smith2020#^c-11111111",
        current_hash="aa11",
    )
    assert not inbox.is_acknowledged(
        fixture_vault,
        "quote",
        "smith2020#^c-11111111",
        current_hash="bb22",
    )


def test_changed_hash_recurrence_stays_open_in_summary_and_open_entries(fixture_vault):
    first = inbox.append_entry(
        fixture_vault,
        "quote",
        "smith2020#^c-11111111",
        Result.UNMATCHED,
        "fuzzy-quote",
        date="2026-08-16",
        target_hash="aa11",
    )
    inbox.append_ack(
        fixture_vault,
        first.id,
        "manual — manual check ok",
        actor="human:eran",
        target_hash="aa11",
    )
    changed = inbox.append_entry(
        fixture_vault,
        "quote",
        "smith2020#^c-11111111",
        Result.UNMATCHED,
        "fuzzy-quote",
        date="2026-08-16",
        target_hash="bb22",
    )

    assert inbox.open_entries(fixture_vault) == [changed]
    assert inbox.summary(fixture_vault) == {
        "unacknowledged": 1,
        "oldest": "2026-08-16",
    }
    assert not inbox.is_acknowledged(
        fixture_vault,
        "quote",
        "smith2020#^c-11111111",
    )


def test_none_hash_ack_requires_an_explicit_matching_none_hash(fixture_vault):
    finding = inbox.append_entry(
        fixture_vault,
        "doi",
        "smith2020",
        Result.UNMATCHED,
        "mismatch",
        date="2026-08-16",
        target_hash=None,
    )
    inbox.append_ack(
        fixture_vault,
        finding.id,
        "manual — wrong scope",
        actor="human:eran",
        target_hash="different",
    )

    assert not inbox.is_acknowledged(
        fixture_vault, "doi", "smith2020", current_hash=None
    )
    assert inbox.open_entries(fixture_vault) == [finding]

    inbox.append_ack(
        fixture_vault,
        finding.id,
        "manual — matching scope",
        actor="human:eran",
        target_hash=None,
    )

    assert inbox.is_acknowledged(fixture_vault, "doi", "smith2020", current_hash=None)
    assert inbox.open_entries(fixture_vault) == []


def test_one_human_ack_closes_all_same_hash_warning_entries(fixture_vault):
    correction = inbox.append_entry(
        fixture_vault,
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "warn-notice — correction",
        date="2026-08-01",
        target_hash="aa11",
    )
    inbox.append_entry(
        fixture_vault,
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "warn-notice — expression-of-concern",
        date="2026-08-02",
        target_hash="aa11",
    )
    inbox.append_ack(
        fixture_vault,
        correction.id,
        "manual — reviewed all notices",
        actor="human:eran",
        target_hash="aa11",
    )

    assert inbox.open_entries(fixture_vault) == []
    assert inbox.summary(fixture_vault) == {"unacknowledged": 0, "oldest": None}

    changed = inbox.append_entry(
        fixture_vault,
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "warn-notice — correction",
        date="2026-08-03",
        target_hash="bb22",
    )

    assert inbox.open_entries(fixture_vault) == [changed]
    assert inbox.summary(fixture_vault) == {
        "unacknowledged": 1,
        "oldest": "2026-08-03",
    }


def test_summary_counts_and_age(fixture_vault):
    inbox.append_entry(
        fixture_vault,
        "doi",
        "a",
        Result.UNMATCHED,
        "mismatch",
        date="2026-08-01",
    )
    inbox.append_entry(
        fixture_vault,
        "doi",
        "b",
        Result.UNREACHABLE,
        "outage",
        date="2026-08-16",
    )

    assert inbox.summary(fixture_vault) == {
        "unacknowledged": 2,
        "oldest": "2026-08-01",
    }
