---
name: issue-maker
description: "repo → issues: zero-trust spec audit mapping AES spec documents (PRD, ROADMAP, BACKLOG, FRD, DESIGN) into modular GitHub tracking issues with closing conditions. Done rows are re-verified against live source and test evidence. Never opens a PR — issues only."
when-to-use: "Use when mapping incomplete tasks from spec documents to GitHub issues (repo → issues), creating tracking issues from ROADMAP or BACKLOG, verifying Done claims against code, or auditing task completion with validate.py. Outputs GitHub issues only; never edits source or creates PRs."
argument-hint: "<repo-root> [--trust-mode <no-trust|trust>] [--dry-run] [--legacy] [--gh]"
---

# Issue Maker — repo → issues: zero-trust spec audit → modular GitHub tracking issues with closing conditions

One run covers one repo. It reads spec-document states, verifies which rows reflect real work vs fiction, and opens a modular issue per finding. Direction: repo → issues only. It never edits source code, never creates a branch, and never opens a PR. Every issue carries exactly one closing condition: a concrete check whose fulfillment advances that issue's row to Done in its source document.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **Lane attribution.** Lane is determined from physical env vars: `HERMES_AGENT=true` -> Hermes lane (Steps 0–2); `GROK_AGENT=1` -> Grok lane (auxiliary recipes, Steps 0–6). If neither is set, halt and report `UNSET`. Never guess the lane. | `[[ -n "${HERMES_AGENT:-}" ]]` enters Hermes; `[[ -n "${GROK_AGENT:-}" ]]` enters Grok. |
| R2 | **Zero trust.** Never trust any spec doc claim — rows marked Done are re-verified against live source code and test execution evidence. | Classification matches live code evidence; no unverified Done claim accepted. |
| R3 | **Issues only invariant.** The run outputs GitHub issues only. Never edit source code, never create a git branch, and never open a pull request. | `git status --short` in `<repo-root>` is unchanged; zero branches or PRs created. |
| R4 | **One closing condition per issue.** Every created issue must contain exactly one `## Closing condition` section specifying the exact check that advances the row to Done. | Every created issue body contains `## Closing condition`. |
| R5 | **Full row accounting.** Fixing all open issues equals all FR states = Done. Every row from every in-scope doc (PRD, ROADMAP, BACKLOG, FRD, DESIGN) must appear in the ledger with a classification. | Ledger row count equals total discovered spec rows. |
| R6 | **Tooling and scripts.** All runner and verification scripts live under `scripts/`, use Python standard library only (no third-party dependencies, no `uv sync`), and must pass unit tests (`pytest`). | `pytest scripts/tests` passes; zero non-stdlib imports in scripts. |
| R7 | **Completion gate.** The run is complete when `validate.py` exits 0 against the ledger and report in `~/.agents/develop/<namarepo>/issue-maker/`: `python3 scripts/validate.py --repo-root <repo-root>`. | `validate.py` exits 0. |
| R8 | **Scope and iteration ceilings.** File writes are strictly confined to `~/.agents/develop/<namarepo>/issue-maker/` (`task-tracker-ledger.jsonl`, `task-tracker-report.json`, and intermediate JSON artifacts). Target repo source code is never modified. Max 2 repair iterations on validation failure. Forbidden: modifying repo code or external repositories. | Touched files match declared artifact paths only. |
| R9 | **Audience and tone.** Coordinate execution for Hermes autonomous operations or Grok auxiliary runs. Output in English, imperative mood, concrete facts and paths; no filler or promotional text. | Output adheres to concise factual status and command paths. |
| R10 | **Input preconditions.** Requires `<repo-root>` pointing to an existing git repository containing spec docs. Reads optional flags `--trust-mode`, `--dry-run`, `--legacy`, `--gh`. All artifacts are stored in `~/.agents/develop/<namarepo>/issue-maker/`. | Target `<repo-root>` exists and is a valid git repository. |
| R11 | **Branching logic.** IF `--dry-run` -> generate ledger and report in `~/.agents/develop/<namarepo>/issue-maker/`, skip `gh issue create`. IF `--gh` -> probe `gh auth status`; verify opened issues exist and are `OPEN`. IF not `--gh` -> mark issue liveness as `deferred-to-gh`. IF `validate.py` fails -> report error verbatim and halt. | Branch outcomes match flags and command statuses. |
| R12 | **Failure fallback.** If GitHub rate limit (403/429) -> report rate limit, defer live checks, do not crash. If `gh` unauthenticated with `--gh` -> report `CONNECTION_REQUIRED` and stop. If malformed spec markdown -> report failing file:line and run with discovery override. | Failure causes identified with exact recovery commands. |

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
| Hermes | 0 | [`references/hermes/step-0-plan-and-authorize.md`](references/hermes/step-0-plan-and-authorize.md) | Scope decision (trust mode, `--gh`), GitHub auth check, Hermes lane entry via `run.py` |
| Hermes | 1 | [`references/hermes/step-1-wait-and-verify.md`](references/hermes/step-1-wait-and-verify.md) | Wait for `run.py`; verify gate — `validate.py --repo-root <repo-root>` exit 0, issues opened vs ledger rows, issues-only invariant |
| Hermes | 2 | [`references/hermes/step-2-final-report.md`](references/hermes/step-2-final-report.md) | Final report from `~/.agents/develop/<namarepo>/issue-maker/`: rows, classes, issues opened (or dry-run deferred), closing conditions, `--gh` liveness, invariant result |
| Grok | 0 | [`references/grok/step-0-discovery-scope.md`](references/grok/step-0-discovery-scope.md) | Spec-doc scope discovery, the three state-source layouts, and the feature/FR model |
| Grok | 1 | [`references/grok/step-1-discover-features.md`](references/grok/step-1-discover-features.md) | Enumerate feature directories and root spec docs into a discovery table |
| Grok | 2 | [`references/grok/step-2-scan.md`](references/grok/step-2-scan.md) | Run `scan.py` (default) or the legacy read-only scanner subagent per feature (`--legacy`) |
| Grok | 3 | [`references/grok/step-3-classify.md`](references/grok/step-3-classify.md) | Trust modes, Next Action handling, zero-trust policy, state vocabulary, classification, evidence, roll-up reconciliation; run `classify.py` |
| Grok | 4 | [`references/grok/step-4-verify.md`](references/grok/step-4-verify.md) | Read-only verification of every row; verdicts |
| Grok | 5 | [`references/grok/step-5-open-issues.md`](references/grok/step-5-open-issues.md) | One modular issue per row: title, body, labels, dry-run |
| Grok | 6 | [`references/grok/step-6-ledger-report.md`](references/grok/step-6-ledger-report.md) | Ledger + two-phase run report in `~/.agents/develop/<namarepo>/issue-maker/`, scripts, personas, completion criteria, and the `validate.py` CI gate |
