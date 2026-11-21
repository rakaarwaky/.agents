# Step 0 — version bump

**All work happens in an Orca worktree created in Step 1. Never edit version files in the main clone.**

Before touching versions, resolve what this repo uses. Read `repo.json` and the repo's own release workflow.

**Rule: drive the repo's existing release pipeline; do not invent a parallel one.** git-cliff is the changelog source for every repo (see the setup lane).

**General release pipeline model** (adapt to the repo's own workflow):

1. A `release.yml` workflow with three entry points:
   - `workflow_dispatch`: computes the version and opens a `chore(release): vX.Y.Z` PR to `main` with the `release` label.
   - `pull_request` (closed, merged to `main`, `release` label present): creates and pushes the `vX.Y.Z` tag.
   - `push` (tag `v*.*.*`): runs test → build → publish.
2. If the repo has a different but working release pipeline, use that instead. The key invariant: the prep PR must be labeled `release`, and the commit/PR title must start with `chore(release):`.

IF `cliff.toml` is missing -> create it (setup lane step 2) before generating notes.
IF `git-cliff` is not installed -> install it before generating notes.
IF the repo has no `scripts/bump.sh` -> stamp the version file and commit manually (section 2 below).

## Multi-language version files

If the repo uses more than one language, the version must be stamped in **all** files. The bump script handles this automatically. Supported languages:

| Language | Version file | Lock file (optional) |
|---|---|---|
| Python | `pyproject.toml` | `uv.lock` |
| TypeScript / JavaScript | `package.json` | `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` |
| Rust | `Cargo.toml` (and `VERSION` if present) | `Cargo.lock` |

For mixed-language repos (e.g. Python + TypeScript), set `VERSION_FILE` to the primary language file and `TS_VERSION_FILE` / `TS_LOCK_FILE` to the secondary. The bump script stamps both. Verify all versions match before committing.

## 0a. Resolve the version

Determine the next version from the **last git tag**, not the last GitHub release (a repo may tag without publishing, or publish without a tag):

```shell
last=$(git tag --list 'v*' --sort=-v:refname | head -1)   # newest semver tag
```

## 0b. Generate the changelog with git-cliff

Install if missing, create `cliff.toml` if missing (valid `commit_parsers` array; first match wins, `group` sets the section, `skip = true` drops it). The header advertises the 2-release rolling window:

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
trim = true
header = """
# Changelog

This changelog shows the current release in full plus a summary of the previous release.
Older releases are available as git tags.
"""
```

### Changelog state detection (first release vs existing versions)

Before generating, check whether `CHANGELOG.md` already has version entries:

```shell
release_count=$(grep -cE '^## (\[)?(v|[0-9])' CHANGELOG.md 2>/dev/null || echo 0)
```

- **`release_count == 0`** (first release ever): generate from the full commit history. The tag range is empty because the version does not exist yet:

  ```shell
  git-cliff --tag "$NEW_VERSION" --output /tmp/changelog-new.md 2>/dev/null || \
  git-cliff "HEAD" --tag "$NEW_VERSION" --output /tmp/changelog-new.md
  ```

  Then prepend the generated content after the header. The first release has no "previous release" to summarize.

- **`release_count >= 1`** (existing changelog): generate only for commits since the newest tag:

  ```shell
  last=$(git tag --list 'v*' --sort=-v:refname | head -1)
  git-cliff "${last}..HEAD" --tag "$NEW_VERSION" --prepend CHANGELOG.md 2>/dev/null || \
  git-cliff --unreleased --tag "$NEW_VERSION" --prepend CHANGELOG.md
  ```


IF `scripts/changelog.sh` exists -> run it to keep only the newest 2 releases (current + 1 summary):

```shell
bash scripts/changelog.sh
```

IF `scripts/changelog.sh` does not exist -> keep the full history for now; the changelog script is optional and can be added later via the setup lane (step 2).

## 1. Compute `NEW_VERSION`

Pick the bump type from the accumulated changes since the last tag. Read the commit messages / PR titles and apply these rules:

| Signal | Bump type | Example |
|---|---|---|
| `BREAKING CHANGE:` in a commit body, or `!` after `feat:`/`fix:` | **major** | `feat!` — new behavior that breaks the public API |
| New `feat:` commit, or a PR labeled `breaking` / `feature` | **minor** | `feat` — new user-facing capability |
| `fix:` commit, or a PR labeled `bug` | **patch** | `fix` — bug fix |
| Only `docs`, `chore`, `refactor`, `test`, `ci`, or `perf` commits | **patch** | Internal-only changes still ship a patch version |

**Decision tree:**

```
IF any commit message contains "BREAKING CHANGE:" OR starts with "feat!" OR "fix!"
  -> major

ELSE IF any PR title or commit starts with "feat"
  -> minor

ELSE IF any PR title or commit starts with "fix"
  -> patch

ELSE
  -> patch  (default: docs/chore/refactor/test/ci/perf only)
```

**How Risa checks the signals:**

```shell
last=$(git tag --list 'v*' --sort=-v:refname | head -1)
range="${last:+${last}..}HEAD"

# breaking?
if git log "$range" --oneline | grep -qiE 'BREAKING CHANGE|^feat!|^fix!|^feat\(!|^fix\(!'
  then BUMP_TYPE=major
# new feature?
elif git log "$range" --oneline | grep -qiE '^feat(\(.+\))?:'
  then BUMP_TYPE=minor
else
  BUMP_TYPE=patch
fi

# Compute the version
CUR=$(git describe --tags --abbrev=0 2>/dev/null | sed 's/^v//' || echo "0.0.0")
bash scripts/bump.sh "$BUMP_TYPE" --yes   # bump.sh accepts patch|minor|major
```

For CalVer repos, `NEW_VERSION` is always `YYYY.M.D.N` — no major/minor/patch distinction.

IF the repo has no `scripts/bump.sh` that accepts a bump type -> compute the explicit version number manually:

```shell
IFS='.' read -r major minor patch <<< "$CUR"
case "$BUMP_TYPE" in
  major) NEW_VERSION="$((major + 1)).0.0" ;;
  minor) NEW_VERSION="${major}.$((minor + 1)).0" ;;
  patch) NEW_VERSION="${major}.${minor}.$((patch + 1))" ;;
esac
```

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

> **Lockfile sync:** after stamping, if the repo has a `uv.lock` or `Cargo.lock`, regenerate it so CI passes. The bump script does this automatically. If it's missing, run `uv lock` or `cargo update` manually before opening the prep PR.

> Match the target repo's release commit prefix — read its workflow before committing. The common convention is `chore(release):`.

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

## Rolling window (2 releases)

`CHANGELOG.md` keeps only the newest 2 releases: the current release (full New / Fixed / Changed) plus a summary of the previous release. Older releases are dropped — the version still exists as a git tag, so the file stays short without losing history.

| Release | `CHANGELOG.md` contains |
|---|---|
| v1 | v1 (full) |
| v2 | v2 (full) + summary of v1 |
| v3 | v3 (full) + summary of v2 (v1 dropped) |

The summary of the previous release is one tight paragraph per group (New / Fixed / Changed) — the gist, not every bullet. `scripts/changelog.sh` keeps the newest 2 blocks and drops the rest; older tags remain in git.