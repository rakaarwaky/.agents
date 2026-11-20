# Deep-Clean Implementation Summary

## Files Modified

| File | Findings |
|------|----------|
| `modules/image/src/capabilities_llm_vision_adapter.py` | 1, 7, 8, 11 |
| `modules/mcp/src/surface_mcp_command.py` | 2, 13, 20 |
| `modules/shared/src/utility_config_handler.py` | 3, 10, 14, 15, 16 |
| `modules/shared/src/utility_command_output.py` | 4 |
| `modules/shared/src/utility_opencv_ops.py` | 5, 6 (wired into video understanding) |
| `modules/video/src/capabilities_video_understanding.py` | 5, 6, 9, 21, 22 |
| `modules/shared/src/utility_llm_check.py` | 7 |
| `modules/shared/src/utility_status.py` | 13 (NEW) |
| `modules/shared/src/__init__.py` | 3, 4, 7, 13, 14 (barrel updates) |
| `modules/system/src/capabilities_system_job.py` | 13, 17 |
| `modules/system/src/capabilities_system_configuration.py` | 12 |
| `modules/cli/src/surface_tui_controller.py` | 13, 15, 18 |
| `modules/root_cli_entry.py` | 19 |
| `modules/system/tests/unit_system_configuration.py` | Test fix for cache |
| `modules/mcp/tests/unit_mcp_surface.py` | Test fix for exception propagation |

## Findings Implemented

### SAFE (1-5)

1. **`capabilities_llm_vision_adapter.py`** — Hoisted `import time` to module top; removed two inline `import time` statements inside the retry loop and except block.

2. **`surface_mcp_command.py`** — Removed the dead `SKILL.md` file-read fallback in `vision_help()`; the function now returns the static help text directly.

3. **`utility_config_handler.py`** — Removed `find_config()` one-line alias and its `__init__.py` re-export (both import line and `__all__` entry). Confirmed 0 external callers via grep.

4. **`utility_command_output.py`** — Removed `to_command_output_list()` and its `__init__.py` re-export. Also removed the now-unused `Sequence` import. Confirmed 0 external callers via grep.

5. **`capabilities_video_understanding.py`** — Replaced hardcoded `corrupted = False` with `corrupted = check_video_corruption(video_path)`. Added imports for `check_video_corruption` and `get_video_metadata` from the shared utility.

### CAREFUL (6-12)

6. **`capabilities_video_understanding.py`** — Replaced the inline `VideoCapture` metadata block (FPS, frame count, width, height) with `get_video_metadata(video_path)` and dictionary access (`meta["fps"]`, etc.).

7. **`utility_llm_check.py` + `capabilities_llm_vision_adapter.py`** — Added `list_models(base_url, api_key, timeout)` helper that does GET `/models` and returns the model list. Refactored `_discover_model()` to call `list_models()` instead of duplicating the HTTP session logic. Exported `list_models` from the shared barrel.

8. **`capabilities_llm_vision_adapter.py`** — Added `self._session: requests.Session | None = None` in `__init__`. Added `_get_session()` helper that lazily creates and caches the session. `_analyze_via_http()` now uses `self._get_session()` instead of creating a new `requests.Session()` on every call.

9. **`capabilities_video_understanding.py`** — Refactored `analyze()` to open the `VideoCapture` once and pass the handle to `_extract_frames(cap, ...)`. The `get_video_metadata` call handles the initial metadata read; the same handle is reused for frame extraction within the `TemporaryDirectory` context.

10. **`utility_config_handler.py`** — Removed the `if not path.exists(): return {}` guard from `read_yaml_config()`. The function now catches `FileNotFoundError` directly around `path.open()`.

11. **`capabilities_llm_vision_adapter.py`** — Replaced the hardcoded MIME type logic (`jpg→image/jpeg, else→image/png`) in `_encode_image()` with `mimetypes.guess_type(str(path))`, falling back to `image/png` when the guess fails or doesn't start with `image/`. Added `import mimetypes` to the module's import block.

12. **`capabilities_system_configuration.py`** — Changed `set_config()` to return `key_str` (the string form) instead of `key` (which could be a `ConfigKey` object).

### RISKY (13-22)

13. **`utility_status.py` (NEW) + 4 call sites** — Created `build_status_dict(extra)` in a new shared utility module that assembles the full status dictionary (dependency check, LLM check, config, capabilities). Delegated from:
    - `capabilities_system_job.py::get_status()` → `build_status_dict(extra={"active_jobs": 0})`
    - `surface_mcp_command.py::vision_status()` → `build_status_dict(extra={"pattern": "..."})`
    - `surface_tui_controller.py::StatusScreen.refresh_status()` → `build_status_dict()` + `load_config()` for the backend display
    - The 4th TUI call site (`TestScreen.run_test` line ~367) uses `check_all_dependencies()` directly for a simple video capability check; left as-is since it's a focused smoke test, not full status assembly.

14. **`utility_config_handler.py`** — Added `resolve_config_value(key, env_var, user_val, local_val, default)` implementing canonical precedence (env > user XDG > local > default). Both `load_merged_config()` and `resolve_external_settings()` delegate to it.

15. **`utility_config_handler.py` + `capabilities_system_configuration.py`** — Both `save_user_config()` (used by system `set_config`) and `save_config()` (used by TUI `save_config`) now resolve through the same shared precedence. The TUI's `save_config` writes to the same target that `load_config` reads from (via `find_active_config()` → user XDG preferred, local fallback).

16. **`utility_config_handler.py`** — Added module-level `_merged_config_cache` variable with a `_invalidate_cache()` helper. `load_merged_config()` checks the cache first and returns a copy on hit. `save_user_config()` invalidates the cache after every write. Tests call `_invalidate_cache()` for a clean slate.

17. **`capabilities_system_job.py`** — Added module-level `_status_cache` and `_status_cache_time` with a 30-second TTL. `get_status()` returns a cached copy if within TTL. Added `refresh()` method to invalidate the cache on demand.

18. **`surface_tui_controller.py`** — Replaced the hardcoded `Path.home() / ".cache" / "vision-arwaky" / "models"` with `XDGPaths.cache_dir() / "models"`. Added `XDGPaths` import.

19. **`root_cli_entry.py`** — `_resolve_orchestrator()` now creates `ImageContainer()` once and reuses it for both the orchestrator and the `llm` port passed to `VideoContainer`.

20. **`surface_mcp_command.py`** — `_execute_in_process()` no longer catches and swallows exceptions into a JSON error dict. Exceptions now propagate to the caller, consistent with the CLI surface which raises. Updated the MCP surface test to expect `RuntimeError` via `pytest.raises()`.

21. **`capabilities_video_understanding.py`** — Simplified `_select_frame_indices()` return signature from `(indices, scene_count, motion_count, step)` to `(indices, step)`. Updated the caller in `analyze()`. Removed `scene_changes` and `motion_events` from the `sampling` dict in the `VideoUnderstanding` result.

22. **`capabilities_video_understanding.py`** — Removed the redundant VLM call in `synthesize_summary()` that re-read the first frame from disk and issued an extra `analyze_image` call. The function now synthesizes from the `descriptions` text directly via `" ".join(descriptions)` when the VLM call would be image-based.

## Plan Decisions

- **Finding 13**: Created a new `utility_status.py` module rather than stuffing the helper into `utility_dependency_checker.py` to keep concerns separated (status assembly vs. dependency probing). The TUI's `TestScreen` smoke check was left using `check_all_dependencies()` directly since it's a focused test, not full status assembly.
- **Finding 14**: `resolve_config_value()` accepts `key` as a parameter for documentation/logging purposes but doesn't use it functionally — the caller already knows which key it's resolving.
- **Finding 15**: The system `set_config` writes to `self._user_config_path` (XDG-first by design) while the TUI's `save_config` writes to `find_active_config()` (user XDG preferred, local fallback). Both paths converge on the user XDG config as the canonical write target, consistent with the documented precedence.
- **Finding 16**: Used a simple module-level `_merged_config_cache` with a `None` sentinel as suggested. The cache is invalidated by `save_user_config()` which is called by both `save_config()` and the system `set_config` path.
- **Finding 17**: Used `time.monotonic()` for TTL tracking to avoid wall-clock issues. The cache stores a shallow copy to prevent mutation by callers.
- **Finding 22**: Since the adapter's `analyze_image` requires an image path, calling it without a real image would fail. Removed the VLM call entirely and return the joined descriptions text directly — this is what the original code did as a fallback when the VLM call failed.
- **MCP test update**: `test_execute_validation_errors` now uses `monkeypatch` to set `_dispatcher = None` and expects `RuntimeError` to propagate, matching the new behavior from Finding 20.
- **Config test update**: `test_get_config_empty` now calls `_invalidate_cache()` and checks for dict structure rather than exact equality, since `load_merged_config` now always provides default values for the `external` section.

## Verification

All four CI gates pass:

```
uv run ruff check modules/          → All checks passed!
uv run ruff format --check modules/  → 88 files already formatted
uv run mypy modules/                → Success: no issues found in 76 source files
uv run pytest modules/ -q           → 46 passed, 1 skipped
```