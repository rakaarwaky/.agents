# Step 1: Wait for Grok to Finish

Grok Build runs the full implement → review → fix loop itself, in its own Orca worktree, driven by the skill's `grok/` references. Hermes waits and does nothing else.

## Wait

Poll with `orca terminal read --terminal <handle> --cursor <cursor> --limit 1000 --json` until the session is idle. A fresh long run may need `orca terminal wait --terminal <handle> --for tui-idle --timeout-ms 60000 --json`; if `satisfied: false`, retry with a larger timeout.

- First read: use `--cursor 0`. The JSON response reports `result.terminal.nextCursor` (the paging token for the next read) and `result.terminal.status` (`running` | `exited` | `unknown`).
- Subsequent reads: pass the previous `nextCursor` as `--cursor` so only new output since that read is returned. Stop paging when `nextCursor` is null or unchanged from `latestCursor`.
- `limit` defaults to 120 for tail previews; use `--limit 1000` for long agent responses.
- `orca terminal status --terminal <handle>` is **not** a valid subcommand (returns `invalid_argument`). Use `terminal wait --for tui-idle` to test idle and `terminal read` to drain output.
- Do NOT send text while waiting.

## When Grok Is Done

Grok writes two artifacts to its scratch dir (`~/.agents/develop/<repo-slug>/implement/`):

- **Implementation summary**: `impl-summary-<run_id>.md` — files changed, design decisions.
- **Review**: `review-<run_id>.md` — the final merged review, 0 open issues when the loop exits.

The run id appears in Grok's terminal output. If Grok reports failure or exits non-idle with an error, report it verbatim to the user and stop — do not retry, do not hand-fix the worktree.

Report to the user: "Grok Build finished the implement→review→fix loop. <worktree_path> is ready."

Then proceed to Step 2.
