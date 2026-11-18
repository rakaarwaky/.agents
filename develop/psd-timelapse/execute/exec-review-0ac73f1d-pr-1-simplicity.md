# Simplicity Review — pr-1 (`0ac73f1d`)

## Summary

The change adds `GET /api/renders` listing endpoint and
`SystemOrchestrator.list_runs()`. Overall the implementation is
straightforward and most helpers are justified. Three findings below.

## Issues

### suggestion — `getattr(self._orchestrator, "list_runs", None)` fallback is speculative

- **File:** `modules/api/src/surface_api_run_controller.py`
- **Lines:** 66-68
- **Description:** The controller stores `self._orchestrator` typed as
  `ISystemAggregate`. At runtime the only production caller is
  `ApiContainer`, which wires `SystemContainer.orchestrator` — always a
  `SystemOrchestrator` that defines `list_runs`. The `getattr` / empty-list
  branch cannot fire in production. Every sibling controller
  (`EventsController`, `OutputController`, the `ApiController` itself) calls
  orchestrator methods directly without a `getattr` guard. The pattern is
  inconsistent and adds a branch that only a test with a `Mock` exercises.
  If `ISystemAggregate` is intentionally narrow (single `execute` entry
  point per AES402), the controller should reach the concrete
  `SystemOrchestrator` type directly, consistent with how the rest of the
  codebase treats non-`execute` methods (`get_state`, `get_progress`,
  `load_config` etc. are not on the interface but are called without guards
  throughout `surface_api_controller.py`, `surface_api_events_controller.py`,
  and `surface_cli_system_command.py`).
- **Suggestion:** Remove the `getattr` fallback. Either call
  `self._orchestrator.list_runs()` directly (the orchestrator always has
  it at runtime), or narrow the constructor parameter type to
  `SystemOrchestrator` so the dependency is explicit. The test
  `test_aggregate_without_list_runs_reports_empty_listing` can be dropped —
  it tests a scenario that cannot occur in production.

### nit — `_input_path_from_run_dir` round-trip check is over-thorough

- **File:** `modules/system/src/agent_system_orchestrator.py`
- **Lines:** 841-846
- **Description:** The helper already does `datetime.strptime(tail,
  RUN_FOLDER_TIMESTAMP_FORMAT)` (line 842) and then does a
  `parsed.strftime(RUN_FOLDER_TIMESTAMP_FORMAT) != tail` round-trip check
  (line 845). Because `strptime` accepts non-padded values (e.g. single-digit
  hours) that `strftime` would zero-pad, the round-trip check catches those
  edge cases — but the format is `"%Y-%m-%d_%Hh%Mm%Ss"` with all
  fixed-width numeric fields, and run directories are produced by
  `strftime` itself (`capabilities_system_workspace.py` line 69,
  `XDGPaths.psd_output_dir`). The round-trip check adds 2 lines for a
  case that never occurs in practice.
- **Suggestion:** Drop the round-trip check; `strptime` alone is sufficient
  to validate the tail shape for any name produced by this codebase.

### nit — `list_runs` builds a `(mtime, VO)` tuple list when `sorted` + key would suffice

- **File:** `modules/system/src/agent_system_orchestrator.py`
- **Lines:** 356-386
- **Description:** The method accumulates `(mtime, ListRunsItemVO)` tuples,
  sorts by `pair[0]` descending, then strips the mtime with a list
  comprehension. This is a manual decorate-sort-undecorate pattern that adds
  a type annotation (`list[tuple[float, ListRunsItemVO]]`) and an extra
  strip pass. The same result is achievable by collecting `ListRunsItemVO`
  items into a list and sorting with a key function that reads the mtime
  from the record file — but since mtime is needed during iteration anyway,
  the tuple approach is a reasonable idiom. The only simplification is to
  sort the `items` list in-place with `items.sort(key=lambda p: p[0],
  reverse=True)` (already done) and return
  `[item for _, item in items]` — which is exactly what the code does.
  Flagging as a nit because the pattern is slightly more verbose than
  necessary but not wrong; the tuple approach avoids a second
  `record_file.stat()` call, so it is the right trade-off.
- **Suggestion:** No change needed — this is the simplest correct approach
  given that mtime is already fetched during iteration. Noted for awareness.

## Items checked and found appropriately simple

- **`_terminal_record` returning a tuple** — Justified. Returns
  `(status, duration)` from the JSONL evidence file; a tuple is the minimal
  shape and inlining would tangle JSON parsing with the orchestrator loop.
  Correctly uses `json.loads` (not manual parsing) and `splitlines()` (not
  manual line splitting).

- **`_input_path_from_run_dir` as a separate helper** — Justified. The
  logic (tail-width calculation, `-` separator check, `strptime` validation,
  stem extraction) is self-contained and would clutter `list_runs` if
  inlined. The helper is used once but is non-trivial enough to warrant
  extraction.

- **`ListRunsItemVO` and `ListRunsItemResponse`** — Both needed. VO is
  the transport-agnostic data object; the Pydantic model is the API schema
  boundary. This matches the existing pattern (e.g. `RunResultVO` /
  `RunResultResponse`).

- **No reinvented stdlib** — `json.loads`, `Path.glob`, `Path.iterdir`,
  `Path.stat`, `datetime.strptime`, `datetime.now().strftime`,
  `sorted`/`list.sort` are all used correctly.

- **No speculative config flags or extra files** — None added.

- **Test file** — Appropriately focused; 8 tests cover the endpoint's
  behavior without padding.