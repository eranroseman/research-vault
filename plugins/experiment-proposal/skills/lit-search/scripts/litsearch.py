#!/usr/bin/env python3
"""litsearch.py: the lit-search skill's one entry point, over the nine scripts
vendored beside it from hutzelmann/thesis-proposal-skills (MIT, v0.9.0).

Usage:
    litsearch.py search "<query>" [--limit N] [--sources a,b,c]
                 [--dblp-query "<two or three terms>"] [--exclude FILE]
                 [--compact | --full] [--out FILE]
    litsearch.py snowball <DOI> [--direction both|backward|forward] [--limit-per-seed N]
                 [--exclude FILE] [--compact | --full] [--out FILE]

The records go to stdout as CSL-YAML with every string a double-quoted JSON
scalar, each character outside YAML's printable set, and the line breaks NEL,
U+2028 and U+2029, escaped and a lone surrogate made U+FFFD, valid YAML whatever
a title holds; compact by default (title, author surnames, year, venue, DOI,
abstract cut to 300 characters), --full adds given names, URL, type and source
and cuts the abstract at 1,500. --exclude names the judged file, one record per
line `<DOI or title> | <kept or rejected> | <reason>`, of which only the first
field is read; every record whose DOI or title it holds is dropped, except, in
search mode, a record whose title is the query itself (compared normalized):
that search is the title lookup for a source's DOI, and the source is in the
judged file by its title. --out writes the records to that file instead.

Stderr carries the vendored scripts' own notes verbatim, then one line per
index `<index>(<returned>, <kept>) query="<query>"`, the line
`semantic_scholar: skipped (HTTP 429); snowball's graph endpoints cover it`
when that index refused a search, `kept "<title>" despite the exclude: it is
the title searched for` for each record the exception keeps, and
`candidates: N (after exclude: M)`.

Exit 0: records printed or written. Exit 1: no record left, the round added
nothing. Exit 2: a file could not be read or written, the arguments were
malformed, or the interpreter is older than 3.11.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING, TextIO

if TYPE_CHECKING:
    from collections.abc import Sequence

# The vendored siblings import each other by bare name: first on sys.path when
# this file runs as a script, and put there for any other caller.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import common
import dblp
import search
import snowball

ABSTRACT_COMPACT = 300
ABSTRACT_FULL = 1500
DEGRADED_429 = "note: source degraded — semantic_scholar: HTTP 429"
SKIP_429 = "semantic_scholar: skipped (HTTP 429); snowball's graph endpoints cover it"
KEPT_SEARCHED = 'kept "{title}" despite the exclude: it is the title searched for'
DEFAULT_SOURCES = [name for name in search.SEARCH_SOURCES if name != "dblp"]
# What JSON leaves raw and a YAML parser refuses or alters: the characters
# outside YAML's printable set (DEL, the C1 controls, U+FFFE, U+FFFF) and the
# line breaks NEL (U+0085), U+2028 and U+2029, which YAML folds together with
# the spaces beside them. Each is escaped as \uXXXX.
NOT_YAML_PRINTABLE = re.compile(
    r"[^\t\n\r\x20-\x7e\xa0-\u2027\u202a-\ud7ff\ue000-\ufffd\U00010000-\U0010ffff]"
)
# Half a UTF-16 pair, from a \ud800-style escape in a server's JSON: no
# character, so no UTF-8 file and no YAML parser holds it; it becomes U+FFFD.
LONE_SURROGATE = re.compile(r"[\ud800-\udfff]")


class Tee(io.TextIOBase):
    """Writes to a stream and keeps a copy: the vendored notes reach stderr
    verbatim and can still be read afterwards. (Accepted by mypy as the
    argument of contextlib.redirect_stderr; probed 2026-10-24 with the repo's
    mypy at check_untyped_defs.)"""

    def __init__(self, stream: TextIO) -> None:
        self.stream = stream
        self.copy = io.StringIO()

    def write(self, text: str) -> int:
        self.stream.write(text)
        self.copy.write(text)
        return len(text)

    def flush(self) -> None:
        self.stream.flush()


def read_exclude(path: Path) -> tuple[set[str], set[str]]:
    """The first field of every record line, read as a DOI and as a title."""
    dois: set[str] = set()
    titles: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        first = raw.split("|", 1)[0].strip()
        if not first or first.startswith("#"):
            continue
        if doi := common.clean_doi(first):
            dois.add(doi)
        if title := common.normalize_title(first):
            titles.add(title)
    return dois, titles


def excluded(record: dict, dois: set[str], titles: set[str]) -> bool:
    doi = common.clean_doi(record.get("DOI"))
    title = common.normalize_title(record.get("title", ""))
    return (doi is not None and doi in dois) or (bool(title) and title in titles)


def apply_exclude(
    records: Sequence[dict], dois: set[str], titles: set[str], searched: str
) -> tuple[list[dict], list[dict]]:
    """The records the exclude leaves, and among them those it names but keeps:
    a record whose normalized title is `searched`, the normalized query of a
    search (empty for a snowball), is the paper a title lookup is for."""
    kept: list[dict] = []
    despite: list[dict] = []
    for record in records:
        if not excluded(record, dois, titles):
            kept.append(record)
        elif searched and common.normalize_title(record.get("title", "")) == searched:
            kept.append(record)
            despite.append(record)
    return kept, despite


def sources_of(record: dict) -> list[str]:
    return [tag for tag in str(record.get("_source", "")).split(",") if tag]


def source_lines(
    queries: dict[str, str],
    records: Sequence[dict],
    kept: Sequence[dict],
    default_query: str,
) -> list[str]:
    """`<index>(<returned>, <kept>) query="..."` for every queried index;
    returned counts the records carrying the index's tag after the vendored
    de-duplication, kept those left after the exclude."""
    counts: dict[str, list[int]] = {tag: [0, 0] for tag in queries}
    for record in records:
        for tag in sources_of(record):
            counts.setdefault(tag, [0, 0])[0] += 1
    for record in kept:
        for tag in sources_of(record):
            counts.setdefault(tag, [0, 0])[1] += 1
    return [
        f'{tag}({returned}, {left}) query="{queries.get(tag, default_query)}"'
        for tag, (returned, left) in sorted(counts.items())
    ]


def scalar(value: object) -> str:
    """A YAML double-quoted scalar: JSON's string form is a subset of YAML's
    once the characters YAML cannot hold raw are escaped."""
    text = json.dumps(LONE_SURROGATE.sub("\ufffd", str(value)), ensure_ascii=False)
    return NOT_YAML_PRINTABLE.sub(lambda match: f"\\u{ord(match[0]):04x}", text)


def to_yaml(records: Sequence[dict], *, compact: bool) -> str:
    lines: list[str] = []
    for record in records:
        lines.append(f"- title: {scalar(record.get('title', ''))}")
        if authors := record.get("author"):
            lines.append("  author:")
            for author in authors:
                lines.append(f"  - family: {scalar(author.get('family', ''))}")
                if not compact and author.get("given"):
                    lines.append(f"    given: {scalar(author['given'])}")
        if year := (record.get("issued") or {}).get("year"):
            lines.append("  issued:")
            lines.append(f"    year: {year if str(year).isdigit() else scalar(year)}")
        if venue := record.get("container-title"):
            lines.append(f"  container-title: {scalar(venue)}")
        if doi := record.get("DOI"):
            lines.append(f"  DOI: {scalar(doi)}")
        elif not compact and (url := record.get("URL")):
            lines.append(f"  URL: {scalar(url)}")
        if not compact:
            lines.append(f"  type: {scalar(record.get('type', 'article-journal'))}")
            lines.append(f"  source: {scalar(record.get('_source', ''))}")
        if abstract := record.get("abstract"):
            cut = ABSTRACT_COMPACT if compact else ABSTRACT_FULL
            lines.append(f"  abstract: {scalar(abstract[:cut])}")
    return "\n".join(lines) + "\n" if lines else ""


def run_search(args: argparse.Namespace) -> tuple[list[dict], dict[str, str]]:
    """The vendored federate over the main indexes, then DBLP on its own short
    query, de-duplicated together; returns the records and each index's query."""
    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    records = search.federate(args.query, args.limit, sources)
    queries = dict.fromkeys(sources, args.query)
    if args.dblp_query:
        # DBLP's failures are noted as search.federate notes them, its browser
        # hint included: DBLP is the index that sends verification pages.
        extra: list[dict] = []
        try:
            extra = dblp.search(args.dblp_query, limit=args.limit)
        except common.SourceError as exc:
            note = f"note: source degraded — {exc}"
            if exc.kind == "challenge":
                note += ". " + search.BROWSER_HINT.format(source="dblp")
            print(note, file=sys.stderr)
        except Exception as exc:  # a broken source must never block the search
            # the type only: an error's own text can carry what a server sent
            print(
                f"note: source failed unexpectedly — dblp: {type(exc).__name__}",
                file=sys.stderr,
            )
        records = common.dedupe([*records, *extra])
        queries["dblp"] = args.dblp_query
    return records, queries


def run_snowball(args: argparse.Namespace) -> tuple[list[dict], dict[str, str]]:
    """The vendored expand and enrichment for one seed, the seed itself dropped.
    The enrichment replaces a bare DOI with Crossref's record, tagged crossref;
    the tag of the index that found the DOI is put back."""
    expanded = snowball.expand([args.doi], args.limit_per_seed, args.direction)
    found_by = {
        common.clean_doi(item.get("DOI")): item.get("_source")
        for item in expanded
        if item.get("DOI") and not item.get("title")
    }
    enriched = snowball.enrich_bare_dois(expanded)
    for record in enriched:
        if tag := found_by.get(common.clean_doi(record.get("DOI"))):
            record["_source"] = tag
    merged = common.dedupe(enriched)
    seed = common.clean_doi(args.doi)
    left = [record for record in merged if record.get("DOI") != seed]
    return left, dict.fromkeys(snowball.GRAPH_SOURCES, args.doi)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    commands = parser.add_subparsers(dest="command", required=True)
    searcher = commands.add_parser("search")
    searcher.add_argument("query")
    searcher.add_argument("--limit", type=int, default=10)
    searcher.add_argument("--sources", default=",".join(DEFAULT_SOURCES))
    searcher.add_argument(
        "--dblp-query",
        help="two or three terms for DBLP, which matches each as a prefix",
    )
    snowballer = commands.add_parser("snowball")
    snowballer.add_argument("doi")
    snowballer.add_argument(
        "--direction", choices=["both", "backward", "forward"], default="both"
    )
    snowballer.add_argument(
        "--limit-per-seed", type=int, default=snowball.DEFAULT_PER_SEED
    )
    for sub in (searcher, snowballer):
        sub.add_argument(
            "--exclude", type=Path, help="the judged file; its first fields are dropped"
        )
        form = sub.add_mutually_exclusive_group()
        form.add_argument(
            "--compact",
            action="store_true",
            help="the default: surnames only, the abstract cut to 300 characters",
        )
        form.add_argument(
            "--full",
            action="store_true",
            help="every vendored field; the default is compact",
        )
        sub.add_argument(
            "--out", type=Path, help="write the records here instead of stdout"
        )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    # The script runs standalone on whatever python3 the user has.
    if sys.version_info < (3, 11):  # noqa: UP036
        print("litsearch.py needs Python 3.11 or later", file=sys.stderr)
        return 2
    common.utf8_output()
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "search":
        requested = [s.strip() for s in args.sources.split(",") if s.strip()]
        if unknown := [s for s in requested if s not in search.SEARCH_SOURCES]:
            parser.error(
                f"unknown source(s): {', '.join(unknown)}; valid: {', '.join(search.SEARCH_SOURCES)}"
            )
    dois: set[str] = set()
    titles: set[str] = set()
    if args.exclude is not None:
        try:
            dois, titles = read_exclude(args.exclude)
        except OSError as error:
            print(f"{args.exclude}: cannot read: {error}", file=sys.stderr)
            return 2
    tee = Tee(sys.stderr)
    with contextlib.redirect_stderr(tee):
        records, queries = (
            run_search(args) if args.command == "search" else run_snowball(args)
        )
    searched = common.normalize_title(args.query) if args.command == "search" else ""
    kept, despite = apply_exclude(records, dois, titles, searched)
    default_query = args.query if args.command == "search" else args.doi
    for line in source_lines(queries, records, kept, default_query):
        print(line, file=sys.stderr)
    if args.command == "search" and DEGRADED_429 in tee.copy.getvalue():
        print(SKIP_429, file=sys.stderr)
    for record in despite:
        title = " ".join(str(record.get("title", "")).split())
        print(KEPT_SEARCHED.format(title=title), file=sys.stderr)
    print(f"candidates: {len(records)} (after exclude: {len(kept)})", file=sys.stderr)
    if not kept:
        print("no candidates left this round", file=sys.stderr)
        return 1
    text = to_yaml(kept, compact=not args.full)
    if args.out is not None:
        try:
            args.out.write_text(text, encoding="utf-8")
        except OSError as error:
            print(f"{args.out}: cannot write: {error}", file=sys.stderr)
            return 2
        print(f"wrote {len(kept)} records to {args.out}", file=sys.stderr)
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
