# Test Review Findings: pr-1 Studio Canvas Upload

### Issue 1 -- Severity: bug
- **File**: `packages/studio/tests/unit_studio_canvas_upload.test.tsx:59-70`
- **Description**: The test "pressing Enter on dropzone triggers file input click and preventDefault" fails. The `preventDefault` spy is passed as a property in the `fireEvent.keyDown` options object, but React's synthetic event system does not invoke `preventDefault` from the properties object — it only calls the actual `e.preventDefault()` method. The spy never gets called, so the assertion `expect(preventDefaultSpy).toHaveBeenCalled()` fails.
- **Suggestion**: Stop passing `preventDefault` as an event property. Instead, spy on `Event.prototype.preventDefault` or attach a temporary `onKeyDown` listener that captures the real event.
- **Status**: open

### Issue 2 -- Severity: bug
- **File**: `packages/studio/tests/unit_studio_canvas_upload.test.tsx:71-82`
- **Description**: The test "pressing Space on dropzone triggers file input click and preventDefault" fails for the same reason as Issue 1.
- **Suggestion**: Same fix as Issue 1.
- **Status**: open

### Issue 3 -- Severity: bug
- **File**: `packages/studio/tests/unit_studio_canvas_upload.test.tsx`
- **Description**: The execution summary claims "13 test cases" but the file actually contains 16 `it` blocks. When run, 2 fail (the Enter/Space preventDefault tests) and 14 pass.
- **Suggestion**: Correct the summary count. Fix the two failing tests so all 16 pass.
- **Status**: open

### Issue 4 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_canvas_upload.test.tsx:157-163`
- **Description**: The file input reset test verifies `input.value` is cleared but does not test boundary conditions (empty files, undefined onPickFile).
- **Suggestion**: Add tests for empty files list and undefined onPickFile.
- **Status**: open

### Issue 5 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_canvas_upload.test.tsx`
- **Description**: No integration test for StudioLanding re-wiring.
- **Suggestion**: Add integration test verifying StudioCanvas receives the new props and StudioLayerPanel does not receive the removed ones.
- **Status**: open

### Issue 6 -- Severity: nit
- **File**: `packages/studio/tests/unit_studio_canvas_upload.test.tsx:93-100`
- **Description**: Drag-over test does not verify dragLeave resets isDragging.
- **Suggestion**: Add assertion for dragLeave behavior.
- **Status**: open

### Issue 7 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_canvas_upload.test.tsx:102-111`
- **Description**: Drop tests do not test empty files list or undefined onPickFile.
- **Suggestion**: Add edge case tests.
- **Status**: open