# Canonical vault glossary projection design

## Decision

`CONTEXT.md` is the sole owner of research-vault domain definitions. The
scaffolded `system/glossary.md` is a generated OKF guide: fixed `type: "guide"`
frontmatter followed by the unchanged `CONTEXT.md` body. It is a regular file in
each vault, never a runtime symlink.

The template package carries a source-tree link to `CONTEXT.md` only so an
installed distribution can read the canonical body. That link is build plumbing,
not part of the domain model or the generated vault.

## Boundaries

`CONTEXT.md` contains terms and their meanings. It does not describe scaffold
behavior, package paths, YAML envelopes, or which tool writes a file. Rules for
operating a vault remain in its `AGENTS.md`; architectural trade-offs remain in
the ADRs.

The glossary will define every shared term once. This includes the terms that
currently appear only in the template (`Synthesis note`, `System folder`, and
`Venue`) and retains the terms currently found only in `CONTEXT.md` (`Analysis`,
`Report`, and `Closing check`). It will also retain the stronger screening-state
scope, distinguish a bibliography export from citability, and define an update
notice without unexplained jargon. The separate decision about OKF document
maturity versus project workflow state remains out of scope until its persistent
model is decided.

## Rendering

The packaged source is read through `importlib.resources`; `scaffold.py` must
not locate a repository-relative `CONTEXT.md` at runtime. When
`system/glossary.md` is absent, the scaffold writes:

```markdown
---
type: "guide"
---

<exact CONTEXT.md body>
```

When the target already exists, scaffold leaves it unchanged. A vault owner can
therefore customize its glossary, and a later scaffold run cannot silently
change that vault's vocabulary. New vaults receive the current canonical
definitions.

## Operating guidance

The template agents guide retains machine-surface instructions. If a rule is
needed to preserve behavior previously mentioned in the glossary, state it there
as an instruction rather than redefining the term in the glossary.

## Verification

Tests must prove all of the following:

- the canonical context source is included in the package assets;
- scaffold creates `system/glossary.md` as an OKF `guide` when it is absent;
- after removing the fixed envelope, the generated body exactly equals
  `CONTEXT.md`;
- re-scaffold preserves an existing glossary;
- template inventory and scaffold-created-path tests still describe the real
  package and output.

Run the focused scaffold and template tests, then the full suite with the
project's declared Python environment.

## ADR assessment

This is a reversible document-projection mechanism. It does not meet the ADR
bar. A future decision that changes persisted project lifecycle fields may meet
that bar and should be evaluated separately.
