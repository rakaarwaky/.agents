# Setup step 3 — release workflow

Scaffold `.github/workflows/release.yml` as tag-driven (builds and publishes on a tag push):

```yaml
name: Release
on:
  push:
    tags: ["v*.*.*"]
  workflow_dispatch:
    inputs:
      tag:
        description: "Release tag to build (e.g. v0.1.0)"
        required: true
        type: string
permissions:
  contents: write
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: <build command>          # e.g. uv build, npm ci && npm run build, cargo build --release
      - uses: softprops/action-gh-release@v2
        with:
          files: <dist artifacts>      # e.g. dist/*
          generate_release_notes: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Add a `ci.yml` that runs tests + build on every push and PR. Gate the release on green CI via `workflow_run`.