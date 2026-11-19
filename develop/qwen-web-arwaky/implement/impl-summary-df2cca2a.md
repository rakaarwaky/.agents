# Implementation Summary — Option A: Default boundary to git repo root

## Task

Change the default boundary step (step 3) in `_resolve_boundary_root` of
`modules/shared/src/common/utility_folder_compiler.py` from `folder_path.parent.resolve()`
to walking up to find the git repo root, falling back to `folder_path.parent.resolve()`
when not inside a git repo.

## Files changed

### 1. `modules/shared/src/common/utility_folder_compiler.py` (edit)

Added helper `_find_git_root(start: Path) -> Path | None` that walks up from
`start` looking for a `.git` entry (directory for clone, file for
worktree/submodule). Returns the root path if found, `None` otherwise.
Stops at the filesystem root or the user's home directory boundary.
No subprocess/git dependency (Utility/Taxonomy layer constraint).

Modified `_resolve_boundary_root` to insert the git-root step between the
env var and the `folder_path.parent` fallback:

```python
if boundary_root is not None:
    return Path(boundary_root).expanduser().resolve()
env_root = os.environ.get(_WORKSPACE_ROOT_ENV, "").strip()
if env_root:
    return Path(env_root).expanduser().resolve()
git_root = _find_git_root(folder_path)
if git_root is not None:
    return git_root.resolve()
return folder_path.parent.resolve()
```

Updated the docstring of `collect_folder_files_with_imports` to document the
new default boundary (git repo root, then `folder_path.parent`).

### 2. `modules/jobs/src/capabilities_folder_compiler.py` (edit — docstring only)

Updated the `boundary_root` argument docstring of `FolderCompiler.compile_folder`
to document that the default boundary is the env var, then the git repo root
when inside one, else the scanned folder's parent.

### 3. `modules/jobs/tests/unit_folder_compiler.py` (edit)

Added test class `TestGitRootBoundary` with 5 tests:

- `test_default_boundary_is_git_root_when_inside_git_repo` — creates a
  fake git repo root (`repo/.git` dir), target folder `repo/modules/memory`,
  and `repo/PRD.md` linked from `index.md` via `../../PRD.md`. Asserts PRD is
  included in the output when no `boundary_root` or env var is set.
- `test_git_root_fallback_when_no_git_dir` — target folder with no `.git`
  ancestor, importing `...outside.py` from `tmp_path`. Boundary falls back to
  `folder.parent`, so `outside.py` is refused and appears in `skipped`.
- `test_explicit_boundary_still_wins` — passes `boundary_root=narrow`
  explicitly inside a git repo; asserts git-root default is bypassed and only
  files under `narrow` are included.
- `test_env_var_still_wins` — sets `QWEN_WORKSPACE_ROOT` env var inside a git
  repo; asserts env var boundary is used even when inside a git repo.
- `test_git_file_for_worktree` — creates a `.git` file (not dir) at repo root
  (worktree/submodule simulation); asserts boundary is still the repo root.

Existing boundary tests (`test_import_outside_explicit_boundary_refused`,
`test_import_inside_explicit_boundary_kept`,
`test_import_escape_refused_by_boundary` default-parent case,
`test_markdown_exfiltration_link_refused`) unchanged and passing.

## Plan decisions

- `_find_git_root` uses a pure filesystem walk for `.git` (dir or file) rather
  than `subprocess.run(["git", ...])`, per the constraint that the
  Taxonomy/Utility layer must not depend on subprocess/git availability.
- The walk stops at the user's home directory boundary and at the filesystem
  root, avoiding scanning the whole filesystem upward.
- `_find_git_root` returns `Path | None` precisely (no `Any`).
- No dead code left behind; no new modules/config/type helpers introduced
  beyond the single helper for its single caller.

## CI gate results

- `uv run ruff format --check` on the three files: **pass** (3 files already formatted)
- `uv run ruff check` on the three files: **pass** (All checks passed!)
- `uv run mypy modules/shared/src/common/utility_folder_compiler.py modules/jobs/src/capabilities_folder_compiler.py`: **pass** (Success: no issues found in 2 source files)
- `uv run python -m pytest modules/jobs/tests/unit_folder_compiler.py -v`: **pass** (46 passed, 1 warning)
- Filtered boundary run `-k "boundary or escape or exfiltration or import"`: **pass** (32 passed, 14 deselected)
- `lint-arwaky-cli scan .`: **pass** (Total: 0 violations)

## Smoke test output

Full test run output (all 46 tests):
```
============================= test session starts ==============================
platform linux -- Python 3.14.9, pytest-9.2.0, pluggy-1.6.0
collected 46 items

modules/jobs/tests/unit_folder_compiler.py ............................. [100%]

======================== 46 passed, 1 warning in 0.26s =========================
```

Filtered boundary/escape/exfiltration/import run:
```
collected 46 items / 14 deselected / 32 selected
modules/jobs/tests/unit_folder_compiler.py ............................. [100%]

================= 32 passed, 14 deselected, 1 warning in 0.17s =================
```

lint-arwaky-cli scan report:
```
Lint Arwaky v3.17.0 — Scan Report
Target: .
Total: 0 violations
```
