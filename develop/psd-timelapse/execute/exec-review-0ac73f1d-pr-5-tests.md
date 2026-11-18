### Issue 1 -- Severity: bug
- **File**: `packages/root_web_main_entry.ts` (all changed logic)
- **Description**: The new lifecycle logic in `QueueContainer` — server-truth completed-list seeding (`listCompletedRuns`), watchProgress on-complete persistence, `handleDownload`, and `saveCompletedRuns` — has **zero test coverage**. None of the changed branches, error paths, or edge cases are exercised by any test file. `root_web_main_entry.ts` is imported only by `root_test_entry.ts` (which mounts the app router, not the queue) and by smoke tests that never render the queue route.
- **Suggestion**: Add unit tests for `QueueContainer`'s container logic (e.g., via an exported render helper or by refactoring `QueueContainer` into its own testable file). At minimum cover: completed runs merge from `client.listCompletedRuns()`, on-complete persistence, download wiring, and error-swallowing paths.
- **Status**: open

### Issue 2 -- Severity: suggestion
- **File**: `packages/queue/tests/unit_queue_component.test.tsx:137`
- **Description**: The new "invokes onDownload with itemId" test asserts `onDownload` is called with `"c1"` but does not assert the Download button's enabled state from props. Combined with the existing "disables Download when outputPath is undefined" test, coverage is adequate for the prop contract, but there is no test asserting the actual invocation happens **through** the button's enabled path with a realistic `outputPath`.
- **Suggestion**: Add an assertion that `onDownload` is not called when the button is disabled (already covered) and consider asserting the button receives `aria-label="Download ok.psd"` for completeness.
- **Status**: open

### Issue 3 -- Severity: suggestion
- **File**: `packages/queue/tests/unit_queue_component.test.tsx:146`
- **Description**: The "does not invoke onDownload when Download button is disabled" test clicks a disabled button and asserts `onDownload` is not called. `userEvent.click` on a disabled button is a no-op in testing-library (it does not dispatch click events on disabled elements), so the test is technically sound but relies on implicit behavior rather than explicitly checking `btn` is disabled first.
- **Suggestion**: Add `expect(btn).toBeDisabled();` before the click to make the precondition explicit and the assertion more robust.
- **Status**: open

### Issue 4 -- Severity: suggestion
- **File**: `packages/queue/tests/unit_queue_component.test.tsx` (completed section)
- **Description**: The completed section tests do not cover `imageSrc` rendering, `formatDuration` edge cases (e.g., sub-minute durations, zero seconds), or `formatBytes` for zero-byte files. No error/edge path on the `CompletedCard` component is tested.
- **Suggestion**: Add tests for items with `imageSrc`, zero duration, and `sizeBytes: 0`.
- **Status**: open

### Issue 5 -- Severity: suggestion
- **File**: `packages/queue/tests/unit_queue_test_helpers.ts` (unchanged)
- **Description**: `renderQueue` defaults `onDownload: noop`. Tests that exercise download behavior must pass `onDownload` explicitly. No mock-download helper exists for asserting URL creation or object-URL revocation at the surface level (these live in the container, which is untested).
- **Suggestion**: No change required to helpers unless container tests are added; note for future coverage.
- **Status**: open

### Issue 6 -- Severity: nit
- **File**: `packages/queue/tests/unit_queue_component.test.tsx:139`
- **Description**: The two new tests each construct an identical `CompletedItem` array literal `{ id: "c1", inputPath: "/data/input/ok.psd", durationSeconds: 60, outputPath: "/data/out/ok.mp4" }`.
- **Suggestion**: Extract a shared `makeCompletedItem` helper for DRYness, matching the existing `makeRun`/`makeProgress` pattern.
- **Status**: open

## Verdict

1 bug, 4 suggestions, 1 nit — changes required.