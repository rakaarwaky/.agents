---
name: grill-me
description: Relentlessly interviews a plan or design until a shared understanding is reached.
when-to-use: "Use when asked to grill, interview, or stress-test a plan, design, or decision tree until every branch is resolved. Triggers: 'grill this plan', 'interview this design', 'stress-test my approach'."
argument-hint: "<plan or design to grill>"
disable-model-invocation: true
---

# Grill Me

## Rules

| ID | Rule | Covers | Check |
|----|------|--------|-------|
| R1 | One-shot interview. Walk every branch of the design tree once, resolving dependencies between decisions one-by-one, until every open question has an answer recorded in the plan doc. | Method ownership | Full method lives in [`references/interview.md`](references/interview.md); body points to it and never restates it |
| R2 | Codebase-first answers. If a question can be answered by exploring the codebase, explore the codebase instead of asking the user. | Evidence sourcing | Never ask the user a question that codebase exploration can answer |
| R3 | Stop condition. The interview stops when every open question has a recorded answer in the plan doc. | Success metric | Grep the plan doc for unanswered questions returns zero |
| R4 | Scope ceiling. Max 5 interview rounds, max 10 files touched, never ask the same question twice. | Scope & iteration ceilings | Round counter ≤ 5; touched-files set ≤ 10; no repeated question |
| R5 | Failure fallback. IF the plan doc is missing or unreadable -> stop and report the missing file. IF the same question repeats -> treat it as resolved and move on. | Branching & failure fallback | Named cause + concrete recovery command per branch |

## Routing

| File | Purpose |
|------|---------|
| [`references/interview.md`](references/interview.md) | The relentless interview method: branch walk, dependency resolution, codebase-first probing, stop condition. |
