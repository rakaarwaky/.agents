# Lint Review — 0b9c3a95 (implement-deep-clean-findings)

## Tool results (all green except AES architecture scan)

| Tool | Command | Result |
|------|---------|--------|
| Ruff | `uv run ruff check modules/` | exit 0 — All checks passed |
| Ruff | `uv run ruff format --check modules/` | exit 0 — 88 files already formatted |
| Mypy | `uv run mypy modules/` | exit 0 — no issues found in 76 source files |
| pytest | `uv run pytest modules/ -q` | 46 passed, 1 skipped |
| AES scan | `lint-arwaky-cli scan .` | exit 1 — **24 total**, of which **6 are new regressions** (18 pre-existed at HEAD) |
| AES report | `lint-arwaky-cli report .` | first recorded scan for this target; shows 24 absolute |

Pre-existing 18 (unchanged by this task, in untouched files): image FRD.md AES609, image/video agent AES405, image processor AES403, plus the AES704 missing-test-suite-category entries under image/video. Out of scope.

New 6 violations, all traceable to this implementation.

---

## Issues introduced by this change

### Issue 1 [Lint] — Severity: bug
- **File**: `/home/raka/orca/workspaces/tools/implement-deep-clean-findings/modules/shared/src/utility_status.py:14`
- **Description**: AES201:FORBIDDEN_IMPORT — utility layer module imports from four other utility-layer files (`utility_config_handler`, `utility_dependency_checker`, `utility_llm_check`, `utility_version_resolver`). utility files must be stateless and independent; no other utility file at HEAD imports a sibling utility. This is the first violation of AES201 in the shared utility layer and it multiplies 4×.
- **Suggestion**: Either inline the small helper calls into `build_status_dict`, move `build_status_dict` up a layer, or add a documented exception. At minimum confirm `lint_arwaky.config.yaml` AES201 exceptions list and record it.
- **Status**: open

### Issue 2 [Lint] — Severity: bug
- **File**: `/home/raka/orca/workspaces/tools/implement-deep-clean-findings/modules/shared/src/utility_status.py:18`
- **Description**: AES201:FORBIDDEN_IMPORT — same root cause as Issue 1 (line 18 imports from `utility_dependency_checker`).
- **Suggestion**: Same as Issue 1.
- **Status**: open

### Issue 3 [Lint] — Severity: bug
- **File**: `/home/raka/orca/workspaces/tools/implement-deep-clean-findings/modules/shared/src/utility_status.py:19`
- **Description**: AES201:FORBIDDEN_IMPORT — same root cause (line 19 imports from `utility_llm_check`).
- **Suggestion**: Same as Issue 1.
- **Status**: open

### Issue 4 [Lint] — Severity: bug
- **File**: `/home/raka/orca/workspaces/tools/implement-deep-clean-findings/modules/shared/src/utility_status.py:20`
- **Description**: AES201:FORBIDDEN_IMPORT — same root cause (line 20 imports from `utility_version_resolver`).
- **Suggestion**: Same as Issue 1.
- **Status**: open

### Issue 5 [Lint] — Severity: bug
- **File**: `/home/raka/orca/workspaces/tools/implement-deep-clean-findings/modules/shared/src/utility_status.py:1`
- **Description**: AES101:NAMING_CONVENTION — new file name `utility_status.py` does not match the required convention (the tool suggests `utility_status_user.py`). This is a brand-new file added by this task; the violation did not exist at HEAD.
- **Suggestion**: Rename the file to the name the tool prescribes and update all four imports (`__init__.py`, `capabilities_system_job.py`, `surface_mcp_command.py`, `surface_tui_controller.py`), or add a documented AES101 exception.
- **Status**: open

### Issue 6 [Lint] — Severity: bug
- **File**: `/home/raka/orca/workspaces/tools/implement-deep-clean-findings/modules/video/src/capabilities_video_understanding.py:96`
- **Description**: AES304:BYPASS_COMMENT — `cap = None  # type: ignore[assignment]` is a lint suppression masking a type defect. The `# type: ignore` comment is flagged as a CRIT architecture violation and did not exist at HEAD (the line was introduced by Finding 9, which restructured the VideoCapture lifetime).
- **Suggestion**: Restructure so the variable can be re-typed cleanly instead of suppressed. For example, type `cap` from the start as `cv2.VideoCapture | None = open_video_capture(path)` and drop the `None` assignment + ignore. Then verify `uv run mypy modules/` still passes.
- **Status**: open

## Notes

- `uv run ruff check modules/`, `uv run ruff format --check modules/`, `uv run mypy modules/`, and `uv run pytest modules/ -q` all exit 0 cleanly. No formatting, import-order, dead-import, unused-variable, or type diagnostics in ruff/mypy.
- `lint-arwaky-cli scan .` exits 1 (6 new AES violations, all in `utility_status.py` and `capabilities_video_understanding.py`).
- `lint-arwaky-cli report .` shows no prior baseline for this target; it records the absolute 24 count. A second `report` run will produce a delta vs. this baseline.
- The 18 pre-existing AES violations (AES704, AES405, AES403, AES609) are in untouched files and are not regressions from this task.
