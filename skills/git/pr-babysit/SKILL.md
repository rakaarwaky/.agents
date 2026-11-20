---
name: pr-babysit
description: "Watch a PR, fix CI, merge via Mergify queue."
when-to-use: "Triggers on \"/pr-babysit\". Phrasing: \"watch PR 123 until green\", \"babysit PR 123 and merge when ready\", \"fix issue #123 and open a PR\", \"keep fixing PR 123 until it can merge\", \"pr-babysit ship 123\", \"pr-babysit setup 123\", \"pr-babysit repo add owner/repo\", \"pr-babysit repo remove owner/repo\", \"watch repo for new prs\"."
argument-hint: "<ship|setup|repo> <pr link|number|repo name>"
---

# PR Babysitter

Watch pull requests, parse failing CI logs, push incremental fixes, configure Mergify merge queues, and safely merge pull requests through coordinated agent lanes.

## Security gate (mandatory)

Only PRs authored by `rakaarwaky` are processed, fixed, or merged. Enforced at three layers:

1. Orca automation `from=me` filter on `pr_opened`, plus author check inside every automation prompt.
2. Mergify `author = rakaarwaky` in `queue_conditions` and `auto_merge_conditions` of every repo's `.mergify.yml`.
3. The lane's own author check in `ship/step-0-add-pr.md` step 0.2 and `ship/step-7-merge.md`.

A PR from any other author is rejected and reported to the owner. Never override this gate.

## Auto-merge authorized

SOUL.md authorizes auto-merge via the Mergify queue for `rakaarwaky`-authored PRs once CI is green and no reviews request changes. Do not ask the owner for merge permission.

## Watchlist

`/home/raka/.agents/develop/repo.json` is the source of truth for watched repos (symlinked to `/home/raka/.orca/bots/reles/repo.json`). A PR is only processed when its repo is present there. `repo add` and `repo remove` maintain it.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Determine execution lane strictly from physical environment variables (`HERMES_AGENT=1` or `GROK_AGENT=1`); stop if unset. | Verify agent attribution environment variable before loading lane references. |
| R2 | Read only the winning lane's references; never inspect or load the alternate lane's files. | Confirm reference file accesses match detected lane. |
| R3 | Enforce scope ceilings: maximum 3 fix commits per pass, no subagent dispatch inside a single worktree. | Count fix commits and verify single-agent execution in worktree. |
| R4 | Never modify skills outside `skills/git/pr-babysit/` during babysitting runs. | Check modified files match babysit skill path. |
| R5 | Verify live CI status and merge state directly on GitHub before declaring PR babysitting complete. | Run `gh pr view` to verify CI check runs and merge status. |
| R6 | Reject any PR whose author is not `rakaarwaky`, and any repo absent from `repo.json`. | Check author and watchlist before processing. |

## Routing

| Step | Reference | Purpose |
| ----: | --------- | ------- |
| Hermes 0 | [`references/hermes/step-0-watch-and-spawn.md`](references/hermes/step-0-watch-and-spawn.md) | Verify auth, register PR in watchlist, compose detailed brief for Grok, spawn Grok worktree |
| Hermes 1 | [`references/hermes/step-1-wait-and-reverify.md`](references/hermes/step-1-wait-and-reverify.md) | Wait for Grok pass, read report, reverify CI on live head |
| Hermes 2 | [`references/hermes/step-2-merge.md`](references/hermes/step-2-merge.md) | Verify merge landed live on GitHub, retire Grok worktree |
| Hermes 3 | [`references/hermes/step-3-final-report.md`](references/hermes/step-3-final-report.md) | Final report to user with fixes, outcome, and watchlist state |
| Grok Ship 0 | [`references/grok/ship/step-0-add-pr.md`](references/grok/ship/step-0-add-pr.md) | Author gate, repo watchlist check, undraft when green, register PR with ship: true |
| Grok Ship 1 | [`references/grok/ship/step-1-watch-ci.md`](references/grok/ship/step-1-watch-ci.md) | Watch CI until green |
| Grok Ship 2 | [`references/grok/ship/step-2-auto-fix.md`](references/grok/ship/step-2-auto-fix.md) | CI red: parse logs, fix code, Conventional Commits, push |
| Grok Ship 3 | [`references/grok/ship/step-3-decision-tree.md`](references/grok/ship/step-3-decision-tree.md) | Conflict resolution, review threads; troubleshooter: [`references/grok/ship/step-3-troubleshoot.md`](references/grok/ship/step-3-troubleshoot.md) |
| Grok Ship 4 | [`references/grok/ship/step-4-mergify-detect.md`](references/grok/ship/step-4-mergify-detect.md) | Detect Mergify; bootstrap `.mergify.yml` with author gate if missing |
| Grok Ship 5 | [`references/grok/ship/step-5-mergify-diagnostics.md`](references/grok/ship/step-5-mergify-diagnostics.md) | Check `mergify events`, quarantine flaky tests, upload JUnit |
| Grok Ship 6 | [`references/grok/ship/step-6-merge-protections.md`](references/grok/ship/step-6-merge-protections.md) | Check active freezes (`mergify freeze`), dependencies, stacked PRs |
| Grok Ship 7 | [`references/grok/ship/step-7-merge.md`](references/grok/ship/step-7-merge.md) | Re-check author gate, auto-merge via Mergify queue, monitor queue, fallback |
| Grok Setup 0 | [`references/grok/setup/step-0-template.md`](references/grok/setup/step-0-template.md) | Mergify config template with mandatory `author = rakaarwaky` gate |
| Grok Setup 1 | [`references/grok/setup/step-1-detect.md`](references/grok/setup/step-1-detect.md) | Detect Mergify config; bootstrap `.mergify.yml` if missing |
| Grok Setup 2 | [`references/grok/setup/step-2-configure.md`](references/grok/setup/step-2-configure.md) | Write merge rules, validate, open configuration PR |
| Grok Repo 0 | [`references/grok/repo/step-0-add-repo.md`](references/grok/repo/step-0-add-repo.md) | Register/remove repo in `repo.json`; initialize known PRs |
| Grok Repo 1 | [`references/grok/repo/step-1-detect-new-prs.md`](references/grok/repo/step-1-detect-new-prs.md) | Detect new PRs via GitHub webhook forwarding or polling |
| Grok Repo 2 | [`references/grok/repo/step-2-spawn-session.md`](references/grok/repo/step-2-spawn-session.md) | Spawn isolated Grok session in Orca worktree for new PR |
