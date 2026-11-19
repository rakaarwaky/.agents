# Execution Summary: pr-2 — Strip sidebar to layers-only and update sidebar tests

## Changes Made

### packages/studio/src/surface_studio_layer_panel_component.tsx
- Removed imports: `useRef`, `DragEvent`, `ChangeEvent` (no longer needed)
- Removed from `StudioLayerPanelProps`: `fileMeta`, `onPickFile`, `onReinspect`
- Removed `DEFAULT_FILE_META` constant
- Removed state: `fileInputRef`, `isDragging`
- Removed handlers: `processFile`, `handleDrop`, `handleFileInputChange`, `handleReset`
- Removed DOM: hidden `<input type="file">`, `.pt-studio-sidebar-header`, `.pt-studio-sidebar-file`, `.pt-studio-sidebar-dropzone`
- Removed derived variables: `meta`, `metaLine`
- Kept: `StudioFileMeta` interface definition (re-exported through landing), `DEFAULT_LAYERS`, `hiddenLayerIds`, `searchQuery`/`activeLayerId`/`hiddenIds` state, `toggleVisibility`/`handleSelect` handlers, `<aside>` root with `.pt-studio-sidebar-panel`, `.pt-studio-sidebar-layers` with header/search/list
- Updated aria-label from "Source PSD document & layer panel" to "Layer panel"

### packages/studio/tests/unit_studio_layer_panel_component.test.tsx
- Removed imports: `StudioFileMeta` type
- Removed `REAL_FILE_META` constant
- Updated `renderPanel` helper: removed `fileMeta` from default props
- Removed tests: file metadata rendering, dropzone drop, file input change, reinspect button
- Kept tests: real layer rows, DEFAULT_LAYERS fallback, onSelectLayer, visibility toggle, search filter, empty state

## Verification
- `lint-arwaky-cli scan .` — 78 violations (baseline, no new)
- AES compliance: StudioLayerPanel remains passive (callbacks only, no domain logic)
- `StudioFileMeta` interface preserved for re-export chain