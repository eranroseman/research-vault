"""Literature-note generation: managed region + preserved free region (spec §3–§5)."""

import hashlib
import re
import unicodedata
from html import escape
from pathlib import Path

from . import frontmatter

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
    "attachment-sha256",
    "aliases",
    "doi",
    "url",
    "pmid",
    "version",
}


def render_note(item, attachment_hashes, annotations, existing, retrieved) -> str:
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
    fm["retrieved"] = prior.get("retrieved", retrieved)  # day-one, never overwritten
    fm["attachment-sha256"] = attachment_hashes
    fm["status"] = prior.get("status", "unreviewed")
    fm["aliases"] = [item.get("title", item["id"])]
    rendered_keys = set(fm)
    fm_items = list(fm.items())
    for key, value in frontmatter._mapping_items(prior):
        if key not in MANAGED_FIELDS and key not in rendered_keys:
            fm_items.append((key, value))
    fm = frontmatter._mapping_from_items(fm_items)
    return (
        frontmatter.serialize(fm)
        + _managed_body(item, annotations)
        + _split_free(existing)
    )


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


_VERIFY_MARKER = r"\[verify-failed:: [A-Za-z0-9-]+/\d{4}-\d{2}-\d{2}\]"
_VERIFY_BEFORE_ANCHOR = re.compile(
    r" " + _VERIFY_MARKER + r" (?=\^[A-Za-z0-9-]+[ \t]*$)"
)
_VERIFY_TERMINAL = re.compile(r" " + _VERIFY_MARKER + r"(?=[ \t]*$)")
_CLAIM_LINE = re.compile(r"^- \((?:quote|paraphrase|inference|open-question)\) ")
_FENCE_OPEN = re.compile(r"^[ \t]{0,3}(?P<fence>`{3,}|~{3,})")
_FENCE_CLOSE = re.compile(r"^[ \t]{0,3}(?P<chars>`+|~+)[ \t]*$")


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


def _strip_verify_fields(text: str) -> str:
    """Remove deterministic verifier fields only from syntactic claim rows."""
    lines = []
    fence: tuple[str, int] | None = None
    for line in text.splitlines(keepends=True):
        if fence is None:
            opener = _FENCE_OPEN.match(line)
            if opener:
                delimiter = opener["fence"]
                fence = delimiter[0], len(delimiter)
                lines.append(line)
                continue
        if fence is not None and _closes_fence(line, fence):
            fence = None
            lines.append(line)
            continue
        if fence is not None or not _CLAIM_LINE.match(line):
            lines.append(line)
            continue
        ending = (
            "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
        )
        content = line[: -len(ending)] if ending else line
        while True:
            reduced = _VERIFY_BEFORE_ANCHOR.sub(" ", content)
            reduced = _VERIFY_TERMINAL.sub("", reduced)
            if reduced == content:
                break
            content = reduced
        lines.append(content + ending)
    return "".join(lines)


def _closes_fence(line: str, fence: tuple[str, int] | None) -> bool:
    """A closer must use the opening character and at least its length."""
    if fence is None:
        return False
    match = _FENCE_CLOSE.match(line.rstrip("\r\n"))
    if not match:
        return False
    chars = match["chars"]
    return chars[0] == fence[0] and len(chars) >= fence[1]
