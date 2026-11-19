# Step 1 — Configure Mergify Merge Rules (setup lane)

After step 0 detects (or bootstraps) Mergify, write `.mergify.yml` from the lint-arwaky
role model template, customized for this repo's facts and user answers.

## Role model: lint-arwaky `.mergify.yml`

The lint-arwaky repo at `/home/raka/.agents/skills/architechture/tools/.mergify.yml` is the
role model. Its structure:

```
defaults:
  queue_rule:
    update_method: <merge|rebase>       # how queue updates PR before testing
    merge_method: <squash|merge|rebase>  # how queue merges into base branch
    checks_timeout: <duration>           # max queue wait per PR
    merge_conditions:                    # checks that must pass before merge
      - check-success = <check-name>     # one per CI check

merge_queue:
  max_parallel_checks: <N>               # 1 = serial (recommended)
  status_comments: outcomes
  queue_controls_comment: true

merge_protections_settings:
  auto_merge_conditions:                 # conditions to auto-enter queue
    - base = <BASE_BRANCH>
    - -draft
    - -conflict
  post_comment: true
  reporting_method: check-runs

queue_rules:
  - name: default

priority_rules:                          # optional, if include_priority_rules=yes
  - name: hotfixes-first
    conditions:
      - label = hotfix
    priority: high
    allow_checks_interruption: true
  - name: refactors-last
    conditions:
      - label = refactor
    priority: low

pull_request_rules:
  - name: keep-prs-up-to-date            # optional, if include_keep_up_to_date=yes
    conditions:
      - base = <BASE_BRANCH>
      - -draft
      - -merged
      - -closed
      - -conflict
    actions:
      update: {}

  - name: warn-on-conflicts
    conditions:
      - conflict
      - -merged
      - -closed
    actions:
      label:
        add:
          - conflict

  - name: stale-cleanup                  # optional, if include_stale_cleanup=yes
    conditions:
      - base = <BASE_BRANCH>
      - -merged
      - -closed
      - -label = stale
      - updated-at < 14 days ago
      - created-at < 30 days ago
    actions:
      comment:
        message: >
          This PR has been open for 30 days with no commits for 14. If you're still working on it, push a commit or leave a comment. Otherwise, this PR will auto-close in 7 days.
      label:
        add:
          - stale

  - name: close-abandoned-stale          # optional, if include_stale_cleanup=yes
    conditions:
      - base = <BASE_BRANCH>
      - -merged
      - -closed
      - label = stale
      - updated-at < 7 days ago
    actions:
      close:
        message: 'Closed automatically — no activity for 7+ days after a stale warning.'
      label:
        remove:
          - stale

  - name: welcome-new-pr                 # optional, if include_welcome_comment=yes
    conditions:
      - base = <BASE_BRANCH>
      - -merged
      - -closed
      - -label = stale
      - created-at < 5 minutes ago
    actions:
      comment:
        message: >
          Thanks for the PR! CI is running — the merge queue will pick it up automatically once all checks pass.

  - name: merged-notification
    conditions:
      - merged
      - base = <BASE_BRANCH>
    actions:
      comment:
        message: Merged via the merge queue. Thanks for the contribution!

scopes:
  source:
    files: {}
```

## 1. Write `.mergify.yml` from template

Substitute all `<...>` placeholders with values collected in step 0:

| Placeholder | Source | Default |
|-------------|--------|---------|
| `<BASE_BRANCH>` | step 0 `BASE_BRANCH` | detected default branch |
| `<check-name>` | step 0 `CI_CHECKS` | one `check-success = <name>` per check |
| `<duration>` | step 0 checks timeout | `15min` |
| `<N>` | step 0 max parallel checks | `1` |
| `<merge|rebase>` | step 0 merge method | `squash` |
| `<merge|rebase>` (update_method) | step 0 update method | `merge` |

Approval gating (optional):
- If `required_approvals >= 1`, add to the auto-merge pull_request_rule:
  - `"#approved-reviews-by>=<N>"`
- Otherwise omit the approval condition.

Priority rules: include only if `include_priority_rules=yes`.
Stale cleanup: include only if `include_stale_cleanup=yes`.
Welcome comment: include only if `include_welcome_comment=yes`.
Keep PRs up to date: include only if `include_keep_up_to_date=yes` (recommended).

## 2. Validate

```bash
mergify config validate
```

If it fails, fix and retry (max 2 attempts). If still failing, report the error and stop.

Note: `mergify` CLI may not be installed on this host. If so, validate YAML syntax locally
and note that live validation happens on GitHub after the config PR merges.

## 3. Open a configuration PR

Do NOT commit to the PR's branch. Create a separate branch:

```bash
git checkout -b chore/configure-mergify-rules <BASE_BRANCH>
git add .mergify.yml
git commit -m "ci: configure Mergify auto-merge rules"
git push origin chore/configure-mergify-rules
gh pr create \
  --title "ci: configure Mergify auto-merge rules" \
  --body "Auto-merge every green, non-draft PR via Mergify merge queue. Auto-generated by pr-babysit setup.

Config customizations:
- Base branch: <BASE_BRANCH>
- CI checks: <comma-separated>
- Checks timeout: <duration>
- Max parallel checks: <N>
- Merge method: <method>
- Update method: <method>
- Required approvals: <N>
- Priority rules: <yes|no>
- Stale cleanup: <yes|no>
- Welcome comment: <yes|no>
- Keep PRs up to date: <yes|no>" \
  --base <BASE_BRANCH>
```

Report: "Created PR #<N> to configure Mergify merge rules. Once merged, green non-draft PRs will auto-merge via the Mergify merge queue."

## Report to Hermes

Include the configuration PR number and rule summary:

> Mergify: configured
> Config file: .mergify.yml
> Config PR: #<N> (if opened)
> Base branch: <BASE_BRANCH>
> CI checks: <comma-separated>
> Rules: CI green + [approvals] + non-draft → merge queue

## Done

Setup is complete. No further steps run in this lane.
