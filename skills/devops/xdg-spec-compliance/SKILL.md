---
name: xdg-spec-compliance
description: "Audit and fix XDG Base Directory compliance in a repo (data/config/cache/state paths, 0700 dirs, 0600 secrets, precedence). Use when the app resolves paths with `expanduser`/`Path.home`, writes logs outside `$XDG_STATE_HOME`, or ships world-readable secrets."
when-to-use: "Use when auditing a repo's path resolution against the XDG Base Directory spec: relative/tilde rejection, precedence (shell env > XDG file > .env), dir and file permissions, and vendor subdirs."
argument-hint: "[<repo-root>]"
---

# XDG Base Directory Compliance

Audit and fix repository path resolution against the XDG Base Directory specification, enforcing directory permissions, secret security, environment variable precedence, and clean test sandboxing.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Quote the authoritative XDG v0.8 specification directly rather than relying on ungrounded path assumptions. | Verify rules and path mappings adhere to the official Freedesktop specification. |
| R2 | Reproduce path resolution and permission inheritance issues before asserting violations or making code changes. | Run verification probes testing relative path rejections and umask inheritance. |
| R3 | Clean up all test probe artifacts and temporary files, leaving `git status` clean after audit runs. | Check repository git status to ensure zero residual probe files. |
| R4 | Enforce strict file and directory permissions: 0700 for private XDG directories and 0600 for secrets. | Inspect created paths with `stat` to confirm mode permissions. |
| R5 | Preserve precedence order: shell environment variables override XDG default locations, which override `.env`. | Verify resolution fallback order in path resolution tests. |

## Routing

| Step | Reference | Purpose |
| ---- | --------- | ------- |
| Audit order | [`references/audit-order.md`](references/audit-order.md) | The four cheapest-signal-first checks: path grep, LOG/state location, write/read split, repro. |
| The rules projects break | [`references/rules.md`](references/rules.md) | The seven spec rules: absolute-only, empty/unset default, 0700 dirs, 0600 secrets, precedence, vendor subdir, `XDG_RUNTIME_DIR`. |
| Bash installer | [`references/bash-installer.md`](references/bash-installer.md) | Installer rules: absoluteness helper, 0700 tree, venv install, entry points. |
| Test it without touching the user's home | [`references/testing-sandbox.md`](references/testing-sandbox.md) | The import-time sandbox, the asserts, the fake-green guards, and the lazy log handler. |
| Destructive provisioning | [`references/destructive-provisioning.md`](references/destructive-provisioning.md) | Stale-dir rename instead of `rmtree`, and the symlink exfiltration rule. |
