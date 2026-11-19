# Workspace Development Patterns

> This file is maintained by the sdc memory store across /implement, /execute-plan, /planner, and /grill-me runs.
> It records recurring issue patterns to help avoid them in future runs.
> Shared across all working directories that resolve to the same workspace id.

## Common Issues

### Error Handling
- Missing entries in error-type allowlists (seen 1 time)

### Testing
- Missing tests for error/edge case paths (seen 1 time)
- Tests that don't assert on specific error messages, only error types (seen 1 time)

### Code Quality
- Dead code paths left behind after refactoring (seen 1 time)
- Duplicated validation logic between caller and callee (seen 1 time)
- Extra helper/type/config for a single caller (YAGNI) (seen 1 time)
- Functions exceeding reasonable length without decomposition (seen 1 time)
- Type safety leaked via Any-typed protocol attributes (seen 1 time)

### Naming
- Inconsistent naming between test helpers and production code (seen 1 time)

### Security
- Missing input validation at API boundaries (seen 1 time)

## Recent Runs

### 2026-11-20 — "impl: add qwa folder <path> subcommand for folder-to-markdown compilation"
- **Rounds**: 2
- **Issues**: 14 total (8 suggestions, 6 nits)
- **Key patterns**: Type safety leaked via Any-typed protocol attributes, Missing entries in error-type allowlists, Dead code paths left behind after refactoring
- **Specializations used**: general, tests, simplicity
