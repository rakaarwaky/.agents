# Step 2: Verify & Validate the Hand-off

Hermes owns the verification. Read Grok's artifacts, confirm the review loop actually closed, and validate the PR plan so `/execute-plan` can safely consume it.

## 2a: Read the Artifacts

Read all three files from the scratch dir:

- `design-doc-<DESIGN_ID>.md`
- `design-summary-<DESIGN_ID>.md`
- `design-review-<DESIGN_ID>.md`

Cross-check:

- **0 open issues**: the final `review_file` must show no issue with `Status: open`. Grok's cleanup removes `design-review-*` and `design-summary-*` from the plan dir at finalization, so read and record the review state *before* cleanup completes; once cleanup finishes, the presence of `design-doc-*` plus the last-observed "Approved"/"0 open issues" state is the verification evidence. Any `needs-user-input` status is an open decision — surface it to the user and stop (do not proceed to the hand-off validation until the user decides; Grok will re-run the loop on a fresh drop if the user wants it closed).
- **wontfix discipline**: any `wontfix` status should carry a substantive technical explanation in the review file — not a bare "won't fix". If one is bare, flag it.
- **Scope held**: the design doc and summary must not contain implementation code, source-file edits, branches, commits, or PR links — the design-only boundary (Grok lane step 1: the repo is read-only for the writer subagents). Any source-tree drift in the worktree (`git -C <worktree_path> status --short` should be clean or scratch-dir-only) means the boundary was violated; report it.

## 2b: Validate the PR Plan

This is the hand-off gate for `/execute-plan`. Extract the `## PR Plan` section from the design doc and run it through the plan validator:

```
sdc validate-plan <path to a file containing the PR Plan section>
```

`sdc` lives at `~/.local/bin/sdc`. (If the design doc is the whole file, point the validator at it directly — the validator reads the `## PR Plan` section from the file.)

- Exit `0` with `valid == true` and `errors == []`: `linearized_order`, `level_assignments`, `nodes`, `pr_count`, and `max_parallelism` are authoritative. Record them — they are the hand-off facts for the user.
- Exit `1`: DAG validation failed. Read stdout JSON and report the first error.
- Exit `2`: usage/IO failure. Read stderr and report the first error.
- Exit `4`: parse failure (missing section, no entries, malformed PR/dep fields). Read stderr JSON and report the first error.
- On any non-zero exit: stop. Do not hand-edit the PR plan to make it parse.

## 2c: Report

Report to the user:

> Design verified. 0 open issues (or: <K> need your input — listed). PR plan: <N> PRs, <L> levels, max parallelism <P>. Design doc: <abs path>. Ready for /execute-plan <abs path>.

Then proceed to Step 3.
