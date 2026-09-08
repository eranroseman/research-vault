# Ingest Redesign Implementation Plan — Part A: retire, rename, capture, add, doctor

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the vault's import path with the capture side of the ingest design: retire the auto-export, archive, screening-state and managed-region machinery; rename `citekey` to `citationKey`; build the capture verb, the gitignored `fulltext/` layer, the lifecycle linter, re-key propagation and the captured-set lint; rewrite doctor; add the Path A `add` verb; close open points 07–09; rewrite the capture-source and setup-vault skills. The compile wrapper, its tracers, the write-capable live legs and the closing docs are Part B (`docs/superpowers/plans/2026-09-07-ingest-redesign-b-compile.md`), which starts after this part merges to `main`.

**Architecture:** Zotero is the source of truth and capture is the sole writer of the literature note (`literatures/<citationKey>.md`), the text layer (`fulltext/<attachment key>.md`) and the CSL file (`system/bibliography.json`). Identity is the Zotero item key qualified by the server id; the citation key is the name. One lifecycle linter (`research_vault/lifecycle.py`) classifies every note from three local-API reads and runs at capture and at verify through one code path; the pre-commit leg is held. Propagation (`research_vault/propagate.py`) is the one vault-wide mutation and ships in the same plan. Compile is adopted unmodified and wrapped in Part B; this part leaves `wiki/` a guarded machine surface that nothing writes into yet.

**Tech Stack:** Python 3.11+ stdlib only (`urllib`, `json`, `hashlib`, `html.parser`, `subprocess`, `pathlib`). pytest with `monkeypatch` fakes; two live Zotero 10.0.1 instances (production `localhost:23119`, test `localhost:23129`). No new dependency.

**Spec:** `docs/superpowers/specs/2026-09-04-import-redesign-design.md` (the active spec; §9 is its fact register). Also binding: `docs/superpowers/specs/2026-09-05-assembly-design.md` decisions 12, 17, 22, 28, 29 and §9; ADR 0001–0003.

**Split:** two parts, one executable stretch each. Part A needs no human attendance. Part B's tracers (Obsidian open, one sitting), its consent dialog on the test instance and its upstream issue do. Every decision below binds both parts; Part B carries no decisions of its own.

## Global Constraints

- **Commit with an explicit pathspec** (`git commit -m "..." -- <files>`; the message precedes `--`). Parallel sessions share this checkout: never revert or restore another session's uncommitted files; report the precondition as unmeetable instead. Every commit message ends with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
- **Offline suite before every commit:** `.venv/bin/python -m pytest tests -q -n auto` from the repo root. Baseline on 2026-09-07: 1838 passed, 7 skipped, 28 s. Pass `-n` on the command line, never in addopts.
- **Form owners, run directly on touched files, never `pre-commit run`** (it stashes onto a stack every worktree shares): `ruff format research_vault tests scripts hooks`, `ruff check research_vault tests scripts hooks`, `mypy research_vault`, `mdformat --number --wrap keep <touched .md files>`, `python -m json.tool --indent 2 --no-ensure-ascii <file> <file>` for JSON manifests. `mdformat` runs only on mdformat-owned files: `research_vault/templates/vault/index.md` is excluded (`tests/test_config_validity.py::_MDFORMAT_EXCLUDED_FILES`, issue #70) because mdformat escapes Obsidian wikilinks in prose; do not feed it that file, and keep wikilinks in skill prose inside code spans, which mdformat leaves alone.
- **Ruff rules that bite new code:** `T20` (no `print` outside `research_vault/__main__.py` and `scripts/`), `C90` (`max-complexity = 28`), `PTH` (use `pathlib`), `S` (no `shell=True`), `DTZ` (timezone-aware `datetime`). mypy rung 1: annotated functions are checked; no `cast()` laundering.
- **Stdlib only.** The package's one runtime dependency (`defusedxml`) is untouched. `pytest-recording`/`vcrpy` are not adopted (spec §7: no recorder).
- **Four-state everywhere.** Every mechanical step returns `Outcome`s in `MATCHED`/`UNMATCHED`/`UNREACHABLE`/`SKIPPED`. An outage never reads as a pass; a skipped check never reads as clean (ADR 0002).
- **Reason codes and check ids are registries.** `Outcome.__post_init__` validates `reason` against `inbox.REASON_CODES` at construction, so a task adds its codes to `REASON_CODES` **before** any `Outcome` uses them. Every change to `REASON_CODES` must also update the `## Reason-code vocabulary` table in `skills/evidence-conventions/SKILL.md` (`tests/test_skill_contracts.py:440-494` requires every code exactly once) and the `reason codes` row of `docs/terminology.md` §4.4. Every change to `inbox.CHECK_IDS` or a doctor probe id updates the matching §4.4 row in the same commit.
- **Deprecate, never delete, for vault records** (ADR 0003): no transition deletes a literature note. Repository artifacts (plans, docs, code) are outside that rule; deleting them is hygiene.
- **No `Disposition:` line** on new Markdown: the marker system was deleted on 2026-09-07 (`7ec2c95`, `8e2721b`).
- **Machine-local facts stay out of the repo.** Nothing commits a local-API key, a Windows path, a server id, or a version count as a constant. Live values come from `python -m research_vault probe`. Before measuring anything, search `docs/research/`: its dated primary-source records settle facts a probe would only re-measure (record 291 of `2026-09-05-zotero-api-reading.md` held Better BibTeX's `item.search` wire key while this plan asserted the wrong one), and a brief that states an API shape without citing a record is a claim to check, not a fact.
- **Deleting a module or a function prunes its `mutation-baseline.txt` rows** in the same commit, by mechanism, not by a hand-written `grep -v`: run the baseline prune below before committing and put `mutation-baseline.txt` on the pathspec. It drops every row whose module file or function definition no longer exists (a method row `func/Class.method` matches on the method name) and prints each row it drops; a deleted module's `research_vault/<module>.py.manifest.json` sidecar (mutate4py's, unenforced) is deleted by hand. The gate computes `found - baseline` (`scripts/mutation_gate.py::new_survivors`), so a stale row never fails a run; the prune keeps the file honest until the next `--update-baseline`. Measured 2026-09-07: the tree already carries one stale row, `research_vault/scaffold.py::func/_okf_probe`, which the first task to run the prune removes (say so in that commit). New modules need no sidecar; the gate writes one on its first run.

```bash
.venv/bin/python - <<'PY'
import ast, pathlib, re
baseline = pathlib.Path("mutation-baseline.txt")
rows = baseline.read_text(encoding="utf-8").splitlines()
defs, keep = {}, []
for row in rows:
    match = re.match(r"^(research_vault/[^:]+\.py)::func/([^:]+)::", row)
    if match is None:
        keep.append(row)
        continue
    module, func = match.groups()
    path = pathlib.Path(module)
    if module not in defs:
        tree = ast.parse(path.read_text(encoding="utf-8")) if path.is_file() else None
        defs[module] = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))} if tree else set()
    if func.rsplit(".", 1)[-1] in defs[module]:
        keep.append(row)
    else:
        print("pruned", module, func)
baseline.write_text("\n".join(keep) + "\n", encoding="utf-8")
PY
```

- **Deletion lists are claims, not orders.** Every name a Files block says to delete carries the line number it had when the plan was written; before deleting it, grep for callers across `research_vault/`, `tests/`, `hooks/` and `scripts/`, and if kept code still uses it, keep it and report the call site as a deviation instead of deleting it or working around it (Task 3's `registry_agency`, called by the kept `check_update_notice`, and `metadata_year`, imported by `identify.py`, are the measured cases). Deleting an exception class also means removing it from every `except (...)` tuple that names it — `cmd_verify` and `_run_disposition` in `__main__.py` name `notes.ManagedRegionError` and `notes.RenderIntegrityError` — because Python evaluates that tuple only when an exception reaches it, so the suite may stay green while a real error is masked by `AttributeError` at runtime. Line numbers in Files blocks are navigation hints to verify by name.
- **Live legs** stay under the existing `live` marker (`RV_LIVE=1`). Write-capable legs additionally require `RV_LIVE_WRITE_BASE` (the test instance, `http://localhost:23129`) and refuse to run against `zotero.DEFAULT_BASE`; `RV_LIVE_WRITE_KEY` optionally supplies a key granted by an earlier **Always Allow** so the leg runs without the dialog. Nothing in the suite ever writes to the production instance.
- **Outward-facing actions need explicit go-ahead in that turn**: Part B's upstream Zotero issue (its Task 6) is not run on plan approval alone; nothing in this part is outward-facing.
- **Scope held by the spec:** annotations (spec §3.2, decision 28) are specified, tested against a fixture, and **not wired into capture**; the pre-commit lifecycle leg is held (invariant 5); substrate absence is deferred (§0); web pages and repositories are deferred (§0).

______________________________________________________________________

## Decisions this plan settles

Each is a plan-level cell the spec left open, or a measurement made on 2026-09-07 while writing this plan that corrects or completes §9. Rename mechanically at plan review if the author prefers another spelling; nothing else changes.

01. **Propagation is plan-and-apply, and the applied plan is the log** (open point 12, closed by spec `692b134` on 2026-09-07; this supersedes the `system/renames.md` rename log this plan first settled on). `propagate` computes a plan — the old→new mapping, the item key behind each old key, the note rename, and every surface it will rewrite with that surface's sha256 as it stands — writes it to `.research-vault/propagate/<operation id>.json`, prints it with the plan's sha256, and applies nothing. `propagate --plan FILE --approved-plan-sha256 SHA` recomputes the plan from the vault as it is *now* and applies only when the recomputed hash equals the approved one; a draft edited in between, or a new surface that started naming the old key, changes the hash and the apply refuses with `UNMATCHED mismatch — plan changed` (exit 1) — the compile wrapper's `PLAN_CHANGED` shape, and the spec's "sanctioning a computation and comparing what ran against it". The applied plan, with `applied_at` and the approved hash, is written to `system/propagations/<operation id>.json`, committed and never rewritten: it carries the mapping, the surfaces and one hash, so it is the record a reader follows an old key forward through and the residue lint's input; a separate rename log would be a copy of it. `system/propagations/` joins `lints._is_append_only_path` (a write-once file is an append-only file that never grows), the pre-tool-use guard's machine surfaces, and the three formatter-ignore templates. Capture takes no such gate: deterministic, idempotent by render-compare, machine-owned trees only.
02. **The review queue is not rewritten on a re-key.** §3.5 lists "review-queue and acknowledgment targets" among propagation's surfaces, but `inbox/review-queue.md` is append-only (`lint_append_only`) and ADR 0003 forbids rewriting records. A re-key re-renders the note, so the note's content hash changes and every acknowledgment scoped to it lapses by scope mismatch — the behaviour `CONTEXT.md` already defines for an acknowledgment. The applied propagation plan under `system/propagations/` is what lets a reader follow an old target forward. Findings written after the rename carry the new key.
03. **Verbs** (open point 04, terminology §4.3): `capture` (replaces `import-note`), `add` (Path A create, then capture), `propagate` (the re-key pass), `compile` (the wrapper; `compile` prints the tool's approval hash, `compile --bundle <path> --approved-plan-sha256 <sha>` applies, mirroring `transaction apply`). Retired verbs: `import-note`, `archive-source`, `staleness`, `backfill-selectors`.
04. **Check ids** (§4.4 coinages): `capture` (capture's own holds), `lifecycle` (the linter; non-closing on every surface — capture aborts on `database-changed`, nothing else blocks; a genuine `UNREACHABLE` from it still returns exit 3 like every other outage, because `verify.surface_decision` waits on any genuine `UNREACHABLE` whatever the closing sets say), `propagation` (the residue check; closing on `commit` and `publish`), `captured-set` (§4.4's seam lint; closing on `commit` and `publish`), `compile` (the wrapper's outcome). `citekey` becomes `citation-key`. Retired: `doi`, `metadata`, `web-archive`, `screening-state`, `autoexport`.
05. **Reason codes**: added `re-keyed`, `merged`, `trashed`, `deleted`, `database-changed` (spec §6), plus the three §6 asks the plan to assign — `stale-key` (a surface still names a key an applied propagation plan mapped away), `no-fulltext` (capture wrote no compile input: absent, partial or empty index — `UNMATCHED` when an attachment exists and has no usable text, `SKIPPED` and never filed when the item has no stored attachment at all, spec §0 at `ac0cfd2`), `recompile-needed` (the ledger's `content_sha256` for a text file differs from the `sha256` the note's `fulltext` list records for that attachment). `unkeyed` (an added item still has no citation key after the ten-second ceiling, §2). Renamed: `not-imported` → `not-captured`. Retired: `superseded-note`, `missing-archive`, `stale`.
06. **Doctor probe ids**: `tree`, `machine-config`, `zotero`, `write-guard`, `fulltext-sync`, `bbt`, `bbt-git`, `plugins`, `path-shim`, `translator-formats`, `compile-tool`, `remote`, `backup`. Retired: `autoexport`, `staleness`.
07. **The CSL file keeps its path**, `system/bibliography.json`; the glossary retires *Bibliography export* as a concept (the whole admitted library), not the file. `bibliography.py` keeps `BIB_PATH`, `BibliographyError`, `load` and gains `write`.
08. **The captured set** (§1.1, §4.4): the citation keys read from the `citationKey` field of every parseable note under `literatures/*.md` that also carries `zotero-item-key`. Not the filenames: a note whose filename disagrees with its recorded key is a re-key awaiting propagation and the linter reports it; a hand-deleted note leaves the set at once, which is when the captured-set lint should fire.
09. **Multi-line strings in frontmatter** (`abstractNote`, `extra`, any snapshot value with a line break): rendered as a list of their `splitlines()` lines; a reader joins with `\n`. A trailing newline is lost; nothing else is. The codec stays flat (foundation §5); no block scalars are added. Single-line values pass through `display_text`.
10. **Attachment links in the note body** are `zotero://open-pdf/library/items/<attachment key>` plus filename, content type and md5. The `file://` URL from `/file/view/url` is a Windows absolute path and §3.6 forbids absolute paths in the repository; the path shim resolves it at use time (doctor's `path-shim` probe, and any future consumer that needs bytes).
11. **Full-text floor** (§3.3 step 3): `FULLTEXT_MIN_CHARS = 500` — four times the largest masthead §9 measured (126 characters) and an order of magnitude below one page of body text.
12. **`dc:replaces` is a list**, measured 2026-09-07 on `/items/top?format=json` (production): `['http://zotero.org/users/16413661/items/T6GF6HH7']`, and one item carried three URIs. §1 and §3.4 say "a Zotero URI"; the linter accepts a string or a list and compares the last path segment of each.
13. **The Better BibTeX library route returns no `Last-Modified-Version`**, measured 2026-09-07: `GET /better-bibtex/library?/My%20Library.json` → 200, `Content-Type: text/plain`, 1,452 items, every `id` equal to `citation-key`, no version header. `/better-bibtex/library?/1/library.json` is 404. Capture therefore reads Zotero's own `Last-Modified-Version` from `/items/top?format=versions` before and after the library read and re-reads the library route once when it moved (§3.3's "re-read unconditionally" made cheap). The library name is read from the item envelope's `library.name`, never hardcoded.
14. **Zotero base URL** (§6): precedence `--base` > `.research-vault/machine.json` key `zotero_base` > `zotero.DEFAULT_BASE`. `DEFAULT_BASE` moves from `verify.py` to `zotero.py`.
15. **Doctor's profile-only facts** (§5: `extensions.zotero.sync.fulltext.enabled`, `sync.storage.protocol`, the Better BibTeX `git` preference, `extensions.json`, the two auto-enrichment preferences) are read from the profile directory named by `machine.json` key `zotero_profile` (measured on this machine: `/mnt/c/Users/eranr/AppData/Roaming/Zotero/Zotero/Profiles/881hrcxd.default`). Absent key → those probes report `SKIPPED — zotero_profile not configured`, never `MATCHED`.
16. **The add-on declaration** (decision 17) is one packaged file, `research_vault/templates/zotero-addons.md`, embedded verbatim in `README.md` (a test asserts the two tables agree). Doctor parses the packaged copy. Rows, ids read from `extensions.json` on 2026-09-07: Better BibTeX `better-bibtex@iris-advies.com` (required), Attachment Scanner `attachmentscanner@changlab.um.edu.mo` (recommended), DOI Manager `zoteroshortdoi@wiernik.org` (recommended, pref `extensions.shortdoi.autoretrieve`; **`appDisabled` today**), PMCID fetcher `zotero-pmcid-fetcher@iris-advies.com` (recommended, pref `extensions.zotero.pmcid.auto`), MarkDB-Connect `daeda@mit.edu` (optional).
17. **Compile tool location and pin**: `claude plugin marketplace add AgriciDaniel/claude-obsidian` then `claude plugin install claude-obsidian@agricidaniel-claude-obsidian`. Doctor reads `~/.claude/plugins/installed_plugins.json` → `plugins["claude-obsidian@agricidaniel-claude-obsidian"][0].gitCommitSha` and compares its prefix to the pin `ad67087` (warn-only). The wrapper finds the CLI at that record's `installPath` + `scripts/claude-obsidian.py`, overridable by `machine.json` key `claude_obsidian_root`.
18. **`wiki/` joins the pre-tool-use guard's machine surfaces.** The tool's engine is the only writer under `wiki/` (its skills forbid host `Write`/`Edit` there: "Do not use host Write/Edit"), so an agent `Write` into `wiki/` is exactly the bypass the guard exists to refuse. Tracer T1 (Part B Task 1) confirms the tool's own session still completes with the guard active.
19. **`fulltext/` is walked by verify's worktree snapshot** (`gitstate.snapshot_worktree` walks the live tree, `.git` excluded), so `okf-frontmatter` attests it as §3.6 intends; the index snapshot used at pre-commit (`git ls-files --stage`) never sees it, so the held leg costs nothing. `structure.EXCLUDED_DIRS` (`.git`, `.raw`, `.vault-meta`) is one shared set, read by `structure.check_reserved` and by verify's frontmatter walk, and `fulltext/` is deliberately not in it — the walk must attest the layer. `stamp.stamp_types` skips `fulltext/` through its own `_SKIP_DIRS = structure.EXCLUDED_DIRS | {"fulltext"}` (Task 6 built it that way), and `check_reserved` needs no skip at all: it opens only files named `index.md` and `log.md`, and a text file is `<8-character key>.md`. (Stamping 1,335 text files per commit buys nothing: the layer carries its type by construction. Task 6's review found the earlier wording here asked one set to do two things.)
20. **`selectors.py` stays** (unused after `backfill-selectors` retires): it is the Web-Annotation context machinery open point 10 defers with annotations, and lane 5 is its consumer. `backfill-selectors` goes because its only input (claim lines in the managed region) retires.
21. **Open point 07** (closed by spec `692b134`, 2026-09-07): an acknowledgment's scope is *derived*, not passed — `inbox.scope_id(check, target, target_hash)` is `sha256(check \0 target \0 target_hash)`, and for a note-targeted finding `target_hash` is the note's `managed-sha256`, the body hash Task 11 writes (`verify._citation_key_hash` reads it from the frontmatter and falls back to the `_note_bytes` digest only for a note capture has not written). The `fixity-sha256` branch is deleted. A changed target yields a different scope id, the ack stops matching and the finding re-fires — `CONTEXT.md`'s rule with no comparison logic to get wrong. Stated so nobody rediscovers it: `managed-sha256` hashes the body, so an ack on a note-targeted finding survives a frontmatter-only change (an item version moving) and lapses when the body moves. The same shape covers a doctor row (`target` a probe id, the hash what the probe observed) should doctor ever file one; nothing in this plan does. **Open point 08**: `skills/evidence-conventions/SKILL.md` is the single definition site of `[retraction-ack:: <code>]`; `publish.py` carries the one module constant `RETRACTION_ACK_FIELD = "retraction-ack"` any future parser keys on (measured 2026-09-07: nothing in the package reads the field; `grep -rn retraction-ack research_vault` is empty), and a test asserts the skill's fenced example uses that spelling. **Open point 09**: `ack` clears the target's `[failed-verification:: <check>/<date>]` marker.
22. **Tracer results land in Part B** under "Tracer results" (Part B Task 1) and as one dated sentence in the spec's §4.3 tracer paragraph.
23. **Invariant 5 / decomposition §15.20** (no branch protection, no dev pre-commit hook): reported in Task 20's final message to the author, unchanged by this plan.
24. **The tool's inbox, belt and braces (§4.3 conflict 2).** Measured 2026-09-07 in `claude_obsidian/capture.py` and `cli.py` at `ad67087`: the tool's `capture plan|apply` take `--inbox <folder>`, which wins over the file and writes no state; the durable key is `"inbox"` in `.vault-meta/capture/config.json` (schema `claude-obsidian.capture-config.v1`, default `"inbox"`, a dot-prefixed folder refused as `INBOX_NOT_VISIBLE`). This design never runs the tool's `capture` — the wrapper calls only `transaction inspect|apply` (Part B Task 2) — so the vault's `inbox/` is never its drop zone, and tracer T3 (Part B Task 1) checks that a compile run writes only under `wiki/`, so nothing lands under `.raw/`. Should the tool's `capture` ever be adopted, point `"inbox"` at a folder other than `inbox/` in that file, or pass `--inbox` on every call.
25. **`linkMode` is not a local-API query filter.** Measured 2026-09-07: `GET /api/users/0/items?itemType=attachment&linkMode=imported_file&limit=3&format=json` answered 200 with three `imported_url` rows. Doctor's `path-shim` probe (Task 16) requests `itemType=attachment&limit=50` and picks the first `imported_file` row client-side; `itemType` filtering itself is honoured.
26. **A vault with no captured notes does not wait on Zotero at verify or publish time** (raised by Task 2's review, 2026-09-07). `verify._staleness_outcome`, retired with the auto-export contract, ran on every network pass and turned a Zotero outage into exit 3 even for a vault with an empty bibliography and no cited claim; `tests/test_publish.py::test_mark_published_waits_when_the_gate_is_unreachable` pinned that and Task 2 deletes it. The behaviour is not carried forward, on purpose: the lifecycle linter is the one Zotero-facing check at verify (invariant 5), it classifies captured notes, and with none there is nothing whose evidence depends on Zotero — blocking publish on an unrelated service being down was a side effect of the retired contract, and no invariant in §1 names it. Kept: with one or more captured notes a genuine `UNREACHABLE` from `lifecycle` still returns exit 3 (decision 04), and with none `lint_lifecycle` returns one `SKIPPED` outcome, `no-identifier — no note carries a provenance tuple`, so the report shows a check that ran with nothing to check rather than a silent absence (ADR 0002). Zotero liveness on its own is doctor's `zotero` probe. Recorded here so the whole-branch review reads it as settled, not open.
27. **The note body carries three mechanical pointers** (spec §3.3 step 5 and §4.4 as revised at `5ba814c`, 2026-09-07; the §4.4 "no forward link" sentence is reversed for an embed). Rendered by `notes.render_body`, in this order: `## Compiled` with one `![[<page path>]]` per path in the ledger's `pages[]` — the path is read, never guessed, by `notes.compiled_pages`, which matches ledger records on `origin.locator == fulltext/<attachment key>.md` for this note's text files; `## Item` with `zotero://select/library/items/<item key>`; the existing `## Attachments` list, whose `zotero://open-pdf/library/items/<attachment key>` links are the third pointer (decision 10); `## Zotero notes`. Consequence the tasks encode: capture writes the note twice in the normal flow — the first capture has no ledger entry and renders no `## Compiled`, the refresh after compile renders it, and the third run is NOOP (Task 13's test). No Part A task asserts a note is complete after one capture. `LEDGER_PATH` has one definition site, `notes.py`; `captured.py` and `compile.py` import it. Better BibTeX's `zotero://select/items/@<citation key>` is not emitted (a name-keyed link would be a fifth propagation surface). Matching on the `fulltext/` locator is deliberate, not incidental: §4.5 makes the wrapper the ledger's only writer and it registers every source as `fulltext/<attachment key>.md`, so a file record that reaches the ledger by another route (the tool's own `capture`, a hand-authored bundle) describes nothing capture wrote, embeds nothing, and is reported by the captured-set lint's structural leg as `not-captured` (Task 15). `pages[]` entries keep their `.md`: Obsidian resolves `[[path.md]]` and `[[path]]` alike (spec `a066604`), and the tool validates the entries as canonical `wiki/`-relative paths, so nothing is normalised.
28. **A check takes its instant as an argument** (spec §7 `verify --as-of`, `692b134`). `research_vault/clock.py::today(as_of=None)` is the one place the package reads today's date — Task 15 creates it, and a test scans the package for any other `now(datetime.UTC).date()` reader. `verify --as-of` and `inbox --as-of` feed it (Task 18), and `verify_state`'s `detection_date`, the date defaults of `record_finding`, `append_entry` and `searchlog`, and `inbox.summary`'s age arithmetic all resolve through it. Stamps that record when something happened — capture's `accessed` and `generated`, a propagation's `operation_id` and `applied_at` — keep reading the wall clock through their `now=` parameters; they are stamps, not checks. The ledger's `refresh_due` is the third dated surface, and the vault is its only reporter (spec §7 at `ac0cfd2`: the tool defines `source_is_stale` but its lint never calls it): the captured-set structural leg (Task 15) applies the tool's own predicate — `due is None or observed is None or observed > as_of or due < as_of` — to `active` records against the same instant and reports `recompile-needed`; `unreviewed` records, which is what the wrapper writes, are never judged. The vault writes no freshness field of its own (`stale_after` retired and reconciled with `refresh_due`). Part A carries no fixture time bomb: the lifecycle fixtures are version maps without dates, capture's tests pin `now=`, and the update-notice tests already pass `detection_date`.

______________________________________________________________________

## File map

Both parts share this map; items marked (Part B) are created or modified there.

Create:

- `research_vault/fulltext.py` — the `fulltext/<attachment key>.md` layer: usability verdict, render, write, hash.
- `research_vault/capture.py` — the capture verb: key resolution, version-checked read pass, note render, text layer, CSL regeneration, NOOP detection.
- `research_vault/lifecycle.py` — the lifecycle linter: three reads, per-object classification, ordered reason codes.
- `research_vault/propagate.py` — the propagation plan, its hash-gated apply, the surface rewrite, the applied-plan records, the residue lint.
- `research_vault/captured.py` — the captured set and the captured-set lint (textual + structural + recompile-needed).
- (Part B) `research_vault/compile.py` — the compile wrapper: selection, `stable_source_id`, ledger records, bundle, tool invocation.
- `research_vault/addons.py` — the add-on declaration parser doctor reads.
- `research_vault/templates/zotero-addons.md` — the declaration (decision 16).
- `tests/fakes.py` — `FakeZotero`, the canned local-API/JSON-RPC double every offline test shares.
- `tests/fixtures/lifecycle/*.json` — trimmed versions maps from the 2026-09-07 sitting.
- `tests/test_fulltext.py`, `tests/test_capture.py`, `tests/test_lifecycle.py`, `tests/test_propagate.py`, `tests/test_captured.py`, `tests/test_compile.py` (Part B), `tests/test_addons.py`, `tests/test_add.py`, `tests/test_capture_live.py` (Part B), `tests/test_capture_source_skill.py`.
- `skills/capture-source/SKILL.md` (replaces `skills/import-source/`).

Modify: `research_vault/zotero.py` (rewrite), `notes.py` (shrink, then new record), `bibliography.py` (shrink + `write`), `verify.py`, `lints.py`, `checks.py`, `events.py`, `inbox.py`, `structure.py`, `stamp.py`, `scaffold.py`, `claims.py`, `publish.py`, `__main__.py`, `paths.py`, `gitstate.py:644`, `hooks/pretooluse_guard.py`, `hooks/posttooluse_lint.py`, `research_vault/templates/vault/{AGENTS.md,index.md,gitignore,editorconfig,markdownlintignore,prettierignore,system/bases/open-questions.base}`, `research_vault/templates/research-vault/machine.json.example`, `CONTEXT.md` (and its symlink `research_vault/templates/context.md`), `docs/terminology.md`, `docs/testing.md` (Part B), `README.md`, `.github/workflows/quality.yml` (Part B), `skills/setup-vault/SKILL.md`, `skills/synthesis-conventions/SKILL.md` (Part B), `skills/evidence-conventions/SKILL.md`, `tests/conftest.py`, `tests/test_skill_files.py`, `tests/test_skill_contracts.py`, `tests/test_doctor.py`, `tests/test_notes.py`, `tests/test_lints.py`, `tests/test_verify_cli.py`, `tests/test_checks.py`, `tests/test_events.py`, `tests/test_templates.py`, `tests/test_structure.py`, `tests/test_scaffold.py`, `tests/test_hooks.py`, `tests/test_cli_live.py`, `tests/test_zotero.py`, `tests/test_bibliography.py`, `mutation-baseline.txt`.

Delete: `research_vault/archive.py` (+ sidecar), `tests/test_archive.py`, `research_vault/templates/vault/synthesis/index.md`, `research_vault/templates/vault/system/templates/synthesis.md`, `research_vault/templates/vault/system/templates/literature.md`, `skills/import-source/` (whole directory), `tests/test_import_source_skill.py`.

______________________________________________________________________

## Interface index

Names later tasks rely on. A task's Interfaces block cites this index; a mismatch here is a plan bug. Where a task body and this index disagreed in the 2026-09-07 pre-flight scan, the index was corrected to the body: the printed code is the authority, and this index is its summary.

```python
# research_vault/zotero.py                                   (Task 9)
DEFAULT_BASE = "http://localhost:23119"
APP_NAME = "research-vault"
ITEM_KEY = re.compile(r"^[A-Z0-9]{8}$")
class ZoteroError(Exception): result: Result            # UNREACHABLE by default
class DatabaseChangedError(ZoteroError)                  # HTTP 412; result UNMATCHED
class LocalApiDisabledError(ZoteroError)                 # HTTP 403; result UNMATCHED
class NotFoundError(ZoteroError)                         # HTTP 404; result UNMATCHED
class Response(NamedTuple): status: int; body: bytes; headers: Mapping[str, str]   # built positionally (status, body, headers) everywhere
def base_for(vault_root, override: str | None = None) -> str
class ZoteroClient:
    def __init__(self, base=DEFAULT_BASE, timeout=5.0, server_id=None, api_key=None)
    def server_info(self) -> dict                        # {"zotero","api","schema","server_id"}
    def item(self, key) -> dict                          # local-API envelope {key, version, data, library, meta}
    def children(self, key) -> list[dict]
    def annotations(self, key) -> list[dict]             # ?itemType=annotation; tested, unwired
    def fulltext(self, attachment_key) -> dict | None    # None on 404
    def file_view_url(self, attachment_key) -> str | None
    def versions(self) -> tuple[dict[str, int], int | None]   # (map, Last-Modified-Version)
    def trash_versions(self) -> dict[str, int]
    def top_items(self) -> tuple[list[dict], int | None]
    def library_csl(self, library_name) -> list[dict]
    def authorize(self, app_name=APP_NAME) -> dict       # {"key","remember"}
    def create_items(self, items: list[dict]) -> dict    # {"successful","unchanged","failed"}
    def ready(self) -> dict
    def attachments(self, citation_key) -> list[dict]   # BBT item.attachments (annotation fallback, unwired)
    def export_csl(self, citation_keys: list[str]) -> list[dict]   # BBT item.export fallback
    # private, but consumed by Tasks 13 and 16 (no public method serves items/top?format=versions or a raw POST):
    def _http(self, url, data=None, headers=None, method=None) -> Response
    def _local_json(self, path) -> tuple[object, dict[str, str]]   # (decoded payload, response headers)
    @staticmethod
    def _version_header(headers) -> int | None                    # Last-Modified-Version, if present

# research_vault/notes.py                                     (Tasks 5, 7, 11)
SNAPSHOT_FIELDS: tuple[str, ...]; TUPLE_FIELDS: tuple[str, ...]; CAPTURE_FIELDS: frozenset[str]
class InvalidCitationKeyError(ValueError)
@dataclass(frozen=True) class Provenance:
    server_id: str; item_key: str; item_version: int; citation_key: str
    attachments: tuple[dict, ...]; fulltext: tuple[dict, ...]; compile_input_sha256: str | None
def note_path(vault_root, citation_key) -> Path
def display_text(value) -> str
def frontmatter_value(value) -> object                    # decision 9
def note_body(text: str) -> str                          # Task 5: the body below the frontmatter
LEDGER_PATH = "wiki/meta/ledgers/source-ledger.json"      # the one definition site; captured.py and compile.py import it
def compiled_pages(vault_root, provenance: Provenance) -> list[str]   # the ledger's pages[] for this note's text files, by locator; [] before the first compile
def render_body(provenance: Provenance, children, child_notes, pages=()) -> str   # ## Compiled (embeds, if any), ## Item, ## Attachments, ## Zotero notes
def body_sha256(text: str) -> str
def validate_managed_witness(note_bytes: bytes) -> tuple[Result, str]
def read_provenance(text: str) -> Provenance | None
def render_note(item_data, provenance, children, child_notes, existing, accessed, generated_at, pages=()) -> str   # children: the whole child list; attachments are filtered inside; pages from compiled_pages
def content_changed(existing_text, candidate_text) -> bool
def generated_at_now(now=None) -> str
def rename_frontmatter_key(text, old, new) -> str        # Task 7's migration

# research_vault/fulltext.py                                  (Task 10)
FULLTEXT_DIR = "fulltext"; FULLTEXT_MIN_CHARS = 500
class TextVerdict(NamedTuple): usable: bool; reason: str
def verdict(response: dict | None) -> TextVerdict
def path_for(vault_root, attachment_key) -> Path
def write(vault_root, attachment_key, item_key, response) -> tuple[Path, str]   # (path, sha256 of file bytes)
def sha256_of(path) -> str

# research_vault/bibliography.py                              (Task 2)
BIB_PATH; class BibliographyError; def load(vault_root) -> dict[str, dict]
def write(vault_root, items: list[dict]) -> Path         # sorted by "id", indent 2, trailing newline

# research_vault/structure.py                                 (Task 6)
EXCLUDED_DIRS = frozenset({".git", ".raw", ".vault-meta"})
def is_excluded(path: Path, vault: Path) -> bool          # consumed by Tasks 14 and 15
def expected_type(relative: str) -> str | None           # None under wiki/ (existing function, new answer)

# research_vault/capture.py                                   (Task 13)
CHECK = "capture"; MAX_READ_RESTARTS = 3; KEY_WAIT_SECONDS = 10
class ItemRead(NamedTuple): item: dict; children: list[dict]; texts: dict[str, dict | None]; version: int
def resolve_keys(client, keys: list[str]) -> dict[str, str | None]
def read_item(client, item_key) -> ItemRead              # restarts on version movement
def capture(vault_root, client, keys, *, now=None, refresh_all=False, key_wait_seconds=KEY_WAIT_SECONDS) -> list[Outcome]
def add(vault_root, client, items, *, collection=None, now=None) -> list[Outcome]   # Task 17

# research_vault/lifecycle.py                                 (Task 12)
CHECK = "lifecycle"; ORDER = ("database-changed", "merged", "deleted", "trashed", "re-keyed", "drift")   # the per-object precedence classify's branch order implements; documentation, never iterated
class Live(NamedTuple): versions: dict[str,int]; trash: dict[str,int]; top: dict[str, dict]
def replaces_keys(relations) -> set[str]
def read_live(client) -> Live                            # raises DatabaseChangedError
def classify(provenance: Provenance, live: Live) -> tuple[str, str]   # (state, detail)
def lint_lifecycle(vault_root, client, provenances=None) -> list[Outcome]   # provenances: list[tuple[Path, Provenance]]
def _provenances(vault: Path) -> list[tuple[Path, Provenance]]   # private, consumed by Tasks 13 and 17; the shape lint_lifecycle takes

# research_vault/propagate.py                                 (Task 14)
PLAN_DIR = ".research-vault/propagate"; RECORD_DIR = "system/propagations"; CHECK = "propagation"
class Surface(NamedTuple): path: str; sha256: str          # a file the plan rewrites, hashed as it stood at planning
class Plan(NamedTuple): operation_id: str; date: str; mapping: dict[str, str]; item_keys: dict[str, str]; surfaces: tuple[Surface, ...]
def plan(vault_root, client, mapping: dict[str, str] | None, *, now=None) -> tuple[Plan | None, list[Outcome]]   # None + outcomes when nothing can be planned
def plan_sha256(plan: Plan) -> str                        # sha256 of the canonical JSON (sorted keys, no applied_at)
def write_plan(vault_root, plan: Plan) -> Path           # PLAN_DIR/<operation id>.json
def read_plan(path) -> Plan
def apply(vault_root, client, plan_path, approved_sha256: str, *, now=None) -> list[Outcome]   # recompute, compare, rewrite, rename, recapture, record
def rewrite_surfaces(vault_root, old, new) -> list[str]  # relative paths rewritten
def read_records(vault_root) -> list[Plan]               # applied plans under RECORD_DIR, oldest first
def lint_propagation(vault_root) -> list[Outcome]

# research_vault/captured.py                                  (Task 15)
CHECK = "captured-set"; LEDGER_PATH = notes.LEDGER_PATH   # one definition site (Task 11)
def captured_set(vault_root) -> dict[str, str]            # citation key -> item key
def lint_captured_set(vault_root, as_of=None) -> list[Outcome]   # as_of: the instant refresh_due is compared against

# research_vault/clock.py                                     (Task 15)
def today(as_of: str | None = None) -> str                # the one reader of today's date; validates as_of as YYYY-MM-DD, ValueError otherwise

# research_vault/compile.py                                   (Part B Task 2)
LEDGER_PATH = notes.LEDGER_PATH; PIN = "ad67087"
PLUGIN_ID = "claude-obsidian@agricidaniel-claude-obsidian"; CHECK = "compile"
def stable_source_id(kind, locator, content_sha256) -> str
def tool_root(vault_root) -> Path | None
def ledger_record(citation_key, provenance, item_data, today) -> tuple[str, dict]
def plan(vault_root, keys, *, today=None) -> tuple[Path, dict]
def apply(vault_root, bundle_path, approved_sha256) -> Outcome

# research_vault/addons.py                                    (Task 16)
class Addon(NamedTuple): name: str; addon_id: str; need: str; auto_pref: str | None
def declared() -> list[Addon]                            # parses templates/zotero-addons.md
def observe(profile_dir: Path) -> dict[str, dict]        # id -> {"active","appDisabled","version"}
def read_prefs(profile_dir: Path) -> dict[str, str | bool | int]   # user_pref("name", value); lines of prefs.js

# research_vault/scaffold.py                                  (Task 16)
def doctor(vault_root, client=None) -> list[Probe]

# tests/fakes.py                                              (Task 9)
ITEM: dict; ATTACHMENT: dict; CHILD_NOTE: dict; FULLTEXT: dict   # the canned local-API envelopes every offline test shares
class FakeZotero:                                        # canned by (method, path + query string)
    def __init__(self, server_id="6LpvURP2E933", library_name="My Library")
    def get(self, path, status=200, body=None, headers=None, method="GET")   # register a canned GET
    def post(self, path, status=200, body=None, headers=None)               # register a canned POST
    def rpc(self, method, result)                        # register a canned JSON-RPC result
    def install(self, client, monkeypatch) -> ZoteroClient   # patches client._http and client._rpc; returns the client
    calls: list[tuple[str, str, dict]]                   # (method, url, headers) in order; an RPC leg logs ("RPC", method, {"params": params})
    _last_post_body: bytes | None                        # Task 17 adds it: the body of the last POST
def canned_item(fake, item=ITEM, children=(ATTACHMENT, CHILD_NOTE), fulltext=FULLTEXT) -> FakeZotero   # registers one whole item the way capture reads it
```

______________________________________________________________________

## Phase 0 — retire, then rename (spec §1.1: "retire, then rename")

Deleting first shrinks the rename surface. Each retire task leaves the suite green on its own. Retired tests are deleted, not skipped; a test that merely mocked retired machinery to reach something that survives is rewritten to reach it directly.

### Task 1: Retire the web-archive machinery (spec §2, §3.2 `archive-url`, §6)

**Files:**

- Delete: `research_vault/archive.py`, `research_vault/archive.py.manifest.json`, `tests/test_archive.py`
- Modify: `research_vault/__main__.py` (import at :15, `cmd_archive_source` :343-364, parser :835-838, dispatch :922), `research_vault/verify.py` (`_archive_outcomes` :724-754 and its call :1041), `research_vault/lints.py` (`lint_web_archive` :573-596, its call `verify.py:1040`, `_MACHINE_OWNED_FRONTMATTER_KEYS` :618-626), `research_vault/inbox.py` (`CHECK_IDS` drop `web-archive`; `REASON_CODES` drop `missing-archive`), `research_vault/frontmatter.py:74-88` (docstring names `archive.set_archive_url`), `skills/evidence-conventions/SKILL.md` (reason-code table: drop the `missing-archive` row), `docs/terminology.md` §4.4 (check-id and reason-code rows), `mutation-baseline.txt`
- Tests to delete: `tests/test_lints.py::test_web_archive_lint_requires_archive_for_a_doi_less_web_source` (:660), `::test_web_archive_lint_accepts_an_archived_web_source` (:673); `tests/test_verify_cli.py::test_archive_resolution_uses_status_and_distinguishes_404_from_outage` (:634), `::test_the_archive_reader_keeps_the_contact_address_out_of_the_query_string` (:669), `::test_archive_invalid_citekey_falls_back_to_safe_note_target` (:1178); every `archive-url` assertion in `tests/test_notes.py` and `tests/test_lints.py` (`grep -n 'archive-url' tests/test_notes.py tests/test_lints.py`)
- Test: `tests/test_verify_cli.py` (new regression at the end)

**Interfaces:**

- Consumes: nothing new.

- Produces: `inbox.CHECK_IDS` without `web-archive`; `inbox.REASON_CODES` without `missing-archive`; `lints._MACHINE_OWNED_FRONTMATTER_KEYS == frozenset({"managed-sha256", "fixity-sha256", "citekey"})` (Task 5 and Task 11 reshape it again).

- [ ] **Step 1: Write the failing regression test**

Append to `tests/test_verify_cli.py`:

```python
def test_archive_source_verb_and_web_archive_check_are_retired(tmp_vault):
    import research_vault.__main__ as cli
    from research_vault import inbox

    with pytest.raises(SystemExit) as exit_info:
        cli.main(["archive-source", "smith2020", "--vault", str(tmp_vault)])
    assert exit_info.value.code == 2
    assert "web-archive" not in inbox.CHECK_IDS
    assert "missing-archive" not in inbox.REASON_CODES
    assert not hasattr(cli, "cmd_archive_source")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_verify_cli.py -q -k retired`
Expected: FAIL — `main` dispatches `archive-source` and returns normally (no `SystemExit`).

- [ ] **Step 3: Delete the module and its consumers**

```bash
git rm -q research_vault/archive.py research_vault/archive.py.manifest.json tests/test_archive.py
# prune the baseline rows of archive.py and of every function this task deleted: run the baseline prune from Global Constraints
```

In `research_vault/__main__.py`: remove `archive,` from the `from . import (...)` block; delete `cmd_archive_source`; delete the four `archive_source_cmd` parser lines; delete `"archive-source": cmd_archive_source,` from the dispatch dict.

In `research_vault/verify.py`: delete `_archive_outcomes`; delete the two lines

```python
    if network:
        raw.extend(_archive_outcomes(vault))
```

and the line `raw.extend(lints.lint_web_archive(vault))`. If `webapi` is now unused in `verify.py` (`ruff check` reports F401), drop it from the import block.

In `research_vault/lints.py`: delete `lint_web_archive`; replace the `_MACHINE_OWNED_FRONTMATTER_KEYS` block with

```python
# Machine-owned fields that live outside %%rv-managed%%: `notes.render_note`
# owns citekey/managed-sha256/fixity-sha256. Legality rides on the `generated`
# writer attestation, not on slice membership.
_MACHINE_OWNED_FRONTMATTER_KEYS = frozenset(
    {"managed-sha256", "fixity-sha256", "citekey"}
)
```

In `research_vault/inbox.py`: remove `"missing-archive",` from `REASON_CODES` and `"web-archive",` from `CHECK_IDS`.

In `research_vault/frontmatter.py`, rewrite the `render_field` docstring's second paragraph to: ``` This is the one spelling of that grammar: ``serialize`` is its sole caller, so what it emits and what ``frontmatter.parse``/``notes._valid_generated`` expect back cannot drift apart. ```

In `skills/evidence-conventions/SKILL.md`, delete the `missing-archive` row of the `## Reason-code vocabulary` table. In `docs/terminology.md` §4.4, remove `web-archive` from the check-ids row and `missing-archive` from the reason-codes row.

- [ ] **Step 4: Delete the retired tests and run the suite**

Delete the five tests named above and every `archive-url` assertion. Run: `.venv/bin/python -m pytest tests -q -n auto`
Expected: PASS. Then `ruff format research_vault tests && ruff check research_vault tests && mypy research_vault` — clean.

- [ ] **Step 5: Commit**

```bash
git commit -m "retire the web-archive machinery (ingest spec §2, §6)

archive.py, archive-source, lint_web_archive, _archive_outcomes, the
web-archive check id and the missing-archive reason code go. The
archive-url field had a second writer into a record capture alone owns.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- research_vault tests skills/evidence-conventions/SKILL.md docs/terminology.md mutation-baseline.txt
```

### Task 2: Retire the Better BibTeX auto-export contract (spec §6, first bullet)

**Files:**

- Modify: `research_vault/bibliography.py` (keep :1-129 minus the autoexport types; delete :130-763; add `write`), `research_vault/__main__.py` (`cmd_staleness` :367-375, parser :839-840, dispatch, `DOCTOR_*` sets :45-47), `research_vault/verify.py` (`_staleness_outcome` :641-654, the `staleness` branches in `_plan_state` :965-996), `research_vault/scaffold.py` (`doctor` :322-406: the `observe_autoexport` block and the `autoexport`/`staleness` probes; the `bibliography` import), `research_vault/inbox.py` (`CHECK_IDS` drop `autoexport`; `REASON_CODES` drop `stale`), `skills/import-source/SKILL.md` (drop the two `autoexport` rows and the exit-`3` row of its two tables — `tests/test_skill_contracts.py:338-363` fails on a skill naming a check id the code no longer files), `skills/evidence-conventions/SKILL.md` (drop the `stale` row), `docs/terminology.md` §4.4, `docs/testing.md` (drop the `RV_LIVE_AUTOEXPORT_VAULT` sentence), `mutation-baseline.txt` (prune `research_vault/bibliography.py::` rows; the module survives but its surviving functions are re-baselined by the gate)
- Tests: rewrite `tests/test_bibliography.py` to the loader tests plus `write`; `tests/test_doctor.py` (`PROBE_NAMES`, `HARD_*`, `WARN_ONLY`, delete the `observe_autoexport` monkeypatches); delete `tests/test_cli_live.py::test_staleness_after_import_into_a_provisioned_vault` (:120), `::test_staleness_exit_codes` (:1314), `::test_staleness_cli_reports_corrupt_committed_bibliography_as_unmatched` (:1330) and the import-note tests whose subject is the auto-export (:626, :687, :725, :777, :837, :893, :945, :1448); `tests/test_verify_cli.py::test_staleness_reason_reflects_its_actual_result` (:759) deleted and `::test_target_hash_routes_safe_file_claim_citekey_and_staleness` (:232) loses its staleness leg; `grep -ln 'staleness\|autoexport\|observe_autoexport' tests/*.py` lists the rest — each remaining mock of `observe_autoexport` is deleted (the call it mocked no longer exists)

**Interfaces:**

- Produces: `bibliography.write(vault_root, items: list[dict]) -> Path` — validates through `_validate_items`, sorts by `id`, writes `json.dumps(items, indent=2, ensure_ascii=False) + "\n"` to `BIB_PATH`, creating `system/`; `scaffold.doctor(vault_root, client=None) -> list[Probe]` with six probes in order `tree, machine-config, zotero, bbt, remote, backup`; `__main__.DOCTOR_HARD_UNMATCHED = {"tree", "machine-config", "bbt"}`, `DOCTOR_HARD_UNREACHABLE = {"zotero", "bbt"}`, `DOCTOR_WARN_ONLY = {"remote", "backup"}`.

- [ ] **Step 1: Write the failing tests**

Replace `tests/test_bibliography.py` with:

```python
import json

import pytest

from research_vault import Result, bibliography

ITEMS = [
    {"id": "smith2020", "type": "article-journal", "title": "Mortality decline"},
    {"id": "gone2019", "type": "article-journal", "title": "Old result"},
]


def test_write_sorts_by_id_and_load_reads_it_back(tmp_vault):
    path = bibliography.write(tmp_vault, ITEMS)

    assert path == tmp_vault / "system" / "bibliography.json"
    raw = path.read_text()
    assert raw.endswith("\n")
    assert [item["id"] for item in json.loads(raw)] == ["gone2019", "smith2020"]
    assert bibliography.load(tmp_vault) == {item["id"]: item for item in ITEMS}


def test_write_refuses_items_without_string_ids(tmp_vault):
    with pytest.raises(bibliography.BibliographyError) as error:
        bibliography.write(tmp_vault, [{"type": "book"}])
    assert error.value.result is Result.UNMATCHED
    assert not (tmp_vault / "system" / "bibliography.json").exists()


def test_load_returns_empty_universe_when_file_is_absent(tmp_vault):
    assert bibliography.load(tmp_vault) == {}


def test_load_classifies_readable_invalid_bibliography_as_unmatched(tmp_vault):
    (tmp_vault / "system" / "bibliography.json").write_text("[{}]")
    with pytest.raises(bibliography.BibliographyError) as error:
        bibliography.load(tmp_vault)
    assert error.value.result is Result.UNMATCHED


def test_load_classifies_undecodable_bibliography_as_unreachable(tmp_vault):
    (tmp_vault / "system" / "bibliography.json").write_bytes(b"\xff\xfe")
    with pytest.raises(bibliography.BibliographyError) as error:
        bibliography.load(tmp_vault)
    assert error.value.result is Result.UNREACHABLE


def test_autoexport_surface_is_gone():
    for name in ("observe_autoexport", "staleness", "commit_autoexport"):
        assert not hasattr(bibliography, name)
```

(Keep the two existing `load` classification tests' bodies from `:847` and `:858` if they assert more than the versions above.)

In `tests/test_doctor.py` set

```python
PROBE_NAMES = ["tree", "machine-config", "zotero", "bbt", "remote", "backup"]
HARD_UNMATCHED = ["tree", "machine-config", "bbt"]
HARD_UNREACHABLE = ["zotero", "bbt"]
WARN_ONLY = ["remote", "backup"]
```

and delete every `observe_autoexport` monkeypatch and every assertion on `probes[4]`/`probes[5]` (the autoexport and staleness rows).

- [ ] **Step 2: Run them to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_bibliography.py tests/test_doctor.py -q`
Expected: FAIL — `bibliography.write` does not exist; doctor returns eight probes.

- [ ] **Step 3: Shrink `bibliography.py`, add `write`, unwire the callers**

`research_vault/bibliography.py` becomes:

```python
"""The CSL JSON file: one entry per captured item (ingest spec §3.2).

Capture regenerates it whole at the end of every run from one whole-library
Better BibTeX read; verify reads it as the citation-key universe. No
auto-export, no observation, no byte-compare against a third-party writer.
"""

import json
import os
import stat
from pathlib import Path

from . import Result

BIB_PATH = "system/bibliography.json"


class BibliographyError(ValueError):
    """A bibliography that cannot safely participate in verification."""

    def __init__(self, message: str, result: Result):
        super().__init__(message)
        self.result = result


def _path(vault_root) -> Path:
    # abspath, NOT Path.resolve(): resolve() follows symlinks.
    return Path(os.path.abspath(os.fspath(vault_root))) / BIB_PATH  # noqa: PTH100


def load(vault_root) -> dict[str, dict]:
    ...  # unchanged body from :73-98


def _validate_items(items) -> None:
    ...  # unchanged body from :101-127


def write(vault_root, items: list[dict]) -> Path:
    """Regenerate the whole file, sorted by citation key, or write nothing."""
    try:
        _validate_items(items)
    except (TypeError, ValueError) as error:
        raise BibliographyError(
            "refusing to write an invalid bibliography", Result.UNMATCHED
        ) from error
    ordered = sorted(items, key=lambda item: item["id"])
    target = _path(vault_root)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(ordered, indent=2, ensure_ascii=False) + "\n")
    return target
```

Delete everything else in the module (all `_Export*`, lock, git and observation code, `AutoexportObservation`, `staleness`, `commit_autoexport`, `observe_autoexport`). Prune the baseline rows of everything deleted here with the baseline prune from Global Constraints.

`research_vault/__main__.py`: delete `cmd_staleness`, its parser lines and dispatch entry; set

```python
DOCTOR_HARD_UNMATCHED = {"tree", "machine-config", "bbt"}
DOCTOR_HARD_UNREACHABLE = {"zotero", "bbt"}
DOCTOR_WARN_ONLY = {"remote", "backup"}
```

`research_vault/verify.py`: delete `_staleness_outcome` and the `ZoteroClient` import (nothing else in the module uses it until Task 12). In `_plan_state`, replace the `try/except/else` over `bibliography.load` with

```python
    try:
        bibliography_universe = bibliography.load(vault)
    except bibliography.BibliographyError as error:
        bibliography_universe = None
        reason = (
            "schema-violation — bibliography JSON/schema invalid"
            if error.result is Result.UNMATCHED
            else "outage — bibliography unreadable"
        )
        raw.append(
            checks.Outcome(
                "citekey",
                RepoPath(os.fsencode(bibliography.BIB_PATH)),
                error.result,
                reason,
            )
        )
```

(The invalid-file finding now rides the citation-key check, which is closing on the commit surface — an unreadable universe blocks a commit as it did before.)

`research_vault/scaffold.py`: remove `bibliography` from the import; `doctor` becomes

```python
def doctor(vault_root, client=None) -> list[Probe]:
    """Repair the scoped vault substrate and return its six ordered probes."""
    vault = Path(vault_root)
    try:
        scaffold_vault(vault)
        tree_complete = all((vault / relative).is_dir() for relative in VAULT_DIRS)
        tree = Probe(
            "tree",
            Result.MATCHED if tree_complete else Result.UNMATCHED,
            "required vault tree complete"
            if tree_complete
            else "required vault tree incomplete after repair",
        )
    except (OSError, subprocess.SubprocessError, ValueError) as error:
        tree = Probe("tree", Result.UNMATCHED, f"vault tree repair failed: {error}")

    config, machine = _machine_config(vault)
    probes = [tree, machine]
    client = ZoteroClient() if client is None else client
    try:
        versions = client.ready()
        if not isinstance(versions, dict):
            raise ZoteroError("malformed api.ready result: expected an object")
    except (ZoteroError, OSError, UnicodeError, ValueError) as error:
        probes.extend(
            [
                Probe("zotero", Result.UNREACHABLE, str(error)),
                Probe("bbt", Result.UNREACHABLE, "zotero down"),
            ]
        )
    else:
        version_detail = ", ".join(
            f"{name}={value}" for name, value in sorted(versions.items())
        )
        probes.append(Probe("zotero", Result.MATCHED, version_detail))
        bbt_version = versions.get("betterbibtex")
        if not isinstance(bbt_version, str) or not bbt_version.strip():
            probes.append(Probe("bbt", Result.UNMATCHED, "Better BibTeX version missing"))
        else:
            probes.append(Probe("bbt", Result.MATCHED, bbt_version.strip()))
    probes.extend([_remote_probe(vault), _backup_probe(config)])
    return probes
```

`research_vault/inbox.py`: drop `"autoexport",` from `CHECK_IDS` (and its comment) and `"stale",` from `REASON_CODES`. Edit the three skill/doc surfaces named in Files.

- [ ] **Step 4: Delete the retired tests, run the suite and the form owners**

Run: `.venv/bin/python -m pytest tests -q -n auto && ruff format research_vault tests && ruff check research_vault tests && mypy research_vault`
Expected: PASS, clean.

- [ ] **Step 5: Commit**

```bash
git commit -m "retire the Better BibTeX auto-export contract (ingest spec §6)

The CSL file is regenerated whole by capture from one 0.46 s read, so the
observe-and-wait machinery guarded something we can simply produce.
bibliography.py keeps load and gains write; staleness, the autoexport
doctor probe and the stale reason code go.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- research_vault tests skills docs mutation-baseline.txt
```

### Task 3: Retire verify's `doi` and `metadata` checks (spec §6, "retired on screening")

**Files:**

- Modify: `research_vault/checks.py` (delete `check_doi_exists` :186-237, `_metadata_text` :266, `_metadata_authors` :271, `_crossref_csl` :313, `_metadata_extra` :328, `check_metadata` :335-506; **keep** `registry_agency` :239-264, which the kept `check_update_notice` calls at :682, `metadata_year` :294, which `identify.py:4` imports and `:36` uses, and `_doi_path` if `check_update_notice` uses it — measured 2026-09-07 at Task 3's execution), `research_vault/verify.py` (`_network_outcomes` :657-702 and `_offline_network_outcomes` :704-722, `CLOSING_BY_SURFACE["publish"]` drops `doi`), `research_vault/events.py` (`_applicable_note_checks` :248-253), `research_vault/inbox.py` (`CHECK_IDS` drop `doi`, `metadata`), `skills/import-source/SKILL.md` §2 (its sentence naming the `doi`, `metadata`, and `update-notice` checks becomes "would make the `update-notice` check SKIPPED"), `docs/terminology.md` §4.4, `.github/workflows/quality.yml:48-65` (the `check_metadata` CRAP note is now moot — see Part B Task 4 for the removal of `continue-on-error`)
- Tests: delete every `test_doi_exists_*`, `test_doi_paths_*` and `test_metadata_*` in `tests/test_checks.py` (:340-:2367; keep `test_update_notice_*`, keep `test_registry_agency_*` because the function survives, and keep any `test_metadata_year_*` — `metadata_year` survives and `tests/test_identify.py:212` exercises it through `identify.discover`); in `tests/test_verify_cli.py` delete `::test_discovery_partial_identifiers_survive_outage_and_run_recovered_doi` (:58) and rewrite `::test_no_doi_distinguishes_healthy_no_hit_from_discovery_outage` (:99) and `::test_discovery_outage_with_only_pmid_keeps_live_update_unreachable` (:125) to assert on `update-notice` only; `tests/test_events.py` trust-tier tests that list `doi`/`metadata` as applicable checks (grep `applicable`) assert `{"update-notice"}`.

**Interfaces:**

- Produces: `verify._network_outcomes(vault_root, entry, detection_date, notice_lookup) -> list[Outcome]` returns only the reduced `update-notice` outcome; `verify._offline_network_outcomes` returns one synthetic-offline `update-notice` outcome (or the RW leg); `events._applicable_note_checks(data) -> set[str]` returns `{"update-notice"}` when the note carries a DOI (`data.get("DOI") or data.get("doi")`) or a PMID (`data.get("pmid")`, or a line starting `PMID:` in `data.get("extra")` when it is a string or a list of lines), else `set()`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_verify_cli.py`:

```python
def test_network_outcomes_carry_only_update_notice(net_vault, monkeypatch):
    from research_vault import checks, verify

    monkeypatch.setattr(
        checks,
        "check_update_notice",
        lambda vault, entry, date: checks.Outcome(
            "update-notice", entry["id"], Result.MATCHED, "matched"
        ),
    )
    entry = {"id": "smith2020", "DOI": "10.1000/xyz"}
    outcomes = verify._network_outcomes(net_vault, entry, "2026-09-07", None)
    assert [outcome.check for outcome in outcomes] == ["update-notice"]

    offline = verify._offline_network_outcomes(entry, "2026-09-07", None)
    assert [outcome.check for outcome in offline] == ["update-notice"]
    assert offline[0].extra["synthetic_offline"] is True
    assert "doi" not in verify.CLOSING_BY_SURFACE["publish"]
```

Append to `tests/test_events.py`:

```python
@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ({"DOI": "10.1000/xyz"}, {"update-notice"}),
        ({"doi": "10.1000/xyz"}, {"update-notice"}),
        ({"extra": ["PMID: 28503678", "PMCID: PMC5428074"]}, {"update-notice"}),
        ({"extra": "PMID: 28503678"}, {"update-notice"}),
        ({"title": "no identifiers"}, set()),
    ],
)
def test_applicable_note_checks_is_update_notice_or_nothing(data, expected):
    assert events._applicable_note_checks(data) == expected
```

- [ ] **Step 2: Run them to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_verify_cli.py tests/test_events.py -q -k "update_notice or applicable"`
Expected: FAIL — three checks are produced; `doi` still closes publish; `extra` is not read.

- [ ] **Step 3: Implement**

`research_vault/verify.py`:

```python
def _network_outcomes(vault_root, entry, detection_date, notice_lookup):
    """Produce one reduced update-notice outcome for a bibliography entry."""
    if entry.get("_discovery_unreachable") and not (
        entry.get("DOI") or entry.get("doi")
    ):
        live = checks.Outcome(
            "update-notice",
            entry["id"],
            Result.UNREACHABLE,
            "outage — identifier discovery unavailable",
        )
    else:
        live = checks.check_update_notice(vault_root, entry, detection_date)
    rw_leg = (
        checks.check_rw_batch(entry, notice_lookup, detection_date)
        if notice_lookup is not None
        else None
    )
    reduced = checks.reduce_update_notice_outcomes(live, rw_leg)
    return [reduced] if reduced is not None else []


def _offline_network_outcomes(entry, detection_date, notice_lookup):
    rw_leg = (
        checks.check_rw_batch(entry, notice_lookup, detection_date)
        if notice_lookup is not None
        else None
    )
    if rw_leg is not None:
        return [rw_leg]
    return [
        checks.Outcome(
            "update-notice",
            entry["id"],
            Result.UNREACHABLE,
            "outage — network disabled",
            {"synthetic_offline": True},
        )
    ]
```

and remove `"doi",` from `CLOSING_BY_SURFACE["publish"]`.

`research_vault/events.py`:

```python
def _extra_lines(value) -> list[str]:
    if isinstance(value, str):
        return value.splitlines()
    if isinstance(value, list):
        return [line for line in value if isinstance(line, str)]
    return []


def _applicable_note_checks(data: dict) -> set[str]:
    has_doi = bool(data.get("DOI") or data.get("doi"))
    has_pmid = bool(data.get("pmid")) or any(
        line.strip().upper().startswith("PMID:") for line in _extra_lines(data.get("extra"))
    )
    return {"update-notice"} if has_doi or has_pmid else set()
```

`research_vault/checks.py`: delete the functions listed in Files; `research_vault/inbox.py`: drop `"doi",` and `"metadata",` from `CHECK_IDS`. Edit the skill sentence and the terminology row.

- [ ] **Step 4: Delete the retired tests, run the suite and form owners**

Run: `.venv/bin/python -m pytest tests -q -n auto && ruff format research_vault tests && ruff check research_vault tests && mypy research_vault`
Expected: PASS, clean.

- [ ] **Step 5: Commit**

```bash
git commit -m "retire verify's doi and metadata checks (ingest spec §6)

Zotero plugins verify and clean DOIs and refresh metadata in the library;
capture's snapshot inherits the correction and carries tags, so the
verdict stays visible without the vault making the call itself.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- research_vault tests skills docs
```

### Task 4: Retire the note-level screening state (spec §0, §3.2 `status`, §6)

**Files:**

- Modify: `research_vault/lints.py` (delete `_note_status` :490-497 and `lint_screening_state` :500-526), `research_vault/verify.py` (`file_outcomes` :624-634 drops the `lint_screening_state` term), `research_vault/inbox.py` (`CHECK_IDS` drop `screening-state`; `REASON_CODES` drop `superseded-note`), `skills/evidence-conventions/SKILL.md` (drop the `superseded-note` row), `docs/terminology.md` §4.4, `tests/conftest.py` (`fixture_vault`: drop `status: "included"`, `status: "superseded"` and `superseded-by: "smith2020"` from the two literature notes — the frontmatter otherwise stays as it is until Task 5)
- Tests: delete `tests/test_lints.py::test_screening_state_deduplicates_repeated_references_and_records_origin` (:567), `::test_screening_state_catches_excluded_sources` (:590), `::test_screening_state_sorts_mixed_anchored_origins_without_crashing` (:606), `::test_screening_status_hand_edit_is_not_evidence_layer_drift` (:876); grep `tests/*.py` for `superseded-note` and `screening-state` and delete each assertion.

**Interfaces:**

- Produces: `verify.file_outcomes(vault_root, path, bibliography_universe=None) -> list[Outcome]` = `check_citekeys` (when a universe is given) + `check_all_quotes` + `lint_disputed_claim`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_lints.py`:

```python
def test_screening_state_is_retired(fixture_vault):
    from research_vault import inbox, lints, verify

    assert not hasattr(lints, "lint_screening_state")
    assert "screening-state" not in inbox.CHECK_IDS
    assert "superseded-note" not in inbox.REASON_CODES
    draft = fixture_vault / "projects" / "brief" / "draft.md"
    checks = {outcome.check for outcome in verify.file_outcomes(fixture_vault, draft)}
    assert "screening-state" not in checks
```

- [ ] **Step 2: Run it to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_lints.py -q -k screening_state_is_retired`
Expected: FAIL on the first assertion.

- [ ] **Step 3: Implement**

Delete the two lint functions; `file_outcomes` becomes

```python
def file_outcomes(vault_root, path, bibliography_universe=None):
    outcomes = quotes.check_all_quotes(vault_root, path) + lints.lint_disputed_claim(
        vault_root, path
    )
    if bibliography_universe is not None:
        outcomes = (
            checks.check_citekeys(vault_root, path, bibliography_universe) + outcomes
        )
    return outcomes
```

Drop the two registry entries, the skill row, the terminology entries, and the three `status`/`superseded-by` lines in `tests/conftest.py`.

- [ ] **Step 4: Delete the retired tests, run the suite and form owners**

Run: `.venv/bin/python -m pytest tests -q -n auto && ruff format research_vault tests && ruff check research_vault tests && mypy research_vault`
Expected: PASS, clean.

- [ ] **Step 5: Commit**

```bash
git commit -m "retire the note-level screening state (ingest spec §6)

Screening decisions belong to a review, not to the source; the
screening-state lint and the superseded-note reason code go with it.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- research_vault tests skills docs
```

### Task 5: Retire the managed region, claim lines as an ingest output, and `import-note` (spec §3.2, §6 "Retired here, on screening")

The literature note becomes wholly machine-written. `managed-sha256` narrows to a hash over the body below the frontmatter. The `%%rv-managed%%` markers, the free region, the claim-line renderer, the annotation-to-claim adapter, the selector backfill and the `import-note` verb all go; `capture` (Task 12) replaces the verb. The frozen quote check and trust tier keep working on whatever quote claims a note body carries — nothing writes them any more, but a Zotero child note rendered into the body can.

**Files:**

- Modify: `research_vault/notes.py` (delete `MANAGED_*`, `SEED_FREE`, `ManagedRegionError`, `RenderIntegrityError`, `_raw_lines`, `managed_slice_bytes`, `managed_sha256`, `_managed_body`, `_split_free`, `MANAGED_FIELDS`, `_prior_managed_body`, `_managed_projection`, `render_note`, `_assert_managed_body_parses`, `_norm`, `claim_id`, `_escape_selector`, `render_claim`, `_SELECTOR_CONTROL`; keep `display_text`, `InvalidCitekeyError`, `note_path`, `_valid_generated`, `generated_at_now`, `sha256_file`, `content_changed`, `canonical_content` and its helpers; add `note_body`, `body_sha256`, rewrite `validate_managed_witness`), `research_vault/claims.py` (drop the `MANAGED_OPEN`/`MANAGED_CLOSE` import, the `in_managed` field and the region tracking in `parse_claims`), `research_vault/quotes.py:41` and `research_vault/events.py:283` (drop the `claim.in_managed` conjunct), `research_vault/lints.py` (`_managed_bytes` → `_body_bytes`; the `lint_evidence_layer` reason strings; `_MACHINE_OWNED_FRONTMATTER_KEYS = frozenset({"managed-sha256", "fixity-sha256", "citekey"})` unchanged), `research_vault/__main__.py` (delete `QUOTE_ANNOTATION_TYPES`, `normalize_annotation`, `_attachment_annotations`, `_attachment_hash`, `_QUOTE_SELECTOR`, `_prior_contexts`, `_retain_prior_contexts`, `_selector_warning`, `cmd_import_note`, `cmd_backfill_selectors`, their parsers and dispatch entries, and the now-unused imports `selectors`, `paths`, `re`, `datetime`, `okf`, `stamp` as ruff reports them; keep `_hold` and `_hold_reason`; drop `notes.ManagedRegionError` and `notes.RenderIntegrityError` from the `except (...)` tuples in `cmd_verify` :393-405 and `_run_disposition` :508-520 — Python evaluates those tuples only when an exception reaches them, so a stale name there masks the real error as `AttributeError` at runtime and the suite may not notice), `hooks/pretooluse_guard.py:24-27` (`DENY_REASON` names `capture` in place of `import-note`) and `tests/test_hooks.py:26`, `research_vault/inbox.py` (`CHECK_IDS` drop `render` and `integrate` — both were `import-note`'s; keep `citekey`), `research_vault/templates/vault/AGENTS.md:25` (the markers sentence becomes: "Literature notes are wholly machine-written: `capture` regenerates the whole note from Zotero on every run, so per-source prose belongs in a Zotero child note, which capture renders."), `tests/conftest.py` (`_with_managed_witness` → `_with_body_witness`; the two literature notes lose their marker lines and the `## Notes` seed), `docs/terminology.md` (every `%%rv-managed%%` mention; §4.2's `managed-sha256` definition becomes "sha256 over the note body below the frontmatter"), `skills/import-source/SKILL.md` (delete the `## 4. Integrate at import` section, the `render`/`integrate` rows and the §7 table — the file is rewritten whole in Task 19; these deletions keep `tests/test_skill_contracts.py:123-154` and `:338-363` green now. That test requires at least one `python3 -m research_vault finding ...` invocation corpus-wide: move one to `skills/project-flow/SKILL.md` if none survives: `python3 -m research_vault finding disputed-claim CLAIM_LINK UNMATCHED "contradiction — ONE-LINE REASON" --vault PATH`), `skills/evidence-conventions/SKILL.md` (`contradiction` and `low-confidence` stay in `REASON_CODES`: `disputed-claim` and `factcheck` still file them)
- Delete: `research_vault/templates/vault/system/templates/literature.md`
- Tests to delete: in `tests/test_notes.py` every test except `test_note_path_rejects_unsafe_citekeys` (:160) and the `generated_at_now`/`_valid_generated`/`canonical_content`/`content_changed` tests (grep those names); `tests/test_cli_live.py` :100, :261, :302, :366, :394, :425, :453, :511, :579, :1077, :1130, :1166, :1213, :1257, :1387, :1405, :1422, :1486, :1511, :1550, :1567, :1604, :1637 (every `import_note`/`import_source`/`backfill` test) and the `provisioned_vault` fixture if nothing else uses it; `tests/test_render_neutralization.py` :310, :339 and every test whose subject is `render_note`/`render_claim`/selectors (keep the `display_text` tests); `tests/test_lints.py::test_claim_immutability_rejects_marker_change_when_a_selector_continuation_changes` (:359); `tests/test_verify_cli.py::test_managed_note_add_is_collected_and_projected_as_evidence_finding` (:1916) is rewritten as `test_literature_note_add_is_collected_and_projected_as_evidence_finding` over a marker-less note; `tests/test_templates.py:19,161-166` and `tests/test_scaffold.py:40,131,209` (the literature template); `tests/test_selectors.py` stays (the module stays, decision 20).
- Tests to rewrite: every fixture note in `tests/*.py` that carries `%%rv-managed%%` (`grep -ln 'rv-managed' tests/*.py`: conftest, test_checks, test_claims, test_events, test_factcheck, test_lints, test_notes, test_render_neutralization, test_skill_contracts, test_templates, test_trust_tier_cli, test_verify_cli, test_cli_live) drops the two marker lines and, where it carried one, the `## Notes` seed; witnesses are recomputed with `_with_body_witness`.

**Interfaces:**

- Produces: `notes.note_body(text: str) -> str`; `notes.body_sha256(text: str) -> str`; `notes.validate_managed_witness(note_bytes: bytes) -> tuple[Result, str]` (same four-state contract as today, hashing the body); `claims.Claim` without `in_managed`; `lints._body_bytes(image) -> bytes | None`; `tests/conftest._with_body_witness(text) -> str`.

- [ ] **Step 1: Write the failing tests**

Replace the managed-region tests in `tests/test_notes.py` with:

```python
def test_body_sha256_hashes_everything_below_the_frontmatter():
    text = '---\ntype: "literature"\n---\n# Title\n\nbody\n'
    assert notes.note_body(text) == "# Title\n\nbody\n"
    assert notes.body_sha256(text) == hashlib.sha256(b"# Title\n\nbody\n").hexdigest()


def test_body_witness_validation_is_four_state():
    body = "# Title\n"
    digest = hashlib.sha256(body.encode()).hexdigest()
    good = f'---\ntype: "literature"\nmanaged-sha256: "{digest}"\n---\n{body}'.encode()
    assert notes.validate_managed_witness(good) == (Result.MATCHED, "matched")

    stale = good.replace(body.encode(), b"# Edited\n")
    assert notes.validate_managed_witness(stale) == (
        Result.UNMATCHED,
        "schema-violation — stale managed-sha256",
    )
    missing = f'---\ntype: "literature"\n---\n{body}'.encode()
    assert notes.validate_managed_witness(missing) == (
        Result.UNMATCHED,
        "schema-violation — missing managed-sha256",
    )
    assert notes.validate_managed_witness(b"\xff\xfe") == (
        Result.UNREACHABLE,
        "outage — literature note is not UTF-8",
    )
    assert notes.validate_managed_witness(b"---\nunterminated\n") == (
        Result.UNMATCHED,
        "schema-violation — malformed frontmatter",
    )


def test_managed_region_surface_is_gone():
    for name in ("MANAGED_OPEN", "managed_slice_bytes", "render_note", "render_claim"):
        assert not hasattr(notes, name)
```

In `tests/conftest.py`:

```python
def _with_body_witness(text):
    from research_vault import notes

    digest = notes.body_sha256(text)
    return text.replace(
        'type: "literature"\n', f'type: "literature"\nmanaged-sha256: "{digest}"\n', 1
    )
```

and the `smith2020` fixture body becomes exactly

```
# Mortality decline

- (quote) [@smith2020, p. 12] ^c-11111111
  > Mortality fell 12% across all strata.
- (paraphrase) Retrospective design [@smith2020, p. 3] ^c-22222222
```

(`gone2019`'s body: `# Old result\n`).

Append to `tests/test_claims.py`:

```python
def test_claims_carry_no_managed_flag():
    from research_vault import claims

    (claim,) = claims.parse_claims("- (quote) [@smith2020, p. 1] ^c-1\n  > text\n")
    assert not hasattr(claim, "in_managed")
    assert claim.quote_text == "text"
```

- [ ] **Step 2: Run them to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_notes.py tests/test_claims.py -q`
Expected: FAIL — `note_body` undefined; markers still parsed.

- [ ] **Step 3: Implement the body witness and delete the region**

`research_vault/notes.py` — new helpers (the rest of the module is deletions):

```python
def note_body(text: str) -> str:
    """The body below the frontmatter: capture's, compared byte for byte."""
    _data, body = frontmatter.parse(text)
    return body


def body_sha256(text: str) -> str:
    return hashlib.sha256(note_body(text).encode("utf-8")).hexdigest()


def validate_managed_witness(note_bytes: bytes) -> tuple[Result, str]:
    """Return the four-state witness result without inventing I/O state."""
    try:
        text = note_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return Result.UNREACHABLE, "outage — literature note is not UTF-8"
    try:
        data, body = frontmatter.parse(text)
    except frontmatter.FrontmatterError:
        return Result.UNMATCHED, "schema-violation — malformed frontmatter"
    witnesses = [
        value
        for key, value in frontmatter._mapping_items(data)
        if key == "managed-sha256"
    ]
    if not witnesses:
        return Result.UNMATCHED, "schema-violation — missing managed-sha256"
    if len(witnesses) != 1:
        return Result.UNMATCHED, "schema-violation — duplicate managed-sha256"
    witness = witnesses[0]
    if not isinstance(witness, str) or re.fullmatch(r"[0-9a-f]{64}", witness) is None:
        return Result.UNMATCHED, "schema-violation — invalid managed-sha256"
    if witness != hashlib.sha256(body.encode("utf-8")).hexdigest():
        return Result.UNMATCHED, "schema-violation — stale managed-sha256"
    return Result.MATCHED, "matched"
```

`research_vault/claims.py` — `parse_claims` loses the region tracking:

```python
def parse_claims(text: str) -> list[Claim]:
    """Return claims found in any note body, retaining their source metadata."""
    parsed_claims: list[Claim] = []
    current_quote: Claim | None = None
    for line_no, line in enumerate(text.splitlines(), start=1):
        if current_quote is not None and line.startswith("  > "):
            addition = line[4:]
            current_quote.quote_text = (
                addition
                if current_quote.quote_text is None
                else f"{current_quote.quote_text} {addition}"
            )
            continue
        current_quote = None
        match = CLAIM_RE.match(line)
        if not match:
            continue
        ...  # the existing field/anchor/cite extraction, minus `in_managed=in_managed`
```

(Keep the existing extraction body verbatim apart from the dropped keyword.) Remove `in_managed: bool = False` from `Claim`.

`research_vault/quotes.py:41`: `if claim.tag == "quote" and claim.quote_text`. `research_vault/events.py:283`: `if claim.tag != "quote" or not claim.claim_id:` and rename `has_managed_quotes` → `has_quote_claims`.

`research_vault/lints.py`:

```python
def _body_bytes(image: gitstate.FileImage | None) -> bytes | None:
    """The note body below the frontmatter, or None when it cannot be read."""
    if image is None or image.kind != "file":
        return None
    try:
        text = (image.data or b"").decode("utf-8")
        return notes.note_body(text).encode("utf-8")
    except (UnicodeDecodeError, frontmatter.FrontmatterError):
        return None
```

Replace every `_managed_bytes(` call with `_body_bytes(`; the four reasons become `"drift — literature note renamed"`, `"drift — literature note added"`, `"drift — literature note deleted"`, `"drift — literature note body changed"`.

`research_vault/__main__.py`: delete the functions and parsers listed in Files. Delete the template file: `git rm -q research_vault/templates/vault/system/templates/literature.md`.

- [ ] **Step 4: Rewrite the fixtures, delete the retired tests, run everything**

Run: `.venv/bin/python -m pytest tests -q -n auto && ruff format research_vault tests hooks && ruff check research_vault tests hooks && mypy research_vault`
Expected: PASS, clean. Prune `mutation-baseline.txt` rows whose function no longer exists with the baseline prune from Global Constraints (a name-list `grep -v` would also drop rows of the new `render_note` Task 11 adds; the prune matches definitions, not substrings).

- [ ] **Step 5: Commit**

```bash
git commit -m "retire the managed region and import-note (ingest spec §3.2, §6)

The literature note is wholly machine-written and managed-sha256 hashes
the body below the frontmatter. Claim lines stop being an ingest output;
the frozen quote check reads whatever quote claims a body carries.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- research_vault tests hooks skills docs mutation-baseline.txt
```

### Task 6: Move the synthesis layer under `wiki/`; exempt `wiki/index.md`; exclude the tool's stores (spec §4.3 conflicts 1–3, §4.3.1, §6 "The synthesis layer moves")

**Files:**

- Modify: `research_vault/scaffold.py:14-22` (`VAULT_DIRS` drops `"synthesis"`), `research_vault/structure.py` (`_FOLDER_TYPES` drops `synthesis`; add `EXCLUDED_DIRS`; `check_reserved` skips excluded dirs and exempts `wiki/index.md`), `research_vault/stamp.py:42-48` (`_candidate_paths` skips `EXCLUDED_DIRS | {"fulltext"}`), `research_vault/verify.py` (`_plan_state` :997-1004: folders `("literatures", "wiki", "projects")`; the frontmatter walk skips `structure.EXCLUDED_DIRS`; `_mutate_marker` never writes under `wiki/`), `research_vault/lints.py:278` (`roots = (b"literatures/", b"projects/")`) and `:529-534` (`disputed_claim_links` walks `wiki/`), `research_vault/gitstate.py:644` (`(b"literatures/", b"projects/")`), `hooks/posttooluse_lint.py:13` (`CONCEPT_ROOTS = frozenset({"wiki", "projects"})`), `hooks/pretooluse_guard.py:11` (`MACHINE_SURFACE_DIR_NAMES = frozenset({"literatures", "log", "wiki"})` — decision 18), `research_vault/templates/vault/index.md`, `research_vault/templates/vault/AGENTS.md` (every `synthesis/` mention), `research_vault/templates/vault/system/bases/open-questions.base` (`'type == "concept"'`), `research_vault/templates/vault/gitignore` (add `.raw/` and `.vault-meta/`), `tests/conftest.py` (`fixture_vault`: the synthesis note moves to `wiki/concepts/mortality-trends.md` with `type: "concept"`; no `synthesis/index.md`; `tmp_vault` also creates `wiki/concepts`)
- Delete: `research_vault/templates/vault/synthesis/index.md`, `research_vault/templates/vault/system/templates/synthesis.md`
- Tests: `tests/test_structure.py` (:13, :46-50, :79, :97-102), `tests/test_templates.py` (:17, :20, :91, :128, :132, :160, :168, :182), `tests/test_scaffold.py` (:15, :35, :42, :101, :133, :137), `tests/test_hooks.py:212` (`wiki/concepts/...` path), `grep -ln 'synthesis' tests/*.py` for the rest — each `synthesis/` path becomes `wiki/concepts/` and each `type: "synthesis"` becomes `type: "concept"`.

**Interfaces:**

- Produces: `structure.EXCLUDED_DIRS = frozenset({".git", ".raw", ".vault-meta"})`; `structure.is_excluded(path: Path, vault: Path) -> bool`; `structure.expected_type("wiki/concepts/x.md") is None`; `structure.check_reserved` passes a frontmatter-bearing `wiki/index.md` and still fails a frontmatter-bearing `wiki/concepts/index.md`; `scaffold.VAULT_DIRS == ["inbox", "literatures", "log", "projects", "system/templates", "system/bases"]`.

- [ ] **Step 1: Write the failing tests**

In `tests/test_structure.py` replace the synthesis assertions with:

```python
def test_wiki_derives_no_type_and_synthesis_is_gone():
    assert structure.expected_type("wiki/concepts/topic.md") is None
    assert structure.expected_type("wiki/sources/A paper.md") is None
    assert "synthesis" not in structure._FOLDER_TYPES


def test_reserved_check_exempts_wiki_index_only(tmp_path):
    _write(tmp_path, "index.md", '---\nokf_version: "0.2"\n---\n# Root\n')
    _write(
        tmp_path,
        "wiki/index.md",
        "---\ntype: meta\ntitle: Wiki Index\nstatus: evergreen\n"
        "created: 2026-09-07\nupdated: 2026-09-07\ntags:\n  - meta\n---\n# Wiki Index\n",
    )
    (outcome,) = structure.check_reserved(tmp_path)
    assert outcome.result is Result.MATCHED

    _write(tmp_path, "wiki/concepts/index.md", '---\ntype: "index"\n---\n# S\n')
    problems = structure.check_reserved(tmp_path)
    assert problems[0].result is Result.UNMATCHED
    assert "wiki/concepts/index.md" in problems[0].target


def test_reserved_check_skips_the_tool_stores(tmp_path):
    _write(tmp_path, "index.md", '---\nokf_version: "0.2"\n---\n# Root\n')
    _write(tmp_path, ".raw/captured/index.md", '---\ntype: "x"\n---\n')
    _write(tmp_path, ".vault-meta/index.md", '---\ntype: "x"\n---\n')
    (outcome,) = structure.check_reserved(tmp_path)
    assert outcome.result is Result.MATCHED
```

(`tests/test_structure.py` imports `Result` from `research_vault`; add it if absent.) Append to `tests/test_hooks.py` a guard test:

```python
@pytest.mark.parametrize(
    "relative",
    [Path("wiki") / "concepts" / "new.md", Path("wiki") / "index.md", Path("wiki") / "sources" / "a.md"],
)
def test_pretooluse_denies_write_under_wiki(fixture_vault, relative):
    _make_hook_vault(fixture_vault)
    target = fixture_vault / relative
    payload = _pretooluse_payload(fixture_vault, "Write", file_path=str(target), content="x\n")

    result = _run_pretooluse(fixture_vault, payload)

    assert _pretooluse_deny(result) == MACHINE_SURFACE_DENY_REASON
```

and add `Path("wiki") / "concepts" / "new.md"` to the `relative` list of `test_pretooluse_denies_edit_into_every_machine_surface`; in `test_pretooluse_allows_edit_outside_machine_surfaces` replace `Path("synthesis") / "note.md"` with `Path("inbox") / "fleeting.md"` (the folder no longer exists).

- [ ] **Step 2: Run them to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_structure.py tests/test_hooks.py -q`
Expected: FAIL — `wiki/index.md` reported "nested index.md must be frontmatter-free"; `.raw/` index reported; wiki write allowed.

- [ ] **Step 3: Implement**

`research_vault/structure.py`:

```python
_FOLDER_TYPES = {
    "literatures": "literature",
    "log": "daily",
    "inbox": "fleeting",
}
# The compile tool's own stores (ingest spec §4.3): `.raw/` would hold a
# duplicate of `fulltext/` if its capture were ever run, and `.vault-meta/` is
# its runtime state. Both are gitignored and never walked.
EXCLUDED_DIRS = frozenset({".git", ".raw", ".vault-meta"})
# ADR 0001, second exemption (2026-09-07): the adopted compile tool writes
# `wiki/index.md` with frontmatter at a hard-coded path; OKF §8 forbids it on
# a nested index and the tool's own lint requires it. The vault carries the
# deviation; nothing the vault authors deviates.
_EXEMPT_INDEXES = frozenset({"wiki/index.md"})


def is_excluded(path: Path, vault: Path) -> bool:
    return any(part in EXCLUDED_DIRS for part in path.relative_to(vault).parts)
```

In `check_reserved`, the loop opens with `if is_excluded(path, vault): continue` (replacing the `.git` test) and the nested-index branch becomes:

```python
            elif relative in _EXEMPT_INDEXES:
                continue
            elif data:
                problems.append((relative, "nested index.md must be frontmatter-free"))
```

`research_vault/stamp.py`:

```python
_SKIP_DIRS = structure.EXCLUDED_DIRS | {"fulltext"}


def _candidate_paths(vault: Path, paths):
    if paths is not None:
        ...  # unchanged
        return
    for path in sorted(vault.rglob("*.md")):
        if any(part in _SKIP_DIRS for part in path.relative_to(vault).parts):
            continue
        yield path
```

(`stamp.py` imports `structure` already for `expected_type`.)

`research_vault/verify.py` `_plan_state`:

```python
    note_files = [
        path
        for folder in ("literatures", "wiki", "projects")
        for path in sorted((vault / folder).rglob("*.md"))
    ]
    for path in note_files:
        raw.extend(file_outcomes(vault, path, bibliography_universe))
    for path in sorted(vault.rglob("*.md")):
        if structure.is_excluded(path, vault):
            continue
        if path.name == "index.md" or path.name == "log.md":
            continue
        raw.extend(structure.check_note_frontmatter(vault, path))
```

and in `_mutate_marker`, after `path = _safe_relative(...)`:

```python
        if path is None or not path.is_file() or relative.startswith("wiki/"):
            # The compiled layer is the tool's write scope (ingest spec §4.4):
            # verify reads it and never writes into it.
            continue
```

(`relative` here is the encoded repo path string; check `_origins` returns it as `str` — if it is a `RepoPath`, test `relative.raw.startswith(b"wiki/")`.)

`research_vault/lints.py:278`: `roots = (b"literatures/", b"projects/")`; `disputed_claim_links` walks `(vault_root / "wiki").rglob("*.md")` when `wiki` exists. `research_vault/gitstate.py:644`: `(b"literatures/", b"projects/")`. Hooks as listed. Templates:

`research_vault/templates/vault/index.md`:

```markdown
---
okf_version: "0.2"
---
# Vault index

- [literatures/](literatures/) — evidence layer: literature notes, one per captured source, named by citation key
- [wiki/](wiki/) — compiled layer: per-source pages under `wiki/sources/`, cross-source pages under `wiki/concepts/`, written by the adopted compile tool
- [projects/](projects/) — manuscripts and deliverables
- [log/](log/) — daily activity log (summary: [[log]])
- [inbox/](inbox/) — fleeting notes and the review queue
- [system/](system/) — support artifacts: templates, bases, the CSL file, the applied propagation plans

Literature notes, for trust-tier review:

![[system/bases/trust-tier.base]]

Concept pages, flagged where they contain an open-question:

![[system/bases/open-questions.base]]
```

`research_vault/templates/vault/gitignore`:

```
.research-vault/
.obsidian/workspace*
.raw/
.vault-meta/
```

`research_vault/templates/vault/AGENTS.md`: replace "Read `synthesis/index.md` and recent `log/` entries before editing" with "Read `wiki/index.md` and recent `log/` entries before editing", and "`synthesis-conventions` for synthesis-note rules" with "`synthesis-conventions` for the rules of the compiled layer"; add after the machine-surfaces sentence: "`wiki/` is written only by the adopted compile tool's transaction engine; never `Write` or `Edit` under it." Update `tests/test_templates.py` and `tests/test_scaffold.py` expected strings to match exactly.

- [ ] **Step 4: Run the suite and form owners**

Run: `.venv/bin/python -m pytest tests -q -n auto && ruff format research_vault tests hooks && ruff check research_vault tests hooks && mypy research_vault`
Expected: PASS, clean.

- [ ] **Step 5: Commit**

```bash
git commit -m "move the synthesis layer under wiki/ and exempt wiki/index.md (ingest spec §4.3, §6)

Root synthesis/ leaves VAULT_DIRS and the folder-to-type map; wiki/ derives
no type, is never written by verify, and is a machine surface for the
guard. .raw/ and .vault-meta/ are gitignored and never walked.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- research_vault tests hooks
```

### Task 7: Rename `citekey` to `citationKey` (spec §1.1, task 0's rename half)

Zotero's native field is `citationKey` (spec §3.5.1); `citekey` is a Better BibTeX synonym for a field Better BibTeX no longer owns. The rename covers the frontmatter key, the check id, Python identifiers, the ten skill files and the docs. Measured 2026-09-07: 200 identifiers in `research_vault/*.py` before Phase 0; Tasks 1–5 removed roughly a third.

**Files:**

- Modify: every file `grep -rl 'citekey' research_vault tests hooks skills docs/terminology.md docs/testing.md README.md` lists (the spec's own `docs/superpowers/specs/` are not touched; the plan is not touched)
- Test: `tests/test_notes.py` (the migration), `tests/test_checks.py` (the renamed check)

**Interfaces:**

- Produces: frontmatter key `citationKey`; check id `citation-key`; reason `not-captured`; `notes.InvalidCitationKeyError`; `notes.note_path(vault_root, citation_key)`; `notes.rename_frontmatter_key(text, old, new) -> str`; `claims.Claim.citation_key`; `checks.check_citation_keys(vault_root, note_path, bibliography_universe=None)`; `verify._citation_key_hash`, `verify._note_for_citation_key`; `events.trust_tier` reads `citationKey`; `lints._origin` reads `citationKey`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_notes.py`:

```python
def test_rename_frontmatter_key_is_byte_surgical():
    text = '---\ncitekey: "smith2020"\ntype: "literature"\n---\n# T\ncitekey: in body\n'
    renamed = notes.rename_frontmatter_key(text, "citekey", "citationKey")
    assert renamed == '---\ncitationKey: "smith2020"\ntype: "literature"\n---\n# T\ncitekey: in body\n'
    assert notes.rename_frontmatter_key(renamed, "citekey", "citationKey") == renamed
    assert notes.rename_frontmatter_key("no frontmatter\n", "citekey", "citationKey") == "no frontmatter\n"


def test_invalid_citation_key_error_is_the_spelling():
    with pytest.raises(notes.InvalidCitationKeyError):
        notes.note_path("/tmp", "a/b")
```

Rename `test_note_path_rejects_unsafe_citekeys` to `test_note_path_rejects_unsafe_citation_keys`. In `tests/test_checks.py`, rename every `test_citekey_*`/`test_cited_citekey_*` to `citation_key` spellings and assert `outcome.check == "citation-key"` and `reason.startswith("not-captured")` where `not-imported` was asserted.

- [ ] **Step 2: Run them to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_notes.py tests/test_checks.py -q`
Expected: FAIL — `rename_frontmatter_key` and `InvalidCitationKeyError` undefined; check id still `citekey`.

- [ ] **Step 3: Implement the migration helper, then rename mechanically**

`research_vault/notes.py`:

```python
class InvalidCitationKeyError(ValueError):
    """A citation key that cannot safely name one file in ``literatures``."""


def rename_frontmatter_key(text: str, old: str, new: str) -> str:
    """Rename one top-level frontmatter key without touching anything else.

    The one migration §1.1 prices as carrying real risk: byte-surgical on the
    key's own line, inside the frontmatter block only, idempotent.
    """
    opening = frontmatter._FRONTMATTER_OPEN.match(text)
    if opening is None:
        return text
    closing = frontmatter._FRONTMATTER_CLOSE.search(text, opening.end())
    if closing is None:
        return text
    block = text[opening.end() : closing.start()]
    renamed = re.sub(
        rf"^{re.escape(old)}:(?=\s)", f"{new}:", block, count=1, flags=re.MULTILINE
    )
    return text[: opening.end()] + renamed + text[closing.start() :]
```

Then the mechanical pass, in this order, reviewing the diff after each:

```bash
# 1. Python identifiers and strings in the package, hooks and tests.
grep -rl 'InvalidCitekeyError' research_vault tests | xargs sed -i 's/InvalidCitekeyError/InvalidCitationKeyError/g'
grep -rl '_citekey_hash\|_note_for_citekey\|check_citekeys\|citekey_of' research_vault tests hooks | xargs sed -i \
  -e 's/_citekey_hash/_citation_key_hash/g' -e 's/_note_for_citekey/_note_for_citation_key/g' \
  -e 's/check_citekeys/check_citation_keys/g' -e 's/citekey_of/citation_key_of/g'
grep -rl '"citekey"' research_vault tests hooks | xargs sed -i -e 's/"citekey"/"citation-key"/g'
grep -rl "'citekey'" research_vault tests hooks | xargs sed -i -e "s/'citekey'/'citation-key'/g"
# 2. The frontmatter key: the check-id substitution above also hit
#    data.get("citekey") reads and fixture lines; repair those to the field spelling.
grep -rln 'get("citation-key")\|^citation-key: \|\\ncitation-key: ' research_vault tests hooks | xargs sed -i \
  -e 's/get("citation-key")/get("citationKey")/g' -e 's/^citation-key: /citationKey: /' -e 's/\\ncitation-key: /\\ncitationKey: /g'
# 3. Remaining bare identifiers.
grep -rl 'citekey' research_vault tests hooks | xargs sed -i -e 's/citekeys/citation_keys/g' -e 's/citekey/citation_key/g'
# 4. Reason code and its message.
grep -rl 'not-imported' research_vault tests skills docs | xargs sed -i 's/not-imported — cited citation_key has no literature note/not-captured — cited citation key has no literature note/; s/not-imported/not-captured/g'
```

Then read every hunk: a `citation_key` inside prose or an f-string message becomes `citation key`; a frontmatter fixture line `citation_key:` becomes `citationKey:`. The `CITE_RE` group name `key` and the `[@...]` syntax are untouched. In `research_vault/inbox.py` the registries now read `"citation-key"` and `"not-captured"`.

**Classification rule for pass 1.** `s/"citekey"/"citation-key"/g` rewrites every double-quoted literal, and only some of them are check ids; pass 2 repairs three shapes (`get(...)` reads, line-initial fixture keys, the `\n` escape inside a Python string) and no others. After pass 2, run `grep -rn '"citation-key"' research_vault tests hooks` and classify every hit:

- a **check id** keeps `citation-key`: an `Outcome(...)` first argument, a `_hold(...)` check argument, a member of `inbox.CHECK_IDS` or of verify's check-id sets, an `outcome.check == ...` comparison, an `_applicable_note_checks` return;
- a **frontmatter field name** becomes `citationKey`: a member of a frontmatter-keys set or tuple, a dict-literal key that is written out as frontmatter, an indexed read of parsed frontmatter;
- an **internal record field** that is neither (a key both produced and consumed inside the package, such as the annotation dict `__main__.py` builds and `notes.py` reads) keeps `citation-key` on both sides;
- an **external API field the package does not own** (a Better BibTeX JSON-RPC response key, like an RPC method name) keeps the spelling the API emits — `citekey` on an `item.search` hit — with a comment citing the research record that measured it.

Sites of the second kind at HEAD that pass 2 does not reach, with their line numbers at plan-writing time (Tasks 1–5 delete several; classify whatever survives): `research_vault/lints.py:625` the `_MACHINE_OWNED_FRONTMATTER_KEYS` member (Task 1 narrowed the set; Task 11 replaces it with `notes.CAPTURE_FIELDS`); `research_vault/notes.py:160` the `MANAGED_FIELDS` member and `:229` `fm = {"citekey": item["id"], "type": "literature"}`, which writes the note's actual frontmatter key, so a wrong spelling there changes what the CLI emits; `research_vault/__main__.py:74` the annotation dict key (third kind, paired with `notes.py:318`); `research_vault/__main__.py:196` `item.get("citekey")` on a Better BibTeX `item.search` hit — the fourth kind below, an external field: the wire key **is** `citekey` (research record 291 in `docs/research/2026-09-05-zotero-api-reading.md`, quoting `content/json-rpc.ts` L247-251 at v9.0.63), and `citationKey` is Zotero's item-schema field on the local API, not Better BibTeX's JSON-RPC key. Pass 2's `get("citationKey")` rewrite is wrong there; restore `citekey` with a comment citing the record. (Task 7 found that caller already deleted by Task 5 and the shape surviving only in `tests/test_zotero.py`'s fixture, corrected at `838a83a` after the brief's earlier wording sent it the wrong way.)`, which is Zotero's own field name and correct). Do not rely on the suite to find a wrong spelling at `notes.py:229\`; read the grep.

Skills and docs (prose, not code): in the ten skill files and `docs/terminology.md`, `docs/testing.md`, `README.md`: the frontmatter key `citekey` → `citationKey`; the check id `` `citekey` `` → `` `citation-key` ``; the word "citekey" in prose → "citation key"; the placeholder `CITEKEY` → `CITATION_KEY`; `[[citekey#^claim-id]]` → `[[citation-key#^claim-id]]`. `docs/terminology.md` §4.4: replace `citekey` with `citation-key` in the check-id row and `not-imported` with `not-captured` in the reason-code row; the deviation register's `citekey` row already reads "Superseded 2026-09-07 by the ingest redesign spec §3.1" — leave it.

Migration of existing notes (zero today, spec §0):

```bash
python3 - <<'PY'
from pathlib import Path
from research_vault import notes
for path in sorted(Path("literatures").glob("*.md")):
    text = path.read_text(encoding="utf-8", newline="")
    renamed = notes.rename_frontmatter_key(text, "citekey", "citationKey")
    if renamed != text:
        path.write_text(renamed, encoding="utf-8", newline="")
        print("migrated", path)
PY
```

is run once against the author's vault by Task 19's setup-vault skill instructions (it is a person's vault, not this repository).

- [ ] **Step 4: Run the suite and form owners**

Run: `.venv/bin/python -m pytest tests -q -n auto && ruff format research_vault tests hooks && ruff check research_vault tests hooks && mypy research_vault && grep -rn 'citekey' research_vault tests hooks skills docs/terminology.md docs/testing.md README.md CONTEXT.md | grep -v 'Better BibTeX synonym'`
Expected: PASS, clean, and the final grep prints nothing (CONTEXT.md is rewritten in Task 8; if it still matches, that is expected until then).

- [ ] **Step 5: Commit**

```bash
git commit -m "rename citekey to citationKey (ingest spec §1.1)

The schema spelling names the authoritative store: citationKey is Zotero's
own field since Zotero 8. The check id becomes citation-key and
not-imported becomes not-captured.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- research_vault tests hooks skills docs README.md
```

### Task 8: Rewrite the glossary (spec §1.1, §6 "The glossary is rewritten ... as a fresh derivation")

**Files:**

- Modify: `CONTEXT.md` (`research_vault/templates/context.md` is a symlink to it and needs no edit), `docs/terminology.md` (§4.1 vault paths, §4.2 field spellings, §4.3 governed skill names — leave `import-source` until Part B Task 4, §4.4 rows, and the naming-convention examples row at `:120`, whose `import-note`, `backfill-selectors` and `archive-source` are retired verbs — the examples become `stamp-type`, `trust-tier`, `mark-published`), `skills/evidence-conventions/SKILL.md` (`:37` "Claims in `synthesis/` add:" names the folder Task 6 moved — say the compiled layer under `wiki/`; `:82`, `:83` and `:102` still teach `import-note` and "the literature note's managed region", both retired by Task 5 — rewrite them in this task's terms: `capture`, and a note wholly machine-written from Zotero)
- Test: `tests/test_templates.py` (the glossary render test, if it asserts content), `tests/test_skill_contracts.py` (the backticked-token rule at `:157-170` over templates)

**Interfaces:**

- Produces: the vocabulary every later task, skill and finding message uses. The eight concepts of §1.1 plus the captured set, the record home, the three layers, the propagation plan and the acknowledgment scope.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_templates.py`:

```python
def test_glossary_carries_the_ingest_vocabulary_and_no_retired_terms():
    text = (REPO / "CONTEXT.md").read_text()
    for term in (
        "**Ingest**", "**Selection**", "**Add**", "**Capture**", "**Compile**",
        "**Drift**", "**Refresh**", "**Item key**", "**Citation key**",
        "**Captured set**", "**Provenance tuple**", "**Text layer**",
        "**Compiled layer**", "**Propagation plan**",
    ):
        assert term in text, term
    for retired in ("**Admission**", "**Managed region**", "**Screening state**",
                    "**Bibliography export**", "**Synthesis layer**"):
        assert retired not in text, retired
    assert text.count("citekey") == 1 and "_Avoid_: citekey" in text  # named once, as the spelling to avoid
```

(`REPO` is the repository root; `tests/test_skeleton.py` defines it as `Path(__file__).resolve().parents[1]` — reuse that spelling.)

- [ ] **Step 2: Run it to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_templates.py -q -k glossary`
Expected: FAIL — `**Ingest**` absent.

- [ ] **Step 3: Write `CONTEXT.md`**

Replace the file with (keep the two-line header):

```markdown
# research-vault

Trust-first academic research on a personal knowledge vault: every claim traceable to a real source, verified by mechanical checks.

## Language

### Vault

**Vault**: A private git repository of markdown notes — the researcher's durable knowledge store, built to outlive its tools (ADR 0001) as an OKF bundle.

**Type (OKF)**: A note's kind, derived from its folder — `literatures/` → literature, `log/` → daily, `inbox/` → fleeting, and only `projects/<name>/draft.md` → project. `wiki/` derives none: the compile tool writes its own `type` values (source, concept, entity, meta). `fulltext/` notes carry `type: fulltext` by construction. Notes under `system/` and at the vault root carry any non-empty type, freely chosen.

**Evidence layer**: The vault's machine-projected record of captured sources (`literatures/`); never free-written.

**Text layer**: The extracted full text of every indexed attachment, one file per attachment at `fulltext/<attachment key>.md`, gitignored and regenerable from Zotero. Obsidian indexes it; git never carries it. Its sha256 is machine-local: two machines indexing one PDF do not produce identical text.

**Compiled layer**: The adopted compile tool's pages under `wiki/`: one per-source page under `wiki/sources/` and cross-source pages under `wiki/concepts/`. Nothing under `wiki/` passes an evidence gate; it asserts arrangement, not evidence, and is written only by the tool's transaction engine.
_Avoid_: synthesis layer, synthesis note (the layer moved under `wiki/` and took the tool's page names)

**Literature note**: The vault's record of one captured source, `literatures/<citation key>.md`, wholly machine-written by capture: a metadata snapshot, a provenance tuple, and a body carrying only what frontmatter cannot — the attachment list and the item's Zotero child notes. Per-source prose belongs in a Zotero child note, which capture renders.

**Project**: A manuscript or deliverable in progress (`projects/<name>/`), with a publication lifecycle.

**Inbox**: Fleeting captures and the review queue (`inbox/`); never an admission path for citable sources.

**Log**: The append-only per-day activity record (`log/`), summarized in root `log.md`.

**System folder**: The vault's support artifacts (`system/`): templates, bases, the CSL file (`system/bibliography.json`) and the applied propagation plans (`system/propagations/`).

**Propagation plan**: The computed description of one re-key pass — the old→new mapping, the item key behind it, the note rename, every surface to rewrite with its hash as it stands — printed for a person to approve and applied only against its own sha256. The applied plan, kept under `system/propagations/` and never rewritten, is the record a reader follows an old key forward through and the residue check reads. There is no separate rename log.

### Ingest

**Ingest**: The whole process that gets a source from outside the vault into the vault: selection, add, capture, compile. The last of three garbage-in gates (setup, lint, ingest).

**Selection**: The human decision that a source is accepted, with the outcomes **included** and **excluded**, recorded where it is made — the review's selection log or an ad hoc request. Never on the source.

**Add**: Creating the library record in Zotero, by a person or by the agent on the person's instruction over the local API's documented write path. **Import** is reserved for Zotero parsing a bibliographic file (RIS, BibTeX, CSL JSON) into items; it never names the vault's own projection.

**Capture**: The deterministic copy of an item's metadata, attachments, child notes and extracted text into the vault, with provenance. The sole writer of the literature note, the text layer and the CSL file. Runs on demand; re-running it is a **refresh**.

**Compile**: The LLM step that turns a captured source into wiki pages — a **source page** and updated **concept pages** — performed by the adopted compile tool under its own human gate. The compile input is the text-layer file capture wrote.

**Drift**: The lifecycle linter's finding that an object the note depends on carries a version other than the recorded one — the item, an attachment or an annotation, each versioned independently. **Refresh** is the re-copy capture performs on demand.

**Item key**: A source's identity: the Zotero item key qualified by the Zotero server id. Assigned once, never reused, never user-editable.

**Citation key**: A source's name: Zotero's native `citationKey` field, filled by Better BibTeX. It names the file, the prose citation and the CSL entry. A change is a rename of a thing whose identity did not change, propagated mechanically.
_Avoid_: citekey (a Better BibTeX synonym for a field Better BibTeX no longer owns)

**Standing**: A source's state after it was added, in the lifecycle linter's words: current, drifted, re-keyed, **merged**, **trashed**, **deleted** (Zotero's words); **retracted**, **corrected** (Retraction Watch, Cochrane). A transition never deletes a note; it files a finding.

**Captured set**: The citation keys read from the `citationKey` field of every parseable note under `literatures/` that also carries `zotero-item-key`. Not the filenames: a note whose filename disagrees with its recorded key is a re-key awaiting propagation. The CSL file's scope, the compile wrapper's selection and the captured-set lint all read this set.

**Provenance tuple**: The frontmatter fields that record what a literature note depends on: `zotero-server-id`, `zotero-item-key`, `zotero-item-version`, `citationKey`, `attachments` (key, version, md5, content type, filename), `fulltext` (attachment key, sha256), `compile-input-sha256`, `generated`. Versions and keys are meaningful only within one server id.

**Snapshot**: The fixed subset of the Zotero item's data fields a literature note carries verbatim under Zotero's own field names, `tags` and `extra` included. A value with line breaks is carried as a list of its lines.

### Evidence and claims

**Source**: The document itself, existing in the world before and independent of any library record — never the journal, repository, or outlet.
_Avoid_: "source" for an outlet — that is a **venue**, which is what OpenAlex's "source" means and ours never does

**Item**: A source's library record (CSL/Zotero vocabulary) — the object that carries the item key and the citation key.

**Venue**: The journal, repository, or outlet an item appeared in.

**Citable**: What a page or draft is allowed to cite: a source in the captured set. Being in the library is not yet being citable here; the captured-set lint enforces it on the commit surface.

**Claim**: One assertion carried by a note line, tagged with its evidence boundary and anchored for linking. Capture no longer writes claim lines; the checks that read them are frozen pending the workflow-component audit.

**Evidence-boundary tag**: The per-claim marker of epistemic status — quote, paraphrase, inference, or open-question.

**Claim link**: The global address of a claim: `citation-key#^claim-id` (an Obsidian block link).

**Stance link**: A typed claim-to-claim relation — `supports` or `disputes` (CiTO senses). Frozen pending the workflow-component audit.

**Authority**: Two unrelated things share the word. The compile tool's source ledger carries an `authority` enum (official, primary, secondary, community, synthetic, unknown), set by the compile wrapper. The vault's former `authority` frontmatter field had no writer and is retired.

### Verification

**Check**: One named verification a note or claim is put through; most are mechanical, some are LLM judgment.

**Four-state result**: A check's outcome: MATCHED, UNMATCHED, UNREACHABLE (could not run — never guilt), or SKIPPED (does not apply).

**Verified event**: The dated, attributed record that a named check passed on a note; only MATCHED mints one.

**Closing check**: A check whose standing can hold a surface; closing is a property of the surface, not of the check.

**Trust tier**: A note's derived standing: unverified → machine-confirmed → human-reviewed (cumulative).

**Lifecycle linter**: The one check that classifies every literature note against live Zotero from three reads (the versions map, the trash map, the top-level items), at capture and at verify through one code path. Its pre-commit leg is held.

**Review queue**: The append-only findings file (`inbox/review-queue.md`) every warn, hold, and alert writes to.

**Acknowledgment**: A human's standing acceptance of a finding, identified by the derived scope `sha256(check \0 target \0 target content hash)`; for a note-targeted finding the content hash is the note's `managed-sha256`. If the target's body changes, the scope no longer matches and the finding re-fires. An ack lets a check stand down; it never erases the finding.

**Publish gate**: The fail-closed verification boundary every publication crosses.

**Update notice**: A registry's post-publication signal about an item, such as a retraction or correction, recorded with its publication date and the date it was detected.
```

`docs/terminology.md`: §4.1 adds `fulltext/` and `wiki/` and drops `synthesis/`; §4.2 lists `citationKey`, `zotero-server-id`, `zotero-item-key`, `zotero-item-version`, `compile-input-sha256`, `managed-sha256` ("sha256 over the note body below the frontmatter") and drops `fixity-sha256`, `archive-url`, `status`; §4.4 rows reflect the registries as they stand after Task 7.

- [ ] **Step 4: Run the suite, mdformat, commit**

Run: `.venv/bin/python -m pytest tests -q -n auto && mdformat --number --wrap keep CONTEXT.md docs/terminology.md`
Expected: PASS.

```bash
git commit -m "rewrite the glossary around ingest (ingest spec §1.1)

Eight concepts traced to their fields; the captured set defined; the
import and authority collisions named; the false literature-note and
managed-region definitions rewritten rather than repointed.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- CONTEXT.md docs/terminology.md tests/test_templates.py skills/evidence-conventions/SKILL.md
```

______________________________________________________________________

## Phase 1 — capture, the text layer, the lifecycle linter, propagation, the seam lint

### Task 9: Rewrite the Zotero client for the local API (spec §2, §3.3, §3.4, §3.7, §5)

**Files:**

- Modify: `research_vault/zotero.py` (rewrite whole), `research_vault/verify.py:40` (`DEFAULT_BASE` becomes `from .zotero import DEFAULT_BASE`), `research_vault/__main__.py` (`--base` resolution through `zotero.base_for`; `cmd_probe` prints `server_info()` and `ready()`), `research_vault/paths.py` (nothing — `load_machine_config` is reused), `research_vault/templates/research-vault/machine.json.example` (add `"zotero_base": "http://localhost:23119"` and `"zotero_profile": ""` keys; keep canonical JSON form), `tests/test_config_validity.py` (no change: the example is already listed)
- Create: `tests/fakes.py`
- Test: `tests/test_zotero.py` (rewrite whole), `tests/test_cli_live.py` (the `probe` legs assert `server_info()`/`ready()` output; delete `_provisioned_vault_or_defer`, its two self-tests, `PROVISIONED_VAULT_ENV = "RV_LIVE_AUTOEXPORT_VAULT"` and `DEFERRAL_REASON` — the Better BibTeX auto-export drill Task 2 retired, whose last consumer Task 5 deleted)

**Interfaces:**

- Produces: see the Interface index, `research_vault/zotero.py` and `tests/fakes.py` blocks. `verify.DEFAULT_BASE` keeps working as a re-export.

- [ ] **Step 1: Write the fake and the failing tests**

`tests/fakes.py`:

```python
"""The shared Zotero double: canned local-API and JSON-RPC responses.

Every offline test that needs Zotero installs one of these on a client. It
answers by exact path (query string included) so a test asserts the wire
shape spec §3.7 records, and it logs every call in order.
"""

import json
from urllib.parse import urlsplit

from research_vault import zotero


class FakeZotero:
    def __init__(self, server_id="6LpvURP2E933", library_name="My Library"):
        self.server_id = server_id
        self.library_name = library_name
        self.calls: list[tuple[str, str, dict]] = []
        self._gets: dict[str, tuple[int, bytes, dict]] = {}
        self._posts: dict[str, tuple[int, bytes, dict]] = {}
        self._rpc: dict[str, object] = {}
        self.get("/api/", body=b"", headers={
            "X-Zotero-Version": "10.0.1",
            "Zotero-API-Version": "3",
            "Zotero-Schema-Version": "44",
        })

    def get(self, path, status=200, body=None, headers=None, method="GET"):
        payload = body if isinstance(body, bytes) else json.dumps(body).encode()
        table = self._posts if method == "POST" else self._gets
        table[path] = (status, payload, dict(headers or {}))

    def post(self, path, status=200, body=None, headers=None):
        self.get(path, status, body, headers, method="POST")

    def rpc(self, method, result):
        self._rpc[method] = result

    def _http(self, url, data=None, headers=None, method=None):
        parts = urlsplit(url)
        path = parts.path + (f"?{parts.query}" if parts.query else "")
        verb = method or ("POST" if data is not None else "GET")
        self.calls.append((verb, path, dict(headers or {})))
        sent_id = (headers or {}).get("Zotero-Server-ID")
        if path.startswith("/api/") and sent_id and sent_id != self.server_id:
            return zotero.Response(412, b"does not match this server", {})
        if verb == "POST" and path.startswith("/api/") and not sent_id:
            return zotero.Response(428, b"Precondition Required", {})  # measured server answer; authorize() raises before sending
        table = self._posts if verb == "POST" else self._gets
        if path not in table:
            return zotero.Response(404, b"", {"Zotero-Server-ID": self.server_id})
        status, payload, extra = table[path]
        return zotero.Response(
            status, payload, {"Zotero-Server-ID": self.server_id, **extra}
        )

    def _rpc_call(self, method, params):
        self.calls.append(("RPC", method, {"params": params}))
        if method not in self._rpc:
            raise zotero.ZoteroError(f"JSON-RPC error: unknown method {method}")
        return self._rpc[method]

    def install(self, client, monkeypatch):
        monkeypatch.setattr(client, "_http", self._http)
        monkeypatch.setattr(client, "_rpc", self._rpc_call)
        return client


ITEM = {
    "key": "E352DFS8",
    "version": 544,
    "library": {"type": "user", "id": 16413661, "name": "My Library"},
    "meta": {"numChildren": 1},
    "data": {
        "key": "E352DFS8",
        "version": 544,
        "itemType": "journalArticle",
        "title": "Co-writing with opinionated language models affects users' views",
        "creators": [
            {"creatorType": "author", "firstName": "Maurice", "lastName": "Jakesch"}
        ],
        "date": "2023",
        "DOI": "10.1145/3544548.3581196",
        "url": "https://doi.org/10.1145/3544548.3581196",
        "publicationTitle": "CHI 2023",
        "language": "en",
        "abstractNote": "Line one.\n\tLine  two.",
        "extra": "PMID: 28503678\nPMCID: PMC5428074",
        "accessDate": "2026-06-06T10:00:00Z",
        "tags": [{"tag": "ai", "type": 1}],
        "citationKey": "jakesch.etal2023a",
        "relations": {},
        "dateModified": "2026-06-06T10:00:00Z",
    },
}

ATTACHMENT = {
    "key": "D7EJ9FTG",
    "version": 551,
    "data": {
        "key": "D7EJ9FTG",
        "version": 551,
        "itemType": "attachment",
        "linkMode": "imported_file",
        "contentType": "application/pdf",
        "filename": "Jakesch et al. - 2023.pdf",
        "md5": "aa59569ae4f4b3a7c546158d4771c738",
        "mtime": 1788285164904,
        "parentItem": "E352DFS8",
    },
}

CHILD_NOTE = {
    "key": "N0TE0001",
    "version": 552,
    "data": {
        "key": "N0TE0001",
        "version": 552,
        "itemType": "note",
        "note": "<p>Read for the <b>method</b>.</p><p>Second paragraph.</p>",
        "parentItem": "E352DFS8",
    },
}

FULLTEXT = {"content": "Page one text " * 60 + "\fPage two text " * 60, "indexedPages": 2, "totalPages": 2}


def canned_item(fake, item=ITEM, children=(ATTACHMENT, CHILD_NOTE), fulltext=FULLTEXT):
    """Register one whole item the way capture reads it."""
    key = item["key"]
    fake.get(f"/api/users/0/items/{key}?format=json", body=item)
    fake.get(f"/api/users/0/items/{key}/children", body=list(children))
    fake.get(f"/api/users/0/items/{key}/children?itemType=annotation", body=[])
    for child in children:
        if child["data"]["itemType"] == "attachment":
            att = child["key"]
            if fulltext is None:
                fake.get(f"/api/users/0/items/{att}/fulltext", status=404, body=b"")
            else:
                fake.get(f"/api/users/0/items/{att}/fulltext", body=fulltext)
            fake.get(
                f"/api/users/0/items/{att}/file/view/url",
                body=b"file:///D:/Zotero/storage/D7EJ9FTG/Jakesch%20et%20al.%20-%202023.pdf",
            )
    return fake
```

`tests/test_zotero.py` (whole):

```python
import pytest

from research_vault import Result, zotero
from tests.fakes import ATTACHMENT, CHILD_NOTE, FULLTEXT, ITEM, FakeZotero, canned_item


@pytest.fixture
def fake(monkeypatch):
    client = zotero.ZoteroClient()
    double = FakeZotero()
    double.install(client, monkeypatch)
    double.client = client
    return double


def test_base_for_prefers_flag_then_machine_config_then_default(tmp_vault):
    assert zotero.base_for(tmp_vault) == zotero.DEFAULT_BASE
    (tmp_vault / ".research-vault").mkdir()
    (tmp_vault / ".research-vault" / "machine.json").write_text(
        '{"zotero_base": "http://localhost:23129/"}'
    )
    assert zotero.base_for(tmp_vault) == "http://localhost:23129"
    assert zotero.base_for(tmp_vault, "http://other:1/") == "http://other:1"


def test_server_info_reads_the_four_headers(fake):
    assert fake.client.server_info() == {
        "zotero": "10.0.1",
        "api": "3",
        "schema": "44",
        "server_id": "6LpvURP2E933",
    }


def test_recorded_server_id_rides_every_request_and_412_is_typed(fake, monkeypatch):
    canned_item(fake)
    fake.client.server_id = "6LpvURP2E933"
    assert fake.client.item("E352DFS8")["data"]["citationKey"] == "jakesch.etal2023a"
    assert fake.calls[-1][2]["Zotero-Server-ID"] == "6LpvURP2E933"

    fake.client.server_id = "Tdoqsn2J4q4h"
    with pytest.raises(zotero.DatabaseChangedError) as error:
        fake.client.item("E352DFS8")
    assert error.value.result is Result.UNMATCHED


def test_item_children_fulltext_and_file_url(fake):
    canned_item(fake)
    children = fake.client.children("E352DFS8")
    assert [child["data"]["itemType"] for child in children] == ["attachment", "note"]
    assert fake.client.annotations("E352DFS8") == []
    assert fake.client.fulltext("D7EJ9FTG") == FULLTEXT
    assert fake.client.fulltext("MISSING1") is None
    assert fake.client.file_view_url("D7EJ9FTG").startswith("file:///D:/Zotero/storage/")


def test_versions_trash_and_top_carry_the_version_header(fake):
    fake.get(
        "/api/users/0/items?since=0&format=versions",
        body={"E352DFS8": 544, "D7EJ9FTG": 551},
        headers={"Last-Modified-Version": "565"},
    )
    fake.get("/api/users/0/items/trash?format=versions", body={"T6GF6HH7": 15})
    fake.get(
        "/api/users/0/items/top?format=json",
        body=[ITEM],
        headers={"Last-Modified-Version": "565"},
    )
    assert fake.client.versions() == ({"E352DFS8": 544, "D7EJ9FTG": 551}, 565)
    assert fake.client.trash_versions() == {"T6GF6HH7": 15}
    items, version = fake.client.top_items()
    assert items[0]["key"] == "E352DFS8" and version == 565


def test_library_csl_reads_the_whole_library_route(fake):
    fake.get(
        "/better-bibtex/library?/My%20Library.json",
        body=[{"id": "jakesch.etal2023a", "citation-key": "jakesch.etal2023a", "type": "paper-conference"}],
    )
    items = fake.client.library_csl("My Library")
    assert items[0]["id"] == "jakesch.etal2023a"


def test_local_api_403_and_404_are_typed_and_other_statuses_are_outages(fake):
    fake.get("/api/users/0/items/OFF00000?format=json", status=403, body=b"")
    with pytest.raises(zotero.LocalApiDisabledError):
        fake.client.item("OFF00000")
    with pytest.raises(zotero.NotFoundError):
        fake.client.item("NOPE0000")
    fake.get("/api/users/0/items/BROKEN00?format=json", status=500, body=b"")
    with pytest.raises(zotero.ZoteroError) as error:
        fake.client.item("BROKEN00")
    assert error.value.result is Result.UNREACHABLE


def test_authorize_requires_a_server_id_and_returns_the_key(fake):
    fake.post("/api/local/authorize", body={"key": "k" * 32, "remember": True})
    with pytest.raises(zotero.ZoteroError):
        fake.client.authorize()  # no server id -> authorize() raises before any request
    fake.client.server_id = "6LpvURP2E933"
    assert fake.client.authorize() == {"key": "k" * 32, "remember": True}
    verb, path, headers = fake.calls[-1]
    assert (verb, path) == ("POST", "/api/local/authorize")


def test_create_items_sends_key_and_id_and_returns_the_envelope(fake):
    fake.client.server_id = "6LpvURP2E933"
    fake.client.api_key = "k" * 32
    fake.post(
        "/api/users/0/items",
        body={"successful": {"0": {"key": "II7E6CVR", "version": 1710}}, "unchanged": {}, "failed": {}},
    )
    envelope = fake.client.create_items([{"itemType": "journalArticle", "title": "T"}])
    assert envelope["successful"]["0"]["key"] == "II7E6CVR"
    assert fake.calls[-1][2]["Zotero-API-Key"] == "k" * 32


def test_rpc_fallbacks_survive(fake):
    fake.rpc("api.ready", {"zotero": "10.0.1", "betterbibtex": "9.0.63"})
    fake.rpc("item.export", [{"id": "jakesch.etal2023a", "type": "paper-conference"}])
    fake.rpc("item.attachments", [])
    assert fake.client.ready()["betterbibtex"] == "9.0.63"
    assert fake.client.export_csl(["jakesch.etal2023a"])[0]["id"] == "jakesch.etal2023a"
    assert fake.client.attachments("jakesch.etal2023a") == []


def test_item_key_grammar():
    assert zotero.ITEM_KEY.match("E352DFS8")
    assert not zotero.ITEM_KEY.match("jakesch.etal2023a")


@pytest.mark.live
def test_live_server_info_and_ready():
    client = zotero.ZoteroClient()
    info = client.server_info()
    assert info["zotero"].startswith("10.") and len(info["server_id"]) == 12
    assert "betterbibtex" in client.ready()
```

(The old `test_zotero.py` `FakeTransport` tests for `search`/`citation_key_of`/`_normalize_top_level_csl_ids` go: those methods are deleted. Keep its JSON-RPC malformed-shape tests by porting them onto `fake.rpc(...)`.)

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_zotero.py -q`
Expected: FAIL — `zotero.Response`, `base_for`, `server_info` undefined.

- [ ] **Step 3: Rewrite `research_vault/zotero.py`**

```python
"""Clients for the Zotero local API and Better BibTeX JSON-RPC (ingest spec §3.7).

Reads go to the local API. The server id a note recorded rides every request
as ``Zotero-Server-ID``; Zotero answers 412 when a different database is
listening, and that is the only database-changed test this package makes.
Writes take the documented local write path (§2): ``authorize`` once, then an
API key on each write. Better BibTeX JSON-RPC is kept for ``api.ready``, the
annotation fallback ``item.attachments`` and the CSL fallback ``item.export``.
"""

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from pathlib import Path
from typing import NamedTuple

from . import Result, paths

DEFAULT_BASE = "http://localhost:23119"
CSL_TRANSLATOR = "Better CSL JSON"
APP_NAME = "research-vault"
ITEM_KEY = re.compile(r"^[A-Z0-9]{8}$")
_USER = "/api/users/0"


class ZoteroError(Exception):
    """A Zotero operation failure with a research-vault outcome classification."""

    def __init__(self, message, result=Result.UNREACHABLE):
        super().__init__(message)
        self.result: Result = result


class DatabaseChangedError(ZoteroError):
    """412: the instance answering is not the one the tuple recorded (§3.4)."""

    def __init__(self, message="Zotero-Server-ID does not match this server"):
        super().__init__(message, Result.UNMATCHED)


class LocalApiDisabledError(ZoteroError):
    """403: Zotero runs but its local API preference is off (§5)."""

    def __init__(self, message="local API preference is disabled"):
        super().__init__(message, Result.UNMATCHED)


class NotFoundError(ZoteroError):
    """404 from the local API."""

    def __init__(self, message):
        super().__init__(message, Result.UNMATCHED)


class Response(NamedTuple):
    status: int
    body: bytes
    headers: Mapping[str, str]


def base_for(vault_root, override: str | None = None) -> str:
    """--base, then machine.json's zotero_base, then the default (§6)."""
    if override:
        return override.rstrip("/")
    config = paths.load_machine_config(Path(vault_root)) if vault_root else {}
    base = config.get("zotero_base")
    if isinstance(base, str) and base.strip():
        return base.strip().rstrip("/")
    return DEFAULT_BASE


class ZoteroClient:
    """Access local Zotero through its local web API and BBT JSON-RPC."""

    def __init__(
        self,
        base: str = DEFAULT_BASE,
        timeout: float = 5.0,
        server_id: str | None = None,
        api_key: str | None = None,
    ):
        self.base = base.rstrip("/")
        self.timeout = timeout
        self.server_id = server_id
        self.api_key = api_key

    # -- transport -----------------------------------------------------------

    def _headers(self, extra=None) -> dict[str, str]:
        headers = dict(extra or {})
        if self.server_id:
            headers["Zotero-Server-ID"] = self.server_id
        if self.api_key:
            headers["Zotero-API-Key"] = self.api_key
        return headers

    def _http(self, url, data=None, headers=None, method=None) -> Response:
        request = urllib.request.Request(
            url, data=data, headers=headers or {}, method=method
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return Response(response.status, response.read(), dict(response.headers))
        except urllib.error.HTTPError as error:
            return Response(error.code, error.read(), dict(error.headers))
        except OSError as error:
            raise ZoteroError(f"Zotero unreachable at {self.base}: {error}") from error

    def _local(self, path, *, data=None, method=None, expect=(200,)) -> Response:
        response = self._http(
            f"{self.base}{path}", data=data, headers=self._headers(
                {"Content-Type": "application/json"} if data is not None else None
            ), method=method,
        )
        if response.status in expect:
            return response
        if response.status == 412:
            raise DatabaseChangedError()
        if response.status == 403:
            raise LocalApiDisabledError()
        if response.status == 404:
            raise NotFoundError(f"local API 404 for {path}")
        raise ZoteroError(f"local API HTTP {response.status} for {path}")

    def _local_json(self, path):
        response = self._local(path)
        return self._decode_json(response.body, f"local API {path}"), response.headers

    @staticmethod
    def _decode_json(payload, context):
        try:
            return json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as error:
            raise ZoteroError(f"malformed {context}: {error}") from error

    @staticmethod
    def _validate_object_list(items, context):
        if not isinstance(items, list):
            raise ZoteroError(f"malformed {context}: expected a list")
        for index, item in enumerate(items):
            if not isinstance(item, Mapping):
                raise ZoteroError(f"malformed {context}: invalid object at index {index}")
        return items

    @classmethod
    def _validate_csl_items(cls, items, context):
        cls._validate_object_list(items, context)
        for index, item in enumerate(items):
            if not isinstance(item.get("id"), str) or not item["id"]:
                raise ZoteroError(f"malformed {context}: invalid item at index {index}")
        return items

    @staticmethod
    def _version_header(headers) -> int | None:
        raw = headers.get("Last-Modified-Version")
        return int(raw) if isinstance(raw, str) and raw.isdigit() else None

    # -- local API reads (§3.3, §3.4) -----------------------------------------

    def server_info(self) -> dict:
        """One GET /api/: four facts from one response's headers (§5)."""
        response = self._local("/api/")
        headers = response.headers
        info = {
            "zotero": headers.get("X-Zotero-Version", ""),
            "api": headers.get("Zotero-API-Version", ""),
            "schema": headers.get("Zotero-Schema-Version", ""),
            "server_id": headers.get("Zotero-Server-ID", ""),
        }
        if not info["server_id"]:
            raise ZoteroError("malformed /api/ response: no Zotero-Server-ID header")
        return info

    def item(self, key) -> dict:
        payload, _ = self._local_json(f"{_USER}/items/{key}?format=json")
        if not isinstance(payload, Mapping) or not isinstance(payload.get("data"), Mapping):
            raise ZoteroError("malformed item JSON: expected an envelope with data")
        return payload

    def children(self, key) -> list[dict]:
        payload, _ = self._local_json(f"{_USER}/items/{key}/children")
        return self._validate_object_list(payload, "children")

    def annotations(self, key) -> list[dict]:
        """§3.3 step 2's route; measured but unwired this iteration (decision 28)."""
        payload, _ = self._local_json(f"{_USER}/items/{key}/children?itemType=annotation")
        return self._validate_object_list(payload, "annotations")

    def fulltext(self, attachment_key) -> dict | None:
        try:
            payload, _ = self._local_json(f"{_USER}/items/{attachment_key}/fulltext")
        except NotFoundError:
            return None
        if not isinstance(payload, Mapping) or not isinstance(payload.get("content"), str):
            raise ZoteroError("malformed fulltext response: expected content")
        return dict(payload)

    def file_view_url(self, attachment_key) -> str | None:
        try:
            response = self._local(f"{_USER}/items/{attachment_key}/file/view/url")
        except (NotFoundError, ZoteroError) as error:
            if isinstance(error, (DatabaseChangedError, LocalApiDisabledError)):
                raise
            return None
        text = response.body.decode("utf-8", errors="replace").strip()
        return text or None

    def versions(self) -> tuple[dict[str, int], int | None]:
        payload, headers = self._local_json(f"{_USER}/items?since=0&format=versions")
        return self._versions_map(payload, "versions"), self._version_header(headers)

    def trash_versions(self) -> dict[str, int]:
        payload, _ = self._local_json(f"{_USER}/items/trash?format=versions")
        return self._versions_map(payload, "trash versions")

    @staticmethod
    def _versions_map(payload, context) -> dict[str, int]:
        if not isinstance(payload, Mapping) or not all(
            isinstance(k, str) and isinstance(v, int) for k, v in payload.items()
        ):
            raise ZoteroError(f"malformed {context}: expected a key-to-version map")
        return dict(payload)

    def top_items(self) -> tuple[list[dict], int | None]:
        payload, headers = self._local_json(f"{_USER}/items/top?format=json")
        return self._validate_object_list(payload, "top items"), self._version_header(headers)

    def library_csl(self, library_name) -> list[dict]:
        """The whole library as Better CSL JSON in one read (§3.3 step 4).

        Undocumented route; ``export_csl`` is the documented fallback.
        """
        quoted = urllib.parse.quote(library_name, safe="")
        response = self._http(f"{self.base}/better-bibtex/library?/{quoted}.json")
        if response.status != 200:
            raise ZoteroError(f"Better BibTeX library route HTTP {response.status}")
        items = self._decode_json(response.body, "Better BibTeX library export")
        return self._validate_csl_items(items, "Better BibTeX library export")

    # -- local API writes (§2) ------------------------------------------------

    def authorize(self, app_name: str = APP_NAME) -> dict:
        """POST /api/local/authorize: Zotero shows Allow / Always Allow / Deny."""
        if not self.server_id:
            raise ZoteroError("authorize needs the live server id (428 without it)", Result.UNMATCHED)
        response = self._local(
            "/api/local/authorize",
            data=json.dumps({"appName": app_name}).encode(),
            method="POST",
            expect=(200, 403, 429),
        )
        if response.status == 429:
            retry = response.headers.get("Retry-After", "60")
            raise ZoteroError(f"authorize rate-limited; retry after {retry} s")
        payload = self._decode_json(response.body, "authorize response")
        if response.status == 403 or (isinstance(payload, Mapping) and payload.get("denied")):
            raise ZoteroError("authorization denied", Result.UNMATCHED)
        if not isinstance(payload, Mapping) or not isinstance(payload.get("key"), str):
            raise ZoteroError("malformed authorize response: expected a key")
        return {"key": payload["key"], "remember": bool(payload.get("remember"))}

    def create_items(self, items: list[dict]) -> dict:
        """POST up to 50 items; returns Zotero's successful/unchanged/failed envelope."""
        if not self.api_key:
            raise ZoteroError("create_items needs an API key from authorize", Result.UNMATCHED)
        response = self._local(
            f"{_USER}/items", data=json.dumps(items).encode(), method="POST", expect=(200, 401)
        )
        if response.status == 401:
            raise ZoteroError("API key rejected (401); re-authorize", Result.UNMATCHED)
        payload = self._decode_json(response.body, "create response")
        if not isinstance(payload, Mapping) or "successful" not in payload:
            raise ZoteroError("malformed create response: expected successful/unchanged/failed")
        return dict(payload)

    # -- Better BibTeX JSON-RPC -------------------------------------------------

    def _rpc(self, method: str, params: list) -> object:
        ...  # unchanged from today's implementation

    def ready(self) -> dict:
        result = self._rpc("api.ready", [])
        if not isinstance(result, dict):
            raise ZoteroError("malformed api.ready result: expected an object")
        return result

    def attachments(self, citation_key: str) -> list[dict]:
        """BBT ``item.attachments``: the annotation fallback §3.3 step 2 names (unwired)."""
        result = self._rpc("item.attachments", [citation_key])
        return self._validate_object_list(result, "item.attachments result")

    def export_csl(self, citation_keys: list[str]) -> list[dict]:
        """BBT ``item.export``: the documented CSL fallback (§3.3 step 4)."""
        exported = self._rpc("item.export", [citation_keys, CSL_TRANSLATOR])
        if not isinstance(exported, list):
            exported = self._decode_json(exported, "item.export result")
        return self._validate_csl_items(exported, "item.export result")
```

(`_rpc` body is the existing one, verbatim.) In `research_vault/__main__.py`: `main()` resolves `args.base = zotero.base_for(getattr(args, "vault", None), getattr(args, "base", None))` after parsing; `cmd_probe` becomes

```python
def cmd_probe(args):
    client = ZoteroClient(base=args.base)
    report = {}
    try:
        report["server"] = client.server_info()
        report["bbt"] = client.ready()
    except ZoteroError as error:
        report["result"] = Result.UNREACHABLE.value
        report["detail"] = str(error)
        print(json.dumps(report))
        return 3
    print(json.dumps(report))
    return 0
```

`research_vault/verify.py:40`: `from .zotero import DEFAULT_BASE  # re-exported for the CLI`.

- [ ] **Step 4: Run the suite and form owners**

Run: `.venv/bin/python -m pytest tests -q -n auto && ruff format research_vault tests && ruff check research_vault tests && mypy research_vault`
Expected: PASS, clean. Then, with Zotero up: `RV_LIVE=1 .venv/bin/python -m pytest tests/test_zotero.py -q -k live` — PASS; and `.venv/bin/python -m research_vault probe` prints the server block with `"server_id": "6LpvURP2E933"`.

- [ ] **Step 5: Commit**

```bash
git commit -m "rewrite the Zotero client for the local API (ingest spec §3.7)

Reads carry the recorded server id and a 412 is typed database-changed;
403 is typed local-API-off; writes take the documented authorize path.
The base URL is configuration: --base, then machine.json, then default.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- research_vault tests
```

### Task 10: The text layer, `fulltext/<attachment key>.md` (spec §3.3 step 3, §3.6)

**Files:**

- Create: `research_vault/fulltext.py`, `tests/test_fulltext.py`
- Modify: `research_vault/templates/vault/gitignore` (add `fulltext/`), `research_vault/templates/vault/markdownlintignore`, `prettierignore`, `editorconfig` (add `/fulltext/` and a `[fulltext/**]` section), `hooks/pretooluse_guard.py:11` (`MACHINE_SURFACE_DIR_NAMES` adds `"fulltext"`), `tests/test_templates.py` (the ignore-list assertions at :208-216), `tests/test_hooks.py` (a deny test for `fulltext/X.md`), `research_vault/scaffold.py` (nothing: `fulltext/` does **not** join `VAULT_DIRS`, spec §3.6)

**Interfaces:**

- Produces: the Interface index `research_vault/fulltext.py` block. The written file's frontmatter is deterministic (no timestamps), so its sha256 is stable across re-runs of unchanged text:

```
---
type: "fulltext"
zotero-attachment-key: "D7EJ9FTG"
zotero-item-key: "E352DFS8"
indexedPages: 15
totalPages: 15
---
<content verbatim, form feeds included>
```

- [ ] **Step 1: Write the failing tests**

`tests/test_fulltext.py`:

```python
import hashlib

from research_vault import frontmatter, fulltext


def test_verdict_separates_absent_partial_empty_and_complete():
    assert fulltext.verdict(None) == (False, "no-index")
    assert fulltext.verdict({"content": "x" * 900, "indexedPages": 100, "totalPages": 143}) == (
        False, "partial — indexedPages 100 of 143"
    )
    assert fulltext.verdict({"content": "Masthead " * 12, "indexedPages": 9, "totalPages": 9}) == (
        False, "empty — 108 characters below floor 500"
    )
    assert fulltext.verdict({"content": "y" * 600, "indexedChars": 600, "totalChars": 600}) == (
        True, "complete"
    )
    assert fulltext.verdict({"content": "y" * 600, "indexedChars": 600, "totalChars": 700}) == (
        False, "partial — indexedChars 600 of 700"
    )


def test_write_renders_deterministic_frontmatter_and_verbatim_body(tmp_vault):
    response = {"content": "Page one\fPage two", "indexedPages": 2, "totalPages": 2}
    path, digest = fulltext.write(tmp_vault, "D7EJ9FTG", "E352DFS8", response)
    assert path == tmp_vault / "fulltext" / "D7EJ9FTG.md"
    raw = path.read_bytes()
    assert digest == hashlib.sha256(raw).hexdigest() == fulltext.sha256_of(path)
    data, body = frontmatter.parse(raw.decode())
    assert data == {
        "type": "fulltext",
        "zotero-attachment-key": "D7EJ9FTG",
        "zotero-item-key": "E352DFS8",
        "indexedPages": 2,
        "totalPages": 2,
    }
    assert body == "Page one\fPage two"
    again, digest_again = fulltext.write(tmp_vault, "D7EJ9FTG", "E352DFS8", response)
    assert digest_again == digest


def test_write_refuses_an_unsafe_attachment_key(tmp_vault):
    import pytest

    with pytest.raises(ValueError):
        fulltext.write(tmp_vault, "../x", "E352DFS8", {"content": "c"})
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_fulltext.py -q`
Expected: FAIL — `ModuleNotFoundError`.

- [ ] **Step 3: Implement `research_vault/fulltext.py`**

```python
"""The text layer: one OKF-conformant file per indexed attachment (spec §3.6).

Derived, gitignored, regenerable from Zotero's index; Obsidian indexes it;
the literature note records each file's sha256. The hash is machine-local.
"""

import hashlib
from pathlib import Path
from typing import NamedTuple

from . import frontmatter
from .zotero import ITEM_KEY

FULLTEXT_DIR = "fulltext"
# Four times the largest masthead §9 measured on a scanned PDF (126 chars)
# and an order of magnitude below one page of body text.
FULLTEXT_MIN_CHARS = 500


class TextVerdict(NamedTuple):
    usable: bool
    reason: str


def verdict(response) -> TextVerdict:
    """The two tests §3.3 step 3 requires: page/char completeness, then a content floor."""
    if response is None:
        return TextVerdict(False, "no-index")
    if "indexedPages" in response:
        indexed, total, unit = response.get("indexedPages"), response.get("totalPages"), "indexedPages"
    else:
        indexed, total, unit = response.get("indexedChars"), response.get("totalChars"), "indexedChars"
    if not isinstance(indexed, int) or not isinstance(total, int):
        return TextVerdict(False, f"malformed — {unit} pair missing")
    if indexed < total:
        return TextVerdict(False, f"partial — {unit} {indexed} of {total}")
    length = len(response.get("content") or "")
    if length < FULLTEXT_MIN_CHARS:
        return TextVerdict(False, f"empty — {length} characters below floor {FULLTEXT_MIN_CHARS}")
    return TextVerdict(True, "complete")


def path_for(vault_root, attachment_key) -> Path:
    if not ITEM_KEY.match(attachment_key or ""):
        raise ValueError(f"unsafe attachment key: {attachment_key!r}")
    return Path(vault_root) / FULLTEXT_DIR / f"{attachment_key}.md"


def _render(attachment_key, item_key, response) -> str:
    fields: list[tuple[str, object]] = [
        ("type", "fulltext"),
        ("zotero-attachment-key", attachment_key),
        ("zotero-item-key", item_key),
    ]
    for pair in (("indexedPages", "totalPages"), ("indexedChars", "totalChars")):
        if pair[0] in response:
            fields.extend((name, int(response[name])) for name in pair)
    return frontmatter.serialize(dict(fields)) + (response.get("content") or "")


def write(vault_root, attachment_key, item_key, response) -> tuple[Path, str]:
    target = path_for(vault_root, attachment_key)
    target.parent.mkdir(parents=True, exist_ok=True)
    text = _render(attachment_key, item_key, response)
    with target.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)
    return target, hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_of(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
```

Templates: append `fulltext/` to `templates/vault/gitignore`; append `/fulltext/` to `markdownlintignore` and `prettierignore` (and extend their header comments: "plus fulltext/ (capture's derived text layer)"); add to `editorconfig`:

```
[fulltext/**]
insert_final_newline = false
trim_trailing_whitespace = false
```

`hooks/pretooluse_guard.py:11`: `MACHINE_SURFACE_DIR_NAMES = frozenset({"literatures", "log", "wiki", "fulltext"})`. Update `tests/test_templates.py:208-216` expected lists and add `Path("fulltext") / "D7EJ9FTG.md"` to the `relative` list of `tests/test_hooks.py::test_pretooluse_denies_edit_into_every_machine_surface` (and the same path to Task 6's `test_pretooluse_denies_write_under_wiki` list, renamed `test_pretooluse_denies_write_under_machine_layers` if the name now reads wrong).

- [ ] **Step 4: Run the suite and form owners; commit**

Run: `.venv/bin/python -m pytest tests -q -n auto && ruff format research_vault tests hooks && ruff check research_vault tests hooks && mypy research_vault`
Expected: PASS, clean.

```bash
git commit -m "add the text layer fulltext/<attachment key>.md (ingest spec §3.6)

Gitignored, OKF-conformant, regenerable; the usability verdict applies
the page/char completeness test and a 500-character content floor.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- research_vault tests hooks
```

### Task 11: The literature note record — snapshot, provenance tuple, body (spec §3.2, §3.3 step 5)

**Files:**

- Modify: `research_vault/notes.py` (add the record; keep Task 5's helpers), `research_vault/lints.py` (`_MACHINE_OWNED_FRONTMATTER_KEYS = notes.CAPTURE_FIELDS`), `tests/conftest.py` (the two fixture notes take the new frontmatter shape — see Step 1), `tests/test_lints.py` (attestation tests name `citationKey`/`zotero-item-version` instead of `fixity-sha256`), `README.md` (the machine-surface sentence at `:7` and the whole `## The layers` section describe the managed region, the free region and `synthesis/`, all gone by now; this task lands the record they should describe — see Step 3's closing paragraph)
- Test: `tests/test_notes.py`

**Interfaces:**

- Consumes: `frontmatter.serialize/parse`, `notes.display_text`, `notes.body_sha256`, `notes._valid_generated`, `AGENT_ACTOR`.

- Produces: the Interface index `research_vault/notes.py` block. Frontmatter order: `type`, `title`, `aliases`, the snapshot fields present (in `SNAPSHOT_FIELDS` order; `title` is not repeated), the tuple fields in `TUPLE_FIELDS` order, `accessed`, `managed-sha256`, `generated`, then every prior non-capture field in its prior order (the verifier's `verified` list, human-set keys). Body order (spec §3.3 step 5 as revised 2026-09-07, decision 27): `## Compiled` with one `![[<page path>]]` per path in the ledger's `pages[]` for this note's text files — the section is absent before the first compile; `## Item` with `- [Open in Zotero](zotero://select/library/items/<item key>)`; `## Attachments`; `## Zotero notes`. `compiled_pages(vault_root, provenance)` reads `LEDGER_PATH` and matches records by `origin.locator == fulltext/<attachment key>.md`; a missing or unreadable ledger yields `[]` (the captured-set lint owns that finding).

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_notes.py`:

```python
import dataclasses
import json

from tests.fakes import ATTACHMENT, CHILD_NOTE, ITEM

PROVENANCE = notes.Provenance(
    server_id="6LpvURP2E933",
    item_key="E352DFS8",
    item_version=544,
    citation_key="jakesch.etal2023a",
    attachments=(
        {"key": "D7EJ9FTG", "version": 551, "md5": "aa59569ae4f4b3a7c546158d4771c738",
         "contentType": "application/pdf", "filename": "Jakesch et al. - 2023.pdf"},
    ),
    fulltext=({"attachment-key": "D7EJ9FTG", "sha256": "f" * 64},),
    compile_input_sha256="f" * 64,
)


def _render(existing=None, generated_at="2026-09-07T10:00:00Z", pages=()):
    return notes.render_note(
        ITEM["data"], PROVENANCE, [ATTACHMENT], [CHILD_NOTE], existing,
        accessed="2026-09-07", generated_at=generated_at, pages=pages,
    )


def test_render_note_carries_snapshot_tuple_and_witness_in_order():
    text = _render()
    data, body = frontmatter.parse(text)
    keys = list(data)
    assert keys[:3] == ["type", "title", "aliases"]
    assert data["type"] == "literature"
    assert data["aliases"] == [ITEM["data"]["title"]]
    assert data["creators"] == [{"creatorType": "author", "firstName": "Maurice", "lastName": "Jakesch"}]
    assert data["abstractNote"] == ["Line one.", "Line two."]  # ITEM's second line carries a tab and a double space; display_text collapses both
    assert data["extra"] == ["PMID: 28503678", "PMCID: PMC5428074"]
    assert data["tags"] == [{"tag": "ai", "type": 1}]
    assert data["DOI"] == "10.1145/3544548.3581196"
    assert "relations" not in data and "dateModified" not in data
    assert data["zotero-server-id"] == "6LpvURP2E933"
    assert data["zotero-item-key"] == "E352DFS8"
    assert data["zotero-item-version"] == 544
    assert data["citationKey"] == "jakesch.etal2023a"
    assert data["attachments"][0]["md5"] == "aa59569ae4f4b3a7c546158d4771c738"
    assert data["fulltext"] == [{"attachment-key": "D7EJ9FTG", "sha256": "f" * 64}]
    assert data["compile-input-sha256"] == "f" * 64
    assert data["accessed"] == "2026-09-07"
    assert data["managed-sha256"] == notes.body_sha256(text)
    assert data["generated"] == {"by": AGENT_ACTOR, "at": "2026-09-07T10:00:00Z"}
    assert keys.index("generated") == len(keys) - 1


def test_body_renders_only_what_frontmatter_cannot_carry():
    _data, body = frontmatter.parse(_render())
    assert body == (
        "## Item\n\n"
        "- [Open in Zotero](zotero://select/library/items/E352DFS8)\n\n"
        "## Attachments\n\n"
        "- [Jakesch et al. - 2023.pdf](zotero://open-pdf/library/items/D7EJ9FTG) "
        "— application/pdf, md5 aa59569ae4f4b3a7c546158d4771c738, text layer [[fulltext/D7EJ9FTG]]\n\n"
        "## Zotero notes\n\n"
        "Read for the method.\n\nSecond paragraph.\n"
    )
    assert "Co-writing" not in body  # title lives in frontmatter only
    assert "## Compiled" not in body  # absent until the first compile (§3.3 step 5)


def test_body_embeds_the_compiled_page_by_ledger_path_when_one_exists():
    _data, body = frontmatter.parse(_render(pages=["wiki/sources/Co-Writing with Opinionated Language Models.md"]))
    assert body.startswith(
        "## Compiled\n\n![[wiki/sources/Co-Writing with Opinionated Language Models.md]]\n\n## Item\n\n"
    )


def test_compiled_pages_reads_the_ledger_by_locator(tmp_path):
    assert notes.compiled_pages(tmp_path, PROVENANCE) == []
    ledger = tmp_path / "wiki" / "meta" / "ledgers" / "source-ledger.json"
    ledger.parent.mkdir(parents=True)
    ledger.write_text(json.dumps({"schema": "claude-obsidian.source-ledger.v1", "sources": {
        "src-1": {"origin": {"kind": "file", "locator": "fulltext/D7EJ9FTG.md"}, "pages": ["wiki/sources/B.md", "wiki/sources/A.md"]},
        "src-2": {"origin": {"kind": "file", "locator": "fulltext/OTHER001.md"}, "pages": ["wiki/sources/C.md"]},
    }}))
    assert notes.compiled_pages(tmp_path, PROVENANCE) == ["wiki/sources/A.md", "wiki/sources/B.md"]
    ledger.write_text("not json")
    assert notes.compiled_pages(tmp_path, PROVENANCE) == []


def test_rerender_keeps_accessed_generated_and_foreign_fields_when_unchanged():
    first = _render()
    with_events = first.replace(
        "---\n## Item", 'verified:\n  - {by: "research_vault/0.1.0", at: "2026-09-07", check: "update-notice"}\n---\n## Item', 1
    )
    second = notes.render_note(
        ITEM["data"], PROVENANCE, [ATTACHMENT], [CHILD_NOTE], with_events,
        accessed="2026-09-08", generated_at="2026-09-08T00:00:00Z",
    )
    data, _ = frontmatter.parse(second)
    assert data["accessed"] == "2026-09-07"
    assert data["generated"]["at"] == "2026-09-07T10:00:00Z"
    assert data["verified"][0]["check"] == "update-notice"
    assert not notes.content_changed(with_events, second)


def test_rerender_bumps_generated_when_the_projection_moved():
    first = _render()
    moved = dataclasses.replace(PROVENANCE, item_version=545)
    second = notes.render_note(
        ITEM["data"], moved, [ATTACHMENT], [CHILD_NOTE], first,
        accessed="2026-09-08", generated_at="2026-09-08T00:00:00Z",
    )
    data, _ = frontmatter.parse(second)
    assert data["zotero-item-version"] == 545
    assert data["generated"]["at"] == "2026-09-08T00:00:00Z"
    assert data["accessed"] == "2026-09-07"


def test_read_provenance_round_trips_and_rejects_partial_tuples():
    text = _render()
    assert notes.read_provenance(text) == PROVENANCE
    assert notes.read_provenance('---\ntype: "literature"\ncitationKey: "x"\n---\n') is None
    assert notes.read_provenance("no frontmatter") is None


def test_linked_attachment_says_it_has_no_fixity():
    linked = {"key": "LINK0001", "version": 3, "data": {"key": "LINK0001", "version": 3,
              "itemType": "attachment", "linkMode": "linked_url", "url": "https://x"}}
    text = notes.render_note(
        ITEM["data"],
        dataclasses.replace(PROVENANCE, attachments=({"key": "LINK0001", "version": 3, "md5": "absent",
                                                       "contentType": "", "filename": ""},), fulltext=(), compile_input_sha256=None),
        [linked], [], None, accessed="2026-09-07", generated_at="2026-09-07T10:00:00Z",
    )
    data, body = frontmatter.parse(text)
    assert data["attachments"][0]["md5"] == "absent"
    assert "compile-input-sha256" not in data
    assert "- LINK0001 — linked, no fixity" in body
```

(Import `dataclasses` at the top of the test file; `Provenance` is a frozen dataclass, so `dataclasses.replace` is the spelling.) Replace `tests/conftest.py`'s `smith2020` frontmatter with:

```
---
type: "literature"
title: "Mortality decline"
aliases:
  - "Mortality decline"
itemType: "journalArticle"
DOI: "10.1000/xyz"
zotero-server-id: "6LpvURP2E933"
zotero-item-key: "SMITH2020"
zotero-item-version: 12
citationKey: "smith2020"
attachments:
  - {key: "ATT00001", version: 13, md5: "aa11aa11aa11aa11aa11aa11aa11aa11", contentType: "application/pdf", filename: "smith2020.pdf"}
fulltext:
  - {attachment-key: "ATT00001", sha256: "aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11"}
compile-input-sha256: "aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11"
accessed: "2026-08-16"
generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}
---
```

(`_with_body_witness` inserts `managed-sha256` after `type`; the order test above applies to capture's output, not to fixtures.) `gone2019` gets the same shape with `DOI: "10.1000/old"`, key `GONE2019`, version 7, no attachments, no fulltext.

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_notes.py -q`
Expected: FAIL — `notes.Provenance` undefined.

- [ ] **Step 3: Implement the record in `research_vault/notes.py`**

```python
import dataclasses
import json
from html.parser import HTMLParser

SNAPSHOT_FIELDS: tuple[str, ...] = (
    "itemType", "title", "creators", "date", "DOI", "url", "publicationTitle",
    "volume", "issue", "pages", "publisher", "ISBN", "language", "abstractNote",
    "extra", "accessDate", "tags",
)
TUPLE_FIELDS: tuple[str, ...] = (
    "zotero-server-id", "zotero-item-key", "zotero-item-version", "citationKey",
    "attachments", "fulltext", "compile-input-sha256", "generated",  # generated is emitted last by render_note, after accessed and managed-sha256
)
CAPTURE_FIELDS: frozenset[str] = (
    frozenset(SNAPSHOT_FIELDS)
    | frozenset(TUPLE_FIELDS)
    | frozenset({"type", "aliases", "accessed", "managed-sha256"})
)
_ATTACHMENT_KEYS = ("key", "version", "md5", "contentType", "filename")
LEDGER_PATH = "wiki/meta/ledgers/source-ledger.json"  # the compile tool's ledger; captured.py and compile.py import this name


@dataclasses.dataclass(frozen=True)
class Provenance:
    server_id: str
    item_key: str
    item_version: int
    citation_key: str
    attachments: tuple[dict, ...]
    fulltext: tuple[dict, ...]
    compile_input_sha256: str | None


def frontmatter_value(value):
    """Decision 9: a string with line breaks becomes a list of its lines."""
    if isinstance(value, str):
        # Each line goes through display_text: the codec rejects every C0 control, and a tab
        # inside an abstract must not hold the whole capture.
        lines = [display_text(line) for line in value.splitlines()]
        return lines if len(lines) > 1 else display_text(value)
    if isinstance(value, list):
        return [
            {k: display_text(v) if isinstance(v, str) else v for k, v in item.items()}
            if isinstance(item, dict)
            else display_text(item)
            for item in value
        ]
    return value


def snapshot(item_data) -> list[tuple[str, object]]:
    """The fixed subset, verbatim, under Zotero's own names; empty values absent."""
    fields = []
    for name in SNAPSHOT_FIELDS:
        value = item_data.get(name)
        if value in (None, "", []):
            continue
        fields.append((name, frontmatter_value(value)))
    return fields


class _TextExtractor(HTMLParser):
    _BREAKS = {"p", "br", "li", "div", "h1", "h2", "h3", "h4", "h5", "h6", "tr"}

    def __init__(self):
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in self._BREAKS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self._BREAKS:
            self.parts.append("\n")

    def handle_data(self, data):
        self.parts.append(data)


def html_to_text(html: str) -> str:
    """Zotero child notes are HTML; the body carries their text, paragraphs kept."""
    extractor = _TextExtractor()
    extractor.feed(html or "")
    paragraphs = [" ".join(p.split()) for p in "".join(extractor.parts).split("\n")]
    return "\n\n".join(p for p in paragraphs if p)


def _attachment_line(child) -> str:
    data = child.get("data", {})
    key = child.get("key", "")
    if data.get("linkMode") not in {"imported_file", "imported_url"} or not data.get("md5"):
        return f"- {key} — linked, no fixity"
    name = display_text(data.get("filename") or key)
    line = (
        f"- [{name}](zotero://open-pdf/library/items/{key}) — "
        f"{display_text(data.get('contentType'))}, md5 {data['md5']}"
    )
    return line


def compiled_pages(vault_root, provenance: Provenance) -> list[str]:
    """The ledger's pages[] for this note's text files, matched by locator (§3.3 step 5).

    Empty before the first compile. An unreadable ledger renders no embed here;
    reporting it is the captured-set lint's job, not capture's. Only records the
    wrapper wrote match (their locator is fulltext/<key>.md, spec §4.5); a record
    from any other route embeds nothing and the same lint reports it not-captured.
    """
    ledger = Path(vault_root) / LEDGER_PATH
    if not ledger.is_file():
        return []
    try:
        sources = json.loads(ledger.read_text(encoding="utf-8")).get("sources", {})
    except (OSError, UnicodeError, ValueError, AttributeError):
        return []
    locators = {f"fulltext/{entry.get('attachment-key')}.md" for entry in provenance.fulltext}
    pages: set[str] = set()
    for record in sources.values() if isinstance(sources, dict) else ():
        origin = record.get("origin", {}) if isinstance(record, dict) else {}
        if isinstance(origin, dict) and origin.get("locator") in locators:
            pages.update(page for page in record.get("pages", []) if isinstance(page, str))
    return sorted(pages)


def render_body(provenance: Provenance, children, child_notes, pages=()) -> str:
    cached = {entry["attachment-key"] for entry in provenance.fulltext}
    lines = []
    if pages:
        lines.append("## Compiled\n")
        lines.extend(f"![[{page}]]" for page in pages)
        lines.append("")
    lines.append("## Item\n")
    lines.append(f"- [Open in Zotero](zotero://select/library/items/{provenance.item_key})")
    lines.append("")
    attachments = [c for c in children if c.get("data", {}).get("itemType") == "attachment"]
    if attachments:
        lines.append("## Attachments\n")
        for child in attachments:
            line = _attachment_line(child)
            if child.get("key") in cached:
                line += f", text layer [[fulltext/{child['key']}]]"
            lines.append(line)
        lines.append("")
    notes_text = [html_to_text(n.get("data", {}).get("note", "")) for n in child_notes]
    notes_text = [t for t in notes_text if t]
    if notes_text:
        lines.append("## Zotero notes\n")
        lines.append("\n\n".join(notes_text))
    body = "\n".join(lines)
    return body + "\n" if body and not body.endswith("\n") else body


def _tuple_fields(provenance: Provenance) -> list[tuple[str, object]]:
    fields: list[tuple[str, object]] = [
        ("zotero-server-id", provenance.server_id),
        ("zotero-item-key", provenance.item_key),
        ("zotero-item-version", provenance.item_version),
        ("citationKey", provenance.citation_key),
        ("attachments", [dict(a) for a in provenance.attachments]),
        ("fulltext", [dict(f) for f in provenance.fulltext]),
    ]
    if provenance.compile_input_sha256:
        fields.append(("compile-input-sha256", provenance.compile_input_sha256))
    return fields


def _projection(items) -> list[tuple[str, object]]:
    return [(k, v) for k, v in items if k in CAPTURE_FIELDS and k not in {"generated", "managed-sha256", "accessed"}]


def render_note(item_data, provenance, children, child_notes, existing, accessed, generated_at, pages=()) -> str:
    """Frontmatter, then only what frontmatter cannot carry, plus the three pointers (§3.3 step 5)."""
    prior = frontmatter.parse(existing)[0] if existing else {}
    prior_items = list(frontmatter._mapping_items(prior))
    title = display_text(item_data.get("title") or provenance.citation_key)
    fields: list[tuple[str, object]] = [("type", "literature"), ("title", title), ("aliases", [title])]
    fields.extend((k, v) for k, v in snapshot(item_data) if k != "title")
    fields.extend(_tuple_fields(provenance))
    body = render_body(provenance, children, child_notes, pages)
    prior_body = note_body(existing) if existing else None
    unchanged = (
        existing is not None
        and _projection(prior_items) == _projection(fields)
        and prior_body == body
        and _valid_generated(prior.get("generated"))
        and str(prior["generated"]["by"]).startswith(AGENT_ACTOR.split("/")[0] + "/")
    )
    prior_accessed = prior.get("accessed")
    fields.append(("accessed", prior_accessed if isinstance(prior_accessed, str) and prior_accessed else accessed))
    fields.append(("managed-sha256", hashlib.sha256(body.encode("utf-8")).hexdigest()))
    at = prior["generated"]["at"] if unchanged else generated_at
    fields.append(("generated", {"by": AGENT_ACTOR, "at": at}))
    rendered = {k for k, _ in fields}
    fields.extend((k, v) for k, v in prior_items if k not in CAPTURE_FIELDS and k not in rendered)
    return frontmatter.serialize(frontmatter._mapping_from_items(fields)) + body


def read_provenance(text: str) -> Provenance | None:
    try:
        data, _ = frontmatter.parse(text)
    except frontmatter.FrontmatterError:
        return None
    try:
        attachments = tuple(dict(a) for a in data.get("attachments", []) if isinstance(a, dict))
        fulltext = tuple(dict(f) for f in data.get("fulltext", []) if isinstance(f, dict))
        provenance = Provenance(
            server_id=str(data["zotero-server-id"]),
            item_key=str(data["zotero-item-key"]),
            item_version=int(data["zotero-item-version"]),
            citation_key=str(data["citationKey"]),
            attachments=attachments,
            fulltext=fulltext,
            compile_input_sha256=data.get("compile-input-sha256") or None,
        )
    except (KeyError, TypeError, ValueError):
        return None
    if not ITEM_KEY_RE.match(provenance.item_key) or not provenance.citation_key:
        return None
    return provenance
```

with `ITEM_KEY_RE = re.compile(r"^[A-Z0-9]{8}$")` (duplicated here rather than importing `zotero`, so `notes` stays transport-free). `research_vault/lints.py`: `_MACHINE_OWNED_FRONTMATTER_KEYS = notes.CAPTURE_FIELDS` with the comment "every field capture writes; a change to any without a `generated` bump by the machine actor is drift".

`README.md`, which this task's record makes describable. The sentence at `:7` beginning "No skill hand-edits a managed region or machine surface" becomes:

```markdown
No skill hand-edits a machine surface — `literatures/`, `fulltext/`, `wiki/`, `log/`, `system/`, the review queue — mints a verification event, or files a review record: those are verbs, and only the CLI runs them (under `wiki/`, the adopted compile tool's transaction engine). Prose is composed by hand where it belongs: project drafts, and per-source notes written in Zotero, which capture renders into the literature note.
```

`## The layers` becomes, whole:

```markdown
## The layers

- **`literatures/`** — one note per captured source, wholly machine-written: `capture` regenerates the whole note from Zotero on every run — frontmatter carrying Zotero's own fields and the provenance tuple (server id, item key, item version, citation key, attachments, text files); a body carrying the embed of the compiled page once one exists, the item and attachment links into Zotero, and the item's Zotero child notes. Per-source prose is written in Zotero as a child note, and capture renders it.
- **`fulltext/`** — the text layer, gitignored: one `<attachment key>.md` per attachment with usable extracted text, regenerated by capture; the compile input.
- **`wiki/`** — the compiled layer, arrangement not evidence, written only by the adopted compile tool (claude-obsidian) through its transaction gate: per-source pages under `wiki/sources/`, concept pages under `wiki/concepts/`, each citing its source as `[[<citation key>]]`. A page earns its existence at two or more captured sources on the same topic, and that threshold *permits* a page without obligating one — sources set side by side with nothing said about how they relate are a compilation, not a synthesis.
- **`projects/`** — the framed question, the search log, the draft. One project note carries the disposition frontmatter.
- **`inbox/`**, **`log/`** — the review queue and the append-only activity log.
```

Two sentences elsewhere name the old flow and are rewritten in the same terms: `:19` ("Claims get copied — from a literature note into a synthesis page, from synthesis into a draft") — claims are written in project drafts, never in the machine-written literature note, and arranged into `wiki/` pages by the compile tool; `:75` ("already in synthesis") becomes "already in a draft or a compiled page". `grep -n 'managed region\|free region\|synthesis/\|admitted' README.md` must print nothing afterwards (the skills table rows at `:83-84` and `:89` are Task 19's).

- [ ] **Step 4: Run the suite and form owners; commit**

Run: `.venv/bin/python -m pytest tests -q -n auto && ruff format research_vault tests && ruff check research_vault tests && mypy research_vault`
Expected: PASS, clean (the `C90` cap may push `render_note` to split `_projection`/`_tuple_fields` further; keep the names above).

```bash
git commit -m "render the literature note as snapshot, tuple and body (ingest spec §3.2)

Zotero's field names verbatim, every dependent object's key and version,
and a body carrying only the attachment list and the child notes.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- research_vault tests README.md
```

### Task 12: The lifecycle linter (spec §1 table, §3.4, §3.5 detection, §7 fixtures)

**Files:**

- Create: `research_vault/lifecycle.py`, `tests/test_lifecycle.py`, `tests/fixtures/lifecycle/README.md`, `tests/fixtures/lifecycle/{items-before,items-after-delete,trash-before,trash-trashed,trash-after-delete}.json`
- Modify: `research_vault/inbox.py` (`REASON_CODES` add `re-keyed`, `merged`, `trashed`, `deleted`, `database-changed`; `CHECK_IDS` add `lifecycle`), `skills/evidence-conventions/SKILL.md` (five rows), `docs/terminology.md` §4.4, `research_vault/verify.py` (`_plan_state`: online → `lifecycle.lint_lifecycle(vault, ZoteroClient(base=base))`; offline → one synthetic-offline `lifecycle` UNREACHABLE outcome on target `vault`), `research_vault/templates/git/pre-commit` (comment only: "the lifecycle leg is held — verify --offline reports it UNREACHABLE and never blocks; ingest spec invariant 5")

**Interfaces:**

- Consumes: `notes.read_provenance`, `notes.Provenance`, `ZoteroClient.versions/trash_versions/top_items/children`, `fulltext.path_for/sha256_of`, `zotero.DatabaseChangedError`.

- Produces: the Interface index `research_vault/lifecycle.py` block. `classify` returns one of `("current", "")`, `("drifted", "<detail>")`, `("re-keyed", "old → new")`, `("merged", "<successor key>")`, `("trashed", "<key>")`, `("deleted", "<key>")`. `lint_lifecycle` files one `Outcome("lifecycle", <citation key>, UNMATCHED, "<code> — <detail>")` per non-current note in the order `merged, deleted, trashed, re-keyed, drift`, a `MATCHED "matched"` per current note, and on a 412 exactly one `Outcome("lifecycle", "vault", UNMATCHED, "database-changed — ...")` and nothing else; on any other `ZoteroError` one `Outcome("lifecycle", "vault", UNREACHABLE, "outage — ...")`. With no provenance-bearing note, `lint_lifecycle` returns one `SKIPPED` outcome and never touches the client (decision 26).

- [ ] **Step 1: Build the fixtures and write the failing tests**

Trim the sitting's maps to the keys the tests need (the full maps are 51 KB and machine-specific; the trimmed shape is the observed shape):

```bash
mkdir -p tests/fixtures/lifecycle
python3 - <<'PY'
import json, pathlib
src = pathlib.Path.home() / "zotero-test-sitting" / "findings"
keep = {"ALKT2NF7", "NWHM4G5D", "E352DFS8", "DD3DBZ7Y", "II7E6CVR", "HEJXIP6W", "T6GF6HH7"}
out = pathlib.Path("tests/fixtures/lifecycle")
for name, target in [
    ("01-items-versions-before.json", "items-before.json"),
    ("06-items-versions-after-delete.json", "items-after-delete.json"),
    ("01-trash-versions-before.json", "trash-before.json"),
    ("06-trash-versions-trashed.json", "trash-trashed.json"),
    ("06-trash-versions-after-delete.json", "trash-after-delete.json"),
]:
    data = json.loads((src / name).read_text())
    (out / target).write_text(json.dumps({k: v for k, v in data.items() if k in keep}, indent=2, sort_keys=True) + "\n")
PY
```

`tests/fixtures/lifecycle/README.md`:

```markdown
# Lifecycle fixtures

Trimmed excerpts of the versions maps recorded on the Zotero test instance
(server id `Tdoqsn2J4q4h`, port 23129) during the 2026-09-07 sitting; the full
maps live outside the repository at `~/zotero-test-sitting/findings/`. Each file
keeps only the keys the tests name. Shapes are the observed shapes: flat
`{"<ITEMKEY>": <version>}` maps.

- `items-before.json` / `trash-before.json` — the baseline.
- `items-after-delete.json` — `ALKT2NF7` moved 0 → 1708 by a human edit (drifted).
- `trash-trashed.json` — `II7E6CVR` present at 1712 (trashed); **non-replayable
  as a transition**: no snapshot holds the item while it was live — it is absent
  from every items map here — so the pair shows only its arrival in the trash
  map, never its departure from the items map. Part B Task 5 takes the missing
  snapshot.
- `trash-after-delete.json` — `II7E6CVR` gone from both maps (deleted; replays).
```

`tests/test_lifecycle.py`:

```python
import json
from pathlib import Path

import pytest

from research_vault import Result, lifecycle, notes, zotero
from tests.fakes import FakeZotero

FIXTURES = Path(__file__).parent / "fixtures" / "lifecycle"


def _map(name):
    return json.loads((FIXTURES / name).read_text())


def _prov(item_key="ALKT2NF7", version=0, citation_key="alkt2026", attachments=(), fulltext=()):
    return notes.Provenance("Tdoqsn2J4q4h", item_key, version, citation_key, tuple(attachments), tuple(fulltext), None)


def _live(items, trash, top):
    return lifecycle.Live(items, trash, top)


def test_replaces_keys_accepts_a_uri_list_or_a_single_uri():
    assert lifecycle.replaces_keys(["http://zotero.org/users/1/items/T6GF6HH7"]) == {"T6GF6HH7"}
    assert lifecycle.replaces_keys("http://zotero.org/users/1/items/A1B2C3D4") == {"A1B2C3D4"}
    assert lifecycle.replaces_keys(None) == set()


def test_current_and_drifted_from_the_recorded_edit():
    before, after = _map("items-before.json"), _map("items-after-delete.json")
    top = {"ALKT2NF7": {"citationKey": "alkt2026", "replaces": set()}}
    assert lifecycle.classify(_prov(version=before["ALKT2NF7"]), _live(before, {}, top)) == ("current", "")
    state, detail = lifecycle.classify(_prov(version=before["ALKT2NF7"]), _live(after, {}, top))
    assert state == "drifted" and "ALKT2NF7" in detail and "1708" in detail


def test_child_version_moves_the_note_even_when_the_item_did_not():
    items = {"ALKT2NF7": 0, "ATT00001": 5}
    top = {"ALKT2NF7": {"citationKey": "alkt2026", "replaces": set()}}
    prov = _prov(attachments=({"key": "ATT00001", "version": 4, "md5": "x", "contentType": "", "filename": ""},))
    state, detail = lifecycle.classify(prov, _live(items, {}, top))
    assert state == "drifted" and "ATT00001" in detail


def test_rekeyed_when_the_live_citation_key_differs():
    top = {"ALKT2NF7": {"citationKey": "alkt2026a", "replaces": set()}}
    assert lifecycle.classify(_prov(), _live({"ALKT2NF7": 0}, {}, top)) == ("re-keyed", "alkt2026 → alkt2026a")


def test_merged_outranks_trashed_and_deleted():
    top = {"NEW00001": {"citationKey": "new2026", "replaces": {"ALKT2NF7"}}}
    assert lifecycle.classify(_prov(), _live({"NEW00001": 1}, {"ALKT2NF7": 9}, top)) == ("merged", "NEW00001")
    assert lifecycle.classify(_prov(), _live({"NEW00001": 1}, {}, top)) == ("merged", "NEW00001")


def test_trashed_and_deleted_from_the_sitting():
    prov = _prov(item_key="II7E6CVR", version=1711, citation_key="sitting2026")
    trashed = lifecycle.classify(prov, _live(_map("items-after-delete.json"), _map("trash-trashed.json"), {}))
    assert trashed == ("trashed", "II7E6CVR")
    deleted = lifecycle.classify(prov, _live(_map("items-after-delete.json"), _map("trash-after-delete.json"), {}))
    assert deleted == ("deleted", "II7E6CVR")


def test_lint_reads_three_routes_with_the_recorded_server_id(tmp_vault, monkeypatch):
    fake = FakeZotero(server_id="Tdoqsn2J4q4h")
    fake.get("/api/users/0/items?since=0&format=versions", body={"ALKT2NF7": 0}, headers={"Last-Modified-Version": "1707"})
    fake.get("/api/users/0/items/trash?format=versions", body={})
    fake.get("/api/users/0/items/top?format=json", body=[{"key": "ALKT2NF7", "version": 0, "data": {"citationKey": "alkt2026", "relations": {}}}])
    note = tmp_vault / "literatures" / "alkt2026.md"
    note.write_text(
        '---\ntype: "literature"\nzotero-server-id: "Tdoqsn2J4q4h"\nzotero-item-key: "ALKT2NF7"\n'
        'zotero-item-version: 0\ncitationKey: "alkt2026"\nattachments:\nfulltext:\n'
        'generated: {by: "research_vault/0.1.0", at: "2026-09-07T00:00:00Z"}\n---\n'
    )
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    outcomes = lifecycle.lint_lifecycle(tmp_vault, client)
    assert [(o.target, o.result) for o in outcomes] == [("alkt2026", Result.MATCHED)]
    assert all(call[2].get("Zotero-Server-ID") == "Tdoqsn2J4q4h" for call in fake.calls if call[0] == "GET")
    assert [call[1] for call in fake.calls if call[0] == "GET"] == [
        "/api/users/0/items?since=0&format=versions",
        "/api/users/0/items/trash?format=versions",
        "/api/users/0/items/top?format=json",
    ]


def test_database_changed_stops_and_reports_once(tmp_vault, monkeypatch):
    fake = FakeZotero(server_id="6LpvURP2E933")  # production answers, the tuple says test
    note = tmp_vault / "literatures" / "alkt2026.md"
    note.write_text(
        '---\ntype: "literature"\nzotero-server-id: "Tdoqsn2J4q4h"\nzotero-item-key: "ALKT2NF7"\n'
        'zotero-item-version: 0\ncitationKey: "alkt2026"\nattachments:\nfulltext:\n---\n'
    )
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    (outcome,) = lifecycle.lint_lifecycle(tmp_vault, client)
    assert (outcome.check, outcome.target, outcome.result) == ("lifecycle", "vault", Result.UNMATCHED)
    assert outcome.reason.startswith("database-changed")


def test_outage_never_reads_as_a_classification(tmp_vault, monkeypatch):
    fake = FakeZotero()
    note = tmp_vault / "literatures" / "alkt2026.md"
    note.write_text(
        '---\ntype: "literature"\nzotero-server-id: "6LpvURP2E933"\nzotero-item-key: "ALKT2NF7"\n'
        'zotero-item-version: 0\ncitationKey: "alkt2026"\nattachments:\nfulltext:\n---\n'
    )
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    monkeypatch.setattr(client, "_http", lambda *a, **k: (_ for _ in ()).throw(zotero.ZoteroError("down")))
    (outcome,) = lifecycle.lint_lifecycle(tmp_vault, client)
    assert outcome.result is Result.UNREACHABLE and outcome.reason.startswith("outage")


def test_verify_offline_reports_the_held_leg_as_synthetic_unreachable(fixture_vault):
    from research_vault import verify

    report, effective, _hashes, _warn = verify.verify_state(fixture_vault, network=False)
    lifecycle_rows = [o for o in report["outcomes"] if o.check == "lifecycle"]
    assert len(lifecycle_rows) == 1
    assert lifecycle_rows[0].result is Result.UNREACHABLE
    assert lifecycle_rows[0].extra.get("synthetic_offline") is True
    assert not [o for o in effective if o.check == "lifecycle"]


def test_lint_lifecycle_with_no_captured_notes_is_skipped_and_asks_nothing(tmp_vault, monkeypatch):
    fake = FakeZotero()
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    (outcome,) = lifecycle.lint_lifecycle(tmp_vault, client)
    assert outcome.result is Result.SKIPPED
    assert outcome.reason == "no-identifier — no note carries a provenance tuple"
    assert fake.calls == []  # decision 26: an empty vault does not wait on Zotero
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_lifecycle.py -q`
Expected: FAIL — `ModuleNotFoundError: research_vault.lifecycle`.

- [ ] **Step 3: Register the reason codes, then implement `research_vault/lifecycle.py`**

Add to `inbox.REASON_CODES`: `"re-keyed", "merged", "trashed", "deleted", "database-changed"`; to `CHECK_IDS`: `"lifecycle"`. Add the five rows to the skill's reason-code table (one line each, e.g. `| `re-keyed` | The item's live citation key differs from the recorded one under an unchanged item key; propagation renames. |`) and to terminology §4.4.

```python
"""The lifecycle linter: one check, one code path (ingest spec §3.4).

Three reads answer every transition: the whole versions map (children and
annotations included), the trash map, and the top-level items, which alone
carry ``citationKey`` and ``relations.dc:replaces``. Every key in a note's
tuple is compared, because Zotero versions objects independently (§9).
"""

from pathlib import Path
from typing import NamedTuple

from . import AGENT_ACTOR, fulltext, notes
from .outcome import Outcome, Result
from .zotero import DatabaseChangedError, ZoteroClient, ZoteroError

CHECK = "lifecycle"
# First transition that matches wins; merged outranks deleted and trashed
# because Zotero trashes a merge's predecessor and a later purge removes it.
ORDER = ("database-changed", "merged", "deleted", "trashed", "re-keyed", "drift")  # classify's branch order below implements this precedence; exported for the docs, never iterated


class Live(NamedTuple):
    versions: dict[str, int]
    trash: dict[str, int]
    top: dict[str, dict]  # item key -> {"citationKey": str | None, "replaces": set[str]}


def replaces_keys(relations) -> set[str]:
    """``dc:replaces`` is a Zotero URI or a list of them; the key is the last segment."""
    if relations is None:
        return set()
    values = relations if isinstance(relations, list) else [relations]
    return {str(v).rstrip("/").rsplit("/", 1)[-1] for v in values if isinstance(v, str) and v}


def read_live(client: ZoteroClient) -> Live:
    versions, _ = client.versions()
    trash = client.trash_versions()
    items, _ = client.top_items()
    top = {}
    for item in items:
        data = item.get("data", {}) if isinstance(item, dict) else {}
        key = item.get("key")
        if isinstance(key, str):
            top[key] = {
                "citationKey": data.get("citationKey"),
                "replaces": replaces_keys((data.get("relations") or {}).get("dc:replaces")),
            }
    return Live(versions, trash, top)


def _successor(item_key: str, live: Live) -> str | None:
    for key, entry in live.top.items():
        if item_key in entry["replaces"]:
            return key
    return None


def classify(provenance: notes.Provenance, live: Live) -> tuple[str, str]:
    key = provenance.item_key
    successor = _successor(key, live)
    if successor is not None:
        return "merged", successor
    if key not in live.versions:
        return ("trashed", key) if key in live.trash else ("deleted", key)
    live_key = live.top.get(key, {}).get("citationKey")
    if live_key and live_key != provenance.citation_key:
        return "re-keyed", f"{provenance.citation_key} → {live_key}"
    moved = []
    if live.versions[key] != provenance.item_version:
        moved.append(f"item {key} {provenance.item_version} → {live.versions[key]}")
    for attachment in provenance.attachments:
        att_key = attachment.get("key")
        recorded = attachment.get("version")
        if att_key in live.trash:
            return "trashed", str(att_key)
        current = live.versions.get(att_key)
        if current is None:
            moved.append(f"attachment {att_key} absent")
        elif current != recorded:
            moved.append(f"attachment {att_key} {recorded} → {current}")
    if moved:
        return "drifted", "; ".join(moved)
    return "current", ""


def _drift_detail(client: ZoteroClient, vault: Path, provenance: notes.Provenance, detail: str) -> str:
    """Name whether a moved attachment's file changed or only its metadata did (§3.4 step 5)."""
    if "attachment" not in detail:
        return detail
    live_md5 = {}
    try:
        for child in client.children(provenance.item_key):
            data = child.get("data", {})
            live_md5[child.get("key")] = data.get("md5")
    except ZoteroError:
        return detail + "; children unreadable"
    notes_out = []
    cached = {f.get("attachment-key"): f.get("sha256") for f in provenance.fulltext}
    for attachment in provenance.attachments:
        key = attachment.get("key")
        if key not in live_md5 or f"attachment {key}" not in detail:
            continue
        file_changed = live_md5[key] != attachment.get("md5")
        text_changed = False
        if key in cached:
            path = fulltext.path_for(vault, key)
            text_changed = not path.is_file() or fulltext.sha256_of(path) != cached[key]
        notes_out.append(
            f"{key}: {'file changed' if file_changed else 'metadata only'}"
            + (", cached text stale" if text_changed else "")
        )
    return detail + ("; " + "; ".join(notes_out) if notes_out else "")


def _provenances(vault: Path) -> list[tuple[Path, notes.Provenance]]:
    found = []
    for path in sorted((vault / "literatures").glob("*.md")):
        try:
            provenance = notes.read_provenance(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError):
            continue
        if provenance is not None:
            found.append((path, provenance))
    return found


def lint_lifecycle(vault_root, client: ZoteroClient, provenances=None) -> list[Outcome]:
    vault = Path(vault_root)
    pairs = provenances if provenances is not None else _provenances(vault)
    if not pairs:
        # Decision 26: nothing depends on Zotero yet, so the check does not apply; say so rather than vanish.
        return [Outcome(CHECK, "vault", Result.SKIPPED, "no-identifier — no note carries a provenance tuple")]
    recorded_ids = {p.server_id for _, p in pairs}
    client.server_id = sorted(recorded_ids)[0]
    try:
        live = read_live(client)
    except DatabaseChangedError as error:
        return [Outcome(CHECK, "vault", Result.UNMATCHED, f"database-changed — {error}; every recorded version is void")]
    except ZoteroError as error:
        return [Outcome(CHECK, "vault", Result.UNREACHABLE, f"outage — {error}")]
    outcomes = []
    for _path, provenance in pairs:
        if provenance.server_id != client.server_id:
            outcomes.append(Outcome(CHECK, provenance.citation_key, Result.UNMATCHED,
                                    f"database-changed — note records {provenance.server_id}"))
            continue
        state, detail = classify(provenance, live)
        if state == "current":
            outcomes.append(Outcome(CHECK, provenance.citation_key, Result.MATCHED, "matched"))
            continue
        code = "drift" if state == "drifted" else state
        if state == "drifted":
            detail = _drift_detail(client, vault, provenance, detail)
        outcomes.append(Outcome(CHECK, provenance.citation_key, Result.UNMATCHED, f"{code} — {detail}"))
    return outcomes
```

`research_vault/verify.py` `_plan_state`, after the `structure.check_tree` line:

```python
    if network:
        raw.extend(lifecycle.lint_lifecycle(vault, ZoteroClient(base=base)))
    else:
        raw.append(
            checks.Outcome(
                "lifecycle", "vault", Result.UNREACHABLE,
                "outage — network disabled", {"synthetic_offline": True},
            )
        )
```

(add `lifecycle` to the package import block and `from .zotero import DEFAULT_BASE, ZoteroClient`; Task 2 renamed `_plan_state`'s then-unread `base` parameter to `_base` — rename it back to `base`, it is read again here). `lifecycle` is not added to any `CLOSING_BY_SURFACE` set (decision 4).

- [ ] **Step 4: Run the suite and form owners; commit**

Run: `.venv/bin/python -m pytest tests -q -n auto && ruff format research_vault tests && ruff check research_vault tests && mypy research_vault`
Expected: PASS, clean.

```bash
git add tests/fixtures/lifecycle
git commit -m "add the lifecycle linter (ingest spec §3.4)

Three reads, every key in the tuple compared, merged before deleted and
trashed, database-changed on a 412 and nothing else. Verify runs it
online; offline it is a synthetic UNREACHABLE, never a classification.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- research_vault tests skills docs
```

### Task 13: The capture verb (spec §2 "capture runs on the returned keys", §3.3, §3.4 "run at capture", §4.4 "no text → no compile input")

**Files:**

- Create: `research_vault/capture.py`, `tests/test_capture.py`
- Modify: `research_vault/__main__.py` (`cmd_capture`, parser `capture KEY... --vault PATH [--all]`, dispatch), `research_vault/inbox.py` (`REASON_CODES` add `no-fulltext`, `unkeyed`; `CHECK_IDS` add `capture`), `skills/evidence-conventions/SKILL.md`, `docs/terminology.md` §4.4

**Interfaces:**

- Consumes: `ZoteroClient` (Task 9; including `_local_json` and `_version_header` for `items/top?format=versions`), `fulltext.verdict/write` (Task 10), `notes.render_note/read_provenance/Provenance/note_path/content_changed` (Task 11), `lifecycle.lint_lifecycle/_provenances` (Task 12), `bibliography.write` (Task 2), `stamp.stamp_types`, `okf.regenerate_log`, `__main__._hold`.

- Produces: the Interface index `research_vault/capture.py` block. `capture()` returns one `Outcome("capture", <citation key or argument>, ...)` per requested key plus one `Outcome("capture", "system/bibliography.json", ...)` for the CSL regeneration. Reasons: `matched` (wrote), `matched — NOOP` (identical projection), `not-admitted — <arg> is not in the library`, `unkeyed — item <key> has no citation key`, `no-fulltext — <verdict>` (the note is written; this is an additional UNMATCHED finding on the same target), `merged|trashed|deleted — <detail>` (nothing written), `database-changed — ...` (run aborted, nothing written), `outage — ...` (UNREACHABLE, nothing written), `schema-violation — ...`. CLI exit: 0 when every outcome is MATCHED, 1 when any is UNMATCHED, 3 when any is UNREACHABLE and none is UNMATCHED. An item with no stored attachment at all (spec §0 at `ac0cfd2`: 130 of the live library's 138 URL-shaped items carry none) gets its note and `Outcome("capture", <key>, SKIPPED, "no-fulltext — no attachment to read (<itemType>); text checks do not apply")`, and `cmd_capture` holds only `UNMATCHED` and `UNREACHABLE` outcomes — a class this iteration does not handle is not a capture failure, and a finding nothing can clear drains nothing (ADR 0002). `UNMATCHED no-fulltext` is reserved for an attachment that exists and has no usable text.

- [ ] **Step 1: Write the failing tests**

`tests/test_capture.py`:

```python
import json

import pytest

from research_vault import Result, capture, frontmatter, notes, zotero
from tests.fakes import ATTACHMENT, CHILD_NOTE, FULLTEXT, ITEM, FakeZotero, canned_item

LIBRARY = [{"id": "jakesch.etal2023a", "citation-key": "jakesch.etal2023a", "type": "paper-conference", "title": "T"}]


def _client(monkeypatch, fake):
    return fake.install(zotero.ZoteroClient(), monkeypatch)


def _canned_run(fake, items=(ITEM,)):
    fake.get("/api/users/0/items?since=0&format=versions", body={"E352DFS8": 544, "D7EJ9FTG": 551, "N0TE0001": 552}, headers={"Last-Modified-Version": "565"})
    fake.get("/api/users/0/items/trash?format=versions", body={})
    fake.get("/api/users/0/items/top?format=json", body=list(items), headers={"Last-Modified-Version": "565"})
    fake.get("/api/users/0/items/top?format=versions", body={"E352DFS8": 544}, headers={"Last-Modified-Version": "565"})
    fake.get("/better-bibtex/library?/My%20Library.json", body=LIBRARY)
    return fake


def test_capture_writes_note_text_layer_and_csl_file(tmp_vault, monkeypatch):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)

    outcomes = capture.capture(tmp_vault, client, ["jakesch.etal2023a"])

    assert [(o.target, o.result, o.reason) for o in outcomes] == [
        ("jakesch.etal2023a", Result.MATCHED, "matched"),
        ("system/bibliography.json", Result.MATCHED, "matched"),
    ]
    note = tmp_vault / "literatures" / "jakesch.etal2023a.md"
    data, body = frontmatter.parse(note.read_text())
    assert data["zotero-server-id"] == "6LpvURP2E933"
    assert data["zotero-item-version"] == 544
    assert data["attachments"][0]["version"] == 551
    text = tmp_vault / "fulltext" / "D7EJ9FTG.md"
    assert text.is_file()
    assert data["fulltext"][0]["sha256"] == data["compile-input-sha256"]
    assert json.loads((tmp_vault / "system" / "bibliography.json").read_text())[0]["id"] == "jakesch.etal2023a"
    assert (tmp_vault / "log.md").is_file()


def test_capture_accepts_an_item_key_and_resolves_a_citation_key(tmp_vault, monkeypatch):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    assert capture.resolve_keys(client, ["E352DFS8", "jakesch.etal2023a", "nobody2020"]) == {
        "E352DFS8": "E352DFS8", "jakesch.etal2023a": "E352DFS8", "nobody2020": None,
    }
    outcomes = capture.capture(tmp_vault, client, ["nobody2020"])
    assert outcomes[0].result is Result.UNMATCHED and outcomes[0].reason.startswith("not-admitted")


def test_second_run_is_a_noop_and_keeps_generated(tmp_vault, monkeypatch):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    capture.capture(tmp_vault, client, ["E352DFS8"], now=_at("2026-09-07T10:00:00Z"))
    first = (tmp_vault / "literatures" / "jakesch.etal2023a.md").read_text()
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"], now=_at("2026-09-08T10:00:00Z"))
    assert outcomes[0].reason == "matched — NOOP"
    assert (tmp_vault / "literatures" / "jakesch.etal2023a.md").read_text() == first


def _at(text):
    import datetime
    return datetime.datetime.fromisoformat(text.replace("Z", "+00:00"))


def test_refresh_after_compile_embeds_the_page_and_completes_the_note(tmp_vault, monkeypatch):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    capture.capture(tmp_vault, client, ["E352DFS8"])
    note = tmp_vault / "literatures" / "jakesch.etal2023a.md"
    assert "## Compiled" not in note.read_text()  # capture runs before compile (§3.3 step 5)
    ledger = tmp_vault / "wiki" / "meta" / "ledgers" / "source-ledger.json"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(json.dumps({"schema": "claude-obsidian.source-ledger.v1", "sources": {
        "src-1": {"origin": {"kind": "file", "locator": "fulltext/D7EJ9FTG.md"}, "pages": ["wiki/sources/Co-Writing.md"]},
    }}))
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"])
    assert outcomes[0].reason == "matched"  # the second write is what completes the note
    assert "## Compiled\n\n![[wiki/sources/Co-Writing.md]]\n\n## Item\n" in note.read_text()
    assert capture.capture(tmp_vault, client, ["E352DFS8"])[0].reason == "matched — NOOP"


def test_read_restarts_when_the_item_moves_mid_read(tmp_vault, monkeypatch):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    versions = iter([544, 545, 545, 545])
    real_item = client.item

    def moving_item(key):
        envelope = json.loads(json.dumps(real_item(key)))
        envelope["version"] = envelope["data"]["version"] = next(versions)
        return envelope

    monkeypatch.setattr(client, "item", moving_item)
    read = capture.read_item(client, "E352DFS8")
    assert read.version == 545
    assert read.item["data"]["citationKey"] == "jakesch.etal2023a"


def test_no_usable_text_writes_the_note_and_files_no_fulltext(tmp_vault, monkeypatch):
    partial = {"content": "x" * 900, "indexedPages": 100, "totalPages": 143}
    fake = _canned_run(canned_item(FakeZotero(), fulltext=partial))
    client = _client(monkeypatch, fake)
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"])
    reasons = [(o.result, o.reason) for o in outcomes if o.target == "jakesch.etal2023a"]
    assert reasons == [
        (Result.MATCHED, "matched"),
        (Result.UNMATCHED, "no-fulltext — D7EJ9FTG partial — indexedPages 100 of 143"),
    ]
    data, _ = frontmatter.parse((tmp_vault / "literatures" / "jakesch.etal2023a.md").read_text())
    assert "compile-input-sha256" not in data and data["fulltext"] == []
    assert not (tmp_vault / "fulltext").exists()


def test_url_only_item_without_attachment_is_skipped_not_a_finding(tmp_vault, monkeypatch, capsys):
    import research_vault.__main__ as cli
    from research_vault import inbox

    webpage = json.loads(json.dumps(ITEM))
    webpage["data"]["itemType"] = "webpage"
    webpage["links"] = {}
    fake = _canned_run(canned_item(FakeZotero(), item=webpage, children=()), items=(webpage,))
    client = _client(monkeypatch, fake)
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"])
    assert [(o.result, o.reason) for o in outcomes if o.target == "jakesch.etal2023a"] == [
        (Result.MATCHED, "matched"),
        (Result.SKIPPED, "no-fulltext — no attachment to read (webpage); text checks do not apply"),
    ]
    assert (tmp_vault / "literatures" / "jakesch.etal2023a.md").is_file()
    monkeypatch.setattr(cli, "ZoteroClient", lambda base=None: client)
    assert cli.main(["capture", "E352DFS8", "--vault", str(tmp_vault)]) == 0
    assert "SKIPPED jakesch.etal2023a — no-fulltext" in capsys.readouterr().out
    assert not [f for f in inbox.load(tmp_vault) if f.check == "capture"]  # nothing to clear, so nothing filed


def test_unkeyed_item_is_reported_not_written(tmp_vault, monkeypatch):
    unkeyed = json.loads(json.dumps(ITEM))
    unkeyed["data"]["citationKey"] = None
    fake = _canned_run(canned_item(FakeZotero(), item=unkeyed), items=(unkeyed,))
    client = _client(monkeypatch, fake)
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"], key_wait_seconds=0)
    assert outcomes[0].result is Result.UNMATCHED and outcomes[0].reason.startswith("unkeyed")
    assert not list((tmp_vault / "literatures").glob("*.md"))


def test_capture_runs_the_linter_first_and_refuses_a_trashed_item(tmp_vault, monkeypatch):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    capture.capture(tmp_vault, client, ["E352DFS8"])
    fake.get("/api/users/0/items?since=0&format=versions", body={"D7EJ9FTG": 551}, headers={"Last-Modified-Version": "566"})
    fake.get("/api/users/0/items/trash?format=versions", body={"E352DFS8": 566})
    before = (tmp_vault / "literatures" / "jakesch.etal2023a.md").read_text()
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"])
    assert outcomes[0].reason.startswith("trashed — ")
    assert (tmp_vault / "literatures" / "jakesch.etal2023a.md").read_text() == before


def test_database_changed_aborts_before_any_write(tmp_vault, monkeypatch):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    capture.capture(tmp_vault, client, ["E352DFS8"])
    fake.server_id = "Tdoqsn2J4q4h"
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"])
    assert [(o.target, o.result) for o in outcomes] == [("vault", Result.UNMATCHED)]
    assert outcomes[0].reason.startswith("database-changed")


def test_csl_file_falls_back_to_item_export_when_the_library_route_breaks(tmp_vault, monkeypatch):
    fake = _canned_run(canned_item(FakeZotero()))
    fake.get("/better-bibtex/library?/My%20Library.json", status=500, body=b"")
    fake.rpc("item.export", LIBRARY)
    client = _client(monkeypatch, fake)
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"])
    assert outcomes[-1].reason == "matched — item.export fallback"
    assert ("RPC", "item.export", {"params": [["jakesch.etal2023a"], "Better CSL JSON"]}) in fake.calls


def test_library_route_is_reread_once_when_zotero_moved_during_the_run(tmp_vault, monkeypatch):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    seen = iter(["565", "570"])
    original = fake._http

    def moving(url, data=None, headers=None, method=None):
        response = original(url, data, headers, method)
        if url.endswith("/items/top?format=versions"):
            return zotero.Response(response.status, response.body, {**response.headers, "Last-Modified-Version": next(seen, "570")})
        return response

    monkeypatch.setattr(client, "_http", moving)
    capture.capture(tmp_vault, client, ["E352DFS8"])
    library_reads = [c for c in fake.calls if c[1].startswith("/better-bibtex/library")]
    assert len(library_reads) == 2


def test_cli_capture_exit_codes_and_holds(tmp_vault, monkeypatch, capsys):
    import research_vault.__main__ as cli

    fake = _canned_run(canned_item(FakeZotero()))
    monkeypatch.setattr(cli, "ZoteroClient", lambda **kw: fake.install(zotero.ZoteroClient(**kw), monkeypatch))
    assert cli.main(["capture", "E352DFS8", "--vault", str(tmp_vault)]) == 0
    assert cli.main(["capture", "nobody2020", "--vault", str(tmp_vault)]) == 1
    queue = (tmp_vault / "inbox" / "review-queue.md").read_text()
    assert "[check:: capture]" in queue and "not-admitted" in queue
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_capture.py -q`
Expected: FAIL — `ModuleNotFoundError: research_vault.capture`.

- [ ] **Step 3: Register the codes, implement `research_vault/capture.py`, wire the CLI**

`inbox.REASON_CODES` add `"no-fulltext", "unkeyed"`; `CHECK_IDS` add `"capture"`; skill table rows; terminology row.

```python
"""The capture verb: the deterministic copy into the vault (ingest spec §3.3).

One verb, per item or batch, keyed by citation key or item key. Reads are
version-checked per item and restart when the item moves; the CSL file is
regenerated whole at the end of the run; NOOP is a result.
"""

import datetime
import time
from pathlib import Path
from typing import NamedTuple

from . import bibliography, fulltext, lifecycle, notes, okf, stamp
from .outcome import Outcome, Result
from .zotero import (
    ITEM_KEY,
    DatabaseChangedError,
    NotFoundError,
    ZoteroClient,
    ZoteroError,
)

CHECK = "capture"
MAX_READ_RESTARTS = 3
KEY_WAIT_SECONDS = 10
CSL_TARGET = bibliography.BIB_PATH


class ItemRead(NamedTuple):
    item: dict
    children: list[dict]
    texts: dict[str, dict | None]  # attachment key -> fulltext response
    version: int


def resolve_keys(client: ZoteroClient, keys: list[str]) -> dict[str, str | None]:
    """An 8-character upper-case key is an item key; anything else is a citation key."""
    resolved: dict[str, str | None] = {}
    by_citation: dict[str, str] | None = None
    for key in keys:
        if ITEM_KEY.match(key):
            resolved[key] = key
            continue
        if by_citation is None:
            items, _ = client.top_items()
            by_citation = {
                item["data"]["citationKey"]: item["key"]
                for item in items
                if isinstance(item.get("data"), dict) and item["data"].get("citationKey")
            }
        resolved[key] = by_citation.get(key)
    return resolved


def _stored(child) -> bool:
    data = child.get("data", {})
    return data.get("itemType") == "attachment" and data.get("linkMode") in {"imported_file", "imported_url"}


def read_item(client: ZoteroClient, item_key: str) -> ItemRead:
    """Steps 1-3 of §3.3, restarted when the item's version moves (§3.3, re-read boundary)."""
    for _attempt in range(MAX_READ_RESTARTS):
        item = client.item(item_key)
        children = client.children(item_key)
        texts = {c["key"]: client.fulltext(c["key"]) for c in children if _stored(c)}
        again = client.item(item_key)
        if again["version"] == item["version"]:
            return ItemRead(item, children, texts, int(item["version"]))
    raise ZoteroError(f"item {item_key} moved during {MAX_READ_RESTARTS} consecutive read passes")


def _wait_for_key(client: ZoteroClient, item_key: str, wait_seconds: float) -> dict:
    """Better BibTeX fills the key after ``fillKeyAfter``; poll to a ceiling (§2)."""
    deadline = time.monotonic() + wait_seconds
    while True:
        item = client.item(item_key)
        if item["data"].get("citationKey"):
            return item
        if time.monotonic() >= deadline:
            return item
        time.sleep(1)


def _attachment_tuple(child) -> dict:
    data = child.get("data", {})
    return {
        "key": child.get("key", ""),
        "version": int(child.get("version", 0)),
        "md5": data.get("md5") or "absent",
        "contentType": data.get("contentType") or "",
        "filename": data.get("filename") or "",
    }


def _best_attachment(item: dict, usable: list[str]) -> str | None:
    href = ((item.get("links") or {}).get("attachment") or {}).get("href", "")
    best = href.rstrip("/").rsplit("/", 1)[-1] if href else None
    if best in usable:
        return best
    return usable[0] if usable else None


def _write_texts(vault: Path, read: ItemRead) -> tuple[list[dict], list[str], list[str]]:
    """Returns (fulltext tuple entries, usable attachment keys, verdict reasons)."""
    entries, usable, reasons = [], [], []
    for att_key, response in read.texts.items():
        verdict = fulltext.verdict(response)
        if not verdict.usable:
            reasons.append(f"{att_key} {verdict.reason}")
            continue
        _path, digest = fulltext.write(vault, att_key, read.item["key"], response)
        entries.append({"attachment-key": att_key, "sha256": digest})
        usable.append(att_key)
    return entries, usable, reasons


def _capture_one(vault: Path, client: ZoteroClient, read: ItemRead, server_id: str, now) -> list[Outcome]:
    item = read.item
    citation_key = item["data"].get("citationKey")
    entries, usable, reasons = _write_texts(vault, read)
    best = _best_attachment(item, usable)
    digest_by_key = {e["attachment-key"]: e["sha256"] for e in entries}
    provenance = notes.Provenance(
        server_id=server_id,
        item_key=item["key"],
        item_version=read.version,
        citation_key=citation_key,
        attachments=tuple(_attachment_tuple(c) for c in read.children if c.get("data", {}).get("itemType") == "attachment"),
        fulltext=tuple(entries),
        compile_input_sha256=digest_by_key.get(best) if best else None,
    )
    path = notes.note_path(vault, citation_key)
    existing = path.read_text(encoding="utf-8", newline="") if path.is_file() else None
    child_notes = [c for c in read.children if c.get("data", {}).get("itemType") == "note"]
    candidate = notes.render_note(
        item["data"], provenance, read.children, child_notes, existing,
        accessed=now.date().isoformat(), generated_at=notes.generated_at_now(now),
        pages=notes.compiled_pages(vault, provenance),  # absent until the first compile; the refresh after it completes the note
    )
    outcomes = []
    if existing is not None and not notes.content_changed(existing, candidate):
        outcomes.append(Outcome(CHECK, citation_key, Result.MATCHED, "matched — NOOP"))
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(candidate)
        outcomes.append(Outcome(CHECK, citation_key, Result.MATCHED, "matched"))
    if not read.texts:
        # Spec §0 (ac0cfd2): a web page, a repository, a program — no stored attachment, nothing to read.
        # The fourth state, not a failure: the note is written, the text checks do not apply, nothing is filed.
        outcomes.append(Outcome(CHECK, citation_key, Result.SKIPPED,
                                f"no-fulltext — no attachment to read ({item['data'].get('itemType')}); text checks do not apply"))
    elif reasons and best is None:
        outcomes.append(Outcome(CHECK, citation_key, Result.UNMATCHED, "no-fulltext — " + "; ".join(reasons)))
    return outcomes


def _regenerate_csl(vault: Path, client: ZoteroClient, library_name: str, run_version: int | None) -> Outcome:
    """§3.3 step 4: one whole-library read, re-read once if Zotero moved, item.export fallback."""
    captured = sorted(_captured_keys(vault))
    try:
        items = client.library_csl(library_name)
        _versions, after = client.top_items_version() if hasattr(client, "top_items_version") else (None, _top_version(client))
        if run_version is not None and after is not None and after != run_version:
            items = client.library_csl(library_name)
        route = "matched"
    except ZoteroError:
        try:
            items = client.export_csl(captured) if captured else []
            route = "matched — item.export fallback"
        except ZoteroError as error:
            return Outcome(CHECK, CSL_TARGET, Result.UNREACHABLE, f"outage — CSL export unavailable: {error}")
    selected = [item for item in items if item.get("id") in captured]
    try:
        bibliography.write(vault, selected)
    except bibliography.BibliographyError as error:
        return Outcome(CHECK, CSL_TARGET, Result.UNMATCHED, f"schema-violation — {error}")
    return Outcome(CHECK, CSL_TARGET, Result.MATCHED, route)


def _top_version(client: ZoteroClient) -> int | None:
    _payload, headers = client._local_json("/api/users/0/items/top?format=versions")
    return client._version_header(headers)


def _captured_keys(vault: Path) -> set[str]:
    # Task 15 rewires this to captured.captured_set; research_vault/captured.py does not exist yet.
    return {p.citation_key for _, p in lifecycle._provenances(vault)}


def capture(vault_root, client: ZoteroClient, keys, *, now=None, refresh_all=False, key_wait_seconds=KEY_WAIT_SECONDS) -> list[Outcome]:
    vault = Path(vault_root)
    now = now or datetime.datetime.now(datetime.UTC).replace(microsecond=0)
    try:
        info = client.server_info()
    except DatabaseChangedError as error:
        # A client that still carries an earlier run's server id is refused with 412 before any read.
        return [Outcome(CHECK, "vault", Result.UNMATCHED, f"database-changed — {error}")]
    except ZoteroError as error:
        return [Outcome(CHECK, "vault", Result.UNREACHABLE, f"outage — {error}")]
    existing = lifecycle._provenances(vault)
    client.server_id = existing[0][1].server_id if existing else info["server_id"]
    requested = list(keys) + ([p.citation_key for _, p in existing] if refresh_all else [])
    # The linter runs first, through its one code path (§3.4).
    linted = lifecycle.lint_lifecycle(vault, client)
    if any(o.target == "vault" for o in linted):
        return [o for o in linted if o.target == "vault"]
    # The linter targets citation keys; capture resolves item keys. Join the two through the provenance tuples.
    item_key_of = {p.citation_key: p.item_key for _, p in existing}
    standing = {item_key_of.get(o.target, o.target): o for o in linted}
    run_version = _top_version(client)
    outcomes: list[Outcome] = []
    library_name = None
    try:
        resolved = resolve_keys(client, requested)
    except ZoteroError as error:
        return [Outcome(CHECK, "vault", Result.UNREACHABLE, f"outage — {error}")]
    for requested_key, item_key in resolved.items():
        if item_key is None:
            outcomes.append(Outcome(CHECK, requested_key, Result.UNMATCHED, f"not-admitted — {requested_key} is not in the library"))
            continue
        prior = standing.get(item_key)
        if prior is not None and prior.result is Result.UNMATCHED and prior.reason.split(" — ")[0] in {"merged", "trashed", "deleted"}:
            outcomes.append(Outcome(CHECK, requested_key, Result.UNMATCHED, prior.reason))
            continue
        try:
            read = read_item(client, item_key)
            if not read.item["data"].get("citationKey"):
                read = read._replace(item=_wait_for_key(client, item_key, key_wait_seconds))
            if not read.item["data"].get("citationKey"):
                outcomes.append(Outcome(CHECK, requested_key, Result.UNMATCHED, f"unkeyed — item {item_key} has no citation key"))
                continue
            library_name = library_name or read.item.get("library", {}).get("name") or "My Library"
            outcomes.extend(_capture_one(vault, client, read, client.server_id, now))
        except DatabaseChangedError as error:
            return outcomes + [Outcome(CHECK, "vault", Result.UNMATCHED, f"database-changed — {error}")]
        except NotFoundError:
            outcomes.append(Outcome(CHECK, requested_key, Result.UNMATCHED, f"not-admitted — {item_key} is not in the library"))
        except ZoteroError as error:
            outcomes.append(Outcome(CHECK, requested_key, Result.UNREACHABLE, f"outage — {error}"))
        except (notes.InvalidCitationKeyError, OSError) as error:
            outcomes.append(Outcome(CHECK, requested_key, Result.UNMATCHED, f"schema-violation — {error}"))
    if any(o.reason == "matched" for o in outcomes):
        stamp.stamp_types(vault)
        okf.regenerate_log(vault)
    if library_name is not None or existing:
        outcomes.append(_regenerate_csl(vault, client, library_name or "My Library", run_version))
    return outcomes
```

(Drop the `hasattr(client, "top_items_version")` guard: call `_top_version(client)` directly. `_captured_keys` is the inline provenance walk above until Task 15 rewires it to `captured.captured_set`.) In `research_vault/__main__.py`:

```python
def cmd_capture(args):
    client = ZoteroClient(base=args.base)
    outcomes = capture.capture(args.vault, client, args.keys, refresh_all=args.all)
    worst = 0
    for outcome in outcomes:
        print(f"{outcome.result.value} {outcome.target} — {outcome.reason}")
        if outcome.result in (Result.UNMATCHED, Result.UNREACHABLE):  # SKIPPED is automatic-only and never a finding
            _hold(args.vault, capture.CHECK, outcome.target, outcome.result, outcome.reason)
        if outcome.result is Result.UNMATCHED:
            worst = 1
        elif outcome.result is Result.UNREACHABLE and worst == 0:
            worst = 3
    return worst
```

parser: `capture_cmd = sub.add_parser("capture", parents=[common]); capture_cmd.add_argument("keys", nargs="*"); capture_cmd.add_argument("--vault", required=True); capture_cmd.add_argument("--all", action="store_true")`; dispatch `"capture": cmd_capture`. `_hold` on target `"vault"` and on `system/bibliography.json`: `record_finding` accepts identifier targets, so both spellings land as identifiers — acceptable.

- [ ] **Step 4: Run the suite and form owners; run one live capture; commit**

Run: `.venv/bin/python -m pytest tests -q -n auto && ruff format research_vault tests && ruff check research_vault tests && mypy research_vault`
Expected: PASS, clean. Live, against the test instance in a scratch vault:

```bash
scratch=$(mktemp -d) && .venv/bin/python -m research_vault scaffold --vault "$scratch" >/dev/null
.venv/bin/python -m research_vault capture jakesch.etal2023a --vault "$scratch" --base http://localhost:23129
head -30 "$scratch/literatures/jakesch.etal2023a.md"; ls "$scratch/fulltext"; python3 -c "import json;print(len(json.load(open('$scratch/system/bibliography.json'))))"
```

Expected: `MATCHED jakesch.etal2023a — matched`, `MATCHED system/bibliography.json — matched`, one `fulltext/D7EJ9FTG.md`, a one-entry CSL file, and `zotero-server-id: "Tdoqsn2J4q4h"` in the note.

```bash
git commit -m "add the capture verb (ingest spec §3.3)

Version-checked per-item reads that restart when the item moves, the text
layer written only for usable text, the CSL file regenerated whole from
the library route with item.export as the fallback, NOOP as a result, and
the lifecycle linter run first.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- research_vault tests skills docs
```

### Task 14: Propagation — the plan, the hash-gated apply, the applied-plan record, the residue lint (spec §3.5, decision 29, open point 12 as closed at `692b134`)

Propagation is the one mutation in this design that touches human content, so it runs the way the compile wrapper runs: compute a plan, print it, apply only against that plan's hash. The applied plan is the log (decision 01); there is no rename log.

**Files:**

- Create: `research_vault/propagate.py`, `tests/test_propagate.py`
- Modify: `research_vault/__main__.py` (`propagate --vault PATH [--map OLD=NEW ...]` plans; `propagate --vault PATH --plan FILE --approved-plan-sha256 SHA` applies), `research_vault/inbox.py` (`REASON_CODES` add `stale-key`; `CHECK_IDS` add `propagation`), `research_vault/verify.py` (`_plan_state` adds `propagate.lint_propagation(vault)` beside the lints; `CLOSING_BY_SURFACE["commit"]` and `["publish"]` add `"propagation"`), `research_vault/lints.py:109-116` (`_is_append_only_path` adds `rel.startswith(b"system/propagations/")` — a write-once record is an append-only file that never grows), `hooks/pretooluse_guard.py` (`MACHINE_SURFACE_PREFIXES = (Path("system/propagations"),)` and `_is_machine_surface` also answers `any(relative.is_relative_to(prefix) for prefix in MACHINE_SURFACE_PREFIXES)`), `research_vault/templates/vault/{markdownlintignore,prettierignore,editorconfig}` (add `/system/propagations/`; `.research-vault/` is already gitignored, so the unapplied plan is machine-local), `research_vault/templates/vault/index.md` (the `system/` bullet says "the applied propagation plans" if Task 6 left "the rename log"), `skills/evidence-conventions/SKILL.md` (the `stale-key` row), `docs/terminology.md` §4.4, `tests/test_templates.py`, `tests/test_hooks.py` (`Path("system") / "propagations" / "x.json"` joins the deny list)

**Interfaces:**

- Consumes: `lifecycle.lint_lifecycle`, `capture.capture`, `notes.note_path`, `notes.read_provenance`, `structure.is_excluded` (Task 6).

- Produces: the Interface index `research_vault/propagate.py` block. The plan file (`.research-vault/propagate/<operation id>.json`, canonical JSON: sorted keys, two-space indent, trailing newline): `{"schema": "research-vault.propagation.v1", "operation_id": "propagate-20260907T101500Z", "date": "2026-09-07", "mapping": {"old2020": "new2020"}, "item_keys": {"old2020": "E352DFS8"}, "surfaces": [{"path": "projects/brief/draft.md", "sha256": "…"}, …]}`; `plan_sha256` is the sha256 of exactly those bytes. The applied record (`system/propagations/<operation id>.json`) is the same object plus `"applied_at"` and `"approved_plan_sha256"`. Surfaces: every `*.md` under the vault except `literatures/` (renamed, then re-captured), `fulltext/`, `log/`, `log.md`, `inbox/review-queue.md`, `system/propagations/` and `structure.EXCLUDED_DIRS`, that names an old key; patterns `[@old` → `[@new` (followed by `]`, `,` or space), `[[old]]`/`[[old#`/`[[old|` → the same with `new`. `apply` recomputes the plan from the vault as it stands, with the approved plan's `operation_id` and `date`, and refuses with `Outcome("propagation", <operation id>, UNMATCHED, "mismatch — plan changed: …")` when the recomputed hash differs from `--approved-plan-sha256`; nothing is written on refusal. The residue lint reports `Outcome("propagation", <repo path>, UNMATCHED, "stale-key — names <old>, mapped to <new> by <operation id>")` per surface still naming a key an applied record mapped away, or one `MATCHED "matched"` on target `system/propagations` (SKIPPED `no-identifier — no applied propagation plan` when the directory is empty or absent; UNMATCHED `schema-violation — …` on an unreadable record).

- [ ] **Step 1: Write the failing tests**

`tests/test_propagate.py`:

```python
import hashlib
import json

from research_vault import Result, propagate
from research_vault.outcome import Outcome


def _seed(vault):
    (vault / "literatures" / "old2020.md").write_text(
        '---\ntype: "literature"\nzotero-server-id: "S"\nzotero-item-key: "E352DFS8"\n'
        'zotero-item-version: 1\ncitationKey: "old2020"\nattachments:\nfulltext:\n---\n'
    )
    (vault / "projects" / "brief").mkdir(parents=True)
    (vault / "projects" / "brief" / "draft.md").write_text(
        '---\ntype: "project"\n---\nSee [@old2020, p. 3] and [@old2020] and [[old2020]] and [[old2020#^c-1]] and [[old2020|alias]].\n'
    )
    (vault / "wiki" / "sources").mkdir(parents=True)
    (vault / "wiki" / "sources" / "A.md").write_text("---\ntype: source\n---\n[[old2020]] and [[older2020]]\n")
    (vault / "wiki" / "sources" / "B.md").write_text("---\ntype: source\n---\nnames nothing\n")


def _planned(vault, mapping={"old2020": "new2020"}):
    planned, outcomes = propagate.plan(vault, None, dict(mapping))
    assert planned is not None, outcomes
    return planned, propagate.write_plan(vault, planned), propagate.plan_sha256(planned)


def test_plan_lists_the_mapping_the_item_key_and_the_hashed_surfaces(tmp_vault):
    _seed(tmp_vault)
    planned, path, digest = _planned(tmp_vault)
    assert planned.mapping == {"old2020": "new2020"} and planned.item_keys == {"old2020": "E352DFS8"}
    assert [s.path for s in planned.surfaces] == ["projects/brief/draft.md", "wiki/sources/A.md"]
    draft = (tmp_vault / "projects" / "brief" / "draft.md").read_bytes()
    assert planned.surfaces[0].sha256 == hashlib.sha256(draft).hexdigest()
    assert path == tmp_vault / ".research-vault" / "propagate" / f"{planned.operation_id}.json"
    assert propagate.read_plan(path) == planned
    assert digest == hashlib.sha256(path.read_bytes()).hexdigest()
    assert json.loads(path.read_text())["schema"] == "research-vault.propagation.v1"


def test_plan_refuses_a_missing_note_and_never_reads_an_outage_as_nothing_to_do(tmp_vault, monkeypatch):
    planned, outcomes = propagate.plan(tmp_vault, None, {"ghost2020": "new2020"})
    assert planned is None and outcomes[0].result is Result.UNMATCHED
    assert outcomes[0].reason.startswith("schema-violation")
    monkeypatch.setattr(propagate.lifecycle, "lint_lifecycle",
                        lambda vault, client: [Outcome("lifecycle", "vault", Result.UNREACHABLE, "outage — down")])
    planned, outcomes = propagate.plan(tmp_vault, object(), None)
    assert planned is None and outcomes[0].result is Result.UNREACHABLE  # an outage is not "nothing to propagate"


def test_rewrite_surfaces_touches_every_citation_and_wikilink_shape(tmp_vault):
    _seed(tmp_vault)
    changed = propagate.rewrite_surfaces(tmp_vault, "old2020", "new2020")
    assert changed == ["projects/brief/draft.md", "wiki/sources/A.md"]
    draft = (tmp_vault / "projects" / "brief" / "draft.md").read_text()
    assert draft.endswith("See [@new2020, p. 3] and [@new2020] and [[new2020]] and [[new2020#^c-1]] and [[new2020|alias]].\n")
    assert "[[older2020]]" in (tmp_vault / "wiki" / "sources" / "A.md").read_text()


def test_apply_refuses_when_the_vault_moved_since_planning(tmp_vault):
    _seed(tmp_vault)
    _planned_, path, digest = _planned(tmp_vault)
    (tmp_vault / "wiki" / "sources" / "B.md").write_text("---\ntype: source\n---\n[[old2020]] now\n")
    (refused,) = propagate.apply(tmp_vault, None, path, digest)
    assert refused.result is Result.UNMATCHED and refused.reason.startswith("mismatch — plan changed")
    assert (tmp_vault / "literatures" / "old2020.md").is_file()
    assert not (tmp_vault / "system" / "propagations").exists()
    (wrong,) = propagate.apply(tmp_vault, None, path, "0" * 64)
    assert wrong.result is Result.UNMATCHED and wrong.reason.startswith("mismatch — approved hash")


def test_apply_renames_rewrites_recaptures_and_records_the_plan(tmp_vault, monkeypatch):
    _seed(tmp_vault)
    planned, path, digest = _planned(tmp_vault)
    calls = []
    monkeypatch.setattr(propagate.capture, "capture", lambda vault, client, keys, **kw: calls.append(list(keys)) or [])
    outcomes = propagate.apply(tmp_vault, object(), path, digest)
    assert outcomes[0].check == "propagation" and outcomes[0].result is Result.MATCHED
    assert "projects/brief/draft.md" in outcomes[0].reason
    assert (tmp_vault / "literatures" / "new2020.md").is_file()
    assert not (tmp_vault / "literatures" / "old2020.md").exists()
    assert calls == [["E352DFS8"]]
    record = json.loads((tmp_vault / "system" / "propagations" / f"{planned.operation_id}.json").read_text())
    assert record["mapping"] == {"old2020": "new2020"} and record["approved_plan_sha256"] == digest
    assert record["applied_at"] and record["surfaces"][0]["path"] == "projects/brief/draft.md"
    assert propagate.read_records(tmp_vault)[0].operation_id == planned.operation_id


def test_lint_reports_residue_and_is_quiet_when_clean(tmp_vault):
    _seed(tmp_vault)
    (skipped,) = propagate.lint_propagation(tmp_vault)
    assert skipped.result is Result.SKIPPED
    _planned_, path, digest = _planned(tmp_vault)
    propagate.apply(tmp_vault, None, path, digest)
    (clean,) = propagate.lint_propagation(tmp_vault)
    assert clean.result is Result.MATCHED
    (tmp_vault / "projects" / "brief" / "late.md").write_text("---\ntype: \"project\"\n---\n[@old2020]\n")
    (tmp_vault / "literatures" / "old2020.md").write_text("---\ntype: \"literature\"\n---\n")
    stale = propagate.lint_propagation(tmp_vault)
    assert {o.target for o in stale} == {"path-bytes:projects/brief/late.md", "path-bytes:literatures/old2020.md"}
    assert all(o.reason.startswith("stale-key — names old2020, mapped to new2020 by propagate-") for o in stale)


def test_cli_plans_then_applies_only_against_the_printed_hash(tmp_vault, monkeypatch, capsys):
    import research_vault.__main__ as cli

    _seed(tmp_vault)
    monkeypatch.setattr(propagate.capture, "capture", lambda vault, client, keys, **kw: [])
    assert cli.main(["propagate", "--vault", str(tmp_vault), "--map", "old2020=new2020"]) == 0
    line = [l for l in capsys.readouterr().out.splitlines() if l.startswith("apply with:")][0]
    words = line.split()
    path, digest = words[words.index("--plan") + 1], words[words.index("--approved-plan-sha256") + 1]
    assert cli.main(["propagate", "--vault", str(tmp_vault), "--plan", path, "--approved-plan-sha256", "0" * 64]) == 1
    assert (tmp_vault / "literatures" / "old2020.md").is_file()
    assert cli.main(["propagate", "--vault", str(tmp_vault), "--plan", path, "--approved-plan-sha256", digest]) == 0
    assert (tmp_vault / "literatures" / "new2020.md").is_file()
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_propagate.py -q`
Expected: FAIL — `ModuleNotFoundError`.

- [ ] **Step 3: Register `stale-key` and `propagation`; implement**

```python
"""Re-key propagation: the one vault-wide mutation over human content (spec §3.5).

Detection belongs to the lifecycle linter. This module computes a plan — the
mapping, the item keys behind it, every surface it will rewrite with that
surface's hash as it stands — applies only against that plan's hash, and keeps
the applied plan under system/propagations/: the record a reader follows a key
through and the residue lint's input (open point 12: the applied plan is the
log). A draft edited between plan and apply changes the hash, and the apply
refuses.
"""

import datetime
import hashlib
import json
import os
import re
from pathlib import Path
from typing import NamedTuple

from . import capture, lifecycle, notes, structure
from .outcome import Outcome, Result
from .pathcodec import RepoPath

PLAN_DIR = ".research-vault/propagate"
RECORD_DIR = "system/propagations"
CHECK = "propagation"
SCHEMA = "research-vault.propagation.v1"
_SKIP_FILES = {"log.md", "inbox/review-queue.md"}
_SKIP_DIRS = {"literatures", "fulltext", "log"}


class Surface(NamedTuple):
    path: str
    sha256: str


class Plan(NamedTuple):
    operation_id: str
    date: str
    mapping: dict[str, str]
    item_keys: dict[str, str]
    surfaces: tuple[Surface, ...]


def _patterns(old: str) -> list[tuple[re.Pattern[str], str]]:
    key = re.escape(old)
    return [
        (re.compile(rf"\[@{key}(?=[\],\s])"), "[@{new}"),
        (re.compile(rf"\[\[{key}(?=[\]#|])"), "[[{new}"),
    ]


def _names(text: str, old: str) -> bool:
    return any(pattern.search(text) for pattern, _ in _patterns(old))


def _surfaces(vault: Path):
    for path in sorted(vault.rglob("*.md")):
        relative = path.relative_to(vault).as_posix()
        parts = relative.split("/")
        if (
            structure.is_excluded(path, vault)
            or parts[0] in _SKIP_DIRS
            or relative in _SKIP_FILES
            or relative.startswith(RECORD_DIR + "/")
        ):
            continue
        yield path, relative


def _mapping_from_linter(vault: Path, client) -> tuple[dict[str, str], list[Outcome]]:
    mapping: dict[str, str] = {}
    blocking = []
    for outcome in lifecycle.lint_lifecycle(vault, client):
        if outcome.result is Result.UNREACHABLE or (outcome.target == "vault" and outcome.result is Result.UNMATCHED):
            blocking.append(outcome)
        elif outcome.result is Result.UNMATCHED and outcome.reason.startswith("re-keyed — "):
            old, new = outcome.reason[len("re-keyed — "):].split(" → ", 1)
            mapping[old] = new
    return mapping, blocking


def plan(vault_root, client, mapping: dict[str, str] | None, *, now=None) -> tuple[Plan | None, list[Outcome]]:
    """Compute one re-key pass without touching anything (spec §3.5, decision 01)."""
    vault = Path(vault_root)
    now = now or datetime.datetime.now(datetime.UTC)
    if mapping is None:
        if client is None:
            return None, [Outcome(CHECK, RECORD_DIR, Result.UNMATCHED, "schema-violation — no mapping and no Zotero client")]
        mapping, blocking = _mapping_from_linter(vault, client)
        if blocking:
            return None, blocking
    if not mapping:
        return None, [Outcome(CHECK, RECORD_DIR, Result.SKIPPED, "no-identifier — nothing to propagate")]
    outcomes: list[Outcome] = []
    item_keys: dict[str, str] = {}
    for old, new in mapping.items():
        source = vault / "literatures" / f"{old}.md"
        if not source.is_file():
            outcomes.append(Outcome(CHECK, old, Result.UNMATCHED, f"schema-violation — no note literatures/{old}.md to rename"))
            continue
        provenance = notes.read_provenance(source.read_text(encoding="utf-8"))
        if provenance is None:
            outcomes.append(Outcome(CHECK, old, Result.UNMATCHED, "schema-violation — note carries no provenance tuple"))
            continue
        try:
            notes.note_path(vault, new)
        except notes.InvalidCitationKeyError as error:
            outcomes.append(Outcome(CHECK, old, Result.UNMATCHED, f"schema-violation — {error}"))
            continue
        item_keys[old] = provenance.item_key
    if outcomes:
        return None, outcomes
    surfaces = []
    for path, relative in _surfaces(vault):
        data = path.read_bytes()
        text = data.decode("utf-8", errors="surrogateescape")
        if any(_names(text, old) for old in mapping):
            surfaces.append(Surface(relative, hashlib.sha256(data).hexdigest()))
    operation_id = "propagate-" + now.strftime("%Y%m%dT%H%M%SZ")
    return Plan(operation_id, now.date().isoformat(), dict(mapping), item_keys, tuple(surfaces)), []


def _document(plan: Plan) -> dict:
    return {
        "schema": SCHEMA,
        "operation_id": plan.operation_id,
        "date": plan.date,
        "mapping": dict(plan.mapping),
        "item_keys": dict(plan.item_keys),
        "surfaces": [surface._asdict() for surface in plan.surfaces],
    }


def _canonical(document: dict) -> str:
    return json.dumps(document, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def plan_sha256(plan: Plan) -> str:
    return hashlib.sha256(_canonical(_document(plan)).encode("utf-8")).hexdigest()


def write_plan(vault_root, plan: Plan) -> Path:
    path = Path(vault_root) / PLAN_DIR / f"{plan.operation_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_canonical(_document(plan)), encoding="utf-8")
    return path


def read_plan(path) -> Plan:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise ValueError(f"not a propagation plan: {path}")
    return Plan(
        str(data["operation_id"]), str(data["date"]), dict(data["mapping"]), dict(data["item_keys"]),
        tuple(Surface(str(s["path"]), str(s["sha256"])) for s in data["surfaces"]),
    )


def rewrite_surfaces(vault_root, old: str, new: str) -> list[str]:
    vault = Path(vault_root)
    changed = []
    for path, relative in _surfaces(vault):
        text = path.read_text(encoding="utf-8", newline="")
        rewritten = text
        for pattern, template in _patterns(old):
            rewritten = pattern.sub(template.format(new=new), rewritten)
        if rewritten != text:
            with path.open("w", encoding="utf-8", newline="") as handle:
                handle.write(rewritten)
            changed.append(relative)
    return changed


def apply(vault_root, client, plan_path, approved_sha256: str, *, now=None) -> list[Outcome]:
    """Apply a plan only if the vault still computes to the approved hash (decision 01)."""
    vault = Path(vault_root)
    now = now or datetime.datetime.now(datetime.UTC)
    try:
        approved = read_plan(plan_path)
    except (OSError, ValueError, KeyError, TypeError) as error:
        return [Outcome(CHECK, str(plan_path), Result.UNMATCHED, f"schema-violation — unreadable plan: {error}")]
    if plan_sha256(approved) != approved_sha256:
        return [Outcome(CHECK, approved.operation_id, Result.UNMATCHED, "mismatch — approved hash does not name this plan")]
    current, outcomes = plan(vault, None, approved.mapping, now=now)
    if current is None:
        return outcomes
    current = current._replace(operation_id=approved.operation_id, date=approved.date)
    if plan_sha256(current) != approved_sha256:
        return [Outcome(CHECK, approved.operation_id, Result.UNMATCHED,
                        "mismatch — plan changed: the vault moved since this plan was computed; run propagate again")]
    outcomes = []
    for old, new in approved.mapping.items():
        (vault / "literatures" / f"{old}.md").rename(notes.note_path(vault, new))
        changed = rewrite_surfaces(vault, old, new)
        recapture = capture.capture(vault, client, [approved.item_keys[old]]) if client is not None else []
        outcomes.append(Outcome(CHECK, new, Result.MATCHED, "matched — rewrote " + (", ".join(changed) or "nothing")))
        outcomes.extend(o for o in recapture if o.result is not Result.MATCHED)
    record = vault / RECORD_DIR / f"{approved.operation_id}.json"
    record.parent.mkdir(parents=True, exist_ok=True)
    document = _document(approved)
    document["applied_at"] = now.replace(microsecond=0).isoformat()
    document["approved_plan_sha256"] = approved_sha256
    record.write_text(_canonical(document), encoding="utf-8")
    return outcomes


def read_records(vault_root) -> list[Plan]:
    directory = Path(vault_root) / RECORD_DIR
    if not directory.is_dir():
        return []
    return [read_plan(path) for path in sorted(directory.glob("*.json"))]


def _stale(relative: str, old: str, new: str, operation_id: str) -> Outcome:
    return Outcome(
        CHECK, RepoPath(os.fsencode(relative)), Result.UNMATCHED,
        f"stale-key — names {old}, mapped to {new} by {operation_id}",
    )


def lint_propagation(vault_root) -> list[Outcome]:
    vault = Path(vault_root)
    try:
        records = read_records(vault)
    except (OSError, ValueError, KeyError, TypeError) as error:
        return [Outcome(CHECK, RepoPath(os.fsencode(RECORD_DIR)), Result.UNMATCHED, f"schema-violation — unreadable propagation record: {error}")]
    if not records:
        return [Outcome(CHECK, RECORD_DIR, Result.SKIPPED, "no-identifier — no applied propagation plan")]
    outcomes = []
    for record in records:
        for old, new in record.mapping.items():
            if (vault / "literatures" / f"{old}.md").is_file():
                outcomes.append(_stale(f"literatures/{old}.md", old, new, record.operation_id))
            for path, relative in _surfaces(vault):
                if _names(path.read_text(encoding="utf-8", errors="surrogateescape"), old):
                    outcomes.append(_stale(relative, old, new, record.operation_id))
    return outcomes or [Outcome(CHECK, RECORD_DIR, Result.MATCHED, "matched")]
```

(`plan(vault, None, mapping)` never touches Zotero: an explicit mapping needs no client, and `apply` recomputes with `client=None` for the same reason; the recapture inside `apply` is the only client use. The tests pass `object()` where a client is required and monkeypatch `capture.capture`, so the recapture call is observed without a Zotero. `_mapping_from_linter` returns the linter's `UNREACHABLE` and `database-changed` outcomes as blocking, so an outage is never reported as "nothing to propagate".) CLI:

```python
def cmd_propagate(args):
    if bool(args.plan) != bool(args.approved_plan_sha256):
        print("propagate: --plan and --approved-plan-sha256 go together", file=sys.stderr)
        return 2
    client = ZoteroClient(base=args.base)
    if args.plan:
        outcomes = propagate.apply(args.vault, client, args.plan, args.approved_plan_sha256)
    else:
        mapping = dict(pair.split("=", 1) for pair in args.map) if args.map else None
        planned, outcomes = propagate.plan(args.vault, client, mapping)
        if planned is not None:
            path = propagate.write_plan(args.vault, planned)
            for old, new in planned.mapping.items():
                print(f"rename {old} → {new} (item {planned.item_keys[old]})")
            for surface in planned.surfaces:
                print(f"rewrite {surface.path}")
            print(f"apply with: python3 -m research_vault propagate --vault {args.vault} --plan {path} --approved-plan-sha256 {propagate.plan_sha256(planned)}")
            return 0
    worst = 0
    for outcome in outcomes:
        print(f"{outcome.result.value} {outcome.target} — {outcome.reason}")
        if outcome.result is Result.UNMATCHED:
            _hold(args.vault, propagate.CHECK, str(outcome.target), outcome.result, outcome.reason)
            worst = 1
        elif outcome.result is Result.UNREACHABLE and worst == 0:
            worst = 3
    return worst
```

parser: `propagate_cmd = sub.add_parser("propagate", parents=[common]); propagate_cmd.add_argument("--vault", required=True); propagate_cmd.add_argument("--map", action="append", metavar="OLD=NEW"); propagate_cmd.add_argument("--plan"); propagate_cmd.add_argument("--approved-plan-sha256")`. Verify: add `raw.extend(propagate.lint_propagation(vault))` after the other lints; add `"propagation"` to the `commit` and `publish` closing sets. Lints, guard and formatter templates as listed in Files.

- [ ] **Step 4: Run the suite and form owners; commit**

Run: `.venv/bin/python -m pytest tests -q -n auto && ruff format research_vault tests hooks && ruff check research_vault tests hooks && mypy research_vault`
Expected: PASS, clean.

```bash
git commit -m "add re-key propagation as plan-and-apply with its residue lint (ingest spec §3.5)

propagate computes a plan and prints its hash; apply recomputes against
the vault as it stands and refuses if the hash moved, then renames the
note, rewrites [@key] and [[key]] surfaces, re-captures the item and
records the applied plan under system/propagations/ — the log. The lint
fails a commit while any surface still names a mapped-away key.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- research_vault tests hooks skills docs
```

### Task 15: The captured-set lint at the capture→compile seam (spec §1.1 "the captured set", §4.4)

**Files:**

- Create: `research_vault/captured.py`, `tests/test_captured.py`, `research_vault/clock.py` (the one clock a check reads — decision 28; Task 18 threads the CLI flag to it)
- Modify: `research_vault/capture.py` (`_captured_keys` reads `captured.captured_set`), `research_vault/verify.py` (`_plan_state` adds `captured.lint_captured_set(vault, as_of=detection_date)`; `CLOSING_BY_SURFACE["commit"]` and `["publish"]` add `"captured-set"`), `research_vault/inbox.py` (`REASON_CODES` add `recompile-needed`; `CHECK_IDS` add `captured-set`), `skills/evidence-conventions/SKILL.md`, `docs/terminology.md` §4.4

**Interfaces:**

- Consumes: `notes.read_provenance`, `frontmatter.parse`, `structure.is_excluded` (Task 6), `pathcodec.RepoPath`, `Outcome`/`Result`, the compile tool's ledger at `wiki/meta/ledgers/source-ledger.json` (`{"schema": "claude-obsidian.source-ledger.v1", "sources": {"src-…": {"origin": {"kind": "file", "locator": "fulltext/D7EJ9FTG.md"}, "content_sha256": "…", ...}}}`).

- Produces: the Interface index `research_vault/captured.py` block. Wikilink resolution order (the numbered rule): (1) target in the captured set → resolved; (2) a file `<target>.md` exists anywhere under the vault outside `literatures/` and `structure.EXCLUDED_DIRS` → a page link, not a key; (3) target equals a `title` or an `aliases` entry of a captured note → resolved; (4) else a finding. `[@key]` citations resolve only through (1). Structural half: every ledger record with `origin.kind == "file"` must have a locator `fulltext/<KEY>.md` whose `<KEY>` appears in some captured note's `fulltext` list, else `not-captured`; a record whose `content_sha256` differs from the `sha256` the note's `fulltext` list records for the attachment its locator names (`fulltext/<attachment key>.md`) is `recompile-needed` — the ledger hashes one text file, so the comparison is per attachment, never against the per-note `compile-input-sha256` (they coincide only for the compile-input attachment). An `active` record is also `recompile-needed — ledger <id> stale: observed <retrieved_at or ingested_at>, refresh due <refresh_due>, as of <as_of>` when the tool's own staleness predicate holds — `due is None or observed is None or observed > as_of or due < as_of`, with `observed = retrieved_at or ingested_at` and ISO instants compared by their first ten characters (spec §7 at `ac0cfd2`: the tool defines `source_is_stale` but its lint never calls it, so the vault is the only reporter, and it uses the tool's predicate so the two can never disagree about what stale means). Only `active` records are judged: the wrapper writes `unreviewed` with `refresh_due: null`, which the predicate would otherwise call stale. The vault writes no freshness field of its own (`stale_after` reconciled with `refresh_due` at `692b134`); `clock.today(as_of)` is the comparison's other operand. `clock.today(as_of=None) -> str` returns `as_of` validated as `YYYY-MM-DD`, else today's UTC date; it is the only place the package reads today's date (decision 28).

- [ ] **Step 1: Write the failing tests**

`tests/test_captured.py`:

```python
import json

from research_vault import Result, captured


def _note(vault, key, item_key, *, title=None, text_key=None, sha=None):
    lines = [
        '---', 'type: "literature"', f'title: "{title or key}"', 'aliases:', f'  - "{title or key}"',
        'zotero-server-id: "S"', f'zotero-item-key: "{item_key}"', 'zotero-item-version: 1',
        f'citationKey: "{key}"', 'attachments:', 'fulltext:',
    ]
    if text_key:
        lines.append(f'  - {{attachment-key: "{text_key}", sha256: "{sha}"}}')
        lines.append(f'compile-input-sha256: "{sha}"')
    lines += ['---', '']
    (vault / "literatures" / f"{key}.md").write_text("\n".join(lines))


def _ledger(vault, records):
    path = vault / "wiki" / "meta" / "ledgers" / "source-ledger.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"schema": "claude-obsidian.source-ledger.v1", "generated_at": "2026-09-07T00:00:00Z", "sources": records}))


def test_captured_set_is_the_recorded_keys_not_the_filenames(tmp_vault):
    _note(tmp_vault, "smith2020", "SMITH001")
    (tmp_vault / "literatures" / "renamed2020.md").write_text(
        (tmp_vault / "literatures" / "smith2020.md").read_text().replace('citationKey: "smith2020"', 'citationKey: "smith2020a"')
    )
    (tmp_vault / "literatures" / "junk.md").write_text("no frontmatter\n")
    assert captured.captured_set(tmp_vault) == {"smith2020": "SMITH001", "smith2020a": "SMITH001"}


def test_textual_half_resolves_pages_aliases_and_keys_and_reports_the_rest(tmp_vault):
    _note(tmp_vault, "smith2020", "SMITH001", title="Mortality decline")
    pages = tmp_vault / "wiki" / "sources"
    pages.mkdir(parents=True)
    (pages / "Mortality decline.md").write_text("---\ntype: source\nsources:\n  - \"[[Mortality decline]]\"\n---\n[[smith2020]] [@smith2020] [[Other page]] [[ghost2020]] [@ghost2021]\n")
    (tmp_vault / "wiki" / "Other page.md").write_text("---\ntype: concept\n---\n")
    outcomes = captured.lint_captured_set(tmp_vault)
    bad = sorted(o.reason for o in outcomes if o.result is Result.UNMATCHED)
    assert bad == [
        "not-captured — wiki/sources/Mortality decline.md cites [@ghost2021], not in the captured set",
        "not-captured — wiki/sources/Mortality decline.md links [[ghost2020]], not a page and not in the captured set",
    ]


def test_structural_half_checks_locators_and_hashes(tmp_vault):
    _note(tmp_vault, "smith2020", "SMITH001", text_key="ATT00001", sha="a" * 64)
    _ledger(tmp_vault, {
        "src-1": {"origin": {"kind": "file", "locator": "fulltext/ATT00001.md"}, "content_sha256": "a" * 64},
        "src-2": {"origin": {"kind": "file", "locator": "fulltext/ATT00002.md"}, "content_sha256": "b" * 64},
        "src-3": {"origin": {"kind": "file", "locator": "fulltext/ATT00001.md"}, "content_sha256": "c" * 64},
        "src-4": {"origin": {"kind": "url", "locator": "https://example.org/"}, "content_sha256": None},
    })
    outcomes = captured.lint_captured_set(tmp_vault)
    reasons = sorted(o.reason for o in outcomes if o.result is Result.UNMATCHED)
    assert reasons == [
        "not-captured — ledger src-2 names fulltext/ATT00002.md, which no capture wrote",
        "recompile-needed — ledger src-3 holds c" + "c" * 63 + " for fulltext/ATT00001.md; the note records a" + "a" * 63,
    ]


def test_structural_half_applies_the_tools_staleness_predicate_as_of(tmp_vault):
    _note(tmp_vault, "smith2020", "SMITH001", text_key="ATT00001", sha="a" * 64)
    active = {"origin": {"kind": "file", "locator": "fulltext/ATT00001.md"}, "content_sha256": "a" * 64,
              "review_status": "active", "retrieved_at": "2026-02-01T00:00:00Z", "refresh_due": "2026-03-01T00:00:00Z"}

    def unmatched(as_of):
        return [o.reason for o in captured.lint_captured_set(tmp_vault, as_of=as_of) if o.result is Result.UNMATCHED]

    _ledger(tmp_vault, {"src-1": active})
    assert unmatched("2026-09-07") == [
        "recompile-needed — ledger src-1 stale: observed 2026-02-01T00:00:00Z, refresh due 2026-03-01T00:00:00Z, as of 2026-09-07"
    ]
    assert unmatched("2026-02-15") == []
    assert unmatched("2026-01-15") != []  # observed after as_of is stale too: the tool's predicate, verbatim
    _ledger(tmp_vault, {"src-1": {**active, "refresh_due": None}})
    assert unmatched("2026-02-15")[0].startswith("recompile-needed — ledger src-1 stale: observed 2026-02-01T00:00:00Z, refresh due None")
    _ledger(tmp_vault, {"src-1": {**active, "review_status": "unreviewed", "refresh_due": None}})
    assert unmatched("2026-09-07") == []  # what the wrapper writes is never judged stale


def test_clock_today_takes_the_instant_or_reads_utc():
    import re

    from research_vault import clock

    assert clock.today("2026-01-02") == "2026-01-02"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", clock.today())
    try:
        clock.today("2026-13-01")
    except ValueError:
        pass
    else:
        raise AssertionError("an invalid as_of must be refused, never read as today")


def test_quiet_vault_is_matched_and_a_missing_ledger_is_skipped(tmp_vault):
    outcomes = captured.lint_captured_set(tmp_vault)
    assert [(o.target, o.result) for o in outcomes] == [("captured-set", Result.MATCHED), ("wiki/meta/ledgers/source-ledger.json", Result.SKIPPED)]
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_captured.py -q`
Expected: FAIL — `ModuleNotFoundError`.

- [ ] **Step 3: Register `recompile-needed` and `captured-set`; implement**

`research_vault/clock.py`, new and whole:

```python
"""The one clock a check reads (ingest spec §7, `verify --as-of`; decision 28).

A stamp records when something happened and may read the wall clock through a
`now=` parameter. A check decides whether something is stale and must take the
instant as an argument, or its verdict is not reproducible: a fixture recorded
in September would fail in December for no reason present in the fixture.
Every date default in the package resolves through today(); a test scans for
any other reader of today's date.
"""

import datetime


def today(as_of: str | None = None) -> str:
    """Return ``as_of`` validated as YYYY-MM-DD, else today's UTC date."""
    if as_of is None:
        return datetime.datetime.now(datetime.UTC).date().isoformat()
    try:
        return datetime.date.fromisoformat(as_of).isoformat()
    except ValueError as error:
        raise ValueError(f"--as-of must be YYYY-MM-DD, got {as_of!r}") from error
```

```python
"""The captured set, and the one lint at the capture-to-compile seam (spec §4.4).

"Captured" is a fact about this vault's evidence layer that nothing external
knows. The set is the citation keys recorded in parseable literature notes
that carry an item key (decision 8) — not the filenames.
"""

import json
import os
import re
from pathlib import Path

from . import frontmatter, notes, structure
from .outcome import Outcome, Result
from .pathcodec import RepoPath

CHECK = "captured-set"
LEDGER_PATH = notes.LEDGER_PATH
_CITATION = re.compile(r"\[@(?P<key>[A-Za-z0-9_.:-]+)")
_WIKILINK = re.compile(r"\[\[(?P<target>[^\]#|]+)")
_LOCATOR = re.compile(r"^fulltext/(?P<key>[A-Z0-9]{8})\.md$")


def _notes(vault: Path):
    for path in sorted((vault / "literatures").glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
            data, _body = frontmatter.parse(text)
        except (OSError, UnicodeError, frontmatter.FrontmatterError):
            continue
        provenance = notes.read_provenance(text)
        if provenance is not None:
            yield data, provenance


def captured_set(vault_root) -> dict[str, str]:
    return {p.citation_key: p.item_key for _data, p in _notes(Path(vault_root))}


def _aliases(vault: Path) -> set[str]:
    names = set()
    for data, _p in _notes(vault):
        title = data.get("title")
        if isinstance(title, str):
            names.add(title)
        names.update(a for a in data.get("aliases", []) if isinstance(a, str))
    return names


def _page_names(vault: Path) -> set[str]:
    names = set()
    for path in vault.rglob("*.md"):
        if structure.is_excluded(path, vault):
            continue
        if path.relative_to(vault).parts[0] == "literatures":
            continue
        names.add(path.stem)
    return names


def _textual(vault: Path, keys: set[str]) -> list[Outcome]:
    outcomes = []
    wiki = vault / "wiki"
    if not wiki.is_dir():
        return outcomes
    pages, aliases = _page_names(vault), _aliases(vault)
    for path in sorted(wiki.rglob("*.md")):
        if structure.is_excluded(path, vault):
            continue
        relative = path.relative_to(vault).as_posix()
        text = path.read_text(encoding="utf-8")  # frontmatter scanned with the body (§4.4)
        for match in _CITATION.finditer(text):
            key = match.group("key")
            if key not in keys:
                outcomes.append(Outcome(CHECK, RepoPath(os.fsencode(relative)), Result.UNMATCHED,
                                        f"not-captured — {relative} cites [@{key}], not in the captured set"))
        for match in _WIKILINK.finditer(text):
            target = match.group("target").strip()
            if target in keys or target in pages or target in aliases:
                continue
            outcomes.append(Outcome(CHECK, RepoPath(os.fsencode(relative)), Result.UNMATCHED,
                                    f"not-captured — {relative} links [[{target}]], not a page and not in the captured set"))
    return outcomes


def _structural(vault: Path, as_of=None) -> list[Outcome]:
    ledger = vault / LEDGER_PATH
    if not ledger.is_file():
        return [Outcome(CHECK, LEDGER_PATH, Result.SKIPPED, "no-identifier — no source ledger")]
    try:
        records = json.loads(ledger.read_text(encoding="utf-8")).get("sources", {})
    except (OSError, UnicodeError, ValueError, AttributeError):
        return [Outcome(CHECK, RepoPath(os.fsencode(LEDGER_PATH)), Result.UNMATCHED, "schema-violation — source ledger unreadable")]
    written = {}
    for _data, provenance in _notes(vault):
        for entry in provenance.fulltext:
            written[entry.get("attachment-key")] = (provenance.citation_key, provenance.compile_input_sha256, entry.get("sha256"))
    outcomes = []
    for source_id, record in sorted(records.items()):
        origin = record.get("origin", {}) if isinstance(record, dict) else {}
        if origin.get("kind") != "file":
            continue
        locator = str(origin.get("locator", ""))
        match = _LOCATOR.match(locator)
        if match is None or match.group("key") not in written:
            outcomes.append(Outcome(CHECK, RepoPath(os.fsencode(LEDGER_PATH)), Result.UNMATCHED,
                                    f"not-captured — ledger {source_id} names {locator}, which no capture wrote"))
            continue
        _key, _compile_sha, text_sha = written[match.group("key")]
        recorded = record.get("content_sha256")
        if recorded and text_sha and recorded != text_sha:
            outcomes.append(Outcome(CHECK, RepoPath(os.fsencode(LEDGER_PATH)), Result.UNMATCHED,
                                    f"recompile-needed — ledger {source_id} holds {recorded} for {locator}; the note records {text_sha}"))
        if record.get("review_status") == "active":
            # The tool's own predicate (ledgers.py source_is_stale), so the two never disagree about "stale";
            # its lint never calls it, so this is the only reporter (spec §7 at ac0cfd2).
            due = record.get("refresh_due")
            observed = record.get("retrieved_at") or record.get("ingested_at")
            instant = clock.today(as_of)
            stale = (
                not isinstance(due, str) or not isinstance(observed, str)
                or observed[:10] > instant or due[:10] < instant
            )
            if stale:
                outcomes.append(Outcome(CHECK, RepoPath(os.fsencode(LEDGER_PATH)), Result.UNMATCHED,
                                        f"recompile-needed — ledger {source_id} stale: observed {observed}, refresh due {due}, as of {instant}"))
    return outcomes


def lint_captured_set(vault_root, as_of=None) -> list[Outcome]:
    vault = Path(vault_root)
    keys = set(captured_set(vault))
    outcomes = _textual(vault, keys)
    structural = _structural(vault, as_of)
    if not outcomes:
        outcomes.append(Outcome(CHECK, CHECK, Result.MATCHED, "matched"))
    return outcomes + structural
```

Add `clock` to `captured.py`'s `from . import …` line. Wire verify (`raw.extend(captured.lint_captured_set(vault, as_of=detection_date))`; closing on `commit` and `publish`), and `capture._captured_keys` → `set(captured.captured_set(vault))`.

- [ ] **Step 4: Run the suite and form owners; commit**

Run: `.venv/bin/python -m pytest tests -q -n auto && ruff format research_vault tests && ruff check research_vault tests && mypy research_vault`
Expected: PASS, clean.

```bash
git commit -m "add the captured-set lint at the capture-to-compile seam (ingest spec §4.4)

A compiled page may cite only a source capture wrote: [@key] and [[key]]
under wiki/ resolve to the captured set, ledger locators name files
capture wrote, and a stale ledger hash reports recompile-needed.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- research_vault tests skills docs
```

______________________________________________________________________

## Phase 2 — setup and adding

### Task 16: Doctor as setup's linter (spec §5, decomposition decision 17, §6.1)

**Files:**

- Create: `research_vault/addons.py`, `research_vault/templates/zotero-addons.md`, `tests/test_addons.py`
- Modify: `research_vault/scaffold.py` (`doctor` rewrite; new probe helpers), `research_vault/__main__.py` (`DOCTOR_*` sets), `research_vault/templates/research-vault/machine.json.example` (`zotero_profile`, `claude_obsidian_root` keys, canonical JSON), `README.md` (embed the add-on table under a `## Zotero add-ons` heading, verbatim from the template), `tests/test_doctor.py` (rewrite: probe names, sets, the profile-dir fixture), `tests/test_templates.py` (README ↔ template parity), `docs/terminology.md` §4.4 (the `doctor probe ids` row becomes decision 06's thirteen ids; `tests/test_config_validity.py::test_every_doctor_probe_id_at_head_is_governed` asserts that row in both directions, so the suite fails without it)

**Interfaces:**

- Consumes: `ZoteroClient.server_info/ready/file_view_url/_http/_local_json`, `paths.to_local`, `paths.load_machine_config`.
- Produces: `addons.declared() -> list[Addon]`; `addons.observe(profile_dir) -> dict[str, dict]`; `addons.read_prefs(profile_dir) -> dict[str, str | bool | int]` (parses `user_pref("name", value);` lines of `prefs.js`); `scaffold.doctor(vault_root, client=None) -> list[Probe]` with probes in this order and these semantics:

| Probe                | MATCHED                                                                                                                                                                     | UNMATCHED                                                                                  | UNREACHABLE                                                   | SKIPPED             |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------- | ------------------- |
| `tree`               | unchanged                                                                                                                                                                   | unchanged                                                                                  | —                                                             | —                   |
| `machine-config`     | unchanged                                                                                                                                                                   | unchanged                                                                                  | —                                                             | —                   |
| `zotero`             | `server_info()` answered; reason `zotero=10.0.1 api=3 schema=44 server_id=…`                                                                                                | 403: `local API preference is off — enable it in Settings, Advanced`                       | any other failure                                             | —                   |
| `write-guard`        | a `POST /api/users/0/items` with body `[]` and header `Zotero-Server-ID: research-vault-wrong-id` answered 412                                                              | 428 or any other status (guard not armed)                                                  | transport failure                                             | zotero unreachable  |
| `fulltext-sync`      | prefs readable; reason `sync.fulltext.enabled=false storage.protocol=webdav` (report, never a failure)                                                                      | —                                                                                          | —                                                             | no `zotero_profile` |
| `bbt`                | `ready()` answered (asked regardless of the `zotero` probe: the json-rpc route ignores the local-API preference, §9)                                                        | version missing                                                                            | json-rpc transport failure                                    | —                   |
| `bbt-git`            | pref `extensions.zotero.translators.better-bibtex.git` is `off` or unset                                                                                                    | `config` or `always` (warn-only)                                                           | —                                                             | no `zotero_profile` |
| `plugins`            | every `required` add-on is `active` and not `appDisabled`, and every declared auto pref is `true`                                                                           | a required add-on missing/inactive/`appDisabled`, or an auto pref false; reason names each | —                                                             | no `zotero_profile` |
| `path-shim`          | the first `imported_file` row of `items?itemType=attachment&limit=50` (filtered client-side) has its `/file/view/url` resolved through `paths.to_local` to an existing file | resolved path does not exist                                                               | zotero unreachable or no stored attachment among the first 50 | not running in WSL  |
| `translator-formats` | `GET /api/users/0/items/top?format=csljson&limit=1` returns 500 (the closed route stays closed)                                                                             | it returns 200 — "a route this design closed has reopened" (warn-only)                     | transport failure                                             | zotero unreachable  |
| `compile-tool`       | `installed_plugins.json` names `claude-obsidian@agricidaniel-claude-obsidian` with `gitCommitSha` starting `ad67087`                                                        | installed at another sha (warn-only, reason carries both)                                  | —                                                             | not installed       |
| `remote`, `backup`   | unchanged                                                                                                                                                                   | unchanged                                                                                  | —                                                             | —                   |

`__main__.DOCTOR_HARD_UNMATCHED = {"tree", "machine-config", "zotero", "bbt", "write-guard", "plugins"}`, `DOCTOR_HARD_UNREACHABLE = {"zotero", "bbt"}`, `DOCTOR_WARN_ONLY = {"remote", "backup", "bbt-git", "translator-formats", "compile-tool", "fulltext-sync", "path-shim"}`.

- [ ] **Step 1: Write the declaration and the failing tests**

`research_vault/templates/zotero-addons.md`:

```markdown
| Add-on | Add-on id | Need | Automatic-mode preference |
| --- | --- | --- | --- |
| Better BibTeX | `better-bibtex@iris-advies.com` | required | |
| Attachment Scanner | `attachmentscanner@changlab.um.edu.mo` | recommended | |
| DOI Manager | `zoteroshortdoi@wiernik.org` | recommended | `extensions.shortdoi.autoretrieve` |
| PMCID fetcher | `zotero-pmcid-fetcher@iris-advies.com` | recommended | `extensions.zotero.pmcid.auto` |
| MarkDB-Connect | `daeda@mit.edu` | optional | |
```

`tests/test_addons.py`:

```python
import json

from research_vault import addons


def test_declared_parses_the_packaged_table():
    rows = addons.declared()
    assert rows[0] == addons.Addon("Better BibTeX", "better-bibtex@iris-advies.com", "required", None)
    assert any(r.addon_id == "zoteroshortdoi@wiernik.org" and r.auto_pref == "extensions.shortdoi.autoretrieve" for r in rows)
    assert {r.need for r in rows} <= {"required", "recommended", "optional"}


def test_observe_reads_active_and_app_disabled_from_the_running_profile(tmp_path):
    (tmp_path / "extensions.json").write_text(json.dumps({"addons": [
        {"id": "better-bibtex@iris-advies.com", "type": "extension", "location": "app-profile",
         "version": "9.0.63", "active": True, "appDisabled": False, "userDisabled": False},
        {"id": "zoteroshortdoi@wiernik.org", "type": "extension", "location": "app-profile",
         "version": "1.6.0", "active": False, "appDisabled": True, "userDisabled": False},
        {"id": "something@app", "type": "extension", "location": "app-global", "version": "1"},
    ]}))
    observed = addons.observe(tmp_path)
    assert observed["better-bibtex@iris-advies.com"] == {"version": "9.0.63", "active": True, "appDisabled": False}
    assert observed["zoteroshortdoi@wiernik.org"]["appDisabled"] is True
    assert "something@app" not in observed


def test_read_prefs_parses_user_pref_lines(tmp_path):
    (tmp_path / "prefs.js").write_text(
        'user_pref("extensions.zotero.sync.fulltext.enabled", false);\n'
        'user_pref("extensions.zotero.sync.storage.protocol", "webdav");\n'
        'user_pref("extensions.zotero.pmcid.auto", true);\n'
        'user_pref("extensions.zotero.httpServer.port", 23129);\n'
    )
    prefs = addons.read_prefs(tmp_path)
    assert prefs == {
        "extensions.zotero.sync.fulltext.enabled": False,
        "extensions.zotero.sync.storage.protocol": "webdav",
        "extensions.zotero.pmcid.auto": True,
        "extensions.zotero.httpServer.port": 23129,
    }
```

In `tests/test_doctor.py` replace the header lists with

```python
PROBE_NAMES = ["tree", "machine-config", "zotero", "write-guard", "fulltext-sync", "bbt", "bbt-git",
               "plugins", "path-shim", "translator-formats", "compile-tool", "remote", "backup"]
HARD_UNMATCHED = ["tree", "machine-config", "zotero", "bbt", "write-guard", "plugins"]
HARD_UNREACHABLE = ["zotero", "bbt"]
WARN_ONLY = ["remote", "backup", "bbt-git", "translator-formats", "compile-tool", "fulltext-sync", "path-shim"]
```

and add:

```python
def _profile(tmp_path, *, doi_auto=True):
    profile = tmp_path / "profile"
    profile.mkdir()
    (profile / "extensions.json").write_text(json.dumps({"addons": [
        {"id": "better-bibtex@iris-advies.com", "type": "extension", "location": "app-profile", "version": "9.0.63", "active": True, "appDisabled": False},
        {"id": "zoteroshortdoi@wiernik.org", "type": "extension", "location": "app-profile", "version": "1.6.0", "active": False, "appDisabled": True},
    ]}))
    (profile / "prefs.js").write_text(
        'user_pref("extensions.zotero.sync.fulltext.enabled", false);\n'
        'user_pref("extensions.zotero.sync.storage.protocol", "webdav");\n'
        f'user_pref("extensions.shortdoi.autoretrieve", {str(doi_auto).lower()});\n'
        'user_pref("extensions.zotero.pmcid.auto", true);\n'
    )
    return profile


def _doctor_fake(monkeypatch, tmp_path):
    from tests.fakes import FakeZotero

    fake = FakeZotero()
    fake.rpc("api.ready", {"zotero": "10.0.1", "betterbibtex": "9.0.63"})
    fake.post("/api/users/0/items", status=401, body=b"")  # wrong id is intercepted before this
    fake.get("/api/users/0/items/top?format=csljson&limit=1", status=500, body=b"")
    fake.get("/api/users/0/items?itemType=attachment&limit=50&format=json",
             body=[{"key": "Q1W2E3R4", "data": {"linkMode": "imported_url"}},   # skipped: not a stored file
                   {"key": "D7EJ9FTG", "data": {"linkMode": "imported_file"}}])
    fake.get("/api/users/0/items/D7EJ9FTG/file/view/url", body=b"file:///D:/Zotero/storage/D7EJ9FTG/a.pdf")
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    return fake, client


def test_doctor_reports_the_thirteen_probes_in_order(tmp_vault, tmp_path, monkeypatch):
    profile = _profile(tmp_path)
    vault = _doctor_vault(tmp_vault)  # the existing helper writes machine.json; extend it to accept extra keys
    (vault / ".research-vault" / "machine.json").write_text(json.dumps({
        "mailto": "eran@example.edu", "zotero_profile": str(profile), "path_map": {"D:\\Zotero\\": str(tmp_path) + "/"},
    }))
    (tmp_path / "storage" / "D7EJ9FTG").mkdir(parents=True)
    (tmp_path / "storage" / "D7EJ9FTG" / "a.pdf").write_bytes(b"%PDF")
    _fake, client = _doctor_fake(monkeypatch, tmp_path)
    monkeypatch.setattr(scaffold, "_installed_plugins", lambda: {"claude-obsidian@agricidaniel-claude-obsidian": [{"gitCommitSha": "ad67087cad22", "installPath": "/x"}]})
    monkeypatch.setattr(scaffold.paths, "_running_in_wsl", lambda: True)

    probes = scaffold.doctor(vault, client=client)

    assert [p.check for p in probes] == PROBE_NAMES
    by = {p.check: p for p in probes}
    assert by["zotero"].result is Result.MATCHED and "server_id=6LpvURP2E933" in by["zotero"].reason
    assert by["write-guard"].result is Result.MATCHED
    assert by["fulltext-sync"].reason == "sync.fulltext.enabled=False storage.protocol=webdav"
    assert by["bbt-git"].result is Result.MATCHED
    assert by["plugins"].result is Result.MATCHED  # DOI Manager is recommended, not required
    assert "zoteroshortdoi@wiernik.org appDisabled" in by["plugins"].reason
    assert by["path-shim"].result is Result.MATCHED
    assert by["translator-formats"].result is Result.MATCHED
    assert by["compile-tool"].result is Result.MATCHED


def test_doctor_distinguishes_local_api_off_from_zotero_down(tmp_vault, monkeypatch):
    from tests.fakes import FakeZotero

    vault = _doctor_vault(tmp_vault)
    fake = FakeZotero()
    fake.get("/api/", status=403, body=b"")
    fake.rpc("api.ready", {"zotero": "10.0.1", "betterbibtex": "9.0.63"})
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    by = {p.check: p for p in scaffold.doctor(vault, client=client)}
    assert by["zotero"].result is Result.UNMATCHED and "preference" in by["zotero"].reason
    assert by["write-guard"].result is Result.SKIPPED
    assert by["bbt"].result is Result.MATCHED  # the json-rpc route answers with the preference off


def test_doctor_write_guard_fails_when_the_wrong_id_is_not_refused(tmp_vault, tmp_path, monkeypatch):
    from tests.fakes import FakeZotero

    vault = _doctor_vault(tmp_vault)
    fake = FakeZotero()
    fake.rpc("api.ready", {"zotero": "10.0.1", "betterbibtex": "9.0.63"})
    monkeypatch.setattr(fake, "server_id", "research-vault-wrong-id")  # the server "accepts" the wrong id
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    by = {p.check: p for p in scaffold.doctor(vault, client=client)}
    assert by["write-guard"].result is Result.UNMATCHED


def test_doctor_without_a_profile_skips_rather_than_passes(tmp_vault, tmp_path, monkeypatch):
    vault = _doctor_vault(tmp_vault)
    _fake, client = _doctor_fake(monkeypatch, tmp_path)
    by = {p.check: p for p in scaffold.doctor(vault, client=client)}
    assert by["fulltext-sync"].result is Result.SKIPPED
    assert by["plugins"].result is Result.SKIPPED
    assert by["bbt-git"].result is Result.SKIPPED
```

Append to `tests/test_templates.py`:

```python
def test_readme_embeds_the_addon_declaration_verbatim():
    table = asset("zotero-addons.md").read_text()
    assert table.strip() in (REPO / "README.md").read_text()
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_addons.py tests/test_doctor.py tests/test_templates.py -q`
Expected: FAIL — `research_vault.addons` missing; eight/six probes.

- [ ] **Step 3: Implement `addons.py` and the new doctor**

```python
"""The Zotero add-on declaration doctor reads (decomposition decision 17, §6.1)."""

import json
import re
from importlib import resources
from pathlib import Path
from typing import NamedTuple

_ROW = re.compile(r"^\|\s*(?P<name>[^|]+?)\s*\|\s*`(?P<id>[^`]+)`\s*\|\s*(?P<need>required|recommended|optional)\s*\|\s*(?:`(?P<pref>[^`]+)`)?\s*\|$")
_PREF = re.compile(r'^user_pref\("(?P<name>[^"]+)",\s*(?P<value>.+)\);$')


class Addon(NamedTuple):
    name: str
    addon_id: str
    need: str
    auto_pref: str | None


def declared() -> list[Addon]:
    text = resources.files("research_vault").joinpath("templates/zotero-addons.md").read_text(encoding="utf-8")
    rows = []
    for line in text.splitlines():
        match = _ROW.match(line.strip())
        if match:
            rows.append(Addon(match.group("name"), match.group("id"), match.group("need"), match.group("pref")))
    return rows


def observe(profile_dir: Path) -> dict[str, dict]:
    """`active` and `appDisabled` from the running Zotero's extensions.json — never the manifest cap."""
    data = json.loads((Path(profile_dir) / "extensions.json").read_text(encoding="utf-8"))
    observed = {}
    for addon in data.get("addons", []):
        if addon.get("type") != "extension" or addon.get("location") != "app-profile":
            continue
        observed[addon["id"]] = {
            "version": addon.get("version"),
            "active": bool(addon.get("active")),
            "appDisabled": bool(addon.get("appDisabled")),
        }
    return observed


def read_prefs(profile_dir: Path) -> dict[str, str | bool | int]:
    prefs: dict[str, str | bool | int] = {}
    for line in (Path(profile_dir) / "prefs.js").read_text(encoding="utf-8").splitlines():
        match = _PREF.match(line.strip())
        if not match:
            continue
        raw = match.group("value").strip()
        value: str | bool | int
        if raw in {"true", "false"}:
            value = raw == "true"
        elif raw.lstrip("-").isdigit():
            value = int(raw)
        else:
            value = json.loads(raw) if raw.startswith('"') else raw
        prefs[match.group("name")] = value
    return prefs
```

`research_vault/scaffold.py` — replace `doctor` with the thirteen-probe version. The shape (each helper returns one `Probe`; the whole function is a fixed-order list):

```python
_WRONG_ID = "research-vault-wrong-id"
_COMPILE_PLUGIN = "claude-obsidian@agricidaniel-claude-obsidian"
_COMPILE_PIN = "ad67087"


def _installed_plugins() -> dict:
    path = Path.home() / ".claude" / "plugins" / "installed_plugins.json"
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("plugins", {})
    except (OSError, UnicodeError, ValueError, AttributeError):
        return {}


def _zotero_probe(client) -> tuple[Probe, dict | None]:
    try:
        info = client.server_info()
    except LocalApiDisabledError:
        return Probe("zotero", Result.UNMATCHED, "local API preference is off — enable it in Settings, Advanced"), None
    except (ZoteroError, OSError, UnicodeError, ValueError) as error:
        return Probe("zotero", Result.UNREACHABLE, str(error)), None
    return Probe("zotero", Result.MATCHED, " ".join(f"{k}={v}" for k, v in info.items())), info


def _write_guard_probe(client, info) -> Probe:
    if info is None:
        return Probe("write-guard", Result.SKIPPED, "zotero unreachable")
    try:
        response = client._http(
            f"{client.base}/api/users/0/items", data=b"[]",
            headers={"Zotero-Server-ID": _WRONG_ID, "Content-Type": "application/json"}, method="POST",
        )
    except ZoteroError as error:
        return Probe("write-guard", Result.UNREACHABLE, str(error))
    if response.status == 412:
        return Probe("write-guard", Result.MATCHED, "a wrong server id is refused before any key (412)")
    return Probe("write-guard", Result.UNMATCHED, f"wrong server id answered {response.status}, not 412 — the guard is not armed")


def _profile_dir(config) -> Path | None:
    value = config.get("zotero_profile")
    return Path(value) if isinstance(value, str) and value.strip() and Path(value).is_dir() else None


def _fulltext_sync_probe(prefs) -> Probe:
    if prefs is None:
        return Probe("fulltext-sync", Result.SKIPPED, "zotero_profile not configured")
    return Probe("fulltext-sync", Result.MATCHED,
                 f"sync.fulltext.enabled={prefs.get('extensions.zotero.sync.fulltext.enabled', False)} "
                 f"storage.protocol={prefs.get('extensions.zotero.sync.storage.protocol', 'zotero')}")


def _bbt_git_probe(prefs) -> Probe:
    if prefs is None:
        return Probe("bbt-git", Result.SKIPPED, "zotero_profile not configured")
    value = prefs.get("extensions.zotero.translators.better-bibtex.git", "off")
    if value == "off":
        return Probe("bbt-git", Result.MATCHED, "git=off")
    return Probe("bbt-git", Result.UNMATCHED, f"git={value} — Better BibTeX may run git inside an export target")


def _plugins_probe(profile, prefs) -> Probe:
    if profile is None or prefs is None:
        return Probe("plugins", Result.SKIPPED, "zotero_profile not configured")
    try:
        observed = addons.observe(profile)
    except (OSError, UnicodeError, ValueError, KeyError) as error:
        return Probe("plugins", Result.UNREACHABLE, f"extensions.json unreadable: {error}")
    failures, notes_out = [], []
    for addon in addons.declared():
        seen = observed.get(addon.addon_id)
        state = ("missing" if seen is None else "appDisabled" if seen["appDisabled"] else "inactive" if not seen["active"] else "active")
        notes_out.append(f"{addon.addon_id} {state}")
        if addon.need == "required" and state != "active":
            failures.append(f"{addon.name} {state}")
        if addon.auto_pref and state == "active" and prefs.get(addon.auto_pref) is not True:
            failures.append(f"{addon.name} automatic mode off ({addon.auto_pref})")
    result = Result.UNMATCHED if failures else Result.MATCHED
    return Probe("plugins", result, "; ".join(failures) if failures else "; ".join(notes_out))


def _path_shim_probe(client, info, vault) -> Probe:
    if not paths._running_in_wsl():
        return Probe("path-shim", Result.SKIPPED, "not running in WSL")
    if info is None:
        return Probe("path-shim", Result.SKIPPED, "zotero unreachable")
    try:
        # Measured 2026-09-07: the local API ignores a `linkMode` query filter (it answered `imported_url`
        # rows for `linkMode=imported_file`), so fetch attachments and filter client-side.
        payload, _ = client._local_json("/api/users/0/items?itemType=attachment&limit=50&format=json")
        stored = [row for row in payload if isinstance(row, dict) and row.get("data", {}).get("linkMode") == "imported_file"]
        key = stored[0]["key"] if stored else None
        url = client.file_view_url(key) if key else None
    except (ZoteroError, KeyError, IndexError, TypeError) as error:
        return Probe("path-shim", Result.UNREACHABLE, f"no stored attachment to resolve: {error}")
    if not url:
        return Probe("path-shim", Result.UNREACHABLE, "no stored attachment to resolve")
    windows_path = urllib.parse.unquote(url.removeprefix("file:///")).replace("/", "\\")
    try:
        local = paths.to_local(windows_path, vault)
    except paths.PathError as error:
        return Probe("path-shim", Result.UNMATCHED, str(error))
    return Probe("path-shim", Result.MATCHED if local.is_file() else Result.UNMATCHED, str(local))


def _translator_formats_probe(client, info) -> Probe:
    if info is None:
        return Probe("translator-formats", Result.SKIPPED, "zotero unreachable")
    try:
        response = client._http(f"{client.base}/api/users/0/items/top?format=csljson&limit=1")
    except ZoteroError as error:
        return Probe("translator-formats", Result.UNREACHABLE, str(error))
    if response.status == 500:
        return Probe("translator-formats", Result.MATCHED, "translator formats still answer 500 (closed route)")
    return Probe("translator-formats", Result.UNMATCHED, f"format=csljson answered {response.status} — a route this design closed has reopened")


def _compile_tool_probe() -> Probe:
    records = _installed_plugins().get(_COMPILE_PLUGIN) or []
    if not records:
        return Probe("compile-tool", Result.SKIPPED, f"{_COMPILE_PLUGIN} not installed")
    sha = str(records[0].get("gitCommitSha", ""))
    if sha.startswith(_COMPILE_PIN):
        return Probe("compile-tool", Result.MATCHED, f"{_COMPILE_PLUGIN} at {sha[:7]}")
    return Probe("compile-tool", Result.UNMATCHED, f"{_COMPILE_PLUGIN} at {sha[:7]}, pin is {_COMPILE_PIN}")


def _bbt_probe(client) -> Probe:
    """Independent of the local-API preference: `/better-bibtex/json-rpc` answers with it off (§9)."""
    try:
        versions = client.ready()
        if not isinstance(versions, dict):
            raise ZoteroError("malformed api.ready result: expected an object")
    except (ZoteroError, OSError, UnicodeError, ValueError) as error:
        return Probe("bbt", Result.UNREACHABLE, f"zotero down: {error}")
    bbt_version = versions.get("betterbibtex")
    if not isinstance(bbt_version, str) or not bbt_version.strip():
        return Probe("bbt", Result.UNMATCHED, "Better BibTeX version missing")
    return Probe("bbt", Result.MATCHED, bbt_version.strip())


def doctor(vault_root, client=None) -> list[Probe]:
    """Repair the scoped vault substrate and return its thirteen ordered probes (§5)."""
    vault = Path(vault_root)
    tree = _tree_probe(vault)  # the existing try/except around scaffold_vault, extracted
    config, machine = _machine_config(vault)
    client = ZoteroClient() if client is None else client
    zotero_probe, info = _zotero_probe(client)
    profile = _profile_dir(config)
    prefs = None
    if profile is not None:
        try:
            prefs = addons.read_prefs(profile)
        except (OSError, UnicodeError, ValueError):
            prefs = None
    bbt = _bbt_probe(client)  # never gated on `info`: the json-rpc route ignores the local-API preference
    return [
        tree, machine, zotero_probe, _write_guard_probe(client, info), _fulltext_sync_probe(prefs),
        bbt, _bbt_git_probe(prefs), _plugins_probe(profile, prefs), _path_shim_probe(client, info, vault),
        _translator_formats_probe(client, info), _compile_tool_probe(), _remote_probe(vault), _backup_probe(config),
    ]
```

(Imports: `import urllib.parse`, `from . import addons, paths`, `from .zotero import LocalApiDisabledError, ZoteroClient, ZoteroError`.) `research_vault/__main__.py` sets the three `DOCTOR_*` sets per the Interfaces block. `README.md` gains, before `## Development`:

```markdown
## Zotero add-ons

Installing a Zotero add-on is a human step in the setup wizard. Doctor reads this same table (packaged as `research_vault/templates/zotero-addons.md`) and reports each row's `active`/`appDisabled` state from the running profile, plus whether its automatic mode is on.

<the table, verbatim>
```

`machine.json.example` adds `"zotero_profile": ""` and `"claude_obsidian_root": ""` (run `python -m json.tool --indent 2 --no-ensure-ascii` on it).

`docs/terminology.md` §4.4, the `doctor probe ids` row, verbatim:

```markdown
| doctor probe ids | `tree`, `machine-config`, `zotero`, `write-guard`, `fulltext-sync`, `bbt`, `bbt-git`, `plugins`, `path-shim`, `translator-formats`, `compile-tool`, `remote`, `backup`
```

(keep the row's remaining cells as they are. Task 2 already dropped `autoexport` and `staleness` from this row when it deleted the probes; this task replaces the six-id row with the thirteen-id one. `tests/test_config_validity.py::test_every_doctor_probe_id_at_head_is_governed` checks the row against the probes `scaffold.py` emits at head in both directions — the check-id and reason-code tests check one direction only, registry entry without a row — so this is the one task where the suite itself fails without the row edit.)

- [ ] **Step 4: Run the suite and form owners; run doctor live; commit**

Run: `.venv/bin/python -m pytest tests -q -n auto && ruff format research_vault tests && ruff check research_vault tests && mypy research_vault && mdformat --number --wrap keep docs/terminology.md`
Expected: PASS, clean. Live, on a scratch vault whose `machine.json` names this machine's profile (`/mnt/c/Users/eranr/AppData/Roaming/Zotero/Zotero/Profiles/881hrcxd.default`): `.venv/bin/python -m research_vault doctor --vault "$scratch"` prints thirteen rows; expected today: `write-guard` MATCHED, `plugins` MATCHED with `zoteroshortdoi@wiernik.org appDisabled` in the reason, `translator-formats` MATCHED, `compile-tool` SKIPPED until Part B Task 1 installs the tool.

```bash
git commit -m "rewrite doctor as setup's linter (ingest spec §5)

One GET /api/ for four facts, 403 distinguished from down, the write
guard proved with a deliberately wrong id, profile facts from
zotero_profile, add-ons from the packaged declaration README embeds.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- research_vault tests README.md docs/terminology.md
```

### Task 17: The `add` verb — Path A create, then capture (spec §2)

**Files:**

- Create: `tests/test_add.py`
- Modify: `research_vault/capture.py` (`add(vault_root, client, items, *, collection=None, now=None) -> list[Outcome]`; `KEY_STORE = ".research-vault/zotero-keys.json"`), `research_vault/__main__.py` (`add --vault PATH --item FILE [--collection KEY]`), `tests/fakes.py` (`FakeZotero._http` records `self._last_post_body = data` on every POST)

**Interfaces:**

- Consumes: `ZoteroClient.authorize/create_items/server_info`, `zotero.DatabaseChangedError`, `capture.capture`, `lifecycle._provenances`, `notes.SNAPSHOT_FIELDS`.

- Produces: `capture.add(...)`: validates each item (object; `itemType` a non-empty string; every other key in `SNAPSHOT_FIELDS` or `collections`; `creators`/`tags` lists), sets `client.server_id` to the recorded id when any note exists (so a wrong instance is refused with 412 before any write) else the live one, uses a preset `client.api_key` when one is set (the live leg sets it from `RV_LIVE_WRITE_KEY`), else loads the key for that server id from `.research-vault/zotero-keys.json` (`{"<server id>": "<key>"}`, mode `0600`), authorizes **once** when absent (never in a loop: five dialogs a minute), POSTs, on 401 authorizes once more and retries once, then runs `capture(...)` on the returned keys with `key_wait_seconds=KEY_WAIT_SECONDS`. Outcomes: the create as `Outcome("capture", "add", MATCHED, "matched — created <keys>")`, then capture's. Failures: `schema-violation — item 0: unknown field foo`, `outage — authorize rate-limited ...`, `not-admitted — authorization denied` (UNMATCHED), `mismatch — create failed: <Zotero's failed map>` (UNMATCHED).

- [ ] **Step 1: Write the failing tests**

`tests/test_add.py`:

```python
import json

from research_vault import Result, capture, zotero
from tests.fakes import FakeZotero, canned_item, ITEM


def _fake_for_add(monkeypatch):
    fake = canned_item(FakeZotero())
    fake.get("/api/users/0/items?since=0&format=versions", body={}, headers={"Last-Modified-Version": "1"})
    fake.get("/api/users/0/items/trash?format=versions", body={})
    fake.get("/api/users/0/items/top?format=json", body=[ITEM], headers={"Last-Modified-Version": "1"})
    fake.get("/api/users/0/items/top?format=versions", body={}, headers={"Last-Modified-Version": "1"})
    fake.get("/better-bibtex/library?/My%20Library.json", body=[{"id": "jakesch.etal2023a", "type": "paper-conference"}])
    fake.post("/api/local/authorize", body={"key": "k" * 32, "remember": True})
    fake.post("/api/users/0/items", body={"successful": {"0": {"key": "E352DFS8", "version": 544}}, "unchanged": {}, "failed": {}})
    return fake, fake.install(zotero.ZoteroClient(), monkeypatch)


def test_add_authorizes_once_stores_the_key_creates_and_captures(tmp_vault, monkeypatch):
    fake, client = _fake_for_add(monkeypatch)
    items = [{"itemType": "journalArticle", "title": "T", "creators": [{"creatorType": "author", "lastName": "X"}]}]
    outcomes = capture.add(tmp_vault, client, items, collection="IQZW5UVX")
    assert outcomes[0].reason == "matched — created E352DFS8"
    assert (tmp_vault / "literatures" / "jakesch.etal2023a.md").is_file()
    store = tmp_vault / ".research-vault" / "zotero-keys.json"
    assert json.loads(store.read_text()) == {"6LpvURP2E933": "k" * 32}
    assert oct(store.stat().st_mode & 0o777) == "0o600"
    posts = [c for c in fake.calls if c[0] == "POST"]
    assert [p[1] for p in posts] == ["/api/local/authorize", "/api/users/0/items"]
    sent = json.loads(fake._last_post_body) if hasattr(fake, "_last_post_body") else None
    # the FakeZotero records the last POST body in `_last_post_body`; add that attribute to the fake in this task
    assert sent[0]["collections"] == ["IQZW5UVX"]

    capture.add(tmp_vault, client, items)
    assert [c[1] for c in fake.calls if c[0] == "POST"].count("/api/local/authorize") == 1


def test_add_refuses_unknown_fields_before_any_network(tmp_vault, monkeypatch):
    fake, client = _fake_for_add(monkeypatch)
    outcomes = capture.add(tmp_vault, client, [{"itemType": "book", "isbn": "x"}])
    assert outcomes[0].result is Result.UNMATCHED and "unknown field isbn" in outcomes[0].reason
    assert not [c for c in fake.calls if c[0] == "POST"]


def test_add_uses_the_recorded_server_id_when_notes_exist(tmp_vault, monkeypatch):
    fake, client = _fake_for_add(monkeypatch)
    (tmp_vault / "literatures" / "x.md").write_text(
        '---\ntype: "literature"\nzotero-server-id: "Tdoqsn2J4q4h"\nzotero-item-key: "AAAA0000"\n'
        'zotero-item-version: 1\ncitationKey: "x"\nattachments:\nfulltext:\n---\n'
    )
    outcomes = capture.add(tmp_vault, client, [{"itemType": "book", "title": "T"}])
    assert outcomes[0].result is Result.UNMATCHED and outcomes[0].reason.startswith("database-changed")
    assert not [c for c in fake.calls if c[0] == "POST" and c[1].endswith("/items")]


def test_add_reports_a_denied_dialog_and_a_failed_create(tmp_vault, monkeypatch):
    fake, client = _fake_for_add(monkeypatch)
    fake.post("/api/local/authorize", status=403, body={"denied": True})
    outcomes = capture.add(tmp_vault, client, [{"itemType": "book", "title": "T"}])
    assert outcomes[0].reason.startswith("not-admitted — authorization denied")
    fake.post("/api/local/authorize", body={"key": "k" * 32, "remember": False})
    fake.post("/api/users/0/items", body={"successful": {}, "unchanged": {}, "failed": {"0": {"code": 400, "message": "bad"}}})
    outcomes = capture.add(tmp_vault, client, [{"itemType": "book", "title": "T"}])
    assert outcomes[0].reason.startswith("mismatch — create failed")
```

Extend `tests/fakes.py::FakeZotero._http` to record `self._last_post_body = data` on every POST.

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_add.py -q`
Expected: FAIL — `capture.add` undefined.

- [ ] **Step 3: Implement `add` in `research_vault/capture.py` and the verb**

```python
KEY_STORE = ".research-vault/zotero-keys.json"
_ITEM_FIELDS = frozenset(notes.SNAPSHOT_FIELDS) | {"collections"}


def _validate_items(items) -> str | None:
    if not isinstance(items, list) or not items or len(items) > 50:
        return "items must be a non-empty list of at most 50 objects"
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            return f"item {index}: not an object"
        if not isinstance(item.get("itemType"), str) or not item["itemType"]:
            return f"item {index}: itemType missing"
        for field_name in item:
            if field_name != "itemType" and field_name not in _ITEM_FIELDS:
                return f"item {index}: unknown field {field_name}"
    return None


def _load_key(vault: Path, server_id: str) -> str | None:
    path = vault / KEY_STORE
    try:
        return json.loads(path.read_text(encoding="utf-8")).get(server_id)
    except (OSError, ValueError, AttributeError):
        return None


def _store_key(vault: Path, server_id: str, key: str) -> None:
    path = vault / KEY_STORE
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        current = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        current = {}
    current[server_id] = key
    path.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
    path.chmod(0o600)


def add(vault_root, client: ZoteroClient, items, *, collection=None, now=None) -> list[Outcome]:
    """Path A: authorize once, create, poll for the citation key, capture (§2)."""
    vault = Path(vault_root)
    problem = _validate_items(items)
    if problem:
        return [Outcome(CHECK, "add", Result.UNMATCHED, f"schema-violation — {problem}")]
    try:
        info = client.server_info()
    except DatabaseChangedError as error:
        return [Outcome(CHECK, "add", Result.UNMATCHED, f"database-changed — {error}")]
    except ZoteroError as error:
        return [Outcome(CHECK, "add", Result.UNREACHABLE, f"outage — {error}")]
    existing = lifecycle._provenances(vault)
    client.server_id = existing[0][1].server_id if existing else info["server_id"]
    if client.server_id != info["server_id"]:
        return [Outcome(CHECK, "add", Result.UNMATCHED,
                        f"database-changed — notes record {client.server_id}, Zotero answers {info['server_id']}")]
    payload = [dict(item, **({"collections": [collection]} if collection else {})) for item in items]
    key = client.api_key or _load_key(vault, client.server_id)  # a preset key (RV_LIVE_WRITE_KEY) wins over the store
    for attempt in (1, 2):
        if key is None:
            try:
                granted = client.authorize()
            except ZoteroError as error:
                if error.result is Result.UNMATCHED:
                    return [Outcome(CHECK, "add", Result.UNMATCHED, f"not-admitted — {error}")]
                return [Outcome(CHECK, "add", Result.UNREACHABLE, f"outage — {error}")]
            key = granted["key"]
            if granted["remember"]:
                _store_key(vault, client.server_id, key)
        client.api_key = key
        try:
            envelope = client.create_items(payload)
            break
        except ZoteroError as error:
            if "401" in str(error) and attempt == 1:
                key = None
                continue
            return [Outcome(CHECK, "add", error.result, f"{'outage' if error.result is Result.UNREACHABLE else 'mismatch'} — {error}")]
    created = [entry["key"] for entry in envelope.get("successful", {}).values() if isinstance(entry, dict) and entry.get("key")]
    if envelope.get("failed") or not created:
        return [Outcome(CHECK, "add", Result.UNMATCHED, f"mismatch — create failed: {envelope.get('failed')}")]
    outcomes = [Outcome(CHECK, "add", Result.MATCHED, "matched — created " + ", ".join(created))]
    return outcomes + capture(vault, client, created, now=now)
```

CLI: `cmd_add` reads `--item FILE` (JSON list or object), calls `capture.add`, prints and holds like `cmd_capture`. Parser: `add_cmd = sub.add_parser("add", parents=[common]); add_cmd.add_argument("--vault", required=True); add_cmd.add_argument("--item", required=True); add_cmd.add_argument("--collection")`.

- [ ] **Step 4: Run the suite and form owners; commit**

Run: `.venv/bin/python -m pytest tests -q -n auto && ruff format research_vault tests && ruff check research_vault tests && mypy research_vault`
Expected: PASS, clean. (The attended live leg is Part B Task 5.)

```bash
git commit -m "add the add verb: Path A create, then capture (ingest spec §2)

Authorize once through Zotero's own dialog, keep the key per server id
outside git, refuse a wrong instance before any write, poll for the
citation key to a ten-second ceiling, then capture the returned keys.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- research_vault tests
```

______________________________________________________________________

## Phase 3 — open points, the two skills, verification

### Task 18: Close open points 07, 08 and 09, and thread `--as-of` (spec §8; §7 `verify --as-of`; decisions 21 and 28)

**Files:**

- Modify: `research_vault/verify.py` (`_citation_key_hash` returns the note's `managed-sha256` and loses the `fixity-sha256` branch — open point 07; `clear_marker_for(vault_root, check, target) -> bool` — open point 09), `research_vault/inbox.py` (`scope_id(check, target, target_hash)`; `_scope_acknowledged`'s standing-scope branch compares derived scope ids; `append_entry`'s date default and `summary(vault, as_of=None)` resolve through `clock.today`), `research_vault/searchlog.py` (`_resolved_date` through `clock.today`), `research_vault/__main__.py` (`verify --as-of`, `inbox --as-of`, `_as_of(args)`; `record_finding`'s date default through `clock.today`; `cmd_ack` calls `clear_marker_for`), `research_vault/publish.py` (add the module constant `RETRACTION_ACK_FIELD = "retraction-ack"`; nothing in the package reads the field today — `grep -rn retraction-ack research_vault` is empty, measured 2026-09-07 — so there is no literal to hoist, and the constant is the code-side mirror of the definition site — open point 08)
- Test: `tests/test_verify_cli.py`, `tests/test_publish.py`, `tests/test_config_validity.py` (the one-clock scan)

**Interfaces:**

- Produces: `verify.clear_marker_for(vault_root, check, target) -> bool` — for a target of the form `<citation key>#^<claim id>` finds `literatures/<citation key>.md` (or, when absent, every `*.md` under `projects/` carrying that anchor) and removes `[failed-verification:: <check>/<date>]` from the anchored line; for a `path-bytes:` target, the file it names; returns whether a marker was removed. `publish.RETRACTION_ACK_FIELD`. `inbox.scope_id(check, target, target_hash) -> str` = `sha256(check \0 target \0 (target_hash or ""))` hex; `inbox.summary(vault, as_of=None)`; `verify --as-of YYYY-MM-DD` and `inbox --as-of YYYY-MM-DD`, both resolved by `clock.today` before any work and refused with exit 2 when malformed.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_verify_cli.py`:

```python
def test_ack_scope_hash_is_the_notes_managed_sha256(fixture_vault):
    from research_vault import frontmatter, verify

    digest = verify._citation_key_hash(fixture_vault, "smith2020")
    data, _ = frontmatter.parse((fixture_vault / "literatures" / "smith2020.md").read_text())
    assert digest == data["managed-sha256"]  # open point 07: the body hash capture writes, never a hash passed by hand


def test_ack_scope_is_derived_and_lapses_when_the_body_moves(fixture_vault, capsys):
    import research_vault.__main__ as cli
    from research_vault import inbox

    target = "fabricated2020#^c-77777777"
    expected = hashlib.sha256(b"citation-key\x00" + target.encode() + b"\x00" + b"a" * 64).hexdigest()
    assert inbox.scope_id("citation-key", target, "a" * 64) == expected
    assert inbox.scope_id("citation-key", target, "b" * 64) != expected
    assert cli.main(["finding", "citation-key", target, "UNMATCHED", "mismatch — not in bibliography",
                     "--vault", str(fixture_vault), "--date", "2026-09-07", "--target-hash", "a" * 64]) == 0
    finding_id = capsys.readouterr().out.strip()
    assert cli.main(["ack", finding_id, "--vault", str(fixture_vault), "--reason", "manual — known", "--actor", "human:eran"]) == 0
    assert inbox.is_acknowledged(fixture_vault, "citation-key", target, "a" * 64)
    assert not inbox.is_acknowledged(fixture_vault, "citation-key", target, "b" * 64)  # the body moved: the finding re-fires


def test_as_of_pins_the_instant_a_check_compares_against(fixture_vault, capsys):
    import research_vault.__main__ as cli
    from research_vault import inbox

    assert cli.main(["finding", "citation-key", "fabricated2020#^c-77777777", "UNMATCHED", "mismatch — not in bibliography",
                     "--vault", str(fixture_vault), "--date", "2026-09-07"]) == 0
    capsys.readouterr()
    assert inbox.summary(fixture_vault, as_of="2026-09-10")["oldest_age_days"] == 3
    assert cli.main(["inbox", "--vault", str(fixture_vault), "--as-of", "2026-09-10"]) == 0
    assert '"oldest_age_days": 3' in capsys.readouterr().out
    assert cli.main(["verify", "--vault", str(fixture_vault), "--offline", "--as-of", "2026-13-01"]) == 2
    assert "--as-of must be YYYY-MM-DD" in capsys.readouterr().err


def test_ack_clears_the_failed_verification_marker(fixture_vault, monkeypatch, capsys):
    import research_vault.__main__ as cli

    draft = fixture_vault / "projects" / "brief" / "draft.md"
    text = draft.read_text().replace(
        "- (inference) This will replicate [@fabricated2020] ^c-77777777",
        "- (inference) This will replicate [@fabricated2020] [failed-verification:: citation-key/2026-09-07] ^c-77777777",
    )
    draft.write_text(text)
    assert cli.main(["finding", "citation-key", "fabricated2020#^c-77777777", "UNMATCHED",
                     "mismatch — not in bibliography", "--vault", str(fixture_vault), "--date", "2026-09-07"]) == 0
    finding_id = capsys.readouterr().out.strip()
    assert cli.main(["ack", finding_id, "--vault", str(fixture_vault), "--reason", "manual — known", "--actor", "human:eran"]) == 0
    assert "[failed-verification::" not in draft.read_text()
```

Append to `tests/test_config_validity.py` (use the repository-root constant that file already defines):

```python
def test_the_package_reads_one_date_clock():
    """A check takes its instant as an argument (decision 28); only clock.py reads today's date."""
    offenders = sorted(
        path.name
        for path in (ROOT / "research_vault").glob("*.py")
        if "now(datetime.UTC).date()" in path.read_text(encoding="utf-8") and path.name != "clock.py"
    )
    assert offenders == [], offenders
```

Append to `tests/test_publish.py`:

```python
def test_retraction_ack_field_has_one_definition_site():
    from research_vault import publish

    skill = (ROOT / "skills" / "evidence-conventions" / "SKILL.md").read_text()
    assert f"[{publish.RETRACTION_ACK_FIELD}:: <code>" in skill
    assert publish.RETRACTION_ACK_FIELD == "retraction-ack"
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_verify_cli.py tests/test_publish.py tests/test_config_validity.py -q -k "ack_scope or clears or definition_site or as_of or one_date_clock"`
Expected: FAIL — fixity branch still consulted; `scope_id` missing; `--as-of` unknown; four `now(...).date()` readers outside `clock.py`; marker survives; constant missing.

- [ ] **Step 3: Implement**

In `_citation_key_hash`, delete both `attachment_hashes = data.get("fixity-sha256") ... return first` blocks and in their place return the note's `managed-sha256` when the frontmatter carries one (`value = data.get("managed-sha256")`; `if isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value): return value`), keeping the `_note_bytes` digest only as the fallback for a note capture has not written. `research_vault/inbox.py`:

```python
def scope_id(check: str, target: str, target_hash: str | None) -> str:
    """Open point 07: an acknowledgment's identity is derived, never passed."""
    parts = (check, str(target), target_hash or "")
    return hashlib.sha256(b"\x00".join(part.encode("utf-8") for part in parts)).hexdigest()
```

In `_scope_acknowledged`'s last branch (the standing scope; leave the legacy update-notice and repeatable-act branches as they are), compute `wanted = scope_id(finding.check, finding.target, finding.target_hash)` and replace the four-field comparison: `scope_ids` collects entries with `entry.ack_of is None and entry.target_kind == finding.target_kind and scope_id(entry.check, entry.target, entry.target_hash) == wanted` (plus the existing update-notice fingerprint condition), and an ack matches when `ack.ack_of in scope_ids and ack.actor.startswith("human:") and scope_id(finding.check, finding.target, ack.target_hash) == wanted` (plus the same fingerprint condition). `append_entry`: `date = _validate_date("date", clock.today(date))`. `summary(vault, as_of=None)`: the age arithmetic uses `datetime.date.fromisoformat(clock.today(as_of))` in place of `datetime.datetime.now(datetime.UTC).date()`. `research_vault/searchlog.py`: `_resolved_date(date)` returns `_validate_date("date", clock.today(date))`. `research_vault/__main__.py`: `record_finding`'s `resolved_date = clock.today(date)`; parser lines `verify.add_argument("--as-of", metavar="YYYY-MM-DD")` and `review_inbox.add_argument("--as-of", metavar="YYYY-MM-DD")`; and:

```python
def _as_of(args) -> str | None:
    """Resolve --as-of once, before any work; a malformed value is exit 2, never today."""
    try:
        return clock.today(getattr(args, "as_of", None))
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return None
```

`cmd_verify` starts with `as_of = _as_of(args)` / `if as_of is None: return 2` and passes `detection_date=as_of` to `verify_state`; `cmd_inbox` does the same and calls `inbox.summary(args.vault, as_of=as_of)`. Then add:

```python
def clear_marker_for(vault_root, check: str, target: str) -> bool:
    """Open point 09: a human acknowledgment stands the marker down."""
    vault = Path(vault_root)
    if "#^" in target:
        citation_key, claim_id = target.split("#^", 1)
        note = _note_for_citation_key(vault, citation_key)
        candidates = [note] if note and note.is_file() else sorted((vault / "projects").rglob("*.md"))
    elif target.startswith("path-bytes:"):
        candidates = [_safe_relative(vault, target, "repo-path")]
        claim_id = None
    else:
        return False
    pattern = _terminal_marker_pattern(check, claim_id)
    cleared = False
    for path in candidates:
        if path is None or not path.is_file():
            continue
        lines = _read_note_text(path).splitlines(keepends=True)
        for index, line in enumerate(lines):
            content, ending = _split_line_ending(line)
            if claim_id is not None and _terminal_anchor_match(content, claim_id) is None:
                continue
            replacement = pattern.sub(" " if claim_id else "", content)
            if replacement != content:
                lines[index] = replacement.rstrip(" ") + (" " + content[_terminal_anchor_match(content, claim_id).start():] if claim_id and not replacement.endswith(content[_terminal_anchor_match(content, claim_id).start():]) else "") + ending
                cleared = True
        if cleared:
            _write_note_text(path, "".join(lines))
            break
    return cleared
```

(Read `_terminal_marker_pattern` and `_mutate_marker`'s `clear=True` branch first and reuse their exact substitution so the anchor is preserved; the block above states the intent, the existing clear branch is the reference implementation.) `cmd_ack`:

```python
def cmd_ack(args):
    try:
        entry = inbox.append_ack(args.vault, args.finding, args.reason, args.actor)
    except (inbox.InboxError, ValueError, OSError) as error:
        print(f"acknowledgment refused: {error}", file=sys.stderr)
        return 2
    acked = next((f for f in inbox.load(args.vault) if f.id == args.finding), None)
    if acked is not None and clear_marker_for(args.vault, acked.check, acked.target):
        print(f"cleared [failed-verification:: {acked.check}] on {acked.target}")
    print(entry.id)
    return 0
```

`publish.py`: add `RETRACTION_ACK_FIELD = "retraction-ack"` beside its other module constants, with a one-line comment naming `skills/evidence-conventions/SKILL.md` as the definition site. No literal exists to hoist (see Files); the constant is where any future parser keys on the field.

- [ ] **Step 4: Run everything; commit**

Run: `.venv/bin/python -m pytest tests -q -n auto && ruff format research_vault tests && ruff check research_vault tests && mypy research_vault`
Expected: PASS, clean.

```bash
git commit -m "close open points 07, 08 and 09; verify and inbox take --as-of (ingest spec §8, §7)

The ack scope is derived from check, target and the note's managed-sha256;
retraction-ack has one definition site; a human acknowledgment clears the
failed-verification marker; every date default resolves through clock.today,
the one reader of today's date.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- research_vault tests
```

### Task 19: Rewrite the capture-source and setup-vault skills (spec §6 "Rewritten skills: import-source, setup-vault and synthesis-conventions")

`compile` does not exist until Part B Task 2, so the compile sections of both skills and the `synthesis-conventions` rewrite follow in Part B Task 3. This task ships the two skills without them.

**Files:**

- Create: `skills/capture-source/SKILL.md`, `tests/test_capture_source_skill.py`
- Delete: `skills/import-source/` (whole directory), `tests/test_import_source_skill.py`
- Modify: `skills/setup-vault/SKILL.md`, `skills/project-flow/SKILL.md` (`:15` "Read `synthesis/index.md`" and `:52` "`synthesis/` pages" become `wiki/index.md` and "`wiki/` pages" — the folder Task 6 moved) with `tests/test_project_flow_skill.py:54` (the `sequence` list's `"synthesis/index.md"` becomes `"wiki/index.md"`), `research_vault/templates/vault/AGENTS.md` (the skills table row), `README.md` (the skills table rows at `:83-84` — `find-sources` "terminates at the admission boundary" and the `import-source` row — and the routing sentence at `:89`, "Import this paper"), `docs/terminology.md` §4.3 (governed skill names: `capture-source` replaces `import-source`), `tests/test_skill_files.py`, `tests/test_skill_contracts.py:33-41` (`ENTRY_SKILLS`), `tests/test_templates.py`

**Interfaces:**

- Consumes: the verbs `capture`, `add`, `propagate`, `doctor`, `probe`; check ids and reason codes as registered.

- Produces: two skills whose frontmatter passes `tests/test_skill_contracts.py` (name equals directory, description begins `Use when `, entry skills carry `disable-model-invocation: true`, every backticked check id names one the code files).

- [ ] **Step 1: Write the failing tests**

`tests/test_capture_source_skill.py`:

```python
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
SKILL = REPOSITORY / "skills" / "capture-source" / "SKILL.md"


def test_capture_source_replaces_import_source():
    assert SKILL.is_file()
    assert not (REPOSITORY / "skills" / "import-source").exists()
    text = SKILL.read_text()
    assert text.startswith("---\nname: capture-source\ndescription: Use when ")
    assert "disable-model-invocation: true\n---\n" in text


def test_capture_source_keeps_the_kept_rules():
    text = SKILL.read_text()
    for needle in (
        "No project is required", "project-independent", "zero projects",
        "Citation Key", "Better BibTeX",
        "SKIPPED applied to reading", "the range you did not read named",
        "python3 -m research_vault capture", "python3 -m research_vault add",
        "python3 -m research_vault propagate",
        "matched — NOOP", "re-keyed", "no-fulltext", "database-changed",
    ):
        assert needle in text, needle
    assert "import-note" not in text and "managed region" not in text and "auto-export" not in text
```

In `tests/test_skill_files.py`: replace the four auto-export assertions (`"exact target path doctor reported"`, `"whole-library scope"`, `"Better CSL JSON translator"`, `"keep updated"`, `"re-run doctor to verify"`, `"Never register an auto-export for them"`, the `autoexport` MATCHED sentence) and the decision-17 strings (`"BBT required"`, `"MarkDB-Connect optional"`) with:

```python
    assert "Zotero .xpi installs are human-only wizard steps" in companions
    assert "research_vault/templates/zotero-addons.md" in companions
    assert "README" in companions
    assert "zotero_profile" in companions
    assert "rename_frontmatter_key" in text  # the one-shot citekey migration, §1.1
```

In `tests/test_skill_contracts.py` `ENTRY_SKILLS`, replace `"import-source"` with `"capture-source"`.

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_capture_source_skill.py tests/test_skill_files.py tests/test_skill_contracts.py -q`
Expected: FAIL — no `capture-source` directory.

- [ ] **Step 3: Write the skills**

`git mv skills/import-source skills/capture-source && git rm -q skills/capture-source/references/*.md tests/test_import_source_skill.py`. Then `skills/capture-source/SKILL.md`:

````markdown
---
name: capture-source
description: Use when a person asks to capture, refresh, or add a source in a research-vault vault, or to propagate a citation-key change
disable-model-invocation: true
---

# Capture a source

Ingest is the process that gets a source from outside the vault into the vault: **selection** (the person's decision), **add** (the Zotero item), **capture** (the deterministic copy into the vault), **compile** (the adopted tool's pages). This skill runs the mechanical steps; the decision is never yours. If the person has not decided, stop and ask; nothing in `inbox/` is citable, and no amount of capturing changes that.

**No project is required.** The flow is continuous and project-independent, so every step below runs on a vault with zero projects; only `find-sources` is project-scoped.

In every command, `PATH` is the vault and `KEY` is either the Zotero item key (eight upper-case characters, shown in Zotero's item pane) or the citation key — Zotero's own **Citation Key** field, which Better BibTeX fills and which shows in the item list's Citation Key column. Never invent or guess one. Every mechanical act below is a CLI verb call: you compose and explain, the CLI writes. `literatures/`, `fulltext/`, `system/bibliography.json`, `system/propagations/` and `wiki/` are machine surfaces; never `Write` or `Edit` them.

## 1. Add: `add`

When the item is not in Zotero yet and the person has asked you to add it, write a Zotero item JSON file — `itemType` plus any of the snapshot fields (`title`, `creators`, `date`, `DOI`, `url`, `publicationTitle`, `volume`, `issue`, `pages`, `publisher`, `ISBN`, `language`, `abstractNote`, `extra`, `accessDate`, `tags`) — and run:

```sh
python3 -m research_vault add --vault PATH --item ITEM.json [--collection COLLECTION_KEY]
```

The first run on a machine opens Zotero's own consent dialog (**Allow**, **Always Allow**, **Deny**); tell the person to answer it in Zotero. Never retry `add` in a loop: the dialog is rate-limited to five a minute. Better BibTeX fills the citation key a few seconds after creation; `add` waits up to ten seconds and then captures the new item. `unkeyed` means the key never arrived: report it, do not write a note by hand.

## 2. Capture: `capture`

```sh
python3 -m research_vault capture KEY [KEY ...] --vault PATH
python3 -m research_vault capture --all --vault PATH      # refresh every captured note
```

Capture runs the lifecycle linter first, then for each item reads the item, its children and the indexed text, writes `literatures/<citation key>.md` (frontmatter: Zotero's own fields verbatim, the provenance tuple, a body carrying only the attachment list and the item's Zotero child notes), writes `fulltext/<attachment key>.md` for every attachment with usable text, and regenerates `system/bibliography.json` whole. One line per outcome:

| Line | What happened |
| --- | --- |
| `MATCHED KEY — matched` | The note was written or rewritten. |
| `MATCHED KEY — matched — NOOP` | The projection is identical. Nothing was written. Report it as "already current", never as an error and never as a capture you performed. |
| `UNMATCHED KEY — not-admitted — …` | The key is not in the library. |
| `UNMATCHED KEY — no-fulltext — …` | The note was written, but no attachment has usable text (absent, partial past Zotero's page cap, or below the content floor), so there is no compile input. Read the reason back verbatim. |
| `SKIPPED KEY — no-fulltext — no attachment to read (…)` | The item holds no file at all — a web page, a repository, a program. The note was written; the text checks do not apply, and nothing was filed. Getting text for such sources is a later lane's work, not a capture failure. |
| `UNMATCHED KEY — re-keyed — old → new` | The citation key changed. Run `propagate` (§4). |
| `UNMATCHED KEY — merged|trashed|deleted — …` | The item left the library. Nothing was written; the note is kept. |
| `UNMATCHED vault — database-changed — …` | A different Zotero database answered. Nothing was written. Stop and tell the person which server id the notes record. |
| `UNREACHABLE … — outage — …` | Zotero did not answer. **Never a verdict on the source.** Retry later. |

Every non-MATCHED line already filed its own review record under check id `capture`; never file one for a failed capture yourself. If stderr carries `warning: review record refused:`, say so out loud.

## 3. Verify what capture cannot see

Run `python3 -m research_vault verify --vault PATH` with the network on after a capture: it runs the lifecycle linter over every note (check id `lifecycle`), the captured-set lint at the compile seam (`captured-set`) and the update-notice check. Route reading of that run to `verify-citations`.

## 4. Propagate a citation-key change: `propagate`

A `re-keyed` finding means the source's *name* changed while its identity (the item key) did not. Until propagation runs, the note's filename contradicts its recorded key and every `[@old]` and `[[old]]` dangles. Propagation is the one command here that rewrites what a person wrote, so it is planned, shown, and applied only against the plan you showed:

```sh
python3 -m research_vault propagate --vault PATH                    # plan: every re-keyed note the linter reports
python3 -m research_vault propagate --vault PATH --map OLD=NEW      # plan from an explicit mapping, e.g. after a deliberate regenerate
python3 -m research_vault propagate --vault PATH --plan FILE --approved-plan-sha256 SHA   # apply, exactly as printed
```

The plan lists the rename, the item key and every file it will rewrite, and ends with the apply line carrying the plan's hash; show it to the person and run that line unchanged. If anything the plan named moved in between, apply refuses with `mismatch — plan changed`: plan again. Apply renames the note, rewrites `[@key]` and `[[key]]` in drafts and wiki pages, re-captures the item, and keeps the applied plan under `system/propagations/` — the record a reader follows an old key forward through. The review queue is never rewritten; acknowledgments on the renamed note lapse by scope, as they do for any content change. The `propagation` check fails a commit while any surface still names a key an applied plan mapped away.

## Four-state honesty

| Result | Meaning at capture |
| --- | --- |
| MATCHED | The step ran and agreed. Only the CLI's deterministic checks mint a `verified` event; nothing in this skill ever does. |
| UNMATCHED | The step ran and disagreed. Already in the review queue — do not file it again. |
| UNREACHABLE | The step could not run — Zotero or the network is down. Never a verdict on the source. Retry later. |
| SKIPPED | The step does not apply. Automatic only. |

The same honesty covers your own reading. A source you read only in part is reported **partial**, with the range you did not read named — pages the text layer stops at, sections you never reached. That is SKIPPED applied to reading: an unread stretch must never read as read.

## Routing

| Need | Route to |
| --- | --- |
| Find sources to add | `find-sources` |
| Rules for the compiled layer | `synthesis-conventions` |
| Run the deterministic checks | `verify-citations` |
| Acknowledge a finding capture filed | `project-flow` or `publish` (the `ack` verb) |
| Install Zotero add-ons | `setup-vault` |
````

`skills/setup-vault/SKILL.md`: keep `## Scaffold` and `## Diagnose` as they are except the doctor sentence, which becomes "Report every doctor probe, not only failures — thirteen rows — plus the inbox count and oldest age." Replace `## Provision companions` from its fourth paragraph on with:

````markdown
Zotero .xpi installs are human-only wizard steps. The add-ons the vault asks for are declared once, in the table `README.md` embeds from `research_vault/templates/zotero-addons.md` (required, recommended, optional, each with its add-on id and, where one exists, the preference that switches its automatic mode on). Walk the person through installing each *required* row in Zotero's Add-ons window and enabling the automatic-mode preferences; never download, never install, never click, and never close Zotero for the user. Doctor's `plugins` probe reads the same table and reports each add-on's `active`/`appDisabled` state and whether its automatic mode is on.

Doctor can only read those facts when `.research-vault/machine.json` names the Zotero profile directory under `zotero_profile` (on this class of machine: `/mnt/c/Users/<user>/AppData/Roaming/Zotero/Zotero/Profiles/<id>.default`). Ask the person for it once; without it doctor reports `fulltext-sync`, `bbt-git` and `plugins` as SKIPPED, never as passed.

## Migrate an older vault

A vault whose literature notes carry the old `citekey:` frontmatter key runs the one-shot migration before its first capture:

```sh
python3 - <<'PY'
from pathlib import Path
from research_vault import notes
for path in sorted(Path("literatures").glob("*.md")):
    text = path.read_text(encoding="utf-8", newline="")
    renamed = notes.rename_frontmatter_key(text, "citekey", "citationKey")
    if renamed != text:
        path.write_text(renamed, encoding="utf-8", newline="")
        print("migrated", path)
PY
```

Run it from the vault root, report the paths it printed, and then `capture --all` to bring every note to the current record shape.
````

`research_vault/templates/vault/AGENTS.md`: the skills table row becomes `capture-source` — "add, capture, refresh, or propagate a re-key of a source". `README.md`: the `find-sources` row's "terminates at the admission boundary" becomes "terminates at the person's selection"; the `import-source` row becomes `| Catalog | \`capture-source\` | Add an item to Zotero, capture it into \`literatures/\` and \`fulltext/\`, propagate a citation-key change |`; the routing sentence at `:89`becomes "Capture this paper" is not "capture it and rebuild the concept page."`docs/terminology.md`§4.3: the governed skill names list swaps`import-source`for`capture-source\`.

- [ ] **Step 4: Run the suite and form owners; commit**

Run: `.venv/bin/python -m pytest tests -q -n auto && mdformat --number --wrap keep skills/capture-source/SKILL.md skills/setup-vault/SKILL.md research_vault/templates/vault/AGENTS.md docs/terminology.md`
Expected: PASS.

```bash
git commit -m "rewrite capture-source and setup-vault (ingest spec §6)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- skills tests research_vault docs README.md
```

### Task 20: Final verification, the merge, the report to the author

**Files:**

- Modify: nothing; this task's deliverable is a green tree on `main` and a message.

- [ ] **Step 1: Full verification**

```bash
.venv/bin/python -m pytest tests -q -n auto
ruff format --check research_vault tests scripts hooks && ruff check research_vault tests scripts hooks && mypy research_vault
.venv/bin/python -m pytest tests -q --cov=research_vault --cov-branch --cov-report=lcov:lcov.info && .venv/bin/crap4py research_vault --lcov lcov.info --max-crap 30 && .venv/bin/drywall research_vault
RV_LIVE=1 .venv/bin/python -m pytest tests -q -k live
python3 scripts/mutation_gate.py --lcov lcov.info --max-workers 1 --base main
git status --porcelain   # must be empty
```

Expected: every command exits 0; report the pytest counts and the mutation-gate summary line verbatim. If the mutation gate reports survivors in `factcheck.py`, `lints.py` or `verify.py` whose only difference from a baseline row is Task 7's rename or the `ruff format` reflow of the same expression, refresh those rows from the run's output and say so rather than judging them new (row 15 of `2026-09-07-ingest-redesign-a-deferred.md` records the one pre-existing row that never matched). The CRAP command must already pass: the two functions the dated deferral covered (`_bump_generated`, `check_metadata`) were deleted in Tasks 1 and 3. The workflow's `continue-on-error` itself is removed in Part B Task 4.

- [ ] **Step 2: Merge to `main`**

Per `AGENTS.md`: fetch first, merge back to `main` locally and push `main` to origin in the same motion. If this part ran on `main` directly, push. Part B does not start before this lands.

- [ ] **Step 3: Disposition the deferred-minor roll-up**

The execution keeps `docs/superpowers/plans/2026-09-07-ingest-redesign-a-deferred.md` on the branch — one row per finding a task review deferred (file, line, one sentence, the task that recorded it), plus a `Do not fix` section for decided non-actions with their reason (the first is the `quote:<claim-link>:managed-region` check value, a durable value in written `verified` events that ADR 0003 keeps), and a `Process notes` section for lessons about running the plan. It is committed as it grows, so nothing in it dies with the SDD workspace, and it is the home `AGENTS.md`'s task-reports rule asks each Concern to name at write time. The whole-branch review works from it: every row ends as **fixed** (commit named) or **declined** (reason written into the row). Rows still open after that review become one repository issue, filed here with `gh issue create --label ready-for-agent` and the rows as its body (a repository issue on this tracker is ordinary work, not the outward-facing act the constraints gate; the upstream Zotero issue is Part B's). The file itself stays: it is the record.

- [ ] **Step 4: Report invariant 5 to the author (no action)**

In the completion message, state: the lifecycle linter's pre-commit leg is held (spec invariant 5); `verify --offline` reports it `UNREACHABLE` and never blocks; the write-side gate the leg waits on is unchanged — measured 2026-09-06 (decomposition §15.20), `main` has no branch protection and no rulesets, and this checkout has no `.git/hooks/pre-commit`. Settling the gate is the author's call; the plan changes nothing there.

- [ ] **Step 5: Completion message**

Report: the tasks landed (with commit shas), the read-only live-leg results, the invariant-5 report, the roll-up's disposition (fixed, declined, filed as `#<n>`), the process notes the roll-up records, anything skipped with its reason, and what Part B needs from the author before it starts: presence for the tracers (Part B Task 1, Obsidian open) and for one consent dialog on the test instance (Part B Task 5).

______________________________________________________________________

## Self-review

### Spec coverage

Task numbers are this part's; `B n` names a Part B task. Part B's own self-review covers its sections again from its side.

| Spec section                         | Requirement                                                                                                                                                                                                    | Task                         |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| §0                                   | Scope: scholarly documents; capture on demand; greenfield; derived text as gitignored cache; screening belongs to the review; URL-only classes deferred mechanically — no attachment is SKIPPED, not a finding | 4, 10, 13                    |
| §1 table                             | States and owners: captured, compiled, current, drifted, re-keyed, merged, trashed, deleted, database changed                                                                                                  | 12, 13, 14, B2               |
| §1 invariants 1–6                    | identity once; server id in every tuple; no deletion; every transition visible; one linter code path with the pre-commit leg held; falsifiability                                                              | 11, 12, 13, 20; B6           |
| §1 "full-map read"                   | `?since=0` full maps, three reads                                                                                                                                                                              | 9, 12                        |
| §1.1                                 | retire then rename; 200 identifiers; ten skill files; frontmatter migration; glossary; `import`/`authority` collisions; captured set defined                                                                   | 1–8, 15, 19                  |
| §2                                   | Path A authorize/write; `Zotero-Server-ID` recorded not echoed; key poll to 10 s; Path B dropped; tags verbatim; no pinning; URL-only cut; archive retired                                                     | 1, 9, 11, 17                 |
| §3.1                                 | item key + server id identity; filename `literatures/<citation key>.md`; alias probe; rename by propagation                                                                                                    | 11, 14, B1 (T5)              |
| §3.2                                 | snapshot fields; provenance tuple; `annotations` deferred; wholly machine-written note; vault-owned fields dispositioned; CSL file scope = captured set; `Extra` note                                          | 5, 11, 13, 18                |
| §3.3 steps 1–7                       | reads; annotations route measured/unwired; fulltext usability; whole-library CSL read + fallback; body renders only what frontmatter cannot; NOOP; per-item restart; library re-read                           | 9, 10, 11, 13                |
| §3.4                                 | linter at capture and verify; 412 stop; three reads; per-object classification; drift cause; reason order; outage at pre-commit never a classification                                                         | 12, 13                       |
| §3.5, 3.5.1                          | detection only in the linter; propagation task set; the applied plan is the log (open point 12 closed); regenerate_key never called                                                                            | 12, 14                       |
| §3.6                                 | no absolute paths; `fulltext/` layer, gitignored, OKF-conformant, walked; not in `VAULT_DIRS`; named by attachment key; compile input = best attachment; hash machine-local                                    | 10, 11, 13                   |
| §3.7                                 | local API only; translator formats 500; base URL configurable                                                                                                                                                  | 9, 16                        |
| §3.8                                 | build verdict recorded; nothing to implement                                                                                                                                                                   | —                            |
| §4.1–4.3                             | adoption at `ad67087`; tracers T1–T4; `wiki/` layout; `.raw/`, `.vault-meta/` gitignored and unwalked; `capture` unused; modes                                                                                 | 6, B1, B2                    |
| §4.3.1                               | `wiki/index.md` exemption in `structure.py`                                                                                                                                                                    | 6                            |
| §4.4                                 | captured-set lint (textual + structural); no second copy of text; `wiki/concepts/`; recompile-needed; the note embeds the compiled page (reversed 2026-09-07)                                                  | 6, 11, 13, 15                |
| §4.5                                 | wrapper owns selection, locators, ledger records, invocation; no prompt                                                                                                                                        | B2                           |
| §5                                   | doctor probes incl. write guard, 403, profile facts, plugins via `appDisabled`/`active`, path shim, translator-format warning; facts file gone; auto-export retired from setup                                 | 16, 19, B3                   |
| §6 retire                            | auto-export; base constant; screening state; claim lines; managed region; doi/metadata; `archive-source`; synthesis under `wiki/`; frozen checks untouched; kept items                                         | 1–6                          |
| §6 reason codes                      | five new; three plan-assigned (`stale-key`, `no-fulltext`, `recompile-needed`)                                                                                                                                 | 12, 13, 14, 15               |
| §6 skills                            | import-source, setup-vault, synthesis-conventions rewritten                                                                                                                                                    | 19, B3                       |
| §7                                   | offline fixtures from the sitting; no recorder; live legs; the missing trashed snapshot; `--as-of` replay                                                                                                      | 12, 15, 18, B5               |
| §8 open points 04, 07, 08, 09, 12    | names; derived ack scope; retraction-ack site; ack clears marker; the applied plan is the log                                                                                                                  | Decisions 1, 3–7, 21; 14, 18 |
| §8 open points 05, 06, 10, 11, 13–16 | recorded deferrals; nothing to build                                                                                                                                                                           | —                            |
| Decision 17 / §6.1                   | add-on declaration with ids; `active` + `appDisabled`                                                                                                                                                          | 16                           |
| Decision 28                          | annotations deferred, specified not run                                                                                                                                                                        | 9 (`annotations()` unwired)  |
| Decision 29                          | propagation in the same plan, rename-log site settled first                                                                                                                                                    | Decision 1, Task 14          |

### Placeholder scan

Every `...` in a code block names the existing lines it stands for (`# unchanged body from :73-98`, `# the existing extraction body verbatim`); none says "implement later". The two hook deny legs (Tasks 6 and 10) are a printed test plus named additions to the existing parametrize lists in `tests/test_hooks.py`; nothing is left as "copy the other one".

### Type consistency

- `notes.Provenance` fields and `notes.read_provenance` (Task 11) are what `lifecycle.classify` (12), `capture._capture_one` (13), `propagate.propagate` (14), `captured._notes` (15) and `compile.ledger_record` (Part B Task 2) consume.
- `ZoteroClient.versions()` returns `(map, version)`; `trash_versions()` returns the map alone; `top_items()` returns `(list, version)` — used that way in 12, 13, 16 and Part B Task 5.
- `fulltext.write` returns `(path, sha256)`; `capture._write_texts` records the sha256 as the `fulltext` entry and `compile-input-sha256`; `captured._structural` compares the ledger's `content_sha256` against that same value; `compile.ledger_record` writes it as `content_sha256`.
- Check ids and reason codes used in code blocks are exactly the registries Part B Task 4 fixes.
