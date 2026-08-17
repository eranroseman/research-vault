"""Offline, warn-tier integrity lints for the knowledge harness."""

from __future__ import annotations

import re
import subprocess
from datetime import date
from pathlib import Path

from . import Result, frontmatter
from . import claims as claims_mod
from .checks import Outcome

ANCHOR = re.compile(r"\^(c-[A-Za-z0-9-]+)\s*$")
VERIFY_FAILED = re.compile(r"\[verify-failed:: [A-Za-z0-9-]+/\d{4}-\d{2}-\d{2}\]")
ADDRESS = re.compile(r"\[\[([A-Za-z0-9_.:-]+#\^c-[A-Za-z0-9-]+)\]\]")
PUBLISHED_TAG = re.compile(r"^published/(.+)-\d{4}-\d{2}-\d{2}$")
TRANSITION_FIELD = re.compile(
    r"\[(status|deprecated-at|deprecated-by|reason):: ([^\]]*)\]"
)


def _git(vault_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=vault_root, capture_output=True, text=True, check=False
    )


def _deduplicate(outcomes: list[Outcome]) -> list[Outcome]:
    """Return stable findings; repeated references must not flood the inbox."""

    def extra_key(extra: dict) -> tuple[tuple[str, str], ...]:
        return tuple(sorted((key, repr(value)) for key, value in extra.items()))

    seen = set()
    result = []
    for outcome in sorted(
        outcomes,
        key=lambda item: (
            item.check,
            item.target,
            item.reason,
            extra_key(item.extra),
        ),
    ):
        key = (
            outcome.check,
            outcome.target,
            outcome.result,
            outcome.reason,
            extra_key(outcome.extra),
        )
        if key not in seen:
            seen.add(key)
            result.append(outcome)
    return result


def _relative(vault_root: Path, path: Path) -> str:
    return path.relative_to(vault_root).as_posix()


def _parse_frontmatter(text: str) -> tuple[dict, bool]:
    try:
        data, _ = frontmatter.parse(text)
    except frontmatter.FrontmatterError:
        return {}, False
    return data, True


def _schema_outcome(check: str, target: str, extra: dict | None = None) -> Outcome:
    return Outcome(
        check,
        target,
        Result.UNMATCHED,
        "schema-violation — malformed frontmatter",
        extra=extra or {},
    )


def lint_append_only(vault_root) -> list[Outcome]:
    """Detect deleted historical content, one finding for every affected file."""
    vault = Path(vault_root)
    changed = _git(
        vault, "diff", "--name-only", "HEAD", "--", "calendar", "+/review-queue.md"
    )
    outcomes = []
    for rel in sorted(set(changed.stdout.splitlines())):
        diff = _git(vault, "diff", "HEAD", "--unified=0", "--", rel).stdout
        if any(
            line.startswith("-") and not line.startswith("---")
            for line in diff.splitlines()
        ):
            outcomes.append(
                Outcome(
                    "append-only",
                    rel,
                    Result.UNMATCHED,
                    "drift — append-only file rewrote history",
                )
            )
    return outcomes


def _head_text(vault_root: Path, rel: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"HEAD:{rel}"], cwd=vault_root, capture_output=True, check=False
    )
    return (
        result.stdout.decode(errors="surrogateescape")
        if result.returncode == 0
        else None
    )


def _head_markdown_paths(vault_root: Path) -> set[str]:
    result = _git(
        vault_root,
        "ls-tree",
        "-r",
        "--name-only",
        "HEAD",
        "--",
        "literatures",
        "atlas",
        "efforts",
    )
    return {path for path in result.stdout.splitlines() if path.endswith(".md")}


def _current_markdown_paths(vault_root: Path) -> set[str]:
    paths = set()
    for folder in ("literatures", "atlas", "efforts"):
        base = vault_root / folder
        if base.is_dir():
            paths.update(
                _relative(vault_root, path)
                for path in base.rglob("*.md")
                if path.is_file()
            )
    return paths


def _claim_blocks(text: str) -> dict[str, str]:
    """Return full anchored claim blocks, including quote and selector continuations."""
    blocks = {}
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        match = ANCHOR.search(line.rstrip("\r\n"))
        if match is None:
            continue
        block = [line]
        for continuation in lines[index + 1 :]:
            if continuation.startswith(("  > ", "  <!-- hk-sel")):
                block.append(continuation)
            else:
                break
        blocks[match.group(1)] = "".join(block)
    return blocks


def _block_lines(block: str) -> list[str]:
    return block.splitlines(keepends=True)


def _line_content_and_ending(line: str) -> tuple[str, str]:
    match = re.search(r"(?:\r\n|\n|\r)$", line)
    if match is None:
        return line, ""
    return line[: match.start()], match.group()


def _remove_single_marker(line: str) -> str | None:
    """Remove one marker and its one separator; reject all other marker shapes."""
    matches = list(VERIFY_FAILED.finditer(line))
    if len(matches) != 1:
        return None
    match = matches[0]
    if match.start() and line[match.start() - 1].isspace():
        return line[: match.start() - 1] + line[match.end() :]
    if match.end() < len(line) and line[match.end()].isspace():
        return line[: match.start()] + line[match.end() + 1 :]
    return line[: match.start()] + line[match.end() :]


def _normalize_marker_transition(old_block: str, new_block: str) -> tuple[str, str]:
    """Normalize exactly one marker addition/removal, never a marker replacement."""
    old_lines = _block_lines(old_block)
    new_lines = _block_lines(new_block)
    if len(old_lines) != len(new_lines) or old_lines[1:] != new_lines[1:]:
        return old_block, new_block
    old_content, old_ending = _line_content_and_ending(old_lines[0])
    new_content, new_ending = _line_content_and_ending(new_lines[0])
    old_count = len(VERIFY_FAILED.findall(old_content))
    new_count = len(VERIFY_FAILED.findall(new_content))
    if (old_count, new_count) == (0, 1):
        stripped = _remove_single_marker(new_content)
        if stripped is not None:
            new_lines[0] = stripped + new_ending
    elif (old_count, new_count) == (1, 0):
        stripped = _remove_single_marker(old_content)
        if stripped is not None:
            old_lines[0] = stripped + old_ending
    return "".join(old_lines), "".join(new_lines)


def _without_fields(line: str, names: set[str]) -> str:
    return re.sub(
        r"\s+\[(" + "|".join(re.escape(name) for name in names) + r"):: [^\]]*\]",
        "",
        line,
    )


def _is_complete_deprecation_transition(old_block: str, new_block: str) -> bool:
    old_block, new_block = _normalize_marker_transition(old_block, new_block)
    old_lines = _block_lines(old_block)
    new_lines = _block_lines(new_block)
    if len(old_lines) != len(new_lines) or old_lines[1:] != new_lines[1:]:
        return False
    old_line, old_ending = _line_content_and_ending(old_lines[0])
    new_line, new_ending = _line_content_and_ending(new_lines[0])
    if old_ending != new_ending:
        return False
    required = {"status", "deprecated-at", "deprecated-by", "reason"}
    fields = {name: [] for name in required}
    for name, value in TRANSITION_FIELD.findall(new_line):
        fields[name].append(value)
    if any(len(values) != 1 for values in fields.values()):
        return False
    if fields["status"] != ["deprecated"]:
        return False
    if any(not fields[name][0].strip() for name in required - {"status"}):
        return False
    try:
        date.fromisoformat(fields["deprecated-at"][0])
    except ValueError:
        return False
    if TRANSITION_FIELD.search(old_line) and "[status:: deprecated]" in old_line:
        return False
    old_base = _without_fields(old_line, {"status"})
    new_base = _without_fields(new_line, required)
    return old_base == new_base


def _claim_target(rel: str, text: str, claim_id: str) -> str:
    data, parsed = _parse_frontmatter(text)
    citekey = data.get("citekey") if parsed else None
    if isinstance(citekey, str) and citekey:
        return claims_mod.claim_address(citekey, claim_id)
    return f"{rel}#^{claim_id}"


def lint_claim_immutability(vault_root) -> list[Outcome]:
    """Require committed claims to stay byte-identical absent a real transition."""
    vault = Path(vault_root)
    outcomes = []
    for rel in sorted(_head_markdown_paths(vault) | _current_markdown_paths(vault)):
        head = _head_text(vault, rel)
        if head is None:
            continue
        current_path = vault / rel
        current = (
            current_path.read_bytes().decode(errors="surrogateescape")
            if current_path.is_file()
            else ""
        )
        _, parsed = _parse_frontmatter(current if current_path.is_file() else head)
        if current_path.is_file() and not parsed:
            outcomes.append(_schema_outcome("claim-immutability", rel))
        old_blocks = _claim_blocks(head)
        new_blocks = _claim_blocks(current)
        for claim_id, old_block in old_blocks.items():
            new_block = new_blocks.get(claim_id)
            if new_block is not None:
                normalized_old, normalized_new = _normalize_marker_transition(
                    old_block, new_block
                )
                unchanged = normalized_old == normalized_new
            else:
                unchanged = False
            if unchanged or (
                new_block and _is_complete_deprecation_transition(old_block, new_block)
            ):
                continue
            outcomes.append(
                Outcome(
                    "claim-immutability",
                    _claim_target(rel, head, claim_id),
                    Result.UNMATCHED,
                    f"drift — claim ^{claim_id} mutated or vanished without deprecation",
                    extra={"note_path": rel, "claim_id": claim_id},
                )
            )
    return _deduplicate(outcomes)


def _tag_paths(vault_root: Path, tag: str, prefix: str) -> set[str]:
    result = _git(vault_root, "ls-tree", "-r", "--name-only", tag, "--", prefix)
    return set(result.stdout.splitlines())


def _current_paths(vault_root: Path, prefix: str) -> set[str]:
    base = vault_root / prefix
    if not base.is_dir():
        return set()
    return {_relative(vault_root, path) for path in base.rglob("*") if path.is_file()}


def _tag_bytes(vault_root: Path, tag: str, rel: str) -> bytes | None:
    result = subprocess.run(
        ["git", "show", f"{tag}:{rel}"],
        cwd=vault_root,
        capture_output=True,
        check=False,
    )
    return result.stdout if result.returncode == 0 else None


def _effort_status(
    vault_root: Path, prefix: str, tag: str | None = None
) -> tuple[set[str], list[str]]:
    paths = (
        _tag_paths(vault_root, tag, prefix)
        if tag
        else _current_paths(vault_root, prefix)
    )
    statuses, malformed = set(), []
    for rel in sorted(path for path in paths if path.endswith(".md")):
        if tag:
            raw = _tag_bytes(vault_root, tag, rel)
            text = raw.decode(errors="surrogateescape") if raw is not None else ""
        else:
            text = (vault_root / rel).read_bytes().decode(errors="surrogateescape")
        data, parsed = _parse_frontmatter(text)
        if not parsed:
            malformed.append(rel)
        elif isinstance(data.get("status"), str):
            statuses.add(data["status"])
    return statuses, malformed


def _effort_differs(vault_root: Path, tag: str, prefix: str) -> bool:
    for rel in _tag_paths(vault_root, tag, prefix) | _current_paths(vault_root, prefix):
        current = (
            (vault_root / rel).read_bytes() if (vault_root / rel).is_file() else None
        )
        if _tag_bytes(vault_root, tag, rel) != current:
            return True
    return False


def lint_published_drift(vault_root) -> list[Outcome]:
    """Compare every published tag to the working tree, including untracked files."""
    vault = Path(vault_root)
    tags = sorted(_git(vault, "tag", "--list", "published/*").stdout.split())
    outcomes = []
    for tag in tags:
        match = PUBLISHED_TAG.match(tag)
        if match is None:
            continue
        effort_dir = f"efforts/{match.group(1)}"
        if not _effort_differs(vault, tag, effort_dir):
            continue
        current_statuses, malformed = _effort_status(vault, effort_dir)
        for rel in malformed:
            outcomes.append(_schema_outcome("published-drift", rel))
        if current_statuses:
            published = "published" in current_statuses
        else:
            prior_statuses, prior_malformed = _effort_status(vault, effort_dir, tag)
            for rel in prior_malformed:
                outcomes.append(_schema_outcome("published-drift", rel))
            published = "published" in prior_statuses
        if published:
            outcomes.append(
                Outcome(
                    "published-drift",
                    effort_dir,
                    Result.UNMATCHED,
                    "drift — published effort diverged from its tag",
                )
            )
    return _deduplicate(outcomes)


def _origin(
    vault_root: Path, note_file: Path, claim, fallback: str
) -> tuple[str, dict]:
    vault = Path(vault_root)
    note = Path(note_file)
    rel = _relative(vault, note)
    data, parsed = _parse_frontmatter(note.read_text())
    citekey = data.get("citekey") if parsed else None
    if claim.claim_id and isinstance(citekey, str) and citekey:
        target = claims_mod.claim_address(citekey, claim.claim_id)
    else:
        target = fallback
    return target, {"note_path": rel, "claim_id": claim.claim_id}


def _note_status(vault_root: Path, citekey: str) -> tuple[str | None, str | None, bool]:
    path = vault_root / "literatures" / f"{citekey}.md"
    if not path.is_file():
        return None, None, True
    data, parsed = _parse_frontmatter(path.read_text())
    if not parsed:
        return None, None, False
    return data.get("status"), data.get("superseded-by"), True


def lint_source_status(vault_root, note_file) -> list[Outcome]:
    vault, note = Path(vault_root), Path(note_file)
    text = note.read_text()
    outcomes = []
    lines = text.splitlines()
    for claim in claims_mod.parse_claims(text):
        citekeys = [
            match.group("key")
            for match in claims_mod.CITE_RE.finditer(lines[claim.line_no - 1])
        ]
        for citekey in citekeys:
            target, extra = _origin(vault, note, claim, citekey)
            status, successor, parsed = _note_status(vault, citekey)
            if not parsed:
                outcomes.append(_schema_outcome("source-status", target, extra))
            elif status in {"rejected", "superseded"}:
                suffix = f" (superseded-by {successor})" if successor else ""
                outcomes.append(
                    Outcome(
                        "source-status",
                        target,
                        Result.UNMATCHED,
                        f"superseded-source — cites {citekey} with status {status}{suffix}",
                        extra=extra,
                    )
                )
    return _deduplicate(outcomes)


def _contested_addresses(vault_root: Path) -> tuple[set[str], list[Outcome]]:
    contested, outcomes = set(), []
    for path in (
        sorted((vault_root / "atlas").rglob("*.md"))
        if (vault_root / "atlas").is_dir()
        else []
    ):
        rel = _relative(vault_root, path)
        text = path.read_text()
        data, parsed = _parse_frontmatter(text)
        if not parsed:
            outcomes.append(_schema_outcome("contested", rel))
        page_key = data.get("citekey") if parsed else None
        if not isinstance(page_key, str) or not page_key:
            page_key = path.stem
        for claim in claims_mod.parse_claims(text):
            if "contested-by" not in claim.fields:
                continue
            if claim.claim_id:
                contested.add(claims_mod.claim_address(page_key, claim.claim_id))
            contested.update(ADDRESS.findall(claim.fields.get("supported-by", "")))
    return contested, outcomes


def lint_contested(vault_root, note_file) -> list[Outcome]:
    vault, note = Path(vault_root), Path(note_file)
    contested, outcomes = _contested_addresses(vault)
    text = note.read_text()
    for claim in claims_mod.parse_claims(text):
        target, extra = _origin(vault, note, claim, "")
        for address in ADDRESS.findall(claim.fields.get("supported-by", "")):
            if address in contested:
                outcomes.append(
                    Outcome(
                        "contested",
                        address,
                        Result.UNMATCHED,
                        f"contested — {address} has standing counter-evidence",
                        extra=extra,
                    )
                )
    return _deduplicate(outcomes)


def lint_web_archive(vault_root) -> list[Outcome]:
    vault = Path(vault_root)
    outcomes = []
    literature = vault / "literatures"
    if not literature.is_dir():
        return outcomes
    for path in sorted(literature.glob("*.md")):
        rel = _relative(vault, path)
        data, parsed = _parse_frontmatter(path.read_text())
        if not parsed:
            outcomes.append(_schema_outcome("web-archive", rel))
            continue
        if data.get("url") and not data.get("doi") and not data.get("archive-url"):
            target = (
                data.get("citekey") if isinstance(data.get("citekey"), str) else rel
            )
            outcomes.append(
                Outcome(
                    "web-archive",
                    target,
                    Result.UNMATCHED,
                    "missing-archive — web source has no archive-url",
                )
            )
    return _deduplicate(outcomes)
