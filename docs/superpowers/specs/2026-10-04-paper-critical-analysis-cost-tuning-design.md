# Design: cost tuning for paper-critical-analysis

Date: 2026-10-04. Status: draft, awaiting review — supersedes nothing; amends the merged skill at `89f3a8c`. Branch: `paper-critical-analysis-cost-tuning`.

## Goal

Cut the skill's fresh-token cost by roughly 40% and its wall time by roughly 30%, with a measured quality floor: the acceptance results stand (Bloom 19/20, CheckIfExist 13.5/15, every targeted fix bound, blind pair rating 9/10 with verifiability 9). Spend that produced findings is untouched; the cuts land only where the acceptance runs measured spend that did not.

## Evidence

Both acceptance runs (2026-10-04, one Opus runner per paper; full accounting in the evals README and `sources/bloom-skill-comparison/run3-setup.md`):

| Agent     | Bloom fresh in | CheckIfExist fresh in | Wall (Bloom / CIE)  | What it bought                                      |
| --------- | -------------- | --------------------- | ------------------- | --------------------------------------------------- |
| main      | 13.9M          | 7.3M                  | —                   | the findings; bloated by whole-file repo/data reads |
| judge     | 4.9M           | 2.4M                  | 41 m / 33 m         | the points; carries all 56 page images today        |
| editor    | 1.3M           | 2.5M                  | 31 m / 49 m         | −166 and −49 words net; zero findings by design     |
| verifier  | 2.2M           | 1.2M                  | 57 m / ~35 m        | 12 + 7 fixes, incl. the wrong-outside-claim class   |
| **total** | **22.2M**      | **13.4M**             | 3 h 28 m / 2 h 49 m |                                                     |

Three observations drive the design:

- The editor's stylistic sweep and per-passage accounting bar produced most of its 51 + 46 items and most of its 80 combined minutes, while the reader-visible value sat in the structural moves and the copy flags. The stage's premise — an author reviewing its own text keeps everything — is **unmeasured by these runs, not refuted**: the pre-edit drafts were already tight.
- The verifier carries the paper, the images, the report, the evidence file and the web in one context, although its three checks need disjoint inputs.
- The judge receives every page render, although the points it writes cite only the figures, tables and equations the evidence file already names.

## Decisions

| Question                  | Decision                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Editor scope              | Structural pass and copy flags only; the stylistic pass and the per-passage accounting bar ("every rule applied to every passage") are dropped. Items are returned only where a change is proposed; **Before** stays verbatim on every item, because the verifier's drift check consumes it.                                                                                                                                         |
| Judge page images         | The judge receives only the renders of pages that the evidence file's locators cite (figures, tables, equations named in claims, N, C or key-number lines) — derivable mechanically from the evidence file at dispatch. Dropping images entirely is the A/B arm, not the default.                                                                                                                                                    |
| Verifier shape            | One brief, three parallel dispatches. `prompts/verify.md` gains a `{CHECK}` selector and three per-check `## Inputs` subsections; each dispatch runs one check with only that check's inputs. V1 (locators/quotes/numbers): the paper, its images, the report — nothing else. V2 (W entries): the evidence file, the scratch saved copies, the web. V3 (edit drift + claim strength): the report, the draft, the full evidence file. |
| Claim-strength check      | V3 gains the generalized rule: a claim citing an N, C or J entry says no more than the entry does — the existing W-entry rule extended. (From the pair rating: four instances where the report stated a notch firmer than its entry supports.)                                                                                                                                                                                       |
| Artifact reads            | `references/released-artifacts.md` adds: code and data reach the main context as script-extracted excerpts; a whole data file is never read into context, and code files are opened at the functions a check names. The probe scripts already work this way; this forbids the full-file reads around them.                                                                                                                           |
| Model guidance            | SKILL.md stages 5 and 7 note that the editor and verifier briefs do not require the strongest model; dispatch them on a smaller one where the harness offers the choice. Guidance, not mechanism — the dispatcher owns model selection.                                                                                                                                                                                              |
| Evidence pointer          | The report template's front matter gains a literal line `Evidence file: critical-analysis-<paper-slug>.evidence.md, alongside this report.` and the checker requires `^Evidence file: ` exactly as it requires the `Key:` line, with one failing fixture. (Pair rating: the report alone scored 5/10 on verifiability; the pointer survives the file leaving its folder.)                                                            |
| Computed evidence entries | The evidence template's entry guidance adds: a computed entry carries its inputs and result in the entry, in the shape the acceptance run's W22 used; a script name alone is not evidence. (J15 named a script and showed nothing.)                                                                                                                                                                                                  |
| Finding-entry shape       | The evidence template says finding entries should use the already-legal indented continuation lines for the five fields, one per line, instead of one semicolon chain.                                                                                                                                                                                                                                                               |
| Mandated-slot semantics   | The evidence template states that `not applicable: <reason>` is a legal slot fill (the checker already accepts it); CheckIfExist's `Headline recomputations:` slot is the worked example.                                                                                                                                                                                                                                            |

Drive-by on the same branch, outside the cost story: the write-scope rule and the three briefs say tools run from inside the output folder, so cwd-caching tools (mypy) cache there — closes the one leak the write-scope audit found.

## Non-goals

- Stage 2 exhaustiveness, the mandated-check slots, the released-code reading mandate, stage 1's view-every-figure bar: untouched — that is where 19/20 came from.
- Shrinking verifier coverage: all three checks keep their full item counts; the split changes contexts, not scope.
- Chasing the original ~8.5M bar at any cost: if the measured floor (below) and 8.5M conflict, the floor wins and the bar is re-set from evidence.
- A fast mode, a deep mode, or any second depth.

## Expected effect

Estimates against the Bloom run, honest ranges: editor-lite −1 to −2M and −20 to −35 m; verifier split −0.5 to −1M and −25 to −35 m of wall (parallel); judge image diet −1 to −2M; artifact-excerpt discipline −2 to −4M on repo-heavy papers. Combined: roughly 22.2M → 13–16M and 3 h 28 m → about 2 h 15 m on a Bloom-class paper; model guidance cuts dollars beyond tokens.

## Testing and evaluation

Offline: the full suite; contract tests updated for the brief's `{CHECK}` selector and per-check input lists (one new test: the three input lists in `prompts/verify.md` match what SKILL.md stage 7 says to fill per dispatch), the new checker rule and fixture for the `Evidence file:` line, and the template-wording changes.

Behavioural, one A/B run: **CheckIfExist** with the same prompt and the pre-registered key (`sources/bloom-skill-comparison/checkifexist-answer-key.md`). Targets: ≤8M fresh tokens and about 2 hours. Quality floor, all three required:

1. score ≥ 13 of 15 on the key;
2. D1–D4 all pass;
3. a pair rating (report + evidence file, same rubric as 2026-10-04) keeps verifiability ≥ 8 — the one number the editor and evidence-shape changes could move.

A Bloom re-run only if the CheckIfExist result is ambiguous. The judge-images A/B arm (no images at all) runs only after the default lands clean.

## Migration

All on this branch, only after this spec passes review:

- `skills/paper-critical-analysis/SKILL.md`: stage 3 image-selection sentence; stage 5 scope sentence; stage 7 three-dispatch instructions and model-guidance notes; write-scope clause.
- `prompts/edit.md`: drop the stylistic pass and the accounting bar; keep structural, copy flags, invariant, verbatim Before.
- `prompts/verify.md`: `{CHECK}` selector, per-check inputs, V3's claim-strength rule.
- `references/released-artifacts.md`: excerpt rule.
- `templates/report-template.md`: `Evidence file:` line. `templates/evidence-template.md`: computed-entry rule, continuation-line guidance, slot-semantics sentence.
- `scripts/check_report.py` + `tests/test_check_report.py`: the `Evidence file:` rule and fixture.
- `tests/test_paper_critical_analysis_skill.py`: the verify-brief input-list test; placeholder updates.
- Issues: #219's evidence-shape items and #220's claim-strength item close with this; the judge-images A/B gets its own issue if the arm is wanted.
