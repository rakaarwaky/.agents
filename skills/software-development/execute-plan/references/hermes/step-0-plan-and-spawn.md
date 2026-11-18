# Step 0: Parse the Plan, Prepare the DAG & Spawn Grok Build

Hermes never writes code. This step turns the plan document into a validated DAG + a self-contained brief, then drops the whole plan into a single Grok Build Orca worktree. Grok runs the full execution loop (worktrees, implementers, review panel, fix rounds, final assembly) internally — Hermes's only job is to wait and ship.

## Parse & Validate the DAG

Run the bundled validator (same as `grok/step-3-parse-dag.md`):

```
sdc validate-plan <plan_doc_path>
```

- Exit `0`: parse the JSON report. Require `valid == true` and `errors == []`. `linearized_order`, `level_assignments`, `nodes`, `pr_count`, and `max_parallelism` are authoritative.
- Exit `1`: DAG validation failed. Read the JSON on stdout and report the first error.
- Exit `2`: usage or IO error. Read stderr and report the first error.
- Exit `4`: plan parse error, including missing `## PR Plan` section, no entries, or malformed PR/dep fields. Read the JSON on stderr and report the first error.
- On any non-zero exit: stop.

**Only proceed to spawn if the plan is valid.** An invalid or ambiguous DAG goes back to `/planner`, not into Grok.

## Plan the Task Brief

Grok has zero conversation context. Compose a brief covering:

1. **Goal** — implement the full PR Plan DAG from `<plan_doc_path>`: `pr_count` PRs, `max_parallelism` wide, in `linearized_order`.
2. **DAG summary** — the validated `linearized_order` with each PR's id, slug, and dependencies. This is Grok's authoritative execution order; it must not re-derive or re-order.
3. **Per-PR instructions** — for each PR, the `description`, `files/components affected`, and `dependencies` from the plan.
4. **Constraints** — style, tests, repo conventions from AGENTS.md / CONTRIBUTING.md; out-of-scope list (any path the plan never named).
5. **Acceptance criteria** — all PRs implemented, 3-reviewer panel (general, tests, simplicity) at 0 open issues on every PR, final branch assembled with all conflicts resolved, final PR opened as a draft to `main`.
6. **Deliverable** — one final branch `execute-plan/<PLAN_ID>-final` with all PRs merged, one draft PR opened. Grok writes `exec-summary-<PLAN_ID>-<pr-id>.md` and `exec-review-<PLAN_ID>-<pr-id>.md` to its scratch dir for every PR, and `exec-plan-<PLAN_ID>.json` as the state file.

## Create the Orca Worktree

Resolve `$ORCA` (`$ORCA_CLI_COMMAND` if set, else resolve via `command -v orca-ide` with fallback to `$HOME/.local/bin/orca-ide` — never bare `orca`). `$ORCA` is not exported by the shell, so `${ORCA}` expands to empty and bash reports `command not found`. Always call by the absolute path unless `$ORCA_CLI_COMMAND` is set. Resolve the main clone.

```
"$ORCA" worktree create --repo path:<main_clone_path> --name <PLAN_ID> --agent grok --no-parent --surface terminal --json
```

- Parse JSON: `result.worktree.path` → `worktree_path`, `result.worktree.id` → `worktree_id`, `result.worktree.branch` → `worktree_branch` (strip `refs/heads/`).
- **Failure:** if create fails or no Orca CLI resolves, report the error and stop. Never fall back to the main clone.

If `--agent grok` is blocked (e.g. `agent_session_operation_unknown`), fall back to a plain `git worktree add` at `~/orca/workspaces/<repo-basename>/<PLAN_ID>` and drive Grok headless **inside that worktree** via `grok -p '<brief>' --cwd <worktree_path> --always-approve`. Never run bare `grok` / `grok -p` directly in the Hermes terminal session outside a worktree context.

## Drop the Task

Send exactly this, once, via `orca terminal send --terminal <handle> --text "<brief>" --enter --json`:

```
/execute-plan <plan_doc_path>

<constraints, DAG summary, and acceptance criteria from the brief>
```

Confirm `accepted: true` in the response. **After this send, do not send any more text to Grok.** No status checks, no course corrections, no "is PR-3 done?".

## Proceed to Step 1

Do NOT end the turn after dropping the task. Hermes must stay active and proceed immediately to Step 1 in this session to wait and poll for Grok Build to finish:

> Dropped /execute-plan into Grok Build at <worktree_path> (<pr_count> PRs, max parallelism <max_parallelism>). Proceeding to Step 1 to wait for completion.
