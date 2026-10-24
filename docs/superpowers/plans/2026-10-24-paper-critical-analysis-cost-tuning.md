# paper-critical-analysis Cost Tuning — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cut the paper-critical-analysis skill's fresh-token cost by about 40% and its wall time by about 30% without moving its measured quality floor — a lighter editor, a verifier split into three parallel contexts, a judge that sees only cited page renders, and an excerpt rule for code and data — plus four evidence-shape fixes and one write-scope clause the acceptance reviews asked for.

**Architecture:** Prose changes to one skill (`SKILL.md`, three briefs, two templates, one reference file) and one new checker rule, each pinned by a contract test in `tests/`. Nothing structural moves: the eight stages, the templates' headings, and the checker's single-source-of-truth design stay as they are. Acceptance is one behavioural A/B run on CheckIfExist against the pre-registered key, with a decision rule written down before the run.

**Tech Stack:** Markdown skill files; Python 3 (stdlib only) for `scripts/check_report.py`; pytest; ruff + mdformat for form; `gh` for issues.

**Spec:** `docs/superpowers/specs/2026-10-04-paper-critical-analysis-cost-tuning-design.md` — the plan argues from the spec; executors read both.

## Global Constraints

Every task's requirements implicitly include these.

- **Branch and worktree:** `paper-critical-analysis-cost-tuning`, created from `main` at `6419497` when this plan was written and pushed to origin with the plan as its first commit (the spec names the branch, but it did not exist before). The worktree `/home/eranr/research-vault/.claude/worktrees/paper-critical-analysis-cost-tuning` is already on it: execute there, and create no second worktree or branch. The shared main checkout at `/home/eranr/research-vault` stays on `main`; never `git checkout` a branch there.
- **Commits:** explicit pathspec only, `git commit -m "<message>" -- <files>` (the message before the `--`: after it, every word is a pathspec); never `git add -A` or `git commit -a` — parallel sessions share this checkout. Every commit message ends with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
- **Tests:** from the worktree root, with the main checkout's interpreter — the worktree has no `.venv`, so prefix every tool with `/home/eranr/research-vault/.venv/bin/` and set `PYTHONPATH=.` for pytest so `research_vault` resolves to the worktree, not the parent checkout (`docs/agents/testing.md`, the wrong-tree import trap; canary: `PYTHONPATH=. .venv/bin/python -c "import research_vault; print(research_vault.__file__)"`). Commands below write `python`, `ruff`, `mdformat` for brevity. Fast loop: `python -m pytest tests/test_check_report.py tests/test_paper_critical_analysis_skill.py -q`. Full gate before push: `python -m pytest tests -q -n auto`. Baseline on `main` at plan time: 62 passed in the two files.
- **Form:** run the form owners on the touched files directly, never `pre-commit run` (it stashes other sessions' unstaged work): `ruff format <py files>`, `ruff check <py files>`, `mdformat --number --wrap keep <md files>`. mdformat realigns tables and renders thematic breaks as underscore lines; commit what it produces.
- **Spec non-goals, verbatim:** "Stage 2 exhaustiveness, the mandated-check slots, the released-code reading mandate, stage 1's view-every-figure bar: untouched." "Shrinking verifier coverage: all three checks keep their full item counts; the split changes contexts, not scope." "A fast mode, a deep mode, or any second depth." "Chasing the original ~8.5M bar at any cost: if the measured floor and 8.5M conflict, the floor wins and the bar is re-set from evidence."
- **SKILL.md's cost sentence** ("on a 33-page paper expect about 8M fresh tokens and about 2 hours", line 9) stays as it is until Task 9 measures. No earlier task touches it.
- **Templates are the checker's single source of truth.** `template_leads()` in `check_report.py` reads every `- Word:` bullet in the evidence template's External-check section and the report template's Coverage section as a mandated slot or lead. New guidance in those sections is prose, never a `- Word:` bullet, or it mints a new required slot.
- **Briefs keep one fenced block each.** `test_every_brief_placeholder_is_documented` slices a brief from its first triple-backtick to its last; a second fence breaks the slice. Brief placeholders are `{UPPER_SNAKE}` filled by the dispatcher; template placeholders are `{{lower words}}` filled by the writer.
- **`sources/`** is git-ignored run evidence. Read it; never commit it.
- **Issues #219 and #220:** comment, never close. #219 keeps its Key-line coverage item and #220 its polish items, which this spec does not cover.

### Spec readings settled here (decided once; every task assumes them)

- **Check 1 cannot check derived numbers.** `prompts/verify.md` today says a number marked "derived" is checked against the C, W or J entry it cites. The spec gives check 1 the paper, its images and the report — "nothing else" — so that sentence moves to check 3, which holds the full evidence file.
- **Check 2 cannot see the report.** Today's check 2 also tests that "what the report attributes to the entry says no more than the entry does". The spec gives check 2 the evidence file, the saved copies and the web, no report; that half moves to check 3 as part of the generalized claim-strength rule, which therefore covers N, C, W **and** J entries. Check 2 re-opens **every** W entry in the evidence file (it cannot know which the report cites, and every ID is cited somewhere, Coverage's `Evidence file only:` line included), so its item count does not shrink.
- **Unselected Inputs subsections are removed, not blanked.** The dispatcher fills `{CHECK}` and the chosen check's Inputs subsection and deletes the other two subsections from the brief it sends. Each verifier then holds only its own inputs — the point of the split.
- **Copy pass becomes flags only.** The spec says "Structural pass and copy flags only". The copy pass's consistency *fix* ("make terms, numbers and abbreviations consistent") is a per-passage sweep and goes with the stylistic pass; the flag bullet (uncited generalizations, numbers that do not add up) stays.
- **The pointer line's slug is a template placeholder.** The spec writes `critical-analysis-<paper-slug>.evidence.md`; the template uses `{{paper slug}}` so the existing placeholder error forces the writer to fill it, and the checker's new rule is prefix-only (`^Evidence file: `), exactly as the `Key:` rule is.
- **Two additions outside the spec's Migration list,** each one phrase: `prompts/judge.md`'s `{PAGE_RENDERS}` parenthetical (which would otherwise describe the judge's inputs wrongly after Task 5), and `ATTRIBUTION.md`'s editor-brief paragraph (which would otherwise credit sources the brief no longer paraphrases after Task 3).

## File Structure

| File                                                                              | Change                                                                                                                                                                              | Task          |
| --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| `skills/paper-critical-analysis/templates/report-template.md`                     | `Evidence file:` front-matter line; preamble sentence                                                                                                                               | 1             |
| `skills/paper-critical-analysis/scripts/check_report.py`                          | `EVIDENCE_LINE_RE` and its error; docstring bullet                                                                                                                                  | 1             |
| `tests/test_check_report.py`                                                      | `EVIDENCE_LINE` fixture line, `_missing_evidence_pointer` mutation, template-token assertion; `not applicable` slot pin                                                             | 1, 2          |
| `skills/paper-critical-analysis/templates/evidence-template.md`                   | computed-entry rule (preamble); slot-semantics sentence; J-entry shape on continuation lines                                                                                        | 2             |
| `skills/paper-critical-analysis/prompts/edit.md`                                  | Scope names the Evidence file line (1); structural pass + copy flags only, no accounting bar (3); tools run from the scratch folder (7)                                             | 1, 3, 7       |
| `ATTRIBUTION.md`                                                                  | editor-brief paragraph: stylistic sources become history                                                                                                                            | 3             |
| `skills/paper-critical-analysis/prompts/verify.md`                                | `{CHECK}` selector, three Inputs subsections, `{DRAFT_PATH}`, claim-strength rule in check 3, one count line per check (4); tools run from the scratch folder (7)                   | 4, 7          |
| `skills/paper-critical-analysis/prompts/judge.md`                                 | `{PAGE_RENDERS}` parenthetical (5); tools run from the scratch folder (7)                                                                                                           | 5, 7          |
| `skills/paper-critical-analysis/SKILL.md`                                         | stage 5 scope + model note (3); stage 7 three dispatches, table, model note (4); stage 3 render selection (5); Write-scope rule (7); cost sentence re-set from the measured run (9) | 3, 4, 5, 7, 9 |
| `skills/paper-critical-analysis/references/released-artifacts.md`                 | `## How to read` excerpt rule                                                                                                                                                       | 6             |
| `tests/test_paper_critical_analysis_skill.py`                                     | five-fields test (2); no-stylistic-pass test (3); dispatch-table test (4); renders-differ test (5); tools-inside-scratch test (7)                                                   | 2, 3, 4, 5, 7 |
| `docs/research/2026-09-20-paper-critical-analysis-evals/README.md`                | A/B run record                                                                                                                                                                      | 9             |
| `docs/research/2026-09-20-paper-critical-analysis-evals/mine_tokens.py`           | transcript token miner (new; the 2026-10-04 mining was retyped by hand)                                                                                                             | 9             |
| `docs/superpowers/specs/2026-10-04-paper-critical-analysis-cost-tuning-design.md` | status line                                                                                                                                                                         | 9             |

______________________________________________________________________

## Task 1: The report names its evidence file, and the checker requires the line

**Files:**

- Modify: `skills/paper-critical-analysis/templates/report-template.md:3,11`
- Modify: `skills/paper-critical-analysis/scripts/check_report.py:27,97,416-417`
- Modify: `skills/paper-critical-analysis/prompts/edit.md:19` (the brief restates the checker's constraints; a rule added to one and not the other drifts — issue #220's cache-coupling note)
- Test: `tests/test_check_report.py`

**Interfaces:**

- Produces: a report-template front-matter line `Evidence file: critical-analysis-{{paper slug}}.evidence.md, alongside this report.`; checker constant `EVIDENCE_LINE_RE = re.compile(r"^Evidence file: ", re.MULTILINE)`; error text `report: missing evidence-file pointer (the 'Evidence file:' line)`; test constant `EVIDENCE_LINE` in `tests/test_check_report.py`. Task 3's `edit.md` rewrite keeps the Scope phrase this task adds.

- [ ] **Step 1: Write the failing tests**

In `tests/test_check_report.py`, directly after the `KEY_LINE = (...)` constant (ends line 29), add:

```python
EVIDENCE_LINE = (
    "Evidence file: critical-analysis-example.evidence.md, alongside this report."
)
```

In `build_report()`, replace

```python
            lines.append(KEY_LINE)
```

with

```python
            lines.append(KEY_LINE)
            lines.append(EVIDENCE_LINE)
```

In `test_the_shipped_templates_carry_the_checker_tokens`, after `assert "\nKey: " in report_template` add:

```python
    assert "\nEvidence file: " in report_template
```

After `_missing_key` (line 177-178) add:

```python
def _missing_evidence_pointer(report: str) -> str:
    return report.replace(EVIDENCE_LINE + "\n", "")
```

In the `@pytest.mark.parametrize(("mutate", "expected"), [...])` list, after `(_missing_key, "provenance key"),` add:

```python
        (_missing_evidence_pointer, "evidence-file pointer"),
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_check_report.py -q`

Expected: 2 failures — `test_the_shipped_templates_carry_the_checker_tokens` (the template has no `Evidence file:` line yet) and `test_each_report_rule_fails_its_fixture[_missing_evidence_pointer-evidence-file pointer]` (status is 0: nothing requires the line yet). Everything else passes — the extra fixture line is plain content.

- [ ] **Step 3: Add the checker rule**

In `skills/paper-critical-analysis/scripts/check_report.py`:

In the module docstring, after the line

```text
- the ``Key:`` provenance line is missing;
```

add

```text
- the ``Evidence file:`` pointer line is missing;
```

After `KEY_LINE_RE = re.compile(r"^Key: ", re.MULTILINE)` add:

```python
EVIDENCE_LINE_RE = re.compile(r"^Evidence file: ", re.MULTILINE)
```

In `check_report()`, after

```python
    if not KEY_LINE_RE.search(text):
        errors.append("report: missing provenance key (the 'Key:' line)")
```

add

```python
    if not EVIDENCE_LINE_RE.search(text):
        errors.append(
            "report: missing evidence-file pointer (the 'Evidence file:' line)"
        )
```

- [ ] **Step 4: Add the line to the report template**

In `skills/paper-critical-analysis/templates/report-template.md`, in the preamble (line 3), replace

```text
Replace every `{{placeholder}}`, and keep the `Key:` line verbatim — the checker requires it.
```

with

```text
Replace every `{{placeholder}}`, and keep the `Key:` line verbatim — the checker requires it, and requires the `Evidence file:` line too: it names the evidence file by filename, so the pointer survives the report leaving its folder.
```

After the `Key:` line (line 11) and its following blank line, insert a new paragraph:

```text
Evidence file: critical-analysis-{{paper slug}}.evidence.md, alongside this report.
```

so the front matter reads: citation line, blank, `Key:` line, blank, `Evidence file:` line, blank, `## 1. Context`.

- [ ] **Step 5: Keep the editor's restated constraints in step**

In `skills/paper-critical-analysis/prompts/edit.md`, in the `## Scope` paragraph, replace

```text
The front matter (the citation block and the Key line), the Verdicts block, and Coverage take the copy pass alone:
```

with

```text
The front matter (the citation block, the Key line and the Evidence file line), the Verdicts block, and Coverage take the copy pass alone:
```

and replace

```text
fails the report unless every heading, every Coverage lead word and the Key line stay as written;
```

with

```text
fails the report unless every heading, every Coverage lead word, the Key line and the Evidence file line stay as written;
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `python -m pytest tests/test_check_report.py tests/test_paper_critical_analysis_skill.py -q`

Expected: all pass (63 in `test_check_report.py` counting the new parametrize case, plus the skill tests). `test_a_template_only_pair_fails` still fails its fixture for other reasons (empty sections, unfilled slots), so it stays green.

- [ ] **Step 7: Form and commit**

```bash
ruff format skills/paper-critical-analysis/scripts/check_report.py tests/test_check_report.py
ruff check skills/paper-critical-analysis/scripts/check_report.py tests/test_check_report.py
mdformat --number --wrap keep skills/paper-critical-analysis/templates/report-template.md skills/paper-critical-analysis/prompts/edit.md
git add skills/paper-critical-analysis/templates/report-template.md skills/paper-critical-analysis/scripts/check_report.py skills/paper-critical-analysis/prompts/edit.md tests/test_check_report.py
git commit -m "feat(skills): the report names its evidence file, and the checker requires the line

The blind rating scored the merged report 5/10 on verifiability when read
alone and 9/10 with its evidence file: the pointer survives the report
leaving its folder. The checker requires the line as it requires Key:.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- skills/paper-critical-analysis/templates/report-template.md skills/paper-critical-analysis/scripts/check_report.py skills/paper-critical-analysis/prompts/edit.md tests/test_check_report.py
```

______________________________________________________________________

## Task 2: Evidence entries carry their computations, their fields and their not-applicable slots

**Files:**

- Modify: `skills/paper-critical-analysis/templates/evidence-template.md:3,63,76`
- Test: `tests/test_check_report.py` (one pin), `tests/test_paper_critical_analysis_skill.py` (one contract test)

**Interfaces:**

- Consumes: `prompts/judge.md`'s sentence `Every point carries five fields: **Kind**, **Locator**, **Observation**, **Evidence**, **Why it matters**.` (unchanged by this plan).

- Produces: the J-entry shape — `- J1: <Kind>` followed by four two-space-indented continuation lines `Locator:`, `Observation:`, `Evidence:`, `Why it matters:`. The checker's `DEFINED_ID_RE` (`^- ([NCWJ]\d+):`) still reads the ID from the first line; nothing in the checker changes. The shape is shown in the template's preamble, above the thematic break, because `DEFINED_ID_RE` is not fence-aware (verified 2026-10-24: it finds `J1` inside a fence) and a `- J1:` line below the break would define J1 in every evidence file a run copies the template into.

- [ ] **Step 1: Write the failing contract test**

Append to `tests/test_paper_critical_analysis_skill.py`:

```python
def test_the_evidence_template_houses_the_judges_five_fields():
    """The judge returns five fields per point and the evidence template shows
    where each lands: Kind on the ID line, the other four one per indented
    continuation line. A field renamed on one surface strands the other, and
    the one-line semicolon chain this replaces is what the pair rating called
    unreadable."""
    brief = _brief("judge.md")
    sentence = brief[brief.index("Every point carries five fields") :]
    sentence = sentence.split("\n", 1)[0]
    fields = re.findall(r"\*\*([A-Za-z ]+)\*\*", sentence)
    assert len(fields) == 5, fields
    template = (SKILL_DIR / "templates" / "evidence-template.md").read_text(
        encoding="utf-8"
    )
    assert f"- J1: <{fields[0]}>" in template
    for field in fields[1:]:
        assert f"\n  {field}:" in template, (
            f"evidence-template.md has no continuation line for {field}"
        )
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_paper_critical_analysis_skill.py::test_the_evidence_template_houses_the_judges_five_fields -q`

Expected: FAIL — `- J1: <Kind>` is not in the template (today's shape is `- J1: <Kind; Locator; Observation; Evidence; Why it matters>`).

- [ ] **Step 3: Write the pin for the not-applicable slot**

Append to `tests/test_check_report.py` (after `test_more_abbreviations_do_not_end_a_derived_sentence`):

```python
def test_a_slot_filled_not_applicable_with_a_reason_passes(tmp_path):
    """The evidence template names `not applicable: <reason>` as a legal slot
    fill — CheckIfExist's Headline recomputations slot is the worked example.
    The checker accepted it before the template said so; this pins that."""
    evidence = _swap(
        build_evidence(),
        "- Headline recomputations: W1.",
        "- Headline recomputations: not applicable: the abstract and conclusion "
        "state no number.",
    )
    status, out = run(build_report(), evidence, tmp_path)
    assert status == 0, out
    assert "bare" not in out
```

Run: `python -m pytest tests/test_check_report.py::test_a_slot_filled_not_applicable_with_a_reason_passes -q`

Expected: PASS already (this is a pin, not a red step — the spec says the checker already accepts the form; the test keeps it that way).

- [ ] **Step 4: Edit the evidence template**

In `skills/paper-critical-analysis/templates/evidence-template.md`:

Preamble (line 3): replace

```text
and detail may continue on indented lines beneath it; the checker reads IDs from exactly that first-line shape.
```

with

````text
and detail may continue on indented lines beneath it; the checker reads IDs from exactly that first-line shape. A computed entry — a recomputation, a reconciliation, a derived rate — carries its inputs and its result on those continuation lines: the inputs with their locators or source, the operation, and the value beside the paper's, as a table where several are compared. A script name alone is not evidence; name the script beside the figures, never in their place. A finding entry puts its five fields one per continuation line, never in one semicolon chain:

```
- J1: <Kind>
  Locator: <locator>
  Observation: <one sentence>
  Evidence: <admissible items>
  Why it matters: <one sentence>
```
````

The fence stays above the thematic break with the rest of the preamble: everything below the break is copied into every run's evidence file, and `DEFINED_ID_RE` would read a copied `- J1: <Kind>` as a definition.

External-check list (line 63): replace

```text
Each mandated check fills its slot below with the W IDs that discharged it or `not checked: <reason>`; the checker fails an unfilled slot:
```

with

```text
Each mandated check fills its slot below with the W IDs that discharged it, with `not checked: <reason>` when the check could not run, or with `not applicable: <reason>` when the paper gives it nothing to check — for a paper whose abstract and conclusion state no number, `Headline recomputations:` reads `not applicable: the abstract and conclusion state no number`. The checker fails an unfilled slot and accepts all three forms:
```

(Prose, not a bullet: a `- Word:` line here would become a ninth required slot — see Global Constraints.)

Judge points (line 76): replace

```text
Filled at stage 3's return: the kept points under assigned IDs, `- J1: <Kind; Locator; Observation; Evidence; Why it matters>`, then the judge's Recalled lines, then the count of points dropped as inadmissible.
```

with

```text
Filled at stage 3's return: the kept points under assigned IDs, in the five-field shape the preamble shows — one field per indented continuation line, never one semicolon chain — then the judge's Recalled lines, then the count of points dropped as inadmissible.
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest tests/test_check_report.py tests/test_paper_critical_analysis_skill.py -q`

Expected: all pass. In particular `test_the_template_built_pair_passes`, `test_a_template_only_pair_fails` (still fails its fixture on empty sections and unfilled slots), `test_the_shipped_templates_carry_the_checker_tokens` and `test_every_ledger_the_evidence_file_defines_is_admissible_to_the_judge` are unaffected by the fenced J shape.

- [ ] **Step 6: Form and commit**

```bash
ruff format tests/test_check_report.py tests/test_paper_critical_analysis_skill.py
ruff check tests/test_check_report.py tests/test_paper_critical_analysis_skill.py
mdformat --number --wrap keep skills/paper-critical-analysis/templates/evidence-template.md
git add skills/paper-critical-analysis/templates/evidence-template.md tests/test_check_report.py tests/test_paper_critical_analysis_skill.py
git commit -m "docs(skills): evidence entries carry their computations, their fields and their not-applicable slots

From the pair re-rating of the Bloom run: J15 named a script and showed no
inputs or result, where W22's table let the rater reproduce the arithmetic;
long J entries read as one semicolon chain. The slot semantics close #219's
open comment: not applicable: <reason> is a legal fill, and the checker
already accepted it.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- skills/paper-critical-analysis/templates/evidence-template.md tests/test_check_report.py tests/test_paper_critical_analysis_skill.py
```

______________________________________________________________________

## Task 3: The editor runs a structural pass and copy flags, on a smaller model

**Files:**

- Modify: `skills/paper-critical-analysis/prompts/edit.md` (the whole fenced brief)
- Modify: `skills/paper-critical-analysis/SKILL.md:102` (stage 5 paragraph)
- Modify: `ATTRIBUTION.md:128-132`
- Test: `tests/test_paper_critical_analysis_skill.py`

**Interfaces:**

- Consumes: Task 1's Scope phrase naming the Evidence file line (kept verbatim in the rewrite below).

- Produces: `edit.md` Test-field vocabulary `delete, one-place, move-detail, table, order`; the **Before** field stays verbatim (check 3 of the verifier reads it — Task 4). Task 7 later appends a tools clause to the brief's Delegation section; this task does not add it.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_paper_critical_analysis_skill.py`:

```python
def test_the_editor_brief_runs_no_stylistic_pass():
    """The 2026-10-04 acceptance runs measured the stylistic sweep and the
    every-rule-to-every-passage bar at most of the editor's items and minutes,
    with the reader-visible value in the structural moves and the copy flags.
    A stylistic bullet, the accounting bar, or their Test-field words coming
    back brings the sweep back. Before stays verbatim because the verifier's
    drift check consumes it."""
    brief = _brief("edit.md")
    assert "Stylistic:" not in brief
    assert "every rule has been applied to every passage" not in brief
    for word in ("tighten", "AI-pattern", "consistency"):
        assert word not in brief, f"edit.md's Test vocabulary still names {word}"
    before = brief[brief.index("**Before**") :].split("\n", 1)[0]
    assert "verbatim" in before
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_paper_critical_analysis_skill.py::test_the_editor_brief_runs_no_stylistic_pass -q`

Expected: FAIL on `assert "Stylistic:" not in brief`.

- [ ] **Step 3: Rewrite the brief**

Replace the entire fenced block of `skills/paper-critical-analysis/prompts/edit.md` (everything between the opening and closing triple-backtick lines; keep the two lines of prose above the fence as they are) with:

````text
```
You are editing a critical-analysis report for one reader: someone deciding whether to trust and use the paper it describes. You return a change list; you edit no file.

## Inputs

- Report: {REPORT_PATH}
- Evidence file: {EVIDENCE_PATH} — read only, for checking that a claim you touch keeps its IDs resolvable and for naming the section a moved detail lands in.

## The invariant

Every change keeps the claim and its strength: its qualifiers, numbers, locators, N/C/W/J IDs and provenance marks ((W12), [inferred], "derived"). A sentence that fails the delete rule below (repetitive, irrelevant or superfluous) is deleted whole, never trimmed to a weaker version of itself. You add no finding and no fact.

## Scope

The structural pass works on sections 1–3, except the Verdicts block. The front matter (the citation block, the Key line and the Evidence file line), the Verdicts block, and Coverage take the copy flags alone: their one-line repetitions and fixed lead words are the outline's, not padding — a verdict appears both in the Verdicts block and opening its topic by design. Sentence-level style — wording, tone, needless words — is out of scope: a sentence you keep stays as written. A checker runs after you and fails the report unless every heading, every Coverage lead word, the Key line and the Evidence file line stay as written; every section keeps content of its own, every topic a locator or ID, and Credibility its confidence level; every ID the evidence file defines still appears in the report (Coverage's `Evidence file only:` line counts); and every "derived" number keeps its C, W or J ID in its own sentence.

## Your passes, in order (Professional Editorial Standards 2024, paraphrased: the structural pass, then the copy pass's flags)

Structural:

- Delete repetitive, irrelevant and superfluous sentences.
- Keep each meaning in one place, under the topic it bears on most, with a one-line cross-reference where another topic needs it.
- Move detail behind its ID into the evidence file: derivations, number lists and source quotes go there; the claim, its locators and its IDs stay in the report.
- Recast number-heavy prose as a table.
- Put the most relevant material first within each section.

Copy flags:

- Flag, without fixing, any generalization that has no citation and any number that does not add up.

You are done when the structural pass has run over its scope and the flags are listed. Return an item only where you propose a change; a passage that needs none gets no item and no mention.

## Delegation

Do this work yourself, and spawn no subagent: this pipeline already fills every seat the critique gets, and an agent you spawned would re-read the skill and fan out again.

Any file you create goes in the scratch folder beside the evidence file (`<paper-slug>-work/`), and nowhere else.

## What you return

A numbered change list, then a Flags section, then two word-count lines, and nothing else. Each item:

- **Where**: the section and enough quoted text to find the place.
- **Before**: the text as it stands, verbatim (for a deletion or move, the whole sentence or block) — the verifier's drift check reads this field, so it is never paraphrased or abridged.
- **After**: the replacement text; "delete" for a deletion; for a move, the evidence-file section it lands in and the one-line claim that stays.
- **Test**: which rule above the item applies (delete, one-place, move-detail, table, order).

The flags go in a section headed "Flags", one line each: the section, enough quoted text to find the place, and what is uncited or does not add up.

End with two lines: the report's word count as you received it, and as it would stand with every item applied.
```
````

- [ ] **Step 4: Update SKILL.md stage 5**

In `skills/paper-critical-analysis/SKILL.md`, under `## Stage 5 — Edit`, replace

```text
**Fresh context, required** — an author reviewing its own text keeps everything. Run one subagent whose whole context is `prompts/edit.md` with its placeholders filled: the report and the evidence file, which it reads only. It returns a change list;
```

with

```text
**Fresh context, required** — an author reviewing its own text keeps everything. Run one subagent whose whole context is `prompts/edit.md` with its placeholders filled: the report and the evidence file, which it reads only. The brief asks for a structural pass and copy flags, not a stylistic sweep, and it does not need the strongest model: where the harness offers the choice, dispatch it on a smaller one. It returns a change list;
```

The rest of the paragraph and the **Done when** line stay as they are.

- [ ] **Step 5: Update ATTRIBUTION.md**

Replace

```text
The stage 5 editor brief paraphrases, and copies nothing from: Editors
Canada's *Professional Editorial Standards 2024* (structural, stylistic and
copy-editing stages; the text is copyrighted); Strunk's *The Elements of
Style* (public domain); and Wikipedia's "Signs of AI writing"
(CC BY-SA, paraphrased).
```

with

```text
The stage 5 editor brief paraphrases, and copies nothing from, Editors
Canada's *Professional Editorial Standards 2024* (its structural and
copy-editing stages; the text is copyrighted). Its stylistic pass, dropped
in the 2026-10 cost tuning, paraphrased Strunk's *The Elements of Style*
(the 1918 edition, public domain) and Wikipedia's "Signs of AI writing"
(CC BY-SA); git retains that text.
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `python -m pytest tests/test_check_report.py tests/test_paper_critical_analysis_skill.py -q`

Expected: all pass, including `test_every_brief_placeholder_is_documented[edit.md]` (the two placeholders are unchanged) and `test_the_skill_dispatches_every_brief_it_ships`.

- [ ] **Step 7: Form and commit**

```bash
ruff format tests/test_paper_critical_analysis_skill.py
ruff check tests/test_paper_critical_analysis_skill.py
mdformat --number --wrap keep skills/paper-critical-analysis/prompts/edit.md skills/paper-critical-analysis/SKILL.md ATTRIBUTION.md
git add skills/paper-critical-analysis/prompts/edit.md skills/paper-critical-analysis/SKILL.md ATTRIBUTION.md tests/test_paper_critical_analysis_skill.py
git commit -m "feat(skills): the editor runs a structural pass and copy flags, on a smaller model

The acceptance runs put most of the editor's 51 + 46 items and most of its
80 combined minutes in the stylistic sweep and the every-rule-to-every-
passage bar; the reader-visible value sat in the structural moves and the
flags. Before stays verbatim on every item: the verifier's drift check
consumes it.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- skills/paper-critical-analysis/prompts/edit.md skills/paper-critical-analysis/SKILL.md ATTRIBUTION.md tests/test_paper_critical_analysis_skill.py
```

______________________________________________________________________

## Task 4: The verifier runs as three parallel checks, each with its own inputs

**Files:**

- Modify: `skills/paper-critical-analysis/prompts/verify.md` (the whole file)
- Modify: `skills/paper-critical-analysis/SKILL.md:112-118` (stage 7)
- Test: `tests/test_paper_critical_analysis_skill.py`

**Interfaces:**

- Consumes: the draft path SKILL.md already defines, `critical-analysis-<paper-slug>.draft.md`; the editor's verbatim **Before** field (Task 3).

- Produces: brief placeholders `{CHECK}` (filled `1`, `2` or `3`) and `{DRAFT_PATH}` (new), alongside the existing `{PAPER_PATHS}`, `{PAGE_RENDERS}`, `{REPORT_PATH}`, `{EVIDENCE_PATH}`, `{LOCATOR_CONVENTION}`. Inputs subsections headed exactly `### Check 1 — locators, quotes and numbers`, `### Check 2 — W entries`, `### Check 3 — claim strength and edit drift`. A SKILL.md stage 7 table whose rows are `| 1 | … | placeholders |`, `| 2 | … |`, `| 3 | … |`. The test below hard-codes the per-check placeholder sets; Task 7 appends a tools clause to the brief's Delegation section and does not touch these.

- [ ] **Step 1: Write the failing contract test**

Append to `tests/test_paper_critical_analysis_skill.py`:

```python
# One brief, three dispatches: which placeholders each verifier check receives.
VERIFY_DISPATCHES = {
    "1": {"PAPER_PATHS", "PAGE_RENDERS", "REPORT_PATH"},
    "2": {"EVIDENCE_PATH"},
    "3": {"REPORT_PATH", "DRAFT_PATH", "EVIDENCE_PATH"},
}


def _verify_inputs_by_check() -> dict[str, set[str]]:
    """The placeholders under each `### Check N` subsection of verify.md's
    Inputs section."""
    brief = _brief("verify.md")
    inputs = brief[brief.index("## Inputs") : brief.index("## Locator convention")]
    found = {}
    for block in re.split(r"^### Check ", inputs, flags=re.MULTILINE)[1:]:
        number = block.split(maxsplit=1)[0]
        found[number] = set(_PLACEHOLDER.findall(block))
    return found


def _skill_dispatch_table() -> dict[str, set[str]]:
    """SKILL.md stage 7's dispatch table: the {CHECK} number of each row and
    the placeholders its last column says to fill."""
    text = _skill_text()
    stage_7 = text[text.index(STAGES[7]) :]
    rows = {}
    for line in stage_7.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[0] in ("1", "2", "3"):
            rows[cells[0]] = set(_PLACEHOLDER.findall(cells[2]))
    return rows


def test_each_verifier_dispatch_fills_exactly_its_checks_inputs():
    """The verifier's three checks need disjoint inputs, so stage 7 runs three
    dispatches of one brief. SKILL.md's table says which placeholders each
    fills; verify.md's Inputs subsections say which each check reads. A
    placeholder in one list and not the other is an input a verifier never
    receives, or one it receives and should not hold. The locator convention
    sits outside the Inputs section and goes to every dispatch."""
    brief = _brief("verify.md")
    assert "{CHECK}" in brief
    assert _verify_inputs_by_check() == VERIFY_DISPATCHES
    assert _skill_dispatch_table() == VERIFY_DISPATCHES
    inputs = brief[brief.index("## Inputs") : brief.index("## Locator convention")]
    assert "{LOCATOR_CONVENTION}" not in inputs
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_paper_critical_analysis_skill.py::test_each_verifier_dispatch_fills_exactly_its_checks_inputs -q`

Expected: FAIL on `assert "{CHECK}" in brief`.

- [ ] **Step 3: Rewrite the verifier brief**

Replace the entire contents of `skills/paper-critical-analysis/prompts/verify.md` with:

````text
# Stage 7 brief

Sent verbatim to each of the three stage 7 verifier subagents, with the placeholders filled. It is the subagent's whole context.

```
You are checking a report against the paper it describes and against the sources it cites. Every check is match or fail; you leave the report as it stands and create no files.

Three checks are listed under "What you check". You run check {CHECK} alone; the other two run in parallel contexts of their own, and the Inputs below hold only what your check needs.

## Inputs

### Check 1 — locators, quotes and numbers

- Paper: {PAPER_PATHS} — the paper and every appendix and supplement — and {PAGE_RENDERS} (images of every page carrying a figure, table or equation; "none" if none).
- Report: {REPORT_PATH}

### Check 2 — W entries

- Evidence file: {EVIDENCE_PATH} — its External-check list holds the W entries, one per outside check, each naming the claim checked, the source, its URL, the saved copy and what the source said.
- Scratch folder: `<paper-slug>-work/`, beside the evidence file — the saved copies of fetched sources.
- The web, for re-opening each entry's URL.

### Check 3 — claim strength and edit drift

- Report: {REPORT_PATH}
- Draft: {DRAFT_PATH} — the report as it stood before the editor's changes.
- Evidence file: {EVIDENCE_PATH} — every N, C, W and J entry the report cites, and the Pruning record: the editor's change list with each item marked applied or rejected.

## Locator convention

{LOCATOR_CONVENTION}

Resolve every locator under this convention, by the paper's own numbering and names.

## What you check

1. Every locator, quote and number the report attributes to the paper: find it in the paper. An item passes when the locator resolves to text that says what the report says it says, the quote matches the paper verbatim, and the number appears at the stated place; read a number in a figure, table or equation off the page as an image (its render, or the PDF page itself when there are no renders). A `whole paper` locator passes when a search of the paper and its supplements finds the absent item nowhere. A number the report marks "derived" is check 3's, not yours: skip it.
2. Every W entry in the evidence file: re-open it at its URL, or at its saved copy in the scratch folder when the URL fails. It passes when the source says what the entry says it said.
3. Two checks of the report against the evidence file. Claim strength: every sentence citing an N, C, W or J entry says no more than the entry does — the same scope, the same hedges, the same time and tense, the same subject (the released code is not the deployment; "pointed out" is not "judged inadequate") — and a number marked "derived" matches the value its C, W or J entry computes. Edit drift: every change-list item the Pruning record marks applied — compare the report's text where it landed with Before, for lost or added meaning, reading the draft where Before needs its surroundings. A rewording passes when it keeps the claim, its strength, and every qualifier, number, locator, N/C/W/J ID and provenance mark ((W12), [inferred], "derived") Before carried; for a move, check the one-line claim that stayed against what moved.

## Delegation

Do this work yourself, and spawn no subagent: this pipeline already fills every seat the critique gets, and an agent you spawned would re-read the skill and fan out again.

## What you return

The items that failed, then your count line, and nothing else. Each failed item:

- the report line (quote enough to identify it),
- what the report claims,
- the locator, entry, or change-list item you checked,
- what you found there, or "not found".

End with one count line for your check: check 1, locators, quotes and numbers checked and failed; check 2, W entries checked and failed; check 3, claims checked and failed, then change-list items checked and failed. If nothing failed, return the count line alone.
```

`{CHECK}` is filled with `1`, `2` or `3`. The dispatcher fills that check's Inputs subsection and removes the other two subsections, so each verifier holds only its own inputs. `{DRAFT_PATH}` is the draft stage 4 saved, `critical-analysis-<paper-slug>.draft.md`. `{LOCATOR_CONVENTION}` is filled verbatim from SKILL.md's "Locators" section, in every dispatch.
````

- [ ] **Step 4: Rewrite SKILL.md stage 7**

In `skills/paper-critical-analysis/SKILL.md`, replace the three paragraphs under `## Stage 7 — Verify` (from `**Fresh context, required** — a verifier holding` through the `**Done when:**` line) with:

```text
**Fresh context, required** — a verifier holding the reasoning behind a locator is no longer checking it. Run three subagents in parallel, each with `prompts/verify.md` as its whole context: `{CHECK}` filled with the row's number, the row's placeholders filled, the other two Inputs subsections removed, and `{LOCATOR_CONVENTION}` filled from the Locators section above (verbatim) in every dispatch. The brief does not need the strongest model: where the harness offers the choice, dispatch it on a smaller one.

| `{CHECK}` | Checks                        | Placeholders filled                                |
| --------- | ----------------------------- | -------------------------------------------------- |
| 1         | locators, quotes and numbers  | `{PAPER_PATHS}`, `{PAGE_RENDERS}`, `{REPORT_PATH}` |
| 2         | W entries                     | `{EVIDENCE_PATH}`                                  |
| 3         | claim strength and edit drift | `{REPORT_PATH}`, `{DRAFT_PATH}`, `{EVIDENCE_PATH}` |

Each returns failures only, with its count line. Fix, drop, or move each returned item to Coverage; record the dispositions under Verifier list in the evidence file; update Coverage's `Verification:` line with the four counts (locators, quotes and numbers; W entries; claims; change-list items); run the checker again. Then delete raw participant-level data from the scratch folder and record what was deleted under Deletions.

**Done when:** all three verifiers have returned, every verifier item has a disposition, the checker is clean, and the deletion is recorded.
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest tests/test_check_report.py tests/test_paper_critical_analysis_skill.py -q`

Expected: all pass — the new test, `test_every_brief_placeholder_is_documented[verify.md]` (`{CHECK}` and `{DRAFT_PATH}` are documented in the trailing prose), `test_every_brief_that_handles_locators_is_given_the_convention[verify.md]`, and `test_the_stages_run_in_order_and_none_went_missing`.

- [ ] **Step 6: Form and commit**

mdformat realigns the stage 7 table; the test reads cells by position, so the realignment is harmless.

```bash
ruff format tests/test_paper_critical_analysis_skill.py
ruff check tests/test_paper_critical_analysis_skill.py
mdformat --number --wrap keep skills/paper-critical-analysis/prompts/verify.md skills/paper-critical-analysis/SKILL.md
python -m pytest tests/test_paper_critical_analysis_skill.py -q
git add skills/paper-critical-analysis/prompts/verify.md skills/paper-critical-analysis/SKILL.md tests/test_paper_critical_analysis_skill.py
git commit -m "feat(skills): the verifier runs as three parallel checks, each with its own inputs

The one verifier carried the paper, the images, the report, the evidence
file and the web in one context for three checks that need disjoint inputs
(57 minutes on Bloom). One brief, a {CHECK} selector, three dispatches.
Check 3 gains the claim-strength rule from the pair re-rating: a sentence
citing an N, C, W or J entry says no more than the entry does (four Bloom
instances stated a notch firmer than their entry). Closes #220's
claim-strength item.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- skills/paper-critical-analysis/prompts/verify.md skills/paper-critical-analysis/SKILL.md tests/test_paper_critical_analysis_skill.py
```

______________________________________________________________________

## Task 5: The judge receives only the page renders the evidence file cites

**Files:**

- Modify: `skills/paper-critical-analysis/SKILL.md:88` (stage 3 dispatch sentence)
- Modify: `skills/paper-critical-analysis/prompts/judge.md:10` (`{PAGE_RENDERS}` parenthetical — an addition to the spec's Migration list, see "Spec readings settled here")
- Test: `tests/test_paper_critical_analysis_skill.py`

**Interfaces:**

- Consumes: Task 4's `verify.md`, whose check 1 parenthetical reads `images of every page carrying a figure, table or equation`.

- Produces: nothing other tasks use. Stage 0's render-every-page rule and stage 1's view-every-figure bar are untouched (spec non-goal); only what the judge is handed changes.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_paper_critical_analysis_skill.py`:

```python
def test_the_judge_and_the_verifier_describe_their_renders_differently():
    """The judge gets the renders the evidence file cites — its points cite
    only figures, tables and equations the evidence file already names, and
    every render cost Bloom's judge most of its 4.9M fresh tokens. Check 1 of
    the verifier gets every render, because it must find a number wherever
    the report points. One parenthetical copied over the other hands one of
    them the wrong set."""
    renders = re.compile(r"\{PAGE_RENDERS\} \(([^)]*)\)")
    judge = renders.search(_brief("judge.md"))
    verifier = renders.search(_brief("verify.md"))
    assert judge and verifier, "a brief lost its {PAGE_RENDERS} parenthetical"
    assert "cites" in judge.group(1)
    assert "every page" in verifier.group(1)
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_paper_critical_analysis_skill.py::test_the_judge_and_the_verifier_describe_their_renders_differently -q`

Expected: FAIL on `assert "cites" in judge.group(1)` (judge.md still says `images of pages carrying figures, tables or equations`).

- [ ] **Step 3: Edit SKILL.md stage 3**

In `skills/paper-critical-analysis/SKILL.md`, under `## Stage 3 — Judge`, replace

```text
Run one subagent whose whole context is `prompts/judge.md` with its placeholders filled: the paper and its supplements, the page images, the evidence file, the Locators section above (verbatim), and the background file paths the load table assigns.
```

with

```text
Run one subagent whose whole context is `prompts/judge.md` with its placeholders filled: the paper and its supplements; the renders of the pages the evidence file cites — walk its claims, N and C entries and key-number lines for Figure, Table and Equation locators and hand over those pages only, since the points the judge writes cite what the evidence file already names; the evidence file; the Locators section above (verbatim); and the background file paths the load table assigns.
```

- [ ] **Step 4: Edit the judge brief's parenthetical**

In `skills/paper-critical-analysis/prompts/judge.md`, in the Inputs section, replace

```text
and {PAGE_RENDERS} (images of pages carrying figures, tables or equations; "none" if none).
```

with

```text
and {PAGE_RENDERS} (renders of the pages carrying the figures, tables and equations the evidence file cites; "none" if none).
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest tests/test_check_report.py tests/test_paper_critical_analysis_skill.py -q`

Expected: all pass.

- [ ] **Step 6: Form and commit**

```bash
ruff format tests/test_paper_critical_analysis_skill.py
ruff check tests/test_paper_critical_analysis_skill.py
mdformat --number --wrap keep skills/paper-critical-analysis/prompts/judge.md skills/paper-critical-analysis/SKILL.md
git add skills/paper-critical-analysis/prompts/judge.md skills/paper-critical-analysis/SKILL.md tests/test_paper_critical_analysis_skill.py
git commit -m "feat(skills): the judge receives only the page renders the evidence file cites

Bloom's judge carried all 56 page images at 4.9M fresh tokens while its
points cited only the figures, tables and equations the evidence file
already names. The set is read off the evidence file at dispatch; dropping
images entirely stays the A/B arm, not the default.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- skills/paper-critical-analysis/prompts/judge.md skills/paper-critical-analysis/SKILL.md tests/test_paper_critical_analysis_skill.py
```

______________________________________________________________________

## Task 6: Code and data reach the context as script-extracted excerpts

**Files:**

- Modify: `skills/paper-critical-analysis/references/released-artifacts.md` (new section between `## What to open` and `## What never to open or fetch`)

**Interfaces:**

- Produces: nothing other tasks use. The reference file is loaded by stage 0's conditions table and stage 2's W-list bullet, both unchanged.

- [ ] **Step 1: Add the section**

In `skills/paper-critical-analysis/references/released-artifacts.md`, after the `## What to open` paragraph (ends `...not against the paper's description of it.`) and before `## What never to open or fetch`, insert:

```text
## How to read

Code and data reach the main context as excerpts a script extracts, never as whole files. Open a code file at the functions a check names — the analysis behind one headline number — and read those lines; never read a data file into context — a script computes the aggregate a check needs, and you read its output. The recomputation scripts a run writes already work this way; this rule forbids the whole-file reads around them, which bloated the Bloom run's main context to 13.9M fresh tokens.
```

- [ ] **Step 2: Verify**

Run: `python -m pytest tests/test_paper_critical_analysis_skill.py -q`

Expected: all pass (`test_every_shipped_path_the_skill_and_briefs_cite_exists` and `test_every_reference_file_is_reachable_from_the_load_table` still see the same file at the same path). Then read the file top to bottom once: the new section sits between "What to open" and "What never to open or fetch", and nothing in it contradicts "How to handle data" (download only what a recomputation needs; aggregates only).

- [ ] **Step 3: Form and commit**

```bash
mdformat --number --wrap keep skills/paper-critical-analysis/references/released-artifacts.md
git add skills/paper-critical-analysis/references/released-artifacts.md
git commit -m "docs(skills): code and data reach the context as script-extracted excerpts

Bloom's main context ran to 13.9M fresh tokens on whole-file reads of the
released repository and data around probe scripts that already extracted
what each check needed. The excerpt rule forbids the reads around them.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- skills/paper-critical-analysis/references/released-artifacts.md
```

______________________________________________________________________

## Task 7: Tools run from inside the output folder

**Files:**

- Modify: `skills/paper-critical-analysis/SKILL.md:29` (the Write-scope rule)
- Modify: `skills/paper-critical-analysis/prompts/judge.md` (Delegation section, last line)
- Modify: `skills/paper-critical-analysis/prompts/edit.md` (Delegation section, last line)
- Modify: `skills/paper-critical-analysis/prompts/verify.md` (Delegation section, add a line)
- Test: `tests/test_paper_critical_analysis_skill.py`

**Interfaces:**

- Consumes: Task 3's `edit.md` and Task 4's `verify.md` Delegation sections, as rewritten there.

- Produces: the phrase `working directory` in all three briefs and in SKILL.md's Write-scope rule, which the test pins.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_paper_critical_analysis_skill.py`:

```python
def test_every_brief_keeps_tools_inside_the_scratch_folder():
    """The 2026-10-04 write-scope audit found one leak: a runner type-checked
    its scratch scripts with mypy from the repo root, and mypy cached at its
    working directory. Files were already confined to the output folder;
    tools were not. The rule and every brief name the working directory."""
    text = _skill_text()
    rule = text[text.index("**Write scope.**") :].split("\n", 1)[0]
    assert "working directory" in rule
    for brief_name in BRIEFS:
        brief = _brief(brief_name)
        assert "working directory" in brief, f"{brief_name} says nothing about cwd"
        assert "<paper-slug>-work/" in brief, f"{brief_name} never names the scratch folder"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_paper_critical_analysis_skill.py::test_every_brief_keeps_tools_inside_the_scratch_folder -q`

Expected: FAIL on `assert "working directory" in rule`.

- [ ] **Step 3: Edit the Write-scope rule**

In `skills/paper-critical-analysis/SKILL.md`, under `## Rules`, replace

```text
- **Write scope.** Every file the run creates, scratch work included, goes in the output folder.
```

with

```text
- **Write scope.** Every file the run creates, scratch work included, goes in the output folder, and every tool runs from inside it, so a tool that caches at its working directory (mypy, for one) caches there too.
```

- [ ] **Step 4: Edit the judge and editor briefs**

In both `skills/paper-critical-analysis/prompts/judge.md` and `skills/paper-critical-analysis/prompts/edit.md`, in the Delegation section, replace

```text
Any file you create goes in the scratch folder beside the evidence file (`<paper-slug>-work/`), and nowhere else.
```

with

```text
Any file you create goes in the scratch folder beside the evidence file (`<paper-slug>-work/`), and nowhere else; run every tool from inside it, so a tool that caches at its working directory caches there too.
```

- [ ] **Step 5: Edit the verifier brief**

In `skills/paper-critical-analysis/prompts/verify.md`, in the Delegation section, after the paragraph ending `...would re-read the skill and fan out again.` add a paragraph:

```text
Run any tool from the scratch folder (`<paper-slug>-work/`, in the folder holding your inputs), so a tool that caches at its working directory caches there; you still create no file of your own.
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `python -m pytest tests/test_check_report.py tests/test_paper_critical_analysis_skill.py -q`

Expected: all pass, `test_each_verifier_dispatch_fills_exactly_its_checks_inputs` included (the new paragraph adds no placeholder).

- [ ] **Step 7: Form and commit**

```bash
ruff format tests/test_paper_critical_analysis_skill.py
ruff check tests/test_paper_critical_analysis_skill.py
mdformat --number --wrap keep skills/paper-critical-analysis/SKILL.md skills/paper-critical-analysis/prompts/judge.md skills/paper-critical-analysis/prompts/edit.md skills/paper-critical-analysis/prompts/verify.md
git add skills/paper-critical-analysis/SKILL.md skills/paper-critical-analysis/prompts/judge.md skills/paper-critical-analysis/prompts/edit.md skills/paper-critical-analysis/prompts/verify.md tests/test_paper_critical_analysis_skill.py
git commit -m "fix(skills): tools run from inside the output folder, so cwd caches land there

The acceptance runs' write-scope audit found one leak: a .mypy_cache at
the repo root, from a runner type-checking its scratch scripts from there.
Files were confined; tools were not. Closes the write-scope item on #220.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- skills/paper-critical-analysis/SKILL.md skills/paper-critical-analysis/prompts/judge.md skills/paper-critical-analysis/prompts/edit.md skills/paper-critical-analysis/prompts/verify.md tests/test_paper_critical_analysis_skill.py
```

______________________________________________________________________

## Task 8: Branch close-out — full gate, push, merge, issue comments

**Files:** none modified; this task runs the gates and the git workflow from `AGENTS.md`.

- [ ] **Step 1: Full offline suite**

Run from the repo root inside `.venv`: `python -m pytest tests -q -n auto`

Expected: all pass, no new skips. If anything fails, fix it in the task that owns the file (amend nothing; add a `fix:` commit with pathspec) before going on.

- [ ] **Step 2: Form check on every touched file**

```bash
ruff format --check skills/paper-critical-analysis/scripts/check_report.py tests/test_check_report.py tests/test_paper_critical_analysis_skill.py
ruff check skills/paper-critical-analysis/scripts/check_report.py tests/test_check_report.py tests/test_paper_critical_analysis_skill.py
mdformat --number --wrap keep --check skills/paper-critical-analysis/SKILL.md skills/paper-critical-analysis/prompts/*.md skills/paper-critical-analysis/templates/*.md skills/paper-critical-analysis/references/released-artifacts.md ATTRIBUTION.md
git status --porcelain
```

Expected: every check clean; `git status --porcelain` shows nothing of yours uncommitted (other sessions' files may show — leave them alone).

- [ ] **Step 3: Push and wait for the required check**

```bash
git push -u origin paper-critical-analysis-cost-tuning
SHA="$(git rev-parse HEAD)"
until RUN_ID="$(gh run list --commit "$SHA" --workflow quality --limit 1 --json databaseId --jq '.[0].databaseId')" && [ -n "$RUN_ID" ]; do sleep 10; done
gh run watch "$RUN_ID" --exit-status
```

The run appears a few seconds after the push; the loop waits for it rather than watching an empty id or a stale earlier run. Expected: the `quality` workflow is green. A red run names the failing job; fix on the branch, push again, wait again.

- [ ] **Step 4: Fast-forward merge into main and push**

From the worktree (no checkout changes anywhere — a ref push to `main` is fast-forward only by default and moves `main` to the exact sha the check ran on, which is what `AGENTS.md`'s `git merge --ff-only` + push achieves):

```bash
git fetch origin
git push origin paper-critical-analysis-cost-tuning:main
git log --oneline -1 origin/main
git -C /home/eranr/research-vault pull --ff-only origin main
```

Expected: the push succeeds and `origin/main` is the branch tip. If it is refused as non-fast-forward, `main` moved: `git rebase origin/main` in the worktree, `git push --force-with-lease origin paper-critical-analysis-cost-tuning`, wait for green again (Step 3), then retry. Never `--no-ff`: it mints a sha no check has run on. If the final `pull` into the shared main checkout refuses because another session has uncommitted work there, leave it — `origin/main` is the record, and Task 9 Step 2 re-checks the checkout before it runs.

Note the merged sha; Task 9 and the issue comments cite it.

- [ ] **Step 5: Comment on #219 and #220 (do not close)**

```bash
gh issue comment 219 --body "Landed on main (<merged sha>) from the cost-tuning spec: the report's front matter carries an \`Evidence file:\` line that the checker requires (one fixture); the evidence template says a computed entry carries its inputs and result on continuation lines and that a script name alone is not evidence (the W22-vs-J15 item); finding entries put their five fields one per continuation line; and \`not applicable: <reason>\` is a documented slot fill with \`Headline recomputations:\` as the worked example (the checker already accepted it; a test now pins that). Still open here: the Key-line coverage item (N, C and J IDs and 'Claim n' references are not in the Key), and whether the stage 1 records deserve their own headings."
gh issue comment 220 --body "Landed on main (<merged sha>) from the cost-tuning spec: the verifier now runs as three parallel checks of one brief, and check 3 holds the claim-strength rule — a sentence citing an N, C, W or J entry says no more than the entry does — generalizing the W-entry rule to the four instances the pair re-rating found. The write-scope rule and all three briefs say tools run from inside the output folder, so cwd caches (.mypy_cache) land there. The brief-wording, contract-test and attribution polish items stay open; the Strunk edition is now named in ATTRIBUTION.md as a side effect of retiring the stylistic pass."
```

Replace `<merged sha>` with the sha from Step 4 before running.

______________________________________________________________________

## Task 9: Acceptance — the CheckIfExist A/B run, scored against the pre-registered key

This task spends roughly 8M fresh tokens and about two hours of wall time on a live run. **Confirm with the user before Step 3 dispatches.** Everything before Step 3 is setup and costs nothing.

Its commits go on a second branch from the merged `main`, in a worktree of its own (`$WT` below); the shared main checkout is never switched off `main`:

```bash
cd /home/eranr/research-vault && git fetch origin
git worktree add .claude/worktrees/paper-critical-analysis-cost-tuning-ab -b paper-critical-analysis-cost-tuning-ab origin/main
WT=/home/eranr/research-vault/.claude/worktrees/paper-critical-analysis-cost-tuning-ab
```

**Files:**

- Create: `docs/research/2026-09-20-paper-critical-analysis-evals/mine_tokens.py`
- Create (git-ignored, under `sources/`): `sources/checkifexist-run2/PROMPT.md`, `sources/checkifexist-run2/rater-prompt.md`, `sources/checkifexist-run2/input/<paper>.pdf`, `sources/checkifexist-run2/dispatch.stamp`
- Modify: `docs/research/2026-09-20-paper-critical-analysis-evals/README.md` (new subsection after `### Results (2026-10-04, …)`)
- Modify: `skills/paper-critical-analysis/SKILL.md:9` (the cost sentence — only on the outcome the decision rule names)
- Modify: `docs/superpowers/specs/2026-10-04-paper-critical-analysis-cost-tuning-design.md:3` (status line)

**Interfaces:**

- Consumes: the merged skill at `/home/eranr/research-vault/skills/paper-critical-analysis/` at Task 8's merged sha; the key `sources/bloom-skill-comparison/checkifexist-answer-key.md` (15 scored items A1–A6, B1–B6, C1–C3; D1–D4 in prose); the 2026-10-04 baseline in `sources/bloom-skill-comparison/run3-setup.md` (CheckIfExist: 13.5/15, D1–D4 pass, 13.4M fresh, 2 h 49 m, verifiability 9 on the pair rating).

**Decision rule (from the spec, fixed before the run):**

- Targets: ≤ 8M fresh input tokens; wall time about 2 hours.

- Quality floor, all three required: (1) score ≥ 13 of 15 on the key; (2) D1–D4 all pass; (3) pair-rating verifiability ≥ 8.

- Floor holds → record the run; re-set SKILL.md's cost sentence to the measured numbers whether or not the targets were hit ("the floor wins and the bar is re-set from evidence"); mark the spec implemented.

- Floor fails on one criterion → record; leave SKILL.md's sentence alone; open one issue titled `paper-critical-analysis cost tuning: A/B floor miss on <criterion>` naming the miss and the change suspected (editor-lite → verifiability; verifier split → an unverified claim; judge diet → a missed key item citing a figure); do not merge anything further.

- Ambiguous (a miss that is a known variance item — A3 was missed on 2026-10-04 too; B2 scored ½) → the Bloom re-run the spec reserves for this case, as a separate decision with the user.

- The judge-images A/B arm (no images at all) is not run here; it gets its own issue only if the user wants it after this run lands clean.

- [ ] **Step 1: Write the token miner (the 2026-10-04 mining was done by hand; a retyped check belongs in a script)**

Create `$WT/docs/research/2026-09-20-paper-critical-analysis-evals/mine_tokens.py`:

```python
#!/usr/bin/env python3
"""Sum fresh input tokens over Claude Code transcripts.

Usage: python3 mine_tokens.py LABEL=transcript.jsonl [LABEL=transcript.jsonl ...]

"Fresh" is the comparison runs' definition (run3-setup.md, 2026-10-04):
uncached input plus cache-write, per API call — ``usage.input_tokens`` +
``usage.cache_creation_input_tokens`` on every assistant message. Cache reads
and output tokens are reported beside it. One row per label, then a total.
"""

import json
import sys
from pathlib import Path


def usage_rows(path: Path):
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        usage = (record.get("message") or {}).get("usage")
        if isinstance(usage, dict):
            yield usage


def totals(path: Path) -> tuple[int, int, int]:
    fresh = cached = output = 0
    for usage in usage_rows(path):
        fresh += usage.get("input_tokens", 0) + usage.get(
            "cache_creation_input_tokens", 0
        )
        cached += usage.get("cache_read_input_tokens", 0)
        output += usage.get("output_tokens", 0)
    return fresh, cached, output


def main(argv: list[str]) -> int:
    if not argv:
        sys.stderr.write(__doc__)
        return 2
    grand = [0, 0, 0]
    print(f"{'agent':<12} {'fresh in':>12} {'cache read':>12} {'output':>10}")
    for arg in argv:
        label, _, raw = arg.partition("=")
        fresh, cached, output = totals(Path(raw or label))
        grand = [a + b for a, b in zip(grand, (fresh, cached, output), strict=True)]
        print(f"{label:<12} {fresh:>12,} {cached:>12,} {output:>10,}")
    print(f"{'total':<12} {grand[0]:>12,} {grand[1]:>12,} {grand[2]:>10,}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

Smoke-test it on the 2026-10-04 CheckIfExist transcripts if they are still under `~/.claude/projects/`: the main-runner row should read about 7.30M fresh (run3-setup.md's table). If the transcripts are gone, test on any transcript and eyeball that the numbers are non-zero; note which you did in the README record.

- [ ] **Step 2: Build the run root**

```bash
cd /home/eranr/research-vault
git status --porcelain skills/paper-critical-analysis   # must print nothing
git log -1 --format=%H -- skills/paper-critical-analysis   # must equal Task 8's merged sha
mkdir -p sources/checkifexist-run2/input sources/checkifexist-run2/paper-critical-analysis
cp "sources/checkifexist-run/input/Abbonato - 2026 - CheckIfExist Detecting Citation Hallucinations in the Era of AI-Generated Content.pdf" sources/checkifexist-run2/input/
sha256sum sources/checkifexist-run/input/*.pdf sources/checkifexist-run2/input/*.pdf   # the two hashes match
ls sources/checkifexist-run2/paper-critical-analysis/   # empty: an existing evidence file would make the run a resume
```

Write `sources/checkifexist-run2/PROMPT.md` — the 2026-10-04 prompt with only the run-root paths changed:

```text
Critique a paper using the skill at `/home/eranr/research-vault/skills/paper-critical-analysis/`: read its `SKILL.md` in full and follow it exactly, resolving the skill's relative paths against that directory.

Paper (first argument): `/home/eranr/research-vault/sources/checkifexist-run2/input/Abbonato - 2026 - CheckIfExist Detecting Citation Hallucinations in the Era of AI-Generated Content.pdf`

It is the only input; the paper names no supplements.

Output folder (second argument): `/home/eranr/research-vault/sources/checkifexist-run2/paper-critical-analysis/`

Keep a run log in the output folder as you go: the run is unattended, and every decision you make that the skill leaves open is recorded there with its reason.

Boundaries: do not read anything under `/home/eranr/research-vault/sources/` outside `/home/eranr/research-vault/sources/checkifexist-run2/`, and do not read `/home/eranr/research-vault/docs/research/2026-09-20-paper-critical-analysis-evals/` or `/home/eranr/research-vault/docs/superpowers/`. Nothing in the repository is needed beyond the skill's own directory and your run folder.
```

Write `sources/checkifexist-run2/rater-prompt.md` now, before the run exists, so the rubric is on disk this time (the 2026-10-04 rubric survives only as run3-setup.md's description of it; this reconstructs it):

```text
You are a reader deciding whether to trust and use the paper this report describes. You are not a referee and you have no answer key. Read the report and its evidence file:

- Report: /home/eranr/research-vault/sources/checkifexist-run2/paper-critical-analysis/critical-analysis-checkifexist.md
- Evidence file: /home/eranr/research-vault/sources/checkifexist-run2/paper-critical-analysis/critical-analysis-checkifexist.evidence.md

Read nothing else. Return:

1. Overall, 1–10: how far this report lets you decide whether to trust and use the paper, and whether you would hand it to a colleague.
2. Verifiability, 1–10: how far you can check the report's distinctive numbers and claims from what you hold — pick six, try to trace each to the paper locator or evidence entry it cites, and say what happened to each.
3. Calibration, 1–10: whether the verdicts match the evidence shown for them.
4. Trust-lowering items: every sentence in the report that states more than the evidence entry or locator it cites supports — quote the sentence and the entry.
5. Leads: anything the report should have run down and did not.

Scores first, one line each, then the lists.
```

Stamp the dispatch for the write-scope audit: `touch sources/checkifexist-run2/dispatch.stamp`.

- [ ] **Step 3: Dispatch the run (user-confirmed)**

Confirm the spend with the user. Then dispatch one Opus runner with the exact text of `sources/checkifexist-run2/PROMPT.md` as its prompt (Agent tool, `subagent_type: general-purpose`, `model: opus` — the runner must be able to spawn its own judge, editor and three verifiers). Record the dispatch wall-clock time. Do not poll it; wait for its completion notice.

- [ ] **Step 4: Score and audit**

In this order, recording each result in a scratch note `sources/checkifexist-run2/scoring.md`:

1. Checker: `python3 skills/paper-critical-analysis/scripts/check_report.py sources/checkifexist-run2/paper-critical-analysis/critical-analysis-checkifexist.md` — expected `ok`; record warnings.
2. Key: walk `sources/bloom-skill-comparison/checkifexist-answer-key.md` item by item (A1–A6, B1–B6, C1–C3) against the final report and evidence file, crediting ✓ / ½ / ✗ as the key's header defines; then D1–D4 in prose. Compare with the 2026-10-04 scorecard in `run3-setup.md` item by item.
3. Wall time: the evidence file's Stage log (`stage <n>: met — <time>`) gives stage 0 and stage 7; also the dispatch-to-completion time from Step 3.
4. Tokens: locate the transcripts of the run's agents (the runner and every subagent it spawned — judge, editor, verifier 1, 2, 3 — under `~/.claude/projects/`, by the run's timestamps) and run `python3 $WT/docs/research/2026-09-20-paper-critical-analysis-evals/mine_tokens.py main=<…> judge=<…> editor=<…> v1=<…> v2=<…> v3=<…>`.
5. Write-scope audit: `find /home/eranr/research-vault /tmp -newer sources/checkifexist-run2/dispatch.stamp -not -path '*/sources/checkifexist-run2/*' -not -path '*/.git/*' 2>/dev/null` — expected: nothing attributable to the run (attribute anything found by content, as run3-setup.md did). Confirm no `.mypy_cache` outside the output folder.
6. Pair rating: dispatch a fresh Opus agent with the exact text of `sources/checkifexist-run2/rater-prompt.md`; save its return as `sources/checkifexist-run2/rater-return.md`.
7. Verifier dispositions: from the evidence file's Verifier list, the four counts (locators/quotes/numbers; W entries; claims; change-list items) and how many failures each check raised — the claim-strength check's count is new and gets recorded on its own.

- [ ] **Step 5: Apply the decision rule and record**

In the worktree, add to `$WT/docs/research/2026-09-20-paper-critical-analysis-evals/README.md`, after the `### Results (2026-10-04, …)` subsection and before the `Deferred review findings` paragraph, a subsection in the README's existing voice:

```text
### Cost-tuning A/B (CheckIfExist, <date>, skill at <merged sha>)

One run, same prompt and pre-registered key as 2026-10-04, after the cost-tuning spec (`docs/superpowers/specs/2026-10-04-paper-critical-analysis-cost-tuning-design.md`): editor without its stylistic pass, verifier as three parallel checks, judge handed only cited page renders, excerpt rule for code and data. Artifacts local and git-ignored in `sources/checkifexist-run2/` (prompt, rater prompt and return, run log, scoring note).

**Score: <n> of 15** on the key (<per-item deltas against 2026-10-04's 13.5: name each item that changed>). D1–D4: <pass/fail each>. Pair rating: overall <n>, verifiability <n>, calibration <n>; <count> trust-lowering items (<one line on their class, or "none">).

**Cost:** <n>M fresh input tokens against 13.4M (main <n>M, judge <n>M, editor <n>M, verifiers <n>M + <n>M + <n>M; mined with `mine_tokens.py`), wall <h> h <m> m against 2 h 49 m (stage timeline: <stage 0 time> … <stage 7 time>). Targets: ≤ 8M and about 2 h — <met / missed by how much>.

**Verifier counts:** <locators/quotes/numbers checked, failed>; <W entries checked, failed>; <claims checked, failed — the new claim-strength check>; <change-list items checked, failed>. Checker: <ok / warnings>. Write-scope audit: <clean / what was found>.

**Disposition:** <floor holds → "SKILL.md's cost sentence re-set to the measured numbers"; floor fails → "issue #<n> opened; SKILL.md unchanged"; ambiguous → "Bloom re-run pending the user's call">.
```

Fill every `<…>`; a slot with no value reads `not measured: <reason>` (the Nothing-silent rule applies to run records too).

Then, **only if the floor holds**, in `$WT/skills/paper-critical-analysis/SKILL.md` line 9 replace

```text
on a 33-page paper expect about 8M fresh tokens and about 2 hours.
```

with the measured figures, in the same shape, naming the paper class — for example `on a 9-page paper expect about <n>M fresh tokens and about <h> hours; a 33-page paper with released code ran <n>M before this tuning.` (Use the measured numbers; do not keep this example's placeholders.)

In `$WT/docs/superpowers/specs/2026-10-04-paper-critical-analysis-cost-tuning-design.md`, replace the status line's `Status: draft, awaiting review` with `Status: implemented on main at <merged sha>; A/B result in the evals README (<date>)`.

- [ ] **Step 6: Commit, push, merge**

From `$WT`, inside the repo's `.venv`:

```bash
cd "$WT"
ruff format docs/research/2026-09-20-paper-critical-analysis-evals/mine_tokens.py
ruff check docs/research/2026-09-20-paper-critical-analysis-evals/mine_tokens.py
mdformat --number --wrap keep docs/research/2026-09-20-paper-critical-analysis-evals/README.md skills/paper-critical-analysis/SKILL.md docs/superpowers/specs/2026-10-04-paper-critical-analysis-cost-tuning-design.md
PYTHONPATH=. python -m pytest tests -q -n auto
git add docs/research/2026-09-20-paper-critical-analysis-evals/mine_tokens.py docs/research/2026-09-20-paper-critical-analysis-evals/README.md skills/paper-critical-analysis/SKILL.md docs/superpowers/specs/2026-10-04-paper-critical-analysis-cost-tuning-design.md
git commit -m "docs(evals): cost-tuning A/B on CheckIfExist — <score>/15, <n>M fresh, <time>

<One sentence: floor held or failed, and what was re-set or opened.>

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- docs/research/2026-09-20-paper-critical-analysis-evals/mine_tokens.py docs/research/2026-09-20-paper-critical-analysis-evals/README.md skills/paper-critical-analysis/SKILL.md docs/superpowers/specs/2026-10-04-paper-critical-analysis-cost-tuning-design.md
git push -u origin paper-critical-analysis-cost-tuning-ab
```

Drop `skills/paper-critical-analysis/SKILL.md` from the `git add` and `git commit` pathspecs if the floor failed and the sentence was not changed. Wait for the `quality` check as in Task 8 Step 3 (same loop, this branch's sha), then fast-forward `main` as in Task 8 Step 4: `git push origin paper-critical-analysis-cost-tuning-ab:main`, then `git -C /home/eranr/research-vault pull --ff-only origin main`. Afterwards `git -C /home/eranr/research-vault worktree remove .claude/worktrees/paper-critical-analysis-cost-tuning-ab && git worktree prune`. Leave `sources/checkifexist-run2/` where it is: git-ignored evidence, like its predecessors.
