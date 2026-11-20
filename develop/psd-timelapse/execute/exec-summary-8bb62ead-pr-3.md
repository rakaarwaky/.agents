# Exec Summary — PR-3

- **Plan ID**: 8bb62ead
- **PR ID**: pr-3
- **Title**: Wire `packages/psd/` into StudioContainer + upload-on-render flow + StudioContainer `psdAggregate` prop + doc updates
- **Branch**: `execute-plan/8bb62ead-pr-3` (linearized stack tip, also on `execute-plan/8bb62ead-final`)
- **Commit**: `aef4d492587f4bf7c9881a228c10f786182fe08e`
- **Status**: Done

## What changed

### Smart container (`packages/root_web_smart_container.ts`)
- Imports `createPsdAggregate` (`./psd/src/root_psd_container.js`), `parsePsdFile` (`./shared/src/psd/utility_psd_parser.js`), `IPsdAggregate`, `PsdDocumentVO`, `LayerVO` (`./shared/src/psd/index.js`).
- New `StudioContainerProps` interface with optional `psdAggregate?: IPsdAggregate`.
- `StudioContainer` accepts props, `psdAggregate = useMemo(() => injectedPsd ?? createPsdAggregate(), [injectedPsd])`.
- New state `const [psdDoc, setPsdDoc] = useState<PsdDocumentVO | null>(null);`.
- `uploadFile(client, file)` helper calls `client.execute({operation: "upload_file", file})`, returns `{path: out.uploadPath?.value ?? ""}`.
- `handlePickFile` rewritten: `setSelectedFile(file)`, `setPsdDoc(null)`, `setInspectState({status:"loading"})`; calls `psdAggregate.execute({operation:"validate",file})`; on `!out.validation?.valid` → error state; else `parsePsdFile(file).then(doc => {setPsdDoc(doc); setInspectState({status:"ready"});})`; `.catch` → error. No longer calls `executeInspect`/`serverPath`.
- `handleRender` rewritten: if `selectedFile` → `uploadFile(client, selectedFile)` → `setServerPath(pathToRender)`; else `pathToRender = serverPath.trim()` and if empty, error `"Pick a PSD file or enter a server path before rendering"`. Then `startRender(client, pathToRender)`, `persistActiveRun(runId, pathToRender)`, `window.location.hash = "#queue"`.
- `layers` prefers `psdDoc.layers` mapped to `{id, label: name, visible, classification ?? ""}`.
- `fileMeta` prefers `psdDoc.sourceFile` for name/size, `psdDoc.width/height`, `psdDoc.layerCount`, falls back to `inspectState.doc` then `selectedFile`.
- Server-path label: `"absolute path on the server:"` → `"server path (optional, for manual inspect):"`, aria-label and tooltip updated.

### Tests
- `packages/studio/tests/unit_studio_client_psd_wiring.test.tsx` (NEW, 7 tests):
  1. Valid `.psd` shows layers without calling `inspect_full`.
  2. Non-PSD file shows "Unsupported file extension" error.
  3. Corrupt PSD (bad magic) shows "Invalid PSD format" error.
  4. `handleRender` with `selectedFile` calls `upload_file` then `start_render` with `/ws/uploads/mock-uuid.psd`.
  5. `handleRender` with `serverPath` only calls `start_render` directly.
  6. `handleRender` with neither shows `"Pick a PSD file or enter a server path before rendering"`.
  7. `handleReinspect` with `serverPath` still calls `inspect_full` (backward compat).
- `packages/studio/tests/unit_studio_render_wiring.test.tsx` (updated): test "reports an error and does not start a render when no file or server path is set" expects the new message.

### Documentation
- `packages/psd/FRD.md`: removed "future work" sentence about not being wired into StudioContainer; now describes the active integration.
- `packages/psd/BACKLOG.md`: state `In Progress` → `Done`; Progress Overview updated with PR-3 integration details.
- `packages/studio/BACKLOG.md`: Progress Overview updated with PR-3 wiring details (location, flow, test file).
- `modules/api/BACKLOG.md`: added `DS-API-010` row for `POST /api/upload`.
- `fixtures/openapi.json`: already has `/api/upload` from PR-1 (no regen needed).

## Verification

- `npx vitest run --config root_config_vite_entry.ts studio/tests/` — 61 tests passed (7 new + 18 render-wiring + 36 others).
- `npx vitest run --config root_config_vite_entry.ts` — full suite green (486 tests, 62 files).
- `npx tsc -p root_tsconfig_entry.json --noEmit` — zero new errors vs. PR-2 baseline. The 6 errors initially seen in the new test file (unused `ReactElement`, `IClientAggregate | null`, `.map`/`.find` callback arg types, `toEqual` overload mismatches) were all fixed before commit.
- `uv run ruff check modules/` — unchanged (PR-3 is TypeScript + docs only).
- `uv run ruff format --check modules/` — 4 pre-existing reformat needs (3 in `modules/api/tests/unit_api_upload.py` from PR-1, 1 each in `modules/shared/src/system/contract_system_protocol.py`, `modules/system/src/agent_system_orchestrator.py`, `modules/system/src/capabilities_system_logging.py`); none introduced by PR-3.

## Notes

- Studio surfaces (canvas, layer panel, landing) stay passive — no changes to `packages/studio/src/`.
- `StudioContainer` is the only smart container wired to the PSD aggregate.
- `validatePsdFile(File)` is async; `StudioContainer` handles it via `.then()`/`.catch()`.
- `PsdDocumentVO.layers` (LayerVO[]) maps to `StudioLayerRow[]` with `{id, label: name, visible, classification ?? ""}`.
- Existing manual `inspectFull(serverPath)` path is preserved as a fallback for users who type a valid server path.
- The `psdAggregate` prop makes `StudioContainer` testable without a real PSD parser.