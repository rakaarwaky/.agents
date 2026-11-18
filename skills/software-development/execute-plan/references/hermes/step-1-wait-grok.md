# Step 1: Wait for Grok to Finish

Grok Build runs the full execution loop itself — per-PR worktrees, implementer subagents, the 3-reviewer panel per PR, fix rounds, failure cascades, final assembly — driven by its own `grok/` references. Hermes waits and does nothing else.

## Wait

Poll with `orca terminal read --terminal <handle> --cursor <cursor> --limit 1000 --json` until the session is idle. A multi-PR plan can run for a long time; use `orca terminal wait --terminal <handle> --for tui-idle --timeout-ms 60000 --json` and retry with a larger timeout while `satisfied: false`.

- First read: use `--cursor 0`. The JSON response reports `result.terminal.nextCursor` (the paging token for the next read) and `result.terminal.status` (`running` | `exited` | `unknown`).
- Subsequent reads: pass the previous `nextCursor` as `--cursor` so only new output since that read is returned. Stop paging when `nextCursor` is null or unchanged from `latestCursor`.
- `limit` defaults to 120 for tail previews; use `--limit 1000` for long agent responses.
- `orca terminal status --terminal <handle>` is **not** a valid subcommand (returns `invalid_argument`). Use `terminal wait --for tui-idle` to test idle and `terminal read` to drain output.
- Do NOT send text while waiting.

### Automated Polling Script

Execute this loop in `terminal` (set `timeout=600`):

```bash
ORCA="${ORCA_CLI_COMMAND:-$(command -v orca-ide || echo "$HOME/.local/bin/orca-ide")}"
cursor=0
deadline=$((SECONDS + 7200))  # 2 hour absolute deadline
consecutive_errors=0
while true; do
  if (( SECONDS >= deadline )); then
    echo "ERROR: polling deadline exceeded (2h)"
    break 2
  fi
  wait_res=$("$ORCA" terminal wait --terminal "<handle>" --for tui-idle --timeout-ms 60000 --json 2>/dev/null || true)
  satisfied=$(echo "$wait_res" | jq -r '.result.satisfied // false' 2>/dev/null || echo "false")
  if [[ "$satisfied" == "true" ]]; then
    read_res=$("$ORCA" terminal read --terminal "<handle>" --cursor "$cursor" --limit 1000 --json 2>/dev/null || echo "")
    if echo "$read_res" | grep -q "EXECUTE_PLAN_COMPLETE"; then
      echo "SENTINEL: EXECUTE_PLAN_COMPLETE"
      break 2
    fi
    status=$(echo "$read_res" | jq -r '.result.terminal.status // "unknown"' 2>/dev/null || echo "unknown")
    if [[ "$status" == "exited" ]]; then
      echo "ERROR: terminal exited without sentinel — run failed"
      break 2
    fi
    new_cursor=$(echo "$read_res" | jq -r '.result.terminal.nextCursor // empty' 2>/dev/null || echo "")
    if [[ -n "$new_cursor" ]]; then
      cursor="$new_cursor"
    fi
    consecutive_errors=0
  else
    consecutive_errors=$((consecutive_errors + 1))
    if (( consecutive_errors >= 30 )); then
      echo "ERROR: 30 consecutive wait failures — aborting"
      break 2
    fi
  fi
  sleep 5
done
```

## When Grok Is Done

Grok writes artifacts to its scratch dir (`~/.agents/develop/<repo-slug>/execute/`):

- **State file**: `exec-plan-<PLAN_ID>.json` — the full DAG state: per-PR status, `commit_sha`, `review_rounds`, `final_branch`, `final_review_passed`, `pr_urls`, `deferred_issues`.
- **Per-PR summaries**: `exec-summary-<PLAN_ID>-<pr-id>.md`.
- **Per-PR merged reviews**: `exec-review-<PLAN_ID>-<pr-id>.md`.
- **Final report**: Grok's terminal output ends with its final report (per `grok/step-13-final-report.md`).

Read the state file first — it is the single authoritative record of what happened. If Grok reports failure or exits non-idle with an error, report it verbatim to the user and stop — do not retry, do not hand-assemble the final branch yourself.

Report to the user: "Grok Build finished the execution loop. <worktree_path> state: <N> completed, <M> failed, <K> skipped. Final branch: <final_branch>."

Then proceed to Step 2.
