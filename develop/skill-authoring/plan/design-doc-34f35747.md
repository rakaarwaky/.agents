# Design Document: Fixing Skill-Authoring MCP Adapter Response Rendering and Lifecycle Operations

**Title:** Fix Skill-Authoring MCP Module Response Rendering and Lifecycle Equivalence  
**Author:** Grok Build (Antigravity Systems Architect)  
**Date:** 2026-11-17  
**Status:** Draft  
**Target Module:** `skill-authoring-tools` (`modules/mcp/`, `modules/root_mcp_entry.py`, `modules/root_skills_container.py`, `modules/design/src/agent_design_orchestrator.py`, `modules/observability/src/agent_observability_orchestrator.py`)  

---

## 1. Overview

The `skill-authoring-tools` Model Context Protocol (MCP) server provides 19 tool endpoints (`sac_*`) that bridge LLM agent interactions to the underlying `sac` skill-pack toolset. Although the command-line interface (`sac`) works effectively for browsing, auditing, and executing skill lifecycle operations, the MCP surface suffers from significant presentation and execution defects:

1. **`sac_list` output suppression:** The tool returns a generic exit stub (`"list: exit 0"`) instead of the formatted skill inventory table (skill name, truncated description, and total skill count) produced by the CLI.
2. **`sac_read` content omission:** The tool returns `"read: exit 0"` instead of rendering the raw markdown content of the requested `SKILL.md`.
3. **`sac_status` routing failure:** Invoking `sac_status` causes an immediate fatal error (`"Unknown skills op: status"` / `"Unknown skills subcommand: status"`), rendering the lifecycle state inspectability broken across both the MCP server and CLI entry points.

This design document establishes the architectural and behavioral fixes required to achieve strict 1:1 functional equivalence between the MCP adapter and the CLI surface, resolves the missing lifecycle handler and telemetry type alignment in the system aggregate orchestrators, and details a phased path to expose structured JSON schemas for all 19 MCP tool parameters.

---

## 2. Background & Motivation

### 2.1 Current State Architecture
The `skill-authoring` package is structured according to the Antigravity Extensible Standard (AES) layered architecture:
- **AES Surface Layer (`modules/cli/`, `modules/mcp/`):** Translates incoming transport inputs (CLI arguments or JSON-RPC tool parameters) into internal request value objects (`SkillsRequest`), dispatches them to an `ISkillsAggregate`, and serializes the resulting `SkillsResult` for the caller.
- **AES Composition Root (`modules/root_skills_container.py`, `modules/root_mcp_entry.py`):** Instantiates capabilities across five bounded modules (`design`, `discovery`, `maintenance`, `observability`, `storage`), binds them into `_ComposedAggregate`, and exposes public factories such as `create_mcp_adapter()` and `default_aggregate()`.
- **AES Agents / Orchestrators:** `SkillsDiscoveryAgent`, `SkillsDesignAgent`, `SkillsObservabilityAgent`, `SkillsMaintenanceAgent`, and `SkillsStorageAgent` implement domain logic and return typed responses (`DiscoveryResponse`, `MaintenanceResponse`, `SkillsResult`).

### 2.2 The Root Causes

#### A. Decoupled Fields in `SkillsResult`
`SkillsResult` (defined in `modules/shared/src/design/taxonomy_design_response.py`) carries distinct payload fields tailored for specific verbs:
- `records: tuple[SkillRecord, ...]` (runtime union `tuple[SkillRecord | TelemetryRow, ...]`): Populated during `LIST`, `LIST_ARCHIVED`, `LIST_UNMANAGED`, and telemetry queries (`STATUS`, `USAGE`).
- `content: SkillContent | None`: Populated during `READ` (raw string of `SKILL.md`).
- `message: str`: Populated with concise status strings, operational warnings, or error descriptions.
- `lint_report`, `catalog`, `phrases_exact`: Populated for specialized operations.

In `modules/mcp/src/surface_mcp_command.py`, `SkillsMcpAdapter.execute_tool()` produces its text payload using:
```python
text = result.message or f"{result.op}: exit {result.exit_code}"
```
When `sac_list` executes, `_execute_list` in `SkillsDiscoveryAgent` generates a `DiscoveryResponse(ok=True, verb=..., records=records)` with an empty `message`. This maps in `modules/root_skills_container.py` via `_discovery_response_to_result()` to `SkillsResult(records=records, message="")`. Because `result.message` is falsy, the adapter evaluates the fallback expression `f"{result.op}: exit {result.exit_code}"`, returning `"list: exit 0"`.

Similarly, when `sac_read` runs, `_execute_read` generates `DiscoveryResponse(ok=True, verb=..., content=content, message="")`. `result.content` holds the text, but `result.message` is empty, leading to the fallback string `"read: exit 0"`.

#### B. The `STATUS` Orphaned Operation
In `modules/mcp/src/surface_mcp_command.py`, `_op_from_tool("status")` maps to `SkillsOp.STATUS`. In `modules/cli/src/surface_skills_command.py`, `"status"` is in `_LIFECYCLE_OPS`. However, in `modules/root_skills_container.py`, `SkillsOp.STATUS` is completely omitted from the operation routing tables:
- `_DESIGN_OPS`: `{CREATE, LINT}`
- `_DISCOVERY_OPS`: `{CATALOG, DISCOVER, LINT, LIST, LIST_ARCHIVED, LIST_UNMANAGED, READ}`
  *(Note: `SkillsOp.LINT` appears in both `_DESIGN_OPS` and `_DISCOVERY_OPS` in the existing codebase; because `_ComposedAggregate.execute()` evaluates `_DESIGN_OPS` first in its `if/elif` chain, `LINT` routes to `_design`.)*
- `_MAINTENANCE_OPS`: `{PRUNE, PAUSE, RESUME, RUN, MOVE, PIN, UNPIN}`
- `_OBSERVABILITY_OPS`: `{LEDGER, USAGE, TRACES}`
- `_STORAGE_OPS`: `{ARCHIVE, EXPORT, RESTORE}`

Because `SkillsOp.STATUS` does not match any known opset in `_ComposedAggregate.execute()`, the dispatcher falls through to:
```python
return SkillsResult(
    ok=False,
    op=op,
    exit_code=2,
    message=f"Unknown skills op: {op}",
)
```
Even if routed to `_design` or `_observability`, neither `SkillsDesignAgent` nor `SkillsObservabilityAgent` implements `_execute_status`. CLI `sac status` also crashes with `[FAIL] Unknown skills op: status`.

#### C. Free-form Schema Permissiveness
In `modules/root_mcp_entry.py`, all 19 tools are declared with:
```json
{
  "type": "object",
  "properties": {},
  "additionalProperties": true
}
```
LLMs interacting with the MCP server lack guidance regarding tool parameter names (`query`, `skill`, `apply`, `category`, `days`, `target`), leading to malformed arguments and sub-optimal agent calls.

---

## 3. Goals & Non-Goals

### 3.1 Goals
1. **Accurate Rendering for Read-Only Tools:** Ensure `sac_list` renders the formatted skill table (matching CLI `_cmd_list` layout) and `sac_read` returns the verbatim markdown content of `SKILL.md`.
2. **First-Class Lifecycle Status & Type Alignment:** Align `SkillsTelemetry.curated_report()` with `ISkillsTelemetryProtocol.curated_report() -> tuple[TelemetryRow, ...]` (including the `name` field) and implement end-to-end `SkillsOp.STATUS` execution across orchestrators, CLI, and MCP surfaces.
3. **1:1 Presentation Equivalence:** Guarantee that both `sac` CLI and `skill-authoring-tools` MCP return identical information and human-readable text representations.
4. **Structured Tool Schemas:** Define explicit JSON Schema properties for all 19 MCP tools, documenting required and optional parameters with types and descriptions.
5. **Architectural Purity (AES Compliance):** Preserve strict layer separation (no surface imports into capability or domain logic; formatting stays within the presentation boundary or reuses shared pure formatters).

### 3.2 Non-Goals
1. **Changing Storage Sidecars:** No alterations to `.usage.json` or `.lifecycle_config.json` schema formats.
2. **Altering Execution Core:** No rewriting of the underlying BM25F discovery algorithms, AST linter rules, or atomic filesystem mutation primitives.
3. **Creating Secondary MCP Servers:** No additional servers; all functionality remains consolidated in `modules/root_mcp_entry.py` and `SkillsMcpAdapter`.
4. **Fixing Pre-Existing `scan_summary` Dataclass Bug:** `ObservabilityAgent._execute_phrases` (line 201) passes `scan_summary=scan_result` when constructing `SkillsResult`, but `scan_summary` is only a field on `ObservabilityResult` (`modules/shared/src/observability/taxonomy_observability_response.py:56`), not `SkillsResult`. This pre-existing bug affects only the unexposed `TRACES` operation and is documented here as out-of-scope known tech debt to avoid scope creep in this cycle.

---

## 4. Proposed Design

### 4.1 System Interaction Flow
The revised dispatch flow handles data extraction, lifecycle status resolution, and multi-field presentation:

```mermaid
sequenceDiagram
    autonumber
    actor Client as LLM / Agent / User
    participant Entry as modules/root_mcp_entry.py
    participant Adapter as SkillsMcpAdapter (surface_mcp_command.py)
    participant Aggregate as _ComposedAggregate (root_skills_container.py)
    participant Agent as Owning Agent (Discovery/Observability)
    participant Cap as Capability (Lister/Reader/Telemetry)

    Client->>Entry: call_tool("sac_list", {})
    Entry->>Adapter: execute_tool("sac_list", {})
    Adapter->>Aggregate: execute(SkillsRequest(op=LIST))
    Aggregate->>Agent: execute(DiscoveryRequest(verb=LIST))
    Agent->>Cap: list_skills(root)
    Cap--Agent: tuple[SkillRecord, ...]
    Agent-->>Aggregate: DiscoveryResponse(records=...)
    Aggregate-->>Adapter: SkillsResult(records=...)
    Note over Adapter: Adapter renders records table (SKILL + DESCRIPTION + count)
    Adapter-->>Entry: {"ok": true, "content": [{"type": "text", "text": "..."}]}
    Entry-->>Client: CallToolResult
```

### 4.2 Fix 1: Multi-Payload Rendering in `SkillsMcpAdapter`

`SkillsMcpAdapter.execute_tool()` must inspect all payload channels of `SkillsResult` instead of relying solely on `result.message`:

```mermaid
flowchart TD
    Start([Execute Tool Completed]) --> CheckOk{Is result.ok true?}
    CheckOk -- No --> ErrMsg{Has result.message?}
    ErrMsg -- Yes --> EmitMsg[Emit result.message]
    ErrMsg -- No --> EmitExit[Emit f'{op}: exit {exit_code}']
    
    CheckOk -- Yes --> CheckOp{Examine result.op}
    CheckOp -- READ --> CheckContent{result.content present?}
    CheckContent -- Yes --> EmitContent[Emit raw SKILL.md content]
    CheckContent -- No --> EmitReadErr[Emit 'Skill not found']
    
    CheckOp -- LIST --> CheckRecords{result.records present?}
    CheckRecords -- Yes --> FormatTable[Render clean 2-column table + summary]
    CheckRecords -- No --> FormatEmpty[Render 'No skills in the pack yet.']
    
    CheckOp -- STATUS --> FormatStatus[Render TelemetryRow lifecycle states]
    CheckOp -- USAGE --> FormatUsage[Render TelemetryRow usage rows]
    CheckOp -- Other Ops --> FallbackText[Emit result.message or exit string]
```

#### Shared Plain-Text Formatter
Because the CLI uses ANSI escape codes (`CYAN()`, `BOLD()`, `RESET()`), the MCP adapter must render a clean plain-text version without ANSI terminal escapes to ensure clean LLM tokenization.

```python
def _render_records_table(records: tuple[SkillRecord, ...]) -> str:
    """Render SkillRecord objects as a clean 2-column text table."""
    if not records:
        return "No skills in the pack yet.\nCreate one: sac create skill <name> --category <cat> --apply"
    
    col_width = 28
    lines = [
        "SKILL".ljust(col_width) + " " + "DESCRIPTION",
        "-" * col_width + " " + "-" * 60,
    ]
    truncated = False
    for r in records:
        desc = (r.description or "").replace("\n", " ").strip()
        if len(desc) > 70:
            desc = desc[:69] + "…"
            truncated = True
        lines.append(f"{r.name.ljust(col_width)} {desc}")
    
    if truncated:
        lines.append("Tip: sac read <name> for full content")
    lines.append(f"\n{len(records)} skills in the pack.")
    return "\n".join(lines)
```

For `sac_read`:
```python
def _render_read_content(result: SkillsResult, name: str) -> str:
    """Render raw SKILL.md content or standard not-found error."""
    if result.content is not None and str(result.content).strip():
        return str(result.content)
    return result.message or f"Skill not found: {name}"
```

### 4.3 Fix 2: Telemetry Alignment and Resolution for `sac_status`

#### Architectural Placement Decision
Status reports the lifecycle state (`active`, `stale`, `archived`, `pinned`) of each skill in the pack, derived from activity timestamps stored in `.usage.json`.

In our AES module topology:
1. `modules/maintenance/` owns *mutation* operations (running transitions, pausing, resuming, pruning, moving).
2. `modules/observability/` owns *inspection* operations over telemetry sidecars (reading ledger, curated usage reports, mining traces).
3. `ISkillsTelemetryProtocol` in `modules/shared/src/observability/contract_observability_protocol.py:120` defines `curated_report(root) -> tuple[TelemetryRow, ...]`.
4. However, the concrete `SkillsTelemetry.curated_report()` (`modules/observability/src/capabilities_skills_telemetry.py:74`) currently returns `list[dict]`, omitting the skill `name` from each entry because `name = skill_md.parent.name` is used as the sidecar lookup key but not attached to the emitted dictionary.
5. Consequently, `ObservabilityAgent._execute_usage` (`agent_observability_orchestrator.py:148`) assigns `records=report` (a `list[dict]`), violating both the protocol signature and `SkillsResult.records`.

**Decision:** `SkillsOp.STATUS` belongs to `_OBSERVABILITY_OPS` in `modules/root_skills_container.py`, delegating directly to `ObservabilityAgent`. We also align `SkillsTelemetry.curated_report()` with its protocol contract by returning `tuple[TelemetryRow, ...]` (with `name=skill_md.parent.name`).

#### Implementation Across Modules

1. **In `modules/observability/src/capabilities_skills_telemetry.py`:**
   Update `curated_report()` to return `tuple[TelemetryRow, ...]`, mapping each normalized sidecar record into a `TelemetryRow` with the skill's `name`:
   ```python
   def curated_report(self, root: SkillsRoot) -> tuple[TelemetryRow, ...]:
       skills_root = Path(root)
       path = pack_usage_path(skills_root)
       data = _read_sidecar(path)
       rows: list[TelemetryRow] = []
       for skill_md in iter_skill_mds(skills_root):
           name = skill_md.parent.name
           rec = _normalize(data.get(name, {})) if name in data else _baseline_record()
           rows.append(
               TelemetryRow(
                   name=name,
                   state=str(rec.get("state", DEFAULT_STATE)),
                   pinned=bool(rec.get("pinned", False)),
                   created_by=rec.get("created_by"),
                   created_at=rec.get("created_at"),
                   first_seen_at=rec.get("first_seen_at"),
                   last_activity_at=rec.get("last_activity_at"),
                   archived_at=rec.get("archived_at"),
                   views=int(rec.get("views", 0)),
                   uses=int(rec.get("uses", 0)),
                   activity_window_start=rec.get("activity_window_start"),
               )
           )
       rows.sort(key=lambda r: r.name)
       return tuple(rows)
   ```

2. **In `modules/observability/src/agent_observability_orchestrator.py`:**
   Update `_execute_usage()` to wrap `telemetry.curated_report(root)` in `tuple(report)` (since `SkillsResult.records` is declared as `tuple[SkillRecord | TelemetryRow, ...]`), and add `_execute_status()`:
   ```python
   def _execute_usage(self, request: SkillsRequest, op: SkillsOp) -> SkillsResult:
       """USAGE: bump/report per-skill telemetry sidecar."""
       telemetry = self._require(self._telemetry, "telemetry")
       root = self._root(request)
       verb = request.flags.get("verb", "report")
       skill = str(request.query or "")
       if verb == "seed":
           telemetry.seed_record_if_missing(skill, root)
           return SkillsResult(ok=True, op=op, message=f"seeded {skill}")
       if verb == "reanchor":
           telemetry.reanchor_clock(skill, root)
           return SkillsResult(ok=True, op=op, message=f"reanchored {skill}")
       report = telemetry.curated_report(root)
       return SkillsResult(ok=True, op=op, records=report, root=root)

   def _execute_status(self, request: SkillsRequest, op: SkillsOp) -> SkillsResult:
       """STATUS: inspect lifecycle state for all skills in the pack."""
       telemetry = self._require(self._telemetry, "telemetry")
       root = self._root(request)
       report = telemetry.curated_report(root)
       return SkillsResult(
           ok=True,
           op=op,
           exit_code=SkillsExitCode.CLEAN,
           records=report,
           root=root,
       )
   ```

3. **In `modules/root_skills_container.py`:**
   Add `SkillsOp.STATUS` to `_OBSERVABILITY_OPS`:
   ```python
   _OBSERVABILITY_OPS = frozenset({
       SkillsOp.LEDGER,
       SkillsOp.USAGE,
       SkillsOp.TRACES,
       SkillsOp.STATUS,
   })
   ```

4. **In `modules/shared/src/design/taxonomy_design_response.py`:**
   Update the type annotation on `SkillsResult.records` from `tuple[SkillRecord, ...]` to `tuple[SkillRecord | TelemetryRow, ...]` (with `TelemetryRow` imported under `TYPE_CHECKING`) so static type checkers (`mypy`) recognize `TelemetryRow` entries from observability without `list[dict]` type violations.

5. **In `modules/cli/src/surface_skills_command.py`:**
   Update `_render_status()` (lines 286–292) and `_render_usage()` (lines 295–301) to format `TelemetryRow` attributes cleanly:
   ```python
   def _render_status(result: SkillsResult) -> int:
       records = result.records or ()
       info(f"[OK] status — {len(records)} state row(s)")
       if records:
           for rec in records:
               name = getattr(rec, "name", "unknown")
               state = getattr(rec, "state", "active")
               pinned = " (pinned)" if getattr(rec, "pinned", False) else ""
               info(f"  {name}: {state}{pinned}")
       return 0
   ```

6. **In `modules/mcp/src/surface_mcp_command.py`:**
   Render `TelemetryRow` objects cleanly without dict fallback `"unknown"`:
   ```python
   def _render_status_records(self, records: tuple) -> str:
       lines = [f"[OK] status — {len(records)} state row(s)"]
       for rec in records:
           name = getattr(rec, "name", "unknown")
           state = getattr(rec, "state", "active")
           pinned = " (pinned)" if getattr(rec, "pinned", False) else ""
           lines.append(f"  {name}: {state}{pinned}")
       return "\n".join(lines)
   ```

### 4.4 Fix 3: Schema Definitions for All 19 MCP Tools

Instead of empty wildcard schemas (`{type: object, properties: {}, additionalProperties: True}`), each tool descriptor returned by `SkillsMcpAdapter.list_tools()` will include a typed `inputSchema` dictionary.

| Tool Name | Key Parameters | Schema Specification |
|---|---|---|
| `sac_list` | None | `{type: "object", properties: {}}` |
| `sac_read` | `skill` (string, required) | `{type: "object", properties: {"skill": {"type": "string", "description": "Skill name to read"}}, required: ["skill"]}` |
| `sac_status` | `query` (string, optional) | `{type: "object", properties: {"query": {"type": "string", "description": "Optional skill name filter"}}}` |
| `sac_usage` | `query` (string, optional), `verb` (string: report/seed/reanchor) | `{type: "object", properties: {"query": {"type": "string"}, "verb": {"type": "string", "enum": ["report", "seed", "reanchor"]}}}` |
| `sac_export` | `skill` (string, required) | `{type: "object", properties: {"skill": {"type": "string"}}, required: ["skill"]}` |
| `sac_lint` | `category` (string, optional) | `{type: "object", properties: {"category": {"type": "string", "description": "Filter lint scan by category"}}}` |
| `sac_catalog` | `check` (boolean, optional) | `{type: "object", properties: {"check": {"type": "boolean", "description": "Check if catalog.json is in sync"}}}` |
| `sac_discover` | `query` (string, required), `limit` (integer, optional) | `{type: "object", properties: {"query": {"type": "string"}, "limit": {"type": "integer", "default": 20}}, required: ["query"]}` |
| `sac_move` | `skill` (string, required), `target` (string, required), `apply` (boolean) | `{type: "object", properties: {"skill": {"type": "string"}, "target": {"type": "string"}, "apply": {"type": "boolean"}}, required: ["skill", "target"]}` |
| `sac_archive` | `skill` (string, required), `apply` (boolean) | `{type: "object", properties: {"skill": {"type": "string"}, "apply": {"type": "boolean"}}, required: ["skill"]}` |
| `sac_restore` | `skill` (string, required), `category` (string, optional), `apply` (boolean) | `{type: "object", properties: {"skill": {"type": "string"}, "category": {"type": "string"}, "apply": {"type": "boolean"}}, required: ["skill"]}` |
| `sac_create` | `skill` (string, required for `kind=skill`), `category` (string, required for `kind=skill`), `kind` (string: skill/category), `description` (string), `apply` (boolean) | `{type: "object", properties: {"skill": {"type": "string"}, "category": {"type": "string"}, "kind": {"type": "string", "enum": ["skill", "category"]}, "description": {"type": "string"}, "apply": {"type": "boolean"}}, required: ["skill", "category"]}` |
| `sac_run` | `apply` (boolean) | `{type: "object", properties: {"apply": {"type": "boolean", "description": "Execute state transitions"}}}` |
| `sac_pause` | None | `{type: "object", properties: {}}` |
| `sac_resume` | None | `{type: "object", properties: {}}` |
| `sac_pin` | `skill` (string, required) | `{type: "object", properties: {"skill": {"type": "string"}}, required: ["skill"]}` |
| `sac_unpin` | `skill` (string, required) | `{type: "object", properties: {"skill": {"type": "string"}}, required: ["skill"]}` |
| `sac_prune` | `days` (integer), `purge_days` (integer), `dry_run` (boolean) | `{type: "object", properties: {"days": {"type": "integer"}, "purge_days": {"type": "integer"}, "dry_run": {"type": "boolean"}}}` |
| `sac_ledger` | `action` (string), `skill` (string) | `{type: "object", properties: {"action": {"type": "string"}, "skill": {"type": "string"}}}` |

*(Note: `sac_create` uses `query` as the skill name when `kind="skill"` and as the category name when `kind="category"`, while `category` is the parent category folder required whenever `kind="skill"`. Both `"skill"` and `"category"` are listed in `required`.)*

In `SkillsMcpAdapter.list_tools()`, each returned descriptor embeds its `inputSchema`:
```python
    def list_tools(self) -> list[dict]:
        """Return MCP tool descriptors, one per sac verb (19 tools)."""
        return [
            {
                "name": "sac_read",
                "description": "Print a skill's SKILL.md",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "skill": {
                            "type": "string",
                            "description": "Skill name to read",
                        }
                    },
                    "required": ["skill"],
                },
            },
            # ... remaining 18 tool descriptors with their inputSchema ...
        ]
```

---

## 5. API & Interface Changes

### 5.1 `modules/mcp/src/surface_mcp_command.py`

#### Before:
```python
def execute_tool(self, name: str, arguments: dict) -> dict:
    tool_name = name.removeprefix("sac_")
    result = self._dispatch(tool_name, arguments)
    return {
        "ok": result.ok,
        "content": [
            {
                "type": "text",
                "text": result.message or f"{result.op}: exit {result.exit_code}",
            }
        ],
    }
```

#### After:
```python
def execute_tool(self, name: str, arguments: dict) -> dict:
    tool_name = name.removeprefix("sac_")
    result = self._dispatch(tool_name, arguments)
    rendered_text = self._render_tool_result(arguments, result)
    return {
        "ok": result.ok,
        "content": [
            {
                "type": "text",
                "text": rendered_text,
            }
        ],
    }

def _render_tool_result(self, args: dict, result: SkillsResult) -> str:
    if not result.ok:
        return result.message or f"{result.op}: exit {result.exit_code}"

    if result.op == SkillsOp.LIST:
        return self._render_list_records(result.records)
    if result.op == SkillsOp.READ:
        return self._render_read_content(result, args.get("skill", args.get("query", "")))
    if result.op == SkillsOp.STATUS:
        return self._render_status_records(result.records)
    if result.op == SkillsOp.USAGE:
        return self._render_usage_records(result.records)

    return result.message or f"{result.op}: exit {result.exit_code}"
```

### 5.2 `modules/root_mcp_entry.py`

#### Before:
```python
async def _call_tool(context, params) -> _CallToolResult:
    adapter = create_mcp_adapter()
    name = params.name
    args = params.arguments or {}
    result = adapter.execute_tool(name, args)
    text = result["content"][0]["text"] if result.get("content") else f"{result.get('op')}: exit {result.get('exit_code')}"
    return _CallToolResult(content=[_TextContent(type="text", text=text)])
```
*(No change needed in `_call_tool` because `adapter.execute_tool` already packages the text into `result["content"][0]["text"]`.)*

In `_list_tools`:
```python
# Pass through schema from adapter descriptor
input_schema = d.get("inputSchema") or {
    "type": "object",
    "properties": {},
    "additionalProperties": True,
}
```

---

## 6. Alternatives Considered

### Alternative 1: Modify `_execute_list` and `_execute_read` to Populate `result.message` Directly
*Description:* Have `SkillsDiscoveryAgent` format strings into `DiscoveryResponse.message` at the capability/agent level.  
*Pros:* Avoids special-case rendering logic in `SkillsMcpAdapter`.  
*Cons:* Violates AES separation of concerns. `SkillsResult.records` and `SkillsResult.content` are structured domain value objects designed for consumption by diverse presentation adapters (CLI, GUI, MCP, web). Stamping ANSI strings or pre-rendered plain text into `message` couples the domain agent to a specific presentation medium.  
*Decision:* **Rejected.** Formatting belongs strictly in surface adapters.

### Alternative 2: Return Raw JSON Dictionaries for All MCP Tools Instead of CLI Text
*Description:* Have MCP tools return `json.dumps()` of `result.records` or `result.content`.  
*Pros:* Highly structured for programmatic consumption by custom LLM pipelines.  
*Cons:* Breaks the explicit project goal of **1:1 CLI Equivalence**. The CLI prints a concise, human-readable table with skill descriptions and counts. LLM agents act as terminal operators and benefit from reading the same predictable format as human engineers.  
*Decision:* **Rejected.** Maintain 1:1 formatted text equivalence for standard text tools. Future structured MCP extensions can provide `_json` tools if required.

### Alternative 3: Remove `sac_status` Entirely and Rely Exclusively on `sac_usage`
*Description:* Eliminate `sac_status` from `list_tools()` and delete the CLI command mapping.  
*Pros:* Simplifies the verb registry since `sac usage` also inspects `.usage.json`.  
*Cons:* `sac status` is documented extensively in `README.md`, `PRD.md`, and operational procedures as the primary command for checking whether skills are `active`, `stale`, or `archived`. `sac usage` focuses on numerical telemetry (views, uses, activity windows). Removing `status` creates user confusion and breaks muscle memory.  
*Decision:* **Rejected.** Retain and fix `sac_status` by routing it to `ObservabilityAgent`.

---

## 7. Observability, Security & Rollout

### 7.1 Security Considerations
- **Containment Checks:** `sac_read` must never escape the skill pack directory root. Existing boundary enforcement in `SkillsReader` verifies that resolved paths reside strictly within `skills_root`.
- **Argument Sanitization:** All schema string properties are stripped of traversal patterns before path resolution.

### 7.2 Observability & Telemetry
- Views through `sac_read` continue to bump the view telemetry sidecar via `_observability.record_view(skill_name)` in `_ComposedAggregate.execute()`.
- MCP stdio logging remains directed to stderr (`sys.stderr`), preserving the stdout channel for clean JSON-RPC protocol transport.

### 7.3 Verification & Testing Plan
1. **Unit Tests (`modules/observability/tests/` and `modules/mcp/tests/`):**
   - In `modules/observability/tests/unit_observability.py`: Verify `SkillsTelemetry.curated_report()` returns `tuple[TelemetryRow, ...]` with `.name` populated for every skill.
   - In `modules/mcp/tests/unit_mcp_rendering.py`: Verify `execute_tool("sac_list", {})` outputs the two-column table and count line; `execute_tool("sac_read", {"skill": "arxiv"})` returns the exact text of `arxiv/SKILL.md`; `execute_tool("sac_status", {})` returns state rows with exit code 0; and unknown commands return structured error messages with exit code 2.
2. **Regression Testing:**
   - Execute `uv run pytest modules/*/tests` to ensure no regressions in existing unit/integration tests.
   - Run `lint-arwaky scan` to confirm zero AES architectural boundary violations.

---

## Open Questions

None. All technical choices—including aligning `SkillsTelemetry.curated_report()` to `tuple[TelemetryRow, ...]`, routing `SkillsOp.STATUS` through `ObservabilityAgent`, formatting table data in the MCP surface without ANSI escapes, and exposing explicit JSON schemas—are fully resolved by repository standards.

---

## Key Decisions

1. **Surface-Level Formatting:** `SkillsMcpAdapter` performs plain-text table formatting directly in `modules/mcp/src/surface_mcp_command.py` dispatching solely on `result.op`. The agent and capability layers continue returning clean, unrendered `SkillRecord` and `TelemetryRow` objects.
2. **Plain-Text (ANSI-Free) Output:** MCP output strips terminal color codes (`CYAN()`, `BOLD()`, `RESET()`) used by the CLI, avoiding LLM token bloat while maintaining identical tabular alignment and content layout.
3. **Telemetry Contract Alignment & Observability Ownership of Status:** `SkillsTelemetry.curated_report()` is aligned to return `tuple[TelemetryRow, ...]` (populating `name=skill_md.parent.name`), fixing the latent type mismatch and missing skill names in telemetry reports. `SkillsOp.STATUS` is assigned to `_OBSERVABILITY_OPS` in `modules/root_skills_container.py` and implemented via `_execute_status()` in `ObservabilityAgent`.
4. **Tool Parameter Schemas:** `SkillsMcpAdapter.list_tools()` will declare typed JSON schemas for all 19 verbs, providing clear parameter hints (`skill`, `category`, `apply`, `query`) to AI agents.

---

## PR Plan

### PR 1: Align `curated_report` to `TelemetryRow` and Wire `SkillsOp.STATUS`
- **Title:** `fix(observability): align curated_report to TelemetryRow and wire SkillsOp.STATUS`
- **Affected Files:**
  - `modules/root_skills_container.py`
  - `modules/shared/src/design/taxonomy_design_response.py`
  - `modules/observability/src/capabilities_skills_telemetry.py`
  - `modules/observability/src/agent_observability_orchestrator.py`
  - `modules/observability/tests/unit_observability.py`
  - `modules/cli/src/surface_skills_command.py`
- **Dependencies:** None
- **Description:** Updates `SkillsTelemetry.curated_report()` to construct and return `tuple[TelemetryRow, ...]` with `.name` populated for each skill, and updates `SkillsResult.records` annotation to `tuple[SkillRecord | TelemetryRow, ...]`. Adds `_execute_status()` in `ObservabilityAgent` and routes `SkillsOp.STATUS` through `_OBSERVABILITY_OPS` in `_ComposedAggregate`. Updates `_render_status` in the CLI to format `TelemetryRow` attributes cleanly. Adds unit tests verifying `curated_report()` type safety and `sac status` execution.

### PR 2: Multi-Payload Rendering in `SkillsMcpAdapter` for List, Read, and Status
- **Title:** `fix(mcp): render records and content in SkillsMcpAdapter for 1:1 CLI equivalence`
- **Affected Files:**
  - `modules/mcp/src/surface_mcp_command.py`
  - `modules/mcp/tests/unit_mcp_rendering.py`
- **Dependencies:** PR 1
- **Description:** Updates `SkillsMcpAdapter.execute_tool()` to dispatch solely on `result.op`, rendering `result.records` for `LIST`, `STATUS`, and `USAGE`, and `result.content` for `READ`. Implements ANSI-free plain-text formatters for the two-column skill table and `TelemetryRow` status rows. Adds `modules/mcp/tests/unit_mcp_rendering.py` to assert real rendered output for `sac_list`, `sac_read`, and `sac_status` using fake aggregates.

### PR 3: Comprehensive MCP Tool Input Schemas in Adapter and Entry Point
- **Title:** `feat(mcp): declare typed JSON inputSchema for all 19 sac MCP tools`
- **Affected Files:**
  - `modules/mcp/src/surface_mcp_command.py`
  - `modules/root_mcp_entry.py`
  - `modules/mcp/tests/unit_mcp_schema.py`
- **Dependencies:** PR 2
- **Description:** Populates explicit `inputSchema` definitions (properties, types, descriptions, and required arrays including `["skill", "category"]` for `sac_create`) across all 19 tool descriptors in `list_tools()`. Passes through `input_schema` in `modules/root_mcp_entry.py`. Adds unit tests in `modules/mcp/tests/unit_mcp_schema.py` verifying schema conformance and parameter validation.