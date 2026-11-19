# Test Review — remove-queue-gallery-hero (c3cee5f6)

## Summary

The change removes the `hero` prop (`HeaderMenuHero`) from `QueueRoot` and `GalleryRoot` route definitions in `/home/raka/orca/workspaces/psd-timelapse/remove-queue-gallery-hero/packages/root_web_main_entry.ts`. The implementer also updated the docstrings and comments in `packages/root_web_main_entry.ts` to accurately reflect that only the Home route renders a hero.

- **Existing test suite pass rate:** The full test suite passes (`npm test -- --run` covers 45 test files, 389 tests).
- **Home route ShowcaseGrid ("Designer Showcase"):** Completely unaffected. Unit tests (`packages/home/tests/unit_home_showcase_grid_component.test.tsx`), card integration tests (`packages/home/tests/integration_home_navigation.test.tsx`), and layout tests (`packages/home/tests/integration_home_page_layout.test.tsx`) all pass.
- **Hero rendering on Queue/Gallery routes:** No tests were coupled to the presence of `hero` on `QueueRoot` or `GalleryRoot`. `QueueSurface`, `GallerySurface`, `QueueContainer`, and `GalleryContainer` are tested directly.
- **Previous test suggestions:** Both previous test suggestions (adding dedicated smoke tests for `QueueRoot`/`GalleryRoot` and updating test comments in `packages/shell/tests/integration_shell_frame.test.tsx`) were addressed as `wontfix` by the implementer due to strict task scope constraints limiting changes exclusively to `packages/root_web_main_entry.ts`. These pushbacks are valid and acceptable for this task boundary.
- **New issues:** None introduced by the comment and docstring updates.

No issues found.
