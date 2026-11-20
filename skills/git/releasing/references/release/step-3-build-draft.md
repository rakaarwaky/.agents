# Step 3 — build / tag

Which command depends on the repo. Read `repo.json` and the repo's own `.github/workflows/` before choosing.

## psd-timelapse (SemVer tags)

The pipeline is tag-driven, not draft-driven:

1. `auto-release.yml` opens a `chore(release): vX.Y.Z` PR on `develop` after CI passes.
2. `tag-release-prs.yml` watches that PR; on merge it creates the `vX.Y.Z` tag and dispatches `release.yml`.
3. `release.yml` runs test → build → smoke-test → provenance → publishes the GitHub release (assets + auto-generated notes).

To trigger it manually with a known version:

```shell
gh workflow run release.yml -f tag="$NEW_VERSION" -R <owner>/<repo>
```

There is no draft/publish split here — the workflow publishes directly. Watch the single run:

```shell
gh run list --workflow=release.yml -R <owner>/<repo> --limit 1
gh run watch <run-id> -R <owner>/<repo> --exit-status
```

Verify assets match the expected dist outputs (`dist/*` wheel + sdist from `uv build`):

```shell
gh release list -R <owner>/<repo> --limit 1
gh release view "$NEW_VERSION" -R <owner>/<repo> --json assets,url --jq '{url:.url,assets:[.assets[].name]}'
```

## lint-arwaky (SemVer, hand-maintained CHANGELOG)

Same tag-driven model via its `release.yml` / `release-tag.yml`. Prepend the drafted notes to `CHANGELOG.md` in Step 1's prep PR, commit the version bump, then dispatch:

```shell
gh workflow run release.yml -f tag="$NEW_VERSION" -R <owner>/<repo>
gh run watch <run-id> -R <owner>/<repo> --exit-status
```

Watch it (~5–10 min). Verify the release is live with the expected assets:

```shell
gh release view "$NEW_VERSION" -R <owner>/<repo> --json assets,url --jq '{url:.url,assets:[.assets[].name]}'
```

Recovery:

- Build job failed: delete the release and its tag (`gh release delete <tag> -R <owner>/<repo> --cleanup-tag`), fix, re-dispatch.
- Assets missing: delete and re-dispatch — never backfill a published release by hand.
- For a repo that DOES use a draft→publish split (`softprops/action-gh-release` with draft, then undraft), use `gh release edit "$tag" --draft=false` and watch the follow-up publish job.

Proceed to [step-5-verify.md](step-5-verify.md) on success.