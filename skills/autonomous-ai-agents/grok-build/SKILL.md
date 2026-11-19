---
name: grok-build
description: "Delegates coding and multi-agent orchestration to the local Grok Build CLI over the OmniRoute gateway (model myomniroute, not an xAI subscription) via Orca CLI worktrees. Hermes delegates exclusively through Orca CLI (`orca worktree create ... --agent grok` and `orca terminal send`) — never running grok directly in a headless terminal. Use when a coding task should go to Grok instead of being implemented inline, or when authoring Rhai workflows. Sibling of the orca skill: orca owns the worktrees and terminals; this defines the Grok agent surface inside them."
when-to-use: "Use when the user asks to build a feature, refactor, review a PR, or fix issues via Grok Build; when a coding task should be delegated to Grok instead of implemented inline; or when the user wants to author a Rhai workflow, automate a multi-agent pipeline, or runs /create-workflow, /implement, /planner, /execute-plan. Observed user phrasing: '/implement paths cek dpc rules', '/implement ... buat pr untuk perbaiki template dari PRD', '/planner file palse redesign rules aes ... remove all legacy', 'fix doc violations in crate', 'find any segfault error in my environment and clean it', 'we need to spawn sub agent to make all FRD becoming real FRD'."
argument-hint: "<task> [-p <prompt>] [-m <model>] [-c] [-s <session> | -r | --continue] [--output-format <fmt>] [--always-approve] [--no-alt-screen] [--cwd <path>] [--max-turns <n>]"
---

# Grok Build

Delegate coding tasks to Grok Build: Grok reads files, writes code, runs shell commands, spawns subagents, and manages git workflows inside Orca CLI worktrees using the OmniRoute gateway.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Verify the gateway first: `curl -s -o /dev/null -w '%{http_code}\n' "$OMNIROUTE_URL/v1/models"` must return 200. | Check gateway probe endpoint returns HTTP 200 before executing runs. |
| R2 | Auth exclusively via gateway key; never run `grok login` or set `XAI_API_KEY`. | Confirm `OMNIROUTE_KEY` is present and xAI subscription keys are unset. |
| R3 | Delegate through Orca CLI worktrees (`--agent grok`) and never run bare `grok -p` in scratch directories. | Verify Orca worktree exists and agent slot is configured. |
| R4 | Select one orchestration mode per task: headless `-p` for one-shots or interactive PTY/tmux for multi-turn. | Check task configuration for single-mode invocation with `--cwd` set. |
| R5 | Re-read `~/.agents/config.toml` before relying on model provider configurations. | Verify live provider and model blocks in config.toml. |
| R6 | Do not rely on `tui-idle` as progress signal; verify git diff, git status, and full test suite in the worktree. | Inspect `git diff <base>..HEAD` and test results in worktree directory. |
| R7 | Break large refactors into multi-round headless runs keyed on shrinking symbol grep counts. | Measure symbol occurrences after each round and write focused follow-up briefs. |

## Routing

| Reference | Purpose |
|-----------|---------|
| [`references/flags-and-tui.md`](references/flags-and-tui.md) | Full flag tables, sessions, TUI cheatsheet, and dashboard commands |
| [`references/delegation-scenarios.md`](references/delegation-scenarios.md) | Delegation recipes: read-only audit notes, PR review, and parallel issue fixing across worktrees |
| [`references/workflow-authoring.md`](references/workflow-authoring.md) | Authoring and editing `.rhai` workflows: procedure, smoke-check, and language reference |
