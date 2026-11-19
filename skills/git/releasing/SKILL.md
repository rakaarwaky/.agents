---
name: releasing
description: "Release, cut a release, ship a new version, publish or tag a release for the mergify CLI, recover a failed release run."
when-to-use: 'Cut a CalVer release of the mergify CLI autonomously — bump via the bump script, open and merge a release prep PR, build and publish the draft through GitHub workflows, and recover failed release runs. Triggers: "release", "cut a release", "ship a new version", "publish a release", "tag a version", "release run recovery".'
argument-hint: "--tag <tag> --target_commitish <sha>"
---

# Releasing `mergify-cli` — autonomous headless release agent

Execute end-to-end CalVer releases for the `mergify-cli` project through automated version bumps, release prep pull requests, artifact builds, and PyPI publishing.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Confirm repository remote is `Mergifyio/mergify-cli` with CalVer versioning scheme before proceeding. | Verify `git remote -v` and version format match `mergify-cli` requirements. |
| R2 | Drive versioning strictly through `.github/workflows/release.yml`; never manually edit version strings in config files. | Verify placeholder version retention in `pyproject.toml` and `Cargo.toml`. |
| R3 | Enforce mandatory prep PR flow: never commit version bumps directly to main or push tags manually. | Check that release branch PR is opened, approved, and merged with green CI. |
| R4 | Never create releases via `gh release create` or the GitHub Releases UI, which bypasses workflow asset builders. | Ensure release drafts are initiated strictly by workflow dispatch. |
| R5 | Treat Step 4 (Publish) as irreversible and autonomous, proceeding straight to publish without stopping for approval. | Verify automated transition from validated draft to published release. |
| R6 | Report Homebrew tap PR merge as the only human-actionable manual step upon release completion. | Confirm final output highlights Homebrew tap merge link for manual sign-off. |

## Routing

| Step | Reference | Purpose |
| ---- | --------- | ------- |
| Step 0 | [`references/step-0-version-bump.md`](references/step-0-version-bump.md) | Version bump and changelog generation: compute `NEW_VERSION`, generate changelog with `git-cliff`, run the bump script (`scripts/bump.sh` / `scripts/bump.py`). Working directory: project root. |
| Step 1 | [`references/step-1-prep-pr.md`](references/step-1-prep-pr.md) | Release prep PR: create branch, open PR, wait for green CI, auto-approve and merge with admin, switch back to main. |
| Step 2 | [`references/step-2-preflight.md`](references/step-2-preflight.md) | Pre-flight checks: verify main is clean (CI green, no leftover draft release), report what ships since the previous tag. Stop on anything red. |
| Step 3 | [`references/step-3-build-draft.md`](references/step-3-build-draft.md) | Build the draft: trigger `release.yml`, watch (~5–10 min), verify the draft carries exactly seven assets. Proceed immediately to Step 4. |
| Step 4 | [`references/step-4-publish.md`](references/step-4-publish.md) | Publish: `gh release edit "$tag" --draft=false --latest`, watch the publish job (~5–10 min), confirm PyPI + Homebrew tap PR. |
| Step 5 | [`references/step-5-verify.md`](references/step-5-verify.md) | Verify after publishing: confirm PyPI reports the new version and the Homebrew tap PR is open. Report final status. |
