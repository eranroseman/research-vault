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


def test_normalize_rewrites_every_resolvable_wikilink_and_is_idempotent(tmp_path):
    index = _index(tmp_path)
    text = "See [[Only Here]] and [[Foo#Heading|shown]] and ![[img.png|480]].\n"
    out, problems = links.normalize(text, index, source="wiki/concepts/Other.md")
    assert out == (
        "See [Only Here](/wiki/concepts/Only%20Here.md) and "
        "[[Foo#Heading|shown]] and ![480](/wiki/img.png).\n"
    )  # Foo is ambiguous (two Foo.md), so its link stays as written
    assert [(p.kind, p.target) for p in problems] == [("ambiguous", "Foo")]
    again, _ = links.normalize(out, index, source="wiki/concepts/Other.md")
    assert again == out


def test_normalize_adds_the_slash_to_a_markdown_destination_that_resolves(tmp_path):
    index = _index(tmp_path)
    text = (
        "[a](wiki/concepts/Only%20Here.md) [b](concepts/Foo.md#^c-1) "
        "[c](./Foo.md) [d](../sources/Foo.md) [e](https://x.org/y) "
        "[f](/wiki/img.png) [g](nowhere.md)\n"
    )
    out, problems = links.normalize(text, index, source="wiki/concepts/Other.md")
    assert out == (
        "[a](/wiki/concepts/Only%20Here.md) [b](/wiki/concepts/Foo.md#^c-1) "
        "[c](./Foo.md) [d](../sources/Foo.md) [e](https://x.org/y) "
        "[f](/wiki/img.png) [g](nowhere.md)\n"
    )
    assert [(p.kind, p.target) for p in problems] == [("dead", "nowhere.md")]


def test_normalize_leaves_dead_and_ambiguous_targets_as_written(tmp_path):
    index = _index(tmp_path)
    text = "[[Foo]] [[nowhere]] ![[gone.png]]\n"
    out, problems = links.normalize(text, index, source="projects/brief/draft.md")
    assert out == text
    assert [(p.kind, p.target, p.candidates) for p in problems] == [
        ("ambiguous", "Foo", ("wiki/concepts/Foo.md", "wiki/sources/Foo.md")),
        ("dead", "nowhere", ()),
        ("dead", "gone.png", ()),
    ]


def test_normalize_masks_code_fences_inline_code_and_comments(tmp_path):
    index = _index(tmp_path)
    text = (
        "```\n[[Only Here]]\n```\n"
        "~~~md\n[[Only Here]]\n~~~\n"
        "inline `[[Only Here]]` here\n"
        "<!-- [[Only Here]] -->\n"
        "%% [[Only Here]] %%\n"
        "real [[Only Here]]\n"
    )
    out, _ = links.normalize(text, index, source="projects/brief/draft.md")
    assert out.count("[[Only Here]]") == 5
    assert out.endswith("real [Only Here](/wiki/concepts/Only%20Here.md)\n")


def test_normalize_skips_anchored_claim_blocks_whole_and_masks_inline_fields(tmp_path):
    """Q19: a committed claim's bytes are frozen (claim-immutability), and
    Dataview reads only `[[…]]` inside a `[k:: …]` field."""
    index = _index(tmp_path)
    text = (
        "- (quote) Mortality fell [@smith2020, p. 3] [supports:: [[smith2020#^c-1]]] ^c-2\n"
        "  > the quoted [[Only Here]] text\n"
        "Prose with [[Only Here]] and a field [related:: [[Only Here]]] here.\n"
    )
    out, _ = links.normalize(text, index, source="projects/brief/draft.md")
    assert out == (
        "- (quote) Mortality fell [@smith2020, p. 3] [supports:: [[smith2020#^c-1]]] ^c-2\n"
        "  > the quoted [[Only Here]] text\n"
        "Prose with [Only Here](/wiki/concepts/Only%20Here.md) and a field "
        "[related:: [[Only Here]]] here.\n"
    )


@pytest.mark.parametrize(
    "block",
    [
        '---\ntype: note\nrelated: "[[Only Here]]"\nmd: "[b](concepts/Foo.md)"\n---\n',
        (
            '---\ntype: note\nrelated: "[[Only Here]]"\nbare: [[Only Here]]\n'
            'md: "[b](concepts/Foo.md)"\nup: [[Foo]]\ngone: "[[nowhere]]"\n---\n'
        ),
    ],
    ids=["quoted-only", "mixed"],
)
def test_normalize_leaves_the_frontmatter_block_byte_for_byte(tmp_path, block):
    """Only the body is normalised: Dataview reads only `[[…]]` as a link in a
    property, so a rewritten one would lose its Link type. Nothing in the
    block is rewritten or reported, dead and ambiguous links included.

    Two blocks, because each catches what the other cannot. Rewriting
    `quoted-only` leaves valid YAML, so a rewrite guarded by "keep the block
    if the YAML breaks" changes its bytes. In `mixed`, rewriting `bare:`
    breaks the YAML, so that guard keeps the bytes as written; there,
    `problems == []` catches any report of the block's links."""
    index = _index(tmp_path)
    out, problems = links.normalize(
        block + "body [[Only Here]]\n", index, source="projects/brief/draft.md"
    )
    assert out == block + "body [Only Here](/wiki/concepts/Only%20Here.md)\n"
    assert problems == []


@pytest.mark.parametrize(
    ("relative", "skipped"),
    [
        ("literature/smith2020.md", True),
        ("log/2026-10-24.md", True),
        ("log.md", True),
        ("inbox/review-queue.md", True),
        ("system/propagations/p.json", True),
        ("wiki/concepts/Foo.md", True),
        ("fulltext/ABCD1234.md", True),
        ("projects/brief/draft.md", False),
        ("inbox/idea.md", False),
        ("daily/2026-10-24.md", False),
        ("system/templates/project.md", False),
        ("index.md", False),
    ],
)
def test_normaliser_skips_the_surfaces_the_spec_names(relative, skipped):
    assert links.is_normalised_surface(relative) is (not skipped)


def test_normalize_never_rewrites_a_relative_target_and_reports_every_dead_one(
    tmp_path,
):
    """`./` and `../` are left as written in both forms (§5.2); a `/`-led
    destination is already normal and left alone. Every one of them is still
    resolved, so a dead one is reported: outside `wiki/` the normaliser is the
    only reader that would say so."""
    index = _index(tmp_path)
    text = (
        "[[./Foo]] [[../sources/Foo|src]] [[../Foo]] [x](./Missing.md) "
        "[y](/wiki/gone.md) [z](../nope.md) [[/wiki/concepts/Only Here]]\n"
    )
    out, problems = links.normalize(text, index, source="wiki/concepts/Other.md")
    assert out == (
        "[[./Foo]] [[../sources/Foo|src]] [[../Foo]] [x](./Missing.md) "
        "[y](/wiki/gone.md) [z](../nope.md) [Only Here](/wiki/concepts/Only%20Here.md)\n"
    )
    assert [(p.kind, p.target) for p in problems] == [
        ("dead", "../Foo"),
        ("dead", "./Missing.md"),
        ("dead", "/wiki/gone.md"),
        ("dead", "../nope.md"),
    ]


def test_normalize_leaves_same_page_anchors_as_written(tmp_path):
    """A same-page link names the linking file; written out as its `/`-led path
    it would break on the file's first `git mv`."""
    index = _index(tmp_path)
    text = "[see](#section), [[#Heading]] and [[#^c-1|that claim]]\n"
    out, problems = links.normalize(text, index, source="projects/brief/draft.md")
    assert out == text
    assert problems == []


def test_normalize_reads_a_colon_wikilink_as_a_name_and_skips_only_a_url(tmp_path):
    """Only a markdown destination can be a URI: `[[re:2020]]` is a captured-set
    key and `[[ghost:2020]]` a dead name, never a skipped URL."""
    index = _index(tmp_path)
    text = "[[re:2020]] [[ghost:2020]] [m](mailto:a@b.c) ![u](https://x.org/a.png)\n"
    out, problems = links.normalize(text, index, source="projects/brief/draft.md")
    assert out == (
        "[re2020](/literature/re2020.md) [[ghost:2020]] "
        "[m](mailto:a@b.c) ![u](https://x.org/a.png)\n"
    )
    assert [(p.kind, p.target) for p in problems] == [("dead", "ghost:2020")]


def test_normalize_leaves_the_seed_index_folder_links_alone_and_unreported(tmp_path):
    """A target ending in `/` is a folder: read as `log.md`, the seed index's
    `[log/](log/)` would be re-pointed at the root log, and the other six
    would be dead at every commit that stages `index.md`."""
    for relative in (
        "log.md",
        "log/2026-10-24.md",
        "system/bases/trust-tier.base",
        "system/bases/open-questions.base",
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n")
    index = links.Index.build(tmp_path, literature={}, names={})
    seed = (Path(links.__file__).parent / "templates/vault/index.md").read_text()
    folders = [link for link in links.find_links(seed) if links.is_folder(link.target)]
    assert len(folders) == 7
    out, problems = links.normalize(seed + "[[wiki/]]\n", index, source="index.md")
    for link in folders:
        assert seed[link.start : link.end] in out
    assert out.endswith("[[wiki/]]\n")
    assert problems == []


_AFTER = "\nafter [[Only Here]]\n"
_AFTER_NORMAL = "\nafter [Only Here](/wiki/concepts/Only%20Here.md)\n"


@pytest.mark.parametrize(
    "fenced",
    [
        "> ~~~\n> [[Only Here]] [[nowhere]]\n> ~~~\n",
        "> [!note]\n> ```\n> [[Only Here]]\n>\n> [[Only Here]] [[nowhere]]\n> ```\n",
        "1. a\n    1. b\n        ~~~\n        [[Only Here]] [[nowhere]]\n        ~~~\n",
        "- ~~~\n  [[Only Here]] [[nowhere]]\n  ~~~\n",
        "```\n[[Only Here]] [[nowhere]]\n   ```\n",
        "```markdown\n    ```\n    [[Only Here]] [[nowhere]]\n    ```\n```\n",
        "```markdown\n> [!note]\n> ```python\n> [[Only Here]] [[nowhere]]\n> ```\n```\n",
        "```\n* ```\n[[Only Here]] [[nowhere]]\n```\n",
        "~~~\n1. ~~~\n   [[Only Here]] [[nowhere]]\n~~~\n",
    ],
    ids=[
        "blockquote",
        "callout-with-blank-line",
        "nested-list",
        "list-marker-line",
        "closer-indented-three",
        "indented-fence-in-a-fence",
        "callout-fence-in-a-fence",
        "bullet-fence-in-a-fence",
        "ordered-fence-in-a-fence",
    ],
)
def test_normalize_masks_a_fence_in_a_container_up_to_its_own_closer(tmp_path, fenced):
    """A fence opens behind any container prefix, a list marker included, but
    closes only behind quotes and indent: a list marker opens a new container,
    so a line led by one is content. Only a closer at the opener's `>` depth,
    indented at most three columns away from it, ends the fence: a fence
    quoted or listed inside one is content. The code inside is left as
    written and unreported, and the link after it is rewritten."""
    index = _index(tmp_path)
    out, problems = links.normalize(
        fenced + _AFTER, index, source="projects/brief/draft.md"
    )
    assert out == fenced + _AFTER_NORMAL
    assert problems == []


def test_normalize_masks_no_comment_inside_code_and_no_span_across_a_blank_line(
    tmp_path,
):
    """A `%%` or `<!--` inside a fence or a code span is code, not a comment
    running to the end of the file; a code span never crosses a blank line;
    and a line holding ```x``` is a code span, not a fence."""
    index = _index(tmp_path)
    text = (
        "```sql\nSELECT a %% b\n```\n"
        "~~~\n%% <!-- c\n~~~\n"
        "one [[Only Here]] and `%%` and `<!--`\n\n"
        "a `b\n\n"
        "two [[Only Here]]\n\n"
        "```x``` then three [[Only Here]]\n\n"
        "later `c` d\n"
    )
    out, problems = links.normalize(text, index, source="projects/brief/draft.md")
    assert out == text.replace(
        "[[Only Here]]", "[Only Here](/wiki/concepts/Only%20Here.md)"
    )
    assert problems == []


@pytest.mark.parametrize(
    "text",
    [
        "---\nrelated: [[Only Here]]\nup: [[nowhere]]\n---",
        "---\nrelated: [[Only Here]]\nup: [[nowhere]]\n",
        "---\r\nrelated: [[Only Here]]\r\nup: [[nowhere]]\r\n",
    ],
    ids=["closed-at-eof-without-newline", "unterminated", "unterminated-crlf"],
)
def test_normalize_reports_an_unterminated_frontmatter_block_once_and_rewrites_nothing(
    tmp_path, text
):
    """With no closing `---` line read_okf would accept, the note is not
    normalised: one `frontmatter` Problem for the note, written as its opening
    line, and none for the links in it."""
    index = _index(tmp_path)
    out, problems = links.normalize(text, index, source="projects/brief/draft.md")
    assert out == text
    assert [(p.kind, p.target, p.candidates, p.written) for p in problems] == [
        ("frontmatter", "", (), "---")
    ]


def test_normalize_reports_each_problem_with_its_link_as_written(tmp_path):
    index = _index(tmp_path)
    text = (
        "---\nrelated: [[Only Here|here]]\n---\n"
        "[g](nowhere.md) ![[x.png]] [[Foo|B]] [y](/wiki/gone.md)\n"
    )
    _, problems = links.normalize(text, index, source="projects/brief/draft.md")
    assert [(p.kind, p.target, p.written) for p in problems] == [
        ("dead", "nowhere.md", "[g](nowhere.md)"),
        ("dead", "x.png", "![[x.png]]"),
        ("ambiguous", "Foo", "[[Foo|B]]"),
        ("dead", "/wiki/gone.md", "[y](/wiki/gone.md)"),
    ]


def test_normalize_reads_a_backslashed_relative_target_as_resolve_does(tmp_path):
    """One fold serves resolving and keeping: `..\\sources\\Foo` resolves as
    relative, so it is kept as written like `../sources/Foo`."""
    index = _index(tmp_path)
    text = "[[..\\sources\\Foo|src]] [x](.\\nowhere.md)\n"
    out, problems = links.normalize(text, index, source="wiki/concepts/Other.md")
    assert out == text
    assert [(p.kind, p.target) for p in problems] == [("dead", ".\\nowhere.md")]


# The captured set of one note and no other file: what `names_note` must agree
# with, target for target, since both read a target through one candidate step.
_NOTE = "literature/old2020.md"
_LITERATURE_ONLY = links.Index([], literature={"old2020": _NOTE}, names={})


@pytest.mark.parametrize(
    ("target", "named"),
    [
        ("old2020", True),
        ("literature/old2020", True),
        ("literature/old2020.md", True),
        ("/literature/old2020.md", True),
        ("../../literature/old2020.md", True),  # from wiki/sources/A.md
        ("../literature/old2020.md", False),  # wiki/literature/old2020.md from there
        ("old2020a", False),
        ("concepts/old2020", False),
        ("https://x.org/old2020", False),
        ("/Literature/old2020.md", True),  # a path matches case-insensitively
        ("literature/OLD2020", True),
        ("Old2020", False),  # the bare key exactly, as the captured set holds it
        ("/literature/old2020/", False),  # a folder names no note
        ("../../literature/old2020/", False),
        ("old%32020", False),  # a target is never decoded a second time
    ],
)
def test_names_note_recognises_every_spelling_of_a_literature_link(target, named):
    source = "wiki/sources/A.md"
    assert links.names_note(target, "old2020", source=source) is named
    assert (_LITERATURE_ONLY.resolve(target, source=source) == [_NOTE]) is named


@pytest.mark.parametrize(
    ("target", "named"),
    [
        ("/old2020.md", False),
        ("./old2020.md", False),
        ("../old2020.md", False),
        ("/old2020", False),
        ("/literature/old2020.md", True),
        ("./literature/old2020.md", True),
        ("old2020.md", True),
        ("old2020", True),
    ],
)
def test_names_note_reads_a_led_path_only_as_the_literature_path(target, named):
    """A `/`-led, `./` or `../` target is a path, resolved from its source as
    `Index.resolve` reads it: from a root note `/old2020.md` is the root file
    `old2020.md`, never the note. Only a target led by neither is a key form."""
    assert links.names_note(target, "old2020", source="index.md") is named
    assert (_LITERATURE_ONLY.resolve(target, source="index.md") == [_NOTE]) is named


def test_rewrite_key_renames_wiki_and_markdown_links_and_display_text():
    text = (
        "[[old2020]] [[old2020#^c-1]] [[old2020|alias]] [old2020](/literature/old2020.md) "
        "[shown](literature/old2020.md#^c-1) [x](../../literature/old2020.md) "
        "[[old2020a]] [other](/literature/other2020.md) ![[old2020]]\n"
    )
    assert links.rewrite_key(
        text, "old2020", "new2020", source="wiki/sources/A.md"
    ) == (
        "[[new2020]] [[new2020#^c-1]] [[new2020|alias]] [new2020](/literature/new2020.md) "
        "[shown](/literature/new2020.md#^c-1) [x](/literature/new2020.md) "
        "[[old2020a]] [other](/literature/other2020.md) ![[new2020]]\n"
    )


def test_rewrite_key_renames_the_display_text_the_normaliser_renders():
    """`render_markdown` writes `[[old2020#^c-1]]` as `[old2020 > ^c-1](…)`:
    the key in that text is renamed with the target; other text is kept."""
    text = (
        "[old2020 > ^c-1](/literature/old2020.md#^c-1) "
        "[old2020 >x](/literature/old2020.md) [d](/literature/old2020/)\n"
    )
    assert links.rewrite_key(text, "old2020", "new2020", source="index.md") == (
        "[new2020 > ^c-1](/literature/new2020.md#^c-1) "
        "[old2020 >x](/literature/new2020.md) [d](/literature/old2020/)\n"
    )


def test_rewrite_key_reads_a_colon_key_as_a_name_only_in_a_wikilink():
    """A captured-set key may hold a `:`: `[[re:2020]]` names it, while a
    markdown destination `re:2020` is a URI (`is_external`), never a note."""
    text = "[[re:2020]] [x](re:2020)\n"
    assert links.rewrite_key(text, "re:2020", "re2021", source="index.md") == (
        "[[re2021]] [x](re:2020)\n"
    )


def test_find_links_reads_a_table_escaped_pipe_as_the_alias_separator():
    """R2, §5.2: inside a table Obsidian writes `[[x\\|y]]`, the pipe escaped
    so the row keeps its cells. `\\|` separates the alias, and the `\\` is no
    part of the target (else `_fold` makes it a `/` and the link a folder);
    the span stays as written."""
    text = "| [[ghost2021\\|Ghost]] | [[Foo#Heading\\|shown]] | ![[img.png\\|480]] |"
    found = links.find_links(text)
    assert [
        (link.target, link.subpath, link.alias, text[link.start : link.end])
        for link in found
    ] == [
        ("ghost2021", "", "Ghost", "[[ghost2021\\|Ghost]]"),
        ("Foo", "#Heading", "shown", "[[Foo#Heading\\|shown]]"),
        ("img.png", "", "480", "![[img.png\\|480]]"),
    ]
    assert not any(links.is_folder(link.target) for link in found)


def test_normalize_rewrites_a_table_escaped_wikilink_to_a_pipe_free_link(tmp_path):
    """R2: the markdown form `[Here](/…)` carries no `|`, so the table cell
    needs no escape and the row keeps its cells; a dead one is reported
    under its target, its span as written."""
    index = _index(tmp_path)
    text = "| a | b |\n| --- | --- |\n| [[Only Here\\|Here]] | [[nowhere\\|N]] |\n"
    out, problems = links.normalize(text, index, source="projects/brief/draft.md")
    assert out == (
        "| a | b |\n| --- | --- |\n"
        "| [Here](/wiki/concepts/Only%20Here.md) | [[nowhere\\|N]] |\n"
    )
    assert [(p.kind, p.target, p.written) for p in problems] == [
        ("dead", "nowhere", "[[nowhere\\|N]]")
    ]


def test_rewrite_key_keeps_a_table_escaped_pipe_as_written():
    """A re-keyed wikilink in a table keeps its `\\|`: a bare `|` would split
    the cell."""
    text = "| [[old2020\\|Old]] | [[old2020#^c-1\\|q]] | [[old2020|x]] |\n"
    assert links.rewrite_key(text, "old2020", "new2020", source="index.md") == (
        "| [[new2020\\|Old]] | [[new2020#^c-1\\|q]] | [[new2020|x]] |\n"
    )


@pytest.mark.parametrize(
    "field",
    [
        "up:: [[Only Here]] and [[nowhere]]",
        "- related:: [[Only Here]] [[nowhere]]",
        "  * next :: [x](wiki/concepts/Only%20Here.md) [[nowhere]]",
        "1. prev:: [[Only Here]], [[nowhere]]",
        "Due Date 2:: [[Only Here]] [[nowhere]]",
        "Prose (prev:: [[Only Here]]) and (next:: [[nowhere]]) end",
        "Prose [due date:: [[Only Here]]] and [k_2:: [[nowhere]]] end",
        "Prose [up:: [x](wiki/concepts/Only%20Here.md)] (up:: [y](nowhere.md)) end",
    ],
)
def test_normalize_masks_every_dataview_inline_field(tmp_path, field):
    """R3, Q19: Dataview reads only `[[…]]` as a Link inside an inline field,
    in all three of its syntaxes — a line-leading `key:: value` (behind a
    list marker too), `[key:: value]` and `(key:: value)`, keys with spaces,
    digits and `_`. A link in one is neither rewritten nor reported."""
    index = _index(tmp_path)
    text = field + "\n"
    out, problems = links.normalize(text, index, source="projects/brief/draft.md")
    assert (out, problems) == (text, [])


def test_normalize_reads_no_field_where_dataview_reads_none(tmp_path):
    """A single colon, a `::` behind other text and a claim line are no
    line-leading field: their links are normalised as prose."""
    index = _index(tmp_path)
    text = (
        "See: [[Only Here]]\n"
        "- 09:00 met [[Only Here]]\n"
        "Prose with [[Only Here]] then a (paren) and std::vector\n"
        "- (inference) [[Only Here]] says x:: y [@smith2020]\n"
    )
    out, _ = links.normalize(text, index, source="projects/brief/draft.md")
    rendered = "[Only Here](/wiki/concepts/Only%20Here.md)"
    assert out == text.replace("[[Only Here]]", rendered)
