# Step 7 — Merge

Run only after all checks pass, review threads are resolved, protections are cleared, and `ship` is `true`.

## Security gate (re-check before merging)

```bash
AUTHOR=$(gh pr view <number> --json author --jq '.author.login')
[ "$AUTHOR" = "rakaarwaky" ] || { echo "REFUSED: author=$AUTHOR"; exit 1; }
```

If the author is not `rakaarwaky`, refuse the merge and report to the owner. Do not queue, do not direct-merge.

### Release-label gate (re-check before merging)

```bash
gh pr view <number> --json labels --jq '[.labels[].name] | index("release")'
```

If the result is not `null` (the PR carries the `release` label), refuse the merge and report to the owner. Do not queue, do not direct-merge. This gate enforces R7 in `SKILL.md` — release PRs are owned by Risa-AutoRelease.

## Auto-merge authorized

SOUL.md authorizes auto-merge for `rakaarwaky`-authored PRs. Once the pre-merge checks below pass, queue the PR immediately — do not ask the owner for merge permission.

## Pre-merge checks

1. Live gate re-query: `state==OPEN`, `!isDraft`, `mergeable==MERGEABLE`, `mergeStateStatus!=DIRTY`, `reviewDecision!=CHANGES_REQUESTED`
2. Every job passed (`SUCCESS`, `NEUTRAL`, `SKIPPED`)
3. No open comments or unresolved threads
4. Merge protections cleared (Step 6) in `ship/`.

Any gate fails → stop and report live values.

## Merge Path Selection

### Path A: Mergify Merge Queue (`MERGIFY_AVAILABLE` is `"configured"`)

Queue via comment:

```bash
gh pr comment <number> --body "@mergifyio queue"
```

Wait for 👍 reaction on the comment (up to 30s):

```bash
COMMENT_ID=$(gh api "repos/$OWNER_REPO/issues/<number>/comments" --jq 'last | .id')
for i in $(seq 1 6); do
  REACTIONS=$(gh api "repos/$OWNER_REPO/issues/comments/$COMMENT_ID/reactions" \
    --jq '[.[] | select(.content == "+1" and .user.login == "mergify[bot]")] | length')
  [ "$REACTIONS" -gt 0 ] && break
  sleep 5
done
```

Monitor progress:

```bash
mergify queue show <number> --json
```

Poll every 30s:
- `queued: true` → still in queue, report position and CI state
- `queued: false, dequeued: false` → merged by the queue → success
- `queued: false, dequeued: true` → dequeued, read `dequeue_code`

On dequeue:
- `CHECKS_FAILED`: fix via Step 2, push, requeue
- `CONFLICT_WITH_BASE_BRANCH`: resolve conflict, push, requeue
- `PULL_REQUEST_UPDATED`: requeue (`@mergifyio queue`)
- Other: report reason, stop (max 2 auto-requeues)

Confirm merge:

```bash
gh pr view <number> --json state -q .state   # must be MERGED
```

If Mergify queue fails or does not react within 30s, fall back to Path B.

### Path B: Direct Merge (fallback)

When `MERGIFY_AVAILABLE` is NOT `"configured"`, setup was declined, or Path A failed:

```bash
gh pr merge <number> --squash --delete-branch
```

Or auto-merge: `gh pr merge <number> --auto --squash --delete-branch`.

Fallback git+curl:

```bash
PR_NUMBER=<number>
curl -s -X PUT \
  -H "Authorization: token ***" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/merge \
  -d '{"merge_method": "squash"}'

git push origin --delete <head_ref>
```

## After the Merge

- Comment on linked issue (if any): PR link + one-line note
- Update state: `last_status: "merged"`, `merge_method: "queue" | "direct"`
- Remove the PR number from the repo's `open_prs` array in `/home/raka/.agents/develop/repo.json`
- Delete branch if not already deleted

## Report to Hermes

> PR <number> merged (<queue|direct-squash|auto>) and branch deleted.
> Mergify status: <configured|installed|none|bootstrapping>
> Quarantined tests: <list or none>
> Worktree clean, ready for retirement.
