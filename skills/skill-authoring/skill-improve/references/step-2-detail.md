# Improve — Step 2: Naming, description, and content detail

**Goal:** name or rename a skill, write a third-person specific description, and fix body content so examples are concrete and conventions are followed.

## Naming detail

- Gerund form preferred (`processing-pdfs`) over `pdf-processing`, when both are valid.
- Pipeline reference files follow `step-<N>-<name>.md` in execution order (Pattern B; decision lives in `step-3-publish.md`). When converting an existing flat `references/<name>.md` tree to a pipeline: renumber in execution order, merge any content that belongs to one step into that step's file, and use `git mv` so history survives.
- A new file's content shape derives from the pattern: a new Pattern B step file must carry the reference template's shape (`# Step N — <name>`, a `**Goal:**` line, sections, and a `## Completion` block).
- Two files may never share the same step number — if a conversion would produce `step-2-a` and `step-2-b`, the second file's content belongs inside the first file's step, as a section.
- After renumbering or merging, sweep for old names: every cross-reference, Routing-table row, and `skill_dir`/`args` hint naming a reference file must be updated to the new name, and each renamed file's own `# Title` must match its step. Verify with one grep for the deleted file names — every hit is a dangling link and the renumber is incomplete.
- Renaming a skill = rename the directory (`git mv`); the dangling-pointer sweep afterwards is owned by the Verify step. After the rename, verify:

```bash
sac read <new-name>
sac catalog --build
```

`sac read` confirms the directory and frontmatter match; `sac catalog --build` refreshes the catalog rows that carry the old path. If `sac lint` reports `name-mismatch`, the frontmatter `name:` was not updated to match the new directory name — fix the frontmatter, not the directory.

## Description detail

Write a third-person, specific `description` that names the artifact and action, and keep trigger phrases out of it:

- Third person: "Extracts text from PDFs", never "I can help".
- Specific: "Helps with documents" fails — name the artifact and the action.
- Leftover trigger phrases go to `when-to-use:`, not into an ever-longer description.

## Content detail

Judge and fix body content so examples are concrete, defaults replace menus, and scripts, tool references, and paths follow conventions:

- Concrete examples over abstract description; input/output pairs for style-dependent output.
- Defaults, not menus of alternatives.
- Scripts handle errors themselves, justify constants, list dependencies.
- Prefer referencing existing CLI tools over writing custom scripts.
- MCP tools named fully qualified (`ServerName:tool_name`).
- Forward slashes in paths (`scripts/helper.py`); no time-sensitive content in the body.
- **Safety-model consistency**: when the user re-specifies which mode control flag governs the run (e.g. `--dry-run` vs `--headless` vs no flag), the single source of truth is the Safety model bullet in `SKILL.md` Rules. Sync that bullet, the `argument-hint` in frontmatter, and every step-file line describing mode behavior — all three must agree on default-vs-flag semantics.

## Completion

- Directory name, frontmatter `name:`, and catalog agree; `sac read <name>` resolves.
- A grep for every old filename and old path returns zero hits.
- `description` names the artifact and action in third person, no trigger phrases; trigger phrases moved to `when-to-use:`.
- Examples are concrete input/output pairs; defaults replace menus; scripts handle errors themselves; MCP tools fully qualified; paths use forward slashes; no time-sensitive content; safety-model bullet, `argument-hint`, and step files agree on default-vs-flag semantics.
