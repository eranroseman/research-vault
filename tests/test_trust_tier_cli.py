"""The `trust-tier` subcommand: a read-only report over events.trust_tier (spec §5).

`events.trust_tier` derives a literature note's cumulative verification tier
(unverified / machine-confirmed / human-reviewed) but had no production
consumer at HEAD — only tests exercised it directly. `project-flow`'s
resume-orientation step needs to display each cited note's tier, and a
prompt skill cannot call a Python function, so this is the invocable
surface: Task 3's `factcheck` precedent (a read-only mechanical part joins
the one binary as a branch-1 bare report noun, docs/terminology.md §4.3;
spec §7's one-binary/one-exit-code-contract CLI). It writes nothing — no
event, status, tag, hold, or ack — the same shape as `verify`/`factcheck`.
"""

import subprocess
import sys
from pathlib import Path

from research_vault import Result, events
from research_vault.__main__ import main

PMID_ONLY = """---
citationKey: "pmid2020"
type: "literature"
pmid: "12345"
---
"""


def _write_note(vault, citation_key, text):
    (vault / "literatures" / f"{citation_key}.md").write_text(text)


def test_trust_tier_prints_unverified_for_an_unverified_note(tmp_vault, capsys):
    _write_note(tmp_vault, "pmid2020", PMID_ONLY)

    code = main(["trust-tier", "pmid2020", "--vault", str(tmp_vault)])

    assert code == 0
    assert capsys.readouterr().out == "unverified\n"


def test_trust_tier_prints_machine_confirmed_after_applicable_checks_pass(
    tmp_vault, capsys
):
    text = events.record_pass(
        PMID_ONLY, "update-notice", Result.MATCHED, at="2026-08-16"
    )
    _write_note(tmp_vault, "pmid2020", text)

    code = main(["trust-tier", "pmid2020", "--vault", str(tmp_vault)])

    assert code == 0
    assert capsys.readouterr().out == "machine-confirmed\n"


def test_trust_tier_prints_human_reviewed_after_a_human_event(tmp_vault, capsys):
    text = events.record_pass(
        PMID_ONLY, "update-notice", Result.MATCHED, at="2026-08-16"
    )
    text = events.record_pass(
        text, "update-notice", Result.MATCHED, by="human:eran", at="2026-08-17"
    )
    _write_note(tmp_vault, "pmid2020", text)

    code = main(["trust-tier", "pmid2020", "--vault", str(tmp_vault)])

    assert code == 0
    assert capsys.readouterr().out == "human-reviewed\n"


def test_trust_tier_refuses_an_invalid_citation_key(tmp_vault, capsys):
    """Exit 2, not 1: an unsafe citation key is the verb failing to run, and the
    exit-code contract reserves 1 for a check that ran and disagreed."""
    code = main(["trust-tier", "../escape", "--vault", str(tmp_vault)])

    assert code == 2
    assert "invalid citation key" in capsys.readouterr().err


def test_trust_tier_refuses_a_missing_note(tmp_vault, capsys):
    """Exit 2 for the same reason: no note means no tier to report at all."""
    code = main(["trust-tier", "nosuch2020", "--vault", str(tmp_vault)])

    assert code == 2
    assert "not found" in capsys.readouterr().err


def test_trust_tier_reports_malformed_frontmatter_without_a_traceback(
    tmp_vault, capsys
):
    _write_note(tmp_vault, "broken2020", "---\nunterminated\n")

    code = main(["trust-tier", "broken2020", "--vault", str(tmp_vault)])

    assert code == 2
    assert "trust tier unavailable" in capsys.readouterr().err


def test_trust_tier_is_reachable_through_the_one_binary_cli(tmp_vault):
    """Proves `trust-tier` is genuinely wired into the shared dispatch table —
    ``python3 -m research_vault trust-tier``, not a second binary."""
    _write_note(tmp_vault, "pmid2020", PMID_ONLY)
    repo = Path(__file__).resolve().parents[1]

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "research_vault",
            "trust-tier",
            "pmid2020",
            "--vault",
            str(tmp_vault),
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert completed.stdout == "unverified\n"
