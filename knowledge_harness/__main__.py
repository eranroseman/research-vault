"""CLI surface consumed by hooks (Plan C) and skills (Plan D)."""

import argparse
import datetime
import json
import re
import sys
from collections.abc import Mapping
from pathlib import Path

from . import (
    AGENT_ACTOR,
    Result,
    bibliography,
    frontmatter,
    gitstate,
    inbox,
    notes,
    okf,
    paths,
    publish,
    scaffold,
    selectors,
)
from .pathcodec import (
    PathCodecError,
)
from .scaffold import doctor
from .verify import (
    CLOSING_BY_SURFACE,
    DEFAULT_BASE,
    _read_note_text,
    _write_note_text,
    surface_decision,
    verify_state,
)
from .zotero import ZoteroClient, ZoteroError

QUOTE_ANNOTATION_TYPES = {"highlight", "underline"}
DOCTOR_HARD_UNMATCHED = {"tree", "machine-config", "bbt", "autoexport"}
DOCTOR_HARD_UNREACHABLE = {"zotero", "bbt", "autoexport"}
DOCTOR_WARN_ONLY = {"staleness", "remote", "backup", "inbox", "okf"}


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
        "pageLabel": notes.display_text(_text(raw.get("annotationPageLabel"))),
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


_QUOTE_SELECTOR = re.compile(
    r"^- \(quote\)[^\r\n]*\^(?P<claim_id>c-[0-9a-f]{8})\r?\n"
    r"(?:  >[^\r\n]*(?:\r\n|\n|$))*"
    r'  <!-- hk-selector prefix="(?P<prefix>.*?)" suffix="(?P<suffix>.*?)" -->',
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
    try:
        candidate = notes.render_note(
            item,
            hashes,
            annotations,
            existing,
            accessed=now.date().isoformat(),
            generated_at=generated_at,
        )
    except (
        notes.RenderIntegrityError,
        notes.InvalidCitekeyError,
        frontmatter.FrontmatterError,
    ) as error:
        # Ruled 2026-08-21: this class is loud and fail-closed — nothing is
        # written, and it does not file an inbox hold on its own. Uniform
        # hold-to-inbox wiring arrives with integrate-at-import.
        print(f"render rejected for {args.citekey}: {error}", file=sys.stderr)
        return 1

    if not notes.content_changed(existing, candidate):
        print("NOOP")
        return 0
    _write_note_text(path, candidate)
    okf.regenerate_log(vault)
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


def cmd_verify(args):
    surface = getattr(args, "surface", "audit")
    try:
        report, effective, hashes, warning_effective = verify_state(
            args.vault,
            network=not args.offline,
            rw_csv=args.rw_csv,
            base=getattr(args, "base", DEFAULT_BASE),
            git_base=getattr(args, "git_base", None),
            git_candidate=getattr(args, "git_candidate", "worktree"),
            changed_paths_file=getattr(args, "changed_paths_file", None),
            commit_projected=getattr(args, "commit_projected", None),
        )
    except (
        # Named domain failures only. A bare ValueError here would dress an
        # implementation bug as a tidy exit 2 with no traceback.
        gitstate.GitStateError,
        PathCodecError,
        bibliography.BibliographyError,
        inbox.InboxError,
        frontmatter.FrontmatterError,
        notes.ManagedRegionError,
        notes.InvalidCitekeyError,
        notes.RenderIntegrityError,
        OSError,
    ) as error:
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
    decision, _blockers = surface_decision(surface, effective, warning_effective)
    return decision


def cmd_arm_publish(args):
    try:
        path = publish.arm(args.vault, args.project, bypass=args.bypass)
    except publish.PublishError as error:
        print(f"cannot arm the publish gate: {error}", file=sys.stderr)
        return 2
    print(str(path))
    return 0


def cmd_disarm_publish(args):
    try:
        removed = publish.disarm(args.vault)
    except publish.PublishError as error:
        print(f"cannot disarm the publish gate: {error}", file=sys.stderr)
        return 2
    print("disarmed" if removed else "not armed")
    return 0


def _run_disposition(action):
    """Report one disposition: 1/3 are the gate's answer, 2 is our own failure."""
    try:
        outcome = action()
    except (
        publish.PublishError,
        gitstate.GitStateError,
        PathCodecError,
        bibliography.BibliographyError,
        inbox.InboxError,
        frontmatter.FrontmatterError,
        notes.ManagedRegionError,
        notes.InvalidCitekeyError,
        notes.RenderIntegrityError,
        OSError,
    ) as error:
        print(f"cannot complete this disposition: {error}", file=sys.stderr)
        return 2
    for blocker in outcome.blockers:
        print(blocker)
    if outcome.decision:
        return outcome.decision
    print(
        json.dumps(
            {
                "project": f"projects/{outcome.project}",
                "status": outcome.status,
                "commit": outcome.commit,
                "tag": outcome.tag,
            },
            sort_keys=True,
        )
    )
    return 0


def cmd_mark_published(args):
    return _run_disposition(
        lambda: publish.mark_published(args.vault, args.project, base=args.base)
    )


def cmd_mark_corrected(args):
    return _run_disposition(
        lambda: publish.mark_corrected(args.vault, args.project, base=args.base)
    )


def cmd_mark_withdrawn(args):
    return _run_disposition(lambda: publish.mark_withdrawn(args.vault, args.project))


def cmd_park(args):
    return _run_disposition(lambda: publish.park(args.vault, args.project))


def cmd_ack(args):
    try:
        entry = inbox.append_ack(args.vault, args.finding, args.reason, args.actor)
    except (inbox.InboxError, ValueError, OSError) as error:
        print(f"acknowledgment refused: {error}", file=sys.stderr)
        return 2
    print(entry.id)
    return 0


def cmd_finding(args):
    """Append one review-record finding — the writer prose is never allowed to be.

    Factcheck's adjudicated findings and Task 5's import-time holds both go
    through this, so it validates the check id against the governed §4.4
    registry itself (``append_entry`` does not — see ``inbox.CHECK_IDS``).
    A retry that matches an already-open entry exactly (check, target,
    result, and target hash) is a no-op that reprints the existing id,
    mirroring the deterministic pipeline's own open-entry dedup
    (``verify._file_effects``) so a rerun never doubles a standing finding
    into an unacknowledgeable pair.
    """
    if args.check not in inbox.CHECK_IDS:
        print(
            f"finding refused: unregistered check id: {args.check!r}", file=sys.stderr
        )
        return 2
    try:
        result = Result[args.result]
    except KeyError:
        print(f"finding refused: invalid result: {args.result!r}", file=sys.stderr)
        return 2
    actor = args.actor if args.actor is not None else AGENT_ACTOR
    try:
        existing = next(
            (
                entry
                for entry in inbox.open_entries(args.vault)
                if entry.check == args.check
                and entry.target == args.target
                and entry.target_kind == "identifier"
                and entry.result == result.value
                and entry.target_hash == args.target_hash
            ),
            None,
        )
        if existing is not None:
            print(existing.id)
            return 0
        entry = inbox.append_entry(
            args.vault,
            args.check,
            args.target,
            result,
            args.reason,
            actor=actor,
            date=args.date,
            target_hash=args.target_hash,
        )
    except (inbox.InboxError, ValueError, OSError) as error:
        print(f"finding refused: {error}", file=sys.stderr)
        return 2
    print(entry.id)
    return 0


def cmd_inbox(args):
    print(json.dumps(inbox.summary(args.vault), sort_keys=True))
    for entry in sorted(
        inbox.open_entries(args.vault), key=lambda item: (item.date, item.id)
    ):
        # The id leads: it is the argument `ack` requires, and this listing
        # is where the publish skill sends a person to find it.
        print(
            f"{entry.id} {entry.date} {entry.result} {entry.check} "
            f"{entry.target} — {entry.reason}"
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
    for check, result, reason in probes:
        prefix = (
            "warn:"
            if check in DOCTOR_WARN_ONLY
            and result in {Result.UNMATCHED, Result.UNREACHABLE}
            else ""
        )
        print(f"{prefix}{result.value} {check} — {reason}")
    if any(
        check in DOCTOR_HARD_UNMATCHED and result is Result.UNMATCHED
        for check, result, _reason in probes
    ):
        return 1
    if any(
        check in DOCTOR_HARD_UNREACHABLE and result is Result.UNREACHABLE
        for check, result, _reason in probes
    ):
        return 3
    return 0


def main(argv=None):
    # A shared parent accepts --base before or after each subcommand.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--base", default=argparse.SUPPRESS)
    parser = argparse.ArgumentParser(prog="knowledge_harness", parents=[common])
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
    arm_publish = sub.add_parser("arm-publish", parents=[common])
    arm_publish.add_argument("project")
    arm_publish.add_argument("--vault", required=True)
    arm_publish.add_argument("--bypass")
    disarm_publish = sub.add_parser("disarm-publish", parents=[common])
    disarm_publish.add_argument("--vault", required=True)
    for disposition in ("mark-published", "mark-corrected", "mark-withdrawn", "park"):
        verb = sub.add_parser(disposition, parents=[common])
        verb.add_argument("project")
        verb.add_argument("--vault", required=True)
    acknowledge = sub.add_parser("ack", parents=[common])
    acknowledge.add_argument("finding")
    acknowledge.add_argument("--vault", required=True)
    acknowledge.add_argument("--reason", required=True)
    acknowledge.add_argument("--actor", required=True)
    finding = sub.add_parser("finding", parents=[common])
    finding.add_argument("check")
    finding.add_argument("target")
    finding.add_argument("result", choices=tuple(Result.__members__))
    finding.add_argument("reason")
    finding.add_argument("--vault", required=True)
    finding.add_argument("--actor")
    finding.add_argument("--date")
    finding.add_argument("--target-hash")
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
        "arm-publish": cmd_arm_publish,
        "disarm-publish": cmd_disarm_publish,
        "mark-published": cmd_mark_published,
        "mark-corrected": cmd_mark_corrected,
        "mark-withdrawn": cmd_mark_withdrawn,
        "park": cmd_park,
        "ack": cmd_ack,
        "finding": cmd_finding,
        "inbox": cmd_inbox,
        "scaffold": cmd_scaffold,
        "doctor": cmd_doctor,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
