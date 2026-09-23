"""The current-state surfaces describe the tree as it is.

Four mechanisms. Three are the residue of a hand sweep (2026-09-16) that found
the same defect class over and over: a path a reader cannot open, a name for a
mechanism that no longer exists, and a status marker for a workflow that is
gone. Records under ``docs/research/``, ``docs/product-landscape/`` and the
executed plans are dated accounts and are out of scope for those three; the
active specs, the agent references, the ADRs, the skills, the vault template
and the plugin manifests are what an agent reads as current, and they are in
scope. The fourth, the home-literal scan (#164), is not scoped to current
state at all: it alone runs over every tracked text file, dated accounts
included, because a leaked home-directory path is exposure wherever it sits.
"""

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _tracked(*globs: str, root: Path = ROOT) -> list[Path]:
    """Every tracked path matching `globs`, one `Path` per file. `-z` because
    `git ls-files` otherwise separates paths by newline and C-quotes a
    non-ASCII one (`core.quotePath`, default true): splitting that output on
    whitespace turns `a b.md` into two names and `café.md` into a literal that
    is not the path on disk, and the scans below skip a name that is not a
    file. The empty records `-z` leaves -- a trailing one always, and only
    that one when nothing is tracked -- would each become `root` itself."""
    out = subprocess.run(
        ["git", "ls-files", "-z", "--", *globs],
        cwd=root,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.split("\0")
    return sorted(root / p for p in out if p)


_DISPOSITION = re.compile(r"^Disposition: (\S+)", re.MULTILINE)


def _active_design_specs() -> list[str]:
    """Every tracked design spec whose header carries no `Disposition:` line:
    the active specs enter this scan by construction, the historical one and
    the `*-evidence.md` siblings stay out."""
    return [
        str(path.relative_to(ROOT))
        for path in _tracked("docs/superpowers/specs/*-design.md")
        if not _DISPOSITION.search(
            "\n".join(path.read_text(encoding="utf-8").splitlines()[:10])
        )
    ]


CURRENT_STATE_SURFACES = _tracked(
    "README.md",
    "CONTEXT.md",
    "AGENTS.md",
    "ATTRIBUTION.md",
    "docs/agents/*.md",
    "docs/adr/*.md",
    *_active_design_specs(),
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
            # `"" in "*{"` is True: a path that ends its line must still be
            # checked, so the glob/template hatch needs a character to read.
            if following and following in "*{":
                continue  # a glob or a template
            token = re.sub(r":\d+(?:[-–]\d+)?$", "", token)  # `path.py:12-34`
            token = token.split("#", 1)[0]
            if _PLACEHOLDER.search(token) or token.endswith("/*"):
                continue
            yield token


def test_a_path_that_ends_its_line_is_checked():
    """The end-of-line hole: `following` is empty there, and an empty string
    is a substring of every string."""
    assert list(_path_literals("see docs/agents/nowhere.md")) == [
        "docs/agents/nowhere.md"
    ]
    assert list(_path_literals("see docs/agents/nowhere.md and more")) == [
        "docs/agents/nowhere.md"
    ]
    assert list(_path_literals("glob docs/agents/*")) == []


def test_the_active_specs_are_derived_not_listed():
    """This spec's successor enters the scan without an edit; the historical
    spec and the evidence siblings stay out."""
    if not _tracked("docs/superpowers/specs/*-design.md"):
        pytest.skip(
            "no tracked spec: not the repository checkout (mutmut's mutants/ tree)"
        )
    specs = _active_design_specs()
    assert "docs/superpowers/specs/2026-09-17-pre-lane-2-design.md" in specs
    assert "docs/superpowers/specs/2026-09-05-assembly-design.md" in specs
    assert not any("evidence" in spec for spec in specs)
    assert not any("2026-09-01-canonical" in spec for spec in specs)


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
# surface it asserts something the tree contradicts. The deny-list has one
# writer: the retired-spellings table in docs/agents/terminology.md §5, read
# here, one regular expression per row.
_TERMINOLOGY = ROOT / "docs" / "agents" / "terminology.md"
_RETIRED_HEADING = "## 5. Retired spellings"
_RETIRED_ROW = re.compile(r"^\|\s*`(?P<pattern>[^`]+)`\s*\|")


def _retired_rows() -> list[tuple[str, str]]:
    """`(pattern, line)` for every row of the retired-spellings table; the
    line is kept so the table's own rows can be exempted from the scan."""
    lines = _TERMINOLOGY.read_text(encoding="utf-8").splitlines()
    start = lines.index(_RETIRED_HEADING)
    rows = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        match = _RETIRED_ROW.match(line)
        if match:
            rows.append((match.group("pattern").replace("\\|", "|"), line))
    return rows


RETIRED = [pattern for pattern, _line in _retired_rows()]
_RETIRED = [re.compile(pattern) for pattern in RETIRED]
_RETIRED_TABLE_LINES = {line for _pattern, line in _retired_rows()}
# A glossary line that names a spelling in order to forbid it is not a use.
_FORBIDDING_LINE = re.compile(r"_Avoid_|Declined anchor|stale names|not aliases")


def test_the_retired_table_is_the_deny_list():
    """Fifteen rows on 2026-09-17; every pattern compiles; the pipe inside a
    code span is written `\\|` in the table and read back as `|`."""
    assert len(RETIRED) >= 15, RETIRED
    assert r"\b[Aa]dmission is (?:a|the) human act" in RETIRED
    assert all(isinstance(pattern, re.Pattern) for pattern in _RETIRED)


@pytest.mark.parametrize("path", PROSE_SURFACES, ids=_ids)
def test_no_retired_vocabulary(path):
    hits = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line in _RETIRED_TABLE_LINES or _FORBIDDING_LINE.search(line):
            continue
        hits.extend(
            f"{number}: {pattern.pattern} — {line.strip()[:100]}"
            for pattern in _RETIRED
            if pattern.search(line)
        )
    assert hits == [], (
        f"{path.relative_to(ROOT)} uses retired vocabulary:\n" + "\n".join(hits)
    )


@pytest.mark.parametrize("path", _tracked("*.md", "**/*.md"), ids=_ids)
def test_disposition_marker_is_historical_or_superseded(path):
    """The marker system is gone; a header may say a record is history, or name
    what superseded it, and nothing else — `pending-*` and `current` named a
    workflow that no longer runs. Runs over every tracked Markdown file, which
    the retired-vocabulary scan does not: this guards a header grammar."""
    values = _DISPOSITION.findall(path.read_text(encoding="utf-8"))
    bad = [v for v in values if v.rstrip(":") not in {"historical", "superseded-by"}]
    assert bad == [], f"{path.relative_to(ROOT)}: Disposition {bad}"


# A path under a user's home directory is a machine-local fact (AGENTS.md:
# environment facts are not written down); in a public repository it is also
# the author's. `~/…` or `$HOME/…` spell the same path without the name.
_HOME_LITERAL = re.compile(r"/home/[A-Za-z][A-Za-z0-9._-]*")
# The same fact, spelled the Windows way, natively (`C:\Users\<user>\…`) or
# through a WSL mount (`/mnt/c/Users/<user>/…`); `C:\Users\<user>\…` or `/mnt/
# c/Users/<user>/…` is the spelling that carries the same information without
# the name. Case-insensitive, because a Windows path is: `c:\users\<user>` is
# one path with the two above and is what a WSL user's shell history prints.
# Anchored to a drive letter or an `/mnt/<letter>` mount so a bare macOS
# `/Users/<name>` — not a machine-local fact about this repository, and seen
# only inside verbatim quotes of licensed third-party docs — is not scanned;
# that gap is deliberate, not an oversight. The UNC spelling of the same home
# (`\\wsl$\<distro>\home\<user>`) is not matched either: no drive letter, no
# mount point, and a backslash separator the POSIX pattern below cannot read.
_WINDOWS_HOME_LITERAL = re.compile(
    r"(?:[A-Za-z]:|/mnt/[a-z])[/\\]Users[/\\][A-Za-z][A-Za-z0-9._-]*", re.IGNORECASE
)


def test_no_home_directory_literal():
    """#164 (assembly spec §12, precondition 3): no tracked text file names a
    directory under `/home/<user>` or a Windows/WSL `Users/<user>`; POSIX and
    Windows spell the same machine-local fact, so both are scanned — the
    Windows one in any case, the POSIX one exactly, each as its own filesystem
    reads a path. Every tracked text file, dated records included, and `-z`
    above is what makes "every" true of a name with a space or a non-ASCII
    character. A placeholder in angle brackets is not a name, and `~` or
    `C:\\Users\\<user>\\…` is the spelling that carries the same information."""
    hits = []
    for path in _tracked("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # a binary fixture
        for number, line in enumerate(text.splitlines(), 1):
            hits.extend(
                f"{path.relative_to(ROOT)}:{number}: {pattern.pattern} — {line.strip()[:100]}"
                for pattern in (_HOME_LITERAL, _WINDOWS_HOME_LITERAL)
                if pattern.search(line)
            )
    assert hits == [], "\n".join(hits)


def test_the_tracked_scan_reads_every_tracked_name(tmp_path):
    """`_tracked` feeds the home-literal scan, whose `is_file()` guard skips
    anything that is not a real path. Splitting `git ls-files` on whitespace
    loses two kinds of name silently: a path with a space becomes two
    fragments, and a non-ASCII path is C-quoted under the default
    `core.quotePath`, so the literal is not the path on disk. Either way the
    file is never opened and a home-directory literal inside it ships. `-z`
    emits one NUL-separated path per file and suppresses the quoting."""
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "docs" / "my notes.md").write_text("x\n", encoding="utf-8")
    (repo / "docs" / "café.md").write_text("y\n", encoding="utf-8")

    def git(*argv: str) -> None:
        subprocess.run(["git", *argv], cwd=repo, check=True, capture_output=True)

    git("init", "-q")
    git("config", "core.quotePath", "true")  # the default, pinned
    git("add", "-A")

    tracked = _tracked("*", root=repo)

    assert tracked == sorted([repo / "docs" / "café.md", repo / "docs" / "my notes.md"])
    assert all(path.is_file() for path in tracked)


# Spelled in fragments: this file is itself a tracked text file, so
# `test_no_home_directory_literal` scans it and a fixture written whole would
# be a hit against the very pattern it pins.
_LOWERCASE_DRIVE = "c:" + r"\users" + r"\eranr"
_UPPERCASE_MOUNT = "/MNT" + "/C/USERS/eranr"


def test_the_windows_home_literal_ignores_case():
    """A Windows path is case-insensitive, and `c:\\users\\<user>` is the
    spelling a WSL user's shell history produces — the drive-letter pattern
    has to read it. The POSIX `/home/<user>` is a case-sensitive path and
    stays case-sensitive; a bare `/Users/<name>` stays out (the macOS gap the
    comment above the patterns records)."""
    assert _WINDOWS_HOME_LITERAL.search(_LOWERCASE_DRIVE)
    assert _WINDOWS_HOME_LITERAL.search(_UPPERCASE_MOUNT)
    assert _WINDOWS_HOME_LITERAL.search("C:" + r"\Users" + r"\eranr")
    assert not _HOME_LITERAL.search("/HOME/eranr")
    assert not _WINDOWS_HOME_LITERAL.search("/Users/eranr")
