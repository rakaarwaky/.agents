# Interview — Grill Me method

**Goal:** Interview the plan relentlessly until every branch is resolved and every open question has a recorded answer in the plan doc.

Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. If a question can be answered by exploring the codebase, explore the codebase instead of asking the user.

## Lane Structure

This skill follows the Hermes/Grok lane split used by the sibling skills (`implement`, `planner`, `execute-plan`):

- **Hermes lane** (`references/hermes/`) — plans the task brief, creates the Orca worktree with `--agent grok`, drops `/grill-me` into Grok Build, waits for completion, verifies, commits, and reports. Hermes never writes code.
- **Grok lane** (`references/grok/`) — runs inside the Orca worktree: host setup, branch walk, dependency resolution, exit check, cleanup. Grok does the actual interviewing.

Lane selection is determined by the physical attribution signal (`HERMES_AGENT` / `GROK_AGENT` env vars), same as the sibling skills. Read only the winning lane's references.

## Steps

| Step | Reference | Purpose |
| ----: | --- | --- |
| 0 | [`references/grok/step-0-setup.md`](references/grok/step-0-setup.md) | Host setup (`sdc host setup --subdir plan`), shared file paths, orchestrator state, owning repo, workspace memory retrieval |
| 1 | [`references/grok/step-1-branch-walk.md`](references/grok/step-1-branch-walk.md) | Walk every branch of the design tree; codebase-first probing before asking the user |
| 2 | [`references/grok/step-2-dependency-resolution.md`](references/grok/step-2-dependency-resolution.md) | Resolve dependencies between decisions one-by-one; stalemate detection |
| 3 | [`references/grok/step-3-exit-check.md`](references/grok/step-3-exit-check.md) | Exit condition: all branches walked, all dependencies resolved, no open questions, shared understanding reached |
| 4 | [`references/grok/step-4-cleanup.md`](references/grok/step-4-cleanup.md) | Write interview summary; host cleanup of temporary files |

## Completion

- Every branch of the design tree walked; dependencies between decisions resolved one-by-one.
- Grep for unanswered questions in the plan doc returns zero (machine-checkable).
- Questions answerable from the codebase were answered by exploring it, not by asking the user.
- `open_questions` is empty (or remaining questions explicitly escalated to the user).
- Max 5 interview rounds; max 10 files touched; no repeated question (scope ceiling).
- Shared understanding reached; interview summary written to `interview-summary-<INTERVIEW_ID>.md` under the scratch dir; resolved decisions written back into the original plan (`plan_file`); cleanup ran with exit code 0.

## Outputs

1. **Interview summary** — `<scratch_dir>/interview-summary-<INTERVIEW_ID>.md` — full record of branches walked, decisions resolved, dependency chains, and sources.
2. **Improved original plan** — `plan_file` (the document you passed in) updated with every resolved decision, its answer, dependency chain, and source. Original content preserved; only new `grill-me` result sections are added.

## Routing

Hermes lane (plan/spawn/wait/verify/ship):

| Step | Reference | Purpose |
| ----: | --- | --- |
| 0 | [`references/hermes/step-0-plan-and-spawn.md`](references/hermes/step-0-plan-and-spawn.md) | Plan the brief; create Orca worktree with `--agent grok`; drop `/grill-me` |
| 1 | [`references/hermes/step-1-wait-grok.md`](references/hermes/step-1-wait-grok.md) | Wait for Grok to finish the interview; read summary and artifacts |
| 2 | [`references/hermes/step-2-verify-and-ship.md`](references/hermes/step-2-verify-and-ship.md) | Verify (summary exists, all branches walked, lint gate non-positive); commit |
| 3 | [`references/hermes/step-3-final-report.md`](references/hermes/step-3-final-report.md) | Flush memory patterns; final report to the user |

## Host Integration

The interview uses the `sdc` host helper for per-repo artifact management:

- `sdc host setup --subdir plan` creates `~/.agents/develop/<repo-slug>/plan/` and returns `{python, scratch_dir, run_id}`. The `run_id` (8 hex chars) is stored as `INTERVIEW_ID`.
- All interview artifacts live under `scratch_dir`: `interview-tree-<INTERVIEW_ID>.md`, `resolved-decisions-<INTERVIEW_ID>.md`, `open-questions-<INTERVIEW_ID>.md`, `interview-summary-<INTERVIEW_ID>.md`.
- `sdc host cleanup` removes temporary files under `scratch_dir` at the end of the interview; the durable summary is kept.