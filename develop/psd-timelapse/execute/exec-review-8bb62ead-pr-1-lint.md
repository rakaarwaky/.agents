# PR-1 lint review — POST /api/upload multipart endpoint

Scope: linting, formatting, type diagnostics, and architectural rule compliance (`lint-arwaky`, `ruff`, `mypy`). General business logic, security, and test coverage are out of scope.

## Linter execution summary

- `uv run lint-arwaky-cli scan modules/api`: exit 0, 0 violations.
- `uv run lint-arwaky-cli report .`: exit 0, 0 violations in `modules/api` (56 pre-existing violations outside `modules/api`: `packages/shared` 29, `packages/psd` 11, `PRD.md` 6, `ROADMAP.md` 6, `packages/client` 3, `modules/system` 1).
- `uv run ruff check modules/api/`: exit 0 (`All checks passed!`).
- `uv run ruff format --check modules/api/`: exit 0 (`22 files already formatted`).
- AES naming conventions: `modules/api/src/surface_api_upload_controller.py` follows the `surface_` prefix requirement.
- Import hygiene: all imports in `surface_api_upload_controller.py` are ordered and used; one unused constant exists in `unit_api_upload.py` (Issue 1 below).
- `uv run mypy --config-file mypy-api.ini modules/api/src modules/root_api_main_entry.py`: reports `"ISystemAggregate" has no attribute "load_config"` at `modules/api/src/surface_api_upload_controller.py:81` (consistent with existing `ISystemAggregate` method access in `surface_api_controller.py`, `surface_api_run_controller.py`, `surface_api_output_controller.py`, and `surface_api_events_controller.py`; Issue 2 below).

### Issue 1 -- Severity: nit
- **File**: `modules/api/tests/unit_api_upload.py:32`
- **Description**: `CORRUPT_FIXTURE = REPO_ROOT / "fixtures" / "corrupt.psd"` is defined at module level and never referenced anywhere in the file (nor used across the test suite).
- **Suggestion**: Remove the unused `CORRUPT_FIXTURE` constant or use `CORRUPT_FIXTURE.read_bytes()` inside `test_upload_invalid_magic_bytes_rejected`.
- **Status**: open

### Issue 2 -- Severity: suggestion
- **File**: `modules/api/src/surface_api_upload_controller.py:81`
- **Description**: `self._orchestrator.load_config()` produces a mypy `[attr-defined]` error under `mypy-api.ini` (`"ISystemAggregate" has no attribute "load_config"`), matching the existing pattern across `surface_api_controller.py`, `surface_api_run_controller.py`, `surface_api_output_controller.py`, and `surface_api_events_controller.py` where `ISystemAggregate` only declares `execute()` in `modules/shared/src/system/contract_system_aggregate.py`. Note that `.github/workflows/ci.yml` includes a `Dump OpenAPI snapshot` and `git diff --exit-code fixtures/openapi.json` check; `fixtures/openapi.json` is currently out of date with the new `/api/upload` schema unless `uv run python scripts/dump_openapi.py` output is committed.
- **Suggestion**: Dispatch `LOAD_CONFIG` through `self._orchestrator.execute(SystemRequestVO(operation=SystemOperationVO.LOAD_CONFIG)).config` (or declare the concrete protocol on `ISystemAggregate`) and regenerate/commit `fixtures/openapi.json` via `uv run python scripts/dump_openapi.py`.
- **Status**: open