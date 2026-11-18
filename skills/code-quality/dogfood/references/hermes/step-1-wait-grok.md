# Step 1: Wait for Grok to Finish

Grok Build runs the full exploratory QA pipeline itself — plan, explore per target type, evidence capture, categorization, report — driven by its `grok/` references. Hermes waits and does nothing else.

## Wait

Worktree case: poll with `orca terminal read --terminal <handle> --cursor <cursor> --limit 1000 --json` until the session is idle.

- First read: use `--cursor 0`. The JSON response reports `result.terminal.nextCursor` (the paging token for the next read) and `result.terminal.status` (`running` | `exited` | `unknown`).
- Subsequent reads: pass the previous `nextCursor` as `--cursor` so only new output since that read is returned. Stop paging when `nextCursor` is null or unchanged from `latestCursor`.
- `limit` defaults to 120 for tail previews; use `--limit 1000` for long agent responses.
- Use `orca terminal wait --terminal <handle> --for tui-idle --timeout-ms 60000 --json` and retry with a larger timeout while `satisfied: false`.
- `orca terminal status --terminal <handle>` is **not** a valid subcommand (returns `invalid_argument`). Use `terminal wait --for tui-idle` to test idle and `terminal read` to drain output.
- Do NOT send text while waiting.

### Automated Polling Script (Worktree case)

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

Headless case: the `grok -p` call (launched inside the worktree/scratch directory, never in the Hermes session directly) is foreground/blocking — it returns when Grok finishes. No polling.

## When Grok Is Done

Grok writes `{output_dir}/report.md` (inside the worktree for repo targets, or under `--cwd` for headless runs). The report is built from `templates/dogfood-report-template.md` with:

- Per-issue evidence (screenshots, transcripts, log lines) — file paths relative to the output dir.
- Severity categorization per `grok/shared.md`'s issue taxonomy.
- The target type's specific issue categories from the matching step-1 reference.

Read the report. If Grok reports failure or exits with an error, report it verbatim to the user and stop — do not retry, do not hand-explore the target yourself.

Report to the user: "Grok Build finished the dogfood run over <target> (<type>). Report: <output_dir>/report.md — <N> issues found (<breakdown by severity>)."

Then proceed to Step 2.
