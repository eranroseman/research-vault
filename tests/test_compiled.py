import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

from research_vault import Result, captured, compiled, gitstate, propagate, scaffold


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _page(vault, relative, text):
    path = vault / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def _journal(vault, operation, writes, *, state="complete", epoch=None):
    """A complete compile-tool journal naming `writes` ({path: sha256 or None})."""
    folder = vault / ".vault-meta" / "transactions" / operation
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "journal.json").write_text(
        json.dumps(
            {
                "schema": "claude-obsidian.transaction-journal.v1",
                "operation_id": operation,
                "operation_type": "ingest",
                "state": state,
                "created_epoch": epoch if epoch is not None else time.time(),
                "writes": [
                    {
                        "path": path,
                        "mode": "replace",
                        "new_sha256": sha,
                        "original_sha256": None,
                    }
                    for path, sha in writes.items()
                ],
                "applied": list(writes),
            }
        )
    )


def _commit(vault, message="sealed"):
    subprocess.run(["git", "add", "-A"], cwd=vault, check=True)
    subprocess.run(
        ["git", "commit", "-qm", message, "--no-verify"], cwd=vault, check=True
    )


@pytest.fixture
def wiki_vault(tmp_path):
    scaffold.scaffold_vault(tmp_path)
    (tmp_path / "wiki").mkdir()
    return tmp_path


def test_seal_moves_a_complete_journal_write_into_the_record_and_normalises_links(
    wiki_vault,
):
    page = _page(
        wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\nSee [[B]].\n"
    )
    _page(wiki_vault, "wiki/concepts/B.md", "---\ntype: concept\n---\n")
    _journal(
        wiki_vault,
        "op1",
        {
            "wiki/sources/A.md": _sha(page.read_bytes()),
            "wiki/concepts/B.md": _sha(
                (wiki_vault / "wiki" / "concepts" / "B.md").read_bytes()
            ),
        },
    )
    rows = compiled.seal(wiki_vault)
    assert [(o.result, o.reason) for o in rows] == [
        (Result.MATCHED, "matched — sealed 2")
    ]
    assert page.read_text() == "---\ntype: source\n---\nSee [B](/wiki/concepts/B.md).\n"
    record = compiled.load_record(wiki_vault)
    assert record == {
        "wiki/sources/A.md": _sha(page.read_bytes()),
        "wiki/concepts/B.md": _sha(
            (wiki_vault / "wiki" / "concepts" / "B.md").read_bytes()
        ),
    }
    assert compiled.seal(wiki_vault) == [
        compiled.Outcome(
            compiled.CHECK, compiled.RECORD_PATH, Result.MATCHED, "matched — sealed 0"
        )
    ]


def test_the_record_is_canonical_sorted_json(wiki_vault):
    compiled.write_record(wiki_vault, {"wiki/b.md": "2" * 64, "wiki/a.md": "1" * 64})
    assert (wiki_vault / compiled.RECORD_PATH).read_text() == (
        '{\n  "schema": "research-vault.compiled-pages.v1",\n  "pages": {\n'
        f'    "wiki/a.md": "{"1" * 64}",\n    "wiki/b.md": "{"2" * 64}"\n  }}\n}}\n'
    )


def test_seal_refuses_bytes_no_complete_compile_wrote(wiki_vault):
    page = _page(
        wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\nhand-written\n"
    )
    _journal(wiki_vault, "op0", {"wiki/sources/A.md": "0" * 64}, state="applying")
    rows = compiled.seal(wiki_vault)
    assert [(o.result, o.target, o.reason) for o in rows] == [
        (
            Result.UNMATCHED,
            "path-bytes:wiki/sources/A.md",
            (
                "drift — wiki/sources/A.md is not sealed: no complete compile wrote these bytes"
                "; write it through the compile tool and seal, remove it, or acknowledge (a row stamped with a commit clears only by acknowledgement)"
            ),
        )
    ]
    assert compiled.load_record(wiki_vault) == {}
    assert page.read_text().endswith("hand-written\n")


def test_seal_accepts_only_the_latest_complete_write_for_a_path(wiki_vault):
    """Accepting any complete journal would re-seal a File-recovery restore of an older compile."""
    page = _page(wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\nolder\n")
    older = _sha(page.read_bytes())
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": older}, epoch=1_000)
    _journal(wiki_vault, "op2", {"wiki/sources/A.md": "f" * 64}, epoch=2_000)
    (row,) = compiled.seal(wiki_vault)
    assert row.result is Result.UNMATCHED
    assert compiled.journal_hashes(wiki_vault) == {"wiki/sources/A.md": "f" * 64}


def test_seal_drops_a_recorded_page_the_tool_deleted(wiki_vault):
    page = _page(wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\n")
    _journal(
        wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())}, epoch=1_000
    )
    compiled.seal(wiki_vault)
    page.unlink()
    _journal(wiki_vault, "op2", {"wiki/sources/A.md": None}, epoch=2_000)
    (row,) = compiled.seal(wiki_vault)
    assert row.result is Result.MATCHED
    assert compiled.load_record(wiki_vault) == {}


def test_seal_refuses_a_page_whose_frontmatter_is_not_yaml(wiki_vault):
    page = _page(wiki_vault, "wiki/sources/A.md", "---\ntitle: A: B\n---\n")
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())})
    (row,) = compiled.seal(wiki_vault)
    assert row.result is Result.UNMATCHED
    assert row.reason.startswith(
        "schema-violation — wiki/sources/A.md: frontmatter is not valid YAML"
    )
    assert compiled.load_record(wiki_vault) == {}


def test_lint_reports_drift_against_the_record_and_accepts_the_local_journal(
    wiki_vault,
):
    """Designs cluster 2(a): a hand edit is drift; a fresh compile before seal is
    MATCHED locally; CI, with no .vault-meta, reads only the record."""
    page = _page(wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\nv1\n")
    _journal(
        wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())}, epoch=1_000
    )
    compiled.seal(wiki_vault)
    assert [o.result for o in compiled.lint_compiled_layer(wiki_vault)] == [
        Result.MATCHED
    ]
    page.write_text("---\ntype: source\n---\nv1 edited by hand\n")
    (row,) = compiled.lint_compiled_layer(wiki_vault)
    assert (row.check, row.result, row.target, row.reason) == (
        "compiled-layer",
        Result.UNMATCHED,
        "path-bytes:wiki/sources/A.md",
        (
            "drift — wiki/sources/A.md differs from the compiled-page record"
            "; revert it to the sealed bytes, rewrite it through the compile tool and seal, or acknowledge (a row stamped with a commit clears only by acknowledgement)"
        ),
    )
    page.write_text("---\ntype: source\n---\nv2\n")
    _journal(
        wiki_vault, "op2", {"wiki/sources/A.md": _sha(page.read_bytes())}, epoch=2_000
    )
    assert [o.result for o in compiled.lint_compiled_layer(wiki_vault)] == [
        Result.MATCHED
    ]
    assert [
        o.result
        for o in compiled.lint_compiled_layer(
            wiki_vault, repository_root=wiki_vault / "nowhere"
        )
    ] == [Result.UNMATCHED]


def test_lint_hashes_bases_canvases_and_attachments_too(wiki_vault):
    """Q27: every file under wiki/, not only pages."""
    base = _page(wiki_vault, "wiki/views/all.base", "views: []\n")
    canvas = _page(wiki_vault, "wiki/canvases/map.canvas", "{}\n")
    image = wiki_vault / "wiki" / "fig.png"
    image.write_bytes(b"\x89PNG")
    _journal(
        wiki_vault,
        "op1",
        {
            "wiki/views/all.base": _sha(base.read_bytes()),
            "wiki/canvases/map.canvas": _sha(canvas.read_bytes()),
            "wiki/fig.png": _sha(image.read_bytes()),
        },
    )
    compiled.seal(wiki_vault)
    base.write_text("views: [{type: table}]\n")
    (row,) = [
        o
        for o in compiled.lint_compiled_layer(wiki_vault)
        if o.result is Result.UNMATCHED
    ]
    assert "wiki/views/all.base" in row.target


def test_lint_reports_a_recorded_page_that_vanished_and_an_unsealed_newcomer(
    wiki_vault,
):
    page = _page(wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\n")
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())})
    compiled.seal(wiki_vault)
    page.unlink()
    _page(wiki_vault, "wiki/sources/New.md", "---\ntype: source\n---\n")
    rows = sorted(
        (o.target, o.reason)
        for o in compiled.lint_compiled_layer(wiki_vault)
        if o.result is Result.UNMATCHED
    )
    assert rows == [
        (
            "path-bytes:wiki/sources/A.md",
            "drift — wiki/sources/A.md is recorded but absent; restore it, or acknowledge (a row stamped with a commit clears only by acknowledgement)",
        ),
        (
            "path-bytes:wiki/sources/New.md",
            (
                "drift — wiki/sources/New.md is not sealed: no complete compile wrote these bytes"
                "; write it through the compile tool and seal, remove it, or acknowledge (a row stamped with a commit clears only by acknowledgement)"
            ),
        ),
    ]


def test_a_link_only_change_from_a_rename_reseals_itself(wiki_vault):
    """Decision 13: Obsidian's rename rewrote `[B](/wiki/concepts/B.md)` to
    `[B](/wiki/concepts/C.md)`; the only differences are link destinations
    that resolve, so the page is MATCHED and seal updates the entry."""
    page = _page(
        wiki_vault,
        "wiki/sources/A.md",
        "---\ntype: source\n---\nSee [B](/wiki/concepts/B.md) and [B](/wiki/concepts/B.md#h).\n",
    )
    target = _page(wiki_vault, "wiki/concepts/B.md", "---\ntype: concept\n---\n")
    _journal(
        wiki_vault,
        "op1",
        {
            "wiki/sources/A.md": _sha(page.read_bytes()),
            "wiki/concepts/B.md": _sha(target.read_bytes()),
        },
    )
    compiled.seal(wiki_vault)
    # The record and the page are committed together: `_recorded_text` reads
    # the sealed bytes back from HEAD.
    _commit(wiki_vault)
    target.rename(wiki_vault / "wiki" / "concepts" / "C.md")
    page.write_text(
        "---\ntype: source\n---\nSee [B](/wiki/concepts/C.md) and [B](/wiki/concepts/C.md#h).\n"
    )
    rows = compiled.lint_compiled_layer(wiki_vault)
    assert [(o.result, o.target, o.reason) for o in rows if "A.md" in o.target] == [
        (
            Result.MATCHED,
            "path-bytes:wiki/sources/A.md",
            "matched — link targets follow a rename; run seal wiki/sources/A.md",
        )
    ]
    # the renamed-away path is recorded but absent
    assert any(o.result is Result.UNMATCHED and "B.md" in o.target for o in rows)
    # and the new one is not sealed
    assert any(o.result is Result.UNMATCHED and "C.md" in o.target for o in rows)
    (sealed,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert sealed.result is Result.MATCHED
    assert compiled.load_record(wiki_vault)["wiki/sources/A.md"] == _sha(
        page.read_bytes()
    )


def test_a_content_change_beside_a_link_change_is_still_drift(wiki_vault):
    page = _page(
        wiki_vault,
        "wiki/sources/A.md",
        "---\ntype: source\n---\nSee [B](/wiki/concepts/B.md). Old prose.\n",
    )
    _page(wiki_vault, "wiki/concepts/B.md", "---\ntype: concept\n---\n")
    _page(wiki_vault, "wiki/concepts/C.md", "---\ntype: concept\n---\n")
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())})
    compiled.seal(wiki_vault)
    _commit(wiki_vault)
    page.write_text(
        "---\ntype: source\n---\nSee [B](/wiki/concepts/C.md). New prose.\n"
    )
    rows = [o for o in compiled.lint_compiled_layer(wiki_vault) if "A.md" in o.target]
    assert rows[0].result is Result.UNMATCHED


def _propagation_record(vault, operation_id, mapping):
    """An applied propagation record under system/propagations/, as
    `propagate.apply` writes it."""
    folder = vault / propagate.RECORD_DIR
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{operation_id}.json").write_text(
        json.dumps(
            {
                "schema": propagate.SCHEMA,
                "operation_id": operation_id,
                "date": "2026-11-27",
                "mapping": mapping,
                "item_keys": dict.fromkeys(mapping, "E352DFS8"),
                "merges": {},
                "removes": {},
                "surfaces": [],
            }
        )
    )


def _sealed_citing_page(vault):
    page = _page(
        vault,
        "wiki/sources/A.md",
        "---\ntype: source\n---\nAs [@old2020, p. 3] shows.\n",
    )
    _journal(vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())})
    compiled.seal(vault)
    _commit(vault)
    return page


def test_a_key_rewrite_a_propagation_record_names_reseals_itself(wiki_vault):
    """R35: the diff between the sealed bytes and the page is only the
    citation-key rewrite an applied propagation record names."""
    page = _sealed_citing_page(wiki_vault)
    page.write_text("---\ntype: source\n---\nAs [@new2020, p. 3] shows.\n")
    _propagation_record(wiki_vault, "20261127T000000Z", {"old2020": "new2020"})
    rows = [o for o in compiled.lint_compiled_layer(wiki_vault) if "A.md" in o.target]
    assert [(o.result, o.reason) for o in rows] == [
        (
            Result.MATCHED,
            (
                "matched — citation keys follow propagation 20261127T000000Z; "
                "run seal wiki/sources/A.md"
            ),
        )
    ]
    (sealed,) = compiled.seal(wiki_vault)
    assert (sealed.result, sealed.reason) == (Result.MATCHED, "matched — sealed 1")
    assert compiled.load_record(wiki_vault)["wiki/sources/A.md"] == _sha(
        page.read_bytes()
    )


def test_a_key_rewrite_no_propagation_record_names_is_refused(wiki_vault):
    page = _sealed_citing_page(wiki_vault)
    page.write_text("---\ntype: source\n---\nAs [@new2020, p. 3] shows.\n")
    _propagation_record(wiki_vault, "20261127T000000Z", {"old2020": "other2020"})
    (row,) = compiled.seal(wiki_vault)
    assert row.result is Result.UNMATCHED
    assert row.reason == (
        "drift — wiki/sources/A.md differs from the compiled-page record"
        "; revert it to the sealed bytes, rewrite it through the compile tool and seal, or acknowledge (a row stamped with a commit clears only by acknowledgement)"
    )
    (row,) = compiled.lint_compiled_layer(wiki_vault)
    assert row.result is Result.UNMATCHED


def test_a_key_rewrite_beside_a_content_change_is_refused(wiki_vault):
    page = _sealed_citing_page(wiki_vault)
    page.write_text("---\ntype: source\n---\nAs [@new2020, p. 3] proves.\n")
    _propagation_record(wiki_vault, "20261127T000000Z", {"old2020": "new2020"})
    (row,) = compiled.seal(wiki_vault)
    assert row.result is Result.UNMATCHED


def test_an_unreadable_record_is_one_row_not_a_traceback(wiki_vault):
    (wiki_vault / "system" / "compiled-pages.json").write_text("{not json")
    _page(wiki_vault, "wiki/sources/A.md", "x\n")
    (row,) = compiled.lint_compiled_layer(wiki_vault)
    assert (row.result, row.target) == (
        Result.UNMATCHED,
        "path-bytes:system/compiled-pages.json",
    )
    assert row.reason.startswith("schema-violation — compiled-page record unreadable")
    (row,) = compiled.seal(wiki_vault)
    assert row.reason.startswith("schema-violation — compiled-page record unreadable")


@pytest.mark.parametrize(
    "document",
    [
        '["a list"]',
        '{"schema": "other", "pages": {}}',
        '{"schema": "research-vault.compiled-pages.v1", "pages": {"a": 1}}',
    ],
)
def test_a_record_of_the_wrong_shape_is_unreadable(wiki_vault, document):
    (wiki_vault / "system" / "compiled-pages.json").write_text(document)
    with pytest.raises(compiled.RecordError):
        compiled.load_record(wiki_vault)


def test_a_name_that_is_not_utf8_is_a_row_and_never_sealed(wiki_vault):
    """The reason carries no raw name: a lone surrogate would crash the
    queue's strict UTF-8 write. The encoded target names the file."""
    try:
        (wiki_vault / "wiki" / os.fsdecode(b"caf\xe9.md")).write_bytes(b"x\n")
    except OSError:
        pytest.skip("the filesystem refuses a name that is not UTF-8")
    reason = (
        "drift — this file's name is not UTF-8 text, so it cannot be sealed; "
        "rename it to UTF-8 text, remove it, or acknowledge (a row stamped with a commit clears only by acknowledgement)"
    )
    (row,) = compiled.lint_compiled_layer(wiki_vault)
    assert (row.result, row.target, row.reason) == (
        Result.UNMATCHED,
        "path-bytes:wiki/caf%E9.md",
        reason,
    )
    (row,) = compiled.seal(wiki_vault)
    assert (row.result, row.target, row.reason) == (
        Result.UNMATCHED,
        "path-bytes:wiki/caf%E9.md",
        reason,
    )
    assert compiled.load_record(wiki_vault) == {}


def test_a_symlink_whose_name_is_not_utf8_is_this_file_in_the_reason(
    wiki_vault, tmp_path_factory
):
    """The reason is a filed finding's field, written strictly as UTF-8, so
    it says "this file" where the name is not text."""
    outside = tmp_path_factory.mktemp("outside") / "x.md"
    outside.write_text("x\n")
    try:
        (wiki_vault / "wiki" / os.fsdecode(b"caf\xe9.md")).symlink_to(outside)
    except OSError:
        pytest.skip("the filesystem refuses a name that is not UTF-8")
    (row,) = compiled.lint_compiled_layer(wiki_vault)
    assert (row.target, row.reason) == (
        "path-bytes:wiki/caf%E9.md",
        "drift — this file is a symlink; a compiled page is a file: "
        + compiled.NOT_A_FILE_REMEDY,
    )


def test_no_wiki_is_skipped(tmp_vault):
    # The bare fixture vault carries an empty wiki/concepts/; a vault with no
    # wiki/ at all has no compiled layer.
    shutil.rmtree(tmp_vault / "wiki")
    assert compiled.lint_compiled_layer(tmp_vault) == [
        compiled.Outcome(
            compiled.CHECK, "wiki", Result.SKIPPED, "no-identifier — no compiled layer"
        )
    ]


def test_a_retarget_between_two_pages_that_both_exist_is_drift(wiki_vault):
    """C8a: no rename happened; Supports.md and Refutes.md both stand."""
    page = _page(
        wiki_vault,
        "wiki/sources/A.md",
        "---\ntype: source\n---\nSee [S](/wiki/concepts/Supports.md).\n",
    )
    _page(wiki_vault, "wiki/concepts/Supports.md", "---\ntype: concept\n---\n")
    _page(wiki_vault, "wiki/concepts/Refutes.md", "---\ntype: concept\n---\n")
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())})
    compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    _commit(wiki_vault)
    page.write_text("---\ntype: source\n---\nSee [S](/wiki/concepts/Refutes.md).\n")
    rows = [o for o in compiled.lint_compiled_layer(wiki_vault) if "A.md" in o.target]
    assert [o.result for o in rows] == [Result.UNMATCHED]
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert row.result is Result.UNMATCHED


def test_an_old_propagation_record_vouches_for_no_rewrite(wiki_vault):
    """C8b: a record HEAD already holds was applied long ago; a hand edit that
    happens to replay it is still drift."""
    _propagation_record(wiki_vault, "20260101T000000Z", {"old2020": "new2020"})
    page = _sealed_citing_page(wiki_vault)  # commits the record with the page
    page.write_text("---\ntype: source\n---\nAs [@new2020, p. 3] shows.\n")
    (row,) = compiled.lint_compiled_layer(wiki_vault)
    assert row.result is Result.UNMATCHED
    (row,) = compiled.seal(wiki_vault)
    assert row.result is Result.UNMATCHED


def test_an_uncommitted_seal_still_judges_a_rename(wiki_vault):
    """C7: seal keeps the sealed bytes by hash, so a rename before the next
    commit is judged against them."""
    page = _page(
        wiki_vault,
        "wiki/sources/A.md",
        "---\ntype: source\n---\nSee [B](/wiki/concepts/B.md).\n",
    )
    target = _page(wiki_vault, "wiki/concepts/B.md", "---\ntype: concept\n---\n")
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())})
    compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert (
        wiki_vault
        / compiled.SEALED_STORE
        / compiled.load_record(wiki_vault)["wiki/sources/A.md"]
    ).read_bytes() == page.read_bytes()
    target.rename(wiki_vault / "wiki" / "concepts" / "C.md")
    page.write_text("---\ntype: source\n---\nSee [B](/wiki/concepts/C.md).\n")
    (sealed,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert (sealed.result, sealed.reason) == (Result.MATCHED, "matched — sealed 1")


def test_a_rename_committed_before_reseal_is_found_in_the_path_s_history(wiki_vault):
    """C7: HEAD holds the renamed bytes and the store is gone (a fresh
    clone); the history search finds the sealed blob by its hash."""
    page = _page(
        wiki_vault,
        "wiki/sources/A.md",
        "---\ntype: source\n---\nSee [B](/wiki/concepts/B.md).\n",
    )
    target = _page(wiki_vault, "wiki/concepts/B.md", "---\ntype: concept\n---\n")
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())})
    compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    _commit(wiki_vault)
    target.rename(wiki_vault / "wiki" / "concepts" / "C.md")
    page.write_text("---\ntype: source\n---\nSee [B](/wiki/concepts/C.md).\n")
    _commit(wiki_vault, "rename, not resealed")
    shutil.rmtree(wiki_vault / compiled.SEALED_STORE)
    rows = [o for o in compiled.lint_compiled_layer(wiki_vault) if "A.md" in o.target]
    assert [o.reason for o in rows] == [
        "matched — link targets follow a rename; run seal wiki/sources/A.md"
    ]
    (sealed,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert (sealed.result, sealed.reason) == (Result.MATCHED, "matched — sealed 1")


def test_the_journal_vouches_only_when_asked(wiki_vault):
    """C6: verify passes journal=False on the index and HEAD candidates."""
    page = _page(wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\n")
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())})
    assert [o.result for o in compiled.lint_compiled_layer(wiki_vault)] == [
        Result.MATCHED
    ]
    (row,) = compiled.lint_compiled_layer(wiki_vault, journal=False)
    assert row.result is Result.UNMATCHED


def test_a_symlink_under_wiki_is_a_row_and_never_sealed(wiki_vault, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside")
    (outside / "x.md").write_text("x\n")
    (wiki_vault / "wiki" / "linked.md").symlink_to(outside / "x.md")
    (wiki_vault / "wiki" / "folder").symlink_to(outside, target_is_directory=True)
    rows = sorted(
        (o.result, o.target, o.reason) for o in compiled.lint_compiled_layer(wiki_vault)
    )
    assert rows == [
        (
            Result.UNMATCHED,
            "path-bytes:wiki/folder",
            (
                "drift — wiki/folder is a symlink; a compiled page is a file"
                ": replace it with the file itself, or acknowledge (a row stamped with a commit clears only by acknowledgement)"
            ),
        ),
        (
            Result.UNMATCHED,
            "path-bytes:wiki/linked.md",
            (
                "drift — wiki/linked.md is a symlink; a compiled page is a file"
                ": replace it with the file itself, or acknowledge (a row stamped with a commit clears only by acknowledgement)"
            ),
        ),
    ]
    assert sorted(o.target for o in compiled.seal(wiki_vault)) == [
        "path-bytes:wiki/folder",
        "path-bytes:wiki/linked.md",
    ]
    assert compiled.load_record(wiki_vault) == {}


def test_a_symlinked_wiki_is_one_row_and_nothing_behind_it_is_read(wiki_vault):
    """Round 2: `wiki` itself may be the symlink; its target lies outside
    the compiled layer, and the record's entries behind it are the symlink's
    row, not each "recorded but absent"."""
    page = _page(wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\n")
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())})
    compiled.seal(wiki_vault)
    moved = wiki_vault / "projects" / "w"
    (wiki_vault / "wiki").rename(moved)
    (moved / "hand.md").write_text("---\ntype: source\n---\nby hand\n")
    (wiki_vault / "wiki").symlink_to(moved, target_is_directory=True)
    expected = [
        (
            Result.UNMATCHED,
            "path-bytes:wiki",
            (
                "drift — wiki is a symlink; a compiled page is a file"
                ": replace it with the file itself, or acknowledge (a row stamped with a commit clears only by acknowledgement)"
            ),
        )
    ]
    assert [
        (o.result, o.target, o.reason) for o in compiled.lint_compiled_layer(wiki_vault)
    ] == expected
    assert [
        (o.result, o.target, o.reason) for o in compiled.seal(wiki_vault)
    ] == expected
    assert [
        (o.result, o.target, o.reason)
        for o in compiled.seal(wiki_vault, ["wiki/hand.md", "wiki/sources/A.md"])
    ] == expected
    assert list(compiled.load_record(wiki_vault)) == ["wiki/sources/A.md"]


def test_a_recorded_page_behind_a_symlinked_folder_is_the_symlink_s_row(
    wiki_vault, tmp_path_factory
):
    page = _page(wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\n")
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())})
    compiled.seal(wiki_vault)
    outside = tmp_path_factory.mktemp("outside")
    shutil.move(str(wiki_vault / "wiki" / "sources"), str(outside / "sources"))
    (wiki_vault / "wiki" / "sources").symlink_to(
        outside / "sources", target_is_directory=True
    )
    assert [(o.target, o.reason) for o in compiled.lint_compiled_layer(wiki_vault)] == [
        (
            "path-bytes:wiki/sources",
            (
                "drift — wiki/sources is a symlink; a compiled page is a file"
                ": replace it with the file itself, or acknowledge (a row stamped with a commit clears only by acknowledgement)"
            ),
        )
    ]


def test_a_record_applied_before_the_seal_never_vouches(wiki_vault):
    """R41 keeps F2's protection: the record's commit is an ancestor of the
    commit that sealed the page's entry, so it predates the seal. This is
    the later holder of a key: `old2020` was mapped away, and a new item took
    the name before the page citing it was sealed; replaying the old record
    over that page is a hand edit."""
    _propagation_record(wiki_vault, "20260101T000000Z", {"old2020": "new2020"})
    _commit(wiki_vault, "an old propagation")
    page = _sealed_citing_page(wiki_vault)  # sealed in a later commit
    page.write_text("---\ntype: source\n---\nAs [@new2020, p. 3] shows.\n")
    _commit(wiki_vault, "the old rewrite replayed by hand")
    (row,) = compiled.lint_compiled_layer(wiki_vault)
    assert row.result is Result.UNMATCHED
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert row.result is Result.UNMATCHED


def test_a_record_committed_after_the_seal_vouches_at_head(wiki_vault):
    """R41: the record and the rewrite were committed by hand together; the
    record is at HEAD, but its commit is not an ancestor of the sealing
    commit, so `seal <path>` accepts the rewrite."""
    page = _sealed_citing_page(wiki_vault)
    page.write_text("---\ntype: source\n---\nAs [@new2020, p. 3] shows.\n")
    _propagation_record(wiki_vault, "20261127T000000Z", {"old2020": "new2020"})
    _commit(wiki_vault, "the rewrite and its record, by hand")
    (row,) = compiled.lint_compiled_layer(wiki_vault)
    assert (row.result, row.reason) == (
        Result.MATCHED,
        (
            "matched — citation keys follow propagation 20261127T000000Z; "
            "run seal wiki/sources/A.md"
        ),
    )
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert (row.result, row.reason) == (Result.MATCHED, "matched — sealed 1")


def _git(vault, *args):
    return subprocess.run(
        ["git", *args], cwd=vault, check=True, capture_output=True, text=True
    ).stdout.strip()


def test_a_merge_that_reintroduces_a_seal_is_the_sealing_commit(wiki_vault):
    """M1: S0 seals H; a side branch adds a propagation record; main reseals
    H2; the merge resolution reseals H. The entry's sealing commit is the
    merge, which the side's record is an ancestor of, so a hand rewrite of
    H is not vouched for."""
    page = _sealed_citing_page(wiki_vault)  # S0: H sealed
    sealed_h = page.read_bytes()
    main = _git(wiki_vault, "rev-parse", "--abbrev-ref", "HEAD")
    _git(wiki_vault, "switch", "-qc", "side")
    _propagation_record(wiki_vault, "20261127T000000Z", {"old2020": "new2020"})
    _commit(wiki_vault, "side: a record")
    _git(wiki_vault, "switch", "-q", main)
    page.write_text("---\ntype: source\n---\nAs [@old2020, p. 4] shows.\n")
    _journal(
        wiki_vault,
        "op2",
        {"wiki/sources/A.md": _sha(page.read_bytes())},
        epoch=time.time() + 1,
    )
    compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    _commit(wiki_vault, "main: H2 sealed")
    subprocess.run(
        ["git", "merge", "-q", "--no-ff", "--no-commit", "side"],
        cwd=wiki_vault,
        check=False,
    )
    page.write_bytes(sealed_h)
    record = compiled.load_record(wiki_vault)
    record["wiki/sources/A.md"] = _sha(sealed_h)
    compiled.write_record(wiki_vault, record)
    _git(wiki_vault, "add", "-A")
    _git(wiki_vault, "commit", "-qm", "merge: H resealed", "--no-verify")
    page.write_text("---\ntype: source\n---\nAs [@new2020, p. 3] shows.\n")
    (row,) = compiled.lint_compiled_layer(wiki_vault, journal=False)
    assert row.result is Result.UNMATCHED
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert row.result is Result.UNMATCHED


def test_a_moved_old_record_is_still_old(wiki_vault):
    """M2: a record is known by its operation id. `git mv` of a record that
    predates the seal does not make it look applied after it."""
    _propagation_record(wiki_vault, "20260101T000000Z", {"old2020": "new2020"})
    _commit(wiki_vault, "an old propagation")
    page = _sealed_citing_page(wiki_vault)
    folder = wiki_vault / "system" / "propagations"
    _git(
        wiki_vault,
        "mv",
        "system/propagations/20260101T000000Z.json",
        "system/propagations/moved.json",
    )
    assert (folder / "moved.json").is_file()
    _commit(wiki_vault, "the record moved")
    page.write_text("---\ntype: source\n---\nAs [@new2020, p. 3] shows.\n")
    _commit(wiki_vault, "the old rewrite replayed by hand")
    (row,) = compiled.lint_compiled_layer(wiki_vault)
    assert row.result is Result.UNMATCHED
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert row.result is Result.UNMATCHED


def _raw_record(vault, name, operation_id, *, compact=False):
    """A propagation record mapping old2020 → new2020, in a spelling
    `propagate._canonical` never writes."""
    folder = vault / propagate.RECORD_DIR
    folder.mkdir(parents=True, exist_ok=True)
    document = {
        "schema": propagate.SCHEMA,
        "operation_id": operation_id,
        "date": "2026-01-01",
        "mapping": {"old2020": "new2020"},
        "item_keys": {"old2020": "E352DFS8"},
        "merges": {},
        "removes": {},
        "surfaces": [],
    }
    separators = (",", ":") if compact else None
    (folder / name).write_text(
        json.dumps(document, separators=separators, ensure_ascii=False)
    )


@pytest.mark.parametrize(
    ("operation_id", "compact"),
    [("20260101T000000Z", True), (20260101, False), ("opé-1", False)],
    ids=["compact", "non-string-id", "non-ascii-id"],
)
def test_an_old_record_in_any_spelling_never_vouches(wiki_vault, operation_id, compact):
    """N1 (C10): a record is known by its parsed operation id, never by its
    bytes, so an old record committed compact, with a number for its id, or
    with an id outside ASCII is still old."""
    _raw_record(wiki_vault, "old.json", operation_id, compact=compact)
    _commit(wiki_vault, "an old propagation")
    page = _sealed_citing_page(wiki_vault)
    page.write_text("---\ntype: source\n---\nAs [@new2020, p. 3] shows.\n")
    _commit(wiki_vault, "the old rewrite replayed by hand")
    (row,) = compiled.lint_compiled_layer(wiki_vault)
    assert row.result is Result.UNMATCHED
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert row.result is Result.UNMATCHED


@pytest.mark.parametrize(
    ("operation_id", "compact"),
    [("20261127T000000Z", True), ("opé-2", False)],
    ids=["compact", "non-ascii-id"],
)
def test_a_post_seal_record_in_any_spelling_still_vouches(
    wiki_vault, operation_id, compact
):
    """The R41 control under C10: a record committed after the seal vouches
    whatever its spelling."""
    page = _sealed_citing_page(wiki_vault)
    page.write_text("---\ntype: source\n---\nAs [@new2020, p. 3] shows.\n")
    _raw_record(wiki_vault, "new.json", operation_id, compact=compact)
    _commit(wiki_vault, "the rewrite and its record, by hand")
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert (row.result, row.reason) == (Result.MATCHED, "matched — sealed 1")


def test_an_unparseable_record_in_history_never_vouches(wiki_vault):
    """C10: a blob under system/propagations/ that does not parse may be any
    record, so the lookup is undecided and nothing vouches."""
    folder = wiki_vault / propagate.RECORD_DIR
    folder.mkdir(parents=True)
    (folder / "broken.json").write_text("{not json")
    _commit(wiki_vault, "a broken record")
    page = _sealed_citing_page(wiki_vault)
    page.write_text("---\ntype: source\n---\nAs [@new2020, p. 3] shows.\n")
    _raw_record(wiki_vault, "new.json", "20261127T000000Z")
    _commit(wiki_vault, "the rewrite and its record, by hand")
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert row.result is Result.UNMATCHED


def test_a_stray_file_beside_the_records_decides_nothing(wiki_vault):
    """P2: only the files `propagated_by` reads are records; a committed
    `notes.txt` beside them leaves the R41 control vouched for."""
    folder = wiki_vault / propagate.RECORD_DIR
    folder.mkdir(parents=True)
    (folder / "notes.txt").write_text("not a record\n")
    _commit(wiki_vault, "a stray note")
    page = _sealed_citing_page(wiki_vault)
    page.write_text("---\ntype: source\n---\nAs [@new2020, p. 3] shows.\n")
    _raw_record(wiki_vault, "new.json", "20261127T000000Z")
    _commit(wiki_vault, "the rewrite and its record, by hand")
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert (row.result, row.reason) == (Result.MATCHED, "matched — sealed 1")


def test_the_record_lookup_costs_a_bounded_number_of_git_calls(wiki_vault, monkeypatch):
    """P1: 150 records, each in its own commit, then the R41 control. The
    replay runs first and the operation-id map is read once, so the git
    calls do not grow with records times commits."""
    page = _sealed_citing_page(wiki_vault)
    folder = wiki_vault / propagate.RECORD_DIR
    folder.mkdir(parents=True, exist_ok=True)
    script = (
        'for i in $(seq 1 150); do printf \'{"schema": "research-vault.propagation.v1",'
        ' "operation_id": "op-%s", "date": "2026-11-27", "mapping": {"x%s": "y%s"},'
        ' "item_keys": {}, "merges": {}, "removes": {}, "surfaces": []}\' "$i" "$i" "$i"'
        " > system/propagations/op-$i.json && git add -A"
        ' && git commit -qm "record $i" --no-verify || exit 1; done'
    )
    subprocess.run(["bash", "-c", script], cwd=wiki_vault, check=True)
    page.write_text("---\ntype: source\n---\nAs [@new2020, p. 3] shows.\n")
    _raw_record(wiki_vault, "new.json", "20261127T000000Z")
    _commit(wiki_vault, "the rewrite and its record, by hand")
    calls = []
    real = compiled.gitstate._git

    def counting(*args, **kwargs):
        calls.append(args[1:3])
        return real(*args, **kwargs)

    monkeypatch.setattr(compiled.gitstate, "_git", counting)
    (row,) = compiled.lint_compiled_layer(wiki_vault)
    assert row.result is Result.MATCHED
    assert len(calls) <= 12, calls


# Survivor triage (Plan C Task 4): what the record lookup reads from git.

_REWRITTEN = "---\ntype: source\n---\nAs [@new2020, p. 3] shows.\n"


def _r41_control(vault):
    """The R41 control: a page sealed in one commit, then its key rewrite and
    the record naming it committed together by hand."""
    page = _sealed_citing_page(vault)
    page.write_text(_REWRITTEN)
    _propagation_record(vault, "20261127T000000Z", {"old2020": "new2020"})
    _commit(vault, "the rewrite and its record, by hand")
    return page


def test_a_stray_file_in_the_old_record_s_commit_leaves_the_record_old(wiki_vault):
    """P2: the stray `0notes.txt` sorts before the record in the same commit's
    raw diff; the lookup skips it and still reads the record after it."""
    folder = wiki_vault / propagate.RECORD_DIR
    folder.mkdir(parents=True)
    (folder / "0notes.txt").write_text("not a record\n")
    _propagation_record(wiki_vault, "20260101T000000Z", {"old2020": "new2020"})
    _commit(wiki_vault, "an old propagation beside a stray note")
    page = _sealed_citing_page(wiki_vault)
    page.write_text(_REWRITTEN)
    _commit(wiki_vault, "the old rewrite replayed by hand")
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert row.result is Result.UNMATCHED


def test_a_deleted_record_in_history_leaves_the_r41_control_vouched_for(wiki_vault):
    """A deletion's raw line names no new blob (forty zeros); the lookup
    reads no blob for it, so it neither fails nor decides anything."""
    _propagation_record(wiki_vault, "20260101T000000Z", {"old2020": "new2020"})
    _commit(wiki_vault, "an old propagation")
    _git(wiki_vault, "rm", "-q", "system/propagations/20260101T000000Z.json")
    _commit(wiki_vault, "the old record removed")
    _r41_control(wiki_vault)
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert (row.result, row.reason) == (Result.MATCHED, "matched — sealed 1")


def test_the_history_lookups_hold_when_the_worktree_lacks_the_paths(wiki_vault):
    """The hook judges a materialised index while the repository is the real
    checkout, whose worktree may lack system/propagations/ and the record;
    the paths are pathspecs after `--`, never read as revisions."""
    page = _sealed_citing_page(wiki_vault)
    sealing = _git(wiki_vault, "rev-parse", "HEAD")
    recorded = compiled.load_record(wiki_vault)["wiki/sources/A.md"]
    page.write_text(_REWRITTEN)
    _propagation_record(wiki_vault, "20261127T000000Z", {"old2020": "new2020"})
    _commit(wiki_vault, "the rewrite and its record, by hand")
    introduced = _git(wiki_vault, "rev-parse", "HEAD")
    shutil.rmtree(wiki_vault / propagate.RECORD_DIR)
    (wiki_vault / compiled.RECORD_PATH).unlink()
    judge = compiled._Local(wiki_vault)
    assert judge._introduced("20261127T000000Z") == [introduced]
    assert judge._sealing_commit("wiki/sources/A.md", recorded) == sealing


def test_a_record_renamed_into_place_before_the_seal_is_old(wiki_vault):
    """M2 with rename detection off: a record committed as `stash.txt`, then
    moved to its record name, is introduced by the move, which predates the
    seal. Renames detected would read only the old, non-record path."""
    folder = wiki_vault / propagate.RECORD_DIR
    folder.mkdir(parents=True)
    _propagation_record(wiki_vault, "20260101T000000Z", {"old2020": "new2020"})
    (folder / "20260101T000000Z.json").rename(folder / "stash.txt")
    _commit(wiki_vault, "a record under a stray name")
    _git(
        wiki_vault,
        "mv",
        "system/propagations/stash.txt",
        "system/propagations/20260101T000000Z.json",
    )
    _commit(wiki_vault, "the record moved to its name")
    page = _sealed_citing_page(wiki_vault)
    page.write_text(_REWRITTEN)
    _commit(wiki_vault, "the old rewrite replayed by hand")
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert row.result is Result.UNMATCHED


def test_a_record_a_merge_resolution_added_before_the_seal_is_old(wiki_vault):
    """`-m`: a merge diffs against each parent, so a record the resolution
    itself added is introduced by the merge, which predates the seal."""
    (wiki_vault / "inbox" / "base.md").write_text("base\n")
    _commit(wiki_vault, "base")
    main = _branch(wiki_vault)
    _git(wiki_vault, "switch", "-qc", "side")
    (wiki_vault / "inbox" / "side.md").write_text("side\n")
    _commit(wiki_vault, "side")
    _git(wiki_vault, "switch", "-q", main)
    (wiki_vault / "inbox" / "main.md").write_text("main\n")
    _commit(wiki_vault, "main")
    _git(wiki_vault, "merge", "-q", "--no-ff", "--no-commit", "side")
    _propagation_record(wiki_vault, "20260101T000000Z", {"old2020": "new2020"})
    _commit(wiki_vault, "merge, adding an old record")
    page = _sealed_citing_page(wiki_vault)
    page.write_text(_REWRITTEN)
    _commit(wiki_vault, "the old rewrite replayed by hand")
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert row.result is Result.UNMATCHED


def _failing(monkeypatch, which):
    """`gitstate._git` with the call `which(args)` picks replaced by a git
    call that fails, its check flag passed through."""
    real = compiled.gitstate._git

    def failing(repository, *args, **kwargs):
        if which(args):
            return real(repository, "log", "--no-such-option", **kwargs)
        return real(repository, *args, **kwargs)

    monkeypatch.setattr(compiled.gitstate, "_git", failing)


def test_a_failing_record_history_read_never_vouches(wiki_vault, monkeypatch):
    """C10: the introductions log failing is an undecided lookup, a row, not
    a traceback."""
    _r41_control(wiki_vault)
    _failing(monkeypatch, lambda args: "--topo-order" in args)
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert row.result is Result.UNMATCHED


def test_a_failing_record_blob_read_never_vouches(wiki_vault, monkeypatch):
    """C10: a blob batch that fails, answering nothing, is undecided: a row,
    not a traceback."""
    _r41_control(wiki_vault)
    _failing(monkeypatch, lambda args: "cat-file" in args)
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert row.result is Result.UNMATCHED


def test_a_file_named_head_in_an_unborn_repository_is_not_a_commit(wiki_vault):
    """No commit yet, so every record is newer than the seal; `--verify`
    keeps rev-parse from reading a worktree file named HEAD as a path."""
    shutil.rmtree(wiki_vault / ".git")  # the scaffold commits
    _git(wiki_vault, "init", "-q")
    (wiki_vault / "HEAD").write_text("")
    page = _page(
        wiki_vault,
        "wiki/sources/A.md",
        "---\ntype: source\n---\nAs [@old2020, p. 3] shows.\n",
    )
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())})
    compiled.seal(wiki_vault)
    page.write_text(_REWRITTEN)
    _propagation_record(wiki_vault, "20261127T000000Z", {"old2020": "new2020"})
    rows = [o for o in compiled.lint_compiled_layer(wiki_vault) if "A.md" in o.target]
    assert [(o.result, o.reason) for o in rows] == [
        (
            Result.MATCHED,
            (
                "matched — citation keys follow propagation 20261127T000000Z; "
                "run seal wiki/sources/A.md"
            ),
        )
    ]


def test_the_sealing_commit_is_found_whatever_the_user_s_log_format(wiki_vault):
    _git(wiki_vault, "config", "format.pretty", "%s")
    _r41_control(wiki_vault)
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert (row.result, row.reason) == (Result.MATCHED, "matched — sealed 1")


def test_the_entry_s_text_outside_the_record_names_no_sealing_commit(wiki_vault):
    """The `-S` search is limited to the record: a later commit that copies
    the entry's text into another file is not the sealing commit."""
    page = _sealed_citing_page(wiki_vault)
    recorded = compiled.load_record(wiki_vault)["wiki/sources/A.md"]
    _propagation_record(wiki_vault, "20261127T000000Z", {"old2020": "new2020"})
    _commit(wiki_vault, "a record after the seal")
    _page(
        wiki_vault,
        "notes/copy.md",
        json.dumps("wiki/sources/A.md") + ": " + json.dumps(recorded) + "\n",
    )
    _commit(wiki_vault, "the entry's text copied")
    page.write_text(_REWRITTEN)
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert row.result is Result.MATCHED


def test_a_later_record_write_that_keeps_the_entry_is_not_its_sealing_commit(
    wiki_vault,
):
    """The sealing commit is the one that introduced the entry (`-S`), not
    the newest that rewrote the record around it."""
    page = _sealed_citing_page(wiki_vault)
    _propagation_record(wiki_vault, "20261127T000000Z", {"old2020": "new2020"})
    _commit(wiki_vault, "a record after the seal")
    other = _page(wiki_vault, "wiki/sources/B.md", "---\ntype: source\n---\nB\n")
    _journal(
        wiki_vault,
        "op2",
        {"wiki/sources/B.md": _sha(other.read_bytes())},
        epoch=time.time() + 1,
    )
    compiled.seal(wiki_vault, ["wiki/sources/B.md"])
    _commit(wiki_vault, "B sealed")
    page.write_text(_REWRITTEN)
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert row.result is Result.MATCHED


def test_a_failing_sealing_commit_search_never_vouches(wiki_vault, monkeypatch):
    _r41_control(wiki_vault)
    _failing(
        monkeypatch,
        lambda args: any(isinstance(a, bytes) and a.startswith(b"-S") for a in args),
    )
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert row.result is Result.UNMATCHED


def test_a_page_named_outside_ascii_finds_its_sealing_commit(wiki_vault):
    """The record spells names raw (`ensure_ascii=False`), so the search
    must too."""
    page = _page(
        wiki_vault,
        "wiki/sources/Café.md",
        "---\ntype: source\n---\nAs [@old2020, p. 3] shows.\n",
    )
    _journal(wiki_vault, "op1", {"wiki/sources/Café.md": _sha(page.read_bytes())})
    compiled.seal(wiki_vault)
    _commit(wiki_vault)
    page.write_text(_REWRITTEN)
    _propagation_record(wiki_vault, "20261127T000000Z", {"old2020": "new2020"})
    _commit(wiki_vault, "the rewrite and its record, by hand")
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/Café.md"])
    assert (row.result, row.reason) == (Result.MATCHED, "matched — sealed 1")


def test_an_uncommitted_seal_is_newer_than_a_committed_record(wiki_vault):
    """R41: HEAD holds no record entry for the page, so the seal is newer
    than HEAD and the committed record predates it."""
    _propagation_record(wiki_vault, "20260101T000000Z", {"old2020": "new2020"})
    _commit(wiki_vault, "a propagation")
    assert (
        compiled.gitstate.blob_bytes(wiki_vault, "HEAD", compiled.RECORD_PATH) is None
    )
    page = _page(
        wiki_vault,
        "wiki/sources/A.md",
        "---\ntype: source\n---\nAs [@old2020, p. 3] shows.\n",
    )
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())})
    compiled.seal(wiki_vault)
    page.write_text(_REWRITTEN)
    rows = [o for o in compiled.lint_compiled_layer(wiki_vault) if "A.md" in o.target]
    assert [o.result for o in rows] == [Result.UNMATCHED]


def test_sealed_bytes_only_a_merge_resolution_wrote_are_read_from_head(wiki_vault):
    """C7: with the store gone, a merge resolution's reseal is read from HEAD;
    the path's history (`git log --raw`, no `-m`) shows no diff for a merge."""
    page = _page(
        wiki_vault,
        "wiki/sources/A.md",
        "---\ntype: source\n---\nSee [B](/wiki/concepts/B.md).\n",
    )
    target = _page(wiki_vault, "wiki/concepts/B.md", "---\ntype: concept\n---\n")
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())})
    compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    _commit(wiki_vault, "S0")
    main = _branch(wiki_vault)
    _git(wiki_vault, "switch", "-qc", "side")
    (wiki_vault / "inbox" / "side.md").write_text("side\n")
    _commit(wiki_vault, "side")
    _git(wiki_vault, "switch", "-q", main)
    (wiki_vault / "inbox" / "main.md").write_text("main\n")
    _commit(wiki_vault, "main")
    _git(wiki_vault, "merge", "-q", "--no-ff", "--no-commit", "side")
    page.write_text("---\ntype: source\n---\nSee [B](/wiki/concepts/B.md), merged.\n")
    _journal(
        wiki_vault,
        "op2",
        {"wiki/sources/A.md": _sha(page.read_bytes())},
        epoch=time.time() + 1,
    )
    compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    _commit(wiki_vault, "merge: A resealed")
    shutil.rmtree(wiki_vault / compiled.SEALED_STORE)
    target.rename(wiki_vault / "wiki" / "concepts" / "C.md")
    page.write_text("---\ntype: source\n---\nSee [B](/wiki/concepts/C.md), merged.\n")
    rows = [o for o in compiled.lint_compiled_layer(wiki_vault) if "A.md" in o.target]
    assert [o.reason for o in rows] == [
        "matched — link targets follow a rename; run seal wiki/sources/A.md"
    ]


# Survivor triage (Plan C Task 4): the judges' sealed-bytes reads.


def _versions(vault, relative, *bodies):
    """``relative`` committed once per body, oldest first."""
    path = vault / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    for body in bodies:
        path.write_bytes(body)
        _commit(vault, f"{relative} = {body!r}")
    return path


def _empty_base(vault):
    """The re-check's judge over a base snapshot holding nothing, so only the
    path's history can answer."""
    return compiled.snapshot_base(gitstate.Snapshot({}), vault)


def test_the_re_check_reads_a_sealed_blob_from_deep_in_the_path_s_history(
    wiki_vault,
):
    """C7: the log yields v2, v3, then v1, so the oldest blob is the batch's
    last answer and is found only when every earlier one parses."""
    _versions(wiki_vault, "wiki/a.md", b"v1\n", b"v2\n", b"v3\n")
    assert _empty_base(wiki_vault).sealed("wiki/a.md", _sha(b"v1\n")) == b"v1\n"


def test_the_re_check_reads_sealed_bytes_from_the_base_snapshot(tmp_path):
    """C2: a file image in the base whose bytes hash to the entry is the
    sealed copy; any other hash, or no image, falls through to a history
    that (with no `.git`) holds nothing."""
    snapshot = gitstate.Snapshot(
        {b"wiki/a.md": gitstate.FileImage(b"wiki/a.md", "file", 0o100644, b"x")}
    )
    base = compiled.snapshot_base(snapshot, tmp_path)
    assert base.sealed("wiki/a.md", _sha(b"x")) == b"x"
    assert base.sealed("wiki/a.md", _sha(b"y")) is None
    assert base.sealed("wiki/b.md", _sha(b"x")) is None


def test_a_deleted_page_s_history_still_holds_its_sealed_bytes(wiki_vault):
    """A deletion names no new blob (forty zeros), which is never asked of
    the batch; the path, absent from the worktree, is a pathspec after
    `--`."""
    _versions(wiki_vault, "wiki/a.md", b"v1\n", b"v2\n")
    _git(wiki_vault, "rm", "-q", "wiki/a.md")
    _commit(wiki_vault, "wiki/a.md removed")
    assert compiled._history_blob(wiki_vault, "wiki/a.md", _sha(b"v1\n")) == b"v1\n"


def test_an_unborn_repository_has_no_history_and_the_page_differs(wiki_vault):
    """No commit yet: the history read fails and answers nothing, a row,
    not a traceback."""
    shutil.rmtree(wiki_vault / ".git")  # the scaffold commits
    _git(wiki_vault, "init", "-q")
    (wiki_vault / "wiki" / "a.md").write_bytes(b"new\n")
    compiled.write_record(wiki_vault, {"wiki/a.md": _sha(b"old\n")})
    rows = [
        (o.result, o.reason)
        for o in compiled.lint_compiled_layer(wiki_vault)
        if o.target == "path-bytes:wiki/a.md"
    ]
    assert rows == [
        (
            Result.UNMATCHED,
            "drift — wiki/a.md differs from the compiled-page record; "
            + compiled.DIFFERS_REMEDY,
        )
    ]


def test_the_history_read_is_bounded_to_the_path_s_last_commits(
    wiki_vault, monkeypatch
):
    """C7: only the last `HISTORY_BOUND` commits touching the path are read,
    and a commit's old blob counts as well as its new one. A later commit
    touching another page is outside the path's history."""
    monkeypatch.setattr(compiled, "HISTORY_BOUND", 1)
    _versions(wiki_vault, "wiki/a.md", b"v1\n", b"v2\n", b"v3\n")
    _versions(wiki_vault, "wiki/other.md", b"other\n")
    base = _empty_base(wiki_vault)
    assert base.sealed("wiki/a.md", _sha(b"v2\n")) == b"v2\n"
    assert base.sealed("wiki/a.md", _sha(b"v1\n")) is None


def test_the_history_read_holds_when_git_abbreviates_with_an_ellipsis(
    wiki_vault, monkeypatch
):
    """`--no-abbrev`: with GIT_PRINT_SHA1_ELLIPSIS=yes git prints an
    abbreviated oid as `a8116d9...`, which the batch reports missing."""
    monkeypatch.setenv("GIT_PRINT_SHA1_ELLIPSIS", "yes")
    _versions(wiki_vault, "wiki/a.md", b"v1\n", b"v2\n")
    assert _empty_base(wiki_vault).sealed("wiki/a.md", _sha(b"v1\n")) == b"v1\n"


def test_a_gitlink_in_the_path_s_history_ends_the_history_read(wiki_vault):
    """A gitlink may name a commit of this very repository, which the batch
    answers as `commit <size>`: not a blob, so nothing after it is read
    (C10: fail closed), and the older blob is not found."""
    _versions(wiki_vault, "wiki/p.md", b"v1\n")
    own = _git(wiki_vault, "rev-parse", "HEAD")
    _git(wiki_vault, "update-index", "--cacheinfo", f"160000,{own},wiki/p.md")
    _git(wiki_vault, "commit", "-qm", "a gitlink to an own commit", "--no-verify")
    _versions(wiki_vault, "wiki/p.md", b"v3\n")
    assert (
        _git(wiki_vault, "log", "--format=", "--raw", "--", "wiki/p.md").count("160000")
        == 2
    )
    assert _empty_base(wiki_vault).sealed("wiki/p.md", _sha(b"v1\n")) is None


def test_a_record_lookup_holds_when_git_abbreviates_with_an_ellipsis(
    wiki_vault, monkeypatch
):
    """`--no-abbrev`: an abbreviated record blob `a8116d9...` would be
    missing from the batch, an undecided lookup that never vouches."""
    monkeypatch.setenv("GIT_PRINT_SHA1_ELLIPSIS", "yes")
    _r41_control(wiki_vault)
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert (row.result, row.reason) == (Result.MATCHED, "matched — sealed 1")


def test_the_record_lookup_never_reads_a_path_outside_the_records(wiki_vault):
    """The record folder is a pathspec: a name holding \\x01 then a byte
    outside ASCII would split the `-z` log at the commit marker and leave a
    commit id that is not ASCII."""
    try:
        (wiki_vault / "inbox" / os.fsdecode(b"n\x01\xff")).write_bytes(b"n\n")
    except OSError:
        pytest.skip("the filesystem refuses a name that is not UTF-8")
    _commit(wiki_vault, "a stray name")
    _r41_control(wiki_vault)
    (row,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert (row.result, row.reason) == (Result.MATCHED, "matched — sealed 1")


def test_an_operation_no_record_introduced_has_no_commits(wiki_vault):
    _r41_control(wiki_vault)
    assert compiled._Local(wiki_vault)._introduced("20990101T000000Z") == []


def test_only_a_json_object_carrying_an_operation_id_names_one():
    assert compiled._parsed_operation(b'{"schema": 1}') is None
    assert compiled._parsed_operation(b'["operation_id"]') is None
    assert compiled._parsed_operation(b'{"operation_id": 7}') == "7"


def test_a_commit_s_symlinks_and_special_files_in_the_layer_are_its_nodes():
    """`README.md` sorts first and is outside the layer, `wiki/.obsidian`
    sorts before the pages and is excluded: each is skipped, not the end."""

    def image(raw, kind, mode, data):
        return gitstate.FileImage(raw, kind, mode, data)

    snapshot = gitstate.Snapshot(
        {
            b"README.md": image(b"README.md", "file", 0o100644, b""),
            b"wiki/.obsidian": image(b"wiki/.obsidian", "symlink", 0o120000, b"t"),
            b"wiki/a": image(b"wiki/a", "symlink", 0o120000, b"t"),
            b"wiki/b": image(b"wiki/b", "special", 0o160000, None),
        }
    )
    assert compiled._snapshot_nodes(snapshot) == {
        "wiki/a": "symlink",
        "wiki/b": "special",
    }


def test_a_sealed_page_edited_into_bytes_that_are_not_utf8_differs(wiki_vault):
    """The definite tests read both sides as text with `surrogateescape`, so
    a byte that is not UTF-8 is a difference, not a traceback."""
    page = _page(wiki_vault, "wiki/a.md", "---\ntype: source\n---\nok\n")
    _journal(wiki_vault, "op1", {"wiki/a.md": _sha(page.read_bytes())})
    compiled.seal(wiki_vault)
    page.write_bytes(b"---\ntype: source\n---\nok \xff\n")
    rows = [
        (o.result, o.reason)
        for o in compiled.lint_compiled_layer(wiki_vault)
        if o.target == "path-bytes:wiki/a.md"
    ]
    assert rows == [
        (
            Result.UNMATCHED,
            "drift — wiki/a.md differs from the compiled-page record; "
            + compiled.DIFFERS_REMEDY,
        )
    ]


# Survivor triage (Plan C Task 4): journal_hashes, the link-only test, seal,
# the two lints and the record's custody.


def _raw_journal(vault, name, document):
    """A journal written as given, so a test can shape what `_journal` fixes."""
    folder = vault / ".vault-meta" / "transactions" / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "journal.json").write_text(
        document if isinstance(document, str) else json.dumps(document)
    )


def _complete(writes, **fields):
    return {"state": "complete", "writes": writes, **fields}


def _record_bytes(pages):
    """A record's bytes, as HEAD or a carried commit holds them."""
    return json.dumps({"schema": compiled.SCHEMA, "pages": pages}).encode()


def _in_the_c_locale(vault, statement):
    """Run ``statement`` (``compiled`` and ``VAULT`` bound) in a child whose
    locale codec is ASCII: UTF-8 mode off and the C locale left uncoerced
    (not `-I`, which turns UTF-8 mode back on). Any read or write that leaves
    its encoding to the locale fails there on a byte outside ASCII. The
    child prints JSON, so its own stdout stays ASCII."""
    package = str(Path(compiled.__file__).resolve().parents[1])
    path = os.pathsep.join(p for p in (package, os.environ.get("PYTHONPATH")) if p)
    env = {
        **os.environ,
        "LC_ALL": "C",
        "PYTHONCOERCECLOCALE": "0",
        "PYTHONUTF8": "0",
        "PYTHONPATH": path,
    }
    script = (
        "import json, locale\n"
        "from research_vault import compiled\n"
        f"VAULT = {str(vault)!r}\n"
        "assert locale.getencoding() == 'ANSI_X3.4-1968', locale.getencoding()\n"
        f"{statement}\n"
    )
    completed = subprocess.run(
        [sys.executable, "-X", "utf8=0", "-c", script],
        cwd=vault,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout)


def test_journal_hashes_skips_writes_that_name_no_path_or_hash(wiki_vault):
    """A malformed write is skipped, not the end of the journal."""
    _raw_journal(
        wiki_vault,
        "op1",
        _complete(
            [
                "junk",
                {"new_sha256": "a" * 64},
                {"path": "wiki/x.md", "new_sha256": 5},
                {"path": "wiki/a.md", "new_sha256": "b" * 64},
            ],
            created_epoch=1_000,
        ),
    )
    assert compiled.journal_hashes(wiki_vault) == {"wiki/a.md": "b" * 64}


def test_journal_hashes_skips_an_unreadable_or_unfinished_journal(wiki_vault):
    """`0` is not JSON and `a` is only prepared: each is skipped, and the
    complete journal after them still counts."""
    _raw_journal(wiki_vault, "0", "{not json")
    _raw_journal(
        wiki_vault,
        "a",
        {
            "state": "prepared",
            "writes": [{"path": "wiki/p.md", "new_sha256": "p" * 64}],
        },
    )
    _raw_journal(
        wiki_vault, "b", _complete([{"path": "wiki/a.md", "new_sha256": "a" * 64}])
    )
    assert compiled.journal_hashes(wiki_vault) == {"wiki/a.md": "a" * 64}


def test_journal_hashes_takes_the_latest_date_not_the_latest_name(wiki_vault):
    """`a` is dated after `b`, the reverse of their sorted names."""
    _journal(wiki_vault, "a", {"wiki/a.md": "2" * 64}, epoch=2_000)
    _journal(wiki_vault, "b", {"wiki/a.md": "1" * 64}, epoch=1_000)
    assert compiled.journal_hashes(wiki_vault) == {"wiki/a.md": "2" * 64}


def test_journal_hashes_breaks_a_date_tie_by_the_later_name(wiki_vault):
    """Every undated journal ties at 0; the later one in sorted order wins."""
    _journal(wiki_vault, "a", {"wiki/a.md": "1" * 64}, epoch=1_000)
    _journal(wiki_vault, "b", {"wiki/a.md": "2" * 64}, epoch=1_000)
    assert compiled.journal_hashes(wiki_vault) == {"wiki/a.md": "2" * 64}


def test_an_undated_journal_ranks_below_every_dated_one(wiki_vault):
    _raw_journal(
        wiki_vault, "a", _complete([{"path": "wiki/a.md", "new_sha256": "1" * 64}])
    )
    _journal(wiki_vault, "b", {"wiki/a.md": "2" * 64}, epoch=0.5)
    assert compiled.journal_hashes(wiki_vault) == {"wiki/a.md": "2" * 64}


def test_journal_hashes_reads_a_utf8_journal_whatever_the_locale(wiki_vault):
    """The compile tool writes journals with `ensure_ascii=False`, so a page
    name outside ASCII is raw UTF-8 in the file."""
    folder = wiki_vault / ".vault-meta" / "transactions" / "op1"
    folder.mkdir(parents=True)
    (folder / "journal.json").write_bytes(
        json.dumps(
            _complete([{"path": "wiki/Café.md", "new_sha256": "a" * 64}]),
            ensure_ascii=False,
        ).encode("utf-8")
    )
    assert _in_the_c_locale(
        wiki_vault, "print(json.dumps(compiled.journal_hashes(VAULT)))"
    ) == {"wiki/Café.md": "a" * 64}


@pytest.fixture
def link_index(wiki_vault):
    _page(wiki_vault, "wiki/concepts/B.md", "---\ntype: concept\n---\n")
    _page(wiki_vault, "wiki/concepts/C.md", "---\ntype: concept\n---\n")
    return captured.link_index(wiki_vault)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("See [B](/wiki/concepts/B.md).\n", "Saw [B](/wiki/concepts/B.md).\n"),
        ("Xsee [B](/wiki/concepts/B.md).\n", "Ysee [B](/wiki/concepts/B.md).\n"),
        (
            "See [B](/wiki/concepts/B.md).\n",
            "See [B](/wiki/concepts/B.md) and [B](/wiki/concepts/B.md).\n",
        ),
        ("plain\n", "plain\n"),
    ],
    ids=["prose-between", "first-character", "link-count", "no-links"],
)
def test_a_change_outside_the_link_destinations_is_not_link_only(link_index, old, new):
    """Prose that differs, from the very first character; a link added; and
    a text with no links at all, which no rename touched."""
    assert (
        compiled.only_link_targets_changed(old, new, link_index, "wiki/sources/A.md")
        is False
    )


def test_a_nested_json_file_under_the_records_is_no_record():
    assert compiled.is_record_file(b"system/propagations/r.json") is True
    assert compiled.is_record_file(b"system/propagations/sub/r.json") is False


def test_the_record_write_keeps_a_name_outside_ascii_as_text(wiki_vault):
    """`_Local._sealing_commit` searches HEAD's record for the entry as
    `json.dumps(..., ensure_ascii=False)` writes it."""
    compiled.write_record(wiki_vault, {"wiki/Café.md": "a" * 64})
    assert '"wiki/Café.md"' in (wiki_vault / compiled.RECORD_PATH).read_text(
        encoding="utf-8"
    )


def test_a_record_of_another_schema_names_the_schema_in_its_row(wiki_vault):
    """The reason feeds the row's finding id, so it is pinned whole."""
    (wiki_vault / compiled.RECORD_PATH).write_text(
        json.dumps({"schema": "other", "pages": {}})
    )
    (row,) = compiled.lint_compiled_layer(wiki_vault)
    assert row.reason == (
        "schema-violation — compiled-page record unreadable: not a "
        "research-vault.compiled-pages.v1 document"
    )


@pytest.mark.skipif(
    not hasattr(os, "geteuid") or os.geteuid() == 0, reason="root reads any file"
)
def test_a_record_the_os_refuses_to_read_names_the_error_in_its_row(wiki_vault):
    path = compiled.write_record(wiki_vault, {"wiki/a.md": "a" * 64})
    path.chmod(0)
    try:
        (row,) = compiled.lint_compiled_layer(wiki_vault)
    finally:
        path.chmod(0o644)
    assert row.reason.startswith(
        "schema-violation — compiled-page record unreadable: [Errno 13]"
    )


def test_an_unreadable_or_excluded_propagation_record_is_skipped(wiki_vault):
    """`.hidden.json` (excluded) and `0000-broken.json` (not JSON) sort
    before the real record; each is skipped, not the end of the search."""
    page = _sealed_citing_page(wiki_vault)
    page.write_text(_REWRITTEN)
    _propagation_record(wiki_vault, "20261127T000000Z", {"old2020": "new2020"})
    folder = wiki_vault / propagate.RECORD_DIR
    (folder / ".hidden.json").write_text("{not json")
    (folder / "0000-broken.json").write_text("{not json")
    rows = [o for o in compiled.lint_compiled_layer(wiki_vault) if "A.md" in o.target]
    assert [(o.result, o.reason) for o in rows] == [
        (
            Result.MATCHED,
            (
                "matched — citation keys follow propagation 20261127T000000Z; "
                "run seal wiki/sources/A.md"
            ),
        )
    ]


def test_lint_reads_past_a_symlinked_folder_s_entries_to_an_absent_page(
    wiki_vault, tmp_path_factory
):
    outside = tmp_path_factory.mktemp("outside")
    (wiki_vault / "wiki" / "link").symlink_to(outside, target_is_directory=True)
    compiled.write_record(
        wiki_vault, {"wiki/link/x.md": "a" * 64, "wiki/z.md": "b" * 64}
    )
    assert compiled.lint_compiled_layer(wiki_vault) == [
        compiled._not_a_file("wiki/link", "symlink"),
        compiled._absent("wiki/z.md"),
    ]


def test_lint_drops_only_the_entry_the_tool_deleted(wiki_vault):
    """`a` has a journal delete and files no row; `b`, after it, has none."""
    compiled.write_record(wiki_vault, {"wiki/a.md": "a" * 64, "wiki/b.md": "b" * 64})
    _journal(wiki_vault, "op1", {"wiki/a.md": None})
    assert compiled.lint_compiled_layer(wiki_vault) == [compiled._absent("wiki/b.md")]


def test_lint_reads_past_a_rename_reseal_to_the_next_page(wiki_vault):
    """The MATCHED note for `A.md` is not the end: `Z.md`, unsealed, still
    files its row."""
    page = _page(
        wiki_vault,
        "wiki/sources/A.md",
        "---\ntype: source\n---\nSee [B](/wiki/concepts/B.md).\n",
    )
    target = _page(wiki_vault, "wiki/concepts/B.md", "---\ntype: concept\n---\n")
    _journal(
        wiki_vault,
        "op1",
        {
            "wiki/sources/A.md": _sha(page.read_bytes()),
            "wiki/concepts/B.md": _sha(target.read_bytes()),
        },
    )
    compiled.seal(wiki_vault)
    _commit(wiki_vault)
    target.rename(wiki_vault / "wiki" / "concepts" / "C.md")
    page.write_text("---\ntype: source\n---\nSee [B](/wiki/concepts/C.md).\n")
    _page(wiki_vault, "wiki/sources/Z.md", "---\ntype: source\n---\nby hand\n")
    rows = compiled.lint_compiled_layer(wiki_vault, journal=False)
    assert [(o.target, o.result) for o in rows] == [
        ("path-bytes:wiki/concepts/C.md", Result.UNMATCHED),
        ("path-bytes:wiki/sources/A.md", Result.MATCHED),
        ("path-bytes:wiki/sources/Z.md", Result.UNMATCHED),
        ("path-bytes:wiki/concepts/B.md", Result.UNMATCHED),
    ]


def test_seal_refuses_a_recorded_page_that_is_absent_and_keeps_its_entry(
    wiki_vault,
):
    compiled.write_record(wiki_vault, {"wiki/a.md": "a" * 64})
    assert compiled.seal(wiki_vault) == [compiled._absent("wiki/a.md")]
    assert compiled.load_record(wiki_vault) == {"wiki/a.md": "a" * 64}


def test_seal_counts_every_entry_the_tool_deleted(wiki_vault):
    compiled.write_record(wiki_vault, {"wiki/a.md": "a" * 64, "wiki/b.md": "b" * 64})
    _journal(wiki_vault, "op1", {"wiki/a.md": None, "wiki/b.md": None})
    assert compiled.seal(wiki_vault) == [
        compiled.Outcome(
            compiled.CHECK, compiled.RECORD_PATH, Result.MATCHED, "matched — sealed 2"
        )
    ]
    assert compiled.load_record(wiki_vault) == {}


def test_seal_reads_past_its_refusals_to_the_next_page(wiki_vault):
    """`0.md` is recorded but absent and `1.md` is unsealed; each is refused,
    and `z.md` after them is still sealed."""
    compiled.write_record(wiki_vault, {"wiki/0.md": "0" * 64})
    _page(wiki_vault, "wiki/1.md", "---\ntype: source\n---\nby hand\n")
    page = _page(wiki_vault, "wiki/z.md", "---\ntype: source\n---\nz\n")
    _journal(wiki_vault, "op1", {"wiki/z.md": _sha(page.read_bytes())})
    assert [o.target for o in compiled.seal(wiki_vault)] == [
        "path-bytes:wiki/0.md",
        "path-bytes:wiki/1.md",
    ]
    assert compiled.load_record(wiki_vault) == {
        "wiki/0.md": "0" * 64,
        "wiki/z.md": _sha(page.read_bytes()),
    }


def test_seal_stores_a_page_sealed_before_the_store_existed(wiki_vault):
    """C7's back-fill: an entry already equal to the page's bytes."""
    page = _page(wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\nA\n")
    data = page.read_bytes()
    compiled.write_record(wiki_vault, {"wiki/sources/A.md": _sha(data)})
    assert compiled.stored_bytes(wiki_vault, _sha(data)) is None
    compiled.seal(wiki_vault)
    assert compiled.stored_bytes(wiki_vault, _sha(data)) == data


def test_seal_takes_a_named_path_with_its_slashes_stripped(wiki_vault):
    page = _page(wiki_vault, "wiki/sources/X", "x\n")
    _journal(wiki_vault, "op1", {"wiki/sources/X": _sha(page.read_bytes())})
    (row,) = compiled.seal(wiki_vault, ["/wiki/sources/X"])
    assert row.reason == "matched — sealed 1"
    assert compiled.load_record(wiki_vault) == {"wiki/sources/X": _sha(b"x\n")}


def test_seal_reads_journals_from_the_repository_root_it_is_given(wiki_vault):
    page = _page(wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\nA\n")
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())})
    (row,) = compiled.seal(wiki_vault, repository_root=wiki_vault)
    assert row.reason == "matched — sealed 1"


def test_seal_names_the_yaml_error_in_its_refusal(wiki_vault):
    """The reason feeds the row's finding id, so it is pinned whole."""
    page = _page(wiki_vault, "wiki/sources/C.md", "---\ntitle: A: B\n---\nx\n")
    _journal(wiki_vault, "op1", {"wiki/sources/C.md": _sha(page.read_bytes())})
    (row,) = compiled.seal(wiki_vault)
    assert row.reason == (
        "schema-violation — wiki/sources/C.md: frontmatter is not valid YAML "
        "(frontmatter is not valid YAML: mapping values are not allowed in this "
        "context (line 2, column 9))"
    )


def test_seal_normalises_a_page_whose_bytes_are_not_utf8(wiki_vault):
    """The stray byte rides through the link rewrite and back to disk."""
    page = wiki_vault / "wiki" / "sources" / "A.md"
    page.parent.mkdir(parents=True)
    page.write_bytes(b"---\ntype: source\n---\nSee [[B]] \xff.\n")
    target = _page(wiki_vault, "wiki/concepts/B.md", "---\ntype: concept\n---\n")
    _journal(
        wiki_vault,
        "op1",
        {
            "wiki/sources/A.md": _sha(page.read_bytes()),
            "wiki/concepts/B.md": _sha(target.read_bytes()),
        },
    )
    (row,) = compiled.seal(wiki_vault)
    assert row.reason == "matched — sealed 2"
    normalised = b"---\ntype: source\n---\nSee [B](/wiki/concepts/B.md) \xff.\n"
    assert page.read_bytes() == normalised
    assert compiled.load_record(wiki_vault)["wiki/sources/A.md"] == _sha(normalised)


def test_seal_writes_a_normalised_page_as_utf8_whatever_the_locale(wiki_vault):
    page = wiki_vault / "wiki" / "sources" / "A.md"
    page.parent.mkdir(parents=True)
    page.write_bytes("---\ntype: source\n---\nCafé [[B]].\n".encode())
    target = _page(wiki_vault, "wiki/concepts/B.md", "---\ntype: concept\n---\n")
    _journal(
        wiki_vault,
        "op1",
        {
            "wiki/sources/A.md": _sha(page.read_bytes()),
            "wiki/concepts/B.md": _sha(target.read_bytes()),
        },
    )
    assert _in_the_c_locale(
        wiki_vault, "print(json.dumps([o.reason for o in compiled.seal(VAULT)]))"
    ) == ["matched — sealed 2"]
    assert page.read_bytes() == (
        "---\ntype: source\n---\nCafé [B](/wiki/concepts/B.md).\n".encode()
    )


def test_custody_reads_past_carried_records_that_hold_nothing(wiki_vault):
    """A missing and an unreadable carried record carry nothing; the good
    one after them justifies `a`'s entry, and `b`, after `a`, is judged."""
    compiled.write_record(wiki_vault, {"wiki/a.md": "b" * 64, "wiki/b.md": "c" * 64})
    rows = compiled.lint_record_custody(
        wiki_vault,
        _record_bytes({"wiki/a.md": "a" * 64}),
        carried=[None, b"{not json", _record_bytes({"wiki/a.md": "b" * 64})],
    )
    assert [o.target for o in rows] == ["path-bytes:wiki/b.md"]


def test_custody_reads_past_entries_a_journal_or_the_store_justifies(wiki_vault):
    data = b"stored\n"
    compiled._store(wiki_vault, data)
    _journal(wiki_vault, "op1", {"wiki/a.md": "a" * 64})
    compiled.write_record(
        wiki_vault,
        {"wiki/a.md": "a" * 64, "wiki/b.md": _sha(data), "wiki/c.md": "c" * 64},
    )
    rows = compiled.lint_record_custody(wiki_vault, None)
    assert [o.target for o in rows] == ["path-bytes:wiki/c.md"]


def test_custody_reads_past_a_rename_reseal_to_the_next_entry(wiki_vault):
    (wiki_vault / "inbox" / "B.md").write_text("B\n")
    page = _committed_page(wiki_vault, "See [B](/inbox/B.md).")
    (wiki_vault / "inbox" / "B.md").rename(wiki_vault / "inbox" / "C.md")
    page.write_text(_CONCEPT.format("A", "See [B](/inbox/C.md)."))
    compiled.seal(wiki_vault, ["wiki/concepts/A.md"])
    shutil.rmtree(wiki_vault / compiled.SEALED_STORE)
    record = compiled.load_record(wiki_vault)
    compiled.write_record(wiki_vault, {**record, "wiki/concepts/Z.md": "z" * 64})
    head = _git(wiki_vault, "show", f"HEAD:{compiled.RECORD_PATH}").encode()
    rows = compiled.lint_record_custody(wiki_vault, head)
    assert [o.target for o in rows] == ["path-bytes:wiki/concepts/Z.md"]


def test_an_unreadable_head_record_counts_as_empty(wiki_vault):
    compiled.write_record(wiki_vault, {"wiki/a.md": "a" * 64})
    rows = compiled.lint_record_custody(wiki_vault, b"{not json")
    assert [o.reason.split(";")[0] for o in rows] == [
        (
            "drift — wiki/a.md's record entry was added with no compile, "
            "rename or seal behind it"
        )
    ]


def test_custody_judges_each_removed_entry_on_its_own(wiki_vault):
    """`a` was deleted by the compile tool and `b` is absent from a carried
    record too, so neither files a row; `c`, removed with neither behind
    it, does."""
    compiled.write_record(wiki_vault, {})
    _journal(wiki_vault, "op1", {"wiki/a.md": None})
    head = _record_bytes(
        {"wiki/a.md": "a" * 64, "wiki/b.md": "b" * 64, "wiki/c.md": "c" * 64}
    )
    rows = compiled.lint_record_custody(
        wiki_vault, head, carried=[_record_bytes({"wiki/c.md": "c" * 64})]
    )
    assert [(o.target, o.reason) for o in rows] == [
        (
            "path-bytes:wiki/c.md",
            (
                "drift — wiki/c.md's record entry was removed with no compile "
                "delete behind it; restore the entry, or acknowledge"
            ),
        )
    ]


def test_custody_judges_a_rename_without_the_seal_store(wiki_vault):
    """W3: the store holds the page's old bytes and git does not, so the
    index leg, which reads no store, cannot see the rename and holds."""
    old = b"---\ntype: source\n---\nSee [B](/wiki/concepts/B.md).\n"
    new = b"---\ntype: source\n---\nSee [B](/wiki/concepts/C.md).\n"
    page = wiki_vault / "wiki" / "sources" / "A.md"
    page.parent.mkdir(parents=True)
    page.write_bytes(new)
    _page(wiki_vault, "wiki/concepts/C.md", "---\ntype: concept\n---\n")
    compiled._store(wiki_vault, old)
    compiled.write_record(wiki_vault, {"wiki/sources/A.md": _sha(new)})
    rows = compiled.lint_record_custody(
        wiki_vault, _record_bytes({"wiki/sources/A.md": _sha(old)})
    )
    assert [o.target for o in rows] == ["path-bytes:wiki/sources/A.md"]


# Final-review fix wave (W2, W3, W6, W8).


def test_a_deleted_wiki_lists_every_recorded_page_absent(wiki_vault):
    """W2: with the record still listing pages, a vault with no `wiki/` has
    a compiled layer: each recorded entry is `recorded but absent`."""
    page = _page(wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\n")
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())})
    compiled.seal(wiki_vault)
    shutil.rmtree(wiki_vault / "wiki")
    assert [
        (o.result, o.target, o.reason) for o in compiled.lint_compiled_layer(wiki_vault)
    ] == [
        (
            Result.UNMATCHED,
            "path-bytes:wiki/sources/A.md",
            "drift — wiki/sources/A.md is recorded but absent; restore it, or acknowledge (a row stamped with a commit clears only by acknowledgement)",
        )
    ]


_WIKI_NOT_A_FILE = (
    Result.UNMATCHED,
    "path-bytes:wiki",
    (
        "drift — wiki is not a regular file; a compiled page is a file"
        ": replace it with the file itself, or acknowledge (a row stamped with a commit clears only by acknowledgement)"
    ),
)


def test_a_fifo_wiki_is_one_row_and_seal_refuses_the_node(wiki_vault):
    """W2: a non-directory `wiki` is a not-a-file row, in the lint and at
    seal, whose refusal names the node rather than each entry behind it."""
    page = _page(wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\n")
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())})
    compiled.seal(wiki_vault)
    shutil.rmtree(wiki_vault / "wiki")
    os.mkfifo(wiki_vault / "wiki")
    assert [
        (o.result, o.target, o.reason) for o in compiled.lint_compiled_layer(wiki_vault)
    ] == [_WIKI_NOT_A_FILE]
    assert [(o.result, o.target, o.reason) for o in compiled.seal(wiki_vault)] == [
        _WIKI_NOT_A_FILE
    ]
    assert list(compiled.load_record(wiki_vault)) == ["wiki/sources/A.md"]


def test_no_wiki_and_an_empty_record_is_skipped(wiki_vault):
    shutil.rmtree(wiki_vault / "wiki")
    compiled.write_record(wiki_vault, {})
    assert [o.result for o in compiled.lint_compiled_layer(wiki_vault)] == [
        Result.SKIPPED
    ]


def test_the_index_and_head_judges_never_read_the_seal_store(wiki_vault):
    """W3: the store is local and untracked, so CI and the replay cannot see
    it; with journal=False (the hook's index, CI's HEAD) the judge reads
    only bytes git reaches, so the hook holds what CI would hold."""
    page = _page(
        wiki_vault,
        "wiki/sources/A.md",
        "---\ntype: source\n---\nSee [B](/wiki/concepts/B.md).\n",
    )
    target = _page(wiki_vault, "wiki/concepts/B.md", "---\ntype: concept\n---\n")
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())})
    compiled.seal(wiki_vault, ["wiki/sources/A.md"])  # uncommitted
    target.rename(wiki_vault / "wiki" / "concepts" / "C.md")
    page.write_text("---\ntype: source\n---\nSee [B](/wiki/concepts/C.md).\n")

    def a_rows(**kwargs):
        return [
            o.result
            for o in compiled.lint_compiled_layer(wiki_vault, **kwargs)
            if o.target == "path-bytes:wiki/sources/A.md"
        ]

    assert a_rows() == [Result.MATCHED]
    assert a_rows(journal=False) == [Result.UNMATCHED]
    (sealed,) = compiled.seal(wiki_vault, ["wiki/sources/A.md"])
    assert sealed.result is Result.MATCHED
    assert a_rows() == a_rows(journal=False) == []


def test_an_operation_id_that_is_not_text_never_reaches_the_reason(wiki_vault):
    """W6: a lone surrogate in a record's id would crash the strict write."""
    page = _sealed_citing_page(wiki_vault)
    page.write_text("---\ntype: source\n---\nAs [@new2020, p. 3] shows.\n")
    folder = wiki_vault / propagate.RECORD_DIR
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "20261127T000000Z.json").write_text(
        json.dumps(
            {
                "schema": propagate.SCHEMA,
                "operation_id": "\udcff",
                "date": "2026-11-27",
                "mapping": {"old2020": "new2020"},
                "item_keys": {"old2020": "E352DFS8"},
                "merges": {},
                "removes": {},
                "surfaces": [],
            }
        )
    )
    rows = [o for o in compiled.lint_compiled_layer(wiki_vault) if "A.md" in o.target]
    assert [(o.result, o.reason) for o in rows] == [
        (
            Result.MATCHED,
            (
                "matched — citation keys follow a propagation record; "
                "run seal wiki/sources/A.md"
            ),
        )
    ]
    rows[0].reason.encode("utf-8")


def test_the_record_write_is_atomic(wiki_vault, monkeypatch):
    """W8: a write interrupted before its rename leaves the old record."""
    compiled.write_record(wiki_vault, {"wiki/a.md": "1" * 64})
    before = (wiki_vault / compiled.RECORD_PATH).read_bytes()

    def interrupted(*_args, **_kwargs):
        raise OSError("interrupted")

    monkeypatch.setattr(compiled.os, "replace", interrupted)
    with pytest.raises(OSError, match="interrupted"):
        compiled.write_record(wiki_vault, {"wiki/b.md": "2" * 64})
    assert (wiki_vault / compiled.RECORD_PATH).read_bytes() == before
    assert sorted(p.name for p in (wiki_vault / "system").iterdir()) == sorted(
        p.name for p in (wiki_vault / "system").iterdir() if not p.name.startswith(".")
    )


def test_the_record_write_creates_the_folders_it_needs(tmp_path):
    """`write_record` is exported: a caller may write into a vault that has
    no `system/` yet, nor the vault folder itself."""
    path = compiled.write_record(tmp_path / "new-vault", {"wiki/a.md": "1" * 64})
    assert path == tmp_path / "new-vault" / compiled.RECORD_PATH
    assert compiled.load_record(tmp_path / "new-vault") == {"wiki/a.md": "1" * 64}


def test_seal_writes_the_record_before_the_pages_and_a_rerun_accepts_them(
    wiki_vault, monkeypatch
):
    """W8: seal computes every normalised page first and writes the record
    before any page; an interruption between the two leaves pages the
    journal still vouches for, so a rerun seals them."""
    page = _page(
        wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\nSee [[B]].\n"
    )
    target = _page(wiki_vault, "wiki/concepts/B.md", "---\ntype: concept\n---\n")
    _journal(
        wiki_vault,
        "op1",
        {
            "wiki/sources/A.md": _sha(page.read_bytes()),
            "wiki/concepts/B.md": _sha(target.read_bytes()),
        },
    )
    written = page.read_bytes()
    real = compiled.write_record

    def interrupted(*_args, **_kwargs):
        raise OSError("interrupted")

    monkeypatch.setattr(compiled, "write_record", interrupted)
    with pytest.raises(OSError, match="interrupted"):
        compiled.seal(wiki_vault)
    assert page.read_bytes() == written  # no page rewritten before the record
    monkeypatch.setattr(compiled, "write_record", real)

    def interrupted_page(self, *_args, **_kwargs):
        raise OSError("interrupted")

    monkeypatch.setattr(compiled.Path, "write_text", interrupted_page)
    with pytest.raises(OSError, match="interrupted"):
        compiled.seal(wiki_vault)
    monkeypatch.undo()
    assert page.read_bytes() == written
    assert [
        o.result
        for o in compiled.lint_compiled_layer(wiki_vault)
        if o.target.endswith("A.md")
    ] == []
    (row,) = compiled.seal(wiki_vault)
    assert row.result is Result.MATCHED
    assert page.read_text() == "---\ntype: source\n---\nSee [B](/wiki/concepts/B.md).\n"
    assert compiled.load_record(wiki_vault)["wiki/sources/A.md"] == _sha(
        page.read_bytes()
    )


# R44 (W17): the hook's custody of the record itself, on the index.

_CONCEPT = '---\ntitle: "{0}"\ntype: "concept"\nstatus: "draft"\n---\n{1}\n'


def _hook(vault):
    """The pre-commit hook's verify over the staged index: its exit code."""
    import research_vault.__main__ as cli

    subprocess.run(["git", "add", "-A"], cwd=vault, check=True)
    return cli.main(
        [
            "verify",
            "--vault",
            str(vault),
            "--offline",
            "--surface",
            "commit",
            "--git-candidate",
            "index",
        ]
    )


def _committed_page(vault, body="body"):
    page = _page(vault, "wiki/concepts/A.md", _CONCEPT.format("A", body))
    _journal(vault, "op1", {"wiki/concepts/A.md": _sha(page.read_bytes())})
    compiled.seal(vault)
    _commit(vault)
    return page


def test_a_page_co_edited_with_its_entry_holds_the_hook(wiki_vault, capsys):
    page = _committed_page(wiki_vault)
    page.write_text(_CONCEPT.format("A", "edited by an interpreter"))
    record = compiled.load_record(wiki_vault)
    record["wiki/concepts/A.md"] = _sha(page.read_bytes())
    compiled.write_record(wiki_vault, record)
    assert _hook(wiki_vault) == 1
    assert (
        "drift — wiki/concepts/A.md's record entry changed with no compile, "
        "rename or seal behind it; restore the entry, rewrite the page through "
        "the compile tool and seal, or acknowledge"
    ) in capsys.readouterr().out


def test_an_entry_added_or_removed_by_hand_holds_the_hook(wiki_vault):
    page = _committed_page(wiki_vault)
    _page(wiki_vault, "wiki/concepts/B.md", _CONCEPT.format("B", "by hand"))
    record = compiled.load_record(wiki_vault)
    record["wiki/concepts/B.md"] = _sha(
        (wiki_vault / "wiki/concepts/B.md").read_bytes()
    )
    compiled.write_record(wiki_vault, record)
    subprocess.run(["git", "add", "-A"], cwd=wiki_vault, check=True)
    rows = compiled.lint_record_custody(
        wiki_vault,
        subprocess.run(
            ["git", "show", f"HEAD:{compiled.RECORD_PATH}"],
            cwd=wiki_vault,
            check=True,
            capture_output=True,
        ).stdout,
    )
    assert [(o.target, o.reason.split(";")[0]) for o in rows] == [
        (
            "path-bytes:wiki/concepts/B.md",
            (
                "drift — wiki/concepts/B.md's record entry was added with no "
                "compile, rename or seal behind it"
            ),
        )
    ]
    page.unlink()
    del record["wiki/concepts/A.md"]
    compiled.write_record(wiki_vault, record)
    head = subprocess.run(
        ["git", "show", f"HEAD:{compiled.RECORD_PATH}"],
        cwd=wiki_vault,
        check=True,
        capture_output=True,
    ).stdout
    assert [
        (o.target, o.reason) for o in compiled.lint_record_custody(wiki_vault, head)
    ][-1] == (
        "path-bytes:wiki/concepts/A.md",
        (
            "drift — wiki/concepts/A.md's record entry was removed with no "
            "compile delete behind it; restore the entry, or acknowledge"
        ),
    )
    _journal(wiki_vault, "op2", {"wiki/concepts/A.md": None})
    assert [o.target for o in compiled.lint_record_custody(wiki_vault, head)] == [
        "path-bytes:wiki/concepts/B.md"
    ]


def test_a_compile_then_seal_passes_the_hook(wiki_vault):
    page = _committed_page(wiki_vault)
    page.write_text(_CONCEPT.format("A", "recompiled"))
    _journal(wiki_vault, "op2", {"wiki/concepts/A.md": _sha(page.read_bytes())})
    (row,) = compiled.seal(wiki_vault)
    assert row.result is Result.MATCHED
    assert _hook(wiki_vault) == 0


def test_a_rename_reseal_passes_the_hook_without_the_store(wiki_vault):
    """The entry's change is a rename's link change from HEAD's entry, so
    the witness justifies it even when the local store is gone."""
    (wiki_vault / "inbox" / "B.md").write_text("B\n")
    page = _committed_page(wiki_vault, "See [B](/inbox/B.md).")
    (wiki_vault / "inbox" / "B.md").rename(wiki_vault / "inbox" / "C.md")
    page.write_text(_CONCEPT.format("A", "See [B](/inbox/C.md)."))
    (row,) = compiled.seal(wiki_vault, ["wiki/concepts/A.md"])
    assert row.result is Result.MATCHED
    shutil.rmtree(wiki_vault / compiled.SEALED_STORE)
    assert _hook(wiki_vault) == 0


def test_an_uncommitted_seal_then_a_rename_holds_the_hook_until_seal(wiki_vault):
    """W3 on the index: the hook reads no store, so it holds the page CI
    would hold; after `seal` both legs are clean."""
    (wiki_vault / "inbox" / "B.md").write_text("B\n")
    _commit(wiki_vault, "B")
    page = _page(
        wiki_vault, "wiki/concepts/A.md", _CONCEPT.format("A", "See [B](/inbox/B.md).")
    )
    _journal(wiki_vault, "op1", {"wiki/concepts/A.md": _sha(page.read_bytes())})
    compiled.seal(wiki_vault)  # not committed
    (wiki_vault / "inbox" / "B.md").rename(wiki_vault / "inbox" / "C.md")
    page.write_text(_CONCEPT.format("A", "See [B](/inbox/C.md)."))
    assert _hook(wiki_vault) == 1
    (row,) = compiled.seal(wiki_vault, ["wiki/concepts/A.md"])
    assert row.result is Result.MATCHED
    assert _hook(wiki_vault) == 0
    _commit(wiki_vault, "renamed and resealed")
    from research_vault import verify

    for candidate in ("worktree", "HEAD"):
        _report, effective, _hashes, _warning = verify.verify_state(
            wiki_vault, network=False, git_candidate=candidate
        )
        assert not [
            o
            for o in effective
            if o.check == compiled.CHECK and o.result is Result.UNMATCHED
        ], candidate


def test_a_plain_file_named_wiki_is_not_a_directory(wiki_vault):
    page = _page(wiki_vault, "wiki/sources/A.md", "---\ntype: source\n---\n")
    _journal(wiki_vault, "op1", {"wiki/sources/A.md": _sha(page.read_bytes())})
    compiled.seal(wiki_vault)
    shutil.rmtree(wiki_vault / "wiki")
    (wiki_vault / "wiki").write_text("not a folder\n")
    assert [
        (o.result, o.target, o.reason) for o in compiled.lint_compiled_layer(wiki_vault)
    ] == [
        (
            Result.UNMATCHED,
            "path-bytes:wiki",
            (
                "drift — wiki is not a directory; the compiled layer is a folder: "
                "replace it with the folder, or acknowledge (a row stamped with a "
                "commit clears only by acknowledgement)"
            ),
        )
    ]


def test_a_normalised_seal_is_vouched_for_only_by_the_store(wiki_vault):
    """R45's question (a): seal records the hash of the normalised bytes,
    which no journal names and which HEAD never held, so on the index only
    the seal store vouches for the entry; without it the hook holds."""
    (wiki_vault / "inbox" / "B.md").write_text("B\n")
    _commit(wiki_vault, "B")
    page = _page(wiki_vault, "wiki/concepts/A.md", _CONCEPT.format("A", "See [[B]]."))
    _journal(wiki_vault, "op1", {"wiki/concepts/A.md": _sha(page.read_bytes())})
    (row,) = compiled.seal(wiki_vault)
    assert row.result is Result.MATCHED
    assert "[[B]]" not in page.read_text()  # normalised
    assert _hook(wiki_vault) == 0
    shutil.rmtree(wiki_vault / compiled.SEALED_STORE)
    assert _hook(wiki_vault) == 1


def test_a_reseal_chain_between_commits_passes_the_hook(wiki_vault):
    """R45's question (b): compile and seal, then a rename and its reseal,
    with no commit between; only the store holds the intermediate seal."""
    (wiki_vault / "inbox" / "B.md").write_text("B\n")
    page = _committed_page(wiki_vault, "See [B](/inbox/B.md). v1")
    page.write_text(_CONCEPT.format("A", "See [B](/inbox/B.md). v2"))
    _journal(
        wiki_vault,
        "op2",
        {"wiki/concepts/A.md": _sha(page.read_bytes())},
        epoch=time.time() + 10,
    )
    compiled.seal(wiki_vault)
    (wiki_vault / "inbox" / "B.md").rename(wiki_vault / "inbox" / "C.md")
    page.write_text(_CONCEPT.format("A", "See [B](/inbox/C.md). v2"))
    (row,) = compiled.seal(wiki_vault, ["wiki/concepts/A.md"])
    assert row.result is Result.MATCHED
    assert _hook(wiki_vault) == 0
    shutil.rmtree(wiki_vault / compiled.SEALED_STORE)
    assert _hook(wiki_vault) == 1


# C14: a merge, cherry-pick or revert carries entries judged where they were made.


def _branch(vault):
    return subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=vault,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _sealed_on(vault, relative, body, message):
    page = _page(vault, relative, _CONCEPT.format(relative, body))
    _journal(vault, message, {relative: _sha(page.read_bytes())})
    (row,) = compiled.seal(vault, [relative])
    assert row.result is Result.MATCHED
    _commit(vault, message)
    return page


def _diverged(vault):
    """Clone A sealed a.md on branch `other`; this clone sealed b.md. Each
    clone's local evidence is its own, so this one keeps none of A's."""
    compiled.write_record(vault, {})
    _commit(vault, "empty record")
    main = _branch(vault)
    subprocess.run(["git", "checkout", "-qb", "other"], cwd=vault, check=True)
    _sealed_on(vault, "wiki/concepts/a.md", "A", "seal a")
    subprocess.run(["git", "checkout", "-q", main], cwd=vault, check=True)
    _sealed_on(vault, "wiki/concepts/b.md", "B", "seal b")
    shutil.rmtree(vault / ".vault-meta")


def _resolve_union(vault):
    """The person's resolution of the conflicted record: both entries."""
    pages = {}
    for relative in ("wiki/concepts/a.md", "wiki/concepts/b.md"):
        pages[relative] = _sha((vault / relative).read_bytes())
    compiled.write_record(vault, pages)


def _conflicts(vault, *args):
    result = subprocess.run(
        ["git", *args], cwd=vault, capture_output=True, text=True, check=False
    )
    assert result.returncode != 0, result.stdout
    assert "compiled-pages.json" in result.stdout + result.stderr


def test_a_resolved_merge_taking_the_other_side_s_entry_passes_the_hook(wiki_vault):
    _diverged(wiki_vault)
    _conflicts(wiki_vault, "merge", "-q", "--no-edit", "other")
    _resolve_union(wiki_vault)
    assert _hook(wiki_vault) == 0


def test_a_resolved_cherry_pick_passes_the_hook(wiki_vault):
    _diverged(wiki_vault)
    _conflicts(wiki_vault, "cherry-pick", "other")
    _resolve_union(wiki_vault)
    assert _hook(wiki_vault) == 0


def test_a_hand_co_edit_during_a_merge_still_holds_the_hook(wiki_vault):
    _diverged(wiki_vault)
    _conflicts(wiki_vault, "merge", "-q", "--no-edit", "other")
    page = wiki_vault / "wiki" / "concepts" / "a.md"
    page.write_text(page.read_text() + "by hand\n")
    _resolve_union(wiki_vault)
    assert _hook(wiki_vault) == 1


def test_an_entry_checked_out_from_another_branch_is_a_hold(wiki_vault):
    """C14: with no merge, cherry-pick or revert in progress, an entry taken
    from another branch has nothing behind it: the commit waits for an
    acknowledgement."""
    _diverged(wiki_vault)
    subprocess.run(
        ["git", "checkout", "other", "--", "wiki/concepts/a.md"],
        cwd=wiki_vault,
        check=True,
    )
    _resolve_union(wiki_vault)
    assert _hook(wiki_vault) == 1
