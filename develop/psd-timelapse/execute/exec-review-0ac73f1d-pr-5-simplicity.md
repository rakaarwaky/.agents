### Issue 1 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:359-375`
- **Description**: The `setCompleted` updater inside the `listCompletedRuns` effect performs three responsibilities: deduplication by `id`, calling `saveCompletedRuns` with a field-mapping literal, and returning the merged array. The serialization object literal `{ id: c.id, outputPath: c.outputPath ?? null, sizeBytes: c.sizeBytes ?? null, durationSeconds: c.durationSeconds }` appears identically in two places (line 362 and line 399), violating DRY.
- **Suggestion**: Extract a `serializeCompletedItem(c: CompletedItem)` helper and use it in both call sites. Optionally extract a `mergeCompletedLists(prev, serverItems)` pure helper so the merge logic is testable in isolation.
- **Status**: open

### Issue 2 -- Severity: nit
- **File**: `packages/root_web_main_entry.ts:329-343`
- **Description**: The `loadCompletedRuns().map(...)` initialization maps the localStorage shape to `CompletedItem`. The field mapping (`r.outputPath ?? undefined`, `r.sizeBytes ?? undefined`, `r.durationSeconds ?? 0`) duplicates the inverse of the serialization done in `saveCompletedRuns`. This round-trip mapping logic (load → map → save → map) is a common source of drift.
- **Suggestion**: Define a single `completedItemFromStorage(r)` and `completedItemToStorage(c)` pair and use them on all boundaries.
- **Status**: open

### Issue 3 -- Severity: nit
- **File**: `packages/root_web_main_entry.ts:308`
- **Description**: `saveCompletedRuns` wraps localStorage access in try/catch with `// ignore`, mirroring `clearActiveRun` (line 289). Three separate localStorage helpers (`loadActiveRun`, `clearActiveRun`, `loadCompletedRuns`, `saveCompletedRuns`) each repeat the same `typeof window !== "undefined" && window.localStorage` guard and try/catch pattern.
- **Suggestion**: Extract a small `safeLocalStorage<T>(fn)` wrapper to eliminate the repeated guard and catch scaffolding.
- **Status**: open

### Issue 4 -- Severity: nit
- **File**: `packages/root_web_main_entry.ts:439-449`
- **Description**: `handleDownload` builds and clicks an anchor element inline. The object-URL + click + revoke pattern is a standard web idiom but lives inline in the component, making the component longer and the download mechanics untestable without rendering.
- **Suggestion**: Extract a `triggerDownload(blob, filename)` helper outside the component for clarity and testability.
- **Status**: open

### Issue 5 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:390-394`
- **Description**: The on-complete `CompletedItem` hardcodes `inputPath: ""` and `durationSeconds: 0`. The `inputPath` is not recoverable from `RenderOutputMetaVO` in the closure without the `activeRunId` (which is available but unused for path resolution). Empty `inputPath` means the completed card shows an empty filename via `basename("")` → `""`.
- **Suggestion**: Capture the input path when the render starts (or derive it from the run handle) so the completed item has a meaningful filename. This is a correctness/UX gap more than dead code, but worth noting here for the empty-string artifact.
- **Status**: open

### Issue 6 -- Severity: nit
- **File**: `packages/root_web_main_entry.ts:390-396`
- **Description**: The on-complete handler creates `item` with `outputPath: meta.video_path ?? undefined` (server file path) while `CompletedCard` only uses `outputPath` as an "is download enabled" boolean. The actual value is never read for download (download uses `item.id`).
- **Suggestion**: If the path is genuinely unused for download, store `outputPath: undefined` and drive the button purely off a dedicated `downloadable: boolean` field, or keep as-is with a comment clarifying that the value is display-only metadata.
- **Status**: open

### Issue 7 -- Severity: nit
- **File**: `packages/root_web_main_entry.ts:390-396`
- **Description**: `onComplete` handler and the `handleCancel` method (line 428-433) both reset `setActiveRunId(null); clearActiveRun(); setCurrentStage(null); setCurrentPercent(0);` — the same 4-line teardown sequence duplicated.
- **Suggestion**: Extract a `resetActiveRun()` function to avoid the duplication.
- **Status**: open

## Verdict

0 bugs, 1 suggestion, 6 nits — changes required.