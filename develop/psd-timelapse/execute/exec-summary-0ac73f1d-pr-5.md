# Exec Summary — PR 5: Queue live run lifecycle

## Changes

### `packages/root_web_main_entry.ts`

1. **Added `useCallback` import** from React (used for stable `handleDownload` reference).

2. **Added `saveCompletedRuns()` helper** — mirrors the existing `loadCompletedRuns()` reader, writing the completed-runs array back to `localStorage` under `pt-completed-runs`.

3. **Rewired `QueueContainer`** with three functional changes:
   - **`onDownload`**: Replaced `(_id) => undefined` with `handleDownload`, which calls `client.downloadOutput(itemId)`, creates a temporary object URL via `URL.createObjectURL(blob)`, triggers a browser download via a programmatic anchor click (`<a download>` pattern), then revokes the object URL.
   - **Completed list from server**: Added a `useEffect` that calls `client.listCompletedRuns()` on mount. Server-returned `RenderCompletedVO` items are merged into the existing `localStorage`-seeded completed list (deduped by `id`). The merged list is persisted back to `localStorage` via `saveCompletedRuns()`. Failures (server unavailable) are caught silently, keeping the `localStorage` cache as the offline fallback.
   - **`watchProgress` on-complete callback**: The previously empty `onComplete` callback now captures the `RenderOutputMetaVO`, constructs a `CompletedItem` (with `outputPath = meta.video_path`, `sizeBytes = meta.size_bytes`), appends it to the completed list (if not already present), persists to `localStorage`, and clears the active run state.

4. **`completed` state** changed from `const [completed]` (no setter) to `const [completed, setCompleted]` to support dynamic updates from both the server listing and the on-complete callback.

### `packages/queue/src/surface_queue_component.tsx`

No changes. The surface already has the correct prop contract (`onDownload?: (itemId: string) => void`, `CompletedItem.outputPath`, download button `disabled` when `outputPath === undefined`).

### `packages/queue/tests/unit_queue_component.test.tsx`

Added 3 new tests to the "completed section" describe block:
- **`invokes onDownload with itemId when Download is clicked`** — verifies the callback fires with the correct item ID.
- **`does not invoke onDownload when Download button is disabled`** — verifies disabled buttons (no `outputPath`) suppress the callback.
- (The existing `enables Download button when outputPath is provided` test was already present.)

## Validation

- `npm run typecheck` — passes clean (0 errors).
- `npm test -- --run` — 309 tests pass across 40 files (queue: 23 tests, up from 20).
