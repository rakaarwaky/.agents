# Step 1: Wait for Grok to Finish

Grok Build runs the full implement → review → fix loop itself, in its own Orca worktree, driven by the skill's `grok/` references. Hermes waits and does nothing else.

## Wait

Run `sdc pool grok <terminal_handle> --wait` to poll until Grok finishes. The `sdc pool` command is the standardized grok-session poller — it reads the rendered screen (`orca terminal read --screen --json`), paces with `orca terminal wait --for tui-idle`, and detects completion from either the `EXECUTE_PLAN_COMPLETE` sentinel or a final-report shape (PR marker + settled prompt) on an idle screen.

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

## When Grok Is Done

Grok writes artifacts to `/tmp/grok-<username>/` (resolved by `scripts/host.py` via `scratch_dir()`), keyed by `REVIEW_ID`:

- **Per-persona review files**: `grok-review-<REVIEW_ID>-<persona>.md` for every auto-selected persona.
- **Summary file**: `grok-review-summary-<REVIEW_ID>.md` — aggregate counts and top issues.

The run id (`REVIEW_ID`) is an 8-hex-character identifier (e.g. `cca7ab30`) printed in Grok's terminal output or visible in artifact filenames. After Grok exits, locate artifacts with:

```bash
ls -lt /tmp/grok-<username>/grok-review-* 2>/dev/null
```

**Pitfall — terminal `tui-idle` and empty content are not reliable completion signals.** `orca terminal read` can return `content len: 0` and `nextCursor: 0` while Grok is still actively working internally (e.g. the TUI shows "Waiting for response…" but edits, test runs, and lint scans are happening in parallel). Do not stop polling based on empty terminal output or `tui-idle` alone. Confirm Grok finished by checking `git -C <worktree_path> diff --stat` for the expected edits — if the diff is stable across multiple polls and matches the brief scope, Grok is done even if the terminal shows no new output.

**Pitfall — Grok may write no review artifacts.** A headless or single-pass Grok run produces no files under `/tmp/grok-<username>/` and its terminal `tail` can stay empty for minutes, showing only the `grok '--permission-mode' 'bypassPermissions'` launch line while it works. Neither is a failure: confirm the run did its job by checking `git -C <worktree> diff` / `status --short` for the expected edits rather than blocking on artifacts that may never appear. The worktree diff is the primary proof of completion, not the artifact files.

If Grok reports failure or exits non-idle with an error, report it verbatim to the user and stop — do not retry, do not hand-fix the worktree.

Report to the user: "Grok Build finished the implement→review→fix loop. <worktree_path> is ready."

Then proceed to Step 2.