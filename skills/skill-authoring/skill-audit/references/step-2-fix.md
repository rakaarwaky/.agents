# Audit — Step 2: Fix each class at its owner

Repair every bucketed issue with the recipe its class names, one edit per owner file.

With `--dry-run`, print the planned edit or command for each bucketed issue and stop — no file edits, no `sac archive`, no `git mv`.

Run the recipes in the order the classes appear in the scan; a fix in one class can resolve or create another, so re-check the affected skills after each recipe.

## 2.1 Class-to-recipe map

| Class | Recipe | Verify |
| --- | --- | --- |
| `missing-category-description` | Write `skills/<cat>/DESCRIPTION.md` with YAML frontmatter: `---`, then `description: <one line>`, then `---` — the linter reads the frontmatter, so a bare `# Heading` file does not clear the class. `sac create category <cat> --description "<one-line>" --apply` performs the same write when the category is new. Remove an empty category dir instead if it holds no skills. | `sac lint --category <cat>` output has no `missing-category-description` line |
| `empty-category-description` | Fill `skills/<cat>/DESCRIPTION.md` frontmatter: `---`, then `description: <one line>`, then `---`. | `sac lint --category <cat>` output has no `empty-category-description` line |
| `name-mismatch` | Compare frontmatter `name:` with the directory. If the description matches the directory's intent, `git mv` the directory to the frontmatter name; otherwise rewrite the frontmatter `name:` to the directory name. | `grep -m1 '^name:' <SKILL.md>` equals `basename $(dirname <SKILL.md>)` |
| `too-deep` | `mkdir -p` the target `<cat>/<name>`; `git mv <old>/SKILL.md <cat>/<name>/SKILL.md`; move `references/` and `templates/` too; remove the emptied parent dir. | `sac lint --category <cat>` output has no `too-deep` line for that skill |
| `duplicate-skill-name` | The linter keys duplicates on the directory name (`entry.skill = skill_dir.name`), so a frontmatter `name:` change does not clear the class — the directory must move. Read both paths from the `sac lint` issue line (`... appears in: <cat1>/<name>, <cat2>/<name>`) or `skills/catalog.json`. `sac archive <name>` writes on the bare verb in this pack: the renderer prints "No files were modified. Pass --apply" whenever the verb returns without a plan and carries a message, and archive's outcome dict is non-empty — so the message prints while the skill has already moved. It resolves a bare name to the alphabetically first match (`find_skill_dir` → `min(matches)`), which may be the survivor — archive by bare name only when the alphabetical-first path is the loser; otherwise move the loser's directory with `git mv`. After every archive, run `git status --porcelain skills/.archive` and handle that tree per step-4.3a. | `sac lint --category <cat>` output has no `duplicate-skill-name` line for that name |
| `duplicate-description` | Keep the description on the alphabetically-first path (the one `sac archive` resolves to); rewrite the other description to name its own distinct scope, or `sac archive` the other by bare name when it duplicates the whole skill (same bare-verb and alphabetical-first caveats as `duplicate-skill-name`; check `git status` after). When both `duplicate-skill-name` and `duplicate-description` hit the same pair, fix `duplicate-skill-name` first, then re-scan for `duplicate-description`. | `sac lint` output has no `duplicate-description` line for the pair |
| `reference-not-linked` | Add a `## Routing` row in the owning `SKILL.md` linking the file, or delete the orphan with `git rm` when it duplicates a linked file. | `grep -q '<file>' SKILL.md` succeeds |
| any other class | Open the linter's rule catalog in `skill-improve/references/step-1-format.md`, fix at the file the rule owns, record the class in the report. If the class is not in that catalog, report it and stop. | `sac lint` output has no line for that class and subject |

**Note:** `sac lint --category <cat>` always exits `1` when any library-wide weed line exists (duplicates, empty categories) — the exit code is not a scoped pass. Verify a scoped fix by grepping the output for the class and subject. `sac discover` is also unreliable in this pack — its renderer prints names only and returns no matches. Read paths from the `sac lint` issue line or `skills/catalog.json`.

## 2.2 Branch table

| Condition | Action |
| --- | --- |
| two skills share a name and both look current | read both paths from the `sac lint` issue line or `skills/catalog.json`; archive the one in the wrong category (bare name only if the alphabetical-first match is the loser; the bare verb writes); never rewrite both descriptions to make them differ |
| the `too-deep` skill's `references/` links use relative paths | fix the relative links after the move; `grep -rn 'references/' <cat>/<name>/SKILL.md` |
| the `name-mismatch` rename would break a cross-skill link | `grep -rn '<old-name>' skills/` first, then `git mv`, then fix every hit |
| a `duplicate-skill-name` pair survives a frontmatter edit | the linter keys on the directory name — `git mv` the loser's directory or `sac archive` it (bare name, alphabetical-first check); a `name:` edit alone cannot clear the class |
| a fix would delete a skill directory | `sac archive <name>` writes on the bare verb (see the `duplicate-skill-name` row); check `git status --porcelain skills/.archive` after; never `rm -rf` a skill |
| a fix would edit `modules/`, `vendor/`, `workflows/`, `personas/`, `roles/`, `develop/`, `config/` | stop; report the issue as out of scope with its owning path |

## 2.3 Worked example

Scan line: `- [too-deep] figcraft/figure-skills/paper-figure/SKILL.md: SKILL.md is nested deeper than category/skill/SKILL.md.`

```bash
cd "$(git rev-parse --show-toplevel)"
mkdir -p skills/figcraft/paper-figure
git mv skills/figcraft/figure-skills/paper-figure/SKILL.md skills/figcraft/paper-figure/SKILL.md
git mv skills/figcraft/figure-skills/paper-figure/references skills/figcraft/paper-figure/references
rmdir skills/figcraft/figure-skills/paper-figure
sac lint --category figcraft; echo "exit=$?"
```

Expected: the `too-deep` line for `paper-figure` is gone from the output.

## 2.4 Fix-safety

Before the first `git mv`, record `git rev-parse HEAD` (step-1). If a fix corrupts a skill, `git reset --hard <SHA>` restores the pack and the loop restarts from step-1. Republishing the restored state after a reset is the rollback path in step-5.4 — the only force-push path this skill documents.

## Completion

- Every bucketed issue has a recipe applied at its owner.
- Every `git mv` was preceded by `mkdir -p` of the destination.
- Every delete went through `sac archive` (bare verb writes) or `git rm` for orphans; `git status --porcelain skills/.archive` checked after each archive.
- No out-of-scope path was edited.
- Continue to [`step-3-loop.md`](step-3-loop.md).