### Issue 1 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:533-666`
- **Description**: The `StudioContainer` builds a server-path bar with ~130 lines of inline `createElement` calls (label, input, inspect button, error span, ready span). Each element has 10-15 style properties inline. This is the most verbose part of the PR — the JSX could be written as a separate `<StudioServerPathBar>` component or extracted to a `.tsx` file with a proper `return (<div>...</div>)`. The inline `createElement` pattern in a `.ts` file (not `.tsx`) is a deliberate choice to avoid adding JSX to a `.ts` file, but the result is hard to read and maintain. The `root_web_main_entry.ts` is already 900+ lines and this PR adds 304 more.
- **Suggestion**: Extract the server-path bar into a small `StudioServerPathBar` component in `packages/studio/src/` or `packages/root_web_main_entry.ts` using a `.tsx` sub-file. This would reduce the `StudioContainer` function by ~100 lines and improve readability. Alternatively, accept the verbosity as a trade-off for keeping the container in a `.ts` file (which is the existing convention in this codebase).
- **Status**: open

### Issue 2 -- Severity: suggestion
- **File**: `packages/studio/src/surface_studio_canvas_component.tsx:40-48`
- **Description**: The `activeRun`, `isRendering`, and `renderNotification` computations are derived state that is recomputed on every render. The `renderNotification` ternary is particularly complex (nested ternary with `progress.percent >= 100 || progress.stage === "completed"`). This logic is duplicated in the `handlePreviewClick` guard (line 72-74) and the `useEffect` at line 87-91. The completion check (`progress.percent >= 100 || progress.stage === "completed"`) appears 3 times in the file (lines 45, 74, 88). This is a minor DRY violation.
- **Suggestion**: Extract a `const isComplete = activeRun && (progress.percent >= 100 || progress.stage === "completed");` helper and reuse it in the three places. This is a nit-level improvement but would make the logic easier to follow and test.
- **Status**: open

### Issue 3 -- Severity: suggestion
- **File**: `packages/studio/src/surface_studio_layer_panel_component.tsx:65-68`
- **Description**: The `hiddenLayerIds` helper is a one-liner that filters and maps to a `Set`. It is used in two places: the initial state (line 86-88) and the `useEffect` (line 93) and `handleReset` (line 151). The helper is fine, but the `new Set(...)` wrapper is slightly verbose. The `hiddenLayerIds` function could be inlined as `new Set((layers ?? []).filter(l => !l.visible).map(l => l.id))` in the three places, but the helper is arguably cleaner. This is a nit — the helper is fine as-is.
- **Suggestion**: No change needed. The helper is clean and reduces duplication.
- **Status**: open

### Issue 4 -- Severity: suggestion
- **File**: `packages/studio/src/surface_studio_layer_panel_component.tsx:92-94`
- **Description**: The `useEffect` that re-syncs `hiddenIds` and `activeLayerId` on `[layers]` prop change is a reactive synchronization pattern. The effect is necessary because the component holds local state (`hiddenIds`, `activeLayerId`) that must be reset when the `layers` prop changes. However, this is a code smell: the component is duplicating state that could be derived. The `hiddenIds` could be a `Set` that is always derived from `layers` (via `useMemo`), and the `activeLayerId` could be a `useState` that is reset via a `key` prop or a `useRef` comparison. The current pattern works but adds a re-render cycle (the effect runs after render, causing a second render with the updated state).
- **Suggestion**: Consider deriving `hiddenIds` with `useMemo(() => hiddenLayerIds(layers ?? []), [layers])` and using a `useRef` to track the previous `layers` for the `activeLayerId` reset. This would eliminate the extra render cycle. However, the current approach is correct and the performance impact is negligible for a panel with ~10-50 layers.
- **Status**: open

### Issue 5 -- Severity: suggestion
- **File**: `packages/studio/src/surface_studio_canvas_component.tsx:426`
- **Description**: The preview modal's `<video>` element uses a Google demo video URL. This is pre-existing code (not part of this PR's diff), but the PR adds logic to enable the Preview button after a real render completes. The PR's scope is "Studio PSD inspection integration" — the preview video is out of scope for PR 3 (it is likely addressed in PR 4 or later). However, the PR does not add a `TODO` comment or annotation to document this. The hard-coded URL is a code smell that will confuse future readers.
- **Suggestion**: Add a `// TODO(pr-4): replace demo video with real render output` comment above the `<video>` element. This is a documentation nit, not a code change.
- **Status**: open

### Issue 6 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:498-503`
- **Description**: The layer mapping `inspectState.doc.layers.map((layer, index) => ({ id: \`layer-${index}\`, ... }))` creates a new array on every render. The `StudioContainer` re-renders on every progress update (lines 412-430), so the `layers` array is recreated ~60 times during a render. This causes the `StudioLayerPanel`'s `useEffect` (line 92-94) to fire on every progress tick, resetting `activeLayerId` and `hiddenIds`. This is a performance issue and a correctness issue (Issue 9 in the general review).
- **Suggestion**: Wrap the layer mapping in `useMemo(() => inspectState.doc ? inspectState.doc.layers.map(...) : undefined, [inspectState.doc])`. This is a one-line change that eliminates the re-render churn.
- **Status**: open

### Issue 7 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:525-527`
- **Description**: The `progress` object is created inline: `const progress = activeRunId ? { percent: currentPercent, stage: currentStage } : null;`. This creates a new object reference on every render, causing the `StudioCanvas`'s `useEffect` (line 87-91) to re-run on every render. This is a minor performance issue but exacerbates the re-render churn from Issue 6.
- **Suggestion**: Wrap in `useMemo`: `const progress = useMemo(() => activeRunId ? { percent: currentPercent, stage: currentStage } : null, [activeRunId, currentPercent, currentStage])`.
- **Status**: open

### Issue 8 -- Severity: suggestion
- **File**: `packages/studio/src/surface_studio_canvas_component.tsx:55-69`
- **Description**: The `handleRenderClick` and `handlePreviewClick` functions have inline logic that is hard to read. The `handleRenderClick` has a guard, a callback, a conditional notification, and a state reset. The `handlePreviewClick` has two guards and a modal open. These could be simplified by extracting the guard conditions into named variables.
- **Suggestion**: Extract the guard conditions: `const canRender = !activeRun || !isRendering;` and `const canPreview = !activeRun || isRendering || hasRendered || (progress.percent >= 100 || progress.stage === "completed");`. This would make the functions more readable and testable. This is a nit-level improvement.
- **Status**: open

### Issue 9 -- Severity: suggestion
- **File**: `packages/studio/src/surface_studio_layer_panel_component.tsx:107-109`
- **Description**: The `metaLine` construction uses `.filter(Boolean).join("")` to concatenate optional parts. This is a clean pattern, but the `""` join separator means the parts are concatenated with no separator between them (the separators are embedded in the template strings: ` · ${meta.dimensions}`, ` · ${meta.layerCount} layers`). This works but is slightly fragile — if someone adds a new optional part without the ` · ` prefix, the output will be malformed.
- **Suggestion**: Use a more explicit join: `const parts = [meta.sizeLabel, meta.dimensions ? \` · ${meta.dimensions}\` : "", meta.layerCount != null ? \` · ${meta.layerCount} layers\` : ""]; const metaLine = parts.filter(Boolean).join("");`. This is functionally identical but more readable. Nit-level.
- **Status**: open

### Issue 10 -- Severity: suggestion
- **File**: `packages/studio/src/surface_studio_layer_panel_component.tsx:189-191`
- **Description**: The file name truncation `meta.name.length > 30 ? \`${meta.name.slice(0, 27)}...\` : meta.name` is a common pattern but the magic numbers `30` and `27` are hard-coded. The `27` is `30 - 3` (to account for the `...` suffix). This is a minor readability issue.
- **Suggestion**: Extract the constants: `const MAX_NAME_LEN = 30; const ELLIPSIS = "...";` and use `meta.name.length > MAX_NAME_LEN ? \`${meta.name.slice(0, MAX_NAME_LEN - ELLIPSIS.length)}${ELLIPSIS}\` : meta.name`. Nit-level.
- **Status**: open

### Issue 11 -- Severity: suggestion
- **File**: `packages/studio/src/surface_studio_canvas_component.tsx:191-192`
- **Description**: The canvas still has a hard-coded `CANVAS PREVIEW · 3000 × 3000 PX` chip (line 192). The PR maps real dimensions to `fileMeta.dimensions` but the canvas does not consume them. This is a missed integration, but also a code smell: the canvas has a hard-coded string that should be a prop. The PR's scope is "Studio PSD inspection integration" — the canvas dimensions are part of the inspection data.
- **Suggestion**: Pass `fileMeta?.dimensions` to `StudioCanvas` as a `dimensions?: string` prop and render it in the chip: `CANVAS PREVIEW · ${dimensions ?? "3000 × 3000"} PX`. This is a scope expansion but aligns with the PR's goal.
- **Status**: open

### Issue 12 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:405-407`
- **Description**: The `inspectState` initial value is `{ status: "idle" }`. The `InspectState` interface has `doc?: InspectFullVO` and `error?: Error` as optional fields. The `status: "idle"` state has neither `doc` nor `error`, which is correct. However, the `status: "error"` state sets `error` but not `doc`, and the `status: "ready"` state sets `doc` but not `error`. This is a discriminated union pattern, but it is not enforced by TypeScript (the interface allows any combination). This is a minor type-safety gap.
- **Suggestion**: Use a discriminated union: `type InspectState = { status: "idle" } | { status: "loading" } | { status: "error"; error: Error } | { status: "ready"; doc: InspectFullVO }`. This would enforce the invariant at compile time. Nit-level.
- **Status**: open

### Issue 13 -- Severity: suggestion
- **File**: `packages/studio/src/surface_studio_layer_panel_component.tsx:155-218`
- **Description**: The dropzone `<div>` has a `role="button"` and `tabIndex={0}` with `onKeyDown` for Enter/Space (line 218-223). This is correct for accessibility. However, the dropzone also has `onClick={() => fileInputRef.current?.click()}` (line 218). When the user presses Enter or Space, both the `onKeyDown` and the `onClick` may fire (since pressing Enter on a `role="button"` element triggers a click in some browsers). This could cause the file picker to open twice. The `onKeyDown` should `preventDefault` or the `onClick` should be removed in favor of the keyboard handler.
- **Suggestion**: Add `e.preventDefault()` in the `onKeyDown` handler, or remove the `onClick` and rely on the `onKeyDown` for keyboard activation. This is a minor accessibility nit.
- **Status**: open

### Issue 14 -- Severity: suggestion
- **File**: `packages/studio/src/surface_studio_canvas_component.tsx:110-150`
- **Description**: The zoom toolbar has a `⌘` character (line 149) as a visual separator. This is a macOS-specific symbol that may not render correctly on Windows/Linux. The `⌘` character is the "Place of Interest Sign" and is commonly used as a command-key symbol on macOS. On Windows/Linux, it may render as a tofu box or be confusing.
- **Suggestion**: Replace `⌘` with a more platform-neutral separator (e.g. `|` or `·`) or remove it. Nit-level.
- **Status**: open

### Issue 15 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:588-591`
- **Description**: The `onKeyDown` handler on the server path input calls `handleReinspect()` when Enter is pressed. The `handleReinspect` function checks `if (serverPath.trim())` and calls `executeInspect(serverPath)`. If the path is empty, nothing happens. This is correct, but the user gets no feedback (no error message) when they press Enter with an empty path. The `executeInspect` function does set an error state for empty paths (line 441), but `handleReinspect` guards against calling `executeInspect` with an empty path, so the error state is never set in this path.
- **Suggestion**: Either remove the `if (serverPath.trim())` guard in `handleReinspect` and let `executeInspect` handle the empty case (which sets an error state), or add an inline check that sets the error state. The current behavior is silent — the user presses Enter and nothing happens.
- **Status**: open

---

**0 bugs, 15 suggestions, 0 nits — changes required**