# Environment facts (live-verified)

Machine facts the harness design depends on. Each dated — recheck on stack changes.

| Fact | Value | Verified |
|---|---|---|
| Host | Windows + WSL2, `networkingMode=mirrored` (`.wslconfig`) — Windows localhost services reachable as localhost from WSL | 2026-08-15 |
| Zotero | 9.0.6, running on Windows; local API **enabled** — `http://localhost:23119/api/users/16413661` returns items from WSL | 2026-08-15 |
| Better BibTeX | 9.0.55; JSON-RPC responding at `localhost:23119/better-bibtex/json-rpc` (`api.ready` verified) | 2026-08-15 |
| BBT auto-export JSON-RPC surface | BBT 9.0.55 JSON-RPC exposes `autoexport.add` only; `.list`/`.remove`/`.delete`/`.get` live-probed `-32601 METHOD_NOT_FOUND`; `add` is collection-scoped by implementation (source-verified). | 2026-08-20 |
| Whole-library auto-export registration | `autoexport.add("//", …)` fails 404 `path is too short` before registration storage: no entry is created, so whole-library registration is impossible through the public RPC. Provisioning is a one-time human step in BBT Preferences. | 2026-08-20 |
| BBT auto-export persistence | BBT persists auto-exports as profile preference keys `better-bibtex.autoExport.<encoded-path>`. Human-debugging fact only: doctor detection stays behavioral (target presence plus staleness) and never scrapes preferences. | 2026-08-20 |
| Live drill vault disposal | The retained drill vault was removed through the drill's own confirmed-cleanup path after read-only inspection of the Windows profile preferences and `zotero.sqlite` confirmed no registration was ever stored for its target; the sibling audit state is stamped `cleanup-confirmed`. | 2026-08-21 |
| Zotero user library ID | 16413661 | 2026-08-15 |
| Zotero local write probe | Malformed-JSON `POST /api/users/0/items` returns HTTP 400 (not 501); write support must be version-gated fail-closed, not inferred from HTTP status | 2026-08-16 |
| CSL-JSON read scope | Paged `/api/users/0/items/top?format=csljson` returned 1,407 citekey-ID records and 4 URI-ID top-level attachment/note records; plain `/items` returned 1,341 URI-ID child records among 2,748 total. Whole-library client reads use `/items/top`, normalize URI IDs through BBT citation-key lookup, and exclude only records with no mapping. | 2026-08-16 |
| BBT citation-key lookup | `item.citationkey` returns JSON `null` values for item keys with no citekey; the client filters those absent mappings and exposes only string-to-string entries. No item identifiers recorded. | 2026-08-16 |
| BBT key stability (9.0.57, current docs 2026-08-22) | Keys are conservative-by-default: no regeneration on metadata change; pattern changes leave existing keys untouched. Drift requires an explicit manual Refresh (select → right-click → Refresh) — the one hazard: never bulk-Refresh keys already cited in a vault. Auto-pin-after-delay no longer exists (stale-recall corrected by author); manual fix-to-value pinning remains | 2026-08-22 |
| BBT version drift | BBT auto-updated 9.0.55 → **9.0.57**; live re-probe 2026-08-22: `autoexport.list` still `-32601 METHOD_NOT_FOUND` — the add-only/collection-only RPC surface facts hold at 9.0.57 | 2026-08-22 |
| PDF path translation | BBT returns Windows paths (`D:\...`); `wslpath -u` resolves them from WSL (live-verified against a real PDF, see research/zotero-bridge-design-space.md) | 2026-08-16 |
| obsidian-cli | Installed at `~/.local/bin/obsidian-cli` but cannot find Obsidian from WSL ("Please make sure Obsidian is running") — app-level integration unresolved | 2026-08-15 |
| git | 2.43.0 (WSL) | 2026-08-15 |
| gh CLI | Authenticated as eranroseman (https protocol) | 2026-08-16 |
| Zotero annotations | One annotation is now live-observed through BBT `item.attachments`: string fields `annotationAuthorName`, `annotationColor`, `annotationComment`, `annotationPageLabel`, `annotationSortIndex`, `annotationText`, `annotationType`, `dateAdded`, `dateModified`, `itemType`, `key`, `parentItem`; integer `version`; empty-list `tags`; empty-dict `relations`; and `annotationPosition` dict with integer `pageIndex` and list-of-lists `rects`. No annotation text or identifiers recorded. | 2026-08-16 |
