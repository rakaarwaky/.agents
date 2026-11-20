# Step 1: Wait for Grok to Finish

Grok Build runs the full execution loop itself — per-PR worktrees, implementer subagents, the 5-reviewer panel per PR, fix rounds, failure cascades, final assembly — driven by its own `grok/` references. Hermes waits and does nothing else.

## Wait

Run `sdc pool grok <terminal_handle> --wait` to poll until Grok finishes. The `sdc pool` command is the standardized grok-session poller — it reads the rendered screen (`orca terminal read --screen --json`), paces with `orca terminal wait --for tui-idle`, and detects completion from either the `EXECUTE_PLAN_COMPLETE` sentinel or a final-report shape (PR marker + settled prompt) on an idle screen.

```bash
sdc pool grok <terminal_handle> --wait
```

- Without `--wait`, `sdc pool grok <terminal_handle>` performs a single probe and returns immediately with JSON status.
- With `--wait`, it blocks until completion, failure, or deadline (default 2 hours). Pass `--deadline-hours 4` for sequential DAGs — a 2-hour default can be exhausted by PR-1 alone.
- Exit codes: `0` = success (done), `1` = runtime error (orca CLI failure or terminal exited without final report), `3` = deadline exceeded (status still running, `timed_out=true`).
- Override pacing with `--wait-ms` (default 15000), `--idle-confirm` (default 2), `--tail` (default 50), `--sentinel`, `--orca` (default `orca-ide`).
- Heartbeat progress lines go to stderr; the JSON result goes to stdout.
- Do NOT gate completion solely on the literal `EXECUTE_PLAN_COMPLETE` sentinel — many runs end with a per-PR summary table and a `Draft PR: #N` line plus a `Worked for Xm` footer and never print the sentinel. The poller detects both.
- `tui-idle` returning not-satisfied means Grok is BUSY, not that the poll failed — keep polling. Only a genuine CLI/parse failure counts as an error.
- Run exactly one poll loop at a time. Before starting a fresh loop, kill any existing `sdc pool grok` processes for the same terminal handle.
- Long runtime is not a stall signal — do not escalate, interrupt, or re-spawn before ~90 minutes.

## When Grok Is Done

If the session dies mid-DAG — the screen shows `Turn cancelled because the session shut down` with no PR URL, no `Draft PR` line, and no modular branch pushed — the run is incomplete, not failed. Do NOT hand-assemble the remaining PRs. Re-drop the plan with `--resume <PLAN_ID>` so Grok reuses the completed PR branches and reviewer verdicts already in the worktree:

```
/execute-plan <plan_doc_path> --resume <PLAN_ID>
```

Distinguish a genuine mid-run subagent turnover from a dead session before resuming: a screen line reading `Turn cancelled because the session shut down in Xm` scoped to a *subagent* panel while the parent Grok prompt is still live and emitting new tool calls is normal implementer→reviewer handoff — keep waiting. Only resume when the parent session itself stops producing output.

Grok writes a state file `exec-plan-<PLAN_ID>.json` with the full DAG state: per-PR status, `commit_sha`, `review_rounds`, `final_branch`, `final_review_passed`, `pr_urls`, `deferred_issues`. **The state file MUST be written exclusively to `<scratch_dir>/exec-plan-<PLAN_ID>.json`**, where `scratch_dir` is the absolute path returned by `sdc host setup --subdir execute` (Step 0). If the state file is not found at `<scratch_dir>/exec-plan-<PLAN_ID>.json`, treat it as missing — do NOT search the worktree root or any repo-tracked directory, as that indicates Grok violated the scratch-dir contract. The per-PR `exec-summary-<PLAN_ID>-<pr-id>.md` / `exec-review-<PLAN_ID>-<pr-id>.md` markdown artifacts are written unreliably and are often absent from disk even on a clean run — do not gate verification on their existence; reconstruct the per-PR outcome from the state file's `dag` array plus `git log` on the final branch.

Do NOT trust the state file as proof of completion — it is written at the start and is frequently left at `status: "initializing"` with every PR `pending` even after a fully successful run. Confirm completion from the rendered screen (`terminal read --screen` shows Grok's final report block: PR URL, branch, CI results, `EXECUTE_PLAN_COMPLETE`) and from the actual `git` / `gh pr` state on `origin`, not from `exec-plan-<PLAN_ID>.json`. If Grok reports failure or the terminal exits non-idle with an error, report it verbatim to the user and stop — do not retry, do not hand-assemble the final branch yourself.

Report to the user: "Grok Build finished the execution loop. <worktree_path> state: <N> completed, <M> failed, <K> skipped. Final branch: <final_branch>."

Then proceed to Step 2.
