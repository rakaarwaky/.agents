## Plan Document Review: Move Studio PSD Upload Affordance to Canvas Top Bar with Empty-Canvas Drag-and-Drop

### Summary
Needs revision. The architectural direction, passive component boundaries (AES201/AES406), and user experience improvements are solid, but the plan contains a PR boundary contradiction between the rollout strategy and PR 1 implementation, an unhandled HTML5 drag-leave event flickering bug on child stage elements, and complete omission of document metadata from the UI.

### Issue 1: Discrepancy between Rollout Plan and PR 1 implementation for sidebar upload
- **Severity**: bug
- **Section**: Section 3 (`surface_studio_landing_component.tsx`), Rollout Plan (lines 567–571), and PR Plan
- **Description**: The Rollout Plan states: *"At this PR [PR 1], both the sidebar and canvas accept dropped PSD files (duplicated, temporarily)."* However, Section 3 of the plan updates `StudioLanding` in PR 1 so that it stops passing `onPickFile` and `fileMeta` to `<StudioLayerPanel>`:
  ```tsx
  <aside className="pt-studio-sidebar">
    <StudioLayerPanel
      layers={layers}
      onSelectLayer={onSelectLayer}
      onReinspect={onReinspect}
    />
  </aside>
  ```
  If `StudioLanding` stops passing `onPickFile` in PR 1, the sidebar dropzone in `StudioLayerPanel` immediately becomes non-functional in the running app (dropping a file invokes an undefined `onPickFile`, doing nothing), and file metadata immediately reverts to fallback `DEFAULT_FILE_META`. Conversely, if `StudioLanding` retains `onPickFile` and `fileMeta` during PR 1 to support the temporary dual-dropzone state, then PR 2 must touch `surface_studio_landing_component.tsx` when removing those props from `StudioLayerPanelProps`, but `surface_studio_landing_component.tsx` is omitted from PR 2's affected files list.
- **Suggestion**: Align the PR boundaries. Either:
  1. Have PR 1 keep passing `onPickFile={onPickFile}` and `fileMeta={fileMeta}` to `<StudioLayerPanel>` so dual dropzones function during PR 1, and add `surface_studio_landing_component.tsx` to PR 2's affected files list to disconnect them cleanly in lockstep with `StudioLayerPanelProps`; or
  2. Acknowledge that PR 1 decommissions sidebar upload immediately at the composition level, update the Rollout Plan description to remove the claim of temporary dual dropzone support, and keep `surface_studio_landing_component.tsx` in PR 1.
- **Status**: open

### Issue 2: Drag-and-drop flickering on stage child elements (`onDragLeave`)
- **Severity**: bug
- **Section**: Section 1 (`surface_studio_canvas_component.tsx` — Canvas stage render logic)
- **Description**: The plan attaches `onDragLeave={() => setIsDragging(false)}` directly to `.pt-studio-canvas-stage`. In HTML5 / React drag-and-drop, when a dragged file passes over any child element (e.g. `.pt-studio-canvas-frame`, preview SVG, chip, or `.pt-studio-canvas-dropzone` children like icons and text), the browser fires `dragleave` on the stage and `dragenter` on the child. Without checking whether the drag has actually left the stage boundary (e.g. using `e.currentTarget.contains(e.relatedTarget as Node)` or a drag counter ref), `isDragging` will rapidly toggle between `true` and `false`, repeatedly mounting and unmounting `.pt-studio-canvas-drag-overlay` or toggling CSS classes while dragging.
- **Suggestion**: Specify child-boundary protection for the drag event handlers. In `handleDragLeave`, check `if (!e.currentTarget.contains(e.relatedTarget as Node)) { setIsDragging(false); }` or maintain a counter ref (`dragCounter`), and ensure child elements within the dropzone have `pointer-events: none` or boundary guards.
- **Status**: open

### Issue 3: Complete loss of document metadata display across the entire Studio surface
- **Severity**: suggestion
- **Section**: Section 1, Section 2, and Alternatives Considered (Alternative 4)
- **Description**: Current `StudioLayerPanel` displays document metadata (`sycan-front-shirt.psd`, `184.2 MB · RGB 16-bit · 3000 × 3000 · 2 layers`). The plan strips this block from the sidebar and explicitly rejects passing `fileMeta` to `StudioCanvas` (Alternative 4), providing only a boolean `hasDocument`. As a result, once a document is loaded, the user has zero visual confirmation of which file is open, its dimensions, or its size anywhere in the Studio surface (the canvas preview frame hardcodes `"CANVAS PREVIEW · 3000 × 3000 PX"`). Furthermore, `StudioContainer` in `root_web_smart_container.ts` continues to compute `fileMeta` on every render, but that computation becomes completely dead except for `Boolean(fileMeta)`.
- **Suggestion**: Either pass `fileMeta?: StudioFileMeta` (or at least `documentName?: string`) to `StudioCanvas` so the top toolbar or frame chip (`.pt-studio-canvas-chip`) can dynamically display the active document name and dimensions, or explicitly document this trade-off as an intentional product simplification and plan a follow-up task to surface the document title in the canvas toolbar.
- **Status**: open

### Issue 4: Ambiguity in `onReinspect` handling and retention in `StudioLayerPanel`
- **Severity**: suggestion
- **Section**: Section 2 (`surface_studio_layer_panel_component.tsx`) and Key Decisions (Decision 2 & 5)
- **Description**: The document contains conflicting statements regarding `onReinspect` in `StudioLayerPanel`. In Section 2, the plan lists `handleReset` under "Code removals", but under "Retained" says `onReinspect prop (remains available; the layers header or canvas can invoke it)` and suggests it is "optionally wired to a small refresh icon in the layers header row". However, Key Decision 5 states that "All file ingestion, metadata display, and refresh controls are removed" from the sidebar. If all refresh controls are removed, retaining `readonly onReinspect?: () => void` in `StudioLayerPanelProps` creates an unused prop. Furthermore, Section 5 notes that the unit test for `onReinspect` should be "removed or relocated to canvas tests (sidebar may retain a secondary refresh but the primary is in canvas)".
- **Suggestion**: Clarify whether `StudioLayerPanel` retains a refresh icon in `.pt-studio-sidebar-layers-header` or removes it entirely. If retaining it, provide the exact JSX markup and keep the unit test for it in `unit_studio_layer_panel_component.test.tsx`. If removing it, remove `onReinspect` from `StudioLayerPanelProps` as well to prevent dead prop declarations.
- **Status**: open

### Issue 5: File input `value` not cleared on upload, blocking re-upload of the same file
- **Severity**: suggestion
- **Section**: Section 1 (`surface_studio_canvas_component.tsx` — Event handlers)
- **Description**: The `handleFileInputChange` handler calls `onPickFile?.(e.target.files[0])`, but does not reset `e.target.value = ""`. In standard browser behavior, if a user picks a file, modifies it on disk, and attempts to re-select the exact same file path via the "Upload" button, the native `<input type="file">` will not fire an `onChange` event because the file input value has not changed.
- **Suggestion**: Reset the input value after triggering the callback:
  ```ts
  const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onPickFile?.(e.target.files[0]);
    }
    e.target.value = "";
  };
  ```
- **Status**: open

### Issue 6: Misleading empty-state copy on canvas stage
- **Severity**: nit
- **Section**: Section 1 (`surface_studio_canvas_component.tsx` — Canvas stage render logic)
- **Description**: The empty-state dropzone card displays `"Click or drag new .PSD to replace"`. In an empty state where no document has been inspected or loaded yet, instructing the user to "replace" is confusing copy inherited directly from the old sidebar dropzone.
- **Suggestion**: Change the empty-state prompt text to `"Click or drag .PSD to open"` or `"Click or drag .PSD to inspect"` when `!hasDocument`, while reserving `"Drop new .PSD to replace"` for active drag-over when `hasDocument` is true.
- **Status**: open

### Issue 7: `.pt-studio-canvas-divider` usage without text or rule styles
- **Section**: Section 1 (`surface_studio_canvas_component.tsx`) and Section 4 (`styles.css`)
- **Severity**: nit
- **Description**: The plan specifies inserting `<span className="pt-studio-canvas-divider" />` as a separator between the Upload button and the zoom cluster. In `packages/shared/src/common/styles.css`, `.pt-studio-canvas-divider` only defines font size, font color, and margin (`0 0.125rem`), because it was previously used with textual content like `⌘` or `100%`. An empty `<span className="pt-studio-canvas-divider" />` has zero width, no background, and no border, so it will not render a visible separator line.
- **Suggestion**: Either provide explicit separator styling in CSS (e.g. `width: 1px; height: 1rem; background: rgba(255, 255, 255, 0.15); margin: 0 0.5rem;`) or use a visible divider token/character.
- **Status**: open

### Issue 8: Missing `data-testid` on `.pt-studio-canvas-stage` and missing Enter/Space `preventDefault`
- **Severity**: nit
- **Section**: Section 1 (`surface_studio_canvas_component.tsx`) and Section 5 (Test Changes)
- **Description**: The test plan states that test 6 will `fireEvent.drop` on `.pt-studio-canvas-stage`. However, `.pt-studio-canvas-stage` lacks a `data-testid` (only `data-testid="studio-canvas"` and `data-testid="studio-canvas-empty-dropzone"` are defined), requiring tests to query by CSS class. Additionally, `onKeyDown` on the empty dropzone does not call `e.preventDefault()`, which may trigger default page scrolling when pressing the spacebar.
- **Suggestion**: Add `data-testid="studio-canvas-stage"` to `.pt-studio-canvas-stage` and call `e.preventDefault()` on Enter/Space key events.
- **Status**: open

### Strengths
- **Strict passive component adherence**: Adheres cleanly to AES201 and AES406 by keeping `StudioCanvas` purely passive and lifting file pick/reinspect orchestration to `StudioContainer`.
- **Zero modification to Smart Container**: Correctly avoids churn in `packages/root_web_smart_container.ts` by deriving `hasDocument` in `StudioLanding`.
- **Preserved re-export compatibility**: Thoughtfully preserves the `StudioFileMeta` type export chain from `surface_studio_layer_panel_component.tsx` through `surface_studio_landing_component.tsx` to prevent breaking existing consumers.
- **Well-structured test coverage plan**: Specifies a dedicated new test file `unit_studio_canvas_upload.test.tsx` and carefully identifies which obsolete test assertions in `unit_studio_layer_panel_component.test.tsx` must be retired.
- **Clear visual hierarchy and UX improvement**: Correctly diagnoses the UI imbalance in the Studio surface and provides a modern drag-and-drop canvas UX matching industry standards.
