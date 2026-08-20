"""CLI surface consumed by hooks (Plan C) and skills (Plan D)."""

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import tempfile
from collections.abc import Mapping
from pathlib import Path

from . import (
    Result,
    bibliography,
    checks,
    events,
    frontmatter,
    gitstate,
    identify,
    inbox,
    lints,
    notes,
    paths,
    quotes,
    scaffold,
    selectors,
    webapi,
)
from .pathcodec import (
    PathCodecError,
    RepoPathValue,
    decode_repo_path,
    encode_repo_path,
)
from .scaffold import doctor
from .zotero import ZoteroClient, ZoteroError

QUOTE_ANNOTATION_TYPES = {"highlight", "underline"}
DEFAULT_BASE = "http://localhost:23119"
_OMITTED_BIBLIOGRAPHY = object()
DOCTOR_HARD_UNMATCHED = {"tree", "machine-config", "bbt", "autoexport"}
DOCTOR_HARD_UNREACHABLE = {"zotero", "bbt", "autoexport"}
DOCTOR_WARN_ONLY = {"staleness", "remote", "backup", "inbox"}


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


def _read_note_text(path):
    with Path(path).open("r", encoding="utf-8", newline="") as note:
        return note.read()


def _write_note_text(path, text):
    with Path(path).open("w", encoding="utf-8", newline="") as note:
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

    observed = bibliography.observe_autoexport(vault, client)
    if observed.result is not Result.MATCHED:
        print(observed.detail, file=sys.stderr)
        return 1 if observed.result is Result.UNMATCHED else 3

    existing = _read_note_text(path) if path.is_file() else None
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

    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    generated_at = now.isoformat().replace("+00:00", "Z")
    candidate = notes.render_note(
        item,
        hashes,
        annotations,
        existing,
        accessed=now.date().isoformat(),
        generated_at=generated_at,
    )

    if not notes.content_changed(existing, candidate):
        print("NOOP")
        return 0
    _write_note_text(path, candidate)
    print(str(path))
    return 0


def cmd_backfill_selectors(args):
    literature_dir = notes.note_path(args.vault, "placeholder").parent
    failures = 0
    for path in sorted(literature_dir.glob("*.md")):
        try:
            data, _ = frontmatter.parse(_read_note_text(path))
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


CLOSING_BY_SURFACE = {
    "audit": frozenset(),
    "commit": frozenset({"citekey", "evidence-layer"}),
    "publish": frozenset(
        {"citekey", "evidence-layer", "quote", "update-notice", "doi"}
    ),
}
CLOSING_CHECKS = frozenset().union(*CLOSING_BY_SURFACE.values())


def _safe_relative(vault_root, target, target_kind="identifier"):
    """Return an exact vault path only for explicit canonical repo-path metadata."""
    if target_kind != "repo-path" or not isinstance(target, str):
        return None
    try:
        raw = decode_repo_path(target)
        absolute = gitstate._absolute(Path(vault_root), raw)
        image = gitstate.live_image(Path(vault_root), raw)
    except (PathCodecError, gitstate.GitStateError, OSError):
        return None
    if image is not None and image.kind in {"symlink", "special"}:
        return None
    return Path(os.fsdecode(absolute))


def _extra_path(vault_root, outcome, key):
    if key not in outcome.path_extra_fields:
        return None
    return _safe_relative(vault_root, outcome.extra.get(key), "repo-path")


def _note_bytes(data: bytes) -> bytes:
    return notes.canonical_content(data.decode(errors="surrogateescape")).encode(
        errors="surrogateescape"
    )


def _claim_bytes_from_text(text, claim_id):
    """Hash one anchored claim and its continuations, ignoring our marker."""
    lines = notes.canonical_content(text).splitlines(keepends=True)
    for index, line in enumerate(lines):
        content, _ = _split_line_ending(line)
        if _terminal_anchor_match(content, claim_id):
            block = [line]
            for continuation in lines[index + 1 :]:
                if continuation.startswith(("  > ", "  <!-- hk-sel")):
                    block.append(continuation)
                else:
                    break
            return "".join(block).encode(errors="surrogateescape")
    return None


def _claim_bytes(path, claim_id):
    try:
        return _claim_bytes_from_text(_read_note_text(path), claim_id)
    except (OSError, UnicodeError):
        return None


def _append_only_basis(vault_root, raw_path, base_snapshot=None):
    if base_snapshot is not None:
        image = base_snapshot.image(raw_path)
        return image.data or b"" if image is not None and image.kind == "file" else b""
    return gitstate.blob_bytes(vault_root, "HEAD", raw_path) or b""


def _directory_bytes(path):
    if not path.is_dir():
        return None
    chunks = []
    root = path.resolve()
    try:
        children = sorted(path.rglob("*"))
    except OSError:
        return b"unreadable-directory"
    for child in children:
        try:
            relative = os.fsencode(child.relative_to(path).as_posix())
        except ValueError:
            continue
        try:
            if child.is_symlink():
                try:
                    link_target = os.fsencode(os.readlink(child))
                except OSError:
                    link_target = b"unreadable-link"
                chunks.extend((relative, b"symlink", link_target))
                continue
            if not child.is_file():
                continue
            child.resolve().relative_to(root)
        except ValueError:
            chunks.extend((relative, b"outside"))
            continue
        except OSError:
            chunks.extend((relative, b"unreadable"))
            continue
        try:
            data = child.read_bytes()
        except OSError:
            chunks.extend((relative, b"unreadable"))
            continue
        if child.suffix == ".md":
            data = _note_bytes(data)
        chunks.extend((relative, data))
    return b"\0".join(chunks)


def _snapshot_directory_bytes(snapshot, raw_path):
    prefix = raw_path + b"/"
    chunks = []
    for child_path in sorted(snapshot.images):
        if not child_path.startswith(prefix):
            continue
        image = snapshot.images[child_path]
        relative = child_path[len(prefix) :]
        if image.kind == "symlink":
            chunks.extend((relative, b"symlink", image.data or b""))
        elif image.kind == "file":
            data = image.data or b""
            if child_path.endswith(b".md"):
                data = _note_bytes(data)
            chunks.extend((relative, data))
    return b"\0".join(chunks)


def _note_for_citekey(vault_root, citekey):
    try:
        vault = Path(vault_root)
        candidate = notes.note_path(vault, citekey)
        raw_path = os.fsencode(candidate.relative_to(vault))
    except notes.InvalidCitekeyError:
        return None
    except ValueError:
        return None
    return _safe_relative(vault, encode_repo_path(raw_path), "repo-path")


def _citekey_hash(vault_root, citekey, candidate_snapshot=None):
    if candidate_snapshot is not None:
        try:
            candidate = notes.note_path(Path(vault_root), citekey)
            raw_path = os.fsencode(candidate.relative_to(vault_root))
        except (notes.InvalidCitekeyError, ValueError):
            return None
        image = candidate_snapshot.image(raw_path)
        if image is None or image.kind != "file":
            return None
        raw = image.data or b""
        try:
            data, _ = frontmatter.parse(raw.decode(errors="surrogateescape"))
        except (UnicodeError, frontmatter.FrontmatterError):
            data = {}
        attachment_hashes = data.get("fixity-sha256")
        if isinstance(attachment_hashes, list) and attachment_hashes:
            first = attachment_hashes[0]
            if isinstance(first, str) and first:
                return first
        return hashlib.sha256(_note_bytes(raw)).hexdigest()[:16]
    note = _note_for_citekey(vault_root, citekey)
    if note and note.is_file():
        try:
            data, _ = frontmatter.parse(_read_note_text(note))
        except (OSError, UnicodeError, frontmatter.FrontmatterError):
            data = {}
        attachment_hashes = data.get("fixity-sha256")
        if isinstance(attachment_hashes, list) and attachment_hashes:
            first = attachment_hashes[0]
            if isinstance(first, str) and first:
                return first
        return hashlib.sha256(_note_bytes(note.read_bytes())).hexdigest()[:16]
    return None


def _target_hash(
    vault_root,
    outcome,
    bibliography_universe=_OMITTED_BIBLIOGRAPHY,
    *,
    base_snapshot=None,
    candidate_snapshot=None,
):
    """Return the stable, kind-aware acknowledgment hash for an outcome."""
    target = outcome.target
    raw_origin = (
        decode_repo_path(outcome.extra["note_path"])
        if "note_path" in outcome.path_extra_fields
        else None
    )
    origin_image = (
        candidate_snapshot.image(raw_origin)
        if candidate_snapshot is not None and raw_origin is not None
        else None
    )
    origin = (
        None
        if candidate_snapshot is not None
        else _extra_path(vault_root, outcome, "note_path")
    )
    if isinstance(target, str) and "#^" in target:
        citekey, claim_id = target.split("#^", 1)
        known_citekey_hash = _citekey_hash(
            vault_root, citekey, candidate_snapshot=candidate_snapshot
        )
        if known_citekey_hash is not None:
            return known_citekey_hash
        data = (
            _claim_bytes_from_text(
                (origin_image.data or b"").decode(errors="surrogateescape"), claim_id
            )
            if origin_image is not None and origin_image.kind == "file"
            else _claim_bytes(origin, claim_id)
            if origin
            else None
        )
        if data is None and raw_origin is not None:
            base_image = (
                base_snapshot.image(raw_origin) if base_snapshot is not None else None
            )
            head = (
                base_image.data
                if base_image is not None and base_image.kind == "file"
                else gitstate.blob_bytes(vault_root, "HEAD", raw_origin)
                if base_snapshot is None
                else None
            )
            if head is not None:
                data = _claim_bytes_from_text(
                    head.decode(errors="surrogateescape"), claim_id
                )
        if data is None and candidate_snapshot is None:
            note = _note_for_citekey(vault_root, citekey)
            data = _claim_bytes(note, claim_id) if note else None
        if data is not None:
            return hashlib.sha256(data).hexdigest()[:16]

    if outcome.target_kind == "repo-path":
        raw_target = decode_repo_path(target)
        if candidate_snapshot is not None:
            candidate_image = candidate_snapshot.image(raw_target)
            if candidate_image is not None and candidate_image.kind in {
                "symlink",
                "special",
            }:
                return None
            if outcome.check == "append-only":
                data = _append_only_basis(vault_root, raw_target, base_snapshot)
            elif candidate_image is not None and candidate_image.kind == "file":
                data = candidate_image.data or b""
                if raw_target.endswith(b".md"):
                    data = _note_bytes(data)
            elif candidate_image is not None and candidate_image.kind == "directory":
                data = _snapshot_directory_bytes(candidate_snapshot, raw_target)
            else:
                base_image = (
                    base_snapshot.image(raw_target)
                    if base_snapshot is not None
                    else None
                )
                data = (
                    base_image.data
                    if base_image is not None and base_image.kind == "file"
                    else b""
                ) or b""
                if raw_target.endswith(b".md"):
                    data = _note_bytes(data)
            return hashlib.sha256(data).hexdigest()[:16]
        base_image = (
            base_snapshot.image(raw_target) if base_snapshot is not None else None
        )
        path = _safe_relative(vault_root, target, outcome.target_kind)
        if path is None:
            data = (
                base_image.data
                if base_image is not None and base_image.kind == "file"
                else None
            )
            if data is None:
                return None
            if raw_target.endswith(b".md"):
                data = _note_bytes(data)
            return hashlib.sha256(data).hexdigest()[:16]
        live_target = gitstate.live_image(Path(vault_root), raw_target)
        if live_target is not None and live_target.kind in {"symlink", "special"}:
            return None
        if outcome.check == "append-only":
            data = _append_only_basis(vault_root, raw_target, base_snapshot)
        elif path.is_file():
            data = path.read_bytes()
            if path.suffix == ".md":
                data = _note_bytes(data)
        elif path.is_dir():
            data = _directory_bytes(path)
        else:
            data = (
                base_image.data
                if base_image is not None and base_image.kind == "file"
                else gitstate.blob_bytes(vault_root, "HEAD", raw_target)
                if base_snapshot is None
                else b""
            ) or b""
            if raw_target.endswith(b".md"):
                data = _note_bytes(data)
        return hashlib.sha256(data).hexdigest()[:16] if data is not None else None

    if isinstance(target, str):
        known_citekey_hash = _citekey_hash(
            vault_root, target, candidate_snapshot=candidate_snapshot
        )
        if known_citekey_hash is not None:
            return known_citekey_hash
        if origin_image is not None and origin_image.kind == "file":
            data = _note_bytes(origin_image.data or b"")
            return hashlib.sha256(data).hexdigest()[:16]
        if origin and origin.is_file():
            data = _note_bytes(origin.read_bytes())
            return hashlib.sha256(data).hexdigest()[:16]
        if raw_origin is not None:
            base_image = (
                base_snapshot.image(raw_origin) if base_snapshot is not None else None
            )
            data = (
                base_image.data
                if base_image is not None and base_image.kind == "file"
                else gitstate.blob_bytes(vault_root, "HEAD", raw_origin)
                if base_snapshot is None
                else None
            )
            if data is not None:
                return hashlib.sha256(_note_bytes(data)).hexdigest()[:16]
        if bibliography_universe is _OMITTED_BIBLIOGRAPHY:
            entry = bibliography.load(vault_root).entry(target)
        elif bibliography_universe is not None:
            entry = bibliography_universe.entry(target)
        else:
            entry = None
        if entry is not None:
            data = json.dumps(entry, sort_keys=True, separators=(",", ":")).encode()
            return hashlib.sha256(data).hexdigest()[:16]
    return None


def _origins(outcome):
    """Yield only the exact claim origins supplied by a checker."""
    note_path = (
        outcome.extra.get("note_path")
        if "note_path" in outcome.path_extra_fields
        else None
    )
    if outcome.check == "citekey":
        for claim in outcome.extra.get("claims", []):
            if isinstance(claim, Mapping):
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
    for relative, claim_id, line_no in _origins(outcome):
        path = _safe_relative(vault_root, relative, "repo-path")
        if path is None or not path.is_file():
            continue
        lines = _read_note_text(path).splitlines(keepends=True)
        for index, line in enumerate(lines):
            content, ending = _split_line_ending(line)
            anchor = _terminal_anchor_match(content, claim_id)
            anchored = anchor is not None
            numbered = isinstance(line_no, int) and index == line_no - 1
            if not anchored and not numbered:
                continue
            terminal_claim_id = claim_id if anchored else None
            pattern = _terminal_marker_pattern(outcome.check, terminal_claim_id)
            replacement = (
                pattern.sub(" " if isinstance(terminal_claim_id, str) else "", content)
                if clear
                else line
            )
            if not clear and pattern.search(content) is None:
                if anchored:
                    before = content[: anchor.start()]
                    terminal_anchor = content[anchor.start() :]
                    replacement = (
                        before
                        + f"[failed-verification:: {outcome.check}/{date}] "
                        + terminal_anchor
                    )
                else:
                    replacement = (
                        content + f" [failed-verification:: {outcome.check}/{date}]"
                    )
                replacement += ending
            elif clear:
                replacement += ending
            if replacement != line:
                lines[index] = replacement
                _write_note_text(path, "".join(lines))
            break


_ANY_VERIFY_MARKER = r"\[failed-verification:: [A-Za-z0-9-]+/\d{4}-\d{2}-\d{2}\]"


def _terminal_marker_pattern(check, claim_id):
    marker = r"\[failed-verification:: " + re.escape(check) + r"/\d{4}-\d{2}-\d{2}\]"
    if isinstance(claim_id, str):
        trailing = rf"(?:{_ANY_VERIFY_MARKER} )*\^{re.escape(claim_id)}[ \t]*$"
        return re.compile(rf" {marker} (?={trailing})")
    trailing = rf"(?: {_ANY_VERIFY_MARKER})*[ \t]*$"
    return re.compile(rf" {marker}(?={trailing})")


def _terminal_anchor_match(content, claim_id):
    if not isinstance(claim_id, str):
        return None
    return re.search(rf"\^{re.escape(claim_id)}[ \t]*$", content)


def _split_line_ending(line):
    if line.endswith("\r\n"):
        return line[:-2], "\r\n"
    if line.endswith("\n"):
        return line[:-1], "\n"
    return line, ""


def _file_outcomes(vault_root, path, bibliography_universe=None):
    outcomes = (
        quotes.check_all_quotes(vault_root, path)
        + lints.lint_source_status(vault_root, path)
        + lints.lint_contested(vault_root, path)
    )
    if bibliography_universe is not None:
        outcomes = (
            checks.check_citekeys(vault_root, path, bibliography_universe) + outcomes
        )
    return outcomes


def _bibliography_entries(bib):
    return [bib.entry(key) for key in sorted(bib.citekeys)]


def _staleness_outcome(vault_root, base=DEFAULT_BASE):
    result = bibliography.staleness(vault_root, ZoteroClient(base=base))
    reasons = {
        Result.MATCHED: "matched",
        Result.SKIPPED: "no-identifier — bibliography absent",
        Result.UNMATCHED: "stale — bibliography differs or is invalid",
        Result.UNREACHABLE: "outage — bibliography comparison unavailable",
    }
    return checks.Outcome(
        "staleness",
        RepoPathValue(os.fsencode(bibliography.BIB_PATH)),
        result,
        reasons[result],
    )


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
    rw_leg = (
        checks.check_rw_batch(entry, rw, detection_date) if rw is not None else None
    )
    if rw_leg is not None:
        return [rw_leg]
    outcomes = [
        checks.Outcome(
            "doi",
            target,
            Result.UNREACHABLE,
            "outage — network disabled",
            {"synthetic_offline": True},
        ),
        checks.Outcome(
            "metadata",
            target,
            Result.UNREACHABLE,
            "outage — network disabled",
            {"synthetic_offline": True},
        ),
        checks.Outcome(
            "update-notice",
            target,
            Result.UNREACHABLE,
            "outage — network disabled",
            {"synthetic_offline": True},
        ),
    ]
    return outcomes


def _archive_outcomes(vault_root):
    outcomes = []
    for path in sorted((Path(vault_root) / "literatures").glob("*.md")):
        try:
            data, _ = frontmatter.parse(_read_note_text(path))
        except (OSError, UnicodeError, frontmatter.FrontmatterError):
            continue
        archive_url = data.get("archive-url")
        if not isinstance(archive_url, str) or not archive_url:
            continue
        raw_target = data.get("citekey")
        target = (
            raw_target.strip()
            if isinstance(raw_target, str)
            and raw_target.strip()
            and _note_for_citekey(vault_root, raw_target.strip()) is not None
            else RepoPathValue(os.fsencode(path.relative_to(vault_root)))
        )
        try:
            status = webapi.get_status(archive_url, vault_root)
        except webapi.ApiError:
            result = Result.UNREACHABLE
            reason = "outage — archive-url unavailable"
        else:
            if status == 404:
                result = Result.UNMATCHED
                reason = "missing-archive — archive-url 404s"
            else:
                result = Result.MATCHED
                reason = "matched"
        outcomes.append(checks.Outcome("web-archive", target, result, reason))
    return outcomes


def _notice_fingerprint(outcome):
    if outcome.check != "update-notice":
        return None, None, None
    return (
        outcome.extra.get("class"),
        outcome.extra.get("type"),
        outcome.extra.get("notice_date"),
    )


def _effective(outcomes, hashes, vault_root):
    return [
        outcome
        for outcome in outcomes
        if outcome.result is Result.MATCHED
        or not inbox.is_acknowledged(
            vault_root,
            outcome.check,
            outcome.target,
            hashes[id(outcome)],
            *_notice_fingerprint(outcome),
            target_kind=outcome.target_kind,
        )
    ]


def _projection_identity(outcome):
    if outcome.check in {"doi", "metadata", "update-notice"}:
        return outcome.target, outcome.check
    if outcome.check == "quote" and isinstance(outcome.target, str):
        comparison_target = outcome.extra.get("target", "managed-region")
        if (
            "#^" in outcome.target
            and isinstance(comparison_target, str)
            and comparison_target
        ):
            citekey = outcome.target.split("#^", 1)[0]
            return citekey, f"quote:{outcome.target}:{comparison_target}"
    return None


def _apply_state_transitions(vault_root, raw, detection_date):
    """Project raw current state after the candidate-bound decision is frozen."""
    for outcome in raw:
        projection = _projection_identity(outcome)
        if projection is not None:
            citekey, check = projection
            note = _note_for_citekey(vault_root, citekey)
            if note and note.is_file():
                try:
                    text = _read_note_text(note)
                    updated = (
                        events.record_pass(
                            text,
                            check,
                            Result.MATCHED,
                            at=detection_date,
                        )
                        if outcome.result is Result.MATCHED
                        else events.record_failure(text, check, outcome.result)
                    )
                except (
                    OSError,
                    UnicodeError,
                    ValueError,
                    frontmatter.FrontmatterError,
                ):
                    pass
                else:
                    if updated != text:
                        _write_note_text(note, updated)
        if outcome.result is Result.UNMATCHED:
            _mutate_marker(vault_root, outcome, detection_date)
        elif outcome.result is Result.MATCHED:
            _mutate_marker(vault_root, outcome, detection_date, clear=True)


def _warning_effectiveness(outcomes, hashes, vault_root):
    frozen = {}
    for outcome in outcomes:
        statuses = []
        for index, warning in enumerate(outcome.extra.get("warn_notices", [])):
            warning_type = warning.get("type") if isinstance(warning, Mapping) else None
            notice_date = (
                warning.get("notice_date") if isinstance(warning, Mapping) else None
            )
            effective = isinstance(warning_type, str) and not inbox.is_acknowledged(
                vault_root,
                outcome.check,
                outcome.target,
                hashes[id(outcome)],
                "warn",
                warning_type,
                notice_date,
                target_kind=outcome.target_kind,
            )
            frozen[(id(outcome), index)] = effective
            statuses.append(effective)
        frozen[id(outcome)] = any(statuses)
    return frozen


def _file_effects(vault_root, effective, hashes, warning_effective, detection_date):
    """File findings from the frozen candidate-bound decision state."""
    open_keys = set()
    for entry in inbox.open_entries(vault_root):
        open_keys.add(
            (
                entry.check,
                entry.target,
                entry.target_kind,
                entry.result,
                entry.target_hash,
                entry.notice_class,
                entry.notice_type,
                entry.notice_date,
            )
        )
    for outcome in effective:
        target_hash = hashes[id(outcome)]
        if outcome.result is not Result.MATCHED:
            notice_class, notice_type, notice_date = _notice_fingerprint(outcome)
            key = (
                outcome.check,
                outcome.target,
                outcome.target_kind,
                outcome.result.value,
                target_hash,
                notice_class,
                notice_type,
                notice_date,
            )
            if key not in open_keys:
                inbox.append_entry(
                    vault_root,
                    outcome.check,
                    outcome.target,
                    outcome.result,
                    outcome.reason,
                    date=detection_date,
                    target_hash=target_hash,
                    notice_class=notice_class,
                    notice_type=notice_type,
                    notice_date=notice_date,
                    detection_date=(
                        outcome.extra.get("detection_date", detection_date)
                        if notice_class is not None
                        else None
                    ),
                    target_kind=outcome.target_kind,
                )
                open_keys.add(key)
        for index, warning in enumerate(outcome.extra.get("warn_notices", [])):
            if not warning_effective[(id(outcome), index)]:
                continue
            warning_type = warning.get("type")
            if not isinstance(warning_type, str):
                continue
            notice_date = warning.get("notice_date")
            key = (
                outcome.check,
                outcome.target,
                outcome.target_kind,
                Result.UNMATCHED.value,
                target_hash,
                "warn",
                warning_type,
                notice_date,
            )
            if key not in open_keys:
                inbox.append_entry(
                    vault_root,
                    outcome.check,
                    outcome.target,
                    Result.UNMATCHED,
                    f"warn-notice — {warning_type}",
                    date=detection_date,
                    target_hash=target_hash,
                    notice_class="warn",
                    notice_type=warning_type,
                    notice_date=notice_date,
                    detection_date=warning.get("detection_date", detection_date),
                    target_kind=outcome.target_kind,
                )
                open_keys.add(key)


def _plan_state(
    vault_root,
    scope="all",
    network=True,
    detection_date=None,
    rw_csv=None,
    base=DEFAULT_BASE,
    *,
    repository_root=None,
    snapshots=None,
):
    """Compute one complete projection inside a materialized candidate."""
    del scope
    vault = Path(vault_root)
    repository = Path(repository_root) if repository_root is not None else vault
    detection_date = detection_date or datetime.date.today().isoformat()
    raw = []
    try:
        bibliography_universe = bibliography.load(vault)
    except bibliography.BibliographyError as error:
        bibliography_universe = None
        reason = (
            "schema-violation — bibliography JSON/schema invalid"
            if error.result is Result.UNMATCHED
            else "outage — bibliography unreadable"
        )
        raw.append(
            checks.Outcome(
                "staleness",
                RepoPathValue(os.fsencode(bibliography.BIB_PATH)),
                error.result,
                reason,
            )
        )
    else:
        if network:
            raw.append(_staleness_outcome(vault, base))
        else:
            raw.append(
                checks.Outcome(
                    "staleness",
                    RepoPathValue(os.fsencode(bibliography.BIB_PATH)),
                    Result.UNREACHABLE,
                    "outage — network disabled",
                    {"synthetic_offline": True},
                )
            )
    note_files = [
        path
        for folder in ("literatures", "synthesis", "projects")
        for path in sorted((vault / folder).rglob("*.md"))
    ]
    for path in note_files:
        raw.extend(_file_outcomes(vault, path, bibliography_universe))
    rw = checks.load_rw_csv(rw_csv) if rw_csv else None
    entries = (
        _bibliography_entries(bibliography_universe)
        if bibliography_universe is not None
        else []
    )
    for original in entries:
        entry = dict(original)
        if network and not (entry.get("DOI") or entry.get("doi")):
            discovery = identify.discover(vault, entry)
            raw.append(discovery)
            identifiers = discovery.extra.get("identifiers", {})
            if isinstance(identifiers, Mapping):
                entry.update(identifiers)
            entry["_discovery_unreachable"] = discovery.result is Result.UNREACHABLE
        if network:
            raw.extend(_network_outcomes(vault, entry, detection_date, rw))
        else:
            raw.extend(_offline_network_outcomes(entry, detection_date, rw))
    if snapshots is None:
        base_snapshot = None
        candidate_snapshot = None
    else:
        base_snapshot = snapshots.base
        candidate_snapshot = snapshots.candidate
        raw.extend(
            lints.lint_evidence_layer(repository, base_snapshot, candidate_snapshot)
        )
    raw.extend(lints.lint_append_only(repository, base_snapshot, candidate_snapshot))
    raw.extend(
        lints.lint_claim_immutability(repository, base_snapshot, candidate_snapshot)
    )
    raw.extend(lints.lint_published_drift(repository, candidate_snapshot))
    raw.extend(lints.lint_web_archive(vault))
    if network:
        raw.extend(_archive_outcomes(vault))
    authoritative = [
        outcome for outcome in raw if outcome.extra.get("synthetic_offline") is not True
    ]
    hashes = {
        id(outcome): _target_hash(
            vault,
            outcome,
            bibliography_universe,
            base_snapshot=base_snapshot,
            candidate_snapshot=candidate_snapshot,
        )
        for outcome in authoritative
    }
    effective = _effective(authoritative, hashes, vault)
    warning_effective = _warning_effectiveness(authoritative, hashes, vault)
    _apply_state_transitions(vault, authoritative, detection_date)
    _file_effects(vault, effective, hashes, warning_effective, detection_date)
    counts = {}
    for outcome in effective:
        counts[outcome.result.value] = counts.get(outcome.result.value, 0) + 1
    return {"outcomes": raw, "counts": counts}, effective, hashes, warning_effective


def _candidate_destinations_match_live(snapshots, outputs):
    if snapshots.candidate_name == "worktree":
        return
    for output in outputs:
        if snapshots.candidate.image(output.raw_path) != snapshots.live.image(
            output.raw_path
        ):
            raise gitstate.GitStateError(
                "selected candidate differs from live projection destination: "
                f"{encode_repo_path(output.raw_path)}"
            )


def _rollback_prepublication(vault, snapshots, outputs, primary):
    try:
        gitstate.rollback_outputs(vault, snapshots.live, outputs)
    except gitstate.GitStateError as rollback:
        raise gitstate.GitStateError(f"{primary}; {rollback}") from primary
    raise primary


def _verify_state(
    vault_root,
    scope="all",
    network=True,
    detection_date=None,
    rw_csv=None,
    base=DEFAULT_BASE,
    *,
    git_base=None,
    git_candidate="worktree",
    changed_paths_file=None,
    commit_projected=None,
):
    """Run one immutable collect/plan/apply/manifest/publication transaction."""
    vault = Path(vault_root)
    resolved_manifest = (
        gitstate.validate_manifest_destination(vault, Path(changed_paths_file))
        if changed_paths_file is not None
        else None
    )
    snapshots = gitstate.resolve_snapshots(
        vault, git_base=git_base, candidate=git_candidate
    )
    with tempfile.TemporaryDirectory(prefix="harness-verification-plan-") as temporary:
        planning = Path(temporary)
        gitstate.materialize_snapshot(snapshots.candidate, planning)
        report, effective, hashes, warning_effective = _plan_state(
            planning,
            scope,
            network,
            detection_date,
            rw_csv,
            base,
            repository_root=vault,
            snapshots=snapshots,
        )
        planned_snapshot = gitstate.restore_candidate_nonfiles(
            snapshots.candidate, gitstate.snapshot_worktree(planning)
        )
        outputs = gitstate.outputs_between(snapshots.candidate, planned_snapshot)
    outputs = gitstate.validate_planned_outputs(outputs)
    _candidate_destinations_match_live(snapshots, outputs)
    if commit_projected is not None:
        gitstate.validate_dirty_overlap(vault, snapshots, outputs)
    gitstate.apply_outputs(vault, snapshots.live, outputs)
    captured = outputs
    if resolved_manifest is not None:
        try:
            captured = gitstate.audit_and_write_manifest(
                vault,
                snapshots.live,
                outputs,
                resolved_manifest,
                resolved_destination=resolved_manifest,
            )
        except gitstate.GitStateError as error:
            _rollback_prepublication(vault, snapshots, outputs, error)
    if commit_projected is not None:
        gitstate.publish_outputs(vault, snapshots, captured, commit_projected)
    return report, effective, hashes, warning_effective


def run_verify(vault_root, scope="all", network=True, detection_date=None, rw_csv=None):
    """Collect raw outcomes and apply their effective verification effects."""
    report, _effective_outcomes, _hashes, _warnings = _verify_state(
        vault_root, scope, network, detection_date, rw_csv
    )
    return report


def cmd_verify(args):
    surface = getattr(args, "surface", "audit")
    try:
        report, effective, hashes, warning_effective = _verify_state(
            args.vault,
            network=not args.offline,
            rw_csv=args.rw_csv,
            base=getattr(args, "base", DEFAULT_BASE),
            git_base=getattr(args, "git_base", None),
            git_candidate=getattr(args, "git_candidate", "worktree"),
            changed_paths_file=getattr(args, "changed_paths_file", None),
            commit_projected=getattr(args, "commit_projected", None),
        )
    except (gitstate.GitStateError, PathCodecError, OSError, ValueError) as error:
        print(f"verification unavailable: {error}", file=sys.stderr)
        return 2
    for outcome in effective:
        if outcome.result is not Result.MATCHED:
            print(
                f"{outcome.result.value} {outcome.check} {outcome.target} — {outcome.reason}"
            )
        for index, warning in enumerate(outcome.extra.get("warn_notices", [])):
            if warning_effective.get(
                (id(outcome), index), warning_effective.get(id(outcome), False)
            ):
                warning_type = warning.get("type")
                if isinstance(warning_type, str):
                    print(
                        f"UNMATCHED {outcome.check} {outcome.target} — "
                        f"warn-notice — {warning_type}"
                    )
    print(json.dumps(report["counts"], sort_keys=True))
    closing = CLOSING_BY_SURFACE[surface]
    blocking_warning = any(
        outcome.check in closing and warning_effective.get((id(outcome), index), False)
        for outcome in effective
        for index, _warning in enumerate(outcome.extra.get("warn_notices", ()))
    )
    if blocking_warning or any(
        outcome.result is Result.UNMATCHED and outcome.check in closing
        for outcome in effective
    ):
        return 1
    if surface == "audit":
        return 0
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


def cmd_scaffold(args):
    for path in scaffold.scaffold_vault(
        args.vault, with_ci=args.with_ci, with_rw_ci=args.with_rw_ci
    ):
        print(path)
    return 0


def cmd_doctor(args):
    probes = doctor(args.vault, ZoteroClient(base=args.base))
    for name, result, detail in probes:
        prefix = (
            "warn:"
            if name in DOCTOR_WARN_ONLY
            and result in {Result.UNMATCHED, Result.UNREACHABLE}
            else ""
        )
        print(f"{prefix}{result.value} {name} — {detail}")
    if any(
        name in DOCTOR_HARD_UNMATCHED and result is Result.UNMATCHED
        for name, result, _detail in probes
    ):
        return 1
    if any(
        name in DOCTOR_HARD_UNREACHABLE and result is Result.UNREACHABLE
        for name, result, _detail in probes
    ):
        return 3
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
    verify.add_argument("--surface", choices=tuple(CLOSING_BY_SURFACE), default="audit")
    verify.add_argument("--git-base")
    verify.add_argument(
        "--git-candidate", choices=("worktree", "index", "HEAD"), default="worktree"
    )
    verify.add_argument("--changed-paths-file")
    verify.add_argument("--commit-projected")
    review_inbox = sub.add_parser("inbox", parents=[common])
    review_inbox.add_argument("--vault", required=True)
    scaffold_vault = sub.add_parser("scaffold", parents=[common])
    scaffold_vault.add_argument("--vault", required=True)
    scaffold_vault.add_argument("--with-ci", action="store_true")
    scaffold_vault.add_argument("--with-rw-ci", action="store_true")
    doctor_vault = sub.add_parser("doctor", parents=[common])
    doctor_vault.add_argument("--vault", required=True)
    args = parser.parse_args(argv)
    if args.cmd == "verify" and args.commit_projected is not None:
        if not args.commit_projected.strip():
            parser.error("--commit-projected requires a non-empty message")
        if args.changed_paths_file is None:
            parser.error("--commit-projected requires --changed-paths-file")
    if not hasattr(args, "base"):
        args.base = DEFAULT_BASE
    return {
        "probe": cmd_probe,
        "import-note": cmd_import_note,
        "staleness": cmd_staleness,
        "backfill-selectors": cmd_backfill_selectors,
        "verify": cmd_verify,
        "inbox": cmd_inbox,
        "scaffold": cmd_scaffold,
        "doctor": cmd_doctor,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
