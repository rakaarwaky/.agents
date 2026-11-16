# Create — Step 1: Gather information

**10Q:** Q2, Q4

**Goal:** collect the skill's name, category, scope, and job description before drafting anything.

The job description is the only fact that must come from the user. Everything else defaults from the repo and is reported as `assumed` (Rules: safety model — the run is autonomous; the one blocking prompt lives in step 2).

| Fact | Resolution | Ask only when |
| ---- | ---- | ---- |
| Job description | From the invocation argument | It is missing or names two different deliverables |
| Skill name | Gerund-form, lowercase-hyphen, derived from the job; validate against `name-format` in `../../skill-improve/references/step-4-validator-catalog.md` | The derived name collides with an existing skill |
| Category | The category of the sibling skills that do the same kind of work | No sibling category fits |
| Scope | **Project** (`<repo-root>/<skills-dir>/<category>/<skill-name>/SKILL.md`) when inside a git repo; otherwise **User** (the harness's user-level skills directory) | The invocation names neither and the repo root is ambiguous |

Resolve the real directory for the chosen scope from the harness config or repo layout before writing; never hardcode a home path into the skill body.

## Commands

- `sac list` — check the existing pack before naming; a new skill must not collide with an existing name or duplicate a description.
- `sac discover <query>` — find skills that already cover the requested job; if a close match exists, route to `skill-improve` instead of creating a second skill.

## Completion

- Skill name validated against `name-format`; category and scope resolved; the job is described in one sentence naming one deliverable.
- Every defaulted fact is recorded for the report; the run continues to [`step-2-tenq-draft.md`](step-2-tenq-draft.md).
