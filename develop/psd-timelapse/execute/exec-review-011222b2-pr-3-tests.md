# Test Review — PR 3: Client Agent Orchestrator & DI Container

**Branch:** `rakaarwaky/011222b2-pr-3`  
**Reviewer:** GrokBuild subagent (test-engineer lens)  
**Date:** 2026-11-18  

---

## Summary

The PR adds a TypeScript `ClientOrchestrator` (4 injected protocols, implements `IClientAggregate`) plus a DI container (`createClientAggregate`) and three new test files (`unit_client_orchestrator.test.ts`, `contract_client_conformance.test.ts`, `integration_client_flow.test.ts`) plus a mock server (`fixture_client_mock_server.ts`). All 289 existing tests pass unchanged; zero regressions.

Coverage breadth across the nine aggregate methods is good (delegation mapping, AbortSignal forwarding, basic SSE lifecycle). However, several non-trivial error paths in `watchProgress` are uncovered, the conformance test exercises only happy-paths, and the integration test suite lacks two realistic error-mode flows.

---

## Findings

### [bug] `unit_client_orchestrator.test.ts`; Missing test: `terminal → getOutputMeta rejects`; Uncovered

**Description:** In `agent_client_orchestrator.ts:127–137`, the `terminalCb` calls `renderCapability.getOutputMeta(result.run_id)` and chains `.then().catch()`. The `.catch` branch calls `onStatus("error")` and `onError(...)`. No unit test fires a `terminal` event and then makes `getOutputMeta` reject. The existing terminal test (`fires connecting→open→progress→terminal→closed in order`) stubs `render.getOutputMeta.mockResolvedValueOnce(FIXTURE_OUTPUT_META)` — the success path only.

**Suggestion:** Add a `watchProgress` sub-test where `stream.subscribeEvents` injects an `onTerminal` handler that triggers `getOutputMeta` to reject (e.g. `render.getOutputMeta.mockRejectedValueOnce(new Error("meta unavailable"))`). Assert that `statuses` contains `"error"` (not just `"closed"`) and `errors` is non-empty.

**Status: open**

---

### [bug] `integration_client_flow.test.ts`; Missing test: genuine server-side 404 on SSE subscribe; Not synthetic callback invocation

**Description:** The integration test's `"error path: non-2xx before stream"` block invokes the onError callback directly inside the mock server callback chain rather than producing an actual HTTP 404 on the `/api/renders/nonexistent-run/events` endpoint. The mock server's `events` route returns `errorEnvelope(res, 404, ...)` for unknown run IDs (see `fixture_client_mock_server.ts:297`), but the integration test sidesteps this by calling the error-handler closure directly. As a result, the end-to-end path `fetch(404) → normalizeErrorEnvelope → ApiTransportError throw → stream.onError(...)` is exercised by `unit_client_stream.test.ts` but not by the integration layer against the live mock server.

**Suggestion:** Replace the direct-callback invocation with a proper `aggregate.watchProgress("nonexistent-run", ...)` call and `await waitMicrotask()`. Verify `errors[0]` is an `ApiTransportError` with `status === 404`. Remove the current block that manually drives the error closure.

**Status: open**

---

### [bug] `contract_client_conformance.test.ts`; Conformance test covers only happy-paths; Error paths untested

**Description:** All six conformance tests use inline mocks that resolve successfully. `IClientRenderProtocol.retryRender` never tests the 409 `ACTIVE_JOB_CONFLICT` error case. `IClientStreamProtocol.subscribeEvents` never tests a non-2xx fetch or a network error reaching `onError`. `IClientInspectProtocol.inspectPsd` never tests an invalid input path throwing `ClientError`. The contract test claims runtime verification of "all 9 methods delegate correctly" but never asserts any rejection behavior.

**Suggestion:** Extend the inline mocks so that at least one method per protocol rejects. For example: `retryRender` rejects with an `ApiTransportError(409)`, `subscribeEvents` calls `onError(new TypeError("network"))` synchronously, `inspectPsd` throws `ClientError("INVALID_INPUT")`. Assert that these propagate through the orchestrator's delegation layer. This strengthens the "client satisfies IClientAggregate at both compile-time and runtime" claim.

**Status: open**

---

### [suggestion] `unit_client_orchestrator.test.ts`; Protocol rejections are untested; Only resolved mocks used

**Description:** Every injected protocol in the orchestrator unit tests resolves successfully (`mockResolvedValueOnce`). There is no test asserting that a rejection from `inspectPsd`, `startRender`, `getOutputMeta`, `getView`, `cancelRender`, `retryRender`, `getHealth`, or `getConfig` propagates as a rejected promise from the corresponding orchestrator method. Since the orchestrator contains zero try/catch around delegation, the correctness of raw rejection passthrough must still be verified to guard against future defensive wrapping that would break the AES405 constraint ("no business calculation — pure orchestration/sequencing").

**Suggestion:** Add one parametrized test: for each public async method, mock the underlying protocol to reject with a distinct Error, assert the orchestrator method rejects with the same Error instance (identity check via `expect(...).rejects.toBe(errorInstance)`). This pins the passthrough guarantee.

**Status: open**

---

### [suggestion] `unit_client_orchestrator.test.ts`; Missing: `already-subscribed, second watchProgress concurrently`

**Description:** The orchestrator holds no session state beyond the four injected dependencies. Calling `watchProgress` twice with different run IDs simultaneously creates two independent SSE subscriptions. Neither the first run's callbacks nor the second run's callbacks cross-contaminate each other — but this is implicit from the design, never asserted.

**Suggestion:** Add a test creating two `watchProgress` subscriptions with distinct `runId` values, feeding each its own sequence of state/progress/terminal events through separate `streamCb` captures. Verify that callbacks for run A never fire for events belonging to run B.

**Status: open**

---

### [suggestion] `unit_client_orchestrator.test.ts`; Missing: `watchProgress` unsubscribe before any events arrive

**Description:** The "unsubscribe return type" test only asserts that the return value is a function. It never calls that function, nor does it verify that calling it suppresses further callbacks. Given that the `queueMicrotask(() => { onStatus("open") })` fires regardless of whether unsubscribe was called, unsubscribing early could leave the microtask's `"open"` status callback outstanding if the internal stream is still listening.

**Suggestion:** Call the returned unsubscribe function immediately (or within a microtask tick) after `watchProgress`, then verify `statuses` contains `"connecting"` and `"open"` but NOT `"closed"` — or confirm the behavior matches the intended API contract. Document the expected semantics.

**Status: open**

---

### [suggestion] `unit_client_orchestrator.test.ts`; Missing: `inspect` with `summary` absent from response payload

**Description:** The `mapInspectResponse` helper casts `payload.summary as Record<string, unknown>` then accesses `.width` and `.height`. If the server omits the `summary` key entirely, `typeof summary.width` is `"undefined"`, defaulting to `0`. This silent fallback path is never exercised by any test — all fixtures include `summary: { width, height }`.

**Suggestion:** Add a test with `{ valid: true, summary: {}, layer_count: 2, layers: [...] }` and assert `result.width === 0 && result.height === 0`.

**Status: open**

---

### [nit] `integration_client_flow.test.ts`; `waitMicrotask` uses `setTimeout` with 20 ms instead of `new Promise(r => queueMicrotask(r))`

**Description:** The helper defined in the integration test file delays 20 ms via `setTimeout`, while the unit test file defines its own with 10 ms. These are longer than necessary and make the integration tests flaky under load. The orchestrator's `queueMicrotask(() => { onStatus("open") })` guarantees the `"open"` status within a single JS microtask turn. Using `await new Promise(r => queueMicrotask(r))` would be deterministic.

**Suggestion:** Replace the custom `waitMicrotask` helper in the integration test with `await new Promise(r => queueMicrotask(r))`. Align with the unit test pattern for consistency.

**Status: open**

---

### [nit] `unit_client_orchestrator.test.ts`; `waitMicrotask` defined locally vs. imported/shared

**Description:** The unit test file defines its own 10 ms `waitMicrotask`. The integration test file defines its own 20 ms version. They serve the same purpose. If they drift, maintenance cost grows.

**Suggestion:** Extract a shared utility in `packages/client/tests/shared/helpers.ts` (or reuse the one already present elsewhere if available) so both test files import the same function.

**Status: open**

---

## Coverage Gaps Matrix

| Method / Path | Unit (orchestrator) | Contract | Integration |
|---|---|---|---|
| `inspect` — delegation | ✅ | partial | N/A |
| `inspect` — AbortSignal | ✅ | ❌ | N/A |
| `inspect` — protocol rejects | ❌ | ❌ | N/A |
| `inspect` — empty summary | ❌ | ❌ | N/A |
| `startRender` — delegation | ✅ | partial | ✅ |
| `startRender` — outputPath null | ✅ | ❌ | N/A |
| `startRender` — AbortSignal | ✅ (via inspect only) | ❌ | N/A |
| `checkProgress` — delegation | ✅ | partial | ✅ |
| `checkProgress` — error-mapped message | ❌ | ❌ | N/A |
| `fetchResult` — delegation | ✅ | partial | ✅ |
| `cancel` — true / false | ✅ | partial | ✅ |
| `retry` — delegation | ✅ | partial | ✅ |
| `watchProgress` — full lifecycle | ✅ | ❌ | ✅ |
| `watchProgress` — error-after-progress | ✅ | ❌ | N/A |
| `watchProgress` — already-terminal-at-open | ✅ | ❌ | N/A |
| `watchProgress` — error-before-open | ✅ | ❌ | ❌ (synthetic only) |
| `watchProgress` — terminal + getOutputMeta reject | ❌ | ❌ | N/A |
| `watchProgress` — concurrent multi-run | ❌ | ❌ | N/A |
| `watchProgress` — unsubscribe before events | ❌ | ❌ | N/A |
| `probeHealth` — delegation / AbortSignal | ✅ | partial | N/A |
| `loadConfig` — delegation / AbortSignal | ✅ | partial | N/A |
| Mock server — retry returning 409 | ❌ | ❌ | ❌ |
| Mock server — GET /health degraded | ❌ | ❌ | ❌ |
| Mock server — output.meta unavailable | ❌ | ❌ | ❌ |

---

## Verdict

**Pass with conditions.** The core orchestrator logic is well-covered for its happy-path delegation contracts. Three bugs remain open that could mask regressions if the `terminalCb`'s `.catch` path ever changes: (1) the `getOutputMeta` rejection branch, (2) the genuine 404 integration flow, and (3) the broader protocol-rejection passthrough gap. Fixing these before merge is recommended. The remaining items are suggestions/nits suitable for follow-up.
