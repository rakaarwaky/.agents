# Plan Document Re-Review: New TypeScript package `packages/psd/` (PSD adapter)

### Summary
**Verdict: Approve.** All 12 previously-open issues are genuinely addressed in the revised plan doc (Issue 1 correctly restates the single-workspace layout; Issue 2 now edits `packages/shared/DATA.md`+`BACKLOG.md` with `DT-PSD-*` entries; the parser decision gate, extension check, dispatch shape, and prototype-pollution mitigation are all present and re-verified against source). No new blocking issues were found; the two new issues below (test-count phrasing, count-guard scope) are minor and non-blocking. The PR plan is realistic, ordered, and independently mergeable; the AES-rule citations are accurate; the codebase claims are verified. The plan is ready for implementation.

---

### Issue 1: Plan claims to "mirror `packages/client/` exactly" but the actual package has no `package.json` or `tsconfig.json`
- **Severity**: critical (was critical → now addressed)
- **Section**: Overview (line 16), Package-config note (line 103), package.json / tsconfig / vite / root wiring (line 329), PR1 file list (line 566)
- **Description**: RE-VERIFIED. The revised plan now correctly states `packages/psd/` follows the single-workspace pattern with **no per-member `package.json` or `tsconfig.json`**. Verified on disk: `ls packages/client/` returns only `BACKLOG.md`, `FRD.md`, `src/`, `tests/` — no `package.json`/`tsconfig.json`. The workspace `packages/package.json` (`"name": "psd-web"`, line 2) is correctly described as unchanged, and registration is correctly via `@psd` alias in `packages/root_config_vite_entry.ts` and `@psd/*` path + `psd/src|tests|benches` in `packages/root_tsconfig_entry.json`. Both root files were read and match the described edit points: `root_config_vite_entry.ts` line 23 has `"@client": here + "client/src"` (a sibling `@psd` alias is the correct pattern), and `root_tsconfig_entry.json` line 33 has `"@client/*": ["client/src/*"]` with `client/src` in `include`.
- **Suggestion**: None required. The layout, package-config note, PR1 file list, and summary file all agree on the single-workspace pattern.
- **Status**: addressed

---

### Issue 2: No shared-layer `DATA.md`/`BACKLOG.md` DT-PSD registration
- **Severity**: major (was major → now addressed)
- **Section**: Shared-layer doc-pair registration (lines 335–347), PR1 file list (line 566)
- **Description**: RE-VERIFIED. The revised plan adds a dedicated "Shared-layer doc-pair registration (AES701 / AES608)" subsection specifying five `DT-PSD-001..005` entries for `packages/shared/DATA.md` and matching `DT-PSD-*` blocks in `packages/shared/BACKLOG.md`, and PR1's file list now includes `packages/shared/DATA.md` and `packages/shared/BACKLOG.md`. Verified against the real files: `packages/shared/DATA.md` currently has `DT-SHARED-001..005` with the `ID | Field | Type | Description` table shape (line 9 onward) and `packages/shared/BACKLOG.md` has the `ID | Data Ref | Work Item | Priority | State | Actual Condition | Owner | Dependencies | Updated` shape (line 19 onward) — the plan correctly mirrors both. Both files were confirmed to currently lack any `DT-PSD-*` entries (verified via grep), so the registration is genuinely additive and correctly owned by PR1. AES608 (`DT-<NAME>-NNN` format, ARCHITECTURE.md line 467) and AES701 (shared folder must carry DATA.md + BACKLOG.md, ARCHITECTURE.md line 519) citations are accurate.
- **Suggestion**: None required. Optionally clarify that the `DT-PSD-*` entries use the `State: Planned` / `Dependencies: None` initial values (the plan already states this at line 347).
- **Status**: addressed

---

### Issue 3: Open Question 1 (PSD parser strategy) blocks PR2 but the plan schedules PR2 immediately after PR1
- **Severity**: major (was major → now addressed)
- **Section**: Open Questions #1 (lines 521), PR2 description (line 570)
- **Description**: RE-VERIFIED. Open Question 1 is now a hard decision gate with a named owner (@raka) and deadline ("before PR2 is scheduled"), and PR2's description carries a "Decision required" callout with the fallback: scope reduces to `validateMagicBytes` + `validatePsdDocument` only, `parsePsdFile` deferred to PR2a. This matches the revision summary (line 545) and the PR Plan (lines 569–570). The plan's claim that no PSD parser exists in `node_modules` was verified earlier and is consistent with the absence of `@adobe`/`psd-*` (the `packages/package.json` dependency/devDependency list at lines 18–32 contains no PSD parser — only react, vite, vitest, typescript, testing-library).
- **Suggestion**: None required. The gate, owner, deadline, and fallback are all present and consistent across Open Questions, PR2, and the revision summary.
- **Status**: addressed

---

### Issue 4: Client-side validation checks magic bytes but not the `.psd` extension
- **Severity**: minor (was minor → now addressed)
- **Section**: Detailed design → utility_psd_parser.ts (lines 308–311), Security (line 459), PR2 (line 569)
- **Description**: RE-VERIFIED. The plan now specifies both a case-insensitive `.psd` extension check (`PsdValidationError` code `INVALID_EXTENSION`, `retryable: false`) and the `8BPS` magic-byte check, mirroring the Python `CapabilitiesPsdToolsAdapter.validate_psd` (verified: `modules/scripting/src/capabilities_psdtools_adapter.py` lines 54–61 raise `PsdValidationError("Unsupported file extension. Only .psd is supported: ...")`). The plan also correctly notes the studio canvas picker `accept=".psd,image/*"` (verified at `packages/studio/src/surface_studio_canvas_component.tsx` line 181) as the reason the extension gate is needed.
- **Suggestion**: None required.
- **Status**: addressed

---

### Issue 5: `smoke_psd_transport.test.ts` is a misleading test name
- **Severity**: minor (was minor → now addressed)
- **Section**: Package layout (line 99), PR5 file list (line 581)
- **Description**: RE-VERIFIED. The revised plan renames it to `smoke_psd_aggregate.test.ts` in both the layout (line 99) and the PR5 file list (line 581), and the PR5 description explicitly notes "the package does no transport" (line 581). This matches the Non-Goals (no transport) and AES406 passivity.
- **Suggestion**: None required.
- **Status**: addressed

---

### Issue 6: `LayerVO.name` → `StudioLayerRow.label` mapping not called out as a smart-container concern
- **Severity**: minor (was minor → now addressed)
- **Section**: Detailed design → taxonomy_psd_vo.ts (lines 262–264), Open Questions #4
- **Description**: RE-VERIFIED. The plan adds a "Smart-container mapping obligation (deferred PR)" note stating the future PR must map `LayerVO.name → StudioLayerRow.label` while preserving the synthetic `id`, and references `packages/root_web_smart_container.ts` line 477. Verified on disk: that line maps `id: layer.name, label: layer.name` (lines 476–479), and `StudioLayerRow` (in `surface_studio_layer_panel_component.tsx` line 22) carries `label` not `name`. The obligation is correctly recorded as a future-PR contract.
- **Suggestion**: None required.
- **Status**: addressed

---

### Issue 7: Agent "no free fns" rule (AES405 sub-check 10) asserted but dispatch shape unstated
- **Severity**: minor (was minor → now addressed)
- **Section**: agent_psd_orchestrator.ts (lines 322–324)
- **Description**: RE-VERIFIED. The plan now states the orchestrator uses a `switch (operation)` with one `case` per operation returning `this.<protocol>.<method>(...)`, with "no module-level dispatch table and no module-level free functions (AES405 sub-check 10 `check_agent_free_fn`)". It references `packages/client/src/agent_client_orchestrator.ts` line 69. Verified on disk: that line is `switch (operation)` (line 69) inside `ClientOrchestrator.execute`, dispatching to `this.doInspect(...)` etc. — the mirror pattern is accurate.
- **Suggestion**: None required. (Minor observation: the real `agent_client_orchestrator.ts` dispatches to private `doInspect`/`doStartRender` methods rather than directly to protocol objects; the plan's described shape `this.<protocol>.<method>(...)` is a reasonable simplification and still satisfies AES405.)
- **Status**: addressed

---

### Issue 8: `parsePsdFile` async signature vs. synchronous main-thread parsing unspecified
- **Severity**: minor (was minor → now addressed)
- **Section**: Detailed design → utility_psd_parser.ts (lines 313–314), Observability (line 471), Data Model (line 410)
- **Description**: RE-VERIFIED. The plan now states v1 runs on the main thread with a stable async `Promise<PsdDocumentVO>` signature (so a future worker offload does not change the contract) and defines a profiling trigger: "if `bench_psd_parse.ts` shows parse p95 > 500 ms on a 100 MB fixture, open a worker-offload PR." This appears in both the parser section and Observability (line 471). The Data Model line 410 still states "< 2 s for a ≤ 500 MB PSD on the main thread" — this is a target, not a contradiction with the 500 ms-on-100 MB profiling trigger (different fixtures/thresholds), so it is acceptable.
- **Suggestion**: None required. Optionally reconcile the two numbers ("≤ 500 MB target < 2 s" vs "p95 > 500 ms on 100 MB → offload") in one sentence to avoid a reviewer thinking they conflict.
- **Status**: addressed

---

### Issue 9: Mermaid PR dependency graph vs. PR3 dependency text disagree
- **Severity**: minor (was minor → now addressed)
- **Section**: Mermaid PR dependency graph (lines 352–360), PR3 (line 574)
- **Description**: RE-VERIFIED. The Mermaid graph shows `P1 --> P3 --> P4` (PR3 depends only on PR1) with a note at line 360: "PR3 depends only on PR1; PR2 is a soft dependency." PR3's dependency list (line 574) now reads "Dependencies: PR 1" with the same soft-dependency note. Mermaid and text agree.
- **Suggestion**: None required.
- **Status**: addressed

---

### Issue 10: No explicit test-count guard or coverage target
- **Severity**: minor (was minor → now addressed, but see New Issue A)
- **Section**: PR5 (lines 581–582)
- **Description**: RE-VERIFIED. PR5 now states "~9 files with an expected ≥ 30 assertions total (validate: ≥4, rearrange: ≥4, visibility: ≥4, remove: ≥4, orchestrator: ≥4, protocol contract: ≥3, schema contract: ≥3, integration: ≥3, smoke: ≥1)." It also correctly notes `packages/tests/count-guard.mjs` is referenced by `packages/package.json` line 15 (`test:count`) but does **not exist on disk**, and that PR5 must create it or the assertion counts are the completion criterion. VERIFIED on disk: `packages/package.json` line 15 `test:count` references `tests/count-guard.mjs`; `find packages -name count-guard.mjs` returns nothing; `packages/tests/` does not exist. The plan's factual claim is correct.
- **Suggestion**: The objective completion criterion (≥ 30 assertions) is present, which resolves the original issue. However, see New Issue A: the per-file assertion minimums sum to 30 only if every unit/contract/integration file meets its floor — this is internally consistent, but the "≥ 30" phrasing could be read as a total floor while the parenthetical sums to exactly 30, so a reviewer should confirm the parenthetical is the authoritative per-file floor, not an illustrative breakdown.
- **Status**: addressed

---

### Issue 11: Does `packages/psd/` need a `DESIGN.md` or only `FRD.md` + `BACKLOG.md`?
- **Severity**: minor (was minor → now addressed)
- **Section**: Goals #5 (lines 56–58), AES compliance
- **Description**: RE-VERIFIED. The plan states feature folders carry `FRD.md` + `BACKLOG.md` only (AES702); `DESIGN.md` is surface-only (AES703) and not required for `packages/psd/`, matching `packages/client/` (verified: `packages/client/` has only `FRD.md` + `BACKLOG.md`). Verified against ARCHITECTURE.md: AES702 (line 521) requires `feature_missing_doc_pair` (FRD.md/BACKLOG.md) and does NOT require DESIGN.md; AES703 (line 530) `surface_missing_design_md` applies only to surface folders. The citation is accurate.
- **Suggestion**: None required.
- **Status**: addressed

---

### Issue 12: Security table does not address prototype pollution via crafted layer names
- **Severity**: minor (was minor → now addressed)
- **Section**: Security & Privacy (line 462)
- **Description**: RE-VERIFIED. The plan adds a threat-table row: "Prototype pollution via crafted layer names (`__proto__`, `constructor`, `toString`) — Low — Sanitize `LayerVO.name`/`LayerVO.classification` with a `sanitizeName()` utility mirroring Python `sanitize_name` ... Never use layer names as plain-object keys; use a `Map` or prefix keys." Verified the Python reference: `sanitize_name` is defined at `modules/shared/src/scripting/utility_scripting_geometry.py` line 18, and `capabilities_psdtools_adapter.py` uses `_sanitize_name` at line 246–247 (the plan cites "line 213" for the call site, which is where `_sanitize_name` is invoked to build the DTO name — line 213 reads `name=self._sanitize_name(layer.name) or f"Layer_{layer_id}"`, so the citation is correct).
- **Suggestion**: None required.
- **Status**: addressed

---

### New Issues

#### New Issue A: Test-count completion criterion's per-file floors do not all fit the 9 listed files
- **Severity**: minor
- **Section**: PR5 (line 582)
- **Description**: PR5 lists 9 test files and a parenthetical assertion breakdown: "validate: ≥4, rearrange: ≥4, visibility: ≥4, remove: ≥4, orchestrator: ≥4, protocol contract: ≥3, schema contract: ≥3, integration: ≥3, smoke: ≥1" — these sum to 30. The 9 files map 1:1 to those 9 categories (validate, rearrange, visibility, remove, orchestrator, protocol contract, schema contract, integration, smoke), so the per-file floors are internally consistent and reachable. This is not a blocking problem, but the phrase "~9 files with an expected ≥ 30 assertions total" could be read as a total floor separate from the parenthetical. A reader implementing PR5 should treat the parenthetical as the authoritative per-file minimums.
- **Suggestion**: Clarify "the parenthetical lists the per-file assertion minimums; the sum (30) is the package-level floor" so the completion criterion is unambiguous. No re-scoping required.
- **Status**: open (minor; non-blocking)

#### New Issue B: Count-guard replacement path is internally consistent but leaves `test:count` as a permanent no-op unless PR5 creates the guard
- **Severity**: minor
- **Section**: PR5 (line 582), Rollout → Verification (line 486)
- **Description**: PR5 correctly notes `packages/tests/count-guard.mjs` does not exist and `packages/package.json` line 15 `test:count` is therefore a no-op (verified). However, the plan says PR5 "must either create `packages/tests/count-guard.mjs` ... or update the existing inventory once the guard is introduced; until then `test:count` is a no-op." Creating a new `count-guard.mjs` is out of scope for a package-scaffold PR (it would touch the shared `packages/tests/` harness and the `package.json` script contract), and the Rollout "Verification" line (line 486) only lists `npm test -- --run`, `uv run ruff check`, and `lint-arwaky-cli scan .` — it does NOT run `test:count`. So the guard is neither created nor exercised by this plan, which is fine, but the plan should state explicitly that `test:count` is intentionally not wired in this plan (the guard is a pre-existing repo gap, not a psd-package deliverable).
- **Suggestion**: Add one sentence to PR5 or Rollout stating the `count-guard.mjs` gap is pre-existing and out of scope; PR5's completion criterion is the assertion counts, not `test:count`. Avoid implying PR5 should create a shared harness file.
- **Status**: open (minor; non-blocking)

---

### Strengths

- **All 12 original issues genuinely addressed, not just claimed.** Each was re-verified against the actual file text: the single-workspace layout (Issue 1), the `DT-PSD-*` registration in shared docs (Issue 2), the parser decision gate with owner/deadline/fallback (Issue 3), the extension check mirroring the Python `validate_psd` message (Issue 4), the smoke-test rename (Issue 5), the `LayerVO.name → StudioLayerRow.label` obligation (Issue 6), the `switch (operation)` dispatch shape (Issue 7), the main-thread + profiling-trigger statement (Issue 8), the Mermaid/PR3 dependency agreement (Issue 9), the test-count criterion + count-guard gap (Issue 10), the DESIGN.md-not-required note (Issue 11), and the prototype-pollution row (Issue 12).
- **Factual accuracy of codebase citations is high.** Verified: `packages/client/` has no per-member `package.json`/`tsconfig.json`; `packages/package.json` is `"name": "psd-web"` with `test:count` → `tests/count-guard.mjs` (nonexistent); `root_config_vite_entry.ts` line 23 has the `@client` alias; `root_tsconfig_entry.json` line 33 has `@client/*` path; `root_web_smart_container.ts` lines 476–479 map `id: layer.name, label: layer.name`; `agent_client_orchestrator.ts` line 69 is `switch (operation)`; Python `validate_psd` raises `PsdValidationError` with "Unsupported file extension. Only .psd is supported"; `sanitize_name` is at `utility_scripting_geometry.py` line 18; `surface_studio_canvas_component.tsx` line 181 has `accept=".psd,image/*"`; `surface_studio_layer_panel_component.tsx` line 22 defines `StudioLayerRow` with `label`.
- **AES rule citations are accurate.** AES701 (shared folder purity + doc pair), AES702 (feature health + FRD/BACKLOG + `shared/src/<feature>/` mirror), AES703 (surface DESIGN.md), AES704 (test/bench coverage), AES705 (member-root placement), AES706 (PR ID folder mapping), AES608 (DT-ID format) all match ARCHITECTURE.md lines 467–557.
- **PR sequencing is realistic and independently mergeable.** PR1 (scaffold + shared mirror + root aliases, no deps) → PR2 (parser/validate, gated) and PR3 (layer edits, deps PR1, PR2 soft) in parallel → PR4 (agent + container) → PR5 (tests/benches). The Mermaid and text now agree (Issue 9).
- **Open Questions are honest and correctly scoped.** The parser decision gate (Q1), v1 output shape (Q2), PR/FR id (Q3), studio wiring (Q4, deferred), and error mapping (Q5) are all real and correctly deferred or gated.
- **Security table is now complete.** Covers DoS, path traversal, XSS, prototype pollution, sensitive content, and auth — matching the threat model for a client-side parser operating on untrusted `File` objects.
- **Revision Summary is accurate and traceable.** Each of the 12 issues maps to a concrete text change with line references; spot-checks against the plan body confirm the changes are present.

---

### Notes for the orchestrator

- **Blocking (critical/major) open issues: none.** All critical/major issues from the prior review are addressed.
- **Minor open issues: New Issue A and New Issue B**, both non-blocking (test-count phrasing and count-guard scope clarification). These do not block implementation; they are documentation nit-reads that a reviewer implementing PR5 should clarify.
- **Exit condition met:** All 12 previously-open issues are `addressed`, and there are no new blocking (critical/major) issues. Per the exit condition, the verdict is **approve**, and the orchestrator may proceed to Step 6 (summary). The plan is implementable as written; New Issues A and B are optional clarifications to carry forward into PR5.