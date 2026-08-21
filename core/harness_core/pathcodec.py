"""Canonical, byte-preserving textual identities for repository paths."""

from __future__ import annotations

import re
from dataclasses import dataclass

PATH_BYTES_PREFIX = "path-bytes:"
_SAFE = frozenset(
    b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._~-/"
)
_HEX = frozenset(b"0123456789ABCDEF")
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
class RepoPathValue:
    """An explicitly typed raw repository-relative path."""

    raw: bytes

    def __post_init__(self) -> None:
        _validate_raw(self.raw)


def encode_repo_path(raw: bytes) -> str:
    """Encode one raw path to its unique ASCII persistence token."""
    raw = _validate_raw(raw)
    payload = "".join(
        chr(value) if value in _SAFE else f"%{value:02X}" for value in raw
    )
    return PATH_BYTES_PREFIX + payload


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
    raw = bytearray()
    index = 0
    while index < len(encoded):
        value_byte = encoded[index]
        if value_byte == ord("%"):
            if index + 2 >= len(encoded):
                raise PathCodecError("truncated repository path escape")
            first, second = encoded[index + 1 : index + 3]
            if first not in _HEX or second not in _HEX:
                raise PathCodecError(
                    "repository path escapes use uppercase hexadecimal"
                )
            decoded = int(bytes((first, second)), 16)
            if decoded in _SAFE:
                raise PathCodecError("repository path over-encodes a safe byte")
            raw.append(decoded)
            index += 3
            continue
        if value_byte not in _SAFE:
            raise PathCodecError("repository path contains a literal reserved byte")
        raw.append(value_byte)
        index += 1
    result = _validate_raw(bytes(raw))
    if encode_repo_path(result) != value:
        raise PathCodecError("repository path is not canonically encoded")
    return result


__all__ = [
    "PATH_BYTES_PREFIX",
    "PathCodecError",
    "RepoPathValue",
    "decode_repo_path",
    "encode_repo_path",
]
