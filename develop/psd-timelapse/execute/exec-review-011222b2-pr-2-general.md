# Re-Review: pr-2 — Client Capabilities Implementation (Round 2)

**Scope**: Verify fixes for all 6 issues from `exec-review-011222b2-pr-2.md`, plus check for regressions.

---

## Fix Verification

### Issue 1 (bug) — SSE Stream Chunk Buffering — FIXED

- **File**: `packages/client/src/capabilities_client_stream.ts:125-128`
- **Description**: The unconditional `buffer = ""` has been replaced with boundary detection. After processing parsed frames, the code finds the last complete SSE event boundary via `/\r?\n\r?\n(?![\s\S]*\r?\n\r?\n)/` and retains trailing incomplete frame data for the next reader chunk.
- **Suggestion**: N/A (fix applied)
- **Status**: closed

### Issue 2 (bug) — AES403 Non-Canonical Banner Comments — FIXED

- **File**: All 5 capability files
  - `packages/client/src/capabilities_client_inspect.ts:16,22,40`
  - `packages/client/src/capabilities_client_render.ts:30,36,100`
  - `packages/client/src/capabilities_client_stream.ts:27,34,55`
  - `packages/client/src/capabilities_client_system.ts:19,25,36`
  - `packages/client/src/capabilities_client_transport.ts:17,23,40`
- **Description**: All five files now use canonical AES block headers: `// ─── Block 1: Module Declaration ───`, `// ─── Block 2: Module Contract ───`, `// ─── Block 3: Module Helpers ───`. `lint-arwaky-cli scan packages/client` reports 0 violations.
- **Suggestion**: N/A (fix applied)
- **Status**: closed

### Issue 3 (bug) — FRD AES609 Compliance — FIXED

- **File**: `packages/client/FRD.md:44,82,124,213,258`
- **Description**: All five non-streaming FR tables (FR-CLIENT-001, 002, 003, 005, 006) now include the `| Event | None |` row. No concrete source filenames appear anywhere in FRD.md (verified: grep for `.ts` returns zero matches in FRD). Source file references replaced with abstract seam descriptions.
- **Suggestion**: N/A (fix applied)
- **Status**: closed

### Issue 4 (suggestion) — Transport Abort Differentiation — FIXED

- **File**: `packages/client/src/capabilities_client_transport.ts:67-77`
- **Description**: The catch block now differentiates: (1) `callerSignal?.aborted` → `"Request cancelled by caller"`, (2) `err instanceof DOMException && err.name === "AbortError"` or `timeoutSignal.aborted` → `"Request timed out"`, (3) fallback → generic network error. Logic is correct and covers both caller abort and timeout scenarios.
- **Suggestion**: N/A (fix applied)
- **Status**: closed

### Issue 5 (suggestion) — FRD Concrete Filename References — FIXED

- **File**: `packages/client/FRD.md` (lines 11, 24, 273-277)
- **Description**: All concrete source filenames (`contract_client_protocol.ts`, `utility_client_parser.ts`, `capabilities_client_*.ts`) have been removed. The Public Interface tables now use abstract protocol names and seam responsibilities. Confirmed via grep: no `.ts` references remain in FRD.md.
- **Suggestion**: N/A (fix applied)
- **Status**: closed

### Issue 6 (nit) — FRD POST Without Body Edge Case — FIXED

- **File**: `packages/client/FRD.md:35`
- **Description**: Edge case statement now reads "POST without body → sends request without body payload", matching the actual transport behavior (`body: body !== undefined ? JSON.stringify(body) : undefined` at `capabilities_client_transport.ts:59`).
- **Suggestion**: N/A (fix applied)
- **Status**: closed

---

## Issues

### Issue N -- Severity: suggestion

- **File**: `packages/client/src/capabilities_client_transport.ts:239`
- **Description**: The timeout abort test only covers the `AbortError` path (no caller signal passed, so `callerSignal?.aborted` is false/undefined, `timeoutSignal.aborted` is true). The caller-cancellation path (`callerSignal?.aborted` is true → throws `"Request cancelled by caller"`) is not tested. A future regression in the abort differentiation logic would not be caught by existing tests.
- **Suggestion**: Add a test that passes an already-aborted `AbortSignal` to `transport.get()` or `transport.post()` and asserts `NetworkConnectionError` with message `"Request cancelled by caller"`.
- **Status**: open

---

## Summary

| Category | Original Issues | Fixed | New Issues | Verdict |
|----------|----------------|-------|------------|---------|
| Bugs | 3 | 3 | 0 | All fixed |
| Suggestions | 2 | 2 | 1 (test coverage) | All fixed |
| Nits | 1 | 1 | 0 | All fixed |
| **Total** | **6** | **6** | **1** | **PASS** |

**Verdict**: All 6 original issues correctly resolved. Lint passes (0 violations). All 117 client tests pass. No new bugs or regressions introduced. One non-blocking suggestion: add a test for the caller-signal abort path in transport to improve regression coverage.