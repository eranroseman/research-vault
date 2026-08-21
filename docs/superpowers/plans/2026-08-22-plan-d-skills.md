# Plan D: The Eight Skills + Glossary Seed — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the eight remaining spec-§7 skills (guards first, then the project-flow and information-flow entries), the vault glossary seed, and the deferred items ruled to land with them — completing the plugin's user surface so the validation slice can run.

**Architecture:** Deterministic-Python-core + thin-prompt-skill split throughout (§7): every mechanical act goes through the CLI (one binary, one exit-code contract); SKILL.md files carry orchestration prose and normative rules only. Guards ship first so every entry skill can cite them. New core surface is small and enumerated: gate arming verbs, uniform hold emission, the search-log writer.

**Tech Stack:** Python ≥3.10 stdlib (+ the admitted deps at HEAD), pytest, SKILL.md frontmatter per the ruled control model.

**Authority:** spec §7 rows verbatim (the per-skill contracts), §5 (provenance), §6 (gates), §8 (control model); deferred-register items named per task. **As-built HEAD governs.** Control model (ruled): entry skills ship `disable-model-invocation: true`; guard skills are model-invoked AND user-invocable; nothing ships `user-invocable: false`.

## Global Constraints

- Worktree via `superpowers:using-git-worktrees`, branch `build/plan-d`; merge + push in the same motion.
- Every skill's frontmatter must pass the config-validity contract (name = dirname, non-empty description, boolean flags); descriptions follow writing-for-agents (front-loaded triggers, no identity restating).
- Skill prose uses CONTEXT.md vocabulary exactly; new identifiers (reason codes, check ids) require their terminology §4.4 row in the same commit (the parity test will enforce this once Plan Q lands; do it by hand until then).
- LLM judgment never blocks; every closed surface stays deterministic (§6 doctrine) — factored verification and integrate-at-import emit findings and holds, never gate closures.
- Suite green per task (offline; live where the task says so); one conventional commit per task.
- The four-state vocabulary and MATCHED-only minting are load-bearing in every skill's prose — no skill may describe an outage as failure or promise verification it didn't run.

## File Structure

```
skills/evidence-conventions/SKILL.md      skills/synthesis-conventions/SKILL.md
skills/project/SKILL.md                   skills/find-sources/SKILL.md   (+ vendored lookup script)
skills/import-source/SKILL.md             skills/verify-citations/SKILL.md
skills/factcheck-draft/SKILL.md           skills/publish/SKILL.md
knowledge_harness/__main__.py             (+ arm-publish/disarm-publish, hold-emission wiring, search-log verb)
knowledge_harness/templates/vault/system/glossary.md
tests/  (per-skill frontmatter/content tests; verb tests)
```

---

### Task 1: Guard skills — `evidence-conventions` and `synthesis-conventions`

Prose-only; unblocks the vault template's `evidence-conventions` pointer (Plan D landing check) and gives every later skill its citation target.

**`evidence-conventions/SKILL.md` normative content (contract):**
- Frontmatter: guard (model-invoked, user-invocable), description triggering on: writing or editing claims, citing sources, drafting with evidence, claim syntax questions.
- **The Iron Law, verbatim rule**: *no claim enters a draft without a verified source first* — a claim line exists only after its literature note exists and its citekey resolves; drafting prose ahead of evidence goes to `inbox/` as fleeting notes, never into `projects/`.
- §5 schema, stated as rules with examples: evidence-boundary tags `(quote|paraphrase|inference|open-question)`; `[@citekey, locator]` citation; `^claim-id` anchors; blockquote quotes; stance links `[supports:: …]`/`[disputes:: …]` with claim-link targets; `[failed-verification::]` markers are verifier-owned — never write or remove one by hand.
- **Rationalization table** (the §7 requirement): a two-column table of the standard evasions ("I'll add the citation later", "it's common knowledge", "the abstract said so", "I remember reading it", "the source is paywalled") each answered by the mechanical rule that forbids it.
- Annotations-scatter: quotes travel into drafts by claim link (`citekey#^claim-id`), never by re-typing text.

**`synthesis-conventions/SKILL.md` normative content (contract):**
- Frontmatter: guard. Triggers: creating or editing synthesis notes, organizing claims, page-creation decisions.
- The 2+-source page-creation threshold (the ONLY threshold); minimum-link discipline (≥2 outgoing wikilinks per synthesis note); orientation-first (read `synthesis/index.md` + recent `log/` before operating); synthesis asserts arrangement, not evidence — freely rewritable, but every claim it arranges cites its source claim link; index registration (new note ⇒ one line in `synthesis/index.md`, wikilink + one-line gist).

- [ ] Step 1: write both SKILL.md files per contract. Step 2: extend the skill-frontmatter/content tests (guard invocation flags asserted). Step 3: suite green; verify the vault template's `evidence-conventions` pointer now resolves (landing check). Step 4: commit.

---

### Task 2: Gate verbs + `publish` skill

**Core:** `arm-publish` / `disarm-publish` CLI verbs — write/remove `.harness/publish-pending.json` (`{"project": <name>, "armed_at": <iso>}` — the flag field is `"project"` per the wave). The Stop hook already reads it; these verbs are the only writers. Tests: arm→hook blocks on UNMATCHED closing checks; disarm→inert; arming a nonexistent project errors.

**`publish/SKILL.md` (contract):** entry (`disable-model-invocation: true`). The closed-gate surface: orientation (drain review inbox — unacknowledged blocking-class entries counted), run `verify --surface publish`, present the four-state report, then the **fixed disposition menu** (verbatim): *publish* (arm gate, human completes their outward act, record `published` status + log entry, disarm), *park* (status `parked`, disarm, log), *withdraw* (status `withdrawn`, log), *fix-first* (list UNMATCHED/UNREACHABLE with reasons; no disposition recorded). Acks are composed by the skill, consented by the human (§3 affordance). No disposition is ever chosen by the model.

- [ ] Steps: verbs tests-first → skill text → suite green → commit.

---

### Task 3: `verify-citations` + `factcheck-draft`

**`verify-citations/SKILL.md`:** entry. Thin wrapper: run the CLI `verify` (open audit surface by default; `--surface commit|publish` when the user names one), render the four-state report grouped by check id, route non-MATCHED to their §6 dispositions (UNMATCHED → review inbox entries the CLI already emits; UNREACHABLE → named as outage, never failure). Verified events are the CLI's to mint — the skill never writes them.

**`factcheck-draft/SKILL.md`:** entry. Factored verification at draft→review: extract the draft's claims (each with its claim link), check each against its cited literature note's managed region (quote fidelity, paraphrase support, inference marked as inference), emit **adjudicated findings** to the review inbox with reason codes — never auto-blocking (§6: LLM judgment is warn-tier). Fork scientific-writing's offline audit scripts (SHA-256 claim hashing, verified-evidence-only counting) as the starting mechanical layer where they fit; anything forked is vendored with provenance headers.
New reason codes minted here get their §4.4 rows in the same commit.

- [ ] Steps: skill texts → any forked script vendored + tested → suite green → commit.

---

### Task 4: `project` skill

Entry; **the real-life entry point** (§7). Contract:
- **Start**: question framing by the owned inline elicitation procedure — the framed question must state: the question itself, scope bounds (in/out), expected source types, success criteria. Written to `projects/<name>/question.md` (type `project`, status `draft`).
- **Resume orientation** (every invocation): read `synthesis/index.md`, recent `log/`, the project's own files; **drain the review inbox** — surface unacknowledged entries with count and age, oldest first (the Whittaker guard).
- **Gap analysis**: framed question vs the synthesis layer and bibliography — what's covered, what's contested (surface `disputes` links — disconfirmation must be seen), what's missing → a gap list that feeds `find-sources`.
- **Draft frame**: scaffold the draft in `projects/<name>/` carrying the Iron Law via `evidence-conventions` (the skill invokes the guard's rules, never restates them).
- Routing: acquisition → `find-sources`; cataloging → `import-source`; verification → `verify-citations`/`factcheck-draft`; delivery → `publish`.

- [ ] Steps: skill text → content test (elicitation fields present verbatim; inbox-drain instruction present) → suite green → commit.

---

### Task 5: `import-source` + uniform hold wiring (register item lands here)

**Core first — uniform hold-to-inbox wiring** (deferred register, ruled 2026-08-21): every `import-note` failure exit emits a reason-coded review record (spec §121 contract) in addition to stderr + exit code; the render-rejection class from Plan R Task 1 joins the same uniform path. **Evaluate the blockquote-split repair candidate now** (register): render splits `annotationText` on the full `splitlines()` set so each segment gets its `> ` prefix — if adopted, U+2028 quote text imports cleanly instead of holding; decide by writing the test both ways and keeping the behavior that preserves quote-verification fidelity (escalate as an SDD ruling if the evidence is ambiguous).

**`import-source/SKILL.md` (contract):** entry. Orchestrates, in order: identifier discovery before any SKIPPED sticks (§6); `import-note` (the CLI projects the literature note — catalog/index/log always land); **registry-first dedup** (check `synthesis/index.md` before creating pages); **integrate-at-import**: synthesis updates + stance links land immediately under `synthesis-conventions`, EXCEPT surgical auto-hold on contradiction, low/absent confidence, or schema violation — each hold emits its reason-coded review record; 2+-source page-creation threshold; re-import no-op via render-first comparison (a legitimate outcome, reported as such); refresh mode for note-level maintenance; batch mode for backfills; **archive-at-import** for web sources (trigger Save Page Now via the polite pool or record an existing snapshot).

- [ ] Steps: hold wiring tests-first (every failure exit produces an inbox record with a §4.4-rowed reason) → blockquote-split evaluation → skill text → suite green **including live legs** (`HARNESS_LIVE=1`, Zotero required) → commit.

---

### Task 6: `find-sources` (vendored fork) + search provenance

- Vendor K-Dense `paper-lookup` (MIT): renamed into the plugin namespace, provenance header (upstream URL, commit, license), output shaped to §5 fields, terminating in the admission step — the skill's last act is presenting candidates for the human to admit into Zotero; it never writes the evidence layer.
- **PRISMA-S search log** (ruled here): search provenance is project-scoped — `projects/<name>/search-log.md`, appended per run: query as run, source searched, date, hit count; candidates NOT admitted recorded with a reason code (§4.4 rows). `find-sources` runs inside a project context (acquisition serves the project flow — "no one compounds information for its own sake"); invoked without an active project it asks which project it serves.
- Core: a `search-log` append goes through the CLI (append-only file, entry grammar documented) — never free-written by the skill.

- [ ] Steps: vendor + provenance header → CLI append verb tests-first → skill text → §4.4 rows → suite green → commit.

---

### Task 7: Glossary seed + probe decision + landing checks

- **Glossary seed**: `templates/vault/system/glossary.md` (type `guide`) projecting CONTEXT.md's vault-facing entries (Vault through Update notice — the meaning layer's user half; harness-internal entries stay behind); scaffold ships it; template test pins it whole-file (the ruled pattern).
- **Probe-verb decision comes due** (recorded pending Plan D): setup-vault's provisioning detect step picks its instrument. Decide at HEAD: if `doctor` gained a vault-less bridge mode, `probe` deletes; otherwise `probe` is the detect instrument and setup-vault's SKILL.md says so. Either way the decision is recorded in the commit message and the loser's text removed.
- **Landing checks** (recorded 2026-08-22): every skill name the vault template cites now resolves; `grep` the shipped templates for skill references and assert each has a `skills/<name>/` directory — add this as a permanent test, not a one-time check.
- [ ] Steps: glossary template + test → probe decision → landing-check test → suite green → commit.

---

### Task 8: Acceptance + merge

- [ ] Full suite green offline AND live (`HARNESS_LIVE=1 HARNESS_LIVE_NET=1 HARNESS_MAILTO=<real>`; Zotero running).
- [ ] Frontmatter policy audit: every entry skill `disable-model-invocation: true`; guards model-invoked; the validity test passes over all ten skill files.
- [ ] §4.4 parity: every reason code minted by Tasks 3/5/6 has its reference row.
- [ ] Two-flow walkthrough (manual, recorded in the task report): information flow (find → admit → import → integrate) and project flow (question → gap → acquire → draft-under-Iron-Law → verify → publish) each traced end-to-end against the shipped skills — every §7 row's scope items checked off against shipped text.
- [ ] Merge per `superpowers:finishing-a-development-branch`; push in the same motion; report the SHA.

## Self-Review (at authoring)

- Guards ship first so no entry skill ever cites a dangling pointer (the exact defect class the template task just fixed).
- The three deferred-register items that named Plan D as their landing (uniform hold wiring, blockquote-split evaluation, probe decision) each have a task and step; the glossary seed and landing checks close the 2026-08-22 records.
- Nothing in any skill closes a gate on LLM judgment; publish's menu is fixed and human-chosen; factcheck findings are warn-tier — §6 doctrine survives every task.
- The slice (turning the dev corpus into a vault) is deliberately NOT in this plan — it's the validation project that runs ON these skills after they merge.
