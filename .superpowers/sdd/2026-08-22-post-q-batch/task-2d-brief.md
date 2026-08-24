### Task 2d: Formatter ignore files + invocation-scope line (audit findings 1 and 12)

**Files:** Modify: `knowledge_harness/scaffold.py` + vault templates (new `.prettierignore`, `.markdownlintignore`, `.editorconfig` covering `literatures/`, `log/`, `inbox/review-queue.md`, `system/bibliography.json`); `knowledge_harness/templates/vault/AGENTS.md`; pins.

- [ ] **Step 1:** Scaffold ships the three ignore files — formatters obey config, not paragraphs. The AGENTS.md formatter paragraph (which says of itself "it is not what enforces them") shrinks to one line naming the ignore files.
- [ ] **Step 2 (finding 12):** Scope AGENTS.md's "prefer the knowledge-harness skills" line to the two model-invocable guards — seven of nine skills are user-gated by deliberate design; the line must not read as steering all nine. Do NOT flip any `disable-model-invocation` flag.
- [ ] **Step 3:** Pins; suite; commit `feat: formatter ignores ship with the vault; AGENTS.md scope line corrected`.

