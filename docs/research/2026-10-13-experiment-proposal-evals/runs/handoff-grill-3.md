# handoff grill scenario, run 3

Date: 2026-10-14. Plugin commit: `3893203` (`git rev-parse --short HEAD` at the start of the runs; the worktree head moved to `959cdac` during them through record-only commits, and `git diff --stat 3893203 959cdac -- plugins/experiment-proposal` is empty, so the plugin tree is identical). Scenario 6 (hand-off), research-grill PRESENT. This is a fresh scenario 5 project, not the continuation of a review record; the 12 defects are not scored.

## Install record (shared by the three runs)

Taken before the runs; the user approved this install (relayed by the plan's author), the one exception to the never-install rule in the common rules.

Before:

```text
$ claude plugin marketplace list
Configured marketplaces: claude-code-plugins, ponytail, claude-plugins-official, caveman, obsidian-skills, jrjsmrtn-skills, openai-codex, <own-marketplace>, agricidaniel-claude-obsidian, typesafe-ai
(ten marketplaces; open-science-skills not among them)

$ claude plugin list
Installed plugins (user scope unless noted): caveman@caveman 309834233183, claude-obsidian@agricidaniel-claude-obsidian 2.2.0, codex@openai-codex 1.0.6, diataxis-skills@jrjsmrtn-skills 0.1.5, obsidian@obsidian-skills 1.0.1, ponytail@ponytail 4.9.0, security-guidance@claude-code-plugins 2.0.0 (user and project), sensemaking@<own-marketplace> 0.2.2, software-dev@<own-marketplace> 0.8.0, superpowers@<own-marketplace> 6.3.0, typesafe@typesafe-ai 0.5.7, writing-clearly-and-concisely@<own-marketplace> 0.1.0
(no oss@ entry; installed_plugins.json held no key beginning oss@)
```

Install commands, output verbatim:

```text
$ claude plugin marketplace add scdenney/open-science-skills
Adding marketplace…Cloning via SSH: git@github.com:scdenney/open-science-skills.git
Refreshing marketplace cache (timeout: 120s)…
Cloning repository (timeout: 120s): git@github.com:scdenney/open-science-skills.git
Clone complete, validating marketplace…
Cleaning up old marketplace cache…
✔ Successfully added marketplace: open-science-skills (declared in user settings)
(exit 0)

$ claude plugin install oss@open-science-skills
Installing plugin "oss@open-science-skills"...✔ Successfully installed plugin: oss@open-science-skills (scope: user)
(exit 0)
```

After:

```text
$ claude plugin list   (the oss entry)
  ❯ oss@open-science-skills
    Version: 2.35.1
    Scope: user
    Status: ✔ enabled
```

`~/.claude/plugins/installed_plugins.json` now holds the key `oss@open-science-skills` (version 2.35.1, user scope, git sha `cd70e9b44a417ada7a0ebe405e3d1e66815d78ce`). The cache directory holds `skills/research-grill`. research-grill was left installed.

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

Both turns exited 0 in this run. The three runs executed in parallel in three scratch projects. Turn 2 is the last turn; no further turn was run. The defend command was not run.

## Turn 1, stdout from the batch question onward

```text
Which fixes should I apply? Give their numbers.** Fix 2 and fix 20 need your decision text, not just a number. Any fail you will not fix: say so, with a reason, and I record a waiver.

Run `/oss:research-grill defend proposal/draft.md`

Seed objections:

- Could someone run a session from the Method alone?
- Delta (13.6, pass narrowly): the third contribution, a reusable program and its logs, reads as a feature list rather than something the study adds beyond the cited work.
- Falsifiability (13.7, pass narrowly): under the draft's decision rule a null is only "not supported", never a refutation, until a smallest-effect-size bound is written in.
- Necessity (13.9, pass narrowly): the Fitts's law index-of-difficulty formula is stated but no hypothesis or analysis uses it.
- Executability (13.11, pass narrowly): the mouse and trackball are placeholders, "each named by make and model".
```

## Turn 2, the FINAL message of the session (full stdout, verbatim)

```text
Review file updated. Items 3.1, 5.2, 13.4 now pass, confirmed 2026-10-14. Items 11.10 and 13.1 fail per your answer. Neither has a draft fix: 11.10 needs the dry run of `proposal/power.R` on simulated data (file absent from proposal directory now), 13.1 needs the seven-reader-question pass. Both re-attest once done, or take a waiver with your reason.

Summary now: 79 checked, 53 pass, 26 fail, 2 defend-stage, 21 fixes proposed, 0 waivers.

Still blocked on fixes. Which fixes should I apply? Give their numbers. Fix 2 needs the mouse and trackball make and model. Fix 20 needs your call: amend brief via `/experiment-proposal:design` to device within subjects, or rewrite draft to device between subjects. Any fail you will not fix: say so with a reason, and I record a waiver.

Run `/oss:research-grill defend proposal/draft.md`

Seed objections:

- Could someone run a session from the Method alone?
- Delta (13.6, pass narrowly): the third contribution, a reusable program and its logs, reads as a feature list rather than something the study adds beyond the cited work.
- Falsifiability (13.7, pass narrowly): under the draft's decision rule a null is only "not supported", never a refutation, until a smallest-effect-size bound is written in.
- Necessity (13.9, pass narrowly): the Fitts's law index-of-difficulty formula is stated but no hypothesis or analysis uses it.
- Executability (13.11, pass narrowly): the mouse and trackball are placeholders, "each named by make and model".
```

## The Hand-off section of proposal/review.md after turn 2

```text
## Hand-off

Run `/oss:research-grill defend proposal/draft.md`

Seed objections:

- Could someone run a session from the Method alone?
- Delta (13.6, pass narrowly): the third contribution, a reusable program and its logs, reads as a feature list rather than something the study adds beyond the cited work.
- Falsifiability (13.7, pass narrowly): under the draft's decision rule a null is only "not supported", never a refutation, until a smallest-effect-size bound is written in.
- Necessity (13.9, pass narrowly): the Fitts's law index-of-difficulty formula is stated but no hypothesis or analysis uses it.
- Executability (13.11, pass narrowly): the mouse and trackball are placeholders, "each named by make and model".
```

## How review detected the install

Review tried Bash first (two attempts, both refused, same messages as runs 1 and 2), then read the file with the Read tool:

```text
Read: ~/.claude/plugins/installed_plugins.json
  -> (file contents returned; it holds the key "oss@open-science-skills")
```

So the detection was `installed_plugins.json`, via Read. The skill listing in the transcript contains no `oss:` entry (nor any `experiment-proposal` entry), so the listing was not the means. The session then printed the installed-case hand-off.

## Criteria

| Criterion                                                                   | Result | Evidence                                                                                                                                                                    |
| --------------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Exact command `/oss:research-grill defend proposal/draft.md`                | pass   | "Run `/oss:research-grill defend proposal/draft.md`" in the final message and in review.md                                                                                  |
| No install commands (research-grill is installed)                           | pass   | neither the final message nor review.md mentions "not installed" or the two install commands                                                                                |
| Seed list: each waiver (none in this fixture)                               | pass   | no waivers in this fixture, and review.md records none; none listed. The hand-off does not say "no waivers" in words; the summary line of the same message says "0 waivers" |
| Seed list: "could someone run a session from the Method alone?"             | pass   | first seed objection                                                                                                                                                        |
| Seed list: each narrow pass with its doubt                                  | pass   | 13.6, 13.7, 13.9 and 13.11, each with a doubt; the review.md rows for those items read `pass narrowly`                                                                      |
| Final message ends with the hand-off text itself, not a pointer to the file | pass   | turn 2's stdout ends on the last seed objection                                                                                                                             |
| review.md Hand-off matches the final message                                | pass   | same command and seed list (compare the quoted blocks)                                                                                                                      |
| Detection of the install                                                    | pass   | `installed_plugins.json` via Read (see the detection section)                                                                                                               |

## Verdict

Run 3 of the scenario 6 hand-off with research-grill present: **PASS**. review detected the install by reading `installed_plugins.json` with the Read tool, printed the exact defend command with no install commands, and the final message ends with the seed list.
