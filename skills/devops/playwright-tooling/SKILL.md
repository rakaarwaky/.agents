---
name: playwright-tooling
description: Recover Playwright browser cache on restricted hosts.
when-to-use: "Use when playwright install times out on a network-restricted host, manually placed browser dirs are wiped every run, or headless-shell/FFmpeg is missing from the Playwright cache."
argument-hint: "[<browser>]"
---

# Playwright Tooling

Playwright browser infrastructure: cache recovery, headless Chromium setup, and mirror routing for network-restricted hosts.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Normalize browser directory names on disk: dashes normalize to underscores to prevent install wipes. | Check directory names under `~/.cache/ms-playwright/` use underscore format. |
| R2 | Create both marker files (`INSTALLATION_COMPLETE`) after every manual browser directory placement. | Verify existence of `INSTALLATION_COMPLETE` marker inside placed browser directory. |
| R3 | Route downloads through mirror paths when CDN is reachable via curl but blocked for Node fetch. | Test curl reachability versus Node client and configure mirror environment variables. |
| R4 | Use cache layout specification as single source of truth for exact directory naming and structure. | Validate cache layout against reference directory tables. |

## Routing

| Step | Reference | Purpose |
| ---- | --------- | ------- |
| Cache layout + recovery | [`references/cache-layout.md`](references/cache-layout.md) | Dir names, marker files, CDN-unreachable recovery procedure. |
| Verification | [`references/verify.md`](references/verify.md) | Post-placement checks: marker presence, install exit 0, headless launch. |
