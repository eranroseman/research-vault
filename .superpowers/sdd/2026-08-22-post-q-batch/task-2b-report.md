# Task 2b report — vault index embeds the two Bases

Disposition: historical (2026-09-06)

## Status: DONE

Commit: `660f752 feat: vault index embeds the trust-tier and open-questions Bases`

## Each Base's actual content, beside the lead-in compressed from it

### `research_vault/templates/vault/system/bases/trust-tier.base`

```yaml
views:
  - type: table
    name: Trust tier
filters:
  and:
    - 'type == "literature"'
```

No `formulas` key, no explicit `order`/columns. It is a table view named
"Trust tier" whose only mechanism is a filter to `type == "literature"`. I
checked whether a `trust_tier` frontmatter property exists that the Base
could be showing as a column — it does not: `trust_tier` is computed at
runtime by `research_vault/events.py:242 trust_tier(note_text)`, a Python
function over verified events, not a stored property. A Base (declarative
filter/formula over file properties and content) cannot read it. So I did
not write a lead-in implying the table shows or computes a tier — that would
be invented. What the Base actually does is select every literature note
into one table, named for its intended use.

**Lead-in written:** `Literature notes, for trust-tier review:`

This states the filter (literature notes) and the view's own stated purpose
(its name, "Trust tier") without asserting a mechanism the file doesn't have.

### `research_vault/templates/vault/system/bases/open-questions.base`

```yaml
views:
  - type: table
    name: Open questions
filters:
  and:
    - 'type == "synthesis"'
formulas:
  open_q: 'file.content.contains("(open-question)")'
```

A table view named "Open questions", filtered to `type == "synthesis"`,
with a formula column `open_q` that is `true` when the note's content
contains the literal string `"(open-question)"` — the evidence-boundary tag
used in synthesis claims (confirmed against
`research_vault/templates/vault/system/glossary.md:57` and
`docs/superpowers/specs/2026-08-16-foundation-spec.md:81`, which define
`(open-question)` as the fourth evidence-boundary tag). Unlike trust-tier,
this Base does carry a real formula, so the lead-in can honestly describe
the flagging behavior.

**Lead-in written:** `Synthesis notes, flagged where they contain an open-question:`

## Template before / after

Before (12 lines, unchanged frontmatter/heading/first six bullets):

```
---
type: "index"
okf_version: "0.2"
---
# Vault index

- [[literatures/]] — evidence layer: citekey-keyed literature notes
- [[synthesis/]] — synthesis notes (see [[synthesis/index]])
- [[projects/]] — manuscripts and deliverables
- [[log/]] — daily activity log (summary: [[log]])
- [[inbox/]] — fleeting notes and the review queue
- [[system/]] — support artifacts: templates, bases, the bibliography export
```

After (six lines appended under the folder links, nothing above line 12
touched):

```
- [[system/]] — support artifacts: templates, bases, the bibliography export

Literature notes, for trust-tier review:
![[system/bases/trust-tier.base]]

Synthesis notes, flagged where they contain an open-question:
![[system/bases/open-questions.base]]
```

The `.base` files were not moved, copied, or duplicated — both embeds
reference `system/bases/...` in place. `system/bases/` remains one of the
six pinned scaffold paths; I did not touch the scaffold path list, `doctor`,
or `VAULT_DIRS`/`EXPECTED_CREATED` constants (only their expected *content*
string, addressed below).

## Pin updates — two, not one

The brief named a single whole-file pin: `tests/test_templates.py:79`
(byte-equality on the packaged template asset). I updated that one first,
then re-ran the full suite per the verification-before-completion norm
rather than assuming the brief's surface list was exhaustive, and the suite
caught a **second** whole-file pin the brief did not name:
`tests/test_scaffold.py:81`, inside
`test_scaffold_creates_the_complete_okf_vault_and_returns_paths`. It asserts
the *scaffolded* vault's `index.md` (the output of
`scaffold.scaffold_vault()`, not the packaged template path) against the
identical literal string. Both pins now carry the same appended six lines,
byte-for-byte. Both files are staged and committed in this one commit, per
"whole-file pins update in the SAME commit as the content they pin."

Flagging this as a finding for the task author: the brief's "surfaces,
verified by me — nothing to hunt for" list covered only one of the two
pins on this exact string. I did not treat this as license to widen scope —
the second pin restates the same content, not a text this task's brief
scoped elsewhere — but it's worth noting other task briefs in this batch may
have similarly incomplete pin enumerations if they're pinning content that's
duplicated between a template asset and a scaffold-output assertion.

## mdformat

Confirmed out of scope before relying on it: the pre-commit hook's `entry`
is `mdformat --number --wrap keep README.md AGENTS.md CONTEXT.md docs
skills` (`.pre-commit-config.yaml:57`) — `research_vault/templates` and
`tests/` are not in that path list, so mdformat never touches
`vault/index.md`, `test_templates.py`, or `test_scaffold.py`. Ran the form
gate twice anyway (once after the template+test_templates.py edit, once
after adding the test_scaffold.py fix) and inspected `cat -A` output on the
template file to confirm the `![[...]]` embed syntax survived byte-exact
(no `\` escaping, no smart-quote substitution, no whitespace collapse).
Both runs: 8/8 passed.

## Line 10 confirmation

`sed -n '10p' research_vault/templates/vault/index.md` after all edits
still reads exactly:

```
- [[log/]] — daily activity log (summary: [[log]])
```

Byte-identical to the pre-edit version. Not touched, not reworded.

## What I tested

1. `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files` — 8/8,
   run twice (after the template edit, after the second pin fix).
2. `.venv/bin/python -m pytest tests -q` — first run failed on the
   previously-unknown `test_scaffold.py:81` pin (1 failed, 1574 passed, 7
   skipped); after fixing that pin, second run: **1575 passed, 7 skipped**,
   matching the stated baseline exactly (task adds no tests, only moves two
   existing pins).
3. `git diff` / `git status --short` inspected before staging — confirmed
   only the three intended files changed (`vault/index.md`,
   `tests/test_templates.py`, `tests/test_scaffold.py`) and no incidental
   churn from mdformat or other hooks.
4. `cat -A` on the template file to check for hidden byte differences
   (trailing whitespace, non-breaking spaces) around the new lines.

## Self-review (per the brief's checklist)

- Each lead-in true of its Base's actual filter/formula? Yes — verified
  against the raw YAML above; the trust-tier lead-in deliberately avoids
  claiming a tier-column mechanism the file doesn't have, since `trust_tier`
  is runtime-computed, not a Base-readable property.
- Line 10 untouched? Confirmed byte-identical.
- Pin matches the template byte-for-byte? Confirmed — both
  `test_templates.py` (packaged asset) and `test_scaffold.py` (scaffolded
  output) now match `vault/index.md`'s actual bytes; full suite green is
  the mechanical proof.

## Concerns

None that block. One observation already covered above: the brief's pin
enumeration was incomplete by one file; caught by running the full suite
rather than trusting the named surface list, and fixed in the same commit
as required.

## Follow-up: 3d26a44 — blank line before each Base embed

Review on commit `660f752` came back spec compliant / Approved, zero
Critical or Important findings, with one risk-elimination request (not a
proven defect): whether Obsidian promotes `![[x.base]]` to a block-level
embed when the lead-in text sits on the line immediately above with no
blank line between. In CommonMark those two lines are one paragraph; if
Obsidian follows that, the embed renders inline and the table never
appears — and that failure mode defeats this task's entire purpose (one-
click dashboard access) while still passing every byte-equality pin, since
the pins only check the string, not the render. The reviewer could not
verify Obsidian's actual behavior offline, and asked for the blank line as
a zero-cost hedge rather than asserting the bug is real.

New commit on top of `660f752` (not an amend — that commit is reviewed and
its review recorded): `3d26a44 fix: blank line before each Base embed so
it renders as a block`.

### Change

`research_vault/templates/vault/index.md`, before -> after:

```diff
 Literature notes, for trust-tier review:
+
 ![[system/bases/trust-tier.base]]
 
 Synthesis notes, flagged where they contain an open-question:
+
 ![[system/bases/open-questions.base]]
```

Both pins (`tests/test_templates.py`, `tests/test_scaffold.py`) moved in
the same commit, same treatment as before — each lead-in line's trailing
`\n` became `\n\n` in the literal string; the embed lines are unchanged.

### Not addressed — routed elsewhere per the reviewer's instruction

The reviewer's other cannot-verify — whether `open-questions.base`'s
`open_q` formula column actually renders in the default table view, given
the file declares `formulas.open_q` but no `order`/column list — was
explicitly marked "not yours to fix" and routed to the task that applies
these templates to a live vault (where a real Obsidian exists to check).
I left `open-questions.base` untouched, confirmed by `git status` showing
only the three files above.

### Test evidence

1. `.venv/bin/python -m pytest tests/test_templates.py tests/test_scaffold.py -q`
   -> `23 passed`.
2. `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files` ->
   8/8 passed. Checked specifically for mdformat interference: took an
   md5sum of `vault/index.md` before running the hook suite and diffed
   against the post-run md5sum — identical, confirming mdformat did not
   touch (let alone collapse) the new blank lines. This matches the
   config read earlier: the `mdformat` hook's `entry` is scoped to
   `README.md AGENTS.md CONTEXT.md docs skills` (`.pre-commit-config.yaml:57`),
   which excludes `research_vault/templates` and `tests/` entirely, so
   there was never a risk of the formatter reaching this file, and the
   checksum confirms it empirically rather than by config-reading alone.
3. `.venv/bin/python -m pytest tests -q` -> `1575 passed, 7 skipped` —
   matches the `660f752` baseline exactly, as expected (still no new
   tests, only the same two pins' literal strings changed again).

### Concerns

None. The change is minimal (2 inserted blank lines in the template, 2
matching edits in each of the two existing pins), mechanically verified
not to have been touched by any formatter, and the full suite is baseline-
equal. The remaining open question (does `open_q` actually render as a
column) is explicitly out of scope and routed per the reviewer's
instruction, not silently dropped.
