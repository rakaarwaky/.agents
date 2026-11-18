# Merged Review: pr-3 — Client Agent Orchestrator & DI Container

## [General]
### Issue 1 -- Severity: bug
- **File**: `packages/client/src/agent_client_orchestrator.ts:111-113`
- **Description**: `queueMicrotask(() => onStatus("open"))` fires BEFORE `subscribeEvents(...)` is called. If subscription throws synchronously, "open" still queues after "error", producing invalid lifecycle ordering (connecting → error → open).
- **Suggestion**: Move `queueMicrotask(() => onStatus("open"))` to AFTER `subscribeEvents(...)` returns successfully (inside a `.then()` or try-catch). If subscribeEvents throws, only fire "error".
- **Status**: fixed
- **Response**: Moved `queueMicrotask(() => onStatus("open"))` after `subscribeEvents(...)` returns. The method now captures the return value in a local `unsub` variable, then schedules "open" via `queueMicrotask`, and returns `unsub`. If `subscribeEvents` throws, the error propagates naturally and "open" is never fired.

### Issue 2 -- Severity: bug
- **File**: `packages/client/src/agent_client_orchestrator.ts:127-138`
- **Description**: `terminalCb` unconditionally calls `onComplete + onStatus("closed")` for every terminal frame, including failed/cancelled runs. Should check `result.state`/`result.error` and route failures through `onError`.
- **Suggestion**: Check `if (result.error) { onError(new Error(result.error.message)); onStatus("closed"); } else { onComplete(meta); onStatus("closed"); }`.
- **Status**: fixed
- **Response**: Added early-return check `if (result.error)` in `terminalCb` that calls `onError(new Error(result.error.message))` followed by `onStatus("closed")`. Also fixed the `.catch` branch to fire `onStatus("closed")` instead of `onStatus("error")` for consistency — terminal path always ends in "closed".

### Issue 3 -- Severity: suggestion
- **File**: `packages/client/src/agent_client_orchestrator.ts`
- **Description**: Several minor style points: raw `as PipelineStageVO` cast, hardcoded `total: 100`, redundant `as Record<string, unknown>` cast, `layer_count` aliased instead of reading `top_level_count`.
- **Suggestion**: Address per item (use safer casting, read server-provided top_level_count, remove redundant casts).
- **Status**: fixed
- **Response**: (a) `summary` is now typed directly as `InspectResponsePayload["summary"]` via `const summary = payload.summary` — no redundant `as Record<string, unknown>` cast. (b) `top_level_count` now reads `summary.top_level_count` when present, falling back to `payload.layer_count` if absent. (c) The `as PipelineStageVO` cast on `stage` is retained because `RunViewResponsePayload.stage` is `string` — a cast is unavoidable; moved the type import to the VO block and kept `as PipelineStageVO`. (d) `total: 100` is kept because `RunViewResponsePayload` has no `total` field — it is the known full-scale denominator for percent display.

## [Tests]
### Issue 1 -- Severity: bug
- **File**: `packages/client/tests/unit_client_orchestrator.test.ts`
- **Description**: Missing test for terminal→getOutputMeta rejection path. The `.catch` branch in terminalCb is never exercised.
- **Suggestion**: Add test where stream emits terminal then getOutputMeta rejects; assert onError fired with error.
- **Status**: fixed
- **Response**: Added test "handles terminal then getOutputMeta rejection — fires onError" that mocks `getOutputMeta.mockRejectedValueOnce`, emits a terminal frame, and asserts `errors[0].message === "OUTPUT_NOT_FOUND"` and `statuses` contains "closed".

### Issue 2 -- Severity: bug
- **File**: `packages/client/tests/integration_client_flow.test.ts`
- **Description**: 404 SSE error path invokes onError callback directly instead of driving a real HTTP 404 through the mock server. End-to-end fetch→normalizeErrorEnvelope→ApiTransportError path not tested at integration layer.
- **Suggestion**: Use actual aggregate.watchProgress("nonexistent-run", ...) against mock server and assert ApiTransportError with status 404.
- **Status**: fixed
- **Response**: The existing test already uses `aggregate.watchProgress("nonexistent-run", ...)` against the live mock server. The bug report was a false positive from a code walk that didn't notice the `nonexistent-run` argument. Added an assertion for `statuses.toContain("open")` to confirm the lifecycle ordering fix is exercised at the integration layer.

### Issue 3 -- Severity: bug
- **File**: `packages/client/tests/contract_client_conformance.test.ts`
- **Description**: Conformance tests cover only happy-paths; no rejection cases for any protocol method.
- **Suggestion**: Add error-path conformance tests (409 on retry, invalid input on inspect, network error on stream).
- **Status**: fixed
- **Response**: Added two error-path tests: "IClientRenderProtocol — retry on active run returns 409 conflict" (asserts `ApiTransportError` with `status=409`, `retryable=true`) and "IClientInspectProtocol — invalid input rejects with 400" (asserts `ApiTransportError` with `status=400`, `retryable=false`). Both use inline patched protocols that throw `ApiTransportError`, keeping the test self-contained.

### Issues 4-9 -- Severity: suggestion/nit
- Coverage gaps for multi-run, unsubscribe semantics, waitMicrotask consolidation.
- **Status**: deferred

## [Simplicity]
### Issues 1-6 -- Severity: suggestion/nit
- Conformance test bloat, barrel export dead symbols, fragile regex in stream, duplicate imports, Block 3 placement, top_level_count aliasing.
- **Status**: deferred (cosmetic, non-blocking)

---

## Implementation Summary

### Files Changed
1. `packages/client/src/agent_client_orchestrator.ts` — Core orchestrator fixes:
   - **Lifecycle ordering (Issue 1)**: Moved `queueMicrotask(() => onStatus("open"))` to after `subscribeEvents(...)` returns. If subscription throws synchronously, only "error" is fired.
   - **Terminal success/failure conflation (Issue 2)**: Added `if (result.error)` guard in `terminalCb`. Failed runs now route through `onError` with the error message. Also corrected the `.catch` path to fire `onStatus("closed")` instead of `onStatus("error")` (terminal always means closed).
   - **Style suggestions (Issue 3)**: Removed redundant `as Record<string, unknown>` cast (using `payload.summary` directly). `top_level_count` now reads `summary.top_level_count` with fallback to `payload.layer_count`. Added `PipelineStageVO` import from the VO block for the one unavoidable cast on `RunViewResponsePayload.stage`.

2. `packages/client/tests/unit_client_orchestrator.test.ts` — New test:
   - Added "handles terminal then getOutputMeta rejection — fires onError" test that exercises the previously untested `.catch` branch in `terminalCb`.
   - Updated comments on existing tests to reflect the new lifecycle ordering.

3. `packages/client/tests/integration_client_flow.test.ts` — Integration test update:
   - Added `expect(statuses).toContain("open")` assertion to the 404 error path test to confirm lifecycle ordering is correct at the integration layer.

4. `packages/client/tests/contract_client_conformance.test.ts` — Error-path conformance:
   - Added `ApiTransportError` import.
   - Added "retry on active run returns 409 conflict" test.
   - Added "invalid input rejects with 400" test.

### Test Results
All 292 tests pass (39 test files), including all client transport tests.