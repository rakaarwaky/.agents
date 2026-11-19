# Implementation Summary — Folder Compile CLI Verb

## Files Changed

### 1. `modules/cli/src/surface_cli_folder_command.py` (NEW)
AES6 surface file exposing the folder-to-markdown compiler as a CLI verb.

- Defines a local `_FolderCompiler` protocol (structural type for the `compile_folder` call shape) and a `_FolderContainer` protocol (structural type for the container's `folder_compiler` attribute). The container attribute is typed `Any` so the surface accepts the real `SharedContainer` without importing the Capabilities class or the contract protocol — both forbidden for the surface layer by AES201.
- `_cmd_compile(args, compiler)`: validates `args.folder_path` is an existing directory, calls `compiler.compile_folder(folder_path)`, prints `Compiled <folder> -> <output>` on success, prints `[ERROR] <msg>` to stderr on `FolderValidationError`/`FolderEmptyError`/`FolderCompileError`, returns 0/1.
- `handle_folder_command(args, container)`: dispatches `args.folder_command == "compile"`; unknown/missing verbs print a usage hint to stderr and return 1.
- `__all__ = ["handle_folder_command"]` at the bottom.

### 2. `modules/root_cli_main_entry.py` (EDIT)
- Added import for `handle_folder_command` from the new surface module.
- Added `folder` subcommand group under the top-level parser (next to `job`, `swarm`, `observability`): `folder compile <folder_path>` with a positional `folder_path` argument (no `-o`, no `--json`, no `--max-depth`, etc.).
- Added `folder` to the `no_cfg_actions` tuple in `main()` so it skips `AppConfig` building and session rotation.
- Added `if action == "folder": return handle_folder_command(args, _default_container())` in `_dispatch()`.
- Added `"folder": "direct"` to the mode mapping in `_build_config()` for direct-call safety.
- Updated the top docstring to list `qwen-web-arwaky folder compile <path>`.

### 3. `modules/cli/tests/unit_surface_cli_folder_command.py` (NEW)
Nine unit tests using `capsys`, `tmp_path`, `monkeypatch`, and a stub container:
- `test_compile_tmp_folder`: real `FolderCompiler(input_dir=tmp_path/"out")` compiles a folder with `a.md`+`b.md`; asserts rc 0, output file exists, stdout contains path.
- `test_compile_default_output_under_dot_dir`: `monkeypatch.chdir(tmp_path)`, default compiler; asserts output under `.qwen-web-arwaky/input/`.
- `test_reject_file_not_folder`: file path → rc 1, stderr contains `Not a directory`.
- `test_reject_missing_path`: missing path → rc 1, stderr contains `Folder not found`.
- `test_unknown_verb_prints_usage_hint`: `folder_command="list"` → rc 1, usage hint.
- `test_missing_verb_prints_usage_hint`: `folder_command=None` → rc 1, usage hint.
- `test_compile_errors_print_error_line` (parametrized): `FolderValidationError`, `FolderEmptyError`, `FolderCompileError` each → rc 1, `[ERROR]` + message on stderr.

### 4. `modules/cli/tests/integration_surface_cli_main.py` (EDIT)
Replaced the stub docstring with two integration tests driving `modules.root_cli_main_entry.main(argv=...)`:
- `test_folder_compile_exits_zero_and_writes_output`: `["folder", "compile", str(tmp_folder)]` → rc 0, file under `.qwen-web-arwaky/input/`, path in stdout.
- `test_folder_compile_on_file_exits_nonzero`: `["folder", "compile", str(tmp_file)]` → rc 1, error on stderr.

### 5. `README.md` (EDIT)
Added one row to the "Frequently Used Commands" table after the `job submit` row:
```
| `qwen-web-arwaky folder compile <path>` | Compile a folder to a single Markdown file. | The `.qwen-web-arwaky/input/` path prints on success. |
```

## Plan Decisions

### AES import-matrix tradeoff (the key decision)
The task suggested importing `IFolderCompileProtocol` from `modules.shared.src.prompt.contract_prompt_protocol` for the type hint. **This is forbidden by AES201** — the surface layer's allowed imports are `[taxonomy, contract(aggregate), utility, surface]`, and `contract(protocol)` is not in that set. `lint-arwaky-cli scan` flagged it as a CRITICAL violation.

Resolution: declared a local `_FolderCompiler` protocol in the surface file and typed the container's `folder_compiler` attribute as `Any`. This keeps the surface free of forbidden imports while still accepting the real `SharedContainer` (whose `folder_compiler` is a concrete `FolderCompiler`). mypy passes cleanly on both `surface_cli_folder_command.py` and `root_cli_main_entry.py` with this approach — no `type: ignore` needed (and `type: ignore` would have triggered AES304 BYPASS_COMMENT).

The alternative of importing `FolderCompiler` directly from `modules.jobs.src.capabilities_folder_compiler` would also violate AES201 (surface → capabilities is forbidden).

### Positional argument naming
The task's example used `p_compile.add_argument("path", ...)` with `dest="folder_path"`. argparse rejects `dest=` on positionals (raises `TypeError: dest supplied twice`). Fixed by naming the positional itself `folder_path`, which sets `args.folder_path` directly — matching what the handler reads.

### No new agent orchestrator
Per the task constraint, no AES5 agent orchestrator was created. The CLI surface calls the AES4 capability (`container.folder_compiler.compile_folder(...)`) directly via the `SharedContainer`, which is the Root wiring.

## CI Gate Results

```
$ uv run ruff format --check modules/cli/ modules/root_cli_main_entry.py
40 files already formatted

$ uv run ruff check modules/cli/ modules/root_cli_main_entry.py
All checks passed!

$ uv run mypy modules/root_cli_main_entry.py modules/cli/src/surface_cli_folder_command.py
Success: no issues found in 2 source files

$ uv run python -m pytest modules/cli/tests/unit_surface_cli_folder_command.py -v
9 passed

$ uv run python -m pytest modules/cli/tests/integration_surface_cli_main.py -v
2 passed

$ lint-arwaky-cli scan .
Total: 0 violations
```

Note: `mypy modules/` (the full CI gate) reports the same pre-existing `pytest` stub errors across 105 test files that exist on `main` before this change; the two non-test source files touched here (`surface_cli_folder_command.py`, `root_cli_main_entry.py`) pass mypy cleanly.

## Manual Smoke Test

```
$ mkdir -p /tmp/folder_smoke && echo "# hi" > /tmp/folder_smoke/a.md
$ uv run python -m modules.root_cli_main_entry folder compile /tmp/folder_smoke
Compiled /tmp/folder_smoke -> /home/raka/orca/workspaces/tools/folder-compile-cli/.qwen-web-arwaky/input/folder_smoke_20261119-165309.md
$ ls .qwen-web-arwaky/input/
folder_smoke_20261119-165309.md
```

Output lands under `.qwen-web-arwaky/input/` with the `{folder_name}_{timestamp}.md` shape, matching the `FolderCompiler` default.