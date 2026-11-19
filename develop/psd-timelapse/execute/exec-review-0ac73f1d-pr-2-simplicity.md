# Simplicity Review — pr-2 (`0ac73f1d-pr-2`)

## Summary

The PR extends the client contract with `inspectFull`, `downloadOutput`,
and `listCompletedRuns` across the protocol, aggregate, capability, and
orchestrator layers. Each method is the minimum needed to satisfy its
contract: `inspectFull` reuses `mapInspectResponse`, `downloadOutput` is a
three-line delegate-plus-wrap, `listCompletedRuns` is a one-line transport
call plus a four-line snake→camel mapper. The three new VOs
(`InspectFullVO`, `RenderDownloadVO`, `RenderCompletedVO`) and the
`ListRunsItemResponse` payload mirror existing naming conventions and add
no speculative fields. No over-engineering, no unnecessary abstractions,
no reinvented stdlib. No issues found.

## Issues

None.

## Items checked and confirmed appropriate

- **`getOutput` inline error handling does not reinvent
  `ClientTransport`** — `getOutput` must use raw `fetch` (binary body,
  not JSON), so it cannot go through `transport.get`. It correctly
  reuses the shared `normalizeErrorEnvelope` from
  `utility_client_parser.ts` for the non-OK branch, the same primitive
  `ClientTransport.request` and `ClientStream.consumeStream` use. The
  only duplicated lines are the 6-line `json = await response.json()
  catch → json = null` preamble, which appears at three sites total.
  At three sites a shared helper is borderline; lifting it would add an
  indirection that is not justified by this PR alone. Leaving the
  preamble inline is the simpler choice.

- **`RenderDeps.baseUrl` is not a speculative config flag** — Every
  prior `ClientRender` method delegated to `transport`, so `baseUrl` was
  unnecessary before. `getOutput` is the first method that needs raw
  `fetch`, which requires the base URL. Adding `baseUrl?: string`
  defaulting to `API_BASE_URL_DEFAULT` is the minimal change, and the
  container wiring (`root_client_container.ts:32-35`) passes
  `config.baseUrl` through identically to `ClientTransport` and
  `ClientStream`. No extra config layer.

- **Default filename `timelapse_${runId}.mp4` is a reasonable
  simplification, not over-engineering** — The protocol pins `getOutput`
  to return `Blob` only (no headers), so the orchestrator cannot read
  `Content-Disposition`. A deterministic default is the correct choice
  under that constraint; the inline comment at
  `agent_client_orchestrator.ts:186-187` documents the trade-off. If a
  future surface needs the real filename, the protocol signature must
  change to `{blob, filename}` — out of scope here.

- **`ListRunsItemResponse` (wire) vs `RenderCompletedVO` (domain) are
  field-isomorphic but the split is consistent with the codebase** —
  Every protocol method returns a wire payload; every aggregate method
  returns a domain VO. The mapper in
  `agent_client_orchestrator.ts:197-204` is pure snake→camel renaming,
  same shape as `mapRunHandleToHandle`, `mapOutputMetaToVO`, etc.
  Maintaining the layering boundary is the right call even when the two
  shapes happen to be isomorphic today.

- **`InspectFullVO` extension is minimal** —
  `interface InspectFullVO extends PsdDocumentInfoVO { readonly layers:
  readonly LayerPayload[] }` adds exactly one field. No duplication of
  summary fields, no speculative members.

- **`RenderDownloadVO` has no speculative fields** — `blob`, `filename`,
  `sizeBytes` are what a download consumer needs. `sizeBytes` is
  derivable from `blob.size` but kept as a convenience VO field,
  consistent with how other VOs expose derivable values.

- **Mock server `output` route and GET/POST branching on `/renders`** —
  The new `case "output"` is 8 lines of canned MP4 bytes. The GET
  branch on `case "renders"` is 5 lines of canned list items. Both are
  minimal fixtures for the new tests. The `Content-Disposition` header
  on the mock output is unused by production code (filename is defaulted
  in the orchestrator) but documents the real server's behavior —
  acceptable, not over-engineered.

- **The `packages/shell/tests/unit_client_hook.test.tsx` tsc fix adds no
  unnecessary changes** — One line: `children` moved from a third
  positional argument to a property of the props object passed to
  `createElement(ClientProvider, {...})`. This is the correct fix for a
  pre-existing tsc error (`ClientProviderProps.children` is required and
  the three-arg `createElement` form bypasses props type-checking). No
  surrounding code touched.

- **Tests are not bloated** — 16 new tests across four files. Each
  targets a distinct behavior (happy path, AbortSignal forwarding, error
  path, schema pin, snake→camel mapping). No padding, no redundant
  assertions. The `getOutput` 404 test stubs `globalThis.fetch` because
  the mock server always returns 200 for the output route — a pragmatic
  choice that covers the error path without forcing the mock server to
  support error injection.

- **No reinvented stdlib or new dependencies** — `fetch`, `Blob`,
  `AbortSignal`, `Buffer.from`, `encodeURIComponent` (via `formatRoute`)
  are all standard. No new npm dependencies, no manual URL/JSON parsing.

## Conclusion

The PR is appropriately simple. No deletions, refactors, or
simplifications recommended.