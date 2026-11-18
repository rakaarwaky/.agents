# PR 6 / 7 — Merged Review (general + tests + simplicity)

Branch: `execute-plan/0ac73f1d-pr-6-gallery-live`
Commits: `54f8e2bd` (implementer) + `ee7a6cef` (review fixes)

## Reviewer verdicts

- **General**: 4 bugs, 3 suggestions, 1 nit — changes required.
- **Tests**: 2 bugs, 5 suggestions, 1 nit — changes required.
- **Simplicity**: 0 bugs, 2 suggestions, 4 nits — changes required.

## Bugs fixed (`ee7a6cef`)

1. **Modal never showed the video on first play**: `activeModalItem` copied `videoUrl` (undefined at click time) into state and never re-synced. Replaced with `activeModalId` + reactive derivation on each render; the modal now renders `<video>` as soon as the lazy URL resolves.
2. **Missing revoke on close**: `GallerySurfaceProps` gained `onClose`; `GalleryContainer` revokes the item's object-URL and clears `videoUrl` when the modal closes (lazy URLs bounded to 2 concurrent as the design requires).
3. **Unmount leak + AES304 bypass comment**: object-URLs tracked in a `useRef<Map>`; unmount cleanup revokes all of them; the `eslint-disable react-hooks/exhaustive-deps` suppression was removed (issue fixed, not hidden).
4. **Stale revoked URLs after LRU eviction**: evicting the oldest URL now clears `videoUrl: undefined` for that id in `items`/`featured` so a re-play resolves a fresh URL.

## Suggestions addressed

- Featured item no longer duplicated in the recent grid (`filter(id !== featured.id)`).
- `pendingRef` Set guards concurrent in-flight `downloadOutput` for the same run.
- `triggerBrowserDownload` revokes the object-URL after a 1s delay so slow browsers do not abort the stream.
- New `unit_gallery_container.test.tsx` (8 tests): empty state, completed-run mapping, lazy download on play, error handling, LRU bound of 2 + eviction, revoke on close, revoke on unmount.
- Component tests extended: reactive lazy `videoUrl` in open modal, backdrop dismiss, modal download button, featured card callbacks.

## Verification

```
npm run typecheck   # exit 0
npm test -- --run   # 42 files, 335 tests pass
```

## Verdict

**0 open issues. Approved for merge.**