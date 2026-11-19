# Step 0 Setup

## Invocation

The user runs:

```text
/execute-plan <plan-doc-path> [--resume <PLAN_ID>]
```

- `<plan-doc-path>`: Required. plan document containing the PR Plan DAG.
- `--resume <PLAN_ID>`: Optional. Resume a previous run. If specified, skip to Step 9.

Internal defaults: `concurrency = 8`.

## Todo Scaffold

The PR plan is a DAG. Each DAG node becomes a top-level todo with id `pr-<node-id>`. Inside each node, use sub-id namespacing for phases:

- `pr-<n>:branch-prep` — Step 5
- `pr-<n>:execute` — Step 6 (worker loop)
- `pr-<n>:review` — review phase if invoked
- `pr-<n>:merge-ready` — final branch assembled + final review green + final PR pushed

Terminal state: all `pr-<n>:merge-ready` ids `completed`. Only then write the final report.
**Reseed after compaction** — rebuild the todo list from the cached DAG (persisted in the state file) if a compaction lands mid-execution.

## Persona Injection

This skill uses the `implementer` and `reviewer` personas.
Resolve each persona name in this order:

1. `~/.agents/personas/<name>.toml`
2. `<skill_dir>/../../../../personas/<name>.toml`

Extract the `instructions` value from each file's top-level `instructions` field (e.g. `python3 -c "import tomllib,sys; print(tomllib.load(open(sys.argv[1],'rb'))['instructions'])" <path>`; the `[[inputs]]` and `[[outputs]]` arrays are siblings, not nested under a table) and store as:

- `implementer_persona_instructions`
- `reviewer_persona_instructions`

When launching a subagent, **prepend** the appropriate persona instructions to its prompt. Do NOT pass a `persona` parameter to `spawn_subagent`. Prefix the `description` with a bracketed role tag (`[implementer]`, `[reviewer]`, `[tests]`, `[simplicity]`, `[lint]`, `[user]`). Keep the tag on `resume_from` follow-ups.

## Host & Environment Setup

Host commands run in bash on Linux. Use `run_terminal_command`.

### Default Branch Detection

Before any git operations, detect the repository's default branch and store it as `default_branch`:

```bash
default_branch=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||')
if [ -z "$default_branch" ]; then
  default_branch=$(gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name' 2>/dev/null || echo "main")
fi
```

Use `<default_branch>` everywhere the skill previously hardcoded `main` (fetch, reset, compare URL, PR base).

Run `sdc host setup --subdir execute` and parse the JSON stdout. Store `python` as `PYTHON`, `scratch_dir` as `SCRATCH_DIR`, and `run_id` as `PLAN_ID`.

`SCRATCH_DIR` is `~/.agents/develop/<repo-slug>/execute/`. State, summaries, and reviews live here.
**Validate** that `PLAN_ID` is 8 hex characters.
**Inline the resolved absolute `SCRATCH_DIR` and `PYTHON`** into every later command.

Define shared file paths (all under `SCRATCH_DIR`):

- `state_file`: `<SCRATCH_DIR>/exec-plan-<PLAN_ID>.json`
- Per-PR summary: `<SCRATCH_DIR>/exec-summary-<PLAN_ID>-<pr-id>.md`
- Per-PR merged review: `<SCRATCH_DIR>/exec-review-<PLAN_ID>-<pr-id>.md`
- Individual reviewer files: `<SCRATCH_DIR>/exec-review-<PLAN_ID>-<pr-id>-<specialist>.md`

Initialize orchestrator state variables:

- `plan_doc_path`, `main_clone_path` (`git rev-parse --show-toplevel`)
- `max_concurrent` (default 8), `dag`, `linearized_order`, `ready_queue`, `in_progress`, `completed`, `failed`, `skipped`
- `past_issues_briefing`: `""` (populated in Step 1)
- `issue_patterns`: `[]` (accumulated during reviews, used in Step 12)
- `total_issues_by_severity`: `{}` (accumulated during reviews)
- `existing_patterns_snapshot`: `[]` (from Step 1)
- `memory_existed_before`: `false` (from Step 1)
- `user_instructions`: `""`
- `gh_available`: `null` (populated in Step 2)
- `PR_TIMEOUT`: `1800` (seconds; per-PR execution timeout before marking as failed)

### Status Enum

PR status values: `pending` → `branch_created` → `implementing` → `reviewing` → `completed` | `failed` | `skipped`.

Valid transitions:
- `pending` → `branch_created` (Step 5)
- `branch_created` → `implementing` (Step 6a)
- `implementing` → `reviewing` (Step 7)
- `reviewing` → `completed` (0 open issues) or `implementing` (fix round)
- `implementing` → `failed` (timeout, crash, or unrecoverable error)
- `pending` → `skipped` (dependency not completed)

Initialize the state file:

```json
{
  "plan_id": "<PLAN_ID>",
  "plan_doc_path": "<plan-doc-path>",
  "status": "initializing",
  "created_at": "<ISO 8601 timestamp>",
  "max_concurrent": 8,
  "linearized_order": [],
  "dag": { "nodes": [] },
  "final_assembly_started": false,
  "final_branch_pushed": false,
  "pr_urls": [],
  "user_instructions": "",
  "gh_available": null
}
```

Write this initial state file using the `write` tool.
Report: `"Starting execute-plan with PLAN_ID: <PLAN_ID>, concurrency: <max_concurrent>"`

## Orca Worktree Protocol

Every subagent runs in its own Orca-managed worktree under `~/orca/workspaces/`. The orchestrator interacts with those worktrees through the `orca-ide` CLI. Do not work on the default branch in the main clone.

### Subagent boundary

Subagents (implementers, fixers, reviewers) never create branches, push, fetch across worktrees, run `orca-ide`, or use `gh`. Their only git obligations are editing files and committing locally in their own worktree. The orchestrator owns all git, Orca-worktree, and stack-tooling operations, including merge-conflict resolution — its sole exception to the no-source-file-modification rule (applied in Step 5 branch prep and Steps 10.1/10.4; see Step 10 Rules).

### Worktree kinds

- **Orca-managed worktrees** live under `~/orca/workspaces/` and are tracked by Orca. Remove them only with `orca-ide worktree rm --worktree <id> --force --json`; removing them via raw `git worktree remove` orphans Orca's internal registry. A `not found` response from `orca-ide worktree rm` counts as success (teardown is idempotent).
- **Raw temp worktrees** (Step 5 diamond-dependency merges) are plain `git worktree add` worktrees under a `mktemp` directory — remove those with `git worktree remove`, not Orca.

### Worktree creation (Step 6a)

```bash
orca-ide worktree create \
  --repo path:<main_clone_path> \
  --name <PLAN_ID>-<pr.id> \
  --base-branch <pr.branch> \
  --agent grok \
  --no-parent \
  --json
```

- `--repo path:<main_clone_path>` targets the orchestrator's main clone.
- `--name <PLAN_ID>-<pr.id>` gives each PR a unique worktree display name.
- `--base-branch <pr.branch>` checks the modular branch out inside the new worktree.
- `--agent grok` puts a Grok Build TUI in the worktree's first terminal — the coding agent for this environment. Do NOT send task text to it (no `--prompt`): the implementer and reviewers are `spawn_subagent` children with `cwd` inside the worktree; the TUI is the orchestrator's monitoring surface only.
- `--no-parent` keeps the DAG lineage out of Orca's model.
Record `pr.orca_worktree_id` (`<repoId>::<worktreePath>`) and `pr.worktree_path`.

### Completion and teardown

**Rule 1 — fetch without a destination refspec.**

```bash
git fetch <worktree_path> HEAD --no-tags
```

**Rule 2 — `pr.commit_sha` is the authoritative reference.**

```bash
pr.commit_sha = $(git -C <worktree_path> rev-parse HEAD)
git cat-file -t <pr.commit_sha>
```

Every downstream step keys off `commit_sha`, never off `refs/heads/<pr.branch>`.

**Rule 3 — tear down the worktree before mutating its branch ref.**

```bash
orca-ide worktree rm --worktree <pr.orca_worktree_id> --force --json
```

Run this immediately before merging the branch into the final branch (Step 10.1).

**Rule 4 — completion sentinel.**

When the entire execute-plan run is complete (all PRs done, final branch pushed, final PR created), print the sentinel line as the final line of terminal output before going idle:
```
EXECUTE_PLAN_COMPLETE
```
This sentinel is what Hermes polls for — it must be the very last line of output. If the run fails before completion, the sentinel is absent and Hermes treats the run as failed.