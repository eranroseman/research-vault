import argparse
import ast
import json
import subprocess
from pathlib import Path

import pytest

from research_vault import Result, paths, scaffold, zotero
from tests.conftest import package_ast
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
HARD_UNREACHABLE = ["zotero", "bbt", "write-guard", "plugins"]
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
PROFILE_PROBES = ("fulltext-sync", "bbt-git", "plugins")
LISTING = (
    "/api/users/0/items?itemType=attachment&sort=dateAdded&direction=asc"
    "&limit=50&start={start}&format=json"
)


def _linked_rows(start, count=50):
    """A page of attachments that are not stored files."""
    return [
        {"key": f"L{start + i:07d}", "data": {"linkMode": "imported_url"}}
        for i in range(count)
    ]


LOCAL_API_PROBES = ("write-guard", "path-shim", "translator-formats")


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


def test_cmd_doctor_warn_prefix_needs_both_a_warn_only_check_and_a_failure(
    monkeypatch, capsys
):
    """`warn:` marks a warn-only check that failed -- never a hard check's
    failure, never a warn-only check that passed."""
    _code, captured = _run_cmd(monkeypatch, capsys, _probes())
    assert not [line for line in captured.out.splitlines() if line.startswith("warn:")]
    _code, captured = _run_cmd(
        monkeypatch, capsys, _probes(tree=Result.UNMATCHED, remote=Result.UNREACHABLE)
    )
    lines = captured.out.splitlines()
    assert "UNMATCHED tree — tree detail" in lines
    assert "warn:UNREACHABLE remote — remote detail" in lines


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


def _result_literal(node) -> str | None:
    """`Result.<NAME>` as written, or None for any other result expression."""
    if (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "Result"
    ):
        return node.attr
    return None


def _maybe_unreachable_probe_ids() -> set[str]:
    """Every probe id scaffold.py may construct with Result.UNREACHABLE, off the AST.

    The technique of test_config_validity's _probe_ids, keyed on the result
    argument. A Probe whose result is written as any other expression — a
    variable, a NamedTuple field — can carry any result, so it counts too.
    """
    tree = package_ast(Path(scaffold.__file__))
    ids: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or getattr(node.func, "id", None) != "Probe":
            continue
        positional = [
            *node.args,
            *(k.value for k in node.keywords if k.arg == "result"),
        ]
        assert len(positional) >= 2, ast.unparse(node)
        check, result = positional[0], positional[1]
        assert isinstance(check, ast.Constant), ast.unparse(node)
        assert isinstance(check.value, str), ast.unparse(node)
        if _result_literal(result) in {None, "UNREACHABLE"}:
            ids.add(check.value)
    return ids


def test_every_unreachable_row_doctor_can_emit_reaches_an_exit_code_set():
    """An UNREACHABLE row in neither set prints bare and exits 0: an outage as a pass."""
    import research_vault.__main__ as cli

    ids = _maybe_unreachable_probe_ids()
    assert ids, "AST scan found no UNREACHABLE rows — the scan itself is broken"
    unrouted = sorted(ids - (cli.DOCTOR_HARD_UNREACHABLE | cli.DOCTOR_WARN_ONLY))
    assert not unrouted, (
        "probe ids that can emit UNREACHABLE but are in neither "
        f"DOCTOR_HARD_UNREACHABLE nor DOCTOR_WARN_ONLY: {unrouted}"
    )


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
        LISTING.format(start=0),
        body=[
            # skipped: not a stored file
            {"key": "Q1W2E3R4", "data": {"linkMode": "imported_url"}},
            {"key": "D7EJ9FTG", "data": {"linkMode": "imported_file"}},
        ],
        headers={"Total-Results": "2"},
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
            COMPILE_PLUGIN: [{"gitCommitSha": "32ac5a02c4e0", "installPath": "/x"}]
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
    monkeypatch.setattr(paths, "_running_in_wsl", lambda: True)

    by = {p.check: p for p in scaffold.doctor(vault, client=client)}

    assert by["zotero"].result is Result.UNMATCHED
    assert "preference" in by["zotero"].reason
    for name in LOCAL_API_PROBES:
        assert by[name] == scaffold.Probe(
            name, Result.SKIPPED, "local API preference is off"
        )
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


def test_doctor_zotero_down_is_unreachable_and_its_dependents_are_skipped(
    tmp_vault, monkeypatch
):
    vault = _doctor_vault(tmp_vault)
    monkeypatch.setattr(paths, "_running_in_wsl", lambda: True)

    # No fake installed: the offline socket guard makes every read an outage.
    probes = scaffold.doctor(vault, client=None)
    by = {p.check: p for p in probes}

    assert [probe.check for probe in probes] == PROBE_NAMES
    assert by["zotero"].result is Result.UNREACHABLE
    assert by["bbt"].result is Result.UNREACHABLE
    assert by["bbt"].reason.startswith("zotero down: ")
    for name in LOCAL_API_PROBES:
        assert by[name] == scaffold.Probe(name, Result.SKIPPED, "zotero unreachable")
    assert [probe.check for probe in probes[-2:]] == ["remote", "backup"]


def test_doctor_reads_the_remote_of_the_vault_not_of_the_process_cwd(
    tmp_vault, monkeypatch
):
    """The remote probe runs git in the vault: from a cwd that is no repository
    at all it still finds the vault's `origin`."""
    vault = _doctor_vault(tmp_vault)
    monkeypatch.chdir(tmp_vault.parent)
    probes = scaffold.doctor(vault, client=None)
    by = {p.check: p for p in probes}
    assert by["remote"] == scaffold.Probe("remote", Result.MATCHED, "origin")


@pytest.mark.parametrize(
    "local_api_status", [200, 403], ids=["local-api-on", "local-api-off"]
)
def test_doctor_bbt_not_answering_is_a_setup_fault_when_zotero_answered(
    local_api_status, tmp_vault, monkeypatch
):
    vault = _doctor_vault(tmp_vault)
    fake = FakeZotero()
    if local_api_status == 403:
        fake.get("/api/", status=403, body=b"")
    # No api.ready registered: the fake raises ZoteroError, as the real 404 on
    # /better-bibtex/json-rpc does when Better BibTeX is not installed.
    client = fake.install(zotero.ZoteroClient(), monkeypatch)

    by = {p.check: p for p in scaffold.doctor(vault, client=client)}

    assert by["zotero"].result is not Result.UNREACHABLE
    assert by["bbt"].result is Result.UNMATCHED
    assert by["bbt"].reason.startswith("Better BibTeX not answering json-rpc: ")


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
        "sync.fulltext.enabled=unset (Zotero default) "
        "storage.protocol=unset (Zotero default)",
    )


def test_doctor_reports_a_zotero_profile_that_is_not_a_string(tmp_vault, monkeypatch):
    vault = _doctor_vault(tmp_vault)
    (vault / ".research-vault" / "machine.json").write_text(
        json.dumps({"mailto": "eran@example.edu", "zotero_profile": 42})
    )

    by = {p.check: p for p in scaffold.doctor(vault, client=_ready_client(monkeypatch))}

    for name in PROFILE_PROBES:
        assert by[name] == scaffold.Probe(
            name, Result.UNMATCHED, "zotero_profile must be a string"
        )


@pytest.mark.parametrize("value", [None, "", "  "], ids=["null", "empty", "blank"])
def test_doctor_treats_a_null_or_empty_zotero_profile_as_not_configured(
    value, tmp_vault, monkeypatch
):
    vault = _doctor_vault(tmp_vault)
    (vault / ".research-vault" / "machine.json").write_text(
        json.dumps({"mailto": "eran@example.edu", "zotero_profile": value})
    )

    by = {p.check: p for p in scaffold.doctor(vault, client=_ready_client(monkeypatch))}

    for name in PROFILE_PROBES:
        assert by[name] == scaffold.Probe(
            name, Result.SKIPPED, "zotero_profile not configured"
        )


def test_doctor_reports_a_zotero_profile_that_is_not_a_directory(
    tmp_vault, tmp_path, monkeypatch
):
    missing = tmp_path / "no-such-profile"
    vault = _profiled_vault(tmp_vault, tmp_path, missing)

    by = {p.check: p for p in scaffold.doctor(vault, client=_ready_client(monkeypatch))}

    for name in PROFILE_PROBES:
        assert by[name] == scaffold.Probe(
            name, Result.UNMATCHED, f"zotero_profile {missing} is not a directory"
        )


def test_doctor_reports_an_unreadable_prefs_js_as_an_outage(
    tmp_vault, tmp_path, monkeypatch
):
    profile = tmp_path / "profile"
    profile.mkdir()  # no prefs.js: could not read, no verdict on content nobody saw
    (profile / "extensions.json").write_text(json.dumps({"addons": []}))
    vault = _profiled_vault(tmp_vault, tmp_path, profile)

    by = {p.check: p for p in scaffold.doctor(vault, client=_ready_client(monkeypatch))}

    for name in PROFILE_PROBES:
        assert by[name].result is Result.UNREACHABLE
        assert by[name].reason.startswith("prefs.js unreadable: ")


def test_doctor_reports_an_unparseable_prefs_js_as_a_fault(
    tmp_vault, tmp_path, monkeypatch
):
    profile = _profile(tmp_path)
    (profile / "prefs.js").write_bytes(b"\xff\xfe not utf-8")
    vault = _profiled_vault(tmp_vault, tmp_path, profile)

    by = {p.check: p for p in scaffold.doctor(vault, client=_ready_client(monkeypatch))}

    for name in PROFILE_PROBES:
        assert by[name].result is Result.UNMATCHED
        assert by[name].reason.startswith("prefs.js unparseable: ")


def test_doctor_plugins_unreadable_extensions_json_is_an_outage(
    tmp_vault, tmp_path, monkeypatch
):
    profile = _profile(tmp_path)
    (profile / "extensions.json").unlink()
    vault = _profiled_vault(tmp_vault, tmp_path, profile)

    by = {p.check: p for p in scaffold.doctor(vault, client=_ready_client(monkeypatch))}

    assert by["plugins"].result is Result.UNREACHABLE
    assert by["plugins"].reason.startswith("extensions.json unreadable: ")
    assert by["fulltext-sync"].result is Result.MATCHED  # prefs.js itself was fine


@pytest.mark.parametrize(
    "content", ["{not json", "[]"], ids=["not-json", "not-an-object"]
)
def test_doctor_plugins_malformed_extensions_json_is_a_fault(
    content, tmp_vault, tmp_path, monkeypatch
):
    profile = _profile(tmp_path)
    (profile / "extensions.json").write_text(content)
    vault = _profiled_vault(tmp_vault, tmp_path, profile)

    by = {p.check: p for p in scaffold.doctor(vault, client=_ready_client(monkeypatch))}

    assert by["plugins"].result is Result.UNMATCHED
    assert by["plugins"].reason.startswith("extensions.json malformed: ")


def test_doctor_path_shim_fails_when_the_resolved_file_is_absent(
    tmp_vault, tmp_path, monkeypatch
):
    vault = _profiled_vault(tmp_vault, tmp_path, _profile(tmp_path))
    _fake, client = _doctor_fake(monkeypatch, tmp_path)
    monkeypatch.setattr(paths, "_running_in_wsl", lambda: True)

    by = {p.check: p for p in scaffold.doctor(vault, client=client)}

    assert by["path-shim"].result is Result.UNMATCHED
    assert by["path-shim"].reason == (
        f"{tmp_path / 'storage' / 'D7EJ9FTG' / 'a.pdf'} does not exist"
    )


@pytest.mark.parametrize(
    ("rows", "headers", "reason"),
    [
        ([], {"Total-Results": "0"}, "no stored attachment among the first 0 of 0"),
        (
            _linked_rows(0, 1),
            {"Total-Results": "1"},
            "no stored attachment among the first 1 of 1",
        ),
        (
            _linked_rows(0, 1),
            {},
            "no stored attachment among the first 1 (total unreported)",
        ),
    ],
    ids=["empty-library", "linked-only", "no-total-results-header"],
)
def test_doctor_path_shim_is_skipped_without_a_stored_attachment_and_names_the_span(
    rows, headers, reason, tmp_vault, monkeypatch
):
    vault = _doctor_vault(tmp_vault)
    fake = FakeZotero()
    fake.rpc("api.ready", READY)
    fake.get(LISTING.format(start=0), body=rows, headers=headers)
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    monkeypatch.setattr(paths, "_running_in_wsl", lambda: True)

    by = {p.check: p for p in scaffold.doctor(vault, client=client)}

    # nothing to check is not an outage; a short page ends the walk
    assert by["path-shim"] == scaffold.Probe("path-shim", Result.SKIPPED, reason)
    listing_calls = [c for c in fake.calls if c[1].startswith("/api/users/0/items?")]
    assert [c[1] for c in listing_calls] == [LISTING.format(start=0)]


def test_doctor_path_shim_walks_to_a_stored_file_on_the_second_page(
    tmp_vault, tmp_path, monkeypatch
):
    vault = _profiled_vault(tmp_vault, tmp_path, _profile(tmp_path))
    _stored_attachment(tmp_path)
    fake = FakeZotero()
    fake.rpc("api.ready", READY)
    fake.get(
        LISTING.format(start=0), body=_linked_rows(0), headers={"Total-Results": "51"}
    )
    fake.get(
        LISTING.format(start=50),
        body=[{"key": "D7EJ9FTG", "data": {"linkMode": "imported_file"}}],
        headers={"Total-Results": "51"},
    )
    fake.get(
        "/api/users/0/items/D7EJ9FTG/file/view/url",
        body=b"file:///D:/Zotero/storage/D7EJ9FTG/a.pdf",
    )
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    monkeypatch.setattr(paths, "_running_in_wsl", lambda: True)

    by = {p.check: p for p in scaffold.doctor(vault, client=client)}

    assert by["path-shim"].result is Result.MATCHED
    listing_calls = [c[1] for c in fake.calls if c[1].startswith("/api/users/0/items?")]
    assert listing_calls == [LISTING.format(start=0), LISTING.format(start=50)]


def test_doctor_path_shim_caps_the_walk_at_twenty_pages(tmp_vault, monkeypatch):
    vault = _doctor_vault(tmp_vault)
    fake = FakeZotero()
    fake.rpc("api.ready", READY)
    for page in range(21):  # a 21st page exists and must not be read
        start = page * 50
        fake.get(
            LISTING.format(start=start),
            body=_linked_rows(start),
            headers={"Total-Results": "1372"},
        )
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    monkeypatch.setattr(paths, "_running_in_wsl", lambda: True)

    by = {p.check: p for p in scaffold.doctor(vault, client=client)}

    assert by["path-shim"] == scaffold.Probe(
        "path-shim",
        Result.SKIPPED,
        "no stored attachment among the first 1000 of 1372",
    )
    listing_calls = [c[1] for c in fake.calls if c[1].startswith("/api/users/0/items?")]
    assert listing_calls == [LISTING.format(start=page * 50) for page in range(20)]


@pytest.mark.parametrize("failing_page", [0, 1], ids=["first-page", "second-page"])
def test_doctor_path_shim_listing_failure_is_an_outage(
    failing_page, tmp_vault, monkeypatch
):
    vault = _doctor_vault(tmp_vault)
    fake = FakeZotero()
    fake.rpc("api.ready", READY)
    fake.get(
        LISTING.format(start=0), body=_linked_rows(0), headers={"Total-Results": "60"}
    )
    fake.get(LISTING.format(start=failing_page * 50), status=500, body=b"")
    client = fake.install(zotero.ZoteroClient(), monkeypatch)
    monkeypatch.setattr(paths, "_running_in_wsl", lambda: True)

    by = {p.check: p for p in scaffold.doctor(vault, client=client)}

    assert by["path-shim"].result is Result.UNREACHABLE
    assert "500" in by["path-shim"].reason


def test_doctor_path_shim_reports_a_malformed_machine_json_instead_of_raising(
    tmp_vault, tmp_path, monkeypatch
):
    # `machine-config` is the reporter for this file; the shim, which reads it
    # again through paths.to_local, must not turn the same fault into a traceback.
    vault = _doctor_vault(tmp_vault)
    (vault / ".research-vault" / "machine.json").write_text("{not json")
    _fake, client = _doctor_fake(monkeypatch, tmp_path)
    monkeypatch.setattr(paths, "_running_in_wsl", lambda: True)

    probes = scaffold.doctor(vault, client=client)
    by = {p.check: p for p in probes}

    assert [p.check for p in probes] == PROBE_NAMES
    assert by["machine-config"].result is Result.UNMATCHED
    assert by["path-shim"].result is Result.UNMATCHED
    # The reason names the file and the fault class, not a bare str(error).
    assert by["path-shim"].reason.startswith("machine.json path_map: ")


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
        ({COMPILE_PLUGIN: [{"gitCommitSha": "32ac5a02c4e0"}]}, Result.MATCHED),
        # An installed record without a sha is malformed: UNMATCHED, and the
        # reason says so rather than printing `at , pin is` (row 42).
        ({COMPILE_PLUGIN: [{"installPath": "/x"}]}, Result.UNMATCHED),
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
        assert "32ac5a0" in by["compile-tool"].reason
        record = installed[COMPILE_PLUGIN][0]
        if "gitCommitSha" in record:
            assert "0000000" in by["compile-tool"].reason
        else:
            assert "has no gitCommitSha" in by["compile-tool"].reason


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


# --- boundaries pinned against mutation survivors -----------------------------


def test_compile_tool_probe_names_the_seven_char_sha_and_reads_an_empty_record_list(
    monkeypatch,
):
    monkeypatch.setattr(
        scaffold,
        "_installed_plugins",
        lambda: {COMPILE_PLUGIN: [{"gitCommitSha": "32ac5a02c4e0"}]},
    )
    probe = scaffold._compile_tool_probe()
    assert (probe.check, probe.result, probe.reason) == (
        "compile-tool",
        Result.MATCHED,
        f"{COMPILE_PLUGIN} at 32ac5a0",
    )
    monkeypatch.setattr(scaffold, "_installed_plugins", lambda: {COMPILE_PLUGIN: []})
    probe = scaffold._compile_tool_probe()
    assert (probe.result, probe.reason) == (
        Result.SKIPPED,
        f"{COMPILE_PLUGIN} not installed",
    )


def test_doctor_tree_refuses_a_stray_literatures_directory_without_creating_the_new_root(
    tmp_vault, monkeypatch
):
    """An old vault (`literatures/`, before the 2026-09-17 rename): the tree
    probe would otherwise scaffold an empty `literature/` beside the populated
    old root and report MATCHED. It reports the stray root instead, and the
    scaffold-inside-doctor does not run while it exists."""
    import shutil

    vault = _doctor_vault(tmp_vault)
    shutil.move(vault / "literature", vault / "literatures")
    (vault / "literatures" / "smith2020.md").write_text(
        '---\ntype: "literature"\n---\n'
    )

    by = {p.check: p for p in scaffold.doctor(vault, client=_ready_client(monkeypatch))}

    assert by["tree"].result is Result.UNMATCHED
    assert by["tree"].reason == (
        "stray literatures/: rename to literature/ by hand, then run capture --all"
    )
    assert not (vault / "literature").exists()
    assert (vault / "literatures" / "smith2020.md").is_file()


def test_doctor_tree_refuses_when_both_roots_exist(tmp_vault, monkeypatch):
    vault = _doctor_vault(tmp_vault)
    (vault / "literatures").mkdir()

    by = {p.check: p for p in scaffold.doctor(vault, client=_ready_client(monkeypatch))}

    assert by["tree"].result is Result.UNMATCHED
    assert by["tree"].reason.startswith("stray literatures/: ")
