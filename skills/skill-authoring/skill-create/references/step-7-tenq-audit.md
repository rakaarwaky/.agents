# Create — Step 7: Score the written skill against the 10Q gate

**10Q:** Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10

**Goal:** the artifact on disk — not the draft — passes the 10Q gate before the mechanical verify step runs.

Step 2 scored the answers; this step scores what actually landed in the files. An answer that never reached a file scores 0. Rubric, gate arithmetic, and the score-block shape: `../../skill-improve/references/step-14-tenq-standard.md`.

## Procedure

1. **Read back the artifact.** Read `<SKILL_DIR>/SKILL.md` and every file under `<SKILL_DIR>/references/`. Score from the files, never from the draft sheet.
2. **Run the probes.**

   ```bash
   python3 <skill-improve-dir>/scripts/audit_probes.py <SKILL_DIR>
   ```

   The script reports unclaimed questions, body-shape drift, unlinked references, dangling links, and unresolved rule citations. Exit 0 = no findings; exit 1 = fix the findings; exit 2 = path error, re-resolve `<SKILL_DIR>`.

3. **Score ten questions with evidence.** Each row cites `path:line` or a command. Place-check every answer: a Q7 ceiling buried in a step file instead of Rules is a placement defect, not a missing answer — move it, then score.
4. **Apply the gate.** PASS → continue to `step-8-verify.md`. FAIL → run the patch cycle in `../../skill-improve/references/step-15-tenq-diagnosis.md` against the new skill, then re-score. The cycle budget is the gate's.
5. **Budget exhausted below the gate** → leave the files on disk, carry `Gate: FAIL` and the remaining gap list into the report, and stop. Do not announce the skill as ready (Rules: 10Q gate is hard).

## Dry-run variant

With `--dry-run`, score the draft sheet from step 2 instead of the artifact, label the block `source: draft`, and stop after the report. No probes are run against disk state that was never written.

## Completion

- Ten questions scored from the files on disk, each with `path:line` or command evidence.
- The probe script exited 0, or every finding it printed was fixed or reported.
- The score block carries total, gate verdict, cycles used, and remaining gaps; a FAIL verdict is carried into `step-8-verify.md` unchanged.
