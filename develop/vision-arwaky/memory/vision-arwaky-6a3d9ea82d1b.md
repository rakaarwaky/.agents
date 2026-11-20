# Workspace Development Patterns

> This file is maintained by the sdc memory store across /implement, /execute-plan, /planner, and /grill-me runs.
> It records recurring issue patterns to help avoid them in future runs.
> Shared across all working directories that resolve to the same workspace id.

## Common Issues

### Architecture
- New shared utility module violates layer import rules (utility importing sibling utilities) (seen 1 time)

### Code Quality
- Dead no-op constructor left behind after removing the fields it initialized (seen 1 time)
- Dead truncation block left behind after removing the function that consumed the truncated value (seen 1 time)
- Inlined helper called at 3+ sites drops a field present in all original call sites (seen 1 time)
- Module-level cache ignores per-call path arguments, returning stale data to callers with different paths (seen 1 time)
- Status output shape silently changed without preserving backward-compatible keys (seen 1 time)
- Unused module-level constants and imports left behind after removing their sole consumer (seen 1 time)

### Testing
- Exception propagation change tested only on the no-dispatcher path, not on the dispatcher-throws path (seen 1 time)
- New shared utility function has no dedicated test file (seen 1 time)

### Error Handling
- User-facing help text references a non-existent CLI command (seen 1 time)

## Recent Runs

### 2026-11-20 — "impl: apply deep-clean findings across 22 audit items"
- **Rounds**: 3
- **Issues**: 32 total (12 bugs, 15 suggestions, 5 nits)
- **Key patterns**: New shared utility module violates layer import rules, Inlined helper called at 3+ sites drops a field present in all original call sites, Exception propagation change tested only on one path
- **Specializations used**: general, tests, simplicity, lint, user
