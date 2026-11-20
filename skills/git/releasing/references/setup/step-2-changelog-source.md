# Setup step 2 — git-cliff + cliff.toml

git-cliff is the changelog source. There is no alternative.

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

Create `cliff.toml` with a `commit_parsers` array (first match wins; `group` sets the section, `skip = true` drops it):

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

Adjust `group` names and skip patterns to the project's commit conventions.