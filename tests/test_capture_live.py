"""Live legs against Zotero 10 (spec §7). Read legs need RV_LIVE=1; the write
leg needs RV_LIVE_WRITE_BASE too and refuses the production instance."""

import json
import os
import re
import time

import pytest

from research_vault import Result, capture, lifecycle, literature_notes, zotero
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
