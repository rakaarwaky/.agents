# Simplicity Review — implement-deep-clean-findings (0b9c3a95)

Reviewer lane: over-engineering / unnecessary complexity only.
Correctness bugs, security holes, and test-coverage gaps are out of scope.

### Issue 1 [Simplicity] — Severity: suggestion
- **File**: modules/system/src/capabilities_system_job.py:46-49
- **Description**: `CapabilitiesSystemJob.refresh()` was added to invalidate the `_status_cache`, but it has zero callers anywhere in the codebase (grep finds only the definition; the TUI `refresh_status` call is a method on `StatusScreen`, not this `refresh`; the `R` binding on the status screen re-runs `build_status_dict` directly and never touches the job capability's cache). The method exists on the concrete class but is not part of `ISystemJobProtocol`, so nothing can invoke it through the contract either. It is speculative plumbing for a cache-invalidation path that is never exercised.
- **Suggestion**: Delete `refresh()`. If a manual invalidation hook is genuinely wanted, add it to `ISystemJobProtocol` and wire a caller (e.g. a TUI button or CLI command) so it is actually reachable.
- **Status**: open

### Issue 2 [Simplicity] — Severity: suggestion
- **File**: modules/shared/src/utility_config_handler.py:117-121
- **Description**: `_merged_config_cache` is keyed to nothing — it is a single module-level `dict | None`. But `load_merged_config(user_path, local_path)` accepts caller-supplied path overrides, and the cache check at line 120 ignores those arguments and returns whatever was cached first. The system configuration capability instantiates `CapabilitiesSystemConfiguration(config_path=..., local_config_path=...)` with explicit paths (root_system_container.py:30 and tests at unit_system_configuration.py:18/30), so the first `get_config()` caches the merged result of those paths, and any subsequent call with different paths silently returns the stale cached dict. To be correct, the cache would need to be keyed by `(user_path, local_path)` or dropped entirely for non-default paths — both make it more complex than the no-op fast path it replaced. The implementer's own summary (Finding 16) notes the cache is "available for tests that need a clean slate," which is the only non-production consumer, and tests already call `_invalidate_cache()`.
- **Suggestion**: Remove `_merged_config_cache` and `_invalidate_cache()` entirely; `load_merged_config` already short-circuits cheaply (two `read_yaml_config` calls that early-return on `FileNotFoundError`). If a cache is later proven necessary via profiling, key it by `(user_path, local_path)` and add a real eviction story. Revert the test changes in `modules/system/tests/unit_system_configuration.py` that depend on `_invalidate_cache()`.
- **Status**: open

### Issue 3 [Simplicity] — Severity: suggestion
- **File**: modules/shared/src/utility_config_handler.py:67-96
- **Description**: `resolve_config_value` was extracted as a shared helper for "canonical precedence," but it has exactly one caller (`load_merged_config` at lines 135/142/149). Its docstring claims the `key` parameter is "for documentation/logging," yet the parameter is never read in the body — it is pure dead surface area. The helper also wraps a 6-line precedence chain (env > user > local > default) that the original inline code already expressed in roughly the same line count (`os.getenv(...) or str(ext.get(...)) or DEFAULT`). The net effect is +1 exported symbol in the barrel (`__init__.py:68,148`), +1 function, +1 `key` parameter, with no second caller to justify the indirection.
- **Suggestion**: Inline the precedence back into `load_merged_config` (the three `resolve_config_value(...)` blocks become three `os.getenv(...) or user or local or default` expressions) and delete the helper plus its barrel exports. If a shared resolver is genuinely wanted later, add it when a second caller appears.
- **Status**: open

### Issue 4 [Simplicity] — Severity: nit
- **File**: modules/video/src/capabilities_video_understanding.py:243-248
- **Description**: `synthesize_summary` builds `summary_text` (join descriptions, then truncate to `MAX_SUMMARY_PROMPT_CHARS` with an "[Additional frame descriptions omitted...]" suffix) but never uses it — the function returns `" ".join(descriptions)`. The truncation/omission logic and the `MAX_SUMMARY_PROMPT_CHARS` import are now dead code left over from the removed VLM-call path (Finding 22 removed the `analyze_image` call but kept the string that fed it). This is leftover scaffolding, not active complexity, but it misleads the reader into thinking truncation happens.
- **Suggestion**: Reduce `synthesize_summary` to `return " ".join(descriptions)` (plus the empty guard) and drop the `summary_text` block and the `MAX_SUMMARY_PROMPT_CHARS` import if it is unused elsewhere in the module.
- **Status**: open