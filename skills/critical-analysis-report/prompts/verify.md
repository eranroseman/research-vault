# Verify the report against the paper

Fill in the paths, then give everything below the rule to a fresh-context subagent.

______________________________________________________________________

You are verifying a critical analysis of a research paper.

- Paper: {{paper path or URL}}
- Report: {{report path}}
- Notes: {{notes path}}

One question per cited claim: does the location say what the report says it says?

1. From the report's section 3, Critical discussion, list every claim with a locator (section, page, figure, table, appendix, or a section name such as Introduction).

2. Add the counts in 1.5 (references; with an author; from the authors' institution; year span) and the method family in 2.2.

3. Open each locator, read enough around it, and give one verdict:

   - supported: the location says this
   - partly: the location says something weaker, narrower, or different in a way that matters
   - unsupported: the location says something else
   - not found: the locator does not exist or would not open; say what you tried
     Recount the references yourself.

4. List unsupported and not-found claims first, then partly supported ones, then one line covering all supported ones:

   ```
   report line <N>: <claim, shortened>; <verdict>; <what the location says, one sentence, quoted where short>
   ```

   Then `checked: <sections, pages, figures, tables opened>`.
   Then `counts: references <n>, with an author <n>, same institution <n>, years <first>-<last>`.

Leave all three files untouched. Report only on claims the report already makes. Quote the paper wherever the quote is short. Keep the reply under 600 words plus the claim list.
