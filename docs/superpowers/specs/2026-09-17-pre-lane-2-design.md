# Clearing the way to lane 2: the pre-lane-2 milestone as one spec

Status: **the active spec** (2026-09-17), beside the open decomposition (`2026-09-05-assembly-design.md`). Decision 22 of that document allows one open plan at a time; this spec's plan is it. It succeeds `2026-09-06-import-redesign-design.md` (lane 1, closed 2026-09-16) and amends it in place where a finding here changes it, each amendment dated. The skills comparison's briefs and matrix are the evidence sibling `2026-09-17-pre-lane-2-design-skills-evidence.md`.

**What this spec is.** The seventeen open issues of the `pre-lane-2` milestone, resolved here — none deferred — plus two preconditions outside it: the quality lane is red at `HEAD`, and the write-side gate the operator chose needs a public repository. The plan beneath this spec executes the spec, not the tickets; the issues close when the spec is approved (§11). What the spec sends onward is filed as issues in the same pass (§11).

**How to read.** Every `file:line` is at `edb91fd` unless dated otherwise; every citation was re-verified on 2026-09-17. Files an issue cites that the 2026-09-16 sweep deleted are read from history: `git show 3a58a44^:<path>` (the three deferred registers), `git show 1d019ff^:<path>` (the results files), `git show 3e35f8d^:<path>` (the Part A mutation-survivors record). An unqualified "decision NN" means this spec's §1; the Part A plan's decisions 08 (the citation key as identity) and 10 (the Windows file-URL premise) are always named as the Part A plan's. Part A, Plan W, Part B, the lanes and invariant 5 are the assembly spec's terms. Each issue section carries the finding in one sentence, the design, and the pins; the closed issue keeps its own text.

**What binds.** The measured environment, dated; the decisions in §1; ADRs 0001–0003; the ingest spec's invariants and chosen headings as amended here. Churn is not priced: where two shapes differ only in how much they touch, the complete one is taken (operator, 2026-09-17).

______________________________________________________________________

## 1. Decisions

Rulings only; each section carries the argument.

01. **One spec for the milestone.** Assembly-spec decision 22 governs that document's own slot, not what a follow-up may bundle; it carries a dated sentence saying so (§11).
02. **Issues close at approval, in one pass with the touched-issue comments and the filed-onward issues** (§11).
03. **The quality lane is repaired first** (§2.1).
04. **`tests/test_current_state.py` stays and is repaired** — four repairs (§2.2).
05. **The repository goes public now, history cleaned first**; the product boundary's distribution-clean-artifact sentence becomes a mechanism (§3.1–§3.2).
06. **The write-side gate is a ruleset with required status checks; the mutation gate is its own job and is not required** (§3.3–§3.5). Supersedes the assembly spec's "branch protection follows after lane 4" (`:103`).
07. **Invariant 5's pre-commit leg stays held, with lane 5 as its new trigger; no developer pre-commit hook in this checkout** (§3.6–§3.7).
08. **The gate refuses a dirty tree, in both modes** (§3.8).
09. **The time budget is gate-side, guarding modules 2..N after the first returns** (§3.9).
10. **`literatures/` becomes `literature/` everywhere it is spelled; a doctor row catches an old vault** (§4.1).
11. **The vault template's machine-surface roster is derived from the guard's constants by a test** (§4.2).
12. **`notes.py` becomes `literature_notes.py`, every reference following, no alias**; later sections use the new name (§4.3).
13. **The vault hook path is a literal; `_git_path` is removed rather than guarded** (§4.4).
14. **Three module cuts land in the same batch as the two renames** (§4.5).
15. **`research_vault/frontmatter.py` stays: verdict `build`, `floor_failed` M3** — the must no candidate met (§5.1).
16. **A duplicated machine-owned frontmatter key is a `schema-violation`, per candidate file, one row per key, drift comparison skipped for that file** (§5.2).
17. **An equivalence reason lives beside its key in `mutation-baseline.txt`; the gate preserves it across rewrites and reports one it cannot re-attach** (§6.1).
18. **Every key of the named functions and modules is dispositioned; the lost partition is not reconstructed** (§6.2).
19. **The Part A plan's decision 10 stands; the path-shim probe reports `SKIPPED` on a POSIX URL** (§7.1).
20. **A nested directory under `literature/` is a `tree` finding, one row per directory; the walker stays** (§7.1).
21. **Capture refuses a re-keyed item by identity** (§7.1).
22. **An unguarded read of a record under judgement yields a per-target row; of a run input, exit 2** (§7.2).
23. **`_worktree_path_hash` is deleted narrowly** (§7.2).
24. **`stamp_types(paths=…)` resolves and contains; `paths=` stays** (§7.3).
25. **`test_pyproject_fmt_flags_match_the_hook_the_seam_actually_runs` is rebuilt on `yaml.safe_load`** (§7.4).
26. **The OKF pin has one writer, a data file beside the job that consumes it** (§7.5).
27. **No research-vault skill drops for the tool's; three adapt, six keep; nine edits** (§8).
28. **The client paragraph lands at the head of ingest spec §3.7** (§9.1).
29. **The distribution name is `research-vault-core`; slug and plugin name stay `research-vault`** (§9.2).
30. **One blanket `--update-baseline --out-dir` run closes the plan** (§10).

______________________________________________________________________

## 2. The quality lane and `tests/test_current_state.py`

### 2.1 The lane is red

Every run since `4df5e95` fails at "Form + lint" — ruff `PERF401` at `tests/test_current_state.py:136`, `FURB167` at `:142` — and skips every later step. Fixed in the plan's first task.

### 2.2 The file stays; four repairs

Its scanner already earns its place: run over this spec's inputs it caught #134's two test-pinned ingest-spec citations (`:141`, `:146`), and after #142 and #91 it guards a stray old spelling on a prose surface and a stale path in the #139 paragraph.

1. **Derived surfaces.** `CURRENT_STATE_SURFACES` (`:32-47`) is a literal list. It becomes the fixed prose surfaces plus every tracked `docs/superpowers/specs/*-design.md` whose header has no `Disposition:` line — this spec enters without an edit; the `*-evidence.md` siblings and the one historical spec stay out.
2. **The deny-list has one writer.** `RETIRED` (`:106-122`) is fifteen patterns that exist nowhere else. `docs/agents/terminology.md` gains a section "Retired spellings" — one row per pattern: the pattern as a code literal, the date, what replaced it — and the test reads it. The table's own rows are exempt: the test reads the table first and skips those lines. `\bliteratures/` is the first new row; the `_FORBIDDING_LINE` hatch (`:125`) stays for a prose line that names a retired spelling in order to forbid it.
3. **The end-of-line hole.** `following in "*{"` is true for the empty string, so a path that ends its line is never checked (`quality.yml:82` today). It becomes `following and following in "*{"`.
4. **Check 3 stays its own test.** It runs over every tracked Markdown file (`:145-152`), which check 2 does not; it guards a header grammar, not a spelling.

______________________________________________________________________

## 3. Going public and the write-side gate

#130's three questions: a ruleset or branch protection; a developer pre-commit hook; whether invariant 5's hold is permanent. A ruleset on a private repository needs a paid plan this account does not have; the repository will be public in any case, so it goes public now (operator, 2026-09-17).

### 3.1 History first, then visibility, then the ruleset

The history holds two kinds of material the tree no longer does:

- 120 Claude Code session-transcript blobs (the largest ~32 MB) — at `research/raw/knowledge-harness-transcripts/` from `e900dfa`, under `docs/research/raw/` as `knowledge-harness-transcripts/` and later `research-vault-transcripts/` from `ee2c1df`, removed from the tree at `d815463`.
- Eight PDFs, one `.txt` extraction and a `README.md` once tracked under `sources/`.

A scan of every transcript blob for secret-shaped tokens found none. Contributor state (`wiki/`, `.raw/`, `.vault-meta/`) never entered history (`git log --all --diff-filter=A`, empty, 2026-09-17). The first commit touching the paths above is `3719086`; every later commit is renumbered, and both `origin/prototype/*` branches reach the same blobs.

1. **Bundle** the old history (`git bundle create <outside-the-repo>/research-vault-pre-rewrite.bundle --all`) and keep it privately; it resolves any sha the map misses, commit messages included.
2. **Rewrite**, on a fresh clone of the bundle (`git-filter-repo` is in the venv and refuses a non-fresh clone without `--force`), over the paths removed from history:
   `git filter-repo --invert-paths --path research/raw/knowledge-harness-transcripts --path docs/research/raw/knowledge-harness-transcripts --path docs/research/raw/research-vault-transcripts --path sources` — every historical prefix of the removed paths is listed, since filter-repo does not follow renames.
   Verify: `git rev-list --all --objects | grep -c 'transcripts/.*\.jsonl'` is 0 and no `sources/` blob remains.
   Push every ref (`git push --force --all` and `--tags`); the two `prototype/*` branches go with the rest or are deleted on origin.
   Run only when no other session is active: after the push this checkout is reset to the rewritten `main` and its linked worktree `.kilo/worktrees/candle-ski` is re-created. The one irreversible act in the spec; the plan's task says so and asks.
   Request GitHub's purge of unreachable objects; the flip does not wait for it (operator, 2026-09-17).
3. **Commit the map** — `.git/filter-repo/commit-map` becomes `docs/agents/history-rewrite-2026-09-17.tsv` (to be created; old, new, one line each) — and rewrite through it: every sha-shaped token in any tracked text file that resolved before the rewrite (98 in Markdown; `de1867d` at `tests/test_skill_contracts.py:492` only outside it), and every issue body and comment citing one (35 issues; tokens the map has no entry for — run ids, transcript hashes, foreign shas — are left alone). The same pass sweeps the old-slug URLs (§9.2). Commit messages keep their old shas.
4. **Flip visibility** after two assertions: nothing tracked under root `wiki/`, `.raw/`, `.vault-meta/` (§3.2); `LICENSE` present (MIT).
5. **Create the ruleset** (§3.3), last — after the renamed `quality` job has reported on `main` (§10 step 1).

### 3.2 The product boundary, restated as a mechanism

`AGENTS.md`'s "Product and vault boundaries" section keeps its job — vault rules and conventions govern a user vault, not this tree — and every bullet stating it; its purpose line landed on 2026-09-17. One sentence's mechanism changes: "a public default branch is populated from a distribution-clean artifact, never by pushing contributor-vault state" becomes *This repository is public. Root `wiki/`, `.raw/` and `.vault-meta/` are ignored and a test asserts they are untracked; `sources/` stays ignored.* `.gitignore` gains the three roots; the test asserts `git ls-files` returns nothing under them.

### 3.3 The ruleset

One `gh api -X POST repos/{owner}/{repo}/rulesets`: `target: branch`, `conditions.ref_name.include: ["~DEFAULT_BRANCH"]`, `enforcement: active`, no bypass actors; rules `required_status_checks` with context `quality` (integration id 15368; `strict_required_status_checks_policy: false`, which concerns pull requests only), `non_fast_forward`, `deletion`. With no bypass actor the owner is bound like everyone. GitHub's rule text: a direct push succeeds when the sha already carries the passing check — "commits must first be pushed to another ref where the checks pass".

### 3.4 #125 — `quality.yml`: trigger, job split, done-when

The gate diffs `origin/main...HEAD`, empty on every push to `main`; and `on.push.branches: [main]` (`:5-6`) means a branch push starts no run at all. Two changes:

- **Trigger.** `push:` loses its filter; `pull_request:` goes; `workflow_dispatch` and the schedule stay. `concurrency.cancel-in-progress` (`:12-14`) becomes true for every ref except `main`.
- **Job split.** `quality` — form and lint, the offline suite, CRAP — is the required context, renamed from "dev-quality lane (advisory)" (`:19`); it reports in ~4 min, which is why a landing does not wait for the gate. `mutation-gate` is its own job, `needs: quality`, not required, running the gate as today and reporting. Its `timeout-minutes` and §3.9's `--time-budget` both read one repository variable, `vars.MUTATION_GATE_TIMEOUT_MINUTES` (`gh variable set` once): `jobs.<id>.timeout-minutes` accepts `vars`, not `env`. The comments at `:10-11` and `:96-100` say what now fires the gate.

**Done when** a `push` run on a branch other than `main` shows, in the gate job's log, `[gate] N mutants across M changed modules …`, one `[gate] <module>` line per module and a verdict — `pass` or `FAIL`. Not done: `no changed research_vault modules; pass` or `not measured`. The first branch of §10 step 4 that touches a module is the observation, and `FAIL` satisfies it: until the blanket run every relocated key reads as a new survivor by construction.

### 3.5 `AGENTS.md`'s Git line

`:25` becomes: *Push the branch; when its required check is green, `git merge --ff-only` it into `main` and push. A `--no-ff` merge mints a sha no check has run on and the push is refused; a branch behind `main` cannot fast-forward — rebase, push the branch again, wait again. Fetch before claiming something is absent from the remote.*

### 3.6 The other two dispositions #130 asked for

No developer pre-commit hook: `.pre-commit-config.yaml:3-6` already rules `pre-commit run` unsafe in this shared checkout (it stashes across every worktree), and the required check is now the gate. The hold on invariant 5 is not permanent — §3.7. The assembly spec's `:573` and `:579` carry a dated "settled by" sentence (§11).

### 3.7 Invariant 5

Ingest spec `:55` holds the pre-commit leg "until the write-side gate is settled"; that trigger fires today. Amendment at `:55`, `:190` and `:495`, dated 2026-09-17: *The write-side gate settled on 2026-09-17 (`2026-09-17-pre-lane-2-design.md` §3). The leg stays held: binding it costs a running Zotero at every commit for every consumer vault (ingest spec §6), for the substrate-absence question ingest spec §0 defers. New trigger: lane 5's gap pass, which revisits substrate absence together with two-way sync.*

### 3.8 #133 — the gate refuses a dirty tree

**Finding.** Gate mode selects modules from `git diff --name-only --relative <base>...HEAD -- research_vault/*.py` (`changed_modules`, `scripts/mutation_gate.py:366-393`), so an uncommitted change measures nothing and reads as a pass — while mutmut copies and `_tree_digest` hashes the working tree, so the gate selects from commits and measures the tree. `_update_baseline` (`:748-810`) has the same exposure.

**Design.** One helper, `_refuse_dirty_tree(cwd)`: `git status --porcelain -- research_vault tests`; any output raises a `GateAbortError` subclass naming the paths — *commit first — the gate selects from `<base>...HEAD` and measures the working tree*. `changed_modules` calls it first; `_update_baseline` calls it before its first measurement. Inside `changed_modules` because (1) fourteen tests (fifteen call sites) already fake that seam, (2) `test_mutation_gate.py:1652`'s `calls == []` keeps holding, (3) under the gate the script runs from `mutants/`, its own repository with no commits, where a real status call would report every file untracked. `_gate` passes `ROOT` explicitly (`changed_modules(base, ROOT)`), as `_measure` does, so a test can point the check at a temporary repository. The header (`:6-8`) states the select-from-commits, measure-the-tree fact; the Part B plan's `:35` gets a dated "closed by #133" suffix.

**Pins.** A tmp repository (the `:381-402` shape) with `A = 2` staged over a committed `A = 1` raises the refusal naming the path; the same through `main()` exits 1 with the `[gate] ABORT:` line; `--update-baseline` against the same tree refuses; `:405-424`'s empty-repository abort message is unchanged.

### 3.9 #132 — a time budget beside the count budget

**Finding.** `--max-mutants 9000` is the only budget (`_over_budget`, `:822-841`); a slow multi-module set can exceed the job timeout, which reads as failure rather than "not measured". The issue's premise is off by one layer: mutmut's stats file (`save_stats`, `__main__.py:1156-1171`) holds `duration_by_test` and `tests_by_mangled_function_name`, and the per-mutant estimate is computed inside the fork loop (`:1450-1452`, before `os.fork()` at `:1472`; the same sum is `estimated_worst_case_time`, `:1300-1302`). `_run_mutmut` generates, runs the stats phase and forks every mutant of a module before it returns, so nothing gate-side can see an estimate before the first module is measured; the launcher-side alternative patches a private mutmut function a version bump renames silently.

**Design.** Gate-side; the first module is measured regardless, and that is enough: no single module approaches the timeout (the largest, `verify.py`, 1,719 mutants, is under seventy minutes at the slowest measured rate), so a one-module set is bounded by the count budget and the timeout risk is the multi-module set. Steps: (1) after the first `_run_mutmut` returns, read `mutants/mutmut-stats.json`; (2) for each remaining changed module map its mutants (`mm.mutate_file_contents(...).mutant_names`, `get_mutant_name`, `mangled_name_from_mutant_name` at `__main__.py:569`) to the functions' test sets; (3) sum `duration_by_test`, divide by `--max-children`, add the fixed per-module cost measured on run 34827110718; (4) subtract the wall clock since the gate's own start; (5) compare with `--time-budget <seconds>`; on overrun print the first module's verdict line, then `[gate] not measured: estimated <m> min for <k> remaining modules exceeds the <n> min left of the time budget`, and exit with the first module's verdict code — a FAIL found is a FAIL, otherwise 0. `mutation-gate`'s first step records `JOB_START=$(date +%s)`; the gate step passes `--time-budget $((T*60 - ($(date +%s) - JOB_START)))` with `T` = `${{ vars.MUTATION_GATE_TIMEOUT_MINUTES }}`; the gate never reads the environment. `workflow_dispatch` gains an optional `time_budget` input that replaces the computed value. The count budget stays first — it refuses before generation. The header's budget paragraph (`:121-137`) documents both budgets and their order, and its "34 modules" becomes the post-cut count.

**Pins.** A fabricated stats file (shape from `__main__.py:1156-1171`) through the `_fake_measurement` seam: the refusal after module one, the exit code following its verdict, no further launch; the pass-through; the flag's argparse shape (`:1695-1714`). **Done when** a `workflow_dispatch` on a branch touching two modules with `time_budget: 60` refuses after the first module.

______________________________________________________________________

## 4. The rename batch and the module cuts

In execution order. Every piece relocates `mutation-baseline.txt` keys, changes a key's diff text in place, or rewrites the same template line; the blanket run (§10) measures all of it once.

### 4.1 #142 — `literatures/` → `literature/`

**Finding.** "Literature" is uncountable; the directory is `literature/` (operator, 2026-09-16).

**Design.** Everywhere the word is spelled, dated records included — 72 files, 623 lines, of which:

- thirteen modules, not the seven the issue names: also `structure.py:29` (`_FOLDER_TYPES`; key and value coincide afterwards), `checks.py:160`, `factcheck.py:77,94`, `lifecycle.py:143`, `compile.py:93`, `gitstate.py:643` (a bytes prefix); plus `hooks/pretooluse_guard.py:11`, `hooks/posttooluse_lint.py:97`;
- the template files `AGENTS.md:7,9`, `index.md:6`, `editorconfig:1,33`, `markdownlintignore:7`, `prettierignore:7` (the directory itself is created by `scaffold.py:15-22,27`);
- five baseline keys whose diff text carries the literal, changed in place: `propagate.py::func/_sources` (`:1316`), four `verify.py::func/_plan_state` (`:2115-2118`);
- three test function names; 167 lines in dated plans and research records.

`\bliteratures/` is the first row of terminology.md's retired-spellings table (§2.2). `skills/setup-vault/SKILL.md` gains a "rename by hand" section (its migration section went in `4df5e95`), phrased with a hatch token. **The old-vault mechanism:** doctor's `tree` probe (`scaffold.py:351-361`) would otherwise create an empty `literature/` beside a populated `literatures/` and report MATCHED; it gains a row that fires whenever `literatures/` exists — `UNMATCHED — stray literatures/: rename to literature/ by hand, then run capture --all` — and the scaffold-inside-doctor does not create the new root while the old one exists.

**Pins.** The seven byte-pin sites (`test_templates.py:88, :125-128, :213`; `test_scaffold.py:15, :31, :97, :199`) re-pinned; doctor tests with `literatures/` alone and with both directories; the deny-list firing on a stray `literatures/` in a prose surface.

### 4.2 #25 — the template roster

**Finding.** `templates/vault/AGENTS.md:7` names six machine-written surfaces and omits `system/bibliography.json`, which the guard denies; line 31 says Better BibTeX is the file's sole writer, false since capture regenerates it (`capture.py:288`; `CONTEXT.md:40`). Nine re-pins since filing carried neither edit.

**Design.** Line 7 gains `system/bibliography.json`; line 31 becomes *capture is the sole writer of the CSL file `system/bibliography.json`, rendered from Better BibTeX; users and other tools must not write it.* Mechanism: `tests/test_templates.py` derives the line-7 roster from `hooks/pretooluse_guard.py`'s three constants (`:11`, `:14`, `:18-24`) minus `wiki/` (its own sentence at `:29`) and asserts the template names each. Rides #142's template commit and its re-pin of `:122-161`; the comment at `:112-114` ("six"), `:207-208` ("Better BibTeX's export") and `tests/test_config_validity.py:47` ("BBT-owned") follow.

### 4.3 #134 — `notes.py` → `literature_notes.py`

**Finding.** The module is the literature-note record; the generic name says nothing.

**Design.** `git mv` the module and `tests/test_notes.py`; every reference follows, no alias: nine source importers (`__main__.py:20`, `capture.py:22`, `captured.py:13`, `compile.py:17`, `lifecycle.py:13`, `lints.py:13`, `propagate.py:23`, `quotes.py:7`, `verify.py:30`), 164 `notes.X` references (49 source, 115 tests), ten other test files, `tests/test_config_validity.py:677`'s literal, `skills/project-flow/SKILL.md:48`, ingest spec `:141,:145,:146,:486,:503`, the module's self-references at `:24-25` and `:30-31`, and 60 occurrences in dated records under `docs/superpowers/plans/`, `docs/research/` and `docs/product-landscape/`. First underscored module name in the package: the domain term (`CONTEXT.md:20`) wins. Keys: 32 relocate; seven of other modules change text in place with the import — `lifecycle.py::func/_provenances` ×2 (`:1101-1102`), `lints.py::func/_body_bytes`, `::_machine_attested`, `::lint_evidence_layer` (`:1108`, `:1148`, `:1200`), `verify.py::func/_note_bytes` ×2 (`:2067-2068`). This spec's own citations are rewritten by the same sweep; this heading keeps the old name.

### 4.4 #131 item 1 — the hook install is contained

**Finding.** `scaffold_vault` installs the vault pre-commit hook at whatever `git rev-parse --git-path` answers for it (`_git_path`, `scaffold.py:189-192`; install at `:250-255`): a linked worktree of another repository, a gitfile pointing elsewhere, or a `core.hooksPath` setting all put the hook in a foreign directory (measured 2026-09-17, git 2.43.0), and a mutant with a non-vault argument once wrote it into this repository's `.git/hooks`. `tests/test_scaffold.py:340-353` pins the linked-worktree case as a success; the toplevel refusal (`:148-149`) has no test.

**Design.** Eliminate, then guard. The hook path is the literal `vault / ".git" / "hooks" / "pre-commit"`; `_git_path` goes. `_prepare_repository` gains two refusals, both `ValueError`s in the shape of the toplevel refusal: (1) a destination whose `git rev-parse --git-common-dir` (absolute) is not `(vault / ".git").resolve()` — naming both paths; (2) a set `core.hooksPath` (`git config --get core.hooksPath`) — naming the configured directory and the literal, since nothing now reads where git would resolve the hook.

**Pins.** `:340-353` inverts into the linked-worktree refusal; gitfile-elsewhere, hooksPath and missing-parent-directory cases added (the `mkdir(parents=…)` keys at `mutation-baseline.txt:1596-1598` are observable only there); `:191-196`, `:218-233` keep the plain vault; the toplevel refusal gets its test. Of `_prepare_repository`'s fourteen keys, ten die to the refusals, three to the missing-parent case, and the `init -q` drop (`:1594`) is reasoned.

### 4.5 The three cuts

**Finding** (#129 rows 46, 51 and the module-cuts item). `scaffold.py` (691 lines) mixes scaffolding with thirteen doctor probes; `capture.py` (663) owns the credential store; `verify.py` (1,247) carries the marker writer. A move re-keys every survivor of the moved functions.

**`doctor.py`.** Scaffolding is `:1-274` (`Probe` `:33-38`, `scaffold_vault` `:223-273`); the doctor half is `:276-691` and calls only `scaffold_vault`, `VAULT_DIRS`, `_git` from the other side. `Probe` moves with it. Followers: `tests/test_config_validity.py:141,171,177`; `tests/test_doctor.py:65,306,870,918,927` (`_installed_plugins` patch targets), `:172` (`scaffold.__file__`), `:921,928`, and ~50 other `scaffold.<name>` references; `__main__.py:32`; `compile.py:73`; `tests/test_scaffold.py:625-642`; `tests/test_okf.py:79`; the assembly spec's `scaffold.py … doctor()` mentions at `:82,:379,:494,:575`; `structure.py:186`'s docstring. 128 of 174 keys relocate.

**`keystore.py`.** `KEY_STORE` `:544`, `_load_key` `:565-570`, `_store_key` `:573-587`; callers `add()` at `:621,:634`. `capture` imports the three names so `tests/test_add.py:366`'s patch target survives; `tests/test_capture.py:1444,1447` move. 16 keys relocate. Row 47's fixes (§7.2) land here.

**`markers.py`.** *What moves:* the block `verify.py:592-750` (`_mutate_marker`, `_cites`, `_claim_notes`, `clear_marker_for`, `_terminal_marker_pattern`, `_terminal_anchor_match`, `_split_line_ending`) and the helpers it needs, so that `verify` imports from `markers` and no cycle forms — `_origins` (`:569-589`), `_safe_relative` (`:102-114`), `_read_note_text`/`_write_note_text` (`:62-69`), `_without_own_marks` with `_OWN_MARK` and `_ANY_VERIFY_MARKER` (`:45-59`). *What stays:* `CLOSING_CHECKS`; its guard at `:593` moves to the call site `_apply_state_transitions` (`:896-898`). *Followers:* `__main__.py:33-40`; `publish.py:30-31`; `tests/test_verify_cli.py:27-36`, `:2555`, `:2708`, `:3183-3197`, `:3254`. *Closed inside the cut:* row 54 — one `_rewrite_marker_lines(path, check, matcher, *, clear, first_only)` under both `_mutate_marker` (first matching line, then stop) and `clear_marker_for` (every matching line, track `changed`); row 55(b) — `_mutate_marker`'s `wiki/` guard (`:599`) roots on `gitstate._root_bytes` as `clear_marker_for` does (`:674-677`). *Keys:* 29 relocate (`_mutate_marker` 5, `clear_marker_for` 6, `_origins` 4, `_safe_relative` 4, `_read_note_text` 4, `_write_note_text` 5, `_split_line_ending` 1).

______________________________________________________________________

## 5. The frontmatter screen and the duplicate-key guard

### 5.1 #136 — sourcing screen: python-frontmatter versus `research_vault/frontmatter.py`

**The bounded question.** Does a library give every guarantee the vault's readers and writers depend on, so that `frontmatter.py` (182 lines, stdlib `re` only, 15 importers, 27 baseline keys) can be deleted? There is no zero-dependency rule; `docs/agents/sourcing.md:27` governs — a library by default, in-tree only when the contract mismatch can be named.

**The musts**, with the pin at `HEAD` or the recorded gap, and the consumer:

| #   | Must                                                                                                                             | Pinned by                                                                                                    | Depended on by                                                                                                                       |
| --- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| M1  | A duplicated top-level key is observable after parse                                                                             | `test_notes.py:104-116`; `test_stamp.py:43-52`                                                               | `notes.validate_managed_witness` (`:118-127`); `stamp.py:114`                                                                        |
| M2  | A duplicated key inside an inline `{…}` mapping fails closed                                                                     | `test_frontmatter.py:90-99`; `test_events.py:458-486`; `test_notes.py:278-330`                               | `events.py:49,89`; `notes.py:177`                                                                                                    |
| M3  | The body is returned byte-for-byte — no strip, CRLF kept                                                                         | `test_frontmatter.py:41-48`; `test_notes.py:235`; `test_events.py:60-84`                                     | the `managed-sha256` witness (`notes.py:98-131`); `render_note` (`:502`)                                                             |
| M4  | `serialize(parse(x))` is byte-identical for serializer-emitted text; `serialize()` lines splice lexically into an existing block | gap — only dict round trips and line spellings (`test_frontmatter.py:19-33,51-87,114-165`)                   | `render_note`'s `unchanged` test (`:486-491`); `events.py:167-215`; `stamp.py:120`                                                   |
| M5  | Key order: source order on parse, insertion order on dump                                                                        | `test_notes.py:416-445`; gap — the order-exact header comparison (`test_inbox.py:99-114` pins presence only) | `inbox.py:278`; `searchlog.py:100`; `notes.py:475,507`                                                                               |
| M6  | An unterminated block raises, never reads as "no frontmatter"                                                                    | `test_notes.py:74-77`                                                                                        | `stamp.py:90-92` (`unparseable`); `captured.py:55-59`, `lints.py:91-96,577-588` (fail closed); `publish.py:138-140` (skips the file) |
| M7  | No YAML 1.1 coercion of unquoted scalars; control characters refused on write                                                    | `test_frontmatter.py:75-87`; `test_render_neutralization.py:47-76`; gap — `_parse_scalar` has no direct test | `notes.py:120-129,174-183`; `events.py:47-55`                                                                                        |
| M8  | The boundary grammar is exact and shared with the byte-surgical writers (`----`, `---  ` are not boundaries)                     | gap — no test feeds either                                                                                   | `notes.py:155-158`; `events.py:172,180-191`; `stamp.py:38-39,122`                                                                    |

**Candidate: python-frontmatter 1.3.0** — 2026-05-20, three days after 1.2.0 ended a 28-month gap; single maintainer; one dependency, PyYAML, unpinned. Measured 2026-09-17 from source at `dc7c0af` against this venv's PyYAML 6.0.3: fails M1 (`handler.load(fm)` feeds `metadata.update`, `__init__.py:93-95`; PyYAML's `BaseConstructor.construct_mapping` is `mapping[key] = value`, `constructor.py:144`), M2 (a plain `dict` with the repeat collapsed), M3 (`\r\n` → `\n` at `util.py:30`; `strip()` at `__init__.py:75,97`), M4 (quotes dropped, date-like strings single-quoted, list indent and inline mappings reformatted, trailing newline dropped; upstream issues #87, #117), M5 on dump (`sort_keys=True` default, not overridden), M6 (the split's `ValueError` is caught and returns `(defaults, text)`), M7 (SafeLoader coerces `no`, dates, `1.0`, `0x1f`), M8 (`FM_BOUNDARY = ^-{3,}\s*$`). Every conflict is either in the library's own hundred lines over PyYAML or in SafeLoader's semantics. Gate-path cost avoided: `import yaml` ≈13 ms per hook invocation.

**Excluded.** PyYAML direct — same M1, M4, M5, M7. ruamel.yaml `rt` — raises on duplicates and keeps order, but not byte-equal to this grammar, and no document splitter. strictyaml — rejects flow-style `{…}` mappings (from its documentation). mdit-py-plugins `front_matter` — a splitter, no parser. mdformat-frontmatter — a formatter.

**Verdict: `build`, keep in-tree.** Tier: mature tool. `floor_failed`: M3 (any of M1, M4, M6, M8 alone would do). **The exit** (`docs/agents/sourcing.md`): delete `frontmatter.py` and every note on disk is still a strict subset of YAML — `---`-fenced, quoted scalars, two-space-indented `-` list items, `{k: v}` flow maps — that PyYAML, ruamel and Obsidian read. The four gaps in the table (M4, M5, M7, M8) each get a test in the plan.

### 5.2 #20 — a duplicated machine-owned key is a schema violation

**Finding.** `lints._frontmatter_attestation_outcomes` (`:650-676`), `_write_attested` (`:613-630`) and the added-note leg (`:733`) read frontmatter through `data.get(key)`, which is last-key-wins, over `CAPTURE_FIELDS` (29 keys, `notes.py:64-68`, aliased at `lints.py:570`). Four shapes evade at `HEAD`:

- candidate `citationKey: "evil"` then `citationKey: "smith2020"` (equals base) — no finding;
- a duplicated `generated`, human-first machine-last, with a bumped `at` and an altered key — attested;
- a duplicated `generated` whose last copy equals base — no finding;
- the same on the added-note leg.

Only `validate_managed_witness` counts occurrences (`notes.py:118-126`). `render_note` emits each capture key once and keeps human duplicates, so a base with a duplicate that capture re-renders is the attested cleaning path — provided the guard is candidate-side; a base-side guard would turn that cleaning into the unparseable-base drift set `test_lints.py:1140-1163` pins.

**Design.** `literature_notes.duplicate_capture_fields(data) -> list[str]`: every key in `CAPTURE_FIELDS` occurring more than once in `frontmatter._mapping_items(data)`, sorted — a future writer field inherits coverage. It runs per candidate file in `lint_evidence_layer`'s first loop (`lints.py:699-704`), covering the added, renamed and surviving legs. One `UNMATCHED schema-violation — duplicate <key>` row per key; the drift comparison is skipped for a file with any such row. Candidate-side only; human-owned duplicates stay legal.

**Pins.** Order reversal; equal final value; duplicate `generated` on the surviving and the added leg; the cleaning case (`base` duplicated, capture-rendered candidate → `[]`); `test_lints.py:653-697` and `:1085-1163` unchanged. Tests derive the key sample from `CAPTURE_FIELDS`.

______________________________________________________________________

## 6. The survivor triage

#131 items 2 and 3.

**Finding.** Item 2 names 50 in-scope survivors across thirteen `verify.py` functions; item 3, 82 behaviour survivors across eight Part A modules — both to be killed or "recorded in the results file's accepted list". At `HEAD` the thirteen functions hold 267 keys and the eight modules 159 (addons 10, capture 51, captured 20, clock 1, lifecycle 8, paths 8, propagate 52, stamp 9); the file marks no subset, and the accepted list never existed in any committed file (the results file says it was in a task report that was never committed). Item 4 of the 2026-09-14 comment (the `no tests` set) is outside the baseline and filed onward (§11).

**Eight dead keys.** `mutation-baseline.txt:1119-1126` are `lints.py::func/_frontmatter_attestation_outcomes` keys whose `-` text moved into `_write_attested` at `72fea9c`; the baseline can hold dead keys undetected (`scripts/mutation_gate.py:89-92` warns of the class). The blanket run drops them; their disappearance is expected, not a kill.

### 6.1 Where a reason lives

The file has no slot: `baseline_keys` (`:346-353`) reads every non-`#` line verbatim; `new_survivors` is `found - baseline` (`:342-343`); `_update_baseline` (`:800-805`) rewrites header plus sorted keys, and its header wording still reads "every research_vault module measured by …" where `mutation-baseline.txt:1` was reworded by `4df5e95` — the writer changes first or the blanket run reverts that edit. An issue comment leaves reasoned and unreasoned keys indistinguishable in the file; a sidecar goes stale silently.

**Chosen.** A `# reason: <text>` line immediately preceding its key. `baseline_keys` keeps skipping `#` lines (`test_mutation_gate.py:364-378` holds); `baseline_reasons(path) -> dict[str, str]` pairs each reason with the key that follows it and refuses a dangling one. After a run a reason's key is in one of three states: generated and surviving — re-emitted above it; generated and killed — dropped, correctly; not generated at all, because no mutant of the run carries that relpath and diff text — reported on stderr as `[baseline] reason not re-attached: <key>`. The third is the case a cut or rename produces when the reason sits above the old spelling. The header documents the format.

**Pins.** The three states; a dangling reason is an error; the six `baseline_keys(baseline_path) == <expected set>` assertions (`:1070-1385`) hold.

### 6.2 What is dispositioned

Every key of the thirteen functions and the eight modules: a kill or a reason. Reason text names its class — one of #42's three rulings (prose to a human; docstring; never-read-back literal) or Task 25's two largest accepted groups (encoding alias; locale default). Roughly seventy-five of the 159 module keys are codec/errors/newline keyword mutants and read in seconds. `captured._structural`'s `[:10] → [:11]` (`captured.py:273`) gets back the reason Plan W recorded and lost: the fixtures' first ten characters agree.

**Kills already located:**

- `_identifier_hash` (`:2000-2041`): three fixtures — the bibliography-entry branch with an out-of-order entry pinned to a `hexdigest()[:16]` literal (kills `sort_keys`); a witness-less note reached through `origin` and through `origin_image`, each pinned to `sha256(_note_bytes(...)).hexdigest()[:16]`; a deleted note with a `note_path` reached through `base_snapshot` (the `[:17]` at `:2018`). Together they kill the `[:17]` at `:2035`, one key text shared by `verify.py:467,470,494`. `test_verify_cli.py:381-387` stays the `is not None` pin.
- `_plan_state` (`:2074-2127`): five of six through `verify_state` with a fixture whose counts, DOI presence and `repository_root` each change the rows; the `network=True` default (`:2114`) is never read — a direct `_plan_state` call, or a reason.
- `_candidate_destinations_match_live` (`:1885-1894`): the product caller is `verify_state` (`:1193`); a worktree candidate cannot reach either shape (the function returns first on `candidate_name == "worktree"`), so use an index candidate (`gitstate.resolve_snapshots(net_vault, candidate="index")`, as `tests/test_gitstate.py:105`) with a worktree that differs from the index at a planned output path, asserting the `selected candidate differs from live projection destination` refusal.
- `_network_outcomes` (`:2047-2064`): the only direct test call (`:2394`) passes `notice_lookup=None`; add one with a lookup.
- `verify_state` (`:2218`): pin the `network` default's observable effect.
- `captured._aliases` (`:199-208`, nine `data.get` mutants and `names.add(None)`): a note with `title` and `aliases` both absent and both present.
- `propagate.plan` (`:1335-1337`, `strftime`/`datetime.now(None)`); `_mapping_from_linter` (`:1313-1315`, `split(" → ", 1)`); `lifecycle.replaces_keys` (`:1105-1107`, three `rsplit` shapes); `paths._running_in_wsl` (`:1304-1305`, two env-name mutants); `scaffold._prepare_repository` (`:1594-1607`) per §4.4.

The file holds pre-move spellings until the blanket run and decision 30 forbids an interim write, so the triage writes each reason above a key line hand-spelled with the post-cut relpath and post-rename diff text; §6.1's report catches any it misses.

______________________________________________________________________

## 7. Verify, capture and scaffold hygiene

"Row NN", "Residual 1–3", "I-1" and "the double hold" are #129's register rows and its dated comments.

### 7.1 Three design changes

**Row 45 — a POSIX `file:///` URL in the path-shim probe.** `scaffold.py:589` strips `file:///`, turns `/` into `\`, and `paths.to_local` (`:49-62`) hands the result to `wslpath -u`, which answers a relative `home/…` path with exit 0 — the reason string is mangled; the UNMATCHED verdict is right. **Design.** Keep the Part A plan's decision 10. A URL whose path has no drive letter is reported `SKIPPED — file URL is not a Windows path; the shim resolves Windows file URLs only: <raw url>`, unwound by nothing. One dated sentence at ingest spec `:241`; one test beside `test_doctor.py:685-697`.

**Residual 3 — a nested directory under `literature/`.** `verify.py:1057-1062` walks the vault and `structure.check_note_frontmatter` types each file by folder, so `literature/older/x.md` gets one `okf-frontmatter MATCHED` row while every literature reader ignores it (flat since `e37296b`). **Design.** The walker stays. `structure.check_tree` returns a list — the existing tree row plus one `UNMATCHED — literature/ is flat: literature/<dir>/` row per stray directory; `verify.py:1064` extends; the id stays `tree`. `test_verify_cli.py:3223-3264`'s `okf-frontmatter` assertion (`:3259-3263`) gains the row.

**I-1 — the identity-based refusal.** `_refused` (`capture.py:375-403`) refuses a re-keyed item only while `literature/<old>.md` exists, and steps aside (`:393-398`) when the recorded old key is unrepresentable, so a hand-edited note recording `../escape` gets a second note beside it; its `is_file()` (`:399`) runs before the per-item `try` (`:483`), so a `PermissionError` on the directory is a vault-wide exit 2 (residual 2). `capture()` already computes `existing = lifecycle._provenances(vault)` (`:433`) — the `(path, provenance)` pairs whose recorded key is the Part A plan's decision 08 identity, as `propagate._sources` (`:98-142`) uses it. **Design.** `_refused(vault, prior, requested_key, existing, new)` refuses when any entry of `existing` recording `old` has a path other than `note_path(vault, new)`; the step-aside and the `is_file()` go, closing residual 2. `tests/test_capture.py:860-879` inverts from MATCHED to the refusal; `:746-790` keeps the reason string and the one-hold assertion. #146 is not pre-empted: this changes when capture refuses, not what a re-key propagates.

### 7.2 #129 — the remaining rows and items

**Row 21 — exact-case header reads.** `zotero.py:159-163` builds a plain dict; readers at `:234`, `:244-247`, `:358` and `scaffold.py:552` look up exact-case. **Design.** One case-insensitive helper at the four sites; the fakes (23 literal registrations across six test files) untouched; one test feeds a lower-cased header.

**Row 24 — CLI and test hygiene.** (1) The five `getattr(args, …, DEFAULT)` fallbacks at `__main__.py:283-287` are dead for the CLI (`main()` sets `base` at `:889-893`, argparse the rest at `:796-801`) and live only for nine direct `cmd_verify(...)` callers in `tests/test_verify_cli.py` (`:874, :900, :935, :1006, :1332, :1572, :1615, :1651, :1954`) that build an ad-hoc `Args` object: the fallbacks go, the nine objects gain the attributes through a shared helper. (2) The dead-port test — fixed at `f2afa2d`. (3) `assert fake.calls == []` at `test_zotero.py:238-245`; the row's second target could not be resolved at any filing-era tree. (4) `FakeZotero._rpc_call`'s unregistered-method raise becomes `Result.UNMATCHED` (`fakes.py:70`, mirroring `zotero.py:476`); `test_doctor.py:434-435`'s comment follows. (5) Fixture ids — closed on the Part B plan's ruling (`b-compile.md:31`).

**Row 25 — `fulltext.verdict` labels** (`fulltext.py:31-46`, `_render`). The neither-pair case reads `malformed — indexedPages/indexedChars pair missing`; `indexed > total` reads `malformed — indexed exceeds total` with `usable` unchanged; `_render` guards a non-numeric value with the same label. Quirk 3 (the "empty" label) does not match the code, which has carried the length since `fee77c3`. Three pins in `tests/test_fulltext.py`.

**Row 41.** `tests/test_capture.py:305-312` snapshots every file's bytes after the first capture and asserts equality after the second.

**Row 11 — closed on evidence:** `tests/test_structure.py:144-166` already scaffolds with `scaffold_vault` and runs `verify_state` over the result. **Row 43 — closed on evidence:** fixed at `741516c` (`tests/test_scaffold.py:608-642`).

**Row 44 — four doctor branches.** Tests in `tests/test_doctor.py` for a required add-on that is `inactive` (`scaffold.py:493-500`), `write-guard` UNREACHABLE on a transport failure (`:398-409`), a non-numeric `Total-Results` (`:551-555`), and `attachment listing malformed: expected a list` (`:545-549`); about 24 survivors die with them, read under `doctor.py`'s relpath.

**Row 47 — key-store hygiene** (in `keystore.py`). (a) An unparseable store (`capture.py:576-581`) is renamed aside to `zotero-keys.json.bad-<utc timestamp>` with one stderr line, then written; `tests/test_add.py:148-160` holds. (b) The 401 branch (`:621-644`) deletes the rejected server id's entry before the re-grant, tolerating an absent store (`test_add.py:307-329`); one test with a 401 then `remember: false`.

**Rows 54 and 55(b)** — closed inside the `markers.py` cut (§4.5).

**Row 55(a) — the tab-terminated claim.** `claims.ANCHOR_RE` (`:10`) needs no whitespace before `^`, so the writer (`verify.py:619-625`) produces `…\t[marker] ^id`, which `_terminal_marker_pattern` (`:730-736`) and `_without_own_marks` (`:48-59`) never find. **Design.** The readers accept `[ \t]+` before the marker. The writer stays: normalising its output would change the claim's own bytes under a stamp — `_note_bytes` (`:123-126`) and `_claim_bytes_from_text` (`:141`) strip only the marker — so an acknowledgment's scope hash would move the moment verify stamped, breaking the "invariant under the tool's own stamp and clear" contract (`:52-58`) and `test_verify_cli.py:1174-1178`. A tab-terminated case is added beside `:1202`.

**Row 56.** (a) `test_correction_ack_does_not_suppress_same_hash_blocking_retraction` (`:1558-1667`) lost its "nothing else open" pin when the lifecycle leg began filing an UNREACHABLE row under the socket guard: `_isolate_network_verify` (`:1541-1555`) gains a patch of `lifecycle.lint_lifecycle` to `[]` and the whole-set assertion returns. (b) `:2507` drops its unused `monkeypatch`. (c) The two spelling-bound guards (`test_config_validity.py:638-649`, `:652-690`) stay as designed.

**Residual 1 — a `null` row in `lifecycle.read_live`.** `:53` guards `data` for a non-mapping item but `:57` runs `item.get("key")` unconditionally. The real client's `_validate_object_list` (`zotero.py:214-222`) refuses the row first, so the guard — `if not isinstance(item, Mapping): continue` — is defence in depth, pinned with a stub client whose `top_items()` returns `[None]`.

**The unguarded reads.** Record reads (a per-target row — `UNREACHABLE outage` for `OSError`, `UNMATCHED schema-violation — not UTF-8` for a decode fault, the `captured.py:37-53` shape — and the walk continues):

- `checks.py:139`; `quotes.py:40,130`; `lints.py:481,502,521`; `factcheck.py:97` (the literature note);
- `propagate.py:436` — `lint_propagation`'s read of every surface, each with its own `stale-key` row;
- `stamp.py:87` (`_read_text`, `open`-based); `stamp_types` is reached from `capture.py:534`, `publish.py:415` and `__main__.py:735` — the last, `cmd_stamp_type`, has no `_NAMED_FAILURES` wrapper at all;
- `_read_note_text` (`verify.py:62-64`, in `markers.py` after the cut), guarded once for its callers `verify.py:603,698` and `publish.py:373,467,479`; `capture.py:187`.

Run-input reads (exit 2 naming the path): `factcheck.py:67,112` (the draft), `inbox.py:271`, `searchlog.py:93`, `paths.py:46` (`load_machine_config`, guarded at the function so all four callers agree), `addons.py:26-30` (the packaged `zotero-addons.md`). `encoding="utf-8"` is added where a call has none; the stopgap comment at `__main__.py:65-67` and the `UnicodeDecodeError` entry at `:77` retire. One test per guarded site.

**`_worktree_path_hash`** (`verify.py:379-421`) is reached only from `_repo_path_hash`'s `None` branch (`:432-436`), and the one production caller always passes a candidate snapshot. **Design.** Delete the leg and that branch; `candidate_snapshot` stays optional so `_citation_key_hash` and `_claim_anchor_hash` are not stranded. Of the 54 `_target_hash(` test calls without a candidate snapshot, six are in the three leg-only tests (`:2958-3000`) that go; the other 48 gain a snapshot fixture (`gitstate.snapshot_worktree(net_vault)` as `:281`/`:314`). Eleven keys are deleted; the one `_repo_path_hash` key sits on the retained call and stays.

**The double hold.** `_regenerate_csl` (`capture.py:243-293`) exports every recorded key, the refused old key included, so a refused re-keyed item files a second `not-admitted` hold on the CSL file. `capture()` collects the keys it refused as `re-keyed` and the export skips them; `_re_keyed_fake` (`test_capture.py:724`) raises -32602 for the old key so `:770-774` can see a second hold if one returns.

**`--base` on the printed `apply with:` line.** `__main__.py:240-243` and the compile sibling `:381-384` echo `--base {args.base}`; `tests/test_propagate.py:289-298` parses by token; one assertion per line.

### 7.3 #107 — `stamp_types(paths=…)` escapes through a symlinked ancestor

**Finding.** With explicit paths (`stamp.py:42-47`) only the leaf's `is_symlink()` (`:76-80`) is checked; a real file inside a symlinked directory is rewritten outside the vault (reproduced). An absolute outside path reaches `:83`'s `relative_to` as an uncaught `ValueError`; a `..` path passes the lexical `relative_to` and is reported `no-type`. No production caller passes `paths=`.

**Design.** Resolve, then `resolved.relative_to(vault.resolve())`; a path that fails is reported with a new token `outside` (the `..` and absolute cases become reports); the reported relative string stays the unresolved one (`test_stamp.py:169`). `__main__.py:741-742` gains the line; `stamp.py:20-27` and `test_verify_cli.py:715-719` follow. `paths=` stays for the path-scoping flag the issue anticipates.

### 7.4 #32 — `str.index()` over `.pre-commit-config.yaml`

**Finding.** `tests/test_config_validity.py:378-379` bounds a raw-text slice with the next `- id:`, an opaque `ValueError` if `pyproject-fmt` becomes the last hook; the sibling at `:549-553` already parses YAML but its `(hook,) = (...)` (`:552`) fails a missing or duplicated hook with the same opaque class.

**Design.** `yaml.safe_load`; hooks selected by id with `assert len(found) == 1, f"expected exactly one pyproject-fmt hook, found {len(found)}"`; `shlex`-split flags compared as a set against `PYPROJECT_FMT_FLAGS`; `--table-format` followed by `long` as adjacent tokens. The sibling at `:552` gets the same assertion.

### 7.5 #126 — the OKF pin is written twice

**Finding.** The upstream `SPEC.md` sha256 is a `PINNED:` literal at `quality.yml:144` and a value in ADR 0001; the commit ref `ad30107` is a second literal pair (`quality.yml:151,162`); `ATTRIBUTION.md:30-31` restates both; nothing compares them. The issue's fix — the ADR as writer, the workflow scraping its prose — was withdrawn on the 2026-09-17 counter-argument: (1) an ADR records why and is not meant to change on a schedule, while the pin changes whenever upstream re-stamps; (2) scraping prose for "the sole 64-hex token" relies on a constraint nothing enforces until CI fails; (3) `AGENTS.md` records such a fact where it is used, with method and date.

**Design.** `.github/okf-pin.json` (to be created) — `{"ref": "ad30107", "sha256": "26aa5da0…", "method": "sha256sum of raw SPEC.md at ref", "measured": "<the date the implementer re-runs it>"}` — is the one writer, beside its only consumer. The job reads `ref` and `sha256` with `jq` and builds its title and issue body from them; the three literals go. ADR 0001 keeps the rationale and points at the file; `ATTRIBUTION.md:30-31` keeps its link and points at the file. A test asserts the file's shape (four keys; 64-hex `sha256`; 7–40-hex `ref`; a date), so a hand edit fails on the branch's required check.

______________________________________________________________________

## 8. The skills comparison (#138)

**Record.** Each of the nine research-vault skills was compared in full against all fifteen of the tool's `SKILL.md` files at `32ac5a0` (`autoresearch`, `canvas`, `defuddle`, `obsidian-bases`, `obsidian-markdown`, `save`, `think`, `wiki`, `wiki-cli`, `wiki-fold`, `wiki-ingest`, `wiki-lint`, `wiki-mode`, `wiki-query`, `wiki-retrieve`), 2026-09-17, and the nine comparisons cross-checked in one matrix; the briefs and the matrix are the evidence sibling. A prior audit (deleted at `871e4b1`) had adopted from the tool the routing guard in project-flow and the compilation-value gate in synthesis-conventions (`e76805c`). Every edit is to research-vault's own `skills/*/SKILL.md` and the tests that pin them; the tool stays as ingest spec §4.3 adopted it.

### 8.1 Verdicts

*Adapt*: the skill gains a route to, or names, a tool skill. *Keep*: content stands, prose repaired.

| Skill                   | Verdict | Structural reason                                                                                                                                                                                          | Edits |
| ----------------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- |
| `capture-source`        | adapt   | Four of five sections act on Zotero, `literature/`, `fulltext/`, `system/bibliography.json`, `system/propagations/` — no tool skill touches them; the fifth already hands compile to wiki-ingest.          | 1, 7  |
| `setup-vault`           | adapt   | Scaffold, thirteen doctor probes and the Zotero wizard have no counterpart; its `adopt` paragraph is stronger than the tool's own.                                                                         | 1, 8  |
| `project-flow`          | adapt   | Frames `projects/NAME/draft.md`, drains the review queue, reads `trust-tier`, calls `ack` — none reachable from the tool.                                                                                  | 9     |
| `synthesis-conventions` | keep    | The only model-visible carrier of six facts the tool cannot supply (the 2+-source threshold, `[[<citation key>]]`, `captured-set`, the registration step, the frozen claim currency, the index exemption). | 2     |
| `evidence-conventions`  | keep    | Governs claims under `projects/`; the tool's claim ledger requires `location.path` under `wiki/` (`ledgers.py:973-979`) and its pages carry no citation key.                                               | 5     |
| `verify-citations`      | keep    | The tool's wiki-lint runs none of the checks `verify` reports (four-state, findings file, acknowledgment, network legs).                                                                                   | 4     |
| `factcheck-draft`       | keep    | Reads a draft under `projects/`, which no tool skill opens; frozen pending the workflow-component audit (ingest spec §6 `:493`).                                                                           | 6     |
| `find-sources`          | keep    | Eleven bibliographic databases and the search log; the tool's tree mentions no bibliographic database, DOI or PRISMA.                                                                                      | —     |
| `publish`               | keep    | No tool skill carries a publication lifecycle; `checkpoint` commits one transaction's paths with no status, tag, event, correction or armed hold.                                                          | 3     |

The reason repeats across all nine and is structural: every tool skill is confined by its transaction contract to `wiki/`, `.raw/` and `.vault-meta/` (`setup`/`migration` additionally write the tool's template paths, `.obsidian/` among them — `operation-transactions.md:72-81`), with `inbox/` as its read-staging surface, and the tool has no durable non-blocking finding and no acknowledgment (ingest spec §6 `:481`).

### 8.2 The edits

`tests/test_skill_contracts.py:230-253` treats every backticked kebab token in a skill as a research-vault skill name, so tool skill names stay unbackticked in skill prose — wiki-lint, wiki-query, defuddle, autoresearch, wiki-mode — as `capture-source:74` already writes wiki-ingest.

1. **wiki-lint is routed to by nothing** (`grep -rn wiki-lint skills/ research_vault/templates/ docs/agents/ README.md CONTEXT.md` is empty). Two homes: capture-source §5 after compile — *then run the tool's wiki-lint skill over `wiki/`, then `verify`* — and setup-vault once after `adopt`. Not from verify-citations, which reports one engine's checks.
2. **`synthesis-conventions:24` is false** — orphans do not block the tool's checkpoint (`checkpoint.py:41-49`), and the vault never runs `checkpoint`. Reworded to what the lint reports and what the vault's own gate closes on.
3. **`publish:33` names four closing ids and `:39` "the other two"; `verify.py:85-96` closes the publish surface on nine.** Both say "the publish closing set"; `tests/test_publish.py:916`'s comment follows; `:896` keeps pinning the minting ids.
4. **`verify-citations:9` cites "§6"** of the retired foundation spec; it points at the ingest spec's §6.
5. **`evidence-conventions:16` and `:35-40` carry a hop the vault forbids.** `:16` copies claims "into the compiled layer under `wiki/`"; `:35-40` writes `[confidence::]`, `[supports::]`, `[disputes::]` there. `CONTEXT.md:17` makes `wiki/` the tool's alone, stance links are frozen (`CONTEXT.md:76`), `synthesis-conventions:36` forbids them. `:35-40` goes; `:16` loses the hop.
6. **`factcheck-draft:36-42` reads the literature note's "body"**, which carries no source text (`notes.py:407-437`); the text is `fulltext/<attachment key>.md`. Named; the skill gains the untrusted-content sentence wiki-query (`:11-15`) carries.
7. **`capture-source:74` says "there is no second one"** of the human gate; there are two hash-approved bundles — the wrapper's ledger record and wiki-ingest's page bundle. Said plainly, with the fact that the tool's model reads `fulltext/<attachment key>.md` (absent from wiki-ingest's own input list, `:48-49`). The `SKIPPED no-fulltext` row gains: a source with no attachment reaches compile by attaching it in Zotero, letting Zotero index it, and capturing again — defuddle and autoresearch output lands where `select()` and `_LOCATOR` never look.
8. **`setup-vault` never states the mode.** After `adopt`: the vault runs the tool in `generic` mode (`CONTEXT.md:17`'s paths); `mode get` reads it back. A doctor row for it is lane 3a's (§11).
9. **`project-flow`'s gap analysis routes to wiki-query**; its Contested bucket (`:55`) reads the tool's `contested` assessment instead of frozen `[disputes:: ...]` links.

Pins that move: `tests/test_capture_source_skill.py`; `tests/test_finding_cli.py:443-454`, `:457-477`; `tests/test_publish.py:896`, `:916`; `tests/test_project_flow_skill.py:97`; `tests/test_skill_files.py`.

### 8.3 Tool skills with no counterpart

wiki-retrieve backs wiki-query (edit 9); autoresearch and defuddle are placed by edit 7; wiki-mode by edit 8. `canvas`, `obsidian-markdown`, `save`, `think`, `wiki-fold`, `wiki-cli` share no ground with a research-vault surface. `obsidian-bases` against the seeded `system/bases/*.base` files is an unexamined seam, lane 3a's (§11).

### 8.4 What neither covers — lane 5's (§11)

- The `[[<citation key>]]` back-citation (`capture-source:74`, `synthesis-conventions:8,24`) is enforced by no check.
- The 2+-captured-source threshold for a concept page has no mechanism.
- Retractions and lifecycle findings never reach the tool's ledgers (`compile.py:127` writes `review_status: "unreviewed"` once).
- `published-drift` compares only `projects/<name>` against the tag; drift in the pages a draft cites is compared by nothing.
- `daily-log` has no skill on either side.
- Orientation is split across the vault's `index.md`, `log.md`, `log/` and the tool's `wiki/index.md`, `wiki/hot.md`, `wiki/log.md`; `synthesis-conventions:16` reads three of the six and nothing reads `wiki/log.md`.
- No step tells a person that a search candidate is already captured.
- Byte-comparing a draft's quote against source text has no live producer.

______________________________________________________________________

## 9. Records

### 9.1 #139 — the client paragraph

**Finding.** The choice to speak Zotero's local API and Better BibTeX's JSON-RPC directly is stated nowhere: ingest spec §3.7 (`:264-284`, the section `zotero.py:1` cites) holds only the negatives; §3.8 screened the capture route, not a client library, and `docs/agents/sourcing.md:37` records that no such screen was kept. In the ingest spec "connector" means Zotero's own `/connector/*` server.

**Design.** The opening paragraph of §3.7, labelled *chosen*, dated 2026-09-17 — the client's record:

> `research_vault/zotero.py` speaks Zotero's local API and Better BibTeX's JSON-RPC directly, with no third-party imports. The product adopts Zotero as it is: no client library between product and Zotero, and no translation layer interpreting Zotero's records — every field the snapshot carries is Zotero's own name and value (§3.2). Two bounded exceptions are recorded, not contradicted: Path A's `add` admits caller-supplied item JSON through a whitelist of the same field names (§2), and the CSL file is Better BibTeX's own translator output, which destructures `Extra` (§3.2). The route was chosen over a client library because the contract mismatches can be named (`docs/agents/sourcing.md`). The `Zotero-Server-ID` guard (§2) requires a client that sends the id the provenance tuple recorded; a library that reads the live header and echoes it back defeats the guard by design. Better BibTeX's JSON-RPC (`api.ready`, `item.export`, `item.attachments`) is not exposed by pyzotero, the one Python client in the dev extra. And the gate path imports nothing heavy. Exit: without `zotero.py`, the notes and `system/bibliography.json` are ordinary vault content under Zotero's field names. §3.8 screened the capture route, not the client; this paragraph is the client's record. In this document "connector" means Zotero's own `/connector/*` server, never a third-party client.

Two repairs ride the edit: `:272` still says `export_csl(None)` "is live in the tree today" (removed at `a1210c6`); `sourcing.md:37` gains a dated sentence pointing at the paragraph as the record. `zotero.py`'s docstring points at it.

### 9.2 #91 — the identity rename, closed

**Finding.** Done at `0bf6588` except `pyproject.toml:9`, which reads `name = "research-vault"` on the strength of a terminology row (`41a2d4a`, an hour before #91 was filed; collapsed at `7bdcb22`, dropping the PyPI sentence) that never cited #91. PyPI, 2026-09-17: `research-vault` taken, `research-vault-core` free. The pip-install label lives in `research_vault/templates/ci/verify.yml:18` and `rw-batch.yml:23`, pinned at `tests/test_templates.py:296-297, 336-337`. 35 issues still carry the old slug (13 bodies, 26 comment threads).

**Design.** `pyproject.toml:9` → `research-vault-core`; the two labels follow; the two assertions are hand-edited in a separate commit. `docs/agents/terminology.md:176` splits into two rows — slug and plugin name `research-vault`; distribution `research-vault-core` — with the reasoning: the distribution is not the product, and the PyPI collision above. The old slug is never reused (the redirect's one failure mode), recorded there. The 35 issues are rewritten in §3.1 step 3's pass. `setup-vault` says what a vault scaffolded with `--with-ci` before this changes by hand (the label is create-once).

______________________________________________________________________

## 10. Order of work and verification

One plan, tests first in every task:

01. §2 in full; the `quality.yml` split and rename and the `AGENTS.md` Git line (§3.4, §3.5) — under the old motion, so the renamed job has reported on `main` before the ruleset exists.
02. Going public — §3.1 steps 1–5, the ruleset last; §3.2's `.gitignore` and test; §3.7's amendment.
03. `scripts/mutation_gate.py`: §3.8, §3.9, §6.1 (the reason slot and the header wording).
04. The batch, §4.1 → §4.5 in order. The first branch touching a module is #125's observation.
05. §5.1's four gap tests; §5.2.
06. §7.1, then §7.2–§7.5.
07. §6.2, reasons spelled above post-cut keys.
08. §8.2, §9, the `pyproject.toml` field with its hand-edited assertions.
09. **The blanket run** — one run, because no `--out-dir` records exist and the writer refuses a partial write: `python scripts/mutation_gate.py --update-baseline --out-dir <dir>` over all 38 modules (35 plus `doctor.py`, `keystore.py`, `markers.py`), from a committed tree; a module with no survivors still gets its record; the write carries the reasons, reports any it cannot re-attach, and drops the killed and orphaned keys.
10. The plan's whole-branch review.

From step 4 until step 9 the non-required `mutation-gate` job reports `FAIL` on every branch push touching a moved module and blocks nothing (§3.4).

**Verification.** The offline suite green in the shared checkout with `-p no:cacheprovider` and `PYTHONDONTWRITEBYTECODE=1`; `tests/test_mutation_gate.py` for every gate change; §3.9's `workflow_dispatch` done-when; the live legs on the test instance (`docs/agents/testing.md`) for row 21 and the double hold.

**Not in this spec.** Lane 2 itself.

______________________________________________________________________

## 11. The tracker at approval: closed, filed onward, touched

One pass when the operator approves this spec: seventeen closes, each comment naming its section; the onward issues; the touched-issue comments. Where a row closed on evidence rather than on work, the comment says so.

| Issue | Section  | Closes into                                                                                                                                                                                                                      |
| ----- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| #130  | §3       | decisions 05–07                                                                                                                                                                                                                  |
| #125  | §3.4     | decision 06; done-when at §10 step 4                                                                                                                                                                                             |
| #133  | §3.8     | decision 08                                                                                                                                                                                                                      |
| #132  | §3.9     | decision 09; the issue's stats-file premise corrected                                                                                                                                                                            |
| #142  | §4.1     | decision 10                                                                                                                                                                                                                      |
| #25   | §4.2     | decision 11                                                                                                                                                                                                                      |
| #134  | §4.3     | decision 12                                                                                                                                                                                                                      |
| #131  | §4.4, §6 | decisions 13, 17, 18; item 4 filed onward                                                                                                                                                                                        |
| #129  | §4.5, §7 | rows 11 (`test_structure.py:144-166`), 43 (`741516c`) and 24's dead port (`f2afa2d`) closed on evidence; row 24's fixture ids on the Part B ruling; row 25's quirk 3 as not matching the code; every other row and item designed |
| #136  | §5.1     | decision 15                                                                                                                                                                                                                      |
| #20   | §5.2     | decision 16                                                                                                                                                                                                                      |
| #107  | §7.3     | decision 24                                                                                                                                                                                                                      |
| #32   | §7.4     | decision 25                                                                                                                                                                                                                      |
| #126  | §7.5     | decision 26; the 2026-09-17 counter-argument adopted                                                                                                                                                                             |
| #138  | §8       | decision 27; the record is the evidence sibling                                                                                                                                                                                  |
| #139  | §9.1     | decision 28                                                                                                                                                                                                                      |
| #91   | §9.2     | decision 29                                                                                                                                                                                                                      |

**Filed onward**, each an issue labelled `ready-for-agent` naming its lane; the assembly spec's §7.3 (lane 3a) and §7.4 (lane 5) gain one dated sentence each pointing at them: #131 item 4 (the `no tests` set); lane 3a — the mode doctor row beside the `.obsidian/` seeding, and `obsidian-bases` against the seeded `.base` files; lane 5 — the eight gaps of §8.4, as one issue.

**Touched, not in the milestone** — one comment each naming what moved under it: #141 (compile reads `literature/`; setup-vault's wording; the fixture copies #20's tests extend; a compile.py record in the blanket run), #146 (the refusal identity changes; the cascade does not), #22 (rows 24, 41 and 56(a) resolve part of its inventory), #43 (the cuts and the deletions it would have listed), #27 (no new check id; `tree` absorbs residual 3), #145 (`CAPTURE_FIELDS` is the set #20's guard iterates), #156 (residual 1's null row and row 21's header mapping), #18 and #17 (stale paths their bodies cite), #137 (rests on §9.1's paragraph).

**Amendments that rode the spec commit** (`7d9e436`): the ingest spec's `:3` became an execution record (executed as lane 1; binds until superseded; amended from here); the assembly spec gained the 2026-09-17 State line at `:297`, the decision 22 amendment at `:105-107`, the corrections and supersession at `:101`/`:103`, and the "settled by" sentences at `:573`/`:579`.
