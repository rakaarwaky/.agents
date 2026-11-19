# Tests Review — fix-js-ts-import-resolution

**Scope:** Test coverage and quality for changes in `/home/raka/orca/workspaces/tools/fix-js-ts-import-resolution`.
**Baseline:** Clean working tree (2 modified files).
**Verdict:** PASS_WITH_SUGGESTIONS

---

## Findings

### 1. Bug (missing integration coverage)

**File:line:** `crates/filesystem/tests/unit_filesystem_import_resolution.rs:622-810`
**Severity:** bug
**Description:**
The new tests added for `.js`/`.jsx`/`.ts`/`.tsx`/`.mjs`/`.cjs` extension swapping call `resolve_import_target` directly with hand-built `ImportEntry` structs and manually constructed `HashSet<&str>` / `HashMap<String, Vec<String>>`. There is no end-to-end test exercising the full `FilesystemOrchestrator` pipeline (`FilesystemRequest::build_orphan_graph_context` -> `ASTParser` -> `resolve_import_target` -> `ImportGraph` reachability) with TypeScript files that use explicit `.js` extension specifiers on disk (such as `root_web_main_entry.ts` importing `'./root_web_container.js'` pointing to `root_web_container.ts`). The existing end-to-end tests (`e2e_chained_python_import_graph_reaches_capabilities` at line 270 in this file, and `aes503_typescript_di_wiring_reachable` in `crates/orphan-rules/tests/acceptance_DI_wiring.rs:194`) only test extensionless imports or Python imports.

**Suggestion:**
Add an end-to-end test (either in `crates/filesystem/tests/unit_filesystem_import_resolution.rs` or `crates/orphan-rules/tests/acceptance_DI_wiring.rs`) that writes a multi-file TypeScript workspace on disk where modules import each other using explicit `.js` specifiers (e.g., `import { Container } from './root_web_container.js';`), runs `FilesystemRequest::build_orphan_graph_context`, and asserts that the resulting import graph contains reachability edges from the entry file through to the target `.ts` files.
**Status:** open

---

### 2. Suggestion (missing reverse `.mts` and `.cts` swap tests)

**File:line:** `crates/shared/src/filesystem/utility_import_resolution.rs:444-448` and `crates/filesystem/tests/unit_filesystem_import_resolution.rs:691-722`
**Severity:** suggestion
**Description:**
`resolve_import_target` implements 8 extension-swapping rules:
- `.mjs` -> `.mts`
- `.mts` -> `.mjs`
- `.cjs` -> `.cts`
- `.cts` -> `.cjs`

The test suite includes `test_mjs_import_resolves_to_mts_file_on_disk` and `test_cjs_import_resolves_to_cts_file_on_disk`, but omits the reverse direction: `.mts` importing a `.mjs` file on disk, and `.cts` importing a `.cjs` file on disk. Additionally, only the first candidate in multi-candidate swap lists (e.g., `.js` -> `.tsx` and `.js` -> `.jsx` in `&[".ts", ".tsx", ".jsx"]`) is exercised.

**Suggestion:**
Add unit tests `test_mts_import_resolves_to_mjs_file_on_disk` and `test_cts_import_resolves_to_cjs_file_on_disk` (and optionally a fallback test verifying `.js` resolves to `.tsx` when `.ts` is absent) to cover all branches of the extension-swap logic.
**Status:** open

---

### 3. Suggestion (untested candidate priority when multiple files share a stem)

**File:line:** `crates/shared/src/filesystem/utility_import_resolution.rs:425-465` and `crates/filesystem/tests/unit_filesystem_import_resolution.rs:622-810`
**Severity:** suggestion
**Description:**
None of the new tests populate `all_files_set` with multiple files matching the same stem (for example, when both `./container.ts` and `./container.tsx` exist on disk for an import of `./container.js`, or when both `./container.js` and `./container.ts` exist on disk for an import of `./container.js`). Because `swap_candidates.iter().find_map(...)` picks the first match in array order, a future reordering of `&[".ts", ".tsx", ".jsx"]` would silently change resolution behavior without any test failing.

**Suggestion:**
Add boundary tests verifying:
1. When both `./foo.js` and `./foo.ts` exist on disk and a module imports `./foo.js`, `all_files_set.contains(normalized)` matches `./foo.js` first and never swaps.
2. When `./foo.js` does not exist and both `./foo.ts` and `./foo.tsx` exist on disk, `./foo.ts` is deterministically selected according to `swap_candidates` order.
**Status:** open

---

### 4. Suggestion (missing tests for dotted directory + extension swap and root-level extension swap)

**File:line:** `crates/shared/src/filesystem/utility_import_resolution.rs:412-465` and `crates/filesystem/tests/unit_filesystem_import_resolution.rs:559-794`
**Severity:** suggestion
**Description:**
Two boundary interactions with `resolve_import_target` are not covered by tests:
1. **Root-level (`src_dir.is_empty()`) extension swapping:** `test_root_relative_dot_slash_resolves` and `test_root_relative_dotdot_resolves` (lines 559–615) test extensionless imports from a root-level `main.js`, and all new extension-swapping tests use nested source paths (e.g. `packages/...`). Neither `main.ts` importing `./container.js` (resolving to root `container.ts`) nor `main.ts` importing `../shared/util.js` (resolving to `shared/util.ts`) is tested.
2. **Combined dotted directory + explicit extension swap:** `test_directory_with_dot_in_name_still_gets_extension_added` (line 765) tests `./lib.v2/foo` (extensionless), but does not test `./lib.v2/container.js` resolving to `packages/client/src/lib.v2/container.ts`.

**Suggestion:**
Add test cases for root-level `.js` -> `.ts` resolution (with both `./` and `../`) and for `.js` -> `.ts` resolution when the parent directory contains a dot (e.g. `./lib.v2/container.js` -> `lib.v2/container.ts`).
**Status:** open

---

### 5. Nit (inconsistent boilerplate across new tests)

**File:line:** `crates/filesystem/tests/unit_filesystem_import_resolution.rs:648-722`
**Severity:** nit
**Description:**
In the newly added tests, `test_jsx_import_resolves_to_tsx_file_on_disk` (line 648), `test_mjs_import_resolves_to_mts_file_on_disk` (line 693), and `test_cjs_import_resolves_to_cts_file_on_disk` (line 708) omit `let _orch = make_orchestrator();`, whereas all other tests in the file (including the other new tests) initialize `let _orch = make_orchestrator();`.

**Suggestion:**
Add `let _orch = make_orchestrator();` to the three tests for consistency with the rest of the test file.
**Status:** open

---

## Summary

| # | Severity | File:line | Description | Status |
|---|----------|-----------|-------------|--------|
| 1 | bug | `crates/filesystem/tests/unit_filesystem_import_resolution.rs:622-810` | No end-to-end test through `FilesystemRequest::build_orphan_graph_context` for TypeScript imports with explicit `.js` extensions | open |
| 2 | suggestion | `crates/shared/src/filesystem/utility_import_resolution.rs:444-448` | Reverse swaps `.mts` -> `.mjs` and `.cts` -> `.cjs` (and secondary `.js` -> `.tsx`/`.jsx` swaps) are untested | open |
| 3 | suggestion | `crates/shared/src/filesystem/utility_import_resolution.rs:425-465` | Candidate priority / exact-match precedence is untested when multiple files share the same stem on disk | open |
| 4 | suggestion | `crates/shared/src/filesystem/utility_import_resolution.rs:412-465` | Root-level (`src_dir == ""`) extension swapping and combined dotted-directory + extension swapping are untested | open |
| 5 | nit | `crates/filesystem/tests/unit_filesystem_import_resolution.rs:648-722` | 3 of the new tests omit `let _orch = make_orchestrator();` unlike the rest of the file | open |