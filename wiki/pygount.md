---
title: pygount — LOC metrics tool
created: 2026-11-18
updated: 2026-11-18
type: concept
tags: [pygount, metrics, LOC, codebase, repository]
sources: [raw/articles/codegraph-skill.md]
confidence: high
---

# pygount — LOC metrics tool

pygount counts lines of code by language and reports code-vs-comment
ratios. Reach for it on "how big is this repo" questions: language mix, file
counts, and composition.

## Install

```bash
pip install --break-system-packages pygount 2>/dev/null || pip install pygount
```

## Basic summary (most common)

```bash
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs,*.egg-info" \
  .
```

**Always** pass `--folders-to-skip` — without it pygount crawls dependency
and build trees and can take minutes or hang on large projects. Tailor the
exclusion list by project type:

```bash
# Python
--folders-to-skip=".git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs,.mypy_cache"
# JS/TS
--folders-to-skip=".git,node_modules,dist,build,.next,.cache,.turbo,coverage"
```

## Other forms

```bash
pygount --suffix=py --format=summary .              # filter by language
pygount --format=json .                             # programmatic output
pygount --folders-to-skip=".git,node_modules,venv" .   # per-file breakdown
```

## Interpreting the summary

Columns: **Language**, **Files**, **Code**, **Comment**, **%**. Watch for
pseudo-languages: `__empty__`, `__binary__`, `__generated__`, `__duplicate__`,
`__unknown__`.

## Pitfalls

1. Exclude `.git`, `node_modules`, `venv` — otherwise long scans or hangs.
2. Markdown shows 0 code lines — all Markdown is classified as comments, not
   code. This is expected.
3. JSON files show conservatively low code counts — use `wc -l` for exact
   JSON line counts.
4. For large monorepos, target specific languages with `--suffix` rather than
   scanning everything.

## Related

- [[codebase-inspection-routing]] — when to reach for pygount vs CodeGraph
- [[codegraph]] — the symbol/call-graph companion lens
- [[codegraph-skill-architecture]] — where this sits in the skill