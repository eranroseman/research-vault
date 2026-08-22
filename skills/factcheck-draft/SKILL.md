---
name: factcheck-draft
description: Use when a person asks to factcheck a draft, sanity-check claims against their sources, or run factored verification before review
disable-model-invocation: true
---

# Factcheck a draft

This is **factored verification** (§6): an LLM decompose-and-check pass at draft→review. It is deliberately not deterministic and it **never blocks** — not a commit, not a publish attempt, nothing. Every result becomes an adjudicated finding, written through the `finding` verb, warn-tier, for a person to triage later. Never write a review-inbox entry, a `[failed-verification::]` marker, or a `verified` event yourself — this skill's job is judgment; the CLI's job is every write.

## Select claims mechanically, never by reading the draft yourself

Selection under the budget is **deterministic** — run the CLI's `factcheck` subcommand; do not sort or prioritize claims by eye:

```sh
python3 -m knowledge_harness factcheck --vault PATH --draft projects/NAME/DRAFT.md --cap 30
```

`--cap` defaults to 30 and is user-overridable — ask before changing it, and say what you changed it to. The budget is one LLM pass per selected claim; do not re-check a claim twice in the same run.

`factcheck` is a read-only report, like `verify` — it prints one JSON report and writes nothing durable itself:

```json
{
  "cap": 30,
  "selected": [{"claim_link": "smith2020#^c-1a2b3c4d", "tag": "paraphrase", "line_no": 12, "text_hash": "…"}],
  "skipped": [{"claim_link": "smith2020#^c-9f8e7d6c", "tag": "quote", "line_no": 40, "text_hash": "…"}],
  "skipped_digest": "…" 
}
```

Its selection order (spec §6, binding — not a suggestion): **inference/paraphrase claims lacking any `verified` event first, contested-adjacent claims boosted, quote claims last** (quote claims are already deterministically covered by `verify-citations`'s quote checker, so they carry the least urgency for an LLM pass). Ties keep document order. `selected` holds at most `--cap` claims; anything past the cap lands in `skipped` — this is the budget working as designed, not an error.

## Check every selected claim, one pass each

For each entry in `selected`, open the draft at `line_no` and the cited literature note (`literatures/<citekey>.md`, citekey from `claim_link`) and read its managed region. What you're judging depends on the claim's tag:

- **`quote`** — quote fidelity: the deterministic checker already confirmed the text matches byte-for-byte (or flagged it if not); your job is whether the excerpt, as used in the draft, is fair to the source — not cherry-picked or presented out of the context that would change its meaning.
- **`paraphrase`** — paraphrase support: does the cited managed region actually support this paraphrase's direction, magnitude, population, and certainty — not just its general topic?
- **`inference`** — inference-marked-as-inference: is this genuinely an inference from the cited material (not dressed up as an established fact), and is it a reasonable step from what the source actually says?

## Record the result — never silently

**MATCHED** writes nothing. Factored verification is LLM judgment, and per §5/§6, LLM judgment never mints a `verified` event — only a genuine deterministic check does — so a clean adjudication has no durable record to write. Report MATCHED counts to the person directly in your summary; that summary, not the inbox, is where a clean pass lives.

Every other outcome is a finding, filed by check id `factcheck`, targeting the claim link, carrying that claim's `text_hash` as `--target-hash` (so a later edit to the claim reopens the finding, and an unchanged retry does not duplicate it):

```sh
python3 -m knowledge_harness finding factcheck CLAIM_LINK UNMATCHED "mismatch — ONE-LINE REASON" --vault PATH --target-hash TEXT_HASH
python3 -m knowledge_harness finding factcheck CLAIM_LINK UNREACHABLE "outage — ONE-LINE REASON" --vault PATH --target-hash TEXT_HASH
python3 -m knowledge_harness finding factcheck CLAIM_LINK SKIPPED "no-identifier — ONE-LINE REASON" --vault PATH --target-hash TEXT_HASH
```

Per-claim SKIPPED here means a claim the script selected but that turned out structurally uncheckable (its managed region was empty, or otherwise unreadable) — this should be rare, since ineligible claims are already excluded from `selected`.

## Record the skipped set — never silently dropped

If `skipped` is non-empty, file **one** finding naming everything the budget cap left unchecked this pass — an unchecked claim must never read as checked:

```sh
python3 -m knowledge_harness finding factcheck "projects/NAME" SKIPPED "budget-cap — N claims not checked this pass: LINK1, LINK2, …" --vault PATH --target-hash SKIPPED_DIGEST
```

The target is the project itself — a gate-run reference, not a claim link — and `--target-hash` is the script's own `skipped_digest`: a rerun with the identical skipped set is a no-op (the `finding` verb collapses it to the existing entry), while a genuinely different skipped set gets its own record.

## Four-state honesty, at the factcheck level too

| Result | Meaning here | Recorded? |
|---|---|---|
| MATCHED | The claim held up under LLM adjudication. | No — see above. |
| UNMATCHED | The claim's stated content disagrees with what the cited region actually supports. | Yes, `mismatch`. |
| UNREACHABLE | The adjudication could not run — the cited source text wasn't accessible, or the pass was interrupted. **Never a verdict on the claim.** | Yes, `outage`. |
| SKIPPED | Never checked — either structurally (this one claim) or by budget (the whole skipped set). **Never present a skipped claim as if it were checked and clean.** | Yes, `no-identifier` or `budget-cap`. |

An UNREACHABLE result is named as an outage in every summary you give — never as a failure, never as "probably fine." Do not claim you checked a claim you did not: the skipped set exists precisely so silence never reads as clearance.

## This never blocks

Every finding this skill files is warn-tier: no commit, no session, no publish attempt is ever held by a factcheck result — that gating belongs entirely to `verify-citations`'s deterministic suite. A person may triage and acknowledge factcheck findings through the `publish` skill's `ack` flow at their own pace, or simply revise the draft and re-run this skill; either is fine, and neither is required before anything else proceeds.
