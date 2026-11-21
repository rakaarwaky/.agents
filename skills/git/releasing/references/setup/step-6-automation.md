# Setup step 6 — automation registration

Update the Orca release automation's repo scope so events from the new repo fire.

## Why this step exists

Risa's release automation ("Risa auto-release on PR merge", id `e6e330a1`) triggers on `github.pr_merged`. Its `in` filter currently only includes repos already registered in `repo.json`. When you add a new repo via [step-0-add-repo.md](step-0-add-repo.md), the automation does not yet know about it — so `pr_merged` events for that repo will be silently ignored until you update the automation. This is the same gap Nany flagged in the pr-babysit setup lane.

## When to run this step

Run this **after** the setup PR is merged and `repo.json` fields are set to `"ready"`, but **before** the release lane runs on the new repo. The release lane reads `repo.json`; the automation reads its own `in` list. Both must include the new repo.

## What to do

### 1. Find the automation ID

```shell
orca automations list --json | jq -r '.result.automations[] | select(.name == "Risa auto-release on PR merge") | .id'
```

Expected: `e6e330a1-3925-4f75-884a-30e92a5569ad`

### 2. Get the current `in` list for pr_merged

```shell
orca automations show e6e330a1-3925-4f75-884a-30e92a5569ad --json \
  | jq -r '.result.automation.on[] | select(.event=="pr_merged") | .in'
```

Example output:
```
["github:184019079:1206546093", "github:184019079:1274832767"]
```

### 3. Resolve the new repo's GitHub ref

Get the immutable numeric GitHub repo ID from `gh api`:

```shell
gh api repos/<owner>/<repo> --jq '{id,full_name}'
```

Record `id` as `<repo-id>` and `full_name` as `<owner>/<repo>`.

If the new repo is a sibling of an existing watched repo (same owner/org), the `in` entry format is `github:<owner-id>:<repo-id>`. Use `gh api orgs/<org-name> --jq '.id'` if you don't know the owner ID.

### 4. Update the automation's `in` list

Use `orca automations edit` with the extended `--on` rule. Pass every event type (not just pr_merged) because edit replaces the entire `on` list when invoked:

```shell
orca automations edit e6e330a1-3925-4f75-884a-30e92a5569ad \
  --on 'github.pr_merged github:184019079:1206546093/github:184019079:1274832767/github:184019079:<new-repo-id>' \
  --json
```

If there are additional event types on the automation, preserve them by reading the full list first:

```shell
orca automations show e6e330a1-3925-4f75-884a-30e92a5569ad --json \
  | jq -r '.result.automation.on[] | "\(.[source]).\(.[event]) \(.[in]|join("/"))"'
```

Then repeat all lines above, appending `<new-repo-id>` to each line's `in` list.

### 5. Verify

```shell
orca automations show e6e330a1-3925-4f75-884a-30e92a5569ad --json \
  | jq '.result.automation.on[] | select(.event=="pr_merged") | .in'
```

Confirm the new `github:<owner-id>:<repo-id>` entry appears.