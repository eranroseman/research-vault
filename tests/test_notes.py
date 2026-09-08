import datetime
import hashlib

import pytest

from research_vault import AGENT_ACTOR, Result, frontmatter, notes

LITERATURE = '---\ncitekey: "smith2020"\ntype: "literature"\n'
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
    "citekey",
    # An absolute-path ESCAPE fixture: the value is a citekey that note_path must
    # reject, never a temporary file this test writes to.
    ["", "../escape", "/tmp/escape", "..\\escape", "nested/escape"],  # noqa: S108
)
def test_note_path_rejects_unsafe_citekeys(tmp_vault, citekey):
    with pytest.raises(notes.InvalidCitekeyError):
        notes.note_path(tmp_vault, citekey)


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

    stale = good.replace(body.encode(), b"# Edited\n")
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
    for name in ("MANAGED_OPEN", "managed_slice_bytes", "render_note", "render_claim"):
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
    note = text.replace(original_line, duplicate, 1).encode()

    result, reason = notes.validate_managed_witness(note)

    assert result is Result.UNMATCHED
    assert reason.startswith("schema-violation")


def test_generated_metadata_is_substantive_canonical_content():
    first = _note(generated="2026-08-20T12:34:56Z")
    changed = first.replace("2026-08-20T12:34:56Z", "2026-08-21T01:02:03Z")

    assert notes.content_changed(first, changed)


def test_content_changed_compares_only_the_verifier_owned_surface():
    base = _note()
    verified = base.replace(
        "---\n# Mortality decline\n",
        'verified:\n  - {by: "bot", at: "2026-08-16", check: "quote"}\n'
        "---\n# Mortality decline\n",
        1,
    )
    changed = _note(body="# Updated title\n")

    assert notes.content_changed(base, verified) is False
    assert notes.content_changed(base, changed) is True
    assert notes.content_changed(None, base) is True


def test_canonical_content_excludes_only_valid_verifier_owned_surfaces():
    base = """---
citekey: "x"
verified:
  - {by: "bot", at: "2026-08-16", check: "doi"}
status: "included"
---
- (quote) text [failed-verification:: quote/2026-08-16] ^c-1
plain [failed-verification:: quote/2026-08-16]
"""
    changed_events = base.replace('check: "doi"', 'check: "metadata"')
    changed_marker = base.replace("quote/2026-08-16", "quote/2026-08-17", 1)
    deprecated = base.replace('status: "included"', 'status: "deprecated"')

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
citekey: "x"
status: "included"
deprecated-at: ""
deprecated-by: ""
reason: ""
---
body
"""
    transitions = [
        base.replace('status: "included"', 'status: "deprecated"'),
        base.replace('deprecated-at: ""', 'deprecated-at: "2026-08-16"'),
        base.replace('deprecated-by: ""', 'deprecated-by: "human:eran"'),
        base.replace('reason: ""', 'reason: "superseded source"'),
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
        "[failed-verification:: citekey/2026-08-17] ^c-1\n"
        "- (paraphrase) unanchored [failed-verification:: quote/2026-08-16] "
        "[failed-verification:: citekey/2026-08-17]\n"
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
