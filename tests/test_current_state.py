"""The current-state surfaces describe the tree as it is.

Three mechanisms, each the residue of a hand sweep (2026-09-16) that found the
same defect class over and over: a path a reader cannot open, a name for a
mechanism that no longer exists, and a status marker for a workflow that is
gone. Records under ``docs/research/``, ``docs/product-landscape/`` and the
executed plans are dated accounts and are out of scope here; the active specs,
the agent references, the ADRs, the skills, the vault template and the plugin
manifests are what an agent reads as current, and they are in scope.
"""

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _tracked(*globs: str) -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "--", *globs],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.split()
    return sorted(ROOT / p for p in out)


CURRENT_STATE_SURFACES = _tracked(
    "README.md",
    "CONTEXT.md",
    "AGENTS.md",
    "ATTRIBUTION.md",
    "docs/agents/*.md",
    "docs/adr/*.md",
    "docs/superpowers/specs/2026-09-05-assembly-design.md",
    "docs/superpowers/specs/2026-09-06-import-redesign-design.md",
    "skills/*/SKILL.md",
    "research_vault/templates/vault/**/*.md",
    ".claude-plugin/*.json",
    ".out-of-scope/*.md",
    "pyproject.toml",
    ".github/workflows/quality.yml",
)

_ids = lambda p: str(p.relative_to(ROOT))  # noqa: E731

# The specs narrate what they retired, by name; the scan for retired names
# covers the surfaces that state the present without that history.
PROSE_SURFACES = [
    p for p in CURRENT_STATE_SURFACES if "superpowers/specs" not in str(p)
]

# A repository path a reader could try to open. Vault-relative paths
# (`system/…`, `inbox/…`) are not repository paths and are not matched.
_REPO_PATH = re.compile(
    r"(?<![\w./-])((?:docs|research_vault|skills|tests|scripts|hooks|\.github|\.claude-plugin|\.out-of-scope)/[A-Za-z0-9_./-]*[A-Za-z0-9_/-])"
)
_PLACEHOLDER = re.compile(r"[<>*{}…]|\bN\b|\.\.\.")
# A line that says a path is gone, or names a file in another repository, or
# a file this spec schedules but has not created, is not a dangling pointer.
_NOT_A_POINTER = re.compile(
    r"deleted|removed|retired|retires|\bgoes\b|gone|went with|no longer|claude-obsidian|the tool's|K-Dense|upstream|not yet|to be created|planned"
)


def _path_literals(text: str):
    for line in text.splitlines():
        if _NOT_A_POINTER.search(line):
            continue
        for match in _REPO_PATH.finditer(line):
            token = match.group(1)
            following = line[match.end() : match.end() + 1]
            if following in "*{":
                continue  # a glob or a template
            token = re.sub(r":\d+(?:[-–]\d+)?$", "", token)  # `path.py:12-34`
            token = token.split("#", 1)[0]
            if _PLACEHOLDER.search(token) or token.endswith("/*"):
                continue
            yield token


@pytest.mark.parametrize("path", CURRENT_STATE_SURFACES, ids=_ids)
def test_no_dangling_repository_path(path):
    text = path.read_text(encoding="utf-8")
    missing = sorted(
        {
            token
            for token in _path_literals(text)
            if not (ROOT / token).exists() and not (path.parent / token).exists()
        }
    )
    assert missing == [], (
        f"{path.relative_to(ROOT)} names paths that do not exist: {missing}"
    )


# Names of mechanisms the ingest redesign retired (2026-09), or of the product
# before its rename. Each survives only in dated records; on a current-state
# surface it asserts something the tree contradicts. Exact identifiers that
# legitimately survive (`not-admitted` the reason code, `managed-region` the
# check target kind) do not match these shapes.
RETIRED = [
    r"synthesis/",
    r"\bfixity-sha256\b",
    r"knowledge-harness",
    r"\.harness/",
    r"\bHARNESS_",
    r"\bhk-[a-z]",
    r"\bmanaged region",
    r"\bfree region",
    r"\b[Aa]dmission is (?:a|the) human act",
    r"\b[Aa]dmitted (?:through|into|to) Zotero",
    r"\bcitekey:",
    r"\bimport-source\b",
    r"\bscreening-state\b",
    r"\bLiterature screening states\b",
    r"\brename log\b",
]
_RETIRED = [re.compile(p) for p in RETIRED]
# A glossary line that names a spelling in order to forbid it is not a use.
_FORBIDDING_LINE = re.compile(r"_Avoid_|Declined anchor|stale names|not aliases")


@pytest.mark.parametrize("path", PROSE_SURFACES, ids=_ids)
def test_no_retired_vocabulary(path):
    hits = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if _FORBIDDING_LINE.search(line):
            continue
        for pattern in _RETIRED:
            if pattern.search(line):
                hits.append(f"{number}: {pattern.pattern} — {line.strip()[:100]}")
    assert hits == [], (
        f"{path.relative_to(ROOT)} uses retired vocabulary:\n" + "\n".join(hits)
    )


_DISPOSITION = re.compile(r"^Disposition: (\S+)", re.M)


@pytest.mark.parametrize("path", _tracked("*.md", "**/*.md"), ids=_ids)
def test_disposition_marker_is_historical_or_superseded(path):
    """The marker system is gone; a header may say a record is history, or name
    what superseded it, and nothing else — `pending-*` and `current` named a
    workflow that no longer runs."""
    values = _DISPOSITION.findall(path.read_text(encoding="utf-8"))
    bad = [v for v in values if v.rstrip(":") not in {"historical", "superseded-by"}]
    assert bad == [], f"{path.relative_to(ROOT)}: Disposition {bad}"
