# Step 6: Summarize and Finalize

Read the final `<plan_doc_file>` and present these sections to the user.

## 6a: Key Decisions

Extract and summarize each decision and its rationale.

## 6b: Open Questions

If an "Open Questions" section exists in the document, present each as a clear question with selectable trade-off options (plus an "Other" option):

- Never resolve these silently; always ask the user.
- If the user answers, resume the writer to incorporate the answers. Skip re-review.
- If empty or missing, skip this section.

## 6c: PR Plan

Present the PR Plan section.

### 6d: Validate PR Plan Format

Run the plan validator to confirm the PR Plan section is well-formed and parseable by `/execute-plan`:

```bash
sdc validate-plan <plan_doc_file>
```

- Exit `0` with `valid == true` and `errors == []`: plan is valid. Report: `PR plan validated: <N> PRs, <L> levels, max parallelism <P>`.
- Exit `1`: DAG validation failed. Read stdout JSON, show the error, and resume the writer to fix the PR Plan section.
- Exit `2`: IO error (file missing/unreadable). Read stderr and stop.
- Exit `4`: parse error (missing section, no entries, malformed heading/dependency). Read stderr JSON, show the error, and resume the writer.

Then continue to Step 7.