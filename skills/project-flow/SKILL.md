---
name: project-flow
description: Use when a person starts a new research-vault research project, resumes an existing one, or asks to frame a research question
disable-model-invocation: true
---

# Start or resume a project

This is the real-life entry point — the project flow (question → literature → synthesis → draft → publish) starts and resumes here. In every command, `PATH` is the vault and `NAME` is the project's name under `projects/` — `brief`, not `projects/brief`.

## Orient, every time

Before framing anything or touching a draft, orient — whether this is a brand-new project or the twentieth session on an old one:

1. Read `wiki/index.md` — what topics the vault already arranges.
2. Read the recent `log/` entries — what happened lately, across every project.
3. If `projects/NAME/` already exists, read the project's files — the framed question, the draft frame, whatever is there.

### Drain the review queue

```sh
python3 -m research_vault inbox --vault PATH
```

Report the unacknowledged count and the oldest entry's date, oldest first — the Whittaker inbox-rot guard: a warn queue nobody drains is a silent failure. `inbox`'s summary reports `oldest_age_days` directly — whole days since the oldest entry, 0 for one filed today, `None` only when nothing is unacknowledged — so read that figure rather than computing the entry's age from its date yourself. When the oldest entry is old, lead with it: name it first in your summary and say plainly that it has been sitting, rather than folding it into a routine count — an aging queue earns more prominence the longer it goes untouched. This is display only; nothing here blocks on age, and the inbox stays warn-tier regardless of how old an entry gets.

Every finding in that queue is another check's non-MATCHED result — UNMATCHED, UNREACHABLE, or SKIPPED (a MATCHED result never files a finding; it mints a `verified` event instead and never appears here). Never re-derive or restate a result from a note's frontmatter yourself, and never describe an UNREACHABLE finding as a failure — it means the check could not run, not that it disagreed. If a person asks whether a citation is trustworthy, route to `verify-citations` rather than guessing from what's in the queue.

### Surface trust tiers

For every citation key the project's files cite, look up its tier:

```sh
python3 -m research_vault trust-tier CITATION_KEY --vault PATH
```

Report each cited note next to its tier — `unverified`, `machine-confirmed`, or `human-reviewed` (cumulative: human-reviewed implies machine-confirmed). This is a read-only report; it writes nothing. `unverified` is the normal starting tier, not a verdict of failure — it just means `verify-citations` has not yet run, or has not yet matched, for that note. This skill never claims a check ran that it did not; it only reads what the CLI already computed.

## Frame the question (new projects)

If `projects/NAME/` does not exist yet, frame it before anything else. Elicit — inline, in conversation, with no external reference document — exactly four elements from the person, and do not proceed to drafting or gap analysis with any of them missing:

- **The question itself** — stated plainly.
- **Scope bounds** — in/out.
- **Expected source types** — what kind of evidence will answer it.
- **Success criteria** — what a defensible answer looks like.

Write the framed question, in the person's own words, into `projects/NAME/draft.md`, starting from `system/templates/project.md` (ships `type: "project"`, `status: "draft"`). Substitute the template's `{{TITLE}}`/`{{ACTOR}}`/`{{NOW}}` placeholders rather than carrying them verbatim into durable frontmatter: `{{TITLE}}` is the project's name; `{{ACTOR}}` is the actor per §7 — `human:<id>` when a person authors the note, `<producer>/<version>` when a skill does; `{{NOW}}` comes from `python3 -c "from research_vault.notes import generated_at_now; print(generated_at_now())"`. This is authored prose, not a mechanical status write — you compose it, the person reviews it, and no CLI verb is involved. `draft.md` is the project's one `type: "project"` note — the frontmatter every later disposition (`publish`'s gate, `arm-publish`, `mark-published`, …) reads and writes; do not duplicate that frontmatter type onto any other file this skill creates in the same folder. A sibling `.md` in the same project folder (an appendix, a scratch file) still needs some non-empty `type` of its own — just not `"project"` — since `stamp-type` cannot derive one for a project-directory sibling and an untyped file blocks the commit gate (`okf-frontmatter`) with no automatic fix.

## Gap analysis (existing projects)

Once a project has a framed question, compare it against what the vault already knows — `wiki/` pages and the bibliography (`system/bibliography.json`) — and sort what you find into three buckets:

- **Covered** — the question, or a piece of it, is already answered by synthesis claims with solid backing.
- **Contested** — synthesis claims bear on the question but carry `[disputes:: ...]` links against them; surface those disputing claim links explicitly, not just the claim they attach to. Disconfirmation must be seen, never silently folded into "covered."
- **Missing** — no synthesis claim addresses this part of the question at all.

The missing bucket becomes the gap list — hand it to `find-sources` as the next step. Do not paper over a gap with an inference of your own.

## Draft frame

When it is time to draft, invoke `evidence-conventions` before writing a single claim into `projects/NAME/` — its rules govern the frame from the first line. Read and follow that skill directly; do not paraphrase or re-derive its rules here — a restatement that drifts from the guard is exactly the failure this rule exists to prevent.

## Routing

`project-flow` orchestrates; it does not do any of these itself:

| Need                                                     | Route to           |
| -------------------------------------------------------- | ------------------ |
| Acquire new sources                                      | `find-sources`     |
| Add, capture, refresh, or propagate a re-key of a source | `capture-source`   |
| Verify citations deterministically                       | `verify-citations` |
| Factcheck a draft against its sources                    | `factcheck-draft`  |
| Publish, park, correct, or withdraw                      | `publish`          |

Route the user's intent without silently broadening it. Hand the routed skill the need the person actually stated — not an enlarged version of it, and not the adjacent work you can see it will need. "Capture this paper" is not "capture it and rebuild the concept page"; "find sources" is not "find and admit them." When the stated need turns out to sit inside a larger job, say so and let the person widen it; never widen it for them and report back on work they never asked for.

## Acknowledgments

Any finding drained from the review queue is acknowledged only through the `ack` verb, with the person's own consent and reason text:

```sh
python3 -m research_vault ack FINDING-ID --vault PATH --reason "CODE free text" --actor "human:NAME"
```

Compose and explain the finding; the person consents; the CLI writes — every mechanical act in this skill (events, statuses, tags, holds, acknowledgments) is a CLI verb call.
