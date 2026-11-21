# Step 0: Add to Watchlist, Check CI, & Spawn Grok for the Fix Pass

Hermes owns watchlist state and CI observation. All code changes — fixing a red check, resolving conflicts, addressing review threads — are delegated to Grok Build. This step: verify auth, register the PR, observe CI once, then (if red) spawn a Grok worktree for the fix pass.

## 0a: Verify Authentication

```
gh auth status
```

If not authenticated, report the error and stop.

## 0b: Fetch PR Details & Register

```
gh pr view <number> --json headRefName,baseRefName,url,title,state,number
gh repo view --json nameWithOwner --jq '.nameWithOwner'
```

- Verify the PR exists and is open. If MERGED or CLOSED, inform the user and stop.
- If `baseRefName` is another PR branch (not the repo default branch), stop: this skill handles standalone PRs targeting the default branch only.
- **Ship flag**: if the user used `ship` argument, set `ship: true` for this PR.

## 0c: Persist the Watchlist Entry

State file (per session): `~/.agents/develop/<namarepo>/pr-babysit/watched-prs-<INSTANCE_ID>.json`. `<namarepo>` is the basename of the repo containing the PR (resolve from `OWNER_REPO`, lowercased and slugified to match the `implement` host.py convention). `INSTANCE_ID` is a UUID generated on first `add` (resolve `HOST_PY` as `<dirname of this SKILL.md>/scripts/host.py`, run `<python> <HOST_PY> uuid --full`); dedupe by `number` + repo; update `ship` if the PR is already watched and `ship` argument was passed.

```json
{
  "instance_id": "<INSTANCE_ID>",
  "prs": [
    {
      "number": <number>,
      "repo": "<OWNER_REPO>",
      "head_ref": "<headRefName>",
      "base_ref": "<baseRefName>",
      "ship": false,
      "last_status": null,
      "last_checked": null,
      "fix_count": 0,
      "mergify_available": "<configured|installed|cli-only|none|declined|bootstrapping>",
      "merge_method": null,
      "requeue_count": 0
    }
  ]
}
```

Report: "Watching PR <number> (<title>) — ship: <true|false>."

## 0d: Check CI Once

Run the CI status check from `grok/ship/step-1-watch-ci.md` (`gh pr checks` for the PR's head SHA, or the git+curl variant). Store the result as `last_status`, set `last_checked` to now.

- **All green, no open review threads**: report "PR <number> is green and ship-ready (or ready-to-watch)." If `ship` is `true`, proceed to Step 1 (Merge). Otherwise, the watchlist entry is idle — the user (or a later event) re-invokes this skill to re-check.
- **Red check or open thread**: proceed to Step 0e — spawn the fix pass.

## 0e: Spawn Grok for the Fix Pass

Resolve `$ORCA` (`$ORCA_CLI_COMMAND` if set, else `orca-ide` on Linux — never bare `orca`) and the owning repo for the PR's head branch.

```
"$ORCA" worktree create --repo path:<repo_path> --name pr-babysit-<number> --base-branch <head_ref> --agent grok --no-parent --surface terminal --json
```

Parse JSON: `result.worktree.path` → `worktree_path`, `result.worktree.id` → `worktree_id`.

Compose the brief (Grok has zero context):

1. **Goal** — Bring PR `<number>` to green and merge-ready:
   - Fix every failing check, resolve conflicts, address every review thread (commit titles follow Conventional Commits).
   - **Mergify detection & bootstrap** (`grok/ship/step-4-mergify-detect.md`): Detect a Mergify config (`.github/workflows/mergify.yml` or any other supported location) or the Mergify app on the repo. If missing and `ship` argument is used, bootstrap a minimal validated `.github/workflows/mergify.yml` on a separate PR branch.
   - **CI diagnostics** (`grok/ship/step-5-mergify-diagnostics.md`): If CI fails, inspect `mergify events`, detect scopes via `mergify ci scopes`, and quarantine flaky tests via `mergify tests quarantines add`.
   - **Merge protections** (`grok/ship/step-6-merge-protections.md`): Before merging, check `mergify freeze list`, `Depends-On:`, `Merge-After:`, and handle stacked PRs (`mergify stack list`).
   - **Merge** (`grok/ship/step-7-merge.md`): If `ship` argument is true and PR is healthy, merge via Mergify queue (`@mergifyio queue`); fallback to `gh pr merge --squash --delete-branch` if Mergify is unavailable.
2. **Current state** — Paste failing check names + log excerpts, list of open review threads, and `fix_count`.
3. **Ship argument** — State whether `ship` argument is active (`true`/`false`).
4. **Acceptance criteria** — All checks passing or quarantined, zero open review threads, PR merged (if `ship`) or reported merge-ready, worktree clean.

Drop the task, once, via `orca terminal send --terminal <handle> --text "<brief>" --enter --json`:

```
/pr-babysit fix <number>
```

Confirm `accepted: true`. **After this send, do not send any more text to Grok.** Increment `fix_count`.

## Proceed to Step 1

Do NOT end the turn after dropping the task. Hermes must stay active and proceed immediately to Step 1 in this session to wait for the fix pass:

> Dropped /pr-babysit fix into Grok Build at <worktree_path> (PR <number>, <N> failing checks, <M> open threads). Proceeding to Step 1 to wait for completion.