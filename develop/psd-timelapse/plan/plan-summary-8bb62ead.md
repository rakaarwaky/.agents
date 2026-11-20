# Plan Summary: Wire `packages/psd/` into StudioContainer

**Document:** `plan-doc-8bb62ead.md`
**Date:** 2026-11-20
**Status:** Draft

## Problem

`StudioContainer.handlePickFile()` sends the browser file name (e.g. `design.psd`) to the Python server via `POST /api/inspect`. The server checks `Path("design.psd").is_file()`, which fails because the file is only in the browser. The layers panel stays empty ("No PSD imported yet") and users must manually type a server path. `packages/psd/` (PR #301) was merged with `createPsdAggregate()` but explicitly not wired into StudioContainer.

## Proposed Solution

Two changes, three PRs:

1. **Client-side PSD preview/validate (no network):** StudioContainer imports `createPsdAggregate()` from `packages/psd/`, validates the picked/dropped file in the browser (`execute({operation: "validate", file})` + `parsePsdFile(file)`), and maps `PsdDocumentVO.layers` to `StudioLayerRow[]`. Layers appear instantly in the sidebar.

2. **Server upload only on Render:** A new `POST /api/upload` multipart endpoint saves the uploaded PSD to `workspace_dir/uploads/<uuid>.psd` and returns `{path}`. StudioContainer calls `uploadFile(client, selectedFile)` then `startRender(serverPath)` when the user clicks RENDER.

3. **Client upload capability (AES-compliant):** New `ClientUpload` capability, `IClientUploadProtocol`, `upload_file` orchestrator dispatch case, `ClientTransport` FormData branch. Mirrors `packages/client/` patterns exactly.

## Key Architectural Choices

- **`StudioContainer` gains an optional `psdAggregate` prop** (defaults to `createPsdAggregate()`). Only API change to the container; enables testability and future Web-Worker injection.
- **New `UploadController` class** in a new file `surface_api_upload_controller.py`, mirroring the existing `InspectController`/`OutputController` pattern. Registered in `ApiController.__init__`.
- **Uploads save to `workspace_dir/uploads/<uuid>.psd`** — reuses existing `ISystemConfigurationProtocol.load_config().workspace_dir`. Server-generated UUID prevents path traversal and filename collisions.
- **`ClientTransport.post()` FormData branch** — omits `Content-Type` when body is `FormData` (browser sets the multipart boundary). Backward-compatible with all existing JSON callers.
- **Render flow: upload-then-render when `selectedFile` is set; direct `startRender(serverPath)` when only `serverPath` is set.** Manual server-path inspect remains unchanged.
- **No changes to passive surfaces** (`packages/studio/src/`). The canvas and layer panel are already wired correctly.

## Files Modified (by PR)

- **PR 1 (Python upload endpoint):**
  - `modules/api/src/surface_api_upload_controller.py` (new)
  - `modules/api/src/surface_api_schema_view.py`
  - `modules/api/src/surface_api_controller.py`
  - `modules/api/tests/unit_api_upload.py` (new)

- **PR 2 (Client upload capability):**
  - `packages/shared/src/client/taxonomy_client_constant.ts`
  - `packages/shared/src/client/taxonomy_client_vo.ts`
  - `packages/shared/src/client/taxonomy_client_response.ts`
  - `packages/shared/src/client/contract_client_protocol.ts`
  - `packages/shared/src/client/contract_client_aggregate.ts`
  - `packages/shared/src/client/index.ts`
  - `packages/client/src/capabilities_client_upload.ts` (new)
  - `packages/client/src/capabilities_client_transport.ts`
  - `packages/client/src/agent_client_orchestrator.ts`
  - `packages/client/src/root_client_container.ts`
  - `packages/client/tests/unit_client_upload.test.ts` (new)
  - `packages/client/tests/contract_client_protocol.test.ts`

- **PR 3 (StudioContainer wiring + render flow):**
  - `packages/root_web_smart_container.ts`
  - `packages/root_web_main_entry.ts`
  - `packages/studio/tests/unit_studio_client_psd_wiring.test.tsx` (new)
  - `packages/studio/tests/unit_studio_render_wiring.test.tsx`
  - Documentation + OpenAPI updates

## Open Questions

None. All decisions resolved:
- Upload target: `workspace_dir/uploads/<uuid>.psd`
- Upload cleanup: deferred (v1)
- Upload auth: out of scope (local-profile API)
- Full-fidelity parse: out of scope (minimal parse already shipped in PR #301)
