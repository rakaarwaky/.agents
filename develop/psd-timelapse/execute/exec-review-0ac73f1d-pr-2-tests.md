# Test Review — PR 2 (Extend client contract with `inspectFull`, `downloadOutput`, `listCompletedRuns`)

Scope: new/changed test files plus the production code they exercise. Focus on coverage adequacy, assertion specificity, error/edge paths, mock-server route usage, and the shell tsc fix. General style/naming/architecture excluded.

## Verdict

Coverage is **mostly adequate** — happy paths and field mappings are pinned with concrete value assertions, AbortSignal forwarding is consistently checked, and the mock server's new routes (`GET /renders`, `/renders/:run_id/output`) are genuinely exercised. However, several non-OK / edge error paths for the three new methods are untested, the `getOutput` error test asserts too loosely, and a couple of behavior-mapping branches (`top_level_count`, `summary.top_level_count`) are uncovered. Findings below are all suggestions/nits — no blocking bugs.

## Issues

- **severity: suggestion**
  **File:** `packages/client/tests/unit_client_render.test.ts` (the `getOutput` "throws on non-ok response" test)
  **Description:** The error-path test only asserts `caught instanceof Error`. It does not verify the error is an `ApiTransportError`, nor that `status === 404` (or `retryable === false`) is propagated. A regression that threw a bare `Error`, or that dropped the status code, would still pass this test. The test also stubs `globalThis.fetch` to return a bodyless 404, so the `normalizeErrorEnvelope` JSON-parse branch and the `ACTIVE_JOB_CONFLICT`/retryable derivation are never observed through `getOutput`.
  **Suggestion:** Assert the concrete type and fields, e.g.:
  ```ts
  expect(caught).toBeInstanceOf(ApiTransportError);
  expect((caught as ApiTransportError).status).toBe(404);
  expect((caught as ApiTransportError).retryable).toBe(false);
  ```
  Also add a 409 case returning `{ error: { code: "ACTIVE_JOB_CONFLICT", message: "..." } }` and assert `retryable === true`, since the review explicitly calls out 404/409 coverage and this is the only place that error-normalization path is wired into `getOutput`.

- **severity: suggestion**
  **File:** `packages/client/tests/unit_client_render.test.ts` (`listCompletedRuns` describe block)
  **Description:** `listCompletedRuns` success is only tested by mocking the transport, and the mock returns the exact array that is then asserted — so the test proves the transport was called and its value passed through, but not the real `GET /renders` route. No test exercises the live mock-server `case "renders"` GET branch (which returns the two canned items), and there is no error-path test for `listCompletedRuns` (non-ok response → `ApiTransportError`). The task specifically asks whether error paths and the new server routes are exercised.
  **Suggestion:** Add an integration-style test that points `ClientRender` at `createMockServer()`'s `baseUrl` and calls `listCompletedRuns()`, asserting the two canned items (`run-completed-1` / `run-failed-1`, states, `input_path`, `duration_s`). Add one non-ok test (stub `transport.get` to reject, or stub fetch to 500) and assert `ApiTransportError` with the right `status`.

- **severity: suggestion**
  **File:** `packages/client/tests/unit_client_orchestrator.test.ts` (`downloadOutput` describe block)
  **Description:** `downloadOutput` has only happy-path + signal-forwarding tests. There is no test that `render.getOutput` rejecting propagates the error (and does not wrap it), and no test that a non-mp4 Blob type or zero-size Blob still maps `sizeBytes` correctly. The filename default is asserted for one runId (`timelapse_run-1.mp4`); a second runId would guard against an accidental template swap, but this is minor.
  **Suggestion:** Add a rejection-propagation test:
  ```ts
  render.getOutput.mockRejectedValueOnce(new ApiTransportError("not found", "RUN_NOT_FOUND", 404, false));
  await expect(orch.downloadOutput("missing")).rejects.toBeInstanceOf(ApiTransportError);
  ```
  Optionally assert the filename for a runId containing a path-like value to confirm it is interpolated verbatim.

- **severity: suggestion**
  **File:** `packages/client/tests/unit_client_orchestrator.test.ts` (`inspectFull` describe block)
  **Description:** `inspectFull` is tested with a fixture whose `summary` has `width`/`height` but no `top_level_count`, so the `mapInspectResponse` branch that reads `summary.top_level_count` is never exercised through `inspectFull`. `result.layers[0]!.name` is checked but the full layer payload shape (bounds/classification/reveal_style/visible) is not asserted, so a regression that aliased layers to the wrong field or dropped a subfield would pass.
  **Suggestion:** Add a case where `summary.top_level_count` is present and assert it flows through (e.g. `top_level_count` differs from `layer_count`), and assert `result.layers[0]` deep-equals the full `LayerPayload` object rather than just `.name`.

- **severity: nit**
  **File:** `packages/client/tests/unit_client_render.test.ts` (`getOutput` success test)
  **Description:** Neither `getOutput` test asserts that the `AbortSignal` is forwarded into the underlying `fetch` call. The success test omits the signal entirely and the error test uses a real `AbortController` but never asserts `fetch` received it. Every other capability test in this file has a symmetric "forwards AbortSignal" case; `getOutput` is the one that lacks it.
  **Suggestion:** Add:
  ```ts
  it("forwards AbortSignal to fetch", async () => {
    const controller = new AbortController();
    const fetchSpy = vi.fn().mockResolvedValue(new Blob(["x"]));
    globalThis.fetch = fetchSpy as typeof fetch;
    try {
      const render = new ClientRender({ transport: createMockTransport(), baseUrl: "http://127.0.0.1:1/api" });
      await render.getOutput("run-1", controller.signal);
      expect(fetchSpy.mock.calls[0]![1]!.signal).toBe(controller.signal);
    } finally {
      delete globalThis.fetch; // restore
    }
  });
  ```

- **severity: suggestion**
  **File:** `packages/client/tests/unit_client_orchestrator.test.ts` (`listCompletedRuns` describe block)
  **Description:** Mapping is asserted with `toEqual` against the full expected VO array (good, exact values). However there is no test for the `duration_s: null` case, even though `ListRunsItemResponse.duration_s` and `RenderCompletedVO.durationSeconds` are both `number | null`. The null-mapping branch is a plausible regression site (e.g. `?? 0` vs `=== null ? null : ...`).
  **Suggestion:** Add a case with `duration_s: null` and assert `result[0]!.durationSeconds` is `null` (not `0` or `undefined`).

- **severity: nit**
  **File:** `packages/client/tests/unit_client_render.test.ts` (`getOutput` success test)
  **Description:** The success test spins up the real mock server (good — this is the only test that exercises the `case "output"` route and its `Content-Disposition`/`Content-Type: video/mp4` headers), but it does not assert the `Content-Type` that comes back. The test asserts `blob.type === "video/mp4"`, which does cover the server's header indirectly. The `Content-Disposition: attachment; filename="test.mp4"` header is set on the server but is never asserted anywhere — it is declared but unused (the design doc intentionally ignores it, so this is acceptable, but worth noting it is dead data today).
  **Suggestion:** No change required; if future work ever reads `Content-Disposition`, add an assertion then. Consider a brief comment in the fixture noting the header is intentionally unused by `getOutput`.

- **severity: nit**
  **File:** `packages/client/tests/contract_client_conformance.test.ts` (`IClientAggregate — all 12 methods` test)
  **Description:** The `inspectFull` assertion is `expect((await agg.inspectFull("/test.psd")).layers).toEqual([])` — it only checks the `layers` field and uses an empty array, so the conformance test does not pin the `InspectFullVO` scalar fields (`has_layers`, `width`, `height`, `layer_count`, `top_level_count`). `downloadOutput` is only checked for `filename`.
  **Suggestion:** Strengthen to assert the scalar fields and `sizeBytes`, e.g. `const dl = await agg.downloadOutput("run-1"); expect(dl.sizeBytes).toBe(15);` and assert `inspectFull` returns `has_layers: true` etc. This is a contract test, so tighter pinning matches its intent.

- **severity: nit**
  **File:** `packages/client/tests/contract_client_protocol.test.ts`
  **Description:** The mock protocols/aggregate were extended with the three new methods, but the file's two `it` blocks only exercise `inspect`, `startRender`, `watchProgress`, `getHealth` on the real instances — the new `getOutput`/`listCompletedRuns`/`inspectFull`/`downloadOutput` methods on `MockRenderProtocol`/`MockClientAggregate` are declared but never invoked in this file (they are invoked in `contract_client_conformance.test.ts`). Not a coverage gap at the suite level, but the file's mocks carry dead code relative to its own tests.
  **Suggestion:** Either invoke the new methods here too (one line each) or leave as-is; the conformance test covers them. Nit only.

- **severity: nit**
  **File:** `packages/shell/tests/unit_client_hook.test.tsx`
  **Description:** The pre-existing tsc fix (moving `children` into the `ClientProvider` props object) is a compile-only change; the file's runtime tests (`useOptionalClient`, `useRenderProgress` idle/absent paths) already exercise `Harness` → `ClientProvider` → `useOptionalClient`, so the fix is indirectly covered by the existing two passing tests (`status=has-client` requires `ClientProvider` to render its children). No new test is needed for the tsc fix itself, and none was added — this is acceptable.
  **Suggestion:** No change required.

## Areas that are well-covered (no action)

- `inspectFull` success: asserts `has_layers`, `width`, `height`, `layer_count`, `top_level_count`, `layers` length, and first layer name — concrete values, not just types. Signal forwarding asserted.
- `downloadOutput` success: asserts exact `filename` (`timelapse_run-1.mp4`), `sizeBytes === blob.size`, and `blob` identity. Signal forwarding asserted.
- `listCompletedRuns` mapping: uses `toEqual` with full expected objects (`runId`/`state`/`inputPath`/`durationSeconds` exact values including `12.5`/`3.0`) — strong.
- `getOutput` success: real mock server, asserts `instanceof Blob`, `type === "video/mp4"`, `size === "fake-mp4-bytes".length`. This is the **only** test that exercises the live `case "output"` route (and its `Content-Type`/`Content-Disposition` headers) against the mock server.
- Mock server new routes — partial exercise:
  - `case "output"` (`/renders/:run_id/output`): **exercised** by the `getOutput` success test above.
  - `case "renders"` GET branch (`/renders` → two canned items): **not exercised** by any live-server test. `listCompletedRuns` is unit-tested only via a mocked `IClientTransportProtocol` (which bypasses `parsePath`/the route handler entirely), and `integration_client_flow.test.ts` never calls `listCompletedRuns`/`downloadOutput`/`getOutput`/`inspectFull`. So the GET-vs-POST `req.method` branch and the GET response shape are dead server code relative to the test suite. See the `listCompletedRuns` suggestion above for a concrete live-server test.
- OpenAPI schema pin for `ListRunsItemResponse`: 4/4 fields pinned via `Record<keyof ListRunsItemResponse, true>` + `SCHEMA_MAP` entry — exact and compile-time exhaustive.
- The schema test's `ALL_CLIENT_ROUTES` now includes `ROUTE_OUTPUT` and `ROUTE_RENDERS`, and the 1:1 OpenAPI-paths assertion still passes (confirmed against `fixtures/openapi.json`: both `/api/renders` and `/api/renders/{run_id}/output` are present). Good.
- AbortSignal forwarding: asserted for `listCompletedRuns` (capability + orchestrator), `downloadOutput`, and `inspectFull`. The `getOutput` success test does **not** assert signal forwarding (it calls `render.getOutput("run-1")` with no signal); add a symmetric signal-forwarding assertion for `getOutput` for completeness (the stubbed-fetch error test passes a real controller but doesn't assert `fetch` received the signal).