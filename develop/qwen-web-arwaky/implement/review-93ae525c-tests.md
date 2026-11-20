# Re-Review — fix-py-import-parser (round 2)

**Scope:** Python import parser fix in `modules/shared/src/common/utility_folder_compiler.py` and the expanded regression test suite in `modules/jobs/tests/unit_folder_compiler.py`. Same scope as round 1.

**Verdict:** All eight in-scope issues from round 1 are properly resolved. The implementer deleted the redundant `_PY_MODULE_PAREN` regex (and its loop) and correctly retained the single `_PY_MODULE` regex with `[^\n]+`, which matches both plain and parenthesized imports at the module-path level. Five new/expanded tests were added. No new problems were introduced by the changes.

---

## Verification of round-1 fixes (all verified, not just asserted)

### Issue 1 (simplicity) — `_PY_MODULE_PAREN` redundant → **fixed, verified**
- `grep` confirms `_PY_MODULE_PAREN` is fully deleted; only `_PY_MODULE` at `utility_folder_compiler.py:338` remains.
- Probed the retained regex against every parenthesized form the deleted regex handled: multi-line, single-line, empty `()`, paren-close-without-newline, and paren-as-second-import-in-a-chain. All resolve the module path correctly. The deletion is behavior-preserving.
- `modules/shared/tests/ modules/jobs/tests/ -m "not benchmark"` → 428 passed. No regression from the deletion.

### Issue 2 (nit) — `re.DOTALL` no-op → **fixed, verified**
- `re.DOTALL` is gone along with `_PY_MODULE_PAREN`; no dangling flag remains.

### Issue 3 (suggestion) — aliased import coverage → **fixed, verified**
- `test_python_aliased_imports` (`unit_folder_compiler.py:82`) covers both `import utils.first as f1` and `from utils.second import run_second as rs`, asserting both `first.py` and `second.py` resolve with origin `("a.py",)`.

### Issue 4 (suggestion) — 3+ consecutive imports → **fixed, verified**
- `test_python_consecutive_from_imports` (`unit_folder_compiler.py:53`) now uses three consecutive `from utils.X import ...` lines (first, second, third) and asserts all three resolve with origin `("a.py",)`.

### Issue 5 (suggestion) — mixed parenthesized + plain in one file → **fixed, verified**
- `test_python_mixed_parenthesized_and_plain_imports` (`unit_folder_compiler.py:116`) combines `from utils.helper import (\n    run_one,\n)` with `from utils.second import run_second` in one file, asserting both modules resolve with origin `("a.py",)`.

### Issue 6 (suggestion) — single-line parenthesized → **fixed, verified**
- `test_python_parenthesized_single_line` (`unit_folder_compiler.py:103`) covers `from utils.helper import (run_one, run_two)`, asserting `helper.py` resolves with origin `("a.py",)`.

### Issue 7 (suggestion) — trailing comments → **fixed, verified**
- `test_python_import_with_trailing_comment` (`unit_folder_compiler.py:136`) covers `from utils.helper import run_one  # needed for caching`, asserting `helper.py` resolves with origin `("a.py",)`.

### Issue 8 (nit) — comment accuracy → **confirmed accurate**
- The regression comment at `unit_folder_compiler.py:54-56` remains accurate and now correctly describes the three-line scenario.

---

## New tests — quality assessment

All six Python tests (existing two + four new, plus the retained parenthesized test) are well-structured:
- Consistent use of the `_write` helper throughout.
- Test names follow the `test_python_*` convention used by `test_python_import_from_outside_folder` / `test_python_relative_import`.
- Assertions are specific: membership in `names` set, then `origins[f] == ("a.py",)` for each module — not mere "doesn't throw".
- Comments are short, factual, and explain the non-obvious constraint each test pins.

---

## Pre-existing gaps (unchanged, out of scope — not re-litigated)

The following were correctly left out of scope in round 1 and remain unaddressed; they are pre-existing parse limitations, not regressions from this fix:
- `import os; import utils.h1` (semicolon) — only first resolved.
- `import os, sys` (comma multi-module) — only first resolved.

No action required for this PR.

---

## Summary

All 8 in-scope round-1 issues are properly addressed; no new issues introduced. Test coverage for the Python import parser is now comprehensive for the changed code paths (consecutive imports, aliased imports, parenthesized single/multi-line, mixed forms, trailing comments). The suite is green (428 passed), linters clean, and arch scan reports 0 violations. **Approve.**