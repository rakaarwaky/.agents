# Setup step 4 — bump script

## Copy into the Orca worktree

## Copy into the Orca worktree

Set up the bump script inside an Orca worktree for the target repo — never in the main clone. The main clone stays clean.

```shell
cp <skill>/templates/bump.sh <worktree path>/scripts/bump.sh
cp <skill>/templates/changelog.sh <worktree path>/scripts/changelog.sh
chmod +x <worktree path>/scripts/bump.sh <worktree path>/scripts/changelog.sh
```

The template is a **multi-package, multi-language** bumper. One run stamps the version into every package that exists in the project — no exceptions.

## How discovery works

The script reads the version from the primary `VERSION_FILE`, then stamps it into:

1. `VERSION_FILE` itself (the root package).
2. **Every nested package version file** matched by `NESTED_VERSION_FILES` (a space-separated glob, relative to the project root). All matches that exist on disk are stamped — TOML with `sed`, JSON with Python.
3. `TS_VERSION_FILE` + `TS_LOCK_FILE` when the repo is mixed-language (e.g. Python + TypeScript).
4. The lock file, via `LOCK_CMD` (`uv lock`, `cargo update`, `npm install`).

The key invariant: **after a bump, no version file in the repo may disagree with the root.** If a test or gate asserts that every package declares the root version, this is what keeps it passing.

## Pick the config for the target repo

| Repo shape | `VERSION_FILE` | `NESTED_VERSION_FILES` | Extra |
|---|---|---|---|
| Single Python package | `pyproject.toml` | `""` (empty) | — |
| Python monorepo (feature modules) | `pyproject.toml` | `modules/*/pyproject.toml` | `LOCK_CMD=uv lock` |
| Python + TypeScript | `pyproject.toml` | `modules/*/pyproject.toml` | `TS_VERSION_FILE=packages/package.json`, `TS_LOCK_FILE=packages/package-lock.json` |
| Rust workspace | `Cargo.toml` | `crates/*/Cargo.toml` | members with `version.workspace = true` inherit automatically; only crates with a literal `version` need the glob |
| Node monorepo | `package.json` | `packages/*/package.json` | `LOCK_CMD=npm install` |

Cargo note: workspace members that use `version.workspace = true` pick up the change with no per-crate edit — the glob only matters for members that declare a literal version.

## What the script does

1. Parses `--dry-run`, `--no-commit`, `--no-changelog`, `-y` flags
2. Accepts either a bump type (`patch`/`minor`/`major`) or an explicit `X.Y.Z` version
3. Stamps the version into the root, all nested packages, and the TS package
4. Generates the changelog: uses `git-cliff` if `cliff.toml` exists, otherwise a `git log`-based entry. For a **first-ever release** (no `## [x.y.z]` heading yet) it builds from the full commit history; otherwise it uses the tag-based range
5. Trims `CHANGELOG.md` to the newest 2 releases (calls `scripts/changelog.sh` if present)
6. **Syncs the lockfile** via `LOCK_CMD` (e.g. `uv lock`) so CI's `uv sync --locked` check passes
7. Commits with `chore(release): $NEW_VERSION`, adding every version file it touched

Risa's release lane calls it with the bump type: `bash scripts/bump.sh minor --yes` — the bump type is decided by the decision tree in [`../release/step-0-version-bump.md`](../release/step-0-version-bump.md) section 1.

## Verify before you commit

After the bump, confirm no package drifted:

```shell
# Python: every pyproject (root + nested) agrees with the root
grep -m1 '^version' pyproject.toml
for f in $NESTED_VERSION_FILES; do [ -f "$f" ] && grep -m1 '^version' "$f"; done
```

If a repo ships a packaging-metadata gate (a test that fails when any package version disagrees with the root), run it after the bump to confirm all packages are in sync before opening the release prep PR.
