---
name: planner
description: "Orchestrates a write-review-revise loop using `plan-doc-writer` and `plan-doc-reviewer` subagents to produce a polished plan document and PR plan."
when-to-use: "Use when asked to write a plan doc, produce a system architecture/spec, or via the `/planner <description>` slash command. Triggers: 'plan a feature', 'plan a feature', 'write a plan doc', 'create technical spec'."
argument-hint: "<description of what to plan>"
---

# Planner Skill

Orchestrate a structured write-review-revise loop using specialized writer and reviewer subagents to produce rigorous architectural plan documents and PR plans.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Determine execution lane strictly from physical attribution environment variables (`HERMES_AGENT=1` or `GROK_AGENT=1`); stop if unset. | Verify agent attribution environment variable prior to routing. |
| R2 | Read only the winning lane's step files; never read or load files from the alternate lane. | Confirm references inspected match active execution lane. |
| R3 | Structure planning as a multi-round write-review-revise loop until reviewer findings reach zero open issues. | Verify exit condition check records zero unresolved reviewer findings. |
| R4 | Validate the final PR plan using the plan validator tool before completing the hand-off to `/execute-plan`. | Check plan validation tool returns clean validation report. |

## Routing

| Step | Reference | Purpose |
| ----: | --------- | ------- |
| Hermes 0 | [`references/hermes/step-0-plan-and-spawn.md`](references/hermes/step-0-plan-and-spawn.md) | Plan brief from description, create Orca worktree with `--agent grok`, drop `/planner` |
| Hermes 1 | [`references/hermes/step-1-wait-grok.md`](references/hermes/step-1-wait-grok.md) | Wait for Grok to finish write-review-revise loop, read plan doc and artifacts |
| Hermes 2 | [`references/hermes/step-2-verify-and-ship.md`](references/hermes/step-2-verify-and-ship.md) | Verify 0 open issues, validate PR plan as `/execute-plan` hand-off gate |
| Hermes 3 | [`references/hermes/step-3-final-report.md`](references/hermes/step-3-final-report.md) | Final report to user with key decisions, stats, and next-step command |
| Grok 0 | [`references/grok/step-0-setup.md`](references/grok/step-0-setup.md) | Host setup, shared file paths, orchestrator state, personas |
| Grok 1 | [`references/grok/step-1-write.md`](references/grok/step-1-write.md) | Spawn writer to draft the plan document |
| Grok 2 | [`references/grok/step-2-review.md`](references/grok/step-2-review.md) | Spawn reviewer to produce structured findings |
| Grok 3 | [`references/grok/step-3-check-exit.md`](references/grok/step-3-check-exit.md) | Exit check, stalemate detection, escalation to user |
| Grok 4 | [`references/grok/step-4-revise.md`](references/grok/step-4-revise.md) | Resume writer to address open issues |
| Grok 5 | [`references/grok/step-5-rereview.md`](references/grok/step-5-rereview.md) | Resume reviewer to re-review revisions |
| Grok 6 | [`references/grok/step-6-summarize.md`](references/grok/step-6-summarize.md) | Synthesize key decisions, open questions, and PR plan |
| Grok 7 | [`references/grok/step-7-cleanup-final-report.md`](references/grok/step-7-cleanup-final-report.md) | Final report and cleanup of temporary artifacts |
