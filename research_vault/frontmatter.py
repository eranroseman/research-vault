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
    that grammar: ``serialize`` is its sole caller, so what it emits and what
    ``frontmatter.parse``/``literature_notes._valid_generated`` expect back cannot drift
    apart.
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


# --- the OKF reader (#194): PyYAML, the reference loader's rules -----------------
#
# `parse` above is capture's own grammar: flat, quoted, one spelling per value,
# used for every surface capture or verify writes. OKF §11 rules 1-2 are judged
# against YAML, which is what the reference implementation reads
# (open-knowledge-format/okf-ref, document.py), so the structure checks read
# through this function instead. The two readers split the block on the same
# delimiters (`_FRONTMATTER_OPEN`, `_FRONTMATTER_CLOSE`) so they never disagree
# about where a body starts.


class DependencyMissingError(RuntimeError):
    """PyYAML cannot be imported: the OKF reader cannot run, and nothing that
    depends on it may read as a pass. The CLI maps this to exit 4 on every
    verb that reaches the reader (`main`'s dispatch), which the vault's
    pre-commit hook refuses (its `*)` branch), and doctor's `pyyaml` row
    names the repair."""


_LOADER = None


def _loader():
    """The reference loader: SafeLoader (C when available) minus the timestamp
    resolver, with a duplicate-key constructor that checks hashability first."""
    global _LOADER  # noqa: PLW0603 — one lazily built loader class per process
    if _LOADER is not None:
        return _LOADER
    try:
        import yaml
    except ImportError as error:
        raise DependencyMissingError(
            "PyYAML is not installed; the OKF frontmatter reader cannot run "
            "(pip install PyYAML)"
        ) from error

    base = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

    class _OkfLoader(base):  # type: ignore[misc,valid-type]
        pass

    # OKF's reference loader keeps every implicit resolver except timestamps:
    # a date-shaped scalar stays text, so `2026-13-45` is neither a datetime
    # nor a ValueError, and a calendar date compares as the string it is.
    _OkfLoader.yaml_implicit_resolvers = {
        first: [
            (tag, regexp)
            for tag, regexp in resolvers
            if tag != "tag:yaml.org,2002:timestamp"
        ]
        for first, resolvers in base.yaml_implicit_resolvers.items()
    }

    def construct_mapping(self, node, deep=False):
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError as error:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found unhashable key {key!r}",
                    key_node.start_mark,
                ) from error
            if key in mapping:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key {key!r}",
                    key_node.start_mark,
                )
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping

    _OkfLoader.add_constructor("tag:yaml.org,2002:map", construct_mapping)
    _LOADER = _OkfLoader
    return _LOADER


def _yaml_fault(error, first_line: int) -> str:
    """One line naming a YAML fault's cause, at the file's line and column.

    PyYAML's own message spans lines and leads with the context's mark, so a
    constructor fault's cause (``found unhashable key``) sat past the first
    two; its marks count from the block, which starts at ``first_line`` of
    the file. A fault with no problem (a reader fault: a control character)
    gives its first line, without the block offset that follows it.
    """
    problem = getattr(error, "problem", None)
    if problem is None:
        return str(error).splitlines()[0]
    context = getattr(error, "context", None)
    detail = f"{context}, {problem}" if context else problem
    mark = getattr(error, "problem_mark", None)
    if mark is None:
        return detail
    return f"{detail} (line {mark.line + first_line}, column {mark.column + 1})"


def read_okf(text: str) -> tuple[dict, str]:
    """OKF §11's reader: YAML frontmatter as the reference implementation reads it.

    Returns ``({}, text)`` for a file with no block and ``({}, body)`` for an
    empty block (document.py:71-75). A non-mapping block, a duplicate key, an
    unhashable key, a custom tag, a value its constructor cannot build
    (``!!int abc``) and any YAML syntax fault are ``FrontmatterError``; a
    missing PyYAML is ``DependencyMissingError``.
    """
    opening = _FRONTMATTER_OPEN.match(text)
    if opening is None:
        return {}, text
    closing = _FRONTMATTER_CLOSE.search(text, opening.end())
    if closing is None:
        raise FrontmatterError("unterminated frontmatter")
    block = text[opening.end() : closing.start()]
    body = text[closing.end() :]
    # `_loader()` raises DependencyMissingError before any `yaml` name is
    # touched; once it has returned, the import below cannot fail.
    loader = _loader()
    import yaml

    try:
        # The loader is a SafeLoader (C or pure) subclass that only narrows the
        # resolver table and tightens the mapping constructor: `safe_load`
        # itself is `load(stream, SafeLoader)`, and no constructor here builds
        # an arbitrary Python object.
        data = yaml.load(block, Loader=loader)  # noqa: S506
    except yaml.YAMLError as error:
        first_line = text.count("\n", 0, opening.end()) + 1
        raise FrontmatterError(
            f"frontmatter is not valid YAML: {_yaml_fault(error, first_line)}"
        ) from error
    except (ValueError, TypeError, KeyError, IndexError, AttributeError) as error:
        # PyYAML's typed constructors raise plain Python errors, not YAMLError:
        # `!!int abc` and an implicit `0b_` (int()), `!!bool abc` (a table
        # lookup), `!!timestamp abc` (a regex that does not match), a bare
        # `!!int` (an index), `!!map [a]` (an unpack). They are content.
        raise FrontmatterError(
            "frontmatter is not valid YAML: cannot construct a value "
            f"({type(error).__name__}: {error})"
        ) from error
    if data is None:
        return {}, body
    if not isinstance(data, dict):
        raise FrontmatterError("frontmatter block is not a mapping")
    return data, body


def okf_type(data) -> bool:
    """OKF §11 rule 2 as the reference tests it: ``not fm.get("type")`` is a
    missing type, so a null, ``false``, ``0`` or an empty list or mapping is
    missing, and any other value passes — a non-str one too (``[a, b]``,
    ``{a: 1}``, ``5``, ``true``), as OKF's reference test reads it, where the
    flat-parser check refused every non-str type. A whitespace-only string
    is also missing: the one place this reader is stricter than OKF's."""
    value = data.get("type") if isinstance(data, dict) else None
    return bool(value) and not (isinstance(value, str) and not value.strip())
