# Step 0 — Add PR to Watchlist (ship lane)

When the user runs `/pr-babysit ship <number>`:

Set `ship: true` on the PR entry.

## Step 0.1 — Verify authentication

```bash
gh auth status
```

If not authenticated, report the error and stop.

## Step 0.2 — Security: author gate (mandatory)

```bash
AUTHOR=$(gh pr view <number> --json author --jq '.author.login')
```

If `AUTHOR` is not `rakaarwaky`, stop immediately. Report the PR number, author, and that it was rejected for security. Do **not** process, fix, or merge the PR. This gate is enforced at the skill level; Orca automation `from=me` and Mergify `author = rakaarwaky` enforce it at two more layers.

### Release-label gate (mandatory)

```bash
gh pr view <number> --json labels --jq '[.labels[].name] | index("release")'
```

If the result is not `null` (the PR carries the `release` label), stop immediately. Report the PR number and that it is owned by Risa-AutoRelease. Do **not** process, fix, comment on, or merge the PR. This gate enforces R7 in `SKILL.md`.

## Step 0.3 — Verify PR details

```bash
gh pr view <number> --json headRefName,baseRefName,url,title,state,number,draft
gh repo view --json nameWithOwner --jq '.nameWithOwner'
```

Verify the PR exists and is open. If MERGED or CLOSED, inform the user and stop.

Store `OWNER_REPO`, `headRefName`, `baseRefName` for the whole pipeline run.

If `baseRefName` is another PR branch (not the repo default branch), stop and tell the user: this skill handles standalone PRs targeting the default branch; stacked PRs need the stack tool that created them.

## Step 0.4 — Security: watchlist check

Confirm `<OWNER_REPO>` is present in `/home/raka/.agents/develop/repo.json` (the source-of-truth watchlist).

If the repo is **not** in the watchlist, stop and report that the repo is not being watched. Add it first via `/pr-babysit repo add <owner/repo>`.

## Step 0.5 — Undraft PR when CI is green

```bash
DRAFT=$(gh pr view <number> --json isDraft --jq '.isDraft')
```

If `DRAFT` is `true`:
- Check CI: `gh pr checks <number> --json statusCheckRollup`
- If all checks are `SUCCESS`/`NEUTRAL`/`SKIPPED` (green), run `gh pr ready <number>` to undraft the PR before watching CI.
- If CI is not green, acknowledge the draft PR and begin watching CI (the PR will be undrafted automatically once CI turns green in later cycles).

## Step 0.6 — Register and persist

State file (per session): `/home/raka/.agents/develop/<namarepo>/pr-babysit/watched-prs-<INSTANCE_ID>.json`. `<namarepo>` is the basename of the repo containing the PR (resolve from `OWNER_REPO` via `basename`, lowercased and slugified to match the `implement` host.py convention). `INSTANCE_ID` is a UUID generated on first `ship` (resolve `HOST_PY` as `<dirname of this SKILL.md>/scripts/host.py`, run `<python> <HOST_PY> uuid --full` with a real Python 3 interpreter, rejecting WindowsApps stubs) and held in conversation context.

Deduplicate: skip if `number` + repo already in the watchlist. The `ship` flag is always `true` in this lane.

```json
{
  "instance_id": "<INSTANCE_ID>",
  "prs": [
    {
      "number": 123,
      "repo": "owner/repo",
      "head_ref": "feat/x",
      "base_ref": "main",
      "ship": true,
      "last_status": null,
      "last_checked": null,
      "fix_count": 0
    }
  ]
}
```

Write the state file. Report what was added and the ship flag.

## Next

After `ship`, the pipeline continues with step 1 (watch CI) in `ship/`.
