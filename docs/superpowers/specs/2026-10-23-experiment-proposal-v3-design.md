# Design: experiment-proposal v3, usable by agents, checked where it can be

Date: 2026-10-23. Status: approved in brainstorming, awaiting spec review. Branch: `experiment-proposal-v3`. Supersedes `docs/superpowers/specs/2026-10-14-experiment-proposal-v2-design.md` where it changes it; every v2 decision not named here stands.

## Why

The plugin's second use, on the author's own proposal (the Bloom response-length study, 15 to 23 October 2026), was the first with full material and a comparison against another process. Four findings drive this release:

1. Agents could not run the skills. All four are user-invoked only, so an orchestrating agent re-ran each `SKILL.md` by hand from a pasted path, and the design decisions lived outside the brief until the brief was back-filled.
2. `lit-search` degraded on every round: Semantic Scholar answered HTTP 429 on each keyword query, DBLP returned nothing to any query, the snowball output was not valid YAML (one unquoted title split across lines), and the second round had no way to drop the 361 records already judged.
3. The draft checker mis-measured two things the course rule asks for: an ACM-numbered reference list (`[1] ...` lines) counted as one entry, and `--references` counted the whole list while the rule covers the literature review, so the author had to widen the bounds.
4. The review's most expensive manual step, cross-section consistency of numbers, is mechanical to search and only its judgment needs a reader.

The lens is unchanged: the plugin produces the course proposal and is judged by it.

## Decisions

| Question | Decision |
| --- | --- |
| Agent use | Skills become model-invocable by name with a name-only description and no trigger phrases; each `SKILL.md` gains an Agent run paragraph. Codex keeps `allow_implicit_invocation: false` pending the test below. |
| Checker references | `[n]` lines count as entries; `--references A-B` checks distinct citations inside the Literature Review section; the list total is a second, informational line. |
| Checker numbers | `draft --numbers` prints a report of values near keywords with locations; `review` reads it for the cross-section row. No declared constants, no new brief shape. |
| Checker word count | Unchanged (headings, title block, and tables count; references and appendices do not); documented in the README as the conservative reading. |
| Attested rows | `not confirmed` is an accepted result on attested items only. |
| lit-search | A wrapper of our own, `scripts/litsearch.py`, around the vendored scripts: 429 backoff, lenient parse, valid YAML out, `--exclude` by DOI, `--compact`, per-source counts with the query echoed. Vendored files untouched. Upstream: one PR (YAML quoting, 429 backoff), one issue (DBLP empty). |
| Ethics board | Not consumed by `review`. If `proposal/ethics-review.md` exists, item 12.3's row and the hand-off seed list name it with the count of revision entries not yet marked Applied. |
| Codex | Kept and tested; mirror the Claude behavior (callable by name, triggered by nothing). |
| Release | One release, 0.3.0, tag `experiment-proposal--v0.3.0`; scenarios 2, 3, 5, 6 re-run once each; new real-material scenario 8 recorded without a bar. |

Out of scope, considered and rejected: one combined CLI (renames a script every reference file cites, for no shape change); `review` parsing the ethics board's revision list (no checked shape, imports rules the lens does not ask for); declared constants in the brief (a shape that can go stale, and regexes that misfire on legitimate other numbers).

## 1. Invocation and agent mode

Frontmatter of `design`, `review`, `lit-search`: `disable-model-invocation` removed; `description` is one line that names the skill and what it produces, with no trigger phrases, for example:

- design: "Invoked by name: settles a controlled experiment's design decisions in numbered rounds and freezes them in proposal/design-brief.md."
- review: "Invoked by name: checks a written experiment proposal against its frozen design brief and the checklist, writes proposal/review.md."
- lit-search: "Invoked by name: searches scholarly indexes and snowballs from seed DOIs for a literature review's sources; writes no files."

`the-ethics-board` is vendored: the flag is removed and its description is shortened to a name-only line as a second marked local edit, with the provenance comment updated. Its upstream body stays.

Each `SKILL.md` ends with a paragraph headed **Agent run**: when no human answers (the caller is an agent, or `claude -p` without `--continue`), the skill does not wait. `design` marks every unanswered frontier item `provisional` with the recommendation standing in and leaves the brief `open`. `review` records attested items (3.1, 5.2, 13.1, 13.4) as `not confirmed`, takes the course defaults at item 3.1, applies no fixes, and returns the file path and the Summary line. `lit-search` and `the-ethics-board` return their report. Nothing else in the steps changes.

README: an "Agent use" paragraph after Commands: call a skill by name from any agent; the agent-run behavior; the headless paragraph stays as is.

Codex: `agents/openai.yaml` unchanged for now. The Codex test (section 5) invokes each skill by name from a prompt. If `allow_implicit_invocation: false` admits a named instruction, nothing changes; if it refuses, the four yaml files flip to `true` and rely on the name-only description, and the README records which. Either way the README's Codex paragraph names the result.

## 2. The checker

`scripts/check_proposal.py` stays standard library, Python 3.11 or later, no network, no writes.

- `LIST_ITEM` also matches `^\[\d+\] `, so ACM-numbered reference lines are entries.
- `draft --references A-B` checks the count of distinct citations in the Literature Review section: `[n]` numbers found between its heading and the next heading of the same or higher level, split on commas and ranges inside one bracket; when no bracketed numbers occur in that section, `(Surname, year)` or `Surname [year]` keys, de-duplicated. The section is the one matching the second name in `--sections` (default "Literature Review"). A second line, `references: <N> entries in the list`, is informational and never a defect. The defect message names which count failed.
- `draft --numbers`: scans the body and appendices for a number within six words of a keyword from a fixed list (participants, N, minutes, min, session, items, sequences, turns, words, `$`, `%`), and prints, grouped by keyword, each distinct value with its locations (section or appendix heading and line). Exit 0 always; output to stdout; `--json` honored. It judges nothing.
- `review`: `not confirmed` joins the accepted results, valid only on the rows of items 3.1, 5.2, 13.1 and 13.4; on any other row it is a defect "attested result on a draft-checked item". The Summary line counts it under Fail.
- Word count unchanged.

`references/review.md`: the Items rules name `not confirmed`; the Cross-section section says the report is the search and the reviewer's lines are the findings. `references/brief.md`: unchanged.

## 3. lit-search wrapper and upstream

New `skills/lit-search/scripts/litsearch.py`, ours (not vendored), standard library, Python 3.11 or later. It is the only script the skill names.

- Subcommands mirror the vendored ones: `litsearch.py search "<query>" --limit N` and `litsearch.py snowball <DOI...> --direction both --limit-per-seed N`; both accept `--exclude <file>`, `--compact`, `--out <file>`.
- It runs the vendored `search.py` or `snowball.py` with `python3 -B` as a subprocess from the current directory (the key file lookup is unchanged), capturing stdout and stderr.
- Backoff: a stderr degradation note containing `HTTP 429` triggers up to three re-runs of the same command after 20, 40, and 80 seconds, keeping the best result per source (the run in which that source returned records); each retry is reported on stderr.
- Parse: the captured YAML is read leniently (a line that is not a key-value pair inside a quoted-string context is appended to the previous title or abstract), records are de-duplicated by DOI within the run, and records whose DOI (case-insensitive, without a `https://doi.org/` prefix) appears in the exclude file, one per line, are dropped and counted.
- Output: valid YAML with every string quoted, written to stdout or `--out`; `--compact` keeps `title`, `author` (surnames), `issued` year, `container-title`, `DOI`, and `abstract` truncated to 300 characters.
- Summary on stderr, one line per source: `<source>(<returned>, <kept after exclude>) query="<query>"`, then the vendored notes verbatim, then `excluded: <n>`.

`SKILL.md` steps 2 to 4 call the wrapper; the exclude file is `proposal/notes/lit-search-judged.txt`, which the judge appends every judged DOI to before the next round; `--compact` is the default after round 1. The vendored scripts and their provenance header are untouched; THIRD-PARTY-NOTICES is unchanged until a re-vendor.

Upstream (hutzelmann/thesis-proposal-skills): one pull request that quotes strings on output and adds 429 backoff, referencing the fixture that reproduces the broken YAML; one issue listing the three DBLP queries that returned nothing with the dates and the responses. The wrapper keeps exclude and compact whatever upstream does.

## 4. Ethics cross-reference, docs, version

- `review` step 4: if `proposal/ethics-review.md` exists, count the numbered entries under the heading "The Revision List" that are not followed by a line beginning "Applied"; item 12.3's row ends with "; ethics-review.md: N revisions open"; the hand-off seed list gains "the N open ethics revisions". Absent file: nothing printed. The checker ignores the clause.
- `the-ethics-board` `SKILL.md`: a marked local edit of two lines under What This Skill Produces asking that each revision entry, when revisited, gains an "Applied <date>: ..." or "Author: ..." line.
- README: Commands table gains the by-name call; the checker's two reference lines, `--numbers`, and the word-count rule; the wrapper, its exclude file and compact mode; the ethics count; the version 0.3.0 and tag.
- `plugin.json`: 0.3.0. Briefs frozen under 0.2.0 stay valid (the brief shape is unchanged; the older-brief rule already checks headers and amendments only).
- The eval README's spec pointer moves to this file.

## 5. Tests and evaluation

Unit tests in `tests/test_experiment_proposal_plugin.py` (the existing file): `[n]` lines counted as entries; literature-review citation count passes at 18 while the list holds 28; `--numbers` on a fixture with one planted mismatch lists both values with locations; `not confirmed` accepted on 3.1 and rejected on 7.5; the wrapper on a broken-YAML fixture yields strict-parseable output, honors an exclude file, truncates abstracts under `--compact`, and retries on a planted 429 note (subprocess stubbed).

Codex test: with the Codex CLI and the installed plugin, invoke each skill by name from a prompt; record whether `allow_implicit_invocation: false` admits it; apply the section 1 rule; record under `docs/research/2026-10-13-experiment-proposal-evals/runs/installs-codex-v3-1.md`.

Evals: scenarios 2, 3, 5 and 6 re-run once each at 0.3.0 with their 0.2.0 bars; scenario 7 (installs) re-run for the name-only check with the flag removed (no skill invoked unprompted in three runs). New scenario 8, real material from the author's project, recorded without a bar: `design` extracting from `docs/study-decisions.md` into a brief (compared with the hand-written brief); `review` in agent mode on `proposal/proposal.md` against the frozen brief (expect 65 of 65 with four `not confirmed`, the ethics count printed); `lit-search` round 2 with the exclude file holding round 1's DOIs (expect the same stop-rule verdict on a smaller candidate set).

Done when: the unit tests pass; scenarios 2, 3, 5, 6 and 7 hold their bars; scenario 8 is recorded; the README matches the shipped files; the Codex result is recorded; the tag exists.
