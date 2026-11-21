# Setup step 3 — release workflow

Copy the template from [`../../templates/release.yml`](../../templates/release.yml) into the target repo:

```shell
cp <skill>/templates/release.yml <repo>/.github/workflows/release.yml
```

## If the repo already has release workflows

If the repo has any existing release workflow(s) (e.g. `auto-release.yml`, `tag-release-prs.yml`, or an existing `release.yml`):

1. **Read the existing workflow(s)** — note the job names, build commands, and release mechanism (draft or direct).
2. **Merge into a single `release.yml`** using the template structure:
   - `open-release-pr` job (workflow_dispatch only): compute version, bump, open PR to `main` with `release` label
   - `create-tag` job (on merged PR with `release` label): extract version, create and push the tag
   - `test` → `build` → `smoke-test` → `provenance` → `release` jobs (on tag push): build and publish
3. **Delete the other release workflow files** (any workflow that the merged `release.yml` now replaces) after confirming the merged `release.yml` covers their triggers.
4. **Adapt the template to the repo's language:**
   - Build command: `uv build` (Python), `cargo build --release` (Rust), `npm run build` (Node)
   - Smoke test: use the repo's actual CLI entry point
   - Provenance: add only if the repo publishes to a registry (PyPI, npm, crates.io)
5. **Base branch is `main`**, not `develop`.

## CI gate

Add or keep a `ci.yml` that runs tests + build on every push and PR. The `test` job in `release.yml` must pass before the release jobs run. If the repo uses `workflow_run` gating, keep it — but the release `test` job is the authoritative gate for the release pipeline.

## Verification

After writing the workflow:

```shell
# Dry-run the workflow YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))"
```

IF `python3` with PyYAML is not available, use `ruby -ryaml -e "YAML.load_file('.github/workflows/release.yml')" || true` as a fallback.
