# Step 0 — Initialize Nightly Sweep (sweep lane)

When the user runs `/pr-babysit sweep` or the nightly sweep automation fires:

## Step 0.1 — Verify authentication

```bash
gh auth status
```

If not authenticated, report the error and stop.

## Step 0.2 — Read watchlist

Read `/home/raka/.agents/develop/repo.json` and iterate over every entry in the `repos` array. For each repo, capture `owner`, `name`, and `default_branch`. If `repos` is empty or missing, report nothing to watch and stop.

Report how many repos will be swept before proceeding to step 1.

## Next

After sweep init, the pipeline continues with step 1 (check main CI) in `sweep/`.
