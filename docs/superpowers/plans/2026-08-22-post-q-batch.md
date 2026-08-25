# Pre-Slice Batch — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The single dispatch between Plan Q's merge and slice Phase 2 — instrument freeze for §9: the `project`→`project-flow` rename, the routing index, nine skill-prose corrections from the audits, and four code fixes (SKIPPED counting, tier-2 citekeys, free-region refusal, duplicate-anchor assert).

**Architecture:** One branch, tasks ordered as numbered — the rename precedes the index so the seven entry names are written once, correctly. Skill-prose tasks are edit + test-pin + judged-grep cycles; code tasks are TDD. (The polish pass + four-state dedup stay in their own POST-slice plan: they exist to be informed by slice usage.)

**Tech Stack:** Existing pinned toolchain; no new dependencies.

## Global Constraints

- Read this plan from origin/main at each task start (`git show origin/main:docs/superpowers/plans/2026-08-22-post-q-batch.md`).
- Worktree via `superpowers:using-git-worktrees`, branch `fix/pre-slice-batch`.
- Every test Run begins `source .venv/bin/activate` (`pip install -e ".[dev]" -q` if imports fail).
- Whole-file test pins (`tests/test_skill_files.py`-style) update in the SAME commit as the prose they pin.
- Content sources referenced by task: `research/validation-slice/2026-08-22-skills-layer-audit.md` (the C-findings and ecosystem steals), `research/validation-slice/2026-08-22-references-cross-read.md` (items 11–12's itemized annotations). Copy their itemized content verbatim — the triage there is the decided set.
- Suite green offline at each task's end. Commit messages conventional; one commit per task.

______________________________________________________________________

### Task 1: Rename `project` → `project-flow` (item 1)

Ruled 2026-08-22: class-4 collision with CONTEXT.md's *Project* dissolved by the other governed noun for the process, *project flow* (governed at `docs/terminology.md` §4.3; its CONTEXT.md entry was cut 2026-08-23 as a process description rather than an is-definition — the noun stands, its home moved). Entry family becomes uniformly two-part.

**Files:** Move: `skills/project/` → `skills/project-flow/`. Modify: `docs/terminology.md` §4.3 skills row; routing tables in `skills/find-sources/SKILL.md` and `skills/import-source/SKILL.md`; the skill's content test in `tests/`.

- [x] **Step 1:** `git mv skills/project skills/project-flow`; update `name:` in its SKILL.md frontmatter to `project-flow`.
- [x] **Step 2:** Update terminology §4.3's skills row and both routing tables (grep `skills/ -rn "\`project\`"\` and judge each hit — routing rows change; prose about "a project" (the noun) does not).
- [x] **Step 3:** Update the content test that names the skill (locate via `grep -rn "project" tests/test_skill_contracts.py tests/test_skill_files.py`); run it: PASS.
- [x] **Step 4:** Judged grep for retired references: `grep -rn "skills/project/\|Skill(project)\|\`project\` skill" --include="\*.md" .\` — every hit either updated or judged non-referential (record the judgment list in the commit body).
- [x] **Step 5:** Full offline suite. Commit `refactor: rename project skill to project-flow`.

### Task 2: C-7 routing index into the vault AGENTS.md template (item 2)

**Files:** Modify: `knowledge_harness/templates/vault/AGENTS.md`; its whole-file test pin.

- [x] **Step 1:** Add the index: the seven entry names (post-rename) + one clause each — source each clause from the skill's own description line (compress, don't invent). `tests/test_skill_contracts.py:153`'s self-validation must pass (every cited name exists as a shipped skill).
- [x] **Step 2:** Update the template's whole-file pin in the same commit; full suite; commit `feat: vault AGENTS.md routing index (C-7)`.

### Task 2b: Root index embeds the Bases (decided 2026-08-24 — dashboards surface at vault-open; the `.base` files stay filed as tool artifacts)

**Files:** Modify: `knowledge_harness/templates/vault/index.md`; its whole-file pin. **Ordering:** independent — run anywhere in Part 1; if Task 2's template work already passed, this is its own commit.

- [x] **Step 1:** Add to the index template, under its folder links: `![[system/bases/trust-tier.base]]` and `![[system/bases/open-questions.base]]` with a one-line lead-in each (compress from the Base's own purpose; don't invent). Rationale in place: the Bases are the researcher's dashboards (§9 derives trust tiers in one), but `.base` is Obsidian-only, so the files stay in `system/` per vault-outlives-harness — embedding gives one-click access without moving a tool artifact into the knowledge tree.
- [x] **Step 2:** Pin updated same commit; suite; commit `feat: vault index embeds the trust-tier and open-questions Bases`.

### Task 2c: Vault AGENTS.md integrity preamble (decided 2026-08-24 — the oblivious-agent defense)

**Files:** Modify: `knowledge_harness/templates/vault/AGENTS.md`; its whole-file pin. **Ordering:** independent — its own commit if Task 2's template work already passed.

- [x] **Step 1:** The template OPENS with a two-sentence integrity preamble, before the routing index — for the agent that reads nothing else: *"This is a knowledge-harness vault. `literatures/`, `log/`, root `log.md`, and `inbox/review-queue.md` are machine-written — the CLI writes them; hand edits are warned in session and caught at commit."* (Adjust the surface list to what the template already names; don't restate the routing index.)
- [x] **Step 2:** Pin same commit; suite; commit `feat: vault AGENTS.md opens with the integrity preamble`. Item 15's live-vault application now carries this too.

### Task 2d: Formatter ignore files + invocation-scope line (audit findings 1 and 12)

**Files:** Modify: `knowledge_harness/scaffold.py` + vault templates (new `.prettierignore`, `.markdownlintignore`, `.editorconfig` covering `literatures/`, `log/`, `inbox/review-queue.md`, `system/bibliography.json`); `knowledge_harness/templates/vault/AGENTS.md`; pins.

- [x] **Step 1:** Scaffold ships the three ignore files — formatters obey config, not paragraphs. The AGENTS.md formatter paragraph (which says of itself "it is not what enforces them") shrinks to one line naming the ignore files.
- [x] **Step 2 (finding 12):** Scope AGENTS.md's "prefer the knowledge-harness skills" line to the two model-invocable guards — seven of nine skills are user-gated by deliberate design; the line must not read as steering all nine. Do NOT flip any `disable-model-invocation` flag.
- [x] **Step 3:** Pins; suite; commit `feat: formatter ignores ship with the vault; AGENTS.md scope line corrected`.

### Task 2e: Form-gate coherence (measured audit 2026-08-24 — root cause is the recorded imperative-path-list debt, now with measured cost)

**Files:** Modify: `pyproject.toml` (comments), `.pre-commit-config.yaml`, `knowledge_harness/templates/vault/**/*.md` + pins.

- [x] **Step 1 (vendored exclusion made explicit — REVERSES the audit's gate-them recommendation):** `skills/find-sources/scripts/*.py` stay ungated BY the vendor rule (frozen fork; re-vendor to update; our formatters/fixers would create vendor drift). Make it explicit: one comment at ruff's path list naming the exclusion and its reason. The real finding there — `jats_to_text.py:291` passing `Element | None` into `collect_sections` — goes to the vendor channel: a ready-to-file upstream note in the K-Dense report queue, fix lands at next re-vendor, never by hand.
- [x] **Step 2 (render-contract event, NOT a path-list edit):** add `knowledge_harness/templates/vault` to mdformat's paths and canonicalize the 11 template files — five change. This IS a render change by the repo's own doctrine (canonical template form leaks into rendered notes): its own commit, template pins updated, and the note that existing vaults see managed-region diffs on next refresh (legitimate `stale` outcomes, not defects). The RENDER-CONTRACT pin's justification becomes enforced on the files it names.
- [x] **Step 3 (hook stays uninstalled — ruled):** pre-commit's stash/restore plus whole-tree `always_run` hooks is exactly the interference the pathspec rule guards against in a shared checkout. Fix the header sentence to the truth: "when typed, and in CI"; add one line naming the practice that replaces it (run the form owner directly on touched files before committing — `pre-commit run` also stashes and is NOT the safe form here).
- [x] **Step 4 (small trues):** document yamlfix's self-exclusion in one comment (readability of the hand-wrapped entries — a choice, now stated); drop the dead `analysis` pathspec from the record-immutability hook; make that hook fail loud on git errors (it currently swallows any `git diff` failure into an empty `touched` and passes — add explicit failure handling inside the `bash -c`); add an mdformat upgrade-protocol comment on its pin, matching ruff's: a canonical-form-changing upgrade rewrites append-only paths, so it lands as a recorded churn commit through the bypass channel (the commit message IS the record — blame-ignore-revs was measured useless against mdformat churn and deleted 2026-08-24).
- [x] **Step 5:** Suite + `pre-commit run --all-files` green; commit `fix: form gates match their own claims — explicit vendor exclusion, templates canonicalized, hook truths`.

### Task 3: verify-citations de-enumeration + the enumeration checker (items 3–4)

**Files:** Modify: `skills/verify-citations/SKILL.md`; `tests/test_skill_contracts.py`.

- [x] **Step 1 (C-1):** Replace the check-id enumeration with the canonical obsidian-cli form — the replacement sentence: *"Run the CLI; its output is always up to date."* Teach the four states, not the fourteen ids (the four-state table stays; the id list goes).
- [x] **Step 2 (C-2):** Correct the registry-scope sentence: TWO registry codes are out of scope, not one (the audit's C-2 card names them — copy from it), and pin with a test.
- [x] **Step 3 (the enumeration checker):** Generalize the `test_skill_contracts.py:133` instrument: every check id any SKILL.md enumerates must be one `verify` can emit. Write it as a parametrized sweep over `skills/*/SKILL.md` extracting backtick-quoted check ids against the CLI's emitted set (source the canonical set from `knowledge_harness` code, not a hand list).
- [x] **Step 4:** Full suite; commit `fix: verify-citations defers to CLI output; enumeration checker guards all skills`.

### Task 4: find-sources corrections + cross-read wiring (items 5, 7, 11, 12)

**Files:** Modify: `skills/find-sources/SKILL.md` (+ its `references/` where the cross-read says so); test pins.

- [x] **Step 1 (C-3 + item 11 fold):** Credential counts align to `redact_url` — the SKILL.md says "several" and defers to `redact_url` as the authority (3 query-string-auth APIs; 6 redacted params live in code, not prose). Mailto: SKILL.md states it is sourced from harness config and that vendored scripts don't read it.
- [x] **Step 2 (C-5):** One vendoring-note line: upstream prose describes upstream's corpus.
- [x] **Step 3 (item 12):** One vendoring-note section carrying the six upstream-fact annotations — copy verbatim from the cross-read report's triage (research/validation-slice/2026-08-22-references-cross-read.md). Add the routing guards: no single-DOI lookups via paginate; the openalex row points at `openalex_abstract.py`; `OPENALEX_API_KEY` env caution. Add the XML annotation (ruled 2026-08-24): `arxiv_atom.py`/`jats_to_text.py` parse network XML via stdlib ElementTree by upstream's choice — not XXE (no EXTERNAL entity expansion — internal entities DO expand, probe-verified 2026-08-24, which is exactly the class the next clause hedges); residual expansion-DoS rides the runtime's libexpat; kept frozen per the vendor rule, noted in the K-Dense upstream queue beside the jats arg-type finding.
- [x] **Step 4:** Pins updated same commit; full suite; commit `fix: find-sources credential/vendoring corrections + cross-read wiring`.

### Task 5: setup-vault C-6 (item 6)

**Files:** Modify: `skills/setup-vault/SKILL.md`; test pins.

- [x] **Step 1:** Drop the 14-path inventory; keep the six test-pinned paths as an honesty rule, not an inventory (one sentence: the pinned six are the contract; the CLI's scaffold output is the full list).
- [x] **Step 2:** Pins updated; suite; commit `fix: setup-vault paths are a contract, not an inventory (C-6)`.

### Task 6: import-source references split (item 8)

**Files:** Create: `skills/import-source/references/` (content moved from SKILL.md §7–9). Modify: `skills/import-source/SKILL.md` (pointer table, find-sources shape).

- [x] **Step 1:** Move §7 (refresh), §8 (batch), §9 (archive) content unchanged into `references/` files; SKILL.md gets the pointer table in find-sources' shape. Content byte-preserved; tests unmoved and green.
- [x] **Step 2:** Suite; commit `refactor: import-source §7-9 to references with pointer table`.

### Task 7: Prose sweeps — leading word + prohibition cuts (items 9–10)

**Files:** Modify: the SKILL.md files the greps hit; pins.

- [x] **Step 1 (item 9):** The never-hand-write refrain's five spellings collapse to the single inline token *the CLI writes* (grep for the variants — "never hand-write", "never write by hand", etc. — one token per site, meaning preserved).
- [x] **Step 2 (item 10):** Delete two prohibitions whose recipes are already present: "not as a raw dump" (find-sources:88), "not in raw run order" (verify-citations:27).
- [x] **Step 3:** Judged grep confirms no returned prohibitions; pins; suite; commit `style: leading-word collapse + prohibition cuts`.

### Task 8: Ecosystem steals (items 13–14)

**Files:** Modify: `skills/project-flow/SKILL.md`, `skills/synthesis-conventions/SKILL.md`, `skills/import-source/SKILL.md`, `skills/factcheck-draft/SKILL.md`, `skills/publish/SKILL.md`, `skills/setup-vault/SKILL.md`; pins.

- [x] **Step 1:** Land the adopted set, each sourced from the audit §6/§7 adjudication (copy the decided phrasings): routing guard line in project-flow; compilation-value line in synthesis-conventions; partial-read honesty rule (import-source + factcheck-draft); "validates declarations, not their truth" + the why-one-pass sentence in factcheck-draft; disposition rationalization table in publish (seed rows ported from finishing-a-development-branch per audit §7); publish announces gate-armed at start; setup-vault fails closed on ambiguous vault selection.
- [x] **Step 2:** Item 14 is a no-op by design: all §6 deferred items carry their triggers in the audit doc — verify none landed here.
- [x] **Step 3:** Pins; suite; commit `feat: ecosystem-steal prose adoptions (audit §6 adopted set)`.

### Task 8b: Guard sentences from the ADR triage — LANDED 2026-08-24 (d7fa91b, author session); VERIFY ONLY

Step 1's content lives in the rewritten "The abstract said so." row (replaced, not duplicated); Step 2's inline-provenance sentence is at evidence-conventions:16. **Executor: verify both are present and land nothing — working the original steps would produce a duplicate row.** Original steps retained for the verify:

- [x] **Step 1 (from dropped 0007):** Add a rationalization-table row beside "The abstract said so.": *"I'll summarize from the abstract."* → *"A summary is written from the full text, or it says "no full text available" and stops. An abstract-derived summary states methods, conditions, and magnitudes the abstract cannot carry — fabricated facts under the source's citekey — and inherits the authors' pitch as fact. No tag repairs it."*
- [x] **Step 2 (from dropped 0009 — verify-then-add):** Check whether the claim-syntax section already forces provenance inline per claim (tag + citekey + anchor on the claim line, never frontmatter-only). If it does, add NOTHING — the rule shipped. If the never-frontmatter-only clause is absent, add its one sentence.
- [x] **Step 3:** Landed in d7fa91b with pins.

**Test-name note for Part 2:** Task 16's regression tests name the invariant they pin (e.g. `test_absence_is_not_a_pass_*`) — the dropped 0005's home is a named test, not a doc. Task 12's duplicate-anchor guard already satisfies the dropped 0008 the same way.

### Task 9: SKIPPED entries excluded from unacknowledged counts (item 16, slice finding 14)

**Files:** Modify: `knowledge_harness/inbox.py` (`summary`, ~line 710, and every drain surface that counts). Test: `tests/test_inbox.py`.

- [x] **Step 1: Failing test**

```python
def test_skipped_entries_not_counted_unacknowledged(tmp_vault):
    # queue holding ONLY SKIPPED-result entries (write via the finding writer)
    assert inbox.summary(tmp_vault)["unacknowledged"] == 0
    # mixed queue: one SKIPPED + one UNMATCHED → count == 1, oldest = the UNMATCHED's date
```

(Locate the `Finding` field carrying `result` in `inbox.py` and the writer tests' scaffolding — copy their fixture shape.)

- [x] **Step 2: Run — Expected: FAIL** (SKIPPED counts today).
- [x] **Step 3: Implement:** filter `result == SKIPPED` out of the *counting* path — in `summary()` and every drain surface's unacknowledged arithmetic (grep for `summary(` and `open_entries(` consumers; doctor's inbox probe included). Entries stay RECORDED (audit trail) and stay visible in full listings; only the unacknowledged count and oldest-age basis exclude them — does-not-apply needs no acknowledgment, and counting it manufactures rubber-stamp pressure.
- [x] **Step 4:** Full suite; commit `fix: SKIPPED findings recorded but never counted unacknowledged`.

**Task 9 addendum (2026-08-24, audit finding 10):** `summary()` also emits `oldest_age_days` (and `aging: true` past the Whittaker threshold) — the skill currently asks the agent to do date math against a clock it doesn't reliably have; the sort instruction is already mechanical. One extra assertion in Task 9's tests.

### Task 10: Two-tier citekey check (item 17, spec §4 as ruled 2026-08-22)

**Files:** Modify: `knowledge_harness/checks.py` (`check_citekeys`, ~line 131); `knowledge_harness/inbox.py` (REASON_CODES) or wherever the registry lives; `docs/terminology.md` §4.4 (new row); `skills/evidence-conventions/SKILL.md` reason-code table. Test: `tests/test_checks.py`.

**Interfaces:** `check_citekeys` signature unchanged; new reason code `not-imported`.

- [x] **Step 1: Failing tests**

```python
def test_cited_citekey_requires_literature_note(tmp_vault):
    # citekey present in bibliography, literatures/<citekey>.md absent:
    outcome = ...  # run check_citekeys on a draft citing it
    assert outcome.result is Result.UNMATCHED
    assert outcome.reason.startswith("not-imported")

def test_cited_citekey_with_note_passes(tmp_vault): ...      # MATCHED as today
def test_cited_citekey_absent_everywhere(tmp_vault): ...     # existing "mismatch — citekey not in bibliography"
```

- [x] **Step 2: Run — Expected: FAIL** (bibliography membership alone MATCHES today).
- [x] **Step 3: Implement:** in the per-citekey loop, bibliography-present + note-absent → `Result.UNMATCHED`, reason `"not-imported — cited citekey has no literature note"`. The note's OWN citekey row (note-vs-bibliography identity) keeps current semantics — scope the new rule to citations only.
- [x] **Step 4:** Register `not-imported` (distinct from `not-admitted`) in the reason-code registry, terminology §4.4, and evidence-conventions' table — same commit (dialect-surface rule).
- [x] **Step 5:** Full suite; commit `feat: tier-2 citability — cited citekeys require a literature note (not-imported)`.

### Task 11: Free-region destruction fix (item 18, audit defect 5)

**Files:** Modify: `knowledge_harness/notes.py` (`_split_free`, ~line 141; `render_note`), `knowledge_harness/__main__.py` (`cmd_import_note` catch + review record). Test: `tests/test_notes.py`, `tests/test_import_note.py`.

- [x] **Step 1: Failing tests**

```python
def test_existing_note_without_marker_refuses_render():
    existing = "---\ntype: literature\n---\nhand-written prose, no marker\n"
    with pytest.raises(notes.RenderIntegrityError):
        notes.render_note(ITEM, ..., existing=existing)

def test_import_refusal_files_review_record_and_exits_1(tmp_vault, ...):
    # cmd_import_note over a marker-less existing note → exit 1, file untouched
    # byte-for-byte, a render/UNMATCHED/schema-violation review record filed
    # (the uniform-wiring contract — same writer the finding verb uses).

def test_fresh_note_still_seeds():  # parametrize existing=None AND existing="" → SEED_FREE
    # ("" reaches the fallthrough by accident today; once it raises, the empty case
    #  must be an explicit first-branch catch or fresh renders start crashing)
```

- [x] **Step 2: Run — Expected: FAIL** (marker-less body silently replaced by `SEED_FREE` today, printed as success).
- [x] **Step 3: Implement:** `_split_free` distinguishes three cases — `existing` None/empty → `SEED_FREE` (fresh seed); marker found → preserved tail (unchanged); non-empty without marker → raise `RenderIntegrityError("existing note has no managed-close marker — refusing to overwrite the body")`. `cmd_import_note` already routes render rejections to exit 1 + the review record (verify against the import-note skill §1 table: check `render`, UNMATCHED, `schema-violation`); confirm the record actually files, don't assume.
- [x] **Step 4:** Never-delete (§5) now covers the free region — add the sentence to the spec §5 invariants line in the same commit.
- [x] **Step 5:** Full suite (the byte-exact free-region preservation test stays green); commit `fix: refuse import over a marker-less note — never reseed the free region`.

### Task 12: Duplicate-anchor render assert (item 19, claim-anchor audit)

**Files:** Modify: `knowledge_harness/notes.py` (`_assert_managed_body_parses`, ~line 260). Test: `tests/test_notes.py`.

- [x] **Step 1: Failing test** — two identical keyless annotation texts (ids derive from quote hash, truncate to 8 hex) render duplicate `^id` anchors undetected today:

```python
def test_duplicate_anchors_refuse_render():
    annotations = [KEYLESS_ANNOTATION, dict(KEYLESS_ANNOTATION)]  # identical text
    with pytest.raises(notes.RenderIntegrityError):
        notes.render_note(ITEM_WITH(annotations), ...)
```

- [x] **Step 1b: Second failing case** (added 2026-08-23, reproduced at HEAD — [issue #16](https://github.com/eranroseman/knowledge-harness/issues/16)): two keyless annotations with **empty** `annotationText` and different comments both render `^c-e3b0c442`, the truncated hash of the empty string. This is the broader case — every keyless comment-only annotation collides with every other, not just ones whose text matches — and the same uniqueness line closes it.

- [x] **Step 2: Run — Expected: FAIL** (`parsed != expected` passes when both lists carry the same duplicates).

- [x] **Step 3: Implement** — one uniqueness line in `_assert_managed_body_parses`:

```python
if len(set(expected)) != len(expected):
    raise RenderIntegrityError(f"duplicate claim anchors in render: {expected!r}")
```

- [x] **Step 4:** Full suite; commit `fix: render refuses duplicate claim anchors`.

### Task 13: Live-vault index application + acceptance (item 15)

- [x] **Step 1 (consent-gated; scope re-ruled 2026-08-24 as a CLASS, not a count):** update the live vault at `~/kh-vault` to the CURRENT template set — every file the landed template tasks produced (at this writing: AGENTS.md with routing index + integrity preamble, index.md with the Base embeds, and 2d's ignore files — the live vault is the in-use vault, exactly where an editor's trim-on-save corrupting the append-only byte contract stops being hypothetical). Enumerate the actual file list at dispatch from the landed tasks; one vault commit; **only with the author's explicit consent** (ask; never push to the vault remote without it). The open_q Bases check rides AFTER the commit as author-side verification (needs a Bases-capable Obsidian); if it needs a `.base` edit, that is a recorded finding, never this task's scope.
- [x] **Step 2 (Part 1 checkpoint):** Full suite green offline; `test_skill_contracts` green over the renamed set; judged greps re-run (retired `project` skill references; no returned prohibitions). Do NOT merge yet — Part 2 continues on the same branch; final acceptance and the merge live at Task 21.

______________________________________________________________________

______________________________________________________________________

## Part 2: Trust-core remediation (Plan V, absorbed 2026-08-22)

Closes the no-fabrication audit's remaining trust-core defects (research/validation-slice/2026-08-22-no-fabrication-audit.md defects 1-3 and 6-8, the RW arming ruling, the additive `relation` read) so slice Phases 4-6 and the gate drill run against remediated gates. Doctrine: missing input is SKIPPED or legible absence, never silence, never a synthesized value; UNMATCHED is never reduced away; trust tiers require evidence, not vacuity. No new dependencies (python-dateutil rejected under §8: the RW CSV's formats are enumerable, so a `strptime` list is the contract match). Part 1's Tasks 10-11 already carry audit defects 4-5.

### Task 14: RW date parsing + arming honesty (audit defect 1 + the arming ruling)

**Files:**

- Modify: `knowledge_harness/checks.py` (`_rw_date`, ~line 910)
- Modify: `knowledge_harness/verify.py` (RW-leg absence line, near `notice_lookup = checks.load_rw_csv(rw_csv) if rw_csv else None`, ~line 986)
- Test: `tests/test_checks.py`, `tests/test_verify.py`

**Interfaces:** `_rw_date(value) -> str | None | object` contract unchanged (ISO string, `None` for empty, `_INVALID` sentinel). No signature changes anywhere.

- [x] **Step 1: Failing test — production date formats parse**

```python
def test_rw_date_accepts_production_formats():
    assert checks._rw_date("1/2/2023 0:00") == "2023-01-02"
    assert checks._rw_date("12/31/2019") == "2019-12-31"
    assert checks._rw_date("2023-01-02") == "2023-01-02"  # ISO still accepted
    assert checks._rw_date("not a date") is checks._INVALID
    assert checks._rw_date("13/45/2023 0:00") is checks._INVALID
```

- [x] **Step 2: Run** `pytest tests/test_checks.py::test_rw_date_accepts_production_formats -v` — Expected: FAIL (first two assertions return `_INVALID` today).

- [x] **Step 3: Implement** — replace the `fromisoformat`-only body with an enumerated format loop:

```python
_RW_DATE_FORMATS = ("%m/%d/%Y %H:%M", "%m/%d/%Y")

def _rw_date(value) -> str | None | object:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if not isinstance(value, str):
        return _INVALID
    text = value.strip()
    try:
        return _date.fromisoformat(text).isoformat()
    except ValueError:
        pass
    for fmt in _RW_DATE_FORMATS:
        try:
            return _datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    return _INVALID
```

(`_datetime` = `datetime.datetime`; add the import alias beside `_date` if absent.)

- [x] **Step 4: Failing test — unarmed RW leg is legible, not silent.** The `verify` output summary must carry exactly one line when `--rw-csv` was not supplied, e.g. `update-notice: RW leg not run (no --rw-csv)`. Write the test against whatever summary surface `verify` already prints (locate the existing summary emission in `verify.py`; assert on captured stdout of a minimal vault run without `--rw-csv`). This is a stdout line, NOT a review-queue record — no new reason code, no inbox noise (the SKIPPED-counting lesson, slice finding 14).

- [x] **Step 5: Implement the one-line emission. Run both tests + full offline suite. Commit** `fix: RW date parsing accepts production formats; unarmed RW leg says so`

**Arming ruling implemented by this task (record in the commit body):** the RW leg's home is the scheduled CI lane (`templates/ci/rw-batch.yml`, already passes `--rw-csv`) and the drill runs it explicitly armed (Plan S amendment already recorded); local `verify` without the flag now states the absence. No default-on: fetching the RW CSV is a network+license act that stays deliberate.

### Task 15: Reduction must not round UNMATCHED to MATCHED (audit defect 2)

**Files:**

- Modify: `knowledge_harness/checks.py` (`reduce_update_notice_outcomes`, ~line 1024)

- Test: `tests/test_checks.py`

- [x] **Step 1: Failing test**

```python
def test_reduce_preserves_nonblocking_unmatched_over_matched():
    live = Outcome("update-notice", "10.1/x", Result.UNMATCHED,
                   "version mismatch", extra={"class": "warn", "warn_notices": []})
    rw = Outcome("update-notice", "10.1/x", Result.MATCHED,
                 "matched", extra={"warn_notices": [{"type": "correction"}]})
    reduced = checks.reduce_update_notice_outcomes(live, rw)
    assert reduced.result is Result.UNMATCHED   # ran-and-disagreed survives
    assert reduced.extra.get("warn_notices")    # RW's warns still merged
```

(Adjust constructor call shape to the real `Outcome` signature in the file — the assertion pair is the contract.)

- [x] **Step 2: Run it** — Expected: FAIL (today the fallback priority is UNREACHABLE > MATCHED > SKIPPED, so the non-blocking UNMATCHED loses to MATCHED).

- [x] **Step 3: Implement** — in the non-blocking `chosen` fallback, insert `Result.UNMATCHED` ahead of `Result.MATCHED`:

```python
for result in (Result.UNREACHABLE, Result.UNMATCHED, Result.MATCHED, Result.SKIPPED)
```

- [x] **Step 4: Sweep the consequences.** Run the full offline suite; any test that pinned the old rounding is a test asserting the defect — fix the test, and say so in the commit body per-test. Then check the event-minting path: an UNMATCHED reduction must not mint a `verified` update-notice event (read `verify.py`'s minting condition and add a regression test if none pins it).

- [x] **Step 5: Commit** `fix: update-notice reduction preserves non-blocking UNMATCHED`

### Task 16: No vacuous machine-confirmed tier (audit defect 3 + spec §86 gap; closes the DERIVATION half of [issue #17](https://github.com/eranroseman/knowledge-harness/issues/17): `human-reviewed` derives correctly given a `human:` event, pinned in this task's tests via fixture-written events (a fixture can write the event even though no production surface mints one). The MINTING half stays OPEN on #17 — deferred with a slice-Phase-5 trigger, spec §10 — so this task must NOT auto-close the issue; reference #17 in the commit with non-closing prose)

**The reason, for the test name and the docstring:** an empty applicable-check set satisfies "every applicable check passed" vacuously, and vacuous truth is not evidence. A machine tier needs at least one check that ran and passed — otherwise a note with no identifiers, no quotes, and no verified events derives the top tier, which is what it does at HEAD.

**Files:**

- Modify: `knowledge_harness/events.py` (`trust_tier`, ~line 240)

- Modify: `docs/superpowers/specs/2026-08-16-foundation-spec.md` (§5 Event-integrity paragraph)

- Test: `tests/test_events.py`

- [x] **Step 1: Failing test**

```python
def test_no_identifier_no_claims_note_is_unverified():
    text = "---\ntype: literature\ncitekey: url2024only\nurl: https://example.org\n---\nbody\n"
    assert events.trust_tier(text) == "unverified"

def test_frontmatterless_text_is_unverified():
    assert events.trust_tier("just some text\n") == "unverified"
```

- [x] **Step 2: Run** — Expected: FAIL, both return `"machine-confirmed"` today (empty applicable set, subset test vacuously true, no quote claims to block it).

- [x] **Step 3: Implement** — machine-confirmed requires evidence, not absence of counter-evidence. After the existing `machine_confirmed` computation, add the checkability floor:

```python
has_applicable = bool(_applicable_note_checks(data))
has_managed_quotes = any(
    claim.tag == "quote" and claim.in_managed and claim.claim_id
    for claim in claims_mod.parse_claims(note_text)
)
if not has_applicable and not has_managed_quotes:
    machine_confirmed = False
```

(Reuse the existing `parse_claims` iteration rather than iterating twice if straightforward — a flag set inside the current loop plus the `has_applicable` check is equivalent.)

- [x] **Step 4: Spec amendment, same commit** — §5's event-integrity paragraph gains one sentence: *"An item with no applicable note-level checks and no managed quote claims derives `unverified` — the machine tiers require at least one deterministic check to have run and matched, never vacuous satisfaction (closed 2026-08-22, audit defect 3)."*

- [x] **Step 5: Full suite; fix any test that pinned the vacuous tier (say so per-test in the commit body). Commit** `fix: trust tier requires evidence — no vacuous machine-confirmed`

### Task 17: The "unresolved" placeholder never anchors acknowledgments (audit defects, fixity pair)

**Files:**

- Modify: `knowledge_harness/__main__.py` (attachment loop, ~line 234)

- Modify: `knowledge_harness/verify.py` (`_citekey_hash` fixity adoption, ~line 209)

- Test: `tests/test_import_note.py` (or the file holding import-note frontmatter tests), `tests/test_verify.py`

- [x] **Step 1: Failing tests, both sides**

```python
def test_unresolved_attachment_omitted_from_fixity(...):
    # import with one attachment whose path resolution raises PathError
    # (monkeypatch _attachment_hash to raise) → rendered frontmatter's
    # fixity-sha256 list does NOT contain "unresolved"; the stderr warning
    # remains (already pinned elsewhere — keep that pin green).

def test_ack_hash_rejects_placeholder_fixity(...):
    # a note whose fixity-sha256 is ["unresolved"] (legacy content) →
    # _citekey_hash falls back to the managed-bytes hash, never adopts
    # the placeholder string.
```

Write these as real tests against the existing fixtures in those files — the shapes above are the contracts; copy the neighboring tests' vault/monkeypatch scaffolding.

- [x] **Step 2: Run — Expected: FAIL both.**

- [x] **Step 3: Implement side (a)** — in `__main__.py`'s attachment loop, on the unresolved branch, keep the stderr warning and **do not append** to `hashes` (delete the `hashes.append("unresolved")` line). The field's semantics become: list of successfully hashed attachment digests; absence is honest.

- [x] **Step 4: Implement side (b)** — in `verify.py`, guard adoption with a digest-shape check so legacy notes can't anchor acks to a constant:

```python
if isinstance(first, str) and re.fullmatch(r"[0-9a-f]{64}", first):
    return first
```

(The existing managed-bytes fallback below already handles the reject path.)

- [x] **Step 5: Full suite. Commit** `fix: unresolved attachments omit fixity entries; ack scope never anchors to a placeholder`

### Task 17b: Machine-owned frontmatter joins the closing guard (prose-vs-mechanism audit 2026-08-24, bucket-1 finding 2 — the biggest gap: literature frontmatter sits OUTSIDE %%hk-managed%%, so `lint_evidence_layer`'s managed-slice diff never sees it)

**Files:** Modify: `knowledge_harness/lints.py` (`lint_evidence_layer`, ~line 618). Test: `tests/test_lints.py`.

- [x] **Step 1: Failing test** — a hand-edit to a literature note's `archive-url` (and parametrized: `managed-sha256`, `fixity-sha256`, `generated`, `citekey`) with the managed slice untouched currently passes `lint_evidence_layer`; after the fix it is UNMATCHED (`drift`), while edits to non-machine keys (`status`, free-region prose) still pass — screening is human-writable by design.
- [x] **Step 2 (legality rule decided 2026-08-24, superseding the managed-slice coupling — which leaks on archive-url's frontmatter-only write AND on attachment-only fixity changes):** a machine-owned key change (`archive-url`, `managed-sha256`, `fixity-sha256`, `citekey`) is legal iff `generated` changed in the same diff with `by` = the machine actor — writer attestation, not slice coupling. `generated` itself stays guarded under its OWN predicate: a `generated` change whose `by` is not the machine actor is drift — no circularity (it can't legalize itself), and Step 1's five-key parametrization stands, with `generated` asserting the second predicate. Scope stated in the lint's docstring (author ruling 2026-08-24, correcting this clause's original "finding text" — over-specification, not a requirement: the reason string is a governed one-liner repeated on every inbox row, and it carries findings, not scope philosophy): this catches accidents and oblivious agents; forging the attestation is deliberate circumvention (recorded-bypass class). Stated boundary, not a compliance control. No ADR — a scope limitation is a fact, not a decision, and minting one dilutes "only ADRs are binding". Extend `lint_evidence_layer` accordingly.
- [x] **Step 2b:** `archive-source` bumps `generated.{by,at}` on its write (gaining a snapshot IS a meaningful content change; orthogonal to byte-identical-rerender preservation). Test: a legitimate archive run passes the new lint; a bare hand-edit to `archive-url` fails it.
- [x] **Step 3:** Full suite; commit `fix: closing guard covers machine-owned frontmatter keys via writer attestation`.

### Task 18: Supplied snapshots must be snapshots of THIS url (audit defect, archive)

**Files:**

- Modify: `knowledge_harness/archive.py` (supplied-snapshot branch, ~lines 166–185; `is_archive_url` or a new `_snapshot_original`)

- Test: `tests/test_archive.py`

- [x] **Step 1: Failing tests**

```python
def test_supplied_snapshot_must_have_wayback_shape(...):
    # snapshot="https://web.archive.org/" (host-only, alive) → UNMATCHED
    # "missing-archive — supplied snapshot is not a Wayback snapshot URL"

def test_supplied_snapshot_must_match_note_url(...):
    # note url = "https://example.org/paper", snapshot =
    # "https://web.archive.org/web/20240101000000/https://other.site/page"
    # → UNMATCHED "missing-archive — supplied snapshot is for a different URL"
```

- [x] **Step 2: Run — Expected: FAIL** (today `is_archive_url` + non-404 liveness suffices and both cases record MATCHED).

- [x] **Step 3: Implement** — parse the supplied snapshot before any network call:

```python
_SNAPSHOT_RE = re.compile(
    r"^https?://web\.archive\.org/web/(\d{4,14})(?:[a-z_]+)?/(?P<original>https?://.+)$"
)
```

Shape fails → the first UNMATCHED. Shape passes → compare `original` against the note's `url` after the same normalization the codebase already uses for URL comparison (locate it — do not invent a second normalizer; if none exists, exact-match after stripping a single trailing slash and lowercasing scheme+host only). Mismatch → the second UNMATCHED. Then the existing liveness probe and `_record` proceed unchanged.

- [x] **Step 4: Full suite (the live archive legs are env-gated — run them at Task 21). Commit** `fix: supplied archive snapshots verified by shape and target URL`

### Task 19: Partial notice dates keep their precision (audit defect 6)

**Files:**

- Modify: `knowledge_harness/checks.py` (`_notice_date_from_updated`, ~line 506; the reinstatement-clears comparison — locate by `notice_date` ordering use)

- Test: `tests/test_checks.py`

- [x] **Step 1: Failing tests**

```python
def test_partial_date_parts_keep_precision():
    assert checks._notice_date_from_updated({"date-parts": [[2023]]}) == "2023"
    assert checks._notice_date_from_updated({"date-parts": [[2023, 6]]}) == "2023-06"
    assert checks._notice_date_from_updated({"date-parts": [[2023, 6, 15]]}) == "2023-06-15"

def test_ambiguous_reinstatement_does_not_clear():
    # retraction notice_date "2023" (year-only), reinstatement "2023-06-15":
    # the ordering is ambiguous at shared precision → the alert STANDS.
```

- [x] **Step 2: Run — Expected: FAIL** (year-only pads to `2023-01-01` today, and the padded date lets the June reinstatement clear the alert).

- [x] **Step 3: Implement** — `_notice_date_from_updated` returns the ISO-prefix string at the given precision (validate ranges via `_date(year, month or 1, day or 1)` but *emit* only the supplied parts). The reinstatement-clears comparison becomes conservative: it clears **only when** `retraction_date < reinstatement_date` is unambiguous — i.e., neither is a strict prefix of the other and plain string comparison decides, or both are full dates. A prefix-ambiguous pair keeps the alert standing (fail-safe: a standing alert costs an ack; a wrongly-cleared retraction costs the thesis).

- [x] **Step 4: Trace every consumer of `notice_date`** (grep; the reduction's `max()` key, inbox record fields, ack fingerprints). String ordering over ISO prefixes is already consistent for the `max()` newest-wins key; inbox and fingerprints carry the honest partial string. Record each consumer checked in the commit body.

- [x] **Step 5: Full suite; fix tests that pinned padded dates (note each). Commit** `fix: partial Crossref dates keep precision; ambiguous reinstatement never clears`

### Task 19b: PreToolUse deny on machine surfaces (trigger fired 2026-08-24 — the §10 entry said revisit blocking "only on evidence that warnings fail"; the 2c reproduction showed warnings don't exist for two of them: an in-format append to `log/` day files or `inbox/review-queue.md` passes the append-only lint (prefix-preserving), draws no PostToolUse warning (hook covers `literatures/` only), and `okf.py` launders appended log lines into root `log.md`. The sharpest consequence: a hand-Written ack line silently bypasses closures — the publish gate rests on ack integrity)

**Files:** Create/modify: the plugin hooks config + a PreToolUse hook script (audit finding 4's design, verbatim): `permissionDecision: deny` on Edit/Write/NotebookEdit into `literatures/`, `log/`, root `log.md`, `inbox/review-queue.md`, `system/bibliography.json` — fixed path list, no vault import (so no fail-open inheritance). (Author ruling 2026-08-24, correcting this clause: `log.md` was missing from my original four-path enumeration, which predates Task 2c's preamble naming it machine-written. `okf.py` writes root `log.md` in Python, not via a tool call, so the deny costs the legitimate writer nothing — and `okf.regenerate_log` folding appended `log/` lines into `log.md` is this task's own trigger evidence, so omitting it would ship a guard that ignores the exact route the task exists to close. Correct the brief, don't obey it.) The CLI writes through Python, not tool calls — owner unaffected. Test: hook-script unit test over the path list (deny on each machine path incl. a `log/2026-01-01.md` append target; allow on `synthesis/`, `inbox/note.md`, free-region-bearing paths outside the list — the deny is path-scoped, not content-scoped).

- [x] **Step 1:** Failing test first over the path decisions; implement the hook; wire it in the plugin hooks config.
- [x] **Step 2:** The deny message names the legal path — one line: "machine surface; the CLI writes this — use the matching verb (`finding`, `ack`, `import-note`, …)". An agent denied without a route is an agent that retries creatively.
- [x] **Step 3:** Update the §10 deferred entry: trigger fired, evidence cited, blocking shipped for the machine-surface list; the citekey-lint PreToolUse question (warn-vs-block for `[@citekey]` prose) remains deferred — this task ships only the machine-surface deny. Suite; commit `feat: PreToolUse deny guards machine surfaces (trigger evidence: 2c reproduction)`.

### Task 20: Additive `relation.is-retracted-by` read (queued 2026-08-22)

**Files:**

- Modify: `knowledge_harness/checks.py` (`_crossref_notices`, ~line 533)

- Test: `tests/test_checks.py`

- [x] **Step 1: Failing test** — a Crossref message fixture with NO `updated-by` but `"relation": {"is-retracted-by": [{"id": "10.1/notice", "id-type": "doi"}]}` yields one blocking notice (type `retraction`, `notice_date` None, the relation id recorded).

- [x] **Step 2: Run — Expected: FAIL** (only `updated-by` is read today).

- [x] **Step 3: Implement** — after the `updated-by` loop, read `message.get("relation", {}).get("is-retracted-by", [])`; each well-formed entry appends a blocking record `{"type": "retraction", "notice_date": None, "source": "relation", ...}` **unless** an `updated-by` retraction for the same work already exists (no double-count). Malformed relation entries are ignored (the field is additive — it may only add signal, never change an existing verdict). Add the no-double-count test.

- [x] **Step 4: Full suite. Commit** `feat: read Crossref relation.is-retracted-by as an additive retraction signal`

### Task 21: Spec gap closures + acceptance

**Files:**

- Modify: `docs/superpowers/specs/2026-08-16-foundation-spec.md` (§6 gate rows: metadata, update-notice)

- Modify: `docs/superpowers/plans/2026-08-22-plan-s-validation-slice.md` (second sequencing gate: mark satisfied)

- [ ] **Step 1: Metadata row (§6, ~line 98)** — append: *"A compared field absent on either side is SKIPPED for that field, recorded in the outcome's detail — never folded into MATCHED (closed 2026-08-22, audit gap)."* Then verify the implementation agrees (read `check_metadata`'s absent-field handling; if it silently folds, fix it with a failing-test-first micro-cycle inside this task and note it).

- [ ] **Step 2: Update-notice row (§6, ~line 99)** — append the missing-local-version rule by the four-state definitions: *"an item lacking a local `version` field is SKIPPED for the version leg (the item lacks the field the check needs) — never UNREACHABLE, which is reserved for attempted-and-failed"* — then reconcile the implementation (`_datacite_version_outcome` / arXiv twin report UNREACHABLE "outage — version status unavailable" for a missing local field today; both audit lanes disputed this — settle it by the doctrine definition, failing test first, and record the resolution in the commit body).

- [ ] **Step 3: Acceptance sweep** — re-run the audit's confirmed reproductions for every defect this plan claims (defects 1, 2, 3, 6, the fixity pair, the archive branch): each must now be unreproducible. Full suite offline AND live (`HARNESS_LIVE=1 HARNESS_LIVE_NET=1 HARNESS_MAILTO=<real>`, Zotero running). 8/8 hooks.

- [ ] **Step 4: Mark BOTH Plan S sequencing gates satisfied** (one line each, dated, pointing at this plan) — Phases 2–6 and the drill unblock together.

- [ ] **Step 5: Commit** `fix: close spec §6 missing-data gaps; trust-core remediation acceptance` — then merge to main and push in the same motion.

______________________________________________________________________

## Part 3: Terminology (added 2026-08-23)

**NAMING RULING (author, 2026-08-23) — the authored per-source account is a `summary`.** Binding on every implementer who touches this artifact; it creates no work in this plan.

**What is named:** the authored prose account of what one source says, written into that source's literature note free region — authored (salience judgment), never machine-projected. Ruled into existence by slice findings 15–16 (`research/validation-slice/2026-08-22-slice-findings.md`), still unbuilt: no skill step writes it today (Plan D polish-pass item 10, gated on the deferred `/fulltext` leg).

**The name is `summary`.** Walk, per `docs/terminology.md` §2, under the author's ruling that **churn is not a cost and the user-facing term takes precedence** (§1; tie-breaker 4, surface fit is absolute): T1 OKF silent (its `description` is a frontmatter field, not body prose); T2 toolchain surfaces name the container, not this artifact (ZotLit's `note` template body, Zotero child notes, CSL `note`/`annote`); T4 offers *summary*, *synopsis*, *précis*; **T6 is near-unanimous on `## Summary` / "source summary page"** — paperclip (79k★), claude-obsidian (11.3k★), SamurAIGPT/llm-wiki-agent (3.4k★), sdyckjq-lab/llm-wiki-skill (2.4k★), obsidian-llm-wiki-local (809★ — schema field `summary`), swarmvault (666★), pi-llm-wiki (524★), tonbistudio/llm-wiki (247★ — page-type enum value `summary`), wiki-skills (179★); the llm-wiki gist itself writes "a summary page in the wiki". T4 and T6 agree. *Page* is dropped from the borrowed phrase — it names the file, and that slot is `literature note`.

**Declined, so they are not re-proposed:** `digest` (adopted earlier the same day and superseded — the sole ecosystem instance is a 9-star repo, and `hexdigest()` is stdlib so the collision residual never fully clears); `synopsis` (zero collisions but no user-facing currency, which the ruling makes decisive); `précis` (same, and it implies a proportional in-order restatement, which an `(inference)`-tagged region is not); `annotation` (exact in annotated-bibliography practice, fatal against Zotero's highlight sense); bare `summary` **as a vault-facing word for anything else** is now spent.

**The glossary entry does NOT land now** (author ruling): a glossary defines what exists, and this artifact has no writer yet. `CONTEXT.md` gains the term — and `knowledge_harness/templates/vault/system/glossary.md` its projection — in the same change that ships the step which authors it. The entry's wording is settled by this ruling; write it when the step ships.

**What the implementer of that step pays, all priced at zero (`docs/terminology.md` §1) but listed so none is discovered late:**

- `knowledge_harness/templates/vault/index.md:10` — "daily activity log (summary: \[[log]\])" is the only *vault-facing* competing use of the word; reword ("rolled up") in the same change, and update its whole-file test pin in the same commit.
- `CONTEXT.md`'s *Log* entry — "summarized in root `log.md`" → same reword, with the vault-glossary projection.
- `knowledge_harness/okf.py:1` ("the log summary artifact") and `inbox.summary()` are dev-facing (T7) and never reach vault prose — rename or leave, implementer's discretion, not a blocker.
- **Third-party surfaces never rename:** arXiv's `<summary>` element and PubMed's `eSummary` endpoint keep their own names. `skills/find-sources/scripts/arxiv_atom.py:93` already translates arXiv's `<summary>` to `abstract` at the boundary — keep that translation exactly, because it is what stops the wire word for *abstract* from reaching the vault as the word for the one thing an abstract may never produce (ADR-level rule, slice finding 16).
- The section heading in the literature-note free region reads `## Summary`, matching the ecosystem the researcher already knows.

### Task 22: Rename `skipped_digest` → `skipped_sha256` (terminology ruling 2026-08-23)

**RULING (author, 2026-08-23; motivation revised same day) — name the value what it is.** The report field holds a SHA-256 hex string, so it takes the algorithm's own name, in the form `fixity-sha256` and `managed-sha256` already use where the value is durable.

**This is a precision fix, not a collision fix.** It was first ruled to free the word *digest* for the authored per-source account; that account is now named **summary** (the walk above), so nothing collides and nothing downstream waits on this task. It stays in the batch because `skipped_digest` names the shape of the value less honestly than the codebase does everywhere else, and churn is priced at zero (`docs/terminology.md` §1). **If the implementer hits any friction in Step 4, drop the task rather than spend the instrument-freeze window on it** — that is the honest trade now that no collision forces it.

**Non-negotiables:** no alias, no deprecation shim, no back-compat key in the JSON report. `skipped_digest` is a report surface a skill reads, not a persisted vault record — `docs/terminology.md` §4.3 rules that living-surface names rename outright, unlike reason codes and check ids. One verb, one name, one commit.

**Scope bound — rename this and nothing else.** The `factcheck` check id, the `budget-cap` reason code, and the word `skipped` (the four-state result, ADR 0002) are governed vocabulary and stay exactly as they are. This task renames one function, one dict key, and their references.

**Files:** Modify: `knowledge_harness/factcheck.py` (function def + the report dict key); `skills/factcheck-draft/SKILL.md` (the JSON example and the prose sentence naming the field); `tests/test_factcheck.py` (the section marker, the two assertions, the None-case assertion); `knowledge_harness/factcheck.py.manifest.json` (regenerated, see Step 4). Line numbers read at this authoring: `factcheck.py:165,192`; `SKILL.md:28,64`; `tests/test_factcheck.py:199-227` — re-locate by content if drifted. **Also `factcheck.py:39` (`claim_text_hash`'s docstring, "the stable SHA-256 hex digest of one claim's normalized text")** — found 2026-08-23 by the naming sweep, missed by the first site list; the word *digest* there is the hash sense in prose, so it reads "SHA-256 hex value" after this task. `hexdigest()` itself is stdlib and never renames.

- [x] **Step 1: Tests first.** Rename the assertions in `tests/test_factcheck.py` to the new name and run: FAIL (`AttributeError: module 'knowledge_harness.factcheck' has no attribute 'skipped_sha256'`). This is a rename, so the RED phase is the rename's own proof, not a new behavior test — do not add coverage here.
- [x] **Step 2: Rename in `factcheck.py`** — the `def`, the call site inside `run()`, the report dict key, and the docstring's own use of the word. Tests: PASS.
- [x] **Step 3: Skill prose** — update both `skills/factcheck-draft/SKILL.md` sites (the JSON example field and the sentence describing `--target-hash`), then update that file's whole-file test pin in the SAME commit (Global Constraints).
- [x] **Step 4: Mutation sidecar.** `mutation-baseline.txt` carries NO entry for this function (verified 2026-08-23 — the eight `factcheck` baseline keys name other functions), so **no baseline key needs editing**. The sidecar `knowledge_harness/factcheck.py.manifest.json` does carry `func/skipped_digest` plus a `module_hash`/`source_sha256` over the file, both of which the rename invalidates: regenerate it through the gate script's own path (`scripts/mutation_gate.py` always invokes mutate4py with `--manifest-file`; gate mode already scopes to files changed vs the base ref) and commit the regenerated sidecar. **If regeneration is not clean, commit the rename anyway and record the stale manifest in the commit body** — mutate4py's role is frozen until the post-deepening checkpoint (spec §10), so a stale sidecar for one module is an accepted, recorded cost and never a reason to open a new mutation experiment. **If this task runs AFTER Part 4's Task 25 (mutmut adopted, mutate4py sidecars retired), skip this step entirely — there is no sidecar to regenerate.**
- [x] **Step 5: Verification.** `grep -rn "skipped_digest" . --exclude-dir=.git` returns nothing outside this plan's own text. Full offline suite green.
- [x] **Step 6: Commit** `refactor: rename skipped_digest to skipped_sha256 (one sense per term)`.

**Ordering:** independent of every other task in this plan — it touches `factcheck.py` and its own tests, which no other task modifies. Run it anywhere in the batch. If it lands before Task 21, its acceptance rides Task 21's suite and merge; if after, it carries its own suite run and merges on its own.

______________________________________________________________________

## Part 4 — SPLIT OUT (2026-08-24, review finding: the plan outgrew its "single dispatch" header)

The non-gating post-merge tail (mutmut adoption, comment sweep, hermeticity, version currency, CI hardening, full baseline) now lives in its own plan: `docs/superpowers/plans/2026-08-24-plan-w-quality-tail.md`. It runs on main AFTER this plan's Task 21 merge; nothing in it gates the slice.

## NOT in this plan

Four-state dedup (migrate 3–4 — RED-gated) · anything the in-flight references cross-read confirms beyond items 11–12's decided set (triaged separately when it reports) · the skills polish pass + skill-eval lane (POST-slice, informed by usage).

Plan V was absorbed here as Part 2 on 2026-08-22 — the two plans were forced serial by shared `checks.py` test surfaces, and Phase 3's imports run the very checks Part 2 remediates, so one combined merge unblocks slice Phases 2–6 and the drill together. (Its standalone file was removed with the implemented-plans sweep, 2026-08-23; git history holds it.)

## Self-Review (at authoring)

- **Item coverage**: all 19 numbered items of the ruled list map to Tasks 1–13 (items 3+4→T3; 5+7+11+12→T4; 9+10→T7; 13+14→T8; 15→T13); audit defects map 4→T10, 5→T11, 1→T14, 2→T15, 3→T16, fixity pair→T17, archive→T18, 6→T19, relation→T20, spec gaps 86/98/99→T16/T21. Nothing dropped; item 14 is an explicit no-op verification. **Task 22 (added 2026-08-23)** sits outside the original 19-item list — a terminology ruling made after this plan was authored, appended rather than renumbered. **Part 4 (Tasks 23–25, added 2026-08-23)** is the mutmut adoption, author-ruled on the landed pilot; non-gating by placement (post-Task-21), so the slice never waits on it. Commit-note: 3cfb79b's message says "Part 3 — mutmut adoption" but its content is Task 22 (terminology) — a parallel session's uncommitted work swept in under the wrong label; THIS commit carries the actual mutmut Part 4.
- **Placeholder scan**: code tasks (9–12, 14–21) carry failing-test shapes with located scaffolding sources and exact implementation deltas; prose tasks name their content source docs (audit adjudication, cross-read triage) where the decided text is itemized — copy-verbatim instructions, not TBDs.
- **Order dependencies**: T1 (rename) before T2 (index) before T13 (live vault gets the final template). T10's reason-code registration is same-commit with its check (dialect-surface rule). Part 2 runs after Part 1 (shared `checks.py`/inbox test surfaces — T10 and T14–15 touch the same file family). Acceptance consolidates at T21: full suite offline AND live, the audit's reproductions unreproducible, BOTH Plan S sequencing gates marked satisfied.
- **Line numbers** read at 8e98a02/dd4e9f9; re-locate by content if drifted.
