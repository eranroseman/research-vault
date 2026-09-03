"""Config surfaces that currently fail SILENTLY, made to fail loudly in CI.

Three classes of silent failure live here, all of the same shape — a file the
plugin loader or a human reader trusts, which nothing mechanically checks:

* a malformed ``hooks.json`` or plugin manifest is swallowed at plugin load;
* a typo'd ``SKILL.md`` frontmatter key is swallowed the same way;
* an identifier coined in code but never given a row in ``docs/terminology.md``
  §4.4 stays ungoverned until somebody happens to run a naming audit.

The JSON half doubles as the *formatter*: ``json.tool``'s canonical form is
asserted here rather than run as a separate hook, so the one-form-owner matrix
gains a JSON owner with zero new dependencies (docs/research/rethink-audits/2026-08-21-lint-format-rethink.md).
"""

import ast
import json
import re
import shlex
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
import yaml

from research_vault import frontmatter, inbox

ROOT = Path(__file__).resolve().parents[1]

# The repo's own JSON manifests, and only those. Deliberately NOT globbed:
# `docs/research/` JSON is source material outside this formatter's managed surface,
# `.vscode/*.json` is JSONC — a dialect VS Code owns — and a vault's
# `system/bibliography.json` is BBT-owned, outside every repo formatter.
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
    for tool in ("ruff", "mypy", "mdformat", "yamlfix", "pyproject-fmt", "pre-commit"):
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
        for line in (ROOT / "docs/terminology.md")
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
    tree = ast.parse((ROOT / "research_vault/scaffold.py").read_text())
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

    This asserted only that the row contained the string ``REASON_CODES`` until
    2026-08-22, on the reading that §4.4 governed this group by reference. The
    row's own Status cell says otherwise -- "additions require a reference row" --
    so the document was already promising the property the test declined to
    enforce, and a new code could land with no row and leave the suite green.
    Reason codes go verbatim onto ``inbox/review-queue.md``, the highest-traffic
    human surface in the system; it is the last group that should be governed
    more loosely than the rest.
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
# Ruled 2026-08-22 after an as-built re-measure contradicted the plan's adoption
# claim ("verified: tool-section comments preserved, zero spurious churn" — which
# had been tested on a synthetic fragment, not on this file). Measured against the
# REAL pyproject.toml, bare pyproject-fmt truncated pins (`mdformat==1.0.0` to
# `==1`), invented a classifiers block claiming Python 3.14, and — the dangerous
# one — alpha-sorted the dependency list while hoisting a ruling comment's
# continuation lines onto a DIFFERENT package, so a recorded ruling silently
# described the wrong dependency.
#
# The flags below fix that. These tests are what stop the fix from being a
# remembered rule: a future pyproject-fmt that drops --keep-full-version, or that
# relocates a comment block, fails here instead of quietly making a recorded
# ruling false. The association tests assert PLACEMENT, not presence — the
# original failure preserved every comment character while attaching it to the
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
    ("Lazy-imported at research_vault's single parse site", '"defusedxml==0.7.1"'),
    ("FORMAT + RENDER-CONTRACT pin", '"mdformat==1.0.0"'),
    ("never in addopts", '"pytest-xdist==3.8.0"'),
    ("Dev-lane instrument, read-only posture", '"pyzotero[cli]==1.14.0"'),
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
    over this set, and three rows of the foundation spec's frontmatter table
    carried `status: unscreened | included | excluded | superseded`. GFM ends the
    cell at the first unescaped `|` REGARDLESS of the code span, so mdformat
    reformatted the truncated parse back out and the enum values plus an entire
    `superseded-by` clause were deleted -- by a commit whose message read "No
    sentence, no code, and no meaning is changed anywhere in this commit".

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
