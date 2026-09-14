"""Offline behavioral tests for the vendored `find-sources` scripts.

Upstream: https://github.com/K-Dense-AI/scientific-agent-skills @
336c4f838a6c21b54e1e1f58cbbeae143d151fe2, ``skills/paper-lookup/scripts/``,
license MIT (© 2025 K-Dense Inc.). Renamed into the plugin namespace at
``skills/find-sources/scripts/`` (spec §7's vendoring doctrine: behavior
stays frozen). Upstream's own ``tests/paper-lookup/`` is not vendored — only
what the skill uses is vendored — and these are our own tests proving the
vendored copies still work, offline, after the provenance-header edit. No network: every case here feeds a local XML/JSON
fixture on stdin, never a live API call (the suite's ``live_net`` marker
convention is for the CLI's own network-touching tests, not for this).
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "find-sources" / "scripts"
SKILL_MD = SCRIPTS.parent / "SKILL.md"

JATS_WITH_BODY = """<article>
<front>
<article-meta>
<article-id pub-id-type="doi">10.1000/example</article-id>
<title-group><article-title>Example Title</article-title></title-group>
<contrib-group><contrib><name><surname>Smith</surname><given-names>Jo</given-names></name></contrib></contrib-group>
</article-meta>
</front>
<body>
<sec sec-type="methods"><title>Methods</title><p>We did an experiment.</p></sec>
</body>
</article>
"""

JATS_NO_BODY = """<article>
<front>
<article-meta>
<article-id pub-id-type="doi">10.1000/example</article-id>
</article-meta>
</front>
<!-- The publisher does not allow downloading of the full text in XML form. -->
</article>
"""

ARXIV_ENTRY = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <link href="http://arxiv.org/api/query" rel="self" type="application/atom+xml"/>
  <title>ArXiv Query: search_query=all:attention</title>
  <opensearch:totalResults>1</opensearch:totalResults>
  <opensearch:startIndex>0</opensearch:startIndex>
  <opensearch:itemsPerPage>1</opensearch:itemsPerPage>
  <entry>
    <id>http://arxiv.org/abs/1706.03762v7</id>
    <title>Attention Is All You Need</title>
    <summary>The dominant sequence transduction models are based on
    complex recurrent or convolutional neural networks.</summary>
    <published>2017-06-12T17:57:34Z</published>
    <updated>2023-08-02T00:41:18Z</updated>
    <author><name>Ashish Vaswani</name></author>
    <link href="http://arxiv.org/abs/1706.03762v7" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/1706.03762v7" rel="related" type="application/pdf"/>
    <arxiv:primary_category term="cs.CL"/>
    <category term="cs.CL"/>
  </entry>
</feed>
"""

ARXIV_ERROR = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">
<opensearch:totalResults>1</opensearch:totalResults>
<entry><title>Error</title><summary>malformed id list</summary></entry>
</feed>
"""

OPENALEX_WORK = json.dumps(
    {
        "id": "https://openalex.org/W123",
        "doi": "https://doi.org/10.1/x",
        "title": "Example Work",
        "publication_year": 2020,
        "abstract_inverted_index": {"Hello": [0], "world": [1]},
    }
)


def _run(script: str, *args: str, stdin: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), "-", *args],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


def test_jats_to_text_extracts_sections_when_a_body_is_present():
    result = _run("jats_to_text.py", stdin=JATS_WITH_BODY)

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["full_text_available"] is True
    assert payload["metadata"]["title"] == "Example Title"
    assert payload["metadata"]["doi"] == "10.1000/example"
    assert payload["metadata"]["authors"] == ["Jo Smith"]
    assert payload["sections"][0]["title"] == "Methods"
    assert payload["sections"][0]["text"] == "Methods We did an experiment."


def test_jats_to_text_exits_2_and_surfaces_the_comment_when_no_body():
    """The upstream hazard this script exists for: HTTP 200 with metadata
    only. Presenting that as full text is exactly what §6's four-state rule
    forbids — this must read as UNREACHABLE-full-text, never a quiet pass."""
    result = _run("jats_to_text.py", stdin=JATS_NO_BODY)

    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["full_text_available"] is False
    assert "does not allow" in payload["reason"]


def test_arxiv_atom_parses_a_real_entry():
    result = _run("arxiv_atom.py", stdin=ARXIV_ENTRY)

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["returned"] == 1
    entry = payload["entries"][0]
    assert entry["arxiv_id"] == "1706.03762"
    assert entry["version"] == "7"
    assert entry["title"] == "Attention Is All You Need"
    assert entry["pdf_url"] == "http://arxiv.org/pdf/1706.03762v7"


def test_arxiv_atom_exits_3_on_the_error_feed():
    """arXiv's HTTP-200 failure mode: a malformed parameter returns a
    structurally valid one-hit result titled 'Error'. Reporting that as a
    match would be a fabricated citation candidate."""
    result = _run("arxiv_atom.py", stdin=ARXIV_ERROR)

    assert result.returncode == 3
    assert "arXiv returned an error feed" in result.stderr


def test_openalex_abstract_reconstructs_text_from_the_inverted_index():
    result = _run("openalex_abstract.py", stdin=OPENALEX_WORK)

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["works"][0]["abstract"] == "Hello world"
    assert payload["with_abstract"] == 1


def test_paginate_dry_run_builds_a_url_without_any_network_call():
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "paginate.py"),
            "--api",
            "biorxiv",
            "--query",
            "2024-01-01/2024-01-03",
            "--dry-run",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["first_url"] == (
        "https://api.biorxiv.org/details/biorxiv/2024-01-01/2024-01-03/0/json"
    )


def test_paginate_list_apis_is_offline_and_enumerates_every_walked_api():
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "paginate.py"), "--list-apis"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert set(payload) == {"biorxiv", "medrxiv", "europepmc", "openalex", "crossref"}


def test_common_redact_url_hides_credential_query_parameters():
    """`_common.py`'s ``redact_url`` is what keeps a fetched-URL provenance
    line from leaking an API key or a personal mailto — imported directly
    since it has no CLI of its own."""
    sys.path.insert(0, str(SCRIPTS))
    try:
        import _common

        redacted = _common.redact_url(
            "https://api.crossref.org/works?query=x&mailto=me@example.edu"
        )
    finally:
        sys.path.remove(str(SCRIPTS))

    assert "me@example.edu" not in redacted
    assert "mailto=REDACTED" in redacted


def test_every_vendored_file_carries_a_provenance_header():
    header_marker = "336c4f838a6c21b54e1e1f58cbbeae143d151fe2"
    vendored = list((SCRIPTS.parent / "references").glob("*.md")) + list(
        SCRIPTS.glob("*.py")
    )
    assert len(vendored) == 16
    for path in vendored:
        text = path.read_text(encoding="utf-8")
        assert header_marker in text, f"{path} is missing its provenance header"
        assert "MIT" in text
        assert "K-Dense" in text


def _env_vars_read_by_the_vendored_scripts() -> set[str]:
    """Every literal name the scripts pull out of the environment, off their AST."""
    names: set[str] = set()
    for path in sorted(SCRIPTS.glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.Call) or not node.args:
                continue
            target = node.func
            if getattr(target, "attr", None) not in {"get", "getenv"}:
                continue
            source = (
                ast.unparse(target.value) if isinstance(target, ast.Attribute) else ""
            )
            if source not in {"os.environ", "environ", "os"}:
                continue
            first = node.args[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                names.add(first.value)
    return names


def test_the_skill_names_exactly_the_environment_variables_the_scripts_read():
    """Pins two SKILL.md claims, both of them hand-maintainable prose about
    what the code reads: the scripts are not credential-free —
    ``paginate.py`` consumes three env vars — and ``paginate.py``'s docstring
    names two more (``NCBI_API_KEY``, ``S2_API_KEY``) that nothing reads,
    which the vendoring note records as dead. Both claims are true only while
    this set is what it is."""
    read = _env_vars_read_by_the_vendored_scripts()

    assert read == {"OPENALEX_EMAIL", "OPENALEX_API_KEY", "CROSSREF_MAILTO"}
    skill = SKILL_MD.read_text(encoding="utf-8")
    for name in sorted(read):
        assert name in skill, (
            f"SKILL.md does not name {name}, which a vendored script reads"
        )


def test_no_vendored_script_imports_research_vault():
    for path in SCRIPTS.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "research_vault" not in text, (
            f"{path} imports research_vault — vendored code must stay standalone"
        )
