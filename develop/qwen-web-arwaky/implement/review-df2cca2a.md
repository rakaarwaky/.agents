# Merged Review — boundary-git-root (impl df2cca2a, round 1)

Source: 5 reviewers in parallel (general, tests, simplicity, lint, user).
All open issues must be addressed before the fix round completes.

## Issue 1 [General] — Severity: bug (security)
- **File**: modules/shared/src/common/utility_folder_compiler.py:716-730 (`_find_git_root`)
- **Description**: `_find_git_root` can return `/` (the filesystem root) as the boundary when the scanned path lives outside the user's home directory (e.g. `/tmp` where pytest `tmp_path` and CI checkouts live). The home-boundary guard `cur == home` only triggers for walks that pass through `~/`; a walk starting in `/tmp` climbs straight to `/`, and because the `.git` check runs before the root check, `/.git` existing makes `_find_git_root` return `/`. If `/` (or `/home`) is itself a git repo — common in CI/container environments — the boundary becomes `/`, disabling import confinement and allowing any system file to be compiled (exfiltration).
- **Suggestion**: Never treat the filesystem root `/` as a valid git root. When `cur.parent == cur` (reached `/`), return `None` immediately without checking `/.git`. Equivalently, cap the walk so the returned git root is never `/`. Update the docstring to describe the true termination.
- **Status**: open

## Issue 2 [Simplicity] — Severity: suggestion
- **File**: modules/shared/src/common/utility_folder_compiler.py:716-732
- **Description**: `_find_git_root` uses a manual `while True` loop with a multi-line docstring, but the same module already uses the `for cand in (path, *path.parents):` upward-walk idiom in `_find_tsconfig` (line 438) and `_find_crate_root` (line 537).
- **Suggestion**: Rewrite `_find_git_root` with `for cand in (cur, *cur.parents):` and a one-line docstring to match the existing helpers.
- **Status**: open

## Issue 3 [Simplicity] — Severity: nit
- **File**: modules/shared/src/common/utility_folder_compiler.py:751
- **Description**: `git_root.resolve()` in `_resolve_boundary_root` re-resolves an already-resolved `Path` returned by `_find_git_root`.
- **Suggestion**: Return `git_root` directly (it is already resolved).
- **Status**: open

## Issue 4 [Tests] — Severity: suggestion
- **File**: modules/jobs/tests/unit_folder_compiler.py:496 (TestGitRootBoundary class area)
- **Description**: Missing tests: (a) folder at the filesystem root (no parent), (b) folder inside `Path.home()` with no git repo, (c) target folder == git repo root, (d) direct unit test of `_resolve_boundary_root`/`_find_git_root` asserting the exact returned `Path` for each precedence case, (e) hermeticity of the existing boundary tests (they depend on `tmp_path` having no `.git` ancestor).
- **Suggestion**: Add the missing edge-case tests; make the existing boundary tests hermetic by explicitly asserting `_find_git_root(target) is None` or by setting `boundary_root`/env var explicitly.
- **Status**: open

## Issue 5 [User] — Severity: bug (UX)
- **File**: modules/jobs/src/capabilities_folder_compiler.py:107 (`log.warning` for refused imports)
- **Description**: When an import resolves outside the boundary, it is reported only via `log.warning`, invisible without `-v`. A user running `qwa folder <path>` sees no feedback about which linked files were excluded.
- **Suggestion**: This is out of scope for Option A (it would require CLI changes in `modules/cli/`, which are out of scope for this task). Mark as `wontfix` for this PR — note it as a follow-up issue. The current `log.warning` with `-v` is the existing behavior and is not a regression.
- **Status**: open

## Issue 6 [User] — Severity: suggestion
- **File**: modules/cli/src/surface_cli_folder_command.py:46-47, modules/root_cli_main_entry.py:255-261
- **Description**: `qwa folder --help` does not disclose the new git-root default boundary, `QWEN_WORKSPACE_ROOT`, or how to constrain imports.
- **Suggestion**: Out of scope for Option A (CLI changes are out of scope). Note as a follow-up issue.
- **Status**: open

## Issue 7 [User] — Severity: suggestion
- **File**: modules/cli/src/surface_cli_folder_command.py:59
- **Description**: No `--boundary-root` CLI flag on `qwa folder <path>`; users must set `QWEN_WORKSPACE_ROOT` env var or call the Python API to tighten the boundary.
- **Suggestion**: Out of scope for Option A. Note as a follow-up issue.
- **Status**: open

## Issue 8 [User] — Severity: suggestion (security-relevant)
- **File**: modules/shared/src/common/utility_folder_compiler.py:743-753
- **Description**: Widening the boundary to the git root can surface non-keyword secret files (e.g. `internal_keys.yaml`, `app_config.json`) that don't match `_SECRET_KEYWORDS` but are linked from module files.
- **Suggestion**: Document the widened boundary in the docstring and add a note to the `collect_folder_files_with_imports` docstring that any importable file under the git root linked from module files will be pulled into the compiled output. The user should tighten via `QWEN_WORKSPACE_ROOT` if compiling folders that link to credentials.
- **Status**: open

## Issue 9 [User] — Severity: suggestion
- **File**: modules/shared/src/common/utility_folder_compiler.py:716-731
- **Description**: In a monorepo with a single `.git` at the top, `qwa folder projects/A/src` sets the boundary to the monorepo root. Links to `projects/B/lib.py` from `projects/A/src` will now be resolved and included — users compiling one sub-project may be surprised.
- **Suggestion**: Document monorepo behavior explicitly in the docstring, pointing users to `QWEN_WORKSPACE_ROOT` to scope compilation to a single sub-project.
- **Status**: open

## Issue 10 [User] — Severity: nit
- **File**: modules/shared/src/common/utility_folder_compiler.py:768-775
- **Description**: The docstrings say cross-folder references are included "when linked" but don't warn that *any* importable file under the git root is in scope, not just docs.
- **Suggestion**: Extend the docstring note to clarify the full scope.
- **Status**: open

## Issue 11 [General] — Severity: nit
- **File**: modules/shared/src/common/utility_folder_compiler.py:716-721
- **Description**: The `_find_git_root` docstring says it returns None when "no ancestor up to (and excluding) the user's home directory contains .git", which is inaccurate for start paths outside `~`.
- **Suggestion**: Reword the docstring (will be handled with the Issue 2 rewrite).
- **Status**: open

---

## Summary
- **General**: 1 bug (security), 5 nits (2 actionable: docstring, filesystem-root termination)
- **Tests**: 5 suggestions (all edge-case coverage gaps)
- **Simplicity**: 1 suggestion (while→for loop), 1 nit (redundant resolve)
- **Lint**: 0 issues
- **User**: 1 bug (UX feedback gap — out of scope, wontfix), 4 suggestions (2 in-scope docstring updates, 2 out-of-scope CLI follow-ups), 1 nit (docstring)
- **Merged open issues**: 11
- **In-scope for this PR**: Issues 1, 2, 3, 4, 8, 9, 10, 11 (8 issues)
- **Out-of-scope (wontfix, note as follow-up)**: Issues 5, 6, 7 (3 issues — CLI changes are out of scope for Option A)
