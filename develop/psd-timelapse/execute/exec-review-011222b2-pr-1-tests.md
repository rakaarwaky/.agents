# Test Review: pr-1 — Shared Client Contracts & Taxonomy (Round 2)

**Reviewer:** Test Engineer
**Target Branch:** `execute-plan/011222b2-pr-1-shared-client-contracts-taxonomy`
**Date:** 2026-11-18

## Overview

This review assesses the test coverage and quality for PR 1 (`Shared Client Contracts & Taxonomy`). The review focuses on:
1. `unit_client_parser.test.ts` (coverage of `utility_client_parser.ts`)
2. `unit_client_url.test.ts` (coverage of `utility_client_url.ts`)
3. `unit_client_error.test.ts` (coverage of `taxonomy_client_error.ts`)
4. `contract_client_schema.test.ts` (coverage of request & response payloads, nested structures, nullability)
5. `contract_client_protocol.test.ts` (protocol interface conformance)
6. Assertion specificity across all new tests.

---

## Findings

### Issue 1 -- Severity: suggestion
- **File**: `/home/raka/orca/workspaces/psd-timelapse/011222b2-pr-1/packages/client/tests/contract_client_schema.test.ts:219-245`
- **Description**: While `InspectRequest` and `StartRenderRequest` were added to `SCHEMA_MAP` for field-name parity testing, `test("validates nested types and nullability constraints")` only checks `InspectLayerResponse`, `InspectResponse`, and `RunResultResponse`. It omits assertion of request payload schemas (e.g. verifying `StartRenderRequest.output_path` is optional/nullable via `anyOf: [{type: "string"}, {type: "null"}]` and `input_path` is required).
- **Suggestion**: Add assertions in `validates nested types and nullability constraints` verifying `StartRenderRequest.properties.output_path.anyOf` contains string and null types, and that `InspectRequest.required` and `StartRenderRequest.required` include `"input_path"`.
- **Status**: open

### Issue 2 -- Severity: suggestion
- **File**: `/home/raka/orca/workspaces/psd-timelapse/011222b2-pr-1/packages/client/tests/unit_client_parser.test.ts:16-79`
- **Description**: `parseSseChunk` tests do not test `\r\n` (CRLF) delimiters, which are common in HTTP/SSE chunk streams. The implementation explicitly uses `/\r?\n\r?\n/` and `/\r?\n/`, but tests only pass `\n\n` and `\n`. Additionally, field prefixes without a space after colon (e.g., `data:{"test":1}` or `event:done` vs `data: {"test":1}`) are supported by the implementation (`if (val.startsWith(" ")) val = val.slice(1);`), but are not exercised in the unit test.
- **Suggestion**: Add test cases for CRLF line endings (`\r\n\r\n`) and SSE fields without leading whitespace after the colon (`data:payload\n\n`) to verify delimiter parsing under real-world server variations.
- **Status**: open

### Issue 3 -- Severity: suggestion
- **File**: `/home/raka/orca/workspaces/psd-timelapse/011222b2-pr-1/packages/client/tests/contract_client_protocol.test.ts:227-279`
- **Description**: In `contract_client_protocol.test.ts`, several methods implemented on `MockRenderProtocol` (`getProgress`, `getResult`, `getView`, `getOutputMeta`, `cancelRender`, `retryRender`) and `MockClientAggregate` (`checkProgress`, `fetchResult`, `cancel`, `retry`, `probeHealth`, `loadConfig`) are defined but never invoked in the test assertions. While the mock definition verifies that the class satisfies TypeScript interface typing at compile-time, runtime invocations for those methods are omitted.
- **Suggestion**: Exercise each mock method invocation in the test to ensure all protocol and aggregate methods execute without runtime errors and return expected types.
- **Status**: open

### Issue 4 -- Severity: nit
- **File**: `/home/raka/orca/workspaces/psd-timelapse/011222b2-pr-1/packages/client/tests/unit_client_url.test.ts:32-35`
- **Description**: `buildApiUrl` tests cover empty string templates `""`, but do not test `undefined` or route templates that contain query parameters or fragments, nor relative base URLs (e.g. `"/api"`).
- **Suggestion**: Add a test verifying `buildApiUrl` with a relative base path (e.g., `buildApiUrl("/api", "/renders/:run_id", { run_id: "1" }) === "/api/renders/1"`).
- **Status**: open

### Issue 5 -- Severity: nit
- **File**: `/home/raka/orca/workspaces/psd-timelapse/011222b2-pr-1/packages/client/tests/unit_client_error.test.ts:47-103`
- **Description**: In `unit_client_error.test.ts`, the default `code` for `ApiTransportError` is not asserted (though status 404/400/500 constructors pass explicit code strings). Testing `new ApiTransportError("Msg", "CODE", 500)` checks `status` and `retryable`, but verifying default error name across all subclasses in single-assertion blocks improves test isolation.
- **Suggestion**: Add a test asserting `error.code` and `error.status` behavior when non-standard HTTP codes (e.g., 499, 599) are supplied to `ApiTransportError`.
- **Status**: open

---

## Assertion Quality & Coverage Assessment

1. **`unit_client_parser.test.ts`**:
   - **Quality**: High. Assertions are specific (`toEqual`, `toBe`, `toBeInstanceOf`) with exact payload matching rather than vague checks or "doesn't throw".
   - **Coverage**: Thoroughly covers `parseSseChunk` (single data, multi-line concat, comments, retry directives, empty/whitespace inputs, malformed lines), `parseJsonSafely` (primitives, objects, arrays, fallback behavior), and `normalizeErrorEnvelope` (status codes 408, 425, 429, 400, 404, 409 active/non-active conflict, 5xx, non-object payloads, missing fields).

2. **`unit_client_url.test.ts`**:
   - **Quality**: High. All 14 tests assert exact string outputs with `toBe`.
   - **Coverage**: Covers `buildApiUrl` (trailing slashes, missing slashes, static templates, parameter substitution), `formatRoute` (single/duplicate token replacement, URL encoding of spaces/slashes, unmapped tokens), and `appendQueryParams` (existing params with `&`, new with `?`, empty dict, undefined omission, percent-encoding).

3. **`unit_client_error.test.ts`**:
   - **Quality**: High. Tests verify prototype chains (`toBeInstanceOf(Error)`, `toBeInstanceOf(ClientError)`), property assignments, cause chaining, and status-based retryable defaults (4xx vs 5xx vs explicit overrides).

4. **`contract_client_schema.test.ts`**:
   - **Quality**: High. Uses compile-time `Record<keyof T, true>` maps for bidirectional parity. Includes `InspectRequest` and `StartRenderRequest`. Verifies nested schemas (`InspectLayerResponse.bounds`, `InspectResponse.layers`), nullability unions (`error`, `video_path`), and bidirectional route parity (`openApiPaths` vs converted client constants).

5. **`contract_client_protocol.test.ts`**:
   - **Quality**: Good compile-time validation. Runtime exercise covers key protocol and aggregate methods (`inspect`, `startRender`, `subscribeEvents`, `watchProgress`, `getHealth`). Minor gap is that not all defined mock helper methods are executed at runtime (see Issue 3).
