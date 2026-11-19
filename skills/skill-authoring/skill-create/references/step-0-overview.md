# Create — Step 0: Overview

Autonomous workflow for creating a new skill from scratch — default runs write without confirmation; `--dry-run` stops after the report. Design rules and frontmatter constraints are Rules in `SKILL.md`; these files hold only the step order.

**Goal:** produce a publishable `SKILL.md` + `references/` for a job the user describes, ending at the pre-publish checklist with the skill registered in the catalog and the quality gate cleared.

Run the steps in order; each links to the next.

| Step | File | What it does |
| ---- | ---- | ------------ |
| 1 | [`step-1-gather.md`](step-1-gather.md) | Collect name, category, scope, and the job description. |
| 2 | [`step-2-drafting.md`](step-2-drafting.md) | Answer all ten core questions and draft under `$DRAFT_DIR` (system temp directory). |
| 3 | [`step-3-review.md`](step-3-review.md) | Reviewer loop on the draft; write to real skills directory on 0 issues. |
| 4 | [`step-4-write.md`](step-4-write.md) | Create the directory, pick the writer path, write SKILL.md and supporting files. |
| 5 | [`step-5-verify.md`](step-5-verify.md) | Score the artifact, run the probes, enforce the gate, and verify/report. |

## Completion
- The five steps ran in order, or the run stopped at the step whose Completion failed.
- `--dry-run` ends with the planned-create report and no files written.
