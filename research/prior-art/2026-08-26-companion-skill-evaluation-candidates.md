# Companion skill-evaluation candidate dispositions

**Verdict (2026-08-26):** The companion needs one cross-harness behavioral
evaluation contract, not a new catalog of knowledge tooling or another
subjective scorecard. Adopt the official Agent Skills paired-evaluation loop;
adapt only Anthropic's skill-type and maintenance heuristics into that loop;
reject the two OKF candidates and the third-party skill-quality scorecard; and
defer the portable plugin auditor until the design gate selects the Agent
Plugins root contract. These are inputs to [Companion: design
spec](https://github.com/eranroseman/knowledge-harness/issues/58), not that
ticket's decisions about plugin name, repository, front door, manifests, or
vendoring policy.

The six rows below are exhaustive. Each named family has exactly one
disposition.

| #   | Candidate family                                                                                                                                        | Disposition | Constraint carried to the design gate                                                                                                                                                                                                                             |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | [Open Knowledge Format ecosystem map](https://okf.md/ecosystem-map/)                                                                                    | **Reject**  | Do not use the map as a companion roster, dependency list, or maturity authority. It surveys knowledge-bundle products, outside the companion's distribution-and-maintenance boundary.                                                                            |
| 2   | [`okf-open-knowledge-format`](https://github.com/fabricioctelles/skills/tree/b10f69fd2402e3d66bbd83f112bfe64788bc82b2/skills/okf-open-knowledge-format) | **Reject**  | Do not install or vendor it. OKF authoring and validation are knowledge-harness product concerns, explicitly outside this map.                                                                                                                                    |
| 3   | [Agent Skills: Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills)                                                | **Adopt**   | Make its paired, clean-context, evidence-graded evaluation loop the minimum behavioral contract for companion-owned and deliberately adapted skills. Reference the maintained page; do not vendor its prose.                                                      |
| 4   | [Improving skill-creator: Test, measure, and refine Agent Skills](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills) | **Adapt**   | Carry only the skill-type classification, model-change regression trigger, and trigger-precision lane into a harness-neutral protocol. The companion maintainer owns the Claude Code and Codex adapters and revalidates them on supported harness/model upgrades. |
| 5   | [`skill-evaluation`](https://github.com/fabricioctelles/skills/tree/b10f69fd2402e3d66bbd83f112bfe64788bc82b2/skills/skill-evaluation)                   | **Reject**  | Do not ship its 0–100 rubric, arithmetic gate, or self-reported trigger test. Existing machinery plus the official paired loop covers its useful surface with less false precision.                                                                               |
| 6   | [`agent-plugin-eval`](https://github.com/fabricioctelles/skills/tree/b10f69fd2402e3d66bbd83f112bfe64788bc82b2/skills/agent-plugin-eval)                 | **Defer**   | **Reopen trigger:** the design gate records root `plugin.json` conformance to Agent Plugins 1.x as a companion target. Until then, do not vendor or build around its scanner.                                                                                     |

## Boundary and method

The governing map defines the companion as the cross-harness distribution and
maintenance layer for shared skills, routing, setup, and drift, supporting
Claude Code and Codex. It excludes Report, vault workflow, and other
knowledge-harness product features. This note therefore evaluates whether a
candidate improves shared-skill authoring, behavioral evaluation, package
validation, or update discipline. A generally useful knowledge format is still
out of scope if it does not serve one of those jobs.

Evidence was collected as follows:

- Read all three candidate directories and the root license from
  `fabricioctelles/skills` at commit
  [`b10f69fd2402e3d66bbd83f112bfe64788bc82b2`](https://github.com/fabricioctelles/skills/commit/b10f69fd2402e3d66bbd83f112bfe64788bc82b2).
  Repository claims below refer only to those pinned bytes.
- Read the three named web pages on 2026-08-26. They are dynamic sources, so
  every use below carries that access date.
- Verified the Agent Skills repository's license statement at commit
  [`69ef37e9424c0a7ea9dd2293b559e43ec8176379`](https://github.com/agentskills/agentskills/commit/69ef37e9424c0a7ea9dd2293b559e43ec8176379).
- Compared the candidates with the companion's local baseline at
  [`7300714d8ccb07d7e2a2458b5b471b239aabd9fc`](https://github.com/eranroseman/knowledge-harness/commit/7300714d8ccb07d7e2a2458b5b471b239aabd9fc),
  the installed Codex `skill-creator` system bundle (accessed 2026-08-26;
  SHA-256 `5714dd6fb6c5c22c7b72dd29e6600a851d233318ecaecfe061ed7a4e662dda81`
  of its sorted per-file SHA-256 manifest), and Superpowers' pinned
  [`writing-skills`](https://github.com/obra/superpowers/blob/44c9b2d6e889982ac18c27d05a19fefe335194e1/skills/writing-skills/SKILL.md).
- Inspected source statically. No candidate was installed, no bundled program
  was executed, and no general ecosystem survey was attempted.

## What the companion already has

The useful comparison is against the whole current evaluation stack, not
against an empty directory.

| Existing layer                | What it already proves                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Remaining gap                                                                                  |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Codex `skill-creator`         | Frontmatter/name validation, unfinished-scaffold detection, script checks, and an optional independent forward test for complex skills.                                                                                                                                                                                                                                                                                                                                                                          | It does not define a repeatable paired benchmark workspace or aggregate quality/cost deltas.   |
| Superpowers `writing-skills`  | Failure-first pressure scenarios, no-skill baseline, fresh subagent contexts, behavior-specific cases, and red/green iteration. Its source explicitly maps skill authoring to TDD.                                                                                                                                                                                                                                                                                                                               | It lacks a shared result schema, token/time aggregation, and a human-review record.            |
| Repository skill contracts    | [`tests/test_skill_contracts.py`](https://github.com/eranroseman/knowledge-harness/blob/7300714d8ccb07d7e2a2458b5b471b239aabd9fc/tests/test_skill_contracts.py) checks every shipped skill's parseability, name/path parity, invocation policy, command identifiers, and template references. [`tests/test_config_validity.py`](https://github.com/eranroseman/knowledge-harness/blob/7300714d8ccb07d7e2a2458b5b471b239aabd9fc/tests/test_config_validity.py) adds literal-frontmatter and configuration checks. | These deterministic contracts catch shape and drift, not whether a skill improves task output. |
| House verification discipline | The method record already requires counted adversarial passes, planted failures, discrimination proofs, and pinned vendored-fork provenance ([method ledger](https://github.com/eranroseman/knowledge-harness/blob/7300714d8ccb07d7e2a2458b5b471b239aabd9fc/research/2026-08-25-plugin-development-process-reconstruction.md)).                                                                                                                                                                                  | Those practices need a small, repeatable skill-eval artifact shape shared by both harnesses.   |

The missing layer is therefore behavioral comparison across realistic cases,
not another prose-review rubric. Both products consume Agent Skills: Claude
Code discovers plugin skills under `skills/<name>/SKILL.md` ([Claude Code
plugin docs](https://code.claude.com/docs/en/plugins), accessed 2026-08-26),
and OpenAI describes skills as one authoring format used by ChatGPT and Codex
([OpenAI skill docs](https://developers.openai.com/codex/build-skills), accessed
2026-08-26). The shared skill bytes are portable; invocation controls,
subagent APIs, telemetry, hooks, and plugin manifests are not.

## Candidate findings

### 1. Open Knowledge Format ecosystem map

**Fit and overlap.** The map places OKF producers, validators, visualizers,
catalogs, Obsidian integrations, and publishing tools on maturity and entry-cost
axes. Its only coding-agent row says that space is partially filled; it does
not document shared-skill routing, harness setup, drift detection, or skill
evaluation. Following its links would reopen the forbidden general-ecosystem
survey and cross the map's explicit product boundary.

**Maintenance, testability, and provenance.** The page is a mutable catalog of
community projects. As accessed on 2026-08-26, its table assigns labels such as
“Ready,” “Released,” and “Production” without publishing a test protocol, and
its footer still says OKF v0.1 while the timeline records v0.2. It is useful as
a lead list, not as evidence that a component meets the companion's acceptance
conditions. The site advertises MIT licensing, but the companion should neither
copy the table nor acquire an update obligation for it. Dating and linking the
page is sufficient provenance.

### 2. `okf-open-knowledge-format`

**Fit.** The skill teaches agents to create, enrich, migrate, convert, and
validate OKF knowledge bundles. That is a knowledge product capability, not a
cross-harness distribution or maintenance capability. Its generic Agent Skills
container may load in both target harnesses, but subject-matter portability
does not make the subject part of this companion.

**Overlap and maintenance.** The pinned family contains a 694-line entrypoint,
two copied specifications, examples, conversion guidance, and a regex-based
Bash validator—3,195 lines in total. It also prefers installing a separate
`okflint` tool. Owning this would add three upstreams (the skill, OKF, and the
linter), duplicated specification text, and a Unix-oriented script surface.
The companion already has a deliberate vendored-fork discipline; applying it
to an out-of-scope domain would create maintenance work without closing a
companion gap.

**Testability, licensing, and provenance.** The pinned directory contains no
tests or eval cases. The Bash validator provides a runnable seam, but its
frontmatter parsing is regex-based and cannot establish full YAML conformance.
The source repository is Apache-2.0 ([pinned
license](https://github.com/fabricioctelles/skills/blob/b10f69fd2402e3d66bbd83f112bfe64788bc82b2/LICENSE));
copying would require the license, retained notices, and prominent modification
notices. Legal reusability does not overcome the scope and upkeep costs.

### 3. Agent Skills evaluation guidance

**Bounded adopted surface.** The official page supplies the exact missing
behavioral layer ([accessed 2026-08-26](https://agentskills.io/skill-creation/evaluating-skills)):

1. Begin with two or three realistic cases, including varied phrasing and a
   boundary case.
2. Run each case in a clean context both with the candidate skill and without
   it; use the previous skill version instead of no skill for regression work.
3. Preserve outputs plus timing and token data per arm.
4. Add observable assertions after seeing first-round output. Use deterministic
   scripts for mechanical assertions and require evidence for every pass.
5. Compare outputs blindly for holistic qualities, aggregate pass-rate and
   cost deltas, inspect outliers and nondiscriminating assertions, and record
   human feedback before the next iteration.

This surface composes with the installed layers: Superpowers supplies
failure-first cases, the repository supplies deterministic invariants, and the
official loop supplies paired artifacts and aggregation. It should replace
none of them.

**Portability and ownership.** The case schema and paired method are
client-neutral. The runner is not: Claude Code and Codex expose different
subagent and telemetry surfaces. The companion must run the same case IDs and
assertions independently in each supported harness, preserve harness/model
identity with every result, and never use a pass in one product as evidence for
the other. Results use the repository's four states: `MATCHED`, `UNMATCHED`,
`UNREACHABLE`, and `SKIPPED` ([governing
ADR](https://github.com/eranroseman/knowledge-harness/blob/7300714d8ccb07d7e2a2458b5b471b239aabd9fc/docs/adr/0002-verification-records-tell-the-truth.md)).
A missing token or duration metric is `UNREACHABLE`, not zero.

**Licensing and updates.** Agent Skills repository code/specification is
Apache-2.0 and its documentation is CC BY 4.0 ([pinned license
statement](https://github.com/agentskills/agentskills/blob/69ef37e9424c0a7ea9dd2293b559e43ec8176379/README.md#license)). The companion
should cite the maintained page and store its own small case/result schema,
not copy the guide. Re-read the page when the Agent Skills specification or
either supported harness changes its skills runtime.

### 4. Anthropic's improved `skill-creator`

**Bounded reusable surface.** The announcement distinguishes capability-uplift
skills from encoded-preference skills. That distinction changes what a useful
baseline means: a capability skill must beat the no-skill agent, while a
preference skill must reproduce the intended workflow. It also names two
maintenance triggers that matter here: model/runtime updates can regress a
skill or make a capability skill unnecessary, and description changes need a
separate false-positive/false-negative trigger set. The post reports clean
parallel agents, token/time benchmarks, and blind comparators, but those
mechanics are already owned by the adopted official evaluation guide
([Anthropic post](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills),
accessed 2026-08-26).

**Required translation and update responsibility.** Do not import Anthropic's
Claude-specific plugin or result plumbing as the companion's sole evaluator.
The companion maintainer owns a two-adapter translation:

- record `capability-uplift` or `encoded-preference` in each skill's evaluation
  metadata;
- keep positive and adjacent-negative trigger cases separate from output
  assertions;
- rerun the relevant cases after a supported model or harness upgrade; and
- retire a capability instruction only when paired no-skill runs erase its
  measured advantage in both harnesses.

The blog is a dated, copyrighted product announcement, not code to vendor.
Paraphrase and cite it. If implementation is later borrowed from Anthropic's
open `skill-creator`, pin that repository separately and review its own license
at the selected commit.

### 5. `skill-evaluation`

**Overlap.** The skill scores 18 criteria across Trigger, Structure, Steering,
and Pruning, then reduces them to a weighted 0–100 grade. Useful concepts such
as realistic trigger cases, evidence-cited findings, deletion tests, and
progressive disclosure already exist in the installed Codex creator,
Superpowers' writing skill, or the official Agent Skills guidance. Its
66-line `score.py` only validates triples and computes the authored weights; it
does not validate that the weights or grade boundaries predict better agent
behavior.

**Portability and testability.** Its trigger experiment asks ten subagents to
self-report `SKILLS_USED`. That report is an extra prompt instruction, not a
harness observation, so it can disagree with actual loading. It also assumes
Claude's `disable-model-invocation` field when deciding whether to skip trigger
tests; Codex uses a separate invocation-policy surface. The pinned family has
no tests or eval cases of its own. Shipping it would add a second evaluator
whose scalar grade can conflict with the adopted paired behavioral evidence.

**Maintenance, licensing, and provenance.** The 751-line family is
Apache-2.0 under the pinned repository license. It is legally adaptable, but
the companion would own the rubric, weights, category table, templates,
trigger harness, and their calibration. No unique mechanism justifies that
surface. Preserve the pinned link as negative knowledge so this review is not
repeated.

### 6. `agent-plugin-eval`

**Potential value.** The candidate has a useful static-audit shape: resolve one
plugin root, inventory files and symlinks, avoid executing untrusted package
code, check path containment and suspected credentials, validate Agent Skills
and MCP entries, and separate normative conformance from subjective quality.
Its 415-line scanner and 101-line calculator are small enough to test if their
governing format becomes a companion target.

**Why the trigger has not fired.** The candidate treats Agent Plugins 1.0's
root `plugin.json` as authoritative. The published format's portable core is
Agent Skills plus MCP servers; client-specific hooks, agents, distribution,
and permissions remain outside that core ([Agent Plugins 1.0
specification](https://agent-plugins.org/specification), accessed 2026-08-26).
The official compatible-client list names ChatGPT/Codex but not Claude Code
([compatible clients](https://agent-plugins.org/compatible-clients), accessed
2026-08-26). Claude Code instead documents `.claude-plugin/plugin.json` plus
native skills, agents, hooks, MCP, LSP, and marketplace surfaces. Therefore a
clean result from this auditor cannot establish the destination's required
dual-harness behavior, and adopting its root-manifest premise now would make a
design-gate choice by indirection.

**Obligations if reopened.** If the named trigger fires, evaluate a bounded
adaptation of the static inventory and containment scanner, not the subjective
score. The companion owner must pin both the Agent Plugins release and the
candidate commit; add fixtures for valid/invalid root manifests, both native
harness manifests, symlink escapes, malformed skills, and suspected secrets;
cross-check against each harness's native validator; and preserve Apache-2.0
license and modification notices. The pinned candidate family itself contains
no automated tests, so its scripts are evidence leads until those fixtures
discriminate them.

## Constraints for the design specification

These findings leave the design gate choices open while fixing five acceptance
constraints:

1. **One owned protocol.** Structural validation, behavioral comparison, and
   package validation may have separate deterministic instruments, but one
   evaluation protocol owns case IDs, result states, evidence, and update
   triggers. Do not ship competing quality grades.
2. **Same cases, separate harness results.** Every shared skill's required and
   adjacent-negative cases run in Claude Code and Codex. Record harness,
   version, model, skill commit, case ID, arm, assertions, artifacts, tokens,
   duration, and four-state outcome.
3. **Paired discrimination.** A behavioral claim needs a with-skill versus
   no-skill/previous-version delta. Mechanical assertions use scripts; judgment
   assertions preserve cited evidence and human feedback. A suite that both
   arms always pass is nondiscriminating and must be repaired or removed.
4. **Upgrade is an evidence event.** Supported model, harness, or upstream-skill
   upgrades rerun the affected cases before compatibility is claimed. Adapted
   assets retain upstream URL, commit, license, local change record, and named
   update owner.
5. **Keep product knowledge out.** OKF and other vault/content skills do not
   enter the companion merely because their container format is portable.

## Uncertainties and limits

- No live candidate evaluation ran. This ticket asked for source assessment,
  prohibited installation/implementation, and supplied no stable cross-harness
  telemetry API. The note distinguishes runnable seams from tested behavior.
- Dynamic documentation may change after 2026-08-26. In particular, Agent
  Plugins 1.1 is already a working draft while 1.0 is published, and Claude
  Code could later join its compatible-client list. The named reopen trigger
  prevents that uncertainty from becoming ambient upkeep.
- The OKF ecosystem map's maturity labels were assessed as claims made by the
  map. Verifying every linked project's status would violate this ticket's
  explicit ban on a general ecosystem survey.
- The third-party repository's absence of per-candidate tests means this note
  does not infer defect-free scripts from readable source. Any later reuse
  starts with discriminating fixtures, not trust in the scorecard.

## Source ledger

| Source                                                                                                                                           | Fixity                                                                                                   | Use                                                                                |
| ------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| [`fabricioctelles/skills`](https://github.com/fabricioctelles/skills/tree/b10f69fd2402e3d66bbd83f112bfe64788bc82b2)                              | Commit `b10f69fd2402e3d66bbd83f112bfe64788bc82b2`                                                        | Candidate bytes, directory inventories, scripts, and Apache-2.0 license            |
| [OKF ecosystem map](https://okf.md/ecosystem-map/)                                                                                               | Accessed 2026-08-26                                                                                      | Map contents, stated maturity labels, timeline, and footer                         |
| [Agent Skills evaluation guide](https://agentskills.io/skill-creation/evaluating-skills)                                                         | Accessed 2026-08-26                                                                                      | Paired evaluation method and artifact schema                                       |
| [Anthropic skill-creator announcement](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills)                     | Published 2026-03-03; accessed 2026-08-26                                                                | Skill-type distinction, regression rationale, trigger tuning, and benchmark claims |
| [Agent Skills repository](https://github.com/agentskills/agentskills/tree/69ef37e9424c0a7ea9dd2293b559e43ec8176379)                              | Commit `69ef37e9424c0a7ea9dd2293b559e43ec8176379`                                                        | Format ownership and documentation/code licensing                                  |
| [Agent Plugins specification](https://agent-plugins.org/specification) and [client matrix](https://agent-plugins.org/compatible-clients)         | Version 1.0 published; accessed 2026-08-26                                                               | Portable plugin boundary and current client coverage                               |
| [Claude Code plugin docs](https://code.claude.com/docs/en/plugins) and [OpenAI skill docs](https://developers.openai.com/codex/build-skills)     | Accessed 2026-08-26                                                                                      | Native-package differences and shared Agent Skills support                         |
| [`knowledge-harness`](https://github.com/eranroseman/knowledge-harness/tree/7300714d8ccb07d7e2a2458b5b471b239aabd9fc)                            | Commit `7300714d8ccb07d7e2a2458b5b471b239aabd9fc`                                                        | Existing contract tests, provenance discipline, and companion boundary             |
| [Superpowers `writing-skills`](https://github.com/obra/superpowers/blob/44c9b2d6e889982ac18c27d05a19fefe335194e1/skills/writing-skills/SKILL.md) | Commit `44c9b2d6e889982ac18c27d05a19fefe335194e1`                                                        | Existing failure-first skill-testing machinery                                     |
| Installed Codex `skill-creator` system bundle                                                                                                    | Accessed 2026-08-26; manifest SHA-256 `5714dd6fb6c5c22c7b72dd29e6600a851d233318ecaecfe061ed7a4e662dda81` | Existing structural skill-creation and validation machinery                        |
