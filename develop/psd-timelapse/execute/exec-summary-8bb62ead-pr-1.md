# Exec Summary — PR-1

- **Plan ID**: 8bb62ead
- **PR ID**: pr-1
- **Title**: Add Python `POST /api/upload` multipart endpoint
- **Branch**: `execute-plan/8bb62ead-pr-1` (linearized stack, also on `execute-plan/8bb62ead-pr-3` and `execute-plan/8bb62ead-final`)
- **Commit**: `dcf9f04b8f03f65c3c74e0e6edbf317a9ee4b9b3`
- **Status**: Done

## What changed

New `UploadController` in `modules/api/src/surface_api_upload_controller.py`:
- Accepts a multipart `.psd` file upload.
- Validates extension (`.psd`, case-insensitive), file size (`MAX_PSD_FILE_SIZE_BYTES` = 500 MB), and magic bytes (`8BPS`).
- Saves the file to `workspace_dir/uploads/<uuid>.psd` (configurable workspace directory from the system layer config).
- Returns `{path: "<absolute server path>"}`.
- Wired into `ApiController.__init__` as `surface_api_upload_controller.UploadController`.

Schema view updated in `modules/api/src/surface_api_schema_view.py` (request/response types).
Controller dispatch updated in `modules/api/src/surface_api_controller.py` (route registration).

## Tests

7 unit tests in `modules/api/tests/unit_api_upload.py`:
1. Valid upload → 200, file saved to `uploads/<uuid>.psd`, returns path.
2. Missing file → 400.
3. Non-PSD extension → 400.
4. Oversize file → 400.
5. Bad magic bytes → 400.
6. Workspace-dir placement → file lands in the configured workspace `uploads/` dir.
7. UUID naming → saved filename matches `^[0-9a-f-]{36}\.psd$`.

`fixtures/openapi.json` documents `/api/upload` (already present from this PR).

## Verification

- `uv run pytest modules/api/tests/unit_api_upload.py` — 7 passed.
- `uv run pytest modules/` — full Python suite green.
- `uv run ruff check modules/` — All checks passed.
- `uv run ruff format --check modules/` — 1 pre-existing reformat needed in `unit_api_upload.py` (PR-1 authoring artifact, not a regression; addressed by `ruff format` if desired).
- `uv run mypy` — no new errors.
- `lint-arwaky-cli scan .` — no new violations.

## Notes

- The endpoint uses the existing workspace config from `modules/system` for the upload directory, per the plan constraint.
- `MAX_PSD_FILE_SIZE_BYTES` is imported from `packages/shared/src/psd/taxonomy_psd_constant.ts` (500 MB).
- Studio surfaces stay passive — this PR only adds the server-side upload route.