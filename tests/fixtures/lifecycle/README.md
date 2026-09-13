# Lifecycle fixtures

Trimmed excerpts of the versions maps recorded on the Zotero test instance
(server id `Tdoqsn2J4q4h`, port 23129) during the 2026-09-07 sitting; the full
maps live outside the repository at `~/zotero-test-sitting/findings/`. Each file
keeps only the keys the tests name. Shapes are the observed shapes: flat
`{"<ITEMKEY>": <version>}` maps.

- `items-before.json` / `trash-before.json` — the baseline.
- `items-after-delete.json` — `ALKT2NF7` moved 0 → 1708 by a human edit (drifted).
- `trash-trashed.json` — `II7E6CVR` present at 1712 (trashed); **non-replayable
  as a transition**: no snapshot holds the item while it was live — it is absent
  from every items map here — so the pair shows only its arrival in the trash
  map, never its departure from the items map. Part B Task 5 takes the missing
  snapshot.
- `trash-after-delete.json` — `II7E6CVR` gone from both maps (deleted; replays).
