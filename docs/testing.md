# Testing instruments

## The suite

Offline (default): `python -m pytest tests -q -n auto` from the repo root, inside `.venv` (xdist pinned; pass `-n` on the command line, never in addopts). Env-gated live legs are skipped unless flagged; live runs stay serial (polite pools, settle windows).

**Live invocation** (Zotero must be running on the Windows host; the local API answers on `localhost:23119`, the unsynced test instance on `localhost:23129` — `python -m research_vault probe --base <base>` names each). Read-only legs run against whichever `--base` they are given; **write-capable legs run only against the test instance** and refuse `zotero.DEFAULT_BASE`:

```bash
RV_LIVE=1 RV_LIVE_NET=1 RV_MAILTO=<real address> python -m pytest tests -q            # read-only local-Zotero and external-registry legs
RV_LIVE=1 RV_LIVE_WRITE_BASE=http://localhost:23129 python -m pytest tests -q -k live  # plus the add/trash/delete leg (one consent dialog the first time)
```

The offline suite is hermetic through four mechanisms in `tests/conftest.py`: three autouse fixtures the markers gate — a marked test keeps the real thing (the marker each honours is named below), and every unmarked test gets the block in every run, live flags or not — and one opt-in fixture for subprocess tests.

- **The Zotero client patch** (`_no_zotero_socket`; `live` keeps the real transport): every `ZoteroClient` read outside the `live` markers is an outage, so the offline suite gives the same answer on a machine with no Zotero and on one where a production instance is running; a test that needs a Zotero answer registers it on `tests/fakes.py::FakeZotero`.
- **The socket block** (`_no_socket`; `live` or `live_net` keeps the real transport): any TCP connect raises, naming the address, so no client class can reopen the hole; the resolver is blocked with it — `socket.getaddrinfo` raises for any host outside loopback, because `urllib` resolves before it connects, and a leaked hostname would otherwise be a real DNS query on a networked machine and an outage on one without DNS.
- **`dead_base` for subprocess tests**: both blocks are in-process patches, so a test that launches the CLI in a subprocess is hermetic only through the `dead_base` fixture — an ephemeral loopback port nothing listens on, refused at once — which is also the one address the in-process block lets through.
- **The per-test HOME** (`_per_test_home`; `live` or `live_net` keeps the real home, because the operator's registry and profile paths are what a live leg reads): `HOME` and `XDG_CONFIG_HOME` point at a fresh directory holding only a synthetic git identity (as global config, so a local `user.name` a test sets still wins; the git variables that would outrank it are removed from the environment), for the test and every subprocess it launches, so nothing a test reads from `~` — doctor's plugin registry, git's global excludes, a credential helper — depends on the machine (measured 2026-09-14: a mutant of the registry read died on the developer's machine and lived on the runner). The session-scoped template vaults are built under a home of the same shape.

`RV_LIVE` unlocks the local-Zotero legs; `RV_LIVE_NET` the external-registry legs (the mailto rides the polite pools — Crossref etiquette). `RV_LIVE_WRITE_BASE` unlocks the write-capable leg, which carries both the `live` and the `live_write` markers — the hermeticity fixtures honour `live`; `live_write` only adds the base gate. With all three set the suite has no remaining skip. Gated tests are invisible to offline suite-green — after renames or seam moves, run the live legs before claiming the wave complete.

The first write leg on a machine pops Zotero's consent dialog on the test instance; answer **Always Allow** there and the key persists in the scratch vault's `.research-vault/zotero-keys.json` for the run. If a later run re-opens the dialog, export that key as `RV_LIVE_WRITE_KEY` and the leg runs unattended. `--as-of YYYY-MM-DD` on `verify` and `inbox` pins the instant a check compares against, which is how a recorded fixture replays without drifting (spec §7).

## Poking Zotero

Preference order:

1. **research-vault's own client** — same code paths production uses, findings transfer:
   `python -c "from research_vault.zotero import ZoteroClient; ..."` — or the CLI: `python -m research_vault probe` / `doctor`.
   `python -m research_vault probe --base http://localhost:23129` names the test instance.
2. **pyzotero** (dev extra, pinned) — richer read API for test authoring and diagnostics:
   `python -c "from pyzotero import zotero; z = zotero.Zotero('0','user',local=True); print(z.top(limit=5))"`
   Posture: local mode is read-only by default and stays that way — local writes sit behind Zotero's own GUI consent dialog (admission is a human act). Web API for tests: read-only key by default; a write-capable key only for a test that needs it, only against a scratch/group library, and no key is ever stored in this repo.
3. **Raw JSON-RPC** (escape hatch when neither client covers a probe):
   `curl -s -X POST http://localhost:23119/better-bibtex/json-rpc -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"api.ready","id":1}'`
   Record a newly discovered API fact where the design uses it, with its date and how it was established. There is no standing facts file: one went stale for three weeks while claiming to be live-verified.

## The stale-pyc trap

A same-length edit reverted within the same second is invisible to bytes, to `git status`, and to CPython's timestamp-based `.pyc` validation (mtime + size) — the interpreter keeps running the old bytecode while the source reads correctly. Rules: (1) never run a code-swap experiment (mutation replay, hot-patch trial) in a tree another run is using; (2) set `PYTHONDONTWRITEBYTECODE=1` and clear `__pycache__` first; (3) if caching is wanted, use hash-based pycs (`compileall --invalidation-mode checked-hash`).

## The wrong-tree import trap

An editable install can resolve `research_vault` to the parent checkout instead of the scratch/worktree copy being probed — every probe then silently measures the wrong code. Rules for any scratch-tree or worktree probe: run with `PYTHONPATH=.` and open with an import-path canary (`python -c "import research_vault; print(research_vault.__file__)"`) asserting the tree under test.

## Exemplars

Live test files (`tests/test_*_live.py`) are the copy-from source for new live tests: fixture shapes, settle windows, cleanup discipline. Environment facts are not kept in a file. Run `python3 -m research_vault probe` for live values, and read the specs for facts a probe cannot answer.

## The WSL2 low-port trap

WSL2 swallows RST on low ports, so a connection to `127.0.0.1:1` hangs for the full connect
timeout (5s) instead of failing fast — three dead-port tests were ~15.2s of a 67.4s serial
run (2026-08-24, `2e6f1385` @ 15:15:14Z). A dead-port fixture must bind an ephemeral port,
close it, and hand out `http://127.0.0.1:<port>` (measured: ~1ms fail vs 5029ms for port 1).

## Multi-seat venv parity

During the pre-slice batch the seats kept each venv bound to its referent — main's venv
validates main, each worktree's venv validates its branch — so environment upgrades were
deferred until post-merge to keep the seats' green runs comparable (2026-08-24,
`cb5ecedf` @ 16:30:23Z). A venv change mid-flight makes "main is green" and "branch is green"
mean different things.
