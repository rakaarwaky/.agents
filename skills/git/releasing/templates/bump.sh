#!/usr/bin/env bash
# bump.sh — multi-package, multi-language version bumper
#
# Usage:
#   bash scripts/bump.sh patch          # 1.2.3 → 1.2.4
#   bash scripts/bump.sh minor          # 1.2.3 → 1.3.0
#   bash scripts/bump.sh major          # 1.2.3 → 2.0.0
#   bash scripts/bump.sh 1.5.0          # explicit version
#   bash scripts/bump.sh --dry-run patch
#
# Options:
#   --dry-run       Show changes without applying
#   --no-commit     Skip git commit after bump
#   --no-changelog  Skip changelog generation
#   -y, --yes       Auto-confirm (no prompts)
#
# What it stamps:
#   1. The primary VERSION_FILE (Python / Rust / Node).
#   2. Every nested package version file discovered on disk
#      (modules/*/pyproject.toml, sub-packages/*/, Cargo workspace members,
#      a TypeScript package.json tree, or any other pattern you set).
#   3. The optional secondary TS_VERSION_FILE when a mixed-language repo
#      (e.g. Python + TypeScript) needs both stamped.
#   4. The lock file(s) via LOCK_CMD (uv lock, cargo update, npm install).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# ── Config (fill these in) ────────────────────────────────────────────────────
# <project-name>          : short repo name, used in commit messages
# <version-file>          : pyproject.toml | Cargo.toml | package.json | VERSION
# <lock-file>             : uv.lock | Cargo.lock | package-lock.json | go.sum
# <lock-command>          : uv lock | cargo update | npm install | (leave empty)
# <build-command>         : uv build | cargo build --release | npm run build
# <cli-entry>             : <your-cli> --help | (leave empty for non-CLI projects)
# <dist-dir>              : dist | target/release | (leave empty)
#
# Nested-package discovery (globs relative to PROJECT_ROOT, space-separated):
#   Python multi-package : "modules/*/pyproject.toml"
#   Rust workspace       : "crates/*/Cargo.toml"  (members with version.workspace inherit automatically)
#   Node monorepo        : "packages/*/package.json"
#   Set to an empty string "" to disable nested discovery.
PROJECT_NAME="<project-name>"
VERSION_FILE="${VERSION_FILE:-<version-file>}"
LOCK_FILE="${LOCK_FILE:-<lock-file>}"
LOCK_CMD="${LOCK_CMD:-<lock-command>}"
BUILD_CMD="${BUILD_CMD:-<build-command>}"
CLI_ENTRY="${CLI_ENTRY:-<cli-entry>}"
DIST_DIR="${DIST_DIR:-<dist-dir>}"
CHANGELOG="CHANGELOG.md"
CLIFF_TOML="cliff.toml"
TS_VERSION_FILE="${TS_VERSION_FILE:-packages/package.json}"
TS_LOCK_FILE="${TS_LOCK_FILE:-packages/package-lock.json}"
NESTED_VERSION_FILES="${NESTED_VERSION_FILES:-modules/*/pyproject.toml}"

DRY_RUN=false
NO_COMMIT=false
NO_CHANGELOG=false
AUTO=false
BUMP_TYPE=""
EXPLICIT_VERSION=""

# ── Parse args ────────────────────────────────────────────────────────────────
usage() {
  sed -n '3,21p' "$0" | sed 's/^#//; s/^ //'
  echo ""
  echo "Usage: bash scripts/bump.sh <patch|minor|major|X.Y.Z> [--dry-run] [--no-commit] [--no-changelog] [-y]"
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage ;;
    --dry-run) DRY_RUN=true; shift ;;
    --no-commit) NO_COMMIT=true; shift ;;
    --no-changelog) NO_CHANGELOG=true; shift ;;
    -y|--yes) AUTO=true; shift ;;
    patch|minor|major) BUMP_TYPE="$1"; shift ;;
    [0-9]*.[0-9]*.[0-9]*) EXPLICIT_VERSION="$1"; shift ;;
    *) echo "Unknown option: $1" >&2; usage ;;
  esac
done

if [[ -z "$BUMP_TYPE" && -z "$EXPLICIT_VERSION" ]]; then
  echo "Usage: bump.sh <patch|minor|major|X.Y.Z>" >&2
  exit 1
fi

# ── Helpers ───────────────────────────────────────────────────────────────────

version_from_file() {
  local file="$1"
  case "$file" in
    *.toml)
      grep -m1 '^version' "$file" | sed -E 's/^version *= *"([^"]+)".*$/\1/'
      ;;
    *.json)
      python3 -c "import json; print(json.load(open('$file')).get('version',''))" 2>/dev/null || true
      ;;
    VERSION|version.txt)
      head -1 "$file" | tr -d '[:space:]'
      ;;
    *)
      grep -m1 -E '^version|^__version__|^VERSION' "$file" | sed -E 's/.*["=:] *"?([0-9][^"]*)".*/\1/' || true
      ;;
  esac
}

current_version() {
  version_from_file "$VERSION_FILE"
}

bump_version() {
  local cur="$1" type="$2"
  IFS='.' read -r major minor patch <<< "${cur//[^0-9.]}"
  major="${major:-0}"; minor="${minor:-0}"; patch="${patch:-0}"
  case "$type" in
    patch) patch=$((patch + 1)) ;;
    minor) minor=$((minor + 1)); patch=0 ;;
    major) major=$((major + 1)); minor=0; patch=0 ;;
    *) echo "Invalid bump type: $type" >&2; return 1 ;;
  esac
  echo "${major}.${minor}.${patch}"
}

latest_tag() {
  git tag --merged HEAD --sort=-v:refname 2>/dev/null | grep -E '^v?[0-9]' | head -1 || true
}

stamp_version() {
  local ver="$1"
  case "$VERSION_FILE" in
    *.toml)
      sed -i -E "s/^version *= *\"[^\"]*\"/version = \"${ver}\"/" "$VERSION_FILE"
      ;;
    *.json)
      python3 - "$VERSION_FILE" "$ver" <<'PY'
import json, sys
path, ver = sys.argv[1], sys.argv[2]
with open(path) as f: data = json.load(f)
data['version'] = ver
with open(path, 'w') as f: json.dump(data, f, indent=2, ensure_ascii=False); f.write('\n')
PY
      ;;
    VERSION|version.txt)
      echo "$ver" > "$VERSION_FILE"
      ;;
    *)
      echo "Unknown version file format: $VERSION_FILE" >&2
      grep -q "$ver" "$VERSION_FILE" || sed -i -E "s/^[[:space:]]*(version|__version__|VERSION)[[:space:]]*=.*/\1 = \"${ver}\"/" "$VERSION_FILE"
      ;;
  esac
}

stamp_ts_version() {
  local ver="$1"
  [[ -n "${TS_VERSION_FILE:-}" && -f "$TS_VERSION_FILE" ]] || return 0
  python3 - "$TS_VERSION_FILE" "$ver" <<'PY'
import json, sys
path, ver = sys.argv[1], sys.argv[2]
with open(path) as f: data = json.load(f)
data['version'] = ver
with open(path, 'w') as f: json.dump(data, f, indent=2, ensure_ascii=False); f.write('\n')
PY
  echo "  ✓ Updated $TS_VERSION_FILE: $ver"
  # Keep the JS lockfile in sync when it mirrors the package version.
  if [[ -n "${TS_LOCK_FILE:-}" && -f "$TS_LOCK_FILE" ]]; then
    python3 - "$TS_LOCK_FILE" "$ver" <<'PY'
import json, sys
path, ver = sys.argv[1], sys.argv[2]
with open(path) as f: data = json.load(f)
data['version'] = ver
if 'packages' in data and '' in data['packages']:
    data['packages']['']['version'] = ver
with open(path, 'w') as f: json.dump(data, f, indent=2, ensure_ascii=False); f.write('\n')
PY
    echo "  ✓ Updated $TS_LOCK_FILE: $ver"
  fi
}

# Stamp every nested package version file that exists on disk (TOML or JSON).
# Cargo workspace members using version.workspace = true need no edit.
stamp_nested() {
  local ver="$1" f
  [[ -n "$NESTED_VERSION_FILES" ]] || return 0
  for f in $NESTED_VERSION_FILES; do
    [[ -f "$f" ]] || continue
    case "$f" in
      *.json)
        python3 - "$f" "$ver" <<'PY'
import json, sys
path, ver = sys.argv[1], sys.argv[2]
with open(path) as f: data = json.load(f)
data['version'] = ver
with open(path, 'w') as f: json.dump(data, f, indent=2, ensure_ascii=False); f.write('\n')
PY
        ;;
      *)
        sed -i -E "s/^version *= *\"[^\"]*\"/version = \"${ver}\"/" "$f"
        ;;
    esac
    echo "  ✓ Updated $f: $ver"
  done
}

generate_changelog() {
  local ver="$1"
  if [[ ! -f "$CHANGELOG" ]]; then
    echo "# Changelog" > "$CHANGELOG"
  fi

  if command -v git-cliff >/dev/null 2>&1 && [[ -f "$CLIFF_TOML" ]]; then
    # First release ever (no prior version heading) -> build from full history.
    local release_count
    release_count="$(grep -cE '^## (\[)?(v|[0-9])' "$CHANGELOG" 2>/dev/null || echo 0)"
    if [[ "$release_count" -eq 0 ]]; then
      git-cliff --unreleased --tag "$ver" --prepend "$CHANGELOG" || \
        git-cliff "HEAD" --tag "$ver" --output /tmp/cliff-full.md
    else
      git-cliff --unreleased --tag "$ver" --prepend "$CHANGELOG"
    fi
  else
    local date last_tag range
    date="$(date -u +%Y-%m-%d)"
    last_tag="$(latest_tag)"
    if [[ -n "$last_tag" ]]; then
      range="${last_tag}..HEAD"
    else
      range="HEAD"
    fi

    {
      echo "## ${ver} (${date})"
      echo ""
      git log "$range" --pretty=format:'- %s' 2>/dev/null | grep -vE '^(chore|docs|test|refactor|ci|Merge)' | head -30
      echo ""
    } | cat - "$CHANGELOG" > /tmp/changelog_new
    python3 -c "
with open('/tmp/changelog_new') as f: new = f.read()
with open('$CHANGELOG') as f: old = f.read()
lines = old.split('\n', 1)
header = lines[0] + '\n'
rest = lines[1] if len(lines) > 1 else ''
entries = new.split('\n', 1)
body = entries[1] if len(entries) > 1 else ''
with open('$CHANGELOG', 'w') as f: f.write(header + body + rest)
"
    rm -f /tmp/changelog_new
  fi

  if [[ -f "scripts/changelog.sh" ]]; then
    bash scripts/changelog.sh
  fi
}

sync_lockfile() {
  if [[ -z "$LOCK_CMD" ]]; then
    echo "  · No lock command configured — skipping"
    return
  fi
  if [[ -z "$LOCK_FILE" || ! -f "$LOCK_FILE" ]]; then
    echo "  · No lock file ($LOCK_FILE) — skipping"
    return
  fi
  if ! command -v "${LOCK_CMD%% *}" &>/dev/null; then
    echo "  · ${LOCK_CMD%% *} not installed — skipping lock sync"
    return
  fi
  $LOCK_CMD 2>/dev/null || true
  if git diff --quiet "$LOCK_FILE" 2>/dev/null; then
    echo "  ✓ $LOCK_FILE unchanged"
  else
    git add "$LOCK_FILE"
    echo "  ✓ Regenerated $LOCK_FILE for $NEW"
  fi
}

# ── Resolve version ───────────────────────────────────────────────────────────

if [[ ! -f "$VERSION_FILE" ]]; then
  echo "Version file not found: $VERSION_FILE" >&2
  exit 1
fi

CUR="$(current_version)"
if ! [[ "$CUR" =~ ^[0-9]+(\.[0-9]+)*$ ]]; then
  echo "Cannot parse current version: '$CUR' from $VERSION_FILE" >&2
  exit 1
fi

if [[ -n "$BUMP_TYPE" ]]; then
  NEW="$(bump_version "$CUR" "$BUMP_TYPE")"
else
  NEW="$EXPLICIT_VERSION"
fi

echo ""
echo "  Project:  $PROJECT_NAME"
echo "  Current:  $CUR"
echo "  New:      $NEW"
echo ""

if $DRY_RUN; then
  echo "[DRY-RUN] Would update: $VERSION_FILE, nested packages, $TS_VERSION_FILE, $CHANGELOG"
  exit 0
fi

if [[ "$AUTO" = false ]]; then
  read -rp "Bump to $NEW? [Y/n] " ans
  [[ "$ans" =~ ^[nN] ]] && { echo "Aborted."; exit 0; }
fi

# ── Apply ─────────────────────────────────────────────────────────────────────

stamp_version "$NEW"
echo "  ✓ Updated $VERSION_FILE: $NEW"
stamp_nested "$NEW"
stamp_ts_version "$NEW"

if ! $NO_CHANGELOG; then
  generate_changelog "$NEW"
  echo "  ✓ Updated $CHANGELOG"
fi

sync_lockfile "$NEW"

# ── Commit ────────────────────────────────────────────────────────────────────

if [[ "$NO_COMMIT" = false ]]; then
  git add "$VERSION_FILE" $NESTED_VERSION_FILES "$TS_VERSION_FILE" "$TS_LOCK_FILE" "$CHANGELOG" 2>/dev/null || true
  [[ -f "$CLIFF_TOML" ]] && git add "$CLIFF_TOML" 2>/dev/null || true
  [[ -f "scripts/bump.sh" ]] && git add "scripts/bump.sh"
  [[ -n "$LOCK_FILE" && -f "$LOCK_FILE" ]] && git add "$LOCK_FILE" 2>/dev/null || true
  if git diff --cached --quiet; then
    echo "  No version files changed — nothing to commit"
  else
    git commit -m "chore(release): $NEW"
    echo "  ✓ Committed"
  fi
fi

echo ""
echo "  Done: $CUR → $NEW"
