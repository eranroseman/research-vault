"""Shared verification vocabulary: the four-state Result and the Outcome record.

Its own module so every checker, lint, and the verify engine depend on the
vocabulary rather than on each other.
"""

import enum
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal

from .pathcodec import RepoPath, encode_repo_path


class Result(enum.Enum):
    MATCHED = "MATCHED"
    UNMATCHED = "UNMATCHED"
    UNREACHABLE = "UNREACHABLE"
    SKIPPED = "SKIPPED"


def _detached_extra(value, key_path="extra"):
    """Copy one JSON-shaped extra graph away from the caller's own objects.

    Outcomes are built from literals this package constructs, so this validates
    shape and detaches; it does not defend against cycles or exotic scalars.
    """
    if isinstance(value, Mapping):
        detached = {}
        for key, item in value.items():
            if type(key) is not str:
                raise TypeError("Outcome extra mapping keys must be strings")
            detached[key] = _detached_extra(item, key)
        return detached
    if isinstance(value, (list, tuple)):
        return [_detached_extra(item, key_path) for item in value]
    if value is None or type(value) in {str, bool, int, float}:
        return value
    raise TypeError(
        f"unsupported Outcome extra value at {key_path}: {type(value).__name__}"
    )


@dataclass(frozen=True)
class Outcome:
    check: str
    target: str | RepoPath
    result: Result
    reason: str
    extra: Mapping[str, object] = field(default_factory=dict)
    target_kind: Literal["identifier", "repo-path"] = field(init=False)
    path_extra_fields: tuple[str, ...] = field(init=False)
    __hash__ = None

    def __post_init__(self):
        if type(self.check) is not str or not self.check:
            raise TypeError("Outcome check must be a nonempty string")
        if not isinstance(self.result, Result):
            raise TypeError("Outcome result must be a Result")
        if type(self.target) is str:
            target = self.target
            target_kind = "identifier"
        elif isinstance(self.target, RepoPath):
            target = encode_repo_path(self.target.raw)
            target_kind = "repo-path"
        else:
            raise TypeError("Outcome target must be an identifier or RepoPath")
        if not target or any(character in target for character in "\r\n\0"):
            raise ValueError("Outcome target must be nonempty single-line text")
        if not isinstance(self.extra, Mapping):
            raise TypeError("Outcome extra must be a mapping")
        direct = {}
        path_fields = []
        for key, value in self.extra.items():
            if type(key) is not str:
                raise TypeError("Outcome extra mapping keys must be strings")
            if isinstance(value, RepoPath):
                direct[key] = encode_repo_path(value.raw)
                path_fields.append(key)
            else:
                direct[key] = value
        object.__setattr__(self, "target", target)
        object.__setattr__(self, "target_kind", target_kind)
        object.__setattr__(self, "path_extra_fields", tuple(sorted(path_fields)))
        # Deferred: inbox imports this module for Result, so the reason-code
        # vocabulary can only be reached at construction time.
        from . import inbox

        object.__setattr__(self, "reason", inbox.validate_reason(self.reason))
        object.__setattr__(self, "extra", _detached_extra(direct))


def normalize_text(s: str) -> str:
    """Normalize quote text without changing its case."""
    text = unicodedata.normalize("NFKC", s or "")
    text = text.replace("\u00ad", "").replace("-\r\n", "").replace("-\n", "")
    return " ".join(text.split())
