# Workflow comparison: History Notes (Zotero + Obsidian) vs research-vault

Disposition: historical (2026-09-06) [should-be-scoping-review]

Comparison note, 2026-08-24. Workflow only — process and information flow, not UI or plugin
mechanics for their own sake.

**Verified (2026-08-24):** independent re-verification of both sides — internal claims against
this repo at HEAD, external claims against `obsidian-history-vault` at `a3d22d0a` (exact HEAD of
master) and the live pages. All eight gaps and the reverse-strengths list are real; the
starter-vault evidence checked byte-exact. Seven substantive citation errors and the
precision drift were folded in `6809fa0` (author re-verified each against primary source first).
Dispositions routed: the three cheap adoptions → issue #18 (post-slice, instrument freeze);
entity layer and the §7 frontmatter trade-off → spec §10 deferrals with triggers; query surface,
manuscript assembly, and the task aggregator → the Obsidian ecosystem on the portable vault;
archive notes → declined (YAGNI, revisit on real friction).

## How to read this

**Part I** frames both systems from primary sources. **Part II** maps pipeline stages
side by side. **Part III** is what research-vault lacks, ranked by how much workflow it
costs. **Part IV** is the reverse: what research-vault has that History Notes does not.
**Part V** records the five corrections this pass and an independent peer-verification pass
made. **Part VI**
is the recommendation layer — what to do about Part III, split the way this folder's other
comparison and adoption plan are split ("The comparison is what was found. The adoption plan
is what to do about it," `docs/product-landscape/README.md`), just kept in one file here
because the scope is one gap list, not a whole product landscape.

## Evidence rule

History Notes side, read directly (not summarized by an intermediate model):

- `https://publish.obsidian.md/history-notes/01+Notetaking+for+Historians` — the main workflow
  page, fetched as raw markdown via `defuddle` 2026-08-24. This is the source the two diagrams
  the user supplied were drawn from.
- `https://publish.obsidian.md/history-notes/03+Search+Research+Notes` — the search/query
  subpage, same method.
- `github.com/erazlogo/obsidian-history-vault` at commit `a3d22d0a` (2023-05-27, the repo's last
  push) — the actual starter vault the author distributes. File tree pulled via the GitHub API;
  nine representative note files read at their raw-content URLs. This is the primary evidence for
  Part III: it is the only place the workflow's claims are checkable against real files rather
  than a template listing.

research-vault side, read directly from this repository: `research_vault/literature_notes.py`,
`research_vault/frontmatter.py`, `research_vault/__main__.py`, `docs/adr/0003-*.md`,
`skills/evidence-conventions/SKILL.md`, `skills/synthesis-conventions/SKILL.md`,
`skills/publish/SKILL.md`, `skills/verify-citations/SKILL.md`, `CONTEXT.md`. Claims cite
file and line.

Where a claim about History Notes rests on the author's prose rather than a file this pass
read directly, it says so.

______________________________________________________________________

# Part I — What each system is

**History Notes** (Elena Razlogova, Concordia University) is one historian's personally
maintained Zotero+Obsidian setup, written up as a how-to and distributed as a working starter
vault (`obsidian-history-vault`, 142 stars, no license file). It has no admission gate, no
verification pass, and no publish step — its unit of success is "the researcher can find and
assemble their own notes," not "a third party can trust an unread claim." Every mechanical
step (annotate, import, extract, tag, search) is driven by the researcher's own hands via
Obsidian plugins — the guide requires Zotero Integration, Templater, and Dataview for the core
workflow (page 01) plus Advanced URI and QuickAdd for workspace switching (page 03); the starter
vault additionally ships Kanban and Longform (acknowledged in the vault's own `readme.md`, used
for its `03 writing/` Longform project — not covered by the guide's own prose). There is no CLI
and no agent anywhere in the stack.

**research-vault** (this repo) is a Claude Code plugin for a pipeline — question → literature
→ synthesis → draft → submit (`README.md`) — built around **trust-first** output: "every claim
traceable to a real source, zero fabricated citations" (`README.md`). Its unit of success is a
publishable claim that survives a fail-closed gate. An agent composes and explains; a CLI is the
sole writer for every mechanical act (`skills/import-source/SKILL.md`); a human's role narrows to
admission (accepting a source into Zotero) and disposition choices (publish, acknowledge a
finding).

These are different-genus tools solving overlapping halves of the same problem: History Notes is
strong exactly where research-vault is thin (capture, entities, assembly, retrieval), and
research-vault is strong exactly where History Notes has nothing (admission boundary,
verification, publish gate, non-destructive history).

______________________________________________________________________

# Part II — Stage-by-stage map

| Stage                           | History Notes                                                                                                                                                                                                                                                                                                                                                                                     | research-vault                                                                                                                                                                                                                                                      |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Search / discovery              | not covered by the guide — assumes items are already found                                                                                                                                                                                                                                                                                                                                        | `find-sources` skill: 11 bibliographic databases, PRISMA-S search-log provenance, explicitly upstream of Zotero                                                                                                                                                     |
| Admission                       | ordinary Zotero import, no distinct name                                                                                                                                                                                                                                                                                                                                                          | **admission**: named as the sole path to citability; `find-sources` never performs it (`skills/find-sources/SKILL.md`)                                                                                                                                              |
| Annotate                        | Zotero 6 built-in PDF reader, 5-color highlight palette + free comments                                                                                                                                                                                                                                                                                                                           | same tool, research-vault has no opinion on annotation                                                                                                                                                                                                              |
| Import → note                   | Zotero Integration renders one **research note** per Zotero item from a Templater template — fully editable top to bottom                                                                                                                                                                                                                                                                         | `import-note` CLI renders one **literature note** per citekey; frontmatter + a machine-owned **managed region** the CLI regenerates, never hand-edited (`literature_notes.py:211-257`); free prose lives below it, preserved across re-renders (`literature_notes.py:257`, `_split_free`) |
| Atomize multi-topic source      | the system's defining move, not an edge case — the guide explicitly rejects the popular "one literature note per source" pattern: "different annotations from the same source actually might belong in different places in your draft," so a Templater hotkey extracts selected text into a **new file**, with a reciprocal link left in the original (`extract research note from selection.md`) | claims are atomized at the **line** inside one file: `- (quote\|paraphrase\|inference\|open-question) text [@citekey, locator] ^claim-id` (`skills/evidence-conventions/SKILL.md:12-26`); no new file, a stable anchor instead                                      |
| Arrange across sources          | Graph view, backlinks, and a separate `02 analysis/` note type that transcludes claim blocks from multiple research notes (`obsidian-history-vault`, `02 analysis/3. boycotts...md`)                                                                                                                                                                                                              | **synthesis layer**: pages arrange claims across ≥2 sources on one topic (`2+-source threshold`, `skills/synthesis-conventions/SKILL.md:14`), minimum 2 outgoing links (`:18`), registered in `synthesis/index.md`                                                  |
| Entities (people/places/events) | first-class note types in `04 index/` — person, place, event, work notes, each with their own frontmatter (`start-date`, `country`, `occupation`), linked from research notes, rendered as a social/spatial network in Graph view                                                                                                                                                                 | none — no entity note type exists                                                                                                                                                                                                                                   |
| Draft / manuscript assembly     | Longform plugin: a project `Index.md` holds a declarative `scenes:` list ordering per-paragraph/per-subsection files into one compiled document — reordering the argument means reordering the list                                                                                                                                                                                               | a draft is one arbitrary file, no declared convention for its name or shape (`projects/NAME/` formally holds only `question.md` and `search-log.md`); no declarative structure orders it — restructuring means re-cutting prose in place                            |
| Fact-check                      | none                                                                                                                                                                                                                                                                                                                                                                                              | `factcheck-draft`: capped LLM pass per selected claim, non-blocking, files findings (`skills/factcheck-draft/SKILL.md`)                                                                                                                                             |
| Verify                          | none                                                                                                                                                                                                                                                                                                                                                                                              | `verify-citations`: 10 deterministic checks (citekey, DOI, quote byte-match, update-notice/retraction, screening-state, disputed-claim, …), four-state MATCHED/UNMATCHED/UNREACHABLE/SKIPPED (`skills/verify-citations/SKILL.md`)                                   |
| Publish                         | none — a finished draft just *is* finished                                                                                                                                                                                                                                                                                                                                                        | `publish` skill: drains review queue, blocks on retraction-class findings, closes a fail-closed gate on 5 checks (`skills/publish/SKILL.md`)                                                                                                                        |
| Retrieval                       | 6 saved Dataview views: faceted search (15 inputs including keyword, with operators and sort), the same facet engine as a single-column note-title list, a paragraph-scoped drafts search, quick search, 20-latest feed, cross-vault task aggregator (`obsidian-history-vault/meta/dataview/*.js`)                                                                                                | none shipped; frontmatter is flat, "spec §5: flat, Bases-queryable" (`frontmatter.py:1`), for an external Obsidian plugin to use — research-vault ships no query itself                                                                                             |
| History / deletion              | ordinary Obsidian files — delete or overwrite freely                                                                                                                                                                                                                                                                                                                                              | **deprecate, never delete** — excluded sources marked `excluded`, superseded claims keep a `superseded-by` pointer, nothing silently removed (`docs/adr/0003-deprecate-never-delete.md:1-15`)                                                                       |

______________________________________________________________________

# Part III — What research-vault lacks

Ranked by workflow cost, most expensive first.

## 1. No entity layer

`04 index/` in the starter vault holds dedicated note types for people, places, events, and
works — e.g. `Gómez, Manuel Octavio (person note).md` carries `start-date`/`end-date`,
`country:: [[Cuba (place note)]]`, `occupation:: film director`; `1972.03.24 Cuban Film Festival (event note).md` carries its own date range and links to `city::`/`country::` place
notes. Research notes link into these, and Graph view then renders the social/spatial network
for free.

research-vault has two note kinds — literature notes and synthesis pages — and no way to ask
"what do I know about this person" as a first-class object distinct from "which sources mention
them." A biographical or place-based claim has nowhere durable to accumulate outside a claim
line buried in whichever literature or synthesis note happened to cite it.

## 2. No round-trip link back to the source, and no color-coded annotation semantics

Every quote claim in a History Notes research note carries
`[Go to annotation](zotero://open-pdf/library/items/<key>?page=<n>&annotation=<id>)`, and even a
hand-typed, PDF-less note gets a `[local](zotero://select/library/items/<key>)` link (verified in
`01 notes/1. cuban film festival....md`, raw content, 2026-08-24) — navigation is two-way, PDF
page to claim and back. Zotero's 5-color highlight palette carries researcher-assigned meaning
there too: the import template maps hex codes to callout headers (`#ff6666` → "Important,"
`#5fb236` → "Reference," `#2ea8e5`/`#a28ae5` left for the researcher to define), styled by a
`callouts.css` snippet; only the default yellow imports as plain text.

A research-vault claim has neither. `render_claim()` (`literature_notes.py:302-329`) cites
`[@citekey, p. N]` — text, not a link — and shapes every highlight the same way regardless of
color: `annotationText` present → `(quote)`, else a bare `comment` → `(paraphrase)`.

Both are missing for the same reason, not two reasons. Better BibTeX's `item.attachments` call
already returns `annotationColor` and a per-attachment `zotero://open-pdf/...` URI
(`docs/research/prior-art/zotero-bridge-design-space.md:51`; the `open` URI is visible at the
attachment level in the fixture at `tests/test_zotero.py:29`, though that fixture's own
`annotations` list is empty). The exact-match evidence is
`tests/test_cli_live.py:160-185` (`test_normalize_annotation_maps_live_bbt_shape_without_raw_aliases`):
it feeds `normalize_annotation()` a live-shaped annotation dict carrying `"annotationColor": "#ffd400"` and asserts the returned dict does not carry it. `normalize_annotation()`
(`__main__.py:54-79`) is an explicit field allowlist — `type`, `comment`, `pageLabel`, `key`,
`annotationText`, `citekey`, plus optional `context_prefix`/`context_suffix` — that never copies
either value through. Both are dropped at that one normalization boundary, one hop before
`literature_notes.py` ever runs. Restoring them is a two-field change to one function, not new integration
work.

## 3. No manuscript-assembly structure

The Longform plugin's `Index.md` (`03 writing/Your first article/Index.md`) holds:

```yaml
longform:
  scenes:
    - TITLE
    - The first paragraph of your introduction
    - SUBSECTION 1
    - - your paragraph on censorship of cuban cinema
    - SUBSECTION 2
    - - the first paragraph of part 2
```

— a declarative, reorderable manifest over per-paragraph files. This is the literal mechanism
behind the "notes reshuffle into Chapter 1 / Chapter 2" diagram: moving a paragraph between
chapters is a one-line edit to the list, not a cut-and-paste inside prose.

No such assembly convention exists to compare against — a research-vault draft is one
arbitrary file. `projects/NAME/DRAFT.md` is only the CLI's own example path
(`skills/factcheck-draft/SKILL.md:16`, `--draft projects/NAME/DRAFT.md`, any path is accepted);
`projects/NAME/` is formally defined to hold `question.md` (`skills/project/SKILL.md`) and
`search-log.md`, nothing more. Whatever the file is named, there is no declarative structure a
tool could read to answer "what order are the sections in" — reordering the argument means
editing prose in place.

## 4. No query or retrieval surface

The starter vault ships six saved views (`meta/dataview/*.md`, backed by `meta/dataview/*.js`): a
faceted search over 15 inputs (keyword plus 14 filter/sort fields, with date and tag operators —
`search-research-notes.js`); the identical facet engine rendered as a single-column note-title
list instead of the full table (`research-notes.js`); a paragraph-scoped drafts search
(`Drafts.md`, over `writing-notes.js`); a quick keyword search; a 20-latest-notes feed; and a
cross-vault task aggregator.

research-vault's `__main__.py` command list (`inbox`, `search-log`, `verify`, `factcheck`,
`trust-tier`, …) has no query verb — nothing answers "show me every claim tagged `paraphrase`
from 2024, sorted by date" without hand-grepping the vault. Frontmatter is deliberately kept flat,
"spec §5: flat, Bases-queryable" (`frontmatter.py:1`), so an external tool (Obsidian Bases) could
query it, but research-vault itself ships zero canned retrieval.

## 5. No archive/repository description note

`06 archives/Sound Recordings, MOMA, NYC (archive note).md` describes the archive itself — finding
aid URL, reel/tape numbers, a `- [ ] visit archive` task — as a research object independent of any
single cited item. research-vault has no equivalent; admission requires an item to already
exist as a Zotero entry, so there is nowhere to record "this collection exists and I haven't
processed it yet."

## 6. No tag import

The template converts Zotero item tags into a hierarchy: `secondary`/`primary` →
`#source/secondary`/`#source/primary`, any tag ending `-project` → `#project/<name>`, everything
else → `#subject/<tag>` — confirmed live in `01 notes/1. cuban film....md`:
`#source/secondary` `#project/film-censorship`.

`grep -n '"tags?"' research_vault/frontmatter.py research_vault/literature_notes.py research_vault/zotero.py` returns nothing. Zotero item tags never reach the literature note.

## 7. Thin per-note bibliographic metadata

The research-note YAML carries `type`, creators normalized by role (`interviewee`, `director`,
`presenter`, … all folded into a queryable `author` field), `title`, `publication`, `date`,
`archive`, `archive-location`, `citekey` — a full citation visible at a glance, collapsible.

The literature-note frontmatter (`literature_notes.py:217-229`) carries only `citekey`, `type: literature`,
`doi`, `url`, `pmid`, `version`, `accessed`, `fixity-sha256`, `status`, `aliases`. No author, no
date, no archive location. Full bibliographic detail lives centrally in `system/bibliography.json`
(`bibliography.py:16`) instead of on the note — a deliberate anti-duplication choice, but the
practical cost is that opening one literature note does not tell you who wrote it or when.

## 8. No cross-vault task list; no *convention* for a comment field

`comment::` is a standard inline Dataview field on every History Notes research note, exposed as
a column in the faceted search dashboard (Part III §4). It is not aggregated with tasks — those
are separate: `all tasks.md` runs `TASK FROM -"07 writing" SORT file.mtime DESC`, a checkbox-only
query across the vault (and, as shipped, a stale reference — this vault's writing folder is
`03 writing`, not `07 writing`).

The mechanism to carry a `comment` on a research-vault claim already exists — every claim line
accepts arbitrary `[field:: value ...]` pairs, parsed into a `fields: dict[str, str]`
(`claims.py:25`, `claims.py:54-56`). Several keys are already documented this way: the
synthesis-only `[confidence::]` and stance links, and the deprecation/retraction fields
`[status:: deprecated]`, `[deprecated-at::]`, `[deprecated-by::]`, `[reason::]`,
`[superseded-by::]`, and `[retraction-ack::]` (`skills/evidence-conventions/SKILL.md:42-57`) —
but `comment` isn't one of them. A `[comment:: ...]` would parse and round-trip today, but it is
scoped to one claim line, not a note, has no query surface, and isn't a recognized convention
anyone would know to reach for. There is also no equivalent of a cross-vault task aggregator —
the closest thing, the review-inbox, is a verification artifact (warn/hold/alert findings), not a
general-purpose note-to-self.

______________________________________________________________________

# Part IV — What research-vault has that History Notes does not

For balance — the comparison runs both ways.

- **A named admission boundary.** "Admission is the human act of accepting a source into Zotero,
  and it is the only way anything becomes citable" (`skills/import-source/SKILL.md:9`).
  `find-sources` explicitly stops short of it and never writes the evidence layer. History Notes
  has no equivalent boundary — importing into Zotero is just an ordinary step.
- **Machine/human ownership split inside one file.** The managed region is bridge-rendered and
  never hand-edited; free prose sits below it and survives re-renders untouched
  (`literature_notes.py:257`). History Notes' research note is one undifferentiated editable file from
  import onward.
- **Claim-level atomicity with stable anchors.** `^claim-id` derives from a Zotero annotation key
  or a content hash, never render order, so re-rendering never breaks a link
  (`skills/evidence-conventions/SKILL.md:26`). History Notes atomizes at file granularity via a
  manual extraction step.
- **A gated synthesis threshold.** Synthesis pages require ≥2 sources on the same topic and ≥2
  outgoing links before they're allowed to exist, and must be registered in an index
  (`skills/synthesis-conventions/SKILL.md:14-24`) — preventing the stub/orphan pages an
  unconstrained `02 analysis/` folder permits.
- **Two dedicated verification stages.** `factcheck-draft` (LLM judgment, capped, non-blocking)
  and `verify-citations` (10 deterministic checks, four-state results) — nothing in History Notes
  checks a claim against its source after import.
- **A fail-closed publish gate.** Retraction-class findings block; the gate closes on citekey,
  evidence-layer, quote, update-notice, and DOI checks (`skills/publish/SKILL.md`). A History
  Notes draft is "done" whenever the researcher says so.
- **Deprecate, never delete.** Every state change is a recorded transition, not an overwrite
  (`docs/adr/0003-deprecate-never-delete.md:1-15`). History Notes files can be edited or deleted
  with no trace.
- **PRISMA screening state.** Literature notes carry a `status` field (defaulting to
  `unscreened`, `literature_notes.py:228`), and the full `unscreened`/`included`/`excluded`/`superseded` set
  is enforced by the screening-state check (`lints.py:515`) and adopted from PRISMA/Covidence
  (`docs/terminology.md:49`) — a systematic-review inclusion judgment History Notes' four note
  categories don't encode as durable state.

______________________________________________________________________

# Part V — Corrections this pass made

1. An earlier turn compared the two user-supplied diagrams against the History Notes URL as if
   they were two different systems. The user clarified they're the same source — a visual
   rendering of one workflow, not two. Once the primary source was read directly, the earlier
   "differences" turned out to be real parts of History Notes this repo hadn't fetched yet (the
   `02 analysis`/Longform/entity-note layers).
2. That same pass relied on a WebFetch summary — an intermediate model's paraphrase — instead of
   the raw page. Re-reading via `defuddle` surfaced what the summary had dropped: the exact
   color-hex-to-callout mapping, the `zotero://` URI shapes, the tag-transformation rule, the
   `03 Search Research Notes` subpage, and the `obsidian-history-vault` starter repo. This report
   rests on those raw sources.
3. §8 (comment field) first claimed no mechanism exists, based on grepping the literal string
   `comment` in three files. `claims.py:25,54-56` shows every claim line already accepts
   arbitrary `[field:: value]` pairs — narrowed to "no convention," not "no mechanism."
4. §2 first claimed the round-trip link and color data were simply absent, based on grepping only
   `literature_notes.py`. Tracing the actual Zotero bridge found both arrive from Better BibTeX already and
   are dropped one function later, by `normalize_annotation()`'s field allowlist
   (`__main__.py:54-79`) — narrowed from "absent integration" to "one boundary drops two fields."

Corrections 3 and 4 share a lesson: a grep finding nothing locates where a symptom isn't, not
where a cause is — the repo's own evidence rule (§Evidence rule) exists for exactly this failure
mode, and this pass hit it twice.

5. A second Claude session independently re-verified every internal claim against this repo at
   HEAD and every external claim against `obsidian-history-vault` at `a3d22d0a` and the live
   `publish.obsidian.md` pages. Headline: substance held — all eight gaps and the reverse-strengths
   list were confirmed real, nothing fabricated, the starter-vault evidence verified byte-exact.
   Citation discipline hadn't: two false claims (§8's comment field wrongly said to feed the
   task aggregator; the "one flat file per project" `DRAFT.md` convention doesn't exist), one
   misquote presented in quotation marks (`frontmatter.py:1`, "so it stays Bases-queryable" for
   the actual "flat, Bases-queryable"), one overclaimed "only" (`evidence-conventions` documents
   six more field keys beyond confidence/stance), a scope error (ADR 0004 is about a second
   identity *for a source*, not entities in general), an under-cited fixture (`test_zotero.py:29`
   swapped for the exact-match `test_cli_live.py:160-185`), a missing field
   (`fixity-sha256`), three off-by-a-few line numbers, an undercount (6 saved views, not 5; 15
   filter inputs, not 14), and one recommendation ("cheap, do now") that ignored a standing
   instrument freeze this repo is currently under. All folded in above; none changed a
   conclusion. Verified independently before folding — this session re-derived each claim rather
   than taking the correction on trust, the same discipline corrections 3 and 4 record.

______________________________________________________________________

# Part VI — Recommendations

What to do about Part III's eight gaps, grouped by how they should be closed rather than by the
cost ranking Part III uses — cost to fix and cost to leave open aren't the same ordering.

## Cheap, adopt post-slice

The repo is currently under a pre-slice instrument freeze — "Phases 2+ wait for the pre-slice
batch to merge — instrument freeze" (`docs/superpowers/plans/2026-08-22-plan-s-validation-slice.md:8`).
research-vault is the instrument under test; changing `research_vault/__main__.py` mid-freeze
would be exactly the kind of change that plan is holding open. None of the below is blocked
forever — just not now, and not by this document. Routing any of it past the freeze is the
controller's call, not this file's.

- **Pass `annotationColor` and the `open` URI through `normalize_annotation()`**
  (`__main__.py:54-79` — closes §2). Two fields, one function, exactly where §2 locates the drop.
  Do **not** copy History Notes' hardcoded color→meaning table — that's one researcher's scheme
  baked into a Templater macro. Pass the raw hex through and let `evidence-conventions` decide
  what, if anything, a color means here; hardcoding someone else's taxonomy would be adopting
  their opinion, not their mechanism.
- **Document a `comment` claim field** (closes the field half of §8 — the task-aggregator half
  is a redirect, not a fix; see below). The mechanism already exists (`claims.py:25,54-56`); this
  is a paragraph in `skills/evidence-conventions/SKILL.md` naming `comment` as a recognized key,
  nothing in the parser.
- **Import Zotero item tags into literature-note frontmatter** (closes §6). Frontmatter, not a
  per-claim field — tags describe the source, not one claim. Check `docs/terminology.md`'s
  existing vocabulary before adding the key.

## Redirect to the existing tool ecosystem, don't rebuild

- **Query/retrieval surface (§4) and manuscript assembly (§3)**. The vault is portable markdown
  by design — "packaged to survive its tools" (`docs/adr/0001-vault-outlives-its-tools.md`) — and
  literature-note frontmatter is already kept flat, "spec §5: flat, Bases-queryable"
  (`frontmatter.py:1`). Nothing stops a human opening the same vault directly in Obsidian and
  running Dataview, Bases, or Longform against it — that is precisely the portability the format
  promises. Building a bespoke CLI query verb or a research-vault-native scene-manifest format would
  duplicate tooling the ecosystem already does well, for a workflow stage (browsing, drafting)
  that doesn't touch the trust core. Only build a research-vault-native version if a concrete need
  surfaces that Obsidian's own plugins can't cover.
- **The task-aggregator half of §8.** Same redirect: a Dataview `TASK` query over the portable
  vault gets this for free — it's exactly how History Notes' own `all tasks.md` works. Not worth
  a research-vault-native task type.

## Leave as-is, but name the trade-off

- **Thin per-note bibliographic metadata (§7).** No fix recommended — centralizing bibliographic
  detail in `system/bibliography.json` instead of duplicating author/date onto every literature
  note avoids exactly the drift risk a second copy would create. But that trade-off has never
  been written down as a decision anywhere this pass found, only made implicitly by what
  `literature_notes.py:217-229` happens to include. It should be recorded the way ADR 0004 recorded why
  citekey carries no alias — a line in `docs/terminology.md` or a short ADR, so "nobody got
  around to it" and "this was decided, here's why" stop being indistinguishable from outside.

## Needs a design pass, not a patch

- **Entity layer (§1)**, the highest-cost gap in Part III. This is not a small addition. ADR 0004
  states "research-vault never mints a second identity for a source"
  (`docs/adr/0004-citekey-is-the-only-identity.md`) — scoped to source identity at admission, so a
  person, place, or event note doesn't conflict with it; it falls outside what the ADR decided at
  all. That makes this an *extension* of the identity doctrine to a class research-vault has never
  had to reason about, not a reopening of 0004: does an entity note get verified, carry a
  screening state, participate in `trust-tier`, or sit outside the trust core entirely the way
  `synthesis/` does? Each answer has downstream consequences for `verify.py` and the publish gate.
  This belongs in a brainstorming session and likely a new ADR, not a skill patch and not an edit
  to 0004.

## Skip for now (YAGNI)

- **Archive/repository description notes (§5)**. Solve the immediate need — "this collection
  exists and I haven't processed it yet" — with a documented `inbox/` convention rather than a
  new note type or mechanism. Revisit only if that friction shows up in practice; a speculative
  note type for a need that hasn't materialized is exactly the kind of premature abstraction
  worth avoiding.
