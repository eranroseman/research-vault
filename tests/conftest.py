import ast
import json as _json
import os
import re
import shutil
import socket
import subprocess
import urllib.parse
from pathlib import Path
from typing import AnyStr

import pytest

from research_vault import scaffold, zotero


def must_replace(text: AnyStr, old: AnyStr, new: AnyStr, count: int = 1) -> AnyStr:
    """str.replace that refuses to be a no-op: a fixture edit that removes `old` must fail loudly.

    ``text``, ``old`` and ``new`` are all ``str`` or all ``bytes``.
    """
    assert old in text, f"substitution target no longer in the fixture: {old!r}"
    return text.replace(old, new, count)


# The generated siblings mutmut writes next to every function in its mutants/
# copy of the package: `<mangled>__mutmut_<N>` carries one mutation each (a
# literal among them), `<mangled>__mutmut_orig` is the pristine copy. The
# trampoline stub keeps the original name and body.
_MUTMUT_SIBLING = re.compile(r"__mutmut_(?:\d+|orig)$")


def package_ast(path: Path) -> ast.Module:
    """Parse a package module for inventory, mutmut's generated siblings pruned.

    A test that reads literals or defs off a module's AST runs, under the
    mutation gate, against mutmut's schemata copy of that module, where every
    function has mutant siblings with mutated literals: a `Probe("XXidXX")`
    among them would read as an ungoverned id. Pruning the siblings (module
    level and inside class bodies) leaves exactly the original's defs.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))

    def keep(node: ast.stmt) -> bool:
        return not (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and _MUTMUT_SIBLING.search(node.name)
        )

    tree.body = [node for node in tree.body if keep(node)]
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            node.body = [child for child in node.body if keep(child)]
    return tree


def _with_body_witness(text):
    from research_vault import notes

    digest = notes.body_sha256(text)
    return must_replace(
        text,
        'type: "literature"\n',
        f'type: "literature"\nmanaged-sha256: "{digest}"\n',
    )


# --- a HOME of the suite's own -----------------------------------------------

# The identity every offline commit is made under, as GLOBAL git config in the
# test's HOME -- not GIT_AUTHOR_* / GIT_COMMITTER_* variables, which outrank a
# local `user.name` and would defeat the tests that set one and assert it; a
# developer's shell exporting them is scrubbed for the same reason (below).
OFFLINE_GIT_IDENTITY = ("research-vault-offline-suite", "offline-suite@example.invalid")

# What outranks the `.gitconfig` in a HOME, so an export of any of these on the
# machine would reach the suite's commits over the synthetic identity: the
# config-location family (and the numbered GIT_CONFIG_KEY_n / GIT_CONFIG_VALUE_n
# pairs GIT_CONFIG_COUNT introduces, found at call time), the identity family,
# and the template directory a `git init` would seed hooks from.
GIT_HOME_OVERRIDES = (
    "GIT_CONFIG_GLOBAL",
    "GIT_CONFIG_SYSTEM",
    "GIT_CONFIG_NOSYSTEM",
    "GIT_CONFIG_COUNT",
    "GIT_AUTHOR_NAME",
    "GIT_AUTHOR_EMAIL",
    "GIT_AUTHOR_DATE",
    "GIT_COMMITTER_NAME",
    "GIT_COMMITTER_EMAIL",
    "GIT_COMMITTER_DATE",
    "GIT_TEMPLATE_DIR",
)


def _make_home(root: Path) -> tuple[dict[str, str], tuple[str, ...]]:
    """Populate `root` as a HOME the suite can run under and return the
    environment entries that point a process at it, and the keys that must
    be absent for it to be the HOME git reads (GIT_HOME_OVERRIDES, plus every
    numbered GIT_CONFIG_KEY_n / GIT_CONFIG_VALUE_n present). What is there: a
    `.gitconfig` carrying the synthetic identity (CI writes the same shape with
    `git config --global`). What is not: everything else a test could read
    from the operator's home -- the plugin registry doctor's compile-tool
    probe opens, git's global excludes and `init.templateDir`, credential
    helpers -- so an answer never depends on the machine running the test."""
    name, email = OFFLINE_GIT_IDENTITY
    (root / ".gitconfig").write_text(
        f"[user]\n\tname = {name}\n\temail = {email}\n", encoding="utf-8"
    )
    (root / ".config").mkdir()
    numbered = sorted(
        key
        for key in os.environ
        if key.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))
    )
    entries = {"HOME": str(root), "XDG_CONFIG_HOME": str(root / ".config")}
    return entries, (*GIT_HOME_OVERRIDES, *numbered)


def _home_env(root: Path) -> dict[str, str]:
    """`os.environ` as a process under the HOME at `root` gets it: the
    overrides removed, the home entries set."""
    entries, remove = _make_home(root)
    return {**{k: v for k, v in os.environ.items() if k not in remove}, **entries}


@pytest.fixture(scope="session")
def _suite_home_env(tmp_path_factory):
    """The environment the session-scoped template vaults are built under:
    the same kind of HOME every test runs under (below), so a global setting
    on the developer's machine never reaches the tree each test copies."""
    return _home_env(tmp_path_factory.mktemp("suite-home"))


@pytest.fixture(autouse=True)
def _per_test_home(request, monkeypatch, tmp_path_factory):
    """An unmarked test runs under a HOME of its own: `Path.home()`, `~` and
    `$XDG_CONFIG_HOME` resolve into a fresh directory holding only the
    synthetic git identity, for the test and for every subprocess it launches;
    the git variables that would outrank that identity (GIT_HOME_OVERRIDES)
    are removed from the environment for the test's duration.

    The class of leak this closes is the one the socket block closes for the
    network: measured 2026-09-14 on the mutation gate's first CI run, a
    mutant of the plugin-registry read was killed on the developer's machine
    (a registry exists under the real home) and survived on the runner (none
    does) -- a covering test that reads outside the repository is not a
    covering test. The marker is the mechanism, per test, as for the socket
    block: a ``live`` or ``live_net`` test keeps the real HOME on purpose (the
    operator's registry and profile paths are what a live leg reads); every
    other test is redirected in every run, live flags or not.

    Returns the home, so a test can seed it (the registry fixture in
    tests/test_scaffold.py). Removed at teardown -- the retained artefact of a
    failed test is its vault, and the identity is in the commits.
    """
    if request.node.get_closest_marker("live") or request.node.get_closest_marker(
        "live_net"
    ):
        yield None
        return
    home = tmp_path_factory.mktemp("home")
    entries, remove = _make_home(home)
    for key in remove:
        monkeypatch.delenv(key, raising=False)
    for key, value in entries.items():
        monkeypatch.setenv(key, value)
    yield home
    shutil.rmtree(home, ignore_errors=True)


# --- the vault templates -----------------------------------------------------


def _build_bare_vault(root: Path, env: dict[str, str]) -> None:
    for d in scaffold.VAULT_DIRS:
        (root / d).mkdir(parents=True)
    (root / "wiki" / "concepts").mkdir(parents=True)
    # `--template=`: no sample hooks, description or info/exclude — 16 files
    # nothing reads, copied per test otherwise. A copied entry is ~0.2 ms on
    # WSL2 (copytree micro-bench, 2026-09-13), so entry count is the cost.
    subprocess.run(["git", "init", "-q", "--template="], cwd=root, check=True, env=env)


def _copy_vault(template: Path, tmp_path: Path) -> Path:
    # Into `tmp_path` itself, not a child of it: tests read the vault root and
    # `tmp_path` as one directory (`tmp_path.parent / f"{tmp_path.name}-x"` is
    # "outside the vault"). `.git` copies fine; symlinks stay symlinks.
    shutil.copytree(template, tmp_path, symlinks=True, dirs_exist_ok=True)
    return tmp_path


@pytest.fixture(scope="session")
def _bare_vault_template(tmp_path_factory, _suite_home_env):
    """One bare vault per xdist worker: the tree plus `git init`, built once.

    The git processes were the fixture cost (`init` here; `add` + `commit` too
    for the fixture vault), one to three per test. Every test gets its own
    copy; the template is never handed out.
    """
    template = tmp_path_factory.mktemp("bare-vault-template")
    _build_bare_vault(template, _suite_home_env)
    return template


@pytest.fixture(scope="session")
def _fixture_vault_template(tmp_path_factory, _suite_home_env):
    template = tmp_path_factory.mktemp("fixture-vault-template")
    _build_bare_vault(template, _suite_home_env)
    _populate_fixture_vault(template, _suite_home_env)
    # One pack in place of 16 loose objects in 16 fan-out directories.
    subprocess.run(
        ["git", "repack", "-adq"], cwd=template, check=True, env=_suite_home_env
    )
    return template


@pytest.fixture
def tmp_vault(tmp_path, _bare_vault_template):
    return _copy_vault(_bare_vault_template, tmp_path)


@pytest.fixture
def fixture_vault(tmp_path, _fixture_vault_template):
    return _copy_vault(_fixture_vault_template, tmp_path)


def _populate_fixture_vault(tmp_vault: Path, env: dict[str, str]) -> None:
    (tmp_vault / "index.md").write_text(
        '---\nokf_version: "0.2"\n---\n# Knowledge bundle\n'
    )
    (tmp_vault / "log.md").write_text("# Log\n")
    literature = tmp_vault / "literatures"
    (literature / "smith2020.md").write_text(
        _with_body_witness("""---
type: "literature"
title: "Mortality decline"
aliases:
  - "Mortality decline"
itemType: "journalArticle"
DOI: "10.1000/xyz"
zotero-server-id: "6LpvURP2E933"
zotero-item-key: "SMITH020"
zotero-item-version: 12
citationKey: "smith2020"
attachments:
  - {key: "ATT00001", version: 13, md5: "aa11aa11aa11aa11aa11aa11aa11aa11", contentType: "application/pdf", filename: "smith2020.pdf"}
fulltext:
  - {attachment-key: "ATT00001", sha256: "aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11"}
compile-input-sha256: "aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11"
accessed: "2026-08-16"
generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}
---
# Mortality decline

- (quote) [@smith2020, p. 12] ^c-11111111
  > Mortality fell 12% across all strata.
- (paraphrase) Retrospective design [@smith2020, p. 3] ^c-22222222
""")
    )
    (literature / "gone2019.md").write_text(
        _with_body_witness("""---
type: "literature"
title: "Old result"
aliases:
  - "Old result"
itemType: "journalArticle"
DOI: "10.1000/old"
zotero-server-id: "6LpvURP2E933"
zotero-item-key: "GONE2019"
zotero-item-version: 7
citationKey: "gone2019"
attachments:
fulltext:
accessed: "2026-08-16"
generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}
---
# Old result
""")
    )
    (tmp_vault / "wiki" / "concepts" / "mortality-trends.md").write_text(
        """---
title: "Mortality trends"
type: "concept"
status: "draft"
generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}
---
- (inference) Decline is robust [confidence:: moderate] [supports:: [[smith2020#^c-11111111]]] [disputes:: [[gone2019#^c-22222222]]] ^c-55555555
"""
    )
    project = tmp_vault / "projects" / "brief"
    project.mkdir()
    (project / "draft.md").write_text(
        """---
title: "Evidence brief"
type: "project"
status: "draft"
generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}
---
- (quote) [@smith2020, p. 12] ^c-66666666
  > Mortality fell 12% across all strata.
- (inference) This will replicate [@fabricated2020] ^c-77777777
"""
    )
    bibliography = [
        {
            "id": "gone2019",
            "title": "Old result",
            "type": "article-journal",
            "DOI": "10.1000/old",
            "author": [{"family": "Gone", "given": "Ann"}],
            "issued": {"date-parts": [[2019]]},
        },
        {
            "id": "smith2020",
            "title": "Mortality decline",
            "type": "article-journal",
            "DOI": "10.1000/xyz",
            "author": [{"family": "Smith", "given": "Jo"}],
            "issued": {"date-parts": [[2020]]},
        },
    ]
    (tmp_vault / "system" / "bibliography.json").write_text(
        _json.dumps(bibliography, indent=1)
    )
    (tmp_vault / "log" / "2026-08-16.md").write_text(
        '---\ntype: "daily"\n---\n- 09:00 human:eran — imported smith2020\n'
    )
    (tmp_vault / "inbox" / "review-queue.md").write_text(
        '---\ntype: "review-queue"\n---\n'
    )
    subprocess.run(["git", "add", "-A"], cwd=tmp_vault, check=True, env=env)
    subprocess.run(
        ["git", "commit", "-q", "-m", "fixture vault"],
        cwd=tmp_vault,
        check=True,
        env=env,
    )


@pytest.fixture
def net_vault(fixture_vault):
    rv_dir = fixture_vault / ".research-vault"
    rv_dir.mkdir(exist_ok=True)
    (rv_dir / "machine.json").write_text('{"mailto": "eran@example.edu"}')
    return fixture_vault


@pytest.fixture
def net_vault_real_mailto(fixture_vault):
    rv_dir = fixture_vault / ".research-vault"
    rv_dir.mkdir(exist_ok=True)
    (rv_dir / "machine.json").write_text(
        _json.dumps({"mailto": os.environ.get("RV_MAILTO", "")})
    )
    return fixture_vault


def pytest_collection_modifyitems(config, items):
    skip_live = pytest.mark.skip(reason="live Zotero not enabled (RV_LIVE=1)")
    skip_net = pytest.mark.skip(reason="live network not enabled (RV_LIVE_NET=1)")
    for item in items:
        if "live" in item.keywords and os.environ.get("RV_LIVE") != "1":
            item.add_marker(skip_live)
        if "live_net" in item.keywords and os.environ.get("RV_LIVE_NET") != "1":
            item.add_marker(skip_net)
    skip_write = pytest.mark.skip(
        reason="write-capable live leg not enabled (RV_LIVE_WRITE_BASE=http://localhost:23129)"
    )
    for item in items:
        if "live_write" in item.keywords and not os.environ.get("RV_LIVE_WRITE_BASE"):
            item.add_marker(skip_write)


@pytest.fixture(autouse=True)
def _no_zotero_socket(request, monkeypatch):
    """The offline suite never reaches a Zotero: an unpatched read is an outage.

    Both instances run on the author's machine, so an unguarded read would pass
    or fail with whatever happens to be live — and verify's lifecycle leg opens
    a client on every network-capable run. Fakes install at instance level and
    shadow this; live legs (``RV_LIVE=1``) keep the real transport.
    """
    if request.node.get_closest_marker("live"):
        return
    from research_vault import zotero

    def refused(self, url, *_args, **_kwargs):
        raise zotero.ZoteroError(f"Zotero unreachable in the offline suite: {url}")

    monkeypatch.setattr(zotero.ZoteroClient, "_http", refused)


class SocketBlockedError(RuntimeError):
    """An offline test opened a TCP connection, or resolved a name for one.

    Deliberately not an ``OSError``: the transports catch that and dress it
    as an outage, which is exactly how a leak would stay invisible.
    """


# Loopback by name or literal — one endpoint, however a base URL spells it.
_LOOPBACK_NAMES = frozenset({"localhost", "127.0.0.1", "::1"})
# The hosts a name lookup may answer for in the offline suite: no host, and
# loopback. Every other name is a leak, blocked before it leaves the process.
_LOOPBACK_HOSTS = _LOOPBACK_NAMES | {None, ""}


def _endpoint(base: str) -> tuple[str | None, int | None]:
    """A base URL's (host, port), every loopback spelling folded to one name."""
    parts = urllib.parse.urlsplit(base)
    host = parts.hostname
    return ("loopback" if host in _LOOPBACK_NAMES else host), parts.port


def is_production_base(base: str) -> bool:
    """Whether ``base`` names the production Zotero instance — by endpoint,
    not by string: ``http://127.0.0.1:23119`` is ``zotero.DEFAULT_BASE`` by
    another loopback spelling, and the write legs must refuse it too."""
    return _endpoint(base) == _endpoint(zotero.DEFAULT_BASE)


@pytest.fixture(autouse=True)
def _no_socket(request, monkeypatch):
    """An unmarked test is socket-blocked: its TCP connect raises, naming the
    address — never a real connection, never a quiet outage — and so does a
    name lookup outside loopback, because ``urllib`` resolves through
    ``socket.getaddrinfo`` before it connects: without this, a leaked hostname
    is a real DNS query on a networked machine and a ``gaierror`` (an outage
    to the transports) on one without DNS, the machine-dependent visibility
    the block exists to remove.

    ``_no_zotero_socket`` gives a Zotero read a Zotero-shaped outage; this is
    the belt under it, so a new client class cannot reopen the hole. Unix
    sockets and socketpairs are not connects to block; xdist workers talk over
    pipes. The marker is the mechanism, per test: a ``live`` or ``live_net``
    test keeps the real transport (the collection hook has already skipped it
    unless its flag is set); every other test is blocked in every run, so a
    live run cannot leak a connection an offline run would have caught.

    Returns the test's allowlist: ``dead_base`` adds the loopback address it
    proved dead, so a test of the real transport meets a real refusal.
    """
    allowed: set[tuple[str, int]] = set()
    if request.node.get_closest_marker("live") or request.node.get_closest_marker(
        "live_net"
    ):
        return allowed

    def blocked(what: str, host, port) -> SocketBlockedError:
        return SocketBlockedError(
            f"{what} blocked in the offline suite: {host}:{port}"
            " — a test that needs the network carries a `live` or"
            " `live_net` marker (tests/conftest.py::_no_socket)"
        )

    def guarded(real):
        def connect(self, address):
            if self.family in (socket.AF_INET, socket.AF_INET6):
                host, port = address[0], address[1]
                if (host, port) not in allowed:
                    raise blocked("socket connect", host, port)
            return real(self, address)

        return connect

    real_getaddrinfo = socket.getaddrinfo

    # The real function's signature, `type` included: callers pass it by keyword.
    def getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):  # noqa: A002
        name = host.decode("ascii", "replace") if isinstance(host, bytes) else host
        if name not in _LOOPBACK_HOSTS and name not in {h for h, _ in allowed}:
            raise blocked("name resolution", name, port)
        return real_getaddrinfo(host, port, family, type, proto, flags)

    monkeypatch.setattr(socket.socket, "connect", guarded(socket.socket.connect))
    monkeypatch.setattr(socket.socket, "connect_ex", guarded(socket.socket.connect_ex))
    monkeypatch.setattr(socket, "getaddrinfo", getaddrinfo)
    return allowed


@pytest.fixture
def dead_base(_no_socket):
    """A base URL nothing listens on: an ephemeral port, bound and released.

    A connect there is refused at once; port 1 hangs for the whole connect
    timeout under WSL2 (docs/agents/testing.md, "The WSL2 low-port trap"). This is
    the base for every test that needs a real refusal — in-process, where the
    socket block lets this one address through, or through a subprocess CLI,
    which no in-process patch can reach.
    """
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    _no_socket.add(("127.0.0.1", port))
    return f"http://127.0.0.1:{port}"
