# handoff-v2 scenario 6, run 3

Date: 2026-10-15. Plugin commit under test: `5e13529` (`<checkout>/plugins/experiment-proposal`, version 0.2.0 by the session's init event). Scenario 6 (the defend-stage hand-off), both cases, on the scenario 5 project `/tmp/ep-eval/review-v2-3` (the review scenario's project; its saved runs are turns 1 to 3, the defects are not scored here).

The present case (research-grill installed) is scored from the saved final messages of turn 2 and turn 3 of the scenario 5 run, which ran with `oss@open-science-skills` installed. The absent case is a new turn 5 (`Print the hand-off again.`) run after `oss@open-science-skills` was uninstalled, with the user's approval for this evaluation. Turn 4 of the scenario 5 run (the same prompt) failed with a 429 and produced nothing, so turn 5 reuses its prompt.

## Install state

Before the absent case, `claude plugin list` showed:

```text
  ❯ oss@open-science-skills
    Version: 2.35.1
    Scope: user
    Status: ✔ enabled
```

The session's own Read of `~/.claude/plugins/installed_plugins.json` in turn 1 returned a file holding the key `"oss@open-science-skills"` (the only Read of that file in the session), and the init event of turn 3 listed 42 `oss:` skills including `oss:research-grill`.

Uninstall: `claude plugin uninstall oss@open-science-skills` printed `✔ Successfully uninstalled plugin: oss (scope: user)` (exit 0). Afterwards `claude plugin list` held no `oss@` line and `grep -o '"oss@[^"]*"' ~/.claude/plugins/installed_plugins.json` printed nothing. The init event of turn 5 lists no `oss` plugin and 0 `oss:` skills.

Reinstall after the third absent turn (the three turns ran back to back, 02:05 to 02:06 CDT): `claude plugin install oss@open-science-skills` printed `Installing plugin "oss@open-science-skills"...✔ Successfully installed plugin: oss@open-science-skills (scope: user)`; the marketplace was still configured, so no `marketplace add` was needed. `claude plugin list` afterwards shows the same four lines as before: `oss@open-science-skills`, Version 2.35.1, Scope user, Status enabled.

## Commands

The scenario 5 turns (the harness flags, saved to `$S.turnN.jsonl`; turn 1 has no `--continue`):

```bash
S=/tmp/ep-eval/review-v2-3
P=<checkout>/plugins/experiment-proposal
cd "$S" && claude -p --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "/experiment-proposal:review"
cd "$S" && claude -p --continue --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "Template mechanics: accept the course's defaults, with the citation style author-year, as the draft uses, and the supervisor the course instructor. Confirm 3.1, 5.2, 13.1 and 13.4."
cd "$S" && claude -p --continue --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "Apply fixes 8 and 11."
cd "$S" && claude -p --continue --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "Print the hand-off again."
```

| Turn | Prompt                                    | Exit and seconds | Result                                           |
| ---- | ----------------------------------------- | ---------------- | ------------------------------------------------ |
| 1    | `/experiment-proposal:review`             | rc=0 secs=539    | success (is_error false)                         |
| 2    | the attested batch (3.1, 5.2, 13.1, 13.4) | rc=0 secs=75     | success (is_error false)                         |
| 3    | `Apply fixes 8 and 11.`                   | rc=0 secs=77     | success (is_error false)                         |
| 4    | `Print the hand-off again.`               | rc=1 secs=5      | 429, `You've hit your session limit` (no output) |

The absent case, in this order, with the plugin directory and flags of the harness; the helper script `review-v2-drive.sh` reads the prompt from `$S.turn5.prompt` and runs the same command with `--continue`:

```bash
claude plugin list
claude plugin uninstall oss@open-science-skills
claude plugin list
grep -o '"oss@[^"]*"' ~/.claude/plugins/installed_plugins.json
cd "$S" && claude -p --continue --model opus --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)" --output-format stream-json --verbose "Print the hand-off again."
claude plugin install oss@open-science-skills
claude plugin list
```

Turn 5: rc=0 secs=6, `is_error` false, `api_error_status` null, 1 turn, 4036 ms. Before uninstalling, one trivial `claude -p --model opus` call from an unrelated scratch directory (no plugin directory) returned `end_turn`, which showed the session limit had lifted; it is not part of this run.

## Present case: turn 2 final message, closing lines (verbatim)

The turn 2 prompt was the attested batch; the final message ends with the hand-off.

````text
Which fixes should I apply? Give their numbers.

```
/oss:research-grill defend proposal/draft.md
Seed list: could someone run a session from the Method alone?; item 13.8 passed narrowly, the doubt being that the third contribution, a reusable task program and its trial logs, would read the same for any pointing study.
```
````

## Present case: turn 3 final message, closing lines (verbatim)

The turn 3 prompt was `Apply fixes 8 and 11.`.

````text
Which fixes should I apply? Give their numbers.

```
/oss:research-grill defend proposal/draft.md
Seed list: could someone run a session from the Method alone?; item 13.8 passed narrowly, the doubt being that the third contribution, a reusable task program and its trial logs, would read the same for any pointing study.
```
````

## The Hand-off section of `proposal/review.md` (after turn 3)

None of the Edit calls of turns 2 and 3 touched this section, and a diff of the section saved after turn 1 against the one after turn 3 is empty.

```text
## Hand-off

/oss:research-grill defend proposal/draft.md
Seed list: could someone run a session from the Method alone?; item 13.8 passed narrowly, the doubt being that the third contribution, a reusable task program and its trial logs, would read the same for any pointing study.
```

The rows for the narrow passes it seeds sit at line 96 (`/tmp/ep-eval/review-v2-3.turn3.review.md`).

## Absent case: turn 5 final message (verbatim, whole)

Prompt: `Print the hand-off again.` Tool calls in the turn: none (the stream holds no tool_use entry).

````text
research-grill is installed (`oss@open-science-skills`).

```
/oss:research-grill defend proposal/draft.md
Seed list: could someone run a session from the Method alone?; item 13.8 passed narrowly, the doubt being that the third contribution, a reusable task program and its trial logs, would read the same for any pointing study.
```

No waivers, so none seed the list. This is the same text as the Hand-off section of `proposal/review.md`.
````

## Criteria, present case (installed)

| Criterion                                                                   | Result | Evidence                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| --------------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The exact command `/oss:research-grill defend proposal/draft.md`            | pass   | present as its own line in the closing lines of turn 2 and of turn 3, and in review.md                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| The seed list: each waiver, the Method question, each narrow substance pass | pass   | `Seed list: ... could someone run a session from the Method alone?; ...` with each narrow pass (13.8) carrying its doubt, matching the `pass narrowly` rows. The seed list names 13.8, the only substance-test row that reads `pass narrowly` (13.9 reads `fail`, so it is not a narrow pass). Item 8.3 also reads `pass narrowly` (line 46) but it is not a substance test, and the seed list is limited to waivers, the Method question and substance tests passed narrowly (SKILL.md step 7), so its absence is correct. No waivers. |
| The final message ends with the hand-off in full                            | pass   | turn 2 and turn 3 each end on the seed list line, or on its closing code fence where the run fences it (quoted above); the command line and the whole seed list are in the message, not a pointer to review.md                                                                                                                                                                                                                                                                                                                          |
| The hand-off matches review.md's Hand-off section                           | pass   | the same command line and the same seed list text; the section is unchanged since turn 1                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Installed state was established with the Read tool                          | note   | turn 1 read `~/.claude/plugins/installed_plugins.json` and got `"oss@open-science-skills"`; turns 2 and 3 did not read it again (no match for `installed_plugins` in either stream)                                                                                                                                                                                                                                                                                                                                                     |

## Criteria, absent case (`oss@open-science-skills` uninstalled)

| Criterion                                                          | Result | Evidence                                                                                                                                                                                                                           |
| ------------------------------------------------------------------ | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Says `research-grill is not installed`                             | fail   | the turn 5 text opens with the sentence "research-grill is installed (oss@open-science-skills).", the opposite of the machine state                                                                                                |
| Gives both install commands (`marketplace add`, then `install`)    | fail   | neither `claude plugin marketplace add scdenney/open-science-skills` nor `claude plugin install oss@open-science-skills` appears                                                                                                   |
| Gives the defend command after the install commands                | fail   | the defend command `/oss:research-grill defend proposal/draft.md` is printed, but with no install commands and no statement before it, so it reads as ready to run                                                                 |
| Gives the seed list                                                | pass   | the same seed list as the installed case, unchanged (nothing in the project changed)                                                                                                                                               |
| The final message ends with the absent-form hand-off in full       | fail   | the message ends with the installed-form hand-off followed by a sentence saying it matches review.md                                                                                                                               |
| Re-establishes the install state before printing (SKILL.md step 7) | fail   | zero tool calls in turn 5 (1 turn, 4036 ms); no Read of `~/.claude/plugins/installed_plugins.json`, which held no `oss@` key at that moment and whose absence the init event of turn 5 confirms (0 `oss:` skills, no `oss` plugin) |

## Verdict

Run 3 of scenario 6: the present case passes and the absent case fails, so the scenario bar is not met on this run.

Present: the closing lines of both turns carry the exact command and the full seed list, and the seed list matches the `pass narrowly` rows of review.md.

Absent: with `oss@open-science-skills` uninstalled (no `oss` plugin and no `oss:` skills in turn 5's init event, no `oss@` key in `~/.claude/plugins/installed_plugins.json`), the continued session answered `Print the hand-off again.` in 4036 ms without a tool call and reprinted the installed-form hand-off from its context, and asserted that research-grill is installed. The only Read of `installed_plugins.json` in the session was turn 1's, made while the plugin was installed. SKILL.md step 7 and `references/review.md` give the installed test as a read of that file ("read with the Read tool"); neither says to read it again each time the hand-off is printed, and this run did not. Nothing about the Hand-off text itself was wrong: the miss is in detecting the state, not in the wording of the two forms.

Notes on the setup, not scored. The session carried the 429 turn's unanswered `Print the hand-off again.` and its synthetic error reply into turn 5. A UserPromptSubmit hook from the `caveman` plugin adds `CAVEMAN MODE ACTIVE (full)` context to these sessions (present in the turn 2 and turn 5 streams of each of the three runs). Plugin files were not edited; the miss is recorded for the plan's author.
