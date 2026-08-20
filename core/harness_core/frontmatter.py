"""Flat YAML subset for note frontmatter (spec §5: flat, Bases-queryable)."""

import re


class FrontmatterError(ValueError):
    pass


class _DuplicateKeyMapping(dict):
    """Parsed mapping that retains the fact its source repeated a key."""

    def __init__(self, pairs):
        super().__init__(pairs)
        self.source_items = tuple(pairs)


_INLINE_DICT = re.compile(r"^\{(.*)\}$")
_FRONTMATTER_OPEN = re.compile(r"\A---(?:\r\n|\n)")
_FRONTMATTER_CLOSE = re.compile(r"(?:\r\n|\n)---(?:\r\n|\n)")


def _emit_scalar(v):
    if isinstance(v, int):
        return str(v)
    escaped = str(v).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def serialize(data: dict) -> str:
    lines = ["---"]
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                if isinstance(item, dict):
                    items = (
                        item.source_items
                        if isinstance(item, _DuplicateKeyMapping)
                        else item.items()
                    )
                    inner = ", ".join(
                        f"{key}: {_emit_scalar(item_value)}"
                        for key, item_value in items
                    )
                    lines.append(f"  - {{{inner}}}")
                else:
                    lines.append(f"  - {_emit_scalar(item)}")
        else:
            lines.append(f"{key}: {_emit_scalar(value)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def _parse_scalar(raw: str):
    raw = raw.strip()
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    return raw


def _split_unquoted(raw: str, delimiter: str, maxsplit: int = -1):
    parts = []
    start = 0
    splits = 0
    quoted = False
    index = 0
    while index < len(raw):
        char = raw[index]
        if char == "\\" and quoted:
            index += 2
            continue
        if char == '"':
            quoted = not quoted
        elif not quoted and splits != maxsplit and raw.startswith(delimiter, index):
            parts.append(raw[start:index])
            start = index + len(delimiter)
            index = start
            splits += 1
            continue
        index += 1
    parts.append(raw[start:])
    return parts


def _parse_item(raw: str):
    m = _INLINE_DICT.match(raw)
    if not m:
        return _parse_scalar(raw)
    pairs = []
    out = {}
    duplicate = False
    for part in _split_unquoted(m.group(1), ", "):
        pair = _split_unquoted(part, ": ", 1)
        key = pair[0].strip()
        value = _parse_scalar(pair[1] if len(pair) > 1 else "")
        duplicate = duplicate or key in out
        pairs.append((key, value))
        out[key] = value
    return _DuplicateKeyMapping(pairs) if duplicate else out


def parse(text: str) -> tuple[dict, str]:
    opening = _FRONTMATTER_OPEN.match(text)
    if opening is None:
        return {}, text
    closing = _FRONTMATTER_CLOSE.search(text, opening.end())
    if closing is None:
        raise FrontmatterError("unterminated frontmatter")
    block = text[opening.end() : closing.start()]
    body = text[closing.end() :]
    data: dict = {}
    current_list = None
    for line in block.splitlines():
        if line.startswith("  - "):
            if current_list is None:
                raise FrontmatterError(f"list item outside list: {line!r}")
            current_list.append(_parse_item(line[4:].strip()))
        elif line.startswith("  "):
            raise FrontmatterError(
                f"nested maps unsupported (flat schema, spec §5): {line!r}"
            )
        else:
            parts = _split_unquoted(line, ":", 1)
            if len(parts) == 1:
                raise FrontmatterError(f"bad line: {line!r}")
            key, raw = parts
            if raw.strip() == "":
                current_list = []
                data[key] = current_list
            else:
                data[key] = _parse_scalar(raw)
                current_list = None
    return data, body
