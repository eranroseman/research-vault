"""Deterministic core for the knowledge-harness plugin (spec docs/specs/2026-08-16-foundation-spec.md)."""

from .outcome import Result  # noqa: F401  (re-exported vocabulary)

__version__ = "0.1.0"

AGENT_ACTOR = (
    f"harness_core/{__version__}"  # §5 actor convention for process-written records
)
