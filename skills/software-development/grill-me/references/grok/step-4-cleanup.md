# Step 4: Cleanup

When shared understanding is reached, clean up temporary interview artifacts and write the final summary.

## Write the Interview Summary

Write `interview_summary_file` (`<scratch_dir>/interview-summary-<INTERVIEW_ID>.md`) containing:

- Repo: `<repo-path>`
- Interview ID: `<INTERVIEW_ID>`
- Branches walked: `<N>`
- Decisions resolved: `<M>` (list each with its answer and dependency chain)
- Open questions: none (or list any escalated to the user)
- Shared understanding: reached / not reached

## Improve the Original Plan

Write the resolved decisions back into `plan_file` (the original plan document). For each entry in `decisions_resolved`, append or update the corresponding section of `plan_file` with:

- The decision and its answer
- The dependency chain (`depends_on`)
- The source of the answer (codebase path/line, or user answer)

Do not delete or restructure existing content in `plan_file` — only add the resolved decisions as new sections or inline updates, clearly marked as `grill-me` interview results. Keep the original plan intact plus the improvements.

## Host Cleanup

Run `sdc host cleanup` on any temporary files under `scratch_dir` that should not persist (e.g. `interview_tree_file`, `resolved_decisions_file`, `open_questions_file` if they were working files). Keep `interview_summary_file` as the durable record.

Missing paths are skipped silently; the exit code reports any unlink failures. If cleanup exits non-zero, report the failure but do not treat the interview as failed.

## Report

> Interview complete. Summary: <interview_summary_file>. Cleanup: <exit code>.

Stop. Do not proceed further.
