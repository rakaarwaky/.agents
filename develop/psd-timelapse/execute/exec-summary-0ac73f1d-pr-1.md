# Exec Summary — pr-1 (`0ac73f1d`)

## Scope

Backend-only. Adds `GET /api/renders` listing endpoint and
`SystemOrchestrator.list_runs()` so the web Gallery/Queue can be data-driven.
`RunResultVO` is memory-only (`_run_state.last_result`); the only on-disk record
of a finished run is the JSONL evidence file at `<run_dir>/log/<run_id>.jsonl`.
`ISystemAggregate` is NOT extended (single `execute()` entry point preserved).

## Files changed

| File | Change |
|------|--------|
| `modules/shared/src/system/taxonomy_system_vo.py` | New `ListRunsItemVO` frozen dataclass after `RunResultVO`; added to `__all__`. |
| `modules/system/src/agent_system_orchestrator.py` | New `SystemOrchestrator.list_runs()` method + module-level helpers `_terminal_record()` and `_input_path_from_run_dir()`. Imports `json`, `os` (removed — `os` not needed, used `Path.stat()`), `datetime`, `Path`, `Any`, `XDGPaths`, `RUN_FOLDER_TIMESTAMP_FORMAT`, `TERMINAL_STAGE_VALUES`, `ListRunsItemVO`. |
| `modules/api/src/surface_api_schema_view.py` | New `ListRunsItemResponse` and `RunListResponse` Pydantic models; added to `__all__`. |
| `modules/api/src/surface_api_run_controller.py` | New `RunViewController.list_runs()` method (uses `getattr` to reach `list_runs` on the concrete orchestrator, bypassing `ISystemAggregate`); mounts `GET /renders` before `/{run_id}/view`. |
| `modules/api/tests/unit_api_local_surface.py` | Added `("/api/renders", "get")` to `DOCUMENTED_ROUTES` so the OpenAPI exact-match test accounts for the new route. |
| `modules/api/tests/unit_api_run_listing.py` | New test file — 8 tests covering empty dir, completed, failed, no-terminal-record skip, unmatched dir name, newest-first ordering, missing data dir, and aggregate-without-list_runs fallback. |
| `fixtures/openapi.json` | Regenerated via `DISPLAY=:99 uv run python scripts/dump_openapi.py` — adds `ListRunsItemResponse`, `RunListResponse` schemas and `GET /api/renders` path. |

## Key design decisions

1. **`list_runs` on concrete class only** — `ISystemAggregate` has a single
   `execute()` method (AES402). `list_runs` is a new public method on
   `SystemOrchestrator` only. The controller reaches it via `getattr` with a
   graceful empty-listing fallback, matching the design doc's intent without
   widening the contract.

2. **Disk scan over memory** — `RunResultVO` lives in `_run_state.last_result`
   (one run). The listing must see ALL terminal runs across process
   restarts, so it scans `XDGPaths.data_dir()/*/log/*.jsonl`. Each JSONL file is
   reduced to its LAST terminal record (status in `TERMINAL_STAGE_VALUES`).

3. **PSD stem extraction** — Run dirs are `<psd-stem>-<timestamp>` where the
   timestamp is `RUN_FOLDER_TIMESTAMP_FORMAT` (`%Y-%m-%d_%Hh%Mm%Ss`, 17 chars).
   `_input_path_from_run_dir` strips the trailing `-<timestamp>` and appends
   `.psd`. Dirs that don't match return `"unknown"`.

4. **Robustness** — File reads wrapped in try/except (`OSError`,
   `json.JSONDecodeError`); missing data dir returns `[]`; no exceptions
   propagate.

5. **Sort order** — Newest-first by JSONL file mtime (`stat().st_mtime`),
   which is a robust proxy for run completion time.

6. **Test uses real `SystemOrchestrator` with fakes** — Following
   `unit_api_controller.py` pattern (FakeConfiguration, FakeWorkspace,
   FakeEvidence, FakePipeline). The real orchestrator is needed because
   `ISystemAggregate` spec on a Mock hides `list_runs`. `XDG_DATA_HOME` is
   monkeypatched to `tmp_path` so the orchestrator scans test-created run dirs.

## Testing

| Command | Result |
|---------|--------|
| `uv run ruff check modules/` | All checks passed |
| `uv run ruff format --check <changed files>` | 4 files already formatted (orchestrator has pre-existing format issues unrelated to this change) |
| `uv run pytest modules/api/tests/unit_api_run_listing.py -q` | 8 passed |
| `uv run mypy <changed source files>` | No new errors (pre-existing monkey-patch attr-defined errors remain) |
| `DISPLAY=:99 uv run python scripts/dump_openapi.py` | Wrote fixture with new schemas + path |
| `uv run lint-arwaky-cli scan <each changed file>` | 0 violations on source files; test file has 1 AES101 (naming convention, same as all existing `unit_api_*` test files) |

## Deviations from plan

1. **`os` import removed** — The plan suggested `os`/`pathlib.Path` "as needed".
   Used `Path.stat().st_mtime` and `Path.iterdir()` instead of `os.path.getmtime`
   / `os.listdir`, so `os` was not imported (ruff F401 would flag it).

2. **`_terminal_record` returns a tuple, not a dict** — Initially returned
   `dict[str, object]` which caused mypy `arg-type` errors when constructing
   `ListRunsItemVO`. Changed to `tuple[str, float | None]` for type safety.

3. **Test uses real orchestrator, not Mock** — `Mock(spec=ISystemAggregate)`
   doesn't expose `load_config` (not on the contract) and the controller's
   `_managed_output_dirs` calls it lazily. The real `SystemOrchestrator` with
   fake protocols is the established pattern (`unit_api_controller.py`) and
   avoids the issue entirely.

4. **`support_api_envelope` import avoided** — `unit_api_output.py` and other
   tests import `from support_api_envelope import envelope`, but that module was
   deleted in commit `117a0fff` (the helper was consolidated into
   `unit_api_envelope.py` but the imports were not updated). Those tests are
   currently broken at collection. My new test does not depend on it.

5. **`DOCUMENTED_ROUTES` updated** — The exact-match OpenAPI test in
   `unit_api_local_surface.py` would fail without adding `("/api/renders",
   "get")`. This test was already failing on the base commit (30 failures due to
   the `support_api_envelope` issue), but the route set is now correct.

## Reviewer notes

- The orchestrator's pre-existing `ruff format --check` failures (3 files
  repo-wide) are unrelated to this change and exist on the base commit. My
  added code does not appear in the format diff.
- The `support_api_envelope` import breakage in `unit_api_output.py`,
  `unit_api_events.py`, `unit_api_inspect.py`, and `unit_api_controller.py` is
  pre-existing (commit `117a0fff` deleted the file without updating imports).
  My new test file does not depend on it.
- The `getattr` pattern in `RunViewController.list_runs` is intentional: it
  keeps `ISystemAggregate` narrow (single `execute` entry point) while letting
  the listing reach the concrete orchestrator. An aggregate that doesn't expose
  `list_runs` returns `{"items": []}` rather than 500.