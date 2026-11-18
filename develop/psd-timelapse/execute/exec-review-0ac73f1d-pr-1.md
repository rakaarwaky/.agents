# Merged Review: pr-1 — Add `GET /api/renders` listing endpoint + `SystemOrchestrator.list_runs()`

## [General]
### Issue 1 -- Severity: suggestion
- **File**: modules/system/src/agent_system_orchestrator.py:347-348
- **Description**: `list_runs` hard-codes `XDGPaths.data_dir()` instead of reading `config.output_dir` from the injected configuration. The design doc says "output_dir comes from the injected configuration." Works in the default profile (both are the XDG data dir), but a custom `output_dir` would silently exclude runs.
- **Suggestion**: Read `output_dir` from `self._configuration.load().output_dir` and scan that path. If a custom output_dir is out of scope, add a comment documenting the intentional XDG-only scan.
- **Status**: open

### Issue 2 -- Severity: suggestion
- **File**: modules/api/src/surface_api_run_controller.py:58-61
- **Description**: `getattr(self._orchestrator, "list_runs", None)` weakens static checkability; a future rename would silently degrade to always-empty. No sibling controller uses `getattr` for any method.
- **Suggestion**: Call `self._orchestrator.list_runs()` directly, or narrow the constructor type to `SystemOrchestrator` (concrete). `ISystemAggregate` stays unchanged.
- **Status**: open

### Issue 3 -- Severity: suggestion
- **File**: modules/api/src/surface_api_run_controller.py:49-55
- **Description**: `GET /renders` documents only `200` in OpenAPI (no `500`), inconsistent with the companion `POST /renders` (which documents 400/409/422/500).
- **Suggestion**: Add `responses=error_responses(500)` to the route registration.
- **Status**: open

### Issue 4 -- Severity: suggestion
- **File**: modules/api/tests/unit_api_run_listing.py:307-308
- **Description**: `test_aggregate_without_list_runs_reports_empty_listing` is tautological. `Mock(spec=ISystemAggregate)` has no `list_runs` by construction, so the test only exercises the fallback branch and would pass even if the mapping branch were swapped.
- **Suggestion**: Strengthen to assert the orchestrator's `list_runs` was never called, or remove the test (the fallback branch is defensive enough that an explicit test has limited value).
- **Status**: open

### Issue 5 -- Severity: nit
- **File**: modules/system/src/agent_system_orchestrator.py:346-348
- **Description**: Docstring omits the `XDGPaths.data_dir()` scan-root limitation.
- **Suggestion**: Add one sentence: "Scans ``XDGPaths.data_dir()`` (the default output dir); runs written to a custom configured ``output_dir`` are not included."
- **Status**: open

## [Tests]
### Issue 1 -- Severity: suggestion
- **File**: modules/api/tests/unit_api_run_listing.py
- **Description**: No test for cancelled run — explicitly required by the task, exercises `duration=None` via `_finish_cancelled`.
- **Suggestion**: Add a test with a terminal `cancelled` record asserting `state == "cancelled"`, `duration_s is None`, `input_path == "cancelled.psd"`.
- **Status**: open

### Issue 2 -- Severity: suggestion
- **File**: modules/api/tests/unit_api_run_listing.py
- **Description**: No test for malformed JSON line — `_terminal_record` has explicit `json.JSONDecodeError` handling that could regress silently.
- **Suggestion**: Write a JSONL with a malformed line followed by a valid terminal record; assert the valid record is still picked up.
- **Status**: open

### Issue 3 -- Severity: suggestion
- **File**: modules/api/tests/unit_api_run_listing.py
- **Description**: No test for empty JSONL file (worker crashes before writing records).
- **Suggestion**: Write an empty `.jsonl` file; assert it is skipped (not in items).
- **Status**: open

### Issue 4 -- Severity: suggestion
- **File**: modules/api/tests/unit_api_run_listing.py:219-229
- **Description**: `test_failed_run_is_listed` only asserts `run_id` and `state`; does not check `input_path` or `duration_s`.
- **Suggestion**: Extend assertions: `input_path == "broken.psd"`, `duration_s == 3.0`.
- **Status**: open

### Issue 5 -- Severity: suggestion
- **File**: modules/api/tests/unit_api_run_listing.py:246-256
- **Description**: `test_unmatched_run_dir_name_reports_unknown_input` only asserts `run_id` and `input_path`; does not check `state` or `duration_s`.
- **Suggestion**: Add `state == "completed"`, `duration_s == 1.0`.
- **Status**: open

### Issue 6 -- Severity: suggestion
- **File**: modules/api/tests/unit_api_run_listing.py
- **Description**: No test for `duration_s is None` when `duration` key is absent from JSONL (vs `duration=0.0` present).
- **Suggestion**: Add a test with a terminal record that omits the `duration` key; assert `duration_s is None`.
- **Status**: open

### Issue 7 -- Severity: suggestion
- **File**: modules/api/tests/unit_api_run_listing.py
- **Description**: No test for "last terminal record wins" — the implementation overwrites on each terminal match; a first-match regression would go undetected.
- **Suggestion**: Write a JSONL with two terminal records (different statuses); assert the last one wins.
- **Status**: open

### Issue 8 -- Severity: nit
- **File**: modules/api/tests/unit_api_run_listing.py
- **Description**: No test for non-`.jsonl` file exclusion — the `glob("*.jsonl")` filter is correct but unverified.
- **Suggestion**: Add a `.txt` file in the log dir; assert it is ignored.
- **Status**: open

### Issue 9 -- Severity: nit
- **File**: modules/api/tests/unit_api_run_listing.py
- **Description**: `test_runs_are_listed_newest_first` only has two runs; a sort that only swaps adjacent pairs would also pass with two elements.
- **Suggestion**: Add a third run with intermediate mtime.
- **Status**: open

## [Simplicity]
### Issue 1 -- Severity: suggestion
- **File**: modules/api/src/surface_api_run_controller.py:66-68
- **Description**: `getattr` fallback is speculative. At runtime the orchestrator is always `SystemOrchestrator` which always has `list_runs`. No sibling controller uses `getattr`.
- **Suggestion**: Remove the `getattr` fallback; call `self._orchestrator.list_runs()` directly. Drop the tautological test.
- **Status**: open

### Issue 2 -- Severity: nit
- **File**: modules/system/src/agent_system_orchestrator.py:841-846
- **Description**: `_input_path_from_run_dir` round-trip check (`strptime` + `strftime` round-trip) is over-thorough for a format with all fixed-width numeric fields.
- **Suggestion**: Drop the round-trip check; `strptime` alone is sufficient.
- **Status**: open

### Issue 3 -- Severity: nit
- **File**: modules/system/src/agent_system_orchestrator.py:356-386
- **Description**: `(mtime, VO)` tuple list is a manual decorate-sort-undecorate, but it is the right trade-off since mtime is already fetched during iteration.
- **Suggestion**: No change needed — noted for awareness.
- **Status**: wontfix