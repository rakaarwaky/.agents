---
name: orca
description: "Orca CLI agent environment: Orca-managed worktrees, folder contexts, terminals, repos, automations and cron jobs, embedded browser, artifacts, and skill sharing via the orca CLI; visible local app windows via orca computer; iOS and Android emulator control; Linear ticket work; per-workspace environment recipes; multi-agent orchestration with DAGs and decision gates. Use for $orca-cli, Orca worktree, child worktree, spawn codex/claude in a worktree, read/wait/send Orca terminal, handoff/handover/give this to another agent, Orca browser, orca artifacts, share skills, scheduled agent tasks or cron jobs, visible GUI windows, booted iOS Simulator or Android emulator, linked Linear issue, per-workspace environment recipe setup, multi-agent DAG coordination. Observed user phrasing: 'build the worktree in orca', 'worktree deleted from disk / recreate worktree', 'why isn't it showing in orca IDE', 'check all open PRs', 'resolve conflicts in another worktree', orca cli-commands, orca config-system."
when-to-use: "Use for any Orca CLI agent-environment task. Load references/cli.md for worktrees, terminals, repos, automations, artifacts, skill sharing, and the embedded browser; references/automations.md for scheduled agent runs and cron jobs; references/computer-use.md for visible GUI windows; references/emulator.md for a booted iOS Simulator; references/emulator-android.md for an adb-connected Android emulator or phone; references/linear.md for Linear ticket work; references/per-workspace-env.md for per-workspace environment recipes; references/orchestration.md for supervised multi-agent coordination with DAGs and decision gates. Also matches observed user phrasing: 'build the worktree in orca', 'worktree deleted from disk / recreate worktree', 'why isn't it showing in orca IDE', 'check all open PRs', 'resolve conflicts in another worktree'."
argument-hint: "open --json | skills get <skill-name> [--json] [--reference <path>] | <command> [<flags>]"
---

# Orca CLI Agent Environment

Unified control surface for Orca-managed worktrees, terminal execution, GUI computer-use, mobile emulators, Linear integrations, and multi-agent DAG orchestration.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Resolve CLI executable once via precedence: `ORCA_CLI_COMMAND` > `orca-dev` > `orca-ide` on Linux > `orca`; never run bare `/usr/bin/orca`. | Verify resolved CLI path is not the GNOME screen reader before running commands. |
| R2 | Load version-matched guide via `ORCA skills get <skill-name> --json` before executing unfamiliar commands. | Check skill schema or help flags before executing complex operations. |
| R3 | Treat `runtime_unavailable` as transient; retry after a brief pause and never run `ORCA open` to retry commands. | Confirm `ORCA open` is only called if Orca is truly not running. |
| R4 | Configure Grok Build in worktrees using `--agent grok --no-parent` and enforce single orchestration mode per worktree. | Verify worktree creation flags and slot mode configuration. |
| R5 | Never rely solely on `tui-idle`; verify worktree progress using `git diff`, `git log`, and full test execution. | Inspect worktree directory status and test outputs directly on disk. |
| R6 | Maintain strict separation between full handoff (disengage after acceptance) and supervised orchestration (drive via DAG gates). | Check orchestration type and prevent overlapping control calls. |
| R7 | Run headless Grok invocations strictly inside the created Orca worktree context using `--cwd`. | Verify execution directory is the root of the managed worktree. |

## Routing

| Scenario | Reference | Purpose |
|---|---|---|
| Worktrees, folder contexts, terminals, repos, automations, artifacts, skill sharing, embedded browser | [`references/cli.md`](references/cli.md) | Core CLI operations and worktree management |
| Scheduled automations and cron jobs | [`references/automations.md`](references/automations.md) | Periodic jobs, triggers, and automations |
| Visible local app windows (native apps, browsers, webviews) | [`references/computer-use.md`](references/computer-use.md) | Local window automation and computer use |
| Booted iOS Simulator on macOS | [`references/emulator.md`](references/emulator.md) | iOS Simulator controls and app lifecycle |
| adb-connected Android emulator or phone | [`references/emulator-android.md`](references/emulator-android.md) | Android emulator and device workflows |
| Linear ticket work | [`references/linear.md`](references/linear.md) | Linear issue updates and tracker sync |
| Per-workspace environment recipes | [`references/per-workspace-env.md`](references/per-workspace-env.md) | Environment configuration and setup recipes |
| Supervised multi-agent coordination, DAGs, decision gates | [`references/orchestration.md`](references/orchestration.md) | Orchestration DAGs and multi-agent coordination |
| Large briefs and long-context guidance | [`references/large-briefs.md`](references/large-briefs.md) | Context management for multi-file briefs |
