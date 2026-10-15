# Real-material session, 0.2.0, run 1: an amendment on the author's own project

- Date: 2026-10-15.
- Plugin commit: `5e13529`, loaded with `--plugin-dir "$P"` where `P` is `<checkout>/plugins/experiment-proposal`. The installed `experiment-proposal@research-vault` (0.1.0) was present; the collision probe in `delegation-v2-1.md` shows the `--plugin-dir` copy wins.
- Host: Claude Code 2.1.273, model `opus`.
- Project: `~/bloom-length-pilot`, approved by the user for this run. It is a git repository on branch `master`. Raw output of each turn is kept outside the repository (`/tmp/ep-eval/real-material/turn1.jsonl`, `turn2.jsonl`, `turn3.jsonl`).
- Kind of record: no bar. It records what the skill did on a brief frozen under checklist 0.1.0.
- Scope rule I kept: the only change allowed in the project was the skill's own amendment, appended to `proposal/design-brief.md` and committed with a pathspec on that file. I ran no `git add`, `stash`, `reset`, `checkout` or clean there, did not touch `logs/` or `proposal/ethics-review.md`, and did not edit the brief myself.

## State before

```text
$ git status --porcelain
?? logs/
?? proposal/ethics-review.md
$ git log --oneline -3
a35227c Freeze the design brief
b706402 Idea and references
```

Before the first turn I also took sha256 sums of `proposal/design-brief.md`, `proposal/ethics-review.md`, `proposal/power.R` and every file under `logs/` (58 files in all), outside the project, to compare afterwards. The brief's header: `Draft: proposal/draft.md`, `Status: frozen 2026-10-14`, `Checklist: experiment-proposal 0.1.0`; 284 lines, 32 entries under Decisions (29 `provisional`, 3 `settled`).

## Commands

Every turn ran from the project, stdin from `/dev/null`, raw stream saved:

```text
$ cd ~/bloom-length-pilot && claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "/experiment-proposal:design"
$ cd ~/bloom-length-pilot && claude -p --continue --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "<answer>"
```

The three prompts: `/experiment-proposal:design`; then the user's amendment request verbatim ("Retire the power entries: items 8.5, 8.6 and 8.7 are superseded by the 0.2.0 checklist; item 8.5 now reads: four participants in the pilot, set by the course term; a full study would follow MacKenzie-style device comparisons at 12 to 24."); then "Yes, keep the refinement clause. Leave item 6.6 and Open items 13 and 14 alone; no further amendments, and the MacKenzie lit-search is for later. OK to commit the amendment." Exit codes 0, 0, 0; stderr files empty; no permission denial in turn 3.

## Turn 1: the skill finds the frozen brief

Decisive reply (quoted):

> Brief frozen (`frozen 2026-10-14`, commit `a35227c`, checklist 0.1.0). Checker passes — header and Amendments only get checked on an old-checklist brief, frozen entries stay as they are.
>
> So: amend mode. Every entry counts as settled now, including the 16 provisional ones. [...]
>
> **What do you want to change?** Name the item and the new decision [...]

It read the checklist, `references/brief.md` and the brief, ran the checker, asked what to amend (step 8 as expected), and offered to read `proposal/ethics-review.md` only if the changes came from it ("otherwise I leave it closed"). It did not read `logs/`. The checker output it saw was the single stderr line below. Its sentence "the 16 provisional ones" does not match the file: 29 entries are `provisional`, and the Open items list has 18 numbered lines (6 of them of the form `Item ... provisional`). A miscount in its chat, not in the brief.

Harness effects (not plugin behaviour): with `--allowedTools` as given, two Bash calls were refused. `cat` of the plugin's `plugin.json` ("may only concatenate files from the allowed working directories"), and a checker call chained with `; echo "exit: $?"`. The skill went around both (a `python3 -c` read of `plugin.json`, the checker alone); `Read` of plugin files outside the project worked throughout.

## Turn 2: the amendment is appended

The skill first said that the checker "validates the header and Amendments only, and the amendment heading regex doesn't test item IDs against 0.2.0 — so retiring 8.6 and 8.7 by amendment passes shape", and that it had carried a refinement clause for item 8.5 forward from the frozen item 2.3 because 0.2.0's item 8.5 asks how the pilot refines the count and the user's words did not say. It then made one `Edit` to `proposal/design-brief.md`: the old string was the last Open items line (unchanged) and the new string that line plus the new section, so no existing text changed (`git diff`: 17 insertions, 0 deletions). The checker was re-run: the same single stderr line and nothing else.

Its reply (quoted in part): "Three amendment blocks appended, brief not yet committed", a summary of 8.5, 8.6 and 8.7, then:

> One line needs your yes before I commit. The refinement clause is mine, not yours: "The pilot refines that count by measuring the achieved length contrast and the spread of the primary composite, as item 2.3 records."

It also said it left alone "Frozen entries 2.3, 2.4, 6.7 and 11.x, plus Open items 13, 14 and 16", which "still cite 'item 8.5's computed count of 24' and the power run", because frozen text is a record; it asked whether item 6.6 and Open items 13 and 14 should be amended ("6.6 is not a 0.2.0 item either"), and said MacKenzie is not in `references/`, suggesting `/experiment-proposal:lit-search`. It named the commit it would make: `git commit -m "Amend the design brief: items 8.5, 8.6 and 8.7" -- proposal/design-brief.md`.

## Turn 3: the OK and the commit

After "Yes, keep the refinement clause [...] OK to commit", the skill made one more `Edit` (inside its own uncommitted amendment, not a frozen entry) replacing the Reason tail of the 8.5 block with `accepted recommendation: carried from item 2.3` as it had promised, re-ran the checker (same single stderr line), and ran exactly `git commit -m "Amend the design brief: items 8.5, 8.6 and 8.7" -- proposal/design-brief.md`. Its closing summary named `f77af3d`, one file, 17 insertions, and stated that `logs/` and `proposal/ethics-review.md` stayed untracked.

## The amendment block as committed

```markdown
## Amendments

### 2026-10-15, item 8.5, the count justified by similar experiments rather than by a power analysis
- New decision: Four participants in the pilot, pre-specified, set by the course term as a resource limit named as such. A full study would follow MacKenzie-style device comparisons at 12 to 24 participants, which replaces the power analysis's 24 as the justification. The pilot refines that count by measuring the achieved length contrast and the spread of the primary composite, as item 2.3 records.
- Reason: "item 8.5 now reads: four participants in the pilot, set by the course term; a full study would follow MacKenzie-style device comparisons at 12 to 24"; refinement clause: accepted recommendation: carried from item 2.3, which item 8.5 of the 0.2.0 checklist still requires.
- Replaces: the 8.5 entry under Decisions

### 2026-10-15, item 8.6, the assumed effect size retired
- New decision: Retired with no replacement. The 0.2.0 checklist has no item 8.6 and runs no power analysis, so the assumed effect size of 0.5 composite scale points, its rank-1 sourcing and the reasons ranks 2 and 3 were unavailable are no longer design decisions of this brief.
- Reason: "items 8.5, 8.6 and 8.7 are superseded by the 0.2.0 checklist"
- Replaces: the 8.6 entry under Decisions

### 2026-10-15, item 8.7, the count across plausible effect sizes retired
- New decision: Retired with no replacement. The 0.2.0 checklist has no item 8.7, so the simulated range — more than 32 participants at 0.25 points, 20 to 24 at the assumed 0.5, 8 at 1.00 — is no longer a design decision; item 8.5's band of 12 to 24 from similar experiments stands in its place.
- Reason: "items 8.5, 8.6 and 8.7 are superseded by the 0.2.0 checklist"
- Replaces: the 8.7 entry under Decisions
```

## Entries for items that no longer exist

Of the 32 entries under Decisions, eleven are not design-tree items in 0.2.0: 6.7, 8.6, 8.7, 11.2, 11.4, 11.5, 11.6, 11.7, 11.8 and 11.9 are absent from the 0.2.0 checklist, and 6.6 is present only as `review-only`. Every 0.2.0 design-tree item has an entry. What the skill did:

- 8.5 (exists in 0.2.0, reworded): amended as the user asked. 8.6 and 8.7: each retired by an amendment block, as the user asked.
- 6.7 and 11.2 to 11.9: no amendment, no edit. It left them as frozen records and noted that 2.3, 2.4, 6.7 and the 11.x entries cite the count of 24 and the power run. It did not say that the 11.x entries and 6.7 are themselves absent from 0.2.0, and did not offer to retire them.
- 6.6: it asked whether to amend it; its remark "6.6 is not a 0.2.0 item either" is loose, since 0.2.0 keeps 6.6 as a review-only item. The user declined further amendments.
- Open items 13, 14 and 16: left unchanged.

The plugin's `references/brief.md` and `SKILL.md` step 8 give no form for retiring an entry; the skill improvised `New decision: Retired with no replacement.` in the three-line shape, which the checker accepts.

## The checker, run by me after the session

```text
$ cd ~/bloom-length-pilot && python3 "$P/scripts/check_proposal.py" brief proposal/design-brief.md
stdout: (empty)
stderr: proposal/design-brief.md: brief frozen under checklist 0.1.0; only the header and Amendments are checked
exit code: 0
```

The expected 0.2.0 note appears (once). No defect lines appear. The 0.1.0-era lines, such as `entry 11.4 is not a design-tree item`, are absent: `grep -c 'not a design-tree item'` on the saved stdout and stderr gives 0 and 0. The checker saw the same output before and after each edit in the session.

## State after

```text
$ git log --oneline -3
f77af3d Amend the design brief: items 8.5, 8.6 and 8.7
a35227c Freeze the design brief
b706402 Idea and references
$ git show --stat HEAD
Author: Eran Roseman <eran-roseman@uiowa.edu>
    Amend the design brief: items 8.5, 8.6 and 8.7

 proposal/design-brief.md | 17 +++++++++++++++++
 1 file changed, 17 insertions(+)
$ git status --porcelain
?? logs/
?? proposal/ethics-review.md
```

- `git diff --numstat a35227c HEAD`: `17  0  proposal/design-brief.md`, no deleted line. The header (`Status: frozen 2026-10-14`, `Checklist: experiment-proposal 0.1.0`) and every frozen entry are byte-identical to before.
- `git status --porcelain` is identical to the pre-session output.
- Against the sums taken before the session: the only file whose sum changed is `proposal/design-brief.md`; `proposal/ethics-review.md`, `proposal/power.R` and all of `logs/` match.
- One commit was made, with one file. No branch was created; `git stash list` is empty.

## Observations (no bar)

- The 0.2.0 checker's older-brief mode worked as specified: header and Amendments only, one stderr note, exit 0, and no stale-entry defects.
- The skill kept to the frozen-entry rule: it edited only its own uncommitted amendment text, committed with a pathspec on the one file, and asked for the user's OK on the one clause that was not the user's words before committing.
- Gaps found, for the plan's author: (a) no documented form for retiring an entry whose item no longer exists; (b) the skill did not warn that 6.7 and the 11.x entries are also gone from 0.2.0, only that they cite the old count; (c) its chat said "16 provisional" where the file has 29 provisional entries.
