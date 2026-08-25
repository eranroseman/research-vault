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
`test_supplied_snapshot_shape_requires_web_archive_org_not_bare_archive_org`
(renamed in fix round 1 — see below),
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
- `test_supplied_snapshot_shape_requires_web_archive_org_not_bare_archive_org`
  (renamed in fix round 1 — see below) — pins the
  `archive.org`-vs-`web.archive.org` decision above.
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
- **Superseded by fix round 1:** the original version of this report declined
  to tighten `test_a_supplied_snapshot_off_the_archives_host_is_refused`'s
  loose `Result.UNMATCHED`-only assertion as out of scope. Round 1's review
  showed that decline was reasonable only *before* this task's diff — this
  task's own new UNMATCHED reasons could silently satisfy that test in place
  of the `is_archive_url` check it was meant to pin. Fixed in round 1 (below);
  see that section for the exact-reason assertion and its discrimination
  proof.
- **Other loose-prefix reason assertions remain in `test_archive.py`**
  (`test_an_unconfirmed_snapshot_is_never_recorded`'s
  `reason.startswith("missing-archive")`,
  `test_save_page_now_outage_writes_nothing`'s
  `reason.startswith("outage — Save Page Now unavailable")`, and
  `test_a_snapshot_url_off_the_archives_host_is_never_recorded`'s bare
  `Result.UNMATCHED` with no reason check at all) — none of these overlap
  code this task touches, so none were tightened here. Destination:
  **GitHub issue #22** ("Sweep loose prefix assertions on outcome reason
  strings"), which already tracks exactly this class of defect across the
  suite.

## Fix round 1 (review response)

Commit: `fix: Task 18 review round 1 — close the tab-smuggling gap, fix
path-only trailing-slash comparison, pin the host gate and shape
boundaries` (follow-up on top of `f05103e`, nothing amended, nothing
rebased).

Spec was PASS; the following are quality findings (F1-F9) from the round.

### F3 — this section, plus the commit body, carries what was report-only before

The two-validator reconciliation, the `archive.org`-vs-`web.archive.org`
decision, and the deliberate confirmed-path asymmetry were written into the
first report but not into `f05103e`'s (empty) commit body, so — per this
repo's comment-hygiene doctrine, which routes provenance/correctness
arguments to the commit body rather than code comments — that material had
nowhere in history to live. This round's commit body restates all three,
plus the two reasons for the host-then-shape ordering below.

### F1 / F8 — two comments the diff had made false

- `ARCHIVE_HOSTS`'s comment said "The only hosts a recorded snapshot may live
  on," which stopped being true the moment a supplied snapshot was narrowed
  to `web.archive.org` only. Reworded to state what each path actually
  allows: `is_archive_url` (and therefore `ARCHIVE_HOSTS`) still gates both
  paths at the coarse two-host level; only the supplied path is narrowed
  further, by `_SNAPSHOT_RE`.
- The module docstring's "it records only what the availability API
  returns" was never true for the supplied branch, which was already
  recording caller input, not an API response. Reworded to describe both
  cases: an automatic capture records the availability API's answer; a
  supplied snapshot is recorded once independently confirmed to be a Wayback
  capture of the note's own url.

### F2 — the `is_archive_url` gate on the supplied branch was pinned by zero tests

Deleting `if not is_archive_url(snapshot): ...` from the supplied branch left
the entire offline suite green (confirmed independently by the coordinator;
reproduced here). Two fixes:

1. **`test_a_supplied_snapshot_off_the_archives_host_is_refused`** now
   asserts the exact reason
   (`"missing-archive — supplied snapshot is not a web.archive.org URL"`),
   not just `Result.UNMATCHED`. Before this round, the task's own new
   UNMATCHED reasons could silently satisfy that assertion in place of the
   check it was meant to pin.
2. **New test,
   `test_a_supplied_snapshot_with_a_smuggled_trailing_newline_is_refused`**,
   pins the exact case the layering argument rests on: `SNAPSHOT + "\n"`
   satisfies `_SNAPSHOT_RE` (Python's `$` matches before a single trailing
   newline) and satisfies the target-url comparison (the captured `original`
   excludes the newline, since `.` doesn't match it), so only
   `is_archive_url`'s `splitlines() != [url]` check refuses it.

**Discrimination.** Deleted the `is_archive_url` gate block from
`archive_source` (temporarily, restored before committing): both tests went
red — the off-host test on the reason-string assertion (`Result.UNMATCHED`
still held, since the shape regex also rejects `https://evil.example/x`, but
under the wrong reason), and the newline test by actually reaching the
forbidden `webapi.get_status` call and raising.

**A second, independent reason for the host-before-shape order** (not
stated in the original report): `is_archive_url` and `_SNAPSHOT_RE` disagree
in the *other* direction too. A host string with an embedded tab (e.g.
`web.arch\tive.org`) is rejected by `_SNAPSHOT_RE`'s literal match (the tab
sits inside characters the regex requires verbatim) but would be
**accepted** by `is_archive_url` alone, because `urlsplit` silently drops
tabs before `is_archive_url` ever compares `netloc` against `ARCHIVE_HOSTS`
— so on its own, `is_archive_url` cannot tell that string from a clean
`web.archive.org`. Running the shape regex is what actually catches it in
that direction. Combined with the newline case above (where the reverse is
true — `_SNAPSHOT_RE` alone would accept it, `is_archive_url` alone rejects
it), the two checks are complementary, not redundant, and both must run.

### F4 — `_comparable_url` stripped the wrong trailing slash

The bug: `removesuffix("/")` ran on the fully recomposed URL string, so a
trailing `/` inside the **query string** or **fragment** was stripped as
though it were a path separator. Reproduced the coordinator's two failing
cases directly against the pre-fix function
(`_comparable_url('https://example.org/p?a=b/') ==
_comparable_url('https://example.org/p?a=b')` → `True`, wrong) before
touching code. Fixed by stripping the suffix from `parts.path` specifically,
before recomposing, so only a path-level trailing slash is ever touched.

**New test,**
`test_supplied_snapshot_trailing_slash_outside_the_path_does_not_match`
(parametrized: query-string and fragment cases), asserts these must be
`UNMATCHED` — a URL differing only in whether its query string or fragment
happens to end in `/` is a different resource, not the stated
trailing-slash equivalence. **Discrimination:** reverted `_comparable_url`
to the round-1 (recompose-then-strip) version; both parametrizations went
red (`MATCHED` instead of the expected `UNMATCHED`). Restored, reran clean.

### F5 — a tab in the supplied snapshot passed both gates, then raised out of `archive_source`

`urlsplit` unconditionally strips exactly three bytes anywhere in a URL
before parsing: `\t`, `\r`, `\n` (confirmed directly against
`urllib.parse._UNSAFE_URL_BYTES_TO_REMOVE`). `is_archive_url`'s
`splitlines() != [url]` check catches `\r`/`\n` (and the other
`str.splitlines()` boundaries), but not `\t`. So a snapshot whose `original`
carries a raw tab — e.g.
`https://web.archive.org/web/20240101000000/https://exa\tmple.org/page` —
matches the shape regex (`.` matches a tab) and then compares as
`_comparable_url`-equal to a clean note url (`urlsplit` drops the tab from
both sides of the comparison), passing every check. `_record` then writes
the **raw, still-tab-carrying** `snapshot` string to the frontmatter, and
`frontmatter.render_field` raises `FrontmatterError`, uncaught — verified
directly:

```
RAISED: FrontmatterError frontmatter scalars cannot carry control or
line-break characters: '...exa\tmple.org/page'
```

This is the four-state contract violation the coordinator named: the verb
must return an `Outcome`, never raise, for anything short of "cannot run at
all." Fix: extended the shape gate to `if match is None or "\t" in
snapshot:`, so the check happens before either gate downstream, using the
same shape-rejection reason (a URL carrying a raw tab is not a well-formed
snapshot shape either). **New test,**
`test_supplied_snapshot_carrying_a_raw_tab_is_never_recorded`, asserts
`UNMATCHED` with that reason and zero network calls. **Discrimination:**
removed the `or "\t" in snapshot` clause — the test went red by reaching the
forbidden `get_status` call (proving the vulnerable path is live without
the check); separately reproduced the full pre-fix crash end-to-end (fake
`get_status` returning 200, no `forbidden` trap) and confirmed the
uncaught `FrontmatterError`. Restored the fix and reran clean — the same
scenario now returns `UNMATCHED` before any network call.

### F6 (minor) — non-capturing timestamp group

`(\d{4,14})` was captured but never read (only `original` is). Changed to
`(?:\d{4,14})`. No behavior change: ran the F9 3/4/15/17-digit probe
directly against both the old (capturing) and new (non-capturing) pattern
side by side — identical match/no-match and identical `original` for all
four lengths.

### F7 (minor) — test name didn't match its body

`test_supplied_snapshot_on_the_availability_hosts_bare_domain_fails_shape`
supplied a full, shape-plausible capture path hosted on `archive.org`, not a
bare domain. Renamed to
`test_supplied_snapshot_shape_requires_web_archive_org_not_bare_archive_org`
and reworded its docstring to say so.

### F9 (minor) — untested-but-correct boundary shapes, now pinned

Added four end-to-end tests (through `archive_source`, matching this file's
existing convention rather than probing `_SNAPSHOT_RE` directly), covering
exactly the cases named:

- `test_supplied_snapshot_timestamp_length_bound` (parametrized 3/4/15/17
  digits) — 3, 15, and 17 digits fail shape; 4 succeeds and records. Probed
  directly against the regex first to confirm the boundary (`\d{4,14}`
  accepts 4-14, rejects 3 and anything ≥15) before writing the test.
- `test_supplied_snapshot_original_with_a_non_http_scheme_fails_shape` — an
  `original` with an `ftp://` scheme fails shape (the named group itself
  requires `https?://`).
- `test_supplied_snapshot_uppercase_modifier_suffix_fails_shape` — `ID_`
  (uppercase) fails shape; the modifier class (`[a-z_]+`) is lowercase-only,
  matching Wayback's own (always-lowercase) suffixes.

No production behavior changed for these three; they pin what the regex
(unchanged apart from F6's non-capturing-group edit, which doesn't affect
matching) already did, so per the coordinator's own framing ("behaves
correctly and is untested is exactly the state that lets a guard be deleted
silently") the goal was coverage, not a fix — no stash/mutation
discrimination performed for these three since there is no round-1
production change tied to them to discriminate against.

### Verification after all nine findings

- Full offline suite: `1621 passed, 7 skipped` (round-1's `1611 passed / 7
  skipped` + 10 new tests: 1 newline test + 4 timestamp-length + 1
  non-http-scheme + 1 uppercase-suffix + 2 trailing-slash + 1 tab test).
- `ruff check` — clean (two `PT006` hits from writing parametrize argnames
  as a comma string instead of a tuple, matching this file's own convention
  elsewhere; fixed, then `ruff format` reformatted the wrapped lines).
- `ruff format --check` — clean.
- `mypy knowledge_harness/` — `Success: no issues found in 27 source files`.
- `echo '{}' | python hooks/stop_publish_gate.py` — silent, exit 0.
- Working tree clean after commit; no amend, no rebase — this round's commit
  sits on top of `f05103e`. `progress.md` excluded (concurrent edit by the
  coordinator).

### Deferred (coordinator instruction, not touched)

- Stale `archive.py.manifest.json` sidecar — pre-existing, already stale at
  `c010d0f`, tool that reads it is being replaced.
- Confirmed-path residual: a `closest.url` pointing at a different site than
  the note's own `url` is still recorded on that path — deliberate, out of
  this task's scope (see the asymmetry discussion above).
