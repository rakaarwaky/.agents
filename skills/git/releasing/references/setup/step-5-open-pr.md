# Setup step 5 — open PR

All setup PRs (.citi, .mergify.yaml, release.yml changes) are opened with the `setup` label so the PR babysitter does not auto-queue them.

## Open the setup PR

```shell
git push -u origin "setup/<repo-name>"
PR_NUM=$(gh pr create --base main \
  --head "setup/<repo-name>" \
  --title "setup: <repo> release pipeline" \
  --body "Adds release.yml, ci.yml, cliff.toml, bump.sh, and changelog.sh." \
  --label setup \
  --jq .number)
```

## Mark repo.json ready

After the setup PR is merged, update `repo.json` for this repo:

```json
{
  "ci.yaml": "ready",
  "mergify.yaml": "ready",
  "release.yaml": "ready"
}
```

Set all three fields that were `need-setup`. If `ci.yaml` or `mergify.yaml` were already `ready`, leave them.

## Run the release lane

Once `release.yaml` is `"ready"` in `repo.json`, run the release lane ([`../release/step-0-version-bump.md`](../release/step-0-version-bump.md)). The release lane runs in an Orca worktree — never the main clone.

Before the release lane runs, update the automation's repo scope ([step-6-automation.md](step-6-automation.md)) so `pr_merged` events from the new repo actually fire.
