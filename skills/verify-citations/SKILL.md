---
name: verify-citations
description: Use when a person asks to verify citations, run the citation checks, or check whether a vault's evidence is trustworthy
disable-model-invocation: true
---

# Verify citations

This is a thin wrapper over the CLI's `verify` verb — the deterministic suite of §6 (citekey, DOI, metadata, quote, update-notice, evidence-layer, identifier-discovery, web-archive, screening-state, disputed-claim). It ships no mechanics of its own: your job is orientation, running the verb, and reporting its four-state results grouped by check id. Never hand-write a result, a `verified` event, or a review-inbox entry — the CLI does all of that already, inside `verify` itself.

## Run the audit

Default to an open audit — it reports everything and blocks nothing:

```sh
python3 -m knowledge_harness verify --vault PATH
```

This is `--surface audit`, the default. It is always safe to run: no surface closes on its result, so running it never holds a commit, a session, or a publish attempt.

Only add `--surface commit` or `--surface publish` if the person explicitly asks whether a specific gate would pass right now. Even then, this skill only **reports** that decision — it does not act as the gate. Commit-time closing runs via the pre-commit hook on its own; publish-time closing and its disposition menu belong to the `publish` skill. Do not arm, bypass, or otherwise act on a gate from here.

## Report the four states honestly

`verify` prints one line per non-MATCHED outcome — `RESULT check target — reason` — followed by a final JSON summary of counts by result. MATCHED outcomes never print individually, for every check id, whether or not they mint an event — silence about one check id in the line output is not itself news; read the JSON counts to confirm what actually ran.

Present the printed lines to the person **grouped by check id** (the second token on each line — `citekey`, `doi`, `metadata`, `quote`, `update-notice`, `evidence-layer`, `identifier-discovery`, `web-archive`, `screening-state`, `disputed-claim`), not in raw run order — a person triaging results wants "here is everything wrong with quotes," not an interleaved dump.

| Result | Meaning |
|---|---|
| MATCHED | The check ran and agreed. **Only `doi`, `metadata`, `update-notice`, and per-claim `quote` mint a `verified` event on MATCHED** — every other check id (`citekey`, `evidence-layer`, `identifier-discovery`, `web-archive`, `screening-state`, `disputed-claim`) leaves no separate durable trace beyond the run's counts. You never write an event either way. |
| UNMATCHED | The check ran and disagreed. Already recorded in the review inbox by `verify` itself — do not also file it yourself. |
| UNREACHABLE | The check could not run — a network or service outage. **Never a verdict on the work.** |
| SKIPPED | The item lacks the field the check needs (no identifier, no quote claims, …). Automatic only — never something you or the person can set. |

An outage is never a failure and never a pass. Describe an UNREACHABLE result as "could not run — outage," never as "failed," "probably fine," or any wording that reads as a verdict. Never claim a check ran that did not, and never claim a `verified` event exists for a check id that doesn't mint one — only the CLI mints events, only on a genuine MATCHED result, and only for the four check ids named above.

## Exit codes

`0` clean (or, on the default audit surface, always — audit never fails the process). `1` a closing check is UNMATCHED (only possible with `--surface commit`/`--surface publish`). `3` a closing check was UNREACHABLE, so that surface would wait. `2` verification could not run at all — read the printed message on stderr back verbatim; do not summarize it as "it failed."

## What this skill does not do

It never files a review-inbox finding itself (`verify`'s own pipeline already does, for every non-MATCHED result) and it never runs `finding` or `ack`. Factored (LLM) verification is a different skill — `factcheck-draft` — with a different, non-blocking contract; do not conflate the two when a person asks to "check the citations."
