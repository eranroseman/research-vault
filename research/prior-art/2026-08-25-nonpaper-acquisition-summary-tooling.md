# Non-paper acquisition and summary tooling

Research note, 2026-08-25, for issue #36. Scope: web pages, product documentation, and software repositories. Primary sources only.

## Verdict

Keep **Zotero as the human admission gate and the citation-identity registry**. Its Connector already creates Web Page items and snapshots, and Zotero has both Webpage and Software item types; nothing reviewed supports creating a second citation identity system ([Zotero: adding items](https://www.zotero.org/support/adding_items_to_zotero), [item types](https://www.zotero.org/support/kb/item_types_and_fields)). Zotero object versions synchronize *library metadata*; they do not version the bytes served by a site or a repository tree ([Zotero API syncing](https://www.zotero.org/support/dev/web_api/v3/syncing)).

Add a source-class adapter layer before/alongside admission:

1. preserve an immutable raw capture and its source-native version;
2. derive normalized, model-ready full text with explicit lineage;
3. summarize only an admitted, complete, bounded source;
4. reuse an identical prior response through a real cache.

Integrate mature capture and extraction tools. Build only the thin dispatcher, provenance manifest, quality gates, and cache/staleness glue. Fixity values and archive locators are evidence about a Zotero item, not competing identities.

## Stage and source-class decision matrix

| Stage     | Web page                                                                                                  | Product documentation                                                                                                     | Software repository                                                                                                  | Decision/control                                                      |
| --------- | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Discover  | URL supplied by the researcher; Connector metadata when a translator exists                               | Prefer the publisher's canonical docs URL and locate its source repository/version selector                               | Canonical origin URL plus requested ref                                                                              | Discovery does not admit or summarize                                 |
| Admit     | Human saves a Zotero Web Page item; keep snapshot as convenience                                          | Human saves the citable docs page/release                                                                                 | Human creates/saves a Zotero Software item                                                                           | Citekey remains the only cross-layer identity                         |
| Acquire   | Static: conditional HTTP retrieval. Dynamic, interactive, or multi-page: pinned Browsertrix crawl to WACZ | Prefer upstream Markdown/docs repository at an exact commit or release; otherwise capture rendered pages with Browsertrix | Clone exact commit; preserve a full bundle/mirror; fetch submodules and LFS objects when part of the asserted source | Never normalize in place of preserving raw input                      |
| Version   | Hash response bytes; retain final URL, headers, retrieval time, and capture config                        | Record docs release/tag/commit and raw hash; hash publisher Markdown separately                                           | Commit ID plus bundle hash; request a Software Heritage archive/SWHID for public code                                | Source-native version + artifact hash, both linked to the Zotero item |
| Normalize | Defuddle from captured local HTML/DOM; Trafilatura only as fallback/comparison                            | Native Markdown unchanged where available; otherwise Defuddle                                                             | Plain checked-out files or an uncompressed, explicitly scoped Repomix pack                                           | Normalized text is a lossy derivative with its own hash               |
| Validate  | Replay/QA capture; inspect code, tables, images, footnotes, hidden panels                                 | Compare navigation inventory and version banner against capture                                                           | Verify commit, file inventory, submodule/LFS completeness, and pack exclusions                                       | Failed validation blocks summary, not admission                       |
| Summarize | Exact normalized full text only                                                                           | Exact complete bounded document/release only                                                                              | Exact complete bounded tree/package only                                                                             | Isolated single-turn call; cache by all semantic inputs               |

### Why these defaults

**Web capture.** Browsertrix is a browser-based crawler that emits WACZ and supports crawl bounds, behaviors, and text extraction; its QA mode compares the live crawl with replay using screenshots, text, and resource counts ([crawler guide](https://crawler.docs.browsertrix.com/user-guide/), [QA guide](https://crawler.docs.browsertrix.com/user-guide/qa/)). WARC 1.1 records request/response metadata, dates, record IDs, and block/payload digests ([IIPC WARC 1.1](https://iipc.github.io/warc-specifications/specifications/warc-format/warc-1.1-annotated/)). WACZ packages WARC, indexes, page metadata, and SHA-256 resource fixity for portable replay, but WACZ 1.2 is explicitly a draft rather than a standards-body publication ([WACZ 1.2 draft](https://specs.webrecorder.net/wacz/1.2.0/)).

Use HTTP validators only to avoid needless transfer. RFC 9110 distinguishes strong and weak validators; weak ETags and most `Last-Modified` values do not prove byte equality ([RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html)). `curl --etag-compare/--etag-save` can drive conditional requests, but a successful body retrieval still needs a local content hash ([curl manual](https://curl.se/docs/manpage.html)).

**Extraction.** Defuddle converts HTML to cleaned Markdown/JSON, preserves common structures, exposes removal/debug information, and accepts an explicit content selector ([Defuddle documentation](https://defuddle.md/docs)). It is nevertheless heuristic and lossy: run it against the captured local artifact, pin its version and options, disable asynchronous third-party fallback, and retain raw input. Trafilatura offers precision/recall controls and Markdown, JSON, XML, and TEI outputs, but its documented options change which links, images, tables, and formatting survive; use it as an independent fallback, not a second lossy transform chained after Defuddle ([Trafilatura repository](https://github.com/adbar/trafilatura), [usage documentation](https://trafilatura.readthedocs.io/en/latest/usage-python.html)).

For publisher-supplied `/llms.txt` or Markdown, treat the file as a useful discovery map or derivative, not proof of the rendered site. The authors call `llms.txt` a proposal and describe a curated Markdown overview with links to Markdown resources ([llms.txt proposal](https://llmstxt.org/)). Prefer the versioned docs repository when available.

**Repositories.** Git is content-addressed, and exact commit links are stable while branch links move ([Git objects](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects), [GitHub permanent links](https://docs.github.com/en/repositories/working-with-files/using-files/getting-permanent-links-to-files)). A full `git bundle` can carry objects and refs offline; a mirror carries all refs, but mirror cloning has no checkout and ignores recursive-submodule checkout ([git-bundle](https://git-scm.com/docs/git-bundle), [git-clone](https://git-scm.com/docs/git-clone)). Git LFS leaves pointer files in Git, so capture referenced LFS objects explicitly ([GitHub LFS documentation](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage)).

For public repositories, integrate Software Heritage's Save Code Now and record the resulting SWHID when available. SWHIDs identify content, directories, revisions, releases, and snapshots with intrinsic hashes and optional origin/path/line qualifiers; they complement, rather than replace, Zotero identity ([SWHID specification](https://docs.softwareheritage.org/devel/swh-model/persistent-identifiers.html), [Save Code Now API](https://docs.softwareheritage.org/_modules/swh/web/save_code_now/api_views.html)).

Repomix is useful only after Git capture: it packages selected files into AI-oriented XML/Markdown/JSON/plain output, honors ignore/default patterns, may omit oversized files, and can intentionally compress away implementation details ([Repomix README](https://github.com/yamadashy/repomix/blob/main/README.md?plain=1)). Therefore hash its output and record exact version/config/file inventory; never treat a Repomix pack as the archival repository or call a compressed pack “full text.”

## Raw-versus-derived provenance contract

Store one machine-readable manifest per admitted source version.

### Raw capture record

- Zotero citekey and an integration locator for its Zotero object; the citekey is the identity.
- Canonical origin and final retrieval URL, retrieval timestamp, and declared capture scope.
- Exact acquisition tool version, configuration, seeds/ref, and authentication mode.
- Raw artifact path/media type, byte length, SHA-256, and source-native version (`ETag` as hint, docs tag/commit, Git commit, or SWHID).
- For WACZ: manifest/resource fixity and QA result. A signed WACZ can authenticate the package creator and timestamp, not prove that the origin server served the content ([WACZ signing specification](https://specs.webrecorder.net/wacz-auth/0.1.0/)).

### Normalized full-text record

- Parent raw SHA-256; extractor name/version/options and any include/exclude selector.
- Output path/media type, SHA-256, byte/token counts, and extraction warnings/removal report.
- Validation result and reviewer, including an explicit statement of the bounded corpus.
- Never overwrite raw capture; a changed extractor produces a new derivative.

### Summary record

- Parent SHA-256 of the *exact complete full-text artifact passed to the model*.
- First line exactly `[summary-of:: <fixity-prefix>]`; mismatch means stale.
- Template/instruction hash, requested model, provider-resolved model ID, decoding/options/schema, generation time, output hash, token usage/cost, and log reference.
- Cache key over full-text hash + template hash + a pinned model identifier + all response-affecting options. Record the provider-resolved model ID too; reject mutable aliases from reproducible cache entries. An intentional regeneration must bypass the cache explicitly.

The `llm` CLI can supply pinned templates, model/options/schema capture, prompt/response logs, token usage, and SHA-256-addressed fragments ([templates](https://llm.datasette.io/en/stable/templates.html), [logging](https://llm.datasette.io/en/stable/logging.html), [fragments](https://llm.datasette.io/en/stable/fragments.html)). **Those logs and content-addressed fragments are not a response cache:** repeating a command still calls a model. Persist the composite key and prior output in repo-owned state, and return the saved output without a model call on a hit. LlamaIndex demonstrates transformation caching keyed by node content and transformation configuration, but adopting its ingestion/RAG framework for this one operation would exceed the repo's needs ([pipeline source](https://github.com/run-llama/llama_index/blob/main/llama-index-core/llama_index/core/ingestion/pipeline.py)).

## Required summary doctrine

- Generate only from full text, never an abstract, search snippet, navigation index, compressed Repomix skeleton, or partial crawl.
- Use one isolated turn containing only the bounded source text and the instruction/template; never summarize midway through a conversational session.
- If the bounded source cannot be completely retrieved, emit `no full text available`. If complete text exists but does not fit the selected model's input contract, do not summarize: select a capable model or narrow the citable source with human approval. Do not silently map-reduce summaries of fragments.
- Run summaries after admission by default, so rejected candidates incur no model cost.
- If raw bytes change but re-extraction yields identical normalized full text, retain the new raw provenance without regenerating the summary. If normalized fixity or any cache-key input changes, mark stale and regenerate once.

## Failure modes and gates

| Failure                                                                             | Consequence                                            | Gate/mitigation                                                                                                                                                                                                              |
| ----------------------------------------------------------------------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| JS, lazy loading, tabs, consent walls, or crawl timeouts hide content               | Incomplete “full text”                                 | Browsertrix behaviors plus explicit crawl bounds; replay QA; block summary on failed scope check ([behaviors](https://crawler.docs.browsertrix.com/user-guide/behaviors/))                                                   |
| Readability heuristic drops code, tables, notes, or images                          | Confident summary of a mutilated derivative            | Retain raw; inspect fixture features and extraction warnings; compare Trafilatura only on failure                                                                                                                            |
| Authenticated crawl records secrets, cookies, or private content                    | Evidence archive becomes credential/data leak          | Dedicated account, restricted storage, and pre-export inspection; Browsertrix warns Basic-auth credentials are written into the archive ([YAML configuration](https://crawler.docs.browsertrix.com/user-guide/yaml-config/)) |
| WACZ fixity is mistaken for origin authenticity                                     | Tamper-evident capture is overstated as server proof   | State observer/tool/time and trust boundary; never claim cryptographic origin attestation                                                                                                                                    |
| Generic Web Page metadata or Zotero object version is mistaken for source version   | Citation survives while evidence silently changes      | Raw hash + source-native version alongside Zotero registry record                                                                                                                                                            |
| Branch/tag, submodule ref, or LFS pointer is mistaken for complete repository bytes | Irreproducible repository evidence                     | Resolve commit; fetch/verify submodules and LFS; preserve full bundle and inventory                                                                                                                                          |
| Repomix ignore/compression or publisher `llms.txt` is called full text              | Summary omits implementation/details by construction   | Only uncompressed, inventoried pack of a bounded tree qualifies; otherwise use original files                                                                                                                                |
| Logged prompt or fragment hash is mistaken for cached response                      | Unchanged sources spend tokens again and outputs drift | Assert zero provider calls on cache hit; record cache key, response, and usage                                                                                                                                               |

## Integrate versus build

**Integrate now:** Zotero Connector/API; conditional HTTP retrieval; Browsertrix + WARC/WACZ replay/QA; Defuddle with Trafilatura fallback; Git bundle/clone plus Software Heritage; optional uncompressed Repomix packaging; `llm` as the isolated executor and audit log.

**Build now:** a small source-class dispatcher; raw/derived manifest schema; deterministic hashing and version pinning; extraction/corpus gates; Zotero linkage; the composite response cache; `[summary-of::]` staleness check. These are project-policy seams that no reviewed tool owns end to end.

**Do not make default:** SingleFile says professional/academic archiving should prefer WARC and notes that removing scripts can break interactive content ([SingleFile FAQ](https://github.com/gildas-lormeau/SingleFile/blob/master/faq.md)); keep it as a manual convenience. ArchiveBox orchestrates many useful formats, but its documented runtime spans Python, Node, Chrome, wget, curl, Git, media downloaders, Django, and a database—too much operational surface for the thin initial path ([ArchiveBox README](https://github.com/ArchiveBox/ArchiveBox)). Firecrawl returns useful Markdown/HTML/screenshots/JSON and handles browser actions, but its cited contract is a hosted/self-hosted scraping derivative rather than a WARC/WACZ evidence package, and self-hosting adds multiple services ([Firecrawl repository](https://github.com/firecrawl/firecrawl)). Reconsider either when crawl volume, scheduling, or blocked-site handling—not provenance glue—becomes the dominant cost.

## Minimal next experiment

Use three redistributable fixtures: (1) a static page containing code, table, footnote, image, and redirects; (2) a JavaScript docs mini-site with hidden tabs and lazy content; (3) a tagged Git repository with one submodule and one LFS object.

1. Admit each fixture to a test Zotero library and assign a citekey.
2. Capture with the chosen adapter, normalize, and produce the manifest without a model call.
3. Verify raw replay/byte recovery, final URL/ref, feature inventory, submodule/LFS bytes, and reported omissions.
4. Run one isolated summary from the validated complete artifact; verify its marker and full cache provenance.
5. Repeat unchanged and assert **zero provider calls and zero new tokens**.
6. Change only page chrome: raw hash should change; identical normalized text should reuse the summary.
7. Change one substantive sentence/file: normalized hash should change, old summary should be stale, and exactly one new call should occur.

Adopt the path only if all three retain recoverable raw evidence, make every lossy step inspectable, preserve one Zotero identity, and meet the zero-cost unchanged rerun. Otherwise the failing source class stays manual; do not weaken the full-text gate.
