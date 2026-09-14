# Part B deferred findings

Minor findings raised by the per-task reviews of `2026-09-07-ingest-redesign-b-compile.md` and
deliberately held out of their tasks' fix loops. None blocks a merge.

Rows are appended by the controller in a pathspec commit that follows the task's review, so the
record is written at the moment the finding is deferred rather than assembled at the end.

**Task 6 Step 1b's whole-branch review dispositions every row.** Each ends **fixed**, naming the
commit, or **declined**, with the reason written into the row. Rows still open after that review
become one repository issue (`gh issue create --label ready-for-agent`) with the open rows as its
body; Part A's #129 is the shape.

| #   | File                                | Finding                                                                                                                                                                                                                             | Task | Disposition                                                                                                                 |
| --- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- | --------------------------------------------------------------------------------------------------------------------------- |
| 1   | `docs/terminology.md:154`           | The reason-codes row carries the prose prefix "the `REASON_CODES` registry at HEAD:" that the plan's printed row lacks. Inert: the registry test captures only lowercase-hyphen backticked tokens, and the row is one physical row. | 4    | open                                                                                                                        |
| 2   | `tests/test_skill_contracts.py:609` | `test_terminology_registries_match_the_code` re-imports `re` and `inbox` locally; both are module-scope imports already (lines 9, 16). Verbatim from the plan's printed test (plan-mandated).                                       | 4    | open                                                                                                                        |
| 3   | `pyproject.toml:89`                 | A `per-file-ignores` entry (`PT018`) for `tests/test_capture_live.py`: the plan's printed write-leg assertion pairs two facts in one `assert`. Reviewer: sound, precedented (`test_cli_live.py` = `UP012`), no action.              | 5    | declined — the plan's printed test stays verbatim; the ignore is file- and rule-scoped with a comment (review of `c551a0b`) |
