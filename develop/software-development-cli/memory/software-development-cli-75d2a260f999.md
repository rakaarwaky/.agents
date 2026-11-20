# Implementation Review Patterns

> This file is maintained by the /implement skill.
> It records common issues found during implementation reviews to help avoid them in future runs.
> Shared across all working directories that resolve to the same workspace id.

## Common Issues

### Test
- test pattern (seen 1 time)
- x pattern (seen 1 time)

### Error Handling
- Broad exception catch masks real bugs (seen 1 time)
- Error diagnostics written to stdout instead of stderr (seen 1 time)
- File existence check performed before acquiring lock (TOCTOU race) (seen 1 time)
- Missing exception handler for a new error type at the surface boundary (seen 1 time)
- Non-SdcError exceptions raised for invalid input bypass exit-code contract (seen 1 time)
- OSError handler ignores dynamic exit code (seen 1 time)
- Partial failure exit code with no failure detail (seen 1 time)
- UnicodeDecodeError and OSError must be wrapped in MemoryHelperError, not propagate as tracebacks (seen 1 time)
- Unwired capability misclassified as a usage error (seen 1 time)

### Code Quality
- Docstring describes behavior not implemented (seen 1 time)
- Duplicate bootstrap code across files (seen 1 time)
- Import removed while still referenced in function signatures (seen 1 time)
- Inconsistent trailing newline on text output (seen 1 time)
- Module-level capability globals without reset or teardown (seen 1 time)
- Speculative diagnostic helper for marginal value (seen 1 time)
- Speculative re-export layer with zero callers (seen 1 time)
- Unused import in test file (seen 1 time)

### Testing
- Missing tests for error/edge case paths (seen 2 times)
- Missing end-to-end surface test for exit code contract (seen 1 time)
- Missing tests for CLI exit codes and error streams (seen 1 time)
- No concurrency test for lock serialization (seen 1 time)
- Test assertion matches substrings across potentially different strings (seen 1 time)

### Documentation
- Doc references removed CLI flag (seen 1 time)
- Docstring implies mutual exclusivity that no longer holds (seen 1 time)

### Python
- datetime.UTC requires Python 3.11+; use timezone.utc for 3.9 compat (seen 1 time)

### Git
- memory_paths() must fall back to cwd slug when not inside a git repo (seen 1 time)

### Parser
- parse_memory_file() must preserve unmatched lines; render_memory_file() must re-emit them (seen 1 time)

### CLI
- top_patterns() must validate n >= 1 and raise MemoryUsageError for invalid input (seen 1 time)

### UX
- Error messages must use plain language, not Python tuple reprs (seen 1 time)
- Lock timeout messages must state cause, retry guidance, and that nothing was written (seen 1 time)
- TTY-gated stderr hints needed for missing-file states in read commands (seen 1 time)

### Design System
- Closed vocabularies (workflow enum) and prefix gates must be consistently applied (seen 1 time)

## Recent Runs

### 2026-11-20 — "impl: fix 13 UX review findings for memory store"
- **Workflow**: impl
- **Rounds**: 1
- **Issues**: 10 total (3 bugs, 5 suggestions, 2 nits)
- **Key patterns**: datetime.UTC 3.9 compat, non-git cwd fallback, parse-preserve-re-emit, MemoryUsageError exit 2, MemoryHelperError wrapping
- **Specializations used**: Python 3.9 compat, AES layer conventions, git worktree orchestration

### 2026-11-18 — "Fix planner review findings"
- **Rounds**: 2
- **Issues**: 14 total (3 bugs, 8 suggestions, 3 nits)
- **Key patterns**: Missing exception handler for a new error type at the surface boundary, Import removed while still referenced in function signatures, Docstring describes behavior not implemented
- **Specializations used**: general, tests, simplicity

### 2026-11-18 — "Fix memory review findings"
- **Rounds**: 3
- **Issues**: 24 total (10 bugs, 8 suggestions, 6 nits)
- **Key patterns**: Non-SdcError exceptions raised for invalid input bypass exit-code contract, File existence check performed before acquiring lock (TOCTOU race), Missing tests for error/edge case paths
- **Specializations used**: general, tests, simplicity

### 2026-11-18 — "Fix CLI surface exit-code contract and error handling"
- **Rounds**: 1
- **Issues**: 9 total (4 bugs, 4 suggestions, 1 nit)
- **Key patterns**: Unwired capability misclassified as a usage error, Error diagnostics written to stdout instead of stderr, Missing tests for CLI exit codes and error streams
- **Specializations used**: general, tests, simplicity

### 2026-11-18 — "Smoke test"
