# Review — Host Review-Finding Fixes (877edc3e)

**Date:** 2026-11-18
**Reviewer:** general
**Scope:** `modules/host/src/*.py`, `modules/shared/src/host/utility_host_helper.py`, `modules/host/tests/*.py`, `modules/host/FRD.md`, `modules/host/BACKLOG.md`

---

## Summary

The implementation correctly resolves all 10 review findings from the original task. The source-code changes are minimal, focused, and correct. The four new test files pass 25/25 on Linux. No security-relevant defects were found. Several minor style/documentation issues exist in the test files and docstrings. No scope creep detected: the FRD and BACKLOG updates align with the planned items in the summary.

**Verdict:** Approve with minor non-blocking issues.

---

## Issues

### 1. Bug — docstring in `capabilities_host_setup.py` references the wrong capability

| Field | Value |
|-------|-------|
| **Severity** | nit |
| **File:Line** | `modules/host/src/capabilities_host_setup.py:1` |
| **Description** | The module docstring reads `"""Host cleanup capability (AES capabilities layer).` and line 3 says `Implements IHostCleanupProtocol: unlinks file paths, skipping missing ones.` This is a copy-paste from `capabilities_host_cleanup.py`. The class actually implements `IHostSetupProtocol` and creates artifact directories, not unlinks files. |
| **Suggestion** | Replace the docstring with: `"""Host setup capability (AES capabilities layer).<br>Implements IHostSetupProtocol: creates the per-repo artifact root under<br>~/.agents/develop/<repo>/<subdir>/ and returns setup info."""` |
| **Status** | open |

---

### 2. Bug — `test_setup_with_remote` in `test_capabilities_host_setup.py` has an unused parameter

| Field | Value |
|-------|-------|
| **Severity** | nit |
| **File:Line** | `modules/host/tests/test_capabilities_host_setup.py:46` |
| **Description** | `test_creates_directory_with_remote(self, setup_cap, git_repo, develop_root, check_mode)` accepts `check_mode` but the assertion `check_mode(scratch)` is never called in this method body (it is called in `test_plan_subdir_with_remote` and `test_execute_subdir_with_remote`, but not here). This means the `0o700` mode check is silently skipped for the first test. |
| **Suggestion** | Add `check_mode(scratch)` to `test_creates_directory_with_remote` after the `scratch.is_dir()` assertion, matching the pattern in the sibling tests. |
| **Status** | open |

---

### 3. Bug — `existing_files` fixture in `conftest.py` has a misleading docstring

| Field | Value |
|-------|-------|
| **Severity** | nit |
| **File:Line** | `modules/host/tests/conftest.py:119` |
| **Description** | The docstring says `Usage: existing_files(tmp_path, 3)` implying the fixture is callable with a count argument. In reality `existing_files` is a plain pytest fixture (no parameterisation) that always creates exactly 3 files. The `tmp_path` in the docstring is already injected automatically. |
| **Suggestion** | Change the docstring to: `"""Create 3 existing files under tmp_path and return their paths as a list of strings."""` |
| **Status** | open |

---

### 4. Bug — `test_cleanup_empty` in `test_capabilities_host_cleanup.py` passes an unused `tmp_path` fixture

| Field | Value |
|-------|-------|
| **Severity** | nit |
| **File:Line** | `modules/host/tests/test_capabilities_host_cleanup.py:109` |
| **Description** | `def test_no_paths(self, tmp_path, capsys):` — `tmp_path` is injected but never used in the body. This is a harmless but sloppy signature; it can mislead a future reader into thinking the test depends on a temp directory. |
| **Suggestion** | Remove `tmp_path` from the parameter list: `def test_no_paths(self, capsys):` |
| **Status** | open |

---

### 5. Bug — performance test in `test_capabilities_host_setup.py` uses `__import__("sys").platform`

| Field | Value |
|-------|-------|
| **Severity** | nit |
| **File:Line** | `modules/host/tests/test_capabilities_host_setup.py:185` |
| **Description** | `@pytest.mark.skipif(os.name != "posix" or __import__("sys").platform != "linux", ...)` uses `__import__("sys")` inline instead of importing `sys` at the top of the module. The `os` module is already imported at the top; `sys` is not. This is inconsistent with the module's import style and makes the skip condition harder to read. |
| **Suggestion** | Add `import sys` to the top-of-module imports and change the skip condition to `os.name != "posix" or sys.platform != "linux"`. |
| **Status** | open |

---

### 6. Bug — `test_no_directory_created` in `TestSetupUnknownSubdir` has redundant logic

| Field | Value |
|-------|-------|
| **Severity** | nit |
| **File:Line** | `modules/host/tests/test_capabilities_host_setup.py:124` |
| **Description** | `test_no_directory_created(self, setup_cap, git_repo, develop_root)` asserts that after a `HostError` is raised, `develop_root / "my-repo" / "foo"` does not exist. However, since `resolve_subdir("foo")` raises before any directory creation, the directory is guaranteed not to exist. The `if repo_root.exists():` guard also makes the assertion vacuous when `repo_root` does not exist (which it won't, because the setup call failed before creating anything). The test would still pass even if the guard were removed entirely. |
| **Suggestion** | Simplify to: `assert not (develop_root / "my-repo" / "foo").exists()` without the `if repo_root.exists()` guard. Or, since this test adds little value beyond `test_raises_host_error` in the same class, consider merging the two assertions into a single test method. |
| **Status** | open |

---

### 7. Bug — `HostAgent.create()` in `agent_host_orchestrator.py` is a classmethod that duplicates the `__init__` signature

| Field | Value |
|-------|-------|
| **Severity** | suggestion |
| **File:Line** | `modules/host/src/agent_host_orchestrator.py:48` |
| **Description** | `HostAgent.create(setup_cap=..., cleanup_cap=...)` is a `@classmethod` that simply forwards to `cls(setup_cap=..., cleanup_cap=...)`. It adds no behaviour, no logging, no validation — it is a pass-through alias. This does not violate any rule, but it invites confusion: callers can construct `HostAgent` directly or via `HostAgent.create()` interchangeably with identical results. The FRD mentions constructor injection via `HostAgent.create()`, so it is a public API contract. |
| **Suggestion** | Either (a) document explicitly in the docstring that `create()` is a convenience alias for the constructor, or (b) remove `create()` and update the FRD to reference the constructor directly. Option (a) is lower-risk. |
| **Status** | open |

---

### 8. Bug — `make_scratch_dir` in `utility_host_helper.py` silently swallows `chmod` failures

| Field | Value |
|-------|-------|
| **Severity** | suggestion |
| **File:Line** | `modules/shared/src/host/utility_host_helper.py:57` |
| **Description** | `try: path.chmod(stat.S_IRWXU) except OSError: pass` — the `chmod` failure is silently discarded. The FRD explicitly says "failure to chmod shall not fail the setup operation", so this behaviour is correct by spec. However, the `pass` without any log or comment makes it invisible to future maintainers. The same pattern exists in `utility_sdc_common.scratch_dir_for` (line 154–156). |
| **Suggestion** | Add a brief comment: `# FR-HOST-001: chmod failure is non-fatal; the directory is still usable.` |
| **Status** | open |

---

### 9. Bug — `test_p95_latency_under_100ms` uses `setup_cap` which reuses the same `CapabilitiesHostSetup` instance across 1000 calls

| Field | Value |
|-------|-------|
| **Severity** | suggestion |
| **File:Line** | `modules/host/tests/test_capabilities_host_setup.py:192` |
| **Description** | The performance test calls `setup_cap.setup(...)` 1000 times in a tight loop. Each call invokes `resolve_python()` (which shells out or returns `sys.executable`), `repo_slug()` (which runs `git rev-parse`), and `make_scratch_dir()` (which calls `mkdir` with `exist_ok=True`). After the first call the directory already exists so `mkdir` is cheap, but `git rev-parse` and `shutil.which("python3")` are re-run 1000 times. The test is therefore measuring I/O + subprocess overhead, not the pure logic path. This is acceptable for a p95 gate (< 100ms is generous), but the test does not isolate the code under test from environment noise. |
| **Suggestion** | Consider mocking `repo_slug` and `resolve_python` with `monkeypatch` to measure the pure `make_setup_result` logic, or add a comment noting that the test includes subprocess overhead and the threshold was chosen with that in mind. |
| **Status** | open |

---

### 10. Bug — `HostRequest.subdir` defaults to `""` rather than `SkillSubdir`

| Field | Value |
|-------|-------|
| **Severity** | nit |
| **File:Line** | `modules/shared/src/host/taxonomy_host_request.py:27` |
| **Description** | `subdir: SkillSubdir = ""` — the default is a bare `str` literal `""`, not `SkillSubdir("")`. Since `SkillSubdir` is a `NewType("SkillSubdir", str)`, at runtime it is just `str`, so `""` is a valid `SkillSubdir`. This is technically correct but inconsistent: the type annotation says `SkillSubdir` and the default is a `str` literal. A mypy check with `--disallow-untyped-calls` or `--strict` would flag this. |
| **Suggestion** | Change the default to `SkillSubdir("")` for type-literal consistency: `subdir: SkillSubdir = SkillSubdir("")`. |
| **Status** | open |

---

### 11. Bug — `test_setup_routes_to_setup_cap` in `test_agent_host_orchestrator.py` asserts on a `SkillSubdir` value stored in a `list[str]`

| Field | Value |
|-------|-------|
| **Severity** | nit |
| **File:Line** | `modules/host/tests/test_agent_host_orchestrator.py:33` |
| **Description** | `FakeSetup.__init__` declares `self.calls: list[str] = []` but `test_setup_routes_to_setup_cap` asserts `setup_cap.calls == [SkillSubdir("implement")]`. `SkillSubdir` is a `NewType("SkillSubdir", str)`, so at runtime `SkillSubdir("implement") == "implement"` and the assertion passes. However, the type annotation on `calls` says `list[str]` while the comparison uses a `SkillSubdir` value. This is not a bug at runtime (NewType is erased), but it is a minor type-inconsistency that a strict type checker would flag. |
| **Suggestion** | Either change `calls: list[str]` to `calls: list[SkillSubdir]` in `FakeSetup`, or change the assertion to `setup_cap.calls == ["implement"]`. |
| **Status** | open |

---

### 12. Bug — `git_repo_no_remote` fixture creates a repo named `norepo` but the slug resolution falls back to the toplevel directory name

| Field | Value |
|-------|-------|
| **Severity** | nit |
| **File:Line** | `modules/host/tests/conftest.py:77` |
| **Description** | The fixture creates a git repo at `<tmp_path>/norepo/` and the docstring says `repo_slug() will resolve to norepo`. This is correct: when no origin remote is configured, `repo_slug()` falls back to `Path(git_toplevel).name` which is `norepo`. The test in `test_capabilities_host_setup.py:105` asserts `develop_root / "norepo" / SKILL_SUBDIR_PLAN`. This is all correct. However, the directory name `norepo` is slightly confusing — it reads as "no repo" rather than "a repo with no remote". |
| **Suggestion** | Rename the fixture directory to `plain-repo` or `bare-repo` to better convey "a git repo without an origin remote". This is purely cosmetic. |
| **Status** | open |

---

## Verification Checklist

| Focus Area | Result |
|------------|--------|
| **Type safety: `SkillSubdir` import and usage** | ✅ Correct. `capabilities_host_setup.py:1` imports `SkillSubdir` from `shared.src.common.taxonomy_sdc_vo`. `setup(self, subdir: SkillSubdir)` matches `IHostSetupProtocol`. `resolve_subdir` accepts `str` (NewType is erased at runtime), which is fine. |
| **Cleanup error routing: `sys.stderr`** | ✅ Correct. `utility_host_helper.py:11` adds `import sys`; `make_cleanup_result` at line 82 uses `print(..., file=sys.stderr)`. Test `test_directory_unlink_fails` and `test_each_failure_reported` both use `capsys.readouterr().err` to verify. |
| **Error handling consistency: `HostError` replaces `ValueError`** | ✅ Correct. `agent_host_orchestrator.py:5` imports `HostError` from `shared.src.common.taxonomy_sdc_error`. The `dispatch` method raises `HostError(...)` at line 38. Test `test_raises_host_error_not_valueerror` in `test_agent_host_orchestrator.py:95` confirms `HostError` (not `ValueError`) is raised. |
| **`paths` guard: None vs empty-list semantics** | ✅ Correct. `agent_host_orchestrator.py:39` uses `request.paths if request.paths is not None else []`. Test `test_paths_none_treated_as_empty` in `test_agent_host_orchestrator.py:107` confirms `cleanup_cap.calls == [[]]` when `paths=None`. |
| **Test coverage: all FRD test cases** | ✅ Verified. FR-HOST-001: setup with/without remote, all 3 subdirs, unknown subdir, not-in-git-repo, run_id uniqueness, 8-hex format, absolute Python path, 0o700 mode, exact error messages, p95 perf. FR-HOST-002: all-existing, partial-missing, directory-as-path, all-missing, empty-list, exact stderr format, partial-failure visibility. Orchestrator: setup dispatch, cleanup dispatch, unknown action, paths=None guard, constructor injection. All 25 tests pass. |
| **No scope creep** | ✅ FRD and BACKLOG updates are limited to the items listed in the summary. No unplanned features added. |
| **Security: input validation, injection, secrets** | ✅ No security-relevant defects. `resolve_subdir` validates against a closed set of 3 values. `repo_slug` runs `git` subprocesses with `capture_output=True` and a timeout. No user input is interpolated into shell commands. No secrets are logged. |
| **No `unwrap()`, unnecessary `clone()`, or lock usage** | ✅ N/A — Python codebase, no such patterns present. |

---

## Test Results

```
PYTHONPATH="modules" .venv/bin/python3 -m pytest modules/host/tests/ -q
25 passed in 3.40s
```

All 25 tests pass. The performance test (p95 < 100ms over 1000 iterations) is among them.

---

## Verdict

**Approve with minor non-blocking issues.** All 10 review findings from the original task are correctly resolved. The source-code changes are minimal and correct. The test suite is comprehensive and passes. The 12 issues identified above are all `nit` or `suggestion` severity — none block merge. The most actionable items are #1 (wrong docstring in `capabilities_host_setup.py`), #2 (missing `check_mode` assertion in one test), and #10 (type-literal inconsistency in `HostRequest`).
