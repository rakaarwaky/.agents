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

Grok writes artifacts to `/tmp/grok-<username>/` (resolved by `scripts/host.py` via `scratch_dir()`), keyed by `REVIEW_ID`:

- **Per-persona review files**: `grok-review-<REVIEW_ID>-<persona>.md` for every auto-selected persona.
- **Summary file**: `grok-review-summary-<REVIEW_ID>.md` — aggregate counts and top issues.

The run id (`REVIEW_ID`) is an 8-hex-character identifier (e.g. `cca7ab30`) printed in Grok's terminal output or visible in artifact filenames. After Grok exits, locate artifacts with:

```bash
ls -lt /tmp/grok-<username>/grok-review-* 2>/dev/null
```

If Grok reports failure or exits non-idle with an error, report it verbatim to the user and stop — do not retry, do not hand-review the target yourself.

Report to the user: "Grok Build finished the <mode> review of <target>. <N>/<P> personas completed (<M> errored). <bugs> bugs, <suggestions> suggestions, <nits> nits. Summary: <path>."

Then proceed to Step 2.
