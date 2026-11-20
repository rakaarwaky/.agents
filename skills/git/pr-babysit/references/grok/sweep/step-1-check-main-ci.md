# Step 1 — Check main CI (sweep lane)

Run when the sweep has loaded the watchlist and is checking each repo's default branch.

## Step 1.1 — Read latest CI run on default branch

For each repo `<owner>/<repo>`:

```bash
gh run list -R <owner>/<repo> --branch <default_branch> --limit 1 --json conclusion,status,databaseId
```

Capture:
- If `status` is `in_progress` or `queued`: CI still running. Skip this repo this cycle — nothing to fix yet.
- If `conclusion` is `failure`: record `<run_id>` (from `databaseId`) and proceed to step 2 (fix main CI).
- If `conclusion` is `success`: record as green.
- If no runs found: record as no CI.

## Step 1.2 — Collect results

Store a list of repos with their CI state: `green`, `red`, `running`, or `none`.

## Next

After reading CI for every repo, the pipeline continues with step 2 (fix main CI) in `sweep/`.