# Reference file template

The single source of truth for the shape of any `references/<file>.md` a skill ships. Copy this shape; fill the placeholders. A reference holds the task-conditional detail the body's Rules row points at — commands with exact syntax, field shapes, per-step stop conditions, worked examples.

```markdown
# <Reference title — `Step <N>: <verb>` in a Pattern B pipeline>

<One or two lines: what this reference covers and when a step consults it. Design rules stay in SKILL.md Rules; this file never restates them.>

**Goal:** <one line — what the reader should achieve by the end of this reference.>

## <First section — usually scope / input resolution>

<The section body. The input read, the branches, and the fallback tables live here when this step owns them.>

## <Next section — commands, field shapes, examples>

<Exact syntax for any command or flag. Show the output shape.>

## Completion

- <Checkable stop condition 1.>
- <Checkable stop condition 2.>
```

## How to fill each section

- **Title** — `# <Reference title>`; one `#` heading naming what the reference is. In a Pattern B skill it carries the step number and verb.
- **Goal** — one line stating the outcome; a reference with no checkable goal is a no-op (Rules: no no-op sentences).
- **Sections** — group by what a step actually reads: scope/input resolution, then the concrete commands, field shapes, and worked examples. Move any fact read by more than one step up to the `SKILL.md` Rules instead: if a single invocation reads the fact in two or more steps, the Rules row is its home.
- **Completion** — every reference ends in checkable stop conditions; never "verify it works".

## The 3 reference patterns

A reference ships in one of three layouts: A (one file per mode, flat `references/<mode>.md`), B (numbered step files for one ordered pipeline, `references/step-<N>-<name>.md`), C (per-mode subdirs of numbered steps, `references/<mode>/step-<N>-<name>.md`). Pick from the skill's shape, never from the tree that exists today.

1. Does the skill run one ordered pipeline — does the agent always execute every step in sequence, with state flowing forward? Yes → Pattern B.
2. Does the agent pick exactly one mode per invocation? Yes → under ~100 lines and under 5 ordered steps per mode → Pattern A; larger → Pattern C for that mode only.
3. Neither → return to question 1 and apply Pattern B.

Renaming a reference file requires a grep sweep of the whole skill directory for the old name; the Routing table row, the file title, and every cross-link change in the same edit.

## Completion

- The file matches this skeleton: title, goal, sections, checkable `## Completion`.
- The pattern was chosen from the Routing table via the reference-pattern decision, and the filename matches that pattern.
