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

## Host Cleanup

Run `sdc host cleanup` on any temporary files under `scratch_dir` that should not persist (e.g. `interview_tree_file`, `resolved_decisions_file`, `open_questions_file` if they were working files). Keep `interview_summary_file` as the durable record.

Missing paths are skipped silently; the exit code reports any unlink failures. If cleanup exits non-zero, report the failure but do not treat the interview as failed.

## Report

> Interview complete. Summary: <interview_summary_file>. Cleanup: <exit code>.

Stop. Do not proceed further.
