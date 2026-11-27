import hashlib
import json
import os
import shutil
import subprocess
import time

import pytest

from research_vault import Result, compiled, propagate, scaffold


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
                "; write it through the compile tool and seal, remove it, or acknowledge"
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
            "; revert it to the sealed bytes, rewrite it through the compile tool and seal, or acknowledge"
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
            "drift — wiki/sources/A.md is recorded but absent; restore it, or acknowledge",
        ),
        (
            "path-bytes:wiki/sources/New.md",
            (
                "drift — wiki/sources/New.md is not sealed: no complete compile wrote these bytes"
                "; write it through the compile tool and seal, remove it, or acknowledge"
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
        "; revert it to the sealed bytes, rewrite it through the compile tool and seal, or acknowledge"
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
        "rename it to UTF-8 text, remove it, or acknowledge"
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
                ": replace it with the file itself, or acknowledge"
            ),
        ),
        (
            Result.UNMATCHED,
            "path-bytes:wiki/linked.md",
            (
                "drift — wiki/linked.md is a symlink; a compiled page is a file"
                ": replace it with the file itself, or acknowledge"
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
                ": replace it with the file itself, or acknowledge"
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
                ": replace it with the file itself, or acknowledge"
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
