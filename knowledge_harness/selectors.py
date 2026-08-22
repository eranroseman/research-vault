"""Selector production: prefix/suffix context capture for quote annotations."""

import html
import unicodedata
from pathlib import Path

from .outcome import normalize_text

CONTEXT_CHARS = 32


def pdf_text(path) -> str | None:
    """Extract PDF text, degrading cleanly when the optional reader cannot run."""
    try:
        import pypdf

        reader = pypdf.PdfReader(str(Path(path)))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        return None


def _nfkc_with_spans(text: str) -> list[tuple[str, int, int]]:
    """Normalize whole-string NFKC while retaining conservative raw spans."""
    tokens = [
        (char, raw_index, raw_index + 1)
        for raw_index, raw_char in enumerate(text)
        for char in unicodedata.normalize("NFKD", raw_char)
    ]
    ordered: list[tuple[str, int, int]] = []
    run: list[tuple[str, int, int]] = []
    for token in tokens:
        if unicodedata.combining(token[0]) == 0 and run:
            ordered.extend(_order_canonical_run(run))
            run = []
        run.append(token)
    ordered.extend(_order_canonical_run(run))

    normalized = unicodedata.normalize("NFKC", text)
    spans = []
    token_index = 0
    for char in normalized:
        decomposition = unicodedata.normalize("NFD", char)
        consumed = ordered[token_index : token_index + len(decomposition)]
        if "".join(token[0] for token in consumed) != decomposition:
            raise AssertionError("NFKD span run does not reproduce the decomposition")
        spans.append(
            (
                min(token[1] for token in consumed),
                max(token[2] for token in consumed),
            )
        )
        token_index += len(decomposition)
    if token_index != len(ordered):
        raise AssertionError("NFKC span mapping did not consume every token")
    return [(char, *span) for char, span in zip(normalized, spans, strict=True)]


def _order_canonical_run(
    run: list[tuple[str, int, int]],
) -> list[tuple[str, int, int]]:
    """Apply Unicode canonical combining-class ordering to one starter run."""
    if not run:
        return []
    start = 1 if unicodedata.combining(run[0][0]) == 0 else 0
    return run[:start] + sorted(
        run[start:], key=lambda token: unicodedata.combining(token[0])
    )


def _norm_with_map(text: str) -> tuple[str, list[tuple[int, int]]]:
    """Return exactly ``normalize_text(text)`` with raw spans for each char."""
    chars = _nfkc_with_spans(text or "")
    dehyphenated: list[tuple[str, int, int]] = []
    index = 0
    while index < len(chars):
        char, start, end = chars[index]
        if char == "\u00ad":
            index += 1
            continue
        if char == "-" and index + 1 < len(chars) and chars[index + 1][0] == "\n":
            index += 2
            continue
        if (
            char == "-"
            and index + 2 < len(chars)
            and chars[index + 1][0] == "\r"
            and chars[index + 2][0] == "\n"
        ):
            index += 3
            continue
        dehyphenated.append((char, start, end))
        index += 1

    output: list[str] = []
    spans: list[tuple[int, int]] = []
    whitespace: list[tuple[int, int]] = []
    for char, start, end in dehyphenated:
        if char.isspace():
            whitespace.append((start, end))
            continue
        if output and whitespace:
            output.append(" ")
            spans.append((whitespace[0][0], whitespace[-1][1]))
        whitespace = []
        output.append(char)
        spans.append((start, end))

    normalized = "".join(output)
    if normalized != normalize_text(text):
        raise AssertionError("span-mapped normalization diverged from normalize_text")
    return normalized, spans


def find_context(text: str, quote: str) -> tuple[str, str] | None:
    """Find a normalized quote and return its raw 32-character surroundings."""
    normalized_text, spans = _norm_with_map(text)
    normalized_quote = normalize_text(quote)
    if not normalized_quote:
        return None
    position = normalized_text.find(normalized_quote)
    if position < 0:
        return None
    start = spans[position][0]
    end = spans[position + len(normalized_quote) - 1][1]
    while end < len(text) and unicodedata.combining(text[end]):
        end += 1
    return text[max(0, start - CONTEXT_CHARS) : start], text[end : end + CONTEXT_CHARS]


def attach_contexts(annotations: list[dict], text: str) -> int:
    """Attach contexts to quote annotations found in one attachment's text."""
    attached = 0
    for annotation in annotations:
        quote = annotation.get("annotationText") or ""
        context = find_context(text, quote) if isinstance(quote, str) else None
        if context is None:
            continue
        annotation["context_prefix"], annotation["context_suffix"] = context
        attached += 1
    return attached


def unescape_selector(value: str) -> str:
    """Invert ``html.escape(value, quote=True)`` used by the note renderer."""
    return html.unescape(value)
