# Environment facts (live-verified)

Machine facts the harness design depends on. Each dated — recheck on stack changes.

| Fact | Value | Verified |
|---|---|---|
| Host | Windows + WSL2, `networkingMode=mirrored` (`.wslconfig`) — Windows localhost services reachable as localhost from WSL | 2026-08-15 |
| Zotero | 9.0.6, running on Windows; local API **enabled** — `http://localhost:23119/api/users/16413661` returns items from WSL | 2026-08-15 |
| Better BibTeX | 9.0.55; JSON-RPC responding at `localhost:23119/better-bibtex/json-rpc` (`api.ready` verified) | 2026-08-15 |
| Zotero user library ID | 16413661 | 2026-08-15 |
| PDF path translation | BBT returns Windows paths (`D:\...`); `wslpath -u` resolves them from WSL (live-verified against a real PDF, see research/zotero-bridge-design-space.md) | 2026-08-16 |
| obsidian-cli | Installed at `~/.local/bin/obsidian-cli` but cannot find Obsidian from WSL ("Please make sure Obsidian is running") — app-level integration unresolved | 2026-08-15 |
| git | 2.43.0 (WSL) | 2026-08-15 |
| gh CLI | Authenticated as eranroseman (https protocol) | 2026-08-16 |
| Zotero annotations | Library currently has zero PDF annotations — annotation-extraction paths source-verified only, not live-verified | 2026-08-16 |
