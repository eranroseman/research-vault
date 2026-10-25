# Codex admission test at 0.3.0, run 1

- Date: 2026-10-25.
- Plugin commit: `8882c9f` (branch `experiment-proposal-v3`, `plugin.json` 0.3.0, working tree clean), installed by local path from the branch's checkout (`<checkout>`) before the tag. The same commit's `quality` check passed (run 40194136203).
- Host: codex-cli 0.147.0. Model `gpt-5.6-sol`, as every attempt's session records it (no model was set, so this is Codex's default for the account; the 0.1.0 record ran `gpt-5.6-terra`). Sandbox `workspace-write` with network access off, approval `never`, as the sessions record them.
- Codex home: a scratch home (`<scratch codex home>`, under `~/.cache`, mode 700) holding only a copy of `auth.json`. The scripts that ran the test set it as `CODEX_HOME` on every `codex` invocation, `codex --version` included. Before the install, `codex plugin list` in it printed `No marketplace plugins found.`, so the setting was honoured. No `config.toml` was written by hand; Codex wrote its own on `marketplace add` and `plugin add`. Three scratch homes were used, and each was deleted when its script exited:
  - a probe home, for `codex --version`, `codex plugin list` and the `--help` pages only, with nothing installed;
  - home a, with the install below, for the review attempt (run first, alone, to check the judging on a real stream);
  - home b, with the same install, for the other three skills.
- The operator's Codex home: before any scratch home existed, one bare `codex --version` ran against it during orientation. No plugin or marketplace command ran there, and its `research-vault` marketplace (the GitHub form) and 0.2.0 install were not touched.
- Scratch projects: a fresh `mktemp -d` project per attempt (`<scratch>`), `git init`, an empty `init` commit, `proposal/`, the fixtures committed as `fixtures`. Design: `fixtures/material-with-gaps.md` as `material.md`. Review, lit-search and the ethics board: `fixtures/proposal-with-defects.md` as `proposal/draft.md` and `fixtures/proposal-with-defects.brief.md` as `proposal/design-brief.md` (the brief names no lit-search project; this one's draft is the pointing-device study the need names).
- Each attempt: `codex exec --json -C <scratch> -s workspace-write '<prompt>' </dev/null`, run from `<scratch>` under `timeout 1500`. Each exited 0, in 99 s (review), 102 s (design), 55 s (lit-search) and 79 s (the ethics board), as the run logs time them. `-s workspace-write` lets a loaded skill read and write the project and run `python3`. Each attempt printed `Reading additional input from stdin...` on stderr despite the redirect; the prompt is the argument, and stdin added nothing.

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

with the whole `SKILL.md` after the path (the other three skills the same, with their names). The load is that record.

Admission was judged by the spec's rule (section 1): the mention loads the skill, read here as Codex inserting the `SKILL.md` into the session at record 10, and no tool call before that load names a path under the plugin cache. The brief's decisive line was kept as a check that the loaded skill ran, not as the load point. Taken as the load point, it would put cache-path calls before the load: 5 for review (whose first call `cat`s the cache's `SKILL.md`), 3 for design, 1 for the ethics board and 0 for lit-search. Those calls are the skill's own steps after the inserted load, not a search for the skill, so they do not disqualify it.

A tool call naming a path under the plugin cache was counted when its input named `<scratch codex home>` or `plugins/cache`. The counts are taken from each attempt's root session rollout. Every such call came after the load: the skill's own follow-ups, which read `SKILL.md` and `references/checklist.md` and run `scripts/check_proposal.py` or `litsearch.py` by cache path, because `${CLAUDE_PLUGIN_ROOT}` stays literal in Codex (as the 0.1.0 record found). No attempt ran `rg`, `find`, `ls` or `cat` over the cache before the load. The brief's `grep -c 'plugins/cache'` over a whole stream gives 10, 6, 2 and 2 lines (review, design, lit-search, ethics board), all after the load.

The three skills that read `$ARGUMENTS` got no arguments: Codex leaves the text after the mention in the message. In all three the model read the word `agent` after the mention as the agent-run token (review's first message: "I’m using the `experiment-proposal:review` skill in agent mode"), and none waited. The ethics-board prompt carries "no human will answer".

## Attempts

| Skill            | Attempt | Prompt                                                                                            | Load                   | Cache-path tool calls before the load (after, root session) | Verdict  |
| ---------------- | ------- | ------------------------------------------------------------------------------------------------- | ---------------------- | ----------------------------------------------------------- | -------- |
| design           | 1       | `'$experiment-proposal:design agent material.md'`                                                 | the mention, record 10 | 0 (3)                                                       | admitted |
| review           | 1       | `'$experiment-proposal:review agent'`                                                             | the mention, record 10 | 0 (5)                                                       | admitted |
| lit-search       | 1       | `'$experiment-proposal:lit-search agent "similar studies of pointing-device comparison"'`         | the mention, record 10 | 0 (1)                                                       | admitted |
| the-ethics-board | 1       | `'$experiment-proposal:the-ethics-board on the study in proposal/draft.md; no human will answer'` | the mention, record 10 | 0 (1)                                                       | admitted |

Each skill was admitted on its first attempt, so no second or third attempt ran.

### Every cache-path tool call in the four root sessions

Here `<cache>` is `<scratch codex home>/plugins/cache/research-vault/experiment-proposal/0.3.0`. The numbers count each root session's tool calls in rollout order. The `--json` stream leaves out design's three `spawn_agent` calls and lit-search's `wait` and `write_stdin`, so its count is 5 calls for design and 4 for lit-search; for review (8) and the ethics board (4) the two counts agree. Every listed call comes after the load.

- design (3 of 8 calls):
  - Call 1: `git rev-parse --show-toplevel`, then `sed -n` of `<cache>/references/checklist.md`, `<cache>/references/brief.md`, `<cache>/.claude-plugin/plugin.json` and `material.md`.
  - Calls 2 to 4 are the three `spawn_agent` calls of step 4 (see design below). Their readable arguments name no cache path; their messages are encrypted.
  - Call 6: `python3 <cache>/scripts/check_proposal.py brief proposal/design-brief.md`.
  - Call 8: the same checker call again, with `git status`, `git diff --check` and entry counts.
- review (5 of 8 calls):
  - Call 1: `cat` of `<cache>/skills/review/SKILL.md` (a re-read of the file the mention had injected), `<cache>/references/checklist.md`, `<cache>/references/review.md` and `<cache>/.claude-plugin/plugin.json`.
  - Call 3: after reading the draft, `python3 <cache>/scripts/check_proposal.py draft proposal/draft.md --words 2000-4000 --references 15-20`, then the same with `--numbers` and with `--placeholders`.
  - Call 4: `rg` counting the item lines of `<cache>/references/checklist.md`, then reading `~/.claude/plugins/installed_plugins.json`.
  - Call 6: `python3 <cache>/scripts/check_proposal.py review proposal/review.md` (exit 1).
  - Call 8: the same (exit 0), then `git diff` of the review and the draft.
- lit-search (1 of 6 calls):
  - Call 4: `python3 -B <cache>/skills/lit-search/scripts/litsearch.py search "modern mouse trackball target selection pointing device comparison movement time error rate" --exclude proposal/notes/lit-search-judged.txt --dblp-query "mouse trackball pointing" --out proposal/notes/lit-search-round-1.yaml`.
  - Calls 5 and 6, a `wait` and a `write_stdin` on the running search, name no cache path.
- the-ethics-board (1 of 4 calls):
  - Call 1: `sed -n` of `<cache>/skills/the-ethics-board/SKILL.md` (a re-read of the injected file), then of `proposal/draft.md`.

The three design subagent threads' own tool calls were not captured. Only each attempt's root rollout was copied out, and the subagents' rollouts went with home b. So this list covers the four root sessions only, and whether a subagent named the cache is unknown. The subagents forked after the load at record 10, so admission is unaffected either way.

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

Step 4's HCI-researcher delegation, for items 7.5, 7.7 and 7.9, ran as three `spawn_agent` calls in Codex's collaboration namespace, at rollout records 20, 25 and 30. The calls are named `hci_75`, `hci_77` and `hci_79` and set `fork_turns: "all"`, so each fork inherited the whole conversation, the inserted skill included. They started as threads `01a1731d-c05f-7531-8061-098decf0da3d`, `01a1731d-ceaa-7863-b651-0ba664d7b221` and `01a1731d-daf2-7113-bd7c-8970cb84e2d2` (records 21, 26 and 31) and returned FINAL_ANSWER messages at records 35, 40 and 42. The brief carries their answers as `Rationale: Recommended (hci-researcher): ...` under 7.5, 7.7 and 7.9. Under Codex, then, design's delegation runs as `spawn_agent` forks of the root session. The root session never read `agents/hci-researcher.md` (the path does not occur in its rollout); what the forks read is unknown.

### review

The final message carries the four attested rows, a closing line and the hand-off:

```text
- **3.1** not confirmed
- **5.2** not confirmed
- **13.1** not confirmed
- **13.4** not confirmed
...
The user picks fixes with `/experiment-proposal:review`

/oss:research-grill defend proposal/draft.md
```

Codex printed the closing line as "The user picks fixes with `/experiment-proposal:review`", capitalised and with the command in a code span. That differs from the pinned text, "the user picks fixes with /experiment-proposal:review". Admission rests on the `not confirmed` rows, not on the closing line.

`proposal/review.md` holds 67 rows with those four `not confirmed`, and `check_proposal.py review` exits 0 on it. The model's first write failed the checker with four defects (two passes without a quoted passage, and the Summary's Pass and Fail counts each off by one), and it corrected them before finishing. The draft is unchanged: `git diff` is empty, and `git status --porcelain` shows only `?? proposal/review.md`. Step 7 read `~/.claude/plugins/installed_plugins.json` (read-only), found an `oss@` key, and printed the installed form of the hand-off.

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

Home b held six rollout files after its three attempts. That matches the three attempts' root sessions plus the three design subagent threads (`01a1731d-c05f-7531-8061-098decf0da3d`, `01a1731d-ceaa-7863-b651-0ba664d7b221` and `01a1731d-daf2-7113-bd7c-8970cb84e2d2`). Home a held one, for review, which spawned nothing, and lit-search and the ethics board spawned nothing either. Only the root rollouts were copied out (each matched by the thread id in its stream); the subagent rollouts were deleted with the home.

## Conclusion

| Skill            | Admitted on | Result                                                                                                               |
| ---------------- | ----------- | -------------------------------------------------------------------------------------------------------------------- |
| design           | attempt 1   | The explicit mention loads the skill; extraction table and the agent-run closing line.                               |
| review           | attempt 1   | The explicit mention loads the skill; four `not confirmed` rows, a closing line not quite the pinned text, hand-off. |
| lit-search       | attempt 1   | The explicit mention loads the skill; step 2's index line.                                                           |
| the-ethics-board | attempt 1   | The explicit mention loads the skill; `# Ethics Review:` heading in the written review.                              |

Every skill is admitted. `allow_implicit_invocation` stays `false` in the four `agents/openai.yaml`, the flip is not applied, and the README is unchanged.

## Cleanup

No `codex plugin remove` or `codex plugin marketplace remove` was run, because the install existed only in scratch Codex homes a and b (the probe home had nothing installed). All three scratch homes were deleted when their scripts exited: an exit trap in each, and a deletion line in the logs of a and b. Nothing was removed from the operator's Codex home, and its `research-vault` marketplace and 0.2.0 install stay as they were.
