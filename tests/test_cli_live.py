import argparse
import datetime as datetime_lib
import json
import os
import subprocess
import sys
import types
from pathlib import Path

import pytest

from knowledge_harness import Result, bibliography, frontmatter, notes, paths

REAL_OBSERVE_AUTOEXPORT = bibliography.observe_autoexport

PROVISIONED_VAULT_ENV = "HARNESS_LIVE_AUTOEXPORT_VAULT"
DEFERRAL_REASON = (
    "deferred: the harness never registers an auto-export, so no BBT output "
    "reaches a throwaway vault. Set "
    f"{PROVISIONED_VAULT_ENV} to the absolute path of a vault after a person "
    "creates the whole-library Better CSL JSON auto-export in BBT Preferences "
    "targeting that vault's system/bibliography.json."
)


def _provisioned_vault_or_defer(environ):
    """Return the human-provisioned vault, or defer aloud naming the human step."""
    configured = environ.get(PROVISIONED_VAULT_ENV, "").strip()
    if not configured:
        pytest.skip(DEFERRAL_REASON)
    vault = Path(configured)
    if not vault.is_absolute() or not vault.is_dir():
        pytest.fail(
            f"{PROVISIONED_VAULT_ENV} must name an existing vault by absolute "
            f"path; got {configured!r}"
        )
    return vault


@pytest.fixture
def provisioned_vault():
    return _provisioned_vault_or_defer(os.environ)


def test_end_to_end_legs_defer_aloud_until_a_person_provisions_a_vault():
    """Deferring the falsified-contract legs silently must fail."""
    with pytest.raises(pytest.skip.Exception) as deferred:
        _provisioned_vault_or_defer({})

    reason = str(deferred.value)
    assert PROVISIONED_VAULT_ENV in reason
    assert "whole-library Better CSL JSON auto-export in BBT Preferences" in reason
    assert "system/bibliography.json" in reason


def test_provisioned_vault_opt_in_rejects_a_path_that_is_not_a_vault(tmp_path):
    """Letting a mistyped opt-in quietly skip the end-to-end legs must fail."""
    with pytest.raises(pytest.fail.Exception, match=PROVISIONED_VAULT_ENV):
        _provisioned_vault_or_defer({PROVISIONED_VAULT_ENV: str(tmp_path / "absent")})


@pytest.fixture(autouse=True)
def matched_autoexport_observer(monkeypatch):
    """Keep import-unit fakes deterministic; observer behavior is tested explicitly."""
    import knowledge_harness.__main__ as cli

    monkeypatch.setattr(
        cli.bibliography,
        "observe_autoexport",
        lambda *args, **kwargs: types.SimpleNamespace(
            result=Result.MATCHED,
            detail="genuine BBT output",
            staleness=Result.MATCHED,
            staleness_detail="current",
        ),
        raising=False,
    )


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "knowledge_harness", *args],
        capture_output=True,
        text=True,
    )


@pytest.mark.live
def test_probe():
    proc = run_cli("probe")
    assert proc.returncode == 0
    info = json.loads(proc.stdout)
    assert "betterbibtex" in info


@pytest.mark.live
def test_import_note_end_to_end_in_a_provisioned_vault(provisioned_vault):
    # Pick any real citekey from the live library.
    from knowledge_harness.zotero import ZoteroClient

    items = ZoteroClient().export_csl(None)
    citekey = items[0]["id"]

    proc = run_cli("import-note", citekey, "--vault", str(provisioned_vault))
    assert proc.returncode == 0, proc.stderr
    note = (provisioned_vault / "literatures" / f"{citekey}.md").read_text()
    assert f'citekey: "{citekey}"' in note
    assert "%%hk-managed%%" in note
    assert (provisioned_vault / "system" / "bibliography.json").is_file()

    # Second import is a no-op.
    proc2 = run_cli("import-note", citekey, "--vault", str(provisioned_vault))
    assert "NOOP" in proc2.stdout


@pytest.mark.live
def test_staleness_after_import_into_a_provisioned_vault(provisioned_vault):
    from knowledge_harness.zotero import ZoteroClient

    citekey = ZoteroClient().export_csl(None)[0]["id"]

    imported = run_cli("import-note", citekey, "--vault", str(provisioned_vault))
    proc = run_cli("staleness", "--vault", str(provisioned_vault))

    assert imported.returncode == 0, imported.stderr
    assert proc.stdout.strip() in {"MATCHED", "UNMATCHED"}
    assert proc.returncode in (0, 1)


def test_probe_unreachable():
    proc = run_cli("probe", "--base", "http://127.0.0.1:1")
    assert proc.returncode == 3
    assert json.loads(proc.stdout)["result"] == "UNREACHABLE"


def test_base_option_works_before_and_after_subcommand(monkeypatch, capsys):
    import knowledge_harness.__main__ as cli

    bases = []

    class FakeClient:
        def __init__(self, base):
            bases.append(base)

        def ready(self):
            return {"zotero": "9.0.6", "betterbibtex": "9.0.55"}

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)

    assert cli.main(["--base", "http://before.invalid", "probe"]) == 0
    assert cli.main(["probe", "--base", "http://after.invalid"]) == 0

    assert bases == ["http://before.invalid", "http://after.invalid"]
    assert len(capsys.readouterr().out.splitlines()) == 2


def test_normalize_annotation_maps_live_bbt_shape_without_raw_aliases():
    from knowledge_harness.__main__ import normalize_annotation

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
    from knowledge_harness.__main__ import normalize_annotation

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


def test_import_note_uses_python_310_compatible_utc_surface(tmp_vault, monkeypatch):
    import knowledge_harness.__main__ as cli

    seen_timezones = []

    class FixedDateTime:
        @classmethod
        def now(cls, timezone):
            seen_timezones.append(timezone)
            return datetime_lib.datetime(2026, 8, 20, 12, 34, 56, tzinfo=timezone)

    python_310_datetime = types.SimpleNamespace(
        datetime=FixedDateTime,
        timezone=datetime_lib.timezone,
    )
    _install_import_client(
        monkeypatch,
        cli,
        {"title": "Mortality decline", "DOI": "10.1000/xyz"},
        [],
    )
    monkeypatch.setattr(cli, "datetime", python_310_datetime)
    result = cli.cmd_import_note(
        argparse.Namespace(
            citekey="smith2020", vault=str(tmp_vault), base="http://unused"
        )
    )

    data, _ = frontmatter.parse(
        (tmp_vault / "literatures" / "smith2020.md").read_text()
    )
    assert result == 0
    assert seen_timezones == [datetime_lib.timezone.utc]
    assert data["accessed"] == "2026-08-20"
    assert data["generated"]["at"] == "2026-08-20T12:34:56Z"


def test_import_note_identical_projection_is_noop(tmp_vault, monkeypatch, capsys):
    import knowledge_harness.__main__ as cli

    item = {"title": "Mortality decline", "DOI": "10.1000/xyz"}
    raw = _raw_quote("Mortality fell.")
    note_path = notes.note_path(tmp_vault, "smith2020")
    original = notes.render_note(
        {**item, "id": "smith2020"},
        ["unresolved"],
        [cli.normalize_annotation(raw, "smith2020")],
        existing=None,
        accessed="2026-08-16",
        generated_at="2026-08-16T00:00:00Z",
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
    import knowledge_harness.__main__ as cli

    item = {"title": "Mortality decline", "DOI": "10.1000/xyz"}
    old_raw = _raw_quote("Mortality fell.")
    new_raw = _raw_quote("Mortality fell by 12%.")
    note_path = notes.note_path(tmp_vault, "smith2020")
    original = notes.render_note(
        {**item, "id": "smith2020"},
        ["unresolved"],
        [cli.normalize_annotation(old_raw, "smith2020")],
        existing=None,
        accessed="2026-08-16",
        generated_at="2026-08-16T00:00:00Z",
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
    import knowledge_harness.__main__ as cli

    note_path = notes.note_path(tmp_vault, "smith2020")
    original = notes.render_note(
        {"id": "smith2020", "title": "Original title"},
        [],
        [],
        existing=None,
        accessed="2026-08-16",
        generated_at="2026-08-16T00:00:00Z",
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
    import knowledge_harness.__main__ as cli

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
        accessed="2026-08-16",
        generated_at="2026-08-16T00:00:00Z",
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
    import knowledge_harness.__main__ as cli

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
    assert list((tmp_vault / "system").iterdir()) == []


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
    import knowledge_harness.__main__ as cli

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
    assert data["fixity-sha256"] == ["unresolved"]
    assert "- (quote) [@smith2020, p. 12]" in body
    assert "annotationPageLabel" not in body


def test_import_note_observes_autoexport_before_noop_without_old_writer(
    tmp_vault, monkeypatch, capsys
):
    import knowledge_harness.__main__ as cli

    class FakeClient:
        def __init__(self, base):
            self.base = base

        def search(self, terms):
            return [{"citekey": terms, "title": "Mortality decline"}]

        def attachments(self, citekey):
            return []

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)
    observed = []
    monkeypatch.setattr(
        cli.bibliography,
        "observe_autoexport",
        lambda vault, client: (
            observed.append((vault, client))
            or bibliography.AutoexportObservation(
                Result.MATCHED, "genuine BBT output", Result.MATCHED, "current"
            )
        ),
    )
    monkeypatch.setattr(
        cli.bibliography,
        "write_and_commit",
        lambda *args: (_ for _ in ()).throw(AssertionError("old writer called")),
        raising=False,
    )
    note_path = notes.note_path(tmp_vault, "smith2020")
    original = notes.render_note(
        {"id": "smith2020", "title": "Mortality decline"},
        [],
        [],
        existing=None,
        accessed="2026-08-16",
        generated_at="2026-08-16T00:00:00Z",
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
    assert len(observed) == 1
    assert not (tmp_vault / "system" / "bibliography.json").exists()


@pytest.mark.parametrize(
    ("state", "expected_code"),
    [(Result.UNMATCHED, 1), (Result.UNREACHABLE, 3)],
)
def test_import_note_autoexport_failure_prevents_attachment_and_note_writes(
    tmp_vault, monkeypatch, capsys, state, expected_code
):
    import knowledge_harness.__main__ as cli

    class FakeClient:
        def __init__(self, base):
            self.base = base

        def search(self, terms):
            return [{"citekey": terms, "title": "Mortality decline"}]

        def attachments(self, citekey):
            raise AssertionError("attachments must not be read after observer failure")

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)
    monkeypatch.setattr(
        cli.bibliography,
        "observe_autoexport",
        lambda *args, **kwargs: bibliography.AutoexportObservation(
            state, "autoexport failed", state, "autoexport failed"
        ),
    )

    result = cli.cmd_import_note(
        argparse.Namespace(
            citekey="smith2020", vault=str(tmp_vault), base="http://unused"
        )
    )

    captured = capsys.readouterr()
    assert result == expected_code
    assert captured.out == ""
    assert captured.err.strip() == "autoexport failed"
    assert not notes.note_path(tmp_vault, "smith2020").exists()
    assert not (tmp_vault / bibliography.BIB_PATH).exists()


def test_import_note_stderr_carries_the_bbt_preferences_repair(
    tmp_vault, monkeypatch, capsys
):
    """Telling a person the auto-export is broken without the remedy must fail."""
    import knowledge_harness.__main__ as cli

    class FakeClient:
        def __init__(self, base):
            self.base = base

        def search(self, terms):
            return [{"citekey": terms, "title": "Mortality decline"}]

        def export_csl(self, citekeys):
            assert citekeys is None
            return [{"id": "smith2020", "title": "Mortality decline"}]

        def attachments(self, citekey):
            raise AssertionError("attachments must not be read after observer failure")

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)
    monkeypatch.setattr(paths, "_running_in_wsl", lambda: False)
    monkeypatch.setattr(
        cli.bibliography,
        "observe_autoexport",
        lambda vault, client: REAL_OBSERVE_AUTOEXPORT(
            vault,
            client,
            settle_seconds=0,
            poll_interval=1,
            monotonic=lambda: 0,
            sleep=lambda seconds: None,
        ),
    )

    result = cli.cmd_import_note(
        argparse.Namespace(
            citekey="smith2020", vault=str(tmp_vault), base="http://unused"
        )
    )

    captured = capsys.readouterr()
    assert result == 1
    assert captured.err.strip() == (
        "bibliography auto-export absent; a person must create or fix the "
        "whole-library Better CSL JSON auto-export in BBT Preferences with "
        f"target {tmp_vault / bibliography.BIB_PATH}"
    )
    assert not notes.note_path(tmp_vault, "smith2020").exists()
    assert not (tmp_vault / bibliography.BIB_PATH).exists()


def test_import_note_post_commit_git_read_oserror_exits_three_without_note_write(
    tmp_vault, monkeypatch, capsys
):
    import knowledge_harness.__main__ as cli

    items = [{"id": "smith2020", "title": "Mortality decline"}]
    target = tmp_vault / bibliography.BIB_PATH
    target.write_bytes(json.dumps(items, separators=(",", ":")).encode())

    class FakeClient:
        def __init__(self, base):
            self.base = base

        def search(self, terms):
            return [{"citekey": terms, "title": "Mortality decline"}]

        def export_csl(self, citekeys):
            assert citekeys is None
            return items

        def attachments(self, citekey):
            raise AssertionError("attachments must not be read after observer failure")

    real_run = bibliography.subprocess.run

    def fail_post_commit_read(command, *args, **kwargs):
        if command == ["git", "show", f"HEAD:{bibliography.BIB_PATH}"]:
            raise OSError("git unavailable")
        return real_run(command, *args, **kwargs)

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)
    monkeypatch.setattr(bibliography.subprocess, "run", fail_post_commit_read)
    monkeypatch.setattr(
        cli.bibliography,
        "observe_autoexport",
        lambda vault, client: REAL_OBSERVE_AUTOEXPORT(
            vault,
            client,
            settle_seconds=0,
            poll_interval=1,
            monotonic=lambda: 0,
            sleep=lambda seconds: None,
        ),
    )

    result = cli.cmd_import_note(
        argparse.Namespace(
            citekey="smith2020", vault=str(tmp_vault), base="http://unused"
        )
    )

    captured = capsys.readouterr()
    assert result == 3
    assert captured.out == ""
    assert "git unavailable" in captured.err
    assert "Traceback" not in captured.err
    assert not notes.note_path(tmp_vault, "smith2020").exists()
    assert target.is_file()


def test_import_note_target_read_oserror_exits_three_without_note_write(
    tmp_vault, monkeypatch, capsys
):
    import knowledge_harness.__main__ as cli

    items = [{"id": "smith2020", "title": "Mortality decline"}]
    target = tmp_vault / bibliography.BIB_PATH
    target.write_text(json.dumps(items))

    class FakeClient:
        def __init__(self, base):
            self.base = base

        def search(self, terms):
            return [{"citekey": terms, "title": "Mortality decline"}]

        def export_csl(self, citekeys):
            assert citekeys is None
            return items

        def attachments(self, citekey):
            raise AssertionError("attachments must not be read after observer failure")

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)
    monkeypatch.setattr(
        bibliography.os,
        "fdopen",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("target read denied")),
    )
    monkeypatch.setattr(
        cli.bibliography,
        "observe_autoexport",
        lambda vault, client: REAL_OBSERVE_AUTOEXPORT(
            vault,
            client,
            settle_seconds=0,
            poll_interval=1,
            monotonic=lambda: 0,
            sleep=lambda seconds: None,
        ),
    )

    result = cli.cmd_import_note(
        argparse.Namespace(
            citekey="smith2020", vault=str(tmp_vault), base="http://unused"
        )
    )

    captured = capsys.readouterr()
    assert result == 3
    assert captured.out == ""
    assert "target read denied" in captured.err
    assert "Traceback" not in captured.err
    assert not notes.note_path(tmp_vault, "smith2020").exists()


def test_import_note_accepts_genuine_bbt_output_already_at_the_target(
    tmp_vault, monkeypatch, capsys
):
    import knowledge_harness.__main__ as cli

    items = [{"id": "smith2020", "title": "Mortality decline"}]
    (tmp_vault / bibliography.BIB_PATH).write_bytes(
        b'[{"id":"smith2020","title":"Mortality decline"}]'
    )

    class FakeClient:
        def __init__(self, base):
            self.base = base

        def search(self, terms):
            return [{"citekey": terms, "title": "Mortality decline"}]

        def export_csl(self, citekeys):
            assert citekeys is None
            return items

        def attachments(self, citekey):
            return []

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)
    monkeypatch.setattr(
        cli.bibliography,
        "observe_autoexport",
        lambda vault, client: REAL_OBSERVE_AUTOEXPORT(
            vault,
            client,
            settle_seconds=0,
            poll_interval=1,
            monotonic=lambda: 0,
            sleep=lambda seconds: None,
        ),
    )

    result = cli.cmd_import_note(
        argparse.Namespace(
            citekey="smith2020", vault=str(tmp_vault), base="http://unused"
        )
    )

    assert result == 0
    assert notes.note_path(tmp_vault, "smith2020").is_file()
    assert (tmp_vault / bibliography.BIB_PATH).read_bytes() == (
        b'[{"id":"smith2020","title":"Mortality decline"}]'
    )
    assert capsys.readouterr().err == ""


def test_import_note_autoexport_commit_preserves_all_unrelated_git_state(
    tmp_vault, monkeypatch, capsys
):
    import knowledge_harness.__main__ as cli

    tracked = tmp_vault / "tracked.txt"
    tracked.write_bytes(b"baseline\n")
    subprocess.run(["git", "add", "tracked.txt"], cwd=tmp_vault, check=True)
    subprocess.run(["git", "commit", "-qm", "baseline"], cwd=tmp_vault, check=True)
    tracked.write_bytes(b"unstaged bytes\n")
    staged = tmp_vault / "staged.txt"
    staged.write_bytes(b"staged bytes\n")
    subprocess.run(["git", "add", "staged.txt"], cwd=tmp_vault, check=True)
    untracked = tmp_vault / "untracked.txt"
    untracked.write_bytes(b"untracked bytes\n")
    staged_blob_before = subprocess.run(
        ["git", "show", ":staged.txt"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
    ).stdout
    staged_diff_before = subprocess.run(
        ["git", "diff", "--cached", "--binary", "--", "staged.txt"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
    ).stdout

    items = [{"id": "smith2020", "title": "Mortality decline"}]
    target = tmp_vault / bibliography.BIB_PATH
    bbt_bytes = b'[ { "title": "Mortality decline", "id": "smith2020" } ]\n'
    target.write_bytes(bbt_bytes)
    status_before = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
    ).stdout

    class FakeClient:
        def __init__(self, base):
            self.base = base

        def search(self, terms):
            return [{"citekey": terms, "title": "Mortality decline"}]

        def export_csl(self, citekeys):
            assert citekeys is None
            return items

        def attachments(self, citekey):
            return []

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)
    monkeypatch.setattr(
        cli.bibliography,
        "observe_autoexport",
        lambda vault, client: REAL_OBSERVE_AUTOEXPORT(
            vault,
            client,
            settle_seconds=0,
            poll_interval=1,
            monotonic=lambda: 0,
            sleep=lambda seconds: None,
        ),
    )

    result = cli.cmd_import_note(
        argparse.Namespace(
            citekey="smith2020", vault=str(tmp_vault), base="http://unused"
        )
    )

    assert result == 0
    assert target.read_bytes() == bbt_bytes
    assert (
        subprocess.run(
            ["git", "show", f"HEAD:{bibliography.BIB_PATH}"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
        ).stdout
        == bbt_bytes
    )
    assert subprocess.run(
        ["git", "show", "--pretty=format:", "--name-only", "HEAD"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines() == [bibliography.BIB_PATH]
    assert (
        subprocess.run(
            ["git", "show", ":staged.txt"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
        ).stdout
        == staged_blob_before
    )
    assert (
        subprocess.run(
            ["git", "diff", "--cached", "--binary", "--", "staged.txt"],
            cwd=tmp_vault,
            check=True,
            capture_output=True,
        ).stdout
        == staged_diff_before
    )
    assert tracked.read_bytes() == b"unstaged bytes\n"
    assert untracked.read_bytes() == b"untracked bytes\n"

    status_after = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=tmp_vault,
        check=True,
        capture_output=True,
    ).stdout

    def unrelated(lines):
        return [
            line
            for line in lines.splitlines()
            if not line.endswith(b" system/bibliography.json")
            and not line.endswith(b" literatures/smith2020.md")
            and not line.endswith(b" log.md")
        ]

    assert unrelated(status_after) == unrelated(status_before)
    assert capsys.readouterr().err == ""


def test_import_note_applies_extracted_text_only_to_its_attachment(
    tmp_vault, monkeypatch, capsys
):
    import knowledge_harness.__main__ as cli

    first = _raw_quote("First attachment quote")
    second = _raw_quote("Second attachment quote")
    attachments = [
        {"path": "first.pdf", "annotations": [first]},
        {"path": "second.pdf", "annotations": [second]},
    ]

    class FakeClient:
        def __init__(self, base):
            self.base = base

        def search(self, terms):
            return [{"citekey": terms, "title": "Isolation"}]

        def attachments(self, citekey):
            return attachments

        def export_csl(self, citekeys):
            return [{"id": "smith2020", "title": "Isolation"}]

    def local(path, vault):
        return tmp_vault / path

    def extracted(path):
        return (
            "prefix First attachment quote suffix" if path.name == "first.pdf" else ""
        )

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)
    monkeypatch.setattr(cli.paths, "to_local", local)
    monkeypatch.setattr(cli.notes, "sha256_file", lambda _: "hash")
    monkeypatch.setattr("knowledge_harness.selectors.pdf_text", extracted)

    assert (
        cli.cmd_import_note(
            argparse.Namespace(
                citekey="smith2020", vault=str(tmp_vault), base="http://unused"
            )
        )
        == 0
    )
    note = (tmp_vault / "literatures" / "smith2020.md").read_text()
    assert 'prefix="prefix " suffix=" suffix"' in note
    second_claim = note.split("Second attachment quote", 1)[1].split("- (quote)", 1)[0]
    assert "hk-selector" not in second_claim
    assert "no extractable PDF text" in capsys.readouterr().err


def test_import_note_preserves_prior_selectors_when_contexts_degrade(
    tmp_vault, monkeypatch, capsys
):
    import knowledge_harness.__main__ as cli

    raw = _raw_quote("Quote remains")
    existing_ann = cli.normalize_annotation(raw, "smith2020")
    existing_ann["context_prefix"] = "kept prefix"
    existing_ann["context_suffix"] = "kept suffix"
    note_path = notes.note_path(tmp_vault, "smith2020")
    original = notes.render_note(
        {"id": "smith2020", "title": "Retention"},
        ["unresolved"],
        [existing_ann],
        existing=None,
        accessed="2026-08-16",
        generated_at="2026-08-16T00:00:00Z",
    )
    free_tail = b"\r\ncustom tail\r\n"
    note_path.write_bytes(original.encode() + free_tail)
    _install_import_client(monkeypatch, cli, {"title": "Retention"}, [raw])

    assert (
        cli.cmd_import_note(
            argparse.Namespace(
                citekey="smith2020", vault=str(tmp_vault), base="http://unused"
            )
        )
        == 0
    )
    assert note_path.read_bytes() == original.encode() + free_tail
    stderr = capsys.readouterr().err
    assert "warning: selectors degraded" in stderr
    assert "existing selector contexts retained" in stderr


def test_import_note_migrates_and_retains_legacy_multiline_selector(
    tmp_vault, monkeypatch, capsys
):
    import knowledge_harness.__main__ as cli

    raw = _raw_quote("Quote remains")
    note_path = notes.note_path(tmp_vault, "smith2020")
    original = notes.render_note(
        {"id": "smith2020", "title": "Legacy selector"},
        ["unresolved"],
        [cli.normalize_annotation(raw, "smith2020")],
        existing=None,
        accessed="2026-08-16",
        generated_at="2026-08-16T00:00:00Z",
    )
    legacy = (
        '  <!-- hk-selector prefix="legacy\r\nprefix" suffix="suffix\nlegacy" -->\n'
    )
    note_path.write_bytes(
        original.replace(notes.MANAGED_CLOSE, legacy + notes.MANAGED_CLOSE).encode()
    )
    _install_import_client(monkeypatch, cli, {"title": "Legacy selector"}, [raw])

    assert (
        cli.cmd_import_note(
            argparse.Namespace(
                citekey="smith2020", vault=str(tmp_vault), base="http://unused"
            )
        )
        == 0
    )
    migrated = note_path.read_text()
    assert 'prefix="legacy&#13;&#10;prefix" suffix="suffix&#10;legacy"' in migrated
    assert "existing selector contexts retained" in capsys.readouterr().err

    assert (
        cli.cmd_import_note(
            argparse.Namespace(
                citekey="smith2020", vault=str(tmp_vault), base="http://unused"
            )
        )
        == 0
    )
    assert capsys.readouterr().out.strip() == "NOOP"
    assert note_path.read_text() == migrated


def test_import_note_reports_unresolved_attachment_in_mixed_extraction(
    tmp_vault, monkeypatch, capsys
):
    import knowledge_harness.__main__ as cli

    first = _raw_quote("Resolved quote")
    second = _raw_quote("Unresolved quote")

    class FakeClient:
        def __init__(self, base):
            self.base = base

        def search(self, terms):
            return [{"citekey": terms, "title": "Mixed attachments"}]

        def attachments(self, citekey):
            return [
                {"path": "resolved.pdf", "annotations": [first]},
                {"path": None, "annotations": [second]},
            ]

        def export_csl(self, citekeys):
            return [{"id": "smith2020", "title": "Mixed attachments"}]

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)
    monkeypatch.setattr(cli.paths, "to_local", lambda path, vault: tmp_vault / path)
    monkeypatch.setattr(cli.notes, "sha256_file", lambda _: "hash")
    monkeypatch.setattr(
        "knowledge_harness.selectors.pdf_text", lambda _: "before Resolved quote after"
    )

    assert (
        cli.cmd_import_note(
            argparse.Namespace(
                citekey="smith2020", vault=str(tmp_vault), base="http://unused"
            )
        )
        == 0
    )
    stderr = capsys.readouterr().err
    assert "attachment unresolved" in stderr
    assert "quotes were not found" not in stderr


def test_backfill_selectors_skips_malformed_and_unsafe_notes_and_aggregates_failures(
    fixture_vault, monkeypatch, capsys
):
    import knowledge_harness.__main__ as cli

    (fixture_vault / "literatures" / "bad.md").write_text("not frontmatter")
    (fixture_vault / "literatures" / "unsafe.md").write_text(
        '---\ncitekey: "../escape"\ntype: "literature"\n---\nbody\n'
    )
    called = []

    def fake_import(args):
        called.append((args.citekey, args.base))
        return 1 if args.citekey == "smith2020" else 0

    monkeypatch.setattr(cli, "cmd_import_note", fake_import)
    result = cli.main(
        ["--base", "http://base", "backfill-selectors", "--vault", str(fixture_vault)]
    )

    assert result == 1
    assert called == [
        ("gone2019", "http://base"),
        ("smith2020", "http://base"),
    ]
    stderr = capsys.readouterr().err
    assert "malformed literature note" in stderr
    assert "invalid citekey" in stderr

    called.clear()
    assert (
        cli.main(
            [
                "backfill-selectors",
                "--vault",
                str(fixture_vault),
                "--base",
                "http://after",
            ]
        )
        == 1
    )
    assert called == [
        ("gone2019", "http://after"),
        ("smith2020", "http://after"),
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
    import knowledge_harness.__main__ as cli
    from knowledge_harness import Result

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
    import knowledge_harness.__main__ as cli

    class FakeClient:
        def __init__(self, base):
            self.base = base

        def export_csl(self, citekeys):
            return [{"id": "smith2020", "title": "Mortality decline"}]

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)
    (tmp_vault / "system" / "bibliography.json").write_text("{", encoding="utf-8")

    code = cli.cmd_staleness(
        argparse.Namespace(vault=str(tmp_vault), base="http://unused")
    )

    assert code == 1
    assert capsys.readouterr().out.strip() == "UNMATCHED"
