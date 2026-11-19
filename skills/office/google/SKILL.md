---
name: google
description: 'Daily Google ops via workspace MCP: Gmail, Drive, Calendar, Docs, Sheets, Slides, Forms, Tasks, Contacts, Chat. For user tasks.'
when-to-use: "Use when performing daily Google Workspace operations — Gmail, Drive, Calendar, Docs, Sheets, Slides, Forms, Tasks, Contacts, or Chat — via the workspace MCP server."
argument-hint: "search_gmail_messages <query>|get_gmail_message_content <message_id>|send_gmail_message|manage_event|read_sheet_values|modify_sheet_values|create_doc|modify_doc_text|create_drive_file|list_drive_items|get_events|query_freebusy|start_google_auth"
---

# Google Workspace -- Tool Router

Coordinate Google Workspace tools across Gmail, Drive, Calendar, Docs, Sheets, Slides, Forms, and Chat via MCP server integrations and command line utilities.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Obtain explicit confirmation before mutating events, sending emails, sharing files, or editing spreadsheets. | Verify approval before executing write actions across Workspace APIs. |
| R2 | Read back mutated objects following updates to verify provider-confirmed IDs, links, and content changes. | Confirm returned resource ID matches expected updated object. |
| R3 | Verify OAuth authentication before calling tools; resolve credential failures using setup references rather than blind retries. | Test auth status and halt retries on authentication rejections. |
| R4 | Handle pagination tokens completely on calendar listings, event retrievals, and drive search results. | Verify all pages are fetched before declaring search or listing complete. |
| R5 | Never invent tool names or undocumented parameters; use consolidated `manage_*` action schemas. | Validate tool names and arguments against official service schemas. |
| R6 | Construct formatted documents incrementally, inserting headers and styling before adding paragraph content. | Verify document build sequence follows incremental styling order. |

## Routing

| Step | Reference | Purpose |
| --- | --- | --- |
| Server registration, tool naming, CLI usage | [`references/execution-mode.md`](references/execution-mode.md) | `workspace` server naming, `mcp__workspace__` prefix, `workspace-cli` headless path. |
| First-time OAuth setup | [`references/setup.md`](references/setup.md) | OAuth credential creation, client-secret placement, and authentication. |
| Task-to-tool index | [`references/tool-reference.md`](references/tool-reference.md) | Full tool-to-task mapping across every service. |
| Per-service parameter tables | [`references/gmail.md`](references/gmail.md), [`references/drive.md`](references/drive.md), [`references/calendar.md`](references/calendar.md), [`references/docs.md`](references/docs.md), [`references/sheets.md`](references/sheets.md), [`references/slides.md`](references/slides.md), [`references/forms.md`](references/forms.md), [`references/tasks.md`](references/tasks.md), [`references/contacts.md`](references/contacts.md), [`references/chat.md`](references/chat.md), [`references/apps-script.md`](references/apps-script.md), [`references/search.md`](references/search.md) | Full parameter reference per service — read the matching file before calling a service's tools. |
| Gmail query operators | [`references/gmail-search-syntax.md`](references/gmail-search-syntax.md) | `is:unread`, `newer_than:7d`, `has:attachment`, and ready-made query patterns. |
| Common workflows | [`references/workflows.md`](references/workflows.md) | Daily brief, reply, find+share, sheet read/update, formatted doc, attachments, doc editing. |
| Reproduced failure modes | [`references/pitfalls.md`](references/pitfalls.md) | Recurring-event 400s, the 3-rejection pause, calendar 404s, real credential paths. Read before debugging an error. |
| Start-of-day brief | [`references/daily-brief.md`](references/daily-brief.md) | Day window, events, conflicts, meeting prep, urgent mail, follow-ups owed. |
| Docs build order | [`references/docs-layout.md`](references/docs-layout.md) | Incremental Google Docs build order that avoids style cascade, index shifting, and table-cell corruption. |
| Server options | [`references/server-options.md`](references/server-options.md) | Transports, auth modes, tool filtering/tiers, deployment, and credential-loading priority. |
