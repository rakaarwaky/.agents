# Step 1: Wait for Grok to Finish

Grok Build runs the full parallel-persona review itself — per-mode file-list collection, auto persona selection, per-persona subagent fan-out, per-persona review files, aggregation — driven by its `grok/` references. Hermes waits and does nothing else.

## Wait

Grok Build's TUI process stays alive after finishing the task — the terminal reports `status: running` and `tui-idle` may never fire, so a `tui-idle`-only poll can hang the full timeout even though the review is already done. **Detect completion by artifacts on disk, not by terminal status alone.** After dropping the task, poll for the per-persona review files and the summary file appearing in the scratch dir (`ls -lt <scratch_dir>/grok-review-<REVIEW_ID>-*`), then verify the set is complete (one file per selected persona + the summary). When the artifacts are present and the summary's `## Totals` line is filled, Grok is done regardless of `terminal.status`.

Use `orca terminal wait --terminal <handle> --for tui-idle --timeout-ms 60000 --json` only as a secondary signal; if `satisfied: false` persists but artifacts exist on disk, treat the run as complete and proceed to Step 2.

Poll the terminal with `orca terminal read --terminal <handle> --cursor <cursor> --limit 1000 --json` for progress text.

- First read: use `--cursor 0`. The JSON response reports `result.terminal.nextCursor` (the paging token for the next read) and `result.terminal.status` (`running` | `exited` | `unknown`).
- Subsequent reads: pass the previous `nextCursor` as `--cursor` so only new output since that read is returned. Stop paging when `nextCursor` is null or unchanged from `latestCursor`.
- `limit` defaults to 120 for tail previews; use `--limit 1000` for long agent responses.
- `orca terminal status --terminal <handle>` is **not** a valid subcommand (returns `invalid_argument`). Use `terminal wait --for tui-idle` to test idle and `terminal read` to drain output.
- Do NOT send text while waiting.

### Automated Polling Script

This loop breaks on either `tui-idle`, terminal `exited`, or artifacts appearing on disk — whichever fires first. The disk check is the reliable terminator because Grok's TUI stays `running` after finishing.

```bash
ORCA="$(command -v orca || echo /home/raka/.config/orca/linux-orca-cli-shim/orca)"
SCRATCH="<scratch_dir>"
REVIEW_ID="<review_id>"
EXPECTED_PERSONAS=<N>
cursor=0
while true; do
  # Artifact-based completion check (primary)
  artifact_count=$(ls "$SCRATCH"/grok-review-"$REVIEW_ID"-*.md 2>/dev/null | grep -v summary | wc -l)
  summary_ok=$([ -f "$SCRATCH/grok-review-summary-$REVIEW_ID.md" ] && echo 1 || echo 0)
  if [[ "$artifact_count" -ge "$EXPECTED_PERSONAS" && "$summary_ok" == "1" ]]; then
    echo "Artifacts complete: $artifact_count persona files + summary."
    break
  fi

  wait_res=$("$ORCA" terminal wait --terminal "<handle>" --for tui-idle --timeout-ms 30000 --json 2>/dev/null || true)
  satisfied=$(echo "$wait_res" | jq -r '.result.satisfied // false' 2>/dev/null || echo "false")
  if [[ "$satisfied" == "true" ]]; then
    echo "Terminal reached tui-idle."
    break
  fi
  read_res=$("$ORCA" terminal read --terminal "<handle>" --cursor "$cursor" --limit 100 --json 2>/dev/null || true)
  new_cursor=$(echo "$read_res" | jq -r '.result.terminal.nextCursor // empty' 2>/dev/null || echo "")
  [[ -n "$new_cursor" ]] && cursor="$new_cursor"
  status=$(echo "$read_res" | jq -r '.result.terminal.status // empty' 2>/dev/null || echo "")
  if [[ "$status" == "exited" ]]; then
    echo "Terminal process exited."
    break
  fi
  sleep 5
done
```

## When Grok Is Done

Grok writes artifacts to the per-user scratch dir resolved by `scripts/host.py setup` (`result.scratch_dir` — on this host it is `$TMPDIR/grok-raka`, e.g. `/home/raka/.hermes/cache/scratch/grok-raka`, NOT `/tmp/grok-raka`, because `TMPDIR` points at the Hermes cache scratch dir). Do not assume `/tmp`; read the path from `host.py setup` output. Artifacts are keyed by `REVIEW_ID`:

- **Per-persona review files**: `grok-review-<REVIEW_ID>-<persona>.md` for every auto-selected persona.
- **Summary file**: `grok-review-summary-<REVIEW_ID>.md` — aggregate counts and top issues.

The run id (`REVIEW_ID`) is an 8-hex-character identifier (e.g. `cca7ab30`) printed in Grok's terminal output or visible in artifact filenames. Locate artifacts with:

```bash
ls -lt <scratch_dir>/grok-review-* 2>/dev/null
```

If Grok reports failure or exits non-idle with an error, report it verbatim to the user and stop — do not retry, do not hand-review the target yourself.

Report to the user: "Grok Build finished the <mode> review of <target>. <N>/<P> personas completed (<M> errored). <bugs> bugs, <suggestions> suggestions, <nits> nits. Summary: <path>."

Then proceed to Step 2.

## Completion

- Grok terminal reached `tui-idle` or `exited` status, OR all per-persona review files + the summary file are present on disk with the summary's `## Totals` line filled.
- Artifacts located at the `host.py setup` scratch dir with correct `REVIEW_ID` prefix.
- Brief progress report emitted to user.
- Proceed to Step 2.