"""Live legs against Zotero 10 (spec §7). Read legs need RV_LIVE=1 and read
``RV_LIVE_WRITE_BASE`` when set, else production (they never write); the write
legs need RV_LIVE_WRITE_BASE too and refuse the production instance.

Legs: the capture round trip; add/edit/trash/delete; native PMID/PMCID per item
type (#185, write); the schema fold with a conference paper's venue (#188); the
schema's CSL text fields for PMID/PMCID; a tagged item's CSL entry carries no
tags or keyword. Facts a leg measures are one ``LIVE-FACT`` JSON line each on
stderr (read them under ``-s``), every one naming the base it came from."""

import json
import os
import re
import sys
import time

import pytest

from research_vault import (
    Result,
    capture,
    frontmatter,
    lifecycle,
    literature_notes,
    zotero,
)
from tests.conftest import is_production_base

READ_BASE = os.environ.get("RV_LIVE_WRITE_BASE") or zotero.DEFAULT_BASE


@pytest.mark.live
def test_capture_round_trip_on_a_live_item(tmp_vault):
    client = zotero.ZoteroClient(base=READ_BASE)
    items, _ = client.top_items()
    keyed = next(
        i
        for i in items
        if i["data"].get("citationKey") and i.get("meta", {}).get("numChildren")
    )
    key = keyed["data"]["citationKey"]
    outcomes = capture.capture(tmp_vault, client, [key])
    assert outcomes[0].result is Result.MATCHED
    text = (tmp_vault / "literature" / f"{key}.md").read_text()
    provenance = literature_notes.read_provenance(text)
    assert provenance.server_id == client.server_info()["server_id"]
    assert provenance.item_version == keyed["version"]
    again = capture.capture(tmp_vault, client, [key])
    assert again[0].reason == "matched — NOOP"
    (row,) = [o for o in lifecycle.lint_lifecycle(tmp_vault, client) if o.target == key]
    assert row.result is Result.MATCHED


@pytest.mark.live
@pytest.mark.live_write
def test_add_edit_trash_delete_transitions_and_record_the_trashed_snapshot(tmp_vault):
    base = os.environ["RV_LIVE_WRITE_BASE"]
    assert not is_production_base(base), "write legs never touch production"
    client = zotero.ZoteroClient(
        base=base, api_key=os.environ.get("RV_LIVE_WRITE_KEY") or None
    )
    stamp = time.strftime("%Y%m%d%H%M%S")
    outcomes = capture.add(
        tmp_vault,
        client,
        [
            {
                "itemType": "journalArticle",
                "title": f"research-vault live leg {stamp}",
                "creators": [
                    {
                        "creatorType": "author",
                        "lastName": "Sitting",
                        "firstName": "Live",
                    }
                ],
                "date": "2026",
            }
        ],
    )
    # One item was posted, so the reason names exactly one Zotero key (eight
    # upper-case alphanumerics); the key itself is the instance's to mint.
    created = re.fullmatch(r"matched — created ([A-Z0-9]{8})", outcomes[0].reason)
    assert created, outcomes
    item_key = created.group(1)
    note = next((tmp_vault / "literature").glob("*.md"))
    provenance = literature_notes.read_provenance(note.read_text())
    assert provenance.item_key == item_key

    # the snapshot the sitting missed: the scratch item live in the items map
    versions, _ = client.versions()
    assert item_key in versions
    live_snapshot = {k: v for k, v in versions.items() if k == item_key}

    envelope = client.item(item_key)
    status = client.trash_item(item_key, envelope["version"])
    assert status == 204
    trashed_versions, _ = client.versions()
    trash = client.trash_versions()
    assert item_key not in trashed_versions
    assert item_key in trash
    (row,) = lifecycle.lint_lifecycle(tmp_vault, client)
    assert row.reason == f"trashed — {item_key}"
    fixture = {
        "live": live_snapshot,
        "trashed_items": {k: v for k, v in trashed_versions.items() if k == item_key},
        "trashed_trash": {k: v for k, v in trash.items() if k == item_key},
    }
    (tmp_vault / "items-trashed.json").write_text(
        json.dumps(fixture, indent=2, sort_keys=True) + "\n"
    )

    status = client.delete_item(item_key, trash[item_key])
    assert status == 204
    (row,) = lifecycle.lint_lifecycle(tmp_vault, client)
    assert row.reason == f"deleted — {item_key}"


def _record(name, base, facts):
    """A live fact the controller reads back: one stderr line, visible under
    ``-s``, naming the base it came from. Not ``record_property``: that needs
    ``--junitxml`` to be read at all, and ruff bans ``print`` in tests."""
    text = json.dumps({"base": base, **facts}, sort_keys=True, default=str)
    sys.stderr.write(f"LIVE-FACT {name} {text}\n")


def _csl_fact(client, citation_key):
    """The exported CSL entry's PMID/PMCID, or why none was read (a live fact)."""
    if not citation_key:
        return "no citation key, so no export"
    try:
        (entry,) = client.export_csl([citation_key])
    except (zotero.ZoteroError, ValueError) as error:
        return f"export failed: {error}"
    return {name: entry.get(name) for name in ("PMID", "PMCID")}


def _trash_stamped(client, title):
    """Trash every live top item titled ``title``; the errors, not a raise, so a
    cleanup failure cannot mask the error that sent the test here."""
    errors = []
    try:
        items, _ = client.top_items()
        for item in items:
            if item["data"].get("title") == title:
                try:
                    client.trash_item(item["key"], item["version"])
                except zotero.ZoteroError as error:
                    errors.append(f"{item['key']}: {error}")
    except zotero.ZoteroError as error:
        errors.append(f"listing leftovers: {error}")
    return errors


_IDS = {"PMID": "28503678", "PMCID": "PMC5428074"}


@pytest.mark.live
@pytest.mark.live_write
@pytest.mark.parametrize(
    "item_type", ["journalArticle", "conferencePaper", "book", "preprint", "report"]
)
def test_zotero_accepts_pmid_and_pmcid_per_item_type(tmp_vault, item_type):
    base = os.environ["RV_LIVE_WRITE_BASE"]
    assert not is_production_base(base), "write legs never touch production"
    client = zotero.ZoteroClient(
        base=base, api_key=os.environ.get("RV_LIVE_WRITE_KEY") or None
    )
    title = f"research-vault #185 {item_type} {time.strftime('%Y%m%d%H%M%S')}"
    try:
        outcomes = capture.add(
            tmp_vault,
            client,
            [
                {
                    "itemType": item_type,
                    "title": title,
                    "creators": [
                        {
                            "creatorType": "author",
                            "lastName": "Sitting",
                            "firstName": "Live",
                        }
                    ],
                    "date": "2026",
                    **_IDS,
                }
            ],
        )
        _check_ids_per_type(tmp_vault, client, base, item_type, outcomes)
    finally:
        errors = _trash_stamped(client, title)
        if errors and sys.exc_info()[0] is None:
            raise AssertionError(f"cleanup failed: {errors}")
        if errors:
            sys.stderr.write(f"LIVE-CLEANUP-FAILED {title}: {errors}\n")


def _check_ids_per_type(tmp_vault, client, base, item_type, outcomes):
    """Record what Zotero did with the two ids, then assert the capture agrees."""
    # outcomes[0] is add's own row; the capture rows follow it. The brief read
    # outcomes[0] as the capture row.
    facts = {"item_type": item_type, "add": outcomes[0].reason}
    created = re.fullmatch(r"matched — created ([A-Z0-9]{8})", outcomes[0].reason)
    if created is None:
        # Only Zotero's own refusal of the post says the field is not accepted;
        # a denial, not-admitted, outage or database-changed row is not that.
        refused = outcomes[0].reason.startswith("mismatch — create failed")
        facts["verdict"] = "REFUSED (create failed)" if refused else "NOT RUN"
        _record(f"#185 {item_type}", base, facts)
        assert refused, outcomes
        return
    data = client.item(created.group(1))["data"]
    facts["stored"] = {n: data.get(n) for n in _IDS}
    facts["per_field"] = {
        n: "kept" if data.get(n) == v else "dropped" for n, v in _IDS.items()
    }
    facts["capture"] = [(o.result.name, o.reason) for o in outcomes[1:]]
    facts["csl"] = _csl_fact(client, data.get("citationKey"))
    notes = list((tmp_vault / "literature").glob("*.md"))
    if notes:
        note, _ = frontmatter.parse(notes[0].read_text())
        facts["note"] = {n: note.get(n) for n in _IDS}
    _record(f"#185 {item_type}", base, facts)  # before any assert: a failure keeps it
    assert outcomes[1].result is Result.MATCHED, outcomes
    assert facts.get("note") == facts["stored"], facts


@pytest.mark.live
def test_the_schema_serves_csl_text_fields_for_pmid_and_pmcid():
    """``schema()["csl"]["fields"]["text"]`` entries for PMID/PMCID, ``.get``
    all the way down: a payload without the key is a recorded fact, not a
    failure."""
    csl = zotero.ZoteroClient(base=READ_BASE).schema().get("csl")
    fields = csl.get("fields") if isinstance(csl, dict) else None
    text = fields.get("text") if isinstance(fields, dict) else None
    fact = (
        {n: text.get(n, "absent") for n in _IDS}
        if isinstance(text, dict)
        else "schema carries no csl.fields.text"
    )
    _record("#185 schema csl.fields.text", READ_BASE, {"entries": fact})


@pytest.mark.live
def test_the_local_api_serves_the_schema_and_a_conference_paper_folds(tmp_vault):
    client = zotero.ZoteroClient(base=READ_BASE)
    folded = literature_notes.base_field_map(client.schema())
    assert folded["conferencePaper"]["proceedingsTitle"] == "publicationTitle"
    assert folded["bookSection"]["bookTitle"] == "publicationTitle"
    items, _ = client.top_items()
    paper = next(
        (
            i
            for i in items
            if i["data"].get("itemType") == "conferencePaper"
            and i["data"].get("citationKey")
            and i["data"].get("proceedingsTitle")
            and not i["data"].get("publicationTitle")
        ),
        None,
    )
    if paper is None:
        pytest.skip("no conference paper with only a proceedingsTitle on this instance")
    key = paper["data"]["citationKey"]
    outcomes = capture.capture(tmp_vault, client, [key])
    assert outcomes[0].result is Result.MATCHED
    data, _ = frontmatter.parse((tmp_vault / "literature" / f"{key}.md").read_text())
    # the folded value, as the note renders any string
    expected = literature_notes.frontmatter_value(paper["data"]["proceedingsTitle"])
    assert data.get("publicationTitle") == expected
    assert "proceedingsTitle" not in data


@pytest.mark.live
def test_a_tagged_items_csl_entry_carries_no_tags_or_keyword():
    client = zotero.ZoteroClient(base=READ_BASE)
    items, _ = client.top_items()
    tagged = next(
        (i for i in items if i["data"].get("tags") and i["data"].get("citationKey")),
        None,
    )
    if tagged is None:
        pytest.skip("no tagged item with a citation key on this instance")
    (entry,) = client.export_csl([tagged["data"]["citationKey"]])
    _record("R15 csl keys", READ_BASE, {"keys": sorted(entry)})
    assert "tags" not in entry
    extra = tagged["data"].get("extra") or ""
    if not re.search(r"^\s*keyword:", extra, re.MULTILINE | re.IGNORECASE):
        assert "keyword" not in entry, entry
