# PR 2 / 7 — Merged Review (general + tests + simplicity)

Branch: `rakaarwaky/0ac73f1d-pr-2`
Commits: `63844d4a` (implementer) + `c3a07d88` (review fixes)

## Reviewer verdicts

- **General**: 2 bugs, 2 suggestions, 3 nits — changes required before merge.
- **Tests**: 6 suggestions, 4 nits — no blocking bugs.
- **Simplicity**: 0 issues — explicitly approved.

## Bugs fixed

1. **Wire-shape mismatch (general Issue 1 + 2, critical)**: `listCompletedRuns` expected a bare `ListRunsItemResponse[]` but the live FastAPI `GET /api/renders` returns `RunListResponse({items: [...]})`. Both the capability and the mock server encoded the wrong shape, masking the bug in tests. **Fix**: `ClientRender.listCompletedRuns` now unwraps `.items`; mock server returns `{items: [...]}`; integration test exercises the live route.
2. **Shell mockClient incomplete (general Issue 3)**: `mockClient` was missing `inspectFull`, `downloadOutput`, `listCompletedRuns`. **Fix**: added all three to `unit_client_hook.test.tsx`.

## Suggestions addressed

- **`getOutput` error test too loose (tests S1)**: now asserts `ApiTransportError` type, `status === 404`, `retryable === false`; added 409 `ACTIVE_JOB_CONFLICT` `retryable === true` case.
- **`listCompletedRuns` live-server exercise (tests S2)**: added integration test against `createMockServer()` `GET /renders` route asserting both canned items.
- **`downloadOutput` error propagation (tests S3)**: added rejection-propagation test asserting `ApiTransportError` passes through unwrapped.
- **`inspectFull` full layer payload (tests S4)**: strengthened to assert full `LayerPayload` object (bounds/classification/reveal_style/visible), not just `.name`.
- **`getOutput` signal forwarding (tests S5)**: added symmetric AbortSignal forwarding test.
- **`duration_s: null` mapping (tests S6)**: added test asserting `null` maps to `null` (not `0`).
- **Conformance test too loose (tests S7/S8)**: strengthened to pin `inspectFull` scalar fields and `downloadOutput` `sizeBytes`.
- **Inline `import(...)` type (general Issue 6)**: replaced with imported `ListRunsItemResponse`.
- **Missing trailing newline (general Issue 7)**: added to `unit_client_orchestrator.test.ts`.
- **Content-Disposition dead data (tests S6 nit)**: added comment noting the header is intentionally unused by `getOutput`.

## Nits accepted as-is

- **Protocol layering (general Issue 4)**: `listCompletedRuns` unwraps `RunListResponse` in the capability layer, consistent with how other capabilities return inner payloads. The protocol return type `readonly ListRunsItemResponse[]` is correct. No change needed.
- **Import reorder (general Issue 5)**: cosmetic, acceptable.
- **Protocol test mocks (tests S8)**: new methods declared but not invoked in `contract_client_protocol.test.ts`; covered by conformance test. No change needed.
- **Content-Disposition (tests S6)**: header unused, documented. No change needed.

## Verification

```
npm run typecheck   # exit 0
npm test -- --run   # 40 files, 312 tests pass
```

## Verdict

**0 open issues. Changes approved for merge.**