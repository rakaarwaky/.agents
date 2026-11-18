# AES103 — ignore `conftest.py` by default

Implements the user request: `conftest.py` must be silently ignored by AES103
via a constant, so no `architecture.rules.AES103.exceptions` entry is needed.

## Files changed

| Path | Change |
| ---- | ------ |
| `crates/shared/src/naming_rules/taxonomy_naming_rules_constant.rs` | Added `PYTEST_CONFTEST_FILENAME` constant with value `"conftest.py"`, documented the same way neighbouring constants are (why it is ignored). |
| `crates/naming-rules/src/capabilities_test_file_prefix_checker.rs` | Imported `PYTEST_CONFTEST_FILENAME`; extended `is_barrel()` to match it alongside the existing barrels; extended the inline comment to explain pytest auto-discovers `conftest.py` as a shared fixture file, so it carries no test of its own. |
| `crates/naming-rules/tests/unit_naming_rules_test_prefix_checker.rs` | Added unit test `conftest_py_is_skipped_even_without_a_legal_prefix` asserting `check("crates/calc/tests/conftest.py")` returns `None`. No existing test removed. |
| `crates/naming-rules/tests/acceptance_AES103.rs` | Added acceptance test `conftest_py_is_skipped_by_default` asserting `audit("crates/calc/tests/conftest.py")` returns `None`. No existing test removed. |
| `crates/naming-rules/FRD.md` | Added one line to the AES103 Business Logic list stating `conftest.py` is silently skipped by default (like barrels), no config exception required. |
| `ARCHITECTURE.md` | Added a "Skipped by default" note under the AES103 Legal Test Prefixes table listing `conftest.py` plus the barrels. |

## New constant

- `PYTEST_CONFTEST_FILENAME` = `"conftest.py"` in `crates/shared/src/naming_rules/taxonomy_naming_rules_constant.rs`

## New tests

- `conftest_py_is_skipped_even_without_a_legal_prefix` (unit): a file literally
  named `conftest.py` inside `tests/` produces NO AES103 finding.
- `conftest_py_is_skipped_by_default` (acceptance): same assertion through the
  acceptance-test `audit` seam.

## Verification

`cargo fmt --all -- --check`: pass (no diff).

`CARGO_INCREMENTAL=0 cargo nextest run -p naming-rules-lint-arwaky --lib --tests`:
```
Summary [   0.124s] 131 tests run: 131 passed, 0 skipped
```
(includes `conftest_py_is_skipped_even_without_a_legal_prefix` PASS)

`CARGO_INCREMENTAL=0 cargo clippy -p shared-naming-rules-lint-arwaky -p naming-rules-lint-arwaky --all-targets -- -D warnings`:
```
Finished `dev` profile [unoptimized] target(s) in 4.45s
```
(no warnings; note: the task's `-p shared` package name does not exist in this
workspace, so the actual crate name `shared-naming-rules-lint-arwaky` was used)

Config files (`lint_arwaky.config.yaml`, `crates/shared/config/lint_arwaky.config.yaml`)
were NOT modified. No fixtures in `workspaces-bad/` / `workspaces-good/` were
modified. No other AES rule was touched.
