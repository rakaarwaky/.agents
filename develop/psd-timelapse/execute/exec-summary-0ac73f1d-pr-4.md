# PR 4 Implementation Summary — Studio RENDER Wiring & Bottom-Bar Cleanup

## Scope

Design doc 0ac73f1d, PR 4 of 7. Wire the Studio RENDER button to `client.startRender(inputPath)`, persist the run ID to localStorage, navigate to Queue, and remove the orphaned bottom-bar stub.

## Changes

### 1. `packages/studio/src/surface_studio_bottom_bar_component.tsx` — REMOVED
- Deleted the orphaned stub file. It duplicated the canvas `<footer>` and was imported nowhere (verified via grep across all packages).
- AES704 orphan compliance: no remaining references in any source file.

### 2. `packages/root_web_main_entry.ts` — StudioContainer.handleRender rewritten
- **Added `persistActiveRun(runId, inputPath)` helper** at module level (same `RUN_KEY = "pt-active-run"` pattern as `QueueContainer`). Stores `{ runId, inputPath }` as JSON in localStorage.
- **Updated `loadActiveRun()`** to parse JSON first, falling back to raw string for backward compatibility with pre-PR-4 plain-string values.
- **Rewrote `handleRender`**:
  - Validates `serverPath.trim()` is non-empty → sets `inspectState` to error with "Server path is required before starting a render" (matches pr-3's `inspectState` error pattern).
  - Calls `client.startRender(pathToRender)` (cosmetic quality/resolution forwarded but never mapped to wire — backend `SystemConfigVO` is locked).
  - On success: `persistActiveRun(handle.runId, pathToRender)` → `setActiveRunId` → `window.location.hash = "#queue"` so the Queue surface picks up the live run.
  - On failure: surfaces error via `inspectState` (not console.error).

### 3. `packages/studio/src/surface_studio_landing_component.tsx` — VERIFIED (no change needed)
- Already forwards `onRender` through to `StudioCanvas`. The `onCancelRun` prop is not in the current contract; cancel is handled by `QueueContainer.handleCancel()`. Props compose correctly.

### 4. `packages/studio/src/surface_studio_canvas_component.tsx` — VERIFIED (no change needed)
- `handleRenderClick` already calls `onRender({ quality, resolution })` — no 1.2s fake setTimeout (removed in pr-3). The local notification only fires when `!activeRun` (no live pipeline state wired), which is the correct fallback behavior.
- RENDER button is disabled while `isRendering` is true (live run in progress).

### 5. `packages/studio/tests/unit_studio_render_wiring.test.tsx` — NEW
11 tests covering:
- Canvas RENDER click delegates `onRender` with default `{ quality: "High", resolution: "1080p" }`
- Canvas passes changed quality/resolution through to `onRender`
- Canvas does not throw when `onRender` is undefined (passive safety)
- Canvas disables RENDER button while a live run is in progress
- Canvas shows progress notification with `runId` + `progress` props
- Canvas shows complete state at 100%
- Bottom-bar stub file removal verified via fs.stat (AES704)
- No source file imports `bottom_bar` / `StudioBottomBar` (AES704)
- `persistActiveRun` / `loadActiveRun` localStorage round-trip (3 tests including backward-compat with legacy plain-string values)

## Quality / Resolution — Cosmetic Passthrough
Quality (Low/Med/High) and Resolution (720p/1080p) are forwarded in `onRender(settings)` but never mapped to a wire field. Backend `SystemConfigVO` is locked. No wire field invented.

## Verification

- `npm run typecheck` — clean (0 errors)
- `npm test -- --run` — 325 tests passed across 42 files (0 failures)
- `lint-arwaky-cli scan .` — 37 violations, all pre-existing in `shared/src/client/*` (none in changed files)

## Constraints Honored

- Surfaces stay passive: zero `contract_*`/`capabilities_*`/`agent_*`/`root_*` imports in `surface_*` files.
- No changes to `packages/home/`, `modules/`, `packages/client/`, `packages/queue/`, `packages/gallery/`, `packages/shared/`.
- Smallest change that solves the problem.