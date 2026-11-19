# Review Notes — Test Coverage & Quality

Commit: boundary-git-root worktree
Files reviewed:
- `modules/shared/src/common/utility_folder_compiler.py` (new `_find_git_root` + modified `_resolve_boundary_root`)
- `modules/jobs/tests/unit_folder_compiler.py` (new `TestGitRootBoundary` class)

All tests pass (46 passed). No failures found. The following are coverage/quality gaps, all with Status: open.

---

## Issue 1 — Missing test: folder at the filesystem root (no parent)

**Severity:** suggestion  
**File:** modules/jobs/tests/unit_folder_compiler.py:496 (TestGitRootBoundary class area)  
**Description:** `_find_git_root` (utility_folder_compiler.py:716-729) terminates the upward walk when `cur.parent == cur` (the filesystem root). `TestGitRootBoundary` has no test that scans a folder whose only ancestor chain reaches the filesystem root with no `.git` anywhere. In that case the boundary should fall back to `folder_path.parent`, which at the real root resolves to itself; no test exercises this code path or asserts the resulting behavior (refusal vs. inclusion of sibling imports).  
**Suggestion:** Add a test that places the target folder under a path whose upward walk cannot find `.git` and asserts the parent-boundary fallback still refuses escaping imports. Note: in CI `tmp_path` lives under `/tmp`, which itself is not a filesystem root, so a dedicated fixture/dir under a controlled mount would be needed to reach the true root; alternatively unit-test `_find_git_root`/`_resolve_boundary_root` directly with a path constructed to stop at root.  
**Status:** open

---

## Issue 2 — Missing test: folder inside the home directory but no git repo

**Severity:** suggestion  
**File:** modules/jobs/tests/unit_folder_compiler.py:496 (TestGitRootBoundary class area)  
**Description:** `_find_git_root` terminates the walk at `cur == home` (utility_folder_compiler.py:729) and returns `None`, so the boundary falls back to `folder_path.parent`. `TestGitRootBoundary` has no test where the scanned folder resides inside `Path.home()` with no `.git` ancestor, to confirm the home-boundary stop does not escalate past home and does not accidentally treat home as a boundary.  
**Suggestion:** Add a test using a target under `Path.home()` (or monkeypatched `Path.home()`) with no `.git` ancestor, asserting the fallback boundary is `folder_path.parent` and an escaping import is refused. Keep it hermetic (use `monkeypatch` on `Path.home` rather than writing to the real home directory).  
**Status:** open

---

## Issue 3 — Existing boundary tests depend on environment assumptions (tmp_path has no `.git` ancestor; tmp_path outside HOME)

**Severity:** suggestion  
**File:** modules/jobs/tests/unit_folder_compiler.py:356-448 (TestImportBoundaryConfinement)  
**Description:** The pre-existing boundary tests (`test_import_escape_refused_by_boundary` default-parent case, `test_git_root_fallback_when_no_git_dir`, etc.) rely on `tmp_path` (under `/tmp`) having no `.git` anywhere up to `/`, and on `/tmp` being outside `HOME` so the home stop never triggers. They pass locally because `/tmp/.git` and `/.git` do not exist and `HOME=/home/raka`. This is environment-dependent: a CI/dev machine where an ancestor of `tmp_path` (or `/`) contains `.git`, or where `HOME` lies inside the `tmp_path` tree, would silently change the resolved boundary and could flip assertions without any code change.  
**Suggestion:** Make these tests hermetic against the environment. Either (a) explicitly assert `_find_git_root(target) is None` for the no-git targets, or (b) set `QWEN_WORKSPACE_ROOT`/`boundary_root` explicitly in every boundary test so the result does not depend on the absence of `.git` ancestors of `tmp_path`.  
**Status:** open

---

## Issue 4 — Tests verify outcomes, not the intermediate boundary-resolution logic

**Severity:** suggestion  
**File:** modules/jobs/tests/unit_folder_compiler.py:496-570 (TestGitRootBoundary)  
**Description:** All five new tests infer the resolved boundary indirectly (a PRD/import is included or refused). None directly assert what `_resolve_boundary_root` or `_find_git_root` returned, so a refactor that changes which root is chosen while keeping the same include/exclude outcome would not be caught. In particular, precedence between env var and explicit `boundary_root` (env wins per the docstring? actually explicit wins per code) is only partially exercised: `test_env_var_still_wins` does not pass `boundary_root`, so it does not prove explicit-parameter precedence over env.  
**Suggestion:** Add direct unit tests for `_resolve_boundary_root` / `_find_git_root` that assert the exact returned `Path` for each precedence case, including explicit-boundary-over-env and env-over-git-root ordering.  
**Status:** open

---

## Issue 5 — No test for git-root precedence when the target folder is itself at the repo root

**Severity:** suggestion  
**File:** modules/jobs/tests/unit_folder_compiler.py:496 (TestGitRootBoundary)  
**Description:** When the scanned folder equals the git repo root, `_find_git_root` returns that same folder, so the boundary equals `folder_path.parent` behaviorally but via the git-root code path. No test covers target == git root; all git-repo tests use a subfolder (`repo/modules/memory`). Imports that escape upward from the repo root itself (past `/` is impossible, but imports pointing at siblings of the repo root) would be refused — worth one assertion to pin the boundary == repo-root case.  
**Suggestion:** Add a test where `folder_path` is the repo root itself (contains `.git`), with an import referencing a sibling outside the repo, asserting refusal and the sibling appearing in `skipped`.  
**Status:** open

---

## Positive findings

- All five required `TestGitRootBoundary` scenarios are present and passing: git-repo-root default, no-git-dir fallback, explicit `boundary_root` wins, env-var override wins, and `.git` file (worktree/submodule).
- No mocking of the filesystem walk — tests create real directories/files under `tmp_path`; `_find_git_root` is exercised through the real `collect_folder_files_with_imports`. Appropriate use of `monkeypatch` only for `QWEN_WORKSPACE_ROOT`.
- Existing boundary tests (`test_import_outside_explicit_boundary_refused`, `test_import_inside_explicit_boundary_kept`, `test_import_escape_refused_by_boundary`, `test_markdown_exfiltration_link_refused`, `test_symlinked_import_resolves_out_of_boundary`, `test_base_folder_files_never_refused`) still pass with valid assertions after the change (46 passed total).
- Assertions are specific (file membership, `origins` tuples, `skipped` names) rather than "doesn't throw."
- The autouse `_clear_workspace_env` fixture keeps boundary tests hermetic against a stray `QWEN_WORKSPACE_ROOT` in the environment.
