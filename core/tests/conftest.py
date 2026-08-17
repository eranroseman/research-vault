import json as _json
import os
import subprocess

import pytest

VAULT_DIRS = ["+", "literatures", "atlas", "calendar", "efforts", "x"]


@pytest.fixture
def tmp_vault(tmp_path):
    for d in VAULT_DIRS:
        (tmp_path / d).mkdir()
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    return tmp_path


@pytest.fixture
def fixture_vault(tmp_vault):
    literature = tmp_vault / "literatures"
    (literature / "smith2020.md").write_text(
        """---
citekey: "smith2020"
type: "literature"
doi: "10.1000/xyz"
retrieved: "2026-08-16"
attachment-sha256:
  - "aa11"
status: "active"
aliases:
  - "Mortality decline"
---
%%hk-managed%%
# Mortality decline

- (quote) [@smith2020, p. 12] ^c-11111111
  > Mortality fell 12% across all strata.
- (paraphrase) Retrospective design [@smith2020, p. 3] ^c-22222222
%%/hk-managed%%

## Notes
"""
    )
    (literature / "gone2019.md").write_text(
        """---
citekey: "gone2019"
type: "literature"
doi: "10.1000/old"
retrieved: "2026-08-16"
status: "superseded"
superseded-by: "smith2020"
---
%%hk-managed%%
# Old result
%%/hk-managed%%

## Notes
"""
    )
    (tmp_vault / "atlas" / "index.md").write_text(
        "# Atlas index\n\n- [[mortality-trends]] — mortality synthesis\n"
    )
    (tmp_vault / "atlas" / "mortality-trends.md").write_text(
        """---
title: "Mortality trends"
type: "topic"
---
- (inference) Decline is robust [confidence:: moderate] [supported-by:: [[smith2020#^c-11111111]]] [contested-by:: [[gone2019#^c-22222222]]] ^c-55555555
"""
    )
    effort = tmp_vault / "efforts" / "brief"
    effort.mkdir()
    (effort / "draft.md").write_text(
        """---
title: "Evidence brief"
type: "effort"
status: "drafting"
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
    (tmp_vault / "x" / "bibliography.json").write_text(
        _json.dumps(bibliography, indent=1)
    )
    (tmp_vault / "calendar" / "2026-08-16.md").write_text(
        "- 09:00 human:eran — imported smith2020\n"
    )
    (tmp_vault / "+" / "review-queue.md").write_text("")
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
