# Step 1 Memory Retrieval

## Step 1: Memory Retrieval (Past Issues Briefing)

Before launching any implementers, attempt to load past issue patterns from the workspace memory file. This briefing is injected into both implementer and reviewer prompts to help avoid recurring issues. The execute-plan skill **shares the same memory file** as the `/implement` skill -- patterns from both skills help each other.

### Resolve the helper command once

All memory operations go through `sdc memory <path|read|snapshot|update>`. The `sdc` launcher is already on PATH after installation at `~/.local/bin/sdc`. Capture it once as orchestrator state:

```
memory_cmd = "sdc memory"
```

Invoke the helper from the workspace root (the default cwd for `run_terminal_command`). The helper derives the workspace id from the cwd's git context.

### Read Path

1. Run `sdc memory snapshot` via `run_terminal_command` and capture stdout. The helper prints structured JSON:

   ```json
   {
     "common_issues": [
       {"category": "Error Handling", "description": "Missing null check", "count": 5}
     ],
     "recent_runs": [...],
     "exists": true
   }
   ```

   Store the `common_issues` list as `existing_patterns_snapshot`. Store the boolean `exists` as `memory_existed_before`.
2. If the helper exits non-zero, log a brief note, set `past_issues_briefing` to `""`, `existing_patterns_snapshot` to `[]`, `memory_existed_before` to `false`, and proceed to Step 3.
3. If `existing_patterns_snapshot` is empty (or `exists` is `false`), set `past_issues_briefing` to `""`.

### Parsing & Formatting

If `existing_patterns_snapshot` is non-empty:

1. Filter to only entries with `count >= 2`.
2. Sort by `count` descending.
3. Take the top 10 entries.
4. Format into `past_issues_briefing`:
