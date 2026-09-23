import datetime
import json
import os
import stat
from pathlib import Path

from research_vault import capture, keystore


def test_store_key_creates_the_file_0600_before_any_byte_lands(tmp_vault, monkeypatch):
    """Moved from tests/test_capture.py: write_text then chmod would leave the
    key at the umask default for the instant between them (row 47)."""
    monkeypatch.setattr(Path, "chmod", lambda self, mode, **kwargs: None)
    previous = os.umask(0o022)
    try:
        keystore.store_key(tmp_vault, "6LpvURP2E933", "k" * 32)
    finally:
        os.umask(previous)
    store = tmp_vault / keystore.KEY_STORE
    assert stat.S_IMODE(store.stat().st_mode) == 0o600
    assert json.loads(store.read_text()) == {"6LpvURP2E933": "k" * 32}


def test_capture_calls_the_store_through_the_module_not_a_re_export():
    """`add` reaches the store as `keystore.<name>` at call time, so a test
    patches `keystore.store_key` and no private name is re-exported."""
    assert capture.keystore is keystore
    for name in ("_store_key", "_load_key", "_forget_key", "KEY_STORE"):
        assert not hasattr(capture, name), name


def test_an_unparseable_store_is_moved_aside_then_written(tmp_vault, capsys):
    """Row 47(a): the bytes are kept beside the store under a dated name, one
    stderr line says so, and the grant is written to a fresh store."""
    store = tmp_vault / keystore.KEY_STORE
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text("{not json")

    keystore.store_key(tmp_vault, "6LpvURP2E933", "k" * 32)

    aside = [
        p for p in store.parent.iterdir() if p.name.startswith("zotero-keys.json.bad-")
    ]
    assert len(aside) == 1
    assert aside[0].read_text() == "{not json"
    assert aside[0].name[len("zotero-keys.json.bad-") :].endswith("Z")
    assert json.loads(store.read_text()) == {"6LpvURP2E933": "k" * 32}
    err = capsys.readouterr().err
    assert err.count("\n") == 1
    assert "zotero-keys.json" in err
    assert "moved aside" in err


def test_move_aside_stamps_utc_not_local_time(tmp_vault, monkeypatch):
    """The `.bad-<stamp>` suffix's own `Z` claims UTC; `datetime.now(None)`
    would be local time, drifting by the zone offset under a non-UTC TZ — a
    lie in a filename. Mirrors
    test_plan_operation_id_is_utc_and_the_format_is_pinned's technique."""
    import time

    store = tmp_vault / keystore.KEY_STORE
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text("{not json")
    monkeypatch.setenv("TZ", "Asia/Kolkata")
    time.tzset()
    try:
        before = datetime.datetime.now(datetime.UTC)
        keystore.store_key(tmp_vault, "6LpvURP2E933", "k" * 32)
        aside = [
            p
            for p in store.parent.iterdir()
            if p.name.startswith("zotero-keys.json.bad-")
        ]
        assert len(aside) == 1
        stamp_text = aside[0].name[len("zotero-keys.json.bad-") :]
        stamped = datetime.datetime.strptime(stamp_text, "%Y%m%dT%H%M%SZ").replace(
            tzinfo=datetime.UTC
        )
        assert abs((stamped - before).total_seconds()) < 60
    finally:
        monkeypatch.delenv("TZ")
        time.tzset()


def test_a_non_object_store_is_moved_aside_the_same_way(tmp_vault, capsys):
    store = tmp_vault / keystore.KEY_STORE
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text("[]")
    keystore.store_key(tmp_vault, "6LpvURP2E933", "k" * 32)
    assert json.loads(store.read_text()) == {"6LpvURP2E933": "k" * 32}
    assert any(
        p.name.startswith("zotero-keys.json.bad-") for p in store.parent.iterdir()
    )
    assert "moved aside" in capsys.readouterr().err


def test_load_key_answers_none_for_an_absent_unparseable_or_shapeless_store(tmp_vault):
    assert keystore.load_key(tmp_vault, "6LpvURP2E933") is None
    store = tmp_vault / keystore.KEY_STORE
    store.parent.mkdir(parents=True, exist_ok=True)
    for body in ("{not json", "[]", '{"6LpvURP2E933": 42}'):
        store.write_text(body)
        assert keystore.load_key(tmp_vault, "6LpvURP2E933") is None
    store.write_text('{"6LpvURP2E933": "k"}')
    assert keystore.load_key(tmp_vault, "6LpvURP2E933") == "k"
    assert not any(
        p.name.startswith("zotero-keys.json.bad-") for p in store.parent.iterdir()
    )


def test_store_key_preserves_an_existing_valid_entry_when_adding_another(tmp_vault):
    """A real existing store is read, not discarded: `_read_store` forced to
    `None` regardless of the file's content would wrongly treat a valid
    store as corrupt and move it aside, losing the first key."""
    keystore.store_key(tmp_vault, "6LpvURP2E933", "k" * 32)
    keystore.store_key(tmp_vault, "OTHER0000000", "j" * 32)
    store = tmp_vault / keystore.KEY_STORE
    assert json.loads(store.read_text()) == {
        "6LpvURP2E933": "k" * 32,
        "OTHER0000000": "j" * 32,
    }
    assert not any(
        p.name.startswith("zotero-keys.json.bad-") for p in store.parent.iterdir()
    )


def test_store_key_creates_a_multi_level_missing_vault_directory(tmp_path):
    vault = tmp_path / "missing" / "vault"
    keystore.store_key(vault, "6LpvURP2E933", "k" * 32)
    store = vault / keystore.KEY_STORE
    assert store.is_file()


def test_store_key_writes_pretty_printed_two_space_json(tmp_vault):
    keystore.store_key(tmp_vault, "6LpvURP2E933", "k" * 32)
    store = tmp_vault / keystore.KEY_STORE
    assert store.read_text() == '{\n  "6LpvURP2E933": "' + "k" * 32 + '"\n}\n'


def test_forget_key_drops_one_entry_and_tolerates_an_absent_store(tmp_vault):
    keystore.forget_key(tmp_vault, "6LpvURP2E933")  # no store: nothing to forget
    keystore.store_key(tmp_vault, "6LpvURP2E933", "k" * 32)
    keystore.store_key(tmp_vault, "OTHER0000000", "j" * 32)
    keystore.forget_key(tmp_vault, "6LpvURP2E933")
    store = tmp_vault / keystore.KEY_STORE
    assert json.loads(store.read_text()) == {"OTHER0000000": "j" * 32}
    assert stat.S_IMODE(store.stat().st_mode) == 0o600
