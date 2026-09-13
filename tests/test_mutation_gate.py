"""Unit tests for the no-new-survivors mutation gate over mutmut.

No real mutmut run: the tests fake mutmut's on-disk artifacts (a schemata file
under mutants/<relpath> and its .meta JSON) in a tmp tree and read them through
the gate, which reads them through mutmut's own readers. The launcher subprocess
is faked at subprocess.run. Every test is satisfiable from inside a mutants/
copy of this repo (nothing here reads a committed file through the gate's ROOT),
because the gate's own tests run in mutmut's stats phase.
"""

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


def test_mutation_key_names_the_function_never_the_positional_mutant_id():
    diff = "--- p\n+++ p\n@@ -1,2 +1,2 @@\n def add(a, b):\n-    return a + b\n+    return a - b"
    key = mutation_key(MODULE, "research_vault.fake.x_add__mutmut_17", diff)
    assert key == KEY_ADD_1
    assert "mutmut_17" not in key


def test_mutation_key_qualifies_a_method_with_its_class():
    diff = (
        "--- p\n+++ p\n@@ -1,2 +1,2 @@\n def size(self):\n-    return 1\n+    return 2"
    )
    assert mutation_key(MODULE, SIZE_1, diff) == KEY_SIZE_1


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
    assert result.unchecked == []


def test_read_module_results_reports_timeouts_by_name_not_as_survivors(tmp_path):
    """A timeout (a mutant that hangs the tests) or a suspicious exit is a
    legitimate outcome that must stay visible: named, counted, never a
    survivor and never silently folded into killed."""
    root = _fake_root(tmp_path)
    _fake_module(root, MODULE, {ADD_1: 36, ADD_2: 35, ADD_3: 1, SIZE_1: 1})

    result = read_module_results(MODULE, root=root)

    assert result.survivors == set()
    assert result.counts == {"timeout": 1, "suspicious": 1, "killed": 2}
    assert result.flagged == [
        ("timeout", ADD_1, KEY_ADD_1),
        ("suspicious", ADD_2, KEY_ADD_2),
    ]


def test_read_module_results_marks_unchecked_and_interrupted_mutants(tmp_path):
    """mutmut swallows a KeyboardInterrupt and still exits 0, leaving `null`
    (not checked) or 2 (interrupted) codes behind -- an incomplete
    measurement the gate must refuse rather than read as zero survivors."""
    root = _fake_root(tmp_path)
    _fake_module(root, MODULE, {ADD_1: None, ADD_2: 2, ADD_3: 1, SIZE_1: 1})

    result = read_module_results(MODULE, root=root)

    assert result.unchecked == [ADD_1, ADD_2]
    assert result.survivors == set()


def test_read_module_results_missing_meta_raises(tmp_path):
    """No .meta is no measurement; it must never parse as a clean module."""
    root = _fake_root(tmp_path)
    (root / "mutants" / "research_vault").mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        read_module_results(MODULE, root=root)


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
    mutate4py era is still a line (mutmut never produces one, so it simply
    never matches a found survivor)."""
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


# --- the mutmut invocation ---------------------------------------------------


def _completed(cmd, code: int = 0) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(cmd, code, stdout="mutmut out", stderr="")


def test_run_mutmut_invokes_the_launcher_with_pattern_env_and_cwd(
    tmp_path, monkeypatch
):
    """The launcher shim, the module's name pattern, --max-children passed
    through, cwd at the repo root (mutmut reads [tool.mutmut] from the cwd),
    PYTHONDONTWRITEBYTECODE=1, and the shims directory PREPENDED to PYTHONPATH
    as an absolute path: test subprocesses change cwd, so a relative entry
    would stop resolving in exactly the processes sitecustomize exists for."""
    root = _fake_root(tmp_path)
    seen: dict = {}

    def fake_run(cmd, **kwargs):
        seen["cmd"] = cmd
        seen.update(kwargs)
        return _completed(cmd)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setenv("PYTHONPATH", "/elsewhere")

    out, code = mutation_gate._run_mutmut("research_vault/x.py", 6, root=root)

    assert (out, code) == ("mutmut out", 0)
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
        cache = root / "tests" / "__pycache__"
        cache.mkdir()
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
        assert proc.stderr == ""


# --- main(): --update-baseline, --out-dir, --only ------------------------------


def _fake_measurement(root: Path, monkeypatch, calls: list[str] | None = None):
    """Make _run_mutmut a no-op that reports success; the module's artifacts
    must already be in place (see _fake_module) so the real reader runs."""

    def fake_run_mutmut(relpath, max_children, root=root):
        if calls is not None:
            calls.append(relpath)
        return "mutmut out", 0

    monkeypatch.setattr(mutation_gate, "ROOT", root)
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


def _argv_gate(monkeypatch, root: Path) -> Path:
    baseline_path = root / "mutation-baseline.txt"
    monkeypatch.setattr(
        sys, "argv", ["mutation_gate.py", "--baseline", str(baseline_path)]
    )
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


def test_update_baseline_refuses_to_write_when_a_module_errors(
    tmp_path, monkeypatch, capsys
):
    """The Q1 guard: a module mutmut did not finish has no survivor list, and
    an empty contribution is not a clean one."""
    root = _fake_root(tmp_path)
    a, b = "research_vault/a.py", "research_vault/b.py"
    _fake_module(root, a, {ADD_1: 0, ADD_2: 1, ADD_3: 1, SIZE_1: 1})
    _fake_module(root, b, {ADD_1: 1, ADD_2: 1, ADD_3: 1, SIZE_1: 1})
    _fake_measurement(root, monkeypatch)

    def fake_run_mutmut(relpath, max_children, root=root):
        return "mutmut out", 1 if relpath == b else 0

    monkeypatch.setattr(mutation_gate, "_run_mutmut", fake_run_mutmut)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [a, b])
    baseline_path = _argv_baseline(monkeypatch, root)

    assert mutation_gate.main() == 1
    assert not baseline_path.exists()
    out = capsys.readouterr().out
    assert f"[baseline] FAIL {b}" in out
    assert "[baseline]   error (1): research_vault/b.py" in out


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


def test_timeouts_are_reported_by_name_and_never_written(tmp_path, monkeypatch, capsys):
    root = _fake_root(tmp_path)
    a = "research_vault/a.py"
    _fake_module(root, a, {ADD_1: 36, ADD_2: 1, ADD_3: 1, SIZE_1: 0})
    _fake_measurement(root, monkeypatch)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: [a])
    baseline_path = _argv_baseline(monkeypatch, root)

    assert mutation_gate.main() == 0
    assert baseline_keys(baseline_path) == {KEY_SIZE_1.replace(MODULE, a)}
    out = capsys.readouterr().out
    assert "timeout" in out
    assert "research_vault.a.x_add__mutmut_1" in out
    assert KEY_ADD_1.replace(MODULE, a) in out


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
        unchecked=[],
    )
    mutation_gate._write_record(out_dir, a, "old out", 0, "ok", recorded)

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("a recorded success must not be re-run")

    monkeypatch.setattr(mutation_gate, "ROOT", root)
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
        survivors=set(), counts={"killed": 1}, unchecked=[ADD_2.replace("fake", "a")]
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

    def fake_run_mutmut(relpath, max_children, root=root):
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


def test_only_requires_update_baseline(tmp_path, monkeypatch):
    root = _fake_root(tmp_path)
    monkeypatch.setattr(
        sys, "argv", ["mutation_gate.py", "--only", "research_vault/a.py"]
    )
    monkeypatch.setattr(mutation_gate, "ROOT", root)
    with pytest.raises(SystemExit) as exit_info:
        mutation_gate.main()
    assert exit_info.value.code == 2


def test_only_rejects_a_path_that_is_no_module(tmp_path, monkeypatch, capsys):
    """A typo in --only must not become a run that measures nothing."""
    root = _fake_root(tmp_path)
    monkeypatch.setattr(mutation_gate, "ROOT", root)
    monkeypatch.setattr(mutation_gate, "_all_modules", lambda: ["research_vault/a.py"])
    _argv_baseline(monkeypatch, root, only=["research_vault/typo.py"])
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

    def fake_run_mutmut(relpath, max_children, root=root):
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
    monkeypatch.setattr(mutation_gate, "changed_modules", lambda base: [])
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
    monkeypatch.setattr(mutation_gate, "changed_modules", lambda base: [a])
    baseline_path = _argv_gate(monkeypatch, root)
    baseline_path.write_text(KEY_ADD_1.replace(MODULE, a) + "\n", encoding="utf-8")

    assert mutation_gate.main() == 1
    out = capsys.readouterr().out
    assert "[gate] FAIL — 1 new survivor(s):" in out
    assert KEY_SIZE_1.replace(MODULE, a) in out


def test_gate_passes_when_every_survivor_is_baselined(tmp_path, monkeypatch, capsys):
    root = _fake_root(tmp_path)
    a = "research_vault/a.py"
    _fake_module(root, a, {ADD_1: 0, ADD_2: 1, ADD_3: 1, SIZE_1: 0})
    _fake_measurement(root, monkeypatch)
    monkeypatch.setattr(mutation_gate, "changed_modules", lambda base: [a])
    baseline_path = _argv_gate(monkeypatch, root)
    baseline_path.write_text(
        KEY_ADD_1.replace(MODULE, a) + "\n" + KEY_SIZE_1.replace(MODULE, a) + "\n",
        encoding="utf-8",
    )

    assert mutation_gate.main() == 0
    assert "[gate] pass — no new survivors" in capsys.readouterr().out.splitlines()


def test_gate_fails_when_a_module_errors(tmp_path, monkeypatch, capsys):
    root = _fake_root(tmp_path)
    a = "research_vault/a.py"
    monkeypatch.setattr(mutation_gate, "ROOT", root)
    monkeypatch.setattr(
        mutation_gate, "_run_mutmut", lambda relpath, max_children, root=root: ("", 1)
    )
    monkeypatch.setattr(mutation_gate, "changed_modules", lambda base: [a])
    _argv_gate(monkeypatch, root)

    assert mutation_gate.main() == 1
    out = capsys.readouterr().out
    assert f"[gate] {a}: error" in out
    assert "[gate]   error (1): research_vault/a.py" in out


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
