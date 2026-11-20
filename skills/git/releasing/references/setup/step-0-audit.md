# Setup step 0 — audit

Working directory: the repo (an Orca worktree for this repo).

Run this to see what is missing:

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

Fill only what is missing. If all four exist, skip to [step-5-handoff.md](step-5-handoff.md).