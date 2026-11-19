# Simplicity Review: pr-2 — Strip sidebar to layers-only and update sidebar tests

Scope: over-engineering and unnecessary complexity only. Correctness, security, and test-coverage are out of scope.

---

severity: suggestion
File: packages/studio/src/surface_studio_layer_panel_component.tsx
Description: `StudioFileMeta` interface is defined in the layer panel component but is not used by `StudioLayerPanel` or `StudioLayerPanelProps`. After PR #2 stripped the upload/dropzone code from the layer panel, this file-metadata interface remains as an orphaned abstraction in the wrong module. `StudioCanvas` imports it from the layer panel (conceptually backwards — canvas does not depend on the layer panel), `StudioLanding` re-exports it, and `root_web_smart_container` imports it through landing — an unnecessary type-definition indirection chain. This is exactly the kind of unnecessary abstraction that can remain after removing upload/dropzone code.
Suggestion: Move `StudioFileMeta` to `surface_studio_canvas_component.tsx` (where it is actually consumed for the canvas chip), import it directly from there in `root_web_smart_container.ts`, and remove the `StudioFileMeta` re-export from `StudioLanding`.
Status: open

---

severity: nit
File: packages/studio/src/surface_studio_layer_panel_component.tsx
Description: The empty state message uses `&quot;` HTML entities instead of plain `"` characters in JSX (`No layers matching &quot;{searchQuery}&quot;`). JSX supports regular quotes, so the entities are unnecessary verbosity.
Suggestion: Replace `&quot;` with `"` in the empty state text.
Status: open

---

## Verified clean (no findings)

- `packages/studio/src/surface_studio_layer_panel_component.tsx` — imports (`useState`, `useEffect`, `JSX`, `ReactMouseEvent`) are all used; no leftover upload/dropzone imports (`useRef`, `DragEvent`, `ChangeEvent`, `fileInputRef`, `isDragging`, `handleDrop`, `processFile`, etc.); component is focused on layers only (header, count badge, search, rows, visibility toggle, select).
- `packages/studio/tests/unit_studio_layer_panel_component.test.tsx` — all imports used; no leftover `StudioFileMeta` import or `REAL_FILE_META`; all tests relevant to layers-only (real layer rows, DEFAULT_LAYERS fallback, onSelectLayer, visibility toggle, search filter, empty state).
- No dead code or unused imports found in either file.
- `surface_studio_canvas_component.tsx` retains all upload/dropzone code — correctly, since that responsibility lives in Canvas per PR #1; nothing was left behind in the layer panel.
- No orphaned files or leftover config in `packages/studio/`.