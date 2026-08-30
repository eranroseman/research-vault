"""Canonical, byte-preserving textual identities for repository paths."""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import quote, unquote_to_bytes

PATH_BYTES_PREFIX = "path-bytes:"
_DRIVE = re.compile(rb"^[A-Za-z]:")


class PathCodecError(ValueError):
    """A repository path or its persisted spelling is invalid."""


def _validate_raw(raw: bytes) -> bytes:
    if type(raw) is not bytes:
        raise TypeError("repository path must be bytes")
    if not raw:
        raise PathCodecError("repository path must not be empty")
    if raw.startswith(b"/") or b"\0" in raw:
        raise PathCodecError("repository path must be relative and NUL-free")
    components = raw.split(b"/")
    if any(component in {b"", b".", b".."} for component in components):
        raise PathCodecError("repository path contains an invalid component")
    if _DRIVE.match(components[0]):
        raise PathCodecError("repository path has a platform drive alias")
    return raw


@dataclass(frozen=True)
class RepoPath:
    """An explicitly typed raw repository-relative path."""

    raw: bytes

    def __post_init__(self) -> None:
        _validate_raw(self.raw)


def encode_repo_path(raw: bytes) -> str:
    """Encode one raw path to its unique ASCII persistence token."""
    # quote() leaves exactly the RFC 3986 unreserved set literal and emits every
    # other byte as uppercase %HH, which is this codec's canonical spelling.
    return PATH_BYTES_PREFIX + quote(_validate_raw(raw), safe="/")


def decode_repo_path(value: str) -> bytes:
    """Decode one canonical persistence token back to the exact raw path."""
    if type(value) is not str:
        raise TypeError("encoded repository path must be text")
    if not value.startswith(PATH_BYTES_PREFIX):
        raise PathCodecError("encoded repository path has the wrong prefix")
    payload = value[len(PATH_BYTES_PREFIX) :]
    if not payload:
        raise PathCodecError("encoded repository path has an empty payload")
    try:
        encoded = payload.encode("ascii")
    except (UnicodeEncodeError, UnicodeError) as error:
        raise PathCodecError("encoded repository path must be ASCII") from error
    raw = _validate_raw(unquote_to_bytes(encoded))
    # unquote_to_bytes is permissive: it accepts lowercase escapes, over-encoded
    # safe bytes, literal reserved bytes, and truncated escapes alike. Requiring
    # the round trip to reproduce the input rejects every non-canonical spelling.
    if encode_repo_path(raw) != value:
        raise PathCodecError("repository path is not canonically encoded")
    return raw


__all__ = [
    "PATH_BYTES_PREFIX",
    "PathCodecError",
    "RepoPath",
    "decode_repo_path",
    "encode_repo_path",
]
