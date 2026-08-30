# Task 2c report — vault AGENTS.md opens with the integrity preamble

## Status: DONE_WITH_CONCERNS

Commit: `514d12b feat: vault AGENTS.md opens with the integrity preamble`

## Surface-list reconciliation

**Brief's draft (task-2c-brief.md, Step 1):**
> `literatures/`, `log/`, root `log.md`, and `inbox/review-queue.md` are
> machine-written — the CLI writes them; hand edits are warned in session
> and caught at commit.

**What the template already names, verified before writing:**
- Line 6: `literatures/` — "evidence notes exist only by projection, never
  by hand."
- Line 24 (now line 26): `Machine surfaces (`log/`, `inbox/review-queue.md`,
  managed regions, `system/bibliography.json`) are owner-written: hand or
  tool edits are regenerated away or raise a finding.`

Root `log.md` appears in **neither**. It is nonetheless a genuine
machine-written surface — confirmed in code, not assumed:
`research_vault/okf.py:1` ("Root log.md regeneration: the single writer
for OKF's log summary artifact"), with `scaffold.py:206-207` shipping a
freshly-scaffolded vault's `log.md` already OKF-conformant.

**Ruling:** dropped root `log.md` from the preamble; kept `literatures/`,
`log/`, `inbox/review-queue.md` — the three items the template's own prose
already names. Left out `managed regions` and `system/bibliography.json`
(reasoning under Redundancy below). This is the literal reading of "adjust
the surface list to what the template already names," and it is the
reading that avoids silently expanding the preamble past what line 24
already says — which the brief explicitly warned against.

**Finding, reported not fixed:** line 24's "machine surfaces" enumeration
is itself incomplete relative to what research-vault actually machine-writes
— it omits root `log.md`. This is a real inconsistency in the template's
existing text, pre-dating this task. Fixing it would mean editing line 24,
which this brief does not authorize ("the brief authorises adding a
preamble, not deleting line 24" — and by the same logic, not silently
expanding it either). Left for the plan author to rule on.

## Shipped preamble

Inserted as the first paragraph after the `# Vault agents guide` heading,
before the existing orientation paragraph and before the routing index
(the seven-skill table landed by `45aa45d`):

> This is a research-vault vault. `literatures/`, `log/`, and
> `inbox/review-queue.md` are machine-written — the CLI writes them; hand
> edits are warned in session and caught at commit.

Two sentences, as specified. "The CLI writes them" matches the token this
batch standardized on (`eb54ab6`, `a2a5aad`) and already used verbatim or
near-verbatim in `skills/verify-citations/SKILL.md:9`,
`skills/project-flow/SKILL.md:86`, `skills/import-source/SKILL.md:13`, and
`skills/publish/SKILL.md:13`.

## Redundancy judgment against line 24

The preamble and line 24 both name `log/` and `inbox/review-queue.md` —
deliberate overlap, not a bug: the preamble exists for the agent that reads
nothing else, so it has to stand alone even though line 24 says something
close two paragraphs later. I differentiated them in altitude rather than
wording:

- **Preamble**: a coarse, path-level deterrent — three surfaces, the
  enforcement story in one clause, nothing about mechanism.
- **Line 24**: the complete, mechanism-level enumeration — five items
  including `managed regions` and `system/bibliography.json`, plus the
  precise consequence ("regenerated away or raise a finding").

I did not fold `managed regions` or `system/bibliography.json` into the
preamble. Doing so would have made the two paragraphs near-verbatim
restatements of each other (the exact defect flagged as a risk), for no
protective gain — see the "warned in session" precision concern below,
which independently argues against including `system/bibliography.json`
in a sentence that claims session-time warning.

Line 24 itself is untouched, byte-for-byte, as the brief scopes.

## Concern: the enforcement clause's precision is uneven across the three surfaces

I verified this in code rather than asserting it from the prose, and it
applies to the brief's draft sentence structure as much as to mine (I only
adjusted the noun list, not the verb clause, which the brief scoped as
out of bounds for this task):

- **`literatures/`**: warned in session — `hooks/posttooluse_lint.py:97-98`
  fires an explicit warning for any path under `literatures/`. Also
  **blocks** at commit — `lint_evidence_layer`'s check id `evidence-layer`
  is in `CLOSING_BY_SURFACE["commit"]` (`research_vault/verify.py:53-58`),
  so a hand-edited managed region fails the pre-commit gate.
- **`log/`** and **`inbox/review-queue.md`**: **not** warned in session —
  `hooks/posttooluse_lint.py:13,104` only fires its warning path for
  `CONCEPT_ROOTS = {"synthesis", "projects"}` plus the separate
  `literatures/` case; there is no PostToolUse warning for these two.
  They also do **not** block at commit — `lint_append_only`'s check id
  (`append-only`) is not in `CLOSING_BY_SURFACE["commit"]`, only
  `{"citekey", "evidence-layer"}` are. This is exactly what the existing
  pin comment at `tests/test_templates.py:94-99` already records:
  "machine-surface rule reworded to 'raise a finding' ... 'fail the gate'
  was false" for these two surfaces.

So "hand edits are warned in session and caught at commit" is fully
accurate only for `literatures/`. For `log/` and `inbox/review-queue.md`,
"warned in session" is false (no such warning exists) and "caught at
commit" overstates the mechanism (a finding is raised and recorded, but
the commit is not blocked).

I did not reword this clause. The brief's Step 1 authorizes adjusting the
*surface list* ("adjust the surface list to what the template already
names") and says nothing about the enforcement clause, which is the plan
author's exact draft wording; rewording it would exceed what this task
scopes, the same principle that kept me from touching line 24. Flagging it
here for the plan author to rule on, the same way task 2b flagged its
second pin rather than silently absorbing the fix.

## Pin(s) — how I found them, not assumed from the brief

The brief's own warning ("do not trust any surface list, including mine")
plus task 2b's precedent (a second byte-equality pin on the same content
in `tests/test_scaffold.py`) meant I ran the full suite rather than editing
only the pin named in the brief.

1. Edited the template first, alone.
2. `.venv/bin/python -m pytest tests -q` → exactly one failure:
   `tests/test_templates.py::test_markdown_templates_match_canonical_content`,
   at the `asset("vault/AGENTS.md").read_text() ==` byte-equality
   assertion (line 100). `1574 passed, 7 skipped, 1 failed`.
3. Checked for a task-2b-style second pin specifically: grepped
   `tests/*.py` for `AGENTS.md` content. `tests/test_scaffold.py` lists
   `AGENTS.md` only as a path in `EXPECTED_CREATED` (line 25/111) and
   checks its frontmatter `type` is truthy (line 110-120) — no full-body
   byte-equality assertion exists there, so there is no second pin to move.
4. Repo-wide grep for the template's distinctive strings ("Vault agents
   guide", "Evidence is admitted through Zotero") found only
   `research_vault/templates/vault/AGENTS.md` itself, `tests/test_templates.py`,
   and `docs/superpowers/plans/2026-08-22-vault-agents-template-revision.md`
   (a completed plan doc — per this repo's AGENTS.md, "completed plans ...
   stand as written," so correctly left untouched).
5. Updated the one pin, re-ran the full suite: `1575 passed, 7 skipped` —
   matches the stated baseline exactly.

## What I tested

1. `.venv/bin/python -m pytest tests -q` — before the pin fix: `1574
   passed, 7 skipped, 1 failed` (confirms the template edit surfaced
   exactly the pin expected, nothing hidden). After: `1575 passed, 7
   skipped`, twice (once before commit, once after, at the committed
   `HEAD = 514d12b` with a clean tree).
2. `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files` —
   8/8 passed.
3. `git status --short` / `git diff` inspected before staging — confirmed
   only the two intended files changed (`research_vault/templates/vault/AGENTS.md`,
   `tests/test_templates.py`), five inserted lines total, no formatter
   churn.
4. Verified `mdformat`'s pre-commit hook is structurally scoped away from
   both changed files (`.pre-commit-config.yaml:57` path list is `README.md
   AGENTS.md CONTEXT.md docs skills`, `pass_filenames: false`), and the
   green form-gate run corroborates this empirically.
5. Read the actual enforcement code (`hooks/posttooluse_lint.py`,
   `research_vault/verify.py`'s `CLOSING_BY_SURFACE`,
   `research_vault/lints.py`'s `_is_append_only_path` and
   `lint_evidence_layer`) rather than trusting the prose, before deciding
   which surfaces belonged in a sentence that makes a specific enforcement
   claim.

## Self-review (per the brief's checklist)

- **Is every surface I named actually machine-written?** Yes: `literatures/`
  (projected from Zotero, never hand-written per line 6 and
  `hooks/posttooluse_lint.py:97-98`), `log/` (per-day activity log, written
  by `research_vault/publish.py:400`'s append step), `inbox/review-queue.md`
  (owner-written per line 24 and protected by `lint_append_only`).
- **Does the preamble read as protection for someone who stops there,
  rather than a summary of the document?** It states the one fact that
  matters if nothing else is read — this vault has machine-owned surfaces,
  do not hand-edit them — without previewing the routing index, the
  managed-region rule, or the formatter warning that follow. It does not
  mention the seven skills, `synthesis/index.md`, `evidence-conventions`,
  or any of the document's other content.

## Concerns

1. **Line 24's own surface list is incomplete** (omits root `log.md`,
   which is genuinely machine-written per `research_vault/okf.py`).
   Reported per the brief's explicit instruction, not fixed — out of this
   task's scope.
2. **The preamble's enforcement clause ("warned in session and caught at
   commit") is precise only for `literatures/`.** For `log/` and
   `inbox/review-queue.md`, there is no session-time warning, and
   "caught at commit" means a non-blocking finding is raised, not that the
   commit fails — exactly the distinction the pre-existing pin comment at
   `tests/test_templates.py:94-99` already records for the same two
   surfaces. I did not reword the clause since the brief scoped this task
   to the surface list only; flagging for the plan author instead of
   silently rewording language the brief didn't authorize me to touch.

Neither concern blocks: the suite is green at baseline, the form gate is
8/8, and both are pre-existing template-text issues surfaced by this task
rather than introduced by it.

## Fix round 1 (coordinator-ruled)

Concern 2 above (the enforcement clause's precision) was escalated by the
coordinator to the plan author, who independently verified it against
`CLOSING_BY_SURFACE` in `research_vault/verify.py:53-58` and ruled:
weaken the clause to what is true of every named surface, keep all three
surface names, do not narrow the list and do not change gate behavior
(spec §6's warn-tier lint design is deliberate; changing it as a side
effect of a sentence fix would be out of scope).

**Change applied:** `hand edits are warned in session and caught at
commit` → `hand edits leave a trace`, in both the template
(`research_vault/templates/vault/AGENTS.md`) and its pin
(`tests/test_templates.py:105`). The author confirmed `leave a trace` is
true on all three named surfaces: `literatures/` via evidence-layer
closure (blocks at commit), `log/` and `inbox/review-queue.md` via
append-only findings (recorded, non-blocking) and drift records. This is
a decided correction from the plan author via the coordinator, not this
task's own editorial judgment — recorded as such in the amended commit
body.

Concern 1 (line 24's own machine-surfaces list omits root `log.md`) was
confirmed correct to report-and-leave: deferred to the final review,
line 24 untouched.

**Commit:** amended in place — `514d12b` was still the branch tip with
nothing landed on top, so per the coordinator's instruction this was an
amend, not a follow-up commit. New SHA: `a5668d6 feat: vault AGENTS.md
opens with the integrity preamble`.

**Test evidence for the fix:**
1. `.venv/bin/python -m pytest tests/test_templates.py -q` → `7 passed`.
2. `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files` →
   8/8 passed.
3. `.venv/bin/python -m pytest tests -q` → `1575 passed, 7 skipped`
   (baseline-equal).
4. `git status --short` clean at the amended commit; `git show a5668d6`
   confirms the diff against the pre-preamble parent is exactly the same
   five inserted lines as before, with only the enforcement clause's
   wording changed relative to the pre-amend version.

## Status: DONE (fix round 1 applied)

## Fix round 2 (coordinator-ruled, supersedes round 1)

Review reproduced, end to end in a scaffolded vault, that round 1's
"hand edits leave a trace" is also false: an in-format append to a `log/`
day file produces no PostToolUse warning
(`hooks/posttooluse_lint.py:97,104` covers only `literatures/` and
`CONCEPT_ROOTS = {synthesis, projects}`), no append-only finding
(`research_vault/lints.py`'s `lint_append_only` fires only on
`not new_bytes.startswith(old_bytes)`, and an append keeps the old bytes
as a prefix, so the predicate never trips — verified by reading the exact
condition), and no gate (`append-only` is absent from
`CLOSING_BY_SURFACE["commit"]`). `verify --surface commit` exits 0 with
zero findings, and `research_vault/okf.py` then copies the fabricated
line into root `log.md` unchallenged. The same prefix predicate silences
in-format appends to `inbox/review-queue.md` too — so no enforcement
wording is true of every named surface, confirming the pattern my original
concern 2 flagged was structural, not a one-clause wording slip.

**Ruling:** drop the mechanism claim entirely — assert a boundary, not a
compliance control. **Decided sentence:** "This is a research-vault
vault. `literatures/`, `log/`, `log.md`, and `inbox/review-queue.md` are
machine-written — the CLI writes them; don't edit them by hand." This
also resolves concern 1 (root `log.md` named nowhere in the template):
adding a fourth surface is now safe because the sentence makes no
per-surface enforcement claim that would need separate verification
against `log.md`.

**Changes applied:**
1. Template (`research_vault/templates/vault/AGENTS.md` line 6) and its
   pin (`tests/test_templates.py`) both updated to the decided sentence,
   same commit.
2. Added a constraint comment directly above the `vault/AGENTS.md`
   byte-equality assertion in `tests/test_templates.py`, stating (as a
   constraint, not a history note) that the preamble must assert no
   enforcement mechanism, and that any future wording claiming detection
   or blocking must be re-verified against `CLOSING_BY_SURFACE` and
   `lint_append_only`'s startswith predicate before landing — closing the
   gap the review flagged (the old comment only protected line 26's
   wording, not the new preamble's).

**Commit:** `a5668d6` was still branch tip with nothing landed on top, so
amended again per instruction. New SHA: `c8cac73 feat: vault AGENTS.md
opens with the integrity preamble`. Commit body records round 1 (kept for
the record, marked superseded), round 2's reproduction and ruling, and
that this is a decided change via the coordinator, not editorial judgment.

**Test evidence:**
1. `.venv/bin/python -m pytest tests/test_templates.py -q` → `7 passed`.
2. `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files` →
   8/8 passed.
3. `.venv/bin/python -m pytest tests -q` → `1575 passed, 7 skipped`
   (baseline-equal).
4. `git status --short` clean at the amended commit.

## Status: DONE (fix round 2 applied)
