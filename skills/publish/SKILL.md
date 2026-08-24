---
name: publish
description: Use when a person asks to publish, park, correct, or withdraw a knowledge-harness project
disable-model-invocation: true
---

# Publish a project

Use this only when the person explicitly invokes it. "Publish" is this skill's action, not a branch merge.

Say this before the first command: publishing here runs through an armed gate — `arm-publish` sets a state flag the Stop hook reads, and from the moment it is set the hook holds the session until the attempt lands, is acknowledged, or is disarmed. This is the most irreversible thing the vault does, so the person hears it at the start rather than meeting it at the first refusal.

Every mechanical act below — a status, a `verified` event, a tag, an acknowledgment, a review-inbox entry — is a CLI verb call: you compose and explain, the person chooses, the CLI writes — never by hand, not in a note, not in frontmatter, not anywhere.

In every command, `PATH` is the vault and `NAME` is the project's name under `projects/` — `brief`, not `projects/brief`.

## Orient

Drain the review inbox before anything else:

```sh
python3 -m knowledge_harness inbox --vault PATH
```

Each finding line begins with its finding id — the argument `ack` needs later. Report the unacknowledged count and the oldest entry's date, then count the **blocking-class** entries separately: those carry the reason code `retracted` — a retraction, partial retraction, removal, or withdrawal targeting a cited work. They are the only *standing alerts* that hold the publish gate; every other finding already in the queue informs and never closes a surface. (The gate still closes on its own checks' current results — see below — so a clean inbox is not the same as a green gate.) State that count out loud before anyone chooses a disposition.

## Run the gate

```sh
python3 -m knowledge_harness verify --surface publish --vault PATH
```

The publish surface closes on `citekey`, `evidence-layer`, `quote`, `update-notice`, and `doi`. Exit `0` means green, `1` means a closing check is UNMATCHED, `3` means something was UNREACHABLE, and `2` means verification could not run at all.

## Report the four states honestly

| Result      | Meaning                                                | At publish                                                                                                                                                                                                                                                                                                                                                                                                           |
| ----------- | ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MATCHED     | The check ran and agreed.                              | Passes. **Only `doi`, `metadata`, `update-notice`, and per-claim `quote` mint a `verified` event on MATCHED** — this surface's other two closing checks, `citekey` and `evidence-layer`, mint nothing, and leave no durable trace beyond the run's counts. The project-level `verified` event is separate and real: `mark-published` and `mark-corrected` mint one on the project note under the check id `publish`. |
| UNMATCHED   | The check ran and disagreed.                           | Holds the gate until it is fixed or acknowledged.                                                                                                                                                                                                                                                                                                                                                                    |
| UNREACHABLE | The check could not run — a network or service outage. | **Holds the gate: publishing waits.** Never a verdict on the work.                                                                                                                                                                                                                                                                                                                                                   |
| SKIPPED     | The item lacks the field the check needs.              | Exempt, and recorded in the review inbox so it stays auditable.                                                                                                                                                                                                                                                                                                                                                      |

An outage is never a failure and never a pass. Do not describe an UNREACHABLE result as "verified", "failed", or "probably fine" — say the check could not run and publishing waits until it can. Never claim a check ran that did not, and never claim a `verified` event exists for a check id that doesn't mint one — only the CLI mints events, only on a genuine MATCHED result, and only for the four check ids named above plus the project-level `publish` event the disposition verbs write.

## The day-one disposition menu

This is the **pre-publication** menu. Present exactly these three and let the person choose. Never pick for them.

- **mark-published** — a full gate run plus its effects: sets `status: "published"` in the project's frontmatter, appends a project-level `verified` event, commits and tags `published/<project>-<date>-<time>` (`published/brief-2026-08-01-091500`; the time is UTC, `HHMMSS`, and every publication tag carries one).
- **park** — sets `status: "parked"`, nothing else. The CLI verb is `mark-parked` (`park → mark-parked`, matching `mark-published`/`mark-corrected`/`mark-withdrawn`).
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

`mark-published` disarms the gate itself once it has committed and tagged. `mark-parked` needs no arming:

```sh
python3 -m knowledge_harness mark-parked NAME --vault PATH
```

`mark-published` and `mark-parked` both refuse a project that is already published, naming the two dispositions that do apply — see the correction lifecycle below.

Deletion is not on the menu. Delete a project only when the person explicitly asks for deletion **and** types `discard` on its own. Anything less — "drop it", "get rid of it", a nodded-through summary — is not consent; offer park or keep-draft instead. Never infer the typed word from context and never type it on their behalf.

## Acknowledging a blocking finding

An acknowledgment is a human's standing acceptance of a finding — the only bypass a closed check has, and it keeps the record rather than deleting it. Show the person the exact finding, explain what accepting it means, and let them supply the reason. Then write it with the verb:

```sh
python3 -m knowledge_harness ack FINDING-ID --vault PATH --reason "CODE free text" --actor "human:NAME"
```

The finding id is the first token of each line in the `inbox` listing — copy it exactly, never retype or abbreviate it. The reason must start with a registry code (see `evidence-conventions`), and the actor must be a real `human:` identity — the CLI refuses to consent on anyone's behalf. An acknowledgment is scoped to the content it was granted for: if the note changes afterwards, the finding returns and needs a fresh one.

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

**A correction on the day of publication just works.** Publish in the morning, correct in the afternoon when a retraction notice lands, correct again that evening: every tag carries a UTC time, so each disposition mints its own and none collides. Say so plainly rather than telling a person to wait for tomorrow.

The date half of that tag — which is also the `verified` event's stamp and the withdrawal log line's day — defaults to today. Name it explicitly only to date a disposition to a different day, on any of the three dated dispositions:

```sh
python3 -m knowledge_harness mark-corrected NAME --vault PATH --date YYYY-MM-DD
```

The date must be a real calendar day in that form; anything else is refused before a byte is written. `--date` never supplies the time. `mark-parked` takes no `--date` — it writes a status and nothing dated.

These two are the *only* dispositions a published project has. Both refuse a project that was never published — the lifecycle opens only after publication — and, in the mirror, `mark-published` and `mark-parked` refuse a project that already is. Re-publishing without going through `mark-corrected` would record a correction as a first publication in tags and events that are never deleted; parking a published project would flip its status out of the set the published-drift lint watches (`published` and `corrected`) and quietly stop it watching the tag — which is exactly why `mark-corrected` does not: a corrected project stays watched. **The original tag is never deleted**, by either disposition or by hand: a correction adds a tag, it does not replace one. Never offer tag deletion, history rewriting, or a quiet edit of the published note as an alternative.

## Refusals and exit codes

`mark-published` and `mark-corrected` run the gate, so they answer with it: `0` done, `1` a closing check is UNMATCHED, `3` a check was UNREACHABLE so publishing waits. `mark-withdrawn` and `mark-parked` run no gate, so they only ever answer `0` or `2`. Across all four, `2` means the CLI could not carry the disposition out at all — no such project, the project has uncommitted files, a tag of that name already exists, the project was never published, the project is already published, or its name is one git cannot turn into a tag (`arm-publish` refuses that last one up front, before anyone waits on a gate run). Read the printed blockers back verbatim; do not summarize them into "it failed".

Publishing commits only the project note. If the CLI reports uncommitted files under `projects/NAME`, have the person commit them first — the published tag has to match the project the moment it is minted, or the published-drift lint reports the project as diverged.

The gate has one audited bypass, and it is the person's to ask for, never yours to suggest:

```sh
python3 -m knowledge_harness arm-publish NAME --vault PATH --bypass "why this one time"
```

The Stop hook records that token in the review inbox as an open finding. Explain that it is recorded, not forgiven, before writing it.

## Rationalizations, answered

Every act on this page is irreversible or close to it, and irreversible steps attract excuses. These are the ones that show up:

| What you're tempted to think                                                         | The mechanical rule that forbids it                                                                                                                                                                                                                                       |
| ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "They said go ahead so the ack is covered."                                          | Consent spoken in conversation writes nothing. An acknowledgment exists only once the `ack` verb has written one, with a registry reason code and a real `human:` actor — and it is scoped to the content it was granted for, so an edit to the note takes it away again. |
| "UNREACHABLE is basically fine."                                                     | It holds the gate. The check could not run, so publishing waits until it can — an outage is never a failure and never a pass, and never "probably fine".                                                                                                                  |
| "They obviously want it out — I'll pick the disposition."                            | Present exactly the three and let the person choose. Never pick for them, and never read a green gate as a decision already made.                                                                                                                                         |
| "'Drop it' is close enough to `discard`."                                            | Only the typed word `discard`, on its own, authorizes deletion. Anything less gets park or keep-draft offered instead — never infer the word from context and never type it on their behalf.                                                                              |
| "The gate refused, so nothing is armed now."                                         | A refusal leaves the gate armed and the Stop hook still holding the session. It clears when `mark-published` succeeds, or when the person asks to disarm — never by failing.                                                                                              |
| "It is already published; re-running the publish verb is simpler than a correction." | It is refused, and rightly. Re-publishing would record a correction as a first publication in tags and events that are never deleted; `mark-corrected` exists for exactly this, and keeps the project watched.                                                            |
| "They're in a hurry — I'll offer the bypass."                                        | The bypass is the person's to ask for, never yours to suggest. Offering it turns a gate the person built into a step you talked them out of, and leaves a permanent open finding behind.                                                                                  |
