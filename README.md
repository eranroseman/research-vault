# knowledge-harness

A Claude Code harness for knowledge work — academic research first (question → literature → synthesis → draft → submit), then analysis/reports, personal knowledge management, and long-form writing.

Success criterion: **trustworthy output** — every claim traceable to a real source, zero fabricated citations.

Planning happens on the [wayfinder map](../../issues) (label `wayfinder:map`). `research/harness-audits/dev-harness-analysis.md` is the anatomy of the software-dev harness this re-imagines.

## Development

One command runs every form and lint owner, locally and in CI:

```bash
source .venv/bin/activate && pre-commit run --all-files
```

Each file type has exactly one form owner (`.pre-commit-config.yaml` is the matrix):
ruff for Python, mdformat for CommonMark Markdown, yamlfix for YAML, pyproject-fmt for
TOML, stdlib `json.tool` canonical form for JSON manifests (asserted in
`tests/test_config_validity.py`), and — for vault-dialect Markdown, which no
off-the-shelf formatter speaks — the sole writer, verified by
`tests/test_canonical_form.py`.

them so `git blame` keeps pointing at the change that meant something:

```bash
```
