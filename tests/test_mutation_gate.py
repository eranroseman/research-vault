"""Unit tests for the no-new-survivors mutation gate over mutmut.

No real mutmut run: the tests fake mutmut's on-disk artifacts (a schemata file
under mutants/<relpath> and its .meta JSON) in a tmp tree and read them through
the gate, which reads them through mutmut's own readers. The launcher subprocess
is faked at subprocess.run. Every test is satisfiable from inside a mutants/
copy of this repo (nothing here reads a committed file through the gate's ROOT),
because the gate's own tests run in mutmut's stats phase.
"""

import argparse
import ast
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import scripts.mutation_gate as mutation_gate
from scripts.mutation_gate import (
    ModuleResult,
    SourceTreeChangedError,
    baseline_keys,
    changed_modules,
    mutation_key,
    mutation_text,
    new_survivors,
    read_module_results,
)

# A schemata file in the shape mutmut 3.7.0 writes to mutants/<relpath>: the
# trampoline stub keeps the original name and body, `<mangled>__mutmut_orig` is
# the pristine copy, `<mangled>__mutmut_<N>` are the mutants. A method's
# mangled name carries the class between CLASS_NAME_SEPARATOR characters.
FAKE_SCHEMATA = """\
from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict

mutants_x_add__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_add__mutmut)
def add(a, b):
    return a + b


def x_add__mutmut_orig(a, b):
    return a + b


def x_add__mutmut_1(a, b):
    return a - b


def x_add__mutmut_2(a, b):
    return a * b


def x_add__mutmut_3(a, b):
    return None


class Box:
    def size(self):
        return 1

    def xǁBoxǁsize__mutmut_orig(self):
        return 1

    def xǁBoxǁsize__mutmut_1(self):
        return 2
"""

MODULE = "research_vault/fake.py"
ADD_1 = "research_vault.fake.x_add__mutmut_1"
ADD_2 = "research_vault.fake.x_add__mutmut_2"
ADD_3 = "research_vault.fake.x_add__mutmut_3"
SIZE_1 = "research_vault.fake.xǁBoxǁsize__mutmut_1"

KEY_ADD_1 = f"{MODULE}::func/add::-    return a + b\\n+    return a - b"
KEY_ADD_2 = f"{MODULE}::func/add::-    return a + b\\n+    return a * b"
KEY_ADD_3 = f"{MODULE}::func/add::-    return a + b\\n+    return None"
KEY_SIZE_1 = f"{MODULE}::func/Box.size::-    return 1\\n+    return 2"

# The gate's real read of the inherited RLIMIT_AS, captured before the fixture
# below replaces it for every test here.
_REAL_GETRLIMIT = mutation_gate._getrlimit


@pytest.fixture(autouse=True)
def _unlimited_inherited_address_space(monkeypatch):
    """Every test here also runs inside mutmut's stats phase, in-process,
    under whatever --child-address-space the enclosing gate set (CI: 3 GiB);
    the pre-check would read that cap as the hard limit and refuse the 4 GiB
    default every launch below uses (measured 2026-09-14, run 34822363722:
    all ten changed modules errored on this file's first launching test). So
    the seam reports no limit unless a test sets one itself."""
    infinity = mutation_gate.resource.RLIM_INFINITY
    monkeypatch.setattr(
        mutation_gate, "_getrlimit", lambda _which: (infinity, infinity)
    )


def _fake_root(tmp_path: Path) -> Path:
    """A tmp repo root mutmut's readers accept: a pyproject.toml carrying
    [tool.mutmut] (mutmut loads its config from the cwd at import time -- the
    gate chdirs there -- and the loaded Config is a process singleton, so this
    file is what keeps these tests order-independent under xdist), plus the
    two source trees the gate hashes and sweeps."""
    (tmp_path / "pyproject.toml").write_text(
        '[tool.mutmut]\nsource_paths = [ "research_vault" ]\n', encoding="utf-8"
    )
    (tmp_path / "research_vault").mkdir()
    (tmp_path / "tests").mkdir()
    return tmp_path


def _fake_module(root: Path, relpath: str, codes: dict[str, int | None]) -> None:
    """Write the schemata + .meta pair mutmut leaves behind for one module."""
    target = root / "mutants" / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    schemata = FAKE_SCHEMATA.replace(
        "research_vault.fake", relpath[:-3].replace("/", ".")
    )
    target.write_text(schemata, encoding="utf-8")
    module = relpath[:-3].replace("/", ".")
    (root / "mutants" / f"{relpath}.meta").write_text(
        json.dumps(
            {
                "exit_code_by_key": {
                    name.replace("research_vault.fake", module): code
                    for name, code in codes.items()
                },
                "hash_by_function_name": {},
                "type_check_error_by_key": {},
                "durations_by_key": {},
                "estimated_durations_by_key": {},
            }
        ),
        encoding="utf-8",
    )


# --- key format ------------------------------------------------------------


def test_mutation_text_keeps_only_the_diff_body_lines_on_one_line():
    """Header lines, hunk headers and context are dropped; the `-`/`+` lines
    survive verbatim (marker and indentation included), in order, joined by a
    literal backslash-n so a multi-line hunk is still one baseline line."""
    diff = (
        "--- research_vault/x.py\n"
        "+++ research_vault/x.py\n"
        "@@ -1,5 +1,4 @@\n"
        " def f(x):\n"
        "-    if x:\n"
        "-        return 1\n"
        "+    if not x:\n"
        "     return 2"
    )
    text = mutation_text(diff)
    assert text == "-    if x:\\n-        return 1\\n+    if not x:"
    assert "\n" not in text


def test_mutation_text_keeps_a_body_line_that_itself_begins_with_two_dashes():
    """The file headers are dropped by position, never by prefix: a removed
    code line whose text begins `--` (its diff line then begins `---`) is body,
    and so is an added `++`-prefixed one."""
    diff = "--- p\n+++ p\n@@ -1,2 +1,2 @@\n def f(x):\n---x\n+++x"
    assert mutation_text(diff) == "---x\\n+++x"


def test_mutation_key_names_the_function_never_the_positional_mutant_id(tmp_path):
    """Keyed through mutmut's own name parser under the tmp root's config --
    nothing here reads the real pyproject.toml."""
    diff = "--- p\n+++ p\n@@ -1,2 +1,2 @@\n def add(a, b):\n-    return a + b\n+    return a - b"
    key = mutation_key(
        MODULE, "research_vault.fake.x_add__mutmut_17", diff, root=_fake_root(tmp_path)
    )
    assert key == KEY_ADD_1
    assert "mutmut_17" not in key


def test_mutation_key_qualifies_a_method_with_its_class(tmp_path):
    diff = (
        "--- p\n+++ p\n@@ -1,2 +1,2 @@\n def size(self):\n-    return 1\n+    return 2"
    )
    assert mutation_key(MODULE, SIZE_1, diff, root=_fake_root(tmp_path)) == KEY_SIZE_1


# --- reading mutmut's artifacts ----------------------------------------------


def test_read_module_results_extracts_survivors_and_counts_from_faked_artifacts(
    tmp_path,
):
    """Through mutmut's own get_diff_for_mutant: the schemata file is parsed
    for the `__mutmut_orig` / `__mutmut_<N>` pair, so a key here is exactly
    what a real run would write."""
    root = _fake_root(tmp_path)
    _fake_module(root, MODULE, {ADD_1: 0, ADD_2: 1, ADD_3: 33, SIZE_1: 0})

    result = read_module_results(MODULE, root=root)

    assert result.survivors == {KEY_ADD_1, KEY_SIZE_1}
    assert result.counts == {"survived": 2, "killed": 1, "no tests": 1}
    assert result.flagged == []
    assert result.no_verdict == []


def test_read_module_results_reports_timeouts_by_name_not_as_survivors(tmp_path):
    """A timeout (a mutant that hangs the tests) or a type-check catch is a
    verdict the mutant caused, and must stay visible: named, counted, never a
    survivor and never silently folded into killed."""
    root = _fake_root(tmp_path)
    _fake_module(root, MODULE, {ADD_1: 36, ADD_2: 37, ADD_3: 1, SIZE_1: 1})

    result = read_module_results(MODULE, root=root)

    assert result.survivors == set()
    assert result.counts == {"timeout": 1, "caught by type check": 1, "killed": 2}
    assert result.flagged == [
        ("timeout", ADD_1, KEY_ADD_1),
        ("caught by type check", ADD_2, KEY_ADD_2),
    ]
    assert result.no_verdict == []


def test_read_module_results_marks_mutants_without_a_verdict(tmp_path):
    """Four codes are the ABSENCE of a verdict, not one: `null` (not checked)
    and 2 (interrupted) -- mutmut swallows a KeyboardInterrupt and still
    exits 0 -- plus `suspicious` (a code mutmut cannot classify, e.g. pytest's
    usage-error 4) and `segfault` (-9, the OOM killer's SIGKILL; -11). An
    incomplete measurement the gate must refuse, never read as zero
    survivors."""
    root = _fake_root(tmp_path)
    _fake_module(root, MODULE, {ADD_1: None, ADD_2: 2, ADD_3: 4, SIZE_1: -9})

    result = read_module_results(MODULE, root=root)

    assert result.no_verdict == [
        ("not checked", ADD_1),
        ("check was interrupted by user", ADD_2),
        ("suspicious", ADD_3),
        ("segfault", SIZE_1),
    ]
    assert result.survivors == set()
    assert result.flagged == []


def test_read_module_results_missing_meta_raises(tmp_path):
    """No .meta is no measurement; it must never parse as a clean module."""
    root = _fake_root(tmp_path)
    (root / "mutants" / "research_vault").mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        read_module_results(MODULE, root=root)


@pytest.mark.parametrize(
    ("body", "fault"),
    [
        ('{"exit_code_by_key": {"research_vault.fake.x_add__mutmut_1": 0', "record"),
        ('{"hash_by_function_name": {}}', "record"),
        ('{"exit_code_by_key": [1, 2]}', "record"),
        (
            '{"exit_code_by_key": {"research_vault.fake.add": 0}}',
            "'research_vault.fake.add'",
        ),
        (
            '{"exit_code_by_key": {"research_vault.fake.x_gone__mutmut_1": 0}}',
            "'research_vault.fake.x_gone__mutmut_1'",
        ),
        ('{"exit_code_by_key": {"research_vault.fake.x_add__mutmut_1": [0]}}', "[0]"),
    ],
    ids=[
        "truncated",
        "no-exit-codes",
        "not-a-mapping",
        "no-mutmut-in-name",
        "absent-from-schemata",
        "unhashable-code",
    ],
)
def test_read_module_results_names_a_malformed_meta_as_a_read_error(
    tmp_path, body, fault
):
    """A .meta that exists but is not mutmut's record -- truncated JSON, no
    exit_code_by_key, a mutant name its readers cannot resolve, a code that
    is no exit code -- is a MetaReadError naming the file and the fault, never
    a traceback and never a clean module."""
    root = _fake_root(tmp_path)
    _fake_module(root, MODULE, {ADD_1: 0})
    (root / "mutants" / f"{MODULE}.meta").write_text(body, encoding="utf-8")
    with pytest.raises(mutation_gate.MetaReadError) as caught:
        read_module_results(MODULE, root=root)
    assert f"{MODULE}.meta" in str(caught.value)
    assert fault in str(caught.value)


def test_a_malformed_meta_classes_only_its_module_error_and_the_rest_still_run(
    tmp_path, monkeypatch, capsys
):
    """Through main(), both modes: the offending module reads `error` with the
    fault on its own class line, gets a record, and the modules after it are
    still measured -- the loop is not torn down by the read."""
    root = _fake_root(tmp_path)
    out_dir = root / "records"
    a, b, c = "research_vault/a.py", "research_vault/b.py", "research_vault/c.py"
    for module in (a, b, c):
        _fake_module(root, module, {ADD_1: 1, ADD_2: 1, ADD_3: 1, SIZE_1: 1})
    (root / "mutants" / f"{b}.meta").write_text('{"nothing": 1}', encoding="utf-8")
    calls: list[str] = []
    _fake_measurement(root, monkeypatch, calls)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [a, b, c])
    baseline_path = _argv_baseline(monkeypatch, root, out_dir)

    assert mutation_gate.main() == 1
    assert calls == [a, b, c]
    assert not baseline_path.exists()
    out = capsys.readouterr().out
    assert (
        f"[baseline] {b}: error (mutmut exited 0; no result read: "
        f"{root / 'mutants' / b}.meta: not mutmut's record (" in out
    )
    assert f"[baseline] FAIL {b}" in out
    assert f"[baseline] {c}: ok" in out
    assert "[baseline]   error (1): research_vault/b.py" in out
    assert (out_dir / "research_vault__b.py.exit").read_text(encoding="utf-8") == (
        "0 error"
    )
    assert (out_dir / "research_vault__c.py.exit").read_text(encoding="utf-8") == "0 ok"

    calls.clear()
    monkeypatch.setattr(mutation_gate, "changed_modules", lambda base, **_: [a, b, c])
    _argv_gate(monkeypatch, root)
    assert mutation_gate.main() == 1
    assert calls == [a, b, c]
    out = capsys.readouterr().out
    assert f"[gate] {b}: error (mutmut exited 0; no result read: " in out
    assert "not mutmut's record" in out
    assert "[gate]   error (1): research_vault/b.py" in out


# --- baseline compare --------------------------------------------------------


def test_new_survivors_ignores_baselined_keys():
    assert new_survivors({KEY_ADD_1, KEY_SIZE_1}, {KEY_ADD_1}) == {KEY_SIZE_1}


def test_baseline_round_trip(tmp_path: Path):
    path = tmp_path / "mutation-baseline.txt"
    keys = {KEY_ADD_1, KEY_SIZE_1}
    path.write_text("\n".join(sorted(keys)) + "\n", encoding="utf-8")
    assert baseline_keys(path) == keys


def test_baseline_missing_file_is_empty(tmp_path: Path):
    assert baseline_keys(tmp_path / "absent.txt") == set()


def test_baseline_keys_skips_comment_header_and_tolerates_module_keys(tmp_path):
    """A '#' header is metadata, never a key; a `::module::` key from the
    retired predecessor's era (the gate header names it) is still a line
    (mutmut never produces one, so it simply never matches a found survivor)."""
    path = tmp_path / "mutation-baseline.txt"
    path.write_text(
        "# mutation-baseline.txt -- header\n\n"
        f"{KEY_ADD_1}\n"
        "research_vault/inbox.py::module::True -> False\n",
        encoding="utf-8",
    )
    assert baseline_keys(path) == {
        KEY_ADD_1,
        "research_vault/inbox.py::module::True -> False",
    }


def test_baseline_reasons_pairs_each_reason_with_the_key_beneath_it(tmp_path):
    path = tmp_path / "mutation-baseline.txt"
    path.write_text(
        "# mutation-baseline.txt -- header\n"
        "# reason: a docstring, prose to a human\n"
        f"{KEY_ADD_1}\n"
        f"{KEY_ADD_2}\n"
        "# reason: encoding alias\n"
        f"{KEY_SIZE_1}\n",
        encoding="utf-8",
    )
    assert mutation_gate.baseline_reasons(path) == {
        KEY_ADD_1: "a docstring, prose to a human",
        KEY_SIZE_1: "encoding alias",
    }
    assert baseline_keys(path) == {KEY_ADD_1, KEY_ADD_2, KEY_SIZE_1}
    assert mutation_gate.baseline_reasons(tmp_path / "absent.txt") == {}


@pytest.mark.parametrize(
    "tail",
    ["", "\n", "# another comment\n", "# reason: two in a row\n" + KEY_ADD_1 + "\n"],
    ids=["eof", "blank", "comment", "double"],
)
def test_a_dangling_reason_is_an_error_naming_its_line(tmp_path, tail):
    path = tmp_path / "mutation-baseline.txt"
    path.write_text(f"{KEY_ADD_2}\n# reason: dangling\n{tail}", encoding="utf-8")
    with pytest.raises(mutation_gate.BaselineFormatError) as caught:
        mutation_gate.baseline_reasons(path)
    assert str(caught.value).startswith(f"{path}:2: ")
    assert isinstance(caught.value, mutation_gate.GateAbortError)


def test_read_module_results_records_every_generated_key(tmp_path):
    """Killed, survived, no tests: each carries a key, so the writer can tell
    a reason whose key was killed (dropped, correctly) from one whose key no
    mutant of the run produced (reported)."""
    root = _fake_root(tmp_path)
    _fake_module(root, MODULE, {ADD_1: 0, ADD_2: 1, ADD_3: 33, SIZE_1: 1})
    result = read_module_results(MODULE, root)
    assert result.survivors == {KEY_ADD_1}
    assert result.generated == {KEY_ADD_1, KEY_ADD_2, KEY_ADD_3, KEY_SIZE_1}


def test_changed_modules_lists_modified_core_files(tmp_path: Path):
    """The one function deciding whether the gate ever runs must be proven live:
    a wrong pathspec makes the diff silently empty and the gate passes forever."""
    repo = tmp_path / "repo"
    (repo / "research_vault").mkdir(parents=True)

    def git(*argv: str) -> None:
        subprocess.run(["git", *argv], cwd=repo, check=True, capture_output=True)

    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@example.invalid")
    git("config", "user.name", "t")
    (repo / "research_vault" / "x.py").write_text("A = 1\n", encoding="utf-8")
    (repo / "research_vault" / "__init__.py").write_text("", encoding="utf-8")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    git("checkout", "-q", "-b", "feature")
    (repo / "research_vault" / "x.py").write_text("A = 2\n", encoding="utf-8")
    (repo / "research_vault" / "__init__.py").write_text("B = 1\n", encoding="utf-8")
    git("commit", "-q", "-a", "-m", "change")

    assert changed_modules("main", cwd=repo) == ["research_vault/x.py"]


def test_changed_modules_aborts_with_the_command_when_base_does_not_resolve(
    tmp_path: Path,
):
    """Real git. A --base that is no ref (a shallow clone without origin/main)
    makes the diff fail: the gate's own GitCommandError, naming the command
    (the ref inside it), the exit code and git's stderr -- not the
    CalledProcessError's traceback."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, capture_output=True)

    with pytest.raises(mutation_gate.GitCommandError) as caught:
        changed_modules("no-such-ref", cwd=repo)
    message = str(caught.value)
    assert message.startswith("`git diff --name-only --relative no-such-ref...HEAD")
    assert "exited 128: " in message
    assert "no-such-ref" in message.split("exited 128: ", 1)[1]  # git's stderr
    assert "\n" not in message
    assert isinstance(caught.value, mutation_gate.GateAbortError)
    assert isinstance(caught.value.__cause__, subprocess.CalledProcessError)


def _dirty_repo(tmp_path: Path) -> Path:
    """The `test_changed_modules_lists_modified_core_files` shape with `A = 2`
    staged over a committed `A = 1`: the selection would read the commits
    (nothing changed since `main`) while the measurement reads the tree."""
    repo = tmp_path / "repo"
    (repo / "research_vault").mkdir(parents=True)
    (repo / "tests").mkdir()

    def git(*argv: str) -> None:
        subprocess.run(["git", *argv], cwd=repo, check=True, capture_output=True)

    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@example.invalid")
    git("config", "user.name", "t")
    (repo / "research_vault" / "x.py").write_text("A = 1\n", encoding="utf-8")
    (repo / "research_vault" / "__init__.py").write_text("", encoding="utf-8")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    (repo / "research_vault" / "x.py").write_text("A = 2\n", encoding="utf-8")
    git("add", "research_vault/x.py")
    return repo


def test_changed_modules_refuses_a_dirty_tree_naming_the_path(tmp_path: Path):
    """Gate mode selects from `<base>...HEAD` and measures the working tree,
    so an uncommitted change measures nothing and would read as a pass (#133).
    The refusal names the path and says what to do."""
    repo = _dirty_repo(tmp_path)
    with pytest.raises(mutation_gate.DirtyTreeError) as caught:
        changed_modules("main", cwd=repo)
    message = str(caught.value)
    assert "research_vault/x.py" in message
    assert "commit first" in message
    assert isinstance(caught.value, mutation_gate.GateAbortError)


def test_gate_main_aborts_on_a_dirty_tree(tmp_path: Path, monkeypatch, capsys):
    repo = _dirty_repo(tmp_path)
    monkeypatch.setattr(mutation_gate, "ROOT", repo)
    monkeypatch.setattr(mutation_gate, "_run_mutmut", _fail_if_called)
    monkeypatch.setattr(
        sys,
        "argv",
        ["mutation_gate.py", "--base", "main", "--baseline", str(repo / "b.txt")],
    )
    assert mutation_gate.main() == 1
    out = capsys.readouterr().out
    assert out.startswith("[gate] ABORT: ")
    assert "research_vault/x.py" in out


def test_update_baseline_refuses_a_dirty_tree_before_measuring(
    tmp_path: Path, monkeypatch, capsys
):
    repo = _dirty_repo(tmp_path)
    monkeypatch.setattr(mutation_gate, "ROOT", repo)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: ["research_vault/x.py"])
    monkeypatch.setattr(mutation_gate, "_run_mutmut", _fail_if_called)
    monkeypatch.setattr(
        sys,
        "argv",
        ["mutation_gate.py", "--update-baseline", "--baseline", str(repo / "b.txt")],
    )
    assert mutation_gate.main() == 1
    out = capsys.readouterr().out
    assert out.startswith("[baseline] ABORT: ")
    assert "research_vault/x.py" in out
    assert not (repo / "b.txt").exists()


def test_a_clean_tree_passes_the_refusal(tmp_path: Path):
    repo = _dirty_repo(tmp_path)
    subprocess.run(["git", "commit", "-q", "-m", "committed"], cwd=repo, check=True)
    mutation_gate._refuse_dirty_tree(repo)  # no raise
    assert changed_modules("main", cwd=repo) == []


# --- the mutmut invocation ---------------------------------------------------


def _completed(cmd, code: int = 0) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(cmd, code, stdout="mutmut out", stderr="")


def _fail_if_called(*_args, **_kwargs):
    raise AssertionError("must not be called")


def _record_runs(monkeypatch) -> list[dict]:
    """Fake subprocess.run at the gate's one seam; every call (the git init
    that isolates mutants/, the rev-parse that verifies an existing
    mutants/.git -- answered as git would for an own repository -- and the
    launcher) lands in the returned list as {"cmd": argv, **kwargs}."""
    calls: list[dict] = []

    def fake_run(cmd, **kwargs):
        calls.append({"cmd": cmd, **kwargs})
        if cmd[-1] == "--git-common-dir":
            return subprocess.CompletedProcess(cmd, 0, stdout=".git\n", stderr="")
        return _completed(cmd)

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


def _launcher_call(calls: list[dict]) -> dict:
    (call,) = [c for c in calls if c["cmd"][1:2] == [str(mutation_gate.LAUNCHER)]]
    return call


def test_run_mutmut_invokes_the_launcher_with_pattern_env_and_cwd(
    tmp_path, monkeypatch
):
    """The launcher shim, the module's name pattern, --max-children passed
    through, cwd at the repo root (mutmut reads [tool.mutmut] from the cwd),
    PYTHONDONTWRITEBYTECODE=1, and the shims directory PREPENDED to PYTHONPATH
    as an absolute path: test subprocesses change cwd, so a relative entry
    would stop resolving in exactly the processes sitecustomize exists for."""
    root = _fake_root(tmp_path)
    calls = _record_runs(monkeypatch)
    monkeypatch.setenv("PYTHONPATH", "/elsewhere")

    out, code = mutation_gate._run_mutmut("research_vault/x.py", 6, root=root)

    assert (out, code) == ("mutmut out", 0)
    seen = _launcher_call(calls)
    assert seen["cmd"] == [
        sys.executable,
        str(mutation_gate.LAUNCHER),
        "research_vault.x.*",
        "--max-children",
        "6",
    ]
    assert mutation_gate.LAUNCHER.is_absolute()
    assert seen["cwd"] == root
    env = seen["env"]
    assert env["PYTHONDONTWRITEBYTECODE"] == "1"
    assert env["PYTHONPATH"] == f"{mutation_gate.SHIMS}{os.pathsep}/elsewhere"
    assert mutation_gate.SHIMS.is_absolute()
    assert "PATH" in env  # inherited, not replaced


def test_run_mutmut_caps_the_address_space_of_the_mutmut_process_and_its_children(
    tmp_path, monkeypatch
):
    """RLIMIT_AS, soft and hard, set in the preexec_fn of the launcher process
    -- mutmut forks its per-mutant children from there, so they inherit it and
    a runaway-allocation mutant dies by MemoryError (pytest exit 1, killed)
    instead of the cgroup OOM-killing the whole run. The preexec is called
    here in-process against a recorder; the real setrlimit never runs under
    pytest."""
    root = _fake_root(tmp_path)
    calls = _record_runs(monkeypatch)
    limits: list = []
    monkeypatch.setattr(
        mutation_gate.resource, "setrlimit", lambda *args: limits.append(args)
    )
    cap = mutation_gate.parse_size("2.5GiB")

    mutation_gate._run_mutmut("research_vault/x.py", 2, root=root, address_space=cap)

    preexec = _launcher_call(calls)["preexec_fn"]
    assert limits == []  # applied in the child, never in the gate's process
    preexec()
    assert cap == 2_684_354_560
    assert limits == [(mutation_gate.resource.RLIMIT_AS, (cap, cap))]


def test_git_isolation_refuses_a_symlinked_mutants_before_touching_anything(
    tmp_path, monkeypatch, capsys
):
    """Real symlink. `root/mutants -> victim`, where victim/.git is a gitfile:
    without the refusal, mkdir(exist_ok=True) accepts the link, the gitfile is
    "not own", unlinked, and `git init` runs over the victim (measured
    2026-09-14 -- had the link pointed at the root, that is the worktree's
    own gitfile). The gate aborts naming the path, in both modes, and the victim's
    gitfile bytes are untouched; no mutants/.git appears. Through _run_mutmut
    the refusal comes before the pycache sweep, which walks mutants/ too: a
    __pycache__ under the victim survives."""
    root = tmp_path / "root"
    root.mkdir()
    victim = tmp_path / "victim"
    victim.mkdir()
    gitfile = victim / ".git"
    gitfile.write_text("gitdir: /elsewhere/.git\n")
    (victim / "__pycache__").mkdir()
    (root / "mutants").symlink_to(victim)

    with pytest.raises(mutation_gate.MutantsTreeError, match="mutants") as caught:
        mutation_gate._isolate_git(root)
    assert isinstance(caught.value, mutation_gate.GateAbortError)
    assert str(root / "mutants") in str(caught.value)
    assert gitfile.read_text() == "gitdir: /elsewhere/.git\n"
    assert not (victim / "mutants").exists()
    assert (root / "mutants").is_symlink()

    # A plain file where the directory should be is refused the same way.
    (root / "mutants").unlink()
    (root / "mutants").write_text("not a directory\n")
    with pytest.raises(mutation_gate.MutantsTreeError):
        mutation_gate._isolate_git(root)
    assert (root / "mutants").read_text() == "not a directory\n"

    # Through main(), in both modes: the gate's own ABORT line, exit 1.
    (root / "mutants").unlink()
    (root / "mutants").symlink_to(victim)
    fake = _fake_root(root)
    a = "research_vault/a.py"
    monkeypatch.setattr(mutation_gate, "ROOT", fake)
    # A fake root is no repository: the dirty-tree refusal is pinned by its
    # own tests against a real one, and stands aside here.
    monkeypatch.setattr(mutation_gate, "_refuse_dirty_tree", lambda cwd: None)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [a])
    baseline_path = _argv_baseline(monkeypatch, fake)
    assert mutation_gate.main() == 1
    assert not baseline_path.exists()
    out = capsys.readouterr().out
    assert f"[baseline] ABORT: {fake / 'mutants'} is not a real directory" in out
    monkeypatch.setattr(mutation_gate, "changed_modules", lambda base, **_: [a])
    _argv_gate(monkeypatch, fake)
    assert mutation_gate.main() == 1
    assert f"[gate] ABORT: {fake / 'mutants'} is not a real directory" in (
        capsys.readouterr().out
    )
    assert gitfile.read_text() == "gitdir: /elsewhere/.git\n"
    assert not (victim / "HEAD").exists()
    assert (victim / "__pycache__").is_dir()  # the sweep never crossed the link


def test_run_mutmut_refuses_a_cap_above_the_inherited_hard_limit(tmp_path, monkeypatch):
    """setrlimit in the child can only lower the hard limit: a cap above the
    inherited RLIMIT_AS hard limit is refused before anything is launched --
    the gate's own ChildLimitError naming both numbers, no subprocess, no
    git init -- while an unlimited hard limit, or one at/above the cap, lets
    the launch proceed."""
    root = _fake_root(tmp_path)
    calls = _record_runs(monkeypatch)
    cap = mutation_gate.parse_size("4GiB")
    # The seam's default is the real read; the tests replace it (autouse
    # fixture above) so the inherited limit never decides a test's outcome.
    assert _REAL_GETRLIMIT is mutation_gate.resource.getrlimit
    monkeypatch.setattr(mutation_gate, "_getrlimit", lambda _which: (cap, cap - 1))

    with pytest.raises(mutation_gate.ChildLimitError, match=f"{cap}.*{cap - 1}"):
        mutation_gate._run_mutmut(
            "research_vault/x.py", 6, root=root, address_space=cap
        )
    assert calls == []
    assert not (root / "mutants").exists()

    infinity = mutation_gate.resource.RLIM_INFINITY
    for limits in ((infinity, infinity), (cap, cap), (cap - 1, cap + 1)):
        monkeypatch.setattr(mutation_gate, "_getrlimit", lambda _w, pair=limits: pair)
        calls.clear()
        mutation_gate._run_mutmut(
            "research_vault/x.py", 6, root=root, address_space=cap
        )
        assert _launcher_call(calls)["preexec_fn"] is not None


def test_run_mutmut_reports_a_refused_preexec_as_a_gate_abort(tmp_path, monkeypatch):
    """A preexec_fn that raises reaches the parent as subprocess.SubprocessError
    ("Exception occurred in preexec_fn."): it becomes ChildLimitError, the
    gate's abort, carrying the module, the cap and the cause -- and the
    source-tree window is not misreported."""
    root = _fake_root(tmp_path)
    calls = _record_runs(monkeypatch)
    cap = mutation_gate.parse_size("2.5GiB")

    def refusing_run(cmd, **kwargs):
        calls.append({"cmd": cmd, **kwargs})
        if kwargs.get("preexec_fn") is not None:
            raise subprocess.SubprocessError("Exception occurred in preexec_fn.")
        return _completed(cmd)

    monkeypatch.setattr(subprocess, "run", refusing_run)

    with pytest.raises(mutation_gate.ChildLimitError) as caught:
        mutation_gate._run_mutmut(
            "research_vault/x.py", 2, root=root, address_space=cap
        )
    assert str(caught.value) == (
        f"research_vault/x.py: launching mutmut under --child-address-space {cap} "
        "failed: Exception occurred in preexec_fn."
    )
    assert isinstance(caught.value.__cause__, subprocess.SubprocessError)
    assert isinstance(caught.value, mutation_gate.GateAbortError)


def test_a_child_limit_failure_is_the_gates_abort_line_in_both_modes(
    tmp_path, monkeypatch, capsys
):
    """main() prints `[baseline] ABORT: ...` / `[gate] ABORT: ...` and returns
    1 for a ChildLimitError exactly as for a source-tree change -- no
    traceback, and no baseline written."""
    root = _fake_root(tmp_path)
    a = "research_vault/a.py"
    monkeypatch.setattr(mutation_gate, "ROOT", root)
    # A fake root is no repository: the dirty-tree refusal is pinned by its
    # own tests against a real one, and stands aside here.
    monkeypatch.setattr(mutation_gate, "_refuse_dirty_tree", lambda cwd: None)

    def fake_run_mutmut(relpath, max_children, root=root, address_space=None):
        raise mutation_gate.ChildLimitError("--child-address-space 4 exceeds ...")

    monkeypatch.setattr(mutation_gate, "_run_mutmut", fake_run_mutmut)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [a])
    baseline_path = _argv_baseline(monkeypatch, root)
    assert mutation_gate.main() == 1
    assert not baseline_path.exists()
    assert "[baseline] ABORT: --child-address-space 4 exceeds ..." in (
        capsys.readouterr().out
    )

    monkeypatch.setattr(mutation_gate, "changed_modules", lambda base, **_: [a])
    _argv_gate(monkeypatch, root)
    assert mutation_gate.main() == 1
    assert "[gate] ABORT: --child-address-space 4 exceeds ..." in (
        capsys.readouterr().out
    )


def test_parse_size_reads_bytes_and_binary_suffixes():
    parse = mutation_gate.parse_size
    assert parse("4GiB") == 4 << 30
    assert parse("2.5GiB") == 2_684_354_560
    assert parse("512MiB") == 512 << 20
    assert parse("1073741824") == 1 << 30
    assert mutation_gate.DEFAULT_ADDRESS_SPACE == "4GiB"
    for bad in ("4GB", "4G", "GiB", "abc", "0", "-1", "1.5"):
        with pytest.raises(argparse.ArgumentTypeError):
            parse(bad)


def test_run_mutmut_isolates_git_from_the_repository(tmp_path, monkeypatch):
    """The env the launcher gets carries GIT_CEILING_DIRECTORIES=<root> and no
    GIT_CONFIG_* injection (a core.hooksPath override was measured to break
    the scaffold tests and to share one hook across every child), and
    mutants/ is made its own repository first, `--template=` so nothing seeds
    hooks into it, and the init itself runs under the same env; a second
    invocation finds mutants/.git, verifies it with `rev-parse
    --git-common-dir` under that env, and inits nothing."""
    root = _fake_root(tmp_path)
    calls = _record_runs(monkeypatch)

    mutation_gate._run_mutmut("research_vault/x.py", 4, root=root)

    env = _launcher_call(calls)["env"]
    assert env["GIT_CEILING_DIRECTORIES"] == str(root)
    assert not any(key.startswith("GIT_CONFIG") for key in env)
    assert calls[0]["cmd"] == [
        "git",
        "init",
        "-q",
        "--template=",
        str(root / "mutants"),
    ]
    assert calls[0]["check"] is True
    assert calls[0]["env"]["GIT_CEILING_DIRECTORIES"] == str(root)
    (root / "mutants" / ".git").mkdir()  # the fake ran no git; stand in for it
    calls.clear()
    mutation_gate._run_mutmut("research_vault/x.py", 4, root=root)
    assert [c["cmd"] for c in calls][:-1] == [
        ["git", "-C", str(root / "mutants"), "rev-parse", "--git-common-dir"]
    ]
    assert calls[0]["env"]["GIT_CEILING_DIRECTORIES"] == str(root)
    assert calls[-1]["cmd"][:2] == [sys.executable, str(mutation_gate.LAUNCHER)]
    assert (root / "mutants" / ".git").is_dir()  # verified as own, kept


def test_run_mutmut_drops_the_inherited_git_location_variables(tmp_path, monkeypatch):
    """GIT_DIR, GIT_WORK_TREE, GIT_COMMON_DIR or GIT_INDEX_FILE inherited by
    the launcher would name a repository outright and bypass the ceiling:
    none reaches the launcher, the init, or the verification probe."""
    root = _fake_root(tmp_path)
    for name in mutation_gate.GIT_LOCATION_VARS:
        monkeypatch.setenv(name, f"/elsewhere/{name.lower()}")
    monkeypatch.setenv("GIT_AUTHOR_NAME", "kept")  # not a location variable
    calls = _record_runs(monkeypatch)

    mutation_gate._run_mutmut("research_vault/x.py", 4, root=root)
    (root / "mutants" / ".git").mkdir()
    mutation_gate._run_mutmut("research_vault/x.py", 4, root=root)

    assert mutation_gate.GIT_LOCATION_VARS == (
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_COMMON_DIR",
        "GIT_INDEX_FILE",
    )
    assert len(calls) == 4  # init, launcher, probe, launcher
    for call in calls:
        assert not set(mutation_gate.GIT_LOCATION_VARS) & set(call["env"])
        assert call["env"]["GIT_AUTHOR_NAME"] == "kept"
        assert call["env"]["GIT_CEILING_DIRECTORIES"] == str(root)


def test_a_failed_git_init_of_mutants_is_the_gates_abort_not_a_traceback(
    tmp_path, monkeypatch
):
    """The isolation's `git init` failing (an unwritable root, a git that
    refuses) is GitCommandError -- the command, the exit code and git's
    stderr on one line -- raised before any launch; the init keeps check=True
    so the failure cannot pass as a made repository."""
    root = _fake_root(tmp_path)
    calls: list[dict] = []

    def refusing_run(cmd, **kwargs):
        calls.append({"cmd": cmd, **kwargs})
        if cmd[:2] == ["git", "init"]:
            raise subprocess.CalledProcessError(
                128,
                cmd,
                output="",
                stderr="fatal: cannot mkdir .git: Permission denied\n",
            )
        return _completed(cmd)

    monkeypatch.setattr(subprocess, "run", refusing_run)

    with pytest.raises(mutation_gate.GitCommandError) as caught:
        mutation_gate._run_mutmut("research_vault/x.py", 4, root=root)
    assert str(caught.value) == (
        f"`git init -q --template= {root / 'mutants'}` exited 128: "
        "fatal: cannot mkdir .git: Permission denied"
    )
    assert isinstance(caught.value, mutation_gate.GateAbortError)
    assert [c["cmd"][:2] for c in calls] == [["git", "init"]]  # no launcher
    assert calls[0]["check"] is True


@pytest.mark.parametrize("shape", ["gitfile-elsewhere", "garbage-head", "symlink"])
def test_git_isolation_replaces_a_mutants_git_that_is_not_its_own(tmp_path, shape):
    """Real git. A pre-seeded mutants/.git that is a gitfile pointing at another
    repository, a directory git no longer reads as a repository (`git init`
    over it leaves the garbage HEAD in place -- measured), or a symlink to
    another repository's .git is removed and mutants/ initialised afresh: the
    common dir resolves to mutants/.git itself, the other repository is
    untouched, and an own repository is then kept, not re-initialised."""
    root = tmp_path / "root"
    mutants = root / "mutants"
    mutants.mkdir(parents=True)
    elsewhere = tmp_path / "elsewhere"
    subprocess.run(
        ["git", "init", "-q", str(elsewhere)], check=True, capture_output=True
    )
    (elsewhere / ".git" / "marker").write_text("untouched\n")
    dot_git = mutants / ".git"
    if shape == "gitfile-elsewhere":
        dot_git.write_text(f"gitdir: {elsewhere / '.git'}\n")
    elif shape == "garbage-head":
        dot_git.mkdir()
        (dot_git / "HEAD").write_text("garbage\n")
    else:
        dot_git.symlink_to(elsewhere / ".git")

    env = {**mutation_gate._git_env(root), **mutation_gate._isolate_git(root)}

    def common_dir() -> Path:
        probe = subprocess.run(
            ["git", "-C", str(mutants), "rev-parse", "--git-common-dir"],
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        return (mutants / probe.stdout.strip()).resolve()

    assert dot_git.is_dir()
    assert not dot_git.is_symlink()
    assert common_dir() == dot_git.resolve()
    assert not (dot_git / "hooks").exists()  # --template=
    assert (elsewhere / ".git" / "marker").read_text() == "untouched\n"
    assert (elsewhere / ".git" / "HEAD").exists()
    head_before = (dot_git / "HEAD").read_bytes()
    (dot_git / "own-marker").write_text("kept\n")
    mutation_gate._isolate_git(root)  # own now: verified, not replaced
    assert (dot_git / "own-marker").read_text() == "kept\n"
    assert (dot_git / "HEAD").read_bytes() == head_before


def test_git_isolation_contains_hook_paths_under_mutants_and_walls_off_the_root(
    tmp_path,
):
    """The measured escape, with real git: `git rev-parse --git-path
    hooks/pre-commit` from under mutants/ resolves inside mutants/.git, and
    from anywhere else under the root it finds no repository at all -- never
    the one enclosing the root -- while the root itself (mutmut's own cwd)
    and a repository outside it are untouched."""
    outer = tmp_path / "outer"
    root = outer / "root"
    (root / "mutants" / "research_vault").mkdir(parents=True)
    (root / "scripts").mkdir()
    subprocess.run(["git", "init", "-q", str(outer)], check=True, capture_output=True)
    elsewhere = tmp_path / "elsewhere"
    subprocess.run(
        ["git", "init", "-q", str(elsewhere)], check=True, capture_output=True
    )

    env = {**mutation_gate._git_env(root), **mutation_gate._isolate_git(root)}

    def hook_path(cwd: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", "rev-parse", "--git-path", "hooks/pre-commit"],
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    assert (root / "mutants" / ".git").is_dir()
    assert not (root / "mutants" / ".git" / "hooks").exists()  # --template=
    inside = hook_path(root / "mutants" / "research_vault")
    assert inside.returncode == 0
    resolved = (root / "mutants" / "research_vault" / inside.stdout.strip()).resolve()
    assert resolved == (root / "mutants" / ".git" / "hooks" / "pre-commit").resolve()
    assert hook_path(root / "scripts").returncode == 128
    assert hook_path(root).returncode == 0  # the ceiling itself still discovers
    assert hook_path(elsewhere).returncode == 0


def test_run_mutmut_sweeps_pycache_before_invoking(tmp_path, monkeypatch):
    """PYTHONDONTWRITEBYTECODE blocks writing a pyc, not loading one: CPython
    validates on (mtime, size), and a same-length edit inside one mtime
    second reuses stale bytecode. The sweep removes what the env var cannot,
    under all three trees, before every invocation."""
    root = _fake_root(tmp_path)
    caches = [
        root / "research_vault" / "__pycache__",
        root / "tests" / "__pycache__",
        root / "mutants" / "research_vault" / "__pycache__",
        root / "mutants" / "tests" / "sub" / "__pycache__",
    ]
    for cache in caches:
        cache.mkdir(parents=True)
        (cache / "x.cpython-312.pyc").write_bytes(b"stale")
    (root / "research_vault" / "x.py").write_text("A = 1\n", encoding="utf-8")

    def fake_run(cmd, **kwargs):
        assert not any(cache.exists() for cache in caches), "sweep must precede"
        return _completed(cmd)

    monkeypatch.setattr(subprocess, "run", fake_run)
    mutation_gate._run_mutmut("research_vault/x.py", 4, root=root)
    assert (root / "research_vault" / "x.py").exists()  # source untouched


def test_run_mutmut_fails_loudly_when_the_source_tree_changes(tmp_path, monkeypatch):
    """mutmut never edits the source (schemata live in mutants/); the hash
    check is the proof. A change under research_vault/ or tests/ during the
    invocation aborts the measurement instead of reporting on a tree that
    is not the one being gated."""
    root = _fake_root(tmp_path)
    source = root / "research_vault" / "x.py"
    source.write_text("A = 1\n", encoding="utf-8")

    def fake_run(cmd, **kwargs):
        source.write_text("A = 2\n", encoding="utf-8")
        return _completed(cmd)

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(SourceTreeChangedError, match=r"research_vault/x\.py"):
        mutation_gate._run_mutmut("research_vault/x.py", 4, root=root)


def test_run_mutmut_hash_ignores_bytecode_written_during_the_run(tmp_path, monkeypatch):
    """The hash covers tracked source, not __pycache__: a pyc some child wrote
    anyway is not a source change."""
    root = _fake_root(tmp_path)
    (root / "tests" / "test_x.py").write_text("def test(): pass\n", encoding="utf-8")

    def fake_run(cmd, **kwargs):
        # Seen twice: the isolation's git init and the launcher.
        cache = root / "tests" / "__pycache__"
        cache.mkdir(exist_ok=True)
        (cache / "test_x.cpython-312.pyc").write_bytes(b"pyc")
        return _completed(cmd)

    monkeypatch.setattr(subprocess, "run", fake_run)
    mutation_gate._run_mutmut("research_vault/x.py", 4, root=root)


def test_launcher_answers_help_before_importing_mutmut(tmp_path):
    """The smoke check as literally written: `run_mutmut.py --help` from any
    cwd, with neither MUTANT_UNDER_TEST nor PYTHONPATH set, answers with the
    launcher's own usage and exits 0 -- before mutmut is imported, whose
    import-time config load would otherwise die outside a configured root."""
    env = {
        k: v
        for k, v in os.environ.items()
        if k not in ("MUTANT_UNDER_TEST", "PYTHONPATH")
    }
    for flag in ("--help", "-h"):
        proc = subprocess.run(
            [sys.executable, str(mutation_gate.LAUNCHER), flag],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, proc.stderr
        assert proc.stdout.startswith(
            "Usage: python scripts/mutmut_shims/run_mutmut.py"
        )
        assert "mutmut run" in proc.stdout
        assert "Traceback" not in proc.stderr, proc.stderr


def _seeded_config_keywords(shim: Path) -> set[str]:
    """The keyword names sitecustomize.py passes to its one `Config(...)` seed."""
    tree = ast.parse(shim.read_text(encoding="utf-8"))
    (seed,) = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "Config"
    ]
    assert not seed.args, "the seed passes every field by keyword"
    return {keyword.arg for keyword in seed.keywords if keyword.arg is not None}


def test_shim_seeds_exactly_the_fields_of_mutmuts_config_dataclass():
    """sitecustomize.py seeds `Config(...)` inside a blanket except (its body
    is the pilot's, verbatim). A mutmut release that adds or drops a field
    would turn the seed into a swallowed TypeError: no config seeded, every
    hook subprocess dead at import, and the run recording those deaths as
    kills -- the false-kill class the shim exists to prevent, written into
    the baseline silently. So a pin bump that changes the field list fails
    here, in the suite: the seed's keyword set is the dataclass's field set
    (21 names at 3.7.0). The dataclass module loads no config at import; the
    shim itself imports it from an unconfigured cwd."""
    import dataclasses

    import mutmut.configuration

    seeded = _seeded_config_keywords(mutation_gate.SHIMS / "sitecustomize.py")
    fields = {f.name for f in dataclasses.fields(mutmut.configuration.Config)}
    assert seeded == fields
    assert len(seeded) == 21


def test_launcher_patches_a_pytest_runner_method_mutmut_still_defines(tmp_path):
    """run_mutmut.py rebinds one method on mutmut's PytestRunner to widen the
    re-escaped parametrize ids (its header). Under a pin bump that renames
    or reshapes the method, the assignment would bind a name nothing calls
    and the defect would return as false kills forty minutes into a run.
    The name the launcher assigns is read from its source, and mutmut must
    still define it as a function taking (self, tests)."""
    import inspect

    tree = ast.parse(mutation_gate.LAUNCHER.read_text(encoding="utf-8"))
    patched = {
        target.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Attribute)
        and isinstance(target.value, ast.Attribute)
        and target.value.attr == "PytestRunner"
    }
    assert patched == {"_pytest_args_regular_run"}
    mm = mutation_gate._mutmut(_fake_root(tmp_path))
    (name,) = patched
    method = inspect.getattr_static(mm.PytestRunner, name)
    assert inspect.isfunction(method)
    assert list(inspect.signature(method).parameters) == ["self", "tests"]


# --- main(): --update-baseline, --out-dir, --only ------------------------------


def _fake_measurement(root: Path, monkeypatch, calls: list[str] | None = None):
    """Make _run_mutmut a no-op that reports success; the module's artifacts
    must already be in place (see _fake_module) so the real reader runs."""

    def fake_run_mutmut(relpath, max_children, root=root, address_space=None):
        if calls is not None:
            calls.append(relpath)
        return "mutmut out", 0

    monkeypatch.setattr(mutation_gate, "ROOT", root)
    # A fake root is no repository: the dirty-tree refusal is pinned by its
    # own tests against a real one, and stands aside here.
    monkeypatch.setattr(mutation_gate, "_refuse_dirty_tree", lambda cwd: None)
    monkeypatch.setattr(mutation_gate, "_run_mutmut", fake_run_mutmut)


def _argv_baseline(
    monkeypatch, root: Path, out_dir: Path | None = None, only: list[str] = ()
) -> Path:
    baseline_path = root / "mutation-baseline.txt"
    argv = ["mutation_gate.py", "--update-baseline", "--baseline", str(baseline_path)]
    if out_dir is not None:
        argv += ["--out-dir", str(out_dir)]
    for module in only:
        argv += ["--only", module]
    monkeypatch.setattr(sys, "argv", argv)
    return baseline_path


def _no_tests_line(prefix: str, mutants: int, modules: int) -> str:
    """The end-of-run block's first line, verbatim: the count and the reading."""
    return (
        f"{prefix} no tests: {mutants} mutant(s) in {modules} module(s) -- coverage "
        "reached only through subprocesses is invisible to mutmut's stats, so these "
        "are unmeasured, not killed"
    )


def _argv_gate(monkeypatch, root: Path, max_mutants: int | None = None) -> Path:
    baseline_path = root / "mutation-baseline.txt"
    argv = ["mutation_gate.py", "--baseline", str(baseline_path)]
    if max_mutants is not None:
        argv += ["--max-mutants", str(max_mutants)]
    monkeypatch.setattr(sys, "argv", argv)
    return baseline_path


def test_update_baseline_writes_every_survivor_and_names_the_no_tests_gap(
    tmp_path, monkeypatch, capsys
):
    root = _fake_root(tmp_path)
    a, b = "research_vault/a.py", "research_vault/b.py"
    _fake_module(root, a, {ADD_1: 0, ADD_2: 1, ADD_3: 33, SIZE_1: 1})
    _fake_module(root, b, {ADD_1: 1, ADD_2: 1, ADD_3: 1, SIZE_1: 0})
    _fake_measurement(root, monkeypatch)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [a, b])
    baseline_path = _argv_baseline(monkeypatch, root)

    assert mutation_gate.main() == 0
    assert baseline_keys(baseline_path) == {
        KEY_ADD_1.replace(MODULE, a),
        KEY_SIZE_1.replace(MODULE, b),
    }
    out = capsys.readouterr().out
    assert f"[baseline] {a}: ok" in out
    assert "no tests 1" in out  # the per-module gap, visible in the module line
    # ...and again in the end-of-run block, by module, with the reading spelled
    # out so the gap never reads as strength.
    assert out.splitlines()[-3:] == [
        f"[baseline] 2 survivors written to {baseline_path}",
        _no_tests_line("[baseline]", 1, 1),
        "[baseline]   research_vault/a.py: 1",
    ]


def test_update_baseline_carries_reasons_and_reports_the_unattached(
    tmp_path, monkeypatch, capsys
):
    """The three states after a run: a reasoned key that survives is
    re-emitted beneath its reason; one that was killed is dropped with its
    reason, silently; one no mutant of the run produced (a cut or rename
    moved the function, the reason sits above the old spelling) is reported
    on stderr, and the file no longer carries it."""
    root = _fake_root(tmp_path)
    a = "research_vault/a.py"
    _fake_module(root, a, {ADD_1: 0, ADD_2: 1, ADD_3: 33, SIZE_1: 0})
    _fake_measurement(root, monkeypatch)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [a])
    baseline_path = _argv_baseline(monkeypatch, root)
    surviving, killed = KEY_ADD_1.replace(MODULE, a), KEY_ADD_2.replace(MODULE, a)
    moved = f"{a}::func/gone::-    return 0\\n+    return 1"
    baseline_path.write_text(
        "# old header\n"
        "# reason: prose to a human\n"
        f"{surviving}\n"
        "# reason: killed by the new test\n"
        f"{killed}\n"
        "# reason: written above the pre-cut spelling\n"
        f"{moved}\n",
        encoding="utf-8",
    )

    assert mutation_gate.main() == 0

    text = baseline_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert lines[lines.index(surviving) - 1] == "# reason: prose to a human"
    assert "killed by the new test" not in text
    assert "pre-cut spelling" not in text
    assert moved not in text
    assert baseline_keys(baseline_path) == {surviving, KEY_SIZE_1.replace(MODULE, a)}
    assert lines[0].startswith(
        "# mutation-baseline.txt -- every survivor of the research_vault modules"
    )
    assert lines[1].startswith("# a `# reason: <text>` line")
    err = capsys.readouterr().err
    assert f"[baseline] reason not re-attached: {moved}" in err
    assert "killed by the new test" not in err


def test_update_baseline_refuses_a_malformed_reason_before_measuring(
    tmp_path, monkeypatch, capsys
):
    root = _fake_root(tmp_path)
    a = "research_vault/a.py"
    _fake_measurement(root, monkeypatch)
    monkeypatch.setattr(mutation_gate, "_run_mutmut", _fail_if_called)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [a])
    baseline_path = _argv_baseline(monkeypatch, root)
    baseline_path.write_text("# reason: dangling\n", encoding="utf-8")

    assert mutation_gate.main() == 1
    assert capsys.readouterr().out.startswith("[baseline] ABORT: ")


def test_cached_record_restores_the_generated_keys(tmp_path, monkeypatch, capsys):
    """A resumed blanket run reads `generated` back from the record, so a
    reason above a key the cached module killed is still dropped silently
    and one it never produced is still reported."""
    root = _fake_root(tmp_path)
    a = "research_vault/a.py"
    _fake_module(root, a, {ADD_1: 0, ADD_2: 1, ADD_3: 33, SIZE_1: 1})
    out_dir = root / "records"
    out_dir.mkdir()
    mutation_gate._write_record(
        out_dir, a, "out", 0, "ok", read_module_results(a, root)
    )
    cached = mutation_gate._cached_result(out_dir, a)
    assert cached is not None
    assert cached.generated == {
        KEY_ADD_1.replace(MODULE, a),
        KEY_ADD_2.replace(MODULE, a),
        KEY_ADD_3.replace(MODULE, a),
        KEY_SIZE_1.replace(MODULE, a),
    }
    data = json.loads((out_dir / "research_vault__a.py.result.json").read_text())
    assert data["generated"] == sorted(cached.generated)


def test_max_children_and_the_cap_reach_the_launch_in_both_modes(tmp_path, monkeypatch):
    """`--max-children N --child-address-space BYTES` on the command line are
    what _run_mutmut is launched with, in --update-baseline and in gate mode;
    the defaults (4, 4 GiB) when neither is given."""
    root = _fake_root(tmp_path)
    a = "research_vault/a.py"
    _fake_module(root, a, {ADD_1: 1, ADD_2: 1, ADD_3: 1, SIZE_1: 1})
    launches: list[tuple[str, int, int]] = []

    def fake_run_mutmut(relpath, max_children, root=root, address_space=None):
        launches.append((relpath, max_children, address_space))
        return "mutmut out", 0

    monkeypatch.setattr(mutation_gate, "ROOT", root)
    # A fake root is no repository: the dirty-tree refusal is pinned by its
    # own tests against a real one, and stands aside here.
    monkeypatch.setattr(mutation_gate, "_refuse_dirty_tree", lambda cwd: None)
    monkeypatch.setattr(mutation_gate, "_run_mutmut", fake_run_mutmut)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [a])
    monkeypatch.setattr(mutation_gate, "changed_modules", lambda base, **_: [a])
    baseline_path = root / "mutation-baseline.txt"
    flags = ["--max-children", "3", "--child-address-space", "2.5GiB"]

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "mutation_gate.py",
            "--update-baseline",
            "--baseline",
            str(baseline_path),
            *flags,
        ],
    )
    assert mutation_gate.main() == 0
    monkeypatch.setattr(
        sys, "argv", ["mutation_gate.py", "--baseline", str(baseline_path), *flags]
    )
    assert mutation_gate.main() == 0
    monkeypatch.setattr(
        sys, "argv", ["mutation_gate.py", "--baseline", str(baseline_path)]
    )
    assert mutation_gate.main() == 0

    assert launches == [
        (a, 3, round(2.5 * (1 << 30))),
        (a, 3, round(2.5 * (1 << 30))),
        (a, 4, 4 << 30),
    ]


def test_update_baseline_refuses_to_write_when_a_module_errors(
    tmp_path, monkeypatch, capsys
):
    """The Q1 guard: a module mutmut did not finish has no survivor list, and
    an empty contribution is not a clean one. The refusal still ends with the
    no-tests block -- the gap is reported on every run that measured anything."""
    root = _fake_root(tmp_path)
    a, b = "research_vault/a.py", "research_vault/b.py"
    _fake_module(root, a, {ADD_1: 0, ADD_2: 1, ADD_3: 33, SIZE_1: 1})
    _fake_module(root, b, {ADD_1: 1, ADD_2: 1, ADD_3: 1, SIZE_1: 1})
    _fake_measurement(root, monkeypatch)

    def fake_run_mutmut(relpath, max_children, root=root, address_space=None):
        return "mutmut out", 1 if relpath == b else 0

    monkeypatch.setattr(mutation_gate, "_run_mutmut", fake_run_mutmut)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [a, b])
    baseline_path = _argv_baseline(monkeypatch, root)

    assert mutation_gate.main() == 1
    assert not baseline_path.exists()
    out = capsys.readouterr().out
    assert f"[baseline] FAIL {b}" in out
    assert out.splitlines()[-3:] == [
        "[baseline]   error (1): research_vault/b.py",
        _no_tests_line("[baseline]", 1, 1),
        "[baseline]   research_vault/a.py: 1",
    ]


def test_update_baseline_refuses_to_write_on_an_unchecked_mutant(
    tmp_path, monkeypatch, capsys
):
    """Exit 0 from mutmut is not enough: an interrupted run leaves unchecked
    mutants behind and still exits 0."""
    root = _fake_root(tmp_path)
    a = "research_vault/a.py"
    _fake_module(root, a, {ADD_1: 0, ADD_2: None, ADD_3: 1, SIZE_1: 1})
    _fake_measurement(root, monkeypatch)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [a])
    baseline_path = _argv_baseline(monkeypatch, root)

    assert mutation_gate.main() == 1
    assert not baseline_path.exists()
    assert "not checked" in capsys.readouterr().out


def test_update_baseline_refuses_to_write_when_meta_is_missing(tmp_path, monkeypatch):
    root = _fake_root(tmp_path)
    a = "research_vault/a.py"
    (root / "mutants" / "research_vault").mkdir(parents=True)
    _fake_measurement(root, monkeypatch)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [a])
    baseline_path = _argv_baseline(monkeypatch, root)

    assert mutation_gate.main() == 1
    assert not baseline_path.exists()


def test_timeout_verdict_keeps_the_module_ok_in_both_modes(
    tmp_path, monkeypatch, capsys
):
    """A timeout is a verdict the mutant caused: listed by name (id and key),
    never written to the baseline, and no change to either mode's exit code."""
    root = _fake_root(tmp_path)
    a = "research_vault/a.py"
    _fake_module(root, a, {ADD_1: 36, ADD_2: 1, ADD_3: 1, SIZE_1: 0})
    _fake_measurement(root, monkeypatch)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [a])
    baseline_path = _argv_baseline(monkeypatch, root)

    assert mutation_gate.main() == 0
    assert baseline_keys(baseline_path) == {KEY_SIZE_1.replace(MODULE, a)}
    out = capsys.readouterr().out
    assert f"[baseline] {a}: ok (killed 2, survived 1, no tests 0, timeout 1)" in out
    assert f"[baseline]   timeout {ADD_1.replace('fake', 'a')}  " in out
    assert KEY_ADD_1.replace(MODULE, a) in out

    monkeypatch.setattr(mutation_gate, "changed_modules", lambda base, **_: [a])
    _argv_gate(monkeypatch, root)  # the baseline just written holds the survivor
    assert mutation_gate.main() == 0
    assert "[gate] pass — no new survivors" in capsys.readouterr().out.splitlines()


@pytest.mark.parametrize(
    ("code", "status"),
    [(4, "suspicious"), (-9, "segfault")],
    ids=["suspicious", "segfault"],
)
def test_suspicious_and_segfault_verdicts_class_the_module_error_in_both_modes(
    tmp_path, monkeypatch, capsys, code, status
):
    """Suspicious (a code mutmut cannot classify) and segfault (SIGKILL) are the
    absence of a verdict: the module is an error, --update-baseline refuses to
    write, gate mode fails, and the class line names the offending mutant id so
    the module can be redone with --only once the cause is fixed."""
    root = _fake_root(tmp_path)
    a = "research_vault/a.py"
    _fake_module(root, a, {ADD_1: 0, ADD_2: code, ADD_3: 1, SIZE_1: 1})
    _fake_measurement(root, monkeypatch)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [a])
    baseline_path = _argv_baseline(monkeypatch, root)

    assert mutation_gate.main() == 1
    assert not baseline_path.exists()
    out = capsys.readouterr().out
    offender = ADD_2.replace("fake", "a")
    assert f"{status} {offender}" in out
    class_line = next(line for line in out.splitlines() if f"{a}: error" in line)
    assert offender in class_line
    assert "[baseline]   error (1): research_vault/a.py" in out

    baseline_path.write_text(KEY_ADD_1.replace(MODULE, a) + "\n", encoding="utf-8")
    monkeypatch.setattr(mutation_gate, "changed_modules", lambda base, **_: [a])
    _argv_gate(monkeypatch, root)
    assert mutation_gate.main() == 1
    out = capsys.readouterr().out
    assert f"[gate] {a}: error" in out
    assert offender in out
    assert "[gate]   error (1): research_vault/a.py" in out


def test_out_dir_skips_module_with_recorded_success(tmp_path, monkeypatch):
    """The whole point of --out-dir: a resumed run must not redo work a prior
    run already finished and recorded -- and the baseline is assembled from the
    RECORD, not from mutants/ (mutant ids renumber and mutants/ regenerates)."""
    root = _fake_root(tmp_path)
    out_dir = root / "records"
    out_dir.mkdir()
    a = "research_vault/a.py"
    recorded = ModuleResult(
        survivors={KEY_ADD_2.replace(MODULE, a)},
        counts={"survived": 1, "killed": 3},
        flagged=[],
        no_verdict=[],
    )
    mutation_gate._write_record(out_dir, a, "old out", 0, "ok", recorded)

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("a recorded success must not be re-run")

    monkeypatch.setattr(mutation_gate, "ROOT", root)
    # A fake root is no repository: the dirty-tree refusal is pinned by its
    # own tests against a real one, and stands aside here.
    monkeypatch.setattr(mutation_gate, "_refuse_dirty_tree", lambda cwd: None)
    monkeypatch.setattr(mutation_gate, "_run_mutmut", fail_if_called)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [a])
    baseline_path = _argv_baseline(monkeypatch, root, out_dir)

    assert mutation_gate.main() == 0
    assert baseline_keys(baseline_path) == recorded.survivors


def test_out_dir_reruns_module_with_recorded_failure(tmp_path, monkeypatch):
    root = _fake_root(tmp_path)
    out_dir = root / "records"
    out_dir.mkdir()
    a = "research_vault/a.py"
    (out_dir / "research_vault__a.py.stdout").write_text("", encoding="utf-8")
    (out_dir / "research_vault__a.py.exit").write_text("1 error", encoding="utf-8")
    _fake_module(root, a, {ADD_1: 0, ADD_2: 1, ADD_3: 1, SIZE_1: 1})
    calls: list[str] = []
    _fake_measurement(root, monkeypatch, calls)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [a])
    baseline_path = _argv_baseline(monkeypatch, root, out_dir)

    assert mutation_gate.main() == 0
    assert calls == [a]
    assert (out_dir / "research_vault__a.py.exit").read_text(encoding="utf-8") == "0 ok"
    assert (out_dir / "research_vault__a.py.stdout").read_text(encoding="utf-8") == (
        "mutmut out"
    )
    assert baseline_keys(baseline_path) == {KEY_ADD_1.replace(MODULE, a)}


def test_out_dir_reruns_an_interrupted_module_recorded_with_exit_zero(
    tmp_path, monkeypatch
):
    """The record an interrupted run leaves behind is "0 error" with unchecked
    mutants: exit 0 no longer implies ok, so a resume must re-run it rather
    than merge its partial survivor list into the baseline."""
    root = _fake_root(tmp_path)
    out_dir = root / "records"
    out_dir.mkdir()
    a = "research_vault/a.py"
    partial = ModuleResult(
        survivors=set(),
        counts={"killed": 1},
        no_verdict=[("not checked", ADD_2.replace("fake", "a"))],
    )
    mutation_gate._write_record(out_dir, a, "interrupted", 0, "error", partial)
    assert (out_dir / "research_vault__a.py.exit").read_text(encoding="utf-8") == (
        "0 error"
    )
    _fake_module(root, a, {ADD_1: 0, ADD_2: 1, ADD_3: 1, SIZE_1: 1})
    calls: list[str] = []
    _fake_measurement(root, monkeypatch, calls)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [a])
    baseline_path = _argv_baseline(monkeypatch, root, out_dir)

    assert mutation_gate.main() == 0
    assert calls == [a]
    assert baseline_keys(baseline_path) == {KEY_ADD_1.replace(MODULE, a)}


def test_out_dir_writes_no_baseline_when_a_module_still_fails(tmp_path, monkeypatch):
    root = _fake_root(tmp_path)
    out_dir = root / "records"
    out_dir.mkdir()
    a, b = "research_vault/a.py", "research_vault/b.py"
    _fake_module(root, b, {ADD_1: 1, ADD_2: 1, ADD_3: 1, SIZE_1: 1})
    _fake_measurement(root, monkeypatch)

    def fake_run_mutmut(relpath, max_children, root=root, address_space=None):
        return "", 1 if relpath == a else 0

    monkeypatch.setattr(mutation_gate, "_run_mutmut", fake_run_mutmut)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [a, b])
    baseline_path = _argv_baseline(monkeypatch, root, out_dir)

    assert mutation_gate.main() == 1
    assert not baseline_path.exists()
    assert (out_dir / "research_vault__a.py.exit").read_text(encoding="utf-8") == (
        "1 error"
    )


def test_only_narrows_the_run_and_refuses_to_write_until_every_module_has_a_record(
    tmp_path, monkeypatch, capsys
):
    """--only runs the named module(s) and records them; the baseline is
    written only once EVERY module has a usable record, so a narrowed run can
    never produce a baseline with a module silently missing from it."""
    root = _fake_root(tmp_path)
    out_dir = root / "records"
    out_dir.mkdir()
    a, b = "research_vault/a.py", "research_vault/b.py"
    _fake_module(root, a, {ADD_1: 0, ADD_2: 1, ADD_3: 1, SIZE_1: 1})
    _fake_module(root, b, {ADD_1: 1, ADD_2: 1, ADD_3: 1, SIZE_1: 0})
    calls: list[str] = []
    _fake_measurement(root, monkeypatch, calls)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [a, b])

    baseline_path = _argv_baseline(monkeypatch, root, out_dir, only=[a])
    assert mutation_gate.main() == 1
    assert calls == [a]
    assert not baseline_path.exists()
    assert (out_dir / "research_vault__a.py.exit").read_text(encoding="utf-8") == "0 ok"
    out = capsys.readouterr().out
    assert "[baseline]   not measured (1): research_vault/b.py" in out

    _argv_baseline(monkeypatch, root, out_dir, only=[b])
    assert mutation_gate.main() == 0
    assert calls == [a, b]
    assert baseline_keys(baseline_path) == {
        KEY_ADD_1.replace(MODULE, a),
        KEY_SIZE_1.replace(MODULE, b),
    }


def test_only_requires_update_baseline(tmp_path, monkeypatch, capsys):
    root = _fake_root(tmp_path)
    monkeypatch.setattr(
        sys, "argv", ["mutation_gate.py", "--only", "research_vault/a.py"]
    )
    monkeypatch.setattr(mutation_gate, "ROOT", root)
    with pytest.raises(SystemExit) as exit_info:
        mutation_gate.main()
    assert exit_info.value.code == 2
    assert "--only requires --update-baseline" in capsys.readouterr().err


def test_only_requires_out_dir(tmp_path, monkeypatch, capsys):
    """--only without --out-dir would refuse the write every time (the other
    modules have no record to be read from): argparse says so up front, and
    nothing is measured."""
    root = _fake_root(tmp_path)
    a = "research_vault/a.py"
    _fake_module(root, a, {ADD_1: 1, ADD_2: 1, ADD_3: 1, SIZE_1: 1})
    calls: list[str] = []
    _fake_measurement(root, monkeypatch, calls)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [a])
    baseline_path = _argv_baseline(monkeypatch, root, only=[a])
    with pytest.raises(SystemExit) as exit_info:
        mutation_gate.main()
    assert exit_info.value.code == 2
    assert "--only requires --out-dir" in capsys.readouterr().err
    assert calls == []
    assert not baseline_path.exists()


def test_only_rejects_a_path_that_is_no_module(tmp_path, monkeypatch, capsys):
    """A typo in --only must not become a run that measures nothing."""
    root = _fake_root(tmp_path)
    monkeypatch.setattr(mutation_gate, "ROOT", root)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: ["research_vault/a.py"])
    _argv_baseline(
        monkeypatch, root, out_dir=root / "records", only=["research_vault/typo.py"]
    )
    with pytest.raises(SystemExit) as exit_info:
        mutation_gate.main()
    assert exit_info.value.code == 2
    assert "research_vault/typo.py" in capsys.readouterr().err


def test_source_tree_change_aborts_the_run_without_writing(
    tmp_path, monkeypatch, capsys
):
    root = _fake_root(tmp_path)
    a = "research_vault/a.py"
    monkeypatch.setattr(mutation_gate, "ROOT", root)

    def fake_run_mutmut(relpath, max_children, root=root, address_space=None):
        raise SourceTreeChangedError("research_vault/x.py changed")

    monkeypatch.setattr(mutation_gate, "_run_mutmut", fake_run_mutmut)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [a])
    baseline_path = _argv_baseline(monkeypatch, root)

    assert mutation_gate.main() == 1
    assert not baseline_path.exists()
    assert "ABORT" in capsys.readouterr().out


# --- main(): gate mode -------------------------------------------------------


def test_gate_passes_with_no_changed_modules(tmp_path, monkeypatch, capsys):
    root = _fake_root(tmp_path)
    monkeypatch.setattr(mutation_gate, "ROOT", root)
    monkeypatch.setattr(mutation_gate, "changed_modules", lambda base, **_: [])
    _argv_gate(monkeypatch, root)
    assert mutation_gate.main() == 0
    assert "no changed research_vault modules" in capsys.readouterr().out


def test_gate_fails_on_a_survivor_absent_from_the_baseline(
    tmp_path, monkeypatch, capsys
):
    root = _fake_root(tmp_path)
    a = "research_vault/a.py"
    _fake_module(root, a, {ADD_1: 0, ADD_2: 1, ADD_3: 1, SIZE_1: 0})
    _fake_measurement(root, monkeypatch)
    monkeypatch.setattr(mutation_gate, "changed_modules", lambda base, **_: [a])
    baseline_path = _argv_gate(monkeypatch, root)
    baseline_path.write_text(KEY_ADD_1.replace(MODULE, a) + "\n", encoding="utf-8")

    assert mutation_gate.main() == 1
    out = capsys.readouterr().out
    assert "[gate] FAIL — 1 new survivor(s):" in out
    assert KEY_SIZE_1.replace(MODULE, a) in out


def test_gate_passes_when_every_survivor_is_baselined(tmp_path, monkeypatch, capsys):
    """...and the pass still ends with the no-tests block, by module, so the
    subprocess-only gap is on every run's output."""
    root = _fake_root(tmp_path)
    a = "research_vault/a.py"
    _fake_module(root, a, {ADD_1: 0, ADD_2: 1, ADD_3: 33, SIZE_1: 0})
    _fake_measurement(root, monkeypatch)
    monkeypatch.setattr(mutation_gate, "changed_modules", lambda base, **_: [a])
    baseline_path = _argv_gate(monkeypatch, root)
    baseline_path.write_text(
        KEY_ADD_1.replace(MODULE, a) + "\n" + KEY_SIZE_1.replace(MODULE, a) + "\n",
        encoding="utf-8",
    )

    assert mutation_gate.main() == 0
    assert capsys.readouterr().out.splitlines()[-3:] == [
        _no_tests_line("[gate]", 1, 1),
        "[gate]   research_vault/a.py: 1",
        "[gate] pass — no new survivors",
    ]


def test_gate_fails_when_a_module_errors(tmp_path, monkeypatch, capsys):
    root = _fake_root(tmp_path)
    a = "research_vault/a.py"
    monkeypatch.setattr(mutation_gate, "ROOT", root)
    monkeypatch.setattr(mutation_gate, "_run_mutmut", lambda *_args, **_kwargs: ("", 1))
    monkeypatch.setattr(mutation_gate, "changed_modules", lambda base, **_: [a])
    _argv_gate(monkeypatch, root)

    assert mutation_gate.main() == 1
    out = capsys.readouterr().out
    assert f"[gate] {a}: error" in out
    assert "[gate]   error (1): research_vault/a.py" in out


# --- main(): the CI mutant budget --------------------------------------------

# A source whose mutant count under mutmut 3.7.0's operator set is known:
# `a + b` -> `a - b` and `return 1` -> `return 2`, two mutants.
BUDGET_SOURCE = (
    "def add(a, b):\n    return a + b\n\n\nclass Box:\n    def size(self):\n"
    "        return 1\n"
)
# `modules` is the counted noun phrase, spelled by the test: "2 changed modules",
# "1 changed module".
OVER_BUDGET = (
    "[gate] not measured: {count} mutants across {modules} "
    "exceed the CI budget of {budget}; run the gate locally"
)


def test_count_mutants_is_mutmuts_own_generation_run_in_memory(tmp_path):
    """The count is mutmut's generator over the module's source -- the same
    operator set and pragma handling a run applies, so it equals what the run
    would generate -- with nothing written under mutants/, the source
    untouched, and no test run."""
    root = _fake_root(tmp_path)
    a = "research_vault/a.py"
    (root / a).write_text(BUDGET_SOURCE, encoding="utf-8")

    assert mutation_gate.count_mutants(a, root) == 2
    assert not (root / "mutants").exists()
    assert (root / a).read_text(encoding="utf-8") == BUDGET_SOURCE

    (root / a).write_text(
        "def add(a, b):\n    return a + b  # pragma: no mutate\n", encoding="utf-8"
    )
    assert mutation_gate.count_mutants(a, root) == 0


@pytest.mark.parametrize(
    ("source", "parser_error"),
    [
        ("def add(a, b:\n    return a + b\n", "ParserSyntaxError"),
        ("# pragma: no mutate end\nA = 1\n", "PragmaParseError"),
    ],
    ids=["syntax", "pragma"],
)
def test_count_mutants_aborts_naming_a_module_the_generator_cannot_parse(
    tmp_path, source, parser_error
):
    """A syntax error, or a `# pragma: no mutate` context mutmut's pragma
    parser refuses, is ModuleParseError -- the module, the parser's class and
    its message on one line -- not libcst's or mutmut's own traceback."""
    root = _fake_root(tmp_path)
    a = "research_vault/a.py"
    (root / a).write_text(source, encoding="utf-8")

    with pytest.raises(mutation_gate.ModuleParseError) as caught:
        mutation_gate.count_mutants(a, root)
    message = str(caught.value)
    assert message.startswith(
        f"{a}: mutmut's generator cannot parse it ({parser_error}: "
    )
    assert "\n" not in message
    assert type(caught.value.__cause__).__name__ == parser_error
    assert isinstance(caught.value, mutation_gate.GateAbortError)
    assert not (root / "mutants").exists()


def test_a_git_or_parse_failure_is_the_gates_abort_line_in_gate_mode(
    tmp_path, monkeypatch, capsys
):
    """main() prints `[gate] ABORT: ...` and returns 1 for GitCommandError (a
    --base that does not resolve) and for ModuleParseError (a changed module
    the budget count cannot parse), as it does for the other aborts: no
    traceback, no launch, no baseline read."""
    root = _fake_root(tmp_path)
    a = "research_vault/a.py"
    monkeypatch.setattr(mutation_gate, "ROOT", root)
    monkeypatch.setattr(mutation_gate, "_run_mutmut", _fail_if_called)
    monkeypatch.setattr(mutation_gate, "baseline_keys", _fail_if_called)

    def unresolved(base, **_):
        raise mutation_gate.GitCommandError(
            f"`git diff --name-only --relative {base}...HEAD -- research_vault/*.py` "
            "exited 128: fatal: bad revision"
        )

    monkeypatch.setattr(mutation_gate, "changed_modules", unresolved)
    _argv_gate(monkeypatch, root)
    assert mutation_gate.main() == 1
    assert capsys.readouterr().out.splitlines() == [
        (
            "[gate] ABORT: `git diff --name-only --relative origin/main...HEAD -- "
            "research_vault/*.py` exited 128: fatal: bad revision"
        )
    ]

    (root / a).write_text("def add(a, b:\n    return a + b\n", encoding="utf-8")
    monkeypatch.setattr(mutation_gate, "changed_modules", lambda base, **_: [a])
    _argv_gate(monkeypatch, root, max_mutants=3)
    assert mutation_gate.main() == 1
    (line,) = capsys.readouterr().out.splitlines()
    assert line.startswith(
        f"[gate] ABORT: {a}: mutmut's generator cannot parse it (ParserSyntaxError: "
    )


def test_gate_reads_an_oversize_diff_as_unmeasured_without_launching_mutmut(
    tmp_path, monkeypatch, capsys
):
    """Over budget: exactly the qualified line plus the per-module counts,
    exit 0, no mutmut launch through the seam, no baseline comparison and no
    mutants/ -- the four-state rule: an unrun check reads unmeasured, never
    pass or fail, and the advisory lane does not go red for size."""
    root = _fake_root(tmp_path)
    a, b = "research_vault/a.py", "research_vault/b.py"
    for module in (a, b):
        (root / module).write_text(BUDGET_SOURCE, encoding="utf-8")
    monkeypatch.setattr(mutation_gate, "ROOT", root)
    calls = _record_runs(monkeypatch)
    monkeypatch.setattr(mutation_gate, "_run_mutmut", _fail_if_called)
    monkeypatch.setattr(mutation_gate, "new_survivors", _fail_if_called)
    monkeypatch.setattr(mutation_gate, "changed_modules", lambda base, **_: [a, b])
    _argv_gate(monkeypatch, root, max_mutants=3)

    assert mutation_gate.main() == 0
    assert capsys.readouterr().out.splitlines() == [
        OVER_BUDGET.format(count=4, modules="2 changed modules", budget=3),
        f"[gate]   {a}: 2",
        f"[gate]   {b}: 2",
    ]
    assert calls == []
    assert not (root / "mutants").exists()


def test_gate_measures_a_diff_within_the_budget(tmp_path, monkeypatch, capsys):
    """At the budget exactly the gate runs as it would without one (`>`
    decides, not `>=`), one mutant over it does not; with no --max-mutants
    nothing is counted at all."""
    root = _fake_root(tmp_path)
    a = "research_vault/a.py"
    (root / a).write_text(BUDGET_SOURCE, encoding="utf-8")
    _fake_module(root, a, {ADD_1: 0, SIZE_1: 0})
    calls: list[str] = []
    _fake_measurement(root, monkeypatch, calls)
    monkeypatch.setattr(mutation_gate, "changed_modules", lambda base, **_: [a])
    baseline_path = _argv_gate(monkeypatch, root, max_mutants=2)
    baseline_path.write_text(
        KEY_ADD_1.replace(MODULE, a) + "\n" + KEY_SIZE_1.replace(MODULE, a) + "\n",
        encoding="utf-8",
    )

    assert mutation_gate.main() == 0
    out = capsys.readouterr().out.splitlines()
    assert calls == [a]
    assert "[gate] 2 mutants across 1 changed module, within the CI budget of 2" in out
    assert f"[gate]   {a}: 2" in out
    assert "[gate] pass — no new survivors" in out
    assert not any("not measured" in line for line in out)

    calls.clear()
    _argv_gate(monkeypatch, root, max_mutants=1)
    assert mutation_gate.main() == 0
    out = capsys.readouterr().out.splitlines()
    assert calls == []
    assert OVER_BUDGET.format(count=2, modules="1 changed module", budget=1) in out
    assert "[gate] pass — no new survivors" not in out

    monkeypatch.setattr(mutation_gate, "count_mutants", _fail_if_called)
    _argv_gate(monkeypatch, root)
    assert mutation_gate.main() == 0
    assert "[gate] pass — no new survivors" in capsys.readouterr().out.splitlines()


def test_max_mutants_is_a_positive_gate_mode_budget(tmp_path, monkeypatch, capsys):
    """--max-mutants with --update-baseline, or a non-positive budget, is an
    argparse error (exit 2 naming the flag), never a run."""
    root = _fake_root(tmp_path)
    monkeypatch.setattr(mutation_gate, "ROOT", root)
    monkeypatch.setattr(mutation_gate, "changed_modules", _fail_if_called)
    monkeypatch.setattr(mutation_gate, "_all_modules", _fail_if_called)
    for argv, expected in (
        (["--update-baseline", "--max-mutants", "5"], "--update-baseline"),
        (["--max-mutants", "0"], "positive"),
        (["--max-mutants", "-1"], "positive"),
        (["--max-mutants", "many"], "positive"),
    ):
        monkeypatch.setattr(sys, "argv", ["mutation_gate.py", *argv])
        with pytest.raises(SystemExit) as exit_info:
            mutation_gate.main()
        assert exit_info.value.code == 2
        err = capsys.readouterr().err
        assert "--max-mutants" in err
        assert expected in err


# --- the time budget (gate mode; §3.9) ----------------------------------------


def _stats_file(root: Path, module: str, seconds_by_function: dict[str, float]):
    """mutants/mutmut-stats.json in the shape mutmut's save_stats writes: a
    test set per `<module>.<mangled function>` and a duration per test."""
    dotted = module[: -len(".py")].replace("/", ".")
    tests_by_function = {}
    duration_by_test = {}
    for mangled, seconds in seconds_by_function.items():
        test_id = f"tests/test_{mangled}.py::test_{mangled}"
        tests_by_function[f"{dotted}.{mangled}"] = [test_id]
        duration_by_test[test_id] = seconds
    (root / "mutants").mkdir(exist_ok=True)
    (root / "mutants" / "mutmut-stats.json").write_text(
        json.dumps(
            {
                "tests_by_mangled_function_name": tests_by_function,
                "duration_by_test": duration_by_test,
                "stats_time": 1.0,
                "function_hashes": {},
                "function_dependencies": {},
                "config_fingerprint": "x",
                "watched_file_hashes": {},
                "git_commit": None,
            }
        ),
        encoding="utf-8",
    )


def _two_module_gate(root: Path, monkeypatch, calls: list[str]):
    """Module a already measured (its artifacts faked); module b remaining,
    with the source `count_mutants` and the estimate generate from."""
    a, b = "research_vault/a.py", "research_vault/b.py"
    _fake_module(root, a, {ADD_1: 0, ADD_2: 1, ADD_3: 33, SIZE_1: 1})
    _fake_module(root, b, {ADD_1: 1, ADD_2: 1, ADD_3: 1, SIZE_1: 1})
    (root / a).write_text(BUDGET_SOURCE, encoding="utf-8")
    (root / b).write_text(BUDGET_SOURCE, encoding="utf-8")
    _fake_measurement(root, monkeypatch, calls)
    monkeypatch.setattr(mutation_gate, "changed_modules", lambda base, **_: [a, b])
    return a, b


@pytest.mark.parametrize("first_module_fails", [False, True])
def test_gate_refuses_the_remaining_modules_over_the_time_budget(
    tmp_path, monkeypatch, capsys, first_module_fails
):
    """After the first module returns, the remaining modules' mutants are
    mapped to their tests through the stats file, the durations summed and
    divided by --max-children, the fixed per-module cost added, and the sum
    compared with what is left of the budget. Over it: the first module's
    verdict, one qualified line, no further launch, and the exit code the
    first module earned (a FAIL found is a FAIL, otherwise 0)."""
    root = _fake_root(tmp_path)
    calls: list[str] = []
    a, b = _two_module_gate(root, monkeypatch, calls)
    # b: x_add's tests 900 s, Box.size's 300 s; /4 children = 300 s, + 300 s
    # fixed = 600 s = 10 min, against a 500 s (8 min) budget.
    _stats_file(root, b, {"x_add": 900.0, "xǁBoxǁsize": 300.0})
    baseline_path = _argv_gate(monkeypatch, root)
    monkeypatch.setattr(
        sys, "argv", [*sys.argv, "--max-children", "4", "--time-budget", "500"]
    )
    if not first_module_fails:
        baseline_path.write_text(KEY_ADD_1.replace(MODULE, a) + "\n", encoding="utf-8")

    code = mutation_gate.main()

    assert calls == [a]
    out = capsys.readouterr().out.splitlines()
    assert f"[gate] {a}: ok (killed 2, survived 1, no tests 1)" in out
    if first_module_fails:
        assert code == 1
        assert "[gate] FAIL — 1 new survivor(s):" in out
    else:
        assert code == 0
        assert "[gate] pass — no new survivors" in out
    assert out[-1] == (
        "[gate] not measured: estimated 10 min for 1 remaining module exceeds "
        "the 8 min left of the time budget"
    )


def test_gate_measures_every_module_within_the_time_budget(
    tmp_path, monkeypatch, capsys
):
    root = _fake_root(tmp_path)
    calls: list[str] = []
    a, b = _two_module_gate(root, monkeypatch, calls)
    _stats_file(root, b, {"x_add": 900.0, "xǁBoxǁsize": 300.0})
    _argv_gate(monkeypatch, root)
    monkeypatch.setattr(
        sys, "argv", [*sys.argv, "--max-children", "4", "--time-budget", "5000"]
    )

    assert mutation_gate.main() == 1  # a's survivor is new: measured, not budgeted away
    assert calls == [a, b]
    assert "not measured" not in capsys.readouterr().out


def test_gate_without_a_time_budget_never_reads_the_stats_file(
    tmp_path, monkeypatch, capsys
):
    root = _fake_root(tmp_path)
    calls: list[str] = []
    a, b = _two_module_gate(root, monkeypatch, calls)
    monkeypatch.setattr(mutation_gate, "_estimate_seconds", _fail_if_called)
    _argv_gate(monkeypatch, root)

    mutation_gate.main()

    assert calls == [a, b]


def test_gate_continues_when_the_estimate_is_unavailable(tmp_path, monkeypatch, capsys):
    """No stats file after the first module (mutmut's own fault): the budget
    cannot be applied, the gate says so on one line and measures on -- an
    unknowable estimate must not read as over budget or as pass."""
    root = _fake_root(tmp_path)
    calls: list[str] = []
    a, b = _two_module_gate(root, monkeypatch, calls)
    _argv_gate(monkeypatch, root)
    monkeypatch.setattr(sys, "argv", [*sys.argv, "--time-budget", "1"])

    mutation_gate.main()

    assert calls == [a, b]
    line = next(
        line
        for line in capsys.readouterr().out.splitlines()
        if line.startswith("[gate] time budget not applied: ")
    )
    assert "mutmut-stats.json" in line


def test_estimate_seconds_is_the_stats_sum_over_children_plus_the_fixed_cost(
    tmp_path,
):
    root = _fake_root(tmp_path)
    b = "research_vault/b.py"
    (root / b).write_text(BUDGET_SOURCE, encoding="utf-8")
    _stats_file(root, b, {"x_add": 900.0, "xǁBoxǁsize": 300.0})
    assert mutation_gate._estimate_seconds([b], root, 4) == 300.0 + 300.0
    assert mutation_gate._estimate_seconds([b], root, 2) == 600.0 + 300.0
    assert mutation_gate._estimate_seconds([b, b], root, 4) == 2 * 600.0
    # A function no test reaches costs nothing beyond the fixed per-module cost.
    _stats_file(root, b, {})
    assert mutation_gate._estimate_seconds([b], root, 4) == 300.0


def test_estimate_seconds_names_a_module_mutmut_cannot_parse(tmp_path):
    root = _fake_root(tmp_path)
    b = "research_vault/b.py"
    (root / b).write_text("def (:\n", encoding="utf-8")
    _stats_file(root, b, {})

    with pytest.raises(
        mutation_gate.ModuleParseError, match=r"research_vault/b\.py"
    ) as caught:
        mutation_gate._estimate_seconds([b], root, 4)
    assert isinstance(caught.value, mutation_gate.GateAbortError)


@pytest.mark.parametrize(
    ("argv", "fragment"),
    [
        (["--update-baseline", "--time-budget", "5"], "--update-baseline"),
        (["--time-budget", "0"], "positive"),
        (["--time-budget", "-1"], "positive"),
        (["--time-budget", "soon"], "positive"),
    ],
)
def test_time_budget_argparse_shape(argv, fragment, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["mutation_gate.py", *argv])
    with pytest.raises(SystemExit) as caught:
        mutation_gate.main()
    assert caught.value.code == 2
    err = capsys.readouterr().err
    assert "--time-budget" in err
    assert fragment in err


# --- the suite's own mutant-awareness ----------------------------------------


def test_package_ast_prunes_mutmut_siblings_at_module_and_class_level(tmp_path):
    """Under the gate, an AST-inventory test reads mutmut's schemata copy of a
    module; the mutant siblings' mutated literals must not enter the
    inventory. Only the original's defs remain, at both levels."""
    from tests.conftest import package_ast

    path = tmp_path / "fake.py"
    path.write_text(FAKE_SCHEMATA, encoding="utf-8")
    tree = package_ast(path)
    defs = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
    (box,) = (node for node in tree.body if isinstance(node, ast.ClassDef))
    methods = [node.name for node in box.body if isinstance(node, ast.FunctionDef)]
    assert defs == ["add"]
    assert methods == ["size"]
    returns = {
        ast.unparse(node.value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Return) and node.value is not None
    }
    assert returns == {"a + b", "1"}
