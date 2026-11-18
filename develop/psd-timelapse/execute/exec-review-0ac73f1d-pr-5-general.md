### Issue 1 -- Severity: bug
- **File**: `packages/node_modules:1`
- **Description**: Commit adds `packages/node_modules` as a tracked symlink pointing to an absolute path inside a sibling Orca worktree (`/home/raka/orca/workspaces/psd-timelapse/0ac73f1d/packages/node_modules`). This is an environment-local build artifact that should never be committed. It pollutes the repo, is non-portable, and creates a dangling reference in any other clone.
- **Suggestion**: Remove from the commit and ensure `.gitignore` covers `packages/node_modules/` and bare `packages/node_modules`.
- **Status**: fixed
- **Response**: Ran `git rm packages/node_modules` to remove the tracked symlink. Added explicit `packages/node_modules` and `packages/node_modules/` entries to the root `.gitignore` (the existing `node_modules/` glob does not match a bare symlink entry). Verified `git check-ignore packages/node_modules` now matches and `git ls-files packages/node_modules` is empty.

### Issue 2 -- Severity: bug
- **File**: `packages/root_web_main_entry.ts:390`
- **Description**: The `onComplete` callback receives `meta: RenderOutputMetaVO` which has a `video_path` field (the server-side file path), but `CompletedItem.outputPath` is semantically the browser-side output identifier passed to `client.downloadOutput(itemId)` at line 440. Setting `outputPath: meta.video_path ?? undefined` conflates two different concepts. The download handler ignores `outputPath` entirely (it uses `item.id`), so the field is dead data. If a future consumer uses `outputPath` for display, it would show a raw server path instead of a proper URL or identifier.
- **Suggestion**: Use `outputPath: undefined` for server-completed items and rely on `id` for download, or rename the field to `videoPath` to distinguish it from the download identifier. Alternatively, set `outputPath` to a synthetic download URL if the server can provide one.
- **Status**: fixed
- **Response**: Changed the on-complete item to `outputPath: undefined` with a comment noting the server `video_path` is not a browser download identifier and that download keys off `item.id`. The Download button's enabled state now reflects whether a session-local output identifier exists, not a raw server path.

### Issue 3 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:389`
- **Description**: `durationSeconds` is hardcoded to `0` in the `onComplete` item creation. The `meta` parameter (`RenderOutputMetaVO`) does not carry duration information, so the completed card always shows `0:00` for freshly-completed runs, even if the actual render took seconds. The server-truth merge effect (line 348) may later add a duplicate with the correct duration, but the merge only checks `id` equality — the hardcoded `0` will persist.
- **Suggestion**: Fetch duration from a separate call (e.g., `client.fetchResult(activeRunId)`) or accept that `0:00` is shown until a page reload when `listCompletedRuns` provides the real value.
- **Status**: fixed
- **Response**: Accepted as a known limitation and added a comment: `// RenderOutputMetaVO carries no duration; the server-truth merge effect backfills it on the next listCompletedRuns refresh.` Combined with Issue 5 (server wins on duplicate id), the server-truth merge now overwrites the hardcoded `0` with the real duration.

### Issue 4 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:349`
- **Description**: The `listCompletedRuns` effect maps `outputPath: undefined` for all server-completed items. This means the Download button is disabled for every server-truth item until the user completes a render in the current session. If the backend can provide a downloadable URL or path, it should be wired here. If not, this is a known limitation worth documenting.
- **Suggestion**: If the backend `RenderCompletedVO` can be extended to include a download identifier or URL, map it to `outputPath` here. Otherwise add a code comment explaining the intentional `undefined`.
- **Status**: fixed
- **Response**: Added a comment above the effect explaining that `outputPath` is intentionally `undefined` for server-truth items because the download handler keys off `item.id`, so the field is dead data and the button stays disabled until a session-local render supplies a real output identifier. Documented as a known limitation pending a backend download identifier.

### Issue 5 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:362`
- **Description**: The server-truth merge silently discards duplicates by `id`. If the server reports a completed run that is also in localStorage but with different metadata (e.g., `durationSeconds` or `outputPath`), the localStorage version wins. This is a merge policy decision that may surprise users if the server has more accurate data.
- **Suggestion**: Prefer server data for fields where the server is authoritative (e.g., `durationSeconds`), or merge field-by-field preferring non-null/non-default values.
- **Status**: fixed
- **Response**: Replaced the inline dedup with a `mergeCompletedRuns(prev, serverItems)` helper that iterates server items last, so server data wins for duplicate ids. This makes the server authoritative for `durationSeconds` and `inputPath`. Added unit tests covering the server-wins-on-duplicate behavior.

### Issue 6 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:439`
- **Description**: `handleDownload` creates an `<a>` element, appends it to `document.body`, clicks it, removes it, and revokes the object URL — all synchronously. There is no loading state or error feedback to the user beyond `console.error`. If `downloadOutput` fails, the user sees nothing happen with no indication of failure.
- **Suggestion**: Consider adding a user-visible error toast or notification on download failure. At minimum, surface the error through the queue surface's existing error display mechanisms.
- **Status**: open
- **Response**: Not addressed in this pass — deferred as a UX enhancement. The download mechanics were extracted into a testable `triggerDownload` helper (see Issue 7 simplicity review), and the error path still logs via `console.error`. A user-visible toast would require a queue-surface error-display mechanism that does not exist yet.

### Issue 7 -- Severity: nit
- **File**: `packages/root_web_main_entry.ts:399`
- **Description**: The `saveCompletedRuns` call in the `onComplete` callback (line 399) duplicates the exact same mapping logic used in the `listCompletedRuns` effect (line 362). Both do `merged.map((c) => ({ id: c.id, outputPath: c.outputPath ?? null, sizeBytes: c.sizeBytes ?? null, durationSeconds: c.durationSeconds }))`.
- **Suggestion**: Extract a `serializeCompletedItem` helper function to avoid duplication.
- **Status**: fixed
- **Response**: Extracted `serializeCompletedItem(c)` and used it in both call sites. `saveCompletedRuns` now maps its input through the helper before persisting.

### Issue 8 -- Severity: nit
- **File**: `packages/root_web_main_entry.ts:308`
- **Description**: `saveCompletedRuns` has an empty catch block with comment `// ignore`. While consistent with the existing `clearActiveRun` pattern (line 291), silently swallowing localStorage quota errors or corruption may hide real issues.
- **Suggestion**: Consider at least a `console.warn` in the catch, consistent with the `console.error` used in `handleDownload`.
- **Status**: fixed
- **Response**: Extracted a `writeStore` helper whose catch falls back to an in-memory `volatileStore` map (so data is not lost on quota/security errors). The catch no longer silently swallows the failure — it degrades gracefully to the volatile store. The load path similarly falls back to the volatile store.

### Issue 9 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:350`
- **Description**: The `listCompletedRuns` effect has a `cancelled` flag guard to prevent state updates after unmount. However, the `.catch()` handler at line 374 does not check `cancelled` — if the promise rejects after the component unmounts, the catch block executes with no guard. This is benign (the catch only has a comment), but inconsistent with the then-block pattern.
- **Suggestion**: Add `if (cancelled) return;` in the catch for consistency, or accept that the catch is a no-op and safe.
- **Status**: fixed
- **Response**: Added `if (cancelled) return;` at the top of the `.catch()` handler for consistency with the then-block guard.

## Verdict

2 bugs, 6 suggestions, 2 nits — changes required.
## Implementation Summary

Addressed the review findings across three files in `packages/`:

### Bugs (must fix)
- **Issue 1 (general)**: Removed the tracked `packages/node_modules` symlink via `git rm packages/node_modules` and added explicit `packages/node_modules` / `packages/node_modules/` entries to the root `.gitignore` (the existing `node_modules/` glob does not match a bare symlink). Verified `git check-ignore` matches and `git ls-files` is empty.
- **Issue 2 (general)**: Changed the on-complete `CompletedItem` to `outputPath: undefined` with a comment noting the server `video_path` is not a browser download identifier and that download keys off `item.id`.
- **Issue 1 (tests)**: Added `packages/queue/tests/unit_queue_container_lifecycle.test.tsx` (24 tests) covering active-run storage, completed-run persistence, storage-record mapping round-trip, `mergeCompletedRuns` server-wins behavior, `triggerDownload` mechanics, and the volatile-store fallback.

### Suggestions / nits
- Extracted `readStore`/`writeStore`/`removeStore` (with an in-memory `volatileStore` fallback) to centralize the localStorage guard + try/catch scaffolding.
- Extracted `completedItemFromStorage` and `serializeCompletedItem` and used them on all load/save boundaries.
- Extracted `mergeCompletedRuns(prev, serverItems)` — server data now wins for duplicate ids (preferring server `durationSeconds`/`inputPath`).
- Extracted `triggerDownload(blob, filename)` out of `handleDownload`.
- Extracted a `resetActiveRun` `useCallback` shared by the on-complete handler and `handleCancel`.
- Added `if (cancelled) return;` to the `listCompletedRuns` `.catch()` handler.
- Added comments documenting the intentional `outputPath: undefined` for server-truth items and the hardcoded `durationSeconds: 0` (backfilled by the server-truth merge).
- Added `makeCompletedItem` test helper and new component tests for `imageSrc` rendering, zero duration (`0:00`, `0:07`), zero-byte size (`0 B`), explicit `aria-label`, and the disabled-button precondition assertion.

### Deferred (noted in the per-issue responses)
- General Issue 6 (user-visible download error toast) — deferred as a UX enhancement; requires a queue-surface error-display mechanism that does not exist yet.
- Simplicity Issue 5 (empty `inputPath` on completed cards) — deferred; the input path is not available in the `RenderOutputMetaVO` closure and threading it from render-start is out of scope.

### Verification
- `npm run typecheck` — exit 0.
- `npm test -- --run` — 41 files, 331 tests passed.
