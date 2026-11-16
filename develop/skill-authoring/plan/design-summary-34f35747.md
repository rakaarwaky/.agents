# Design Summary: Fixing Skill-Authoring MCP Adapter & Lifecycle Operations

**Reference Design Document:** `/home/raka/.agents/develop/skill-authoring/plan/design-doc-34f35747.md`  
**Date:** 2026-11-17  
**Status:** Draft  

---

## Executive Summary

The `skill-authoring-tools` MCP server currently exposes 20 tools (`sac_*`) wrapping the `sac` CLI, but `sac_list` and `sac_read` return uninformative exit stubs (`"list: exit 0"` and `"read: exit 0"`), while `sac_status` crashes with an unknown subcommand error across both MCP and CLI entry points.

This design document establishes the architectural fixes to:
1. **Render Rich Payloads in `SkillsMcpAdapter`:** Inspect `result.records` (for `LIST`, `STATUS`, `USAGE`) and `result.content` (for `READ`), rendering them into clean plain-text representations that achieve 1:1 parity with CLI commands.
2. **Wire `SkillsOp.STATUS` into Observability:** Route `SkillsOp.STATUS` to `SkillsObservabilityAgent._execute_status()` in the composition root (`modules/root_skills_container.py`), fetching per-skill lifecycle states via `SkillsTelemetry.curated_report()`.
3. **Equip Tools with Typed JSON Schemas:** Upgrade the MCP tool registry from empty wildcards to typed schemas defining parameters such as `skill`, `category`, `apply`, `query`, and `target`.

---

## Root Cause Analysis

- **List & Read Payloads:** `SkillsResult` isolates tabular records in `result.records` and file contents in `result.content`, leaving `result.message` empty on success. `SkillsMcpAdapter.execute_tool()` previously evaluated `result.message or f"{result.op}: exit {result.exit_code}"`, falling back to bare exit strings.
- **Status Op Disconnection:** `SkillsOp.STATUS` was mapped in `SkillsMcpAdapter._op_from_tool` and `surface_skills_command.py`, but omitted from `_ComposedAggregate.execute()` routing sets and unhandled by any orchestrator.

---

## Architectural Decisions

1. **Surface-Level Text Rendering:** Table and content formatting is kept in the presentation layer (`modules/mcp/src/surface_mcp_command.py`) without polluting domain VOs or capability layers with pre-rendered strings.
2. **Plain-Text Without ANSI Escapes:** MCP output strips CLI terminal escape codes (`CYAN`, `BOLD`, `RESET`) to optimize readability and LLM token efficiency.
3. **Observability Owns Status:** Status inspection is assigned to `_OBSERVABILITY_OPS` and handled by `SkillsObservabilityAgent`, resolving both the MCP `sac_status` tool and the CLI `sac status` command simultaneously.
4. **Parameter Schema Publication:** All 20 tools in `SkillsMcpAdapter.list_tools()` will declare typed JSON schemas passed to MCP clients by `modules/root_mcp_entry.py`.

---

## Implementation Roadmap (PR Plan)

1. **PR 1: `fix(lifecycle): wire SkillsOp.STATUS to observability aggregate and implement status handler`**
   - Routes `SkillsOp.STATUS` to `_OBSERVABILITY_OPS` in `modules/root_skills_container.py`.
   - Implements `_execute_status()` in `modules/observability/src/agent_observability_orchestrator.py`.
   - Fixes `sac status` in CLI and aggregate.
2. **PR 2: `fix(mcp): render records and content in SkillsMcpAdapter for 1:1 CLI equivalence`**
   - Updates `execute_tool()` in `modules/mcp/src/surface_mcp_command.py` to format `records` into tables and output `content` directly.
   - Adds unit tests in `modules/observability/tests/unit_observability.py`.
3. **PR 3: `feat(mcp): declare typed JSON inputSchema for all 20 sac MCP tools`**
   - Populates typed parameter schemas for all tool descriptors in `list_tools()`.
   - Passes schemas through `modules/root_mcp_entry.py`.
