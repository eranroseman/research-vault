# Better BibTeX owns the bibliography export

Status: accepted (2026-08-30)

Better BibTeX is the sole content writer of `system/bibliography.json`: research-vault observes
it, compares it against an on-demand export of the same scope, and commits only a byte-exact
match. What a citekey names has one origin — the admitted Zotero library as BBT renders it.

## Considered Options

**research-vault generates the export from the Zotero API.** Rejected: a second minting
authority over the vault's one address space (ADR 0004). Byte-compatibility with keys already in
every filename and citation would also mean reimplementing BBT's CSL translator.

**A human maintains the export by hand.** Rejected: the library runs past a thousand items and
grows with every admission, so a hand-maintained file drifts on the first one — silently.

**A scoped export from a curated Zotero collection.** Rejected: a source would stop resolving
because someone reorganised a Zotero collection, with no record in the vault of why.
Whole-library scope keeps the universe stable and leaves project scoping to the vault, where
checks can see it.

## Consequences

A human creates the export once, in BBT. research-vault reports a missing or mismatched export
with the exact repair; it never registers one.

The export is the vault's only bibliographic record. Author, date, and venue have no second
authoritative home — any appearance elsewhere is a projection from it — which is why pandoc
reads it directly as Better CSL JSON.

Membership in the export is not permission to cite. BBT writes the whole admitted library, blind
to what this vault imported or screened; checks make the citability judgment.
