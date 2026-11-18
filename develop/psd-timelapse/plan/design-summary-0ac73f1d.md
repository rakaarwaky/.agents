# Summary: PSD Timelapse Client Integration Surface (design-doc-0ac73f1d)

**Scope.** Wire `packages/studio/`, `packages/queue/`, and `packages/gallery/` to the finished `packages/client/` transport (`IClientAggregate` + SSE `ClientStream` + FastAPI at `127.0.0.1:8000/api`), keeping every surface passive per AES201 row 13 / AES406, with all smart logic in the `root_web_main_entry.ts` containers.

**Key changes.**
- **Client capability extension (PR 2, additive):** `inspectFull` (returns `PsdDocumentInfoVO` + full `layers[]` instead of discarding `InspectResponsePayload.layers`), `downloadOutput(runId)` → `{ blob, filename, sizeBytes }` via raw `fetch` on the existing `GET /renders/:id/output` route, and `listCompletedRuns()` over a new `GET /api/renders` listing endpoint (PR 1, backend-only, maps from a new lightweight `ListRunsItemVO`, regenerates `fixtures/openapi.json` for the CI drift gate).
- **Studio (PR 3–4):** file pick/drag-drop → `inspectFull()` → real layer rows + dimensions + byte size replace `DEFAULT_LAYERS` and the hard-coded caption (mocks stay only as the no-client fallback); RENDER → `startRender()` (kills the 1.2s fake) → persist `runId` to `localStorage` → hash-navigate to `#queue`; orphaned `surface_studio_bottom_bar_component.tsx` removed (duplicated by the canvas footer).
- **Queue (PR 5):** `onDownload` → `downloadOutput` + `URL.createObjectURL`; completed list seeded from `listCompletedRuns()` instead of `localStorage`-only; `watchProgress` on-complete now persists a `CompletedItem`.
- **Gallery (PR 6):** new `GalleryContainer` replaces the `DEMO_GALLERY_*` demo constants: live `listCompletedRuns` → `GalleryItem[]`, playback modal with the real `<video>` (lazy object-URL, revoked on close), download via the same `downloadOutput` path.
- **Gate (PR 7):** `npm run typecheck`, `npm run build`, `npm test -- --run`, and `lint-arwaky-cli scan packages/` all green. No test-count guard is part of this design's validation surface (`ci.yml` runs vitest only; `packages/tests/count-guard.mjs` does not exist in the repo).

**Resolved Decisions.**
1. **Studio's server-visible PSD path** (blocking): Studio shows an editable text field pre-filled from `File.name`, explicitly labelled "absolute path on the server" with a tooltip explaining the path must exist on the machine running the Python API. Zero backend change; upload endpoint deferred.
2. **Quality/Resolution selectors**: Cosmetic passthrough for this milestone; the backend's locked `SystemConfigVO` is the source of truth.
3. **Bottom-bar stub**: Remove `surface_studio_bottom_bar_component.tsx` (orphaned; canvas's inline footer is the source of truth).
4. **List runs scan targets**: Scans `<output_dir>/*/log/<run_id>.jsonl` evidence records on disk for terminal records (`status` ∈ completed/failed/cancelled), maps to a new lightweight `ListRunsItemVO` (`run_id`, `state`, `input_path`, `duration_s`). `ISystemAggregate` is preserved (calls `AgentSystemOrchestrator.list_runs()` directly).

**Risks.** `Blob` in node-env vitest (mitigated: Node ≥18 global `Blob`, mock server serves `Buffer`); SSE stream loss on tab sleep (mitigated: opening-state re-emit in `surface_api_events_controller.py`); Gallery blob memory (mitigated: lazy, max 2 concurrent object-URLs).

**Output.** Full design at `design-doc-0ac73f1d.md` (same directory): 7 ordered PRs (5 levels, max parallelism 3), each listed with files affected, dependencies, and a one-line description.
