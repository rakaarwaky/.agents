# Step 6 — Merge Protections Check

Run before Step 7 (Merge) when `MERGIFY_AVAILABLE` is `"configured"`. Verify no active protection blocks the merge.

## 1. Scheduled freezes

```bash
mergify freeze list --json 2>/dev/null
```

For each active freeze matching this PR's base branch:

> ⚠️ Active merge freeze: "<reason>"
> Started: <start>, Ends: <end or "no end">
> Exclusions: <list or "none">

If the PR matches an exclusion (e.g. `label=hotfix`), note it and continue. Otherwise stop and report — do not queue.

## 2. Depends-On

```bash
gh pr view <number> --json body -q .body | grep -i '^Depends-On:'
```

For each reference, verify the dependency PR is `MERGED`:

```bash
gh pr view <dep> --json state -q .state
gh pr view <dep> --repo <org/repo> --json state -q .state   # cross-repo
```

Any non-merged dependency → stop and report:

> ⚠️ Blocked by dependency: PR #<dep> is still <state>. Cannot merge.

## 3. Merge-After

```bash
gh pr view <number> --json body -q .body | grep -i '^Merge-After:'
```

Parse the timestamp. If current time < Merge-After time:

> ⚠️ Merge-After: gate opens at <timestamp> (<duration> remaining).

## 4. Stacked PR ordering

```bash
mergify stack list --json 2>/dev/null
```

If the PR is part of a stack and is NOT the bottom PR:

> ⚠️ PR is mid-stack. Queue bottom-up: #<bottom> → #<this> → #<top>.

Queue each PR bottom-up:

```bash
for pr in <bottom_up_prs>; do
  gh pr comment $pr --body "@mergifyio queue"
  sleep 2
done
```

## 5. GitHub-native stacks

If the PR was pushed with `mergify stack push` (GitHub-native registration), the classic merge endpoint returns 403. The ONLY merge path is `@mergifyio queue`. Do not attempt `gh pr merge`.

## Proceed

All protections pass → proceed to Step 7.
