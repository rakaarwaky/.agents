# Setup step 1 — version scheme

Pick the scheme from the project's language:

| Project type      | Scheme                                 | Where it is stamped                  |
| ----------------- | -------------------------------------- | ------------------------------------ |
| Python            | CalVer `YYYY.M.D.N` or SemVer `vX.Y.Z` | `pyproject.toml` `[project] version` |
| Node / TypeScript | SemVer `X.Y.Z`                         | `package.json` `"version"`           |
| Rust              | SemVer `X.Y.Z`                         | `Cargo.toml` `[package] version`     |

If a version file exists, read its current version and confirm the scheme matches the project's existing tags. If no version file exists, create one matching the language and stamp `0.0.1` as the baseline.