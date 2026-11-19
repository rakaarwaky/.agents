---
name: notion
description: 'Notion API + ntn CLI: pages, databases, markdown, Workers.'
when-to-use: "Use when reading or writing Notion pages, databases, markdown, file uploads, or Workers via the ntn CLI or the Notion API (curl)."
argument-hint: "ntn api v1/search|ntn api v1/users|ntn api v1/pages <parent[page_id]> [properties...]|ntn api v1/pages/<id>/markdown|ntn api v1/pages/<id>/markdown -X PATCH|ntn api v1/blocks/<id>/children|ntn api v1/data_sources/<id>/query -X POST|ntn files create|ntn files list|ntn workers new|ntn workers deploy|ntn workers exec"
---

# Notion

Interact with Notion databases, pages, blocks, and Workers using the official `ntn` CLI or raw HTTP REST API endpoints.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Require integration token configured as `NOTION_API_KEY` for both CLI and HTTP execution paths. | Verify `NOTION_API_KEY` environment variable is defined. |
| R2 | Ensure target Notion pages and databases are shared with the integration to avoid 404 errors. | Test page access and confirm 404 errors are diagnosed as missing integration permissions. |
| R3 | Respect Notion API rate limits of approximately 3 requests per second with backoff and batching. | Check request throttling and retry logic on rate limit responses. |
| R4 | Use `-s` flag with curl commands and parse JSON responses with `jq` for clean automated parsing. | Verify curl commands include silent flag and format outputs cleanly. |

## Routing

| Step | Reference | Purpose |
| --- | --- | --- |
| Setup, `ntn` CLI commands, path choice, notes | [`references/ntn-cli.md`](references/ntn-cli.md) | Integration-token setup, `ntn` install, raw API shorthand, search/read/create/patch/query/upload command blocks, env vars, and the choosing-the-right-path table. |
| Cross-platform HTTP + curl fallback | [`references/http-path.md`](references/http-path.md) | Full curl command set for search, pages, blocks, data sources, properties, and file uploads — the default on Windows or when `ntn` is absent. |
| Common property formats + API versioning | [`references/property-types.md`](references/property-types.md) | Property type reference for building data sources. |
| Block types | [`references/block-types.md`](references/block-types.md) | Block type reference for reading/writing page content as blocks. |
| Notion-flavored markdown | [`references/flavored-markdown.md`](references/flavored-markdown.md) | Notion-flavored markdown blocks and inline tags used by the `/markdown` endpoints. |
| Notion Workers | [`references/workers.md`](references/workers.md) | Workers scaffold, webhook capability, and lifecycle commands. |
