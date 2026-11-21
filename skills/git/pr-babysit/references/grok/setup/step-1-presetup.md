# Step 1 — Presetup: Template Reference & Repo Facts (setup lane)

Collect repo facts and customization answers before writing CI or Mergify
configs. The actual template files live in `templates/`; read them for YAML
structure and placeholders. Do not inline or duplicate them here.

## Templates

| Template | File | Purpose |
|----------|------|---------|
| Mergify config | [`templates/mergify.yml`](../../../templates/mergify.yml) | Merge queue, auto-merge, priority, stale cleanup |
| CI workflow | [`templates/ci.yml`](../../../templates/ci.yml) | Lint (lint-arwaky-cli scan), build, test per language |

## Repo facts

Gather these before writing any config:

| Fact | How to detect | Example |
|------|---------------|---------|
| `BASE_BRANCH` | `gh api repos/$OWNER_REPO --jq .default_branch` | `main`, `master`, `develop` |
| `REPO_NAME` | `gh api repos/$OWNER_REPO --jq .full_name` | `owner/repo` |
| `LANGUAGE` | Check root files (see step 2) | `rust`, `python`, `typescript`, `multi` |
| `MERGIFY_APP` | Check runs with `app.slug == "mergify"` on PR head | `present`, `absent` |
| `MERGIFY_CONFIG` | Any of the 6 standard paths (see step 3) | `configured`, `none`, `declined` |

## Customization questions (ask once, apply to both templates)

Ask these and record answers as variables for steps 2 and 3:

1. **Base branch** — default detected (`$BASE_BRANCH`). Accept or override.
2. **CI checks** — detected from step 2 (CI workflow job names). Accept, add, or remove.
3. **Checks timeout** — default `15min`. Accept or override (`10min`, `20min`).
4. **Max parallel checks** — default `1` (serial). Accept or override.
5. **Merge method** — default `squash`. Options: `squash`, `merge`, `rebase`.
6. **Update method** — default `merge`. Options: `merge`, `rebase`.
7. **Required approvals** — default `0` (no gate). Set `>=1` if reviews required.
8. **Include priority rules** — default `yes` (hotfix/high, refactor/low).
9. **Include stale cleanup** — default `yes` (warn 30d/14d idle, close after 7d).
10. **Include welcome comment** — default `yes`.
11. **Include keep-up-to-date** — default `yes` (recommended).

## Security: author gate (MANDATORY)

The Mergify config MUST include `author = rakaarwaky` in BOTH:
- `queue_rules[0].queue_conditions`
- `merge_protections_settings.auto_merge_conditions`

This ensures only PRs from `rakaarwaky` are processed. PRs from other authors
are rejected at the queue level.

## Per-language CI check names (for Mergify `check-success` conditions)

| Language | Typical job names |
|----------|-------------------|
| Rust | `lint`, `build`, `test` |
| Python | `lint`, `test` |
| TypeScript | `lint`, `build`, `test` |
| Multi-workspace | `lint`, `test` |

## Validation

```bash
# Mergify
mergify config validate

# CI YAML
yamllint .github/workflows/ci.yml
```

If a CLI is not installed, validate YAML syntax locally; live validation happens
on GitHub after the config PR merges.

## Next

- CI must be written before Mergify (Mergify queue conditions reference CI check
  names). Continue to **step 2** (setup CI), then **step 3** (setup Mergify).