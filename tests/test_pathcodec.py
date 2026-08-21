import string

import pytest

from harness_core.pathcodec import (
    PATH_BYTES_PREFIX,
    PathCodecError,
    RepoPath,
    decode_repo_path,
    encode_repo_path,
)

SAFE = set((string.ascii_letters + string.digits + "._~-/").encode())


def test_exact_examples_and_byte_identity():
    assert PATH_BYTES_PREFIX == "path-bytes:"
    assert (
        encode_repo_path(b"literatures/a b%2F.md")
        == "path-bytes:literatures/a%20b%252F.md"
    )
    assert encode_repo_path(b"literatures/\xff.md") == "path-bytes:literatures/%FF.md"
    assert encode_repo_path(b"a/b-A_z.~9") == "path-bytes:a/b-A_z.~9"
    assert encode_repo_path(b"a/\xe9") != encode_repo_path(b"a/\xc3\xa9")
    assert encode_repo_path(b"a/%2F") != "path-bytes:a//"


def test_all_byte_values_use_the_one_canonical_treatment():
    for value in range(1, 256):
        raw = b"root/x" + bytes([value]) + b"y"
        if value == ord("/"):
            # A separator in this position creates a legal extra component.
            expected_fragment = "/"
        elif value in SAFE:
            expected_fragment = chr(value)
        else:
            expected_fragment = f"%{value:02X}"
        encoded = encode_repo_path(raw)
        assert encoded == f"path-bytes:root/x{expected_fragment}y"
        assert decode_repo_path(encoded) == raw


@pytest.mark.parametrize(
    "raw",
    [
        b"a",
        b"a/b",
        b"a/space name.md",
        b"a/percent%name",
        b"a/line\nname",
        b"a/back\\slash",
        b"a/[brackets]",
        b"a/\xff",
    ],
)
def test_round_trip_legal_paths_without_normalization(raw):
    assert decode_repo_path(encode_repo_path(raw)) == raw


@pytest.mark.parametrize(
    "raw",
    [
        "text",
        bytearray(b"a"),
        memoryview(b"a"),
        b"",
        b"/absolute",
        b"a/",
        b"a//b",
        b".",
        b"..",
        b"a/./b",
        b"a/../b",
        b"a\0b",
    ],
)
def test_encoder_and_wrapper_reject_nonbytes_or_invalid_repo_paths(raw):
    with pytest.raises((TypeError, PathCodecError)):
        encode_repo_path(raw)
    with pytest.raises((TypeError, PathCodecError)):
        RepoPath(raw)


@pytest.mark.parametrize(
    "value",
    [
        "a/b",
        "PATH-BYTES:a/b",
        "path-bytes:",
        "path-bytes:/a",
        "path-bytes:a/",
        "path-bytes:a//b",
        "path-bytes:.",
        "path-bytes:..",
        "path-bytes:a/./b",
        "path-bytes:a/%2E%2E/b",
        "path-bytes:a%",
        "path-bytes:a%2",
        "path-bytes:a%GG",
        "path-bytes:a%ff",
        "path-bytes:a%41",
        "path-bytes:a%7E",
        "path-bytes:a%2F",
        "path-bytes:a b",
        "path-bytes:a[b]",
        "path-bytes:a\\b",
        "path-bytes:a\n",
        "path-bytes:a\N{LATIN SMALL LETTER E WITH ACUTE}",
        "path-bytes:a\udcff",
        "path-bytes:a%00b",
    ],
)
def test_decoder_rejects_aliases_malformed_text_and_traversal(value):
    with pytest.raises((TypeError, PathCodecError)):
        decode_repo_path(value)


def test_decoder_requires_text_and_exact_reencode(monkeypatch):
    with pytest.raises(TypeError):
        decode_repo_path(b"path-bytes:a")

    # The public round trip itself is the canonicality witness.
    canonical = encode_repo_path(b"dir/%41")
    assert canonical == "path-bytes:dir/%2541"
    assert encode_repo_path(decode_repo_path(canonical)) == canonical
