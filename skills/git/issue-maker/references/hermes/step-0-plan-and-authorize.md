# Step 0: Plan & Authorize (Hermes)

Hermes owns the audit plan — which spec docs are in scope, the trust mode, and GitHub auth. This is coordination, not coding.

## 0a: Scope Decision

From the argument hint `[<no-trust|trust>] [--dry-run]` resolve:

- Repo root: defaults to the current working directory (`cwd`), which must be a git checkout with spec docs present.
- `[<no-trust|trust>]` — trust mode (default `no-trust` per the skill's invariant).
- `--dry-run` — do not call `gh issue create`, still write ledger + report to `~/.agents/develop/<namarepo>/issue-maker/`.

All artifacts (`discovery.json`, `scan-out.json`, `classify-out.json`, `task-tracker-ledger.jsonl`, `task-tracker-report.json`) are automatically written to and read from `~/.agents/develop/<namarepo>/issue-maker/` (`namarepo` = lowercase git repo directory name).

## 0b: Auth Check (Hermes)

When running live (without `--dry-run`), confirm `gh auth status` before creating issues; report `CONNECTION_REQUIRED` if not authenticated.

## 0c: Hermes Lane Entry

The Hermes lane runs the audit driver itself via terminal (stdlib scripts, no LLM subagent, no Orca worktree):

```
python3 <this-skill>/scripts/run.py [no-trust|trust] [--dry-run]
```

This is Hermes invoking its own repo scripts — not a subagent. After `run.py` exits, proceed to Step 1.

Report: "issue-maker audit planned: repo=<cwd>, trust-mode=<no-trust|trust>, dry-run=<yes|no>."
