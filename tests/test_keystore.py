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
        keystore._store_key(tmp_vault, "6LpvURP2E933", "k" * 32)
    finally:
        os.umask(previous)
    store = tmp_vault / keystore.KEY_STORE
    assert stat.S_IMODE(store.stat().st_mode) == 0o600
    assert json.loads(store.read_text()) == {"6LpvURP2E933": "k" * 32}


def test_capture_re_exports_the_store_names_for_its_patch_targets():
    assert capture.KEY_STORE == keystore.KEY_STORE
    assert capture._store_key is keystore._store_key
    assert capture._load_key is keystore._load_key


def test_an_unparseable_store_is_moved_aside_then_written(tmp_vault, capsys):
    """Row 47(a): the bytes are kept beside the store under a dated name, one
    stderr line says so, and the grant is written to a fresh store."""
    store = tmp_vault / keystore.KEY_STORE
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text("{not json")

    keystore._store_key(tmp_vault, "6LpvURP2E933", "k" * 32)

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


def test_a_non_object_store_is_moved_aside_the_same_way(tmp_vault, capsys):
    store = tmp_vault / keystore.KEY_STORE
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text("[]")
    keystore._store_key(tmp_vault, "6LpvURP2E933", "k" * 32)
    assert json.loads(store.read_text()) == {"6LpvURP2E933": "k" * 32}
    assert any(
        p.name.startswith("zotero-keys.json.bad-") for p in store.parent.iterdir()
    )
    assert "moved aside" in capsys.readouterr().err


def test_load_key_answers_none_for_an_absent_unparseable_or_shapeless_store(tmp_vault):
    assert keystore._load_key(tmp_vault, "6LpvURP2E933") is None
    store = tmp_vault / keystore.KEY_STORE
    store.parent.mkdir(parents=True, exist_ok=True)
    for body in ("{not json", "[]", '{"6LpvURP2E933": 42}'):
        store.write_text(body)
        assert keystore._load_key(tmp_vault, "6LpvURP2E933") is None
    store.write_text('{"6LpvURP2E933": "k"}')
    assert keystore._load_key(tmp_vault, "6LpvURP2E933") == "k"
    assert not any(
        p.name.startswith("zotero-keys.json.bad-") for p in store.parent.iterdir()
    )


def test_store_key_preserves_an_existing_valid_entry_when_adding_another(tmp_vault):
    """A real existing store is read, not discarded: `_read_store` forced to
    `None` regardless of the file's content would wrongly treat a valid
    store as corrupt and move it aside, losing the first key."""
    keystore._store_key(tmp_vault, "6LpvURP2E933", "k" * 32)
    keystore._store_key(tmp_vault, "OTHER0000000", "j" * 32)
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
    keystore._store_key(vault, "6LpvURP2E933", "k" * 32)
    store = vault / keystore.KEY_STORE
    assert store.is_file()


def test_store_key_writes_pretty_printed_two_space_json(tmp_vault):
    keystore._store_key(tmp_vault, "6LpvURP2E933", "k" * 32)
    store = tmp_vault / keystore.KEY_STORE
    assert store.read_text() == '{\n  "6LpvURP2E933": "' + "k" * 32 + '"\n}\n'


def test_forget_key_drops_one_entry_and_tolerates_an_absent_store(tmp_vault):
    keystore._forget_key(tmp_vault, "6LpvURP2E933")  # no store: nothing to forget
    keystore._store_key(tmp_vault, "6LpvURP2E933", "k" * 32)
    keystore._store_key(tmp_vault, "OTHER0000000", "j" * 32)
    keystore._forget_key(tmp_vault, "6LpvURP2E933")
    store = tmp_vault / keystore.KEY_STORE
    assert json.loads(store.read_text()) == {"OTHER0000000": "j" * 32}
    assert stat.S_IMODE(store.stat().st_mode) == 0o600
