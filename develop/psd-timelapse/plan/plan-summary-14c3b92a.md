# Summary: Move Studio PSD Upload Affordance to Canvas Top Bar (plan-doc-14c3b92a)

**Scope.** Re-architect the PSD upload interaction within the interactive Studio surface (`packages/studio/`): move file upload trigger from the right sidebar (`StudioLayerPanel`) to the canvas top toolbar (`StudioCanvas`), introduce centered drag-and-drop empty state on the canvas stage, enable file replacement via stage drag-and-drop on loaded state, and strip the sidebar down strictly to layer controls.

**Key changes.**
- **Canvas Top Bar (`StudioCanvas`):**
  - Insert primary **Upload** button into `.pt-studio-canvas-toolbar` before the zoom controls cluster, styled with `--pt-primary`.
  - Add `↻` re-inspect button to the canvas toolbar when a document is loaded (`hasDocument=true`).
  - Add hidden `<input type="file" accept=".psd,image/*" data-testid="studio-canvas-file-input">` at canvas root.
- **Canvas Center Stage (`StudioCanvas`):**
  - **Empty state (`!hasDocument`):** Renders centered dropzone card reading:
    - `"Click or drag new .PSD to replace"`
    - `"Photoshop CC 2024+ · Max 500 MB"`
    - `cloud_upload` icon via `material-symbols-outlined`
  - **Loaded state (`hasDocument`):** Renders preview mockup frame as before, with a subtle dashed overlay during active drag-over (`.pt-studio-canvas-drag-overlay`).
  - Stage handles `onDragOver`, `onDragLeave`, `onDrop` in both states, invoking `onPickFile(file)`.
- **Sidebar Stripping (`StudioLayerPanel`):**
  - Remove `"SOURCE PSD DOCUMENT"` header and refresh button.
  - Remove file metadata block (`Ps` icon, name, size, dimensions, menu).
  - Remove inline sidebar dropzone (`☁`, labels).
  - Remove `onPickFile` and `fileMeta` from `StudioLayerPanelProps`.
  - Sidebar now contains strictly: LAYERS header (icon + "LAYERS" + count), search input, and layer list stack.
- **Composition Root (`StudioLanding`):**
  - Passes `onPickFile`, `onReinspect`, and `hasDocument={Boolean(fileMeta)}` to `<StudioCanvas>`.
  - Passes `layers`, `onSelectLayer`, and `onReinspect` to `<StudioLayerPanel>`.
  - `StudioContainer` in `packages/root_web_smart_container.ts` requires zero changes.
- **Styling (`packages/shared/src/common/styles.css`):**
  - Added: `.pt-studio-canvas-upload-btn`, `.pt-studio-canvas-dropzone`, `.pt-studio-canvas-dropzone-icon`, `.pt-studio-canvas-dropzone-label`, `.pt-studio-canvas-dropzone-hint`, `.pt-studio-canvas-dropzone-drag`, `.pt-studio-canvas-drag-overlay`.
- **Testing:**
  - New test file: `packages/studio/tests/unit_studio_canvas_upload.test.tsx` (toolbar upload button click, empty-state rendering, drag-and-drop in empty/loaded states, re-inspect button gating).
  - Updated test file: `packages/studio/tests/unit_studio_layer_panel_component.test.tsx` (remove dropzone and file-info assertions).

**Resolved Decisions.**
1. **Upload button placement:** Leading edge of `.pt-studio-canvas-toolbar`, styled with primary accent color (`--pt-primary`) and separated by a divider from the zoom group.
2. **Re-inspect button:** Relocated to canvas toolbar beside Upload, gated on `hasDocument=true`.
3. **Interface minimalism:** Canvas receives `hasDocument: boolean` rather than full `StudioFileMeta`. `StudioLanding` derives it from `fileMeta`.
4. **Preserved type exports:** `StudioFileMeta` stays declared in `surface_studio_layer_panel_component.tsx` to maintain re-export chain through `StudioLanding` to `StudioContainer`.
5. **AES compliance:** Canvas remains a passive surface component (AES406). No domain logic enters the surface layer; all file actions delegate through `onPickFile` to `StudioContainer`.

**PR Plan (2 ordered PRs).**
- **PR 1:** Canvas top bar upload button, empty-state dropzone, and StudioLanding re-wiring (`styles.css`, `surface_studio_canvas_component.tsx`, `surface_studio_landing_component.tsx`, `unit_studio_canvas_upload.test.tsx`).
- **PR 2:** Strip sidebar to layer control and update sidebar tests (`surface_studio_layer_panel_component.tsx`, `unit_studio_layer_panel_component.test.tsx`).

Full plan document available at: `/home/raka/.agents/develop/psd-timelapse/plan/plan-doc-14c3b92a.md`
