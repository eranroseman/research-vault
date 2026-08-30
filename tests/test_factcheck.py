"""The vendored claim-selection module for factored verification (spec §6).

Forked from K-Dense-AI/scientific-agent-skills @ 336c4f8 (MIT) — see the
provenance header in ``research_vault/factcheck.py`` for exactly what was
ported (SHA-256 claim hashing; verified-evidence-only counting) versus what
is this repo's own contract (the four-bucket deterministic order, the
budget cap).
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from research_vault import Result, events, factcheck
from research_vault.__main__ import main
from research_vault.factcheck import ClaimRef

MANAGED = "%%rv-managed%%\n{body}\n%%/rv-managed%%\n"


def _note(citekey, body, verified=None):
    header = f'---\ncitekey: "{citekey}"\ntype: "literature"\n---\n'
    text = header + MANAGED.format(body=body)
    if verified is not None:
        for event in verified:
            text = events.record_pass(
                text, event["check"], Result.MATCHED, by=event["by"], at=event["at"]
            )
    return text


def _draft(claims_text):
    return (
        '---\ntitle: "Draft"\ntype: "project"\nstatus: "draft"\n'
        'generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}\n'
        "---\n" + claims_text
    )


def _write_vault(tmp_vault, notes: dict[str, str], draft_claims: str):
    literatures = tmp_vault / "literatures"
    for citekey, text in notes.items():
        (literatures / f"{citekey}.md").write_text(text)
    project = tmp_vault / "projects" / "brief"
    project.mkdir(parents=True, exist_ok=True)
    draft_path = project / "draft.md"
    draft_path.write_text(_draft(draft_claims))
    return draft_path


# --- claim_text_hash -----------------------------------------------------


def test_claim_text_hash_is_stable_and_normalizes_whitespace():
    a = factcheck.claim_text_hash("Mortality   fell 12%\n")
    b = factcheck.claim_text_hash("Mortality fell 12%")
    assert a == b
    assert len(a) == 64


def test_claim_text_hash_changes_with_content():
    assert factcheck.claim_text_hash("Mortality fell 12%") != factcheck.claim_text_hash(
        "Mortality fell 20%"
    )


# --- eligible_claims -------------------------------------------------------


def test_eligible_claims_excludes_open_question_and_unresolved_citekey(tmp_vault):
    draft_path = _write_vault(
        tmp_vault,
        {"smith2020": _note("smith2020", "# Note\n")},
        "- (open-question) Does this hold? ^c-11111111\n"
        "- (inference) It replicates [@fabricated2020] ^c-22222222\n"
        "- (paraphrase) Effect confirmed [@smith2020, p. 3] ^c-33333333\n",
    )

    refs = factcheck.eligible_claims(tmp_vault, draft_path)

    assert [ref.claim_link for ref in refs] == ["smith2020#^c-33333333"]
    assert refs[0].tag == "paraphrase"


def test_eligible_claims_preserves_document_order(tmp_vault):
    draft_path = _write_vault(
        tmp_vault,
        {"smith2020": _note("smith2020", "# Note\n")},
        "- (paraphrase) First [@smith2020, p. 1] ^c-11111111\n"
        "- (inference) Second [@smith2020, p. 2] ^c-22222222\n"
        "- (quote) [@smith2020, p. 3] ^c-33333333\n"
        "  > Verbatim text.\n",
    )

    refs = factcheck.eligible_claims(tmp_vault, draft_path)

    assert [ref.claim_link for ref in refs] == [
        "smith2020#^c-11111111",
        "smith2020#^c-22222222",
        "smith2020#^c-33333333",
    ]
    quote_ref = refs[2]
    assert quote_ref.text_hash == factcheck.claim_text_hash(
        "- (quote) [@smith2020, p. 3] ^c-33333333\n  > Verbatim text."
    )


# --- select_claims: the binding §6 order -----------------------------------


def test_selection_orders_unverified_first_contested_boosted_quote_last(tmp_vault):
    notes = {
        "verified2020": _note(
            "verified2020",
            "# Note\n",
            verified=[{"by": "process:cli", "at": "2026-08-01", "check": "doi"}],
        ),
        "unverified2020": _note("unverified2020", "# Note\n"),
    }
    draft_path = _write_vault(
        tmp_vault,
        notes,
        "- (quote) [@unverified2020, p. 1] ^c-quote0001\n"
        "  > Verbatim.\n"
        "- (paraphrase) Backed by a verified note [@verified2020, p. 1] ^c-verified1\n"
        "- (inference) Unverified source [@unverified2020, p. 2] ^c-unverif01\n"
        "- (paraphrase) Contested claim [@verified2020, p. 2] ^c-contested\n",
    )
    refs = factcheck.eligible_claims(tmp_vault, draft_path)
    by_link = {ref.claim_link: ref for ref in refs}
    contested = {by_link["verified2020#^c-contested"].claim_link}

    selected, skipped = factcheck.select_claims(tmp_vault, refs, contested, cap=4)

    assert [ref.claim_link for ref in selected] == [
        "unverified2020#^c-unverif01",
        "verified2020#^c-contested",
        "verified2020#^c-verified1",
        "unverified2020#^c-quote0001",
    ]
    assert skipped == []


def test_selection_respects_the_cap_and_returns_the_tail_as_skipped(tmp_vault):
    draft_path = _write_vault(
        tmp_vault,
        {"smith2020": _note("smith2020", "# Note\n")},
        "".join(
            f"- (inference) Claim {n} [@smith2020, p. {n}] ^c-{n:08d}\n"
            for n in range(5)
        ),
    )
    refs = factcheck.eligible_claims(tmp_vault, draft_path)

    selected, skipped = factcheck.select_claims(tmp_vault, refs, set(), cap=3)

    assert len(selected) == 3
    assert len(skipped) == 2
    assert {ref.claim_link for ref in selected} | {
        ref.claim_link for ref in skipped
    } == {ref.claim_link for ref in refs}


def test_select_claims_rejects_a_negative_cap(tmp_vault):
    with pytest.raises(ValueError, match="cap"):
        factcheck.select_claims(tmp_vault, [], set(), cap=-1)


# --- contested_adjacent_links ------------------------------------------------


def test_contested_adjacent_links_reuses_the_disputed_claim_lint(tmp_vault):
    (tmp_vault / "literatures" / "smith2020.md").write_text(_note("smith2020", "# N\n"))
    (tmp_vault / "literatures" / "gone2019.md").write_text(_note("gone2019", "# N\n"))
    (tmp_vault / "synthesis" / "mortality.md").write_text(
        '---\ntitle: "Mortality"\ntype: "synthesis"\nstatus: "draft"\n'
        'generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}\n---\n'
        "- (inference) Contested [supports:: [[smith2020#^c-11111111]]] "
        "[disputes:: [[gone2019#^c-22222222]]] ^c-99999999\n"
    )
    project = tmp_vault / "projects" / "brief"
    project.mkdir(parents=True)
    draft_path = project / "draft.md"
    draft_path.write_text(
        _draft(
            "- (paraphrase) Builds on it [@smith2020, p. 1] "
            "[supports:: [[smith2020#^c-11111111]]] ^c-33333333\n"
        )
    )

    contested = factcheck.contested_adjacent_links(tmp_vault, draft_path)

    assert contested == {"smith2020#^c-33333333"}


# --- skipped_sha256 ----------------------------------------------------------


def test_skipped_sha256_is_order_independent_and_content_sensitive():
    a = ClaimRef("smith2020#^c-1", "inference", 1, "h1")
    b = ClaimRef("smith2020#^c-2", "inference", 2, "h2")

    assert factcheck.skipped_sha256([a, b]) == factcheck.skipped_sha256([b, a])
    assert factcheck.skipped_sha256([a]) != factcheck.skipped_sha256([a, b])


# --- run() and the CLI entry -------------------------------------------------


def test_run_reports_cap_selected_skipped_and_a_sha256_only_when_something_skipped(
    tmp_vault,
):
    draft_path = _write_vault(
        tmp_vault,
        {"smith2020": _note("smith2020", "# Note\n")},
        "- (inference) Only claim [@smith2020, p. 1] ^c-11111111\n",
    )

    report = factcheck.run(tmp_vault, draft_path, cap=30)

    assert report["cap"] == 30
    assert len(report["selected"]) == 1
    assert report["skipped"] == []
    assert report["skipped_sha256"] is None


def test_run_wires_contested_adjacency_into_the_ordering_end_to_end(tmp_vault):
    """A regression that dropped ``contested`` from ``run()``'s wiring would
    pass every ordering test that feeds ``select_claims`` its set by hand —
    this one exercises ``run()`` alone, with a quote claim (bucket 3 by
    default) boosted past an ordinary quote claim (also bucket 3) purely by
    disputed-claim adjacency."""
    (tmp_vault / "literatures" / "smith2020.md").write_text(
        _note("smith2020", "# Note\n")
    )
    (tmp_vault / "literatures" / "gone2019.md").write_text(
        _note("gone2019", "# Note\n")
    )
    (tmp_vault / "synthesis" / "mortality.md").write_text(
        '---\ntitle: "Mortality"\ntype: "synthesis"\nstatus: "draft"\n'
        'generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}\n---\n'
        "- (inference) Disputing [supports:: [[smith2020#^c-11111111]]] "
        "[disputes:: [[gone2019#^c-99999999]]] ^c-syn00001\n"
    )
    project = tmp_vault / "projects" / "brief"
    project.mkdir(parents=True)
    draft_path = project / "draft.md"
    # The ordinary claim comes FIRST in document order and the contested one
    # SECOND — the opposite of the expected selection — so a broken wiring
    # (both claims falling into bucket 3 with no boost) would pick the
    # ordinary claim by document-order tie-break, not the contested one,
    # and this assertion would actually fail rather than pass by accident.
    draft_path.write_text(
        _draft(
            "- (quote) [@smith2020, p. 2] ^c-ordinary1\n"
            "  > Verbatim B.\n"
            "- (quote) [@smith2020, p. 1] [supports:: [[smith2020#^c-11111111]]] "
            "^c-contested\n"
            "  > Verbatim A.\n"
        )
    )

    report = factcheck.run(tmp_vault, draft_path, cap=1)

    assert [claim["claim_link"] for claim in report["selected"]] == [
        "smith2020#^c-contested"
    ]
    assert [claim["claim_link"] for claim in report["skipped"]] == [
        "smith2020#^c-ordinary1"
    ]


def test_factcheck_subcommand_prints_json_and_exits_zero(tmp_vault, capsys):
    """The CLI entry lives at ``research_vault.__main__.main(["factcheck",
    …])`` — spec §7's one-binary/one-exit-code-contract CLI — not a separate
    ``factcheck.main``; the module itself ships no standalone entry point."""
    draft_path = _write_vault(
        tmp_vault,
        {"smith2020": _note("smith2020", "# Note\n")},
        "- (inference) Only claim [@smith2020, p. 1] ^c-11111111\n",
    )

    code = main(
        [
            "factcheck",
            "--vault",
            str(tmp_vault),
            "--draft",
            str(draft_path),
            "--cap",
            "1",
        ]
    )

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["cap"] == 1
    assert len(payload["selected"]) == 1


def test_factcheck_subcommand_reports_a_missing_draft_without_a_traceback(
    tmp_vault, capsys
):
    code = main(
        [
            "factcheck",
            "--vault",
            str(tmp_vault),
            "--draft",
            "projects/missing/draft.md",
        ]
    )

    assert code == 2
    assert "selection unavailable" in capsys.readouterr().err


def test_factcheck_is_reachable_through_the_one_binary_cli(tmp_vault):
    """Proves `factcheck` is genuinely wired into the shared dispatch table —
    ``python3 -m research_vault factcheck``, not a second binary."""
    draft_path = _write_vault(
        tmp_vault,
        {"smith2020": _note("smith2020", "# Note\n")},
        "- (inference) Only claim [@smith2020, p. 1] ^c-11111111\n",
    )
    repo = Path(__file__).resolve().parents[1]

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "research_vault",
            "factcheck",
            "--vault",
            str(tmp_vault),
            "--draft",
            str(draft_path),
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(completed.stdout)
    assert len(payload["selected"]) == 1
