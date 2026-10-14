# Target selection with a mouse and a trackball: a controlled experiment

## Introduction

Does selecting targets with a mouse rather than a trackball change movement time and error rate? We will compare movement time and error rate with a mouse and a trackball when right-handed young adults select targets at three distances and three sizes on a desktop display. Pointing devices remain the main way people select on-screen targets, and the choice between a mouse and a trackball still comes up wherever desk space is tight (MacKenzie, 1992; Card, English and Burr, 1978). Earlier comparisons report mixed results across target sizes, and none we found used the same target geometry across both devices with young adults. Only a controlled experiment can show that the device, rather than the person or the task, causes a difference in movement time; a survey of device preference or an observation of daily use could not. The contributions will be:

- movement-time and error-rate estimates for both devices across nine distance-and-size combinations;
- a test of whether the mouse's advantage grows for small targets;
- a reusable target-selection task program and its logs.

The rest of this proposal reviews the literature, states the hypotheses, and describes the design, participants, materials, procedure and planned analysis, with the consent form, script and questionnaire in the appendix.

## Literature review

Fitts's law models movement time as a function of the index of difficulty, log2(A/W + 1), where A is the distance and W the target width (Fitts, 1954; MacKenzie, 1992). Card, English and Burr (1978) found the mouse faster than a joystick and step keys for text selection. Epps (1986) and MacKenzie, Sellen and Buxton (1991) compared pointing devices and found the trackball slower than the mouse in several tasks, with the gap depending on target size. Later work on cursor acceleration and display resolution (Casiez and Roussel, 2011) suggests the gap may have narrowed. The gap in this literature is a comparison that crosses device with a full distance-by-size grid in young adults using current devices; our study fills it by testing both devices on the same nine combinations with the same participants.

## Hypotheses

- H1: Mean movement time will be shorter with the mouse than with the trackball (MacKenzie, Sellen and Buxton, 1991; Epps, 1986).
- H2: Error rate will be lower with the mouse than with the trackball.
- H3: The mouse's movement-time advantage will be larger for smaller targets, an interaction between device and target size (MacKenzie, Sellen and Buxton, 1991).

Each hypothesis is scoped to the two devices and the nine combinations tested and can be tested against a null hypothesis of no difference. If a difference is not statistically significant, we will report the estimate and its interval and treat the hypothesis as not supported rather than as refuted.

## Design

Independent variables. Device: mouse or trackball, each a named make and model, within subjects, because individual pointing skill varies far more than the device effect we expect and a within-subjects comparison removes it; the order of the two devices is counterbalanced, half the participants starting with the mouse and half with the trackball, assigned from a shuffled list. Distance: 128, 256 and 512 pixels from the start point to the target centre, within subjects. Target size: 16, 32 and 64 pixels wide, within subjects. Together, a 2 × 3 × 3 within-subjects factorial design. Carry-over between the devices is expected to be symmetric: a few minutes on either device disturbs habits on the other by about the same amount. The distances and sizes span the range of ordinary desktop targets, from icons to menu bars, wide enough to show an effect and realistic in practice. There is no between-subjects variable.

Dependent variables. Movement time: milliseconds from the start of a trial to the click, timed by the study software; ratio scale; reliable to the millisecond because the software timestamps both events. Error rate: the proportion of trials in which the click falls outside the target, logged by the software; ratio scale; it measures selection accuracy, the complement of the speed measure, and the two will be reported together.

Control variables. Right-handed participants aged 18 to 22, determined by self-report on the screening form; the same display, software, task, room and scripted instructions for everyone; this buys internal validity at the cost of external validity: the results may not describe left-handed users or older adults.

Random variables. Individual skill, vision, mood, time of day, and anything else that varies by chance within the sample.

Confounds. History and time of day: both devices are used by every participant within one session. Maturation: a single short session. Instrumentation: the study software is frozen before the first participant. Experimenter: one experimenter runs every session.

## Participants

Twenty-four right-handed adults aged 18 to 22 will take part, recruited from the author's own course section by an announcement in class and a sign-up sheet, and screened by a short form for handedness and age. They are a convenience sample, so the results describe right-handed young adults only cautiously. The number follows similar device comparisons (MacKenzie, Sellen and Buxton, 1991, used 12) and the power analysis in the planned analysis section, which gives 24 for 80% power on movement time; the pilot will confirm the trial count rather than the participant count. Twenty-four is a multiple of the two counterbalanced device orders. Four extras will be recruited for no-shows. The pilot sample (three lab members) differs from the main sample and its data will not be reported.

## Materials

A mouse and a trackball, each named by make and model; a desktop computer with a 24-inch, 1920 × 1080 display, which fixes the physical size of the pixel distances and sizes; a program that presents targets at the three distances and three sizes and logs, for each trial, the participant code, the device, the distance, the size, the movement time and whether the click landed on the target; a demographic questionnaire asking age and handedness. The program will be run through two complete sessions by the experimenters before the pilot, and its log checked against a screen recording of those sessions. The questionnaire is custom because the two items need no standard instrument; its answers are what participants reported.

## Procedure

Each participant is tested alone in room 204, the same room for every session. Welcome (2 minutes); consent form (5 minutes); scripted instructions, read from the script in a neutral tone (3 minutes); 10 practice trials on the first device, then 5 trials of each of the nine distance-and-size combinations (10 minutes); the same on the second device (10 minutes); the demographic questionnaire (2 minutes); debriefing (3 minutes). The session estimate is 35 minutes. Every participant hears the same instructions because the experimenter reads the verbatim script, and the device order is the only cue that differs between conditions, which counterbalancing holds constant across the sample.

## Planned analysis

The primary measure is movement time. Before testing we will check for impossible values, missing trials and failed sessions, plot each dependent variable's distribution, and compute means and medians per participant and condition, since time measures are skewed. Movement time will be reduced to one mean per participant per device and compared with a paired t-test, or Wilcoxon's matched-pairs test if the differences are clearly not normal; error rate, one proportion per participant per device, the same way. H3 will be tested with a repeated-measures ANOVA on device, distance and size, with a sphericity check for distance and size. Participants whose mean trackball movement time exceeds 2000 milliseconds will be excluded as not having engaged with the task; failed sessions will be excluded and reported. The significance level is .05; every p value will be reported with its effect size, whether or not it supports the hypotheses; the three hypotheses form one family, Holm-adjusted. All of the above is pre-specified. The power analysis (`proposal/power.R`) assumed a 120 ms device difference from MacKenzie, Sellen and Buxton (1991) and gave 24 participants for 80% power; across 90 to 150 ms the count ranges from 36 to 16.

## Timeline

Pilot in week 3; data collection in weeks 4 to 7; analysis in weeks 8 and 9; write-up in weeks 10 to 12. If sign-ups fall short by week 5, recruiting extends to a second section.

## References

- Card, S. K., English, W. K., and Burr, B. J. (1978). Evaluation of mouse, rate-controlled isometric joystick, step keys, and text keys for text selection on a CRT. Ergonomics, 21(8), 601–613.
- Casiez, G., and Roussel, N. (2011). No more bricolage! Methods and tools to characterize, replicate and compare pointing transfer functions. UIST 2011.
- Epps, B. W. (1986). Comparison of six cursor control devices based on Fitts' law models. Proceedings of the Human Factors Society, 30(4), 327–331.
- Fitts, P. M. (1954). The information capacity of the human motor system in controlling the amplitude of movement. Journal of Experimental Psychology, 47(6), 381–391.
- MacKenzie, I. S. (1992). Fitts' law as a research and design tool in human-computer interaction. Human-Computer Interaction, 7(1), 91–139.
- MacKenzie, I. S., Sellen, A., and Buxton, W. (1991). A comparison of input devices in elemental pointing and dragging tasks. CHI 1991, 161–166.

## Appendix A: recruiting announcement

Right-handed students aged 18 to 22 are invited to a 35-minute study of pointing devices in room 204. Sign up on the sheet at the front of the class.

## Appendix B: consent form

You are invited to take part in a study run by the author, a graduate student in the Department of Computer Science, supervised by the course instructor, as a course project. The study compares two pointing devices. You will select targets on a screen with a mouse and a trackball and answer two questions about yourself; it takes about 20 minutes. You may stop at any time. The risks are no greater than those of ordinary computer use; there is no payment. Your data are stored under a code, not your name; the two experimenters see the data. Questions about the research go to the author at the address below; questions about your rights as a participant go to the university's research office. Consent is recorded by your signature below.

## Appendix C: session script

"Welcome, and thank you for coming. Please read the consent form and sign it if you agree to take part. In this study you will select targets on the screen with two devices. Click on each target as quickly and accurately as you can. There are ten practice trials first. Begin when ready." After the first device: "Now the second device; the task is the same." After the questionnaire: "That ends the session. The study compares the two devices on speed and accuracy. Thank you."

## Appendix D: demographic questionnaire

Age: \_\_\_\_ Handedness: \_\_\_\_

## Appendix E: ethics review

The study falls under the department's standing approval for minimal-risk interaction studies with adult participants (protocol CS-HCI-2026-01).
