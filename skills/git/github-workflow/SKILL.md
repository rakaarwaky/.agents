---
name: github-workflow
description: "Umbrella for GitHub auth, repo management, issues, PRs, and releases."
when-to-use: "Use for GitHub auth setup (gh CLI or git-only), repo clone/create/fork/configure, repo settings and Actions, gitignore audit."
argument-hint: "<auth | repo> <subcommand> [flags]"
---

# GitHub Workflow

Manage GitHub authentication, repository lifecycle, organization settings, workflow actions, and gitignore audits through `gh` CLI commands and git-native fallbacks.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Authenticate with GitHub before any repo or pipeline operation using `scripts/gh-env.sh` for auth and repo detection. | `gh auth status` exits 0, or git credential helper is configured. |
| R2 | Prefer `gh` commands over raw curl, falling back to git and curl only when `gh` lacks coverage. | Commands use `gh` when available. |
| R3 | Determine execution lane via physical signal: `HERMES_AGENT=1` or `GROK_AGENT=1`; never guess lane. | Environment variable checked before dispatch. |
| R4 | Enforce scope boundary: this skill owns auth and repo management; delegate issues, babysitting, and releasing to dedicated skills. | No pipeline steps duplicated from sibling skills. |
| R5 | Require token scopes: `repo`, `workflow`, `read:org`. | `gh auth status` shows required scopes. |
| R6 | Configure git identity (`user.name`, `user.email`) prior to creating commits. | `git config user.name` and `git config user.email` return values. |
| R7 | Confine modifications to credentials/configs for auth jobs and remotes/settings for repo jobs; never modify source code. | `git diff --name-only` shows no source changes. |
| R8 | Use imperative English in documentation and third-person phrasing in metadata descriptions. | No first-person pronouns in body or references. |
| R9 | Read `scripts/gh-env.sh` to resolve `$GH_OWNER` and `$GH_REPO` rather than hardcoding values. | `source scripts/gh-env.sh` runs before any repo operation. |
| R10 | Execute reference files in sequence: Auth -> Clone/Create/Fork -> Settings/Actions -> Gitignore -> Info. | Reference files executed in Routing table order. |
| R11 | Resolve branching logic: follow auth troubleshooting on failure, use git-only paths if `gh` is missing, verify scopes on permission denial. | IF-THEN branches resolved before proceeding. |
| R12 | Require every repo operation to produce a verifiable state change before completing. | Completion criteria in each reference file met. |
| R13 | Handle errors via troubleshooting trees with a maximum of 2 retry attempts before stopping. | Error reported with cause and recovery attempt logged. |

## Routing

| Step | File | Purpose |
| ---- | ---- | ------- |
| Auth | [`references/auth.md`](references/auth.md) | Detection flow, `gh` CLI login (browser, device, hosts.yml fallback), git-only HTTPS PAT or SSH setup, API-without-gh, troubleshooting. |
| Clone | [`references/clone.md`](references/clone.md) | `git clone` and `gh repo clone`. |
| Create | [`references/create.md`](references/create.md) | `gh repo create`. |
| Fork | [`references/fork.md`](references/fork.md) | `gh repo fork` and sync. |
| Settings | [`references/setting.md`](references/setting.md) | `gh repo edit` + branch protection. |
| Actions | [`references/action.md`](references/action.md) | `gh workflow` / `gh run` / `gh secret` / `gh release`. |
| Gitignore | [`references/gitignore.md`](references/gitignore.md) | Three-way diff + `git check-ignore -v`. |
| Info | [`references/info.md`](references/info.md) | `gh repo view` / `gh repo list` / `gh search repos`. |
