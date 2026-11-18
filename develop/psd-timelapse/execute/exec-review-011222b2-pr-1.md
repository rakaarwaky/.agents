# Merged Review: pr-1 — Shared Client Contracts & Taxonomy

## [General]
### Issue 1 -- Severity: bug
- **File**: `packages/shared/src/client/taxonomy_client_constant.ts:16-23`
- **Description**: Route templates use `:runId` (camelCase) instead of `:run_id` (snake_case). In design doc §4.2, `formatRoute(template, replacements)` requires replacement keys to match colon placeholder names exactly (e.g. `ROUTE_RENDER_DETAIL = "/renders/:run_id"` requires key `"run_id"`, not `"runId"`). Calling `formatRoute(ROUTE_RENDER_DETAIL, { run_id })` will fail to replace the token and leave `:runId` unreplaced in the URL.
- **Suggestion**: Update all render route templates to use `:run_id`:
  ```typescript
  export const ROUTE_RENDER_DETAIL = "/renders/:run_id" as const;
  export const ROUTE_RENDER_PROGRESS = "/renders/:run_id/progress" as const;
  export const ROUTE_RENDER_CANCEL = "/renders/:run_id/cancel" as const;
  export const ROUTE_RENDER_RETRY = "/renders/:run_id/retry" as const;
  export const ROUTE_RENDER_EVENTS = "/renders/:run_id/events" as const;
  export const ROUTE_RENDER_VIEW = "/renders/:run_id/view" as const;
  export const ROUTE_OUTPUT = "/renders/:run_id/output" as const;
  export const ROUTE_OUTPUT_META = "/renders/:run_id/output/meta" as const;
  ```
- **Status**: fixed
- **Response**: Updated all 8 render route constants in `taxonomy_client_constant.ts` to use snake_case `:run_id`.

### Issue 2 -- Severity: bug
- **File**: `packages/shared/src/client/contract_client_protocol.ts` and `contract_client_aggregate.ts`
- **Description**: Subsystem protocols omit optional `signal?: AbortSignal` parameter on all async methods. Design doc §4.3 explicitly defines methods like `get<T>(path: string, signal?: AbortSignal): Promise<T>`. Without this, request cancellation via `AbortController` cannot propagate from React hooks in PR 4.
- **Suggestion**: Add `signal?: AbortSignal` to every method across all five protocol interfaces and `IClientAggregate`.
- **Status**: fixed
- **Response**: Added `signal?: AbortSignal` to every async method across `IClientTransportProtocol`, `IClientInspectProtocol`, `IClientRenderProtocol`, `IClientSystemProtocol`, and `IClientAggregate`.

### Issue 3 -- Severity: bug
- **File**: `packages/shared/src/client/contract_client_protocol.ts` and `contract_client_aggregate.ts`
- **Description**: `IClientStreamProtocol.subscribeEvents` omits `onState` and `onError` callbacks defined in §4.3. `IClientAggregate.watchProgress` omits `onStatus`, `onState`, `onComplete`, and `onError` handlers — currently only passes `onProgress` and `onTerminal`, which breaks PR 4's `useRenderProgress` hook lifecycle.
- **Suggestion**: Align stream and aggregate method signatures with design doc §4.3:
  - `IClientStreamProtocol.subscribeEvents(runId, onState, onProgress, onTerminal, onError): () => void`
  - `IClientAggregate.watchProgress(runId, onStatus, onState, onProgress, onComplete, onError): () => void`
- **Status**: fixed
- **Response**: Updated `subscribeEvents` and `watchProgress` signatures and their return types (`() => void`) to fully match design doc §4.3.

### Issue 4 -- Severity: suggestion
- **File**: `packages/shared/src/client/contract_client_aggregate.ts`
- **Description**: `IClientAggregate` methods return wire `*Payload` interfaces instead of domain Value Objects. Design doc §4.3 specifies concrete return types: `inspect` → `Promise<PsdDocumentInfoVO>`, `startRender` → `Promise<RenderExecutionHandle>`, `fetchResult` → `Promise<RenderOutputMetaVO>`, etc.
- **Suggestion**: Update all `IClientAggregate` method signatures to return the domain VOs specified in §4.3.
- **Status**: fixed
- **Response**: Updated `IClientAggregate` to return domain VOs (`PsdDocumentInfoVO`, `RenderExecutionHandle`, `ProgressSnapshotVO`, `RenderOutputMetaVO`, `SystemHealthVO`, `SystemConfigVO`, `boolean`) and exported `RenderExecutionHandle`.

### Issue 5 -- Severity: suggestion
- **File**: `packages/shared/src/client/utility_client_url.ts`
- **Description**: `buildApiUrl` signature is `(route, baseUrl?)` but design doc §4.2 specifies `(baseUrl, endpointTemplate, params?)` — accepting params and delegating to `formatRoute`. Callers must call `formatRoute` manually before `buildApiUrl`.
- **Suggestion**: Update to match §4.2: `buildApiUrl(baseUrl: string, endpointTemplate: string, params?: Record<string, string>): string`
- **Status**: fixed
- **Response**: Updated `buildApiUrl` signature and implementation to `(baseUrl: string, endpointTemplate: string, params?: Record<string, string>): string`, delegating route placeholder formatting to `formatRoute`.

### Issue 6 -- Severity: suggestion
- **File**: `packages/shared/src/client/utility_client_parser.ts`
- **Description**: `normalizeErrorEnvelope` returns `ApiErrorEnvelopePayload | null` instead of constructing an `ApiTransportError` instance. Design doc §4.2 specifies it should map status codes to retryability and return a typed error.
- **Suggestion**: Return `ApiTransportError` with retryability derived from HTTP status: 408/425/429/5xx → retryable=true; 400/404/422 → retryable=false; 409 → retryable only when code === "ACTIVE_JOB_CONFLICT".
- **Status**: fixed
- **Response**: Updated `normalizeErrorEnvelope` to construct and return an `ApiTransportError` with status code retryability heuristics per design doc §4.2.

### Issue 7 -- Severity: nit
- **File**: `packages/shared/src/client/taxonomy_client_error.ts`
- **Description**: `ClientError` does not extend native JavaScript `Error`. Design doc §4.1 shows `export class ClientError extends Error`.
- **Suggestion**: Change to `export class ClientError extends Error` with proper constructor forwarding.
- **Status**: fixed
- **Response**: Changed `ClientError` to `extend Error` with proper `super(message, cause !== undefined ? { cause } : undefined)` forwarding and prototype/name preservation across subclasses.

### Issue 8 -- Severity: nit
- **File**: `packages/shared/src/client/taxonomy_client_vo.ts`
- **Description**: `RenderOutputMetaVO.state` is typed as `PipelineStageVO`, but design doc §4.1 types it as `string`.
- **Suggestion**: Change `state` field to `string`.
- **Status**: fixed
- **Response**: Changed `RenderOutputMetaVO.state` from `PipelineStageVO` to `string`.

## [Tests]
### Issue 1 -- Severity: bug
- **File**: `utility_client_parser.ts`, `utility_client_url.ts`
- **Description**: Zero unit test coverage for both utility modules. `parseSseChunk` has an untested edge case where consecutive `data:` lines overwrite rather than concatenate. `formatRoute` and `appendQueryParams` lack boundary-condition testing.
- **Suggestion**: Add `packages/client/tests/unit_client_parser.test.ts` covering parseSseChunk (single data, multi-line data concat, comment lines, retry lines, malformed chunks), parseJsonSafely (valid objects/arrays/primitives, invalid/truncated syntax), and normalizeErrorEnvelope (valid envelopes, missing fields, non-object bodies). Add `packages/client/tests/unit_client_url.test.ts` covering buildApiUrl (trailing/leading slashes, empty route), formatRoute (param encoding, duplicate placeholders, unmapped placeholders), appendQueryParams (existing query params, empty params dict, percent-encoding).
- **Status**: fixed
- **Response**: Added `unit_client_parser.test.ts` (21 unit tests covering SSE parsing, JSON safe parsing, error envelope normalization) and `unit_client_url.test.ts` (14 unit tests covering URL composition, parameter encoding, duplicate token replacement, and query parameter appending).

### Issue 2 -- Severity: bug
- **File**: `packages/client/tests/contract_client_schema.test.ts`
- **Description**: Request payloads (`InspectInputRequest`, `StartRenderRequest`) are omitted from `SCHEMA_MAP`. OpenAPI fixture includes request models `InspectRequest` and `StartRenderRequest`, but they are never asserted against.
- **Suggestion**: Add request model entries to SCHEMA_MAP with exhaustive field records for compile-time parity.
- **Status**: fixed
- **Response**: Added `InspectRequest` and `StartRenderRequest` with exhaustive compile-time field records to `SCHEMA_MAP` in `contract_client_schema.test.ts`.

### Issue 3 -- Severity: bug
- **File**: `taxonomy_client_error.ts`
- **Description**: Error taxonomy hierarchy has 0% unit test coverage. Critical branching for `retryable` defaults (4xx vs 5xx, explicit override) is unverified.
- **Suggestion**: Add `packages/client/tests/unit_client_error.test.ts` asserting property defaults, error codes, prototype inheritance, and retryable status heuristics.
- **Status**: fixed
- **Response**: Added `unit_client_error.test.ts` with 12 tests verifying error inheritance from native Error, property defaults, status code heuristics, explicit retryable overrides, and cause chaining.

### Issue 4 -- Severity: suggestion
- **File**: `contract_client_schema.test.ts`
- **Description**: Schema test only checks top-level property presence, not nested types or nullability.
- **Suggestion**: Add type-checking assertions for nested structures (e.g. `LayerPayload.bounds` is `{x,y,width,height}`).
- **Status**: fixed
- **Response**: Added assertions verifying nested schema references and nullability in `contract_client_schema.test.ts` (`InspectLayerResponse.bounds`, `InspectResponse.layers`, `RunResultResponse.error`, `RunResultResponse.video_path`).

### Issue 5 -- Severity: suggestion
- **File**: `contract_client_schema.test.ts`
- **Description**: Schema loaded at module level outside test lifecycle. Missing fixture crashes entire test runner.
- **Suggestion**: Load schema inside `beforeAll()` hook for clean failure reporting.
- **Status**: fixed
- **Response**: Loaded schema within Vitest `beforeAll()` hook with fixture existence check for clean test failure reporting.

### Issue 6 -- Severity: nit
- **File**: `taxonomy_client_constant.ts`
- **Description**: Route constants not validated against OpenAPI paths.
- **Suggestion**: Add contract test converting `:param` to `{param}` and asserting 1:1 coverage with OpenAPI paths.
- **Status**: fixed
- **Response**: Added test in `contract_client_schema.test.ts` validating 1:1 bidirectional parity between converted client route constants (`:param` -> `{param}`) and live OpenAPI schema paths.

### Issue 7 -- Severity: nit
- **File**: `contract_client_protocol.ts`, `contract_client_aggregate.ts`
- **Description**: No mock conformance test for protocol implementations.
- **Suggestion**: Add a lightweight stub implementing all protocols to verify consumer readiness.
- **Status**: fixed
- **Response**: Added `packages/client/tests/contract_client_protocol.test.ts` implementing and exercising mock stubs for all 5 subsystem protocols and `IClientAggregate`.

## [Simplicity]
### Issue 1 -- Severity: suggestion
- **File**: `packages/shared/src/client/taxonomy_client_vo.ts`
- **Description**: Seven exported VOs (`RunIdVO`, `PsdDocumentInfoVO`, `LayerMetadataVO`, `SystemHealthVO`, `SystemConfigVO`, `RenderOutputMetaVO`, `LayerClassificationType`) have zero references outside their definition file and duplicate fields already carried by `*Payload` response interfaces.
- **Suggestion**: Defer adding these until a surface layer consumer needs them (PR 4+).
- **Status**: deferred

### Issue 2 -- Severity: suggestion
- **File**: `packages/shared/src/client/DATA.md`, `packages/shared/src/client/BACKLOG.md`
- **Description**: These duplicate existing `packages/shared/DATA.md` / `BACKLOG.md` which already declare DT-SHARED-001..005 for the same shapes.
- **Suggestion**: Consider extending the existing shared docs rather than creating a parallel DT-CLIENT track. Low priority — can stay as-is.
- **Status**: deferred

### Issue 3 -- Severity: suggestion
- **File**: `contract_client_aggregate.ts`, `contract_client_protocol.ts`
- **Description**: `IClientAggregate` re-declares method-for-method every operation in the five subsystem protocols. Neither interface has any implementer or consumer yet.
- **Suggestion**: Keep both as designed — aggregate provides the single facade surfaces consume; defer merging until PR 4 wiring.
- **Status**: deferred

### Issue 4 -- Severity: nit
- **File**: `utility_client_url.ts`
- **Description**: `appendQueryParams` hand-rolls URLSearchParams behavior; `buildApiUrl` hand-concats base + route strings instead of using `new URL()`.
- **Suggestion**: Consider using `new URL(route, base)` for buildApiUrl and `URLSearchParams` for appendQueryParams. Deferred to PR 2 if simpler.
- **Status**: deferred

### Issue 5 -- Severity: nit
- **File**: `taxonomy_client_error.ts`
- **Description**: Three subclasses forward near-identical option bags to `ClientError`; no consumer imports them yet.
- **Suggestion**: Keep for now; consumers arrive in PR 2 capabilities.
- **Status**: deferred

## Implementation Summary
- **Route Constants**: Updated 8 route constants in `packages/shared/src/client/taxonomy_client_constant.ts` to use snake_case `:run_id`.
- **Protocols & Aggregate**: Added `signal?: AbortSignal` to all async methods across `contract_client_protocol.ts` and `contract_client_aggregate.ts`. Updated `subscribeEvents` and `watchProgress` to match design doc §4.3 callback signatures and return unsubscribe handlers (`() => void`). Updated `IClientAggregate` methods to return domain VOs (`PsdDocumentInfoVO`, `RenderExecutionHandle`, `ProgressSnapshotVO`, `RenderOutputMetaVO`, `SystemHealthVO`, `SystemConfigVO`, `boolean`) and exported `RenderExecutionHandle`.
- **URL & Parser Utilities**: Updated `buildApiUrl` to `(baseUrl, endpointTemplate, params?)` delegating token formatting to `formatRoute`. Improved `parseSseChunk` to support multi-line `data:` concatenation, ignore comment and retry directives, and handle malformed chunks. Updated `normalizeErrorEnvelope` to construct `ApiTransportError` with retryability heuristics mapping HTTP status codes (408/425/429/5xx retryable, 400/404/422 non-retryable, 409 conditional on ACTIVE_JOB_CONFLICT).
- **Error Taxonomy & VOs**: Updated `ClientError` to extend native `Error` with `cause` forwarding and prototype inheritance. Changed `RenderOutputMetaVO.state` to `string`.
- **Test Suite**:
  - Added `packages/client/tests/unit_client_parser.test.ts` (21 tests).
  - Added `packages/client/tests/unit_client_url.test.ts` (14 tests).
  - Added `packages/client/tests/unit_client_error.test.ts` (12 tests).
  - Added `packages/client/tests/contract_client_protocol.test.ts` (2 tests).
  - Updated `packages/client/tests/contract_client_schema.test.ts` to include request payloads in `SCHEMA_MAP`, check nested schema types and nullability, load fixtures inside `beforeAll()`, and validate 1:1 route constant coverage against live OpenAPI paths.
