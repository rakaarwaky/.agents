# Step 2: Verify & Ship

Verify Grok's interview work before any commit or final report.

## Verification Checks

1. **Interview summary exists** — `interview-summary-<INTERVIEW_ID>.md` is present under `scratch_dir` and contains the shared understanding.
2. **All branches walked** — the summary lists every branch of the design tree as walked.
3. **All dependencies resolved** — every decision in the summary has its `depends_on` chain resolved.
4. **No open questions** — `open_questions` is empty, or any remaining questions were explicitly escalated to the user.
5. **Shared understanding confirmed** — the summary states shared understanding was reached (or records user confirmation).
6. **Lint gate** — run `lint-arwaky-cli report .` from the worktree and compare against the start-turn baseline recorded in Step 0. A positive Delta is a regression: stop, revert, re-run. Zero or negative delta passes.

## Scope Audit

Run `git -C <worktree_path> status --short` and diff touched paths against the resolved scope. Any out-of-scope path → revert it yourself (`git -C <worktree_path> checkout -- <path>` / `rm` for untracked) and tell the user what you reverted.

## Commit

If all checks pass, commit the changes in the worktree (one commit). Hermes owns the commit; Grok never commits. Do not push and do not open a PR unless the user asks.

## Report

> Verified grill-me interview at <worktree_path>. Interview ID: <INTERVIEW_ID>. Shared understanding reached. Commit: <sha>.

Proceed to Step 3 (Final Report).
