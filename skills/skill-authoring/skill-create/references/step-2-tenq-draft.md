# Create — Step 2: Draft the 10Q answers

**10Q:** Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10

**Goal:** the job description becomes ten scored answers with named homes before a single file is written.

The questions, the 0–2 rubric, and the gate live in `../../skill-improve/references/step-14-tenq-standard.md`. Read it once here; do not restate it in the answer sheet.

## Procedure

1. **One capability test.** State the deliverable in one sentence. If it needs two different WHATs, stop and propose two skills — one skill per invocation (Rules: 10Q answers precede prose).
2. **Copy the sheet.** Copy `../template/tenq-answers.md` and fill all ten answers. Write bullets, not prose; each answer names paths, commands, numbers, or steps.
3. **Ground the answers in the repo.** Read the files the new skill will operate on (its config, one existing example of the artifact it produces) before answering Q4, Q5, and Q6. An answer invented without reading the repo scores 1 at best.
4. **Fill silence with defaults.** Anything the job description does not state takes the conservative default below and is logged as `assumed` in the sheet. Never default to a wider scope.
5. **Score the draft** with the rubric and record the total. Below the gate → apply defaults again, then ask exactly one question naming the missing fact and the question ID. This is the only blocking prompt in the create run; every other step is autonomous (Rules: safety model).
6. **Carry the sheet forward.** Step 3 builds the trigger fields from Q1 + Q2; step 6 places each answer at its home; step 7 re-scores the written artifact.

## Defaults when the job is silent

| Q | Conservative default |
| --- | --- |
| Q1 | Done = the repo's own check command exits 0 (`sac lint`, `cargo test`, `pytest`); never an adjective |
| Q2 | Environment = the directory or file the job names; if none is named, require it as a precondition and stop when absent |
| Q3 | Audience = the maintainer of this repo; English body; follow the conventions already in the tree |
| Q4 | Inputs = the project config plus one existing example of the artifact being produced |
| Q5 | Tools = what the repo already uses; forbidden: new dependencies without permission |
| Q6 | Read the existing pattern → write the artifact → register it → run the check command → report |
| Q7 | Maximum 3 files touched; maximum 2 self-repair iterations; no edits outside the named target; destructive actions go to `_archive/` first |
| Q8 | At minimum: target already exists → stop and report the conflict; precondition missing → stop |
| Q9 | Files written under the target path, plus a changed-files table in chat |
| Q10 | At minimum: check command fails → read the error → at most 2 attempts → stop and report expected vs actual |

## Completion

- The answer sheet holds ten answers, each with its owning home named, and every default used is logged as `assumed`.
- The draft total meets the gate in `../../skill-improve/references/step-14-tenq-standard.md`, or the one blocking question has been asked and answered.
- Q1 states one deliverable; a two-WHAT job was split instead of drafted.
