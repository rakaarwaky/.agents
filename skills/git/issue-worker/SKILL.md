---
name: issue-worker
description: "issue → PR: analyzes and groups open GitHub issues, verifies claims at HEAD, asks user decisions via quiz, isolates work in Orca worktrees, delegates implementation to new Grok Build session(s) via /implement, verifies fixes, and pushes draft PRs. Unified flow for Hermes and Grok."
when-to-use: "Use when resolving open GitHub issues into PRs (/issue-worker <latest|oldest> <N> or /issue-worker <issue-numbers>), triaging and grouping issues by subsystem, verifying bug reproduction at HEAD, delegating fixes to Grok Build via /implement in Orca worktrees, or opening draft PRs. Never creates issues (handled by /issue-maker) and never auto-merges."
argument-hint: "<latest|oldest> <N> | <issue-numbers>"
---

# Issue Worker — issue → PR

End-to-end workflow for resolving GitHub issues: parse issue hints, verify claims at HEAD, group related issues into cohesive cohorts while separating disjoint tasks, delegate implementation to new Grok Build session(s) via `/implement` in isolated Orca worktrees, independently verify fixes, and push branches to open draft PRs. The orchestrator workflow is completely unified whether invoked from Hermes or Grok. Never merges.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **Unified orchestrator flow.** Orchestration logic is identical whether executed by Hermes or Grok: the orchestrator coordinates issue resolution, triage, grouping, worktree management, verification, and PR creation; all implementation is delegated to new Grok Build session(s) via `/implement`. | Confirm caller orchestrates and spawns new Grok sessions in Orca worktrees without lane divergence. |
| R2 | **Verify at HEAD before deciding.** Never trust issue labels, audit dates, or commit message claims alone. Inspect the cited file:line at HEAD and check git log for existing fixes before planning fixes. Close `fixed-on-main` issues immediately with concrete evidence comments. | Verified code inspection or reproduction output documented prior to scheduling implementation. |
| R3 | **Interactive decision quiz.** If open ambiguities or architectural decisions exist across issues, collect all questions into a single interactive quiz with recommended options first before implementation. | All unresolved questions presented in a single quiz; user choices recorded as brief constraints. |
| R4 | **Issue grouping and isolation.** Actionable issues are grouped into cohorts based on shared files, subsystems, or root causes for a single `/implement` pass. Disjoint or conflicting issues are strictly isolated into separate worktrees. | Cohort groupings documented with shared file justification; disjoint issues assigned distinct worktrees. |
| R5 | **Orchestrator-implementer separation.** The orchestrator (Hermes or Grok) drives coordination and never edits repo code directly. Each implementation group is delegated to a new Grok session running `/implement` in an isolated Orca worktree. | Zero direct code commits on orchestrator branch; implementation confined to child Grok sessions in worktrees. |
| R6 | **Build isolation per worktree.** Each worktree maintains dedicated build artifact and cache directories (e.g. `CARGO_TARGET_DIR`, `.venv`, isolated cache dirs) to avoid concurrency locks and cache corruption. | Worktree configuration verifies dedicated isolated target/cache paths. |
| R7 | **Independent verification.** A child Grok session's summary is a self-report. The orchestrator independently verifies file:line changes, confirms clean git status, and re-executes reproduction and test commands in the worktree. | Reproduction command re-executed and exit code 0 confirmed inside worktree before marking verified. |
| R8 | **Safe push and draft PRs.** Pushes use `git push --force-with-lease origin <branch>` and open draft PRs via `gh pr create --draft`. PR descriptions explicitly cite all grouped issues. Auto-merge is forbidden. | Push uses `--force-with-lease`; PR is created in draft mode referencing all cohort issues. |
| R9 | **Concurrency and wave ceilings.** Maximum concurrent worktrees ≤ 10. Groups beyond the wave limit execute in subsequent waves after active worktrees complete. | Active concurrent worktrees do not exceed 10. |
| R10 | **Worktree teardown & final report.** Verified worktrees are marked `in-review` during inspection, then retired via `orca worktree rm` after push and PR creation. Orchestrator synthesizes a comprehensive final report. | Worktrees cleaned up via `orca worktree rm`; final summary reports all issues, groups, and PRs. |
| R11 | **Zero-issue graceful halt.** If the repository has issues disabled, contains zero open issues, or no issues match the query, report the exact status cleanly, spawn zero worktrees, and halt without error. Suggest `/issue-maker` when spec docs exist. | Query returns zero matching issues or issues disabled; run halts immediately with clean status. |
| R12 | **Terminal handle resilience.** Stale or segfaulted terminal handles are re-resolved via `orca terminal list` filtered by `worktreeId`, and direct worktree-path inspection (`git -C "$WT_PATH" …`) is an acceptable fallback for independent verification. | Any `terminal_handle_stale` / segfault triggers a re-resolve-and-retry before failing. |

## Routing

| Step | Reference | Purpose |
| ---- | --------- | ------- |
| Step 0 | [`references/step-0-resolve-issues.md`](references/step-0-resolve-issues.md) | Parse issue hints, verify GitHub auth, query issues, and fetch live metadata |
| Step 1 | [`references/step-1-triage-and-verify.md`](references/step-1-triage-and-verify.md) | Verify issues against HEAD, close fixed-on-main issues with evidence, run decision quiz |
| Step 2 | [`references/step-2-grouping-and-planning.md`](references/step-2-grouping-and-planning.md) | Cluster related issues into cohesive /implement groups, separate conflicting issues, formulate briefs |
| Step 3 | [`references/step-3-spawn-grok-implement.md`](references/step-3-spawn-grok-implement.md) | Create Orca worktree per group, wait for TUI idle, dispatch /implement to new Grok session |
| Step 4 | [`references/step-4-wait-and-verify.md`](references/step-4-wait-and-verify.md) | Poll Grok sessions to completion, independently verify code changes and test runs in worktrees |
| Step 5 | [`references/step-5-ship-and-report.md`](references/step-5-ship-and-report.md) | Push verified branches, open draft PRs, tear down worktrees, and synthesize final report |
