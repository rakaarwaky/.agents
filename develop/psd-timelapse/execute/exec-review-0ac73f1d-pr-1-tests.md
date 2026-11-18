# Test Review — pr-1: `GET /api/renders` listing endpoint

**Scope:** Test coverage and quality for the new `GET /api/renders` endpoint,
`SystemOrchestrator.list_runs()`, and associated schema/VO additions.

**Files reviewed:**
- `modules/api/tests/unit_api_run_listing.py` (new — 8 tests, 315 lines)
- `modules/api/tests/unit_api_local_surface.py` (updated — route set)
- `modules/system/src/agent_system_orchestrator.py` (implementation)
- `modules/api/src/surface_api_run_controller.py` (implementation)
- `modules/api/src/surface_api_schema_view.py` (implementation)

**Test run result:** All 8 tests pass in 0.53s.

---

## Summary

The 8 existing tests cover the happy paths (completed, failed, newest-first
ordering, empty/missing dirs) and the two key skip paths (no terminal record,
unmatched dir name). Specific assertions check exact `run_id`, `state`,
`input_path`, and `duration_s` values. The fake orchestrator / XDG monkeypatch
setup is sound and would catch a regression in the JSONL parsing or dir-name
parsing logic. The newest-first ordering test uses `os.utime` for deterministic
mtime and asserts exact run_id sequence, so it would fail if `list_runs` returned
runs in the wrong order.

However, there are several gaps in edge-case coverage and some tests miss
specific assertions on all fields. Issues below are ordered by severity.

---

## Issues

### 1. SUGGESTION — No test for cancelled run

**File:** `modules/api/tests/unit_api_run_listing.py`

**Description:** The task explicitly lists "cancelled run" as a required test
case. `TERMINAL_STAGE_VALUES` includes `PipelineStage.CANCELLED`, and the
orchestrator's `_finish_cancelled` writes a terminal record with `status:
"cancelled"` and `duration=None`. No test exercises this path. A regression that
accidentally drops `CANCELLED` from `TERMINAL_STAGE_VALUES`, or mis-handles the
`duration=None` case for cancelled runs, would go undetected.

**Suggestion:** Add a test mirroring `test_failed_run_is_listed`:

```python
def test_cancelled_run_is_listed(tmp_path: Path, monkeypatch) -> None:
    client = _client(tmp_path, monkeypatch)
    run_id = "22222222-3333-4444-5555-666666666666"
    _write_run(
        _data_dir(tmp_path),
        "cancelled-2026-08-29_10h51m06s",
        run_id,
        [_record(run_id, "cancelled", duration=None)],
    )
    item = client.get("/api/renders").json()["items"][0]
    assert item["run_id"] == run_id
    assert item["state"] == "cancelled"
    assert item["duration_s"] is None
    assert item["input_path"] == "cancelled.psd"
```

**Status:** open

---

### 2. SUGGESTION — No test for malformed JSON line in JSONL

**File:** `modules/api/tests/unit_api_run_listing.py`

**Description:** `_terminal_record` has explicit `try/except json.JSONDecodeError`
to skip malformed lines and continue scanning. This is a real error path that
could regress silently — a future refactor could let `JSONDecodeError` propagate
and 500 the endpoint. No test exercises this.

**Suggestion:** Write a JSONL file with a malformed line followed by a valid
terminal record and assert the valid record is still picked up:

```python
def test_malformed_jsonl_line_is_skipped(tmp_path: Path, monkeypatch) -> None:
    client = _client(tmp_path, monkeypatch)
    run_id = "33333333-4444-5555-6666-777777777777"
    log_dir = _data_dir(tmp_path) / "partial-2026-08-29_10h51m06s" / "log"
    log_dir.mkdir(parents=True)
    (log_dir / f"{run_id}.jsonl").write_text(
        '{"broken": not-json\n'
        + json.dumps(_record(run_id, "completed", duration=7.0))
        + "\n",
        encoding="utf-8",
    )
    body = client.get("/api/renders").json()
    assert len(body["items"]) == 1
    assert body["items"][0]["run_id"] == run_id
    assert body["items"][0]["state"] == "completed"
    assert body["items"][0]["duration_s"] == 7.0
```

**Status:** open

---

### 3. SUGGESTION — No test for empty JSONL file

**File:** `modules/api/tests/unit_api_run_listing.py`

**Description:** An empty `.jsonl` file (zero lines) is a plausible real-world
state: the evidence file is created by `FakeEvidence.initialize` but the worker
thread crashes before writing any records. `_terminal_record` handles this
correctly (the `for line in raw.splitlines()` loop never executes, `terminal`
stays `None`, returns `None`), but there's no test pinning this behavior.

**Suggestion:**

```python
def test_empty_jsonl_file_is_skipped(tmp_path: Path, monkeypatch) -> None:
    client = _client(tmp_path, monkeypatch)
    _write_run(
        _data_dir(tmp_path),
        "empty-2026-08-29_10h51m06s",
        "44444444-5555-6666-7777-888888888888",
        [],  # empty file
    )
    body = client.get("/api/renders").json()
    assert body["items"] == []
```

**Status:** open

---

### 4. SUGGESTION — `test_failed_run_is_listed` doesn't assert all fields

**File:** `modules/api/tests/unit_api_run_listing.py`, line 219–229

**Description:** The failed-run test only asserts `run_id` and `state`. It does
not check `input_path` or `duration_s`, unlike `test_completed_run_is_listed`
which asserts all four fields. A regression that drops `duration` extraction
for failed runs, or returns the wrong `input_path` for a failed run, would not
be caught here.

**Suggestion:** Extend the assertions:

```python
    item = client.get("/api/renders").json()["items"][0]
    assert item["run_id"] == run_id
    assert item["state"] == "failed"
    assert item["input_path"] == "broken.psd"
    assert item["duration_s"] == 3.0
```

**Status:** open

---

### 5. SUGGESTION — `test_unmatched_run_dir_name_reports_unknown_input` doesn't
assert all fields

**File:** `modules/api/tests/unit_api_run_listing.py`, lines 246–256

**Description:** Only asserts `run_id` and `input_path`. Does not check `state`
or `duration_s`. Since the implementation computes `input_path` before scanning
JSONL files, a regression that changes the control flow (e.g., skips the
`input_path` assignment for unmatched names) could be missed if only one field
is asserted.

**Suggestion:** Add:

```python
    assert item["state"] == "completed"
    assert item["duration_s"] == 1.0
```

**Status:** open

---

### 6. SUGGESTION — No test for `duration_s is None` when `duration` key is
absent from JSONL

**File:** `modules/api/tests/unit_api_run_listing.py`

**Description:** `_terminal_record` extracts duration as:

```python
duration = terminal.get("duration")
duration_s = float(duration) if isinstance(duration, (int, float)) else None
```

This means `duration=None` (absent key) yields `duration_s=None`, which is
distinct from `duration=0.0` (present, zero). The `_record` helper defaults to
`duration=12.5`, and all tests pass a value. No test pins the "duration key
absent" behavior, which is a realistic edge case for a terminal record that
predates the duration field.

**Suggestion:** Add a test with a terminal record that omits the `duration` key:

```python
def test_terminal_record_without_duration_reports_null(
    tmp_path: Path, monkeypatch
) -> None:
    client = _client(tmp_path, monkeypatch)
    run_id = "55555555-6666-7777-8888-999999999999"
    record = _record(run_id, "completed", duration=None)
    del record["duration"]  # simulate a record written without duration
    _write_run(
        _data_dir(tmp_path),
        "no-duration-2026-08-29_10h51m06s",
        run_id,
        [record],
    )
    item = client.get("/api/renders").json()["items"][0]
    assert item["run_id"] == run_id
    assert item["state"] == "completed"
    assert item["duration_s"] is None
```

**Status:** open

---

### 7. SUGGESTION — No test for JSONL where terminal record is not the last line

**File:** `modules/api/tests/unit_api_run_listing.py`

**Description:** `_terminal_record` iterates all lines and keeps the *last*
terminal record found (overwriting `terminal` on each match). If a JSONL file
has `completed` on line 1 followed by `progress` on line 2 (which can happen if
evidence is appended out-of-order), the implementation correctly picks
`completed` and ignores the trailing `progress`. But no test pins this — all
tests have the terminal record as the last line, or have `progress` before the
terminal. A regression that stops at the first terminal match (instead of the
last) would not be caught.

**Suggestion:**

```python
def test_last_terminal_record_wins(tmp_path: Path, monkeypatch) -> None:
    client = _client(tmp_path, monkeypatch)
    run_id = "66666666-7777-8888-9999-aaaaaaaaaaaa"
    _write_run(
        _data_dir(tmp_path),
        "multi-terminal-2026-08-29_10h51m06s",
        run_id,
        [
            _record(run_id, "completed", duration=10.0),
            _record(run_id, "progress", duration=None),
        ],
    )
    item = client.get("/api/renders").json()["items"][0]
    assert item["state"] == "completed"
    assert item["duration_s"] == 10.0
```

**Status:** open

---

### 8. SUGGESTION — No test that non-`.jsonl` files in the log directory are
ignored

**File:** `modules/api/tests/unit_api_run_listing.py`

**Description:** `list_runs` uses `log_dir.glob("*.jsonl")` so non-jsonl files
are naturally excluded. But no test confirms this. A regression that changes the
glob to `*` or uses `iterdir()` without filtering could pick up `.txt`, `.log`,
or `.tmp` files and crash on `json.loads`.

**Suggestion:** Create a non-jsonl file alongside a valid jsonl and assert only
the jsonl is listed:

```python
def test_non_jsonl_files_in_log_dir_are_ignored(
    tmp_path: Path, monkeypatch
) -> None:
    client = _client(tmp_path, monkeypatch)
    run_id = "77777777-8888-9999-aaaa-bbbbbbbbbbbb"
    log_dir = _data_dir(tmp_path) / "mixed-2026-08-29_10h51m06s" / "log"
    log_dir.mkdir(parents=True)
    (log_dir / f"{run_id}.jsonl").write_text(
        json.dumps(_record(run_id, "completed", duration=5.0)) + "\n",
        encoding="utf-8",
    )
    (log_dir / "debug.txt").write_text("not a jsonl", encoding="utf-8")
    (log_dir / "metadata.tmp").write_text("{broken", encoding="utf-8")
    body = client.get("/api/renders").json()
    assert len(body["items"]) == 1
    assert body["items"][0]["run_id"] == run_id
```

**Status:** open

---

### 9. NIT — `test_aggregate_without_list_runs_reports_empty_listing` doesn't
assert HTTP 200

**File:** `modules/api/tests/unit_api_run_listing.py`, lines 289–308

**Description:** The test asserts `body == {"items": []}` but does not check
`response.status_code == 200`. If a future change caused the fallback to return
a 500 error with an empty body (or a different 200 body), the test would still
pass because it only checks the JSON body.

**Suggestion:**

```python
    response = TestClient(controller.app).get("/api/renders")
    assert response.status_code == 200
    assert response.json() == {"items": []}
```

**Status:** open

---

### 10. NIT — All tests create the data dir in `_client` but don't clean up;
relying on `tmp_path` auto-cleanup is fine but the `_data_dir` helper
duplicates the `psd-timelapse` suffix

**File:** `modules/api/tests/unit_api_run_listing.py`, lines 145–157

**Description:** The `_client` helper sets `XDG_DATA_HOME` to `tmp_path`, and
`_data_dir` returns `tmp_path / "psd-timelapse"`. The string `"psd-timelapse"`
is hardcoded in both places. If `APP_NAME` ever changes (it's defined as a
constant in `taxonomy_common_constant.py`), these tests would silently break.
This is minor since the constant is stable, but using `APP_NAME` would be more
robust.

**Suggestion:** Import `APP_NAME` and use it:

```python
from modules.shared.src.common.taxonomy_common_constant import APP_NAME

def _data_dir(tmp_path: Path) -> Path:
    return tmp_path / APP_NAME
```

**Status:** open

---

### 11. NIT — `test_runs_are_listed_newest_first` only has two runs

**File:** `modules/api/tests/unit_api_run_listing.py`, lines 259–280

**Description:** Two runs is enough to verify sort direction (newest first).
However, with only two runs, a sort implementation that accidentally reverses
the list would produce `[older, newer]` which is caught, but a sort that only
swaps adjacent pairs (e.g., a buggy insertion sort) would also pass with two
elements. Three or more runs would provide stronger coverage. This is very minor
since the implementation uses Python's built-in `list.sort()`, which is
well-tested.

**Suggestion:** (optional) Add a third run with an intermediate mtime to make
the ordering test more robust against adjacent-swap bugs:

```python
    middle_file = _write_run(
        data_dir, "mid-2026-08-29_10h51m06s",
        "cccccccc-0000-0000-0000-000000000003",
        [_record("cccccccc-0000-0000-0000-000000000003", "completed", duration=1.5)],
    )
    os.utime(middle_file, (1_500_000, 1_500_000))
    # ...
    assert [i["run_id"] for i in items] == [newer, middle, older]
```

**Status:** open

---

## Coverage Matrix

| Required case | Test | Status |
|---|---|---|
| Empty output dir | `test_empty_output_dir_returns_empty_items` | Covered |
| Completed run | `test_completed_run_is_listed` | Covered |
| Failed run | `test_failed_run_is_listed` | Partial (missing `input_path`, `duration_s` assertions) |
| Cancelled run | — | **Missing** |
| No terminal record (skipped) | `test_run_without_terminal_record_is_skipped` | Covered |
| Dir name not matching pattern | `test_unmatched_run_dir_name_reports_unknown_input` | Partial (missing `state`, `duration_s` assertions) |
| Newest-first ordering | `test_runs_are_listed_newest_first` | Covered |
| Missing data dir | `test_missing_output_dir_returns_empty_items` | Covered |
| `duration_s` extraction (present) | `test_completed_run_is_listed` | Covered |
| `duration_s` extraction (absent) | — | **Missing** |
| Malformed JSON line | — | **Missing** |
| Empty JSONL file | — | **Missing** |
| Terminal record not last line | — | **Missing** |
| Non-.jsonl files ignored | — | **Missing** |
| Aggregate without `list_runs` fallback | `test_aggregate_without_list_runs_reports_empty_listing` | Covered |
| `duration_s is None` (cancelled path) | — | **Missing** |

---

## What's working well

- **Assertion specificity:** The completed-run test checks all four fields with
  exact values, which is the right pattern.
- **Newest-first ordering test:** Uses `os.utime` for deterministic mtime and
  asserts exact run_id sequence. This would fail if `list_runs` returned runs in
  the wrong order.
- **XDG monkeypatch setup:** Correctly points `XDG_DATA_HOME` at `tmp_path` and
  creates run dirs under `tmp_path / "psd-timelapse"`. The fake orchestrator
  with real `SystemOrchestrator` is the right approach — a `Mock(spec=
  ISystemAggregate)` would hide `list_runs` since it's not on the contract.
- **Test isolation:** Each test creates its own run dirs and doesn't depend on
  execution order. `tmp_path` auto-cleanup handles teardown.
- **Repo conventions:** Uses `TestClient`, follows the `test_<description>`
  naming pattern, imports from `modules.*` paths consistently.
- **Aggregate fallback test:** The `Mock(spec=ISystemAggregate)` test for the
  `getattr` fallback is a good defensive test — it pins the behavior when a
  future aggregate doesn't implement `list_runs`.

---

## Recommendations

1. **Add the cancelled-run test** (Issue 1) — this is the most significant gap
   since it's an explicitly required case and exercises a different terminal
   record path (`duration=None` via `_finish_cancelled`).
2. **Add malformed JSON, empty JSONL, and absent-duration tests** (Issues 2, 3,
   6) — these cover the error paths in `_terminal_record` that have explicit
   try/except guards.
3. **Strengthen the failed-run and unmatched-dir-name tests** (Issues 4, 5) with
   full field assertions.
4. **Add the terminal-record-not-last test** (Issue 7) to pin the "last terminal
   wins" semantics.
5. The non-jsonl and three-run ordering suggestions (Issues 8, 11) are nice-to-have
   but low priority given the current implementation.