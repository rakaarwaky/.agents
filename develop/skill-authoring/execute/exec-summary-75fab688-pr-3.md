# Exec Summary: PR 3 — Typed JSON Input Schemas for All 19 `sac` MCP Tools

**Commit:** `fd48a72` on branch `rakaarwaky/75fab688-pr-3`
**Message:** `feat(mcp): declare typed JSON inputSchema for all 19 sac MCP tools`
**Base:** `ad2d0c2` (`fix(mcp): render records and content in SkillsMcpAdapter for 1:1 CLI equivalence`, PR 2)
**Push / PR:** not performed — this task explicitly forbids pushing or opening a PR.

## Changes (3 files, +493 −26)

### 1. `modules/mcp/src/surface_mcp_command.py` (+281 −26)

Rewrote `SkillsMcpAdapter.list_tools()`. The registry previously returned
19 single-line `{"name": ..., "description": ...}` dicts with no
`inputSchema`, so every tool advertised the same empty wildcard to MCP
clients. Each descriptor now embeds its own draft-07 `inputSchema` with
per-property `type` and `description`.

Schemas implemented (matching design doc §4.4 and the arguments the CLI
parsers accept):

| Tool | Required | Properties |
|------|----------|------------|
| `sac_list` | — | (none) |
| `sac_read` | `skill` | `skill`: string |
| `sac_export` | `skill` | `skill`: string |
| `sac_lint` | — | `category`: string |
| `sac_catalog` | — | `check`: boolean |
| `sac_discover` | `query` | `query`: string, `limit`: integer (default 20) |
| `sac_move` | `skill`, `target` | `skill`: string, `target`: string, `apply`: boolean |
| `sac_archive` | `skill` | `skill`: string, `apply`: boolean |
| `sac_create` | `skill`, `category` | `skill`: string, `category`: string, `kind`: string enum `skill`/`category`, `description`: string, `apply`: boolean |
| `sac_status` | — | `query`: string |
| `sac_usage` | — | `query`: string, `verb`: string enum `report`/`seed`/`reanchor` |
| `sac_run` | — | `apply`: boolean |
| `sac_pause` | — | (none) |
| `sac_resume` | — | (none) |
| `sac_pin` | `skill` | `skill`: string |
| `sac_unpin` | `skill` | `skill`: string |
| `sac_restore` | `skill` | `skill`: string, `category`: string, `apply`: boolean |
| `sac_prune` | — | `days`: integer, `purge_days`: integer, `dry_run`: boolean |
| `sac_ledger` | — | `action`: string, `skill`: string |

Two deliberate choices worth noting:

- **`sac_ledger.action` has no `enum`.** The task brief said "use `enum`
  for ... `action` in ledger", but design doc §4.4 types it as a plain
  string and the ledger capability (`capabilities_skills_ledger.py`)
  accepts arbitrary action strings, defaulting to `"patch"` and also
  writing `"rollback"`. A closed enum would have rejected valid ledger
  actions, so `action` is `{"type": "string"}` with a description. Test
  `test_ledger_action_is_a_free_form_string` (UT-MCP-SCHEMA-010) locks
  this decision in place.
- **Parameterless tools get a fresh dict each call.** The first draft
  hoisted `empty: dict = {"type": "object", "properties": {}}` out of the
  return list for `sac_list`/`sac_pause`/`sac_resume`. That aliased one
  mutable dict across three tools and across calls, so a client mutating
  one tool's advertised schema would silently change another's. Each of
  the three now inlines its own literal. Test UT-MCP-SCHEMA-012 asserts
  the three dicts are distinct objects.
- The docstring count was corrected from "(20 tools)" to "(19 tools)"; the
  registry has 19 entries.

### 2. `modules/root_mcp_entry.py` (+2 −5)

`_list_tools()` no longer hardcodes the wildcard schema. It forwards the
adapter descriptor:

```python
input_schema=d.get("inputSchema")
or {"type": "object", "properties": {}, "additionalProperties": True},
```

The wildcard is retained only as a fallback for a descriptor that omits
`inputSchema`, so a future tool added without a schema still lists
instead of raising.

### 3. `modules/mcp/tests/unit_mcp_schema.py` (new, 231 lines)

12 unit tests, following the `unit_*.py` naming and
`UT-MCP-SCHEMA-NNN` docstring convention used by
`unit_mcp_rendering.py`:

- `UT-MCP-SCHEMA-001` — `list_tools()` returns exactly the 19 expected
  verbs, in registry order, with no duplicates.
- `UT-MCP-SCHEMA-002` — every descriptor has `inputSchema` and a
  non-empty `description`; every schema is `type: object`.
- `UT-MCP-SCHEMA-003` — every declared property has a `type` and a
  non-empty `description`.
- `UT-MCP-SCHEMA-004` — mandatory args appear in `required` (data-driven
  over a `REQUIRED_ARGS` table).
- `UT-MCP-SCHEMA-005` — `sac_create` requires both `skill` and
  `category`.
- `UT-MCP-SCHEMA-006` — optional-only tools omit `required` entirely
  (10 tools checked).
- `UT-MCP-SCHEMA-007` — declared property types match the CLI flags,
  data-driven over a `PROPERTY_TYPES` table.
- `UT-MCP-SCHEMA-008` — `apply`/`dry_run` are boolean, `limit`/`days`/
  `purge_days` are integer, `limit` carries `default: 20`.
- `UT-MCP-SCHEMA-009` — `kind` enum is `["skill", "category"]`; `verb`
  enum is `["report", "seed", "reanchor"]`.
- `UT-MCP-SCHEMA-010` — ledger `action` is a free-form string.
- `UT-MCP-SCHEMA-011` — `sac_list`/`sac_pause`/`sac_resume` declare empty
  `properties`.
- `UT-MCP-SCHEMA-012` — those three schemas are not the same object.

The file bootstraps `sys.path` the same way `unit_mcp_rendering.py` does
and imports the adapter over a `MagicMock()` aggregate, since
`list_tools()` never touches the aggregate.

## Verification

Commands run from the worktree root. The worktree has no `pyproject.toml`,
no `.venv`, and `uv` cannot spawn `pytest` here, so the main checkout venv
was used directly (Python 3.14.9, pytest 9.2.0), with
`PYTHONPATH` covering every module `src/` dir and
`-o python_files="*.py"` for the non-`test_*.py` filenames.

| Check | Result |
|-------|--------|
| `pytest modules/mcp/tests -q -o python_files="*.py"` | **22 passed** (10 pre-existing + 12 new) |
| Full module suite (`design`, `discovery`, `maintenance`, `storage`, `observability`, `mcp`) | **115 passed, 1 skipped, 4 failed** |
| Same suite on PR-2 base `ad2d0c2` | 103 passed, 1 skipped, **the same 4 failures** |
| `mypy modules/mcp/src` | 9 errors, **all pre-existing** |
| `py_compile` on the 3 touched files | OK |

The 4 full-suite failures are pre-existing and unrelated to this change;
each was reproduced on the PR-2 base commit before any edit:

- `modules/design/tests/unit_design.py::test_unknown_op_returns_usage_error`
  — Python 3.14 enum behavior (known, per project memory).
- `modules/discovery/tests/acceptance_discovery.py::test_drift_fails_closed`
  — stale acceptance test (known, per PR-1 summary).
- `modules/discovery/tests/dogfood_discovery.py::test_cli_discover_subcommand`
  — pre-existing.
- `modules/observability/tests/unit_observability.py::test_execute_tool_empty_message_fallback`
  — introduced by PR 2's rendering change (it now expects
  `"list: exit 0"` but gets `"No skills in the pack yet."`); present on
  `ad2d0c2`, out of scope here.

### Runtime check of the pass-through

Beyond the unit tests, `_list_tools()` was invoked directly against the
composed adapter. It returned 19 `Tool` objects with the expected
per-tool `required` lists and property sets (e.g. `sac_create` →
`required=['skill', 'category']`, `props=['apply', 'category',
'description', 'kind', 'skill']`), and a stub adapter whose descriptor
omitted `inputSchema` produced the wildcard fallback
`{'type': 'object', 'properties': {}, 'additionalProperties': True}`.

## Notes / follow-ups

- **mypy is not clean and cannot be made clean here.** The pre-existing
  errors are `SkillsUsageError(str)` vs `ErrorMessage` arg-type mismatches
  in `surface_mcp_command.py` and `shared/src/common/utility_common_skills.py`,
  plus `import-untyped` on the sys.path-based `surface_mcp_command` import
  in the test files. None were introduced or worsened by this change; the
  task brief's `uv run mypy modules/mcp` is not runnable in this worktree
  (no uv project, no mypy installed), so the main checkout venv's mypy
  2.4.1 was used instead. The CI gate "Python compile check" is satisfied
  by `py_compile`.
- **`ruff` is not installed** in the available venv, so lint was limited
  to `py_compile` plus a manual check that no new line exceeds 100 chars
  (all over-length lines are box-drawing section comments, matching the
  existing file style).
- **Not pushed, no PR opened**, per instructions. Branch
  `rakaarwaky/75fab688-pr-3` is one commit ahead of the PR-2 branch head
  `ad2d0c2`; working tree is clean.
- `sac_usage`'s `verb` and `sac_create`'s `kind` are advisory in the
  schema (no `required` on the owning tool), which matches the design doc:
  both default server-side (`report`, and skill-kind behavior).