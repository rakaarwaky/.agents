---
name: context7-cli
description: Operates the ctx7 CLI and Context7 MCP registry — resolve a library ID, then query its docs (doc lookup / find-docs), skills install/search/suggest/list/remove/generate, and MCP setup. Use when mentioning ctx7 or context7, looking up API docs or library docs for a library or framework, finding docs via ctx7, installing skills, or configuring Context7 MCP for an editor.
when-to-use: Use when the user mentions ctx7, context7, or find-docs; asks to look up API docs or library docs for a library or framework; wants docs via MCP (context7__resolve-library-id / context7__query-docs) or the ctx7 CLI; wants to install, search, suggest, list, remove, or generate skills; or needs Context7 MCP set up for Claude Code, Cursor, OpenCode, or a project.
argument-hint: "ctx7 library <name> [query] | ctx7 docs <libraryId> <query> | ctx7 skills install|search|suggest|list|remove|info <args> | ctx7 setup [--mcp|--cli] | ctx7 login|logout|whoami | ctx7 upgrade"
---

# ctx7 CLI

Context7 CLI and MCP interface for querying up-to-date framework documentation, managing community skills, and configuring MCP editor integrations.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Keep CLI up to date by invoking via latest npm package or npx runner. | Verify CLI version compatibility before executing documentation lookups. |
| R2 | Require leading slash in library identifiers (e.g. `/facebook/react`); resolve ID via `ctx7 library` before running `ctx7 docs`. | Validate library ID format prior to documentation queries. |
| R3 | Enforce `/owner/repo` syntax for skills repository installation commands. | Check skill installation argument format. |
| R4 | Use non-interactive token authentication via `CONTEXT7_API_KEY` for automated operations. | Verify API key environment variable is utilized to bypass interactive prompts. |

## Routing

| Step | Reference | Purpose |
| ---- | --------- | ------- |
| Doc lookup workflow | [`references/find-docs.md`](references/find-docs.md) | Resolve a library ID, then query its docs — two transports (MCP tools or CLI). |
| `ctx7 library` / `ctx7 docs` | [`references/docs.md`](references/docs.md) | Command reference. Use when writing code, verifying API signatures, or when training data may be outdated. |
| Skills management | [`references/skills.md`](references/skills.md) | `ctx7 skills install /owner/repo`, `search <keywords>`, `suggest`, `list`, `remove <name>`, `generate` (login required). |
| MCP setup | [`references/setup.md`](references/setup.md) | `ctx7 setup` — configure Context7 MCP for Claude Code / Cursor / OpenCode. |
