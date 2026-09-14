import dataclasses
import datetime
import hashlib
import json

import pytest

from research_vault import AGENT_ACTOR, Result, frontmatter, notes
from tests.conftest import must_replace
from tests.fakes import ATTACHMENT, CHILD_NOTE, ITEM

LITERATURE = '---\ncitationKey: "smith2020"\ntype: "literature"\n'
BODY = "# Mortality decline\n"


def _note(body: str = BODY, **frontmatter_lines: str) -> str:
    """One literature note built by hand, witness included — no renderer."""
    extra = "".join(f'{key}: "{value}"\n' for key, value in frontmatter_lines.items())
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return f'{LITERATURE}{extra}managed-sha256: "{digest}"\n---\n{body}'


def test_note_path(tmp_vault):
    assert (
        notes.note_path(tmp_vault, "smith2020")
        .as_posix()
        .endswith("literatures/smith2020.md")
    )


@pytest.mark.parametrize(
    "citation_key",
    # An absolute-path ESCAPE fixture: the value is a citation key that note_path must
    # reject, never a temporary file this test writes to.
    ["", "../escape", "/tmp/escape", "..\\escape", "nested/escape"],  # noqa: S108
)
def test_note_path_rejects_unsafe_citation_keys(tmp_vault, citation_key):
    with pytest.raises(notes.InvalidCitationKeyError):
        notes.note_path(tmp_vault, citation_key)


def test_sha256_file(tmp_path):
    f = tmp_path / "x.pdf"
    f.write_bytes(b"pdfbytes")
    assert len(notes.sha256_file(f)) == 64


def test_body_sha256_hashes_everything_below_the_frontmatter():
    text = '---\ntype: "literature"\n---\n# Title\n\nbody\n'
    assert notes.note_body(text) == "# Title\n\nbody\n"
    assert notes.body_sha256(text) == hashlib.sha256(b"# Title\n\nbody\n").hexdigest()


def test_body_witness_validation_is_four_state():
    body = "# Title\n"
    digest = hashlib.sha256(body.encode()).hexdigest()
    good = f'---\ntype: "literature"\nmanaged-sha256: "{digest}"\n---\n{body}'.encode()
    assert notes.validate_managed_witness(good) == (Result.MATCHED, "matched")

    stale = must_replace(good, body.encode(), b"# Edited\n")
    assert notes.validate_managed_witness(stale) == (
        Result.UNMATCHED,
        "schema-violation — stale managed-sha256",
    )
    missing = f'---\ntype: "literature"\n---\n{body}'.encode()
    assert notes.validate_managed_witness(missing) == (
        Result.UNMATCHED,
        "schema-violation — missing managed-sha256",
    )
    assert notes.validate_managed_witness(b"\xff\xfe") == (
        Result.UNREACHABLE,
        "outage — literature note is not UTF-8",
    )
    assert notes.validate_managed_witness(b"---\nunterminated\n") == (
        Result.UNMATCHED,
        "schema-violation — malformed frontmatter",
    )


def test_managed_region_surface_is_gone():
    for name in ("MANAGED_OPEN", "managed_slice_bytes", "render_claim"):
        assert not hasattr(notes, name)


@pytest.mark.parametrize(
    "witness",
    [None, 42, "", "A" * 64, "a" * 63, "g" * 64, "0" * 64],
)
def test_managed_witness_validation_rejects_missing_malformed_or_stale(witness):
    text = _note()
    data, body = frontmatter.parse(text)
    if witness is None:
        data.pop("managed-sha256")
    else:
        data["managed-sha256"] = witness
    invalid = (frontmatter.serialize(data) + body).encode()

    result, reason = notes.validate_managed_witness(invalid)

    assert result is Result.UNMATCHED
    assert reason.startswith("schema-violation")


@pytest.mark.parametrize("valid_last", [False, True])
def test_managed_witness_rejects_duplicate_top_level_keys_in_either_order(valid_last):
    text = _note()
    valid = frontmatter.parse(text)[0]["managed-sha256"]
    bad, good = 'managed-sha256: "bad"\n', f'managed-sha256: "{valid}"\n'
    duplicate = (bad + good) if valid_last else (good + bad)
    original_line = f'managed-sha256: "{valid}"\n'
    note = must_replace(text, original_line, duplicate).encode()

    result, reason = notes.validate_managed_witness(note)

    assert result is Result.UNMATCHED
    assert reason.startswith("schema-violation")


def test_generated_metadata_is_substantive_canonical_content():
    """The `{by, at}` mapping `_valid_generated` defines — the shape a
    mapping-aware exemption would have to match — moves the content."""
    first = must_replace(
        _note(),
        "---\n# Mortality decline\n",
        f'generated: {{by: "{AGENT_ACTOR}", at: "2026-08-20T12:34:56Z"}}\n'
        "---\n# Mortality decline\n",
    )
    assert notes._valid_generated(frontmatter.parse(first)[0]["generated"])
    changed = must_replace(first, "2026-08-20T12:34:56Z", "2026-08-21T01:02:03Z")

    assert notes.content_changed(first, changed)


def test_content_changed_compares_only_the_verifier_owned_surface():
    base = _note()
    verified = must_replace(
        base,
        "---\n# Mortality decline\n",
        'verified:\n  - {by: "bot", at: "2026-08-16", check: "quote"}\n'
        "---\n# Mortality decline\n",
    )
    changed = _note(body="# Updated title\n")

    assert notes.content_changed(base, verified) is False
    assert notes.content_changed(base, changed) is True
    assert notes.content_changed(None, base) is True


def test_canonical_content_excludes_only_valid_verifier_owned_surfaces():
    base = """---
citationKey: "x"
verified:
  - {by: "bot", at: "2026-08-16", check: "doi"}
status: "included"
---
- (quote) text [failed-verification:: quote/2026-08-16] ^c-1
plain [failed-verification:: quote/2026-08-16]
"""
    changed_events = must_replace(base, 'check: "doi"', 'check: "metadata"')
    changed_marker = must_replace(base, "quote/2026-08-16", "quote/2026-08-17")
    deprecated = must_replace(base, 'status: "included"', 'status: "deprecated"')

    assert notes.canonical_content(base) == notes.canonical_content(changed_events)
    assert notes.canonical_content(base) != notes.canonical_content(changed_marker)
    assert notes.content_changed(base, changed_events) is False
    assert notes.content_changed(base, changed_marker) is True
    assert notes.content_changed(base, deprecated) is True
    assert "plain [failed-verification" in notes.canonical_content(base)


def test_canonical_content_keeps_malformed_verified_scalar_and_marker_lookalike():
    text = """---
verified: "not-a-list"
---
- (quote) text [failed-verification:: bad date] ^c-1
"""
    assert notes.canonical_content(text) == text


def test_canonical_content_keeps_mixed_verified_list_byte_for_byte():
    text = """---
verified:
  - {by: "bot", at: "2026-08-16", check: "doi"}
  - "not-an-event"
---
- (quote) live [failed-verification:: quote/2026-08-16] ^c-1
"""

    canonical = notes.canonical_content(text)

    assert '  - "not-an-event"\n' in canonical
    assert "live [failed-verification" in canonical


def test_deprecation_transition_fields_are_all_substantive():
    base = """---
citationKey: "x"
status: "included"
deprecated-at: ""
deprecated-by: ""
reason: ""
---
body
"""
    transitions = [
        must_replace(base, 'status: "included"', 'status: "deprecated"'),
        must_replace(base, 'deprecated-at: ""', 'deprecated-at: "2026-08-16"'),
        must_replace(base, 'deprecated-by: ""', 'deprecated-by: "human:eran"'),
        must_replace(base, 'reason: ""', 'reason: "superseded source"'),
    ]

    assert all(notes.content_changed(base, changed) for changed in transitions)


def test_canonical_content_preserves_markers_in_frontmatter_prose_fences_and_continuations():
    text = """---
verified: "not-a-list"
marker: "[failed-verification:: quote/2026-08-16]"
---
prose [failed-verification:: quote/2026-08-16]
```md
- (quote) code [failed-verification:: quote/2026-08-16] ^c-1
```
- (quote) live [failed-verification:: quote/2026-08-16] ^c-2
  > continuation [failed-verification:: quote/2026-08-16]
"""
    canonical = notes.canonical_content(text)
    assert 'marker: "[failed-verification:: quote/2026-08-16]"' in canonical
    assert "prose [failed-verification" in canonical
    assert "code [failed-verification" in canonical
    assert "continuation [failed-verification" in canonical
    assert "live [failed-verification" in canonical


def test_canonical_content_preserves_crlf_and_unterminated_frontmatter():
    text = '---\r\nverified:\r\n  - {by: "bot"}\r\n---\r\n- (quote) x [failed-verification:: quote/2026-08-16] ^c-1\r\n'
    assert "\r\n" in notes.canonical_content(text)
    malformed = (
        '---\nverified:\n  - {by: "bot"}\n'
        "- (quote) unterminated [failed-verification:: quote/2026-08-16] ^c-1\n"
    )
    assert notes.canonical_content(malformed) == malformed


def test_canonical_content_keeps_fenced_marker_rows_until_matching_closure():
    text = """~~~markdown
- (quote) tilde [failed-verification:: quote/2026-08-16] ^c-1
```
- (quote) mismatched [failed-verification:: quote/2026-08-16] ^c-2
~~
- (quote) short [failed-verification:: quote/2026-08-16] ^c-3
~~~~
- (quote) live [failed-verification:: quote/2026-08-16] ^c-4
"""

    canonical = notes.canonical_content(text)

    assert canonical == text


def test_canonical_content_preserves_short_fence_lookalike_outside_a_fence():
    text = "~~\nprose [failed-verification:: quote/2026-08-16]\n"

    assert notes.canonical_content(text) == text


def test_canonical_content_keeps_multiple_terminal_markers_substantive():
    text = (
        "- (quote) anchored [failed-verification:: quote/2026-08-16] "
        "[failed-verification:: citation-key/2026-08-17] ^c-1\n"
        "- (paraphrase) unanchored [failed-verification:: quote/2026-08-16] "
        "[failed-verification:: citation-key/2026-08-17]\n"
    )

    assert notes.canonical_content(text) == text


# A parsed frontmatter dict from a source line with a duplicate `by`: the
# unique key set is still exactly {by, at} (so the keyset-equality clause
# alone would accept it), but the item COUNT is 3, not 2. `len(items) != 2`
# is the sole rejecter of this shape — last-value-wins `.get("by")` would
# otherwise read the second, machine-actor-looking `by` and ignore that a
# forged decoy preceded it.
_DUPLICATE_BY_LAST_WINS = frontmatter.parse(
    '---\ngenerated: {by: "human:eran", by: "research_vault/0.1.0", '
    'at: "2026-08-24T00:00:00Z"}\n---\n'
)[0]["generated"]


@pytest.mark.parametrize(
    "value",
    [
        None,
        "not-a-dict",
        42,
        [],
        {"by": "research_vault/0.1.0"},
        {"at": "2026-08-20T12:34:56Z"},
        {"by": "research_vault/0.1.0", "at": "2026-08-20T12:34:56Z", "extra": "x"},
        {"by": "research_vault/0.1.0", "when": "2026-08-20T12:34:56Z"},
        {"by": "", "at": "2026-08-20T12:34:56Z"},
        {"by": 42, "at": "2026-08-20T12:34:56Z"},
        {"by": "research_vault/0.1.0", "at": 42},
        {"by": "research_vault/0.1.0", "at": "not-a-timestamp"},
        {"by": "research_vault/0.1.0", "at": "2026-08-20T12:34:56+00:00"},
        {"by": "research_vault/0.1.0", "at": "2026-08-20"},
        _DUPLICATE_BY_LAST_WINS,
    ],
    ids=[
        "none",
        "string",
        "int",
        "empty-list",
        "missing-at",
        "missing-by",
        "extra-key",
        "wrong-key-names",
        "empty-by",
        "by-not-a-string",
        "at-not-a-string",
        "at-unparseable",
        "at-offset-not-z",
        "at-date-only",
        "duplicate-by-last-wins",
    ],
)
def test_valid_generated_rejects_every_malformed_shape(value):
    assert notes._valid_generated(value) is False


def test_valid_generated_accepts_the_one_true_shape():
    assert (
        notes._valid_generated(
            {"by": "research_vault/0.1.0", "at": "2026-08-20T12:34:56Z"}
        )
        is True
    )


# --- `generated_at_now`: the one spelling of "now" --------------------------


def test_generated_at_now_output_satisfies_valid_generated():
    stamp = notes.generated_at_now()
    assert stamp.endswith("Z")
    assert "." not in stamp
    assert notes._valid_generated({"by": AGENT_ACTOR, "at": stamp}) is True


def test_generated_at_now_truncates_microseconds_and_formats_utc_offset_as_z():
    moment = datetime.datetime(2026, 8, 24, 15, 4, 5, 123456, tzinfo=datetime.UTC)

    assert notes.generated_at_now(moment) == "2026-08-24T15:04:05Z"


# --- the citekey -> citationKey migration (ingest spec §1.1) ----------------


def test_rename_frontmatter_key_is_byte_surgical():
    text = '---\ncitekey: "smith2020"\ntype: "literature"\n---\n# T\ncitekey: in body\n'
    renamed = notes.rename_frontmatter_key(text, "citekey", "citationKey")
    assert (
        renamed
        == '---\ncitationKey: "smith2020"\ntype: "literature"\n---\n# T\ncitekey: in body\n'
    )
    assert notes.rename_frontmatter_key(renamed, "citekey", "citationKey") == renamed
    assert (
        notes.rename_frontmatter_key("no frontmatter\n", "citekey", "citationKey")
        == "no frontmatter\n"
    )
    # `new` is inserted literally, never read as a replacement template (row 14).
    assert notes.rename_frontmatter_key(text, "citekey", "a\\g<0>b").startswith(
        '---\na\\g<0>b: "smith2020"\n'
    )


def test_invalid_citation_key_error_is_the_spelling():
    with pytest.raises(notes.InvalidCitationKeyError):
        notes.note_path("/tmp", "a/b")  # noqa: S108


# --- the literature note record: snapshot, provenance tuple, body (ingest spec §3.2) ---

PROVENANCE = notes.Provenance(
    server_id="6LpvURP2E933",
    item_key="E352DFS8",
    item_version=544,
    citation_key="jakesch.etal2023a",
    attachments=(
        {
            "key": "D7EJ9FTG",
            "version": 551,
            "md5": "aa59569ae4f4b3a7c546158d4771c738",
            "contentType": "application/pdf",
            "filename": "Jakesch et al. - 2023.pdf",
        },
    ),
    fulltext=({"attachment-key": "D7EJ9FTG", "sha256": "f" * 64},),
    compile_input_sha256="f" * 64,
)


def _render(existing=None, generated_at="2026-09-07T10:00:00Z", pages=()):
    return notes.render_note(
        ITEM["data"],
        PROVENANCE,
        [ATTACHMENT],
        [CHILD_NOTE],
        existing,
        accessed="2026-09-07",
        generated_at=generated_at,
        pages=pages,
    )


def test_render_note_carries_snapshot_tuple_and_witness_in_order():
    text = _render()
    data, _body = frontmatter.parse(text)
    keys = list(data)
    assert keys[:3] == ["type", "title", "aliases"]
    assert data["type"] == "literature"
    assert data["aliases"] == [ITEM["data"]["title"]]
    assert data["creators"] == [
        {"creatorType": "author", "firstName": "Maurice", "lastName": "Jakesch"}
    ]
    assert (
        data["abstractNote"] == ["Line one.", "Line two."]
    )  # ITEM's second line carries a tab and a double space; display_text collapses both
    assert data["extra"] == ["PMID: 28503678", "PMCID: PMC5428074"]
    assert data["tags"] == [{"tag": "ai", "type": 1}]
    assert data["DOI"] == "10.1145/3544548.3581196"
    assert "relations" not in data
    assert "dateModified" not in data
    assert data["zotero-server-id"] == "6LpvURP2E933"
    assert data["zotero-item-key"] == "E352DFS8"
    assert data["zotero-item-version"] == 544
    assert data["citationKey"] == "jakesch.etal2023a"
    assert data["attachments"][0]["md5"] == "aa59569ae4f4b3a7c546158d4771c738"
    assert data["fulltext"] == [{"attachment-key": "D7EJ9FTG", "sha256": "f" * 64}]
    assert data["compile-input-sha256"] == "f" * 64
    assert data["accessed"] == "2026-09-07"
    assert data["managed-sha256"] == notes.body_sha256(text)
    assert data["generated"] == {"by": AGENT_ACTOR, "at": "2026-09-07T10:00:00Z"}
    assert keys.index("generated") == len(keys) - 1


def test_body_renders_only_what_frontmatter_cannot_carry():
    _data, body = frontmatter.parse(_render())
    assert body == (
        "## Item\n\n"
        "- [Open in Zotero](zotero://select/library/items/E352DFS8)\n\n"
        "## Attachments\n\n"
        "- [Jakesch et al. - 2023.pdf](zotero://open-pdf/library/items/D7EJ9FTG) "
        "— application/pdf, md5 aa59569ae4f4b3a7c546158d4771c738, text layer [[fulltext/D7EJ9FTG]]\n\n"
        "## Zotero notes\n\n"
        "Read for the method.\n\nSecond paragraph.\n"
    )
    assert "Co-writing" not in body  # title lives in frontmatter only
    assert "## Compiled" not in body  # absent until the first compile (§3.3 step 5)


def test_body_embeds_the_compiled_page_by_ledger_path_when_one_exists():
    _data, body = frontmatter.parse(
        _render(pages=["wiki/sources/Co-Writing with Opinionated Language Models.md"])
    )
    assert body.startswith(
        "## Compiled\n\n![[wiki/sources/Co-Writing with Opinionated Language Models.md]]\n\n## Item\n\n"
    )


def test_compiled_pages_reads_the_ledger_by_locator(tmp_path):
    assert notes.compiled_pages(tmp_path, PROVENANCE) == []
    ledger = tmp_path / "wiki" / "meta" / "ledgers" / "source-ledger.json"
    ledger.parent.mkdir(parents=True)
    ledger.write_text(
        json.dumps(
            {
                "schema": "claude-obsidian.source-ledger.v1",
                "sources": {
                    "src-1": {
                        "origin": {"kind": "file", "locator": "fulltext/D7EJ9FTG.md"},
                        "pages": ["wiki/sources/B.md", "wiki/sources/A.md"],
                    },
                    "src-2": {
                        "origin": {"kind": "file", "locator": "fulltext/OTHER001.md"},
                        "pages": ["wiki/sources/C.md"],
                    },
                },
            }
        )
    )
    assert notes.compiled_pages(tmp_path, PROVENANCE) == [
        "wiki/sources/A.md",
        "wiki/sources/B.md",
    ]


def test_compiled_pages_missing_ledger_is_a_true_empty(tmp_path):
    assert not (tmp_path / notes.LEDGER_PATH).exists()
    assert notes.compiled_pages(tmp_path, PROVENANCE) == []


@pytest.mark.parametrize(
    "payload",
    [
        b"not json",
        b"\xff\xfe",
        b"[]",
        b"{}",
        b'{"sources": null}',
        b'{"sources": []}',
    ],
    ids=[
        "not-json",
        "not-utf8",
        "top-level-array",
        "no-sources-key",
        "sources-null",
        "sources-not-an-object",
    ],
)
def test_compiled_pages_unreadable_ledger_raises_rather_than_reading_as_empty(
    tmp_path, payload
):
    """Four-state: a missing ledger and an unreadable one must not share a value.

    Capture writes the note from this value, so an unreadable ledger reading as
    `[]` would strip `## Compiled`, bump `generated`, and break decision 27's
    third-run NOOP — silently, since the next readable run re-adds it. A
    document the tool's schema would never write (no `sources` object) is
    malformed, not "no compile yet", and lands here too.
    """
    ledger = tmp_path / notes.LEDGER_PATH
    ledger.parent.mkdir(parents=True)
    ledger.write_bytes(payload)
    with pytest.raises(notes.LedgerUnreadableError) as caught:
        notes.compiled_pages(tmp_path, PROVENANCE)
    # Subject first: capture's hold reason and this error both start with
    # "<ledger path> unreadable".
    assert str(caught.value).startswith(f"{notes.LEDGER_PATH} unreadable: ")
    assert "source-ledger.json unreadable" in str(caught.value)
    # Only the decode branch has an underlying error to report; the schema
    # branch must not invent one.
    assert "None" not in str(caught.value)
    # Not a ValueError or OSError: a caller's broad `except` around the JSON
    # read cannot fold the outage back into the empty it is not.
    assert not issubclass(notes.LedgerUnreadableError, (ValueError, OSError))


def test_compiled_pages_schema_conformant_empty_ledger_is_the_one_true_empty(
    tmp_path,
):
    """`{"sources": {}}` is what the tool writes before any source is registered:
    the one present-and-empty shape that must still yield `[]`."""
    ledger = tmp_path / notes.LEDGER_PATH
    ledger.parent.mkdir(parents=True)
    ledger.write_text(
        json.dumps({"schema": "claude-obsidian.source-ledger.v1", "sources": {}})
    )
    assert notes.compiled_pages(tmp_path, PROVENANCE) == []


def test_rerender_keeps_accessed_generated_and_foreign_fields_when_unchanged():
    first = _render()
    with_events = must_replace(
        first,
        "---\n## Item",
        'verified:\n  - {by: "research_vault/0.1.0", at: "2026-09-07", check: "update-notice"}\n---\n## Item',
    )
    second = notes.render_note(
        ITEM["data"],
        PROVENANCE,
        [ATTACHMENT],
        [CHILD_NOTE],
        with_events,
        accessed="2026-09-08",
        generated_at="2026-09-08T00:00:00Z",
    )
    data, _ = frontmatter.parse(second)
    assert data["accessed"] == "2026-09-07"
    assert data["generated"]["at"] == "2026-09-07T10:00:00Z"
    assert data["verified"][0]["check"] == "update-notice"
    assert not notes.content_changed(with_events, second)


def test_rerender_bumps_generated_when_the_projection_moved():
    first = _render()
    moved = dataclasses.replace(PROVENANCE, item_version=545)
    second = notes.render_note(
        ITEM["data"],
        moved,
        [ATTACHMENT],
        [CHILD_NOTE],
        first,
        accessed="2026-09-08",
        generated_at="2026-09-08T00:00:00Z",
    )
    data, _ = frontmatter.parse(second)
    assert data["zotero-item-version"] == 545
    assert data["generated"]["at"] == "2026-09-08T00:00:00Z"
    assert data["accessed"] == "2026-09-07"


def test_read_provenance_round_trips_and_rejects_partial_tuples():
    text = _render()
    assert notes.read_provenance(text) == PROVENANCE
    assert (
        notes.read_provenance('---\ntype: "literature"\ncitationKey: "x"\n---\n')
        is None
    )
    assert notes.read_provenance("no frontmatter") is None


def test_linked_attachment_says_it_has_no_fixity():
    linked = {
        "key": "LINK0001",
        "version": 3,
        "data": {
            "key": "LINK0001",
            "version": 3,
            "itemType": "attachment",
            "linkMode": "linked_url",
            "url": "https://x",
        },
    }
    text = notes.render_note(
        ITEM["data"],
        dataclasses.replace(
            PROVENANCE,
            attachments=(
                {
                    "key": "LINK0001",
                    "version": 3,
                    "md5": "absent",
                    "contentType": "",
                    "filename": "",
                },
            ),
            fulltext=(),
            compile_input_sha256=None,
        ),
        [linked],
        [],
        None,
        accessed="2026-09-07",
        generated_at="2026-09-07T10:00:00Z",
    )
    data, body = frontmatter.parse(text)
    assert data["attachments"][0]["md5"] == "absent"
    assert "compile-input-sha256" not in data
    assert "- LINK0001 — linked, no fixity" in body


def test_canonical_content_excludes_the_verifier_owned_failure_rows():
    """The `failed-verification` list `events.record_failure` writes and
    `record_pass` removes is the tool's own record, excluded from the scope
    exactly as `verified` events are; a row that fails the verifier-owned
    shape stays byte for byte."""
    from research_vault import events

    base = _note()
    failed = events.record_failure(base, "doi", Result.UNMATCHED)
    passed = events.record_pass(failed, "doi", Result.MATCHED, at="2026-08-16")
    assert failed != base
    assert passed != failed
    assert notes.canonical_content(failed) == notes.canonical_content(base)
    assert notes.canonical_content(passed) == notes.canonical_content(base)
    assert notes.content_changed(base, failed) is False

    hand_written = must_replace(
        failed,
        'failed-verification:\n  - {check: "doi", result: "UNMATCHED"}\n',
        'failed-verification:\n  - {check: "doi", result: "MATCHED"}\n',
    )
    assert notes.canonical_content(hand_written) == hand_written

    body = "- (quote) body ^c-1\n"
    enveloped = events.record_failure(body, "doi", Result.UNMATCHED)
    assert enveloped.startswith("---\nfailed-verification:\n")
    assert notes.canonical_content(enveloped) == body


# --- boundaries pinned against mutation survivors -----------------------------


def test_canonical_content_drops_an_empty_verified_list_that_closes_the_frontmatter():
    """The owned-list header is found anywhere before the closing delimiter,
    including on the line right above it."""
    text = '---\ntitle: "x"\nverified:\n---\nbody\n'
    assert notes.canonical_content(text) == '---\ntitle: "x"\n---\nbody\n'


def test_rename_frontmatter_key_renames_the_first_of_a_duplicated_key_only():
    assert notes.rename_frontmatter_key("---\na: 1\na: 2\n---\n", "a", "b") == (
        "---\nb: 1\na: 2\n---\n"
    )


def test_rename_frontmatter_key_reaches_a_key_below_the_first_line_of_the_block():
    assert notes.rename_frontmatter_key(
        "---\nx: 0\na: 1\n---\na: body\n", "a", "b"
    ) == ("---\nx: 0\nb: 1\n---\na: body\n")


def test_canonical_content_owns_a_verified_header_with_trailing_blanks():
    text = (
        '---\ntitle: "x"\nverified:  \t\n  - {by: "bot", at: "2026-08-16"}\n---\nbody\n'
    )
    assert notes.canonical_content(text) == '---\ntitle: "x"\n---\nbody\n'


def test_render_note_writes_the_title_once():
    assert _render().count("\ntitle:") == 1


def test_attachment_line_names_an_imported_url_attachment_with_its_md5():
    child = {
        "key": "URL00001",
        "data": {"linkMode": "imported_url", "md5": "abc", "filename": "page.html"},
    }
    line = notes._attachment_line(child)
    assert line.startswith("- [page.html](zotero://open-pdf/library/items/URL00001)")
    assert "no fixity" not in line


def test_read_provenance_reads_a_tuple_without_list_fields_and_refuses_a_bad_item_key():
    """A note whose tuple carries no `attachments:`/`fulltext:` keys at all is
    a complete tuple with empty lists; an item key that is not eight
    characters of [A-Z0-9] is no tuple even when the citation key is fine."""
    bare = (
        '---\nzotero-server-id: "S"\nzotero-item-key: "E352DFS8"\n'
        'zotero-item-version: 1\ncitationKey: "x"\n---\n'
    )
    assert notes.read_provenance(bare) == notes.Provenance(
        "S", "E352DFS8", 1, "x", (), (), None
    )
    bad_key = bare.replace('"E352DFS8"', '"bad"')
    assert notes.read_provenance(bad_key) is None


def test_attachment_line_needs_both_an_imported_link_mode_and_an_md5():
    linked_with_md5 = {
        "key": "LINK0001",
        "data": {"linkMode": "linked_file", "md5": "abc", "filename": "f.pdf"},
    }
    imported_without_md5 = {
        "key": "IMP00001",
        "data": {"linkMode": "imported_file", "filename": "f.pdf"},
    }
    assert notes._attachment_line(linked_with_md5) == "- LINK0001 — linked, no fixity"
    assert (
        notes._attachment_line(imported_without_md5) == "- IMP00001 — linked, no fixity"
    )


def test_render_body_ends_with_one_newline_and_joins_the_child_notes_it_can_read():
    prov = notes.Provenance("S", "E352DFS8", 1, "x", (), (), None)
    assert notes.render_body(prov, [], []) == (
        "## Item\n\n- [Open in Zotero](zotero://select/library/items/E352DFS8)\n"
    )
    child_notes = [
        {"data": {"note": "<p>a</p>"}},
        {"data": {}},
        {"key": "N0DATA01"},
        {"data": {"note": "<p>b</p>"}},
    ]
    assert notes.render_body(prov, [], child_notes) == (
        "## Item\n\n- [Open in Zotero](zotero://select/library/items/E352DFS8)\n\n"
        "## Zotero notes\n\na\n\nb\n"
    )


def test_rerender_replaces_a_blank_or_non_string_prior_accessed_and_drops_a_stale_capture_field():
    """`accessed` is kept from the prior note only when it is a non-empty
    string; a capture field the new tuple no longer renders (here the compile
    digest) is not carried over from the prior note."""
    first = _render()
    for prior_accessed in ('""', "2026"):
        prior = must_replace(
            first, 'accessed: "2026-09-07"', f"accessed: {prior_accessed}"
        )
        data, _ = frontmatter.parse(
            notes.render_note(
                ITEM["data"],
                PROVENANCE,
                [ATTACHMENT],
                [CHILD_NOTE],
                prior,
                accessed="2026-09-08",
                generated_at="2026-09-08T00:00:00Z",
            )
        )
        assert data["accessed"] == "2026-09-08"
    without_digest = dataclasses.replace(PROVENANCE, compile_input_sha256=None)
    data, _ = frontmatter.parse(
        notes.render_note(
            ITEM["data"],
            without_digest,
            [ATTACHMENT],
            [CHILD_NOTE],
            first,
            accessed="2026-09-08",
            generated_at="2026-09-08T00:00:00Z",
        )
    )
    assert "compile-input-sha256" not in data
