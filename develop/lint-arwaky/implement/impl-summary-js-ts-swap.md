# Implementation Summary: Fix `.js` Import Specifier Resolution for TypeScript Projects

## Overview
Fixed `resolve_import_target` in `crates/shared/src/filesystem/utility_import_resolution.rs` so relative ESM/TypeScript imports with explicit file extensions (such as `./root_web_container.js` pointing to `root_web_container.ts` on disk) resolve correctly, and fixed the overly broad `contains('.')` check that skipped extension addition when parent directories contained dots (such as `./lib.v2/foo`). Refactored the resolution logic using a shared `probe` helper closure and a clean `match` on `Path::extension()` to address all panel review findings.

## Files Changed

### 1. `/home/raka/orca/workspaces/tools/fix-js-ts-import-resolution/crates/shared/src/filesystem/utility_import_resolution.rs`
- **Function modified:** `resolve_import_target` (lines 422–451)
- **Changes:**
  1. Extracted a local `probe` closure (`|stem: &str, exts: &[&str]|`) to deduplicate extension probing across the no-extension branch (`[".ts", ".js", ".tsx", ".jsx", ".rs", ".py"]`) and the extension-swap branch (Suggestions 4 & 5).
  2. Replaced `!normalized.contains('.')` with `Path::new(&normalized).extension().is_none()`, ensuring paths whose parent directories contain dots (e.g., `./lib.v2/foo`) still receive extension suffix probing.
  3. Replaced the 8-arm `if/else` string-suffix chain and `strip_suffix(...).unwrap_or(...)` with a `match` on `normalized_path.extension().and_then(|ext| ext.to_str())` (Suggestions 4 & Nit):
     - `Some("js")` → `[".ts", ".tsx", ".jsx"]`
     - `Some("jsx")` → `[".tsx", ".ts", ".js"]`
     - `Some("ts")` (excluding `.d.ts` declaration files where `stem.ends_with(".d")`) → `[".tsx", ".js", ".jsx"]`
     - `Some("tsx")` → `[".ts", ".jsx", ".js"]`
     - `Some("mjs")` ↔ `Some("mts")`
     - `Some("cjs")` ↔ `Some("cts")`
     - Any other extension returns `&[]` (`None`).

### 2. `/home/raka/orca/workspaces/tools/fix-js-ts-import-resolution/crates/filesystem/tests/unit_filesystem_import_resolution.rs`
- **Changes:**
  - Added helper `make_typescript_import(source_file: &str, raw_path: &str) -> ImportEntry` and imported `FilesystemRequest` and `IFilesystemAggregate`.
  - Added 15 unit and end-to-end tests:
    - `test_js_import_resolves_to_ts_file_on_disk`
    - `test_jsx_import_resolves_to_tsx_file_on_disk`
    - `test_ts_import_resolves_to_js_file_on_disk`
    - `test_tsx_import_resolves_to_jsx_file_on_disk`
    - `test_mjs_import_resolves_to_mts_file_on_disk` (Bug 1)
    - `test_mts_import_resolves_to_mjs_file_on_disk` (Bug 1 / Suggestion 1)
    - `test_cjs_import_resolves_to_cts_file_on_disk` (Bug 1)
    - `test_cts_import_resolves_to_cjs_file_on_disk` (Bug 1 / Suggestion 1)
    - `test_js_import_prefers_ts_when_both_ts_and_tsx_exist` (Bug 2)
    - `test_exact_file_match_takes_precedence_over_swap` (Suggestion 2)
    - `test_non_js_ts_extensions_unaffected`
    - `test_dts_declaration_import_does_not_swap` (Bug 4)
    - `test_directory_with_dot_in_name_still_gets_extension_added`
    - `test_dotted_directory_with_js_extension_swap` (Suggestion 3)
    - `test_root_level_extension_swap_resolves` (Suggestion 3)
    - `test_unresolvable_relative_import_returns_none`
    - `e2e_js_specifier_import_graph_reaches_target_files` (Bug 3: end-to-end test running `FilesystemRequest::build_orphan_graph_context` on a multi-file TypeScript workspace with `.js` specifiers importing `.ts` modules)

## Verification
- `cargo fmt --all -- --check`: Passed with zero diffs.
- `cargo clippy --all-targets -- -D warnings`: Passed with zero errors.
- `CARGO_INCREMENTAL=0 cargo nextest run -p filesystem-lint-arwaky -p orphan-rules-lint-arwaky -p shared-common-lint-arwaky -p shared-doc-rules-lint-arwaky`: All 272 tests passed.
- `lint-arwaky-cli report .`: 0 violations (0 delta).