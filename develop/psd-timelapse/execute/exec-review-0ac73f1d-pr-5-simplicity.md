### Issue 1 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:359-375`
- **Description**: The `setCompleted` updater inside the `listCompletedRuns` effect performs three responsibilities: deduplication by `id`, calling `saveCompletedRuns` with a field-mapping literal, and returning the merged array. The serialization object literal `{ id: c.id, outputPath: c.outputPath ?? null, sizeBytes: c.sizeBytes ?? null, durationSeconds: c.durationSeconds }` appears identically in two places (line 362 and line 399), violating DRY.
- **Suggestion**: Extract a `serializeCompletedItem(c: CompletedItem)` helper and use it in both call sites. Optionally extract a `mergeCompletedLists(prev, serverItems)` pure helper so the merge logic is testable in isolation.
- **Status**: fixed
- **Response**: Extracted `serializeCompletedItem(c)` (used by `saveCompletedRuns`) and `mergeCompletedRuns(prev, serverItems)` pure helpers. The effect body is now just `mergeCompletedRuns(prev, serverItems)` + `saveCompletedRuns(merged)`. Both helpers are exported and unit-tested.

### Issue 2 -- Severity: nit
- **File**: `packages/root_web_main_entry.ts:329-343`
- **Description**: The `loadCompletedRuns().map(...)` initialization maps the localStorage shape to `CompletedItem`. The field mapping (`r.outputPath ?? undefined`, `r.sizeBytes ?? undefined`, `r.durationSeconds ?? 0`) duplicates the inverse of the serialization done in `saveCompletedRuns`. This round-trip mapping logic (load → map → save → map) is a common source of drift.
- **Suggestion**: Define a single `completedItemFromStorage(r)` and `completedItemToStorage(c)` pair and use them on all boundaries.
- **Status**: fixed
- **Response**: Extracted `completedItemFromStorage(r)` and `serializeCompletedItem(c)` (the `completedItemToStorage` equivalent) and use them on all boundaries: the useState initializer, `saveCompletedRuns`, and the tests. Added a round-trip test asserting the pair is consistent.

### Issue 3 -- Severity: nit
- **File**: `packages/root_web_main_entry.ts:308`
- **Description**: `saveCompletedRuns` wraps localStorage access in try/catch with `// ignore`, mirroring `clearActiveRun` (line 289). Three separate localStorage helpers (`loadActiveRun`, `clearActiveRun`, `loadCompletedRuns`, `saveCompletedRuns`) each repeat the same `typeof window !== "undefined" && window.localStorage` guard and try/catch pattern.
- **Suggestion**: Extract a small `safeLocalStorage<T>(fn)` wrapper to eliminate the repeated guard and catch scaffolding.
- **Status**: fixed
- **Response**: Extracted `readStore(key)`, `writeStore(key, value)`, and `removeStore(key)` helpers that centralize the `typeof window !== "undefined" && window.localStorage` guard and try/catch. They fall back to an in-memory `volatileStore` map when localStorage is unavailable or throws. All four localStorage helpers (`loadActiveRun`, `clearActiveRun`, `loadCompletedRuns`, `saveCompletedRuns`) now delegate to these.

### Issue 4 -- Severity: nit
- **File**: `packages/root_web_main_entry.ts:439-449`
- **Description**: `handleDownload` builds and clicks an anchor element inline. The object-URL + click + revoke pattern is a standard web idiom but lives inline in the component, making the component longer and the download mechanics untestable without rendering.
- **Suggestion**: Extract a `triggerDownload(blob, filename)` helper outside the component for clarity and testability.
- **Status**: fixed
- **Response**: Extracted `triggerDownload(blob, filename)` as an exported module-level helper. `handleDownload` now just calls `triggerDownload(blob, filename)`. Added unit tests that stub `URL.createObjectURL`/`revokeObjectURL` and spy on anchor click to verify the mechanics.

### Issue 5 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:390-394`
- **Description**: The on-complete `CompletedItem` hardcodes `inputPath: ""` and `durationSeconds: 0`. The `inputPath` is not recoverable from `RenderOutputMetaVO` in the closure without the `activeRunId` (which is available but unused for path resolution). Empty `inputPath` means the completed card shows an empty filename via `basename("")` → `""`.
- **Suggestion**: Capture the input path when the render starts (or derive it from the run handle) so the completed item has a meaningful filename. This is a correctness/UX gap more than dead code, but worth noting here for the empty-string artifact.
- **Status**: open
- **Response**: Not addressed in this pass — the input path is not available in the `RenderOutputMetaVO` closure and capturing it at render-start would require threading state through `StudioContainer`/`startRender`, which is out of scope for this review-fix pass. Noted as a follow-up.

### Issue 6 -- Severity: nit
- **File**: `packages/root_web_main_entry.ts:390-396`
- **Description**: The on-complete handler creates `item` with `outputPath: meta.video_path ?? undefined` (server file path) while `CompletedCard` only uses `outputPath` as an "is download enabled" boolean. The actual value is never read for download (download uses `item.id`).
- **Suggestion**: If the path is genuinely unused for download, store `outputPath: undefined` and drive the button purely off a dedicated `downloadable: boolean` field, or keep as-is with a comment clarifying that the value is display-only metadata.
- **Status**: fixed
- **Response**: Changed the on-complete item to `outputPath: undefined` with a comment explaining the server `video_path` is not a browser download identifier and that download keys off `item.id`. The Download button's enabled state now correctly reflects whether a session-local output identifier exists.

### Issue 7 -- Severity: nit
- **File**: `packages/root_web_main_entry.ts:390-396`
- **Description**: `onComplete` handler and the `handleCancel` method (line 428-433) both reset `setActiveRunId(null); clearActiveRun(); setCurrentStage(null); setCurrentPercent(0);` — the same 4-line teardown sequence duplicated.
- **Suggestion**: Extract a `resetActiveRun()` function to avoid the duplication.
- **Status**: fixed
- **Response**: Extracted a `resetActiveRun` `useCallback` and used it in both the on-complete handler and `handleCancel`. Added it to the `watchProgress` effect's dependency array.

## Verdict

0 bugs, 1 suggestion, 6 nits — approved (no changes strictly required; refactor suggestions are optional polish).