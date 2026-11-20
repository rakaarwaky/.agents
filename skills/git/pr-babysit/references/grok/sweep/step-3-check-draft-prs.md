# Step 3 — Check draft PRs (sweep lane)

Run after main CI has been checked for every repo in the watchlist.

## Step 3.1 — List open draft PRs per repo

For each repo `<owner>/<repo>`:

```bash
gh pr list -R <owner>/<repo> --state open --draft --json number,author
```

If no draft PRs exist, skip this repo.

## Step 3.2 — Security: author gate

For each draft PR:

```bash
AUTHOR=$(gh pr view <number> -R <owner>/<repo> --json author --jq '.author.login')
```

If `AUTHOR` is not `rakaarwaky`, skip this PR. Do not undraft, comment, or process it in any way.

## Step 3.3 — Undraft when CI is green

For each draft PR by `rakaarwaky`:

```bash
gh pr checks <number> -R <owner>/<repo> --json statusCheckRollup
```

- If all checks are `SUCCESS` / `NEUTRAL` / `SKIPPED` (green): run `gh pr ready <number> -R <owner>/<repo>` to mark it ready for review. Record the PR as undrafted.
- If any check is still running (`QUEUED`, `IN_PROGRESS`) or failed (`FAILURE`, `TIMED_OUT`, `CANCELLED`): skip. CI is not green.

## Step 3.4 — Maximum undraft attempts

Only undraft each PR once per sweep cycle. Do not retry in the same run.

## Next

After all draft PRs are checked, the pipeline continues with step 4 (report) in `sweep/`.