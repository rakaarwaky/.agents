# Review Notes — PR-1: Canvas Upload Button, Empty-State Dropzone, Re-wire StudioLanding

**Source**: `/home/raka/.agents/develop/psd-timelapse/execute/exec-summary-598d57eb-pr-1.md`
**Reviewed files**:
- `packages/studio/src/surface_studio_canvas_component.tsx`
- `packages/studio/src/surface_studio_landing_component.tsx`
- `packages/shared/src/common/styles.css`
- `packages/studio/tests/unit_studio_canvas_upload.test.tsx`

**Scope alignment**: PR-1 is described as adding a canvas upload button, empty-state dropzone, and re-wiring StudioLanding. The implementation matches this scope. No scope creep detected. The studio BACKLOG.md states "No declared spec IDs for this surface layer (passive surface, no FRD)" and DESIGN.md says PR-1 is design-spec-only; the implementation adds interactive surface behavior beyond the PR-1 spec-only framing, but this matches the exec-summary's stated intent and is internally consistent.

---

### Issue 1 -- Severity: bug
- **File**: `packages/studio/src/surface_studio_canvas_component.tsx:79`
- **Description**: The drag-flicker guard in `handleDragLeave` checks `e.currentTarget.contains(e.relatedTarget as Node)`. For `DragEvent`, `relatedTarget` is typically `null` in browsers (it is a `MouseEvent` property not populated during drag operations). `currentTarget.contains(null)` returns `false`, so `!false` is `true` and `setIsDragging(false)` always runs. The guard never prevents the flicker when the cursor moves across stage child elements.
- **Suggestion**: Replace the `relatedTarget`-based guard with a drag-enter/leave counter (increment on `onDragEnter`, decrement on `onDragLeave`, only set `isDragging(false)` when count reaches 0) or compare `e.target` against `e.currentTarget` and ignore `dragLeave` when the drag is still within the stage subtree.
- **Status**: open

### Issue 2 -- Severity: suggestion
- **File**: `packages/studio/src/surface_studio_canvas_component.tsx:84-88`
- **Description**: `handleDrop` calls `onPickFile?.(e.dataTransfer.files[0])` without validating the dropped file's type or size. The `accept=".psd,image/*"` attribute only constrains the `<input>` file picker dialog; drag-and-drop is unconstrained, so any file type can be dropped and passed to the container.
- **Suggestion**: Add file type/size validation in `handleDrop` (mirroring the `accept` constraint) before invoking `onPickFile`, or document that the container must validate. At minimum, guard against non-PSD/image MIME types.
- **Status**: open

### Issue 3 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_canvas_upload.test.tsx:59-68` and `:71-80`
- **Description**: The Enter/Space keyboard tests pass `preventDefault: preventDefaultSpy` in the `fireEvent.keyDown` event init, then assert `preventDefaultSpy` was called. The component calls the native `e.preventDefault()` on the synthetic event. Whether the spy intercepts that call depends on the test framework's event init handling; this is a fragile assertion that may pass trivially or fail unpredictably across renderer versions.
- **Suggestion**: Assert on `event.defaultPrevented` after dispatch, or spy on `Element.prototype.dispatchEvent` / the dropzone's `onKeyDown` prop directly, rather than passing a `preventDefault` property in the event init.
- **Status**: open

### Issue 4 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_canvas_upload.test.tsx:150-164`
- **Description**: The file-input-reset test calls `fireEvent.change(input, { target: { files: [fakeFile] } })`, which mocks `e.target` as a plain object `{ files: [fakeFile] }`. The component's `e.target.value = ""` then sets `value` on that mock object, not on the real `<input>` DOM node. The subsequent `expect(input.value).toBe("")` checks the real input, whose value was never changed by the mocked event — so the test passes trivially without actually verifying the reset behavior.
- **Suggestion**: Set `input.value` to a non-empty string before firing the change event, then fire a real change event with `Object.defineProperty(input, 'files', { value: [fakeFile] })` (or use `HTMLInputElement`'s `files` setter if available), and assert `input.value === ""` afterward.
- **Status**: open

### Issue 5 -- Severity: nit
- **File**: `packages/shared/src/common/styles.css:4349` and `:4754`
- **Description**: `.pt-studio-canvas` is defined twice in styles.css (line 4349 and line 4754). The second rule overrides the first due to source order. The first defines `gap: 1rem; padding: 1rem;`; the second defines `gap: 0.5rem; min-height: 0; flex: 1; background...`. This is redundant and could cause confusion during future edits.
- **Suggestion**: Consolidate into a single `.pt-studio-canvas` rule.
- **Status**: open

### Issue 6 -- Severity: suggestion
- **File**: `packages/studio/src/surface_studio_layer_panel_component.tsx:39-42, 90-153`
- **Description**: `StudioLayerPanel` still declares and uses `fileMeta`, `onPickFile`, and `onReinspect` props (renders its own file input, dropzone, and refresh button), but `StudioLanding` no longer passes them (`surface_studio_landing_component.tsx:63-69` passes only `layers` and `onSelectLayer`). When composed through `StudioLanding`, the panel's upload/dropzone/re-inspect UI is dead — `onPickFile` and `onReinspect` are `undefined`, so `processFile` and `onReinspect?.()` no-op. The panel falls back to `DEFAULT_LAYERS`/`DEFAULT_FILE_META`. This creates a UX inconsistency: the sidebar shows non-functional upload/re-inspect controls while the canvas toolbar has working ones.
- **Suggestion**: Either remove the dead upload/dropzone/re-inspect UI from `StudioLayerPanel` (since responsibility moved to the canvas), or keep passing the props from `StudioLanding` so the sidebar remains functional.
- **Status**: open

---

### Items confirmed clean (no issue)

- **File input value reset** (`surface_studio_canvas_component.tsx:92-96`): `e.target.value = ""` is correctly placed after `onPickFile?.(e.target.files[0])`, so selecting the same file consecutively still triggers `onChange`. This is the standard pattern and works as intended.
- **Drag-flicker guard syntax** (`surface_studio_canvas_component.tsx:77-81`): The code pattern `e.currentTarget.contains(e.relatedTarget as Node)` is the correct idiom for mouse events; the defect is that `relatedTarget` is null for `DragEvent` (see Issue 1).
- **StudioCanvas passivity** (AES201/AES406): All behavior delegates through `onPickFile`, `onReinspect`, `onRender` callbacks. No domain logic, no direct API calls, no secrets handling. Confirmed passive.
- **StudioLanding re-wiring** (`surface_studio_landing_component.tsx:62-69`): Correctly passes `onPickFile`, `onReinspect`, `hasDocument={Boolean(fileMeta)}`, `fileMeta` to `<StudioCanvas>`; `<StudioLayerPanel>` receives only `layers` and `onSelectLayer`. No props leaked to wrong component.
- **CSS class naming** (`packages/shared/src/common/styles.css:4898-4990`): `.pt-studio-canvas-upload-btn`, `.pt-studio-canvas-divider-v`, `.pt-studio-canvas-dropzone`, `.pt-studio-canvas-drag-overlay` are properly scoped, distinct from existing `.pt-studio-canvas-divider` (⌘ glyph), and documented with a clarifying comment.
- **Test naming convention**: New test file `unit_studio_canvas_upload.test.tsx` uses the `unit_` prefix (AES103).
- **Null safety**: `handleDrop` guards `e.dataTransfer.files && e.dataTransfer.files.length > 0`; `handleFileInputChange` guards `e.target.files && e.target.files.length > 0`; `fileInputRef.current?.click()` uses optional chaining throughout.
- **Progress bar clamping** (`surface_studio_canvas_component.tsx:370`): `Math.max(0, Math.min(100, progress.percent))` correctly clamps `aria-valuenow`; only rendered when `activeRun` is true.
- **Keyboard accessibility**: Dropzone has `role="button"`, `tabIndex={0}`, and `onKeyDown` handling Enter/Space with `preventDefault`.

---

### Verdict

The implementation matches the PR-1 scope (upload button, empty-state dropzone, StudioLanding re-wiring) with no scope creep. `StudioCanvas` remains passive (callbacks only), the `e.target.value = ""` reset is correctly implemented, and the flicker-guard *syntax* is the right idiom. However, there are **6 findings**: 1 bug (drag-flicker guard ineffective because `DragEvent.relatedTarget` is null), 4 suggestions (no file-type validation on drop, two fragile test assertions around `preventDefault` and mocked `target`, dead UI in `StudioLayerPanel`), and 1 nit (duplicate `.pt-studio-canvas` CSS rule). The code is otherwise clean, well-typed, and follows project conventions.

**Review file**: `/home/raka/.agents/develop/psd-timelapse/execute/exec-review-598d57eb-pr-1-general.md`