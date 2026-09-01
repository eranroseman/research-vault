# Transcript-archive mining record — the 63-session export, mined then discarded

**Status (2026-09-01):** MINED — DISCARDED. The one-time transcript export tracked (post-sweep,
2026-08-30) at `docs/research/raw/research-vault-transcripts/` was mined per
[#68](https://github.com/eranroseman/knowledge-harness/issues/68) and deleted in the same commit
that added this record. Authentic pre-sweep bytes remain retrievable at commit `e900dfa` (path
`research/raw/knowledge-harness-transcripts/`); they hash-match the
[fixity manifest](2026-08-25-transcript-archive-manifest.md) 63/63.

What this record is: the durable replacement for the discarded raw export. Every finding below
carries provenance (session file id + UTC message timestamp, resolvable against the authentic
bytes at `e900dfa`); the instruments are named so the mining is checkable; the disposition
states exactly what was deleted and what survives where. What it is not: a transcript dump.
The early-turn detail of the four compaction-capped main-session files survives only as the
compaction summaries; nothing here re-quotes beyond what those held.

## Instruments

- **Authentic bytes.** The export landed 2026-08-25 in `e900dfa` ("the project's process lab
  notebook, preserved per the standing recommendation"). The tracked HEAD copies were rewritten
  by the knowledge-harness → research-vault sweep (`da637c9`, 2026-08-30) under the
  renames-sweep ruling (docs/terminology.md §1, #87). Mining used the `e900dfa` blobs — the
  bytes the manifest authenticates — not HEAD's.
- **Extraction.** Per file: user-side messages only — human text, typed slash commands,
  cross-session relays, compaction handoffs — each with its timestamp; tool results, IDE/task
  notifications, hook enqueues (540 entries) dropped as noise. "Enough assistant context" = a
  one-line snippet after each user message, never independent evidence.
- **Lineage and dedup.** Resume-copies regenerate message uuids (a uuid-prefix lineage finds
  nothing) but preserve (timestamp, text) and embedded task ids; lineage was therefore computed
  content-wise. Dedup key: exact (timestamp, text), earliest-frozen file wins — 1,000
  resume-duplicates collapsed into 689 unique main-cluster messages; 992 unique user-side
  messages across the whole export.

## Lineage map — 63 sessions

One multi-day main controller session (4 files), 44 independent side sessions, 15 hook-spawned
machine sessions with zero human turns (SDK-spawned security reviews, "entrypoint":"sdk-py";
their "user" messages are enqueued diffs, not author voice). No session shares content with
another except the four main-cluster files; the 59 others are content-independent.

| file       | kind                                     | first (UTC)      | last (UTC)       | msgs | noise | compacts | bytes    | title                                          |
| ---------- | ---------------------------------------- | ---------------- | ---------------- | ---- | ----- | -------- | -------- | ---------------------------------------------- |
| `2e6f1385` | main-session member                      | 2026-08-16T04:31 | 2026-08-25T21:11 | 649  | 98    | 3        | 31928261 |                                                |
| `6253e249` | main-session member                      | 2026-08-16T04:31 | 2026-08-21T19:00 | 180  | 33    | 1        | 9106699  |                                                |
| `b1fcd241` | main-session member                      | 2026-08-16T04:31 | 2026-08-23T20:26 | 443  | 87    | 2        | 22843058 | Redesign harness for knowledge work productivi |
| `f5219270` | main-session member                      | 2026-08-16T04:31 | 2026-08-23T22:15 | 417  | 53    | 2        | 19095958 |                                                |
| `3605faa4` | independent session                      | 2026-08-21T04:36 | 2026-08-21T14:23 | 2    | 28    | 0        | 1551911  | Plan C scaffold enforcement                    |
| `4abe1fa7` | independent session                      | 2026-08-21T14:22 | 2026-08-21T15:08 | 4    | 38    | 0        | 2314519  | Superpowers subagent-driven development        |
| `e4fd8696` | independent session                      | 2026-08-21T18:18 | 2026-08-21T20:26 | 8    | 2     | 0        | 2913325  | Ponytail audit core                            |
| `3e0d19d7` | independent session                      | 2026-08-21T18:50 | 2026-08-21T18:50 | 1    | 0     | 0        | 177345   | @core/ structure analysis                      |
| `9df75b39` | independent session                      | 2026-08-21T19:14 | 2026-08-21T19:14 | 1    | 0     | 0        | 422409   | Core naming conventions analysis               |
| `90b05287` | independent session                      | 2026-08-21T19:44 | 2026-08-21T19:47 | 2    | 0     | 0        | 290149   | Repository organization analysis               |
| `cde0aaec` | independent session                      | 2026-08-21T21:08 | 2026-08-21T21:08 | 1    | 1     | 0        | 633559   | Plan L layout flip                             |
| `7ad21fe6` | independent session                      | 2026-08-21T22:24 | 2026-08-21T23:17 | 3    | 2     | 0        | 610301   | Vault agents template revision                 |
| `78e32f92` | independent session                      | 2026-08-21T22:43 | 2026-08-21T23:27 | 3    | 3     | 0        | 593419   | Package rename                                 |
| `84b9b138` | independent session                      | 2026-08-21T23:23 | 2026-08-22T00:02 | 2    | 2     | 0        | 898766   | Selector escape hardening                      |
| `17ddee07` | independent session                      | 2026-08-22T02:03 | 2026-08-22T02:03 | 1    | 33    | 0        | 2454200  | Subagent-driven development                    |
| `1a9bb5a5` | independent session                      | 2026-08-22T15:40 | 2026-08-22T15:40 | 1    | 0     | 0        | 137482   | Ponytail review                                |
| `6b816c8f` | independent session                      | 2026-08-22T15:43 | 2026-08-22T15:54 | 2    | 1     | 0        | 427733   | Ponytail review                                |
| `8dbe64c9` | independent session                      | 2026-08-22T16:07 | 2026-08-22T16:40 | 5    | 0     | 0        | 1636627  | @skills in-depth analysis                      |
| `2193ae86` | independent session                      | 2026-08-22T20:11 | 2026-08-22T20:11 | 1    | 0     | 0        | 60050    | Pytest runtime                                 |
| `b92b8e8c` | independent session                      | 2026-08-22T21:52 | 2026-08-22T22:07 | 6    | 4     | 0        | 718557   | Skills coverage comparison with research files |
| `7c5f56a9` | independent session                      | 2026-08-22T22:09 | 2026-08-22T22:09 | 1    | 0     | 0        | 935627   | Comparable products from prior art research    |
| `0f009656` | independent session                      | 2026-08-22T22:14 | 2026-08-23T17:38 | 64   | 11    | 0        | 5869302  | Comparable products analysis                   |
| `854bd1f1` | independent session                      | 2026-08-23T04:15 | 2026-08-23T20:27 | 22   | 43    | 0        | 3466505  | 2026-08-20 plan Q quality lane                 |
| `a89fa797` | independent session                      | 2026-08-23T20:28 | 2026-08-24T13:39 | 43   | 21    | 0        | 2614148  | Foundation spec ADR and context review         |
| `ceeb9ed7` | independent session                      | 2026-08-24T01:15 | 2026-08-24T01:25 | 3    | 3     | 0        | 239721   | Superpowers specs and plans cleanup            |
| `ed32a3f5` | independent session                      | 2026-08-24T01:21 | 2026-08-24T01:21 | 1    | 0     | 0        | 124565   | Setup Matt Pocock skills                       |
| `0b0be296` | independent session                      | 2026-08-24T01:27 | 2026-08-24T01:41 | 3    | 2     | 0        | 123212   | Scan docs research analysis for deletable file |
| `c84f659a` | independent session                      | 2026-08-24T01:42 | 2026-08-24T01:52 | 6    | 0     | 0        | 905706   | Documentation organization review              |
| `c18f4c28` | independent session                      | 2026-08-24T03:21 | 2026-08-24T03:24 | 3    | 0     | 0        | 190405   | Delete .claude/worktrees/build+quality-lane    |
| `1bd3c5cd` | independent session                      | 2026-08-24T14:22 | 2026-08-24T14:28 | 3    | 0     | 0        | 201529   | CONTEXT.md domain modeling review              |
| `9a90b8a7` | independent session                      | 2026-08-24T14:41 | 2026-08-24T14:54 | 3    | 5     | 0        | 489269   | Writing for agents documentation               |
| `27824b73` | independent session                      | 2026-08-24T14:58 | 2026-08-24T14:58 | 1    | 0     | 0        | 120765   | Writing for agents docs/testing.md             |
| `dbde8db2` | independent session                      | 2026-08-24T14:59 | 2026-08-24T14:59 | 2    | 1     | 0        | 297186   | Pytest runtime optimization                    |
| `67d2e84c` | independent session                      | 2026-08-24T15:17 | 2026-08-24T15:17 | 1    | 0     | 0        | 591763   | Vault skills and agents prose refactoring      |
| `13139c53` | independent session                      | 2026-08-24T15:31 | 2026-08-24T15:40 | 2    | 0     | 0        | 260225   | Writing for agents                             |
| `87284ffe` | independent session                      | 2026-08-24T15:43 | 2026-08-24T16:19 | 6    | 0     | 0        | 999554   | Vale.sh evaluation                             |
| `cb5ecedf` | independent session                      | 2026-08-24T16:23 | 2026-08-24T17:19 | 8    | 0     | 0        | 866817   | Dependency and tooling versions                |
| `d7f1d4ff` | independent session                      | 2026-08-24T17:32 | 2026-08-25T20:32 | 8    | 0     | 0        | 1582551  |                                                |
| `239f54c7` | independent session                      | 2026-08-24T18:02 | 2026-08-24T18:24 | 9    | 1     | 0        | 440849   | Claude code inter-instance communication       |
| `e322c366` | independent session                      | 2026-08-24T18:33 | 2026-08-24T18:58 | 11   | 2     | 0        | 475691   | Python libraries for summary quality evaluatio |
| `b36beb72` | independent session                      | 2026-08-24T19:14 | 2026-08-24T20:01 | 18   | 10    | 0        | 2312257  | Skills system mechanisms and validation        |
| `f9a674e2` | independent session                      | 2026-08-24T21:18 | 2026-08-24T22:21 | 13   | 6     | 0        | 1193069  | Zotero fulltext endpoint                       |
| `7ce655e7` | independent session                      | 2026-08-24T22:30 | 2026-08-24T23:05 | 12   | 0     | 0        | 2619146  | Historian notetaking workflow comparison       |
| `f0d18dbc` | independent session                      | 2026-08-24T23:23 | 2026-08-24T23:44 | 5    | 2     | 0        | 326317   | Settings and config drift resolution           |
| `b3d6fbc7` | independent session                      | 2026-08-24T23:45 | 2026-08-24T23:57 | 3    | 0     | 0        | 493355   | Writing for agents                             |
| `ff9c235b` | independent session                      | 2026-08-25T20:04 | 2026-08-25T20:49 | 7    | 2     | 0        | 611681   | Rethink audit docs/product-landscape/2026-08-2 |
| `9fb523ad` | independent session                      | 2026-08-25T20:33 | 2026-08-25T20:33 | 1    | 3     | 0        | 784200   | 2026-08-25 plugin development process reconstr |
| `d5dcfa17` | independent session                      | 2026-08-25T20:35 | 2026-08-25T20:35 | 1    | 11    | 0        | 663837   | Rethink audit controller protocol material     |
| `0c18cd3a` | machine — hook-spawned, zero human turns | —                | —                | 0    | 2     | 0        | 36308    | Review test template changes for security      |
| `165542b6` | machine — hook-spawned, zero human turns | —                | —                | 0    | 2     | 0        | 36877    | Review test templates for security vulnerabili |
| `2e161431` | machine — hook-spawned, zero human turns | —                | —                | 0    | 2     | 0        | 55039    | Review VSCode config and documentation path ch |
| `47ba4435` | machine — hook-spawned, zero human turns | —                | —                | 0    | 2     | 0        | 50968    | Review glossary documentation formatting chang |
| `57e834b0` | machine — hook-spawned, zero human turns | —                | —                | 0    | 3     | 0        | 398109   | Review refactoring changes for security        |
| `78b5ebf5` | machine — hook-spawned, zero human turns | —                | —                | 0    | 2     | 0        | 98293    | Review config documentation cleanup for securi |
| `8035e83a` | machine — hook-spawned, zero human turns | —                | —                | 0    | 2     | 0        | 220038   | Rename harness_core package to knowledge_harne |
| `97434ebe` | machine — hook-spawned, zero human turns | —                | —                | 0    | 2     | 0        | 24249    | Review test change for security vulnerabilitie |
| `c5756684` | machine — hook-spawned, zero human turns | —                | —                | 0    | 2     | 0        | 737752   | Review security changes in knowledge harness c |
| `c6c7b4d1` | machine — hook-spawned, zero human turns | —                | —                | 0    | 2     | 0        | 56737    | Review vault agents test security changes      |
| `c831a602` | machine — hook-spawned, zero human turns | —                | —                | 0    | 2     | 0        | 25819    | Review security vulnerabilities in VSCode sett |
| `d526fd43` | machine — hook-spawned, zero human turns | —                | —                | 0    | 2     | 0        | 272157   | Review security vulnerabilities in refactored  |
| `eb7466da` | machine — hook-spawned, zero human turns | —                | —                | 0    | 3     | 0        | 690147   | Review security vulnerabilities in verificatio |
| `f45a1ce5` | machine — hook-spawned, zero human turns | —                | —                | 0    | 2     | 0        | 43005    | Review config test security vulnerabilities    |
| `ff8ab652` | machine — hook-spawned, zero human turns | —                | —                | 0    | 2     | 0        | 35900    | Review security vulnerabilities in pyproject.t |

**The main-session cluster** (all first-message 2026-08-16T04:31Z — the same kickoff, linked by
resume/replay):

- `6253e249` — earliest leg; own messages end 08-21 19:00.
- `b1fcd241` — continuation carrying replayed history; ran to 08-23 20:26; shares 178 messages
  with `6253e249`.
- `f5219270` — rewind-fork from `b1fcd241` at message ~405 (does not contain its last 38);
  owns 12 messages, ended 08-23 22:43.
- `2e6f1385` — continuation of `f5219270` (full 417-message prefix); surviving tail to 08-25
  21:11; owns 232 messages; three in-place compactions along the way.

```text
MAIN controller session (4 files, resumed/replayed)
├── 6253e249  — 08-16 04:31 → 08-21 19:00 (213 msgs, 2 compaction handoffs)
├── b1fcd241  — carries 178 replayed msgs of 6253e249; runs to 08-23 20:26
│   └── f5219270 — rewind-fork of b1fcd241 at msg ~405; runs to 08-23 22:43
│       └── 2e6f1385 — full-prefix continuation of f5219270; to 08-25 21:11 (3 compactions)
44 independent side sessions — 08-21 … 08-25, 1–64 user-side msgs each (303 total)
15 machine sessions — hook-spawned security reviews, zero human turns
```

The 44 side sessions span 08-21 → 08-25 with 1–64 user-side messages each (303 total); the 15
machine sessions are the review-request queue's own sessions, listed in the table above.

## Instrument findings (about the archive itself)

- **A1 — the sweep invalidated the fixity manifest at HEAD (correction, manifest).** The
  renames-sweep ruling (#87: "renames sweep the historical record") executed by #90 (`da637c9`)
  rewrote the transcripts' message text in place — long-form names only: `2e6f1385` had 23,485
  `knowledge-harness` occurrences at `e900dfa`, 814 at HEAD, while `kh` short forms were
  untouched (2,536 = 2,536). 57 of 63 manifest hashes therefore authenticate only the `e900dfa`
  bytes; the 6 that still match had no message-text targets (their tool-result payloads kept
  the era's remote URL verbatim, e.g. `e322c366`'s push stdout). The manifest — whose stated
  role is "process claims cite a transcript by session id + SHA-256" — was never re-baselined.
  Consequence adopted: hash-citations resolve against `e900dfa`; the manifest header now says
  so. A fixity manifest is a measurement; rewriting its measured object invalidates the
  measurement, whatever the sweep ruling says about the records themselves. If a future record
  needs byte-proof authenticity (ADR 0002's domain), exclusion from sweeps is part of its
  design.
- **A2 — "Source snapshot commit: e45c976" does not resolve in this repository** (checked
  `git fetch origin` then `git cat-file -t e45c976`: no object with that prefix exists in any
  local ref; the export landed at `e900dfa`, parent `cca397a`). Most plausibly a commit in the
  discarded external clone, gone with it. The manifest's snapshot anchor is now `e900dfa`.
- **A3 — 15 of the 63 files are machine sessions.** Hook/SDK-spawned security-review sessions
  (the "Review this change for security vulnerabilities… Investigate per the method in your
  instructions" prompt, `promptSource: sdk`, `entrypoint: sdk-py`). Zero human turns; they
  contain no decisional user material. Their existence documents the review-request machinery
  the ask-matt/superpowers-hooks investigation (08-28) already banked as evidence-source.
- **A4 — the archive's content is ~half one session.** The main controller session's four
  files carry 689 of the export's 992 unique user-side messages (69%). The marginal value of
  the export concentrates there and in the 08-24 side sessions.

## Findings — decisional material recovered from the early stage

The early era (08-16 → 08-20) is almost entirely banked: the wayfinder ledger, spec, ADRs,
and terminology absorbed it. The un-banked margin concentrates in 08-21 → 08-25, and most of
it is *method*: rulings about how rulings are made, sharpened live, never distilled. Findings
are grouped by durable home below; every one carries provenance.

### Already-distilled this run (recorded here, no further action)

01. **`R` The pin-vs-narrow decision trio.** When a claim and reality disagree: *weaken the
    claim* (no mechanism worth building), *strengthen reality* (mechanism is cheap), or *state
    the exception* (the deviation is correct) — with each direction's failure mode named
    ("narrow everything and you document a weak system honestly; strengthen everything and you
    relitigate settled design to save a sentence; excuse everything and the exception list
    becomes the system"). Three instances in one day, one per direction.
    Provenance: `2e6f1385` @ 2026-08-24T16:50:34Z, @ 16:58:11Z (of: `b1fcd241`/`f5219270`
    lineage files at `e900dfa`).
02. **`R` The correction-vs-decision test.** "Would this decision exist if the agent had simply
    done the obvious thing? If not, it is a correction, not a decision." Killed a five-ADR slate
    ("an agent proposed 170 confirmations, you said no, the agent wrote the correction into the
    spec as a 'ruling', and I harvested the ruling as an ADR… doctrine manufactured from one
    agent's mistake") and the same shape twice more.
    Provenance: `2e6f1385` @ 2026-08-24T13:19:31Z.
03. **`R` The ADR routing doctrine.** "Rules agents follow go where agents read them; invariants
    code must hold go in tests that name the reason; an ADR is only for a choice a future
    designer would otherwise reverse without knowing what it cost." Plus the two learned
    kill-tests for the ADR bar: textbook/received-wisdom doctrine fails the surprise test, and a
    ruling that exists only because an agent first did something bad does not harvest as
    doctrine.
    Provenance: `2e6f1385` @ 2026-08-24T13:41:42Z, @ 12:43:37Z.
04. **`R` "No homebrew changes to a third-party skill."** Ruled twice in one day against
    extending `/domain-modeling`'s ADR bar: "we follow the skill to the letter, no homebrew
    addition or changes."
    Provenance: `b1fcd241`/`f5219270` @ 2026-08-23T18:56:14Z, @ 19:07:11Z.
05. **`P` Fresh-context preference for high-stakes prose.** "Please spin a fresh subagent to
    edit these files. Your context window makes them barely readable" then "scrap all adr
    proposal. I'll open a new session for it" — layered-edit degradation is treated as a real
    constraint on judgment work, and fresh-context agents are the fix.
    Provenance: `b1fcd241`/`f5219270` @ 2026-08-23T20:07:10Z, @ 20:19:23Z.
06. **`R` "Forced human gates become rubber stamps."** "We won't make sure we don't create any
    of those" — the 170-click admission session as the harness's first rubber-stamp factory;
    habituation transfers ("a user trained to click through admission clicks through the publish
    gate"). Later sharpened to the grouping principle: "judgment calls should be grouped
    together as much as possible to prevent rubber stamping."
    Provenance: `b1fcd241` @ 2026-08-22T19:33:27Z; `b1fcd241` @ 2026-08-23T19:52:38Z.
07. **`M` The filter-repo history purge (2026-08-23) — the largest unrecorded event.** All
    draft ADRs (`docs/adr/0004-*`–`0008-*`) purged from history with git filter-repo and
    force-pushed; hashes changed `ab31984` → `25c2b23`; the stale-clone hazard and the recovery
    protocol (rebase `--onto`, purged-path grep must print nothing, ff-only push, old
    merge/pull forbidden) were written as a ruling. The banked reconstruction records only
    "three proposed ADRs scrapped" (5ad05a0); none of the mechanics is in it. Predates the
    record-immutability gate work (#28) without being reconciled with it.
    Provenance: `b1fcd241`/`f5219270` @ 2026-08-23T20:22:38Z, @ 20:26:32Z; `f5219270` @
    2026-08-23T20:42:41Z.
08. **`R` "Refutations need instruments as much as claims do."** A refutation holds only if the
    check could have seen the mechanism ("the collection-time hypothesis was reported refuted by
    a check that could only see direct references, and it took the isolation replay to overturn
    the refutation"); a prediction that failed for an unrelated reason goes back to open.
    Provenance: `854bd1f1` @ 2026-08-23T16:55:00Z, @ 17:20:24Z (side session).
09. **`R` The decision-persistence bar.** "A deliberate hardening stands until real friction
    produces evidence against it" — reversal without a driving case is un-deciding, not
    deciding; revisitable only when the validation slice actually hits it.
    Provenance: `3605faa4` @ 2026-08-21T14:23:54Z (side session).
10. **`R` Over-engineering-audit triage doctrine.** Write-only-today is not dead-code when the
    reader is a scheduled future phase ("phase-dead, not design-dead"); audits cannot un-decide
    ruled contracts ("out of the audit's jurisdiction"); trust-path metric swaps are never
    acceptable from a cleanup pass (the 0.90 threshold "belongs to the deliberate calibration
    task… never to a lint pass"). Feeds the banked #42 audit directly.
    Provenance: `e4fd8696` @ 2026-08-21T18:45:06Z (side session).
11. **`R` "A correct observation can carry a wrong conclusion, and the observation's honesty
    is what makes the conclusion persuasive."** Self-reports are worth more than silence *and*
    still need checking — "those aren't in tension." Companion fact: a 100%-branch-coverage
    number can be true and misleading (short-circuit sub-expressions invisible to the metric's
    model).
    Provenance: `2e6f1385` @ 2026-08-25T05:58:25Z, @ 04:55:44Z.
12. **`R` The no-observed-failure bar.** A trap/branch/trigger clause may be advertised in
    pointer lines only after an observed failure, never on theoretical risk ("we established
    the no-observed-failure bar for exactly this question").
    Provenance: `13139c53` @ 2026-08-24T15:40:48Z (side session).
13. **`M` Boundary-review record class + standing reviewer role.** Independent review reports
    are a named record class (committed, never left in `/tmp`, header naming observer, method,
    date, branch state reviewed); one reviewer session holds a standing boundary-review seat
    across batch phases; the reviewer's own "working well" list is promoted to the bar.
    Provenance: `d7f1d4ff` @ 2026-08-24T17:49:30Z (side session).
14. **`R` The vault trust gate refused its own author's live-vault commit — unbypassed.** A
    legitimate template-apply into `~/kh-vault` was refused because the user's own uncommitted
    machine-record files differed; resolved by committing those first, no `--no-verify`
    anywhere: "the gate working, not failing… being on the receiving end doesn't change the
    verdict."
    Provenance: `2e6f1385` @ 2026-08-25T13:26:11Z.
15. **`M` Venv parity discipline.** Main's venv validates main; each worktree's venv validates
    its branch; environment upgrades were deferred to keep the seats' greens comparable.
    Provenance: `cb5ecedf` @ 2026-08-24T16:30:23Z (side session).
16. **`M` Batch seats were separate VS Code instances over cc-socks.** Opaque `new-folder-XX`
    names, built-in `SendMessage` traffic over `uds:…/cc-socks/*.sock`; a global SessionStart
    self-naming hook trial was vetoed minutes after it was added.
    Provenance: `239f54c7` @ 2026-08-24T18:24:33Z, `7ce655e7` @ 23:05:22Z (side sessions).
17. **`R` Judgment where the answer is determined is not overreach.** A retroactive
    self-flag for acting without a further ask, where an earlier ruling already determined the
    answer, was overruled.
    Provenance: `87284ffe` @ 2026-08-24T16:05:58Z (side session).
18. **`P` In-flight plans never pause; planning assumes them complete.** "We won't stop Q mid
    flight. For planning purposes we can assume Q is done" — plus the same-hour push-back that
    adopt-vs-build evaluation is never deferred on completion.
    Provenance: `0f009656` @ 2026-08-23T04:38:18Z, @ 04:32:50Z (side session).
19. **`P` Approvals bind exactly the question asked.** "I didn't ask you to provide a new edit
    of the reports"; "no. I just approve the use of summary as proposed" — approvals never
    bundle; artifacts only on request.
    Provenance: `b92b8e8c` @ 2026-08-22T22:04:32Z; `a89fa797` @ 2026-08-24T00:50:25Z (side
    sessions).
20. **`P` Comparative analyses must re-derive from primary sources.** "DO NOT READ THE CONTENT
    OF THESE DOCUMENTS OR ANY OTHER DOCUMENT IN THIS REPO… base your comparison only on
    information from these repos" — in-repo prior prose is inadmissible for comparative claims.
    Provenance: `0f009656` @ 2026-08-22T22:14:33Z (side session).
21. **`P` The AGENTS.md economy.** "Does it worth the cost of having it loaded to the context
    window of every agent ever"; "a line returns only with a named incident behind it"; "clutter
    accumulated in AGENTS.md makes agents make wrong decisions… stale law beats correct
    reasoning, because agents read that file as law."
    Provenance: `b1fcd241` @ 2026-08-21T20:37:54Z → @ 20:52:57Z.
22. **`P` Mirror discipline across harnesses.** Word-for-word duplicated sections across
    `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md` are intentional ("neither harness reads the
    other's file"); extraction into a shared source was explicitly declined. Process rules
    belong at user level ("process belongs to user, not project"), backed by harness-backup.
    Provenance: `f0d18dbc` @ 2026-08-24T23:44:20Z; `d7f1d4ff` @ 23:23:34Z (side sessions).
23. **`R` The "comment doctrine."** Probe/provenance detail (probe-verified, dates) belongs in
    the commit body, not the code comment, because "plans are decision records, skill comments
    aren't"; author-approved implementer wording beats byte-alignment to plan text.
    Provenance: `d7f1d4ff` @ 2026-08-24T18:15:34Z (side session).
24. **`E` Interpreter policy.** Everything develops and verifies on Python 3.12.3; 3.13/3.14
    declined "until post-slice, with the deepening pass" as a natural revisit.
    Provenance: `cb5ecedf` @ 2026-08-24T16:30:23Z (side session).
25. **`P` Standing no-redundancy restructure after append-only drafting.** Issued verbatim
    three times in one evening: "ensure the content of your doc is presented in a logical and
    easy to follow way with no redundant information."
    Provenance: `b36beb72` @ 2026-08-24T19:43:08Z; `7ce655e7` @ 22:51:43Z (side sessions).
26. **`P` Human full-text fallback.** "If you give me doi or arxiv I can get you the full
    text" — a standing human-in-the-loop escalation when acquisition hits a paywalled source.
    Provenance: `b36beb72` @ 2026-08-24T19:20:13Z (side session).
27. **`R` Superpowers plans are temporary.** "Superpowers specs and plans are intended to be
    temporary files that are deleted after implementation" — acted on (14 files deleted the
    same night), recorded nowhere.
    Provenance: `ceeb9ed7` @ 2026-08-24T01:16:38Z (side session).

### Corrected this run (targeted durable-home amendments, this commit)

28. **`C` The plugin-layering prior-art doc still ships the refuted "nocoders" claim.**
    `docs/product-landscape/2026-08-25-plugin-layering-prior-art.md` §1 asserts "**both argue
    against composing them**" and frames nocoders.com as stating the decision as exclusive; the
    author's own verification: "nocoders.com is a neutral comparison that explicitly says
    'neither bet is wrong' and never discusses combining." The file also presents the obra
    #1007 close reason without provenance. Filed as issue (see below); the dated correction
    block goes in the file.
    Provenance: `ff9c235b` @ 2026-08-25T20:49:58Z (side session).
29. **`C` ADR-authoring rules belong in `docs/agents/domain.md`.** The shape rules of the
    accepted ADRs (13–33 lines) were ruled in-chat and never distilled: cut what a working
    reader already knows; never cite records the reader cannot open — assert borrowed reasoning
    on its own merits; titles must carry the decision, not a truism; "ADRs carry no history"
    (only a commit message); prefer one sentence in an existing ADR or vault AGENTS.md over a
    new file. Amended into domain.md this commit.
    Provenance: `a89fa797` @ 2026-08-24T01:09:30Z, @ 00:56:32Z, @ 13:32:40Z, @ 22:39:54Z (side
    session).
30. **`C` The record-immutability gate's two discovered limitations.** (a) `research/`
    appends are `M` and fail the hook on feature branches — "there is no append-shaped
    escape"; every in-record append must land on main directly. (b) The hook compares
    `origin/main...HEAD`, so pushing makes it pass — it never protects merged history, and its
    git-failure path green-lights on an empty `touched`. Both feed #28 (commented there).
    Provenance: `2e6f1385` @ 2026-08-24T18:13:15Z; `2e6f1385` @ 2026-08-25T20:36:13Z.
31. **`E` The WSL2 low-port trap.** WSL2 swallows RST on low ports, so connections to
    `127.0.0.1:1` hang to a full 5s timeout — three dead-port tests were ~15s of a 67s serial
    run. Absent from docs/environment.md and docs/testing.md. Added as a dated line.
    Provenance: `2e6f1385` @ 2026-08-24T15:15:14Z.
32. **`C` Register item 12 executed.** `docs/product-landscape/2026-08-25-coding-companion- plugins-comparison.md` item 12 (transcript mining and disposal) is now executed; the entry
    points at this record.
    Provenance: this mining run, 2026-09-01.

### Leads filed this run

33. **`L` Issue — superpowers plans lifecycle + backlog prune.** The temporary-files ruling
    (finding 27) has no durable home; `docs/superpowers/plans/2026-08-22-post-q-batch.md`
    still sits in the tree as a completed plan with no recorded disposition.
34. **`L` Issue — nocoders correction block** (finding 28).

## Disposition

- Deleted at HEAD: `docs/research/raw/research-vault-transcripts/` — all 63 session files and
  its README. This record replaces it.
- Survives: authentic bytes at `e900dfa` (git history of this private repo); the fixity
  manifest (updated header below) as the citable inventory of what the archive was; this record
  as the durable home of the mine's output.
- The redundant external clone at `~/knowledge-harness-transcripts` was verified absent
  (2026-09-01 filesystem sweep: `~/`, `/mnt/c` to depth 3, all of `/home/eranr`).
- Raw export bytes remain reachable in git history at `e900dfa`; deletion at HEAD removes them
  from the working tree and from any future clone of the current repo state. That is the
  intended meaning of "discard" here.
