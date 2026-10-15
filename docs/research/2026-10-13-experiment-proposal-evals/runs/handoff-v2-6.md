# handoff-v2 scenario 6, run 6

Date: 2026-10-15. Plugin commit under test: `76e9c28` (`<checkout>/plugins/experiment-proposal`, version 0.2.0 by the session's init event). The harness file names `5e13529`; for these runs the plugin commit is `76e9c28` (design fix `ed96208`, review and fixture fix `76e9c28`). The fix that matters for this scenario is `76e9c28`: `skills/review/SKILL.md` step 7 now says "Read the file each time you print the hand-off; an earlier reading is stale." The plugin tree was unchanged while the runs went (`git diff 76e9c28 HEAD --stat -- plugins/experiment-proposal` printed nothing, and `git status --porcelain -- plugins/experiment-proposal` was empty).

Scenario 6 (the defend-stage hand-off), both cases, on the scenario 5 project `/tmp/ep-eval/review-v2-6` (review run 6, saved turns 1 to 3, scored in `runs/review-v2-6.md`; its defects are not scored here).

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

Reinstall, directly after this third absent turn (all three turns ran back to back, 02:59 to 03:00 CDT; the reinstall ran at 03:00:20 CDT): `claude plugin install oss@open-science-skills` printed `Installing plugin "oss@open-science-skills"...✔ Successfully installed plugin: oss@open-science-skills (scope: user)` (exit 0); no `marketplace add` was needed. `claude plugin list` afterwards:

```text
  ❯ oss@open-science-skills
    Version: 2.35.1
    Scope: user
    Status: ✔ enabled
```

## Commands

The scenario 5 turns (turn 1 has no `--continue`), as `review-v2-drive.sh` runs them, saved to `$S.turnN.jsonl`:

```bash
S=/tmp/ep-eval/review-v2-6
P=<checkout>/plugins/experiment-proposal
cd "$S" && claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "/experiment-proposal:review"
cd "$S" && claude -p --continue --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "Template mechanics: accept the course's defaults, with the citation style author-year, as the draft uses, and the supervisor the course instructor. Confirm 3.1, 5.2, 13.1 and 13.4."
cd "$S" && claude -p --continue --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "Apply fixes 5 and 8."
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
| 1    | `/experiment-proposal:review`             | rc=0 secs=32     | success (is_error false)                                           |
| 2    | the attested batch (3.1, 5.2, 13.1, 13.4) | rc=0 secs=518    | success (is_error false)                                           |
| 3    | `Apply fixes 5 and 8.`                    | rc=0 secs=64     | success (is_error false)                                           |
| 4    | `Print the hand-off again.`               | rc=0 secs=21     | success (is_error false, api_error_status null, 5 turns, 17910 ms) |

No turn hit a 429 or a session limit; the `.err` file of turn 4 is empty. A UserPromptSubmit hook from the `caveman` plugin adds `CAVEMAN MODE ACTIVE` context to these sessions (present in the turn 4 stream); it is not scored.

## Present case: turn 2 final message, closing lines (verbatim)

The turn 2 prompt was the attested batch. The message ends with the hand-off, after the question and a `---` rule, unfenced.

```text
Which fixes should I apply? Give their numbers.

---

/oss:research-grill defend proposal/draft.md
Seed list: could someone run a session from the Method alone?; item 13.9 passed narrowly, the doubt being that Accot and Zhai (1997) is cited and then set aside as not applying to the discrete task, so removing it would not weaken the argument.
```

Tool calls of turn 2: 14. The 14th and last was `Read {"file_path": "~/.claude/plugins/installed_plugins.json"}` (the whole file, after the final checker run and before the print). Turn 1 had read the file as its 6th and last tool call.

## Present case: turn 3 final message, closing lines (verbatim)

The turn 3 prompt was `Apply fixes 5 and 8.`. The hand-off is the last content of the message, after a `---` rule, unfenced.

```text
Open and blocking the submission: fix 9 (the consent form) needs the instructor's name and two contact addresses from you; fix 12 needs `/experiment-proposal:design` to settle device within versus between, since the brief contradicts itself on it.

---

/oss:research-grill defend proposal/draft.md
Seed list: could someone run a session from the Method alone?; item 13.9 passed narrowly, the doubt being that Accot and Zhai (1997) is cited and then set aside as not applying to the discrete task, so removing it would not weaken the argument.
```

Tool calls of turn 3: 10. The 10th and last was `Read {"file_path": "~/.claude/plugins/installed_plugins.json", "limit": 5, "offset": 144}`, after both checker runs. Its result:

```text
144	    ],
145	    "oss@open-science-skills": [
146	      {
147	        "scope": "user",
148	        "installPath": "~/.claude/plugins/cache/open-science-skills/oss/2.35.1",
```

## The Hand-off section of `proposal/review.md` (after turn 3)

```text
## Hand-off

/oss:research-grill defend proposal/draft.md
Seed list: could someone run a session from the Method alone?; item 13.9 passed narrowly, the doubt being that Accot and Zhai (1997) is cited and then set aside as not applying to the discrete task, so removing it would not weaken the argument.
```

Rows 13.6 to 13.11: 13.9 reads `pass narrowly` (the doubt: "Accot and Zhai (1997) is cited and then set aside in the same sentence as not applying to the discrete task, so removing it would not weaken the argument") and the other five read `pass`; the Waivers section reads `none`. The seed list names the one narrow pass with its doubt, and the section is the same after turn 2 and after turn 3.

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
`oss@open-science-skills` is gone from `~/.claude/plugins/installed_plugins.json` — it was there earlier this session, so research-grill was uninstalled in between. Fresh read wins, so the hand-off changes form. Updating the file to match.
```

The final message, whole:

```text
Checker still exits 0. No waivers, so the seed list is unchanged.

---

research-grill is not installed. Install it with:
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
Then run: /oss:research-grill defend proposal/draft.md
Seed list: could someone run a session from the Method alone?; item 13.9 passed narrowly, the doubt being that Accot and Zhai (1997) is cited and then set aside as not applying to the discrete task, so removing it would not weaken the argument.
```

The Hand-off section of `proposal/review.md` after turn 4 holds the same five lines (the absent form), and the checker exits 0 on the file (run again after the turn).

## Criteria, present case (installed)

| Criterion                                                                   | Result | Evidence                                                                                                                                                                                                                                                              |
| --------------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The exact command `/oss:research-grill defend proposal/draft.md`            | pass   | its own line in the closing lines of turn 2 and of turn 3, and in review.md                                                                                                                                                                                           |
| The seed list: each waiver, the Method question, each narrow substance pass | pass   | `Seed list: could someone run a session from the Method alone?; item 13.9 passed narrowly, the doubt being ...` There are no waivers; the one narrow pass, 13.9, is named with its doubt, matching the `pass narrowly` row; 13.6 to 13.8, 13.10 and 13.11 read `pass` |
| The final message ends with the hand-off in full                            | pass   | turn 2 and turn 3 each end on the seed list line, after a `---` rule; the command line and the whole seed list are in the message, not a pointer to review.md. The hand-off is not fenced; content is scored, not fencing                                             |
| The hand-off matches review.md's Hand-off section                           | pass   | byte-equal text for both lines; the section is unchanged from turn 2 to turn 3                                                                                                                                                                                        |
| The plugins file was read in the turn that printed the hand-off (step 7)    | pass   | turn 2: a Read of the whole file as the last tool call before the print; turn 3: a Read with offset 144 and limit 5 as the last tool call before the print, its result showing the key at line 145                                                                    |

## Criteria, absent case (`oss@open-science-skills` uninstalled)

| Criterion                                                       | Result | Evidence                                                                                                                                                      |
| --------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Re-reads the plugins file in this turn (step 7)                 | pass   | two Read calls on `~/.claude/plugins/installed_plugins.json` (a window at offset 144, then the whole file) before any text; neither result held an `oss@` key |
| Says `research-grill is not installed`                          | pass   | first line of the hand-off block                                                                                                                              |
| Gives both install commands (`marketplace add`, then `install`) | pass   | `claude plugin marketplace add scdenney/open-science-skills` then `claude plugin install oss@open-science-skills`                                             |
| Gives the defend command after the install commands             | pass   | `Then run: /oss:research-grill defend proposal/draft.md`, the fourth line                                                                                     |
| Gives the seed list                                             | pass   | the Method question and the 13.9 narrow pass with its doubt, unchanged                                                                                        |
| The final message ends with the absent-form hand-off in full    | pass   | the message is a one-line checker report, a `---` rule and the five-line block, which is the last content                                                     |
| The hand-off is in the file in the same form                    | pass   | an Edit replaced the installed form in `proposal/review.md`, the checker exited 0, and the file holds the five absent-form lines                              |

## Verdict

Run 6 of scenario 6: pass. The scenario bar and the per-print read clause of `76e9c28` are both met in both cases.

Present: turn 2 and turn 3 each end on the exact command and the full seed list, which match review.md; each was printed straight after a Read of the plugins file as the last tool call, so the reading was never stale.

Absent: with `oss@open-science-skills` uninstalled (no `oss` plugin and no `oss:` skills in turn 4's init event, no `oss@` key in the file), the continued session read the file again before saying anything, saw the key was gone, said `research-grill is not installed`, printed the two install commands, then the defend command, then the seed list, edited review.md to match, and ended its message on the block in full. This is the case run 1 of `5e13529` missed (it answered from context with no tool call); the new sentence in step 7 produced the read here.

Flagged, not part of the bar: the session opened turn 4 with a window at a remembered line (offset 144, limit 12), the same peek it made in turn 3; the window held only the file's closing brackets, and the session widened to the whole file before it concluded, so no false "installed" or false "absent" followed. A window at a stale line number after a reinstall could land on other content; here it did not matter. Plugin files were not edited.
