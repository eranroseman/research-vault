# Part A mutation survivors — the full gate at `9bd1f1c`, as far as it ran

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

## `research_vault/fulltext.py` — (running or not finished)

no survivor lines recorded.
