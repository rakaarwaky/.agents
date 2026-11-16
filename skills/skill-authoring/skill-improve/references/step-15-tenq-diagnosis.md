# Improve — Step 15: Symptom diagnosis and the patch cycle

**Goal:** a failed question or an observed misbehavior becomes the smallest patch at the fact's owning home, and the re-score proves it closed.

The repair half of the quality gate. The questions, rubric, and cycle budget live in `step-14-tenq-standard.md`; this file owns the symptom-to-question map, the cycle procedure, and the worked patches.

## Symptom → gap map

One symptom maps to one or two questions. Never respond to a symptom by rewriting the whole skill.

| Observed symptom | Gap | Patch owner |
| --- | --- | --- |
| Skill never triggers | When & where | Frontmatter; `../../skill-create/references/step-2-drafting.md` |
| Skill triggers on the wrong tasks | When & where | `when-to-use:` negative scope, same step |
| Agent asks basic questions back | What & why, From where | Rules success-metric row + the gathering step |
| Agent edits the wrong files | When & where, How far | Rules ceilings row (scope + forbidden paths) |
| Agent installs dependencies unasked | By what means | Rules tools row (forbidden clause) |
| Agent loops without stopping | How far, What & why | Rules ceilings row (iteration cap) + success metric |
| Agent is stuck when a command fails | Whether, How come | The failing step's branch and fallback tables |
| Output format is wrong | What kind | Rules report-shape row + the verify step |
| Tone or language drifts | Who | Rules audience & tone row |
| Result is correct but useless | What & why | Success metric: it measures the wrong outcome |
| Agent deletes or damages existing work | How far | Forbidden-actions clause; archive-before-destroy |
| `sac lint` reports `reference-not-linked` | How | Routing table row for the orphaned reference |
| A retired flag still governs a step | Whether | Rules safety-model row + every step mentioning the flag (Rules: interface changes ripple) |
| Two files state the same fact | How | The losing copy; keep the owner per `step-10-information-distribution.md` |

## The cycle

Run once per failing question set, not once per question. The budget is the gate's (`step-14-tenq-standard.md`).

1. **OBSERVE** — record the symptom verbatim and the invocation that produced it. No symptom, no patch: a question scored 1 with no observed failure is still patched, but the report says `source: audit`, not `source: run`.
2. **MAP** — pick the row above; write down the question and the owning home before opening an editor.
3. **PATCH** — edit only that home. If the owner is a step file, never edit the body; if the owner is Rules, never restate it in the step (Rules: one home per fact).
4. **REGRESS** — re-run three scenarios against the patched skill: happy path, edge case, deliberate error (a missing precondition or a failing check command). Then re-run `sac lint` and the coverage probe. A patch that fixes the happy path and breaks the error path is not a patch.
5. **RE-SCORE** — score the patched questions with evidence and recompute the gate. Do not add a `version:` key: the parser ignores it (Rules: Grok Build parser limits). The version record is the commit message plus the report's change list.

## Worked patches

| Before (score 1) | After (score 2) | Question |
| --- | --- | --- |
| "Fix it if there is an error" | "IF `sac lint` exits non-zero with `name-format` → rename directory and frontmatter `name:` to lowercase-hyphen; IF a check fails twice → stop and report" | How come |
| "Do not change too much" | "Maximum 3 files: the new module, its registration, its test. Forbidden: editing sibling skills, `git add -A`, new dependencies" | How far |
| "Make sure the quality is good" | "Done = `sac lint` exit 0 and `grep -c '^## ' SKILL.md` returns 2" | What & why |
| "Read the relevant files first" | "Read `SKILL.md`, `references/step-0-overview.md`, and one sibling skill as the pattern reference" | From where |
| "Report the result" | "Report a changed-files table, the lint result, and the quality score block; write files only under `<SKILL_DIR>/`" | What kind |

## Stop conditions

- Budget exhausted (`step-14-tenq-standard.md`) → emit the remaining gap list with the owning home for each, and stop. Do not claim done.
- A patch would touch a skill outside the resolved scope (Rules: run ceilings) → do not apply it; report it as an out-of-scope finding.
- The same question fails the same way twice → the diagnosis was wrong; re-map from the symptom table instead of retrying the same edit.

## Completion

- Every failing question has a mapped symptom row, a named owning home, and an applied patch or a reported reason it was not applied.
- The three regression scenarios and `sac lint` were re-run after the last patch.
- The re-scored block is emitted with cycles used and remaining gaps.