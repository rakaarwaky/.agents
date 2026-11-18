---
title: Codebase Inspection Routing — pygount vs CodeGraph
created: 2026-11-18
updated: 2026-11-18
type: comparison
tags: [comparison, routing, codebase, metrics, symbols]
sources: [raw/articles/codegraph-skill.md]
confidence: high
---

# Codebase Inspection Routing — pygount vs CodeGraph

The `codegraph` skill bundles two complementary lenses on a codebase. They
answer different jobs, so the first decision is which question the user is
really asking.

## Routing table

| Question | Tool | Reference |
|---|---|---|
| How big is this repo? Language mix? Code-vs-comment ratios? | `pygount` | `references/pygount.md` |
| What calls this symbol? What breaks if I change it? Which tests cover it? | `CodeGraph` | `references/codegraph.md` |

## Key difference

Grep matches text; CodeGraph resolves symbols and the edges between them.
The distinction shows up only in the questions each can answer — "what breaks
if I change this", "which tests cover this file", "what calls this and how"
are CodeGraph questions, while LOC counts and language breakdowns are pygount
questions.

## Order of operations

Reach for CodeGraph **before** grep/Read, not after they fail. CodeGraph is
a pre-built search index, so one `codegraph_explore` call returns verbatim
source plus the call paths and blast radius that a grep+read loop would take
dozens of round-trips to reconstruct.

## Related

- [[codegraph]] — symbol/call-graph engine details
- [[pygount]] — LOC metrics engine details
- [[codegraph-skill-architecture]] — how the skill is structured