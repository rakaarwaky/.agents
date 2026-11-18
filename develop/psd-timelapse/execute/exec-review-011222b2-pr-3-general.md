# Review Notes — PR #3: Client Agent Orchestrator & DI Container

**Branch:** `rakaarwaky/011222b2-pr-3`
**Date:** 2026-11-18
**Reviewer scope:** Files added/modified by commit `b1ce4781`:
- `packages/client/src/agent_client_orchestrator.ts`
- `packages/client/src/root_client_container.ts`
- `packages/client/src/index.ts`
- `packages/client/tests/unit_client_orchestrator.test.ts`
- `packages/client/tests/contract_client_conformance.test.ts`
- `packages/client/tests/integration_client_flow.test.ts`
- `packages/client/tests/fixture_client_mock_server.ts`
- `packages/client/BACKLOG.md`

All checks ran locally: TypeScript strict mode passes (`tsc -p root_tsconfig_entry.json --noEmit` exit 0), lint-arwaky scan of `packages/client` reports **0 violations**, 148 client tests across 13 files pass (14 passed, 148 tests).

---

### Verdict: Needs fixes before merge (2 bugs, 1 locked-in incorrect behavior, 4 suggestions/nits)

The implementation is architecturally sound: four protocols injected, pure orchestration, no direct I/O in the orchestrator, canonical 3-block structure, correct DI wiring (`stream` takes `baseUrl` not `transport`), and comprehensive tests. However, two real bugs in the orchestrator plus one test that codifies incorrect lifecycle ordering must be fixed prior to landing.

---

## Issues

### Issue 1 -- Severity: bug
- **File**: `packages/client/src/agent_client_orchestrator.ts:111-113`
- **Description**: The `queueMicrotask(() => onStatus("open"))` is scheduled *before* `subscribeEvents` is called (line 148-154). If the subscription fails synchronously — e.g., `streamCapability.subscribeEvents` throws immediately — the caller receives an exception from `watchProgress`, yet the queued microtask still fires `onStatus("open")` afterward. In practice `ClientStream.subscribeEvents` never throws synchronously, but the pattern is fragile and the scheduler's placement guarantees incorrect behaviour for any future caller or mock. Worse, the unit test at `unit_client_orchestrator.test.ts:537` explicitly asserts `statuses` contains `"open"` even when an error callback fired first, locking in the wrong ordering.
- **Suggestion**: Move the `queueMicrotask` for `"open"` inside the successful-resume path of `subscribeEvents`, or guard it with a subscription-success flag. Alternatively, invoke `onStatus("open")` only after `subscribeEvents` returns cleanly; do not schedule it beforehand.
- **Status**: open

### Issue 2 -- Severity: bug
- **File**: `packages/client/src/agent_client_orchestrator.ts:127-138`
- **Description**: The `terminalCb` unconditionally routes every terminal SSE frame through the success path (`onComplete` + `onStatus("closed")`), ignoring whether the run actually failed. The `RunResultResponsePayload` carries both `state` (e.g. `"failed"` / `"cancelled"`) and `error` (non-null on failure). When the backend emits a terminal frame for a failed run, the consumer receives `onComplete(meta)` with whatever metadata the output-meta fetch returns — even though `available` will be `false`. The caller has no visibility that the run itself failed; they only learn it indirectly from `meta.available`. This breaks the clear success/failure split promised by the orchestrator contract.
- **Suggestion**: Inspect `result.state` and/or `result.error` inside `terminalCb` and route to `onError(new Error(result.error?.message ?? \`Render ${result.state}\`))` for terminal stages other than `completed`. For a `completed` terminal, keep the existing `onComplete` + `onStatus("closed")` path. Update the contract doc comment on `IClientAggregate.watchProgress` to clarify that `onComplete` only fires for completed runs, while failures route through `onError`.
- **Status**: open

### Issue 3 -- Severity: suggestion
- **File**: `packages/client/tests/unit_client_orchestrator.test.ts:537`
- **Description**: The test named "handles error-before-open (ApiTransportError before any onState/onProgress)" asserts `expect(statuses).toContain("open")`. Combined with Issue 1, this codifies incorrect lifecycle ordering: for a stream that errors before opening, consumers see `["connecting", "open", "error"]`. That makes the status stream non-deterministic — `open` appearing after `error` — which violates a reasonable contract a caller might rely on.
- **Suggestion**: Revise this assertion once Issue 1 is fixed. The corrected order for the error-before-open path should be `["connecting", "error"]` (with `open` skipped entirely) or `["connecting", "error", "open"]` only if the design intentionally wants the connection acknowledged after error (unlikely). Prefer removing the `open` expectation so the test enforces the clean ordering you want.
- **Status**: open

### Issue 4 -- Severity: nit
- **File**: `packages/client/src/agent_client_orchestrator.ts:189`
- **Description**: `mapViewToProgressSnapshot` casts the wire-stage string directly to `PipelineStageVO` via `payload.stage as ProgressSnapshotVO["stage"]`. The server-side `RunViewResponsePayload.stage` is declared `string` (intentionally loose), but any unrecognized value silently smuggles past the cast into the VO layer, breaking the invariant that `ProgressSnapshotVO.stage` is drawn from the union defined in `taxonomy_pipeline_stage_vo.ts`.
- **Suggestion**: Replace the unsafe cast with a runtime validation helper or a lookup map. E.g.:
  ```ts
  const knownStages = new Set([
    "idle","validating","planning","animating","compositing","encoding",
    "completed","failed","cancelled"
  ]);
  // or use a type guard
  ```
  Fall back to `"idle"` for unrecognized values and optionally surface via telemetry. This aligns with the defensive posture already taken elsewhere (e.g., the `summary.width` default-to-0 in `mapInspectResponse`).
- **Status**: open

### Issue 5 -- Severity: nit
- **File**: `packages/client/src/agent_client_orchestrator.ts:191`
- **Description**: `mapViewToProgressSnapshot` hardcodes `total: 100` and derives both `current` and `percent` from the single `payload.progress` field. The server-side `RunViewController._progress_percent` returns a bounded float in `[0, 100]`, so `current === percent` here is correct under the current protocol, but it makes the three fields redundant. Any future backend change sending `progress` as an absolute frame count would silently break the semantic promise of `ProgressSnapshotVO` (which distinguishes current vs percent).
- **Suggestion**: Add a clarifying comment documenting the assumption that `progress` is a percentage, not an absolute count. Consider adding a type-level alias such as `type PercentValue = number;` in the taxonomy to signal intent to readers, rather than leaving it implicit.
- **Status**: open

### Issue 6 -- Severity: nit
- **File**: `packages/client/src/agent_client_orchestrator.ts:166`
- **Description**: `const summary = payload.summary as Record<string, unknown>` is a redundant cast. `payload.summary` is already typed as `Record<string, unknown>` per `InspectResponsePayload` (`shared/src/client/taxonomy_client_response.ts:40`), so the cast is unnecessary noise.
- **Suggestion**: Replace with `const summary = payload.summary;`. Style-only; no behavioural impact.
- **Status**: open

### Issue 7 -- Severity: suggestion
- **File**: `packages/client/src/agent_client_orchestrator.ts:175`
- **Description**: `top_level_count` is mapped from `payload.layer_count` — the top-level array length returned by `/inspect`. The Python-side `PsdInfoVO` has both `layer_count` (descendants) and `top_level_count` (first-level layers) as distinct concepts, populated from separate `len(list(psd.descendants()))` and `len(top_level)` in `capabilities_psdtools_adapter.py:80-86`. The `inspect_payload` serializes them into the `summary` dict at `surface_api_response_view.py:251-258`, but the orchestrator reads them from the *wrapper* keys (`payload.layer_count`) rather than from `summary.top_level_count`. Under typical PSDs these happen to match because the API only returns top-level layers in `layers` and the controller echoes that length, but a future refactor where `layers` carried descendants would desync the fields.
- **Suggestion**: Read `summary.top_level_count` directly (with fallback to `payload.layer_count`) when present, making the mapping explicit and resilient to future schema changes:
  ```ts
  const topLevelCount =
    typeof summary.top_level_count === "number"
      ? summary.top_level_count
      : payload.layer_count;
  ```
- **Status**: open

### Issue 8 -- Severity: nit
- **File**: `packages/client/tests/integration_client_flow.test.ts:17-20`
- **Description**: `waitMicrotask` uses `setTimeout(resolve, 20)` — a macrotask millisecond sleep — despite its name suggesting a true microtask wait. On fast local hardware it works; on slow CI containers it may occasionally race the SSE processing. All 148 client tests pass here, so it's working today.
- **Suggestion**: Replace with `vi.waitFor` (already available via vitest) so tests fail clearly rather than timing out. Either change improves robustness without behavioural difference.
- **Status**: open

---

## Checks Passed

| Check | Result |
|-------|--------|
| AES405 `check_agent_routing` — aggregate implementor + ≤3 types + no `any` | ✅ Pass (1 type decl, no `any`) |
| AES405 `check_agent_block_order` — Block 2 before Block 3 | ✅ Pass |
| AES405 `check_agent_protocol_forbidden` — does not implement capability protocol | ✅ Pass (implements `IClientAggregate`, not `IClient*Protocol`) |
| AES405 `check_agent_block_markers` — max block number 3 | ✅ Pass (blocks 1–3) |
| AES405 `check_agent_io_forbidden` — no fetch/fs/EventSource inside orchestrator | ✅ Pass (all I/O delegated) |
| AES405 `check_agent_constant_placement` — no file-level constants | ✅ Pass |
| AES405 `check_agent_computation` — no arithmetic/fold/reduce | ✅ Pass (only field renames + ternaries) |
| AES405 `check_agent_stateless` — no mutation outside ctor | ✅ Pass |
| AES405 `check_agent_free_fn` — no module-level functions | ✅ Pass |
| AES405 `check_agent_subsystem_count` — ≥2 injected protocols | ✅ Pass (4: inspect, render, stream, system) |
| `lint-arwaky-cli scan packages/client` | ✅ 0 violations |
| `tsc --noEmit` | ✅ Pass |
| All client tests pass | ✅ 148 / 148 |
| `root_client_container.ts` wires `stream` with `baseUrl` not `transport` | ✅ Correct (commented explicitly on lines 33-35) |
| `index.ts` barrel completeness | ✅ Exports createClientAggregate, ClientOrchestrator, all protocols/V Os/payloads/errors/constants/utilities |
| `fixture_client_mock_server.ts` SSE frames | ✅ Matches backend: `retry:` line, `state`/`progress`/`terminal` events with correct snake_case payloads |
| Backend wire-shape conformance | ✅ Verified against `modules/api/src/surface_api_schema_view.py` and `surface_api_response_view.py`; `RunViewResponse` stage/type contracts match |

---

## Summary

PR #3 delivers a correct, well-structured orchestrator and DI composition root that satisfies the architectural contract. Two real bugs remain: (1) lifecycle ordering lets `"open"` race ahead of `"error"` when subscription fails, and (2) the terminal handler conflates successful and failed runs, calling `onComplete` even on failures. One test encodes the first bug as expected behavior and must be updated alongside the fix. The remaining five items are style/nit suggestions that improve long-term maintainability but don't break correctness today.
