import os
import stat

import pytest

from harness_core import Result, inbox
from harness_core.pathcodec import encode_repo_path

INBOX_HEADER = '---\ntype: "review-inbox"\n---\n'


def _write_body(queue, body):
    queue.write_text(INBOX_HEADER + body)


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
    assert first.startswith(b'---\ntype: "review-inbox"\n---\n')
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
        '---\ntype: "review-inbox"\n- [id:: broken]\n',
        "- [id:: broken]\n",
    ],
)
def test_load_rejects_nonempty_inbox_without_valid_required_header(tmp_vault, content):
    queue = tmp_vault / "inbox" / "review-queue.md"
    queue.parent.mkdir(exist_ok=True)
    queue.write_text(content)

    with pytest.raises(inbox.InboxError, match="frontmatter|type"):
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


def test_target_kind_round_trips_and_participates_in_identity_and_ack_scope(
    fixture_vault,
):
    token = encode_repo_path(b"synthesis/a.md")
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


def test_legacy_missing_target_kind_defaults_only_to_identifier(fixture_vault):
    queue = fixture_vault / inbox.INBOX_PATH
    _write_body(
        queue,
        "- [id:: quote/path-bytes:a/2026-08-16] [check:: quote] "
        "[target:: path-bytes:a] [result:: UNMATCHED] [date:: 2026-08-16] "
        "[actor:: harness_core/0.1.0] [reason:: mismatch — legacy]\n",
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
        "[actor:: harness_core/0.1.0] [reason:: mismatch — wrong identity]\n",
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
        "[actor:: harness_core/0.1.0] [reason:: mismatch — invalid]\n",
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
        "[actor:: harness_core/0.1.0] [reason:: invented]\n",
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
        ("ack", {"entry_id": "", "actor": "human:eran"}),
        ("ack", {"entry_id": "doi/x/2026-08-16", "actor": "human:\nother"}),
        ("ack", {"entry_id": "doi/x/2026-08-16", "actor": "human:"}),
        (
            "ack",
            {"entry_id": "doi/x/2026-08-16", "actor": "human:eran", "target_hash": 7},
        ),
        (
            "ack",
            {
                "entry_id": "doi/x/2026-08-16",
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
    if api == "ack" and kwargs["entry_id"]:
        kwargs["entry_id"] = seed.id

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
        "- [ack:: {entry_id}] [actor:: human:eran] [reason:: manual — checked]"
        "{fields}\n"
    )

    _write_body(queue, ack.format(entry_id="doi/missing/2026-08-16", fields=""))
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
            entry_id=finding.id,
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
            entry_id=finding.id,
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
        "- [id:: doi/x/2026-02-30] [check:: doi] [target:: x] "
        "[result:: UNMATCHED] [date:: 2026-02-30] [actor:: harness_core/0.1.0] "
        "[reason:: mismatch]",
        "- [id:: doi/x/2026-08-16] [check:: doi] [target:: x] "
        "[result:: MAYBE] [date:: 2026-08-16] [actor:: harness_core/0.1.0] "
        "[reason:: mismatch]",
        "- [id:: update-notice/x/2026-08-16] [check:: update-notice] "
        "[target:: x] [result:: UNMATCHED] [date:: 2026-08-16] "
        "[actor:: harness_core/0.1.0] [reason:: warn-notice — correction] "
        "[notice-class:: warn]",
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
    }
