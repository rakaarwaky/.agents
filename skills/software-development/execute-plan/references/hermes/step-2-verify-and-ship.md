# Step 2: Verify & Ship

Hermes owns the final git and PR operations. Read Grok's state file and artifacts, verify the final branch is sound, and confirm the PR is in the right place.

## 2a: Read the State File & Artifacts

The state file `exec-plan-<PLAN_ID>.json` is written at the start of the run and is frequently NOT updated — it commonly still reads `status: "initializing"` with every PR `pending` and `final_review_passed: false` even after Grok completed the whole loop and opened the PR. Do not gate on its `status` / `final_review_passed` fields; treat them as advisory only. The authoritative record of what happened is Grok's final rendered screen (`orca terminal read --terminal <handle> --screen`) plus the real `git` and `gh pr` state on `origin`. Read the state file only for the static inputs (`linearized_order`, `dag`, `max_concurrent`) and the per-PR `exec-summary-*` / `exec-review-*` markdown artifacts, which Grok does write reliably.

Cross-check the real outcome from origin, not the state file:

- `git fetch origin <final_branch>` then `git log --oneline origin/<final_branch> -<N>` — the branch and its commits are the truth.
- `gh pr list --head <final_branch> --json url,isDraft,state` or `gh pr view <n>` — confirms the PR Grok opened.
- Grok's final screen block names the PR URL, final branch, and CI results — use it as the human-readable summary.

## 2b: Verify the Final Branch

In the main clone (or the worktree if the final branch lives there):

```
git -C <path> fetch origin <final_branch>
git -C <path> log --oneline <final_branch> -<N>   # N = completed PR count + 1
```

- Confirm the final branch exists on `origin` with `final_commit_sha` as its tip (Grok pushed it per `grok/step-10-stack-assembly.md`).
- Run the repo's local gate on the final branch tip (per AGENTS.md / repo lint commands). A dirty-tree green is not proof; check `git status --short` is clean first.
- If the gate fails on the committed SHA, that is a verification defect, not a Grok flake — report it to the user with the exact failing commands and do not push a fix yourself.

## 2c: Handle Partial Failures

If the run is incomplete (Grok's screen shows failure, or the branch/PR is absent on origin):

- Read `deferred_issues` and any failed PR ids from Grok's per-PR `exec-review-*` artifacts and final screen.
- Report to the user which PRs did not make it into the final branch and why, and suggest `/execute-plan --resume <PLAN_ID>` for a Grok-driven retry of just the failed/skipped PRs.
- Do NOT hand-assemble the missing PRs into the final branch yourself.

## 2d: Report

Report to the user:

> Plan executed via Grok Build in <worktree_path>. <N> PRs completed, <M> failed, <K> skipped. Final branch: <final_branch>. PR: <url> (draft). <D> issues deferred. Post-merge action: `"$ORCA" worktree rm --worktree <final_orca_worktree_id> --force --json`.

Then proceed to Step 3.
