# Testing instruments

## The suite

Offline (default): `python -m pytest tests -q -n auto` from the repo root, inside `.venv` (xdist pinned; pass `-n` on the command line, never in addopts). Env-gated live legs are skipped unless flagged; live runs stay serial (polite pools, settle windows).

**Live invocation** (Zotero must be running on the Windows host; the local API answers on `localhost:23119`):

```bash
HARNESS_LIVE=1 HARNESS_LIVE_NET=1 HARNESS_MAILTO=<real address> python -m pytest tests -q
```

`HARNESS_LIVE` unlocks the local-Zotero legs; `HARNESS_LIVE_NET` the external-registry legs (the mailto rides the polite pools — Crossref etiquette). Remaining skips after both flags are the deferred end-to-end autoexport drill (`HARNESS_LIVE_AUTOEXPORT_VAULT`, needs a real vault and a human BBT step). Gated tests are invisible to offline suite-green — after renames or seam moves, run the live legs before claiming the wave complete.

## Poking Zotero

Preference order:

1. **The harness's own client** — same code paths production uses, findings transfer:
   `python -c "from knowledge_harness.zotero import ZoteroClient; ..."` — or the CLI: `python -m knowledge_harness probe` / `doctor`.
2. **pyzotero** (dev extra, pinned) — richer read API for test authoring and diagnostics:
   `python -c "from pyzotero import zotero; z = zotero.Zotero('0','user',local=True); print(z.top(limit=5))"`
   Posture: local mode is read-only by default and stays that way — local writes sit behind Zotero's own GUI consent dialog (admission is a human act). Web API for tests: read-only key by default; a write-capable key only for a test that needs it, only against a scratch/group library, and no key is ever stored in this repo.
3. **Raw JSON-RPC** (escape hatch when neither client covers a probe):
   `curl -s -X POST http://localhost:23119/better-bibtex/json-rpc -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"api.ready","id":1}'`
   Record any newly discovered API fact in `docs/environment.md` with a date.

## The stale-pyc trap

A same-length edit reverted within the same second is invisible to bytes, to `git status`, and to CPython's timestamp-based `.pyc` validation (mtime + size) — the interpreter keeps running the old bytecode while the source reads correctly. Rules: (1) never run a code-swap experiment (mutation replay, hot-patch trial) in a tree another run is using; (2) set `PYTHONDONTWRITEBYTECODE=1` and clear `__pycache__` first; (3) if caching is wanted, use hash-based pycs (`compileall --invalidation-mode checked-hash`).

## Exemplars

Live test files (`tests/test_*_live.py`) are the copy-from source for new live tests: fixture shapes, settle windows, cleanup discipline. Environment facts (versions, API surfaces, path translation) live in `docs/environment.md` — check it before rediscovering; extend it when a live probe teaches something new.
