# Zotero and Better BibTeX API reading, 2026-09-04

Disposition: historical (2026-09-06)

**What this is.** A dated reading of Zotero and Better BibTeX documentation and source, taken on 2026-09-04 during the adopt-first sourcing run for the ingest redesign. The bodies read, listed below with their pins, are Zotero and Better BibTeX documentation pages and source files, read against a seven-fact register, Z1 through Z7. They produced 623 fact entries, which deduplicate by quote to 448 distinct facts, each carried below with its verbatim quote and the location it came from. Every quote is reproduced exactly as the run recorded it.

**What this is not.** It is not a maintained fact base. Nothing here was re-read or re-verified after 2026-09-04, and what it describes moves: it reads Better BibTeX at 9.0.63 and Zotero at the 10 line as they stood on that date. The facts the ingest design depends on do not live here. They live in section 9 of `docs/superpowers/specs/2026-09-06-import-redesign-design.md`, each with the method that established it and the date it was established, and each is re-probed rather than read from this file. A reader who needs a current answer runs the probe. This file says what the documentation and the source said on one day, and it is useful for the reasoning and the wording behind a fact, not for the fact's current value.

**Where it came from.** The sourcing run at `docs/research/2026-09-04-import-sourcing.md`. That run carried a Zotero-fact lane alongside its digest and capture lanes, and this register was the lane's output. It was moved out on 2026-09-05 because it is environment documentation rather than a sourcing finding. The register's prose below still speaks from inside the run: where it names a candidate's own section, the capture lane, or the coverage matrix, those resolve in the sourcing note, whose coverage matrix carries one row per body read against Z1 through Z7.

______________________________________________________________________

## The Zotero fact register

The Z lane is not coverage. Its records are documentation pages and source files read for the seven facts the redesign needs established from primary sources. Nine records were read, and between them they produced 623 fact entries. Deduplicated by quote, that is **448 distinct facts**, listed below in full, each with its verbatim quote and the location it came from. Where the same quote was recorded by more than one reader, every reader is named and every record id it was filed under is kept, because the ids carry the readers' own framing.

### The bodies read

| Body                                                                                           | Pin                                                                                                 | Facts before dedup |
| ---------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- | ------------------ |
| Zotero Local API page, with the linked write, full-text, basics, syncing and file-upload pages | Footer "Last updated 2026-07-29"                                                                    | 92                 |
| Zotero 10 for Developers page, with the same linked set                                        | Footer "Last updated 2026-08-20", source commit recorded                                            | 96                 |
| zotero-schema commit 55a1312                                                                   | Commit `55a13120bab31e95d6dc88a82fbfa4bbb60e069c`, authored 2025-12-20                              | 83                 |
| Zotero Web API v3 Write Requests page                                                          | Footer "Last updated 2026-07-29"                                                                    | 71                 |
| Zotero Web API v3 Basics page                                                                  | Footer "Last updated 2026-07-29"                                                                    | 64                 |
| Better BibTeX `content/json-rpc.ts` at v9.0.63                                                 | Read 2026-09-04 at commit `cfdba6ac`; the file carries no modification line                         | 53                 |
| Zotero Web API v3 Full-Text Content page                                                       | Footer "Last updated 2026-07-29"                                                                    | 50                 |
| Better BibTeX documentation, JSON-RPC page, first read                                         | Read 2026-09-04                                                                                     | 43                 |
| Better BibTeX documentation, JSON-RPC page, second read                                        | No modification line on the page, which the reader checked in the body, the footer and the metadata | 37                 |
| Better BibTeX `content/key-manager.ts` at v9.0.63                                              | Read 2026-09-04 at the same commit                                                                  | 34                 |

Two of these are the same page read twice. Both reads are kept, and where they produced the same quote the entry names both.

Six of the nine records carry a verify pass. The two Better BibTeX source-file reads share two passes that confirmed the licence and the pin at that commit and re-checked no coverage rows, and because both passes name the same repository and the same commit, neither can be assigned to one of the two reads rather than the other; this note assigns one to each and says so here rather than leaving the choice silent. The Better BibTeX documentation record has no verify pass. One further bookkeeping defect belongs here and is the subject of the critic's last gap: the Write Requests record has an empty coverage array, and its verifier applied a default-refuted rule to three rows the record never asserted, which is where three of the run's four refutations come from.

### How to read the register

Every entry's quote is verbatim from the body named in its Where line. The statement above the quote is the reader's own wording. Four sub-facts rest on source code, commit history or a single live probe rather than on any Zotero documentation page, and the register marks each of them in its own statement rather than presenting them as documented:

- **The full-text page separator.** No Zotero page states it. The evidence is the extractor's own source, which pushes a form feed between pages, plus one probe that counted 16 form feeds in a 17-page document.
- **The file-URL path form.** The documentation says only that a file URL is returned. The concrete shape, with a drive letter, is one probe from this environment.
- **Saved-search execution.** Documented but never exercised, because the library used for probing contained no saved searches.
- **The Zotero version in which the native citation-key field reached all item types.** Neither the Zotero 8 nor the Zotero 9 changelog mentions the field. The version is triangulated from the schema commit to a schema version to a client tag, and it sits in unresolved tension with Better BibTeX's own statement that the field arrived with Zotero 8. Both statements are in the register, and neither is deleted.

One observation is left open rather than reconciled. A live local request returned a last-modified version of 20694 for an attachment whose item version is zero, in a library at version 540, which does not fit the Local API page's statement that these are local versions. Two records log it as an observation and neither resolves it. Both entries stay.

The register also carries one flat contradiction from the capture lane, recorded in that candidate's own section: one capture candidate's repository-wide grep for the citation-key names returns zero, and its reader takes that as corroboration that citekeys belong to Better BibTeX rather than to Zotero. The Z6 entries below say the field is native. Not looking for a field is not the same as the field being absent, and both readings stay as written.

### Z1. Local API write support on Zotero 10

78 facts, deduplicated by quote.

**1.** Zotero 10+ local API supports POST/PUT/PATCH/DELETE for items, collections and saved searches, plus tag deletion, full-text writes and file uploads.

```
In Zotero 10+, POST, PUT, PATCH, and DELETE are supported for items, collections, and saved searches. The local API also supports tag deletion, full-text writes, and file uploads.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api#write_requests, 'Write Requests'. Read in: Full-Text Content page, Write Requests page. Recorded under ids: `Z1-local-write-methods`, `Z1-local-methods-supported`.

**2.** The local API must be switched on in Settings > Advanced; otherwise requests return 403.

```
The local API must be enabled in Zotero’s preferences (Settings → Advanced → “Allow other applications on this computer to communicate with Zotero”). Requests will return 403 Forbidden if it is not enabled.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, intro, second paragraph. Read in: Full-Text Content page, Write Requests page, Basics page, zotero-schema commit 55a1312. Recorded under ids: `Z1-local-api-enable-403`, `Z1-local-api-enable-pref`, `Z1-local-api-preference-gate`, `Z1-preference-gate-403`.

**3.** Local reads need no authentication; local writes (Zotero 10+) need a runtime-granted local API key.

```
Read requests require no authentication. Write requests (Zotero 10+) require a local API key, which the user grants through a confirmation dialog.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, intro bullet list of differences from the Web API. Read in: Full-Text Content page. Record id `Z1-reads-unauth-writes-need-key`.

**4.** A client obtains a local key at runtime via POST /api/local/authorize with {"appName": ...} and a Zotero-Server-ID header; local keys are unrelated to zotero.org keys and cannot be pre-created.

```
Local API keys (Zotero 10+) are unrelated to zotero.org API keys and can’t be created in advance. A client asks for one at runtime:
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api#authorizing_writes, 'Authorizing Writes' (request block 'POST /api/local/authorize', 'Zotero-Server-ID: <serverID>', '{ "appName": "My Application" }'). Read in: Full-Text Content page. Record id `Z1-authorize-endpoint`.

**5.** Authorization pops a Zotero dialog naming the app with Allow / Always Allow / Deny buttons.

```
Zotero shows a dialog naming the application and asking the user to allow the change, with “Allow”, “Always Allow”, and “Deny” buttons.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api#authorizing_writes, 'Authorizing Writes'. Read in: Full-Text Content page, Write Requests page. Recorded under ids: `Z1-consent-dialog-buttons`, `Z1-consent-dialog`.

**6.** The response {key, remember}: remember=true (Always Allow) makes the 32-char key reusable indefinitely; otherwise the key is single-use, consumed by the first validated write, and clients must re-authorize on 401.

```
remember is true if the user chose “Always Allow”, in which case the key can be reused indefinitely. Otherwise the key is single-use: the first write request that successfully validates it consumes it, and a subsequent write needs a new key. Clients should always be prepared to handle a 401 from a write request by authorizing again.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api#authorizing_writes, 'Authorizing Writes' (response '{ "key": "\<32-character key>", "remember": false }'). Read in: Full-Text Content page, Write Requests page, Basics page, zotero-schema commit 55a1312. Recorded under ids: `Z1-key-lifetime-always-allow`, `Z1-always-allow-key-lifetime`, `Z1-key-lifetime`, `Z1-key-lifetime-single-use-vs-always-allow`.

**7.** Denial returns 403 with {"denied": true}; at most five dialog-producing requests per minute are accepted, after which 429 with Retry-After.

```
To limit prompt spam, no more than five requests that would show a dialog are accepted per minute; further requests return 429 Too Many Requests with a Retry-After header.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api#authorizing_writes, 'Authorizing Writes' (preceding sentence: 'If the user denies the request, the response is 403 Forbidden with { "denied": true }.'). Read in: Full-Text Content page. Record id `Z1-deny-403-and-rate-limit-429`.

**8.** The key is passed like a Web API key (Zotero-API-Key header recommended, Authorization: Bearer, or key= query); missing/unknown key yields 401 with a WWW-Authenticate challenge.

```
A write request with no key or an unrecognized key returns 401 Unauthorized with a WWW-Authenticate: Zotero-API-Key realm="Zotero Local API" header.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api#authorizing_writes, 'Authorizing Writes' (numbered list: 'As an HTTP header in the form Zotero-API-Key: <key> (recommended)'). Read in: Full-Text Content page, Write Requests page, Basics page. Recorded under ids: `Z1-key-passing-401`, `Z1-key-missing-401`, `Z1-key-passing-and-401`.

**9.** Local keys are stored in the profile, are unscoped (any editable library), and all remembered authorizations can be revoked via 'Clear Write Authorizations' in Settings > Advanced.

```
Keys are stored with the user’s profile, and unlike Web API keys, they aren’t scoped: a key allows writes to any library the user can edit. Users can revoke all remembered authorizations at any time with the “Clear Write Authorizations” button in Settings → Advanced.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api#authorizing_writes, 'Authorizing Writes'. Read in: Full-Text Content page, Write Requests page, Local API page, Basics page, Zotero 10 for Developers page, zotero-schema commit 55a1312. Recorded under ids: `Z1-key-unscoped-revoke`, `Z1-key-scope-and-revocation`, `Z1-key-scope-revocation`, `Z1-key-storage-scope-revocation`, `Z1-key-unscoped-and-revocation`.

**10.** Zotero-Server-ID request header is mandatory on every write including /api/local/authorize; omitting it is 428 Precondition Required.

```
On write requests, including POST /api/local/authorize, the header is required. A write without it is rejected with 428 Precondition Required.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api#server_id, 'Server ID'. Read in: Full-Text Content page, Write Requests page, zotero-schema commit 55a1312. Recorded under ids: `Z1-server-id-required-on-writes-428`, `Z1-server-id-required-on-write`.

**11.** The local API honours Zotero-Write-Token but caches tokens only in memory, so they are lost on Zotero restart.

```
Zotero-Write-Token is supported, but tokens are cached in memory, so they’re forgotten when Zotero restarts.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api#write_requests, 'Write Requests'. Read in: Full-Text Content page. Record id `Z1-write-token-local-memory`.

**12.** Zotero-Write-Token is an optional client-generated 32-char idempotency key for unversioned writes; the server remembers tokens of successful requests for 12 hours and rejects reuse with 412; failed requests do not store the token.

```
Zotero-Write-Token is an optional HTTP header, containing a client-generated random 32-character identifier string, that can be included with unversioned write requests to prevent them from being processed more than once (e.g., if a user clicks a form submit button twice). The Zotero server caches write tokens for successful requests for 12 hours, and subsequent requests from the same API key using the same write token will be rejected with a 412 Precondition Failed status code. If a request fails, the write token will not be stored.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests#zotero-write-token, 'Zotero-Write-Token'. Read in: Full-Text Content page, Write Requests page, Basics page. Recorded under ids: `Z1-write-token-semantics`, `Z1-write-token-web-semantics`, `Z1-write-token-definition`.

**13.** When a write carries If-Unmodified-Since-Version or per-object version properties, Zotero-Write-Token is redundant and should be omitted; the local API's 12-hour cache is in-memory only.

```
If using versioned write requests (i.e., those that include an If-Unmodified-Since-Version HTTP header or individual object version properties), Zotero-Write-Token is redundant and should be omitted.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests#zotero-write-token, 'Zotero-Write-Token' (next paragraph: 'In Zotero 10+, the local API also caches write tokens for 12 hours, but only in memory, so a token is forgotten if Zotero restarts.'). Read in: Full-Text Content page, Write Requests page. Record id `Z1-write-token-redundant-when-versioned`.

**14.** PUT/PATCH on an item must carry the current version via the version property or If-Unmodified-Since-Version; a stale version is 412, and omitting both is 428.

```
PUT and PATCH requests must include the item’s current version number in either the version property or the If-Unmodified-Since-Version header.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests#both_put_and_patch, 'Both PUT and PATCH' (and https://www.zotero.org/support/dev/web_api/v3/syncing#if-unmodified-since-version: 'If both are omitted, the API will return a 428 Precondition Required.'). Read in: Full-Text Content page. Record id `Z1-version-precondition-required`.

**15.** Up to 50 items/collections/searches per write request; the 200 result keys successful/unchanged/failed by array index and Last-Modified-Version is the version assigned to the successful objects.

```
The keys of the successful, unchanged, and failed objects are the numeric indexes of the Zotero objects in the uploaded array. The Last-Modified-Version is the version that has been assigned to any Zotero objects in the successful object — that is, objects that were modified in this request.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests#creating_multiple_objects, 'Creating Multiple Objects' (opening sentence: 'Up to 50 collections, saved searches, or items can be created in a single request by including multiple objects in an array:'). Read in: Full-Text Content page. Record id `Z1-multi-object-limit-and-result`.

**16.** Local API writes are ordinary local changes: immediately visible in the UI and synced up on the next sync.

```
Changes made through the local API are ordinary local changes. They’re visible in the Zotero UI immediately and will be uploaded to zotero.org on the next sync if the library is synced.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api#write_requests, 'Write Requests'. Read in: Full-Text Content page, Write Requests page, Local API page, Basics page, Zotero 10 for Developers page, zotero-schema commit 55a1312. Recorded under ids: `Z1-local-writes-are-ordinary-changes`, `Z1-local-writes-are-ordinary`, `Z1-local-changes-sync`, `Z1-local-writes-are-ordinary-local-changes`, `Z1-local-changes-are-ordinary`.

**17.** Local three-phase file upload works only for stored-file attachments (imported_file/imported_url), files under 4 GB; partial (binary diff) PATCH uploads are 405.

```
Uploads are only accepted for stored-file attachments (imported_file and imported_url); other attachment types return 400. Files must be under 4 GB.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api#file_uploads, 'File Uploads' (intro bullets: 'Partial (binary diff) file uploads are not supported. PATCH <userOrGroupPrefix>/items/<itemKey>/file will fail with 405 Method Not Allowed. Upload the full file instead.'). Read in: Full-Text Content page, Write Requests page, Basics page. Recorded under ids: `Z1-local-file-upload-constraints`, `Z4-upload-attachment-types`, `Z4-local-upload-constraints`.

**18.** The write_requests page states that in Zotero 10+ the local API supports the same write methods against the local database, using a runtime-granted local API key and local object versions for preconditions.

```
In Zotero 10+, the local API supports the same write methods against the local database. Writes there use a local API key granted by the user at runtime and check preconditions against local object versions; see Local API for the differences.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests, intro paragraph under H1 'Zotero Web API Write Requests'. Read in: Write Requests page, zotero-schema commit 55a1312. Recorded under ids: `Z1-local-write-parity`, `Z1-local-writes-use-local-versions`.

**19.** A denied authorization returns 403 {"denied":true}; at most five dialog-showing requests per minute are accepted, then 429 with Retry-After.

```
If the user denies the request, the response is 403 Forbidden with { "denied": true }. To limit prompt spam, no more than five requests that would show a dialog are accepted per minute; further requests return 429 Too Many Requests with a Retry-After header.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, H2 'Authorizing Writes'. Read in: Write Requests page, Basics page, zotero-schema commit 55a1312. Record id `Z1-deny-and-prompt-rate-limit`.

**20.** Not on the doc pages: the source stores local API keys in localAPIKeys.json in the Zotero profile directory, each entry recording key, appName, remember and createdAt.

```
return PathUtils.join(Zotero.Profile.dir, 'localAPIKeys.json');
```

Where: https://github.com/zotero/zotero/blob/fc17dcd24ad34686cb24e6b3ffb06a6a7a5e0e5d/chrome/content/zotero/xpcom/server/server_localAPI.js, function \_localAPIKeysPath (line 136). Read in: Write Requests page. Record id `Z1-key-store-src`.

**21.** The Zotero 10+ local API honours Zotero-Write-Token with the same 12-hour window but only in memory, so tokens are forgotten on restart.

```
In Zotero 10+, the local API also caches write tokens for 12 hours, but only in memory, so a token is forgotten if Zotero restarts.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests, H2 'Zotero-Write-Token' (same statement on local_api H2 'Write Requests': 'Zotero-Write-Token is supported, but tokens are cached in memory, so they’re forgotten when Zotero restarts.'). Read in: Write Requests page, Basics page, zotero-schema commit 55a1312. Recorded under ids: `Z1-write-token-local-memory`, `Z1-write-token-local-memory-only`, `Z1-write-token-local-in-memory`.

**22.** Not on the doc pages: the local implementation accepts a Zotero-Write-Token of 5-32 characters (400 otherwise), not strictly 32.

```
Validate the Zotero-Write-Token header (5-32 chars). If present, check that it
```

Where: https://github.com/zotero/zotero/blob/fc17dcd24ad34686cb24e6b3ffb06a6a7a5e0e5d/chrome/content/zotero/xpcom/server/server_localAPI.js, \_checkWriteToken doc comment (line 685). Read in: Write Requests page. Record id `Z1-write-token-length-src`.

**23.** PUT and PATCH on a single item must carry the current item version (JSON version property or If-Unmodified-Since-Version); stale version yields 412 and the client must re-fetch.

```
PUT and PATCH requests must include the item’s current version number in either the version property or the If-Unmodified-Since-Version header. (version is included in responses from the API, so clients that simply modify the editable data do not need to bother with a version header.) If the item has been changed on the server since the item was retrieved, the write request will be rejected with a 412 Precondition Failed error, and the most recent version of the item will have to be retrieved from the server before changes can be made.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests, H4 'Both PUT and PATCH'. Read in: Write Requests page, Basics page, zotero-schema commit 55a1312. Recorded under ids: `Z1-put-patch-version-precondition`, `Z1-version-precondition-on-put-patch`, `Z1-versioned-write-precondition-412`.

**24.** Writes that modify existing objects without either a version header or per-object version get 428 Precondition Required.

```
All write requests that modify existing objects must include either the If-Unmodified-Since-Version: <version> header or a #JSON version property for each object. If both are omitted, the API will return a 428 Precondition Required.
```

Where: https://www.zotero.org/support/dev/web_api/v3/syncing, H4 'If-Unmodified-Since-Version'. Read in: Write Requests page. Record id `Z1-428-when-no-version`.

**25.** PATCH sends only changed properties; omitted properties are untouched, and array properties are complete lists (clear with empty string/array).

```
With PATCH, you can submit just the properties that have actually changed, for a potentially much more efficient operation. Properties not included in the uploaded JSON are left untouched on the server. To clear a property, pass an empty string or an empty array as appropriate.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests, H4 'Partial-item updating (PATCH)'. Read in: Write Requests page. Record id `Z1-patch-partial-semantics`.

**26.** Multi-object create/update/delete requests are capped at 50 objects per request.

```
Up to 50 collections, saved searches, or items can be created in a single request by including multiple objects in an array:
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests, H3 'Creating Multiple Objects'. Read in: Write Requests page. Record id `Z1-batch-limit-50`.

**27.** Multi-object POST updates use PATCH semantics: unspecified properties are left alone; erase with empty string or false.

```
Note that POST follows PATCH semantics, meaning that any properties not specified will be left untouched on the server. To erase an existing property, include it with an empty string or false as the value.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests, H4 'Updating Multiple Objects'. Read in: Write Requests page. Record id `Z1-post-follows-patch`.

**28.** The Last-Modified-Version on a multi-object write response is the version assigned to every object in 'successful'.

```
The Last-Modified-Version is the version that has been assigned to any Zotero objects in the successful object — that is, objects that were modified in this request.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests, H3 'Creating Multiple Objects'. Read in: Write Requests page. Record id `Z1-multi-response-version`.

**29.** Client-generated object keys must match /[23456789ABCDEFGHIJKLMNPQRSTUVWXYZ]{8}/.

```
Local object keys should conform to the pattern /[23456789ABCDEFGHIJKLMNPQRSTUVWXYZ]{8}/.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests, H2 'Object Keys'. Read in: Write Requests page. Record id `Z1-object-key-pattern`.

**30.** Notes and attachments become children by setting parentItem; when created in the same POST the child must follow the parent and use a locally created key.

```
Notes and attachments can be made child items by assigning the parent item’s key to the parentItem property.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests, H4 'Both PUT and PATCH'. Read in: Write Requests page. Record id `Z1-child-items-parentItem`.

**31.** Basics page summarises local-API-specific status codes: 403 when disabled, 501 for unsupported features, 401 for writes lacking a key, 412/428 for Zotero-Server-ID errors.

```
It returns 401 Unauthorized for a write request without a valid local API key, and 412 or 428 for Zotero-Server-ID errors in addition to the versioning errors above.
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics, H2 'HTTP Status Codes'. Read in: Write Requests page. Record id `Z1-local-status-codes`.

**32.** The local API must be switched on in Settings → Advanced; otherwise every request returns 403.

```
The local API must be enabled in Zotero’s preferences (Settings → Advanced → “Allow other applications on this computer to communicate with Zotero”). Requests will return `403 Forbidden` if it is not enabled.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, intro (H1 'Zotero Local API'). Read in: Local API page, Zotero 10 for Developers page. Recorded under ids: `Z1-enable-pref-403`, `Z1-local-api-must-be-enabled-403`.

**33.** Base URL is http://localhost:23119/api/; reads need no auth, writes (Zotero 10+) need a runtime-granted local API key.

```
Read requests require no authentication. Write requests (Zotero 10+) require a local API key, which the user grants through a confirmation dialog. See [Authorizing Writes](#authorizing_writes).
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, intro bullet list under 'The notable differences from the Web API are:'. Read in: Local API page. Record id `Z1-base-url-reads-unauthenticated`.

**34.** Only API v3 is served, one version at a time; clients should GET /api/ and read Zotero-API-Version first.

```
Only API version 3 is supported, and only one version will ever be supported at a time. If a future version is released and your client needs to work against both old and new copies of Zotero, request `/api/` first and read the `Zotero-API-Version` response header to determine which version the running client speaks before making further requests.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, intro bullet list. Read in: Local API page, Zotero 10 for Developers page. Recorded under ids: `Z1-api-version-header`, `Z1-api-version-3-only`.

**35.** Only the locally logged-in user's data is served; pass 0 or the real numeric userID, anything else is 400.

```
Only data for the locally logged-in user is available. Pass `0` as the user ID or the user’s actual numeric ID, which can be found on the [API Keys](/settings/keys) page. Requests for any other user ID return `400`.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, intro bullet list. Read in: Local API page. Record id `Z1-user-id-zero`.

**36.** Zotero 10+ local API supports POST/PUT/PATCH/DELETE on items, collections and saved searches, plus tag deletion, full-text writes and file uploads, in Web API format.

```
In Zotero 10+, `POST`, `PUT`, `PATCH`, and `DELETE` are supported for items, collections, and saved searches. The local API also supports tag deletion, full-text writes, and file uploads. Requests and responses follow the same format as the Web API, described in [Write Requests](/support/dev/web_api/v3/write_requests).
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, § Write Requests. Read in: Local API page. Record id `Z1-write-methods`.

**37.** Local API keys cannot be pre-created; a client POSTs /api/local/authorize with {appName} and the Zotero-Server-ID header at runtime.

```
Local API keys (Zotero 10+) are unrelated to zotero.org API keys and can’t be created in advance. A client asks for one at runtime:

    POST /api/local/authorize
    Content-Type: application/json
    Zotero-Server-ID: <serverID>

    { "appName": "My Application" }
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, § Authorizing Writes. Read in: Local API page, Basics page, Zotero 10 for Developers page, zotero-schema commit 55a1312. Record id `Z1-authorize-endpoint`.

**38.** Zotero shows a consent dialog naming the app with Allow / Always Allow / Deny; approval returns a 32-character key plus a remember flag.

```
Zotero shows a dialog naming the application and asking the user to allow the change, with “Allow”, “Always Allow”, and “Deny” buttons. On approval, the response is

    { "key": "<32-character key>", "remember": false }
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, § Authorizing Writes. Read in: Local API page, Basics page, Zotero 10 for Developers page, zotero-schema commit 55a1312. Recorded under ids: `Z1-consent-dialog`, `Z1-consent-dialog-buttons`, `Z1-consent-dialog-allow-always-deny`.

**39.** Always Allow yields a reusable key (remember=true); plain Allow yields a single-use key consumed by the first validated write, so clients must handle 401 by re-authorizing.

```
`remember` is `true` if the user chose “Always Allow”, in which case the key can be reused indefinitely. Otherwise the key is single-use: the first write request that successfully validates it consumes it, and a subsequent write needs a new key. Clients should always be prepared to handle a `401` from a write request by authorizing again.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, § Authorizing Writes. Read in: Local API page, Zotero 10 for Developers page. Recorded under ids: `Z1-key-lifetime`, `Z1-key-lifetime-single-use-vs-always-allow`.

**40.** Deny returns 403 {denied:true}; at most five dialog-showing requests per minute, then 429 with Retry-After.

```
If the user denies the request, the response is `403 Forbidden` with `{ "denied": true }`. To limit prompt spam, no more than five requests that would show a dialog are accepted per minute; further requests return `429 Too Many Requests` with a `Retry-After` header.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, § Authorizing Writes. Read in: Local API page, Zotero 10 for Developers page. Recorded under ids: `Z1-deny-and-rate-limit`, `Z1-deny-403-and-dialog-rate-limit-429`.

**41.** The key is passed as Zotero-API-Key header (recommended), Authorization: Bearer, or key= query param; missing/unknown key gives 401 with a WWW-Authenticate header.

```
1.  As an HTTP header in the form `Zotero-API-Key: <key>` (recommended)
2.  As an HTTP header in the form `Authorization: Bearer <key>`
3.  As a URL query parameter, in the form `key=<key>` (not recommended)

A write request with no key or an unrecognized key returns `401 Unauthorized` with a `WWW-Authenticate: Zotero-API-Key realm="Zotero Local API"` header.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, § Authorizing Writes. Read in: Local API page. Record id `Z1-key-transport-401`.

**42.** Zotero-Server-ID request header is optional on reads (412 if mismatched) and required on all writes including /api/local/authorize (428 if absent).

```
- On read requests, the header is optional. If provided, it must match the current server, or the request is rejected with `412 Precondition Failed`.
- On write requests, including `POST /api/local/authorize`, the header is required. A write without it is rejected with `428 Precondition Required`.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, § Server ID. Read in: Local API page. Record id `Z1-server-id-required-on-writes`.

**43.** Zotero-Write-Token works on the local API but the token cache is in-memory and lost on restart.

```
`Zotero-Write-Token` is supported, but tokens are cached in memory, so they’re forgotten when Zotero restarts.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, § Write Requests. Read in: Local API page. Record id `Z1-write-token-local-memory`.

**44.** Zotero-Write-Token is an optional client-generated 32-char idempotency token for unversioned writes; server caches successful tokens 12 h and rejects reuse with 412; the local API does the same but in memory only.

```
`Zotero-Write-Token` is an optional HTTP header, containing a client-generated random 32-character identifier string, that can be included with unversioned write requests to prevent them from being processed more than once (e.g., if a user clicks a form submit button twice). The Zotero server caches write tokens for successful requests for 12 hours, and subsequent requests from the same API key using the same write token will be rejected with a `412 Precondition Failed` status code. If a request fails, the write token will not be stored. [...] In Zotero 10+, the [local API](/support/dev/web_api/v3/local_api) also caches write tokens for 12 hours, but only in memory, so a token is forgotten if Zotero restarts.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests, § Zotero-Write-Token (near end of page, before § Examples). Read in: Local API page. Record id `Z1-write-token-definition`.

**45.** With versioned writes (If-Unmodified-Since-Version or per-object version) the write token is redundant and should be omitted.

```
If using [versioned write requests](/support/dev/web_api/v3/syncing#version_numbers) (i.e., those that include an `If-Unmodified-Since-Version` HTTP header or individual object `version` properties), `Zotero-Write-Token` is redundant and should be omitted.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests, § Zotero-Write-Token. Read in: Local API page. Record id `Z1-write-token-redundant-when-versioned`.

**46.** SOURCE-DERIVED: the local server accepts write tokens of 5-32 chars (400 otherwise), 412 on reuse within the cache window.

```
Validate the Zotero-Write-Token header (5-32 chars). If present, check that it
	 * hasn't been used for a successful write within the last 12 hours; otherwise,
	 * return a 412 response.
```

Where: https://raw.githubusercontent.com/zotero/zotero/main/chrome/content/zotero/xpcom/server/server_localAPI.js @ fc17dcd2, \_checkWriteToken(). Read in: Local API page. Record id `Z1-write-token-length-SOURCE`.

**47.** PUT/PATCH must carry the current object version (JSON version or If-Unmodified-Since-Version); stale version gives 412.

```
`PUT` and `PATCH` requests must include the item’s current version number in either the `version` property or the `If-Unmodified-Since-Version` header. (`version` is included in responses from the API, so clients that simply modify the editable data do not need to bother with a version header.) If the item has been changed on the server since the item was retrieved, the write request will be rejected with a `412 Precondition Failed` error
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests, § Item Requests › Updating an Existing Item. Read in: Local API page. Record id `Z1-version-precondition-on-updates`.

**48.** Deletes without If-Unmodified-Since-Version return 428 Precondition Required.

```
| `428 Precondition Required` | `If-Unmodified-Since-Version` was not provided.                                           |
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests, § Deleting an Item (also § Deleting Multiple Items). Read in: Local API page. Record id `Z1-428-when-no-version`.

**49.** The write_requests page confirms local writes use a runtime-granted key and local-version preconditions.

```
In Zotero 10+, the [local API](/support/dev/web_api/v3/local_api) supports the same write methods against the local database. Writes there use a local API key granted by the user at runtime and check preconditions against local object versions; see [Local API](/support/dev/web_api/v3/local_api#write_requests) for the differences.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests, intro. Read in: Local API page. Record id `Z1-write-requests-page-crossref`.

**50.** Local API write support shipped in Zotero 10.0 (August 17, 2026).

```
**[Local API write support](https://www.zotero.org/support/dev/web_api/v3/local_api#write_requests)**
```

Where: https://www.zotero.org/support/changelog, § Changes in 10.0 (August 17, 2026) › Developer-specific changes/fixes. Read in: Local API page. Record id `Z1-introduced-in-zotero-10`.

**51.** Because reads are unauthenticated the port must not be exposed externally.

```
Since reads are unauthenticated, applications running locally can read the user’s library. Do not forward the port or otherwise expose it externally.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, intro bullet list. Read in: Local API page. Record id `Z1-no-port-forwarding`.

**52.** The basics page states the desktop client serves the same API endpoints locally on localhost:23119 under /api/ from the local database.

```
The Zotero desktop client exposes a local implementation of this API on localhost:23119 under /api/, serving data from the user’s local database. See Local API for details. The sections below note where local API behavior diverges from the Web API.
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics, heading "Local API". Read in: Basics page. Record id `Z1-local-api-overview`.

**53.** Local API reads need no auth; writes (Zotero 10+) need a runtime-granted local API key unrelated to zotero.org keys.

```
The local API does not use authentication for read requests. Write requests (Zotero 10+) require a local API key, which is unrelated to a zotero.org API key and is granted by the user at runtime; see Authorizing Writes.
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics, heading "Authentication". Read in: Basics page. Record id `Z1-reads-unauthenticated-writes-need-local-key`.

**54.** Zotero 10+ local API supports POST/PUT/PATCH/DELETE for items, collections and saved searches, plus tag deletion, full-text writes and file uploads, in Web API format.

```
In Zotero 10+, POST, PUT, PATCH, and DELETE are supported for items, collections, and saved searches. The local API also supports tag deletion, full-text writes, and file uploads. Requests and responses follow the same format as the Web API, described in Write Requests.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, heading "Write Requests". Read in: Basics page, zotero-schema commit 55a1312. Recorded under ids: `Z1-write-methods`, `Z1-local-write-methods`.

**55.** Zotero-Server-ID request header is optional on reads (412 if mismatched) but required on writes including /api/local/authorize (428 if absent).

```
-   On read requests, the header is optional. If provided, it must match the current server, or the request is rejected with 412 Precondition Failed.
-   On write requests, including POST /api/local/authorize, the header is required. A write without it is rejected with 428 Precondition Required.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, heading "Server ID". Read in: Basics page. Record id `Z1-server-id-required-for-writes`.

**56.** Local API returns 403 when the preference is off, 501 for unsupported asks, 401 for unauthenticated writes, and 412/428 for Zotero-Server-ID errors.

```
The local API returns 403 Forbidden when the local API preference is not enabled and 501 Not Implemented when a request asks for something it does not support (Atom output, or an API version other than 3 on an endpoint other than /api/). It returns 401 Unauthorized for a write request without a valid local API key, and 412 or 428 for Zotero-Server-ID errors in addition to the versioning errors above.
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics, heading "HTTP Status Codes". Read in: Basics page, zotero-schema commit 55a1312. Recorded under ids: `Z1-local-status-codes`, `Z2-error-codes-local`.

**57.** Source confirms single-use keys are deleted from the profile key store on first successful validation; remembered keys persist with no expiry logic.

```
/**
 * Look up a candidate API key. If valid, single-use keys (non-"remember") are deleted
 * before being returned.
 * Returns null if the key isn't registered.
 */
async function consumeLocalAPIKey(key) {
```

Where: https://github.com/zotero/zotero/blob/fc17dcd24ad34686cb24e6b3ffb06a6a7a5e0e5d/chrome/content/zotero/xpcom/server/server_localAPI.js, lines 184-190 (addLocalAPIKey at 166-181 stores {key, appName, remember, createdAt} via \_saveLocalAPIKeys to a JSON file). Read in: Basics page. Record id `Z1-source-single-use-key-consumption`.

**58.** Only the locally logged-in user's data is served; pass user ID 0 or the real numeric ID.

```
-   Only data for the locally logged-in user is available. Pass 0 as the user ID or the user’s actual numeric ID, which can be found on the API Keys page. Requests for any other user ID return 400.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, intro list "The notable differences from the Web API are:". Read in: Basics page. Record id `Z1-local-user-id-zero`.

**59.** Zotero 10's local API (/api/) supports write requests, and every response carries a stable Zotero-Server-ID header that is optional on reads and required on writes.

```
The local API (`/api/`) now supports write requests. Every response includes a `Zotero-Server-ID` header with a stable ID identifying the Zotero instance. Cache it and pass it back in a `Zotero-Server-ID` request header to confirm you’re still talking to the same instance — optional on reads, required on writes. If the ID changes, discard or reconcile any locally cached data: object versions from one instance have no relation to versions from another instance or from the web API.
```

Where: https://www.zotero.org/support/dev/zotero_10_for_developers § Local HTTP server and local API. Read in: Zotero 10 for Developers page. Record id `Z1-local-api-write-support-z10`.

**60.** The Zotero 10 local HTTP server (port 23119) rejects requests whose Host header is not localhost/127.0.0.1/[::1] with a 400.

```
Requests must send a `Host` header of `localhost`, `127.0.0.1`, or `[::1]`; anything else gets a 400.
```

Where: https://www.zotero.org/support/dev/zotero_10_for_developers § Local HTTP server and local API. Read in: Zotero 10 for Developers page. Record id `Z1-host-header-400`.

**61.** Requests with a Mozilla/ User-Agent or any Origin header are silently dropped unless they send Zotero-Allowed-Request; this now applies to JSON POSTs too.

```
Requests that look like they come from a browser — a `User-Agent` starting with `Mozilla/` or any `Origin` header — are dropped without a response unless they send a `Zotero-Allowed-Request` header or come from the connector. This check previously applied only to CORS-simple content types, so, e.g., a JSON POST that worked before may now be rejected — add the `Zotero-Allowed-Request` header. Custom endpoints can opt out with `allowRequestsFromUnsafeWebContent = true`.
```

Where: https://www.zotero.org/support/dev/zotero_10_for_developers § Local HTTP server and local API. Read in: Zotero 10 for Developers page. Record id `Z1-browser-like-requests-dropped`.

**62.** Local API reads need no authentication; writes (Zotero 10+) need a runtime-granted local API key.

```
Read requests require no authentication. Write requests (Zotero 10+) require a local API key, which the user grants through a confirmation dialog. See Authorizing Writes.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api (intro bullet list). Read in: Zotero 10 for Developers page, zotero-schema commit 55a1312. Recorded under ids: `Z1-reads-unauthenticated-writes-need-key`, `Z1-reads-unauthenticated`.

**63.** Zotero 10+ local API supports POST/PUT/PATCH/DELETE for items, collections and saved searches, plus tag deletion, full-text writes and file uploads, in the Web API request/response format.

```
In Zotero 10+, `POST`, `PUT`, `PATCH`, and `DELETE` are supported for items, collections, and saved searches. The local API also supports tag deletion, full-text writes, and file uploads. Requests and responses follow the same format as the Web API, described in Write Requests.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api § Write Requests. Read in: Zotero 10 for Developers page. Record id `Z1-write-methods-supported`.

**64.** The local key is passed like a Web API key (Zotero-API-Key header recommended, Bearer, or key= query param); a missing/unknown key yields 401 with a WWW-Authenticate realm header.

```
Pass the key with each write request, the same way as a Web API key: 1. As an HTTP header in the form `Zotero-API-Key: <key>` (recommended) 2. As an HTTP header in the form `Authorization: Bearer <key>` 3. As a URL query parameter, in the form `key=<key>` (not recommended) A write request with no key or an unrecognized key returns `401 Unauthorized` with a `WWW-Authenticate: Zotero-API-Key realm="Zotero Local API"` header.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api § Authorizing Writes. Read in: Zotero 10 for Developers page. Record id `Z1-key-transport-and-401`.

**65.** Zotero-Server-ID is optional on reads (mismatch → 412) and required on writes including /api/local/authorize (absent → 428).

```
On read requests, the header is optional. If provided, it must match the current server, or the request is rejected with `412 Precondition Failed`. On write requests, including `POST /api/local/authorize`, the header is required. A write without it is rejected with `428 Precondition Required`.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api § Server ID. Read in: Zotero 10 for Developers page. Record id `Z1-server-id-optional-reads-required-writes`.

**66.** The local API honours Zotero-Write-Token but caches tokens only in memory (12 hours per the write_requests page), so they are forgotten on restart.

```
`Zotero-Write-Token` is supported, but tokens are cached in memory, so they’re forgotten when Zotero restarts. || In Zotero 10+, the local API also caches write tokens for 12 hours, but only in memory, so a token is forgotten if Zotero restarts.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api § Write Requests || https://www.zotero.org/support/dev/web_api/v3/write_requests § Zotero-Write-Token. Read in: Zotero 10 for Developers page. Record id `Z1-write-token-local-memory-only`.

**67.** Zotero-Write-Token is an optional client-generated 32-char idempotency token for unversioned writes; reuse within 12 h → 412; redundant when versioned preconditions are used.

```
`Zotero-Write-Token` is an optional HTTP header, containing a client-generated random 32-character identifier string, that can be included with unversioned write requests to prevent them from being processed more than once (e.g., if a user clicks a form submit button twice). The Zotero server caches write tokens for successful requests for 12 hours, and subsequent requests from the same API key using the same write token will be rejected with a `412 Precondition Failed` status code. If a request fails, the write token will not be stored. If using versioned write requests (i.e., those that include an `If-Unmodified-Since-Version` HTTP header or individual object `version` properties), `Zotero-Write-Token` is redundant and should be omitted.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests § Zotero-Write-Token. Read in: Zotero 10 for Developers page. Record id `Z1-write-token-definition`.

**68.** Creating objects requires either Zotero-Write-Token or If-Unmodified-Since-Version with the last library version.

```
POST <userOrGroupPrefix>/items Content-Type: application/json Zotero-Write-Token: <write token> or If-Unmodified-Since-Version: <last library version>
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests § Creating an Item. Read in: Zotero 10 for Developers page. Record id `Z1-create-requires-token-or-version`.

**69.** Every write that modifies existing objects must carry If-Unmodified-Since-Version or a per-object JSON version; omitting both yields 428.

```
All write requests that modify existing objects must include either the `If-Unmodified-Since-Version: <version>` header or a JSON version property for each object. If both are omitted, the API will return a `428 Precondition Required`.
```

Where: https://www.zotero.org/support/dev/web_api/v3/syncing § If-Unmodified-Since-Version. Read in: Zotero 10 for Developers page. Record id `Z1-modify-requires-version-428`.

**70.** PUT and PATCH must include the item's current version (JSON version property or header); a stale version is rejected with 412.

```
`PUT` and `PATCH` requests must include the item’s current version number in either the `version` property or the `If-Unmodified-Since-Version` header. (`version` is included in responses from the API, so clients that simply modify the editable data do not need to bother with a version header.) If the item has been changed on the server since the item was retrieved, the write request will be rejected with a `412 Precondition Failed` error, and the most recent version of the item will have to be retrieved from the server before changes can be made.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests § Both PUT and PATCH. Read in: Zotero 10 for Developers page. Record id `Z1-put-patch-version-412`.

**71.** PATCH sends only changed properties; omitted properties are untouched, arrays are complete lists, and clearing uses empty string/array.

```
With `PATCH`, you can submit just the properties that have actually changed, for a potentially much more efficient operation. Properties not included in the uploaded JSON are left untouched on the server. To clear a property, pass an empty string or an empty array as appropriate. [...] Array properties are interpreted as complete lists, so omitting a collection key would cause the item to be removed from that collection.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests § Partial-item updating (PATCH). Read in: Zotero 10 for Developers page. Record id `Z1-patch-semantics`.

**72.** Multi-object POST handles up to 50 objects, follows PATCH semantics, and returns successful/unchanged/failed keyed by array index.

```
Up to 50 collections, saved searches, or items can be updated in a single request. [...] Note that `POST` follows `PATCH` semantics, meaning that any properties not specified will be left untouched on the server. To erase an existing property, include it with an empty string or `false` as the value. || The keys of the `successful`, `unchanged`, and `failed` objects are the numeric indexes of the Zotero objects in the uploaded array. The `Last-Modified-Version` is the version that has been assigned to any Zotero objects in the `successful` object — that is, objects that were modified in this request.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests § Updating Multiple Objects; § Creating Multiple Objects. Read in: Zotero 10 for Developers page. Record id `Z1-multi-object-post-patch-semantics-50`.

**73.** On update, dateAdded if supplied must match (else 400) and dateModified defaults to now when omitted.

```
If `dateAdded` is included with an existing item, it must match the existing `dateAdded` value or else the API will return a 400 error. If a new `dateModified` time is not included with an update to existing item, the item’s `dateModified` value will be set to the current time.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests § Updating Multiple Objects. Read in: Zotero 10 for Developers page. Record id `Z1-dateModified-dateAdded-rules`.

**74.** Client-generated object keys must match /[23456789ABCDEFGHIJKLMNPQRSTUVWXYZ]{8}/.

```
Local object keys should conform to the pattern `/[23456789ABCDEFGHIJKLMNPQRSTUVWXYZ]{8}/`.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests § Object Keys. Read in: Zotero 10 for Developers page. Record id `Z1-object-key-pattern`.

**75.** The key is passed as Zotero-API-Key header (recommended), Authorization: Bearer, or key= query; missing/unknown key yields 401 with a WWW-Authenticate header.

```
As an HTTP header in the form Zotero-API-Key: <key> (recommended)
As an HTTP header in the form Authorization: Bearer <key>
As a URL query parameter, in the form key=<key> (not recommended)
A write request with no key or an unrecognized key returns 401 Unauthorized with a WWW-Authenticate: Zotero-API-Key realm="Zotero Local API" header.
```

Where: local_api, heading "Authorizing Writes". Read in: zotero-schema commit 55a1312. Record id `Z1-key-transport-and-401`.

**76.** Zotero-Write-Token is an optional 32-char client-generated idempotency header for unversioned writes, cached 12 hours server-side, duplicate → 412; redundant when versioned preconditions are used.

```
Zotero-Write-Token is an optional HTTP header, containing a client-generated random 32-character identifier string, that can be included with unversioned write requests to prevent them from being processed more than once (e.g., if a user clicks a form submit button twice). The Zotero server caches write tokens for successful requests for 12 hours, and subsequent requests from the same API key using the same write token will be rejected with a 412 Precondition Failed status code. If a request fails, the write token will not be stored.
If using versioned write requests (i.e., those that include an If-Unmodified-Since-Version HTTP header or individual object version properties), Zotero-Write-Token is redundant and should be omitted.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests, heading "Zotero-Write-Token" (Last updated 2026-07-29). Read in: zotero-schema commit 55a1312. Record id `Z1-write-token-web-semantics`.

**77.** Up to 50 objects can be created or updated per multi-object request.

```
Up to 50 collections, saved searches, or items can be created in a single request by including multiple objects in an array:
...
Up to 50 collections, saved searches, or items can be updated in a single request.
```

Where: write_requests, headings "Creating Multiple Objects" and "Updating Multiple Objects". Read in: zotero-schema commit 55a1312. Record id `Z1-batch-limit-50`.

**78.** Live: the local Zotero 10.0.1 returns Zotero-Server-ID and Zotero-Schema-Version on GET /api/.

```
HTTP/1.0 200 OK
X-Zotero-Version: 10.0.1
X-Zotero-Connector-API-Version: 3
Zotero-API-Version: 3
Zotero-Schema-Version: 44
Zotero-Server-ID: 6LpvURP2E933
```

Where: GET http://localhost:23119/api/, response headers, observed 2026-09-05 (docs/environment.md still says 9.0.6). Read in: zotero-schema commit 55a1312. Record id `Z1-live-local-headers-zotero-10`.

### Z2. Version semantics

55 facts, deduplicated by quote.

**79.** Zotero 10+ local object versions bear no relation to Web API versions or to other instances' versions, everywhere versions appear (JSON version, Last-Modified-Version, format=versions, ?since=, If-Unmodified-Since-Version).

```
Local versions in Zotero 10+ therefore have no relation to Web API versions, and no relation to the local versions reported by any other Zotero instance. This applies everywhere versions appear: the version property of object JSON, Last-Modified-Version response headers, format=versions responses, ?since= filtering, and the If-Unmodified-Since-Version and per-object version preconditions used for writes.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api#object_versions, 'Object Versions'. Read in: Full-Text Content page, zotero-schema commit 55a1312. Recorded under ids: `Z2-local-versions-no-relation`, `Z2-local-versions-apply-everywhere`.

**80.** Local versions increment once per library per transaction on any save or delete, regardless of whether the change came from the user, a sync, or a local API write.

```
They’re incremented once per library per transaction whenever an object in that library is saved or deleted, whether the change comes from the user, a sync, or a local API write.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api#object_versions, 'Object Versions'. Read in: Full-Text Content page. Record id `Z2-local-version-increment-rule`.

**81.** Every Zotero 10+ local response carries Zotero-Server-ID identifying the instance; all object versions are local to that instance.

```
In Zotero 10+, every response includes a Zotero-Server-ID header identifying the Zotero instance, and all object versions are local to that instance, with no relation to Web API versions.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, intro bullet list (example header 'Zotero-Server-ID: sPMHtLD6HHBd' under 'Server ID'). Read in: Full-Text Content page. Record id `Z2-server-id-header`.

**82.** The server ID lives in the database, survives restarts/upgrades, and a different ID means a different database with different versions and keys.

```
The ID is stored in the Zotero database, so it follows the user’s data rather than the installation, and it stays the same across restarts and upgrades. A different ID means a different database and therefore a different set of object versions and keys.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api#server_id, 'Server ID'. Read in: Full-Text Content page, Write Requests page, Zotero 10 for Developers page, zotero-schema commit 55a1312. Recorded under ids: `Z2-server-id-follows-database`, `Z2-server-id-stability`, `Z2-server-id-identity`.

**83.** Persisted client state must be partitioned by server ID; Web API data belongs to its own partition because the Web API does not yet emit or validate Zotero-Server-ID.

```
Clients that store data between runs should partition it by server ID. The Web API does not currently provide or validate Zotero-Server-ID, but it will in the future, so treat Web API data as belonging to its own partition.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api#server_id, 'Server ID'. Read in: Full-Text Content page, Write Requests page, Basics page, zotero-schema commit 55a1312. Recorded under ids: `Z2-partition-by-server-id`, `Z2-server-id-partition-rule`, `Z2-partition-web-api-too`.

**84.** Sending a Zotero-Server-ID on reads is optional but, if sent and mismatched, yields 412; a 412 means a different instance and the client must discard cached data and versions.

```
A 412 means the client is talking to a Zotero instance other than the one its cached data came from. Discard cached data, including versions, and start over with the new ID.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api#server_id, 'Server ID' (bullet: 'On read requests, the header is optional. If provided, it must match the current server, or the request is rejected with 412 Precondition Failed.'). Read in: Full-Text Content page, Basics page. Recorded under ids: `Z2-server-id-mismatch-412-discard`, `Z2-412-means-discard-cache`.

**85.** Before Zotero 10 the local API reported synced versions (0 for never-synced, unchanged on local edits), so clients must discard versions stored from older releases rather than compare.

```
Earlier versions of Zotero reported synced versions from the local API, which were 0 for objects that had never been synced and didn’t change when an object was modified locally.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api#object_versions, 'Object Versions' (continues: 'local API clients should discard any stored versions rather than compare them to new ones.'). Read in: Full-Text Content page. Record id `Z2-pre-zotero10-versions-unusable`.

**86.** Group metadata (/groups, /groups/<groupID>) still reports the synced group version; objects inside group libraries use local versions.

```
Group metadata is the exception: <userOrGroupPrefix>/groups and /groups/<groupID> report the synced group version, which has no local counterpart.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api#object_versions, 'Object Versions'. Read in: Full-Text Content page, Write Requests page. Record id `Z2-group-metadata-exception`.

**87.** ?since=<integer> (default 0) returns only objects modified after the given library version, which the client takes from a previous Last-Modified-Version header.

```
Return only objects modified after the specified library version, returned in a previous Last-Modified-Version header. See Syncing for more info.
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics#search_parameters, 'Search Parameters' table, since row (Values: integer, Default: 0). Read in: Full-Text Content page, Write Requests page. Recorded under ids: `Z2-since-parameter`, `Z2-since-param`.

**88.** format=versions on multi-object collection/item/search requests returns {objectKey: version} for all matches with no default or maximum limit.

```
versions, valid for multi-object collection, item, and search requests, will return a JSON object with Zotero object keys as keys and object versions as values. Like keys, versions mode has no default or maximum limit.
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics#general_parameters, 'General Parameters' table, format row. Read in: Full-Text Content page, Basics page, zotero-schema commit 55a1312. Record id `Z2-format-versions`.

**89.** Last-Modified-Version is the library version on multi-object requests and the object version on single-object requests.

```
The Last-Modified-Version response header indicates the current version of either a library (for multi-object requests) or an individual object (for single-object requests).
```

Where: https://www.zotero.org/support/dev/web_api/v3/syncing#last-modified-version, 'Version Numbers' > 'Last-Modified-Version' (page last updated 2022-08-14; linked from write_requests and basics). Read in: Full-Text Content page. Record id `Z2-last-modified-version-scope`.

**90.** Versions are monotonically increasing but not sequential and must be treated as opaque integers.

```
The version number is guaranteed to be monotonically increasing but is not guaranteed to increase sequentially, and clients should treat it as an opaque integer value.
```

Where: https://www.zotero.org/support/dev/web_api/v3/syncing#version_numbers, 'Version Numbers' (page last updated 2022-08-14). Read in: Full-Text Content page, Write Requests page, Local API page, Basics page, Zotero 10 for Developers page. Recorded under ids: `Z2-versions-monotonic-opaque`, `Z2-version-opaque-monotonic`, `Z2-version-monotonic-opaque`.

**91.** format=versions returns a JSON object mapping object keys to object versions, with no default or maximum limit.

```
format=versions is similar to format=keys, but instead of returning a newline-delimited list of object keys, it returns a JSON object with object versions keyed by object keys:
```

Where: https://www.zotero.org/support/dev/web_api/v3/syncing, H4 '?format=versions'. Read in: Write Requests page, Basics page. Recorded under ids: `Z2-format-versions`, `Z2-format-versions-syncing`.

**92.** format=versions is not paginated and returns all matching objects by default.

```
Like format=keys, format=versions is not limited by a maximum number of results and returns all matching objects by default.
```

Where: https://www.zotero.org/support/dev/web_api/v3/syncing, H4 '?format=versions'. Read in: Write Requests page. Record id `Z2-format-versions-unlimited`.

**93.** Last-Modified-Version is the library version on multi-object requests and the object version on single-object requests; a write bumps the library version and stamps modified objects with it.

```
The Last-Modified-Version response header indicates the current version of either a library (for multi-object requests) or an individual object (for single-object requests). If changes are made to a library in a write request, the library’s version number will be increased, any objects modified in the same request will be set to the new version number, and the new version number will be returned in the Last-Modified-Version header.
```

Where: https://www.zotero.org/support/dev/web_api/v3/syncing, H4 'Last-Modified-Version'. Read in: Write Requests page. Record id `Z2-last-modified-version-header`.

**94.** If-Modified-Since-Version on a multi-object read yields 304 when the library is unchanged.

```
Multi-object requests (e.g., /users/1/items) return a Last-Modified-Version header with the current library version. If a If-Modified-Since-Version: <libraryVersion> header is passed with a subsequent multi-object read request and data has not changed in the library since the specified version, the API will return 304 Not Modified instead of 200.
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics, H2 'Caching'. Read in: Write Requests page. Record id `Z2-if-modified-since-304`.

**95.** In Zotero 10+ local API versions are maintained locally, incremented once per library per transaction on any save/delete from any source.

```
In Zotero 10+, data object versions returned by the local API are maintained locally, not by the sync server. They’re incremented once per library per transaction whenever an object in that library is saved or deleted, whether the change comes from the user, a sync, or a local API write.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, H2 'Object Versions'. Read in: Write Requests page, Local API page, Zotero 10 for Developers page, zotero-schema commit 55a1312. Recorded under ids: `Z2-local-versions-are-local`, `Z2-local-versions-per-library-transaction`, `Z2-version-increment-rule`, `Z2-local-version-increment-rule`.

**96.** Local versions apply to the JSON version property, Last-Modified-Version, format=versions, ?since= and all write preconditions.

```
This applies everywhere versions appear: the version property of object JSON, Last-Modified-Version response headers, format=versions responses, ?since= filtering, and the If-Unmodified-Since-Version and per-object version preconditions used for writes.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, H2 'Object Versions'. Read in: Write Requests page. Record id `Z2-local-versions-everywhere`.

**97.** Pre-10 Zotero local API returned synced versions (0 for never-synced, unchanged on local edits), so stored pre-10 versions must be discarded, not compared.

```
Earlier versions of Zotero reported synced versions from the local API, which were 0 for objects that had never been synced and didn’t change when an object was modified locally. Local versions are usually much lower than the synced versions those releases returned, so local API clients should discard any stored versions rather than compare them to new ones.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, H2 'Object Versions'. Read in: Write Requests page, Basics page, zotero-schema commit 55a1312. Recorded under ids: `Z2-pre-10-version-drift`, `Z2-pre-10-versions-were-synced`, `Z2-pre-10-synced-versions`.

**98.** On reads the Zotero-Server-ID header is optional but, if sent and mismatched, yields 412 (client should discard cache and restart).

```
On read requests, the header is optional. If provided, it must match the current server, or the request is rejected with 412 Precondition Failed.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, H2 'Server ID'. Read in: Write Requests page. Record id `Z2-server-id-read-optional`.

**99.** Basics page: ?since= is the preferred change-fetch mechanism against the local API, with the server-ID partition caveat.

```
The ?since= parameter is also supported and is the preferred way to fetch only changed objects from a large local library. Note that in Zotero 10+, local versions are unrelated to the versions in this API, so clients must partition cached data by server ID. See Object Versions.
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics, H2 'Caching'. Read in: Write Requests page, zotero-schema commit 55a1312. Recorded under ids: `Z2-basics-since-preferred-locally`, `Z2-local-since-and-partition-rule`.

**100.** When creating objects with client-chosen keys and no If-Unmodified-Since-Version, use version 0 to assert they do not yet exist.

```
When writing new objects with an object key in a request without If-Unmodified-Since-Version, use the special version 0 to indicate that the objects should not yet exist on the server.
```

Where: https://www.zotero.org/support/dev/web_api/v3/syncing, H4 'JSON version property'. Read in: Write Requests page. Record id `Z2-version-0-for-new-keyed-objects`.

**101.** Every Zotero 10+ local response carries Zotero-Server-ID, a DB-stored instance identifier stable across restarts/upgrades; a different ID means different versions and keys.

```
In Zotero 10+, every local API response includes a `Zotero-Server-ID` header containing a string that identifies the Zotero instance being talked to:

    Zotero-Server-ID: sPMHtLD6HHBd

The ID is stored in the Zotero database, so it follows the user’s data rather than the installation, and it stays the same across restarts and upgrades. A different ID means a different database and therefore a different set of object versions and keys.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, § Server ID. Read in: Local API page. Record id `Z2-server-id-header`.

**102.** Clients cache the ID from any response (bare GET /api/ suffices), echo it back, discard all cached data on 412, and partition stored data by server ID, treating Web API data as its own partition.

```
Clients should read the ID from any response — a bare `GET /api/` is enough — cache it, and pass it back in the `Zotero-Server-ID` request header: [...] A `412` means the client is talking to a Zotero instance other than the one its cached data came from. Discard cached data, including versions, and start over with the new ID.

Clients that store data between runs should partition it by server ID. The Web API does not currently provide or validate `Zotero-Server-ID`, but it will in the future, so treat Web API data as belonging to its own partition.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, § Server ID. Read in: Local API page. Record id `Z2-server-id-partition-rule`.

**103.** Local versions have no relation to Web API or other-instance versions, and this applies to JSON version, Last-Modified-Version, format=versions, ?since=, and write preconditions.

```
Local versions in Zotero 10+ therefore have **no relation** to Web API versions, and no relation to the local versions reported by any other Zotero instance. This applies everywhere versions appear: the `version` property of object JSON, `Last-Modified-Version` response headers, `format=versions` responses, `?since=` filtering, and the `If-Unmodified-Since-Version` and per-object `version` preconditions used for writes.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, § Object Versions. Read in: Local API page, Zotero 10 for Developers page. Recorded under ids: `Z2-versions-apply-everywhere`, `Z2-no-relation-to-web-or-other-instances`.

**104.** Pre-10 Zotero exposed synced versions (0 for never-synced, unchanged by local edits); clients must discard stored versions rather than compare.

```
Earlier versions of Zotero reported synced versions from the local API, which were `0` for objects that had never been synced and didn’t change when an object was modified locally. Local versions are usually much lower than the synced versions those releases returned, so local API clients should discard any stored versions rather than compare them to new ones.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, § Object Versions. Read in: Local API page, Zotero 10 for Developers page. Recorded under ids: `Z2-pre-10-versions-discard`, `Z2-discard-pre-10-stored-versions`.

**105.** Group metadata endpoints report the synced group version; objects inside group libraries use local versions.

```
Group metadata is the exception: `<userOrGroupPrefix>/groups` and `/groups/<groupID>` report the synced group version, which has no local counterpart. Objects *within* group libraries — their items, collections, and searches — use local versions like all others.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, § Object Versions. Read in: Local API page, Zotero 10 for Developers page. Recorded under ids: `Z2-group-metadata-exception`, `Z2-group-metadata-version-exception`.

**106.** ?since=<integer> returns only objects modified after the given library version (from a prior Last-Modified-Version); default 0.

```
| `since`    | integer                         | `0`     | Return only objects modified after the specified library version, returned in a previous `Last-Modified-Version` header. See [Syncing](/support/dev/web_api/v3/syncing) for more info. |
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics, § Searching › Search Parameters. Read in: Local API page. Record id `Z2-since-param-definition`.

**107.** On the local API ?since= is the preferred way to fetch changed objects, and cached data must be partitioned by server ID.

```
Conditional requests work the same way against the [local API](/support/dev/web_api/v3/local_api), but local responses are already inexpensive to produce, so aggressive caching on the client side is less important. The `?since=` parameter is also supported and is the preferred way to fetch only changed objects from a large local library. Note that in Zotero 10+, local versions are unrelated to the versions in this API, so clients must partition cached data by server ID. See [Object Versions](/support/dev/web_api/v3/local_api#object_versions).
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics, § Caching. Read in: Local API page. Record id `Z2-since-preferred-locally-partition`.

**108.** Multi-object reads return Last-Modified-Version; sending If-Modified-Since-Version yields 304 when nothing changed.

```
Multi-object requests (e.g., `/users/1/items`) return a `Last-Modified-Version` header with the current library version. If a `If-Modified-Since-Version: <libraryVersion>` header is passed with a subsequent multi-object read request and data has not changed in the library since the specified version, the API will return `304 Not Modified` instead of `200`. (Single-object conditional requests are not currently supported, but will be supported in the future.)
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics, § Caching. Read in: Local API page, Zotero 10 for Developers page. Recorded under ids: `Z2-if-modified-since-version-304`, `Z2-if-modified-since-304`.

**109.** Last-Modified-Version is the library version on multi-object requests and the object version on single-object requests; writes bump the library version and stamp modified objects with it.

```
The `Last-Modified-Version` response header indicates the current version of either a library (for multi-object requests) or an individual object (for single-object requests). If changes are made to a library in a write request, the library’s version number will be increased, any objects modified in the same request will be set to the new version number, and the new version number will be returned in the `Last-Modified-Version` header.
```

Where: https://www.zotero.org/support/dev/web_api/v3/syncing, § Version Numbers › Last-Modified-Version (page Last updated 2022-08-14). Read in: Local API page, Zotero 10 for Developers page. Record id `Z2-last-modified-version-semantics`.

**110.** format=versions returns a JSON map of objectKey -> version, unlimited by result count.

```
`format=versions` is similar to `format=keys`, but instead of returning a newline-delimited list of object keys, it returns a JSON object with object versions keyed by object keys:

    {
      "<itemKey>": <version>,
      "<itemKey>": <version>,
      "<itemKey>": <version>
    }

[...] Like `format=keys`, `format=versions` is not limited by a maximum number of results and returns all matching objects by default.
```

Where: https://www.zotero.org/support/dev/web_api/v3/syncing, § Version Numbers › ?format=versions. Read in: Local API page. Record id `Z2-format-versions`.

**111.** format=json puts a version property in each object's data; it equals the top-level version and, for single-object requests, Last-Modified-Version.

```
`format=json` responses will include a `version` property in each object’s editable JSON (the `data` property) indicating the current version of that object. This value will be identical to the `version` property supplied at the top level of the JSON object. For single-object requests, this will also be identical to the value of the `Last-Modified-Version` response header.
```

Where: https://www.zotero.org/support/dev/web_api/v3/syncing, § Version Numbers › JSON version property. Read in: Local API page. Record id `Z2-json-version-property`.

**112.** Recommended delta fetch: GET <type>?since=<version>&format=versions per object type, where <version> is the last completed Last-Modified-Version or 0.

```
    GET <userOrGroupPrefix>/collections?since=<version>&format=versions
    GET <userOrGroupPrefix>/searches?since=<version>&format=versions
    GET <userOrGroupPrefix>/items/top?since=<version>&format=versions&includeTrashed=1
    GET <userOrGroupPrefix>/items?since=<version>&format=versions&includeTrashed=1

[...] `<version>` is the final `Last-Modified-Version` returned from the API for the last successfully completed sync process, or `0` when syncing a library for the first time.
```

Where: https://www.zotero.org/support/dev/web_api/v3/syncing, § Full-Library Syncing › 3) Sync library data › i. Get updated data. Read in: Local API page, Zotero 10 for Developers page. Record id `Z2-sync-recipe-since-versions`.

**113.** ?since= also works on .../tags requests (without format=versions).

```
(The `since` parameter can also be used on `.../tags` requests (without `format=versions`) by clients that don’t download all items and wish to keep a list of all tags in a library up-to-date. It isn’t necessary for clients that download all items to request updated tags directly, as item objects contain all associated tags.)
```

Where: https://www.zotero.org/support/dev/web_api/v3/syncing, § i. Get updated data. Read in: Local API page. Record id `Z2-since-on-tags`.

**114.** Zotero 10 developer page restates: local versions replace synced versions in object JSON, format=versions, since=, and Last-Modified-Version; ID change means discard/reconcile cache.

```
Version fields in local API responses — object JSON, `format=versions`, `since=` filtering, and `Last-Modified-Version` — now report a new local version rather than the synced version, which didn’t reflect local changes and was 0 for unsynced objects.
```

Where: https://www.zotero.org/support/dev/zotero_10_for_developers, § Local HTTP server and local API. Read in: Local API page, Zotero 10 for Developers page. Recorded under ids: `Z2-z10dev-summary`, `Z2-local-versions-replace-synced-z10`.

**115.** Local API returns full result sets by default; limit/start and Link headers still work.

```
Results are not paginated by default. The local API will return the full set of matching objects in one response, since nothing has to be transferred over the network. The `limit` and `start` parameters still work if you want them, and `Link` headers are still included.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, intro bullet list. Read in: Local API page, Zotero 10 for Developers page. Recorded under ids: `Z2-no-default-pagination`, `Z5-local-no-default-pagination`.

**116.** Responses carry Zotero-Schema-Version for the local instance's schema.

```
Responses include a `Zotero-Schema-Version` header reflecting the schema version of the local Zotero instance, which may lag behind or run ahead of the version served by the Web API.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, intro (after the 'also supports' list). Read in: Local API page, Zotero 10 for Developers page. Record id `Z2-schema-version-header`.

**117.** ?since=<version> returns only objects modified after the given library version, as previously returned in Last-Modified-Version.

```
since       integer         0         Return only objects modified after the specified library version, returned in a previous Last-Modified-Version header. See Syncing for more info.
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics, heading "Search Parameters". Read in: Basics page. Record id `Z2-since-parameter`.

**118.** Multi-object reads return Last-Modified-Version (library version); If-Modified-Since-Version yields 304 when unchanged; single-object conditional GETs are not supported.

```
Multi-object requests (e.g., /users/1/items) return a Last-Modified-Version header with the current library version. If a If-Modified-Since-Version: <libraryVersion> header is passed with a subsequent multi-object read request and data has not changed in the library since the specified version, the API will return 304 Not Modified instead of 200. (Single-object conditional requests are not currently supported, but will be supported in the future.)
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics, heading "Caching". Read in: Basics page, zotero-schema commit 55a1312. Recorded under ids: `Z2-last-modified-version-and-conditional-get`, `Z2-last-modified-version-and-304`.

**119.** The basics page itself states the partition rule: Zotero 10+ local versions are unrelated to Web API versions, so cached data must be partitioned by server ID.

```
Conditional requests work the same way against the local API, but local responses are already inexpensive to produce, so aggressive caching on the client side is less important. The ?since= parameter is also supported and is the preferred way to fetch only changed objects from a large local library. Note that in Zotero 10+, local versions are unrelated to the versions in this API, so clients must partition cached data by server ID. See Object Versions.
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics, heading "Caching" (last paragraph). Read in: Basics page. Record id `Z2-partition-rule-on-basics-page`.

**120.** Every Zotero 10+ local response carries Zotero-Server-ID, a database-resident instance ID stable across restarts/upgrades; a different ID means different versions and keys.

```
In Zotero 10+, every local API response includes a Zotero-Server-ID header containing a string that identifies the Zotero instance being talked to:

    Zotero-Server-ID: sPMHtLD6HHBd

The ID is stored in the Zotero database, so it follows the user’s data rather than the installation, and it stays the same across restarts and upgrades. A different ID means a different database and therefore a different set of object versions and keys.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, heading "Server ID". Read in: Basics page. Record id `Z2-server-id-header`.

**121.** Zotero 10+ local versions increment once per library per transaction on any save/delete (user, sync, or local API), and apply to every place versions appear.

```
In Zotero 10+, data object versions returned by the local API are maintained locally, not by the sync server. They’re incremented once per library per transaction whenever an object in that library is saved or deleted, whether the change comes from the user, a sync, or a local API write.

Local versions in Zotero 10+ therefore have no relation to Web API versions, and no relation to the local versions reported by any other Zotero instance. This applies everywhere versions appear: the version property of object JSON, Last-Modified-Version response headers, format=versions responses, ?since= filtering, and the If-Unmodified-Since-Version and per-object version preconditions used for writes.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, heading "Object Versions". Read in: Basics page. Record id `Z2-local-object-versions`.

**122.** The local API imposes no default or maximum limit; omitting limit returns all matches in one response.

```
The local API does not impose a default or maximum limit. If limit is omitted, all matching objects are returned in one response. Pagination parameters and Link headers still work for clients that want them.
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics, heading "Sorting and Pagination Parameters". Read in: Basics page. Record id `Z2-local-no-default-limit`.

**123.** A 412 on a Zotero-Server-ID mismatch means a different instance; discard cached data including versions and restart with the new ID.

```
A `412` means the client is talking to a Zotero instance other than the one its cached data came from. Discard cached data, including versions, and start over with the new ID.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api § Server ID. Read in: Zotero 10 for Developers page. Record id `Z2-412-means-different-instance`.

**124.** Persistent clients must partition cached data by server ID and treat Web API data as its own partition.

```
Clients that store data between runs should partition it by server ID. The Web API does not currently provide or validate `Zotero-Server-ID`, but it will in the future, so treat Web API data as belonging to its own partition.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api § Server ID. Read in: Zotero 10 for Developers page. Record id `Z2-partition-rule`.

**125.** ?since=<libraryVersion> returns only objects modified after that library version, as returned in a previous Last-Modified-Version header.

```
`since` integer `0` Return only objects modified after the specified library version, returned in a previous `Last-Modified-Version` header. See Syncing for more info.
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics § Search Parameters. Read in: Zotero 10 for Developers page. Record id `Z2-since-parameter-definition`.

**126.** format=versions returns a JSON object mapping object keys to versions for collection/item/search multi-object requests, with no result limit.

```
`versions`, valid for multi-object collection, item, and search requests, will return a JSON object with Zotero object keys as keys and object versions as values. Like `keys`, `versions` mode has no default or maximum limit.
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics § General Parameters (format). Read in: Zotero 10 for Developers page. Record id `Z2-format-versions-definition`.

**127.** ?since= is the preferred way to fetch changes from a large local library, and Zotero 10 local versions require partitioning cached data by server ID.

```
Conditional requests work the same way against the local API, but local responses are already inexpensive to produce, so aggressive caching on the client side is less important. The `?since=` parameter is also supported and is the preferred way to fetch only changed objects from a large local library. Note that in Zotero 10+, local versions are unrelated to the versions in this API, so clients must partition cached data by server ID.
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics § Caching. Read in: Zotero 10 for Developers page. Record id `Z2-since-preferred-locally-partition`.

**128.** GET <prefix>/deleted?since=<version> returns keys of deleted collections, searches, items and tag names since that version.

```
GET <userOrGroupPrefix>/deleted?since=<version> [...] { "collections": [ "<collectionKey>" ], "searches": [ "<searchKey>" ], "items": [ "<itemKey>", "<itemKey>" ], "tags": [ "<tagName>", "<tagName>" ] }
```

Where: https://www.zotero.org/support/dev/web_api/v3/syncing § ii. Get deleted data. Read in: Zotero 10 for Developers page. Record id `Z2-deleted-since-endpoint`.

**129.** Clients should compare Last-Modified-Version across the sync's responses and restart if it changed mid-run.

```
For each response from the API, check the `Last-Modified-Version` to see if it has changed since the `Last-Modified-Version` returned from the first request (e.g., `collections?since=`). If it has, restart the process of retrieving updated and deleted data, waiting increasing amounts of time between restarts to give the other client the opportunity to finish.
```

Where: https://www.zotero.org/support/dev/web_api/v3/syncing § iii. Check for concurrent remote updates. Read in: Zotero 10 for Developers page. Record id `Z2-concurrent-update-check`.

**130.** ?since=<version> returns only objects modified after that library version, as returned in a prior Last-Modified-Version header.

```
since | integer | 0 | Return only objects modified after the specified library version, returned in a previous Last-Modified-Version header. See Syncing for more info.
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics, heading "Search Parameters" (Last updated 2026-07-29). Read in: zotero-schema commit 55a1312. Record id `Z2-since-parameter`.

**131.** On reads the header is optional but must match if sent (412 otherwise); a 412 means discard all cached data and start over with the new ID.

```
On read requests, the header is optional. If provided, it must match the current server, or the request is rejected with 412 Precondition Failed.
...
A 412 means the client is talking to a Zotero instance other than the one its cached data came from. Discard cached data, including versions, and start over with the new ID.
```

Where: local_api, heading "Server ID". Read in: zotero-schema commit 55a1312. Record id `Z2-server-id-read-optional-412`.

**132.** Group metadata endpoints report the synced group version; objects inside group libraries use local versions.

```
Group metadata is the exception: <userOrGroupPrefix>/groups and /groups/<groupID> report the synced group version, which has no local counterpart. Objects within group libraries — their items, collections, and searches — use local versions like all others.
```

Where: local_api, heading "Object Versions". Read in: zotero-schema commit 55a1312. Record id `Z2-group-metadata-exception`.

**133.** Live: format=versions&since=535 returned Last-Modified-Version 540 with three entries; If-Modified-Since-Version: 540 gave 304; a wrong Zotero-Server-ID on a read gave 412.

```
Last-Modified-Version: 540
Zotero-Server-ID: 6LpvURP2E933
{'FFGWM8B6': 540, '27MDQHEI': 539, 'VYSQYFG3': 536}
--- If-Modified-Since-Version conditional GET ---
HTTP 304
--- Zotero-Server-ID mismatch on read -> expect 412 ---
HTTP 412
```

Where: GET http://localhost:23119/api/users/0/items?format=versions&since=535 ; same with header If-Modified-Since-Version: 540 ; GET /api/ with header Zotero-Server-ID: WRONGIDXXXXX, observed 2026-09-05 on Zotero 10.0.1. Read in: zotero-schema commit 55a1312. Record id `Z2-live-versions-304-412`.

### Z3. Full-text endpoints

46 facts, deduplicated by quote.

**134.** The full-text endpoints exist in the local API too, and under Zotero 10+ every version they return is a local version, not a server version.

```
These methods are also available in the local API. In Zotero 10+, the versions returned are local versions rather than server versions.
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content, intro paragraph under 'Zotero Web API Full-Text Content Requests'. Read in: Full-Text Content page, Write Requests page, Basics page, Zotero 10 for Developers page, zotero-schema commit 55a1312. Recorded under ids: `Z3-fulltext-local-versions`, `Z3-fulltext-local-availability`, `Z3-local-fulltext-versions`, `Z3-local-availability-and-versions`.

**135.** GET <userOrGroupPrefix>/fulltext?since=<version> returns a JSON map of itemKey to full-text version with a Last-Modified-Version library-version header; the client then fetches content for each item whose version exceeds its stored one.

```
For each item with a full-text content version greater than stored locally, get the item’s full-text content, as described below.
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content, 'Getting new full-text content' (request 'GET <userOrGroupPrefix>/fulltext?since=<version>', response 'Last-Modified-Version: <library version>' and '{ "<itemKey>": <version>, ... }'). Read in: Full-Text Content page, Write Requests page. Recorded under ids: `Z3-get-new-fulltext-since`, `Z3-fulltext-since-listing`.

**136.** Omitting the since parameter on GET /fulltext is a 400 Bad Request.

```
The 'since' parameter was not provided.
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content, 'Getting new full-text content', Common responses table, 400 Bad Request row. Read in: Full-Text Content page. Record id `Z3-since-required-400`.

**137.** GET <userOrGroupPrefix>/items/<itemKey>/fulltext (itemKey must be an attachment) returns JSON with content plus page/char counts, and its Last-Modified-Version header is the version of that item's full-text content, not the library version.

```
Last-Modified-Version: <version of item's full-text content>
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content, 'Getting an item’s full-text content' (response headers block; request 'GET <userOrGroupPrefix>/items/<itemKey>/fulltext'; '<itemKey> should correspond to an existing attachment item.'). Read in: Full-Text Content page. Record id `Z3-get-item-fulltext-header`.

**138.** PDFs report indexedPages/totalPages; text documents report indexedChars/totalChars.

```
indexedChars and totalChars are used for text documents, while indexedPages and totalPages are used for PDFs.
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content, 'Getting an item’s full-text content' (example body '{ "content": "This is full-text content.", "indexedPages": 50, "totalPages": 50 }'). Read in: Full-Text Content page, Write Requests page. Recorded under ids: `Z3-indexedPages-vs-indexedChars`, `Z3-fulltext-get-item-fields`.

**139.** A 404 from GET /items/<itemKey>/fulltext is ambiguous: either the item does not exist or it has no full-text content.

```
The item wasn't found, or no full-text content was found for the given item.
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content, 'Getting an item’s full-text content', Common responses table, 404 Not Found row. Read in: Full-Text Content page, Write Requests page. Recorded under ids: `Z3-get-404-meaning`, `Z3-fulltext-get-404-meaning`.

**140.** PUT <userOrGroupPrefix>/items/<itemKey>/fulltext with a JSON body sets an attachment's full-text content and returns 204; the body must carry the chars or pages counters matching the document type.

```
For text documents, include indexedChars and totalChars. For PDFs, include indexedPages and totalPages.
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content, 'Setting an item’s full-text content' (request 'PUT <userOrGroupPrefix>/items/<itemKey>/fulltext', '204 No Content, The item's full-text content was updated.'). Read in: Full-Text Content page, Write Requests page. Recorded under ids: `Z3-put-fulltext`, `Z3-fulltext-put`.

**141.** PUT fulltext returns 404 when the key is missing or is not an attachment, and 400 for invalid JSON.

```
The item wasn't found or was not an attachment.
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content, 'Setting an item’s full-text content', Common responses table (404 row; 400 row reads 'Invalid JSON was provided.'). Read in: Full-Text Content page. Record id `Z3-put-404-400`.

**142.** The page models content as one string plus page/char counters and documents no page separator or per-page structure (gap for Z3's 'page separator').

```
"content": "This is full-text content.",
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content, response example under 'Getting an item’s full-text content' (no 'separator', 'form feed' or 'page break' text on this page, local_api, or basics). Read in: Full-Text Content page. Record id `Z3-content-single-string-no-separator`.

**143.** Full-text search is not a fulltext endpoint; it is the items quicksearch with qmode=everything.

```
Quick search mode. To include full-text content, use everything. Searching of other fields will be possible in the future.
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics#search_parameters, 'Search Parameters (Items Endpoints)', qmode row (linked from fulltext_content 'Searching for items by full-text content': 'See the q and qmode search parameters.'). Read in: Full-Text Content page. Record id `Z3-search-fulltext-qmode`.

**144.** The local API adds a bulk POST /fulltext of up to 10 keyed entries that returns the standard multi-object result and requires If-Unmodified-Since-Version.

```
POST <userOrGroupPrefix>/fulltext accepts an array of up to 10 entries, each with a key property, returning the same result object as other multi-object writes. Bulk writes require If-Unmodified-Since-Version.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api#full-text_content, 'Full-Text Content'. Read in: Full-Text Content page. Record id `Z3-local-bulk-fulltext-post`.

**145.** Local /fulltext?since= and Last-Modified-Version values are local versions (must be partitioned by server ID), and attachments of unindexed content types return 400.

```
The versions returned by GET <userOrGroupPrefix>/fulltext?since=<version> and in Last-Modified-Version are local versions, so partitioning is essential. Items whose content type Zotero doesn’t index return 400.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api#full-text_content, 'Full-Text Content'. Read in: Full-Text Content page, Write Requests page. Recorded under ids: `Z3-local-fulltext-versions-partition-400`, `Z3-fulltext-local-versions-400`.

**146.** Local API additionally accepts POST <prefix>/fulltext with up to 10 keyed entries (multi-object result format), requiring If-Unmodified-Since-Version.

```
PUT <userOrGroupPrefix>/items/<itemKey>/fulltext sets an attachment’s full-text content as documented in Full-Text Content, and POST <userOrGroupPrefix>/fulltext accepts an array of up to 10 entries, each with a key property, returning the same result object as other multi-object writes. Bulk writes require If-Unmodified-Since-Version.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, H2 'Full-Text Content'. Read in: Write Requests page. Record id `Z3-fulltext-local-bulk-post`.

**147.** Page separator is NOT documented on any Zotero doc page; the PDF extractor (zotero/pdf-worker getFulltext, called by Zotero.Fulltext) ends each page with '\\n\\n' and inserts a form feed '\\f' between pages (not after the last), then NFC-normalises.

```
text.push('\f');
```

Where: https://github.com/zotero/pdf-worker/blob/8fb70af4000873561c82b2f4eb88be190efb9979/src/pdf/index.js, async function getFulltext (lines 463-503; the call site is chrome/content/zotero/xpcom/fulltext.js line 651 'await Zotero.PDFWorker.getFullText(itemID, allPages ? null : maxPages)'). Read in: Write Requests page. Record id `Z3-page-separator-src`.

**148.** GET <prefix>/fulltext?since=<version> returns a JSON map itemKey -> full-text version with Last-Modified-Version; since is mandatory (400 if absent).

```
    GET <userOrGroupPrefix>/fulltext?since=<version>

    Content-Type: application/json
    Last-Modified-Version: <library version>

    {
        "<itemKey>": <version>,
        "<itemKey>": <version>,
        "<itemKey>": <version>
    }

For each item with a full-text content version greater than stored locally, get the item’s full-text content, as described below.

| `400 Bad Request` | The 'since' parameter was not provided.       |
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content, § Getting new full-text content. Read in: Local API page. Record id `Z3-get-fulltext-since`.

**149.** GET <prefix>/items/<itemKey>/fulltext returns {content, indexedPages, totalPages} for PDFs (indexedChars/totalChars for text) with Last-Modified-Version = the content's version.

```
    GET <userOrGroupPrefix>/items/<itemKey>/fulltext

`<itemKey>` should correspond to an existing attachment item.

    Content-Type: application/json
    Last-Modified-Version: <version of item's full-text content>

    {
        "content": "This is full-text content.",
        "indexedPages": 50,
        "totalPages": 50
    }

`indexedChars` and `totalChars` are used for text documents, while `indexedPages` and `totalPages` are used for PDFs.
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content, § Getting an item’s full-text content. Read in: Local API page, Zotero 10 for Developers page. Recorded under ids: `Z3-get-item-fulltext`, `Z3-get-item-fulltext-shape`.

**150.** 404 on GET fulltext means the item was not found OR it has no full-text content.

```
| `404 Not Found`  | The item wasn't found, or no full-text content was found for the given item. |
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content, § Getting an item’s full-text content. Read in: Local API page. Record id `Z3-404-meaning`.

**151.** PUT <prefix>/items/<itemKey>/fulltext sets content with indexedChars/totalChars (text) or indexedPages/totalPages (PDF); 204 on success, 400 bad JSON, 404 not found / not an attachment.

```
    PUT <userOrGroupPrefix>/items/<itemKey>/fulltext
    Content-Type: application/json

    {
        "content": "This is full-text content.",
        "indexedChars": 26,
        "totalChars": 26
    }

`<itemKey>` should correspond to an existing attachment item.

For text documents, include `indexedChars` and `totalChars`. For PDFs, include `indexedPages` and `totalPages`.

| `204 No Content`  | The item's full-text content was updated.       |
| `400 Bad Request` | Invalid JSON was provided.                      |
| `404 Not Found`   | The item wasn't found or was not an attachment. |
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content, § Setting an item’s full-text content. Read in: Local API page. Record id `Z3-put-fulltext`.

**152.** Locally, PUT single fulltext works as documented and POST <prefix>/fulltext accepts up to 10 keyed entries; bulk writes require If-Unmodified-Since-Version.

```
`PUT <userOrGroupPrefix>/items/<itemKey>/fulltext` sets an attachment’s full-text content as documented in [Full-Text Content](/support/dev/web_api/v3/fulltext_content), and `POST <userOrGroupPrefix>/fulltext` accepts an array of up to 10 entries, each with a `key` property, returning the same result object as other multi-object writes. Bulk writes require `If-Unmodified-Since-Version`.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, § Full-Text Content. Read in: Local API page. Record id `Z3-local-bulk-post`.

**153.** Page claims fulltext ?since= and Last-Modified-Version are local versions (partition needed); unindexable content types return 400. (See notes: live 10.0.1 contradicts the version claim.)

```
The versions returned by `GET <userOrGroupPrefix>/fulltext?since=<version>` and in `Last-Modified-Version` are local versions, so partitioning is essential. Items whose content type Zotero doesn’t index return `400`.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, § Full-Text Content. Read in: Local API page. Record id `Z3-local-fulltext-versions-and-400`.

**154.** fulltext_content page states the methods work locally and that Zotero 10+ returns local versions.

```
These methods are also available in the [local API](/support/dev/web_api/v3/local_api#full-text_content). In Zotero 10+, the versions returned are local versions rather than server versions.
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content, intro. Read in: Local API page. Record id `Z3-fulltext-page-local-note`.

**155.** Neither fulltext_content nor local_api specifies how pages are delimited inside `content`; the only shape statement is the pages/chars stats sentence.

```
`indexedChars` and `totalChars` are used for text documents, while `indexedPages` and `totalPages` are used for PDFs.
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content, § Getting an item’s full-text content (absence of any separator statement verified by grep of both pages for 'separator', '\\f', '\\n'). Read in: Local API page. Record id `Z3-page-separator-DOC-SILENT`.

**156.** SOURCE-DERIVED: pdf-worker joins pages with '\\n\\n' after each page and a form feed '\\f' between pages (not after the last), then trims and NFC-normalizes; extractedPages/totalPages become indexedPages/totalPages.

```
		text.push('\n\n');
		if (i !== pageIndexes.length - 1) {
			text.push('\f');
		}
	}

	// Normalize text by precomposing characters and accents into single composed characters
	// to prevent indexing issues
	text = text.join('').trim().normalize('NFC');

	return {
		text,
		extractedPages: pageIndexes.length,
		totalPages: actualCount
	};
```

Where: https://raw.githubusercontent.com/zotero/pdf-worker/master/src/pdf/index.js @ 8fb70af4, function getFulltext(); consumed by zotero/zotero chrome/content/zotero/xpcom/fulltext.js indexPDF() ('var stats = { indexedPages: extractedPages, totalPages };'). Read in: Local API page. Record id `Z3-page-separator-SOURCE`.

**157.** SOURCE-DERIVED: local GET fulltext returns 404 when the item is missing, is not a file attachment, has a non-cached MIME type, or its .zotero-ft-cache file does not exist; version comes from fulltextItems.version.

```
		let item = await Zotero.Items.getByLibraryAndKeyAsync(libraryID, pathParams.itemKey);
		if (!item || !item.isFileAttachment() || !Zotero.Fulltext.isCachedMIMEType(item.attachmentContentType)) {
			return _404;
		}
		let file = Zotero.Fulltext.getItemCacheFile(item);
		if (!file.exists()) {
			return _404;
		}
		let { indexedPages, totalPages, indexedChars, totalChars, version } = await Zotero.DB.rowQueryAsync(
			"SELECT indexedPages, totalPages, indexedChars, totalChars, version FROM fulltextItems WHERE itemID=?",
```

Where: https://raw.githubusercontent.com/zotero/zotero/main/chrome/content/zotero/xpcom/server/server_localAPI.js @ fc17dcd2, Zotero.Server.LocalAPI.ItemFullText.run(). Read in: Local API page. Record id `Z3-404-conditions-SOURCE`.

**158.** SOURCE-DERIVED: local GET /fulltext?since= selects fulltextItems.version and returns every row when since=0 (including version-0 rows); non-integer since gives 400.

```
		let rows = await Zotero.DB.queryAsync(
			"SELECT I.key, FI.version "
				+ "FROM fulltextItems FI JOIN items I USING (itemID) "
				+ "WHERE libraryID=?1 AND (?2=0 OR FI.version>?2)",
			[libraryID, since]
		);
```

Where: https://raw.githubusercontent.com/zotero/zotero/main/chrome/content/zotero/xpcom/server/server_localAPI.js @ fc17dcd2, Zotero.Server.LocalAPI.FullText.run(). Read in: Local API page. Record id `Z3-since-sql-SOURCE`.

**159.** GET <prefix>/fulltext?since=<version> returns itemKey→version for changed full-text content; since is mandatory (400 otherwise).

```
GET <userOrGroupPrefix>/fulltext?since=<version>
    Content-Type: application/json
    Last-Modified-Version: <library version>

    {
        "<itemKey>": <version>,
        "<itemKey>": <version>,
        "<itemKey>": <version>
    }

For each item with a full-text content version greater than stored locally, get the item’s full-text content, as described below.

  200 OK             Full-text content was successfully retrieved.
  400 Bad Request    The 'since' parameter was not provided.
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content, heading "Getting new full-text content". Read in: Basics page. Record id `Z3-fulltext-since-endpoint`.

**160.** GET <prefix>/items/<itemKey>/fulltext returns content plus indexedPages/totalPages (PDF) or indexedChars/totalChars (text), with Last-Modified-Version = the content's version.

```
GET <userOrGroupPrefix>/items/<itemKey>/fulltext

<itemKey> should correspond to an existing attachment item.

    Content-Type: application/json
    Last-Modified-Version: <version of item's full-text content>

    {
        "content": "This is full-text content.",
        "indexedPages": 50,
        "totalPages": 50
    }

indexedChars and totalChars are used for text documents, while indexedPages and totalPages are used for PDFs.
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content, heading "Getting an item’s full-text content". Read in: Basics page, zotero-schema commit 55a1312. Recorded under ids: `Z3-get-item-fulltext`, `Z3-get-item-fulltext-shape`.

**161.** On GET, 404 means either the item does not exist or it has no full-text content.

```
404 Not Found      The item wasn't found, or no full-text content was found for the given item.
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content, heading "Getting an item’s full-text content" (Common responses table). Read in: Basics page. Record id `Z3-get-404-meaning`.

**162.** PUT <prefix>/items/<itemKey>/fulltext sets content with chars stats for text or pages stats for PDFs; 204 on success, 404 if not found or not an attachment.

```
PUT <userOrGroupPrefix>/items/<itemKey>/fulltext
    Content-Type: application/json

    {
        "content": "This is full-text content.",
        "indexedChars": 26,
        "totalChars": 26
    }

<itemKey> should correspond to an existing attachment item.

For text documents, include indexedChars and totalChars. For PDFs, include indexedPages and totalPages.

  204 No Content     The item's full-text content was updated.
  400 Bad Request    Invalid JSON was provided.
  404 Not Found      The item wasn't found or was not an attachment.
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content, heading "Setting an item’s full-text content". Read in: Basics page. Record id `Z3-put-fulltext`.

**163.** Locally, POST <prefix>/fulltext accepts up to 10 keyed entries and requires If-Unmodified-Since-Version; unindexable content types return 400.

```
PUT <userOrGroupPrefix>/items/<itemKey>/fulltext sets an attachment’s full-text content as documented in Full-Text Content, and POST <userOrGroupPrefix>/fulltext accepts an array of up to 10 entries, each with a key property, returning the same result object as other multi-object writes. Bulk writes require If-Unmodified-Since-Version.

The versions returned by GET <userOrGroupPrefix>/fulltext?since=<version> and in Last-Modified-Version are local versions, so partitioning is essential. Items whose content type Zotero doesn’t index return 400.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, heading "Full-Text Content". Read in: Basics page, zotero-schema commit 55a1312. Recorded under ids: `Z3-local-bulk-fulltext-write`, `Z3-local-bulk-post-and-400`.

**164.** Source: local GET fulltext 404s when the item is missing, not a file attachment, of a non-cached MIME type, or has no .zotero-ft-cache file; content is the raw cache file text.

```
let item = await Zotero.Items.getByLibraryAndKeyAsync(libraryID, pathParams.itemKey);
		if (!item || !item.isFileAttachment() || !Zotero.Fulltext.isCachedMIMEType(item.attachmentContentType)) {
			return _404;
		}
		let file = Zotero.Fulltext.getItemCacheFile(item);
		if (!file.exists()) {
			return _404;
		}
		let { indexedPages, totalPages, indexedChars, totalChars, version } = await Zotero.DB.rowQueryAsync(
			"SELECT indexedPages, totalPages, indexedChars, totalChars, version FROM fulltextItems WHERE itemID=?",
			item.id
		);
		return [
			200,
			{
				'Content-Type': 'application/json',
				'Last-Modified-Version': version,
			},
			JSON.stringify(
				{
					content: await Zotero.File.getContentsAsync(file),
```

Where: https://github.com/zotero/zotero/blob/fc17dcd24ad34686cb24e6b3ffb06a6a7a5e0e5d/chrome/content/zotero/xpcom/server/server_localAPI.js, lines 1423-1442 (ItemFullText.run); cache file name from fulltext.js line 27: this.__defineGetter__("fulltextCacheFile", function () { return '.zotero-ft-cache'; });. Read in: Basics page. Record id `Z3-local-404-source-and-raw-cache`.

**165.** No doc page defines a page separator; the cache text comes from pdf-worker getFulltext, which appends '\\n\\n' after each page and a form feed '\\f' between pages, then trims and NFC-normalizes.

```
		text.push('\n\n');
		if (i !== pageIndexes.length - 1) {
			text.push('\f');
		}
	}

	// Normalize text by precomposing characters and accents into single composed characters
	// to prevent indexing issues
	text = text.join('').trim().normalize('NFC');
```

Where: https://github.com/zotero/pdf-worker/blob/8fb70af4000873561c82b2f4eb88be190efb9979/src/pdf/index.js, function getFulltext, lines 495-503. Chain: zotero/zotero fulltext.js lines 647-660 (`await Zotero.PDFWorker.getFullText(itemID, ...)` then `await Zotero.File.putContentsAsync(cacheFilePath, text)`) → local API returns that file verbatim (Z3-local-404-source-and-raw-cache). Not a documented contract; content PUT by other clients carries no separator guarantee.. Read in: Basics page. Record id `Z3-page-separator-not-documented-source-chain`.

**166.** GET <prefix>/fulltext?since=<version> returns a map of item keys to full-text content versions; since is mandatory (400 if absent).

```
GET <userOrGroupPrefix>/fulltext?since=<version> Content-Type: application/json Last-Modified-Version: <library version> { "<itemKey>": <version>, "<itemKey>": <version>, "<itemKey>": <version> } For each item with a full-text content version greater than stored locally, get the item’s full-text content, as described below. [...] `400 Bad Request` The 'since' parameter was not provided.
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content § Getting new full-text content. Read in: Zotero 10 for Developers page. Record id `Z3-get-fulltext-since`.

**167.** A 404 on GET .../fulltext means either the item does not exist or it has no full-text content.

```
`404 Not Found` The item wasn't found, or no full-text content was found for the given item.
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content § Getting an item’s full-text content (Common responses). Read in: Zotero 10 for Developers page. Record id `Z3-get-fulltext-404-meaning`.

**168.** PUT <prefix>/items/<itemKey>/fulltext sets content with indexedChars/totalChars (text) or indexedPages/totalPages (PDF); 204 on success, 400 bad JSON, 404 not found or not an attachment.

```
PUT <userOrGroupPrefix>/items/<itemKey>/fulltext Content-Type: application/json { "content": "This is full-text content.", "indexedChars": 26, "totalChars": 26 } `<itemKey>` should correspond to an existing attachment item. For text documents, include `indexedChars` and `totalChars`. For PDFs, include `indexedPages` and `totalPages`. [...] `204 No Content` The item's full-text content was updated. `400 Bad Request` Invalid JSON was provided. `404 Not Found` The item wasn't found or was not an attachment.
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content § Setting an item’s full-text content. Read in: Zotero 10 for Developers page. Record id `Z3-put-fulltext`.

**169.** The local API adds POST <prefix>/fulltext for up to 10 entries keyed by item key, requiring If-Unmodified-Since-Version; unindexable content types return 400.

```
`PUT <userOrGroupPrefix>/items/<itemKey>/fulltext` sets an attachment’s full-text content as documented in Full-Text Content, and `POST <userOrGroupPrefix>/fulltext` accepts an array of up to 10 entries, each with a `key` property, returning the same result object as other multi-object writes. Bulk writes require `If-Unmodified-Since-Version`. The versions returned by `GET <userOrGroupPrefix>/fulltext?since=<version>` and in `Last-Modified-Version` are local versions, so partitioning is essential. Items whose content type Zotero doesn’t index return `400`.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api § Full-Text Content. Read in: Zotero 10 for Developers page. Record id `Z3-local-bulk-fulltext-post`.

**170.** None of the fetched Zotero pages specify a page separator inside the full-text `content` string; the only shape given is the example object (grep for separator/form feed/page break across fulltext_content, local_api, basics and the Zotero 10 page: no hits).

```
{ "content": "This is full-text content.", "indexedPages": 50, "totalPages": 50 }
```

Where: https://www.zotero.org/support/dev/web_api/v3/fulltext_content § Getting an item’s full-text content (absence noted across all fetched pages). Read in: Zotero 10 for Developers page. Record id `Z3-page-separator-not-documented`.

**171.** Zotero 10 rewrote full-text search on SQLite FTS5, dropped fulltextWords/fulltextItemWords, and keeps indexes in a separate attached database 'ftindex'.

```
Full-text content search was rewritten on SQLite FTS5. The `fulltextWords` and `fulltextItemWords` tables were dropped from zotero.sqlite; the content and note indexes live in a separate database attached as `ftindex`. Various `Zotero.FullText` methods were removed or replaced.
```

Where: https://www.zotero.org/support/dev/zotero_10_for_developers § Full-text search. Read in: Zotero 10 for Developers page. Record id `Z3-fts5-rewrite-z10`.

**172.** The fulltextWord search condition was removed in favour of fulltextContent backed by a real index.

```
The `fulltextWord` condition was removed. Use `fulltextContent`, which is now backed by a real full-text index and is fast enough for general use.
```

Where: https://www.zotero.org/support/dev/zotero_10_for_developers § Search API. Read in: Zotero 10 for Developers page. Record id `Z3-fulltextWord-condition-removed`.

**173.** Quick search includes full-text content only with qmode=everything.

```
`qmode` `titleCreatorYear`, `everything` `titleCreatorYear` Quick search mode. To include full-text content, use `everything`. Searching of other fields will be possible in the future.
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics § Search Parameters (Items Endpoints). Read in: Zotero 10 for Developers page. Record id `Z3-qmode-everything`.

**174.** On GET, 404 means the item was not found OR it has no full-text content; on PUT, 404 means not found or not an attachment.

```
404 Not Found | The item wasn't found, or no full-text content was found for the given item.
...
404 Not Found | The item wasn't found or was not an attachment.
```

Where: fulltext_content, "Common responses" tables under "Getting an item’s full-text content" and "Setting an item’s full-text content". Read in: zotero-schema commit 55a1312. Record id `Z3-404-meaning`.

**175.** GET /fulltext?since=<version> returns a key→version map of items whose full-text version is newer; omitting since is a 400.

```
GET <userOrGroupPrefix>/fulltext?since=<version>
Content-Type: application/json
Last-Modified-Version: <library version>
{
    "<itemKey>": <version>,
    ...
}
For each item with a full-text content version greater than stored locally, get the item’s full-text content, as described below.
400 Bad Request | The 'since' parameter was not provided.
```

Where: fulltext_content, heading "Getting new full-text content". Read in: zotero-schema commit 55a1312. Record id `Z3-fulltext-since-listing`.

**176.** PUT /items/<key>/fulltext with content plus the chars or pages pair returns 204; invalid JSON is 400.

```
PUT <userOrGroupPrefix>/items/<itemKey>/fulltext
Content-Type: application/json
{
    "content": "This is full-text content.",
    "indexedChars": 26,
    "totalChars": 26
}
<itemKey> should correspond to an existing attachment item.
For text documents, include indexedChars and totalChars. For PDFs, include indexedPages and totalPages.
204 No Content | The item's full-text content was updated.
```

Where: fulltext_content, heading "Setting an item’s full-text content". Read in: zotero-schema commit 55a1312. Record id `Z3-put-fulltext`.

**177.** Live observation (no documentation source): PDF full-text content separates pages with a form-feed character (U+000C)-16 form feeds across a 17-page document.

```
{'content': "'A Threat in the Air\\nHow Stereotypes Shape Intellectual Identity and Performance\\nClaude M. Steele Sta'...", 'indexedPages': 17, 'totalPages': 17}
len 98966 ; form-feed count: 16 ; around first FF: 'ologies, are reserved.\n\n\n\x0cClaude M.\nSteele\nCopyrig'
```

Where: GET http://localhost:23119/api/users/0/items/22AR2P7G/fulltext, response body analysed with Python (content.count('\\f')), Zotero 10.0.1, observed 2026-09-05. Read in: zotero-schema commit 55a1312. Record id `Z3-live-page-separator-form-feed`.

**178.** Live discrepancy: the fulltext endpoint returned Last-Modified-Version 20694 for an attachment whose item version is 0 in a library at version 540, and 432 of 1350 ?since=0 entries are 0, inconsistent with the doc's 'local versions' claim; recorded as observation.

```
HTTP/1.0 200 OK
Content-Type: application/json
Last-Modified-Version: 20694
Zotero-Server-ID: 6LpvURP2E933
... attachment application/pdf imported_url version 0
zero-version entries 432 of 1350
```

Where: GET http://localhost:23119/api/users/0/items/22AR2P7G/fulltext (headers) ; GET /api/users/0/items/22AR2P7G?format=json (version) ; GET /api/users/0/fulltext?since=0, observed 2026-09-05; compare local_api "Full-Text Content": "The versions returned by GET <userOrGroupPrefix>/fulltext?since=<version> and in Last-Modified-Version are local versions". Read in: zotero-schema commit 55a1312. Record id `Z3-live-fulltext-version-discrepancy`.

**179.** Live: an existing stored PDF attachment that is not in the full-text index returns a plain-text 404 'Not found', matching the doc's 'no full-text content' branch.

```
== GET /items/JWZ94GMK/fulltext (PDF) ==
HTTP/1.0 404 Not Found
Content-Type: text/plain
... Not found
== versions entry for JWZ94GMK in /fulltext?since=0 ==
entries 1350 ; JWZ94GMK -> None
```

Where: GET http://localhost:23119/api/users/0/items/JWZ94GMK/fulltext (attachment imported_url application/pdf), observed 2026-09-05. Read in: zotero-schema commit 55a1312. Record id `Z3-live-404-for-unindexed-pdf`.

### Z4. File endpoints

21 facts, deduplicated by quote.

**180.** Locally, /items/<itemKey>/file and /file/view both 302-redirect to a file:// URL of the attachment on disk, while /file/view/url returns that URL as plain text.

```
<userOrGroupPrefix>/items/<itemKey>/file returns a 302 redirect to a file:// URL for the attachment on disk, and /file/view does the same. /file/view/url returns the URL as plain text rather than redirecting.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, intro, 'The local API also supports a few things the Web API does not:' bullet list. Read in: Full-Text Content page, Write Requests page, zotero-schema commit 55a1312. Recorded under ids: `Z4-local-file-endpoints-file-url`, `Z4-file-endpoints-local`.

**181.** On the Web API, GET /users/<userID>/items/<itemKey>/file downloads the stored file and its ETag should equal the attachment item's md5.

```
Check the ETag header of the response to make sure it matches the attachment item’s md5 value. If it doesn’t, check the attachment item again.
```

Where: https://www.zotero.org/support/dev/web_api/v3/file_upload, '1b) Modify an existing attachment' > 'ii. Download the existing file' (request 'GET /users/<userID>/items/<itemKey>/file'). Read in: Full-Text Content page. Record id `Z4-web-file-download-etag`.

**182.** Not on the doc pages: the source returns item.getLocalFileURL() (a file:// URL, not an OS path) for all three routes, with 400 for non-file attachments and 404 for missing items.

```
return [200, 'text/plain', item.getLocalFileURL()];
```

Where: https://github.com/zotero/zotero/blob/fc17dcd24ad34686cb24e6b3ffb06a6a7a5e0e5d/chrome/content/zotero/xpcom/server/server_localAPI.js, Zotero.Server.LocalAPI.ItemFile.run (lines 1265-1268; the /file and /file/view branch is "return [302, { Location: item.getLocalFileURL() }, ''];"). Read in: Write Requests page. Record id `Z4-file-url-form-src`.

**183.** Zotero 10+ local API supports the Web API's three-phase full upload (authorize → POST bytes to /api/local/uploads/<uploadKey> → register), with the file going to Zotero, and no binary diffs.

```
In Zotero 10+, the local API supports the same full-upload flow, with the file going to Zotero rather than to S3. Binary diffs are not supported locally.
```

Where: https://www.zotero.org/support/dev/web_api/v3/file_upload, intro under H1 'Zotero Web API File Uploads'. Read in: Write Requests page. Record id `Z4-file-upload-local-flow`.

**184.** PATCH .../file (partial upload) fails locally with 405.

```
Partial (binary diff) file uploads are not supported. PATCH <userOrGroupPrefix>/items/<itemKey>/file will fail with 405 Method Not Allowed. Upload the full file instead.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, differences bullet list under H1 'Zotero Local API'. Read in: Write Requests page, zotero-schema commit 55a1312. Recorded under ids: `Z4-file-patch-405`, `Z4-no-partial-upload-405`.

**185.** On the Web API, GET .../file returns the file with an ETag that should equal the attachment item's md5.

```
Check the ETag header of the response to make sure it matches the attachment item’s md5 value.
```

Where: https://www.zotero.org/support/dev/web_api/v3/file_upload, H3 'ii. Download the existing file'. Read in: Write Requests page. Record id `Z4-file-download-etag-md5`.

**186.** /file and /file/view respond 302 to a file:// URL on disk; /file/view/url returns that URL as plain text.

```
`<userOrGroupPrefix>/items/<itemKey>/file` returns a `302` redirect to a `file://` URL for the attachment on disk, and `/file/view` does the same. `/file/view/url` returns the URL as plain text rather than redirecting.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, intro, 'The local API also supports a few things the Web API does not:'. Read in: Local API page, Zotero 10 for Developers page. Recorded under ids: `Z4-file-endpoints-file-url`, `Z4-file-endpoints-return-file-url`.

**187.** SOURCE-DERIVED: non-file attachments get 400; the URL is item.getLocalFileURL(); POST/PATCH on /view or /url paths give 405.

```
		if (!item.isFileAttachment()) {
			return [400, 'text/plain', `Not a file attachment: ${item.key}`];
		}
		if (pathname.endsWith('/url')) {
			return [200, 'text/plain', item.getLocalFileURL()];
		}
		return [302, { Location: item.getLocalFileURL() }, ''];
```

Where: https://raw.githubusercontent.com/zotero/zotero/main/chrome/content/zotero/xpcom/server/server_localAPI.js @ fc17dcd2, Zotero.Server.LocalAPI.ItemFile.run(); endpoints registered for /items/:itemKey/file, /file/view, /file/view/url. Read in: Local API page. Record id `Z4-file-endpoint-SOURCE`.

**188.** Zotero 10+ local API implements the 3-phase upload with the upload going to /api/local/uploads/<uploadKey>; upload keys expire after an hour; step 3 returns 204 with new Last-Modified-Version.

```
1.  `POST <userOrGroupPrefix>/items/<itemKey>/file` with `md5`, `filename`, `filesize`, and `mtime` parameters, and an `If-Match` or `If-None-Match` header, exactly as in the Web API. The response contains a `url` pointing at `/api/local/uploads/<uploadKey>` on the local server, along with `uploadKey`, `contentType`, and empty `prefix` and `suffix` strings. If the file on disk already matches the given MD5, the response is `{ "exists": 1 }` and no upload is needed.
2.  `POST` the file contents to `url`. A successful upload returns `201 Created`. The received bytes must hash to the `md5` provided in the previous step, or the response is `400`. This request doesn’t need `Zotero-Server-ID` or an API key, since the upload key authorizes it. Upload keys expire after an hour.
3.  `POST` to the file endpoint again with `upload=<uploadKey>`, repeating the `If-Match` or `If-None-Match` header. Zotero moves the uploaded file into the attachment’s storage directory and updates the item, returning `204 No Content` with the new library version in `Last-Modified-Version`.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, § File Uploads. Read in: Local API page. Record id `Z4-local-upload-three-phase`.

**189.** Uploads only for imported_file/imported_url attachments (400 otherwise), under 4 GB; PATCH binary-diff uploads return 405.

```
Uploads are only accepted for stored-file attachments (`imported_file` and `imported_url`); other attachment types return `400`. Files must be under 4 GB. [...] Partial (binary diff) file uploads are not supported. `PATCH <userOrGroupPrefix>/items/<itemKey>/file` will fail with `405 Method Not Allowed`. Upload the full file instead.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, § File Uploads and intro bullet list. Read in: Local API page. Record id `Z4-upload-limits`.

**190.** On the Web API, GET /items/<itemKey>/file downloads the file and its ETag should match the item's md5.

```
    GET /users/<userID>/items/<itemKey>/file

Check the `ETag` header of the response to make sure it matches the attachment item’s `md5` value.
```

Where: https://www.zotero.org/support/dev/web_api/v3/file_upload, § 1b) Modify an existing attachment › ii. Download the existing file. Read in: Local API page. Record id `Z4-webapi-file-download-etag`.

**191.** Locally, /file and /file/view return a 302 to a file:// URL for the on-disk attachment; /file/view/url returns that URL as plain text.

```
-   <userOrGroupPrefix>/items/<itemKey>/file returns a 302 redirect to a file:// URL for the attachment on disk, and /file/view does the same. /file/view/url returns the URL as plain text rather than redirecting.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, intro list "The local API also supports a few things the Web API does not:". Read in: Basics page. Record id `Z4-local-file-endpoints`.

**192.** Source: all three paths map to one ItemFile endpoint; non-file attachments get 400, missing items 404, and the returned form is item.getLocalFileURL() (a file:// URL, not a filesystem path).

```
		let item = await Zotero.Items.getByLibraryAndKeyAsync(libraryID, pathParams.itemKey);
		if (!item) return _404;
		if (!item.isFileAttachment()) {
			return [400, 'text/plain', `Not a file attachment: ${item.key}`];
		}
		if (pathname.endsWith('/url')) {
			return [200, 'text/plain', item.getLocalFileURL()];
		}
		return [302, { Location: item.getLocalFileURL() }, ''];
	}
};
Zotero.Server.Endpoints["/api/users/:userID/items/:itemKey/file"] = Zotero.Server.LocalAPI.ItemFile;
Zotero.Server.Endpoints["/api/groups/:groupID/items/:itemKey/file"] = Zotero.Server.LocalAPI.ItemFile;
Zotero.Server.Endpoints["/api/users/:userID/items/:itemKey/file/view"] = Zotero.Server.LocalAPI.ItemFile;
Zotero.Server.Endpoints["/api/groups/:groupID/items/:itemKey/file/view"] = Zotero.Server.LocalAPI.ItemFile;
Zotero.Server.Endpoints["/api/users/:userID/items/:itemKey/file/view/url"] = Zotero.Server.LocalAPI.ItemFile;
Zotero.Server.Endpoints["/api/groups/:groupID/items/:itemKey/file/view/url"] = Zotero.Server.LocalAPI.ItemFile;
```

Where: https://github.com/zotero/zotero/blob/fc17dcd24ad34686cb24e6b3ffb06a6a7a5e0e5d/chrome/content/zotero/xpcom/server/server_localAPI.js, lines 1260-1276 (Zotero.Server.LocalAPI.ItemFile). The docs do not specify the URL's path encoding.. Read in: Basics page. Record id `Z4-file-endpoint-source`.

**193.** On the Web API, GET /users/<userID>/items/<itemKey>/file downloads the file and its ETag should match the item's md5.

```
GET /users/<userID>/items/<itemKey>/file

Check the ETag header of the response to make sure it matches the attachment item’s md5 value. If it doesn’t, check the attachment item again. If the attachment item still has a different hash, the latest version of the file may be available only via WebDAV, not via Zotero File Storage, and it is up to the client how to proceed.
```

Where: https://www.zotero.org/support/dev/web_api/v3/file_upload, heading "ii. Download the existing file". Read in: Basics page. Record id `Z4-web-file-download`.

**194.** Partial (binary-diff) uploads are unsupported locally; PATCH .../file returns 405.

```
Partial (binary diff) file uploads are not supported. `PATCH <userOrGroupPrefix>/items/<itemKey>/file` will fail with `405 Method Not Allowed`. Upload the full file instead.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api (intro differences list). Read in: Zotero 10 for Developers page. Record id `Z4-patch-file-405`.

**195.** Zotero 10+ implements the three-phase upload locally: POST .../file with md5/filename/filesize/mtime (returns url at /api/local/uploads/<uploadKey> or {exists:1}), POST bytes (201; keys expire after an hour), then POST upload=<uploadKey> (204 with new library version).

```
`POST <userOrGroupPrefix>/items/<itemKey>/file` with `md5`, `filename`, `filesize`, and `mtime` parameters, and an `If-Match` or `If-None-Match` header, exactly as in the Web API. The response contains a `url` pointing at `/api/local/uploads/<uploadKey>` on the local server, along with `uploadKey`, `contentType`, and empty `prefix` and `suffix` strings. If the file on disk already matches the given MD5, the response is `{ "exists": 1 }` and no upload is needed. [...] Upload keys expire after an hour. [...] Zotero moves the uploaded file into the attachment’s storage directory and updates the item, returning `204 No Content` with the new library version in `Last-Modified-Version`.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api § File Uploads. Read in: Zotero 10 for Developers page. Record id `Z4-local-upload-flow`.

**196.** Local uploads are accepted only for imported_file/imported_url attachments (others 400) and files must be under 4 GB.

```
Uploads are only accepted for stored-file attachments (`imported_file` and `imported_url`); other attachment types return `400`. Files must be under 4 GB.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api § File Uploads. Read in: Zotero 10 for Developers page. Record id `Z4-upload-stored-files-only-4gb`.

**197.** Zotero 10 requires stored-file paths to be a bare filename after 'storage:'; setters throw on slashes and a schema update strips old full paths.

```
The `attachmentFilename`/`attachmentPath` setters throw if a stored-file path contains a slash. Stored-file paths must be a bare filename after the `storage:` prefix. A schema update strips full paths written by older third-party tools.
```

Where: https://www.zotero.org/support/dev/zotero_10_for_developers § Item data validation. Read in: Zotero 10 for Developers page. Record id `Z4-stored-path-bare-filename`.

**198.** Zotero 10 enables SQLite WAL mode; direct readers must account for -wal/-shm files, and the page steers tools to the local API instead.

```
**WAL mode is enabled**. If your plugin or external tool reads zotero.sqlite directly (which it probably shouldn’t — use the local API instead!), it must account for the `-wal` and `-shm` files — copying the main database file alone can produce a stale or inconsistent snapshot.
```

Where: https://www.zotero.org/support/dev/zotero_10_for_developers § Database changes. Read in: Zotero 10 for Developers page. Record id `Z4-wal-mode-direct-sqlite-warning`.

**199.** Live: the path form is a file:/// URI with the Windows drive letter (file:///D:/Zotero/storage/<KEY>/<filename>), identical in the 302 Location and the text/plain body.

```
== GET /items/FFGWM8B6/file/view/url ==
HTTP/1.0 200 OK
...
Content-Type: text/plain
...
file:///D:/Zotero/storage/FFGWM8B6/270894089_Cognitive_Interviewing_A_Tool_For_Improving_Questionnaire_Design.html
== GET /items/FFGWM8B6/file (no follow) ==
HTTP/1.0 302 undefined
Location: file:///D:/Zotero/storage/FFGWM8B6/270894089_Cognitive_Interviewing_A_Tool_For_Improving_Questionnaire_Design.html
```

Where: GET http://localhost:23119/api/users/0/items/FFGWM8B6/file/view/url and /file and /file/view, Zotero 10.0.1 on Windows, observed from WSL 2026-09-05. Read in: zotero-schema commit 55a1312. Record id `Z4-live-path-form-windows-file-uri`.

**200.** Local three-phase upload: POST /file with md5/filename/filesize/mtime + If-Match/If-None-Match → url at /api/local/uploads/<uploadKey>; POST bytes (201, key expires in an hour); POST /file?upload=<key> → 204 with new library version; only imported_file/imported_url, under 4 GB.

```
POST <userOrGroupPrefix>/items/<itemKey>/file with md5, filename, filesize, and mtime parameters, and an If-Match or If-None-Match header, exactly as in the Web API. The response contains a url pointing at /api/local/uploads/<uploadKey> on the local server, along with uploadKey, contentType, and empty prefix and suffix strings. If the file on disk already matches the given MD5, the response is { "exists": 1 } and no upload is needed.
...
Uploads are only accepted for stored-file attachments (imported_file and imported_url); other attachment types return 400. Files must be under 4 GB.
```

Where: local_api, heading "File Uploads". Read in: zotero-schema commit 55a1312. Record id `Z4-local-upload-flow`.

### Z5. Saved searches and collections

27 facts, deduplicated by quote.

**201.** The local API executes saved searches via /searches/<searchKey>/items; the Web API only exposes search metadata.

```
<userOrGroupPrefix>/searches/<searchKey>/items returns the items matching a saved search. The Web API exposes search metadata but does not actually execute searches.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, intro, 'The local API also supports a few things the Web API does not:' bullet list. Read in: Full-Text Content page, Write Requests page, zotero-schema commit 55a1312. Recorded under ids: `Z5-local-saved-search-execution`, `Z5-saved-search-execution-local`, `Z5-saved-search-execution-local-only`.

**202.** Web API saved-search endpoints are /searches and /searches/<searchKey>, returning metadata only, not results.

```
(Note: Only search metadata is currently available, not search results.)
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics#searches, 'Resources' > 'Searches' table. Read in: Full-Text Content page, Write Requests page. Record id `Z5-web-searches-metadata-only`.

**203.** Collection endpoints are /collections, /collections/top, /collections/<collectionKey>, /collections/<collectionKey>/collections, plus /collections/<collectionKey>/items and .../items/top for members.

```
Subcollections within a specific collection in the library
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics#collections, 'Resources' > 'Collections' table (URI '<userOrGroupPrefix>/collections/<collectionKey>/collections'); 'Items' table rows '<userOrGroupPrefix>/collections/<collectionKey>/items, Items within a specific collection in the library' and '.../items/top, Top-level items within a specific collection in the library'. Read in: Full-Text Content page, Write Requests page. Record id `Z5-collections-endpoints`.

**204.** Local API responses are unpaginated by default (full result set), though limit/start and Link headers still work.

```
Results are not paginated by default. The local API will return the full set of matching objects in one response, since nothing has to be transferred over the network. The limit and start parameters still work if you want them, and Link headers are still included.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, intro bullet list of differences from the Web API. Read in: Full-Text Content page. Record id `Z5-local-no-pagination`.

**205.** Collection membership is written through the item's collections array, not a collection endpoint.

```
Items can be added to or removed from collections via the collections property in the item JSON.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests, H3 'Collection-Item Membership'. Read in: Write Requests page, Basics page. Recorded under ids: `Z5-collection-membership-via-item`, `Z5-collection-writes-and-membership`.

**206.** Local API returns the whole result set by default (no default/max limit); limit/start and Link headers still work.

```
Results are not paginated by default. The local API will return the full set of matching objects in one response, since nothing has to be transferred over the network.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, differences bullet list under H1 'Zotero Local API'. Read in: Write Requests page. Record id `Z5-local-no-pagination`.

**207.** Local-only: <prefix>/searches/<searchKey>/items executes a saved search and returns matching items; the Web API only exposes search metadata.

```
`<userOrGroupPrefix>/searches/<searchKey>/items` returns the items matching a saved search. The Web API exposes search metadata but does not actually execute searches.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, intro, 'The local API also supports a few things the Web API does not:'. Read in: Local API page, Zotero 10 for Developers page. Recorded under ids: `Z5-saved-search-execution`, `Z5-saved-search-execution-endpoint`.

**208.** Saved-search read endpoints: /searches (all) and /searches/<searchKey> (one); Web API returns metadata only.

```
(Note: Only search metadata is currently available, not search results.)

| \<userOrGroupPrefix\>/searches               | All saved searches in the library      |
| \<userOrGroupPrefix\>/searches/\<searchKey\> | A specific saved search in the library |
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics, § Read Requests › Searches. Read in: Local API page. Record id `Z5-searches-metadata-endpoints`.

**209.** Collection read endpoints: /collections, /collections/top, /collections/<key>, /collections/<key>/collections, plus /collections/<key>/items, /items/top and /tags.

```
| \<userOrGroupPrefix\>/collections                               | Collections in the library                                 |
| \<userOrGroupPrefix\>/collections/top                           | Top-level collections in the library                       |
| \<userOrGroupPrefix\>/collections/\<collectionKey\>             | A specific collection in the library                       |
| \<userOrGroupPrefix\>/collections/\<collectionKey\>/collections | Subcollections within a specific collection in the library |
[...]
| \<userOrGroupPrefix\>/collections/\<collectionKey\>/items     | Items within a specific collection in the library           |
| \<userOrGroupPrefix\>/collections/\<collectionKey\>/items/top | Top-level items within a specific collection in the library |
[...]
| \<userOrGroupPrefix\>/collections/\<collectionKey\>/tags           | Tags within a specific collection in the library                       |
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics, § Read Requests › Collections / Items / Tags tables. Read in: Local API page. Record id `Z5-collections-endpoints`.

**210.** Collections are created via POST /collections (name, parentCollection), membership is edited via the item's collections array, deletion needs If-Unmodified-Since-Version, up to 50 per multi-delete.

```
    POST <userOrGroupPrefix>/collections
    Content-Type: application/json
    Zotero-Write-Token: <write token> or If-Unmodified-Since-Version: <last library version>

    [
      {
        "name" : "My Collection",
        "parentCollection" : "QRST9876"
      }
[...]
Items can be added to or removed from collections via the `collections` property in the item JSON.
[...]
    DELETE <userOrGroupPrefix>/collections/<collectionKey>
    If-Unmodified-Since-Version: <last collection version>
[...]
Up to 50 collections can be deleted in a single request.
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests, § Collection Requests. Read in: Local API page. Record id `Z5-collection-writes`.

**211.** Saved searches are created via POST /searches with name + conditions and multi-deleted via DELETE /searches?searchKey=... (max 50).

```
    POST <userOrGroupPrefix>/searches
    Content-Type: application/json
    Zotero-Write-Token: <write token> or If-Unmodified-Since-Version: <last library version>

    [
      {
        "name": "My Search",
        "conditions": [
[...]
Up to 50 searches can be deleted in a single request.

    DELETE <userOrGroupPrefix>/searches?searchKey=<searchKey>,<searchKey>,<searchKey>
    If-Unmodified-Since-Version: <last library version>
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests, § Saved Search Requests. Read in: Local API page. Record id `Z5-search-writes`.

**212.** Local API accepts the same search params but uses Zotero's local quicksearch, so q results may differ from the Web API.

```
The [local API](/support/dev/web_api/v3/local_api) accepts the same search parameters but uses Zotero’s local quicksearch implementation, so the set of items returned by a given `q` value may not match the Web API exactly.
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics, § Searching › Search Parameters. Read in: Local API page. Record id `Z5-local-quicksearch-differs`.

**213.** SOURCE-DERIVED: the saved-search execution route is registered for both user and group prefixes and served by the generic Items endpoint.

```
Zotero.Server.Endpoints["/api/users/:userID/searches/:searchKey/items"] = Zotero.Server.LocalAPI.Items;
Zotero.Server.Endpoints["/api/groups/:groupID/searches/:searchKey/items"] = Zotero.Server.LocalAPI.Items;
```

Where: https://raw.githubusercontent.com/zotero/zotero/main/chrome/content/zotero/xpcom/server/server_localAPI.js @ fc17dcd2. Read in: Local API page. Record id `Z5-search-items-endpoint-SOURCE`.

**214.** The Web API exposes saved-search metadata only (/searches, /searches/<searchKey>), not results.

```
(Note: Only search metadata is currently available, not search results.)

  <userOrGroupPrefix>/searches               All saved searches in the library
  <userOrGroupPrefix>/searches/<searchKey>   A specific saved search in the library
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics, heading "Searches". Read in: Basics page, Zotero 10 for Developers page. Recorded under ids: `Z5-web-searches-metadata-only`, `Z5-web-searches-endpoints-metadata-only`.

**215.** The local API executes a saved search via <prefix>/searches/<searchKey>/items, which the Web API cannot do.

```
-   <userOrGroupPrefix>/searches/<searchKey>/items returns the items matching a saved search. The Web API exposes search metadata but does not actually execute searches.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api, intro list "The local API also supports a few things the Web API does not:" (source: server_localAPI.js line 1218 `Zotero.Server.Endpoints["/api/users/:userID/searches/:searchKey/items"] = Zotero.Server.LocalAPI.Items;`). Read in: Basics page. Record id `Z5-local-search-execution`.

**216.** Collection read endpoints: /collections, /collections/top, /collections/<key>, /collections/<key>/collections, plus /collections/<key>/items and /items/top.

```
  <userOrGroupPrefix>/collections                               Collections in the library
  <userOrGroupPrefix>/collections/top                           Top-level collections in the library
  <userOrGroupPrefix>/collections/<collectionKey>               A specific collection in the library
  <userOrGroupPrefix>/collections/<collectionKey>/collections   Subcollections within a specific collection in the library
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics, heading "Collections" (Items table adds "<userOrGroupPrefix>/collections/<collectionKey>/items Items within a specific collection in the library" and ".../items/top"). Read in: Basics page. Record id `Z5-collections-endpoints`.

**217.** Saved searches are created by POSTing name + conditions (condition/operator/value) to /searches.

```
POST <userOrGroupPrefix>/searches
    Content-Type: application/json
    Zotero-Write-Token: <write token> or If-Unmodified-Since-Version: <last library version>

    [
      {
        "name": "My Search",
        "conditions": [
          {
            "condition": "title",
            "operator": "contains",
            "value": "foo"
          },
          {
            "condition": "date",
            "operator": "isInTheLast",
            "value": "7 days"
          }
        ]
      }
    ]
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests, heading "Creating a Search". Read in: Basics page. Record id `Z5-saved-search-create`.

**218.** Collection endpoints: /collections, /collections/top, /collections/<key>, /collections/<key>/collections, plus /collections/<key>/items and /items/top.

```
<userOrGroupPrefix>/collections Collections in the library <userOrGroupPrefix>/collections/top Top-level collections in the library <userOrGroupPrefix>/collections/<collectionKey> A specific collection in the library <userOrGroupPrefix>/collections/<collectionKey>/collections Subcollections within a specific collection in the library || <userOrGroupPrefix>/collections/<collectionKey>/items Items within a specific collection in the library <userOrGroupPrefix>/collections/<collectionKey>/items/top Top-level items within a specific collection in the library
```

Where: https://www.zotero.org/support/dev/web_api/v3/basics § Collections; § Items. Read in: Zotero 10 for Developers page. Record id `Z5-collections-endpoints`.

**219.** Collections are created via POST /collections (name, parentCollection), updated via PUT /collections/<key>, deleted via DELETE (up to 50 by collectionKey list); item membership is set via the item's collections property.

```
POST <userOrGroupPrefix>/collections Content-Type: application/json Zotero-Write-Token: <write token> or If-Unmodified-Since-Version: <last library version> [ { "name" : "My Collection", "parentCollection" : "QRST9876" } ] || Items can be added to or removed from collections via the `collections` property in the item JSON. || Up to 50 collections can be deleted in a single request. DELETE <userOrGroupPrefix>/collections?collectionKey=<collectionKey>,<collectionKey>,<collectionKey> If-Unmodified-Since-Version: <last library version>
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests § Creating a Collection; § Collection-Item Membership; § Deleting Multiple Collections. Read in: Zotero 10 for Developers page. Record id `Z5-collection-write-endpoints`.

**220.** Saved searches are created via POST /searches with name + conditions[{condition, operator, value}] and deleted via DELETE /searches?searchKey=... (up to 50).

```
POST <userOrGroupPrefix>/searches Content-Type: application/json Zotero-Write-Token: <write token> or If-Unmodified-Since-Version: <last library version> [ { "name": "My Search", "conditions": [ { "condition": "title", "operator": "contains", "value": "foo" }, { "condition": "date", "operator": "isInTheLast", "value": "7 days" } ] } ] || Up to 50 searches can be deleted in a single request. DELETE <userOrGroupPrefix>/searches?searchKey=<searchKey>,<searchKey>,<searchKey>
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests § Creating a Search; § Deleting Multiple Searches. Read in: Zotero 10 for Developers page. Record id `Z5-saved-search-write-endpoints`.

**221.** Zotero 10 searches support condition groups (groupStart/groupEnd with joinMode) and resultLevel (item/attachment/note/annotation); addCondition throws on the legacy required parameter.

```
Searches can now express much more complicated logic using condition groups. Wrap conditions in `groupStart`/`groupEnd` conditions with a `joinMode`. Use `resultLevel` to specify what the search returns (`item`, `attachment`, `note`, or `annotation`) or, within a group, the level at which the group’s conditions match (e.g., ‘items that have a single annotation matching these conditions’). `Zotero.Search#addCondition()` throws if the legacy `required` parameter is truthy. Use a condition group instead.
```

Where: https://www.zotero.org/support/dev/zotero_10_for_developers § Search API. Read in: Zotero 10 for Developers page. Record id `Z5-search-condition-groups-z10`.

**222.** The childNote condition is deprecated; saved searches using it are auto-migrated to note with resultLevel item.

```
The `childNote` condition is deprecated; saved searches containing it are automatically migrated to `note` with a `resultLevel` set to `item`.
```

Where: https://www.zotero.org/support/dev/zotero_10_for_developers § Search API. Read in: Zotero 10 for Developers page. Record id `Z5-childNote-deprecated-migrated`.

**223.** Local API serves only the logged-in user; pass 0 or the real numeric user ID, other IDs return 400.

```
Only data for the locally logged-in user is available. Pass `0` as the user ID or the user’s actual numeric ID, which can be found on the API Keys page. Requests for any other user ID return `400`.
```

Where: https://www.zotero.org/support/dev/web_api/v3/local_api (intro differences list). Read in: Zotero 10 for Developers page. Record id `Z5-user-id-zero`.

**224.** Up to 50 tags can be deleted per request via DELETE /tags?tag=... with '||' separators.

```
Up to 50 tags can be deleted in a single request. DELETE <userOrGroupPrefix>/tags?tag=<URL-encoded tag 1> || <URL-encoded tag 2> || <URL-encoded tag 3> If-Unmodified-Since-Version: <last library version> 204 No Content Last-Modified-Version: <library version>
```

Where: https://www.zotero.org/support/dev/web_api/v3/write_requests § Deleting Multiple Tags. Read in: Zotero 10 for Developers page. Record id `Z5-tags-delete-endpoint`.

**225.** Saved-search metadata endpoints are /searches and /searches/<searchKey>.

```
<userOrGroupPrefix>/searches | All saved searches in the library
<userOrGroupPrefix>/searches/<searchKey> | A specific saved search in the library
```

Where: basics, heading "Searches" (table). Read in: zotero-schema commit 55a1312. Record id `Z5-searches-endpoints`.

**226.** Collections endpoints: /collections, /collections/top, /collections/<key>, /collections/<key>/collections, plus /collections/<key>/items and /collections/<key>/items/top.

```
<userOrGroupPrefix>/collections | Collections in the library
<userOrGroupPrefix>/collections/top | Top-level collections in the library
<userOrGroupPrefix>/collections/<collectionKey> | A specific collection in the library
<userOrGroupPrefix>/collections/<collectionKey>/collections | Subcollections within a specific collection in the library
...
<userOrGroupPrefix>/collections/<collectionKey>/items | Items within a specific collection in the library
<userOrGroupPrefix>/collections/<collectionKey>/items/top | Top-level items within a specific collection in the library
```

Where: basics, headings "Collections" and "Items" (tables). Read in: zotero-schema commit 55a1312. Record id `Z5-collections-endpoints`.

**227.** Live gap: the local library has zero saved searches, so /searches/<key>/items was documented but not exercised.

```
saved searches: 0
[]
```

Where: GET http://localhost:23119/api/users/0/searches?format=json, observed 2026-09-05. Read in: zotero-schema commit 55a1312. Record id `Z5-live-gap-no-saved-searches`.

### Z6. The native `citationKey` field

30 facts, deduplicated by quote.

**228.** No fetched documentation page mentions citationKey (zero hits in basics and types_and_fields); the live api.zotero.org/schema (version 42, fetched 2026-09-04) carries a citationKey field on 37 of 40 item types with en-US label 'Citation Key', and GET /items/new?itemType=journalArticle includes a citationKey key. SOURCE: live API + schema repo, not the docs.

```
"field": "citationKey"
```

Where: https://api.zotero.org/schema (itemTypes[].fields[] entries) and https://api.zotero.org/items/new?itemType=journalArticle; the same '"field": "citationKey"' lines appear in the patch of https://github.com/zotero/zotero-schema/commit/55a13120bab31e95d6dc88a82fbfa4bbb60e069c. Read in: Full-Text Content page, Write Requests page. Recorded under ids: `Z6-docs-silent-schema-has-citationKey`, `Z6-citationKey-native-schema`.

**229.** citationKey first entered schema.json on 2022-03-03 in the commit that added the preprint item type (preprint only; the file's version field read 14 both before and after, so the version bump shipped later). SOURCE: zotero/zotero-schema history, not the docs.

```
Add `preprint` item type (closes zotero/zotero-bits#88)
```

Where: https://github.com/zotero/zotero-schema/commit/187305727c5866aef7004fdc8d5ec577a0969bc7 (commit subject; bisect over 69 schema.json commits: parent 97e0a8ef has no citationKey, this commit has it on ['preprint']; later dataset and standard also carried it). Read in: Full-Text Content page, Zotero 10 for Developers page. Recorded under ids: `Z6-citationKey-first-added-2022-preprint`, `Z6-schema-history-first-appearance-v14`.

**230.** citationKey was extended from 3 item types (dataset, preprint, standard) to 37 of 40 on 2025-12-20 in commit 55a13120 (schema.json version field 33 before and after; repo HEAD b86c79b5 is at version 45, live API at 42). No Zotero client release version is established by these sources. SOURCE: zotero/zotero-schema history, not the docs.

```
- Add `citationKey` to all item types (closes zotero/zotero-bits#24)
```

Where: https://github.com/zotero/zotero-schema/commit/55a13120bab31e95d6dc88a82fbfa4bbb60e069c, commit message 'Type/field updates (#2)', bullet list. Read in: Full-Text Content page, zotero-schema commit 55a1312. Recorded under ids: `Z6-citationKey-all-item-types-2025-12`, `Z6-55a1312-all-item-types`.

**231.** BBT reads and writes the citekey through Zotero's regular item field API as field name 'citationKey' (getField/setField), i.e. it is a native item field rather than an Extra-field convention.

```
#getNativeKey(item: Zotero.Item): string {
    return this.#getField.call(item, 'citationKey')
  }
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/key-manager.ts#L260-L262; write at #L463 `item.setField('citationKey', proposed)`. Read in: Better BibTeX docs, first read, Basics page. Recorded under ids: `Z6-bbt-writes-native-citationKey`, `Z6-bbt-reads-writes-native-field`.

**232.** Supplementary (outside the BBT page): the current Zotero global schema (version 45) defines a citationKey field on 37 of 40 item types with en-US label 'Citation Key'; since which schema version it exists was not determined.

```
"citationKey": "Citation Key"
```

Where: https://raw.githubusercontent.com/zotero/zotero-schema/master/schema.json > locales.en-US.fields (schema 'version': 45); itemTypes[].fields[].field == 'citationKey' counted locally. Read in: Better BibTeX docs, first read, Local API page, Basics page, Zotero 10 for Developers page. Recorded under ids: `Z6-schema-field-supplementary`, `Z6-schema-has-citationKey`, `Z6-schema-label-version-15`, `Z6-schema-has-citationKey-field`, `Z6-client-version-shipping-library-wide-citationKey`.

**233.** From Zotero 8 on, items have a Zotero-native citation key field which replaced BBT's own key store; BBT 8.0.25 is the last version for Zotero 7 and v9.0.63 targets Zotero 8 and 9 beta.

```
With the advent of Zotero 8, items have a Zotero-native citation key field. This has replaced the BBT citation key field. This has caused a few somewhat disruptive changes: Zotero 7 is no longer supported. BBT 8.0.25 still works on 7.0.32, but will not receive further updates.
```

Where: https://retorque.re/zotero-better-bibtex/, heading "Notice" (also verbatim under "v8.0.0 (Major Release)" at https://retorque.re/zotero-better-bibtex/changelog/); release note v9.0.63: "This release is compatible with Zotero 8 and Zotero 9 beta. Per BBT 8.0.26, Zotero 7 is no longer supported.". Read in: Better BibTeX docs, second read. Record id `Z6-Z7-native-citationkey-field-zotero8`.

**234.** Schema history (git log -S citationKey): added to the preprint type only on 2022-03-02 (schema 14), to 3 types by 2023-03-23 (schema 22), and to 37 types in commit 55a1312 on 2025-12-19, i.e. broadly native only from the Zotero 8 era.

```
55a1312 2025-12-19 22:24:20 -0500 Type/field updates (#2)
```

Where: https://github.com/zotero/zotero-schema/commit/55a13120, git log -S'citationKey' --format='%h %ci %s' -- schema.json in a clone taken 2026-09-04. Read in: Write Requests page. Record id `Z6-citationKey-schema-history`.

**235.** Zotero's own changelog first surfaces citation keys in 9.0 (April 10, 2026) as an items-list column and searchable field; the 8.0 and 9.0 changelogs do not say when the field itself was added.

```
-   Added "Citation Key" column to items list
```

Where: https://github.com/zotero/zotero-docs/blob/1dc2c958795749ead0cd61f175b48cbf3356cac3/content/9.0_changelog.md, H2 'Changes in 9.0 (April 10, 2026)' (rendered at https://www.zotero.org/support/9.0_changelog); next line: '- Search by citation key in search bar ("Title, Creator, Year" mode) and citation dialog'. Read in: Write Requests page. Record id `Z6-zotero9-changelog-citation-key-ui`.

**236.** None of the six Zotero API doc pages fetched (local_api, basics, write_requests, fulltext_content, syncing, file_upload) mention citationKey; the only zotero-docs page listing it is file_renaming (as a template field).

```
-   `citationKey`
```

Where: https://www.zotero.org/support/file_renaming (zotero-docs content/file_renaming.md, field list); absence on API pages verified by grep -i citationKey over all six converted pages. Read in: Local API page. Record id `Z6-api-pages-silent`.

**237.** citationKey entered zotero/zotero-schema in commit 55a13120 'Type/field updates (#2)' dated 2025-12-19, i.e. before the Zotero 8.0 release (2026-01-22).

```
+				{
+					"field": "citationKey"
+				},
```

Where: gh api repos/zotero/zotero-schema/commits/55a13120ba, schema.json patch (commit date 2025-12-19T22:24:20-05:00). Read in: Local API page, Basics page. Recorded under ids: `Z6-schema-commit-date`, `Z6-schema-field-added-2022`.

**238.** Better BibTeX's v8.0.0 changelog attributes the native citation key field to Zotero 8 (this is BBT's statement, not a Zotero page's).

```
**With the advent of Zotero 8, items have a Zotero-native citation key field. This has replaced the BBT citation key field.**
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/site/content/changelog.md, § v8.0.0 (Major Release); rendered at https://retorque.re/zotero-better-bibtex/changelog/. Read in: Local API page, Basics page, zotero-schema commit 55a1312. Recorded under ids: `Z6-bbt-attributes-to-zotero-8`, `Z6-bbt-says-zotero8-native-field`, `Z6-bbt-native-field-since-zotero-8`.

**239.** Zotero 9.0 (April 10, 2026) added a 'Citation Key' items-list column and citation-key search, implying the field already existed natively.

```
- Added “Citation Key” column to items list
- Search by citation key in search bar (“Title, Creator, Year” mode) and citation dialog
```

Where: https://www.zotero.org/support/9.0_changelog, § Changes in 9.0 (April 10, 2026). Read in: Local API page, Basics page. Recorded under ids: `Z6-zotero-9-column`, `Z6-zotero9-citation-key-column`.

**240.** zotero/zotero commit b80bcea184 (2026-03-05) added citationKey to the titleCreatorYear quicksearch.

```
add citationKey to quicksearch-titleCreatorYear (#5814)
```

Where: gh api search/commits?q=repo:zotero/zotero+citationKey, commit b80bcea184, author date 2026-03-05T17:08:52-08:00. Read in: Local API page, Zotero 10 for Developers page. Recorded under ids: `Z6-zotero-commit-quicksearch`, `Z6-citationKey-in-quicksearch`.

**241.** The unauthenticated Web API new-item template already includes a native citationKey field (fetched 2026-09-05).

```
"citationKey": ""
```

Where: https://api.zotero.org/items/new?itemType=journalArticle, JSON body (curl, no auth). Read in: Basics page, Zotero 10 for Developers page. Recorded under ids: `Z6-web-api-template-has-citationKey`, `Z6-item-template-carries-citationKey`.

**242.** BBT 9 reads and writes a native Zotero item field named citationKey (itemData join on fields.fieldName = 'citationKey') and v9.0.0 declares BBT strictly Zotero 8+; this establishes the field exists in Zotero 8+, but this page does not state the Zotero version that introduced it.

```
* new major (should have been done earlier) as BBT is now strictly Zotero 8+
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/site/content/changelog.md, heading '## v9.0.0'; field evidence in content/key-manager.ts sql.load. Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z6-native-field-exists-zotero8`.

**243.** citationKey was extended from 3 to 37 of 40 item types by zotero-schema commit 55a1312 on 2025-12-20 (schema version 33).

```
Type/field updates (#2)
```

Where: https://github.com/zotero/zotero-schema/commit/55a13120bab31e95d6dc88a82fbfa4bbb60e069c (2025-12-20T03:24:20Z; previous commit 81b5f0cc 2025-12-18 had citationKey on 3 types). Read in: Zotero 10 for Developers page. Record id `Z6-schema-history-library-wide-v33`.

**244.** Better BibTeX's extra-field table maps 'citation key' to the Zotero field citationKey and CSL citation-key.

```
| **citation key**                | text | citationKey                          | citation-key                |
```

Where: https://retorque.re/zotero-better-bibtex/exporting/extra-fields/ (field mapping table). Read in: Zotero 10 for Developers page. Record id `Z6-bbt-maps-to-native-field`.

**245.** citationKey first entered schema.json in commit 1873057 (2021-11-17, schema version 14) on the new `preprint` item type only-1 of 38 item types.

```
Add `preprint` item type (closes zotero/zotero-bits#88)

And map Document to CSL 1.0.2 `document`
```

Where: https://github.com/zotero/zotero-schema/commit/1873057, commit message; schema.json at that commit has "version": 14 and the diff adds `"field": "citationKey"` under preprint (found via git log -S'"citationKey"' -- schema.json). Read in: zotero-schema commit 55a1312. Record id `Z6-first-appearance-schema-v14-preprint`.

**246.** Commit 168b222 (2023-03-23) added citationKey to the new `dataset` and `standard` item types; the parent of 55a1312 (81b5f0c, version 33) therefore carries citationKey on exactly dataset, preprint and standard.

```
168b222 2023-03-23 Add Dataset and Standard item types
```

Where: git log -S'"citationKey"' --format='%h %ad %s' -- schema.json in clone of zotero/zotero-schema; parse of schema.json at 81b5f0c: types with citationKey ['dataset', 'preprint', 'standard'] of 40. Read in: zotero-schema commit 55a1312. Record id `Z6-second-step-dataset-standard-2023`.

**247.** After 55a1312, 37 of 40 item types carry citationKey; the three without it are annotation, attachment and note.

```
itemTypes with citationKey: 37 of 40
missing: ['annotation', 'attachment', 'note']
```

Where: Parse of schema.json at 55a13120bab31e95d6dc88a82fbfa4bbb60e069c (gh api repos/zotero/zotero-schema/contents/schema.json?ref=55a1312...). Read in: zotero-schema commit 55a1312. Record id `Z6-55a1312-coverage-37-of-40`.

**248.** 55a1312 is also the commit that added the CSL text-field mapping citation-key → citationKey (git log -S'"citation-key"' returns only this commit).

```
csl text mapping: {'citation-key': ['citationKey']}
```

Where: schema.json at 55a1312, csl.fields.text (parsed); diff line `+ "citationKey"` at diff line 1744. Read in: zotero-schema commit 55a1312. Record id `Z6-55a1312-csl-citation-key-mapping`.

**249.** 55a1312 did not bump the schema version (stays 33); the first bump to 34 is commit 9e0f220 on 2025-12-24, so schema version 34 is the first version whose item types all carry citationKey.

```
-	"version": 33,
+	"version": 34,
```

Where: https://github.com/zotero/zotero-schema/commit/9e0f220 ("Update version", 2025-12-24 11:41:20 -0500), schema.json diff. Read in: zotero-schema commit 55a1312. Record id `Z6-55a1312-no-version-bump`.

**250.** The en-US field label for citationKey is "Citation Key", both in schema.json locales and in the live web API itemTypeFields response.

```
[{'field': 'citationKey', 'localized': 'Citation Key'}]
```

Where: https://api.zotero.org/itemTypeFields?itemType=journalArticle (live 2026-09-05, schema version 42); schema.json at 55a1312 locales['en-US'].fields.citationKey = 'Citation Key'. Read in: zotero-schema commit 55a1312. Record id `Z6-locale-label-citation-key`.

**251.** The first tagged Zotero release bundling a schema that contains citationKey (preprint only) is 6.0.0 (2022-03-17, schema submodule 3d52ff1 = version 15); 5.0.96.3 (2021-08-19) still shipped version 11.

```
zotero 5.0.96.3 (2021-08-19): schema 68ad875 version=11 predates-1873057
zotero 6.0.0 (2022-03-17): schema 3d52ff1 version=15 contains-1873057
```

Where: gh api repos/zotero/zotero/contents/resource/schema/global?ref=<tag> (submodule sha) cross-checked with git merge-base --is-ancestor 1873057 in the zotero-schema clone. Read in: zotero-schema commit 55a1312. Record id `Z6-first-zotero-release-with-any-citationKey`.

**252.** The first tagged Zotero release bundling 55a1312 (citationKey on all types) is 7.0.32 (2026-01-14, schema version 40); 8.0.0 ships v41, 9.0.0 v42, 10.0.0/10.0.1 v44.

```
zotero 7.0.32 (2026-01-14): schema submodule 7f04bb5 version=40 contains-55a1312
zotero 8.0.0 (2026-01-21): schema submodule 5eedf44 version=41 contains-55a1312
zotero 9.0.0 (2026-04-10): schema submodule 62e983a version=42 contains-55a1312
zotero 10.0.0 (2026-08-17): schema submodule 70c3aa9 version=44 contains-55a1312
```

Where: gh api repos/zotero/zotero/contents/resource/schema/global?ref={7.0.32,8.0.0,9.0.0,10.0.0} + git merge-base --is-ancestor 55a1312 <sha>. Read in: zotero-schema commit 55a1312. Record id `Z6-first-zotero-release-with-all-types`.

**253.** The Zotero client added a Citation Key items-list column in commit f6811bd (2026-03-08); the compare API shows 8.0.0 is behind it and 9.0.0 ahead, so the column first ships in 9.0.0.

```
Add Citation Key column

https://forums.zotero.org/discussion/130194/feature-request-citation-key-column-in-library-window
```

Where: https://github.com/zotero/zotero/commit/f6811bd1a8, commit message (file chrome/content/zotero/itemTreeColumns.jsx, dataKey: "citationKey", label: "itemFields.citationKey"); gh api repos/zotero/zotero/compare/f6811bd...8.0.0 → behind, ...9.0.0 → ahead. Read in: zotero-schema commit 55a1312. Record id `Z6-zotero-client-citation-key-column`.

**254.** Live: api.zotero.org serves schema version 42 and the journalArticle item template includes a citationKey property between DOI and url.

```
zotero-schema-version: 42
... 'journalAbbreviation', 'DOI', 'citationKey', 'url', 'accessDate', 'PMID', 'PMCID', 'ISSN', ...
```

Where: GET https://api.zotero.org/items/new?itemType=journalArticle (response headers + JSON keys), observed 2026-09-05. Read in: zotero-schema commit 55a1312. Record id `Z6-live-web-api-template-carries-citationKey`.

**255.** Live: the local Zotero 10.0.1 (schema version 44) returns item JSON whose data object carries citationKey natively with a BBT-filled value.

```
X-Zotero-Version: 10.0.1 ... Zotero-Schema-Version: 44 ... citationKey key present in data: True
citationKey value: 'ieeestandardadoption2013'
```

Where: GET http://localhost:23119/api/users/0/items?limit=1&format=json&itemType=journalArticle, response headers and data keys, observed 2026-09-05. Read in: zotero-schema commit 55a1312. Record id `Z6-live-local-item-json-carries-citationKey`.

**256.** The issue 55a1312 closes, zotero-bits#24, dates from 2011-01-19 and asked for a citation label/key field on all item types mapped to CSL.

```
By adding a "Citation Label"/**citationLabel** field (mapped  to **citation-label** in CSL) to all item types, we should be able to support most label styles.
```

Where: https://github.com/zotero/zotero-bits/issues/24, title "Citation Label", created 2011-01-19, closed 2025-12-20T03:24:21Z. Read in: zotero-schema commit 55a1312. Record id `Z6-zotero-bits-24-origin`.

**257.** PARTIAL Z6 observation: Zotero itself has a native item field named 'citationKey' (present in the fields table and settable via item.setField), which BBT 9.0.63 reads and writes directly, but this page states nothing about which Zotero version introduced it, nor whether the local-API item JSON serialises it.

```
    LEFT JOIN itemData id ON item.itemID = id.itemID AND id.fieldID = (SELECT fieldID FROM fields WHERE fieldName = 'citationKey')
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/key-manager.ts line 42 (sql.missing). Z6's version question is NOT answered by this page, it must come from Zotero's own schema/API docs.. Read in: Better BibTeX `content/key-manager.ts`. Record id `Z6-partial-native-citationkey-field`.

### Z7. Better BibTeX JSON-RPC at 9.0.6x

191 facts, deduplicated by quote.

**258.** Better BibTeX exposes a JSON-RPC endpoint at http://localhost:23119/better-bibtex/json-rpc, called with a JSON-RPC 2.0 body.

```
You can call into BBT using JSON-RPC on the URL http://localhost:23119/better-bibtex/json-rpc . An example could look like:
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/ > JSON-RPC (intro paragraph). Read in: Better BibTeX docs, first read, Better BibTeX docs, second read. Recorded under ids: `Z7-endpoint-url`, `Z7-jsonrpc-endpoint`.

**259.** The page lists exactly 14 methods in six namespaces: api.ready, autoexport.add, collection.scanAUX, item.attachments, item.bibliography, item.citationkey, item.collections, item.export, item.notes, item.pandoc_filter, item.regenerate_key, item.search, user.groups, viewer.viewPDF.

```
const api = new class API {
  public $user = new NSUser
  public $item = new NSItem

  public $collection = new NSCollection
  public $autoexport = new NSAutoExport
  public $viewer = new NSViewer
  public $api = new NSAPI
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/json-rpc.ts#L686-L693 (namespaces); method headings on https://retorque.re/zotero-better-bibtex/exporting/json-rpc/ > 'The available methods are:'; public async methods at v9.0.63 lines 64 scanAUX, 82 add, 122 groups, 162 search, 261 attachments, 316 collections, 368 notes, 392 bibliography, 422 citationkey, 483 regenerate_key, 529 export, 577 pandoc_filter, 665 viewPDF, 681 ready. Read in: Better BibTeX docs, first read. Record id `Z7-method-inventory-14`.

**260.** content/json-rpc.ts is byte-identical at tags v9.0.60 and v9.0.63 and at master HEAD cfdba6ac (empty diffs), so the 14-method inventory holds for those; v9.0.61 is a re-release of 9.0.54 per its release note and was not diffed.

```
This is actually release 9.0.54, as a stop-gap while I address the dead-object problems.
```

Where: https://github.com/retorquere/zotero-better-bibtex/releases/tag/v9.0.61 (release body, published 2026-08-26T01:07:32Z); diffs run locally against https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.60/content/json-rpc.ts and .../v9.0.63/content/json-rpc.ts. Read in: Better BibTeX docs, first read. Record id `Z7-inventory-version-scope`.

**261.** api.ready() returns the Zotero and BBT version strings and serves as the readiness probe.

```
Returns the Zotero and BetterBibTeX version to show the JSON-RPC API is ready.
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/ > api.ready (returns: { betterbibtex: string; zotero: string }). Read in: Better BibTeX docs, first read. Record id `Z7-api-ready`.

**262.** autoexport.add(collection, translator, path, displayOptions?, replace=false) registers a collection auto-export, creating the collection path if needed, and returns the collection's libraryID/key/id.

```
Add an auto-export for the given collection. The target collection will be created if it does not exist
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/ > autoexport.add (returns: { id: number; key: string; libraryID: number }). Read in: Better BibTeX docs, first read. Record id `Z7-autoexport-add-signature`.

**263.** autoexport.add's replace flag defaults to false and controls whether an existing auto-export at the same path is replaced.

```
Replace the auto-export if it exists, default false
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/ > autoexport.add > replace. Read in: Better BibTeX docs, first read. Record id `Z7-autoexport-add-replace-param`.

**264.** If an auto-export already exists at the path with the same translator and collection it is merely rescheduled; if it exists with different parameters and replace is false the call errors with INVALID_PARAMETERS.

```
if (ae && ae.translatorID === translatorID && ae.type === 'collection' && ae.id === coll.id) {
      AutoExport.schedule(ae.type, [ae.id])
    }
    else if (ae && !replace) {
      throw { code: INVALID_PARAMETERS, message: 'Auto-export exists with incompatible parameters, but no \'replace\' was requested' }
    }
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/json-rpc.ts#L88-L94. Read in: Better BibTeX docs, first read, Better BibTeX `content/json-rpc.ts`. Recorded under ids: `Z7-autoexport-add-conflict-error`, `Z7-autoexport-add-replace`.

**265.** The JSON-RPC auto-export namespace has only add(); listing, removing and editing auto-exports is done only in the BBT preferences UI, and the UI cannot add them.

```
There, you can remove auto-exports or change
settings on them. You cannot add new auto-exports
from here, that can only be done by initiating an export.
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/master/site/content/exporting/auto.md > ## Managing auto-exports (rendered at https://retorque.re/zotero-better-bibtex/exporting/auto/); NSAutoExport class at https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/json-rpc.ts#L71-L116 declares only `public async add(`. Read in: Better BibTeX docs, first read, Better BibTeX `content/key-manager.ts`. Recorded under ids: `Z7-autoexport-api-is-add-only`, `Z7-autoexport-ui-add-only`.

**266.** Scheduled auto-exports run in one of three preference-controlled modes: on change, on idle, or paused (still scheduled, not run).

```
* **on change**: run the scheduled export as soon as possible
* **on idle**: run the scheduled export as soon as Zotero goes idle (meaning you haven't used it for some seconds)
* **paused**: run the scheduled exports manually, or run then whenever you change the setting back to "on change" or "on idle". In sthis mode, exports _are still scheduled_, they are just not ran until you give permission.
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/master/site/content/exporting/auto.md > ## Managing auto-exports. Read in: Better BibTeX docs, first read, Basics page, Better BibTeX `content/json-rpc.ts`, zotero-schema commit 55a1312. Recorded under ids: `Z7-autoexport-run-modes`, `Z7-autoexport-doc-register-and-modes`.

**267.** In the UI, an auto-export is registered by ticking 'Keep updated' in the export dialog of a BBT translator.

```
With BBT’s export translators (e.g., “Better BibTeX”), checking the Keep updated option will register the export for automation.
```

Where: https://retorque.re/zotero-better-bibtex/exporting/auto/ > Automatic export (intro paragraph). Read in: Better BibTeX docs, first read. Record id `Z7-autoexport-keep-updated`.

**268.** item.citationkey(item_keys | 'selected') maps Zotero item keys (optionally prefixed libraryID:) to citekeys; unresolved keys map to null.

```
A list of [libraryID]:[itemKey] strings. If [libraryID] is omitted, assume ‘My Library’
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/ > item.citationkey > item_keys; null on miss from https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/json-rpc.ts#L453 (`?.citationKey || null`). Read in: Better BibTeX docs, first read. Record id `Z7-item-citationkey-lookup`.

**269.** item.regenerate_key(citekeys, library?) recomputes each item's citekey from current metadata using the configured citekeyFormat.

```
Regenerate citekeys from current item metadata. For each input citekey, the underlying item’s key is recomputed using the configured citekeyFormat.
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/ > item.regenerate_key (paragraph wraps across lines in HTML; joined with a space). Read in: Better BibTeX docs, first read. Record id `Z7-regenerate-key-purpose`.

**270.** item.regenerate_key returns an old-to-new map; null only when the input citekey resolves to no item, otherwise the resulting key (equal to the input if unchanged).

```
Returns an old → new mapping per input citekey. The value is null only when the input citekey cannot be resolved to an item. Otherwise the value is the resulting citekey — equal to the input if the recomputed key is unchanged, or the new citekey if it changed.
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/ > item.regenerate_key (paragraph wraps across lines in HTML; joined with a space). Read in: Better BibTeX docs, first read, Better BibTeX docs, second read, Write Requests page. Record id `Z7-regenerate-key-mapping`.

**271.** Read-only library handling for regenerate_key is deferred to issue #3430; callers should scope with the library parameter to a writeable library.

```
Read-only library handling is deferred to #3430; until that lands, scope the call to a writeable library via library to avoid touching read-only items.
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/ > item.regenerate_key (joined lines). Read in: Better BibTeX docs, first read, Write Requests page. Record id `Z7-regenerate-key-readonly-caveat`.

**272.** regenerate_key is the write counterpart of item.citationkey and invokes KeyManager.fill(..., { replace: true }), the same path as the 'Regenerate BibTeX key' context-menu item.

```
Counterpart to the read-only item.citationkey lookup. Internally calls the same KeyManager.fill(..., { replace: true }) path the Regenerate BibTeX key right-click menu item invokes.
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/ > item.regenerate_key (joined lines). Read in: Better BibTeX docs, first read, Write Requests page. Recorded under ids: `Z7-regenerate-key-impl-path`, `Z7-regenerate-key-internals`.

**273.** In the implementation, feed items and non-regular items (attachments/notes) are not regenerated and map to their old key rather than null.

```
const eligible = items.filter(item => !item.isFeedItem && item.isRegularItem())
    const eligibleIDs = new Set(eligible.map(item => item.id))

    for (const r of resolved) {
      if (!eligibleIDs.has(r.itemID)) result[r.citekey] = r.oldKey
    }
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/json-rpc.ts#L504-L509. Read in: Better BibTeX docs, first read, Local API page, Better BibTeX `content/json-rpc.ts`. Recorded under ids: `Z7-regenerate-key-non-regular-items`, `Z7-regenerate-key-nonregular-SOURCE`, `Z7-regenerate_key-nonregular`.

**274.** When library is omitted, regenerate_key searches only the user library; '\*' searches all libraries.

```
if (typeof library === 'undefined') library = Zotero.Libraries.userLibraryID
    const libraryID = library === '*' ? undefined : getLibraryID(library)
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/json-rpc.ts#L484-L485; page text: 'Pass * to search across your library and all groups.' at https://retorque.re/zotero-better-bibtex/exporting/json-rpc/ > item.regenerate_key > library. Read in: Better BibTeX docs, first read. Record id `Z7-regenerate-key-library-default`.

**275.** item.regenerate_key was added on 2026-06-10 in commit 88c99bb1 (PR #3530) and is present in tags v9.0.60 and v9.0.63.

```
88c99bb1 2026-06-10T21:48:17Z feat(json-rpc): add item.regenerate_key (#3530)
```

Where: GitHub API repos/retorquere/zotero-better-bibtex/commits?path=content/json-rpc.ts (commit list); grep of regenerate_key in v9.0.60 and v9.0.63 content/json-rpc.ts = 1 hit each. Read in: Better BibTeX docs, first read. Record id `Z7-regenerate-key-introduced`.

**276.** With replace=true the key manager overwrites whatever is in Zotero's native citationKey field via item.setField, so regenerate_key has no pinned/unpinned distinction to respect (derived from source).

```
const current = this.#getNativeKey(item) || ''
    // Respect existing native keys unless caller requested replacement.
    if (current && !replace) return

    const proposed = inspireHEP || this.propose(item)
    // No-op when generation failed or produced the same key.
    if (!proposed || proposed === current) return

    this.store(item, proposed)

    if (readonly(item)) {
      // Read-only keys are cache-only; never write generated keys into Zotero's citationKey field.
      return
    }

    item.setField('citationKey', proposed)
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/key-manager.ts#L448-L463. Read in: Better BibTeX docs, first read, Better BibTeX `content/json-rpc.ts`. Recorded under ids: `Z7-regenerate-overwrites-native-key`, `Z7-pin-store-native-field`.

**277.** Since BBT 8.0.0 (Zotero 8) the citekey store is Zotero's native citation key field, replacing BBT's own store.

```
With the advent of Zotero 8, items have a Zotero-native citation key field. This has replaced the BBT citation key field.
```

Where: https://retorque.re/zotero-better-bibtex/ > Notice; also https://retorque.re/zotero-better-bibtex/changelog/ > v8.0.0 (Major Release). Read in: Better BibTeX docs, first read, Write Requests page. Recorded under ids: `Z7-pin-store-is-native-field`, `Z6-bbt-statement-zotero8`, `Z6-bbt-attributes-native-field-to-zotero8`.

**278.** BBT no longer distinguishes pinned from generated keys; every key is effectively pinned because Zotero has nowhere to store a pinned flag.

```
The concept of pinning keys is gone; keys are always pinned now. Zotero doesn’t have a place I can store whether a key is pinned or not.
```

Where: https://retorque.re/zotero-better-bibtex/ > Notice (bullet 3). Read in: Better BibTeX docs, first read. Record id `Z7-pinning-concept-gone`.

**279.** Zotero migrated the old 'Citation Key:' pins out of the extra field into the native field.

```
Zotero will have moved all pinned keys out of the extra field into the native field
```

Where: https://retorque.re/zotero-better-bibtex/ > Notice (bullet 2). Read in: Better BibTeX docs, first read, Write Requests page. Recorded under ids: `Z7-pinned-keys-moved-from-extra`, `Z7-pin-store-is-native-field`.

**280.** Tools that used to read better-bibtex.sqlite for citekeys must now read the Zotero database (or use the API).

```
Integrations that read the BBT database directly will have to read the Zotero database instead.
```

Where: https://retorque.re/zotero-better-bibtex/ > Notice (bullet 5). Read in: Better BibTeX docs, first read. Record id `Z7-bbt-db-not-an-integration-surface`.

**281.** Because keys now live in a native Zotero field, they sync with Zotero.

```
Upside to all of this is that keys will sync.
```

Where: https://retorque.re/zotero-better-bibtex/ > Notice (closing line). Read in: Better BibTeX docs, first read, zotero-schema commit 55a1312. Recorded under ids: `Z7-keys-sync`, `Z6-bbt-keys-sync`.

**282.** The legacy BBT store that the migration reads is better-bibtex.sqlite in the Zotero data directory, table citationkey with columns itemID, itemKey, libraryID, citationKey, pinned.

```
let bbt: StoredKey[] = (await db.execute('SELECT itemID, itemKey, libraryID, citationKey, pinned FROM citationkey'))
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/key-manager/migrate.ts (function migrate; path from PathUtils.join(Zotero.DataDirectory.dir, `better-bibtex.${ext}`)). Read in: Better BibTeX docs, first read, Better BibTeX `content/json-rpc.ts`, Better BibTeX `content/key-manager.ts`. Recorded under ids: `Z7-legacy-pin-store-schema`, `Z7-pin-store-legacy-sqlite`, `Z7-legacy-pinned-flag-sqlite`.

**283.** The migration dialog offers moving all BBT keys or only pinned keys into the native field, and reports pre-existing native keys.

```
* The migration tool now reports the total count of native Zotero citation keys already present.
* Migration options were clarified to distinguish between moving all keys versus only pinned keys.
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/master/site/content/changelog.md > ## v8.0.4 (rendered at https://retorque.re/zotero-better-bibtex/changelog/). Read in: Better BibTeX docs, first read. Record id `Z7-migration-choice-all-vs-pinned`.

**284.** The citekey-formula function pinned() is retained only as a no-op for legacy formulas; pinned keys in Extra are no longer supported.

```
Legacy compatibility formatter.</p>
<p>Pinned citation keys in Extra are no longer supported, but existing
formulas may still reference $pinned(). Keep this formatter as a no-op.
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/site/data/citekeyformatters/functions.json (entry summary '<b>pinned</b>'). Read in: Better BibTeX docs, first read. Record id `Z7-pinned-formatter-noop`.

**285.** The former auto-pin behaviour is now auto-fill, and its preferences were renamed in 9.0.8 (autoPinDelay to fillKeyAfter, autoPinOverwrite to resetKeyOnChange).

```
* preference autoPinDelay has been renamed to fillKeyAfter
* preference autoPinOverwrite has been renamed to resetKeyOnChange
* native Zotero citation key field is now hidden and replaced with a field at the top
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/master/site/content/changelog.md > ## v9.0.8; rename statement also at > ## v8.0.0 (Major Release) > ### Changes: 'The "auto-pin" feature has been effectively renamed to "auto-fill" to align with native Zotero behavior.'. Read in: Better BibTeX docs, first read, Better BibTeX `content/json-rpc.ts`. Recorded under ids: `Z7-autopin-renamed-autofill`, `Z7-changelog-9.0.8-native-field`.

**286.** The endpoint accepts GET (JSON in the bare query string) and POST, and a JSON array body is handled as a batch of requests.

```
public supportedMethods = [ 'GET', 'POST' ]
  public supportedDataTypes = ['application/json']
  public permitBookmarklet = false

  public async init(request) {
    const query = Server.queryParams(request)
    await Zotero.BetterBibTeX.ready

    try {
      if (request.method === 'GET') request.data = JSON.parse(query[''])

      const response = await (Array.isArray(request.data) ? Promise.all(request.data.map(req => api.handle(req))) : api.handle(request.data))
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/json-rpc.ts#L759-L771 (class Handler). Read in: Better BibTeX docs, first read, Better BibTeX docs, second read, Better BibTeX `content/json-rpc.ts`. Recorded under ids: `Z7-transport-get-post-batch`, `Z7-handler-transport-source`, `Z7-transport-get-post`.

**287.** params may be a positional array or a named object; named keys are mapped onto the method's parameter order and unknown names are rejected.

```
if (!Array.isArray(request.params)) {
      const params = request.params
      request.params = schema.parameters.map(_ => undefined)
      for (const [k, v] of Object.entries(params)) {
        const i = schema.parameters.indexOf(k)
        if (i < 0) return this.invalid(`unsupported argument ${k} for ${method}`)
        request.params[i] = v
      }
    }
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/json-rpc.ts#L719-L727 (API.handle). Read in: Better BibTeX docs, first read, Local API page. Recorded under ids: `Z7-params-positional-or-named`, `Z7-jsonrpc-named-params-SOURCE`.

**288.** The handler checks only JSON-RPC shape (jsonrpc '2.0', string method) and per-method parameter schema; no token, key or consent step exists in the JSON-RPC path.

```
private validRequest(req) {
    if (typeof req !== 'object') return false
    if (req.jsonrpc !== '2.0') return false
    if (typeof req.method !== 'string') return false
    return true
  }
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/json-rpc.ts#L751-L756; startup registers Server.register('/better-bibtex/json-rpc', Handler) at #L784. Read in: Better BibTeX docs, first read. Record id `Z7-no-auth-step`.

**289.** item.export once double-wrapped the JSON-RPC response; the extra layer was removed in 6.7.143.

```
mind that the items.export method had a bug where it would double-wrap the JSON-RPC response; the extra layer has been removed in 6.7.143, but if you were expecting the previous result you will have to update your code.
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/ > closing paragraph after viewer.viewPDF (page's own 'items.export' spelling kept). Read in: Better BibTeX docs, first read, Better BibTeX docs, second read. Recorded under ids: `Z7-items-export-double-wrap`, `Z7-item-export-unwrap-6.7.143`.

**290.** item.attachments(citekey, library?) returns, per attachment, a zotero://open-pdf link and the local file path via att.getFilePath(), plus annotations (with parsed annotationPosition and cached image paths) for file attachments; unknown citekeys raise INVALID_PARAMETERS.

```
if (!key) throw { code: INVALID_PARAMETERS, message: `${ citekey } not found` }
    const item = await getItemAsync(key.itemID)
    const attachments = await getItemsAsync(item.getAttachments())
    const output: Record<string, any>[] = []

    for (const att of attachments) {
      const data: Record<string, any> = {
        open: `zotero://open-pdf/${Zotero.API.getLibraryPrefix(item.libraryID || Zotero.Libraries.userLibraryID)}/items/${att.key}`,
        path: att.getFilePath(),
      }
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/json-rpc.ts#L266-L275; page: 'List attachments for an item with the given citekey' (returns: any) at https://retorque.re/zotero-better-bibtex/exporting/json-rpc/ > item.attachments. Read in: Better BibTeX docs, first read. Record id `Z7-item-attachments-shape`.

**291.** item.search returns each hit as Zotero's CSL-JSON for the item plus a library name and the BBT citekey (empty string if none).

```
return {
        ...Zotero.Utilities.Item.itemToCSLJSON(item),
        library: libraries[item.libraryID],
        citekey: Zotero.BetterBibTeX.KeyManager.get(item.id)?.citationKey || '',
      }
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/json-rpc.ts#L247-L251; page: 'Search for items in Zotero.' at https://retorque.re/zotero-better-bibtex/exporting/json-rpc/ > item.search. Read in: Better BibTeX docs, first read, Better BibTeX `content/json-rpc.ts`. Recorded under ids: `Z7-item-search-shape`, `Z7-method-item.search`.

**292.** The citing docs expose a separate cite-as-you-write HTTP endpoint at http://127.0.0.1:23119/better-bibtex/cayw?format=..., usable from curl/editors but not from a browser since Zotero 5.0.71.

```
**PSA: as of Zotero 5.0.71, access to the CAYW URL will no longer work from the browser for security reasons; `curl` and other programmatic access such as from editors access will work.**
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/master/site/content/citing/cayw.md (top of page; rendered at https://retorque.re/zotero-better-bibtex/citing/cayw/); example URL 'http://127.0.0.1:23119/better-bibtex/cayw?format='.format.'&brackets=1' under ### vim. Read in: Better BibTeX docs, first read. Record id `Z7-cayw-endpoint`.

**293.** Pull export serves a library/collection export over HTTP at http://127.0.0.1:23119/better-bibtex/collection?[collectionID].[format], with format bib/biblatex, bibtex, json/csljson, yaml/yml/cslyaml, jzon, or any translatorID.

```
You can fetch your bibliography on the url http://127.0.0.1:23119/better-bibtex/collection?`[collectionID]`.`[format]` [^1]. You can get this URL for a group, library or collection by right-clicking it and selecting `Download Better BibTeX export...`
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/master/site/content/exporting/pull.md (intro; rendered at https://retorque.re/zotero-better-bibtex/exporting/pull/); format list under 'format can be:'. Read in: Better BibTeX docs, first read. Record id `Z7-pull-export-endpoint`.

**294.** BBT v9.0.63 (2026-08-26) supports Zotero 8 and Zotero 9 beta; Zotero 7 has been unsupported since BBT 8.0.26.

```
This release is compatible with Zotero 8 and Zotero 9 beta. Per BBT 8.0.26, Zotero 7 is no longer supported.
```

Where: https://github.com/retorquere/zotero-better-bibtex/releases/tag/v9.0.63 (release body, published 2026-08-26T21:19:32Z). Read in: Better BibTeX docs, first read. Record id `Z7-version-compat-9063`.

**295.** BBT 9.0.0 declared itself strictly Zotero 8+ and dropped lokijs for auto-export storage.

```
* removed lokijs which gave unpredictable errors when storing auto-exports
* new major (should have been done earlier) as BBT is now strictly Zotero 8+
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/master/site/content/changelog.md > ## v9.0.0. Read in: Better BibTeX docs, first read. Record id `Z7-bbt9-zotero8-only`.

**296.** Changing the citekey formula does not regenerate existing keys; users must select items and Refresh (the JSON-RPC equivalent is item.regenerate_key).

```
**Note**: editing the formula **does not** update any citation keys. A new formula takes effect for items changed *from that point forward*. If you want to apply your new formula, select the items, right-click, and choose BBT -> Refresh
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/master/site/content/citing/_index.md > ### Generating citekeys (rendered at https://retorque.re/zotero-better-bibtex/citing/). Read in: Better BibTeX docs, first read, Local API page, Zotero 10 for Developers page, Better BibTeX `content/key-manager.ts`. Recorded under ids: `Z7-citekey-refresh-not-automatic`, `Z7-formula-change-does-not-rekey`, `Z7-formula-change-needs-refresh`, `Z7-formula-change-not-retroactive`.

**297.** The JSON-RPC page's method list is a Hugo shortcode filled from the JSDoc in content/json-rpc.ts, so the rendered page tracks master rather than a release tag.

```
The available methods are:

{{% json-rpc %}}
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/master/site/content/exporting/json-rpc.md (site source; last commit 743322e1 2024-01-11 'json-rpc changelog'); the page's Edit link points to https://github.com/retorquere/zotero-better-bibtex/edit/master/site/content/exporting/json-rpc.md. Read in: Better BibTeX docs, first read, Zotero 10 for Developers page. Recorded under ids: `Z7-page-source-and-generation`, `Z7-jsonrpc-docs-generated-from-code`.

**298.** Requests are JSON-RPC 2.0 objects POSTed as application/json with method and positional params.

```
curl http://localhost:23119/better-bibtex/json-rpc -X POST -H "Content-Type: application/json" -H "Accept: application/json" --data-binary '{"jsonrpc": "2.0", "method": "collection.scanAUX", "params": ["/My Library/thesis/article1", "/Users/phantom/Downloads/output.aux"] }'
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, heading "JSON-RPC", code example. Read in: Better BibTeX docs, second read. Record id `Z7-jsonrpc-request-shape`.

**299.** The documented method inventory is 14 methods: api.ready, autoexport.add, collection.scanAUX, item.attachments, item.bibliography, item.citationkey, item.collections, item.export, item.notes, item.pandoc_filter, item.regenerate_key, item.search, user.groups, viewer.viewPDF (all present in content/json-rpc.ts at tag v9.0.63).

```
api.ready() | autoexport.add(collection: string, translator: string, path: string, displayOptions?: { [string]: boolean }, replace: boolean=false) | collection.scanAUX(collection: string, aux: string) | item.attachments(citekey: string, library?: string | number) | item.bibliography(citekeys: string[], format?: { contentType: ‘html’ | ’text’; id: string; locale: string; quickCopy: boolean }, library?: string | number) | item.citationkey(item_keys: string[] | ‘selected’) | item.collections(citekeys: string[], includeParents?: boolean) | item.export(citekeys: string[], translator: string, libraryID?: string | number) | item.notes(citekeys: string[]) | item.pandoc_filter(citekeys: string[], asCSL: boolean, libraryID?: string | number | string[], style?: string, locale?: string) | item.regenerate_key(citekeys: string[], library?: string | number) | item.search(terms: string | ([ string ] | [ string, string ] | [ string, string, string | number ] | [ string, string, string | number, boolean ])[], library?: string | number) | user.groups(includeCollections?: boolean) | viewer.viewPDF(id: string, page: number)
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, "The available methods are:" (each signature is a method sub-heading; joined here with " | "). Read in: Better BibTeX docs, second read. Record id `Z7-method-inventory-9.0.6x`.

**300.** api.ready returns the Zotero and BBT version strings and serves as the readiness probe.

```
api.ready() returns: { betterbibtex: string; zotero: string } Returns the Zotero and BetterBibTeX version to show the JSON-RPC API is ready.
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, sub-heading "api.ready()". Read in: Better BibTeX docs, second read. Record id `Z7-api-ready`.

**301.** autoexport.add is the only auto-export JSON-RPC method; it registers a collection-scoped auto-export and returns the target collection's id/key/libraryID (source at v9.0.63: NSAutoExport has no other method, always type 'collection').

```
autoexport.add(collection: string, translator: string, path: string, displayOptions?: { [string]: boolean }, replace: boolean=false) returns: { id: number; key: string; libraryID: number } ... Add an auto-export for the given collection. The target collection will be created if it does not exist
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, sub-heading "autoexport.add(...)". Read in: Better BibTeX docs, second read. Record id `Z7-autoexport-add-only`.

**302.** autoexport.add takes a slash-separated collection path rooted at the library name (empty // = personal library, missing intermediates created), a translator name or GUID, an absolute output path, exportNotes/useJournalAbbreviation display options, and a replace flag defaulting to false.

```
collection: The forward-slash separated path to the collection. The first part of the path must be the library name, or empty (//); empty is your personal library. Intermediate collections that do not exist will be created as needed. translator: The name or GUID of a BBT translator path: The absolute path to which the collection will be auto-exported displayOptions: Options which you would be able to select during an interactive export; exportNotes, default false, and useJournalAbbreviation, default false replace: Replace the auto-export if it exists, default false
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, sub-heading "autoexport.add(...)", parameter list. Read in: Better BibTeX docs, second read. Record id `Z7-autoexport-add-params`.

**303.** In the v9.0.63 source, autoexport.add re-schedules an identical existing export, throws INVALID_PARAMETERS if a different export exists at the path and replace is false, and otherwise creates an enabled, non-recursive collection export.

```
if (ae && ae.translatorID === translatorID && ae.type === 'collection' && ae.id === coll.id) { AutoExport.schedule(ae.type, [ae.id]) } else if (ae && !replace) { throw { code: INVALID_PARAMETERS, message: 'Auto-export exists with incompatible parameters, but no \'replace\' was requested' } } else { await AutoExport.add({ enabled: true, type: 'collection', id: coll.id, path, status: 'done', recursive: false,
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/json-rpc.ts, class NSAutoExport, method add (lines 82-112). Read in: Better BibTeX docs, second read. Record id `Z7-autoexport-replace-conflict-source`.

**304.** Outside JSON-RPC, auto-exports are registered only by ticking Keep updated during an interactive export; the preferences tab can remove or edit them but not add them.

```
After you’ve set up an auto-export using an Keep updated export, you can manage your auto-exports in the BBT preferences under the Automatic exports tab. There, you can remove auto-exports or change settings on them. You cannot add new auto-exports from here, that can only be done by initiating an export.
```

Where: https://retorque.re/zotero-better-bibtex/exporting/auto/, heading "Managing auto-exports". Read in: Better BibTeX docs, second read. Record id `Z7-autoexport-ui-management`.

**305.** A Keep updated export re-exports the file whenever items in the collection/library change.

```
With BBT’s export translators (e.g., “Better BibTeX”), checking the Keep updated option will register the export for automation. After you’ve completed the current export, any changes to the collection or library will trigger an automatic re-export to update the file.
```

Where: https://retorque.re/zotero-better-bibtex/exporting/auto/, heading "Automatic export", first paragraph. Read in: Better BibTeX docs, second read. Record id `Z7-autoexport-keep-updated-trigger`.

**306.** Scheduled auto-exports run in one of three modes, on change, on idle, or paused (still scheduled, not run).

```
on change: run the scheduled export as soon as possible on idle: run the scheduled export as soon as Zotero goes idle (meaning you haven’t used it for some seconds) paused: run the scheduled exports manually, or run then whenever you change the setting back to “on change” or “on idle”. In sthis mode, exports are still scheduled, they are just not ran until you give permission.
```

Where: https://retorque.re/zotero-better-bibtex/exporting/auto/, heading "Managing auto-exports", mode list. Read in: Better BibTeX docs, second read. Record id `Z7-autoexport-scheduling-modes`.

**307.** The Automatic export preference defaults to On Change (options On Change / When Idle / Paused) and exports are debounced by a delay defaulting to 5 seconds (minimum 1, restart required).

```
Automatic export default: On Change ... Options: On Change When Idle Paused Delay auto-export for default: 5 If you have auto-exports set up, BBT will wait this many seconds before actually kicking off the exports to buffer multiple changes in quick succession setting off an unreasonable number of auto-exports. Minimum is 1 second. Changes to this preference take effect after restarting Zotero.
```

Where: https://retorque.re/zotero-better-bibtex/preferences/automatic-export/, headings "Automatic export" and "Delay auto-export for". Read in: Better BibTeX docs, second read. Record id `Z7-autoexport-preference-defaults`.

**308.** An auto-export into a git clone with zotero.betterbibtex.push=true makes BBT pull, export, add, commit and push on every update.

```
To activate git support, first clone the repo that holds your article/thesis/whatnot from your provider (github, overleaf, etc), run git config zotero.betterbibtex.push true in a command shell in that clone, and set up an auto export to that directory; at each update, BBT will now also push your library to the git service.
```

Where: https://retorque.re/zotero-better-bibtex/exporting/auto/, heading "git support". Read in: Better BibTeX docs, second read. Record id `Z7-autoexport-git-push`.

**309.** item.citationkey maps \[libraryID\]:[itemKey] strings (or the current selection) to citekeys; omitting libraryID means My Library.

```
item.citationkey(item_keys: string[] | ‘selected’) returns: { [string]: string } item_keys: A list of [libraryID]:[itemKey] strings. If [libraryID] is omitted, assume ‘My Library’ Fetch citationkeys given item keys
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, sub-heading "item.citationkey(item_keys: string[] | ‘selected’)". Read in: Better BibTeX docs, second read. Record id `Z7-item-citationkey-lookup`.

**310.** item.regenerate_key recomputes each input citekey's item key from current metadata using the configured citekeyFormat, optionally scoped to a library (\* = all libraries).

```
item.regenerate_key(citekeys: string[], library?: string | number) returns: { [string]: string | null } citekeys: Array of citekeys whose items should be regenerated. library: The libraryID to search in (optional). Pass * to search across your library and all groups. Regenerate citekeys from current item metadata. For each input citekey, the underlying item’s key is recomputed using the configured citekeyFormat.
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, sub-heading "item.regenerate_key(citekeys: string[], library?: string | number)". Read in: Better BibTeX docs, second read. Record id `Z7-regenerate-key-signature`.

**311.** regenerate_key is meant for two-phase item creation (stub then enrichment) and, pending #3430, must be scoped to a writeable library; it invokes the same KeyManager.fill replace path as the right-click Regenerate menu item.

```
Useful when items were created in two phases — initial record from partial metadata, enrichment landing later — and the key generated during phase one no longer matches what current metadata would produce. ... Read-only library handling is deferred to #3430; until that lands, scope the call to a writeable library via library to avoid touching read-only items. Counterpart to the read-only item.citationkey lookup. Internally calls the same KeyManager.fill(..., { replace: true }) path the Regenerate BibTeX key right-click menu item invokes.
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, sub-heading "item.regenerate_key(...)", description paragraphs 2, 4, 5. Read in: Better BibTeX docs, second read. Record id `Z7-regenerate-key-usecase-and-readonly`.

**312.** In v9.0.63 source (added 2026-06-11, commit 88c99bb, #3530), regenerate_key returns the old key unchanged for resolved items that are feed items or not regular items, and only calls KeyManager.fill with replace:true for eligible regular items.

```
const eligible = items.filter(item => !item.isFeedItem && item.isRegularItem()) ... for (const r of resolved) { if (!eligibleIDs.has(r.itemID)) result[r.citekey] = r.oldKey } if (!eligible.length) return result await Zotero.BetterBibTeX.KeyManager.fill(eligible.map(item => item.id), { replace: true })
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/json-rpc.ts, class NSItem, method regenerate_key (lines 483-520). Read in: Better BibTeX docs, second read. Record id `Z7-regenerate-key-source-nonregular`.

**313.** item.export renders a list of citekeys through a named BBT translator and returns the export as a string; libraryID defaults to My Library.

```
item.export(citekeys: string[], translator: string, libraryID?: string | number) returns: string citekeys: Array of citekeys translator: BBT translator name or GUID libraryID: ID of library to select the items from. When omitted, assume ‘My Library’ Generate an export for a list of citekeys
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, sub-heading "item.export(...)". Read in: Better BibTeX docs, second read. Record id `Z7-item-export`.

**314.** item.attachments lists an item's attachments by citekey, optionally across all libraries with library='\*'; the return type is untyped (any).

```
item.attachments(citekey: string, library?: string | number) returns: any citekey: The citekey to search for library: The libraryID to search in (optional). Pass * to search across your library and all groups. List attachments for an item with the given citekey
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, sub-heading "item.attachments(citekey: string, library?: string | number)". Read in: Better BibTeX docs, second read. Record id `Z7-item-attachments`.

**315.** item.notes returns note bodies per citekey and item.collections returns the containing collections per citekey, optionally including parents to the root.

```
item.collections(citekeys: string[], includeParents?: boolean) returns: { [string]: { key: string; name: string } } citekeys: An array of citekeys includeParents: Include all parent collections back to the library root Fetch the collections containing a range of citekeys ... item.notes(citekeys: string[]) returns: { [string]: { note: string }[] } citekeys: An array of citekeys Fetch the notes for a range of citekeys
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, sub-headings "item.collections(...)" and "item.notes(...)". Read in: Better BibTeX docs, second read. Record id `Z7-item-notes-collections`.

**316.** item.search accepts either a quick-search string or Zotero advanced-search condition tuples (including joinMode and ignore_feeds), returning untyped hits.

```
terms: Single string as typed into the search box in Zotero (search for Title Creator Year) Array of tuples similar as typed into the advanced search box in Zotero ... search(’’) or search([]): return every entries search(‘Zotero’): quick search for ‘Zotero’ search([[’title’, ‘contains’, ‘Zotero’]]): search for ‘Zotero’ in the Title search([[’library’, ‘is’, ‘My Library’]]): search for entries in ‘My Library’ ... search([[‘joinMode’, ‘any’], [‘creator’, ‘contains’, ‘Johnny’], [’title’, ‘contains’, ‘Zotero’]]): search for entries with Creator ‘Johnny’ OR Title ‘Zotero’
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, sub-heading "item.search(...)", "Examples". Read in: Better BibTeX docs, second read. Record id `Z7-item-search`.

**317.** item.bibliography renders a bibliography string for citekeys with a CSL style id, locale, html/text content type, or the Zotero quick-copy setting.

```
item.bibliography(citekeys: string[], format?: { contentType: ‘html’ | ’text’; id: string; locale: string; quickCopy: boolean }, library?: string | number) returns: string citekeys: An array of citekeys format: A specification of how the bibliography should be formatted .quickCopy: Format as specified in the Zotero quick-copy settings .contentType: Output as HTML or text .locale: Locale to use to generate the bibliography .id: CSL style to use Generate a bibliography for the given citekeys
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, sub-heading "item.bibliography(...)". Read in: Better BibTeX docs, second read. Record id `Z7-item-bibliography`.

**318.** item.pandoc_filter exports citekeys in a form tailored to the pandoc Zotero filter, optionally as CSL.

```
item.pandoc_filter(citekeys: string[], asCSL: boolean, libraryID?: string | number | string[], style?: string, locale?: string) returns: any citekeys: Array of citekeys asCSL: Return the items as CSL libraryID: ID of library to select the items from. When omitted, assume ‘My Library’ Generate an export for a list of citekeys, tailored for the pandoc zotero filter
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, sub-heading "item.pandoc_filter(...)". Read in: Better BibTeX docs, second read. Record id `Z7-item-pandoc-filter`.

**319.** user.groups lists the user's libraries/groups with id and name, optionally with each library's collections.

```
user.groups(includeCollections?: boolean) returns: ({ collections: null | any[]; id: number; name: string })[] includeCollections: Wether or not the result should include a list of collection for each library (default is false) List the libraries (also known as groups) the user has in Zotero
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, sub-heading "user.groups(includeCollections?: boolean)". Read in: Better BibTeX docs, second read. Record id `Z7-user-groups`.

**320.** collection.scanAUX populates (and clears if existing) a collection from citekeys found in a LaTeX .aux file.

```
collection.scanAUX(collection: string, aux: string) returns: { key: string; libraryID: number } ... aux: The absolute path to the AUX file on disk Scan an AUX file for citekeys and populate a Zotero collection from them. The target collection will be cleared if it exists.
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, sub-heading "collection.scanAUX(collection: string, aux: string)". Read in: Better BibTeX docs, second read. Record id `Z7-collection-scanAUX`.

**321.** viewer.viewPDF opens an item's PDF at a zero-based page, addressed by the item's zotero.org URI id as returned by item.search.

```
viewer.viewPDF(id: string, page: number) id: id in the form of http://zotero.org/users/12345678/items/ABCDEFG0 page: Page Number, counting from zero Open the PDF associated with an entry with a given id. the id can be retrieve with e.g. item.search(“mypdf”) -> result[0].id
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, sub-heading "viewer.viewPDF(id: string, page: number)". Read in: Better BibTeX docs, second read. Record id `Z7-viewer-viewPDF`.

**322.** The citekey pin store is now Zotero's native citation key field: pinned keys were migrated out of the extra field, the pinned/unpinned distinction no longer exists, keys are always pinned, and they sync.

```
Zotero will have moved all pinned keys out of the extra field into the native field The concept of pinning keys is gone; keys are always pinned now. Zotero doesn’t have a place I can store whether a key is pinned or not. The Zotero-native citation keys are stored in another place than the BBT citation keys. If you have no Zotero-native citation keys yet, BBT will silently migrate them to there. If you do have Zotero-native citation keys, and a migration would overwrite them, you will be offered a window with the choice on how to migrate your citation keys from the BBT storage to the Zotero storage. Integrations that read the BBT database directly will have to read the Zotero database instead. Upside to all of this is that keys will sync.
```

Where: https://retorque.re/zotero-better-bibtex/, heading "Notice", bullet list and closing line. Read in: Better BibTeX docs, second read. Record id `Z7-pin-store-moved-to-native-field`.

**323.** In v9.0.63 source the key manager reads and writes the Zotero item field named citationKey (SQL fields.fieldName = 'citationKey'; item.setField('citationKey', ...)).

```
LEFT JOIN itemData id ON item.itemID = id.itemID AND id.fieldID = (SELECT fieldID FROM fields WHERE fieldName = 'citationKey') ... const citationKey = item.getField('citationKey') ... item.setField('citationKey', proposed)
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/key-manager.ts, lines 41, 231, 463. Read in: Better BibTeX docs, second read. Record id `Z7-pin-store-source-field-name`.

**324.** The `pinned` citekey-formula function that once read a pinned key from Extra is now a documented no-op kept only for legacy formulas.

```
pinned Legacy compatibility formatter. Pinned citation keys in Extra are no longer supported, but existing formulas may still reference $pinned(). Keep this formatter as a no-op.
```

Where: https://retorque.re/zotero-better-bibtex/citing/formulas/, functions table, entry "pinned" (data source site/data/citekeyformatters/functions.json); history: changelog v8.0.20 "new the `pinned` function for citation key patterns, which retrieves a pinned citation key from the `extra` field.". Read in: Better BibTeX docs, second read. Record id `Z7-pinned-formula-function-noop`.

**325.** Key generation is governed by two preferences: Regenerate citation key when item changes (default no) and Automatically fill citation key after N seconds (default 2; 0 = only on request), renamed in v9.0.8 from autoPinOverwrite/autoPinDelay to resetKeyOnChange/fillKeyAfter.

```
## Regenerate citation key when item changes default: `no` When true, BBT will overwrite existing keys with new keys after an item changes. ## Automatically fill citation key after default: `2` When &gt; 0, BBT will automatically fill the citation key for an item that does not currently have one after this many seconds. When 0, keys will only be generated on user request.
```

Where: https://retorque.re/zotero-better-bibtex/preferences/ (source site/content/preferences/\_index.md), headings "Regenerate citation key when item changes", "Automatically fill citation key after"; rename: https://retorque.re/zotero-better-bibtex/changelog/, "v9.0.8": "preference autoPinDelay has been renamed to fillKeyAfter / preference autoPinOverwrite has been renamed to resetKeyOnChange". Read in: Better BibTeX docs, second read. Record id `Z7-key-fill-and-reset-preferences`.

**326.** Changing the citekey formula never rewrites existing keys; regeneration requires an explicit Refresh (UI), which is what item.regenerate_key exposes programmatically.

```
Changing a pattern will only affect items created/changed after you changed the pattern; existing keys are not automatically regenerated when you change the pattern. If you want your keys to update after a pattern change you will have to select your items, right-click, and select Refresh.
```

Where: https://retorque.re/zotero-better-bibtex/citing/, heading "Configurable citekey generator". Read in: Better BibTeX docs, second read. Record id `Z7-formula-change-does-not-regenerate`.

**327.** The default citekey formula is auth.lower + shorttitle(3,3) + year with an undisableable clash postfix.

```
The default key pattern is auth.lower + shorttitle(3,3) + year; ... a letter postfix (a, b, c, etc) in case of a clash (this part is always added, you can’t disable it, although you can change it to Zotero-style numeric)
```

Where: https://retorque.re/zotero-better-bibtex/citing/, heading "Configurable citekey generator". Read in: Better BibTeX docs, second read. Record id `Z7-default-citekey-formula`.

**328.** A failed BBT-to-native key migration can be re-run from the Help menu during the first five minutes after BBT starts.

```
If key migration appears to have failed, YOUR CITATION KEYS ARE SAFE. Make sure you are on the latest version. For the first 5 minutes after BBT start, the Help menu will have an option Re-do BBT citation key migration.
```

Where: https://retorque.re/zotero-better-bibtex/, heading "Re-do migration". Read in: Better BibTeX docs, second read. Record id `Z7-key-migration-redo`.

**329.** BBT 9.x is strictly Zotero 8+ and dropped lokijs for auto-export storage.

```
## v9.0.0 * removed lokijs which gave unpredictable errors when storing auto-exports * new major (should have been done earlier) as BBT is now strictly Zotero 8+
```

Where: https://retorque.re/zotero-better-bibtex/changelog/, heading "v9.0.0". Read in: Better BibTeX docs, second read. Record id `Z7-zotero8-only-since-9.0.0`.

**330.** BBT's JSON-RPC 2.0 endpoint is POST http://localhost:23119/better-bibtex/json-rpc.

```
You can call into BBT using JSON-RPC on the URL http://localhost:23119/better-bibtex/json-rpc
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, H1 'JSON-RPC'. Read in: Write Requests page. Record id `Z7-jsonrpc-endpoint`.

**331.** At v9.0.63 (and identical on master cfdba6a) the JSON-RPC surface is exactly: api.ready, autoexport.add, collection.scanAUX, item.attachments, item.bibliography, item.citationkey, item.collections, item.export, item.notes, item.pandoc_filter, item.regenerate_key, item.search, user.groups, viewer.viewPDF (namespaces NSAPI, NSAutoExport, NSCollection, NSItem, NSUser, NSViewer).

```
item.citationkey(item_keys: string[] | ‘selected’)
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, list under 'The available methods are:'; confirmed against https://github.com/retorquere/zotero-better-bibtex/blob/v9.0.63/content/json-rpc.ts (grep of 'public async' per exported class). Read in: Write Requests page. Record id `Z7-jsonrpc-method-inventory-9063`.

**332.** The auto-export JSON-RPC API is add-only: NSAutoExport exposes a single public method add(collection, translator, path, displayOptions?, replace=false) that creates the target collection if missing and re-schedules an identical existing export; there is no list/remove/run method (removal is UI-only per the Automatic export page).

```
autoexport.add(collection: string, translator: string, path: string, displayOptions?: { [string]: boolean }, replace: boolean=false)
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, 'The available methods are:'; source https://github.com/retorquere/zotero-better-bibtex/blob/v9.0.63/content/json-rpc.ts 'export class NSAutoExport {' (one public method); UI-only removal per https://retorque.re/zotero-better-bibtex/exporting/auto/ H2 'Managing auto-exports': 'There, you can remove auto-exports or change settings on them. You cannot add new auto-exports from here, that can only be done by initiating an export.'. Read in: Write Requests page. Record id `Z7-autoexport-api-add-only`.

**333.** Not on the doc pages: BBT v9.0.63 source still carries the legacy Extra-field parser for 'Citation Key:' / 'bibtex:' lines (used for reading/migrating old pins), so vault code should treat such Extra lines as legacy input, not as the store.

```
ck: /^(citation[ -]?key|bibtex):(?<citationKey>.*)/i,
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/v9.0.63/content/extra.ts, const re (line 16), consumed by export function citationKey(extra). Read in: Write Requests page, Local API page, Basics page, Better BibTeX `content/json-rpc.ts`, Better BibTeX `content/key-manager.ts`. Recorded under ids: `Z7-extra-citation-key-regex-src`, `Z7-extra-citation-key-regex-SOURCE`, `Z7-legacy-extra-pin-syntax-still-parsed`, `Z7-pin-extra-field-syntax`, `Z7-legacy-extra-pin-line`.

**334.** BBT release under review is v9.0.63 (published 2026-08-26); package.json at that tag reports 9.0.63 and its JSON-RPC public method list matches master at cfdba6ac (2026-09-04).

```
v9.0.63 2026-08-26T21:19:32Z
```

Where: gh api repos/retorquere/zotero-better-bibtex/releases (tag_name + published_at), 2026-09-04. Read in: Write Requests page. Record id `Z7-bbt-version-pin`.

**335.** BBT JSON-RPC 2.0 is served at http://localhost:23119/better-bibtex/json-rpc via POST.

```
You can call into BBT using JSON-RPC on the URL http://localhost:23119/better-bibtex/json-rpc . An example could look like:

curl http://localhost:23119/better-bibtex/json-rpc -X POST -H "Content-Type: application/json" -H "Accept: application/json" --data-binary '{"jsonrpc": "2.0", "method": "collection.scanAUX", "params": ["/My Library/thesis/article1", "/Users/phantom/Downloads/output.aux"] }'
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, H1 'JSON-RPC' (source: site/content/exporting/json-rpc.md; method list rendered by the {{% json-rpc %}} shortcode from content/json-rpc.ts). Read in: Local API page, Zotero 10 for Developers page. Record id `Z7-jsonrpc-endpoint`.

**336.** At 9.0.6x the JSON-RPC inventory is exactly 14 methods: api.ready, autoexport.add, collection.scanAUX, item.attachments, item.bibliography, item.citationkey, item.collections, item.export, item.notes, item.pandoc_filter, item.regenerate_key, item.search, user.groups, viewer.viewPDF (content/json-rpc.ts is byte-identical at v9.0.60, v9.0.63 and master).

```
**api.ready**()
**autoexport.add**(collection: string, translator: string, path: string, displayOptions?: { [string]: boolean }, replace: boolean=false)
**collection.scanAUX**(collection: string, aux: string)
**item.attachments**(citekey: string, library?: string | number)
**item.bibliography**(citekeys: string[], format?: { contentType: ‘html’ | ’text’; id: string; locale: string; quickCopy: boolean }, library?: string | number)
**item.citationkey**(item_keys: string[] | ‘selected’)
**item.collections**(citekeys: string[], includeParents?: boolean)
**item.export**(citekeys: string[], translator: string, libraryID?: string | number)
**item.notes**(citekeys: string[])
**item.pandoc_filter**(citekeys: string[], asCSL: boolean, libraryID?: string | number | string[], style?: string, locale?: string)
**item.regenerate_key**(citekeys: string[], library?: string | number)
**item.search**(terms: string | ([ string ] | [ string, string ] | [ string, string, string | number ] | [ string, string, string | number, boolean ])[], library?: string | number)
**user.groups**(includeCollections?: boolean)
**viewer.viewPDF**(id: string, page: number)
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, 'The available methods are:' (rendered from master; diff of content/json-rpc.ts v9.0.60 vs v9.0.63 vs master is empty). Read in: Local API page. Record id `Z7-method-inventory-9.0.6x`.

**337.** SOURCE-DERIVED: the `items.` namespace is an alias of `item.` (so items.export == item.export); the doc warns items.export stopped double-wrapping in 6.7.143.

```
  constructor() {
    this.$items = this.$item
  }
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/json-rpc.ts, class API; doc note at https://retorque.re/zotero-better-bibtex/exporting/json-rpc/: 'mind that the `items.export` method had a bug where it would double-wrap the JSON-RPC response; the extra layer has been removed in 6.7.143, but if you were expecting the previous result you will have to update your code.'. Read in: Local API page, Better BibTeX `content/key-manager.ts`. Recorded under ids: `Z7-items-namespace-alias`, `Z7-items-is-item-alias`.

**338.** The auto-export JSON-RPC surface is add-only: autoexport.add is the sole method (no list/remove/run), collection-scoped, translator by name or GUID, absolute path, optional exportNotes/useJournalAbbreviation, replace flag.

```
**autoexport.add**(collection: string, translator: string, path: string, displayOptions?: { [string]: boolean }, replace: boolean=false)
returns: { id: number; key: string; libraryID: number }
- collection: The forward-slash separated path to the collection. The first part of the path must be the library name, or empty (`//`); empty is your personal library. Intermediate collections that do not exist will be created as needed.
- translator: The name or GUID of a BBT translator
- path: The absolute path to which the collection will be auto-exported
- displayOptions: Options which you would be able to select during an interactive export; `exportNotes`, default `false`, and `useJournalAbbreviation`, default `false`
- replace: Replace the auto-export if it exists, default `false`
Add an auto-export for the given collection. The target collection will be created if it does not exist
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, autoexport.add; source: class NSAutoExport in content/json-rpc.ts has a single public method `add` at v9.0.5, v9.0.6, v9.0.50, v9.0.58-v9.0.63 and master. Read in: Local API page. Record id `Z7-autoexport-api-add-only`.

**339.** SOURCE-DERIVED: add() on an existing export with identical translator/collection just reschedules it; a differing existing export errors unless replace=true; new exports are type 'collection', recursive false.

```
    const ae = AutoExport.get(path)
    if (ae && ae.translatorID === translatorID && ae.type === 'collection' && ae.id === coll.id) {
      AutoExport.schedule(ae.type, [ae.id])
    }
    else if (ae && !replace) {
      throw { code: INVALID_PARAMETERS, message: 'Auto-export exists with incompatible parameters, but no \'replace\' was requested' }
    }
    else {
      await AutoExport.add({
        enabled: true,
        type: 'collection',
        id: coll.id,
        path,
        status: 'done',
        recursive: false,
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/json-rpc.ts, NSAutoExport.add(). Read in: Local API page, zotero-schema commit 55a1312. Recorded under ids: `Z7-autoexport-add-semantics-SOURCE`, `Z7-autoexport-add-reschedule-vs-replace`.

**340.** In the UI, auto-exports are registered only by doing an export with 'Keep updated'; the preferences tab can remove/edit but not add; scheduling modes are on change / on idle / paused.

```
When you check "keep updated" in the export screen, that means "in the future, schedule this export for re-export when any of its items change, to the file I pick next". [...] * **on change**: run the scheduled export as soon as possible
* **on idle**: run the scheduled export as soon as Zotero goes idle (meaning you haven't used it for some seconds)
* **paused**: run the scheduled exports manually, or run then whenever you change the setting back to "on change" or "on idle". In sthis mode, exports _are still scheduled_, they are just not ran until you give permission. [...] You cannot add new auto-exports
from here, that can only be done by initiating an export.
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/master/site/content/exporting/auto.md, § Managing auto-exports (rendered at https://retorque.re/zotero-better-bibtex/exporting/auto/). Read in: Local API page. Record id `Z7-autoexport-ui-registration`.

**341.** Auto-export can push to git when the target clone has zotero.betterbibtex.push=true (pull, export, add, commit, push).

```
To activate git support, first clone the repo that holds your article/thesis/whatnot from your provider (github, overleaf, etc), run `git config zotero.betterbibtex.push true` in a command shell in that clone, and set up an auto export to that directory; at each update, BBT will now also push your library to the git service.
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/master/site/content/exporting/auto.md, § git support. Read in: Local API page, Better BibTeX `content/json-rpc.ts`. Record id `Z7-autoexport-git-push`.

**342.** item.citationkey maps '\[libraryID\]:[itemKey]' strings (or 'selected') to citekeys; libraryID omitted means My Library.

```
**item.citationkey**(item_keys: string[] | ‘selected’)
returns: { [string]: string }
- item_keys: A list of [libraryID]:[itemKey] strings. If [libraryID] is omitted, assume ‘My Library’
Fetch citationkeys given item keys
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, item.citationkey. Read in: Local API page. Record id `Z7-item-citationkey-lookup`.

**343.** SOURCE-DERIVED: item.citationkey returns null for keys with no cached citekey; in 'selected' mode a child attachment resolves to its parent's key.

```
      keys[key] = Zotero.BetterBibTeX.KeyManager.any(_ => _.libraryID === libraryID && _.itemKey === itemKey)?.citationKey || null
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/json-rpc.ts, NSItem.citationkey(). Read in: Local API page. Record id `Z7-item-citationkey-null-SOURCE`.

**344.** item.regenerate_key returns an old→new map per input citekey: null only when unresolved, otherwise the resulting key (same as input if unchanged); it calls KeyManager.fill(..., {replace:true}).

```
**item.regenerate_key**(citekeys: string[], library?: string | number)
returns: { [string]: string | null }
- citekeys: Array of citekeys whose items should be regenerated.
- library: The libraryID to search in (optional). Pass `*` to search across your library and all groups.
Regenerate citekeys from current item metadata. For each input citekey, the underlying item’s key is recomputed using the configured `citekeyFormat`.
[...]
Returns an old → new mapping per input citekey. The value is `null` only when the input citekey cannot be resolved to an item. Otherwise the value is the resulting citekey — equal to the input if the recomputed key is unchanged, or the new citekey if it changed.
Read-only library handling is deferred to #3430; until that lands, scope the call to a writeable library via `library` to avoid touching read-only items.
Counterpart to the read-only `item.citationkey` lookup. Internally calls the same `KeyManager.fill(..., { replace: true })` path the `Regenerate BibTeX key` right-click menu item invokes.
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, item.regenerate_key. Read in: Local API page. Record id `Z7-regenerate-key-mapping`.

**345.** SOURCE-DERIVED: regenerate_key exists in content/json-rpc.ts at v9.0.50, v9.0.58, v9.0.59, v9.0.60-v9.0.63 and master; it is absent at v9.0.5 and v9.0.6 (introducing tag between 9.0.7 and 9.0.50 not pinned).

```
  public async regenerate_key(citekeys: string[], library?: string | number): Promise<Record<string, string | null>> {
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/json-rpc.ts, NSItem (grep -c regenerate_key: v9.0.5=0, v9.0.6=0, v9.0.50=1, v9.0.58=1, v9.0.59=1, v9.0.60=1, v9.0.63=1). Read in: Local API page, Better BibTeX `content/json-rpc.ts`. Recorded under ids: `Z7-regenerate-key-availability-SOURCE`, `Z7-method-item.regenerate_key-signature`.

**346.** Since BBT 8.0.0 the citekey store is Zotero's native citationKey field: pinned keys were moved out of `extra`, 'pinning' as a distinct state was dropped (keys always pinned), and keys sync.

```
* Zotero will have moved all pinned keys out of the `extra` field into the native field
* The concept of pinning keys is gone; keys are *always* pinned now. Zotero doesn't have a place I can store whether a key is pinned or not.
* The Zotero-native citation keys are stored in another place than the BBT citation keys. If you have no Zotero-native citation keys yet, BBT will silently migrate them to there. If you do have Zotero-native citation keys, and a migration would overwrite them, you will be offered a windows with the choice on how to migrate your citation keys from the BBT storage to the Zotero storage.
* I have enabled auto-pin (what really is auto-fill now) even you had it turned off. You can still turn it back off if you don't want this.

Upside to all of this is that keys will sync.
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/site/content/changelog.md, § v8.0.0 (Major Release); same text in site/content/\_index.md. Read in: Local API page. Record id `Z7-pin-store-native-field-v8`.

**347.** SOURCE-DERIVED: at 9.0.63 KeyManager reads keys from itemData where fieldName='citationKey', writes via item.setField('citationKey', ...), respects an existing native key unless replace, and never writes keys for read-only libraries (cache-only).

```
    LEFT JOIN itemData id ON item.itemID = id.itemID AND id.fieldID = (SELECT fieldID FROM fields WHERE fieldName = 'citationKey')
[...]
    const current = this.#getNativeKey(item) || ''
    // Respect existing native keys unless caller requested replacement.
    if (current && !replace) return
[...]
    if (readonly(item)) {
      // Read-only keys are cache-only; never write generated keys into Zotero's citationKey field.
      return
    }

    item.setField('citationKey', proposed)
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/key-manager.ts, sql.load and KeyManager.update(). Read in: Local API page. Record id `Z7-pin-store-SOURCE`.

**348.** SOURCE-DERIVED: KeyManager.fill without replace only fills items with an empty citationKey; with replace it regenerates all regular items; saves use skipDateModifiedUpdate so dateModified does not change.

```
    const items = (await getItemsAsync(ids)).filter(item => {
      // these get no key
      if (item.isFeedItem || !item.isRegularItem()) return false
      return replace || !item.getField('citationKey')
    })
[...]
    for (const item of items) {
      if (readonly(item)) continue // keys for read-only items are cached only, never written back
      await item.saveTx({ skipDateModifiedUpdate: true })
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/key-manager.ts, KeyManager.fill(). Read in: Local API page. Record id `Z7-fill-semantics-SOURCE`.

**349.** Later 8.x releases partially reinstated pinning: v8.0.20 added a `pinned` formula function reading a pinned key from `extra`, v8.0.38 restored a manual Pin command (for autoPinOverwrite users); v8.0.17 renamed 'pin' to 'fill'.

```
## v8.0.38

* Context-aware menu visibility: Menu items for citation keys (pin, fill, refresh, copy) now hide automatically when no valid, editable items are selected.
* Manual "Pin" command: pinning is back for people who have autoPinOverwrite on
* Citation key pattern update: a new key formula function `pinned` was added, that's always prepended
[...]
## v8.0.20

* dynamic citation keys are back, option in migration
* new the `pinned` function for citation key patterns, which retrieves a pinned citation key from the `extra` field.
* autoPinDelay defaults to on (2 seconds)
[...]
## v8.0.17

* Updated terminology changing "pin" to "fill" for clarity
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/site/content/changelog.md, §§ v8.0.38, v8.0.20, v8.0.17. Read in: Local API page. Record id `Z7-pinned-function-and-pin-command`.

**350.** BBT 9.0.8 renamed autoPinDelay→fillKeyAfter and autoPinOverwrite→resetKeyOnChange and hid the native field behind a top-of-pane field; 9.0.10 'Citation key at the top'.

```
## v9.0.10

* Citation key at the top

## v9.0.8

* preference autoPinDelay has been renamed to fillKeyAfter
* preference autoPinOverwrite has been renamed to resetKeyOnChange
* native Zotero citation key field is now hidden and replaced with a field at the top
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/site/content/changelog.md, §§ v9.0.10, v9.0.8. Read in: Local API page. Record id `Z7-9.0.8-prefs-renamed`.

**351.** Default citekey pattern is auth.lower + shorttitle(3,3) + year with an always-on clash postfix.

```
The default key pattern is `auth.lower + shorttitle(3,3) + year`; [...] 4. a letter postfix (a, b, c, etc) in case of a clash (this part is always added, you can't disable it, although you can change it to Zotero-style numeric)
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/master/site/content/citing/_index.md, § Configurable citekey generator. Read in: Local API page. Record id `Z7-default-pattern`.

**352.** api.ready returns Zotero and BBT versions, usable as a liveness/version probe.

```
**api.ready**()
returns: { betterbibtex: string; zotero: string }
Returns the Zotero and BetterBibTeX version to show the JSON-RPC API is ready.
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/, api.ready. Read in: Local API page. Record id `Z7-api-ready`.

**353.** BBT 9.0.63 is the latest 9.0.6x tag (2026-08-26T21:06:44Z, commit f3c9299e); package.json version 9.0.63; licence MIT.

```
  "version": "9.0.63",
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/package.json; gh api repos/retorquere/zotero-better-bibtex/commits/v9.0.63 → f3c9299e1f8684df96b8ddf116c3880da1cdde7f 2026-08-26T21:06:44Z; tags v9.0.60 2026-08-26T00:05:02Z, v9.0.61 2026-08-26T00:51:25Z, v9.0.62 2026-08-26T21:06:06Z. Read in: Local API page, Better BibTeX `content/json-rpc.ts`, Better BibTeX `content/key-manager.ts`. Recorded under ids: `Z7-version-pin`, `Z7-version-at-sha`, `Z7-version-9063`.

**354.** BBT JSON-RPC 2.0 is served at http://localhost:23119/better-bibtex/json-rpc.

```
You can call into BBT using [JSON-RPC](https://www.jsonrpc.org/) on the URL http://localhost:23119/better-bibtex/json-rpc . An example could look like:
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/v9.0.63/site/content/exporting/json-rpc.md (renders at https://retorque.re/zotero-better-bibtex/exporting/json-rpc/), intro. Read in: Basics page, Better BibTeX `content/json-rpc.ts`, zotero-schema commit 55a1312, Better BibTeX `content/key-manager.ts`. Recorded under ids: `Z7-jsonrpc-endpoint`, `Z7-endpoint-url-docs`, `Z7-rpc-endpoint-doc`.

**355.** At v9.0.63 the documented JSON-RPC inventory is 14 methods: api.ready, autoexport.add, collection.scanAUX, item.attachments, item.bibliography, item.citationkey, item.collections, item.export, item.notes, item.pandoc_filter, item.regenerate_key, item.search, user.groups, viewer.viewPDF.

```
**api.ready**()
**autoexport.add**(collection: string, translator: string, path: string, displayOptions?: { [string]: boolean }, replace: boolean=false)
**collection.scanAUX**(collection: string, aux: string)
**item.attachments**(citekey: string, library?: string | number)
**item.bibliography**(citekeys: string[], format?: { contentType: 'html' | 'text'; id: string; locale: string; quickCopy: boolean }, library?: string | number)
**item.citationkey**(item_keys: string[] | 'selected')
**item.collections**(citekeys: string[], includeParents?: boolean)
**item.export**(citekeys: string[], translator: string, libraryID?: string | number)
**item.notes**(citekeys: string[])
**item.pandoc_filter**(citekeys: string[], asCSL: boolean, libraryID?: string | number | string[], style?: string, locale?: string)
**item.regenerate_key**(citekeys: string[], library?: string | number)
**item.search**(terms: string | ([ string ] | [ string, string ] | [ string, string, string | number ] | [ string, string, string | number, boolean ])[], library?: string | number)
**user.groups**(includeCollections?: boolean)
**viewer.viewPDF**(id: string, page: number)
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/v9.0.63/site/layouts/shortcodes/json-rpc.md, the generated shortcode the json-rpc doc page renders via {{% json-rpc %}} (signature lines 1,10,23,33,43,57,66,76,87,96,107,135,159,168). Read in: Basics page. Record id `Z7-method-inventory-9063`.

**356.** Dispatch maps namespaces user/item/items/collection/autoexport/viewer/api, with items. aliased to item.

```
const api = new class API {
  public $user = new NSUser
  public $item = new NSItem
  public $items: NSItem
  public $collection = new NSCollection
  public $autoexport = new NSAutoExport
  public $viewer = new NSViewer
  public $api = new NSAPI

  constructor() {
    this.$items = this.$item
  }
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/v9.0.63/content/json-rpc.ts, lines 686-697. Read in: Basics page, zotero-schema commit 55a1312. Recorded under ids: `Z7-namespaces-and-items-alias`, `Z7-method-inventory-9.0.63`.

**357.** The auto-export JSON-RPC surface is add-only: NSAutoExport exposes a single `add` (with replace flag); no list/remove/run methods exist.

```
export class NSAutoExport {
  /**
   * Add an auto-export for the given collection. The target collection will be created if it does not exist
   *
   * @param collection                             The forward-slash separated path to the collection. The first part of the path must be the library name, or empty (`//`); empty is your personal library. Intermediate collections that do not exist will be created as needed.
   * @param translator                             The name or GUID of a BBT translator
   * @param path                                   The absolute path to which the collection will be auto-exported
   * @param displayOptions                         Options which you would be able to select during an interactive export; `exportNotes`, default `false`, and `useJournalAbbreviation`, default `false`
   * @param replace                                Replace the auto-export if it exists, default `false`
   * @returns                                      Collection ID of the target collection
   */
  public async add(collection: string, translator: string, path: string, displayOptions: Record<string, boolean> = {}, replace = false): Promise<{ libraryID: number; key: string; id: number }> {
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/v9.0.63/content/json-rpc.ts, lines 71-82 (class body ends line 114 with no other public method; error text at line 92: 'Auto-export exists with incompatible parameters, but no 'replace' was requested'). Read in: Basics page. Record id `Z7-autoexport-api-add-only`.

**358.** item.regenerate_key recomputes keys from current metadata via KeyManager.fill(replace: true) and returns an old→new map where null means the input citekey resolved to no item and an unchanged value means the recomputed key was identical.

```
Regenerate citekeys from current item metadata. For each input citekey, the
 underlying item's key is recomputed using the configured `citekeyFormat`.

Useful when items were created in two phases — initial record from partial
metadata, enrichment landing later — and the key generated during phase one
no longer matches what current metadata would produce.

Returns an old → new mapping per input citekey. The value is `null` only
when the input citekey cannot be resolved to an item. Otherwise the value
is the resulting citekey — equal to the input if the recomputed key is
unchanged, or the new citekey if it changed.
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/v9.0.63/site/layouts/shortcodes/json-rpc.md, "**item.regenerate_key**(citekeys: string[], library?: string | number)" block (lines 107-124); source json-rpc.ts lines 483-520, including "Internally calls the same `KeyManager.fill(..., { replace: true })` path the `Regenerate BibTeX key` right-click menu item invokes." and `if (!eligibleIDs.has(r.itemID)) result[r.citekey] = r.oldKey` for non-regular/feed items. Read in: Basics page. Record id `Z7-regenerate-key-mapping`.

**359.** item.citationkey maps Zotero item keys (\[libraryID\]:[itemKey] strings, or 'selected') to citekeys, the read-only counterpart of regenerate_key.

```
**item.citationkey**(item_keys: string[] | 'selected')

returns: { [string]: string }

* item_keys: A list of [libraryID]:[itemKey] strings. If [libraryID] is omitted, assume 'My Library'

Fetch citationkeys given item keys
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/v9.0.63/site/layouts/shortcodes/json-rpc.md, lines 57-63. Read in: Basics page. Record id `Z7-item-citationkey-lookup`.

**360.** Since BBT 8, the citekey pin store is Zotero's native citationKey field; pinned keys were moved out of Extra and every key is now effectively pinned.

```
* Zotero will have moved all pinned keys out of the `extra` field into the native field
* The concept of pinning keys is gone; keys are *always* pinned now. Zotero doesn't have a place I can store whether a key is pinned or not.
* The Zotero-native citation keys are stored in another place than the BBT citation keys. If you have no Zotero-native citation keys yet, BBT will silently migrate them to there. If you do have Zotero-native citation keys, and a migration would overwrite them, you will be offered a windows with the choice on how to migrate your citation keys from the BBT storage to the Zotero storage.
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/v9.0.63/site/content/changelog.md, heading "v8.0.0 (Major Release)" (also "Key Pinning Changes: The concept of pinning is technically gone; because Zotero lacks a specific "pinned" toggle, keys are now always pinned." under "### Changes"; same bullets repeated in site/content/\_index.md). Read in: Basics page. Record id `Z7-pin-store-native-field-always-pinned`.

**361.** Source: KeyManager.update leaves an existing native key untouched unless replace is requested, which is what makes every native key act as pinned.

```
    const current = this.#getNativeKey(item) || ''
    // Respect existing native keys unless caller requested replacement.
    if (current && !replace) return
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/v9.0.63/content/key-manager.ts, lines 449-451 (update()); fill() at line 216 filters `return replace || !item.getField('citationKey')`. Read in: Basics page, Better BibTeX `content/key-manager.ts`. Recorded under ids: `Z7-native-key-respected-unless-replace`, `Z7-pin-semantics-replace`.

**362.** The JSON-RPC doc warns items.export used to double-wrap responses until 6.7.143.

```
mind that the `items.export` method had a bug where it would double-wrap the JSON-RPC response; the extra layer has been removed in 6.7.143, but if you were expecting the previous result you will have to update your code.
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/v9.0.63/site/content/exporting/json-rpc.md, closing paragraph. Read in: Basics page, Better BibTeX `content/json-rpc.ts`, Zotero 10 for Developers page, zotero-schema commit 55a1312. Recorded under ids: `Z7-items-export-double-wrap-note`, `Z7-docs-export-double-wrap`.

**363.** BBT registers its JSON-RPC handler at the path /better-bibtex/json-rpc on the BBT/Zotero connector HTTP server (localhost:23119 per the docs page).

```
Server.register('/better-bibtex/json-rpc', Handler)
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, export function startup(). Read in: Better BibTeX `content/json-rpc.ts`, Better BibTeX `content/key-manager.ts`. Recorded under ids: `Z7-endpoint-path`, `Z7-rpc-endpoint-and-verbs`.

**364.** The API exposes six namespaces, user, item, collection, autoexport, viewer, api, and `items` is an alias of `item`, so `items.export` and `item.export` are the same method.

```
  public $user = new NSUser
  public $item = new NSItem
  public $items: NSItem
  public $collection = new NSCollection
  public $autoexport = new NSAutoExport
  public $viewer = new NSViewer
  public $api = new NSAPI

  constructor() {
    this.$items = this.$item
  }
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, const api = new class API. Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-namespaces`.

**365.** Method names are split on '.' into namespace and method; a method must exist both on the namespace class and in the generated schema (gen/api/json-rpc), otherwise METHOD_NOT_FOUND (-32601) is returned. Full inventory (14): api.ready, autoexport.add, collection.scanAUX, item.search, item.attachments, item.collections, item.notes, item.bibliography, item.citationkey, item.regenerate_key, item.export, item.pandoc_filter, user.groups, viewer.viewPDF.

```
    const [ namespace, methodName ] = request.method.split('.')
    const method = this[`$${ namespace }`]?.[methodName]
    if (!method) return { jsonrpc: '2.0', error: { code: METHOD_NOT_FOUND, message: `Method not found: ${ request.method }` }, id: null }
    const schema = methods[request.method]
    if (!schema) return { jsonrpc: '2.0', error: { code: METHOD_NOT_FOUND, message: `Method schema not found: ${ request.method }` }, id: null }
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class API, handle(). Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-dispatch-and-schema`.

**366.** params may be a name-keyed object instead of a positional array; names are remapped to positions via the schema parameter list and an unknown name yields an INVALID_PARAMETERS (-32602) response.

```
    if (!request.params) request.params = []
    if (!Array.isArray(request.params)) {
      const params = request.params
      request.params = schema.parameters.map(_ => undefined)
      for (const [k, v] of Object.entries(params)) {
        const i = schema.parameters.indexOf(k)
        if (i < 0) return this.invalid(`unsupported argument ${k} for ${method}`)
        request.params[i] = v
      }
    }
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class API, handle(). Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-named-params`.

**367.** Every error response carries id: null (the request id is not echoed), while success responses echo request.id or null; thrown errors with a .code pass that code through, others become INTERNAL_ERROR (-32603).

```
      return { jsonrpc: '2.0', result: await method(...request.params), id: request.id || null }
    }
    catch (err) {
      log.error('JSON-RPC:', err)
      if ((err as any).code) {
        return { jsonrpc: '2.0', error: { code: (err as any).code, message: (err as any).message }, id: null }
      }
      else {
        return { jsonrpc: '2.0', error: { code: INTERNAL_ERROR, message: `${ err }` }, id: null }
      }
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class API, handle(). Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-error-id-null`.

**368.** The standard JSON-RPC 2.0 error codes are used: -32700 parse, -32600 invalid request, -32601 method not found, -32602 invalid params, -32603 internal.

```
const PARSE_ERROR = -32700 // Invalid JSON was received by the server.
const INVALID_REQUEST = -32600 // The JSON sent is not a valid Request object.
const METHOD_NOT_FOUND = -32601 // The method does not exist / is not available.
const INVALID_PARAMETERS = -32602 // Invalid method parameter(s).
const INTERNAL_ERROR = -32603 // Internal JSON-RPC error.
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, module constants. Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-error-codes`.

**369.** api.ready() returns the Zotero and BBT version strings, as a readiness probe.

```
  public async ready(): Promise<{ zotero: string; betterbibtex: string }> {
    return { zotero: Zotero.version, betterbibtex: BBT.version }
  }
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class NSAPI. Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-method-api.ready`.

**370.** user.groups(includeCollections?) lists all libraries (id, name) and optionally their collections.

```
  public async groups(includeCollections?: boolean): Promise<{ id: number; name: string; collections: null | any[] }[]> {
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class NSUser. Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-method-user.groups`.

**371.** collection.scanAUX(collection, aux) scans a LaTeX .aux file for citekeys and (re)populates a Zotero collection, clearing it first; collection is a slash path whose first segment is the library name (empty = personal library).

```
  public async scanAUX(collection: string, aux: string): Promise<{ libraryID: number; key: string }> {
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class NSCollection. Read in: Better BibTeX `content/json-rpc.ts`, Better BibTeX `content/key-manager.ts`. Recorded under ids: `Z7-method-collection.scanAUX`, `Z7-method-inventory-14`.

**372.** String-term search matches title, publicationTitle, shortTitle, court, year AND citationKey, and excludes feed libraries and attachment items.

```
      const fields = [
        // search the quicksearch-titleCreatorYear fields
        'title',
        'publicationTitle',
        'shortTitle',
        'court',
        'year',

        // plus the citationKey
        'citationKey',
      ]
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class NSItem, search(). Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-search-string-fields`.

**373.** item.attachments(citekey, library?) returns, per attachment, an `open` zotero://open-pdf URI, the local file `path`, and (for file attachments with annotations) an `annotations` array with annotationPosition parsed from JSON and annotationImagePath for image annotations.

```
      const data: Record<string, any> = {
        open: `zotero://open-pdf/${Zotero.API.getLibraryPrefix(item.libraryID || Zotero.Libraries.userLibraryID)}/items/${att.key}`,
        path: att.getFilePath(),
      }
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class NSItem, attachments(). Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-method-item.attachments`.

**374.** item.attachments resolves the citekey with strict === (only an anchored leading @ is stripped via /^@/), unlike the byKeys helper used by collections/notes/export/bibliography/regenerate_key which honours the citekeyCaseInsensitive preference.

```
    const key = Zotero.BetterBibTeX.KeyManager.any(_ => _.citationKey === citationKey && (library === '*' || _.libraryID === libraryID))
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class NSItem, attachments(). Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-attachments-strict-match`.

**375.** The shared byKeys/byKey matcher strips a leading @ from citekeys and compares case-insensitively when the citekeyCaseInsensitive preference is on.

```
function byKeys(citekeys: string[]): (key: CitekeyRecord) => boolean {
  citekeys = citekeys.map(citekey => citekey.replace('@', ''))
  const different = strcmp[Preference.citekeyCaseInsensitive ? 'base' : 'variant']
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, function byKeys(). Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-bykeys-case-insensitive`.

**376.** item.collections(citekeys, includeParents?) returns, per citekey, the collections containing the item (Zotero collection JSON minus relations/version), optionally with parent chain expanded.

```
  public async collections(citekeys: string[], includeParents?: boolean): Promise<Record<string, { key: string; name: string }>> {
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class NSItem. Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-method-item.collections`.

**377.** item.notes(citekeys) returns, per citekey, the HTML note bodies of the item's child notes.

```
  public async notes(citekeys: string[]): Promise<Record<string, { note: string }[]>> {
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class NSItem. Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-method-item.notes`.

**378.** item.bibliography(citekeys, format?, library?) renders a bibliography via Zotero QuickCopy for the given CSL style id (bare ids are prefixed with http://www.zotero.org/styles/), contentType html or text.

```
  public async bibliography(citekeys: string[], format: { quickCopy?: boolean; contentType?: 'html' | 'text'; locale?: string; id?: string } = {}, library?: string | number): Promise<string> {
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class NSItem. Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-method-item.bibliography`.

**379.** item.citationkey(item_keys | 'selected') maps Zotero item keys (\[libraryID\]:[itemKey], libraryID defaulting to My Library) to citekeys, the itemKey-to-citekey bridge; 'selected' uses the current Zotero pane selection and resolves attachments to their parent's key.

```
   * @param item_keys  A list of [libraryID]:[itemKey] strings. If [libraryID] is omitted, assume 'My Library'
   */
  public async citationkey(item_keys: string[] | 'selected'): Promise<Record<string, string>> {
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class NSItem. Read in: Better BibTeX `content/json-rpc.ts`, Better BibTeX `content/key-manager.ts`. Recorded under ids: `Z7-method-item.citationkey`, `Z7-citationkey-lookup`.

**380.** regenerate_key's result value is null only when the input citekey cannot be resolved; otherwise it is the resulting key, equal to the input when unchanged or the new key when changed.

```
   * Returns an old → new mapping per input citekey. The value is `null` only
   * when the input citekey cannot be resolved to an item. Otherwise the value
   * is the resulting citekey — equal to the input if the recomputed key is
   * unchanged, or the new citekey if it changed.
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class NSItem, regenerate_key() JSDoc. Read in: Better BibTeX `content/json-rpc.ts`, Better BibTeX `content/key-manager.ts`. Recorded under ids: `Z7-regenerate_key-mapping`, `Z7-regenerate-key-mapping`.

**381.** regenerate_key calls KeyManager.fill(ids, { replace: true }), the same path as the 'Regenerate BibTeX key' context-menu item; the JSDoc describes it as the counterpart to the read-only item.citationkey lookup.

```
   * Counterpart to the read-only `item.citationkey` lookup. Internally calls
   * the same `KeyManager.fill(..., { replace: true })` path the `Regenerate
   * BibTeX key` right-click menu item invokes.
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class NSItem, regenerate_key() JSDoc. Read in: Better BibTeX `content/json-rpc.ts`, Better BibTeX `content/key-manager.ts`. Recorded under ids: `Z7-regenerate_key-fill-path`, `Z7-regenerate-key-internals`.

**382.** The regenerate_key JSDoc says read-only library handling is deferred to issue #3430 and advises scoping the call via `library`; however KeyManager.fill at this same SHA already skips writing keys for read-only items (cache-only), both recorded, tension left unresolved.

```
   * Read-only library handling is deferred to #3430; until that lands, scope
   * the call to a writeable library via `library` to avoid touching read-only
   * items.
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class NSItem, regenerate_key() JSDoc; contrast content/key-manager.ts fill(): 'if (readonly(item)) continue // keys for read-only items are cached only, never written back'. Read in: Better BibTeX `content/json-rpc.ts`, Better BibTeX `content/key-manager.ts`. Recorded under ids: `Z7-regenerate_key-readonly-caveat`, `Z7-regenerate-key-readonly-caveat`.

**383.** KeyManager.fill never writes generated keys back for items in read-only (non-editable) libraries; such keys are cache-only.

```
      if (readonly(item)) continue // keys for read-only items are cached only, never written back
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/key-manager.ts, class \_KeyManager, fill(). Read in: Better BibTeX `content/json-rpc.ts`, Better BibTeX `content/key-manager.ts`. Recorded under ids: `Z7-keymanager-readonly-cache-only`, `Z7-readonly-never-written-back`.

**384.** item.regenerate_key was added by commit 88c99bb18a (PR #3530, committer date 2026-06-10); the first tag containing that commit is v9.0.28 (v9.0.27 is behind it), and content/json-rpc.ts is unchanged between tag v9.0.63 (f3c9299e1f, 2026-08-26) and the pinned SHA.

```
feat(json-rpc): add item.regenerate_key (#3530)
```

Where: GitHub API: search/commits q=repo:retorquere/zotero-better-bibtex regenerate_key → sha 88c99bb18a, committer date 2026-06-10; compare/88c99bb18a...v9.0.27 status=behind, compare/88c99bb18a...v9.0.28 status=ahead behind=0; compare/f3c9299e1f...cfdba6ac files list does not include content/json-rpc.ts. Read in: Better BibTeX `content/json-rpc.ts`, Zotero 10 for Developers page. Recorded under ids: `Z7-regenerate_key-first-release`, `Z7-regenerate-key-introduced-v9.0.28`.

**385.** item.export(citekeys, translator, libraryID?) runs a BBT translator (name or GUID) over the items and returns the export string; missing or duplicate citekeys raise INVALID_PARAMETERS listing them.

```
  public async export(citekeys: string[], translator: string, libraryID?: string | number): Promise<string> {
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class NSItem. Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-method-item.export`.

**386.** export() reports both missing and duplicate citekeys in one -32602 error before running the translator.

```
      const message = [
        error.missing.length ? `not found: ${ error.missing.join(', ') }` : '',
        error.duplicates.length ? `duplicates found: ${ error.duplicates.join(', ') }` : '',
      ].filter(msg => msg).join('\n')
      throw { code: INVALID_PARAMETERS, message }
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class NSItem, export(). Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-export-missing-duplicates`.

**387.** item.pandoc_filter(citekeys, asCSL, libraryID?, style?, locale?) returns { errors: {citekey: matchCount}, items: {...} } tailored for the pandoc zotero filter, as Better CSL JSON (with custom.author) or Zotero export format.

```
  public async pandoc_filter(citekeys: string[], asCSL: boolean, libraryID?: string | number | string[], style?: string, locale?: string): Promise<any> {
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class NSItem. Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-method-item.pandoc_filter`.

**388.** viewer.viewPDF(id, page) opens the first PDF attachment of the item identified by a Zotero URI at a zero-based page.

```
  public async viewPDF(id: string, page: number): Promise<void> {
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class NSViewer. Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-method-viewer.viewPDF`.

**389.** The autoexport namespace exposes exactly one method, add(collection, translator, path, displayOptions?, replace?); there is no list, remove, run or update auto-export method over JSON-RPC.

```
  public async add(collection: string, translator: string, path: string, displayOptions: Record<string, boolean> = {}, replace = false): Promise<{ libraryID: number; key: string; id: number }> {
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class NSAutoExport (sole method). Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-autoexport-add-only`.

**390.** autoexport.add always creates a collection-scoped, non-recursive auto-export (type hard-coded to 'collection'); library-level auto-exports cannot be registered via JSON-RPC.

```
      await AutoExport.add({
        enabled: true,
        type: 'collection',
        id: coll.id,
        path,
        status: 'done',
        recursive: false,
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts, class NSAutoExport, add(). Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-autoexport-add-collection-only`.

**391.** Per the auto-export docs, auto-exports are registered by checking 'Keep updated' in an export dialog; the preferences pane can only manage/remove them, not add.

```
After you've set up an auto-export using an `Keep updated` export,
you can manage your auto-exports in the BBT preferences under the
`Automatic exports` tab. There, you can remove auto-exports or change
settings on them. You cannot add new auto-exports
from here, that can only be done by initiating an export.
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/site/content/exporting/auto.md, heading 'Managing auto-exports'. Read in: Better BibTeX `content/json-rpc.ts`, zotero-schema commit 55a1312. Recorded under ids: `Z7-autoexport-ui-registration`, `Z7-autoexport-removal-ui-only`.

**392.** KeyManager's in-memory key cache is loaded from Zotero's own itemData rows for the field named 'citationKey'; keys for read-only libraries are additionally persisted to read-only.json in the BBT data dir.

```
    JOIN fields f ON id.fieldID = f.fieldID AND f.fieldName = 'citationKey'
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/key-manager.ts, const sql.load; see also class Keys: path() returns PathUtils.join(Zotero.BetterBibTeX.dir, 'read-only.json'). Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-pin-store-cache-load`.

**393.** Only read-only-library keys are written to read-only.json; writable-library keys live solely in the native field.

```
        // Persist only read-only-library keys in read-only.json.
        return !!library && readonly(library)
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/key-manager.ts, class Keys, save(). Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-pin-store-readonly-json`.

**394.** The migration writes legacy keys into the native field with item.setField('citationKey', citationKey) unless a native key already exists (or overwrite chosen).

```
            if (choice.overwrite || !item.getField('citationKey')) {
              item.setField('citationKey', citationKey)
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/key-manager/migrate.ts, export async function migrate(), switch(choice.migrate) block. Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-pin-store-legacy-migrate-write`.

**395.** A context-menu helper applies/moves an extra-field citation key into the native citationKey field and strips it from extra.

```
      const { citationKey, extra } = Extra.citationKey(item.getField('extra'))
      if (!citationKey) continue

      if (move) item.setField('citationKey', citationKey)
      item.setField('extra', extra)
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/menu-helper.ts, export async function applyCitationKeyFromExtra(move). Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-pin-extra-menu-move`.

**396.** The BibTeX exporter falls back to the extra-field citation key only for items without a numeric itemID (external/uncached items).

```
      if (typeof item.itemID !== 'number') { // https://github.com/diegodlh/zotero-cita/issues/145
        item.citationKey = Extra.citationKey(item.extra).citationKey
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/translators/bibtex/exporter.ts, item preprocessing loop. Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-pin-extra-exporter-fallback`.

**397.** On item change, KeyManager regenerates an existing key only if the resetKeyOnChange preference is on (default no); otherwise existing native keys are kept.

```
        if (this.update(item, { replace: Preference.resetKeyOnChange })) {
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/key-manager.ts, class \_KeyManager, start(), items-changed handler. Read in: Better BibTeX `content/json-rpc.ts`, Better BibTeX `content/key-manager.ts`. Recorded under ids: `Z7-resetKeyOnChange`, `Z7-resetkeyonchange`.

**398.** Preferences doc: 'Regenerate citation key when item changes' defaults to no and overwrites existing keys after an item changes when on; 'Automatically fill citation key after' defaults to 2 seconds.

```
When true, BBT will overwrite existing keys with new keys after an item changes.
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/site/content/preferences/_index.md, heading 'Regenerate citation key when item changes'. Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-resetKeyOnChange-doc`.

**399.** The JSON-RPC docs page and the runtime parameter schema are both generated from the NS\* classes' JSDoc in content/json-rpc.ts by setup/apis.js.

```
  const jsonrpc = new APIReader('content/json-rpc.ts', /^NS/, /./)
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/setup/apis.js, IIFE JSONRPC(); also writes site/layouts/shortcodes/json-rpc.md and gen/api/json-rpc.js. Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-docs-generated-from-jsdoc`.

**400.** The citing docs describe key stability and that users can fix keys to any value of their choosing (no explicit mention of the extra-field syntax on that page).

```
* BBT is conservative about citation key changes, and allows you to fix keys to any value of your choosing.
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/site/content/citing/_index.md, heading 'Generating citekeys for your items'. Read in: Better BibTeX `content/json-rpc.ts`. Record id `Z7-citing-doc-pin-prose`.

**401.** At v9.0.63 the JSON-RPC namespaces are user, item (alias items), collection, autoexport, viewer, api; method = '<namespace>.<name>'.

```
public $user = new NSUser public $item = new NSItem public $items: NSItem public $collection = new NSCollection public $autoexport = new NSAutoExport public $viewer = new NSViewer public $api = new NSAPI constructor() { this.$items = this.$item } [...] const [ namespace, methodName ] = request.method.split('.')
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/json-rpc.ts lines 686-716 (class API). Read in: Zotero 10 for Developers page. Record id `Z7-jsonrpc-namespaces-9.0.63`.

**402.** At v9.0.63 the full method inventory is: api.ready, autoexport.add, collection.scanAUX, item.attachments, item.bibliography, item.citationkey, item.collections, item.export, item.notes, item.pandoc_filter, item.regenerate_key, item.search, user.groups, viewer.viewPDF (14 methods; the live docs page lists the same set).

```
**api.ready**() [...] **autoexport.add**(collection: string, translator: string, path: string, displayOptions?: { [string]: boolean }, replace: boolean=false) [...] **collection.scanAUX**(collection: string, aux: string) [...] **item.attachments**(citekey: string, library?: string | number) [...] **item.bibliography**(citekeys: string[], format?: { contentType: ‘html’ | ’text’; id: string; locale: string; quickCopy: boolean }, library?: string | number) [...] **item.citationkey**(item_keys: string[] | ‘selected’) [...] **item.collections**(citekeys: string[], includeParents?: boolean) [...] **item.export**(citekeys: string[], translator: string, libraryID?: string | number) [...] **item.notes**(citekeys: string[]) [...] **item.pandoc_filter**(citekeys: string[], asCSL: boolean, libraryID?: string | number | string[], style?: string, locale?: string) [...] **item.regenerate_key**(citekeys: string[], library?: string | number) [...] **item.search**(terms: ..., library?: string | number) [...] **user.groups**(includeCollections?: boolean) [...] **viewer.viewPDF**(id: string, page: number)
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/ ('The available methods are:'); corroborated by grep of `public async` in content/json-rpc.ts at tag v9.0.63 (lines 64, 82, 122, 162, 261, 316, 368, 392, 422, 483, 529, 577, 665, 681). Read in: Zotero 10 for Developers page. Record id `Z7-jsonrpc-method-inventory-9.0.63`.

**403.** The autoexport JSON-RPC namespace exposes only `add` at v9.0.63 (no list/remove/run); add re-schedules an identical existing export, errors if an incompatible one exists unless replace=true.

```
public async add(collection: string, translator: string, path: string, displayOptions: Record<string, boolean> = {}, replace = false): Promise<{ libraryID: number; key: string; id: number }> { [...] if (ae && ae.translatorID === translatorID && ae.type === 'collection' && ae.id === coll.id) { AutoExport.schedule(ae.type, [ae.id]) } else if (ae && !replace) { throw { code: INVALID_PARAMETERS, message: 'Auto-export exists with incompatible parameters, but no \'replace\' was requested' } }
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/json-rpc.ts lines 71-114 (export class NSAutoExport, the only `public async` member is `add`). Read in: Zotero 10 for Developers page. Record id `Z7-autoexport-api-add-only`.

**404.** autoexport.add takes a slash path (library name or empty for personal), translator name/GUID, absolute output path, displayOptions exportNotes/useJournalAbbreviation, and replace; creates missing collections.

```
collection: The forward-slash separated path to the collection. The first part of the path must be the library name, or empty (`//`); empty is your personal library. Intermediate collections that do not exist will be created as needed. translator: The name or GUID of a BBT translator path: The absolute path to which the collection will be auto-exported displayOptions: Options which you would be able to select during an interactive export; `exportNotes`, default `false`, and `useJournalAbbreviation`, default `false` replace: Replace the auto-export if it exists, default `false` Add an auto-export for the given collection. The target collection will be created if it does not exist
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/ § autoexport.add. Read in: Zotero 10 for Developers page. Record id `Z7-autoexport-add-doc-params`.

**405.** Auto-exports are registered via 'Keep updated' on an export; the prefs tab can remove/edit but not add; scheduled runs are 'on change', 'on idle', or 'paused'.

```
With BBT’s export translators (e.g., “Better BibTeX”), checking the `Keep updated` option will register the export for automation. [...] on change: run the scheduled export as soon as possible on idle: run the scheduled export as soon as Zotero goes idle (meaning you haven’t used it for some seconds) paused: run the scheduled exports manually, or run then whenever you change the setting back to “on change” or “on idle”. In sthis mode, exports *are still scheduled*, they are just not ran until you give permission. [...] There, you can remove auto-exports or change settings on them. You cannot add new auto-exports from here, that can only be done by initiating an export.
```

Where: https://retorque.re/zotero-better-bibtex/exporting/auto/ (intro; § Managing auto-exports). Read in: Zotero 10 for Developers page. Record id `Z7-autoexport-ui-registration-and-modes`.

**406.** item.regenerate_key recomputes keys from current metadata using citekeyFormat and returns an old→new map; null only when the citekey cannot be resolved; equal to input when unchanged.

```
Regenerate citekeys from current item metadata. For each input citekey, the underlying item’s key is recomputed using the configured `citekeyFormat`. [...] Returns an old → new mapping per input citekey. The value is `null` only when the input citekey cannot be resolved to an item. Otherwise the value is the resulting citekey — equal to the input if the recomputed key is unchanged, or the new citekey if it changed.
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/ § item.regenerate_key. Read in: Zotero 10 for Developers page. Record id `Z7-regenerate-key-mapping-semantics`.

**407.** regenerate_key's read-only library handling is deferred (#3430); scope calls to a writeable library; it uses the same KeyManager.fill({replace:true}) path as the right-click 'Regenerate BibTeX key'.

```
Read-only library handling is deferred to #3430; until that lands, scope the call to a writeable library via `library` to avoid touching read-only items. Counterpart to the read-only `item.citationkey` lookup. Internally calls the same `KeyManager.fill(..., { replace: true })` path the `Regenerate BibTeX key` right-click menu item invokes.
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/ § item.regenerate_key. Read in: Zotero 10 for Developers page. Record id `Z7-regenerate-key-readonly-caveat`.

**408.** In code, non-regular/feed items resolve to their old key unchanged; eligible items are refilled with replace:true and the result is the KeyManager's new key or the old key as fallback.

```
if (!eligibleIDs.has(r.itemID)) result[r.citekey] = r.oldKey [...] await Zotero.BetterBibTeX.KeyManager.fill(eligible.map(item => item.id), { replace: true }) for (const r of resolved) { if (!eligibleIDs.has(r.itemID)) continue result[r.citekey] = Zotero.BetterBibTeX.KeyManager.get(r.itemID)?.citationKey || r.oldKey }
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/json-rpc.ts lines 483-520 (NSItem.regenerate_key). Read in: Zotero 10 for Developers page. Record id `Z7-regenerate-key-implementation-9.0.63`.

**409.** item.citationkey maps '\[libraryID\]:[itemKey]' strings (or 'selected') to citekeys, defaulting to My Library; unresolved keys map to null in code.

```
item_keys: A list of [libraryID]:[itemKey] strings. If [libraryID] is omitted, assume ‘My Library’ Fetch citationkeys given item keys || keys[key] = Zotero.BetterBibTeX.KeyManager.any(_ => _.libraryID === libraryID && _.itemKey === itemKey)?.citationKey || null
```

Where: https://retorque.re/zotero-better-bibtex/exporting/json-rpc/ § item.citationkey; content/json-rpc.ts at v9.0.63 lines 422-460. Read in: Zotero 10 for Developers page. Record id `Z7-item-citationkey-lookup`.

**410.** At v9.0.63 BBT stores citation keys (including pinned/fixed ones) in Zotero's native citationKey item field: generation skips items that already have a native key unless replace is requested, and writes proposed keys via setField('citationKey').

```
return replace || !item.getField('citationKey') [...] const current = this.#getNativeKey(item) || '' // Respect existing native keys unless caller requested replacement. if (current && !replace) return [...] item.setField('citationKey', proposed) return item
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/key-manager.ts lines 213-216 and 448-465. Read in: Zotero 10 for Developers page. Record id `Z7-citekey-pin-store-is-native-field`.

**411.** Pinned citation keys in the Extra field are no longer supported; the $pinned() formula function is retained only as a no-op.

```
Legacy compatibility formatter. Pinned citation keys in Extra are no longer supported, but existing formulas may still reference $pinned(). Keep this formatter as a no-op. public $pinned(): string { return '' }
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/key-manager/formatter.ts lines 933-941. Read in: Zotero 10 for Developers page. Record id `Z7-pinned-in-extra-no-longer-supported`.

**412.** BBT migrates its legacy citationkey table (which had a pinned column) into Zotero's citationKey field, optionally migrating only pinned keys and not overwriting existing native keys unless chosen.

```
SELECT itemID, itemKey, libraryID, citationKey, pinned FROM citationkey [...] migrate: 'postpone' as 'none' | 'all' | 'pinned' | 'postpone', [...] case 'pinned': bbt = bbt.filter(k => k.pinned) [...] if (choice.overwrite || !item.getField('citationKey')) { item.setField('citationKey', citationKey) await item.save({ skipDateModifiedUpdate: true, skipNotifier: !!choice.zotero }) }
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/key-manager/migrate.ts lines 55, 65, 164-178. Read in: Zotero 10 for Developers page. Record id `Z7-legacy-pin-migration`.

**413.** The in-memory CitekeyRecord at v9.0.63 has no pinned flag (itemID, libraryID, itemKey, citationKey only).

```
export type CitekeyRecord = { itemID: number libraryID: number itemKey: string citationKey: string }
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/key-manager.ts lines 61-66. Read in: Zotero 10 for Developers page. Record id `Z7-citekey-record-has-no-pinned-flag`.

**414.** For read-only libraries BBT keeps generated keys cache-only and never writes them into the citationKey field.

```
// If a read-only item already has a cached key, keep serving it until a caller explicitly asks to regenerate. if (!replace && this.#keys.get(item.id)?.citationKey) return // Otherwise generate a new shadow key for export/UI use, but never write it back to Zotero. [...] // Read-only keys are cache-only; never write generated keys into Zotero's citationKey field.
```

Where: https://raw.githubusercontent.com/retorquere/zotero-better-bibtex/v9.0.63/content/key-manager.ts lines 442-461. Read in: Zotero 10 for Developers page. Record id `Z7-readonly-keys-cache-only`.

**415.** BBT's default citekey pattern is auth.lower + shorttitle(3,3) + year with a mandatory clash postfix.

```
The default key pattern is `auth.lower + shorttitle(3,3) + year`; [...] a letter postfix (a, b, c, etc) in case of a clash (this part is always added, you can’t disable it, although you can change it to Zotero-style numeric)
```

Where: https://retorque.re/zotero-better-bibtex/citing/ § Configurable citekey generator. Read in: Zotero 10 for Developers page. Record id `Z7-default-key-pattern`.

**416.** Latest BBT release at fetch is v9.0.63 (2026-08-26); preceding 9.0.6x tag is v9.0.61 (2026-08-26); repo HEAD cfdba6ac; licence MIT.

```
v9.0.63 2026-08-26T21:19:32Z v9.0.61 2026-08-26T01:07:32Z v9.0.54 2026-08-01T12:48:42Z
```

Where: gh api repos/retorquere/zotero-better-bibtex/releases (tag_name, published_at); gh api repos/retorquere/zotero-better-bibtex (.license.spdx_id = MIT, pushed_at 2026-09-04T17:29:40Z). Read in: Zotero 10 for Developers page. Record id `Z7-bbt-version-pin`.

**417.** A method is callable only if both the namespace class has it and the generated `methods` schema (gen/api/json-rpc) lists it, so the 14 class methods are the ceiling of the inventory.

```
import { methods } from '../gen/api/json-rpc'
...
    const [ namespace, methodName ] = request.method.split('.')
    const method = this[`$${ namespace }`]?.[methodName]
    if (!method) return { jsonrpc: '2.0', error: { code: METHOD_NOT_FOUND, message: `Method not found: ${ request.method }` }, id: null }
    const schema = methods[request.method]
    if (!schema) return { jsonrpc: '2.0', error: { code: METHOD_NOT_FOUND, message: `Method schema not found: ${ request.method }` }, id: null }
```

Where: content/json-rpc.ts at v9.0.63, line 20 and `handle(request)` (lines 709-716). Read in: zotero-schema commit 55a1312. Record id `Z7-dispatch-requires-generated-schema`.

**418.** The auto-export RPC namespace exposes only `add` (collection, translator, path, displayOptions, replace); there is no list/remove/update method.

```
/**
   * Add an auto-export for the given collection. The target collection will be created if it does not exist
   * @param collection                             The forward-slash separated path to the collection. The first part of the path must be the library name, or empty (`//`); empty is your personal library. Intermediate collections that do not exist will be created as needed.
   * @param translator                             The name or GUID of a BBT translator
   * @param path                                   The absolute path to which the collection will be auto-exported
   * @param displayOptions                         Options which you would be able to select during an interactive export; `exportNotes`, default `false`, and `useJournalAbbreviation`, default `false`
   * @param replace                                Replace the auto-export if it exists, default `false`
   * @returns                                      Collection ID of the target collection
   */
  public async add(collection: string, translator: string, path: string, displayOptions: Record<string, boolean> = {}, replace = false): Promise<{ libraryID: number; key: string; id: number }>
```

Where: content/json-rpc.ts at v9.0.63, class NSAutoExport (only public method); rendered doc lists autoexport.add as the sole autoexport method. Read in: zotero-schema commit 55a1312. Record id `Z7-autoexport-api-add-only`.

**419.** item.regenerate_key(citekeys, library?) returns an old→new map; null only when the input citekey cannot be resolved; unchanged key returns the input; it calls KeyManager.fill(..., {replace:true}), the same path as the Regenerate BibTeX key menu.

```
Returns an old → new mapping per input citekey. The value is `null` only
   * when the input citekey cannot be resolved to an item. Otherwise the value
   * is the resulting citekey — equal to the input if the recomputed key is
   * unchanged, or the new citekey if it changed.
   ...
   * Counterpart to the read-only `item.citationkey` lookup. Internally calls
   * the same `KeyManager.fill(..., { replace: true })` path the `Regenerate
   * BibTeX key` right-click menu item invokes.
   *
   * @param citekeys  Array of citekeys whose items should be regenerated.
   * @param library   The libraryID to search in (optional). Pass `*` to search across your library and all groups.
```

Where: content/json-rpc.ts at v9.0.63, doc comment on NSItem.regenerate_key (lines 462-482); body: `await Zotero.BetterBibTeX.KeyManager.fill(eligible.map(item => item.id), { replace: true })` then `result[r.citekey] = Zotero.BetterBibTeX.KeyManager.get(r.itemID)?.citationKey || r.oldKey`. Read in: zotero-schema commit 55a1312. Record id `Z7-regenerate-key-mapping`.

**420.** regenerate_key defers read-only-library handling to BBT issue #3430 and advises scoping the call to a writeable library.

```
Read-only library handling is deferred to #3430; until that lands, scope
   * the call to a writeable library via `library` to avoid touching read-only
   * items.
```

Where: content/json-rpc.ts at v9.0.63, doc comment on NSItem.regenerate_key. Read in: zotero-schema commit 55a1312. Record id `Z7-regenerate-key-readonly-caveat`.

**421.** item.citationkey takes \[libraryID\]:[itemKey] strings (library defaults to My Library) or the literal 'selected', and returns key→citekey (null when none).

```
/**
   * Fetch citationkeys given item keys
   *
   * @param item_keys  A list of [libraryID]:[itemKey] strings. If [libraryID] is omitted, assume 'My Library'
   */
  public async citationkey(item_keys: string[] | 'selected'): Promise<Record<string, string>>
```

Where: content/json-rpc.ts at v9.0.63, NSItem.citationkey. Read in: zotero-schema commit 55a1312. Record id `Z7-citationkey-lookup-input-form`.

**422.** At v9.0.63 the citekey store is Zotero's native citationKey field: KeyManager loads keys from itemData joined on fields.fieldName='citationKey' and writes generated keys with item.setField('citationKey', ...).

```
JOIN fields f ON id.fieldID = f.fieldID AND f.fieldName = 'citationKey'
...
    const proposed = inspireHEP || this.propose(item)
    // No-op when generation failed or produced the same key.
    if (!proposed || proposed === current) return

    this.store(item, proposed)

    if (readonly(item)) {
      // Read-only keys are cache-only; never write generated keys into Zotero's citationKey field.
      return
    }

    item.setField('citationKey', proposed)
    return item
```

Where: content/key-manager.ts at v9.0.63, sql.load (line 53) and KeyManager.update (lines 448-464). Read in: zotero-schema commit 55a1312. Record id `Z7-pin-store-is-native-citationKey-field`.

**423.** BBT states pinning no longer exists as a flag: every native key is treated as pinned; auto-pin became auto-fill.

```
* The concept of pinning keys is gone; keys are *always* pinned now. Zotero doesn't have a place I can store whether a key is pinned or not.
...
* Key Pinning Changes: The concept of pinning is technically gone; because Zotero lacks a specific "pinned" toggle, keys are now always pinned.
* Feature Renaming: The "auto-pin" feature has been effectively renamed to "auto-fill" to align with native Zotero behavior.
```

Where: site/content/changelog.md at v9.0.63, heading "v8.0.0 (Major Release)" and its "Changes" subsection. Read in: zotero-schema commit 55a1312. Record id `Z7-pinning-concept-gone`.

**424.** KeyManager.fill only touches regular items lacking a citationKey unless replace is set; update() returns early when a native key exists and replace is false.

```
const items = (await getItemsAsync(ids)).filter(item => {
      // these get no key
      if (item.isFeedItem || !item.isRegularItem()) return false
      return replace || !item.getField('citationKey')
    })
...
    const current = this.#getNativeKey(item) || ''
    // Respect existing native keys unless caller requested replacement.
    if (current && !replace) return
```

Where: content/key-manager.ts at v9.0.63, fill() (lines 213-217) and update() (lines 448-450). Read in: zotero-schema commit 55a1312. Record id `Z7-fill-respects-existing-unless-replace`.

**425.** For read-only libraries BBT keeps generated keys only in a shadow cache persisted to read-only.json under the BBT data dir, never writing them to Zotero.

```
public get path() {
    return PathUtils.join(Zotero.BetterBibTeX.dir, 'read-only.json')
  }
...
      await IOUtils.writeJSON(this.path, this.values(key => {
        // Cache rows can outlive their originating group library; skip rows whose library no longer exists.
        const library = Zotero.Libraries.get(key.libraryID)
        // Persist only read-only-library keys in read-only.json.
        return !!library && readonly(library)
      }))
```

Where: content/key-manager.ts at v9.0.63, CitekeyCache path()/load()/save() (lines 133-167). Read in: zotero-schema commit 55a1312. Record id `Z7-readonly-shadow-store-read-only-json`.

**426.** On the Zotero 8 migration, pinned keys were moved out of the `extra` field into the native field, and BBT migrates its own store to the native field (silently, or via a choice dialog if native keys already exist).

```
* Zotero will have moved all pinned keys out of the `extra` field into the native field
...
* The Zotero-native citation keys are stored in another place than the BBT citation keys. If you have no Zotero-native citation keys yet, BBT will silently migrate them to there. If you do have Zotero-native citation keys, and a migration would overwrite them, you will be offered a windows with the choice on how to migrate your citation keys from the BBT storage to the Zotero storage.
```

Where: site/content/changelog.md at v9.0.63, heading "v8.0.0 (Major Release)". Read in: zotero-schema commit 55a1312. Record id `Z7-migration-extra-to-native`.

**427.** The citekey formula function `pinned` (added v8.0.20, auto-prepended since v8.0.38) reads a legacy pinned key from the `extra` field.

```
* new the `pinned` function for citation key patterns, which retrieves a pinned citation key from the `extra` field.
...
* Citation key pattern update: a new key formula function `pinned` was added, that's always prepended
```

Where: site/content/changelog.md at v9.0.63, headings "v8.0.20" and "v8.0.38". Read in: zotero-schema commit 55a1312. Record id `Z7-pinned-formula-function-reads-extra`.

**428.** Since BBT v9.0.8 the native Zotero citation key field is hidden in the item pane and replaced by a BBT field at the top.

```
* native Zotero citation key field is now hidden and replaced with a field at the top
```

Where: site/content/changelog.md at v9.0.63, heading "v9.0.8". Read in: zotero-schema commit 55a1312. Record id `Z7-native-field-hidden-in-item-pane`.

**429.** BBT 9.0.63 declares minVersion 8.0.1 and maxVersion 10.\* for Zotero.

```
"minVersion": "8.0.1",
 "maxVersion": "10.*
```

Where: package.json at v9.0.63, xpi block (also "version": "9.0.63"). Read in: zotero-schema commit 55a1312. Record id `Z7-bbt-min-max-zotero`.

**430.** Live: api.ready reports Zotero 10.0.1 and BBT 9.0.63.

```
{"jsonrpc":"2.0","result":{"zotero":"10.0.1","betterbibtex":"9.0.63"},"id":1}
```

Where: POST http://localhost:23119/better-bibtex/json-rpc {"method":"api.ready"}, observed 2026-09-05. Read in: zotero-schema commit 55a1312. Record id `Z7-live-api-ready`.

**431.** The Citing page states BBT keys are deterministic across the library, conservative about change, and that pattern changes apply only to later-changed items unless Refresh is used.

```
* Stable citation keys, without key clashes. BBT generates citation keys that take into account other existing keys in your library in a deterministic way, regardless of what part of your library you export, or the order in which you do it.
* BBT is conservative about citation key changes, and allows you to fix keys to any value of your choosing.
...
Changing a pattern will only affect items created/changed after you changed the pattern; existing keys are not automatically regenerated when you change the pattern. If you want your keys to update after a pattern change you will have to select your items, right-click, and select `Refresh`.
```

Where: site/content/citing/\_index.md at v9.0.63, headings "Generating citekeys for your items" and "Configurable citekey generator" (renders at https://retorque.re/zotero-better-bibtex/citing/). Read in: zotero-schema commit 55a1312. Record id `Z7-citing-page-key-stability-and-refresh`.

**432.** The JSON-RPC surface at 9.0.63 is exactly seven namespaces, user, item, items, collection, autoexport, viewer, api, instantiated as fields on a single API singleton.

```
const api = new class API {
  public $user = new NSUser
  public $item = new NSItem
  public $items: NSItem
  public $collection = new NSCollection
  public $autoexport = new NSAutoExport
  public $viewer = new NSViewer
  public $api = new NSAPI
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts lines 686-693 (`const api = new class API`). Read in: Better BibTeX `content/key-manager.ts`. Record id `Z7-rpc-namespaces`.

**433.** The auto-export JSON-RPC API is add-only: NSAutoExport declares exactly one method, `add`, with no list, get, remove or run counterpart.

```
export class NSAutoExport {
  /**
   * Add an auto-export for the given collection. The target collection will be created if it does not exist
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts lines 71-73 (class NSAutoExport; class body ends at line 113 and contains only `public async add(...)` at line 82). Read in: Better BibTeX `content/key-manager.ts`. Record id `Z7-autoexport-add-only`.

**434.** autoexport.add takes (collection path, translator name/GUID, absolute output path, displayOptions, replace) and returns the target collection's libraryID/key/id; without `replace` an incompatible existing auto-export for the same path is an INVALID_PARAMETERS error.

```
      throw { code: INVALID_PARAMETERS, message: 'Auto-export exists with incompatible parameters, but no \'replace\' was requested' }
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts line 95 (NSAutoExport.add); signature at line 82: `public async add(collection: string, translator: string, path: string, displayOptions: Record<string, boolean> = {}, replace = false)`. Read in: Better BibTeX `content/key-manager.ts`. Record id `Z7-autoexport-add-params`.

**435.** item.regenerate_key(citekeys, library?) takes an array of citekeys and an optional library selector, where '\*' searches the personal library and all groups and an omitted library defaults to the user library.

```
   * @param citekeys  Array of citekeys whose items should be regenerated.
   * @param library   The libraryID to search in (optional). Pass `*` to search across your library and all groups.
   */
  public async regenerate_key(citekeys: string[], library?: string | number): Promise<Record<string, string | null>> {
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts lines 480-483 (NSItem.regenerate_key). Read in: Better BibTeX `content/key-manager.ts`. Record id `Z7-regenerate-key-signature`.

**436.** Feed items and non-regular items are silently skipped by regenerate_key: they resolve, so they are not null, but their entry is returned as the unchanged old key.

```
    for (const r of resolved) {
      if (!eligibleIDs.has(r.itemID)) result[r.citekey] = r.oldKey
    }
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts lines 505-507 (NSItem.regenerate_key), after `const eligible = items.filter(item => !item.isFeedItem && item.isRegularItem())` at line 502. Read in: Better BibTeX `content/key-manager.ts`. Record id `Z7-regenerate-key-ineligible`.

**437.** The citekey pin store at 9.0.63 is Zotero's own database: keys live in itemData under the native field named 'citationKey', which KeyManager reads with SQL joins on fields.fieldName = 'citationKey' rather than in any BBT-owned table.

```
    SELECT item.itemID, item.key AS itemKey, item.libraryID, idv.value AS citationKey
    FROM items item
    JOIN itemData id ON item.itemID = id.itemID
    JOIN fields f ON id.fieldID = f.fieldID AND f.fieldName = 'citationKey'
    JOIN itemDataValues idv ON id.valueID = idv.valueID
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/key-manager.ts lines 49-53 (`const sql = { ... load: ... }`). Read in: Better BibTeX `content/key-manager.ts`. Record id `Z7-pin-store-is-native-field`.

**438.** Writing a generated key is a plain Zotero field write to 'citationKey' followed by saveTx with skipDateModifiedUpdate, so a BBT-generated key and a hand-pinned key are indistinguishable in storage.

```
    item.setField('citationKey', proposed)
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/key-manager.ts line 463 (KeyManager.update); persisted at line 253: `await item.saveTx({ skipDateModifiedUpdate: true })`. Read in: Better BibTeX `content/key-manager.ts`. Record id `Z7-pin-write-is-setfield`.

**439.** For read-only (non-editable) libraries BBT keeps a separate shadow store, a JSON file read-only.json in the BBT profile directory, because it cannot write the native field there.

```
  public get path() {
    return PathUtils.join(Zotero.BetterBibTeX.dir, 'read-only.json')
  }
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/key-manager.ts lines 133-135 (class Keys). Read in: Better BibTeX `content/key-manager.ts`. Record id `Z7-readonly-shadow-store`.

**440.** For read-only items a native citationKey coming from outside BBT always wins over the cached shadow key.

```
      // Native keys on read-only items come from outside BBT and always take precedence over the cached shadow key.
      const nativeKey = this.#getNativeKey(item) || ''
      if (nativeKey) {
        this.store(item, nativeKey)
        return
      }
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/key-manager.ts lines 437-442 (KeyManager.update). Read in: Better BibTeX `content/key-manager.ts`. Record id `Z7-readonly-native-precedence`.

**441.** The in-memory key cache is flushed to read-only.json on a 10-second interval timer (and on shutdown), with a generation counter so writes landing during an async flush are not lost.

```
    this.#timer = setInterval(() => { void this.save() }, 10000)
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/key-manager.ts line 149 (Keys.load); shutdown flush at lines 275-277 (`shutdown: async () => { await this.#keys.flush() }`). Read in: Better BibTeX `content/key-manager.ts`. Record id `Z7-cache-flush-10s`.

**442.** Migration copies the old BBT keys into the native citationKey field, writes the read-only-library remainder to read-only.json, and renames better-bibtex.sqlite to better-bibtex.migrated so it runs once.

```
        await IOUtils.writeJSON(PathUtils.join(Zotero.BetterBibTeX.dir, 'read-only.json'), readonly)

        try {
          const renamed = await Zotero.File.rename(sqlite, 'better-bibtex.migrated', { unique: true })
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/key-manager/migrate.ts lines 187-190 (function migrate); the field write is at lines 179-180: `item.setField('citationKey', citationKey)` / `await item.save({ skipDateModifiedUpdate: true, skipNotifier: !!choice.zotero })`. Read in: Better BibTeX `content/key-manager.ts`. Record id `Z7-migration-writes-native-and-renames-db`.

**443.** Old citekeys are retained as aliases in a 'Citation Key Alias' Extra line (comma-separated), and when a regenerated key equals one of those aliases KeyManager removes it from the alias list.

```
      const aliases = Extra.get(item.getField('extra'), 'zotero', { aliases: true })
      if (aliases.extraFields.aliases?.includes(citationKey)) {
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/key-manager.ts lines 235-236 (KeyManager.fill); the Extra parser key is at content/extra.ts line 173: `if (options.aliases && key === 'citation key alias') {`. Read in: Better BibTeX `content/key-manager.ts`. Record id `Z7-citekey-aliases-in-extra`.

**444.** Uniqueness postfixing is scoped by the keyScope preference (global across libraries vs per-library) and compared case-sensitively or not per citekeyCaseInsensitive; conflicts are resolved by incrementing an Excel-column postfix.

```
    const caseInsensitive = Preference.citekeyCaseInsensitive
    const keyscopeGlobal = Preference.keyScope === 'global'
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/key-manager.ts lines 493-494 (KeyManager.propose); conflict predicate at lines 503-507. Read in: Better BibTeX `content/key-manager.ts`. Record id `Z7-keyscope-and-uniqueness`.

**445.** BBT can mark colliding keys by tagging items with the literal tag '#duplicate-citation-key', adding it to newly-duplicated items and removing it when the duplication is gone.

```
    const tag = '#duplicate-citation-key'
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/key-manager.ts line 533 (KeyManager.tagDuplicates). Read in: Better BibTeX `content/key-manager.ts`. Record id `Z7-duplicate-tag`.

**446.** Citation keys are only ever assigned to regular items: attachments, notes, annotations, feed items and trashed items are excluded by both the SQL and the in-code guards.

```
      AND item.itemTypeID NOT IN (SELECT itemTypeID FROM itemTypes WHERE typeName IN ('attachment', 'note', 'annotation'))
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/key-manager.ts line 56 (sql.load); in-code guard at line 426: `if (item.isFeedItem || !item.isRegularItem()) return`. Read in: Better BibTeX `content/key-manager.ts`. Record id `Z7-no-keys-for-attachments-notes`.

**447.** The default citekey pattern is `auth.lower + shorttitle(3,3) + year`, with an always-appended letter postfix on clashes that cannot be disabled (only switched to Zotero-style numeric).

```
The default key pattern is `auth.lower + shorttitle(3,3) + year`; if you have papers that use keys which were generated by the key generator of the standard Bib(La)TeX exporters of Zotero you may want to use `zotero.clean` instead in order to ease migration from existing exports for people who previously used the standard Zotero Bib(La)TeX exports.
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/site/content/citing/_index.md, heading '## Configurable citekey generator'. Read in: Better BibTeX `content/key-manager.ts`. Record id `Z7-default-formula`.

**448.** The handler uses standard JSON-RPC 2.0 error codes, returning METHOD_NOT_FOUND (-32601) both for an unknown namespace/method and for a method whose generated schema is missing.

```
    if (!method) return { jsonrpc: '2.0', error: { code: METHOD_NOT_FOUND, message: `Method not found: ${ request.method }` }, id: null }
```

Where: https://github.com/retorquere/zotero-better-bibtex/blob/cfdba6ac507a0b49a99d4b23fc4fed359edebc5d/content/json-rpc.ts line 714 (API.handle); code constants declared at lines 24-28. Read in: Better BibTeX `content/key-manager.ts`. Record id `Z7-rpc-error-codes`.

## Live measurements, 2026-09-13 — Task 20 of Part A (test instance, Zotero 10.0.2 / Better BibTeX 9.0.64, server id `Tdoqsn2J4q4h`)

Measured by the attended propagate leg; the operator answered one consent dialog. Production received one read-only probe.

**449.** Live: the Zotero 10.0.2 local API accepts a `PATCH` of the native `citationKey` field on a regular item; Better BibTeX 9.0.64 adopts the new key within about two seconds without touching `extra`, and the lifecycle linter reports the item `re-keyed`. This is the mechanism Part B Task 5's automated leg can use; the Extra-line fallback was not needed and was not exercised.

```
PATCH http://localhost:23129/api/users/0/items/ALKT2NF7
headers: Content-Type: application/json; If-Unmodified-Since-Version: 1708; Zotero-Server-ID: Tdoqsn2J4q4h; Zotero-API-Key: <32-char key from /api/local/authorize, remember=true>
body: {"citationKey": "aston-jones2005INTEGRATIVEleg"}
HTTP 204 in 0.11 s
X-Zotero-Version: 10.0.2
X-Zotero-Connector-API-Version: 3
Last-Modified-Version: 1714
Zotero-API-Version: 3
Zotero-Schema-Version: 44
Zotero-Server-ID: Tdoqsn2J4q4h
Content-Length: 0
(empty body)
```

Then, polled once a second: `GET …/items/ALKT2NF7?format=json` answered `version 1714, data.citationKey "aston-jones2005INTEGRATIVEleg", extra "sitting probe"` from the first read (t+0 s); BBT JSON-RPC `item.citationkey [["ALKT2NF7"]]` still answered the old key at t+0 s and t+1 s and the new key at t+2 s. `capture ALKT2NF7` on a vault whose note records the old key then printed `UNMATCHED ALKT2NF7 — re-keyed — aston-jones2005INTEGRATIVE → aston-jones2005INTEGRATIVEleg; run propagate`.

Where: the test instance, Zotero 10.0.2 / server id `Tdoqsn2J4q4h` / Better BibTeX 9.0.64, item `ALKT2NF7`, item version 1708 → 1714, observed 2026-09-13T16:28:58Z. Sent through `ZoteroClient._http` with `ZoteroClient._headers`, attended (Task 20 Step 1's propagate leg). Read in: Task 20 attended leg, 2026-09-13. Record id `Z6-live-patch-native-citationKey-accepted`.

**450.** Live: the same `PATCH` restores the original key; a second write with a reusable (`remember: true`) key needs no second `authorize`. Better BibTeX again lagged Zotero by about two seconds. The item's `dateModified` and version are the only residue.

```
PATCH http://localhost:23129/api/users/0/items/ALKT2NF7
headers: Content-Type: application/json; If-Unmodified-Since-Version: 1714; Zotero-Server-ID: Tdoqsn2J4q4h; Zotero-API-Key: <same key as record 449>
body: {"citationKey": "aston-jones2005INTEGRATIVE"}
HTTP 204 in 0.39 s
X-Zotero-Version: 10.0.2
X-Zotero-Connector-API-Version: 3
Last-Modified-Version: 1715
Zotero-API-Version: 3
Zotero-Schema-Version: 44
Zotero-Server-ID: Tdoqsn2J4q4h
Content-Length: 0
(empty body)
```

Polled: GET answered `version 1715, citationKey "aston-jones2005INTEGRATIVE", extra "sitting probe"` at t+0 s; BBT `item.citationkey` answered the leg's key at t+0 s and t+1 s and the original at t+2 s. Final read: `version 1715, citationKey "aston-jones2005INTEGRATIVE", extra "sitting probe", dateModified "2026-09-13T16:30:13Z"`; BBT `{"ALKT2NF7":"aston-jones2005INTEGRATIVE"}`.

Where: same instance and item, item version 1714 → 1715, observed 2026-09-13T16:30:13Z. Read in: Task 20 attended leg, 2026-09-13. Record id `Z6-live-patch-native-citationKey-restore`.

**451.** Live: `POST /api/local/authorize` on Zotero 10.0.2 with `Zotero-Server-ID` and body `{"appName": "research-vault"}` blocked 5.0 s until the person answered Always Allow, then returned a 32-character key with `remember: true`. One call, one dialog; the key served two writes.

```
POST http://localhost:23129/api/local/authorize  (Zotero-Server-ID: Tdoqsn2J4q4h; Content-Type: application/json; body {"appName": "research-vault"})
answered after 5.0 s: remember=True key_len=32
```

Where: the test instance, observed 2026-09-13T16:28:46Z–16:28:51Z, through `ZoteroClient.authorize()` with `timeout=180`. Read in: Task 20 attended leg, 2026-09-13. Record id `Z1-live-authorize-always-allow-10.0.2`.

**452.** Live: `GET /api/users/0/items/trash?format=versions`, as `ZoteroClient.trash_versions()` sends it, answers 200 with a flat map of 212 trashed-item keys to integer versions — the corroboration behind `trash_versions`'s reading, which the spec's own measurement had none of.

```
GET http://localhost:23129/api/users/0/items/trash?format=versions
headers: Zotero-Server-ID: Tdoqsn2J4q4h
HTTP 200
X-Zotero-Version: 10.0.2
X-Zotero-Connector-API-Version: 3
Total-Results: 212
Link: <http://localhost:23129/api/users/0/items/trash?format=versions>; rel="last", <https://www.zotero.org/users/16413661/items/trash>; rel="alternate"
Last-Modified-Version: 1715
Content-Type: application/json
Zotero-API-Version: 3
Zotero-Schema-Version: 44
Zotero-Server-ID: Tdoqsn2J4q4h
body: a flat object of 212 entries, each key → an integer version; one example: "HEJXIP6W": 14
```

Where: the test instance, Zotero 10.0.2 / server id `Tdoqsn2J4q4h`, observed 2026-09-16T19:54:59Z. Sent through `ZoteroClient._http` with `ZoteroClient._headers`. Read in: Part B Task 5 attended half, 2026-09-16. Record id `Z2-live-trash-versions-map`.

**453.** Live, re-measured a second time: `GET /api/users/0/items/top?format=csljson&limit=1` still answers 200 with a CSL JSON body on this instance — the same route the spec's §9 row measured 500 on 2026-09-04 (Zotero 10.0.1) and Part A's Task 16 leg measured 200 on 2026-09-13. The answer's `Content-Type` is `text/plain`, not `application/json`, even though the body is a JSON array.

```
GET http://localhost:23129/api/users/0/items/top?format=csljson&limit=1
headers: Zotero-Server-ID: Tdoqsn2J4q4h
HTTP 200
X-Zotero-Version: 10.0.2
X-Zotero-Connector-API-Version: 3
Total-Results: 1461
Link: <http://localhost:23129/api/users/0/items/top?format=csljson&limit=1&start=1460>; rel="last", <http://localhost:23129/api/users/0/items/top?format=csljson&limit=1&start=1>; rel="next", <https://www.zotero.org/users/16413661/items/top>; rel="alternate"
Last-Modified-Version: 1715
Content-Type: text/plain
Zotero-API-Version: 3
Zotero-Schema-Version: 44
Zotero-Server-ID: Tdoqsn2J4q4h
body: a JSON array of one CSL item; the item's "id" is "aston-jones2005INTEGRATIVE", its "type" is "article-journal"
```

Where: the test instance, Zotero 10.0.2 / server id `Tdoqsn2J4q4h` / Better BibTeX 9.0.64 (`ready()`: `{"zotero": "10.0.2", "betterbibtex": "9.0.64"}`), observed 2026-09-16T19:55:06Z. Sent through `ZoteroClient._http` with `ZoteroClient._headers`. Read in: Part B Task 5 attended half, 2026-09-16. Record id `Z1-live-csljson-reopened-again`.
