"""Live legs against Zotero 10 (spec §7). Read legs need RV_LIVE=1; the write
leg needs RV_LIVE_WRITE_BASE too and refuses the production instance."""

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


def _record(record_property, name, facts):
    """A live fact the controller reads back: a junit property
    (``--junitxml``) and one stderr line (visible under ``-s``). ruff bans
    ``print`` in tests; stderr keeps the line out of the captured stdout."""
    text = json.dumps(facts, sort_keys=True, default=str)
    record_property(name, text)
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


def _schema_csl_fact(client):
    """``schema()["csl"]["fields"]["text"]`` entries for PMID/PMCID, ``.get``
    all the way down: the payload may not carry the key at all."""
    csl = client.schema().get("csl")
    fields = csl.get("fields") if isinstance(csl, dict) else None
    text = fields.get("text") if isinstance(fields, dict) else None
    if not isinstance(text, dict):
        return "schema carries no csl.fields.text"
    return {name: text.get(name, "absent") for name in ("PMID", "PMCID")}


@pytest.mark.live
@pytest.mark.live_write
@pytest.mark.parametrize(
    "item_type", ["journalArticle", "conferencePaper", "book", "preprint", "report"]
)
def test_zotero_accepts_pmid_and_pmcid_per_item_type(
    tmp_vault, item_type, record_property
):
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
                "itemType": item_type,
                "title": f"research-vault #185 {item_type} {stamp}",
                "creators": [
                    {
                        "creatorType": "author",
                        "lastName": "Sitting",
                        "firstName": "Live",
                    }
                ],
                "date": "2026",
                "PMID": "28503678",
                "PMCID": "PMC5428074",
            }
        ],
    )
    # outcomes[0] is add's own row (created, or Zotero refused the post); the
    # capture rows follow it. The brief read outcomes[0] as the capture row.
    created = re.fullmatch(r"matched — created ([A-Z0-9]{8})", outcomes[0].reason)
    item_key = created.group(1) if created else None
    try:
        facts = {"item_type": item_type, "add": outcomes[0].reason}
        if item_key is None:
            # Zotero refused the post: the field is not accepted for this type.
            assert outcomes[0].result is Result.UNMATCHED, outcomes
            facts["verdict"] = "REFUSED (create failed)"
        else:
            data = client.item(item_key)["data"]
            facts["stored"] = {n: data.get(n) for n in ("PMID", "PMCID")}
            facts["capture"] = [(o.result.name, o.reason) for o in outcomes[1:]]
            kept = facts["stored"] == {"PMID": "28503678", "PMCID": "PMC5428074"}
            facts["verdict"] = "ACCEPTED" if kept else "DROPPED (created without them)"
            facts["csl"] = _csl_fact(client, data.get("citationKey"))
            facts["schema_csl_text"] = _schema_csl_fact(client)
            notes = list((tmp_vault / "literature").glob("*.md"))
            if kept and outcomes[1].result is Result.MATCHED:
                note, _ = frontmatter.parse(notes[0].read_text())
                facts["note"] = {n: note.get(n) for n in ("PMID", "PMCID")}
                assert facts["note"] == facts["stored"], facts
        _record(record_property, f"#185 {item_type}", facts)
    finally:
        if item_key is not None:
            client.trash_item(item_key, client.item(item_key)["version"])


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
        ),
        None,
    )
    if paper is None:
        pytest.skip("no conference paper on this instance")
    key = paper["data"]["citationKey"]
    outcomes = capture.capture(tmp_vault, client, [key])
    assert outcomes[0].result is Result.MATCHED
    data, _ = frontmatter.parse((tmp_vault / "literature" / f"{key}.md").read_text())
    assert "proceedingsTitle" not in data


@pytest.mark.live
def test_a_tagged_items_csl_entry_carries_no_tags_or_keyword(record_property):
    client = zotero.ZoteroClient(base=READ_BASE)
    items, _ = client.top_items()
    tagged = next(
        (i for i in items if i["data"].get("tags") and i["data"].get("citationKey")),
        None,
    )
    if tagged is None:
        pytest.skip("no tagged item with a citation key on this instance")
    (entry,) = client.export_csl([tagged["data"]["citationKey"]])
    _record(record_property, "R15 csl keys", sorted(entry))
    assert "tags" not in entry
    if not re.search(r"^keyword:", tagged["data"].get("extra") or "", re.MULTILINE):
        assert "keyword" not in entry, entry
