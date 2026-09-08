---
name: evidence-conventions
description: Use when writing or editing claims, citing sources, or drafting in a research-vault vault — also for claim or quote syntax questions
---

# Evidence conventions

## The Iron Law

No claim enters a draft without a verified source first.

A claim line exists only after its literature note exists and its citation key resolves. Prose written ahead of its evidence goes to `inbox/`, never `projects/` — write the sentence as fleeting prose, not as a tagged claim, until the source is admitted and projected. A fleeting note opens with `type: "fleeting"` frontmatter when the agent writes it; humans capture free-form and the stamp converges it at triage.

## Claim syntax (§5)

Every claim is one line, and it carries its own tag, citation, and anchor. Claims get copied — from a literature note into a synthesis page, from synthesis into a draft — and whatever is not on the line does not travel with it, so attribution held in frontmatter survives exactly one hop:

```
- (quote|paraphrase|inference|open-question) <text> [@citation-key, locator] [field:: value ...] ^claim-id
```

- **Evidence-boundary tag** — `quote`, `paraphrase`, `inference`, or `open-question`. `open-question` marks a claim with no derivation edge; it is itself lintable, not an escape hatch.

- **`[@citation-key, locator]`** — cites the source; `locator` carries the pinpoint (page, section, …) and parses losslessly to CSL `locator`+`label`.

- **`^claim-id`** — anchors the line for linking, always the last token. Stable across re-render: an anchor derives from stable content (a Zotero annotation key, else a quote hash), never from render order, so re-rendering never breaks an existing claim link.

- **Quotes are blockquotes.** The tag, citation, and anchor ride the claim line; the verbatim text sits in a blockquote line below it:

  ```
  - (quote) [@smith2020, p. 12] ^c-a1b2c3d4
    > Mortality fell 12% (95% CI 8–16).
  ```

### Compiled-layer fields

Claims in the compiled layer under `wiki/` add:

- **`[confidence:: <level>]`** — inference-only.
- **Stance links** — `[supports:: [[citation-key#^claim-id]]]` / `[disputes:: [[citation-key#^claim-id]]]`, targeting another claim link, never a bare note.

### Deprecation — never delete

A claim is retired by a **transition record** on the same line, never by deleting it:

```
[status:: deprecated] [deprecated-at:: <date>] [deprecated-by:: <actor>] [reason:: <code> …]
```

Add `[superseded-by:: <claim link>]` when a successor claim exists. The claim keeps its `^claim-id` anchor through the transition — deprecate with a reason, never delete.

### Retraction acknowledgment

When a cited work carries a blocking-class update notice (retraction, partial retraction, removal, withdrawal), the citing claim needs a reader-side acknowledgment before `publish` can proceed past it:

```
[retraction-ack:: <code> …]
```

This asserts the reader has seen the notice and is knowingly citing the work anyway — for example, citing a retracted paper's methodology while discussing the retraction itself. It is required only when a blocking-class notice targets the citation; warn-class notices (expression of concern, correction, corrigendum, erratum) never require it.

### Verifier-owned markers

`failed-verification` markers are written and cleared only by the CLI's deterministic checks (`research_vault.events.record_pass` / `record_failure`), never by hand. Never add, edit, or remove one yourself, including when retyping a claim — let the next check run clear it.

## Reason-code vocabulary

Findings in `inbox/review-queue.md`, and any other durable surface this registry serves (`find-sources`'s `projects/<name>/search-log.md` is the other shipped one), carry a `reason` code from the controlled registry (`research_vault.inbox.REASON_CODES`, governed at terminology §4.4). The codes you meet in the review queue today:

| Code               | Meaning                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `schema-violation` | The note or claim is structurally broken — malformed frontmatter, a quote claim missing its anchor/text/citation key, invalid bibliography data.                                                                                                                                                                                                                                                                                                                 |
| `mismatch`         | Two authoritative values disagree — citation key not in the bibliography, DOI does not resolve, metadata differs from the registry, quote text absent from the literature note.                                                                                                                                                                                                                                                                                  |
| `outage`           | The check needed a network or service resource that was unreachable. Never a verdict on the claim — retry later.                                                                                                                                                                                                                                                                                                                                                 |
| `no-identifier`    | The check's required field is absent (no DOI/PMID, no citation key, no quote claims), so the check was SKIPPED rather than run.                                                                                                                                                                                                                                                                                                                                  |
| `fuzzy-quote`      | The quote matched only approximately (similarity ≥ 0.90, not exact) — close enough to flag, not to trust.                                                                                                                                                                                                                                                                                                                                                        |
| `warn-notice`      | The cited work carries a warn-class update notice (expression of concern, correction, corrigendum, erratum). Informational, never blocks.                                                                                                                                                                                                                                                                                                                        |
| `retracted`        | The cited work's update-notice check found a blocking-class notice (retraction, partial retraction, removal, withdrawal).                                                                                                                                                                                                                                                                                                                                        |
| `drift`            | An append-only surface was rewritten, a claim anchor mutated or vanished without a deprecation record, a literature note changed outside capture, or a published project diverged from its tag.                                                                                                                                                                                                                                                                  |
| `disputed-claim`   | A claim you're building on (via a `supports` link) has standing counter-evidence elsewhere. Surfaces disconfirmation instead of letting it get silently relied on.                                                                                                                                                                                                                                                                                               |
| `budget-cap`       | Factored verification's per-run budget cap (default 30 claims) was reached; this finding names everything the cap left unchecked this pass. Never means the excluded claims were checked and clean.                                                                                                                                                                                                                                                              |
| `not-admitted`     | Nothing was admitted. Two conditions share this code: the citation key names nothing in the Zotero library (`capture`'s condition — the source was never admitted, or its item has left), or a human looked at a `find-sources` search candidate and declined to admit it (`search-log`'s not-admitted record, spec §7). Admission is a human act; no capture can substitute for it, and a search finding nothing worth admitting is a real result, not silence. |
| `not-captured`     | A citation's citation key is in the bibliography, but no `literatures/<citation-key>.md` note exists — bibliography membership alone is not citability, since there is nothing to verify a quote or paraphrase against. Distinct from `not-admitted`: the source did enter the Zotero library, it just was not run through `capture` yet.                                                                                                                        |
| `contradiction`    | A claim being integrated at compile contradicts a claim already in the compiled layer. Both sides are preserved and linked with `disputes`; a contradiction is never resolved by dropping one.                                                                                                                                                                                                                                                                   |
| `low-confidence`   | An inference claim held back at integration because its `[confidence:: ...]` is low or missing altogether.                                                                                                                                                                                                                                                                                                                                                       |
| `manual`           | A human act rather than a machine observation — no check files it; a person does, when they bypass the publish gate. It is the reason on the finding the Stop hook records for a publish-gate bypass, and the only code in this table a person writes.                                                                                                                                                                                                           |

One registry code stays off this table: `matched` never reaches the queue (only non-MATCHED results file findings).

## Rationalizations, answered

| What you're tempted to think                        | The mechanical rule that forbids it                                                                                                                                                                                                                                                                                                                                            |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "I'll cite it later."                               | The Iron Law: no claim line exists before its citation key resolves. Write it as prose in `inbox/`, not as a tagged claim, until the source is admitted.                                                                                                                                                                                                                       |
| "It's common knowledge."                            | Common knowledge is not an evidence-boundary tag. Every claim line needs `(quote\|paraphrase\|inference\|open-question)` plus a citation key — if it can't carry one, it isn't a claim, it's prose.                                                                                                                                                                            |
| "The abstract said so."                             | Write from the source, never from its abstract. An abstract cannot supply the methods, conditions, and magnitudes a claim states, so expanding one invents specifics and attributes them to the source — a tag does not launder that. Read the admitted item (its attachment lives in Zotero storage); where no full text is reachable, say "no full text available" and stop. |
| "I remember reading it."                            | A claim link only resolves to a literature note that already exists in `literatures/` with a resolving citation key. No note, no citation key — find it or admit the source first.                                                                                                                                                                                             |
| "It's paywalled, I can't verify the exact wording." | Use `(paraphrase)` or `(inference)`, not `(quote)`. A `(quote)` tag commits to text the checker can byte-compare — never fabricate a quote to sound authoritative.                                                                                                                                                                                                             |

## Annotations scatter by link, never by retyping

When the same quote is needed on another page, link the existing claim — `[[citation-key#^claim-id]]` — never retype the quote text. Retyping creates a second, unverified copy that the checker never compares; the single verified quote lives once, in the literature note — a note wholly machine-written from Zotero.
