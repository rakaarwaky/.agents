### Issue 1 -- Severity: suggestion
- **File**: `packages/gallery/src/surface_gallery_component.tsx:520-546`
- **Description**: Storing a duplicate copy of item data in `activeModalItem` state adds unnecessary complexity and causes state desynchronization. `GallerySurface` stores `{ id, title, imageSrc, videoUrl } | null` in state. Duplicating prop data into state creates synchronization overhead and directly causes the bug where lazy `videoUrl` resolution is ignored by the open modal.
- **Suggestion**: Replace `activeModalItem` state with a single primitive identifier `activeModalId: string | null`. Derive the active item reactively on render: `const activeItem = activeModalId ? (featured?.id === activeModalId ? featured : recent.find((r) => r.id === activeModalId)) : null;`. This eliminates state copying, reduces code, and ensures the modal always receives fresh prop data.
- **Status**: open

### Issue 2 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:468-500`
- **Description**: Redundant multi-location object-URL storage and over-engineered LRU cache. Object-URLs are stored in three separate locations: the `objectUrls` Map in state, inside `state.items[i].videoUrl`, and inside `state.featured.videoUrl`. Bounding blob memory by implementing an LRU cache with eviction logic across all three state locations is unnecessarily complex. If the requirement "revoke on close" were implemented, at most one video plays at a time, bounding active blob memory naturally to 1 and eliminating the need for LRU eviction logic.
- **Suggestion**: Simplify URL lifecycle: manage a single active object-URL (or track active URLs in a ref) and revoke the URL when the modal is closed or another video is selected.
- **Status**: open

### Issue 3 -- Severity: nit
- **File**: `packages/root_web_main_entry.ts:510`
- **Description**: ESLint suppression comment hides stale closure instead of fixing it. Using `// eslint-disable-next-line react-hooks/exhaustive-deps` suppresses the compiler warning, masks a real memory leak on unmount, and triggers `AES304:BYPASS_COMMENT`.
- **Suggestion**: Use a `useRef` to store active URLs or pass active URLs cleanly into the cleanup hook, removing the suppression comment.
- **Status**: open

### Issue 4 -- Severity: nit
- **File**: `packages/gallery/src/surface_gallery_component.tsx:548-556`
- **Description**: Unguarded `setTimeout` in `handleDownloadItem`. `setTimeout(() => setDownloadToast(null), 3000)` does not track or clear the timer handle on component unmount, potentially setting state on an unmounted component.
- **Suggestion**: Store the timer ID in a ref and clear it on unmount or when a new toast is scheduled.
- **Status**: open

### Issue 5 -- Severity: nit
- **File**: `packages/root_web_main_entry.ts:443`
- **Description**: Inline string manipulation for extracting PSD basename without extension. `r.inputPath.split("/").pop()?.replace(/\.psd$/i, "") ?? r.runId` is duplicated across components.
- **Suggestion**: Consider extracting a small shared helper `psdStem(path: string): string` if repeated elsewhere, or keep inline with a brief explanatory comment.
- **Status**: open

### Issue 6 -- Severity: nit
- **File**: `packages/gallery/src/surface_gallery_component.tsx:374`
- **Description**: Hardcoded display strings `"1080p 60fps"` and `"Deterministic MP4 · H.264 CRF 18"` in `VideoPlayerModal`. While matching UI mockups, hardcoding them inside the modal prevents displaying the actual resolution or metadata of the selected render.
- **Suggestion**: Pass the render's `meta` string or quality badge into `VideoPlayerModal` as a prop.
- **Status**: open

## Verdict

0 bugs, 2 suggestions, 4 nits — changes required.
