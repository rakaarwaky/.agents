# Step 3: Final Report

Report to the user:

1. **PR** — `<number>` (`<title>`), repo.
2. **Fix passes** — total `fix_count`, which checks were fixed in each pass (commit SHAs), which threads were addressed.
3. **Outcome**:
   - `ship: true, merge_method: "queue"` → "Merged via Mergify merge queue to `<base_ref>`, branch deleted."
   - `ship: true, merge_method: "direct"` → "Merged to `<base_ref>` (<squash|auto>), branch deleted."
   - `ship: false` → "Green and ready to merge. Run `/pr-babysit ship on <number>` when you want it landed."
4. **Mergify** (when `mergify_available` is `"configured"`):
   - Queue history: how many queue/dequeue cycles occurred
   - Merge protections checked: freezes, Depends-On, Merge-After status
   - Flaky tests quarantined (if any)
   - CI Insights uploaded (if any)
5. **Open items** — any unfixed failures or unresolved threads from the last pass, with a one-line reason each.
6. **Worktree** — retired (Step 2) or left in place if the run stopped red (post-action: `"$ORCA" worktree rm --worktree <worktree_id> --force --json`).
7. **Watchlist** — the PR entry's final state (`last_status`, removed-if-merged). Suggest re-check cadence or a re-invocation trigger (e.g. "re-run on the next CI failure or new review thread").

Report: "PR babysit complete."
