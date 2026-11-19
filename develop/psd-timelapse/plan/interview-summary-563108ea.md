# Grill-Me Interview Summary

- **Repo:** `/home/raka/orca/workspaces/psd-timelapse/planner-studio-upload-to-topbar`
- **Interview ID:** `563108ea`
- **Plan file:** `/home/raka/.agents/develop/psd-timelapse/plan/plan-doc-14c3b92a.md`
- **Date:** 2026-11-19
- **Lint baseline:** 78 total (packages/shared 43, PRD.md 11, ROADMAP.md 11, packages/client 11, modules/api 1, modules/system 1; AES706=23, AES402=19, AES401=14, AES501=5, AES503=5, AES704=4, AES502=2, AES504=2, AES303/304/505/609=1 each)

## Branches Walked

1. **CSS divider class collision** — Resolved (codebase)
2. **Server-path input bar redundancy** — Resolved (codebase)
3. **`onSelectLayer` not threaded from container** — Resolved (codebase)
4. **`onSelectLayer` not forwarded from StudioLanding to StudioCanvas** (plan omission) — Resolved (codebase)
5. **Test file completeness (PR 1 scope vs sidebar prop removal)** — Resolved (codebase)
6. **`lint-arwaky-cli scan` as a CI gate** — Resolved (codebase)
7. **CSS cleanup of dead sidebar selectors** — Resolved (codebase, scoped out)
8. **`StudioFileMeta` re-export chain preservation** — Resolved (codebase)

## Decisions Resolved

### D1 — CSS divider class collision (BLOCKING DEFECT)
- **Branch:** CSS additions to `packages/shared/src/common/styles.css`
- **Answer:** The plan reuses `.pt-studio-canvas-divider` for two incompatible purposes. Source: `styles.css:4808-4812` defines it as mono-font metadata (`font-size: 0.6875rem; color: rgba(255, 255, 255, 0.35); margin: 0 0.125rem`), and `surface_studio_canvas_component.tsx:148` uses `<span className="pt-studio-canvas-divider">⌘</span>` as the ⌘ glyph carrier. The plan's proposed CSS override (`.pt-studio-canvas-divider:empty { width: 1px; height: 1rem; background: ... }`) produces a 1px×16px vertical rule that collides with the existing ⌘ span, and `:empty` only matches when the span has no children — the ⌘ span has a text child, so it would NOT match the rule and would still render as a glyph, leaving the new divider unstyled (no width/height/background applied). The upload divider must use a distinct class name (e.g. `.pt-studio-canvas-divider-v`).
- **Depends on:** —
- **Source:** `packages/shared/src/common/styles.css:4808-4812`, `packages/studio/src/surface_studio_canvas_component.tsx:148`

### D2 — Server-path input bar redundancy
- **Branch:** Placement of file ingestion entry point
- **Answer:** The plan keeps the container's server-path bar (`.pt-studio-server-path-bar`, rendered by `StudioContainer` in `packages/root_web_smart_container.ts:450-573`). The canvas upload button provides a file picker, but `handlePickFile` in the container just calls `executeInspect(file.name)` which only uses `file.name` as a relative path — the actual PSD is read from a server-side filesystem, not from the browser file. So the server-path bar remains the canonical way to specify an absolute path for server-side inspection. The canvas drop/pick provides a convenient entry point, but the user may still need to override the path in the server-path bar for paths that differ from the file name.
- **Depends on:** —
- **Source:** `packages/root_web_smart_container.ts:322-355` (handlePickFile, executeInspect), `packages/root_web_smart_container.ts:450-573` (server-path bar render)

### D3 — `onSelectLayer` not threaded from container
- **Branch:** Data flow from StudioContainer to StudioLayerPanel
- **Answer:** The container (`StudioContainer`) does not pass `onSelectLayer` to `StudioLanding` at all — the `createElement(StudioLanding, {...})` call at lines 573-580 only passes `onPickFile`, `onReinspect`, `onRender`, `layers`, `fileMeta`, `runId`, and `progress`. The `onSelectLayer` prop exists in `StudioLandingProps` and `StudioLayerPanelProps` but is dead in practice from the container's perspective. The plan does not need to thread `onSelectLayer` through `StudioCanvas`; it is an existing dead prop unrelated to this change.
- **Depends on:** —
- **Source:** `packages/root_web_smart_container.ts:573-580`

### D4 — `onSelectLayer` not forwarded from StudioLanding to StudioCanvas (plan omission)
- **Branch:** Component architecture (mermaid diagram and prop flow)
- **Answer:** The plan's mermaid diagram (lines 72-100) and the component code snippets (lines 325-350) do not forward `onSelectLayer` from `StudioLanding` to `StudioCanvas` (or to `StudioLayerPanel` with the new stripped interface). The existing code at `surface_studio_landing_component.tsx:69-73` passes `onSelectLayer={onSelectLayer}` to `StudioLayerPanel`, and the new `StudioLayerPanelProps` retains `onSelectLayer`. The plan must explicitly thread `onSelectLayer` through `StudioLanding` to `StudioLayerPanel` in the updated code snippet.
- **Depends on:** D3
- **Source:** `packages/studio/src/surface_studio_landing_component.tsx:69-73`

### D5 — Test file completeness (PR 1 scope vs sidebar prop removal)
- **Branch:** Test changes and PR decomposition
- **Answer:** The plan says PR 1 updates `unit_studio_canvas_upload.test.tsx` and PR 2 updates `unit_studio_layer_panel_component.test.tsx`. However, after PR 1, the sidebar test file still references `fileMeta`, `onPickFile`, and `onReinspect` in `renderPanel` (lines 37-42 of the test) and passes them as props to `StudioLayerPanel`. After PR 1, `StudioLayerPanelProps` no longer accepts those props — so `unit_studio_layer_panel_component.test.tsx` will fail to type-check (`tsc -p root_tsconfig_entry.json --noEmit`) and the sidebar test group `"invokes onPickFile with the selected File on drop"` will fail at runtime (`getByRole("button", { name: "Drop PSD file or click to browse" })` finds nothing). The plan's rollout plan must include a minimal sidebar test fix in PR 1 (remove file-meta/onPickFile/onReinspect assertions) and full sidebar DOM removal in PR 2. Alternatively, merge PR 1 and PR 2 into a single PR to avoid the broken intermediate state.
- **Depends on:** —
- **Source:** `packages/studio/tests/unit_studio_layer_panel_component.test.tsx:37-42`, `packages/studio/tests/unit_studio_layer_panel_component.test.tsx:87-106`, `packages/studio/tests/unit_studio_layer_panel_component.test.tsx:128-135`

### D6 — `lint-arwaky-cli scan` as a CI gate
- **Branch:** CI gates
- **Answer:** The plan lists `lint-arwaky-cli scan .` as a CI gate, but the baseline shows 78 existing violations with no staged reduction in the plan. The CLI exits non-zero when violations are present. The correct gate wording is "no NEW violations introduced; total count does not increase from baseline (78)". The implementer must scope new code to avoid triggering AES violations (passive component boundaries, file-size limits, naming conventions).
- **Depends on:** —
- **Source:** lint-arwaky baseline scan output (recorded above)

### D7 — CSS cleanup of dead sidebar selectors
- **Branch:** CSS additions (scope of cleanup)
- **Answer:** Leaving `.pt-studio-sidebar-header`, `.pt-studio-sidebar-file*`, `.pt-studio-sidebar-dropzone*` in `styles.css` after PR 2 removes the DOM leaves ~120 lines of dead CSS. This is acceptable as a deliberate decision to avoid a gratuitous diff, but should be noted as tech debt. Moving them out is a follow-up, not a blocker.
- **Depends on:** —
- **Source:** `packages/shared/src/common/styles.css:4905-5043`

### D8 — `StudioFileMeta` re-export chain preservation
- **Branch:** Type definition location
- **Answer:** The plan correctly keeps the `StudioFileMeta` interface definition in `surface_studio_layer_panel_component.tsx` and preserves the re-export chain through `surface_studio_landing_component.tsx:39` (`export type { StudioFileMeta }`) consumed by `root_web_smart_container.ts:38`. After PR 2 removes the sidebar's file-meta DOM, the `StudioFileMeta` type is still imported by `root_web_smart_container.ts` for the `fileMeta` computation at line 412 and passed through `StudioLanding` to `StudioCanvas`. The chain stays intact. No change needed.
- **Depends on:** —
- **Source:** `packages/studio/src/surface_studio_layer_panel_component.tsx:29-33`, `packages/studio/src/surface_studio_landing_component.tsx:6-7, 39`, `packages/root_web_smart_container.ts:38, 412`

## Open Questions

None.

## Shared Understanding

Reached. The plan is architecturally sound (passive components, callback threading, AES201/406 compliance) but contains one blocking CSS defect (D1) and one scope/rollout gap (D5). All other branches resolve cleanly against the codebase.