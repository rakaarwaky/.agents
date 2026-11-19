# Create — Step 4: Write the skill to disk

**Goal:** create the skill directory, pick the writer path, write `SKILL.md` and supporting files from the templates, with every answer landed at its single home.

## Dry-run guard

With `--dry-run`, skip this step entirely. Nothing is written to the real skills directory. Proceed directly to step 5 (`step-5-verify.md`) for the terminal report.

## Part A: Create the directory

```bash
mkdir -p <SKILL_DIR>
```

Create `<SKILL_DIR>/scripts/` if the skill ships helper scripts, `<SKILL_DIR>/references/` if it needs reference docs, and `<SKILL_DIR>/template/` if it ships one skeleton file per artifact it produces. The file fails to save without the directory. If the category folder is new, create its `DESCRIPTION.md` — the pack audit requires one.

```bash
# Create the skill directory
mkdir -p <SKILL_DIR>

# Register a new category (only when the category folder is new)
sac create category <cat> --description "<one-line category description>" --apply

# Rebuild the catalog so the new category appears
sac catalog --build
```

Without `--apply` the `create category` command previews the plan; with it, the category folder and `DESCRIPTION.md` are written.

## Part B: Choose the writer path

Pick by description length:

- **`sac create skill <name> --category <cat> --apply`** — CLI verb; creates the directory and `SKILL.md` in one call with frontmatter keys `name`, `description`, `when-to-use`, `argument-hint`, and the body. Pass `--apply` to write; without it you get a dry-run plan. Enforces a ~60-char budget on `description:`.
- **`skill_manage(action=create)`** — safe default; creates the directory and `SKILL.md` in one call. Enforces the ~60-char `description:` budget and rolls back the whole batch on any violation. If it succeeds, skip Part C and go to step 5 (`step-5-verify.md`).
- **Write the files directly** (`write_file`) — continue with Part C. Use this when the description needs more than ~60 chars, when building a richer multi-file skill, or when `sac create skill` keeps rejecting frontmatter. After writing, run `sac catalog --build` to register the skill.

The ~60-char index budget and the 1,024-char parser limit are different ceilings: the parser accepts long descriptions, the index display clips them.

## Part C: Write SKILL.md and supporting files

Frontmatter first, then the standard body. The shape of every template lives in `template/`, and `template/template.md` is the single entry point that routes to the right one — read that index, then copy the template it names rather than restating any shape here.

1. Open [`../template/skill.md`](../template/skill.md), fill the placeholders, and write the result to `<SKILL_DIR>/SKILL.md`. Any reference docs the skill ships use [`../template/reference.md`](../template/reference.md) as their shape (both chosen via [`../template/template.md`](../template/template.md)).
2. Place each answer at its single home: the success metric, audience and tone, tools, ceilings, and report shape as Rules rows; activation and precondition in the trigger fields; the read-inputs, steps, branches, and fallback in the step files that own them.
3. Ship at least one concrete Input → Output example in the step file that owns the output shape: the user request verbatim, then the exact files or text it produces.
4. Write supporting scripts and references as needed, using absolute paths so nothing lands in the wrong place.

Mandatory keys, YAML hygiene, and which optional keys are safe to add are Rules in `SKILL.md`; nothing else gates them.

## Completion

- `<SKILL_DIR>` exists with any needed `scripts/` / `references/` subdirs; a new category has a `DESCRIPTION.md`. `catalog.json` is rebuilt by `sac catalog --build`.
- A writer path was chosen: `skill_manage` (short description, skip to step 5 verify) or `write_file` (long/rich, files written here).
- `SKILL.md` written from `../template/skill.md`: four mandatory frontmatter keys, then `# <Skill Name>` / `## Rules` / `## Routing` and nothing else in the body.
- Every one of the ten answers is present in the file its home names, stated once; references follow `../template/reference.md`.
- The run continues to step 5 (`step-5-verify.md`).
