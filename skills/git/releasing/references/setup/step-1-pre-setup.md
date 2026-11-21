# Setup step 1 — pre-setup

Working directory: the repo (an Orca worktree for this repo). Run this after [step-0-add-repo.md](step-0-add-repo.md) and before any setup work.

## What this step does

1. Confirm the repo is in `repo.json` and at least one of its three fields (`ci.yaml`, `mergify.yaml`, `release.yaml`) is `need-setup`.
2. Run the audit to see what is missing:

```shell
# 1. version file?
for f in pyproject.toml package.json Cargo.toml setup.py setup.cfg __version__.py VERSION; do
  [ -e "$f" ] && echo "version file: $f"
done
# 2. release workflow?
ls .github/workflows/ 2>/dev/null
# 3. cliff.toml?
[ -f cliff.toml ] && echo "cliff.toml: yes"
# 4. bump script?
ls scripts/bump.* 2>/dev/null
```

3. Pick the version scheme from the project's language:

| Project type      | Scheme                                 | Where it is stamped                  |
| ----------------- | -------------------------------------- | ------------------------------------ |
| Python            | CalVer `YYYY.M.D.N` or SemVer `vX.Y.Z` | `pyproject.toml` `[project] version` |
| Node / TypeScript | SemVer `X.Y.Z`                         | `package.json` `"version"`           |
| Rust              | SemVer `X.Y.Z`                         | `Cargo.toml` `[package] version`     |

If a version file exists, read its current version and confirm the scheme matches the project's existing tags. If no version file exists, create one matching the language and stamp `0.0.1` as the baseline.

Fill only what is missing. If all four exist, skip to [step-5-open-pr.md](step-5-open-pr.md).