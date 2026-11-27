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
            "drift — wiki/sources/A.md is not sealed: no complete compile wrote these bytes",
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
        "drift — wiki/sources/A.md differs from the compiled-page record; seal or acknowledge",
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
            "drift — wiki/sources/A.md is recorded but absent",
        ),
        (
            "path-bytes:wiki/sources/New.md",
            "drift — wiki/sources/New.md is not sealed: no complete compile wrote these bytes",
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
            "matched — link targets follow a rename; reseal",
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
            "matched — citation keys follow propagation 20261127T000000Z; reseal",
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
        "drift — wiki/sources/A.md is not sealed: no complete compile wrote these bytes"
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
    (row,) = compiled.lint_compiled_layer(wiki_vault)
    assert (row.result, row.target) == (Result.UNMATCHED, "path-bytes:wiki/caf%E9.md")
    row.reason.encode("utf-8")
    (row,) = compiled.seal(wiki_vault)
    assert (row.result, row.target) == (Result.UNMATCHED, "path-bytes:wiki/caf%E9.md")
    row.reason.encode("utf-8")
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
        "matched — link targets follow a rename; reseal"
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
            "drift — wiki/folder is a symlink; a compiled page is a file",
        ),
        (
            Result.UNMATCHED,
            "path-bytes:wiki/linked.md",
            "drift — wiki/linked.md is a symlink; a compiled page is a file",
        ),
    ]
    assert sorted(o.target for o in compiled.seal(wiki_vault)) == [
        "path-bytes:wiki/folder",
        "path-bytes:wiki/linked.md",
    ]
    assert compiled.load_record(wiki_vault) == {}
