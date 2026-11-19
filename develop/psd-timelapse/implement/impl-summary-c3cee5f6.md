# Implementation Summary: Remove Queue and Gallery Hero Banners

## Overview
Stripped the hero banner slots from `QueueRoot` and `GalleryRoot` route definitions in `packages/root_web_main_entry.ts`. Both routes now compose only header, main content container, and footer in `ShellLayout`.

## Files Changed
- `/home/raka/orca/workspaces/psd-timelapse/remove-queue-gallery-hero/packages/root_web_main_entry.ts`

## What Was Added / Modified
- In `QueueRoot`: Removed the `hero: createElement(HeaderMenuHero, {...})` prop from the `ShellLayout` props object. Updated component docstring to note no hero is rendered.
- In `GalleryRoot`: Removed the `hero: createElement(HeaderMenuHero, {...})` prop from the `ShellLayout` props object. Updated component docstring to note no hero is rendered.
- Kept `HeaderMenuHero` import from `./header/src/index` and re-export (`export { HeaderMenu, HeaderMenuHero };`) on line 49 intact to preserve AES506 surface-orphan compliance.
- Kept the Home route's `ShowcaseGrid` ("Designer Showcase") section completely untouched.

## Plan Decisions Made
- `ShellLayout` already defines `readonly hero?: ReactNode` as an optional prop, so omitting the `hero` property from the `createElement` configuration required zero changes to `ShellLayout` or child packages.
- Preserved existing indentation (4 spaces), double-quote style, and `createElement` calling convention.
- Did not modify any other package directories or test files.

## Verification
- Web UI test suite (`npm test -- --run` inside `packages/`): 45 test files passed, 389 passed.
- TypeScript typecheck (`npm run typecheck` inside `packages/`): Passed with zero errors.
- Architecture scan (`lint-arwaky-cli scan packages/root_web_main_entry.ts`): Passed with 0 violations.
- Python lint (`uv run ruff check modules/`): All checks passed.
