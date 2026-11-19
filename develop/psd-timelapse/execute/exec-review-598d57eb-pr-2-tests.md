# Review Findings: pr-2 Tests

**PR:** Strip sidebar to layers-only and update sidebar tests
**Scope:** Test coverage / quality review only (no code style, naming, or architecture)
**Source files:**
- `/home/raka/orca/workspaces/psd-timelapse/plan-doc-14c3b92a/packages/studio/tests/unit_studio_layer_panel_component.test.tsx`
- `/home/raka/orca/workspaces/psd-timelapse/plan-doc-14c3b92a/packages/studio/src/surface_studio_layer_panel_component.tsx`
- `/home/raka/orca/workspaces/psd-timelapse/plan-doc-14c3b92a/packages/studio/tests/unit_studio_canvas_upload.test.tsx`
- `/home/raka/orca/workspaces/psd-timelapse/plan-doc-14c3b92a/packages/studio/src/surface_studio_landing_component.tsx`
- `/home/raka/orca/workspaces/psd-timelapse/plan-doc-14c3b92a/packages/root_web_smart_container.ts`

Test result: `vitest run studio/` → **43 passed** (all 6 layer-panel + 19 canvas-upload + 18 render-wiring). `tsc --noEmit` clean.

---

| Severity | File | Description | Suggestion | Status |
|----------|------|-------------|------------|--------|
| bug | `packages/studio/tests/unit_studio_layer_panel_component.test.tsx` | The fallback test uses `renderPanel({ layers: undefined })` but does not pass `layers: undefined` explicitly in `base` — instead it passes `undefined` into `Partial`. Because `renderPanel` spreads `{ layers: REAL_LAYERS, ...props }`, `layers: undefined` overrides the default and triggers fallback to `DEFAULT_LAYERS`. This works, but the `utils.unmount()` call is present while other tests that render the same component do not unmount, leaving potential DOM leakage across tests in the same file. | Remove `utils.unmount()` for symmetry, or add `unmount()`/`cleanup()` to every test for consistent isolation. | open |
| suggestion | `packages/studio/tests/unit_studio_layer_panel_component.test.tsx` | The visibility-toggle test (`toggles layer visibility when the visibility button is clicked`) only verifies the visible→hidden direction (opacity 0.4). It does not verify the toggle-back direction (hidden→visible) nor that clicking the visibility button does **not** trigger `onSelectLayer` (the `toggleVisibility` handler calls `e.stopPropagation()`). | Add a second click asserting opacity returns to `1`, and/or assert that `onSelectLayer` spy was not called when the visibility button is clicked. | open |
| suggestion | `packages/studio/tests/unit_studio_layer_panel_component.test.tsx` | `activeLayerId` state and the `pt-studio-sidebar-layer-active` class (component line 166–168) are never asserted visually. Only the `onSelectLayer` callback is spied on. | Add an assertion that clicking a layer row applies `pt-studio-sidebar-layer-active` to that row (or that the active class moves from row to row on successive clicks). | open |
| suggestion | `packages/studio/tests/unit_studio_layer_panel_component.test.tsx` | The "Clear layer search" button (component line 143–157) and its `aria-label="Clear layer search"` are rendered but never exercised by a test. | Add a test: enter a search query, then click the clear button, assert the full layer list is restored and the clear button is removed from the DOM. | open |
| suggestion | `packages/studio/tests/unit_studio_layer_panel_component.test.tsx` | The search-empty-state test asserts `/No layers matching/` but does not assert the matched query text appears inside the message (component line 230: `No layers matching &quot;{searchQuery}&quot;`). | Assert the rendered message includes the actual query, e.g. `getByText(/No layers matching "nonexistent"/)`. | open |
| nit | `packages/studio/tests/unit_studio_layer_panel_component.test.tsx` | File ends without a trailing newline (`\ No newline at end of file` in diff). | Add trailing newline. | open |
| suggestion | `packages/studio/tests/unit_studio_layer_panel_component.test.tsx` | The fallback test asserts `screen.getByText("10")` for the layer count badge. This is a numeric assertion that could match other "10" text on the page if the component ever grows more UI. It is currently safe because the only other numeric content is layer IDs ("L1"–"L10"), which are not bare "10". | Change to `screen.getByText("LAYERS")` vicinity or assert the count within the `.pt-studio-sidebar-layers-count` container for tighter scoping. | open |
| bug | `packages/studio/tests/unit_studio_canvas_upload.test.tsx` | Import line 11: `import type { StudioFileMeta } from "../src/surface_studio_layer_panel_component";`. This re-export chain (`StudioFileMeta` defined in layer-panel, re-exported through landing) is intact per `root_web_smart_container.ts`, but `StudioLayerPanelProps` no longer includes `fileMeta`, so any caller that still passes `fileMeta` to `StudioLayerPanel` directly would be a type error. No such caller exists — smart container passes props to `StudioLanding`, which forwards `fileMeta` to `StudioCanvas`, not `StudioLayerPanel`. Verified via grep: no direct `StudioLayerPanel` caller passes `fileMeta`. | No action needed — verified safe. Document as confirmed-closed. | open |
| nit | `packages/studio/tests/unit_studio_canvas_upload.test.tsx` | The docstring (line 3) says "dynamic canvas chip with fileMeta" — accurate. No stale references to removed layer-panel DOM (`studio-file-input`, `Drop PSD file or click to browse`, `Refresh PSD document`, `studio-sidebar-header`, `studio-sidebar-file`, `studio-sidebar-dropzone`) found in any test file. | No action needed. | open |

---

## Focus Area 1: Updated test file covers remaining layers functionality

**DEFAULT_LAYERS fallback** — Covered by `StudioLayerPanel — fallback when props absent` (renders `Base Fabric Body Silhouette` and count badge `10`). Confirmed passing. Edge case: the fallback default `activeLayerId` ("L4") when `layers` is undefined is not visually asserted, and `useEffect` re-sync on `layers` change is not tested at all (no test swaps `layers` prop after initial render).

**Visibility toggle** — Covered by `toggles layer visibility when the visibility button is clicked`. Only verifies visible→hidden (opacity 0.4); toggle-back and stopPropagation not tested (see suggestions above).

**Search** — Covered by `filters layers by search query` (case-insensitive substring match; `Collar` shows, `Chest Graphic` hidden) and `shows empty state message when search matches nothing`. Empty-state query interpolation not asserted (see suggestion).

**Select** — Covered by `invokes onSelectLayer when a layer row is clicked` (spy assertion on `layer-0`). Visual active-state not asserted (see suggestion).

## Focus Area 2: Removed tests are not still referenced

Confirmed. Grep across `packages/` for `studio-file-input`, `Drop PSD file or click to browse`, `Refresh PSD document`, `DEFAULT_FILE_META`, `REAL_FILE_META`, `onReinspect`, `studio-sidebar-header`, `studio-sidebar-file`, `studio-sidebar-dropzone`, `Source PSD document` returns **zero** matches in `packages/studio/tests/`. The upload/dropzone/reinspect behavior now lives in `unit_studio_canvas_upload.test.tsx` (19 tests, all passing), which is the correct location per the PR summary. No stale imports (`StudioFileMeta` type import removed from layer-panel test; `StudioFileMeta` still imported by canvas-upload test and landing component, which is correct).

## Focus Area 3: renderPanel helper correctly omits fileMeta/onPickFile/onReinspect

Confirmed. `renderPanel` base object is `{ layers: REAL_LAYERS, ...props }` (line 31–35). It no longer includes `fileMeta`, `onPickFile`, or `onReinspect`. `StudioLayerPanelProps` no longer declares those fields (component lines 33–36), so passing them would be a type error — verified by clean `tsc --noEmit`. No test in the layer-panel file references `fileMeta`, `onPickFile`, or `onReinspect` (grep returned only `renderPanel` calls).

---

**Summary:** The test updates correctly reflect the layers-only sidebar. All tests pass and type-check clean. The main gaps are in edge-case depth (toggle-back, stopPropagation, active visual state, clear-search button, search-empty query interpolation) and minor test hygiene (trailing newline, consistent unmount). No removed functionality is still referenced anywhere.
