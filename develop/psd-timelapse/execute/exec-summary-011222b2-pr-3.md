# Implementation Summary: pr-3 Client Agent Orchestrator & DI Container

## Files Changed
1. `packages/client/src/agent_client_orchestrator.ts` — Core orchestrator fixes
2. `packages/client/tests/unit_client_orchestrator.test.ts` — New test + updated assertions
3. `packages/client/tests/integration_client_flow.test.ts` — Integration test assertion
4. `packages/client/tests/contract_client_conformance.test.ts` — Error-path conformance tests

## Changes Detail

### Bug Fix 1: Lifecycle ordering (agent_client_orchestrator.ts)
Moved `queueMicrotask(() => onStatus("open"))` to AFTER `subscribeEvents(...)` returns. The method now:
1. Fires `onStatus("connecting")`
2. Calls `subscribeEvents(...)` and captures the return value
3. Schedules `onStatus("open")` via `queueMicrotask`
4. Returns the unsubscribe function

If `subscribeEvents` throws synchronously, the error propagates naturally and "open" is never fired — only "error" fires via the error callback path.

### Bug Fix 2: Terminal success/failure conflation (agent_client_orchestrator.ts)
Added `if (result.error)` guard at the top of `terminalCb`:
- If `result.error` exists → `onError(new Error(result.error.message))` + `onStatus("closed")`
- If no error → `getOutputMeta` → `onComplete` + `onStatus("closed")`

Also fixed the `.catch` path to fire `onStatus("closed")` instead of `onStatus("error")` — the terminal path always ends in "closed" regardless of success or failure.

### Suggestion Fix 3: Style improvements (agent_client_orchestrator.ts)
- Removed redundant `as Record<string, unknown>` cast on `payload.summary`
- `top_level_count` now reads `summary.top_level_count` when present, falling back to `payload.layer_count`
- Kept `as PipelineStageVO` cast on `RunViewResponsePayload.stage` (unavoidable — wire type is `string`)
- Kept `total: 100` (no `total` field in `RunViewResponsePayload` — it's the full-scale denominator for percent)

### Test Fix 4: Terminal→getOutputMeta rejection test (unit_client_orchestrator.test.ts)
Added new test "handles terminal then getOutputMeta rejection — fires onError" that:
- Mocks `render.getOutputMeta.mockRejectedValueOnce(new Error("OUTPUT_NOT_FOUND"))`
- Emits a terminal frame via `streamCb.onTerminal(FIXTURE_RUN_RESULT)`
- Asserts `errors[0].message === "OUTPUT_NOT_FOUND"` and `statuses` contains "closed"

### Test Fix 5: Integration 404 path (integration_client_flow.test.ts)
The existing test already uses `aggregate.watchProgress("nonexistent-run", ...)` against the live mock server. Added `expect(statuses).toContain("open")` to verify lifecycle ordering at the integration layer.

### Test Fix 6: Conformance error paths (contract_client_conformance.test.ts)
Added two error-path tests:
- "retry on active run returns 409 conflict" — asserts `ApiTransportError` with `status=409`, `retryable=true`
- "invalid input rejects with 400" — asserts `ApiTransportError` with `status=400`, `retryable=false`

## Test Results
All 292 tests pass across 39 test files.

## Deferred Issues
Issues 4-9 in Tests section and Issues 1-6 in Simplicity section remain deferred (cosmetic, non-blocking coverage gaps).