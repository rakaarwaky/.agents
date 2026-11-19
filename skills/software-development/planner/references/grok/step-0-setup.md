## Step 0: Setup

Prepare the environment, shared file paths, orchestrator state, and personas before spawning any subagent.

### Default Branch Detection

Before any git operations, detect the repository's default branch and store it as `default_branch`:

```bash
default_branch=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||')
if [ -z "$default_branch" ]; then
  default_branch=$(gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name' 2>/dev/null || echo "main")
fi
```

Use `<default_branch>` everywhere the skill previously hardcoded `main` (fetch, reset, compare URL, PR base).

## Host Setup

Run all host commands through `run_terminal_command` (bash on Linux; standard utilities allowed). Run `sdc host setup --subdir plan`:

```bash
sdc host setup --subdir plan
```

Parse the JSON on stdout and store:

- `python` as `PYTHON`
- `run_id` as `PLAN_ID` (validate: exactly 8 hex characters)
- `scratch_dir` as the artifact base directory. `sdc` is the single source of truth for this location: `~/.agents/develop/<repo-slug>/plan/`, where `<repo-slug>` is the lowercased git repository name normalized to `[a-z0-9-]`. It also creates the directory. If setup fails (e.g. not inside a git repository), stop and report.

Always use expanded absolute paths (for example `/home/<user>/.agents/develop/<repo-slug>/plan/plan-doc-<PLAN_ID>.md`), including in subagent prompts.

## Shared File Paths

Fixed for the entire run; derive each from `scratch_dir`:

- `plan_doc_file`: `<scratch_dir>/plan-doc-<PLAN_ID>.md`
- `summary_file`: `<scratch_dir>/plan-summary-<PLAN_ID>.md`
- `review_file`: `<scratch_dir>/plan-review-<PLAN_ID>.md`

Never regenerate `PLAN_ID` or these paths during review/revise iterations.

## Orchestrator State

- `round_count`: `0`. Increment each time a review completes — after Step 2 and after every Step 5 re-review.
- `total_issues_by_severity`: `{}`. Map from severity (`bug`, `suggestion`, `nit`) to cumulative count; updated at Step 3.
- `previous_review_snapshot`: `""`. Previous `review_file` contents, used for stalemate detection; updated at Step 3.

## Persona Injection

Load the `plan-doc-writer` and `plan-doc-reviewer` personas from `~/.agents/personas/<name>.toml`, extracting the full `instructions` value from each file's top-level `instructions` field into:

- `writer_persona_instructions`
- `reviewer_persona_instructions`

Injection timing: prepend the persona instructions on the initial launch only, never on resume.

## Memory Retrieval

Before spawning any subagent, load the workspace's past issue patterns. The briefing is **injected, not enforced**, and the run never fails over memory.

All memory operations go through `sdc memory <path|read|top|update>`. The `sdc` launcher is on PATH at `~/.local/bin/sdc`; capture it once as `memory_cmd = "sdc memory"`. The helper is cwd-sensitive only for workspace-id derivation (it runs `git config --get remote.origin.url` and `git rev-parse --git-common-dir` in the cwd), so invoke it from the session's cwd — the worktree or main clone that owns the task's repo. Never `cd` to the skill's own directory before invoking it.

1. Run `sdc memory top --n 10` via `run_terminal_command` and capture stdout. The `top` subcommand is the cheap read-only briefing query — it returns the count-desc top-10 patterns without parsing the full snapshot. The helper prints structured JSON:

   ```json
   {
     "patterns": [
       {"category": "Error Handling", "description": "Missing null check", "count": 5},
       ...
     ],
     "total": 12,
     "exists": true
   }
   ```

   Parse the JSON (no `jq`, no markdown re-parsing) and store orchestrator state:
   - `existing_patterns_snapshot` — the `patterns` list (used in the Step 7 flush to harmonize phrasing and reuse category names).
   - `memory_existed_before` — the `exists` boolean (report wording: "file created" vs "file updated").
   - `past_issues_briefing` — the briefing block (built below), or `""` when the snapshot is empty, does not exist, or the helper fails.
   - `plan_issue_patterns` — `[]`. One-line descriptions of distinct issues observed open in any review pass; appended at Step 3, flushed at Step 7.

   The `total` field is the full pattern count (before the `--n 10` truncation); the planner does not consume it beyond the briefing.
2. If `existing_patterns_snapshot` is non-empty, build `past_issues_briefing`:
   1. Filter to entries with `count >= 2` (one-off issues are excluded — they may not be real patterns).
   2. Sort by `count` descending; take the top 10.
   3. Format into the briefing block (the filter makes `count >= 2`, so always "times"):

   ```text
   ## Known Recurring Issues in This Workspace
   From previous runs in this repo (implement/execute-plan/plan), the following patterns recur:
   1. Missing tests for error/edge case paths (seen 8 times)
   2. Functions exceeding reasonable length without decomposition (seen 4 times)
   ...
   When drafting the plan: for each pattern above, the plan must either (a) address it, or (b) explicitly declare it out of scope (an Open Question, or a Key Decisions entry with a reason). Do not silently ignore a listed pattern.
   ```
3. If the snapshot is empty, does not exist (`exists: false`), or the helper exits non-zero (very rare — workspace id undeterminable, cwd unreadable), set `past_issues_briefing` to `""`, `existing_patterns_snapshot` to `[]`, `memory_existed_before` to `false`, log a brief note, and proceed to Step 1. Never fail the run due to memory retrieval issues.

## Invocation Input

The user ran `/planner <description>` (or `/plan <description>`). Treat `<description>` as the plan task: feature plan, system architecture, migration plan, technical spec, or another plan deliverable. Capture any file paths, links, constraints, or extra context the user provided — Step 1 must include all of it in the writer prompt.