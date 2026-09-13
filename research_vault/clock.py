"""The one clock a check reads (ingest spec §7, `verify --as-of`; decision 28).

A stamp records when something happened and may read the wall clock through a
`now=` parameter. A check decides whether something is stale and must take the
instant as an argument, or its verdict is not reproducible: a fixture recorded
in September would fail in December for no reason present in the fixture.
Every date default in the package resolves through today(); a test scans for
any other reader of today's date.
"""

import datetime
import re

# date.fromisoformat is wider than the promise this module makes: measured
# 2026-09-08 on this interpreter, "20260102" parses as 2026-01-02 and the ISO week
# date "2026-W01-1" parses as 2025-12-29 -- an instant a reader of the flag would
# never recognise as the day they asked for. The shape is checked first, so the
# error message is true.
_YYYY_MM_DD = re.compile(r"\d{4}-\d{2}-\d{2}")


def today(as_of: str | None = None) -> str:
    """Return ``as_of`` validated as YYYY-MM-DD, else today's UTC date."""
    if as_of is None:
        return datetime.datetime.now(datetime.UTC).date().isoformat()
    if _YYYY_MM_DD.fullmatch(as_of) is None:
        raise ValueError(f"--as-of must be YYYY-MM-DD, got {as_of!r}")
    try:
        return datetime.date.fromisoformat(as_of).isoformat()
    except ValueError as error:
        raise ValueError(f"--as-of must be YYYY-MM-DD, got {as_of!r}") from error
