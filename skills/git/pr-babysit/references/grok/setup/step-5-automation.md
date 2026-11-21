# Step 5 — Register New Repo in Orca Event Automation (setup lane)

The event-driven automation `PR babysitter event watcher` (id `cc7013a7-83ff-4cb7-889e-261216c52c02`)
is repo-scoped via its `on[].in` filter. When a new repo is registered in `repo.json`, the
automation must be updated to include that repo in its `in` list — otherwise no `pr_opened`,
`pr_pushed`, `ci_failed`, or any other GitHub event will fire for it, and `ship` / `sweep`
lanes have no event trigger to work from.

## Step 5.1 — Check whether the repo is already registered

Run the current automation list:

```bash
orca automations list --json
```

Find the automation named `PR babysitter event watcher` (id `cc7013a7-...`).
Inspect its `on` array. Each entry has an `in` field listing repo IDs.

If the new repo's GitHub repo ID is already present in any `on[].in` entry, skip to Step 5.4.

## Step 5.2 — Resolve the new repo's GitHub repo ID

```bash
gh api repos/<owner>/<repo> --jq .id
```

Store the result as `NEW_REPO_ID`.

## Step 5.3 — Update the automation's `in` list

Use `orca automations create` (which replaces the automation atomically). Preserve the
existing prompt and all existing `on` entries. Add the new repo to **every** GitHub event
entry's `in` list so that all events (`pr_opened`, `pr_pushed`, `ci_failed`, `pr_ready`,
`pr_merged`, `pr_closed`, `review`, `review_comment`, `comment`, `review_requested`,
`mentioned`, `assigned`) now fire for the new repo.

The full set of GitHub event entries the automation must carry is:

| Event | `in` filter |
|-------|-------------|
| `github.pr_opened` | `in=<new_repo_id>` + all existing repo IDs |
| `github.pr_pushed` | same |
| `github.ci_failed` | same |
| `github.pr_ready` | same |
| `github.pr_merged` | same |
| `github.pr_closed` | same |
| `github.review` | same |
| `github.review_comment` | same |
| `github.comment` | same |
| `github.review_requested` | same |
| `github.mentioned` | same |
| `github.assigned` | same |

Use the `--on` flag once per event, passing `in=<all_repo_ids>` with all IDs comma-separated.
The `from=me` filter on `github.pr_opened` is preserved as the first entry.

## Step 5.4 — Report

> Automation updated: `PR babysitter event watcher` now covers repo `<owner>/<repo>`
> (repo ID `<NEW_REPO_ID>`) across all 12 GitHub event types.

If the automation already covered the repo, report:

> Automation already covers repo `<owner>/<repo>` — no update needed.

## Next

The setup lane is complete. The repo is now:
- Registered in `repo.json` (step 0)
- Has CI + Mergify config (steps 1–4)
- Triggers event-driven ship sessions via the Orca automation (step 5)
