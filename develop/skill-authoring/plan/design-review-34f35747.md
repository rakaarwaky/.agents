# Design Document Review: Fixing Skill-Authoring MCP Adapter Response Rendering and Lifecycle Operations

## Summary

**Verdict: Addressed** — All review issues and suggestions have been incorporated into the design document (`/home/raka/.agents/develop/skill-authoring/plan/design-doc-34f35747.md`). Specifically:
1. `curated_report` contract alignment to `tuple[TelemetryRow, ...]` with skill name retention has been designed into PR 1.
2. Tool counts corrected to 19 across all sections.
3. Flowchart narrowed to match actual MCP tools (`LIST`).
4. Overlap of `LINT` in `_DESIGN_OPS` and `_DISCOVERY_OPS` documented with precedence explanation.
5. Pre-existing `scan_summary` issue documented as out-of-scope tech debt.
6. Skill name extraction in `curated_report` solved by attaching `name=skill_md.parent.name` to `TelemetryRow`.
7. `_render_tool_result` simplified to dispatch solely on `result.op`.
8. `sac_create` schema requires both `skill` and `category`.
9. PR 2 test file moved to `modules/mcp/tests/unit_mcp_rendering.py`.
10. Code snippet added illustrating descriptor shape with embedded `inputSchema`.

---

## Issue 1: `curated_report` return type mismatch — design inherits a contract violation

- **Severity**: major
- **Section**: 4.3 (Fix 2: Resolution and Routing for `sac_status`), code block for `_execute_status`
- **Description**: The proposed `_execute_status` calls `telemetry.curated_report(root)` and passes the result directly as `records=tuple(report)` into `SkillsResult`. The protocol `ISkillsTelemetryProtocol.curated_report` declares `-> tuple[TelemetryRow, ...]` (in `contract_observability_protocol.py:120`), but the concrete implementation `SkillsTelemetry.curated_report` (in `capabilities_skills_telemetry.py:74`) returns `list[dict]`. `SkillsResult.records` is typed `tuple[SkillRecord, ...]`, not `tuple[dict, ...]` or `tuple[TelemetryRow, ...]`. The existing `_execute_usage` handler (line 148–149 of `agent_observability_orchestrator.py`) already commits this same violation, but the design does not acknowledge or plan to fix it. The proposed `_render_status_records` in section 4.3 defensively checks `isinstance(rec, dict)`, which implicitly acknowledges the mismatch without documenting it.
- **Suggestion**: Either (a) add an explicit note that `records` is effectively `tuple[Any, ...]` at runtime for telemetry ops and document this as accepted tech debt, or (b) include a preparatory PR that aligns `curated_report` to return `tuple[TelemetryRow, ...]` as its protocol promises, and update `_execute_usage` and the new `_execute_status` to map dicts to `TelemetryRow` objects. Option (b) is strongly preferred since it fixes the root cause.
- **Status**: addressed
- **Response**: Option (b) adopted. Section 4.3 and PR 1 have been updated to align `SkillsTelemetry.curated_report()` with its protocol contract `tuple[TelemetryRow, ...]`, populating all attributes of `TelemetryRow`. `SkillsResult.records` type annotation is updated in `taxonomy_design_response.py` to `tuple[SkillRecord | TelemetryRow, ...]`. Both `_execute_usage` and `_execute_status` will handle strongly-typed `TelemetryRow` instances.

---

## Issue 2: Tool count claim ("20 tools") is inconsistent with actual code

- **Severity**: minor
- **Section**: 1 (Overview), 3.1 (Goals), 4.4 (Schema Definitions)
- **Description**: The document repeatedly states "20 tool endpoints" and "all 20 MCP tools." Actual `list_tools()` returns 19 descriptors (verified by grep — there is no `sac_list_archived`, `sac_list_unmanaged`, or `sac_traces` tool). The `_op_from_tool` mapping also has 19 entries. The ground-truth header says 20, but the enumerated list ("list, read, export, lint, catalog, discover, move, archive, create, status, usage, run, pause, resume, pin, unpin, restore, prune, ledger") contains exactly 19 names. The schema table in section 4.4 similarly lists 19 rows.
- **Suggestion**: Audit which verbs are intentionally omitted from MCP (`list-archived`, `list-unmanaged`, `traces`) and either (a) correct the count to 19 throughout, or (b) add the missing tools to `list_tools()` and `_op_from_tool`. If verbs like `traces` are intentionally MCP-excluded, state why.
- **Status**: addressed
- **Response**: Corrected the count from 20 to 19 throughout the document (sections 1, 3.1, 4.4, Key Decisions, PR Plan). Omitted verbs (`list-archived`, `list-unmanaged`, `traces`) are CLI-only verbs not registered in MCP.

---

## Issue 3: `LIST_ARCHIVED` and `LIST_UNMANAGED` rendering not covered

- **Severity**: minor
- **Section**: 4.2 (Flowchart: `LIST / LIST_*`), 5.1 (proposed `_render_tool_result` code)
- **Description**: The flowchart in section 4.2 shows a branch `LIST / LIST_*` leading to `CheckRecords`, implying `LIST_ARCHIVED` and `LIST_UNMANAGED` will be handled. However, the proposed `_render_tool_result` code in section 5.1 only checks `tool == "list" or result.op == SkillsOp.LIST` — it does not match `SkillsOp.LIST_ARCHIVED` or `SkillsOp.LIST_UNMANAGED`. Since these verbs are not currently exposed via MCP `list_tools()`, this is not a runtime bug today, but the code contradicts the flowchart and will silently fall through to the exit-stub fallback if these tools are added later.
- **Suggestion**: Either expand the `_render_tool_result` condition to match `LIST_ARCHIVED` and `LIST_UNMANAGED` (future-proofing), or narrow the flowchart to match the code (show only `LIST`).
- **Status**: addressed
- **Response**: Narrowed the flowchart in section 4.2 from `LIST / LIST_*` to `LIST`, matching the code and the 19 registered MCP tools.

---

## Issue 4: `SkillsOp.LINT` appears in both `_DESIGN_OPS` and `_DISCOVERY_OPS`

- **Severity**: nit
- **Section**: 2.2B (listing of op routing sets)
- **Description**: The document quotes the routing sets verbatim and includes `LINT` in both `_DESIGN_OPS` and `_DISCOVERY_OPS`, which matches the actual code (`root_skills_container.py` lines 236–250). The `if/elif` chain in `_ComposedAggregate.execute()` means `_DESIGN_OPS` wins at runtime. The document does not flag this overlap or explain the intended behavior, which could confuse implementers.
- **Suggestion**: Add a one-line note: "`LINT` intentionally appears in both sets; `_DESIGN_OPS` takes precedence at the `if/elif` boundary."
- **Status**: addressed
- **Response**: Added an explicit explanatory note in Section 2.2B noting that `LINT` appears in both sets and that `_DESIGN_OPS` takes precedence at the `if/elif` boundary in `_ComposedAggregate.execute()`.

---

## Issue 5: `scan_summary` field used in `_execute_phrases` does not exist on `SkillsResult`

- **Severity**: minor (pre-existing bug, not introduced by this design)
- **Section**: Not directly addressed — but relevant to the "1:1 equivalence" goal
- **Description**: `ObservabilityAgent._execute_phrases` (line 201) constructs `SkillsResult(..., scan_summary=scan_result, ...)`, but `SkillsResult` (in `taxonomy_design_response.py`) has no `scan_summary` field. Because `SkillsResult` is `@dataclass(frozen=True)`, this would raise `TypeError` at runtime when `sac_traces` is invoked (though traces is not exposed in MCP). This is a pre-existing issue, not caused by this design, but the design claims "1:1 presentation equivalence" without noting it.
- **Suggestion**: Either add `scan_summary` to `SkillsResult`, or note this as known tech debt excluded from scope.
- **Status**: addressed
- **Response**: Added Section 3.2 Non-Goal 4 documenting `scan_summary` as a pre-existing issue on the unexposed `TRACES` verb, explicitly kept out of scope for this design cycle.

---

## Issue 6: `_execute_status` return shape may not match `_render_status` expectations

- **Severity**: major
- **Section**: 4.3 (proposed `_execute_status` code)
- **Description**: The design proposes `_execute_status` returning `records=tuple(report)` where `report` is `list[dict]` from `curated_report`. The CLI `_render_status` (lines 286–292) iterates `result.records` and prints each `rec` with `info(f"  {rec}")` — which works for dicts (prints `{'state': 'active', ...}`). The MCP `_render_status_records` checks `isinstance(rec, dict)` and extracts `rec.get("skill")` / `rec.get("name")`. But the actual dict keys from `curated_report` are set by `_normalize()` in `capabilities_skills_telemetry.py`, and the skill *name* is the dict key in the sidecar data, NOT a value inside the dict. Looking at line 80–83: `name = skill_md.parent.name` is used as the sidecar lookup key, but `rows.append(_normalize(record))` appends only the record — the skill name is lost. The MCP render code would find `rec.get("skill")` and `rec.get("name")` both None, falling back to `"unknown"`.
- **Suggestion**: `_execute_status` (or `curated_report`) must inject the skill name into each row dict (e.g., `record["skill"] = name`) before appending. Verify by reading `_normalize()` to confirm whether it already includes a `"skill"` or `"name"` key. If not, this is a data-layer fix needed in PR 1.
- **Status**: addressed
- **Response**: Solved completely by Issue 1's type alignment in PR 1. `SkillsTelemetry.curated_report()` will construct `TelemetryRow(name=name, ...)` where `name=skill_md.parent.name`. Both the CLI `_render_status` and MCP `_render_status_records` access `rec.name` and `rec.state`, completely eliminating `"unknown"` fallbacks and raw dict dumps.

---

## Issue 7: Proposed `_render_tool_result` dispatches on both `tool` string and `result.op` redundantly

- **Severity**: nit
- **Section**: 5.1 (After code block)
- **Description**: Each branch checks `tool == "list" or result.op == SkillsOp.LIST`. Since `_dispatch` already maps `tool` → `SkillsOp` and sets `result.op`, the `tool` string check is redundant and couples the renderer to raw verb names. If a new verb alias is added, both paths must be updated.
- **Suggestion**: Dispatch solely on `result.op`. The `tool` string is only needed for `_render_read_content` (to extract `args.get("skill")`), but even that can use `args` directly without tool-name matching.
- **Status**: addressed
- **Response**: Refactored `_render_tool_result(self, args: dict, result: SkillsResult)` in Section 5.1 and Key Decisions to dispatch solely on `result.op` (`SkillsOp.LIST`, `SkillsOp.READ`, `SkillsOp.STATUS`, `SkillsOp.USAGE`).

---

## Issue 8: `sac_create` schema marks only `skill` as required; `category` should also be required for `kind=skill`

- **Severity**: minor
- **Section**: 4.4 (Schema table, `sac_create` row)
- **Description**: The schema lists `required: ["skill"]` for `sac_create`. But `_execute_create` in `agent_design_orchestrator.py` (line 191–194) raises `SkillsUsageError("Missing --category")` when `kind != "category"` and no `category` flag is provided. The schema should communicate this conditional requirement or make `category` unconditionally required (since the common case is `kind=skill`). Without it, LLM agents will routinely omit `category` and receive an error.
- **Suggestion**: Either mark `category` as required in the schema (acceptable since `kind=category` uses the `query` field for the category name, not the `category` flag), or add a `description` note explaining the conditional requirement.
- **Status**: addressed
- **Response**: Updated the `sac_create` schema in Section 4.4 and PR 3 to list `required: ["skill", "category"]` with explanatory notes regarding `kind=skill` vs `kind=category`.

---

## Issue 9: PR 2 test file location

- **Severity**: nit
- **Section**: PR Plan, PR 2
- **Description**: PR 2 lists `modules/observability/tests/unit_observability.py` as the test target for MCP adapter rendering changes. MCP adapter tests should live in `modules/mcp/tests/`, not `modules/observability/tests/`. Section 7.3 (Verification) correctly identifies `modules/mcp/tests/` as the test location, contradicting the PR plan.
- **Suggestion**: PR 2's affected-files list should include `modules/mcp/tests/test_mcp_rendering.py` (or similar) instead of or in addition to `modules/observability/tests/unit_observability.py`.
- **Status**: addressed
- **Response**: Updated PR 2 in Section 7.3 and Section PR Plan to target `modules/mcp/tests/unit_mcp_rendering.py` for all MCP rendering unit tests.

---

## Issue 10: `root_mcp_entry.py` hardcodes empty schemas — design proposes pass-through but doesn't show the adapter change

- **Severity**: minor
- **Section**: 4.4, 5.2
- **Description**: The design says `list_tools()` in `SkillsMcpAdapter` will include `inputSchema` dicts and `root_mcp_entry.py` will pass them through via `d.get("inputSchema")`. But the proposed code for `list_tools()` (section 4.4's schema table) never shows how those schemas get INTO the descriptor dicts — the current `list_tools()` returns `[{"name": ..., "description": ...}]` with no `inputSchema` key. PR 3 says it will "populate explicit `inputSchema` definitions across all 20 tool descriptors in `list_tools()`" but the design never shows the modified `list_tools()` code. The entry point change is shown but the adapter-side change is only described in prose.
- **Suggestion**: Add a code snippet showing the new shape of at least one `list_tools()` descriptor, e.g. `{"name": "sac_read", "description": "...", "inputSchema": {...}}`. This removes ambiguity for the implementer.
- **Status**: addressed
- **Response**: Added a code snippet in Section 4.4 illustrating the exact descriptor structure returned by `list_tools()`, showing embedded `name`, `description`, and `inputSchema` dictionaries with typed properties and required arrays.

---

## Strengths

1. **Root-cause analysis is precise.** The document correctly traces the `"list: exit 0"` / `"read: exit 0"` symptoms to the `result.message or f"..."` fallback in `execute_tool()`, and correctly identifies that `DiscoveryResponse` leaves `message=""` on success while populating `records` and `content` in separate fields.

2. **AES layer discipline is maintained.** The fix keeps formatting in the surface layer (`SkillsMcpAdapter`) and domain logic in the agent layer, with no cross-layer pollution. The alternatives analysis correctly rejects stuffing pre-rendered strings into `DiscoveryResponse.message`.

3. **STATUS routing decision is well-reasoned.** Placing `SkillsOp.STATUS` in `_OBSERVABILITY_OPS` is architecturally correct — status inspects telemetry sidecars, which is the observability module's domain. The decision section provides clear rationale distinguishing STATUS from USAGE.

4. **PR ordering is sound.** PR 1 (routing fix) → PR 2 (rendering) → PR 3 (schemas) is a correct dependency chain. Each PR is independently mergeable and testable.

5. **Alternatives analysis is thorough.** Three alternatives are evaluated with concrete pros/cons, and the rejections are justified against stated project constraints (AES compliance, 1:1 CLI equivalence).

6. **Security considerations address path traversal.** The document notes that `SkillsReader` enforces boundary checks, which is the correct existing safeguard.

---

## Revision Summary

All 10 review issues have been reviewed, addressed, and incorporated into `/home/raka/.agents/develop/skill-authoring/plan/design-doc-34f35747.md`:
- **Contract & Data Safety:** Aligned `SkillsTelemetry.curated_report()` to return `tuple[TelemetryRow, ...]` with `name=skill_md.parent.name`, resolving Issue 1 and Issue 6 simultaneously. Updated `SkillsResult.records` annotation to `tuple[SkillRecord | TelemetryRow, ...]`.
- **Factual Accuracies:** Corrected tool count from 20 to 19 across all sections (Issue 2). Narrowed flowchart to `LIST` (Issue 3). Added documentation for `LINT` precedence in `_DESIGN_OPS` (Issue 4). Documented pre-existing `scan_summary` issue as out-of-scope tech debt (Issue 5).
- **Code Cleanliness & Precision:** Simplified `_render_tool_result` to dispatch solely on `result.op` (Issue 7). Updated `sac_create` schema to require `["skill", "category"]` (Issue 8). Directed PR 2 tests to `modules/mcp/tests/unit_mcp_rendering.py` (Issue 9). Added descriptor code snippet demonstrating embedded `inputSchema` in `list_tools()` (Issue 10).
