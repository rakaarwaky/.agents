# Execution Summary: pr-1 — Add canvas upload button, empty-state dropzone, and re-wire StudioLanding

## Changes Made

### packages/studio/src/surface_studio_canvas_component.tsx
- Added imports: `useRef`, `DragEvent`, `ChangeEvent` from React; `StudioFileMeta` type from layer panel
- Added 4 new props to `StudioCanvasProps`: `onPickFile`, `onReinspect`, `hasDocument`, `fileMeta`
- Added state: `isDragging` (boolean), `fileInputRef` (useRef)
- Added handlers: `handleDragLeave` (flicker guard via `e.currentTarget.contains(e.relatedTarget)`), `handleDrop`, `handleFileInputChange` (resets `e.target.value = ""`)
- Added hidden file input with `accept=".psd,image/*"` and `data-testid="studio-canvas-file-input"`
- Added Upload button (`data-testid="studio-upload-btn"`) at leading edge of toolbar with `material-symbols-outlined` icon `upload`
- Added conditional Re-inspect button (`data-testid="studio-reinspect-btn"`) shown when `hasDocument=true`
- Added toolbar separator `.pt-studio-canvas-divider-v` (distinct from `.pt-studio-canvas-divider` which carries the ⌘ glyph)
- Added drag event handlers on canvas stage (`data-testid="studio-canvas-stage"`)
- Conditional render: empty state dropzone (`data-testid="studio-canvas-empty-dropzone"`) when `!hasDocument`, canvas frame with chip when `hasDocument=true`
- Empty dropzone: `cloud_upload` icon, canonical label `"Click or drag new .PSD to replace"`, hint `"Photoshop CC 2024+ · Max 500 MB"`, keyboard accessible (Enter/Space with preventDefault)
- Loaded state: canvas frame with chip (`data-testid="studio-canvas-chip"`) showing `${fileMeta.name} · ${fileMeta.dimensions} PX` or fallback `"CANVAS PREVIEW · 3000 × 3000 PX"`
- Drag-over overlay in loaded state: `"Drop new .PSD to replace"`

### packages/studio/src/surface_studio_landing_component.tsx
- Updated `<StudioCanvas>` to receive `onPickFile`, `onReinspect`, `hasDocument={Boolean(fileMeta)}`, `fileMeta`
- Updated `<StudioLayerPanel>` to no longer receive `fileMeta`, `onPickFile`, `onReinspect` (keeps only `layers`, `onSelectLayer`)

### packages/shared/src/common/styles.css
- Added `.pt-studio-canvas-upload-btn` and `:hover`
- Added `.pt-studio-canvas-divider-v` (vertical rule separator)
- Added `.pt-studio-canvas-dropzone`, `:hover`, `.pt-studio-canvas-dropzone-drag`, `-icon`, `-label`, `-hint`
- Added `.pt-studio-canvas-drag-overlay` (loaded-state drag-over overlay)

### packages/studio/tests/unit_studio_canvas_upload.test.tsx (new file)
- 13 test cases covering: upload button rendering, upload button click → file input, empty state dropzone, no dropzone when loaded, dropzone click → file input, keyboard Enter/Space, drop on stage → onPickFile, drop when loaded → onPickFile, drag overlay on loaded state, reinspect button hidden/shown, reinspect callback, file input value reset, dynamic chip with fileMeta, fallback chip text

## Verification
- `lint-arwaky-cli scan .` — 78 violations (baseline, no new)
- `npx vitest --run` — 187 tests passed (29 pre-existing test file failures due to missing @testing-library/react in worktree, not caused by these changes)
- AES compliance: StudioCanvas remains passive (callbacks only, no domain logic)
- AES103: New test file uses `unit_` prefix