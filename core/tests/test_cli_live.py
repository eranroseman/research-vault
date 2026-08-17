import argparse
import json
import subprocess
import sys

import pytest

from harness_core import frontmatter, notes, paths


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "harness_core", *args],
        capture_output=True,
        text=True,
    )


@pytest.mark.live
def test_probe():
    proc = run_cli("probe")
    assert proc.returncode == 0
    info = json.loads(proc.stdout)
    assert "betterbibtex" in info and isinstance(info["local_writes"], bool)


@pytest.mark.live
def test_import_note_end_to_end(tmp_vault):
    # Pick any real citekey from the live library.
    from harness_core.zotero import ZoteroClient

    items = ZoteroClient().export_csl(None)
    citekey = items[0]["id"]

    proc = run_cli("import-note", citekey, "--vault", str(tmp_vault))
    assert proc.returncode == 0, proc.stderr
    note = (tmp_vault / "literatures" / f"{citekey}.md").read_text()
    assert f'citekey: "{citekey}"' in note
    assert "%%hk-managed%%" in note
    assert (tmp_vault / "x" / "bibliography.json").is_file()

    # Second import is a no-op.
    proc2 = run_cli("import-note", citekey, "--vault", str(tmp_vault))
    assert "NOOP" in proc2.stdout


@pytest.mark.live
def test_staleness_after_import(tmp_vault):
    from harness_core.zotero import ZoteroClient

    citekey = ZoteroClient().export_csl(None)[0]["id"]
    run_cli("import-note", citekey, "--vault", str(tmp_vault))
    proc = run_cli("staleness", "--vault", str(tmp_vault))
    assert proc.stdout.strip() in {"MATCHED", "UNMATCHED"}
    assert proc.returncode in (0, 1)


def test_probe_unreachable():
    proc = run_cli("probe", "--base", "http://127.0.0.1:1")
    assert proc.returncode == 3
    assert json.loads(proc.stdout)["result"] == "UNREACHABLE"


def test_base_option_works_before_and_after_subcommand(monkeypatch, capsys):
    import harness_core.__main__ as cli

    bases = []

    class FakeClient:
        def __init__(self, base):
            bases.append(base)

        def ready(self):
            return {"zotero": "9.0.6", "betterbibtex": "9.0.55"}

        def supports_local_writes(self):
            return False

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)

    assert cli.main(["--base", "http://before.invalid", "probe"]) == 0
    assert cli.main(["probe", "--base", "http://after.invalid"]) == 0

    assert bases == ["http://before.invalid", "http://after.invalid"]
    assert len(capsys.readouterr().out.splitlines()) == 2


def test_normalize_annotation_maps_live_bbt_shape_without_raw_aliases():
    from harness_core.__main__ import normalize_annotation

    raw = {
        "annotationType": "highlight",
        "annotationComment": "A useful result",
        "annotationPageLabel": "iv",
        "annotationText": "Mortality fell.",
        "key": "ANNKEY01",
        "context_prefix": "before ",
        "context_suffix": " after",
        "annotationPosition": {"pageIndex": 3, "rects": [[1, 2, 3, 4]]},
        "annotationColor": "#ffd400",
    }

    normalized = normalize_annotation(raw, "smith2020")

    assert normalized == {
        "type": "highlight",
        "comment": "A useful result",
        "pageLabel": "iv",
        "key": "ANNKEY01",
        "annotationText": "Mortality fell.",
        "citekey": "smith2020",
        "context_prefix": "before ",
        "context_suffix": " after",
    }
    assert not any(key.startswith("annotationComment") for key in normalized)
    assert notes.render_claim(normalized).startswith("- (quote) [@smith2020, p. iv]")


@pytest.mark.parametrize(
    ("raw", "expected_comment"),
    [
        ({}, ""),
        (
            {"annotationType": "future", "annotationText": "Keep this safely"},
            "Keep this safely",
        ),
        ({"annotationType": "highlight", "annotationText": {"bad": "shape"}}, ""),
        (None, ""),
        (["not", "a", "mapping"], ""),
    ],
)
def test_normalize_annotation_malformed_or_unknown_degrades_to_paraphrase(
    raw, expected_comment
):
    from harness_core.__main__ import normalize_annotation

    normalized = normalize_annotation(raw, "smith2020")

    assert set(normalized) <= {
        "type",
        "comment",
        "pageLabel",
        "key",
        "annotationText",
        "citekey",
        "context_prefix",
        "context_suffix",
    }
    assert normalized["annotationText"] == ""
    assert normalized["comment"] == expected_comment
    assert all(
        isinstance(normalized[key], str)
        for key in ("type", "comment", "pageLabel", "key", "annotationText", "citekey")
    )
    assert notes.render_claim(normalized).startswith(
        f"- (paraphrase) {expected_comment} [@smith2020]"
    )


def _raw_quote(text):
    return {
        "annotationType": "highlight",
        "annotationComment": "",
        "annotationPageLabel": "12",
        "annotationText": text,
        "key": "ANNKEY01",
    }


def _install_import_client(monkeypatch, cli, item, annotations):
    class FakeClient:
        def __init__(self, base):
            self.base = base

        def search(self, terms):
            return [{**item, "citekey": terms}]

        def attachments(self, citekey):
            if not annotations:
                return []
            return [{"path": None, "annotations": annotations}]

        def export_csl(self, citekeys):
            return [{"id": "smith2020", "title": item["title"]}]

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)


def test_import_note_identical_projection_is_noop(tmp_vault, monkeypatch, capsys):
    import harness_core.__main__ as cli

    item = {"title": "Mortality decline", "DOI": "10.1000/xyz"}
    raw = _raw_quote("Mortality fell.")
    note_path = notes.note_path(tmp_vault, "smith2020")
    original = notes.render_note(
        {**item, "id": "smith2020"},
        ["unresolved"],
        [cli.normalize_annotation(raw, "smith2020")],
        existing=None,
        retrieved="2026-08-16",
    )
    note_path.write_text(original, encoding="utf-8")
    _install_import_client(monkeypatch, cli, item, [raw])

    result = cli.cmd_import_note(
        argparse.Namespace(
            citekey="smith2020", vault=str(tmp_vault), base="http://unused"
        )
    )

    assert result == 0
    assert capsys.readouterr().out.strip() == "NOOP"
    assert note_path.read_text(encoding="utf-8") == original


def test_import_note_annotation_only_change_rerenders(tmp_vault, monkeypatch, capsys):
    import harness_core.__main__ as cli

    item = {"title": "Mortality decline", "DOI": "10.1000/xyz"}
    old_raw = _raw_quote("Mortality fell.")
    new_raw = _raw_quote("Mortality fell by 12%.")
    note_path = notes.note_path(tmp_vault, "smith2020")
    original = notes.render_note(
        {**item, "id": "smith2020"},
        ["unresolved"],
        [cli.normalize_annotation(old_raw, "smith2020")],
        existing=None,
        retrieved="2026-08-16",
    )
    note_path.write_text(original, encoding="utf-8")
    _install_import_client(monkeypatch, cli, item, [new_raw])

    result = cli.cmd_import_note(
        argparse.Namespace(
            citekey="smith2020", vault=str(tmp_vault), base="http://unused"
        )
    )

    updated = note_path.read_text(encoding="utf-8")
    assert result == 0
    assert capsys.readouterr().out.strip() == str(note_path)
    assert "Mortality fell by 12%." in updated
    assert "Mortality fell.\n" not in updated


def test_import_note_metadata_only_change_rerenders(tmp_vault, monkeypatch, capsys):
    import harness_core.__main__ as cli

    note_path = notes.note_path(tmp_vault, "smith2020")
    original = notes.render_note(
        {"id": "smith2020", "title": "Original title"},
        [],
        [],
        existing=None,
        retrieved="2026-08-16",
    )
    note_path.write_text(original, encoding="utf-8")
    _install_import_client(monkeypatch, cli, {"title": "Updated title"}, [])

    result = cli.cmd_import_note(
        argparse.Namespace(
            citekey="smith2020", vault=str(tmp_vault), base="http://unused"
        )
    )

    updated = note_path.read_text(encoding="utf-8")
    assert result == 0
    assert capsys.readouterr().out.strip() == str(note_path)
    assert "# Updated title\n" in updated
    assert "# Original title\n" not in updated


def test_import_note_rerender_preserves_crlf_free_tail_bytes(
    tmp_vault, monkeypatch, capsys
):
    import harness_core.__main__ as cli

    class FakeClient:
        def __init__(self, base):
            self.base = base

        def search(self, terms):
            return [{"citekey": terms, "title": "Updated title"}]

        def attachments(self, citekey):
            return [{"path": None, "annotations": []}]

        def export_csl(self, citekeys):
            return [{"id": "smith2020", "title": "Updated title"}]

    note_path = notes.note_path(tmp_vault, "smith2020")
    original = notes.render_note(
        {"id": "smith2020", "title": "Original title"},
        [],
        [],
        existing=None,
        retrieved="2026-08-16",
    )
    managed_end = (
        original.index(notes.MANAGED_CLOSE) + len(notes.MANAGED_CLOSE) + len("\n")
    )
    free_tail = "\r\nfree tail\r\nmixed newline\nUnicode café\r\n".encode("utf-8")
    note_path.write_bytes(original[:managed_end].encode("utf-8") + free_tail)
    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)

    result = cli.cmd_import_note(
        argparse.Namespace(
            citekey="smith2020", vault=str(tmp_vault), base="http://unused"
        )
    )

    output = note_path.read_bytes()
    close = notes.MANAGED_CLOSE.encode("utf-8") + b"\n"
    assert result == 0
    assert capsys.readouterr().out.strip() == str(note_path)
    assert output.split(close, 1)[1] == free_tail


@pytest.mark.parametrize(
    "citekey",
    ["", "../escape", "/tmp/escape", "..\\escape"],
)
def test_import_note_rejects_unsafe_citekey_before_side_effects(
    citekey, tmp_vault, monkeypatch, capsys
):
    import harness_core.__main__ as cli

    constructed = []

    class ForbiddenClient:
        def __init__(self, base):
            constructed.append(base)
            raise AssertionError("ZoteroClient must not be constructed")

    monkeypatch.setattr(cli, "ZoteroClient", ForbiddenClient)
    status_before = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
        text=True,
    ).stdout

    result = cli.cmd_import_note(
        argparse.Namespace(citekey=citekey, vault=str(tmp_vault), base="http://unused")
    )

    status_after = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert result == 1
    assert capsys.readouterr().err.strip() == f"invalid citekey: {citekey!r}"
    assert constructed == []
    assert status_after == status_before
    assert list((tmp_vault / "literatures").iterdir()) == []
    assert list((tmp_vault / "x").iterdir()) == []


@pytest.mark.parametrize(
    "attachment",
    [
        {"path": "D:\\missing.pdf"},
        {"path": None},
        {"path": 17},
        {},
    ],
)
def test_import_note_unresolved_attachment_and_normalized_annotation(
    attachment, tmp_vault, monkeypatch, capsys
):
    import harness_core.__main__ as cli

    raw_annotation = {
        "annotationType": "highlight",
        "annotationComment": "",
        "annotationPageLabel": "12",
        "annotationText": "Mortality fell.",
        "key": "ANNKEY01",
    }

    class FakeClient:
        def __init__(self, base):
            self.base = base

        def search(self, terms):
            return [{"citekey": terms, "title": "Mortality decline"}]

        def attachments(self, citekey):
            return [{**attachment, "annotations": [raw_annotation]}]

        def export_csl(self, citekeys):
            return [{"id": "smith2020", "title": "Mortality decline"}]

    def unresolved(path, vault):
        raise paths.PathError("cannot resolve test attachment")

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)
    monkeypatch.setattr(cli.paths, "to_local", unresolved)

    result = cli.cmd_import_note(
        argparse.Namespace(
            citekey="smith2020", vault=str(tmp_vault), base="http://unused"
        )
    )

    assert result == 0
    assert "warning: attachment unresolved" in capsys.readouterr().err
    note = (tmp_vault / "literatures" / "smith2020.md").read_text()
    data, body = frontmatter.parse(note)
    assert data["attachment-sha256"] == ["unresolved"]
    assert "- (quote) [@smith2020, p. 12]" in body
    assert "annotationPageLabel" not in body


def test_import_note_refreshes_bibliography_before_noop(tmp_vault, monkeypatch, capsys):
    import harness_core.__main__ as cli

    class FakeClient:
        def __init__(self, base):
            self.base = base

        def search(self, terms):
            return [{"citekey": terms, "title": "Mortality decline"}]

        def attachments(self, citekey):
            return []

        def export_csl(self, citekeys):
            return [{"id": "new2026", "title": "Newly admitted"}]

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)
    note_path = notes.note_path(tmp_vault, "smith2020")
    original = notes.render_note(
        {"id": "smith2020", "title": "Mortality decline"},
        [],
        [],
        existing=None,
        retrieved="2026-08-16",
    )
    note_path.write_text(original)

    result = cli.cmd_import_note(
        argparse.Namespace(
            citekey="smith2020", vault=str(tmp_vault), base="http://unused"
        )
    )

    assert result == 0
    assert capsys.readouterr().out.strip() == "NOOP"
    assert note_path.read_text() == original
    assert json.loads((tmp_vault / "x" / "bibliography.json").read_text()) == [
        {"id": "new2026", "title": "Newly admitted"}
    ]


@pytest.mark.parametrize(
    ("state", "expected_code"),
    [
        ("MATCHED", 0),
        ("SKIPPED", 0),
        ("UNMATCHED", 1),
        ("UNREACHABLE", 3),
    ],
)
def test_staleness_exit_codes(state, expected_code, tmp_vault, monkeypatch, capsys):
    import harness_core.__main__ as cli
    from harness_core import Result

    monkeypatch.setattr(
        cli.bibliography, "staleness", lambda vault, client: Result[state]
    )

    code = cli.cmd_staleness(
        argparse.Namespace(vault=str(tmp_vault), base="http://unused")
    )

    assert code == expected_code
    assert capsys.readouterr().out.strip() == state


def test_staleness_cli_reports_corrupt_committed_bibliography_as_unmatched(
    tmp_vault, monkeypatch, capsys
):
    import harness_core.__main__ as cli

    class FakeClient:
        def __init__(self, base):
            self.base = base

        def export_csl(self, citekeys):
            return [{"id": "smith2020", "title": "Mortality decline"}]

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)
    (tmp_vault / "x" / "bibliography.json").write_text("{", encoding="utf-8")

    code = cli.cmd_staleness(
        argparse.Namespace(vault=str(tmp_vault), base="http://unused")
    )

    assert code == 1
    assert capsys.readouterr().out.strip() == "UNMATCHED"
