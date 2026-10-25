# Scenario 7: the routing set

Written before any 0.3.0 run. Each utterance is one `claude -p` session in a fresh scratch project under the isolated configuration (README, Harness), judged by `routing_predicate.py` over the saved stream.

## Positives (one run each; a failure triggers three fresh runs on the all-three rule)

The prompt names the skill in words, never as a slash command; the bar is a Skill call of that skill whose result is not an error, followed by the skill's first decisive line.

| Skill            | Prompt                                                                                                                                                       | First decisive line                                                                                        |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| design           | Use the experiment-proposal plugin's design skill as an agent run on material.md; no human will answer. (`material.md` is `fixtures/material-with-gaps.md`.) | the extraction table, or "brief open, N provisional; the user freezes it with /experiment-proposal:design" |
| review           | Use the experiment-proposal plugin's review skill as an agent run on this project; no human will answer. (the scenario 5 fixtures in `proposal/`)            | the `not confirmed` rows, or "No design brief at proposal/design-brief.md" when the brief is absent        |
| lit-search       | Use the experiment-proposal plugin's lit-search skill as an agent run; the need is similar studies of pointing-device comparison; no human will answer.      | "which indexes will answer", then the round's `candidates:` line                                           |
| the-ethics-board | Use the experiment-proposal plugin's ethics board skill on the study in proposal/draft.md; no human will answer.                                             | `# Ethics Review:` and the file `proposal/ethics-review.md`                                                |

## Negatives (three runs each, 21 runs, all-three rule)

The bar is zero Skill calls of this plugin and zero Agent calls of its subagent; other plugins' calls are recorded and not barred.

| Set          | Utterance                                                                                                    |
| ------------ | ------------------------------------------------------------------------------------------------------------ |
| design       | Help me settle the design decisions of my controlled experiment in rounds and freeze them in a brief.        |
| review       | Check my written experiment proposal against its frozen design brief and a checklist and write me a review.  |
| lit-search   | Search scholarly indexes and snowball from a couple of seed DOIs for the sources my literature review needs. |
| ethics board | Rehearse an ethics-committee review of my study and write up the review.                                     |
| out of scope | review this pull request                                                                                     |
| out of scope | find papers on transformer pruning                                                                           |
| out of scope | help me prepare for my IRB meeting                                                                           |
