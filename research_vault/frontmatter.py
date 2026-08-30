"""Flat YAML subset for note frontmatter (spec §5: flat, Bases-queryable)."""

import re


class FrontmatterError(ValueError):
    pass


class _DuplicateKeyMapping(dict):
    """Parsed mapping that retains the fact its source repeated a key."""

    def __init__(self, pairs):
        pairs = tuple(pairs)
        super().__init__(pairs)
        self.source_items = pairs


def _mapping_items(mapping):
    return (
        mapping.source_items
        if isinstance(mapping, _DuplicateKeyMapping)
        else mapping.items()
    )


def _mapping_from_items(items):
    items = tuple(items)
    mapping = dict(items)
    return _DuplicateKeyMapping(items) if len(mapping) != len(items) else mapping


_INLINE_DICT = re.compile(r"^\{(.*)\}$")
_FRONTMATTER_OPEN = re.compile(r"\A---(?:\r\n|\n)")
_FRONTMATTER_CLOSE = re.compile(r"(?:\r\n|\n)---(?:\r\n|\n)")


# The reject class is a superset of what ``str.splitlines()`` treats as a
# line break, because that is the parser this serializer must not outrun:
# C0, DEL, NEL, and the Unicode line/paragraph separators. (DEL and the
# non-break C0 controls are rejected too, even though splitlines() does not
# treat them as breaks — over-rejecting here is safe.)
_CONTROL = re.compile(r"[\x00-\x1f\x7f\x85\u2028\u2029]")


def _emit_scalar(v):
    if isinstance(v, int):
        return str(v)
    text = str(v)
    if _CONTROL.search(text) is not None:
        # Upstream display-class collapse has already run by the time a value
        # reaches the serializer, so a surviving control character is a bug:
        # fail loudly rather than emit frontmatter that cannot be re-parsed.
        raise FrontmatterError(
            f"frontmatter scalars cannot carry control or line-break "
            f"characters: {text!r}"
        )
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _render_inline_mapping(mapping: dict) -> str:
    """Render a one-level mapping as ``{a: b, c: d}`` — the sole spelling of
    that grammar, shared by a ``key: {...}`` field and a ``  - {...}`` list
    item.
    """
    inner = ", ".join(
        f"{inner_key}: {_emit_scalar(inner_value)}"
        for inner_key, inner_value in _mapping_items(mapping)
    )
    return f"{{{inner}}}"


def render_field(key: str, value) -> str:
    """Render one top-level ``key: value`` frontmatter line.

    ``value`` may be a scalar or a one-level mapping (rendered ``{a: b, ...}``,
    matching a parsed ``generated``-shaped field). This is the one spelling of
    that grammar: ``serialize`` and any byte-surgical single-field writer
    (``archive.set_archive_url``, ``archive._bump_generated``) share it, so
    what they emit and what ``frontmatter.parse``/``notes._valid_generated``
    expect back cannot drift apart.
    """
    if isinstance(value, dict):
        return f"{key}: {_render_inline_mapping(value)}"
    return f"{key}: {_emit_scalar(value)}"


def serialize(data: dict) -> str:
    lines = ["---"]
    for key, value in _mapping_items(data):
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                if isinstance(item, dict):
                    lines.append(f"  - {_render_inline_mapping(item)}")
                else:
                    lines.append(f"  - {_emit_scalar(item)}")
        else:
            lines.append(render_field(key, value))
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
    for part in _split_unquoted(m.group(1), ", "):
        pair = _split_unquoted(part, ": ", 1)
        key = pair[0].strip()
        value = _parse_scalar(pair[1] if len(pair) > 1 else "")
        pairs.append((key, value))
    return _mapping_from_items(pairs)


def parse(text: str) -> tuple[dict, str]:
    opening = _FRONTMATTER_OPEN.match(text)
    if opening is None:
        return {}, text
    closing = _FRONTMATTER_CLOSE.search(text, opening.end())
    if closing is None:
        raise FrontmatterError("unterminated frontmatter")
    block = text[opening.end() : closing.start()]
    body = text[closing.end() :]
    source_items = []
    current_list: list[object] | None = None
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
                value = current_list
            else:
                value = _parse_item(raw.strip())
                current_list = None
            source_items.append((key, value))
    return _mapping_from_items(source_items), body
