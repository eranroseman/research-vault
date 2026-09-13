import argparse
import json
import subprocess

import pytest

from research_vault import Result, paths, scaffold, zotero
from tests.fakes import FakeZotero

PROBE_NAMES = [
    "tree",
    "machine-config",
    "zotero",
    "write-guard",
    "fulltext-sync",
    "bbt",
    "bbt-git",
    "plugins",
    "path-shim",
    "translator-formats",
    "compile-tool",
    "remote",
    "backup",
]
HARD_UNMATCHED = ["tree", "machine-config", "zotero", "bbt", "write-guard", "plugins"]
HARD_UNREACHABLE = ["zotero", "bbt"]
WARN_ONLY = [
    "remote",
    "backup",
    "bbt-git",
    "translator-formats",
    "compile-tool",
    "fulltext-sync",
    "path-shim",
]
READY = {"zotero": "10.0.1", "betterbibtex": "9.0.63"}
COMPILE_PLUGIN = "claude-obsidian@agricidaniel-claude-obsidian"


@pytest.fixture(autouse=True)
def _hermetic_host(monkeypatch):
    """Doctor reads two host facts outside the vault — WSL detection and
    ``~/.claude/plugins/installed_plugins.json``. Pin both so a test's answer
    never depends on the machine running it; a test that wants them re-patches."""
    monkeypatch.setattr(paths, "_running_in_wsl", lambda: False)
    monkeypatch.setattr(scaffold, "_installed_plugins", dict)


def _probes(**states):
    return [
        (name, states.get(name, Result.MATCHED), f"{name} detail")
        for name in PROBE_NAMES
    ]


def _run_cmd(monkeypatch, capsys, probes):
    import research_vault.__main__ as cli

    monkeypatch.setattr(cli, "doctor", lambda *args, **kwargs: probes)
    code = cli.cmd_doctor(argparse.Namespace(vault="/unused", base="http://unused"))
    return code, capsys.readouterr()


def test_cmd_doctor_all_matched_exits_zero_and_prints_in_order(monkeypatch, capsys):
    code, captured = _run_cmd(monkeypatch, capsys, _probes())

    assert code == 0
    assert [line.split()[1] for line in captured.out.splitlines()] == PROBE_NAMES


@pytest.mark.parametrize("name", HARD_UNMATCHED)
def test_cmd_doctor_each_hard_unmatched_exits_one(name, monkeypatch, capsys):
    code, captured = _run_cmd(monkeypatch, capsys, _probes(**{name: Result.UNMATCHED}))

    assert code == 1
    assert f"UNMATCHED {name}" in captured.out


@pytest.mark.parametrize("name", HARD_UNREACHABLE)
def test_cmd_doctor_each_hard_unreachable_exits_three(name, monkeypatch, capsys):
    code, captured = _run_cmd(
        monkeypatch, capsys, _probes(**{name: Result.UNREACHABLE})
    )

    assert code == 3
    assert f"UNREACHABLE {name}" in captured.out


@pytest.mark.parametrize("name", WARN_ONLY)
@pytest.mark.parametrize("state", [Result.UNMATCHED, Result.UNREACHABLE])
def test_cmd_doctor_warn_only_failures_exit_zero_and_print_warn_prefix(
    name, state, monkeypatch, capsys
):
    code, captured = _run_cmd(monkeypatch, capsys, _probes(**{name: state}))

    assert code == 0
    line = next(line for line in captured.out.splitlines() if f" {name} " in line)
    assert line.startswith(f"warn:{state.value} {name}")


def test_cmd_doctor_hard_unmatched_wins_over_hard_unreachable(monkeypatch, capsys):
    code, _ = _run_cmd(
        monkeypatch,
        capsys,
        _probes(tree=Result.UNMATCHED, zotero=Result.UNREACHABLE),
    )
    assert code == 1


def test_cmd_doctor_sets_partition_the_thirteen_probes():
    import research_vault.__main__ as cli

    assert set(HARD_UNMATCHED) == cli.DOCTOR_HARD_UNMATCHED
    assert set(HARD_UNREACHABLE) == cli.DOCTOR_HARD_UNREACHABLE
    assert set(WARN_ONLY) == cli.DOCTOR_WARN_ONLY
    assert set(PROBE_NAMES) == cli.DOCTOR_HARD_UNMATCHED | cli.DOCTOR_WARN_ONLY
    assert not cli.DOCTOR_HARD_UNMATCHED & cli.DOCTOR_WARN_ONLY


def _doctor_vault(tmp_vault, *, backup="/backup"):
    for relative in scaffold.VAULT_DIRS:
        (tmp_vault / relative).mkdir(parents=True, exist_ok=True)
    rv_dir = tmp_vault / ".research-vault"
    rv_dir.mkdir(exist_ok=True)
    (rv_dir / "machine.json").write_text(
        json.dumps({"mailto": "researcher@example.edu", "zotero_backup": backup})
    )
    subprocess.run(
        ["git", "remote", "add", "origin", "https://example.invalid/vault.git"],
        cwd=tmp_vault,
        check=True,
    )
    return tmp_vault


def _ready_client(monkeypatch, versions=READY):
    fake = FakeZotero()
    fake.rpc("api.ready", versions)
    return fake.install(zotero.ZoteroClient(), monkeypatch)


def _profile(tmp_path, *, doi_auto=True, addons=None):
    profile = tmp_path / "profile"
    profile.mkdir()
    if addons is None:
        addons = [
            {
                "id": "better-bibtex@iris-advies.com",
                "type": "extension",
                "location": "app-profile",
                "version": "9.0.63",
                "active": True,
                "appDisabled": False,
            },
            {
                "id": "zoteroshortdoi@wiernik.org",
                "type": "extension",
                "location": "app-profile",
                "version": "1.6.0",
                "active": False,
                "appDisabled": True,
            },
        ]
    (profile / "extensions.json").write_text(json.dumps({"addons": addons}))
    (profile / "prefs.js").write_text(
        'user_pref("extensions.zotero.sync.fulltext.enabled", false);\n'
        'user_pref("extensions.zotero.sync.storage.protocol", "webdav");\n'
        f'user_pref("extensions.shortdoi.autoretrieve", {str(doi_auto).lower()});\n'
        'user_pref("extensions.zotero.pmcid.auto", true);\n'
    )
    return profile


def _doctor_fake(monkeypatch, tmp_path):
    fake = FakeZotero()
    fake.rpc("api.ready", READY)
    # wrong id is intercepted before this
    fake.post("/api/users/0/items", status=401, body=b"")
    fake.get("/api/users/0/items/top?format=csljson&limit=1", status=500, body=b"")
    fake.get(
        "/api/users/0/items?itemType=attachment&limit=50&format=json",
        body=[
            # skipped: not a stored file
            {"key": "Q1W2E3R4", "data": {"linkMode": "imported_url"}},
            {"key": "D7EJ9FTG", "data": {"linkMode": "imported_file"}},
        ],
    )
    fake.get(
        "/api/users/0/items/D7EJ9FTG/file/view/url",
        body=b"file:///D:/Zotero/storage/D7EJ9FTG/a.pdf",
    )
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    return fake, client


def _profiled_vault(tmp_vault, tmp_path, profile):
    vault = _doctor_vault(tmp_vault)
    (vault / ".research-vault" / "machine.json").write_text(
        json.dumps(
            {
                "mailto": "eran@example.edu",
                "zotero_profile": str(profile),
                "path_map": {"D:\\Zotero\\": str(tmp_path) + "/"},
            }
        )
    )
    return vault


def _stored_attachment(tmp_path):
    (tmp_path / "storage" / "D7EJ9FTG").mkdir(parents=True)
    (tmp_path / "storage" / "D7EJ9FTG" / "a.pdf").write_bytes(b"%PDF")


def test_doctor_reports_the_thirteen_probes_in_order(tmp_vault, tmp_path, monkeypatch):
    profile = _profile(tmp_path)
    vault = _profiled_vault(tmp_vault, tmp_path, profile)
    _stored_attachment(tmp_path)
    _fake, client = _doctor_fake(monkeypatch, tmp_path)
    monkeypatch.setattr(
        scaffold,
        "_installed_plugins",
        lambda: {
            COMPILE_PLUGIN: [{"gitCommitSha": "ad67087cad22", "installPath": "/x"}]
        },
    )
    monkeypatch.setattr(scaffold.paths, "_running_in_wsl", lambda: True)

    probes = scaffold.doctor(vault, client=client)

    assert [p.check for p in probes] == PROBE_NAMES
    by = {p.check: p for p in probes}
    assert by["zotero"].result is Result.MATCHED
    assert "server_id=6LpvURP2E933" in by["zotero"].reason
    assert by["write-guard"].result is Result.MATCHED
    assert by["fulltext-sync"].reason == (
        "sync.fulltext.enabled=False storage.protocol=webdav"
    )
    assert by["bbt-git"].result is Result.MATCHED
    assert by["plugins"].result is Result.MATCHED  # DOI Manager is recommended
    assert "zoteroshortdoi@wiernik.org appDisabled" in by["plugins"].reason
    assert by["path-shim"].result is Result.MATCHED
    assert by["translator-formats"].result is Result.MATCHED
    assert by["compile-tool"].result is Result.MATCHED


def test_doctor_distinguishes_local_api_off_from_zotero_down(tmp_vault, monkeypatch):
    vault = _doctor_vault(tmp_vault)
    fake = FakeZotero()
    fake.get("/api/", status=403, body=b"")
    fake.rpc("api.ready", READY)
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    by = {p.check: p for p in scaffold.doctor(vault, client=client)}
    assert by["zotero"].result is Result.UNMATCHED
    assert "preference" in by["zotero"].reason
    assert by["write-guard"].result is Result.SKIPPED
    assert by["bbt"].result is Result.MATCHED  # json-rpc answers with the pref off


def test_doctor_write_guard_fails_when_the_wrong_id_is_not_refused(
    tmp_vault, monkeypatch
):
    vault = _doctor_vault(tmp_vault)
    fake = FakeZotero()
    fake.rpc("api.ready", READY)
    # the server "accepts" the wrong id
    monkeypatch.setattr(fake, "server_id", "research-vault-wrong-id")
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    by = {p.check: p for p in scaffold.doctor(vault, client=client)}
    assert by["write-guard"].result is Result.UNMATCHED


def test_doctor_without_a_profile_skips_rather_than_passes(
    tmp_vault, tmp_path, monkeypatch
):
    vault = _doctor_vault(tmp_vault)
    _fake, client = _doctor_fake(monkeypatch, tmp_path)
    by = {p.check: p for p in scaffold.doctor(vault, client=client)}
    assert by["fulltext-sync"].result is Result.SKIPPED
    assert by["plugins"].result is Result.SKIPPED
    assert by["bbt-git"].result is Result.SKIPPED


def test_doctor_returns_thirteen_tuple_probes_and_repairs_tree(tmp_vault, monkeypatch):
    vault = _doctor_vault(tmp_vault)
    (vault / "projects").rmdir()

    probes = scaffold.doctor(vault, client=_ready_client(monkeypatch))

    assert [probe.check for probe in probes] == PROBE_NAMES
    assert all(isinstance(probe, tuple) and len(probe) == 3 for probe in probes)
    assert (vault / "projects").is_dir()
    assert probes[0].result is Result.MATCHED
    by = {p.check: p for p in probes}
    assert by["zotero"] == scaffold.Probe(
        "zotero",
        Result.MATCHED,
        "zotero=10.0.1 api=3 schema=44 server_id=6LpvURP2E933",
    )
    assert by["bbt"] == scaffold.Probe("bbt", Result.MATCHED, "9.0.63")


def test_doctor_zotero_down_is_unreachable_and_its_dependents_are_skipped(tmp_vault):
    vault = _doctor_vault(tmp_vault)

    # No fake installed: the offline socket guard makes every read an outage.
    probes = scaffold.doctor(vault, client=None)
    by = {p.check: p for p in probes}

    assert [probe.check for probe in probes] == PROBE_NAMES
    assert by["zotero"].result is Result.UNREACHABLE
    assert by["bbt"].result is Result.UNREACHABLE
    assert by["bbt"].reason.startswith("zotero down: ")
    for name in ("write-guard", "translator-formats"):
        assert by[name] == scaffold.Probe(name, Result.SKIPPED, "zotero unreachable")
    assert [probe.check for probe in probes[-2:]] == ["remote", "backup"]


def test_doctor_missing_bbt_reports_unmatched(tmp_vault, monkeypatch):
    vault = _doctor_vault(tmp_vault)

    probes = scaffold.doctor(
        vault, client=_ready_client(monkeypatch, {"zotero": "10.0.1"})
    )

    assert {p.check: p.result for p in probes}["bbt"] is Result.UNMATCHED


def test_doctor_treats_whitespace_bbt_version_as_missing(tmp_vault, monkeypatch):
    vault = _doctor_vault(tmp_vault)

    probes = scaffold.doctor(
        vault,
        client=_ready_client(monkeypatch, {"zotero": "10.0.1", "betterbibtex": "  "}),
    )

    assert {p.check: p.result for p in probes}["bbt"] is Result.UNMATCHED


def test_doctor_scaffold_failure_still_returns_all_thirteen_probes(
    tmp_path, monkeypatch
):
    vault = tmp_path / "missing-vault"
    monkeypatch.setattr(
        scaffold,
        "scaffold_vault",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("cannot create")),
    )

    probes = scaffold.doctor(vault, client=_ready_client(monkeypatch))

    assert [probe.check for probe in probes] == PROBE_NAMES
    assert probes[0].result is Result.UNMATCHED


def test_doctor_classifies_machine_remote_and_backup_conditions(tmp_vault, monkeypatch):
    vault = _doctor_vault(tmp_vault, backup="")
    subprocess.run(["git", "remote", "remove", "origin"], cwd=vault, check=True)
    (vault / ".research-vault" / "machine.json").write_text(
        '{"mailto":"you@example.edu","zotero_backup":""}'
    )

    probes = scaffold.doctor(vault, client=_ready_client(monkeypatch))
    by_check = {probe.check: probe for probe in probes}

    assert by_check["machine-config"].result is Result.UNMATCHED
    assert by_check["remote"] == scaffold.Probe(
        "remote",
        Result.UNMATCHED,
        "no remote — vault endures only on this disk (§2)",
    )
    assert by_check["backup"] == scaffold.Probe(
        "backup",
        Result.UNMATCHED,
        "no stated Zotero storage backup (§2 boundary)",
    )


def test_doctor_bbt_git_warns_when_better_bibtex_may_run_git(
    tmp_vault, tmp_path, monkeypatch
):
    profile = _profile(tmp_path)
    with (profile / "prefs.js").open("a") as prefs:
        prefs.write(
            'user_pref("extensions.zotero.translators.better-bibtex.git", "config");\n'
        )
    vault = _profiled_vault(tmp_vault, tmp_path, profile)

    by = {p.check: p for p in scaffold.doctor(vault, client=_ready_client(monkeypatch))}

    assert by["bbt-git"].result is Result.UNMATCHED
    assert by["bbt-git"].reason.startswith("git=config")


def test_doctor_plugins_fails_on_a_missing_required_addon_and_names_it(
    tmp_vault, tmp_path, monkeypatch
):
    profile = _profile(tmp_path, addons=[])
    vault = _profiled_vault(tmp_vault, tmp_path, profile)

    by = {p.check: p for p in scaffold.doctor(vault, client=_ready_client(monkeypatch))}

    assert by["plugins"] == scaffold.Probe(
        "plugins", Result.UNMATCHED, "Better BibTeX missing"
    )


def test_doctor_plugins_fails_when_an_active_addon_has_automatic_mode_off(
    tmp_vault, tmp_path, monkeypatch
):
    active = {
        "type": "extension",
        "location": "app-profile",
        "active": True,
        "appDisabled": False,
    }
    profile = _profile(
        tmp_path,
        doi_auto=False,
        addons=[
            {"id": "better-bibtex@iris-advies.com", "version": "9.0.63", **active},
            {"id": "zoteroshortdoi@wiernik.org", "version": "1.6.0", **active},
        ],
    )
    vault = _profiled_vault(tmp_vault, tmp_path, profile)

    by = {p.check: p for p in scaffold.doctor(vault, client=_ready_client(monkeypatch))}

    assert by["plugins"] == scaffold.Probe(
        "plugins",
        Result.UNMATCHED,
        "DOI Manager automatic mode off (extensions.shortdoi.autoretrieve)",
    )


def test_doctor_fulltext_sync_reports_zotero_defaults_when_prefs_are_unset(
    tmp_vault, tmp_path, monkeypatch
):
    profile = tmp_path / "profile"
    profile.mkdir()
    (profile / "prefs.js").write_text("")
    (profile / "extensions.json").write_text(json.dumps({"addons": []}))
    vault = _profiled_vault(tmp_vault, tmp_path, profile)

    by = {p.check: p for p in scaffold.doctor(vault, client=_ready_client(monkeypatch))}

    assert by["fulltext-sync"] == scaffold.Probe(
        "fulltext-sync",
        Result.MATCHED,
        "sync.fulltext.enabled=False storage.protocol=zotero",
    )


def test_doctor_path_shim_fails_when_the_resolved_file_is_absent(
    tmp_vault, tmp_path, monkeypatch
):
    vault = _profiled_vault(tmp_vault, tmp_path, _profile(tmp_path))
    _fake, client = _doctor_fake(monkeypatch, tmp_path)
    monkeypatch.setattr(paths, "_running_in_wsl", lambda: True)

    by = {p.check: p for p in scaffold.doctor(vault, client=client)}

    assert by["path-shim"].result is Result.UNMATCHED
    assert by["path-shim"].reason == str(tmp_path / "storage" / "D7EJ9FTG" / "a.pdf")


def test_doctor_path_shim_is_unreachable_without_a_stored_attachment(
    tmp_vault, monkeypatch
):
    vault = _doctor_vault(tmp_vault)
    fake = FakeZotero()
    fake.rpc("api.ready", READY)
    fake.get(
        "/api/users/0/items?itemType=attachment&limit=50&format=json",
        body=[{"key": "Q1W2E3R4", "data": {"linkMode": "imported_url"}}],
    )
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    monkeypatch.setattr(paths, "_running_in_wsl", lambda: True)

    by = {p.check: p for p in scaffold.doctor(vault, client=client)}

    assert by["path-shim"].result is Result.UNREACHABLE
    assert "no stored attachment" in by["path-shim"].reason


def test_doctor_path_shim_is_skipped_outside_wsl(tmp_vault, tmp_path, monkeypatch):
    vault = _doctor_vault(tmp_vault)
    _fake, client = _doctor_fake(monkeypatch, tmp_path)

    by = {p.check: p for p in scaffold.doctor(vault, client=client)}

    assert by["path-shim"] == scaffold.Probe(
        "path-shim", Result.SKIPPED, "not running in WSL"
    )


def test_doctor_translator_formats_warns_when_the_closed_route_reopens(
    tmp_vault, monkeypatch
):
    vault = _doctor_vault(tmp_vault)
    fake = FakeZotero()
    fake.rpc("api.ready", READY)
    fake.get("/api/users/0/items/top?format=csljson&limit=1", status=200, body=[])
    client = fake.install(zotero.ZoteroClient(), monkeypatch)

    by = {p.check: p for p in scaffold.doctor(vault, client=client)}

    assert by["translator-formats"].result is Result.UNMATCHED
    assert "reopened" in by["translator-formats"].reason


@pytest.mark.parametrize(
    ("installed", "expected"),
    [
        ({}, Result.SKIPPED),
        ({COMPILE_PLUGIN: [{"gitCommitSha": "0000000beef"}]}, Result.UNMATCHED),
        ({COMPILE_PLUGIN: [{"gitCommitSha": "ad67087cad22"}]}, Result.MATCHED),
    ],
)
def test_doctor_compile_tool_compares_the_installed_sha_to_the_pin(
    installed, expected, tmp_vault, monkeypatch
):
    vault = _doctor_vault(tmp_vault)
    monkeypatch.setattr(scaffold, "_installed_plugins", lambda: installed)

    by = {p.check: p for p in scaffold.doctor(vault, client=_ready_client(monkeypatch))}

    assert by["compile-tool"].result is expected
    if expected is Result.UNMATCHED:
        assert "0000000" in by["compile-tool"].reason
        assert "ad67087" in by["compile-tool"].reason


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (["doctor", "--base", "http://after", "--vault", "/vault"], "http://after"),
        (["--base", "http://before", "doctor", "--vault", "/vault"], "http://before"),
    ],
)
def test_doctor_base_routes_before_and_after_subcommand(
    argv, expected, monkeypatch, capsys
):
    import research_vault.__main__ as cli

    bases = []

    class FakeClient:
        def __init__(self, base):
            bases.append(base)

    monkeypatch.setattr(cli, "ZoteroClient", FakeClient)
    monkeypatch.setattr(cli, "doctor", lambda vault, client: _probes())

    assert cli.main(argv) == 0
    assert bases == [expected]
    assert len(capsys.readouterr().out.splitlines()) == 13
