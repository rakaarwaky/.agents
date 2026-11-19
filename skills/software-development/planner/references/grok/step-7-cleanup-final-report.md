# Step 7: Final Report & Cleanup

## Final Report

Present a final summary to the user containing:

1. The absolute path to `<plan_doc_file>`.
2. Total review rounds (`round_count`).
3. Issue breakdown (`total_issues_by_severity`).
4. Resolved open questions (or state "None").
5. Next action: run `/execute-plan <plan-doc-file-path>` to implement the PR plan.

## Cleanup

Do NOT delete the plan summary or review files. Hermes (Step 1 of the Hermes lane) reads these files to verify the run:

- `plan-summary-<run_id>.md` — the plan summary
- `plan-review-<run_id>.md` — the plan review

These files are the verification gate. Grok must not delete what Hermes consumes.

**Hermes owns post-verification cleanup** — Hermes Step 3 runs `sdc host cleanup` on these files after it has read them and produced the final report.

The plan document itself is kept.