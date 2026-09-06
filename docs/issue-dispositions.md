# Issue dispositions

Disposition: current (2026-09-06)

Written by the status-marking pass of `docs/superpowers/specs/2026-09-05-assembly-design.md`
§10 and maintained by `scripts/dispositions.py`. One row per issue the pass
dispositioned, closed issues included: closing an issue is one of the things a
disposition decides, so the row outlives it as the record of why.
Issue vocabulary: `absorbed-by: <spec §>`, `superseded`, `still-open`,
`pending-map` — a different axis from the `Disposition:` line above, which is
this file's own marker in the *document* vocabulary.
`tests/test_dispositions.py` refuses an off-vocabulary row and, where `gh` is
usable, an open issue with no row.

The `Title` column is read from GitHub at write time and is not round-tripped
into a proposal row; a re-render given no fresh listing carries the committed
cells forward rather than blanking them. `Note` holds the author's *reason*,
and never the title again. A reader gets both without clicking through.

| Issue | Title                                                                                                                 | Disposition       | Note                                                                                 |
| ----- | --------------------------------------------------------------------------------------------------------------------- | ----------------- | ------------------------------------------------------------------------------------ |
| 124   | Four errata in the assembly spec §10, one of them created by the pass it specifies                                    | still-open        | four prose errata in the spec, one made false by this pass's own correct decision    |
| 123   | docs/testing.md names the wrong gate for the issue-table coverage leg                                                 | still-open        | documentation-class; docs/testing.md names the wrong gate for a live leg             |
| 122   | The issue table hardcodes its own disposition, discarding the reviewed row for it                                     | still-open        | documentation-class; the discarded value is silent, not destructive                  |
| 121   | Seam register: two guards in scripts/dispositions.py that a neighbouring function did not adopt                       | still-open        | seam register S3 and S4 — both bounded, both currently linted or refused loudly      |
| 120   | Remove the Note-as-title compensation: give the disposition TSV its own title column                                  | still-open        | the eliminate rung under the Note-as-title compensation; #121's seams sit on it      |
| 119   | Specify the scoping review workflow against PRISMA-ScR                                                                | still-open        | §10 names this as staying open                                                       |
| 118   | Workflow-component audit: disposition the nine components the ingest redesign froze                                   | absorbed-by: §5   | §10 names this as absorbed by §5                                                     |
| 117   | Specify the search step against PRISMA-S                                                                              | still-open        | §10 names this as staying open                                                       |
| 116   | Land the ingest redesign's vocabulary and retire the two suspended decision records                                   | still-open        | §10 names this as staying open                                                       |
| 115   | Upstream filing: the Zotero local API serves no /deleted endpoint                                                     | still-open        | outbound upstream filing; nothing internal decides it                                |
| 114   | Upstream filing: every translator format returns HTTP 500 on the Zotero 10.0.1 local API                              | still-open        | outbound upstream filing; nothing internal decides it                                |
| 113   | Upstream filing: the Zotero local API does not expose the retraction flag                                             | still-open        | outbound upstream filing; nothing internal decides it                                |
| 111   | Carrying adhd: a plugin whose description must be rewritten before it ships                                           | still-open        | sibling-owned; carried by the sibling-project milestone (#5), not by this vocabulary |
| 110   | Carrying archify: an adopted skill-only, unpinnable component                                                         | still-open        | sibling-owned; carried by the sibling-project milestone (#5), not by this vocabulary |
| 109   | Redesign the import process from first principles                                                                     | superseded        | the 2026-09-04 spec performed the redesign; the assembly spec re-framed it as lane 1 |
| 108   | Redesign: vault-owned SSOT bibliography record; retire the whole-library auto-export                                  | pending-map       | lane 1 decides it; §7.1 schedules the question rather than answering it              |
| 107   | stamp_types(paths=...) bypasses the vault-boundary symlink check via a symlinked ancestor directory                   | still-open        | concrete defect; no register decides it                                              |
| 104   | Upstream filing: OKF has no bundle-scope marker (no way to put a subtree outside the bundle)                          | still-open        | outbound upstream filing; nothing internal decides it                                |
| 103   | Upstream filing: OKF §5.1 has no locator/pinpoint concept                                                             | still-open        | outbound upstream filing; nothing internal decides it                                |
| 102   | Scaffolded vault CI templates install from the old knowledge-harness slug                                             | still-open        | concrete defect; no register decides it                                              |
| 100   | Regulated-workload obligations for the coaching apps: which line, and what changes on each side of it                 | still-open        | sibling-owned; carried by the sibling-project milestone (#5), not by this vocabulary |
| 97    | Review research-vault's third-party components: fork or vendor?                                                       | absorbed-by: §5.2 | §10 names this as absorbed by §5.2                                                   |
| 96    | Distribution model for the recommended plugin bucket                                                                  | absorbed-by: §6   | §10 names this as absorbed by §6                                                     |
| 94    | Implement the one-source glossary (accepted 2026-08-28 proposal, Q1)                                                  | pending-map       | component or scope question a lane settles                                           |
| 91    | Complete the research-vault identity rename: distribution, plugin manifests, repo slug                                | still-open        | concrete defect; no register decides it                                              |
| 88    | neuroarxiv skill candidate                                                                                            | pending-map       | component or scope question a lane settles                                           |
| 84    | out-of-scope-bug → issue mechanism                                                                                    | pending-map       | component or scope question a lane settles                                           |
| 82    | Prior-art-search skill                                                                                                | pending-map       | component or scope question a lane settles                                           |
| 79    | consistency-audit vs adversarial-verification skill boundary                                                          | pending-map       | component or scope question a lane settles                                           |
| 78    | local deploy-drift doctor                                                                                             | absorbed-by: §9   | §10 names this as absorbed by §9                                                     |
| 71    | Pre-slice audit: formatter and linter ownership                                                                       | pending-map       | component or scope question a lane settles                                           |
| 70    | Validate vault and generated-bundle OKF conformance                                                                   | pending-map       | component or scope question a lane settles                                           |
| 69    | Agent Plugins standard conformance (design check)                                                                     | still-open        | sibling-owned; carried by the sibling-project milestone (#5), not by this vocabulary |
| 67    | File the queued upstream reports                                                                                      | still-open        | outbound upstream filing; nothing internal decides it                                |
| 66    | adopt/adapt/reject/defer skill survey                                                                                 | pending-map       | component or scope question a lane settles                                           |
| 65    | kh: CLI reference skill (four-state canonical home decision + build)                                                  | pending-map       | component or scope question a lane settles                                           |
| 64    | Harness-backup retirement decision                                                                                    | still-open        | sibling-owned; carried by the sibling-project milestone (#5), not by this vocabulary |
| 63    | upstream-drift monitoring approach                                                                                    | absorbed-by: §9   | §10 names this as absorbed by §9                                                     |
| 62    | Setup/materialization mechanism decision                                                                              | absorbed-by: §9   | §10 names this as absorbed by §9                                                     |
| 59    | Repo and manifest structure decision                                                                                  | still-open        | sibling-owned; carried by the sibling-project milestone (#5), not by this vocabulary |
| 58    | Design and implementation plan                                                                                        | still-open        | sibling-owned; carried by the sibling-project milestone (#5), not by this vocabulary |
| 53    | software-development plugin — wayfinder map                                                                           | still-open        | sibling-owned; carried by the sibling-project milestone (#5), not by this vocabulary |
| 52    | Write a proposal for a claims layer                                                                                   | pending-map       | component or scope question a lane settles                                           |
| 50    | Document Zotero 10 capabilities for Report specifications                                                             | pending-map       | component or scope question a lane settles                                           |
| 49    | verify agent plugin compliance                                                                                        | pending-map       | component or scope question a lane settles                                           |
| 48    | Specify the next Report workflow: specialization and resources                                                        | superseded        | August Report roadmap; assembly spec lane structure replaces it                      |
| 46    | Assess the first repo-to-vault migration for the Report workflow                                                      | superseded        | August Report roadmap; assembly spec lane structure replaces it                      |
| 45    | Disposition the complete post-slice improvement queue                                                                 | superseded        | August Report roadmap; assembly spec lane structure replaces it                      |
| 44    | Choose the next post-slice architecture deepening                                                                     | superseded        | August Report roadmap; assembly spec lane structure replaces it                      |
| 43    | Audit the post-Plan-W repository for over-engineering                                                                 | superseded        | August Report roadmap; assembly spec lane structure replaces it                      |
| 42    | Run Plan W: Quality Tail                                                                                              | still-open        | queued work with a named target                                                      |
| 41    | Run the revised Plan S validation slice                                                                               | still-open        | queued work with a named target                                                      |
| 39    | Define source-class admission, import, and Summary routing                                                            | superseded        | August Report roadmap; assembly spec lane structure replaces it                      |
| 38    | Define the Report review loop                                                                                         | superseded        | August Report roadmap; assembly spec lane structure replaces it                      |
| 36    | Research acquisition and Summary tooling beyond scholarly papers                                                      | pending-map       | component or scope question a lane settles                                           |
| 35    | Audit current plugin coverage of the Report case-study questions                                                      | superseded        | August Report roadmap; assembly spec lane structure replaces it                      |
| 34    | Classify the current corpus across the repo–vault seam                                                                | superseded        | August Report roadmap; assembly spec lane structure replaces it                      |
| 33    | Report workflow and post-slice roadmap — wayfinder map                                                                | superseded        | August Report roadmap; assembly spec lane structure replaces it                      |
| 32    | test_config_validity: str.index() over .pre-commit-config.yaml raises if the parsed hook is last                      | still-open        | concrete defect; no register decides it                                              |
| 31    | archive: the API-confirmed snapshot path has no shape or target-URL check                                             | still-open        | concrete defect; no register decides it                                              |
| 30    | Act on the process-reconstruction note's recommendations                                                              | still-open        | queued work with a named target                                                      |
| 27    | Check-id sweep: phrase-less hole (skills/publish/SKILL.md:37 shape)                                                   | still-open        | concrete defect; no register decides it                                              |
| 25    | Vault AGENTS.md template: preamble omits system/bibliography.json from the deny surfaces                              | still-open        | concrete defect; no register decides it                                              |
| 23    | Precision-ordering choice: max() over notice_date strings sorts less-precise before more-precise within the same year | still-open        | concrete defect; no register decides it                                              |
| 22    | Strengthen substitution-prone trust-sensitive test assertions                                                         | still-open        | concrete defect; no register decides it                                              |
| 21    | Renamed literature notes skip the per-key attestation diagnostic                                                      | still-open        | concrete defect; no register decides it                                              |
| 20    | Attestation comparison evadable via duplicate frontmatter keys (last-key-wins)                                        | still-open        | concrete defect; no register decides it                                              |
| 19    | Machine-owned frontmatter guard: other MANAGED_FIELDS keys are outside it                                             | still-open        | concrete defect; no register decides it                                              |
| 18    | Post-slice adoptions from History Notes comparison                                                                    | pending-map       | component or scope question a lane settles                                           |
| 17    | The human-reviewed trust tier cannot be minted by any shipped surface                                                 | still-open        | concrete defect; no register decides it                                              |
| 16    | Keyless comment-only annotations block import after duplicate-anchor safeguard                                        | still-open        | concrete defect; no register decides it                                              |
