# Exec Summary — PR 6: Gallery completed runs, playback, and download

## Changes

### `packages/gallery/src/surface_gallery_component.tsx`
- Extended `GalleryItem` interface with optional `readonly videoUrl?: string` for object-URL or `/api` download URL.
- Updated `VideoPlayerModal` to accept `videoUrl` prop. When present, renders `<video src={videoUrl} controls autoPlay>` instead of the previous static placeholder (image + `play_circle` glyph).
- Updated modal state and `handlePlayItem` to carry `videoUrl` through to the modal.

### `packages/root_web_main_entry.ts`
- Added `useCallback` to React imports.
- Added `triggerBrowserDownload(blob, filename)` helper for programmatic file downloads.
- Implemented `GalleryContainer` smart container that:
  - Uses `useOptionalClient()` to access the client aggregate.
  - Fetches completed runs via `client.listCompletedRuns()` on mount, mapping `RenderCompletedVO[]` → `GalleryItem[]` (title = PSD stem from `inputPath`, duration from `durationSeconds`).
  - First item becomes `featured` with `GalleryFeatured` shape.
  - Lazily resolves video object-URLs via `client.downloadOutput()` + `URL.createObjectURL()` on play (avoids N blobs on page load).
  - Bounds blob memory to 2 concurrent object-URLs by evicting the oldest on overflow.
  - Revokes all object-URLs on unmount.
  - Downloads via `triggerBrowserDownload` using `client.downloadOutput()`.
- Updated `GalleryRoot` to render `GalleryContainer` instead of static `DEMO_GALLERY_*` constants.
- Removed all unused `DEMO_GALLERY_*` constants (required by `noUnusedLocals`).

### `packages/root_tsconfig_entry.json`
- Added `gallery/src` and `gallery/tests` to the `include` array so TypeScript covers the new test file.

### `packages/gallery/tests/unit_gallery_component.test.tsx` (new)
- 16 unit tests covering:
  - Empty state rendering and Refresh callback.
  - Loading state rendering.
  - Featured card rendering (title, path, Play Video, Download buttons).
  - Recent grid rendering, search filtering, completed count.
  - Action callbacks (`onPlay`, `onDownload`).
  - Video player modal open/close (Close button, Escape key).
  - Placeholder rendering when `videoUrl` is absent.
  - `<video>` element rendering when `videoUrl` is present (verifies `src`, `controls`, `autoplay`).

## Verification
- `npm run typecheck` — passes clean (0 errors).
- `npm test -- --run` — 41 test files, 323 tests all passing.
