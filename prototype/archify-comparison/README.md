# Throwaway prototype — archify vs hand-written Mermaid

Captured as a primary source for the resolution of
[#86 "archify skill candidate"](https://github.com/eranroseman/knowledge-harness/issues/86).
Not production code. Nothing here is maintained, and this branch is never merged to `main`.

## The question it answered

Does archify produce a diagram good enough to justify its authoring cost, compared with
hand-written Mermaid rendered via CDN — the pattern `improve-codebase-architecture`
already uses? The prior discussion had run on descriptions and code review; this made one
concrete artifact both ways so the difference could be looked at.

## Subject

One real structure from this project: the `research-vault` / `software-development` /
`sensemaking` / `superpowers`-fork / `harness-backup` distribution topology. Eight
components, eight connections, one boundary, three summary cards — identical content in
both versions.

## Files

| File | What it is |
|---|---|
| `distribution-topology.architecture.json` | The archify spec. 5,439 bytes. All 8 components hand-placed with `pos`/`size`; explicit `fromSide`/`toSide` on all 8 connections. |
| `archify-topology.html` | archify output, 713,200 bytes, `sha256:7ad08a98836925877995e834e96b4cd6ccb1aa501ab5173aff7178295d2ce8cd`. Standalone; open it directly. |
| `mermaid-topology.html` | The counterpart: 18 lines of Mermaid in a `<pre class="mermaid">`, rendered by mermaid@11 from jsDelivr, Tailwind via CDN. Needs network. |
| `archify-rendered.png` | Headless screenshot of the archify output at 1600×1800. |
| `mermaid-rendered.png` | Headless screenshot of the Mermaid version at 1600×1100. |

## Reproducing

archify at `HEAD = 06dd052`, version `2.17.0-dev.1`:

```bash
node bin/archify.mjs validate architecture distribution-topology.architecture.json --quality showcase --json
node bin/archify.mjs deliver  architecture distribution-topology.architecture.json out.html --quality showcase --json
```

Screenshots were taken from WSL2 through Windows interop, against a copy of the file at a
path Windows can address:

```bash
"/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --headless=new --disable-gpu --hide-scrollbars --window-size=1600,1800 \
  --screenshot="C:\temp\proto\archify.png" "file:///C:/temp/proto/archify-topology.html"
```

## What it cost

archify took three validation rounds: a 7px micro-segment error on the `claude-code` →
`harness-backup` edge, then eight `clean-flow/endpoint-side-direction` errors after the
components were moved, then a pass. The diagnostics named the exact segment
`[385,85] → [385,92]`, the overlapping label rectangle, and a suggested
`labelAt [385,138] or labelDy +59`.

Mermaid took one shot and zero rounds.

## The answer

Recorded on #86: **go, adopt as-is.** archify routed every edge orthogonally with no
crossings and placed every label clear; Mermaid's auto-layout reversed two nodes against
source order, pushed `harness-backup` into the left gutter, and rendered the dashed edge
close to invisible. The split that justifies keeping both: Mermaid wins for a diagram read
once while thinking, archify for one read repeatedly by someone who was not in the
conversation. They compose — archify ingests pasted Mermaid.
