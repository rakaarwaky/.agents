## Implementation Summary — Bug fix: Python import parser skips consecutive `from ... import ...` lines

### Files changed

**1. `modules/shared/src/common/utility_folder_compiler.py`** (production code)

- `_PY_MODULE` regex (line ~337): Changed the imported-names character class from `[\w,*\s]+` to `[^\n]+`, so the match stops at the line terminator and cannot consume the `from ...` prefix of the next line. The previous `\s` matched newlines, and since `f/r/o/m/shared` are all word characters, consecutive `from ... import ...` lines were merged into a single match, silently skipping the second (and third, etc.) module.
- Added `_PY_MODULE_PAREN` regex (line ~338): `r"^\s*from\s+([.\w]+)\s+import\s*\(\s*([^)]*)\s*\)"` with `re.MULTILINE | re.DOTALL` to match parenthesized multi-line imports like `from x import (\n    a,\n    b,\n)`.
- Updated `_parse_imports` (lines ~380-387): Added a loop over `_PY_MODULE_PAREN.finditer(content)` that appends the matched module name (group 1) to the spec list.

**2. `modules/jobs/tests/unit_folder_compiler.py`** (regression test)

Added two tests to `TestCollectFolderFilesWithImports`:
- `test_python_consecutive_from_imports`: writes `a.py` with two consecutive `from utils.first import ...` / `from utils.second import ...` lines and asserts both `first.py` and `second.py` are included in `collect_folder_files_with_imports` output with correct origins.
- `test_python_parenthesized_from_import`: writes `a.py` with a parenthesized multi-line `from utils.helper import (\n    run_one,\n    run_two,\n)` and asserts `helper.py` is included with correct origin.

### Plan decisions

- Used `[^\n]+` rather than dropping `\s` and using `[\w,*]+`, because `import a, b` includes whitespace after commas; `[^\n]+` captures everything on the line after `import` without crossing line boundaries.
- The parenthesized regex captures only the module path (group 1), not individual names — the resolver needs `shared.src.memory.utility_memory_helper`, not `shared.src.memory.utility_memory_helper.run_one`. Individual names inside parens are irrelevant for folder-compile file discovery.
- No new imports needed; `re` was already imported at module top.

### Verification

- `uv run python -m pytest modules/jobs/tests/ -v` — 111 passed (includes the 2 new regression tests).
- `uv run python -m pytest modules/shared/tests/ -v` — 313 passed.
- `uv run ruff format --check modules/ tests/` — 449 files formatted, pass.
- `uv run ruff check modules/ tests/` — All checks passed.
- `lint-arwaky-cli scan .` — Total: 0 violations.
- mypy errors across `modules/` are pre-existing (pytest stubs missing, untyped decorators in test files); none introduced by this change.
- Ran `qwen-web-arwaky folder modules/memory` against the real target at `/home/raka/.agents/skills/software-development/tools/` — output now contains `## ../shared/src/memory/utility_memory_helper.py *(imported by src/capabilities_memory_path.py)*` as a proper content block, confirming the original bug is resolved.