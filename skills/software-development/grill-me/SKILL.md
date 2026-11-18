---
name: grill-me
description: Relentlessly interviews a plan or design until a shared understanding is reached, and writes resolved decisions back into the original plan.
when-to-use: "Use when asked to grill, interview, or stress-test a plan, design, or decision tree until every branch is resolved. Triggers: 'grill this plan', 'interview this design', 'stress-test my approach'."
argument-hint: "<plan or design to grill>"
disable-model-invocation: true
---
# Grill Me

You orchestrate a relentless interview of a plan or design end-to-end. This file is the lane identification step only; the working method lives in `references/hermes/` and `references/grok/`.

## Global Rules

The lane is determined from a physical signal, not by self-identification. Each agent's launcher stamps a fixed attribution env var into every command it runs; the model cannot set these.

```bash
if [[ -n "${HERMES_AGENT:-}" ]]; then echo HERMES
elif [[ -n "${GROK_AGENT:-}" ]]; then echo GROK
else echo UNSET; fi
```

- `HERMES` → **Hermes lane.** Read `references/hermes/`. Stop.
- `GROK` → **Grok lane.** Read `references/grok/`. Stop.
- `UNSET` → stop and report. Do not guess the lane.

Marker provenance:

- **Hermes** re-exports `AI_AGENT=hermes-agent` and `HERMES_AGENT=true` on every command.
- **Grok Build** runs with `GROK_AGENT=1`.

Read only the winning lane's references. Do not read the other lane's.

## Rules

- **One-shot interview.** Walks every branch of the design tree, resolving dependencies between decisions one-by-one, until a shared understanding is reached. The full method lives in [`references/interview.md`](references/interview.md).
- **Codebase-first answers.** If a question can be answered by exploring the codebase, explore the codebase instead of asking.

## Host Integration

The interview uses the `sdc` host helper for per-repo artifact management:

- `sdc host setup --subdir plan` creates `~/.agents/develop/<repo-slug>/plan/` and returns `{python, scratch_dir, run_id}`. The `run_id` (8 hex chars) is stored as `INTERVIEW_ID`.
- All interview artifacts live under `scratch_dir`: `interview-tree-<INTERVIEW_ID>.md`, `resolved-decisions-<INTERVIEW_ID>.md`, `open-questions-<INTERVIEW_ID>.md`, `interview-summary-<INTERVIEW_ID>.md`.
- `sdc host cleanup` removes temporary files under `scratch_dir` at the end of the interview; the durable summary is kept.

## Outputs

1. **Interview summary** — `<scratch_dir>/interview-summary-<INTERVIEW_ID>.md` — full record of branches walked, decisions resolved, dependency chains, and sources.
2. **Improved original plan** — `plan_file` (the document you passed in) updated with every resolved decision, its answer, dependency chain, and source. Original content preserved; only new `grill-me` result sections are added.

## Routing

Grok lane (setup → branch walk → dependency resolution → exit check → cleanup):

| Step | Reference | Purpose |
| ----: | --- | --- |
| 0 | [`references/grok/step-0-setup.md`](references/grok/step-0-setup.md) | Host setup (`sdc host setup --subdir plan`), shared file paths, orchestrator state, owning repo |
| 1 | [`references/grok/step-1-branch-walk.md`](references/grok/step-1-branch-walk.md) | Walk every branch of the design tree; codebase-first probing before asking the user |
| 2 | [`references/grok/step-2-dependency-resolution.md`](references/grok/step-2-dependency-resolution.md) | Resolve dependencies between decisions one-by-one; stalemate detection |
| 3 | [`references/grok/step-3-exit-check.md`](references/grok/step-3-exit-check.md) | Exit condition: all branches walked, all dependencies resolved, no open questions, shared understanding reached |
| 4 | [`references/grok/step-4-cleanup.md`](references/grok/step-4-cleanup.md) | Write interview summary; host cleanup of temporary files |

Hermes lane (plan/spawn/wait/verify/ship):

| Step | Reference | Purpose |
| ----: | --- | --- |
| 0 | [`references/hermes/step-0-plan-and-spawn.md`](references/hermes/step-0-plan-and-spawn.md) | Plan the brief; create Orca worktree with `--agent grok`; drop `/grill-me` |
| 1 | [`references/hermes/step-1-wait-grok.md`](references/hermes/step-1-wait-grok.md) | Wait for Grok to finish the interview; read summary and artifacts |
| 2 | [`references/hermes/step-2-verify-and-ship.md`](references/hermes/step-2-verify-and-ship.md) | Verify (summary exists, all branches walked, lint gate non-positive); commit |
| 3 | [`references/hermes/step-3-final-report.md`](references/hermes/step-3-final-report.md) | Flush memory patterns; final report to the user |
