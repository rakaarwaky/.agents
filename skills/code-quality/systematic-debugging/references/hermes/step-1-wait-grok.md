# Step 1: Wait for Grok to Finish

Grok Build runs the full debugging pipeline itself — intake, red-capable loop, pattern analysis, ranked hypotheses, TDD fix, verify, guardrails — driven by its `grok/` references. Hermes waits and does nothing else.

## Wait

Poll with `orca terminal read --terminal <handle> --cursor <cursor> --limit 1000 --json` until the session is idle. Debugging runs can be long; use `orca terminal wait --terminal <handle> --for tui-idle --timeout-ms 60000 --json` and retry with a larger timeout while `satisfied: false`.

- First read: use `--cursor 0`. The JSON response reports `result.terminal.nextCursor` (the paging token for the next read) and `result.terminal.status` (`running` | `exited` | `unknown`).
- Subsequent reads: pass the previous `nextCursor` as `--cursor` so only new output since that read is returned. Stop paging when `nextCursor` is null or unchanged from `latestCursor`.
- `limit` defaults to 120 for tail previews; use `--limit 1000` for long agent responses.
- `orca terminal status --terminal <handle>` is **not** a valid subcommand (returns `invalid_argument`). Use `terminal wait --for tui-idle` to test idle and `terminal read` to drain output.
- Do NOT send text while waiting.

### Automated Polling Script

Execute this loop in `terminal` (set `timeout=600`):

```bash
ORCA="${ORCA_CLI_COMMAND:-/home/raka/.local/bin/orca-ide}"
cursor=0
while true; do
  wait_res=$("$ORCA" terminal wait --terminal "<handle>" --for tui-idle --timeout-ms 60000 --json 2>/dev/null || true)
  satisfied=$(echo "$wait_res" | jq -r '.result.satisfied // false' 2>/dev/null || echo "false")
  if [[ "$satisfied" == "true" ]]; then
    echo "Terminal reached tui-idle."
    break
  fi
  read_res=$("$ORCA" terminal read --terminal "<handle>" --cursor "$cursor" --limit 100 --json 2>/dev/null || true)
  cursor=$(echo "$read_res" | jq -r '.result.terminal.nextCursor // empty' 2>/dev/null || echo "$cursor")
  status=$(echo "$read_res" | jq -r '.result.terminal.status // empty' 2>/dev/null || echo "")
  if [[ "$status" == "exited" ]]; then
    echo "Terminal process exited."
    break
  fi
  sleep 5
done
```

## When Grok Is Done

Grok writes its artifacts to its scratch dir (`~/.agents/develop/<repo-slug>/`) and makes one local commit in the worktree (regression test + minimal fix + refactor, per the brief):

- **Debug summary** — the run's final report: symptom, root cause found, the hypothesis that held, `fix_attempts` count, the regression test that now passes.
- **Guardrails check** — confirmation the red-flag list was checked and no rationalization was accepted.
- **Red-flag stops**: if Grok hit a red flag (3+ failed fix attempts → architecture question, or a stop it could not resolve), it surfaces it in the final report rather than guessing.

Read the report and `git -C <worktree_path> log --oneline -3` to confirm the commit landed. If Grok reports a red-flag stop or exits non-idle with an error, report it verbatim to the user and stop — do not retry, do not hand-debug the issue yourself.

Report to the user: "Grok Build finished the debugging run. Root cause: <...>. Fix committed in <worktree_path> (<sha>). Regression test: <...>."

Then proceed to Step 2.
