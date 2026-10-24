# Substrate Components, Plan B: The Capture Monitor and `literature/`

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every change a Zotero add-on or a restore pushes into `literature/` visible and held: the snapshot carries native identifiers (#185), folded field names (#188) and Obsidian-readable tags (#195); a new `capture-monitor` check reports every attested value change with an older-render guard (#205); a trashed attachment is drift (#189), a bibliography entry moves only with its note (#196), the verifier's lists are append-only (#206), a merge is a propagation (#183); and publish re-checks every commit since the last publication (Q2).

**Architecture:** `literature_notes.snapshot` grows the native fields and the schema fold; a `zotero-tags`/`tags` split lands in the same render path. `lints.lint_evidence_layer` gains two sibling functions inside its pair loops: `_capture_monitor_outcomes` (check `capture-monitor`, attested pairs only, reasons built from JSON-encoded capped values) and `_verifier_list_outcomes` (#206, hashed on the lists). Capture exports each item's CSL entry before rendering and writes `csl-sha256` into the tuple; `captured-set` compares it. `propagate` learns a `merged` mapping with a successor item key. `verify_state` gains a per-commit history re-check that publish and CI call.

**Tech Stack:** Python 3.12 in `.venv`; pytest with xdist and `tests/fakes.py::FakeZotero`; git 2.43; the local Zotero API and Better BibTeX JSON-RPC on the test instance (`localhost:23129`) for the live legs.

**Spec:** `docs/superpowers/specs/2026-10-03-substrate-components-design.md` §5.3 (all subsections), §5.3.1's publish re-check, §8's Zotero legs for these items, §11's ingest-spec amendments. Designs cluster 1 (`…-section-3-designs.md`) carries the acceptance tests 1–16 this plan implements; research Q2, Q3, Q9, Q20, Q21 the mechanisms. "§N", "decision NN", "ruling N" as in Plan A. Every `file:line` cite is the spec's, valid at `6419497` for files Plan A did not touch; where Plan A moved a line the task says so.

**Precondition:** Plan A (`2026-10-24-substrate-components-a-structure-and-links.md`) has merged to `main`: `research_vault/links.py`, `research_vault/fixer.py`, `frontmatter.read_okf`, the `dead-link` check and the fix-then-fail hook exist. Check with `python -c "from research_vault import links, fixer; from research_vault.frontmatter import read_okf"` before Task 1.

## Global Constraints

The Global Constraints of Plan A apply verbatim (venv and suite command, form owners run directly, pathspec commits with the model trailer, branch motion with `--ff-only` merges, `must_replace`, the skill-name backtick rule, the dangling-path hatch, the baseline hand-edit rule, dates, machine-local facts, registry rows in the same commit, issues closed by the task that lands them, live checks as attended tasks). Branch names here are `substrate-b/<task-slug>`. Two more:

- Every offline test that needs Zotero registers its answers on `tests/fakes.py::FakeZotero`; a test that needs the schema reads `fakes.SCHEMA` (Task 2). Nothing in the offline suite opens a socket (`docs/agents/testing.md`).
- The designs' acceptance tests 1–16 (cluster 1, "Acceptance tests") are the floor: each task names the numbers it discharges, and Task 11 checks that every number has a test.

## Deviations from the spec, settled here

1. **#183's deletion and ADR 0003.** §5.3.6 deletes a merged-away note when the survivor already has one; ADR 0003 says a note that leaves the library is kept, `propagate.plan` refuses to rename over an existing file on that ground (`propagate.py:184-195`), and `lint_evidence_layer` reports every deletion. §11 amends no ADR. Task 8 adds a dated scope note to ADR 0003, carries the merge in the propagation record, and teaches the evidence-layer lint to read that record so the deletion is attested by the plan that made it. The operator should read that note; the plan does not stop for it.
2. **Tag-only changes are capture's row, not verify's.** §5.3.1 files them "as one non-blocking summary row per capture run"; verify has no notion of a run. Capture files it under its own check id `capture` (closing on no surface) with the notes named (Task 4).
3. **The whole-library CSL read goes.** §5.3.7 and Q20 say an entry changes only when its note re-renders, and Q20 costs it as "one `item.export` before render". The Better BibTeX library route (`zotero.library_csl`, `capture._regenerate_csl`) has no remaining caller and is deleted with its tests (Task 6); `export_csl` stays.
4. **#206's rows ride `evidence-layer`** (§7 coins no id for them) with reasons of their own and `extra={"hash_basis": "verifier-lists"}`, which `_snapshot_path_hash` reads to hash the lists instead of the note bytes (Task 7).
5. **The history re-check's base.** "Every commit since the last publication" is read as the newest `published/*` tag of any project, by the tag's own date-time suffix (`lints.PUBLISHED_TAG`); a vault with no publication re-checks its whole history, as Q2 measured (about 2 s). CI passes its push base (Task 9).

______________________________________________________________________

### Task 1: Native `PMID` and `PMCID` in the snapshot (#185)

**Files:**

- Modify: `research_vault/literature_notes.py:34-52` (`SNAPSHOT_FIELDS`), `research_vault/events.py:256-262` (`_applicable_note_checks`), `skills/capture-source/SKILL.md:17` (the field list)
- Test: `tests/test_literature_notes.py`, `tests/test_events.py:545-556`, `tests/test_capture.py`

**Interfaces:**

- Produces: `SNAPSHOT_FIELDS` carries `PMID` and `PMCID` after `DOI`; `events._applicable_note_checks` reads `data["PMID"]` first. `capture.add` accepts the two fields (`_ITEM_FIELDS` derives from `SNAPSHOT_FIELDS`).

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_literature_notes.py`:

```python
def test_snapshot_carries_zoteros_native_identifier_fields():
    """#185: Zotero 10 carries PMID and PMCID as fields; the snapshot copies
    them under Zotero's own names, beside DOI, and the trust tier sees them."""
    fields = dict(
        literature_notes.snapshot(
            {"itemType": "journalArticle", "title": "T", "PMID": "28503678", "PMCID": "PMC5428074"}
        )
    )
    assert fields["PMID"] == "28503678"
    assert fields["PMCID"] == "PMC5428074"
    assert literature_notes.SNAPSHOT_FIELDS.index("PMID") == literature_notes.SNAPSHOT_FIELDS.index("DOI") + 1
    assert literature_notes.SNAPSHOT_FIELDS.index("PMCID") == literature_notes.SNAPSHOT_FIELDS.index("DOI") + 2
```

In `tests/test_events.py:545-556`, add two cases to the parametrize: `({"PMID": "28503678"}, {"update-notice"})` and `({"PMCID": "PMC5428074"}, set())` (a PMCID alone is not a PubMed id the update-notice check can query). Append to `tests/test_capture.py`:

```python
def test_add_accepts_the_native_identifier_fields():
    assert capture._validate_items([{"itemType": "journalArticle", "PMID": "1", "PMCID": "PMC1"}]) is None
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_literature_notes.py tests/test_events.py tests/test_capture.py -q -k "native or applicable or accepts_the_native"`
Expected: FAIL — `PMID` is not in `SNAPSHOT_FIELDS`; `_applicable_note_checks` ignores it; `_validate_items` rejects it.

- [ ] **Step 3: The three edits**

`research_vault/literature_notes.py:34-52`:

```python
SNAPSHOT_FIELDS: tuple[str, ...] = (
    "itemType",
    "title",
    "creators",
    "date",
    "DOI",
    # #185: Zotero 10's native identifier fields, under Zotero's names.
    "PMID",
    "PMCID",
    "url",
    "publicationTitle",
    "volume",
    "issue",
    "pages",
    "publisher",
    "ISBN",
    "language",
    "abstractNote",
    "extra",
    "accessDate",
    "tags",
)
```

`research_vault/events.py:256-262`:

```python
def _applicable_note_checks(data: dict) -> set[str]:
    has_doi = bool(data.get("DOI") or data.get("doi"))
    # #185: the native field first; the Extra line is the pre-Zotero-10 spelling.
    has_pmid = (
        bool(data.get("PMID"))
        or bool(data.get("pmid"))
        or any(
            line.strip().upper().startswith("PMID:")
            for line in _extra_lines(data.get("extra"))
        )
    )
    return {"update-notice"} if has_doi or has_pmid else set()
```

`skills/capture-source/SKILL.md:17`: the parenthesised field list gains `` `PMID`, `PMCID` `` after `` `DOI` ``.

- [ ] **Step 4: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider`
Expected: PASS. `tests/test_capture_source_skill.py` scans the skill for needles only, so the longer list passes.

- [ ] **Step 5: Form, commit, branch**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests && mdformat skills/capture-source/SKILL.md
git switch -c substrate-b/native-pmid
git commit -m "feat(capture): the snapshot carries Zotero 10's native PMID and PMCID; the trust tier reads them (#185)" -- research_vault/literature_notes.py research_vault/events.py skills/capture-source/SKILL.md tests/test_literature_notes.py tests/test_events.py tests/test_capture.py
git push -u origin substrate-b/native-pmid
```

#185 closes after Task 10's live leg confirms Zotero accepts the fields per item type (§8); the offline half is this task.

______________________________________________________________________

### Task 2: Type-specific fields fold to Zotero's base names through `/api/schema` (#188, Q21)

**Files:**

- Modify: `research_vault/zotero.py` (`ZoteroClient.schema`), `research_vault/literature_notes.py:327-335,475-521` (`base_field_map`, `snapshot(item_data, base_fields)`, `render_note(..., base_fields)`), `research_vault/capture.py:162-258,433-579` (one schema read per run; refuse on failure), `tests/fakes.py` (a canned schema every fake serves)
- Test: `tests/test_literature_notes.py`, `tests/test_capture.py`, `tests/test_zotero.py`

**Interfaces:**

- Produces: `ZoteroClient.schema() -> dict` (GET `/api/schema`; a payload without an `itemTypes` list is a `ZoteroError`). `literature_notes.base_field_map(schema) -> dict[str, dict[str, str]]` — `{itemType: {typeField: baseField}}` for every field that declares a `baseField`. `literature_notes.snapshot(item_data, base_fields: Mapping[str, str] | None = None)` — a value under a type-specific name is emitted under its base name; a base-named value wins when both are present. `render_note(..., base_fields=None)`. `fakes.SCHEMA` and `FakeZotero.__init__` registering `/api/schema`.

- Consumes: Task 1's field list.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_literature_notes.py`:

```python
from tests.fakes import SCHEMA


def test_base_field_map_reads_every_declared_base_field():
    folded = literature_notes.base_field_map(SCHEMA)
    assert folded["conferencePaper"]["proceedingsTitle"] == "publicationTitle"
    assert folded["bookSection"]["bookTitle"] == "publicationTitle"
    assert folded["webpage"]["websiteTitle"] == "publicationTitle"
    assert folded["report"]["institution"] == "publisher"
    assert "title" not in folded["journalArticle"]  # a base field names no base


def test_snapshot_folds_a_type_specific_field_to_its_base_name():
    """#188: a conference paper's venue is `proceedingsTitle` in Zotero's JSON and
    `publicationTitle` in the note, so a change of item type is not read as a
    removed venue (Q21)."""
    folded = literature_notes.base_field_map(SCHEMA)["conferencePaper"]
    fields = dict(
        literature_notes.snapshot(
            {"itemType": "conferencePaper", "title": "T", "proceedingsTitle": "CHI 2023", "pages": "1-10"},
            folded,
        )
    )
    assert fields["publicationTitle"] == "CHI 2023"
    assert "proceedingsTitle" not in fields
    assert [k for k, _ in literature_notes.snapshot({"itemType": "conferencePaper", "proceedingsTitle": "C", "title": "T"}, folded)] == ["itemType", "title", "publicationTitle"]


def test_snapshot_without_a_map_keeps_zoteros_names_as_before():
    fields = dict(literature_notes.snapshot({"itemType": "conferencePaper", "proceedingsTitle": "C"}))
    assert "publicationTitle" not in fields and "proceedingsTitle" not in fields
```

Append to `tests/test_capture.py`:

```python
def test_capture_reads_the_schema_once_and_folds_the_venue(tmp_vault, monkeypatch):
    paper = json.loads(json.dumps(ITEM))
    paper["data"]["itemType"] = "conferencePaper"
    paper["data"]["proceedingsTitle"] = paper["data"].pop("publicationTitle")
    fake = _canned_run(canned_item(FakeZotero(), item=paper), items=(paper,))
    client = _client(monkeypatch, fake)
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"])
    assert outcomes[0].result is Result.MATCHED
    data, _ = frontmatter.parse((tmp_vault / "literature" / "jakesch.etal2023a.md").read_text())
    assert data["publicationTitle"] == "CHI 2023"
    assert "proceedingsTitle" not in data
    assert [c for c in fake.calls if c[1] == "/api/schema"] == [("GET", "/api/schema", {"Zotero-Server-ID": "6LpvURP2E933"})] or len(
        [c for c in fake.calls if c[1] == "/api/schema"]
    ) == 1


def test_capture_refuses_when_the_schema_cannot_be_read(tmp_vault, monkeypatch):
    """Q21: without the fold the snapshot would carry unfolded names, which the
    monitor would later read as a removed venue; capture refuses instead."""
    fake = _canned_run(canned_item(FakeZotero()))
    fake.get("/api/schema", status=500, body=b"")
    client = _client(monkeypatch, fake)
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"])
    assert [(o.target, o.result) for o in outcomes] == [("vault", Result.UNREACHABLE)]
    assert outcomes[0].reason.startswith("outage — ")
    assert not (tmp_vault / "literature" / "jakesch.etal2023a.md").exists()
```

Append to `tests/test_zotero.py`:

```python
def test_schema_reads_the_local_api_schema_route(monkeypatch):
    fake = FakeZotero()
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    schema = client.schema()
    assert isinstance(schema["itemTypes"], list)
    fake.get("/api/schema", body={"version": 1})
    with pytest.raises(zotero.ZoteroError, match="malformed schema"):
        client.schema()
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_literature_notes.py tests/test_capture.py tests/test_zotero.py -q -k "schema or fold or base_field"`
Expected: FAIL — no `SCHEMA`, no `schema()`, no `base_field_map`.

- [ ] **Step 3: The fake's schema**

Append to `tests/fakes.py` and register it in `FakeZotero.__init__` after the `/api/` route (`self.get("/api/schema", body=SCHEMA)`):

```python
# The subset of Zotero's schema the fold reads (`/api/schema`): every type-specific
# field names its base field. Shapes from the Zotero schema JSON (version 44 on
# 10.0.5); only the fields the tests exercise are listed.
SCHEMA = {
    "version": 44,
    "itemTypes": [
        {
            "itemType": "journalArticle",
            "fields": [{"field": "title"}, {"field": "publicationTitle"}, {"field": "DOI"}, {"field": "PMID"}, {"field": "PMCID"}],
            "creatorTypes": [{"creatorType": "author", "primary": True}],
        },
        {
            "itemType": "conferencePaper",
            "fields": [{"field": "title"}, {"field": "proceedingsTitle", "baseField": "publicationTitle"}, {"field": "DOI"}, {"field": "pages"}],
            "creatorTypes": [{"creatorType": "author", "primary": True}],
        },
        {
            "itemType": "bookSection",
            "fields": [{"field": "title"}, {"field": "bookTitle", "baseField": "publicationTitle"}, {"field": "publisher"}],
            "creatorTypes": [{"creatorType": "author", "primary": True}],
        },
        {
            "itemType": "webpage",
            "fields": [{"field": "title"}, {"field": "websiteTitle", "baseField": "publicationTitle"}, {"field": "url"}],
            "creatorTypes": [{"creatorType": "author", "primary": True}],
        },
        {
            "itemType": "report",
            "fields": [{"field": "title"}, {"field": "institution", "baseField": "publisher"}, {"field": "reportNumber", "baseField": "number"}],
            "creatorTypes": [{"creatorType": "author", "primary": True}],
        },
        {
            "itemType": "preprint",
            "fields": [{"field": "title"}, {"field": "repository", "baseField": "publisher"}, {"field": "DOI"}],
            "creatorTypes": [{"creatorType": "author", "primary": True}],
        },
    ],
}
```

- [ ] **Step 4: The client, the fold, the render**

`research_vault/zotero.py` — after `server_info`:

```python
    def schema(self) -> dict:
        """Zotero's own field schema (#188): type-specific names and their base
        fields, read once per capture run from the local API."""
        payload, _ = self._local_json("/api/schema")
        if not isinstance(payload, Mapping) or not isinstance(payload.get("itemTypes"), list):
            raise ZoteroError("malformed schema: expected an object with itemTypes")
        return dict(payload)
```

`research_vault/literature_notes.py` — add after `SNAPSHOT_FIELDS`:

```python
def base_field_map(schema: Mapping) -> dict[str, dict[str, str]]:
    """``{itemType: {typeField: baseField}}`` from Zotero's schema (#188): the
    mapping is Zotero's, read from ``/api/schema``, never ours."""
    folded: dict[str, dict[str, str]] = {}
    for item_type in schema.get("itemTypes", []):
        if not isinstance(item_type, Mapping):
            continue
        name = item_type.get("itemType")
        if not isinstance(name, str):
            continue
        folded[name] = {
            field["field"]: field["baseField"]
            for field in item_type.get("fields", [])
            if isinstance(field, Mapping)
            and isinstance(field.get("field"), str)
            and isinstance(field.get("baseField"), str)
        }
    return folded
```

(`from collections.abc import Mapping` at the top.) Replace `snapshot` (`:327-335`):

```python
def snapshot(item_data, base_fields: Mapping[str, str] | None = None) -> list[tuple[str, object]]:
    """The fixed subset, verbatim, under Zotero's base field names; empty values absent.

    ``base_fields`` is the item type's row of ``base_field_map``: a value under a
    type-specific name (``proceedingsTitle``) is carried under its base name
    (``publicationTitle``), so a change of item type is not a removed field
    (#188). A base-named value already present wins over a folded one.
    """
    folded: dict[str, object] = {}
    for name, value in item_data.items():
        key = (base_fields or {}).get(name, name)
        if key not in SNAPSHOT_FIELDS or value in (None, "", []):
            continue
        if key == name or key not in folded:
            folded[key] = value
    return [(name, frontmatter_value(folded[name])) for name in SNAPSHOT_FIELDS if name in folded]
```

`render_note` gains `base_fields=None` as its last keyword and passes it to `snapshot`; its title line becomes `title = display_text(dict(snapshot(item_data, base_fields)).get("title") or provenance.citation_key)` (so `caseName` and the other title-shaped fields fold too), and the `fields.extend((k, v) for k, v in snapshot(item_data, base_fields) if k != "title")` call passes the map.

- [ ] **Step 5: Capture reads the schema once and refuses without it**

In `research_vault/capture.py::capture`, after `info = client.server_info()`'s `try` block and before `existing = lifecycle._provenances(vault)`:

```python
    try:
        base_fields = literature_notes.base_field_map(client.schema())
    except ZoteroError as error:
        # #188: without the fold the snapshot would carry unfolded names, which
        # the monitor reads as a removed venue on the next run; refuse instead.
        return [lifecycle.blocked(CHECK, "vault", error)]
```

`_capture_one(vault, read, server_id, now, base_fields)` takes the run's map and passes `base_fields.get(item["data"].get("itemType"), {})` into `render_note(..., base_fields=…)`; the two callers (`capture()`'s loop and `propagate.apply`'s recapture through `capture.capture`) are covered by the one call site in `capture()`.

- [ ] **Step 6: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider && mypy`
Expected: PASS. Every capture test already builds a `FakeZotero`, which now serves the schema; a test that asserts the exact call list of the fake (grep `fake.calls ==` in `tests/test_capture.py`) gains the `GET /api/schema` call after `/api/`.

- [ ] **Step 7: Form, commit, branch**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests
git switch -c substrate-b/schema-fold
git commit -m "feat(capture): type-specific fields fold to Zotero's base names through /api/schema; capture refuses without the schema (#188)" -- research_vault/zotero.py research_vault/literature_notes.py research_vault/capture.py tests/fakes.py tests/test_literature_notes.py tests/test_capture.py tests/test_zotero.py
git push -u origin substrate-b/schema-fold
```

#188 closes after Task 10's live leg (the fold against the real `/api/schema`); Task 11 amends the ingest spec's `:133`.

______________________________________________________________________

### Task 3: `zotero-tags` and a slugged `tags` (#195, Q9)

**Files:**

- Modify: `research_vault/literature_notes.py` (`SNAPSHOT_FIELDS`, `slug_tag`, `slug_tags`, `snapshot`), `research_vault/capture.py:582` (`_ITEM_FIELDS`), `CONTEXT.md:57` and `research_vault/templates/context.md` (the **Snapshot** entry), `skills/capture-source/SKILL.md:17`
- Test: `tests/test_literature_notes.py`, `tests/test_capture.py`

**Interfaces:**

- Produces: `SNAPSHOT_FIELDS` ends `…, "accessDate", "zotero-tags", "tags"`; `snapshot` emits `zotero-tags` as Zotero's list exactly and `tags` as `slug_tags(...)`. `literature_notes.slug_tag(name: str) -> str | None`, `literature_notes.slug_tags(entries) -> list[str]`, `literature_notes.TAG_REJECT: re.Pattern`. `capture._ITEM_FIELDS` excludes `zotero-tags` (an `add` payload carries `tags`).

- Consumes: Task 2's `snapshot` signature.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_literature_notes.py`:

```python
@pytest.mark.parametrize(
    ("tag", "slug"),
    [
        ("ai", "ai"),
        ("doi-fix:low-confidence", "doi-fix-low-confidence"),
        ("triage:needed", "triage-needed"),
        ("human/computer interaction", "human/computer-interaction"),
        ("Evaluation / methodology", "Evaluation/methodology"),
        ("#nosource", "nosource"),
        ("❌ nosource", "nosource"),
        ("/unread", "unread"),
        ("a‐b—c’d", "a-b-c-d"),  # U+2010, U+2014, U+2019 are in Obsidian's rejected class
        ("x[1];y+z", "x-1-y-z"),
        ("日记", "日记"),
        ("2020", None),  # all ASCII digits
        ("٢٠٢٠", "٢٠٢٠"),  # non-ASCII digits are not "digits only" to Obsidian's ^#\d+$
        ("", None),
        ("---", None),
        ("a\x1cb", "a\x1cb"),  # JS \s lacks U+001C–U+001F and U+0085
        ("a﻿b", "a-b"),  # JS \s has U+FEFF
    ],
)
def test_slug_tag_repairs_what_obsidian_rejects_and_never_reinterprets_a_valid_tag(tag, slug):
    assert literature_notes.slug_tag(tag) == slug


def test_slug_tags_drops_duplicates_ignoring_case_and_keeps_both_tag_types():
    entries = [{"tag": "AI", "type": 1}, {"tag": "ai"}, {"tag": "2020"}, {"tag": "Methods: survey"}, "bare"]
    assert literature_notes.slug_tags(entries) == ["AI", "Methods-survey", "bare"]


def test_snapshot_splits_tags_into_zotero_tags_and_a_slugged_copy():
    fields = dict(
        literature_notes.snapshot(
            {"itemType": "journalArticle", "title": "T", "tags": [{"tag": "doi-fix:low-confidence"}, {"tag": "ai", "type": 1}]}
        )
    )
    assert fields["zotero-tags"] == [{"tag": "doi-fix:low-confidence"}, {"tag": "ai", "type": 1}]
    assert fields["tags"] == ["doi-fix-low-confidence", "ai"]
    assert literature_notes.SNAPSHOT_FIELDS[-2:] == ("zotero-tags", "tags")
    assert {"zotero-tags", "tags"} <= literature_notes.CAPTURE_FIELDS


def test_snapshot_omits_both_tag_keys_when_zotero_has_none():
    fields = dict(literature_notes.snapshot({"itemType": "journalArticle", "title": "T", "tags": []}))
    assert "zotero-tags" not in fields and "tags" not in fields
```

Append to `tests/test_capture.py`:

```python
def test_capture_writes_both_tag_fields(tmp_vault, monkeypatch):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    capture.capture(tmp_vault, client, ["E352DFS8"])
    data, _ = frontmatter.parse((tmp_vault / "literature" / "jakesch.etal2023a.md").read_text())
    assert data["zotero-tags"] == [{"tag": "ai", "type": 1}]
    assert data["tags"] == ["ai"]


def test_add_takes_tags_and_refuses_zotero_tags():
    assert capture._validate_items([{"itemType": "journalArticle", "tags": [{"tag": "a"}]}]) is None
    assert capture._validate_items([{"itemType": "journalArticle", "zotero-tags": []}]) == "item 0: unknown field zotero-tags"
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_literature_notes.py tests/test_capture.py -q -k "slug or tag"`
Expected: FAIL — `slug_tag` missing; `zotero-tags` absent.

- [ ] **Step 3: The slug and the split**

In `research_vault/literature_notes.py`, replace the last entry of `SNAPSHOT_FIELDS` (`"tags",`) with:

```python
    # #195: `zotero-tags` is Zotero's list exactly (today's `tags`, renamed);
    # `tags` is the slugged copy Obsidian reads.
    "zotero-tags",
    "tags",
```

and add after `SNAPSHOT_FIELDS`:

```python
# Obsidian 1.13.7's rejected tag characters, copied literally (Q9): general
# and supplemental punctuation, ASCII punctuation other than `_ - /`, and
# JavaScript's `\s` — which has U+FEFF and lacks U+001C–U+001F and U+0085,
# so Python's `\s` is not used. A tag that is only ASCII digits is also
# rejected (Obsidian's `^#\d+$` is ASCII-only, unlike Python's `\d`).
_JS_WHITESPACE = "\t\n\x0b\x0c\r    -     　﻿"
TAG_REJECT = re.compile(
    rf"[ -⁯⸀-⹿'!\"#$%&()*+,.:;<=>?@^`{{|}}~\[\]\\{_JS_WHITESPACE}]"
)
_ASCII_DIGITS_ONLY = re.compile(r"^[0-9]+$")


def slug_tag(name: str) -> str | None:
    """Repair what Obsidian rejects, never reinterpret what it accepts: every
    rejected character becomes `-`, runs collapse, `/` is kept so it nests,
    `-` is dropped around `/` and at the ends; empty and all-digit results are
    None (#195, Q9)."""
    slug = TAG_REJECT.sub("-", name)
    slug = re.sub(r"-{2,}", "-", slug)
    slug = re.sub(r"-*/-*", "/", slug)
    slug = re.sub(r"/{2,}", "/", slug).strip("-/")
    if not slug or _ASCII_DIGITS_ONLY.match(slug):
        return None
    return slug


def slug_tags(entries) -> list[str]:
    """Every tag of either type, slugged, duplicates removed ignoring case."""
    seen: set[str] = set()
    slugs: list[str] = []
    for entry in entries or []:
        name = entry.get("tag") if isinstance(entry, Mapping) else entry
        if not isinstance(name, str):
            continue
        slug = slug_tag(name)
        if slug is None or slug.casefold() in seen:
            continue
        seen.add(slug.casefold())
        slugs.append(slug)
    return slugs
```

In `snapshot`, after the `folded` loop, insert the split:

```python
    tags = folded.pop("tags", None)
    if isinstance(tags, list) and tags:
        folded["zotero-tags"] = tags
        slugs = slug_tags(tags)
        if slugs:
            folded["tags"] = slugs
```

`research_vault/capture.py:582`: `_ITEM_FIELDS = (frozenset(literature_notes.SNAPSHOT_FIELDS) - {"zotero-tags"}) | {"collections"}`.

- [ ] **Step 4: The glossary and the skill**

`CONTEXT.md:57` and `research_vault/templates/context.md`'s **Snapshot** entry become:

```markdown
**Snapshot**: The fixed subset of the Zotero item's data fields a literature note carries verbatim under Zotero's base field names: a type-specific name (`proceedingsTitle`, `bookTitle`, `websiteTitle`, `repository`, `institution`, …) folds to its base field through Zotero's own schema, so the names and the mapping stay Zotero's. `extra` is carried whole; `zotero-tags` is Zotero's tag list exactly and `tags` a slugged copy Obsidian can read. A value with line breaks is carried as a list of its lines.
```

`skills/capture-source/SKILL.md:17`: the field list's `` `tags` `` stays (the `add` input), and the sentence after the list gains: ``` capture writes the item's tags twice: ``zotero-tags`` as Zotero holds them and ``tags`` slugged for Obsidian (``doi-fix:low-confidence`` becomes ``doi-fix-low-confidence``); type-specific field names fold to Zotero's base names in the note. ```

- [ ] **Step 5: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider`
Expected: PASS. `tests/test_literature_notes.py`'s key-order pins (`keys.index("generated") == len(keys) - 1`) still hold; a test that pins the full key list of a rendered note gains `zotero-tags`, `tags` where the item has tags.

- [ ] **Step 6: Form, commit, branch**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests && mdformat CONTEXT.md research_vault/templates/context.md skills/capture-source/SKILL.md
git switch -c substrate-b/tag-split
git commit -m "feat(capture): zotero-tags holds Zotero's list; tags is a slugged copy Obsidian reads (#195)" -- research_vault/literature_notes.py research_vault/capture.py CONTEXT.md research_vault/templates/context.md skills/capture-source/SKILL.md tests/test_literature_notes.py tests/test_capture.py
git push -u origin substrate-b/tag-split
```

After the merge: `gh issue close 195 --comment "Closed by Plan B Task 3: zotero-tags holds Zotero's tag list exactly; tags is a slugged copy (punctuation Obsidian rejects becomes -, / kept, duplicates removed ignoring case, empty and all-digit results dropped, Obsidian's character class copied literally). The Tags-view leg runs with Plan E's cold open."`

______________________________________________________________________

### Task 4: The `capture-monitor` check, with #205 (§5.3.1, §5.3.2, Q3)

**Files:**

- Modify: `research_vault/lints.py:698-875` (`_capture_monitor_outcomes` beside `_frontmatter_attestation_outcomes`, called from both pair loops), `research_vault/inbox.py:67-91`, `research_vault/verify.py:53-79`, `research_vault/capture.py:162-258,433-579` (the tag-only summary row)
- Modify: `docs/agents/terminology.md:137`, `skills/publish/SKILL.md:33`, `skills/project-flow/SKILL.md` (the acknowledgement paragraph names the monitor), `skills/capture-source/SKILL.md` (the outcome table gains the tags row)
- Test: `tests/test_lints.py`, `tests/test_capture.py`, `tests/test_verify_cli.py`
- Tracker: one new issue (the identity guard capture lacks)

**Interfaces:**

- Produces: check id `capture-monitor`, closing on commit and publish; `lints.MONITOR_CHECK`, `lints.MONITOR_EXEMPT = frozenset({"zotero-tags", "tags"})`, `lints._capture_monitor_outcomes(raw_path, base_data, candidate_data) -> list[Outcome]`; capture's `Outcome(..., extra={"tags-only": True})` on a note whose only moved fields are the tag fields, and one `UNMATCHED capture tags — drift — tags changed on: <notes>` row per run that saw any.

- Consumes: `lints._write_attested`, `_field`, `_frontmatter` (unchanged); Task 3's two tag fields.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_lints.py` (the helpers `_base_tree`, `_evidence_rows`, `_bump_generated`, `_refresh_body_witness` are at `:619-655`):

```python
def _recapture(path, **changes):
    """What a recapture that moved `changes` writes: the fields swapped, `generated`
    bumped under the machine actor, the witness refreshed."""
    text = path.read_text()
    for old, new in changes.items():
        text = must_replace(text, old, new)
    # The first recapture of a test moves the fixture stamp; a second one in the
    # same test finds it moved already and stays attested (generated differs
    # from HEAD's either way).
    if _FIXTURE_GENERATED in text:
        text = _bump_generated(text)
    path.write_text(text)
    _refresh_body_witness(path)


def _monitor_rows(vault, base):
    return [
        (item.target, item.reason)
        for item in lints.lint_evidence_layer(
            gitstate.snapshot_tree(vault, base), gitstate.snapshot_worktree(vault)
        )
        if item.check == "capture-monitor"
    ]


def test_monitor_reports_every_attested_snapshot_change_with_old_and_new(fixture_vault):
    """Designs test 1: a recapture that moved DOI, dropped the venue and added
    pages raises one monitor row per field, values JSON-encoded."""
    base = _base_tree(fixture_vault)
    note = fixture_vault / "literature" / "smith2020.md"
    _recapture(
        note,
        **{
            'DOI: "10.1000/xyz"': 'DOI: "10.1000/abc"\npages: "1-10"',
            'itemType: "journalArticle"': 'itemType: "conferencePaper"',
        },
    )
    assert _monitor_rows(fixture_vault, base) == [
        ("path-bytes:literature/smith2020.md", 'drift — DOI changed: "10.1000/xyz" → "10.1000/abc"'),
        ("path-bytes:literature/smith2020.md", 'drift — itemType changed: "journalArticle" → "conferencePaper"'),
        ("path-bytes:literature/smith2020.md", 'drift — pages added: "1-10"'),
    ]


def test_monitor_reasons_are_one_line_and_capped(fixture_vault):
    """Designs test 9: a multi-line abstract and a long value never reach
    append_entry as line breaks or a kilobyte."""
    base = _base_tree(fixture_vault)
    note = fixture_vault / "literature" / "smith2020.md"
    long_value = "x" * 500
    _recapture(note, **{'DOI: "10.1000/xyz"': f'DOI: "10.1000/xyz"\nabstractNote:\n  - "Line one"\n  - "{long_value}"'})
    ((_target, reason),) = _monitor_rows(fixture_vault, base)
    assert "\n" not in reason and "\r" not in reason
    assert reason.startswith("drift — abstractNote added: ")
    assert len(reason) < 200
    assert reason.endswith("…")


def test_monitor_is_silent_on_an_unattested_change(fixture_vault):
    """Designs test 10: a hand edit is evidence-layer's row, never a second
    row costing a second acknowledgement."""
    base = _base_tree(fixture_vault)
    note = fixture_vault / "literature" / "smith2020.md"
    note.write_text(must_replace(note.read_text(), 'DOI: "10.1000/xyz"', 'DOI: "10.1000/abc"'))
    assert _monitor_rows(fixture_vault, base) == []
    rows = _evidence_rows(fixture_vault, base)
    assert any(r.reason == "drift — DOI changed without writer attestation" for r in rows)


def test_monitor_exempts_both_tag_fields(fixture_vault):
    """Designs test 14: a tag-only recapture commits clean (ruling 3: the
    scanner's status tags move on every modify)."""
    base = _base_tree(fixture_vault)
    note = fixture_vault / "literature" / "smith2020.md"
    _recapture(note, **{'DOI: "10.1000/xyz"': 'DOI: "10.1000/xyz"\nzotero-tags:\n  - {tag: "#nosource"}\ntags:\n  - "nosource"'})
    assert _monitor_rows(fixture_vault, base) == []


def test_monitor_reports_an_attachment_that_left_and_a_swapped_md5(fixture_vault):
    """Designs test 13 (first half) and the [added] md5 row."""
    base = _base_tree(fixture_vault)
    note = fixture_vault / "literature" / "smith2020.md"
    _recapture(
        note,
        **{'md5: "aa11aa11aa11aa11aa11aa11aa11aa11"': 'md5: "bb22bb22bb22bb22bb22bb22bb22bb22"'},
    )
    assert _monitor_rows(fixture_vault, base) == [
        (
            "path-bytes:literature/smith2020.md",
            "drift — attachment ATT00001 md5 changed: aa11aa11aa11aa11aa11aa11aa11aa11 → bb22bb22bb22bb22bb22bb22bb22bb22",
        )
    ]
    _recapture(
        note,
        **{'  - {key: "ATT00001", version: 13, md5: "bb22bb22bb22bb22bb22bb22bb22bb22", contentType: "application/pdf", filename: "smith2020.pdf"}\n': ""},
    )
    assert ("path-bytes:literature/smith2020.md", "drift — attachment ATT00001 left the tuple") in _monitor_rows(fixture_vault, base)


def test_monitor_reports_a_changed_item_key_at_the_same_path(fixture_vault):
    """Designs test 13 (second half): capture has no identity guard, so a
    deleted item's note overwritten by a new item with the same key is a row."""
    base = _base_tree(fixture_vault)
    note = fixture_vault / "literature" / "smith2020.md"
    _recapture(note, **{'zotero-item-key: "SMITH020"': 'zotero-item-key: "OTHER001"'})
    assert ("path-bytes:literature/smith2020.md", "drift — zotero-item-key changed at the same path: SMITH020 → OTHER001") in _monitor_rows(fixture_vault, base)


def test_monitor_reports_an_older_render_restored(fixture_vault):
    """#205 (designs test 12): a `git checkout` of an earlier render carries a
    valid machine attestation; the version going backwards is the row."""
    base = _base_tree(fixture_vault)
    note = fixture_vault / "literature" / "smith2020.md"
    _recapture(note, **{"zotero-item-version: 12": "zotero-item-version: 11"})
    rows = _monitor_rows(fixture_vault, base)
    assert rows[0] == ("path-bytes:literature/smith2020.md", "drift — older render restored: version 11 < 12")


def test_monitor_tie_breaks_a_same_version_restore_on_generated_at(fixture_vault):
    base = _base_tree(fixture_vault)
    note = fixture_vault / "literature" / "smith2020.md"
    text = must_replace(note.read_text(), 'DOI: "10.1000/xyz"', 'DOI: "10.1000/old"')
    text = must_replace(text, 'at: "2026-08-16T09:00:00Z"', 'at: "2026-08-15T09:00:00Z"')
    note.write_text(text)
    _refresh_body_witness(note)
    rows = _monitor_rows(fixture_vault, base)
    assert (
        "path-bytes:literature/smith2020.md",
        "drift — older render restored: generated.at 2026-08-15T09:00:00Z < 2026-08-16T09:00:00Z",
    ) in rows  # beside the DOI row; _deduplicate sorts by reason


def test_monitor_runs_across_a_renamed_pair_too(fixture_vault):
    base = _base_tree(fixture_vault)
    source = fixture_vault / "literature" / "smith2020.md"
    renamed = fixture_vault / "literature" / "smith2020b.md"
    renamed.write_text(
        _bump_generated(
            must_replace(
                must_replace(source.read_text(), 'citationKey: "smith2020"', 'citationKey: "smith2020b"'),
                'DOI: "10.1000/xyz"',
                'DOI: "10.1000/abc"',
            )
        )
    )
    _refresh_body_witness(renamed)
    source.unlink()
    assert ("path-bytes:literature/smith2020b.md", 'drift — DOI changed: "10.1000/xyz" → "10.1000/abc"') in _monitor_rows(fixture_vault, base)
```

Append to `tests/test_verify_cli.py`:

```python
def test_capture_monitor_closes_commit_and_publish_and_its_ack_lapses_on_any_byte(net_vault):
    """Designs test 11: ack, recapture with no value moved (generated bumps),
    stage: the row is raised again with a new hash."""
    from tests.test_lints import _base_tree, _recapture

    from research_vault import inbox, verify

    assert "capture-monitor" in inbox.CHECK_IDS
    assert "capture-monitor" in verify.CLOSING_BY_SURFACE["commit"]
    assert "capture-monitor" in verify.CLOSING_BY_SURFACE["publish"]
    note = net_vault / "literature" / "smith2020.md"
    _recapture(note, **{'DOI: "10.1000/xyz"': 'DOI: "10.1000/abc"'})
    _report, effective, hashes, warning = verify.verify_state(net_vault, network=False)
    (row,) = [o for o in effective if o.check == "capture-monitor"]
    first_hash = hashes[id(row)]
    assert verify.surface_decision("commit", effective, warning)[0] == 1
    finding = next(f for f in inbox.open_entries(net_vault) if f.check == "capture-monitor")
    inbox.append_ack(net_vault, finding.id, "manual — accepted", "human:eran")
    _report, effective, _hashes, warning = verify.verify_state(net_vault, network=False)
    assert verify.surface_decision("commit", effective, warning)[0] == 0
    _recapture(note, **{'at: "2026-09-16T09:00:00Z"': 'at: "2026-09-17T09:00:00Z"'})
    _report, effective, hashes, warning = verify.verify_state(net_vault, network=False)
    (row,) = [o for o in effective if o.check == "capture-monitor"]
    assert hashes[id(row)] != first_hash
    assert verify.surface_decision("commit", effective, warning)[0] == 1
```

Append to `tests/test_capture.py`:

```python
def test_a_tag_only_recapture_files_one_summary_row_under_capture(tmp_vault, monkeypatch):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    capture.capture(tmp_vault, client, ["E352DFS8"])
    retagged = json.loads(json.dumps(ITEM))
    retagged["data"]["tags"] = [{"tag": "ai", "type": 1}, {"tag": "#nosource"}]
    fake = _canned_run(canned_item(FakeZotero(), item=retagged), items=(retagged,))
    client = _client(monkeypatch, fake)
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"])
    assert outcomes[0].extra.get("tags-only") is True
    summary = [o for o in outcomes if o.target == "tags"]
    assert [(o.check, o.result, o.reason) for o in summary] == [
        ("capture", Result.UNMATCHED, "drift — tags changed on: jakesch.etal2023a")
    ]
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_lints.py tests/test_verify_cli.py tests/test_capture.py -q -k "monitor or tag_only"`
Expected: FAIL — no `capture-monitor` rows; `capture-monitor` unregistered.

- [ ] **Step 3: The monitor**

In `research_vault/lints.py`, add `import json` to the imports and, after `_frontmatter_attestation_outcomes`:

```python
MONITOR_CHECK = "capture-monitor"
# Ruling 3: the declared add-ons move tags on every modify (Attachment
# Scanner's status tags, MarkDB-Connect's ObsCite); a hold on each would be an
# approval gate. Capture files one summary row per run instead (Q3).
MONITOR_EXEMPT = frozenset({"zotero-tags", "tags"})
_VALUE_CAP = 60


def _shown(value) -> str:
    """One line, ASCII, capped: `append_entry` refuses line breaks and the full
    values stay in `git diff` (designs cluster 1, [corrected])."""
    text = json.dumps(value, ensure_ascii=True, sort_keys=True)
    return text if len(text) <= _VALUE_CAP else text[: _VALUE_CAP - 1] + "…"


def _attachments_by_key(data: dict | None) -> dict[str, dict]:
    entries = data.get("attachments") if data is not None else None
    return {
        str(entry["key"]): entry
        for entry in (entries if isinstance(entries, list) else [])
        if isinstance(entry, dict) and "key" in entry
    }


def _restored_reason(base_data: dict, candidate_data: dict) -> str | None:
    """#205: the same item rendered at a lower version, or at the same version
    with an earlier `generated.at`, is an older render restored — a valid
    attestation on the way back in."""
    if _field(base_data, "zotero-item-key") != _field(candidate_data, "zotero-item-key"):
        return None
    old, new = _field(base_data, "zotero-item-version"), _field(candidate_data, "zotero-item-version")
    if isinstance(old, int) and isinstance(new, int):
        if new < old:
            return f"drift — older render restored: version {new} < {old}"
        if new == old:
            old_at = (base_data.get("generated") or {}).get("at")
            new_at = (candidate_data.get("generated") or {}).get("at")
            if (
                literature_notes._valid_generated(base_data.get("generated"))
                and literature_notes._valid_generated(candidate_data.get("generated"))
                and new_at < old_at
            ):
                return f"drift — older render restored: generated.at {new_at} < {old_at}"
    return None


def _capture_monitor_outcomes(raw_path, base_data, candidate_data) -> list[Outcome]:
    """Every attested change to a literature note's snapshot, attachments and
    identity (spec §5.3.1). Attested pairs only: an unattested change is
    already evidence-layer's row, and a second row would cost a second ack."""
    if base_data is None or candidate_data is None:
        return []
    if not _write_attested(base_data, candidate_data):
        return []
    target = RepoPath(raw_path)

    def row(reason: str) -> Outcome:
        return Outcome(MONITOR_CHECK, target, Result.UNMATCHED, reason)

    rows: list[Outcome] = []
    restored = _restored_reason(base_data, candidate_data)
    if restored is not None:
        rows.append(row(restored))
    for key in literature_notes.SNAPSHOT_FIELDS:
        if key in MONITOR_EXEMPT:
            continue
        old, new = _field(base_data, key), _field(candidate_data, key)
        if old == new:
            continue
        if old is None:
            rows.append(row(f"drift — {key} added: {_shown(new)}"))
        elif new is None:
            rows.append(row(f"drift — {key} removed: {_shown(old)}"))
        else:
            rows.append(row(f"drift — {key} changed: {_shown(old)} → {_shown(new)}"))
    old_attachments, new_attachments = _attachments_by_key(base_data), _attachments_by_key(candidate_data)
    for key in sorted(set(old_attachments) - set(new_attachments)):
        rows.append(row(f"drift — attachment {key} left the tuple"))
    for key in sorted(set(old_attachments) & set(new_attachments)):
        old_md5, new_md5 = old_attachments[key].get("md5"), new_attachments[key].get("md5")
        if old_md5 != new_md5:
            rows.append(row(f"drift — attachment {key} md5 changed: {old_md5} → {new_md5}"))
    for key in ("zotero-server-id", "zotero-item-key"):
        old, new = _field(base_data, key), _field(candidate_data, key)
        if old is not None and new is not None and old != new:
            rows.append(row(f"drift — {key} changed at the same path: {old} → {new}"))
    return rows
```

In `lint_evidence_layer`, after each `outcomes.extend(_frontmatter_attestation_outcomes(raw_path, base_data, candidate_data))` — in the renamed-pair branch (`:821-823`) and in the same-path loop (`:872-874`) — add `outcomes.extend(_capture_monitor_outcomes(raw_path, base_data, candidate_data))`. `_deduplicate` sorts by check, so the monitor rows come out grouped; the tests above compare lists in that order (the `_restored_reason` row sorts first only because `_deduplicate` orders by reason text: `drift — DOI…` < `drift — older…`; the #205 tests therefore assert `rows[0]` after sorting on a note where no other field moved).

- [ ] **Step 4: The registries and the tag-only row**

`research_vault/inbox.py` — `CHECK_IDS` gains, after `dead-link`:

```python
        # Every attested change to a literature note's snapshot (spec §5.3.1).
        "capture-monitor",
```

`research_vault/verify.py:53-79`: `"capture-monitor"` joins both the `commit` and `publish` sets. `docs/agents/terminology.md:137`: `` `capture-monitor` `` joins the check-ids row; `skills/publish/SKILL.md:33` gains it in the parenthesised list.

`research_vault/capture.py::_capture_one`: where the MATCHED row is appended after a write (`:235`), decide tags-only:

```python
        tags_only = existing is not None and _only_tags_moved(existing, candidate)
        outcomes.append(
            Outcome(CHECK, citation_key, Result.MATCHED, "matched", extra={"tags-only": True} if tags_only else {})
        )
```

with, in `capture.py`:

```python
def _only_tags_moved(existing: str, candidate: str) -> bool:
    """Whether a re-render moved nothing but the two tag fields (spec §5.3.1)."""
    before = dict(literature_notes._projection(frontmatter._mapping_items(frontmatter.parse(existing)[0])))
    after = dict(literature_notes._projection(frontmatter._mapping_items(frontmatter.parse(candidate)[0])))
    exempt = {"zotero-tags", "tags"}
    moved = {key for key in set(before) | set(after) if before.get(key) != after.get(key)}
    return bool(moved) and moved <= exempt and literature_notes.note_body(existing) == literature_notes.note_body(candidate)
```

and in `capture()` before the CSL step:

```python
    retagged = sorted(str(o.target) for o in outcomes if o.extra.get("tags-only"))
    if retagged:
        outcomes.append(
            Outcome(CHECK, "tags", Result.UNMATCHED, "drift — tags changed on: " + ", ".join(retagged))
        )
```

`_print_and_hold` files the UNMATCHED row under `capture`, which closes no surface. `skills/capture-source/SKILL.md`'s outcome table (`:34-45`) gains a row whose first cell is “`UNMATCHED tags — drift — tags changed on: …`” and whose second reads “A recapture moved only the tag fields of the named notes. One summary row per run, held under `capture`; it blocks nothing (ruling 3).” `skills/project-flow/SKILL.md`'s acknowledgement paragraph (`:84`) gains the sentence “A `capture-monitor` row names a snapshot value a Zotero add-on or a restore changed; read the old and new values in the row, confirm them in Zotero, and acknowledge only what the person accepts.”

- [ ] **Step 5: The identity-guard issue**

```bash
gh issue create --label bug --label ready-for-agent --title "capture has no identity guard: a new item with a deleted item's citation key overwrites that item's note" --body "$(cat <<'BODY'
Found by the lanes 2-3 spec (designs cluster 1, [added]): `capture._capture_one` (`capture.py:162-258`) and `literature_notes.render_note` (`:475-487`) compare the existing note's projection with the new render and write when they differ; nothing compares `zotero-item-key`. A deleted item's note is therefore overwritten by a new item that received the same citation key — an ADR 0003 breach (the record of what the first source said is gone).

Plan B Task 4's `capture-monitor` reports the key change at the same path (`drift — zotero-item-key changed at the same path`), so the overwrite is held at commit; it is not prevented. The fix is capture's: refuse to render over a note whose `zotero-item-key` differs, filing `not-admitted — note records item X, Zotero item is Y` and leaving the note as it stands.
BODY
)"
```

- [ ] **Step 6: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider && mypy`
Expected: PASS. `tests/test_skill_contracts.py` and `tests/test_config_validity.py:157` pass once the terminology row carries the id.

- [ ] **Step 7: Form, commit, branch, close #205**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests && mdformat docs/agents/terminology.md skills/publish/SKILL.md skills/project-flow/SKILL.md skills/capture-source/SKILL.md
git switch -c substrate-b/capture-monitor
git commit -m "feat(verify): capture-monitor — every attested snapshot, attachment and identity change is a row; an older render restored is one too (§5.3.1, #205)" -- research_vault/lints.py research_vault/inbox.py research_vault/verify.py research_vault/capture.py docs/agents/terminology.md skills/publish/SKILL.md skills/project-flow/SKILL.md skills/capture-source/SKILL.md tests/test_lints.py tests/test_verify_cli.py tests/test_capture.py
git push -u origin substrate-b/capture-monitor
```

After the merge: `gh issue close 205 --comment "Closed by Plan B Task 4: capture-monitor's own predicate reports an older render restored (version N < M, generated.at tie-break) under a valid attestation."`

______________________________________________________________________

### Task 5: A trashed attachment is drift, not a refusal (#189)

**Files:**

- Modify: `research_vault/lifecycle.py:86-91,98-105,111-143` (the trashed-attachment branch goes; `_drift_detail` names a trashed child), `research_vault/capture.py:84-112,127-135,162-184` (`read_item` and the tuple skip a child Zotero has trashed)
- Modify: `skills/capture-source/SKILL.md:42` (the merged|trashed|deleted row names the item only)
- Test: `tests/test_lifecycle.py:117-136`, `tests/test_capture.py`

**Interfaces:**

- Produces: `lifecycle.classify` never returns `("trashed", <attachment key>)`; a trashed child is `drifted` with `attachment K trashed` in its detail; `capture.read_item` excludes children whose `data.deleted` is truthy, so the next render drops the attachment from the tuple and the monitor files `attachment K left the tuple` (Task 4). Designs test 7's offline half is the lifecycle change; the live half is Task 10.

- [ ] **Step 1: Write the failing tests**

Replace `tests/test_lifecycle.py::test_a_trashed_attachment_outranks_a_re_key` (`:117-136`) with:

```python
def test_a_trashed_attachment_is_drift_on_its_note_not_a_trashed_note():
    """#189: `trashed` is the item's state. A trashed child moves the note to
    drift (its version moved into the trash map), and a re-key still wins."""
    top = {"ALKT2NF7": {"citationKey": "alkt2026", "replaces": set()}}
    prov = _prov(attachments=({"key": "ATT00001", "version": 4, "md5": "x", "contentType": "", "filename": ""},))
    assert lifecycle.classify(prov, _live({"ALKT2NF7": 0, "ATT00001": 5}, {"ATT00001": 5}, top)) == (
        "drifted",
        "attachment ATT00001 4 → 5",
    )
    assert lifecycle.classify(prov, _live({"ALKT2NF7": 0}, {"ATT00001": 5}, top)) == (
        "drifted",
        "attachment ATT00001 absent",
    )
    top["ALKT2NF7"]["citationKey"] = "alkt2026a"
    assert lifecycle.classify(prov, _live({"ALKT2NF7": 0}, {"ATT00001": 4}, top)) == (
        "re-keyed",
        "alkt2026 → alkt2026a",
    )


def test_drift_detail_names_a_trashed_child(tmp_vault, monkeypatch):
    fake = _drift_fake([{"key": "ATT00001", "data": {"md5": "aa11", "deleted": 1}}])
    assert _drift_reason(tmp_vault, monkeypatch, fake) == (
        "drift — attachment ATT00001 4 → 5; ATT00001: trashed"
    )
```

(Read `_drift_fake` and `_drift_reason` at `tests/test_lifecycle.py:340-375` before writing the second test; if `_drift_fake` cannot carry `deleted`, extend it.) Append to `tests/test_capture.py`:

```python
def test_capture_drops_a_trashed_child_from_the_tuple_and_the_text_layer(tmp_vault, monkeypatch):
    """#189: the children route lists a trashed attachment with `deleted: 1`;
    capture reads it as gone, so the tuple shrinks and the monitor reports the
    attachment leaving (designs test 7, offline half)."""
    trashed = json.loads(json.dumps(ATTACHMENT))
    trashed["data"]["deleted"] = 1
    fake = _canned_run(canned_item(FakeZotero(), children=(trashed, CHILD_NOTE)))
    client = _client(monkeypatch, fake)
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"])
    assert outcomes[0].result is Result.MATCHED
    data, body = frontmatter.parse((tmp_vault / "literature" / "jakesch.etal2023a.md").read_text())
    assert data["attachments"] == []
    assert not (tmp_vault / "fulltext" / "D7EJ9FTG.md").exists()
    assert "## Attachments" not in body
    assert outcomes[1].result is Result.SKIPPED  # no attachment left to read
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_lifecycle.py tests/test_capture.py -q -k "trashed"`
Expected: FAIL — `classify` returns `("trashed", "ATT00001")`; the tuple keeps the child.

- [ ] **Step 3: `lifecycle.py`**

Delete `lifecycle.py:86-91` (the comment and the `for attachment in provenance.attachments: … return "trashed", str(att_key)` loop). In `_drift_detail`, pass `live` through (`_drift_detail(client, vault, provenance, detail, live)` from `lint_lifecycle`) and extend the per-attachment note:

```python
        state = "trashed" if key in live.trash else ("file changed" if file_changed else "metadata only")
        notes_out.append(f"{key}: {state}" + (", cached text stale" if text_changed else ""))
```

Update the module docstring's `ORDER` comment and `lifecycle.py:1-7` to say a trashed attachment is drift on its note (#189), and the ingest spec's `:195` step 4 is amended in Task 11.

- [ ] **Step 4: `capture.py`**

In `read_item`, filter the children once:

```python
        children = [
            child
            for child in client.children(item_key)
            if not (isinstance(child.get("data"), Mapping) and child["data"].get("deleted"))
        ]
```

(`Mapping` is already imported.) `_capture_one`'s attachments tuple and `_write_texts` then see only live children. `skills/capture-source/SKILL.md:42`: the row's text becomes ``` The item left the library. Nothing was written; the note is kept. A trashed attachment is not this row: capture re-renders the note without it and the commit hook reports the attachment leaving the tuple (``capture-monitor``). ```

- [ ] **Step 5: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider`
Expected: PASS. `tests/test_lifecycle.py::test_trashed_and_deleted_from_the_sitting` and the fixture-driven transition tests concern the item key and still pass.

- [ ] **Step 6: Form, commit, branch, close #189**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests && mdformat skills/capture-source/SKILL.md
git switch -c substrate-b/trashed-attachment
git commit -m "fix(lifecycle): a trashed attachment is drift on its note, never a trashed note; capture drops a trashed child from the tuple (#189)" -- research_vault/lifecycle.py research_vault/capture.py skills/capture-source/SKILL.md tests/test_lifecycle.py tests/test_capture.py
git push -u origin substrate-b/trashed-attachment
```

After the merge: `gh issue close 189 --comment "Closed by Plan B Task 5: lifecycle.py's trashed-attachment branch is deleted; a trashed child is drift the capture monitor reports (attachment left the tuple), and capture reads a child with deleted: 1 as gone. The Attachment Scanner's declared settings land in Plan D now that a dropped child is a finding (spec §9 item 2)."`

______________________________________________________________________

### Task 6: A bibliography entry moves only with its note — `csl-sha256` (#196, Q20)

**Files:**

- Modify: `research_vault/literature_notes.py:53-63,75-86,452-463,524-550` (`csl_sha256` in the tuple), `research_vault/bibliography.py` (`entry_sha256`, `update`), `research_vault/capture.py:162-258,261-323,433-579` (export before render; `_update_csl`; `_regenerate_csl` and `_top_version` deleted), `research_vault/zotero.py:339-353` (`library_csl` deleted), `research_vault/captured.py:193-284` (`_structural` compares the hash)
- Modify: `skills/capture-source/SKILL.md:32`, `research_vault/templates/vault/AGENTS.md:32` unchanged, `CONTEXT.md:55` (the tuple entry)
- Test: `tests/test_capture.py` (the library-route tests are rewritten), `tests/test_captured.py`, `tests/test_bibliography.py`, `tests/test_zotero.py`, `tests/test_literature_notes.py`

**Interfaces:**

- Produces: `Provenance.csl_sha256: str | None = None`; `TUPLE_FIELDS` gains `csl-sha256` after `fulltext`; `bibliography.entry_sha256(entry: dict) -> str` (sha256 of `json.dumps(entry, sort_keys=True, ensure_ascii=False, separators=(",", ":"))`); `bibliography.update(vault_root, rendered: Mapping[str, dict], keep: Iterable[str]) -> Path` — the existing file's entries filtered to `keep`, overwritten by `rendered`, written sorted; capture exports one entry per rendered item before rendering (`client.export_csl([citation_key])`), carries its hash in the tuple, and calls `update` once at the end; `captured._structural` files `mismatch` when a note's `csl-sha256` differs from its entry's hash or the entry is missing.

- Consumes: Tasks 2–3's `render_note`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_bibliography.py`:

```python
def test_entry_sha256_is_the_canonical_json_hash():
    from research_vault import bibliography

    entry = {"id": "a", "title": "T", "author": [{"family": "S"}]}
    assert bibliography.entry_sha256(entry) == bibliography.entry_sha256({"title": "T", "author": [{"family": "S"}], "id": "a"})
    assert bibliography.entry_sha256(entry) != bibliography.entry_sha256({**entry, "title": "U"})


def test_update_replaces_rendered_entries_keeps_the_rest_and_drops_uncaptured_keys(tmp_vault):
    from research_vault import bibliography

    bibliography.write(tmp_vault, [{"id": "a", "title": "A"}, {"id": "b", "title": "B"}, {"id": "gone", "title": "G"}])
    bibliography.update(tmp_vault, {"a": {"id": "a", "title": "A2"}}, keep={"a", "b"})
    assert bibliography.load(tmp_vault) == {"a": {"id": "a", "title": "A2"}, "b": {"id": "b", "title": "B"}}
```

In `tests/test_capture.py`, delete `test_csl_file_falls_back_to_item_export_when_the_library_route_breaks`, `test_library_route_is_reread_once_when_zotero_moved_during_the_run`, `test_a_database_change_during_the_csl_read_voids_the_run_not_the_file`, `test_a_refused_item_export_is_unmatched_not_an_outage`, `test_a_trashed_refusal_does_not_skip_its_key_from_csl_regeneration`, `test_csl_regeneration_needs_no_library_name_when_nothing_was_read`, `test_a_mid_run_move_stops_reading_and_never_reads_the_csl_library`, `test_the_library_route_is_read_once_when_zotero_did_not_move`, `test_an_item_without_a_library_envelope_falls_back_to_item_export` and `test_a_csl_schema_violation_is_an_unmatched_row_on_the_csl_file`; remove the `/better-bibtex/library?/My%20Library.json` line from `_canned_run` and register the export instead: `fake.rpc("item.export", lambda params: [e for e in LIBRARY if e["id"] in params[0]])`. Add:

```python
def test_capture_exports_each_rendered_items_entry_before_rendering_and_records_its_hash(tmp_vault, monkeypatch):
    """#196 / Q20: the note carries csl-sha256 of its own entry; the file holds
    exactly the rendered entries plus the untouched ones."""
    from research_vault import bibliography

    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    bibliography.write(tmp_vault, [{"id": "other2020", "title": "untouched"}])
    (tmp_vault / "literature" / "other2020.md").write_text(
        '---\ntype: "literature"\nzotero-server-id: "6LpvURP2E933"\nzotero-item-key: "OTHER001"\n'
        'zotero-item-version: 1\ncitationKey: "other2020"\nattachments:\nfulltext:\n---\n'
    )
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"])
    assert [(o.target, o.result, o.reason) for o in outcomes] == [
        ("jakesch.etal2023a", Result.MATCHED, "matched"),
        ("system/bibliography.json", Result.MATCHED, "matched"),
    ]
    export_calls = [c for c in fake.calls if c[0] == "RPC" and c[1] == "item.export"]
    assert export_calls == [("RPC", "item.export", {"params": [["jakesch.etal2023a"], "Better CSL JSON"]})]
    first_render = fake.calls.index(next(c for c in fake.calls if c[1].endswith("/items/E352DFS8?format=json")))
    assert fake.calls.index(export_calls[0]) > first_render  # read first, then export, then render
    data, _ = frontmatter.parse((tmp_vault / "literature" / "jakesch.etal2023a.md").read_text())
    entries = bibliography.load(tmp_vault)
    assert data["csl-sha256"] == bibliography.entry_sha256(entries["jakesch.etal2023a"])
    assert entries["other2020"] == {"id": "other2020", "title": "untouched"}


def test_an_export_that_returns_no_entry_for_the_key_is_unmatched_and_writes_no_note(tmp_vault, monkeypatch):
    fake = _canned_run(canned_item(FakeZotero()))
    fake.rpc("item.export", lambda params: [])
    client = _client(monkeypatch, fake)
    outcomes = capture.capture(tmp_vault, client, ["E352DFS8"])
    assert (outcomes[0].result, outcomes[0].reason) == (
        Result.UNMATCHED,
        "mismatch — item.export returned no entry for jakesch.etal2023a",
    )
    assert not (tmp_vault / "literature" / "jakesch.etal2023a.md").exists()


def test_a_refused_export_is_unmatched_and_an_outage_is_unreachable(tmp_vault, monkeypatch):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)

    def refusing(method, params, *, timeout=None):
        raise zotero.ZoteroError("JSON-RPC error: unknown key", zotero.Result.UNMATCHED)

    monkeypatch.setattr(client, "_rpc", refusing)
    assert capture.capture(tmp_vault, client, ["E352DFS8"])[0].result is Result.UNMATCHED

    def down(method, params, *, timeout=None):
        raise zotero.ZoteroError("Zotero unreachable")

    monkeypatch.setattr(client, "_rpc", down)
    assert capture.capture(tmp_vault, client, ["E352DFS8"])[0].result is Result.UNREACHABLE


def test_noop_includes_the_csl_hash(tmp_vault, monkeypatch):
    fake = _canned_run(canned_item(FakeZotero()))
    client = _client(monkeypatch, fake)
    capture.capture(tmp_vault, client, ["E352DFS8"])
    assert capture.capture(tmp_vault, client, ["E352DFS8"])[0].reason == "matched — NOOP"
    fake.rpc("item.export", lambda params: [{**LIBRARY[0], "title": "T2"}])
    assert capture.capture(tmp_vault, client, ["E352DFS8"])[0].reason == "matched"
```

Append to `tests/test_captured.py`:

```python
def test_a_csl_entry_that_does_not_match_its_notes_hash_is_a_mismatch_row(tmp_vault):
    """Designs test 15, Q20's exact backstop: a hand-edited entry, a note
    reverted without its entry, or an entry that moved alone."""
    import json

    from research_vault import bibliography

    _note(tmp_vault, "smith2020", "SMITH001")
    entry = {"id": "smith2020", "title": "Right"}
    bibliography.write(tmp_vault, [entry])
    note = tmp_vault / "literature" / "smith2020.md"
    note.write_text(note.read_text().replace("fulltext:\n", f'fulltext:\ncsl-sha256: "{bibliography.entry_sha256(entry)}"\n'))
    assert [o for o in captured.lint_captured_set(tmp_vault) if o.result is Result.UNMATCHED] == []
    bibliography.write(tmp_vault, [{"id": "smith2020", "title": "Wrong"}])
    rows = [o for o in captured.lint_captured_set(tmp_vault) if o.result is Result.UNMATCHED]
    assert [(o.check, decode_repo_path(o.target), o.reason) for o in rows] == [
        ("captured-set", b"literature/smith2020.md", "mismatch — csl-sha256 of literature/smith2020.md does not match its system/bibliography.json entry")
    ]
    bibliography.write(tmp_vault, [])
    rows = [o for o in captured.lint_captured_set(tmp_vault) if o.result is Result.UNMATCHED]
    assert rows[0].reason == "mismatch — literature/smith2020.md records csl-sha256 but system/bibliography.json has no entry for smith2020"
```

In `tests/test_zotero.py`, delete the `library_csl` tests. In `tests/test_literature_notes.py`, the tuple-order pin (`:452-460`) gains `csl-sha256` after `fulltext` when `PROVENANCE` carries one; add `csl_sha256="c" * 64` to the fixture `Provenance` and assert `data["csl-sha256"] == "c" * 64`.

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_bibliography.py tests/test_capture.py tests/test_captured.py -q -k "entry_sha256 or update_replaces or exports_each or no_entry or refused_export or noop_includes or csl_entry"`
Expected: FAIL — `entry_sha256`, `update` missing; capture still reads the library route.

- [ ] **Step 3: `bibliography.py` and the tuple**

Append to `research_vault/bibliography.py`:

```python
def entry_sha256(entry: dict) -> str:
    """The hash a literature note records of its own CSL entry (#196): canonical
    JSON, sorted keys, no whitespace, so the same entry hashes the same whatever
    Better BibTeX's key order was."""
    canonical = json.dumps(entry, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def update(vault_root, rendered, keep) -> Path:
    """Replace the rendered items' entries, keep every other captured key's
    entry as it stands, drop the rest (a merged-away or re-keyed key), write
    whole. An unreadable or invalid existing file raises `BibliographyError`
    rather than being overwritten from a partial read."""
    existing = load(vault_root)
    wanted = set(keep)
    merged = {key: entry for key, entry in existing.items() if key in wanted}
    merged.update(rendered)
    return write(vault_root, list(merged.values()))
```

with `import hashlib` and `from collections.abc import Iterable, Mapping` as needed. `research_vault/literature_notes.py`: `Provenance` gains `csl_sha256: str | None = None` as its last field; `TUPLE_FIELDS` gains `"csl-sha256"` after `"fulltext"`; `_tuple_fields` appends `("csl-sha256", provenance.csl_sha256)` after `fulltext` when it is set; `read_provenance` passes `csl_sha256=data.get("csl-sha256") or None`. Every `Provenance(...)` positional construction in tests keeps working because the new field has a default.

- [ ] **Step 4: Capture exports before it renders**

In `research_vault/capture.py`, add:

```python
def _export_entry(client: ZoteroClient, citation_key: str) -> dict:
    """One `item.export` for one key, before the render (Q20): the entry the
    note will hash. No entry for the key is a mismatch, never an outage."""
    exported = client.export_csl([citation_key])
    for entry in exported:
        if entry.get("id") == citation_key:
            return entry
    raise ZoteroError(f"item.export returned no entry for {citation_key}", result=Result.UNMATCHED)
```

In `capture()`'s loop, after `read = _read_keyed(...)` returned a keyed read and before `_capture_one`:

```python
            citation_key = read.item["data"]["citationKey"]
            try:
                entry = _export_entry(client, citation_key)
            except ZoteroError as error:
                if "returned no entry" in str(error):
                    outcomes.append(Outcome(CHECK, requested_key, Result.UNMATCHED, f"mismatch — {error}"))
                else:
                    outcomes.append(lifecycle.blocked(CHECK, requested_key, error))
                continue
            rendered_entries[citation_key] = entry
            outcomes.extend(_capture_one(vault, read, server_id, now, base_fields, entry))
```

`_capture_one(..., entry)` sets `csl_sha256=bibliography.entry_sha256(entry)` on the `Provenance` it builds; because the hash is a tuple field, `render_note`'s `_projection` sees it and a changed entry breaks NOOP. Replace the CSL tail of `capture()` (`:573-578`) with:

```python
    if rendered_entries or existing:
        try:
            bibliography.update(vault, rendered_entries, keep=_captured_keys(vault))
        except bibliography.BibliographyError as error:
            outcomes.append(Outcome(CHECK, CSL_TARGET, Result.UNMATCHED, f"schema-violation — {error}"))
        else:
            outcomes.append(Outcome(CHECK, CSL_TARGET, Result.MATCHED, "matched"))
    return outcomes
```

Delete `_regenerate_csl`, `_top_version`, `run_version`, `library_name` and the `re_keyed` skip set (a re-keyed key simply falls out of `keep`); `rendered_entries: dict[str, dict] = {}` is initialised before the loop. Delete `ZoteroClient.library_csl` (`zotero.py:339-353`) and its import of `urllib.parse` if nothing else uses it. `skills/capture-source/SKILL.md:32`: replace “regenerates `system/bibliography.json` whole” with “exports each rendered item's CSL entry before rendering, records its hash in the note (`csl-sha256`), and rewrites the entries of the items it rendered in `system/bibliography.json` — an entry moves only with its note”. `CONTEXT.md:55`: the tuple list gains “`csl-sha256` (the hash of the note's own CSL entry)” after `fulltext`.

- [ ] **Step 5: `captured._structural` compares**

In `research_vault/captured.py::_structural`, after the ledger block (or before it, when the ledger is absent — the comparison must run either way, so restructure `_structural` so the ledger-missing early return only skips the ledger half), add:

```python
    try:
        entries = bibliography.load(vault)
    except bibliography.BibliographyError:
        entries = None  # the citation-key check files the file's own row
    if entries is not None:
        for relative, provenance in _notes_with_paths(vault):
            if provenance.csl_sha256 is None:
                continue
            entry = entries.get(provenance.citation_key)
            if entry is None:
                reason = (
                    f"mismatch — {relative} records csl-sha256 but {bibliography.BIB_PATH} "
                    f"has no entry for {provenance.citation_key}"
                )
            elif bibliography.entry_sha256(entry) != provenance.csl_sha256:
                reason = f"mismatch — csl-sha256 of {relative} does not match its {bibliography.BIB_PATH} entry"
            else:
                continue
            outcomes.append(Outcome(CHECK, RepoPath(os.fsencode(relative)), Result.UNMATCHED, reason))
```

where `_notes_with_paths(vault)` is `_read_notes` extended to yield `(relative, provenance)` (add the path to the tuple `_read_notes` builds and adapt `_notes`, `captured_set`, `literature_paths`). `captured.py` imports `bibliography` (no cycle: `bibliography` imports only `Result`).

- [ ] **Step 6: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider && mypy`
Expected: PASS. Every remaining capture test that asserted `("system/bibliography.json", MATCHED, "matched")` still does; `test_capture_writes_note_text_layer_and_csl_file` reads `[0]["id"]` from a file that now holds the exported entry.

- [ ] **Step 7: Form, commit, branch, close #196**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests && mdformat skills/capture-source/SKILL.md CONTEXT.md
git switch -c substrate-b/csl-sha256
git commit -m "feat(capture): export each item's CSL entry before rendering, record csl-sha256 in the tuple, rewrite only the rendered entries; captured-set compares the hash (#196)" -- research_vault/literature_notes.py research_vault/bibliography.py research_vault/capture.py research_vault/zotero.py research_vault/captured.py skills/capture-source/SKILL.md CONTEXT.md tests/test_capture.py tests/test_captured.py tests/test_bibliography.py tests/test_zotero.py tests/test_literature_notes.py
git push -u origin substrate-b/csl-sha256
```

After the merge: `gh issue close 196 --comment "Closed by Plan B Task 6: capture exports one CSL entry per rendered item before rendering, records csl-sha256 in the tuple and rewrites only those entries; the whole-library route is gone; captured-set compares every note's hash with its entry exactly."`

______________________________________________________________________

### Task 7: The verifier's lists are append-only (#206)

**Files:**

- Modify: `research_vault/lints.py` (`_verifier_list_outcomes`, called in both pair loops), `research_vault/verify.py:261-314` (`_snapshot_path_hash` hashes the lists for these rows)
- Test: `tests/test_lints.py`, `tests/test_verify_cli.py`

**Interfaces:**

- Produces: `lints._verifier_list_outcomes(raw_path, base_data, candidate_data) -> list[Outcome]` — check `evidence-layer`, `extra={"hash_basis": "verifier-lists"}`, reasons `drift — verified event removed: <check>@<at> by <by>` and `drift — failed-verification row for <check> removed without a passing event`; `verify._verifier_lists_bytes(image) -> bytes` and the `hash_basis` branch in `_snapshot_path_hash`.

- Consumes: `events._verified_events`, `events._failure_rows`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_lints.py`:

```python
def _with_lists(path, verified, failures):
    text = path.read_text()
    block = ""
    if verified:
        block += "verified:\n" + "".join(f'  - {{by: "{e[0]}", at: "{e[1]}", check: "{e[2]}"}}\n' for e in verified)
    if failures:
        block += "failed-verification:\n" + "".join(f'  - {{check: "{f[0]}", result: "{f[1]}"}}\n' for f in failures)
    path.write_text(must_replace(text, "accessed:", block + "accessed:"))


def _list_rows(vault, base):
    return [
        (item.reason, item.extra.get("hash_basis"))
        for item in lints.lint_evidence_layer(
            gitstate.snapshot_tree(vault, base), gitstate.snapshot_worktree(vault)
        )
        if item.check == "evidence-layer" and "verif" in item.reason
    ]


def test_removing_a_verified_event_is_drift(fixture_vault):
    note = fixture_vault / "literature" / "smith2020.md"
    _with_lists(note, [("research_vault/0.1.0", "2026-09-01", "update-notice")], [])
    subprocess.run(["git", "commit", "-qam", "events"], cwd=fixture_vault, check=True)
    base = _base_tree(fixture_vault)
    _with_lists(note, [], [])
    note.write_text(must_replace(note.read_text(), 'verified:\n  - {by: "research_vault/0.1.0", at: "2026-09-01", check: "update-notice"}\n', ""))
    assert _list_rows(fixture_vault, base) == [
        ("drift — verified event removed: update-notice@2026-09-01 by research_vault/0.1.0", "verifier-lists")
    ]


def test_a_failure_row_may_change_result_or_be_added_but_not_vanish(fixture_vault):
    note = fixture_vault / "literature" / "smith2020.md"
    _with_lists(note, [], [("update-notice", "UNMATCHED")])
    subprocess.run(["git", "commit", "-qam", "failure"], cwd=fixture_vault, check=True)
    base = _base_tree(fixture_vault)
    note.write_text(must_replace(note.read_text(), 'result: "UNMATCHED"', 'result: "UNREACHABLE"'))
    assert _list_rows(fixture_vault, base) == []
    note.write_text(must_replace(note.read_text(), 'failed-verification:\n  - {check: "update-notice", result: "UNREACHABLE"}\n', ""))
    assert _list_rows(fixture_vault, base) == [
        ("drift — failed-verification row for update-notice removed without a passing event", "verifier-lists")
    ]


def test_a_failure_row_removed_by_a_passing_event_in_the_same_diff_is_legal(fixture_vault):
    note = fixture_vault / "literature" / "smith2020.md"
    _with_lists(note, [], [("update-notice", "UNMATCHED")])
    subprocess.run(["git", "commit", "-qam", "failure"], cwd=fixture_vault, check=True)
    base = _base_tree(fixture_vault)
    note.write_text(
        must_replace(
            note.read_text(),
            'failed-verification:\n  - {check: "update-notice", result: "UNMATCHED"}\n',
            'verified:\n  - {by: "research_vault/0.1.0", at: "2026-09-02", check: "update-notice"}\n',
        )
    )
    assert _list_rows(fixture_vault, base) == []
```

Append to `tests/test_verify_cli.py`:

```python
def test_a_verifier_list_row_is_acknowledged_on_the_lists_not_the_note(net_vault):
    """Designs test 16: an ack on 'verified deleted' must not cover every later
    well-formed list edit, because canonical_content excludes the lists."""
    from tests.test_lints import _with_lists

    from research_vault import inbox, verify

    note = net_vault / "literature" / "smith2020.md"
    _with_lists(note, [], [("update-notice", "UNMATCHED")])
    subprocess.run(["git", "commit", "-qam", "failure"], cwd=net_vault, check=True)
    note.write_text(note.read_text().replace('failed-verification:\n  - {check: "update-notice", result: "UNMATCHED"}\n', ""))
    _report, effective, hashes, warning = verify.verify_state(net_vault, network=False)
    (row,) = [o for o in effective if "removed without a passing event" in o.reason]
    first_hash = hashes[id(row)]
    finding = next(f for f in inbox.open_entries(net_vault) if f.target_hash == first_hash)
    inbox.append_ack(net_vault, finding.id, "manual — accepted", "human:eran")
    _report, effective, _hashes, warning = verify.verify_state(net_vault, network=False)
    assert not [o for o in effective if "removed without a passing event" in o.reason]
    _with_lists(note, [("human:eran", "2026-09-03", "quote:smith2020#^c-11111111:managed-region")], [])
    _report, effective, hashes, warning = verify.verify_state(net_vault, network=False)
    (row,) = [o for o in effective if "removed without a passing event" in o.reason]
    assert hashes[id(row)] != first_hash
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_lints.py tests/test_verify_cli.py -q -k "verified_event or failure_row or verifier_list"`
Expected: FAIL — no rows.

- [ ] **Step 3: The lint and the hash basis**

Append to `research_vault/lints.py`:

```python
VERIFIER_LISTS = "verifier-lists"


def _events_of(data: dict | None) -> list[tuple[str, str, str]]:
    from . import events  # noqa: PLC0415

    parsed, malformed = events._verified_events(data or {})
    if malformed:
        return []
    return [(str(e.get("by")), str(e.get("at")), str(e.get("check", ""))) for e in parsed]


def _failures_of(data: dict | None) -> dict[str, str]:
    from . import events  # noqa: PLC0415

    rows, malformed = events._failure_rows(data or {})
    return {} if malformed else {row["check"]: row["result"] for row in rows}


def _verifier_list_outcomes(raw_path, base_data, candidate_data) -> list[Outcome]:
    """#206: `verified` events are append-only; a failure row may be added or
    change its result, and may vanish only when the same diff appends a
    passing event for its check. These rows hash on the lists themselves
    (`hash_basis`), because the note's canonical bytes exclude the lists."""
    if base_data is None or candidate_data is None:
        return []
    rows: list[Outcome] = []
    extra = {"hash_basis": VERIFIER_LISTS}
    before, after = _events_of(base_data), _events_of(candidate_data)
    remaining = list(after)
    for event in before:
        if event in remaining:
            remaining.remove(event)
        else:
            by, at, check = event
            rows.append(
                Outcome(
                    "evidence-layer",
                    RepoPath(raw_path),
                    Result.UNMATCHED,
                    f"drift — verified event removed: {check}@{at} by {by}",
                    extra=extra,
                )
            )
    passed = {check for _by, _at, check in after} - {check for _by, _at, check in before}
    for check in sorted(set(_failures_of(base_data)) - set(_failures_of(candidate_data))):
        if check in passed:
            continue
        rows.append(
            Outcome(
                "evidence-layer",
                RepoPath(raw_path),
                Result.UNMATCHED,
                f"drift — failed-verification row for {check} removed without a passing event",
                extra=extra,
            )
        )
    return rows
```

Call it beside `_capture_monitor_outcomes` in both pair loops of `lint_evidence_layer` (it does not test attestation: the lists are verify's, so a capture that carries them forward unchanged raises nothing and a capture that drops one raises). In `research_vault/verify.py`, add:

```python
def _verifier_lists_bytes(image) -> bytes:
    """#206's ack basis: the two verifier-owned lists as canonical JSON."""
    data: dict = {}
    if image is not None and image.kind == "file":
        try:
            data, _ = frontmatter.parse((image.data or b"").decode(errors="surrogateescape"))
        except frontmatter.FrontmatterError:
            data = {}
    return json.dumps(
        {"verified": data.get("verified"), "failed-verification": data.get("failed-verification")},
        sort_keys=True,
        default=str,
    ).encode("utf-8")
```

and in `_snapshot_path_hash`, before the `append-only` branch:

```python
    if outcome.extra.get("hash_basis") == lints.VERIFIER_LISTS:
        data = _verifier_lists_bytes(candidate_image)
    elif outcome.check == "append-only":
```

- [ ] **Step 4: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider && mypy`
Expected: PASS.

- [ ] **Step 5: Form, commit, branch, close #206**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests
git switch -c substrate-b/verifier-lists
git commit -m "fix(verify): verified events are append-only and a failure row vanishes only with a passing event; the rows hash on the lists (#206)" -- research_vault/lints.py research_vault/verify.py tests/test_lints.py tests/test_verify_cli.py
git push -u origin substrate-b/verifier-lists
```

After the merge: `gh issue close 206 --comment "Closed by Plan B Task 7: removing a verified event, or a failed-verification row without a passing event for its check in the same diff, is an evidence-layer row hashed on the lists themselves, so an ack never covers a later list edit."`

______________________________________________________________________

### Task 8: A merge becomes a propagation (#183, §5.3.6)

**Files:**

- Modify: `research_vault/lifecycle.py:72-85` (the `merged` reason names the successor's citation key), `research_vault/propagate.py:41-47,78-91,145-243,245-253,271-281,307-376` (`merges` in the plan, the delete-or-rename apply), `research_vault/lints.py:727-875` (`lint_evidence_layer` reads the propagation records for merge losers), `docs/adr/0003-deprecate-never-delete.md` (a dated scope note), `CONTEXT.md:51` (**Standing**), `skills/capture-source/SKILL.md:52-62`
- Test: `tests/test_lifecycle.py:138-148`, `tests/test_propagate.py`, `tests/test_lints.py`

**Interfaces:**

- Produces: `lifecycle.classify` returns `("merged", "<successor item key> (<successor citation key>)")` and the reason reads `merged — into <item key> (<citation key>)`; `propagate.Plan.merges: dict[str, str]` (loser's citation key → successor's item key), carried in the plan document and the applied record as `"merges"`; `propagate.plan` maps a merged loser to the survivor's citation key, verifies the mapping against the *survivor's* item, and allows an existing `literature/<survivor>.md` for a merge; `propagate.apply` deletes the loser's note when the survivor has one, renames it otherwise, rewrites surfaces and recaptures the survivor; `lints._merged_losers(candidate_snapshot) -> set[bytes]` suppresses the deletion row for a loser the records name.

- Consumes: Task 4's monitor (the survivor's recapture is attested as any recapture is).

- [ ] **Step 1: Write the failing tests**

In `tests/test_lifecycle.py::test_merged_outranks_trashed_and_deleted` (`:138-148`), the expected tuple becomes `("merged", "NEW00001 (new2026)")` once the fixture's `top` carries `{"NEW00001": {"citationKey": "new2026", "replaces": {"ALKT2NF7"}}}` (read the test and give the successor a key). Append to `tests/test_propagate.py`:

```python
def _merge_fake(monkeypatch, *, survivor_has_note):
    """old2020 (E352DFS8) was merged into NEW00001, whose key is new2020."""
    fake = FakeZotero(server_id="S")
    survivor = {**ITEM, "key": "NEW00001", "data": {**ITEM["data"], "key": "NEW00001", "citationKey": "new2020", "relations": {"dc:replaces": ["http://zotero.org/users/0/items/E352DFS8"]}}}
    canned_item(fake, item=survivor)
    fake.get("/api/users/0/items?since=0&format=versions", body={"NEW00001": 600, "D7EJ9FTG": 551, "N0TE0001": 552}, headers={"Last-Modified-Version": "600"})
    fake.get("/api/users/0/items/trash?format=versions", body={"E352DFS8": 545})
    fake.get("/api/users/0/items/top?format=json", body=[survivor], headers={"Last-Modified-Version": "600"})
    fake.rpc("item.export", lambda params: [{"id": "new2020", "title": "T"}])
    return fake.install(zotero.ZoteroClient(), monkeypatch)


def test_plan_maps_a_merged_loser_to_the_survivor_through_its_item(tmp_vault, monkeypatch):
    _seed(tmp_vault)
    client = _merge_fake(monkeypatch, survivor_has_note=False)
    planned, outcomes = propagate.plan(tmp_vault, client, None)
    assert planned is not None, outcomes
    assert planned.mapping == {"old2020": "new2020"}
    assert planned.merges == {"old2020": "NEW00001"}
    assert planned.item_keys == {"old2020": "NEW00001"}
    assert propagate.read_plan(propagate.write_plan(tmp_vault, planned)).merges == {"old2020": "NEW00001"}


def test_apply_renames_the_loser_when_the_survivor_has_no_note(tmp_vault, monkeypatch):
    _seed(tmp_vault)
    client = _merge_fake(monkeypatch, survivor_has_note=False)
    planned, path, sha = _planned(tmp_vault, client, mapping=None)
    outcomes = propagate.apply(tmp_vault, client, path, sha)
    assert all(o.result is Result.MATCHED for o in outcomes), outcomes
    assert not (tmp_vault / "literature" / "old2020.md").exists()
    note = tmp_vault / "literature" / "new2020.md"
    assert note.is_file()
    assert 'zotero-item-key: "NEW00001"' in note.read_text()  # re-rendered from the survivor
    assert "[[new2020]]" in (tmp_vault / "wiki" / "sources" / "A.md").read_text()


def test_apply_deletes_the_loser_when_the_survivor_already_has_a_note(tmp_vault, monkeypatch):
    """§5.3.6: the loser's note is wholly machine-written and the merge moved
    its Zotero child notes onto the survivor; nothing person-written is lost.
    ADR 0003's scope note of 2026-10-24 covers this one deletion."""
    _seed(tmp_vault)
    (tmp_vault / "literature" / "new2020.md").write_text(_note("NEW00001", "new2020"))
    client = _merge_fake(monkeypatch, survivor_has_note=True)
    planned, path, sha = _planned(tmp_vault, client, mapping=None)
    assert planned.merges == {"old2020": "NEW00001"}
    outcomes = propagate.apply(tmp_vault, client, path, sha)
    assert all(o.result is Result.MATCHED for o in outcomes), outcomes
    assert not (tmp_vault / "literature" / "old2020.md").exists()
    assert (tmp_vault / "literature" / "new2020.md").is_file()
    record = json.loads(next((tmp_vault / "system" / "propagations").glob("*.json")).read_text())
    assert record["merges"] == {"old2020": "NEW00001"}


def test_a_plain_re_key_still_refuses_an_existing_target(tmp_vault, monkeypatch):
    """The exists-check is bypassed for merges only."""
    _seed(tmp_vault)
    (tmp_vault / "literature" / "new2020.md").write_text(_note("OTHER001", "new2020"))
    client = _zotero(monkeypatch)
    planned, outcomes = propagate.plan(tmp_vault, client, {"old2020": "new2020"})
    assert planned is None
    assert "already exists" in outcomes[0].reason
```

Append to `tests/test_lints.py`:

```python
def test_a_merge_losers_deletion_is_attested_by_the_propagation_record(fixture_vault):
    """#183: the record under system/propagations/ names the loser, so the
    deletion is a transition with a record (ADR 0003 scope note), not drift."""
    base = _base_tree(fixture_vault)
    record = fixture_vault / "system" / "propagations" / "propagate-20261024T100000Z.json"
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(json.dumps({
        "schema": "research-vault.propagation.v1",
        "operation_id": "propagate-20261024T100000Z",
        "date": "2026-10-24",
        "mapping": {"gone2019": "smith2020"},
        "item_keys": {"gone2019": "SMITH020"},
        "merges": {"gone2019": "SMITH020"},
        "surfaces": [],
        "applied_at": "2026-10-24T10:00:00",
        "approved_plan_sha256": "0" * 64,
    }))
    (fixture_vault / "literature" / "gone2019.md").unlink()
    rows = _evidence_rows(fixture_vault, base)
    assert not any(r.reason == "drift — literature note deleted" and "gone2019" in str(r.target) for r in rows), rows
    (fixture_vault / "literature" / "smith2020.md").unlink()
    rows = _evidence_rows(fixture_vault, base)
    assert any(r.reason == "drift — literature note deleted" and "smith2020" in str(r.target) for r in rows)
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_lifecycle.py tests/test_propagate.py tests/test_lints.py -q -k "merge or loser or re_key_still"`
Expected: FAIL — `Plan` has no `merges`; the plan refuses the existing target; the deletion row is raised.

- [ ] **Step 3: `lifecycle.py`**

`lifecycle.py:72-85`: `_successor` returns `(key, entry)`; `classify` returns `("merged", f"{successor_key} ({entry.get('citationKey') or '?'})")`. `lint_lifecycle`'s reason is then `merged — NEW00001 (new2020)`; the `_REFUSED` set in capture matches on the code only.

- [ ] **Step 4: `propagate.py`**

`Plan` gains `merges: dict[str, str]` after `item_keys` (every constructor passes `{}` for a re-key). `_mapping_from_linter` returns `(mapping, merges, blocking)`:

```python
_MERGED = re.compile(r"^merged — (?P<item>[A-Z0-9]{8}) \((?P<key>[^)]+)\)$")


def _mapping_from_linter(vault, client):
    mapping: dict[str, str] = {}
    merges: dict[str, str] = {}
    blocking: list[Outcome] = []
    for outcome in lifecycle.lint_lifecycle(vault, client):
        if outcome.result is Result.UNREACHABLE or (outcome.target == "vault" and outcome.result is Result.UNMATCHED):
            blocking.append(outcome)
        elif outcome.result is Result.UNMATCHED and outcome.reason.startswith("re-keyed — "):
            old, new = outcome.reason[len("re-keyed — ") :].split(" → ", 1)
            mapping[old] = new
        elif outcome.result is Result.UNMATCHED and (match := _MERGED.match(outcome.reason)):
            if match.group("key") != "?":
                mapping[str(outcome.target)] = match.group("key")
                merges[str(outcome.target)] = match.group("item")
    return mapping, merges, blocking
```

`plan(vault_root, client, mapping, *, merges=None, now=None)`: when `mapping is None`, take all three from the linter; for each `old`: `item_key = merges.get(old, provenance.item_key)`; the exists-check (`:184-195`) applies only when `old not in merges`; the live read verifies `client.item(item_key)["data"]["citationKey"] == new`; `item_keys[old] = item_key`. `_document` adds `"merges": dict(plan.merges)`; `read_plan` reads `dict(data.get("merges", {}))`; `plan_sha256` covers it through `_document`. In `apply`: `current, outcomes = plan(vault, client, approved.mapping, merges=approved.merges, now=now)`; the rename loop becomes:

```python
        if source.name != target.name:
            if old in approved.merges and (target.exists() or target.is_symlink()):
                # §5.3.6: the survivor already has a note; the loser's is wholly
                # machine-written and its Zotero child notes moved with the merge.
                # ADR 0003's scope note of 2026-10-24 covers this deletion; the
                # applied plan under system/propagations/ is its record.
                source.unlink()
            else:
                source.rename(target)
```

- [ ] **Step 5: The evidence-layer lint reads the records**

In `research_vault/lints.py`, add:

```python
def _merged_losers(snapshot: gitstate.Snapshot) -> set[str]:
    """Citation keys the applied propagation records name as merge losers (#183)."""
    losers: set[str] = set()
    for raw_path, image in snapshot.images.items():
        if not raw_path.startswith(b"system/propagations/") or not raw_path.endswith(b".json") or image.kind != "file":
            continue
        try:
            document = json.loads((image.data or b"").decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            continue  # lint_propagation reports an unreadable record
        merges = document.get("merges") if isinstance(document, dict) else None
        if isinstance(merges, dict):
            losers.update(str(key) for key in merges)
    return losers
```

and in `lint_evidence_layer`, where the deletion rows are built (`:852-860`):

```python
    losers = _merged_losers(candidate_snapshot)
    for raw_path in sorted(unpaired_removed):
        base_data = _frontmatter(base_files[raw_path])
        if base_data is not None and str(base_data.get("citationKey")) in losers:
            continue  # a merge the applied plan records (#183, ADR 0003 scope note)
        outcomes.append(Outcome("evidence-layer", RepoPath(raw_path), Result.UNMATCHED, "drift — literature note deleted"))
```

- [ ] **Step 6: The ADR scope note, the glossary, the skill**

Append to `docs/adr/0003-deprecate-never-delete.md`, after the **Scope bound** paragraph:

```markdown
**Scope note, 2026-10-24 (lanes 2–3 spec §5.3.6).** A Zotero merge is a recorded transition whose record is Zotero's own `dc:replaces` relation and the applied propagation plan under `system/propagations/`. When the survivor already has a literature note, the loser's note is removed by `propagate apply` under that plan: the note is wholly machine-written, the merge moved the loser's Zotero child notes onto the survivor, and the survivor's note is re-rendered in the same act, so nothing a person wrote is lost and what the loser's note said remains in history and in the plan. This is the one deletion a verb performs; `trashed` and `deleted` items keep their notes as before. Verified events and acknowledgments keyed on the loser's address are #146's open question.
```

`CONTEXT.md:51` (**Standing**): replace “A transition never deletes a note; it files a finding.” with “A transition files a finding and keeps the note — except a merge whose survivor already has a note, where the applied propagation plan removes the loser's (spec §5.3.6, ADR 0003's 2026-10-24 scope note).” `skills/capture-source/SKILL.md:52-62`: the propagate section gains the sentence “A `merged` finding is propagated the same way: the plan maps the loser's key to the survivor's, renames the loser's note when the survivor has none and removes it when the survivor already has one, then re-captures the survivor.”

- [ ] **Step 7: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider && mypy`
Expected: PASS. `tests/test_propagate.py`'s existing plan tests pass `mapping=` explicitly and never see a merge.

- [ ] **Step 8: Form, commit, branch, close #183**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests && mdformat docs/adr/0003-deprecate-never-delete.md CONTEXT.md skills/capture-source/SKILL.md
git switch -c substrate-b/merge-propagation
git commit -m "feat(propagate): a merge is a propagation — the loser's key maps to the survivor's, its note is renamed or removed under the plan, the survivor is recaptured (#183)" -- research_vault/lifecycle.py research_vault/propagate.py research_vault/lints.py docs/adr/0003-deprecate-never-delete.md CONTEXT.md skills/capture-source/SKILL.md tests/test_lifecycle.py tests/test_propagate.py tests/test_lints.py
git push -u origin substrate-b/merge-propagation
```

After the merge: `gh issue close 183 --comment "Closed by Plan B Task 8: lifecycle's merged reason names the survivor's citation key; propagate plans loser → survivor under its existing plan, approval and residue machinery, renames the note when the survivor has none and removes it when it does (ADR 0003 scope note 2026-10-24), and recaptures the survivor. Records keyed on the old address stay with #146."` Also comment on #146: `gh issue comment 146 --body "Plan B Task 8 (lanes 2-3 spec §5.3.6) lands merges as propagations; verified events and acknowledgments keyed on a merged-away note's address remain this issue's question."`

______________________________________________________________________

### Task 9: Publish re-checks every commit since the last publication; annotated tags; CI (§5.3.1, Q2)

**Files:**

- Modify: `research_vault/gitstate.py` (`commit_parents`), `research_vault/verify.py` (`_history_outcomes`, `verify_state(..., recheck_commits)`, `_plan_state` hashes), `research_vault/publish.py:362-415,398-402` (`_publish` passes the last publication; `_create_tag` annotates), `hooks/stop_publish_gate.py:63-74` (`_verify_publish` passes the same), `research_vault/scaffold.py:125-157` (`push.followTags`), `research_vault/__main__.py` (`verify --recheck-commits`), `research_vault/templates/ci/verify.yml:48`
- Modify: `skills/publish/SKILL.md` (the gate paragraph), `docs/agents/testing.md` (one paragraph on the re-check)
- Test: `tests/test_gitstate.py`, `tests/test_verify_cli.py`, `tests/test_publish.py`, `tests/test_scaffold.py`, `tests/test_templates.py:289-326`, `tests/test_ci_templates.py:17`

**Interfaces:**

- Produces: `gitstate.commit_parents(vault_root, base_ref: str | None) -> list[tuple[str, list[str]]]` — `(commit, parents)` oldest first for `git rev-list --reverse --parents HEAD --not <base>` (every commit when `base_ref` is None); `verify.HISTORY_CHECKS = ("evidence-layer", "append-only", "claim-immutability")` plus Plan C's `compiled-layer`; `verify._history_outcomes(repository, base_ref) -> list[tuple[Outcome, Snapshot, Snapshot]]` — the two-version lints per commit, merge rows kept only when raised against every parent (`--diff-merges=combined`'s reading), each outcome's `extra` carrying `{"commit": sha}`; `verify_state(..., recheck_commits: str | None | object = None)` with the sentinel `verify.WHOLE_HISTORY`; the CLI flag `verify --recheck-commits BASE` (`BASE` a ref, or `--recheck-commits all`); `publish.last_publication(vault) -> str | None`; annotated publication tags; `push.followTags=true` in a scaffolded vault.

- Consumes: Tasks 4 and 7's lints (they run per commit through `lint_evidence_layer`).

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_verify_cli.py`:

```python
def _commit_all(vault, message, *, no_verify=True):
    subprocess.run(["git", "add", "-A"], cwd=vault, check=True)
    args = ["git", "commit", "-qm", message]
    if no_verify:
        args.append("--no-verify")
    subprocess.run(args, cwd=vault, check=True)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=vault, check=True, capture_output=True, text=True).stdout.strip()


def test_recheck_commits_raises_the_row_a_bypassed_commit_hid(net_vault):
    """Q2: a `--no-verify` commit moves the base and the worktree diff is
    empty; the per-commit re-check still finds the hand edit."""
    from research_vault import verify

    base = _commit_all(net_vault, "base")
    note = net_vault / "literature" / "smith2020.md"
    note.write_text(must_replace(note.read_text(), 'DOI: "10.1000/xyz"', 'DOI: "10.1000/abc"'))
    _commit_all(net_vault, "hand edit, bypassed")
    _report, effective, hashes, warning = verify.verify_state(net_vault, network=False)
    assert not [o for o in effective if o.check == "evidence-layer"]
    _report, effective, hashes, warning = verify.verify_state(net_vault, network=False, recheck_commits=base)
    (row,) = [o for o in effective if o.check == "evidence-layer" and "DOI" in o.reason]
    assert row.reason == "drift — DOI changed without writer attestation"
    assert len(row.extra["commit"]) == 40
    assert verify.surface_decision("publish", effective, warning)[0] == 1
    assert verify.surface_decision("commit", effective, warning)[0] == 1


def test_recheck_commits_rows_can_be_acknowledged_and_stay_acknowledged(net_vault):
    from research_vault import inbox, verify

    base = _commit_all(net_vault, "base")
    note = net_vault / "literature" / "smith2020.md"
    note.write_text(must_replace(note.read_text(), 'DOI: "10.1000/xyz"', 'DOI: "10.1000/abc"'))
    _commit_all(net_vault, "bypassed")
    verify.verify_state(net_vault, network=False, recheck_commits=base)
    finding = next(f for f in inbox.open_entries(net_vault) if f.check == "evidence-layer" and "DOI" in f.reason)
    inbox.append_ack(net_vault, finding.id, "manual — accepted", "human:eran")
    _commit_all(net_vault, "ack")
    _report, effective, _hashes, warning = verify.verify_state(net_vault, network=False, recheck_commits=base)
    assert verify.surface_decision("publish", effective, warning)[0] == 0


def test_recheck_commits_reads_a_merge_against_every_parent(net_vault):
    """Q2 [corrected]: a merge whose resolution hand-edits a note the side
    branch added looks `added` against the first parent; combined, it is a row."""
    from research_vault import verify

    base = _commit_all(net_vault, "base")
    subprocess.run(["git", "switch", "-qc", "side"], cwd=net_vault, check=True)
    added = net_vault / "literature" / "added.md"
    added.write_text((net_vault / "literature" / "smith2020.md").read_text().replace('citationKey: "smith2020"', 'citationKey: "added"'))
    _commit_all(net_vault, "side adds a note")
    subprocess.run(["git", "switch", "-q", "-"], cwd=net_vault, check=True)
    (net_vault / "projects" / "brief" / "notes.md").write_text('---\ntype: "note"\n---\nmain moves on\n')
    _commit_all(net_vault, "main moves on")
    subprocess.run(["git", "merge", "--no-ff", "--no-commit", "-q", "side"], cwd=net_vault, check=True)
    added.write_text(must_replace(added.read_text(), 'DOI: "10.1000/xyz"', 'DOI: "10.1000/evil"'))
    _commit_all(net_vault, "merge with a hand edit")
    _report, effective, _hashes, _warning = verify.verify_state(net_vault, network=False, recheck_commits=base)
    rows = [o for o in effective if o.check == "evidence-layer" and "added.md" in str(o.target)]
    assert any("DOI changed without writer attestation" in o.reason for o in rows), rows


def test_cli_recheck_commits_flag(net_vault, monkeypatch, capsys):
    import research_vault.__main__ as cli

    seen = {}

    def state(vault, **kwargs):
        seen.update(kwargs)
        return {"outcomes": [], "counts": {}}, [], {}, {}

    monkeypatch.setattr(cli, "verify_state", state)
    assert cli.main(["verify", "--vault", str(net_vault), "--offline", "--recheck-commits", "abc123"]) == 0
    assert seen["recheck_commits"] == "abc123"
    assert cli.main(["verify", "--vault", str(net_vault), "--offline", "--recheck-commits", "all"]) == 0
    assert seen["recheck_commits"] is cli.WHOLE_HISTORY
```

Append to `tests/test_gitstate.py`:

```python
def test_commit_parents_lists_oldest_first_with_parents(tmp_vault):
    import subprocess

    from research_vault import gitstate

    def commit(msg):
        subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", msg], cwd=tmp_vault, check=True)
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_vault, check=True, capture_output=True, text=True).stdout.strip()

    first = commit("one")
    second = commit("two")
    assert gitstate.commit_parents(tmp_vault, first) == [(second, [first])]
    everything = gitstate.commit_parents(tmp_vault, None)
    assert everything[-1] == (second, [first])
    assert everything[0][1] == []  # the root commit has no parent
    empty_tree = subprocess.run(["git", "hash-object", "-w", "-t", "tree", "/dev/null"], cwd=tmp_vault, check=True, capture_output=True, text=True).stdout.strip()
    assert gitstate.commit_parents(tmp_vault, empty_tree) == everything  # CI's first-push base
```

Append to `tests/test_publish.py`:

```python
def test_publish_recheck_blocks_on_a_bypassed_hand_edit_since_the_last_publication(green_vault, monkeypatch):
    from research_vault import publish

    _tag_clock(monkeypatch, "090000", "100000")
    first = publish.mark_published(green_vault, "brief")
    assert first.decision == 0
    note = green_vault / "literature" / "x.md"
    note.write_text('---\ntype: "literature"\nmanaged-sha256: "' + "0" * 64 + '"\n---\n')
    subprocess.run(["git", "add", "-A"], cwd=green_vault, check=True)
    subprocess.run(["git", "commit", "-qm", "bypassed", "--no-verify"], cwd=green_vault, check=True)
    note.unlink()
    subprocess.run(["git", "add", "-A"], cwd=green_vault, check=True)
    subprocess.run(["git", "commit", "-qm", "and gone", "--no-verify"], cwd=green_vault, check=True)
    (green_vault / "projects" / "brief" / "draft.md").write_text(
        (green_vault / "projects" / "brief" / "draft.md").read_text().replace('status: "published"', 'status: "draft"')
    )
    subprocess.run(["git", "add", "-A"], cwd=green_vault, check=True)
    subprocess.run(["git", "commit", "-qm", "back to draft", "--no-verify"], cwd=green_vault, check=True)
    second = publish.mark_corrected(green_vault, "brief")
    assert second.decision == 1
    assert any("evidence-layer" in b and "literature/x.md" in b for b in second.blockers), second.blockers


def test_publication_tags_are_annotated_and_last_publication_is_the_newest(green_vault, monkeypatch):
    from research_vault import publish

    assert publish.last_publication(green_vault) is None
    _tag_clock(monkeypatch, "090000")
    publish.mark_published(green_vault, "brief")
    (tag,) = _tags(green_vault)
    kind = _git(green_vault, "cat-file", "-t", tag)
    assert kind == "tag"  # annotated: an object of its own, which push.followTags pushes
    assert publish.last_publication(green_vault) == tag
```

Append to `tests/test_scaffold.py`:

```python
def test_scaffold_sets_push_follow_tags(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    value = subprocess.run(["git", "config", "--get", "push.followTags"], cwd=tmp_path, capture_output=True, text=True, check=True).stdout.strip()
    assert value == "true"
```

`tests/test_templates.py:289-326` and `tests/test_ci_templates.py:17`: the verify line's pin becomes `'--git-base "$BASE" --git-candidate HEAD --recheck-commits "$BASE"'`.

- [ ] **Step 2: Run the tests to see them fail**

Run: `python -m pytest tests/test_verify_cli.py tests/test_gitstate.py tests/test_publish.py tests/test_scaffold.py tests/test_templates.py tests/test_ci_templates.py -q -k "recheck or commit_parents or annotated or follow_tags or verify_workflow or ci"`
Expected: FAIL — no `recheck_commits`, no `commit_parents`, lightweight tags, no config.

- [ ] **Step 3: `gitstate.commit_parents`**

Append to `research_vault/gitstate.py`:

```python
def commit_parents(vault_root: Path, base_ref: str | None) -> list[tuple[str, list[str]]]:
    """``(commit, parents)`` oldest first for every commit reachable from HEAD
    and not from ``base_ref`` (every commit when ``base_ref`` is None)."""
    args = ["rev-list", "--reverse", "--parents", "HEAD"]
    if base_ref is not None:
        # CI's first-push base is the empty tree's oid, not a commit; `--not`
        # on a tree fails. A base that is no commit means "every commit".
        resolved = _git(Path(vault_root), "rev-parse", "--verify", "-q", f"{base_ref}^{{commit}}", check=False)
        if resolved.returncode == 0:
            args.extend(["--not", base_ref])
    result = _git(Path(vault_root), *args)
    rows: list[tuple[str, list[str]]] = []
    for line in result.stdout.decode("ascii").split("\n"):
        if not line:
            continue
        commit, *parents = line.split()
        rows.append((commit, parents))
    return rows
```

- [ ] **Step 4: The history re-check in `verify.py`**

Add near the closing sets:

```python
# The two-version checks publish and CI replay per commit (spec §5.3.1, Q2):
# every lint that compares a base and a candidate snapshot. Plan C adds
# `compiled-layer`.
WHOLE_HISTORY = object()


def _history_lints(repository: Path, base_snapshot, candidate_snapshot) -> list:
    return [
        *lints.lint_evidence_layer(base_snapshot, candidate_snapshot),
        *lints.lint_append_only(repository, base_snapshot, candidate_snapshot),
        *lints.lint_claim_immutability(repository, base_snapshot, candidate_snapshot),
    ]


def _history_outcomes(repository: Path, base_ref):
    """Per-commit rows since ``base_ref``: a merge's row counts only when it is
    raised against every parent (`--diff-merges=combined`'s reading), so a
    side branch's own commits are checked once and a conflict resolution that
    hand-edits a note the branch added is still caught (Q2 [corrected])."""
    rows = []
    empty = gitstate.snapshot_tree(repository, gitstate._empty_tree(repository))
    for commit, parents in gitstate.commit_parents(repository, None if base_ref is WHOLE_HISTORY else base_ref):
        candidate = gitstate.snapshot_tree(repository, commit)
        per_parent = []
        for parent in parents or [None]:
            base = gitstate.snapshot_tree(repository, parent) if parent else empty
            per_parent.append({(o.check, o.target, o.reason): (o, base) for o in _history_lints(repository, base, candidate) if o.result is Result.UNMATCHED})
        if not per_parent:
            continue
        common = set(per_parent[0]).intersection(*(set(p) for p in per_parent[1:]))
        for key in sorted(common):
            outcome, base = per_parent[0][key]
            stamped = checks.Outcome(outcome.check, outcome.target if outcome.target_kind == "identifier" else RepoPath(decode_repo_path(outcome.target)), outcome.result, outcome.reason, extra={**outcome.extra, "commit": commit})
            rows.append((stamped, base, candidate))
    return rows
```

`_plan_state(..., recheck_commits=None)` computes, after the worktree lints:

```python
    history = _history_outcomes(repository, recheck_commits) if recheck_commits is not None else []
    raw.extend(outcome for outcome, _base, _candidate in history)
    …
    hashes = {id(outcome): _target_hash(vault, outcome, bibliography_universe, base_snapshot=base_snapshot, candidate_snapshot=candidate_snapshot) for outcome in authoritative if id(outcome) not in history_ids}
    hashes.update({id(outcome): _target_hash(vault, outcome, bibliography_universe, base_snapshot=base, candidate_snapshot=candidate) for outcome, base, candidate in history})
```

(`history_ids = {id(o) for o, _b, _c in history}`.) `verify_state` gains `recheck_commits=None` and forwards it. A history row's `extra["commit"]` is a plain string, so `_file_effects`' key (check, target, kind, result, hash, …) dedupes a row re-raised on the next run.

- [ ] **Step 5: The CLI, publish, scaffold, CI**

`research_vault/__main__.py`: `verify.add_argument("--recheck-commits", metavar="BASE", help="also re-check every commit reachable from HEAD and not from BASE; 'all' is the whole history")`; `cmd_verify` passes `recheck_commits=(WHOLE_HISTORY if args.recheck_commits == "all" else args.recheck_commits)`; import `WHOLE_HISTORY` from `.verify`.

`research_vault/publish.py`:

```python
def last_publication(vault) -> str | None:
    """The newest `published/*` tag of any project, by the date-time its name carries."""
    listed = _git(vault, "tag", "--list", "published/*")
    if listed.returncode != 0:
        raise PublishError("cannot list published tags")
    tags = [tag for tag in listed.stdout.split() if PUBLISHED_TAG.match(tag)]
    return max(tags) if tags else None
```

In `_publish`, the gate run becomes `verify_state(root, network=True, base=base, recheck_commits=last_publication(root) or WHOLE_HISTORY)` (import `WHOLE_HISTORY` from `.verify`). `hooks/stop_publish_gate.py::_verify_publish` passes the same `recheck_commits=publish.last_publication(vault) or WHOLE_HISTORY` (importing both lazily as it imports `verify_state`), so the Stop gate holds on what publish holds on; a test in `tests/test_hooks.py` monkeypatches `verify_state`, invokes `_verify_publish` on a vault with one published tag, and asserts the kwarg names that tag. `_create_tag`:

```python
def _create_tag(vault, tag: str, commit: str) -> None:
    # Annotated (an object of its own): `push.followTags` pushes it, so a fresh
    # clone's publish re-check starts at the last publication, not at the root.
    if _git(vault, "tag", "-a", "-m", f"research-vault publication {tag}", tag, commit).returncode != 0:
        raise PublishError(f"cannot create tag {tag}")
```

`research_vault/scaffold.py::_prepare_repository` ends with `_git(vault, "config", "push.followTags", "true")`. `research_vault/templates/ci/verify.yml:48`: `python -m research_vault verify --vault . --offline --surface commit --git-base "$BASE" --git-candidate HEAD --recheck-commits "$BASE"` (when `$BASE` is the empty tree, `commit_parents` reads a non-commit base as the whole history, which is what a first push should get). `skills/publish/SKILL.md`'s "Run the gate" paragraph gains the sentence “The gate also re-checks every commit since the last publication: a hand edit committed with `--no-verify`, or under a hook that could not import research_vault, is found there and holds publish like any other row.” `docs/agents/testing.md` gains a short paragraph under a new heading `## The publish re-check` naming `verify --recheck-commits BASE` and the measured cost (Q2: 0.98 s for 304 commits at the three checks).

- [ ] **Step 6: Run the suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -n auto -p no:cacheprovider && mypy && yamlfix research_vault/templates/ci/verify.yml`
Expected: PASS. `tests/test_publish.py`'s existing tag tests read `git tag --list`, which lists annotated tags the same way.

- [ ] **Step 7: Form, commit, branch**

```bash
ruff check --fix research_vault tests && ruff format research_vault tests && mdformat skills/publish/SKILL.md docs/agents/testing.md
git switch -c substrate-b/publish-recheck
git commit -m "feat(verify): publish and CI re-check every commit since the last publication, merges against every parent; annotated tags; push.followTags (§5.3.1, Q2)" -- research_vault/gitstate.py research_vault/verify.py research_vault/publish.py research_vault/scaffold.py research_vault/__main__.py research_vault/templates/ci/verify.yml skills/publish/SKILL.md docs/agents/testing.md tests/test_gitstate.py tests/test_verify_cli.py tests/test_publish.py tests/test_scaffold.py tests/test_templates.py tests/test_ci_templates.py
git push -u origin substrate-b/publish-recheck
```

______________________________________________________________________

### Task 10: The live legs on the test Zotero (§8)

Attended. Every leg runs against the unsynced test instance (`python -m research_vault probe --base http://localhost:23129` names it) and never production. If the instance is down, record that in the task report and leave the gated issues open (#180 is the precedent).

**Files:**

- Modify: `tests/test_capture_live.py` (two legs), the task report

- Tracker: #185 and #188 close here; #187 gains a comment

- [ ] **Step 1: Native identifiers per item type (#185, designs test 7)**

Add to `tests/test_capture_live.py`, marked `live` and `live_write`:

```python
@pytest.mark.live
@pytest.mark.live_write
@pytest.mark.parametrize("item_type", ["journalArticle", "conferencePaper", "book", "preprint", "report"])
def test_zotero_accepts_pmid_and_pmcid_per_item_type(tmp_vault, item_type):
    base = os.environ["RV_LIVE_WRITE_BASE"]
    assert not is_production_base(base)
    client = zotero.ZoteroClient(base=base, api_key=os.environ.get("RV_LIVE_WRITE_KEY") or None)
    stamp = time.strftime("%Y%m%d%H%M%S")
    outcomes = capture.add(
        tmp_vault,
        client,
        [{"itemType": item_type, "title": f"research-vault #185 {item_type} {stamp}", "PMID": "28503678", "PMCID": "PMC5428074"}],
    )
    # Record the answer per type in the task report: MATCHED (accepted, and the
    # note carries both fields) or UNMATCHED mismatch (Zotero refused the field
    # for this type). Either is a fact §3.1's PMCID fetcher row depends on.
    assert outcomes[0].result in {Result.MATCHED, Result.UNMATCHED}, outcomes
    if outcomes[0].result is Result.MATCHED:
        note = next((tmp_vault / "literature").glob("*.md"))
        data, _ = frontmatter.parse(note.read_text())
        assert data.get("PMID") == "28503678"
```

Run with `RV_LIVE=1 RV_LIVE_WRITE_BASE=http://localhost:23129 python -m pytest tests/test_capture_live.py -q -k pmid`. Trash the created items afterwards through the client (`client.trash_item`) as the existing write leg does.

- [ ] **Step 2: The fold against the real schema (#188)**

```python
@pytest.mark.live
def test_the_local_api_serves_the_schema_and_a_conference_paper_folds(tmp_vault):
    client = zotero.ZoteroClient(base=READ_BASE)
    folded = literature_notes.base_field_map(client.schema())
    assert folded["conferencePaper"]["proceedingsTitle"] == "publicationTitle"
    assert folded["bookSection"]["bookTitle"] == "publicationTitle"
    items, _ = client.top_items()
    paper = next((i for i in items if i["data"].get("itemType") == "conferencePaper" and i["data"].get("citationKey")), None)
    if paper is None:
        pytest.skip("no conference paper on this instance")
    outcomes = capture.capture(tmp_vault, client, [paper["data"]["citationKey"]])
    assert outcomes[0].result is Result.MATCHED
    data, _ = frontmatter.parse((tmp_vault / "literature" / f"{paper['data']['citationKey']}.md").read_text())
    assert "proceedingsTitle" not in data
```

Run with `RV_LIVE=1 python -m pytest tests/test_capture_live.py -q -k schema`.

- [ ] **Step 3: A trashed attachment after #189 (designs test 7; Attachment Scanner's automatic trash)**

On the test instance: install Attachment Scanner 0.5.1 with the settings Plan D declares (`monitor_attachments=true`, `scan_duplicates=false`, `remove_snapshot=true`, `remove_pubmed_entry=true`), capture an item that has a PDF and a snapshot child, modify the item in Zotero (a tag), wait for the notifier, run `capture <key>` again and `verify --offline --surface commit`. Expected: `capture` is `MATCHED` (not a `trashed` refusal), the note's tuple no longer lists the snapshot, and the monitor files `drift — attachment <key> left the tuple`. Record the date, the add-on version, the child's key and the row. If the children route does not mark the trashed child (`deleted: 1`) and the tuple still lists it, Task 5's filter is wrong: report it as a deviation and file an issue.

- [ ] **Step 4: arXiv Workflow's merge leg, then `propagate` (#187's route)**

On the test instance, with arXiv Workflow 0.3.9 installed at `merge.arXivExtra=true`, `features.arXivUpdate=false`, `merge.trashUnannotatedPDF=false`: capture a preprint, run the add-on's merge against its published version, then `python -m research_vault propagate --vault <scratch> --base http://localhost:23129` and apply the plan. Expected: the plan maps the loser to the survivor with `merges` set; apply renames or removes the loser's note and recaptures the survivor; `verify --offline --surface commit` passes. Comment on #187 with the result (`gh issue comment 187 --body …`): the row stays optional and becomes recommended in Plan D only if this leg passed.

- [ ] **Step 5: Close #185 and #188 on the recorded legs**

```bash
gh issue close 185 --comment "Closed by Plan B Tasks 1 and 10: the snapshot carries Zotero 10's native PMID and PMCID; the live leg on the test instance recorded which item types accept them (see the task report of 2026-…). Whether a clean Retraction Watch lookup by PMID counts as verification stays open here as the spec's §10 says."
gh issue close 188 --comment "Closed by Plan B Tasks 2 and 10: type-specific fields fold to Zotero's base names through /api/schema (measured live on the test instance); capture refuses when the schema cannot be read."
```

If a leg could not run, do not close its issue; comment with what was attempted and why it stopped.

______________________________________________________________________

### Task 11: The records, the review, the baseline

**Files:**

- Modify: `docs/superpowers/specs/2026-09-06-import-redesign-design.md:133,137,195`, `docs/superpowers/specs/2026-09-05-assembly-design.md` (§15 items 03 and 05), `docs/superpowers/specs/2026-10-03-substrate-components-design.md` (§7 names the ids this plan registered under `evidence-layer` and `capture`), `mutation-baseline.txt`

- [ ] **Step 1: The ingest spec's three amendments**

`:133` — replace “so no field is renamed and no mapping is ours. `tags` is in that list for a specific reason:” with “under Zotero's **base** field names: a type-specific name (`proceedingsTitle`, `bookTitle`, `websiteTitle`, `repository`, `institution`, …) folds to its base field through Zotero's own schema (`/api/schema`), so the names and the mapping stay Zotero's and a change of item type is not a removed field (*amended 2026-10-24, lanes 2–3 spec §5.3.4, #188*). `PMID` and `PMCID` join the list as Zotero 10's native fields (#185). Tags are carried twice: `zotero-tags` is Zotero's list exactly and `tags` a slugged copy Obsidian reads (*amended 2026-10-24, §5.3.4, #195*). `tags` was in that list for a specific reason:”.

`:137` — append to the paragraph: `*Amended 2026-10-24 (lanes 2–3 spec, decision 02): assembly decision 28 stands — annotation handling is lane 4's, and this paragraph's claim to supersede it is withdrawn.*`

`:195` — in step 4, replace `trashed (any key in the trash set)` with `trashed (the item key in the trash set; *amended 2026-10-24, lanes 2–3 spec §5.3.5, #189*: a trashed attachment is drift on its note, reported by the capture monitor when the next render drops it, never a trashed note)`.

- [ ] **Step 2: The assembly spec's §15 marks**

Item 03 (the Zoplicate merge path): append “**Closed 2026-10-24 by the lanes 2–3 spec §5.3.6 (#183): a merge is a propagation; the loser's key maps to the survivor's.**” Item 05 (what the PMCID fetcher writes): append “**Answered 2026-10-24 by screen A row 5: Extra lines, and tags only with `pmcid.tags`, which the spec declares false.**”

- [ ] **Step 3: Review, baseline, verification**

As Plan A Task 11: run the gate over this plan's modules and triage survivors (never accept one in `_capture_monitor_outcomes`, `_restored_reason`, `_verifier_list_outcomes`, `_history_outcomes` or `slug_tag` without a stated reason); run the whole-plan review; file what it will not fix. Check the designs' sixteen acceptance tests against the suite: 1 (Task 4), 2–6 and 8 (Tasks 4–7's tests as named), 7 (Tasks 5 and 10), 9–14 (Task 4), 15 (Task 6), 16 (Task 7). Verify the issue states:

```bash
for n in 183 185 188 189 195 196 205 206; do gh issue view $n --json state --jq ".state"; done
```

- [ ] **Step 4: Commit the records**

```bash
mdformat docs/superpowers/specs/2026-09-06-import-redesign-design.md docs/superpowers/specs/2026-09-05-assembly-design.md docs/superpowers/specs/2026-10-03-substrate-components-design.md
git switch -c substrate-b/close
git commit -m "docs(spec): the ingest spec's :133 :137 :195 and assembly §15 items 03 and 05, amended by Plan B" -- docs/superpowers/specs/2026-09-06-import-redesign-design.md docs/superpowers/specs/2026-09-05-assembly-design.md docs/superpowers/specs/2026-10-03-substrate-components-design.md mutation-baseline.txt
git push -u origin substrate-b/close
```

Merge `--ff-only` when green. Plan C opens from this `main`.

______________________________________________________________________

## Coverage notes

- §5.3.1: Task 4 (the monitor, the hold set, built reasons, the ack scope through the existing repo-path hash) and Task 9 (holds at publish through the per-commit re-check; annotated tags; CI).
- §5.3.2 (#205): Task 4. §5.3.3 (#206): Task 7. §5.3.4: Tasks 1 (#185), 2 (#188), 3 (#195). §5.3.5 (#189): Task 5. §5.3.6 (#183): Task 8. §5.3.7 (#196): Task 6.
- §8 Zotero legs for these items: Task 10 (#185/#188, Attachment Scanner after #189, arXiv Workflow's merge leg). ZotMoov's and Linter's legs are Plan D's.
- §11: the ingest spec's `:133`, `:137`, `:195` and assembly §15 items 03, 05 (Task 11); `CONTEXT.md`'s Snapshot and Standing entries (Tasks 3, 8); ADR 0003's scope note (Task 8, a deviation this plan settles); the skills `capture-source`, `project-flow`, `publish` (Tasks 1, 3–6, 8, 9).
- Designs cluster 1's order (#185/#188 → monitor with #205 → #189 and #196 → #206 → #183) is Tasks 1–2 → 4 → 5–6 → 7 → 8; Task 3 (#195) sits before the monitor because the hold set exempts its two fields.
