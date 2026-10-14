# handoff grill scenario, run 2

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

````text
Which fixes should I apply? Give their numbers.** Fixes 2, 21 and 22 are `decide:` fixes needing your choice; 21 routes through `/experiment-proposal:design`.

research-grill is not installed. Install:

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
```

Then run `/oss:research-grill defend proposal/draft.md`.

Seed objections for the defend stage:

- Could someone run a session from the Method alone?
- Delta (13.6, pass narrowly): the third contribution reads as a feature, and the current-device delta rests on a lit-search the brief still lists as open.
- Necessity (13.9, pass narrowly): the Fitts's law formula is stated but no hypothesis or model uses the index of difficulty.
- Executability (13.11, pass narrowly): the apparatus has no make or model, and weeks 1 and 2 are unaccounted for.
````

## Turn 2, the FINAL message of the session (full stdout, verbatim)

````text
Recorded. 3.1, 5.2, 13.4 now pass (confirmed 2026-10-14). 11.10 and 13.1 fail with your answer. 13.5 now also lists 11.10. Summary: 50 pass, 29 fail, 2 not checked.

Two process failures have no draft fix:

- **11.10** dry run. Re-run `proposal/power.R` once the analysis plan is settled (fix 15 and the fix 21 decision change which models it must fit), or accept a waiver with your reason.
- **13.1** seven reader questions. Do the review and tell me, or accept a waiver with your reason.

**Which fixes should I apply? Give their numbers.** Fixes 2, 21 and 22 need your decision; 21 routes through `/experiment-proposal:design`. Say if you want waivers for 11.10 or 13.1, with the reason.

research-grill is not installed. Install:

```text
claude plugin marketplace add scdenney/open-science-skills
claude plugin install oss@open-science-skills
```

Then run `/oss:research-grill defend proposal/draft.md`.

Seed objections for the defend stage:

- Could someone run a session from the Method alone?
- Delta (13.6, pass narrowly): the third contribution reads as a feature, and the current-device delta rests on a lit-search the brief still lists as open.
- Necessity (13.9, pass narrowly): the Fitts's law formula is stated but no hypothesis or model uses the index of difficulty.
- Executability (13.11, pass narrowly): the apparatus has no make or model, and weeks 1 and 2 are unaccounted for.
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

Seed objections for the defend stage:

- Could someone run a session from the Method alone?
- Delta (13.6, pass narrowly): the third contribution reads as a feature, and the current-device delta rests on a lit-search the brief still lists as open.
- Necessity (13.9, pass narrowly): the Fitts's law formula is stated but no hypothesis or model uses the index of difficulty.
- Executability (13.11, pass narrowly): the apparatus has no make or model, and weeks 1 and 2 are unaccounted for.
````

## How review detected the install

Same path as run 1: two Bash attempts, both refused, then no further check.

```text
Bash: ls -la <scratch>/proposal/; grep -o '"oss@[^"]*"' ~/.claude/plugins/installed_plugins.json 2>/dev/null | head -3; echo "grill-check-done"
  -> This Bash command contains multiple operations. The following part requires approval: ...
Bash: grep -c 'oss@' ~/.claude/plugins/installed_plugins.json
  -> grep in '~/.claude/plugins/installed_plugins.json' was blocked. For security, Claude Code may only search for patterns in files from the allowed working directories for this session: '<scratch>'.
```

It never tried the Read tool on that file and wrote "research-grill is not installed" into review.md. The skill listing in the transcript contains no `oss:` entry (nor any `experiment-proposal` entry).

## Criteria

| Criterion                                                                   | Result   | Evidence                                                                                                                                                                                                    |
| --------------------------------------------------------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Exact command `/oss:research-grill defend proposal/draft.md`                | pass     | present in the final message and in review.md                                                                                                                                                               |
| No install commands (research-grill is installed)                           | **fail** | the final message and review.md both open with "research-grill is not installed" and print `claude plugin marketplace add scdenney/open-science-skills` and `claude plugin install oss@open-science-skills` |
| Seed list: each waiver (none in this fixture)                               | pass     | no waivers in this fixture, and review.md records none; none listed                                                                                                                                         |
| Seed list: "could someone run a session from the Method alone?"             | pass     | first seed objection, in the final message and in review.md                                                                                                                                                 |
| Seed list: each narrow pass with its doubt                                  | pass     | 13.6, 13.9 and 13.11 each with a doubt; the review.md rows for those items read `pass narrowly` (see the Hand-off section below for the text)                                                               |
| Final message ends with the hand-off text itself, not a pointer to the file | pass     | turn 2's stdout ends on the last seed objection                                                                                                                                                             |
| review.md Hand-off matches the final message                                | pass     | same statement, commands and seed list                                                                                                                                                                      |
| Detection of the install                                                    | fail     | see the detection section: Bash refused, Read never tried                                                                                                                                                   |

## Verdict

Run 2 of the scenario 6 hand-off with research-grill present: **FAIL**. research-grill was installed, but the session did not detect it and printed the absent-case hand-off ("research-grill is not installed" and the two install commands). The defend command and the seed list are correct, and the final message does end with the hand-off text, but the pass bar says no install commands since research-grill is installed.
