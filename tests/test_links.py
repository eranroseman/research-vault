from pathlib import Path

import pytest

from research_vault import links


def _vault(tmp_path: Path) -> Path:
    for relative in (
        "wiki/concepts/Foo.md",
        "wiki/sources/Foo.md",
        "wiki/concepts/Only Here.md",
        "wiki/concepts/Dr. Smith.md",
        "wiki/concepts/v1.2 notes.md",
        "wiki/img.png",
        "system/bases/trust-tier.base",
        "projects/brief/draft.md",
        "literature/smith2020.md",
        "literature/junk.md",
        ".obsidian/plugins/x/README.md",
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n")
    return tmp_path


def _index(tmp_path: Path) -> links.Index:
    return links.Index.build(
        _vault(tmp_path),
        literature={
            "smith2020": "literature/smith2020.md",
            "smith.2020": "literature/smith.2020.md",
            "re:2020": "literature/re2020.md",
        },
        names={
            "Mortality decline": "literature/smith2020.md",
            "Mortality in the U.S.": "literature/smith2020.md",
        },
    )


@pytest.mark.parametrize(
    ("target", "expected"),
    [
        ("Only Here", ["wiki/concepts/Only Here.md"]),
        ("only here", ["wiki/concepts/Only Here.md"]),  # case-insensitive
        ("Only Here.md", ["wiki/concepts/Only Here.md"]),
        ("concepts/Foo", ["wiki/concepts/Foo.md"]),
        ("wiki/concepts/Foo", ["wiki/concepts/Foo.md"]),
        ("/wiki/concepts/Foo.md", ["wiki/concepts/Foo.md"]),
        ("/concepts/Foo.md", []),  # a /-led link is an exact path or nothing
        ("Foo", ["wiki/concepts/Foo.md", "wiki/sources/Foo.md"]),  # ambiguous
        ("img.png", ["wiki/img.png"]),
        ("wiki/img.png", ["wiki/img.png"]),
        ("trust-tier", []),  # a dotless name resolves only as <name>.md
        ("trust-tier.base", ["system/bases/trust-tier.base"]),
        ("smith2020", ["literature/smith2020.md"]),  # through the captured set
        ("literature/smith2020", ["literature/smith2020.md"]),
        ("smith2020.md", ["literature/smith2020.md"]),  # [[Foo.md]] reads as [[Foo]]
        ("", ["wiki/concepts/Other.md"]),  # a same-page anchor names the linking file
        ("junk", []),  # a literature file with no provenance resolves nowhere
        ("literature/junk.md", []),
        ("Mortality decline", ["literature/smith2020.md"]),  # a note's alias
        # A dot that starts no `md` or attachment extension is part of the name.
        ("Dr. Smith", ["wiki/concepts/Dr. Smith.md"]),
        ("concepts/Dr. Smith", ["wiki/concepts/Dr. Smith.md"]),
        ("/wiki/concepts/Dr. Smith", ["wiki/concepts/Dr. Smith.md"]),
        ("Dr. Smith.md", ["wiki/concepts/Dr. Smith.md"]),
        ("v1.2 notes", ["wiki/concepts/v1.2 notes.md"]),
        ("smith.2020", ["literature/smith.2020.md"]),  # a dotted key
        ("Mortality in the U.S.", ["literature/smith2020.md"]),  # a dotted alias
        ("re:2020", ["literature/re2020.md"]),  # a `:` makes a name, not a URI
        ("README", []),  # excluded directories are not indexed
        ("nowhere", []),
        ("Dr. Nobody", []),
    ],
)
def test_resolve_follows_obsidian_for_a_page_in_wiki(tmp_path, target, expected):
    index = _index(tmp_path)
    assert index.resolve(target, source="wiki/concepts/Other.md") == expected


def test_resolve_relative_forms_are_exact_from_the_source(tmp_path):
    index = _index(tmp_path)
    assert index.resolve("./Foo", source="wiki/concepts/Other.md") == [
        "wiki/concepts/Foo.md"
    ]
    assert index.resolve("../sources/Foo.md", source="wiki/concepts/Other.md") == [
        "wiki/sources/Foo.md"
    ]
    assert index.resolve("../Foo", source="wiki/concepts/Other.md") == []
    # Above the vault root is outside it: nothing there is a vault file.
    assert index.resolve("../../../Foo", source="wiki/concepts/Other.md") == []


def test_a_folder_target_resolves_to_nothing_never_to_a_same_named_note(tmp_path):
    """A target ending in `/` names a folder. `normpath` strips the slash, and
    the dotless rule would then read the seed index's `[log/](log/)` as the
    root `log.md`; a folder is no file, so it resolves to nothing."""
    for relative in ("log.md", "log/2026-10-24.md", "wiki/concepts/Foo.md"):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n")
    index = links.Index.build(tmp_path, literature={}, names={})
    for target in ("log/", "/log/", "./log/", " log/ ", "wiki/concepts/", "/"):
        assert links.is_folder(target), target
        assert index.resolve(target, source="index.md") == [], target
    assert not links.is_folder("log")
    assert index.resolve("log", source="index.md") == ["log.md"]
    (link,) = links.find_links("[log/](log/#today)")
    assert (link.target, link.subpath) == ("log/", "#today")
    assert links.is_folder(link.target)


def test_only_a_markdown_destination_is_external():
    """A scheme makes a markdown destination a URL the caller leaves alone; a
    wikilink target is always a name, colon or not."""
    found = links.find_links(
        "[x](https://a.b) ![m](mailto:a@b.c) [[ghost:2020]] [[Re: Ghost]] [p](a/b.md)"
    )
    assert [(link.target, links.is_external(link)) for link in found] == [
        ("https://a.b", True),
        ("mailto:a@b.c", True),
        ("ghost:2020", False),
        ("Re: Ghost", False),
        ("a/b.md", False),
    ]


def test_an_attachment_is_named_by_its_last_components_extension():
    assert links.is_attachment("system/bases/trust-tier.base")
    assert links.is_attachment("wiki/Figure.PNG")
    for target in ("Dr. Smith", "v1.2/notes", "Foo.md", "trust-tier", "notes."):
        assert not links.is_attachment(target), target


def test_the_walk_prunes_excluded_directories_and_indexes_the_same_files(
    tmp_path, monkeypatch
):
    """The index's walk never enters `.git/` or another dot-directory, and its
    file set is still `rglob`'s filtered by `is_excluded`: a directory with an
    OS-litter name is entered, since litter excludes a file by its own name."""
    vault = _vault(tmp_path)
    for relative in (
        ".git/HEAD",
        ".git/objects/ab/cdef0123",
        "wiki/.trash/old.md",
        "wiki/.DS_Store",
        "wiki/._img.png",
        "wiki/desktop.ini/kept.md",
    ):
        path = vault / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n")
    judged = []
    real = links.structure.is_excluded

    def recording(path, root):
        judged.append(path.relative_to(root).as_posix())
        return real(path, root)

    monkeypatch.setattr(links.structure, "is_excluded", recording)
    index = links.Index.build(vault, literature={}, names={})
    assert ".git" in judged
    assert not [path for path in judged if path.startswith((".git/", "wiki/.trash/"))]
    assert sorted(index._exact.values()) == [
        "projects/brief/draft.md",
        "system/bases/trust-tier.base",
        "wiki/concepts/Dr. Smith.md",
        "wiki/concepts/Foo.md",
        "wiki/concepts/Only Here.md",
        "wiki/concepts/v1.2 notes.md",
        "wiki/desktop.ini/kept.md",
        "wiki/img.png",
        "wiki/sources/Foo.md",
    ]


def test_find_links_parses_both_forms_with_subpath_alias_and_embed():
    text = (
        "see [[Foo]], [[Foo#Heading|shown]], ![[img.png|480]], "
        "[x](wiki/concepts/Foo.md#^c-1), ![](/wiki/img.png), "
        "[u](https://example.org/a(b)) and [[ Spaced ]]"
    )
    found = links.find_links(text)
    assert [
        (link.kind, link.embed, link.target, link.subpath, link.alias) for link in found
    ] == [
        ("wiki", False, "Foo", "", None),
        ("wiki", False, "Foo", "#Heading", "shown"),
        ("wiki", True, "img.png", "", "480"),
        ("markdown", False, "wiki/concepts/Foo.md", "#^c-1", "x"),
        ("markdown", True, "/wiki/img.png", "", ""),
        ("markdown", False, "https://example.org/a(b)", "", "u"),
        ("wiki", False, "Spaced", "", None),
    ]
    assert text[found[1].start : found[1].end] == "[[Foo#Heading|shown]]"


def test_find_links_decodes_a_markdown_destination():
    (link,) = links.find_links("[a](wiki/concepts/Only%20Here.md)")
    assert link.target == "wiki/concepts/Only Here.md"


@pytest.mark.parametrize(
    ("wiki", "path", "rendered"),
    [
        (
            "[[Only Here]]",
            "wiki/concepts/Only Here.md",
            "[Only Here](/wiki/concepts/Only%20Here.md)",
        ),
        ("[[Foo|shown]]", "wiki/concepts/Foo.md", "[shown](/wiki/concepts/Foo.md)"),
        (
            "[[Foo#Heading]]",
            "wiki/concepts/Foo.md",
            "[Foo > Heading](/wiki/concepts/Foo.md#Heading)",
        ),
        (
            "[[Foo#^c-1]]",
            "wiki/concepts/Foo.md",
            "[Foo > ^c-1](/wiki/concepts/Foo.md#^c-1)",
        ),
        ("![[img.png]]", "wiki/img.png", "![](/wiki/img.png)"),
        ("![[img.png|480]]", "wiki/img.png", "![480](/wiki/img.png)"),
        (
            "[[a (b) 100%]]",
            "wiki/a (b) 100%.md",
            "[a (b) 100%](/wiki/a%20(b)%20100%.md)",
        ),
    ],
)
def test_render_markdown_follows_generate_markdown_link(wiki, path, rendered):
    (link,) = links.find_links(wiki)
    assert links.render_markdown(link, path) == rendered


def test_render_encodes_only_backslash_space_and_controls():
    (link,) = links.find_links("[[x]]")
    assert (
        links.render_markdown(link, "w/a\\b c\x01.md")
        == "[a\\b c\x01](/w/a%5Cb%20c%01.md)"
    )


def test_attachment_extensions_are_obsidians_registered_set():
    for extension in (
        "png",
        "jpg",
        "jpeg",
        "gif",
        "bmp",
        "svg",
        "webp",
        "avif",
        "mp3",
        "wav",
        "m4a",
        "3gp",
        "flac",
        "ogg",
        "oga",
        "opus",
        "mp4",
        "webm",
        "ogv",
        "mov",
        "mkv",
        "pdf",
        "canvas",
        "base",
    ):
        assert extension in links.ATTACHMENT_EXTENSIONS
    assert "md" not in links.ATTACHMENT_EXTENSIONS
