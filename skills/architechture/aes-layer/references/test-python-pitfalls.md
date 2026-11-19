# Python Test Pitfalls

## sys.path bootstrap uniformity

Every test file that imports `module.src.X` must bootstrap `sys.path` via `bootstrap_ns_roots()` from `shared.src.common.utility_sdc_common` — never hand-rolled `sys.path.insert(0, ...)` loops in individual test files. Hand-rolled bootstraps that insert `src/` directories at position 0 shadow the `module` package root, breaking `from module.src.X` resolution for every subsequent test file in the same pytest session. `bootstrap_ns_roots()` adds both `modules/<name>` (package root) and `modules/<name>/src` (bare import root) idempotently, and is the only bootstrap that keeps cross-module imports stable when the full suite runs.

## Multiprocessing forkserver sys.path

When a test uses `multiprocessing.Process` on Linux with the `forkserver` start method (default in some environments), the child process does NOT inherit the parent's `sys.path` mutations. The worker function must call `bootstrap_ns_roots()` itself before importing `module.src.*`, or the child crashes with `ModuleNotFoundError`. Set `multiprocessing.set_start_method("fork")` if the worker only needs inherited state and fork is available.

## GIT_CEILING_DIRECTORIES for "not a git repo" fixtures

When `tmp_path` lives under a directory that is itself inside a parent git repo (e.g. the pytest cache under `~/.hermes/cache/scratch/`), `git rev-parse --show-toplevel` walks up and finds the parent repo, so `repo_slug()` succeeds instead of raising `HostError`. The `not_a_git_repo` fixture must set `GIT_CEILING_DIRECTORIES` to `tmp_path.parent` (via `monkeypatch.setenv`) so git stops walking at the test directory boundary.

## Stale test assertions after spec changes

When an implementation change aligns code with the FRD spec (e.g. raising `PlanUsageError` for a missing file instead of returning a `PlanResult`), tests that assert the old behavior must be updated in the same PR — rename the test to reflect the new contract, change the assertion from `assertIsInstance(result, PlanResult)` to `assertRaises(PlanUsageError)`, and import the correct exception. Do not leave stale tests that pass on the base commit but fail after the fix lands; verify the test matches the FRD, not the old implementation.
