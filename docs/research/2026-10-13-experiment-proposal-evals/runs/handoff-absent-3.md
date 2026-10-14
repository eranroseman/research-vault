# handoff absent, run 3

Date: 2026-10-14. Plugin commit: `510579b` (the plugin tree at the worktree head `06a1eec` is identical: `git diff --stat 510579b HEAD -- plugins/experiment-proposal` is empty). Scenario 6 (hand-off), research-grill ABSENT. This is a fresh scenario 5 project, not the continuation of a review record; the 12 defects are not scored. This commit changed how review detects research-grill: it reads `~/.claude/plugins/installed_plugins.json` with the Read tool and looks for a key beginning `oss@`, and asks the user when the file cannot be read.

See `runs/handoff-absent-1.md` for the uninstall output and the confirmation; the state is unchanged for this run.

## Reinstall and final state

After the three absent runs:

```text
$ claude plugin install oss@open-science-skills
Installing plugin "oss@open-science-skills"...✔ Successfully installed plugin: oss@open-science-skills (scope: user)
(exit 0)
```

The marketplace entry was still configured, so `claude plugin marketplace add` was not needed. `claude plugin list` shows:

```text
  ❯ oss@open-science-skills
    Version: 2.35.1
    Scope: user
    Status: ✔ enabled
```

`installed_plugins.json` holds `oss@open-science-skills` again (version 2.35.1, user scope, git sha `cd70e9b44a417ada7a0ebe405e3d1e66815d78ce`). research-grill was left installed and enabled.

## Commands

Setup (scratch project outside the repository, the scenario 5 fixtures committed):

```bash
tmp=$(mktemp -d) && cd "$tmp" && git init -q && git commit --allow-empty -qm init && mkdir proposal
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/proposal-with-defects.brief.md proposal/design-brief.md
cp <checkout>/docs/research/2026-10-13-experiment-proposal-evals/fixtures/proposal-with-defects.md proposal/draft.md
git add -A && git commit -qm fixtures
P=<checkout>/plugins/experiment-proposal
```

Turn 1 (prompt before `--allowedTools`; stdin from `/dev/null`):

```bash
claude -p "/experiment-proposal:review" --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit"
```

Turn 2:

```bash
claude -p --continue "Confirm 3.1, 5.2 and 13.4; 11.10 and 13.1 not done." --plugin-dir "$P" --permission-mode acceptEdits --allowedTools "Read,Write,Edit"
```

Both turns exited 0. Turn 2 is the last turn; no further turn was run. Review did not ask whether research-grill is installed (its fallback question), so no answer was given. The defend command was not run. The three runs of this phase executed in parallel in three scratch projects.

## Turn 1, stdout from the batch question onward

````text
Which fixes should I apply? Give their numbers.

research-grill is not installed. Install it with:

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
```

Then run `/oss:research-grill defend proposal/draft.md`.

Seed objections:

- could someone run a session from the Method alone?
- 13.7 Falsifiability, passed narrowly: the draft's decision rule never calls a hypothesis falsified; a non-significant result is "not supported rather than refuted".
- 13.11 Executability, passed narrowly: the mouse and trackball are placeholders, "each a named make and model", not an apparatus anyone could buy.
````

## Turn 2, the FINAL message of the session (full stdout, verbatim)

````text
Recorded. 3.1, 5.2, 13.4 pass, confirmed by the user, 2026-10-14. 11.10 and 13.1 fail with your words. 13.5 now also cites 11.10. Summary: 52 pass, 27 fail, 0 pending.

11.10 and 13.1 need no draft edit. Two routes each: run `proposal/power.R` end to end and review the draft against the seven reader questions, then tell me and I re-mark them; or give a reason and I record a waiver under Waivers, row marked `fail (waived)`.

Which fixes should I apply? Give their numbers.

research-grill is not installed. Install it with:

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
```

Then run `/oss:research-grill defend proposal/draft.md`.

Seed objections:

- could someone run a session from the Method alone?
- 13.7 Falsifiability, passed narrowly: the draft's decision rule never calls a hypothesis falsified; a non-significant result is "not supported rather than refuted".
- 13.11 Executability, passed narrowly: the mouse and trackball are placeholders, "each a named make and model", not an apparatus anyone could buy.
````

## The Hand-off section of proposal/review.md after turn 2

````text
## Hand-off

research-grill is not installed. Install it with:

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
```

Then run `/oss:research-grill defend proposal/draft.md`.

Seed objections:

- could someone run a session from the Method alone?
- 13.7 Falsifiability, passed narrowly: the draft's decision rule never calls a hypothesis falsified; a non-significant result is "not supported rather than refuted".
- 13.11 Executability, passed narrowly: the mouse and trackball are placeholders, "each a named make and model", not an apparatus anyone could buy.
````

## How review detected the install state

Taken from the session transcript (the session log of the scratch project). Review read the file with the **Read** tool:

```text
Read: ~/.claude/plugins/installed_plugins.json
  -> read succeeded (no error); it holds no key beginning `oss@`
```

A Bash call (`ls` and `git`) came after the Read; it was refused and is unrelated to detection. Review did not ask the user whether research-grill is installed. The state it printed matches the real state.

## Criteria

| Criterion                                                       | Result | Evidence                                                                                                                                                                    |
| --------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Says "research-grill is not installed"                          | pass   | first line of the hand-off in the final message and in review.md                                                                                                            |
| Both install commands                                           | pass   | `claude plugin marketplace add scdenney/open-science-skills` and `claude plugin install oss@open-science-skills` in one fenced block, in the final message and in review.md |
| Defend command for later, after the install commands            | pass   | `/oss:research-grill defend proposal/draft.md` after the install block, in both                                                                                             |
| Seed list: "could someone run a session from the Method alone?" | pass   | first seed objection                                                                                                                                                        |
| Seed list: each waiver                                          | pass   | no waivers in this run; none listed                                                                                                                                         |
| Seed list: each narrow pass with its doubt                      | pass   | 13.7 and 13.11, each with a doubt; review.md has exactly these two rows as `pass narrowly`                                                                                  |
| Final message ends with the hand-off text itself                | pass   | turn 2 stdout ends on the last seed objection                                                                                                                               |
| review.md Hand-off matches the final message                    | pass   | same statement, commands and seed list                                                                                                                                      |
| Detection                                                       | pass   | Read of `installed_plugins.json`, succeeded, no key beginning `oss@`; review printed the absent-case hand-off                                                               |

## Verdict

Run 3 of the scenario 6 hand-off with research-grill absent: **PASS**. Detection by Read found no `oss@` key; the final message states research-grill is not installed, gives both install commands, the defend command and the seed list, and ends with the seed list.
