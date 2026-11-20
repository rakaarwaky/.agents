### Issue 1 -- Severity: bug
- **File**: `modules/api/tests/unit_api_upload.py:78`
- **Description**: `test_upload_missing_file_returns_error` asserts `response.status_code in (400, 422)`. FastAPI's `RequestValidationError` handler maps a missing `file` part to 400 (`REQUEST_INVALID`), but the loose `in (400, 422)` assertion would still pass if the transport regressed to a raw Starlette 422, so it does not pin the actual contract.
- **Suggestion**: Assert `== 400` and optionally assert the error envelope code is `REQUEST_INVALID` and the message references the missing `file` field.
- **Status**: open

### Issue 2 -- Severity: bug
- **File**: `modules/api/tests/unit_api_upload.py:99-112`
- **Description**: `test_upload_oversize_rejected` monkeypatches `MAX_PSD_FILE_SIZE_BYTES` to 10 and uploads the ~2.2 MB fixture. It asserts only `status_code == 400`, never which validation triggered or the error code. Because extension passes (`.psd`) and size is checked before magic bytes, the 400 is effectively from size — but the test does not prove it.
- **Suggestion**: Assert the error envelope code is `VALIDATION_FAILED` and the message references bytes/size. Consider also a tiny (>10 byte) in-memory body so the boundary does not depend on fixture size.
- **Status**: open

### Issue 3 -- Severity: suggestion
- **File**: `modules/api/tests/unit_api_upload.py` (all error tests)
- **Description**: None of the error-path tests assert the structured error envelope `{"error": {"code", "message", "stage"}}` that the rest of the API surface pins (see `unit_api_inspect.py`/`unit_api_output.py`). Upload tests only check `status_code` and substring-in-`response.text`.
- **Suggestion**: Add envelope assertions for code (`INPUT_UNSUPPORTED` / `VALIDATION_FAILED` / `REQUEST_INVALID`), message content, and `stage == "validating"`. Note: `support_api_envelope.py` is deleted on this branch, so assertions must be inline (as `unit_api_controller.py` does) rather than imported.
- **Status**: open

### Issue 4 -- Severity: suggestion
- **File**: `modules/api/tests/unit_api_upload.py:48-59` (`_client` / `_config_mock`)
- **Description**: Tests use a plain `Mock()` orchestrator (justified in the exec summary because `ISystemAggregate` declares only `execute()`, not `load_config()`). This means nothing guards against `load_config` moving off the aggregate or being renamed — every `orchestrator.load_config()` call is unverified by the type contract.
- **Suggestion**: Keep the plain `Mock()` but assert `orchestrator.load_config.assert_called_once()` in the success test, and assert `load_config` is not called on pre-write validation failures (extension/size/magic happen before config load).
- **Status**: open

### Issue 5 -- Severity: suggestion
- **File**: `modules/api/tests/unit_api_upload.py:61-77`
- **Description**: `test_upload_valid_psd_returns_server_path` asserts content equality and path placement but never verifies `UploadResponse` body shape beyond `"path" in body`, nor that `load_config` was invoked.
- **Suggestion**: Assert `set(body) == {"path"}` and add `orchestrator.load_config.assert_called_once()`.
- **Status**: open

### Issue 6 -- Severity: suggestion
- **File**: `modules/api/tests/unit_api_upload.py`
- **Description**: Missing boundary/edge tests: truncated magic (<4 bytes → `VALIDATION_FAILED`), empty 0-byte body, magic-only 4 bytes (accepted, saves a 4-byte file), uppercase `.PSD` extension, multipart part with `filename=None`/empty-string, and `file.size is None` (size validation is skipped when `size is None`). The "missing file" test sends `files={}` (FastAPI validation rejection), which is not the same as a part whose filename is None/empty — both empirically return 400 but via different paths.
- **Suggestion**: Add tests for truncated/empty/magic-only bodies, uppercase extension, and a part with `filename: None` vs `filename: ""`, asserting the correct code/stage for each.
- **Status**: open

### Issue 7 -- Severity: bug
- **File**: `modules/api/tests/unit_api_local_surface.py:69-79` (`DOCUMENTED_ROUTES`)
- **Description**: PR-1 added `POST /api/upload` but `DOCUMENTED_ROUTES` (and `fixtures/openapi.json`) do not include `/api/upload`. `test_openapi_json_is_served_with_the_documented_routes` asserts an exact route set. This branch already fails that test for a pre-existing reason (`Mock(spec=ISystemAggregate)` has no `load_config` → `AttributeError`), but once that pre-existing breakage is resolved, PR-1's new route will make the snapshot test fail with an extra route not in the snapshot.
- **Suggestion**: Add `("/api/upload", "post")` to `DOCUMENTED_ROUTES` and regenerate `fixtures/openapi.json` to include the upload route.
- **Status**: open

### Issue 8 -- Severity: nit
- **File**: `modules/api/tests/unit_api_upload.py:71`
- **Description**: `test_upload_valid_psd_returns_server_path` asserts `saved.suffix == ".psd"`, which is redundant with `test_upload_idempotent_filename` and always true given the server-generated `{uuid}.psd` name.
- **Suggestion**: Remove the redundant suffix assertion or repurpose it to assert the name matches `^[0-9a-f-]+\.psd$`.
- **Status**: open
