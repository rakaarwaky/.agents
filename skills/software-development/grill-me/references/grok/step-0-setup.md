# Step 0: Setup & Interview Environment

Everything the run needs before any subagent can spawn: host helpers, shared file paths, orchestrator state, and the owning repo.

## Start-Turn Gate: Lint Baseline

Run `lint-arwaky-cli report .` from the owning repo (absolute path: `/home/raka/.local/bin/lint-arwaky-cli`) before any subagent spawns. This records the scan baseline in `$XDG_DATA_HOME/lint-arwaky/snapshots.json` keyed by target path. Paste the report output verbatim into the orchestrator's run log. The baseline is the starting violation count for this run. If the CLI is unavailable, note the failure and continue without the gate.

## Host Setup

Run `sdc host setup --subdir plan` via `run_terminal_command` and parse the JSON stdout. Store `python` as `PYTHON`, `scratch_dir` as `scratch_dir`, and `run_id` as `INTERVIEW_ID`. `scratch_dir` is `~/.agents/develop/<repo-slug>/plan/` (per-repo, created by `sdc`); every artifact path in later steps is derived from it.

The helper requires the current directory to be inside a git repository — it exits with a clear error on either condition. If it exits non-zero, report the error and stop.

**Validate** that `INTERVIEW_ID` is 8 hex characters.

**Inline the resolved absolute `scratch_dir` and `PYTHON`** into every later command and subagent prompt. Do not rely on a shell variable surviving across `run_terminal_command` calls.

### Input: Original Plan Path

The user provides the original plan document path as `<plan-path>`. Resolve it to an absolute path and store as `plan_file`. Validate it exists on disk before proceeding; if not, stop and report.

### Shared File Paths

Define the shared file paths (all under `scratch_dir`):

- `interview_tree_file`: `${scratch_dir}/interview-tree-${INTERVIEW_ID}.md` — the design tree branches walked
- `resolved_decisions_file`: `${scratch_dir}/resolved-decisions-${INTERVIEW_ID}.md` — dependency-resolved decisions
- `open_questions_file`: `${scratch_dir}/open-questions-${INTERVIEW_ID}.md` — questions still open to the user
- `interview_summary_file`: `${scratch_dir}/interview-summary-${INTERVIEW_ID}.md` — final shared understanding

Always define these once at Step 0 and reuse them across all rounds. Never regenerate `INTERVIEW_ID` or these paths between iterations.

## Orchestrator State

Initialize these orchestrator variables to maintain across rounds:

- `round_count`: `0` — incremented each time a round of questioning completes.
- `branches_walked`: `[]` — list of design-tree branches already walked.
- `decisions_resolved`: `[]` — list of decisions resolved, each with its dependency chain.
- `open_questions`: `[]` — questions still pending user answer.
- `codebase_answers`: `[]` — questions answered by exploring the codebase (not asked to the user).

## Resolve the Owning Repo

Host setup (`sdc host setup --subdir plan`) must run from inside the owning git repository. Resolve `repo_path` the same way `implement/references/grok/step-0-setup.md` does:

1. Collect candidate paths: every file or directory path named in `<task-description>` and in the conversation context.
2. For the first candidate that exists on disk, run `git -C <parent-dir> rev-parse --show-toplevel` to get `repo_path`.
3. If no candidate exists on disk, run the same command from the current workspace cwd.

## Report to the User

After setup is complete, report:

> Running grill-me interview in <scratch_dir> (repo <repo-basename>, interview id <INTERVIEW_ID>).

Then proceed to Step 1 (Branch Walk).
