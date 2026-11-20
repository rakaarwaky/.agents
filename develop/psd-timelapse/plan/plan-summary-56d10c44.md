# Summary — Plan doc-56d10c44 (rev 1)

**Task:** New TypeScript package `packages/psd/` (PSD adapter) in the PSD Timelapse repo.

**Scope.** Create `packages/psd/` as an AES 7-layer TypeScript feature package, modeled on the existing `packages/client/` package. The package parses a user-uploaded PSD `File` in the web UI, validates it before it is sent to the Python server, and prepares/previews a PSD with simple layer edits (rearrange/sort, hide/visibility, remove layer). It exposes a `createPsdAggregate()` root container wiring four capabilities behind one `IPsdAggregate` agent orchestrator. Studio remains passive; smart-container wiring is deferred to a later PR.

**Three AES layer pieces (plus mandatory mirror).**
- `agent_psd_orchestrator` — agent layer, single `execute` switch dispatch on `IPsdAggregate` (no module-level dispatch table, no free fns; mirrors `agent_client_orchestrator.ts` line 69).
- `capabilities_psd_validate`, `capabilities_psd_layer_rearrange`, `capabilities_psd_layer_visibility`, `capabilities_psd_layer_remove` — four capabilities, one protocol each (AES403).
- `root_psd_container` — root composition wiring all capabilities into `IPsdAggregate` (AES503/AES505 orphan compliance).
- `packages/shared/src/psd/` mirror — taxonomy (`taxonomy_psd_vo.ts`, `taxonomy_psd_request.ts`, `taxonomy_psd_response.ts`, `taxonomy_psd_error.ts`, `taxonomy_psd_constant.ts`), contract (`contract_psd_protocol.ts`, `contract_psd_aggregate.ts`), utility (`utility_psd_parser.ts`), barrel (`index.ts`).
- `packages/psd/FRD.md` + `BACKLOG.md` doc pair (FR ids `FR-PSD-...`, PR id candidate `PR-PSD-016`).
- **Shared doc pair:** new `DT-PSD-001..005` entries in `packages/shared/DATA.md` and matching `DT-PSD-*` blocks in `packages/shared/BACKLOG.md`, mirroring the `DT-SHARED-001` table shape.
- Tests (`packages/psd/tests/`, AES103 prefixes: unit_/contract_/integration_/smoke_) and benches (`packages/psd/benches/bench_psd_parse.ts`).

**Package layout (single-workspace pattern).** `packages/psd/` has **no per-member `package.json` or `tsconfig.json`** — verified `packages/client/` has only `BACKLOG.md`, `FRD.md`, `src/`, `tests/`. The workspace `packages/package.json` (`"name": "psd-web"`) is unchanged. Registration is via: `@psd/*` path alias + `psd/src|tests|benches` `include` entries in `packages/root_tsconfig_entry.json`, and the `@psd` alias in `packages/root_config_vite_entry.ts`.

**Key changes by file.**
- New: `packages/psd/{FRD.md,BACKLOG.md}`, `packages/psd/src/{index.ts,agent_psd_orchestrator.ts,root_psd_container.ts,capabilities_psd_validate.ts,capabilities_psd_layer_rearrange.ts,capabilities_psd_layer_visibility.ts,capabilities_psd_layer_remove.ts}`, `packages/shared/src/psd/{taxonomy_*.ts,contract_*.ts,utility_psd_parser.ts,index.ts}`, `packages/psd/tests/*.test.ts`, `packages/psd/benches/bench_psd_parse.ts`.
- Edited: `packages/shared/DATA.md` (DT-PSD-001..005), `packages/shared/BACKLOG.md` (DT-PSD blocks), `packages/root_tsconfig_entry.json` (@psd/* alias + include), `packages/root_config_vite_entry.ts` (@psd alias).
- Untouched: `packages/client/*`, `packages/shared/src/client/*`, `packages/studio/*`, `packages/root_web_*.ts`, `modules/api/*`.

**AES compliance.** AES101/AES102 naming; AES201 import matrix; AES301/302 file line limits; AES403 3-block capability structure; AES405 agent stateless, no I/O/computation/free fns, ≥2 injected protocols, `switch (operation)` dispatch; AES406 studio stays passive; AES503/505 capabilities/agent wired in `root_psd_container`; AES702 feature health; AES704 test+bench coverage; AES705 no layer files at member root; AES706 PR-ID folder mapping. Feature folders carry `FRD.md` + `BACKLOG.md` only (AES702); `DESIGN.md` is surface-only (AES703), not required for `packages/psd/` (matches `packages/client/`).

**Validation.** `parsePsdFile`/validate capability checks both (1) case-insensitive `.psd` extension — rejecting with `PsdValidationError` code `INVALID_EXTENSION` mirroring the Python message "Unsupported file extension. Only .psd is supported" (studio canvas `accept=".psd,image/*"` lets non-PSD images through) — and (2) `8BPS` magic bytes.

**Parser decision gate (Open Question 1).** No PSD parser in `node_modules` (verified `@adobe`/`psd-*` absent). PR2 is gated on this decision (owner @raka, before PR2 is scheduled). Fallback: if no browser dependency is approved, PR2 scope reduces to `validateMagicBytes` + `validatePsdDocument` only, with `parsePsdFile` deferred to PR2a.

**Parse strategy.** v1 main-thread with a stable async `Promise<PsdDocumentVO>` signature (so a future Web Worker offload does not change the contract). Profiling trigger: if `bench_psd_parse.ts` shows parse p95 > 500 ms on a 100 MB fixture, open a worker-offload PR.

**Security.** Threat table now covers parser DoS (size/layer caps, magic-byte gate), path traversal (no path APIs), XSS (sanitize layer names), prototype pollution via crafted names (`__proto__`/`constructor`/`toString` — `sanitizeName()` utility mirroring Python `sanitize_name`, `Map`/prefix keys), sensitive content, and auth (out of scope).

**Resolved decisions.** (1) Mirror `packages/client/` AES layout/doc pair/test prefixes. (2) Four capabilities, one protocol each. (3) Agent depends on contracts only; container injects protocol-typed instances. (4) Client-side immutable `PsdDocumentVO` edit model; preview synchronous; `Blob` serialization optional/v1-deferred. (5) Studio stays passive; only the smart container imports the psd aggregate. (6) No server changes. (7) Field mapping `LayerVO.name → StudioLayerRow.label` owned by the future smart-container PR (reference `root_web_smart_container.ts` line 477).

**Open questions (5).** (1) PSD parsing strategy — decision gate before PR2. (2) v1 output shape — serialized `Blob` vs. in-memory preview + edit plan. (3) PR/FR id — confirm `PR-PSD-016` / `FR-PSD-...`. (4) Studio wiring of edit actions (deferred). (5) Error mapping to UI / `ClientError` envelope.

**Test count (PR5).** ~9 files, ≥ 30 assertions total. `packages/tests/count-guard.mjs` is referenced by `packages/package.json` line 15 `test:count` but does not exist on disk (verified) — PR5 must create it with a `packages/psd/tests/` inventory or the assertion counts are the completion criterion.

**PR Plan (5 ordered, independently mergeable PRs; PR3 depends on PR1 only, PR2 is a soft dependency).**
- PR1: scaffold package + shared mirror + DATA.md/BACKLOG.md DT-PSD + root aliases (deps: none).
- PR2: parser utility + validate capability (deps: PR1; gated on parser decision gate).
- PR3: layer-edit capabilities (deps: PR1; PR2 soft).
- PR4: agent orchestrator + root container (deps: PR1, PR2, PR3).
- PR5: tests + benches + count guard (deps: PR4).

**Revision Summary:** All 12 review issues addressed (1 critical, 2 major, 9 minor) — see the `## Revision Summary` section in the plan doc for per-issue detail.

**Full plan:** [plan-doc-56d10c44.md](plan-doc-56d10c44.md)