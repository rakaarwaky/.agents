# Tests Review — PR-4 Studio RENDER Wiring

**Commit**: `406c7194`
**New test file**: `packages/studio/tests/unit_studio_render_wiring.test.tsx` (11 tests)
**Suite status**: 42 files / 325 tests pass; typecheck clean.

---

### Issue 1 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_render_wiring.test.tsx`
- **Description**: No test covers the new persistence format end-to-end against `QueueContainer`. `QueueContainer` initializes `activeRunId` from `loadActiveRun()` on mount (root_web_main_entry.ts:341). The tests only verify the local helper copies round-trip. There is no test asserting that a value written by `persistActiveRun` is picked up by `QueueContainer` after navigation.
- **Suggestion**: Add an integration-style test that seeds localStorage via the real persist function, mounts `QueueContainer`, and asserts the active run appears.
- **Status**: fixed
- **Response**: Added `QueueContainer — persistence integration (PR-4)` with two tests: one seeds localStorage via the real `persistActiveRun("r42", "/psd/hoodie.psd")`, mounts `QueueContainer` under a mock client, and asserts the active run's filename heading (`hoodie.psd`) appears; the other asserts the idle state ("No active render.") when no run is stored.

### Issue 2 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_render_wiring.test.tsx`
- **Description**: Error paths are untested:
  - `client.startRender` rejection → `setInspectState({ status: "error" })` (handleRender catch, root_web_main_entry.ts:521)
  - Empty `serverPath` → error state (handleRender, line 506)
  - `!client` → error state (handleRender, line 498)
  None of these branches has a test.
- **Suggestion**: Add unit/integration tests for each `handleRender` failure branch, asserting the error message surfaces in the `studio-server-path-error` node.
- **Status**: fixed
- **Response**: Added three `StudioContainer` tests: (1) no client → "Server client not available" in the `studio-server-path-error` node; (2) empty server path → "Server path is required before starting a render" and `startRender` not called; (3) `startRender` rejection → "render failed" surfaces in the `studio-server-path-error` node via `findByTestId`.

### Issue 3 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_render_wiring.test.tsx`
- **Description**: No test for the navigation side effect: that `handleRender` sets `window.location.hash = "#queue"` on success. This is a core part of the PR scope.
- **Suggestion**: Add a test that spies on `window.location.hash` (or jsdom's hashchange) and asserts navigation occurs after `startRender` resolves.
- **Status**: fixed
- **Response**: Added `persists the run and navigates to #queue on successful startRender`: mocks `startRender` to resolve a handle, clicks RENDER, then `waitFor(() => expect(window.location.hash).toBe("#queue"))`. Asserts the run was persisted (`loadActiveRun()` returns `{ runId: "r42", inputPath: "/psd/hoodie.psd" }`) and `startRender` was called with the trimmed path.

### Issue 4 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_render_wiring.test.tsx`
- **Description**: No test covers `persistActiveRun`'s inputPath write being consumed. The general review flags that `inputPath` is persisted but never read; if it is removed (as suggested), the round-trip test asserting `parsed.inputPath` (line ~145) must be updated too.
- **Suggestion**: Either test that `inputPath` is consumed downstream, or remove the assertion if the field is dropped.
- **Status**: fixed
- **Response**: `inputPath` is now consumed downstream in two places: `QueueContainer` maps the loaded `inputPath` into `activeRun.input_path`, and `StudioContainer` prefills its server-path field from the persisted `inputPath` on mount. Added `prefills the server path field from the persisted inputPath on mount` (StudioContainer) and `picks up a run persisted via persistActiveRun on mount` (QueueContainer). The round-trip test now imports the real helpers from `root_web_helpers.ts`, so the `parsed.inputPath` assertion exercises the production format.

### Issue 5 -- Severity: nit
- **File**: `packages/studio/tests/unit_studio_render_wiring.test.tsx:152`
- **Description**: No trailing newline at end of file.
- **Suggestion**: Add trailing newline.
- **Status**: fixed
- **Response**: Added the trailing newline to `packages/studio/tests/unit_studio_render_wiring.test.tsx` (last byte is `0a`).

### Issue 6 -- Severity: nit
- **File**: `packages/studio/tests/unit_studio_render_wiring.test.tsx`
- **Description**: The "no source file imports" test (lines 99-109) hardcodes a flat `readdir(srcDir)` of `../src` — it does not recurse. If the studio src tree gains a subdirectory, files there won't be scanned for `bottom_bar`/`StudioBottomBar` references.
- **Suggestion**: Note the limitation, or recurse over subdirectories if the studio src tree is expected to grow.
- **Status**: fixed
- **Response**: Replaced the flat `readdir(srcDir)` with a recursive `walk()` helper (using `readdir(..., { withFileTypes: true })`) that descends into subdirectories and scans every `.ts`/`.tsx` file. Added an assertion that at least one file is found so the test fails loudly if the tree is empty.

---

### Strengths
- `StudioCanvas` tests are solid: they cover default and changed quality/resolution, passive safety (no `onRender`), disabled RENDER while a live run is in progress, live progress notification, and 100% complete state.
- Orphan removal is verified two ways (file absent + no source references), which is a good AES704 guard.

### Gaps summary
The biggest test gap is the untested container-level wiring (persist → hash → QueueContainer pickup) and untested error paths. The localStorage round-trip tests validate a local reimplementation, not the production helpers.

---

### Verdict

0 bugs, 4 suggestions, 2 nits — changes required.

---