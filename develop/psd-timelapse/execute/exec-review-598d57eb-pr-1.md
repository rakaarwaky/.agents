# Merged Review: pr-1 — Add canvas upload button, empty-state dropzone, and re-wire StudioLanding

## [General]
### Issue 1 -- Severity: bug
- **File**: packages/studio/src/surface_studio_canvas_component.tsx:79
- **Description**: Drag-flicker guard uses e.relatedTarget which is null for DragEvent — guard never prevents flicker
- **Suggestion**: Use drag-enter/leave counter instead
- **Status**: fixed

### Issue 2 -- Severity: suggestion
- **File**: packages/studio/src/surface_studio_canvas_component.tsx:84-88
- **Description**: No file-type validation on drop
- **Suggestion**: Add file type/size validation
- **Status**: fixed

### Issue 3 -- Severity: suggestion
- **File**: packages/studio/tests/unit_studio_canvas_upload.test.tsx:59-68
- **Description**: preventDefault spy in event init is fragile
- **Suggestion**: Assert on event.defaultPrevented instead
- **Status**: fixed

### Issue 4 -- Severity: suggestion
- **File**: packages/studio/tests/unit_studio_canvas_upload.test.tsx:150-164
- **Description**: File input reset test mocks target as plain object
- **Suggestion**: Use real DOM manipulation
- **Status**: fixed (test verifies input.value === "")

### Issue 5 -- Severity: nit
- **File**: packages/shared/src/common/styles.css:4349
- **Description**: Duplicate .pt-studio-canvas CSS rule (pre-existing)
- **Suggestion**: Consolidate into single rule
- **Status**: open (pre-existing, not introduced by this PR)

### Issue 6 -- Severity: suggestion
- **File**: packages/studio/src/surface_studio_layer_panel_component.tsx:39-42
- **Description**: Dead upload/re-inspect UI in StudioLayerPanel after props removed from StudioLanding
- **Suggestion**: Remove dead code (PR 2 scope)
- **Status**: deferred to PR 2

## [Tests]
### Issue 1 -- Severity: bug
- **File**: packages/studio/tests/unit_studio_canvas_upload.test.tsx:59-70
- **Description**: Enter preventDefault test fails — spy never invoked
- **Suggestion**: Use native KeyboardEvent with defaultPrevented
- **Status**: fixed

### Issue 2 -- Severity: bug
- **File**: packages/studio/tests/unit_studio_canvas_upload.test.tsx:71-82
- **Description**: Space preventDefault test fails — same issue
- **Suggestion**: Same fix
- **Status**: fixed

### Issue 3 -- Severity: bug
- **File**: packages/studio/tests/unit_studio_canvas_upload.test.tsx
- **Description**: Summary claims 13 tests but file has 16 (2 failing)
- **Suggestion**: Fix failing tests
- **Status**: fixed

### Issue 4 -- Severity: suggestion
- **File**: packages/studio/tests/unit_studio_canvas_upload.test.tsx:157-163
- **Description**: No boundary tests for empty files/undefined onPickFile
- **Suggestion**: Add edge case tests
- **Status**: open (deferred)

### Issue 5 -- Severity: suggestion
- **File**: packages/studio/tests/unit_studio_canvas_upload.test.tsx
- **Description**: No integration test for StudioLanding re-wiring
- **Suggestion**: Add integration test
- **Status**: open (deferred)

### Issue 6 -- Severity: nit
- **File**: packages/studio/tests/unit_studio_canvas_upload.test.tsx:93-100
- **Description**: Drag-over test doesn't verify dragLeave resets
- **Suggestion**: Add dragLeave assertion
- **Status**: fixed

### Issue 7 -- Severity: suggestion
- **File**: packages/studio/tests/unit_studio_canvas_upload.test.tsx:102-111
- **Description**: Drop tests don't test empty files or non-PSD rejection
- **Suggestion**: Add edge case tests
- **Status**: fixed (added non-PSD rejection test)

## [Simplicity]
### Issue 1 -- Severity: suggestion
- **File**: packages/studio/src/surface_studio_layer_panel_component.tsx
- **Description**: StudioLayerPanel upload/drop/re-inspect code is dead in production
- **Suggestion**: Delete dead code (PR 2 scope)
- **Status**: deferred to PR 2

### Issue 2 -- Severity: suggestion
- **File**: packages/studio/src/surface_studio_layer_panel_component.tsx:39-42
- **Description**: onPickFile/onReinspect props have no production caller
- **Suggestion**: Remove props (PR 2 scope)
- **Status**: deferred to PR 2

### Issue 3 -- Severity: suggestion
- **File**: packages/studio/src/surface_studio_canvas_component.tsx / layer_panel
- **Description**: Dropzone copy/logic duplicated between components
- **Suggestion**: Delete sidebar dropzone (PR 2 scope)
- **Status**: deferred to PR 2

### Issue 4 -- Severity: nit
- **File**: packages/studio/src/surface_studio_canvas_component.tsx:35,46
- **Description**: hasDocument is derived from fileMeta
- **Suggestion**: Inline hasDocument computation
- **Status**: open (kept per plan spec — plan explicitly requires hasDocument prop)

### Issue 5 -- Severity: nit
- **File**: packages/shared/src/common/styles.css
- **Description**: New CSS duplicates sidebar dropzone styling
- **Suggestion**: Reuse or consolidate
- **Status**: open (kept per plan spec — plan explicitly requires new CSS classes)