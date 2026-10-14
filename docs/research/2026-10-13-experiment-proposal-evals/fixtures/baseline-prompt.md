# Scenario 1: baseline prompt and scoring key

Run three times with no plugin loaded: `claude -p "<the prompt below>"` in a fresh scratch project.

## The prompt

I want to run a controlled experiment comparing a mouse and a trackball for selecting targets on a screen, with right-handed young adults. Help me settle every design decision this experiment needs, with my reasons, and write them into a design brief file I can commit.

## Scoring

Score each run against the 32 design-tree items of `plugins/experiment-proposal/references/checklist.md`. An item counts as settled only when the answer states the decision and a reason; a decision the run invented without asking counts as unasked. Record, per run:

- items settled with a reason, items decided without asking, items never raised;
- whether R or any power tool was checked for, whether a smallest effect size of interest was asked for, whether a decision rule per hypothesis, a random-effects simplification order and a multiplicity policy were raised;
- whether a brief file was written, and whether it records rationale in the user's words (there is no user turn, so any "rationale" is invented).

Expected (the RED step, not a pass bar): most of items 6.6, 6.7, 8.6, 8.7, 11.6, 11.7, 11.9 never raised; no prerequisite check; decisions made without asking.
