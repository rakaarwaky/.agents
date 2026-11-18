# Code Review Notes: PR 1 - Shared Client Contracts & Taxonomy (Round 2 Re-Review)

**Document:** `exec-review-011222b2-pr-1-general.md`  
**Review Type:** Re-Review after Fixes (Correctness, Previous Issue Verification, New Bug Detection)  
**Branch:** `execute-plan/011222b2-pr-1-shared-client-contracts-taxonomy` (`b4b74770`)  
**Verdict:** Pass (All 8 prior review issues resolved correctly; zero new bugs or regressions identified)

---

## Executive Summary

A comprehensive re-review was conducted on the changes addressing feedback from the initial review of PR 1 (`b4b74770`). All 8 previously identified general issues have been resolved cleanly and accurately in accordance with the design specification:

1. **Route Templates Snake Case**: All 8 render route templates in `packages/shared/src/client/taxonomy_client_constant.ts` now consistently use `:run_id` instead of `:runId`, ensuring seamless parameter replacement via `formatRoute`.
2. **Cancellation Signals**: The optional parameter `signal?: AbortSignal` is now present on all async methods across `IClientTransportProtocol`, `IClientInspectProtocol`, `IClientRenderProtocol`, `IClientSystemProtocol`, and `IClientAggregate`.
3. **Stream Callback Signatures**: Callback signatures in `IClientStreamProtocol.subscribeEvents` (`runId, onState, onProgress, onTerminal, onError`) and `IClientAggregate.watchProgress` (`runId, onStatus, onState, onProgress, onComplete, onError`) now align with design doc §4.3 and return standard `() => void` unsubscribe functions.
4. **Aggregate Domain VO Returns**: `IClientAggregate` methods now return domain Value Objects (`PsdDocumentInfoVO`, `RenderExecutionHandle`, `ProgressSnapshotVO`, `RenderOutputMetaVO`, `SystemHealthVO`, `SystemConfigVO`, `boolean`), and `RenderExecutionHandle` is exported.
5. **URL Helper Signature**: `buildApiUrl` has been updated to `(baseUrl: string, endpointTemplate: string, params?: Record<string, string>): string`, delegating route placeholder formatting to `formatRoute`.
6. **Error Envelope Normalization**: `normalizeErrorEnvelope` in `utility_client_parser.ts` returns typed `ApiTransportError` instances with status-code retryability heuristics (408/425/429/5xx retryable, 400/404/422 non-retryable, 409 retryable on ACTIVE_JOB_CONFLICT).
7. **Native Error Extension**: `ClientError` extends JavaScript native `Error` with cause forwarding and prototype inheritance.
8. **Render Output Meta VO State**: `RenderOutputMetaVO.state` is typed as `string`.

In addition, the accompanying test suites (`contract_client_schema.test.ts`, `contract_client_protocol.test.ts`, `unit_client_parser.test.ts`, `unit_client_url.test.ts`, `unit_client_error.test.ts`) provide full coverage without regressions. All 31 test files (205 tests) and TypeScript typechecks pass cleanly with zero diagnostics.

No new bugs, security concerns, or architectural regressions were introduced.

---

## Issues

*(No open issues found)*
