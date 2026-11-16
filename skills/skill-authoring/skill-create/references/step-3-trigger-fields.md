# Create — Step 3: Build the trigger fields

**10Q:** Q2

**Goal:** turn the Q1 and Q2 answers into a `description:` and a `when-to-use:` that stay non-overlapping.

Both fields are mandatory (Rules) and both drive auto-invocation. Take the artifact and action from the Q1 answer and the activation conditions from the Q2 answer — do not re-interview the user. Apply the frontmatter semantics Rule and the description detail in `../../skill-improve/references/step-6-description-detail.md`.

- **Default**: no approval gate — proceed straight to writing the skill; the drafted fields appear in the final report.
- **`--dry-run`**: report only — present the drafted fields in the planned-create report and stop before writing anything.

## Trigger audit

The trigger fields are the skill's activation gate — a vague `description:` or a `when-to-use:` that restates it means the skill never fires (R7). Run both checks before leaving this step:

1. **Description must name artifact + action + condition.** Write `description:` as a third-person sentence naming the artifact and the action (`"Extracts text from PDFs"`), and append the trigger condition as a "Use when …" clause only when it adds a condition the artifact name does not already imply. A trigger phrase that merely restates the artifact ("use when working with PDFs") is redundant — cut it, keep it in `when-to-use:`.
2. **`when-to-use:` is the trigger home.** All activation conditions, synonyms (including the user's own language), and negative-scope ("not for X"; the sibling skill that owns the adjacent job) live in `when-to-use:`, never in `description:`. Keep the two fields non-overlapping (Rules: budget for permanent cost).

Observed trigger failures after publishing are diagnosed by the symptom map in `../../skill-improve/references/step-15-tenq-diagnosis.md`; the fix lands here.

## Completion

- `description:` names the artifact + action in third person; `when-to-use:` carries every trigger phrase, synonym, and negative scope; the two fields share no phrase.
- Both fields trace to the Q1/Q2 answers, and both appear in the run report.
