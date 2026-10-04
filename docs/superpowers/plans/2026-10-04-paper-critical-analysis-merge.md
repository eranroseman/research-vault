# One paper-critical-analysis Skill From Two — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `skills/critical-analysis-report/` and `skills/paper-critical-analysis/` with one skill, `paper-critical-analysis`, running the eight-stage reader–judge–editor–verifier process and producing a report plus an evidence file.

**Architecture:** The report template is the checker's single source of truth: `scripts/check_report.py` reads its required headings from `templates/report-template.md` and `templates/evidence-template.md`. One main context runs stages 0–2, 4 and the dispositions; three fresh-context subagents (judge, editor, verifier) each get a brief from `prompts/`. Contract tests pin the surfaces that can drift apart (SKILL.md ↔ briefs ↔ templates ↔ checker).

**Tech Stack:** Markdown skill files; Python 3 (stdlib only) for the checker; pytest for tests; ruff + mdformat for form.

**Spec:** `docs/superpowers/specs/2026-10-04-paper-critical-analysis-merge-design.md` — the plan argues from the spec; executors read both.

## Global Constraints

Every task's requirements implicitly include these, copied from the spec:

- Branch: `paper-critical-analysis-merge` (this worktree already has it checked out). Never create a new branch or worktree.
- Commit with explicit pathspec: `git commit -- <files>`. End every commit message with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Skill name stays `paper-critical-analysis`; frontmatter keeps `disable-model-invocation: true`.
- Locators: "Section, page, figure, table, equation, footnote or reference number. No paragraph counting."
- Length: "Write uncapped, then prune with a fresh-context editor. No word bound." (The old checker had no length bounds either — removing them is a no-op; do not hunt for them.)
- Web access: "Required. The skill stops if the probe fails."
- Fan-out: "None. Very long papers are read in chunks" — `prompts/extract.md` is deleted.
- Output files, exactly: `critical-analysis-<paper-slug>.md`, `critical-analysis-<paper-slug>.evidence.md`, `critical-analysis-<paper-slug>.draft.md`, `<paper-slug>-work/`.
- Write scope: every file a run creates goes in the output folder.
- The nine topics, in fixed order: Importance, Credibility, Novelty, Applicability, Generalizability, Scalability, Assumptions, Readability, Ethics.
- Offline gate: `python -m pytest tests -q -n auto` (from the repo root, inside `.venv`), plus `ruff format`/`ruff check` and `mdformat --number --wrap keep` on touched files. mdformat owns every tracked `.md` here (templates and prompts included); it renders thematic breaks as underscore lines.
- This repository is the product source: nothing in this plan touches a user vault, `wiki/`, `.raw/`, or `sources/` (git-ignored run artifacts are read-only evidence).

### Pinned conventions (used by several tasks; decided once, here)

- **Placeholder style:** briefs use single-brace `{UPPER_SNAKE}` placeholders filled by the dispatcher; templates use `{{double-brace}}` placeholders filled by the report writer. (Matches the two retired skills.)
- **Brief placeholders:** judge: `{PAPER_PATHS}`, `{PAGE_RENDERS}`, `{EVIDENCE_PATH}`, `{REFERENCE_PATHS}`, `{LOCATOR_CONVENTION}`. editor: `{REPORT_PATH}`, `{EVIDENCE_PATH}`. verifier: `{PAPER_PATHS}`, `{PAGE_RENDERS}`, `{REPORT_PATH}`, `{EVIDENCE_PATH}`, `{LOCATOR_CONVENTION}`.
- **Evidence-file ID shape:** a ledger entry is a list item starting `- N1:` / `- C1:` / `- W1:` / `- P1:` (regex `^- ([NCWP]\d+):`). The checker reads definitions from exactly that shape.
- **ID citation shape in the report:** `\b[NCWP]\d+\b` (so `W3C`, `P2P` never match — no word boundary splits them).
- **Provenance key:** the report carries one literal line starting `Key: ` (template supplies it; checker requires `^Key: `).
- **`derived` sentence rule:** a sentence is a run of text ending at `.`, `!`, `?` or a line break; any sentence containing the word `derived` must also contain `\b[CWP]\d+\b` (P covers the judge's own computations, per the spec). Prose uses of "derived" false-positive by design; the fix is rewording the prose, and the template says so.
- **Coverage leads:** the Coverage section's required lines are the template's own bullets, matched by their lead text up to the first colon: `Not read`, `Not checked`, `For the reader to double-check`, `Verification`, `Recalled`, `Evidence file only`.
- **External-check slots:** the evidence template's External-check section carries one fixed slot per mandated stage 2 check (`Venue rigor`, `Authors' previous work`, `Reference counts`, `Tree backward`, `Tree forward`, `Related works read`, `Undefined concepts`, `Headline recomputations`); the checker requires each `- <lead>:` in the evidence file the same way it requires Coverage leads (run F: a check with no slot can be skipped invisibly).
- **Sections pending a later stage:** the checker runs at stage 6, before the verifier exists; a section whose stage has not run yet is filled `pending: stage <n>` rather than left empty (the templates say this; "nothing silent" covers it).
- **Default evidence path:** `report_path.with_suffix(".evidence.md")` (`.md` → `.evidence.md`).

## File Structure

End state of `skills/paper-critical-analysis/`:

```text
skills/paper-critical-analysis/
  SKILL.md                     stages 0–7 with completion bars; conditions table;
                               load table; locator convention; method menu; rules;
                               output paths                        (Task 3, rewrite)
  templates/
    report-template.md         the guide's outline; checker's heading source   (Task 1, new)
    evidence-template.md       the evidence file's sections; ID shapes         (Task 1, new)
  prompts/
    judge.md                   stage 3 brief                       (Task 3, revised)
    edit.md                    stage 5 brief                       (Task 3, new)
    verify.md                  stage 7 brief                       (Task 3, rewritten)
    extract.md                 DELETED                             (Task 3)
  references/
    sources-and-venues.md      merged source-type material         (Task 2, new)
    research-integrity.md      unchanged
    quantitative-methods.md    absorbs background.md's experiment-design and
                               result-interpretation material      (Task 2, extended)
    qualitative-methods.md     unchanged
    participants.md            absorbs background.md's fair-treatment signs (Task 2, extended)
    released-artifacts.md      new                                 (Task 2, new)
  scripts/
    check_report.py            extended from critical-analysis-report's (Task 1, new file here)
```

Removed in Task 4: `skills/critical-analysis-report/` entirely (SKILL.md, prompts/verify.md, references/background.md, references/notes-template.md, references/report-template.md, scripts/check_report.py).

Tests: `tests/test_check_report.py` (Task 1, new), `tests/test_paper_critical_analysis_skill.py` (Task 3, rewritten), `tests/test_skill_contracts.py` (Task 4, one entry removed + comment), `tests/test_templates.py` (no change — the vault-template row already reads "write an in-depth critical analysis report of one paper", which still fits; record as checked).

Other surfaces (Task 4): `README.md` (merge two flow rows), `ATTRIBUTION.md` (credit merged material and editor sources), `docs/research/2026-09-20-paper-critical-analysis-evals/README.md` (append merged-skill section). `docs/agents/terminology.md` already names only `paper-critical-analysis` — checked 2026-10-04 via repo-wide grep; no task.

______________________________________________________________________

### Task 1: Templates and the checker

**Files:**

- Create: `skills/paper-critical-analysis/templates/report-template.md`
- Create: `skills/paper-critical-analysis/templates/evidence-template.md`
- Create: `skills/paper-critical-analysis/scripts/check_report.py`
- Test: `tests/test_check_report.py`

**Interfaces:**

- Consumes: nothing from other tasks. The old checker at `skills/critical-analysis-report/scripts/check_report.py` is the starting material (copy, then modify); it is deleted only in Task 4, so the repo stays green throughout.

- Produces: `check_report.py` CLI — `python3 check_report.py REPORT.md [EVIDENCE.md]`, exit 0 clean / 1 errors, lines `error: ...` and `warning: ...`; module functions `check_report(report_text, evidence_text|None) -> (errors, warnings)` and `template_headings(path) -> list[(prefix, full)]` that Task 3's contract tests may import. Template heading texts below are load-bearing: SKILL.md (Task 3) and the briefs point at them.

- [ ] **Step 1: Write `templates/report-template.md`**

Write exactly this content (mdformat form: thematic break as underscores, ordered lists numbered):

```markdown
# Report template

Keep the headings, their order, and their numbering; `scripts/check_report.py` reads its required headings from this file, so this template is the single source of truth for the report's structure. The bullets are the guide's questions; answer them in prose. Replace every `{{placeholder}}`. Keep the `Key:` line verbatim — the checker requires it. A sentence containing the word "derived" must cite the C, W or P entry holding the computation; the checker flags any use of the word without one, so keep "derived" out of ordinary prose. A section whose stage has not run yet reads `pending: stage <n>`, never blank.

______________________________________________________________________

# Critical analysis: {{paper title}}

{{Authors (year). Title. Venue, pages or DOI.}} Version read: {{preprint and number, or published}}. Report written {{date}}.

Key: a locator cites the paper; (W12) cites a source outside the paper through the evidence file; [inferred] marks the writer's own reasoning; a number marked "derived" cites the C, W or P entry holding its computation; recalled knowledge appears only under Coverage.

## 1. Context

### 1.1 Title and authors

- Title: short and to the point? Tells you what to expect?
- Authors: how many, and what does the order say? Affiliations: one institution or many, which departments, well known? Their field?

### 1.2 Publication venue

- Which kind of venue (`references/sources-and-venues.md`), and what does that imply about review rigor? If unfamiliar, the predatory-venue check from the same file (cite the W entry).

### 1.3 The authors' previous work

- What have they done before in this area (cite the W entry)?

### 1.4 Motivation

- Why is the problem important? Does the paper motivate the research, state the contribution, and preview the rest?

### 1.5 Related work and references

- Does the paper cover relevant prior work, synthesize it rather than list it, and establish the gap it fills?
- Tree backward: are the works it builds on the field's recognized foundations, or idiosyncratic picks? Tree forward: is recent work citing a key reference conspicuously absent here (cite the W entries)?
- The 3–5 related works read for this report, one line each (cite the W entries).
- Reference counts: total; with at least one of the authors; from the authors' institution; span of years; kinds of sources. A count a citation index could not complete is labelled partial.

## 2. Summary

The abstract's content at greater length, in the paper's own order.

### 2.1 Problem

- The research questions, hypotheses, objectives, or goals; what the authors set out to do.

### 2.2 Method

- What did the authors do? Which method family (SKILL.md's method menu), and what can results from that family show and not show?
- What the Summary reports for the family: `references/quantitative-methods.md` or `references/qualitative-methods.md`; otherwise the methods, techniques, or process followed.

### 2.3 Results

- Big picture first, then details; how the data was analyzed; descriptive then inferential statistics.

### 2.4 Discussion

- The authors' interpretation, implications, practical value, stated limitations, and future work — as they present them.

### 2.5 Conclusion

- Does it summarize methods, results, and discussion, and restate the significance? Acknowledgements and funding?

## 3. Critical discussion

### Verdicts

The nine verdict sentences, one line each, in the order below.

### Importance

Opens with its verdict, then the points that bear on it, in prose. Every point keeps its locators and IDs.

### Credibility

Opens with its verdict. Closes with a confidence level (high, medium, or low) and the evidence that would raise it.

### Novelty

Opens with its verdict, then its points.

### Applicability

Opens with its verdict, then its points.

### Generalizability

Opens with its verdict, then its points.

### Scalability

Opens with its verdict, then its points.

### Assumptions

Opens with its verdict, then its points.

### Readability

Opens with its verdict, then its points.

### Ethics

Opens with its verdict, then its points.

## 4. Coverage

- Not read: parts of the paper, supplements, or artifacts not read, and why.
- Not checked: checks that could not run, each with its reason.
- For the reader to double-check: claims resting on inference or an unconfirmed source.
- Verification: the verifier's counts checked and failed, and the checker's final result.
- Recalled: the judge's recalled knowledge, one line each.
- Evidence file only: findings left in the evidence file, by ID.
```

- [ ] **Step 2: Write `templates/evidence-template.md`**

Write exactly this content:

````markdown
# Evidence template

The evidence file is the report's audit trail; each section is filled during the stage that produces it, so an interrupted run resumes from the stage log. `scripts/check_report.py` reads its required headings from this file. A ledger entry starts on its own line — `- N1:`, `- C1:`, `- W1:`, or `- P1:` — and detail may continue on indented lines beneath it; the checker reads IDs from exactly that first-line shape, and every ID defined here must appear in the report or on Coverage's "Evidence file only" line. A section whose stage has not run yet reads `pending: stage <n>`, never blank.

______________________________________________________________________

# Evidence: {{paper title}}

Report: {{report path}}.

## Identity

Filled at stage 1, from the full text, not from the request: title; authors; venue and year; DOI; version read; full text read from; matches the paper requested ({{yes | no}}, confirmed by {{how}}).

## Conditions

Filled at stage 0: one line per row of SKILL.md's conditions table, each with how it was settled; the web probe's request, response, and verdict.

## Stage log

One line per stage as its completion bar is met: `stage <n>: met — <date, time>`. An interrupted run resumes after the last line.

## Section map

The page or heading of each part: title, abstract, introduction, related work, hypotheses or research questions, methods, results, discussion, conclusion, references, appendices, supplements. Parts missing or merged, named.

## Promises

Five numbered lines, each quoted from or located in the title, abstract, introduction, or conclusion:

1. Problem:
2. Why it matters:
3. Approach:
4. Contribution claimed:
5. What would make it trustworthy:

## Claims

Every principal claim, numbered:

```
Claim 1: [the claim, as the paper states it]
Evidence: [what the paper offers for it]
Needed: [what evidence would settle it]
```

## Not-stated list

Everything the report will need that the paper does not give. One entry per line: `- N1: <item>; needed by <claim or slot>`.

## Inconsistency list

Every place two locations in the paper conflict. One entry per line: `- C1: <both locators; both values>`. The reconciliation log follows as plain lines under this heading: every reported result in the abstract and text reconciled against the tables, figures and supplements, every percentage, sum and effect size against the numbers it rests on, arithmetic done in code.

## External-check list

One entry per outside check: `- W1: <claim checked>; <source>; <URL or saved copy>; <what the source said>`. The related works read and the released-artifact checks are W entries too.

The mandated checks each hold a fixed slot, filled with the W IDs that discharged it or `not checked: <reason>` — the checker reports an unfilled slot, so a skipped check is a visible hole rather than a silent one:

- Venue rigor:
- Authors' previous work:
- Reference counts:
- Tree backward:
- Tree forward:
- Related works read:
- Undefined concepts:
- Headline recomputations:

## Judge points

Filled at stage 3's return: the kept points under assigned IDs, `- P1: <Kind; Locator; Observation; Evidence; Why it matters>`, then the judge's Recalled lines, then the count of points dropped as inadmissible.

## Pruning record

Filled at stage 5: word counts before and after, then the editor's change list with each item applied or rejected and why.

## Verifier list

Filled at stage 7: each verifier item with its disposition (fixed, dropped, or moved to Coverage), then the counts checked.

## Deletions

Filled at the end of stage 7: every raw participant-level file deleted from the scratch folder, by path.
````

- [ ] **Step 3: Write the failing tests**

Create `tests/test_check_report.py` with exactly this content:

```python
"""check_report.py enforces the report rules the spec lists; the templates are
its single source of truth for structure.

The passing fixture is BUILT FROM THE SHIPPED TEMPLATES through the checker's
own heading parser, so a template edit that breaks agreement fails here rather
than in a live run. Each spec rule then gets one failing mutation.
"""

import contextlib
import importlib.util
import io
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[1] / "skills" / "paper-critical-analysis"
CHECKER = SKILL_DIR / "scripts" / "check_report.py"

_spec = importlib.util.spec_from_file_location("check_report", CHECKER)
check_report = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_report)

KEY_LINE = (
    "Key: a locator cites the paper; (W12) cites a source outside the paper "
    "through the evidence file; [inferred] marks the writer's own reasoning; "
    'a number marked "derived" cites the C, W or P entry holding its '
    "computation; recalled knowledge appears only under Coverage."
)


def _topic_body(heading: str) -> str:
    body = "Verdict: the paper holds on this dimension (Table 2; N1). P1 bears here."
    if heading.startswith("### Credibility"):
        body += " Confidence: medium; an independent replication would raise it."
    return body


def _coverage_body() -> str:
    leads = check_report.coverage_leads()
    lines = []
    for lead in leads:
        if lead == "Evidence file only":
            lines.append(f"- {lead}: P2.")
        else:
            lines.append(f"- {lead}: none; checked: the whole run.")
    return "\n".join(lines)


def build_report() -> str:
    """Fill the shipped report template heading-by-heading."""
    lines = []
    for _, full in check_report.template_headings(check_report.REPORT_TEMPLATE):
        heading = full.replace("{{paper title}}", "Example")
        lines.append(heading)
        if heading.startswith("# Critical analysis"):
            lines.append("Doe (2026). Example. Venue. Version read: v1. Written 2026-10-04.")
            lines.append(KEY_LINE)
        elif heading.startswith("### Verdicts"):
            lines.append("Nine one-line verdicts stand here (Section 1; W1).")
        elif heading.startswith("## 4."):
            lines.append(_coverage_body())
        elif heading.startswith("### 2.3"):
            lines.append("The rate is 4.2 per day, derived, from C1. CORE ranks it (W1).")
        elif heading.startswith("###") and check_report.is_topic(heading):
            lines.append(_topic_body(heading))
        else:
            lines.append("Filled in prose; see Section 2 of the paper.")
        lines.append("")
    return "\n".join(lines)


def build_evidence() -> str:
    """Fill the shipped evidence template heading-by-heading."""
    lines = []
    for _, full in check_report.template_headings(check_report.EVIDENCE_TEMPLATE):
        heading = full.replace("{{paper title}}", "Example")
        lines.append(heading)
        if heading.startswith("## Not-stated"):
            lines.append("- N1: consent wording; needed by Claim 1.")
        elif heading.startswith("## Inconsistency"):
            lines.append("- C1: Table 2 says 4.2, abstract says 4.4; recomputed in code.")
        elif heading.startswith("## External-check"):
            lines.append("- W1: venue rigor; CORE; saved copy; ranked A.")
            lines.extend(
                f"- {lead}: W1." for lead in check_report.external_check_leads()
            )
        elif heading.startswith("## Judge points"):
            lines.append("- P1: Not reported; Table 2; no denominator; N1; weakens the rate.")
            lines.append("- P2: Not reported; Section 5; minor wording slip; C1; low stakes.")
        else:
            lines.append("Filled; pending sections read pending: stage 7.")
        lines.append("")
    return "\n".join(lines)


def run(report: str, evidence: str | None, tmp_path: Path) -> tuple[int, str]:
    report_path = tmp_path / "critical-analysis-example.md"
    report_path.write_text(report, encoding="utf-8")
    if evidence is not None:
        (tmp_path / "critical-analysis-example.evidence.md").write_text(
            evidence, encoding="utf-8"
        )
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        status = check_report.main([str(report_path)])
    return status, out.getvalue()


def test_the_template_built_pair_passes(tmp_path):
    status, out = run(build_report(), build_evidence(), tmp_path)
    assert status == 0, out


def test_the_shipped_templates_carry_the_checker_tokens():
    """The key line and the pending device live in the templates; the checker
    requires them in the filled files. If the template drops one, every run
    fails at stage 6 with no way to comply."""
    report_template = check_report.REPORT_TEMPLATE.read_text(encoding="utf-8")
    assert "\nKey: " in report_template
    evidence_template = check_report.EVIDENCE_TEMPLATE.read_text(encoding="utf-8")
    assert "- N1:" in evidence_template
    for text in (report_template, evidence_template):
        assert "pending: stage" in text


def _drop_heading(report: str) -> str:
    return report.replace("### 1.4 Motivation\n", "")


def _empty_section(report: str) -> str:
    return report.replace(
        "### 1.4 Motivation\nFilled in prose; see Section 2 of the paper.",
        "### 1.4 Motivation\n",
    )


def _leftover_placeholder(report: str) -> str:
    return report.replace("Written 2026-10-04.", "Written {{date}}.")


def _topic_without_evidence(report: str) -> str:
    return report.replace(
        "### Importance\n"
        "Verdict: the paper holds on this dimension (Table 2; N1). P1 bears here.",
        "### Importance\nVerdict: fine, broadly speaking.",
    )


def _no_confidence(report: str) -> str:
    return report.replace(
        " Confidence: medium; an independent replication would raise it.", ""
    )


def _missing_coverage_line(report: str) -> str:
    return report.replace("- Not checked: none; checked: the whole run.\n", "")


def _derived_without_id(report: str) -> str:
    return report.replace(
        "The rate is 4.2 per day, derived, from C1.",
        "The rate is 4.2 per day, derived from the tables.",
    )


def _missing_key(report: str) -> str:
    return report.replace(KEY_LINE + "\n", "")


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (_drop_heading, "missing heading"),
        (_empty_section, "empty section"),
        (_leftover_placeholder, "placeholder"),
        (_topic_without_evidence, "no locator"),
        (_no_confidence, "confidence"),
        (_missing_coverage_line, "Not checked"),
        (_derived_without_id, "derived"),
        (_missing_key, "provenance key"),
    ],
)
def test_each_report_rule_fails_its_fixture(tmp_path, mutate, expected):
    status, out = run(mutate(build_report()), build_evidence(), tmp_path)
    assert status == 1
    assert expected in out


def test_an_unused_evidence_id_breaks_the_ledger(tmp_path):
    evidence = build_evidence().replace(
        "- N1: consent wording; needed by Claim 1.",
        "- N1: consent wording; needed by Claim 1.\n- N9: never cited anywhere.",
    )
    status, out = run(build_report(), evidence, tmp_path)
    assert status == 1
    assert "N9" in out and "ledger" in out


def test_a_dangling_report_id_breaks_the_ledger(tmp_path):
    report = build_report().replace("(Table 2; N1)", "(Table 2; N1; W7)", 1)
    status, out = run(report, build_evidence(), tmp_path)
    assert status == 1
    assert "W7" in out and "ledger" in out


def test_a_missing_evidence_file_is_an_error(tmp_path):
    status, out = run(build_report(), None, tmp_path)
    assert status == 1
    assert "evidence" in out and "not found" in out


def test_a_missing_evidence_heading_is_an_error(tmp_path):
    evidence = build_evidence().replace("## Stage log\n", "")
    status, out = run(build_report(), evidence, tmp_path)
    assert status == 1
    assert "missing heading" in out


def test_an_unfilled_mandated_check_slot_is_an_error(tmp_path):
    """Run F: a mandated check that silently never ran was invisible because
    the list had no slot-by-slot accounting. The slots make it a hole."""
    evidence = build_evidence().replace("- Tree forward: W1.\n", "")
    status, out = run(build_report(), evidence, tmp_path)
    assert status == 1
    assert "Tree forward" in out and "slot" in out
```

- [ ] **Step 4: Run the tests to verify they fail**

Run: `cd /home/eranr/research-vault/.worktrees/paper-critical-analysis-merge && .venv/bin/python -m pytest tests/test_check_report.py -q` (if `.venv` lives only in the main checkout, `source /home/eranr/research-vault/.venv/bin/activate` first; same for every pytest step below).
Expected: FAIL at import — `skills/paper-critical-analysis/scripts/check_report.py` does not exist.

- [ ] **Step 5: Write `scripts/check_report.py`**

Create `skills/paper-critical-analysis/scripts/` and write exactly:

```python
#!/usr/bin/env python3
"""Check a critical-analysis report and its evidence file against the templates.

Usage: python3 check_report.py REPORT.md [EVIDENCE.md]

EVIDENCE.md defaults to REPORT.md with ``.evidence.md`` in place of ``.md``.
The required headings are read from ``templates/report-template.md`` and
``templates/evidence-template.md`` beside this script; the templates are the
single source of truth for structure.

Errors (exit status 1): a required heading is missing; a section is empty; a
``{{placeholder}}`` is still in place; a critical-discussion topic cites no
locator and no N/C/W/P ID and does not say "not applicable"; Credibility
states no confidence; a Coverage lead line from the template is missing; a
sentence containing "derived" cites no C, W or P entry; the ``Key:``
provenance line is missing; a mandated-check slot in the evidence file's
External-check list is unfilled; the ledger is broken (an ID defined in the
evidence file appears neither in the report nor on Coverage's "Evidence file
only" line, or the report cites an ID the evidence file never defines); the
evidence file is missing. Warnings (exit status 0) point at things only a
reader can judge.
"""

import argparse
import re
import sys
from pathlib import Path

Heading = tuple[str, str]  # (prefix the line must start with, heading as written)
Section = tuple[int, str, list[str]]  # (level, heading line, body lines)

SKILL_DIR = Path(__file__).resolve().parents[1]
REPORT_TEMPLATE = SKILL_DIR / "templates" / "report-template.md"
EVIDENCE_TEMPLATE = SKILL_DIR / "templates" / "evidence-template.md"

# mdformat renders a thematic break as a run of underscores; accept the raw
# forms too so a hand-written template still parses.
BREAK_RE = re.compile(r"^(?:_{3,}|-{3,}|\*{3,})\s*$")
HEADING_RE = re.compile(r"^(#{1,6})\s+\S")
PLACEHOLDER_RE = re.compile(r"\{\{")
NOT_APPLICABLE_RE = re.compile(r"\bnot applicable\b", re.IGNORECASE)
# "none found", "not checked", "not applicable" each need a tail saying where
# you looked or why: a following ":" ";" "," or a "because"-style connective.
BARE_PHRASE_RE = re.compile(
    r"\b(none found|not checked|not applicable)\b"
    r"(?!\s*[:;,]\s*\S)(?!\s+(?:because|since|as|for)\b)",
    re.IGNORECASE,
)
CONFIDENCE_RE = re.compile(
    r"\bconfidence\b.*?\b(?:high|medium|low)\b", re.IGNORECASE | re.DOTALL
)
BARE_SIGNIFICANT_RE = re.compile(
    r"(?<!statistically )(?<!non-)(?<!non )\bsignificant\b", re.IGNORECASE
)
# Explicit locators only: a word like "results" would let every critique pass.
LOCATOR_RE = re.compile(
    r"§\s*\d|\b(?i:sections?|sect\.|p\.|pp\.|pages?|fig\.|figures?|tables?|"
    r"appendix|appendices|eq\.|equations?|footnotes?|references?)\s*(?:[A-Z]|\d|\[)"
)
SECTION_NAME_RE = re.compile(r"\b(?:Abstract|Introduction|Related Work|Conclusions?)\b")
ID_RE = re.compile(r"\b[NCWP]\d+\b")
CWP_ID_RE = re.compile(r"\b[CWP]\d+\b")
DEFINED_ID_RE = re.compile(r"^- ([NCWP]\d+):", re.MULTILINE)
DERIVED_RE = re.compile(r"\bderived\b", re.IGNORECASE)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
KEY_LINE_RE = re.compile(r"^Key: ", re.MULTILINE)


def _without_key_lines(text: str) -> str:
    """The ``Key:`` legend names (W12) and "derived" as examples; the ledger
    and derived rules must not read the legend as citations."""
    return "\n".join(
        line for line in text.splitlines() if not line.startswith("Key: ")
    )


def template_headings(path: Path) -> list[Heading]:
    """Required headings from a template: every heading after its first
    thematic break. A heading carrying a ``{{placeholder}}`` matches by the
    prefix up to the braces."""
    required: list[Heading] = []
    seen_break = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if not seen_break:
            seen_break = bool(BREAK_RE.match(line))
            continue
        if HEADING_RE.match(line):
            full = line.rstrip()
            prefix = full.split("{{")[0].rstrip() if "{{" in full else full
            required.append((prefix, full))
    return required


def _report_headings() -> list[Heading]:
    return template_headings(REPORT_TEMPLATE)


def is_topic(heading: str) -> bool:
    """A critical-discussion topic: a level-3 heading between ``## 3.`` and
    ``## 4.`` in the report template, excluding the Verdicts block."""
    topics = []
    inside = False
    for prefix, _ in _report_headings():
        if prefix.startswith("## 3."):
            inside = True
        elif prefix.startswith("## "):
            inside = False
        elif inside and prefix.startswith("### ") and not prefix.startswith("### Verdicts"):
            topics.append(prefix)
    return any(heading.startswith(topic) for topic in topics)


def coverage_leads() -> list[str]:
    """The Coverage section's required lead words, from the template's own
    bullets: the text between ``- `` and the first colon."""
    text = REPORT_TEMPLATE.read_text(encoding="utf-8")
    coverage = text[text.index("## 4.") :]
    return [
        line[2 : line.index(":")]
        for line in coverage.splitlines()
        if line.startswith("- ") and ":" in line
    ]


def external_check_leads() -> list[str]:
    """The External-check section's mandated-slot leads, from the evidence
    template's own bullets, excluding the ``- W1:`` entry-shape example."""
    text = EVIDENCE_TEMPLATE.read_text(encoding="utf-8")
    section = text[text.index("## External-check list") :]
    end = section.find("\n## ", 1)
    if end != -1:
        section = section[:end]
    return [
        line[2 : line.index(":")]
        for line in section.splitlines()
        if line.startswith("- ") and ":" in line and not DEFINED_ID_RE.match(line)
    ]


def sections(lines: list[str]) -> list[Section]:
    """Split lines into sections; text before the first heading is dropped."""
    out: list[Section] = []
    level = 0
    heading = ""
    body: list[str] = []
    for line in lines:
        match = HEADING_RE.match(line)
        if match:
            if level:
                out.append((level, heading, body))
            level, heading, body = len(match.group(1)), line.rstrip(), []
        elif level:
            body.append(line)
    if level:
        out.append((level, heading, body))
    return out


def section_text(found: list[Section], index: int) -> str:
    """Body of section ``index`` plus the bodies of its deeper subsections."""
    level, _, body = found[index]
    parts = list(body)
    for next_level, _, next_body in found[index + 1 :]:
        if next_level <= level:
            break
        parts.extend(next_body)
    return "\n".join(parts)


def find_section(found: list[Section], prefix: str) -> str | None:
    """Text of the first section whose heading starts with ``prefix``."""
    for index, (_, heading, _) in enumerate(found):
        if heading.lower().startswith(prefix.lower()):
            return section_text(found, index)
    return None


def structure_errors(
    label: str, lines: list[str], found: list[Section], required: list[Heading]
) -> list[str]:
    """Missing headings, empty sections, and leftover placeholders."""
    errors: list[str] = []
    headings = [heading.lower() for _, heading, _ in found]
    for prefix, full in required:
        if not any(heading.startswith(prefix.lower()) for heading in headings):
            errors.append(f"{label}: missing heading: {full}")
    for index, (level, heading, body) in enumerate(found):
        if any(line.strip() for line in body):
            continue
        next_level = found[index + 1][0] if index + 1 < len(found) else 0
        if level == 1 or next_level <= level:
            errors.append(f"{label}: empty section: {heading}")
    for number, line in enumerate(lines, start=1):
        if PLACEHOLDER_RE.search(line):
            errors.append(
                f"{label}: line {number}: template placeholder still in place"
            )
    return errors


def evidence_errors(found: list[Section]) -> list[str]:
    """Each topic cites a locator or an N/C/W/P ID, or says not applicable."""
    errors: list[str] = []
    for index, (level, heading, _) in enumerate(found):
        if level != 3 or not is_topic(heading):
            continue
        text = section_text(found, index)
        if (
            NOT_APPLICABLE_RE.search(text)
            or LOCATOR_RE.search(text)
            or ID_RE.search(text)
            or SECTION_NAME_RE.search(text)
        ):
            continue
        errors.append(f"report: no locator or ID cited: {heading}")
    return errors


def derived_errors(lines: list[str]) -> list[str]:
    """Every sentence containing "derived" cites the C, W or P entry holding
    the computation. A sentence ends at ., !, ? or the line break."""
    errors: list[str] = []
    for number, line in enumerate(lines, start=1):
        if line.startswith("Key: "):
            continue
        for sentence in SENTENCE_SPLIT_RE.split(line):
            if DERIVED_RE.search(sentence) and not CWP_ID_RE.search(sentence):
                errors.append(
                    f"report: line {number}: derived number cites no C, W or P entry"
                )
    return errors


def coverage_errors(found: list[Section]) -> list[str]:
    coverage = find_section(found, "## 4.")
    if coverage is None:
        return []  # the missing heading is already reported
    return [
        f"report: Coverage is missing its '{lead}' line"
        for lead in coverage_leads()
        if f"- {lead}:" not in coverage
    ]


def ledger_errors(report_text: str, evidence_text: str) -> list[str]:
    """Every ID defined in the evidence file appears in the report (the
    "Evidence file only" line counts); every ID the report cites is defined."""
    defined = set(DEFINED_ID_RE.findall(evidence_text))
    cited = set(ID_RE.findall(_without_key_lines(report_text)))
    errors = [
        f"report: broken ledger: {entry} is defined in the evidence file and "
        "appears neither in the report nor on Coverage's 'Evidence file only' line"
        for entry in sorted(defined - cited)
    ]
    errors.extend(
        f"report: broken ledger: {entry} is cited and the evidence file never "
        "defines it"
        for entry in sorted(cited - defined)
    )
    return errors


def phrase_warnings(label: str, lines: list[str]) -> list[str]:
    """Bare 'none found' / 'not checked' / 'not applicable' without a tail."""
    return [
        f"{label}: line {number}: bare '{match.group(1)}'; add where you looked or why"
        for number, line in enumerate(lines, start=1)
        for match in BARE_PHRASE_RE.finditer(line)
    ]


def check_report(text: str, evidence_text: str | None) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for the report, and the cross-file rules."""
    lines = text.splitlines()
    found = sections(lines)
    errors = structure_errors("report", lines, found, _report_headings())
    errors.extend(evidence_errors(found))
    errors.extend(derived_errors(lines))
    errors.extend(coverage_errors(found))
    credibility = find_section(found, "### Credibility")
    if credibility is not None and not CONFIDENCE_RE.search(credibility):
        errors.append("report: Credibility states no confidence (high, medium, or low)")
    if not KEY_LINE_RE.search(text):
        errors.append("report: missing provenance key (the 'Key:' line)")
    if evidence_text is not None:
        errors.extend(ledger_errors(text, evidence_text))

    warnings = phrase_warnings("report", lines)
    bare = len(BARE_SIGNIFICANT_RE.findall(text))
    if bare:
        warnings.append(
            f"report: 'significant' appears {bare} time(s) without 'statistically'; "
            "fine in prose, wrong for a test result"
        )
    return errors, warnings


def check_evidence(text: str) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for the evidence file."""
    lines = text.splitlines()
    found = sections(lines)
    required = template_headings(EVIDENCE_TEMPLATE)
    errors = structure_errors("evidence", lines, found, required)
    external = find_section(found, "## External-check list")
    if external is not None:
        errors.extend(
            f"evidence: External-check list is missing its '{lead}' slot"
            for lead in external_check_leads()
            if f"- {lead}:" not in external
        )
    return errors, phrase_warnings("evidence", lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("report", type=Path, help="the report Markdown file")
    parser.add_argument(
        "evidence",
        type=Path,
        nargs="?",
        help="the evidence file; defaults to REPORT with .evidence.md in place of .md",
    )
    args = parser.parse_args(argv)
    evidence_path = args.evidence or args.report.with_suffix(".evidence.md")

    evidence_text: str | None = None
    errors: list[str] = []
    warnings: list[str] = []
    if evidence_path.is_file():
        evidence_text = evidence_path.read_text(encoding="utf-8")
        errors, warnings = check_evidence(evidence_text)
    else:
        errors.append(f"evidence: file not found: {evidence_path}")
    report_errors, report_warnings = check_report(
        args.report.read_text(encoding="utf-8"), evidence_text
    )
    errors = report_errors + errors
    warnings = report_warnings + warnings

    for message in errors:
        sys.stdout.write(f"error: {message}\n")
    for message in warnings:
        sys.stdout.write(f"warning: {message}\n")
    if errors:
        sys.stdout.write(f"{len(errors)} error(s)\n")
        return 1
    sys.stdout.write("ok\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 6: Run the tests until they pass**

Run: `.venv/bin/python -m pytest tests/test_check_report.py -q`
Expected: all PASS. If a structure test fails, fix the checker or the builder in the test — never weaken an assertion. Watch one known subtlety: the fixture's topic bodies must not trip the bare-phrase or placeholder rules, and `- Recalled: none; checked: the whole run.` is deliberately colon-tailed so `BARE_PHRASE_RE` stays quiet.

- [ ] **Step 7: Form and commit**

```bash
cd /home/eranr/research-vault/.worktrees/paper-critical-analysis-merge
ruff format skills/paper-critical-analysis/scripts/check_report.py tests/test_check_report.py
ruff check skills/paper-critical-analysis/scripts/check_report.py tests/test_check_report.py
mdformat --number --wrap keep skills/paper-critical-analysis/templates/report-template.md skills/paper-critical-analysis/templates/evidence-template.md
.venv/bin/python -m pytest tests/test_check_report.py -q
git add skills/paper-critical-analysis/templates skills/paper-critical-analysis/scripts tests/test_check_report.py
git commit -m "feat(skills): report and evidence templates, and the checker that reads them

The templates are the checker's single source of truth: required headings
are parsed from them, the Coverage leads from the template's own bullets,
and the nine topics from the outline between sections 3 and 4. New rules
from the merge spec: locator-or-ID per topic, the Key provenance line,
derived numbers citing their C, W or P entry, the six Coverage lines, the
mandated-check slots in the evidence file (run F: a skipped check must be
a visible hole), and the
N/C/W/P ledger closed in both directions. The passing test fixture is
built from the shipped templates through the checker's own parser.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" -- skills/paper-critical-analysis/templates skills/paper-critical-analysis/scripts tests/test_check_report.py
```

Note: mdformat may rewrap or renumber the templates; if it changes them, re-run the test suite before committing (the checker parses headings only, so formatting is safe, but verify).

______________________________________________________________________

### Task 2: The reference files

**Files:**

- Create: `skills/paper-critical-analysis/references/sources-and-venues.md`
- Create: `skills/paper-critical-analysis/references/released-artifacts.md`
- Modify: `skills/paper-critical-analysis/references/quantitative-methods.md` (append material from `skills/critical-analysis-report/references/background.md`)
- Modify: `skills/paper-critical-analysis/references/participants.md` (append fair-treatment signs from the same file)

**Interfaces:**

- Consumes: `skills/critical-analysis-report/references/background.md` (source of merged text; still present until Task 4) and the current `skills/paper-critical-analysis/SKILL.md` "Source types" subtree (lines under `#### Source types`).

- Produces: six reference files whose paths Task 3's load table and judge brief cite verbatim: `references/sources-and-venues.md`, `references/research-integrity.md`, `references/quantitative-methods.md`, `references/qualitative-methods.md`, `references/participants.md`, `references/released-artifacts.md`. No test file changes in this task; Task 3's contract tests pin the load-table paths. This task's check is mdformat + a grep.

- [ ] **Step 1: Write `references/sources-and-venues.md`**

Merged from the old SKILL.md "Source types" subtree and `background.md`'s "types of sources" section (they say the same thing; keep each fact once). Write exactly:

```markdown
# Background: sources and venues

Serves every paper: the venue slot, the related-work and reference checks, and any W entry that weighs a source. The ranking applies to the paper's own venue and to what it cites.

## Source types, by currency and review rigor

- Books — summarize the field up to roughly 13 years before publication; good for foundations; reviewed less rigorously than journals; each author biased toward one approach.
- Review articles and edited-book chapters — narrower and more current, within 5–8 years; not always reviewed as rigorously as journal articles.
- Journal articles — the primary sources, giving the results as interpreted by those who did the work; the most current formal source, appearing a few years after the work began; top journals accept as few as 10–20% of submissions after peer review.
- Proceedings — peer-reviewed, but usually shorter and less rigorously reviewed than a journal article; timely; common in applied fields.
- Technical reports — more procedural detail than a journal article, but usually not peer-reviewed.
- Preprints, electronic, and web sources — no mandatory quality control; check the author's credentials and corroborate before trusting.

## Predatory venue check

If the venue is unfamiliar, check whether it is indexed (Scopus, Web of Science, PubMed, DOAJ) and a COPE member before weighing its review rigor. Think. Check. Submit. (thinkchecksubmit.org) is the field's checklist. The check is a W entry.

## Red flags in the paper's sourcing and context

- Cherry-picked citations
- A single study in isolation, with no replication
- Contradicts the preponderance of evidence
- Press release before peer review

## Citation-index fallback

When a citation index fails, fall back in order: OpenAlex, Crossref, OpenCitations, Semantic Scholar. Each failure becomes a W entry, and any count left incomplete is labelled partial.
```

- [ ] **Step 2: Write `references/released-artifacts.md`**

Write exactly (content from the spec's Components section, expanded into working instructions):

```markdown
# Background: released code and data

Loads when the paper releases code or data. Stage 2 runs these checks; each one is recorded as a W entry.

## What to open

Analysis code, notebooks, data dictionaries, and data files. For every headline number — every number in the abstract and conclusion — find the analysis code behind it, read it, and recompute the number from the released data. Do arithmetic in code, never in prose. Compare the recomputed value with the paper's; a mismatch is a C entry as well as a W entry.

## What never to open or fetch

Credential, key, environment, and config files (`.env`, `*.pem`, `credentials.*`, tokens, API keys, private endpoints). If a repository appears to expose one, record its path only, neutrally, as an observation under Ethics — never its contents, and never test whether it works.

## How to handle data

- Download only what a recomputation needs, into the scratch folder.
- Keep aggregates only; never quote an individual row, free-text response, or identifier in any artifact the run writes.
- Never attempt re-identification. If small cell sizes, quasi-identifiers, or linkable fields make re-identification look feasible, note the risk as an observation — that is a finding about the release, not an experiment to run.
- Raw participant-level files are deleted from the scratch folder at the end of the run, and the deletion is recorded in the evidence file.

## How to record each check

One W entry per check: the claim checked; the repository or dataset (URL and commit or version); the file and the code path read; what it showed; the recomputed value beside the paper's. Usage or coverage claims in the paper are checked against the released data itself, not against the paper's description of it.
```

- [ ] **Step 3: Extend `references/quantitative-methods.md`**

Three edits, absorbing `background.md`'s "designing an experiment" and "interpreting quantitative results" sections without duplicating what the file already says (validity threats, order-of-assessment, p-value conventions, axes, factorial effects are already there).

Edit 1 — insert a new section between `## Reconstruct the design` and `## What the design can support as a causal claim`:

```markdown
## Variables

Independent: manipulated by the researcher, with several values. Dependent: measures the behavior; it states what is measured and how, with its reliability (the same result again, and the expected error) and its validity (it measures the intended thing). Control: held constant; aids replication, but over-control hurts external validity (a quiet, well-lit lab may not mirror real use). Random: varied at random, possibly within constraints, as in random assignment against bias. Confounding: changes along with the independent variable. A sound paper defines its variables explicitly enough to replicate; some (visual complexity, stress) resist definition.
```

Edit 2 — in `## Design types`, replace the two existing bullets and their lead-in line ("Between-subjects, matched-groups, factorial, converging-series, and:") with:

```markdown
- Between-subjects — each participant sees one value; no carry-over, learning, or fatigue, and sometimes the only option (age); needs more participants and equivalent groups (random assignment).
- Within-subjects — exposure itself changes behavior (learning, fatigue, maturation). Mitigated by counterbalancing or, with many values, a Latin square (each value appears in, before, and after every position equally often; the participant count is a multiple of the value count); counterbalancing leans on the symmetrical-transfer assumption, so ask whether that is reasonable for this task.
- Matched groups — a pretest on measures expected to affect behavior; the study runs longer, and the pretest may itself affect performance.
- Single-variable, two-level (experimental vs. control) — easy to interpret; says nothing about whether a numeric relationship is linear. Multi-level shows the relationship's shape at the cost of more time, participants, and analysis.
- Factorial — crosses factors; reveals interactions and gives more precise, more generalizable results; mixed when some factors are within- and some between-subjects; harder to interpret once interactions appear.
- Converging series — several experiments on one question, each fixing a level for the next or eliminating hypotheses; flexible, but interactions across experiments are hard to assess, and there is no random assignment between experiments.
```

Edit 3 — in `## Reading the numbers`, add these bullets after the existing three:

```markdown
- Histograms show whether the data looks normal enough for the test used.
- Bars for a categorical independent variable, lines for a numeric one; scatterplots show whether two variables are related, with a correlation coefficient for strength.
- Crossover interactions may show no main effect.
- Two misreadings: a non-significant difference does not mean the values are equal, and "significant" without "statistically" conflates statistical with practical significance.
```

- [ ] **Step 4: Extend `references/participants.md`**

Append at the end of the file:

```markdown
## Signs of fair treatment

The researcher holds power, participants may feel evaluated, and fairness is the researcher's responsibility. Signs to look for in what the paper reports: sessions on time and prepared; data kept confidential and never released identifiably; interactions limited to the study; participants made comfortable; participants' time spent as freely as the design allows; benefits not over-claimed.
```

- [ ] **Step 5: Check nothing routes to `background.md`, form, test**

```bash
cd /home/eranr/research-vault/.worktrees/paper-critical-analysis-merge
grep -rn "background.md" skills/paper-critical-analysis/   # expected: no output
mdformat --number --wrap keep skills/paper-critical-analysis/references/*.md
.venv/bin/python -m pytest tests -q -n auto
```

Expected: grep silent; suite green (nothing yet reads the new files).

- [ ] **Step 6: Commit**

```bash
git add skills/paper-critical-analysis/references
git commit -m "feat(skills): merged reference files for the unified critique skill

sources-and-venues.md combines the two skills' source-type sections and
gains the citation-index fallback order; released-artifacts.md is new per
the merge spec (what to open, what never to fetch, aggregate-only data
handling, W-entry recording); quantitative-methods.md absorbs the
experiment-design and result-interpretation background; participants.md
absorbs the fair-treatment signs.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" -- skills/paper-critical-analysis/references
```

______________________________________________________________________

### Task 3: SKILL.md, the three briefs, and the contract tests

This is one task because SKILL.md and the briefs are a single contract surface — the contract tests cross-check them, so splitting would leave the suite red between tasks.

**Files:**

- Modify: `skills/paper-critical-analysis/SKILL.md` (full rewrite)
- Modify: `skills/paper-critical-analysis/prompts/judge.md`
- Create: `skills/paper-critical-analysis/prompts/edit.md`
- Modify: `skills/paper-critical-analysis/prompts/verify.md` (full rewrite)
- Delete: `skills/paper-critical-analysis/prompts/extract.md`
- Modify: `tests/test_paper_critical_analysis_skill.py` (full rewrite)

**Interfaces:**

- Consumes: Task 1's template paths and heading texts (`templates/report-template.md`, `templates/evidence-template.md`, `scripts/check_report.py`, the `Key:` line, the Coverage leads, the `- N1:` ledger shape) and Task 2's reference paths.

- Produces: the dispatcher contract later surfaces rely on — SKILL.md's locator-convention section (filled verbatim into `{LOCATOR_CONVENTION}`), the load table, the stage headings `## Stage 0 — Settle conditions` … `## Stage 7 — Verify`, and the three briefs with the placeholder names pinned in Global Constraints.

- [ ] **Step 1: Rewrite the contract tests (failing first)**

Replace the whole of `tests/test_paper_critical_analysis_skill.py` with:

````python
"""The paper-critical-analysis skill's briefs are the contract its subagents obey.

SKILL.md points at them and does not restate them (the judging contract lives
in prompts/judge.md, the editing contract in prompts/edit.md, the verification
contract in prompts/verify.md), so the surfaces can drift silently: an edit to
a dimension name, a placeholder, or a reference path in one file leaves the
others stale, and nothing at runtime complains. These tests are that complaint.
"""

import re
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[1] / "skills" / "paper-critical-analysis"
SKILL_MD = SKILL_DIR / "SKILL.md"
BRIEFS = ("judge.md", "edit.md", "verify.md")

# A bolded dimension name opening a dimension bullet: "- **Importance** — ..."
_DIMENSION_BULLET = re.compile(r"^- \*\*([A-Z][a-z]+)\*\* —", re.MULTILINE)

NINE = (
    "Importance",
    "Credibility",
    "Novelty",
    "Applicability",
    "Generalizability",
    "Scalability",
    "Assumptions",
    "Readability",
    "Ethics",
)
# A brace placeholder a brief expects the dispatcher to fill: "{PAPER_PATHS}"
_PLACEHOLDER = re.compile(r"\{([A-Z_]+)\}")
# A load-table or brief reference to a shipped file, e.g. `references/participants.md`
_SHIPPED_PATH = re.compile(r"`((?:references|prompts|templates|scripts)/[\w./-]+)`")


def _skill_text() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


def _brief(name: str) -> str:
    return (SKILL_DIR / "prompts" / name).read_text(encoding="utf-8")


def test_the_judge_brief_owns_the_nine_dimensions_in_order():
    """The dimension bullets live in the brief, because the judge subagent
    cannot read SKILL.md. Renaming or reordering one silently changes every
    report."""
    section = _brief("judge.md")
    section = section[section.index("## The nine dimensions") :]
    assert tuple(_DIMENSION_BULLET.findall(section)) == NINE


def test_the_skill_lists_the_same_nine_in_the_same_order():
    """SKILL.md keeps the names so the report outline is legible, and the brief
    keeps what each asks. Two surfaces, one order."""
    text = _skill_text()
    sentence = text[text.index("The nine, in order:") :].split("\n", 1)[0]
    found = tuple(n for n in re.findall(r"[A-Z][a-z]+", sentence) if n in NINE)
    assert found == NINE, f"SKILL.md lists {found}"


def test_the_report_template_carries_the_same_nine_as_headings_in_order():
    """The checker takes its required headings from the template, so the
    template is where a renamed dimension would strand every future report."""
    template = (SKILL_DIR / "templates" / "report-template.md").read_text(
        encoding="utf-8"
    )
    body = template[template.index("## 3.") : template.index("## 4.")]
    found = tuple(
        line[4:].strip() for line in body.splitlines() if line.startswith("### ")
    )
    assert found == ("Verdicts", *NINE)


def test_the_judge_brief_asks_for_every_subsection_it_defines():
    """The brief's return contract and its dimension list are separate
    passages; when they disagree the subagent leaves a slot empty and nothing
    errors."""
    brief = _brief("judge.md")
    listed = brief[
        brief.index("## What you return") : brief.index("Each subsection opens")
    ]
    for dimension in NINE:
        assert dimension in listed, (
            f"judge.md never asks for the {dimension} subsection"
        )


@pytest.mark.parametrize("brief_name", BRIEFS)
def test_every_brief_placeholder_is_documented(brief_name):
    """A placeholder the brief never explains is one a dispatcher leaves
    unfilled, and the subagent then reads a literal brace as its input."""
    brief = _brief(brief_name)
    fenced = brief[brief.index("```") : brief.rindex("```")]
    prose = brief.replace(fenced, "")
    for placeholder in sorted(set(_PLACEHOLDER.findall(fenced))):
        documented = (
            f"{{{placeholder}}}" in prose
            or placeholder.lower().replace("_", " ") in prose.lower()
        )
        assert (
            documented
            or f"{{{placeholder}}}" in _skill_text()
            or _names_it(placeholder)
        ), f"{brief_name} uses {{{placeholder}}} and nothing says what fills it"


def _names_it(placeholder: str) -> bool:
    """The skill's dispatch line may name a placeholder in words rather than
    in braces ("the evidence file" for EVIDENCE_PATH)."""
    head = placeholder.lower().split("_")[0]
    return head in _skill_text().lower()


@pytest.mark.parametrize("brief_name", ("judge.md", "verify.md"))
def test_every_brief_that_handles_locators_is_given_the_convention(brief_name):
    """The judge writes Locator fields and the verifier checks them, and each
    runs in a subagent that cannot read SKILL.md where the convention is
    defined. The verifier shipped without it once: it then checked locators
    against a reading of its own and reported correct items as failures. The
    editor only preserves locators verbatim, so it needs no convention."""
    assert "{LOCATOR_CONVENTION}" in _brief(brief_name), (
        f"{brief_name} handles locators and is never handed the convention"
    )


@pytest.mark.parametrize("brief_name", BRIEFS)
def test_the_skill_dispatches_every_brief_it_ships(brief_name):
    """A brief nothing dispatches is dead weight, and a stage that names no
    brief has lost its contract."""
    assert f"prompts/{brief_name}" in _skill_text()


def test_no_retired_brief_survives():
    """Fan-out is a spec non-goal; the extractor brief went with it."""
    assert not (SKILL_DIR / "prompts" / "extract.md").exists()


STAGES = (
    "## Stage 0 — Settle conditions",
    "## Stage 1 — Read into the evidence file",
    "## Stage 2 — Check exhaustively",
    "## Stage 3 — Judge",
    "## Stage 4 — Write",
    "## Stage 5 — Edit",
    "## Stage 6 — Check",
    "## Stage 7 — Verify",
)


def test_the_stages_run_in_order_and_none_went_missing():
    """The stages were renumbered in the merge; a half-finished renumbering
    leaves the file pointing at stages that moved."""
    text = _skill_text()
    seen = []
    for heading in STAGES:
        assert heading in text, f"{heading!r} is gone from SKILL.md"
        seen.append(text.index(heading))
    assert seen == sorted(seen), "the stage headings are out of run order"
    assert "Eight stages" in text, (
        "the file never tells the reader how many stages there are"
    )


def test_the_skill_does_not_restate_the_judging_contract():
    """The contract lives in prompts/judge.md precisely because two copies
    drift. A bolded field name reappearing in SKILL.md is that drift starting
    again: the skill may name a field in prose, never re-specify the set."""
    text = _skill_text()
    for phrase in ("**Observation**", "**Why it matters**", "**Evidence**"):
        assert phrase not in text, (
            f"SKILL.md restates {phrase!r}, which prompts/judge.md owns"
        )


def test_every_ledger_the_evidence_file_defines_is_admissible_to_the_judge():
    """Stage 3 is the discussion's only source of findings, so a ledger the
    judge may not cite reaches the report only through Context, where a reader
    takes it for scene-setting. The external-check list shipped that way once."""
    sentence = _brief("judge.md")
    sentence = sentence[sentence.index("**Admissible evidence**") :].split("\n", 1)[0]
    template = (SKILL_DIR / "templates" / "evidence-template.md").read_text(
        encoding="utf-8"
    )
    for prefix in "NCW":
        assert f"- {prefix}1:" in template, (
            f"evidence-template.md shows no {prefix}1 entry shape"
        )
        assert f"{prefix}-" in sentence or f"{prefix}1" in sentence, (
            f"the evidence file defines {prefix} entries and the judge may not "
            "cite them"
        )


def test_the_kind_values_match_the_count_the_brief_states():
    """The brief states the count and then lists the values, so a value added
    or removed leaves the number stale."""
    brief = _brief("judge.md")
    stated = re.findall(r"Kind is one of (?:the )?([a-z]+)", brief)
    assert stated, "the brief never states how many Kind values there are"
    assert len(set(stated)) == 1, f"the brief states the Kind count as {stated}"
    word_numbers = {"three": 3, "four": 4, "five": 5, "six": 6, "seven": 7}
    start = brief.index("Kind is one of", brief.index("Kind is one of") + 1)
    listed = re.findall(
        r"^- ([A-Z][^—]*)—",
        brief[start : brief.index("Every quote", start)],
        re.MULTILINE,
    )
    assert len(listed) == word_numbers[stated[0]], (
        f"the brief lists {len(listed)} Kind values and calls them {stated[0]}"
    )


def test_every_section_the_judge_returns_has_a_destination():
    """The judge returns the nine subsections and a Recalled section, and
    stage 3's screen drops what it does not recognise. A section the brief
    asks for and the skill never routes is thrown away with the run's
    disclosure in it."""
    brief = _brief("judge.md")
    returned = brief[brief.index("## What you return") : brief.index("## Delegation")]
    assert "Recalled" in returned, "judge.md no longer asks for the Recalled section"
    text = _skill_text()
    stage_3 = text[text.index(STAGES[3]) : text.index(STAGES[4])]
    assert "Recalled" in stage_3, (
        "stage 3 never says what becomes of the Recalled section"
    )


def test_the_paper_type_bar_covers_the_spec_types():
    """The spec names seven paper types; a type with no row is judged against
    somebody else's bar."""
    brief = _brief("judge.md")
    bar = brief[brief.index("## The bar") : brief.index("## The nine dimensions")]
    for paper_type in (
        "Empirical",
        "Theoretical",
        "Survey",
        "Systems",
        "Position",
        "Replication",
        "Negative results",
    ):
        assert paper_type in bar, f"the bar table has no {paper_type} row"


def test_every_shipped_path_the_skill_and_briefs_cite_exists():
    """The load table and the briefs route by repository-relative path; a
    renamed reference file strands the stage that loads it."""
    missing = {
        f"{owner}: {path}"
        for owner, text in (
            ("SKILL.md", _skill_text()),
            *((name, _brief(name)) for name in BRIEFS),
        )
        for path in _SHIPPED_PATH.findall(text)
        if not (SKILL_DIR / path).exists()
    }
    assert not missing, f"cited but not shipped: {sorted(missing)}"


def test_every_reference_file_is_reachable_from_the_load_table():
    """A reference file the load table never assigns is dead weight no stage
    walks and no brief hands the judge."""
    text = _skill_text()
    table = text[text.index("## What the paper loads") :]
    table = table.split("## Stage", 1)[0]
    for path in sorted((SKILL_DIR / "references").glob("*.md")):
        assert f"references/{path.name}" in table, (
            f"references/{path.name} is shipped and the load table never "
            "assigns it"
        )
````

- [ ] **Step 2: Run them to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_paper_critical_analysis_skill.py -q`
Expected: FAIL — `edit.md` missing, stage headings missing, extract.md still present, etc.

- [ ] **Step 3: Rewrite `prompts/judge.md`**

Keep the existing file's framing and dimension bullets; apply exactly these changes:

1. Replace the `## Inputs` block of the fenced brief with:

```markdown
## Inputs

- Paper: {PAPER_PATHS} — the paper and every appendix and supplement stage 0 counted as the paper — and {PAGE_RENDERS} (images of pages carrying figures, tables or equations; "none" if none).
- Evidence file: {EVIDENCE_PATH} — identity, section map, promises, numbered claims, the not-stated list (N1, N2, …), the inconsistency list (C1, C2, …) with its reconciliation log, and the external-check list (W1, W2, …), each W entry a fact outside the paper with the source that settled it, including the related works read and the released-artifact checks.
- Background files, read where a dimension names one: {REFERENCE_PATHS}. A dimension bullet names these by repository-relative path; resolve each against this list.
```

2. Rename the `## Location convention` heading to `## Locator convention` and its placeholder to `{LOCATOR_CONVENTION}`; rename the point field `**Location**` to `**Locator**`, and in the worked example change `**Location**: Methods, paragraph 3 (p. 4).` to `**Locator**: Section 4 (Methods), p. 4.` and its Evidence line from `Methods para 3; Table 2; N7.` to `Section 4; Table 2; N7.`

3. Rename the field `**Evidence or criterion**` to `**Evidence**` everywhere (field list, worked example), and reword the admissibility sentence to: `**Admissible evidence** is a locator in the paper, a numbered N-, C- or W- entry, or a numbered claim from the evidence file. Nothing else is admissible: a background-file criterion may ride alongside an admissible item but never stands in for one. A point with nothing admissible in its Evidence field is not returned.` (Keep it one paragraph so the contract test's single-line read still works — the test reads to the first newline, so keep at least the `**Admissible evidence**` sentence with `N-`, `C-`, `W-` on that first line.)

4. In `## What you return`, replace the verdict sentence's "Location" wording accordingly ("with the Locator it bears on" in the Recalled line).

5. In `## The bar`, add two table rows after `**Position**`:

```markdown
| **Replication** | Fidelity to the original design, statistical power, deviations declared, and an honest comparison of outcomes |
| **Negative results** | Design sensitivity: whether this design could have detected the effect had it been there |
```

And in the prose line below the table, drop "a replication to fidelity rather than novelty; a negative-results paper to its design rather than its direction;" (those live in the table now), keeping the rest.

6. In the `- **Credibility**` dimension bullet, append before the final period: `; venue rigor and source quality in `references/sources-and-venues.md`; and, where code or data are released, the recomputation W entries from `references/released-artifacts.md\`\`.

7. Replace the footer line below the fence with: `` `{LOCATOR_CONVENTION}` is filled verbatim from SKILL.md's "Locators" section. ``

8. Update the header line above the fence from "Stage 3 brief" context if it names stage numbers (keep "# Stage 3 brief" — the stage number is unchanged).

- [ ] **Step 4: Write `prompts/edit.md`**

Create with exactly this content:

````markdown
# Stage 5 brief

Sent verbatim to the stage 5 editor subagent, with the placeholders filled. It is the subagent's whole context.

```
You are editing a critical-analysis report for one reader: someone deciding whether to trust and use the paper it describes. You return a change list; you edit no file.

## Inputs

- Report: {REPORT_PATH}
- Evidence file: {EVIDENCE_PATH} — read only, for checking that a claim you touch keeps its IDs resolvable and for naming the section a moved detail lands in.

## The invariant

Every change keeps the claim and its strength: its qualifiers, numbers, locators, N/C/W/P IDs, and provenance marks (locators, (W12), [inferred], "derived"). A sentence that fails the relevance or no-op test is deleted whole, never trimmed to a weaker version of itself. You add no finding and no fact.

## Scope

The structural and stylistic passes work on sections 1–3 only. The front matter (the citation block and the Key line), the Verdicts block, and Coverage take the copy pass alone: their one-line repetitions and fixed lead words are the outline's, not padding — a verdict appears both in the Verdicts block and opening its topic by design.

## Your passes, in order (Professional Editorial Standards 2024, paraphrased: structural, then stylistic, then copy)

Structural:

- Delete repetitive, irrelevant and superfluous sentences.
- Keep each meaning in one place, under the topic it bears on most, with a one-line cross-reference where another topic needs it.
- Move detail behind its ID into the evidence file: derivations, number lists and source quotes go there; the claim, its locators and its IDs stay in the report. Name the evidence-file section each moved item lands in.
- Recast number-heavy prose as a table.
- Put the most relevant material first within each section.

Stylistic:

- Tighten passing sentences: omit needless words, prefer active and positive forms, use concrete language.
- Remove AI-writing patterns: puffery, empty "-ing" phrases, promotional adjectives, stock vocabulary, scattered bold.

Copy:

- Make terms, numbers and abbreviations consistent across the report.
- Flag, without fixing, any generalization that has no citation and any number that does not add up.

## What you return

A numbered change list, and nothing else. Each item:

- **Where**: the section and enough quoted text to find the place.
- **Before**: the text as it stands (for a deletion or move, the whole sentence or block).
- **After**: the replacement text; "delete" for a deletion; for a move, the evidence-file section it lands in and the one-line claim that stays.
- **Test**: which rule above the item applies (repetition, one-place, move-detail, table, order, tighten, AI-pattern, consistency, flag).

Flag-only items (the copy pass's uncited generalizations and numbers that do not add up) go in a separate final section headed "Flags", one line each.

End with two lines: the report's word count as you received it, and as it would stand with every item applied.
```
````

- [ ] **Step 5: Rewrite `prompts/verify.md`**

Replace the whole file with:

````markdown
# Stage 7 brief

Sent verbatim to the stage 7 verifier subagent, with the placeholders filled. It is the subagent's whole context.

```
You are checking a report against the paper it describes and against the sources it cites. You form no opinion of the paper, you create no files, and you do not rewrite the report.

## Inputs

- Paper: {PAPER_PATHS} — the paper and every appendix and supplement — and {PAGE_RENDERS} (images of pages carrying figures, tables or equations; "none" if none).
- Report: {REPORT_PATH}
- Evidence file: {EVIDENCE_PATH} — the W entries you re-open, and the pruning record holding the editor's change list.

## Locator convention

{LOCATOR_CONVENTION}

Report against this convention, not against a reading of your own.

## What you check

1. Every locator, quote and number the report attributes to the paper: find it in the paper. An item passes when the locator resolves to text that says what the report says it says, the quote matches the paper verbatim, and the number appears at the stated place. A number the report marks "derived" is checked against the C, W or P entry it cites, not recomputed.
2. Every W entry the report cites: re-open it at its URL, or at its saved copy in the scratch folder when the URL fails, and check that the source says what the entry says it said.
3. Every applied change-list item: compare After with Before for lost or added meaning — a dropped qualifier, a strengthened claim, a changed number; for a move, check the one-line claim that stayed against what moved.

## Delegation

Do this work yourself, and spawn no subagent: this pipeline already fills every seat the critique gets, and an agent you spawned would re-read the skill and fan out again.

## What you return

The items that failed, and nothing else. Each item:

- the report line (quote enough to identify it),
- what the report claims,
- the locator, W entry, or change-list item you checked,
- what you found there, or "not found".

End with one line per category: locators/quotes/numbers checked and failed; W entries checked and failed; change-list items checked and failed. If nothing failed, return those three lines alone.
```

`{LOCATOR_CONVENTION}` is filled verbatim from SKILL.md's "Locators" section.
````

- [ ] **Step 6: Delete the extractor brief**

```bash
git rm skills/paper-critical-analysis/prompts/extract.md
```

- [ ] **Step 7: Rewrite `SKILL.md`**

Replace the whole file with (frontmatter first, then body; the locator section, conditions table, load table and stage text below are the normative copies — the spec's tables expanded into instructions):

```markdown
---
name: paper-critical-analysis
description: Critical analysis of one research paper, for a reader deciding whether to trust and use it rather than an editor deciding whether to publish it. Reads the paper with its supplements and released code and data, checks every number exhaustively, judges nine dimensions in a fresh context, then edits, machine-checks and verifies. Writes a report plus an evidence file.
disable-model-invocation: true
---

# Critiquing a paper

The report is the one the critical-analysis guide asks a human to write: context, summary, and a discussion of importance, credibility, novelty, applicability, generalizability, scalability, assumptions, readability and ethics. The process is built around the failures agents actually show — satisficing instead of exhaustive checking, anchoring on the authors' framing, recall presented as evidence, padding kept by its own author, locator slips — so it does not follow the guide's three human reading passes. One depth, no fast or deep mode; on a 33-page paper expect about 8M fresh tokens and about 2 hours.

## Input and output

Input: one paper, named by the first argument. The optional second argument names the output folder; the default is `critical-analysis-<paper-slug>/` beside the paper, where `<paper-slug>` is the lowercased name the paper is known by (its system name, or the first distinctive title word). You need the full text: given only an abstract, citation, or DOI, obtain it first or stop and say so.

The run writes four things into the output folder, and nothing anywhere else — scratch work included:

- `critical-analysis-<paper-slug>.md` — the report, in `templates/report-template.md`'s outline.
- `critical-analysis-<paper-slug>.evidence.md` — the audit trail, in `templates/evidence-template.md`'s sections, each filled during the stage that produces it.
- `critical-analysis-<paper-slug>.draft.md` — the report as it stood before stage 5.
- `<paper-slug>-work/` — fetched sources, page images, scripts, and data downloaded for recomputation. Raw participant-level data is deleted from it at the end of the run.

Eight stages, 0–7, every one on every paper. Each ends on a completion bar, recorded in the evidence file's stage log as it is met; an interrupted run resumes from the log.

## Rules

- **Provenance.** The reader must be able to tell apart what the paper says, what an outside source says, and what the writer infers. The report's `Key:` line states the marks: a locator cites the paper; a W ID such as (W12) cites an outside source through the evidence file; [inferred] marks the writer's own reasoning; a number marked "derived" cites the C, W or P entry holding its computation; recalled knowledge appears only under Coverage.
- **Nothing silent.** Write `none found; checked: <where>`, `not checked: <reason>` or `not applicable: <reason>` rather than leaving a gap; a section whose stage has not run yet reads `pending: stage <n>`.
- **Integrity.** Concerns are neutral observations, given with their benign explanations; never accusations.
- **Write scope.** Every file the run creates goes in the output folder.
- **Quotes.** Short ones only; never reproduce passages.

## Locators

A locator is a section, page, figure, table, equation, footnote or reference number, exactly as the paper numbers it: `Section 4.2`, `p. 7`, `Figure 3`, `Table 2`, `Equation 5`, `footnote 4`, `reference [23]`. A named part of the front matter — title, abstract, author block, keywords — is a locator too. `whole paper` marks something absent throughout. No paragraph counting.

## What the paper loads

Each row sets both the file stage 2 walks and the path stage 3's brief hands the judge, so a row that does not fire puts its file out of the judge's reach too.

| Condition                                                                                          | File                                 |
| -------------------------------------------------------------------------------------------------- | ------------------------------------ |
| Every paper                                                                                        | `references/sources-and-venues.md`   |
| Every paper                                                                                        | `references/research-integrity.md`   |
| The paper reports a quantity it measured, or a statistic it computed from data                     | `references/quantitative-methods.md` |
| The paper collects or analyses qualitative data — interviews, field notes, documents, cases, media | `references/qualitative-methods.md`  |
| People took part in the research                                                                   | `references/participants.md`         |
| The paper releases code or data                                                                    | `references/released-artifacts.md`   |

## Stage 0 — Settle conditions

Settle every row before reading, and record each under Conditions in the evidence file; a condition discovered mid-run costs a stage its work. Create the output folder, the evidence file from `templates/evidence-template.md`, and the scratch folder first. Save every fetched source to the scratch folder as it arrives.

| Condition                           | What it changes                                                                                                                                                                                                                          |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| What counts as the paper            | The body, appendices and supplements, plus any supplied file the paper names as holding its content (for example a taxonomy in the repository it cites). Any other supplied file is an outside source, entering only through W entries. |
| The Read tool cannot render the PDF | Extract text with PyMuPDF, pypdf or pdftotext, and render every page carrying a figure, table or equation to an image in the scratch folder. With no tool available, stop and ask for the text.                                         |
| Web access                          | Probe by fetching one known-good record, such as the Crossref entry for a DOI the paper cites; retry once on a network error. If the probe fails or is refused, stop and report why — the skill does not run without the web.           |
| Released code or data               | Load `references/released-artifacts.md`; stage 2 checks them.                                                                                                                                                                            |
| The paper runs past 100 pages       | Read in chunks, writing the evidence file after each chunk.                                                                                                                                                                              |

**Done when:** every row is settled and recorded, and the probe passed.

## Stage 1 — Read into the evidence file

Read everything stage 0 counted as the paper, once and in full, viewing every figure and table as an image. The evidence file is the working memory — fill it as you go rather than holding the paper in context: identity (confirmed against the request; wrong paper: stop and say what you have) and section map; promises 1–5; every principal claim with its `Needed:` line; key quotes and numbers with their locators; terms you had to look up, which stage 2 settles as W entries. Classify the method family from the method menu below and record which background files the load table assigns.

**Done when:** every page has been read once, the identity is confirmed against the request, and every principal claim carries a `Needed:` line.

## Stage 2 — Check exhaustively

The deepest findings come only from exhaustive reconciliation and artifact checks; depth here is the point, not a cost to manage.

- **N list:** every item the report will need that the paper does not give. Start from the `Needed:` lines, then walk the assigned background files.
- **C list:** every place two locations in the paper conflict. Reconcile every reported result in the abstract and text — statistic, count, percentage, effect size — against the tables, figures and supplements, and every percentage, sum and effect size against the numbers it rests on. Do arithmetic in code, and keep the reconciliation log in the evidence file.
- **W list:** one entry per outside check — the claim checked, the source, its URL and saved copy, and what the source said. The checks:
  - venue rigor and the authors' previous work (`references/sources-and-venues.md`);
  - reference counts, tree backward and tree forward;
  - 3–5 related works, read in full where openly available and as abstracts otherwise: the work the paper builds on most; the primary source behind its load-bearing outside claim; its closest prior or concurrent work that it does not cite; any other work the argument depends on;
  - every concept the paper uses without defining;
  - if code or data are released, the analysis code behind each headline number — every number in the abstract and conclusion — with those numbers recomputed from the released data (`references/released-artifacts.md`).
  - When a citation index fails, fall back in order: OpenAlex, Crossref, OpenCitations, Semantic Scholar. Each failure becomes a W entry, and any count left incomplete is labelled partial.

Each mandated check above fills its fixed slot in the evidence file's External-check section with the W IDs that discharged it or `not checked: <reason>` — the checker reports an unfilled slot, so a skipped check is a hole, not a silence.

**Done when:** every `Needed:` line is resolved to an entry or to evidence; every number is reconciled or entered in C; every Context question is answered or marked `not checked: <reason>`; every mandated-check slot is filled; every released artifact relevant to a headline number has been examined.

## Stage 3 — Judge

**Fresh context, required.** Run one subagent whose whole context is `prompts/judge.md` with its placeholders filled: the paper and its supplements, the page images, the evidence file, the Locators section above (verbatim), and the background file paths the load table assigns. Not the conversation that did the reading — judgment in a fresh context, bound to citable evidence, is better calibrated than judgment in the context that read the paper. That brief is the judging contract; edit it there, not here.

It returns the nine subsections and a Recalled section. The nine, in order: Importance, Credibility, Novelty, Applicability, Generalizability, Scalability, Assumptions, Readability and Ethics. Screen the return: drop any point whose Evidence field cites nothing admissible (the brief defines admissible), log the dropped count, assign P IDs to the kept points, and record them with the Recalled lines under Judge points in the evidence file. The Recalled lines surface later as Coverage's `Recalled:` entries, never as findings.

**Done when:** all nine subsections and the Recalled section are returned, and every kept point carries admissible evidence under a P ID.

## Stage 4 — Write

Build Context and Summary from the evidence file, going back to the paper only for a slot it does not cover. Write the critical discussion in prose: the Verdicts block first, then the nine topics, placing every P point under the topic it bears on most; points may merge into paragraphs as long as each keeps its locators and IDs. Then write Coverage, with `Verification: pending: stage 7`; every N, C, W or P ID the report's body does not cite goes on Coverage's `Evidence file only:` line — the checker closes that ledger. There is no length limit at this stage. Save the result as the report, and copy it to the draft path — the draft is what stage 5 is measured against.

**Done when:** every P point is in the report, every heading in `templates/report-template.md` is filled, and the draft is saved.

## Stage 5 — Edit

**Fresh context, required** — an author reviewing its own text keeps everything. Run one subagent whose whole context is `prompts/edit.md` with its placeholders filled: the report and the evidence file, which it reads only. It returns a change list; apply or reject each item yourself, recording every disposition with its reason, and the before-and-after word counts, under Pruning record in the evidence file. Its Flags section (uncited generalizations, numbers that do not add up) is yours to settle too: fix each flag or move it to Coverage's `For the reader to double-check:` line. The invariant is the brief's: every applied change keeps the claim, its strength, its qualifiers, numbers, locators, IDs and provenance marks.

**Done when:** every change-list item is applied or rejected with a reason, and the word counts are logged.

## Stage 6 — Check

Run `python3 scripts/check_report.py <report>` — the path is relative to this skill's directory; the checker finds the evidence file beside the report. The templates are its single source of truth: it reads required headings from `templates/report-template.md` and `templates/evidence-template.md`, and fails on a missing heading, a leftover placeholder, a topic with no locator or ID, a Credibility section stating no confidence, a missing Coverage line, a "derived" number citing no C, W or P entry, a missing provenance key, an unfilled mandated-check slot, or a broken N/C/W/P ledger. Fix the report, not the checker.

**Done when:** the checker reports no errors.

## Stage 7 — Verify

**Fresh context, required** — a verifier holding the reasoning behind a locator is no longer checking it. Run one subagent whose whole context is `prompts/verify.md` with its placeholders filled: the paper and its supplements, the page images, the report, the evidence file, and the Locators section above (verbatim). It checks every locator, quote and number against the paper, re-opens every W entry the report cites, and compares every applied rewording with its original for meaning drift; it returns failures only, with the counts checked.

Fix, drop, or move each returned item to Coverage; record the dispositions under Verifier list in the evidence file; update Coverage's `Verification:` line with the counts; run the checker again. Then delete raw participant-level data from the scratch folder and record what was deleted under Deletions.

**Done when:** every verifier item has a disposition, the checker is clean, and the deletion is recorded.

## Method menu

- **Experimental method** (quantitative) — random assignment supports a causal claim; every other route to one is ranked in `references/quantitative-methods.md`.
- **Correlational observation** (quantitative) — shows association, not cause.
- **Surveys** (quantitative) — self-report only, no direct observation.
- **Archival research** (quantitative) — relationships between variables, not causes; the records may be unreliable. Meta-analyses and systematic reviews (most widely via PRISMA) are archival research over publications.
- **Qualitative designs** — inductive studies, ethnographies, naturalistic observation, case histories; the traditions, and what each should report, in `references/qualitative-methods.md`.

A paper fitting no family is classified by its paper type — empirical, theoretical, survey, systems, position, replication, or negative results — and the family of its evaluation, if it has one, is named.
```

- [ ] **Step 8: Run the contract tests until green, then the whole suite**

Run: `.venv/bin/python -m pytest tests/test_paper_critical_analysis_skill.py tests/test_check_report.py -q`
Expected: PASS. Then `.venv/bin/python -m pytest tests -q -n auto` — expected: PASS (the old `critical-analysis-report` skill still ships and still satisfies `test_skill_contracts.py`; its deletion is Task 4).

Known traps if something fails:

- `test_every_brief_placeholder_is_documented` resolves `{PAPER_PATHS}` via the word "paper" in SKILL.md ("paper" appears — fine); `{EVIDENCE_PATH}` via "evidence"; `{REFERENCE_PATHS}` via "reference"; `{PAGE_RENDERS}` needs "page" in SKILL.md (stage 0 has "page carrying a figure") — all satisfied by the SKILL.md text above; don't reword those phrases away.

- `test_the_skill_does_not_restate_the_judging_contract` means SKILL.md must never bold **Observation**, **Why it matters**, or **Evidence** — the SKILL.md text above doesn't; keep it that way when editing.

- `LOCATOR_CONVENTION` is filled from the `## Locators` section verbatim; both judge.md and verify.md footers/preambles must say so in those words ("filled verbatim from SKILL.md's "Locators" section").

- If `tests/test_skill_contracts.py::test_recognizable_check_id_enumerations_name_only_ids_the_code_files` trips on the new SKILL.md, the N1/C1/W1/P1 ledger tokens are the likely cause — reword the SKILL.md phrase that reads as a check-id enumeration; don't touch that test.

- [ ] **Step 9: Form and commit**

```bash
ruff check tests/test_paper_critical_analysis_skill.py && ruff format tests/test_paper_critical_analysis_skill.py
mdformat --number --wrap keep skills/paper-critical-analysis/SKILL.md skills/paper-critical-analysis/prompts/judge.md skills/paper-critical-analysis/prompts/edit.md skills/paper-critical-analysis/prompts/verify.md
.venv/bin/python -m pytest tests -q -n auto
git add skills/paper-critical-analysis/SKILL.md skills/paper-critical-analysis/prompts tests/test_paper_critical_analysis_skill.py
git commit -m "feat(skills): paper-critical-analysis runs the eight-stage merged process

SKILL.md carries stages 0-7 with completion bars, the conditions table,
the six-row load table, the locator convention (no paragraph counting),
and the output-folder contract. The judge brief gains the evidence file
as its input, the seven-type bar, and the Locator field; the editor brief
is new (PES 2024 passes, change-list return, meaning-preserving
invariant); the verifier gains W re-opening and change-list drift checks.
The extractor brief is deleted with fan-out. Contract tests rewritten for
the new surfaces.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" -- skills/paper-critical-analysis/SKILL.md skills/paper-critical-analysis/prompts tests/test_paper_critical_analysis_skill.py
```

______________________________________________________________________

### Task 4: Retire critical-analysis-report and update the repo surfaces

**Files:**

- Delete: `skills/critical-analysis-report/` (whole directory, via `git rm -r`)
- Modify: `tests/test_skill_contracts.py:26-40` (ENTRY_SKILLS entry + stale comment)
- Modify: `README.md:86-87` (merge the two flow rows)
- Modify: `ATTRIBUTION.md` (merged-material credit + editor sources)
- Modify: `docs/research/2026-09-20-paper-critical-analysis-evals/README.md` (append merged-skill section)

**Interfaces:**

- Consumes: Task 2 and Task 3 complete (nothing may still read `background.md` or the old checker — the Task 2 grep proved it for the skill; this task re-proves repo-wide).

- Produces: a repo whose only critique skill is `paper-critical-analysis`. `tests/test_templates.py` needs no repin: the vault-template row reads "write an in-depth critical analysis report of one paper", which describes the merged skill unchanged. `docs/agents/terminology.md` names no retired skill (checked 2026-10-04). `research_vault/templates/vault/AGENTS.md` row stays as is.

- [ ] **Step 1: Prove nothing outside the retired directory references it, then delete**

```bash
cd /home/eranr/research-vault/.worktrees/paper-critical-analysis-merge
grep -rn "critical-analysis-report" --include="*.py" --include="*.md" --include="*.json" --include="*.toml" --include="*.yaml" . \
  | grep -v "^./skills/critical-analysis-report/" \
  | grep -v "paper-critical-analysis" \
  | grep -v "^./docs/superpowers/"
```

Expected remaining hits: `README.md:86`, `tests/test_skill_contracts.py:32` (both fixed below), possibly `docs/research/.../README.md` history prose (historical record — leave). Anything else: fix it before deleting. Then:

```bash
git rm -r skills/critical-analysis-report
```

- [ ] **Step 2: ENTRY_SKILLS**

In `tests/test_skill_contracts.py`, delete the line `    "critical-analysis-report",` from `ENTRY_SKILLS`, and replace exactly these two comment lines above the set:

```python
# every other shipped skill is a guard/reference skill, model-invoked AND
# user-invocable, so it carries neither `disable-model-invocation` nor
# `user-invocable`. This list grows by one name as each entry skill ships —
# it only ever grows, never shrinks.
```

with:

```python
# every other shipped skill is a guard/reference skill, model-invoked AND
# user-invocable, so it carries neither `disable-model-invocation` nor
# `user-invocable`. This list grows by one name as each entry skill ships,
# and shrinks only when a spec retires one (critical-analysis-report merged
# into paper-critical-analysis, 2026-10-04).
```

- [ ] **Step 3: README flow table**

Replace the two rows at `README.md:86-87` with one:

```markdown
| Critique       | `paper-critical-analysis`  | Critical analysis of one paper: read everything it ships including released code and data, check every number, judge nine dimensions in a fresh context, edit, machine-check, then verify every locator and outside claim |
```

(The "Analyze" step disappears from the flow table; the surrounding rows keep their order.)

- [ ] **Step 4: ATTRIBUTION.md**

Two edits in the `**Adapted into `skills/paper-critical-analysis/`**` passage:

1. After the paragraph ending "no text from it is reproduced.", append:

```markdown
The retired `critical-analysis-report` skill was merged into this one
(spec: `docs/superpowers/specs/2026-10-04-paper-critical-analysis-merge-design.md`).
Its material — the report outline, the notes-file structure that became the
evidence file, the checker, and the background file — derives from the vault
owner's own guide to critical analysis of a research paper; no third-party
text rode along.

The stage 5 editor brief paraphrases, and copies nothing from: Editors
Canada's *Professional Editorial Standards 2024* (structural, stylistic and
copy-editing stages; the text is copyrighted); Strunk's *The Elements of
Style* (public domain); and Wikipedia's "Signs of AI writing"
(CC BY-SA, paraphrased).
```

2. No change to the nine MIT notices table — it stays as is.

- [ ] **Step 5: Evals README**

Append to `docs/research/2026-09-20-paper-critical-analysis-evals/README.md` (no absolute home paths anywhere in it):

```markdown
## The merged skill (2026-10-04)

`critical-analysis-report` and `paper-critical-analysis` were replaced by one
skill under the latter's name; the design and the evidence behind it are in
`docs/superpowers/specs/2026-10-04-paper-critical-analysis-merge-design.md`.
The comparison runs that drove the design, and the 20-item Bloom answer key,
are local and git-ignored (`sources/bloom-skill-comparison/`,
`sources/bloom-skill-comparison-run2/`; `comparison.md` there holds the full
analysis).

Planned acceptance runs, one per paper, recorded here as they happen:

- **Bloom** (Jörke et al., CHI '26): same inputs and answer key as the
  comparison runs. Pass bar: score ≥ 18; about 8.5M fresh tokens or fewer and
  about 2 hours or less; nothing unsupported after verification and no wrong
  outside claim; no files outside the output folder; no credential files
  fetched; raw participant data deleted. The run is also regression-compared
  against the four comparison runs on three ledgers — the answer key per
  item, the merge's targeted fixes (each miss names the change that should
  have covered it), and calibration and shape; a targeted-fix miss blocks
  acceptance, variance is recorded. Not yet run.
- **CheckIfExist** (Abbonato 2026, arXiv:2602.15871): answer key built from
  the run E and F records before the run; tests a paper with no participants
  and heavy web use. Not yet run.
- **A human read** of one report: is it the guide's result, in prose a person
  would want to read? Not yet done.
```

- [ ] **Step 6: Full suite, form, commit**

```bash
.venv/bin/python -m pytest tests -q -n auto
ruff check tests/test_skill_contracts.py
mdformat --number --wrap keep README.md ATTRIBUTION.md docs/research/2026-09-20-paper-critical-analysis-evals/README.md
.venv/bin/python -m pytest tests -q -n auto   # again if mdformat touched anything pinned
# The `git rm -r` in step 1 already staged the deletions; adding the deleted
# directory again would error ("pathspec did not match any files").
git add tests/test_skill_contracts.py README.md ATTRIBUTION.md docs/research/2026-09-20-paper-critical-analysis-evals/README.md
git commit -m "feat(skills)!: retire critical-analysis-report, merged into paper-critical-analysis

The directory goes; ENTRY_SKILLS shrinks for the first time (comment
updated to say when that is allowed); the README flow table carries one
critique row; ATTRIBUTION credits the merged material (the vault owner's
own guide) and the editor brief's sources (PES 2024 paraphrased, Strunk,
Wikipedia's signs-of-AI-writing paraphrased); the evals README gains the
merged skill's acceptance bars. terminology.md and the vault template row
already fit the merged skill and are unchanged.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" -- skills/critical-analysis-report tests/test_skill_contracts.py README.md ATTRIBUTION.md docs/research/2026-09-20-paper-critical-analysis-evals/README.md
```

(If `git status --porcelain` shows the `git rm` left index-only state that a pathspec commit can't carry, follow AGENTS.md: verify clean status, then commit through the index.)

______________________________________________________________________

### Task 5: Full gate and push

**Files:** none new.

**Interfaces:**

- Consumes: Tasks 1–4 committed.

- Produces: branch `paper-critical-analysis-merge` pushed, required check green. Merging to `main` is `git merge --ff-only` after the check — per AGENTS.md, only when the user says land it.

- [ ] **Step 1: The offline gate, complete**

```bash
cd /home/eranr/research-vault/.worktrees/paper-critical-analysis-merge
.venv/bin/python -m pytest tests -q -n auto
ruff format --check research_vault tests scripts hooks
ruff check research_vault tests scripts hooks
mdformat --check --number --wrap keep $(git ls-files -- "*.md" | grep -v -e "^\.superpowers/" -e "^\.worktrees/" -e "^\.claude/worktrees/" -e "^research_vault/templates/vault/index\.md$")
```

Expected: all clean. Fix anything that isn't; re-run until it is.

- [ ] **Step 2: Push and watch the check**

```bash
git push -u origin paper-critical-analysis-merge
gh run watch --branch paper-critical-analysis-merge || gh run list --branch paper-critical-analysis-merge --limit 1
```

Expected: the required check green. If red, read the log, fix, commit (pathspec), push again.

- [ ] **Step 3: Report**

Report to the user: gate results, branch pushed, check status, and that two follow-ups wait on them — the behavioural runs (Task 6, costly) and, after the branch lands on `main`, deleting the superseded branch `critique-skills-tuning` (`git push origin --delete critique-skills-tuning` plus the local branch; it is NOT deleted before this branch lands).

______________________________________________________________________

### Task 6: Behavioural evaluation — USER-GATED, do not start unprompted

One Bloom run costs roughly 8M fresh tokens and 2 hours. **Stop and get the user's go-ahead before running anything in this task.** The offline gate (Task 5) is the merge bar; this task is the acceptance bar from the spec, plus a regression comparison against the four comparison runs the design was built on (CAR runs 1–2, PCA runs 1–2; `sources/bloom-skill-comparison/comparison.md` in the main checkout is the record).

**Files:** run outputs land under git-ignored local folders only (`sources/`); the evals README's "Planned acceptance runs" section is updated with results (no absolute home paths).

- [ ] **Step 1: Bloom run**

Use the prompt from the comparison runs (`sources/bloom-skill-comparison/` in the main checkout holds the run prompts; `comparison.md` there documents them) with only the skill path changed to `skills/paper-critical-analysis/`. Score against the same 20-item answer key. Pass bar, verbatim from the spec: score at least 18; about 8.5M fresh tokens or fewer, and about 2 hours or less; nothing unsupported after verification, and no outside claim wrong; no files written outside the output folder; no credential files fetched; raw participant data deleted. With one run per paper, a point or two is noise; a second Bloom run only if the first is borderline.

- [ ] **Step 2: Regression comparison against the four prior runs**

Build the comparison from the delivered report and evidence file, the run log, and `comparison.md`'s sections 3–4 and run-2 tables. Three ledgers:

1. **Answer key, per item** — the merged run beside the four prior columns (CAR 12, CAR-U 14.5, CAR run 2 15, PCA 17, PCA run 2 18). An item any two prior runs caught that the merged run misses is a regression; an item only one prior run ever caught is variance unless a merge change targets it.
2. **Targeted-fix items** — each of these exists because a specific merge change claims to cover it; a miss here is a regression of that change regardless of how many prior runs caught it:
   - **C2 / taxonomy judged as paper content** (stage 0's "file the paper names as holding its content" row — the fix that failed on wording in PCA run 2);
   - **H1 coefficient misreading found via the released code** (`released-artifacts.md` makes code reading mandatory; in the prior runs it was luck — CAR run 2 missed it by not reading the scripts);
   - **usage recomputation, satisfaction double-rescale, human-likeness composite** (headline-number recomputation is now mandated);
   - **wrong outside claims caught** (CAR run 2's two factual errors sat in `[checked:]` claims its verifier could not see; the merged verifier re-opens every W entry — the licence slip specifically is a GitHub-API pitfall `released-artifacts.md` should not repeat);
   - **no skipped mandated check** (run F's invisible skip; the External-check slots must all be filled);
   - **verdicts within the first few hundred words** of the critical discussion (PCA run 2's verdict list);
   - **no silently dropped finding** (CAR run 1's cuts; Coverage's "Evidence file only" line is the pointer);
   - **credential path recorded, never fetched** (`serviceAccount.json` from PCA run 2's notes);
   - **participant CSVs deleted at run end with the deletion recorded** (both PCA runs left them on disk);
   - **no `/tmp` scratch files** (three of four prior runs wrote them; write scope now binds subagents via the briefs).
3. **Calibration and shape** — H2's null read as imprecision with its interval (PCA), not as "high confidence of no advantage" (CAR run 1's miscalibration); Credibility closes with a confidence level; the report body in the reader's reach (prior bodies: CAR 3.0k–5.2k, PCA ~10.5k words; the evidence file, not the report, carries the audit bulk).

Also record the cost row beside the four prior runs (fresh tokens, wall time, report words) — the merged target sits between PCA run 2's 10.4M/150 min and CAR's 3.1M/49 min.

- [ ] **Step 3: Regression verdict and change decision**

For each regression found, name the merge change that should have covered it (or name the gap as new), and propose the smallest edit that would have prevented it — mechanism before prose, per the repo's design discipline. Severity rule: a targeted-fix miss or a two-run answer-key miss blocks acceptance and gets a fix plus a re-run of the affected leg; pure variance (single-run findings like SASSI-to-control, score shifts of a point or two) is recorded, not acted on. A finding this task will not fix becomes a GitHub issue, opened when deferred (per `docs/agents/issue-tracker.md`).

- [ ] **Step 4: CheckIfExist run**

Build the answer key from the run E and F records (`docs/research/2026-09-20-paper-critical-analysis-evals/README.md`) **before** the run, then run the skill on Abbonato 2026 (arXiv:2602.15871, 9 pages; the PDF is in `sources/`). Regression reference here is the run E and F record itself: the W-list findings those runs surfaced (uncited prior art as a Novelty point, the wrong cited year as a Credibility point) must still land as findings, not Context prose.

- [ ] **Step 5: Human read**

Hand the user one report and the question: is it the guide's result, in prose a person would want to read?

- [ ] **Step 6: Record**

Fill the results — scores, cost row, and the three regression ledgers with their verdicts — into the evals README's "Planned acceptance runs" section (relative paths only), mdformat it, commit with pathspec.

______________________________________________________________________

## After landing (not plan tasks)

- Delete branch `critique-skills-tuning` (superseded by this branch) once `paper-critical-analysis-merge` is on `main`: `git push origin --delete critique-skills-tuning; git branch -D critique-skills-tuning` from the main checkout.
- Remove this worktree from the main checkout when done: `git worktree remove .worktrees/paper-critical-analysis-merge && git worktree prune`.

## Self-review record

Checked against the spec on 2026-10-04, before saving:

- Every spec decision has a home: one depth (SKILL.md intro), replace-both/keep-name (Tasks 3–4), what-the-skill-reads (stage 0 row 1 + stage 2 W list), reader–judge–editor–verifier (stages 3/5/7 fresh-context), report shape + evidence file (Task 1 templates), uncapped-then-edit (stages 4–5), web required (stage 0 probe row), locators (SKILL.md `## Locators`), no fan-out (extract.md deleted; >100-page chunk row).
- Every checker rule in the spec's stage 6 list has an error path and a failing fixture (Task 1 steps 3/5); "template headings are the checker's single source of truth" is `template_headings()` + the built-from-template fixture.
- Every migration bullet has a task: skill rewrite (3), delete (4), three test files (1/3/4 — test_templates.py confirmed no-change), README (4), ATTRIBUTION (4), terminology (checked, no change), vault AGENTS.md row (no change), evals README (4), critique-skills-tuning (after landing).
- Type/name consistency pass: `{LOCATOR_CONVENTION}`/`{PAPER_PATHS}`/`{EVIDENCE_PATH}` uniform across briefs, SKILL.md, and tests; `- N1:` shape uniform across evidence template, checker `DEFINED_ID_RE`, and fixture; stage headings uniform between SKILL.md and `STAGES`; `Key:` line identical in template, fixture constant, and checker regex; the nine topics identical in brief, SKILL.md sentence, template headings, and `NINE`.

Amended 2026-10-04, after review (spec updated in the same commit): "derived" may cite a P entry, since the judge's own computations (Scalability rates) are neither in-paper conflicts nor outside sources; the editor's structural and stylistic passes are scoped to sections 1–3 so the Verdicts block, front matter and Coverage — repetitive by design — survive; the stage 2 mandated checks get fixed slots in the evidence template that the checker enforces (run F: a skipped check must be a visible hole, not a silence); the verifier checks every applied change-list item, moves included; the spec's locator row absorbed the named front-matter parts and `whole paper` (run F: absent-throughout findings fell outside the verifier's scope without it).
