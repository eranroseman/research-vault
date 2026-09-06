# Zotero full-text indexing: mechanism

Disposition: historical (2026-09-06) [should-be-scoping-review]

**Verified (2026-08-24):** A second session independently re-fetched all 60 claims raw at the pinned
commits (plus GitHub API metadata and the live docs/forum pages): zero fabrications, verbatim quotes
byte-exact, and both high-surprise findings hold — the FTS5 `fulltext.sqlite` schema, and
`document-worker` being a rename of `pdf-worker` (301 redirect). Three substantive corrections and
the citation-precision fixes were folded in `9c5850a`; the extraction file-size-cap unconfirmed
marker closed (no size check in `getFullText()`). Dispositions routed: spec §10.1's /fulltext-leg
entry now carries the consumer facts (`indexedPages == totalPages` gate, 404 semantics, `\f` page
split, one-text-source rule for digest and lint) and the scanned-source remedy — zotero-ocr at the
first scanned source that matters; conversion plugins declined (cloud exfiltration or unverifiable
derived text). Remaining follow-ups (cutover dating, mineru hosted-API OCR default) stay with this
note's author.

We already confirmed empirically (curl against a local Zotero on :23119) that `GET /users/<id>/items/<key>/fulltext`
returns `{content, indexedPages, totalPages}` and that `content` is a high-fidelity (99.5-99.7%
similar to raw PyMuPDF) extraction. This note traces *how* Zotero builds and serves that index, from
primary sources only: `github.com/zotero/zotero`, `github.com/zotero/document-worker`,
`github.com/zotero/pdf.js` (Zotero's fork), `zotero.org/support`, and staff-authored forum posts.

Source citations are pinned to commits so line numbers stay valid: `zotero/zotero` @
[`753dbf5`](https://github.com/zotero/zotero/commit/753dbf557ad4fbd958594253c9ff28e585d7837c)
(branch `main`, 2026-08-24), `zotero/document-worker` @
[`bd2ac56`](https://github.com/zotero/document-worker/commit/bd2ac56bad043d0536b72fc912a1929e41159c74)
(branch `master`), `zotero/pdf.js` @
[`2a28e53`](https://github.com/zotero/pdf.js/commit/2a28e531095d40b3333d939fc80059124f184fdf)
(branch `master`). (The worker repo is `zotero/document-worker`, referenced from the client as
`resource://zotero/document-worker/worker.js` — there is no `zotero-pdf-worker` repo.)

Points that couldn't be pinned to a primary source are marked **unconfirmed** inline, at the point
they come up, rather than collected separately.

## Q1: PDF text extraction engine

**PDF.js (Zotero's own fork), used at the `core/` level, not poppler/xpdf, and not OCR.**

- The client-side PDF worker manager loads its worker from `resource://zotero/document-worker/worker.js`
  and asset paths for `cmaps/` and `standard_fonts/` — hallmark PDF.js resources — from
  `resource://zotero/reader/pdf/web/`.
  [`chrome/content/zotero/xpcom/pdfWorker/manager.js:26-35`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/pdfWorker/manager.js#L26-L35)
- `Zotero.PDFWorker.getFullText(itemID, maxPages, isPriority, password)` sends a `pdf.getFulltext`
  message to that worker.
  [`chrome/content/zotero/xpcom/pdfWorker/manager.js:612-640`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/pdfWorker/manager.js#L612-L640)
- `zotero/document-worker` is a Node/Web-Worker package (`.gitmodules` shows two git submodules:
  `pdf.js` → `https://github.com/zotero/pdf.js.git`, `structured-document-text`).
  [`document-worker/.gitmodules`](https://github.com/zotero/document-worker/blob/bd2ac56bad043d0536b72fc912a1929e41159c74/.gitmodules)
  README: "It supports PDF annotation processing, PDF text extraction and rendering, and structured
  text extraction from PDFs, EPUBs, and HTML snapshots."
  [`document-worker/README.md`](https://github.com/zotero/document-worker/blob/bd2ac56bad043d0536b72fc912a1929e41159c74/README.md)
- The worker's `pdf.getFulltext` handler calls `getFulltext()`, defined in
  `src/pdf/index.js:463-510`. It builds a PDF.js `LocalPdfManager` (imported directly from
  `../../pdf.js/src/core/pdf_manager.js`, line 10 — line 7 of the same import block is an unrelated
  `Util` import) via the local `getPdfManager()` helper (`:430-461`), then pulls characters
  page-by-page via the local `getPageChars()` wrapper (`:56-59`) →
  `pdfDocument.module.getPageChars(pageIndex)`.
  [`document-worker/src/pdf/index.js:10,56-59,430-461,463-510`](https://github.com/zotero/document-worker/blob/bd2ac56bad043d0536b72fc912a1929e41159c74/src/pdf/index.js#L463-L510)
- `pdfDocument.module` is `Module` from Zotero's PDF.js fork,
  `src/core/module/module.js` — a Zotero-specific addition not present in upstream Mozilla PDF.js
  (confirmed: it sits under `src/core/module/`, alongside `paragraph-break-compat.js` and
  `structure.js`, none of which exist in stock PDF.js). `getPageChars()` calls
  `page.getPageContent()` / `page.extractTextContent()` (both from PDF.js's own evaluator) and then
  post-processes the raw character stream through `getStructuredPageChars()`.
  [`pdf.js/src/core/module/module.js:82-106`](https://github.com/zotero/pdf.js/blob/2a28e531095d40b3333d939fc80059124f184fdf/src/core/module/module.js#L82-L106)

So the pipeline is: Zotero client → `document-worker` (Web Worker / Node) → Zotero's `pdf.js` fork's
`core/` module (`LocalPdfManager`, `extractTextContent`) → structured character stream → joined into
plain text. This is a pure text-layer read of what PDF.js's parser finds in the PDF's content
streams; nothing renders pixels or calls a vision/OCR model (see Q2).

Two older repos, `zotero/cross-xpdf` (xpdf's `pdftotext`/`pdfinfo`, last pushed 2022-04-04) and
`zotero/cross-poppler` (poppler's `pdftotext`/`pdfinfo`, last pushed 2020-02-03), exist in the
`zotero` org and confirm Zotero *did* shell out to native `pdftotext` binaries at some point, but
both are stale relative to `document-worker` (pushed 2026-08-19, five days before this research) and
neither is referenced from current `fulltext.js`. Separately, `github.com/zotero/pdf-worker` — a name
closer to the task's original guess — 301-redirects to `github.com/zotero/document-worker`
(confirmed: `curl -so /dev/null -w '%{http_code} %{redirect_url}' https://github.com/zotero/pdf-worker`
→ `301 https://github.com/zotero/document-worker`), i.e. `document-worker` is a rename of the
project, not a new one — its own commit history should let someone date the cutover more precisely.
Whether/when the cutover from xpdf-or-poppler-`pdftotext` to the in-process PDF.js worker happened is
still **unconfirmed** here — that history wasn't read — only that current source has fully moved off
the native binaries for fulltext extraction.

## Q2: OCR fallback

**No OCR. Zotero indexes only whatever machine-readable text layer already exists in the PDF.**

- Source: `getFulltext()` in `document-worker` builds its output purely from PDF.js's character
  stream (`char.c` for each character PDF.js's parser found in the page's content stream); there is
  no image-analysis or OCR step anywhere in the call chain from `pdf.getFulltext` down to
  `LocalPdfManager`.
  [`document-worker/src/pdf/index.js:480-499`](https://github.com/zotero/document-worker/blob/bd2ac56bad043d0536b72fc912a1929e41159c74/src/pdf/index.js#L480-L499)

- `document-worker`'s `package.json` has no OCR-capable dependency (no `tesseract.js` or similar).
  It does depend on `onnxruntime-web`, but that backs the `structure/model/block-seg` classifier
  used for *layout/structure* analysis of already-extracted text/glyphs (block segmentation for the
  "structured document text" feature), not pixel-level character recognition.
  [`document-worker/package.json`](https://github.com/zotero/document-worker/blob/bd2ac56bad043d0536b72fc912a1929e41159c74/package.json)

- Docs page confirms the "OCR is external" model: the Rebuild Index option "may be helpful if you
  use OCR text recognition on a large number of attachment files" — i.e., OCR is something the user
  runs on the PDF *before* Zotero indexes it, not something Zotero performs.
  [zotero.org/support/preferences/search](https://www.zotero.org/support/preferences/search)
  (page text, "Full-Text Cache" section, retrieved 2026-08-24)

- Staff forum confirmation (dstillman, Zotero Team), thread "What's up with OCR?", 2014-01-27, in
  response to "It would be super if Zotero could implement OCR on PDFs. Any chance of that?":

  > "It might happen at some point for people using Zotero File Storage, but not anytime soon."

  [forums.zotero.org/discussion/34575/whats-up-with-ocr](https://forums.zotero.org/discussion/34575/whats-up-with-ocr)

  This post is from 2014, so it's dated, but it is consistent with the current source: no OCR path
  exists in the 2026-08 `document-worker`/`pdf.js` code reviewed above, so nothing has since made it
  false. Whether Zotero staff have made a *more recent* (post-2014) statement reaffirming "no OCR" is
  **unconfirmed** — searches for a newer staff quote on this specific point did not surface one; the
  several other candidate threads found (`/discussion/7614`, `/discussion/110013`, `/discussion/2615`,
  `/discussion/116587`, `/discussion/73440`) either had no dstillman post or a dstillman post that
  didn't address OCR substantively.

## Q3: `indexedPages`/`totalPages` vs `indexedChars`/`totalChars`

**Confirmed from source, both the meaning and why our two test cases showed them equal.**

- `totalPages` = the PDF's actual page count as PDF.js parsed it
  (`pdfManager.pdfDocument.numPages`); `extractedPages`/`indexedPages` = how many of those pages were
  actually walked for text, which is `Math.min(requestedPages, actualCount)` when a page cap is
  passed, or all pages if none is passed.
  [`document-worker/src/pdf/index.js:463-478,507-508`](https://github.com/zotero/document-worker/blob/bd2ac56bad043d0536b72fc912a1929e41159c74/src/pdf/index.js#L463-L478)
- The page cap comes from the `extensions.zotero.fulltext.pdfMaxPages` preference, default **100**.
  [`defaults/preferences/zotero.js:114`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/defaults/preferences/zotero.js#L114)
  `Zotero.FullText.indexPDF()` reads it and passes `allPages ? null : maxPages` to `getFullText()`.
  [`chrome/content/zotero/xpcom/fulltext.js:623-664`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L623-L664)
  So `indexedPages == totalPages` whenever the PDF has ≤100 pages (our 9/9 and 8/8 test cases both
  qualify) or when a caller explicitly requests `allPages`/`complete`. They diverge once a PDF
  exceeds the 100-page default — only the first `pdfMaxPages` pages get indexed and `indexedPages`
  stays fixed at 100 while `totalPages` shows the true count, unless the user reindexes with "all
  pages" or bumps the pref.
- Confirmed via the storage layer too: `getIndexedState()` treats `stats.indexed < stats.total` as
  `INDEX_STATE_PARTIAL`.
  [`chrome/content/zotero/xpcom/fulltext.js:2896-2939`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L2896-L2939)
  A background "reindex limit" queue (`_reindexLimitTimeoutIDs`, declared `:110`) exists
  specifically to reprocess items sitting below the current char/page limit if the limit preference
  changes.
  [`chrome/content/zotero/xpcom/fulltext.js:3085-3106`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L3085-L3106)
  (comment: "are tracked separately, via indexedChars/totalChars and indexedPages/totalPages")

**`indexedChars`/`totalChars` — confirmed, non-paginated content type, but the two only diverge on
some paths, not all.** Used for anything that isn't a PDF: HTML/snapshot documents (via
`indexDocument()`), EPUB (via `indexEPUB()`), and other text items (via the generic `indexItem()`).
Whether `indexedChars` is actually capped below `totalChars` depends on which of those three
functions ran:

- **`indexDocument()`** (HTML/snapshots) does **not** truncate the stored text: `totalChars = text.length` and `indexedChars: text.length` are set from the *same* untruncated `text` variable —
  an over-`textMaxLength` document only gets a `Zotero.debug()` log line, not a cut. So on this path
  `indexedChars` always equals `totalChars`, regardless of the preference.
  [`chrome/content/zotero/xpcom/fulltext.js:591-611`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L591-L611)
- **`indexEPUB()`** does truncate, per chapter, as it accumulates: `totalChars` sums each chapter's
  full length, while `bodyText.substring(0, maxLength - text.length)` caps what's appended to the
  stored `text`.
  [`chrome/content/zotero/xpcom/fulltext.js:697`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L697)
- **`indexItem()`** (the generic text-item path — see the plugin `.md` attachments below) also
  truncates: `totalChars = text.length` first, then `text = text.substr(0, maxLength)` if not
  `complete`, before the `{indexedChars: text.length, totalChars}` stats object is built.
  [`chrome/content/zotero/xpcom/fulltext.js:859-863`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L859-L863)

`extensions.zotero.fulltext.textMaxLength` (default 500,000, "~100,000 words or 180-200 pages of
content" per docs) is the shared preference all three read, even though only two of the three
enforce it as a hard cap.
[`defaults/preferences/zotero.js:113`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/defaults/preferences/zotero.js#L113)
(default value).

**Which pair applies to which item is a hardcoded content-type switch**, not a per-item flag:
`getIndexedState()` uses `case 'application/pdf': /* use getPages() */ default: /* use getChars() */`.
[`chrome/content/zotero/xpcom/fulltext.js:2894-2918`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L2894-L2918)
Confirmed again at the API layer, which reads and returns all four columns unconditionally and lets
the two that don't apply come back `undefined` (dropped by `JSON.stringify`):
[`chrome/content/zotero/xpcom/server/server_localAPI.js:1431-1452`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/server/server_localAPI.js#L1431-L1452)
and the docs page states this directly: "`indexedChars` and `totalChars` are used for text
documents, while `indexedPages` and `totalPages` are used for PDFs."
[zotero.org/support/dev/web_api/v3/fulltext_content](https://www.zotero.org/support/dev/web_api/v3/fulltext_content)

## Q4: Normalization rules

**Three concrete, source-confirmed rules — dehyphenation-at-line-break, whitespace/line-break
handling, and Unicode NFC normalization.**

1. **Dehyphenation at line breaks**, done by character-set membership, not dictionary lookup.
   Zotero's PDF.js fork marks a hyphen-like character `ignorable` when it both ends a line
   (`lineBreakAfter`) and is in a fixed set of "layout hyphen" code points — deliberately excluding
   semantic dashes (en/em dash etc.) so real punctuation at a line end isn't dropped:

   ```js
   // Only hyphen-like characters can plausibly be layout-only hyphenation at a
   // line ending. Semantic dashes (figure dash, en dash, em dash, etc.) must stay
   // in the text when they happen to end a line.
   const lineBreakHyphenChars = new Set([
     '\x2D', '֊', '᐀', '᠆', '‐',
     '⸗', '⸚', '゠', '﹣', '－'
   ]);
   ```

   (source uses `\uXXXX` escapes, not literal glyphs — same ten code points either way: hyphen-minus,
   Armenian hyphen, Canadian syllabics hyphen, Mongolian todo soft hyphen, hyphen, double oblique
   hyphen, hyphen with diaeresis, katakana-hiragana double hyphen, small hyphen-minus, fullwidth
   hyphen-minus.)
   [`pdf.js/src/core/module/structure.js:600-606,863-866`](https://github.com/zotero/pdf.js/blob/2a28e531095d40b3333d939fc80059124f184fdf/src/core/module/structure.js#L600-L606)
   `ignorable` characters are then skipped entirely when the text is assembled:
   `if (!char.ignorable) { text.push(char.c); ... }`.
   [`document-worker/src/pdf/index.js:484-494`](https://github.com/zotero/document-worker/blob/bd2ac56bad043d0536b72fc912a1929e41159c74/src/pdf/index.js#L484-L494)
   This is heuristic (character identity + line-end position), not a dictionary check for whether
   the two halves actually form a real word — matches the observed "hyphenation-joining" diff vs.
   raw PyMuPDF extraction.

2. **Line-break vs. paragraph-break vs. word-space handling.** A line break that is *not* also a
   paragraph break gets replaced with a single space (so a justified-text line wrap doesn't glue two
   words together); a paragraph break becomes `\n`; a page boundary becomes `\f` between pages, plus
   `\n\n` after each page:

   ```js
   if (char.spaceAfter || (char.lineBreakAfter && !char.paragraphBreakAfter)) {
     text.push(' ');
   }
   if (char.paragraphBreakAfter) {
     text.push('\n');
   }
   ...
   text.push('\n\n');
   if (i !== pageIndexes.length - 1) { text.push('\f'); }
   ```

   [`document-worker/src/pdf/index.js:480-499`](https://github.com/zotero/document-worker/blob/bd2ac56bad043d0536b72fc912a1929e41159c74/src/pdf/index.js#L480-L499)
   Paragraph-break detection itself is geometric (line-spacing/gap heuristics comparing consecutive
   lines' bounding boxes, fonts and heights), implemented in
   [`pdf.js/src/core/module/paragraph-break-compat.js:91-149`](https://github.com/zotero/pdf.js/blob/2a28e531095d40b3333d939fc80059124f184fdf/src/core/module/paragraph-break-compat.js#L91-L149).

3. **Unicode NFC normalization**, applied once to the fully assembled string, with an explicit
   comment tying it to indexing correctness:

   ```js
   // Normalize text by precomposing characters and accents into single composed characters
   // to prevent indexing issues
   text = text.join('').trim().normalize('NFC');
   ```

   [`document-worker/src/pdf/index.js:501-503`](https://github.com/zotero/document-worker/blob/bd2ac56bad043d0536b72fc912a1929e41159c74/src/pdf/index.js#L501-L503)
   This runs on the `content` returned by `getFullText()` before it's written to the `.zotero-ft-cache`
   file, so it's present in what the local API serves too (see Q5).

4. **Separately, at search-query time** (not at indexing time), `fulltext.js` also normalizes both
   the query and the compared content before a literal-phrase match: case- and diacritic-folding via
   `Zotero.Utilities.Internal.normalizeForSearch()`, then whitespace/hyphen runs collapsed to a
   single space on both sides, specifically so extraction-layout differences ("decision-making" vs.
   "decision making") don't break a phrase match:

   ```js
   // Case- and diacritic-insensitive, to match the content index
   // (findItemsWithContent). Whitespace and hyphen runs are collapsed to single
   // spaces on both sides (normalizeForSearch folds dash variants to '-'), so the
   // separators between a phrase's words match flexibly -- extraction layout and
   // compound styling ("decision-making" vs. "decision making") vary them -- while
   // other punctuation has to match literally.
   searchText = Zotero.Utilities.Internal.normalizeForSearch(searchText)
     .replace(/[\s-]+/g, ' ');
   ```

   [`chrome/content/zotero/xpcom/fulltext.js:2166-2182`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L2166-L2182)
   `getWordMatchClause()`, used for FTS5 word-index matching, applies only the `normalizeForSearch()`
   half of this (case/diacritic folding) — it does not also collapse whitespace/hyphen runs.
   [`chrome/content/zotero/xpcom/fulltext.js:2441-2442`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L2441-L2442)
   This is query-side, applied when matching against the index, and is a different code path from
   the extraction-time NFC normalization above (point 3) — it doesn't change what's stored in
   `.zotero-ft-cache` or served by the `/fulltext` API.

## Q5: Storage

**Two SQLite databases, plus flat cache files — and the API serves the cache file directly, not a
re-extraction.**

- **`zotero.sqlite`** (main DB) has a `fulltextItems` table, one row per attachment item, keyed by
  `itemID`, holding `indexedChars, totalChars, indexedPages, totalPages, version, synced` — this is
  stats/sync bookkeeping, **not** the extracted text itself. The written columns aren't a fixed list
  in the query itself — `setFulltextItem` builds them dynamically from whatever keys are present on
  the caller's `stats` object (`indexedChars`/`totalChars` or `indexedPages`/`totalPages`, per Q3).
  [`chrome/content/zotero/xpcom/fulltext.js:510-528`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L510-L528)
  (`setFulltextItem`), columns enumerated at
  [`fulltext.js:2799-2877`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L2799-L2877)
  (`getPages`/`getChars`/`setPages`/`setChars`).

- **The actual extracted text lives in a per-attachment cache file on disk**,
  `.zotero-ft-cache`, in the attachment's storage directory:
  `this.__defineGetter__("fulltextCacheFile", function () { return '.zotero-ft-cache'; })`.
  [`chrome/content/zotero/xpcom/fulltext.js:27`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L27)
  `indexPDF()`/`indexEPUB()`/`indexDocument()` all call `Zotero.File.putContentsAsync(cacheFilePath, text)`
  (or `writeCacheFile()`) after extraction.
  [`chrome/content/zotero/xpcom/fulltext.js:660`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L660)

- **A second, separate SQLite database — `fulltext.sqlite`** — holds the FTS5 word-search index,
  attached at runtime as `ftindex`:
  `let path = Zotero.DataDirectory.getDatabase('fulltext'); await Zotero.DB.queryAsync("ATTACH DATABASE ? AS ftindex", [path]);`
  [`chrome/content/zotero/xpcom/fulltext.js:130-131`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L130-L131)
  Four contentless FTS5 virtual tables live there: `fulltextContent` (non-CJK, `unicode61`
  tokenizer), `fulltextContentCJK` (CJK 2-grams, `ascii` tokenizer), `fulltextNotes` and
  `fulltextNotesCJK` (note text, `trigram`/`ascii`), plus bookkeeping tables
  `fulltextIndexState`/`fulltextNoteIndexState`/`fulltextIndexMeta`/`noteText`. The comment block
  is explicit about the split:

  > "It's a local, rebuildable index kept out of zotero.sqlite (so it doesn't bloat the main DB or
  > its backups), versioned independently via PRAGMA user_version. The original extracted text
  > still lives in the .zotero-ft-cache files, so the content tables store only the index built
  > from the normalized text."

  [`chrome/content/zotero/xpcom/fulltext.js:116-230`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L116-L230)
  This confirms the `fulltextItems`/`fulltextWords` guess from the task brief is close but not
  exact: there's no `fulltextItemWords`/`fulltextWords` table in current source — the search index is
  FTS5 virtual tables (`fulltextContent`/`fulltextContentCJK`/`fulltextNotes`/`fulltextNotesCJK`) in
  a second attached database, and `fulltextItems` (in the main DB) is the stats/sync table, not the
  word index.

- **The local API's `GET /items/<key>/fulltext` endpoint reads the `.zotero-ft-cache` file directly
  off disk and returns its contents verbatim — it does not re-extract or otherwise transform the
  text at request time.** This directly answers "is the raw stored content the same content the API
  returns, or does the API do something else": it's the same content, read straight from the cache
  file. If the cache file is missing, the endpoint returns `404` rather than lazily re-extracting:

  ```js
  let file = Zotero.Fulltext.getItemCacheFile(item);
  if (!file.exists()) { return _404; }
  let { indexedPages, totalPages, indexedChars, totalChars, version } = await Zotero.DB.rowQueryAsync(
    "SELECT indexedPages, totalPages, indexedChars, totalChars, version FROM fulltextItems WHERE itemID=?",
    item.id
  );
  return [200, {...}, JSON.stringify({
    content: await Zotero.File.getContentsAsync(file),
    indexedPages: indexedPages ?? undefined, totalPages: totalPages ?? undefined,
    indexedChars: indexedChars ?? undefined, totalChars: totalChars ?? undefined,
  }, null, 4)];
  ```

  [`chrome/content/zotero/xpcom/server/server_localAPI.js:1423-1452`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/server/server_localAPI.js#L1423-L1452)
  (Other internal code paths, e.g. the idle-gated `processAttachmentIndexQueue()` backfill (Q6), *do*
  lazily re-extract via `indexItems()` if the cache file is missing but the source file is present — see
  [`fulltext.js:1572-1596`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L1572-L1596)
  — but that's a different call path from the `/fulltext` GET endpoint itself, which just 404s.)

## Q6: Indexing triggers/limits

**Triggered on import, with a short debounce; a background queue also catches anything missed; hard
limits are `pdfMaxPages` (100) and `textMaxLength` (500,000 chars), both preferences.**

- **On import**: `Zotero.Attachments` calls `Zotero.FullText.queueItem(attachmentItem)` right after
  creating a stored-file attachment (three call sites, e.g. after moving the file into the
  attachment's storage directory).
  [`chrome/content/zotero/xpcom/attachments.js:733`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/attachments.js#L733)
  (also lines 957 and 1141 in the same file).
- **`queueItem()` debounces**: pushes the itemID onto an in-memory queue and schedules
  `_processNextItem()` after `_indexDelay = 5000` ms; each subsequent item in the queue is drained
  `_indexInterval = 500` ms apart, one at a time (`_indexing` guard prevents overlap):
  [`chrome/content/zotero/xpcom/fulltext.js:870-916`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L870-L916)
  So indexing is lazy-but-prompt on import (~5s after add, not instantaneous, and explicitly not
  triggered by "first search" — nothing in the search path calls `indexItems()` for an unindexed
  item other than the lazy-re-extract fallback noted in Q5).
- **A separate background "backfill" queue** exists for items that have a stored file but no
  `fulltextItems` row yet (e.g. after an upgrade, or content synced from another machine without its
  extracted text) — driven by an OS idle observer
  (`nsIUserIdleService`, `_idleObserverDelay = 30` seconds, declared `:68`) rather than on-demand:
  [`chrome/content/zotero/xpcom/fulltext.js:1139-1154`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L1139-L1154)
  and the queue-selection query itself:
  [`chrome/content/zotero/xpcom/fulltext.js:1429-1446`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L1429-L1446)
- **Preferences confirmed in source** (not just guessed from the task brief):
  - `extensions.zotero.fulltext.pdfMaxPages` — default **100** pages per PDF.
    [`defaults/preferences/zotero.js:114`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/defaults/preferences/zotero.js#L114)
    Setting it to `0` disables PDF indexing entirely (`indexPDF()` returns `false` immediately).
    [`fulltext.js:624-627`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L624-L627)
  - `extensions.zotero.fulltext.textMaxLength` — default **500,000** characters, applies to
    HTML/EPUB/plain-text. Setting to `0` disables indexing for those types.
    [`defaults/preferences/zotero.js:113`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/defaults/preferences/zotero.js#L113),
    [`fulltext.js:591-594`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L591-L594)
  - Both preferences are observed live — changing either triggers `scheduleReindex()` for affected
    items: `Zotero.Prefs.registerObserver('fulltext.textMaxLength', ...)` /
    `registerObserver('fulltext.pdfMaxPages', ...)`.
    [`fulltext.js:357-361`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L357-L361)
  - **Docs UI only exposes `textMaxLength`** ("Maximum characters to index per file", default
    500,000, "~100,000 words or 180-200 pages") — `pdfMaxPages` is not mentioned on the
    `/support/preferences/search` page at all; it's a hidden/advanced preference only visible in
    source or `about:config`-style preference inspection.
    [zotero.org/support/preferences/search](https://www.zotero.org/support/preferences/search)
    (page text, retrieved 2026-08-24)
  - No file-size limit for PDFs was found in `fulltext.js`'s `indexPDF()` or in
    `document-worker`'s `getFulltext()` itself. `PDFWorker.getFullText()` (client-side manager) reads
    the whole file straight into memory with `IOUtils.read(path)` and no preceding `IOUtils.stat`
    size check at all.
    [`chrome/content/zotero/xpcom/pdfWorker/manager.js:612-640`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/pdfWorker/manager.js#L612-L640)
    A ~2 GiB file-size cap (`Math.pow(2, 31) - 1` bytes = 2,147,483,647, i.e. ~2 GiB, not 4 GB) does
    exist elsewhere in the same manager, guarded by an explicit `IOUtils.stat` check — but only on
    the `import()`/Citavi/Mendeley annotation-import paths (three call sites), not on `getFullText()`.
    [`chrome/content/zotero/xpcom/pdfWorker/manager.js:331-334,394-395,423-424`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/pdfWorker/manager.js#L331-L334)
    So: no cap applies to full-text extraction specifically — the practical limit is whatever fits in
    memory, not a coded threshold.)
  - "Rebuild Index" / "Reindex Item" are documented user-triggered re-index actions, separate from
    the automatic on-import/backfill triggers above.
    [zotero.org/support/preferences/search](https://www.zotero.org/support/preferences/search)

## Built-in vs plugin PDF-to-text/Markdown capabilities

Four third-party Zotero plugins that do PDF→text/Markdown conversion beyond what Q1-Q6 above
describe. Each subsection cites the plugin's own repo (README + source), pinned to the commit read;
the underlying engines (MinerU, Docling) are cited separately where the plugin repo alone doesn't
answer a question. All four plugins attach their output as a normal Zotero child item (attachment or
note) rather than replacing `.zotero-ft-cache` or writing to `fulltextItems`/`fulltext.sqlite`
directly — whether that output then gets indexed by Zotero's *own* built-in mechanism (Q1-Q6 above)
depends on what content type the new item has, checked per-plugin below.

### zotero-pdf2md

`github.com/qingpy/zotero-pdf2md` @
[`e78c505`](https://github.com/qingpy/zotero-pdf2md/commit/e78c50580e2118a59de0986d93078871d499d701)
(branch `master`).

- **Engine**: [MinerU](https://github.com/opendatalab/MinerU), called over HTTP — not local. README:
  "Conversion is performed by MinerU" and "PDFs are uploaded to mineru.net for conversion."
  [`README.md`](https://github.com/qingpy/zotero-pdf2md/blob/e78c50580e2118a59de0986d93078871d499d701/README.md)
- **Local vs cloud**: cloud-only as documented. `API_BASE: "https://mineru.net/api/v4"`, hardcoded.
  [`addon/zotero-pdf2md.js:17`](https://github.com/qingpy/zotero-pdf2md/blob/e78c50580e2118a59de0986d93078871d499d701/addon/zotero-pdf2md.js#L17)
  Two modes: with a free API token (≤200 MB/≤200 pages/PDF, 1,000 high-priority pages/day) or,
  without one, MinerU's unauthenticated "light API" (≤10 MB, ≤20 pages, IP rate-limited). No
  self-hosted/offline option is documented in this plugin (MinerU itself supports offline deployment
  — see zotero-mineru section below — but zotero-pdf2md's `API_BASE` is not configurable).
- **OCR**: explicit toggle, sent to MinerU's API as `is_ocr`, alongside `enable_formula` and
  `enable_table`, on both request paths this plugin has: the token-authenticated flow (`:454-465`)
  and the unauthenticated "light API" flow (`:541-543`).
  [`addon/zotero-pdf2md.js:454-465,541-543`](https://github.com/qingpy/zotero-pdf2md/blob/e78c50580e2118a59de0986d93078871d499d701/addon/zotero-pdf2md.js#L454-L465)
  Whether MinerU's cloud API actually runs OCR when `is_ocr` is unset, versus auto-detecting scanned
  pages as MinerU's own engine README claims (see zotero-mineru section), is **unconfirmed** from
  this plugin's repo — the plugin just forwards the flag.
- **Structure preservation**: table/formula recognition are explicit settings ("OCR/formula/table
  recognition" in Settings), backed by MinerU's own layout+table+formula pipeline (see engine notes
  below). Output is Markdown text; embedded images are **not** downloaded — README lists this as a
  known limitation ("image links inside the `.md` are not downloaded").
  [`README.md`](https://github.com/qingpy/zotero-pdf2md/blob/e78c50580e2118a59de0986d93078871d499d701/README.md)
- **Output location**: `<pdf name>.md`, imported as a child attachment of the PDF's parent via
  `Zotero.Attachments.importFromFile({ contentType: "text/markdown", ... })`.
  [`addon/zotero-pdf2md.js:660-675`](https://github.com/qingpy/zotero-pdf2md/blob/e78c50580e2118a59de0986d93078871d499d701/addon/zotero-pdf2md.js#L660-L675)
- **Feeds Zotero's own index?** Indirectly, yes, but as a *separate* index entry, not merged into the
  PDF's own `.zotero-ft-cache`/FTS5 entry. `text/markdown` matches Zotero's generic
  `Zotero.MIME.isTextType()` check (`mimeType.substr(0, 5) == 'text/' || mimeType in _textTypes`)
  [`chrome/content/zotero/xpcom/mime.js:136-137`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/mime.js#L136-L137)
  so a stored `.md` child attachment goes through the same import-triggered `queueItem()` →
  `indexItem()` path as any other text attachment
  ([`fulltext.js:777-860`](https://github.com/zotero/zotero/blob/753dbf557ad4fbd958594253c9ff28e585d7837c/chrome/content/zotero/xpcom/fulltext.js#L777-L860),
  trigger confirmed in Q6 above) — it gets its own `indexedChars`/`totalChars` row and FTS5 entry,
  searchable, but the raw Markdown syntax (headings, table pipes, etc.) is indexed verbatim, not the
  PDF's own text-layer extraction.
- **Maturity**: created 2026-06-03, single push the same window (last push 2026-06-04), one release
  (`v1.0.0`), 7 stars, 0 open issues. Reads as a small, effectively single-release/experimental
  project — no evidence of ongoing maintenance activity beyond the initial release.
  [repo metadata, retrieved 2026-08-24]
- **Cost/dependencies**: no local dependency (pure HTTP client from Zotero) but requires a MinerU
  account/API token for anything beyond the light-API's 10 MB/20-page cap; PDFs leave the user's
  machine.

### zotero-mineru

`github.com/lisontowind/zotero-mineru` @
[`4bde508`](https://github.com/lisontowind/zotero-mineru/commit/4bde508bd63d2d03542e0e3ad7baaba99656e9c3)
(branch `main`).

- **Engine**: MinerU API, same underlying engine as zotero-pdf2md, plus an optional separate LLM call
  (user-configured OpenAI-compatible endpoint) for AI summary/translation on top of the parsed
  Markdown. README: "sends PDF attachments to the MinerU API, saves parsed results back to Zotero as
  Markdown attachments, and supports AI summary and AI translation workflows."
  [`README.md`](https://github.com/lisontowind/zotero-mineru/blob/4bde508bd63d2d03542e0e3ad7baaba99656e9c3/README.md)
- **Local vs cloud**: cloud by default (`apiBaseURL` defaults to `"https://mineru.net/api/v4"`) but,
  unlike zotero-pdf2md, this URL is a user-editable preference, not hardcoded.
  [`mineru.js:245-248`](https://github.com/lisontowind/zotero-mineru/blob/4bde508bd63d2d03542e0e3ad7baaba99656e9c3/mineru.js#L245-L248)
  Whether pointing it at a self-hosted MinerU FastAPI server (which MinerU's own repo supports, see
  below) actually works end-to-end is **unconfirmed** — the README only documents the mineru.net
  token flow, and doesn't mention self-hosting. AI summary/translation additionally require a
  separate user-supplied LLM API key. \[`README.md`, "Requirements"/"Configure" sections\]
- **OCR**: only a `model_version` (`pipeline`/`vlm`) preference is sent to MinerU; **no `is_ocr` flag
  was found** in this plugin's source (contrast with zotero-pdf2md, which does send one).
  [`mineru.js:267-281,573`](https://github.com/lisontowind/zotero-mineru/blob/4bde508bd63d2d03542e0e3ad7baaba99656e9c3/mineru.js#L267-L281)
  Whether the mineru.net API OCRs scanned pages by default without an explicit flag is a question
  about MinerU's *API* behavior, not this plugin's code — MinerU's own repo claims automatic
  scanned-page detection at the engine level (see below), but this plugin doesn't confirm that
  applies to the hosted API path it calls.
- **Structure preservation**: strongest of the three Markdown plugins on this axis at the
  *presentation* layer — it post-processes MinerU's Markdown output with its own Markdown/HTML table
  parser (renders tables as proper `<table>` HTML for notes) and preserves LaTeX-style formula
  delimiters (`$...$`/`$$...$$`) through summarization and translation.
  [`mineru.js:1131-1720`](https://github.com/lisontowind/zotero-mineru/blob/4bde508bd63d2d03542e0e3ad7baaba99656e9c3/mineru.js#L1131-L1720)
  (table parsing),
  [`mineru.js:3245-3246`](https://github.com/lisontowind/zotero-mineru/blob/4bde508bd63d2d03542e0e3ad7baaba99656e9c3/mineru.js#L3245-L3246)
  (formula preservation instruction to the translation LLM). Images are preserved and kept under the
  parsed attachment's `images/` directory (not stripped, unlike pdf2md).
  \[`README.md`, "Features"\]
- **Output location**: parsed Markdown → child attachment (`contentType: "text/markdown"`, tagged
  `#MinerU-Parse`); AI summary → child note (tagged `#MinerU-Summary`); AI translation → another
  Markdown child attachment (tagged `#MinerU-Translation`).
  [`mineru.js:2130-2134,3308-3312`](https://github.com/lisontowind/zotero-mineru/blob/4bde508bd63d2d03542e0e3ad7baaba99656e9c3/mineru.js#L2130-L2134)
  and README "Behavior Notes".
- **Feeds Zotero's own index?** Same mechanism as zotero-pdf2md for the Markdown attachments (yes, as
  a separate `text/markdown` index entry via `isTextType()` — see that section for the citation
  chain). The AI-summary note additionally lands in Zotero's separate `fulltextNotes`/`fulltextNotesCJK`
  FTS5 tables (see built-in doc, Q5) since Zotero indexes all note content by default.
- **Maturity**: created 2026-02-28, actively maintained — 14 releases from `v0.1.38` through
  `v0.1.58`, most recent push 2026-08-13, 17 stars, 5 open issues, 1 fork. Clearly the most
  actively-iterated of the three Markdown-conversion plugins by commit/release cadence.
  [repo metadata, retrieved 2026-08-24]
- **Cost/dependencies**: MinerU API token (same tiers as pdf2md) plus, only if summary/translation
  features are used, a separate LLM API key/endpoint the user supplies.

### zotero-docling

`github.com/max3925vats/zotero-docling` @
[`5ef7c76`](https://github.com/max3925vats/zotero-docling/commit/5ef7c769627f15a8e157382fa94a8a3ba070233a)
(branch `main`).

- **Engine**: [Docling](https://github.com/docling-project/docling), via its companion HTTP server
  [`docling-serve`](https://github.com/docling-project/docling-serve) — never called as an in-process
  library. README: "converts PDF attachments to structured Markdown using the Docling
  document-understanding pipeline" and "a small local server (docling-serve) does the actual
  PDF → Markdown conversion, and this plugin connects Zotero to it. You need both."
  [`README.md`](https://github.com/max3925vats/zotero-docling/blob/5ef7c769627f15a8e157382fa94a8a3ba070233a/README.md)
- **Local vs cloud**: local server required, but it's a server the user runs themselves (no
  Zotero-side cloud dependency) — via `uv`/`pipx` Python install or a Docker/Podman container
  (CPU or CUDA image), default `http://localhost:5001`. No data leaves the machine unless the user
  points the server URL at a remote host themselves; optional Bearer/Basic/custom-header auth exists
  for that case. First conversion downloads model weights from Hugging Face: 2-10 min for the
  standard pipeline, "significantly longer (multi-GB)" for VLM presets generally, per the README's
  "First conversion" note — a separate Requirements-section estimate puts the baseline Granite-Docling
  VLM weights specifically at ≈500 MB ("larger models more").
  \[`README.md`, "Requirements" / "First conversion downloads model weights"\]
- **OCR**: full OCR + language selection exposed from Docling's own options ("Full Docling options
  surfaced: pipeline (standard / VLM), OCR + language, table mode, formula / code / chart / picture
  enrichments"). \[`README.md`, "Features"\]
  Docling's actual OCR engine is **not fixed to Tesseract** (contrast with zotero-ocr below) — its
  default is an auto-selecting engine that tries backends in order: `ocrmac` (Apple Vision, macOS
  only), then Nemotron-OCR if installed, then RapidOCR (onnxruntime), then EasyOCR, with a final
  RapidOCR-with-`torch`-backend attempt if all of those are unavailable; Tesseract is available as an
  explicit, separately-selectable engine option rather than the default.
  [`docling/models/stages/ocr/auto_ocr_model.py`](https://github.com/docling-project/docling/blob/83d5de095cb30846a0df5336117b6213f2c5b335/docling/models/stages/ocr/auto_ocr_model.py)
  (engine-selection `if`/`try` chain),
  [`docling/datamodel/pipeline_options.py:1996-2004`](https://github.com/docling-project/docling/blob/83d5de095cb30846a0df5336117b6213f2c5b335/docling/datamodel/pipeline_options.py#L1996-L2004)
  (`ocr_options` defaults to `OcrAutoOptions()`). Which specific engine `zotero-docling`'s
  "OCR + language" preference selects, versus leaving Docling's auto-selection in place, is
  **unconfirmed** from the plugin repo alone — it exposes whatever `docling-serve` accepts via its
  "Advanced JSON escape hatch" rather than hardcoding an engine choice.
- **Structure preservation**: the most structure-aware of the three Markdown plugins by README claim
  — "table mode, formula / code / chart / picture enrichments" are all surfaced as first-class
  options, plus per-item retroactive image handling (**Exclude images** at conversion time, or
  **Remove images from markdown** after the fact, both swap embedded base64 figures for a
  `<!-- image -->` placeholder to control file size). \[`README.md`, "Features"\]
- **Output location**: `.md` sibling child attachment next to the PDF,
  `Zotero.Attachments.importFromFile({ contentType: "text/markdown", ... })`.
  [`src/modules/convert.ts:732-735`](https://github.com/max3925vats/zotero-docling/blob/5ef7c769627f15a8e157382fa94a8a3ba070233a/src/modules/convert.ts#L732-L735)
  Per-parent status tags (`docling/done`, `docling/incomplete`, `docling/error`) track conversion
  state. \[`README.md`, "Features"\]
- **Feeds Zotero's own index?** Same mechanism as zotero-pdf2md/zotero-mineru — `text/markdown`
  content type triggers Zotero's generic text-indexing path as a separate index entry from the PDF's
  own extraction (see zotero-pdf2md section for the citation chain).
- **Maturity**: created 2026-05-19, actively maintained (most recent push 2026-08-20, 8 release tags
  — 7 semver (`v0.1.0`→`v0.3.3`) plus one plain `release` tag — CI workflow, dependabot/renovate
  configured, issue templates, test suite present
  under `test/`), 11 stars, 6 open issues, 3 forks. The most process-mature of the Markdown plugins by
  repo-hygiene signals (tests, CI, structured issue templates) even though it has fewer stars than
  zotero-mineru. [repo metadata, retrieved 2026-08-24]
- **Cost/dependencies**: no per-conversion API cost or account, but requires the user to install and
  run `docling-serve` (Python via `uv`/`pipx`, or a Docker/Podman image; CUDA image available for GPU
  acceleration) and has real local resource cost — first-run multi-GB model downloads for VLM
  presets, and enough RAM/disk to hold model weights. AGPL-3.0-or-later license (copyleft; the README
  flags this explicitly for anyone forking/redistributing).
  \[`README.md`, "License"; repo metadata `licenseInfo`\]

### zotero-ocr

`github.com/UB-Mannheim/zotero-ocr` @
[`cdd286a`](https://github.com/UB-Mannheim/zotero-ocr/commit/cdd286a469e13830f704e2dc037a33367a1551b2)
(branch `master`).

- **Engine**: real OCR, confirmed — [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for
  text recognition, plus Poppler's `pdftoppm` to rasterize PDF pages to images first. README:
  "Tesseract OCR is used for the text recognition itself," listed under "Prerequisites" alongside
  `pdftoppm`. [`README.md`](https://github.com/UB-Mannheim/zotero-ocr/blob/cdd286a469e13830f704e2dc037a33367a1551b2/README.md)
  Both are local binaries the user installs and points the plugin at (paths configurable in
  preferences; empty by default, meaning — per the README — "the usual locations are looked at").
- **Local vs cloud**: fully local/offline. No API, no server, no account — the plugin only shells out
  to the two local binaries. Explicitly incompatible with Flatpak/Snap/AppImage Zotero installs
  because those sandboxes block access to external binaries.
  \[`README.md`, "Prerequisites"\]
- **OCR (scanned/image-only PDFs)**: this plugin's entire purpose, and the one of the four that
  actually adds real OCR rather than delegating to a third-party layout-parsing service. User-facing
  controls: DPI (default 300), Tesseract Page Segmentation Mode (default `3`), and OCR
  language/script (default `eng`, any installed Tesseract model).
  [`src/defaults/preferences/defaults.js`](https://github.com/UB-Mannheim/zotero-ocr/blob/cdd286a469e13830f704e2dc037a33367a1551b2/src/defaults/preferences/defaults.js)
- **Structure preservation**: none beyond what Tesseract's PSM gives you — this plugin recognizes
  characters, not document structure. No table/formula/heading/figure extraction; output is a
  text layer (in the new PDF) or a flat text/HTML dump (note/hOCR), not Markdown.
- **Output location** (all three below are separate, independently-toggleable outputs, all on by
  default): (1) a **new sibling PDF** with the recognized text embedded as a real text layer,
  titled `<original>.ocr`, imported via `Zotero.Attachments.importFromFile()` with no explicit
  `contentType` (so Zotero infers `application/pdf` from the `.pdf` extension) — `outputPDF: true`,
  `overwritePDF: false` by default, i.e. it doesn't replace the original by default; (2) a **child
  note** containing the recognized plain text (`outputNote: true`); (3) **hOCR HTML attachments**,
  one per page, capped at the first 5 pages by default (`outputHocr: true`,
  `maximumPagesAsHtml: "5"`, hOCR-to-HTML attachment import at `:437`), useful for visually verifying
  OCR quality; the sibling-PDF import is a separate block further down (`:461-466`, see below).
  [`src/defaults/preferences/defaults.js`](https://github.com/UB-Mannheim/zotero-ocr/blob/cdd286a469e13830f704e2dc037a33367a1551b2/src/defaults/preferences/defaults.js),
  [`src/chrome/content/zoteroocr.js:403-466`](https://github.com/UB-Mannheim/zotero-ocr/blob/cdd286a469e13830f704e2dc037a33367a1551b2/src/chrome/content/zoteroocr.js#L403-L466)
- **Feeds Zotero's own index?** Yes, and uniquely among the four plugins, **directly into the same
  built-in PDF pipeline** described in Q1-Q6 above, not a separate text-type side channel: the new
  `.ocr.pdf` is a normal stored `application/pdf` attachment, created via the same
  `Zotero.Attachments.importFromFile()` call path that any imported PDF uses, which fires the
  standard on-import `queueItem()` trigger (three call sites in `zotero/zotero`'s
  `attachments.js`, cited in Q6) → Zotero's own PDF.js-based `getFullText()` extraction — meaning
  Zotero re-indexes this attachment itself and now finds real text, because Tesseract put a genuine
  text layer in the PDF. (This claim is scoped to the default "attach as copy" path,
  `outputAsCopyAttachment: true`; the alternate `Zotero.Attachments.linkFromFile()` path for linked,
  non-copied files was not checked against the `queueItem()` trigger conditions.) The child note is
  separately indexed via Zotero's `fulltextNotes`/`fulltextNotesCJK` FTS5 tables (built-in doc, Q5),
  since Zotero indexes all notes by default.
  [`src/chrome/content/zoteroocr.js:461-466`](https://github.com/UB-Mannheim/zotero-ocr/blob/cdd286a469e13830f704e2dc037a33367a1551b2/src/chrome/content/zoteroocr.js#L461-L466)
- **Maturity**: by far the most established of the four — created 2018-10-25, 814 stars, 52 forks,
  20 tagged releases from `0.0.1` (2019-08-28) to `0.9.5.1` (2026-05-04), most recent push
  2026-08-20, 11 open issues. Actively maintained across seven-plus years, with a third-party AUR
  package for Arch Linux. \[repo metadata, retrieved 2026-08-24; `README.md`, "Prerequisites"\]
- **Cost/dependencies**: no account/API cost; requires local installation of Tesseract OCR and
  Poppler's `pdftoppm`, and (per the README) a non-sandboxed Zotero install (Flatpak/Snap/AppImage
  unsupported).

### Comparison table

| capability                       | built-in                                                       | pdf2md                                                                                            | mineru                                                                                                                                                                     | docling                                                                                                                               | zotero-ocr                                                                                                                              |
| -------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| engine                           | Zotero's PDF.js fork (`document-worker`), text-layer read only | MinerU (cloud API)                                                                                | MinerU (cloud API, configurable base URL)                                                                                                                                  | Docling, via local `docling-serve` (OCR engine auto-selected: ocrmac/Nemotron/RapidOCR/EasyOCR/RapidOCR-torch, or explicit Tesseract) | Tesseract OCR + Poppler `pdftoppm` (both local binaries)                                                                                |
| local vs cloud/server dependency | fully local (in-process)                                       | cloud (mineru.net); no self-host documented                                                       | cloud by default (mineru.net); base URL configurable, self-host undocumented                                                                                               | local server required (`docling-serve`, self-run)                                                                                     | fully local, no server/API                                                                                                              |
| OCR support                      | none (Q2)                                                      | yes — explicit `is_ocr` flag to MinerU API                                                        | model_version only; no explicit OCR flag found in plugin source; MinerU engine claims auto-detection of scanned pages (unconfirmed whether the hosted API applies it here) | yes — full OCR + language options surfaced from Docling                                                                               | yes — this is the plugin's entire purpose                                                                                               |
| structure: tables                | no                                                             | yes, via MinerU `enable_table` (→ HTML tables)                                                    | yes, plus its own Markdown/HTML table renderer for notes                                                                                                                   | yes, Docling "table mode" option                                                                                                      | no                                                                                                                                      |
| structure: headings              | no (plain text only)                                           | yes (Markdown output)                                                                             | yes (Markdown output)                                                                                                                                                      | yes (Markdown output)                                                                                                                 | no                                                                                                                                      |
| structure: formulas              | no                                                             | yes, via MinerU `enable_formula` (→ LaTeX)                                                        | yes, LaTeX delimiters preserved through summary/translation                                                                                                                | yes, Docling formula enrichment option                                                                                                | no                                                                                                                                      |
| structure: figures/images        | no                                                             | markdown links only; images not downloaded                                                        | preserved, saved under attachment's `images/`                                                                                                                              | preserved (base64-embedded), opt-out/strip tooling provided                                                                           | n/a (OCR, not conversion)                                                                                                               |
| output location                  | `.zotero-ft-cache` file, served by `GET /fulltext`             | `.md` child attachment (`text/markdown`)                                                          | `.md` child attachment; AI summary as child note; AI translation as another `.md` child attachment                                                                         | `.md` sibling child attachment (`text/markdown`)                                                                                      | new `.ocr.pdf` sibling attachment + child note + per-page hOCR HTML attachments                                                         |
| feeds Zotero's own search index  | yes (is the index)                                             | yes, but as a separate `text/markdown` entry (raw MD syntax indexed, not merged with PDF's entry) | yes, same as pdf2md for `.md` attachments; AI-summary note indexed via `fulltextNotes`                                                                                     | yes, same mechanism as pdf2md                                                                                                         | yes, and uniquely re-enters the *same* built-in PDF pipeline (new PDF now has a real text layer); note also indexed via `fulltextNotes` |

### Which gap each plugin closes

The built-in system's two gaps are **no OCR** (Q2) and **plain text only** (Q1) — no
tables/headings/formulas/figures. **zotero-ocr** is the only one that closes the OCR gap *inside*
Zotero's native index (its output PDF re-enters the same PDF.js pipeline from Q1-Q6); the three
Markdown plugins close the structure gap, but always as a *parallel* `.md` artifact with its own
separate index entry, never merged into the source PDF's own extraction.

For a scanned source PDF specifically: pdf2md and docling both run OCR as part of the same
conversion, so they close *both* gaps in one pass; whether zotero-mineru's hosted API does too is
unconfirmed (see its OCR row above). Locality is the other axis of the tradeoff: the two
MinerU-based plugins send PDF content to mineru.net by default, while docling and zotero-ocr stay
fully local — docling at the cost of running and maintaining a `docling-serve` process with real
compute/storage requirements of its own.
