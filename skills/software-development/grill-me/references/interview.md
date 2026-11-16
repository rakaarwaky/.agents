# Interview — Grill Me method

**Goal:** Interview the plan relentlessly until every branch is resolved and every open question has a recorded answer in the plan doc.

Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. If a question can be answered by exploring the codebase, explore the codebase instead of asking.

## Steps

1. **Open the plan.** Read the plan or design document supplied in `<plan or design to grill>`. List every open question, unresolved decision, and dependency branch.
2. **Branch walk.** For each branch, walk its full depth. Resolve dependencies between decisions one-by-one before moving to the next branch.
3. **Codebase-first probing.** For each question, check whether the codebase answers it. If yes, record the answer from the codebase; if no, record it as a user-facing question.
4. **Record answers.** Write every answer into the plan doc, keyed to its question, so nothing stays unrecorded.
5. **Stop.** Re-read the plan doc. If any open question lacks a recorded answer, return to step 2. Otherwise stop.

## Completion

- Every branch of the design tree walked; dependencies between decisions resolved one-by-one.
- Grep for unanswered questions in the plan doc returns zero (machine-checkable).
- Questions answerable from the codebase were answered by exploring it, not by asking the user.
- Max 5 interview rounds; max 10 files touched; no repeated question (scope ceiling).
- Interview stops when every open question has a recorded answer in the plan doc.
