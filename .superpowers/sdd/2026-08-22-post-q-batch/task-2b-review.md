# Task 2b review - a808f09..660f752

Disposition: historical (2026-09-06)

All verification below ran with the worktree at `HEAD = 660f752f896cdbcc72971b5cbae7538dc7300934`, the reviewed commit, with `git status --short` clean.

## Spec Compliance

**Verdict: compliant.** No missed, extra, or misunderstood requirement survived verification. The brief's two steps are both satisfied, and every constraint the brief and the controller attached to them holds.

Step 1 asked for the two embeds under the folder links, each with a one-line lead-in compressed from the Base's own purpose. `research_vault/templates/vault/index.md:15` is `![[system/bases/trust-tier.base]]` and `:18` is `![[system/bases/open-questions.base]]`, verbatim as specified. `cat -A` on the template shows both embed lines ending `]]$` with no backslash escaping, no smart-quote substitution and no whitespace damage. The lead-ins at `:14` and `:17` are compressed from the Base files' actual bytes, which I read directly rather than from the report: `trust-tier.base` carries `views: - type: table / name: Trust tier` and `filters: and: - 'type == "literature"'` with no formulas and no `order` key, and the lead-in `Literature notes, for trust-tier review:` states exactly that filter plus the view's own declared name, stopping short of claiming a tier column the file cannot produce. `open-questions.base` adds `formulas: open_q: 'file.content.contains("(open-question)")'`, and the lead-in `Synthesis notes, flagged where they contain an open-question:` says *flagged*, which matches a per-row boolean column rather than overstating it as a filter.

Step 2's same-commit pin constraint is satisfied by mechanism, not by luck. I parsed both test files with `ast` and compared each string literal against the template's real bytes: `tests/test_templates.py:79` and `tests/test_scaffold.py:81` each reconstruct `research_vault/templates/vault/index.md` exactly (588 characters, byte-identical), and both landed in commit 660f752 alongside the content they pin. A repo-wide grep for `Vault index` and `vault/index.md` turns up no third assertion on this template's content — the other hits are historical plan documents and per-test fixtures that write their own `index.md`.

The controller's scope guard holds: `sed -n '10p'` on the template returns exactly `- [[log/]] — daily activity log (summary: [[log]])`, and that line appears only as unchanged context in all three diff hunks. No trace of the "rolled up" rewording owed to a future step. Nothing moved: no `.base` file is touched by the diff, both Bases remain at `research_vault/templates/vault/system/bases/`, and `tests/test_templates.py:37` `test_all_canonical_template_paths_are_packaged` — which asserts exact set equality over every packaged template path — still lists both and still passes, so no move, copy or duplicate into the knowledge tree occurred. `research_vault/scaffold.py` `VAULT_DIRS`, `tests/test_scaffold.py:33-34` `EXPECTED_CREATED`, and the doctor path list are all untouched.

The global "comments state constraints; provenance belongs in the commit body" constraint is satisfied on both sides: no explanatory comment was added to the template or either test file, and the commit body carries the full 2026-08-24 ruling.

### Cannot verify from diff

Two of the three items the lenses raised were closed during synthesis; they are recorded here as resolved rather than passed to the controller.

- **Commit body provenance and exact subject — RESOLVED.** `git log -1 --format=%B 660f752` shows the body records the 2026-08-24 plan addition, both lead-ins' derivation from their Base's filter/formula, the vault-outlives-its-tools rationale for leaving `.base` filed in `system/` (Obsidian-only tooling format; embedding buys one-click access without pulling a tool artifact into the knowledge tree), the two-pin situation, and the untouched line 10. The subject is exactly `feat: vault index embeds the trust-tier and open-questions Bases` with nothing appended.
- **Suite and form gate — RESOLVED.** I ran `.venv/bin/python -m pytest tests -q -p no:cacheprovider` at 660f752: **1575 passed, 7 skipped**, no warnings, matching the stated baseline and the implementer's report. The form gate was closed by mechanism instead of re-running it, since `pre-commit run --all-files` can rewrite files and this review is read-only: `.venv/bin/ruff format --check` reports both changed test files already formatted and `ruff check` passes, `.pre-commit-config.yaml:57` runs `mdformat --number --wrap keep README.md AGENTS.md CONTEXT.md docs skills`, whose path list provably excludes `research_vault/templates` and `tests/`, and the working tree is clean at the reviewed commit, so nothing was reformatted. (The report's "8/8" against ten hook ids in the config is not a discrepancy worth chasing: pre-commit skips hooks whose file filters match nothing, and the claim that matters — no reformatting of the three changed files — is independently proven.)
- **Obsidian rendering of the two embeds — OPEN, NON-BLOCKING.** Two sub-questions, neither answerable offline and both raised independently by the quality and fidelity lenses. (a) Each lead-in sits on the line immediately above its embed with no blank line between, so in CommonMark the pair is a single paragraph; whether Obsidian promotes an alone-on-its-line `![[x.base]]` to a block-level table embed under paragraph continuation, or renders it inline, could not be established here. (b) `open-questions.base` declares `formulas.open_q` but no `order`/column list, so whether the `open_q` flag column is visible in the default table view is unsettled — if it is not, the lead-in describes something the reader cannot see.
  **Controller check:** scaffold a fresh vault, open `index.md` in Obsidian 1.9+ (Bases-capable) reading mode, and confirm both embeds render as block tables under their lead-ins and that the open-questions table shows the `open_q` column.
  **This does not block.** If (a) fails, one blank line fixes it; if (b) fails, it is a defect of the pre-existing `open-questions.base` — a file outside this diff — fixed by adding an `order` key. Neither changes the spec or quality verdict.

## Strengths

- **The implementer found the pin the brief and the controller both missed.** The brief named only `tests/test_templates.py:79` and declared its surface list exhaustive ("nothing to hunt for"). Running the full suite rather than trusting it surfaced a second whole-file pin on the identical string, `tests/test_scaffold.py:81` inside `test_scaffold_creates_the_complete_okf_vault_and_returns_paths`, which asserts the *scaffolded* vault's `index.md` rather than the packaged asset. It was fixed in the same commit per the pin constraint, and the gap was flagged back to the task author as a possible batch-wide pattern rather than silently absorbed. Worth relaying: other briefs in this batch that pin content duplicated between a template asset and a scaffold-output assertion may have the same incomplete enumeration.
- **The trust-tier lead-in withholds a claim the file cannot support.** This is the piece of judgement in the change. `trust_tier` is computed at runtime by `research_vault/events.py` over verified events, not stored as a frontmatter property, so a declarative Base cannot read it — and `trust-tier.base` accordingly has no formula and no tier column. The lead-in states the filter plus the view's own name and stops, instead of writing the sentence that would have read better and been false. That is precisely the "compress from the Base's own purpose; don't invent" instruction being followed rather than approximated.
- **Byte-exactness was checked at the right level, and it holds.** Both pins reconstruct the template's 588 bytes exactly — the `\n\n` paragraph joins, the blank line after the `system/` bullet, and the single trailing newline all match `cat -A` output on the real file. The embeds are protected against silent drift in both the packaged asset and the scaffolded output.
- **The scope guard was respected and independently confirmed.** Line 10 is byte-identical, appearing only as unchanged context in all three hunks. The 2026-08-23 "rolled up" rewording that belongs to a later step did not leak in.
- **Provenance is in the commit body and nowhere else.** No explanatory comments were smuggled into the template, which is exactly the split the global constraint asks for.
- **The blast radius is minimal and correct.** Sixteen lines across exactly the three files the work requires; no `.base` file moved, copied or duplicated; `VAULT_DIRS`, `EXPECTED_CREATED` and `doctor` untouched; no new tests, no refactors, no drive-by rewording. The embed paths are vault-root-relative and resolve in a real scaffolded vault, since `tests/test_scaffold.py:33-34` pin `system/bases/open-questions.base` and `system/bases/trust-tier.base` as created scaffold outputs.

## Issues

### Critical (Must Fix)

None.

### Important (Should Fix)

None.

### Minor (Nice to Have)

**1. `tests/test_scaffold.py:81` — the canonical `index.md` literal is duplicated verbatim across two test files.** Status: NOT-VERIFIED-MINOR. Plan-mandated: no.

The same twelve-line (now sixteen-line) literal appears at `tests/test_scaffold.py:81-95` and `tests/test_templates.py:79-93`, and must be hand-edited in lockstep on every template change. The cost is not theoretical — it materialized in this very task: the brief named only the `test_templates.py` pin, the implementer edited it, and the first suite run failed (1 failed / 1574 passed / 7 skipped) on the second, undocumented copy. Every future template edit pays the same tax, discoverable only by running the full suite.

How to fix: do **not** extract a shared constant. That would weaken both pins, since a single wrong edit to the constant would satisfy both assertions and the byte-level guarantee would evaporate. The sound fix is to make `test_scaffold.py` assert fidelity rather than restate content it does not own — `assert (vault / "index.md").read_text() == asset("vault/index.md").read_text()`. Scaffold's contract is "copies the template verbatim"; the template's byte-level content contract stays owned solely by `test_templates.py:79`.

This is pre-existing structure that the change extended rather than introduced, which is why it is Minor and not a block.

**2. `tests/test_scaffold.py:91` — no test asserts the new embed targets actually resolve in a scaffolded vault.** Status: NOT-VERIFIED-MINOR. Plan-mandated: no.

The change introduces a new cross-file reference (`index.md` → `system/bases/*.base`), but the embed paths are pinned only as opaque text. The path strings inside the index pin and the real file paths in `EXPECTED_CREATED` (`tests/test_scaffold.py:33-34`) and the asset list (`tests/test_templates.py:23-24`) are independent literals. Renaming a `.base` file while updating those path lists but not the index template would leave a dangling embed with the whole suite green — and a dangling embed is a silently blank dashboard, which is exactly the user-visible outcome this task exists to deliver.

How to fix: one assertion in the scaffold test makes the linkage self-enforcing, e.g. `for target in re.findall(r"!\[\[(.+?)\]\]", (vault / "index.md").read_text()): assert (vault / target).exists()`. That converts a rename into a test failure instead of a silent blank embed.

The gap is narrow — the path lists live in the same two files as the pins, so a renamer would probably notice — hence Minor.

## Refuted During Verification

None. No lens produced a finding that verification refuted, and no severity required correction: the two surviving findings were raised as Minor and stand as Minor. The spec and fidelity lenses produced no findings at all.

## Assessment

**Task quality: Approved.**

The brief's two steps are met exactly, with the two literal embed strings verbatim, lead-ins that are demonstrably compressed from the Base files rather than invented, both byte-equality pins proven correct by parsing rather than inferred from a green suite, and the suite independently re-run at the reviewed commit (1575 passed / 7 skipped). The only two findings are Minor test-structure observations about pre-existing duplication that this change extended, and neither blocks; the sole open cannot-verify item is an Obsidian rendering question with a trivial fallback on either branch.
