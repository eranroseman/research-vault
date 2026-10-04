# Background: released code and data

Loads when the paper releases code or data. Stage 2 runs these checks; each one is recorded as a W entry.

## What to open

Analysis code, notebooks, data dictionaries, and data files. For every headline number — every number in the abstract and conclusion — find the analysis code behind it, read it, and recompute the number from the released data. Do arithmetic in code, never in prose. Compare the recomputed value with the paper's; a mismatch is a C entry as well as a W entry.

## What never to open or fetch

Credential, key, environment, and config files (`.env`, `*.pem`, `credentials.*`, tokens, API keys, private endpoints). If a repository appears to expose one, record its path only, neutrally, as an observation under Ethics — never its contents, and never test whether it works.

## How to handle data

- Download only what a recomputation needs, into the scratch folder.
- Keep aggregates only; never quote an individual row, free-text response, or identifier in any artifact the run writes.
- Never attempt re-identification. If small cell sizes, quasi-identifiers, or linkable fields make re-identification look feasible, note the risk as an observation — that is a finding about the release, not an experiment to run.
- Raw participant-level files are deleted from the scratch folder at the end of the run, and the deletion is recorded in the evidence file.

## How to record each check

One W entry per check: the claim checked; the repository or dataset (URL and commit or version); the file and the code path read; what it showed; the recomputed value beside the paper's. Usage or coverage claims in the paper are checked against the released data itself, not against the paper's description of it.
