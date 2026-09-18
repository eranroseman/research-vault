# Glossary generation and ADR triage — prior art

Disposition: historical (2026-09-06) [should-be-scoping-review]

Research note, 2026-08-28. Feeds the rethink-audit of the docs subsystem:
(1) the three-way hand-maintained glossary (`CONTEXT.md`,
`research_vault/templates/vault/system/glossary.md`,
`tests/test_templates.py`) and (2) the ADR-0005 incident (a decision record
written `Status: accepted` and committed straight into the numbered register
without review, now being pulled back — see `docs/adr/` currently holding only
0001–0004, an uncommitted `D docs/adr/0005-apply-open-standards-at-applicable-boundaries.md`,
and the untracked `docs/2026-08-28-proposed-adr-and-context-changes.md`).
Method: primary sources only, fetched and — where quoted — verified against
raw source text directly (`curl` + tag-stripped text or raw GitHub markdown),
not accepted as a fetch-tool paraphrase. Repo facts (term counts, test
assertions, git history) verified by reading the files and history directly.

______________________________________________________________________

## 1. Single-source-of-truth glossary generation

**Repo state, verified.** `CONTEXT.md` and the shipped
`research_vault/templates/vault/system/glossary.md` each define 31 terms.
They have already drifted: `Synthesis note`, `System folder`, and `Venue` exist
in the shipped template but not in `CONTEXT.md`. `tests/test_templates.py`
asserts the template's exact bytes as a ~150-line inline Python string literal
(`assert asset("vault/system/glossary.md").read_text() == (...)`) — a
hand-typed golden test, not a generated-and-diffed one, so keeping it in sync
requires a human to re-type the delta into escaped Python on every glossary
edit. This is worse than a checked-in fixture file would be, independent of
the single-sourcing question.

### Mechanisms mature single-sourcing practice actually uses

**Build-time transclusion / include.** OASIS DITA's `@conref`/`@conkeyref`
attributes let one topic pull a canonical content fragment into another at
processing time — "The DITA `@conref`, `@conkeyref`, `@conrefend`, and
`@conaction` attributes provide mechanisms for reusing content within DITA
topics or maps," with `@conkeyref` adding key-based indirection so authors
reference a logical name rather than a brittle file path
([OASIS DITA 1.3 spec, conref](https://docs.oasis-open.org/dita/dita/v1.3/os/part2-tech-content/archSpec/base/conref.html)).
The spec also requires context validity checking on reuse: "DITA processors
compare the restrictions of each context to ensure that the conrefed content
is valid in its new context" — i.e., resolution and validation happen at
build/processing time, not via a separate downstream test suite. Antora's
"partials" are the same idea for AsciiDoc sites: reusable snippets included
into pages via AsciiDoc's `include::` directive, where "changes you make to a
partial will disseminate to all of the pages where you referenced the partial
the next time you build your site" — but reused content is "converted *after*
insertion into the page," inheriting that page's version/module/attribute
context, which is exactly the class of fragility the task asked about: a
partial can render wrong (broken xrefs, wrong heading level) in one consuming
page without erroring
([Antora docs, Partials](https://docs.antora.org/antora/latest/page/partials/)).

**Generation baked together with an enforced parity check.** Microsoft's API
Extractor generates a `.api.md` "API report" from TypeScript source and
commits it to git as "a contract for your library's public interface." CI runs
it *without* the `--local` autofix flag, so a divergence **fails the build**
with an explicit message telling the developer to copy the freshly generated
file over the committed one; the intended next step is "commit the updated
`.api.md` file" and "obtain stakeholder approval"
([api-extractor.com, API Report](https://api-extractor.com/pages/overview/demo_api_report/)).
This is the sharpest real-world analogue to "generate the template from
`CONTEXT.md`, and test that the generated output matches what's committed" —
generation and the parity test are two different steps, and the test fails
loud rather than silently passing a stale file.

**Generation without a built-in guard.** oclif's `readme` command rewrites the
`<!-- usage -->`/`<!-- commands -->`-delimited region of a CLI's `README.md`
from the CLI's own command definitions, leaving hand-written prose around it
untouched — "the readme must have any of the following tags inside of it for
it to be replaced or else it will do nothing," `<!-- usage -->` and
`<!-- commands -->`
([oclif/oclif, docs/readme.md](https://github.com/oclif/oclif/blob/main/docs/readme.md)).
This is closer in shape to the actual proposal (regenerate one marked region,
keep vault-specific prose around it) than API Extractor's whole-file
regeneration — but oclif ships no equivalent CI-fail-on-diff step; that
discipline is left entirely to the consuming project.

**Lint/enforcement after the fact, on already-written prose.** Vale's
`Vocab` mechanism (`accept.txt`/`reject.txt`) flags forbidden terms via a
built-in `Vale.Avoid` rule — it never generates anything, it only scans
existing text and reports. **This repo already evaluated and declined this
exact mechanism for the identical terminology-guard problem**
(`research/prior-art/2026-08-24-vale-evaluation.md`, 2026-08-24): a
`reject.txt` generated from `CONTEXT.md`'s `_Avoid_` lines caught only 3–4
real hits across 248 files, spelling-checking a citekey-heavy corpus was
"effectively 100% false positive," and the repo chose instead to make the
terminology guard "a pytest that parses `CONTEXT.md` at test time — no
generated artifact, so registry drift is structurally impossible," on
AGENTS.md's own rung order: "eliminate the problem > add a mechanism > add a
rule." That decision is the single most relevant piece of prior art for this
audit, because it is this repo's own precedent for the identical question
applied one level down (guard terms, not the glossary body itself).

**Terminology databases (TBX/SDL MultiTerm/Trados).** TBX (ISO 30042,
"TermBase eXchange") is an XML interchange format so different terminology
tools and translators can exchange a termbase across an enterprise
localization pipeline — "designed to support various types of processes
involving terminological data, including analysis, descriptive
representation, dissemination, and interchange (interchange), in various
computer environments," originally a LISA/OSCAR format adopted by ISO TC 37
([ISO 30042:2019](https://www.iso.org/standard/62510.html);
[Wikipedia summary of the standard's own scope statement, cross-checked against the ISO listing](https://en.wikipedia.org/wiki/TermBase_eXchange)).
SDL MultiTerm/Trados is the commercial tooling built on that interchange
model. This solves a different problem than the one in front of us: exchanging
one termbase *between tools and languages*, not deriving a trimmed
audience-specific document *from* prose. It is not adoptable prior art here
beyond confirming that "terminology database" and "generated doc surface" are
different weight classes of problem.

### Failure modes, tied to primary sources

- **Silent drift is not hypothetical — it has already happened.** The
  template and `CONTEXT.md` differ today in three terms, with nobody having
  noticed until this audit read both files side by side. Hand-maintenance
  with a hand-typed byte-exact test has not prevented this.
- **Golden tests only catch divergence after the fact, and can be
  rubber-stamped.** Jest's own testing guidance names this directly: "The goal
  is to make it easy to review snapshots in pull requests, and fight against
  the habit of regenerating snapshots when test suites fail instead of
  examining the root causes of their failure" — commit snapshots and "review
  them as part of your regular code review process," or the mechanism
  degenerates into rubber-stamping
  ([Jest docs, Snapshot Testing](https://jestjs.io/docs/snapshot-testing)).
  API Extractor's design answers this by making divergence a **hard CI
  failure with no auto-fix path** rather than a warning — the closest thing to
  a structural defense against "someone accepts the regenerated file without
  reading it."
- **Generation-step fragility.** Antora's own docs flag that reused content is
  converted in the *consuming* page's context (attributes, xrefs, heading
  depth) — a generator that renders correctly in isolation can still render
  wrong once dropped into a different surface. The vault-specific intro +
  term-subset framing in the proposal is exactly this risk: the generator has
  to reproduce vault framing correctly on every run, not just once.
- **A parity/golden test is not a substitute for eliminating the second
  artifact when elimination is actually available** — this is this repo's own
  stated conclusion for the closely related Vale-vs-pytest decision, and it is
  the frame the audit should apply here too, with one caveat below.

### What this means for the proposal

The Vale precedent's "eliminate" option is not available in the same form
here: the shipped template **must** exist as its own standalone file, because
`research_vault/templates/vault/system/glossary.md` is copied into a vault
that, per ADR 0001, "outlives" its tools — a live pointer back to
`CONTEXT.md` would break the moment research-vault is absent. So the real choice
is between the current state (three hand-synced copies, one of them a
hand-typed Python byte-literal) and a generation step that only runs at
scaffold-template build/dev time — never at vault-runtime — with the parity
check built API-Extractor-style (regenerate, diff, **fail** on mismatch, no
silent auto-fix) rather than Jest's cautionary anti-pattern (regenerate and
blindly accept) or the current hand-typed literal (which has already proven
it doesn't prevent drift). Concretely: replace the hand-typed string literal
in `tests/test_templates.py` with a test that renders the template from
`CONTEXT.md` and asserts equality against the committed file — this converts
today's "assert a fixed string" into "assert generator-output matches
committed artifact," the same shape as API Extractor's report check, and
removes one of the three hand-sync points outright (the test stops being an
independent thing to edit).

### Team-context caveats — Q1

- **Antora's partials** assume a multi-page, often multi-version/multi-repo
  documentation site with component/module boundaries; none of that
  versioning/aggregation apparatus is relevant here — only the underlying
  "one file includes a rendered block from another at build time" idea
  transfers.
- **API Extractor's** "obtain stakeholder approval… many teams configure
  branch policies" step assumes PR reviewers distinct from the author; for a
  solo maintainer the enforceable part is just "CI/pytest fails on diff," and
  the "approval" step collapses to the maintainer's own second look before
  committing the regenerated file.
- **TBX/SDL MultiTerm/Trados** assume an enterprise localization program
  (professional terminologists, multiple target languages, CAT-tool
  interchange) — wildly oversized for one ~30-term English glossary in one
  repo. Cited here only as negative knowledge: don't reach for a termbase
  format, this isn't that problem.

______________________________________________________________________

## 2. ADR-worthiness criteria and review workflow

### Nygard's original 2011 post — verified against raw source

Fetched and tag-stripped directly from
[cognitect.com/blog/2011/11/15/documenting-architecture-decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).

- **What's ADR-worthy:** "We will keep a collection of records for
  'architecturally significant' decisions: those that affect the structure,
  non-functional characteristics, dependencies, interfaces, or construction
  techniques." This is a *scope* filter (architecture vs. not), not a
  reversibility, contentiousness, or cross-cutting-impact filter — those three
  axes the task asked about are **not named by Nygard**. His actual argument
  for writing ADRs at all is the "blind acceptance or blind reversal" risk to
  a future reader lacking context — closest primary-source anchor for
  "surprising without context," but he frames it as *why ADRs have value*, not
  as a triage test for *which* decisions get one.
- **Status states, quoted exactly:** "A decision may be 'proposed' if the
  project stakeholders haven't agreed with it yet, or 'accepted' once it is
  agreed. If a later ADR changes or reverses a decision, it may be marked as
  'deprecated' or 'superseded' with a reference to its replacement." Four
  states total: proposed, accepted, deprecated, superseded.
- **Numbering and reversal:** "ADRs will be numbered sequentially and
  monotonically. Numbers will not be reused. If a decision is reversed, we
  will keep the old one around, but mark it as superseded." Nygard's own
  scheme never discusses what to do with a record that was *never validly
  accepted* in the first place — his numbering rule presumes every numbered
  record passed through the proposed→accepted gate.

### adr.github.io

Fetched and verified against raw text at
[adr.github.io](https://adr.github.io/). It defines the same "architecturally
significant" anchor Nygard uses — "An Architectural Decision (AD) is a
justified design choice that addresses a functional or non-functional
requirement that is architecturally significant," with an Architecturally
Significant Requirement defined as "a requirement that has a measurable effect
on the architecture and quality of a software and/or hardware system" — and
otherwise functions as a portal to templates and papers (MADR, the Zdun et
al. "Sustainable Architectural Decisions" Y-statement work) rather than an
independent essay with its own triage heuristics. **It adds nothing beyond
Nygard's scope filter**; don't over-cite it as an independent source of new
criteria.

**MADR** (linked from adr.github.io; template verified against the raw file
at
[github.com/adr/madr, template/adr-template.md](https://raw.githubusercontent.com/adr/madr/main/template/adr-template.md))
defines its status field as:
`status: "{proposed | rejected | accepted | deprecated | … | superseded by ADR-0123}"`
— adding **"rejected"** as an explicit fifth state Nygard's original four
didn't have. MADR's front matter also carries `decision-makers`, `consulted`,
and `informed` fields (an explicit RACI split) — inherently team-shaped
metadata with no solo-maintainer analogue beyond "decision-makers: me."

### joelparkerhenderson/architecture-decision-record

Fetched and verified against the raw README at
[github.com/joelparkerhenderson/architecture-decision-record](https://raw.githubusercontent.com/joelparkerhenderson/architecture-decision-record/main/README.md).
This is the primary source that actually contains criteria close to what the
task asked about — but every one of them is presented as an *example answer to
a team discussion prompt*, not a fixed rule:

- "What justifies raising an ADR?" → example answer: "We want to create an
  ADR when we want future developers to understand the 'why' of what we're
  doing."
- "What justifies not raising an ADR?" → example answer: "We want to skip an
  ADR when a decision is limited in scope and time and risk and cost, or is
  already covered elsewhere," expanded in the prompt text to: skip when a
  decision is "not about architecture, or are tiny such as minimal-risk or
  self-contained or single-developer, or are already fully covered elsewhere
  such as by standards or policies or documentation, or are temporary such as
  workarounds or proofs of concepts or experiments." **This is the closest
  primary-source match to a reversibility/cost/scope filter**, and it names
  "single-developer" explicitly as a reason to skip — direct textual support
  for scaling ADR-worthiness down in exactly this repo's context.
- Lifecycle example: "Initiating → Researching → Evaluating → Implementing →
  Maintaining → Sunsetting" (explicitly offered as one team's example answer,
  not a mandate).
- Review-before-acceptance example, under the "Teamwork questions for ADRs"
  heading: "We want an ADR to be voted on by stakeholders when the active team
  has 1) completed their research, 2) completed their evaluation, 3) published
  the ADR proposal to the stakeholders with a request for comments and a
  timebox of one week, 4) all stakeholder comments have been incorporated and
  addressed." Governance example in the same section: a priority chain of
  "the CEO, the CTO, the CLO, the team that implements an ADR, the experts on
  the team." Both are explicitly framed by the document's own heading as
  team-oriented example answers to adapt, not universal law.
- **Immutability, stated as an actual characteristic, not an example:**
  "Immutable: Don't alter existing information in an ADR. Instead, amend the
  ADR by adding new information, or supersede the ADR by creating a new ADR."
  This is directly relevant to disposing of ADR 0005 — see below.
- The README also names two newer CI tools —
  [Decision Guardian](https://github.com/DecispherHQ/decision-guardian)
  (surfaces relevant ADRs on a PR touching the code they cover) and
  [ADR Guard](https://github.com/chohan-sarmad-ali/delivery-gates) (a GitHub
  Action that "fails a pull request when watched code paths change without an
  architecture decision record being added or updated," with explicit
  `ADR-Exempt:` waivers) — both assume branch-protected PRs and CI, not a
  solo local-commit workflow.
- **Gap, confirmed by direct grep of the source text:** nowhere in this
  README — nor in Nygard's post, nor on adr.github.io — is there guidance on
  what to do when an unreviewed record has already been committed into the
  same numbered sequence as reviewed ones. No renumbering, no gap-filling, no
  "mark it rejected in place" procedure is specified anywhere in these three
  sources.

### The repo's own heuristic, compared

`docs/2026-08-28-proposed-adr-and-context-changes.md` (the in-flight fix)
states its own test: "a specific decision passes the ADR test: hard to
reverse, surprising without context, and chosen among real alternatives."
Checked against the three sources above: "surprising without context" is the
closest to Nygard's motivating rationale (blind acceptance/blind reversal by
a reader lacking context), but Nygard never states it as a filter axis.
"Hard to reverse" and "chosen among real alternatives" (contentiousness) are
**not named by any of the three primary sources examined** — joelparkerhenderson's
"limited in scope and time and risk and cost" is adjacent to
"hard to reverse" but not identical, and none of the three sources use
alternatives-contentiousness as a named test. The repo's three-part test is a
tighter, original synthesis that goes beyond what the primary sources state
outright — worth knowing precisely so the audit doesn't credit unwritten
"prior art" for a heuristic this repo actually invented.

### Grounding against the ADR-0005 incident

Commit `fd2f81f` added `docs/adr/0005-apply-open-standards-at-applicable-boundaries.md`
with `Status: accepted (2026-08-28)` directly — no `proposed` stage, no
separate review pass. As of this research, the working tree carries an
uncommitted `D docs/adr/0005-apply-open-standards-at-applicable-boundaries.md`
alongside the new proposal document, which states plainly: "an unaccepted
draft was placed in the ADR register" and "Do not reserve ADR 0005 until a
decision is approved."

Set against the sources:

- **Nygard's status semantics were violated at the moment of authorship, not
  just procedurally.** "Proposed" exists in his scheme precisely for when
  "stakeholders haven't agreed with it yet." For a solo maintainer,
  "stakeholders" reduces to a deliberate, separated-in-time second pass — the
  ADR skipped that state by being written straight to `accepted`.
- **None of the three sources tell you how to un-write a wrongly-accepted
  ADR that already occupies a slot in a monotonic sequence.** The repo's
  invented rule — spend a number only at acceptance time, keep drafts in an
  unnumbered proposal document until then — is a real gap-fill, not an
  application of settled prior art, and it is *stronger* than what Nygard
  specifies (his rule, "numbers will not be reused," presumes every number
  was validly spent; the repo's rule prevents the bad spend from happening at
  all).
- **The disposal method in flight (straight `git rm`) is in tension with the
  one immutability convention a primary source actually states.**
  joelparkerhenderson: "amend the ADR by adding new information, or supersede
  the ADR by creating a new ADR" — not erase it. MADR's status vocabulary
  offers the same alternative directly: mark it `rejected` and keep it, rather
  than delete it. Neither says deletion is wrong, but both describe an
  alternative (mark-and-keep) that the current fix doesn't use. This is worth
  a deliberate decision by the audit, not a default.

### Team-context caveats — Q2

- Nygard's proposed/accepted split is the one piece of primary art here that
  **already fits solo maintenance without modification** — it needs no
  scaling down, only actually being used (i.e., not skipping straight to
  `accepted`).
- joelparkerhenderson's stakeholder vote, one-week comment period, and
  CEO/CTO/CLO governance chain assume a multi-person org; scale down to: the
  "review" step becomes a distinct second pass by the same maintainer (or a
  code-review skill/subagent), separated in time or context from the drafting
  pass, before flipping `proposed` → `accepted`. The goal — the same pass that
  drafted it doesn't also approve it — survives; the machinery (voting,
  cross-person timeboxing) does not.
- MADR's `decision-makers`/`consulted`/`informed` RACI fields have no
  solo-maintainer content; either drop them or collapse to a single name.
- ADR Guard / Decision Guardian assume branch-protected PRs in CI. A solo,
  local-commit workflow without mandatory PRs would need a local/pre-commit
  hook to get the same *mechanical* trigger; absent that, per this repo's own
  AGENTS.md ladder ("eliminate the problem > add a mechanism > add a rule"),
  "don't accept your own draft" is presently a **rule**-tier fix, not a
  mechanism, unless a hook is added.

______________________________________________________________________

## Dead ends / negative knowledge

- **adr.github.io adds no heuristics beyond Nygard's "architecturally
  significant" scope filter** — it is a portal to templates and papers, not
  an independent essay; don't cite it as a second, distinct source of
  criteria.
- **None of Nygard, adr.github.io, or joelparkerhenderson's README discuss
  renumbering, marking-rejected, or removing an ADR that skipped review and
  landed in the same numbered sequence as reviewed ones** — confirmed by
  direct grep of the joelparkerhenderson raw source for
  reversib/contentious/renumber/sequence terms, and by reading Nygard's full
  post. The repo's in-flight fix is original synthesis filling a genuine gap
  in the primary sources, not an application of a settled convention.
  Deletion vs. mark-rejected-and-keep is a live design choice these sources
  leave open, not one they resolve.
- **TBX/ISO 30042 and SDL MultiTerm/Trados solve terminology interchange for
  localization, not "one prose glossary generates a trimmed derivative doc."**
  Not adoptable prior art for this repo's problem beyond that scoping note.
- **oclif's README-marker regeneration has no built-in staleness guard**
  (unlike API Extractor) — if this shape is adopted for the vault glossary,
  the parity check has to be built separately, same as this repo already
  plans; oclif is prior art for the "regenerate a marked region, leave prose
  around it" shape only, not for the enforcement half.
- **Fetch failures, and how they were worked around:** `oasis-open.org/docs/dita/dita.html`
  and the OASIS DITA committee landing page returned 404/portal-only content;
  the versioned spec path `docs.oasis-open.org/dita/dita/v1.3/os/part2-tech-content/archSpec/base/conref.html`
  was used instead and is the actual normative source. `docs.vale.sh/topics/vocab/`
  returned 404 during this research session (the Vale docs site has
  apparently restructured since 2026-08-24); rather than re-derive Vale's
  mechanism from a dead link, this note relies on the repo's own
  `research/prior-art/2026-08-24-vale-evaluation.md`, which fetched
  `docs.vale.sh/llms-full.txt` directly and additionally confirmed the
  mechanism empirically by running the Vale binary — a stronger source than a
  fresh doc-page fetch would have been anyway.
- **Quotes from Nygard's post, adr.github.io, and the joelparkerhenderson and
  MADR templates were all verified against raw fetched text (`curl` +
  tag-strip, or raw GitHub markdown) rather than accepted as WebFetch-tool
  paraphrase** — the initial WebFetch summaries for these four sources were
  cross-checked and matched the raw text on every quote used above.
