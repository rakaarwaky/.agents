# Step 0 — Detect Mergify (setup lane)

When the user runs `/pr-babysit setup <number>`:

Run only for the target PR's repo. Determines whether Mergify merge-queue is available
and collects repo-specific facts needed to build a customized `.mergify.yml`.

## Detect Mergify

Check in this order (stop at first positive):

### 1. Config file in the worktree

```bash
for f in .mergify.yml .mergify.yaml .mergify/config.yml .mergify/config.yaml .github/mergify.yml .github/mergify.yaml; do
  if [ -f "$f" ]; then
    MERGIFY_CONFIG="$f"
    MERGIFY_AVAILABLE="configured"
    break
  fi
done
```

### 2. Mergify check-runs on the PR

```bash
SHA=$(gh pr view <number> --json headRefOid -q .headRefOid)
gh api "repos/$OWNER_REPO/commits/$SHA/check-runs" \
  -q '.check_runs[] | select(.app.slug == "mergify") | .name' 2>/dev/null | head -1
```

Non-empty result → `MERGIFY_AVAILABLE="installed"` (app installed, no local config).

### 3. Default

No config, no check-runs → `MERGIFY_AVAILABLE="none"`.

## Collect repo facts

Gather these before writing config (used in step 1):

| Fact | How to detect | Example |
|------|---------------|---------|
| `BASE_BRANCH` | `gh api repos/$OWNER_REPO --jq .default_branch` | `main`, `master`, `develop` |
| `REPO_NAME` | `gh api repos/$OWNER_REPO --jq .full_name` | `owner/repo` |
| `CI_CHECKS` | Check runs on the PR's head commit | `Clippy`, `Build`, `Tests`, `Self-Lint` |
| `MERGIFY_APP` | Check runs with `app.slug == "mergify"` | present or absent |

Detect CI checks:

```bash
SHA=$(gh pr view <number> --json headRefOid -q .headRefOid)
gh api "repos/$OWNER_REPO/commits/$SHA/check-runs" \
  -q '.check_runs[].name' 2>/dev/null | sort -u
```

## Bootstrap `.mergify.yml` (when `MERGIFY_AVAILABLE` is `"none"` or `"installed"`)

### Ask the user

> PR <number> targets a repo without Mergify merge-queue configuration.
> To use Mergify auto-merge, I'll add a `.mergify.yml` with a merge-queue rule
> modeled on the lint-arwaky role model, customized for this repo.
> Proceed?

If declined, set `MERGIFY_AVAILABLE="declined"` and stop.

### Customization questions (ask once, apply to template)

Ask the user these and record answers for step 1:

1. **Base branch** — default is detected (`$BASE_BRANCH`). Accept or override.
2. **CI checks** — detected list shown above. Accept, add, or remove check names.
3. **Checks timeout** — default `15min`. Accept or override (e.g. `10min`, `20min`).
4. **Max parallel checks** — default `1` (serial). Accept or override.
5. **Merge method** — default `squash`. Options: `squash`, `merge`, `rebase`.
6. **Update method** — default `merge`. Options: `merge`, `rebase`.
7. **Required approvals** — default `0` (no approval gate). Set `>=1` if reviews required.
8. **Include priority rules** — default `yes` (hotfix/high, refactor/low).
9. **Include stale cleanup** — default `yes` (warn at 30d/14d idle, close after 7d).
10. **Include welcome comment** — default `yes`.

Record all answers as variables for step 1.

## Report to Hermes

Include `MERGIFY_AVAILABLE` and the collected facts:

> Mergify: <configured|installed|none|declined>
> Config file: <path or "not found">
> Base branch: <BASE_BRANCH>
> CI checks: <comma-separated>
> Customizations: <summary of user answers>

## Next

After detection completes, continue to step 1 (configure and write `.mergify.yml` from template).
