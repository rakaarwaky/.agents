# PR 3 / 7 — Merged Review (general + tests + simplicity)

Branch: `execute-plan/0ac73f1d-pr-3-studio-inspect`
Commits: `f5efd93b` (implementer) + `9a1916d8` (review fixes)

## Reviewer verdicts

- **General**: 6 bugs, 6 suggestions — changes required.
- **Tests**: 16 suggestions (no blocking bugs).
- **Simplicity**: 15 suggestions (no blocking bugs).

## Bugs fixed (`9a1916d8`)

1. **Inverted render-click guard** (`surface_studio_canvas_component.tsx:55`): `activeRun && !isRendering` → `activeRun && isRendering`. The RENDER button is now blocked only while a run is actively rendering; a terminal run allows starting a new render.
2. **Inverted preview-click guard** (`:72`): same inversion fixed, so "Rendering in progress" only shows during an active render.
3. **Fabricated `RGB 16-bit` label** (`root_web_main_entry.ts:503-505`): removed; `InspectFullVO` carries no color-mode/bit-depth field, so the suffix was misleading on every render.
4. **Unstable layer IDs** (`:498-500`): `layer-${index}` → `layer.name`. Layer selection and visibility toggles now survive re-inspection.
5. **Double `watchProgress` subscription**: `StudioContainer` now gates its subscription on `window.location.hash === "#studio"` so a Studio-initiated run navigated to Queue does not produce two live subscribers with duplicate side effects.
6. **No feedback when client is absent**: `executeInspect` / `handleRender` set `inspectState = { status: "error" }` instead of a silent `console.warn`.

## Suggestions addressed

- Windows path split `[/\\]` for `fileMeta.name` fallback.
- `useMemo` on the layer mapping and the `progress` object, so progress ticks no longer reset layer selection / visibility.
- TODO comment on the preview `<video>` (placeholder until pr-4 wires real output playback).

## Suggestions deferred (documented, non-blocking)

- Canvas preview chip dimensions, StudioCanvas/StudioLanding container tests, and broader canvas test matrix — the canvas is reworked in pr-4; pr-4 adds the studio test coverage where the final wiring lives.

## Verification

```
npm run typecheck   # exit 0
npm test -- --run   # 41 files, 314 tests pass
lint-arwaky-cli scan packages/studio   # 0 violations (implementer run)
```

## Verdict

**0 open issues. Approved for merge.**