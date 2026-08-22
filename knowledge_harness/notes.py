"""Literature-note generation: managed region + preserved free region (spec §3–§5)."""

import datetime
import hashlib
import re
import unicodedata
from html import escape
from pathlib import Path

from . import AGENT_ACTOR, Result, frontmatter

MANAGED_OPEN = "%%hk-managed%%"
MANAGED_CLOSE = "%%/hk-managed%%"
MANAGED_OPEN_BYTES = MANAGED_OPEN.encode("ascii")
MANAGED_CLOSE_BYTES = MANAGED_CLOSE.encode("ascii")
SEED_FREE = "\n## Notes\n"


class InvalidCitekeyError(ValueError):
    """A citekey that cannot safely name one file in ``literatures``."""


class ManagedRegionError(ValueError):
    """The exact byte-level managed delimiter grammar is invalid."""


class RenderIntegrityError(RuntimeError):
    """The rendered managed body does not parse back to the intended claims."""


_UNSAFE_IDENTIFIER = re.compile(r"[\s\x00-\x1f\x7f]")

# Matches harness_core.frontmatter._CONTROL (C0, DEL, NEL, and the Unicode
# line/paragraph separators): every code point that some downstream parser
# treats as a line break, not only the \r/\n pair. Selector attribute values
# come from PDF-extracted context and must not be able to forge a rendered
# line using any of them.
_SELECTOR_CONTROL = re.compile(r"[\x00-\x1f\x7f\x85\u2028\u2029]")


def display_text(value) -> str:
    """Collapse a display-class value so it can never span a rendered line.

    Total by design: an import is never held on ugly-but-real metadata. Without
    a line break, injected text cannot forge a claim line, a blockquote line, a
    managed delimiter, or a frontmatter boundary.
    """
    return "" if value is None else " ".join(str(value).split())


def _raw_lines(data: bytes):
    offset = 0
    while offset < len(data):
        newline = data.find(b"\n", offset)
        if newline < 0:
            yield offset, len(data), data[offset:]
            return
        content = data[offset:newline]
        if content.endswith(b"\r"):
            content = content[:-1]
        end = newline + 1
        yield offset, end, content
        offset = end


def managed_slice_bytes(note_bytes: bytes) -> bytes:
    """Return the one exact managed slice, delimiters and line endings included."""
    if type(note_bytes) is not bytes:
        raise TypeError("note bytes must be bytes")
    openings = []
    closings = []
    for start, end, content in _raw_lines(note_bytes):
        if content == MANAGED_OPEN_BYTES:
            openings.append((start, end))
        elif content == MANAGED_CLOSE_BYTES:
            closings.append((start, end))
    if len(openings) != 1 or len(closings) != 1:
        raise ManagedRegionError("managed delimiters must each appear exactly once")
    opening_start, _ = openings[0]
    closing_start, closing_end = closings[0]
    if opening_start >= closing_start:
        raise ManagedRegionError("managed delimiters are misordered")
    return note_bytes[opening_start:closing_end]


def managed_sha256(note_bytes: bytes) -> str:
    return hashlib.sha256(managed_slice_bytes(note_bytes)).hexdigest()


def validate_managed_witness(note_bytes: bytes):
    """Return the four-state witness result without inventing I/O state."""
    try:
        text = note_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return Result.UNREACHABLE, "outage — literature note is not UTF-8"
    try:
        data, _ = frontmatter.parse(text)
        actual = managed_sha256(note_bytes)
    except (frontmatter.FrontmatterError, ManagedRegionError):
        return Result.UNMATCHED, "schema-violation — malformed managed boundary"
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
    if witness != actual:
        return Result.UNMATCHED, "schema-violation — stale managed-sha256"
    return Result.MATCHED, "matched"


def note_path(vault_root, citekey) -> Path:
    if (
        not isinstance(citekey, str)
        or not citekey
        or citekey in {".", ".."}
        or "/" in citekey
        or "\\" in citekey
        or _UNSAFE_IDENTIFIER.search(citekey) is not None
        or Path(citekey).is_absolute()
    ):
        raise InvalidCitekeyError(f"unsafe citekey: {citekey!r}")
    return Path(vault_root) / "literatures" / f"{citekey}.md"


def _managed_body(item, annotations) -> str:
    heading = display_text(item.get("title", item["id"]))
    lines = [MANAGED_OPEN, f"# {heading}", ""]
    for ann in annotations:
        lines.append(render_claim(ann))  # completed in Part B before commit/review
    lines.append(MANAGED_CLOSE)
    return "\n".join(lines) + "\n"


def _split_free(existing) -> str:
    if existing is None:
        return SEED_FREE
    offset = 0
    for line in existing.splitlines(keepends=True):
        if line in {MANAGED_CLOSE, f"{MANAGED_CLOSE}\n", f"{MANAGED_CLOSE}\r\n"}:
            # Verbatim tail after the exact standalone marker line, including
            # blank lines and a deliberately emptied free region (§3).
            return existing[offset + len(line) :]
        offset += len(line)
    return SEED_FREE


# Fields the renderer owns and may rewrite; EVERYTHING else in prior frontmatter
# passes through unchanged (verified events, superseded-by, authority, archive-url,
# human-added keys — §5 never-delete applies to metadata too).
MANAGED_FIELDS = {
    "citekey",
    "type",
    "fixity-sha256",
    "managed-sha256",
    "aliases",
    "doi",
    "url",
    "pmid",
    "version",
    "accessed",
    "generated",
}


def _prior_managed_body(existing: str | None) -> str | None:
    if existing is None:
        return None
    try:
        _, body = frontmatter.parse(existing)
    except frontmatter.FrontmatterError:
        return None
    offset = 0
    for line in body.splitlines(keepends=True):
        offset += len(line)
        if line in {MANAGED_CLOSE, f"{MANAGED_CLOSE}\n", f"{MANAGED_CLOSE}\r\n"}:
            return body[:offset]
    return None


def _managed_projection(data: dict) -> list[tuple[str, object]]:
    return [
        (key, value)
        for key, value in frontmatter._mapping_items(data)
        if key in MANAGED_FIELDS and key != "generated"
    ]


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
        parsed = datetime.datetime.fromisoformat(at.replace("Z", "+00:00"))
    except ValueError:
        return False
    return at.endswith("Z") and parsed.tzinfo is not None


def render_note(
    item, attachment_hashes, annotations, existing, accessed, generated_at=None
) -> str:
    if generated_at is None:
        generated_at = f"{accessed}T00:00:00Z"
    prior = frontmatter.parse(existing)[0] if existing else {}
    fm = {"citekey": item["id"], "type": "literature"}
    if item.get("DOI"):
        fm["doi"] = item["DOI"]
    if item.get("URL"):
        fm["url"] = item["URL"]
    if item.get("PMID"):
        fm["pmid"] = item["PMID"]
    if item.get("version"):
        fm["version"] = item["version"]
    fm["accessed"] = prior.get("accessed", accessed)  # day-one, never overwritten
    fm["fixity-sha256"] = attachment_hashes
    fm["status"] = prior.get("status", "unscreened")
    fm["aliases"] = [display_text(item.get("title", item["id"]))]
    managed_body = _managed_body(item, annotations)
    fm["managed-sha256"] = hashlib.sha256(managed_body.encode("utf-8")).hexdigest()
    prior_generated = prior.get("generated")
    prior_actor = (
        prior_generated.get("by") if isinstance(prior_generated, dict) else None
    )
    projection_changed = (
        existing is None
        or _managed_projection(prior) != _managed_projection(fm)
        or _prior_managed_body(existing) != managed_body
        or prior_actor != AGENT_ACTOR
        or not _valid_generated(prior_generated)
    )
    prior_generated_at = (
        prior_generated.get("at") if isinstance(prior_generated, dict) else None
    )
    fm["generated"] = {
        "by": AGENT_ACTOR,
        "at": generated_at if projection_changed else prior_generated_at,
    }
    rendered_keys = set(fm)
    fm_items = list(fm.items())
    for key, value in frontmatter._mapping_items(prior):
        if key not in MANAGED_FIELDS and key not in rendered_keys:
            fm_items.append((key, value))
    fm = frontmatter._mapping_from_items(fm_items)
    _assert_managed_body_parses(managed_body, annotations)
    return frontmatter.serialize(fm) + managed_body + _split_free(existing)


def _assert_managed_body_parses(managed_body: str, annotations) -> None:
    """Re-parse the emitter's own output before it can reach a note file."""
    from . import claims as claims_mod

    expected = [claim_id(annotation) for annotation in annotations]
    parsed = [
        claim.claim_id
        for claim in claims_mod.parse_claims(managed_body)
        if claim.in_managed
    ]
    if parsed != expected:
        raise RenderIntegrityError(
            f"managed body parsed to {parsed!r}, expected {expected!r}"
        )


def _norm(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).split())


def claim_id(annotation: dict) -> str:
    basis = annotation.get("key") or _norm(annotation.get("annotationText", ""))
    return "c-" + hashlib.sha256(basis.encode()).hexdigest()[:8]


def _escape_selector(value: str) -> str:
    """Escape selector attributes without allowing markup to span source lines."""
    escaped = escape(value, quote=True).replace("\r", "&#13;").replace("\n", "&#10;")
    # \r/\n keep their existing numeric-entity spelling: harness_core.selectors
    # .unescape_selector (the real round-trip consumer, via html.unescape)
    # decodes &#13;/&#10; back correctly. The rest of the control class is
    # dropped outright rather than entity-escaped the same way: per the
    # HTML5 numeric-character-reference algorithm that html.unescape follows,
    # C1 controls such as NEL (\x85) decode to unrelated Windows-1252
    # lookalikes (e.g. "&#133;" -> "…") and most other C0 references
    # decode to nothing, so entity-escaping them would corrupt rather than
    # preserve retained context on a future round trip. Stripping is lossy
    # but never silently wrong, and still guarantees no surviving code point
    # can be read back as a line break by a downstream parser.
    return _SELECTOR_CONTROL.sub("", escaped)


def render_claim(annotation: dict) -> str:
    cid = claim_id(annotation)
    citekey = annotation["citekey"]
    # Identifier class rejects rather than repairs: altering a citekey would
    # silently mis-key the claim against the bibliography.
    if not isinstance(citekey, str) or _UNSAFE_IDENTIFIER.search(citekey) is not None:
        raise InvalidCitekeyError(f"unsafe citekey: {citekey!r}")
    page_label = display_text(annotation.get("pageLabel"))
    cite = f"[@{citekey}, p. {page_label}]" if page_label else f"[@{citekey}]"
    text = annotation.get("annotationText") or ""
    if text:
        lines = [f"- (quote) {cite} ^{cid}"]
        # Segment on the parser's own break set (``claims.parse_claims`` reads
        # with ``str.splitlines()``), not on "\n" alone. A separator left inside
        # a blockquote line — \r, \v, \f, \x1c-\x1e, \x85, U+2028, U+2029 — is a
        # line break to the reader and not to the writer, so everything after it
        # loses its "  > " prefix and the quote silently truncates there. The
        # anchor is unaffected either way: ``claim_id`` hashes whitespace-
        # collapsed content, never render output (§5 anchor durability).
        lines.extend(f"  > {line}" for line in text.splitlines())
        pre, suf = annotation.get("context_prefix"), annotation.get("context_suffix")
        if pre or suf:
            prefix = _escape_selector((pre or "")[-32:])
            suffix = _escape_selector((suf or "")[:32])
            lines.append(f'  <!-- hk-selector prefix="{prefix}" suffix="{suffix}" -->')
        return "\n".join(lines)
    comment = " ".join((annotation.get("comment") or "").split())
    return f"- (paraphrase) {comment} {cite} ^{cid}"


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
