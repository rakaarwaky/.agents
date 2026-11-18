# Execution Summary: PR 1 - Shared Client Contracts & Taxonomy (Review Fixes)

**Branch:** `execute-plan/011222b2-pr-1-shared-client-contracts-taxonomy`
**Date:** 2026-11-18

## Review Issues Addressed

1. **Route Templates Snake Case**: Fixed all 8 route templates in `packages/shared/src/client/taxonomy_client_constant.ts` to use `:run_id` instead of `:runId`, matching design doc §4.2.
2. **Cancellation Signals**: Added optional `signal?: AbortSignal` across all async methods in all 5 protocol interfaces in `contract_client_protocol.ts` and `IClientAggregate` in `contract_client_aggregate.ts`.
3. **Stream Callback Signatures**: Aligned `IClientStreamProtocol.subscribeEvents` (`runId, onState, onProgress, onTerminal, onError`) and `IClientAggregate.watchProgress` (`runId, onStatus, onState, onProgress, onComplete, onError`) signatures and `() => void` unsubscribe returns with design doc §4.3.
4. **Aggregate Domain VO Returns**: Updated `IClientAggregate` methods to return domain Value Objects (`PsdDocumentInfoVO`, `RenderExecutionHandle`, `ProgressSnapshotVO`, `RenderOutputMetaVO`, `SystemHealthVO`, `SystemConfigVO`, `boolean`) and exported `RenderExecutionHandle`.
5. **URL Helper Signature**: Aligned `buildApiUrl` to `(baseUrl: string, endpointTemplate: string, params?: Record<string, string>): string` per design doc §4.2, delegating token replacements to `formatRoute`.
6. **Error Envelope Normalization**: Updated `normalizeErrorEnvelope` in `utility_client_parser.ts` to return typed `ApiTransportError` instances with status-code retryability heuristics (408/425/429/5xx retryable, 400/404/422 non-retryable, 409 retryable on ACTIVE_JOB_CONFLICT).
7. **Native Error Extension**: Updated `ClientError` in `taxonomy_client_error.ts` to extend native `Error` with `cause` forwarding and proper prototype inheritance.
8. **Render Output Meta VO State**: Changed `RenderOutputMetaVO.state` to `string` in `taxonomy_client_vo.ts`.
9. **Parser Unit Tests**: Added `packages/client/tests/unit_client_parser.test.ts` (21 tests covering `parseSseChunk` multi-line concatenation/comments/retry directives/malformed inputs, `parseJsonSafely`, and `normalizeErrorEnvelope`).
10. **URL Unit Tests**: Added `packages/client/tests/unit_client_url.test.ts` (14 tests covering `buildApiUrl`, `formatRoute` encoding/duplicate tokens/unmapped placeholders, and `appendQueryParams`).
11. **Error Taxonomy Tests**: Added `packages/client/tests/unit_client_error.test.ts` (12 tests verifying `ClientError`, `ApiTransportError`, `NetworkConnectionError`, `ServerStreamError`, retryable defaults, and error cause forwarding).
12. **Schema & Route Contract Tests**: Updated `packages/client/tests/contract_client_schema.test.ts` to include request payloads in `SCHEMA_MAP`, assert nested schema structures and nullability, load fixtures within `beforeAll()`, and validate 1:1 bidirectional coverage between route constants and OpenAPI paths.
13. **Protocol Conformance Test**: Added `packages/client/tests/contract_client_protocol.test.ts` (2 tests) exercising mock implementations of all 5 protocols and `IClientAggregate`.

## Deliverables Summary

- `packages/shared/src/client/taxonomy_client_constant.ts`
- `packages/shared/src/client/taxonomy_client_vo.ts`
- `packages/shared/src/client/taxonomy_client_error.ts`
- `packages/shared/src/client/utility_client_url.ts`
- `packages/shared/src/client/utility_client_parser.ts`
- `packages/shared/src/client/contract_client_protocol.ts`
- `packages/shared/src/client/contract_client_aggregate.ts`
- `packages/client/tests/contract_client_schema.test.ts`
- `packages/client/tests/contract_client_protocol.test.ts`
- `packages/client/tests/unit_client_parser.test.ts`
- `packages/client/tests/unit_client_url.test.ts`
- `packages/client/tests/unit_client_error.test.ts`

## Verification

- `cd packages && npm test -- --run`: All 31 test files passed (205/205 tests).
- `cd packages && npx tsc --project root_tsconfig_entry.json --noEmit`: Typecheck clean, zero diagnostics.
- `uv run python scripts/dump_openapi.py && git diff --exit-code fixtures/openapi.json`: Zero schema drift detected.
