---
name: publish
description: Use when a person asks to publish, park, correct, or withdraw a knowledge-harness project
disable-model-invocation: true
---

# Publish a project

Use this only when the person explicitly invokes it. "Publish" is this skill's action, not a branch merge.

Every mechanical act below is a CLI verb call: you compose and explain, the person chooses, the CLI writes. Never hand-write a status, a `verified` event, a tag, an acknowledgment, or a review-inbox entry — not in a note, not in frontmatter, not anywhere.

In every command, `PATH` is the vault and `NAME` is the project's name under `projects/` — `brief`, not `projects/brief`.

## Orient

Drain the review inbox before anything else:

```sh
python3 -m knowledge_harness inbox --vault PATH
```

Report the unacknowledged count and the oldest entry's date, then count the **blocking-class** entries separately: those carry the reason code `retracted` — a retraction, partial retraction, removal, or withdrawal targeting a cited work. They are the only *standing alerts* that hold the publish gate; every other finding already in the queue informs and never closes a surface. (The gate still closes on its own checks' current results — see below — so a clean inbox is not the same as a green gate.) State that count out loud before anyone chooses a disposition.

## Run the gate

```sh
python3 -m knowledge_harness verify --surface publish --vault PATH
```

The publish surface closes on `citekey`, `evidence-layer`, `quote`, `update-notice`, and `doi`. Exit `0` means green, `1` means a closing check is UNMATCHED, `3` means something was UNREACHABLE, and `2` means verification could not run at all.

## Report the four states honestly

| Result | Meaning | At publish |
|---|---|---|
| MATCHED | The check ran and agreed. | Passes; the CLI appends a `verified` event. |
| UNMATCHED | The check ran and disagreed. | Holds the gate until it is fixed or acknowledged. |
| UNREACHABLE | The check could not run — a network or service outage. | **Holds the gate: publishing waits.** Never a verdict on the work. |
| SKIPPED | The item lacks the field the check needs. | Exempt, and recorded in the review inbox so it stays auditable. |

An outage is never a failure and never a pass. Do not describe an UNREACHABLE result as "verified", "failed", or "probably fine" — say the check could not run and publishing waits until it can. Never claim a check ran that did not, and never claim a `verified` event exists: only a MATCHED result mints one, and only the CLI writes it.

## The day-one disposition menu

Present exactly these three and let the person choose. Never pick for them.

- **mark-published** — a full gate run plus its effects: sets `status: "published"` in the project's frontmatter, appends a project-level `verified` event, commits and tags `published/<project>-<date>`.
- **park** — sets `status: "parked"`, nothing else.
- **keep-draft** — a no-op. Say so and stop; write nothing at all.

To publish, arm the gate first, then run the disposition:

```sh
python3 -m knowledge_harness arm-publish NAME --vault PATH
python3 -m knowledge_harness mark-published NAME --vault PATH
```

Arming writes the state flag the Stop hook checks; while it is absent the hook is inert. `mark-published` runs the closed gate itself and refuses unless the publish surface is green or every blocking entry carries a standing acknowledgment. **A refusal leaves the gate armed** — the Stop hook keeps holding the session until the finding is resolved, acknowledged, or the person abandons the attempt:

```sh
python3 -m knowledge_harness disarm-publish --vault PATH
```

`mark-published` disarms the gate itself once it has committed and tagged. Park needs no arming:

```sh
python3 -m knowledge_harness park NAME --vault PATH
```

Deletion is not on the menu. Delete a project only when the person explicitly asks for deletion **and** types `discard` on its own. Anything less — "drop it", "get rid of it", a nodded-through summary — is not consent; offer park or keep-draft instead. Never infer the typed word from context and never type it on their behalf.

## Acknowledging a blocking finding

An acknowledgment is a human's standing acceptance of a finding — the only bypass a closed check has, and it keeps the record rather than deleting it. Show the person the exact finding, explain what accepting it means, and let them supply the reason. Then write it with the verb:

```sh
python3 -m knowledge_harness ack FINDING-ID --vault PATH --reason "CODE free text" --actor "human:NAME"
```

The finding id comes from the `inbox` listing. The reason must start with a registry code (see `evidence-conventions`), and the actor must be a real `human:` identity — the CLI refuses to consent on anyone's behalf. An acknowledgment is scoped to the content it was granted for: if the note changes afterwards, the finding returns and needs a fresh one.

A blocking-class update notice also needs a `[retraction-ack:: <code> …]` field on the citing claim itself, per `evidence-conventions`. That is the reader-side half; the inbox `ack` is the gate-side half, and the gate needs both.

## After publication: the correction lifecycle

A blocking-class alert or a claim deprecation that targets an already-published project does not merely block the next publish. It opens a **correction disposition** — present it as soon as the alert appears, not at the next publish attempt:

- **mark-corrected** — re-publish as corrected: a new gate run, a new `verified` event, a new tag.
- **mark-withdrawn** — set `status: "withdrawn"` and record the withdrawal in the day's log.

```sh
python3 -m knowledge_harness arm-publish NAME --vault PATH
python3 -m knowledge_harness mark-corrected NAME --vault PATH
python3 -m knowledge_harness mark-withdrawn NAME --vault PATH
```

Both verbs refuse a project that was never published — the lifecycle opens only after publication. **The original tag is never deleted**, by either disposition or by hand: a correction adds a tag, it does not replace one. Never offer tag deletion, history rewriting, or a quiet edit of the published note as an alternative.

## Refusals and exit codes

`mark-published` and `mark-corrected` run the gate, so they answer with it: `0` done, `1` a closing check is UNMATCHED, `3` a check was UNREACHABLE so publishing waits. `mark-withdrawn` and `park` run no gate, so they only ever answer `0` or `2`. Across all four, `2` means the CLI could not carry the disposition out at all — no such project, the project has uncommitted files, a tag of that name already exists, the project was never published. Read the printed blockers back verbatim; do not summarize them into "it failed".

Publishing commits only the project note. If the CLI reports uncommitted files under `projects/NAME`, have the person commit them first — the published tag has to match the project the moment it is minted, or the published-drift lint reports the project as diverged.

The gate has one audited bypass, and it is the person's to ask for, never yours to suggest:

```sh
python3 -m knowledge_harness arm-publish NAME --vault PATH --bypass "why this one time"
```

The Stop hook records that token in the review inbox as an open finding. Explain that it is recorded, not forgiven, before writing it.
