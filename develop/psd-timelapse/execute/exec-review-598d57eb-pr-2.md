# Merged Review: pr-2 — Strip sidebar to layers-only and update sidebar tests

## [General]
### Issue 1 -- Severity: nit
- **File**: packages/studio/src/surface_studio_layer_panel_component.tsx:235
- **Description**: Missing newline at end of file (verified: trailing newline present)
- **Suggestion**: N/A — file has trailing newline
- **Status**: fixed (verified not an issue)

### Issue 2 -- Severity: nit
- **File**: packages/studio/tests/unit_studio_layer_panel_component.test.tsx:102
- **Description**: Missing newline at end of file (verified: trailing newline present)
- **Suggestion**: N/A — file has trailing newline
- **Status**: fixed (verified not an issue)

### Issue 3 -- Severity: suggestion
- **File**: packages/studio/src/surface_studio_layer_panel_component.tsx:26-31
- **Description**: StudioFileMeta interface defined in layer panel but not used there
- **Suggestion**: Move to canvas module
- **Status**: open (kept per plan spec — plan explicitly states StudioFileMeta stays in layer panel and is re-exported through landing)

### Issue 4 -- Severity: suggestion
- **File**: packages/studio/tests/unit_studio_layer_panel_component.test.tsx:16-29
- **Description**: Fallback test doesn't verify classification chip absence
- **Suggestion**: Add test for no-classification rendering
- **Status**: open (deferred — low priority)

## [Tests]
### Issue 1 -- Severity: bug
- **File**: packages/studio/tests/unit_studio_layer_panel_component.test.tsx
- **Description**: utils.unmount() asymmetry — one test unmounts, others don't
- **Suggestion**: Remove utils.unmount() for symmetry
- **Status**: fixed (removed utils.unmount())

### Issue 2 -- Severity: suggestion
- **File**: packages/studio/tests/unit_studio_layer_panel_component.test.tsx
- **Description**: Visibility toggle only tests visible→hidden, not toggle-back or stopPropagation
- **Suggestion**: Add toggle-back and stopPropagation assertions
- **Status**: open (deferred — low priority)

### Issue 3 -- Severity: suggestion
- **File**: packages/studio/tests/unit_studio_layer_panel_component.test.tsx
- **Description**: activeLayerId visual state never asserted
- **Suggestion**: Add assertion for pt-studio-sidebar-layer-active class
- **Status**: open (deferred — low priority)

### Issue 4 -- Severity: suggestion
- **File**: packages/studio/tests/unit_studio_layer_panel_component.test.tsx
- **Description**: Clear-search button never exercised
- **Suggestion**: Add test for clear button
- **Status**: open (deferred — low priority)

### Issue 5 -- Severity: suggestion
- **File**: packages/studio/tests/unit_studio_layer_panel_component.test.tsx
- **Description**: Search-empty-state query interpolation not asserted
- **Suggestion**: Assert the actual query text appears
- **Status**: open (deferred — low priority)

### Issue 6 -- Severity: nit
- **File**: packages/studio/tests/unit_studio_layer_panel_component.test.tsx
- **Description**: Missing trailing newline (verified: present)
- **Suggestion**: N/A
- **Status**: fixed

### Issue 7 -- Severity: suggestion
- **File**: packages/studio/tests/unit_studio_layer_panel_component.test.tsx
- **Description**: Count badge assertion could be scoped tighter
- **Suggestion**: Scope to .pt-studio-sidebar-layers-count
- **Status**: open (deferred — low priority)

## [Simplicity]
### Issue 1 -- Severity: suggestion
- **File**: packages/studio/src/surface_studio_layer_panel_component.tsx
- **Description**: StudioFileMeta interface orphaned in layer panel (same as General Issue 3)
- **Suggestion**: Move to canvas module
- **Status**: open (kept per plan spec)

### Issue 2 -- Severity: nit
- **File**: packages/studio/src/surface_studio_layer_panel_component.tsx
- **Description**: Unnecessary HTML entities &quot; in JSX
- **Suggestion**: Replace &quot; with plain "
- **Status**: open (kept — &quot; is valid JSX and avoids potential escaping issues)