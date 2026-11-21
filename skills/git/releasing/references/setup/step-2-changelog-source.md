# Setup step 2 — git-cliff + cliff.toml

git-cliff is the changelog source. There is no alternative.

## Changelog state handling (first release vs existing versions)

The release step must detect whether `CHANGELOG.md` already has version entries:

- **No previous version (first release ever):** the file has only the header (no `## [x.y.z]` entries). The release step must generate the full changelog from ALL commits, not just commits since the last tag. git-cliff with a range covering the whole history produces this correctly.
- **Has previous version(s):** `CHANGELOG.md` contains one or more `## [x.y.z]` entries. The release step generates notes only for commits since the newest existing tag, then prepends them. The rolling-window trim (`scripts/changelog.sh`) keeps the newest 2 releases.

To detect: count release headings with `grep -cE '^## (\[)?(v|[0-9])' CHANGELOG.md`. Zero means first release — use the full-history range. One or more means an existing changelog — use the tag-based range.

Install if missing:

```shell
if ! command -v git-cliff >/dev/null 2>&1; then
  cargo install git-cliff 2>/dev/null \
    || brew install git-cliff 2>/dev/null \
    || (curl -L -o /tmp/git-cliff.tar.gz \
         "https://github.com/oracle/git-cliff/releases/latest/download/git-cliff-x86_64-unknown-linux-musl.tar.gz" \
         && tar -xzf /tmp/git-cliff.tar.gz -C /tmp \
         && sudo mv /tmp/git-cliff /usr/local/bin/)
  git-cliff --version
fi
```

Create `cliff.toml` with a valid `commit_parsers` array (first match wins; `group` sets the section, `skip = true` drops it). The header advertises the 2-release rolling window:

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

Adjust `group` names and skip patterns to the project's commit conventions.

Copy the trim script into the repo so the release step can call it:

```shell
mkdir -p scripts
cp <skill>/templates/changelog.sh scripts/changelog.sh
chmod +x scripts/changelog.sh
```

Recovery: if `cliff.toml` generation fails validation (`git-cliff --print-config`), fix the config — do not fall back to another changelog source.