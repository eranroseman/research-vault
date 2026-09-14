# Part A mutation survivors — the full gate at `9bd1f1c`, as far as it ran — results

- **Date:** 2026-09-13
- **Method:** as the record states below
- **Spec:** 2026-09-06-import-redesign-design.md
- **Binds:** nothing — a record of what an execution produced and measured; the spec is the current state

Run serially (`--max-workers 1 --memory-cap 6G --base main`) in a detached worktree on 2026-09-13; the per-module
"ok" line is mutate4py's failure class, not a verdict. The gate's own verdict (`found − baseline`) is FAIL by
construction for this branch: eight new modules have no baseline rows, so every survivor below is "new". Per the
operator's ruling (plan `61b58be`), this list is **Plan W Task 25's triage input** — each survivor is killed or
accepted there, recorded, before the blanket baseline is written. If the run outlived the session that wrote this
file, the rest is in `/tmp/rv-gate.log` on the machine that ran it.

Snapshot written 2026-09-13T18:06Z; modules finished so far: 11.

## `research_vault/__main__.py` — ok

26 survivor line(s):

```
line 233 worst == 0 -> worst != 0 func/cmd_propagate
line 233 0 -> 1 func/cmd_propagate
line 295 True -> False func/cmd_verify
line 640 True -> False func/cmd_inbox
line 705 True -> False func/main
line 709 True -> False func/main
line 712 True -> False func/main
line 713 True -> False func/main
line 716 True -> False func/main
line 721 True -> False func/main
line 733 True -> False func/main
line 734 True -> False func/main
line 738 True -> False func/main
line 741 True -> False func/main
line 744 True -> False func/main
line 748 True -> False func/main
line 755 True -> False func/main
line 756 True -> False func/main
line 757 True -> False func/main
line 766 True -> False func/main
line 771 True -> False func/main
line 772 True -> False func/main
line 781 True -> False func/main
line 784 True -> False func/main
line 788 True -> False func/main
line 790 True -> False func/main
```

## `research_vault/addons.py` — ok

no survivor lines recorded.

## `research_vault/bibliography.py` — ok

2 survivor line(s):

```
line 98 True -> False func/write
line 99 False -> True func/write
```

## `research_vault/capture.py` — ok

37 survivor line(s):

```
line 74 isinstance(item.get("data"), dict)
line 118 1 -> 0 func/_wait_for_key
line 125 0 -> 1 func/_attachment_tuple
line 126 data.get("md5") or "absent" -> data.get("md5") and "absent" func/_attachment_tuple
line 127 data.get("contentType") or "" -> data.get("contentType") and "" func/_attachment_tuple
line 128 data.get("filename") or "" -> data.get("filename") and "" func/_attachment_tuple
line 174 c.get("data", {}).get("itemType") == "attachment" -> c.get("data", {}).get("itemType") != "attachment" func/_capture_one
line 184 c.get("data", {}).get("itemType") == "note" -> c.get("data", {}).get("itemType") != "note" func/_capture_one
line 231 "no-fulltext — " + "; ".join(reasons) -> "no-fulltext — " - "; ".join(reasons) func/_capture_one
line 343 False -> True func/capture
line 363 o.target == "vault" and o.result is not Result.SKIPPED -> o.target == "vault" or o.result is not Result.SKIPPED func/capture
line 363 o.target == "vault" -> o.target != "vault" func/capture
line 363 o.result is not Result.SKIPPED -> o.result is Result.SKIPPED func/capture
line 407 prior is not None
line 407 prior is not None -> prior is None func/capture
line 408 prior.result is Result.UNMATCHED -> prior.result is not Result.UNMATCHED func/capture
line 409 prior.reason.split(" — ")[0] in _REFUSED -> prior.reason.split(" — ")[0] not in _REFUSED func/capture
line 409 0 -> 1 func/capture
line 587 error.result is Result.UNREACHABLE -> error.result is not Result.UNREACHABLE func/add
line 593 isinstance(entry, dict) and entry.get("key") -> isinstance(entry, dict) or entry.get("key") func/add
line 605 "matched — created " + ", ".join(created) -> "matched — created " - ", ".join(created) func/add
line 83 data.get("itemType") == "attachment" and data.get("linkMode") in {
line 111 time.monotonic() + wait_seconds -> time.monotonic() - wait_seconds func/_wait_for_key
line 116 time.monotonic() >= deadline -> time.monotonic() > deadline func/_wait_for_key
line 134 1 -> 0 func/_best_attachment
line 134 1 -> 0 func/_best_attachment
line 208 True -> False func/_capture_one
line 225 reasons and best is None -> reasons or best is None func/_capture_one
line 256 run_version is not None and after is not None and after != run_version -> run_version is not None or after is not None and after != run_version func/_regenerate_csl
line 323 isinstance(key, str) and key -> isinstance(key, str) or key func/_every_note
line 347 0 -> 1 func/capture
line 381 client.server_id or info["server_id"] -> client.server_id and info["server_id"] func/capture
line 486 not isinstance(items, list) or not items or len(items) > 50 -> not isinstance(items, list) and not items or len(items) > 50 func/_validate_items
line 486 len(items) > 50 -> len(items) >= 50 func/_validate_items
line 491 not isinstance(item.get("itemType"), str) or not item["itemType"] -> not isinstance(item.get("itemType"), str) and not item["itemType"] func/_validate_items
line 512 True -> False func/_store_key
line 595 envelope.get("failed") or not created -> envelope.get("failed") and not created func/add
```

## `research_vault/captured.py` — ok

3 survivor line(s):

```
line 270 not isinstance(due, str)
line 272 observed[:10] > instant -> observed[:10] >= instant func/_structural
line 273 due[:10] < instant -> due[:10] <= instant func/_structural
```

## `research_vault/checks.py` — ok

6 survivor line(s):

```
line 296 "date-parts" not in value or value["date-parts"] is None -> "date-parts" not in value and value["date-parts"] is None func/_notice_date_from_updated
line 303 len(date_parts) != 1 or not isinstance(date_parts[0], list) -> len(date_parts) != 1 and not isinstance(date_parts[0], list) func/_notice_date_from_updated
line 352 notice_type == "reinstatement" -> notice_type != "reinstatement" func/_crossref_notices
line 391 len(a) <= len(b) -> len(a) < len(b) func/_dates_incomparable
line 610 status != 200 or not isinstance(text, str) -> status != 200 and not isinstance(text, str) func/_arxiv_version_outcome
line 768 value is None or (isinstance(value, str) and not value.strip()) -> value is None and (isinstance(value, str) and not value.strip()) func/_rw_date
```

## `research_vault/claims.py` — ok

1 survivor line(s):

```
line 58 current_quote is not None and line.startswith("  > ") -> current_quote is not None or line.startswith("  > ") func/parse_claims
```

## `research_vault/clock.py` — ok

no survivor lines recorded.

## `research_vault/factcheck.py` — ok

3 survivor line(s):

```
line 115 not claim.citation_key or not claim.claim_id -> not claim.citation_key and not claim.claim_id func/contested_adjacent_links
line 148 cap < 0 -> cap <= 0 func/select_claims
line 148 0 -> 1 func/select_claims
```

## Finished after the snapshot (banked 2026-09-13 before the run was stopped)

Banked from `/tmp/rv-gate.log` at 2026-09-14T00:45Z (2026-09-13 19:45 CDT on the machine that ran it), just before
the run was stopped. The run was stopped during `research_vault/verify.py`: `structure.py` finished at 23:34Z and
the gate started mutate4py on `verify.py` at once, so the child was ≈70 min in at the kill. Progress reached the log
as `[gate] research_vault/verify.py` and nothing after it — the old gate runs each module under
`subprocess.run(capture_output=True)` and prints the module's block only when mutate4py exits — so verify.py's
`[N/M]` position is unknown and its partial progress is lost with the kill; `verify.py` therefore has no mutate4py
survivor record, and neither do the modules the gate had queued after it (`webapi.py`, `zotero.py`, if selected).
Why stopped: Plan W Task 25 starts its blanket mutmut run in its own worktree; the two must not overlap for memory.
Between `fulltext.py` and `inbox.py` the gate also printed `gitstate.py: excluded [B]` (the header's reason).

Two corrections to how the lists below are read against the snapshot sections above. (1) Each section here carries
mutate4py's own report line (`selected, killed, survived, uncovered`) and its `N survivor line(s)` count equals the
report's `Survived:`; a survivor whose mutant spans several source lines is copied with its continuation lines, as
mutate4py prints it. (2) For a module with no committed manifest mutate4py also prints an `Uncovered mutations:`
list — sites no test reaches per `lcov.info`, never mutated and never run. The snapshot sections above folded that
list into the survivor fence for the two such modules they cover: `capture.py` (37 lines = 16 survivors + 21
uncovered; its fence lists the uncovered 21 first, from `line 74`, then the 16 survivors from `line 83`) and
`captured.py` (3 lines = 0 survivors + 3 uncovered). Every other snapshot count equals its `Survived:`. Here the
two lists are kept apart and labelled.

Modules banked: fulltext, inbox, lifecycle, lints, notes, propagate, publish, quotes, scaffold, searchlog, stamp,
structure — 12 modules, 36 survivors; uncovered lists printed for fulltext (2), lifecycle (5), propagate (17).

## `research_vault/fulltext.py` — ok

mutate4py: 16 selected, 12 killed, 4 survived, 2 uncovered.

4 survivor line(s):

```
line 41 not isinstance(indexed, int) or not isinstance(total, int) -> not isinstance(indexed, int) and not isinstance(total, int) func/verdict
line 46 length < FULLTEXT_MIN_CHARS -> length <= FULLTEXT_MIN_CHARS func/verdict
line 66 0 -> 1 func/_render
line 73 True -> False func/write
```

2 uncovered mutation(s), never run (no test reaches the line per `lcov.info`):

```
line 42 False -> True func/verdict
line 48 False -> True func/verdict
```

## `research_vault/inbox.py` — ok

mutate4py: 21 selected, 17 killed, 4 survived, 74 uncovered.

4 survivor line(s):

```
line 239 notice_date is not None or detection_date is not None -> notice_date is not None and detection_date is not None func/_validate_notice_fingerprint
line 242 notice_class is None or notice_type is None -> notice_class is None and notice_type is None func/_validate_notice_fingerprint
line 649 finding.check == "update-notice" -> finding.check != "update-notice" func/_scope_acknowledged
line 658 len(colliding) == 1 and any(
          ack.ack_of == finding.id
          and ack.actor.startswith("human:")
          and ack.target_hash == finding.target_hash
          and ack.notice_class is None
          for ack in entries
      ) -> len(colliding) == 1 or any(
          ack.ack_of == finding.id
          and ack.actor.startswith("human:")
          and ack.target_hash == finding.target_hash
          and ack.notice_class is None
          for ack in entries
      ) func/_scope_acknowledged
```

## `research_vault/lifecycle.py` — ok

mutate4py: 31 selected, 30 killed, 1 survived, 5 uncovered.

1 survivor line(s):

```
line 121 False -> True func/_drift_detail
```

5 uncovered mutation(s), never run (no test reaches the line per `lcov.info`):

```
line 37 1 -> 0 func/replaces_keys
line 37 1 -> 0 func/replaces_keys
line 39 isinstance(v, str) and v -> isinstance(v, str) or v func/replaces_keys
line 55 data.get("relations") or {} -> data.get("relations") and {} func/read_live
line 126 f"{key}: {'file changed' if file_changed else 'metadata only'}"
          + (", cached text stale" if text_changed else "") -> f"{key}: {'file changed' if file_changed else 'metadata only'}"
          - (", cached text stale" if text_changed else "") func/_drift_detail
```

## `research_vault/lints.py` — ok

mutate4py: 42 selected, 34 killed, 8 survived, 42 uncovered.

8 survivor line(s):

```
line 270 isinstance(citation_key, str) and citation_key -> isinstance(citation_key, str) or citation_key func/_claim_target
line 308 candidate_image is not None -> candidate_image is None func/lint_claim_immutability
line 309 candidate_image is not None -> candidate_image is None func/lint_claim_immutability
line 485 claim.claim_id and isinstance(citation_key, str) and citation_key -> claim.claim_id or isinstance(citation_key, str) and citation_key func/_origin
line 488 fallback or RepoPath(rel) -> fallback and RepoPath(rel) func/_origin
line 508 not isinstance(page_key, str) or not page_key -> not isinstance(page_key, str) and not page_key func/disputed_claim_links
line 551 image is None or image.kind != "file" -> image is None and image.kind != "file" func/_body_bytes
line 571 image is None or image.kind != "file" -> image is None and image.kind != "file" func/_frontmatter
```

## `research_vault/notes.py` — ok

mutate4py: 56 selected, 50 killed, 6 survived, 23 uncovered.

6 survivor line(s):

```
line 218 close < 0 -> close <= 0 func/canonical_content
line 218 0 -> 1 func/canonical_content
line 246 item < close -> item <= close func/canonical_content
line 348 data.get("linkMode") not in {"imported_file", "imported_url"} or not data.get(
      "md5"
  ) -> data.get("linkMode") not in {"imported_file", "imported_url"} and not data.get(
      "md5"
  ) func/_attachment_line
line 427 body and not body.endswith("\n") -> body or not body.endswith("\n") func/render_body
line 526 not ITEM_KEY_RE.match(provenance.item_key) or not provenance.citation_key -> not ITEM_KEY_RE.match(provenance.item_key) and not provenance.citation_key func/read_provenance
```

## `research_vault/propagate.py` — ok

mutate4py: 32 selected, 27 killed, 5 survived, 17 uncovered.

5 survivor line(s):

```
line 257 True -> False func/_canonical
line 257 False -> True func/_canonical
line 369 o.result is not Result.MATCHED -> o.result is Result.MATCHED func/apply
line 371 True -> False func/apply
line 373 0 -> 1 func/apply
```

17 uncovered mutation(s), never run (no test reaches the line per `lcov.info`):

```
line 66 structure.is_excluded(path, vault)
          or parts[0] in _SKIP_DIRS
          or relative in _SKIP_FILES
          or relative.startswith(RECORD_DIR + "/")
          # Never written through (stamp.py refuses the same), and verify
          # gives a symlink no content identity, so none is hashed either.
          or path.is_symlink() -> structure.is_excluded(path, vault)
          and parts[0] in _SKIP_DIRS
          or relative in _SKIP_FILES
          or relative.startswith(RECORD_DIR + "/")
          # Never written through (stamp.py refuses the same), and verify
          # gives a symlink no content identity, so none is hashed either.
          or path.is_symlink() func/_surfaces
line 67 parts[0] in _SKIP_DIRS -> parts[0] not in _SKIP_DIRS func/_surfaces
line 67 0 -> 1 func/_surfaces
line 68 relative in _SKIP_FILES -> relative not in _SKIP_FILES func/_surfaces
line 69 RECORD_DIR + "/" -> RECORD_DIR - "/" func/_surfaces
line 83 outcome.target == "vault" and outcome.result is Result.UNMATCHED -> outcome.target == "vault" or outcome.result is Result.UNMATCHED func/_mapping_from_linter
line 83 outcome.target == "vault" -> outcome.target != "vault" func/_mapping_from_linter
line 83 outcome.result is Result.UNMATCHED -> outcome.result is not Result.UNMATCHED func/_mapping_from_linter
line 86 outcome.result is Result.UNMATCHED and outcome.reason.startswith(
          "re-keyed — "
      ) -> outcome.result is Result.UNMATCHED or outcome.reason.startswith(
          "re-keyed — "
      ) func/_mapping_from_linter
line 86 outcome.result is Result.UNMATCHED -> outcome.result is not Result.UNMATCHED func/_mapping_from_linter
line 89 1 -> 0 func/_mapping_from_linter
line 366 "matched — rewrote " + (", ".join(changed) or "nothing") -> "matched — rewrote " - (", ".join(changed) or "nothing") func/apply
line 366 ", ".join(changed) or "nothing" -> ", ".join(changed) and "nothing" func/apply
line 444 provenance is not None
          and item_key is not None
          and provenance.item_key != item_key -> provenance is not None
          or item_key is not None
          and provenance.item_key != item_key func/lint_propagation
line 444 provenance is not None -> provenance is None func/lint_propagation
line 445 item_key is not None -> item_key is None func/lint_propagation
line 446 provenance.item_key != item_key -> provenance.item_key == item_key func/lint_propagation
```

## `research_vault/publish.py` — ok

mutate4py: 3 selected, 2 killed, 1 survived, 17 uncovered.

1 survivor line(s):

```
line 410 True -> False func/_append_log
```

## `research_vault/quotes.py` — ok

mutate4py: 3 selected, 2 killed, 1 survived, 13 uncovered.

1 survivor line(s):

```
line 106 best >= FUZZY_THRESHOLD -> best > FUZZY_THRESHOLD func/check_quote
```

## `research_vault/scaffold.py` — ok

mutate4py: 35 selected, 31 killed, 4 survived, 14 uncovered.

4 survivor line(s):

```
line 92 True -> False func/_render_glossary_if_absent
line 175 with_ci and not (vault / ".github" / "workflows" / "verify.yml").exists() -> with_ci or not (vault / ".github" / "workflows" / "verify.yml").exists() func/_preflight_conflicts
line 177 with_rw_ci and not (vault / ".github" / "workflows" / "rw-batch.yml").exists() -> with_rw_ci or not (vault / ".github" / "workflows" / "rw-batch.yml").exists() func/_preflight_conflicts
line 622 isinstance(records, list) and records -> isinstance(records, list) or records func/_compile_tool_probe
```

## `research_vault/searchlog.py` — ok

mutate4py: 1 selected, 1 killed, 0 survived, 5 uncovered.

no survivor lines recorded.

## `research_vault/stamp.py` — ok

mutate4py: 12 selected, 11 killed, 1 survived, 0 uncovered.

1 survivor line(s):

```
line 74 ".git" in path.parts or path.name in _SKIP_NAMES -> ".git" in path.parts and path.name in _SKIP_NAMES func/stamp_types
```

## `research_vault/structure.py` — ok

mutate4py: 25 selected, 24 killed, 1 survived, 0 uncovered.

1 survivor line(s):

```
line 131 1 -> 0 func/_log_shape_problems
```
