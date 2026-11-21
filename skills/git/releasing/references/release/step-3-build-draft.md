# Step 3 — build / tag

Which command depends on the repo. Read `repo.json` and the repo's own `.github/workflows/` before choosing.

**Worktree rule:** do all of this work in an Orca worktree — never in the main clone. The main clone stays clean.


## Pre-check: tag exists

Before triggering the workflow, confirm the tag exists on the remote:

```shell
git ls-remote --tags origin "$NEW_VERSION" | grep -q "$NEW_VERSION" \
  || { echo "tag $NEW_VERSION not found on remote — create it in step 1 (or via the repo's auto-tag workflow)"; exit 1; }
```

IF the tag is missing -> go back to [step-1-prep-pr.md](step-1-prep-pr.md) step 6 and create it.

## Tag-driven pipeline

The standard pipeline is a single self-contained `release.yml`:

1. A `create-tag` job watches for merged PRs with the `release` label whose title starts with `chore(release):`.
2. On merge, it creates the `vX.Y.Z` tag and pushes it.
3. The tag push triggers the build → test → smoke-test → publish jobs in the same workflow.

To trigger it manually with a known version (if the tag already exists):

```shell
gh workflow run release.yml -f tag="$NEW_VERSION" -R <owner>/<repo>
```

There is no draft/publish split here — the workflow publishes directly. Watch the single run:

```shell
gh run list --workflow=release.yml -R <owner>/<repo> --limit 1
gh run watch <run-id> -R <owner>/<repo> --exit-status
```

Verify assets match the expected dist outputs for the repo's build command (e.g. `dist/*` for Python, `target/release/*` for Rust, package tarball for Node):

```shell
gh release list -R <owner>/<repo> --limit 1
gh release view "$NEW_VERSION" -R <owner>/<repo> --json assets,url --jq '{url:.url,assets:[.assets[].name]}'
```

Recovery:

- Build job failed: delete the release and its tag (`gh release delete <tag> -R <owner>/<repo> --cleanup-tag`), fix, re-dispatch.
- Assets missing: delete and re-dispatch — never backfill a published release by hand.
- For a repo that DOES use a draft→publish split (`softprops/action-gh-release` with draft, then undraft), use `gh release edit "$tag" --draft=false` and watch the follow-up publish job.

Proceed to [step-5-verify.md](step-5-verify.md) on success.