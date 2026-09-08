"""The literature note record: snapshot, provenance tuple, body (ingest spec §3.2)."""

import dataclasses
import datetime
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from . import AGENT_ACTOR, Result, frontmatter


class InvalidCitationKeyError(ValueError):
    """A citation key that cannot safely name one file in ``literatures``."""


_UNSAFE_IDENTIFIER = re.compile(r"[\s\x00-\x1f\x7f]")
# Duplicated from ``zotero.ITEM_KEY`` rather than imported, so ``notes`` stays
# transport-free.
ITEM_KEY_RE = re.compile(r"^[A-Z0-9]{8}$")

SNAPSHOT_FIELDS: tuple[str, ...] = (
    "itemType",
    "title",
    "creators",
    "date",
    "DOI",
    "url",
    "publicationTitle",
    "volume",
    "issue",
    "pages",
    "publisher",
    "ISBN",
    "language",
    "abstractNote",
    "extra",
    "accessDate",
    "tags",
)
TUPLE_FIELDS: tuple[str, ...] = (
    "zotero-server-id",
    "zotero-item-key",
    "zotero-item-version",
    "citationKey",
    "attachments",
    "fulltext",
    "compile-input-sha256",
    # generated is emitted last by render_note, after accessed and managed-sha256
    "generated",
)
CAPTURE_FIELDS: frozenset[str] = (
    frozenset(SNAPSHOT_FIELDS)
    | frozenset(TUPLE_FIELDS)
    | frozenset({"type", "aliases", "accessed", "managed-sha256"})
)
# The shape of one ``attachments`` entry (spec §3.2).
_ATTACHMENT_KEYS = ("key", "version", "md5", "contentType", "filename")
# The compile tool's ledger; captured.py and compile.py import this name.
LEDGER_PATH = "wiki/meta/ledgers/source-ledger.json"


@dataclasses.dataclass(frozen=True)
class Provenance:
    """Which Zotero objects, at which versions, produced a literature note."""

    server_id: str
    item_key: str
    item_version: int
    citation_key: str
    attachments: tuple[dict, ...]
    fulltext: tuple[dict, ...]
    compile_input_sha256: str | None


def display_text(value) -> str:
    """Collapse a display-class value so it can never span a rendered line.

    Total by design: a capture is never held on ugly-but-real metadata. Without
    a line break, injected text cannot forge a claim line, a blockquote line, a
    heading, or a frontmatter boundary.
    """
    return "" if value is None else " ".join(str(value).split())


def note_body(text: str) -> str:
    """The body below the frontmatter: capture's, compared byte for byte."""
    _data, body = frontmatter.parse(text)
    return body


def body_sha256(text: str) -> str:
    return hashlib.sha256(note_body(text).encode("utf-8")).hexdigest()


def validate_managed_witness(note_bytes: bytes) -> tuple[Result, str]:
    """Return the four-state witness result without inventing I/O state."""
    try:
        text = note_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return Result.UNREACHABLE, "outage — literature note is not UTF-8"
    try:
        data, body = frontmatter.parse(text)
    except frontmatter.FrontmatterError:
        return Result.UNMATCHED, "schema-violation — malformed frontmatter"
    witnesses = [
        value
        for key, value in frontmatter._mapping_items(data)
        if key == "managed-sha256"
    ]
    if not witnesses:
        return Result.UNMATCHED, "schema-violation — missing managed-sha256"
    if len(witnesses) != 1:
        return Result.UNMATCHED, "schema-violation — duplicate managed-sha256"
    witness = witnesses[0]
    if not isinstance(witness, str) or re.fullmatch(r"[0-9a-f]{64}", witness) is None:
        return Result.UNMATCHED, "schema-violation — invalid managed-sha256"
    if witness != hashlib.sha256(body.encode("utf-8")).hexdigest():
        return Result.UNMATCHED, "schema-violation — stale managed-sha256"
    return Result.MATCHED, "matched"


def note_path(vault_root, citation_key) -> Path:
    if (
        not isinstance(citation_key, str)
        or not citation_key
        or citation_key in {".", ".."}
        or "/" in citation_key
        or "\\" in citation_key
        or _UNSAFE_IDENTIFIER.search(citation_key) is not None
        or Path(citation_key).is_absolute()
    ):
        raise InvalidCitationKeyError(f"unsafe citation key: {citation_key!r}")
    return Path(vault_root) / "literatures" / f"{citation_key}.md"


def rename_frontmatter_key(text: str, old: str, new: str) -> str:
    """Rename one top-level frontmatter key without touching anything else.

    The one migration §1.1 prices as carrying real risk: byte-surgical on the
    key's own line, inside the frontmatter block only, idempotent.
    """
    opening = frontmatter._FRONTMATTER_OPEN.match(text)
    if opening is None:
        return text
    closing = frontmatter._FRONTMATTER_CLOSE.search(text, opening.end())
    if closing is None:
        return text
    block = text[opening.end() : closing.start()]
    renamed = re.sub(
        rf"^{re.escape(old)}:(?=\s)", f"{new}:", block, count=1, flags=re.MULTILINE
    )
    return text[: opening.end()] + renamed + text[closing.start() :]


def _valid_generated(value) -> bool:
    if not isinstance(value, dict):
        return False
    items = list(frontmatter._mapping_items(value))
    if len(items) != 2 or {key for key, _ in items} != {"by", "at"}:
        return False
    actor, at = value.get("by"), value.get("at")
    if not isinstance(actor, str) or not actor or not isinstance(at, str):
        return False
    try:
        parsed = datetime.datetime.fromisoformat(at)
    except ValueError:
        return False
    return at.endswith("Z") and parsed.tzinfo is not None


def generated_at_now(now: datetime.datetime | None = None) -> str:
    """Second-resolution, ``Z``-suffixed ISO 8601 — the one spelling every
    ``generated.at`` stamp of "now" uses, so they cannot drift into formats
    `_valid_generated` disagrees on.
    """
    moment = now if now is not None else datetime.datetime.now(datetime.UTC)
    return moment.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_changed(existing_text, candidate_text) -> bool:
    return existing_text is None or canonical_content(
        existing_text
    ) != canonical_content(candidate_text)


def canonical_content(note_text: str) -> str:
    """Exclude only a valid verifier-owned ``verified`` event list."""
    close, lines = _frontmatter_close(note_text)
    if close is None:
        return note_text
    if close < 0:
        # Do not infer body structure from an unterminated verifier boundary.
        return note_text
    try:
        data, _ = frontmatter.parse(note_text)
    except frontmatter.FrontmatterError:
        return note_text
    from .events import _valid_event

    verified = data.get("verified")
    valid_verified = isinstance(verified, list) and all(
        _valid_event(event) for event in verified
    )
    frontmatter_lines = lines[: close + 1]
    body = "".join(lines[close + 1 :])
    if not valid_verified:
        return note_text
    verified_index = _verified_list_index(frontmatter_lines)
    if verified_index is None:
        # A duplicate or non-list-looking lexical definition is not a
        # verifier-owned surface, even if the permissive flat parser kept a
        # list under the final key.
        return note_text
    if _verified_only_envelope(frontmatter_lines, verified_index):
        return body
    result = frontmatter_lines[:verified_index]
    index = verified_index + 1
    while index < close and frontmatter_lines[index].startswith("  - "):
        index += 1
    result.extend(frontmatter_lines[index:])
    return "".join(result) + body


def _frontmatter_close(text: str) -> tuple[int | None, list[str]]:
    """Return the closing delimiter line, or a malformed-frontmatter sentinel."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0] not in {"---\n", "---\r\n"}:
        return None, lines
    for index, line in enumerate(lines[1:], start=1):
        if line in {"---\n", "---\r\n"}:
            return index, lines
    return -1, lines


def _verified_list_index(lines: list[str]) -> int | None:
    """Find one syntactically top-level ``verified:`` event-list header."""
    verified_lines = [
        index for index, line in enumerate(lines[:-1]) if line.startswith("verified:")
    ]
    if len(verified_lines) != 1:
        return None
    index = verified_lines[0]
    if lines[index].rstrip("\r\n").rstrip(" \t") != "verified:":
        return None
    return index


def _verified_only_envelope(lines: list[str], verified_index: int) -> bool:
    """Whether frontmatter is solely the valid verifier-owned event list."""
    return verified_index == 1 and all(
        line.startswith("  - ") for line in lines[verified_index + 1 : -1]
    )


# --- the record: snapshot, tuple, body (ingest spec §3.2, §3.3 step 5) ---------


def frontmatter_value(value):
    """Decision 9: a string with line breaks becomes a list of its lines."""
    if isinstance(value, str):
        # Each line goes through display_text: the codec rejects every C0 control,
        # and a tab inside an abstract must not hold the whole capture.
        lines = [display_text(line) for line in value.splitlines()]
        return lines if len(lines) > 1 else display_text(value)
    if isinstance(value, list):
        return [
            {k: display_text(v) if isinstance(v, str) else v for k, v in item.items()}
            if isinstance(item, dict)
            else display_text(item)
            for item in value
        ]
    return value


def snapshot(item_data) -> list[tuple[str, object]]:
    """The fixed subset, verbatim, under Zotero's own names; empty values absent."""
    fields: list[tuple[str, object]] = []
    for name in SNAPSHOT_FIELDS:
        value = item_data.get(name)
        if value in (None, "", []):
            continue
        fields.append((name, frontmatter_value(value)))
    return fields


class _TextExtractor(HTMLParser):
    _BREAKS = frozenset(
        {"p", "br", "li", "div", "h1", "h2", "h3", "h4", "h5", "h6", "tr"}
    )

    def __init__(self):
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag, _attrs):
        if tag in self._BREAKS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self._BREAKS:
            self.parts.append("\n")

    def handle_data(self, data):
        self.parts.append(data)


def html_to_text(html: str) -> str:
    """Zotero child notes are HTML; the body carries their text, paragraphs kept."""
    extractor = _TextExtractor()
    extractor.feed(html or "")
    paragraphs = [" ".join(p.split()) for p in "".join(extractor.parts).split("\n")]
    return "\n\n".join(p for p in paragraphs if p)


def _attachment_line(child) -> str:
    data = child.get("data", {})
    key = child.get("key", "")
    if data.get("linkMode") not in {"imported_file", "imported_url"} or not data.get(
        "md5"
    ):
        return f"- {key} — linked, no fixity"
    name = display_text(data.get("filename") or key)
    return (
        f"- [{name}](zotero://open-pdf/library/items/{key}) — "
        f"{display_text(data.get('contentType'))}, md5 {data['md5']}"
    )


def compiled_pages(vault_root, provenance: Provenance) -> list[str]:
    """The ledger's pages[] for this note's text files, matched by locator (§3.3 step 5).

    Empty before the first compile. An unreadable ledger renders no embed here;
    reporting it is the captured-set lint's job, not capture's. Only records the
    wrapper wrote match (their locator is fulltext/<key>.md, spec §4.5); a record
    from any other route embeds nothing and the same lint reports it not-captured.
    """
    ledger = Path(vault_root) / LEDGER_PATH
    if not ledger.is_file():
        return []
    try:
        sources = json.loads(ledger.read_text(encoding="utf-8")).get("sources", {})
    except (OSError, UnicodeError, ValueError, AttributeError):
        return []
    locators = {
        f"fulltext/{entry.get('attachment-key')}.md" for entry in provenance.fulltext
    }
    pages: set[str] = set()
    for record in sources.values() if isinstance(sources, dict) else ():
        origin = record.get("origin", {}) if isinstance(record, dict) else {}
        if isinstance(origin, dict) and origin.get("locator") in locators:
            pages.update(
                page for page in record.get("pages", []) if isinstance(page, str)
            )
    return sorted(pages)


def render_body(provenance: Provenance, children, child_notes, pages=()) -> str:
    """The three mechanical pointers and the child notes (decision 27), in order."""
    cached = {entry["attachment-key"] for entry in provenance.fulltext}
    lines: list[str] = []
    if pages:
        lines.append("## Compiled\n")
        lines.extend(f"![[{page}]]" for page in pages)
        lines.append("")
    lines.append("## Item\n")
    lines.append(
        f"- [Open in Zotero](zotero://select/library/items/{provenance.item_key})"
    )
    lines.append("")
    attachments = [
        c for c in children if c.get("data", {}).get("itemType") == "attachment"
    ]
    if attachments:
        lines.append("## Attachments\n")
        for child in attachments:
            line = _attachment_line(child)
            if child.get("key") in cached:
                line += f", text layer [[fulltext/{child['key']}]]"
            lines.append(line)
        lines.append("")
    notes_text = [html_to_text(n.get("data", {}).get("note", "")) for n in child_notes]
    notes_text = [t for t in notes_text if t]
    if notes_text:
        lines.append("## Zotero notes\n")
        lines.append("\n\n".join(notes_text))
    body = "\n".join(lines)
    return body + "\n" if body and not body.endswith("\n") else body


def _tuple_fields(provenance: Provenance) -> list[tuple[str, object]]:
    fields: list[tuple[str, object]] = [
        ("zotero-server-id", provenance.server_id),
        ("zotero-item-key", provenance.item_key),
        ("zotero-item-version", provenance.item_version),
        ("citationKey", provenance.citation_key),
        ("attachments", [dict(a) for a in provenance.attachments]),
        ("fulltext", [dict(f) for f in provenance.fulltext]),
    ]
    if provenance.compile_input_sha256:
        fields.append(("compile-input-sha256", provenance.compile_input_sha256))
    return fields


def _projection(items) -> list[tuple[str, object]]:
    """The capture fields that decide whether the projection moved."""
    return [
        (k, v)
        for k, v in items
        if k in CAPTURE_FIELDS and k not in {"generated", "managed-sha256", "accessed"}
    ]


def render_note(
    item_data,
    provenance,
    children,
    child_notes,
    existing,
    accessed,
    generated_at,
    pages=(),
) -> str:
    """Frontmatter, then only what frontmatter cannot carry, plus the three pointers (§3.3 step 5)."""
    prior = frontmatter.parse(existing)[0] if existing else {}
    prior_items = list(frontmatter._mapping_items(prior))
    title = display_text(item_data.get("title") or provenance.citation_key)
    fields: list[tuple[str, object]] = [
        ("type", "literature"),
        ("title", title),
        ("aliases", [title]),
    ]
    fields.extend((k, v) for k, v in snapshot(item_data) if k != "title")
    fields.extend(_tuple_fields(provenance))
    body = render_body(provenance, children, child_notes, pages)
    prior_body = note_body(existing) if existing else None
    unchanged = (
        existing is not None
        and _projection(prior_items) == _projection(fields)
        and prior_body == body
        and _valid_generated(prior.get("generated"))
        and str(prior["generated"]["by"]).startswith(AGENT_ACTOR.split("/")[0] + "/")
    )
    prior_accessed = prior.get("accessed")
    fields.append(
        (
            "accessed",
            prior_accessed
            if isinstance(prior_accessed, str) and prior_accessed
            else accessed,
        )
    )
    fields.append(("managed-sha256", hashlib.sha256(body.encode("utf-8")).hexdigest()))
    at = prior["generated"]["at"] if unchanged else generated_at
    fields.append(("generated", {"by": AGENT_ACTOR, "at": at}))
    rendered = {k for k, _ in fields}
    fields.extend(
        (k, v) for k, v in prior_items if k not in CAPTURE_FIELDS and k not in rendered
    )
    return frontmatter.serialize(frontmatter._mapping_from_items(fields)) + body


def read_provenance(text: str) -> Provenance | None:
    """The tuple a note records, or None when it carries no complete tuple."""
    try:
        data, _ = frontmatter.parse(text)
    except frontmatter.FrontmatterError:
        return None
    try:
        attachments = tuple(
            dict(a) for a in data.get("attachments", []) if isinstance(a, dict)
        )
        fulltext = tuple(
            dict(f) for f in data.get("fulltext", []) if isinstance(f, dict)
        )
        provenance = Provenance(
            server_id=str(data["zotero-server-id"]),
            item_key=str(data["zotero-item-key"]),
            item_version=int(data["zotero-item-version"]),
            citation_key=str(data["citationKey"]),
            attachments=attachments,
            fulltext=fulltext,
            compile_input_sha256=data.get("compile-input-sha256") or None,
        )
    except (KeyError, TypeError, ValueError):
        return None
    if not ITEM_KEY_RE.match(provenance.item_key) or not provenance.citation_key:
        return None
    return provenance
