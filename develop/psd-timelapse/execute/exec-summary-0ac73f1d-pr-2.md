# PR 2 / 7 — Extend client contract with `inspectFull`, `downloadOutput`, `listCompletedRuns`

Worktree: `0ac73f1d-pr-2`, branch `rakaarwaky/0ac73f1d-pr-2` (committed locally; not pushed).

## Files changed

| File | Change |
|------|--------|
| `packages/shared/src/client/taxonomy_client_response.ts` | Added `ListRunsItemResponse` interface (run_id, state, input_path, duration_s). |
| `packages/shared/src/client/taxonomy_client_vo.ts` | Added `InspectFullVO`, `RenderDownloadVO`, `RenderCompletedVO`; type-only import of `LayerPayload`. |
| `packages/shared/src/client/contract_client_protocol.ts` | Added `getOutput(runId, signal?): Promise<Blob>` and `listCompletedRuns(signal?): Promise<readonly ListRunsItemResponse[]>` to `IClientRenderProtocol`. |
| `packages/shared/src/client/contract_client_aggregate.ts` | Added `inspectFull`, `downloadOutput`, `listCompletedRuns` to `IClientAggregate` (aggregate now has 12 methods). |
| `packages/client/src/capabilities_client_render.ts` | Implemented `getOutput` (raw `fetch` of `/renders/:run_id/output`, non-JSON error normalization via `normalizeErrorEnvelope`, returns `Blob`) and `listCompletedRuns` (GET `/renders` via transport). Added `baseUrl` to `RenderDeps` (defaults to `API_BASE_URL_DEFAULT`), so `getOutput` can build its own URL. |
| `packages/client/src/root_client_container.ts` | Wired `config.baseUrl` into `ClientRender`. |
| `packages/client/src/agent_client_orchestrator.ts` | Implemented `inspectFull` (reuses `inspectPsd` + maps layers), `downloadOutput` (delegates to `getOutput`, wraps into `RenderDownloadVO`), `listCompletedRuns` (wire→VO mapping). |
| `packages/client/src/index.ts` | Re-exported the three new VOs and `ListRunsItemResponse`. |
| `packages/client/tests/fixture_client_mock_server.ts` | Added `output` route in `parsePath` (before `/renders/:run_id` catch-all) and `case "output"` returning fake MP4 bytes with `Content-Type: video/mp4` + `Content-Disposition`. `case "renders"` now branches on `req.method`: GET returns 2 canned `ListRunsItemResponse` items; POST keeps the existing startRender behavior. |
| `packages/client/tests/unit_client_render.test.ts` | New tests: `getOutput` happy path against the mock server (Blob type + size), `getOutput` non-ok response (stubbed `fetch` returning 404), `listCompletedRuns` via mocked transport + AbortSignal forwarding. |
| `packages/client/tests/unit_client_orchestrator.test.ts` | New tests: `inspectFull` returns doc info + layers; `downloadOutput` returns `{blob, filename, sizeBytes}` with default filename and forwards signal; `listCompletedRuns` maps snake_case→camelCase. |
| `packages/client/tests/contract_client_conformance.test.ts` | Mock protocols/aggregates extended for the new methods; assertions updated (9 render methods, 12 aggregate methods). |
| `packages/client/tests/contract_client_protocol.test.ts` | `MockRenderProtocol` / `MockClientAggregate` extended with the new methods. |
| `packages/client/tests/contract_client_schema.test.ts` | Added `LIST_RUNS_ITEM_FIELDS` pinned against the OpenAPI `ListRunsItemResponse` schema (4/4 fields, matches the live schema from pr-1). |
| `packages/shell/tests/unit_client_hook.test.tsx` | Fixed pre-existing tsc error: `Harness` now passes `children` inside the props object of `createElement(ClientProvider, {...})` instead of as a third positional argument (which React types reject because `ClientProviderProps.children` is required). |

## Key design decisions

1. **Filename defaults to `timelapse_<runId>.mp4`** (documented in the orchestrator): `IClientRenderProtocol.getOutput` returns `Promise<Blob>` per the design doc; `Blob` does not carry `Content-Disposition` headers, so the filename is not available to the orchestrator. The mock server still sets the header (future-proofing), but `RenderDownloadVO.filename` uses the deterministic default. Changing the protocol to return `{blob, filename}` would have been the alternative, but the doc explicitly pins the Blob-only signature.
2. **`getOutput` bypasses `IClientTransportProtocol`**: the transport is JSON-only (`response.json()` + JSON error envelope). Raw MP4 requires a direct `fetch` + `response.blob()`, mirroring the existing `ClientStream` pattern that owns its own HTTP access because it needs `ReadableStream`. Non-OK responses are still normalized through the shared `normalizeErrorEnvelope` so callers get `ApiTransportError` with the same retryability rules.
3. **Mock server GET vs POST on `/renders`**: `parsePath` already mapped `/renders` → `"renders"`, so the route handler now branches on `req.method`. The `/renders/:run_id/output` match was inserted before the `/renders/:run_id` catch-all in `parsePath` (otherwise `output` would be parsed as a run id).

## Deviations from the plan

- The plan's `getOutput` test "throws on 404/409" is not testable against the mock server, which always returns 200 for the output route. Covered instead by stubbing `globalThis.fetch` to return a 404 `Response` and asserting the thrown `ApiTransportError` (status 404). Same code path the mock-server tests exercise.
- Fixed one pre-existing tsc error in `shell/tests/unit_client_hook.test.tsx` (unrelated to this PR) because `npm run typecheck` is the gate and must pass clean.

## Testing

Ran from `packages/`:

```
npm run typecheck   # tsc -p root_tsconfig_entry.json --noEmit → exit 0
npm test -- --run   # vitest → 40 files, 307 tests, all passed
```

All 307 tests pass, including the 16 new ones across `unit_client_render.test.ts`, `unit_client_orchestrator.test.ts`, `contract_client_conformance.test.ts`, and the schema pin in `contract_client_schema.test.ts`.

## Reviewer attention

- `taxonomy_client_vo.ts` now has a type-only import from `taxonomy_client_response.js` (`LayerPayload`) — a taxonomy↔taxonomy import, allowed per ARCHITECTURE layer rules; flag if the lint gate disagrees.
- `RenderDownloadVO.filename` is always the default; if surfaces later need the real filename, `getOutput` must be changed to return `{blob, filename}`.
- `client/tests/unit_client_render.test.ts` uses `Blob`/`Response` in node env (vitest `// @vitest-environment node` via the test script setup) — worked in the suite; no polyfills needed.
