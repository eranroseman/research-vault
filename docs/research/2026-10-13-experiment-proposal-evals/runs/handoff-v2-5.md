# handoff-v2 scenario 6, run 5

Date: 2026-10-15. Plugin commit under test: `76e9c28` (`<checkout>/plugins/experiment-proposal`, version 0.2.0 by the session's init event). The harness file names `5e13529`; for these runs the plugin commit is `76e9c28` (design fix `ed96208`, review and fixture fix `76e9c28`). The fix that matters for this scenario is `76e9c28`: `skills/review/SKILL.md` step 7 now says "Read the file each time you print the hand-off; an earlier reading is stale." The plugin tree was unchanged while the runs went (`git diff 76e9c28 HEAD --stat -- plugins/experiment-proposal` printed nothing, and `git status --porcelain -- plugins/experiment-proposal` was empty).

Scenario 6 (the defend-stage hand-off), both cases, on the scenario 5 project `/tmp/ep-eval/review-v2-5` (review run 5, saved turns 1 to 3, scored in `runs/review-v2-5.md`; its defects are not scored here).

The present case (research-grill installed) is scored from the saved turn 2 and turn 3 final messages and tool calls of the scenario 5 run, which ran with `oss@open-science-skills` installed; the last pass message is turn 3. The absent case is a new turn 4 (`Print the hand-off again.`) run after `oss@open-science-skills` was uninstalled, with the user's approval for this evaluation.

## Install state

Before the absent case, `claude plugin list` showed:

```text
  ❯ oss@open-science-skills
    Version: 2.35.1
    Scope: user
    Status: ✔ enabled
```

The marketplace `open-science-skills` (Source: GitHub (scdenney/open-science-skills)) was configured throughout. `grep -n '"oss@' ~/.claude/plugins/installed_plugins.json` printed line 145, `"oss@open-science-skills": [`.

Uninstall: `claude plugin uninstall oss@open-science-skills` printed `✔ Successfully uninstalled plugin: oss (scope: user)` (exit 0). Afterwards `claude plugin list` held no `oss@` line (the count of matching lines was 0) and `grep -o '"oss@[^"]*"' ~/.claude/plugins/installed_plugins.json` printed nothing (exit 1). The init event of turn 4 lists no `oss` plugin and 0 `oss:` skills.

Reinstall, directly after the third absent turn (all three turns ran back to back, 02:59 to 03:00 CDT): `claude plugin install oss@open-science-skills` printed `Installing plugin "oss@open-science-skills"...✔ Successfully installed plugin: oss@open-science-skills (scope: user)` (exit 0); no `marketplace add` was needed. `claude plugin list` afterwards:

```text
  ❯ oss@open-science-skills
    Version: 2.35.1
    Scope: user
    Status: ✔ enabled
```

## Commands

The scenario 5 turns (turn 1 has no `--continue`), as `review-v2-drive.sh` runs them, saved to `$S.turnN.jsonl`:

```bash
S=/tmp/ep-eval/review-v2-5
P=<checkout>/plugins/experiment-proposal
cd "$S" && claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "/experiment-proposal:review"
cd "$S" && claude -p --continue --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "Template mechanics: accept the course's defaults, with the citation style author-year, as the draft uses, and the supervisor the course instructor. Confirm 3.1, 5.2, 13.1 and 13.4."
cd "$S" && claude -p --continue --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "Apply fixes 6 and 9."
```

The absent case, in this order; the helper reads the prompt from `$S.turn4.prompt` and runs the same command with `--continue`:

```bash
claude plugin list
claude plugin uninstall oss@open-science-skills
claude plugin list
grep -o '"oss@[^"]*"' ~/.claude/plugins/installed_plugins.json
printf '%s' "Print the hand-off again." > "$S.turn4.prompt"
bash /tmp/ep-eval/review-v2-drive.sh "$S" 4
claude plugin install oss@open-science-skills
claude plugin list
```

| Turn | Prompt                                    | Exit and seconds | Result                                                             |
| ---- | ----------------------------------------- | ---------------- | ------------------------------------------------------------------ |
| 1    | `/experiment-proposal:review`             | rc=0 secs=29     | success (is_error false)                                           |
| 2    | the attested batch (3.1, 5.2, 13.1, 13.4) | rc=0 secs=302    | success (is_error false)                                           |
| 3    | `Apply fixes 6 and 9.`                    | rc=0 secs=63     | success (is_error false)                                           |
| 4    | `Print the hand-off again.`               | rc=0 secs=22     | success (is_error false, api_error_status null, 4 turns, 19753 ms) |

No turn hit a 429 or a session limit; the `.err` file of turn 4 is empty. A UserPromptSubmit hook from the `caveman` plugin adds `CAVEMAN MODE ACTIVE` context to these sessions (present in the turn 4 stream); it is not scored.

## Present case: turn 2 final message, closing lines (verbatim)

The turn 2 prompt was the attested batch. The message ends with the hand-off, after the question, unfenced.

```text
Which fixes should I apply? Give their numbers.

/oss:research-grill defend proposal/draft.md
Seed list: could someone run a session from the Method alone?
```

Tool calls of turn 2: 11. The 5th was `Read {"file_path": "~/.claude/plugins/installed_plugins.json"}` (the whole file, before the Write of `proposal/review.md`); after it came the Write of `proposal/review.md`, checker runs and two Edits, the last tool call being Bash.

## Present case: turn 3 final message, closing lines (verbatim)

The turn 3 prompt was `Apply fixes 6 and 9.`. The hand-off is the last content of the message, unfenced.

```text
Still open and unwaived: the device within-versus-between contradiction (fix 5, needs `/experiment-proposal:design`), the 14-reference shortfall, the consent form's 20-versus-35 minutes plus missing supervision/retention clauses, and the 13.9 necessity cut.

/oss:research-grill defend proposal/draft.md
Seed list: could someone run a session from the Method alone?
```

Tool calls of turn 3: 9 (two Edits on the draft, a checker run, five Edits on `proposal/review.md`, a checker run; the last was Bash). None touched `~/.claude/plugins/installed_plugins.json`; the stream has no Read of it. The hand-off was printed on the strength of turn 2's reading.

## The Hand-off section of `proposal/review.md` (after turn 3)

```text
## Hand-off

/oss:research-grill defend proposal/draft.md
Seed list: could someone run a session from the Method alone?
```

Rows 13.6 to 13.11: 13.9 reads `fail` and the other five read `pass`, so no substance test passed narrowly; the Waivers section reads `none`. The seed list holds the Method question alone.

## Absent case: turn 4 (verbatim)

Prompt: `Print the hand-off again.` Tool calls in the turn (3): `Read {"file_path": "~/.claude/plugins/installed_plugins.json"}` (the whole file, 146 lines, no `oss@` key; the first tool call); `Edit` on `proposal/review.md` (old string the installed-form hand-off, new string the absent form); `Bash` running `check_proposal.py review proposal/review.md` (no output, exit 0).

The session's text before the Edit:

```text
research-grill was uninstalled since the last print — `oss@` is no longer a key in `installed_plugins.json`. Hand-off changes to the absent branch; updating the file to match.
```

The final message, whole:

```text
Checker still clean. Hand-off:

research-grill is not installed. Install it with:
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
Then run: /oss:research-grill defend proposal/draft.md
Seed list: could someone run a session from the Method alone?
```

The Hand-off section of `proposal/review.md` after turn 4 holds the same five lines (the absent form), and the checker exits 0 on the file (run again after the turn).

## Criteria, present case (installed)

| Criterion                                                                   | Result  | Evidence                                                                                                                                                                                                                                                                                                |
| --------------------------------------------------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The exact command `/oss:research-grill defend proposal/draft.md`            | pass    | its own line in the closing lines of turn 2 and of turn 3, and in review.md                                                                                                                                                                                                                             |
| The seed list: each waiver, the Method question, each narrow substance pass | pass    | `Seed list: could someone run a session from the Method alone?` There are no waivers and no narrow substance pass (13.9 is `fail`, 13.6 to 13.8, 13.10 and 13.11 are `pass`), so the Method question is the only item; the empty slots are omitted, as the template allows                              |
| The final message ends with the hand-off in full                            | pass    | turn 2 and turn 3 each end on the seed list line; the command line and the whole seed list are in the message, not a pointer to review.md. The hand-off is not fenced; content is scored, not fencing                                                                                                   |
| The hand-off matches review.md's Hand-off section                           | pass    | the same command line and the same seed list text; the section is unchanged from turn 2 to turn 3                                                                                                                                                                                                       |
| The plugins file was read in the turn that printed the hand-off (step 7)    | partial | turn 2 pass: a Read of the whole file as the 5th of 11 tool calls. Turn 3 fail: no Read of the file in the turn, and the hand-off was printed from turn 2's reading, which is the stale reading step 7 rules out. The installed state had not changed, so the printed hand-off was still the right form |

## Criteria, absent case (`oss@open-science-skills` uninstalled)

| Criterion                                                       | Result | Evidence                                                                                                                                 |
| --------------------------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Re-reads the plugins file in this turn (step 7)                 | pass   | `Read {"file_path": "~/.claude/plugins/installed_plugins.json"}` was the first tool call, before any text; the result held no `oss@` key |
| Says `research-grill is not installed`                          | pass   | first line of the hand-off block                                                                                                         |
| Gives both install commands (`marketplace add`, then `install`) | pass   | `claude plugin marketplace add scdenney/open-science-skills` then `claude plugin install oss@open-science-skills`                        |
| Gives the defend command after the install commands             | pass   | `Then run: /oss:research-grill defend proposal/draft.md`, the fourth line                                                                |
| Gives the seed list                                             | pass   | `Seed list: could someone run a session from the Method alone?`, unchanged                                                               |
| The final message ends with the absent-form hand-off in full    | pass   | the message is `Checker still clean. Hand-off:` and the five-line block, which is the last content                                       |
| The hand-off is in the file in the same form                    | pass   | an Edit replaced the installed form in `proposal/review.md`, the checker exited 0, and the file holds the five absent-form lines         |

## Verdict

Run 5 of scenario 6: the scenario bar is met in both cases; the per-print read clause of `76e9c28` is not met on the present case's turn 3. Marked pass on the README bar, with the stricter clause flagged (the `handoff-absent-2` precedent: spec bar met, stricter clause not met).

Present: turn 2 and turn 3 each end on the exact command and the full seed list, which match review.md. Turn 3 printed it without reading `~/.claude/plugins/installed_plugins.json` in that turn; the state had not changed, so the output was right, but step 7's "Read the file each time you print the hand-off" was not followed.

Absent: with `oss@open-science-skills` uninstalled (no `oss` plugin and no `oss:` skills in turn 4's init event, no `oss@` key in the file), the continued session made its Read of the file the first act of turn 4, saw the key was gone, said `research-grill is not installed`, printed the two install commands, then the defend command, then the seed list, edited review.md to match, and ended its message on the block in full. This is the case the run 1 miss of `5e13529` concerned, and the new sentence in step 7 produced the read there. Across the run the plugins file was read in turn 2 and turn 4 and not in turn 3: the clause is followed in the absent case and missed in one of the two present prints. Plugin files were not edited.
