---
title: CodeGraph — symbol & call graph engine
created: 2026-11-18
updated: 2026-11-18
type: concept
tags: [CodeGraph, symbols, call-graph, impact, blast-radius, repository]
sources: [raw/articles/codegraph-skill.md]
confidence: high
---

# CodeGraph — symbol & call graph engine

CodeGraph is a Rust-powered codebase intelligence engine. It builds and
maintains a live graph of symbols, types, call hierarchies, and cross-file
dependencies with zero cloud dependencies. Its value is answering questions
grep cannot: "what breaks if I change this", "which tests cover this file",
"what calls this and how".

## Index must exist first

A project is queryable only after `codegraph init` builds
`<project>/.codegraph/`. The MCP server registers and starts fine with no
index anywhere, so a dead-looking tool usually means a missing index, not
broken wiring. Check with `codegraph status <path>` — "⚠ Not initialized"
means there is nothing to query yet. Running `init` writes to the repo
(creates untracked `.codegraph/`); ask before running it in someone else's
tree and check whether `.gitignore` covers it. `sync` applies the delta since
the last index; the background daemon keeps indexes fresh, so don't re-index
by hand mid-session.

## MCP tools (v1.6.0 — exactly eight)

| Tool | Purpose |
|---|---|
| `codegraph_explore` | Primary — line-numbered source + call paths + blast-radius in one call |
| `codegraph_node` | A symbol's source plus caller/callee trail, or a file read with dependents |
| `codegraph_search` | Symbol lookup by name/kind |
| `codegraph_callers` | Who calls a symbol |
| `codegraph_callees` | What a symbol calls |
| `codegraph_impact` | What code is affected by changing a symbol |
| `codegraph_files` | Project file structure from the index |
| `codegraph_status` | Index presence and statistics |

Any other `codegraph_*` name is a hallucinated tool and will fail.

## CLI direct queries

The CLI mirrors the MCP outputs for quick checks and piping:

```bash
codegraph status                       # index present? how big?
codegraph explore "how does the dispatcher route commands"
codegraph node <symbol>                # source + caller/callee trail
codegraph impact <symbol>              # blast radius of changing it
codegraph affected src/foo.py src/bar.py   # test files touched by changes
codegraph files                        # indexed tree
codegraph ui                           # browse the graph in a browser
```

Each subcommand takes `--path`/`-p` for another project and `--help` for its
own flags. The CLI also exposes `query`, `context`, `callers`, `callees`,
`daemon`, `unlock`, `uninit`, `index`, and `sync` beyond the MCP set.

## Related

- [[codebase-inspection-routing]] — when to reach for CodeGraph vs pygount
- [[codegraph-skill-architecture]] — where this sits in the skill
- [[pygount]] — the LOC-metrics companion lens