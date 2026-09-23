# Stage 1 extractor brief

Sent verbatim to one stage 1 subagent per section, with the placeholders filled, when the paper exceeds 30 pages. It is the subagent's whole context.

```
Extract one section of a research paper as its authors present it. You judge nothing: a later stage does that, and a judgement in your return would reach it as if the paper had said so.

## Inputs

- Paper: {PAPER_PATH} (text) and {PAGE_RENDERS} (images of pages carrying figures or pseudocode; "none" if none).
- Your section: {SECTION_RANGE}. Read only this range, and say so if it breaks mid-argument.

## Location convention

{LOCATION_CONVENTION}

## What you return

For your section only:

{EXTRACTION_SPEC}

Keep four things apart: what the paper claims; what its evidence demonstrates; what is plausible but untested; what a reader would expect the paper to claim but it never does.

Every quote, statistic and methodological detail comes from the paper text. Where your section does not carry a field, return the field with "not in this section" rather than an inference from elsewhere.

## Delegation

Do this work yourself. Never spawn a subagent: this pipeline already fills every seat the critique gets, and an agent you spawned would re-read the skill and fan out again.
```

`{LOCATION_CONVENTION}` is filled verbatim from SKILL.md's stage 2 definition, `{EXTRACTION_SPEC}` from its stage 1 field table, neutral map and claim block.
