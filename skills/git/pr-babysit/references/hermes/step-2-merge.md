# Step 2: Verify Merge & Retire Worktree (only when `ship` is `true`)

Grok performs the merge in Step 7 via Mergify queue (or direct merge fallback). Hermes verifies the merge landed live on GitHub and retires the worktree.

## Verify the Merge

Re-query GitHub live to confirm the PR was merged:

```bash
gh pr view <number> --json state,mergedAt,mergeMethod -q '{state: .state, merged: .mergedAt, method: .mergeMethod}'
```

- If `state` is `MERGED`:
  - Update state file: `last_status: "merged"`, remove the PR entry from the watchlist.
  - Report: "PR <number> merged and branch deleted."
- If `state` is still `OPEN`:
  - Read Grok's final report to see why it wasn't merged (active freeze, unmet Depends-On, timeout, etc.).
  - If Grok reported merge-ready but didn't execute the merge, Hermes executes the fallback:
    ```bash
    gh pr merge <number> --squash --delete-branch
    ```

## After the Merge

- Comment on the linked issue (when one is linked) with the PR link and a one-line explanation.
- **Tear down the Grok worktree** (created in Step 0e):

  ```bash
  "$ORCA" worktree rm --worktree <worktree_id> --force --json
  ```

  A `not found` response counts as success (teardown is idempotent).

## Report

> PR <number> merged (<queue|direct-squash>) and branch deleted. Worktree retired. <Issue comment posted, if applicable.>

Then proceed to Step 3.
