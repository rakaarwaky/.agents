# Step 1: Wait for Grok to Finish

Grok Build runs the full execution loop itself — per-PR worktrees, implementer subagents, the 3-reviewer panel per PR, fix rounds, failure cascades, final assembly — driven by its own `grok/` references. Hermes waits and does nothing else.

## Wait

A full-screen TUI agent (Grok) renders to its terminal *screen*, not to the line stream. `orca terminal read --cursor <n>` returns only the PTY line stream — for a TUI agent that is just the launching shell echo (one line, `nextCursor` stuck at `1`), never the agent's rendered output. The `EXECUTE_PLAN_COMPLETE` sentinel lives on the rendered screen and is ONLY visible via `orca terminal read --screen`. A cursor-paged poll therefore never sees the sentinel and will spin until its failure cap — reporting a false failure on a run that actually succeeded.

Poll with BOTH: use `orca terminal wait --terminal <handle> --for tui-idle --timeout-ms 60000 --json` to detect idle, and `orca terminal read --terminal <handle> --screen --json` to inspect the rendered screen for the sentinel and the final report. A multi-PR plan routinely runs 15–25 minutes; background the loop (see below), do not run it in the foreground.

- `terminal wait --for tui-idle` returns `result.satisfied: true` both while Grok is mid-turn between renders and when it is truly done — idle alone does not mean finished. Confirm completion by finding `EXECUTE_PLAN_COMPLETE` on the screen, not by idle.

### Automated Polling Script

Run the bundled `scripts/poll_grok.py` with `terminal(background=true, notify=true)` and `timeout` unset (or the max foreground value as a fallback). A multi-PR plan routinely runs past the 600s foreground cap — a foreground invocation exits `124` and the loop dies before Grok finishes. Backgrounding with `notify_on_complete` delivers the result as a new message and keeps the session free.

```
python3 <skill-dir>/scripts/poll_grok.py <terminal_handle> --orca "$ORCA"
```

The script uses `terminal read --screen` (the only read mode that surfaces a TUI agent's rendered output) to detect the `EXECUTE_PLAN_COMPLETE` sentinel, `terminal wait --for tui-idle` to pace the loop, and `python3` JSON parsing (not `jq`, which is not guaranteed on every host). Resolve `$ORCA` the same way as Step 0 (including the AppImage mount probe) and pass it with `--orca`.

If you must inline the loop instead, use `python3 -c 'import sys,json; ...'` for JSON extraction rather than `jq` — but prefer the script; inline `python3 -c` one-liners inside bash substitution can trip security scanners on some hosts.

## When Grok Is Done

Grok writes artifacts to its scratch dir (`~/.agents/develop/<repo-slug>/execute/`):

- **State file**: `exec-plan-<PLAN_ID>.json` — the full DAG state: per-PR status, `commit_sha`, `review_rounds`, `final_branch`, `final_review_passed`, `pr_urls`, `deferred_issues`.
- **Per-PR summaries**: `exec-summary-<PLAN_ID>-<pr-id>.md`.
- **Per-PR merged reviews**: `exec-review-<PLAN_ID>-<pr-id>.md`.
- **Final report**: Grok's terminal output ends with its final report (per `grok/step-13-final-report.md`).

Do NOT trust the state file as proof of completion — it is written at the start and is frequently left at `status: "initializing"` with every PR `pending` even after a fully successful run. Confirm completion from the rendered screen (`terminal read --screen` shows Grok's final report block: PR URL, branch, CI results, `EXECUTE_PLAN_COMPLETE`) and from the actual `git` / `gh pr` state on `origin`, not from `exec-plan-<PLAN_ID>.json`. If Grok reports failure or the terminal exits non-idle with an error, report it verbatim to the user and stop — do not retry, do not hand-assemble the final branch yourself.

Report to the user: "Grok Build finished the execution loop. <worktree_path> state: <N> completed, <M> failed, <K> skipped. Final branch: <final_branch>."

Then proceed to Step 2.
