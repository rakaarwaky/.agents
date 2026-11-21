# Step 5 — verify after publishing

Confirm the release workflow finished green and the release is live. Run these commands from the Orca worktree — never from the main clone.

```shell
gh run list --workflow=release.yml -R <owner>/<repo> --limit 2      # publish job green
gh release view "$NEW_VERSION" -R <owner>/<repo> --json url,isDraft,assets --jq '{url, draft:.isDraft, assets:[.assets[].name]}'
```

- `isDraft` must be `false` (published).
- The asset list must match the repo's expected outputs (e.g. Python: wheel + sdist; Node: tarball; Rust: binary).
- For registries beyond GitHub, check the registry endpoint named in `repo.json` or the repo's CI config.

Report the final status:

> Release $NEW_VERSION published successfully. Release URL: <url>