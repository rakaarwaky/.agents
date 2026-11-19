# Wiki Schema

## Domain
General knowledge base — interlinked markdown notes.

## Conventions
- File names: lowercase, hyphens, no spaces (e.g., `transformer-architecture.md`)
- Every wiki page starts with YAML frontmatter
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating a page, always bump the `updated` date
- Every new page must be added to `index.md` under the correct section
- Every action must be appended to `log.md`
- Provenance markers: on pages synthesizing 3+ sources, append `^[raw/articles/source-file.md]` at the end of paragraphs whose claims come from a specific source

## Frontmatter
```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [taxonomy tags]
sources: [raw/articles/source-name.md]
confidence: high | medium | low
contested: true
contradictions: [other-page-slug]
---
```

## Tag Taxonomy

Every tag used on a page must appear below. Add a new tag here before using it.

- Tools: pygount, CodeGraph, cli, pygount
- Code analysis: symbols, call-graph, impact, blast-radius, metrics, LOC, codebase
- Meta: comparison, routing, repository, skill-usage

## Page Thresholds

- **Create a page** when an entity/concept appears in 2+ sources OR is central to one source
- **Add to existing page** when a source mentions something already covered
- **DON'T create a page** for passing mentions, minor details, or things outside the domain
- **Split a page** when it exceeds ~200 lines — break into sub-topics with cross-links
- **Archive a page** when its content is fully superseded — move to `_archive/`, remove from index

## raw/ Frontmatter
Raw files in `raw/` are immutable — read-only. Corrections go in wiki pages, not in `raw/`.

## Directory Layout
- `SCHEMA.md` — this file
- `index.md` — navigational backbone, list of all pages
- `log.md` — action log
- `raw/` — immutable source material
- `_archive/` — retired pages
- `_meta/` — wiki metadata
