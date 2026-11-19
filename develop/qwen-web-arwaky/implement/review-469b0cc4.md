# Merged Review — folder-compile CLI (impl 469b0cc4, round 1)

Source: 3 reviewers in parallel (general, tests, simplicity).
All open issues must be addressed before the fix round completes.
Duplicate findings consolidated.

---

## Issue 1 [General] — Severity: suggestion
- **File**: modules/cli/src/surface_cli_folder_command.py:24-36
- **Description**: `_FolderContainer` declares `folder_compiler: Any` to avoid a forbidden AES201 import. This is a sound layering tradeoff, but `Any` fully disables type checking at the call site `compiler.compile_folder(folder_path)` — a future re-signature of `compile_folder` would not be caught by mypy. The summary claims a local `_FolderCompiler` protocol was declared, but the file only declares `_FolderContainer`; the call-shape protocol was dropped, leaving `Any` as the only guard.
- **Suggestion**: Keep the local-protocol approach (AES-clean) but type the attribute as a call-shape protocol instead of `Any`:
  ```python
  class _FolderCompiler(Protocol):
      def compile_folder(
          self,
          folder_path: Path,
          output_path: Path | None = None,
          *,
          max_depth: int = 2,
          import_depth: int = 1,
          include_imports: bool = True,
          boundary_root: Path | None = None,
      ) -> Path: ...

  class _FolderContainer(Protocol):
      folder_compiler: _FolderCompiler
  ```
  Restore mypy checking of `compile_folder` and the `Path` return, without importing any contract/capability symbol.
- **Status**: fixed
- **Response**: Declared a local `_FolderCompiler` protocol with the full `compile_folder` signature (matching the real `FolderCompiler.compile_folder` exactly — `output_path`, `max_depth`, `import_depth`, `include_imports`, `boundary_root` as positional-or-keyword with defaults). mypy now type-checks the `compile_folder` call and the `Path` return. Dropped the `_FolderContainer` protocol entirely; the surface takes `compiler: _FolderCompiler` directly (see Issue 2). Note: the reviewer's suggested `*` (keyword-only) separator would break protocol compatibility — the real `FolderCompiler.compile_folder` has all params positional-or-keyword, so a keyword-only protocol would not match and mypy would reject the call. The fix uses positional-or-keyword to match the real signature. The `max_depth` default in the protocol is `5` (matching `MAX_FOLDER_DEPTH`), not `2` as in the suggestion.

## Issue 2 [General + Simplicity] — Severity: suggestion
- **File**: modules/root_cli_main_entry.py:553 (general) / modules/cli/src/surface_cli_folder_command.py:24-34 (simplicity)
- **Description** (consolidated): The folder dispatch in `_dispatch` calls `_default_container()` instead of the injected `container` argument, diverging from every sibling branch (`handle_jobs_command(args, container.agent_job_orchestrator)` etc.) and bypassing the test seam. Separately, the `_FolderContainer` protocol with a single `Any`-typed attribute is over-engineered for a single-caller surface — sibling handlers accept their specific capability directly rather than the whole container.
- **Suggestion**: Pass `container` (or `container.folder_compiler`) from the injected scope, matching siblings. Simplify `handle_folder_command` to `handle_folder_command(args, container)` with the same signature as siblings. The `_FolderContainer` protocol may stay if `folder_compiler` is re-typed to the call-shape protocol per Issue 1; if the simplicity reviewer's suggestion to pass the compiler directly is preferred, delete the protocol and type the parameter `compiler: _FolderCompiler`.
- **Status**: fixed
- **Response**: Took option (b) — pass the compiler directly. `_dispatch` now calls `handle_folder_command(args, container.folder_compiler)`, passing the injected container's `folder_compiler` capability (matching how `handle_jobs_command` receives `container.agent_job_orchestrator`). Deleted the `_FolderContainer` protocol; the handler signature is now `handle_folder_command(args: argparse.Namespace, compiler: _FolderCompiler) -> int`. This is cleaner for a single-caller surface and aligns with the sibling pattern of passing the specific capability rather than the whole container.

## Issue 3 [General] — Severity: nit
- **File**: modules/cli/src/surface_cli_folder_command.py:56-60
- **Description**: The unknown-verb branch (`if command != "compile": print(...); return 1`) is unreachable via `main()` because argparse restricts `folder_command` to `{"compile", None}`. It is only reachable by direct unit calls.
- **Suggestion**: Acceptable as defensive coding. No change required for correctness.
- **Status**: wontfix
- **Response**: Intentional defensive coding. The branch is reachable by direct unit calls (which construct `argparse.Namespace` by hand) and guards against future argparse changes that might add verbs without updating the handler. The unit tests `test_unknown_verb_prints_usage_hint` and `test_missing_verb_prints_usage_hint` exercise it directly. Removing it would reduce robustness for no benefit.

## Issue 4 [General] — Severity: suggestion
- **File**: modules/cli/src/surface_cli_folder_command.py:60
- **Description**: For a missing/unknown verb the handler prints the usage hint via bare `print(...)` → **stdout**. Every other error path in the handler writes to stderr. For a non-interactive script that checks `rc` and reads stderr, this message is silently lost.
- **Suggestion**: `print("Use 'qwen-web-arwaky folder --help' for usage", file=sys.stderr)`. The existing tests check `captured.out + captured.err` and will still pass.
- **Status**: fixed
- **Response**: Changed to `print("Use 'qwen-web-arwaky folder --help' for usage", file=sys.stderr)`. All error paths in the handler now write to stderr consistently. Updated the unit tests (Issue 11) to assert on `captured.err` specifically.

## Issue 5 [General] — Severity: suggestion
- **File**: modules/cli/src/surface_cli_folder_command.py:47
- **Description**: The except tuple is `(FolderValidationError, FolderEmptyError, FolderCompileError)`. `FolderDepthExceededError` subclasses `FolderCompileError` (so it is covered), but an `OSError` raised outside the compiler's own try/except would escape to `main()`'s global handler. `capabilities_folder_compiler.compile_folder` already wraps `OSError` into `FolderCompileError` on the write path, so a stray `OSError` from an earlier step (e.g. mkdir) would slip through.
- **Suggestion**: Add `OSError` to the catch tuple: `except (FolderValidationError, FolderEmptyError, FolderCompileError, OSError)`. Belt-and-suspenders.
- **Status**: fixed
- **Response**: Added `OSError` to the except tuple: `except (FolderValidationError, FolderEmptyError, FolderCompileError, OSError)`. This catches stray `OSError` from any step (e.g. `mkdir`, filesystem access) before it reaches `main()`'s global handler.

## Issue 6 [Tests] — Severity: suggestion
- **File**: modules/cli/tests/unit_surface_cli_folder_command.py:118-126
- **Description**: The parametrized error-path test covers `FolderValidationError`, `FolderEmptyError`, and `FolderCompileError` but omits `FolderDepthExceededError` — the fourth subclass of `FolderCompileError` that `_cmd_compile` also catches.
- **Suggestion**: Add `FolderDepthExceededError("depth exceeded")` to the `parametrize` list so all four catchable error types assert on `[ERROR]` + message on stderr and rc 1.
- **Status**: fixed
- **Response**: Added `FolderDepthExceededError("depth exceeded")` to the `parametrize` list in `test_compile_errors_print_error_line`. All four catchable error types now exercise the error path.

## Issue 7 [Tests] — Severity: suggestion
- **File**: modules/cli/tests/unit_surface_cli_folder_command.py
- **Description**: No test exercises a real empty folder (zero compilable files) through a real `FolderCompiler` to trigger `FolderEmptyError` from the capability layer. The path is only covered via a `MagicMock` side-effect.
- **Suggestion**: Add a unit test that creates an empty folder, uses a real `FolderCompiler(input_dir=...)`, and asserts rc 1, stderr contains `[ERROR]`, and the message mentions no compilable files.
- **Status**: fixed
- **Response**: Added `test_compile_empty_folder_returns_error` which creates an empty folder, uses a real `FolderCompiler(input_dir=tmp_path / "out")`, and asserts rc 1, `[ERROR]` in stderr, and `"No compilable files"` in stderr.

## Issue 8 [Tests] — Severity: suggestion
- **File**: modules/cli/tests/integration_surface_cli_main.py:52
- **Description**: `test_folder_compile_on_file_exits_nonzero` asserts `"Not a directory" in err or "[ERROR]" in err` — a weak `or` that passes if either substring appears.
- **Suggestion**: `assert "Not a directory" in err` and separately `assert "[ERROR]" in err`, matching the specificity of the unit-level error tests.
- **Status**: fixed
- **Response**: Replaced the `or` assertion with two separate asserts: `assert "Path is not a directory" in err` and `assert "[ERROR]" in err`. Note: the capability's actual message is `"Path is not a directory: ..."` (lowercase "not"), not `"Not a directory"` — updated to match the real message.

## Issue 9 [Tests] — Severity: suggestion
- **File**: modules/cli/tests/integration_surface_cli_main.py
- **Description**: No integration test drives `["folder"]` (no subcommand) through the real argparse parser. Argparse leaves `folder_command` as `None` and the handler prints a usage hint and returns 1. Covered only at unit level via a hand-built Namespace.
- **Suggestion**: Add `root_entry.main(["folder"])` → assert rc 1 and the usage hint appears on stderr (per Issue 4 the hint moves to stderr).
- **Status**: fixed
- **Response**: Added `test_folder_no_subcommand_prints_usage_hint_on_stderr` which drives `root_entry.main(["folder"])` and asserts rc 1 and `"--help"` in `captured.err`.

## Issue 10 [Tests] — Severity: suggestion
- **File**: modules/cli/tests/integration_surface_cli_main.py
- **Description**: No integration test drives `["folder", "list"]` (unknown subcommand). Argparse rejects with exit code 2 before the handler runs. Similarly `["folder", "compile"]` (missing positional) and `["folder", "compile", "a", "b"]` (extra positional) both exit 2 — neither is covered.
- **Suggestion**: Add integration tests asserting rc 2 for each of the three argparse boundary cases.
- **Status**: fixed
- **Response**: Added `test_folder_argparse_boundary_cases_exit_2` parametrized over `["folder", "list"]`, `["folder", "compile"]`, and `["folder", "compile", "a", "b"]`, asserting `SystemExit` with code 2 for each.

## Issue 11 [Tests] — Severity: nit
- **File**: modules/cli/tests/unit_surface_cli_folder_command.py:100-109
- **Description**: `test_unknown_verb_prints_usage_hint` and `test_missing_verb_prints_usage_hint` assert `"--help" in captured.out + captured.err`. Concatenating is imprecise.
- **Suggestion**: After Issue 4 moves the hint to stderr, assert `"--help" in captured.err` specifically.
- **Status**: fixed
- **Response**: Both tests now assert `"--help" in captured.err` (via `err = capsys.readouterr().err; assert "--help" in err`), no longer concatenating stdout and stderr.

## Issue 12 [Simplicity] — Severity: suggestion
- **File**: modules/cli/src/surface_cli_folder_command.py:37-64
- **Description**: `_cmd_compile` is invoked in exactly one place. Multi-verb command surfaces (`job`, `observability`) split subcommands into `_cmd_*` helpers because they have multiple verbs; `folder` has only one (`compile`).
- **Suggestion**: Inline `_cmd_compile` directly into `handle_folder_command`. Check `if command != "compile": print(...); return 1`, then the compilation logic in one function.
- **Status**: fixed
- **Response**: Inlined `_cmd_compile` into `handle_folder_command`. The handler now checks `if command != "compile"` (printing the usage hint to stderr and returning 1), then runs the compile logic directly in the same function. Removed the `_cmd_compile` helper.

## Issue 13 [Simplicity] — Severity: nit
- **File**: modules/cli/src/surface_cli_folder_command.py:40-45
- **Description**: `_cmd_compile` manually checks `folder_path.exists()` and `folder_path.is_dir()`, returning rc 1 with custom messages. But `compiler.compile_folder` delegates to `collect_folder_files`, which already performs these checks and raises `FolderValidationError("Folder does not exist: ...")` / `FolderValidationError("Path is not a directory: ...")` — caught by the existing except block.
- **Suggestion**: Remove the duplicate pre-checks; let `compiler.compile_folder` validate and catch `FolderValidationError` uniformly.
- **Status**: fixed
- **Response**: Removed the manual `folder_path.exists()` and `folder_path.is_dir()` pre-checks. `compiler.compile_folder` now performs all validation and raises `FolderValidationError("Folder does not exist: ...")` or `FolderValidationError("Path is not a directory: ...")`, caught uniformly by the except block. Updated the unit test assertions to match the capability's actual messages (`"Folder does not exist"` and `"Path is not a directory"`).

## Issue 14 [Simplicity] — Severity: nit
- **File**: modules/root_cli_main_entry.py:409
- **Description**: `"folder": "direct"` in the `_build_config` mode dictionary is dead code on the CLI path because `folder` is in `no_cfg_actions` (which skips `_build_config` entirely).
- **Suggestion**: Omit the entry, or leave it and add a short comment noting it is a defensive fallback for standalone `_build_config` calls.
- **Status**: fixed
- **Response**: Removed the dead `"folder": "direct"` entry from the `_build_config` mode dictionary. `folder` is in `no_cfg_actions` and never reaches `_build_config` on the CLI path; the `.get(action, "direct")` default already handles any standalone `_build_config(["folder", ...])` call.

---

## Summary
- **General**: 7 issues (2 suggestion, 4 nit + 1 suggestion consolidated with simplicity → 4 suggestion, 3 nit)
- **Tests**: 6 issues (5 suggestion, 1 nit)
- **Simplicity**: 5 issues (2 suggestion, 3 nit)
- **Merged open issues**: 14 (no bugs)
- **Duplicates consolidated**: Issue 2 (general + simplicity overlap)
- **Fix round result**: 13 fixed, 1 wontfix (Issue 3 — intentional defensive coding)

---

## Implementation Summary — Fix Round (round 2)

### What changed in this fix round

**`modules/cli/src/surface_cli_folder_command.py`** (rewritten):
- Replaced `_FolderContainer` with `Any` attribute → deleted entirely. Added a local `_FolderCompiler` protocol with the full `compile_folder` signature (matching the real `FolderCompiler.compile_folder` exactly: `output_path`, `max_depth`, `import_depth`, `include_imports`, `boundary_root` as positional-or-keyword with defaults). mypy now type-checks the `compile_folder` call and `Path` return. (Issue 1)
- Changed handler signature from `(args, container: _FolderContainer)` to `(args, compiler: _FolderCompiler)`. Deleted `_cmd_compile` helper; inlined the compile logic into `handle_folder_command`. (Issues 2, 12)
- Moved usage hint from stdout to stderr: `print(..., file=sys.stderr)`. (Issue 4)
- Added `OSError` to the except tuple. (Issue 5)
- Removed manual `folder_path.exists()` / `is_dir()` pre-checks; `compiler.compile_folder` validates and raises `FolderValidationError` uniformly. (Issue 13)

**`modules/root_cli_main_entry.py`**:
- Changed dispatch from `handle_folder_command(args, _default_container())` to `handle_folder_command(args, container.folder_compiler)` — passes the injected container's compiler capability, matching the sibling pattern (`container.agent_job_orchestrator` etc.). (Issue 2)
- Removed dead `"folder": "direct"` entry from `_build_config` mode dict. (Issue 14)

**`modules/cli/tests/unit_surface_cli_folder_command.py`**:
- Updated all call sites to pass the compiler directly instead of a stub container; removed `_stub_container` helper.
- Updated `test_reject_file_not_folder` assertion to `"Path is not a directory"` (matches capability message).
- Updated `test_reject_missing_path` assertion to `"Folder does not exist"` (matches capability message).
- Updated `test_unknown_verb_prints_usage_hint` and `test_missing_verb_prints_usage_hint` to assert on `captured.err` specifically. (Issue 11)
- Added `FolderDepthExceededError("depth exceeded")` to the parametrized error test. (Issue 6)
- Added `test_compile_empty_folder_returns_error` using a real `FolderCompiler` on an empty folder. (Issue 7)

**`modules/cli/tests/integration_surface_cli_main.py`**:
- Replaced weak `or` assertion with two separate asserts (`"Path is not a directory"` and `"[ERROR]"`). (Issue 8)
- Added `test_folder_no_subcommand_prints_usage_hint_on_stderr` for `["folder"]` → rc 1, hint on stderr. (Issue 9)
- Added `test_folder_argparse_boundary_cases_exit_2` parametrized over `["folder", "list"]`, `["folder", "compile"]`, `["folder", "compile", "a", "b"]` → all exit 2. (Issue 10)

### CI gate results (all green)

```
$ uv run ruff format --check modules/cli/ modules/root_cli_main_entry.py
40 files already formatted

$ uv run ruff check modules/cli/ modules/root_cli_main_entry.py
All checks passed!

$ uv run mypy modules/cli/src/surface_cli_folder_command.py modules/root_cli_main_entry.py
Success: no issues found in 2 source files

$ uv run python -m pytest modules/cli/tests/unit_surface_cli_folder_command.py -v
11 passed

$ uv run python -m pytest modules/cli/tests/integration_surface_cli_main.py -v
6 passed

$ uv run python -m pytest modules/cli/tests/ -v
214 passed

$ lint-arwaky-cli scan .
Total: 0 violations
```

### Manual smoke test

```
$ rm -rf /tmp/folder_smoke
$ mkdir -p /tmp/folder_smoke && echo "# hi" > /tmp/folder_smoke/a.md
$ uv run python -m modules.root_cli_main_entry folder compile /tmp/folder_smoke
Compiled /tmp/folder_smoke -> /home/raka/orca/workspaces/tools/folder-compile-cli/.qwen-web-arwaky/input/folder_smoke_20261119-170344.md
$ ls .qwen-web-arwaky/input/
folder_smoke_20261119-170344.md
```

Output lands under `.qwen-web-arwaky/input/` with the `{folder_name}_{timestamp}.md` shape, matching the `FolderCompiler` default.