# Codex admission test at 0.3.0, run 1

- Date: 2026-10-25.
- Plugin commit: `8882c9f` (branch `experiment-proposal-v3`, `plugin.json` 0.3.0, working tree clean), installed by local path from the branch's checkout (`<checkout>`) before the tag. The same commit's `quality` check passed (run 40194136203).
- Host: codex-cli 0.147.0. Model `gpt-5.6-sol`, as every attempt's session records it (no model was set, so this is Codex's default for the account; the 0.1.0 record ran `gpt-5.6-terra`). Sandbox `workspace-write` with network access off, approval `never`, as the sessions record them.
- Codex home: a scratch home (`<scratch codex home>`, under `~/.cache`, mode 700) holding only a copy of `auth.json`, set as `CODEX_HOME` on every `codex` invocation, `codex --version` included. Before the install, `codex plugin list` in it printed `No marketplace plugins found.`, so the setting was honoured. No `config.toml` was written by hand; Codex wrote its own on `marketplace add` and `plugin add`. Two scratch homes were used, the first for the review attempt (run first, alone, to check the judging on a real stream) and the second for the other three skills; each got the install below and was deleted when its script exited. The operator's Codex home was not used: its `research-vault` marketplace (the GitHub form) and its 0.2.0 install were not touched.
- Scratch projects: a fresh `mktemp -d` project per attempt (`<scratch>`), `git init`, an empty `init` commit, `proposal/`, the fixtures committed as `fixtures`. Design: `fixtures/material-with-gaps.md` as `material.md`. Review, lit-search and the ethics board: `fixtures/proposal-with-defects.md` as `proposal/draft.md` and `fixtures/proposal-with-defects.brief.md` as `proposal/design-brief.md` (the brief names no lit-search project; this one's draft is the pointing-device study the need names).
- Each attempt: `codex exec --json -C <scratch> -s workspace-write '<prompt>' </dev/null`, run from `<scratch>` under `timeout 1500`; each finished in one to two minutes with exit 0. `-s workspace-write` lets a loaded skill read and write the project and run `python3`. Each attempt printed `Reading additional input from stdin...` on stderr despite the redirect; the prompt is the argument, and stdin added nothing.

## Install

```text
$ codex plugin list
No marketplace plugins found.
$ codex plugin marketplace add "<checkout>"
Added marketplace `research-vault` from <checkout>.
Installed marketplace root: <checkout>
$ codex plugin add experiment-proposal@research-vault
Added plugin `experiment-proposal` from marketplace `research-vault`.
Installed plugin root: <scratch codex home>/plugins/cache/research-vault/experiment-proposal/0.3.0
$ codex plugin list | grep experiment-proposal
<checkout>/.claude-plugin/marketplace.json
research-vault@research-vault       not installed                <checkout>
experiment-proposal@research-vault  installed, enabled  0.3.0    <checkout>/plugins/experiment-proposal
```

The cache folder holds `.claude-plugin/plugin.json`, `LICENSE`, `README.md`, `THIRD-PARTY-NOTICES.md`, `agents/hci-researcher.md`, `references/` (`brief.md`, `checklist.md`, `review.md`), `scripts/check_proposal.py` and the four skill folders. A local-path install copies the working tree as it stands: an ignored `scripts/__pycache__/` came along.

## How the attempts were judged

The `--json` stream carries the agent messages, the commands and the paths of file changes, but neither the skill load nor file contents. The session rollout Codex writes under `<scratch codex home>/sessions/` carries both, so each attempt's rollout (the one named by the thread id of the stream's `thread.started` event) was copied out before the home was deleted, and the load was read there. In all four, record 8 is the prompt and record 10 is a user-role message that Codex added for the mention, before any tool call:

```text
<skill>
<name>experiment-proposal:review</name>
<path><scratch codex home>/plugins/cache/research-vault/experiment-proposal/0.3.0/skills/review/SKILL.md</path>
---
name: review
...
```

with the whole `SKILL.md` after the path (the other three skills the same, with their names). The load is that record. A tool call naming a path under the plugin cache was counted when its input named `<scratch codex home>` or `plugins/cache`. Every such call came after the load: the skill's own follow-ups, which read `SKILL.md` and `references/checklist.md` and run `scripts/check_proposal.py` or `litsearch.py` by cache path, because `${CLAUDE_PLUGIN_ROOT}` stays literal in Codex (as the 0.1.0 record found). No attempt ran `rg`, `find`, `ls` or `cat` over the cache before the load. The brief's `grep -c 'plugins/cache'` over a whole stream gives 10, 6, 2 and 2 lines (review, design, lit-search, ethics board), all after the load.

The three skills that read `$ARGUMENTS` got no arguments: Codex leaves the text after the mention in the message. In all three the model read the word `agent` after the mention as the agent-run token (review's first message: "I’m using the `experiment-proposal:review` skill in agent mode"), and none waited. The ethics-board prompt carries "no human will answer".

## Attempts

| Skill            | Attempt | Prompt                                                                                            | Load                   | Cache-path tool calls before the load (after) | Verdict  |
| ---------------- | ------- | ------------------------------------------------------------------------------------------------- | ---------------------- | --------------------------------------------- | -------- |
| design           | 1       | `'$experiment-proposal:design agent material.md'`                                                 | the mention, record 10 | 0 (3)                                         | admitted |
| review           | 1       | `'$experiment-proposal:review agent'`                                                             | the mention, record 10 | 0 (5)                                         | admitted |
| lit-search       | 1       | `'$experiment-proposal:lit-search agent "similar studies of pointing-device comparison"'`         | the mention, record 10 | 0 (1)                                         | admitted |
| the-ethics-board | 1       | `'$experiment-proposal:the-ethics-board on the study in proposal/draft.md; no human will answer'` | the mention, record 10 | 0 (1)                                         | admitted |

Each skill was admitted on its first attempt, so no second or third attempt ran.

### design

The extraction table, then the closing line, in the final message:

```text
| Item | Extracted status | Evidence or gap |
|---|---|---|
| 1.1 | settled | “Does entering text…change words per minute…?” |
| 1.2 | settled | Standing protocol, committee, and two-week review stated |
| 1.3 | weak | Raw-data retention undecided |
...
brief open, 11 provisional; the user freezes it with /experiment-proposal:design
```

`proposal/design-brief.md` was written with `Status: open` and eleven entries reading `Status: provisional` and `Source: agent run, 2026-10-25`; `check_proposal.py brief` exits 0 on it (re-run on the saved copy). Nothing was committed: the scratch history is still `init`, `fixtures`, and `git status --porcelain` shows only `?? proposal/`.

### review

The final message carries the four attested rows, the closing line and the hand-off:

```text
- **3.1** not confirmed
- **5.2** not confirmed
- **13.1** not confirmed
- **13.4** not confirmed
...
The user picks fixes with `/experiment-proposal:review`

/oss:research-grill defend proposal/draft.md
```

`proposal/review.md` holds 67 rows with those four `not confirmed`, and `check_proposal.py review` exits 0 on it. The model's first write failed the checker with three defects (two passes without a quoted passage, a Summary count off by one), and it corrected them before finishing. The draft is unchanged: `git diff` is empty, and `git status --porcelain` shows only `?? proposal/review.md`. Step 7 read `~/.claude/plugins/installed_plugins.json` (read-only), found an `oss@` key, and printed the installed form of the hand-off.

### lit-search

Step 2's index line, in the second agent message, before any search:

```text
The available indexes are Crossref, arXiv, Semantic Scholar, DBLP, and OpenCitations for snowballing; OpenAlex will participate if the configured key file supplies its key.
```

The run created `proposal/notes/lit-search-judged.txt`, seeded with the draft's 14 references (`kept | already in the draft`). The sandbox has no network, so the first keyword round failed on name resolution for every index, and the run stopped before snowballing and gave no step 4 report. That does not affect admission, since step 2 comes before any search, but it means this record does not test the searches.

### the-ethics-board

The board wrote `proposal/ethics-review.md`, whose first line is:

```text
# Ethics Review: Target selection with a mouse and a trackball — population: right-handed adults aged 18–22 recruited from the investigator's own course section
```

The heading is in the transcript at rollout record 24, the tool call that adds the file (the `--json` stream gives only its path). The final message lists 13 board exchanges with file notes, a ranked vulnerability map and 12 protocol revisions. `git status --porcelain` shows only `?? proposal/ethics-review.md`.

## Codex's own skills list

The developer message of every session lists the skills Codex offers implicitly, and none of experiment-proposal's are among them. That is expected under `allow_implicit_invocation: false` and is not a failure. The list is not empty in a scratch home: it holds skills installed outside the Codex home (`superpowers:*`, `archify` and others), and the design attempt read one of them (`~/.agents/skills/verification-before-completion/SKILL.md`) after the load. So the scratch home isolates Codex's config, marketplaces and plugins, but not user-level skills.

The second home held six rollout files after its three attempts. Each attempt's own rollout was matched by its thread id. The other three files were not inspected before the home was deleted.

## Conclusion

| Skill            | Admitted on | Result                                                                                   |
| ---------------- | ----------- | ---------------------------------------------------------------------------------------- |
| design           | attempt 1   | The explicit mention loads the skill; extraction table and the agent-run closing line.   |
| review           | attempt 1   | The explicit mention loads the skill; four `not confirmed` rows, closing line, hand-off. |
| lit-search       | attempt 1   | The explicit mention loads the skill; step 2's index line.                               |
| the-ethics-board | attempt 1   | The explicit mention loads the skill; `# Ethics Review:` heading in the written review.  |

Every skill is admitted. `allow_implicit_invocation` stays `false` in the four `agents/openai.yaml`, the flip is not applied, and the README is unchanged.

## Cleanup

No `codex plugin remove` or `codex plugin marketplace remove` was run, because the install existed only in the two scratch Codex homes, and each was deleted when its script exited (an exit trap, with a deletion line in its log). Nothing was removed from the operator's Codex home, and its `research-vault` marketplace and 0.2.0 install stay as they were.
