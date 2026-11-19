# Step 0 — Add Repository to Watchlist (repo lane)

When the user runs `/pr-babysit repo add <owner/repo>`:

Set `repo_mode: true` on the watchlist entry.

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

## Step 0.3 — Register and persist

State file (per user): `~/.agents/develop/repo-watchlist.json`

Generate or resolve `INSTANCE_ID` on first use:

```bash
<python> <HOST_PY> uuid --full
```

Where `HOST_PY` resolves to `<dirname of this SKILL.md>/scripts/host.py` and Python is a real Python 3 interpreter (reject WindowsApps stubs).

Deduplicate: skip if `repo` is already present in `watched_repos`. Initialize `known_prs` with the currently open PR numbers so that pre-existing PRs are not reprocessed:

```bash
gh pr list --repo <owner/repo> --state open --json number --jq '.[].number'
```

Write the state file. Report the registered repo and the initial `known_prs` count.

```json
{
  "instance_id": "<INSTANCE_ID>",
  "watched_repos": {
    "<owner/repo>": {
      "added_at": "<ISO8601>",
      "default_branch": "<DEFAULT_BRANCH>",
      "known_prs": [101, 102, 103]
    }
  }
}
```

## Next

After `repo add`, the pipeline continues with step 1 (webhook forwarding) in `repo/`.
