# Plan R: Pre-Baseline Remediation Batch — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land every ruled pre-baseline change in one batch — the security fixes from the 2026-08-21 correctness review (first), the two seam moves from the architecture analysis, the author-triaged over-engineering cuts, and the recorded Plan C follow-ups — so `/code-review ultra` verifies a fixed tree and Plan Q's mutation manifests hash a settled one.

**Architecture:** Four ordered work packages on one branch. Security neutralization is render-boundary-total (evidence strings can never span lines in managed structure; the emitter proves its own output by re-parsing it). The verify engine moves out of the entrypoint behind a public interface consumed by hooks and tests. Cuts and follow-ups are mechanical against their recorded contracts.

**Tech Stack:** Python ≥3.10 stdlib, pytest, git.

**Authority:** `docs/2026-08-21-correctness-security-review.md` (fix contracts, Task 1); the architecture findings recorded 2026-08-21 (Task 2); the author-triaged audit sheet reproduced in Task 3 (accepts, rejects with reasons); Plan C's "final review non-blocking follow-ups" section at commit 34cf831 (Task 4 contracts). **As-built HEAD governs** — cited line numbers are anchors, not contracts; adapt to HEAD and record in commit messages.

## Global Constraints

- Worktree via `superpowers:using-git-worktrees`, branch `build/pre-baseline-remediation`.
- Every test Run begins `cd core && python3 -m venv .venv 2>/dev/null; source .venv/bin/activate && pip install -e ".[dev]" -q`.
- **Task 1 commits alone and first** — the security fix must be a clean, reviewable commit not mixed with moves or cuts.
- **Semantics change ONLY where Task 1's fix contracts say so.** Tasks 2–4 are behavior-preserving (moves, deletions of dead code, recorded follow-up fixes); if any step forces an unstated behavior question, stop and escalate as an SDD ruling.
- Four-state doctrine holds throughout: a render rejection is a reason-coded hold to the review inbox (spec §7 auto-hold), never a crash; hooks stay fail-open.
- Suite green at the end of every task; one conventional commit per task (Task 3 may split cuts into a few commits by module group).
- After merge: the author runs `/code-review ultra` on the result; Plan Q Task 4's Step 0 gate (pre-baseline batch landed) is satisfied by this plan's merge.

## File Structure

- Create: `core/harness_core/verify.py` (engine moved from `__main__.py`), `core/harness_core/outcome.py` (shared vocabulary: `Result`, `Outcome`, `normalize_text`), `core/tests/test_render_neutralization.py`
- Modify: `core/harness_core/{notes,frontmatter,claims,checks,__main__,__init__}.py`, `hooks/stop_publish_gate.py`, `hooks/posttooluse_lint.py`, cut sites across `core/harness_core/` per Task 3, tests throughout.

---

### Task 1: Render-boundary neutralization (Critical/Important/Minor from the security review)

**Files:**
- Modify: `core/harness_core/notes.py`, `core/harness_core/frontmatter.py`, `core/harness_core/__main__.py` (`normalize_annotation`)
- Test: `core/tests/test_render_neutralization.py` (new), existing render/frontmatter tests

**Interfaces:**
- Produces: `notes.render_note` that (a) never interpolates a line-break-bearing evidence string into managed structure and (b) re-parses its own rendered managed body before returning, raising `RenderIntegrityError` on mismatch; `frontmatter.serialize` that raises `FrontmatterError` on control characters in scalars.

**Fix contract (from the review, ruled):** three neutralization rules by field class —
- **Identifier class** (`citekey`): REJECT on any whitespace or control character (a citekey with a space is never valid; altering it would silently mis-key). Extend the `note_path` guard to reject `\r`/`\n` too.
- **Display class** (`pageLabel`, `title`, `comment` already does this): collapse all whitespace runs to single spaces (`" ".join(value.split())`) — total (no import ever held on ugly-but-real metadata), and sufficient: without a newline, injected text cannot create a claim line, a blockquote line, or a marker line.
- **Serializer boundary** (`frontmatter._emit_scalar`): raise `FrontmatterError` on `\r`, `\n`, or other C0 controls — by the time a value reaches the serializer, upstream collapse has run; a surviving control char is a bug and must fail loudly, not serialize unreadably.

- [ ] **Step 1: Write the failing tests** — `core/tests/test_render_neutralization.py`:

```python
"""Regression tests for the 2026-08-21 evidence-text injection review findings."""

import pytest

from harness_core import frontmatter, notes


def _annotation(**overrides):
    base = {
        "type": "highlight",
        "comment": "",
        "pageLabel": "12",
        "key": "ABCD1234",
        "annotationText": "The exact quote.",
        "citekey": "smith2020",
    }
    base.update(overrides)
    return base


def test_pagelabel_newline_cannot_forge_a_second_claim_line():
    claim = notes.render_claim(
        _annotation(pageLabel="1]\n  > x\n- (quote) [@smith2020] ^c-11111111")
    )
    lines = claim.split("\n")
    assert sum(line.lstrip().startswith("- (") for line in lines) == 1
    assert "^c-11111111" not in claim


def test_title_newline_collapses_in_heading_and_aliases():
    # exact assertion shape depends on render_note's signature at HEAD:
    # feed an item whose title embeds "\n---\n" and assert the rendered note
    # (a) parses via frontmatter.parse, (b) contains managed-sha256, and
    # (c) has exactly one H1 line.
    ...


def test_citekey_with_linebreak_is_rejected():
    with pytest.raises(ValueError):
        notes.note_path("smith\n2020", vault=None)  # adapt call shape to HEAD


def test_emit_scalar_rejects_control_characters():
    with pytest.raises(frontmatter.FrontmatterError):
        frontmatter.serialize({"title": "a\nb"})


def test_render_note_round_trip_assertion_catches_forged_body(monkeypatch):
    # Force a mismatch: monkeypatch render_claim to emit an extra claim line
    # and assert render_note raises notes.RenderIntegrityError.
    ...
```

(The two `...` bodies are written against HEAD signatures in this step — no test lands unimplemented.)

- [ ] **Step 2: Run to verify the injection reproduces** — before fixing, temporarily run the pageLabel test against unfixed code: it FAILS with two claim lines (this run is the review's evidence, reproduced).
- [ ] **Step 3: Implement** — display-class collapse where `normalize_annotation` builds the dict (`__main__.py`) AND defensively in `render_claim`/heading rendering (`notes.py`); citekey rejection in `note_path`; `_emit_scalar` control-char raise; then the round-trip self-check at the end of `render_note`:

```python
class RenderIntegrityError(RuntimeError):
    """The rendered managed body does not parse back to the intended claims."""


# at the end of render_note, before returning:
parsed_ids = [c.claim_id for c in claims.parse_claims(rendered) if c.in_managed]
if parsed_ids != expected_ids:
    raise RenderIntegrityError(
        f"managed body parsed to {parsed_ids!r}, expected {expected_ids!r}"
    )
```

- [ ] **Step 4: Wire the failure mode** — a `RenderIntegrityError`/rejection during import surfaces as the existing reason-coded hold to the review inbox (spec §7); verify by test that `import-note` on a poisoned item holds instead of crashing, and writes no note file.
- [ ] **Step 5: Run full suite** — all PASS. **Step 6: Commit** — `git commit -m "fix: neutralize evidence-text injection at the render boundary (review 2026-08-21 C1/I2/M3) + render_note round-trip self-check"`

---

### Task 2: Seam moves — verify engine out of the entrypoint; shared vocabulary home

**Files:**
- Create: `core/harness_core/verify.py`, `core/harness_core/outcome.py`
- Modify: `core/harness_core/__main__.py` (retains argparse dispatch + thin cmd_ wrappers), `core/harness_core/checks.py`, `core/harness_core/__init__.py` (re-export `Result` for compatibility), `hooks/stop_publish_gate.py`, `hooks/posttooluse_lint.py`, importing modules and tests

**Interfaces:**
- Produces: `verify.verify_state(...)`, `verify.surface_decision(...)`, `verify.file_outcomes(...)` — public names, signatures identical to today's `_verify_state`/`_surface_decision`/`_file_outcomes`; `outcome.Result`, `outcome.Outcome`, `outcome.normalize_text` (checks.py re-exports during this plan; importers move now).

- [ ] **Step 1: Move the engine block** (`__main__.py` ~313–1345 at the review's anchor: `_target_hash`, `_apply_state_transitions`, `_file_effects`, `_file_outcomes`, `_plan_state`, `_verify_state`, `_surface_decision`, and their private helpers) to `verify.py` verbatim; public-rename the three hook-consumed entry points; `__main__` imports them for its cmd_ functions.
- [ ] **Step 2: Switch the hooks** — `stop_publish_gate.py` and `posttooluse_lint.py` import the public names from `harness_core.verify`; no hook imports `__main__` afterward (grep-verified).
- [ ] **Step 3: Vocabulary move** — `Result` (from `__init__`), `Outcome`, `normalize_text` (from `checks`) into `outcome.py`; `__init__` and `checks` re-export; importing modules (`identify`, `quotes`, `selectors`, `lints`, `events`, `inbox`) switch to `outcome`.
- [ ] **Step 4: Verify** — `python -m pytest tests -q` all PASS; `grep -rn "from harness_core.__main__ import\|__main__ import" hooks core/harness_core | grep -v cmd_` returns nothing; behavior-preservation check: `git diff` shows moves + import edits only, no logic edits.
- [ ] **Step 5: Commit** — `git commit -m "refactor: extract verify engine to verify.py (public seam for hooks); co-locate Result/Outcome/normalize_text in outcome.py"`

---

### Task 3: Author-triaged over-engineering cuts

**Files:** per finding, at HEAD (post-Task-2 locations — some sites now live in `verify.py`).

**The triage sheet is the contract. ACCEPTED (implement):**
1. `_freeze_json` deep-immutability → targeted copy helper re-wrapping typed target/extras (2 call sites in `reduce_update_notice_outcomes`) [checks.py]
2. Dead parameters + plumbing: `_plan_state`'s `del scope` thread, `lint_evidence_layer`'s `del vault_root`, doctor's `del network`, `run_verify` test-only wrapper, the `snapshots is None` branch, lints' snapshot=None git-refetch fallbacks, `_project_status` tri-mode dispatch [verify.py/lints.py/scaffold.py]
3. `outcome_to_csv_row`/`outcome_from_csv_row`/`_CSV_FIELDS` — tests-only [outcome.py or checks.py]
4. `_offline_network_outcomes` → comprehension over `("doi", "metadata", "update-notice")` [verify.py]
5. gitstate: inline rollback in `apply_outputs` deduped via `rollback_outputs`; write-only `candidate_tree` / test-only `base_tree`; `audit_and_write_manifest` duplicate destination param [gitstate.py]
6. `staleness`/`_committed_state` fingerprint-ladder unification (one helper over `(bytes source, evidence)`) [bibliography.py]
7. pathcodec → `urllib.parse.quote(raw, safe=b"/")` + `unquote_to_bytes`, keeping `_validate_raw` and the canonical round-trip re-check [pathcodec.py]
8. Inbox legacy id acceptance (`base_id` fallback, `allow_legacy_dates`) — nothing ever wrote that format [inbox.py]
9. `Bibliography` dict-wrapper → pass the dict [bibliography.py]
10. Unreachable datacite branch [checks.py]
11. `supports_local_writes` + `local_writes` probe field — knowledge preserved in docs/environment.md [zotero.py/__main__.py]

**REJECTED (do NOT implement; each names its contract — record nothing further):** selector/context feature (spec §5 day-one context capture — insurance data, write-only by design) · fd-pinning/lock chain (standing symlink-strictness ruling) · `inbox.append_ack` (spec §3 ack affordance's substrate; consumer is Plan D) · `events.trust_tier` + friends (§5/§6 vocabulary; consumer is Plan D orientation) · `levenshtein_ratio`→difflib (metric change against the ruled 0.90 threshold; belongs to the W3C reference-vector calibration task). **Retained pending Plan D:** `probe` verb (detect-step instrument choice).

- [ ] **Step 1:** Implement accepts 1–11 in module groups, tests-first where a cut changes a signature (e.g. `Bibliography` → dict touches callers' tests).
- [ ] **Step 2:** Suite green after each group; judged grep per deletion confirms zero production references.
- [ ] **Step 3:** Commit(s) — `refactor: pre-baseline cuts (<group>) per 2026-08-21 audit triage`.

---

### Task 4: Recorded Plan C follow-ups

**Files:** per the "final review non-blocking follow-ups" section of `docs/plans/2026-08-17-plan-c-scaffold-enforcement.md` (recorded at 34cf831) — that section is the contract; read it first.

- [ ] **Step 1: Bypass id discriminator** (leads — doctrine weight: an unacknowledgeable finding id is a liveness hole in the review-inbox contract). Implement per the recorded description; regression test: two bypasses same day produce distinct, individually acknowledgeable ids.
- [ ] **Step 2:** `cmd_verify` broad except narrowed; projection scratch files cleaned up; standing-scope acks item per its recorded text. (Duplicate `staleness()` already fell to Task 3.6.)
- [ ] **Step 3:** Suite green; commit — `fix: Plan C follow-up batch (bypass id discriminator first)`.

---

### Task 5: Acceptance + merge

- [ ] **Step 1:** Full suite offline green; live suite if the environment allows (`HARNESS_LIVE=1 HARNESS_LIVE_NET=1 HARNESS_MAILTO=<real>`).
- [ ] **Step 2:** `ruff format --check` + `ruff check` clean at current config (Plan Q's extended set arrives later — do not pre-adopt it here).
- [ ] **Step 3:** Boundary greps: no hook imports `__main__`; no production reference to any cut symbol; `git diff main --stat` shows only this plan's files.
- [ ] **Step 4:** Merge per `superpowers:finishing-a-development-branch`; report the merge SHA. The author then runs `/code-review ultra` on the trust-critical modules; Plan Q's Step 0 gate is satisfied.

## Self-Review (at authoring)

- Task 1's display-class collapse is deliberately total (never holds an import on ugly metadata) while the citekey rejects — the asymmetry is the contract, not an inconsistency.
- Task 2 before Task 3 so cut sites are named at their final addresses; the plan text flags post-move locations.
- Rejected cuts are reproduced *with reasons* inside this plan so the executing agent never "helpfully" applies them from the audit text.
- `run_verify` deletion (Task 3.2) does not conflict with Task 2: the public seam is `verify_state`/`surface_decision`/`file_outcomes`; `run_verify` was a test-only wrapper and its tests move to the public names.
