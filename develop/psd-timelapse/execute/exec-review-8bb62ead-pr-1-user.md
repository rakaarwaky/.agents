# User-perspective review of PR #1 — POST /api/upload multipart endpoint

Reviewed strictly from the end-user point of view: QoL, simplicity, hassle-free ergonomics, cognitive load, time efficiency, and actionable friendly feedback.

## What works well (strengths)

- **Zero-friction directory setup**: the `uploads/` folder under the workspace is created automatically (`mkdir(parents=True, exist_ok=True)`), so the user never has to pre-create anything.
- **No filename-collision hassle**: saved files get UUID names (`<uuid>.psd`), so re-uploading the same PSD never overwrites or conflicts — the user doesn't have to manage unique names.
- **Streaming, memory-friendly writes**: large PSDs are streamed to disk rather than loaded whole into memory, which keeps multi-MB uploads feasible.
- **Clean, concise success response**: `{"path": "/abs/path/uploads/<uuid>.psd"}` — immediately usable as input for the next step (render), no wrapper noise.
- **Sensible default size cap**: 500 MB requires no user configuration and covers realistic PSDs.

## Issues

### Issue 1 -- Severity: suggestion
- **File**: modules/api/src/surface_api_upload_controller.py:67
- **Description**: The oversize error reports the limit as a raw byte count: `PSD file exceeds 524288000 bytes: design.psd`. A user must mentally convert bytes to MB, which adds cognitive load and is not friendly feedback.
- **Suggestion**: Render the limit in human-readable units, e.g. `PSD file exceeds 500 MB: design.psd`.
- **Status**: open

### Issue 2 -- Severity: suggestion
- **File**: modules/api/src/surface_api_upload_controller.py:51 (`file: UploadFile` required parameter)
- **Description**: When a user forgets to attach a file, FastAPI raises a required-parameter validation error that surfaces as the generic `Malformed request payload (1 field error(s))`. It does not tell the user what went wrong in their terms or what to do (attach a `.psd` under the `file` field). This is the most common user mistake and currently the least helpful error.
- **Suggestion**: Give `file` a default of `None` and, when missing, raise an explicit friendly 400 such as `No file attached. Please include a .psd file in the 'file' field.` so the error is actionable without inspecting FastAPI internals.
- **Status**: open

### Issue 3 -- Severity: suggestion
- **File**: modules/api/src/surface_api_upload_controller.py:81-91 (the `upload_file` async handler, `shutil.copyfileobj`)
- **Description**: The blocking file write (`shutil.copyfileobj`) runs directly inside the async `upload_file` handler. For a large upload this blocks the event loop for the duration of the write, stalling the API (health, other uploads, renders) until the file lands on disk. This regresses the thread-offloading approach noted in the PR summary (`asyncio.to_thread`) and hurts time efficiency / responsiveness.
- **Suggestion**: Offload the blocking write to `asyncio.to_thread` so the API stays responsive while large files are being written.
- **Status**: open

### Issue 4 -- Severity: nit
- **File**: modules/api/src/surface_api_upload_controller.py:75
- **Description**: The bad-magic-bytes error says `File ... is not a valid PSD (bad magic bytes)` but does not hint at what a valid PSD looks like, so a user who sees it has no guidance on how to fix the file.
- **Suggestion**: Append the expected signature hint, e.g. `... (bad magic bytes; expected 8BPS signature)`.
- **Status**: open
