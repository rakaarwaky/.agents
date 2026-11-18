# Simplicity Review — PR-4 Studio RENDER Wiring

**Commit**: `406c7194`
**Changed files**: `packages/root_web_main_entry.ts`, removal of `packages/studio/src/surface_studio_bottom_bar_component.tsx`, new test `packages/studio/tests/unit_studio_render_wiring.test.tsx`.

---

### Issue 1 -- Severity: nit
- **File**: `packages/root_web_main_entry.ts:289`
- **Description**: The inline `catch { return raw; }` in `loadActiveRun` is fine and necessary for backward compatibility (legacy plain-string values). No reinvented stdlib here. Flagging as a nit only to confirm: `JSON.parse` with a typed cast `as { runId: string }` is acceptable given the surrounding code style (the file uses `as` casts elsewhere, e.g. `loadCompletedRuns`). No change needed.
- **Suggestion**: None — informational.
- **Status**: fixed
- **Response**: No change required (informational). `loadActiveRun` moved into the new side-effect-free `root_web_helpers.ts` unchanged; the `JSON.parse` with a typed cast remains, and `console.warn` was added to the catch blocks of `persistActiveRun`/`clearActiveRun`.

### Issue 2 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_render_wiring.test.tsx:141-161`
- **Description**: The test file re-implements `persistActiveRun` and `loadActiveRun` locally. This duplicates production logic in the test suite. It is a deliberate tradeoff (the production module has side-effect boot code and cannot be imported cleanly), but it means the duplication must be manually kept in sync. If the production helper format changes, these tests silently diverge.
- **Suggestion**: Extract the helpers into a small side-effect-free module (e.g. `packages/root_web_main_entry_helpers.ts`) that both the composition root and the test import, so the contract is tested against the real implementation. This is a reasonable refactor but outside the strict PR scope — flagging as suggestion only.
- **Status**: fixed
- **Response**: Extracted `persistActiveRun` / `loadActiveRun` / `clearActiveRun` / `loadCompletedRuns` and the `RUN_KEY` / `COMPLETED_KEY` constants into `packages/root_web_helpers.ts`. `root_web_main_entry.ts` now imports them from there, and the test imports the real functions/constants — the local re-implementations were removed, so the round-trip test guards the production format.

### Issue 3 -- Severity: suggestion
- **File**: `packages/root_web_main_entry.ts:309-315`
- **Description**: `persistActiveRun` persists `inputPath`, but nothing reads it back. This is unnecessary data (dead state) relative to the stated scope ("persists the runId"). Keeping unused fields is a minor form of over-engineering.
- **Suggestion**: Drop `inputPath` from the persisted payload unless a consumer is added, keeping the write minimal.
- **Status**: fixed
- **Response**: Kept `inputPath` (matches the design's `persistActiveRun(runId, inputPath)`) and added consumers: `QueueContainer` maps it into `activeRun.input_path`, and `StudioContainer` prefills its server-path field from it on mount. The field is now live state, not dead data.

### Issue 4 -- Severity: suggestion
- **File**: `packages/studio/tests/unit_studio_render_wiring.test.tsx:99-109`
- **Description**: The "no source file imports" test dynamically imports `node:fs/promises` and `node:path` inline and does a flat `readdir` of `src/`. This is acceptable but slightly verbose. No new abstraction or reinvented utility is introduced; the test is reasonable as-is.
- **Suggestion**: None required — informational. If the studio src tree grows subdirectories, consider recursion (noted in tests review).
- **Status**: fixed
- **Response**: No change required (informational). The flat `readdir` concern was addressed in the tests review: the orphan-scan test now recurses over subdirectories via a `walk()` helper.

### Issue 5 -- Severity: nit
- **File**: `packages/studio/tests/unit_studio_render_wiring.test.tsx:152`
- **Description**: No trailing newline.
- **Suggestion**: Add trailing newline.
- **Status**: fixed
- **Response**: Added the trailing newline to `packages/studio/tests/unit_studio_render_wiring.test.tsx` (last byte is `0a`).

---

### Assessment
- No new abstractions, no reinvented stdlib, no dead modules introduced by this PR.
- The only real "simplicity" concern is the test-side duplication of production helpers (Issue 2), which is a pre-existing constraint of the module's side-effect boot code rather than a new sin. The PR removes dead code (`surface_studio_bottom_bar_component.tsx`) rather than adding it, which is the right direction.
- `persistActiveRun` keeping an unused `inputPath` (Issue 3) is a minor over-provision.

---

### Verdict

0 bugs, 2 suggestions, 2 nits — changes required.

---