# Setup step 4 — bump script

Create `scripts/bump.sh` that stamps the version, runs git-cliff, and commits:

```bash
#!/usr/bin/env bash
set -euo pipefail
VERSION="${1:?usage: bump.sh <version>}"
CHANGELOG="CHANGELOG.md"

# 1. stamp version (adjust sed for the repo's version file)
sed -i -E 's/^version = .*/version = "'"$VERSION"'"/' pyproject.toml

# 2. changelog via git-cliff
git-cliff --unreleased --tag "$VERSION" --prepend "$CHANGELOG"

# 3. commit
git add pyproject.toml "$CHANGELOG" cliff.toml 2>/dev/null || true
git commit -m "chore(release): $VERSION"
```

Mark it executable:

```shell
chmod +x scripts/bump.sh
```