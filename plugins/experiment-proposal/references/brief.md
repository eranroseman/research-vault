# The brief

`proposal/design-brief.md` is the record of the design decisions `design` settles with the user. `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_proposal.py" brief proposal/design-brief.md` (on a host that leaves the variable unexpanded, `../scripts/check_proposal.py` relative to this file) checks everything below and prints one line per defect; a brief that passes it has the shape, and nothing else is required of the shape.

## Header

Three lines before the first section:

```text
Draft: proposal/draft.md
Status: open
Checklist: experiment-proposal 0.2.0
```

`Draft:` is the path the proposal draft will have. `Status:` is `open` while the rounds run and `frozen YYYY-MM-DD` once the user has approved the brief and it is committed. `Checklist:` carries the plugin's version, read from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`.

## Sections

`## Decisions`, `## Looked up`, `## Open items`, in that order, then `## Amendments` once the first amendment exists. No other section.

## Entries

One entry under Decisions per design-tree item (the checklist items whose scope reads `design-tree`), in checklist order, each exactly:

```markdown
### 7.5 Counterbalancing
- Decision: AB and BA, half the participants each, from a shuffled list.
- Rationale: "two orders are all two conditions allow"
- Would change if: the pilot showed an order effect.
- Status: settled
- Source: user, round 3
```

The five lines, in that order, and nothing else in the entry. The Decision line is at most 400 characters; numbers, tables and long reasoning go in Looked up or the rationale. The Rationale quotes the user's words, or reads `accepted recommendation: <its basis>` after a bare "yes". The Source is `user, round N`, `extracted from <file>, "<quoted passage>" (<location>)`, or `hci-researcher`.

`Status:` is one of three words:

- `settled`: the user decided.
- `pilot settles`: the user decided that the pilot will set the value; the Decision says what the pilot measures to set it.
- `provisional`: the user could not answer, so the recommendation stands in as the Decision; the item is also listed under Open items.

Extraction's `weak` and `missing` never appear in a brief: they are the statuses of the table shown before the first round.

## Looked up

One line per fact the skill found rather than asked: `- <fact>: <value> (<source>, <date>)`.

## Open items

A numbered list: first every provisional item, `1. Item 2.4 provisional, recommendation: <the recommendation>`; then each command the user should run, `2. Run `/experiment-proposal:lit-search` for <what it should find>`. Every provisional entry appears here and every item named here is a provisional entry. Commands come after the items.

## Frozen

A frozen brief has an entry for every design-tree item, each `settled`, `pilot settles` or `provisional`, and the commit `Freeze the design brief` is its record. Frozen entries are never edited.

## Amendments

An amendment appends, never edits:

```markdown
### 2026-11-02, item 7.1, device between subjects
- New decision: device between subjects.
- Reason: "daily mouse users bring habits a few minutes cannot erase"
- Replaces: the 7.1 entry under Decisions
```

The three lines, in that order. Each amendment is committed with the user's OK (`Amend the design brief: item 7.1`).
