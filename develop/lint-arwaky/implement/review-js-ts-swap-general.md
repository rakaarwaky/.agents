````markdown
# General Review — JS/TS Import Resolution Swap (`fix-js-ts-import-resolution`)

## Scope
- `/home/raka/orca/workspaces/tools/fix-js-ts-import-resolution/crates/shared/src/filesystem/utility_import_resolution.rs` (`resolve_import_target`, lines ~423–468)
- `/home/raka/orca/workspaces/tools/fix-js-ts-import-resolution/crates/filesystem/tests/unit_filesystem_import_resolution.rs` (9 new tests)

## Verification completed
- `CARGO_INCREMENTAL=0 cargo nextest run -p filesystem-lint-arwaky`: 266/266 passed
- `cargo fmt --all -- --check`: clean
- `cargo clippy --all-targets -- -D warnings`: clean (no warnings on changed code)
- `lint-arwaky-cli report .`: 0 violations, 0 delta

---

## Findings

### 1. [bug] Missing reverse-direction tests for `.mts`→`.mjs` and `.cts`→`.cjs`
- **Severity:** bug
- **File:line:** `crates/filesystem/tests/unit_filesystem_import_resolution.rs:697-727`
- **Description:**
  The swap logic in `resolve_import_target` (lines 444-451) supports bidirectional swaps for `.mjs↔.mts` and `.cjs↔.cts`, but the test suite only covers the forward direction: `.mjs` import → `.mts` on disk (`test_mjs_import_resolves_to_mts_file_on_disk`) and `.cjs` import → `.cts` on disk (`test_cjs_import_resolves_to_cts_file_on_disk`). There are no tests verifying that a `.mts` import specifier resolves to a `.mjs` file on disk, or `.cts` → `.cjs`.
- **Suggestion:** Add `test_mts_import_resolves_to_mjs_file_on_disk` and `test_cts_import_resolves_to_cjs_file_on_disk` to lock in the reverse direction and prevent regressions.
- **Status:** open

### 2. [bug] No test for ambiguous resolution when both `.ts` and `.tsx` (or `.tsx` and `.ts`) exist on disk
- **Severity:** bug
- **File:line:** `crates/shared/src/filesystem/utility_import_resolution.rs:436-464` / `crates/filesystem/tests/unit_filesystem_import_resolution.rs:622-696`
- **Description:**
  The swap logic uses `find_map` over an ordered candidate list (e.g. `.js` → `[".ts", ".tsx", ".jsx"]`), which is deterministic: the first candidate present in `all_files_set` wins. When both `.ts` and `.tsx` exist for a `.js` import, `.ts` is returned first. This is acceptable behavior but is untested — there is no test covering the case where multiple swapped candidates exist simultaneously.
- **Suggestion:** Add a test such as `test_js_import_prefers_ts_when_both_ts_and_tsx_exist` importing `./foo.js` when both `foo.ts` and `foo.tsx` are in `all_files_set`, asserting `.ts` wins per the swap order.
- **Status:** open

### 3. [nit] Extension-match via `ends_with` can match `.d.ts` declaration files
- **Severity:** nit
- **File:line:** `crates/shared/src/filesystem/utility_import_resolution.rs:440`
- **Description:**
  `normalized.ends_with(".ts")` is true for `packages/types/index.d.ts` (a TypeScript declaration file). A `./index.d.ts` import specifier would then swap to `.tsx`, `.js`, `.jsx`. Swapping a `.d.ts` to `.js` is not harmful (it only resolves when a file actually exists in `all_files_set`), but it conflates declaration files with source files. The more precise check would verify the file has a bare extension using `Path::new(&normalized).extension()` before applying swaps.
- **Suggestion:** Keep as-is unless declaration files cause false resolutions; if so, gate swaps on `normalized` having a clean extension via `Path::new(&normalized).extension()` matching exactly `.ts`/`.js` etc. rather than substring `ends_with`.
- **Status:** open

### 4. [suggestion] TypeScript/JavaScript swap branch applies regardless of `Language` field
- **Severity:** suggestion
- **File:line:** `crates/shared/src/filesystem/utility_import_resolution.rs:426-468`
- **Description:**
  The extension-swapping branch in `resolve_import_target` (lines 426-468) runs for any import whose raw path starts with `./` or `../` and has an extension, without checking `imp.language`. A Rust file importing `./something.js` (unusual but possible) would trigger JS/TS swaps, and a Python file importing `./something.js` would similarly swap. In practice, `extract_js_imports` only produces JS/TS language entries for ESM specifiers, and the swap only succeeds if a matching file exists in `all_files_set`, so no incorrect resolutions can be fabricated.
- **Suggestion:** Optionally gate the swap block on `imp.language` being `Language::TypeScript` or `Language::JavaScript` for clarity and to document intent. Not a defect.
- **Status:** open

### 5. [suggestion] `strip_suffix` fallback to full normalized path when stem is empty
- **Severity:** nit
- **File:line:** `crates/shared/src/filesystem/utility_import_resolution.rs:456`
- **Description:**
  `let stem = normalized.strip_suffix(suffix).unwrap_or(&normalized);` — if `normalized` ends with `.js` but is exactly `.js` (zero-length stem), `strip_suffix` returns `Some("")`, so `stem` becomes `""`. Candidates like `.ts`, `.tsx`, `.jsx` would then be checked against `all_files_set`, which can never contain bare `.ts`. Harmless, but the `unwrap_or(&normalized)` branch is dead code for valid paths (it never triggers because `suffix` only equals a suffix that `ends_with` confirmed).
- **Suggestion:** No change needed; `unwrap_or` is defensive but unreachable in practice.
- **Status:** open

---

## Summary
The implementation correctly fixes the primary bug (`.js` imports resolving to `.ts` files) and the directory-dot regression (`./lib.v2/foo`). All four acceptance checks pass. The change is tightly scoped to `resolve_import_target` with no scope creep. Remaining gaps are test-coverage additions (reverse `.mts`/`.cts` swaps, ambiguous multi-candidate resolution) and minor style hardening, none of which block correctness.
````