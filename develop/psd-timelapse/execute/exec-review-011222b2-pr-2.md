# Merged Review: pr-2 — Client Capabilities Implementation

## [General]
### Issue 1 -- Severity: bug
- **File**: `packages/client/src/capabilities_client_stream.ts:117`
- **Description**: SSE stream chunk buffering drops partial frames. When `frames.length > 0`, buffer is unconditionally cleared, discarding any trailing incomplete frame data split across chunk boundaries.
- **Suggestion**: Maintain unconsumed stream data: find last `\r?\n\r?\n` boundary, parse only up to that boundary, keep remainder in buffer for next read cycle.
- **Status**: fixed
- **Response**: Updated buffer clearing logic to locate the last SSE event boundary (`\r?\n\r?\n`) and retain any trailing incomplete frame data for the next read cycle.

### Issue 2 -- Severity: bug
- **File**: All 5 capability files (`capabilities_client_inspect.ts`, `capabilities_client_render.ts`, `capabilities_client_stream.ts`, `capabilities_client_system.ts`, `capabilities_client_transport.ts`)
- **Description**: Capability files use non-canonical banner comments (`// ── Type Definitions ──`, etc.) instead of required AES canonical markers: `// ─── Block 1: Module Declaration ───`, `// ─── Block 2: Module Contract ───`, `// ─── Block 3: Module Helpers ───`. Triggers AES403 violations.
- **Suggestion**: Replace banner comments with canonical Block 1/2/3 headers in all 5 files.
- **Status**: fixed
- **Response**: Replaced custom banner comments in all five capability files with canonical AES 3-block markers.

### Issue 3 -- Severity: bug
- **File**: `packages/client/FRD.md` (lines 38, 79, 120, 203, 249)
- **Description**: Technical Specification tables for FR-CLIENT-001, 002, 003, 005, and 006 omit the mandatory `| Event | None |` row required by AES609 (only FR-CLIENT-004 has it). Also references concrete source filenames like `contract_client_protocol.ts`, `utility_client_parser.ts`, `capabilities_client_*.ts` which violates AES609:source_file_named.
- **Suggestion**: Add `| Event | None |` row to each non-streaming FR table. Replace concrete source file names with architectural descriptions.
- **Status**: fixed
- **Response**: Added `| Event | None |` to all non-streaming FR Technical Specification tables and replaced concrete source filename references in the FRD with abstract architectural seam descriptions.

### Issue 4 -- Severity: suggestion
- **File**: `packages/client/src/capabilities_client_transport.ts:67`
- **Description**: Caught `AbortError` always reported as "Request timed out" even when caused by caller signal abort. Standard `TimeoutError` falls through to generic message.
- **Suggestion**: Check `timeoutSignal.aborted` or `err.name === "TimeoutError"` for timeouts; check `callerSignal?.aborted` for caller cancellation.
- **Status**: fixed
- **Response**: Differentiated caller cancellation (`callerSignal?.aborted`) from timeout abort (`timeoutSignal.aborted` or `AbortError`/`TimeoutError`) in `capabilities_client_transport.ts`.

### Issue 5 -- Severity: suggestion
- **File**: `packages/client/FRD.md` (lines 11, 24, 273–277)
- **Description**: FRD references concrete source filenames (`contract_client_protocol.ts`, `utility_client_parser.ts`, `capabilities_client_*.ts`). AES architecture requires FRDs to specify requirements without naming source files.
- **Suggestion**: Replace with abstract descriptions of seams and responsibilities.
- **Status**: fixed
- **Response**: Replaced concrete source file references in `FRD.md` with abstract architectural descriptions of subsystem responsibilities and seams.

### Issue 6 -- Severity: nit
- **File**: `packages/client/src/capabilities_client_transport.ts:62`
- **Description**: FRD edge case states "POST without body → sends empty JSON body `{}`" but implementation sends `undefined` (no body).
- **Suggestion**: Either default empty POST bodies to `{}` or update FRD to match actual behavior.
- **Status**: fixed
- **Response**: Aligned the FRD edge case statement (`POST without body → sends request without body payload`) with the actual transport behavior.

## [Tests]
### Issue 1-5 -- Severity: suggestion/nit
- Various test coverage gaps (caller signal composition, non-JSON error responses, SSE chunk buffering, malformed JSON frames, reader.cancel after terminal). No bugs found.
- **Status**: deferred (low priority, no blocking bugs)

## [Simplicity]
### Issue 1-5 -- Severity: suggestion/nit
- Single-field DI wrapper types, inlinable helper method, redundant options interfaces, duplicate imports, duplicated mock factory. No bugs.
- **Status**: deferred (cosmetic, no correctness impact)
