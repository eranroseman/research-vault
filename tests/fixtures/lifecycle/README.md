# Lifecycle fixtures

Trimmed excerpts of the versions maps recorded on the Zotero test instance
(server id `Tdoqsn2J4q4h`, port 23129) during the 2026-09-07 sitting; the full
maps live outside the repository at `~/zotero-test-sitting/findings/`. Each file
keeps only the keys the tests name. Shapes are the observed shapes: flat
`{"<ITEMKEY>": <version>}` maps.

- `items-before.json` / `trash-before.json` — the baseline.
- `items-after-delete.json` — `ALKT2NF7` moved 0 → 1708 by a human edit (drifted).
- `trash-trashed.json` — superseded by `items-trashed.json`, recorded live on
  2026-09-16 by `tests/test_capture_live.py`; the transition now replays.
- `trash-after-delete.json` — `II7E6CVR` gone from both maps (deleted; replays).
- `items-trashed.json` — `4E5FHBVD` live at 1721, then trashed at 1722;
  recorded live on 2026-09-16 by `tests/test_capture_live.py`'s attended
  write leg. Two measured facts from that sitting:
  - The consent dialog re-opened on a second run against a fresh `tmp_vault`
    (a fresh `tmp_vault` has no key store, so the dialog re-opened; measured
    2026-09-16), so an unattended re-run needs `RV_LIVE_WRITE_KEY` exported
    from an attended run's `<basetemp>/<test dir>/.research-vault/zotero-keys.json`.
  - `pyproject.toml`'s `tmp_path_retention_policy = "failed"` deletes a
    PASSING test's `tmp_vault`, fixture included — the attended run that
    records the fixture must pass `-o tmp_path_retention_policy=all` beside
    `--basetemp` (measured 2026-09-16: the first passing run's fixture was gone;
    the second, with the option, retained it).
