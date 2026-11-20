# Review — PR-1: Add Python `POST /api/upload` multipart endpoint

**Reviewer**: general-purpose code reviewer (persona: meticulous; correctness → style; security & plan-alignment folded in).
**Scope reviewed**:
- `modules/api/src/surface_api_upload_controller.py` (new)
- `modules/api/tests/unit_api_upload.py` (new)
- `modules/api/src/surface_api_schema_view.py` (modified)
- `modules/api/src/surface_api_controller.py` (modified)

**References**: exec summary, `modules/api/DESIGN.md`, `modules/api/BACKLOG.md`, `modules/shared/src/system/taxonomy_system_error.py`, `modules/api/src/surface_api_response_view.py`.

## Plan alignment

The local PSD Timelapse API surface (`DESIGN.md` DS-API-001..009) covers health, config, inspect, render lifecycle, events, output, CORS/correlation, and OpenAPI. `POST /api/upload` is **not** enumerated in the current `DESIGN.md` or `BACKLOG.md`. The implementation summary references a "plan-doc section covering this PR" but no such section exists in `modules/api/DESIGN.md` or `modules/api/BACKLOG.md` as written. Treat plan alignment as **unverifiable from the repo state**: either the upload endpoint is scope creep beyond the documented API surface, or the plan doc is missing the corresponding DS-API entry. Flagged as Issue 1.

## Summary of defects found

The endpoint is well-structured and the controller pattern matches the rest of the surface (single class, `register(router)`, `response_model`, error envelope, `VALIDATING` stage). The magic-bytes check correctly handles the short-read edge case. The main gaps are: (1) oversize enforcement is a TOCTOU hole when `Content-Length` is absent, (2) magic bytes are checked before the size cap (a malicious sender can force the server to read a full over-limit body), (3) the filename is interpolated into the error response verbatim (log/header injection), (4) one stat call on every success path, (5) a latent defect in the documented `asyncio.to_thread` write loop, and (6) the `ISystemAggregate` mock pattern deviates from the `Mock(spec=...)` convention used by every sibling test.

## Issues

### Issue 1 -- Severity: bug
- **File**: `modules/api/DESIGN.md` (missing entry for `POST /api/upload`)
- **Description**: The new route is not present in the API `DESIGN.md` (DS-API-001..009) nor in `BACKLOG.md`. The exec summary claims a "plan-doc section covering this PR," but no such section exists in the committed repo state. This is either undocumented scope creep or a missing plan entry that should be reconciled before merge.
- **Suggestion**: Either add a `DS-API-010: Upload input` row to `DESIGN.md` (and the matching `BACKLOG.md` row) before merge, or remove the endpoint if it is out of scope for this PR. Confirm against the originating plan doc.
- **Status**: open

### Issue 2 -- Severity: bug
- **File**: `modules/api/src/surface_api_upload_controller.py:64`
- **Description**: The size cap is enforced only when `file.size` is populated. `UploadFile.size` is set by Starlette only when the incoming request carries a `Content-Length` header. A client using `Transfer-Encoding: chunked` (or any sender that omits `Content-Length`) causes `file.size` to be `None`, so the 500 MB limit is silently skipped and the full body is read into memory by the `while chunk := await file.read(...)` loop at lines 89-90. This is a TOCTOU / resource-exhaustion hole: an unauthenticated loopback caller can force the process to buffer an arbitrarily large file into RAM.
- **Suggestion**: Track bytes read during the streaming loop and abort with the same 400/`VALIDATION_FAILED` once the running total exceeds `MAX_PSD_FILE_SIZE_BYTES`. Alternatively, reject requests that lack a `Content-Length` before reading. Add a test that posts a chunked body (or mocks `file.size` as `None`) to pin the new behavior.
- **Status**: open

### Issue 3 -- Severity: bug
- **File**: `modules/api/src/surface_api_upload_controller.py:73-79`
- **Description**: Magic bytes are validated *before* the size cap can be enforced on a chunked request (Issue 2). For a `Content-Length`-less upload, the server reads the first 4 bytes (fine), then reads the entire body into `chunks` with no cap — the validation order means a malicious sender can force a full-body read of an over-limit file before any rejection happens. Even with `Content-Length` present, the check order is only safe because the size check happens to run first; the comment at line 72 ("Read the first chunk to validate magic bytes before streaming the rest") documents the order but does not make the order sufficient.
- **Suggestion**: Move or duplicate the size enforcement into the streaming loop (see Issue 2), and add the running-byte check *before* appending each chunk. Reorder so the size cap is the first gate that can fire on every path, independent of `Content-Length`.
- **Status**: open

### Issue 4 -- Severity: bug
- **File**: `modules/api/src/surface_api_upload_controller.py:58` and `surface_api_upload_controller.py:74`
- **Description**: The client-supplied `filename` is interpolated verbatim into the error message returned to the caller (`f"Only .psd files can be uploaded: {filename}"`) and into the 400 envelope. `UploadFile.filename` is the multipart `filename=` value, which a caller fully controls. It can contain CR/LF (header/log injection in any downstream consumer that logs the message), control characters, or unbounded length (response/log bloat). The message is also echoed to the client on loopback via `_handle_unexpected_error`, but these two raises are deliberate 400s that always echo.
- **Suggestion**: Sanitize before interpolation: strip CR/LF and non-printables, cap length (e.g. first 64 chars), and prefer a constant message (`"Only .psd files can be uploaded"`) with the filename dropped, or quote/escape it. Apply the same treatment to the magic-bytes message at line 74.
- **Status**: open

### Issue 5 -- Severity: suggestion
- **File**: `modules/api/src/surface_api_upload_controller.py:98`
- **Description**: `saved_path.stat().st_size` is called purely for a log line. `stat()` is a blocking syscall issued on the event-loop thread after `asyncio.to_thread` returned — it is a (small) async anti-pattern in a function that otherwise correctly offloads blocking I/O, and it adds one syscall per upload for log-only value. It also re-opens the TOCTOU window between write and stat.
- **Suggestion**: Have `_write_file()` return the byte count it wrote (`return dest.tell()` or sum of `len(c)`), then log that value. Avoid the extra stat syscall and keep all filesystem access off the loop thread.
- **Status**: open

### Issue 6 -- Severity: bug
- **File**: `modules/api/src/surface_api_upload_controller.py:90-94`
- **Description**: The streaming loop `while chunk := await file.read(1024 * 1024): chunks.append(chunk)` accumulates **all** chunks in a list and only writes them in `_write_file()` after EOF. For a 500 MB upload this holds the entire file in memory twice (chunk list + `writelines` buffering), defeating the purpose of streaming and the `asyncio.to_thread` offload (the expensive part is the giant `writelines` call, not the per-chunk write). The endpoint can OOM on a large-but-legal upload.
- **Suggestion**: Write incrementally: open the destination inside `_write_file` and feed chunks to it via a thread-safe queue / `asyncio.Queue`, or have `_write_file` pull from an iterator that `await`s each `file.read`. Alternatively, copy to a `SpooledTemporaryFile` and then move/rename into the uploads dir. At minimum, document that the whole file is buffered and add a test with a multi-chunk upload that asserts bounded memory behavior.
- **Status**: open

### Issue 7 -- Severity: bug
- **File**: `modules/api/src/surface_api_upload_controller.py:73-79` (test gap)
- **Description**: The magic-bytes edge case the reviewer was asked to confirm (file shorter than 4 bytes, e.g. `b"8BP"` or `b""`) is handled correctly by `if len(head) < 4 or head[:4] != _PSD_MAGIC`, but no test pins it. `test_upload_invalid_magic_bytes_rejected` only covers the wrong-bytes case (`b"NOTAPSD"`, 7 bytes). A short-file path is currently untested and a future refactor could regress it.
- **Suggestion**: Add a parametrized case covering `b""`, `b"8", b"8B", b"8BP"` → all must 400 with `VALIDATION_FAILED`. Also add a `b"8BPS"`-only body (exactly 4 bytes, valid magic, no PSD structure) to confirm the controller does *not* over-claim validity at the magic-byte gate (it currently accepts it, which is correct for this gate but worth pinning).
- **Status**: open

### Issue 8 -- Severity: suggestion
- **File**: `modules/api/tests/unit_api_upload.py:37`
- **Description**: The test uses `Mock()` instead of `Mock(spec=ISystemAggregate)`. The exec summary justifies this because `ISystemAggregate` (the ABC at `contract_system_aggregate.py:20`) declares only `execute()` and not `load_config()`. That is accurate for the ABC, but every sibling test (`unit_api_local_surface.py:90`, `unit_api_container.py`, `unit_cli_surfaces.py`) uses `Mock(spec=ISystemAggregate)` and it works there because the concrete orchestrator (`agent_system_orchestrator.py:201`) defines `load_config`. Using a bare `Mock()` silently accepts any attribute access, so a typo like `orchestrator.load_cnfig()` in the controller would not fail the test. The deviation weakens the contract check.
- **Suggestion**: Either keep `Mock(spec=ISystemAggregate)` and add `load_config` to the spec via `Mock(spec=ISystemAggregate)` plus an explicit `spec`-extension, or (preferred) make the controller depend on a narrower protocol that declares `load_config`. At minimum, document why this test intentionally diverges from the sibling pattern, and add an assertion that the controller calls `load_config` exactly once.
- **Status**: open

### Issue 9 -- Severity: suggestion
- **File**: `modules/api/tests/unit_api_local_surface.py:63` (`DOCUMENTED_ROUTES`)
- **Description**: `test_openapi_json_is_served_with_the_documented_routes` asserts the published route set equals `DOCUMENTED_ROUTES` **exactly** (`assert documented == DOCUMENTED_ROUTES`). Adding `POST /api/upload` registers a new route in `ApiController.__init__` but does not update `DOCUMENTED_ROUTES`. This test will now fail. The exec summary does not mention running the full API suite or updating this snapshot.
- **Suggestion**: Add `("/api/upload", "post")` to `DOCUMENTED_ROUTES`. Re-run `uv run pytest modules/api/ -q` and confirm all tests (including the OpenAPI drift test) pass before merge.
- **Status**: open

### Issue 10 -- Severity: suggestion
- **File**: `modules/api/tests/unit_api_upload.py:81-83`
- **Description**: `test_upload_missing_file_returns_error` accepts either 400 or 422 (`assert response.status_code in (400, 422)`). The rest of the surface consistently answers malformed input with 400 via `RequestValidationError` handler (`surface_api_controller.py:185`). A 422 would mean the `RequestValidationError` handler is not installed or not matched, which is a regression. The loose assertion hides that.
- **Suggestion**: Pin the exact status (400) and the error code (`REQUEST_INVALID`) so a handler regression is caught. If FastAPI genuinely returns 422 for a missing multipart part in this version, document why and add an explicit test for the `RequestValidationError` handler.
- **Status**: open

### Issue 11 -- Severity: suggestion
- **File**: `modules/api/tests/unit_api_upload.py:37-49` (`_config_mock` and `_client`)
- **Description**: The test constructs a full `SystemConfigVO` with every field spelled out (codec, crf, preset, pixel_format, output_size, frame_rate). This duplicates the defaults already in `SystemConfigVO` and couples the upload test to unrelated config fields. If a default changes, this test breaks for no reason. The `_client` helper also imports `ScriptingContainer` inside the function body (line 54), which is unusual; the sibling test imports `ScriptingAggregate` at module top and uses `Mock(spec=ScriptingAggregate)`.
- **Suggestion**: Use `SystemConfigVO(output_dir=..., workspace_dir=...)` and rely on the dataclass defaults for the rest. Use `Mock(spec=ScriptingAggregate)` like the sibling tests, or import `ScriptingContainer` at the top.
- **Status**: open

### Issue 12 -- Severity: suggestion
- **File**: `modules/api/src/surface_api_upload_controller.py:28`
- **Description**: `MAX_PSD_FILE_SIZE_BYTES` is a module-level constant read directly inside `upload_file`. The oversize test (`unit_api_upload.py:102`) monkeypatches the module attribute, which works, but the controller reads the constant at call time via module global lookup. This is fine functionally, but the value is not sourced from `SystemConfigVO` (which is the config source of truth for the rest of the surface). If operators ever need to tune the limit per-deployment, it cannot be configured without a code change.
- **Suggestion**: Either (a) leave as a module constant and document that it is intentionally non-configurable for P0, or (b) surface it via `SystemConfigVO` so the limit is configurable like `output_dir`/`workspace_dir`. Pick one and document the choice in `DESIGN.md`.
- **Status**: open

### Issue 13 -- Severity: nit
- **File**: `modules/api/src/surface_api_upload_controller.py:88-95`
- **Description**: `chunks` is a `list[bytes]` accumulated solely to be passed to `dest.writelines(chunks)`. `writelines` accepts any iterable, so the list materialization is unnecessary even for the current (non-streaming) design. Minor memory overhead.
- **Suggestion**: Pass a generator or write each chunk as it arrives inside `_write_file` (which also fixes Issue 6). If keeping the buffered design, use a `bytearray`/single `b"".join(chunks)` and a single `dest.write(...)` to halve peak memory.
- **Status**: open

### Issue 14 -- Severity: nit
- **File**: `modules/api/src/surface_api_upload_controller.py:81`
- **Description**: `self._orchestrator.load_config()` is called on every upload to resolve `workspace_dir`. For the local profile this is a cheap config read, but it is a synchronous call on the event-loop thread (no `to_thread`). The sibling `get_config`/`_managed_output_dirs` also call it synchronously, so this matches the existing pattern and is not a regression — noted only for completeness.
- **Suggestion**: No change required for P0. If `load_config` ever becomes expensive (file I/O, env parsing), wrap it in `asyncio.to_thread` for consistency with the write path.
- **Status**: open

## Verdict

**Request changes.** The endpoint's shape, validation gate structure, error envelope usage, and controller registration follow the existing surface conventions, and the magic-bytes short-read edge case is handled correctly. However, Issues 2/3/6 are correctness defects that let an unauthenticated caller bypass the size cap (chunked uploads) or force unbounded memory buffering, Issue 4 is a log/header-injection vector, Issue 9 is a CI-breaking test regression, and Issue 1 is an unresolved plan-alignment question (no documented DS-API entry for `/api/upload`). The new unit tests cover the happy path and the simple rejection cases but do not exercise the chunked-upload, short-file, or multi-chunk paths that the additional focus areas call out.

Minimum to merge: resolve Issues 1 (plan doc), 2/3 (size cap on chunked bodies), 4 (filename sanitization), 6 (streaming write), 8 (test mock pattern), and 9 (OpenAPI route snapshot).