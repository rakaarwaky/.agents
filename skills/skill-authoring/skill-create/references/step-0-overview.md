# Create — Step 0: Overview

Autonomous workflow for creating a new skill from scratch — default runs write without confirmation; `--dry-run` stops after the report. Design rules and frontmatter constraints are Rules in `SKILL.md`; these files hold only the step order.

**Goal:** produce a publishable `SKILL.md` + `references/` for a job the user describes, ending at the pre-publish checklist with the skill registered in the catalog and the 10Q gate cleared.

Run the steps in order; each links to the next.

| Step | File | What it does |
| ---- | ---- | ------------ |
| 1 | [`step-1-gather.md`](step-1-gather.md) | Collect name, category, scope, and the job description. |
| 2 | [`step-2-tenq-draft.md`](step-2-tenq-draft.md) | Answer Q1–Q10, apply defaults for silence, score the draft. |
| 3 | [`step-3-trigger-fields.md`](step-3-trigger-fields.md) | Build `description:` / `when-to-use:` from Q1 + Q2. |
| 4 | [`step-4-directory.md`](step-4-directory.md) | Create the skill directory and any `scripts/` / `references/` subdirs. |
| 5 | [`step-5-writer.md`](step-5-writer.md) | Pick a writer by description length. |
| 6 | [`step-6-write-skill.md`](step-6-write-skill.md) | Write `SKILL.md` and supporting files; place each answer at its home. |
| 7 | [`step-7-tenq-audit.md`](step-7-tenq-audit.md) | Score the artifact, run the probes, enforce the gate. |
| 8 | [`step-8-verify.md`](step-8-verify.md) | Verify and report the outcome; `--dry-run` ends with the planned-create report instead. |

## Completion

- The eight steps ran in order, or the run stopped at the step whose Completion failed.
- `--dry-run` ended at step 8's report with no files written.
