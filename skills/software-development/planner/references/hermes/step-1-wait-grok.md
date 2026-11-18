# Step 1: Wait for Grok to Finish

Grok Build runs the full write → review → revise loop itself — `plan-doc-writer` and `plan-doc-reviewer` subagents inside its own skill — driven by its `grok/` references. Hermes waits and does nothing else.

## Wait

Poll with `orca terminal read --terminal <handle> --cursor <cursor> --limit 1000 --json` until the session is idle. plan loops can run many rounds; use `orca terminal wait --terminal <handle> --for tui-idle --timeout-ms 60000 --json` and retry with a larger timeout while `satisfied: false`.

- First read: use `--cursor 0`. The JSON response reports `result.terminal.nextCursor` (the paging token for the next read) and `result.terminal.status` (`running` | `exited` | `unknown`).
- Subsequent reads: pass the previous `nextCursor` as `--cursor` so only new output since that read is returned. Stop paging when `nextCursor` is null or unchanged from `latestCursor`.
- `limit` defaults to 120 for tail previews; use `--limit 1000` for long agent responses.
- `orca terminal status --terminal <handle>` is **not** a valid subcommand (returns `invalid_argument`). Use `terminal wait --for tui-idle` to test idle and `terminal read` to drain output.
- **Silent-loop pitfall:** Grok's write→review→revise loop can run many rounds while the terminal emits no visible output for minutes at a time. Do not treat silence as failure or completion. Cross-check progress by listing `~/.agents/develop/<repo-slug>/plan/` and comparing `plan-doc-*` mtimes between polls; a changing mtime means the loop is still active. Do not send text while waiting (see step-0 rule).
- **Cleanup pitfall:** Grok's final step removes `plan-review-*` and `plan-summary-*` from the plan dir, leaving only `plan-doc-*`. Confirm 0 open issues by reading the review file *before* it disappears; once cleanup completes, rely on the last observed review state plus the presence of the final plan doc.

### Automated Polling Script

Execute this loop in `terminal` (set `timeout=600`):

```bash
ORCA="${ORCA_CLI_COMMAND:-$(command -v orca-ide || echo "$HOME/.local/bin/orca-ide")}"
cursor=0
while true; do
  wait_res=$("$ORCA" terminal wait --terminal "<handle>" --for tui-idle --timeout-ms 60000 --json 2>/dev/null || true)
  satisfied=$(echo "$wait_res" | jq -r '.result.satisfied // false' 2>/dev/null || echo "false")
  if [[ "$satisfied" == "true" ]]; then
    echo "Terminal reached tui-idle."
    break
  fi
  read_res=$("$ORCA" terminal read --terminal "<handle>" --cursor "$cursor" --limit 1000 --json 2>/dev/null || true)
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

Grok writes artifacts to its scratch dir (`~/.agents/develop/<repo-slug>/plan/`):

- **plan document**: `plan-doc-<PLAN_ID>.md` — the polished doc including the `## PR Plan` section (this survives Grok's cleanup).
- **Summary**: `plan-summary-<PLAN_ID>.md` — key decisions, open questions, PR plan.
- **Review**: `plan-review-<PLAN_ID>.md` — the final review file; must show 0 open issues when the loop exits.

The run id appears in Grok's terminal output. Read the summary first, then confirm the review file shows 0 open issues **before Grok's cleanup removes it**. If any issue carries `Status: needs-user-input`, that is an open decision for the user — surface it before proceeding to Step 2. If Grok reports failure or exits non-idle with an error, report it verbatim to the user and stop — do not retry, do not hand-write the document yourself.

Report to the user: "Grok Build finished the plan run. <N> review rounds, 0 open issues (or: <K> issues need your input). plan doc: <path>."

Then proceed to Step 2.
