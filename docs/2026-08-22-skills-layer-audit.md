# Skills-layer audit — `skills/` (nine SKILL.md files)

Date: 2026-08-22. Commit audited: `308dd01`, clean tree.

Five frameworks applied to one corpus: `rethink-audit` (clean-slate design),
`writing-for-agents` + `superpowers:writing-skills` (agent-document
conformance), `ponytail-audit` (over-engineering), `consistency-audit`
(contradictions, drift, stale claims). Report only — nothing applied.

## Scope line

- **Read in full**: all nine `skills/*/SKILL.md` (9,788 words); `skills/find-sources/references/` (11 files) and `scripts/` (5 files) read by header, entry point, and the specific claims the SKILL.md makes about them, not line-by-line.
- **Evidence corpus for refutation**: `knowledge_harness/` (`__main__.py`, `verify.py`, `checks.py`, `inbox.py`, `scaffold.py`, `events.py`, `identify.py`, `factcheck.py`), `tests/test_skill_contracts.py`, `tests/test_skill_files.py`, `tests/test_project_skill.py`, `tests/test_find_sources_vendor.py`, `docs/superpowers/specs/2026-08-16-foundation-spec.md` §7–§8, `docs/superpowers/plans/2026-08-22-plan-d-skills.md`, `docs/terminology.md` §4.3–§4.4, `CONTEXT.md`, `AGENTS.md`, the shipped vault templates.
- **Adaptations disclosed**: `consistency-audit` prescribes two independent `consistency-audit-inspector` readers per slice plus a skeptic that did not raise each candidate. This run used a single reader (the session) with self-refutation against code and tests, on the standing instruction not to dispatch subagents. Every finding below was refuted against primary evidence before it was recorded, and four candidates died there — but the *second-reader* leg did not run, so this run under-samples rather than surveys.
- **Comparison not made**: the eleven `references/` files were not cross-read against each other for internal contradiction.

---

## 1. `rethink-audit` — clean-slate design pass

### `requires:`

What the skills layer must do, tagged by evidence.

| # | Requirement | Evidence |
|---|---|---|
| R1 | Every mechanical act (event, status, tag, hold, finding, ack, search-log line) goes through a CLI verb; prose never writes durable state | `adr` — spec §7 "deterministic-Python-core + thin-prompt-skill split"; Plan D global constraints |
| R2 | Four-state honesty on every surface: an outage is never a failure and never a pass | `adr` — ADR 0002, CONTEXT.md "Four-state result" |
| R3 | Entry skills ship `disable-model-invocation: true`; guards are model-invoked and user-invocable; nothing ships `user-invocable: false` | `adr` + `tests` — spec §7 control model, `tests/test_skill_contracts.py:103-118` |
| R4 | Admission is a human act in Zotero, and the only route to citability | `adr` — CONTEXT.md **Admission**; parked ADR candidate "evidence-layer-is-projection" |
| R5 | The Iron Law: no claim enters a draft before its citekey resolves | `docs` — spec §5/§7 |
| R6 | PRISMA-S search provenance, append-only, project-scoped | `docs` — spec §7 `find-sources` row |
| R7 | Deprecate, never delete | `adr` — ADR 0003 |
| R8 | The vault outlives the harness; skills write vault-portable content only | `adr` — ADR 0001 |
| R9 | Skill prose uses CONTEXT.md vocabulary; every new identifier gets its terminology §4.3/§4.4 row in the same commit | `docs` — Plan D global constraints |
| R10 | Nine skills, names ruled | `docs` — terminology §4.3 line 127; Plan D Task 8 "the count is nine, not ten" |
| R11 | The vendored fork stays frozen: re-vendor to update, never hand-edit | `docs` + `tests` — spec §7 dependency discipline, `tests/test_find_sources_vendor.py` |
| R12 | A human can reach the right skill without holding all nine in their head | `assumed` — no recorded requirement; the user-driven control model implies it and nothing states it |

**Callers accounted for.** The skills have three classes of caller and all three were swept: the **human** typing a skill name (seven user-invoked entry points); **other skills** invoking the two guards (`project` → `evidence-conventions`, `import-source` → `synthesis-conventions`); the **shipped vault `AGENTS.md`** template, which names exactly one skill (`evidence-conventions`) and otherwise says "prefer the knowledge-harness skills" without naming them. Not reachable from this repo: how a real installed session resolves bare cross-reference names against the plugin namespace (see finding C-4), and any downstream consumer outside this checkout.

### `prior-art:`

- **Shared-reference-in-a-model-invoked-skill** (`writing-for-agents/SKILL-MECHANICS.md`): user-invoked skills carry no description, so they cannot invoke each other; shared reference has to live in a model-invoked skill or a plain external file. This repo already uses the pattern correctly — the two guards exist precisely so the seven entries can reach them. It is the answer to the duplication this audit found, and it is already in the building.
- **Router skill** (same source): the cure for user-invoked skills multiplying past what a human remembers. `project`'s Routing table is the shape, in the wrong place — it is itself user-invoked, so it can only be read by someone who already knew to type it.
- **Progressive disclosure by branch** (`writing-for-agents`): inline what every branch needs, push behind a pointer what only some branches reach. `find-sources` already does this correctly with its eleven-row database table; `import-source` does not.
- **Thin-prompt-over-deep-core** (spec §7, claude-obsidian's shape): the skill carries orchestration and normative rules; the CLI carries mechanics. Fits these requirements because the gate surfaces (pre-commit, CI) run where no model session exists.

### `design:`

The clean-slate structure the requirements imply, in `codebase-design` vocabulary.

**The deep module is the CLI. The skills are its interface layer** — and an interface layer should carry each contract exactly once. Three seams:

1. **A verification-vocabulary home.** The four-state contract, the mint-set (`doi`, `metadata`, `update-notice`, per-claim `quote`, plus the project-level `publish` event), the exit-code table, and the never-hand-write doctrine are one invariant serving five surfaces. It gets one authoritative home in a model-invoked skill, and every entry skill invokes it rather than restating it — the same move `project` already makes for the Iron Law ("read and follow that skill directly; do not paraphrase or re-derive its rules here").
2. **Entry skills carry only their surface delta.** What is different about *this* surface: which checks close it, what the verb does, what the person chooses. `verify-citations` becomes an orientation + one command + a grouping rule. `publish` keeps its disposition menu and correction lifecycle, and drops the four-state table.
3. **One reachable index.** A single always-reachable pointer that names the seven entry points and when to reach for each. The shipped vault `AGENTS.md` is the natural home — it already ships per-vault, already routes, and already names one skill.

**Where the target contradicts a ruling.** Seam 1's cleanest form is a tenth skill (`verification-conventions`, guard-class). R10 rules the count at nine. The case for reopening: the nine-count was a *scope* ruling about which capabilities ship, not a design rule about where shared reference lives, and the repo's own control model already provides for guard skills whose entire purpose is to be a shared home. The cheaper form that does not reopen anything: put the contract in `evidence-conventions`, which is already model-invoked and already the home of the shared reason-code registry. **Recommendation: take the cheaper form.** It satisfies the requirement, costs no new always-loaded description, and keeps the ruled count intact.

Every requirement is answered: R1/R2 by seam 1 (one statement of the doctrine, invoked not copied); R3–R11 unchanged by this design; R12 by seam 3.

### `gap:`

Where the current implementation diverges from that target.

| Divergence | Accident, dead constraint, or real? |
|---|---|
| Four-state semantics stated in four entry skills | **Accident of authoring order** — Plan D wrote the skills task by task, each transcribing §6, with no shared home nominated. Real residue: the per-surface columns genuinely differ (gate/import/LLM), so only the invariant is duplicated, not the whole table |
| Never-hand-write doctrine restated in five skills | **Accident**, same cause |
| No reachable index over the seven entry points | **Real gap against an assumed requirement** — R12 is `assumed`; the user-driven control model deliberately keeps entries out of the model catalog, and no one ever wrote down what replaces discovery |
| `verify-citations` names ten check ids where `verify` emits fourteen | **Defect**, see finding C-1 |
| `setup-vault` enumerates scaffold's created paths in prose | **Real constraint, partly** — `tests/test_skill_files.py:111-119` pins six of them, so the enumeration is load-bearing for a test that exists to stop a specific dishonesty ("claiming unrelated work was committed"). The path *list* is still a cache of what the command prints |
| `import-source` at 2,206 words, nine numbered sections | **Accident** — §7 refresh, §8 batch, §9 archive are branches only some runs reach |
| `project` is a bare domain noun | **Dead constraint** — ruled in terminology §4.3 as a "plain descriptive name", before the collision with CONTEXT.md's **Project** (the artifact) mattered |

### `migrate:`

Smallest safe steps, ordered. Each is independently mergeable and independently revertable.

1. **Fix `verify-citations`'s check-id enumeration** (C-1). Name what `verify` actually emits, or state the ten as "§6's suite" and add a catch-all grouping rule for the rest. Isolated, no other skill touches it.
2. **Fix the two count claims** (C-2, C-3). One sentence each.
3. **Land the four-state contract in `evidence-conventions`** as a new section — additive only, nothing removed yet. The suite stays green throughout.
4. **Replace the four copies with invocations**, one skill per commit, in ascending blast radius: `verify-citations`, `factcheck-draft`, `import-source`, `publish`. Each commit keeps the surface's own delta rows and deletes only the invariant. Re-run `tests/test_skill_contracts.py` and the per-skill content tests after each.
5. **Disclose `import-source`'s branch material** — §7/§8/§9 move to `skills/import-source/references/`, reached by a pointer table in the same shape `find-sources` already uses. Content unchanged, so no test moves.
6. **Add the routing lines to the vault `AGENTS.md` template** — the seven entry names and one clause each. `tests/test_skill_contracts.py:153` already asserts every skill name a shipped template cites has a directory, so this step self-validates.
7. **Put the `project` rename to the author** as a terminology question, not a change. If it is taken, it moves in one commit with its §4.3 row, `tests/test_project_skill.py`, and the routing tables in `find-sources` and `import-source`.

Steps 1–2 close the confirmed defects. Steps 3–6 close the structural divergences. Step 7 is a decision, not a migration.

### `trade-offs:`

- **A shared four-state home makes each entry skill less self-contained.** An agent invoked straight into `publish` no longer has the outage doctrine in front of it — it has a pointer. The constraint that would flip this: if invocations of the guard prove unreliable in practice, the copies are the safer form and the duplication is the price of a guarantee. *This is the trade that matters most and it is empirical — Plan D never measured it.*
- **Prose-pinning tests make text moves expensive.** `tests/test_skill_files.py` asserts 30+ exact phrases in `setup-vault`. Any rewording for clarity is a test edit. The constraint that justifies it: this repo has a documented drift problem and prose is the one surface no other test reads. Flipping condition: if the pins start blocking correctness fixes rather than catching drift.
- **Routing lines in the vault `AGENTS.md` spend vault-side context on every turn.** Seven names plus clauses, always loaded inside a vault repo. Flipping condition: if the author never forgets a skill name, R12 is not a real requirement and this cost buys nothing.
- **Disclosing `import-source`'s branches costs a file hop** on the runs that do reach refresh or batch mode. Flipping condition: if most real imports are refreshes, the "rare branch" premise is wrong and the material belongs inline.

**Not "already sound. Keep."** — the four-copy duplication and the missing index are real structural divergences, not invented ones. But the layer is closer to its first-principles shape than most: the hard part (mechanics in the CLI, prose in the skill) is right, and every step above is additive.

---

## 2. `writing-for-agents` + `superpowers:writing-skills` — conformance pass

**Where the two frameworks disagree, and which governs.** `writing-skills` sets word-count targets (<500 words for a general skill). `writing-for-agents` rejects the count and frames the same failure as **sprawl**, cured by the information hierarchy. **`writing-for-agents` governs here**, because seven of nine skills are user-invoked: they cost *zero* context load until typed, so a word budget measures the wrong thing. The right question is whether the material is branch-uniform — inline what every run needs, disclose what only some runs reach.

### Per-skill

| Skill | Words | Invocation | Verdict |
|---|---|---|---|
| `synthesis-conventions` | 233 | guard (model) | **Exemplary.** Four rules, flat peer-set, every one branch-uniform. The `2+-source threshold` and `minimum-link discipline` are leading words doing real work |
| `setup-vault` | 474 | entry (user) | Sound. The scaffold path enumeration is a cache (P-2) |
| `verify-citations` | 672 | entry (user) | ~45% of the body is four-state restatement. Defect C-1 lives here |
| `project` | 917 | entry (user) | Sound. The draft-frame section models the target behaviour: *"Read and follow that skill directly; do not paraphrase or re-derive its rules here"* — this is the single-source-of-truth rule stated in the document that most needs it |
| `factcheck-draft` | 972 | entry (user) | Sound. Selection order is stated as binding, with the reason (quote claims already deterministically covered) — demand and clarity both present |
| `evidence-conventions` | 1,198 | guard (model) | Sound. Carries the reason-code registry for the whole plugin — correct home. Rationalization table is textbook `writing-skills` bulletproofing |
| `publish` | 1,446 | entry (user) | Sound. Longest section (correction lifecycle) is genuinely branch-uniform for a published project |
| `find-sources` | 1,670 | entry (user) | **Best disclosure in the corpus.** Eleven database references behind a one-row-per-branch pointer table; five scripts behind `--help`. The SKILL.md keeps only what every search needs |
| `import-source` | 2,206 | entry (user) | **Sprawl.** Nine numbered sections; §7 refresh, §8 batch, §9 archive are reached by a minority of runs and sit inline at full weight |

### Levers

**Context pointers.** All nine descriptions front-load their trigger and carry no workflow summary — `writing-skills`' SDO rule, obeyed. One form mismatch: `SKILL-MECHANICS.md` says a user-invoked skill's description becomes *human-facing* with trigger lists stripped, and all seven entries keep the model-facing "Use when a person asks to…" shape. Costs nothing (these descriptions never load), so this is a style note, not a finding — and `tests/test_project_skill.py:27` and `test_skill_files.py:19` both pin the `Use when ` prefix, so changing it is a test edit for no gain. **Leave it.**

**The two loads, accounted.** Context load: two guard descriptions, always loaded — correct, they are the only skills that must be model-reachable. Cognitive load: seven entry-point names the human must remember, with no router. That is the whole of finding P-1.

**Information hierarchy.** One real inversion: `verification-conventions`-class material (tier-2 in-file reference in four skills) should be tier-3 disclosed reference in one. One real sprawl case (`import-source`). Everything else sits at the right rung.

**Steps and completion criteria.** Strong throughout. `find-sources`'s *"only a call that actually completed gets logged"*, `import-source`'s *"no SKIPPED identifier result is final until discovery has been attempted"*, and `factcheck-draft`'s *"an unchecked claim must never read as checked"* are all checkable and exhaustive. No premature-completion risk found: these are report-then-stop skills whose post-completion steps are the person's, not the agent's.

**Leading words.** The corpus has a genuinely good vocabulary — *admission*, *projection*, *managed region*, *four-state*, *outage*, *closing check*, *the Iron Law*, *fresh / stale / orphaned*, *arming*. Each recruits priors, each is repeated as a token rather than restated as a sentence, and CONTEXT.md holds the distributed definition. This is the strongest single thing about the layer. One passage still begs to collapse: the never-hand-write refrain appears in five spellings across five skills (`project:84`, `import-source:11`, `publish:11`, `verify-citations:9`, `find-sources:71`) where one leading word — *the CLI writes* — would carry it.

**Negation.** 154 prohibitions across 9 skills (`import-source` and `find-sources` at 27 each). `writing-for-agents` calls negation a failure mode; `writing-skills`' *Match the Form to the Failure* table sanctions prohibition + rationalization table for **discipline** failures — an agent that knows the rule and skips it under pressure. Sorted by that test:

- **Sanctioned, keep**: the honesty guards. *"Never describe an UNREACHABLE result as failed"*, *"never claim a check ran that did not"*, *"never invent a citekey"*, *"never type `discard` on their behalf"*. These are exactly the discipline class — the model knows better and rationalizes under pressure to produce a clean answer. `evidence-conventions`' rationalization table is the correct companion form and it is present.
- **Wrong form, fix**: the shaping prohibitions. `find-sources`' *"not as a raw dump"* and `verify-citations`' *"not in raw run order"* are output-shape instructions written as prohibitions — the arm `writing-skills` measured as performing *worse than no guidance*. Both already carry their positive recipe alongside ("per candidate: title, authors, year, venue; identifiers; enough provenance…"; "grouped by check id"). **Cut the prohibition half, keep the recipe.**

**Testing (`writing-skills`' Iron Law).** No RED-GREEN-REFACTOR anywhere: no baseline run, no pressure scenario, no recorded rationalization harvested from a failing agent. Plan D never required one, so this is a gap against the framework, not a plan violation. What exists instead is four static test modules — and one of them, `tests/test_skill_contracts.py:133`, is better than what the framework asks for: it parses every shipped `finding` invocation out of every SKILL.md with `shlex` and validates the check id and reason code against the live registry. **A shipped command that the CLI would refuse fails the build.** That is the mechanical-constraint-automated rule applied exactly right. The prose pins in `test_skill_files.py` are the inverse — regex over judgment prose — and are the trade-off recorded above, not a defect.

---

## 3. `ponytail-audit` — over-engineering, ranked

```
shrink: four-state semantics restated in 4 entry skills (~55 lines). One section in
        evidence-conventions + per-surface delta rows. [verify-citations:29-36,
        publish:35-42, import-source:152-161, factcheck-draft:66-75]
yagni:  import-source §7/§8/§9 (refresh, batch, archive) inline at full weight for
        every run. references/, pointer table — the shape find-sources already ships.
        [import-source/SKILL.md:92-151]
shrink: never-hand-write doctrine in 5 spellings. One leading word, invoked.
        [project:84, import-source:11, publish:11, verify-citations:9, find-sources:71]
yagni:  setup-vault's 14-path scaffold enumeration, beside "report its exact printed
        created paths". The command prints them. Keep only the six the test pins,
        as an honesty rule rather than an inventory. [setup-vault/SKILL.md:21]
shrink: verify-citations — ~45% of 672 words is restated four-state. After the
        contract moves: orientation, one command, a grouping rule.
        [verify-citations/SKILL.md]
delete: two shaping prohibitions whose positive recipe already sits beside them.
        ["not as a raw dump" find-sources:88; "not in raw run order"
        verify-citations:27]

net: -110 to -140 lines of SKILL.md prose, -0 deps.
```

**Not over-engineered, checked and cleared:** the eleven `references/` files and five `scripts/` (vendored, frozen, correctly disclosed — deleting any is deleting capability); the nine-skill split (one per §7 row, no skill with a single caller); the two-guard/seven-entry control model (each guard has two callers); the CLI-verb-per-mechanical-act doctrine (that is the architecture, not ceremony); `tests/test_skill_contracts.py` (generic, parametrized, no per-skill duplication).

---

## 4. `consistency-audit` — findings

Ranked by severity. Every card was refuted against code, tests, or the reference files before it was recorded. The **State** field on each card is this run's triage; the author's ruling on every one of them is recorded in §5 below and supersedes it.

---

### C-1 · `verify-citations` names ten check ids; `verify` emits fourteen — MEDIUM

**Where** `skills/verify-citations/SKILL.md:9,27`

**Quote** *"the deterministic suite of §6 (citekey, DOI, metadata, quote, update-notice, evidence-layer, identifier-discovery, web-archive, screening-state, disputed-claim)"* … *"Present the printed lines to the person **grouped by check id** (the second token on each line — `citekey`, `doi`, `metadata`, `quote`, `update-notice`, `evidence-layer`, `identifier-discovery`, `web-archive`, `screening-state`, `disputed-claim`)"*

**Contradiction** `knowledge_harness/verify.py:850` appends a `staleness` outcome on **every** run, and `verify.py:889-894` appends `append-only`, `claim-immutability`, and `published-drift` outcomes on every run, regardless of `--surface`. `docs/terminology.md:46-50` states this directly: *"the deterministic pipeline (verify.py, lints.py) legitimately files ids this registry does not carry (`staleness`, `append-only`, `claim-immutability`, `published-drift`, `publish-gate`)"*.

**Verdict** `confirmed`. Refutation attempted on two readings and both failed: (a) *"the list is scoped to §6's suite, not to what prints"* — the second use of the list is explicitly about "the printed lines" and "the second token on each line", so it is a claim about output; (b) *"the extra ids only appear on the commit surface"* — `verify.py:850` is unguarded by surface, and offline it emits `staleness` UNREACHABLE with reason `outage — network disabled`. That is precisely the result class this skill spends most of its length teaching a person to read correctly, arriving in a bucket the skill's own grouping rule cannot name.

**State** `ready-for-agent` — *repair*: extend the enumeration to what the verb emits, or mark the ten as §6's closing-capable subset and add a rule for grouping everything else.

---

### C-2 · `evidence-conventions` claims one registry code is out of scope; two are — LOW

**Where** `skills/evidence-conventions/SKILL.md:86`

**Quote** *"One registry code (`manual`) belongs to a surface not shipped yet — it gets its own glossary row when that surface lands."*

**Contradiction** `knowledge_harness/inbox.py:24-45` — `REASON_CODES` carries 18 members. The table above the quoted line documents 16. Unaccounted: `manual` **and** `matched`.

**Verdict** `confirmed`, low. Partial refutation holds and lowers the severity: `matched` is the reason string attached to MATCHED outcomes (`verify.py:508`, `checks.py:220`, `quotes.py:101`, `archive.py:140`), and MATCHED never files a finding — so it genuinely never appears in the review queue, and the table's own stated scope (*"the codes you meet in the review queue today"*) is correct. What is wrong is only the closing sentence's claim of completeness-with-one-exception.

**State** `ready-for-agent` — *repair*: *"Two registry codes stay off this table: `matched` never reaches the queue (only non-MATCHED results file findings), and `manual` belongs to a surface not shipped yet."*

---

### C-3 · `find-sources` under-counts the APIs that carry a credential in the query string — LOW

**Where** `skills/find-sources/SKILL.md:50`

**Quote** *"Two of these APIs authenticate by query string, so the fetched URL *is* a credential: never echo an API key, and never paste an un-redacted URL into a report"*

**Contradiction** Three reference files document a query-string API key — `references/core.md:23` (`?api_key=`), `references/pubmed.md:21` (`&api_key=`), `references/openalex.md:21` (`?api_key=`) — and a fourth requires an email as a query parameter, `references/unpaywall.md:20`.

The same line carries a second, independent under-count of the same class: its hand-redaction escape hatch names **four** parameters (`api_key`, `email`, `mailto`, `tool`) where `scripts/_common.py:201` strips **six** — `REDACTED_PARAMS = {"api_key", "apikey", "key", "email", "mailto", "tool"}`. A person redacting by hand against the skill's list misses `apikey=` and `key=`.

**Verdict** `confirmed`, low. Strongest refutation, which survives partially: under "*requires* a credential", CORE and Unpaywall are the only two — PubMed's and OpenAlex's keys are optional rate-limit upgrades, so the author's "two" has a defensible reading. It fails as written because the sentence's operative content is *which URLs are unsafe to paste*, and a PubMed URL carrying an optional `&api_key=` is exactly as unsafe as a CORE one. The practical exposure is small: the redaction rule immediately following covers all of them by parameter name.

**State** `ready-for-agent` — *repair*, two edits on one line: drop the count (*"Several of these APIs take a credential in the query string, so the fetched URL* is *a credential"* — the rule then binds every case without an inventory to keep current), and either complete the hand-redaction list to all six or replace it with a pointer to `redact_url`'s own set.

---

### C-4 · Cross-reference names are bare where the plugin namespaces them — LOW, `unsettled`

**Where** Routing tables and inline references throughout: `project/SKILL.md:68-74`, `find-sources/SKILL.md:98-103`, `import-source/SKILL.md:165-171`, `verify-citations/SKILL.md:44`, `publish/SKILL.md:83`

**Quote** *"| Acquire new sources | `find-sources` |"*

**Contradiction** `.claude-plugin/plugin.json` names the plugin `knowledge-harness`, and `docs/superpowers/plans/2026-08-20-plan-t-terminology-wave.md:242` writes the namespaced form for the same skills: `/knowledge-harness:setup-vault`, `…:find-sources`, `…:synthesis-conventions`. The shipped vault `AGENTS.md` template uses the bare form (*"Run `evidence-conventions` for claim syntax"*).

**Verdict** `unsettled` — and deliberately not rounded up. Two of these targets (`evidence-conventions`, `synthesis-conventions`) are model-invoked, so an agent resolves them from its own catalog whatever the spelling. The other five are user-invoked, so the routing line is a *human* instruction, and a human types what the picker shows. Whether the bare name resolves for either audience is a fact about an installed session that this repository cannot settle. `tests/test_skill_contracts.py:153` proves only that a directory of that name exists — not that the name is invocable as written.

**State** `ready-for-human` — one session with the plugin installed settles it. Options: **(a)** leave bare, on the reading that routing lines address the human and the picker disambiguates — *recommended*, it is what ships and nothing has failed; **(b)** namespace every cross-reference, which is unambiguous and costs a rename across five skills plus the vault template if the plugin is ever renamed; **(c)** namespace only the five user-invoked targets, which is correct-by-audience and inconsistent-by-eye. *This audit cannot pick for you.*

---

### C-5 · The vendored `paginate.py` docstring describes a corpus the fork does not have — LOW

**Where** `skills/find-sources/scripts/paginate.py:11`

**Quote** *"Six of the ten databases here paginate differently"*

**Contradiction** `python3 skills/find-sources/scripts/paginate.py --list-apis` returns **five** APIs (`biorxiv`, `crossref`, `europepmc`, `medrxiv`, `openalex`), matching `APIS` at `paginate.py:264-300`. `skills/find-sources/SKILL.md:11` states the fork carries **eleven** per-database reference files, and its own table at lines 44 names five for this script — correctly.

**Verdict** `confirmed`, low, and **structurally unfixable under the current ruling**. The file's own header says *"Do not hand-edit this file; re-vendor from upstream to update it"*, and spec §7's dependency discipline is explicit that vendoring is *"preferred where behavior must stay frozen"*. The stale sentence is upstream's, inherited. Reader impact is near-zero — the SKILL.md's table is correct and is what an agent reads first.

**State** `ready-for-human` — the real question is policy, not this line. Options: **(a)** accept it, and add one line to the vendoring note that upstream prose may describe upstream's corpus rather than this fork's — *recommended*, cheapest and honest; **(b)** extend the frozen-behaviour rule to permit factual-comment corrections, which reopens "frozen" and invites judgment calls at every re-vendor; **(c)** carry a fork-local patch file, which is maintenance for a comment. *Leave it as it is* is a legitimate answer.

---

### C-6 · `setup-vault` keeps a second copy of a list the command prints — LOW

**Where** `skills/setup-vault/SKILL.md:21`

**Quote** *"Run scaffold and report its exact printed created paths. On a fresh vault, scaffold can create `.git/hooks/pre-commit`, `.gitignore`, `.harness/machine.json`, `AGENTS.md`, … and `system/templates/` daily, literature, project, and synthesis templates"*

**Contradiction** Not a factual contradiction — the enumeration matches `knowledge_harness/templates/vault/` exactly, verified file by file. It is a **duplication** finding: two sources of truth for one fact, one of them a cache of a lookup the same paragraph instructs the agent to perform. `scaffold.scaffold_vault()` returns `sorted(created)` (`scaffold.py:241`) and the skill's first instruction is to report it.

**Verdict** `confirmed` as duplication. Refutation partly holds and constrains the fix: `tests/test_skill_files.py:111-119` pins six of these paths, and that test exists for a real dishonesty (*"Claiming unrelated work was committed must fail"*). The pinned six are load-bearing; the other eight are inventory that goes stale the next time a template lands.

**State** `ready-for-agent` — *record*, not a plain repair. Probe first per the method: add a template, run `scaffold`, and see whether anything catches the divergence before this prose does. The deliverable is the honesty rule kept and the inventory dropped — *"scaffold prints every path it created; report that list verbatim, and never present a path it did not print as committed"* — with `test_skill_files.py` narrowed to the six pinned names it actually defends.

---

### C-7 · No reachable index over seven user-invoked entry points — LOW

**Where** `knowledge_harness/templates/vault/AGENTS.md:8`; the absence spans `skills/` as a whole

**Quote** *"Prefer the knowledge-harness skills over generic drafting, even for free-form requests. Run `evidence-conventions` for claim syntax."*

**Contradiction** Seven of nine skills ship `disable-model-invocation: true`, so nothing but a human typing the name can reach them. The one always-loaded routing surface names one skill — a guard the agent could already reach on its own — and gestures at the other eight without naming them. `project`'s Routing table (`project/SKILL.md:66-74`) is the index, inside a user-invoked skill, reachable only by someone who already knew to type it.

**Verdict** `unsettled`. The requirement it violates (R12) is `assumed` — no spec row, no ADR, no plan step states that a human must be able to discover the entry points, and the user-driven control model deliberately trades agent discoverability for the absence of process-skill collisions. That trade was ruled; what was never written down is what replaces discovery on the human side. `writing-for-agents` names the pattern (a router skill) and its cost (cognitive load, *"the price of human agency"*, not a cost to minimise).

**State** `ready-for-human`. Options: **(a)** add the seven names with one clause each to the vault `AGENTS.md` template — *recommended*: it self-installs per vault, it is the surface that already routes, `tests/test_skill_contracts.py:153` already validates every name it cites, and it costs vault-side context only inside a vault; **(b)** a tenth router skill, which reopens the ruled nine-count for a job the template already does; **(c)** leave it — legitimate if you never reach for a name you cannot remember, which only you can say.

---

### Refuted candidates

Recorded so a reader of this report can see what was examined and rejected. A refutation holds only while its reason holds; no second judge checked these.

| Candidate | Why it died |
|---|---|
| *"Plan D Task 1's `test_skill_contracts.py` never landed — the acceptance instrument is missing"* | The file exists at `tests/test_skill_contracts.py`, 166 lines, with the generic contract, the control-model assertion, **and** the landing check Task 8 named (line 153). Missed on a first grep that filtered on the wrong pattern. The framework's own rule earned its keep here |
| *"Eight of nine skills ship untested"* | `tests/test_skill_contracts.py` is parametrized over **every** shipped `SKILL.md` — frontmatter, name/dirname, description, invocation flags, and `finding`-invocation validity all run for all nine. Content acceptance is per-skill for three (`setup-vault`, `project`, the `find-sources` vendor), which is exactly what Plan D's task steps required |
| *"`skills/find-sources/scripts/__pycache__/` ships a `.pyc` in the plugin"* | `git ls-files skills/ \| grep pycache` returns nothing; `.gitignore:8` carries `__pycache__/`. Untracked local build artifact, not shipped |
| *"The shipped vault glossary contradicts the skills on event minting — it says only MATCHED mints, the skills say only four check ids mint"* | Not a contradiction. `templates/vault/system/glossary.md:86` states a necessary condition, the skills state the sufficient one. Both true |
| *"`§5`/`§6`/`§7` references in five skills point at a document that does not ship"* | A plugin install clones the whole repository — `docs/` travels (verified against two installed plugin caches). The *weak-pointer* concern survives as a style note (the references carry no path), but the target is not missing, and the corpus-shipping question is already a recorded release-gate item in spec §10 that this audit does not re-litigate |
| *"154 prohibitions is negation-driven steering at scale"* | Sorted per `writing-skills`' *Match the Form to the Failure*: the overwhelming majority are discipline guards on honesty claims — the sanctioned case for prohibition + rationalization table. Only two are shaping prohibitions, and they are recorded above as a ponytail line, not as a finding |

### Could not verify

- **Whether bare cross-reference names resolve in an installed session** (C-4). Needs a live session with the plugin installed; this checkout cannot answer it.
- **Whether the four-state contract survives being invoked rather than inlined.** The trade-off recorded in §1 is empirical and no baseline exists — `writing-skills`' RED phase is the instrument, and it has never been run on this corpus.

### For the next run

Proposals about scope, not findings — they go to the author with everything else:

- The eleven `references/` files were never cross-read against each other. That is the largest unaudited surface in `skills/` (2,000+ lines) and a natural slice of its own.
- Prose-vs-CLI drift is the recurring class here (C-1, C-2, C-3, C-6 are all one shape: a skill enumerating something the code owns). `tests/test_skill_contracts.py:133` already generalizes one instance of it — parsing shipped `finding` invocations and validating them against the live registry. **C-1 is the same class and admits the same instrument**: assert that every check id a SKILL.md enumerates is one `verify` can emit. That is a checker spec worth writing.
- This run had no second reader and no independent skeptic. A repeat with the full method should assume it under-sampled.

---

## What is strong here

Recorded deliberately — a redesign invented to justify an audit is the failure the method exists to prevent, and most of this layer is right.

- **The invocation split is a correct, non-obvious application of `SKILL-MECHANICS.md`.** User-invoked skills have no descriptions and cannot invoke each other; shared reference has to live somewhere model-invoked. The two guards exist for exactly that, and `project`'s draft-frame section proves the pattern works in practice: it invokes `evidence-conventions` and explicitly refuses to restate it. Most skill collections get this wrong by copying.
- **`find-sources` is textbook progressive disclosure.** Eleven database references and five scripts behind one branch-per-row pointer table, with the failure modes that are *not* branch-specific — the HTTP-200 hazards — kept inline where every run meets them.
- **`tests/test_skill_contracts.py:133` is better than the frameworks ask for.** It `shlex`-parses every `finding` command out of every SKILL.md and validates the check id and reason code against the live registry, so a shipped command the CLI would refuse fails the build. That is the right answer to "prose is the one surface no test reads".
- **The vocabulary is doing real work.** *Admission*, *projection*, *managed region*, *outage*, *closing check*, *fresh / stale / orphaned*, *arming*, *the Iron Law* — repeated as tokens, defined once in CONTEXT.md, governed in terminology §4.3/§4.4. This is the leading-word lever applied systematically across nine documents, and it is why the corpus reads as one system rather than nine.
- **Four-state honesty is genuinely enforced, not gestured at.** Every skill that can report a result distinguishes "could not run" from "ran and disagreed", refuses to round an outage up or down, and names the CLI as the only writer of events. The duplication finding above is a *consequence* of taking this seriously in four places at once — the right problem to have.

---

## 5. Adjudication (author ruling, 2026-08-22)

Every finding above is ruled. This section supersedes the per-card **State** fields, which record the audit's triage rather than the decision.

### The shape rule

The audit's own diagnosis governs the fixes: C-1, C-2, C-3 and C-6 are one class — **prose enumerating what code owns**. The remedy for that class is **defer to the code, or pin the enumeration by test. Never hand-maintain one.** Each ruling below is an application of that rule, not an independent judgement.

### Ready-for-agent — all four accepted

| # | Ruling | Deliverable |
|---|---|---|
| C-1 | **Defer to code.** `verify-citations` stops hand-listing check ids altogether. The prose says *grouped by check id as the CLI reports them* and teaches the four states, not the fourteen ids — the id inventory is `--help` and output territory. This dissolves the unnameable-bucket problem rather than patching it | *repair* |
| C-2 | **Complete and pin.** This is teaching prose, so it stays and gets correct: two codes off the table, not one. The enumeration is then test-pinned | *repair* + checker |
| C-3 | **Align to `redact_url`.** The code is the authority on both counts — three query-string-auth databases, six redacted parameters | *repair* |
| C-6 | **Drop the inventory.** The 14-path list duplicates what the command prints; *"report its exact printed created paths"* was already the right instruction standing alone | *repair* |

**Checker spec — approved.** Extend the `tests/test_skill_contracts.py` instrument to pin every enumeration that survives the fixes (C-2's reason codes). Same mechanism as the existing `finding`-invocation validator, same commit as the fixes.

### Ready-for-human — ruled

**C-4 · Bare cross-reference names — option (a), leave bare.** It ships, nothing has failed, and prose instructions read better bare. The incident that flips this is a real name collision with another plugin's skill. Until then namespacing is foresight, and this repository knows what happens to foresight. → `wontfix`, with the flipping condition on record.

**C-5 · Stale vendored docstring — option (a), accept with an annotation.** One line added to the vendoring note: *upstream prose describes upstream's corpus.* The same move as the existing *"no additional source legs are owed"* parenthetical — an annotation that stops the next auditor re-finding it. The frozen-behaviour rule stays intact. → `ready-for-agent`, *record*.

**C-7 · No reachable index — option (a), the seven names in the vault `AGENTS.md` template.** This addition passes the context bar where most fail it: the template already instructs *"prefer the knowledge-harness skills"* without saying which exist, and **an instruction the reader cannot follow is worse than a missing one.** Every vault session is the branch, so the material is branch-uniform; `tests/test_skill_contracts.py:153` already guards the names mechanically. Option (b)'s tenth router skill would reopen the ruled nine-count for what one paragraph does. Dialect surface: the whole-file test pin updates in the same commit. → `ready-for-agent`, *repair*.

### Sequencing

**No mid-flight grafts.** These fixes queue as the Task-0 rider on the first post-Q batch, per the now-standing practice. `HEAD` stays clean of them until Plan Q lands.

### Next audit slice — approved

The eleven `references/` files (2,000+ lines, never read) become their own audit slice.

### Could-not-verify dispositions (author ruling, 2026-08-22)

- **C-4 empirical half**: unverifiable in any checkout — the test is a live session with the plugin installed. Joins the validation-slice checklist: first vault session confirms the routing table's bare names resolve. Leave-bare stands until then.
- **Four-state dedup (the §1 structural divergence)**: DEFERRED PENDING EVIDENCE, not accepted. Whether an invoked guard preserves compliance like inlined text has no baseline; `writing-skills`' RED phase is the instrument and runs BEFORE any dedup. Until then the four copies are deliberate redundancy in trust-critical prose.

### Next-run rulings

References cross-read: approved, own slice, run with the FULL adversarial method (finders + independent refuters — no standing rule bars subagent skeptics; that was a misread). Enumeration checker: approved, ships with the C-1/C-2 fixes. All fixes ride the first post-Q batch (no mid-flight grafts).

### Second-pass rulings (author, 2026-08-22 — items between the relay and the full report)

- **Migrate step 5 APPROVED**: `import-source` §7–9 disclose into `references/` + pointer table (the find-sources shape); flip recorded (refresh-dominant usage returns them inline). Post-Q batch.
- **"The CLI writes" leading-word collapse APPROVED** (five spellings → one inline token; no invocation dependency, RED gate does not apply). Post-Q batch.
- **Both shaping prohibitions CUT** (recipes already present). Post-Q batch.
- **Migrate steps 3–4 remain RED-gated** (unchanged). **Step 6 = C-7(a)** (unchanged). **Step 7 (`project` rename)**: open author decision — class-4 collision with CONTEXT.md's Project, pre-slice is the cheap rename window.
- **Open investigations**: (1) the RED-phase baseline experiment — designable now, gates steps 3–4, closes the Iron-Law gap; (2) the references cross-read — in flight as its own full-method run; (3) C-4's empirical half — slice checklist.

**Step 7 decided (2026-08-22): `project` → `project-flow`** — the glossary's own *Project flow* term; collision dissolved, not mitigated. Rides the post-Q batch, ordered before the C-7 index.
