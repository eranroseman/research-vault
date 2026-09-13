"""Canonicality of the surfaces no off-the-shelf formatter may touch.

The one-form-owner matrix (docs/research/rethink-audits/2026-08-21-lint-format-rethink.md) gives every
file type a single owner. For WRITTEN vault-dialect markdown -- literature
notes with real claim-line content, not the placeholder templates they are
built from -- the owner is *the sole writer*: mdformat measurably mangles
the dialect on real content — ``[[wikilink]]`` becomes ``\\[[wikilink]\\]``,
``[field:: value]`` gets escaped, a standalone marker line that follows a
list item gets indented into it (verified 2026-08-21 on a real rendered
literature note round-tripped through mdformat) — and ``mdformat-obsidian``
does the same, so no formatter speaks it. (Task 2e gated every STATIC template
but one through mdformat instead: their placeholder content carries no
list markup or wikilinks to mangle, so mdformat owns them now. The one held
out, ``vault/index.md``, does carry real wikilinks and Base embeds and stays
excluded — see .pre-commit-config.yaml's mdformat hook.) "The emitter is the
formatter" only means something if the emitter is actually canonical, which
is what this file makes mechanical:

1. every durable ledger line an emitter produces matches the shared entry
   grammar exactly, anchored end to end;
2. scaffold output is byte-stable across two runs into fresh directories.

Together these give the vault surfaces form-certainty with zero remembered
rules — enforced by the owners, verified here.
"""

import re

import pytest

from research_vault import Result, appendlog, inbox, scaffold, searchlog

# The full-line grammar, BUILT FROM the shared field definition rather than
# restated: a restated copy is exactly the drift this file exists to catch. The
# named groups are made non-capturing first, since the pattern appears twice.
_FIELD = re.sub(r"\(\?P<[a-z]+>", "(?:", appendlog._FIELD.pattern)
LEDGER_LINE = re.compile(rf"^- {_FIELD}(?: {_FIELD})*$")


# --------------------------------------------------------------------------
# 1. Ledger/inbox entry grammar
# --------------------------------------------------------------------------


@pytest.fixture
def project_vault(tmp_vault):
    """A vault with one existing project directory — search-log's precondition."""
    (tmp_vault / "projects" / "brief").mkdir(parents=True)
    return tmp_vault


def _written_lines(path):
    body = path.read_text(encoding="utf-8")
    return [line for line in body.splitlines() if line.startswith("- [")]


def test_every_inbox_line_the_emitter_writes_matches_the_entry_grammar(tmp_vault):
    inbox.append_entry(
        tmp_vault,
        "doi",
        "smith2020",
        Result.UNMATCHED,
        "mismatch — DOI does not resolve",
        date="2026-08-20",
    )
    inbox.append_entry(
        tmp_vault,
        "quote",
        "smith2020#^c-11111111",
        Result.UNMATCHED,
        "fuzzy-quote — quote text drifted",
        date="2026-08-20",
        target_hash="aa11",
    )
    lines = _written_lines(tmp_vault / inbox.INBOX_PATH)
    assert len(lines) == 2
    for line in lines:
        assert LEDGER_LINE.fullmatch(line), f"ungrammatical inbox line: {line!r}"


def test_every_search_log_line_the_emitter_writes_matches_the_entry_grammar(
    project_vault,
):
    searchlog.append_search(
        project_vault, "brief", "mortality AND strata", "PubMed", 5, date="2026-08-20"
    )
    searchlog.append_not_admitted(
        project_vault,
        "brief",
        "Some candidate paper",
        "not-admitted",
        source="PubMed",
        date="2026-08-20",
    )
    lines = _written_lines(searchlog.search_log_path(project_vault, "brief"))
    assert len(lines) == 2
    for line in lines:
        assert LEDGER_LINE.fullmatch(line), f"ungrammatical search-log line: {line!r}"


def test_a_bracket_in_a_value_stays_grammatical_after_escaping(project_vault):
    """The escape pair is what keeps a `]` in free text from ending the field."""
    searchlog.append_search(
        project_vault, "brief", "term [bracketed] here", "PubMed", 1, date="2026-08-20"
    )
    (line,) = _written_lines(searchlog.search_log_path(project_vault, "brief"))
    assert LEDGER_LINE.fullmatch(line), f"ungrammatical escaped line: {line!r}"
    (entry,) = searchlog.load(project_vault, "brief")
    assert entry.query == "term [bracketed] here"


# --------------------------------------------------------------------------
# 2. Scaffold byte-stability
# --------------------------------------------------------------------------


def _scaffolded_bytes(root):
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and ".git/" not in f"{path.relative_to(root)}/"
    }


def test_scaffold_output_is_byte_stable_across_two_fresh_runs(tmp_path):
    first, second = tmp_path / "one", tmp_path / "two"
    first.mkdir()
    second.mkdir()

    created_first = scaffold.scaffold_vault(first)
    created_second = scaffold.scaffold_vault(second)

    assert created_first == created_second
    assert _scaffolded_bytes(first) == _scaffolded_bytes(second)


def test_rescaffolding_an_existing_vault_rewrites_nothing(tmp_path):
    """Idempotence on the second run: the scaffold owns form, so it must settle."""
    vault = tmp_path / "vault"
    vault.mkdir()
    scaffold.scaffold_vault(vault)
    before = _scaffolded_bytes(vault)

    scaffold.scaffold_vault(vault)

    assert _scaffolded_bytes(vault) == before
