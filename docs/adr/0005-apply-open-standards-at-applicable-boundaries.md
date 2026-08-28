# Apply open standards at their applicable boundaries

Status: accepted (2026-08-28)

Compatibility must be intentional rather than implicit. The vault and generated
bundle follow the [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format)
boundary already established by ADR 0001; distributable plugins follow [Agent
Plugins](https://github.com/agentplugins); skills follow [Agent
Skills](https://github.com/agentskills); and any [Model Context Protocol](https://github.com/modelcontextprotocol)
surface follows MCP. A standard applies where its boundary exists — this does not
require every plugin to expose every kind of interface. In particular, MCP
conformance is required if we add an MCP surface, not an obligation to replace the
CLI gate core with an MCP server.

knowledge-harness must work with Claude Code; Codex compatibility is not yet a
knowledge-harness commitment. The Companion must work with Claude Code and Codex.
Portable behavior belongs in the standard artifact, while host-specific manifests,
hooks, and extensions belong in clearly named adapters. The Companion design owns
its own boundary, asset roster, and ownership transition; this ADR fixes only the
interoperability constraint it must honor.
