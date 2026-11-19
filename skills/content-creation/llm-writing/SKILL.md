---
name: llm-writing
description: "Create or improve docs: minimum tokens, exact names, zero AI slop. Use for new docs (--create) or editing existing text (--improve)."
when-to-use: "Use ONLY for concise document creation (--create) or for improving existing text (--improve)."
argument-hint: "[--create|--improve] <path>"
---

# LLM-Optimized Writing

Create or shorten documentation with minimum tokens, exact symbol names, and zero AI slop across authoring and improvement workflows.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Maintain one owner per fact across the document set. | Verify no duplicated facts across sections. |
| R2 | Write action-only sentences without introductory or narrative filler. | Check sentences begin with active imperative verbs. |
| R3 | Use exact entity names or explicitly state `UNKNOWN`. | Verify all referenced identifiers match actual symbol names. |
| R4 | Backtick control keywords and log `CONFLICT:` when contradictions appear. | Inspect text for backticked keywords and conflict flags. |
| R5 | Introduce no new ungrounded facts during text rewrites. | Verify semantic equivalence against source text. |
| R6 | Preserve user voice without over-sterilizing tone. | Confirm unique stylistic attributes remain intact. |
| R7 | Emit concise completion report (under 10 lines) after diffing keep-sets. | Check output report length and keep-set diff verification. |

## Routing

| File | Purpose |
|------|---------|
| [`references/step-1-overview.md`](references/step-1-overview.md) | Objective, mode dispatch, scope boundary. |
| [`references/step-2-rules.md`](references/step-2-rules.md) | R1–R6 with before/after examples. |
| [`references/step-3-patterns.md`](references/step-3-patterns.md) | Cut targets per size. |
| [`references/step-4-anti-patterns.md`](references/step-4-anti-patterns.md) | Slop / concision / clarity fix tables. |
| [`references/step-5-report.md`](references/step-5-report.md) | Report fields, checks, completion. |
