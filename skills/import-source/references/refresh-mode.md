# Refresh mode: fresh, stale, orphaned

Refresh is note-level maintenance, and it is the same verb — re-running `import-note` for a citekey that already has a note. Three outcomes, and these are the words to use:

| Word         | What it means                                                                                 | How the CLI says it                                                                                             |
| ------------ | --------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **fresh**    | The projection matches Zotero.                                                                | `import-note` prints `NOOP`, exit `0`.                                                                          |
| **stale**    | Re-rendering differs, so the managed region was rewritten. The free region below it survives. | `import-note` prints the note path, exit `0`.                                                                   |
| **orphaned** | The note's item has left the library, so nothing projects onto it any more.                   | `import-note` reports `citekey not found` on stderr, exit `1`, and files the `citekey` / `not-admitted` record. |

One honest limit: **orphan detection is per-citekey**. `verify` reports an orphaned note as a `citekey` UNMATCHED only if the note still cites itself, and a note with no quote or paraphrase claims cites nothing at all — so a sweep with `import-note` is the only way to find every orphan.

An orphaned note is never deleted. Records deprecate, never delete — the note stays, and the person decides what its screening state should become.
