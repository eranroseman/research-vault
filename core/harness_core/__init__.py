"""Deterministic core for the knowledge-harness plugin (spec docs/superpowers/specs/2026-08-16-foundation-spec.md)."""

import enum

__version__ = "0.1.0"

AGENT_ACTOR = (
    f"harness_core/{__version__}"  # §5 actor convention for process-written records
)


class Result(enum.Enum):
    MATCHED = "MATCHED"
    UNMATCHED = "UNMATCHED"
    UNREACHABLE = "UNREACHABLE"
    SKIPPED = "SKIPPED"
