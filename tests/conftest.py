import hashlib as _hashlib
import json as _json
import os
import subprocess

import pytest

VAULT_DIRS = ["inbox", "literatures", "synthesis", "log", "projects", "system"]


def _with_managed_witness(text):
    opening = text.index("%%hk-managed%%")
    closing = text.index("%%/hk-managed%%", opening) + len("%%/hk-managed%%")
    if text[closing : closing + 2] == "\r\n":
        closing += 2
    elif text[closing : closing + 1] == "\n":
        closing += 1
    digest = _hashlib.sha256(text[opening:closing].encode()).hexdigest()
    return text.replace(
        'type: "literature"\n', f'type: "literature"\nmanaged-sha256: "{digest}"\n', 1
    )


@pytest.fixture
def tmp_vault(tmp_path):
    for d in VAULT_DIRS:
        (tmp_path / d).mkdir()
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    return tmp_path


@pytest.fixture
def fixture_vault(tmp_vault):
    (tmp_vault / "index.md").write_text(
        '---\nokf_version: "0.2"\n---\n# Knowledge bundle\n'
    )
    (tmp_vault / "log.md").write_text("# Log\n")
    literature = tmp_vault / "literatures"
    (literature / "smith2020.md").write_text(
        _with_managed_witness("""---
citekey: "smith2020"
type: "literature"
doi: "10.1000/xyz"
accessed: "2026-08-16"
fixity-sha256:
  - "aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11"
status: "included"
aliases:
  - "Mortality decline"
generated: {by: "knowledge_harness/0.1.0", at: "2026-08-16T09:00:00Z"}
---
%%hk-managed%%
# Mortality decline

- (quote) [@smith2020, p. 12] ^c-11111111
  > Mortality fell 12% across all strata.
- (paraphrase) Retrospective design [@smith2020, p. 3] ^c-22222222
%%/hk-managed%%

## Notes
""")
    )
    (literature / "gone2019.md").write_text(
        _with_managed_witness("""---
citekey: "gone2019"
type: "literature"
doi: "10.1000/old"
accessed: "2026-08-16"
status: "superseded"
superseded-by: "smith2020"
generated: {by: "knowledge_harness/0.1.0", at: "2026-08-16T09:00:00Z"}
---
%%hk-managed%%
# Old result
%%/hk-managed%%

## Notes
""")
    )
    (tmp_vault / "synthesis" / "index.md").write_text(
        "# Synthesis index\n\n- [[mortality-trends]] — mortality synthesis\n"
    )
    (tmp_vault / "synthesis" / "mortality-trends.md").write_text(
        """---
title: "Mortality trends"
type: "synthesis"
status: "draft"
generated: {by: "knowledge_harness/0.1.0", at: "2026-08-16T09:00:00Z"}
---
- (inference) Decline is robust [confidence:: moderate] [supports:: [[smith2020#^c-11111111]]] [disputes:: [[gone2019#^c-22222222]]] ^c-55555555
"""
    )
    project = tmp_vault / "projects" / "brief"
    project.mkdir()
    (project / "draft.md").write_text(
        """---
title: "Evidence brief"
type: "project"
status: "draft"
generated: {by: "knowledge_harness/0.1.0", at: "2026-08-16T09:00:00Z"}
---
- (quote) [@smith2020, p. 12] ^c-66666666
  > Mortality fell 12% across all strata.
- (inference) This will replicate [@fabricated2020] ^c-77777777
"""
    )
    bibliography = [
        {
            "id": "gone2019",
            "title": "Old result",
            "type": "article-journal",
            "DOI": "10.1000/old",
            "author": [{"family": "Gone", "given": "Ann"}],
            "issued": {"date-parts": [[2019]]},
        },
        {
            "id": "smith2020",
            "title": "Mortality decline",
            "type": "article-journal",
            "DOI": "10.1000/xyz",
            "author": [{"family": "Smith", "given": "Jo"}],
            "issued": {"date-parts": [[2020]]},
        },
    ]
    (tmp_vault / "system" / "bibliography.json").write_text(
        _json.dumps(bibliography, indent=1)
    )
    (tmp_vault / "log" / "2026-08-16.md").write_text(
        '---\ntype: "daily"\n---\n- 09:00 human:eran — imported smith2020\n'
    )
    (tmp_vault / "inbox" / "review-queue.md").write_text(
        '---\ntype: "review-queue"\n---\n'
    )
    subprocess.run(["git", "add", "-A"], cwd=tmp_vault, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "fixture vault"], cwd=tmp_vault, check=True
    )
    return tmp_vault


@pytest.fixture
def net_vault(fixture_vault):
    harness = fixture_vault / ".harness"
    harness.mkdir(exist_ok=True)
    (harness / "machine.json").write_text('{"mailto": "eran@example.edu"}')
    return fixture_vault


@pytest.fixture
def net_vault_real_mailto(fixture_vault):
    harness = fixture_vault / ".harness"
    harness.mkdir(exist_ok=True)
    (harness / "machine.json").write_text(
        _json.dumps({"mailto": os.environ.get("HARNESS_MAILTO", "")})
    )
    return fixture_vault


def pytest_collection_modifyitems(config, items):
    skip_live = pytest.mark.skip(reason="live Zotero not enabled (HARNESS_LIVE=1)")
    skip_net = pytest.mark.skip(reason="live network not enabled (HARNESS_LIVE_NET=1)")
    for item in items:
        if "live" in item.keywords and os.environ.get("HARNESS_LIVE") != "1":
            item.add_marker(skip_live)
        if "live_net" in item.keywords and os.environ.get("HARNESS_LIVE_NET") != "1":
            item.add_marker(skip_net)
