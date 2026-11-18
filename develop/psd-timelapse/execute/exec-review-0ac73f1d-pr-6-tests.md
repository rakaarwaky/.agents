### Issue 1 -- Severity: bug
- **File**: `packages/root_web_main_entry.ts:426-530`
- **Description**: `GalleryContainer` has zero automated test coverage. The entire container logic — calling `client.listCompletedRuns()`, mapping VOs into `GalleryItem` / `GalleryFeatured`, lazy video download on play via `client.downloadOutput()`, bounding object-URLs to 2 concurrent with LRU eviction, unmount cleanup, and file download triggering — is completely unexercised by any test file. All 16 unit tests in `packages/gallery/tests/unit_gallery_component.test.tsx` test only the passive `GallerySurface` component with mock props.
- **Suggestion**: Add integration or container tests (e.g., in `packages/gallery/tests/integration_gallery_container.test.tsx` or `unit_gallery_container.test.tsx`) that mock `useOptionalClient()` and verify `listCompletedRuns` fetching, lazy object-URL creation on play, LRU eviction, and download triggering.
- **Status**: open

### Issue 2 -- Severity: bug
- **File**: `packages/gallery/tests/unit_gallery_component.test.tsx:182-193`
- **Description**: Video playback test masks the lazy loading synchronization bug by pre-populating `videoUrl` statically in initial props. The test passes `makeItem({ id: "r1", title: "Bomber", videoUrl: "blob:http://localhost/test" })` before clicking play. It never tests the realistic production lifecycle where `videoUrl` is initially `undefined`, play is clicked, and `videoUrl` is provided asynchronously via re-render. Testing this asynchronous prop update would have surfaced that `activeModalItem` never updates with the resolved `videoUrl`.
- **Suggestion**: Add a test that renders `GallerySurface` without `videoUrl`, triggers play on a card, asserts the placeholder is displayed, re-renders with `videoUrl` updated, and verifies that the modal updates to display `<video src="..." controls autoplay>`.
- **Status**: open

### Issue 3 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:459-461`
- **Description**: Untested error path for `client.listCompletedRuns()` failure. In `GalleryContainer.load()`, when `listCompletedRuns()` rejects, the catch block sets `{ status: "error", items: [] }`. This error state is completely untested, and `GallerySurface` has no error state display (it renders the empty state instead).
- **Suggestion**: Add a test verifying `GalleryContainer`'s behavior when `listCompletedRuns()` rejects.
- **Status**: open

### Issue 4 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:501-503`
- **Description**: Untested error path for `client.downloadOutput()` failure during playback. In `handlePlay`, when `client.downloadOutput(id)` rejects, the error is caught and silently ignored (`// download failed; modal shows placeholder`). There is no test ensuring that download failures are handled gracefully without unhandled promise rejections.
- **Suggestion**: Add a test asserting that if `downloadOutput` fails, the modal remains on the placeholder and does not crash.
- **Status**: open

### Issue 5 -- Severity: suggestion
- **File**: `packages/gallery/tests/unit_gallery_component.test.tsx:94-105`
- **Description**: Featured card Play and Download click callbacks are not tested. While lines 140-158 test clicking the Play and Download buttons on recent cards (`invokes onPlay when play button is clicked on recent card`), the featured card tests only assert that the buttons are in the DOM (`expect(screen.getByRole("button", ...)).toBeInTheDocument()`). They never simulate clicks to verify that `onPlay(featured.id)` and `onDownload(featured.id)` are invoked.
- **Suggestion**: Add tests clicking the featured card's "Play Video" and "Download" buttons and asserting that `onPlay` and `onDownload` are called with `featured.id`.
- **Status**: open

### Issue 6 -- Severity: suggestion
- **File**: `packages/gallery/tests/unit_gallery_component.test.tsx:160-210`
- **Description**: Missing test for modal backdrop dismiss. `VideoPlayerModal` attaches `onClick={onClose}` to the backdrop overlay and `onClick={(e) => e.stopPropagation()}` to the dialog card. The test suite verifies modal dismissal via the Close button and Escape key, but does not test clicking the backdrop overlay.
- **Suggestion**: Add a test clicking the backdrop overlay and asserting that the modal closes.
- **Status**: open

### Issue 7 -- Severity: suggestion
- **File**: `packages/gallery/tests/unit_gallery_component.test.tsx:160-210`
- **Description**: Missing test for the modal's internal "Download MP4" button. `VideoPlayerModal` contains a "Download MP4" button in its footer that calls `onDownload`. No test verifies that clicking this button inside the modal triggers the download callback.
- **Suggestion**: Add a test opening the modal, clicking the "Download MP4" button, and asserting that `onDownload` is called with the item's ID.
- **Status**: open

### Issue 8 -- Severity: nit
- **File**: `packages/gallery/tests/unit_gallery_component.test.tsx:190-191`
- **Description**: Using `toHaveAttribute("autoplay")` instead of DOM property assertion. In DOM testing, HTML boolean attributes are more cleanly verified with property assertions like `expect(video.autoplay).toBe(true)` and `expect(video.controls).toBe(true)`.
- **Suggestion**: Prefer property assertions for HTML boolean attributes.
- **Status**: open

## Verdict

2 bugs, 5 suggestions, 1 nit — changes required.
