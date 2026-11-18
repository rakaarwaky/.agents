# Step 1: Wait for Grok to Finish

Grok Build runs the full parallel-persona review itself — per-mode file-list collection, auto persona selection, per-persona subagent fan-out, per-persona review files, aggregation — driven by its `grok/` references. Hermes waits and does nothing else.

## Wait

Poll with `orca terminal read --terminal <handle> --cursor <cursor> --limit 1000 --json` until the session is idle.

- First read: use `--cursor 0`. The JSON response reports `result.terminal.nextCursor` (the paging token for the next read) and `result.terminal.status` (`running` | `exited` | `unknown`).
- Subsequent reads: pass the previous `nextCursor` as `--cursor` so only new output since that read is returned. Stop paging when `nextCursor` is null or unchanged from `latestCursor`.
- `limit` defaults to 120 for tail previews; use `--limit 1000` for long agent responses.
- Use `orca terminal wait --terminal <handle> --for tui-idle --timeout-ms 60000 --json` and retry with a larger timeout while `satisfied: false`.
- `orca terminal status --terminal <handle>` is **not** a valid subcommand (returns `invalid_argument`). Use `terminal wait --for tui-idle` to test idle and `terminal read` to drain output.
- Do NOT send text while waiting.

## When Grok Is Done

Grok writes artifacts to its scratch dir (`~/.agents/develop/<repo-slug>/`):

- **Per-persona review files**: `grok-review-<REVIEW_ID>-<persona>.md` for every auto-selected persona (1–3).
- **Summary file**: the aggregated review summary with per-persona issue counts by severity.
- **ERROR rows**: any persona that failed or timed out is recorded as `ERROR` with its error text — the run continues, it is not aborted.

Read the summary file first, then spot-check one per-persona file for a persona you care about most. If Grok reports failure or exits non-idle with an error, report it verbatim to the user and stop — do not retry, do not hand-review the target yourself.

Report to the user: "Grok Build finished the <mode> review of <target>. <N>/<P> personas completed (<M> errored). <bugs> bugs, <suggestions> suggestions, <nits> nits. Summary: <path>."

Then proceed to Step 2.
