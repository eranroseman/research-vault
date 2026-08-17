"""CLI surface consumed by hooks (Plan C) and skills (Plan D)."""

import argparse
import datetime
import json
import re
import sys
from collections.abc import Mapping
from pathlib import Path

from . import Result, bibliography, frontmatter, notes, paths, selectors
from .zotero import ZoteroClient, ZoteroError

QUOTE_ANNOTATION_TYPES = {"highlight", "underline"}
DEFAULT_BASE = "http://localhost:23119"


def _text(value) -> str:
    """Keep only strings that are safe for claim IDs and Markdown rendering."""
    return value if isinstance(value, str) else ""


def normalize_annotation(annotation, citekey: str) -> dict:
    """Adapt a raw BBT item-JSON annotation to ``notes``' input contract."""
    raw = annotation if isinstance(annotation, Mapping) else {}
    annotation_type = _text(raw.get("annotationType"))
    annotation_text = _text(raw.get("annotationText"))
    comment = _text(raw.get("annotationComment"))

    # Unknown or non-quoting annotation types cannot safely assert that their
    # payload is a verbatim quote. Preserve usable text as a paraphrase instead.
    if annotation_type not in QUOTE_ANNOTATION_TYPES:
        comment = comment or annotation_text
        annotation_text = ""

    normalized = {
        "type": annotation_type,
        "comment": comment,
        "pageLabel": _text(raw.get("annotationPageLabel")),
        "key": _text(raw.get("key")),
        "annotationText": annotation_text,
        "citekey": _text(citekey),
    }
    for field in ("context_prefix", "context_suffix"):
        value = raw.get(field)
        if isinstance(value, str):
            normalized[field] = value
    return normalized


def cmd_probe(args):
    client = ZoteroClient(base=args.base)
    try:
        info = client.ready()
        info["local_writes"] = client.supports_local_writes()
    except ZoteroError:
        print(json.dumps({"result": Result.UNREACHABLE.value}))
        return 3
    print(json.dumps(info))
    return 0


def _attachment_annotations(attachment):
    if not isinstance(attachment, Mapping):
        return []
    annotations = attachment.get("annotations")
    return annotations if isinstance(annotations, list) else []


def _attachment_hash(attachment, vault) -> tuple[str, Path]:
    raw_path = attachment.get("path") if isinstance(attachment, Mapping) else None
    if not isinstance(raw_path, str) or not raw_path:
        raise paths.PathError(f"invalid attachment path: {raw_path!r}")
    local_path = paths.to_local(raw_path, vault)
    return notes.sha256_file(local_path), local_path


def _read_note(path):
    with path.open("r", encoding="utf-8", newline="") as note:
        return note.read()


def _write_note(path, text):
    with path.open("w", encoding="utf-8", newline="") as note:
        note.write(text)


_QUOTE_SELECTOR = re.compile(
    r"^- \(quote\)[^\r\n]*\^(?P<claim_id>c-[0-9a-f]{8})\r?\n"
    r"(?:  >[^\r\n]*(?:\r\n|\n|$))*"
    r'  <!-- hk-sel prefix="(?P<prefix>.*?)" suffix="(?P<suffix>.*?)" -->',
    re.MULTILINE | re.DOTALL,
)


def _prior_contexts(existing: str | None) -> dict[str, tuple[str, str]]:
    if not existing:
        return {}
    return {
        match["claim_id"]: (
            selectors.unescape_selector(match["prefix"]),
            selectors.unescape_selector(match["suffix"]),
        )
        for match in _QUOTE_SELECTOR.finditer(existing)
    }


def _retain_prior_contexts(annotations: list[dict], existing: str | None) -> int:
    prior = _prior_contexts(existing)
    retained = 0
    for annotation in annotations:
        if not annotation.get("annotationText"):
            continue
        context = prior.get(notes.claim_id(annotation))
        if context and not (
            annotation.get("context_prefix") or annotation.get("context_suffix")
        ):
            annotation["context_prefix"], annotation["context_suffix"] = context
            retained += 1
    return retained


def _selector_warning(reasons: list[str], *, retained: int) -> None:
    if not reasons:
        return
    reason = "; ".join(dict.fromkeys(reasons))
    if retained:
        print(
            f"warning: selectors degraded ({reason}; existing selector contexts retained)",
            file=sys.stderr,
        )
    else:
        print(f"warning: selectors skipped ({reason})", file=sys.stderr)


def cmd_import_note(args):
    try:
        path = notes.note_path(args.vault, args.citekey)
    except notes.InvalidCitekeyError:
        print(f"invalid citekey: {args.citekey!r}", file=sys.stderr)
        return 1

    client = ZoteroClient(base=args.base)
    vault = args.vault
    matches = [
        item
        for item in client.search(args.citekey)
        if item.get("citekey") == args.citekey
    ]
    if not matches:
        print(f"citekey not found: {args.citekey}", file=sys.stderr)
        return 1
    item = matches[0]
    item["id"] = args.citekey

    existing = _read_note(path) if path.is_file() else None
    hashes = []
    annotations = []
    attachment_pairs = []
    for attachment in client.attachments(args.citekey):
        local_path = None
        try:
            attachment_hash, local_path = _attachment_hash(attachment, vault)
            hashes.append(attachment_hash)
        except (paths.PathError, OSError) as error:
            print(f"warning: attachment unresolved: {error}", file=sys.stderr)
            hashes.append("unresolved")
        attachment_annotations = [
            normalize_annotation(annotation, args.citekey)
            for annotation in _attachment_annotations(attachment)
        ]
        annotations.extend(attachment_annotations)
        attachment_pairs.append((local_path, attachment_annotations))

    degradation_reasons = []
    for local_path, attachment_annotations in attachment_pairs:
        needed = [
            annotation
            for annotation in attachment_annotations
            if annotation["annotationText"]
            and not (
                annotation.get("context_prefix") or annotation.get("context_suffix")
            )
        ]
        if not needed:
            continue
        if local_path is None:
            degradation_reasons.append("attachment unresolved")
            continue
        text = selectors.pdf_text(local_path)
        if not text:
            degradation_reasons.append("no extractable PDF text")
            continue
        if selectors.attach_contexts(needed, text) != len(needed):
            degradation_reasons.append(
                "some annotation quotes were not found in extracted text"
            )
    retained = _retain_prior_contexts(annotations, existing)
    _selector_warning(degradation_reasons, retained=retained)

    today = datetime.date.today().isoformat()
    candidate = notes.render_note(item, hashes, annotations, existing, today)

    # This must precede the note NOOP check: another Zotero item may have been
    # admitted even when this note's complete rendered projection has not changed.
    bibliography.write_and_commit(vault, client.export_csl(None))

    if not notes.content_changed(existing, candidate):
        print("NOOP")
        return 0
    _write_note(path, candidate)
    print(str(path))
    return 0


def cmd_backfill_selectors(args):
    literature_dir = notes.note_path(args.vault, "placeholder").parent
    failures = 0
    for path in sorted(literature_dir.glob("*.md")):
        try:
            data, _ = frontmatter.parse(_read_note(path))
        except (OSError, frontmatter.FrontmatterError) as error:
            print(
                f"warning: malformed literature note {path}: {error}", file=sys.stderr
            )
            failures += 1
            continue
        citekey = data.get("citekey")
        if not isinstance(citekey, str) or not citekey:
            print(
                f"warning: malformed literature note {path}: missing citekey",
                file=sys.stderr,
            )
            failures += 1
            continue
        try:
            notes.note_path(args.vault, citekey)
        except notes.InvalidCitekeyError:
            print(f"invalid citekey: {citekey!r}", file=sys.stderr)
            failures += 1
            continue
        failures += (
            cmd_import_note(
                argparse.Namespace(citekey=citekey, vault=args.vault, base=args.base)
            )
            != 0
        )
    return int(bool(failures))


def cmd_staleness(args):
    result = bibliography.staleness(args.vault, ZoteroClient(base=args.base))
    print(result.value)
    return {
        Result.MATCHED: 0,
        Result.SKIPPED: 0,
        Result.UNMATCHED: 1,
        Result.UNREACHABLE: 3,
    }[result]


def main(argv=None):
    # A shared parent accepts --base before or after each subcommand.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--base", default=argparse.SUPPRESS)
    parser = argparse.ArgumentParser(prog="harness_core", parents=[common])
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe", parents=[common])
    import_note = sub.add_parser("import-note", parents=[common])
    import_note.add_argument("citekey")
    import_note.add_argument("--vault", required=True)
    staleness = sub.add_parser("staleness", parents=[common])
    staleness.add_argument("--vault", required=True)
    backfill = sub.add_parser("backfill-selectors", parents=[common])
    backfill.add_argument("--vault", required=True)
    args = parser.parse_args(argv)
    if not hasattr(args, "base"):
        args.base = DEFAULT_BASE
    return {
        "probe": cmd_probe,
        "import-note": cmd_import_note,
        "staleness": cmd_staleness,
        "backfill-selectors": cmd_backfill_selectors,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
