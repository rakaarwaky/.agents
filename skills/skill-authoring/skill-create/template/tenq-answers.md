# 10Q answer sheet template

The single source of truth for the draft answer sheet a create run fills before writing any file. Copy the fenced shape, fill the placeholders, keep it in the run's scratch notes — it is a working artifact, not a shipped file of the new skill. The questions, rubric, and gate are owned by `../../skill-improve/references/step-14-tenq-standard.md`; this template never restates them.

```markdown
# 10Q draft — <skill-name>

Job: <one sentence, one deliverable>
Scope: <project|user> · Category: <category> · Source: <user job description>

| Q | Answer (paths, commands, numbers, steps) | Home in the artifact | Source |
| --- | --- | --- | --- |
| Q1 | <deliverable + done-criterion command> | Rules R<n> | <job\|repo\|assumed> |
| Q2 | <activation terms + environment precondition> | frontmatter + Rules R<n> | <job\|repo\|assumed> |
| Q3 | <audience + language/tone/conventions> | Rules R<n> | <job\|repo\|assumed> |
| Q4 | <exact files/config/args read> | references/step-<N>-<name>.md | <job\|repo\|assumed> |
| Q5 | <mandatory tools + forbidden tools> | Rules R<n> | <job\|repo\|assumed> |
| Q6 | <ordered steps> | Routing + step files | <job\|repo\|assumed> |
| Q7 | <max files, max iterations, forbidden actions> | Rules R<n> | <job\|repo\|assumed> |
| Q8 | <IF condition -> action or owning step> | Routing row / step-<N> branch table | <job\|repo\|assumed> |
| Q9 | <deliverable format + destination + report shape> | Rules R<n> + verify step | <job\|repo\|assumed> |
| Q10 | <symptom -> cause -> exact recovery> | step-<N> fallback table | <job\|repo\|assumed> |

Draft score: <total> (rubric + gate: skill-improve step-14) · Assumed: <Qn list> · Blocking question: <none, or the one question asked>
```

## How to fill each section

- **Job** — one sentence naming one deliverable. Two WHATs means two skills; split before filling the table (`../references/step-2-tenq-draft.md`).
- **Answer cells** — executable text only: a path, a command, a number, or a named step. An adjective is a score-1 answer.
- **Home** — the single place the answer will land, per the placement map in the standard. Name the Rules row ID or the step file; "somewhere in the body" is not a home.
- **Source** — `job` (the user said it), `repo` (read from the tree, cite the file in the answer), or `assumed` (a default was applied). Every `assumed` row appears in the final report.
- **Draft score** — score the sheet with the rubric before writing files; the artifact is re-scored afterwards by `../references/step-7-tenq-audit.md`.

## Completion

- All ten rows filled; every row names a home and a source; every `assumed` row is listed in the footer.
- The draft total is computed and the gate decision recorded; no row is left as a restatement of its question.
