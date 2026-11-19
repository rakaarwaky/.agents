---
name: grill-me
description: Relentlessly interviews a plan or design until a shared understanding is reached, and writes resolved decisions back into the original plan.
when-to-use: "Use when asked to grill, interview, or stress-test a plan, design, or decision tree until every branch is resolved. Triggers: 'grill this plan', 'interview this design', 'stress-test my approach'."
argument-hint: "<plan or design to grill>"
---

# Grill Me

Relentlessly interview a plan, architectural design, or decision tree until every dependency and branch is resolved, recording decisions into the source plan.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Determine execution lane strictly from physical attribution environment variables (`HERMES_AGENT=1` or `GROK_AGENT=1`); stop if unset. | Verify agent attribution environment variable prior to routing. |
| R2 | Read only the winning lane's step files; never read or load files from the alternate lane. | Confirm references inspected match active execution lane. |
| R3 | Probe codebase for answers before querying the user whenever a question can be resolved from code. | Check that codebase exploration occurs prior to asking user questions. |
| R4 | Walk every branch of the design tree, resolving decision dependencies one-by-one until shared consensus is reached. | Verify that all dependency chains in the interview tree are fully resolved. |
| R5 | Update the target plan document preserving original structure and appending resolved decision outcomes. | Check git diff on original plan to confirm non-destructive append of findings. |
| R6 | Limit interview scope to at most 5 interview rounds, at most 10 files touched, and never repeat a question. | Verify round counter <= 5 and no duplicated questions exist. |
| R7 | If the target plan document is missing or unreadable, stop and report the error; if a question repeats, treat it as resolved. | Verify handling of missing file error and duplicate question resolution. |
| R8 | Retrieve the workspace memory snapshot at Grok Step 0 and use its top patterns as probe seeds in the branch walk; flush the run's plan-weakness patterns back at Hermes Step 3. Degrade gracefully when memory is empty or unavailable. | Verify the snapshot step ran (or a degradation note was logged) and the flush reported stats or "no new patterns". |

## Routing

| Step | Reference | Purpose |
| ----: | --------- | ------- |
| Method | [`references/interview.md`](references/interview.md) | Core interview procedure: branch walk, dependency chains, and exit criteria |
| Grok 0 | [`references/grok/step-0-setup.md`](references/grok/step-0-setup.md) | Host setup (`sdc host setup --subdir plan`), shared file paths, orchestrator state, owning repo, workspace memory retrieval |
| Grok 1 | [`references/grok/step-1-branch-walk.md`](references/grok/step-1-branch-walk.md) | Walk every branch of the design tree; codebase-first probing before asking the user |
| Grok 2 | [`references/grok/step-2-dependency-resolution.md`](references/grok/step-2-dependency-resolution.md) | Resolve dependencies between decisions one-by-one; stalemate detection |
| Grok 3 | [`references/grok/step-3-exit-check.md`](references/grok/step-3-exit-check.md) | Exit condition: all branches walked, all dependencies resolved, no open questions |
| Grok 4 | [`references/grok/step-4-cleanup.md`](references/grok/step-4-cleanup.md) | Write interview summary; host cleanup of temporary files |
| Hermes 0 | [`references/hermes/step-0-plan-and-spawn.md`](references/hermes/step-0-plan-and-spawn.md) | Plan the brief; create Orca worktree with `--agent grok`; drop `/grill-me` |
| Hermes 1 | [`references/hermes/step-1-wait-grok.md`](references/hermes/step-1-wait-grok.md) | Wait for Grok to finish the interview; read summary and artifacts |
| Hermes 2 | [`references/hermes/step-2-verify-and-ship.md`](references/hermes/step-2-verify-and-ship.md) | Verify summary exists, all branches walked, lint gate clean; commit |
| Hermes 3 | [`references/hermes/step-3-final-report.md`](references/hermes/step-3-final-report.md) | Flush memory patterns; final report to the user |
