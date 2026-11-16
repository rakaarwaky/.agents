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

The `10Q` cell names the questions a row answers (`—` = none); the question set, rubric, and gate live in `<path>/skill-improve/references/step-14-tenq-standard.md`.

| ID | Rule | 10Q | Check |
|----|------|-----|-------|
| R1 | <Rule name>. <the rule, stated once — this row is its single home; detail beyond a few lines moves to a reference and the row points to it.> | <Qn> | <how to check compliance: a command, a grep, or a countable condition> |

## Routing

| Step | File | Purpose |
|------|------|---------|
| 0 | [`references/step-0-<name>.md`](references/step-0-<name>.md) | <when this reference is read>. |
```

## How to fill each section

- **Frontmatter** — `name`, `description`, `when-to-use`, `argument-hint` are the four mandatory keys. Optional keys (`user-invocable`, `disable-model-invocation`, `paths`, ...) are target-dependent; the full table is in `../../skill-improve/references/step-3-frontmatter-keys.md`. The two trigger fields carry the Q2 answer.
- **Rules** — one named row per cross-step rule; the row is the single home for that fact. Task-conditional content belongs in a reference, not here (Rules: budget for permanent cost). The rows must cover the cross-step 10Q answers: Q1 success metric, Q3 audience and tone, Q5 tools (mandatory and forbidden), Q7 scope and iteration ceilings, Q9 report shape.
- **`10Q` cell** — the question IDs the row answers, or `—`. Every question Q1–Q10 must be claimed by a Rules row or by a step file's `**10Q:**` line; the placement map and the coverage probe are in `../../skill-improve/references/step-14-tenq-standard.md`.
- **Routing** — one table row per reference file the skill ships, in execution order, each linking `references/step-<N>-<name>.md`. A single-file skill with no references omits the section.

## Completion

- `SKILL.md` matches this skeleton exactly: four mandatory frontmatter keys, then `# <Skill Name>` / `## Rules` / `## Routing` and nothing else in the body.
- Every Rules row has a `10Q` cell and a checkable Check; all ten questions are claimed somewhere in the skill; the artifact passes the gate in the 10Q standard.
