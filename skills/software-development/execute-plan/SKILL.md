---
name: execute-plan
description: "Executes a PR Plan DAG end-to-end: Hermes validates the plan and drops /execute-plan into Grok Build (Grok runs parallel Orca worktrees, implementers, the 5-reviewer panel, fix loops, and final assembly), then Hermes verifies the final branch and ships the PR."
when-to-use: "Use for /execute-plan <plan-doc-path> [--resume <PLAN_ID>], execute plan, run the plan, implement the plan, or after /planner (or /plan) produces a PR plan."
argument-hint: "<plan-doc-path> | --resume <PLAN_ID>"
---

# Execute Plan Skill

Orchestrate a PR Plan DAG end-to-end across parallel Orca worktrees, driving implementers, reviewer panels, fix loops, and stack assembly.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Determine execution lane strictly from physical attribution environment variables (`HERMES_AGENT=1` or `GROK_AGENT=1`); stop if unset. | Verify agent attribution environment variable prior to routing. |
| R2 | Read only the winning lane's step files; never read or load files from the alternate lane. | Confirm references inspected match active execution lane. |
| R3 | Validate the PR Plan DAG using `sdc validate-plan` before dispatching worktrees or subagents. | Check plan validation command exit code before spawning implementers. |
| R4 | Enforce modular branch creation and linearized merge ordering to prevent integration conflicts. | Verify branch preparation sequence follows DAG topological sort. |
| R5 | Require full reviewer panel sign-off (5 reviewers, 0 open issues) on every modular branch before stack assembly. | Inspect reviewer verdict files for zero blocking issues prior to merge. |
| R6 | Read Grok's rendered screen via `--screen`, not the PTY line stream, to detect completion. | `--cursor` paging returns only one line with cursor stuck at `1`; `--screen` shows the agent's rendered output including the final report and `EXECUTE_PLAN_COMPLETE` sentinel. |
| R7 | Confirm completion from screen content, not from `tui-idle` alone. | `tui-idle` returns `satisfied: true` mid-loop between renders — idle is not completion. |
| R8 | Verify the final branch on `origin`, not from `exec-plan-*.json` state file alone. | State file is written at start and often stale; authoritative truth: `git fetch origin <branch>` + `gh pr view <n>`. |
| R9 | Per-PR `exec-summary-*`/`exec-review-*` markdown artifacts may not exist on disk even when state file references them. | Treat them as advisory; rely on final screen block + origin git/gh state instead. |
| R10 | Treat poll-script heartbeat ticks as internal progress, not user turns — one short status line, then end the turn; do not re-read the screen on every tick. | A fresh `--screen` read per heartbeat wastes turns without new signal; spend one only past the expected runtime budget to confirm Grok is still progressing. |
| R11 | Treat `terminal wait --for tui-idle` failures as busy, not errors — only `terminal read` failures count toward the poll-script CLI-error abort threshold. | `wait` timeouts mid-loop mean Grok is still processing; aborting on them kills a run that is progressing normally. |
| R12 | Subagent lifecycle lines ("turn cancelled", "session shut down", subagent completed) do not mean Grok failed. | Grok continues with reviewers and later PRs after an implementer subagent finishes; only a literal failure report or a terminal exit without a final report means failure. |
| R13 | For sequential DAGs (`max_parallelism=1`) with several PRs and fix loops, budget 4+ hours of polling — PR-1 alone (implementer + 5-reviewer panel + fix rounds) routinely runs past 40 minutes. | Under-budgeting the poll deadline reports a false timeout on a run that is still progressing. |
| R14 | When a Grok session disconnects or times out mid-DAG, resume with `--resume <PLAN_ID>` instead of restarting the plan. | Resume keeps completed PR branches and reviewer verdicts, avoiding duplicate work. |
| R15 | Before starting a new `sdc pool grok` poll loop, kill any existing `sdc pool grok` processes for the same terminal handle. | Multiple concurrent loops compete for the same Orca terminal session and cause `tcsetattr` / `bash: tcsetattr: Inappropriate ioctl for device` errors. |

## Routing

| Step | Reference | Purpose |
| ----: | --------- | ------- |
| Hermes 0 | [`references/hermes/step-0-plan-and-spawn.md`](references/hermes/step-0-plan-and-spawn.md) | Validate the DAG with `sdc validate-plan`, plan brief, create Orca worktree, drop command |
| Hermes 1 | [`references/hermes/step-1-wait-grok.md`](references/hermes/step-1-wait-grok.md) | Wait for Grok to finish execution loop, read state file and artifacts |
| Hermes 2 | [`references/hermes/step-2-verify-and-ship.md`](references/hermes/step-2-verify-and-ship.md) | Verify Grok final branch, handle partial failures, report status |
| Hermes 3 | [`references/hermes/step-3-final-report.md`](references/hermes/step-3-final-report.md) | Flush new issue patterns to workspace memory, final report to user |
| Grok 0 | [`references/grok/step-0-setup.md`](references/grok/step-0-setup.md) | Setup, state, personas, Orca protocol, invocation |
| Grok 1 | [`references/grok/step-1-memory-retrieval.md`](references/grok/step-1-memory-retrieval.md) | Past issues briefing |
| Grok 2 | [`references/grok/step-2-tool-detection.md`](references/grok/step-2-tool-detection.md) | Detect Orca and gh |
| Grok 3 | [`references/grok/step-3-parse-dag.md`](references/grok/step-3-parse-dag.md) | Parse PR Plan DAG |
| Grok 4 | [`references/grok/step-4-dag-processing.md`](references/grok/step-4-dag-processing.md) | Sort and linearize DAG for merge order |
| Grok 5 | [`references/grok/step-5-branch-prep.md`](references/grok/step-5-branch-prep.md) | Prepare local modular branches |
| Grok 6 | [`references/grok/step-6-execution-loop.md`](references/grok/step-6-execution-loop.md) | Run parallel implementer subagents |
| Grok 7 | [`references/grok/step-7-review.md`](references/grok/step-7-review.md) | Run per-PR reviewer panel and fix loop |
| Grok 8 | [`references/grok/step-8-failure-handling.md`](references/grok/step-8-failure-handling.md) | Handle failed or skipped PRs |
| Grok 9 | [`references/grok/step-9-resumption.md`](references/grok/step-9-resumption.md) | Resume previous run |
| Grok 10 | [`references/grok/step-10-stack-assembly.md`](references/grok/step-10-stack-assembly.md) | Final branch assembly, final review, push 1 PR |
| Grok 11 | [`references/grok/step-11-cleanup.md`](references/grok/step-11-cleanup.md) | Cleanup worktrees and artifacts |
| Grok 12 | [`references/grok/step-12-memory-flush.md`](references/grok/step-12-memory-flush.md) | Flush memory |
| Grok 13 | [`references/grok/step-13-final-report.md`](references/grok/step-13-final-report.md) | Final report |
