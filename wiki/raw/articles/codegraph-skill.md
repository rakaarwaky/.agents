---
source_url: file:///home/raka/.agents/skills/code-quality/codegraph
ingested: 2026-11-18
sha256: 432cb68a7d420ae0539b98ef996d5c819b5ea2bb70f3b4693e6279b8d5abefa1
---

# codegraph skill — source capture

## SKILL.md

---
name: codegraph
description: "Inspect codebases: LOC, languages, ratios via pygount, plus symbol/call graphs and blast radius via CodeGraph."
when-to-use: "Repository LOC counts, language breakdowns, file counts, and code-vs-comment ratios (pygount — general 'how big is this repo' questions); or symbol lookup, callers/callees, cross-file impact, and test selection for a set of changed files (CodeGraph — use before grep/Read when asking 'what breaks if I change this')."
argument-hint: "[pygount] [--format=summary|json] [--suffix=<langs>] [--folders-to-skip=<globs>] [<path>]  |  [codegraph] <project-path>"
metadata:
  tags:
    - LOC
    - Code Analysis
    - pygount
    - Codebase
    - Metrics
    - Repository
    - symbols
    - call graph
    - impact
    - CodeGraph
  related_skills:
    - github-workflow
---

# Codebase Inspection

Two complementary lenses on a codebase, routed by the question.

## Global rules

- **Routing.** Pick the lens from the question, then read the matching reference end to end; the two tools answer different jobs — pygount counts lines by language, CodeGraph resolves symbols and the edges between them.
- **Order of operations.** Reach for CodeGraph **before** grep/Read, not after they fail: grep matches text, CodeGraph answers "what breaks if I change this", "which tests cover this file", "what calls this and how".
- **Completion.** The chosen reference was read in full and its commands executed against the target repo; results are interpreted with that reference's pitfalls and pseudo-language notes applied.

## Routing

| Question | Tool | Reference |
| --- | --- | --- |
| How big is this repo? Language mix? Code-vs-comment ratios? | `pygount` | [`references/pygount.md`](references/pygount.md) — prerequisites, summary commands, folder exclusions, language filters, output formats, result interpretation, pitfalls. |
| What calls this symbol? What breaks if I change it? Which tests cover it? | `CodeGraph` | [`references/codegraph.md`](references/codegraph.md) — MCP tool table, CLI direct-query syntax, "an index must exist first" notes. |

## references/pygount.md

# pygount — LOC Metrics

Analyze repositories for lines of code, language breakdown, file counts, and code-vs-comment ratios.

**Goal:** the reader can run a pygount summary over a target repo and interpret its output.

## When to Use

- User asks for LOC (lines of code) count
- User wants a language breakdown of a repo
- User asks about codebase size or composition
- User wants code-vs-comment ratios
- General "how big is this repo" questions

## Prerequisites

```bash
pip install --break-system-packages pygount 2>/dev/null || pip install pygount
```

## 1. Basic Summary (Most Common)

Get a full language breakdown with file counts, code lines, and comment lines:

```bash
cd /path/to/repo
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs,*.egg-info" \
  .
```

**IMPORTANT:** Always use `--folders-to-skip` to exclude dependency/build directories, otherwise
pygount will crawl them and take a very long time or hang.

## 2. Common Folder Exclusions

Adjust based on the project type:

```bash
# Python projects
--folders-to-skip=".git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs,.mypy_cache"

# JavaScript/TypeScript projects
--folders-to-skip=".git,node_modules,dist,build,.next,.cache,.turbo,coverage"

# General catch-all
--folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,vendor,third_party"
```

## 3. Filter by Specific Language

```bash
# Only count Python files
pygount --suffix=py --format=summary .

# Only count Python and YAML
pygount --suffix=py,yaml,yml --format=summary .
```

## 4. Detailed File-by-File Output

```bash
# Default format shows per-file breakdown
pygount --folders-to-skip=".git,node_modules,venv" .

# Sort by code lines (pipe through sort)
pygount --folders-to-skip=".git,node_modules,venv" . | sort -t$'\t' -k1 -nr | head -20
```

## 5. Output Formats

```bash
# Summary table (default recommendation)
pygount --format=summary .

# JSON output for programmatic use
pygount --format=json .

# Pipe-friendly: Language, file count, code, docs, empty, string
pygount --format=summary . 2>/dev/null
```

## 6. Interpreting Results

The summary table columns:

- **Language** — detected programming language
- **Files** — number of files of that language
- **Code** — lines of actual code (executable/declarative)
- **Comment** — lines that are comments or documentation
- **%** — percentage of total

Special pseudo-languages:

- `__empty__` — empty files
- `__binary__` — binary files (images, compiled, etc.)
- `__generated__` — auto-generated files (detected heuristically)
- `__duplicate__` — files with identical content
- `__unknown__` — unrecognized file types

## Pitfalls

1. **Always exclude .git, node_modules, venv** — without `--folders-to-skip`, pygount will crawl
   everything and may take minutes or hang on large dependency trees.
2. **Markdown shows 0 code lines** — pygount classifies all Markdown content as comments, not
   code. This is expected behavior.
3. **JSON files show low code counts** — pygount may count JSON lines conservatively. For
   accurate JSON line counts, use `wc -l` directly.
4. **Large monorepos** — for very large repos, consider using `--suffix` to target specific
   languages rather than scanning everything.

## Completion

- A summary table was produced for the target repo and interpreted with the pseudo-language and
  pitfalls notes applied.

## references/codegraph.md

# CodeGraph — Symbol & Call Graph

CodeGraph is a high-performance, Rust-powered codebase intelligence engine. It builds and
maintains a live graph of symbols, types, call hierarchies, and cross-file dependencies with zero
cloud dependencies. Reach for this **before** grep/Read, not after they fail.

## When to Use This Skill

- Exploring an unfamiliar codebase or a large multi-file architecture.
- Finding callers, callees, or references of a specific function or class.
- Resolving a symbol's declaration and signature across files.
- Checking cross-file blast radius before refactoring a shared interface.
- Picking which tests to run for a set of changed files.

Grep matches text; CodeGraph resolves symbols and the edges between them. The difference shows up
in the questions only it can answer — "what breaks if I change this", "which tests cover this
file", "what calls this and how".

## An Index Must Exist First

A project is queryable only after `codegraph init` has built `<project>/.codegraph/`. The MCP
server registers and starts fine with no index anywhere, so a dead-looking tool is usually a
missing index, not a broken wiring:

```bash
codegraph status <project-path>     # "⚠ Not initialized" ⇒ nothing to query from
```

- `init` is a write to the repository (creates untracked `.codegraph/`) — ask before running it
  in someone else's tree, and check whether `.gitignore` covers it.
- `sync` applies the delta since last index; the background daemon keeps indexes fresh, so don't
  re-index by hand mid-session.
- Indexing belongs to the orchestrator: `aa tool run codegraph <cmd>`.

## MCP Tools

The installed build (v1.6.0) exposes exactly these eight. Any other `codegraph_*` name is a
hallucinated tool and will fail.

| Tool | Purpose |
|---|---|
| `codegraph_explore` | **Primary.** One call returns the relevant symbols' line-numbered source, the call paths between them, and a blast-radius summary — replaces a grep+Read loop. |
| `codegraph_node` | A single symbol's source plus its caller/callee trail, or a file read with line numbers and its dependents. |
| `codegraph_search` | Symbol lookup by name/kind. |
| `codegraph_callers` | Who calls a symbol. |
| `codegraph_callees` | What a symbol calls. |
| `codegraph_impact` | What code is affected by changing a symbol. |
| `codegraph_files` | Project file structure from the index. |
| `codegraph_status` | Index presence and statistics — call this when a query comes back empty. |

**No default project:** this server may start somewhere without a `.codegraph/`. For any project
that isn't the session's working directory, pass its path as `projectPath`; the tool resolves the
nearest `.codegraph/` at or above it. A project with no index needs `codegraph init` run in it
first (the user's decision, not yours).

## CLI Direct Queries

Same outputs as MCP, useful for a quick check or when piping:

```bash
codegraph status                       # is there an index, and how big?
codegraph explore "how does the dispatcher route commands"
codegraph node <symbol>                # source + caller/callee trail
codegraph impact <symbol>              # blast radius of changing it
codegraph affected src/foo.py src/bar.py   # test files touched by these changes
codegraph files                        # indexed tree
codegraph ui                           # browse the graph in a browser
```

Each subcommand takes `--path` / `-p` for another project and `--help` for its own flags.
