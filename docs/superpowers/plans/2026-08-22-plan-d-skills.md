# Plan D: The Eight Skills + Glossary Seed — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> Revision 2: 19 confirmed findings from the 2026-08-22 adversarial verification pass folded in (4 blocking — publish effects, disposition menu, writer-less mechanical acts, gate-flag schema).

**Goal:** Ship the eight remaining spec-§7 skills (guards first, then the entries), the CLI verbs that make every mechanical act deterministic, the vault glossary seed, and the deferred items ruled to land with them — completing the plugin's user surface so the validation slice can run.

**Architecture:** Deterministic-Python-core + thin-prompt-skill split (§7): every mechanical act goes through the CLI; SKILL.md files carry orchestration prose and normative rules only. **New core surface, exhaustively**: gate verbs (`arm-publish`, `disarm-publish`), disposition verbs (`mark-published`, `mark-corrected`, `mark-withdrawn`), the review-record writer (`finding`), the acknowledgment writer (`ack` — `inbox.append_ack`'s recorded consumer arrives), the search-log appender. Nothing mechanical is ever written by prose.

**Tech Stack:** Python ≥3.10 stdlib (+ admitted deps at HEAD), pytest, SKILL.md frontmatter per the ruled control model.

**Authority:** spec §7 rows verbatim; §5 (provenance — including per-claim deprecation, `[confidence::]`, `[retraction-ack::]`); §6 (gates — including publish's concrete effect and the day-one disposition menu, transcribed not paraphrased); §8 (control model); deferred-register items named per task. **As-built HEAD governs** — the Stop hook's flag contract at HEAD is normative for Task 2.

## Global Constraints

- Worktree via `superpowers:using-git-worktrees`, branch `build/plan-d`; merge + push in the same motion.
- Control model (ruled): entry skills `disable-model-invocation: true`; guards model-invoked AND user-invocable; nothing ships `user-invocable: false`.
- Skill prose uses CONTEXT.md vocabulary; new identifiers (reason codes, check ids, CLI verbs) get their terminology §4.3/§4.4 rows in the same commit. **New CLI verbs are named by the §4.3 decision tree** — the planned eight already sit on its branches; any verb this plan's execution adds beyond them walks the tree first.
- **LLM judgment never blocks; deterministic gate surfaces alone write events, statuses, tags, holds, and acks** (§5/§6) — every such write in this plan names its CLI verb.
- Four-state honesty in every skill's prose: an outage is never failure; no skill promises verification it didn't run; verified events are the CLI's to mint.
- Suite green per task (offline; live where the task says so); one conventional commit per task.

## File Structure

```
skills/{evidence-conventions,synthesis-conventions,project,find-sources,import-source,verify-citations,factcheck-draft,publish}/SKILL.md
knowledge_harness/__main__.py            (+ verbs: arm-publish, disarm-publish, mark-published, mark-corrected, mark-withdrawn, finding, ack, search-log)
knowledge_harness/publish.py             (disposition effects: status write, project-level verified event, commit + tag)
knowledge_harness/templates/vault/system/glossary.md
tests/  (skill frontmatter/content tests — created in Task 1; verb tests per task)
```

______________________________________________________________________

### Task 1: Guard skills + the skill-contract test

**`evidence-conventions/SKILL.md` normative content (contract):**

- Frontmatter: guard. Triggers: writing or editing claims, citing sources, drafting with evidence, claim-syntax questions.
- **The Iron Law, verbatim**: *no claim enters a draft without a verified source first* — a claim line exists only after its literature note exists and its citekey resolves; prose ahead of evidence goes to `inbox/`, never `projects/`.
- **§5 schema complete** (transcribed, not sampled): evidence-boundary tags `(quote|paraphrase|inference|open-question)`; `[@citekey, locator]`; `^claim-id` anchors; blockquote quotes; stance links `[supports::]`/`[disputes::]` with claim-link targets; **`[confidence::]` per-claim field**; **per-claim deprecation records** (§5: deprecate-with-reason, never delete — the record's syntax and that a deprecated claim keeps its anchor); **`[retraction-ack::]`** (the reader-side acknowledgment that a cited item carries an update notice — when it is required and what it asserts, per §5/§6); `[failed-verification::]` markers are verifier-owned — never write or remove one by hand.
- **Reason-code vocabulary placed here** (finding: users meet these codes in the review queue with no glossary): the controlled registry lives in terminology §4.4; the skill lists the codes a vault user will actually see with one-line meanings.
- **Rationalization table**: standard evasions ("I'll cite it later", "common knowledge", "the abstract said so", "I remember reading it", "paywalled") each answered by the mechanical rule that forbids it.
- Annotations-scatter: quotes travel by claim link, never re-typed.

**`synthesis-conventions/SKILL.md` (contract):** guard. The 2+-source page-creation threshold (the only threshold); ≥2 outgoing wikilinks per synthesis note; orientation-first (`synthesis/index.md` + recent `log/` before operating); synthesis asserts arrangement, not evidence — freely rewritable, every arranged claim cites its source claim link; index registration (new note ⇒ one line in `synthesis/index.md`).

**The skill-contract test is created HERE** (finding: the instrument referenced by acceptance doesn't exist at HEAD — Plan Q's validity test is a different, unexecuted plan): `tests/test_skill_contracts.py` — for every `skills/*/SKILL.md`: frontmatter parses via the core's own parser, `name` = dirname, non-empty description, invocation flags match the ruled control model per skill class (entries listed in the test, guards the rest), and every skill name any shipped template cites has a `skills/<name>/` directory (subsumes the 2026-08-22 landing check).

- [ ] Steps: both SKILL.md files → `test_skill_contracts.py` (red on missing skills it expects only after later tasks — scope the entry-skill list to grow per task, or assert over existing dirs plus the two shipped here) → suite green → commit.

______________________________________________________________________

### Task 2: The publish surface — verbs first, then the skill

**Gate-flag verbs (the hook's contract at HEAD is normative — `hooks/stop_publish_gate.py::_decode_flag`):** `arm-publish <project>` writes `.harness/publish-pending.json` with **exactly** the keys `{"project": "projects/<name>", "vault": "<absolute vault path>", "blocks": 0}`, optional `"bypass": "<single-line token>"` only on explicit human request (the hook's audited-bypass path; the token is consented, single-line, and recorded by the hook's `_append_bypass`). Any other shape is silently inert at HEAD — test this negatively (wrong keys ⇒ hook treats as unarmed). `disarm-publish` removes the flag.

**Disposition verbs (`knowledge_harness/publish.py` + CLI):** §6's concrete effect, transcribed:

- `mark-published <project>`: sets `status: "published"` in the project's frontmatter, **appends a project-level `verified` event** (§5: publish events attach to the project; deterministic gate surfaces alone write these), **commits and tags `published/<project>-<date>`** (the published-drift lint at `lints.py` keys on these tags), then disarms. Refuses unless the publish-surface decision is green or every blocking entry carries a standing ack.
- `mark-corrected <project>` / `mark-withdrawn <project>`: **post-publish only** (refuse if no `published/*` tag exists for the project): corrected = new gate run, new verified event, new tag; withdrawn = status write + log; **the original tag is never deleted** (ADR 0003).
- Commit mechanics follow the ruled transactional pattern (temp-index snapshot; live index untouched).

**`ack` verb** — the §3 acknowledgment affordance's mechanical half: takes a finding id + reason, writes the ack entry via `inbox.append_ack` (its recorded consumer — deferred-ledger seam closed). The skill composes and explains; the human consents; the CLI writes. No ack is ever hand-written or prose-written.

**`publish/SKILL.md` (contract):** entry. Orientation (drain review inbox — unacknowledged blocking-class count); run `verify --surface publish`; present the four-state report; then the **day-one disposition menu, per §6 verbatim**: *mark-published* (full gate run + the effects above) / *park* (sets `status: "parked"`, nothing else) / *keep-draft* (no-op); **deletion only on explicit request plus typed "discard"**. The **post-publish correction lifecycle** is its own section: a blocking-class alert or claim deprecation targeting an already-published project opens the correction disposition — re-publish as corrected, or mark withdrawn; original tag never deleted. Every menu choice is human-chosen; every effect is a verb call.

- [ ] Steps: verbs tests-first (incl. the negative flag-schema test and post-publish-only guards) → skill text → suite green → commit.

______________________________________________________________________

### Task 3: `verify-citations` + `factcheck-draft` + the `finding` verb

**`finding` verb** — the review-record writer: takes check id, target, result, reason (validated against the §4.4 registries), appends the entry via the inbox module. Factcheck findings and Task 5's holds both flow through it — prose never writes the review queue.

**`verify-citations/SKILL.md`:** entry. Thin wrapper over CLI `verify` (open audit by default, `--surface` on request); four-state report grouped by check id; UNREACHABLE named as outage, never failure; events are the CLI's.

**`factcheck-draft/SKILL.md`:** entry. Factored verification at draft→review, per §6's factored-verification contract **including its bounds** (finding: they were dropped): **deterministic claim selection under a budget cap** — the selection rule is stated in the skill (e.g. all claims when under the cap; oldest-unchecked-first when over), and **the skipped set is recorded** (a finding entry naming what was not checked — an unchecked claim must never read as checked; four-state honesty at the factcheck level). Each checked claim: quote fidelity / paraphrase support / inference-marked-as-inference against its cited managed region; results emitted as **adjudicated findings via the `finding` verb** — warn-tier, never blocking. Fork scientific-writing's offline audit scripts (SHA-256 claim hashing, verified-evidence-only counting) where they fit; vendored with provenance headers. New reason codes get §4.4 rows in the same commit.

- [ ] Steps: `finding` verb tests-first → skill texts → forked scripts vendored + tested → suite green → commit.

______________________________________________________________________

### Task 4: `project` skill

Entry; the real-life entry point. Contract:

- **Start**: question framing by the owned inline elicitation procedure — the framed question states: the question, scope bounds (in/out), expected source types, success criteria → `projects/<name>/question.md` (type `project`, status `draft`).

- **Resume orientation** (every invocation): `synthesis/index.md`, recent `log/`, the project's files; **drain the review inbox** (count + age, oldest first); **surface trust tiers** — the orientation displays each cited note's tier via `events.trust_tier` (the recorded consumer this function was retained for: unverified / machine-confirmed / human-reviewed).

- **Gap analysis**: framed question vs synthesis + bibliography — covered, contested (surface `disputes` links), missing → gap list feeding `find-sources`.

- **Draft frame** in `projects/<name>/` carrying the Iron Law via `evidence-conventions` (invoked, never restated).

- Routing: acquisition → `find-sources`; cataloging → `import-source`; verification → `verify-citations`/`factcheck-draft`; delivery → `publish`. Acks happen via the `ack` verb with human consent.

- [ ] Steps: skill text → content test (elicitation fields verbatim; inbox-drain and trust-tier instructions present) → suite green → commit.

______________________________________________________________________

### Task 5: `import-source` + uniform hold wiring

**Core — uniform hold-to-inbox wiring** (register): every `import-note` failure exit emits its reason-coded review record through the same writer the `finding` verb uses, in addition to stderr + exit code; the Plan R render-rejection class joins this path. **Blockquote-split evaluation** (register): render splits `annotationText` on the full `splitlines()` set so each segment gets its `> ` prefix — adopt if quote-verification fidelity is preserved (write the test both ways; escalate as an SDD ruling if ambiguous).

**`import-source/SKILL.md` (contract):** entry. In order: identifier discovery before any SKIPPED sticks; `import-note` (catalog/index/log always land); registry-first dedup against `synthesis/index.md`; **integrate-at-import** under `synthesis-conventions` — synthesis updates + stance links land immediately EXCEPT surgical auto-hold on contradiction, low/absent confidence, or schema violation, **each hold emitted via the `finding` verb** with its reason code; 2+-source page-creation threshold; re-import no-op via render-first comparison (a legitimate outcome, reported as such); **refresh mode speaks the ruled maintenance vocabulary — fresh / stale / orphaned** (finding: it was absent) — fresh = projection matches Zotero, stale = re-render differs, orphaned = note whose item left the bibliography; batch mode for backfills; archive-at-import for web sources (Save Page Now via the polite pool, or record an existing snapshot).

- [ ] Steps: hold wiring tests-first → blockquote-split evaluation → skill text → suite green **including live legs** (`HARNESS_LIVE=1`, Zotero running) → commit.

______________________________________________________________________

### Task 6: `find-sources` (vendored fork) + search provenance

- Vendor K-Dense `paper-lookup` (MIT): renamed into the plugin namespace, provenance header (upstream URL, commit, license), output shaped to §5, terminating at the admission step — the skill presents candidates for the human to admit into Zotero; it never writes the evidence layer. (Its per-API references already include Semantic Scholar alongside OpenAlex/Crossref/PubMed/arXiv — per research/adoptable-skills-audit.md; no additional source legs are owed.)

- **PRISMA-S search log** (ruled): project-scoped `projects/<name>/search-log.md`, appended per run via the CLI `search-log` verb (append-only, entry grammar documented): query as run, source searched, date, hit count; candidates NOT admitted recorded with reason codes (§4.4 rows). Invoked without an active project, the skill asks which project the search serves (acquisition serves the project flow).

- [ ] Steps: vendor + provenance header → `search-log` verb tests-first → skill text → §4.4/§4.3 rows → suite green → commit.

______________________________________________________________________

### Task 7: Glossary seed + probe decision

- **Glossary seed**: `templates/vault/system/glossary.md` (type `guide`) projecting CONTEXT.md's vault-facing entries (the meaning layer's user half; harness-internal entries stay behind); scaffold ships it; whole-file test pin (the ruled pattern).
- **Probe-verb decision comes due** (recorded): setup-vault's detect step picks its instrument at HEAD — if `doctor` gained a vault-less bridge mode, `probe` deletes; else `probe` is the instrument and setup-vault's SKILL.md says so. Decision recorded in the commit message; the loser's text removed.
- [ ] Steps: glossary template + test → probe decision → suite green → commit.

______________________________________________________________________

### Task 8: Acceptance + merge

- [ ] Full suite green offline AND live (`HARNESS_LIVE=1 HARNESS_LIVE_NET=1 HARNESS_MAILTO=<real>`; Zotero running).
- [ ] `test_skill_contracts.py` green over all **nine** skills (setup-vault + the eight shipped here — finding: the count is nine, not ten).
- [ ] §4.3/§4.4 parity: every new verb, check id, and reason code has its reference row.
- [ ] **Publish-effect walkthrough**: on a scratch vault — arm (exact flag schema), gate green, `mark-published` → status + project-level verified event + `published/<project>-<date>` tag present; published-drift lint keys on the tag; `mark-corrected` refuses on an unpublished project; original tag survives correction.
- [ ] Two-flow walkthrough (recorded in the task report): information flow and project flow traced end-to-end; every §7 scope item checked against shipped text.
- [ ] Merge per `superpowers:finishing-a-development-branch`; push in the same motion; report the SHA.

## Self-Review (at revision 2)

- All four blocking findings closed structurally: publish effects are a transcription of §6 with their own verbs and module; the disposition menu is §6's day-one menu including the typed-"discard" guard; the post-publish correction lifecycle is present with its trigger and tag-preservation rule; the flag schema is the hook's exact contract with a negative test; every mechanical act (event, status, tag, hold, finding, ack, search-log line) names its CLI writer.
- The deferred-ledger orphans are consumed: `events.trust_tier` in Task 4's orientation; `inbox.append_ack` behind the `ack` verb.
- Factcheck carries its §6 bounds (budget cap, deterministic selection, recorded skipped set); refresh mode speaks fresh/stale/orphaned; evidence-conventions now carries the complete §5 schema including deprecation, confidence, and retraction-ack, plus the reason-code vocabulary.
- The skill-contract test is created in Task 1, not borrowed from an unexecuted plan; the landing-check becomes a permanent assertion inside it.
