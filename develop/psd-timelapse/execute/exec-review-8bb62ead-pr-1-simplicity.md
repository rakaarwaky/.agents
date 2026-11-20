# PR-1 simplicity review — POST /api/upload multipart endpoint

Scope: over-engineering and unnecessary complexity only. Correctness, security, and test coverage are out of scope. Tests are not flagged for deletion.

## Issue 1 -- Severity: suggestion
- **File**: `modules/api/src/surface_api_upload_controller.py:44-103` (`upload_file`, `asyncio.to_thread`, nested `_write_file`)
- **Description**: The handler is declared `async def` solely to `await file.read(...)`, then wraps the blocking file write in `asyncio.to_thread` to avoid the ASYNC230 ruff violation, plus a nested `_write_file` helper. Every other API route handler in this surface (health, get_config, start_render, get_progress, get_result, cancel_render, retry_render) uses sync `def`. FastAPI already runs sync path operations in a threadpool, so a blocking write is already off the event loop with no extra machinery. Making the handler async creates the ASYNC230 problem and then solves it with `asyncio.to_thread` + a nested helper — an extra abstraction for exactly one caller (the single upload route). This is speculative complexity, not minimal.
- **Suggestion**: Make `upload_file` a sync `def` like the other controllers, read/validate synchronously via `file.file`, and write directly. Remove `asyncio.to_thread`, the nested `_write_file`, and the `import asyncio`. If the ASYNC230 concern is the reason for `async def`, dropping `async def` removes the need for `to_thread` entirely.
- **Status**: open

## Issue 2 -- Severity: suggestion
- **File**: `modules/api/src/surface_api_upload_controller.py:88-95` (`chunks` list accumulation)
- **Description**: After validating the 4-byte magic head, the implementation appends every remaining 1 MB chunk to a Python `chunks` list, then writes with `dest.writelines(chunks)`. For a 500 MB file this holds the entire payload in memory as a list of bytes objects before writing. `UploadFile.file` is a seekable file-like object whose position is already at byte 4 after the head read, so the remainder can be streamed directly to disk with stdlib `shutil.copyfileobj(file.file, dest)` — no intermediate list, no `writelines`, less code, bounded memory. This is the same logic in more lines for one caller.
- **Suggestion**: Replace the `chunks` accumulation loop with `shutil.copyfileobj(file.file, dest)` streaming directly into the opened output file (position is already past the magic bytes). Add `import shutil`, drop `chunks` and the `while` loop.
- **Status**: open
