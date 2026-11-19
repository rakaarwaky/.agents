# Simplicity Review — df2cca2a (Option A: Default boundary to git repo root)

**Scope:** Over-engineering and unnecessary complexity only.
**Baseline:** 3 modified files (`modules/shared/src/common/utility_folder_compiler.py`, `modules/jobs/src/capabilities_folder_compiler.py`, `modules/jobs/tests/unit_folder_compiler.py`).
**Review target:** New `_find_git_root` helper, `_resolve_boundary_root` precedence updates, and `TestGitRootBoundary` test cases.

---

## Findings

### 1. Suggestion (`shrink` / `native`) — `modules/shared/src/common/utility_folder_compiler.py:716`

- **Severity:** `suggestion`
- **File:Line:** `/home/raka/orca/workspaces/tools/boundary-git-root/modules/shared/src/common/utility_folder_compiler.py:716-732`
- **Description:** `_find_git_root` uses a manual `while True` loop with `cur = cur.parent` advancement and a 5-line docstring explaining the `.git` directory vs. file cases. The same file already implements this exact upward directory walk pattern twice — `_find_tsconfig` (lines 438–443) and `_find_crate_root` (lines 537–541) — using `for cand in (path, *path.parents):`. Using `while True` for a single-level-parent walk is more verbose than necessary and diverges from the module's existing helpers.
- **Suggestion:** Rewrite `_find_git_root` using `for cand in (cur, *cur.parents):` to match `_find_tsconfig` and `_find_crate_root`, and trim the docstring to a single summary line:
  ```python
  def _find_git_root(start: Path) -> Path | None:
      """Return the nearest ancestor of ``start`` (up to ``Path.home()``) containing ``.git``."""
      home = Path.home().resolve()
      cur = start.resolve()
      for cand in (cur, *cur.parents):
          if (cand / ".git").exists():
              return cand
          if cand == home:
              break
      return None
  ```
- **Status:** open

---

### 2. Nit (`shrink`) — `modules/shared/src/common/utility_folder_compiler.py:751`

- **Severity:** `nit`
- **File:Line:** `/home/raka/orca/workspaces/tools/boundary-git-root/modules/shared/src/common/utility_folder_compiler.py:751`
- **Description:** `_find_git_root` initializes `cur = start.resolve()` and walks `.parent` pointers, so its return value is always a fully resolved `Path`. Calling `git_root.resolve()` again in `_resolve_boundary_root` (line 751) performs a redundant second filesystem resolution pass (or can be collapsed directly with the fallback return).
- **Suggestion:** Drop the redundant `.resolve()` call (or collapse lines 750–752 to `return _find_git_root(folder_path) or folder_path.parent.resolve()`):
  ```python
  git_root = _find_git_root(folder_path)
  if git_root is not None:
      return git_root
  return folder_path.parent.resolve()
  ```
- **Status:** open

---

## Summary

| # | Severity | File:Line | Description | Suggestion | Status |
|---|----------|-----------|-------------|------------|--------|
| 1 | `suggestion` | `modules/shared/src/common/utility_folder_compiler.py:716` | `_find_git_root` uses a `while True` loop and multi-line docstring instead of the `for cand in (start, *start.parents)` pattern already used by `_find_tsconfig` (line 438) and `_find_crate_root` (line 537) | Rewrite with `for cand in (cur, *cur.parents):` and a one-line docstring | open |
| 2 | `nit` | `modules/shared/src/common/utility_folder_compiler.py:751` | `git_root.resolve()` in `_resolve_boundary_root` re-resolves an already-resolved `Path` returned by `_find_git_root` | Return `git_root` directly or use `return _find_git_root(folder_path) or folder_path.parent.resolve()` | open |

### Items Checked and Found Appropriate

- **`_find_git_root` kept as a standalone helper rather than inlined into `_resolve_boundary_root`** — Justified; inlining a loop into `_resolve_boundary_root` would mix filesystem traversal with precedence branching.
- **4-branch precedence chain in `_resolve_boundary_root`** — Necessary because each source (`boundary_root` parameter, `QWEN_WORKSPACE_ROOT` env var, git root, `folder_path.parent`) has distinct resolution semantics (`expanduser()` vs. filesystem walk).
- **No duplicated logic with `_find_crate_root` / `_find_tsconfig` return types** — `_find_git_root` needs `Path | None` (to fall back to `folder_path.parent.resolve()` when not in a git repo), whereas `_find_crate_root` returns `path` and `_find_tsconfig` searches for a filename rather than `.git` entries.
- **Test additions in `TestGitRootBoundary`** (`modules/jobs/tests/unit_folder_compiler.py:495`) — Five focused unit tests validating the default git-root boundary, no-git fallback, explicit parameter precedence, env var precedence, and `.git` file (worktree) handling without bloat.