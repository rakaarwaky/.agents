---
title: codegraph skill architecture
created: 2026-11-18
updated: 2026-11-18
type: summary
tags: [CodeGraph, pygount, metrics, symbols, routing, repository]
sources: [raw/articles/codegraph-skill.md]
confidence: high
---

# codegraph skill architecture

The `codegraph` skill (`skills/code-quality/codegraph/`) is a thin router over
two codebase-inspection lenses. Its `SKILL.md` defines the routing and global
rules; two reference files carry the per-tool detail.

## Structure

```text
codegraph/
├── SKILL.md                 # routing + global rules
└── references/
    ├── pygount.md           # LOC metrics: install, commands, interpretation, pitfalls
    └── codegraph.md         # symbol/call graph: index, MCP tools, CLI queries
```

## Global rules from SKILL.md

- **Routing** — pick the lens from the question, then read the matching
  reference end to end. The two tools answer different jobs.
- **Order of operations** — reach for CodeGraph before grep/Read, not after
  they fail.
- **Completion** — the chosen reference was read in full and its commands
  executed against the target repo, with the reference's pitfalls applied.

## Frontmatter signals

`when-to-use` distinguishes pygount (LOC counts, language breakdowns,
code-vs-comment ratios) from CodeGraph (symbol lookup, callers/callees,
cross-file impact, test selection). `related_skills: [github-workflow]`.

## Related

- [[codebase-inspection-routing]] — the routing table in detail
- [[codegraph]] — the symbol/call-graph lens
- [[pygount]] — the LOC-metrics lens