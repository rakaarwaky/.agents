# Review notes — qwen-web-arwaky boundary-git-root (df2cca2a)

Scope: `modules/shared/src/common/utility_folder_compiler.py`, `modules/jobs/src/capabilities_folder_compiler.py`, `modules/jobs/tests/unit_folder_compiler.py`. Task: change the default boundary step in `_resolve_boundary_root` from `folder_path.parent.resolve()` to walking up to the git repo root via `_find_git_root`, falling back to `folder_path.parent.resolve()` when not in a git repo.

## Convention
Each entry: severity (bug/suggestion/nit), file:line, description, suggestion, status. All statuses are "open".

---

- severity: bug
- file: modules/shared/src/common/utility_folder_compiler.py:716-730
- description: `_find_git_root` can return the filesystem root `/` as the git root when the scanned path lives outside the user's home directory (e.g. `/tmp`, which is where pytest `tmp_path` lives and where CI checkouts often land). The home-directory guard `cur == home` only triggers for walks that pass through `~/`; a walk starting in `/tmp` goes straight to `/`, and because the `.git` check runs before the root check, `/.git` existing would make `_find_git_root` return `/`. If `/` (or an ancestor such as `/home`) is itself a git repo — common in CI/container environments — the resolved boundary becomes `/`, which disables import confinement and lets any file on the system be imported into the compiled markdown (exfiltration). The home-boundary protection is therefore incomplete and inconsistent.
- suggestion: never treat the filesystem root `/` as a valid git root. At `cur.parent == cur` (reached `/`), return `None` instead of checking/returning `/.git`. Equivalently, cap every walk so the returned git root is never `/` or above a sane project/user scope, and make the docstring describe the actual termination behavior. Also consider resolving symlinks along the walk (cur.parent is lexical, not real-path, so a symlinked start directory can walk the link tree oddly — though it will not loop).
- status: open

- severity: nit
- file: modules/shared/src/common/utility_folder_compiler.py:716-721
- description: The `_find_git_root` docstring says it returns None when "no ancestor up to (and excluding) the user's home directory contains .git", which is inaccurate for start paths outside `~` (those walks continue past home to the filesystem root).
- suggestion: reword the docstring to describe the true termination: walk up to the filesystem root (stopping at home for paths under home), and never return `/` as a git root.
- status: open

- severity: suggestion
- file: modules/shared/src/common/utility_folder_compiler.py:716
- description: `_find_git_root` has a single caller (`_resolve_boundary_root`). Per the summary's own open question, this is borderline over-engineered; inlining the walk into `_resolve_boundary_root` would remove an extra indirection for no gain.
- suggestion: inline the git-root walk into `_resolve_boundary_root` (or keep as a private helper only if a second caller is anticipated). Not a defect either way.
- status: open

- severity: nit
- file: modules/shared/src/common/utility_folder_compiler.py:734-750
- description: Precedence is correct and matches the task: explicit `boundary_root` > `QWEN_WORKSPACE_ROOT` env var > git root > `folder_path.parent`. No scope creep; no missing planned items. The old `folder_path.parent.resolve()` final fallback is retained (no dead code).
- suggestion: none — implementation matches the task description.
- status: open

- severity: nit
- file: modules/jobs/src/capabilities_folder_compiler.py:68-73
- description: Docstring updated to document the new default (env var → git repo root → folder parent). Accurate and matches actual behavior.
- suggestion: none.
- status: open

- severity: nit
- file: modules/shared/src/common/utility_folder_compiler.py:768-780
- description: `collect_folder_files_with_imports` docstring updated to document the git-root default boundary. Accurate and matches actual behavior.
- suggestion: none.
- status: open

- severity: nit
- file: modules/jobs/tests/unit_folder_compiler.py:497-572
- description: New `TestGitRootBoundary` class adds 5 tests covering git-dir default, fallback to parent, explicit-boundary-wins, env-var-wins, and `.git`-file (worktree) cases. Existing boundary tests (`test_import_outside_explicit_boundary_refused`, `test_import_inside_explicit_boundary_kept`, `test_import_escape_refused_by_boundary`, `test_markdown_exfiltration_link_refused`) are unchanged and their assertions remain valid under the new precedence (env var is deleted in the autouse fixture so the legacy tests keep using the folder-parent fallback).
- suggestion: none. All 46 tests pass; `lint-arwaky-cli scan .` reports Total: 0; ruff format/check and mypy pass.
- status: open

- severity: nit
- file: modules/shared/src/common/utility_folder_compiler.py:716-730
- description: Edge-case handling verified: relative paths are normalized by `start.resolve()`; `.exists()` swallows `OSError`/`PermissionError` so unreadable ancestors do not crash the walk (fail-safe, falls back to parent); symlinked `.git` entries are followed by `.exists()`; the walk terminates at the filesystem root or home with no infinite loop. `resolve()` on each candidate import in `collect_folder_files_with_imports` unfolds symlinks before `is_relative_to(boundary)`, so symlinked escapes are neutralized.
- suggestion: none beyond the root-as-boundary fix in the first item.
- status: open

## Overall
The implementation satisfies the task requirement (default boundary → git repo root with `folder_path.parent` fallback, correct precedence, no dead code, docstrings and tests updated, all CI gates passing). The one genuine defect is the security-relevant `_find_git_root` filesystem-root boundary issue in `utility_folder_compiler.py:716-730`; everything else is nit/suggestion level. Remediating the first item is recommended before merge.
