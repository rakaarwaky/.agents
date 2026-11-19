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
