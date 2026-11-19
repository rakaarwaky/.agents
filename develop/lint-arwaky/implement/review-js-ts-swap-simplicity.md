# Simplicity Review — fix-js-ts-import-resolution

**Scope:** Over-engineering and unnecessary complexity only.
**Baseline:** 2 modified files, 247 insertions.
**Review target:** Changes to `utility_import_resolution.rs` (extension-swap logic) and `unit_filesystem_import_resolution.rs` (new tests).

---

## Findings

### 1. Suggestion (yagni / shrink)
**File:** `crates/shared/src/filesystem/utility_import_resolution.rs`
**Lines:** 436–466

**Description:**
The extension-swap dispatch uses an 8-branch `if/else` chain, each arm returning a `(&str, &[&str])` tuple, followed by an `if !swap_candidates.is_empty()` guard. The tuple's first element (`suffix`) is only ever used to `strip_suffix` the original extension off the stem — but every swap candidate already carries its own leading dot, so `strip_suffix` of the *matched* suffix is redundant. The entire block collapses to a single table-driven lookup plus one `find_map` with no `suffix` tracking at all.

**Suggestion:**
Replace the 30-line tuple chain with a `match` on `Path::new(&normalized).extension()` mapping to a candidate slice, then one `find_map`:

```rust
} else {
    let swap: &[&str] = match normalized.rsplit('.').next().unwrap_or("") {
        "js"  => &[".ts", ".tsx", ".jsx"],
        "jsx" => &[".tsx", ".ts", ".js"],
        "ts"  => &[".tsx", ".js", ".jsx"],
        "tsx" => &[".ts", ".jsx", ".js"],
        "mjs" => &[".mts"],
        "mts" => &[".mjs"],
        "cjs" => &[".cts"],
        "cts" => &[".cjs"],
        _     => &[],
    };
    let stem = normalized.rsplit_once('.').map(|(s, _)| s).unwrap_or(&normalized);
    swap.iter().find_map(|ext| {
        let c = format!("{}{}", stem, ext);
        all_files_set.contains(c.as_str()).then_some(c)
    })
}
```

This removes the `suffix` variable, the `!swap_candidates.is_empty()` guard, and the redundant `else { None }` branch, cutting the block roughly in half while preserving identical behavior.

---

### 2. Nit (shrink)
**File:** `crates/shared/src/filesystem/utility_import_resolution.rs`
**Lines:** 433–435 vs 455–465

**Description:**
The extension-probe block (lines 427–434) and the swap-probe block (lines 455–465) both contain the identical `format!("{}{}", ..., ext)` → `all_files_set.contains` → `Some`/`None` pattern in a `find_map`. This duplicated closure can be extracted into a single local helper `probe = |stem: &str, exts: &[&str]| exts.iter().find_map(...)` at the top of the `else` branch, removing the second copy.

**Suggestion:**
Extract a `probe` closure or a tiny `fn find_in_set(candidates: impl Iterator<Item=String>, set: &HashSet<&str>) -> Option<String>` local helper and reuse it for both the no-extension probe and the swap probe.

---

## Summary

| # | Severity | File | Lines | Issue |
|---|----------|------|-------|-------|
| 1 | suggestion | shared/.../utility_import_resolution.rs | 436–466 | 8-arm tuple chain + redundant suffix/guard; replace with `match` + single `find_map` |
| 2 | nit | shared/.../utility_import_resolution.rs | 433–435, 455–465 | Duplicated `format!`+`contains` probe loop; extract single helper |

No test-side findings — the new tests are direct, single-purpose regressions and the `make_typescript_import` helper is appropriately reused across 7 of them.