# Step 2 — Fix main CI failures (sweep lane)

Run when step 1 found a repo whose default branch CI conclusion is `failure`.

## Step 2.1 — Read the failed log

For each failing repo:

```bash
gh run view <run_id> -R <owner>/<repo> --log-failed
```

Parse the log to identify the root cause: test failure, lint error, build error, dependency drift, or flaky test. Write a one-line summary of the cause.

## Step 2.2 — Fix in an Orca worktree

Start an isolated worker on this repo in a new Orca worktree:

```bash
orca orchestration worker-start --worktree new-child --repo <owner>/<repo> --agent grok --spec "Fix main CI failure on <owner>/<repo>. Run <run_id> failed: <one-line cause>. Create a branch fix/main-ci-<short-slug>, apply the fix, commit with a Conventional Commit, push, and open a PR to <default_branch>. Report the PR URL."
```

This runs as a worker (SOUL.md rule: code work goes to a worker, not done inline). The worker owns the PR it opens until it is ready to merge (checks green, review asks answered). When the worker reports back, record the fix branch and PR URL for this repo.

## Step 2.3 — Maximum fix attempts

If a repo already has an open fix PR from a previous sweep, do not open a second one. Instead report that a fix is already in flight and link it. After 3 fix PRs for the same repo remain unmerged, report to the owner instead of opening more.

## Next

After all failing repos have a fix PR (or are skipped), the pipeline continues with step 3 (check draft PRs) in `sweep/`.