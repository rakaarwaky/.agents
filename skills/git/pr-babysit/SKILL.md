---
name: pr-babysit
description: "Watch a PR, fix CI, merge via Mergify queue."
when-to-use: "Triggers on \"/pr-babysit\". Phrasing: \"watch PR 123 until green\", \"babysit PR 123 and merge when ready\", \"fix issue #123 and open a PR\", \"keep fixing PR 123 until it can merge\", \"pr-babysit add 123\", \"pr-babysit ship 123\", \"pr-babysit setup 123\"."
argument-hint: "<add|ship|setup> <pr link|number>"
---

# PR Babysitter

Watch pull requests, parse failing CI logs, push incremental fixes, configure Mergify merge queues, and safely merge pull requests through coordinated agent lanes.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Determine execution lane strictly from physical environment variables (`HERMES_AGENT=1` or `GROK_AGENT=1`); stop if unset. | Verify agent attribution environment variable before loading lane references. |
| R2 | Read only the winning lane's references; never inspect or load the alternate lane's files. | Confirm reference file accesses match detected lane. |
| R3 | Enforce scope ceilings: maximum 3 fix commits per pass, no subagent dispatch inside a single worktree. | Count fix commits and verify single-agent execution in worktree. |
| R4 | Never modify skills outside `skills/git/pr-babysit/` during babysitting runs. | Check modified files match babysit skill path. |
| R5 | Verify live CI status and merge state directly on GitHub before declaring PR babysitting complete. | Run `gh pr view` to verify CI check runs and merge status. |

## Routing

| Step | Reference | Purpose |
| ----: | --------- | ------- |
| Hermes 0 | [`references/hermes/step-0-watch-and-spawn.md`](references/hermes/step-0-watch-and-spawn.md) | Verify auth, register PR in watchlist, compose detailed brief for Grok, spawn Grok worktree |
| Hermes 1 | [`references/hermes/step-1-wait-and-reverify.md`](references/hermes/step-1-wait-and-reverify.md) | Wait for Grok pass, read report, reverify CI on live head |
| Hermes 2 | [`references/hermes/step-2-merge.md`](references/hermes/step-2-merge.md) | Verify merge landed live on GitHub, retire Grok worktree |
| Hermes 3 | [`references/hermes/step-3-final-report.md`](references/hermes/step-3-final-report.md) | Final report to user with fixes, outcome, and watchlist state |
| Grok Ship 0 | [`references/grok/ship/step-0-add-pr.md`](references/grok/ship/step-0-add-pr.md) | PR details, repo, head/base refs, set ship: true |
| Grok Ship 1 | [`references/grok/ship/step-1-watch-ci.md`](references/grok/ship/step-1-watch-ci.md) | Watch CI until green |
| Grok Ship 2 | [`references/grok/ship/step-2-auto-fix.md`](references/grok/ship/step-2-auto-fix.md) | CI red: parse logs, fix code, Conventional Commits, push |
| Grok Ship 3 | [`references/grok/ship/step-3-decision-tree.md`](references/grok/ship/step-3-decision-tree.md) | Conflict resolution, review threads; troubleshooter: [`references/grok/ship/step-3-troubleshoot.md`](references/grok/ship/step-3-troubleshoot.md) |
| Grok Ship 4 | [`references/grok/ship/step-4-mergify-detect.md`](references/grok/ship/step-4-mergify-detect.md) | Detect Mergify on repo; bootstrap `.mergify.yml` setup PR if missing |
| Grok Ship 5 | [`references/grok/ship/step-5-mergify-diagnostics.md`](references/grok/ship/step-5-mergify-diagnostics.md) | Check `mergify events`, quarantine flaky tests, upload JUnit |
| Grok Ship 6 | [`references/grok/ship/step-6-merge-protections.md`](references/grok/ship/step-6-merge-protections.md) | Check active freezes (`mergify freeze`), dependencies, stacked PRs |
| Grok Ship 7 | [`references/grok/ship/step-7-merge.md`](references/grok/ship/step-7-merge.md) | Merge via Mergify queue, monitor queue, fallback to direct merge |
| Grok Add 0 | [`references/grok/add/step-0-add-pr.md`](references/grok/add/step-0-add-pr.md) | PR details, repo, head/base refs, set ship: false |
| Grok Add 1 | [`references/grok/add/step-1-watch-ci.md`](references/grok/add/step-1-watch-ci.md) | Watch CI until green |
| Grok Add 2 | [`references/grok/add/step-2-auto-fix.md`](references/grok/add/step-2-auto-fix.md) | CI red: parse logs, fix code, Conventional Commits, push |
| Grok Add 3 | [`references/grok/add/step-3-decision-tree.md`](references/grok/add/step-3-decision-tree.md) | Conflict resolution, review threads; troubleshooter: [`references/grok/add/step-3-troubleshoot.md`](references/grok/add/step-3-troubleshoot.md) |
| Grok Setup 0 | [`references/grok/setup/step-0-detect.md`](references/grok/setup/step-0-detect.md) | Detect Mergify config; bootstrap `.mergify.yml` if missing |
| Grok Setup 1 | [`references/grok/setup/step-1-configure.md`](references/grok/setup/step-1-configure.md) | Write merge rules, validate, open configuration PR |
