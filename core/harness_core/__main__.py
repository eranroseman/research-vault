"""CLI surface consumed by hooks (Plan C) and skills (Plan D)."""

import argparse
import datetime
import hashlib
import json
import re
import sys
from collections.abc import Mapping
from pathlib import Path

from . import (
    Result,
    bibliography,
    checks,
    events,
    frontmatter,
    identify,
    inbox,
    lints,
    notes,
    paths,
    quotes,
    selectors,
    webapi,
)
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


CLOSING_CHECKS = {"citekey", "quote", "update-notice", "evidence-layer"}
_VERIFY_FAILED = re.compile(r"\s*\[verify-failed:: [A-Za-z0-9-]+/\d{4}-\d{2}-\d{2}\]")


def _safe_relative(vault_root, target):
    """Return a real vault child for an explicitly file-shaped target."""
    if (
        not isinstance(target, str)
        or not target
        or "\0" in target
        or "\n" in target
        or "\r" in target
        or Path(target).is_absolute()
        or ".." in Path(target).parts
    ):
        return None
    vault = Path(vault_root).resolve()
    path = (vault / target).resolve()
    try:
        path.relative_to(vault)
    except ValueError:
        return None
    return path


def _head_bytes(vault_root, relative):
    import subprocess

    result = subprocess.run(
        ["git", "show", f"HEAD:{relative}"],
        cwd=vault_root,
        capture_output=True,
        check=False,
    )
    return result.stdout if result.returncode == 0 else None


def _note_bytes(data: bytes) -> bytes:
    return notes.canonical_content(data.decode(errors="surrogateescape")).encode(
        errors="surrogateescape"
    )


def _claim_bytes_from_text(text, claim_id):
    """Hash one anchored claim and its continuations, ignoring our marker."""
    lines = notes.canonical_content(text).splitlines(keepends=True)
    for index, line in enumerate(lines):
        if line.rstrip("\r\n").endswith(f"^{claim_id}"):
            block = [line]
            for continuation in lines[index + 1 :]:
                if continuation.startswith(("  > ", "  <!-- hk-sel")):
                    block.append(continuation)
                else:
                    break
            return _VERIFY_FAILED.sub("", "".join(block)).encode()
    return None


def _claim_bytes(path, claim_id):
    try:
        return _claim_bytes_from_text(path.read_text(), claim_id)
    except (OSError, UnicodeError):
        return None


def _line_bytes(path, line_no):
    try:
        lines = notes.canonical_content(path.read_text()).splitlines(keepends=True)
    except (OSError, UnicodeError):
        return None
    if not 0 < line_no <= len(lines):
        return None
    return lines[line_no - 1].encode()


def _append_only_basis(vault_root, target):
    import subprocess

    result = subprocess.run(
        ["git", "diff", "HEAD", "--unified=0", "--", target],
        cwd=vault_root,
        capture_output=True,
        check=False,
    )
    removed = [
        line[1:]
        for line in result.stdout.splitlines(keepends=True)
        if line.startswith(b"-") and not line.startswith(b"---")
    ]
    return b"".join(removed) or _head_bytes(vault_root, target) or b""


def _directory_bytes(path):
    if not path.is_dir():
        return None
    chunks = []
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        data = child.read_bytes()
        if child.suffix == ".md":
            data = _note_bytes(data)
        chunks.extend((str(child.relative_to(path)).encode(), data))
    return b"\0".join(chunks)


def _note_for_citekey(vault_root, citekey):
    try:
        return notes.note_path(vault_root, citekey)
    except notes.InvalidCitekeyError:
        return None


def _citekey_hash(vault_root, citekey):
    note = _note_for_citekey(vault_root, citekey)
    if note and note.is_file():
        try:
            data, _ = frontmatter.parse(note.read_text())
        except (OSError, UnicodeError, frontmatter.FrontmatterError):
            data = {}
        attachment_hashes = data.get("attachment-sha256")
        if isinstance(attachment_hashes, list) and attachment_hashes:
            first = attachment_hashes[0]
            if isinstance(first, str) and first:
                return first
        return hashlib.sha256(_note_bytes(note.read_bytes())).hexdigest()[:16]
    return None


def _target_hash(vault_root, outcome):
    """Return the stable, kind-aware acknowledgment hash for an outcome."""
    target = outcome.target
    claim_id = None
    origin = _safe_relative(vault_root, outcome.extra.get("note_path"))
    line_no = outcome.extra.get("line_no")
    if isinstance(target, str) and "#^" in target:
        citekey, claim_id = target.split("#^", 1)
        known_citekey_hash = _citekey_hash(vault_root, citekey)
        if known_citekey_hash is not None:
            return known_citekey_hash
        data = _claim_bytes(origin, claim_id) if origin else None
        if data is None and origin is not None:
            head = _head_bytes(vault_root, outcome.extra["note_path"])
            if head is not None:
                data = _claim_bytes_from_text(
                    head.decode(errors="surrogateescape"), claim_id
                )
        if data is None:
            note = _note_for_citekey(vault_root, citekey)
            data = _claim_bytes(note, claim_id) if note else None
        if data is not None:
            return hashlib.sha256(data).hexdigest()[:16]

    # File targets are deliberately routed before citekeys; a slash must never
    # be interpreted as a citekey by notes.note_path().
    if outcome.check == "staleness":
        target = bibliography.BIB_PATH
    if isinstance(target, str) and "/" in target:
        path = _safe_relative(vault_root, target)
        if path is None:
            return None
        if outcome.check == "append-only":
            data = _append_only_basis(vault_root, target)
        elif path.is_file():
            data = path.read_bytes()
            if path.suffix == ".md":
                data = _note_bytes(data)
        elif path.is_dir():
            data = _directory_bytes(path)
        else:
            data = _head_bytes(vault_root, target) or b""
            if target.endswith(".md"):
                data = _note_bytes(data)
        return hashlib.sha256(data).hexdigest()[:16] if data is not None else None

    if isinstance(target, str):
        known_citekey_hash = _citekey_hash(vault_root, target)
        if known_citekey_hash is not None:
            return known_citekey_hash
        origin = _safe_relative(vault_root, outcome.extra.get("note_path"))
        if origin and origin.is_file():
            data = _note_bytes(origin.read_bytes())
            return hashlib.sha256(data).hexdigest()[:16]
        if origin:
            data = _head_bytes(vault_root, outcome.extra.get("note_path", ""))
            if data is not None:
                return hashlib.sha256(_note_bytes(data)).hexdigest()[:16]
        if origin and origin.is_file() and isinstance(line_no, int):
            data = _line_bytes(origin, line_no)
            if data is not None:
                return hashlib.sha256(data).hexdigest()[:16]
        entry = bibliography.load(vault_root).entry(target)
        if entry is not None:
            data = json.dumps(entry, sort_keys=True, separators=(",", ":")).encode()
            return hashlib.sha256(data).hexdigest()[:16]
    return None


def _origins(outcome):
    """Yield only the exact claim origins supplied by a checker."""
    note_path = outcome.extra.get("note_path")
    if outcome.check == "citekey":
        for claim in outcome.extra.get("claims", []):
            if isinstance(claim, dict):
                claim_id = claim.get("claim_id")
                line_no = claim.get("line_no")
                if isinstance(claim_id, str) or isinstance(line_no, int):
                    yield note_path, claim_id, line_no
        return
    claim_id = outcome.extra.get("claim_id")
    line_no = outcome.extra.get("line_no")
    if isinstance(note_path, str) and (
        isinstance(claim_id, str) or isinstance(line_no, int)
    ):
        yield note_path, claim_id, line_no


def _mutate_marker(vault_root, outcome, date, *, clear=False):
    if outcome.check not in CLOSING_CHECKS:
        return
    marker = re.compile(
        r"\s*\[verify-failed:: " + re.escape(outcome.check) + r"/\d{4}-\d{2}-\d{2}\]"
    )
    for relative, claim_id, line_no in _origins(outcome):
        path = _safe_relative(vault_root, relative)
        if path is None or not path.is_file():
            continue
        lines = path.read_text().splitlines(keepends=True)
        for index, line in enumerate(lines):
            anchored = isinstance(claim_id, str) and line.rstrip("\r\n").endswith(
                f"^{claim_id}"
            )
            numbered = isinstance(line_no, int) and index == line_no - 1
            if not anchored and not numbered:
                continue
            replacement = marker.sub("", line) if clear else line
            if not clear and not marker.search(line):
                ending = "\n" if line.endswith("\n") else ""
                content = line[: -len(ending)] if ending else line
                if anchored:
                    before, terminal_anchor = content.rsplit(f"^{claim_id}", 1)
                    replacement = (
                        before
                        + f"[verify-failed:: {outcome.check}/{date}] "
                        + f"^{claim_id}{terminal_anchor}"
                    )
                else:
                    replacement = content + f" [verify-failed:: {outcome.check}/{date}]"
                replacement += ending
            if replacement != line:
                lines[index] = replacement
                path.write_text("".join(lines))
            break


def _clear_verify_failed(vault_root, outcome):
    """Compatibility helper used by tests; clearing still requires exact origins."""
    _mutate_marker(vault_root, outcome, datetime.date.today().isoformat(), clear=True)


def _file_outcomes(vault_root, path):
    return (
        checks.check_citekeys(vault_root, path)
        + quotes.check_all_quotes(vault_root, path)
        + lints.lint_source_status(vault_root, path)
        + lints.lint_contested(vault_root, path)
    )


def _bibliography_entries(vault_root):
    bib = bibliography.load(vault_root)
    return [bib.entry(key) for key in sorted(bib.citekeys)]


def _staleness_outcome(vault_root, base=DEFAULT_BASE):
    result = bibliography.staleness(vault_root, ZoteroClient(base=base))
    reasons = {
        Result.MATCHED: "matched",
        Result.SKIPPED: "no-identifier — bibliography absent",
        Result.UNMATCHED: "stale — bibliography differs or is invalid",
        Result.UNREACHABLE: "outage — bibliography comparison unavailable",
    }
    return checks.Outcome("staleness", bibliography.BIB_PATH, result, reasons[result])


def _network_outcomes(vault_root, entry, detection_date, rw):
    """Produce DOI/metadata and one reduced update-notice outcome."""
    outcomes = []
    doi = entry.get("DOI") or entry.get("doi")
    if doi:
        outcomes.extend(
            [
                checks.check_doi_exists(vault_root, doi, entry.get("id")),
                checks.check_metadata(vault_root, entry),
            ]
        )
    else:
        unavailable = entry.get("_discovery_unreachable") is True
        result = Result.UNREACHABLE if unavailable else Result.SKIPPED
        reason = (
            "outage — identifier discovery unavailable"
            if unavailable
            else "no-identifier — discovery found nothing"
        )
        outcomes.extend(
            [
                checks.Outcome("doi", entry["id"], result, reason),
                checks.Outcome("metadata", entry["id"], result, reason),
            ]
        )
    if entry.get("_discovery_unreachable") and not (
        entry.get("DOI") or entry.get("doi")
    ):
        live = checks.Outcome(
            "update-notice",
            entry["id"],
            Result.UNREACHABLE,
            "outage — identifier discovery unavailable",
        )
    else:
        live = checks.check_update_notice(vault_root, entry, detection_date)
    rw_leg = (
        checks.check_rw_batch(entry, rw, detection_date) if rw is not None else None
    )
    reduced = checks.reduce_update_notice_outcomes(live, rw_leg)
    if reduced is not None:
        outcomes.append(reduced)
    return outcomes


def _offline_network_outcomes(entry, detection_date, rw):
    target = entry["id"]
    live = checks.Outcome(
        "update-notice", target, Result.UNREACHABLE, "outage — network disabled"
    )
    rw_leg = (
        checks.check_rw_batch(entry, rw, detection_date) if rw is not None else None
    )
    reduced = checks.reduce_update_notice_outcomes(live, rw_leg)
    return [
        checks.Outcome("doi", target, Result.UNREACHABLE, "outage — network disabled"),
        checks.Outcome(
            "metadata", target, Result.UNREACHABLE, "outage — network disabled"
        ),
        reduced,
    ]


def _archive_outcomes(vault_root):
    outcomes = []
    for path in sorted((Path(vault_root) / "literatures").glob("*.md")):
        try:
            data, _ = frontmatter.parse(path.read_text())
        except (OSError, UnicodeError, frontmatter.FrontmatterError):
            continue
        archive_url = data.get("archive-url")
        if not isinstance(archive_url, str) or not archive_url:
            continue
        raw_target = data.get("citekey")
        target = (
            raw_target.strip()
            if isinstance(raw_target, str) and raw_target.strip()
            else path.relative_to(vault_root).as_posix()
        )
        try:
            status = webapi.get_status(archive_url, vault_root)
        except webapi.ApiError:
            outcomes.append(
                checks.Outcome(
                    "web-archive",
                    target,
                    Result.UNREACHABLE,
                    "outage — archive-url unavailable",
                )
            )
        else:
            if status == 404:
                outcomes.append(
                    checks.Outcome(
                        "web-archive",
                        target,
                        Result.UNMATCHED,
                        "missing-archive — archive-url 404s",
                    )
                )
            else:
                outcomes.append(
                    checks.Outcome("web-archive", target, Result.MATCHED, "matched")
                )
    return outcomes


def _warning_type(entry):
    match = re.match(r"warn-notice\s+—\s+(.+)$", entry.reason)
    return match.group(1) if match else None


def _effective(outcomes, hashes, vault_root):
    return [
        outcome
        for outcome in outcomes
        if outcome.result is Result.MATCHED
        or not inbox.is_acknowledged(
            vault_root, outcome.check, outcome.target, hashes[id(outcome)]
        )
    ]


def _file_effects(vault_root, raw, effective, hashes, detection_date):
    """Apply markers, events, and inbox notices only after raw audit collection."""
    effective_ids = {id(outcome) for outcome in effective}
    for outcome in raw:
        if id(outcome) not in effective_ids:
            if outcome.result is Result.UNMATCHED:
                _mutate_marker(vault_root, outcome, detection_date, clear=True)
            continue
        if outcome.result is Result.UNMATCHED:
            _mutate_marker(vault_root, outcome, detection_date)
        elif outcome.result is Result.MATCHED:
            _mutate_marker(vault_root, outcome, detection_date, clear=True)
            if outcome.check == "quote" and "#^" in outcome.target:
                citekey = outcome.target.split("#^", 1)[0]
                note = _note_for_citekey(vault_root, citekey)
                if note and note.is_file():
                    note.write_text(
                        events.record_pass(
                            note.read_text(),
                            f"quote:{outcome.target}:{outcome.extra.get('target', 'managed-region')}",
                            Result.MATCHED,
                            at=detection_date,
                        )
                    )
            elif outcome.check in {"doi", "metadata", "update-notice"}:
                note = _note_for_citekey(vault_root, outcome.target)
                if note and note.is_file():
                    note.write_text(
                        events.record_pass(
                            note.read_text(),
                            outcome.check,
                            Result.MATCHED,
                            at=detection_date,
                        )
                    )

    open_keys = set()
    for entry in inbox.open_entries(vault_root):
        discriminator = _warning_type(entry) or entry.result
        open_keys.add((entry.check, entry.target, discriminator, entry.target_hash))
    for outcome in effective:
        target_hash = hashes[id(outcome)]
        if outcome.result is not Result.MATCHED:
            key = (outcome.check, outcome.target, outcome.result.value, target_hash)
            if key not in open_keys:
                inbox.append_entry(
                    vault_root,
                    outcome.check,
                    outcome.target,
                    outcome.result,
                    outcome.reason,
                    target_hash=target_hash,
                    notice_date=outcome.extra.get("notice_date"),
                    detection_date=outcome.extra.get("detection_date"),
                )
                open_keys.add(key)
        for warning in outcome.extra.get("warn_notices", []):
            if inbox.is_acknowledged(
                vault_root, outcome.check, outcome.target, target_hash
            ):
                continue
            warning_type = warning.get("type")
            if not isinstance(warning_type, str):
                continue
            key = (outcome.check, outcome.target, warning_type, target_hash)
            if key not in open_keys:
                inbox.append_entry(
                    vault_root,
                    outcome.check,
                    outcome.target,
                    Result.UNMATCHED,
                    f"warn-notice — {warning_type}",
                    target_hash=target_hash,
                    notice_date=warning.get("notice_date"),
                    detection_date=warning.get("detection_date", detection_date),
                )
                open_keys.add(key)


def _verify_state(
    vault_root,
    scope="all",
    network=True,
    detection_date=None,
    rw_csv=None,
    base=DEFAULT_BASE,
):
    """Collect raw verification audit outcomes, then apply acknowledged effects."""
    del scope
    vault = Path(vault_root)
    detection_date = detection_date or datetime.date.today().isoformat()
    raw = []
    if network:
        raw.append(_staleness_outcome(vault, base))
    else:
        raw.append(
            checks.Outcome(
                "staleness",
                bibliography.BIB_PATH,
                Result.UNREACHABLE,
                "outage — network disabled",
            )
        )
    note_files = [
        path
        for folder in ("literatures", "atlas", "efforts")
        for path in sorted((vault / folder).rglob("*.md"))
    ]
    for path in note_files:
        raw.extend(_file_outcomes(vault, path))
    rw = checks.load_rw_csv(rw_csv) if rw_csv else None
    for original in _bibliography_entries(vault):
        entry = dict(original)
        if network and not (entry.get("DOI") or entry.get("doi")):
            discovery = identify.discover(vault, entry)
            raw.append(discovery)
            identifiers = discovery.extra.get("identifiers", {})
            if isinstance(identifiers, dict):
                entry.update(identifiers)
            entry["_discovery_unreachable"] = discovery.result is Result.UNREACHABLE
        if network:
            raw.extend(_network_outcomes(vault, entry, detection_date, rw))
        else:
            raw.extend(_offline_network_outcomes(entry, detection_date, rw))
    raw.extend(lints.lint_append_only(vault))
    raw.extend(lints.lint_claim_immutability(vault))
    raw.extend(lints.lint_published_drift(vault))
    raw.extend(lints.lint_web_archive(vault))
    if network:
        raw.extend(_archive_outcomes(vault))
    hashes = {id(outcome): _target_hash(vault, outcome) for outcome in raw}
    effective = _effective(raw, hashes, vault)
    _file_effects(vault, raw, effective, hashes, detection_date)
    counts = {}
    for outcome in effective:
        counts[outcome.result.value] = counts.get(outcome.result.value, 0) + 1
    return {"outcomes": raw, "counts": counts}, effective, hashes


def run_verify(vault_root, scope="all", network=True, detection_date=None, rw_csv=None):
    """Collect raw outcomes and apply their effective verification effects."""
    report, _effective_outcomes, _hashes = _verify_state(
        vault_root, scope, network, detection_date, rw_csv
    )
    return report


def cmd_verify(args):
    report, effective, hashes = _verify_state(
        args.vault,
        network=not args.offline,
        rw_csv=args.rw_csv,
        base=getattr(args, "base", DEFAULT_BASE),
    )
    for outcome in effective:
        if outcome.result is not Result.MATCHED:
            print(
                f"{outcome.result.value} {outcome.check} {outcome.target} — {outcome.reason}"
            )
        if not inbox.is_acknowledged(
            args.vault, outcome.check, outcome.target, hashes[id(outcome)]
        ):
            for warning in outcome.extra.get("warn_notices", []):
                warning_type = warning.get("type")
                if isinstance(warning_type, str):
                    print(
                        f"UNMATCHED {outcome.check} {outcome.target} — "
                        f"warn-notice — {warning_type}"
                    )
    print(json.dumps(report["counts"], sort_keys=True))
    if any(
        outcome.result is Result.UNMATCHED and outcome.check in CLOSING_CHECKS
        for outcome in effective
    ):
        return 1
    return (
        3 if any(outcome.result is Result.UNREACHABLE for outcome in effective) else 0
    )


def cmd_inbox(args):
    print(json.dumps(inbox.summary(args.vault), sort_keys=True))
    for entry in sorted(
        inbox.open_entries(args.vault), key=lambda item: (item.date, item.id)
    ):
        print(
            f"{entry.date} {entry.result} {entry.check} {entry.target} — {entry.reason}"
        )
    return 0


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
    verify = sub.add_parser("verify", parents=[common])
    verify.add_argument("--vault", required=True)
    verify.add_argument("--offline", action="store_true")
    verify.add_argument("--rw-csv")
    review_inbox = sub.add_parser("inbox", parents=[common])
    review_inbox.add_argument("--vault", required=True)
    args = parser.parse_args(argv)
    if not hasattr(args, "base"):
        args.base = DEFAULT_BASE
    return {
        "probe": cmd_probe,
        "import-note": cmd_import_note,
        "staleness": cmd_staleness,
        "backfill-selectors": cmd_backfill_selectors,
        "verify": cmd_verify,
        "inbox": cmd_inbox,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
