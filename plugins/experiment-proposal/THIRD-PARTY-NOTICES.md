# Third-party notices

The experiment-proposal plugin is MIT licensed (see `LICENSE`). It carries copies of, or text adapted from, four MIT-licensed sources. Each copied file names its source, commit and licence in a provenance header; this file reproduces the copyright notices and the licence text, as the MIT licence requires. The index of everything the research-vault repository carries from others is its `ATTRIBUTION.md`.

## Sources

| Source                                                                                    | Commit                                     | What this plugin carries                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Copyright                            |
| ----------------------------------------------------------------------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------ |
| [K-Dense-AI/scientific-agents](https://github.com/K-Dense-AI/scientific-agents)           | `98c7fae46648724e1a43a1f2b207b0c82fcc462e` | `agents/hci-researcher.md`: the upstream subagent `scientific-agents/human-computer-interaction-researcher/agents/human-computer-interaction-researcher.md`, its frontmatter name changed, a routing sentence prefixed to its description and narrowed to the questions design asks, and a tools line added, three marked local edits                                                                                                                                          | Copyright (c) 2026 K-Dense, Inc.     |
| [hutzelmann/thesis-proposal-skills](https://github.com/hutzelmann/thesis-proposal-skills) | `1666e690e7b2f0659531253d319d41ebf0a310d7` | the nine scripts under `skills/lit-search/scripts/`: the upstream `skills/proposal-lit-search/scripts/*.py`, unchanged apart from their headers; and the six substance tests of `shared/guidelines/guidelines.md`, closely paraphrased into `references/checklist.md` items 13.6 to 13.11, some clauses verbatim                                                                                                                                                               | Copyright (c) 2026 Thomas Hutzelmann |
| [mohitagw15856/pm-claude-skills](https://github.com/mohitagw15856/pm-claude-skills)       | `f93fee7459e2bf452ec9bc43163004812efba51f` | `skills/the-ethics-board/SKILL.md`: the upstream file with two marked local edits, the frontmatter description replaced by a name-only line and two sentences under What This Skill Produces that write `proposal/ethics-review.md` and let an agent run proceed on the inputs given; the repository was unreachable on 2026-10-24 (`gh api` 404), licence and copyright as read at the commit when vendored, archived as `swh:1:rev:f93fee7459e2bf452ec9bc43163004812efba51f` | Copyright (c) 2026 Mohit Aggarwal    |
| [mattpocock/skills](https://github.com/mattpocock/skills)                                 | `49dd158d1076134a641b33efb035946536778336` | the frontier-rounds mechanic of `skills/productivity/grilling/SKILL.md`, adapted in this plugin's own words into `skills/design/SKILL.md`                                                                                                                                                                                                                                                                                                                                      | Copyright (c) 2026 Matt Pocock       |

Text closely paraphrased, credited in `ATTRIBUTION.md` and in `references/checklist.md`: the six substance tests of hutzelmann's `shared/guidelines/guidelines.md` (MIT), some clauses verbatim; the MIT notice above covers them.

Ideas restated without copying text: the "why this matters" line, provisional answers and a written record of scdenney's research-grill (CC BY-NC 4.0), consulted and not copied.

The scientific-agents repository's README and `CITATION.cff`, and the pm-claude-skills `CITATION.cff`, ask that the projects be cited; the plugin README repeats the request.

## The MIT licence

Each source's licence file is the standard MIT text below, under its own copyright line:

- Copyright (c) 2026 K-Dense, Inc.
- Copyright (c) 2026 Thomas Hutzelmann
- Copyright (c) 2026 Mohit Aggarwal
- Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
