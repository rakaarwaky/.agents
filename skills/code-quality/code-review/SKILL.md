---
name: code-review
description: "Reviews a commit, uncommitted changes, a PR, or a file/directory in place with parallel reviewer subagents. The orchestrator auto-selects 1–3 relevant lens personas from a roster of 10 based on the target's content. Each reviewer subagent reads the diff (diff modes) or the current files (path mode) and writes a per-persona review file to the host scratch directory. The orchestrator aggregates per-persona issue counts and writes a module summary file to disk."
when-to-use: "Use when asked to 'review the last commit', 'review my uncommitted changes', 'review PR 48', 'review modules/skills', 'review this folder', '/code-review commit', '/code-review uncommit', '/code-review pr 48', '/code-review path <dir>', or when the user drops a commit, PR number, or directory path and wants a code review. Persona selection is automatic — no flags needed."
argument-hint: "commit | uncommit | pr <pr-number> | path <path>"
---

# Code Review

Reviews one of four target types with parallel reviewer subagents seeded with 1–3 auto-selected lens personas. The orchestrator inspects the target's content (diff summary, directory tree, or file head) before launching subagents and picks the most relevant personas.

## Rules

| ID | Rule | Check |
|---|---|---|
| R1 | **Lane identification.** Lane is determined from launcher attribution env vars (`HERMES_AGENT=true` or `AI_AGENT=hermes-agent` → Hermes lane; `GROK_AGENT=1` → Grok lane; unset → stop and report). Hermes orchestrates; Grok Build implements in Orca worktrees. Never guess or mix lanes. | Exact launcher env var resolved; execution routes strictly to winning lane. |
| R2 | **Target argument contract.** Exactly one target per run: `commit` (last commit `HEAD~1..HEAD`), `uncommit` (working tree vs `HEAD`), `pr <pr-number>` (GitHub PR diff), or `path <path>` (file or directory content). Extra tokens, missing required arguments, non-existent paths, or unknown modes reject with usage hint and halt immediately. | Argument matches one of four valid invocations. |
| R3 | **Automatic persona selection.** Zero persona flags allowed. The orchestrator inspects target content (diff summary, directory tree, or file head) and auto-selects 1–3 most relevant lens personas from the 10-persona roster: `backend-engineer`, `business-analyst`, `devops-engineer`, `frontend-engineer`, `product-engineer`, `qa-engineer`, `security-engineer`, `software-architect`, `system-analyst`, `ui-ux-designer`. Default fallback for ambiguous diffs is `backend-engineer`, `qa-engineer`, `software-architect`. | Persona count is 1–3; all selected personas exist in roster. |
| R4 | **Parallel subagent fan-out.** Subagents launch in parallel with `background: true` and `subagent_type: "general-purpose"`. Subagent description is formatted as `[<persona>] <mode> <target>`. Each subagent receives its persona instructions and writes exclusively to its dedicated scratch file `${scratch_dir}/grok-review-<REVIEW_ID>-<persona>.md`. Never pass `capability_mode: read-only`. | Subagent descriptions match pattern; each subagent writes only its own review file. |
| R5 | **Scope and execution ceilings.** Maximum 3 concurrent reviewer subagents per run. Maximum 1 retry attempt per failed persona before recording error. Forbidden actions: modifying source files, running mutating git commands (`checkout`, `switch`, `reset`, `stash`, `fetch`, `commit`, `push`), creating PRs, or deleting paths outside the designated scratch files. | `git status --short` remains clean; source code remains unmodified. |
| R6 | **Error tolerance and non-abort.** If a reviewer subagent fails or times out, record `ERROR` with the failure message for that persona and proceed with aggregating the remaining completed personas. Do not abort the run or discard successful reviews when one persona errors. | Run continues on persona failure; errored persona captured in summary. |
| R7 | **Canonical issue heading contract.** Issue headings in per-persona review files must strictly match `^### Issue \d+ -- Severity: (bug|suggestion|nit)$`. Status must be `open`. Unmatched headings are logged as warnings and skipped during count aggregation. The heading pattern is the canonical count source; do not parse severity from body text. | Issue count matches regex captures on heading lines. |
| R8 | **Count parity and aggregation.** Summary file `${scratch_dir}/grok-review-summary-<REVIEW_ID>.md` aggregate issue counts (`bugs`, `suggestions`, `nits`) must equal the sum of verified headings across completed per-persona review files. Mismatches trigger recalculation using the per-persona files as authoritative. | Summary totals match sum of individual persona review headings. |
| R9 | **Scratch path isolation and cleanup.** Scratch files live under `${scratch_dir}` (resolved via `scripts/host.py setup`). Retain all per-persona review files and the summary file as final deliverables. On successful or partial runs, remove only temporary file lists and diff files via `scripts/host.py cleanup`. On empty diffs, exit cleanly without writing files. | Review deliverables persist in scratch dir; intermediate diff/list files cleaned up. |
| R10 | **Objective success metric.** Execution succeeds when: (1) `git status --short` on target repo is completely clean; (2) summary file `${scratch_dir}/grok-review-summary-<REVIEW_ID>.md` exists with valid Markdown structure; (3) all completed persona files exist and match count parity; (4) worktree teardown command is reported or executed cleanly. | Verification commands confirm exit 0, intact deliverables, and clean git status. |

## Routing

| Lane | Step | File | Purpose |
|---|---|---|---|
| Hermes | Step 0 | [`references/hermes/step-0-plan-and-spawn.md`](references/hermes/step-0-plan-and-spawn.md) | Plan brief, create Orca worktree with `--agent grok`, drop `/code-review <mode> <target>`. |
| Hermes | Step 1 | [`references/hermes/step-1-wait-grok.md`](references/hermes/step-1-wait-grok.md) | Wait for Grok fan-out via `terminal wait --for tui-idle` polling script, locate artifacts. |
| Hermes | Step 2 | [`references/hermes/step-2-verify-and-ship.md`](references/hermes/step-2-verify-and-ship.md) | Verify count parity, check clean git working tree, produce triage summary. |
| Hermes | Step 3 | [`references/hermes/step-3-final-report.md`](references/hermes/step-3-final-report.md) | Final report to user, deliverable paths in scratch dir, worktree teardown instructions. |
| Grok | Step 0 | [`references/grok/step-0-argument-parsing.md`](references/grok/step-0-argument-parsing.md) | Argument parsing, mode resolution, automatic persona selection (1–3 from roster). |
| Grok | Step 1 | [`references/grok/step-1-file-list.md`](references/grok/step-1-file-list.md) | Run state setup via `host.py`, per-mode scope collection, empty diff short-circuit. |
| Grok | Step 2 | [`references/grok/step-2-launch.md`](references/grok/step-2-launch.md) | Persona resolution, prompt templating, parallel subagent spawn contract. |
| Grok | Step 3 | [`references/grok/step-3-final-report.md`](references/grok/step-3-final-report.md) | Aggregation, heading regex parsing, summary generation, asymmetric cleanup. |
| Grok | Step 4 | [`references/grok/step-4-in-progress-reporting.md`](references/grok/step-4-in-progress-reporting.md) | In-progress phase progress updates. |
| Grok | Step 5 | [`references/grok/step-5-rules-and-design.md`](references/grok/step-5-rules-and-design.md) | Architectural rationale, error-handling decisions, and design constraints. |
