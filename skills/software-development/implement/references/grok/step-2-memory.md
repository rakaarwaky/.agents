# Step 2: Memory Retrieval (Past Issues Briefing)


Before launching the implementer, attempt to load past issue patterns from the workspace memory file. This briefing is injected into both the implementer and reviewer prompts to help avoid recurring issues.

The memory file is **workspace-scoped** and lives under `$HOME/.agents/implement-memory/`, keyed by a stable workspace id derived in this order:

1. Canonicalised `git config remote.origin.url` (SSH and HTTPS variants of the same upstream collapse onto one id, with or without the `.git` suffix).
2. Absolute path of the main `.git` directory (`git rev-parse --git-common-dir`) for repos with no remote.
3. Absolute path of cwd as a last-ditch fallback for non-git workspaces.

The `sdc memory` capability (part of `sdc`) resolves the path and handles concurrent access via an exclusive Python lock (`fcntl.flock` on POSIX, `msvcrt.locking` on Windows; no `flock(1)` shell binary required).

### Resolve the helper command once

All memory operations go through `sdc memory <path|read|snapshot|update>`. The `sdc` launcher is already on PATH after installation at `~/.local/bin/sdc`. Capture it once as orchestrator state:

```
memory_cmd = "sdc memory"
```

Invoke the helper from the run's worktree after Step 0 (Setup & Worktree Isolation): `cd <worktree_path> && sdc memory ...`. The helper itself is cwd-sensitive only for its workspace-id derivation: it runs `git config --get remote.origin.url` and `git rev-parse --git-common-dir` in the cwd, so cwd must be inside the repo that owns the task — the worktree guarantees that even when the session sits in a superproject workspace. Never `cd` to the skill's own directory before invoking it.

### Read Path

1. Run `cd <worktree_path> && sdc memory snapshot` via `run_terminal_command` and capture stdout. Use the `snapshot` subcommand for reads — the `read` subcommand is for human inspection only. The helper prints structured JSON — no markdown re-parsing in the orchestrator. The shape is:

   ```json
   {
     "common_issues": [
       {"category": "Error Handling", "description": "Missing null check", "count": 5},
       ...
     ],
     "recent_runs": [
       {"date": "2026-04-23", "description": "\"Add retry logic\"", "body_lines": ["- **Rounds**: 2", "- **Issues**: 7 total (1 bug, 1 suggestion, 5 nits)", "- **Key patterns**: Missing entries in error-type allowlists, incomplete configuration validation", "- **Specializations used**: general, tests, simplicity"]},
       ...
     ],
     "exists": true
   }
   ```

   Parse the JSON and store the `common_issues` list as `existing_patterns_snapshot` (used in Step 8b). Store the boolean `exists` as `memory_existed_before` (used in the Final Report to decide between "file created" and "file updated" wording). The `recent_runs` array is included in the snapshot for debugging and forward compatibility (parse `.recent_runs` from the JSON yourself; do not invoke `jq`). The orchestrator does not currently consume it. Each entry's `body_lines` are the verbatim markdown bullets (leading `- ` and `**...**` formatting preserved).
2. If the helper exits non-zero (very rare — only happens if `$HOME` is unset and inferable home fails, or if cwd is unreadable), log a brief note, set `past_issues_briefing` to `""`, `existing_patterns_snapshot` to `[]`, `memory_existed_before` to `false`, and proceed to Step 3 (Implement). Note that a non-git workspace is **not** a failure mode — the helper falls back to a cwd-based id.
3. If `existing_patterns_snapshot` is empty (or `exists` is `false`), set `past_issues_briefing` to `""` and skip the briefing block below.

Do NOT read or write `.agents/implement-issues.md` directly during a /implement run — that legacy path is per-worktree and is no longer used. The helper is the single source of truth for the path.

**One-time migration from the legacy file:** if a user has a populated `.agents/implement-issues.md` from a prior version, its `## Common Issues` and `## Recent Runs` sections use the **same markdown format** documented under [Memory File Format](step-8-memory-flush.md#memory-file-format). To bring that history forward:

1. **From the workspace root** (the same directory where `.agents/implement-issues.md` lives — the workspace-id is derived from the cwd's git context, so running this from `~` or any unrelated directory will write to the wrong workspace's memory file), write `{}` to a temp file and run `sdc memory update --file <that-file>` once to create the workspace-scoped file and its parent directory — `sdc memory path` only computes the path, it does not create the directory.
2. Open the printed file path in an editor.
3. Hand-copy the bullets from the legacy file's `## Common Issues` section into the corresponding categories in the new file (preserving the `- description (seen N time(s))` syntax).
4. The helper picks up the entries on the next `update`.

There is no automatic migration.

### Parsing & Formatting

If `existing_patterns_snapshot` is non-empty:

1. Filter to only entries with `count >= 2` (minimum threshold — one-off issues are excluded as they may not represent real patterns).
2. Sort by `count` descending.
3. Take the top 10 entries.
4. Format them into the briefing block and store in `past_issues_briefing`:

```
## Past Issues to Avoid
Based on previous implementation runs, the following patterns commonly cause issues:
1. Missing null/undefined checks on function inputs (seen 5 times)
2. Missing tests for error/edge case paths (seen 8 times)
3. Functions exceeding 50 lines without decomposition (seen 4 times)
4. Magic numbers without named constants (seen 6 times)

Pay special attention to these patterns in your work.
```

(Use `time` for `count == 1`, `times` otherwise. The helper renders both forms identically in the file, so the briefing should match.)

If there are no qualifying entries, set `past_issues_briefing` to `""`.

### Graceful Degradation

If the helper command fails for any reason, set `past_issues_briefing` to `""`, `existing_patterns_snapshot` to `[]`, `memory_existed_before` to `false`, and proceed normally. Never fail the run due to memory retrieval issues — log a brief note and continue.

The briefing is **injected, not enforced** — it is informational context for the implementer and reviewers, not a hard constraint.