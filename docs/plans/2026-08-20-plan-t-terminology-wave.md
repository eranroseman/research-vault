# Plan T: Terminology Wave + Reference-Only Terminology Doc — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute every ruled rename and addition from `docs/terminology.md` §9–§10 (the naming pass, inversion deltas, OKF conformance artifacts) across code, templates, tests, spec, and skills — then collapse `docs/terminology.md` into a reference-only document, its working sections having been executed.

**Architecture:** One coherent wave in dependency order: paths/types first (everything else greps against them), then frontmatter keys/values, inline fields, inversion additions, OKF artifacts, skill renames, doc alignment, and finally the terminology-doc restructure. The existing test suite is the safety net — every task ends suite-green with a judged grep proving no old string survives on living surfaces.

**Tech Stack:** Python ≥3.10 stdlib (as-built `harness_core`), pytest, git.

**Authority:** `docs/terminology.md` §10 manifest is the contract (all rulings author-confirmed). **As-built HEAD governs** over any code shape this plan assumes; where a named symbol or file differs at HEAD, adapt within-task and record it in the commit message. The **history rule** binds every task: living surfaces rename (`core/`, `hooks/`, `skills/`, `docs/specs/`, active plan docs, `README.md`, `docs/terminology.md`); history never does (`research/`, `analysis/`, completed plans A/B, audit docs, ADRs already accepted, git history).

## Global Constraints

- Worktree via `superpowers:using-git-worktrees`, branch `build/terminology-wave`. If Plan C is unmerged when this plan starts, **merge or land Plan C first** — this wave must not interleave with it (§10 sequencing rule).
- Every test Run begins `cd core && python3 -m venv .venv 2>/dev/null; source .venv/bin/activate && pip install -e ".[dev]" -q` (idempotent; PEP 668).
- **Greps are judged, never blind-replaced**: words like "atlas", "retrieved", "drafting" may appear in ordinary prose senses and in history-rule-protected paths; every hit is classified before touching.
- Rename churn is mechanical; **semantics must not change** except the four ruled additions (Task 4) and the OKF artifacts (Task 5). If a rename forces a behavior question, stop and escalate as an SDD ruling.
- Commit messages conventional; one commit per task.
- Full acceptance at the end: suite green offline + live (`HARNESS_LIVE=1 HARNESS_LIVE_NET=1 HARNESS_MAILTO=<real>`), and the §10 acceptance greps return only judged-acceptable hits.

## File Structure

No new modules. Touched: `core/harness_core/*.py` (constants, parsers, render, lints, verbs), `core/harness_core/templates/**` (vault tree, note templates, AGENTS.md, pre-commit, CI), `core/tests/**`, `hooks/*.py`, `skills/*` (directory renames + SKILL.md bodies), `docs/specs/2026-08-16-foundation-spec.md`, `docs/plans/2026-08-17-plan-c-scaffold-enforcement.md` (alignment only), `README.md`, `docs/terminology.md` (Task 8 restructure).

---

### Task 1: Paths, folders, and type values

**Files:**
- Modify: `core/harness_core/scaffold.py` (`VAULT_DIRS`), `core/harness_core/notes.py` (`note_path` unaffected — literatures stays), `core/harness_core/inbox.py` (`INBOX_PATH`), `core/harness_core/lints.py` (folder globs), `core/harness_core/__main__.py` (folder walks, publish-flag field), `core/harness_core/templates/vault/**` (directory names, AGENTS.md, note templates), `hooks/posttooluse_lint.py` + `hooks/stop_publish_gate.py` (vault walks, flag field), all touched tests + `conftest.py` fixtures.

**Interfaces:**
- Consumes: §10 manifest path/type pairs.
- Produces (later tasks rely on these exact strings): folders `inbox/ literatures/ synthesis/ log/ projects/ x/`; `INBOX_PATH = "inbox/review-queue.md"`; type values `literature | synthesis | project | daily`; daily log files `log/YYYY-MM-DD.md`; publish flag field `"project"`; synthesis index `synthesis/index.md`.

- [ ] **Step 1: Discover every occurrence (judged)**

Run:
```bash
grep -rnE '"\+"|atlas|calendar|efforts|"topic"|"effort"' core/harness_core core/tests hooks skills --include='*.py' --include='*.md' --include='*.json' | grep -v '\.venv'
```
Classify each hit: rename (manifest pair) / prose-sense keep / protected history. List the classification in the task report.

- [ ] **Step 2: Update tests first to the new vocabulary**

Apply the §10 path/type pairs across `core/tests/` (fixtures build `inbox/ synthesis/ log/ projects/`; assertions expect `type: "synthesis"` etc.). Include `conftest.py`'s `VAULT_DIRS`-mirroring fixture and the `fixture_vault` note contents.

- [ ] **Step 3: Run to verify the suite fails against old code**

Run: `python -m pytest tests -q`
Expected: FAIL — fixtures now build the new tree; production constants still build the old one.

- [ ] **Step 4: Apply the same pairs to production code and templates**

`VAULT_DIRS = ["inbox", "literatures", "synthesis", "log", "projects", "x/templates", "x/bases"]`; `INBOX_PATH = "inbox/review-queue.md"`; every folder glob in lints/verbs/hooks; template directory renames (`templates/vault/synthesis/index.md`, `.keep` set per scaffold's list — now `literatures`, `log`, `projects`); template frontmatter `type: "synthesis"` / `type: "project"`; AGENTS.md template text (folder mentions + `inbox/review-queue.md`); publish flag field `"project"` in gate + its tests.

- [ ] **Step 5: Run to verify green, judged-grep, commit**

Run: `python -m pytest tests -q` — Expected: all PASS.
Run: `grep -rnE '"\+"|atlas|calendar/|efforts|"topic"|"effort"' core hooks skills --include='*.py' | grep -v '\.venv'` — Expected: no rename-class hits.

```bash
cd "$(git rev-parse --show-toplevel)"
git add core hooks skills && git commit -m "rename: vault paths and type values per terminology wave (synthesis/inbox/log/projects)"
```

---

### Task 2: Frontmatter keys and values

**Files:**
- Modify: `core/harness_core/notes.py` (`MANAGED_FIELDS`, render, day-one preservation), `core/harness_core/events.py` (tier applicability reads `doi` — unaffected; verify), `core/harness_core/lints.py` (source-status strings), `core/harness_core/checks.py` + `__main__.py` (`accessed`, `fixity-sha256`, status values), templates, tests.

**Interfaces:**
- Produces: frontmatter keys `accessed`, `fixity-sha256`; source status values `unscreened | included | excluded | superseded`; project status `draft | parked | published | corrected | withdrawn`.

- [ ] **Step 1: Tests first** — apply pairs `retrieved→accessed`, `attachment-sha256→fixity-sha256`, `unreviewed→unscreened`, `active→included`, `rejected→excluded`, `drafting→draft` across `core/tests/` (fixtures, assertions, template tests).
- [ ] **Step 2: Verify red** — `python -m pytest tests -q` — Expected: FAIL.
- [ ] **Step 3: Apply to production** — same pairs in `notes.py` (incl. the day-one-preservation lookup key and `MANAGED_FIELDS`), ack-scope/`_target_hash` reads of the fixity list, `lint_source_status` status set `{"excluded", "superseded"}`... **judged**: the lint's trigger set was `{rejected, superseded}` → now `{excluded, superseded}`; templates (`status: "unscreened"`, `status: "draft"`).
- [ ] **Step 4: Verify green** — all PASS.
- [ ] **Step 5: Commit** — `git add core && git commit -m "rename: frontmatter keys/values (accessed, fixity-sha256, PRISMA screening states, draft)"`

---

### Task 3: Inline fields and the claim-link identifier

**Files:**
- Modify: `core/harness_core/claims.py` (field names in docs; `claim_address`→`claim_link`), `core/harness_core/__main__.py` (stamp/clear `[failed-verification::]`), `core/harness_core/notes.py`/`canonical_content` (marker name in the hash-substantive set), `core/harness_core/lints.py` (deprecation-record check field list unchanged; contested-set reads `[disputes::]`/`[supports::]`), `core/harness_core/quotes.py`/`events.py` (claim_link callers), fixtures/tests.

**Interfaces:**
- Produces: inline fields `[supports::]`, `[disputes::]`, `[failed-verification:: <check>/<date>]`; function `claim_link(citekey, claim_id) -> str` (same behavior as the old `claim_address`).

- [ ] **Step 1: Tests first** — pairs `supported-by→supports`, `contested-by→disputes`, `verify-failed→failed-verification`, `claim_address→claim_link` across tests and fixture note bodies.
- [ ] **Step 2: Verify red.**
- [ ] **Step 3: Apply to production** — parser field reads, stamp format string, clear regex, canonical_content's marker-name reference (rulings 9/11: `failed-verification` markers stay hash-substantive), contested-set builder (`c.fields.get("disputes")` / `supports`), rename `claim_address` → `claim_link` everywhere (grep callers: quotes, events, lints, __main__).
- [ ] **Step 4: Verify green.**
- [ ] **Step 5: Commit** — `git add core && git commit -m "rename: inline fields to CiTO/Wikipedia anchors (supports, disputes, failed-verification); claim_link"`

---

### Task 4: Inversion additions (stale_after, generated, description, synthesis lifecycle)

**Files:**
- Modify: `core/harness_core/notes.py` (render: `generated` on machine-written notes), `core/harness_core/templates/vault/x/templates/synthesis.md` (lifecycle frontmatter), `core/harness_core/frontmatter.py` (verify inline-dict support covers `generated` — it shipped for `verified`), spec `docs/specs/2026-08-16-foundation-spec.md` §3/§5, tests.

**Interfaces:**
- Produces: literature/synthesis machine-written notes carry `generated: [{by, at}]`-compatible field `generated` as a single inline dict `{by: "...", at: "..."}` (OKF shape); optional keys `stale_after`, `description` are **pass-through-preserved** (no writer yet — they are user/OKF-tool supplied; the renderer's unowned-field pass-through already keeps them — add regression test); synthesis template frontmatter becomes:

```markdown
---
title: "{{TITLE}}"
type: "synthesis"
status: "draft"
generated: {by: "{{ACTOR}}", at: "{{TODAY}}"}
---
```

(`growth`/`planted`/`last-tended` are gone — superseded by the inversion ruling.)

- [ ] **Step 1: Write failing tests**

```python
# append to core/tests/test_notes.py
def test_generated_field_written_and_updated():
    v1 = notes.render_note(ITEM, ["aa11"], [], existing=None, retrieved="2026-08-20")
    data, _ = frontmatter.parse(v1)
    assert data["generated"]["by"].startswith("harness_core/")
    assert data["generated"]["at"] == "2026-08-20"


def test_stale_after_and_description_pass_through():
    v1 = notes.render_note(ITEM, ["aa11"], [], existing=None, retrieved="2026-08-20")
    data, body = frontmatter.parse(v1)
    data["stale_after"] = "2027-01-01"
    data["description"] = "Key mortality study"
    edited = frontmatter.serialize(data) + body
    v2 = notes.render_note(ITEM, ["aa11"], [], existing=edited, retrieved="2026-08-21")
    kept, _ = frontmatter.parse(v2)
    assert kept["stale_after"] == "2027-01-01"
    assert kept["description"] == "Key mortality study"
```

Plus a template test asserting the synthesis template carries `status: "draft"` + `generated` and no `growth`.

(Adapt `render_note`'s signature/param names to HEAD — the `retrieved` param was renamed in Task 2; if HEAD names it `accessed`, use that.)

- [ ] **Step 2: Verify red.**
- [ ] **Step 3: Implement** — `render_note` writes `generated: {by: AGENT_ACTOR, at: <today>}` as a managed field (updated each render; `MANAGED_FIELDS` gains `generated`); frontmatter serializer: verify single inline-dict values serialize/parse (extend `_emit_scalar`/`_parse_item` per HEAD shape if list-only today — smallest change that round-trips `{by, at}`); rewrite the synthesis template; update spec §3 (synthesis-page bullet: lifecycle replaces maturity) and §5 (add `generated`, `stale_after`, `description` to the frontmatter table; note pass-through ownership).
- [ ] **Step 4: Verify green.**
- [ ] **Step 5: Commit** — `git add core docs/specs && git commit -m "feat: inversion additions — generated field, stale_after/description pass-through, OKF lifecycle on synthesis pages"`

---

### Task 5: OKF conformance artifacts

**Files:**
- Create: `core/harness_core/templates/vault/index.md`, `core/harness_core/okf.py`
- Modify: `core/harness_core/scaffold.py` (scaffold copies index.md; doctor gains an `okf` probe), `core/harness_core/templates/vault/AGENTS.md` (frontmatter added), review-queue creation (typed frontmatter), `core/harness_core/__main__.py` (log.md regeneration invoked by import/verify), spec §2 cross-check, tests: `core/tests/test_okf.py`.

**Interfaces:**
- Produces:
  - `templates/vault/index.md`:

```markdown
---
type: "index"
okf_version: "0.2"
---
# Vault index

- [[literatures/]] — evidence layer: citekey-keyed source notes
- [[synthesis/]] — synthesis pages (see [[synthesis/index]])
- [[projects/]] — manuscripts and deliverables
- [[log/]] — daily activity log (summary: [[log]])
- [[inbox/]] — fleeting notes and the review queue
```

  - Review queue created with frontmatter `---\ntype: "review-queue"\n---\n` (inbox parser skips frontmatter — extend `inbox.load` to tolerate/skip a leading frontmatter block; regression test).
  - AGENTS.md template gains `---\ntype: "guide"\n---\n` at top.
  - `okf.regenerate_log(vault_root, tail_entries: int = 20) -> str` — writes root `log.md`: frontmatter `type: "log"`, then the last `tail_entries` lines across `log/*.md` (chronological), then links to each day file. Single writer; called from `import-note` and `verify` after their log appends.
  - Doctor probe `okf` (warn-class): every machine-written `.md` parses with non-empty `type`; root `index.md` has `okf_version`; `log.md` exists when any day file does.

- [ ] **Step 1: Write failing tests**

```python
# core/tests/test_okf.py
from harness_core import frontmatter, okf, scaffold


def test_scaffold_ships_okf_artifacts(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    idx, _ = frontmatter.parse((tmp_path / "index.md").read_text())
    assert idx["okf_version"] == "0.2" and idx["type"] == "index"
    rq, _ = frontmatter.parse((tmp_path / "inbox" / "review-queue.md").read_text())
    assert rq["type"] == "review-queue"
    ag, _ = frontmatter.parse((tmp_path / "AGENTS.md").read_text())
    assert ag["type"] == "guide"


def test_regenerate_log_tail(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "log" / "2026-08-19.md").write_text("- 09:00 human:eran — a\n")
    (tmp_path / "log" / "2026-08-20.md").write_text("- 10:00 human:eran — b\n")
    okf.regenerate_log(tmp_path, tail_entries=1)
    text = (tmp_path / "log.md").read_text()
    data, body = frontmatter.parse(text)
    assert data["type"] == "log"
    assert "— b" in body and "— a" not in body
    assert "[[log/2026-08-19]]" in body and "[[log/2026-08-20]]" in body


def test_inbox_load_tolerates_frontmatter(fixture_vault):
    from harness_core import Result, inbox
    p = fixture_vault / "inbox" / "review-queue.md"
    p.write_text('---\ntype: "review-queue"\n---\n' + p.read_text())
    inbox.append_entry(fixture_vault, "doi", "x", Result.UNMATCHED, "mismatch — t",
                       date="2026-08-20")
    assert inbox.load(fixture_vault)[-1].check == "doi"


def test_doctor_okf_probe(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    probes = {p[0] for p in scaffold.doctor(tmp_path, client=None, network=False)}
    assert "okf" in probes
```

(Adapt the doctor call signature to HEAD — network/client params per as-built.)

- [ ] **Step 2: Verify red.**
- [ ] **Step 3: Implement** — template + `okf.py` (~40 lines) + scaffold/doctor/inbox changes per Produces.
- [ ] **Step 4: Verify green.**
- [ ] **Step 5: Commit** — `git add core && git commit -m "feat: OKF conformance artifacts — root index.md/log.md, typed machine files, okf doctor probe"`

---

### Task 6: Skill renames

**Files:**
- Rename: `skills/vault-setup/` → `skills/setup-vault/` (and any `find-papers`/`atlas-conventions` skill dirs existing at HEAD)
- Modify: SKILL.md frontmatter `name:` fields, body references, `PROVISION_COMPANIONS`-adjacent prose, AGENTS.md template skill mentions (`/knowledge-harness:setup-vault`, `…:find-sources`, `…:synthesis-conventions`), `core/tests/test_skill_files.py`.

- [ ] **Step 1: Tests first** — update `test_skill_files.py` paths + `name: setup-vault` assertions; add assertions that no SKILL.md carries an old name.
- [ ] **Step 2: Verify red.** — old paths still present.
- [ ] **Step 3: `git mv` the skill directories; update frontmatter + bodies + AGENTS.md template.** Only rename skill dirs that exist at HEAD (Plan D's unbuilt skills are authored later with the ruled names — no stubs).
- [ ] **Step 4: Verify green.**
- [ ] **Step 5: Commit** — `git add -A skills core && git commit -m "rename: skills to ruled names (setup-vault, find-sources, synthesis-conventions)"`

---

### Task 7: Spec + active-plan alignment and full acceptance

**Files:**
- Modify: `docs/specs/2026-08-16-foundation-spec.md` (§3 tree, §5 schema table, §6 mentions, §7 skill list, §9 drills — every ruled name), `docs/plans/2026-08-17-plan-c-scaffold-enforcement.md` (alignment to its as-built implementation), `README.md`.

- [ ] **Step 1: Judged grep over living docs**

Run: `grep -nE 'atlas|calendar/|efforts|retrieved|attachment-sha256|verify-failed|supported-by|contested-by|unreviewed|drafting|vault-setup|find-papers|\+/review-queue' docs/specs/*.md docs/plans/2026-08-17-plan-c-scaffold-enforcement.md README.md`
Classify hits; apply ruled pairs to the rename class only (spec prose keeps e.g. "PARA sliver" history mentions verbatim where they describe rationale, not names).

- [ ] **Step 2: Full-suite + acceptance greps**

Run: `cd core && source .venv/bin/activate && HARNESS_LIVE=1 HARNESS_LIVE_NET=1 HARNESS_MAILTO=<real address> python -m pytest tests -q`
Expected: all PASS.
Run the §10 acceptance grep (item 2) over `core/ hooks/ skills/ docs/specs/ README.md` — Expected: only judged-acceptable hits, each named in the task report.

- [ ] **Step 3: Commit** — `git add docs README.md && git commit -m "docs: spec and active plan aligned to the terminology wave"`

---

### Task 8: `docs/terminology.md` becomes reference-only + root `CONTEXT.md`

**Files:**
- Modify: `docs/terminology.md` (full restructure)
- Create: `CONTEXT.md` (repo root — the meaning layer, per the domain-modeling CONTEXT format: is-definitions + _Avoid_ lists, zero implementation detail)

The working package is executed; what remains must be **all and only what future readers need** (the ADR standard applied to the reference). Restructure to exactly five sections — everything else is deleted (git history preserves deliberation):

1. **Title + preamble**: "Terminology reference" — states it is the naming authority; decisions carry inline dates; deliberation lives in git history of this file.
2. **Cost model** (§1 verbatim, including the decisions-not-just-names rule).
3. **Precedence order** (§2 tiers + tie-breakers + domain-authority note — WITHOUT the "Inversion deltas" subsection: its adoptions/deviations merge into the tables below).
4. **Adoptions and deviations** — two tables, post-wave truth: adoptions gain the inversion rows (`stale_after`, `generated`, `description`, synthesis lifecycle, actor convention, verified shape, tier names, reserved files) and the CiTO stance fields (`supports`/`disputes` — moved FROM deviations); deviations = the surviving class-forced rows only, updated (the ⚠ `retrieved` row closes — `accessed` shipped; per-claim attribution, `sources`/`resource`, untyped lineage, screening states, project lifecycle, `source`-vs-venue, Crossref taxonomy, `superseded`).
5. **Current inventory** — §6's seven tables with **new names, final A/S statuses per §8's promotion shortlist, and anchor column reduced to the governing anchor only** (candidate lists deleted — decided). Plus §5 standing rules (the naming-pass bullet REWRITTEN: "The naming pass completed 2026-08-20; the §9-slice gate is cleared. New terms walk the tiers; placeholder status no longer exists — every term is A, S, or D.").

**Deleted entirely**: §7 decision order, §8 promotion analysis, §9 proposal sheet, §10 manifest (all executed; recoverable from git history).

- [ ] **Step 1: Write the restructured document** (single Write; content assembled per the five sections above from the post-wave state).

- [ ] **Step 1b: Write root `CONTEXT.md`** — the glossary derived from the reference. Canonical content (adapt names to post-wave HEAD truth; definitions say what a thing IS, never how it is implemented):

```markdown
# knowledge-harness

Trust-first academic research on a personal knowledge vault: every claim traceable to a real source, verified by mechanical checks. This glossary is the meaning layer; naming governance (why these words) lives in docs/terminology.md.

## Vault

**Vault**: A private git repository of markdown notes — the researcher's durable knowledge store, structured as an OKF bundle.
_Avoid_: knowledge base, second brain

**Evidence layer**: The vault's machine-projected record of admitted sources (`literatures/`); never free-written.
_Avoid_: sources folder, references layer

**Synthesis layer**: The LLM-maintained topic pages (`synthesis/`) that arrange claims across sources; freely rewritable because it asserts arrangement, not evidence.
_Avoid_: atlas, wiki, topic pages

**Literature note**: The vault projection of one Zotero item, filename = citekey; a managed region above free prose.
_Avoid_: source note, paper note, reference note

**Synthesis note**: One page of the synthesis layer, carrying block-anchored claims with stance links.
_Avoid_: topic page (collides with OpenAlex topics), evergreen note, concept page

**Project**: A manuscript or deliverable in progress (`projects/<name>/`), with a publication lifecycle.
_Avoid_: effort, draft folder

**Inbox**: Fleeting captures and the review queue (`inbox/`); never an admission path for citable sources.
_Avoid_: `+`, capture folder

**Log**: The append-only per-day activity record (`log/`), summarized in root `log.md`.
_Avoid_: calendar, journal, daily notes folder

**Managed region**: The bridge-regenerated span of a literature note between `%%hk-managed%%` markers; never hand-edited.
_Avoid_: generated section, machine block

## Evidence and claims

**Item**: A bibliographic record in Zotero/CSL terms — the thing a citekey names.
_Avoid_: work (OpenAlex sense), paper (narrower than the corpus)

**Source**: The cited document itself, in the scholarly sense (primary/secondary source).
_Avoid_: using "source" for a journal or repository — that is a **venue**

**Venue**: The journal, repository, or outlet an item appeared in.
_Avoid_: OpenAlex's "source" sense in our prose

**Citekey**: The stable, human-readable key (Better BibTeX) joining prose citations, filenames, and the bibliography.
_Avoid_: reference ID, bibkey

**Claim**: One assertion carried by a note line, tagged with its evidence boundary and anchored for linking.
_Avoid_: statement, fact

**Evidence-boundary tag**: The per-claim marker of epistemic status — quote, paraphrase, inference, or open-question.
_Avoid_: claim type, epistemic label

**Claim link**: The global address of a claim: `citekey#^claim-id` (an Obsidian block link).
_Avoid_: claim address, claim ID (that is only the anchor fragment)

**Stance link**: A typed claim-to-claim relation — `supports` or `disputes` (CiTO senses).
_Avoid_: supported-by/contested-by (old names), related links

**Admission**: The human act of accepting a source into Zotero — the only way anything becomes citable.
_Avoid_: import (that is the projection step that follows), ingestion

**Screening state**: A literature note's PRISMA-style status: unscreened, included, excluded, or superseded.
_Avoid_: unreviewed/active/rejected (old values), review status

## Verification

**Check**: One mechanical verification (citekey exists, DOI resolves, quote matches, update-notice scan, …).
_Avoid_: test, validation

**Four-state result**: A check's outcome: MATCHED, UNMATCHED, UNREACHABLE (could not run — never guilt), or SKIPPED (does not apply — automatic only).
_Avoid_: pass/fail, pytest vocabulary in vault prose

**Verified event**: The record `{by, at, check}` a passing check appends to a note; only MATCHED mints one.
_Avoid_: verification log entry, audit record

**Trust tier**: A note's derived standing: unverified → machine-confirmed → human-reviewed (cumulative).
_Avoid_: confidence level (that is a per-claim field), quality score

**Review inbox**: The append-only findings file (`inbox/review-queue.md`) every warn, hold, and alert writes to; drained at project orientation.
_Avoid_: issue list, warning log

**Acknowledgment**: A human's standing, hash-scoped acceptance of a finding — the only bypass any closed check has.
_Avoid_: dismissal, override (an ack keeps the record; it never deletes)

**Publish gate**: The armed, fail-closed verification boundary a project crosses at publish; inert unless armed.
_Avoid_: release check, CI gate (CI is the async auditor, not the gate)

**Update notice**: A registry's post-publication signal about an item (retraction, correction, expression of concern, …), recorded bi-temporally.
_Avoid_: retraction flag (one class of notice, not the concept)

## Process

**Information flow**: How a source is added, cataloged, and linked — continuous, project-independent.

**Project flow**: How a question becomes a defensible draft — framing, gap analysis, acquisition, drafting, verification, publish.

**Doctor**: The repair-capable diagnostic pass over the vault's substrate (Zotero, exports, tree, conformance).
_Avoid_: health check, setup validator
```

(Every `_Avoid_` entry derives from the reference's deviations and old names; anything the wave renames must appear here under its NEW name with the old name in _Avoid_.)
- [ ] **Step 2: Verify internal consistency** — every name in CONTEXT.md and the reference matches a grep of the post-wave code (`grep -c` spot-checks for `synthesis`, `accessed`, `fixity-sha256`, `supports`, `unscreened` in `core/`); no section references §7–§10 or "proposal"/"pending".
- [ ] **Step 3: Commit** — `git add docs/terminology.md CONTEXT.md && git commit -m "docs: terminology reference + root CONTEXT.md glossary (meaning layer)"`

---

### Task 9: Merge

- [ ] Full suite green (offline + live), acceptance greps clean, then `superpowers:finishing-a-development-branch` for `build/terminology-wave`.

---

## Self-Review (completed at authoring)

**Manifest coverage:** §10 path/type pairs → T1; frontmatter pairs → T2; inline-field pairs + claim_link → T3; inversion additions → T4; OKF artifacts → T5; skill renames → T6; spec/plan/README alignment + acceptance → T7; the §10 "statuses flip / deviation upgrade / defect closes" bookkeeping → T8 (as the reference rewrite); root CONTEXT.md glossary (meaning layer, format-conformant, _Avoid_ lists from deviations) → T8 Step 1b; post-wave gate-clear declared by T8's standing-rules rewrite. Nothing in §10 lacks a task.
**Placeholders:** none — where HEAD shapes are unknown (Plan C in flight), tasks give exact discovery commands, exact target strings, and the HEAD-governs escalation rule instead of invented code; all genuinely new code (T4 tests, T5 module/tests/templates) is written out.
**Type consistency:** `INBOX_PATH`, type values, `claim_link`, `fixity-sha256`, `accessed`, `generated` shape, `okf.regenerate_log` signature used identically across tasks; T8's reference tables are defined as the post-wave truth of T1–T7's strings.
