---
name: blender-arwaky
description: "Blender asset search, GLB import/export, scene assembly, and rendering via MCP or CLI."
when-to-use: "Use when scripting Blender, placing GLB/assets, rendering frames, or managing Blender scenes via CLI or MCP execute_command."
argument-hint: "<init|launch|close|get-scene-info|create-primitive|set-object-transform|render|import-glb|export-model|place-asset|execute-blender-code|get-task-status|get-config|set-config|help> [--flag value]"
---

# BlenderArwaky

Script Blender through the BlenderArwaky toolkit via CLI sub-commands or the unified MCP execute_command surface for scene assembly, transformations, rendering, and asset placements.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Access functionality via direct CLI sub-commands or MCP `execute_command` routing with specific action names. | Verify CLI sub-command or MCP action name exists in supported command set. |
| R2 | Connect to Blender add-on TCP server on port 9876 with retry budget (30 retries x 2s). | Verify TCP listener is responsive on port 9876. |
| R3 | Ensure an active camera is present in the scene before taking viewport screenshots in headless mode. | Confirm scene contains an active camera object prior to screenshot capture. |
| R4 | Follow structured workflows for scene discovery, object manipulation, rendering, and custom bpy execution. | Check that output artifacts match expected JSON payloads or rendered frames. |
| R5 | Verify live connection via `health_check` before declaring operations complete. | Run health check and verify successful connection response. |

## Routing

| Step | Reference | Purpose |
| ---- | --------- | ------- |
| Commands | [`references/commands.md`](references/commands.md) | Every CLI sub-command and MCP action, with parameter tables, screenshot parameters, and the five MCP tools. |
| Workflows | [`references/workflows.md`](references/workflows.md) | Scene discovery, object creation/position, viewport analysis, asset import, render/status, custom code. |
| Add-on & Troubleshooting | [`references/troubleshooting.md`](references/troubleshooting.md) | Blender add-on architecture, port/timeout details, and fixes for the common failure modes. |
