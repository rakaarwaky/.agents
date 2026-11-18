# General Review — PR-4 Studio RENDER Wiring

**Commit**: `406c7194 feat(studio): wire RENDER to client.startRender with run persistence`
**Diff base**: `9a1916d8`
**Changed files**:
- `packages/root_web_main_entry.ts` (modified)
- `packages/studio/src/surface_studio_bottom_bar_component.tsx` (removed)
- `packages/studio/tests/unit_studio_render_wiring.test.tsx` (added)

CI gates verified: `npm run typecheck` clean; `npm test -- --run` 42 files / 325 tests pass.

---

### Issue 1 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:309-312`
- **Description**: `persistActiveRun(runId, inputPath)` writes `inputPath` into `pt-active-run`, but nothing reads it back. `loadActiveRun()` (line 284) only extracts `runId`, and `QueueContainer` (line 345) hard-codes `input_path: ""`. The persisted `inputPath` is dead data — the PR scope says "persists the runId", so the extra field is unused.
- **Suggestion**: Either consume `inputPath` in `QueueContainer` (populate `activeRun.input_path`) or drop it from `persistActiveRun` to match the stated scope of persisting only the runId.
- **Status**: fixed
- **Response**: Kept `inputPath` in the persisted payload (matches the design's `persistActiveRun(runId, inputPath)`) and now read it back in two places. `QueueContainer` maps `loadActiveRun()`'s `inputPath` into `activeRun.input_path` (previously hard-coded `""`). `StudioContainer` prefills its `serverPath` field from the persisted `inputPath` on mount, so re-entering Studio resumes the path. Both behaviours are covered by new tests (`prefills the server path field from the persisted inputPath on mount`, `picks up a run persisted via persistActiveRun on mount`).

### Issue 2 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:309-315`
- **Description**: `persistActiveRun` swallows every localStorage error with `catch { // ignore }`. If the write fails (quota exceeded, private/incognito mode, storage disabled), persistence fails silently: Studio navigates to `#queue` but `QueueContainer` never picks up the run, with no user-visible feedback.
- **Suggestion**: Surface persistence failures at least via `console.warn`, or set inspect state to error so the user knows the run was not registered.
- **Status**: fixed
- **Response**: Added `console.warn` in the `catch` blocks of `persistActiveRun` and `clearActiveRun` (now in the new side-effect-free `root_web_helpers.ts`), matching the pr-5 pattern. `persistActiveRun` logs `"persistActiveRun: failed to persist active run"` and `clearActiveRun` logs `"clearActiveRun: failed to clear active run"` on storage errors.

### Issue 3 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_render_wiring.test.tsx`
- **Description**: The test file re-implements `persistActiveRun`/`loadActiveRun` locally (lines ~141-161) "to test their contract without importing from root_web_main_entry". This duplicates production logic, so the tests do not actually guard the production functions — if the real `loadActiveRun` changes format, these tests won't catch it, and vice versa.
- **Suggestion**: Test the real exported helpers from `root_web_main_entry.ts`, or keep the local copies strictly in sync and document why the real module cannot be imported.
- **Status**: fixed
- **Response**: Extracted `persistActiveRun` / `loadActiveRun` / `clearActiveRun` / `loadCompletedRuns` and the `RUN_KEY` / `COMPLETED_KEY` constants into a new side-effect-free module `packages/root_web_helpers.ts`. Both `root_web_main_entry.ts` and the test import from it, so the round-trip test now exercises the real implementation. The local re-implementation copies were removed.

### Issue 4 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_render_wiring.test.tsx`
- **Description**: No test exercises the actual PR-4 wiring end-to-end: `StudioContainer.handleRender` → `client.startRender` → `persistActiveRun` → `window.location.hash = "#queue"`. Only `StudioCanvas` in isolation and local helper copies are covered. Error paths (`startRender` rejection, malformed stored JSON, localStorage failure) are untested.
- **Suggestion**: Add integration/unit coverage for `handleRender` and the persist→navigate flow, plus the error/edge paths.
- **Status**: fixed
- **Response**: Added container-level tests for `StudioContainer` (rendered with `ClientProvider` + a mock `IClientAggregate`): `!client` → "Server client not available" error, empty server path → "Server path is required before starting a render" (asserts `startRender` not called), `startRender` rejection → "render failed" surfaces in the `studio-server-path-error` node, successful render → persists via `persistActiveRun` and navigates to `#queue` (`window.location.hash` asserted via `waitFor`). Added a `QueueContainer` integration test that seeds localStorage via the real `persistActiveRun`, mounts `QueueContainer`, and asserts the active run filename appears; plus a companion idle-state test. `persistActiveRun`/`loadActiveRun` now come from `root_web_helpers.ts` (no local copies). Test file grew from 11 to 18 tests; all 42 files / 332 tests pass.

### Issue 5 -- Severity: nit
- **File**: `packages/studio/tests/unit_studio_render_wiring.test.tsx:152`
- **Description**: File has no trailing newline.
- **Suggestion**: Add trailing newline.
- **Status**: fixed
- **Response**: Added the trailing newline to `packages/studio/tests/unit_studio_render_wiring.test.tsx` (last byte is now `0a`).

---

## AES boundary compliance (AES201 row 13 / AES406)

All `surface_*` files under `packages/studio/src/` were scanned for `contract_*` / `capabilities_*` / `agent_*` / `root_*` imports — **none found**. Surfaces remain passive.

## Quality/Resolution selectors (cosmetic passthrough only)

Confirmed: `StudioCanvas` keeps `quality`/`resolution` as local UI state and passes them only to `onRender({ quality, resolution })`. `StudioContainer.handleRender` accepts `_settings` but ignores it (underscored, intentional) and renders off `serverPath`. No wire field is introduced. ✓

## Bottom-bar removal

`support_studio_bottom_bar_component.tsx` is deleted. Grep across the workspace confirms zero remaining imports/references to `surface_studio_bottom_bar_component` or `StudioBottomBar` outside the test file that asserts its removal. ✓

## localStorage key/format and backward compatibility

Key `pt-active-run` matches `QueueContainer`'s `loadActiveRun()` read. New format is `JSON.stringify({ runId, inputPath })`. `loadActiveRun` parses JSON and extracts `runId`, falling back to the raw string on parse failure — so legacy plain-string values (`"r1"`) still load. Backward compatible. ✓

## Out-of-scope files

Verified via `git diff --name-only`: only the three files above changed. No changes to `packages/home/`, `modules/`, `packages/client/`, `packages/queue/`, `packages/gallery/`, `packages/shared/`. ✓

## Navigation side effect

`window.location.hash = "#queue"` is set inside `handleRender` (an event handler, not during render) after `startRender` resolves. `QueueContainer` initializes `activeRunId` via `useState(() => loadActiveRun())`, so navigating to `#queue` remounts `QueueRoot`/`QueueContainer` and picks up the persisted run. ✓

---

### Verdict

0 bugs, 4 suggestions, 1 nit — changes required.

---
