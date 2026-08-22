"""Publish-boundary dispositions: gate flag, statuses, events, and tags (spec §6).

"Publish" is the ``publish`` skill action, not a branch merge. Every
mechanical act is a verb the human chooses: the skill composes and explains,
the human consents, this module writes. No status, event, tag, or
acknowledgment in the publish flow is ever prose-written.

The gate run is always network-capable. Spec §6 rules that synthetic
``--offline`` outcomes "never mutate trust, markers, events, or inbox state",
so no offline switch reaches a disposition — the same reason the Stop hook
declines to clear its flag on a run that produced them.
"""

import datetime
import json
import os
import stat
import subprocess
import tempfile
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path

from . import AGENT_ACTOR, Result, frontmatter, gitstate, okf
from .events import record_pass
from .lints import PUBLISHED_TAG
from .pathcodec import encode_repo_path
from .verify import (
    DEFAULT_BASE,
    _read_note_text,
    _write_note_text,
    surface_decision,
    verify_state,
)

FLAG_NAME = "publish-pending.json"
PROJECTS = "projects"
# The check id a publication mints its project-level `verified` event under
# (§5: publish events attach to the project; terminology §4.4).
PUBLISH_CHECK = "publish"


class PublishError(RuntimeError):
    """A publish disposition cannot be carried out as asked."""


@dataclass(frozen=True)
class Disposition:
    """What one disposition did, or the gate decision that refused it."""

    project: str
    decision: int
    blockers: tuple[str, ...] = ()
    status: str | None = None
    commit: str | None = None
    tag: str | None = None


def _name(project) -> str:
    """Validate a bare project name (``brief``), never its vault path."""
    if (
        not isinstance(project, str)
        or not project
        or any(character in project for character in "\r\n\0")
    ):
        raise PublishError(f"invalid project name: {project!r}")
    components = project.split("/")
    if any(component in {"", ".", ".."} for component in components):
        raise PublishError(f"invalid project name: {project!r}")
    if components[0] == PROJECTS:
        raise PublishError(
            f"pass the project name, not its vault path: {project!r} would name "
            f"{PROJECTS}/{project}"
        )
    return project


def project_dir(vault, project) -> Path:
    """Resolve an existing, symlink-free ``projects/<name>/`` directory."""
    name = _name(project)
    current = Path(vault)
    for component in (PROJECTS, *name.split("/")):
        current = current / component
        try:
            metadata = os.lstat(current)
        except OSError as error:
            raise PublishError(f"no such project directory: {current}") from error
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise PublishError(f"project path is not a real directory: {current}")
    return current


def project_note(vault, project) -> Path:
    """Return the project's single ``type: project`` note — its frontmatter."""
    directory = project_dir(vault, project)
    found = []
    for path in sorted(directory.rglob("*.md")):
        try:
            data, _ = frontmatter.parse(_read_note_text(path))
        except (OSError, UnicodeError, frontmatter.FrontmatterError):
            continue
        if data.get("type") == "project":
            found.append(path)
    if len(found) != 1:
        raise PublishError(
            f"{PROJECTS}/{project} needs exactly one type: project note, "
            f"found {len(found)}"
        )
    return found[0]


def flag_path(vault) -> Path:
    """The Stop gate's state flag; the gate is inert while it is absent."""
    return Path(vault) / ".harness" / FLAG_NAME


def arm(vault, project, bypass=None) -> Path:
    """Write the exact flag shape ``hooks/stop_publish_gate.py`` accepts.

    Any other shape is silently inert — an unarmed vault, not a loud one — so
    the project is resolved here rather than left for the hook to reject.
    """
    try:
        root = Path(vault).resolve(strict=True)
    except OSError as error:
        raise PublishError(f"no such vault: {vault}") from error
    project_dir(root, project)
    # An arming that can only end in an untaggable publication is worth
    # refusing here, before the gate run the person is about to wait for.
    _require_taggable(root, project, datetime.date.today().isoformat())
    state = {"project": f"{PROJECTS}/{project}", "vault": str(root), "blocks": 0}
    if bypass is not None:
        token = bypass.strip() if isinstance(bypass, str) else ""
        if not token or any(character in token for character in "\r\n\0"):
            raise PublishError("a bypass token must be a nonempty single line")
        state["bypass"] = token
    path = flag_path(root)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(
            dir=path.parent, prefix=f".{FLAG_NAME}.arm."
        )
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(
                    json.dumps(state, sort_keys=True, separators=(",", ":")).encode()
                )
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        except OSError:
            with suppress(OSError):
                os.unlink(temporary)
            raise
    except OSError as error:
        raise PublishError(f"cannot arm the publish gate: {error}") from error
    return path


def disarm(vault) -> bool:
    """Remove the gate flag; an unarmed vault is not an error."""
    try:
        flag_path(vault).unlink()
    except FileNotFoundError:
        return False
    except OSError as error:
        raise PublishError(f"cannot disarm the publish gate: {error}") from error
    return True


def _set_status(note_text: str, status: str) -> str:
    """Replace the note's single top-level ``status:`` line and nothing else."""
    lines = note_text.splitlines(keepends=True)
    fence = {"---\n", "---\r\n"}
    if not lines or lines[0] not in fence:
        raise PublishError("project note has no frontmatter")
    close = next(
        (index for index, line in enumerate(lines[1:], start=1) if line in fence),
        None,
    )
    if close is None:
        raise PublishError("project note frontmatter is unterminated")
    headers = [index for index in range(1, close) if lines[index].startswith("status:")]
    if len(headers) != 1:
        raise PublishError(
            f"project note needs exactly one status field, found {len(headers)}"
        )
    line = lines[headers[0]]
    ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
    lines[headers[0]] = f'status: "{status}"{ending}'
    updated = "".join(lines)
    try:
        data, _ = frontmatter.parse(updated)
    except frontmatter.FrontmatterError as error:
        raise PublishError(f"status write broke the frontmatter: {error}") from error
    if data.get("status") != status:
        raise PublishError(f"status write did not round-trip: {status!r}")
    return updated


def _git(vault, *args) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=Path(vault), capture_output=True, text=True, check=False
    )


def published_tags(vault, project) -> list[str]:
    """This project's published tags, matched by the lint's own pattern.

    A ``published/<project>-*`` glob would also admit
    ``published/<project>-extra-<date>``, which names a different project.
    """
    name = _name(project)
    listed = _git(vault, "tag", "--list", "published/*")
    if listed.returncode != 0:
        raise PublishError("cannot list published tags")
    return sorted(
        tag
        for tag in listed.stdout.split()
        if (match := PUBLISHED_TAG.match(tag)) is not None and match.group(1) == name
    )


def _require_taggable(vault, project, date) -> str:
    """Return the publication tag, or refuse before a single byte is written.

    ``PUBLISHED_TAG``'s ``.+`` admits spaces and everything else git forbids in
    a ref, so the pattern alone is not enough. A tag that fails only after
    ``publish_outputs`` has advanced HEAD would leave a project committed as
    `published` with no tag — and `mark-corrected`/`mark-withdrawn` both refuse
    a project with no tag, so nothing in the system could repair it.
    """
    tag = f"published/{project}-{date}"
    if PUBLISHED_TAG.match(tag) is None:
        raise PublishError(f"cannot name a published tag for {project!r}/{date!r}")
    if _git(vault, "check-ref-format", f"refs/tags/{tag}").returncode != 0:
        raise PublishError(
            f"git cannot name the tag this project would need ({tag!r}); "
            "rename the project to something git accepts as a ref"
        )
    return tag


def _require_unpublished(vault, project) -> None:
    """§6's day-one menu is the pre-publication menu.

    After publication the spec gives exactly two dispositions. Re-publishing
    would mint a second tag and event that permanently record a correction as a
    first publication, and parking would flip `status` off `published`, which
    silences `lint_published_drift` for the tag that survives.
    """
    tags = published_tags(vault, project)
    if tags:
        raise PublishError(
            f"{PROJECTS}/{project} is already published ({', '.join(tags)}) — "
            "use mark-corrected to re-publish it as corrected, or mark-withdrawn"
        )


def _require_published(vault, project) -> None:
    if not published_tags(vault, project):
        raise PublishError(
            f"{PROJECTS}/{project} has no published tag — the correction "
            "lifecycle opens only after publication"
        )


def _require_clean_project(snapshots, project, raw_note: bytes) -> None:
    """Refuse when the project carries content the publication cannot commit.

    The publication commit carries only the project note, and
    ``lints.lint_published_drift`` compares the whole ``projects/<name>``
    prefix against the tag, so any other uncommitted file there would leave
    the tag drifting the moment it is minted. Directory presence alone
    carries no content: a project git has never seen is not a refusal.
    """
    prefix = f"{PROJECTS}/{project}".encode()
    for raw_path in sorted(set(snapshots.head.images) | set(snapshots.live.images)):
        if raw_path == raw_note or (
            raw_path != prefix and not raw_path.startswith(prefix + b"/")
        ):
            continue
        committed = snapshots.head.image(raw_path)
        live = snapshots.live.image(raw_path)
        if committed == live:
            continue
        if (committed is None or committed.kind == "directory") and (
            live is None or live.kind == "directory"
        ):
            continue
        raise PublishError(
            f"uncommitted change under {PROJECTS}/{project}: "
            f"{encode_repo_path(raw_path)} — commit the project before publishing"
        )


def _publish(vault, project, status, *, base, date, message) -> Disposition:
    """Run the closed gate, then write status, event, commit, and tag as one act."""
    root = Path(vault)
    note = project_note(root, project)
    date = datetime.date.today().isoformat() if date is None else date
    tag = _require_taggable(root, project, date)

    _report, effective, _hashes, warning_effective = verify_state(
        root, network=True, base=base
    )
    # `_effective` already drops every finding a standing acknowledgment
    # closes, so a green decision here *is* spec §6's "green, or every
    # blocking entry carries a standing ack" — never re-check acks by hand.
    decision, blockers = surface_decision("publish", effective, warning_effective)
    if decision:
        return Disposition(project, decision, blockers)

    existing = _git(root, "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}")
    if existing.returncode == 0:
        raise PublishError(f"tag already exists: {tag}")

    updated = record_pass(
        _set_status(_read_note_text(note), status),
        PUBLISH_CHECK,
        Result.MATCHED,
        at=date,
    )
    snapshots = gitstate.resolve_snapshots(root, candidate="worktree")
    raw_note = os.fsencode(note.relative_to(root))
    _require_clean_project(snapshots, project, raw_note)
    live = snapshots.live.image(raw_note)
    mode = live.mode if live is not None and live.kind == "file" else 0o100644
    output = gitstate.CapturedOutput(raw_note, mode, updated.encode())

    _write_note_text(note, updated)
    try:
        commit = gitstate.publish_outputs(root, snapshots, (output,), message)
    except Exception:
        gitstate.rollback_outputs(root, snapshots.live, (output,))
        raise
    if commit is None:
        raise PublishError("publication produced no commit")
    _create_tag(root, tag, commit)
    disarm(root)
    return Disposition(project, 0, (), status, commit, tag)


def _create_tag(vault, tag: str, commit: str) -> None:
    if _git(vault, "tag", tag, commit).returncode != 0:
        raise PublishError(f"cannot create tag {tag}")


def _append_log(vault, message: str, *, date=None) -> Path:
    """Append one activity line to the day's log, then regenerate root log.md."""
    now = datetime.datetime.now()
    day = Path(vault) / "log" / f"{now.date().isoformat() if date is None else date}.md"
    day.parent.mkdir(parents=True, exist_ok=True)
    if not day.exists() or not day.read_bytes():
        day.write_text(frontmatter.serialize({"type": "daily"}))
    with day.open("a", encoding="utf-8", newline="") as stream:
        stream.write(f"- {now:%H:%M} {AGENT_ACTOR} — {message}\n")
    okf.regenerate_log(vault)
    return day


def mark_published(vault, project, *, base=DEFAULT_BASE, date=None) -> Disposition:
    """Publish: gate run, ``status: published``, `verified` event, commit, tag, disarm.

    Pre-publication only; an already-published project goes through
    `mark_corrected` or `mark_withdrawn` (§6's correction lifecycle).
    """
    _require_unpublished(vault, project)
    return _publish(
        vault,
        project,
        "published",
        base=base,
        date=date,
        message=f"publish: {PROJECTS}/{project}",
    )


def mark_corrected(vault, project, *, base=DEFAULT_BASE, date=None) -> Disposition:
    """Re-publish a published project as ``corrected``: new gate run, event, tag.

    Post-publish only (§6's IFCN corrections principle). The original tag is
    never deleted (ADR 0003).
    """
    _require_published(vault, project)
    return _publish(
        vault,
        project,
        "corrected",
        base=base,
        date=date,
        message=f"publish: {PROJECTS}/{project} corrected",
    )


def mark_withdrawn(vault, project, *, date=None) -> Disposition:
    """Withdraw a published project: a status write and a log line, nothing more.

    Post-publish only. No new tag, and the original tag is never deleted.
    """
    _require_published(vault, project)
    note = project_note(vault, project)
    _write_note_text(note, _set_status(_read_note_text(note), "withdrawn"))
    _append_log(vault, f"withdrew {PROJECTS}/{project}", date=date)
    return Disposition(project, 0, (), "withdrawn")


def park(vault, project) -> Disposition:
    """Park a project: sets ``status: parked``, nothing else (§6's day-one menu).

    Pre-publication only, for the same reason the menu it belongs to is.
    """
    _require_unpublished(vault, project)
    note = project_note(vault, project)
    _write_note_text(note, _set_status(_read_note_text(note), "parked"))
    return Disposition(project, 0, (), "parked")
