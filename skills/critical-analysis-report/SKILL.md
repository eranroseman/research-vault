---
name: critical-analysis-report
description: Write a critical analysis report of one research paper, with a notes file holding the evidence behind it.
disable-model-invocation: true
---

# Critical analysis report

**No citation, no finding.** Give every claim about the paper a **locator**: section, page, figure, or table. Count every number from the text or the reference list. Record in Coverage whatever you could not read or check.

## Input

The first argument names the paper; the optional second names the report path. You need the full text: given only an abstract, citation, or DOI, obtain it first or stop and say so.

## Process

### 1. Read once, notes open

Create the notes from `references/notes-template.md` and fill Identity first, from the full text. Wrong paper: stop and say what you have. Read end to end, filling the section map and the template answers chunk by chunk.

**Done when:** Identity and section map filled; every page read once; every unread part listed under the notes' Coverage.

### 2. Record the promises

Fill Promises. The body keeps each promise or breaks it; broken ones go to Gaps.

**Done when:** five promises, each quoted from or located in the title, abstract, introduction, or conclusion.

### 3. Answer the template's questions

`references/report-template.md` is the question bank. Answer each question in the notes under the same heading, with a locator or a "none found" line. Along the way:

- Classify the method family (Background: the research-method menu); the table at the top of `references/background.md` says which sections that family opens.
- Fill Reference counts from the reference list.
- Fill Related work checks (template 1.5) with whatever citation index or web access you have.
- Fill Lookups with every term you cannot define.

**Done when:** every notes section filled; every "none found" in Gaps with its destination.

### 4. Write the report

Follow `references/report-template.md`. Then run `python3 scripts/check_report.py <report>` (path relative to this file; `--help` for options).

**Done when:** checker reports no errors; every Context claim about authors, venue, and prior work carries its provenance mark.

### 5. Verify against the paper

Give a fresh-context subagent `prompts/verify.md` and the three paths. Fix or drop each claim it returns. Without a subagent facility, run the prompt yourself and record "self-verified".

**Done when:** every returned claim fixed or dropped; Coverage records claims checked and changed; checker clean again.

## Rules

- **Provenance.** The reader must be able to tell three kinds of claim apart: what the paper says (locator), what you checked outside it (source named), and what you infer (said so). This matters most for author background, prior work, venue rigor, and the tree-forward check.
- **Nothing silent.** Write "none found; checked: <where>" when the paper doesn't answer, "not checked: <reason>" for a check you could not run, and "not applicable: <reason>" for a topic the paper lacks.

## Output

- Report: the path given, else `critical-analysis-<paper-slug>.md` in the current directory. Notes: the report path with `.notes.md` in place of `.md`.
- 1,500 to 3,000 words unless told otherwise.
- Hand over both paths and the Coverage section.
