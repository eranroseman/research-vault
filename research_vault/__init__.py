"""Deterministic core for the research-vault plugin (specs under docs/superpowers/specs/)."""

from .outcome import Result  # noqa: F401  (re-exported vocabulary)

__version__ = "0.1.0"

# §5 actor convention for process-written records
AGENT_ACTOR = f"research_vault/{__version__}"
