# Archive at import (web sources)

Disposition: current (2026-09-06)

A source with a `url` and no `doi` is a web source, and web content rots. Rescue is impossible after the fact, so the snapshot has to exist **now**, at import — later detection cannot bring a dead page back. Run this for every web source you catalog, in the same session:

```sh
python3 -m research_vault archive-source CITEKEY --vault PATH
```

The verb triggers Internet Archive Save Page Now, confirms the capture against the Wayback availability API, and writes the confirmed snapshot into the note's frontmatter as `archive-url`. **It is the sole writer of that field** — never hand-write, edit, or remove an `archive-url` yourself, in any note, for any reason. That single owner is what keeps the evidence layer machine-written.

If the person already has a snapshot, record that one instead of capturing a fresh one — the verb confirms it resolves before writing it:

```sh
python3 -m research_vault archive-source CITEKEY --vault PATH --snapshot SNAPSHOT-URL
```

It answers with a four-state line and the shared exit codes:

| Exit | Result      | Meaning                                                                                                                |
| ---- | ----------- | ---------------------------------------------------------------------------------------------------------------------- |
| `0`  | MATCHED     | A snapshot is recorded — freshly captured, supplied, or already present. The snapshot URL prints on the next line.     |
| `0`  | SKIPPED     | Not a web source (it has a `doi`, or no `url`). Nothing to archive, and nothing wrong.                                 |
| `1`  | UNMATCHED   | The archive is serving no snapshot for that URL, or the supplied one 404s. Nothing was written.                        |
| `3`  | UNREACHABLE | Save Page Now or the confirmation call could not be reached. **An outage, not a verdict** — retry on the next refresh. |
| `2`  | —           | The verb could not run: no such note, an unsafe citekey, malformed frontmatter. Read the message back verbatim.        |

Never present an UNREACHABLE archive attempt as archived, and never write a URL the verb declined to record — an outage is not a snapshot. `archive-url` is pass-through metadata, so a recorded snapshot survives every later re-render; `accessed` is captured on day one and never overwritten.

`verify`'s `web-archive` check is the reader on the other side: it files a `missing-archive` finding when a web source has no `archive-url`, or when the recorded one no longer resolves. That check only ever detects — this verb is the only thing that captures.
