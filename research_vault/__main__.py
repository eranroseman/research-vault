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
    events,
    factcheck,
    frontmatter,
    gitstate,
    inbox,
    notes,
    okf,
    paths,
    publish,
    scaffold,
    searchlog,
    selectors,
    stamp,
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
DOCTOR_WARN_ONLY = {"staleness", "remote", "backup"}


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
    r'  <!-- rv-selector prefix="(?P<prefix>.*?)" suffix="(?P<suffix>.*?)" -->',
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


def _hold(vault, check, target, result: Result, reason: str) -> None:
    """File one import hold through ``record_finding`` — never a forked writer.

    Additive to the failure exit that calls it: stderr and the exit code stay
    exactly as they were, and a landed hold prints nothing. A *refused* hold is
    the one thing this says out loud — an unrepresentable citekey or an id
    already carrying a different finding leaves the queue without the record,
    and a silently missing review record is the failure this reports.
    """
    status, detail = record_finding(vault, check, target, result, reason)
    if status:
        print(f"warning: review record refused: {detail}", file=sys.stderr)


def _hold_reason(code: str, detail: str) -> str:
    """Compose a reason-coded line from a code and free-text detail."""
    detail = notes.display_text(detail)
    return f"{code} — {detail}" if detail else code


def cmd_import_note(args):
    try:
        path = notes.note_path(args.vault, args.citekey)
    except notes.InvalidCitekeyError:
        print(f"invalid citekey: {args.citekey!r}", file=sys.stderr)
        _hold(
            args.vault,
            "citekey",
            args.citekey,
            Result.UNMATCHED,
            "schema-violation — citekey cannot name a literature note",
        )
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
        _hold(
            vault,
            "citekey",
            args.citekey,
            Result.UNMATCHED,
            "not-admitted — citekey is absent from the Zotero library",
        )
        return 1
    item = matches[0]
    item["id"] = args.citekey

    observed = bibliography.observe_autoexport(vault, client)
    if observed.result is not Result.MATCHED:
        print(observed.detail, file=sys.stderr)
        unmatched = observed.result is Result.UNMATCHED
        _hold(
            vault,
            "autoexport",
            args.citekey,
            observed.result,
            _hold_reason("mismatch" if unmatched else "outage", observed.detail),
        )
        return 1 if unmatched else 3

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

    now = datetime.datetime.now(datetime.UTC).replace(microsecond=0)
    generated_at = notes.generated_at_now(now)
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
        # Ruled 2026-08-21, wired 2026-08-22 with integrate-at-import: this
        # class stays loud and fail-closed — nothing is written and stderr and
        # the exit code are unchanged — and it now also files its reason-coded
        # hold, like every other failure exit here.
        print(f"render rejected for {args.citekey}: {error}", file=sys.stderr)
        _hold(
            vault,
            "render",
            args.citekey,
            Result.UNMATCHED,
            _hold_reason("schema-violation", str(error) or "render rejected"),
        )
        return 1

    if not notes.content_changed(existing, candidate):
        print("NOOP")
        return 0
    _write_note_text(path, candidate)
    stamp.stamp_types(vault)
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
        report, effective, _hashes, warning_effective = verify_state(
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
    if not args.rw_csv:
        # Stdout line only — never a review-queue record.
        print("update-notice: RW leg not run (no --rw-csv)")
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


def cmd_factcheck(args):
    """Deterministically select claims for one factored-verification pass.

    Read-only report over ``factcheck.run`` — the CLI's single exit-code
    contract, one binary (§7), same shape as every other report verb: it
    prints a JSON selection and writes nothing durable. The actual writes
    (adjudicated findings, the skipped-set record) go through `finding`,
    called by the `factcheck-draft` skill after reading this report.
    """
    draft = Path(args.draft)
    if not draft.is_absolute():
        draft = Path(args.vault) / draft
    try:
        report = factcheck.run(args.vault, draft, args.cap)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"selection unavailable: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def cmd_trust_tier(args):
    """Report one literature note's derived trust tier (spec §5) — read-only.

    ``events.trust_tier`` had no production consumer at HEAD — only tests
    exercised it. `project-flow`'s resume-orientation step needs to display each
    cited note's tier, and a prompt skill cannot call a Python function
    directly, so this is the invocable surface: a read-only mechanical part
    joining the one binary as a bare report noun (§7's
    one-binary/one-exit-code-contract CLI), the same shape as `factcheck`
    and `verify`. It writes nothing — no event, status, tag, hold, or ack.

    Every way this verb can fail is the verb failing to run — an unsafe
    citekey, no such note, unreadable frontmatter — so all of them exit 2,
    the exit-code contract's "could not run", never a four-state verdict.
    """
    try:
        path = notes.note_path(args.vault, args.citekey)
    except notes.InvalidCitekeyError:
        print(f"invalid citekey: {args.citekey!r}", file=sys.stderr)
        return 2
    if not path.is_file():
        print(f"literature note not found: {args.citekey}", file=sys.stderr)
        return 2
    try:
        tier = events.trust_tier(_read_note_text(path))
    except (OSError, UnicodeError, frontmatter.FrontmatterError) as error:
        print(f"trust tier unavailable: {error}", file=sys.stderr)
        return 2
    print(tier)
    return 0


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


# §6's fixed disposition menu: one entry per verb, and the only thing that
# differs between them. `--date` reaches the three that stamp a dated artifact
# (a tag, a project-level `verified` event, a log line) — it is what makes a
# same-day correction expressible at all — and never rides as a tag suffix,
# which would break `PUBLISHED_TAG` and the newest-tag ordering the
# published-drift lint depends on.
_DISPOSITIONS = {
    "mark-published": lambda args: publish.mark_published(
        args.vault, args.project, base=args.base, date=args.date
    ),
    "mark-corrected": lambda args: publish.mark_corrected(
        args.vault, args.project, base=args.base, date=args.date
    ),
    "mark-withdrawn": lambda args: publish.mark_withdrawn(
        args.vault, args.project, date=args.date
    ),
    "mark-parked": lambda args: publish.mark_parked(args.vault, args.project),
}


def cmd_disposition(args):
    """Carry out one of §6's four dispositions; the subcommand names which."""
    return _run_disposition(lambda: _DISPOSITIONS[args.cmd](args))


def cmd_ack(args):
    try:
        entry = inbox.append_ack(args.vault, args.finding, args.reason, args.actor)
    except (inbox.InboxError, ValueError, OSError) as error:
        print(f"acknowledgment refused: {error}", file=sys.stderr)
        return 2
    print(entry.id)
    return 0


def record_finding(
    vault,
    check,
    target,
    result: Result,
    reason: str,
    actor=None,
    date=None,
    target_hash=None,
) -> tuple[int, str]:
    """The single review-record writer above ``inbox.append_entry``.

    ``inbox.finding_id`` does not fold `result` into the id, so two calls
    differing only in result or reason compute the *same* id — and
    ``append_ack`` needs exactly one open row per id, so a second append would
    leave both permanently unacknowledgeable. An exact duplicate is a retry and
    returns the existing id; anything else refuses. Answers ``(0, finding_id)``
    or ``(2, detail)``, and no caller may swallow ``detail``.
    """
    if check not in inbox.CHECK_IDS:
        return 2, f"unregistered check id: {check!r}"
    if result is Result.MATCHED:
        return 2, (
            "MATCHED never files a finding — only a deterministic check may "
            "record a pass, and it mints a `verified` event instead"
        )
    # SKIPPED is spec §6's "automatic-only" result everywhere except factored
    # verification's budget-cap bookkeeping, which nothing else could record.
    if result is Result.SKIPPED and check != "factcheck":
        return 2, (
            f"SKIPPED is automatic-only for {check!r} — never agent- or "
            "prose-settable; only the deterministic pipeline itself may "
            "record it"
        )
    try:
        inbox.validate_reason(reason)
    except ValueError as error:
        return 2, str(error)
    actor = AGENT_ACTOR if actor is None else actor
    resolved_date = (
        datetime.datetime.now(datetime.UTC).date().isoformat() if date is None else date
    )
    try:
        candidate_id = inbox.finding_id(
            check,
            target,
            resolved_date,
            target_hash,
            None,
            None,
            None,
            "identifier",
            reason,
        )
        colliding = [
            entry
            for entry in inbox.load(vault)
            if entry.ack_of is None and entry.id == candidate_id
        ]
        if colliding:
            existing = colliding[0]
            duplicate = (
                existing.check == check
                and existing.target == target
                and existing.target_kind == "identifier"
                and existing.result == result.value
                and existing.reason == reason
                and existing.actor == actor
                and existing.target_hash == target_hash
            )
            if duplicate:
                return 0, existing.id
            return 2, (
                f"{candidate_id!r} is already recorded with different content "
                f"(result={existing.result} reason={existing.reason!r} "
                f"actor={existing.actor!r} target-hash={existing.target_hash!r}) "
                "— this id cannot carry two distinct findings; ack the existing "
                "one first, or supply a distinct --target-hash so each stays "
                "separately identifiable and acknowledgeable"
            )
        entry = inbox.append_entry(
            vault,
            check,
            target,
            result,
            reason,
            actor=actor,
            date=date,
            target_hash=target_hash,
        )
    except (inbox.InboxError, ValueError, OSError) as error:
        return 2, str(error)
    return 0, entry.id


def cmd_finding(args):
    """Expose ``record_finding`` as the CLI verb skills call."""
    status, detail = record_finding(
        args.vault,
        args.check,
        args.target,
        Result[args.result],
        args.reason,
        actor=args.actor,
        date=args.date,
        target_hash=args.target_hash,
    )
    if status:
        print(f"finding refused: {detail}", file=sys.stderr)
        return status
    print(detail)
    return 0


def cmd_search_log(args):
    """Append one PRISMA-S search-log record (spec §7 `find-sources` row).

    Two record kinds through one verb, mutually exclusive per call: a search
    run (``--query``, with ``--source`` and ``--hits``) or a not-admitted
    candidate (``--not-admitted``, with ``--reason``). `find-sources` never
    hand-writes ``projects/<name>/search-log.md`` — every line, of either
    kind, is this verb.
    """
    query_given = args.query is not None
    not_admitted_given = args.not_admitted is not None
    if query_given == not_admitted_given:
        print(
            "search-log refused: pass exactly one of --query (a search run) "
            "or --not-admitted (a candidate)",
            file=sys.stderr,
        )
        return 2
    # `--source` rides on both kinds; `--hits` and `--reason` each belong to
    # one. A caller who passes the other kind's flag believes they are writing
    # a record they are not, so the value is refused rather than dropped.
    kind, crossed, crossed_value = (
        ("--query", "--reason", args.reason)
        if query_given
        else ("--not-admitted", "--hits", args.hits)
    )
    if crossed_value is not None:
        print(
            f"search-log refused: {crossed} belongs to the other record kind, "
            f"never to {kind}",
            file=sys.stderr,
        )
        return 2
    actor = args.actor or AGENT_ACTOR
    try:
        if query_given:
            if args.source is None or args.hits is None:
                print(
                    "search-log refused: --query requires --source and --hits",
                    file=sys.stderr,
                )
                return 2
            entry = searchlog.append_search(
                args.vault,
                args.project,
                args.query,
                args.source,
                args.hits,
                date=args.date,
                actor=actor,
            )
            print(f"{entry.date} {entry.source} — {entry.hits} hits — {entry.query}")
        else:
            if args.reason is None:
                print(
                    "search-log refused: --not-admitted requires --reason",
                    file=sys.stderr,
                )
                return 2
            declined = searchlog.append_not_admitted(
                args.vault,
                args.project,
                args.not_admitted,
                args.reason,
                source=args.source,
                date=args.date,
                actor=actor,
            )
            print(
                f"{declined.date} not-admitted {declined.candidate} — {declined.reason}"
            )
    except (searchlog.SearchLogError, ValueError, OSError) as error:
        print(f"search-log refused: {error}", file=sys.stderr)
        return 2
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


def cmd_stamp_type(args):
    """A fixer, not a gate: mechanically stamp what's fully determined, report
    the rest, always exit 0."""
    stamped, reported = stamp.stamp_types(args.vault)
    for path in stamped:
        print(f"stamped {path}")
    for path, reason in reported:
        if reason == "unparseable":
            print(f"skipped {path} — frontmatter is unparseable")
        elif reason == "symlink":
            print(f"skipped {path} — path is a symlink, refusing to write through it")
        else:
            print(f"skipped {path} — no type could be derived")
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
    parser = argparse.ArgumentParser(prog="research_vault", parents=[common])
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
    factcheck_cmd = sub.add_parser("factcheck", parents=[common])
    factcheck_cmd.add_argument("--vault", required=True)
    factcheck_cmd.add_argument("--draft", required=True)
    factcheck_cmd.add_argument("--cap", type=int, default=factcheck.DEFAULT_CAP)
    trust_tier_cmd = sub.add_parser("trust-tier", parents=[common])
    trust_tier_cmd.add_argument("citekey")
    trust_tier_cmd.add_argument("--vault", required=True)
    arm_publish = sub.add_parser("arm-publish", parents=[common])
    arm_publish.add_argument("project")
    arm_publish.add_argument("--vault", required=True)
    arm_publish.add_argument("--bypass")
    disarm_publish = sub.add_parser("disarm-publish", parents=[common])
    disarm_publish.add_argument("--vault", required=True)
    for disposition in _DISPOSITIONS:
        verb = sub.add_parser(disposition, parents=[common])
        verb.add_argument("project")
        verb.add_argument("--vault", required=True)
        # Parking writes a status and nothing dated, so it takes no --date: a
        # flag the verb would silently discard is its own defect.
        if disposition != "mark-parked":
            verb.add_argument("--date")
    acknowledge = sub.add_parser("ack", parents=[common])
    acknowledge.add_argument("finding")
    acknowledge.add_argument("--vault", required=True)
    acknowledge.add_argument("--reason", required=True)
    acknowledge.add_argument("--actor", required=True)
    finding = sub.add_parser("finding", parents=[common])
    finding.add_argument("check")
    finding.add_argument("target")
    finding.add_argument(
        "result",
        choices=tuple(name for name in Result.__members__ if name != "MATCHED"),
    )
    finding.add_argument("reason")
    finding.add_argument("--vault", required=True)
    finding.add_argument("--actor")
    finding.add_argument("--date")
    finding.add_argument("--target-hash")
    search_log = sub.add_parser("search-log", parents=[common])
    search_log.add_argument("--vault", required=True)
    search_log.add_argument("--project", required=True)
    search_log.add_argument("--query")
    search_log.add_argument("--source")
    search_log.add_argument("--hits", type=int)
    search_log.add_argument("--not-admitted", dest="not_admitted")
    search_log.add_argument("--reason")
    search_log.add_argument("--date")
    search_log.add_argument("--actor")
    review_inbox = sub.add_parser("inbox", parents=[common])
    review_inbox.add_argument("--vault", required=True)
    scaffold_vault = sub.add_parser("scaffold", parents=[common])
    scaffold_vault.add_argument("--vault", required=True)
    scaffold_vault.add_argument("--with-ci", action="store_true")
    scaffold_vault.add_argument("--with-rw-ci", action="store_true")
    doctor_vault = sub.add_parser("doctor", parents=[common])
    doctor_vault.add_argument("--vault", required=True)
    stamp_type = sub.add_parser("stamp-type", parents=[common])
    stamp_type.add_argument("--vault", required=True)
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
        "factcheck": cmd_factcheck,
        "trust-tier": cmd_trust_tier,
        "arm-publish": cmd_arm_publish,
        "disarm-publish": cmd_disarm_publish,
        **dict.fromkeys(_DISPOSITIONS, cmd_disposition),
        "ack": cmd_ack,
        "finding": cmd_finding,
        "search-log": cmd_search_log,
        "inbox": cmd_inbox,
        "scaffold": cmd_scaffold,
        "doctor": cmd_doctor,
        "stamp-type": cmd_stamp_type,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
