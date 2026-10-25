# Scenario 2 key: material-with-gaps.md

Expected extraction status per design-tree item (the plugin's checklist IDs). "Settled" items must not be asked in any round; every "weak" or "missing" item must appear in the extraction table as weak or missing.

| Item | Expected | Why                                                                                                                                       |
| ---- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| 1.1  | settled  | one-sentence question with the two levels named                                                                                           |
| 1.2  | settled  | the standing protocol, the committee and its turnaround are named                                                                         |
| 1.3  | weak     | reason and access given; retention explicitly undecided                                                                                   |
| 2.2  | missing  | no session estimate, no condition count                                                                                                   |
| 2.3  | settled  | pilot: three people, refines the phrase count, data not reported                                                                          |
| 2.4  | missing  | no timeline                                                                                                                               |
| 2.5  | missing  | no expected challenges                                                                                                                    |
| 6.1  | settled  | two hypotheses with direction and a research question for the rating                                                                      |
| 6.2  | weak     | H1's direction has a reason but "sources to be added"; H2 cites nothing                                                                   |
| 6.5  | settled  | the material says no interaction is expected, with the reason                                                                             |
| 7.1  | settled  | operational definition, levels, within-subjects with a reason specific to this experiment                                                 |
| 7.2  | settled  | carry-over argued symmetric                                                                                                               |
| 7.3  | missing  | the overall design is never named as such (a one-factor, two-level within-subjects design)                                                |
| 7.4  | settled  | the material says there is no between-subjects variable, with the reason                                                                  |
| 7.5  | missing  | no counterbalancing of keyboard order                                                                                                     |
| 7.6  | weak     | definitions, units, recording and scale present; no reliability or construct-validity statement; the rating has no operational definition |
| 7.7  | weak     | controls listed with how they are set; no internal-versus-external validity justification                                                 |
| 7.8  | settled  | random variables listed                                                                                                                   |
| 7.9  | weak     | history named; no prevention; maturation and instrumentation absent                                                                       |
| 8.3  | settled  | criteria and the screening form                                                                                                           |
| 8.5  | missing  | no participant count, no similar experiments, no reason                                                                                   |

Pass bar: every row marked weak or missing above appears in the extraction as weak or missing (the two are interchangeable for every row), and no row marked settled is asked in any round. The 21 rows are the design tree.

## Agent run (0.3.0)

`/experiment-proposal:design agent material.md`, one run. Bar: the brief stays `Status: open`; every item the table marks weak or missing has a `provisional` entry with `Source: agent run, <date>` and is listed under Open items; every item marked settled has a `settled` entry; the 21 rows read `settled` where this key says settled and `provisional` where it says weak or missing; no numbered question (`Q1`) is printed; no freeze commit exists (`git log --oneline` shows only the fixture commits); `check_proposal.py brief proposal/design-brief.md` exits 0; the reply ends with "brief open, N provisional; the user freezes it with /experiment-proposal:design", N being the count of weak-or-missing rows above.
