import contextlib
import datetime
import os
import stat

import pytest

from research_vault import AGENT_ACTOR, Result, inbox
from research_vault.pathcodec import encode_repo_path

INBOX_HEADER = '---\ntype: "review-queue"\n---\n'


def _write_body(queue, body):
    queue.write_text(INBOX_HEADER + body)


def _age_days(date_str: str) -> int:
    """Whole days between ``date_str`` and today's UTC date.

    Mirrors ``inbox.summary``'s own clock so assertions built around a
    fixture's already-fixed literal date (chosen for reasons unrelated to
    aging) stay correct without hardcoding a day count that would drift as
    "today" moves. The tests that exercise the age math itself compute their
    expected day count independently instead of calling this helper — see
    ``test_skipped_entries_not_counted_unacknowledged``.
    """
    return (
        datetime.datetime.now(datetime.UTC).date()
        - datetime.date.fromisoformat(date_str)
    ).days


def test_new_inbox_is_typed_and_append_preserves_header_bytes(tmp_vault):
    (tmp_vault / "inbox").mkdir(exist_ok=True)

    inbox.append_entry(
        tmp_vault,
        "doi",
        "smith2020",
        Result.UNMATCHED,
        "mismatch",
        date="2026-08-20",
    )

    queue = tmp_vault / "inbox" / "review-queue.md"
    first = queue.read_bytes()
    assert first.startswith(b'---\ntype: "review-queue"\n---\n')
    inbox.append_entry(
        tmp_vault,
        "doi",
        "smith2021",
        Result.UNMATCHED,
        "mismatch",
        date="2026-08-20",
    )
    assert queue.read_bytes().startswith(first)
    assert [entry.target for entry in inbox.load(tmp_vault)] == [
        "smith2020",
        "smith2021",
    ]


@pytest.mark.parametrize("existing", [False, True], ids=["new", "existing"])
def test_durable_append_syncs_visible_bytes_and_new_directory_entry(
    tmp_vault, monkeypatch, existing
):
    queue = tmp_vault / inbox.INBOX_PATH
    queue.parent.mkdir(exist_ok=True)
    if existing:
        queue.write_text(INBOX_HEADER)
    events = []
    original_fsync = os.fsync

    def fsync(descriptor):
        mode = os.fstat(descriptor).st_mode
        if stat.S_ISREG(mode):
            assert b"smith2020" in queue.read_bytes()
            events.append("file")
        elif stat.S_ISDIR(mode):
            events.append("directory")
        return original_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", fsync)

    inbox.append_entry(
        tmp_vault,
        "doi",
        "smith2020",
        Result.UNMATCHED,
        "mismatch",
        date="2026-08-20",
        durable=True,
    )

    assert events == (["file"] if existing else ["file", "directory"])


@pytest.mark.parametrize(
    "content",
    [
        '---\ntype: ""\n---\n- [id:: broken]\n',
        '---\ntype: "wrong"\n---\n- [id:: broken]\n',
        '---\ntype: "review-queue"\n- [id:: broken]\n',
        "- [id:: broken]\n",
    ],
)
def test_load_rejects_nonempty_inbox_without_valid_required_header(tmp_vault, content):
    queue = tmp_vault / "inbox" / "review-queue.md"
    queue.parent.mkdir(exist_ok=True)
    queue.write_text(content)

    with pytest.raises(inbox.InboxError, match=r"frontmatter|type"):
        inbox.load(tmp_vault)


def test_missing_inbox_still_loads_as_empty(tmp_vault):
    assert inbox.load(tmp_vault) == []


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

    assert entries[-1].id == "doi/kind-10:identifier;target-9:smith2020/2026-08-16"
    assert entries[-1].result == "UNMATCHED"
    assert entries[-1].reason.startswith("mismatch")
    line = (fixture_vault / "inbox" / "review-queue.md").read_text().splitlines()[-1]
    assert line.startswith(
        "- [id:: doi/kind-10:identifier;target-9:smith2020/2026-08-16]"
    )


def test_entry_round_trips_bitemporal_dates(fixture_vault):
    inbox.append_entry(
        fixture_vault,
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "retracted — publisher notice found",
        date="2026-08-16",
        target_hash="aa11",
        notice_class="blocking",
        notice_type="retraction",
        notice_date="2025-03-04",
        detection_date="2026-08-16",
    )

    entry = inbox.load(fixture_vault)[-1]

    assert entry.target_hash == "aa11"
    assert entry.notice_class == "blocking"
    assert entry.notice_type == "retraction"
    assert entry.notice_date == "2025-03-04"
    assert entry.detection_date == "2026-08-16"


@pytest.mark.parametrize("notice_date", ["2023", "2023-06", "2023-06-15"])
def test_notice_date_accepts_crossrefs_own_precision(fixture_vault, notice_date):
    """A year-only or month-only Crossref notice date must round-trip at its
    own precision, not silently gain a padded day."""
    inbox.append_entry(
        fixture_vault,
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "retracted — retraction",
        date="2026-08-16",
        target_hash="aa11",
        notice_class="blocking",
        notice_type="retraction",
        notice_date=notice_date,
    )

    entry = inbox.load(fixture_vault)[-1]

    assert entry.notice_date == notice_date


@pytest.mark.parametrize(
    "notice_date",
    [
        "2023-13",  # month out of range
        "2023-06-31",  # June has 30 days
        "23",  # not four year digits
        "2023-6",  # month must be two digits
        "2023-00",  # month 0 is not absent, it is invalid
        "2023-06-00",  # day 0 is not absent, it is invalid
        "2023/06/15",  # wrong separator
        "2023-06-15 ",  # trailing whitespace
    ],
)
def test_notice_date_rejects_malformed_or_out_of_range_partial_dates(
    fixture_vault, notice_date
):
    with pytest.raises(ValueError, match="notice_date"):
        inbox.append_entry(
            fixture_vault,
            "update-notice",
            "smith2020",
            Result.UNMATCHED,
            "retracted — retraction",
            date="2026-08-16",
            target_hash="aa11",
            notice_class="blocking",
            notice_type="retraction",
            notice_date=notice_date,
        )


@pytest.mark.parametrize(
    "notice_date",
    ["٢٠٢٣", "２０２３", "2023-٠٦", "2023-06-١٥"],
    ids=[
        "arabic-indic-year",
        "fullwidth-digit-year",
        "arabic-indic-month",
        "arabic-indic-day",
    ],
)
def test_notice_date_rejects_non_ascii_digits(fixture_vault, notice_date):
    """``\\d`` is Unicode-aware; a governed identifier must stay ASCII-only
    rather than accept whatever Python's int() happens to parse."""
    with pytest.raises(ValueError, match="notice_date"):
        inbox.append_entry(
            fixture_vault,
            "update-notice",
            "smith2020",
            Result.UNMATCHED,
            "retracted — retraction",
            date="2026-08-16",
            target_hash="aa11",
            notice_class="blocking",
            notice_type="retraction",
            notice_date=notice_date,
        )


def test_detection_date_still_requires_full_precision(fixture_vault):
    """Only ``notice_date`` gained partial-precision acceptance — the
    detection date is research-vault's own clock reading and must stay a full
    calendar date."""
    with pytest.raises(ValueError, match="detection_date"):
        inbox.append_entry(
            fixture_vault,
            "update-notice",
            "smith2020",
            Result.UNMATCHED,
            "retracted — retraction",
            date="2026-08-16",
            target_hash="aa11",
            notice_class="blocking",
            notice_type="retraction",
            notice_date="2023",
            detection_date="2023",
        )


def test_partial_notice_date_finding_is_fully_acknowledgeable(fixture_vault):
    """The whole point of keeping the alert standing is that a human can still
    close it: a year-only notice date must not choke the ack path."""
    finding = inbox.append_entry(
        fixture_vault,
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "retracted — retraction",
        date="2026-08-16",
        target_hash="aa11",
        notice_class="blocking",
        notice_type="retraction",
        notice_date="2023",
    )

    assert inbox.load(fixture_vault)[-1].notice_date == "2023"

    inbox.append_ack(
        fixture_vault,
        finding.id,
        "manual — reviewed",
        actor="human:eran",
        target_hash="aa11",
        notice_class="blocking",
        notice_type="retraction",
        notice_date="2023",
    )

    assert inbox.is_acknowledged(
        fixture_vault,
        "update-notice",
        "smith2020",
        current_hash="aa11",
        notice_class="blocking",
        notice_type="retraction",
        notice_date="2023",
    )


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
            actor="research_vault/0.1.0",
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


def test_target_kind_round_trips_and_participates_in_identity_and_ack_scope(
    fixture_vault,
):
    token = encode_repo_path(b"wiki/concepts/a.md")
    identifier = inbox.append_entry(
        fixture_vault,
        "quote",
        token,
        Result.UNMATCHED,
        "mismatch — identifier",
        date="2026-08-16",
        target_hash="aa11",
        target_kind="identifier",
    )
    path = inbox.append_entry(
        fixture_vault,
        "quote",
        token,
        Result.UNMATCHED,
        "mismatch — path",
        date="2026-08-16",
        target_hash="aa11",
        target_kind="repo-path",
    )

    assert identifier.id != path.id
    loaded = inbox.load(fixture_vault)
    assert [(entry.target, entry.target_kind) for entry in loaded[-2:]] == [
        (token, "identifier"),
        (token, "repo-path"),
    ]
    inbox.append_ack(
        fixture_vault,
        path.id,
        "manual — checked path",
        "human:test",
        "aa11",
    )
    assert inbox.is_acknowledged(
        fixture_vault,
        "quote",
        token,
        current_hash="aa11",
        target_kind="repo-path",
    )
    assert not inbox.is_acknowledged(
        fixture_vault,
        "quote",
        token,
        current_hash="aa11",
        target_kind="identifier",
    )
    ack_line = (fixture_vault / inbox.INBOX_PATH).read_text().splitlines()[-1]
    assert "[target-kind:: repo-path]" in ack_line


def test_target_kind_identity_is_injective_when_identifier_contains_kind_syntax(
    fixture_vault,
):
    identifier = inbox.append_entry(
        fixture_vault,
        "quote",
        "path-bytes:a/kind-repo-path",
        Result.UNMATCHED,
        "mismatch — identifier",
        date="2026-08-16",
        target_kind="identifier",
    )
    repo_path = inbox.append_entry(
        fixture_vault,
        "quote",
        "path-bytes:a",
        Result.UNMATCHED,
        "mismatch — repo path",
        date="2026-08-16",
        target_kind="repo-path",
    )

    assert identifier.id != repo_path.id
    assert len(inbox.open_entries(fixture_vault)) == 2
    inbox.append_ack(
        fixture_vault,
        repo_path.id,
        "manual — checked repo path",
        "human:test",
    )
    assert inbox.is_acknowledged(
        fixture_vault,
        "quote",
        "path-bytes:a",
        target_kind="repo-path",
    )
    assert not inbox.is_acknowledged(
        fixture_vault,
        "quote",
        "path-bytes:a/kind-repo-path",
        target_kind="identifier",
    )
    assert [
        (entry.target, entry.target_kind) for entry in inbox.open_entries(fixture_vault)
    ] == [("path-bytes:a/kind-repo-path", "identifier")]


def test_missing_target_kind_defaults_only_to_identifier(fixture_vault):
    queue = fixture_vault / inbox.INBOX_PATH
    _write_body(
        queue,
        "- [id:: quote/kind-10:identifier;target-12:path-bytes:a/2026-08-16] "
        "[check:: quote] "
        "[target:: path-bytes:a] [result:: UNMATCHED] [date:: 2026-08-16] "
        "[actor:: research_vault/0.1.0] [reason:: mismatch — legacy]\n",
    )

    loaded = inbox.load(fixture_vault)

    assert loaded[0].target_kind == "identifier"


def test_explicit_repo_path_kind_rejects_a_legacy_identifier_finding_id(
    fixture_vault,
):
    queue = fixture_vault / inbox.INBOX_PATH
    _write_body(
        queue,
        "- [id:: quote/path-bytes:a/2026-08-16] [check:: quote] "
        "[target:: path-bytes:a] [target-kind:: repo-path] "
        "[result:: UNMATCHED] [date:: 2026-08-16] "
        "[actor:: research_vault/0.1.0] [reason:: mismatch — wrong identity]\n",
    )

    with pytest.raises(inbox.InboxError):
        inbox.load(fixture_vault)


@pytest.mark.parametrize(
    ("target", "kind"),
    [
        ("path-bytes:a%2f", "repo-path"),
        ("path-bytes:a%2F", "repo-path"),
        ("path-bytes:a", "unknown"),
    ],
)
def test_load_rejects_noncanonical_repo_path_or_unknown_kind_before_mutation(
    fixture_vault, target, kind
):
    queue = fixture_vault / inbox.INBOX_PATH
    _write_body(
        queue,
        f"- [id:: x] [check:: quote] [target:: {target}] "
        f"[target-kind:: {kind}] [result:: UNMATCHED] [date:: 2026-08-16] "
        "[actor:: research_vault/0.1.0] [reason:: mismatch — invalid]\n",
    )
    before = queue.read_bytes()

    with pytest.raises(inbox.InboxError):
        inbox.load(fixture_vault)

    assert queue.read_bytes() == before


def test_load_rejects_handwritten_finding_with_invalid_reason(fixture_vault):
    queue = fixture_vault / "inbox" / "review-queue.md"
    _write_body(
        queue,
        "- [id:: doi/smith2020/2026-08-16] [check:: doi] "
        "[target:: smith2020] [result:: UNMATCHED] [date:: 2026-08-16] "
        "[actor:: research_vault/0.1.0] [reason:: invented]\n",
    )

    with pytest.raises(inbox.InboxError, match="line 1"):
        inbox.load(fixture_vault)


def test_load_rejects_handwritten_human_ack_with_invalid_reason(fixture_vault):
    queue = fixture_vault / "inbox" / "review-queue.md"
    _write_body(
        queue,
        "- [ack:: doi/smith2020/2026-08-16] [actor:: human:eran] "
        "[reason:: manualized]\n",
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
        "oldest_age_days": _age_days("2026-08-16"),
    }
    assert not inbox.is_acknowledged(
        fixture_vault,
        "quote",
        "smith2020#^c-11111111",
    )

    assert changed.id != first.id
    inbox.append_ack(
        fixture_vault,
        changed.id,
        "manual — checked changed content",
        actor="human:eran",
        target_hash="bb22",
    )
    assert inbox.open_entries(fixture_vault) == []


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
    queue = fixture_vault / inbox.INBOX_PATH
    before = queue.read_bytes()
    with pytest.raises(ValueError, match="target hash does not match finding"):
        inbox.append_ack(
            fixture_vault,
            finding.id,
            "manual — wrong scope",
            actor="human:eran",
            target_hash="different",
        )

    assert queue.read_bytes() == before
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


def test_update_notice_ack_closes_only_its_exact_notice_fingerprint(fixture_vault):
    correction = inbox.append_entry(
        fixture_vault,
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "warn-notice — correction",
        date="2026-08-01",
        target_hash="aa11",
        notice_class="warn",
        notice_type="correction",
        notice_date="2026-01-01",
    )
    erratum = inbox.append_entry(
        fixture_vault,
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "warn-notice — erratum",
        date="2026-08-01",
        target_hash="aa11",
        notice_class="warn",
        notice_type="erratum",
        notice_date="2026-01-01",
    )
    inbox.append_ack(
        fixture_vault,
        correction.id,
        "manual — reviewed correction",
        actor="human:eran",
        target_hash="aa11",
    )

    assert correction.id != erratum.id
    assert inbox.open_entries(fixture_vault) == [erratum]
    assert inbox.summary(fixture_vault) == {
        "unacknowledged": 1,
        "oldest": "2026-08-01",
        "oldest_age_days": _age_days("2026-08-01"),
    }

    blocking = inbox.append_entry(
        fixture_vault,
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "retracted — retraction",
        date="2026-08-02",
        target_hash="aa11",
        notice_class="blocking",
        notice_type="retraction",
        notice_date="2026-01-01",
    )

    assert inbox.open_entries(fixture_vault) == [erratum, blocking]
    assert inbox.summary(fixture_vault) == {
        "unacknowledged": 2,
        "oldest": "2026-08-01",
        "oldest_age_days": _age_days("2026-08-01"),
    }


def test_identical_update_notice_recurrence_stays_acknowledged(fixture_vault):
    first = inbox.append_entry(
        fixture_vault,
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "warn-notice — correction",
        date="2026-08-01",
        target_hash="aa11",
        notice_class="warn",
        notice_type="correction",
        notice_date="2026-01-01",
    )
    inbox.append_ack(
        fixture_vault,
        first.id,
        "manual — reviewed correction",
        actor="human:eran",
        target_hash="aa11",
    )
    inbox.append_entry(
        fixture_vault,
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "warn-notice — correction",
        date="2026-08-02",
        target_hash="aa11",
        notice_class="warn",
        notice_type="correction",
        notice_date="2026-01-01",
    )

    assert inbox.is_acknowledged(
        fixture_vault,
        "update-notice",
        "smith2020",
        current_hash="aa11",
        notice_class="warn",
        notice_type="correction",
        notice_date="2026-01-01",
    )
    assert inbox.open_entries(fixture_vault) == []


@pytest.mark.parametrize(
    ("api", "kwargs"),
    [
        ("finding", {"check": "", "target": "smith2020"}),
        ("finding", {"check": "doi\npoison", "target": "smith2020"}),
        ("finding", {"check": "doi", "target": ""}),
        ("finding", {"check": "doi", "target": "smith2020", "result": "UNMATCHED"}),
        ("finding", {"check": "doi", "target": "smith2020", "actor": 42}),
        ("finding", {"check": "doi", "target": "smith2020", "date": "2026-02-30"}),
        ("finding", {"check": "doi", "target": "smith2020", "date": ""}),
        ("finding", {"check": "doi", "target": "smith2020", "target_hash": "a\nb"}),
        ("finding", {"check": "doi", "target": "smith2020", "reason": "mismatch\0x"}),
        (
            "finding",
            {
                "check": "update-notice",
                "target": "smith2020",
                "notice_class": "warn",
            },
        ),
        (
            "finding",
            {
                "check": "update-notice",
                "target": "smith2020",
                "notice_class": "warn",
                "notice_type": "retraction",
            },
        ),
        (
            "finding",
            {
                "check": "update-notice",
                "target": "smith2020",
                "notice_class": "warn",
                "notice_type": "correction",
                "result": Result.MATCHED,
            },
        ),
        ("ack", {"finding_id": "", "actor": "human:eran"}),
        ("ack", {"finding_id": "doi/x/2026-08-16", "actor": "human:\nother"}),
        ("ack", {"finding_id": "doi/x/2026-08-16", "actor": "human:"}),
        (
            "ack",
            {"finding_id": "doi/x/2026-08-16", "actor": "human:eran", "target_hash": 7},
        ),
        (
            "ack",
            {
                "finding_id": "doi/x/2026-08-16",
                "actor": "human:eran",
                "target_hash": "different",
            },
        ),
    ],
)
def test_rejected_append_is_byte_atomic(fixture_vault, api, kwargs):
    queue = fixture_vault / "inbox" / "review-queue.md"
    seed = inbox.append_entry(
        fixture_vault,
        "doi",
        "existing",
        Result.UNMATCHED,
        "mismatch",
        date="2026-08-16",
    )
    before = queue.read_bytes()
    kwargs = dict(kwargs)
    if api == "ack" and kwargs["finding_id"]:
        kwargs["finding_id"] = seed.id

    if api == "finding":
        with pytest.raises((TypeError, ValueError)):
            inbox.append_entry(
                fixture_vault,
                result=kwargs.pop("result", Result.UNMATCHED),
                reason=kwargs.pop("reason", "mismatch"),
                **kwargs,
            )
    else:
        with pytest.raises((TypeError, ValueError)):
            inbox.append_ack(
                fixture_vault,
                reason="manual — checked",
                **kwargs,
            )

    assert queue.read_bytes() == before


def test_ack_rejects_missing_or_ambiguous_finding_without_appending(fixture_vault):
    queue = fixture_vault / "inbox" / "review-queue.md"
    before = queue.read_bytes()
    with pytest.raises(ValueError, match="exactly one"):
        inbox.append_ack(
            fixture_vault,
            "doi/missing/2026-08-16",
            "manual — checked",
            "human:eran",
        )
    assert queue.read_bytes() == before

    finding = inbox.append_entry(
        fixture_vault,
        "doi",
        "same",
        Result.UNMATCHED,
        "mismatch",
        date="2026-08-16",
    )
    body = queue.read_text().removeprefix(INBOX_HEADER)
    _write_body(queue, body + body)
    before = queue.read_bytes()
    with pytest.raises(ValueError, match="exactly one"):
        inbox.append_ack(
            fixture_vault,
            finding.id,
            "manual — checked",
            "human:eran",
        )
    assert queue.read_bytes() == before


def test_load_rejects_unknown_hash_mismatched_or_ambiguous_ack_references(
    fixture_vault,
):
    queue = fixture_vault / inbox.INBOX_PATH
    ack = (
        "- [ack:: {finding_id}] [actor:: human:eran] [reason:: manual — checked]"
        "{fields}\n"
    )

    _write_body(queue, ack.format(finding_id="doi/missing/2026-08-16", fields=""))
    with pytest.raises(inbox.InboxError, match="line 1"):
        inbox.load(fixture_vault)

    finding = inbox.append_entry(
        fixture_vault,
        "doi",
        "smith2020",
        Result.UNMATCHED,
        "mismatch",
        date="2026-08-16",
        target_hash="aa11",
    )
    finding_line = queue.read_text().splitlines()[-1]
    _write_body(
        queue,
        finding_line
        + "\n"
        + ack.format(
            finding_id=finding.id,
            fields=" [target-hash:: bb22]",
        ),
    )
    with pytest.raises(inbox.InboxError, match="line 2"):
        inbox.load(fixture_vault)

    _write_body(
        queue,
        finding_line
        + "\n"
        + finding_line
        + "\n"
        + ack.format(
            finding_id=finding.id,
            fields=" [target-hash:: aa11]",
        ),
    )
    with pytest.raises(inbox.InboxError, match="line 3"):
        inbox.load(fixture_vault)


def test_load_rejects_ack_with_incomplete_notice_fingerprint(fixture_vault):
    queue = fixture_vault / inbox.INBOX_PATH
    finding = inbox.append_entry(
        fixture_vault,
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "warn-notice — correction",
        date="2026-08-16",
        target_hash="aa11",
        notice_class="warn",
        notice_type="correction",
        notice_date="2026-01-01",
    )
    queue.write_text(
        queue.read_text() + f"- [ack:: {finding.id}] [actor:: human:eran] "
        "[reason:: manual — checked] [target-hash:: aa11]\n"
    )

    with pytest.raises(inbox.InboxError, match="line 2"):
        inbox.load(fixture_vault)


def test_load_rejects_invalid_dates_results_and_incomplete_notice_fingerprint(
    fixture_vault,
):
    queue = fixture_vault / "inbox" / "review-queue.md"
    rows = [
        (
            "- [id:: doi/x/2026-02-30] [check:: doi] [target:: x] "
            "[result:: UNMATCHED] [date:: 2026-02-30] [actor:: research_vault/0.1.0] "
            "[reason:: mismatch]"
        ),
        (
            "- [id:: doi/x/2026-08-16] [check:: doi] [target:: x] "
            "[result:: MAYBE] [date:: 2026-08-16] [actor:: research_vault/0.1.0] "
            "[reason:: mismatch]"
        ),
        (
            "- [id:: update-notice/x/2026-08-16] [check:: update-notice] "
            "[target:: x] [result:: UNMATCHED] [date:: 2026-08-16] "
            "[actor:: research_vault/0.1.0] [reason:: warn-notice — correction] "
            "[notice-class:: warn]"
        ),
    ]
    for row in rows:
        _write_body(queue, row + "\n")
        with pytest.raises(inbox.InboxError, match="line 1"):
            inbox.load(fixture_vault)


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
        "oldest_age_days": _age_days("2026-08-01"),
    }


def test_skipped_entries_not_counted_unacknowledged(fixture_vault):
    # The UNMATCHED entry below is filed at "today minus `unmatched_age_days`"
    # rather than a fixed calendar date, so the `oldest_age_days` assertion
    # asserts a fixed, independent integer instead of duplicating production's
    # own now-minus-date formula (see `_age_days`, used elsewhere in this file
    # for assertions that are not themselves about the age math) — the fixed
    # SKIPPED date below is always 2026-08-01 whatever "today" is when this
    # runs, so if the SKIPPED-filter regressed and it started contributing to
    # the age basis, `oldest_age_days` would jump to 23-and-growing, never
    # stay at `unmatched_age_days`.
    unmatched_age_days = 3
    unmatched_date = (
        datetime.datetime.now(datetime.UTC).date()
        - datetime.timedelta(days=unmatched_age_days)
    ).isoformat()

    inbox.append_entry(
        fixture_vault,
        "metadata",
        "a",
        Result.SKIPPED,
        "no-identifier",
        date="2026-08-01",
    )

    # A queue holding only SKIPPED findings reports nothing unacknowledged:
    # SKIPPED means "does not apply", not "needs a human decision". With
    # nothing unacknowledged there is no age basis either, so both `oldest`
    # and `oldest_age_days` are None together.
    assert inbox.summary(fixture_vault) == {
        "unacknowledged": 0,
        "oldest": None,
        "oldest_age_days": None,
    }

    inbox.append_entry(
        fixture_vault,
        "doi",
        "b",
        Result.UNMATCHED,
        "mismatch",
        date=unmatched_date,
    )

    # Mixed queue: the SKIPPED entry still contributes neither to the count
    # nor to the oldest-age basis, so all three fields derive from the
    # UNMATCHED entry alone even though it is dated later than the excluded
    # SKIPPED entry.
    assert inbox.summary(fixture_vault) == {
        "unacknowledged": 1,
        "oldest": unmatched_date,
        "oldest_age_days": unmatched_age_days,
    }

    # SKIPPED entries stay in the audit trail and in full listings — only
    # the counting surface excludes them.
    assert {entry.result for entry in inbox.open_entries(fixture_vault)} == {
        Result.SKIPPED.value,
        Result.UNMATCHED.value,
    }


# The review queue is append-only, so one unparseable row is permanent: every
# later `inbox`, `ack`, doctor probe and `verify` read of the file raises, and
# on a fresh vault the first bad write both creates and corrupts it. ``load``
# splits the body with ``str.splitlines()``, so the writer's reject class must
# be the parser's own break set — not the narrower \n/\r/\0 trio, which let \v,
# \f, \x1c-\x1e, \x85, U+2028 and U+2029 through into a durable surface.
SPLITLINES_SEPARATORS = [
    "\n",
    "\r\n",
    "\r",
    "\v",
    "\f",
    "\x1c",
    "\x1d",
    "\x1e",
    "\x85",
    "\u2028",
    "\u2029",
]


@pytest.mark.parametrize("separator", SPLITLINES_SEPARATORS, ids=repr)
@pytest.mark.parametrize("position", ["embedded", "trailing"], ids=str)
def test_append_refuses_any_field_carrying_a_line_break(
    fixture_vault, separator, position
):
    queue = fixture_vault / "inbox" / "review-queue.md"
    before = queue.read_bytes()
    hostile = f"a{separator}b" if position == "embedded" else f"a{separator}"

    with pytest.raises(ValueError, match="single-line"):
        inbox.append_entry(
            fixture_vault, "citation-key", hostile, Result.UNMATCHED, "schema-violation"
        )

    assert queue.read_bytes() == before


# Every argument that reaches a durable inline field, one hostile builder each.
# Varying only `target` was the round-1 defect: it let a test titled "whatever
# gets in, loads back" certify the class closed while `reason` — validated by
# `validate_reason`, not `_validate_text` — still bricked the queue.
def _finding_kwargs(field, hostile):
    kwargs = {
        "check": "citation-key",
        "target": "goodkey",
        "result": Result.UNMATCHED,
        "reason": "mismatch",
        "actor": AGENT_ACTOR,
    }
    if field in {"notice_class", "notice_type", "notice_date"}:
        kwargs.update(
            check="update-notice", notice_class="warn", notice_type="correction"
        )
    kwargs[field] = {
        "check": f"cite{hostile}key",
        "target": f"good{hostile}key",
        "reason": f"mismatch a{hostile}b",
        "actor": f"human:e{hostile}ran",
        "date": f"2026-08{hostile}-22",
        "target_hash": f"aa{hostile}11",
        "target_kind": f"identi{hostile}fier",
        "notice_class": f"warn{hostile}",
        "notice_type": f"correction{hostile}",
        "notice_date": f"2026{hostile}-08-22",
    }[field]
    return kwargs


FINDING_FIELDS = [
    "check",
    "target",
    "reason",
    "actor",
    "date",
    "target_hash",
    "target_kind",
    "notice_class",
    "notice_type",
    "notice_date",
]
ACK_FIELDS = ["reason", "actor", "finding_id", "target_hash"]


@pytest.mark.parametrize("field", FINDING_FIELDS, ids=str)
@pytest.mark.parametrize("separator", SPLITLINES_SEPARATORS, ids=repr)
def test_every_finding_row_the_writer_accepts_stays_loadable(
    fixture_vault, field, separator
):
    """The corruption class as its own invariant: whatever gets in, loads back.

    Every durable field, not just the one the round-1 Critical arrived through.
    A field is allowed to refuse the value or to accept it — what it may never
    do is write a row that ``load`` cannot read, because the queue is
    append-only and one such row is permanent.
    """
    with contextlib.suppress(TypeError, ValueError):
        inbox.append_entry(fixture_vault, **_finding_kwargs(field, separator))

    inbox.load(fixture_vault)


@pytest.mark.parametrize("field", ACK_FIELDS, ids=str)
@pytest.mark.parametrize("separator", SPLITLINES_SEPARATORS, ids=repr)
def test_every_ack_row_the_writer_accepts_stays_loadable(
    fixture_vault, field, separator
):
    """Acknowledgments serialize to the same grammar and need the same bound."""
    seed = inbox.append_entry(
        fixture_vault, "citation-key", "goodkey", Result.UNMATCHED, "mismatch"
    )
    kwargs = {
        "finding_id": seed.id,
        "reason": "manual — reviewed",
        "actor": "human:eran",
    }
    kwargs[field] = {
        "reason": f"manual a{separator}b",
        "actor": f"human:e{separator}ran",
        "finding_id": f"citation_key/x{separator}/2026-08-16",
        "target_hash": f"aa{separator}11",
    }[field]

    with contextlib.suppress(TypeError, ValueError):
        inbox.append_ack(fixture_vault, **kwargs)

    inbox.load(fixture_vault)


@pytest.mark.parametrize("separator", SPLITLINES_SEPARATORS, ids=repr)
@pytest.mark.parametrize("position", ["embedded", "trailing"], ids=str)
def test_validate_reason_refuses_every_line_break(separator, position):
    """`reason` is the one durable field `_validate_text` never sees.

    Its `_REASON` regex ends in `.*`, and `.` matches everything in the
    splitlines set except \\n — so eight separators rode a code-prefixed
    reason straight onto a durable line.
    """
    hostile = (
        f"outage a{separator}b" if position == "embedded" else f"outage a{separator}"
    )

    with pytest.raises(ValueError, match="reason"):
        inbox.validate_reason(hostile)


def _seed_finding(vault):
    """Append one real finding and return it with the exact line it wrote."""
    finding = inbox.append_entry(
        vault,
        "doi",
        "smith2020",
        Result.UNMATCHED,
        "mismatch",
        date="2026-08-16",
    )
    row = (vault / inbox.INBOX_PATH).read_text().splitlines()[-1]
    return finding, row


def test_load_skips_blank_body_lines_but_still_counts_them(fixture_vault):
    """Blank lines are separators, not records — yet they hold their line number.

    The queue is append-only and hand-inspected, so a stray blank line must not
    become a parse error. It must also not renumber the rows around it: the line
    number in a rejection is how a human finds the offending row in the file.
    """
    queue = fixture_vault / inbox.INBOX_PATH
    finding, row = _seed_finding(fixture_vault)

    _write_body(queue, "\n" + row + "\n   \n")
    assert [entry.id for entry in inbox.load(fixture_vault)] == [finding.id]

    _write_body(
        queue,
        "\n"
        + row
        + "\n   \n- [check:: doi] [target:: smith2020] [reason:: mismatch]\n",
    )
    with pytest.raises(inbox.InboxError, match="unparseable inbox line 4"):
        inbox.load(fixture_vault)


@pytest.mark.parametrize(
    ("row_template", "kind"),
    [
        ("- [ack:: {id}] [actor:: human:eran] [reason:: manual — ok] [id:: x]", "ack"),
        ("- [ack:: {id}] [actor:: human:eran]", "ack"),
        (
            "- [ack:: {id}] [actor:: human:eran] [reason:: manual — ok] [check:: doi]",
            "ack",
        ),
        (
            (
                "- [id:: {id}] [target:: smith2020] [result:: UNMATCHED] "
                "[date:: 2026-08-16] [actor:: research_vault/0.1.0] "
                "[reason:: mismatch]"
            ),
            "finding",
        ),
        (
            (
                "- [id:: {id}] [check:: doi] [target:: smith2020] [result:: UNMATCHED] "
                "[date:: 2026-08-16] [actor:: research_vault/0.1.0] "
                "[reason:: mismatch] [bogus:: x]"
            ),
            "finding",
        ),
    ],
    ids=[
        "ack-also-claims-a-finding-id",
        "ack-without-a-reason",
        "ack-carrying-a-finding-only-field",
        "finding-without-a-check",
        "finding-with-an-unknown-field",
    ],
)
def test_load_rejects_a_row_whose_field_set_is_neither_a_finding_nor_an_ack(
    fixture_vault, row_template, kind
):
    """The two record grammars are closed sets, checked before any field is read.

    A row is a finding or an acknowledgment, and each admits exactly its own
    required and optional keys. A row that mixes them, drops a required key or
    invents one is not a record this reader may interpret — an append-only log
    that guessed at a half-understood row would launder it into the vault's
    permanent history.
    """
    queue = fixture_vault / inbox.INBOX_PATH
    finding, row = _seed_finding(fixture_vault)
    malformed = row_template.format(id=finding.id if kind == "ack" else "doi/x")

    _write_body(queue, row + "\n" + malformed + "\n")

    with pytest.raises(inbox.InboxError, match="unparseable inbox line 2"):
        inbox.load(fixture_vault)


@pytest.mark.parametrize(
    "actor", ["research_vault/0.1.0", "human:", "human:   "], ids=repr
)
def test_load_rejects_an_acknowledgment_no_named_human_signed(fixture_vault, actor):
    """An acknowledgment is a human act; the agent may not sign one for itself.

    Closing a finding is the one thing the deterministic pipeline is not allowed
    to do on its own authority, so the actor must be a ``human:`` prefix with an
    actual name behind it. A bare prefix is the same unsigned act wearing the
    right word.
    """
    queue = fixture_vault / inbox.INBOX_PATH
    finding, row = _seed_finding(fixture_vault)

    _write_body(
        queue,
        row + f"\n- [ack:: {finding.id}] [actor:: {actor}] [reason:: manual — ok]\n",
    )

    with pytest.raises(
        inbox.InboxError, match="invalid acknowledgment on inbox line 2"
    ):
        inbox.load(fixture_vault)


def test_a_legacy_update_notice_is_closed_only_by_an_ack_naming_it(fixture_vault):
    """Rows written before notice fingerprints existed close by id alone.

    An update-notice finding with no ``notice-class`` predates the
    class/type/date discriminator, so there is no fingerprint to match an ack
    against — only the row's own id. That ack must therefore close that one row
    and nothing else: a later, properly fingerprinted notice on the same target
    is a different observation and has to stay open until a human sees it.
    """
    legacy = inbox.append_entry(
        fixture_vault,
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "warn-notice — correction",
        date="2026-08-16",
        target_hash="aa11",
    )
    fingerprinted = inbox.append_entry(
        fixture_vault,
        "update-notice",
        "smith2020",
        Result.UNMATCHED,
        "warn-notice — correction",
        date="2026-08-17",
        target_hash="aa11",
        notice_class="warn",
        notice_type="correction",
        notice_date="2026-01-01",
    )
    assert legacy.notice_class is None

    inbox.append_ack(fixture_vault, legacy.id, "manual — reviewed", "human:eran")

    assert [entry.id for entry in inbox.open_entries(fixture_vault)] == [
        fingerprinted.id
    ]
    assert inbox.summary(fixture_vault) == {
        "unacknowledged": 1,
        "oldest": "2026-08-17",
        "oldest_age_days": _age_days("2026-08-17"),
    }
