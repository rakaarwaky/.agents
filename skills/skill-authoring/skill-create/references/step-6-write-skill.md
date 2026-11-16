# Create — Step 6: Write SKILL.md

**10Q:** Q1, Q3, Q5, Q6, Q7, Q9

**Goal:** write `SKILL.md` and any supporting files from the templates, with every 10Q answer landed at its single home.

Frontmatter first, then the standard body. The shape of every template lives in `template/`, and `template/template.md` is the single entry point that routes to the right one — read that index, then copy the template it names rather than restating any shape here.

## Procedure

1. Open [`../template/skill.md`](../template/skill.md), fill the placeholders, and write the result to `<SKILL_DIR>/SKILL.md`. Any reference docs the skill ships use [`../template/reference.md`](../template/reference.md) as their shape (both chosen via [`../template/template.md`](../template/template.md)).
2. Place each answer from the step-2 sheet at the home the placement map assigns (`../../skill-improve/references/step-14-tenq-standard.md`): Q1, Q3, Q5, Q7, Q9 as Rules rows; Q2 in the trigger fields plus a precondition row; Q4, Q6, Q8, Q10 in the step files that own them.
3. Tag every Rules row's `10Q` cell with the questions it answers (`—` if none), and give every step file that owns answers a `**10Q:**` line under its title. Untagged answers are invisible to the coverage probe.
4. Ship at least one concrete Input → Output example in the step file that owns the output shape (Q9): the user request verbatim, then the exact files or text it produces.
5. Write supporting scripts and references as needed, using absolute paths so nothing lands in the wrong place.

Mandatory keys, YAML hygiene, and which optional keys are safe to add are Rules; the full key table and the parser ceilings are in `../../skill-improve/references/step-3-frontmatter-keys.md`.

## Completion

- `SKILL.md` written from `../template/skill.md`: four mandatory frontmatter keys, then `# <Skill Name>` / `## Rules` / `## Routing` and nothing else in the body.
- Every one of the ten answers is present in the file its home names, tagged, and stated once; references follow `../template/reference.md`.
