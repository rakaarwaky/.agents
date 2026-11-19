# User-Advocate Review — `qwen-web-arwaky folder` git-root boundary default

## Summary

The implementation changes the default import boundary for `qwen-web-arwaky folder <path>` from `folder_path.parent` to the git repo root (falling back to `folder_path.parent` when not inside a git repo). This makes cross-folder references like `PRD.md`, `ROADMAP.md`, and `ARCHITECTURE.md` at the repo root resolve and compile by default. The change achieves its stated goal, but several user-experience gaps remain — most notably: the user gets no feedback when files are skipped, the CLI help says nothing about the boundary, there is no CLI flag to tighten it, and widening the boundary can surface non-keyword secrets inside the git root.

---

## Issues

### 1. Bug — No user-facing feedback when linked files are skipped outside the boundary

- **Severity:** bug
- **File:Line:** `modules/jobs/src/capabilities_folder_compiler.py:107` (the `log.warning` in `compile_folder`)
- **Description:** When an import resolves outside the git-root boundary, it is appended to the `refused` list and reported only via `log.warning("Refused %d import(s) outside the workspace boundary ...")`. A user running `qwa folder <path>` without `-v` sees no such warning — only the success line `Compiled <path> -> <output.md>`. If `index.md` links to `../../PRD.md` and PRD is outside the boundary for some reason, the user has no idea it was omitted, nor why.
- **Suggestion:** Emit a concise stdout/stderr summary of refused imports in `handle_folder_command` (or at minimum document that refusal info appears only with `-v`), so end users know which linked files were excluded and that they can tighten/loosen the boundary.
- **Status:** open

### 2. Suggestion — CLI `--help` does not disclose the new default boundary

- **Severity:** suggestion
- **File:Line:** `modules/cli/src/surface_cli_folder_command.py:46-47` (`handle_folder_command`) and `modules/root_cli_main_entry.py:255-261` (folder subparser definition)
- **Description:** `qwen-web-arwaky folder --help` prints only:
  ```
  folder_path    Path to the folder to compile (must be a directory)
  ```
  It does not mention that imports/links are followed, that the default boundary is the git repo root, that `QWEN_WORKSPACE_ROOT` can constrain it, or that the user can tighten it. A user reading `--help` cannot know what files will be included or how to change it.
- **Suggestion:** Add boundary behavior and `QWEN_WORKSPACE_ROOT` documentation to the `folder` subcommand help string and/or `--help` output so users can discover the behavior without reading Python docstrings.
- **Status:** open

### 3. Suggestion — No CLI flag to override `boundary_root` from `qwa folder <path>`

- **Severity:** suggestion
- **File:Line:** `modules/cli/src/surface_cli_folder_command.py:59` (`compiler.compile_folder(Path(folder_path_raw))`)
- **Description:** `handle_folder_command` calls `compile_folder` with only `folder_path`. The `boundary_root`, `max_depth`, `import_depth`, and `include_imports` parameters all use defaults. A user inside a git repo who wants to tighten the boundary (e.g. to avoid compiling linked secrets) must set `QWEN_WORKSPACE_ROOT` or call the Python API — neither is discoverable via CLI.
- **Suggestion:** Add a `--boundary-root` option to the `folder` subcommand so users can explicitly restrict the import confinement boundary from the CLI without touching environment variables.
- **Status:** open

### 4. Security concern — Widening the boundary can surface non-keyword secret files inside the git root

- **Severity:** suggestion (security-relevant)
- **File:Line:** `modules/shared/src/common/utility_folder_compiler.py:743-753` (`_resolve_boundary_root` precedence: git root before `folder_path.parent`)
- **Description:** The previous default (`folder_path.parent`) confined imports to the scanned folder's parent — relatively conservative. The new default walks up to the git repo root. Any importable file under that root linked from a module file gets compiled, even if it contains credentials but does not match `_SECRET_KEYWORDS` (e.g. `internal_keys.yaml`, `app_config.json`, `deploy.config.toml`). Verified: `internal_keys.yaml` containing `jwt_secret: supersecret` linked via `[internal_keys](../internal_keys.yaml)` is included in compiled output.
- **Suggestion:** Document the widened boundary prominently in CLI help/README, and recommend users who compile folders containing links to credentials tighten the boundary via `QWEN_WORKSPACE_ROOT` or `--boundary-root`. Consider expanding secret-keyword detection for common config filenames.
- **Status:** open

### 5. Suggestion — Monorepo boundary may span unrelated sub-projects, which can surprise users

- **Severity:** suggestion
- **File:Line:** `modules/shared/src/common/utility_folder_compiler.py:716-731` (`_find_git_root` walks to nearest `.git`)
- **Description:** In a monorepo with a single `.git` at the top, `qwa folder projects/A/src` sets the boundary to the monorepo root. Links to `projects/B/lib.py` or `shared/config.yaml` from `projects/A/src` will now be resolved and included. Users compiling one sub-project may be surprised to see unrelated sub-project files in their output.
- **Suggestion:** Document monorepo behavior explicitly, and point users to `--boundary-root` / `QWEN_WORKSPACE_ROOT` to scope compilation to a single sub-project directory.
- **Status:** open

### 6. Nit — Docstring does not warn that *any* file under the git root is in scope

- **Severity:** nit
- **File:Line:** `modules/shared/src/common/utility_folder_compiler.py:768-775` (`collect_folder_files_with_imports` docstring) and `modules/jobs/src/capabilities_folder_compiler.py:68-75` (`boundary_root` arg docstring)
- **Description:** The docstrings say cross-folder references like `PRD.md` or `ROADMAP.md` at the repo root are included "when linked." This is accurate but incomplete: any importable file under the git root linked from a module file is included, not just documentation.
- **Suggestion:** Extend the docstring note to clarify that any importable file under the git root linked from module files will be pulled into the compiled output.
- **Status:** open

---

## Bottom line

The feature behaves as intended for the stated task (repo-root docs like `PRD.md` are now included when linked from module folders), and it is transparent in the happy path. The main user-experience gaps are: **no feedback when imports are refused**, **no CLI help text explaining the boundary**, **no CLI flag to tighten it**, and **a latent security risk** where secret-bearing files inside the git root that don't match keyword filters can be compiled into output. Each issue above is marked `open` and should be addressed before release.