---
name: llm-wiki
description: "Karpathy's LLM Wiki: build/query interlinked markdown KB."
when-to-use: Use when the user asks to create, build, or start a wiki, ingest a source into a wiki, ask a question about an existing wiki, or lint/audit/health-check a wiki.
argument-hint: "<init | ingest | query | lint> [wiki-path | source]"
---

# Karpathy's LLM Wiki

Build and maintain a persistent, compounding knowledge base of interlinked Markdown files following Karpathy's LLM Wiki architecture.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Orient session before any operation by reading `SCHEMA.md`, `index.md`, and recent `log.md` entries. | Verify orientation files are read before executing modifications. |
| R2 | Treat `raw/` directory contents as strictly immutable; record corrections in wiki articles rather than modifying sources. | Confirm no write operations target files in `raw/`. |
| R3 | Update navigational anchors `index.md` and `log.md` immediately following any page creation or modification. | Check git diff to ensure navigation files are updated alongside content. |
| R4 | Require every new page to link to at least 2 existing pages via `[[wikilinks]]`. | Validate incoming and outgoing links for all new concept pages. |
| R5 | Constrain taxonomy tags to those defined in `SCHEMA.md`; register new tags in the schema before applying them. | Audit page tags against schema allowed set. |
| R6 | Handle contradicting information explicitly with dates and citations instead of silently overwriting earlier facts. | Verify contradictory claims are documented and flagged for user review. |
| R7 | Seek user confirmation before executing bulk updates that touch 10 or more existing pages. | Confirm approval prompt is issued for large ingest operations. |
| R8 | The wiki location is hardcoded to `/home/raka/.agents/wiki`. Never use `$WIKI_PATH` env vars, `~/wiki` defaults, or any other path. | Confirm all file operations target `/home/raka/.agents/wiki`. |

## Routing

| Step | Reference | Purpose |
| ---- | --------- | ------- |
| Orient (every session) | [`references/resuming-wiki.md`](references/resuming-wiki.md) | Read `SCHEMA.md` + `index.md` + recent `log.md`; do this before ingesting, querying, or linting. |
| Init new wiki | [`references/schema-templates.md`](references/schema-templates.md) | Wiki location is hardcoded to `/home/raka/.agents/wiki` — write initial structure, schema, index, and log there. |
| Ingest | [`references/ingest.md`](references/ingest.md) | Capture raw source, extract takeaways, write/update pages, update navigation. |
| Query | [`references/query.md`](references/query.md) | Search key terms, read relevant pages, synthesize answers, update query logs. |
| Lint | [`references/lint-checklist.md`](references/lint-checklist.md) | 13-point health checklist: orphans, broken links, frontmatter, log rotation. |
| Working with the wiki | [`references/working-with-wiki.md`](references/working-with-wiki.md) | Searching, bulk ingest, archiving, Obsidian integration, headless setup. |
| Obsidian headless | [`references/obsidian-headless.md`](references/obsidian-headless.md) | Headless vault synchronization without requiring desktop GUI. |
