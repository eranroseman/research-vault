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

`verify` prints one line per non-MATCHED outcome — `RESULT check target — reason` — followed by a final JSON summary of counts by result. MATCHED outcomes never print individually (they silently mint a `verified` event instead); do not imply that "no output" for a check means it was never run — the JSON counts confirm what actually happened.

Present the printed lines to the person **grouped by check id** (the second token on each line — `citekey`, `doi`, `metadata`, `quote`, `update-notice`, `evidence-layer`, `identifier-discovery`, `web-archive`, `screening-state`, `disputed-claim`), not in raw run order — a person triaging results wants "here is everything wrong with quotes," not an interleaved dump.

| Result | Meaning |
|---|---|
| MATCHED | The check ran and agreed. The CLI appended a `verified` event; you did not, and never do. |
| UNMATCHED | The check ran and disagreed. Already recorded in the review inbox by `verify` itself — do not also file it yourself. |
| UNREACHABLE | The check could not run — a network or service outage. **Never a verdict on the work.** |
| SKIPPED | The item lacks the field the check needs (no identifier, no quote claims, …). Automatic only — never something you or the person can set. |

An outage is never a failure and never a pass. Describe an UNREACHABLE result as "could not run — outage," never as "failed," "probably fine," or any wording that reads as a verdict. Never claim a check ran that did not, and never claim a `verified` event exists unless you saw a MATCHED line's absence confirm it — only the CLI mints events, and only on a genuine MATCHED result.

## Exit codes

`0` clean (or, on the default audit surface, always — audit never fails the process). `1` a closing check is UNMATCHED (only possible with `--surface commit`/`--surface publish`). `3` a closing check was UNREACHABLE, so that surface would wait. `2` verification could not run at all — read the printed message on stderr back verbatim; do not summarize it as "it failed."

## What this skill does not do

It never files a review-inbox finding itself (`verify`'s own pipeline already does, for every non-MATCHED result) and it never runs `finding` or `ack`. Factored (LLM) verification is a different skill — `factcheck-draft` — with a different, non-blocking contract; do not conflate the two when a person asks to "check the citations."
