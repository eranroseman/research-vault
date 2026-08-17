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
    for key, value in prior.items():  # pass-through of unowned fields
        if key not in MANAGED_FIELDS and key not in fm:
            fm[key] = value
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


def canonical_content(note_text: str) -> str:
    """Exclude only verifier-owned events and failure markers from note comparison."""
    try:
        data, _ = frontmatter.parse(note_text)
    except frontmatter.FrontmatterError:
        data = {}
    verified = data.get("verified")
    valid_verified = isinstance(verified, list) and all(
        isinstance(event, dict) for event in verified
    )
    if not valid_verified:
        return _strip_verify_fields(note_text)
    lines = note_text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        return _strip_verify_fields(note_text)
    result = []
    index = 0
    in_frontmatter = True
    while index < len(lines):
        line = lines[index]
        if in_frontmatter and line.rstrip("\r\n") == "---" and index:
            in_frontmatter = False
            result.append(line)
            index += 1
            continue
        if in_frontmatter and line.rstrip("\r\n").rstrip(" \t") == "verified:":
            index += 1
            while index < len(lines) and lines[index].startswith("  - "):
                index += 1
            continue
        result.append(line)
        index += 1
    return _strip_verify_fields("".join(result))


def _strip_verify_fields(text: str) -> str:
    """Remove deterministic verifier fields only from syntactic claim rows."""
    lines = []
    for line in text.splitlines(keepends=True):
        if not _CLAIM_LINE.match(line):
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
