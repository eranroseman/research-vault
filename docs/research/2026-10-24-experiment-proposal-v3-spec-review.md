# Review of the experiment-proposal v3 spec and the Bloom follow-up project

Date: 2026-10-24. Reviewed: `docs/superpowers/specs/2026-10-23-experiment-proposal-v3-design.md` at 9bc0d4f, and the author's project (bloom-follow-up-research, a local repository at its commit 9f61fe5) that the spec's "Why" section cites. Status: the spec amendments this review proposes were applied the same day in the commit that follows this file on branch `experiment-proposal-v3`; the project findings are the author's to fix.

## Method

A review workflow of 128 agents, read-only throughout. Four readers mapped the project against the course rule (running the shipped checker on `proposal.md`), the evidence behind the spec's four "Why" findings, the plugin code each spec change touches, and the comparison report the spec rests on. Eight reviewers judged one dimension each: evidence, internal consistency, feasibility against the shipped code, the lens and the design discipline, tests and evaluation, licences and attribution, agent-mode semantics and safety, and the project as the course deliverable. Duplicates were merged, then every finding faced three refuters with distinct lenses (is the claim true; does the consequence follow at that severity; is the fix sound and minimal), a finding surviving when at most one refuted it.

| Stage                    | Count |
| ------------------------ | ----- |
| Raw findings             | 59    |
| After merging duplicates | 38    |
| Survived verification    | 32    |
| Refuted                  | 6     |

Line numbers below refer to the spec at 9bc0d4f and to the project's files at 9f61fe5. "F" numbers are the merged findings' ids.

### 1. Verdict

**Spec: ready with amendments.** After overrides nothing is critical, and every finding has a local fix. F1, F3 and F17 must land before planning: a self-contradiction, an agent-run signal no skill can detect, and a Done-when that cannot be met.

**Project:** the proposal meets the assignment's structure and counts. Still open: two stale "36"s in the consent material, an unrecorded licence scope, 28 listed references (an interpretive risk), and a `review.md` that overstates its checks and confirmations.

### 2. Spec findings

Overrides: F1 critical→important; F10, F12, F20, F22 important→minor.

**Important**

- **F1 Carry-forward keeps confirmations no user made** (spec line 23, :49, :87, :101). Claim: :49 marks attested items `not confirmed` in agent runs, while :23/:87 keep earlier confirmations, and the checker trusts those by string alone. Consequence: scenario 8 cannot meet both rules, and agent runs re-certify rows an unattended agent wrote (a98211d9…jsonl:3066). Amend: :87 "confirmed attestations (...) and the item 3.1 values are kept" → "the item 3.1 values are kept; earlier attestations survive only as text in `not confirmed` rows, re-asked interactively"; drop them from :23; :101 "keeps the attestations and waivers" → "re-asks the carried attestations".
- **F3 Agent-run signal is undetectable** (spec line 46). Claim: "an agent calling by name" also covers the model's own Skill call, and no SKILL.md reads `$ARGUMENTS`. Consequence: a person gets an all-provisional brief without being asked, or an unattended run stalls. Amend: "one the caller declares (...)" → "one whose arguments contain the word `agent`; where a host passes none (Codex), the phrase "no human will answer""; design and review only.
- **F17 "Unit tests pass" is unreachable** (spec line 68, :97, :103). Claim: v2 word budgets still stand (lit-search 638/650), and tests the spec does not list go red (nine scripts, "writes nothing", brief.md's version, `valid_draft()`). Consequence: Done-when needs edits that only a spec edit may make. Amend: §5 names raised budgets, a `litsearch.py` allow-list and the checker-suite cases; :68 "unchanged" → "only its example `Checklist:` line changes".
- **F16 + F15 Ethics count contradicts Out of scope, and nothing writes the file** (spec line 35, :44, :88-89). Claim: :88 counts the Revision List that :35 rejects parsing, and no skill text writes the promised `ethics-review.md`. Consequence: item 12.3 carries a number nothing verifies, and the file exists only if the caller asks for it. Amend: delete :88 and its echoes (:91, :101); cut the Ethics board row to its first sentence; :89's body edit becomes "write this document to proposal/ethics-review.md; if an input is missing in an agent run, use what is given".
- **F19 + F2 Scenario 7 counts the wrong events, and only once** (spec line 33, :35, :101). Claim: "no Skill call" fails on other plugins' skills, Agent calls have no bar, the slash-command positive already passes at 0.2.0, and a leak seen in 1 of 3 runs gets one run. Consequence: false fails and missed leaks. Amend: move "scratch config isolation" from :35 into §5. Add a predicate script: a positive is a Skill tool_use `experiment-proposal:<skill>` with `is_error: false`, from a prompt that names the skill in words; a negative is "none of ours" (Skill or Agent), 7 utterances × 3 runs. Descriptions end "Not for unprompted use."
- **F7 `--numbers` misses the real defect** (spec line 63). Claim: no keyword sits near either stale 36. Consequence: scenario 8 passes the cross-section row again. Amend: "within six words of a keyword ... grouped by keyword" → "every non-year integer of two or more digits occurring twice or more, plus `$`/`%`, grouped by value, with heading, line and window text"; the fixture plants Bloom's 36/52 pair.
- **F6 Author-year fallback never runs** (spec line 62). Claim: `Surname [year]` counts as a bracketed number, and `Fitts (1954)` matches no key. Consequence: the scenario 5 fixture counts 0 citations. Amend: "when no bracketed numbers occur there ... second name in `--sections`" → "otherwise an entry is cited when its first surname and year occur in the section headed Literature Review". This replaces F21's D8 re-key.
- **F13 `resolved` duplicates `pass (fix N applied)`** (spec line 87, :97). Claim: `resolved` has no Summary bucket and no quote rule. Consequence: the checker accepts a pass with no quote. Amend: "marked `resolved (fix N applied)`" → "reads `pass (fix N applied)` with its new quote"; delete the acceptance sentence and its test; add "each pass numbers fixes from 1 and carries no earlier `(fix N applied)` markers"; :68 adds "`not confirmed` counts under Fail".
- **F4 Waiting steps incomplete** (spec line 46-50, :81). Claim: lit-search steps 1 and 3, design step 8 and review step 7 also wait. Consequence: runs stall, and scenario 8's design step amends the frozen brief instead of extracting. Amend: :46 lists these steps; :48 adds "on a frozen brief an agent run stops"; :81 "asks for the short query" → "picks two or three terms from the need"; :101 → "ends with the hand-off and contains the closing line".
- **F18 Scenario 8 expectations unreachable** (spec line 101). Claim: design amends the frozen brief, and the review has 67 rows, not 65. Consequence: the record fails on bookkeeping. Amend: copy A, without the brief, is for design; copy B drops `review.md` and re-runs on its own output; compare item by item against the amended brief; "expect 67 rows, 65 checked".
- **F5 Agent-made provisional entries are never asked** (spec line 48, :68). Claim: resume keeps every status, and the frontier holds only weak or missing items. Consequence: the user freezes decisions nobody asked them about. Amend: :48 adds "Source `agent run, <date>`; weak on resume", with the same clause in references/brief.md:34.
- **F11 Lenient parse is dead code** (spec line 29, :76-78, :97). Claim: the in-process functions return dicts, so there is no YAML to parse. Consequence: the test has nothing to run against. Amend: strike the parse and :76's subprocess fallback; :97 → "federate stubbed with a newline title; output strict-parses".
- **F21 A failure cannot reach a pass** (spec line 33, :101, :103). Claim: evals README.md:3 requires all three runs to pass. Consequence: the tester has to invent a verdict rule. Amend: "two more runs before a verdict" → "three fresh runs on the all-three rule", also at :33 and :103.
- **F23 Carried 3.1 values are free prose** (spec line 49, :92). Claim: Bloom's recorded "15-27 ... exited 0" now exits 1. Consequence: a widened workaround bound carries forward. Amend: an optional, checked `Checker:` header line is the only source; :92 adds "0.2.0 reviews carry the course defaults".
- **F24 A placeholder satisfies "no quote, no pass"** (spec line 65). Claim: item 8.9 passes on `[NO-SHOW EXTRAS]`. Consequence: 13.5 passes and the hand-off leaves the item out. Amend: `review` flags `pass-placeholder` when a pass row's quote holds a bracketed all-caps placeholder; re-quote, otherwise `fail` with `decide:`.

**Minor**

- **F10 Biggest build, least-used skill** (spec line 10, :83): lit-search added 0 of 28 references (18 were already cited). Record that, make the upstream PR an issue for after 0.3.0, and add or reject the 13.8 anchors.
- **F12 Retry has no data** (spec line 77): the 429s lasted about 17 minutes. Drop the retry and print "semantic_scholar: skipped (HTTP 429)".
- **F20 Agent bars check shape only** (spec line 101): a hollow review passes. Score against the scenario keys.
- **F22 Upstream gone** (plugin: the-ethics-board/SKILL.md:13, plugins/experiment-proposal/README.md:51): the pointers return 404. Cite `swh:1:rev:f93fee7459e2bf452ec9bc43163004812efba51f` and keep `HEADER_CLOSE`.
- **F26 DBLP figures undated** (spec line 10): add "(DBLP publ API @total, 2026-10-23)".
- **F27 Item 5.1 still measures the list** (checklist.md:54, spec line 11): reword it to count Literature Review citations; Why #3 names the orchestrator.
- **F28 Done-when incomplete** (spec line 103): add the upstream issue, the eval README pointer and the installed-copy updates.
- **F29 Ethics edit count unsettled** (spec line 44, :89): say whether the ethics board gets an Agent run paragraph.
- **F30 Hand-off read has no agent branch** (spec line 46): if `installed_plugins.json` cannot be read, write "research-grill install not checked".
- **F31 Codex rule** (spec line 55): "0.2.0" → "0.1.0"; fail only when a `SKILL.md` search comes before the load; retry twice.
- **F35 Attribution on shared sentences** (THIRD-PARTY-NOTICES.md:14, ATTRIBUTION.md:112): split them so the CC BY-NC research-grill stays "not copied".
- **F36 False statements** (spec line 92, :97, :101): 0.2.0 briefs get the full check; checker tests go in the checker file; the review has 67 rows.
- **F37 Baseline brief is agent-written** (spec line 101): "hand-written brief" → "the agent-extracted brief".
- **F38 Supervision match not tied to the consent form** (plugin: check_proposal.py:743): search consent-headed blocks first.

### 3. Project findings

- **F7 Consent material says 36** (proposal/appendix.md:74, :428). Claim: commit 440c9e5 moved N to 52 everywhere else. Consequence: the graded consent form and the PDF contradict the body. Edit: change both to 52, rebuild the PDF and re-check review.md:73.
- **F25 Approval scope unrecorded** (docs/study-decisions.md:23, AGENTS.md:28). Claim: no file names the signatory, date or scope of the prompt approval. Consequence: the F.2 adaptations may fall outside the licence. Edit: record all three from the letter. Do not restore the placeholder, because it fails proposal/notes/check.py:75-76.
- **F24 Placeholder passes** (proposal/review.md:48, :58): 8.9 becomes `fail` with `decide:`; 12.1 becomes `decide:` naming where the signed checklist is.
- **F1 Unattested confirmations** (proposal/review.md:16, :67): 3.1 and 13.4 lack the author's word. Mark them `fail` with a fix, since 0.2.0 rejects `not confirmed`. :25 and :64 had real answers from the author.
- **F23 Stale checker record** (proposal/review.md:3, :16, :24, :68): refresh to 28 entries, 3,997 words and today's exit status.

### 4. What the project teaches the spec

- Absorb: told to, an agent writes "confirmed by the user" with no user present (a98211d9…jsonl:3066). Make that string unwritable in agent runs.
- Absorb: `proposal/notes/check.py:60-77` is prior art for §2. Its hook kept proposal.md fresh while review.md went stale, so re-run checks rather than record their results.
- Absorb: the real material holds defects the fixtures lack (the stale 36, placeholder quotes). Plant them in the fixtures.
- Reject explicitly: style checks, the assemble pipeline, red-team triage and a word budget for fixes.

### 5. Refuted

- F8 (13.5 fails every agent run): the fail is the honest result, and `decide:` already gives a fix.
- F9 (federate loses per-source counts): `dedupe` merges source tags, so the counts survive.
- F14 (ethics count reads 15 or 1): a model reading the prose counts 1.
- F32 (stale Codex `default_prompt`): it only reaches interactive picks.
- F33 (no word budget for fixes): the rows quote the text that was actually applied.
- F34 (PR omits upstream sync): upstream's test suite already runs the drift check.

### 6. Sound

- The Literature Review citation count follows the course text (Bloom: 18 cited, 28 listed).
- Re-vendoring at v0.9.0 is the right step: identical signatures, byte-identical licence.
- Every Decisions row maps to a section that implements it.
- The attribution correction matches guidelines.md:119-122 word for word.
- The project meets the assignment's form, including the supervision sentence (proposal.md:260).
