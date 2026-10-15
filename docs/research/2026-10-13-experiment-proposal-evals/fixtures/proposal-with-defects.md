# Target selection with a mouse and a trackball: a controlled experiment

## Introduction

Does selecting targets with a mouse rather than a trackball change movement time? We will compare movement time and error rate with a mouse and a trackball when right-handed young adults select targets at three distances and three sizes on a desktop display.

The motivation is practical. Pointing devices remain the main way people select on-screen targets, and the choice between a mouse and a trackball still comes up wherever desk space is tight, where a trackball's fixed footprint and lower wrist travel are offered as advantages (Card, English and Burr, 1978; MacKenzie, 1992). Vendors make the case for each device on comfort and speed, but the evidence that would settle it for ordinary desktop targets is thin and old. Earlier comparisons report mixed results across target sizes (Epps, 1986; MacKenzie, Sellen and Buxton, 1991), and none we found used the same target geometry across both devices with young adults on a current high-resolution display. The problem matters beyond the two devices: a usable estimate of the device effect across target sizes tells interface designers how much the size of a control buys on each device, which bears on toolbar and menu layouts for the many users who cannot or will not use a mouse (Douglas, Kirkpatrick and MacKenzie, 1999). Only a controlled experiment can show that the device, rather than the person or the task, causes a difference in movement time; a survey of device preference or an observation of daily use could not separate the device from the habits of the people who chose it.

The contributions will be (a) movement-time and error-rate estimates for both devices across nine distance-and-size combinations on a 1920 by 1080 display, (b) a test of whether the mouse's advantage grows for small targets, and (c) a reusable target-selection task program and its trial logs, released with the final report. The rest of this proposal reviews the literature, states the hypotheses, and describes the participants, materials, procedure and design, with the recruiting announcement, consent form, script and questionnaire in the appendix.

## Literature review

Three bodies of work motivate the problem, justify the approach, and describe similar studies.

The first is the modelling of rapid aimed movement. Fitts (1954) showed that the time to move to a target grows with the logarithm of the ratio of movement amplitude to target width, the index of difficulty; MacKenzie (1992) reviewed the law's application to human-computer interaction and proposed the Shannon formulation, log2(A/W + 1), that most pointing studies have used since. Soukoreff and MacKenzie (2004) set out how the law should be applied in evaluating pointing devices, including the use of effective target width and the reporting of throughput, and ISO 9241-9 (2000) standardised a multi-directional tapping task for exactly that purpose. Zhai (2004) cautioned that throughput depends on how the index of difficulty is computed and that device comparisons should report their method. Accot and Zhai (1997) extended the law to steering through constrained paths, which matters for menus and sliders but not for the discrete selection task studied here. These works justify the task: discrete selection at controlled amplitudes and widths, so that the device effect can be read off against a known baseline model.

The second body is the comparison of pointing devices. Card, English and Burr (1978) found the mouse faster than a joystick and step keys for text selection, and attributed its advantage to the direct mapping of hand movement to cursor movement. Epps (1986) compared six cursor-control devices with Fitts's law models and reported the trackball slower than the mouse, with the gap depending on the index of difficulty. MacKenzie, Sellen and Buxton (1991) compared a mouse, a tablet with stylus and a trackball in pointing and dragging tasks with twelve participants, and found the trackball slowest in both, with error rates that rose for dragging; their study is the closest to ours in task and devices, and its twelve participants and within-subjects design inform our count. Douglas, Kirkpatrick and MacKenzie (1999) tested the ISO 9241-9 protocol on a joystick and a touchpad and showed that the standard's throughput measure separates devices that a simple time measure does not. Kabbash and Buxton (1995) showed that the size of the cursor, not only of the target, changes selection time, which is why our program keeps one cursor for both devices. Balakrishnan (2004) reviewed techniques that beat Fitts's law by enlarging targets or cursors, and Grossman and Balakrishnan (2005) demonstrated one such technique, the bubble cursor, whose advantage grows exactly where small targets are sparse; both argue that the device-by-size interaction is where design decisions turn, which is the interaction our third hypothesis tests.

The third body concerns the devices as people meet them today. Casiez and Roussel (2011) showed that cursor acceleration functions differ by operating system and device driver and that unreported transfer functions make device comparisons hard to replicate; we will therefore fix and report the pointer settings for both devices. The same work suggests that the gap between a mouse and a trackball measured in the 1980s and 1990s may have narrowed with better sensors and acceleration, which is one reason the question is open again.

A fourth strand concerns how the two measures should be taken and reported. Soukoreff and MacKenzie (2004) argued that movement time and error rate must be read together, because participants trade one for the other, and that an evaluation reporting speed alone can be reversed by a change of instructions; they recommended reporting the raw error rate beside the time and, where throughput is computed, adjusting the target width for the spread of the selection points. Zhai (2004) separated the information and non-information parts of pointing and showed that the regression intercept, not only the slope, differs between devices, which is why our analysis will report both the mean time per combination and the difference between devices at each size rather than a single throughput figure. Douglas, Kirkpatrick and MacKenzie (1999) also found that participants' subjective ratings of a device did not track its measured performance, which is one reason this study measures performance and asks no preference question. MacKenzie, Sellen and Buxton (1991) logged errors as clicks outside the target and reported them as rates per condition, the definition our program uses, so that our error figures can be set beside theirs.

Together these studies motivate the comparison (the device effect is practically important and the old evidence is mixed), justify the approach (a discrete Fitts-style task with controlled amplitudes and widths, within subjects, with reported pointer settings) and describe the nearest similar study (MacKenzie, Sellen and Buxton, 1991). The gap this literature leaves is a comparison that crosses the two devices with a full distance-by-size grid in young adults using current devices on a current display, with the interaction between device and target size tested rather than assumed; our study fills it by testing both devices on the same nine combinations with the same participants.

## Research questions or Hypotheses

- H1: Mean movement time will be shorter with the mouse than with the trackball (MacKenzie, Sellen and Buxton, 1991; Epps, 1986).
- H2: Error rate will be lower with the mouse than with the trackball.
- H3: The mouse's movement-time advantage will be larger for smaller targets, an interaction between device and target size (MacKenzie, Sellen and Buxton, 1991; Grossman and Balakrishnan, 2005).

Each hypothesis is scoped to the two devices and the nine distance-and-size combinations tested and can be tested against a null hypothesis of no difference. The possible outcomes are listed in advance. For H1, a statistically significant advantage for the mouse supports it; a statistically significant advantage for the trackball refutes it; a difference that is not statistically significant is reported with its estimate and interval and treated as not supported rather than refuted, since a study of this size may miss a small effect. The same three outcomes apply to H2 and to H3's interaction, where the interpretable null is an advantage that does not change with target size.

## Participants

Twenty-four right-handed adults aged 18 to 22 will take part, recruited from the author's own course section by an announcement in class (Appendix A) and a sign-up sheet, and screened by a short form (Appendix D) for handedness and age. They are a convenience sample, so the results describe right-handed young adults only cautiously. No eligibility criterion selects people for an extreme score on pointing performance. The study will run under the department's standing approval for minimal-risk studies (Appendix E).

The number follows similar device comparisons and a stated reason: MacKenzie, Sellen and Buxton (1991) used twelve participants in a within-subjects design and found the device effect clearly, and Douglas, Kirkpatrick and MacKenzie (1999) used twelve per device; twenty-four, twice the nearer study, is what the course term allows at one session per participant, and it is a multiple of the two counterbalanced device orders. The count is pre-specified and will not be revised after data collection starts; the pilot will refine the trial count per combination, not the participant count. Four extras will be recruited for no-shows and for participants who turn out not to fit the profile; if sign-ups fall short by week 5, recruiting extends to a second section. Participants who complete the session will receive course credit. The pilot sample, three lab members, differs from the main sample and its data will not be reported; the pilot will run the full procedure once per member, time each phase against the estimates in Procedure, and check that five trials per combination leave the session within 35 minutes, raising the trial count to seven if the sessions run short.

## Materials

Participants will interact with a Logitech M510 mouse and a Kensington Orbit trackball, both with pointer acceleration disabled and the same pointer speed; a desktop computer with a 24-inch, 1920 by 1080 display, which fixes the physical size of the pixel distances and sizes; a program that presents targets at the three distances and three sizes and logs, for each trial, the participant code, the device, the distance, the size, the movement time and whether the click landed on the target; and a demographic questionnaire asking age and handedness.

The program will be written for the study and will log every trial automatically, so nothing will be copied by hand; its logged fields will be the six just listed plus a timestamp. Before anyone uses it, the author will run two complete sessions and check the log against a screen recording of those sessions, trial by trial, so that the timing and the hit test are confirmed. The questionnaire is custom because the two items need no standard instrument; its answers will be what participants report.

## Procedure

Each participant will be tested alone in room 204, the same room for every session. The phases, in order, with their estimated durations: welcome (2 minutes); the consent form (Appendix B), read and signed (5 minutes); scripted instructions, read from the script (Appendix C) in a neutral tone (3 minutes); 10 practice trials on the first device, then 5 trials of each of the nine distance-and-size combinations (10 minutes); the same practice and trials on the second device (10 minutes); the demographic questionnaire (Appendix D) (2 minutes); debriefing (3 minutes). The durations sum to the session estimate of 35 minutes.

Every participant will hear the same instructions because the experimenter will read the verbatim script in the appendix; the device order will be the only cue that differs between conditions, and counterbalancing will hold it constant across the sample. The mouse and the trackball will be used at the point in the session where the script introduces them; the questionnaire will be handed over after the second device; the debriefing will close the session.

## Design

Independent variables. Device: the mouse or the trackball named in Materials, within subjects, because individual pointing skill varies far more than the device effect we expect and a within-subjects comparison removes it from the comparison; the order of the two devices will be counterbalanced, half the participants starting with the mouse and half with the trackball, assigned from a shuffled list prepared before the first session. Distance: 128, 256 and 512 pixels from the start point to the target centre, within subjects. Target size: 16, 32 and 64 pixels wide, within subjects. Together, a 2 by 3 by 3 within-subjects factorial design; H3's interaction has its variables crossed. The distances and sizes span the range of ordinary desktop targets, from icons to menu bars, wide enough to show an effect and realistic in practice (MacKenzie, 1992). Carry-over between the devices is expected to be symmetric: a few minutes on either device disturbs habits on the other by about the same amount. There is no between-subjects variable.

Dependent variables. Movement time: milliseconds from the start of a trial to the click, timed by the study software; ratio scale; reliable to the millisecond because the software will timestamp both events. Error rate: the proportion of trials in which the click falls outside the target, logged by the software; ratio scale; it measures selection accuracy, the complement of the speed measure, and the two will be reported together because people trade speed for accuracy (Soukoreff and MacKenzie, 2004). A trial will begin when the start box is clicked and will end at the first click after the target appears, whether or not it lands on the target, so every trial will yield one time and one hit-or-miss record; the start box and the target will never overlap, and the cursor will be reset to the start box between trials so that every movement begins from the same point.

Control variables. Right-handed participants aged 18 to 22, determined by self-report on the screening form; the same display, software, pointer settings, task, room and scripted instructions for everyone. Holding these constant buys internal validity at the cost of external validity: the results may not describe left-handed users or older adults.

Random variables. Individual skill, vision, mood, time of day, and anything else that varies by chance within the sample.

Confounds to watch for. History and time of day: both devices will be used by every participant within one session, so neither can fall on a different day or time. Maturation: a single short session. Instrumentation: the study software and the pointer settings will be frozen before the first participant. Experimenter: one experimenter will run every session. Device order: counterbalanced as above.

## Timeline

Pilot in week 3; data collection in weeks 4 to 7; analysis in weeks 8 and 9; write-up in weeks 10 to 12.

## References

- Accot, J., and Zhai, S. (1997). Beyond Fitts' law: models for trajectory-based HCI tasks. CHI 1997, 295–302.
- Balakrishnan, R. (2004). "Beating" Fitts' law: virtual enhancements for pointing facilitation. International Journal of Human-Computer Studies, 61(6), 857–874.
- Card, S. K., English, W. K., and Burr, B. J. (1978). Evaluation of mouse, rate-controlled isometric joystick, step keys, and text keys for text selection on a CRT. Ergonomics, 21(8), 601–613.
- Casiez, G., and Roussel, N. (2011). No more bricolage! Methods and tools to characterize, replicate and compare pointing transfer functions. UIST 2011, 603–614.
- Douglas, S. A., Kirkpatrick, A. E., and MacKenzie, I. S. (1999). Testing pointing device performance and user assessment with the ISO 9241, part 9 standard. CHI 1999, 215–222.
- Epps, B. W. (1986). Comparison of six cursor control devices based on Fitts' law models. Proceedings of the Human Factors Society, 30(4), 327–331.
- Fitts, P. M. (1954). The information capacity of the human motor system in controlling the amplitude of movement. Journal of Experimental Psychology, 47(6), 381–391.
- Grossman, T., and Balakrishnan, R. (2005). The bubble cursor: enhancing target acquisition by dynamic resizing of the cursor's activation area. CHI 2005, 281–290.
- ISO (2000). ISO 9241-9: Ergonomic requirements for office work with visual display terminals, part 9: requirements for non-keyboard input devices. International Organization for Standardization.
- Kabbash, P., and Buxton, W. (1995). The "prince" technique: Fitts' law and selection using area cursors. CHI 1995, 273–279.
- MacKenzie, I. S. (1992). Fitts' law as a research and design tool in human-computer interaction. Human-Computer Interaction, 7(1), 91–139.
- MacKenzie, I. S., Sellen, A., and Buxton, W. (1991). A comparison of input devices in elemental pointing and dragging tasks. CHI 1991, 161–166.
- Soukoreff, R. W., and MacKenzie, I. S. (2004). Towards a standard for pointing device evaluation, perspectives on 27 years of Fitts' law research in HCI. International Journal of Human-Computer Studies, 61(6), 751–789.
- Zhai, S. (2004). Characterizing computer input with Fitts' law parameters: the information and non-information aspects of pointing. International Journal of Human-Computer Studies, 61(6), 791–809.

## Appendix A: recruiting announcement

Right-handed students aged 18 to 22 are invited to a 35-minute study of pointing devices in room 204. Sign up on the sheet at the front of the class.

## Appendix B: consent form

You are invited to take part in a study run by the author, a graduate student in the Department of Computer Science, as a course project. The study compares two pointing devices. You will select targets on a screen with a mouse and a trackball and answer two questions about yourself; it takes about 20 minutes. You may stop at any time. The risks are no greater than those of ordinary computer use; there is no payment. Your data are stored under a code, not your name; only the author sees the data. Questions about the research go to the author at the address below; questions about your rights as a participant go to the university's research office. Consent is recorded by your signature below.

## Appendix C: session script

"Welcome, and thank you for coming. Please read the consent form and sign it if you agree to take part. In this study you will select targets on the screen with two devices. Click on each target as quickly and accurately as you can. There are ten practice trials first. Begin when ready." After the first device: "Now the second device; the task is the same." After the questionnaire: "That ends the session. The study compares the two devices on speed and accuracy. Thank you."

## Appendix D: demographic questionnaire

Age: \_\_\_\_ Handedness: \_\_\_\_

## Appendix E: ethics review

The study falls under the department's standing approval for minimal-risk interaction studies with adult participants (protocol CS-HCI-2026-01).
