"""Flat YAML subset for note frontmatter (spec §5: flat, Bases-queryable)."""
import re


class FrontmatterError(ValueError):
    pass


_INLINE_DICT = re.compile(r"^\{(.*)\}$")


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
                    inner = ", ".join(f"{k}: {_emit_scalar(v)}" for k, v in item.items())
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


def _parse_item(raw: str):
    m = _INLINE_DICT.match(raw)
    if not m:
        return _parse_scalar(raw)
    out = {}
    for part in m.group(1).split(", "):
        k, _, v = part.partition(": ")
        out[k.strip()] = _parse_scalar(v)
    return out


def parse(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.index("\n---\n", 4)
    block, body = text[4:end], text[end + 5:]
    data: dict = {}
    current_list = None
    for line in block.split("\n"):
        if line.startswith("  - "):
            if current_list is None:
                raise FrontmatterError(f"list item outside list: {line!r}")
            current_list.append(_parse_item(line[4:].strip()))
        elif line.startswith("  "):
            raise FrontmatterError(f"nested maps unsupported (flat schema, spec §5): {line!r}")
        else:
            key, sep, raw = line.partition(":")
            if not sep:
                raise FrontmatterError(f"bad line: {line!r}")
            if raw.strip() == "":
                current_list = []
                data[key] = current_list
            else:
                data[key] = _parse_scalar(raw)
                current_list = None
    return data, body
