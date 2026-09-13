"""Generic contract every shipped ``skills/*/SKILL.md`` must satisfy (spec §7, §8).

Unlike ``test_skill_files.py`` (setup-vault-specific content acceptance),
this module asserts only what the control model and plugin architecture
require of *every* skill, present and future. It is written to stay green
as entry skills are added — nothing here is scoped to any one skill.
"""

import ast
import re
import shlex
from pathlib import Path

import pytest

from research_vault import inbox
from research_vault.frontmatter import FrontmatterError, parse
from tests.conftest import package_ast

REPOSITORY = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPOSITORY / "skills"
TEMPLATES_DIR = REPOSITORY / "research_vault" / "templates"
PACKAGE_DIR = REPOSITORY / "research_vault"

# Control model (spec §7/§8): entry skills ship
# `disable-model-invocation: true` so they never enter the model catalog;
# every other shipped skill is a guard/reference skill, model-invoked AND
# user-invocable, so it carries neither `disable-model-invocation` nor
# `user-invocable`. This list grows by one name as each entry skill ships —
# it only ever grows, never shrinks.
ENTRY_SKILLS = {
    "setup-vault",
    "publish",
    "verify-citations",
    "factcheck-draft",
    "project-flow",
    "capture-source",
    "find-sources",
}

# A bare kebab-case token in backticks, e.g. `` `evidence-conventions` `` —
# the shape a skill name takes when a template cites one in prose. Requires
# at least one hyphen so ordinary single words never match, and excludes
# slashes/dots/percents so path fragments (`` `synthesis/index.md` ``),
# comment markers (`` `%%rv-anything%%` ``), and similar template furniture
# never false-positive.
_BACKTICKED_KEBAB_TOKEN = re.compile(r"`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`")


def _skill_dirs() -> list[Path]:
    return sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())


def _skill_md_files() -> list[Path]:
    return sorted(SKILLS_DIR.glob("*/SKILL.md"))


def _shipped_template_files() -> list[Path]:
    # context.md is the packaged glossary (byte-identical to CONTEXT.md, pinned
    # by test_templates.py::test_packaged_context_is_the_canonical_glossary_source),
    # never a skill-routing surface: it backticks governed frontmatter fields
    # and identifiers (`zotero-item-key`, `managed-sha256`, `compile-input-sha256`,
    # ...) that take the same bare-kebab shape a cited skill name would, without
    # being one. AGENTS.md's routing table is the surface this scan actually
    # guards, and it is unaffected by the exclusion.
    return sorted(
        p
        for p in TEMPLATES_DIR.rglob("*")
        if p.is_file() and p != TEMPLATES_DIR / "context.md"
    )


def test_every_skill_directory_ships_a_skill_md():
    dirs = _skill_dirs()
    assert dirs, "expected at least one skills/<name>/ directory"
    for directory in dirs:
        assert (directory / "SKILL.md").is_file(), f"{directory} has no SKILL.md"


def test_every_entry_skill_named_here_is_actually_shipped():
    """Keeps ENTRY_SKILLS load-bearing: the per-skill invocation check below is
    parametrized over shipped files, so a name added here without its
    directory would otherwise assert nothing."""
    missing = sorted(ENTRY_SKILLS - {directory.name for directory in _skill_dirs()})
    assert not missing, f"ENTRY_SKILLS names unshipped skill(s): {missing}"


@pytest.mark.parametrize("skill_md", _skill_md_files(), ids=lambda p: p.parent.name)
def test_frontmatter_parses_via_the_core_parser(skill_md):
    text = skill_md.read_text(encoding="utf-8")
    try:
        data, body = parse(text)
    except FrontmatterError as error:
        pytest.fail(f"{skill_md}: frontmatter does not parse: {error}")
    assert data, f"{skill_md}: frontmatter is empty"
    assert body.strip(), f"{skill_md}: body is empty"


@pytest.mark.parametrize("skill_md", _skill_md_files(), ids=lambda p: p.parent.name)
def test_name_matches_directory(skill_md):
    data, _ = parse(skill_md.read_text(encoding="utf-8"))
    assert data.get("name") == skill_md.parent.name


@pytest.mark.parametrize("skill_md", _skill_md_files(), ids=lambda p: p.parent.name)
def test_description_is_nonempty(skill_md):
    data, _ = parse(skill_md.read_text(encoding="utf-8"))
    description = data.get("description")
    assert isinstance(description, str)
    assert description.strip()


@pytest.mark.parametrize("skill_md", _skill_md_files(), ids=lambda p: p.parent.name)
def test_invocation_flags_match_the_ruled_control_model(skill_md):
    name = skill_md.parent.name
    data, _ = parse(skill_md.read_text(encoding="utf-8"))
    if name in ENTRY_SKILLS:
        assert data.get("disable-model-invocation") == "true", (
            f"{name} is an entry skill and must ship disable-model-invocation: true"
        )
    else:
        assert "disable-model-invocation" not in data, (
            f"{name} is a guard/reference skill (model-invoked AND "
            "user-invocable) and must not ship disable-model-invocation"
        )
    # Reserved for future machine contracts; no skill ships it yet (spec §7).
    assert "user-invocable" not in data, (
        f"{name}: user-invocable is reserved for future machine contracts"
    )


_FINDING_INVOCATION = "python3 -m research_vault finding "


def _shipped_finding_invocations() -> list[tuple[Path, list[str]]]:
    invocations = []
    for skill_md in _skill_md_files():
        invocations.extend(
            (skill_md, shlex.split(line.strip()))
            for line in skill_md.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(_FINDING_INVOCATION)
        )
    return invocations


def test_every_shipped_finding_invocation_names_registered_identifiers():
    """A skill that spells a check id or reason code the registry dropped would
    ship a command the CLI refuses — and prose is the one surface no test
    otherwise reads. Catches the drift at build time, not at a person's shell."""
    invocations = _shipped_finding_invocations()
    assert invocations, "expected at least one shipped `finding` invocation"
    for skill_md, tokens in invocations:
        check, _target, result, reason = tokens[4:8]
        assert check in inbox.CHECK_IDS, (
            f"{skill_md}: unregistered check id {check!r} in a shipped command"
        )
        assert result in {"UNMATCHED", "UNREACHABLE", "SKIPPED"}, (
            f"{skill_md}: {result!r} is not a result the `finding` verb accepts"
        )
        try:
            inbox.validate_reason(reason)
        except ValueError as error:
            pytest.fail(f"{skill_md}: {error}")


def test_every_skill_name_a_shipped_template_cites_has_a_skill_directory():
    """Scans every shipped template generically rather than asserting any
    one cited name by hand."""
    cited = set()
    for template in _shipped_template_files():
        text = template.read_text(encoding="utf-8")
        cited.update(_BACKTICKED_KEBAB_TOKEN.findall(text))
    assert cited, "expected at least one skill name cited in a shipped template"
    existing = {directory.name for directory in _skill_dirs()}
    missing = sorted(cited - existing)
    assert not missing, (
        f"shipped templates cite skill name(s) with no skills/<name>/ "
        f"directory: {missing}"
    )


def _code_spelled_identifiers() -> list[str]:
    """Every string the package evaluates, off its AST, docstrings excluded.

    A skill's bare-kebab tokens are not all skill names: check ids
    (``captured-set``), reason codes (``not-admitted``), verbs
    (``mark-published``), doctor probes (``bbt-git``), markers
    (``failed-verification``) and tags (``open-question``) take the same
    shape. Every one of those is an identifier the code spells, so "the code
    spells it" is the decision, deferred to the code the way
    ``_emitted_check_ids`` defers. Measured 2026-09-13 across the 42 distinct
    tokens the nine skills cite: whole-literal equality misses
    ``open-question``, which ``claims.py`` owns only inside a regex
    alternation; a substring read over *every* literal masks three live skill
    names (``factcheck-draft``, ``find-sources``, ``project-flow``) through
    docstrings that talk about them; a substring read over the non-docstring
    literals spells every non-skill token and no live hyphenated skill name.
    A docstring is a bare string-expression statement, prose the code never
    evaluates, so it is dropped rather than read as spelling.
    """
    spelled: list[str] = []
    for module in sorted(PACKAGE_DIR.glob("*.py")):
        tree = package_ast(module)
        prose = {
            id(node.value)
            for node in ast.walk(tree)
            if isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        }
        spelled.extend(
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and id(node) not in prose
        )
    return spelled


def _cited_skill_tokens_by_skill() -> dict[str, set[str]]:
    return {
        skill_md.parent.name: set(
            _BACKTICKED_KEBAB_TOKEN.findall(skill_md.read_text(encoding="utf-8"))
        )
        for skill_md in _skill_md_files()
    }


def test_every_skill_name_a_shipped_skill_cites_has_a_skill_directory():
    """The templates scan above walks ``research_vault/templates/`` only, so
    a live skill routed to a deleted skill directory passes it. Same token
    shape, second corpus: a bare
    kebab token a skill cites is a skill name unless the code spells it as an
    identifier (``_code_spelled_identifiers``), and every skill name needs a
    ``skills/<name>/`` directory. A foreign skill a vendored fork names by
    provenance is prose about a name, not a route, and goes unbackticked
    (``find-sources/SKILL.md:11``) rather than exempted here."""
    existing = {directory.name for directory in _skill_dirs()}
    spelled = _code_spelled_identifiers()
    cited = _cited_skill_tokens_by_skill()
    dangling = {
        skill: sorted(
            token
            for token in tokens - existing
            if not any(token in literal for literal in spelled)
        )
        for skill, tokens in cited.items()
    }
    dangling = {skill: tokens for skill, tokens in dangling.items() if tokens}
    assert not dangling, (
        f"skill(s) cite skill name(s) with no skills/<name>/ directory: "
        f"{dangling}. Fix the route (the skill was renamed or deleted)."
    )


def test_the_code_spells_no_hyphenated_skill_name():
    """The self-check that keeps the exclusion above from masking a route.

    ``_code_spelled_identifiers`` exempts a token the code spells, so the day a
    non-docstring literal in ``research_vault/`` carries a live skill name —
    ``"run capture-source"`` in an error message — that skill's deletion would
    stop failing the scan. This fails that day instead, visibly, and the
    author narrows the reading. A rule on product code, and the price of the
    exclusion; measured 2026-09-13 as already true (``publish`` is spelled,
    but carries no hyphen and so is never a token the scan reads).
    """
    spelled = _code_spelled_identifiers()
    hyphenated = {
        directory.name for directory in _skill_dirs() if "-" in directory.name
    }
    assert hyphenated, "expected at least one hyphenated skill directory"
    offenders = sorted(
        name for name in hyphenated if any(name in literal for literal in spelled)
    )
    assert offenders == [], (
        f"research_vault/ spells skill name(s) in a non-docstring literal: "
        f"{offenders}; the skill-directory scan would no longer catch a route "
        f"to them once deleted"
    )


# --------------------------------------------------------------------------
# Prose enumerating what code owns. A skill that hand-lists an identifier
# set the code owns drifts the moment the code moves. The remedy is defer to
# the code, or pin the enumeration by test — never hand-maintain one. The
# two checks below are the pins.
# --------------------------------------------------------------------------

_BACKTICKED = re.compile(r"`([^`]+)`")
# "check id" / "check ids", the phrase that marks the backticked run after it
# as a claim *about check ids* rather than about verbs, tags, or fields.
_CHECK_ID_PHRASE = re.compile(r"check ids?\b")
# Two backticked tokens belong to one run only when nothing but list
# punctuation separates them. Prose between them ends the run, so
# ``check id `factcheck`, carrying that claim's `text_hash` `` reads as one
# id followed by unrelated prose, not as a two-id list. A markdown cell
# boundary ends a run too: ``|`` is deliberately NOT a joiner, or two
# adjacent table cells would read as one enumeration.
_RUN_JOINER = re.compile(r"^[\s,/]*(?:and|or)?[\s,/]*$")
# A sentence break between the phrase and the first backticked token means the
# token belongs to a later clause, not to the enumeration the phrase opened.
_SENTENCE_BREAK = re.compile(r"[.;]\s")
# How many members of a run must already be check ids the code files before
# the run reads as a check-id enumeration on its own, with no phrase to
# introduce it. Two: one is not a list, and single ids collide with other
# vocabularies (``quote`` is also an evidence-boundary tag, ``disputed-claim``
# also a reason code), so a threshold of one would fail correct prose.
_CO_OCCURRENCE_ANCHOR = 2


def _emitted_check_ids() -> set[str]:
    """Every check id ``research_vault`` can put on an ``Outcome``, off its AST.

    Check ids are literals at their construction sites rather than a registry
    constant. ``inbox.CHECK_IDS`` is the *registry* — the boundary the
    `finding` verb enforces — and ``inbox.py``'s own comment records that the
    deterministic pipeline legitimately files ids that registry does not
    carry (``append-only``, ``claim-immutability``, ``published-drift``). So
    the registry alone would flag correct prose, and
    the AST is the only honest source for what a `verify` run can emit. Same
    technique and same reason as ``_probe_ids`` in ``test_config_validity``.

    Sites whose first argument is a variable are wrappers (``checks.py``'s
    record rehydrator, ``lints.py``'s ``_schema_outcome``, ``verify.py``'s
    offline-network fan-out); every id they are ever handed is a literal at a
    call site this scan already reads, so skipping them loses nothing.
    """
    emitted: set[str] = set()
    for module in sorted(PACKAGE_DIR.glob("*.py")):
        tree = package_ast(module)
        constants = {
            target.id: node.value.value
            for node in tree.body
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
            for target in node.targets
            if isinstance(target, ast.Name)
        }
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not node.args:
                continue
            if (
                getattr(node.func, "id", None) != "Outcome"
                and getattr(node.func, "attr", None) != "Outcome"
            ):
                continue
            check = node.args[0]
            if isinstance(check, ast.Constant) and isinstance(check.value, str):
                emitted.add(check.value)
            elif isinstance(check, ast.Name) and check.id in constants:
                emitted.add(constants[check.id])
    return emitted


def _known_check_ids() -> set[str]:
    """Every check id the code knows, from all three of its code-side sources.

    The emitted set and the registry overlap but neither contains the other:
    the pipeline emits three ids the registry does not carry, and the registry
    carries four (``publish``, ``factcheck``, ``render``, ``integrate``) that
    only the `finding` verb ever files — skills name those in prose too, so
    an emitted-only universe would fail correct prose.
    ``REPEATABLE_ACT_CHECKS`` adds ``publish-gate``, filed by the Stop hook.
    """
    return (
        _emitted_check_ids() | set(inbox.CHECK_IDS) | set(inbox.REPEATABLE_ACT_CHECKS)
    )


def _backticked_runs(line: str) -> list[list[re.Match]]:
    """Split one line into maximal runs of backticked tokens.

    A run continues only across list punctuation; anything else — prose, a
    markdown cell boundary — starts a new run.
    """
    runs: list[list[re.Match]] = []
    current: list[re.Match] = []
    previous_end = None
    for token in _BACKTICKED.finditer(line):
        if previous_end is not None and _RUN_JOINER.match(
            line[previous_end : token.start()]
        ):
            current.append(token)
        else:
            if current:
                runs.append(current)
            current = [token]
        previous_end = token.end()
    if current:
        runs.append(current)
    return runs


def _enumerated_check_ids(text: str) -> list[tuple[int, str]]:
    """Every check id a document names as a check id, with its line number.

    Two anchors decide whether a backticked run is a check-id enumeration.
    Anchoring at all is what keeps the sweep honest: an unanchored scan
    cannot tell the check id ``quote`` from the evidence-boundary tag of the
    same name, and would fail correct prose.

    1. **Phrase** — the first run after "check id"/"check ids" on that line,
       provided no sentence break separates them. Catches the one-id claim
       ("filed by check id `factcheck`"), which no count of members would.
    2. **Co-occurrence** — any run with ``_CO_OCCURRENCE_ANCHOR`` or more
       members the code already files. Catches the enumerations that never
       write the phrase, which is most of them: at HEAD, four of the five
       multi-id enumerations the corpus ships are introduced by prose like
       "this surface closes on" or sit inside a table cell.

    Bound, read off the return condition below rather than guessed at: a run
    is returned only if the prose introduces it, or **at least two of its
    members are still ids the code files**. ``named`` counts survivors, not
    renames — so a phrase-less run's visibility tracks how many valid ids
    remain beside a drifted one, not how many drifted. The two-member run
    shipped at ``skills/publish/SKILL.md:37`` ("this surface's other two
    closing checks, `citation-key` and `evidence-layer`", which sits before that
    line's "check id" phrase and so has only this anchor) goes unread the
    moment *either* single member drifts, carrying the drifted token out of
    view with it. A longer run stays readable while two valid members
    survive and goes dark below that — not only when every member is
    renamed. Pinned by
    ``test_the_documented_bound_on_the_co_occurrence_anchor_holds``.
    """
    known = _known_check_ids()
    found = []
    for number, line in enumerate(text.splitlines(), start=1):
        runs = _backticked_runs(line)
        phrase = _CHECK_ID_PHRASE.search(line)
        introduced = None
        if phrase is not None:
            for run in runs:
                if run[0].start() < phrase.end():
                    continue
                if not _SENTENCE_BREAK.search(line[phrase.end() : run[0].start()]):
                    introduced = run
                break
        for run in runs:
            named = sum(1 for token in run if token.group(1) in known)
            if run is introduced or named >= _CO_OCCURRENCE_ANCHOR:
                found.extend((number, token.group(1)) for token in run)
    return found


@pytest.mark.parametrize("skill_md", _skill_md_files(), ids=lambda p: p.parent.name)
def test_recognizable_check_id_enumerations_name_only_ids_the_code_files(skill_md):
    """A skill naming a check id the code renamed or dropped ships prose
    that describes output the CLI cannot produce. Prose is the one
    surface no other test reads; this catches the drift at build time.

    "Recognizable" is load-bearing and not a hedge — it names exactly what
    ``_enumerated_check_ids`` reads, and that is less than every check id in
    the file. A run the prose does not introduce is read only while at least
    two of its members are still valid ids, so drift in a short phrase-less
    run can take the entire run out of view, drifted token included — see
    that function's bound, pinned by
    ``test_the_documented_bound_on_the_co_occurrence_anchor_holds``. What is
    read at HEAD: all five multi-id enumerations the shipped corpus carries,
    plus every phrase-led single-id claim.
    """
    known = _known_check_ids()
    unknown = sorted(
        f"line {number}: {check!r}"
        for number, check in _enumerated_check_ids(skill_md.read_text(encoding="utf-8"))
        if check not in known
    )
    assert not unknown, (
        f"{skill_md} names check id(s) no `verify` run emits and no registry "
        f"carries: {unknown}"
    )


def test_the_emitted_check_id_scan_finds_the_pipelines_own_ids():
    """Guards the instrument, not the prose: a scan that silently found
    nothing would make the sweep above pass on anything."""
    emitted = _emitted_check_ids()
    assert emitted, "AST scan found no Outcome check ids — the scan itself is broken"
    # The four the registry does not carry are the whole reason this is an AST
    # scan rather than `inbox.CHECK_IDS`; losing them is losing the point.
    assert {
        "append-only",
        "claim-immutability",
        "published-drift",
    } <= emitted


def test_the_documented_bound_on_the_co_occurrence_anchor_holds():
    """The bound the two docstrings state, made executable.

    It was stated wrongly once — ``de1867d``'s body and docstrings claimed
    only a *wholesale* rename escapes — so it is pinned here rather than left
    as prose a later reader has to re-derive. The shape is the two-member run
    the corpus actually ships at ``skills/publish/SKILL.md:37``, which no
    "check id" phrase introduces.
    """
    pair = "— this surface's other two closing checks, `{a}` and `{b}`, mint nothing."
    assert _enumerated_check_ids(pair.format(a="citation-key", b="evidence-layer")) == [
        (1, "citation-key"),
        (1, "evidence-layer"),
    ]
    # ONE rename leaves one survivor, below the anchor, and the whole run goes
    # unread — the drifted token with it. Single-id drift, not wholesale.
    assert (
        _enumerated_check_ids(pair.format(a="citation-keys", b="evidence-layer")) == []
    )
    assert _enumerated_check_ids(pair.format(a="citation-key", b="evidence-tier")) == []

    # Longer runs track survivors too: two survivors keep the run readable and
    # the drifted member is reported; one survivor takes it out of view.
    triple = "This surface closes on `{a}`, `{b}`, and `{c}`."
    assert _enumerated_check_ids(
        triple.format(a="citation-key", b="evidence-layer", c="bogus-one")
    ) == [(1, "citation-key"), (1, "evidence-layer"), (1, "bogus-one")]
    assert (
        _enumerated_check_ids(triple.format(a="bogus-one", b="bogus-two", c="doi"))
        == []
    )


def test_the_check_id_extractor_anchors_on_the_phrase_and_on_co_occurrence():
    """Guards the extractor on a literal sample, so an anchor that quietly
    stopped matching cannot pass as clean prose. Every line here is a shape
    the shipped corpus actually carries."""
    sample = (
        # Phrase anchor: one surviving id, introduced by the prose.
        "Every other outcome is a finding, filed by check id `source-status`, "
        "carrying that claim's `text_hash` as `--target-hash`.\n"
        # Co-occurrence anchor: an enumeration that never says "check id".
        "This surface closes on `citation-key`, `evidence-layer`, and `contested`.\n"
        # One known id is not a list — the evidence-boundary-tag trap.
        "Tag it `quote`, `paraphrase`, `inference`, or `open-question`.\n"
        # No known id is not a list either.
        "`mark-published` and `mark-corrected` mint a project-level event.\n"
        # A markdown cell boundary is not list punctuation: without that,
        # `doi` and `quote` would merge into a two-id run and drag
        # `paraphrase` in with them.
        "| `doi` | check id `quote` | `paraphrase` |\n"
    )
    assert _enumerated_check_ids(sample) == [
        (1, "source-status"),
        (2, "citation-key"),
        (2, "evidence-layer"),
        (2, "contested"),
        (5, "quote"),
    ]


_REASON_SECTION_HEADING = "## Reason-code vocabulary"
EVIDENCE_CONVENTIONS = SKILLS_DIR / "evidence-conventions" / "SKILL.md"
_COUNT_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}


def _reason_code_section() -> tuple[set[str], str]:
    """The reason-code table's own codes, and the prose that closes it."""
    text = EVIDENCE_CONVENTIONS.read_text(encoding="utf-8")
    start = text.index(_REASON_SECTION_HEADING)
    end = text.index("\n## ", start + 1)
    lines = text[start:end].splitlines()
    # A code row leads with its own code in backticks; the header and rule
    # rows do not, so neither needs naming here.
    tabled = {
        _BACKTICKED.search(line).group(1) for line in lines if line.startswith("| `")
    }
    last_row = max(index for index, line in enumerate(lines) if line.startswith("|"))
    return tabled, "\n".join(lines[last_row + 1 :]).strip()


def test_evidence_conventions_accounts_for_every_reason_code():
    """The table plus its closing sentence must together name the whole
    registry, each code exactly once. Registering a new code with no row and
    no exemption fails here — the closing sentence's count claim is the part
    that drifts otherwise.

    ``matched`` is the only exemption the section may claim, and it is a real
    one: only non-MATCHED results file findings, so no MATCHED reason ever
    reaches the queue. ``manual`` carries a row because a person *can* meet it
    there — ``hooks/stop_publish_gate.py`` writes it through
    ``inbox.append_entry`` when someone bypasses the publish gate. Moving it
    back off the table fails the equality below.
    """
    tabled, closing = _reason_code_section()
    assert tabled, "found no reason-code rows — the section scan is broken"
    assert closing, "the reason-code table ships no closing sentence to pin"
    exempt = set(_BACKTICKED.findall(closing))
    assert tabled <= inbox.REASON_CODES, (
        f"table rows name unregistered reason code(s): {sorted(tabled - inbox.REASON_CODES)}"
    )
    assert exempt <= inbox.REASON_CODES, (
        "the closing sentence backticks non-reason-code token(s): "
        f"{sorted(exempt - inbox.REASON_CODES)}"
    )
    assert tabled.isdisjoint(exempt), (
        f"code(s) both tabled and called off the table: {sorted(tabled & exempt)}"
    )
    assert tabled | exempt == inbox.REASON_CODES, (
        "reason codes with neither a table row nor a named exemption: "
        f"{sorted(inbox.REASON_CODES - tabled - exempt)}"
    )
    word = _COUNT_WORDS[len(exempt)]
    assert re.search(rf"\b{word}\b", closing, re.IGNORECASE), (
        f"the closing sentence exempts {len(exempt)} code(s) but does not say {word!r}"
    )
