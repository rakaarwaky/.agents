### Issue 1 -- Severity: bug
- **File**: `packages/studio/tests/unit_studio_layer_panel_component.test.tsx:49-60`
- **Description**: The test "renders real layer labels with synthetic ids and classification chips" asserts `screen.getByText("layer-0")` — this asserts the synthetic ID is rendered as visible text in the layer row. The `StudioLayerRow.id` is `layer-0` and the panel renders it in a `<span className="pt-studio-sidebar-layer-id">{layer.id}</span>` (line 303). The test passes because the ID is rendered, but the test **does not verify that the ID is used as a stable key for selection/visibility**. The more important assertion — that clicking a layer row calls `onSelectLayer` with the correct ID — is tested separately (line 137-145), but the visibility toggle test is missing entirely. The `toggleVisibility` function (line 111-120) is a core feature added in this PR (the `hiddenIds` state, the `hiddenLayerIds` helper, the `useEffect` re-sync) and has zero test coverage.
- **Suggestion**: Add a test that: (a) renders the panel with a layer having `visible: false`, (b) asserts the layer row has reduced opacity (or the `Ø` icon is shown), (c) clicks the visibility toggle button, (d) asserts the opacity/icon changes. This covers the `hiddenIds` state and the `toggleVisibility` handler, which are currently untested.
- **Status**: open

### Issue 2 -- Severity: bug
- **File**: `packages/studio/tests/unit_studio_layer_panel_component.test.tsx:72-81`
- **Description**: The fallback test renders the panel with `layers: undefined, fileMeta: undefined` and asserts the default caption and default layer labels. However, it does not test the **interaction between the fallback and the container**: when the container passes `layers` for the first time (after an inspect resolves), the `useEffect` at line 92-94 re-syncs `hiddenIds` and `activeLayerId`. The test does not cover this transition — rendering with no layers, then re-rendering with real layers, and verifying that `activeLayerId` moves from `"L4"` to `"layer-0"` and `hiddenIds` is recomputed. This is the exact scenario that Issue 9 in the general review flags as a re-render churn bug; a test would catch it.
- **Suggestion**: Add a test using `rerender` from `@testing-library/react`: render with `{ layers: undefined, fileMeta: undefined }`, then rerender with `{ layers: REAL_LAYERS, fileMeta: REAL_FILE_META }`, and assert the active layer and hidden state match the new layers.
- **Status**: open

### Issue 3 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_layer_panel_component.test.tsx:85-102`
- **Description**: The file-pick delegation test uses `fireEvent.drop` with a `dataTransfer: { files: [fakeFile] }` mock. The test asserts `onPickFile` is called with the file. This is good coverage for the drop path. However, the test does not cover the **drag-over visual state**: the panel has `isDragging` state that toggles `pt-studio-sidebar-dropzone-drag` class and changes the dropzone label to "Drop PSD file to inspect". A test should fire `dragOver` and assert the label/class change, then fire `dragLeave` and assert it reverts. This is a user-facing visual state with no test coverage.
- **Suggestion**: Add a test: fire `dragOver` on the dropzone, assert the label text changes to "Drop PSD file to inspect", fire `dragLeave`, assert the label reverts to "Click or drag new .PSD to replace".
- **Status**: open

### Issue 4 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_layer_panel_component.test.tsx:137-145`
- **Description**: The `onSelectLayer` test clicks the `layer-0` text span and asserts `onSelectLayer` is called with `"layer-0"`. However, the click handler is on the `<li>` (line 300: `onClick={() => handleSelect(layer.id)}`), not on the text span. The test passes because the click bubbles up from the span to the `<li>`. But the test does not verify that clicking the **visibility toggle button** (which calls `e.stopPropagation()` at line 112) does **not** trigger `onSelectLayer`. This is an important edge case: the visibility toggle must not select the layer. The `e.stopPropagation()` in `toggleVisibility` is the mechanism that prevents this, and it is untested.
- **Suggestion**: Add a test: click the visibility toggle button for `layer-1`, assert `onSelectLayer` is **not** called, and assert the `hiddenIds` state changes (the row opacity changes or the `Ø` icon appears).
- **Status**: open

### Issue 5 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_layer_panel_component.test.tsx:54-69`
- **Description**: The real-layer test asserts the file metadata line `"184.2 MB · RGB 16-bit · 3000 × 3000 · 2 layers"` is rendered. This is good coverage for the `metaLine` construction (line 104-109). However, it does not test the **partial metadata** case: when `fileMeta` has no `dimensions` or `layerCount` (which is the case when `selectedFile` is set but `inspectState.doc` is not — root_web_main_entry.ts:517-521). The `metaLine` uses `.filter(Boolean).join("")` which should handle this, but there is no test verifying that `dimensions` and `layerCount` are omitted when absent. This is the container's no-doc-but-file-selected branch.
- **Suggestion**: Add a test: render with `fileMeta: { name: "foo.psd", sizeLabel: "1.0 MB" }` (no dimensions, no layerCount), assert the meta line is exactly `"1.0 MB"` (no trailing separators).
- **Status**: open

### Issue 6 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_layer_panel_component.test.tsx:109-121`
- **Description**: The file-input change test fires `change` with `{ target: { files: [fakeFile] } }` and asserts `onPickFile` is called. However, the file input has `style={{ display: "none" }}` (line 167) and is triggered programmatically via `fileInputRef.current?.click()` (line 218). The test does not verify that clicking the dropzone triggers the file input click. This is the user-facing flow: user clicks the dropzone → file picker opens. The test only covers the `change` event, not the click-to-open mechanism.
- **Suggestion**: Add a test: render the panel, click the dropzone (the `role="button"` element), and assert that `fileInputRef.current.click()` was called (mock the ref or spy on `HTMLInputElement.prototype.click`). This is lower priority since the click-to-open pattern is standard.
- **Status**: open

### Issue 7 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_layer_panel_component.test.tsx:126-132`
- **Description**: The re-inspect test clicks the refresh button and asserts `onReinspect` is called. The `handleReset` function (line 149-154) also resets `searchQuery`, `hiddenIds`, and `activeLayerId`. The test does not verify these resets. Specifically, it does not test that: (a) the search query is cleared, (b) `hiddenIds` is recomputed from the `layers` prop, (c) `activeLayerId` resets to the first layer. These are the side effects of `handleReset` that are not just delegating to `onReinspect`.
- **Suggestion**: Add a test that sets a search query (type in the search input), clicks the refresh button, and asserts the search input is cleared. Also set a layer as hidden (click the visibility toggle) and assert the hidden state is reset after refresh.
- **Status**: open

### Issue 8 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_layer_panel_component.test.tsx`
- **Description**: There are no tests for the **search/filter** functionality. The panel has a search input (line 262-274) that filters layers by label (`filteredLayers = rawLayers.filter((l) => l.label.toLowerCase().includes(searchQuery.trim().toLowerCase()))` at line 98-100). The "No layers matching" empty state (line 348-358) is also untested. The search is a user-facing feature that is core to the layer panel.
- **Suggestion**: Add tests: (a) type in the search input and assert the layer list is filtered, (b) type a query that matches no layers and assert the "No layers matching" message appears, (c) click the clear button (✕) and assert the search input is cleared and all layers are shown again.
- **Status**: open

### Issue 9 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_layer_panel_component.test.tsx:63-68`
- **Description**: The real-metadata test asserts the layer count badge shows `"2"` (the number of real layers). The layer count badge is at line 256-258: `<span className="pt-studio-sidebar-layers-count">{filteredLayers.length}</span>`. The test asserts `filteredLayers.length` (which equals `rawLayers.length` when no search query is active). However, the test does not verify that the badge updates when a search filter is applied (i.e., `filteredLayers.length` should be less than `rawLayers.length` when a search query is active). This is a minor coverage gap but the badge is a real UI element.
- **Suggestion**: Add a test: type a search query that matches only one layer, assert the count badge shows `"1"`.
- **Status**: open

### Issue 10 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_layer_panel_component.test.tsx:1-6`
- **Description**: The test file has no tests for the `StudioCanvas` component's new `runId`/`progress` props and the `activeRun`/`isRendering`/`renderNotification` logic (lines 40-48 of `surface_studio_canvas_component.tsx`). The canvas has significant new logic: the `activeRun` computation, the `isRendering` ternary, the `renderNotification` ternary with completion detection, the `handleRenderClick` guard, the `handlePreviewClick` guards, and the `useEffect` that sets `hasRendered` on completion. None of this is tested. The PR's summary explicitly mentions "Update StudioCanvas with runId and progress props for real pipeline telemetry" — this is new logic that needs test coverage.
- **Suggestion**: Create a new test file `packages/studio/tests/unit_studio_canvas_component.test.tsx` covering: (a) render click with no active run calls `onRender`, (b) render click with active run in progress is blocked, (c) render click with active run in terminal state starts a new render (this would catch Issue 2 in the general review), (d) preview click during active run shows "Rendering in progress" (this would catch Issue 3 in the general review), (e) preview click after completion opens the modal, (f) progress bar is rendered with correct `aria-valuenow` and `aria-valuetext`.
- **Status**: open

### Issue 11 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_layer_panel_component.test.tsx`
- **Description**: There are no tests for the `StudioLanding` composition component. `StudioLanding` is the root passive surface that composes `StudioCanvas` and `StudioLayerPanel` and forwards props. While it is a thin wrapper, it has a new `StudioLandingProgress` interface and forwards `onPickFile`, `onSelectLayer`, `onReinspect`, `onRender`, `layers`, `fileMeta`, `runId`, `progress`. A test should verify that `StudioLanding` forwards these props to the child components. This is lower priority since the composition is straightforward, but it is part of the PR's new code.
- **Suggestion**: Add a test file `packages/studio/tests/unit_studio_landing_component.test.tsx` that renders `StudioLanding` with mock callbacks and asserts they are forwarded to the correct child components. This can be done by spying on `StudioCanvas` and `StudioLayerPanel` via module mocks.
- **Status**: open

### Issue 12 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_layer_panel_component.test.tsx:85-102`
- **Description**: The drop test uses `fireEvent.drop` with a `dataTransfer` mock that has a `files` array. However, the `handleDrop` function (line 134-141) checks `e.dataTransfer.files && e.dataTransfer.files.length > 0` and then calls `processFile(e.dataTransfer.files[0])`. The test covers the happy path (one file dropped). It does not cover the **empty drop** case (dropping something that is not a file, e.g. text or a URL, where `dataTransfer.files` is empty). The `handleDrop` function silently does nothing in this case (no error, no feedback), which is a UX gap but also an untested path.
- **Suggestion**: Add a test: fire `drop` with `dataTransfer: { files: [] }` (or no files), assert `onPickFile` is **not** called and no error is thrown.
- **Status**: open

### Issue 13 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_layer_panel_component.test.tsx:43-45`
- **Description**: The `renderPanel` helper uses `Partial<Parameters<typeof StudioLayerPanel>[0]>` for the props type. This is a clever TypeScript pattern, but it means the test file does not explicitly type the props. If the `StudioLayerPanelProps` interface changes (e.g. a new required prop is added), the test file will not catch it at compile time — the `Partial` makes all props optional. This is a minor type-safety gap.
- **Suggestion**: Either define the base props explicitly (e.g. `const base: StudioLayerPanelProps = { layers: REAL_LAYERS, fileMeta: REAL_FILE_META }`) or use `Required<Pick<StudioLayerPanelProps, "layers" | "fileMeta">> & Partial<StudioLayerPanelProps>` for the helper parameter type.
- **Status**: open

### Issue 14 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_layer_panel_component.test.tsx:95-97`
- **Description**: The test asserts `onPickFile` is called with `fakeFile` (the exact same `File` object). This is good — it verifies the file object is passed through, not reconstructed. However, the test does not verify that the container's `handlePickFile` (root_web_main_entry.ts:463-469) uses `file.name` as the server path. The container sets `setServerPath(file.name)` and calls `executeInspect(file.name)`. The test only covers the panel's delegation, not the container's handling. This is a gap in the end-to-end flow: the panel calls `onPickFile`, but what happens next (the container's `executeInspect` call) is untested.
- **Suggestion**: Add a test for `StudioContainer` (in a new file or in the existing test file) that mocks the client, calls `handlePickFile` with a `File`, and asserts `client.inspectFull` is called with `file.name`. This is the critical integration point for the PR.
- **Status**: open

### Issue 15 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_layer_panel_component.test.tsx:107-121`
- **Description**: The file-input change test fires `change` with `{ target: { files: [fakeFile] } }`. However, the `handleFileInputChange` function (line 143-146) reads `e.target.files` and calls `processFile(e.target.files[0])`. The test covers the happy path (one file selected). It does not cover the case where the user cancels the file picker (e.g. `files` is empty or `null`). The `handleFileInputChange` function silently does nothing in this case, which is correct behavior, but untested.
- **Suggestion**: Add a test: fire `change` with `{ target: { files: [] } }`, assert `onPickFile` is **not** called.
- **Status**: open

### Issue 16 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_layer_panel_component.test.tsx:15-32`
- **Description**: The `REAL_LAYERS` fixture has one layer with `visible: true` and one with `visible: false`. The `REAL_FILE_META` has `dimensions: "3000 × 3000"` and `layerCount: 2`. These are good fixtures. However, the test does not cover the case where `classification` is absent (i.e. `undefined`). The `StudioLayerRow.classification` is optional (`classification?: string`), and the panel conditionally renders the classification chip (`layer.classification ? <span>...</span> : null` at line 305-319). A test should verify that when `classification` is `undefined`, no chip is rendered. The `REAL_LAYERS` fixture always provides a classification.
- **Suggestion**: Add a test: render with a layer that has `classification: undefined`, assert the classification chip is not rendered for that layer.
- **Status**: open

---

**0 bugs, 16 suggestions, 0 nits — changes required**