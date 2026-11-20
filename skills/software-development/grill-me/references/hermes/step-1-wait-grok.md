# Step 1: Wait for Grok Build to Finish

Poll the Orca terminal until Grok Build's interview loop exits (idle or exited terminal). Do not yield the turn to the user with a passive "waiting for completion" report.

## Polling

Run `sdc pool grok <terminal_handle> --wait` to poll until Grok finishes. The `sdc pool` command is the standardized grok-session poller — it reads the rendered screen (`orca terminal read --screen --json`), paces with `orca terminal wait --for tui-idle`, and detects completion from either the `INTERVIEW_COMPLETE` sentinel or a final-report shape (PR marker + settled prompt) on an idle screen.

```bash
sdc pool grok <terminal_handle> --wait
```

- Without `--wait`, `sdc pool grok <terminal_handle>` performs a single probe and returns immediately with JSON status.
- With `--wait`, it blocks until completion, failure, or deadline (default 2 hours).
- Exit codes: `0` = success (done), `1` = runtime error (orca CLI failure or terminal exited without final report), `3` = deadline exceeded (status still running, `timed_out=true`).
- Override pacing with `--wait-ms` (default 15000), `--idle-confirm` (default 2), `--tail` (default 50), `--sentinel`, `--orca` (default `orca-ide`).
- Heartbeat progress lines go to stderr; the JSON result goes to stdout.
- `tui-idle` returning not-satisfied means Grok is BUSY, not that the poll failed — keep polling. Only a genuine CLI/parse failure counts as an error.
- Run exactly one poll loop at a time. Before starting a fresh loop, kill any existing `sdc pool grok` processes for the same terminal handle.
- Long runtime is not a stall signal — do not escalate, interrupt, or re-spawn before ~90 minutes.

Between polls, do not send text to Grok. Only read.

## Read Grok's Artifacts

When Grok finishes, read these files from `<scratch_dir>`:

- `interview-summary-<INTERVIEW_ID>.md` — the final shared understanding (durable record)
- `resolved-decisions-<INTERVIEW_ID>.md` — decisions and dependency chains (if not cleaned up)
- `open-questions-<INTERVIEW_ID>.md` — any questions escalated to the user (if not cleaned up)

## Proceed to Step 2

Do NOT end the turn after Grok finishes. Proceed immediately to Step 2 verification:

> Grok Build finished the grill-me interview at <worktree_path>. Interview ID: <INTERVIEW_ID>. Proceeding to Step 2 to verify.