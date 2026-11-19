---
name: arxiv
description: Search arXiv papers by keyword, author, category, or ID.
when-to-use: Use when the user asks to search arXiv papers by keyword, author, category, or ID, or to fetch a paper's metadata, abstract, or PDF.
argument-hint: "[\"QUERY\"] [--author NAME | --category CAT | --id ID] [--max N] [--sort relevance|date|updated]"
---

# arXiv Research

Search and retrieve academic research papers from the arXiv REST API, parse Atom XML metadata, generate BibTeX citations, and extract paper contents.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Generate structured BibTeX entries following metadata retrieval for cited papers. | Verify BibTeX citation block matches fetched paper details. |
| R2 | Preserve explicit version suffixes (e.g. `v1`, `v2`) in URLs and citations to prevent citation drift. | Inspect generated citation links to confirm version preservation. |
| R3 | Check summary text for withdrawal notices before treating query results as valid papers. | Verify paper abstract does not indicate withdrawal or retraction. |
| R4 | Use stdlib Python scripts or raw curl requests without adding external API dependencies. | Confirm requests execute using standard system tools. |

## Routing

| Step | Reference | Purpose |
| ---- | --------- | ------- |
| Search | `scripts/search_arxiv.py` | Handles XML parsing; no dependencies (stdlib only). |
| Raw API (no script) | [`references/search-arxiv.md`](references/search-arxiv.md) | Full search syntax, boolean operators, sorting/pagination parameters, ready-to-paste parsing snippets. |
| Fetch by ID | `curl -s "https://export.arxiv.org/api/query?id_list=2402.03300"` | Direct API access. |
| Read content | `web_extract(urls=["https://arxiv.org/abs/ID"])` | Abstract extraction and full paper parsing. |
| BibTeX | [`references/bibtex.md`](references/bibtex.md) | Generate a BibTeX entry from fetched metadata. |
| Categories | [`references/common-categories.md`](references/common-categories.md) | Quick-reference table of common arXiv category codes and their fields. |
| Semantic Scholar | [`references/semantic-scholar.md`](references/semantic-scholar.md) | Assess impact / citations / related work via the Semantic Scholar API. |
| OCR / scanned pages | [`references/ocr-extraction.md`](references/ocr-extraction.md) | Local PDF processing and OCR fallback for scanned papers. |
