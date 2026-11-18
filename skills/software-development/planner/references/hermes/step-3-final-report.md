# Step 3: Final Report

Report to the user:

1. **What was planned** — the task restated, and the key decisions from `plan-summary-<PLAN_ID>.md`.
2. **Review loop** — how many rounds it took to reach 0 open issues (from Grok's report), and any `wontfix` decisions with their justifications.
3. **Open questions** — anything the summary flags as unresolved for a later pass.
4. **PR plan** — the validated stats from Step 2: `pr_count`, levels, `max_parallelism`, and `linearized_order` (short form: first/last PR ids is enough unless the user wants the full list).
5. **Files** — absolute paths to `plan_doc_file` and `summary_file` in the scratch dir.
6. **Next step** — the exact command to run next, with the plan doc's absolute path inlined:

   ```
   /execute-plan <abs plan_doc_file>
   ```

7. **Worktree** — left in place (plan runs never commit to the repo, so the worktree holds no repo changes, only the TUI session). Post-action:

   ```
   # Resolve $ORCA (via command -v orca-ide or $ORCA_CLI_COMMAND)
   "$ORCA" worktree rm --worktree <worktree_id> --force --json
   ```

Report: "plan complete."
