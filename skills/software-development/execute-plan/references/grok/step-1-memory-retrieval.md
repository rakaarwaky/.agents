# Step 1 Memory Retrieval

## Step 1: Memory Retrieval (Past Issues Briefing)

Before launching any implementers, attempt to load past issue patterns from the workspace memory file. This briefing is injected into both implementer and reviewer prompts to help avoid recurring issues. The execute-plan skill **shares the same memory file** as the `/implement` skill -- patterns from both skills help each other.

### Resolve the helper command once

All memory operations go through `sdc memory <path|read|top|update>`. The `sdc` launcher is already on PATH after installation at `~/.local/bin/sdc`. Capture it once as orchestrator state:

```
memory_cmd = "sdc memory"
```

Invoke the helper from the workspace root (the default cwd for `run_terminal_command`). The helper derives the workspace id from the cwd's git context.

### Read Path

1. Run `sdc memory top --n 10` via `run_terminal_command` and capture stdout. The helper prints structured JSON:

   ```json
   {
     "patterns": [
       {"category": "Error Handling", "description": "Missing null check", "count": 5}
     ],
     "total": 12,
     "exists": true
   }
   ```

   Store the `patterns` list as `existing_patterns_snapshot`. Store the boolean `exists` as `memory_existed_before`.
2. If the helper exits non-zero, log a brief note, set `past_issues_briefing` to `""`, `existing_patterns_snapshot` to `[]`, `memory_existed_before` to `false`, and proceed to Step 3.
3. If `existing_patterns_snapshot` is empty (or `exists` is `false`), set `past_issues_briefing` to `""`.

### Parsing & Formatting

If `existing_patterns_snapshot` is non-empty:

1. Filter to only entries with `count >= 2`.
2. Sort by `count` descending.
3. Take the top 10 entries.
4. Format into `past_issues_briefing`:

   ```
   ## Past Issue Patterns

   The following issue patterns have been seen in previous runs on this
   workspace. Address them proactively in your implementation and review:

   - [<category>] <description> (seen <count> times)
   - ...
   ```

5. Store the formatted string in `past_issues_briefing`. This string is injected into every implementer and reviewer prompt in Step 6.

If `existing_patterns_snapshot` is empty (or `exists` is `false`), set `past_issues_briefing` to `""` and skip the briefing block.

Do NOT read or write `.agents/execute-plan-issues.md` directly — that legacy path is per-worktree and no longer used. The helper is the single source of truth for the path.

Continue to Step 2 (tool detection).
