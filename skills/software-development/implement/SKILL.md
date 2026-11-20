---
name: implement
description: "Run the implement → review → fix loop for a single small-to-medium task in one Orca worktree: Hermes plans the brief, drops /implement into Grok Build (Grok runs the full loop with its 5-reviewer panel), then Hermes verifies, commits, pushes, and opens the PR."
when-to-use: "Use when asked to implement, build, add a feature, fix a bug, or via the /implement slash command. Best for tasks that fit in one worktree. For multi-PR stacks with dependencies, use /execute-plan instead."
argument-hint: "<task-description>"
---

# Implement Skill

Execute a comprehensive implement-review-fix loop for a single task within an Orca worktree, orchestrating a 5-reviewer specialist panel and enforcing lint progress gates.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Determine execution lane strictly from physical attribution environment variables (`HERMES_AGENT=1` or `GROK_AGENT=1`); stop if unset. | Verify agent attribution environment variable prior to routing. |
| R2 | Read only the winning lane's step files; never read or load files from the alternate lane. | Confirm references inspected match active execution lane. |
| R3 | Never yield conversation turns passively after dispatching `/implement`; poll terminal status actively until completion. | Confirm active wait loop in Hermes lane until Orca terminal is idle or exited. |
| R4 | Enforce lint progress gates bookending start and end of turn with `lint-arwaky-cli report .`; reject positive deltas. | Verify zero or negative issue delta between turn start and turn end. |
| R5 | Require all 5 specialist reviewers to reach consensus with zero open issues before proceeding to PR creation. | Check merged reviewer findings report zero blocking issues. |
| R6 | Read Grok's rendered screen via `--screen`, not the PTY line stream, to detect completion. | `--cursor` paging returns only one line with cursor stuck at `1`; `--screen` shows the agent's rendered output including the final report and completion sentinel. |
| R7 | Confirm completion from screen content, not from `tui-idle` alone. | `tui-idle` returns `satisfied: true` mid-loop between renders — idle is not completion. |
| R8 | Verify the final branch on `origin`, not from state/result files alone. | State files can be stale; authoritative truth: `git fetch origin <branch>` + `gh pr view <n>`. |
| R9 | Per-PR summary/review markdown artifacts may not exist on disk even when referenced. | Treat them as advisory; rely on final screen block + origin git/gh state instead. |

## Routing

| Step | Reference | Purpose |
| ----: | --------- | ------- |
| Hermes 0 | [`references/hermes/step-0-plan-and-spawn.md`](references/hermes/step-0-plan-and-spawn.md) | Plan brief from task description, create Orca worktree with `--agent grok`, drop `/implement` |
| Hermes 1 | [`references/hermes/step-1-wait-grok.md`](references/hermes/step-1-wait-grok.md) | Wait for Grok implement-review-fix loop, read summary and review files |
| Hermes 2 | [`references/hermes/step-2-verify-and-ship.md`](references/hermes/step-2-verify-and-ship.md) | Verify Grok work (0 open issues, clean gate), commit, push, open PR |
| Hermes 3 | [`references/hermes/step-3-final-report.md`](references/hermes/step-3-final-report.md) | Flush new issue patterns to workspace memory, final report to user |
| Grok 0 | [`references/grok/step-0-setup.md`](references/grok/step-0-setup.md) | Host setup, shared file paths, orchestrator state, owning repo, worktree |
| Grok 1 | [`references/grok/step-1-specialization.md`](references/grok/step-1-specialization.md) | Fixed 5-reviewer panel; build reviewer configs and announce |
| Grok 2 | [`references/grok/step-2-memory.md`](references/grok/step-2-memory.md) | Past-issues briefing from workspace memory file |
| Grok 3 | [`references/grok/step-3-implement.md`](references/grok/step-3-implement.md) | Spawn implementer in worktree, prepare reviewer focus areas |
| Grok 4 | [`references/grok/step-4-review.md`](references/grok/step-4-review.md) | Launch all 5 reviewers in parallel with specialized prompts |
| Grok 5 | [`references/grok/step-5-merge.md`](references/grok/step-5-merge.md) | Merge review findings, evaluate exit conditions and stalemates |
| Grok 6 | [`references/grok/step-6-fix.md`](references/grok/step-6-fix.md) | Resume implementer to address identified issues |
| Grok 7 | [`references/grok/step-7-rereview.md`](references/grok/step-7-rereview.md) | Re-run reviewers in parallel on updated changes |
| Grok 8 | [`references/grok/step-8-memory-flush.md`](references/grok/step-8-memory-flush.md) | Flush accumulated patterns to workspace memory |
| Grok 9 | [`references/grok/step-9-stack-assembly.md`](references/grok/step-9-stack-assembly.md) | Push branch and open PR with commit hygiene |
| Grok 10 | [`references/grok/step-10-final-report.md`](references/grok/step-10-final-report.md) | Final report and cleanup of temporary artifacts |
