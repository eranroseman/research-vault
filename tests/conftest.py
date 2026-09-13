import json as _json
import os
import subprocess
from typing import AnyStr

import pytest

from research_vault import scaffold


def must_replace(text: AnyStr, old: AnyStr, new: AnyStr, count: int = 1) -> AnyStr:
    """str.replace that refuses to be a no-op: a fixture edit that removes `old` must fail loudly.

    ``text``, ``old`` and ``new`` are all ``str`` or all ``bytes`` (ruling 7).
    """
    assert old in text, f"substitution target no longer in the fixture: {old!r}"
    return text.replace(old, new, count)


def _with_body_witness(text):
    from research_vault import notes

    digest = notes.body_sha256(text)
    return must_replace(
        text,
        'type: "literature"\n',
        f'type: "literature"\nmanaged-sha256: "{digest}"\n',
    )


@pytest.fixture
def tmp_vault(tmp_path):
    for d in scaffold.VAULT_DIRS:
        (tmp_path / d).mkdir(parents=True)
    (tmp_path / "wiki" / "concepts").mkdir(parents=True)
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
        _with_body_witness("""---
type: "literature"
title: "Mortality decline"
aliases:
  - "Mortality decline"
itemType: "journalArticle"
DOI: "10.1000/xyz"
zotero-server-id: "6LpvURP2E933"
zotero-item-key: "SMITH020"
zotero-item-version: 12
citationKey: "smith2020"
attachments:
  - {key: "ATT00001", version: 13, md5: "aa11aa11aa11aa11aa11aa11aa11aa11", contentType: "application/pdf", filename: "smith2020.pdf"}
fulltext:
  - {attachment-key: "ATT00001", sha256: "aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11"}
compile-input-sha256: "aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11aa11"
accessed: "2026-08-16"
generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}
---
# Mortality decline

- (quote) [@smith2020, p. 12] ^c-11111111
  > Mortality fell 12% across all strata.
- (paraphrase) Retrospective design [@smith2020, p. 3] ^c-22222222
""")
    )
    (literature / "gone2019.md").write_text(
        _with_body_witness("""---
type: "literature"
title: "Old result"
aliases:
  - "Old result"
itemType: "journalArticle"
DOI: "10.1000/old"
zotero-server-id: "6LpvURP2E933"
zotero-item-key: "GONE2019"
zotero-item-version: 7
citationKey: "gone2019"
attachments:
fulltext:
accessed: "2026-08-16"
generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}
---
# Old result
""")
    )
    (tmp_vault / "wiki" / "concepts" / "mortality-trends.md").write_text(
        """---
title: "Mortality trends"
type: "concept"
status: "draft"
generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}
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
generated: {by: "research_vault/0.1.0", at: "2026-08-16T09:00:00Z"}
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
    rv_dir = fixture_vault / ".research-vault"
    rv_dir.mkdir(exist_ok=True)
    (rv_dir / "machine.json").write_text('{"mailto": "eran@example.edu"}')
    return fixture_vault


@pytest.fixture
def net_vault_real_mailto(fixture_vault):
    rv_dir = fixture_vault / ".research-vault"
    rv_dir.mkdir(exist_ok=True)
    (rv_dir / "machine.json").write_text(
        _json.dumps({"mailto": os.environ.get("RV_MAILTO", "")})
    )
    return fixture_vault


def pytest_collection_modifyitems(config, items):
    skip_live = pytest.mark.skip(reason="live Zotero not enabled (RV_LIVE=1)")
    skip_net = pytest.mark.skip(reason="live network not enabled (RV_LIVE_NET=1)")
    for item in items:
        if "live" in item.keywords and os.environ.get("RV_LIVE") != "1":
            item.add_marker(skip_live)
        if "live_net" in item.keywords and os.environ.get("RV_LIVE_NET") != "1":
            item.add_marker(skip_net)


@pytest.fixture(autouse=True)
def _no_zotero_socket(request, monkeypatch):
    """The offline suite never reaches a Zotero: an unpatched read is an outage.

    Both instances run on the author's machine, so an unguarded read would pass
    or fail with whatever happens to be live — and verify's lifecycle leg opens
    a client on every network-capable run. Fakes install at instance level and
    shadow this; live legs (``RV_LIVE=1``) keep the real transport.
    """
    if request.node.get_closest_marker("live"):
        return
    from research_vault import zotero

    def refused(self, url, *_args, **_kwargs):
        raise zotero.ZoteroError(f"Zotero unreachable in the offline suite: {url}")

    monkeypatch.setattr(zotero.ZoteroClient, "_http", refused)
