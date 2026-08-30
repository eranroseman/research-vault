# Task 7 report: prose sweeps — leading-word collapse + prohibition cuts (items 9–10)

## Candidate enumeration and rulings

### Item 9 — never-hand-write refrain

The audit doc (`docs/2026-08-22-skills-layer-audit.md:130`) names the five canonical
sites explicitly: `project:84`, `import-source:11`, `publish:11`, `verify-citations:9`,
`find-sources:71`. Re-located by content (line numbers drift): `find-sources:71` is
now `find-sources/SKILL.md:91` (Task 4's vendoring-notes section shifted it +20
lines). The other four line numbers held.

A full grep of `skills/*/SKILL.md` for `hand-writ|written by hand|by hand|hand write`
turned up four more sites not in the audit's list of five. Each is ruled below.

| # | Site | Ruling | Reason |
|---|------|--------|--------|
| 1 | `skills/project-flow/SKILL.md:84` | **IN** | Canonical site 1/5 |
| 2 | `skills/import-source/SKILL.md:13` | **IN** | Canonical site 2/5 |
| 3 | `skills/publish/SKILL.md:11` | **IN** | Canonical site 3/5 |
| 4 | `skills/verify-citations/SKILL.md:9` | **IN** | Canonical site 4/5 |
| 5 | `skills/find-sources/SKILL.md:91` (drifted from :71) | **IN** | Canonical site 5/5 |
| 6 | `skills/find-sources/SKILL.md:74` ("...never hand-written:") | **OUT** | Not one of the audit's named five; already phrased affirmatively ("appended through the CLI verb, never hand-written") rather than the flagged "never hand-write A, B, C" negation-enumeration pattern; predates this batch unchanged. Judgment call, not a trap called out in the brief — left alone for scope discipline. Harmless either way (no test pin, no meaning at stake), so this is a stylistic boundary call, not a correctness one. |
| 7 | `skills/setup-vault/SKILL.md:21` ("Do not create directories or files by hand...") | **OUT** | Different doctrine: this is scaffold-time discipline (don't hand-build vault structure, don't substitute custom CI, don't `git add .`, don't make an unrelated commit) — four distinct prohibited *actions* during setup, not the "compose/explain, the CLI writes" content-authorship refrain the other five restate. Test-pinned at `tests/test_skill_files.py:36` (`test_setup_vault_uses_scaffold_with_separate_ci_consents`, docstring "Hand-building a vault ... must fail") for this specific purpose. Collapsing it to "the CLI writes" would delete three of the four prohibited actions and change the rule's meaning. Ruled OUT per the brief's own steer to judge this one. |
| 8 | `skills/evidence-conventions/SKILL.md:64` ("...never by hand. Never add, edit, or remove one yourself...") | **OUT** | Not one of the audit's five; scoped narrowly to `failed-verification` markers, in a guard-invoked reference skill (different genre from the five entry skills). Carries a unique, non-redundant instruction — "including when retyping a claim — let the next check run clear it" — not restated anywhere else. Collapsing would delete that nuance. |
| 9 | `skills/publish/SKILL.md:110` ("...by either disposition or by hand...") | **OUT** | Unrelated context: prohibits tag deletion/history rewriting, not content-authorship. Different rule entirely. |

**Vendored files (Trap 1):** `skills/find-sources/references/*.md` (11 files) — confirmed
untouched. Each carries "Do not hand-edit this file; re-vendor from upstream to update
it," which is the frozen-third-party-fork vendoring rule, not the refrain. Not part of
this sweep at all; verified with `git diff` that none of the 11 files appear in the
diff.

**Contrast case:** `skills/import-source/references/*.md` (Task 6, our own prose) —
checked; carries no hand-write/vendoring phrasing at all, so nothing to rule on there.

### Item 10 — prohibition cuts

| Site | Ruling | Reason |
|------|--------|--------|
| `skills/find-sources/SKILL.md:108` ("not as a raw dump") | **CUT** | Recipe already present alongside ("per candidate: title, authors, year, venue; identifiers...; and enough provenance..."). |
| `skills/verify-citations/SKILL.md:27` ("not in raw run order") | **CUT** | Recipe already present alongside ("grouped by check id as the CLI reports them"). Left the trailing "not an interleaved dump" alone — that's part of the *rationale* clause ("a person triaging results wants X, not Y"), not a second standalone prohibition the audit named. |

### Trap 2 — test pins checked before editing

Grepped `tests/` for every exact substring I was about to remove or alter, before
touching it:

- `tests/test_skill_files.py:36` — `"Do not create directories or files by hand"` —
  pins **setup-vault**, ruled OUT above (site 7), left untouched, no pin change.
- `tests/test_project_flow_skill.py:140` — `"the person consents; the CLI writes"` —
  the model phrase, already the target token. My edit to `project-flow/SKILL.md:84`
  preserves this substring verbatim (moved from before a period to before an em
  dash — substring match unaffected).
- `tests/test_project_flow_skill.py:149` — `"never prose written by hand"` — I
  preserved this substring verbatim too (see below). **No pin changed.**
- Grepped for any pin on the exact strings I removed from import-source, publish,
  verify-citations, and find-sources (`"Never hand-write a literature note"`,
  `"Never hand-write a status"`, `"Never hand-write a result"`,
  `"Never hand-write a line into"`, `"not as a raw dump"`, `"not in raw run
  order"`, `"is a CLI verb call"`, `"the CLI does all of that already"`,
  `"appended through the CLI verb"`) across all of `tests/` — zero hits. Also
  checked `tests/test_import_source_skill.py`, `tests/test_publish.py` (its
  `test_publish_skill_routes_every_mechanical_act_through_a_verb` token loop),
  `tests/test_finding_cli.py` (verify-citations token loop), and
  `tests/test_searchlog_cli.py` (find-sources token loops) line by line — none
  assert against the sentences edited here. **No pin changes needed for these
  four sites.**

### Trap 3 — the template variant

`tests/test_templates.py:100` pins, byte-for-byte, whole-file, the vault template
`research_vault/templates/vault/AGENTS.md`, which contains "evidence notes exist
only by projection, never by hand." **Ruling: OUT**, left untouched. The brief scopes
this task to "the SKILL.md files the greps hit"; this is a shipped vault template, not
a SKILL.md, and is pinned as an exact byte-for-byte whole-file comparison (a larger,
unrelated blast radius to touch for a purely stylistic gain). Stating the ruling
explicitly per the brief's instruction, since item 9's goal is one token per site and
this is a site left over.

## Per-changed-site: original, replacement, what a reader loses

### 1. `skills/project-flow/SKILL.md:84`

**Superseded by fix round 1 — see "Fix round 1" section at the end of this report
for the final state.** The first draft below only merged two sentences by
punctuation and left both "the CLI writes" and "never prose written by hand"
standing side by side, which the fix-round-1 review correctly identified as the
duplication item 9 exists to remove. Kept here for the record of what actually
happened at commit `eb54ab6`; superseded at the follow-up commit.

- **Original (pre-task):** "Compose and explain the finding; the person consents;
  the CLI writes. Every mechanical act in this skill — events, statuses, tags,
  holds, acknowledgments — is a CLI verb call, never prose written by hand."
- **First-draft replacement (`eb54ab6`, insufficient):** "Compose and explain the
  finding; the person consents; the CLI writes — every mechanical act in this
  skill (events, statuses, tags, holds, acknowledgments) is a CLI verb call, never
  prose written by hand." — 204 characters to 203; both "the CLI writes" and
  "never prose written by hand" still stood side by side.
- **Final replacement (fix round 1):** "Compose and explain the finding; the
  person consents; the CLI writes — every mechanical act in this skill (events,
  statuses, tags, holds, acknowledgments) is a CLI verb call." — the redundant
  "never prose written by hand" clause is cut entirely, matching the pattern
  already applied to import-source/verify-citations/find-sources (state "the CLI
  writes" once; drop the trailing hand-write negation unless it carries a unique
  scope qualifier, as publish's does). "Is a CLI verb call" is kept: it is not a
  restatement of "the CLI writes" (who writes) but a distinct classification of
  the act (what kind of call it is), the same pairing used at every other
  collapsed site.
- **What the reader loses:** nothing. The enumeration (events, statuses, tags,
  holds, acknowledgments) is preserved verbatim — none of the five are elaborated
  elsewhere in this file, so this is the only place a reader learns what counts as
  a "mechanical act" here. The doctrine itself ("not hand-written, always via a
  CLI verb") is now stated exactly once, via "the CLI writes" plus "is a CLI verb
  call", instead of twice.

### 2. `skills/import-source/SKILL.md:13`

- **Original:** "...never invent or guess one. Every mechanical act below is a CLI
  verb call: you compose and explain, the CLI writes. Never hand-write a literature
  note, a managed region, a `verified` event, or a review-inbox entry."
- **Replacement:** "...never invent or guess one. Every mechanical act below — a
  literature note, a managed region, a `verified` event, a review-inbox entry — is a
  CLI verb call: you compose and explain, the CLI writes."
- **What the reader loses:** nothing. Checked each enumerated item against the rest
  of the file: "literature note" is the file's central topic (discussed throughout);
  "managed region" is explained at line 21 ("managed region above the free region,
  which survives untouched"); "verified event" and "review-inbox entry" are restated
  with operational detail at lines 108–109 and 113 (the four-state table and the
  honesty-guard paragraph). The negation ("Never hand-write") is dropped in favor of
  the equivalent affirmative already established in the same sentence ("the CLI
  writes"); nothing enumerated is now unstated anywhere in the file.

### 3. `skills/publish/SKILL.md:11`

- **Original:** "Every mechanical act below is a CLI verb call: you compose and
  explain, the person chooses, the CLI writes. Never hand-write a status, a
  `verified` event, a tag, an acknowledgment, or a review-inbox entry — not in a
  note, not in frontmatter, not anywhere."
- **Replacement:** "Every mechanical act below — a status, a `verified` event, a
  tag, an acknowledgment, a review-inbox entry — is a CLI verb call: you compose
  and explain, the person chooses, the CLI writes — never by hand, not in a note,
  not in frontmatter, not anywhere."
- **What the reader loses:** nothing — this was the site the brief specifically
  flagged as carrying an enumeration that must not be silently dropped. Checked:
  "status" is detailed at lines 48/49/92 (`mark-published`/`mark-parked`/
  `mark-withdrawn` each setting a status value); "verified event" at lines 37/48/91;
  "tag" at lines 48/91/100/102/110; "acknowledgment" at the whole `## Acknowledgments`
  section (lines 76–84, not shown in this file's own line range but present) and
  lines 77/83. All five enumerated nouns are kept in the replacement anyway (moved
  from the "never hand-write" clause into an appositive on "every mechanical act
  below"), so no enumeration is lost even setting the redundancy aside. The
  location-scope clarifier ("not in a note, not in frontmatter, not anywhere") is
  preserved verbatim, since it isn't restated elsewhere and is the one piece of this
  sentence that isn't pure restatement of the doctrine.

### 4. `skills/verify-citations/SKILL.md:9`

- **Original:** "...reporting its four-state results grouped by check id. Never
  hand-write a result, a `verified` event, or a review-inbox entry — the CLI does
  all of that already, inside `verify` itself."
- **Replacement:** "...reporting its four-state results grouped by check id — the
  CLI writes a result, a `verified` event, and a review-inbox entry, inside `verify`
  itself."
- **What the reader loses:** nothing. "Result"/"verified event" are restated with
  full operational detail in the four-state table two lines below (MATCHED row:
  "You never write an event either way"; UNMATCHED row: "Already recorded in the
  review inbox by `verify` itself — do not also file it yourself"). The "inside
  `verify` itself" nuance (the write happens as a side effect of running verify, not
  a separate step) is preserved verbatim.

### 5. `skills/find-sources/SKILL.md:91` (drifted from :71)

- **Original:** "...this is a PRISMA-S trail a methods reviewer reconstructs, not a
  search index. Never hand-write a line into `search-log.md` yourself, for either
  record kind — every append is this verb, and the file is append-only (a rewritten
  line is a lint failure, the same guard `inbox/review-queue.md` and `log/` carry)."
- **Replacement:** "...this is a PRISMA-S trail a methods reviewer reconstructs, not
  a search index. The CLI writes every line into `search-log.md`, for either record
  kind — every append is this verb, and the file is append-only (a rewritten line is
  a lint failure, the same guard `inbox/review-queue.md` and `log/` carry)."
- **What the reader loses:** nothing. Only the negation clause ("Never hand-write...
  yourself") was replaced with its affirmative equivalent ("The CLI writes..."). The
  substantive, non-refrain half of the sentence — the append-only file discipline and
  the shared lint guard with `inbox/review-queue.md` and `log/` — is untouched,
  verbatim.

## Item 10: per-changed-site detail

### `skills/find-sources/SKILL.md:108`

- **Original:** "Report results the way the retrieval can be repeated, not as a raw
  dump — per candidate: title, authors, year, venue; ..."
- **Replacement:** "Report results the way the retrieval can be repeated — per
  candidate: title, authors, year, venue; ..."
- **What the reader loses:** nothing — the positive recipe that follows the dash is
  untouched; only the shaping prohibition ("not as a raw dump") is cut, per the
  audit's explicit "cut the prohibition half, keep the recipe" ruling.

### `skills/verify-citations/SKILL.md:27`

- **Original:** "Present the printed lines to the person **grouped by check id as
  the CLI reports them** (the second token on each line), not in raw run order — a
  person triaging results wants \"here is everything wrong with quotes,\" not an
  interleaved dump."
- **Replacement:** "Present the printed lines to the person **grouped by check id as
  the CLI reports them** (the second token on each line) — a person triaging results
  wants \"here is everything wrong with quotes,\" not an interleaved dump."
- **What the reader loses:** nothing — the positive recipe ("grouped by check id...")
  and its rationale clause are untouched; only the redundant shaping prohibition
  ("not in raw run order") is cut.

## Judged grep (Step 3)

```
$ grep -rn "not as a raw dump\|not in raw run order" skills/
(no output)

$ grep -rn "not as a raw dump\|not in raw run order" . --include="*.md" --include="*.py"
docs/2026-08-22-skills-layer-audit.md:135:- **Wrong form, fix**: the shaping prohibitions. `find-sources`' *"not as a raw dump"* and `verify-citations`' *"not in raw run order"* are output-shape instructions written as prohibitions — the arm `writing-skills` measured as performing *worse than no guidance*. Both already carry their positive recipe alongside ("per candidate: title, authors, year, venue; identifiers; enough provenance…"; "grouped by check id"). **Cut the prohibition half, keep the recipe.**
docs/2026-08-22-skills-layer-audit.md:159:        ["not as a raw dump" find-sources:88; "not in raw run order"
docs/superpowers/plans/2026-08-22-post-q-batch.md:78:- [ ] **Step 2 (item 10):** Delete two prohibitions whose recipes are already present: "not as a raw dump" (find-sources:88), "not in raw run order" (verify-citations:27).
```

Ruling: `skills/` is clean — the only two live sites named by item 10 are cut. The
three repo-wide hits are record documents: `docs/2026-08-22-skills-layer-audit.md`
(the audit itself, quoting the two prohibitions it is diagnosing) and
`docs/superpowers/plans/2026-08-22-post-q-batch.md` (the plan's Step 2, quoting the
same two phrases as the deletion target). Both are deliberately untouched — per
AGENTS.md, `research/`, `analysis/`, completed plans, and accepted ADRs stand as
written, and these are exactly that: the historical record of what item 10 asked
for and found, not live prose subject to the sweep. Fixing this transcript corrects
a false "(no output)" claim in the first draft of this report; it does not change
the underlying ruling, which was always "skills/ clean, record documents
untouched."

## What was tested

- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files` — **8/8 passed**
  (ruff format, ruff lint, mypy, mdformat, yamlfix, pyproject-fmt, json/frontmatter
  lint, append-only records guard).
- `.venv/bin/python -m pytest tests -q` — **1565 passed, 7 skipped** — matches the
  stated baseline exactly. No test files were modified (no pin needed updating,
  since both project-flow pinned substrings survive verbatim and no other site
  edited here was pinned anywhere in `tests/`).

## Self-review

- Re-read every changed sentence after editing: none reads worse than before: each
  is the same length or shorter, keeps the same information, and replaces a
  negation ("never hand-write X") with the plugin's own established affirmative
  token ("the CLI writes"), consistent with item 10's "cut the prohibition, keep the
  recipe" pattern applied to item 9's refrain.
- No pin changed meaning: the two `project-flow` pins survive as literal substrings,
  untouched in content; the `setup-vault` pin was never touched (its site was ruled
  out of scope); no other site had a pin.
- Concern (minor, non-blocking): site 6 (`find-sources/SKILL.md:74`) is a
  boundary call — a sixth spelling of the same vocabulary family, left alone for
  scope discipline since it wasn't one of the audit's named five and isn't a
  negation in the flagged form. Flagging it here in case the coordinator wants it
  swept too in a follow-up.
- Concern (minor, non-blocking): sites 7–9 (setup-vault, evidence-conventions,
  publish:110) share surface vocabulary ("by hand") with the refrain but are
  judged to be distinct rules on inspection; each ruling is recorded above with
  reasoning in case a reviewer disagrees with the judgment call.

## Fix round 1

The coordinator's review came back **spec compliant**, with two open findings and
two of my flagged judgment calls resolved in my favour by evidence (the sixth-spelling
concern at `find-sources/SKILL.md:74` was checked against `git show
82b23a9:skills/find-sources/SKILL.md` — the commit that wrote the audit — and both
`:54` and `:71` already existed at that point, confirming the audit's five-site count
was deliberate, not a miscount that missed a sixth occurrence).

### Finding 1 (Important, CONFIRMED) — false transcript in the judged-grep block

The original "Judged grep (Step 3)" section printed the repo-wide command as
`(no output — checked repo-wide)`. That command actually exits 0 with three hits, all
in record documents (`docs/2026-08-22-skills-layer-audit.md:135`,
`docs/2026-08-22-skills-layer-audit.md:159`,
`docs/superpowers/plans/2026-08-22-post-q-batch.md:78`) — the audit and the plan
quoting the two prohibitions they diagnose/assign, not live prose. `skills/` itself
was and is clean.

**Fix:** replaced the judged-grep block above with the command's real output and an
explicit ruling (`skills/` clean; the three hits are record documents, deliberately
untouched per AGENTS.md's "research/, analysis/, completed plans, and accepted ADRs
stand as written"). No code or commit-body change was needed — the commit message
never repeated the false claim, only the report did.

### Finding 2 — `project-flow/SKILL.md:84` did not actually collapse

Confirmed: the round-1 edit was a punctuation join only. "The CLI writes" and "never
prose written by hand" stood side by side after the edit, which is exactly the
duplication item 9 exists to remove, at a site the audit named as one of the five.

**Fix:** collapsed properly. `skills/project-flow/SKILL.md:84` now reads:

> Compose and explain the finding; the person consents; the CLI writes — every
> mechanical act in this skill (events, statuses, tags, holds, acknowledgments) is a
> CLI verb call.

"Never prose written by hand" is cut; the doctrine is now stated exactly once ("the
CLI writes"). "Is a CLI verb call" is kept — it's a distinct classification (what kind
of act), not a restatement of who writes, the same pairing every other collapsed site
uses. The enumeration (events, statuses, tags, holds, acknowledgments) is unchanged,
since none of those five are elaborated elsewhere in this file.

The pin at `tests/test_project_flow_skill.py:149`
(`test_project_never_hand_writes_a_mechanical_act`) moved in the same commit, from
asserting the now-deleted "never prose written by hand" substring to asserting the
two phrases that now carry the doctrine:

```python
assert "the CLI writes" in text
assert (
    "every mechanical act in this skill (events, statuses, tags, holds, "
    "acknowledgments) is a CLI verb call"
) in text
```

### Test evidence, fix round 1

- `.venv/bin/python -m pytest tests/test_project_flow_skill.py -q` — 10 passed.
- `PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files` — 8/8 passed.
- `.venv/bin/python -m pytest tests -q` — 1565 passed, 7 skipped — matches the
  baseline stated for `eb54ab6` exactly.

### Self-review, fix round 1

- Re-read `project-flow/SKILL.md:84` after the fix: reads cleanly, no leftover
  redundancy, enumeration intact.
- Re-read the corrected judged-grep block: now an honest transcript, ruling stated
  explicitly rather than implied.
- No other site touched; no other pin touched.
