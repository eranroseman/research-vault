"""The `archive-source` verb: the sole writer of literature ``archive-url``.

Spec §7's archive-at-import, ruled into a CLI verb 2026-08-22 because rescue is
impossible at rot time — a source cataloged unarchived stays unarchived. The
network boundary is faked at ``webapi``'s own seam, exactly as
``test_identify`` fakes it; the one genuinely outward leg is marked ``live_net``
so the offline suite never reaches the Internet Archive.
"""

import pytest

from knowledge_harness import Result, archive, frontmatter, notes, webapi

WEB_NOTE = """---
citekey: "rot2024"
type: "literature"
url: "https://example.org/page"
accessed: "2026-08-22"
status: "unscreened"
---
%%hk-managed%%
# A web source
%%/hk-managed%%

## Notes
"""

SNAPSHOT = "https://web.archive.org/web/20260822000000/https://example.org/page"


def _write_note(vault, text=WEB_NOTE, citekey="rot2024"):
    path = notes.note_path(vault, citekey)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _available(url=SNAPSHOT, status="200", available=True):
    return (
        200,
        {
            "archived_snapshots": {
                "closest": {"available": available, "status": status, "url": url}
            }
        },
    )


def _fake_network(monkeypatch, *, save=200, availability=None, save_error=None):
    calls = {"save": [], "availability": []}

    def fake_status(url, vault_root, params=None, headers=None, timeout=10.0, **kwargs):
        calls["save"].append((url, kwargs.get("query_mailto", True)))
        if save_error is not None:
            raise save_error
        return save

    def fake_json(url, vault_root, params=None, headers=None, timeout=10.0):
        calls["availability"].append((url, dict(params or {})))
        if isinstance(availability, Exception):
            raise availability
        return availability

    monkeypatch.setattr(webapi, "get_status", fake_status)
    monkeypatch.setattr(webapi, "get_json", fake_json)
    return calls


# --- The happy path: capture, confirm, record ------------------------------


def test_records_the_snapshot_the_archive_confirms_it_is_serving(
    net_vault, monkeypatch
):
    path = _write_note(net_vault)
    calls = _fake_network(monkeypatch, availability=_available())

    outcome = archive.archive_source(net_vault, "rot2024")

    assert outcome.result is Result.MATCHED
    assert outcome.check == "web-archive"
    assert outcome.target == "rot2024"
    data, _ = frontmatter.parse(path.read_text())
    assert data["archive-url"] == SNAPSHOT
    assert calls["save"] == [
        (archive.SAVE_ENDPOINT + "https://example.org/page", False)
    ]
    assert calls["availability"] == [
        (archive.AVAILABILITY_ENDPOINT, {"url": "https://example.org/page"})
    ]


def test_save_page_now_rides_the_useragent_not_the_query_string(net_vault, monkeypatch):
    """A ``?mailto=`` on a path-carried target archives the wrong address."""
    _write_note(net_vault)
    calls = _fake_network(monkeypatch, availability=_available())

    archive.archive_source(net_vault, "rot2024")

    (save_url, query_mailto) = calls["save"][0]
    assert query_mailto is False
    assert save_url.endswith("https://example.org/page")


def test_recording_preserves_every_other_byte_of_the_note(net_vault, monkeypatch):
    path = _write_note(net_vault)
    before = path.read_text()
    _fake_network(monkeypatch, availability=_available())

    archive.archive_source(net_vault, "rot2024")

    after = path.read_text()
    assert after.replace(f'archive-url: "{SNAPSHOT}"\n', "") == before
    # The managed region and its witness are untouched, so the evidence-layer
    # protection sees no change at all.
    assert notes.managed_slice_bytes(after.encode()) == notes.managed_slice_bytes(
        before.encode()
    )


# --- Four-state honesty: never a fabricated URL ----------------------------


def test_save_page_now_outage_writes_nothing(net_vault, monkeypatch):
    path = _write_note(net_vault)
    before = path.read_bytes()
    _fake_network(monkeypatch, save_error=webapi.ApiError("network failure: timed out"))

    outcome = archive.archive_source(net_vault, "rot2024")

    assert outcome.result is Result.UNREACHABLE
    assert outcome.reason.startswith("outage — Save Page Now unavailable")
    assert path.read_bytes() == before


def test_confirmation_outage_writes_nothing(net_vault, monkeypatch):
    path = _write_note(net_vault)
    before = path.read_bytes()
    _fake_network(monkeypatch, availability=webapi.ApiError("network failure"))

    outcome = archive.archive_source(net_vault, "rot2024")

    assert outcome.result is Result.UNREACHABLE
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "payload",
    [
        (200, {}),
        (200, {"archived_snapshots": {}}),
        (200, {"archived_snapshots": {"closest": {"available": False}}}),
        (200, _available(available=False)[1]),
        (200, _available(status="404")[1]),
        (
            200,
            {"archived_snapshots": {"closest": {"available": True, "status": "200"}}},
        ),
        (200, "not a mapping"),
    ],
    ids=[
        "empty",
        "no-closest",
        "unavailable",
        "available-false",
        "snapshot-404",
        "no-url",
        "not-a-mapping",
    ],
)
def test_an_unconfirmed_snapshot_is_never_recorded(net_vault, monkeypatch, payload):
    path = _write_note(net_vault)
    before = path.read_bytes()
    _fake_network(monkeypatch, availability=payload)

    outcome = archive.archive_source(net_vault, "rot2024")

    assert outcome.result is Result.UNMATCHED
    assert outcome.reason.startswith("missing-archive")
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "hostile",
    [
        "https://evil.example/web/20260822/https://example.org/page",
        "ftp://web.archive.org/x",
        "web.archive.org/no-scheme",
        "",
        "https://web.archive.org/a\u2028b",
    ],
)
def test_a_snapshot_url_off_the_archives_host_is_never_recorded(
    net_vault, monkeypatch, hostile
):
    """The response decides content in a durable vault file — bound it."""
    path = _write_note(net_vault)
    before = path.read_bytes()
    _fake_network(monkeypatch, availability=_available(url=hostile))

    outcome = archive.archive_source(net_vault, "rot2024")

    assert outcome.result is Result.UNMATCHED
    assert path.read_bytes() == before


# --- Scope: exactly the notes lint_web_archive reports ---------------------


@pytest.mark.parametrize(
    "text",
    [
        WEB_NOTE.replace("accessed:", 'doi: "10.1000/xyz"\naccessed:'),
        WEB_NOTE.replace('url: "https://example.org/page"\n', ""),
    ],
    ids=["has-doi", "no-url"],
)
def test_a_non_web_source_is_skipped_without_a_network_call(
    net_vault, monkeypatch, text
):
    _write_note(net_vault, text)

    def forbidden(*args, **kwargs):
        raise AssertionError("a non-web source must make no outward call")

    monkeypatch.setattr(webapi, "get_status", forbidden)
    monkeypatch.setattr(webapi, "get_json", forbidden)

    outcome = archive.archive_source(net_vault, "rot2024")

    assert outcome.result is Result.SKIPPED
    assert outcome.reason == "no-identifier — not a web source"


def test_an_already_archived_note_is_a_matched_no_op(net_vault, monkeypatch):
    text = WEB_NOTE.replace("accessed:", f'archive-url: "{SNAPSHOT}"\naccessed:')
    path = _write_note(net_vault, text)
    before = path.read_bytes()

    def forbidden(*args, **kwargs):
        raise AssertionError("an already-archived note must make no outward call")

    monkeypatch.setattr(webapi, "get_status", forbidden)
    monkeypatch.setattr(webapi, "get_json", forbidden)

    outcome = archive.archive_source(net_vault, "rot2024")

    assert outcome.result is Result.MATCHED
    assert outcome.extra["already_recorded"] is True
    assert path.read_bytes() == before


# --- Recording a snapshot a person already has -----------------------------


def test_a_supplied_snapshot_is_confirmed_then_recorded(net_vault, monkeypatch):
    path = _write_note(net_vault)
    calls = _fake_network(monkeypatch, save=200)

    outcome = archive.archive_source(net_vault, "rot2024", snapshot=SNAPSHOT)

    assert outcome.result is Result.MATCHED
    data, _ = frontmatter.parse(path.read_text())
    assert data["archive-url"] == SNAPSHOT
    assert calls["save"] == [(SNAPSHOT, False)]
    assert calls["availability"] == []


def test_a_supplied_snapshot_rides_the_useragent_not_the_query_string(
    net_vault, monkeypatch
):
    """A Wayback snapshot carries its target in the path, like Save Page Now.

    Live-confirmed 2026-08-22: ``archive.org/wayback/available`` reported this
    snapshot ``available: true, status: "200"``, yet fetching it with
    ``?mailto=`` appended answered 404 — Wayback reads the query string as part
    of the archived address. Sending the contact address in the query here made
    the verb report a snapshot the archive is genuinely serving as missing, and
    the note never got its ``archive-url``.
    """
    _write_note(net_vault)
    calls = _fake_network(monkeypatch, save=200)

    archive.archive_source(net_vault, "rot2024", snapshot=SNAPSHOT)

    (fetched_url, query_mailto) = calls["save"][0]
    assert query_mailto is False
    assert fetched_url == SNAPSHOT


def test_a_supplied_snapshot_that_404s_is_never_recorded(net_vault, monkeypatch):
    path = _write_note(net_vault)
    before = path.read_bytes()
    _fake_network(monkeypatch, save=404)

    outcome = archive.archive_source(net_vault, "rot2024", snapshot=SNAPSHOT)

    assert outcome.result is Result.UNMATCHED
    assert outcome.reason == "missing-archive — supplied snapshot 404s"
    assert path.read_bytes() == before


def test_a_supplied_snapshot_off_the_archives_host_is_refused(net_vault, monkeypatch):
    path = _write_note(net_vault)
    before = path.read_bytes()

    def forbidden(*args, **kwargs):
        raise AssertionError("a malformed snapshot must make no outward call")

    monkeypatch.setattr(webapi, "get_status", forbidden)

    outcome = archive.archive_source(
        net_vault, "rot2024", snapshot="https://evil.example/x"
    )

    assert outcome.result is Result.UNMATCHED
    assert path.read_bytes() == before


# --- Cannot-run cases ------------------------------------------------------


@pytest.mark.parametrize(
    "citekey", ["../escape", "absent2020", "a\vb"], ids=["unsafe", "missing", "control"]
)
def test_a_verb_that_cannot_run_says_so(net_vault, citekey):
    with pytest.raises(archive.ArchiveError):
        archive.archive_source(net_vault, citekey)


def test_malformed_frontmatter_is_refused_not_repaired(net_vault):
    _write_note(net_vault, "no frontmatter here\n")

    with pytest.raises(archive.ArchiveError):
        archive.archive_source(net_vault, "rot2024")


def test_two_archive_url_fields_are_refused_rather_than_guessed(net_vault):
    text = WEB_NOTE.replace(
        "accessed:", f'archive-url: "{SNAPSHOT}"\narchive-url: "{SNAPSHOT}"\naccessed:'
    )

    with pytest.raises(archive.ArchiveError, match="archive-url"):
        archive.set_archive_url(text, SNAPSHOT)


# --- The CLI verb ----------------------------------------------------------


@pytest.mark.parametrize(
    ("availability", "expected_code"),
    [
        (_available(), 0),
        ((200, {"archived_snapshots": {}}), 1),
        (webapi.ApiError("down"), 3),
    ],
    ids=["recorded", "missing", "outage"],
)
def test_cli_exit_codes_follow_the_shared_four_state_contract(
    net_vault, monkeypatch, capsys, availability, expected_code
):
    import knowledge_harness.__main__ as cli

    _write_note(net_vault)
    _fake_network(monkeypatch, availability=availability)

    code = cli.main(["archive-source", "rot2024", "--vault", str(net_vault)])

    assert code == expected_code
    assert capsys.readouterr().out.splitlines()[0].split()[0] in {
        "MATCHED",
        "UNMATCHED",
        "UNREACHABLE",
    }


def test_cli_refusal_exits_two_and_writes_nothing(net_vault, capsys):
    import knowledge_harness.__main__ as cli

    code = cli.main(["archive-source", "absent2020", "--vault", str(net_vault)])

    assert code == 2
    assert capsys.readouterr().err.startswith("archive refused: ")


def test_cli_snapshot_flag_reaches_the_module(net_vault, monkeypatch, capsys):
    import knowledge_harness.__main__ as cli

    _write_note(net_vault)
    _fake_network(monkeypatch, save=200)

    code = cli.main(
        [
            "archive-source",
            "rot2024",
            "--vault",
            str(net_vault),
            "--snapshot",
            SNAPSHOT,
        ]
    )

    assert code == 0
    assert SNAPSHOT in capsys.readouterr().out


# --- The readers this writer exists to satisfy -----------------------------


def test_recording_clears_the_web_archive_lint_it_was_built_for(net_vault, monkeypatch):
    from knowledge_harness import lints

    _write_note(net_vault)
    before = [
        outcome
        for outcome in lints.lint_web_archive(net_vault)
        if outcome.target == "rot2024"
    ]
    assert [outcome.reason for outcome in before] == [
        "missing-archive — web source has no archive-url"
    ]

    _fake_network(monkeypatch, availability=_available())
    archive.archive_source(net_vault, "rot2024")

    after = [
        outcome
        for outcome in lints.lint_web_archive(net_vault)
        if outcome.target == "rot2024"
    ]
    assert after == []


def test_a_rerender_preserves_the_recorded_snapshot(net_vault, monkeypatch):
    """``archive-url`` is pass-through metadata: re-import must never drop it."""
    path = _write_note(net_vault)
    _fake_network(monkeypatch, availability=_available())
    archive.archive_source(net_vault, "rot2024")

    rerendered = notes.render_note(
        {"id": "rot2024", "title": "A web source", "URL": "https://example.org/page"},
        [],
        [],
        existing=path.read_text(),
        accessed="2026-08-22",
    )

    data, _ = frontmatter.parse(rerendered)
    assert data["archive-url"] == SNAPSHOT


# --- The one genuinely outward leg -----------------------------------------


@pytest.mark.live_net
def test_archives_a_real_url_against_the_internet_archive(net_vault_real_mailto):
    """Gated behind HARNESS_LIVE_NET: the offline suite never leaves the box."""
    text = WEB_NOTE.replace(
        'url: "https://example.org/page"', 'url: "https://example.com/"'
    )
    path = _write_note(net_vault_real_mailto, text)

    outcome = archive.archive_source(net_vault_real_mailto, "rot2024")

    assert outcome.result in {Result.MATCHED, Result.UNREACHABLE, Result.UNMATCHED}
    if outcome.result is Result.MATCHED:
        data, _ = frontmatter.parse(path.read_text())
        assert archive.is_archive_url(data["archive-url"])
    else:
        # An outage or an unserved snapshot must leave the note exactly as it
        # was — never a fabricated URL.
        data, _ = frontmatter.parse(path.read_text())
        assert "archive-url" not in data
