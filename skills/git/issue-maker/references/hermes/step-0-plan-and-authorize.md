# Step 0: Plan & Authorize (Hermes)

Hermes owns the audit plan — which spec docs are in scope, the trust mode, and GitHub auth. This is coordination, not coding.

## 0a: Scope Decision

From the argument hint `<repo-root> [--trust-mode <no-trust|trust>] [--dry-run] [--legacy] [--gh]` resolve:

- `<repo-root>` — absolute path; must be a git checkout with spec docs present.
- `--trust-mode <no-trust|trust>` (default `no-trust` per the skill's invariant).
- `--dry-run` — do not call `gh issue create`, still write ledger + report to `~/.agents/develop/<namarepo>/issue-maker/`.
- `--legacy` — bypass deterministic `scripts/scan.py` and use legacy read-only scanner recipes.
- `--gh` — opt-in GitHub liveness check.

All artifacts (`discovery.json`, `scan-out.json`, `classify-out.json`, `task-tracker-ledger.jsonl`, `task-tracker-report.json`) are automatically written to and read from `~/.agents/develop/<namarepo>/issue-maker/` (`namarepo` = lowercase git repo directory name). No path flags are needed.

## 0b: Auth Check (Hermes)

When `--gh` is set, confirm `gh auth status` before spawning anything; report `CONNECTION_REQUIRED` if not authenticated. Without `--gh`, open-issue liveness is reported `deferred-to-gh`.

## 0c: Hermes Lane Entry

The Hermes lane runs the audit driver itself via terminal (stdlib scripts, no LLM subagent, no Orca worktree):

```
python3 <this-skill>/scripts/run.py --repo-root <repo-root> [--trust-mode ...] [--dry-run] [--legacy] [--gh]
```

This is Hermes invoking its own repo scripts — not a subagent. After `run.py` exits, proceed to Step 1.

Report: "issue-maker audit planned: repo=<repo-root>, trust-mode=<no-trust|trust>, dry-run=<yes|no>, gh=<yes|no>."
