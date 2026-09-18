"""Config surfaces that currently fail SILENTLY, made to fail loudly in CI.

Three classes of silent failure live here, all of the same shape — a file the
plugin loader or a human reader trusts, which nothing mechanically checks:

* a malformed ``hooks.json`` or plugin manifest is swallowed at plugin load;
* a typo'd ``SKILL.md`` frontmatter key is swallowed the same way;
* an identifier coined in code but never given a row in ``docs/agents/terminology.md``
  §4.4 stays ungoverned until somebody happens to run a naming audit.

The JSON half doubles as the *formatter*: ``json.tool``'s canonical form is
asserted here rather than run as a separate hook, so the one-form-owner matrix
gains a JSON owner with zero new dependencies (docs/research/rethink-audits/2026-08-21-lint-format-rethink.md).
"""

import ast
import json
import os
import pwd
import re
import shlex
import shutil
import socket
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
import yaml

from research_vault import frontmatter, inbox
from tests.conftest import (
    GIT_HOME_OVERRIDES,
    OFFLINE_GIT_IDENTITY,
    _home_env,
    _make_home,
    is_production_base,
    package_ast,
)

ROOT = Path(__file__).resolve().parents[1]

# The repo's own JSON manifests, and only those. Deliberately NOT globbed:
# `docs/research/` JSON is source material outside this formatter's managed surface,
# `.vscode/*.json` is JSONC — a dialect VS Code owns — and a vault's
# `system/bibliography.json` is capture-written, outside every repo formatter.
JSON_MANIFESTS = [
    "hooks/hooks.json",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    "research_vault/templates/research-vault/machine.json.example",
]

TOML_FILES = ["pyproject.toml"]

SKILL_FILES = sorted(ROOT.glob("skills/*/SKILL.md"))


def _canonical(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


@pytest.mark.parametrize("relative", JSON_MANIFESTS)
def test_json_manifest_parses(relative):
    """A manifest the plugin loader cannot parse fails at load with no message."""
    path = ROOT / relative
    assert path.is_file(), f"{relative} is missing"
    json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("relative", JSON_MANIFESTS)
def test_json_manifest_is_in_canonical_form(relative):
    """JSON's form owner is stdlib ``json.tool``; this assertion IS the check."""
    path = ROOT / relative
    raw = path.read_text(encoding="utf-8")
    assert raw == _canonical(json.loads(raw)), (
        f"{relative} is not in canonical JSON form. Fix it with:\n"
        f"    python -m json.tool --indent 2 --no-ensure-ascii "
        f"{relative} {relative}"
    )


@pytest.mark.parametrize("relative", TOML_FILES)
def test_toml_parses(relative):
    path = ROOT / relative
    assert path.is_file(), f"{relative} is missing"
    with path.open("rb") as handle:
        tomllib.load(handle)


def test_pyproject_pins_the_tools_the_seam_runs():
    """The seam's promise is a PINNED toolchain: an unpinned row breaks it."""
    with (ROOT / "pyproject.toml").open("rb") as handle:
        data = tomllib.load(handle)
    dev = data["project"]["optional-dependencies"]["dev"]
    pinned = {row.split("==")[0] for row in dev if "==" in row}
    for tool in (
        "ruff",
        "mypy",
        "mdformat",
        "yamlfix",
        "pyproject-fmt",
        "pre-commit",
        "pytest",
    ):
        assert tool in pinned, f"{tool} must be pinned with == in the dev extra"


# --------------------------------------------------------------------------
# Identifier governance (terminology.md §4.4) — mechanical, not an audit.
# --------------------------------------------------------------------------


def _governance_row(group: str) -> str:
    # Padding-tolerant by construction: mdformat owns docs/ and pads table cells to
    # align columns, so an exact-prefix match would break on the next reflow.
    prefix = re.compile(rf"\|\s*{re.escape(group)}\s*\|")
    rows = [
        line
        for line in (ROOT / "docs/agents/terminology.md")
        .read_text(encoding="utf-8")
        .splitlines()
        if prefix.match(line)
    ]
    assert len(rows) == 1, f"terminology.md §4.4 must carry exactly one '{group}' row"
    return rows[0]


def _backticked(row: str) -> set[str]:
    return set(re.findall(r"`([^`]+)`", row))


def _probe_ids() -> set[str]:
    """Every doctor probe id the code can emit, read off scaffold.py's AST.

    Probe ids are literals at their construction sites rather than a registry
    constant, so the AST is the only honest source; a grep would also match
    prose in docstrings.
    """
    tree = package_ast(ROOT / "research_vault/scaffold.py")
    return {
        node.args[0].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and getattr(node.func, "id", None) == "Probe"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
    }


def test_every_check_id_at_head_is_governed():
    """A check id coined in code with no §4.4 row is an ungoverned identifier."""
    ungoverned = sorted(
        _backticked(_governance_row("check ids")).symmetric_difference(inbox.CHECK_IDS)
        & inbox.CHECK_IDS
    )
    assert not ungoverned, (
        "check ids in CHECK_IDS with no backticked entry in terminology.md §4.4: "
        f"{ungoverned}"
    )


def test_every_doctor_probe_id_at_head_is_governed():
    probes = _probe_ids()
    assert probes, "AST scan found no Probe ids — the scan itself is broken"
    governed = _backticked(_governance_row("doctor probe ids"))
    ungoverned = sorted(probes - governed)
    assert not ungoverned, (
        "doctor probe ids emitted by scaffold.py with no backticked entry in "
        f"terminology.md §4.4: {ungoverned}"
    )
    stale = sorted(governed - probes)
    assert not stale, (
        "doctor probe ids in terminology.md §4.4 with no matching Probe(...) in "
        f"scaffold.py: {stale} — remove the row entry, the probe was deleted"
    )


def test_every_reason_code_at_head_is_governed():
    """The largest identifier group, enforced the same way as the other two.

    The row's own Status cell -- "additions require a reference row" -- promises
    every code a row, so a code that lands with no row must fail here rather
    than leave the suite green. Reason codes go verbatim onto
    ``inbox/review-queue.md``, the highest-traffic human surface in the system;
    it is the last group that should be governed more loosely than the rest.
    """
    row = _governance_row("reason codes")
    ungoverned = sorted(inbox.REASON_CODES - _backticked(row))
    assert not ungoverned, (
        "reason codes in inbox.REASON_CODES with no backticked entry in "
        f"terminology.md §4.4: {ungoverned}. Its Status cell promises "
        "'additions require a reference row' -- add the row."
    )


def test_reason_codes_row_still_names_the_authoritative_registry():
    """Enumeration is the parity check; the delegation is still the ownership claim."""
    assert "REASON_CODES" in _governance_row("reason codes")
    assert inbox.REASON_CODES, "the reason-code registry must not be empty"


# --------------------------------------------------------------------------
# Skill frontmatter — the hooks.json failure class, one surface over.
# --------------------------------------------------------------------------


def test_skill_files_exist():
    assert SKILL_FILES, "no skills/*/SKILL.md found — the glob is wrong"


def _raw_frontmatter_lines(skill_md: Path) -> list[str]:
    text = skill_md.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{skill_md} does not open with a --- fence"
    closing = text.index("\n---", len("---\n"))
    return text[len("---\n") : closing + 1].splitlines()


@pytest.mark.parametrize("skill_md", SKILL_FILES, ids=lambda p: p.parent.name)
def test_skill_frontmatter_matches_the_plugin_contract(skill_md):
    """Dogfood the core's own tokenizer on real files; zero new dependencies."""
    data, _body = frontmatter.parse(skill_md.read_text(encoding="utf-8"))
    assert data, f"{skill_md.parent.name}/SKILL.md has no frontmatter block"
    assert data.get("name") == skill_md.parent.name, (
        f"{skill_md.parent.name}/SKILL.md declares name={data.get('name')!r}; "
        "the plugin contract requires it to equal the skill directory name"
    )
    description = data.get("description")
    assert isinstance(description, str), (
        f"{skill_md.parent.name}/SKILL.md needs a description"
    )
    assert description.strip(), (
        f"{skill_md.parent.name}/SKILL.md needs a NONEMPTY description"
    )


@pytest.mark.parametrize("skill_md", SKILL_FILES, ids=lambda p: p.parent.name)
def test_skill_disable_model_invocation_is_a_yaml_boolean_literal(skill_md):
    """Asserted against the RAW line, deliberately, not the parsed value.

    ``frontmatter.parse`` is the VAULT-dialect tokenizer: a flat quoted-string
    schema (spec §5) that yields ``'true'`` for ``true`` and for ``"true"``
    alike, and never a bool. The plugin loader, by contrast, reads this file as
    real YAML — so ``"true"``, ``yes``, ``1`` and ``True`` are all silent
    mis-reads that the tokenizer physically cannot distinguish. Checking the raw
    line is therefore the STRONGER assertion, not a concession: it catches every
    one of those, which an ``isinstance(..., bool)`` on the parsed value cannot.
    """
    for line in _raw_frontmatter_lines(skill_md):
        key, _, value = line.partition(":")
        if key.strip() == "disable-model-invocation":
            assert value.strip() in {"true", "false"}, (
                f"{skill_md.parent.name}/SKILL.md: disable-model-invocation must be "
                f"the unquoted YAML boolean `true` or `false`, got {value.strip()!r}"
            )


def test_repo_python_is_the_version_the_pins_were_measured_against():
    """A guard, not a gate: the pinned toolchain's behaviour is version-bound."""
    assert sys.version_info >= (3, 11), "pyproject requires-python is >=3.11"


# --------------------------------------------------------------------------
# pyproject-fmt round-trip losslessness.
#
# Measured 2026-08-22 against the REAL pyproject.toml (a synthetic fragment
# shows none of this): bare pyproject-fmt truncated pins (`mdformat==1.0.0` to
# `==1`), invented a classifiers block claiming Python 3.14, and — the dangerous
# one — alpha-sorted the dependency list while hoisting a ruling comment's
# continuation lines onto a DIFFERENT package, so a recorded ruling silently
# described the wrong dependency.
#
# The flags below fix that. These tests are what stop the fix from being a
# remembered rule: a future pyproject-fmt that drops --keep-full-version, or that
# relocates a comment block, fails here instead of quietly making a recorded
# ruling false. The association tests assert PLACEMENT, not presence — the
# measured failure preserved every comment character while attaching it to the
# wrong key, so a "the string is still there" check would have passed it.
# --------------------------------------------------------------------------

PYPROJECT_FMT_FLAGS = [
    "--keep-full-version",
    "--no-generate-python-version-classifiers",
    "--table-format",
    "long",
]

# Ruling comment -> the setting it rules. The anchor must still appear within the
# two significant (non-comment, non-blank) lines following the comment block,
# which allows for a `[table.header]` line sitting between a block and its key.
RULING_ANCHORS = [
    ("A floor, not a pin", "requires = ["),
    ("Single-sourced from research_vault.__version__", "dynamic = ["),
    ("Lazy-imported at research_vault's single parse site", '"defusedxml==0.7.1"'),
    ("A floor by design", "pdf = ["),
    ("FORMAT + RENDER-CONTRACT pin", '"mdformat==1.0.0"'),
    ("never in addopts", '"pytest-xdist==3.8.0"'),
    ("Dev-lane instrument, read-only posture", '"pyzotero[cli]==1.14.0"'),
    ("ruff 0.16 formats Python fences", "extend-exclude = ["),
    ("Bandit idiom exclusions", "extend-select = ["),
    ("ARG in tests only", '"tests/*" = ['),
    ("PTH off in gitstate ONLY", '"research_vault/gitstate.py" = ['),
    ("Test side of the same ruling", '"tests/test_gitstate.py" = ['),
    ("print IS the CLI output contract", '"research_vault/__main__.py" = ['),
    ("Gate scripts report via stdout", '"scripts/*" = ['),
    ("competes with the CRAP ceiling", "max-complexity = 28"),
    ("Ratchet: disallow_incomplete_defs", "[tool.mypy]"),
    ("pypdf: optional [pdf] extra", 'module = "pypdf.*"'),
    ("defusedxml ships no py.typed", 'module = "defusedxml.*"'),
]

_FIX = (
    "Re-run the form owner exactly as the hook does:\n"
    "    pyproject-fmt " + " ".join(PYPROJECT_FMT_FLAGS) + " pyproject.toml\n"
    "If that does NOT restore the property, the pinned pyproject-fmt has changed "
    "behaviour. Do not loosen this test: re-measure against the real file (the "
    "mistake this guard exists to prevent was measuring a proxy), then either find "
    "the flag that restores losslessness or retire the hook and record why."
)


def _round_tripped_pyproject(tmp_path) -> str:
    """Run the pinned pyproject-fmt over a COPY; never touch the real file.

    Working on a copy is what lets this pass with a dirty tree and keeps the suite
    from mutating repo state as a side effect of asserting about it.
    """
    binary = Path(sys.executable).parent / "pyproject-fmt"
    if not binary.exists():
        located = shutil.which("pyproject-fmt")
        assert located, "pyproject-fmt is not installed; install the [dev] extra"
        binary = Path(located)
    scratch = tmp_path / "pyproject.toml"
    shutil.copyfile(ROOT / "pyproject.toml", scratch)
    result = subprocess.run(
        [str(binary), *PYPROJECT_FMT_FLAGS, str(scratch)],
        capture_output=True,
        text=True,
        check=False,
    )
    # 0 = already canonical, 1 = rewritten. Anything else is a tool failure.
    assert result.returncode in (0, 1), (
        f"pyproject-fmt exited {result.returncode}\n{result.stderr}"
    )
    return scratch.read_text(encoding="utf-8")


def _requirements(text: str) -> set[str]:
    data = tomllib.loads(text)
    rows = set(data["project"].get("dependencies", []))
    for group in data["project"].get("optional-dependencies", {}).values():
        rows.update(group)
    return rows


def _significant_lines_after(text: str, marker: str, count: int) -> list[str]:
    lines = text.splitlines()
    index = next(i for i, line in enumerate(lines) if marker in line)
    found = []
    for line in lines[index:]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        found.append(stripped)
        if len(found) == count:
            break
    return found


def test_pyproject_fmt_flags_match_the_hook_the_seam_actually_runs():
    """A test guarding a different flag set than the hook guards nothing.

    The coupling is enforced here rather than left to a comment on both sides.
    """
    config = (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    start = config.index("- id: pyproject-fmt")
    entry = config[start : config.index("- id: ", start + 1)]
    assert set(re.findall(r"--[a-z-]+", entry)) == {
        flag for flag in PYPROJECT_FMT_FLAGS if flag.startswith("--")
    }, (
        "the pyproject-fmt flags in .pre-commit-config.yaml and the flags this file "
        "round-trips with have drifted apart; make them identical again"
    )
    assert "--table-format long" in " ".join(entry.split())


def test_pyproject_fmt_round_trip_preserves_every_pin_spelling(tmp_path):
    """`mdformat==1.0.0` must never come back as `==1`.

    PEP 440 treats those as equivalent, which is precisely what makes the rewrite
    dangerous: the recorded pin is the artifact, and a silently loosened one still
    resolves today and has stopped being a pin tomorrow.
    """
    before = _requirements((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    after = _requirements(_round_tripped_pyproject(tmp_path))
    assert before == after, (
        "pyproject-fmt changed dependency spellings.\n"
        f"  lost:   {sorted(before - after)}\n"
        f"  gained: {sorted(after - before)}\n" + _FIX
    )


def test_pyproject_fmt_round_trip_invents_no_classifiers(tmp_path):
    """Bare pyproject-fmt asserts support through Python 3.14. Nothing tests that."""
    formatted = tomllib.loads(_round_tripped_pyproject(tmp_path))
    assert "classifiers" not in formatted["project"], (
        "pyproject-fmt generated a classifiers block this project never declared "
        "and does not test.\n" + _FIX
    )


@pytest.mark.parametrize(
    ("marker", "anchor"), RULING_ANCHORS, ids=[anchor for _, anchor in RULING_ANCHORS]
)
def test_every_ruling_comment_sits_on_the_setting_it_rules(marker, anchor):
    """The rulings are attached correctly in the file as committed."""
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert marker in text, f"the ruling comment {marker!r} has gone missing"
    following = _significant_lines_after(text, marker, 2)
    assert any(anchor in line for line in following), (
        f"the ruling comment {marker!r} no longer sits above {anchor!r}; it now "
        f"precedes {following!r}. A comment describing a different setting than the "
        "one it sits on is a false record."
    )


@pytest.mark.parametrize(
    ("marker", "anchor"), RULING_ANCHORS, ids=[anchor for _, anchor in RULING_ANCHORS]
)
def test_pyproject_fmt_round_trip_keeps_rulings_on_their_setting(
    marker, anchor, tmp_path
):
    """...and a round-trip must not move them onto a different one.

    This is the exact defect measured on 2026-08-22: every character of the
    pyzotero ruling survived the format, attached to `mdformat`.
    """
    following = _significant_lines_after(_round_tripped_pyproject(tmp_path), marker, 2)
    assert any(anchor in line for line in following), (
        f"a pyproject-fmt round-trip moved the ruling comment {marker!r} away from "
        f"{anchor!r}; it now precedes {following!r}. The comment TEXT survived, so "
        "only this placement check catches it.\n" + _FIX
    )


# --------------------------------------------------------------------------
# mdformat table-cell truncation
# --------------------------------------------------------------------------

# The mdformat-owned CommonMark set, matching .pre-commit-config.yaml's hook:
# every tracked Markdown file except the explicitly excluded ephemeral workspaces
# and the vault index, whose Obsidian dialect mdformat corrupts on contact (#70).
_MDFORMAT_EXCLUDED_FILES = ("research_vault/templates/vault/index.md",)
_MDFORMAT_EXCLUDED_DIRS = (".superpowers", ".worktrees", ".claude/worktrees")


def _mdformat_owned_markdown() -> list[Path]:
    root = Path(__file__).resolve().parent.parent
    excluded_files = {root / entry for entry in _MDFORMAT_EXCLUDED_FILES}
    excluded_dirs = tuple(root / entry for entry in _MDFORMAT_EXCLUDED_DIRS)
    files: list[Path] = []
    tracked = subprocess.run(
        ["git", "ls-files", "--", "*.md"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    for entry in tracked.stdout.splitlines():
        candidate = root / entry
        if candidate in excluded_files:
            continue
        if any(
            candidate == excluded_dir or excluded_dir in candidate.parents
            for excluded_dir in excluded_dirs
        ):
            continue
        files.append(candidate)
    return files


# Every top-level token after the fixed prefix must be either a literal path
# or a `$(find ...)` substitution -- never another flag. `find`'s OWN flags
# (-name, -not, -path...) live safely inside a `$(...)` block, matched here
# as one atomic token, so they never reach this check.
_MDFORMAT_TOP_LEVEL_TOKEN = re.compile(r"\$\([^)]*\)|\S+")


def _resolved_paths_for_mdformat_entry(entry: str) -> set[Path]:
    """Given a raw pre-commit `entry:` value for the mdformat hook, resolve
    it to the file set it would actually touch -- mdformat swapped for a
    line-per-path printer, then the resulting shell command actually
    EXECUTED (real `find ... -not -path` clauses against the live
    filesystem), rather than re-parsed as text. A stray token between the
    fixed prefix and the path list -- e.g. an inserted `--check`, which
    would defang the hook into report-only mode without changing which
    files it NAMES -- fails loudly here instead of being silently treated
    as a nonexistent path and dropped: a file-set-only comparison downstream
    cannot see a defanged hook, since --check does not change the file set,
    only what mdformat DOES with it.
    """
    command = shlex.split(entry)
    assert command[:2] == ["bash", "-c"], (
        "mdformat hook's entry has changed shape; update this parse"
    )
    inner = command[2]
    prefix = "mdformat --number --wrap keep "
    assert inner.startswith(prefix), (
        "mdformat hook's fixed flags changed; update this parse "
        "(add the new flag to `prefix` above once it is deliberate)"
    )
    remainder = inner[len(prefix) :]
    for token in _MDFORMAT_TOP_LEVEL_TOKEN.findall(remainder):
        if token.startswith("-") and not token.startswith("$("):
            raise AssertionError(
                f"unrecognized flag {token!r} between mdformat's fixed prefix "
                "and its path list. This parser only understands paths and "
                "$(find ...) substitutions there -- a real flag insertion "
                "must fail loudly, not be silently dropped as a "
                "nonexistent path."
            )
    printer = 'printf "%s\\n" ' + remainder
    result = subprocess.run(
        ["bash", "-c", printer], cwd=ROOT, capture_output=True, text=True, check=True
    )
    resolved: set[Path] = set()
    for line in result.stdout.splitlines():
        if not line:
            continue
        target = ROOT / line
        if target.is_file():
            resolved.add(target)
        elif target.is_dir():
            resolved.update(target.rglob("*.md"))
    return resolved


def _resolved_mdformat_hook_paths() -> set[Path]:
    """The real mdformat hook's entry, resolved. Parsed via PyYAML (a hard
    transitive dependency of the pinned `pre-commit` dev tool, the same
    library pre-commit itself uses to read this exact file) rather than a
    text slice, so a multi-line folded scalar round-trips into one
    shell-safe line the way pre-commit itself would run it -- this cannot
    drift from what the hook actually RUNS; only from what it actually
    RESOLVES TO, which is the thing a mirror needs to match.
    """
    config = yaml.safe_load(
        (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    )
    (hook,) = (h for h in config["repos"][0]["hooks"] if h["id"] == "mdformat")
    return _resolved_paths_for_mdformat_entry(hook["entry"])


def test_mdformat_roots_mirror_the_hook_the_seam_actually_runs():
    """_mdformat_owned_markdown()'s independent reimplementation and the
    hook's OWN shell logic, actually executed, must resolve to the same file
    set -- nothing else checked that the mirror stayed true, the exact
    defect this task exists to close."""
    hook_files = _resolved_mdformat_hook_paths()
    mirror_files = set(_mdformat_owned_markdown())
    assert hook_files == mirror_files, (
        "the mdformat hook's actual resolved file set and this file's "
        "_mdformat_owned_markdown() mirror have drifted apart.\n"
        f"  hook only:   {sorted(p.relative_to(ROOT) for p in hook_files - mirror_files)}\n"
        f"  mirror only: {sorted(p.relative_to(ROOT) for p in mirror_files - hook_files)}"
    )


def test_mdformat_hook_parser_rejects_a_flag_inserted_before_the_path_list():
    """Pin: a flag inserted between the fixed prefix and the path list --
    e.g. `--check`, which turns mdformat into report-only mode without
    changing which files it names -- must fail loudly, not be silently
    dropped as a nonexistent path. This is the exact blind spot a
    file-set-only comparison has: --check changes BEHAVIOUR, not the
    resolved file set, so nothing downstream of a silent drop could ever
    catch it.
    """
    defanged = (
        "bash -c 'mdformat --number --wrap keep --check README.md AGENTS.md "
        "CONTEXT.md docs'"
    )
    with pytest.raises(AssertionError, match=r"--check"):
        _resolved_paths_for_mdformat_entry(defanged)


def test_mdformat_hook_parser_rejects_end_of_line_flag_before_the_path_list():
    """Same pin, a second flag shape: `--end-of-line lf` is two tokens, and
    the first one (`--end-of-line`) must be what trips the check."""
    defanged = (
        "bash -c 'mdformat --number --wrap keep --end-of-line lf README.md "
        "AGENTS.md CONTEXT.md docs'"
    )
    with pytest.raises(AssertionError, match=r"--end-of-line"):
        _resolved_paths_for_mdformat_entry(defanged)


def _escaped_backticks_in_row(line: str) -> bool:
    """True when a table row carries an escaped backtick.

    That is the damage signature, and it is NOT an odd backtick count: when a
    `|` inside a code span truncates the cell, the span's opening backtick is
    left orphaned and mdformat writes it back ESCAPED, which keeps the count
    even. Counting backticks therefore misses the very defect this guards --
    verified against the real damaged line before this check was written.
    """
    return line.lstrip().startswith("|") and "\\`" in line


@pytest.mark.parametrize("path", _mdformat_owned_markdown(), ids=lambda p: str(p.name))
def test_markdown_table_rows_have_no_truncated_code_spans(path):
    """A `|` inside an inline code span truncates its table cell, silently.

    Measured, not theoretical: the 2026-08-22 canonical-form churn ran mdformat
    over this set, and three rows of a since-retired spec's frontmatter table
    carried `status: unscreened | included | excluded | superseded`. GFM ends the
    cell at the first unescaped `|` REGARDLESS of the code span, so mdformat
    reformatted the truncated parse back out and the enum values plus an entire
    `superseded-by` clause were deleted.

    The fix is to escape the pipes as \\| inside the span; mdformat then
    round-trips the row unchanged, which is asserted by re-running it.
    """
    offenders = [
        (n, line)
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if _escaped_backticks_in_row(line)
    ]
    assert not offenders, (
        f"{path}: table row(s) carry an escaped backtick, the signature of a code "
        f"span truncated by an unescaped `|` in the cell. Escape the pipes as \\| "
        f"INSIDE the span and re-run mdformat.\n"
        + "\n".join(f"  line {n}: {line[:120]}" for n, line in offenders)
    )


def test_the_package_reads_one_date_clock():
    """A check takes its instant as an argument (decision 28); only clock.py reads today's date."""
    # The call shape, not one spelling: `now(tz=datetime.UTC).date()` is the
    # same reader.
    reads_today = re.compile(r"\.now\([^)]*\)\.date\(\)")
    offenders = sorted(
        path.name
        for path in (ROOT / "research_vault").glob("*.py")
        if reads_today.search(path.read_text(encoding="utf-8"))
        and path.name != "clock.py"
    )
    assert offenders == [], offenders


def test_fixture_substitutions_cannot_become_no_ops():
    """A bare str.replace on fixture text passes silently once a fixture edit removes its target."""
    import ast

    def fixture_shaped(node) -> bool:
        # A str or bytes literal with a line break, a `key: value` or an inline
        # field, or any f-string: the shapes fixture text takes.
        if isinstance(node, ast.JoinedStr):
            return True
        if not isinstance(node, ast.Constant):
            return False
        value = node.value
        if isinstance(value, bytes):
            return b"\n" in value or b": " in value or b"::" in value
        if isinstance(value, str):
            return "\n" in value or ": " in value or "::" in value
        return False

    offenders = [
        f"{name}:{node.lineno}"
        for name in (
            "conftest.py",
            "test_verify_cli.py",
            "test_lints.py",
            "test_events.py",
            "test_notes.py",
        )
        for node in ast.walk(
            ast.parse((ROOT / "tests" / name).read_text(encoding="utf-8"))
        )
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "replace"
            and node.args
            and fixture_shaped(node.args[0])
        )
    ]
    assert offenders == [], f"use must_replace for fixture substitutions: {offenders}"


@pytest.mark.parametrize(
    ("base", "production"),
    [
        ("http://localhost:23119", True),
        ("http://localhost:23119/", True),
        ("http://127.0.0.1:23119", True),
        ("http://[::1]:23119", True),
        ("HTTP://LOCALHOST:23119", True),
        ("http://localhost:23129", False),
        ("http://127.0.0.1:23129", False),
        ("http://zotero.example:23119", False),
    ],
)
def test_write_leg_guard_recognises_production_by_endpoint_not_string(base, production):
    """Review M8: the write leg's guard was string equality on
    ``zotero.DEFAULT_BASE``, so ``http://127.0.0.1:23119`` — the same
    production instance by another loopback spelling — walked through it.
    Host and port after ``urlsplit``, every loopback name alike."""
    assert is_production_base(base) is production


def test_offline_tests_cannot_open_a_tcp_connection(dead_base):
    """An unmarked test's connect raises the block's error, naming the address.

    Not an outage: the block is a ``RuntimeError`` so no transport's
    ``except OSError`` can dress a leak as a tidy UNREACHABLE. The one
    address ``dead_base`` handed out is let through and refused for real.
    Unmarked, deliberately: the block is decided by markers alone, so this
    runs — and must pass — under the live flags too.
    """
    # By base class and message, not identity: pytest loads the conftest as
    # `conftest`, `from tests.conftest import ...` loads a second copy.
    with (
        socket.socket() as sock,
        pytest.raises(
            RuntimeError, match=r"blocked in the offline suite: 127\.0\.0\.1:23119"
        ),
    ):
        sock.connect(("127.0.0.1", 23119))

    port = int(dead_base.rsplit(":", 1)[1])
    with socket.socket() as sock, pytest.raises(ConnectionRefusedError):
        sock.connect(("127.0.0.1", port))


def test_offline_tests_cannot_resolve_a_name_outside_loopback(dead_base):
    """An unmarked test's name lookup raises the block's error, naming the
    host: `urllib` resolves before it connects, so a leaked hostname would
    otherwise be a real DNS query here and a `gaierror` on a machine without
    DNS. Loopback, by name and by literal, still resolves; the one address
    `dead_base` handed out does too. Through `urlopen` the block is what
    comes back, not a URLError-dressed outage. Unmarked, deliberately: the
    block is decided by markers alone and holds under the live flags."""
    import urllib.request

    with pytest.raises(
        RuntimeError,
        match=r"name resolution blocked in the offline suite: example\.invalid:80",
    ):
        socket.getaddrinfo("example.invalid", 80)
    with pytest.raises(RuntimeError, match=r"blocked in the offline suite"):
        urllib.request.urlopen("http://example.invalid/", timeout=1)
    port = int(dead_base.rsplit(":", 1)[1])
    for host in ("localhost", "127.0.0.1", "::1", None):
        assert socket.getaddrinfo(host, port)
    assert socket.getaddrinfo("127.0.0.1", 23119)


def test_a_home_of_the_suites_own_removes_what_outranks_its_gitconfig(
    tmp_path, monkeypatch
):
    """`_make_home` names, beside the entries to set, every variable that
    would outrank the `.gitconfig` it wrote -- the config-location family
    with the numbered GIT_CONFIG_KEY_n / GIT_CONFIG_VALUE_n pairs present,
    the identity family, the template directory -- and `_home_env` builds
    the session templates' environment without them. With those exported,
    a commit under `_home_env` still carries the synthetic identity, where
    the same commit under the inherited environment carries the export."""
    other = tmp_path / "other.gitconfig"
    other.write_text("[user]\n\tname = Other Global\n\temail = other@example.invalid\n")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(other))
    monkeypatch.setenv("GIT_AUTHOR_NAME", "Someone Else")
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "user.email")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "counted@example.invalid")
    home = tmp_path / "home"
    home.mkdir()

    entries, remove = _make_home(home)

    assert entries == {"HOME": str(home), "XDG_CONFIG_HOME": str(home / ".config")}
    assert set(remove) == {
        *GIT_HOME_OVERRIDES,
        "GIT_CONFIG_KEY_0",
        "GIT_CONFIG_VALUE_0",
    }
    assert set(GIT_HOME_OVERRIDES) == {
        "GIT_CONFIG_GLOBAL",
        "GIT_CONFIG_SYSTEM",
        "GIT_CONFIG_NOSYSTEM",
        "GIT_CONFIG_COUNT",
        "GIT_AUTHOR_NAME",
        "GIT_AUTHOR_EMAIL",
        "GIT_AUTHOR_DATE",
        "GIT_COMMITTER_NAME",
        "GIT_COMMITTER_EMAIL",
        "GIT_COMMITTER_DATE",
        "GIT_TEMPLATE_DIR",
    }
    session_home = tmp_path / "session-home"
    session_home.mkdir()
    env = _home_env(session_home)
    assert not set(remove) & set(env)
    assert env["HOME"] == str(session_home)
    assert env["PATH"] == os.environ["PATH"]

    def author(environment: dict[str, str]) -> str:
        repo = tmp_path / str(len(list(tmp_path.iterdir())))
        repo.mkdir()
        for argv in (["init", "-q"], ["commit", "-q", "--allow-empty", "-m", "x"]):
            subprocess.run(
                ["git", *argv],
                cwd=repo,
                env=environment,
                check=True,
                capture_output=True,
            )
        return subprocess.run(
            ["git", "log", "-1", "--format=%an <%ae>"],
            cwd=repo,
            env=environment,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

    name, email = OFFLINE_GIT_IDENTITY
    assert author(env) == f"{name} <{email}>"
    assert author(dict(os.environ)) == "Someone Else <counted@example.invalid>"


def test_an_unmarked_test_runs_under_its_own_home(tmp_path, tmp_path_factory):
    """`Path.home()`, `$HOME` and `$XDG_CONFIG_HOME` resolve into a fresh
    directory under pytest's basetemp, for this process and for a subprocess
    it launches; it holds the synthetic git identity as global config and
    nothing else (no plugin registry, no global excludes), so a commit in a
    temp repository succeeds under that identity and a local `user.name`
    still outranks it; none of the git variables that would outrank the
    `.gitconfig` is in the environment. Unmarked, deliberately: like the
    socket block, the redirect is decided by the markers alone and holds
    under the live flags.
    """

    home = Path.home()
    real_home = Path(pwd.getpwuid(os.getuid()).pw_dir)
    assert home != real_home
    assert home.is_relative_to(tmp_path_factory.getbasetemp())
    assert os.environ["HOME"] == str(home)
    assert os.environ["XDG_CONFIG_HOME"] == str(home / ".config")
    assert sorted(p.name for p in home.iterdir()) == [".config", ".gitconfig"]
    assert not (home / ".claude").exists()
    assert not set(GIT_HOME_OVERRIDES) & set(os.environ)
    assert not [
        key
        for key in os.environ
        if key.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))
    ]
    child = subprocess.run(
        [sys.executable, "-c", "from pathlib import Path; print(Path.home())"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert child.stdout.strip() == str(home)

    def git(*args):
        return subprocess.run(
            ["git", *args], cwd=tmp_path, capture_output=True, text=True, check=True
        ).stdout.strip()

    name, email = OFFLINE_GIT_IDENTITY
    git("init", "-q")
    assert git("config", "--global", "--list").splitlines() == [
        f"user.name={name}",
        f"user.email={email}",
    ]
    (tmp_path / "a.md").write_text("a\n")
    git("add", "--", "a.md")
    git("commit", "-qm", "under the suite identity")
    assert git("log", "-1", "--format=%an <%ae>") == f"{name} <{email}>"
    git("config", "--local", "user.name", "Local Name")
    git("config", "--local", "user.email", "local@example.invalid")
    git("commit", "-q", "--allow-empty", "-m", "under the local identity")
    assert (
        git("log", "-1", "--format=%an <%ae>") == "Local Name <local@example.invalid>"
    )


def test_the_template_vaults_were_built_under_the_suite_home(fixture_vault):
    """The session-scoped fixture vault's one commit carries the synthetic
    identity: the templates every test copies were built under a home of the
    suite's own, not the developer's global config."""
    name, email = OFFLINE_GIT_IDENTITY
    author = subprocess.run(
        ["git", "log", "-1", "--format=%an <%ae>"],
        cwd=fixture_vault,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert author == f"{name} <{email}>"


def test_strict_markers_is_on_so_a_misspelled_marker_cannot_collect(request):
    """``--strict-markers`` is on, read from the live config: a typo'd
    ``live_net`` mark would otherwise run silently in the offline suite and
    make real external API calls. The option is what this pins; the collection
    error it produces is pytest's own behaviour, not provoked here."""
    assert request.config.getoption("strict_markers") is True


def test_contributor_vault_state_is_ignored_and_untracked():
    """`AGENTS.md`'s product boundary as a mechanism: root `wiki/`, `.raw/`
    and `.vault-meta/` are contributor state, ignored by `.gitignore` and
    tracked by nothing (the repository is public)."""
    roots = ("wiki", ".raw", ".vault-meta")
    tracked = subprocess.run(
        ["git", "ls-files", "--", *roots],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    assert tracked == "", f"contributor vault state is tracked: {tracked}"
    for root in roots:
        ignored = subprocess.run(
            ["git", "check-ignore", "-q", f"{root}/anything.md"],
            cwd=ROOT,
            check=False,
        )
        assert ignored.returncode == 0, f"{root}/ is not ignored by .gitignore"
