# Simplicity Review — pr-1 (canvas upload button, empty-state dropzone, re-wire StudioLanding)

Reviewer lane: over-engineering and unnecessary complexity only. Correctness bugs, security, test coverage, language-specific lint, and ownership issues are out of scope.

Commit under review: `21a6b7b6` (`feat: add canvas upload button, empty-state dropzone, and re-wire StudioLanding`).

---

## Findings

### 1. `StudioLayerPanel` upload/drop/re-inspect code is now dead in production (one real caller, no longer passes the props)

- Severity: suggestion
- File: `packages/studio/src/surface_studio_layer_panel_component.tsx`
- Lines: `29-44` (`StudioFileMeta`, `onPickFile`, `onReinspect` props), `66-70` (`hiddenLayerIds` still used, but the file-pick machinery below is not), `88` (`fileInputRef`), `131-153` (`processFile`, `handleDrop`, `handleFileInputChange`, `handleReset`), `162-170` (hidden file input), `206-235` (`.pt-studio-sidebar-dropzone` click/keyboard/drop target), `176-184` (refresh button calls `handleReset` → `onReinspect`)
- Description: This PR re-wires `StudioLanding` so `onPickFile`, `onReinspect`, and `fileMeta` are passed to `StudioCanvas` and **not** to `StudioLayerPanel` (`surface_studio_landing_component.tsx:73-76` now passes only `layers` and `onSelectLayer`). The only production caller of `StudioLayerPanel` is `StudioLanding`; nothing else renders the panel. After this change the panel's `onPickFile`/`onReinspect`/`fileMeta` props are never supplied by any production code path, so the following are now unreachable in production and exercised only by the panel's own unit tests:
  - the hidden `<input type="file" data-testid="studio-file-input">` and its `handleFileInputChange`
  - the `.pt-studio-sidebar-dropzone` clickable/droppable/keyboard target and `handleDrop`
  - `processFile`
  - `handleReset` (the refresh button still calls it, but `onReinspect?.()` is a no-op and the local `setHiddenIds`/`setActiveLayerId` resets are redundant with the `useEffect` at `90-94`)
  - the `fileMeta` prop and `DEFAULT_FILE_META` fallback for the file card (`metaLine`, `meta.name`)
- Suggestion: YAGNI / delete. Now that upload and re-inspect live on `StudioCanvas`, drop the dead upload/drop/re-inspect machinery from `StudioLayerPanel` (the hidden file input, `onPickFile`/`onReinspect` props, `handleDrop`/`handleFileInputChange`/`processFile`, the `.pt-studio-sidebar-dropzone` target, and the `handleReset` reset logic) and reduce the panel to its remaining real responsibility: render `layers` + `onSelectLayer` with the file-name card driven by the still-passed `fileMeta`/`layers` props. This also removes the duplicated dropzone (see finding 3) and the orphaned `studio-file-input` testid. If the panel is intentionally kept as a self-contained widget, gate the dead branches behind a prop so they are not dead-by-default, but the simpler move is to delete them.

### 2. `StudioLayerPanelProps` still declares `onPickFile` / `onReinspect` with no production caller

- Severity: suggestion
- File: `packages/studio/src/surface_studio_layer_panel_component.tsx`
- Lines: `39-42` (interface), `74-77` (destructure)
- Description: The interface advertises `onPickFile` and `onReinspect` as first-class props, but the only production call site (`StudioLanding`) no longer passes them. They survive solely because the panel's own unit tests construct the component directly with them (`unit_studio_layer_panel_component.test.tsx:88-133`). Keeping public props alive for a single test caller is the speculative-surface form of dead code. This is the interface half of finding 1.
- Suggestion: Remove `onPickFile` / `onReinspect` from `StudioLayerPanelProps` and the destructure when the corresponding handlers are removed (finding 1), and update the panel unit tests to assert only the surviving `layers`/`fileMeta`/`onSelectLayer` behavior.

### 3. Empty-state dropzone + copy are duplicated verbatim between `StudioLayerPanel` and `StudioCanvas`

- Severity: suggestion
- File: `packages/studio/src/surface_studio_canvas_component.tsx` (new, lines `303-324`) and `packages/studio/src/surface_studio_layer_panel_component.tsx` (pre-existing, lines `206-235`)
- Description: The new canvas empty-state dropzone is a byte-for-byte clone of the sidebar dropzone's label/hint structure and copy:
  - `{isDragging ? "Drop PSD file to inspect" : "Click or drag new .PSD to replace"}`
  - `"Photoshop CC 2024+ · Max 500 MB"`
  - click → `fileInputRef.current?.click()`, `onKeyDown` Enter/Space, `onDragOver`/`onDragLeave`/`onDrop`, `role="button"` + `tabIndex={0}` + `aria-label="Drop PSD file or click to browse"`
  - both use `.pt-studio-canvas-dropzone*` / `.pt-studio-sidebar-dropzone*` CSS that differs only in padding and font sizes
  This is the same "drop a PSD to inspect/replace" affordance implemented twice. Per finding 1 the sidebar copy becomes dead in production, which makes the duplication pure overhead: two copies of the same strings and keyboard/drag logic that must stay in sync.
- Suggestion: Shrink / dedupe. Pick one dropzone as canonical. Since upload is now owned by `StudioCanvas`, keep the canvas dropzone and either delete the sidebar dropzone (preferred, folds into finding 1) or extract the shared copy into a single constant so the strings do not diverge.

### 4. `hasDocument` prop is a derived value passed alongside `fileMeta` (redundant input)

- Severity: nit
- File: `packages/studio/src/surface_studio_canvas_component.tsx:35,46` (prop) and `packages/studio/src/surface_studio_landing_component.tsx:68` (`hasDocument={Boolean(fileMeta)}`)
- Description: `StudioCanvas` receives both `hasDocument: boolean` and `fileMeta?: StudioFileMeta`, but the sole production caller sets `hasDocument={Boolean(fileMeta)}`. The boolean is fully derived from `fileMeta` and adds a second source of truth that can drift (a caller could pass `hasDocument` without `fileMeta` and hit the chip fallback, or `fileMeta` with `hasDocument={false}` and never render it).
- Suggestion: Native / shrink. Drop the `hasDocument` prop and compute `const hasDocument = fileMeta != null` inside `StudioCanvas`. Callers already pass `fileMeta`; the separate flag is one extra input with one trivial derivation.

### 5. New CSS rules duplicate the existing sidebar dropzone styling instead of reusing it

- Severity: nit
- File: `packages/shared/src/common/styles.css:4928-4974` (new `.pt-studio-canvas-dropzone*`) vs pre-existing `5109-5136` (`.pt-studio-sidebar-dropzone*`)
- Description: The new dropzone block re-declares the same visual language as the sidebar dropzone (`display:flex; flex-direction:column; align-items:center; text-align:center; dashed border; blur backdrop; identical hover/drag color `rgba(99,102,241,0.08)`) with only padding/font-size deltas. Combined with finding 3, the codebase now carries two near-identical dropzone style sets.
- Suggestion: Shrink / native. Reuse the sidebar dropzone class (or promote one `.pt-studio-dropzone` token set) and express the canvas's size deltas as overrides, rather than forking the rules. If finding 1 deletes the sidebar dropzone, delete the sidebar CSS block too and keep only the canvas one.

---

## Summary

No new files, types, configs, or dependencies beyond what the feature needs. The 13 new unit tests are proportionate and are not flagged.

The complexity introduced is duplication-plus-dead-surface: this PR moves upload/re-inspect from `StudioLayerPanel` to `StudioCanvas` but leaves the panel's now-unreachable upload/drop/re-inspect code, props, hidden input, and dropzone in place (findings 1-2), which in turn leaves a verbatim copy of the dropzone copy/logic/CSS across two components (findings 3, 5). `hasDocument` is a derived prop that can be inlined (finding 4). The cleanest reduction is to finish the re-wire inside `StudioLayerPanel` — delete its upload/drop/re-inspect surface and the duplicated dropzone — then inline `hasDocument` and collapse the duplicated CSS.

- bug: 0
- suggestion: 3 (findings 1-3)
- nit: 2 (findings 4-5)

All findings: Status: open