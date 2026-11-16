# Reference file template

The single source of truth for the shape of any `references/<file>.md` a skill ships. Copy this shape; fill the placeholders. A reference holds the task-conditional detail the body's Rules row points at — commands with exact syntax, field shapes, per-step stop conditions, worked examples.

```markdown
# <Reference title — `Step <N>: <verb>` in a Pattern B pipeline>

**10Q:** <Qn list this file answers, or omit the line if it answers none>

<One or two lines: what this reference covers and when a step consults it. Design rules stay in SKILL.md Rules; this file never restates them.>

**Goal:** <one line — what the reader should achieve by the end of this reference.>

## <First section — usually scope / input resolution>

<The section body. Q4 inputs, Q8 branches, and Q10 fallback tables live here when this step owns them.>

## <Next section — commands, field shapes, examples>

<Exact syntax for any command or flag. Show the output shape.>

## Completion

- <Checkable stop condition 1.>
- <Checkable stop condition 2.>
```

## How to fill each section

- **Title** — `# <Reference title>`; one `#` heading naming what the reference is. In a Pattern B skill it carries the step number and verb.
- **10Q line** — the questions this file answers, so the coverage probe can find them. Omit it only when the file answers none.
- **Goal** — one line stating the outcome; a reference with no checkable goal is a no-op (Rules: no no-op sentences).
- **Sections** — group by what a step actually reads: scope/input resolution, then the concrete commands, field shapes, and worked examples. Move any fact read by more than one step up to the `SKILL.md` Rules instead (information-distribution test — `../../skill-improve/references/step-10-information-distribution.md`).
- **Completion** — every reference ends in checkable stop conditions; never "verify it works".

## The 3 reference patterns

A reference can ship in one of three layouts: A (one file per mode), B (numbered step files for one ordered pipeline), C (per-mode subdirs of numbered steps). Pick the pattern from the skill's **shape** — its Routing table — never from what the tree currently looks like. The full decision procedure, the pattern file trees, the "one ordered pipeline?" and "multiple independent modes?" tests, and the renumber-completion checklist live in `../../skill-improve/references/step-11-reference-pattern.md`; run it before creating or renaming any reference file.

## Completion

- The file matches this skeleton: title, optional `**10Q:**` line, goal, sections, checkable `## Completion`.
- The pattern was chosen from the Routing table via the reference-pattern decision, and the filename matches that pattern.
