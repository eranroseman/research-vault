# Testing instruments

## The suite

Offline (default): `python -m pytest tests -q` from the repo root, inside `.venv`. Env-gated live legs are skipped unless flagged.

**Live invocation** (Zotero must be running on the Windows host; the local API answers on `localhost:23119`):

```bash
HARNESS_LIVE=1 HARNESS_LIVE_NET=1 HARNESS_MAILTO=<real address> python -m pytest tests -q
```

`HARNESS_LIVE` unlocks the local-Zotero legs; `HARNESS_LIVE_NET` the external-registry legs (the mailto rides the polite pools — Crossref etiquette). Remaining skips after both flags are the deferred end-to-end autoexport drill (`HARNESS_LIVE_AUTOEXPORT_VAULT`, needs a real vault and a human BBT step). Gated tests are invisible to offline suite-green — after renames or seam moves, run the live legs before claiming the wave complete (this bit once: the `.detail` fallout).

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

## Exemplars

Live test files (`tests/test_*_live.py`) are the copy-from source for new live tests: fixture shapes, settle windows, cleanup discipline. Environment facts (versions, API surfaces, path translation) live in `docs/environment.md` — check it before rediscovering; extend it when a live probe teaches something new.
