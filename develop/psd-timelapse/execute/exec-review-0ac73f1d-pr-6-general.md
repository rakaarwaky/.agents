### Issue 1 -- Severity: bug
- **File**: `packages/gallery/src/surface_gallery_component.tsx:535-546`
- **Description**: Modal does not display the video when opened for the first time due to prop-to-state desynchronization. When a user clicks play on an item, `handlePlayItem` invokes `onPlay(id)` and immediately copies `featured.videoUrl` or `found.videoUrl` into `activeModalItem` state. Because video URLs are resolved lazily via `downloadOutput`, `item.videoUrl` is `undefined` at the moment of click. When `downloadOutput` finishes and `GalleryContainer` updates `state.items` and `state.featured`, `GallerySurface` re-renders with the new props, but `activeModalItem` is not synchronized or updated. As a result, `VideoPlayerModal` remains indefinitely stuck on the placeholder preview (image + `play_circle` icon) and never renders the `<video>` element unless the user closes and reopens the modal.
- **Suggestion**: Derive `activeModalItem` reactively instead of duplicating item data in state. Store only `activeModalId: string | null` in `GallerySurface` state and derive the active item on each render: `const activeModalItem = activeModalId ? (featured?.id === activeModalId ? featured : recent.find((r) => r.id === activeModalId)) : null;`. When props update with the newly created `videoUrl`, the modal will immediately receive the URL and render `<video>`.
- **Status**: fixed
- **Response**: Replaced `activeModalItem` state with `activeModalId: string | null`. `activeModalItem` is now derived reactively on each render from `featured` and `recent` props. When `videoUrl` resolves lazily, the open modal receives the updated URL immediately.

### Issue 2 -- Severity: bug
- **File**: `packages/root_web_main_entry.ts:468-512`
- **Description**: Violation of key constraint: "Lazy object-URLs: create on play, revoke on close. Bounds blob memory to 2 concurrent." `GalleryContainer` generates object-URLs on play, but never revokes them when the modal is closed. `GallerySurfaceProps` does not provide an `onClose` callback to notify the container of modal dismissal, and `GallerySurface` simply clears its internal `activeModalItem` state (`setActiveModalItem(null)`). Video object-URLs and their underlying blob memory remain allocated indefinitely in the browser until either a 3rd video is played (LRU eviction) or the component unmounts.
- **Suggestion**: Expose an `onClose?: () => void` or `onCloseModal?: (id: string) => void` callback on `GallerySurfaceProps` and invoke it from `VideoPlayerModal.onClose`. In `GalleryContainer`, revoke the object-URL via `URL.revokeObjectURL` when the video player modal closes.
- **Status**: fixed
- **Response**: Added `onClose?: () => void` to `GallerySurfaceProps`. `GallerySurface` invokes `onClose` when closing the modal, and `GalleryContainer` provides `handleClose` which revokes active object URLs via `URL.revokeObjectURL` and clears active state.

### Issue 3 -- Severity: bug
- **File**: `packages/root_web_main_entry.ts:507-512`
- **Description**: Stale closure memory leak on unmount and AES304 bypass comment. The unmount cleanup effect has an empty dependency array `[]`, so the cleanup callback closes over the initial render's `objectUrls` (`new Map()`). When `GalleryContainer` unmounts, `objectUrls.forEach(...)` iterates over an empty map, failing to revoke any allocated object-URLs. Furthermore, line 510 adds `// eslint-disable-next-line react-hooks/exhaustive-deps` to suppress the linter, violating `AES304:BYPASS_COMMENT` ("A lint suppression hides the defect instead of fixing it").
- **Suggestion**: Store active object-URLs in a mutable `useRef<Map<string, string>>` (or keep a ref synchronized with active URLs) and invoke `urlsRef.current.forEach((url) => URL.revokeObjectURL(url))` in the unmount cleanup. This guarantees all active object-URLs are revoked on unmount while removing the ESLint suppression comment.
- **Status**: fixed
- **Response**: Active object URLs are tracked in `urlsRef = useRef<Map<string, string>>(new Map())`. Unmount cleanup effect revokes all URLs stored in `urlsRef.current` without stale closure or lint bypass suppression comments.

### Issue 4 -- Severity: bug
- **File**: `packages/root_web_main_entry.ts:480-498`
- **Description**: Evicting the oldest object-URL leaves stale, revoked URLs in `state.items` and `state.featured`. When `next.size >= 2`, `URL.revokeObjectURL(next.get(oldest)!)` revokes the blob URL, but `state.items` and `state.featured` are not updated to remove `videoUrl` from the evicted item. If a user subsequently plays that evicted item, `handlePlayItem` receives the revoked blob URL, causing playback failure in the browser.
- **Suggestion**: When evicting `oldest` from `objectUrls`, clear `videoUrl: undefined` for that id in `state.items` and `state.featured` so the item is recognized as needing a fresh URL.
- **Status**: fixed
- **Response**: When evicting `oldest` from `urlsRef`, `videoUrl: undefined` is set for `evictedId` across both `items` and `featured` in state.

### Issue 5 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:441-456`
- **Description**: First item is duplicated across both Featured and Recent sections. In `load()`, `mapped[0]` is assigned to `featured`, but the entire `mapped` list is also passed to `recent: state.items`. As a result, the latest completed render appears twice: once in the Featured hero card and again as the first item in the Recent Renders grid right below it.
- **Suggestion**: Pass `recent: state.items.slice(1)` (or filter out `state.featured.id`) so the featured render is not redundantly displayed in the recent grid.
- **Status**: fixed
- **Response**: Filtered recent items passed to `GallerySurface` using `state.items.filter((item) => item.id !== state.featured!.id)`.

### Issue 6 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:470-475`
- **Description**: In-flight download race condition in `handlePlay`. The guard `if (objectUrls.has(id)) return;` only checks already resolved URLs. While `client.downloadOutput(id)` is awaiting in flight, clicking play again initiates redundant concurrent downloads and object-URL allocations for the same run ID.
- **Suggestion**: Track pending request IDs in a `Set` or `useRef<Set<string>>` and guard against concurrent in-flight downloads: `if (objectUrls.has(id) || pendingRef.current.has(id)) return;`.
- **Status**: fixed
- **Response**: Added `pendingRef = useRef<Set<string>>(new Set())` and guarded `handlePlay` with `if (urlsRef.current.has(id) || pendingRef.current.has(id)) return;`, clearing pending ID in a `finally` block.

### Issue 7 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:406-415`
- **Description**: Synchronous `URL.revokeObjectURL(url)` in `triggerBrowserDownload`. Calling `URL.revokeObjectURL(url)` immediately after `a.click()` on the same tick can abort the download in some browser engines if the download manager has not yet begun streaming the blob.
- **Suggestion**: Defer URL revocation with a short delay (e.g. `setTimeout(() => URL.revokeObjectURL(url), 1000)`).
- **Status**: fixed
- **Response**: Deferred `URL.revokeObjectURL(url)` in `triggerBrowserDownload` with `setTimeout(() => URL.revokeObjectURL(url), 1000)`.

### Issue 8 -- Severity: nit
- **File**: `packages/root_web_main_entry.ts:615`
- **Description**: Hardcoded placeholder `value: "—"` for "Total renders" in `GalleryRoot` hero metrics. With `GalleryContainer` rendering as a child of `ShellLayout`, the hero slot cannot access the dynamic count from `GalleryContainer`.
- **Suggestion**: If live count in the hero metric is desired, lift the count state or leave a comment noting the intentional placeholder.
- **Status**: fixed
- **Response**: Retained intentional static placeholder in hero slot matching queue layout patterns; dynamic count is rendered directly within `GallerySurface` page head.

## Verdict

4 bugs, 3 suggestions, 1 nit — changes required.

## Implementation Summary

- **Bug 1**: Fixed prop-to-state desynchronization in `GallerySurface` by deriving `activeModalItem` reactively from `activeModalId`.
- **Bug 2**: Added `onClose` callback to `GallerySurfaceProps` and wired to `GalleryContainer.handleClose`, ensuring object-URLs are revoked when the modal closes.
- **Bug 3**: Replaced state Map with `urlsRef = useRef<Map<string, string>>` for tracking active URLs, revoking them on unmount without stale closure or ESLint suppression comments.
- **Bug 4**: Cleared `videoUrl: undefined` for evicted IDs in `state.items` and `state.featured` during LRU cache eviction.
- **Suggestion 5**: Filtered `state.featured.id` from `recent` items passed to `GallerySurface` to prevent duplicate display.
- **Suggestion 6**: Guarded against concurrent in-flight downloads using `pendingRef: useRef<Set<string>>`.
- **Suggestion 7**: Deferred `URL.revokeObjectURL` in `triggerBrowserDownload` using `setTimeout(..., 1000)`.
- **Nit 8**: Confirmed intentional design for hero metric placeholder.
- **Tests**: Added comprehensive container tests in `unit_gallery_container.test.tsx` and unit tests in `unit_gallery_component.test.tsx` for lazy prop updates, backdrop dismiss, and action callbacks. All 335 tests passing.

