# General Code Review — pr-1: `GET /api/renders` listing endpoint + `SystemOrchestrator.list_runs()`

**Commit:** `c2af901c feat(api): add GET /renders listing endpoint and orchestrator.list_runs()`
**Author design doc:** `/home/raka/.agents/develop/psd-timelapse/plan/design-doc-0ac73f1d.md` (PR 1 section)
**Exec summary:** `/home/raka/.agents/develop/psd-timelapse/execute/exec-summary-0ac73f1d-pr-1.md`
**Companion review:** `/home/raka/.agents/develop/psd-timelapse/execute/exec-review-0ac73f1d-pr-1-tests.md`

## Files reviewed

- `modules/system/src/agent_system_orchestrator.py` (new `list_runs` + `_terminal_record` + `_input_path_from_run_dir`)
- `modules/api/src/surface_api_run_controller.py` (new `list_runs` + `GET /renders` route)
- `modules/api/src/surface_api_schema_view.py` (new `RunListResponse` / `ListRunsItemResponse`)
- `modules/shared/src/system/taxonomy_system_vo.py` (new `ListRunsItemVO`)
- `modules/api/tests/unit_api_run_listing.py` (new test file — covered by companion review)
- `modules/api/tests/unit_api_local_surface.py` (`DOCUMENTED_ROUTES` updated)
- `fixtures/openapi.json` (regenerated — verified contains `ListRunsItemResponse`, `RunListResponse`, `GET /api/renders`)

## Verification performed

| Check | Result |
|-------|--------|
| `uv run pytest modules/api/tests/unit_api_run_listing.py -q` | 8 passed |
| `uv run ruff check` on changed source files | All checks passed |
| `fixtures/openapi.json` contains new schemas + path | Confirmed (`ListRunsItemResponse` L194, `RunListResponse` L368, `/api/renders` GET L775) |
| `GET /renders` response codes in fixture | `200` only (no `500` documented) |
| `ISystemAggregate` unchanged | Confirmed — single `execute()` only |
| `execute()` entry point preserved | Confirmed — `RunViewController` reaches `list_runs` via `getattr`, aggregate not extended |
| No standalone `RunResultVO` JSON parsing | Confirmed — only JSONL evidence scan |
| `_terminal_record` picks terminal status, not progress/error | Confirmed — `record.get("status") in TERMINAL_STAGE_VALUES` excludes `"progress"` and `"error"` |
| `_terminal_record` returns LAST terminal (not first) | Confirmed — overwrites `terminal` for each matching line |
| Malformed JSONL line skipped | Confirmed — `try/except json.JSONDecodeError: continue` |
| Missing data dir returns `[]` | Confirmed — `if not root.exists(): return []` |
| `_input_path_from_run_dir` edge cases (empty stem, bad ts, no dash, normal) | Verified by direct invocation — all correct |
| `getattr` fallback for aggregate without `list_runs` | Confirmed — returns empty `RunListResponse` |
| Test coverage gaps (cancelled, malformed, empty JSONL, custom output_dir) | See companion test review — not duplicated here |

## Verdict

The implementation is correct, faithful to the design-doc PR 1 scope, and free
of security or correctness defects. The terminal-record logic, run-dir name
parsing, and robustness (missing dir / malformed JSON / missing file) all match
the design intent. No scope creep, no missing planned items.

Five findings below are all **suggestions/nits** — none block merge.

---

## Issues

### Issue 1 -- Severity: suggestion

- **File**: `modules/system/src/agent_system_orchestrator.py:347-348`
- **Description**: `list_runs` scans `XDGPaths.data_dir()` as the sole run-directory root. The design doc says "Enumerates run directories under the XDG **output dir**" and "The `output_dir` comes from the injected configuration's `SystemConfigVO.output_dir` (default XDG data dir)." The implementation hard-codes `XDGPaths.data_dir()`, ignoring `self._configuration.load().output_dir`. In the default profile these are identical (`capabilities_system_configuration.py:166` sets `data_dir = str(XDGPaths.data_dir())`), so the PR works as-shipped. But `output_dir` is an `OVERRIDABLE_CONFIG_FIELDS` member (`taxonomy_system_constant.py:64`), so an operator who sets a custom `output_dir` in `config.json` would write runs there (via `capabilities_system_workspace.py:prepare`), yet `list_runs` would never see them — silent under-reporting of completed renders.
- **Suggestion**: Read `output_dir` from the injected configuration and scan that path:
  ```python
  config = self._configuration.load()
  root = Path(config.output_dir.value).expanduser()
  ```
  This honors the design doc's "injected configuration's `SystemConfigVO.output_dir`" wording and stays consistent with how `capabilities_system_workspace.prepare` places run dirs. If a custom `output_dir` is considered out of scope for this PR, add a code comment documenting that `list_runs` intentionally scans only `XDGPaths.data_dir()` so a future reviewer understands the deviation.
- **Status**: open

### Issue 2 -- Severity: suggestion

- **File**: `modules/api/src/surface_api_run_controller.py:58-61`
- **Description**: The `list_runs` method uses `getattr(self._orchestrator, "list_runs", None)` and silently returns an empty listing when the attribute is absent. This is intentionally tolerant per the docstring, but the pattern weakens static checkability: a typo in the attribute name would be invisible at review time (mypy can't catch it), and a future refactor that renames `list_runs` on the concrete orchestrator would silently degrade the endpoint to always-empty without any signal. The companion `OutputController` and the existing `RunViewController.get_view` call `self._orchestrator.get_run_result(...)` directly on the `ISystemAggregate` type (which declares it via the protocol surface the controller uses), so the `getattr` indirection is unique to this PR.
- **Suggestion**: Two options —
  1. **Preferred:** Type the controller's `_orchestrator` as `SystemOrchestrator` (concrete) instead of `ISystemAggregate`, and call `self._orchestrator.list_runs()` directly. This makes the call statically checkable and removes the silent-fallback branch. `ISystemAggregate` is preserved unchanged (per the design doc's requirement), and the controller is allowed to reach concrete capabilities — the existing `OutputController` already does this via `get_run_result`.
  2. **Minimal:** Keep the `getattr` but add a `# type: ignore[attr-defined]` suppression or a `Protocol` that declares `list_runs`, so a future rename surfaces at mypy time.
- **Status**: open

### Issue 3 -- Severity: suggestion

- **File**: `modules/api/src/surface_api_run_controller.py:49-55`
- **Description**: The `GET /renders` route is registered without a `responses=` argument, so the OpenAPI fixture documents only `200` for this endpoint (confirmed: `fixtures/openapi.json` shows `GET /api/renders` → `responses: ['200']`). The companion `POST /renders` documents `400, 409, 422, 500`, and `GET /renders/{run_id}/view` documents `400, 404, 422`. If the orchestrator's `list_runs` ever raises unexpectedly (e.g., a future change removes the `root.exists()` guard, or `iterdir()` fails on a permissions error), FastAPI's default `ServerErrorMiddleware` would return a `500` that is not in the documented contract. The `test_openapi_documents_a_typed_body_for_every_json_success` test only checks that a `200` is present, not that `500` is documented, so this is not caught by CI.
- **Suggestion**: Either (a) add `responses=error_responses(500)` to the `router.add_api_route("/renders", ...)` call for consistency with the other run routes and to document the theoretical failure mode, or (b) confirm that the best-effort contract ("missing or malformed file is skipped, and an absent data dir yields an empty listing rather than raising") is the intended guarantee and add a code comment making that explicit. Option (a) is preferred for consistency.
- **Status**: open

### Issue 4 -- Severity: suggestion

- **File**: `modules/api/tests/unit_api_run_listing.py:307-308`
- **Description**: `test_aggregate_without_list_runs_reports_empty_listing` is tautological. It constructs a `Mock(spec=ISystemAggregate)` (which has no `list_runs` attribute by design), so `getattr(..., "list_runs", None)` is guaranteed to be `None` and the test exercises only the fallback branch. The test passes regardless of whether the controller's mapping logic (`ListRunsItemResponse` construction from `ListRunsItemVO`) is correct. A future regression that swapped the `if list_runs_fn is None: return RunListResponse(items=[])` branch with the mapping branch (or vice versa) would still pass. The companion test review also flags test-coverage gaps; this issue is about the *quality* of an existing test rather than a missing case.
- **Suggestion**: Either strengthen this test to also assert that the orchestrator's `list_runs` was never called (e.g., `orchestrator.list_runs.assert_not_called()` won't work since `Mock(spec=...)` doesn't expose it — use a `Mock()` without `spec` and set `list_runs` to a `Mock` that raises `AssertionError`), or remove the test and rely on the eight other tests that exercise the real `SystemOrchestrator.list_runs` path. The fallback branch is defensive enough that an explicit unit test of the "aggregate without list_runs" path has limited value.
- **Status**: open

### Issue 5 -- Severity: nit

- **File**: `modules/system/src/agent_system_orchestrator.py:346-348`
- **Description**: The docstring on `list_runs` accurately describes the on-disk scan and the best-effort guarantee, but it does not mention that the scan is rooted at `XDGPaths.data_dir()` specifically (vs. the configured `output_dir`). A reader who configures a custom `output_dir` would reasonably expect the listing to include runs written there. The gap is invisible from the docstring alone.
- **Suggestion**: Add one sentence to the docstring: `"Scans ``XDGPaths.data_dir()`` (the default output dir); runs written to a custom configured ``output_dir`` are not included."` This makes the limitation explicit and pairs with Issue 1.
- **Status**: open

---

## Non-issues explicitly verified

For the reviewer's checklist:

- **`ISystemAggregate` left unextended**: Confirmed — `modules/shared/src/system/contract_system_aggregate.py` still declares only `execute()`. The controller reaches `list_runs` via `getattr` on the concrete orchestrator.
- **`execute()` entry point preserved**: Confirmed — `ApiController.__init__` still mounts `RunViewController(orchestrator).register(self.router)` at line 107; no change to `surface_api_controller.py`.
- **FastAPI route ordering**: Confirmed — `/renders` (exact) is registered before `/renders/{run_id}/view` in `RunViewController.register`, and FastAPI matches exact paths before parameterized ones. The existing `GET /renders/{run_id}` (result), `GET /renders/{run_id}/view`, etc. are registered by `ApiController._register_routes` and `RunViewController.register` respectively; `/renders` (GET) does not collide with `POST /renders` (different method) or with `/renders/{run_id}` (different path shape). The OpenAPI fixture confirms both `GET /api/renders` and `POST /api/renders` coexist.
- **Response model**: Confirmed — `response_model=RunListResponse` is set on the route, and `RunListResponse.items` is `list[ListRunsItemResponse]` with the correct fields (`run_id`, `state`, `input_path`, `duration_s`).
- **Terminal record identification**: Confirmed — `_terminal_record` reads the whole JSONL file line-by-line, parses each non-blank line as JSON, skips malformed lines and non-dict records, and overwrites `terminal` for each record whose `status` is in `TERMINAL_STAGE_VALUES` (`completed`, `failed`, `cancelled`). A `progress` or `error` record is correctly ignored. The last terminal record wins (overwrite behavior).
- **Run-dir → PSD-stem → input_path**: Confirmed — `_input_path_from_run_dir` validates the trailing `-<timestamp>` shape, round-trips the timestamp through `strptime`/`strftime` to reject impossible dates, and returns `"<stem>.psd"` or `"unknown"`. Verified by direct invocation: `"sycan-pants-2026-08-29_10h51m06s"` → `"sycan-pants.psd"`; `"no-timestamp-here"` → `"unknown"`; `"foo-9999-99-99_99h99m99s"` → `"unknown"`; empty stem → `"unknown"`.
- **Robustness**: Confirmed — `root.exists()` guard for missing data dir; `entry.is_dir()` filter; `log_dir.is_dir()` guard; `try/except OSError` around `read_text`; `try/except json.JSONDecodeError: continue` per line; `try/except OSError: continue` around `stat().st_mtime`. No exception path out of `list_runs` except from `XDGPaths.data_dir()` itself (which is a pure path construction, no I/O).
- **openapi.json fixture**: Confirmed — contains `ListRunsItemResponse` (L194), `RunListResponse` (L368), and `GET /api/renders` path (L775) with the correct `$ref` to `RunListResponse`. The fixture was regenerated as required.
- **No scope creep**: Confirmed — only the files listed in the design-doc PR 1 section were modified. No auth, no hosting, no remote transport, no new Python module beyond the listing route. `ISystemAggregate` not extended. `RunResultVO` not parsed from disk.
- **No missing planned items**: Confirmed — all design-doc PR 1 deliverables are present: `ListRunsItemVO`, `list_runs()` on `SystemOrchestrator`, `RunListResponse`/`ListRunsItemResponse` Pydantic models, `GET /renders` route mounted in `register()`, regenerated OpenAPI fixture, new unit test file, `DOCUMENTED_ROUTES` updated.

---

## Summary

| Severity | Count | IDs |
|----------|-------|-----|
| bug | 0 | — |
| suggestion | 4 | 1, 2, 3, 4 |
| nit | 1 | 5 |

No bugs. No security defects. No correctness defects. No scope creep. No missing
planned items. The four suggestions and one nit are all about robustness
hardening and documentation clarity; none block merge.