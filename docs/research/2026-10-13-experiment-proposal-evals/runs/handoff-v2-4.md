# handoff-v2 scenario 6, run 4

Date: 2026-10-15. Plugin commit under test: `76e9c28` (`<checkout>/plugins/experiment-proposal`, version 0.2.0 by the session's init event). The harness file names `5e13529`; for these runs the plugin commit is `76e9c28` (design fix `ed96208`, review and fixture fix `76e9c28`). The fix that matters for this scenario is `76e9c28`: `skills/review/SKILL.md` step 7 now says "Read the file each time you print the hand-off; an earlier reading is stale." The plugin tree was unchanged while the runs went (`git diff 76e9c28 HEAD --stat -- plugins/experiment-proposal` printed nothing, and `git status --porcelain -- plugins/experiment-proposal` was empty).

Scenario 6 (the defend-stage hand-off), both cases, on the scenario 5 project `/tmp/ep-eval/review-v2-4` (review run 4, saved turns 1 to 3, scored in `runs/review-v2-4.md`; its defects are not scored here).

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
S=/tmp/ep-eval/review-v2-4
P=<checkout>/plugins/experiment-proposal
cd "$S" && claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "/experiment-proposal:review"
cd "$S" && claude -p --continue --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "Template values: accept the course's defaults, with the citation style \"author-year, as the draft uses\" and the supervisor \"the course instructor\". Confirm 3.1, 5.2, 13.1 and 13.4."
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
| 1    | `/experiment-proposal:review`             | rc=0 secs=138    | success (is_error false)                                           |
| 2    | the attested batch (3.1, 5.2, 13.1, 13.4) | rc=0 secs=450    | success (is_error false)                                           |
| 3    | `Apply fixes 6 and 9.`                    | rc=0 secs=66     | success (is_error false)                                           |
| 4    | `Print the hand-off again.`               | rc=0 secs=27     | success (is_error false, api_error_status null, 5 turns, 24817 ms) |

No turn hit a 429 or a session limit; the `.err` file of turn 4 is empty. A UserPromptSubmit hook from the `caveman` plugin adds `CAVEMAN MODE ACTIVE` context to these sessions (present in the turn 4 stream); it is not scored.

## Present case: turn 2 final message, closing lines (verbatim)

Turn 2 is the first pass message. It does not end with the hand-off.

```text
Fix 5 gates fixes 6, 7, 9 and 10 — they are written in the within-design's terms; going between means a second pass over those rows.

Which fixes should I apply? Give their numbers.
```

The file written in that turn did hold the Hand-off section (`/tmp/ep-eval/review-v2-4.turn2.review.md`, the same text as below). Tool calls of turn 2: 16, of which the 2nd was `Read {"file_path": "~/.claude/plugins/installed_plugins.json"}` (the whole file, before the Write of `proposal/review.md`); the last was a Bash run of the checker.

## Present case: turn 3 final message, closing lines (verbatim)

The turn 3 prompt was `Apply fixes 6 and 9.`. The hand-off is the last content of the message, in a `text` fence.

````text
**Still open:** fixes 1, 2, 3, 4, 5, 7, 8, 10, 11 and 13. Fix 5, the device within-vs-between departure, still gates the design and needs `/experiment-proposal:design` either way. No waivers recorded.

```text
/oss:research-grill defend proposal/draft.md
Seed list: no waivers; could someone run a session from the Method alone?; no substance test passed narrowly.
```
````

Tool calls of turn 3: 11. The 11th and last was `Read {"file_path": "~/.claude/plugins/installed_plugins.json", "limit": 10, "offset": 144}`, after the checker run. Its result began:

```text
144	    ],
145	    "oss@open-science-skills": [
146	      {
147	        "scope": "user",
```

## The Hand-off section of `proposal/review.md` (after turn 3)

```text
## Hand-off

/oss:research-grill defend proposal/draft.md
Seed list: no waivers; could someone run a session from the Method alone?; no substance test passed narrowly.
```

The section is the same after turn 2 and after turn 3. Rows 13.6 to 13.11: 13.9 reads `fail` and the other five read `pass`, so no substance test passed narrowly; the Waivers section reads `none`.

## Absent case: turn 4 (verbatim)

Prompt: `Print the hand-off again.` Tool calls in the turn (4): `Read {"file_path": "~/.claude/plugins/installed_plugins.json", "limit": 12, "offset": 144}`; `Read {"file_path": "~/.claude/plugins/installed_plugins.json"}`; `Edit` on `proposal/review.md` (old string the installed-form hand-off, new string the absent form); `Bash` running `check_proposal.py review proposal/review.md` (no output, exit 0).

The windowed Read returned three lines and no key:

```text
144	    ]
145	  }
146	}
```

The session then read the whole file (146 lines; no `oss@` key). Its text before the Edit:

```text
research-grill is gone from the file since the last print (`oss@open-science-skills` uninstalled), so the hand-off takes the absent form. Updating `proposal/review.md` to match.
```

The final message, whole:

````text
Checker clean.

```text
research-grill is not installed. Install it with:
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
Then run: /oss:research-grill defend proposal/draft.md
Seed list: no waivers; could someone run a session from the Method alone?; no substance test passed narrowly.
```
````

The Hand-off section of `proposal/review.md` after turn 4 holds the same five lines (the absent form), and the checker exits 0 on the file (run again after the turn).

## Criteria, present case (installed)

| Criterion                                                                   | Result | Evidence                                                                                                                                                                                                                                                                                                                                                                                                      |
| --------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The exact command `/oss:research-grill defend proposal/draft.md`            | pass   | its own line in turn 3's closing fence and in review.md                                                                                                                                                                                                                                                                                                                                                       |
| The seed list: each waiver, the Method question, each narrow substance pass | pass   | `Seed list: no waivers; could someone run a session from the Method alone?; no substance test passed narrowly.` There are no waivers and no narrow substance pass (13.9 is `fail`), so the Method question is the only item. The line spells the two empty slots out (`no waivers`, `no substance test passed narrowly`); the Hand-off template and runs 5 and 6 leave empty slots out. The content is right. |
| The final message ends with the hand-off in full                            | pass   | turn 3, the last pass message, ends on the closing fence of the hand-off with both lines inside. Flag: turn 2, the first pass message, ends with `Which fixes should I apply? Give their numbers.` and no hand-off, although step 7 says "End every message that ends a pass with the hand-off text itself"; runs 5 and 6 printed the hand-off after that question in turn 2.                                 |
| The hand-off matches review.md's Hand-off section                           | pass   | the same two lines; the section is unchanged from turn 2 to turn 3                                                                                                                                                                                                                                                                                                                                            |
| The plugins file was read in the turn that printed the hand-off (step 7)    | pass   | turn 3: Read with offset 144 and limit 10 as the last tool call, its result showing the key at line 145. Turn 2 read the whole file as the 2nd of 16 tool calls but printed no hand-off at its end                                                                                                                                                                                                            |

## Criteria, absent case (`oss@open-science-skills` uninstalled)

| Criterion                                                       | Result | Evidence                                                                                                                                                      |
| --------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Re-reads the plugins file in this turn (step 7)                 | pass   | two Read calls on `~/.claude/plugins/installed_plugins.json` (a window at offset 144, then the whole file) before any text; neither result held an `oss@` key |
| Says `research-grill is not installed`                          | pass   | first line of the hand-off block                                                                                                                              |
| Gives both install commands (`marketplace add`, then `install`) | pass   | `claude plugin marketplace add scdenney/open-science-skills` then `claude plugin install oss@open-science-skills`                                             |
| Gives the defend command after the install commands             | pass   | `Then run: /oss:research-grill defend proposal/draft.md`, the fourth line                                                                                     |
| Gives the seed list                                             | pass   | `Seed list: no waivers; could someone run a session from the Method alone?; no substance test passed narrowly.`, unchanged                                    |
| The final message ends with the absent-form hand-off in full    | pass   | the message is `Checker clean.` and the fenced five-line block, which is the last content                                                                     |
| The hand-off is in the file in the same form                    | pass   | an Edit replaced the installed form in `proposal/review.md`, the checker exited 0, and the file holds the five absent-form lines                              |

## Verdict

Run 4 of scenario 6: pass. The scenario bar is met in both cases. Present: the last pass message (turn 3) carries the exact command and the full seed list, ends with them, matches review.md, and followed a Read of the plugins file in the same turn. Absent: with `oss@open-science-skills` uninstalled (no `oss` plugin and no `oss:` skills in turn 4's init event, no `oss@` key in the file), the continued session read the file again, saw the key was gone, said `research-grill is not installed`, printed the two install commands, then the defend command, then the seed list, edited review.md to match, and ended its message on the block in full. The step 7 sentence added in `76e9c28` ("Read the file each time you print the hand-off") produced the change of form that run 1 of `5e13529` missed.

Flagged, not part of the bar: turn 2's first-pass message ended with the question and no hand-off. The seed list's explicit `no waivers` and `no substance test passed narrowly` are wording the template does not give. The session peeked at the file with a window at a remembered line (offset 144) before the full read in the absent turn (run 6 did the same); the window held only the file's closing brackets, and the session widened to the whole file before it concluded, so no false "installed" or false "absent" followed. Plugin files were not edited.
