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

## Invocation Input

The user ran `/planner <description>` (or `/plan <description>`). Treat `<description>` as the plan task: feature plan, system architecture, migration plan, technical spec, or another plan deliverable. Capture any file paths, links, constraints, or extra context the user provided — Step 1 must include all of it in the writer prompt.