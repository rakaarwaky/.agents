# Test Review: pr-2 Client Capabilities Implementation (round 2)

## Scope

Focused review of whether new tests were added for the two fixed bugs:
1. SSE stream chunk buffering edge case (last-frame boundary detection, retaining trailing incomplete frame bytes).
2. Transport abort differentiation (caller cancellation vs timeout).

Assertions checked for specificity. General code style and architecture are out of scope.

---

## [Tests]

### Issue 1 — Severity: bug
- **File**: `packages/client/tests/unit_client_stream.test.ts`
- **Description**: The stream buffering fix in `capabilities_client_stream.ts` (retain trailing incomplete frame data after the last `\r?\n\r?\n` boundary for the next read cycle) has no test covering a partial SSE frame split across two `reader.read()` chunks. Every existing stream test feeds complete `\n\n`-terminated frames in a single chunk via `sseResponse()`. There is no test that exercises `reader.read()` returning an unterminated partial frame followed by a second chunk completing it, nor any assertion that trailing bytes are retained in `buffer` across reads.
- **Suggestion**: Add a test where the mocked stream yields chunk 1 containing a truncated frame (e.g. `event: state\ndata: {"stage":"validating","run_id":"run-1","term` with no `\n\n` terminator) and chunk 2 containing the remainder (`inal":false}\n\n`) plus a complete terminal frame. Assert `onState` is called once with the reassembled frame and `onTerminal` is called, proving the buffer retention across chunk boundaries works.
- **Status**: open

### Issue 2 — Severity: bug
- **File**: `packages/client/tests/unit_client_transport.test.ts`
- **Description**: The abort differentiation fix in `capabilities_client_transport.ts` checks `callerSignal?.aborted` to throw `NetworkConnectionError("Request cancelled by caller", err)` versus `timeoutSignal.aborted`/`AbortError` to throw `NetworkConnectionError("Request timed out", err)`. The existing "timeout abort" test only covers the `AbortError` → "Request timed out" path. There is no test for the caller-abort path, and no test asserting that the two paths produce distinct messages when both signals are composed via `AbortSignal.any([callerSignal, timeoutSignal])`.
- **Suggestion**: Add a test where `callerSignal.abort()` is invoked and `fetch` rejects with an `AbortError`, asserting the caught error is a `NetworkConnectionError` with message `"Request cancelled by caller"` and `retryable === true`. Keep the existing timeout test and add an explicit assertion that its message is `"Request timed out"` (not the caller-cancel message), ensuring the two branches are discriminated.
- **Status**: open

### Issue 3 — Severity: suggestion
- **File**: `packages/client/tests/unit_client_stream.test.ts`
- **Description**: Existing assertions on SSE dispatch are specific (`toHaveBeenCalledWith` with exact payloads, `toBeInstanceOf`, exact `status`/`retryable` values). However, the "stream closes without terminal event" test asserts `err.message` equals the literal `"Stream closed without terminal event"` — this couples the test to an implementation string rather than the error type/code. It is specific, but brittle if the message wording changes.
- **Suggestion**: Keep the message assertion but add `expect(err).toBeInstanceOf(ServerStreamError)` and `expect(err.retryable).toBe(true)` so the test relies on type and behavioral contract, not only the literal message string.
- **Status**: open

### Issue 4 — Severity: nit
- **File**: `packages/client/tests/unit_client_transport.test.ts`
- **Description**: The "throws ApiTransportError with retryable=false for 400" test calls `transport.get("/inspect")` twice (once inside `await expect(...).rejects.toThrow`, once in a try/catch whose result is discarded) before re-mocking and asserting. The first call is wasteful and its mock is never asserted on; the second `mockResolvedValueOnce` consumes the second call. The assertion on `err.status`/`err.retryable` is specific, but the test structure obscures what is being verified.
- **Suggestion**: Simplify to a single `fetchMock.mockResolvedValueOnce(...)` followed by one `await transport.get(...).catch(...)` and assert `err.status === 400`, `err.retryable === false`, `err.code === "VALIDATION_FAILED"`.
- **Status**: open

---

## Summary

No new tests were added for either of the two fixed bugs (stream buffering edge case and abort differentiation). Both gaps were flagged as deferred coverage items in the previous merged review (`exec-review-011222b2-pr-2.md`, [Tests] section) and remain open. Existing assertions are largely specific, but the stream "closed without terminal" test and the transport 400 test could be tightened as noted above.

All 36 test files / 258 tests pass and `lint-arwaky-cli scan packages/client` reports 0 violations per the implementation summary, but test coverage for the two bug fixes is absent.