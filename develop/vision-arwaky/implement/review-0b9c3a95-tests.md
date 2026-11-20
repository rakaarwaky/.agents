### Issue 1 [Tests] — Severity: bug
- **File**: `modules/shared/src/utility_status.py`:1-65 (NEW, zero dedicated tests)
- **Description**: `build_status_dict()` is a new shared utility called from 3+ surfaces (system job, MCP, TUI), but has no dedicated test file. Existing tests that exercise it (`test_status_endpoint`, `test_get_status`, `test_status_routes_through_job_port`) are smoke tests checking only key presence — they never verify that `extra` keys are merged, that `capabilities.image_analysis` is derived from `deps["opencv"] == "OK"`, or that `configuration.llm_model` is `None` when the resolved model string is empty.
- **Suggestion**: Create `modules/shared/tests/unit_shared_status.py` with focused tests: (a) `test_extra_merged` passing a known dict and asserting those keys appear verbatim; (b) `test_capabilities_from_deps` mocking `check_all_dependencies` to return a controllable dict and verifying `capabilities.image_analysis` and `capabilities.llm_vision`; (c) `test_model_none_when_empty` mocking `resolve_external_settings` to return `("", "", "")` and asserting `llm_model is None`.
- **Status**: open

### Issue 2 [Tests] — Severity: bug
- **File**: `modules/shared/src/utility_config_handler.py`:18-190
- **Description**: No dedicated unit tests exist for the shared config utility, which contains four new/changed functions: `_invalidate_cache`, `resolve_config_value`, the cached `load_merged_config`, and the refactored `save_user_config`/`save_config`. All coverage is indirect through `unit_system_configuration.py` which tests only happy paths. None of the following are exercised: env-var precedence in `resolve_config_value`; the empty-string sentinel in `resolve_config_value` (`user_val != ""`); cache hit/miss behavior of `load_merged_config`; cache invalidation via `save_user_config`; `read_yaml_config` FileNotFoundError path; `load_merged_config` merging user+local config with external sub-dict.
- **Suggestion**: Create `modules/shared/tests/unit_shared_config_handler.py` with: `test_resolve_config_value_env_wins`, `test_resolve_config_value_empty_string_treated_as_falsy`, `test_load_merged_config_cache_hit_returns_copy`, `test_load_merged_config_cache_miss_reads_files`, `test_read_yaml_config_missing_file`, `test_save_user_config_invalidates_cache`, `test_save_config_falls_back_to_user_path` (with XDG env redirected to tmp_path).
- **Status**: open

### Issue 3 [Tests] — Severity: bug
- **File**: `modules/shared/src/utility_llm_check.py`:27-45
- **Description**: `list_models` is a new exported function in the shared layer with zero tests. Its error paths (`resp.raise_for_status()` → `HTTPError`, empty `data.get("data")` → `[]`, non-list `models` → `[]`, `requests.get` raising `ConnectionError`) are never exercised. The existing `test_status_endpoint` mocks `requests.get` globally and does not touch `list_models`.
- **Suggestion**: Add `modules/shared/tests/unit_shared_llm_check.py` with: `test_list_models_success` (mock returns valid JSON with `data` list), `test_list_models_empty_data`, `test_list_models_http_error` (raise_for_status raises `HTTPError`), `test_list_models_connection_error` (`requests.get` raises `ConnectionError`), `test_check_llm_endpoint_http_500`, `test_check_llm_endpoint_unreachable`.
- **Status**: open

### Issue 4 [Tests] — Severity: bug
- **File**: `modules/system/tests/unit_system_job.py`:1-22
- **Description**: The `_status_cache` + `_STATUS_TTL_S` TTL cache in `CapabilitiesSystemJob.get_status()` is entirely untested. `test_get_status` calls `get_status()` once and checks key presence only — it never verifies: cache hit returns a copy (caller mutation doesn't corrupt cache), `refresh()` clears the cache causing re-probe, TTL expiry triggers re-probe, or that the returned dict is not the same object as the cached one.
- **Suggestion**: Add `test_status_cache_returns_copy` (call `get_status`, mutate returned dict, call again, assert original values intact), `test_refresh_invalidates_cache` (call `get_status`, call `refresh()`, monkeypatch `build_status_dict` to verify re-invocation), `test_status_cache_ttl_expiry` (monkeypatch `time.monotonic` to advance past `_STATUS_TTL_S` and assert re-probe occurs).
- **Status**: open

### Issue 5 [Tests] — Severity: suggestion
- **File**: `modules/image/src/capabilities_llm_vision_adapter.py`:43-231
- **Description**: No tests exist for `LLMVisionAdapter` anywhere in the repo. Two specific changes from the impl are untested: (a) Finding 8 — `_get_session()` lazy session caching and header initialization; (b) Finding 11 — `_encode_image` using `mimetypes.guess_type` with fallback to `image/png` for unknown/non-image extensions. The retry loop in `_analyze_via_http` (3 attempts, 5s sleep, retry on HTTP 4xx/5xx or ValueError) is also completely uncovered.
- **Suggestion**: Add `modules/image/tests/unit_llm_vision_adapter.py` with: `test_get_session_caches_and_sets_headers`, `test_encode_image_jpg_mime_type`, `test_encode_image_unknown_extension_falls_back_to_png`, `test_encode_image_txt_extension_falls_back_to_png`, `test_analyze_via_http_retries_then_succeeds` (mock `session.post` to return 500, 500, 200; assert 3 calls and `time.sleep` called twice), `test_analyze_via_http_all_retries_fail_raises` (mock 500×3, assert `RuntimeError`).
- **Status**: open

### Issue 6 [Tests] — Severity: bug
- **File**: `modules/video/src/capabilities_video_understanding.py`:49-242
- **Description**: `VideoUnderstandingAnalyzer` has zero tests. The `modules/video/tests/` directory contains only `__init__.py`. The impl summary describes five changes to this file (findings 5, 6, 9, 21, 22): `check_video_corruption` wired in, `get_video_metadata` used for structural read, `_select_frame_indices` signature changed from `(indices, scene_count, motion_count, step)` to `(indices, step)`, VLM call removed from `synthesize_summary`, frame extraction refactored to reuse a single `VideoCapture` handle. None of these changes have any test coverage — not even a smoke or integration test.
- **Suggestion**: Add `modules/video/tests/unit_video_understanding.py` with at minimum: `test_select_frame_indices_bounded` (frame_count > MAX_SMART_VIDEO_FRAMES, assert len ≤ MAX), `test_select_frame_indices_normal` (small video, assert step matches interval and indices are uniform), `test_synthesize_summary_empty_descriptions` (returns fallback string), `test_synthesize_summary_joins_descriptions` (assert `" ".join`), `test_analyze_with_corrupted_video` (mock `check_video_corruption` → True, mock metadata, assert `"corrupted": True` in `video` dict).
- **Status**: open

### Issue 7 [Tests] — Severity: suggestion
- **File**: `modules/mcp/tests/unit_mcp_surface.py`:59-66
- **Description**: `test_execute_validation_errors` verifies propagation when `_dispatcher is None` (correct per Finding 20), but does not verify that exceptions raised inside `_dispatcher.execute_in_process` also propagate to the caller. The core behavioral change of Finding 20 is removing the try/except that swallowed all exceptions into a JSON error dict — the test should also cover the dispatcher-throws case to prove the swallow is gone.
- **Suggestion**: Add `test_execute_propagates_dispatcher_exception` that sets a mock dispatcher whose `execute_in_process` raises `ValueError("boom")` and asserts `pytest.raises(ValueError, match="boom")` on `vision_execute`.
- **Status**: open

### Issue 8 [Tests] — Severity: suggestion
- **File**: `modules/system/tests/unit_system_configuration.py`:1-41
- **Description**: The validation path of `set_config` in `capabilities_system_configuration.py` (lines 72-77) raises `ValueError` for empty keys and dot-segments with empty parts, but no test exercises this path. The cache invalidation flow via `save_user_config` (Finding 16) is also only tested implicitly through the existing happy-path test — there is no explicit test verifying that a write followed by a read sees the new value through the cache-invalidation path.
- **Suggestion**: Add `test_set_config_invalid_empty_key` (`pytest.raises(ValueError)` for `set_config("", "val")`), `test_set_config_invalid_empty_dot_segment` (`set_config("external..url", "val")` raises), and strengthen the cache test by explicitly calling `_invalidate_cache()`, reading, writing, and reading again to assert the new value appears.
- **Status**: open

### Issue 9 [Tests] — Severity: nit
- **File**: `modules/system/tests/unit_system_configuration.py`:14-24
- **Description**: `test_get_config_empty` was updated to check dict structure rather than exact equality (correct per impl summary), but the assertion `assert "external" in result` is weak — it only confirms a key exists without verifying that `result["external"]` is a well-formed dict containing the default url/api_key/model fields.
- **Suggestion**: Strengthen: `assert isinstance(result["external"], dict)` and `assert result["external"].get("url") == DEFAULT_LLM_URL` (import `DEFAULT_LLM_URL` from `utility_config_handler`).
- **Status**: open