---
name: fetch-mcp
description: Scrapes web to markdown with transcripts. Use when extracting articles, HTML, YouTube text, or reformatting YouTube content into chapters, threads, blog posts, or quotes.
when-to-use: Use when reading content from external web pages, blogs, or documentation URLs; converting noisy pages to clean Markdown articles; fetching structured JSON from REST API endpoints; extracting captions/transcripts from YouTube videos; or reformatting YouTube content into chapters, threads, blog posts, or quotes.
argument-hint: "mcp-fetch <command> <url> [--max-length N] [--start-index N] [--proxy <URL>] [--lang <code>]"
---

# Fetch MCP Server

Specialized web extraction and content scraping server converting URLs into clean, token-efficient formats such as Markdown, plain text, extracted articles, and video transcripts.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Prefer `fetch_readable` for article content to strip ads and boilerplates via Mozilla Readability. | Inspect extraction command to confirm readable mode is selected for articles. |
| R2 | Maintain default `max_length` of 5000 characters unless explicitly required, using pagination offsets for larger pages. | Check request parameters for bounded character budgets. |
| R3 | Extract YouTube transcripts via `fetch_youtube_transcript` defaulting to English (`lang="en"`). | Confirm transcript command specifies valid language codes. |
| R4 | Support CLI and MCP access paths interchangeably with identical core parameter behaviors. | Verify parameters map correctly across CLI flags and MCP tool schemas. |

## Routing

| Step | Reference | Purpose |
| ---- | --------- | ------- |
| Tools | [`references/tools.md`](references/tools.md) | Per-tool parameters and CLI examples for all six fetch commands (`html`, `markdown`, `readable`, `txt`, `json`, `youtube`). |
| Script | [`scripts/fetch_transcript.py`](scripts/fetch_transcript.py) | Python helper that extracts a YouTube transcript and outputs structured JSON (segments, full text, timestamped text). |
| Output formats | [`references/output-formats.md`](references/output-formats.md) | Example output formats: chapters, summaries, chapter summaries, threads, blog posts, and quotes. |
