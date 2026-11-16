# Create — Step 1: Gather information

**Goal:** collect the skill's name, category, and job description before drafting anything. The job description is the only fact that must come from the user; the agent derives the skill name and category autonomously.


| Fact            | Resolution                                                        | Ask only when                                      |
| --------------- | ----------------------------------------------------------------- | -------------------------------------------------- |
| Job description | From the invocation argument (`<job description>`).               | It is missing or names two different deliverables. |
| Skill name      | Gerund-form, lowercase-hyphen, derived from the job               | The derived name collides with an existing skill.  |
| Category        | The category of the sibling skills that do the same kind of work. | No sibling category fits.                          |


Resolve the real directory for the chosen scope from the harness config or repo layout before writing; never hardcode a home path into the skill body.

## Commands

- `sac list` — check the existing pack before naming; a new skill must not collide with an existing name or duplicate a description.
- `sac discover <query>` — find skills that already cover the requested job; if a close match exists, route to `skill-improve` instead of creating a second skill.

## Completion

- Skill name present and validated against `name-format`.
- Category present and resolved from sibling skills that do the same kind of work.
- Job description is one sentence naming one deliverable.

- The run continues to [`step-2-drafting.md`](step-2-drafting.md).