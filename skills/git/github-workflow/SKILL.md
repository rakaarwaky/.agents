---
name: github-workflow
description: "Umbrella for GitHub auth, repo management, issues, PRs, Mergify, and releases. Routes to sibling skills for issue-to-PR, PR babysitting, and releasing pipelines."
when-to-use: "Use for GitHub auth setup (gh CLI or git-only), repo clone/create/fork/configure, repo settings and Actions, gitignore audit. For issue-to-PR work use issue-worker; for PR watch/fix/merge use pr-babysit; for release prep and publish use releasing. This skill owns the auth helper scripts (gh-env.sh, git-credential-token.py)."
argument-hint: "<auth | repo> <subcommand> [flags]"
---

# GitHub Workflow

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **Auth prerequisite.** Authenticated with GitHub before any repo or pipeline operation. Source `scripts/gh-env.sh` for auth and repo detection rather than re-implementing the fallback chain. | `gh auth status` exits 0, or git credential helper is configured. |
| R2 | **Prefer `gh`.** Use `gh` commands; fall back to `git` + `curl` only where `gh` lacks coverage. | Commands use `gh` when available. |
| R3 | **Lane signal.** Lane is determined by physical signal: `HERMES_AGENT=1` → Hermes lane; `GROK_AGENT=1` → Grok lane; unset → stop and report. Never guess. | Environment variable checked before dispatch. |
| R4 | **Scope boundary.** This skill owns auth and repo management. Issue-to-PR pipeline → `issue-worker`. PR watch/fix/merge → `pr-babysit`. Release prep/publish → `releasing`. Issue creation → `issue-maker`. Never duplicate sibling pipeline logic here. | No pipeline steps duplicated from sibling skills. |
| R5 | **Token scopes.** `repo`, `workflow`, `read:org` (90-day expiration recommended). | `gh auth status` shows required scopes. |
| R6 | **Git identity.** Configure `user.name` and `user.email`; required for commits. | `git config user.name` and `git config user.email` return values. |
| R7 | **Max scope.** Auth job touches only credential/config files. Repo job touches only the target repository's remotes, settings, and Actions configuration. Max 2 retry iterations per failing check. Forbidden: modifying source code, creating commits, pushing branches. | `git diff --name-only` shows no source changes. |

## Routing

| Step      | File                                                 | Purpose                                                                                                                                 |
| --------- | ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Auth      | [`references/auth.md`](references/auth.md)           | Detection flow, `gh` CLI login (browser, device, hosts.yml fallback), git-only HTTPS PAT or SSH setup, API-without-gh, troubleshooting. |
| Clone     | [`references/clone.md`](references/clone.md)         | `git clone` and `gh repo clone`.                                                                                                        |
| Create    | [`references/create.md`](references/create.md)       | `gh repo create`.                                                                                                                       |
| Fork      | [`references/fork.md`](references/fork.md)           | `gh repo fork` and sync.                                                                                                                |
| Settings  | [`references/setting.md`](references/setting.md)     | `gh repo edit` + branch protection.                                                                                                     |
| Actions   | [`references/action.md`](references/action.md)       | `gh workflow` / `gh run` / `gh secret` / `gh release`.                                                                                  |
| Gitignore | [`references/gitignore.md`](references/gitignore.md) | Three-way diff + `git check-ignore -v`.                                                                                                 |
| Info      | [`references/info.md`](references/info.md)           | `gh repo view` / `gh repo list` / `gh search repos`.                                                                                    |
