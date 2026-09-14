"""Live legs against Zotero 10 (spec §7). Read legs need RV_LIVE=1; the write
leg needs RV_LIVE_WRITE_BASE too and refuses the production instance."""

# An automated propagate leg (Part A Task 20 Step 1 ran it attended on
# 2026-09-13) re-keys an item over the local API: measured, PATCH accepts the
# native ``citationKey`` field — ``PATCH /api/users/0/items/<key>`` with
# ``If-Unmodified-Since-Version`` answered 204 and Better BibTeX agreed within
# seconds; the legacy Extra line was never needed (research records 449-451,
# appended by this task from the Task 20 report). Print the leg from those
# records: authorize once, PATCH the native field, run the linter, propagate,
# restore the key with a second PATCH.

import json
import os
import time

import pytest

from research_vault import Result, capture, lifecycle, notes, zotero

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
    text = (tmp_vault / "literatures" / f"{key}.md").read_text()
    provenance = notes.read_provenance(text)
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
    assert base.rstrip("/") != zotero.DEFAULT_BASE, "write legs never touch production"
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
    assert outcomes[0].reason.startswith("matched — created "), outcomes
    item_key = outcomes[0].reason.split("created ")[1].split(",")[0]
    note = next((tmp_vault / "literatures").glob("*.md"))
    provenance = notes.read_provenance(note.read_text())
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
    assert item_key not in trashed_versions and item_key in trash
    (row,) = lifecycle.lint_lifecycle(tmp_vault, client)
    assert row.reason.startswith("trashed — ")
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
    assert row.reason.startswith("deleted — ")
