---
name: pr-babysit
description: "Watch a PR, fix CI, merge via Mergify queue."
when-to-use: "Triggers on \"/pr-babysit\". Phrasing: \"watch PR 123 until green\", \"babysit PR 123 and merge when ready\", \"fix issue #123 and open a PR\", \"keep fixing PR 123 until it can merge\", \"pr-babysit add 123\", \"pr-babysit ship 123\", \"pr-babysit setup 123\"."
argument-hint: "<add|ship|setup> <pr link|number>"
---
# PR Babysitter

## Rules

This file is the lane identification step only. The lane is determined from physical signals, in this order. Each is observable without asking the agent to name itself. Each agent's launcher stamps a fixed attribution env var into every command it runs. The model cannot set these; only the launcher can.

```bash
if [[ -n "${HERMES_AGENT:-}" ]]; then echo HERMES
elif [[ -n "${GROK_AGENT:-}" ]]; then echo GROK
else echo UNSET; fi
```

- `HERMES` → **Hermes lane.** Stop.
- `GROK` → **Grok lane.** Stop.
- `UNSET` → stop and report. Do not guess the lane.

**Scope ceilings.** Max 3 fix commits per pass (stop and report if exceeded); no subagent dispatch inside a single worktree; never edit skills outside `skills/git/pr-babysit/`.

Marker provenance:

- **Hermes** re-exports `AI_AGENT=hermes-agent` and `HERMES_AGENT=true` on every command.
- **Grok Build** runs with `GROK_AGENT=1`.

Read only the winning lane's references. Do not read the other lane's.

## Routing

Read **only** the winning lane's references:

**Hermes lane**

| Step | Reference | Purpose |
| ----: | --------- | ------- |
| 0 | [`references/hermes/step-0-watch-and-spawn.md`](references/hermes/step-0-watch-and-spawn.md) | Verify auth, register PR in watchlist, compose detailed brief for Grok (fixes + Mergify queue/protections/diagnostics), spawn Grok worktree |
| 1 | [`references/hermes/step-1-wait-and-reverify.md`](references/hermes/step-1-wait-and-reverify.md) | Wait for Grok pass; read Grok's report (Mergify status, diagnostics, merge result); reverify CI on live head |
| 2 | [`references/hermes/step-2-merge.md`](references/hermes/step-2-merge.md) | Verify merge landed live on GitHub (merged by Grok via Mergify queue or fallback); retire the Grok worktree |
| 3 | [`references/hermes/step-3-final-report.md`](references/hermes/step-3-final-report.md) | Final report to user (fixes, Mergify outcome, open items, watchlist state) |


**Grok lane** — three independent workflows, each self-contained in its own subfolder:

**`grok/ship/`** — fix CI, merge to main

| Step | Reference | Purpose |
| ----: | --------- | ------- |
| 0 | [`references/grok/ship/step-0-add-pr.md`](references/grok/ship/step-0-add-pr.md) | PR details, repo, head/base refs; sets `ship: true` |
| 1 | [`references/grok/ship/step-1-watch-ci.md`](references/grok/ship/step-1-watch-ci.md) | Watch CI until green |
| 2 | [`references/grok/ship/step-2-auto-fix.md`](references/grok/ship/step-2-auto-fix.md) | CI red: parse logs, fix code, Conventional Commits, push |
| 3 | [`references/grok/ship/step-3-decision-tree.md`](references/grok/ship/step-3-decision-tree.md) | Conflict resolution, review threads, bot comments; troubleshooter: [`references/grok/ship/step-3-troubleshoot.md`](references/grok/ship/step-3-troubleshoot.md) |
| 4 | [`references/grok/ship/step-4-mergify-detect.md`](references/grok/ship/step-4-mergify-detect.md) | Detect Mergify on repo; bootstrap `.mergify.yml` setup PR if missing |
| 5 | [`references/grok/ship/step-5-mergify-diagnostics.md`](references/grok/ship/step-5-mergify-diagnostics.md) | When CI remains red: check `mergify events`, quarantine flaky tests, upload JUnit, detect scopes |
| 6 | [`references/grok/ship/step-6-merge-protections.md`](references/grok/ship/step-6-merge-protections.md) | Before merge: check active freezes (`mergify freeze`), `Depends-On:`, `Merge-After:`, stacked PRs |
| 7 | [`references/grok/ship/step-7-merge.md`](references/grok/ship/step-7-merge.md) | Ship-ready gates pass: merge via Mergify queue (`@mergifyio queue`), monitor queue, fallback to direct merge |

**`grok/add/`** — fix CI, keep draft, do not merge

| Step | Reference | Purpose |
| ----: | --------- | ------- |
| 0 | [`references/grok/add/step-0-add-pr.md`](references/grok/add/step-0-add-pr.md) | PR details, repo, head/base refs; sets `ship: false` |
| 1 | [`references/grok/add/step-1-watch-ci.md`](references/grok/add/step-1-watch-ci.md) | Watch CI until green |
| 2 | [`references/grok/add/step-2-auto-fix.md`](references/grok/add/step-2-auto-fix.md) | CI red: parse logs, fix code, Conventional Commits, push |
| 3 | [`references/grok/add/step-3-decision-tree.md`](references/grok/add/step-3-decision-tree.md) | Conflict resolution, review threads, bot comments; troubleshooter: [`references/grok/add/step-3-troubleshoot.md`](references/grok/add/step-3-troubleshoot.md) |

**`grok/setup/`** — set up Mergify merge automation

| Step | Reference | Purpose |
| ----: | --------- | ------- |
| 0 | [`references/grok/setup/step-0-detect.md`](references/grok/setup/step-0-detect.md) | Detect Mergify config; bootstrap `.mergify.yml` if missing |
| 1 | [`references/grok/setup/step-1-configure.md`](references/grok/setup/step-1-configure.md) | Write merge rules (CI green + ≥1 approval + non-draft → merge queue), validate, open configuration PR |
