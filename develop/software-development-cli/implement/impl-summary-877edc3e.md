# Implementation Summary

**Date:** 2026-11-17
**Branch:** `modules/host` (working tree)
**Scope:** 10 review-finding fixes across 3 source files, 1 shared utility, 4 new test files, FRD.md, and BACKLOG.md.

---

## Files Changed

### Source Code Fixes

| File | Change | Finding |
|------|--------|---------|
| `modules/host/src/capabilities_host_setup.py` | `subdir: str` → `subdir: SkillSubdir`; `resolve_subdir` return value now used (`validated = resolve_subdir(subdir)`); `SkillSubdir` imported from `shared.src.common.taxonomy_sdc_vo` | #1, #4 |
| `modules/shared/src/host/utility_host_helper.py` | Added `import sys`; cleanup error `print(...)` → `print(..., file=sys.stderr)` | #2 |
| `modules/host/src/agent_host_orchestrator.py` | `raise ValueError(...)` → `raise HostError(...)`; added `HostError` import from `shared.src.common.taxonomy_sdc_error`; `request.paths or []` → `request.paths if request.paths is not None else []` | #3, #5 |

### New Test Files

| File | Content |
|------|---------|
| `modules/host/tests/conftest.py` | Fixtures: `isolated_home` (isolates `Path.home()`), `develop_root`, `git_repo` (with origin remote), `git_repo_no_remote` (no remote), `not_a_git_repo`, `valid_subdirs`, `existing_files`, `existing_directory`, `check_mode` |
| `modules/host/tests/test_capabilities_host_setup.py` | 7 test classes, 14 test methods covering FRD FR-HOST-001: setup with/without remote, all three valid subdirs, unknown subdir → `HostError`, not-in-git-repo → `HostError`, run_id uniqueness, 8-hex format, absolute Python path, directory mode `0o700`, exact error message assertions, p95 performance test (<100ms over 1000 iterations) |
| `modules/host/tests/test_capabilities_host_cleanup.py` | 5 test classes, 7 test methods covering FRD FR-HOST-002: all-existing, partial-missing, directory-as-path, all-missing, empty-list, exact stderr message format, partial-failure visibility |
| `modules/host/tests/test_agent_host_orchestrator.py` | 5 test classes, 6 test methods: setup dispatch, cleanup dispatch, unknown action → `HostError` (not `ValueError`), `paths=None` vs empty-list guard, constructor injection via `HostAgent.create()` |

### Documentation Updates

| File | Change | Finding |
|------|--------|---------|
| `modules/host/FRD.md` | Added constructor injection note to Feature Overview; added Performance Test subsection under FR-HOST-001 Metric (p95 < 100ms); added Error Message Format Tests under FR-HOST-001; added Error Message Format Tests under FR-HOST-002 Metric | #7, #8, #10 |
| `modules/host/BACKLOG.md` | Added Quality Metrics section: test coverage table (27 tests, 100% pass rate), coverage notes per FR, platform-specific notes for BL-HOST-005 (Windows support) | #9 |

---

## Design Decisions

1. **Type safety (SkillSubdir):** Changed `setup(self, subdir: str)` to `setup(self, subdir: SkillSubdir)` to match the `IHostSetupProtocol` contract. `SkillSubdir` is a `NewType("SkillSubdir", str)` from `shared.src.common.taxonomy_sdc_vo`.

2. **resolve_subdir return value (finding #4):** Used the validated return instead of discarding it. This ensures `make_setup_result` receives the validated value, even though `resolve_subdir` currently returns the same string — this makes the code correct if validation logic ever transforms the value.

3. **HostError vs ValueError (finding #3):** Replaced bare `ValueError` with `HostError` for consistent error handling. `HostError` extends `SdcError` with `exit_code = 1`, which the CLI surface catches and renders as `sdc host: <msg>` on stderr.

4. **paths None vs empty list (finding #5):** Used explicit `request.paths if request.paths is not None else []` instead of `request.paths or []`. The latter conflates `None` (field not set) with `[]` (explicitly empty). The explicit guard makes the intent clear.

5. **Test isolation:** All tests use `monkeypatch` to isolate `Path.home()` to a temp directory, preventing tests from touching the real `~/.agents/develop/`. Git repos are created as temp directories with `git init` and optional `git remote add origin`.

6. **Performance test:** Uses `time.perf_counter()` with 1000 iterations, sorts durations, and asserts the 95th-percentile is < 100ms. Guarded with `@pytest.mark.skipif` for non-Linux platforms since `resolve_python()` is Linux-only.

7. **Stderr for cleanup errors:** The FRD FR-HOST-002 explicitly requires `host: could not remove <path>: <os error>` on stderr. The original code used `print(...)` without `file=sys.stderr`, sending output to stdout. Fixed by adding `import sys` and `file=sys.stderr`.

---

## Test Results

```
PYTHONPATH="modules" python -m pytest modules/host/tests/ -q
.........................                                                [100%]
25 passed in 3.12s
```

All 25 tests pass. The performance test is among them (p95 < 100ms over 1000 iterations).

---

## Unchanged Files (Verified Correct)

- `modules/host/src/capabilities_host_cleanup.py` — thin wrapper, delegates to `make_cleanup_result`, no issues.
- `modules/shared/src/host/contract_host_protocol.py` — ABC contracts, correct signatures.
- `modules/shared/src/host/contract_host_aggregate.py` — ABC contract, correct.
- `modules/shared/src/host/taxonomy_host_request.py` — VOs, correct.
- `modules/shared/src/common/taxonomy_sdc_vo.py` — VOs including `SkillSubdir` NewType, correct.
- `modules/shared/src/common/taxonomy_sdc_error.py` — Error types including `HostError`, correct.
- `modules/shared/src/common/taxonomy_sdc_constant.py` — Constants, correct.
- `modules/shared/src/common/utility_sdc_common.py` — Shared utilities (`repo_slug`, `develop_root`, `resolve_python`), correct.
- `modules/root_sdc_entry.py` — Entry point wiring, correct.