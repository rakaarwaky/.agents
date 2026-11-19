---
name: vision-arwaky
description: "Unified image and video intelligence for computer vision, OCR, video analysis, object tracking, and MCP integrations."
when-to-use: "Use when the user needs computer vision — image analysis, OCR, screenshot comparison, video info/frame extraction, scene/motion detection, object tracking, or smart-video understanding via CLI or MCP."
argument-hint: "<init|analyze|ocr|compare|video-info|extract-frames|check-corruption|detect-scenes|detect-motion|track|analyze-video> [--image PATH|--image1 PATH|--image2 PATH|--video PATH|--prompt TEXT|--lang CODE|--bbox X,Y,W,H]"
---

# Vision Arwaky

Python computer vision toolkit providing image analysis, optical character recognition, video processing, scene detection, and object tracking via CLI, MCP, and TUI interfaces.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Access capabilities via CLI (`va`), MCP server (`vision-arwaky-mcp`), or TUI config interface (`vision-arwaky-tui`). | Verify command invocation uses recognized entry point. |
| R2 | Route MCP commands through the six standard tools (`vision_init`, `vision_execute`, `vision_list_commands`, `vision_help`, `vision_status`, `vision_cancel`). | Check MCP request targets valid registered tool names. |
| R3 | Use external OpenAI-compatible endpoint for VLM analysis with deterministic fallback when endpoint is unavailable. | Test endpoint reachability or confirm deterministic fallback response. |
| R4 | Require system dependencies (`tesseract-ocr`, `ffmpeg`, `libgl1`) for OCR and video processing pipelines. | Verify dependency binaries exist in system path before running tasks. |
| R5 | Store credentials and caches in compliant XDG directories (`$XDG_CONFIG_HOME`, `$XDG_STATE_HOME`, `$XDG_CACHE_HOME`). | Confirm no secrets or temp files escape XDG standard paths. |
| R6 | Return structured JSON or target media files and verify operation status before completing. | Inspect output artifacts for valid JSON structure or expected file outputs. |

## Routing

| Step | Reference | Purpose |
| ---- | --------- | ------- |
| CLI (workspace) | run `va init [target_dir]` | Initialize workspace with XDG symlinks and skill definitions |
| CLI (image) | `analyze`, `ocr`, `compare` | Image analysis, OCR extraction, and screenshot diffing |
| CLI (video) | `video-info`, `extract-frames`, `check-corruption`, `detect-scenes`, `detect-motion`, `track` | Video metadata, frame extraction, scene events, and tracking |
| Smart video | `analyze-video` | Sampling algorithms and bounded VLM video summarization |
| Documentation map | `internal/vision-arwaky/` | Full product architecture, PRD, and module FRDs |
