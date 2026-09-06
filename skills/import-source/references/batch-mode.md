# Batch mode

Disposition: current (2026-09-06)

For a backfill — refreshing every literature note in the vault:

```sh
python3 -m research_vault backfill-selectors --vault PATH
```

This re-imports every note in `literatures/`, in citekey order, with the same per-note contract as above: each note comes back fresh, stale, or orphaned, and every failure files its own record. Exit `0` means every note succeeded; exit `1` means at least one did not — read the printed warnings, then run `inbox` to see the records they filed:

```sh
python3 -m research_vault inbox --vault PATH
```

Report the per-note breakdown, not just the exit code. A batch that ends `1` because one item left the library is not a broken backfill.
