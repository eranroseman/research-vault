# Plan B: Verification Suite + Review Inbox — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The deterministic verification engine of spec §6 — claim parsing, the review inbox, verified events, all citation checks with four-state results, the six integrity lints, selector production — surfaced as `python -m harness_core verify`.

**Architecture:** Pure functions over the vault's files plus a thin polite-HTTP layer for external APIs; every checker returns four-state outcomes, only MATCHED mints `verified` events, everything else lands in `+/review-queue.md`. Consumes Plan A's as-built modules (commit `7d07d14`); no writer touches a managed region except through Plan A's render pipeline.

**Tech Stack:** Python ≥3.10 stdlib; optional extras group `pdf` (`pypdf>=4`) for selector production only. pytest dev-only. Live-network tests behind a `live_net` marker.

**Spec:** `docs/specs/2026-08-16-foundation-spec.md` (§3 inbox, §5 schema/events, §6 gates, §7 import-source duties). Plan A obligations inherited: selector production + backfill, symmetric selector unescaping.

## Global Constraints

- **Four-state results everywhere**: `MATCHED | UNMATCHED | UNREACHABLE | SKIPPED` (`harness_core.Result`). An outage is never reported as fabrication; malformed API JSON = UNREACHABLE, never a crash.
- **Only MATCHED appends `verified` events** (§5); events carry `{by, at, check}`; quote-check `check` payloads carry claim address **and comparison target** (`managed-region` now; `source-text` later).
- **Every non-MATCHED outcome and every warn-tier finding is one review-inbox entry** (§3 serialization); acknowledgment is a follow-up entry by a `human:` actor; ack scope stands per check+target until the target's recorded hash changes.
- **Reason codes** open every `reason` field: `contradiction | low-confidence | schema-violation | mismatch | not-admitted | outage | stale | drift | contested | superseded-source | missing-archive | fuzzy-quote | no-identifier | retracted | warn-notice | matched | manual` — free text may follow the code. No reason string may open with anything else.
- **Closing-class vs warn-tier exit surface**: `CLOSING_CHECKS = {"citekey", "quote", "update-notice", "evidence-layer"}`. `verify` exits 1 only when a closing-class check is UNMATCHED; warn-tier UNMATCHED (metadata, integrity lints) prints findings and files inbox entries but exits 0; UNREACHABLE-anywhere with no closing UNMATCHED exits 3. Plan C's gates key on this contract.
- **Venv bootstrap**: `core/.venv` is gitignored and does NOT exist in a fresh worktree. Task 1's first Run step creates it (`python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]" -q` — PEP 668 blocks system pip).
- **Polite pools**: every external HTTP call sends `mailto` (from `.harness/machine.json` key `mailto`, fallback env `HARNESS_MAILTO`); ≤3 concurrent never needed (serial calls only); timeout 10 s.
- **Update-notice classes** (§6): blocking = `retraction, partial_retraction, removal, withdrawal`; warn = `expression_of_concern, correction, corrigendum, erratum`; `reinstatement` clears. Match on DOI **and** PMID. Record notice date and detection date (bi-temporal).
- **Quote gate**: NFKC + whitespace-collapse + dehyphenation, then exact = MATCHED; fuzzy-only (normalized Levenshtein ≥ 0.90) = inbox entry, result stays UNMATCHED-with-fuzzy-reason (never silent pass); no comparison target = UNREACHABLE.
- **Execution isolation:** worktree via `superpowers:using-git-worktrees`, branch `build/plan-b`; every test Run begins `cd core && source .venv/bin/activate` from the worktree root; commits run from the worktree root.
- Plan A as-built interfaces are authority; where this plan's code disagrees with `core/harness_core/*.py` at HEAD, **HEAD governs** and the implementer adapts within-task (record the adaptation in the commit message).
- Commit messages conventional. No placeholders.

## File Structure

```
core/harness_core/
├── claims.py        # claim-line parser: tags, citations, anchors, inline fields (Task 1)
├── inbox.py         # +/review-queue.md read/append/ack/summary (Task 2)
├── events.py        # verified events + trust-tier derivation (Task 3)
├── webapi.py        # polite four-state HTTP JSON layer (Task 4)
├── checks.py        # citekey / DOI+registry / metadata / update-notice checks (Tasks 5–8)
├── identify.py      # identifier discovery before SKIPPED (Task 9)
├── quotes.py        # normalization, Levenshtein, quote verification (Task 10)
├── lints.py         # six integrity lints (Task 11)
├── selectors.py     # pypdf text, context capture, symmetric unescape (Task 12)
└── __main__.py      # + verify / inbox verbs (Task 13, modify)
core/tests/
├── conftest.py      # + fixture_vault with populated notes (Task 1, modify)
└── test_{claims,inbox,events,webapi,checks,identify,quotes,lints,selectors,verify_cli}.py
```

`checks.py` holds the four citation checkers in one file: they share the outcome dataclass, the bibliography walk, and the inbox/event plumbing — splitting them would scatter one responsibility (citation verification) across four files.

---

### Task 1: Claim parser + populated fixture vault

**Files:**
- Create: `core/harness_core/claims.py`
- Modify: `core/tests/conftest.py` (add `fixture_vault`)
- Test: `core/tests/test_claims.py`

**Interfaces:**
- Consumes: `harness_core.notes` constants (`MANAGED_OPEN`, `MANAGED_CLOSE`).
- Produces:
  - `@dataclass Claim`: `tag: str` (`quote|paraphrase|inference|open-question`), `citekey: str | None`, `locator: str | None`, `claim_id: str | None`, `line_no: int`, `quote_text: str | None` (joined blockquote lines), `fields: dict[str, str]` (inline `[k:: v]` fields — `confidence`, `status`, `retraction-ack`, `verify-failed`, `supported-by`, `contested-by`, …), `in_managed: bool`.
  - `parse_claims(text: str) -> list[Claim]` — scans any note body; a claim line is `- (<tag>) …` optionally carrying `[@citekey]` or `[@citekey, <locator>]` and `^<id>`; subsequent `  > …` lines aggregate into `quote_text`; inline fields parse from `[key:: value]` (value may contain spaces; fields never nest).
  - `claim_address(citekey: str, claim_id: str) -> str` — `f"{citekey}#^{claim_id}"`.
  - `conftest.fixture_vault(tmp_vault)` — a `tmp_vault` populated with: `literatures/smith2020.md` (managed region, one quote claim `^c-11111111` with locator p. 12, one paraphrase claim `^c-22222222`, frontmatter with `doi`, `retrieved`, `status: "active"`), `literatures/gone2019.md` (`status: "superseded"`, `superseded-by: "smith2020"`), `atlas/index.md`, `atlas/mortality-trends.md` (one inference claim with `[supported-by:: [[smith2020#^c-11111111]]]` and `[contested-by:: [[gone2019#^c-22222222]]]` and `[confidence:: moderate]`), `efforts/brief/draft.md` (cites `[@smith2020, p. 12]` with a quote and `[@fabricated2020]`), `x/bibliography.json` (entries for smith2020, gone2019 with title/author/issued), one `calendar/2026-08-16.md`, empty `+/review-queue.md`; all committed (`git add -A && git commit`) so git-based lints have a HEAD.

- [ ] **Step 1: Write the failing test**

```python
# core/tests/test_claims.py
from harness_core import claims


NOTE = """---
citekey: "smith2020"
---
%%hk-managed%%
# Mortality decline

- (quote) [@smith2020, p. 12] ^c-11111111
  > Mortality fell 12%
  > across all strata.
- (paraphrase) Design is retrospective [@smith2020, p. 3] ^c-22222222
%%/hk-managed%%

## Notes
- (inference) Generalizes widely [@smith2020] [confidence:: moderate] [status:: live] ^c-33333333
- (open-question) What drives the decline? ^c-44444444
plain prose is not a claim
"""


def test_parse_counts_and_tags():
    cs = claims.parse_claims(NOTE)
    assert [c.tag for c in cs] == ["quote", "paraphrase", "inference", "open-question"]


def test_quote_aggregates_blockquote_and_managed_flag():
    q = claims.parse_claims(NOTE)[0]
    assert q.quote_text == "Mortality fell 12% across all strata."
    assert q.citekey == "smith2020" and q.locator == "p. 12"
    assert q.claim_id == "c-11111111" and q.in_managed is True


def test_inline_fields_and_free_region():
    inf = claims.parse_claims(NOTE)[2]
    assert inf.fields == {"confidence": "moderate", "status": "live"}
    assert inf.in_managed is False
    assert inf.locator is None


def test_open_question_may_lack_citation():
    oq = claims.parse_claims(NOTE)[3]
    assert oq.citekey is None and oq.claim_id == "c-44444444"


def test_claim_address():
    assert claims.claim_address("smith2020", "c-11111111") == "smith2020#^c-11111111"


def test_fixture_vault_parses(fixture_vault):
    text = (fixture_vault / "literatures" / "smith2020.md").read_text()
    assert len(claims.parse_claims(text)) >= 2
```

- [ ] **Step 2: Run test to verify it fails**

Run (first step in a fresh worktree — bootstrap the venv):
```bash
cd core && python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]" -q
python -m pytest tests/test_claims.py -v
```
Expected: FAIL — `No module named 'harness_core.claims'`

- [ ] **Step 3: Implement `claims.py` and the fixture**

```python
# core/harness_core/claims.py
"""Parser for §5 claim lines — the shared reader every checker and lint uses."""
import re
from dataclasses import dataclass, field

from .notes import MANAGED_OPEN, MANAGED_CLOSE

CLAIM_RE = re.compile(
    r"^- \((quote|paraphrase|inference|open-question)\) (?P<rest>.*)$")
CITE_RE = re.compile(r"\[@(?P<key>[A-Za-z0-9_.:-]+)(?:, (?P<loc>[^\]]+))?\]")
ANCHOR_RE = re.compile(r"\^(?P<id>[A-Za-z0-9-]+)\s*$")
# field values may contain [[wikilinks]] — the value class must admit them
# (a naive [^\]]* truncates '[[smith2020#^c-1]]' at its first ']')
FIELD_RE = re.compile(
    r"\[(?P<k>[A-Za-z-]+):: (?P<v>(?:[^\[\]]|\[\[[^\]]*\]\])*)\]")


@dataclass
class Claim:
    tag: str
    citekey: str | None
    locator: str | None
    claim_id: str | None
    line_no: int
    quote_text: str | None = None
    fields: dict = field(default_factory=dict)
    in_managed: bool = False


def claim_address(citekey: str, claim_id: str) -> str:
    return f"{citekey}#^{claim_id}"


def parse_claims(text: str) -> list[Claim]:
    out: list[Claim] = []
    managed = False
    for n, line in enumerate(text.split("\n"), start=1):
        if line.strip() == MANAGED_OPEN:
            managed = True
            continue
        if line.strip() == MANAGED_CLOSE:
            managed = False
            continue
        m = CLAIM_RE.match(line)
        if m:
            rest = m.group("rest")
            cite = CITE_RE.search(rest)
            anchor = ANCHOR_RE.search(rest)
            fields = {f.group("k"): f.group("v") for f in FIELD_RE.finditer(rest)
                      if not f.group("k") == ""}
            # [@...] and [k:: v] both bracket; drop the citation from fields if caught
            fields.pop("@", None)
            out.append(Claim(
                tag=m.group(1),
                citekey=cite.group("key") if cite else None,
                locator=cite.group("loc") if cite else None,
                claim_id=anchor.group("id") if anchor else None,
                line_no=n,
                in_managed=managed,
                fields=fields,
            ))
        elif out and line.startswith("  > ") and out[-1].tag == "quote":
            frag = line[4:]
            prev = out[-1].quote_text
            out[-1].quote_text = frag if prev is None else f"{prev} {frag}"
    return out
```

```python
# append to core/tests/conftest.py
import json as _json


@pytest.fixture
def fixture_vault(tmp_vault):
    lit = tmp_vault / "literatures"
    (lit / "smith2020.md").write_text("""---
citekey: "smith2020"
type: "literature"
doi: "10.1000/xyz"
retrieved: "2026-08-16"
attachment-sha256:
  - "aa11"
status: "active"
aliases:
  - "Mortality decline"
---
%%hk-managed%%
# Mortality decline

- (quote) [@smith2020, p. 12] ^c-11111111
  > Mortality fell 12% across all strata.
- (paraphrase) Retrospective design [@smith2020, p. 3] ^c-22222222
%%/hk-managed%%

## Notes
""")
    (lit / "gone2019.md").write_text("""---
citekey: "gone2019"
type: "literature"
doi: "10.1000/old"
retrieved: "2026-08-16"
status: "superseded"
superseded-by: "smith2020"
---
%%hk-managed%%
# Old result
%%/hk-managed%%

## Notes
""")
    (tmp_vault / "atlas" / "index.md").write_text(
        "# Atlas index\n\n- [[mortality-trends]] — mortality synthesis\n")
    (tmp_vault / "atlas" / "mortality-trends.md").write_text("""---
title: "Mortality trends"
type: "topic"
---
- (inference) Decline is robust [confidence:: moderate] [supported-by:: [[smith2020#^c-11111111]]] [contested-by:: [[gone2019#^c-22222222]]] ^c-55555555
""")
    eff = tmp_vault / "efforts" / "brief"
    eff.mkdir()
    (eff / "draft.md").write_text("""---
title: "Evidence brief"
type: "effort"
status: "drafting"
---
- (quote) [@smith2020, p. 12] ^c-66666666
  > Mortality fell 12% across all strata.
- (inference) This will replicate [@fabricated2020] ^c-77777777
""")
    (tmp_vault / "x" / "bibliography.json").write_text(_json.dumps([
        {"id": "gone2019", "title": "Old result", "type": "article-journal",
         "DOI": "10.1000/old",
         "author": [{"family": "Gone", "given": "Ann"}],
         "issued": {"date-parts": [[2019]]}},
        {"id": "smith2020", "title": "Mortality decline", "type": "article-journal",
         "DOI": "10.1000/xyz",
         "author": [{"family": "Smith", "given": "Jo"}],
         "issued": {"date-parts": [[2020]]}},
    ], indent=1))
    (tmp_vault / "calendar" / "2026-08-16.md").write_text(
        "- 09:00 human:eran — imported smith2020\n")
    (tmp_vault / "+" / "review-queue.md").write_text("")
    subprocess.run(["git", "add", "-A"], cwd=tmp_vault, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "fixture vault"], cwd=tmp_vault,
                   check=True)
    return tmp_vault
```

(`conftest.py` already imports `subprocess` and `pytest` from Plan A.)

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_claims.py -v`
Expected: 6 PASS

- [ ] **Step 5: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add core && git commit -m "feat: claim parser + populated fixture vault"
```

---

### Task 2: Review inbox

**Files:**
- Create: `core/harness_core/inbox.py`
- Test: `core/tests/test_inbox.py`

**Interfaces:**
- Consumes: `frontmatter`-style inline-field syntax conventions (§3); nothing from Plan B yet.
- Produces:
  - `INBOX_PATH = "+/review-queue.md"`.
  - `@dataclass Entry`: `id, check, target, result, date, actor, reason, ack_of: str | None, target_hash: str | None`.
  - `append_entry(vault, check, target, result: Result, reason: str, actor: str = AGENT_ACTOR, date: str | None = None, target_hash: str | None = None, notice_date: str | None = None, detection_date: str | None = None) -> Entry` — id = `f"{check}/{target}/{date}"`; serializes one line per §3; the two optional dates serialize as `[notice-date:: …]` / `[detection-date:: …]` — the §6 bi-temporal record for update-notice entries. Implement exactly like `target_hash`: two more optional dataclass fields, serializer entries, parser keys.
  - `append_ack(vault, entry_id, reason, actor, target_hash=None) -> Entry` — raises `ValueError` unless `actor.startswith("human:")`.
  - `load(vault) -> list[Entry]` — parses both entry kinds; unparseable lines raise `InboxError`.
  - `is_acknowledged(vault, check, target, current_hash=None) -> bool` — a matching ack exists for the check+target's latest entry AND (`current_hash is None` or the ack's `target_hash == current_hash`) — the §3 standing-until-content-changes scope.
  - `summary(vault) -> dict` — `{"unacknowledged": int, "oldest": "YYYY-MM-DD" | None}` for the orientation surface.

- [ ] **Step 1: Write the failing test**

```python
# core/tests/test_inbox.py
import pytest

from harness_core import Result, inbox


def test_append_and_load(fixture_vault):
    e = inbox.append_entry(fixture_vault, "doi", "smith2020", Result.UNMATCHED,
                           "mismatch — title differs", date="2026-08-16")
    entries = inbox.load(fixture_vault)
    assert entries[-1].id == "doi/smith2020/2026-08-16"
    assert entries[-1].result == "UNMATCHED"
    assert entries[-1].reason.startswith("mismatch")
    line = (fixture_vault / "+" / "review-queue.md").read_text().splitlines()[-1]
    assert line.startswith("- [id:: doi/smith2020/2026-08-16]")


def test_ack_requires_human(fixture_vault):
    e = inbox.append_entry(fixture_vault, "doi", "smith2020", Result.UNMATCHED,
                           "mismatch", date="2026-08-16")
    with pytest.raises(ValueError):
        inbox.append_ack(fixture_vault, e.id, "looks fine", actor="harness_core/0.1.0")
    inbox.append_ack(fixture_vault, e.id, "verified by hand", actor="human:eran")
    assert inbox.is_acknowledged(fixture_vault, "doi", "smith2020")


def test_ack_scope_invalidated_by_hash_change(fixture_vault):
    e = inbox.append_entry(fixture_vault, "quote", "smith2020#^c-11111111",
                           Result.UNMATCHED, "fuzzy-quote", date="2026-08-16",
                           target_hash="aa11")
    inbox.append_ack(fixture_vault, e.id, "manual check ok", actor="human:eran",
                     target_hash="aa11")
    assert inbox.is_acknowledged(fixture_vault, "quote", "smith2020#^c-11111111",
                                 current_hash="aa11")
    assert not inbox.is_acknowledged(fixture_vault, "quote", "smith2020#^c-11111111",
                                     current_hash="bb22")


def test_summary_counts_and_age(fixture_vault):
    inbox.append_entry(fixture_vault, "doi", "a", Result.UNMATCHED, "mismatch",
                       date="2026-08-01")
    inbox.append_entry(fixture_vault, "doi", "b", Result.UNREACHABLE, "outage",
                       date="2026-08-16")
    s = inbox.summary(fixture_vault)
    assert s == {"unacknowledged": 2, "oldest": "2026-08-01"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_inbox.py -v`
Expected: FAIL — `No module named 'harness_core.inbox'`

- [ ] **Step 3: Implement**

```python
# core/harness_core/inbox.py
"""The shared review inbox: +/review-queue.md (spec §3)."""
import datetime
import re
from dataclasses import dataclass
from pathlib import Path

from . import AGENT_ACTOR, Result

INBOX_PATH = "+/review-queue.md"
_FIELD = re.compile(r"\[(?P<k>[a-z-]+):: (?P<v>[^\]]*)\]")


class InboxError(ValueError):
    pass


@dataclass
class Entry:
    id: str
    check: str = ""
    target: str = ""
    result: str = ""
    date: str = ""
    actor: str = ""
    reason: str = ""
    ack_of: str | None = None
    target_hash: str | None = None


def _file(vault) -> Path:
    return Path(vault) / INBOX_PATH


def _serialize(fields: list[tuple[str, str]]) -> str:
    return "- " + " ".join(f"[{k}:: {v}]" for k, v in fields if v) + "\n"


def append_entry(vault, check, target, result: Result, reason, actor=AGENT_ACTOR,
                 date=None, target_hash=None) -> Entry:
    date = date or datetime.date.today().isoformat()
    e = Entry(id=f"{check}/{target}/{date}", check=check, target=target,
              result=result.value, date=date, actor=actor, reason=reason,
              target_hash=target_hash)
    fields = [("id", e.id), ("check", check), ("target", target),
              ("result", e.result), ("date", date), ("actor", actor),
              ("reason", reason)]
    if target_hash:
        fields.append(("target-hash", target_hash))
    with _file(vault).open("a") as f:
        f.write(_serialize(fields))
    return e


def append_ack(vault, entry_id, reason, actor, target_hash=None) -> Entry:
    if not actor.startswith("human:"):
        raise ValueError(f"acknowledgment requires a human: actor, got {actor!r}")
    e = Entry(id=f"ack/{entry_id}", ack_of=entry_id, actor=actor, reason=reason,
              target_hash=target_hash)
    fields = [("ack", entry_id), ("actor", actor), ("reason", reason)]
    if target_hash:
        fields.append(("target-hash", target_hash))
    with _file(vault).open("a") as f:
        f.write(_serialize(fields))
    return e


def load(vault) -> list[Entry]:
    out = []
    for n, line in enumerate(_file(vault).read_text().splitlines(), start=1):
        if not line.strip():
            continue
        d = {m.group("k"): m.group("v") for m in _FIELD.finditer(line)}
        if "ack" in d:
            out.append(Entry(id=f"ack/{d['ack']}", ack_of=d["ack"],
                             actor=d.get("actor", ""), reason=d.get("reason", ""),
                             target_hash=d.get("target-hash")))
        elif "id" in d:
            out.append(Entry(id=d["id"], check=d.get("check", ""),
                             target=d.get("target", ""), result=d.get("result", ""),
                             date=d.get("date", ""), actor=d.get("actor", ""),
                             reason=d.get("reason", ""),
                             target_hash=d.get("target-hash")))
        else:
            raise InboxError(f"unparseable inbox line {n}: {line!r}")
    return out


def is_acknowledged(vault, check, target, current_hash=None) -> bool:
    entries = load(vault)
    latest = None
    for e in entries:
        if e.ack_of is None and e.check == check and e.target == target:
            latest = e
    if latest is None:
        return False
    for e in entries:
        if e.ack_of == latest.id:
            if current_hash is None or e.target_hash == current_hash:
                return True
    return False


def summary(vault) -> dict:
    entries = load(vault)
    acked = {e.ack_of for e in entries if e.ack_of}
    open_entries = [e for e in entries if e.ack_of is None and e.id not in acked]
    oldest = min((e.date for e in open_entries if e.date), default=None)
    return {"unacknowledged": len(open_entries), "oldest": oldest}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_inbox.py -v`
Expected: 4 PASS

- [ ] **Step 5: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add core && git commit -m "feat: review inbox — entries, human acks, standing scope, summary"
```

---

### Task 3: Verified events + trust tier

**Files:**
- Create: `core/harness_core/events.py`
- Test: `core/tests/test_events.py`

**Interfaces:**
- Consumes: `frontmatter.parse/serialize`; `claims.parse_claims`; `Result`; `AGENT_ACTOR`.
- Produces:
  - `record_pass(note_text: str, check: str, result: Result, by: str = AGENT_ACTOR, at: str | None = None) -> str` — appends `{by, at, check}` to the frontmatter `verified` list and returns new note text; **raises `ValueError` unless `result is Result.MATCHED`** (§5: only MATCHED mints events). `check` strings: `"doi"`, `"metadata"`, `"update-notice"`, `"quote:<claim_address>:<managed-region|source-text>"`.
  - `verified_checks(note_text: str) -> list[dict]`.
  - `trust_tier(note_text: str) -> str` — compute the machine-confirmed predicate first: events cover every **applicable** note-level check (applicable = `doi`/`metadata`/`update-notice` only when frontmatter carries a `doi` — a DOI-less web source has none applicable, per §5 "all applicable") AND every managed quote claim has a `quote:<its address>:` event. `"human-reviewed"` = the predicate AND a `human:` event (tiers are cumulative — a human event without machine coverage is NOT human-reviewed); `"machine-confirmed"` = the predicate alone; else `"unverified"`.

- [ ] **Step 1: Write the failing test**

```python
# core/tests/test_events.py
import pytest

from harness_core import Result, events


BASE = """---
citekey: "smith2020"
type: "literature"
---
%%hk-managed%%
- (quote) [@smith2020, p. 12] ^c-11111111
  > Mortality fell 12% across all strata.
%%/hk-managed%%
"""


def test_record_pass_appends_event():
    out = events.record_pass(BASE, "doi", Result.MATCHED, at="2026-08-16")
    evs = events.verified_checks(out)
    assert evs == [{"by": "harness_core/0.1.0", "at": "2026-08-16", "check": "doi"}]


def test_record_pass_rejects_non_matched():
    for r in (Result.UNMATCHED, Result.UNREACHABLE, Result.SKIPPED):
        with pytest.raises(ValueError):
            events.record_pass(BASE, "doi", r)


def test_trust_tier_progression():
    assert events.trust_tier(BASE) == "unverified"
    t = BASE
    for check in ("doi", "metadata", "update-notice"):
        t = events.record_pass(t, check, Result.MATCHED, at="2026-08-16")
    assert events.trust_tier(t) == "unverified"      # quote claim still unverified
    t = events.record_pass(
        t, "quote:smith2020#^c-11111111:managed-region", Result.MATCHED,
        at="2026-08-16")
    assert events.trust_tier(t) == "machine-confirmed"
    t = events.record_pass(t, "doi", Result.MATCHED, by="human:eran", at="2026-08-17")
    assert events.trust_tier(t) == "human-reviewed"


def test_human_event_alone_is_not_human_reviewed():
    t = events.record_pass(BASE, "doi", Result.MATCHED, by="human:eran",
                           at="2026-08-16")
    assert events.trust_tier(t) == "unverified"
```

(The `BASE` fixture note carries no `doi` frontmatter, so its applicable note-level set is empty — `test_trust_tier_progression` must therefore add `doi: "10.1000/xyz"` to `BASE`'s frontmatter for the doi/metadata/update-notice legs to be applicable; update the fixture string accordingly.)

- [ ] **Step 2: Run test to verify it fails**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_events.py -v`
Expected: FAIL — `No module named 'harness_core.events'`

- [ ] **Step 3: Implement**

```python
# core/harness_core/events.py
"""Verified events + trust-tier derivation (spec §5)."""
import datetime

from . import AGENT_ACTOR, Result
from . import claims as claims_mod
from . import frontmatter


def record_pass(note_text, check, result: Result, by=AGENT_ACTOR, at=None) -> str:
    if result is not Result.MATCHED:
        raise ValueError(f"only MATCHED mints verified events, got {result}")
    data, body = frontmatter.parse(note_text)
    events = list(data.get("verified", []))
    events.append({"by": by, "at": at or datetime.date.today().isoformat(),
                   "check": check})
    data["verified"] = events
    return frontmatter.serialize(data) + body


def verified_checks(note_text) -> list[dict]:
    data, _ = frontmatter.parse(note_text)
    return list(data.get("verified", []))


def trust_tier(note_text) -> str:
    evs = verified_checks(note_text)
    checks = {str(e.get("check", "")) for e in evs}
    data, _ = frontmatter.parse(note_text)
    applicable = {"doi", "metadata", "update-notice"} if data.get("doi") else set()
    machine = applicable <= checks
    citekey = data.get("citekey", "")
    for c in claims_mod.parse_claims(note_text):
        if c.tag == "quote" and c.in_managed and c.claim_id:
            addr = claims_mod.claim_address(citekey, c.claim_id)
            if not any(ch.startswith(f"quote:{addr}:") for ch in checks):
                machine = False
    if not machine:
        return "unverified"
    if any(str(e.get("by", "")).startswith("human:") for e in evs):
        return "human-reviewed"
    return "machine-confirmed"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_events.py -v`
Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add core && git commit -m "feat: verified events (MATCHED-only) + trust-tier derivation"
```

---

### Task 4: Polite four-state HTTP layer

**Files:**
- Create: `core/harness_core/webapi.py`
- Test: `core/tests/test_webapi.py`

**Interfaces:**
- Consumes: `paths.load_machine_config`; `Result`.
- Produces:
  - `class ApiError(Exception)` with `.result = Result.UNREACHABLE`.
  - `mailto(vault_root) -> str` — machine.json `mailto` key, else env `HARNESS_MAILTO`, else raise `ApiError` (polite pools are not optional, §6).
  - `get_json(url: str, vault_root, params: dict | None = None, headers: dict | None = None, timeout: float = 10.0) -> tuple[int, object]` — GET with `mailto` merged into query params and a UA `harness_core/<version> (mailto:<addr>)`; returns `(status, decoded_json)`; network failure or undecodable body raises `ApiError` (UNREACHABLE — malformed JSON is an outage, never a verdict). 404 returns `(404, None)`.
  - `_urlopen` module-level indirection (patchable in tests).

- [ ] **Step 1: Write the failing test**

```python
# core/tests/test_webapi.py
import io
import json

import pytest

from harness_core import Result, webapi


class FakeResponse(io.BytesIO):
    def __init__(self, payload, status=200):
        super().__init__(payload if isinstance(payload, bytes)
                         else json.dumps(payload).encode())
        self.status = status
    def __enter__(self):
        return self
    def __exit__(self, *a):
        return False


@pytest.fixture
def vault_with_mailto(fixture_vault):
    h = fixture_vault / ".harness"
    h.mkdir(exist_ok=True)
    (h / "machine.json").write_text('{"mailto": "eran@example.edu"}')
    return fixture_vault


def test_mailto_required(fixture_vault, monkeypatch):
    monkeypatch.delenv("HARNESS_MAILTO", raising=False)
    with pytest.raises(webapi.ApiError):
        webapi.mailto(fixture_vault)


def test_get_json_sends_mailto(vault_with_mailto, monkeypatch):
    seen = {}
    def fake_urlopen(req, timeout):
        seen["url"] = req.full_url
        seen["ua"] = req.get_header("User-agent")
        return FakeResponse({"ok": True})
    monkeypatch.setattr(webapi, "_urlopen", fake_urlopen)
    status, data = webapi.get_json("https://api.crossref.org/works/10.1/x",
                                   vault_with_mailto)
    assert status == 200 and data == {"ok": True}
    assert "mailto=eran%40example.edu" in seen["url"]
    assert "harness_core/" in seen["ua"] and "eran@example.edu" in seen["ua"]


def test_malformed_json_is_unreachable(vault_with_mailto, monkeypatch):
    monkeypatch.setattr(webapi, "_urlopen",
                        lambda req, timeout: FakeResponse(b"<html>rate limited"))
    with pytest.raises(webapi.ApiError) as e:
        webapi.get_json("https://x", vault_with_mailto)
    assert e.value.result is Result.UNREACHABLE


def test_404_returns_none(vault_with_mailto, monkeypatch):
    import urllib.error
    def fake_urlopen(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 404, "nf", {}, io.BytesIO(b""))
    monkeypatch.setattr(webapi, "_urlopen", fake_urlopen)
    status, data = webapi.get_json("https://x", vault_with_mailto)
    assert status == 404 and data is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_webapi.py -v`
Expected: FAIL — `No module named 'harness_core.webapi'`

- [ ] **Step 3: Implement**

```python
# core/harness_core/webapi.py
"""Polite four-state HTTP layer for external verification APIs (spec §6)."""
import json
import os
import urllib.error
import urllib.parse
import urllib.request

from . import Result, __version__
from .paths import load_machine_config


class ApiError(Exception):
    result = Result.UNREACHABLE


def _urlopen(req, timeout):
    return urllib.request.urlopen(req, timeout=timeout)


def mailto(vault_root) -> str:
    addr = load_machine_config(vault_root).get("mailto") or os.environ.get(
        "HARNESS_MAILTO")
    if not addr:
        raise ApiError("no mailto configured (.harness/machine.json or "
                       "HARNESS_MAILTO) — polite pools are mandatory")
    return addr


def get_json(url, vault_root, params=None, headers=None, timeout=10.0):
    addr = mailto(vault_root)
    q = dict(params or {})
    q.setdefault("mailto", addr)
    full = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(q)
    req = urllib.request.Request(full, headers={
        "User-Agent": f"harness_core/{__version__} (mailto:{addr})",
        **(headers or {})})
    try:
        with _urlopen(req, timeout) as resp:
            body = resp.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return 404, None
        raise ApiError(f"HTTP {e.code} from {url}") from e
    except OSError as e:
        raise ApiError(f"network failure: {e}") from e
    try:
        return 200, json.loads(body)
    except ValueError as e:
        raise ApiError(f"undecodable body from {url}") from e
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_webapi.py -v`
Expected: 4 PASS

- [ ] **Step 5: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add core && git commit -m "feat: polite four-state HTTP layer (mailto mandatory, outage never a verdict)"
```

---

### Task 5: Citekey check

**Files:**
- Create: `core/harness_core/checks.py`
- Test: `core/tests/test_checks.py`

**Interfaces:**
- Consumes: `bibliography.load`, `claims.parse_claims`, `Result`.
- Produces:
  - `@dataclass Outcome`: `check: str`, `target: str`, `result: Result`, `reason: str` (opens with a reason code), `extra: dict` (bi-temporal dates, matched metadata, …).
  - `check_citekeys(vault_root, note_path: Path) -> list[Outcome]` — one Outcome per cited citekey in the note: MATCHED when in the bibliography universe; UNMATCHED (`reason "mismatch — citekey not in bibliography"`) otherwise; SKIPPED for a note with no citations (single Outcome, target = note path).

- [ ] **Step 1: Write the failing test**

```python
# core/tests/test_checks.py
from harness_core import Result, checks


def test_citekey_check_mixed(fixture_vault):
    outs = checks.check_citekeys(fixture_vault,
                                 fixture_vault / "efforts" / "brief" / "draft.md")
    by_target = {o.target: o.result for o in outs}
    assert by_target["smith2020"] is Result.MATCHED
    assert by_target["fabricated2020"] is Result.UNMATCHED


def test_citekey_check_skipped_when_no_citations(fixture_vault):
    p = fixture_vault / "atlas" / "index.md"
    outs = checks.check_citekeys(fixture_vault, p)
    assert len(outs) == 1 and outs[0].result is Result.SKIPPED
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_checks.py -v`
Expected: FAIL — `No module named 'harness_core.checks'`

- [ ] **Step 3: Implement**

```python
# core/harness_core/checks.py
"""Citation checkers (spec §6). Shared Outcome dataclass; four-state everywhere."""
from dataclasses import dataclass, field
from pathlib import Path

from . import Result
from . import bibliography, claims


@dataclass
class Outcome:
    check: str
    target: str
    result: Result
    reason: str = ""
    extra: dict = field(default_factory=dict)


def check_citekeys(vault_root, note_path: Path) -> list[Outcome]:
    bib = bibliography.load(vault_root)
    cited = {c.citekey for c in claims.parse_claims(Path(note_path).read_text())
             if c.citekey}
    if not cited:
        return [Outcome("citekey", str(note_path), Result.SKIPPED,
                        "no-identifier — note cites nothing")]
    out = []
    for key in sorted(cited):
        if key in bib.citekeys:
            out.append(Outcome("citekey", key, Result.MATCHED, "matched"))
        else:
            out.append(Outcome("citekey", key, Result.UNMATCHED,
                               "mismatch — citekey not in bibliography"))
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_checks.py -v`
Expected: 2 PASS

- [ ] **Step 5: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add core && git commit -m "feat: citekey check with four-state outcomes"
```

---

### Task 6: DOI existence + registry routing

**Files:**
- Modify: `core/harness_core/checks.py`
- Test: `core/tests/test_checks.py` (append)

**Interfaces:**
- Consumes: `webapi.get_json`, `webapi.ApiError`.
- Produces:
  - `check_doi_exists(vault_root, doi: str) -> Outcome` — `GET https://doi.org/api/handles/{doi}`: `responseCode == 1` ⇒ MATCHED; `responseCode == 100` or HTTP 404 ⇒ UNMATCHED (`"mismatch — DOI does not resolve"`); ApiError ⇒ UNREACHABLE (`"outage — …"`).
  - `registry_agency(vault_root, doi: str) -> str | None` — `GET https://doi.org/doiRA/{doi}` ⇒ `"Crossref" | "DataCite" | …`; None on UNREACHABLE.
  - Both accept notes without a `doi`: callers pass only real DOIs; SKIPPED handling stays in the orchestrator (Task 13).

- [ ] **Step 1: Write the failing test (append to test_checks.py)**

```python
# append to core/tests/test_checks.py
import pytest

from harness_core import webapi


@pytest.fixture
def net_vault(fixture_vault):
    h = fixture_vault / ".harness"
    h.mkdir(exist_ok=True)
    (h / "machine.json").write_text('{"mailto": "eran@example.edu"}')
    return fixture_vault


def _fake_get(monkeypatch, table):
    """table: {url-substring: (status, payload) or ApiError instance}"""
    def fake(url, vault_root, params=None, headers=None, timeout=10.0):
        for frag, resp in table.items():
            if frag in url:
                if isinstance(resp, Exception):
                    raise resp
                return resp
        raise AssertionError(f"unexpected url {url}")
    monkeypatch.setattr(webapi, "get_json", fake)
    # checks.py imports the module, not the symbol — patching webapi.get_json suffices


def test_doi_exists_matched(net_vault, monkeypatch):
    _fake_get(monkeypatch, {"doi.org/api/handles/10.1000/xyz":
                            (200, {"responseCode": 1})})
    o = checks.check_doi_exists(net_vault, "10.1000/xyz")
    assert o.result is Result.MATCHED


def test_doi_exists_unmatched_on_100(net_vault, monkeypatch):
    _fake_get(monkeypatch, {"doi.org/api/handles/10.1/fake":
                            (200, {"responseCode": 100})})
    o = checks.check_doi_exists(net_vault, "10.1/fake")
    assert o.result is Result.UNMATCHED and o.reason.startswith("mismatch")


def test_doi_exists_unreachable(net_vault, monkeypatch):
    _fake_get(monkeypatch, {"doi.org/api/handles/10.1000/xyz":
                            webapi.ApiError("down")})
    o = checks.check_doi_exists(net_vault, "10.1000/xyz")
    assert o.result is Result.UNREACHABLE and o.reason.startswith("outage")


def test_registry_agency(net_vault, monkeypatch):
    _fake_get(monkeypatch, {"doi.org/doiRA/10.5281/zenodo.1":
                            (200, [{"DOI": "10.5281/zenodo.1", "RA": "DataCite"}])})
    assert checks.registry_agency(net_vault, "10.5281/zenodo.1") == "DataCite"
```

- [ ] **Step 2: Run to verify the new tests fail**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_checks.py -v`
Expected: new tests FAIL (`AttributeError: check_doi_exists`); Task 5 tests PASS

- [ ] **Step 3: Implement (append to checks.py)**

```python
# append to core/harness_core/checks.py
from . import webapi


def check_doi_exists(vault_root, doi: str) -> Outcome:
    try:
        status, data = webapi.get_json(
            f"https://doi.org/api/handles/{doi}", vault_root)
    except webapi.ApiError as e:
        return Outcome("doi", doi, Result.UNREACHABLE, f"outage — {e}")
    if status == 404 or (isinstance(data, dict) and data.get("responseCode") == 100):
        return Outcome("doi", doi, Result.UNMATCHED,
                       "mismatch — DOI does not resolve")
    if isinstance(data, dict) and data.get("responseCode") == 1:
        return Outcome("doi", doi, Result.MATCHED, "matched")
    return Outcome("doi", doi, Result.UNREACHABLE,
                   f"outage — unexpected handle payload {data!r}")


def registry_agency(vault_root, doi: str):
    try:
        status, data = webapi.get_json(f"https://doi.org/doiRA/{doi}", vault_root)
    except webapi.ApiError:
        return None
    if status == 200 and isinstance(data, list) and data and "RA" in data[0]:
        return data[0]["RA"]
    return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_checks.py -v`
Expected: all PASS

- [ ] **Step 5: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add core && git commit -m "feat: DOI existence check + registry-agency routing"
```

---

### Task 7: Metadata match

**Files:**
- Modify: `core/harness_core/checks.py`
- Test: `core/tests/test_checks.py` (append)

**Interfaces:**
- Consumes: `webapi`, `registry_agency` (Task 6), `bibliography.load`.
- Produces:
  - `normalize_text(s: str) -> str` — NFKC, casefold, collapse whitespace, strip soft hyphens (`­`) and join hyphen-linebreaks — **the one normalization pipeline**, exported for reuse by quotes (Task 10) per §6 ("same normalization pipeline as quotes").
  - `check_metadata(vault_root, entry: dict) -> Outcome` — `entry` is a CSL item from the bibliography. No DOI ⇒ SKIPPED. Crossref-registered ⇒ `GET api.crossref.org/works/{doi}`; other registries ⇒ DOI content negotiation (`https://doi.org/{doi}`, `Accept: application/vnd.citationstyles.csl+json`). Compare: normalized titles equal; author family names as an ordered list equal after normalization, given names matching on first initial when both present (§6 author rule); year equal when both sides carry one. All agree ⇒ MATCHED; any divergence ⇒ UNMATCHED with `"mismatch — <field>"` (**no closure** — orchestrator routes to inbox only, §6); UNREACHABLE on ApiError.

- [ ] **Step 1: Write the failing test (append)**

```python
# append to core/tests/test_checks.py
CROSSREF_OK = (200, {"message": {
    "title": ["Mortality  decline"],
    "author": [{"family": "Smith", "given": "Jo"}],
    "issued": {"date-parts": [[2020]]},
}})


def test_metadata_matched(net_vault, monkeypatch):
    _fake_get(monkeypatch, {
        "doi.org/doiRA/10.1000/xyz": (200, [{"RA": "Crossref"}]),
        "api.crossref.org/works/10.1000/xyz": CROSSREF_OK,
    })
    entry = {"id": "smith2020", "DOI": "10.1000/xyz", "title": "Mortality decline",
             "author": [{"family": "Smith", "given": "Jo"}],
             "issued": {"date-parts": [[2020]]}}
    o = checks.check_metadata(net_vault, entry)
    assert o.result is Result.MATCHED


def test_metadata_title_mismatch(net_vault, monkeypatch):
    _fake_get(monkeypatch, {
        "doi.org/doiRA/10.1000/xyz": (200, [{"RA": "Crossref"}]),
        "api.crossref.org/works/10.1000/xyz": (200, {"message": {
            "title": ["A completely different paper"],
            "author": [{"family": "Smith", "given": "Jo"}],
            "issued": {"date-parts": [[2020]]}}}),
    })
    entry = {"id": "smith2020", "DOI": "10.1000/xyz", "title": "Mortality decline",
             "author": [{"family": "Smith", "given": "Jo"}]}
    o = checks.check_metadata(net_vault, entry)
    assert o.result is Result.UNMATCHED and "title" in o.reason


def test_metadata_author_initial_rule(net_vault, monkeypatch):
    _fake_get(monkeypatch, {
        "doi.org/doiRA/10.1000/xyz": (200, [{"RA": "Crossref"}]),
        "api.crossref.org/works/10.1000/xyz": (200, {"message": {
            "title": ["Mortality decline"],
            "author": [{"family": "Smith", "given": "Josephine"}],
            "issued": {"date-parts": [[2020]]}}}),
    })
    entry = {"id": "smith2020", "DOI": "10.1000/xyz", "title": "Mortality decline",
             "author": [{"family": "Smith", "given": "J."}]}
    assert checks.check_metadata(net_vault, entry).result is Result.MATCHED


def test_metadata_datacite_content_negotiation(net_vault, monkeypatch):
    _fake_get(monkeypatch, {
        "doi.org/doiRA/10.5281/z.1": (200, [{"RA": "DataCite"}]),
        "doi.org/10.5281/z.1": (200, {
            "title": "Dataset of mortality",
            "author": [{"family": "Smith"}]}),
    })
    entry = {"id": "smithdata", "DOI": "10.5281/z.1", "title": "Dataset of mortality",
             "author": [{"family": "Smith"}]}
    assert checks.check_metadata(net_vault, entry).result is Result.MATCHED


def test_metadata_skipped_without_doi(net_vault):
    o = checks.check_metadata(net_vault, {"id": "webonly2024", "title": "Blog"})
    assert o.result is Result.SKIPPED
```

- [ ] **Step 2: Run to verify the new tests fail**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_checks.py -v`
Expected: new tests FAIL (`AttributeError: check_metadata`)

- [ ] **Step 3: Implement (append to checks.py)**

```python
# append to core/harness_core/checks.py
import re as _re
import unicodedata


def normalize_text(s: str) -> str:
    """The §6 quote pipeline: NFKC + soft-hyphen strip + dehyphenation +
    whitespace collapse. NO casefold — a case-mutated quote must not pass
    as exact (§9 mutated-quote drill). Metadata comparison casefolds locally."""
    s = unicodedata.normalize("NFKC", s or "")
    s = s.replace("­", "").replace("-\n", "")
    return " ".join(s.split())


def _cmp(s: str) -> str:
    return normalize_text(s).casefold()


def _authors(csl_authors):
    out = []
    for a in csl_authors or []:
        fam = _cmp(a.get("family", ""))
        giv = _cmp(a.get("given", ""))
        out.append((fam, giv[:1]))
    return out


def _year(csl_item):
    parts = (csl_item.get("issued") or {}).get("date-parts") or []
    return parts[0][0] if parts and parts[0] else None


def check_metadata(vault_root, entry: dict) -> Outcome:
    doi = entry.get("DOI") or entry.get("doi")
    if not doi:
        return Outcome("metadata", entry.get("id", "?"), Result.SKIPPED,
                       "no-identifier — item has no DOI")
    agency = registry_agency(vault_root, doi)
    try:
        if agency == "Crossref":
            status, data = webapi.get_json(
                f"https://api.crossref.org/works/{doi}", vault_root)
            remote = (data or {}).get("message", {}) if status == 200 else None
            if remote and isinstance(remote.get("title"), list):
                remote = dict(remote, title=(remote["title"] or [""])[0])
        else:
            status, remote = webapi.get_json(
                f"https://doi.org/{doi}", vault_root,
                headers={"Accept": "application/vnd.citationstyles.csl+json"})
    except webapi.ApiError as e:
        return Outcome("metadata", entry["id"], Result.UNREACHABLE, f"outage — {e}")
    if status == 404 or remote is None:
        return Outcome("metadata", entry["id"], Result.UNREACHABLE,
                       "outage — registry record unavailable")

    if _cmp(str(remote.get("title", ""))) != _cmp(str(entry.get("title", ""))):
        return Outcome("metadata", entry["id"], Result.UNMATCHED,
                       "mismatch — title differs from registry")
    ours, theirs = _authors(entry.get("author")), _authors(remote.get("author"))
    if [f for f, _ in ours] != [f for f, _ in theirs]:
        return Outcome("metadata", entry["id"], Result.UNMATCHED,
                       "mismatch — author family names differ")
    for (f1, g1), (f2, g2) in zip(ours, theirs):
        if g1 and g2 and g1 != g2:
            return Outcome("metadata", entry["id"], Result.UNMATCHED,
                           "mismatch — author given-name initials differ")
    y1, y2 = _year(entry), _year(remote)
    if y1 and y2 and y1 != y2:
        return Outcome("metadata", entry["id"], Result.UNMATCHED,
                       "mismatch — year differs")
    return Outcome("metadata", entry["id"], Result.MATCHED, "matched",
                   extra={"agency": agency or "unknown"})
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_checks.py -v`
Expected: all PASS

- [ ] **Step 5: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add core && git commit -m "feat: metadata match with registry routing + author rule"
```

---

### Task 8: Update-notice check (full taxonomy, bi-temporal, RW CSV)

**Files:**
- Modify: `core/harness_core/checks.py`
- Test: `core/tests/test_checks.py` (append)

**Interfaces:**
- Consumes: `webapi`, `registry_agency`.
- Produces:
  - `BLOCKING_TYPES = {"retraction", "partial_retraction", "removal", "withdrawal"}`; `WARN_TYPES = {"expression_of_concern", "correction", "corrigendum", "erratum"}`.
  - `check_update_notice(vault_root, entry: dict, detection_date: str) -> Outcome` — Crossref-registered: read `updated-by[]` from `api.crossref.org/works/{doi}`; normalize `type` (lowercase, spaces→underscores). Any blocking-type ⇒ UNMATCHED, reason `"retracted — <type>"`, `extra = {"notice_date": "YYYY-MM-DD", "detection_date": …, "class": "blocking", "type": …}` (bi-temporal, §6); a later `reinstatement` clears earlier blocking notices; warn-types only ⇒ MATCHED with `extra["warn_notices"] = [{type, notice_date}]` (orchestrator files them to the inbox — warn, never closure); none ⇒ MATCHED. Non-Crossref: OpenAlex `GET api.openalex.org/works/https://doi.org/{doi}` with `select=is_retracted` — `is_retracted` ⇒ UNMATCHED (notice date unknown ⇒ `notice_date: null`); else MATCHED. No DOI **and** no PMID ⇒ SKIPPED.
  - `load_rw_csv(path: Path) -> dict` — parses a Retraction Watch CSV (columns incl. `OriginalPaperDOI`, `OriginalPaperPubMedID`, `RetractionDate`, `RetractionNature`) into `{"doi": {...}, "pmid": {...}}` lookup maps.
  - `check_rw_batch(entry: dict, rw: dict, detection_date: str) -> Outcome | None` — offline batch leg: match on DOI **or** PMID; blocking natures (`Retraction`) ⇒ UNMATCHED with bi-temporal extra; `Expression of concern` ⇒ MATCHED + warn extra; no match ⇒ None (no Outcome — the live leg governs).

- [ ] **Step 1: Write the failing test (append)**

```python
# append to core/tests/test_checks.py
def _works(payload):
    return (200, {"message": payload})


def test_notice_blocking_retraction(net_vault, monkeypatch):
    _fake_get(monkeypatch, {
        "doi.org/doiRA/10.1000/xyz": (200, [{"RA": "Crossref"}]),
        "api.crossref.org/works/10.1000/xyz": _works({
            "updated-by": [
                {"type": "correction", "updated": {"date-parts": [[2004, 3, 6]]}},
                {"type": "retraction", "updated": {"date-parts": [[2010, 2, 2]]}},
            ]}),
    })
    o = checks.check_update_notice(net_vault, {"id": "x", "DOI": "10.1000/xyz"},
                                   detection_date="2026-08-16")
    assert o.result is Result.UNMATCHED
    assert o.reason.startswith("retracted — retraction")
    assert o.extra["notice_date"] == "2010-02-02"
    assert o.extra["detection_date"] == "2026-08-16"


def test_notice_warn_class_is_matched_with_warns(net_vault, monkeypatch):
    _fake_get(monkeypatch, {
        "doi.org/doiRA/10.1000/xyz": (200, [{"RA": "Crossref"}]),
        "api.crossref.org/works/10.1000/xyz": _works({
            "updated-by": [{"type": "expression_of_concern",
                            "updated": {"date-parts": [[2023, 1, 1]]}}]}),
    })
    o = checks.check_update_notice(net_vault, {"id": "x", "DOI": "10.1000/xyz"},
                                   "2026-08-16")
    assert o.result is Result.MATCHED
    assert o.extra["warn_notices"] == [
        {"type": "expression_of_concern", "notice_date": "2023-01-01"}]


def test_notice_reinstatement_clears(net_vault, monkeypatch):
    _fake_get(monkeypatch, {
        "doi.org/doiRA/10.1000/xyz": (200, [{"RA": "Crossref"}]),
        "api.crossref.org/works/10.1000/xyz": _works({
            "updated-by": [
                {"type": "retraction", "updated": {"date-parts": [[2020, 1, 1]]}},
                {"type": "reinstatement", "updated": {"date-parts": [[2021, 1, 1]]}},
            ]}),
    })
    o = checks.check_update_notice(net_vault, {"id": "x", "DOI": "10.1000/xyz"},
                                   "2026-08-16")
    assert o.result is Result.MATCHED


def test_notice_datacite_via_openalex(net_vault, monkeypatch):
    _fake_get(monkeypatch, {
        "doi.org/doiRA/10.5281/z.1": (200, [{"RA": "DataCite"}]),
        "api.openalex.org/works/https://doi.org/10.5281/z.1":
            (200, {"is_retracted": True}),
    })
    o = checks.check_update_notice(net_vault, {"id": "d", "DOI": "10.5281/z.1"},
                                   "2026-08-16")
    assert o.result is Result.UNMATCHED and o.extra["notice_date"] is None


def test_rw_csv_batch(tmp_path):
    csv_file = tmp_path / "rw.csv"
    csv_file.write_text(
        "Record ID,OriginalPaperDOI,OriginalPaperPubMedID,RetractionDate,RetractionNature\n"
        '1,10.1000/xyz,11111,2010-02-02,Retraction\n'
        '2,10.1000/eoc,22222,2023-01-01,Expression of concern\n')
    rw = checks.load_rw_csv(csv_file)
    hit = checks.check_rw_batch({"id": "x", "DOI": "10.1000/xyz"}, rw, "2026-08-16")
    assert hit.result is Result.UNMATCHED and hit.extra["notice_date"] == "2010-02-02"
    by_pmid = checks.check_rw_batch({"id": "y", "PMID": "22222"}, rw, "2026-08-16")
    assert by_pmid.result is Result.MATCHED and by_pmid.extra["warn_notices"]
    assert checks.check_rw_batch({"id": "z", "DOI": "10.9/clean"}, rw,
                                 "2026-08-16") is None
```

- [ ] **Step 2: Run to verify the new tests fail**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_checks.py -v`
Expected: new tests FAIL

- [ ] **Step 3: Implement (append to checks.py)**

```python
# append to core/harness_core/checks.py
import csv
from pathlib import Path as _Path

BLOCKING_TYPES = {"retraction", "partial_retraction", "removal", "withdrawal"}
WARN_TYPES = {"expression_of_concern", "correction", "corrigendum", "erratum"}


def _norm_type(t: str) -> str:
    return (t or "").strip().lower().replace(" ", "_")


def _date_parts(update: dict):
    parts = ((update.get("updated") or {}).get("date-parts") or [[None]])[0]
    if not parts or parts[0] is None:
        return None
    y, m, d = (list(parts) + [1, 1])[:3]
    return f"{y:04d}-{m:02d}-{d:02d}"


def check_update_notice(vault_root, entry: dict, detection_date: str) -> Outcome:
    doi = entry.get("DOI") or entry.get("doi")
    pmid = entry.get("PMID") or entry.get("pmid")
    if not doi and not pmid:
        return Outcome("update-notice", entry.get("id", "?"), Result.SKIPPED,
                       "no-identifier — no DOI or PMID")
    if not doi:  # PMID-only: live Crossref leg cannot run; RW batch is the check.
        # SKIPPED, not MATCHED — no event may be minted for an unchecked item (§5).
        return Outcome("update-notice", entry["id"], Result.SKIPPED,
                       "no-identifier — live leg needs a DOI; RW batch covers PMID")
    agency = registry_agency(vault_root, doi)
    try:
        if agency == "Crossref":
            status, data = webapi.get_json(
                f"https://api.crossref.org/works/{doi}", vault_root)
            if status == 404 or data is None:
                return Outcome("update-notice", entry["id"], Result.UNREACHABLE,
                               "outage — registry record unavailable")
            updates = (data.get("message") or {}).get("updated-by") or []
            blocking, warns, cleared_at = None, [], None
            for u in updates:
                t = _norm_type(u.get("type"))
                nd = _date_parts(u)
                if t in BLOCKING_TYPES:
                    blocking = {"type": t, "notice_date": nd}
                elif t == "reinstatement":
                    cleared_at = nd
                elif t in WARN_TYPES:
                    warns.append({"type": t, "notice_date": nd})
            cleared = (cleared_at and blocking and blocking["notice_date"]
                       and blocking["notice_date"] <= cleared_at)
            # unknown blocking date NEVER auto-clears — human adjudication via inbox
            if blocking and not cleared:
                return Outcome("update-notice", entry["id"], Result.UNMATCHED,
                               f"retracted — {blocking['type']}",
                               extra={**blocking, "detection_date": detection_date,
                                      "class": "blocking"})
            return Outcome("update-notice", entry["id"], Result.MATCHED, "matched",
                           extra={"warn_notices": warns} if warns else {})
        # non-Crossref: OpenAlex second opinion
        status, data = webapi.get_json(
            f"https://api.openalex.org/works/https://doi.org/{doi}", vault_root,
            params={"select": "is_retracted"})
        if status == 404 or data is None:
            return Outcome("update-notice", entry["id"], Result.UNREACHABLE,
                           "outage — OpenAlex record unavailable")
        if data.get("is_retracted"):
            return Outcome("update-notice", entry["id"], Result.UNMATCHED,
                           "retracted — per OpenAlex/Retraction Watch",
                           extra={"type": "retraction", "notice_date": None,
                                  "detection_date": detection_date,
                                  "class": "blocking"})
        return Outcome("update-notice", entry["id"], Result.MATCHED, "matched")
    except webapi.ApiError as e:
        return Outcome("update-notice", entry["id"], Result.UNREACHABLE,
                       f"outage — {e}")


def load_rw_csv(path) -> dict:
    by_doi, by_pmid = {}, {}
    with _Path(path).open(newline="", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            rec = {"nature": row.get("RetractionNature", ""),
                   "notice_date": row.get("RetractionDate", "")}
            doi = (row.get("OriginalPaperDOI") or "").strip().lower()
            pmid = (row.get("OriginalPaperPubMedID") or "").strip()
            if doi:
                by_doi[doi] = rec
            if pmid and pmid != "0":
                by_pmid[pmid] = rec
    return {"doi": by_doi, "pmid": by_pmid}


def check_rw_batch(entry: dict, rw: dict, detection_date: str):
    doi = (entry.get("DOI") or entry.get("doi") or "").lower()
    pmid = str(entry.get("PMID") or entry.get("pmid") or "")
    rec = rw["doi"].get(doi) or rw["pmid"].get(pmid)
    if rec is None:
        return None
    nature = _norm_type(rec["nature"])
    extra = {"type": nature, "notice_date": rec["notice_date"] or None,
             "detection_date": detection_date}
    if nature in BLOCKING_TYPES:
        return Outcome("update-notice", entry.get("id", doi or pmid),
                       Result.UNMATCHED, f"retracted — {nature}",
                       extra={**extra, "class": "blocking"})
    return Outcome("update-notice", entry.get("id", doi or pmid), Result.MATCHED,
                   "matched", extra={"warn_notices": [extra]})
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_checks.py -v`
Expected: all PASS

- [ ] **Step 5: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add core && git commit -m "feat: update-notice check — full taxonomy, bi-temporal, RW CSV batch, registry routing"
```

---

### Task 9: Identifier discovery

**Files:**
- Create: `core/harness_core/identify.py`
- Test: `core/tests/test_identify.py`

**Interfaces:**
- Consumes: `webapi`, `checks.normalize_text`.
- Produces: `discover(vault_root, entry: dict) -> dict` — for an item lacking a DOI: Crossref bibliographic query (`api.crossref.org/works`, `query.bibliographic=<title> <first-author-family> <year>`, `rows=2`); accept the top hit only when its normalized title equals ours (§6: discovery before SKIPPED sticks, no fuzzy adoption); then PubMed `esearch` (`eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi`, `db=pubmed&term=<title>[Title]&retmode=json`) accepting a single-hit id. Returns any of `{"DOI": …, "PMID": …}` found; `{}` when nothing conclusive; raises nothing (ApiError ⇒ `{}` — discovery is best-effort, the SKIPPED record notes it).

- [ ] **Step 1: Write the failing test**

```python
# core/tests/test_identify.py
from harness_core import identify, webapi


def _fake_get(monkeypatch, table):
    def fake(url, vault_root, params=None, headers=None, timeout=10.0):
        for frag, resp in table.items():
            if frag in url:
                if isinstance(resp, Exception):
                    raise resp
                return resp
        raise AssertionError(f"unexpected url {url}")
    monkeypatch.setattr(webapi, "get_json", fake)


def test_discover_doi_exact_title(net_vault, monkeypatch):
    _fake_get(monkeypatch, {
        "api.crossref.org/works": (200, {"message": {"items": [
            {"DOI": "10.1000/found", "title": ["Mortality decline"]},
            {"DOI": "10.1000/other", "title": ["Something else"]}]}}),
        "esearch.fcgi": (200, {"esearchresult": {"idlist": ["11111"]}}),
    })
    ids = identify.discover(net_vault, {"id": "x", "title": "Mortality  Decline",
                                        "author": [{"family": "Smith"}],
                                        "issued": {"date-parts": [[2020]]}})
    assert ids == {"DOI": "10.1000/found", "PMID": "11111"}


def test_discover_rejects_title_mismatch(net_vault, monkeypatch):
    _fake_get(monkeypatch, {
        "api.crossref.org/works": (200, {"message": {"items": [
            {"DOI": "10.1000/wrong", "title": ["A different study"]}]}}),
        "esearch.fcgi": (200, {"esearchresult": {"idlist": []}}),
    })
    assert identify.discover(net_vault, {"id": "x", "title": "Mortality decline"}) == {}


def test_discover_outage_is_empty(net_vault, monkeypatch):
    _fake_get(monkeypatch, {"api.crossref.org/works": webapi.ApiError("down"),
                            "esearch.fcgi": webapi.ApiError("down")})
    assert identify.discover(net_vault, {"id": "x", "title": "T"}) == {}
```

(The `net_vault` fixture moves to `conftest.py` in this task — cut it from `test_checks.py` and paste there so both files share it.)

- [ ] **Step 2: Run to verify failure**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_identify.py -v`
Expected: FAIL — `No module named 'harness_core.identify'`

- [ ] **Step 3: Implement**

```python
# core/harness_core/identify.py
"""Identifier discovery before SKIPPED sticks (spec §6, Citation-bot pattern)."""
from . import webapi
from .checks import normalize_text


def _crossref_doi(vault_root, entry):
    title = str(entry.get("title", ""))
    if not title:
        return None
    fam = ((entry.get("author") or [{}])[0]).get("family", "")
    year = ((entry.get("issued") or {}).get("date-parts") or [[""]])[0][0]
    q = " ".join(str(x) for x in (title, fam, year) if x)
    try:
        status, data = webapi.get_json("https://api.crossref.org/works", vault_root,
                                       params={"query.bibliographic": q, "rows": 2})
    except webapi.ApiError:
        return None
    items = ((data or {}).get("message") or {}).get("items") or []
    if items:
        top = items[0]
        remote_title = (top.get("title") or [""])[0]
        if normalize_text(remote_title) == normalize_text(title):
            return top.get("DOI")
    return None


def _pubmed_pmid(vault_root, entry):
    title = str(entry.get("title", ""))
    if not title:
        return None
    try:
        status, data = webapi.get_json(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            vault_root, params={"db": "pubmed", "term": f"{title}[Title]",
                                "retmode": "json"})
    except webapi.ApiError:
        return None
    ids = ((data or {}).get("esearchresult") or {}).get("idlist") or []
    return ids[0] if len(ids) == 1 else None


def discover(vault_root, entry: dict) -> dict:
    out = {}
    doi = _crossref_doi(vault_root, entry)
    if doi:
        out["DOI"] = doi
    pmid = _pubmed_pmid(vault_root, entry)
    if pmid:
        out["PMID"] = pmid
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_identify.py tests/test_checks.py -v`
Expected: all PASS (including the relocated `net_vault` fixture)

- [ ] **Step 5: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add core && git commit -m "feat: identifier discovery (Crossref bibliographic + PubMed) before SKIPPED"
```

---

### Task 10: Quote verification

**Files:**
- Create: `core/harness_core/quotes.py`
- Test: `core/tests/test_quotes.py`

**Interfaces:**
- Consumes: `checks.normalize_text` (the one pipeline), `claims.parse_claims`, `notes.note_path`, `checks.Outcome`.
- Produces:
  - `levenshtein_ratio(a: str, b: str) -> float` — `1 - distance/max(len)`; classic DP, stdlib only.
  - `check_quote(vault_root, claim: Claim, source_citekey: str) -> Outcome` — comparison target: the cited literature note's **managed-region quote with the same claim address**, else *any* managed-region quote in that note. Normalized-exact ⇒ MATCHED, `extra = {"target": "managed-region"}`. Best fuzzy ≥ 0.90 ⇒ UNMATCHED with reason `"fuzzy-quote — best ratio <r>"` (inbox, never a silent pass). Below ⇒ UNMATCHED, `"mismatch — quote absent from source note"`. No managed-region quotes at all ⇒ UNREACHABLE (`"outage — no extractable comparison text"` — §6's Marshall-sparsity path; human attestation goes through the inbox ack).
  - `check_all_quotes(vault_root, note_path: Path) -> list[Outcome]` — every quote claim in the note that cites a citekey.

- [ ] **Step 1: Write the failing test**

```python
# core/tests/test_quotes.py
from harness_core import Result, quotes


def test_levenshtein_ratio_bounds():
    assert quotes.levenshtein_ratio("abc", "abc") == 1.0
    assert quotes.levenshtein_ratio("abc", "abd") > 0.6
    assert quotes.levenshtein_ratio("abc", "xyz") < 0.4


def test_exact_after_normalization(fixture_vault):
    outs = quotes.check_all_quotes(
        fixture_vault, fixture_vault / "efforts" / "brief" / "draft.md")
    assert len(outs) == 1
    assert outs[0].result is Result.MATCHED
    assert outs[0].extra["target"] == "managed-region"


def test_fuzzy_goes_to_inbox_tier(fixture_vault):
    draft = fixture_vault / "efforts" / "brief" / "draft.md"
    draft.write_text(draft.read_text().replace(
        "Mortality fell 12% across all strata.",
        "Mortality fell 12% across all stratum."))  # ratio ~0.95: inside [0.90, 1)
    outs = quotes.check_all_quotes(fixture_vault, draft)
    assert outs[0].result is Result.UNMATCHED
    assert outs[0].reason.startswith("fuzzy-quote")


def test_absent_quote_is_mismatch(fixture_vault):
    draft = fixture_vault / "efforts" / "brief" / "draft.md"
    draft.write_text(draft.read_text().replace(
        "Mortality fell 12% across all strata.",
        "Entirely fabricated sentence with nothing in common whatsoever here."))
    outs = quotes.check_all_quotes(fixture_vault, draft)
    assert outs[0].result is Result.UNMATCHED
    assert outs[0].reason.startswith("mismatch")


def test_no_comparison_text_is_unreachable(fixture_vault):
    draft = fixture_vault / "efforts" / "brief" / "draft.md"
    draft.write_text(draft.read_text().replace("smith2020, p. 12", "gone2019, p. 1"))
    outs = quotes.check_all_quotes(fixture_vault, draft)
    assert outs[0].result is Result.UNREACHABLE
```

- [ ] **Step 2: Run to verify failure**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_quotes.py -v`
Expected: FAIL — `No module named 'harness_core.quotes'`

- [ ] **Step 3: Implement**

```python
# core/harness_core/quotes.py
"""Quote verification against the managed-region target (spec §6)."""
from pathlib import Path

from . import Result
from . import claims as claims_mod
from .checks import Outcome, normalize_text
from .notes import note_path

FUZZY_THRESHOLD = 0.90


def levenshtein_ratio(a: str, b: str) -> float:
    if not a and not b:
        return 1.0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1,
                           prev[j - 1] + (ca != cb)))
        prev = cur
    return 1.0 - prev[-1] / max(len(a), len(b))


def _source_quotes(vault_root, citekey):
    p = note_path(vault_root, citekey)
    if not p.is_file():
        return {}
    return {c.claim_id: c.quote_text
            for c in claims_mod.parse_claims(p.read_text())
            if c.tag == "quote" and c.in_managed and c.quote_text}


def check_quote(vault_root, claim, source_citekey) -> Outcome:
    addr = claims_mod.claim_address(source_citekey, claim.claim_id or "?")
    targets = _source_quotes(vault_root, source_citekey)
    if not targets:
        return Outcome(f"quote", addr, Result.UNREACHABLE,
                       "outage — no extractable comparison text in source note")
    ours = normalize_text(claim.quote_text or "")
    norm_targets = {cid: normalize_text(q) for cid, q in targets.items()}
    if ours in norm_targets.values():
        return Outcome("quote", addr, Result.MATCHED, "matched",
                       extra={"target": "managed-region"})
    best = max(levenshtein_ratio(ours, t) for t in norm_targets.values())
    if best >= FUZZY_THRESHOLD:
        return Outcome("quote", addr, Result.UNMATCHED,
                       f"fuzzy-quote — best ratio {best:.2f}",
                       extra={"target": "managed-region"})
    return Outcome("quote", addr, Result.UNMATCHED,
                   "mismatch — quote absent from source note",
                   extra={"target": "managed-region"})


def check_all_quotes(vault_root, note_file: Path) -> list[Outcome]:
    out = []
    for c in claims_mod.parse_claims(Path(note_file).read_text()):
        if c.tag == "quote" and c.citekey and c.quote_text:
            out.append(check_quote(vault_root, c, c.citekey))
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_quotes.py -v`
Expected: 5 PASS

- [ ] **Step 5: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add core && git commit -m "feat: quote verification — normalize-then-exact, fuzzy to inbox, sparsity path"
```

---

### Task 11: The six integrity lints

**Files:**
- Create: `core/harness_core/lints.py`
- Test: `core/tests/test_lints.py`

**Interfaces:**
- Consumes: `claims`, `frontmatter`, `inbox.INBOX_PATH`, `checks.Outcome`, `Result`; `git` via subprocess.
- Produces (each returns `list[Outcome]`, all warn-tier — reasons open with their code; empty list = clean):
  - `lint_append_only(vault_root)` — `git diff HEAD --unified=0 -- calendar/ +/review-queue.md`: any deleted (`-`) content line ⇒ Outcome per file (`"drift — append-only file rewrote history"`).
  - `lint_claim_immutability(vault_root)` — for `literatures/ atlas/ efforts/`: every `^c-…` anchor present in `git show HEAD:<file>` must still exist in the worktree file with an identical claim line, unless the worktree line carries `[status:: deprecated]` (§5 transition record) — else `"drift — claim <address> mutated or vanished without deprecation"`.
  - `lint_published_drift(vault_root)` — for each git tag `published/*`: `git diff <tag> HEAD -- <effort dir>` non-empty while the effort's `status` is still `"published"` ⇒ `"drift — published effort diverged from its tag"`.
  - `lint_source_status(vault_root, note_file)` — claims citing a citekey whose literature note `status` ∈ {`rejected`, `superseded`} ⇒ `"superseded-source — cites <citekey> (…superseded-by <x>)"`.
  - `lint_contested(vault_root, note_file)` — a claim in `note_file` whose `[supported-by:: …]` list references a claim address that any atlas page marks in a `[contested-by:: …]` field, or that cites an address itself carrying `contested-by` ⇒ `"contested — <address> has standing counter-evidence"`. Deterministic string-level resolution only.
  - `lint_web_archive(vault_root)` — literature notes with `url` and no `doi` must carry `archive-url` ⇒ `"missing-archive — web source has no archive-url"`. (Resolution check is live-only; presence is the offline lint.)

- [ ] **Step 1: Write the failing test**

```python
# core/tests/test_lints.py
import subprocess

from harness_core import Result, lints


def test_all_clean_on_fixture(fixture_vault):
    assert lints.lint_append_only(fixture_vault) == []
    assert lints.lint_claim_immutability(fixture_vault) == []
    assert lints.lint_published_drift(fixture_vault) == []


def test_append_only_catches_deletion(fixture_vault):
    f = fixture_vault / "calendar" / "2026-08-16.md"
    f.write_text("")          # rewrote history
    outs = lints.lint_append_only(fixture_vault)
    assert outs and outs[0].reason.startswith("drift")


def test_claim_immutability_catches_silent_edit(fixture_vault):
    f = fixture_vault / "literatures" / "smith2020.md"
    f.write_text(f.read_text().replace("Mortality fell 12%", "Mortality fell 21%"))
    outs = lints.lint_claim_immutability(fixture_vault)
    assert any("c-11111111" in o.target for o in outs)


def test_claim_immutability_allows_deprecation(fixture_vault):
    f = fixture_vault / "literatures" / "smith2020.md"
    f.write_text(f.read_text().replace(
        "- (paraphrase) Retrospective design [@smith2020, p. 3] ^c-22222222",
        "- (paraphrase) Retrospective design [@smith2020, p. 3] "
        "[status:: deprecated] [deprecated-at:: 2026-08-16] "
        "[deprecated-by:: human:eran] [reason:: superseded] ^c-22222222"))
    assert lints.lint_claim_immutability(fixture_vault) == []


def test_published_drift(fixture_vault):
    subprocess.run(["git", "tag", "published/brief-2026-08-16"], cwd=fixture_vault,
                   check=True)
    draft = fixture_vault / "efforts" / "brief" / "draft.md"
    draft.write_text(draft.read_text().replace('status: "drafting"',
                                               'status: "published"')
                     + "\nnew paragraph after publishing\n")
    outs = lints.lint_published_drift(fixture_vault)
    assert outs and outs[0].reason.startswith("drift")


def test_source_status_lint(fixture_vault):
    draft = fixture_vault / "efforts" / "brief" / "draft.md"
    draft.write_text(draft.read_text() +
                     "- (paraphrase) Old claim [@gone2019, p. 1] ^c-88888888\n")
    outs = lints.lint_source_status(fixture_vault, draft)
    assert outs and outs[0].reason.startswith("superseded-source")


def test_contested_lint(fixture_vault):
    # the atlas claim ^c-55555555 CARRIES contested-by and supports
    # smith2020#^c-11111111 — so THAT address has standing counter-evidence
    draft = fixture_vault / "efforts" / "brief" / "draft.md"
    draft.write_text(draft.read_text() +
                     "- (inference) Relies on it [supported-by:: "
                     "[[smith2020#^c-11111111]]] ^c-99999999\n")
    outs = lints.lint_contested(fixture_vault, draft)
    assert outs and outs[0].reason.startswith("contested")


def test_citing_the_contester_is_clean(fixture_vault):
    draft = fixture_vault / "efforts" / "brief" / "draft.md"
    draft.write_text(draft.read_text() +
                     "- (inference) Cites counter-evidence [supported-by:: "
                     "[[gone2019#^c-22222222]]] ^c-99999998\n")
    assert lints.lint_contested(fixture_vault, draft) == []


def test_web_archive_lint(fixture_vault):
    (fixture_vault / "literatures" / "webonly2024.md").write_text("""---
citekey: "webonly2024"
type: "literature"
url: "https://example.org/post"
retrieved: "2026-08-16"
status: "unreviewed"
---
%%hk-managed%%
# Web post
%%/hk-managed%%
""")
    outs = lints.lint_web_archive(fixture_vault)
    assert outs and outs[0].reason.startswith("missing-archive")
```

- [ ] **Step 2: Run to verify failure**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_lints.py -v`
Expected: FAIL — `No module named 'harness_core.lints'`

- [ ] **Step 3: Implement**

```python
# core/harness_core/lints.py
"""The six §6 integrity lints — git-mechanical, warn-tier, never closing alone."""
import re
import subprocess
from pathlib import Path

from . import Result
from . import claims as claims_mod
from . import frontmatter
from .checks import Outcome

ANCHOR = re.compile(r"\^(c-[A-Za-z0-9]+)\s*$", re.M)


def _git(vault_root, *args):
    return subprocess.run(["git", *args], cwd=vault_root, capture_output=True,
                          text=True)


def lint_append_only(vault_root) -> list[Outcome]:
    out = []
    for target in ("calendar", "+/review-queue.md"):
        diff = _git(vault_root, "diff", "HEAD", "--unified=0", "--", target).stdout
        deleted = [l for l in diff.splitlines()
                   if l.startswith("-") and not l.startswith("---")]
        if deleted:
            out.append(Outcome("append-only", target, Result.UNMATCHED,
                               "drift — append-only file rewrote history"))
    return out


def _head_text(vault_root, rel):
    r = _git(vault_root, "show", f"HEAD:{rel}")
    return r.stdout if r.returncode == 0 else None


def _claim_blocks(text: str) -> dict:
    """anchor id -> the claim BLOCK: anchor line + its continuation lines
    ('  > ' blockquotes and '  <!-- hk-sel' selector comments)."""
    blocks, lines = {}, text.splitlines()
    for i, line in enumerate(lines):
        m = ANCHOR.search(line)
        if not m:
            continue
        block = [line]
        for cont in lines[i + 1:]:
            if cont.startswith("  > ") or cont.startswith("  <!-- hk-sel"):
                block.append(cont)
            else:
                break
        blocks[m.group(1)] = "\n".join(block)
    return blocks


def _is_full_deprecation(line: str) -> bool:
    # §5 transition record: status + deprecated-at + deprecated-by + reason
    return all(f"[{k}:: " in line for k in
               ("status", "deprecated-at", "deprecated-by", "reason")) \
        and "[status:: deprecated]" in line


def lint_claim_immutability(vault_root) -> list[Outcome]:
    out = []
    for folder in ("literatures", "atlas", "efforts"):
        for p in sorted(Path(vault_root).glob(f"{folder}/**/*.md")):
            rel = p.relative_to(vault_root).as_posix()
            head = _head_text(vault_root, rel)
            if head is None:
                continue
            head_blocks = _claim_blocks(head)
            now_blocks = _claim_blocks(p.read_text())
            for cid, old_block in head_blocks.items():
                new_block = now_blocks.get(cid)
                if new_block == old_block:
                    continue
                if new_block and _is_full_deprecation(new_block.splitlines()[0]):
                    continue
                out.append(Outcome(
                    "claim-immutability", f"{rel}#^{cid}", Result.UNMATCHED,
                    f"drift — claim ^{cid} mutated or vanished without deprecation"))
    return out


def lint_published_drift(vault_root) -> list[Outcome]:
    out = []
    tags = _git(vault_root, "tag", "--list", "published/*").stdout.split()
    for tag in tags:
        effort = tag.split("/", 1)[1].rsplit("-", 3)[0]
        effort_dir = f"efforts/{effort}"
        diff = _git(vault_root, "diff", tag, "HEAD", "--", effort_dir).stdout
        dirty = _git(vault_root, "diff", "HEAD", "--", effort_dir).stdout
        if not (diff or dirty):
            continue
        status = None
        for p in Path(vault_root, effort_dir).glob("*.md"):
            data, _ = frontmatter.parse(p.read_text())
            status = data.get("status", status)
        if status == "published":
            out.append(Outcome("published-drift", effort_dir, Result.UNMATCHED,
                               "drift — published effort diverged from its tag"))
    return out


def _note_status(vault_root, citekey):
    p = Path(vault_root) / "literatures" / f"{citekey}.md"
    if not p.is_file():
        return None, None
    data, _ = frontmatter.parse(p.read_text())
    return data.get("status"), data.get("superseded-by")


def lint_source_status(vault_root, note_file) -> list[Outcome]:
    out = []
    for c in claims_mod.parse_claims(Path(note_file).read_text()):
        if not c.citekey:
            continue
        status, succ = _note_status(vault_root, c.citekey)
        if status in ("rejected", "superseded"):
            suffix = f" (superseded-by {succ})" if succ else ""
            out.append(Outcome("source-status", c.citekey, Result.UNMATCHED,
                               f"superseded-source — cites {c.citekey} "
                               f"with status {status}{suffix}"))
    return out


ADDR_RE = re.compile(r"\[\[([A-Za-z0-9_.:-]+#\^c-[A-Za-z0-9]+)\]\]")


def _contested_addresses(vault_root, atlas_frontmatters) -> set[str]:
    """Addresses with standing counter-evidence: the addresses a claim CARRYING
    a contested-by field itself supports (its supported-by targets), plus that
    claim's own address. The addresses INSIDE contested-by are the contesters —
    citing them is fine."""
    contested = set()
    for p in Path(vault_root).glob("atlas/**/*.md"):
        text = p.read_text()
        data, _ = frontmatter.parse(text)
        for c in claims_mod.parse_claims(text):
            if "contested-by" not in c.fields:
                continue
            contested.update(ADDR_RE.findall(c.fields.get("supported-by", "")))
            if c.claim_id:
                page_key = data.get("citekey") or p.stem
                contested.add(f"{page_key}#^{c.claim_id}")
    return contested


def lint_contested(vault_root, note_file) -> list[Outcome]:
    contested = _contested_addresses(vault_root, None)
    out = []
    for c in claims_mod.parse_claims(Path(note_file).read_text()):
        for addr in ADDR_RE.findall(c.fields.get("supported-by", "")):
            if addr in contested:
                out.append(Outcome("contested", addr, Result.UNMATCHED,
                                   f"contested — {addr} has standing "
                                   f"counter-evidence"))
    return out


def lint_web_archive(vault_root) -> list[Outcome]:
    out = []
    for p in sorted(Path(vault_root).glob("literatures/*.md")):
        data, _ = frontmatter.parse(p.read_text())
        if data.get("url") and not data.get("doi") and not data.get("archive-url"):
            out.append(Outcome("web-archive", data.get("citekey", p.stem),
                               Result.UNMATCHED,
                               "missing-archive — web source has no archive-url"))
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_lints.py -v`
Expected: 9 PASS

- [ ] **Step 5: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add core && git commit -m "feat: six integrity lints — append-only, claim-immutability, published-drift, source-status, contested, web-archive"
```

---

### Task 12: Selector production + backfill (Plan A obligation)

**Files:**
- Create: `core/harness_core/selectors.py`
- Modify: `core/pyproject.toml` (add `[project.optional-dependencies] pdf = ["pypdf>=4"]`)
- Modify: `core/harness_core/__main__.py` (attach contexts during `import-note` when the extra is present)
- Test: `core/tests/test_selectors.py`

**Interfaces:**
- Consumes: `checks.normalize_text`; Plan A's selector **escaping** in `notes.py` — locate it first (`grep -n "hk-sel" core/harness_core/notes.py` and read the helper it calls); this task's `unescape_selector` must invert it exactly (Task 6/7 ruling: symmetric).
- Produces:
  - `pdf_text(path) -> str | None` — pypdf extraction, `None` when pypdf missing or extraction fails (never raises; the caller records the degradation).
  - `find_context(text: str, quote: str) -> tuple[str, str] | None` — locate the normalized quote inside normalized full text (build a char-map so raw offsets survive normalization), return raw `(prefix[-32:], suffix[:32])`; `None` when the quote isn't present verbatim-after-normalization.
  - `attach_contexts(annotations: list[dict], text: str) -> int` — sets `context_prefix`/`context_suffix` on each normalized annotation whose `annotationText` locates; returns count.
  - `unescape_selector(value: str) -> str` — exact inverse of `notes.py`'s selector escaping.
  - `__main__.cmd_import_note` change: after building `annotations`, when `pdf_text` is importable and an attachment path resolved, call `attach_contexts` before rendering — selectors now have their §5 producer; when unavailable, print `warning: selectors skipped (pdf extra not installed)` to stderr.
  - `backfill-selectors --vault <path>` CLI verb: for every literature note, re-run the import pipeline (render-first comparison makes it a NOOP unless contexts add anything).

- [ ] **Step 1: Write the failing test**

```python
# core/tests/test_selectors.py
import pytest

from harness_core import selectors


TEXT = ("Background prose before the finding. The cohort showed that "
        "Mortality fell 12% across all strata. Further discussion follows here.")


def test_find_context_slices_32():
    ctx = selectors.find_context(TEXT, "Mortality fell 12% across all strata.")
    assert ctx is not None
    prefix, suffix = ctx
    assert prefix.endswith("showed that ") and len(prefix) <= 32
    assert suffix.startswith(" Further") and len(suffix) <= 32


def test_find_context_normalized_match():
    assert selectors.find_context(TEXT, "Mortality  fell 12% across all strata.")


def test_find_context_absent_returns_none():
    assert selectors.find_context(TEXT, "Sentence that is not there.") is None


def test_attach_contexts_counts():
    anns = [{"annotationText": "Mortality fell 12% across all strata.",
             "type": "highlight"},
            {"annotationText": "not present", "type": "highlight"}]
    n = selectors.attach_contexts(anns, TEXT)
    assert n == 1
    assert anns[0]["context_prefix"].endswith("showed that ")
    assert "context_prefix" not in anns[1]


def test_unescape_inverts_notes_escaping():
    from harness_core import notes
    ann = {"key": "K1", "type": "highlight", "citekey": "x2020",
           "annotationText": 'He said "stop" & wrote -->',
           "comment": "", "pageLabel": "1",
           "context_prefix": 'the study\'s "A" & B -->', "context_suffix": "tail"}
    rendered = notes.render_claim(ann)
    sel_line = [l for l in rendered.split("\n") if "hk-sel" in l][0]
    import re
    prefix_escaped = re.search(r'prefix="([^"]*)"', sel_line).group(1)
    assert selectors.unescape_selector(prefix_escaped) == 'the study\'s "A" & B -->'


def test_pdf_text_degrades_without_pypdf(monkeypatch, tmp_path):
    import builtins
    real_import = builtins.__import__
    def no_pypdf(name, *a, **k):
        if name == "pypdf":
            raise ImportError("absent")
        return real_import(name, *a, **k)
    monkeypatch.setattr(builtins, "__import__", no_pypdf)
    f = tmp_path / "x.pdf"
    f.write_bytes(b"%PDF-1.4 minimal")
    assert selectors.pdf_text(f) is None
```

- [ ] **Step 2: Run to verify failure**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_selectors.py -v`
Expected: FAIL — `No module named 'harness_core.selectors'`

- [ ] **Step 3: Implement**

```python
# core/harness_core/selectors.py
"""Selector production: prefix/suffix context capture (§5; Plan A deviation closed)."""
from .checks import normalize_text

CONTEXT_CHARS = 32


def pdf_text(path):
    try:
        import pypdf
    except ImportError:
        return None
    try:
        reader = pypdf.PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception:
        return None


def _norm_with_map(s: str):
    """Normalized string + map from each NORMALIZED index -> raw index.
    NFKC may expand one raw char to several normalized chars (ﬁ -> fi):
    emit one map entry per EMITTED char, all pointing at the raw origin.
    Handles the '-\n' dehyphenation pair and whitespace-run collapse."""
    import unicodedata
    out, idx_map = [], []
    prev_space = True          # leading whitespace collapses to nothing
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "-" and i + 1 < len(s) and s[i + 1] == "\n":
            i += 2             # dehyphenation: drop the pair
            continue
        if ch == "­":          # soft hyphen
            i += 1
            continue
        expanded = unicodedata.normalize("NFKC", ch)
        if expanded.isspace() or ch.isspace():
            if not prev_space:
                out.append(" ")
                idx_map.append(i)
                prev_space = True
            i += 1
            continue
        prev_space = False
        for c in expanded:
            out.append(c)
            idx_map.append(i)
        i += 1
    while out and out[-1] == " ":
        out.pop(); idx_map.pop()
    return "".join(out), idx_map


def find_context(text: str, quote: str):
    norm_text, idx_map = _norm_with_map(text)
    norm_quote, _ = _norm_with_map(quote)
    pos = norm_text.find(norm_quote)
    if pos == -1 or not norm_quote:
        return None
    start_raw = idx_map[pos]
    end_norm = pos + len(norm_quote) - 1
    end_raw = idx_map[end_norm] + 1
    return text[max(0, start_raw - CONTEXT_CHARS):start_raw], \
        text[end_raw:end_raw + CONTEXT_CHARS]


def attach_contexts(annotations, text) -> int:
    n = 0
    for ann in annotations:
        quote = ann.get("annotationText") or ""
        if not quote:
            continue
        ctx = find_context(text, quote)
        if ctx:
            ann["context_prefix"], ann["context_suffix"] = ctx
            n += 1
    return n


def unescape_selector(value: str) -> str:
    # Exact inverse of notes.py's selector escaping (symmetry ruling).
    # As-built escaper is html.escape(quote=True), which also escapes
    # apostrophes to &#x27; — VERIFY against notes.py at HEAD; the escaper
    # is the authority. Inversion in reverse replacement order:
    return (value.replace("--&gt;", "-->").replace("&quot;", '"')
            .replace("&#x27;", "'")
            .replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&"))
```

`__main__.cmd_import_note` integration — the as-built loop is `for attachment in client.attachments(...)` and the resolved local path is currently computed inside `_attachment_hash` and discarded. Concrete change: (1) refactor `_attachment_hash` to return `(hash, local_path | None)`; (2) in the loop, collect `(local_path, annotations-of-this-attachment)` pairs (the as-built `_attachment_annotations(attachment)` gives per-attachment annotations before they are merged); (3) after collection:

```python
    # selector production (§5): attach contexts when the pdf extra is available
    from . import selectors as _selectors
    attached = 0
    for local_path, atts_anns in attachment_pairs:
        text = _selectors.pdf_text(local_path) if local_path else None
        if text:
            attached += _selectors.attach_contexts(atts_anns, text)
    if annotations and not attached:
        print("warning: selectors skipped (pdf extra not installed or "
              "no extractable text)", file=sys.stderr)
```

(the per-attachment annotation dicts are the same objects later merged into `annotations`, so mutation attaches contexts before rendering).

`backfill-selectors` verb: `sub.add_parser("backfill-selectors", parents=[common])` with `--vault`, iterating `literatures/*.md` frontmatter citekeys and calling the import pipeline per citekey (render-first NOOP absorbs unchanged notes).

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_selectors.py -v`
Expected: 6 PASS. If `test_unescape_inverts_notes_escaping` fails, the as-built escaper differs from `html.escape` — read `notes.py`'s helper and mirror-invert it exactly; that test is the symmetry ruling's enforcement.

- [ ] **Step 5: Commit**

```bash
cd "$(git rev-parse --show-toplevel)"
git add core && git commit -m "feat: selector production + backfill — Plan A deviation closed, symmetric unescape"
```

---

### Task 13: `verify` + `inbox` CLI verbs, live drills

**Files:**
- Modify: `core/harness_core/__main__.py`
- Test: `core/tests/test_verify_cli.py`

**Interfaces:**
- Consumes: everything above.
- Produces:
  - `run_verify(vault_root, scope: str = "all", network: bool = True, detection_date: str | None = None, rw_csv: str | None = None) -> dict` — orchestrates: bibliography staleness; per-note citekey/quote checks + source-status/contested lints (offline); per-bibliography-entry DOI, metadata, update-notice checks (network; when `network=False` these record **UNREACHABLE** `"outage — network disabled"` — never SKIPPED, which is automatic-only per §6); identifier discovery for DOI-less entries — after discovery, **re-derive** `doi = entry.get("DOI")`: still absent ⇒ SKIPPED doi/metadata outcomes, but `check_update_notice` STILL runs (PMID-bearing entries are never structurally exempt, §6); `rw_csv` given ⇒ `check_rw_batch` runs across the bibliography (Plan C's cron surface); vault-wide integrity lints incl. a network-mode `archive-url` resolution leg (HEAD via webapi: hard 404 ⇒ warn UNMATCHED, outage ⇒ UNREACHABLE). Effects per §5/§6: MATCHED note-level outcomes mint events (**including MATCHED-with-warns** — the inbox entry is the warn signal, the event is not withheld); **MATCHED quote outcomes mint `quote:<claim_address>:<target>` events on the cited literature note** — machine-confirmed must be reachable through this verb; UNMATCHED claim-level outcomes **stamp `[verify-failed:: <check>/<date>]` on the failing claim line** in the checked note (cleared on a later MATCHED or matching human ack — §5 relay principle for failures); every non-MATCHED outcome and every warn notice files one inbox entry with `target_hash` (the cited note's first attachment hash, else the file's sha256) and, for update-notice entries, `notice_date` + `detection_date` (bi-temporal, §6) — **deduplicated** on `(check, target, result-or-warn-type, target_hash)` against open entries, so re-runs don't flood but a post-ack recurrence with changed content re-enters. Returns `{"outcomes": [...], "counts": {...}}`.
  - CLI `verify --vault <path> [--offline] [--rw-csv <path>]` — prints one line per non-MATCHED outcome + JSON per-check counts. Exit contract (Global Constraints): 1 only when a **closing-class** check (`CLOSING_CHECKS`) is UNMATCHED; 3 when UNREACHABLE anywhere and no closing UNMATCHED; else 0 (warn-tier findings print and file but do not change the exit). `inbox --vault <path>` — `summary()` + unacknowledged entries oldest-first.

- [ ] **Step 1: Write the failing test**

```python
# core/tests/test_verify_cli.py
import json
import subprocess
import sys

import pytest

from harness_core import Result, inbox
from harness_core.__main__ import run_verify


def test_run_verify_offline_effects(net_vault):
    report = run_verify(net_vault, network=False, detection_date="2026-08-16")
    # fabricated2020 is cited in the draft but not in the bibliography
    assert any(o.check == "citekey" and o.target == "fabricated2020"
               and o.result is Result.UNMATCHED for o in report["outcomes"])
    # the failure landed in the inbox exactly once
    entries = [e for e in inbox.load(net_vault)
               if e.check == "citekey" and e.target == "fabricated2020"]
    assert len(entries) == 1
    # re-run does not duplicate
    run_verify(net_vault, network=False, detection_date="2026-08-16")
    entries = [e for e in inbox.load(net_vault)
               if e.check == "citekey" and e.target == "fabricated2020"]
    assert len(entries) == 1


def test_run_verify_quote_matched_no_inbox_entry(net_vault):
    report = run_verify(net_vault, network=False, detection_date="2026-08-16")
    quote_outs = [o for o in report["outcomes"] if o.check == "quote"]
    assert quote_outs and all(o.result is Result.MATCHED for o in quote_outs)


def test_matched_quotes_mint_events_on_source_note(net_vault):
    from harness_core import events
    run_verify(net_vault, network=False, detection_date="2026-08-16")
    note = (net_vault / "literatures" / "smith2020.md").read_text()
    checks_recorded = {e["check"] for e in events.verified_checks(note)}
    assert any(c.startswith("quote:smith2020#^c-") for c in checks_recorded)


def test_offline_network_checks_are_unreachable_not_skipped(net_vault):
    report = run_verify(net_vault, network=False, detection_date="2026-08-16")
    doi_outs = [o for o in report["outcomes"] if o.check == "doi"]
    assert doi_outs and all(o.result is Result.UNREACHABLE for o in doi_outs)


def test_verify_failed_stamped_on_failing_claim(net_vault):
    draft = net_vault / "efforts" / "brief" / "draft.md"
    draft.write_text(draft.read_text().replace(
        "Mortality fell 12% across all strata.",
        "Entirely fabricated sentence with nothing in common whatsoever here."))
    run_verify(net_vault, network=False, detection_date="2026-08-16")
    assert "[verify-failed:: quote/2026-08-16]" in draft.read_text()


def test_cli_exit_codes(net_vault):
    proc = subprocess.run(
        [sys.executable, "-m", "harness_core", "verify", "--vault", str(net_vault),
         "--offline"],
        capture_output=True, text=True)
    assert proc.returncode == 1          # fabricated2020 is UNMATCHED
    assert "fabricated2020" in proc.stdout


def test_cli_inbox_lists_open_entries(net_vault):
    subprocess.run([sys.executable, "-m", "harness_core", "verify", "--vault",
                    str(net_vault), "--offline"], capture_output=True)
    proc = subprocess.run(
        [sys.executable, "-m", "harness_core", "inbox", "--vault", str(net_vault)],
        capture_output=True, text=True)
    assert proc.returncode == 0
    assert "unacknowledged" in proc.stdout and "fabricated2020" in proc.stdout


@pytest.mark.live_net
def test_live_drill_wakefield_and_fabricated(net_vault_real_mailto):
    """The §9 drill legs that only real APIs can prove."""
    from harness_core import checks
    v = net_vault_real_mailto
    o = checks.check_update_notice(
        v, {"id": "wakefield1998", "DOI": "10.1016/S0140-6736(97)11096-0"},
        detection_date="2026-08-16")
    assert o.result is Result.UNMATCHED and o.extra["class"] == "blocking"
    # The registry is the source of record: Crossref's updated-by carries its
    # deposit's notice date (2010-02-06 as of 2026-08-17), not The Lancet's
    # announcement date, and deposits can be re-issued — assert the month,
    # not the day (ruling 13). Offline fixtures keep exact dates.
    assert o.extra["notice_date"].startswith("2010-02")
    o2 = checks.check_doi_exists(v, "10.1000/completely-fabricated-2026")
    assert o2.result is Result.UNMATCHED
    o3 = checks.registry_agency(v, "10.5281/zenodo.3678326")
    assert o3 == "DataCite"
```

Add to `conftest.py`:

```python
@pytest.fixture
def net_vault_real_mailto(fixture_vault):
    import os
    h = fixture_vault / ".harness"
    h.mkdir(exist_ok=True)
    addr = os.environ.get("HARNESS_MAILTO", "")
    h.joinpath("machine.json").write_text(_json.dumps({"mailto": addr}))
    return fixture_vault
```

Register the marker in `pyproject.toml` (`"live_net: hits real external APIs (set HARNESS_LIVE_NET=1 and HARNESS_MAILTO)"`) **and restructure `conftest.pytest_collection_modifyitems` explicitly** — the as-built hook early-returns when `HARNESS_LIVE == "1"`, which would leave `live_net` tests unskipped; replace it with two independent conditionals in one pass, no early return:

```python
def pytest_collection_modifyitems(config, items):
    skip_live = pytest.mark.skip(reason="live Zotero not enabled (HARNESS_LIVE=1)")
    skip_net = pytest.mark.skip(
        reason="live network not enabled (HARNESS_LIVE_NET=1)")
    for item in items:
        if "live" in item.keywords and os.environ.get("HARNESS_LIVE") != "1":
            item.add_marker(skip_live)
        if "live_net" in item.keywords and os.environ.get(
                "HARNESS_LIVE_NET") != "1":
            item.add_marker(skip_net)
```

- [ ] **Step 2: Run to verify failure**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_verify_cli.py -v`
Expected: FAIL — `ImportError: cannot import name 'run_verify'`

- [ ] **Step 3: Implement `run_verify` + verbs in `__main__.py`**

```python
# additions to core/harness_core/__main__.py
import datetime as _dt

from . import bibliography as _bib
from . import checks as _checks
from . import events as _events
from . import inbox as _inbox
from . import lints as _lints
from . import quotes as _quotes
from .notes import note_path as _note_path


def _file_outcomes(vault, path):
    outs = _checks.check_citekeys(vault, path)
    outs += _quotes.check_all_quotes(vault, path)
    outs += _lints.lint_source_status(vault, path)
    outs += _lints.lint_contested(vault, path)
    return outs


def _target_hash(vault, outcome):
    """Ack-scope key: cited note's first attachment hash, else file sha256."""
    from . import frontmatter as _fm
    import hashlib as _hl
    citekey = outcome.target.split("#")[0]
    p = _note_path(vault, citekey)
    if p.is_file():
        data, _ = _fm.parse(p.read_text())
        hashes = data.get("attachment-sha256") or []
        if hashes:
            return hashes[0]
        return _hl.sha256(p.read_bytes()).hexdigest()[:16]
    return None


def _stamp_verify_failed(vault, outcome, date):
    """§5: UNMATCHED claim-level results travel with the claim."""
    from pathlib import Path as _P
    for folder in ("efforts", "atlas", "literatures"):
        for p in _P(vault).glob(f"{folder}/**/*.md"):
            text = p.read_text()
            changed = False
            lines = text.split("\n")
            for i, line in enumerate(lines):
                anchor = outcome.target.rsplit("#^", 1)[-1]
                if line.rstrip().endswith(f"^{anchor}") and \
                        "[verify-failed:: " not in line:
                    lines[i] = line.replace(
                        f"^{anchor}",
                        f"[verify-failed:: {outcome.check}/{date}] ^{anchor}")
                    changed = True
            if changed:
                p.write_text("\n".join(lines))
                return


def _clear_verify_failed(vault, outcome):
    from pathlib import Path as _P
    import re as _re
    anchor = outcome.target.rsplit("#^", 1)[-1]
    for folder in ("efforts", "atlas", "literatures"):
        for p in _P(vault).glob(f"{folder}/**/*.md"):
            text = p.read_text()
            new = _re.sub(r"\[verify-failed:: [^\]]*\] (\^" + anchor + r")",
                          r"\1", text)
            if new != text:
                p.write_text(new)


def run_verify(vault_root, scope="all", network=True, detection_date=None,
               rw_csv=None):
    from . import Result as R
    from pathlib import Path
    detection_date = detection_date or _dt.date.today().isoformat()
    outcomes = []
    open_keys = set()
    for e in _inbox.load(vault_root):
        if e.ack_of is None:
            open_keys.add((e.check, e.target, e.result, e.target_hash))

    if network:
        outcomes.append(_checks.Outcome(
            "staleness", _bib.BIB_PATH,
            _bib.staleness(vault_root, ZoteroClient()), "stale — see §4"))
    else:
        outcomes.append(_checks.Outcome("staleness", _bib.BIB_PATH,
                                        R.UNREACHABLE,
                                        "outage — network disabled"))

    note_files = [p for folder in ("literatures", "atlas", "efforts")
                  for p in sorted(Path(vault_root).glob(f"{folder}/**/*.md"))]
    quote_passes = []
    for p in note_files:
        for o in _file_outcomes(vault_root, p):
            outcomes.append(o)
            if o.check == "quote":
                if o.result is R.MATCHED:
                    quote_passes.append(o)
                    _clear_verify_failed(vault_root, o)
                elif o.result is R.UNMATCHED:
                    _stamp_verify_failed(vault_root, o, detection_date)

    # quote events land on the cited literature note (§5 attachment point)
    for o in quote_passes:
        citekey = o.target.split("#")[0]
        note_file = _note_path(vault_root, citekey)
        if note_file.is_file():
            note_file.write_text(_events.record_pass(
                note_file.read_text(),
                f"quote:{o.target}:{o.extra.get('target', 'managed-region')}",
                R.MATCHED))

    bib = _bib.load(vault_root)
    rw = _checks.load_rw_csv(rw_csv) if rw_csv else None
    for key in sorted(bib.citekeys):
        entry = bib.entry(key)
        if not network:
            for check_name in ("doi", "metadata", "update-notice"):
                outcomes.append(_checks.Outcome(check_name, key, R.UNREACHABLE,
                                                "outage — network disabled"))
            continue
        doi = entry.get("DOI") or entry.get("doi")
        if not doi:
            from . import identify as _identify
            entry = dict(entry, **_identify.discover(vault_root, entry))
            doi = entry.get("DOI")
        note_outs = []
        if doi:
            note_outs.append(_checks.check_doi_exists(vault_root, doi))
            note_outs.append(_checks.check_metadata(vault_root, entry))
        else:
            note_outs.append(_checks.Outcome(
                "doi", key, R.SKIPPED, "no-identifier — discovery found nothing"))
        # update-notice ALWAYS runs — PMID-bearing entries are never exempt (§6)
        note_outs.append(_checks.check_update_notice(vault_root, entry,
                                                     detection_date))
        if rw is not None:
            hit = _checks.check_rw_batch(entry, rw, detection_date)
            if hit is not None:
                note_outs.append(hit)
        outcomes += note_outs
        note_file = _note_path(vault_root, key)
        if note_file.is_file():
            text = note_file.read_text()
            for o in note_outs:
                if o.result is R.MATCHED and o.check in (
                        "doi", "metadata", "update-notice"):
                    text = _events.record_pass(text, o.check, R.MATCHED)
            note_file.write_text(text)

    outcomes += _lints.lint_append_only(vault_root)
    outcomes += _lints.lint_claim_immutability(vault_root)
    outcomes += _lints.lint_published_drift(vault_root)
    for o in _lints.lint_web_archive(vault_root):
        outcomes.append(o)
    if network:
        from . import frontmatter as _fm
        for p in sorted(Path(vault_root).glob("literatures/*.md")):
            data, _ = _fm.parse(p.read_text())
            au = data.get("archive-url")
            if au:
                try:
                    status, _body = _checks.webapi.get_json(au, vault_root)
                    if status == 404:
                        outcomes.append(_checks.Outcome(
                            "web-archive", data.get("citekey", p.stem),
                            R.UNMATCHED, "missing-archive — archive-url 404s"))
                except _checks.webapi.ApiError as e:
                    outcomes.append(_checks.Outcome(
                        "web-archive", data.get("citekey", p.stem),
                        R.UNREACHABLE, f"outage — {e}"))

    # inbox filing: MATCHED never files via _record; warns file dedup'd
    for o in outcomes:
        th = _target_hash(vault_root, o)
        if o.result is not R.MATCHED:
            key4 = (o.check, o.target, o.result.value, th)
            if key4 not in open_keys:
                _inbox.append_entry(
                    vault_root, o.check, o.target, o.result, o.reason,
                    target_hash=th,
                    notice_date=o.extra.get("notice_date"),
                    detection_date=o.extra.get("detection_date"))
                open_keys.add(key4)
        for w in o.extra.get("warn_notices", []):
            wkey = (o.check, o.target, "warn:" + w["type"], th)
            if wkey not in open_keys:
                _inbox.append_entry(
                    vault_root, o.check, o.target, R.UNMATCHED,
                    f"warn-notice — {w['type']}", target_hash=th,
                    notice_date=w.get("notice_date"),
                    detection_date=detection_date)
                open_keys.add(wkey)

    counts = {}
    for o in outcomes:
        counts[o.result.value] = counts.get(o.result.value, 0) + 1
    return {"outcomes": outcomes, "counts": counts}


CLOSING_CHECKS = {"citekey", "quote", "update-notice", "evidence-layer"}


def cmd_verify(args):
    from . import Result as R
    report = run_verify(args.vault, network=not args.offline,
                        rw_csv=getattr(args, "rw_csv", None))
    for o in report["outcomes"]:
        if o.result is not R.MATCHED:
            print(f"{o.result.value} {o.check} {o.target} — {o.reason}")
    print(json.dumps(report["counts"]))
    closing_unmatched = any(
        o.result is R.UNMATCHED and o.check in CLOSING_CHECKS
        for o in report["outcomes"])
    if closing_unmatched:
        return 1
    if report["counts"].get("UNREACHABLE"):
        return 3
    return 0


def cmd_inbox(args):
    s = _inbox.summary(args.vault)
    print(json.dumps(s))
    acked = {e.ack_of for e in _inbox.load(args.vault) if e.ack_of}
    for e in sorted((e for e in _inbox.load(args.vault)
                     if e.ack_of is None and e.id not in acked),
                    key=lambda e: e.date):
        print(f"{e.date} {e.result} {e.check} {e.target} — {e.reason}")
    return 0
```

Wire both into `main()` (`verify` gets `--vault` required, `--offline`, and `--rw-csv <path>` — the Plan C cron surface for the RW batch leg; `inbox` gets `--vault`), reusing the `parents=[common]` pattern. `staleness` line adapts to the as-built import names (`ZoteroClient` is already imported in the module).

- [ ] **Step 4: Run offline tests, then the live-net drill**

Run: `cd core && source .venv/bin/activate && python -m pytest tests/test_verify_cli.py -v`
Expected: 4 PASS, 1 SKIP (live_net)

Run: `HARNESS_LIVE_NET=1 HARNESS_MAILTO=<your real email> python -m pytest tests/test_verify_cli.py -v -m live_net`
Expected: PASS — Wakefield blocking retraction detected with a Crossref-sourced notice date in `2010-02` (currently `2010-02-06`; deposits may be re-issued, so the drill asserts month precision), fabricated DOI UNMATCHED, Zenodo routes to DataCite. **These are §9 drill legs 1, 3, and the registry drill, proven against the real world.**

- [ ] **Step 5: Run the full suite, commit**

Run: `cd core && source .venv/bin/activate && python -m pytest tests -q`
Expected: all PASS (live markers skip per env)

```bash
cd "$(git rev-parse --show-toplevel)"
git add core && git commit -m "feat: verify + inbox CLI verbs — orchestration, events, dedup, exit codes"
```

---

### Task 14: Merge

- [ ] **Step 1: Full suite green** — `cd core && source .venv/bin/activate && HARNESS_LIVE=1 HARNESS_LIVE_NET=1 HARNESS_MAILTO=<real email> python -m pytest tests -q`
- [ ] **Step 2: Merge** — use `superpowers:finishing-a-development-branch` to integrate `build/plan-b` and clean the worktree.

---

## Pre-flight rulings (execution-time, all granted: the contract governs)

1. **Inbox**: notice-date/detection-date implemented as fields; controlled reason prefixes VALIDATED at append (findings, acks, deprecations); example strings corrected to open with vocabulary codes (`manual — …`, `superseded-source — …`).
2. **HTTP boundary**: `get_json` returns the real response status; a status-only helper serves HTML archive-URL resolution; JSON shapes validated; **registry-routing failure = UNREACHABLE, never a non-Crossref match**; discovery distinguishes no-hit from provider outage (outage must not let SKIPPED stick).
3. **Normalization**: shared quote pipeline case-sensitive; metadata/discovery casefold locally; selector offset mapping reproduces whole-string NFKC incl. composed/decomposed sequences.
4. **Coverage**: citations scanned throughout a note, not only claim lines; quote comparison prefers the same-address source quote, falls back only when absent; SKIPPED when a note has no quote claims.
5. **Update notices**: reinstatement computed chronologically, independent of API ordering; live + RW legs combine into ONE effective outcome (blocking precedence); trust-tier requires update-notice coverage when the note has a DOI **or** PMID.
6. **Integrity lints**: HEAD files enumerated so whole-file deletion is detected; deterministic `[verify-failed:: …]` add/remove transitions are permitted mutations in the immutability comparison (the stamp and the lint must not trip each other).
7. **Targets/acks/markers**: note-level targets standardized on citekeys (DOI in `extra`); file targets never reach `note_path`; outcomes carry enough claim identity to mutate only the correct line; hash-aware acks clear the matching marker, hide the finding from inbox/summary, bypass closure, and retain the raw outcome for audit.
8. **Warn dedup**: warn type persisted/reconstructed from entries so re-runs never re-append.

9. **No-attachment ack hashes**: hash canonical note content excluding ONLY verifier-owned surfaces — the frontmatter `verified` list and inline `[verify-failed:: …]` fields, enumerated and frozen in a single `canonical_content(note_text) -> str` both the ack-hash and future changed-content logic use. Deprecation transition records are NOT excluded (substantive — should invalidate acks). Verification cannot invalidate itself; whole-file SHA rejected as a self-invalidation loop. CLI reuses the same pre-effect decision state.

## Whole-branch rulings (final fix wave, all granted)

10. **Notice-fingerprint ack scope**: update-notice acks scope to `(check, target, content-hash, class, type, notice-date)` — identical notices stay acknowledged; a warn-class ack can never suppress a later blocking-class notice. Narrowly supersedes the earlier update-notice ack rule.
11. **Current-state trust projection**: historical `verified` events preserved; a deterministic current-failure projection demotes trust on later failures; a subsequent MATCHED clears the failure and appends a new pass; failures still file in the inbox. **Amends ruling 9**: the ack-hash exclusion set is now the frontmatter `verified` list ONLY — `[verify-failed:: …]` markers are hash-substantive (failure transitions are information; stamping is idempotent so re-runs stay stable; routine passes remain excluded to prevent the self-invalidation loop).
12. **Version-status contract (non-Crossref)**: MATCHED only after BOTH OpenAlex retraction status AND provider version status are established. Day-one provider list: arXiv (API version/withdrawal state) and DataCite (metadata `version`); any other registry — and any missing/ambiguous version status — returns UNREACHABLE, never silently clean.

Ordinary defects handled in the same wave without ruling: malformed bibliography data crashing verification; malformed event mappings elevating trust; non-atomic inbox field validation.

13. **Registry dates**: the live Crossref contract governs notice dates — the check reports registry data with registry vintage, not historical announcement dates (Wakefield: Crossref says 2010-02-06; The Lancet announced 2010-02-02). Live drill assertions harden to month precision against re-deposits; offline fixtures keep exact dates as precise extraction tests.

Clerical (no ruling): ruff-driven test rewrites, exact Plan A marker matching, corrected expected test counts — HEAD governs.

## Self-Review (completed at authoring)

**Spec coverage (this plan's slice):** §3 inbox serialization/ack/scope/summary → T2; §5 events + tier + MATCHED-only → T3; §6 rows: citekey → T5, DOI+registry → T6, metadata+author rule → T7, update-notice full taxonomy + bi-temporal + RW CSV + PMID → T8, discovery-before-SKIPPED → T9, quote gate + sparsity path → T10, six integrity lints → T11; §5 selector capture (Plan A obligation + symmetric unescape) → T12; orchestration/events/dedup/exit codes → T13. Deliberately out: gate *placement* (hooks, pre-commit, CI, publish flag file — Plan C consumes the exit codes), archive-at-import and hold policies (import-source behavior — Plan D skills call these functions), RW CSV *download* (Plan C cron; T8 consumes a local file).
**Placeholders:** none. Two as-built-dependency points are named with their resolution procedure (selector unescape mirrors `notes.py` at HEAD — enforced by a test; `run_verify` staleness line adapts to as-built import names). HEAD-governs rule covers residual drift.
**Verification history:** three-lens adversarial pass (spec fidelity / desk-check vs as-built Plan A in sandbox / zero-context walkthrough) found 6 CRITICAL + 13 IMPORTANT + 11 MINOR defects — all fixed in this revision: quote events now mint via the verify verb (machine-confirmed reachable), DOI-less entries route to update-notice with re-derived identifiers (never structurally exempt), FIELD_RE admits wikilinks, claim-immutability compares whole claim blocks, contested-set semantics corrected, casefold split out of the quote pipeline, offline = UNREACHABLE never SKIPPED, bi-temporal inbox fields, verify-failed stamping/clearing, dedup keyed on target hash with warn-tier keys, closing-class exit contract, selectors index map rebuilt per emitted char, apostrophe in the symmetry inversion, venv bootstrap, conftest two-conditional skip logic.

**Type consistency:** `Outcome` defined T5, consumed T6–T13; `normalize_text` defined T7, consumed T9/T10/T12; `Claim`/`claim_address` defined T1, consumed T3/T10/T11; `Entry`/`INBOX_PATH` defined T2, consumed T13; `Result` semantics uniform; `parents=[common]` argparse pattern continues Plan A's.

## Supersessions (2026-08-21)

1. **`run_verify` superseded — the public seam is the verification transaction
   itself.** The `run_verify(vault_root, scope="all", network=True,
   detection_date=None, rw_csv=None)` signature above is description, not
   contract: it carried no ruling marker, and by 2026-08-21 the function had no
   caller outside the test suite, which used it as a report-projecting wrapper.
   It is removed; its tests call `_verify_state` and project the report locally.
   The `scope` parameter is removed with it — it was deleted unread on entry to
   `_plan_state` and no caller ever passed a non-default value, so no behaviour
   depended on it. Plan R Task 2 renames the remaining private seam
   (`_verify_state`/`_surface_decision`/`_file_outcomes`) to its public spelling.
