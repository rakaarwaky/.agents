# Code Review — PR 2: Extend client contract with `inspectFull`, `downloadOutput`, `listCompletedRuns`

**Branch**: `rakaarwaky/0ac73f1d-pr-2`
**Commits**: 1 (`63844d4a feat(client): extend contract with inspectFull, downloadOutput, listCompletedRuns`)
**Scope check**: Additive contract/capability work only. No changes to `home/`, `studio/`, `queue/`, `gallery/`, `root_web_main_entry.ts`, or Python modules. No scope creep detected. All planned files were modified as specified.

---

## Issues

### Issue 1 -- Severity: bug
- **File**: `packages/client/src/capabilities_client_render.ts:128`
- **Description**: `listCompletedRuns` calls `this.transport.get<ListRunsItemResponse[]>(ROUTE_RENDERS, signal)` which expects a bare JSON array, but the live FastAPI endpoint `GET /api/renders` returns a `RunListResponse` object `{ "items": ListRunsItemResponse[] }` (confirmed in `fixtures/openapi.json:368-384` and `modules/api/src/surface_api_run_controller.py:59-77`). The runtime will receive `{items: [...]}` and `items.map(...)` in `agent_client_orchestrator.ts:198` will fail with `items.map is not a function` because `items` is the wrapper object, not the array. The mock server (`fixture_client_mock_server.ts:180-186`) also returns a bare array, masking this contract violation in tests. The test at `unit_client_render.test.ts:283-295` asserts `result).toEqual(items)` with a bare array, encoding the wrong expectation.
- **Suggestion**: Either (a) change `listCompletedRuns` to unwrap the `RunListResponse` envelope: `const resp = await this.transport.get<{items: ListRunsItemResponse[]}>(ROUTE_RENDERS, signal); return resp.items;`, and update the mock server to return `{items: [...]}` to match the live API; or (b) if the design doc explicitly specifies a bare-array response, file a follow-up to change the Python API to match. Given the OpenAPI spec is authoritative, option (a) is correct.
- **Status**: open

### Issue 2 -- Severity: bug
- **File**: `packages/client/tests/fixture_client_mock_server.ts:180-186`
- **Description**: The `GET /renders` mock returns a bare array `[{run_id, state, ...}, ...]` but the live API returns `RunListResponse({items: [...]})`. This is a fixture/live mismatch that hides Issue 1 in tests. The mock is the only integration test of `listCompletedRuns` against a real HTTP round-trip; if it returns the wrong shape, the test gives false confidence.
- **Suggestion**: Change the `GET` branch to `return json(res, 200, { items: [{run_id: "run-completed-1", ...}, {run_id: "run-failed-1", ...}] });` to match the OpenAPI schema. Then update the corresponding unit test at `unit_client_render.test.ts:283` to expect the wrapped shape and unwrap it (or have `listCompletedRuns` unwrap it internally).
- **Status**: open

### Issue 3 -- Severity: suggestion
- **File**: `packages/shell/tests/unit_client_hook.test.tsx:29-39`
- **Description**: The `mockClient` mock (cast with `as unknown as IClientAggregate`) is missing the three new methods: `inspectFull`, `downloadOutput`, `listCompletedRuns`. Because of the `as unknown as` cast, TypeScript does not flag this, and the shell tests pass. However, any future test in the shell that tries to call one of the new methods on `mockClient` will hit `mockClient.inspectFull is not a function` at runtime. The shell is a consumer of `IClientAggregate` and should have a complete mock.
- **Suggestion**: Add `inspectFull: vi.fn()`, `downloadOutput: vi.fn()`, `listCompletedRuns: vi.fn()` to the `mockClient` object literal.
- **Status**: open

### Issue 4 -- Severity: suggestion
- **File**: `packages/shared/src/client/contract_client_protocol.ts:47`
- **Description**: `listCompletedRuns` is declared on `IClientRenderProtocol` returning `Promise<readonly ListRunsItemResponse[]>`. If Issue 1 is fixed (unwrapping `RunListResponse`), this return type is correct. But the `IClientRenderProtocol` is the low-level HTTP protocol — it should arguably return the wire shape (`RunListResponse`) and let the orchestrator unwrap, consistent with how `inspectPsd` returns `InspectResponsePayload` (the raw wire shape) and the orchestrator maps it. Currently the protocol pre-unwraps (or would need to), which leaks wire-shape knowledge into the capability layer. This is a layering concern, not a correctness bug.
- **Suggestion**: If Issue 1 is fixed by unwrapping inside `ClientRender.listCompletedRuns`, document that the protocol returns the inner items (not the wire envelope) to make the divergence from "protocol returns wire shape" explicit. Alternatively, return `RunListResponse` from the protocol and unwrap in the orchestrator.
- **Status**: open

### Issue 5 -- Severity: nit
- **File**: `packages/shared/src/client/contract_client_protocol.ts:16`
- **Description**: Import order in `contract_client_protocol.ts` was changed to put `CancelResponsePayload` first alphabetically, but this is a cosmetic reordering that adds noise to the PR diff without functional benefit.
- **Suggestion**: Either keep the alphabetical reorder (it's correct) or revert to minimize diff. Not worth a separate commit; acceptable as-is.
- **Status**: open

### Issue 6 -- Severity: nit
- **File**: `packages/client/tests/contract_client_conformance.test.ts:100`
- **Description**: Inline `import(...)` type in `listCompletedRuns` mock return type: `Promise<readonly import("../../shared/src/client/taxonomy_client_response.js").ListRunsItemResponse[]>` is unnecessarily verbose. `ListRunsItemResponse` is already imported at the top of the file (line 41). This is a style inconsistency.
- **Suggestion**: Use the imported `ListRunsItemResponse` type directly: `Promise<readonly ListRunsItemResponse[]>`.
- **Status**: open

### Issue 7 -- Severity: nit
- **File**: `packages/client/tests/unit_client_orchestrator.test.ts:760`
- **Description**: File ends without a trailing newline (`});$` with no `$` on a final blank line). Most style guides require files to end with a single newline.
- **Suggestion**: Add a trailing newline to the file.
- **Status**: open

---

## Verification of Design-Doc Alignment

| Check | Result |
|-------|--------|
| `inspectFull` correctly spreads `mapInspectResponse` + adds `layers` | ✅ `agent_client_orchestrator.ts:74-81` |
| `downloadOutput` returns `{blob, filename, sizeBytes}` with default filename | ✅ `agent_client_orchestrator.ts:185-193`, `filename: timelapse_<runId>.mp4` |
| `getOutput` does raw `fetch` (not JSON transport) | ✅ `capabilities_client_render.ts:108-125`, uses `fetch` + `response.blob()` |
| `getOutput` handles non-OK with error normalization | ✅ `capabilities_client_render.ts:115-123`, calls `normalizeErrorEnvelope` |
| `listCompletedRuns` maps snake_case→camelCase | ✅ `agent_client_orchestrator.ts:197-204` |
| Mock server `GET /renders` vs `POST /renders` method branching | ✅ `fixture_client_mock_server.ts:180-187`, correct branching |
| Mock server `GET /renders/:id/output` returns `Content-Type: video/mp4` | ✅ `fixture_client_mock_server.ts:208-214` |
| `baseUrl` wired into `ClientRender` in container | ✅ `root_client_container.ts:32-35`, matches `ClientStream` pattern |
| `index.ts` re-exports new VOs | ✅ `index.ts:38-41`, `ListRunsItemResponse` at line 58 |
| Shell tsc fix legitimacy | ✅ `unit_client_hook.test.tsx:26` — `createElement(ClientProvider, {client, children})` is correct; passing `children` as a third positional arg to `createElement` with a component whose props type requires `children` is a known React type-system friction point. The fix is legitimate and unrelated to the PR scope. |
| No scope creep | ✅ No changes to `home/`, `studio/`, `queue/`, `gallery/`, `root_web_main_entry.ts`, or Python |
| No missing planned items | ✅ All files from the design-doc scope were modified |
| `inspectFull` test coverage | ✅ `unit_client_orchestrator.test.ts:673-700` |
| `downloadOutput` test coverage | ✅ `unit_client_orchestrator.test.ts:704-730` |
| `listCompletedRuns` test coverage | ✅ `unit_client_orchestrator.test.ts:732-759` |
| `getOutput` test coverage | ✅ `unit_client_render.test.ts:242-277` |
| Schema pin for `ListRunsItemResponse` | ✅ `contract_client_schema.test.ts:163-168` |

---

## Verdict

**Changes required before merge**: 2 bugs (Issues 1 and 2 — the `listCompletedRuns` wire-shape mismatch with the live API, masked by an equally-wrong mock), plus 2 suggestions (incomplete shell mock, protocol layering) and 3 nits.

The core implementation is clean: `getOutput` correctly bypasses the JSON transport with raw `fetch` + `response.blob()` and normalizes errors via `normalizeErrorEnvelope`. `inspectFull` correctly spreads `mapInspectResponse` and adds `layers`. `downloadOutput` returns the correct VO shape with a sensible default filename. `baseUrl` wiring matches the `ClientStream` pattern. The shell tsc fix is legitimate and in-scope as a gate requirement.

The blocking issue is the `listCompletedRuns` response shape: the live API returns `{items: [...]}` but the client expects a bare array. Both the capability and the mock server encode the wrong shape, so tests pass while production will fail at runtime. Fix both the capability (unwrap `RunListResponse.items`) and the mock server (return `{items: [...]}`) to match the OpenAPI spec.