# Task 18 report: supplied archive snapshots verified by shape and target URL

Commit: `fix: supplied archive snapshots verified by shape and target URL`

## What changed

`archive.py`'s supplied-snapshot branch (`archive_source`, ~lines 208-244)
previously accepted any `snapshot` argument that (a) lived on
`web.archive.org`/`archive.org` (`is_archive_url`) and (b) did not 404. Neither
condition established that the snapshot was a Wayback capture *of the note's
own URL*. Two new gates now run before any network call:

1. **Shape.** `_SNAPSHOT_RE` (new module constant) requires the Wayback
   capture path shape — `web.archive.org/web/<timestamp><optional modifier
   suffix>/<original-url>` — and captures the archived target as the
   `original` named group. A snapshot that is merely host-alive (e.g. the bare
   domain `https://web.archive.org/`) fails here:
   `"missing-archive — supplied snapshot is not a Wayback snapshot URL"`.
2. **Target match.** `original` must equal the note's own `url` field after
   normalization (new `_comparable_url` helper). Mismatch:
   `"missing-archive — supplied snapshot is for a different URL"`.

Both checks happen strictly before `webapi.get_status` — a shape or
target-mismatch failure makes no outward call.

## Decisions the controller asked me to make explicit

**Two-validator reconciliation (`is_archive_url` vs. `_SNAPSHOT_RE`).** Kept
both, layered, rather than replacing one with the other:

- `is_archive_url` stays the *first* gate on the supplied branch, unchanged,
  still testing host membership in `ARCHIVE_HOSTS` (`web.archive.org` or
  `archive.org`) — this is the same gate `_closest_snapshot` applies to the
  API-confirmed path, so the two paths still agree on "which hosts is a
  recorded URL allowed to live on."
- `_SNAPSHOT_RE` is a *second*, narrower gate scoped only to the supplied
  branch: it requires the literal host `web.archive.org` (not `archive.org`)
  plus the capture-path shape.

This is not cosmetic layering — I verified empirically that the regex alone
cannot replace `is_archive_url` as the sole gate. Python's `re` `$` anchor
matches both at the true end of string and immediately before a single
trailing `\n`, so `_SNAPSHOT_RE.match(good_snapshot + "\n")` succeeds even
though the string carries a smuggled newline:

```
>>> archive._SNAPSHOT_RE.match(SNAPSHOT + "\n") is not None
True
>>> archive.is_archive_url(SNAPSHOT + "\n")
False
```

`is_archive_url`'s `url.splitlines() != [url]` check is what actually rejects
that string. It is the same class of control-character injection that
`test_a_snapshot_url_off_the_archives_host_is_never_recorded`'s
line-separator case already pins on the API-confirmed path. So the layering
is load-bearing, not redundant: `is_archive_url` blocks host-spoofing and
embedded-newline/control-character strings; `_SNAPSHOT_RE` blocks host-alive
non-snapshots and enforces the capture-path shape.

The `archive.org`-vs-`web.archive.org` split is deliberate:
`AVAILABILITY_ENDPOINT` (`https://archive.org/wayback/available`) is the
availability API's own host, not a host a real Wayback *snapshot* is ever
served from — a real capture always resolves under `web.archive.org/web/...`.
`_SNAPSHOT_RE` hardcodes only `web.archive.org` for exactly this reason.
Pinned by
`test_supplied_snapshot_on_the_availability_hosts_bare_domain_fails_shape`,
which supplies a shape-valid capture path hosted on bare `archive.org` and
asserts it is refused with the shape reason, not silently accepted because
`archive.org` is in `ARCHIVE_HOSTS`.

**Asymmetry (deliberate, scoped to the supplied branch).** `_closest_snapshot`
(the API-confirmed path) still only runs `is_archive_url` — it gains neither
the shape check nor the target-URL check. This is intentional: the
availability API is queried with `params={"url": url}`, so its response is
already an answer about the note's own `url`; the exposure the shape/match
checks close is specific to a *user-supplied* value the harness never sent a
query for. Not touched, not extended — flagged here per instruction rather
than silently inherited.

**Normalizer (`_comparable_url`).** No existing two-URL comparator exists
anywhere in `knowledge_harness/` (confirmed by three independent checks:
no `def` taking two URLs to compare; every `netloc` use elsewhere is a
single-URL test against a constant; the only casefold-on-host idiom is
`_arxiv_identity`/`_arxiv_base_identity`, which is arXiv-specific and not
reusable here). Implemented exactly the brief's stated fallback and nothing
wider: lowercase scheme + host only, strip exactly one trailing slash. No
`www.` stripping, no query-param sorting, no percent-decoding — a more
permissive normalizer would treat two materially different URLs as the same
target, reopening the hole this task closes.

## Tests (TDD)

Added to `tests/test_archive.py`, in a new section right after the existing
supplied-snapshot tests:

- `test_supplied_snapshot_must_have_wayback_shape` — host-only
  `https://web.archive.org/`, live if reached (network call is forbidden via
  monkeypatch to prove it's never made) → exact reason
  `"missing-archive — supplied snapshot is not a Wayback snapshot URL"`.
- `test_supplied_snapshot_on_the_availability_hosts_bare_domain_fails_shape` —
  pins the `archive.org`-vs-`web.archive.org` decision above.
- `test_supplied_snapshot_must_match_note_url` — shape-valid snapshot whose
  `original` is a different site than the note's `url` → exact reason
  `"missing-archive — supplied snapshot is for a different URL"`.
- `test_supplied_snapshot_timestamp_modifier_suffix_is_a_valid_shape` —
  boundary case, `.../20240101000000id_/https://...` — must still PASS
  (MATCHED, recorded, one `save` call, zero `availability` calls).
- `test_supplied_snapshot_original_may_differ_from_note_url_by_one_trailing_slash`
  — boundary case, `original` vs. note `url` differ only by a trailing slash
  — must still PASS under the stated normalization.

**Red before implementing:** ran the three new UNMATCHED-reason tests against
the unmodified source first. All three failed for the intended reason — the
`get_status` monkeypatch's `forbidden()` fired (`AssertionError: a
mal[shaped|matched] snapshot must make no outward call`), proving today's
code reaches the network call in both the shape and mismatch cases (matching
the brief's claim that both record MATCHED today).

**Discrimination, done two ways:**

1. `git stash` on `archive.py` only (tests already in place) → same three
   tests red, for the same reason, confirming the whole diff is what flips
   them. `git stash pop` restored green.
2. Targeted single-line mutations, each isolating one specific piece of new
   logic, each reverted before commit:
   - Removed the regex's `(?:[a-z_]+)?` modifier group →
     `test_supplied_snapshot_timestamp_modifier_suffix_is_a_valid_shape` goes
     red (`UNMATCHED`, "not a Wayback snapshot URL") — proves that test
     actually exercises the modifier-suffix group.
   - Replaced `_comparable_url(...) != _comparable_url(...)` with a bare
     `match.group("original") != url` (no normalization) →
     `test_supplied_snapshot_original_may_differ_from_note_url_by_one_trailing_slash`
     goes red (`UNMATCHED`, "for a different URL") — proves that test
     actually exercises the trailing-slash normalization.

Every new UNMATCHED assertion checks the exact reason string, not just
`Result.UNMATCHED` — per the "assert the exact reason" instruction, since a
looser assertion would be satisfied by any of the branch's several UNMATCHED
paths.

## Verification

- Full offline suite: `1611 passed, 7 skipped` (baseline `1606 passed / 7
  skipped` + 5 new tests, skip count unchanged).
- `ruff check` — clean (one `FURB188` hit on the first pass, fixed by using
  `str.removesuffix("/")` instead of a manual slice-ternary).
- `ruff format --check` — clean (reformatting applied once during
  development, re-checked clean before commit).
- `mypy knowledge_harness/` — `Success: no issues found in 27 source files`.
- `echo '{}' | python hooks/stop_publish_gate.py` — silent, exit 0.

**Live legs untouched by this change.** The one `live_net`-gated test in this
file (`test_archives_a_real_url_against_the_internet_archive`) calls
`archive_source` with no `snapshot=` kwarg, so it exercises only the
API-confirmed path (`_closest_snapshot` → liveness probe), which this task
did not modify. Nothing in this diff is verified against the real network
by the offline suite or by the live legs that exist today; Task 21 is where
any live-network behavior touching this module gets exercised, and even
then only for the confirmed path already covered by that test, not the new
supplied-snapshot gates (there is no live-net test that passes `snapshot=`).

## Concerns

- **The confirmed-snapshot path (`_closest_snapshot`) has no live-net test
  that exercises a *supplied* snapshot's shape/match gates, and none is
  planned to.** Recorded here as the controller instructed (asymmetry is
  deliberate — see above) rather than left implicit. No action taken;
  disposition is "intentionally out of scope for this task."
- **Pre-existing gap, not introduced by this task:**
  `test_a_supplied_snapshot_off_the_archives_host_is_refused` (already in the
  file before this change) still asserts only `Result.UNMATCHED`, not the
  exact reason string, for the `is_archive_url` rejection path. I left it
  alone — it predates this task and the brief scoped this task to the new
  shape/match checks, not to retrofitting every pre-existing assertion in the
  file. Declining to touch it; if tightening every existing loose assertion
  in `test_archive.py` is wanted, it needs its own task/issue rather than
  scope creep on this one.
