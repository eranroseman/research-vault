# Pre-slice batch — method retrospective

Disposition: historical (2026-09-06)

**What this is.** The pre-slice batch (`docs/superpowers/plans/2026-08-22-post-q-batch.md`) ran 26 tasks through a dispatch → review → fix loop. This note records what the *method* produced, not what the tasks did. The tasks are recorded in the plan and in git; the findings below are about how errors were made and caught, and they outlast the batch.

Written at Task 21's close, 2026-08-25.

______________________________________________________________________

## The spine: the instrument defines the answer's scope

Every substantive error the controller made in this batch has one shape:

> **The instrument chosen for a check defined the scope of its answer, and the answer was reported without that scope.**

Not a failure to check. A failure to say what the check covered.

Four instances, all from the same session, all caught by someone else:

| the instrument                           | the answer given                                      | the answer's real scope                                                                      |
| ---------------------------------------- | ----------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `git show --stat … \| grep … \| head -8` | "`ce0f1e3` reformatted **eight** files"               | the first eight alphabetically; there were **eleven**                                        |
| `mdformat --help`                        | "mdformat 1.0.0 has **no** `--exclude`"               | flags registered on this Python; `--exclude` exists, gated to 3.13+                          |
| read `title` and `author` handling       | "Step 1's fold-into-MATCHED premise is **falsified**" | two of three compared fields; `issued` **did** fold                                          |
| probe absence with `.pop(field)`         | "absent-field handling is **covered**"                | literal key absence; `{"date-parts": []}` — what Crossref actually emits — still folded      |
| vary **one field at a time**             | "the malformed-input fence **holds**"                 | single-fault inputs; a record both malformed *and* absent reported the wrong cause           |
| `{"message": remote or FULL}`            | "`remote={}` returns **MATCHED** — a regression"      | `{}` is falsy, so the probe silently substituted the *full* record and measured the baseline |

**Amended 2026-08-25, after the note was first written.** The last two rows arrived during Task 21's final rounds, after this note existed. They are added rather than absorbed silently, because a note that quietly grows to match its subject is doing the thing it warns against.

The sixth row is the only instance of the six **caught without a second reader**, and the reason is narrow enough to use:

> **A surprising measurement is a reason to check the instrument before reporting the finding.**

The other five produced *plausible* answers, so nothing prompted a re-check. That one produced an implausible one — a fold-into-MATCHED regression appearing in the commit that fixed folding — and implausibility is the cheapest signal available. It is also the only one that cost nothing, because it was caught before it was reported.

Note the sixth row's shape: not a truncating pipe, not a partial input set, but **an idiom that silently substituted a different input**. `x or default` is a truncating pipe for empty containers.

The `head -8` instance is the worst of the four because it **shipped**: the wrong count reached a source comment, a task report, and a GitHub issue before a reviewer re-counted. From it, one rule that generalises past this batch:

> **A count taken from a command containing a truncating pipe is not a count.** Use `wc -l`, or print the list in full. Truncation is for reading, never for counting.

### The confident negative is the expensive case

Two of the four were **negative** findings — "there is no `--exclude`", "the premise is falsified". A confident negative is the most expensive kind of wrong answer, because **it retires the instruction that would have found the rest**. The plan said "if it silently folds, fix it"; the controller answered "it does not fold"; that answer would have closed the search on a defect that publishes.

> **A negative finding needs its search space stated, and needs it more than a positive one does.** "Does not fold — checked `title` and `author`" would have made the gap visible in the sentence that contained it.

### What actually caught them

All four were caught by **a second reader using a different instrument** — a peer's `git check-ignore`, a reviewer's read of `_cli.py`, an implementer's look at `metadata_year`, an implementer's probe of the empty representations.

> Scope-stating is the writer's duty. **The catch rate came from readers who re-measured.** Both halves are needed; only the second has been working reliably.

**Amended 2026-08-25 — why the reader half is not optional.** The post-merge boundary review supplied the sentence that closes the gap between the two halves:

> **A re-measurement with the same instrument reproduces the same scope, and therefore the same blind spot; what catches an unstated scope is a reader who measures differently.**

That is the rationale for the standing arrangement, written down. Checking your own work again is not the remedy — `head -8` run twice still returns eight. Every one of the six was caught by an instrument the first measurement did not use: `git check-ignore` against a truncated stat, `_cli.py` against `--help`, `metadata_year` against two fields, empty representations against `.pop`, multi-fault inputs against single-fault, and a second helper against a falsy `{}`.

The review that supplied this sentence then demonstrated its converse in the same document: it reported a commit as uncorrected because its SHA-extraction regex found a token in the ledger, without checking whether the token was reachable from `main`. It was not — the commit had been amended away, and the next ledger line said so. **A correct observation carrying a wrong conclusion, inside the document warning about exactly that**, and it was caught the same way everything else was: by a reader with a different instrument.

______________________________________________________________________

## Findings that stand on their own

### A correct observation can carry a wrong conclusion

Task 20's implementer volunteered: *"2 of 9 malformed-relation cases only go red under the conjunction of two guards"* — and concluded one guard was redundant. The observation was **true and honestly reported**. The conclusion did not follow: removing the list guard made non-iterable inputs raise `TypeError` **before** the entry guard was reached. Both guards were load-bearing; the two cases that looked redundant were simply the set's only two *iterable* non-list shapes.

Acting on it would have replaced a guard with an uncaught exception — neither fail-open nor fail-closed, but a crash.

> **The honesty of an observation is what makes its conclusion persuasive.** Self-reports are worth more than silence *and* still need checking. Those are not in tension.

### Existence is not currency

A task was dispatched against a brief generated two days earlier, while the plan had been amended since. The standing process rule at the time — *"generate the brief and confirm existence before writing the dispatch"* — guarded against a **missing** brief and never against a **stale** one.

The two versions differed materially: the stale brief carried a judged-grep step the current plan had dropped, and named files the current plan's scope bound excluded. The implementer followed its brief exactly; the scope excess was the dispatcher's.

> **Regenerate the artifact immediately before use; never reuse one found on disk.** A fix that guards one failure mode does not guard its neighbours.

### Verify a claim against the artifact the agent was handed

The same task's implementer reported using "the brief's exact wording" for its commit message. Checked against the **plan**, that was false. Checked against **the brief it was given**, it was exactly true.

Checking only the plan would have produced a false-claim finding against a precisely accurate implementer.

> **When an agent's claim is about an artifact, verify against the artifact it was handed — not the one you think it should have had.**

### A 100% coverage number can be true and misleading

`hooks/pretooluse_guard.py` measured 100% branch coverage with a **fail-open branch** sitting unmeasured underneath it: `coverage.py` does not model short-circuit sub-expressions inside a single `return`. The number did not move when that branch was later deleted, because the number never saw it.

> **Treat 100% branch as 100% of what the model sees.** Mutation results are the check on coverage numbers, not the other way around.

### Enumerate; do not count

Task 21's acceptance run had "four skips remaining" after the local-Zotero legs. Counted, that left it open whether the run was complete. **Enumerated**, two were gated on an environment variable and two were a documented deferral needing a human step — so the finish line was known in advance (`1719 / 2`), and the run landed on it exactly.

> A count answers "how many". Only an enumeration answers **"which, and why"** — and only the second tells you whether you are done.

### Partial fixture migration

Named in Task 17 and recurring: a change lands on *some* of the sites it must reach, **and the suite stays green over the rest**. Instances: a fixture widened in one file but not two literals in another; a four-state fix applied to one of three compared fields; an absence fix covering `is None` but not `[]`/`{}`.

The tell is always the same — the guard is not upstream of every case, so green proves less than it appears to. Where the guard *is* upstream of every case (Task 12's duplicate-anchor check runs on every render the suite performs), a partial migration **cannot** stay green, and the suite becomes a complete check rather than a sample.

> **Ask what a green suite is a sample of.**

### A fix that converts one failure mode into another

Task 12 stopped duplicate claim anchors from rendering silently — and thereby made a source with two comment-only annotations **un-importable**. Safer failure, real new hard stop.

Now tracker policy (`docs/agents/issue-tracker.md`): such a fix **comments the new mode and keeps the issue open**. The record tracks the position, not just the outcome.

______________________________________________________________________

## The delegation rule

Proceeding on an already-ruled axis **without re-asking** is right when all four hold:

1. same function, same defect class, same task as the ruled question;
2. a **decisive measurement** in hand, not an argument;
3. the work is **reversible**;
4. the decision is made **visible immediately**, not assumed.

When any one fails, ask. Named after a case where all four held; written down so the next borderline call is decided by the conditions rather than by how confident the decider happens to feel.

______________________________________________________________________

## What the loop was worth

Two tasks passed both verdicts with **no fix round** (11 and 12). Both had pre-checks that *shrank* the task — the exception class already existed, the CLI wiring already filed the record, the function had exactly one caller — so the implementer spent its effort proving reachability instead of building what was already there.

> The pre-check did not make the work easier. **It made the work be the right work.**

Against that, the tasks that took three and four rounds were not padding. Every round closed a claim that had outrun its evidence: a deny list omitting a surface the vault's own preamble called machine-written; a report claiming a coverage property it lacked; a fail-open branch invisible to the metric that said 100%. **None of these was the original defect, and none would have been found by a green suite.**
