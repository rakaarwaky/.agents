# Step 0 — Add or Remove Repository from Watchlist (repo lane)

When the user runs `/pr-babysit repo add <owner/repo>`:

## Step 0.1 — Verify authentication

```bash
gh auth status
```

If not authenticated, report the error and stop.

## Step 0.2 — Resolve repository details

```bash
gh repo view <owner/repo> --json nameWithOwner,defaultBranchRef
```

Verify the repository exists and is accessible. Store `REPO_FULL_NAME` (e.g., `owner/repo`) and `DEFAULT_BRANCH` for the whole pipeline run.

## Step 0.3 — Register in source-of-truth watchlist

Source-of-truth watchlist file: `/home/raka/.agents/develop/repo.json` 

Deduplicate: skip if `repo` is already present in `repos[].name`. Add entry with:

```json
{
  "owner": "<owner>",
  "name": "<repo>",
  "default_branch": "<DEFAULT_BRANCH>",
  "mergify": true,
  "ci_workflow": "ci.yml",
  "status": "watching",
  "main_ci": "unknown",
  "open_prs": []
}
```

Initialize `known_prs` with the currently open PR numbers so that pre-existing PRs are not reprocessed:

```bash
gh pr list --repo <owner/repo> --state open --json number --jq '.[].number'
```

Write the state file. Report the registered repo and the initial `known_prs` count.

## Next

After `repo add`, the pipeline continues with step 1 (webhook forwarding) in `repo/`.

---

When the user runs `/pr-babysit repo remove <owner/repo>`:

## Step 0.4 — Remove repository from watchlist

Read `/home/raka/.agents/develop/repo.json`, find the entry where `owner` and `name` match `<owner/repo>`, and remove it from the `repos` array. Write the file back. Report the removed repo.

If the repo is not found in the watchlist, report that it is not being watched and stop.
