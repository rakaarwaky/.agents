---
name: issue-worker
description: "issue → PR: analyzes open GitHub issues, verifies claims at HEAD, asks user decisions via quiz, isolates work in Orca worktrees, delegates implementation to Grok Build, verifies fixes, and pushes branches to open draft PRs. Never merges."
when-to-use: "Use when analyzing open GitHub issues to create PRs (/issue-worker <issue-number>...), triaging bug reports or feature requests, verifying issue reproduction at HEAD, running isolated Orca worktrees for issue fixes, or opening draft PRs from existing issues. Never creates issues (handled by /issue-maker) and never auto-merges."
argument-hint: "<issue-number> [<issue-number>...]"
---

# Issue Worker — issue → PR

End-to-end workflow for resolving GitHub issues: analyze issues to create PRs. The spine is verify at HEAD → decide → 1 issue → 1 Orca worktree → Grok Build implements → Hermes verifies → Hermes pushes branch + opens a draft PR to main → close/reopen issue per result. Never merges. Lane identification directs execution to `references/hermes/` or `references/grok/`.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **Lane attribution.** Lane is determined from physical env vars: `HERMES_AGENT=true` -> Hermes lane (Steps 0–3); `GROK_AGENT=1` -> Grok lane (Steps 4–10, run by Grok Build per issue). If neither is set, halt and report `UNSET`. Never guess the lane. | `[[ -n "${HERMES_AGENT:-}" ]]` enters Hermes; `[[ -n "${GROK_AGENT:-}" ]]` enters Grok. |
| R2 | **Verify at HEAD before deciding.** Never trust issue labels, audit dates, or commit message claims alone. Verify the cited file:line at HEAD and check `git log --oneline --since <issue-date> -- <path>` for existing fixes before spawning implementation. | Verified reproduction output or fix evidence documented before action. |
| R3 | **One issue, one worktree, one PR.** Each `still-broken` issue gets its own isolated Orca worktree (`issue-<N>`) and produces exactly one draft PR to `main`. Never mix multiple issues into a single worktree or PR. | Exactly 1 worktree and 1 branch per active issue. |
| R4 | **Orchestrator-implementer separation.** Hermes coordinates triage, decision quiz, verification, push, PR creation, and issue closing. Grok Build implements and runs local checks in its assigned worktree. Grok never pushes, never opens PRs, and never writes tracker updates. Hermes never edits code directly. | Grok commits stay local; Hermes alone runs `git push` and `gh pr create`. |
| R5 | **Safe push and draft PRs.** Hermes pushes verified branches with `git push --force-with-lease origin <branch>` (never bare `--force`) and opens draft PRs via `gh pr create --draft`. `Closes #N` is included only upon PR merge; this skill never merges. | Push uses `--force-with-lease`; PR is created in draft mode. |
| R6 | **Independent verification.** Grok's summary is a self-report, not verified fact. Hermes independently verifies code changes at file:line, verifies clean worktree status, and re-executes the symptom repro command before marking an issue verified. | Verification command re-run and passing output confirmed in worktree. |
| R7 | **Completion criteria.** All input issue numbers processed to terminal state: `fixed-on-main` issues closed with live evidence comments (`gh issue close <N> --reason completed --comment "..."`); `still-broken` issues have clean verified branches pushed and draft PRs opened (`gh pr create --draft`); worktrees marked `in-review`. | Every issue resolved to a draft PR or closed with evidence comment. |
| R8 | **Scope and iteration ceilings.** Maximum 10 concurrent Orca worktrees per wave. Edits strictly confined to the assigned worktree and artifact directories. Max 1 Grok implementation pass per issue (no looping retry on failure). Forbidden: auto-merging PRs, editing main branch directly, using shared repo build caches. | Concurrent worktrees ≤ 10; zero direct commits on main branch. |
| R9 | **Audience and tone.** Coordinates operations between Hermes orchestrator and Grok Build agents. Output in English, imperative mood, concrete paths and SHAs; no conversational filler or unverified claims. | Factual summaries with exact file:line references and command outputs. |
| R10 | **From where / Preconditions.** Requires git checkout on `origin`, authenticated `gh` CLI (`gh auth status`), and `$ORCA` (`orca-ide`) available. Reads issue numbers from arguments, issue body/comments via `gh issue view`, and repo state at HEAD. | `gh auth status` exits 0; `$ORCA` binary resolves; issue numbers valid. |
| R11 | **Branching logic.** IF issue already fixed at HEAD -> mark `fixed-on-main`, close with evidence comment, skip Grok. IF issue still broken -> spawn Grok worktree. IF open questions exist -> aggregate into single interactive quiz before implementation. IF Grok fix fails -> leave issue open, report failure verbatim, and tear down worktree. IF non-GitHub remote -> output compare URL and draft PR command. | Branch decisions match issue triage state and execution results. |
| R12 | **Failure fallback.** If `gh` unauthenticated -> halt and prompt `gh auth login`. If Orca worktree creation fails -> verify repo clean status and retry once. If push rejected -> fetch and rebase worktree branch onto origin before `--force-with-lease`. If Grok session fails/exits non-idle -> report error verbatim, keep issue open, and clean up worktree via `ORCA worktree rm`. | Named failure causes with exact recovery commands. |

## Routing

The lane is determined from physical environment variables:

```bash
if [[ -n "${HERMES_AGENT:-}" ]]; then echo HERMES
elif [[ -n "${GROK_AGENT:-}" ]]; then echo GROK
else echo UNSET; fi
```

Read only the winning lane's references. Do not read the other lane's.

| Lane | Step | Reference | Purpose |
|------|------|-----------|---------|
| Hermes | 0 | [`references/hermes/step-0-triage-and-spawn.md`](references/hermes/step-0-triage-and-spawn.md) | Verify claims at HEAD per issue; ask the decision quiz; spawn one Grok worktree per `still-broken` issue and drop the brief |
| Hermes | 1 | [`references/hermes/step-1-wait-and-verify.md`](references/hermes/step-1-wait-and-verify.md) | Wait for each Grok session; verify commits, code, and re-run the symptom repro in that worktree |
| Hermes | 2 | [`references/hermes/step-2-ship-and-close.md`](references/hermes/step-2-ship-and-close.md) | Push each verified branch, open one draft PR per issue; close verified-on-main issues with evidence; rebase still-open branches |
| Hermes | 3 | [`references/hermes/step-3-final-report.md`](references/hermes/step-3-final-report.md) | Final report: verdicts, evidence, PRs, closed issues, failed items, worktree teardown |
| Grok | 0 | [`references/grok/step-0-setup.md`](references/grok/step-0-setup.md) | Prerequisites, auth detection, `gh-env.sh` helper sourcing |
| Grok | 1 | [`references/grok/step-1-viewing.md`](references/grok/step-1-viewing.md) | Auxiliary: list, search, view issues (gh + curl) |
| Grok | 2 | [`references/grok/step-2-managing.md`](references/grok/step-2-managing.md) | Auxiliary: label, assign, comment, close/reopen, link to PRs, branch from issue |
| Grok | 3 | [`references/grok/step-3-triage-bulk.md`](references/grok/step-3-triage-bulk.md) | Auxiliary: issue triage workflow and bulk label/close operations |
| Grok | 4 | [`references/grok/step-4-verify-triage.md`](references/grok/step-4-verify-triage.md) | Load and triage: verify every claim at HEAD before closing |
| Grok | 5 | [`references/grok/step-5-validate.md`](references/grok/step-5-validate.md) | Validate issue state before deciding — rejects stale/fake/duplicate/already-fixed issues |
| Grok | 6 | [`references/grok/step-6-decision-quiz.md`](references/grok/step-6-decision-quiz.md) | Decision quiz before implementation: collect all open questions, ask in one interactive quiz with concrete recommended options first |
| Grok | 7 | [`references/grok/step-7-fanout.md`](references/grok/step-7-fanout.md) | Fan-out setup: 1 issue → 1 Orca worktree → 1 owner; child brief contract |
| Grok | 8 | [`references/grok/step-8-build-isolation.md`](references/grok/step-8-build-isolation.md) | Build isolation per worktree |
| Grok | 9 | [`references/grok/step-9-waves-verify.md`](references/grok/step-9-waves-verify.md) | Run waves, verify children (report files changed, mechanism, verification output, commit SHA) |
| Grok | 10 | [`references/grok/step-10-rebase.md`](references/grok/step-10-rebase.md) | Rebase still-open worktree branches onto the default tip after PRs land |
