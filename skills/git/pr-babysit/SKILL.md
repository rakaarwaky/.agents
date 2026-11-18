---
name: pr-babysit
description: "Watch a PR, fix CI, merge via Mergify queue."
when-to-use: "Triggers on \"/pr-babysit\". Phrasing: \"watch PR 123 until green\", \"babysit PR 123 and merge when ready\", \"fix issue #123 and open a PR\", \"keep fixing PR 123 until it can merge\", \"pr-babysit add --ship 123\"."
argument-hint: "add [--ship] <number> | check <number> | ship on <number> | fix <number>"
disable-model-invocation: true
created_by: curator
---
# PR Babysitter

Watch a standalone GitHub PR end to end: register it, keep it green, merge it when `--ship` is active. When Mergify is configured on the repo, the merge step uses the Mergify merge queue (CI on a temporary merge commit before landing) instead of a direct `gh pr merge`. If Mergify is not configured, the skill bootstraps a minimal `.mergify.yml` with a merge-queue rule. Mergify diagnostics (events log, flaky-test quarantine, CI Insights) augment the CI re-verification loop. The pipeline is event-driven — CI re-runs and new review threads each trigger a fresh pass.

Related: [`mergify`](../mergify/SKILL.md) skill — the full Mergify CLI surface (stacks, queue, freezes, CI Insights, config, events) is owned by that skill; pr-babysit consumes its references when Mergify is active.

## Global Rules

This file is the lane identification step only. The lane is determined from physical signals, in this order. Each is observable without asking the agent to name itself. Each agent's launcher stamps a fixed attribution env var into every command it runs. The model cannot set these; only the launcher can.

```bash
if [[ -n "${HERMES_AGENT:-}" ]]; then echo HERMES
elif [[ -n "${GROK_AGENT:-}" ]]; then echo GROK
else echo UNSET; fi
```

- `HERMES` → **Hermes lane.** Stop.
- `GROK` → **Grok lane.** Stop.
- `UNSET` → stop and report. Do not guess the lane.

Marker provenance:

- **Hermes** re-exports `AI_AGENT=hermes-agent` and `HERMES_AGENT=true` on every command.
- **Grok Build** runs with `GROK_AGENT=1`.

Read only the winning lane's references. Do not read the other lane's.

## Routing

Read **only** the winning lane's references:

### Hermes lane

| Step | Reference | Purpose |
| ----: | --------- | ------- |
| 0 | [`references/hermes/step-0-watch-and-spawn.md`](references/hermes/step-0-watch-and-spawn.md) | Verify auth, register PR in watchlist, compose detailed brief for Grok (fixes + Mergify queue/protections/diagnostics), spawn Grok worktree |
| 1 | [`references/hermes/step-1-wait-and-reverify.md`](references/hermes/step-1-wait-and-reverify.md) | Wait for Grok pass; read Grok's report (Mergify status, diagnostics, merge result); reverify CI on live head |
| 2 | [`references/hermes/step-2-merge.md`](references/hermes/step-2-merge.md) | Verify merge landed live on GitHub (merged by Grok via Mergify queue or fallback); retire the Grok worktree |
| 3 | [`references/hermes/step-3-final-report.md`](references/hermes/step-3-final-report.md) | Final report to user (fixes, Mergify outcome, open items, watchlist state) |


### Grok lane

| Step | Reference | When it runs |
| ----: | --------- | ------------ |
| 0 | [`references/grok/step-0-add-pr.md`](references/grok/step-0-add-pr.md) | PR details, repo, head/base refs for the pass |
| 1 | [`references/grok/step-1-watch-ci.md`](references/grok/step-1-watch-ci.md) | At start of pass; observe check runs |
| 2 | [`references/grok/step-2-auto-fix.md`](references/grok/step-2-auto-fix.md) | CI red: parse logs, fix code, Conventional Commits, push |
| 3 | [`references/grok/step-3-decision-tree.md`](references/grok/step-3-decision-tree.md) | Conflict resolution, review threads, bot comments; troubleshooter: [`references/grok/step-3-troubleshoot.md`](references/grok/step-3-troubleshoot.md) |
| 4 | [`references/grok/step-4-mergify-detect.md`](references/grok/step-4-mergify-detect.md) | Detect Mergify on repo; bootstrap `.mergify.yml` setup PR if missing and `--ship` active |
| 5 | [`references/grok/step-5-mergify-diagnostics.md`](references/grok/step-5-mergify-diagnostics.md) | When CI remains red: check `mergify events`, quarantine flaky tests, upload JUnit, detect scopes |
| 6 | [`references/grok/step-6-merge-protections.md`](references/grok/step-6-merge-protections.md) | Before merge: check active freezes (`mergify freeze`), `Depends-On:`, `Merge-After:`, stacked PRs |
| 7 | [`references/grok/step-4-merge.md`](references/grok/step-4-merge.md) | Ship-ready gates pass: merge via Mergify queue (`@mergifyio queue`), monitor queue, fallback to direct merge |
