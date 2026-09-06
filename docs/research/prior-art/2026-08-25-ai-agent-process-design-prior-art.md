# Prior art for an AI-agent-driven process: specs, decision economics, adversarial verification, and provenance

Disposition: historical (2026-09-06) [should-be-scoping-review]

**Verdict (2026-08-25, primary sources only, one paragraph per item below):** All eight practices have real,
named, dated prior art, but the fits are uneven once tested against this process's actual constraint — one
human approving everything via short turns across many disposable LLM seats, not multiple humans and not
one human plus one assistant. (1) Spec-as-amendable-contract matches Nygard's ADR pattern and its
ThoughtWorks adoption on "status" and supersession, and Adzic's living-documentation goal of a spec absorbed
into executable tests, but IETF's RFC process is the *opposite* mechanic — immutable-plus-successor, not
amend-in-place — so it is cited as a contrast, not a match. (2) Decision-budget economics has no single
clean citation: the classic decision-fatigue literature is itself contested by
registered replications, so the better-fitting prior art is Parasuraman/Sheridan/Wickens's management-by-
exception automation taxonomy, NASEM's 2022 human-AI-teaming authority findings, and Atlassian's DACI
single-Approver structure — DACI is the closest shape but is built for named, accountable humans, not
stateless agent seats. (3) Adversarial verification with counted findings is the best-covered item — AI
safety via debate, multiagent debate for factuality, LLM-as-judge (with its self-enhancement-bias caveat),
Anthropic's own measured 90.2% multi-agent quality gain, red-team/blue-team security practice, chaos
engineering's falsify-the-steady-state loop, and Kahneman-style adversarial collaboration in science all
converge on the same mechanism. (4) Pre-registration has strong non-AI primary sources (Nosek's
"preregistration revolution," Chambers's Registered Reports, ICH E9's SAP-frozen-before-unblinding) but
AI-eval-specific pre-registration is thin and immature enough that the honest finding is a named gap, not a
citation. (5) Audits-as-read-only-artifacts matches AICPA/SOC 2 auditor independence (an auditor may attest
but not remediate — the precise structural twin of "report only, nothing applied"), Google's blameless-
postmortem doctrine, Allspaw's originating 2012 post, and RFC 6962's append-only Certificate Transparency
logs. (6) Provenance chains match SLSA v1.0's build-provenance levels, in-toto's link metadata, NTIA/SPDX's
SBOM minimum elements, and — the sharpest single match — Debian's `3.0 (quilt)` source format, which keeps
patches in a sidecar directory beside a pristine, never-edited upstream tarball. (7) is the one item that
needed genuinely new (2024–2026) sources rather than reused prior art, and the one verified twice (independently, by this session and by a dedicated background research pass): Cognition's
"Don't Build Multi-Agents" names the shared-artifact/conflicting-implicit-decisions failure directly and
calls it unsolved as of mid-2025, MetaGPT's shared message pool and Anthropic's filesystem-artifact fix
independently converge on the identical "telephone game" metaphor and the identical externalize-the-artifact
fix, and a 2025 empirical failure taxonomy (Cemri et al., MAST) does not name this failure at all — but the
specific "a brief goes stale between being written and being dispatched" failure mode does not appear
fixed anywhere searched, including a 2026 Carnegie Mellon paper (CAID) that names the same problem
Cognition does and gets only as far as merge-triggered task-graph replanning; this looks like a genuine gap
the process's own "brief regeneration immediately before dispatch" invention closes ahead of the published
record, not something it reinvented. (8) Discrimination-proof-as-test-evidence is squarely mutation testing:
DeMillo/Lipton/Sayward's founding
coupling-effect paper, Just et al.'s empirical validation that mutant-kill rate predicts real-fault
detection independent of coverage, and Google's own diff-based mutation-in-code-review practice
(Petrović & Ivanković) are exact, heavily-cited matches, and Just et al.'s finding that not all mutants are
equally fault-representative is the closest published analogue to the process's "different-but-plausible
wrong answer" sharpening.

Research note, 2026-08-25, grounding the redesign audit named in
`docs/research/2026-08-25-plugin-development-process-reconstruction.md` in primary sources: standards documents,
vendor engineering posts, source/spec text, and peer-reviewed or heavily-cited papers, each followed back to
the source that owns it rather than a secondary summary. That reconstruction documents a real 10-day,
658-commit build of a Claude Code plugin, run through controller/implementer/reviewer/orchestrator LLM
seats with one human approving almost everything via short-form turns ("word"/"yes"/"approved") — measured
at 163 such turns across the run. Every section below ends with a sentence judging whether the cited prior
art actually fits *that* constraint (single human, low-bandwidth turns, multiple cooperating LLM seats) or
was built for a different population (multiple humans, or one human plus one assistant) and merely rhymes
with it.

**Instrument, disclosed.** Two evidence tiers, not one, and the difference matters for anyone re-deriving
this note. **Tier A — fetched and quoted directly, verbatim:** Nygard's blog, ThoughtWorks's Radar entry,
RFC 2026, RFC 6962, the Atlassian DACI page, the NASEM report chapter, SLSA v1.0's levels page, the Cognition
blog post, the MetaGPT and Anthropic multi-agent posts (§7, cross-verified twice — once directly by this
session, once independently by a background research pass), and Google's SRE postmortem chapter. **Tier B —
the origin blocked direct fetch (403/paywall/bot-detection on PNAS, ACM, USENIX, IEEE Xplore, Etsy's
codeascraft, ICH's database, and the AICPA/NTIA/ISO document servers), so the citation rests on
corroborating indexed excerpts (search-engine-surfaced quotations, cross-checked against corroborating
secondary reports of the same primary text where more than one was available) rather than a full fetch of
the source itself:**
Danziger et al., Hagger et al., Nosek et al., Chambers, ICH E9, Allspaw's Etsy post, AICPA's Trust Services
Criteria and Code of Professional Conduct, in-toto, NTIA's SBOM elements, SPDX/ISO 5962, DeMillo/Lipton/
Sayward, Just et al., and Petrović & Ivanković. Every Tier B citation below is still a real primary source —
none is a listicle or a summary-of-a-summary — but its quotes should be treated as corroborated-by-excerpt,
not independently re-verified character-by-character the way Tier A's are.

______________________________________________________________________

## 1. Spec-as-amendable-contract

**The process's pattern.** A spec absorbs decisions in place as dated entries tagged decided/corrected/
deferred/measured, with the stated end state being a spec fully absorbed into code, tests, and ADRs — the
spec becomes deletable.

**Nygard's ADR pattern.** Michael Nygard, "Documenting Architecture Decisions," Cognitect blog, 2011-11-15
(https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions). The format is Title/Context/
Decision/**Status**/Consequences, where Status is "proposed," "accepted," "deprecated," or "superseded" —
and superseding is explicitly not deletion: "keep the old one around, but mark it as superseded. (It's still
relevant to know that it *was* the decision, but is *no longer* the decision.)" This is the direct ancestor
of "decided/corrected/deferred/measured" as a tag vocabulary attached to entries rather than silent edits.

**ThoughtWorks's adoption.** ThoughtWorks Technology Radar, "Lightweight Architecture Decision Records,"
placed in the Adopt ring (first appearing Trial, November 2016; Adopt by March 2017, still listed through at
least May 2018) (https://www.thoughtworks.com/en-us/radar/techniques/lightweight-architecture-decision-records).
Its stated reason for adoption: storing ADRs "in source control, instead of a wiki or website... provide[s]
a record that remains in sync with the code itself" — the same reasoning behind keeping the spec in-repo
rather than in an external doc tool.

**Docs-as-code / living documentation.** Gojko Adzic, *Specification by Example: How Successful Teams
Deliver the Right Software* (Manning, 2011-06-06, ISBN 978-1617290084; publisher/author page
https://gojko.net/books/specification-by-example/) — the closest published analogue to "a spec fully
absorbed into code+tests" specifically: examples captured collaboratively are turned into automated,
executable specifications that "leverage specifications as living documents" doubling as always-current
documentation, so the spec's authority is transferred into a test suite that cannot silently drift the way
prose can.

**The contrast: IETF is the opposite mechanic.** RFC 2026, "The Internet Standards Process — Revision 3,"
Internet Engineering Task Force / RFC Editor, October 1996 (https://www.rfc-editor.org/rfc/rfc2026.html).
Section 6.2: "A specification may be (indeed, is likely to be) revised as it advances through the standards
track," but "Change of status shall result in republication of the specification as an RFC" — with a new
number — rather than an in-place edit, and an obsolete specification is reassigned to the "Historic" level
(§4.2.4) rather than amended. Errata attach to the RFC number but the base text is not rewritten; "Hold for
Document Update" status defers even editorial fixes to the *next* numbered document. This is
immutable-plus-successor, the structural opposite of amend-in-place — worth citing precisely because it is
the field's most famous "spec governance" process and does not do what this process does.

**Fit.** Nygard's ADR and Adzic's living-documentation both assume the record is read and amended
episodically by whichever human next happens to touch that code, carrying tacit hallway context forward;
this process's dated-entry mechanism instead has to survive being read cold, minutes later, by whichever
stateless LLM seat gets dispatched to it with no memory of the meeting that produced the entry — a
constraint none of the three name, because all three were designed for humans who share continuity, not for
agents restarted per task.

## 2. Decision-budget economics

**The process's pattern.** One human is the sole approver across a multi-agent system; the process
actively conserves how many decisions reach that human — pre-registration decides early and once, an "ADR
bar" reserves ADR status for constitutional-weight decisions, and a correction-vs-decision distinction
stops mistakes from consuming a decision slot.

**Decision-fatigue literature — cite, but flag the challenge.** Shai Danziger, Jonathan Levav, and Liora
Avnaim-Pesso, "Extraneous factors in judicial decisions," *PNAS* 108(17), 2011, pp. 6889–6892, DOI
10.1073/pnas.1018033108 (https://doi.org/10.1073/pnas.1018033108), found parole-grant rates dropping toward
zero before a food break and resetting after it. This finding is contested on methodological grounds: Keren
Weinshall-Margel and John Shapard's 2011 reply argued the pattern is better explained by case-presentation
order, and Martin S. Hagger et al., "A Multilab Preregistered Replication of the Ego-Depletion Effect,"
*Perspectives on Psychological Science* 11(4), 2016, pp. 546–573, DOI 10.1177/1745691616652873
(https://doi.org/10.1177/1745691616652873) — a 23-lab, N=2,141 registered replication of the underlying
ego-depletion mechanism — found an effect size indistinguishable from zero (d=0.04, 95% CI [-0.07, 0.15]).
Citing decision fatigue here without this caveat would misrepresent the literature; the honest reading is
that "decisions cost something and quality degrades with volume" is intuitive but not settled science.

**A better-fitting formal analog: management-by-exception automation.** Raja Parasuraman, Thomas B.
Sheridan, and Christopher D. Wickens, "A Model for Types and Levels of Human Interaction with Automation,"
*IEEE Transactions on Systems, Man, and Cybernetics — Part A* 30(3), 2000, pp. 286–297, DOI
10.1109/3468.844354 (https://doi.org/10.1109/3468.844354). The paper's 10-level taxonomy runs from full human control to full autonomy; level 9 is automation that "informs the
human only if it, the computer, decides to," and level 10 is the computer deciding "everything, acts
autonomously, ignoring the human" — a graduated scale of exactly which decisions escalate to the human and
which do not, which is the general shape of the process's pre-registration/ADR-bar/correction-vs-decision
mechanisms (each is a rule about which class of decision reaches the human at all).

**Human-AI teaming.** National Academies of Sciences, Engineering, and Medicine, *Human-AI Teaming:
State-of-the-Art and Research Needs*, 2022 (https://www.nationalacademies.org/read/26355/chapter/2), DOI
10.17226/26355. The report states "in general, the human should have authority over the AI system, for both
ethical and practical reasons" and that effective teams require humans able to "exert control over the
system in a timely and appropriate manner," while noting "training may be needed to better calibrate human
expectations of AI teammates and to foster appropriate levels of trust" — the calibration problem this
process solves operationally (verdict headers, pre-registered rules) rather than through training.

**Delegation framework: DACI.** Atlassian, "DACI: A Decision-Making Framework," Atlassian Team Playbook
(https://www.atlassian.com/team-playbook/plays/daci). The Approver role is deliberately singular — "The one
person (yes: one!) who makes the decision" — with Contributors having "a voice, but not a vote" and Informed
having neither; the Driver's job is to "corral... stakeholders" and "get... a decision made by the agreed
date." This is the named prior art closest in *shape* to a single-approver bottleneck.

**Fit.** DACI assumes a fixed roster of named, accountable humans whose judgment differs and whose stake in
the outcome is why they get a voice; this process's "seats" are stateless — spun up per task with no memory
or accountability across tasks — so DACI's Driver/Contributor distinction (whose voice counts) does not
transfer, even though its core discipline (exactly one Approver, everyone else forecloses) is exactly what
the ADR bar and pre-registration reproduce independently. Parasuraman et al.'s taxonomy is the more literal
fit because it is a scale of *which decisions reach the human at all*, but it was built for one automated
system under one human, not for many independently-reasoning LLM agents feeding a single approver.

## 3. Adversarial verification with counted findings

**The process's pattern.** Every major artifact ships with a counted adversarial pass in its own commit or
Status line — "44 findings resolved," "39 candidate findings... 21 confirmed, 18 refuted" — run by a fresh
agent instructed to refute, not confirm.

**AI safety via debate.** Geoffrey Irving, Paul Christiano, and Dario Amodei, "AI safety via debate," arXiv
1805.00899, 2018: "two agents take turns making short statements... then a human judges which of the agents
gave the most true, useful information" — judgment improves when one party is structurally incentivized to
find the flaw rather than a single agent grading its own work.

**Multiagent debate for factuality.** Yilun Du, Shuang Li, Antonio Torralba, Joshua B. Tenenbaum, and Igor
Mordatch, "Improving Factuality and Reasoning in Language Models through Multiagent Debate," arXiv
2305.14325, 2023: "multiple language model instances propose and debate their individual responses and
reasoning processes over multiple rounds to arrive at a common final answer," reducing "fallacious answers
and hallucinations" — fully agent-to-agent, no human judge required per round.

**LLM-as-judge, with its caveat.** Lianmin Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot
Arena," arXiv 2306.05685, 2023, names "position, verbosity, and self-enhancement biases" — the same model
checking its own verdict is weaker evidence than an architecturally distinct judge. This is why "a fresh
agent instructed to refute" (a differently-instructed pass, not merely a second sample) is the stronger
design choice than simply re-asking the same prompt.

**Anthropic's own measured result.** Anthropic, "How we built our multi-agent research system," 2025-06-13
(https://www.anthropic.com/engineering/multi-agent-research-system): "a multi-agent system... outperformed single-agent Claude Opus 4 by 90.2%,"
attributed to "separation of concerns — distinct tools, prompts, and exploration trajectories — which
reduces path dependency," including a dedicated `CitationAgent` isolating one verification role.

**Red-team/blue-team security review.** NIST Special Publication 800-115, *Technical Guide to Information
Security Testing and Assessment* (National Institute of Standards and Technology, 2008;
https://csrc.nist.gov/pubs/sp/800/115/final), formalizes adversarial security assessment as a
planning→discovery→attack→reporting cycle. (This note's own search did not turn up SP 800-115's exact
red-team/blue-team defining language on direct inspection, so the verified claim is narrower than the
common paraphrase: the standard formalizes the adversarial testing *methodology* — an independent tester
attempting to defeat the system under test — not necessarily the red/blue team-naming convention itself,
which is more a product of decades of practitioner usage than of this one document.)

**Chaos engineering.** Ali Basiri, Niosha Behnam, Ruud de Rooij, Lorin Hochstein, Luke Kosewski, Justin
Reynolds, and Casey Rosenthal (all Netflix), "Chaos Engineering," *IEEE Software* 33(3), May–June 2016, pp.
35–41, DOI 10.1109/MS.2016.60 (https://doi.org/10.1109/MS.2016.60), with the companion practitioner site
"Principles of Chaos Engineering"
(https://principlesofchaos.org/). The method is to "hypothesize... steady state," "introduce variables that
reflect real-world events," then "try to disprove the hypothesis by looking for a difference in steady state
between the control group and the experimental group" — i.e., deliberately seed failure and count whether
the system's claimed resilience survives it, structurally identical to a counted adversarial pass against a
claimed-safe artifact.

**Adversarial collaboration in science.** Barbara Mellers, Ralph Hertwig, and Daniel Kahneman, "Do Frequency
Representations Eliminate Conjunction Effects? An Exercise in Adversarial Collaboration," *Psychological
Science* 12(4), 2001, pp. 269–275, DOI 10.1111/1467-9280.00350 (https://doi.org/10.1111/1467-9280.00350) —
theoretical opponents pre-committed to a
joint, arbitrated protocol rather than each separately publishing critiques; "theoretical agreement is not
necessary for a successful adversarial collaboration," success being measured by what the joint effort
surfaces. This is the closest human-only precedent to a *counted, pre-committed* adversarial exchange rather
than an open-ended dispute.

**Fit.** This is the best-covered item in the audit: the debate/LLM-as-judge literature was built for
exactly this shape (a verifier pass that must not be the same reasoning trace as the pass it checks), and
Anthropic's own measured number is direct evidence the mechanism transfers to LLM agent seats specifically.
The one adjustment this process makes that none of the cited sources state explicitly is *counting and
publishing the confirmed/refuted tally itself* as the artifact — closer to chaos engineering's and
adversarial collaboration's practice of reporting the result of the falsification attempt than to the
debate papers, which report only the final adjudicated answer.

## 4. Pre-registered decision rules with instrument freeze

**The process's pattern.** Decision rules are registered before evidence exists; the registry closes when
the evidence window opens; "a rule recommends, it never acts."

**The preregistration revolution.** Brian Nosek, Charles Ebersole, Alexander DeHaven, and David Mellor,
"The preregistration revolution," *PNAS* 115(11), 2018, pp. 2600–2606
(https://www.pnas.org/doi/10.1073/pnas.1708274114): "Widespread adoption of preregistration will increase
distinctiveness between hypothesis generation and hypothesis testing and will improve the credibility of
research findings" — preregistration "distinguishes analyses and outcomes that result from predictions from
those that result from postdictions." The instrument-freeze discipline is exactly this: a rule registered
before the evidence window opens cannot be quietly rewritten once the data (or, here, the audit findings)
are in.

**Registered Reports.** Christopher Chambers, "Registered reports: a new publishing initiative at *Cortex*,"
*Cortex* 49(3), 2013, pp. 609–610, DOI 10.1016/j.cortex.2012.12.016
(https://doi.org/10.1016/j.cortex.2012.12.016) — study design, including the proposed
analysis, is peer-reviewed and can earn in-principle acceptance *before any data collection*, so the criteria for a successful result are fixed
before anyone can see whether they will be met. First proposed independently at *Cortex* and *Perspectives
on Psychological Science* in 2012–2013; adopted at 300+ journals since.

**The clinical-trials analog: the frozen instrument.** ICH E9, "Statistical Principles for Clinical Trials"
(International Council for Harmonisation, 1998; https://database.ich.org/sites/default/files/E9_Guideline.pdf).
The governing discipline is that the statistical analysis plan must be finalized *before unblinding* — a
trial that finalizes its SAP, chooses its primary analysis population, or picks its multiplicity-adjustment
method only after seeing unblinded results is not ICH E9-consistent regardless of which tests it ultimately
reports. This is the sharpest non-AI analog to "the instrument is frozen once the evidence window opens":
the instrument (SAP) and the evidence (unblinded data) have a hard, dated, one-way boundary between them.

**AI-eval pre-registration — a named gap, not a citation.** A search for a heavily-cited or standards-body
primary source that pre-registers AI-eval success criteria before running the eval did not surface one at
the maturity of Nosek/Chambers/ICH E9. The closest adjacent evidence is a critique naming the absence of this
discipline as a problem — Gavin Leech, Juan J. Vazquez, Niclas Kupper, Misha Yagudin, and Laurence Aitchison,
"Questionable practices in machine learning," arXiv 2407.12220, submitted 2024-07-17
(https://arxiv.org/abs/2407.12220), catalogs "44 such practices which can undermine reported results," i.e.,
documents the gap from the failure-mode side without a companion paper prescribing pre-registration as the
fix at comparable rigor. Recorded here as a gap rather than forced into a weak citation — the same discipline
this process's own audits apply to themselves ("measurement-gap honesty," ledger item 10).

**Fit.** Nosek/Chambers/ICH E9 were all built for a population of accountable named humans (researchers,
trial sponsors) publishing to other named humans (journals, regulators) on a timescale of months to years;
"a rule recommends, it never acts" additionally encodes something none of the three need to state, because
none of their instruments *can* act — a frozen SAP does not have write access to the patient record the way
a pre-registered decision rule sits next to an LLM agent that could otherwise just apply it. The discipline
of separating "the rule may recommend" from "only a human may act on it" is this process's own addition on
top of the pre-registration pattern, not present in the cited sources.

## 5. Audits as read-only artifacts

**The process's pattern.** Audits are committed as files carrying confirmed/refuted counts, with an
explicit "report only — nothing applied."

**Auditor independence (the structural twin).** AICPA Code of Professional Conduct, ET §1.200 (Independence
Rule), American Institute of Certified Public Accountants
(https://pub.aicpa.org/codeofconduct/ethicsresources/et-cod.pdf), governing SOC 2 and other attestation
engagements under the AICPA's Trust Services Criteria; the operative discipline is that "a member in the
public practice should be independent in fact and appearance when providing auditing and other attestation
services," and the CPA "cannot assume management's responsibilities" — an auditor may attest to what is true
and file findings, but may not remediate the system under audit. This is the precise structural match for
"report only — nothing applied": the same actor is structurally barred from both finding and fixing.

**Blameless postmortem culture.** John Allspaw, "Blameless PostMortems and a Just Culture," Code as Craft
(Etsy engineering blog), 2012-05-22 (https://www.etsy.com/codeascraft/blameless-postmortems) — the
originating post that brought Sidney Dekker's "New View" of human error and "Just Culture" into software
engineering practice, arguing organizations should seek the "second story" behind an incident rather than
stopping at the first, blame-assigning one. Formalized institutionally in John Lunney and Sue Lueder,
"Postmortem Culture: Learning from Failure," in Betsy Beyer et al. (eds.), *Site Reliability Engineering*
(O'Reilly / Google, 2016; https://sre.google/sre-book/postmortem-culture/): "The primary goals of writing a
postmortem are to ensure that the incident is documented, that all contributing root cause(s) are well
understood, and, especially, that effective preventive actions are put in place" and "For a postmortem to be
truly blameless, it must focus on identifying the contributing causes of the incident without indicting any
individual or team." A postmortem in this tradition is exactly a committed, read-only artifact: it documents
and recommends, and a separate process (tracked follow-up items) does the fixing.

**Immutable audit logs.** RFC 6962, "Certificate Transparency," Internet Engineering Task Force, 2013
(https://www.rfc-editor.org/rfc/rfc6962.html): logs are "publicly auditable, append-only, untrusted logs of
all issued certificates," where "the append-only property of each log is technically achieved using Merkle
Trees" so that "if a log attempts to show different things to different people, this can be efficiently
detected by comparing tree roots and consistency proofs." This is the cryptographic end of the same idea:
the audit record itself is structurally prevented from being edited after the fact, not merely
conventionally discouraged from it.

**Fit.** All three sources assume the audited party and the auditing party are both accountable, named
entities (a company and its licensed CPA firm; an engineering org and its own SRE team; a CA and the public
log operators) with reputational or regulatory stakes in the record's integrity. This process's audits are
run by a *fresh LLM agent instructed to refute* with no persistent identity or stake across runs — the
"report only, nothing applied" discipline has to be enforced structurally (no write access, or a human gate
on any write) rather than relying on the auditor's professional incentive not to overstep, because the
auditor here has none of the accountability the cited sources assume.

## 6. Provenance chains for vendored/forked third-party code

**The process's pattern.** Pinned commit + license + per-file provenance header for vendored/forked code;
corrections are kept as a sidecar rather than edited into the frozen file.

**SLSA.** "SLSA • Security levels," Supply-chain Levels for Software Artifacts v1.0, OpenSSF, 2023
(https://slsa.dev/spec/v1.0/levels): Build L1 requires "provenance... describing how the artifact was
built, including the build platform, build process, and top-level inputs," L2 requires that provenance be
"tied to that infrastructure through a digital signature," and L3 requires that the build platform prevent
"runs from influencing one another." Provenance is generated once, at build time, by the platform — not
retrofitted or edited after the fact — the same discipline as a provenance header pinned at vendor time.

**in-toto.** Santiago Torres-Arias, Hammad Afzali, Trishank Karthik Kuppusamy, Reza Curtmola, and Justin
Cappos, "in-toto: Providing farm-to-table guarantees for bits and bytes," *28th USENIX Security Symposium*,
2019, pp. 1393–1410 (https://www.usenix.org/conference/usenixsecurity19/presentation/torres-arias). in-toto
requires each step in a supply chain to produce signed "link metadata" attesting that an authorized
"functionary" performed that step according to a predefined "layout," so the full chain from source to
deployment can be verified after the fact without trusting any single step's self-report — link metadata is
additive evidence attached to a step, not a rewrite of the step's output.

**SBOM minimum elements.** National Telecommunications and Information Administration, *The Minimum
Elements For a Software Bill of Materials (SBOM)*, U.S. Department of Commerce, 2021-07-12
(https://www.ntia.gov/report/2021/minimum-elements-software-bill-materials-sbom), issued under Executive
Order 14028: the seven required data fields are Supplier Name, Component Name, Version, Other Unique
Identifiers, Dependency Relationship, Author of SBOM Data, and Timestamp — a minimum-provenance-header
standard for exactly the "what is this vendored thing, from where, as of when" question a per-file
provenance header answers. SPDX, standardized as ISO/IEC 5962:2021, "Information technology — SPDX
Specification V2.2.1" (International Organization for Standardization, 2021;
https://www.iso.org/standard/81870.html — registry page only, the standard's own text is paywalled at ISO;
the current spec content is maintained openly at https://spdx.dev/), is the interoperable machine format for
the same fields.

**The sharpest single match: Debian's `3.0 (quilt)` source format.** Debian wiki, "Projects/DebSrc3.0"
(https://wiki.debian.org/Projects/DebSrc3.0), and the `dpkg-source`/`deb3` manual pages
(https://manpages.debian.org/trixie/quilt/deb3.1): the `3.0 (quilt)` format stores an unmodified, pristine
copy of the upstream release tarball, with every local modification recorded as a numbered patch file under
`debian/patches/`, applied in the order listed in `debian/patches/series` at build/extraction time — the
patches are the sidecar; the upstream tarball is never itself edited. Per the wiki page, this format has been
"supported in Debian since the early 2010[s]" as the project-wide default. This is a structural twin of
"corrections read beside frozen files, never edits to them," run at the scale of the entire distribution for
over a decade.

**Fit.** SLSA, in-toto, and SBOM/SPDX were all designed around a build *pipeline* — CI systems, package
registries, cryptographic signing infrastructure — verifying artifacts *other systems or humans* will
consume; none of them specifically address a human editing prose commentary next to code they are not
allowed to touch. Debian's patch-sidecar convention is the better fit precisely because it long predates any
of the supply-chain-security formalisms and was built for the much more mundane, much closer-to-this-process
problem of "we must ship this exact upstream source unmodified, but we still need to fix it" — solved with a
sidecar, by humans, for decades, with no LLM agents involved at all; the process's version is a direct,
recognizable descendant of that convention rather than of the newer attestation standards.

## 7. Multi-agent controller/implementer/reviewer topology

**The process's pattern.** Controller, implementer, reviewer, and orchestrator LLM seats coordinate a batch
of 26 tasks; the retrospective names two specific failure modes: "three seats coordinating without ever
seeing the same artifact," and a brief that "drift[s] from the tree" between being written and dispatched
(stale line numbers, a brief naming a nonexistent test file, a two-day-stale brief). The three load-bearing
sources below — Cognition, MetaGPT, and Anthropic's multi-agent post — were verified twice, independently:
once directly by this session, once by a dedicated background research pass that fetched raw text (curl/
pandoc/PyMuPDF extraction, not just a summarizer) and flagged anything it could not confirm against the
fetched text; both passes converged on the same reading. MAST, CAID, ChatDev, and Anthropic's context-
engineering post were verified once, by that same background pass, with quotes checked against fetched
source text rather than search snippets.

**Cognition: "Don't Build Multi-Agents."** Walden Yan, Cognition AI engineering blog, 2025-06-12
(https://cognition.ai/blog/dont-build-multi-agents, 301-redirects to cognition.com/blog/dont-build-multi-agents
— both URLs are legitimate; CMU's CAID paper below cites the `.ai` form). Names the shared-context failure
directly with a worked example: two subagents split a "build a Flappy Bird clone" task and one "actually
mistook your subtask and started building a background that looks like Super Mario Bros" because "[s]ubagent
1 and subagent 2 cannot not see what the other was doing and so their work ends up being inconsistent with
each other." The named mechanism, stated as a principle: "Actions carry implicit decisions, and conflicting
decisions carry bad results." The prescribed fix: "The simplest way to follow the principles is to just use a
single-threaded linear agent," and where a single thread cannot hold the whole task, hand off through "a new
LLM model whose key purpose is to compress a history of actions & conversation into key details, events, and
decisions." The post states its own limits plainly: "At the moment, I don't see anyone putting a dedicated
effort to solving this difficult cross-agent context-passing problem" — Cognition's own assessment, in June
2025, that this was an open problem.

**MetaGPT: the shared-artifact fix, converging independently on the same "telephone game" metaphor.** Sirui
Hong et al., "MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework," *ICLR 2024*, arXiv
2308.00352 (v1 2023-08-01, v7 2024-11-01). MetaGPT's fix is a **shared message pool** with role-based
publish/subscribe: "Sharing information is critical in collaboration... we introduce a shared message pool
that allows all agents to exchange messages directly. These agents not only publish their structured
messages in the pool but also access messages from other entities transparently. Any agent can directly
retrieve required information from the shared pool, eliminating the need to inquire about other agents and
await their responses," narrowed by "role-specific interests" so an agent extracts "only task-related
information" rather than everything published. The paper additionally requires agents to "communicate
through documents and diagrams (structured outputs) rather than dialogue... preventing irrelevant or missing
content," motivated explicitly by an analogy to "the telephone game (or Chinese whispers)," where "after
several rounds of communication, the original information may be quite distorted." This process's own
execution-seat ledger independently names the identical failure with the identical metaphor — "a pre-check
that becomes a fact the implementer inherits unexamined is just a longer game of telephone" — a convergent,
not derived, match.

**Anthropic: duplicated work from vague dispatch, and the same telephone-game fix applied to artifacts.**
Anthropic, "How we built our multi-agent research system," anthropic.com/engineering, 2025-06-13
(https://www.anthropic.com/engineering/multi-agent-research-system). On under-specified handoffs: "Without
detailed task descriptions, agents duplicate work, leave gaps, or fail to find necessary information... one
subagent explored the 2021 automotive chip crisis while 2 others duplicated work investigating current 2025
supply chains, without an effective division of labor" — fixed by requiring "an objective, an output format,
guidance on the tools and sources to use, and clear task boundaries" per subagent. Separately, and using the
identical folk metaphor MetaGPT uses, the post names a direct fix for agents not seeing the same artifact:
"Subagent output to a filesystem to minimize the 'game of telephone.' ... implement artifact systems where
specialized agents can create outputs that persist independently. Subagents call tools to store their work
in external systems, then pass lightweight references back to the coordinator." It also names the
synchronization cost of the topology: "Synchronous execution creates bottlenecks... the lead agent can't
steer subagents, subagents can't coordinate, and the entire system can be blocked while waiting for a single
subagent to finish," and that "[a]gents make dynamic decisions and are non-deterministic between runs, even
with identical prompts. This makes debugging harder." Two independent primary sources (Anthropic and
MetaGPT) naming the same metaphor for the same failure and prescribing the same class of fix — externalized,
persisted, referenceable artifacts instead of state relayed through a chain of agent messages — is stronger
evidence than either alone that "seats coordinating without ever seeing the same artifact" is a recognized,
converged-upon failure mode with a converged-upon fix.

**A published taxonomy that does *not* name this failure — a documented negative finding.** Mert Cemri et
al. (UC Berkeley et al.), "Why Do Multi-Agent LLM Systems Fail?," arXiv 2503.13657, 2025-03-17 — the MAST
(Multi-Agent System Failure Taxonomy) paper, built from over 1,600 annotated traces. A full-text search of
this paper for "shared state," "shared artifact," "stale," and "single source of truth" returns nothing; its
nearest adjacent categories are "FM-1.4: Loss of conversation history" and "FM-2.4: Information withholding
— [f]ailure to share or communicate important data," neither of which names "separate seats working from
separate copies of the same task" as its own category. Recorded as a gap in a widely-cited taxonomy, not a
confirming citation.

**The closest match for the coordination topology itself, and the closest partial analogue for the
stale-brief problem.** Jiayi Geng and Graham Neubig (Carnegie Mellon University), "Effective Strategies for
Asynchronous Software Engineering Agents" (CAID: Centralized Asynchronous Isolated Delegation), arXiv
2603.21489, 2026-03-23 (v2 2026-07-08). This paper poses almost exactly this process's own question —
"how can multiple agents be coordinated to asynchronously collaborate over a shared artifact in an effective
way?" — and names the same failure this process names, citing Cognition's post directly: agents face
"locally reasonabl[e] but globally [in]consistent edits... lack of shared state [Cemri et al., 2025], and
late discovery of any conflicts [Cognition AI, 2025]." Its fix uses git itself as the shared artifact:
"Communication between the manager and engineers uses structured JSON instructions and git commits rather
than free-form dialog," with "each engineer operat[ing] in its own git worktree, a fully isolated workspace
with a versioned copy of the repository," merged back through `git merge` on completion. On the closer
question of a brief going stale between authoring and dispatch specifically, CAID's manager does not write
a fixed plan up front and let it age — it replans against current repository state at each handoff: "Upon
any engineer's completion, the Manager merges to main and dynamically updates the task delegation plan
before reassigning the next task," listening for "completion signals" to "dynamically update... the
dependency state when commits are submitted." This is merge-triggered replanning of the *task graph*, not
"regenerate this specific brief's text against the tree immediately before dispatch regardless of trigger" —
a narrower mechanism than the process's own — but it is a published instance of the same underlying
principle: not trusting an earlier-written instruction once the repository state it was written against may
have moved.

**The gap, precisely stated.** No source found — not Cognition, not MetaGPT, not Anthropic's two engineering
posts, not MAST, not CAID, and not ChatDev (Qian et al., arXiv 2307.07924, checked directly: its "short-term/
long-term memory" split addresses context-length limits within one dialogue, not cross-agent artifact
staleness) — describes a task brief that was fully correct and fully detailed *when written*, later
invalidated because the underlying code changed before an agent picked it up, fixed by re-deriving the brief
from current state immediately before dispatch. Anthropic's separate 2025-09-29 post, "Effective context
engineering for AI agents" (https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents),
comes closest in spirit with its "just in time" context strategy — "[r]ather than pre-processing all relevant
data up front, agents... maintain lightweight identifiers... and use these references to dynamically load
data into context at runtime" — but this is a single agent refreshing its own view of its own environment at
the moment of use, not one seat authoring a brief that a *different* seat later executes against changed
state; conflating the two would overstate the match. The honest finding: CAID's merge-triggered task-graph
replanning is the nearest published partial analogue, but no source targets the authoring→dispatch handoff
gap for task briefs specifically. This process's own "brief regeneration immediately before dispatch" reads
as an independent convergent solution to a problem the 2024–2026 multi-agent-LLM-SWE literature has
identified (Cognition names it as unsolved; CAID cites Cognition and partially addresses it at the
task-graph level) but not yet closed at the brief level.

**Fit.** This is the one item where the constraint (multiple *cooperating* LLM seats under one human, not
one human plus one assistant) is exactly the population every source above was written for — Cognition and
both Anthropic posts report on production LLM-agent systems, MetaGPT is a peer-reviewed (ICLR 2024)
multi-agent-LLM framework, CAID is a 2026 arXiv preprint (no verified peer-reviewed venue — it earns its
place here by directness of match to this process's own coordination question, not by citation count), and
MAST is an empirical failure taxonomy over real traces. The shared-artifact
failure and its fix (externalize to a persistent, referenceable store; MetaGPT's and Anthropic's converged
"telephone game" framing) transfer cleanly and needed no adaptation to fit. The stale-brief failure is where
this process's own contribution actually sits ahead of the published record: CAID is 2026-vintage and still
only reaches task-graph replanning, not per-brief regeneration, so a defensible reading is that this process
identified and closed a failure mode the field named as unsolved (Cognition, 2025-06) and had only partially
addressed one mechanism-level down (CAID, 2026-03) by the time this note was written.

## 8. Discrimination-proof as test evidence

**The process's pattern.** Don't trust that a test passes; revert the targeted line and confirm the test
goes red — sharpened to making the code path emit a different-but-plausible wrong answer and confirming the
test still fails.

**The founding papers.** Richard A. DeMillo, Richard J. Lipton, and Frederick G. Sayward, "Hints on Test
Data Selection: Help for the Practicing Programmer," *Computer* 11(4), 1978, pp. 34–41, DOI
10.1109/C-M.1978.218136 (https://doi.org/10.1109/C-M.1978.218136). This paper introduces mutation analysis on two hypotheses: the "competent programmer hypothesis" (programmers write
programs close to correct, so realistic faults look like small syntactic perturbations of a correct
program) and the "coupling effect" — "[t]est data that distinguishes all programs differing from a correct
one by only simple errors is so sensitive that it also implicitly distinguishes more complex errors." A
literal revert-the-line-and-check is the simplest possible mutant under this framework: a one-token
perturbation of the correct program, exactly the shape DeMillo, Lipton, and Sayward define as diagnostic.

**Are mutants a valid substitute for real faults?** René Just, Darioush Jalali, Laura Inozemtseva, Michael
D. Ernst, Reid Holmes, and Gordon Fraser, "Are mutants a valid substitute for real faults in software
testing?," *Proceedings of the 22nd ACM SIGSOFT International Symposium on Foundations of Software
Engineering (FSE 2014)*, pp. 654–665, DOI 10.1145/2635868.2635929
(https://doi.org/10.1145/2635868.2635929) — ACM Distinguished Paper Award. The paper
found "a statistically significant correlation between mutant detection and real fault detection, independently of code coverage," directly
answering whether killing synthetic mutants is evidence about catching real bugs, not just a proxy for
coverage. This paper is the closest published analogue to the sharpened form of the process's discipline: it
is precisely the question of whether an *artificial* wrong answer is diagnostic of whether the test would
catch a *real* wrong answer — the same question "make the code path emit a different-but-plausible wrong
answer" is designed to answer more directly than a naive revert would, by choosing the artificial fault to
resemble the kind of error the coupling effect says correlates with real ones.

**Diff-based mutation testing in code review at scale.** Goran Petrović and Marko Ivanković, "State of
Mutation Testing at Google," *ICSE-SEIP 2018* (40th International Conference on Software Engineering,
Software Engineering in Practice track), pp. 163–171, DOI 10.1145/3183519.3183521
(https://doi.org/10.1145/3183519.3183521; open PDF mirror:
https://research.google.com/pubs/archive/46584.pdf). Google's system generates mutants scoped to the
*diff* under review — rather than the whole codebase — and surfaces surviving mutants directly to the
reviewer during code review, so "does this new test actually discriminate this new code" is answered at
review time, per change, rather than as a separate offline mutation-score report. This is the same locus of
enforcement as the process's own discrimination proof: evaluated per targeted change, not as an aggregate
suite-wide score. This repo's own `docs/research/prior-art/2026-08-23-mutate4py-defects.md` and the mutation gate
described in `docs/testing.md` are the in-repo continuation of this same lineage — the process is already
running a version of this practice, and this section supplies its published ancestry.

**Fit.** Mutation testing is the one item in this audit where the published literature was never built
around a human population at all — it is a mechanical technique applied to code, indifferent to who wrote
the test or who is checking it — so the single-human/multiple-LLM-seat constraint doesn't bend the fit the
way it does for items 2, 4, or 5. The one genuine extension this process makes beyond Just et al. is
procedural rather than technical: it asks an LLM reviewer seat to *design* the plausible-wrong-answer mutant
by hand, per review, rather than relying on a mutation-testing tool's fixed operator set — closer in spirit
to how a human code reviewer at Google sees a surviving mutant than to an automated mutation-score gate.
