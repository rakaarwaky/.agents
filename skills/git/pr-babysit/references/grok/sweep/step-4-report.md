# Step 4 — Report sweep results (sweep lane)

Run after steps 1–3 have completed for every repo in the watchlist.

## Step 4.1 — Compose the summary

For each repo `<owner>/<repo>`, report:
- **Main CI**: green / red (with run link and one-line cause) / running / no CI.
- **Fix PR**: branch name + PR URL, or "fix already in flight: <PR URL>", or "no fix needed".
- **Draft PRs**: count of draft PRs checked, count undrafted (with PR numbers), count skipped (author or CI).

## Step 4.2 — Format

Write the report as a short bullet list grouped by repo. Lead with what changed: fix PRs opened, PRs undrafted. Then list per-repo CI state.

## Step 4.3 — Report

End with NO_REPLY unless the owner needs to decide something (e.g., a repo has 3 unmerged fix PRs and needs a decision). In that case, describe the decision needed in one line.

## Next

Sweep is complete. No further steps.