"""Literature-note generation: managed region + preserved free region (spec §3–§5)."""
import hashlib
import unicodedata
from html import escape
from pathlib import Path

from . import frontmatter

MANAGED_OPEN = "%%hk-managed%%"
MANAGED_CLOSE = "%%/hk-managed%%"
SEED_FREE = "\n## Notes\n"


def note_path(vault_root, citekey) -> Path:
    return Path(vault_root) / "literatures" / f"{citekey}.md"


def _managed_body(item, annotations) -> str:
    lines = [MANAGED_OPEN, f"# {item.get('title', item['id'])}", ""]
    for ann in annotations:
        lines.append(render_claim(ann))          # completed in Part B before commit/review
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
            return existing[offset + len(line):]
        offset += len(line)
    return SEED_FREE


# Fields the renderer owns and may rewrite; EVERYTHING else in prior frontmatter
# passes through unchanged (verified events, superseded-by, authority, archive-url,
# human-added keys — §5 never-delete applies to metadata too).
MANAGED_FIELDS = {"citekey", "type", "attachment-sha256", "aliases",
                  "doi", "url", "pmid", "version"}


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
    fm["retrieved"] = prior.get("retrieved", retrieved)   # day-one, never overwritten
    fm["attachment-sha256"] = attachment_hashes
    fm["status"] = prior.get("status", "unreviewed")
    fm["aliases"] = [item.get("title", item["id"])]
    for key, value in prior.items():                      # pass-through of unowned fields
        if key not in MANAGED_FIELDS and key not in fm:
            fm[key] = value
    return frontmatter.serialize(fm) + _managed_body(item, annotations) + _split_free(existing)


def _norm(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).split())


def claim_id(annotation: dict) -> str:
    basis = annotation.get("key") or _norm(annotation.get("annotationText", ""))
    return "c-" + hashlib.sha256(basis.encode()).hexdigest()[:8]


def render_claim(annotation: dict) -> str:
    cid = claim_id(annotation)
    cite = f"[@{annotation['citekey']}, p. {annotation['pageLabel']}]" \
        if annotation.get("pageLabel") else f"[@{annotation['citekey']}]"
    text = annotation.get("annotationText") or ""
    if text:
        lines = [f"- (quote) {cite} ^{cid}"]
        lines.extend(f"  > {line}" for line in text.split("\n"))
        pre, suf = annotation.get("context_prefix"), annotation.get("context_suffix")
        if pre or suf:
            prefix = escape((pre or "")[-32:], quote=True)
            suffix = escape((suf or "")[:32], quote=True)
            lines.append(f'  <!-- hk-sel prefix="{prefix}" suffix="{suffix}" -->')
        return "\n".join(lines)
    comment = " ".join((annotation.get("comment") or "").split())
    return f"- (paraphrase) {comment} {cite} ^{cid}"


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_changed(existing_text, attachment_hashes) -> bool:
    if not existing_text:
        return True
    prior = frontmatter.parse(existing_text)[0]
    return prior.get("attachment-sha256") != attachment_hashes
