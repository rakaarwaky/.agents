# Step 0 — version bump

Working directory: the Orca worktree created in Step 1.

Before touching versions, resolve what this repo uses. Read `repo.json` and the repo's own release workflow.

| Repo | Version scheme | Release pipeline |
|------|---------------|------------------|
| `psd-timelapse` | SemVer via `release.yml` (tags `v*.*.*`) | `auto-release.yml` opens a `chore(release): vX.Y.Z` PR on `develop`; `tag-release-prs.yml` tags it on merge; `release.yml` builds + publishes |
| `lint-arwaky` | SemVer `v3.x.y` | `release.yml` builds + publishes |

**Rule: drive the repo's existing release pipeline; do not invent a parallel one.** git-cliff is the changelog source for every repo (see the setup lane). If `cliff.toml` is missing, create it (see the setup lane's step 2) before generating notes.

## 0a. Resolve the version

Determine the next version from the **last git tag**, not the last GitHub release (a repo may tag without publishing, or publish without a tag):

```shell
last=$(git tag --list 'v*' --sort=-v:refname | head -1)   # newest semver tag
```

## 0b. Generate the changelog with git-cliff

Install if missing, create `cliff.toml` if missing (valid `commit_parsers` array; first match wins, `group` sets the section, `skip = true` drops it):

```toml
[git]
conventional_commits = true
filter_unconventional = false

commit_parsers = [
  { message = "^chore\\(release\\):", skip = true },
  { message = "^Merge ",              skip = true },
  { message = "^feat",                group = "Added" },
  { message = "^fix",                group = "Fixed" },
  { message = "^perf",               group = "Changed" },
  { message = "^(docs|test|refactor|chore|ci)", skip = true },
  { message = ".*",                  group = "Other" },
]

[changelog]
prepend = true
```

Generate and prepend:

```shell
git-cliff --unreleased --tag "$NEW_VERSION" --prepend CHANGELOG.md
```

## 1. Compute `NEW_VERSION`

For SemVer, bump the patch by default and let the release PR title / commit encode the intent. For CalVer, use `YYYY.M.D.N` (no zero-padding, `N` starts at 1 each UTC day).

## 2. Stamp the version + commit the changelog

Run the bump script if it exists; otherwise stamp manually:

```shell
if [ -f scripts/bump.sh ]; then
  bash scripts/bump.sh "$NEW_VERSION"
else
  for f in pyproject.toml package.json Cargo.toml; do [ -e "$f" ] && git add -A "$f"; done
  git add CHANGELOG.md cliff.toml 2>/dev/null
  git commit -m "chore(release): $NEW_VERSION"   # match the repo's convention
fi
```

> `psd-timelapse`'s `tag-release-prs.yml` only tags a PR whose title starts with `chore(release): vX.Y.Z`. Match the target repo's exact release commit prefix — read that workflow before committing.

Recovery: if the bump script is missing or fails, stamp the version file and commit manually (above). Then continue from Step 1.

## Release notes style

Notes are for the people who use the product, not the people who built it.

Gather:
- Find the last release tag and list **every** pull request merged since then — the full range between the previous tag and now, not only the PR that triggered this release run. The trigger fires per merge, but the notes cover all accumulated PRs.
- git-cliff handles this automatically.
- Skip refactors, test-only changes, dependency bumps with no user effect, and internal tooling.

Write three groups, in this order, each a short bulleted list:

- **New:** things users can do now that they couldn't before.
- **Fixed:** problems users could hit that are gone. Say what used to go wrong, not how it was fixed.
- **Changed:** things that work differently now, including anything removed.

Each bullet is one sentence in plain words. Lead with what the user sees. Leave out code names, file names and internal project names. Link the pull request at the end only if your owner wants links.

Before sharing:
- Put the biggest change first in its group.
- Ask your owner about anything you couldn't tell was user-facing.
- Post the draft for editing; never publish it yourself.