# Create — Step 2: Draft the trigger fields

**Goal:** draft `description:` and `when-to-use:` together and keep the two fields non-overlapping.

Draft `description:` and `when-to-use:` together — both are mandatory (Rules) and both drive auto-invocation. Apply the Frontmatter semantics bullet and the description detail in `../../skill-improve/references/step-6-description-detail.md`. Keep the two fields non-overlapping (Rules: budget for permanent cost).

- **Default**: no approval gate — proceed straight to writing the skill; the drafted fields appear in the final report.
- **`--dry-run`**: report only — present the drafted fields in the planned-create report and stop before writing anything.

## Trigger audit

The trigger field is the skill's activation gate — a vague `description:` or a `when-to-use:` that restates it means the skill never fires (R7). Run both checks before leaving this step:

1. **Description must name artifact + action + condition.** Write `description:` as a third-person sentence naming the artifact and the action (`"Extracts text from PDFs"`), and append the trigger condition as a "Use when …" clause only when it adds a condition the artifact name does not already imply. A trigger phrase that merely restates the artifact ("use when working with PDFs") is redundant — cut it, keep it in `when-to-use:`.
2. **`when-to-use:` is the trigger home.** All activation conditions, synonyms, and negative-scope ("not for X") live in `when-to-use:`, never in `description:`. Keep the two fields non-overlapping (Rules: budget for permanent cost).

| Symptom (observed after publishing) | Gap | Fix |
|---|---|---|
| Skill never triggers | `description:` is vague or artifact-less / `when-to-use:` missing trigger terms | Rewrite both per this step |
| Skill triggers on wrong tasks | `description:` reads like a trigger phrase; `when-to-use:` has no negative-scope | Move trigger phrasing to `when-to-use:`; add negative scope |
| Skill triggers on every task in the domain | `description:` too broad, no narrow condition | Narrow with a concrete "Use when <condition>" clause |

## Completion

- `description:` and `when-to-use:` drafted and non-overlapping; default runs continue without user approval.
- Description names the artifact + action (third person), trigger phrases live only in `when-to-use:`; both fields satisfy the trigger audit.
