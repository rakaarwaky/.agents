# SKILL.md Template

The single source of truth for the `SKILL.md` skeleton every created skill uses. Copy this shape; fill the placeholders. The body is always exactly three sections in this order: `# <Skill Name>`, `## Rules`, `## Routing`.

```markdown
---
name: <skill-name>
description: <what + when, third person, trigger terms. ≤ ~60 chars for the index display; ≤ 1,024 for the parser.>
when-to-use: "Use when <trigger conditions, synonyms, and negative scope>."
argument-hint: "<arg> [--flag] <other-arg>"
---

# <Skill Name>

You <one paragraph: what the agent does when this skill loads>.

## Rules

The question set, rubric, and gate live in `<path>/skill-improve/references/step-14-tenq-standard.md`.

| ID | Rule | Covers | Check |
|----|------|--------|-------|
| R1 | <Rule name>. <the rule, stated once — this row is its single home; detail beyond a few lines moves to a reference and the row points to it.> | <the ten-question answer this row covers, or `—` if none> | <how to check compliance: a command, a grep, or a countable condition> |

## Routing

| Step | File | Purpose |
|------|------|---------|
| 0 | [`references/step-0-<name>.md`](references/step-0-<name>.md) | <when this reference is read>. |
```

## How to fill each section

- **Frontmatter** — `name`, `description`, `when-to-use`, `argument-hint` are the four mandatory keys. Optional keys (`user-invocable`, `disable-model-invocation`, `paths`, ...) are target-dependent; the full table is in `../../skill-improve/references/step-3-frontmatter-keys.md`. The two trigger fields carry the when-and-where answer.
- **Rules** — one named row per cross-step rule; the row is the single home for that fact. Task-conditional content belongs in a reference, not here (Rules: budget for permanent cost). The rows must cover the cross-step answers: the success metric, audience and tone, tools (mandatory and forbidden), scope and iteration ceilings, and report shape.
- **Covers cell** — the ten-question answer the row covers, or `—`. Every question must be covered somewhere in the skill; the placement map and coverage probe are in `../../skill-improve/references/step-14-tenq-standard.md`.
- **Routing** — one table row per reference file the skill ships, in execution order, each linking `references/step-<N>-<name>.md`. A single-file skill with no references omits the section.

## Completion

- `SKILL.md` matches this skeleton exactly: four mandatory frontmatter keys, then `# <Skill Name>` / `## Rules` / `## Routing` and nothing else in the body.
- Every Rules row has a checkable Check; the ten core questions are answered once, at their assigned home; the artifact passes the gate in `../../skill-improve/references/step-14-tenq-standard.md`.
