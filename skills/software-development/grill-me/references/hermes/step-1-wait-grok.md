# Step 1: Wait for Grok Build to Finish

Poll the Orca terminal until Grok Build's interview loop exits (idle or exited terminal). Do not yield the turn to the user with a passive "waiting for completion" report.

## Polling

Run `orca terminal read --terminal <handle> --json` (or the equivalent for your Orca CLI) repeatedly until:

- The terminal reports idle/exited, **or**
- Grok Build emits the interview-complete sentinel (`INTERVIEW_COMPLETE` as the final line of output).

Between polls, do not send text to Grok. Only read.

## Read Grok's Artifacts

When Grok finishes, read these files from `<scratch_dir>`:

- `interview-summary-<INTERVIEW_ID>.md` — the final shared understanding (durable record)
- `resolved-decisions-<INTERVIEW_ID>.md` — decisions and dependency chains (if not cleaned up)
- `open-questions-<INTERVIEW_ID>.md` — any questions escalated to the user (if not cleaned up)

## Proceed to Step 2

Do NOT end the turn after Grok finishes. Proceed immediately to Step 2 verification:

> Grok Build finished the grill-me interview at <worktree_path>. Interview ID: <INTERVIEW_ID>. Proceeding to Step 2 to verify.
