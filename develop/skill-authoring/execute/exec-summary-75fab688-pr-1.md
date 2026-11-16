# Exec Summary: PR 1 — Align `curated_report` to `TelemetryRow` and Wire `SkillsOp.STATUS`

**Commit:** `7e535ae` on branch `rakaarwaky/75fab688-pr-1`
**Message:** `fix(observability): align curated_report to TelemetryRow and wire SkillsOp.STATUS`

## Changes (5 files, +48 −10)

### 1. `modules/root_skills_container.py`
Added `SkillsOp.STATUS` to `_OBSERVABILITY_OPS` frozenset so the `_ComposedAggregate.execute()` dispatcher routes STATUS requests to `ObservabilityAgent` instead of falling through to the "Unknown skills op" error path.

### 2. `modules/shared/src/design/taxonomy_design_response.py`
- Imported `TelemetryRow` under `TYPE_CHECKING` from `taxonomy_design_vo`.
- Widened `SkillsResult.records` annotation from `tuple[SkillRecord, ...]` to `tuple[SkillRecord | TelemetryRow, ...]`, allowing observability ops to populate telemetry rows without type violations.

### 3. `modules/observability/src/capabilities_skills_telemetry.py`
- Imported `TelemetryRow` from `shared.src.design.taxonomy_design_vo`.
- Rewrote `curated_report()` to return `tuple[TelemetryRow, ...]` instead of `list[dict]`.
- Each row now carries `name=skill_md.parent.name` plus all normalized sidecar fields (`state`, `pinned`, `created_by`, `created_at`, `first_seen_at`, `last_activity_at`, `archived_at`, `views`, `uses`, `activity_window_start`).
- Sort key changed from `state` to `name` for deterministic ordering.

### 4. `modules/observability/src/agent_observability_orchestrator.py`
Added `_execute_status()` method that delegates to `telemetry.curated_report(root)` and returns `SkillsResult(ok=True, records=report, exit_code=CLEAN)`. The existing `_handler_for()` dynamic dispatch resolves `SkillsOp.STATUS` → `_execute_status` automatically via the `_execute_{op.value}` naming convention.

### 5. `modules/cli/src/surface_skills_command.py`
Updated `_render_status()` and `_render_usage()` to format `TelemetryRow` attributes cleanly using `getattr()` instead of printing raw dataclass `repr()`. Status renders `name: state (pinned)`; usage renders `name: views=N uses=N state=S`.

## Verification

- All 5 modified files compile cleanly (`py_compile`).
- Observability tests: **8 passed, 1 skipped** — zero regressions.
- Cross-module tests (design, discovery, maintenance, observability): 73 passed, 2 skipped, 2 pre-existing failures unrelated to this change (Python 3.14 enum behavior in `test_unknown_op_returns_usage_error`; stale `test_drift_fails_closed` acceptance test).
