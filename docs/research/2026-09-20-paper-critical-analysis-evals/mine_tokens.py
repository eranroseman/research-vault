#!/usr/bin/env python3
"""Sum fresh input tokens over Claude Code transcripts.

Usage: python3 mine_tokens.py LABEL=transcript.jsonl [LABEL=transcript.jsonl ...]

"Fresh" is the comparison runs' definition (run3-setup.md, 2026-10-04):
uncached input plus cache-write, per API call — ``usage.input_tokens`` +
``usage.cache_creation_input_tokens`` on every assistant message. Cache reads
and output tokens are reported beside it. One row per label, then a total.
"""

import json
import sys
from pathlib import Path


def usage_rows(path: Path):
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        usage = (record.get("message") or {}).get("usage")
        if isinstance(usage, dict):
            yield usage


def totals(path: Path) -> tuple[int, int, int]:
    fresh = cached = output = 0
    for usage in usage_rows(path):
        fresh += usage.get("input_tokens", 0) + usage.get(
            "cache_creation_input_tokens", 0
        )
        cached += usage.get("cache_read_input_tokens", 0)
        output += usage.get("output_tokens", 0)
    return fresh, cached, output


def main(argv: list[str]) -> int:
    if not argv:
        sys.stderr.write(__doc__)
        return 2
    grand = [0, 0, 0]
    sys.stdout.write(
        f"{'agent':<12} {'fresh in':>12} {'cache read':>12} {'output':>10}\n"
    )
    for arg in argv:
        label, _, raw = arg.partition("=")
        fresh, cached, output = totals(Path(raw or label))
        grand = [a + b for a, b in zip(grand, (fresh, cached, output), strict=True)]
        sys.stdout.write(f"{label:<12} {fresh:>12,} {cached:>12,} {output:>10,}\n")
    sys.stdout.write(f"{'total':<12} {grand[0]:>12,} {grand[1]:>12,} {grand[2]:>10,}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
