# Task 4 report — find-sources corrections + cross-read wiring (items 5, 7, 11, 12)

Commit: `800c492` *fix: find-sources credential/vendoring corrections + cross-read wiring* (one commit, as required).
Files changed: `skills/find-sources/SKILL.md`, `tests/test_find_sources_vendor.py`. **`references/` and `scripts/` untouched.**

Sources read on this branch at `docs/2026-08-22-skills-layer-audit.md` (C-3 :203, C-5 :233) and `docs/2026-08-22-references-cross-read.md` (findings :5–50, Triage :51). Per the coordinator's mid-task path correction, every path that *ships* — commit body, this report, the test docstring — cites the post-reorganisation form: `research/validation-slice/2026-08-22-skills-layer-audit.md`, `research/validation-slice/2026-08-22-references-cross-read.md`. Nothing in `skills/find-sources/SKILL.md` cites a document path at all (deliberate: the skill ships as a plugin, where `research/` does not exist).

## What was implemented

**Step 1 — C-3 + item 11 fold (our-wiring, triage class 1).** Three edits, all in our own prose:

1. Core workflow step 5: the credential sentence now reads *"Several of these APIs take a credential in the query string, so the fetched URL* is *a credential: never echo an API key, and never paste an un-redacted URL into a report."* followed by a pointer making `redact_url` the authority instead of a copied parameter list.
2. Same paragraph: the polite-pool contact is sourced from `.harness/machine.json`'s `mailto`, else `HARNESS_MAILTO`, with the plain statement that the vendored scripts do not read it and the instruction to export `OPENALEX_EMAIL`/`CROSSREF_MAILTO` from that address before a walk.
3. The vendoring paragraph's *"5 stdlib-only, no-credential Python CLIs"* → *"5 stdlib-only Python CLIs — no bundled credentials, though `paginate.py` reads `OPENALEX_EMAIL`, `OPENALEX_API_KEY`, and `CROSSREF_MAILTO` from the environment when they are set"*. **Scope note:** this third edit is not named in the brief's Step 1 line; it is named in the cross-read finding whose remedy the triage put in class 1 (*"correct the 'no-credential' sentence"*, :49). `stdlib-only` is still true and was kept.

**Step 2 — C-5.** One line appended to the vendoring paragraph: *"Upstream prose describes upstream's corpus and upstream's behaviour, not necessarily this fork's; where a vendored file and this one disagree, this one governs."*

**Step 3 — item 12.** One new `## Vendoring notes: where the vendored files are wrong` section directly beneath the vendoring paragraph, carrying the triage's six annotations and, under a second lead-in, the two class-3 guards. Plus the two routing-table touches the brief names.

**Step 4.** Pin added in the same commit; form gate 8/8; full offline suite green.

## Fidelity table — triage line quoted, beside what shipped

The triage (`research/validation-slice/2026-08-22-references-cross-read.md`, Triage ruling section) sorts the eleven findings into three classes. Class 2 is *"Upstream annotations (one vendoring-note section, post-Q batch)"* and names six; class 3 is *"Upstream defects (report + re-vendor channel; interim SKILL.md guards in the batch)"* and names two. Every shipped bullet is one of those eight — none came from my own reading of an upstream file.

| Triage phrase (quoted) | What shipped |
| --- | --- |
| *"the preprint-fallback three-way contradiction (skill's Europe PMC routing supersedes)"* | Bullet 1: quotes `references/biorxiv.md:12` and `references/medrxiv.md:12`, notes neither mentions Europe PMC though sibling `references/europepmc.md:16-17` documents exactly that route (`SRC:"PPR"`), and rules *"The routing table below supersedes both"*; adds the finding's own note that `references/pubmed.md` never claims preprint coverage. |
| *"the category-separator conflict (three conventions, one host — recorded unverified; a two-curl live probe at slice time settles which form filters)"* | Bullet 2: the three conventions with verified line refs, *"which one filters is unverified"*, the HTTP-200-on-out-of-spec hazard, and *"Until a live probe settles it, treat a category-filtered count as unverified — compare it against the same query unfiltered."* **No live call was made.** |
| *"the stale paginate docstring counts"* | Bullet 3: `scripts/paginate.py:8`'s *"Six of the ten databases here paginate differently"* against the fork's 11 reference files and 5 walkers, with `--list-apis` as the check. |
| *"the phantom NCBI/S2 env keys"* | Bullet 4: `scripts/paginate.py:28-29`; nothing reads either name, no walked API is theirs, exporting them does nothing; names the three that are read. |
| *"biorxiv.md's reconciliation overstatement"* | Bullet 5: `references/biorxiv.md:163-164`'s *"reconciles the retrieved total against `total` and `count_new_papers`"* against reconciliation on `total` alone, `count_new_papers` as advisory note only, exit-4 never involving it, and the un-machine-checked version-vs-first-posting mismatch. |
| *"openalex.md's lossy-inversion guidance (SKILL.md routing row gains the openalex_abstract.py pointer — ours)"* | Bullet 6 (`references/openalex.md:162-172` teaches `{position: word}`, drops duplicate positions, never mentions the script) **and** the routing-table row: `references/openalex.md` (abstracts: `scripts/openalex_abstract.py`, not that file's snippet). |
| *"the DOI-loop bug (guard: never route single-DOI lookups through paginate)"* | Guard 1: *"Never walk a single-DOI lookup with `paginate.py`."* — no `count`/`total` so no terminator, ~50 duplicates, complete result labelled INCOMPLETE; remedy *"a direct `curl` for a DOI, or `--max-calls 1`"*. `N`/`Nd` stay hedged (*"likely behave the same way"*) because the finding never verified them. Also the `scripts/paginate.py` row caveat: *"— never a single-DOI lookup (see the vendoring notes)"*. |
| *"the unredacted-stderr key leak (guard: do not set OPENALEX_API_KEY in the environment when invoking paginate; redaction holds everywhere else via redact_url)"* | Guard 2: *"Do not put `OPENALEX_API_KEY` in the environment of a `paginate.py` run."* — error path prints the raw URL, 403 on an invalid key is exactly the printing case, provenance list and `--dry-run` are redacted and the error path is not, and *"Run any paginate stderr you intend to quote through `redact_url` first."* |

The two class-1 findings map to Step 1 above: *"the credential undercount (merges with the batch's C-3 item — same surface, one edit: say "several", defer to `redact_url`)"* and *"the polite-pool wiring gap (SKILL.md sources mailto from the harness config and states plainly that vendored scripts do not read it)"*. The C-3 card's own decided replacement wording — *"Several of these APIs take a credential in the query string, so the fetched URL* is *a credential"* — ships verbatim; the card's option "either complete the hand-redaction list to all six or replace it with a pointer to `redact_url`'s own set" is resolved to the pointer, which is what the brief picks.

**Where the triage overrode an individual finding.** Six of the findings say the remedy is *"a vendoring-note annotation on biorxiv.md/medrxiv.md"* / *"on openalex.md"*. The triage — the decided set — says **one** vendoring-note section, and `references/` was left untouched. Independent support: hand-editing a vendored file would falsify the same paragraph's *"unmodified except for a provenance header on each"* sentence, in the commit that cites it, and the files carry *"Do not hand-edit this file"*. The brief's *"+ its `references/` where the cross-read says so"* therefore resolves to nowhere.

## Every factual claim checked against the tree

Credential counts (the brief told me to verify these rather than trust it — both hold):

- **Six redacted params:** `skills/find-sources/scripts/_common.py:201` — `REDACTED_PARAMS = frozenset({"api_key", "apikey", "key", "email", "mailto", "tool"})`. Six, and `redact_url` (`:205-220`) lowercases the parameter name before the membership test. The brief's *"6 redacted params live in code, not prose"* is correct, and the old SKILL.md line named four of them.
- **Three query-string-auth APIs:** verified in the vendored references — `references/core.md:23` (`?api_key=YOUR_API_KEY`, alternative to the Bearer header), `references/pubmed.md:21` (`&api_key=YOUR_KEY`, inherited by `references/pmc.md:20` — *"Same E-utilities as PubMed, but with `db=pmc`"* — whose own rate table at `references/pmc.md:237` prices `db=pmc` at 3/sec without a key and 10/sec with one; `pmc.md` never spells the parameter itself), `references/openalex.md:21` (`?api_key=YOUR_KEY`). A fourth API takes a *contact* in the query string rather than a key: `references/unpaywall.md:20` (`?email=` mandatory), and `references/crossref.md:20` (`mailto=`, optional polite pool). So "3" is right for API keys and understates URLs that carry something `redact_url` strips — which is exactly why the shipped sentence says *"take a credential"* and names no number.

Code facts behind the annotations and guards:

- `paginate.py` reads exactly `OPENALEX_EMAIL` (`:207`), `OPENALEX_API_KEY` (`:210`), `CROSSREF_MAILTO` (`:240`); `NCBI_API_KEY`/`S2_API_KEY` appear only in the docstring at `:29`. Now pinned by test.
- `APIS` implements five walkers (`biorxiv`, `medrxiv`, `europepmc`, `openalex`, `crossref`); `references/*.md` is 11 files; `paginate.py:8` says "six of the ten".
- DOI loop: `_rxiv_parse` takes `total` from `message["total"]` (None for a DOI lookup), `step` falls back to `len(records)` when no `count` is reported, and `next_state` is capped only when `total is not None` — so the walk never terminates; `walk()` stops at `--max-calls` with *"the walk is INCOMPLETE"*; `DEFAULT_MAX_CALLS = 50` (`:52`), bioRxiv delay 1.0 s. The `biorxiv` API note does advertise *"an interval (2024-01-01/2024-01-03), Nd, N, or a DOI"*.
- Stderr leak: `fetch()` embeds the raw `url` in all three `RuntimeError` messages (`HTTP {code} from {url}`, `could not reach {url}`, `response from {url} was not JSON`); `walk()` catches `RuntimeError` and calls `fail(str(error))`; `_openalex_url` attaches `api_key` from the environment; the provenance list and `--dry-run` use `redact_url`.
- Reconciliation: `reconciliation.expected = page.total` only; `count_new_papers` produces an advisory note telling the caller to deduplicate by DOI.
- Polite pool: `knowledge_harness/webapi.py:38-43` — `.harness/machine.json` `mailto`, else `HARNESS_MAILTO`, failing closed with *"polite pools are mandatory"*.

**Line numbers: seven deviations from the cross-read, tree governing.** *(Corrected in fix round 1 — the first version of this paragraph said six and misfiled the seventh as "correct as cited". See the fix-round section at the end for the re-derivation.)* Cited → verified at HEAD: `biorxiv.md` 113 → **115**, 140-144 → **142-145**, 154-159 → **156-160**, 161-163 → **163-164**, 170 → **172**; `medrxiv.md` 133 → **135**; `openalex.md` 160-168 → **162-172**. Unchanged from the cross-read and verified as cited: `biorxiv.md:12`, `biorxiv.md:40`, `medrxiv.md:12`, `medrxiv.md:53`, `europepmc.md:16-17`, `paginate.py:8`, `paginate.py:28-29`. The shipped annotations carry the verified numbers. Line refs were kept (rather than replaced by section anchors) because the vendored files are frozen at a pinned commit: they cannot drift without a re-vendor, which is precisely when these notes must be re-checked.

**Never-rename constraint honoured.** `skills/find-sources/scripts/arxiv_atom.py:93` reads `"abstract": collapse_ws(entry.findtext("atom:summary", namespaces=NS))` — the `<summary>` → `abstract` boundary translation, at that exact line, untouched by this commit (the diff covers only `SKILL.md` and the test file). Read to confirm it stands; not edited.

## Tests

New pin in `tests/test_find_sources_vendor.py`: `test_the_skill_names_exactly_the_environment_variables_the_scripts_read` — reads every `os.environ.get`/`os.getenv` string literal out of `skills/find-sources/scripts/*.py` by AST, asserts the set is exactly `{OPENALEX_EMAIL, OPENALEX_API_KEY, CROSSREF_MAILTO}`, and asserts SKILL.md names each. One test pins both new claims: the corrected "no bundled credentials, though `paginate.py` reads…" sentence, and the phantom-keys annotation (`NCBI_API_KEY`/`S2_API_KEY` are dead only while that set holds). AST, not grep, for the same reason `test_skill_contracts` uses AST: a substring scan would match the docstring's own dead names.

```
$ .venv/bin/python -m pytest tests/test_find_sources_vendor.py tests/test_skill_contracts.py -q
64 passed in 3.25s

$ PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files
form: python (ruff format)...............................................Passed
lint: python (ruff)......................................................Passed
types: python (mypy rung-1)..............................................Passed
form: markdown CommonMark (mdformat).....................................Passed
form: yaml (yamlfix).....................................................Passed
form: toml (pyproject-fmt)...............................................Passed
lint: json canonical + skill frontmatter (suite).........................Passed
records: append-only under research/analysis/adr.........................Passed

$ .venv/bin/python -m pytest tests -q
1562 passed, 7 skipped in 93.73s (0:01:33)
```

**8/8** on the form gate. Suite delta accounted: **1561 → 1562**, the one new pin. The gate's first run reformatted both files (ruff-format wrapped one line in the new helper; mdformat re-aligned the two touched tables) and those reformats are in the commit.

## Self-review findings, fixed before reporting

1. **"Authenticate by query string" reintroduced the quibble C-3 defused.** My first draft of the step-5 sentence said *"Several of these APIs authenticate by query string"*. The card's decided wording is *"take a credential in"*, which covers Unpaywall's mandatory email and PubMed/OpenAlex's optional keys without inviting the "those aren't authentication" refutation the card records and rejects. Shipped the card's wording.
2. **The stderr guard first said "redact it by hand first"** — a hand-redaction instruction, in the same commit that deletes the hand-redaction list from step 5. Rewritten to route through `redact_url`.
3. **Dead cross-reference risk.** The vendoring-note bullets say "the routing table below" and step 2 says "the vendoring notes above"; the section sits between the vendoring paragraph and the workflow, so both directions are true as written. Checked after mdformat.
4. **No claim that the upstream defects were reported.** The triage calls filing upstream issues *"an outward act — the author's, optional"*, so the guards' lead-in says only *"until a re-vendor fixes them"*.
5. **Scope discipline.** Dropped a drafted Unpaywall HTTP-422 flourish (accurate, but not in any decided remedy) and kept the routing-table touches to exactly the two the brief names.

## Concerns

1. **One annotation ships unverified by design.** The category-separator bullet records a three-way conflict without saying which form filters, because the triage defers that to a live two-curl probe at slice time. An agent reading it gets a warning and a workaround (compare filtered against unfiltered), not an answer. That is the decided state, not an omission — but it is a live loose end for the slice.
2. **The guards are prose, not mechanism.** Nothing prevents an agent from running `paginate.py --api biorxiv --query <DOI>` or from exporting `OPENALEX_API_KEY`. The triage's own channel for the real fix is upstream re-vendor; these two bullets are interim.
3. **Line refs into frozen files are correct today and silently rot at re-vendor.** The re-vendor step should re-verify this section — nothing in `tests/` enforces that, and I did not add such a test (it would need a copy of upstream to diff against, which the repo does not vendor).
4. **The pin covers the env-var claims only.** The other five annotations and both guards are prose claims about frozen files; they are verified in this report but not executable. Pinning them by test would mean asserting on vendored file contents, which drifts into re-implementing the cross-read as a test suite — out of scope for this task, and worth a card only if a re-vendor lands.

______________________________________________________________________

## Fix round 1 — the deviation ledger (record defect; shipped prose unchanged)

Commit `800c492` → amended to `8e7b136` (same tree, body only). **No file in the working tree changed**; the commit's `--stat` is identical: `skills/find-sources/SKILL.md` 62 lines, `tests/test_find_sources_vendor.py` 41 lines.

### The finding, restated

I shipped **seven** line-number deviations and declared six. The undeclared one — `references/biorxiv.md:142-145`, where the cross-read cites **140-144** — was not merely omitted: the report's ledger filed it under *"Correct as cited"*, which asserts a verification that never happened. That is the Task-3 defect class (a stated claim exceeding what was done) reproduced in the record instead of the code, which is why it outranks a simple miscount. The substance was right — the reviewer confirms the paragraph runs 142-146, so 142-145 is the better range — only the accounting was wrong.

### Re-derivation, mechanically rather than by patching

I did not add a row. Both lists were rebuilt from a fresh mechanical pass, on the reasoning that a count I got wrong once should not be corrected by the same faculty that got it wrong:

1. Enumerate every reference the shipped section actually makes, from the file rather than from memory — a `sed` range over the new section piped through `grep -o` for backticked `file:line` tokens, then `sort | uniq -c`: **14** line-carrying refs, each appearing exactly once.
1. Enumerate every `file:line` citation the cross-read makes: `grep -o` over `docs/2026-08-22-references-cross-read.md`, `sort -u`.
1. Match the 14 against the source's citation of the same fact, one row at a time.

Result — **7 changed, 7 unchanged, 14 accounted for**:

| Shipped in SKILL.md | Cross-read cites | Verdict |
| --- | --- | --- |
| `references/biorxiv.md:12` | `biorxiv.md:12` | unchanged |
| `references/biorxiv.md:40` | `biorxiv.md:40` | unchanged |
| `references/biorxiv.md:115` | `biorxiv.md:113` | **changed** |
| `references/biorxiv.md:142-145` | `biorxiv.md:140-144` | **changed** — the one previously misfiled |
| `references/biorxiv.md:156-160` | `biorxiv.md:154-159` | **changed** |
| `references/biorxiv.md:163-164` | `biorxiv.md:161-163` | **changed** |
| `references/biorxiv.md:172` | `biorxiv.md:170` | **changed** |
| `references/medrxiv.md:12` | `medrxiv.md:12` | unchanged |
| `references/medrxiv.md:53` | `medrxiv.md:53` | unchanged |
| `references/medrxiv.md:135` | `medrxiv.md:133` | **changed** |
| `references/europepmc.md:16-17` | `europepmc.md:16-17` **and** `europepmc.md:14-18` | unchanged — the source cites that file two ways for the same fact; the shipped ref matches the narrower |
| `references/openalex.md:162-172` | `openalex.md:160-168` | **changed** |
| `scripts/paginate.py:8` | `paginate.py:8` | unchanged |
| `scripts/paginate.py:28-29` | `paginate.py:28-29` (also `:29` alone in the same finding) | unchanged |

One ref falls outside both lists and is now stated rather than left silent: the shipped bullet 1 cites **`references/pubmed.md` with no line number** where the cross-read cites `references/pubmed.md:10`. That is a *dropped* ref, not a changed one — the claim it supports ("never claims preprint coverage") is about the file as a whole.

### Second-order pass on the same class

The miscount made me distrust the rest of the report's citation claims, so I re-verified every line reference the report asserts but SKILL.md does not ship — the ones taken from the C-3 card or the cross-read rather than derived by me. All confirmed in the tree this round, by grep:

`references/core.md:23`, `references/pubmed.md:21`, `references/openalex.md:21`, `references/unpaywall.md:20`, `references/crossref.md:20` (the C-3 card's narrower forms; the cross-read cites `core.md:22-23`, `pubmed.md:20-21`, `openalex.md:21-22`, `unpaywall.md:20-22` for the same lines), `_common.py:201`, `redact_url` at `_common.py:205-220` (`def` at 205, last statement at 220, `def fail` at 223 — the cross-read's `193-220` spans the explanatory comment block as well), `knowledge_harness/webapi.py:38-43` (line 38 is the `HARNESS_MAILTO` fallback assignment, "polite pools are mandatory" at 42, close at 43), `paginate.py:207`/`:210`/`:240`/`:52`, `references/pmc.md:20` and `:237`.

Two of these were already run as the pre-completion checks the advisor called for last round (`arxiv_atom.py:93`, `references/pmc.md:20`); the other nine are new this round.

### Test evidence — nothing moved

```
$ .venv/bin/python -m pytest tests/test_find_sources_vendor.py -q
11 passed in 0.45s

$ PATH="$PWD/.venv/bin:$PATH" .venv/bin/pre-commit run --all-files
form: python (ruff format)...............................................Passed
lint: python (ruff)......................................................Passed
types: python (mypy rung-1)..............................................Passed
form: markdown CommonMark (mdformat).....................................Passed
form: yaml (yamlfix).....................................................Passed
form: toml (pyproject-fmt)...............................................Passed
lint: json canonical + skill frontmatter (suite).........................Passed
records: append-only under research/analysis/adr.........................Passed

$ .venv/bin/python -m pytest tests -q
1562 passed, 7 skipped in 91.68s (0:01:31)
```

8/8 on the form gate; suite unchanged at 1562/7, matching the reviewer's own run at `800c492`.

### What changed, precisely

1. `8e7b136`'s commit body: "off in six places" → seven, the seventh listed with the other six, the unchanged list stated explicitly, and the derivation method recorded so the count can be re-checked rather than trusted. The ledger stays in the commit body — per the coordinator's forward-looking note, provenance belongs to the commit log, not to code comments.
1. This report's ledger paragraph: seven declared, `biorxiv.md 140-144 → 142-145` moved out of "Correct as cited" into the deviation list, with a pointer to this section.
1. Nothing else. `skills/find-sources/SKILL.md` is byte-identical to what the review passed.

### Concern added by this round

**My verification claims were not uniformly earned.** Two distinct instances now: last round the advisor caught two report claims ("read only to confirm it stands", the `pmc.md` inheritance) that I had asserted without running the check; this round the reviewer caught a third of the same shape. The pattern is that facts I *derived* (the seven corrected line numbers, all of which survived independent re-sampling) are sound, while facts I *restated from a source document* are where the record slips. Both fixes since have been mechanical enumeration rather than re-reading, which is the right correction, but the standing lesson for whoever picks this up: treat any "verified as cited" line in an agent report as a claim to spot-check, not a result.
