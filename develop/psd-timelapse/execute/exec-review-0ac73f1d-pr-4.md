# PR 4 / 7 — Merged Review (general + tests + simplicity)

Branch: `execute-plan/0ac73f1d-pr-4-studio-render`
Commits: `406c7194` (implementer) + `360307e4` (review fixes)

## Reviewer verdicts

- **General**: 0 bugs, 4 suggestions, 1 nit.
- **Tests**: 0 bugs, 4 suggestions, 2 nits.
- **Simplicity**: 0 bugs, 2 suggestions, 2 nits.

## Suggestions fixed (`360307e4`)

1. **Persisted `inputPath` was dead state** — new `packages/root_web_helpers.ts` (side-effect-free, testable) holds `persistActiveRun`/`loadActiveRun`/`clearActiveRun`/`loadCompletedRuns` + `RUN_KEY`/`COMPLETED_KEY`. `StudioContainer` now prefills the server-path field from the persisted `inputPath`; `QueueContainer` maps it into `activeRun.input_path` (was `""`).
2. **Silent localStorage failures** — `persistActiveRun`/`clearActiveRun` now `console.warn` on storage failure (pr-5 pattern).
3. **Test/prod duplication** — tests import the real helpers; local copies removed. Tests: 11 → 18 (added `!client` error, empty-path no-startRender, startRender rejection → error state, persist + `#queue` navigation, server-path prefill, 2 QueueContainer integration tests).
4. Missing trailing newline fixed.

## Verified in review

- AES boundary: zero forbidden imports in `surface_*` files.
- Bottom-bar stub removed with zero dangling references (orphan scan recurses subdirs).
- `pt-active-run` format: `loadActiveRun` parses JSON with legacy plain-string fallback — QueueContainer compat preserved.
- Quality/Resolution remain cosmetic passthrough.

## Verification

```
npm run typecheck   # exit 0
npm test -- --run   # 42 files, 332 tests pass
```

## Verdict

**0 open issues. Approved for merge.**