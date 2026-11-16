# Step 2: Inventory

Read every skill in the audit root so Step 3 can cluster on full knowledge.

**Goal:** list every skill folder and read each `SKILL.md` frontmatter and body.

## Commands

- `sac catalog --build && sac catalog --read` — build the catalog and read every skill in the pack; one entry per skill (name + description).
- `sac read <name>` — read a skill's full `SKILL.md` when the catalog row is not enough to judge scope or overlap.
- `sac discover <query>` — find skills that share the same tooling or purpose before classifying a cluster (Step 4).

## Completion

- Every skill folder in the audit root appears in the catalog.
- Frontmatter and body of each `SKILL.md` is read.
- Each row notes the skills that share tooling or purpose.
