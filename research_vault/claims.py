"""Parser for §5 claim lines — the shared reader every checker and lint uses."""

import re
from dataclasses import dataclass, field

CLAIM_RE = re.compile(
    r"^- \((quote|paraphrase|inference|open-question)\) (?P<rest>.*)$"
)
CITE_RE = re.compile(r"\[@(?P<key>[A-Za-z0-9_.:-]+)(?:, (?P<loc>[^\]]+))?\]")
ANCHOR_RE = re.compile(r"\^(?P<id>[A-Za-z0-9-]+)\s*$")
# Field values may contain [[wikilinks]]; a naive [^\]]* would truncate them.
FIELD_RE = re.compile(r"\[(?P<k>[A-Za-z-]+):: (?P<v>(?:[^\[\]]|\[\[[^\]]*\]\])*)\]")


@dataclass
class Claim:
    tag: str
    citation_key: str | None
    locator: str | None
    claim_id: str | None
    line_no: int
    quote_text: str | None = None
    fields: dict[str, str] = field(default_factory=dict)


def claim_link(citation_key: str, claim_id: str) -> str:
    return f"{citation_key}#^{claim_id}"


def parse_claims(text: str) -> list[Claim]:
    """Return claims found in any note body, retaining their source metadata."""
    parsed_claims: list[Claim] = []
    current_quote: Claim | None = None

    for line_no, line in enumerate(text.splitlines(), start=1):
        match = CLAIM_RE.match(line)
        if match:
            rest = match.group("rest")
            citation = CITE_RE.search(rest)
            anchor = ANCHOR_RE.search(rest)
            fields = {
                field_match.group("k"): field_match.group("v")
                for field_match in FIELD_RE.finditer(rest)
            }
            current_quote = Claim(
                tag=match.group(1),
                citation_key=citation.group("key") if citation else None,
                locator=citation.group("loc") if citation else None,
                claim_id=anchor.group("id") if anchor else None,
                line_no=line_no,
                fields=fields,
            )
            parsed_claims.append(current_quote)
            if current_quote.tag != "quote":
                current_quote = None
            continue

        if current_quote is not None and line.startswith("  > "):
            quote_line = line[4:]
            if current_quote.quote_text is None:
                current_quote.quote_text = quote_line
            else:
                current_quote.quote_text = f"{current_quote.quote_text} {quote_line}"
            continue

        current_quote = None

    return parsed_claims
