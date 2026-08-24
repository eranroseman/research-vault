# Task 8 report — ecosystem-steal prose adoptions (audit items 13–14)

**Branch:** `fix/pre-slice-batch` · **Base:** `a2a5aad` · **Commit:** `e76805c`
(one commit; `skills/` + `tests/` only — `.superpowers/` is git-excluded, so this report is
untracked, matching tasks 1–7)
**Record document:** `research/validation-slice/2026-08-22-skills-layer-audit.md`
(read on-branch at `docs/2026-08-22-skills-layer-audit.md`; line numbers below are that file's).

Eight adoptions across six skill files. Seven come from §6's adopted paragraph at `:381`;
the eighth (gate-armed) from §7's batch-enrichment sentence at `:405` — provenance ruled below.

______________________________________________________________________

## Step 1 — the adopted set, source beside shipped

### 1. Routing guard → `project-flow`

**Audit `:381`:** "the routing guard (\"route the user's intent without silently broadening it\")
into project-flow's routing table"

**Shipped** — `skills/project-flow/SKILL.md`, immediately after the routing table, inside the
`## Routing`–`## Acknowledgments` slice:

> Route the user's intent without silently broadening it. Hand the routed skill the need the
> person actually stated — not an enlarged version of it, and not the adjacent work you can see
> it will need. "Import this paper" is not "import it and rebuild the synthesis page"; "find
> sources" is not "find and admit them." When the stated need turns out to sit inside a larger
> job, say so and let the person widen it; never widen it for them and report back on work they
> never asked for.

The decided fragment survives verbatim as the opening sentence. The examples that follow are
this repo's own verbs, so the guard lands in the corpus's vocabulary rather than the survey's.

### 2. Compilation-value line → `synthesis-conventions`

**Audit `:381`:** "a compilation-value line in synthesis-conventions (the 2+-source threshold
*permits* a page, it never obligates one — create only when arrangement adds synthesis)"

**Shipped** — `skills/synthesis-conventions/SKILL.md`, a new second paragraph under
`## The 2+-source threshold`:

> The threshold *permits* a page; it never obligates one. Two sources on a topic make a page
> allowed, not owed — create one only when the arrangement adds synthesis. Sources set side by
> side with nothing said about how they relate are a compilation, and a compilation earns no
> page: leave the claims in their literature notes and say plainly that there was nothing to
> arrange yet.

The existing sentence ending "— the only threshold" was **not** reworded. Permits-vs-obligates is
not a second threshold, and rewording that clause would have read as one.

### 3. Partial-read honesty rule → `import-source` **and** `factcheck-draft`

**Audit `:381`:** "the partial-read honesty rule (a partially-read source is labeled partial with
the missing range — SKIPPED applied to reading) in import-source/factcheck-draft"

**Shipped (a)** — `skills/import-source/SKILL.md`, in `## Four-state honesty`, before the closing
"Never describe an outage as a failure" paragraph:

> The same honesty covers your own reading. A source you read only in part is reported
> **partial**, with the range you did not read named — the free region you skipped, the pages an
> attachment would not open past, the sections you never reached. That is SKIPPED applied to
> reading: an unread stretch must never read as read, exactly as an unrun check must never read
> as run. It is a rule about what you say, not about what you file — no verb watches your
> reading, which is precisely why the label has to come from you.

**Shipped (b)** — `skills/factcheck-draft/SKILL.md`, closing `## Check every selected claim`:

> Read fully, or say you did not. When the cited managed region was truncated, or the source
> would not open past a point, report that claim's source as **partial** and name the range you
> did not read — SKIPPED applied to reading. Adjudicate from what you actually read and say what
> that was; never let an unread stretch read as read. This governs what you report, not which
> verb you file: the four states below still turn on whether the adjudication ran, not on how
> much of the source you reached.

Both carry "SKIPPED applied to reading" verbatim. **Deliberate restraint:** an earlier draft
routed a partial read to a specific finding verb/result. That was cut. The adoption is a
reporting-honesty rule, and inventing filing mechanics for it would have drifted into the
**machine intake gate** — a §6 deferred item (`:387`). Both paragraphs now say in terms that they
govern what you report, not what you file.

### 4. "It validates declarations, not their truth" → `factcheck-draft`

**Audit `:381`:** "peer-review's sentence — \"it validates declarations, not their truth\" — into
factcheck-draft, which is our four-state posture said better than we say it"

**Shipped** — `skills/factcheck-draft/SKILL.md`, closing `## Four-state honesty, at the factcheck
level too`:

> MATCHED is narrower than it sounds, and saying so is the honest half of reporting one: this
> pass validates declarations, not their truth. It asks whether a claim says what its cited
> source supports — never whether that source is right. A faithful claim resting on a wrong paper
> passes here, exactly as it should; judging the source belongs to the person, to its trust tier,
> and to whatever update notice arrives later.

Placed against the MATCHED row, because MATCHED is where the over-read happens. The sentence is
verbatim.

### 5. Why one honest pass, not an LLM panel → `factcheck-draft`

**Audit `:381`:** "one sentence on why a single honest pass rather than an LLM panel (role
separation is not independent error processes)"

**Audit `:395`** (Rejected, and load-bearing on the phrasing): "deterministic-only closure is an
ADR-adjacent ruling, and the batch's why-one-pass sentence **now says so in the skill instead of
implying it**."

**Shipped** — `skills/factcheck-draft/SKILL.md`, extending the budget paragraph under
`## Select claims mechanically`:

> One pass, never a panel: re-running the same model in different roles separates the roles, not
> the errors — role separation is not independent error processes — so a second agreeing voice
> buys agreement rather than confidence, and closure stays deterministic-only, in
> `verify-citations`'s suite rather than in any count of LLM votes.

One sentence, carrying **both** halves: the anti-panel rationale from `:381` and the
deterministic-only closure ruling `:395` says this sentence must state. A version carrying only
the panel half would have left `:395`'s claim about the skill untrue.

### 6. Disposition rationalization table → `publish`

**Audit `:381`:** "a disposition rationalization table in publish (doubly evidenced at 276k/231k:
irreversible steps attract excuses, name them)"

**Audit `:401`** (§7 survey, the seed rows — the only thing taken from §7's survey): "behind on
the rationalization table (already batched; the survey's ported rows — \"they said go ahead so
the ack is covered\", \"UNREACHABLE is basically fine\" — seed it)"

**Shipped** — `skills/publish/SKILL.md`, new closing section `## Rationalizations, answered`,
seven rows. Both seed rows ship as left-column cells with their wording intact:
`"They said go ahead so the ack is covered."` and `"UNREACHABLE is basically fine."` The lead-in
uses the audit's own rationale: "irreversible steps attract excuses".

The other five rows are drawn from `publish`'s own irreversible acts: picking the disposition,
inferring `discard`, reading a refusal as a disarm, re-publishing instead of correcting, and
volunteering the bypass. Every right-hand cell restates a rule **already** in the file — see the
self-review note below on why that is the form, not a defect.

**Shape:** header `| What you're tempted to think | The mechanical rule that forbids it |` — the
exact header `evidence-conventions` already ships for its rationalization table, so this is the
house form rather than `finishing-a-development-branch`'s `| Excuse | Reality |`. Cell padding is
mdformat's, matching `publish`'s three existing tables.

### 7. Fail closed on ambiguous vault selection → `setup-vault`

**Audit `:381`:** "setup-vault fails closed on ambiguous vault selection."

**Shipped** — `skills/setup-vault/SKILL.md`, second paragraph of `## Scaffold`:

> Fail closed on an ambiguous vault. If the destination is not unambiguous — two candidate vaults
> in play, "my vault" with no path attached, a `PATH` that could name either an existing vault or
> a new one — stop and ask which. Never resolve it yourself: not from the working directory, not
> from the most recently mentioned path, not from the only vault you happen to have seen.
> Scaffolding into the wrong tree writes files nobody asked for, and repairing a vault the person
> did not mean is worse; one question costs less than either.

### 8. `publish` announces the armed gate at start — **provenance ruling**

The brief lists this; the parent's map of `:381` correctly finds it absent there and asked whether
it is plan-sourced. **It is not plan-sourced. It is in the audit**, at `:405`, in §7's
*Adjudication* → **Batch enrichments (existing items, no new scope)**:

> **Batch enrichments (existing items, no new scope):** C-1's replacement sentence uses the
> obsidian-cli canonical form; the publish rationalization table starts from the ported
> finishing-a-branch rows; **publish announces at start that the gate is armed (one line — the
> most irreversible skill should say so)**.

**This does not breach the §7 boundary the parent drew.** That boundary is the deferred polish
pass — §7's numbered items 01–11, gated *after* the post-Q batch. `:405`'s sentence sits above
that list and labels itself "existing items, no new scope"; the same sentence is where item 6's
seed rows are authorized, and the parent already ruled those in scope. Nothing from items 01–11
landed (verified in Step 2 below).

**Shipped** — `skills/publish/SKILL.md`, intro, second paragraph:

> Say this before the first command: publishing here runs through an armed gate — `arm-publish`
> sets a state flag the Stop hook reads, and from the moment it is set the hook holds the session
> until the attempt lands, is acknowledged, or is disarmed. This is the most irreversible thing
> the vault does, so the person hears it at the start rather than meeting it at the first
> refusal.

**Phrasing hazard handled.** The gate is *not* armed when the skill starts — `arm-publish` arms it
later. A literal "announce that the gate is armed" line would have been a false mechanical claim,
the fabrication class this plan has caught three times. The line therefore announces the
*property of the flow* ("runs through an armed gate") and names the verb that does the arming. The
pin asserts this shape, and its docstring records why.

______________________________________________________________________

## Step 2 — item 14: no §6 deferred item landed here

Not a no-op; run and recorded. Method: the diff is **purely additive** in `skills/` — the only
deleted line is the `factcheck-draft` budget sentence, re-added with the why-one-pass clause
appended (`git diff -U0 -- skills/ | grep '^-'` returns that one line and nothing else). No
frontmatter line in any of the six files is touched. Each `:385`–`:390` bullet checked against the
added lines:

| §6 deferred item (audit line)                     | Landed? | Evidence                                                                                                                                                                                                                                    |
| ------------------------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Plan-hash approval handshake** (`:385`)         | No      | No `sha256`, no preview→echo→apply handshake anywhere in the diff. `setup-vault`'s new line is consent-adjacent but adds no hash-scoped ack; consent stays conversational, exactly as the trigger says it does until the first ambiguity incident. |
| **Independence key on claims** (`:386`)           | No      | No claim-schema field, no `[independence:: …]`. The `synthesis-conventions` adoption deliberately leaves "— the only threshold" unreworded, so what *satisfies* the threshold is untouched; permits-vs-obligates is a value question, not an independence one. |
| **Machine intake gate — factcheck-draft** (`:387`) | No      | No intake validation, no malformed-intake handling, no new gate. The partial-read paragraph explicitly disclaims filing mechanics ("governs what you report, not which verb you file") — written that way to stay clear of this item. |
| **Frontmatter metadata** (`:388`)                 | No      | No `related_skills`, no `envVars`. Frontmatter is byte-identical in all six files (grep over the diff for `name:`/`description:`/`disable-model` returns nothing).                                                                            |
| **Freshness fields** (`:389`)                     | No      | No `accessed` field, no update-notice schema change. The single mention — "whatever update notice arrives later" in adoption 4 — is prose referring to the existing mechanism, not a new field.                                              |
| **Repair-as-separate-operation gate** (`:390`)    | No      | Nothing about doctor auto-repair. `setup-vault`'s `## Diagnose` and `## Provision companions` sections are untouched; doctor still guides.                                                                                                   |

**Also confirmed clear of §7's deferred polish list (items 01–11).** Six of its eleven items name
five of the six files edited here, so each was checked:

- **01** (`setup-vault`: wizard-form bash script, consent asks leading with the recommended
  answer, one sentence on why consent precedes exploration) — none landed. My `setup-vault` line
  is `:381`'s fail-closed rule; no bash script, no reordered consent asks.
- **02** (`project-flow`: free-form invocation section with worked examples, routing rows
  distinguishing "type this" from "invoked") — none landed. No new section, and the routing
  table's columns and rows are unchanged; the guard is a sentence *after* the table.
- **04** (`import-source`: explicit Deliverable block — "nine sections never say what the person
  gets") — not landed. No Deliverable block; the edit is one paragraph inside the existing
  four-state section.
- **06** (`synthesis-conventions`: worked example, Rejected-framings section, expanding "asserts
  arrangement, not evidence") — none landed. No example, no new section, and that sentence is
  untouched.
- **08** (`factcheck-draft`: per-claim report template, weighted rubric, the receiving-code-review
  half) — none landed. No template, no rubric, no pushback-handling prose.
- **10** (`import-source`: explicit ingest step between §2 and §3, authoring a full-text digest as
  tagged claims) — not landed, and this is the closest call in the set. No ingest step, no §
  renumbering, nothing authored into the free region. The adjacency is real — item 10's full-text
  precondition and my partial-read rule are both about reading a source honestly — but they act on
  different things: item 10 governs **authoring a digest** from full text, mine governs **labeling
  what you read** when reporting. No digest, no compilation-value gate, no `/fulltext` route
  appears in the diff.

______________________________________________________________________

## Pins touched

All five are **new** asserts in pin files that already existed; no existing assert needed changing,
because every prose edit is additive and none altered a pinned phrase (checked by grepping
`tests/` for a distinctive phrase from each section before editing — only `"Ask together:"` in
`test_skill_files.py` sat in an edited section, and that sentence is unchanged).

| File                               | Test added                                                            | Pins                                                     |
| ---------------------------------- | --------------------------------------------------------------------- | -------------------------------------------------------- |
| `tests/test_project_flow_skill.py` | `test_project_routing_forbids_silently_broadening_the_routed_intent`  | Guard present **inside the `## Routing` slice**            |
| `tests/test_import_source_skill.py`| `test_import_source_labels_a_partially_read_source_as_partial`        | "SKIPPED applied to reading" + the missing-range clause  |
| `tests/test_skill_files.py`        | `test_setup_vault_fails_closed_on_an_ambiguous_vault_selection`       | Fail-closed line inside the `## Scaffold` slice           |
| `tests/test_publish.py`            | `test_publish_skill_announces_the_armed_gate_before_the_first_command` | Announcement in the intro, before `## Orient`             |
| `tests/test_publish.py`            | `test_publish_skill_answers_the_disposition_rationalizations`         | Section heading + both ported seed rows verbatim          |

> **CORRECTED in fix round 1 — the paragraph that stood here was false.** It claimed
> `factcheck-draft` had no per-skill prose pin file. It has one: `tests/test_finding_cli.py:409`,
> `test_factcheck_draft_skill_names_its_bounds_and_never_blocks`, has read
> `FACTCHECK_DRAFT_SKILL` since before this task. See the fix-round section at the end of this
> report for the correction and its consequence.

**One adoption ships unpinned:** `synthesis-conventions` (adoption 2). No test in the repo reads
`skills/synthesis-conventions/SKILL.md` — grep-verified across `tests/`, not assumed. Creating a
pin file for prose that has never been pinned is the polish pass's call, not this task's; the file
remains covered by `test_skill_contracts.py`'s generic per-skill contract. Recorded as a deferred
Minor.

## What was tested

- **Baseline at base `a2a5aad`:** `1565 passed, 7 skipped` — matches the brief's stated baseline.
- **After:** `.venv/bin/python -m pytest tests -q` → **`1570 passed, 7 skipped`** in 91s. The
  delta is exactly +5, the five new pins; nothing else moved.
- **Form gate:** `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files` → **8/8**.
  mdformat reflowed the new `publish` table on the first run (expected — mdformat owns `skills/`);
  re-run is clean. Table content verified after the reflow: no escaping, seed rows intact.
- **Check-id enumeration sweep** (`test_recognizable_check_id_enumerations_name_only_ids_the_code_files`):
  green. New prose was written to avoid backticked runs of two-or-more known check ids, which
  would have been read as an enumeration.

## Self-review

**Does any adoption restate something the file already says?**

- The rationalization table restates by design — that is the genre, and `evidence-conventions`'s
  table does the same thing: the left column is the adversarial framing, the right column is a
  rule already binding elsewhere in the file. Naming the excuse is the new content. One row was
  reworded during drafting for this reason: the bypass row originally repeated the adjacent
  paragraph's "recorded, not forgiven" word-for-word, immediately below it; it now argues the
  consequence instead.
- `setup-vault`'s intro already says "Keep the person in control of destination". The new line is
  the narrower, actionable rule that sentence does not supply: what to do when the destination is
  *ambiguous*. Adjacent, not duplicative.
- The other six adoptions state things none of the six files said at all.

**Does the rationalization table's shape match `publish`'s existing tables?** Yes — same pipe-table
form, same mdformat-padded cells, prose-sentence right column. The header matches
`evidence-conventions`'s rationalization table exactly, which is the in-corpus precedent for this
specific table genre.

## Concerns

1. ~~The two unpinned skills.~~ **Resolved in fix round 1** — the premise was false for
   `factcheck-draft`; its three adoptions are now pinned. Only `synthesis-conventions` remains,
   as a deferred Minor the coordinator ruled should stay unpinned.
2. ~~Adoption 8's phrasing is an interpretation.~~ **Resolved** — the reviewer verified the
   factual premise against the tree (`skills/publish/SKILL.md:61` confirms the gate is inert at
   skill start), so the flow-property phrasing is correct and nothing goes to the author. The
   ruling now has a negative assert enforcing it, not just a docstring describing it.
3. **`publish` is now the longest skill in the corpus** (140 lines, up from 124). The table is seven rows where
   `evidence-conventions` has five; if the polish pass wants it shorter, rows 3–7 are the
   locally-derived ones and rows 1–2 are the audit-mandated seeds.

______________________________________________________________________

# Fix round 1

Commit amended `c0d0854` → **`e76805c`** (still one commit; +18 lines of tests over the original).

## Finding 1 — five test docstrings carried provenance and a correctness argument

**Confirmed and fixed.** All five opened with audit provenance ("Adopted per audit §7's batch
enrichments…", "The routing guard adopted from the ecosystem survey…"), and the adoption-8 one
argued its own correctness. The binding doctrine is that a docstring earns its place by stating
the constraint it enforces; provenance belongs in git log, where the adoption-to-source map for
all eight already sits.

All five rewritten to state what breaks if the pin fails:

| Site                                 | Now states                                                                                                                                                                            |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tests/test_publish.py` (gate-armed) | Drop the warning → a person meets the hook at their first refusal; claim an armed gate → the skill describes state the vault does not have.                                            |
| `tests/test_publish.py` (table)      | A table missing either seeded row stops answering the rationalization it exists to catch; a row whose *answer* drifts is worse than an absent row, because it still reads as a ruling. |
| `tests/test_project_flow_skill.py`   | The section slice is the point: the same sentence elsewhere in the file is not read at the moment it would have to bind.                                                               |
| `tests/test_import_source_skill.py`  | Nothing observes how much of a source was read, so this prose is the only thing standing there; naming the *range* is the load-bearing half.                                           |
| `tests/test_skill_files.py`          | After the command runs, the wrong tree already has files in it — hence scaffold-section placement.                                                                                     |

## Coupled Minor — the gate-armed pin now enforces the ruling instead of describing it

Taken in the same pass, as suggested. Added `assert "the gate is armed" not in intro`, with a
constraint comment ("The false-state half of the rule, which no presence check can enforce").

**Verified it discriminates independently.** A first attempt was inconclusive — replacing the
prose with the audit's literal wording failed on a *positive* assert firing first, so the negative
check went unexercised. Re-ran with every positive phrase left intact and the false-state claim
added *alongside* it ("From the moment this skill starts the gate is armed…"). Result:

```
>       assert "the gate is armed" not in intro
E       AssertionError
```

Only the negative assert can see that drift, and it does.

## Finding 2 — three adoptions unpinned on a false justification

**Confirmed. My claim was false and the tree falsifies it.** `tests/test_finding_cli.py:17` defines
`FACTCHECK_DRAFT_SKILL`, and `:409`'s `test_factcheck_draft_skill_names_its_bounds_and_never_blocks`
has asserted a token tuple against it since before this task. I verified this myself before fixing.

The consequence the reviewer identified is real: every token already in that tuple
(`"MATCHED"`, `"SKIPPED"`, `"--cap"`, …) recurs elsewhere in the file, so it pins *vocabulary*, not
any one paragraph — all three adopted paragraphs could have been deleted with the suite green.

**Fixed with three appended tokens**, each verified to occur exactly once in the file, at exactly
the three adoption lines:

| Token                                                | Occurrences | Line  |
| ---------------------------------------------------- | ----------- | ----- |
| `role separation is not independent error processes` | 1           | `:19` |
| `SKIPPED applied to reading`                         | 1           | `:42` |
| `validates declarations, not their truth`            | 1           | `:79` |

A constraint comment above them records why these three differ from the tokens above them.
Both the report text and the commit body are corrected.

## Discrimination evidence — all nine adoption sites, not one

The requirement was to delete one adopted paragraph and show the pin fails. I ran it across every
site instead, since that is the question the finding actually raises. Each adoption was deleted in
a scratch copy, the five pin files plus `test_skill_contracts.py` were run, then the file restored:

```
CAUGHT  1 routing guard (project-flow)
MISSED! 2 compilation-value (synthesis-conv)
CAUGHT  3a partial-read (import-source)
CAUGHT  3b partial-read (factcheck-draft)
CAUGHT  4 validates-declarations (factcheck)
CAUGHT  5 why-one-pass (factcheck)
CAUGHT  6 rationalization table (publish)
CAUGHT  7 fail-closed (setup-vault)
CAUGHT  8 gate-armed (publish)
```

Eight of nine. The single MISS is `synthesis-conventions`, which the coordinator ruled stays
unpinned. The `skills/` diff was empty afterwards, confirming every scratch mutation was restored.

## Test evidence

- `pytest tests/test_finding_cli.py tests/test_publish.py tests/test_project_flow_skill.py tests/test_import_source_skill.py tests/test_skill_files.py -q` → **97 passed**
- Discrimination sweep → **8/9 CAUGHT** (above); negative assert exercised independently
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files` → **8/8**
- Full offline suite → **1570 passed, 7 skipped**. Unchanged, correctly: the three new tokens went
  into an existing test function and the docstring rewrites add no test.

## On the pattern

Taken. The failure was a scope error in the question I asked: I checked for a *dedicated per-skill
pin file*, found none, and wrote "no pin file exists" — when the question that mattered was whether
*any* test reads the file. `test_finding_cli.py` pins three skills' prose, which a filename-shaped
search will never surface. For this fix I inverted it: grepped `tests/` for `synthesis-conventions`
before writing that it is unpinned, and ran the discrimination sweep above so the claim rests on an
observed failure rather than on my reading of the test files.
