"""Literature-note generation: managed region + preserved free region (spec §3–§5)."""

import datetime
import hashlib
import unicodedata
from html import escape
from pathlib import Path

from . import AGENT_ACTOR, frontmatter

MANAGED_OPEN = "%%hk-managed%%"
MANAGED_CLOSE = "%%/hk-managed%%"
SEED_FREE = "\n## Notes\n"


class InvalidCitekeyError(ValueError):
    """A citekey that cannot safely name one file in ``literatures``."""


def note_path(vault_root, citekey) -> Path:
    if (
        not isinstance(citekey, str)
        or not citekey
        or citekey in {".", ".."}
        or "/" in citekey
        or "\\" in citekey
        or "\0" in citekey
        or Path(citekey).is_absolute()
    ):
        raise InvalidCitekeyError(f"unsafe citekey: {citekey!r}")
    return Path(vault_root) / "literatures" / f"{citekey}.md"


def _managed_body(item, annotations) -> str:
    lines = [MANAGED_OPEN, f"# {item.get('title', item['id'])}", ""]
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
    fm["aliases"] = [item.get("title", item["id"])]
    managed_body = _managed_body(item, annotations)
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
    return frontmatter.serialize(fm) + managed_body + _split_free(existing)


def _norm(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).split())


def claim_id(annotation: dict) -> str:
    basis = annotation.get("key") or _norm(annotation.get("annotationText", ""))
    return "c-" + hashlib.sha256(basis.encode()).hexdigest()[:8]


def _escape_selector(value: str) -> str:
    """Escape selector attributes without allowing markup to span source lines."""
    return escape(value, quote=True).replace("\r", "&#13;").replace("\n", "&#10;")


def render_claim(annotation: dict) -> str:
    cid = claim_id(annotation)
    cite = (
        f"[@{annotation['citekey']}, p. {annotation['pageLabel']}]"
        if annotation.get("pageLabel")
        else f"[@{annotation['citekey']}]"
    )
    text = annotation.get("annotationText") or ""
    if text:
        lines = [f"- (quote) {cite} ^{cid}"]
        lines.extend(f"  > {line}" for line in text.split("\n"))
        pre, suf = annotation.get("context_prefix"), annotation.get("context_suffix")
        if pre or suf:
            prefix = _escape_selector((pre or "")[-32:])
            suffix = _escape_selector((suf or "")[:32])
            lines.append(f'  <!-- hk-sel prefix="{prefix}" suffix="{suffix}" -->')
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
