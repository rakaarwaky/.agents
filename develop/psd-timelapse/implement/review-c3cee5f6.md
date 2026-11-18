# Merged Review — remove-queue-gallery-hero (c3cee5f6)

## Review Issues

### Issue 1 [General/Simplicity] — Severity: nit
- **File**: packages/root_web_main_entry.ts:6
- **Description**: Module docstring still says "All pages share one reusable header (HeaderMenu) and one shared hero (HeaderMenuHero) from header/". After this change, only Home renders a hero; Queue, Gallery, and Studio do not.
- **Suggestion**: Update to reflect reality, e.g. "All pages share one reusable header (HeaderMenu). The Home page additionally renders the shared hero (HeaderMenuHero)."
- **Status**: fixed
- **Response**: Updated the module docstring in `packages/root_web_main_entry.ts` (lines 4–6) to: "All pages share one reusable header (HeaderMenu). The Home page additionally renders the shared hero (HeaderMenuHero) from header/."

### Issue 2 [Simplicity] — Severity: nit
- **File**: packages/root_web_main_entry.ts:32
- **Description**: Import comment says "Shared header + hero (single source of truth for all pages)". The hero is no longer shared by all pages.
- **Suggestion**: Change to "Shared header (single source of truth for all pages)" or "Shared header + hero import (hero used only by Home)".
- **Status**: fixed
- **Response**: Updated the import comment (lines 33–34) to: "Shared header (single source of truth for all pages); the shared hero import below is used only by the Home page (Queue, Gallery, and Studio are hero-less)." The `HeaderMenuHero` import line was kept intact for AES506 orphan compliance.

### Issue 3 [General/Simplicity] — Severity: nit
- **File**: packages/root_web_main_entry.ts:244
- **Description**: Section divider comment reads "App pages — all share HeaderMenu + HeaderMenuHero". Queue, Gallery, and Studio no longer render HeaderMenuHero.
- **Suggestion**: Change to "App pages — all share HeaderMenu" or just "App pages".
- **Status**: fixed
- **Response**: Updated the section divider comment (line 246) to: "App pages — all share HeaderMenu; only Home renders a hero (HeaderMenuHero)".

### Issue 4 [General] — Severity: suggestion
- **File**: packages/root_web_main_entry.ts:278
- **Description**: Docstring naming asymmetry: QueueRoot references "QueueSurface" while GalleryRoot references "GalleryContainer" and StudioRoot references "StudioContainer". Pre-existing asymmetry, not introduced by this change.
- **Suggestion**: For future consistency, consider aligning the naming pattern. Not blocking.
- **Status**: wontfix
- **Response**: This naming asymmetry predates the current change — the original QueueRoot docstring read "header + hero + QueueSurface + footer" and the original GalleryRoot docstring read "header + hero + GalleryContainer + footer". My edits only removed the "+ hero" token from each docstring and appended "No hero." to match the post-change structure; I did not introduce the asymmetry. Renaming `QueueSurface` to `QueueContainer` (or vice versa) would be a cosmetic word-swap with no functional benefit, and would churn the docstring further away from what was in the codebase before this task. Left as a follow-up cleanup item for a separate pass.

### Issue 5 [Tests] — Severity: suggestion
- **File**: packages/root_web_main_entry.ts:279
- **Description**: No smoke test asserts that QueueRoot and GalleryRoot mount without a hero element. Adding one would guard against accidental reintroduction.
- **Suggestion**: Add smoke tests for QueueRoot and GalleryRoot asserting no hero element renders.
- **Status**: wontfix
- **Response**: The task scope explicitly forbids modifying anything under `packages/queue/` or `packages/gallery/` (the natural homes for such tests), and the scope lock restated in the follow-up instructions reiterates this. Adding new test files in `packages/queue/` or `packages/gallery/` is out of scope for this change. The existing test suite (`npm test -- --run`, 45 files / 389 tests) still passes after the change; a future PR could add the smoke-test coverage once scope permits.

### Issue 6 [Tests] — Severity: nit
- **File**: packages/shell/tests/integration_shell_frame.test.tsx:84
- **Description**: Test description says "renders without hero (studio page shape)". Now that Queue, Gallery, and Studio all share the hero-less shell, the description is outdated.
- **Suggestion**: Update to "renders without hero (app page shape: studio, queue, gallery)".
- **Status**: wontfix
- **Response**: The scope lock explicitly excludes `packages/shell/` ("do not create, move, edit, or delete anything under packages/shell/") and the original task instructions state "Do NOT delete the hero slots in the test file. The test file packages/shell/tests/integration_shell_frame.test.tsx renders its own hero and is unrelated." Editing the test description in that file would violate both constraints. Left for a separate pass.

---

## Implementation Summary (post-review)

### Files Modified
- `packages/root_web_main_entry.ts` — only file touched, per the scope lock.

### What Changed
- **Removed**: `hero: createElement(HeaderMenuHero, {...})` props in `QueueRoot` and `GalleryRoot` (lines ~290 and ~320).
- **Removed**: two stale docstring references to "hero" in `QueueRoot` and `GalleryRoot`, now reading "header + QueueSurface + footer. No hero." and "header + GalleryContainer + footer. No hero."
- **Updated**: module docstring (lines 4–6) to say only Home renders the hero.
- **Updated**: import comment (lines 33–34) to clarify the hero import is Home-only.
- **Updated**: section-divider comment (line 246) to read "App pages — all share HeaderMenu; only Home renders a hero (HeaderMenuHero)".
- **Preserved**: `import { HeaderMenu, HeaderMenuHero } from "./header/src/index"` and the `export { HeaderMenu, HeaderMenuHero };` re-export for AES506 surface-orphan compliance.

### Verification
- `npm test -- --run` in `packages/`: 45 files / 389 tests pass.
- `npm run typecheck` in `packages/`: clean.
- `uv run ruff check modules/`: clean.
- `lint-arwaky-cli scan packages/root_web_main_entry.ts`: 0 violations.

### Decisions / Pushbacks
- Issue 4 (naming asymmetry) is pre-existing and not introduced by this task — left alone.
- Issues 5 and 6 are blocked by the scope lock — left alone, with follow-up suggested.