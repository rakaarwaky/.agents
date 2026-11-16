# Create — Step 6: Verify and report

- [ ] Read the file back and confirm frontmatter and body landed correctly, and the body matches `template/skill.md` (`# <Skill Name>` / `## Rules` / `## Routing`).
- [ ] Run `sac lint` and the pre-publish checklist in `../../skill-improve/references/step-8-prepublish-checklist.md`.
- [ ] `sac read <name>` — confirm the skill is registered and the frontmatter parses.
- [ ] Tell the user how to invoke it (slash command, skills menu, description matching — whichever the target harness provides).
- [ ] Remind the user that new or renamed skills appear in the next session: loaders cache the skill list at session start. This is expected.

## Diagnosis & fallback (Rules: R21, R23)

When any check fails, do not emit generic advice — execute the matched fallback:

| Failure symptom | Probable cause | Recovery action |
|---|---|---|
| `sac lint` fails on `missing-description` | `description:` is unquoted with `:` or is an unclosed `>-` block scalar | Quote the description on a single line; verify the second `---` is immediately before `# Title` |
| `sac lint` fails on `reference-not-linked` | A reference file in `references/` has no basename match in `SKILL.md` | Add the link to the `## Routing` table with its purpose |
| `sac lint` fails on `name-format` | Skill name uses uppercase, spaces, or forbidden characters | Rename directory and frontmatter `name:` to lowercase letters, digits, and hyphens |
| `sac` CLI itself is missing/broken | Infra issue (`ModuleNotFoundError`, broken path) | Fall back to grep probes (`grep -n '^#' SKILL.md`, char-count, unlinked-refs probe per `skill-improve/references/step-12-apply.md`); do not block the run |

## Dry-run variant

With `--dry-run`, this step is the terminal report instead: present the planned skill (name, category, trigger fields, intended body outline, files that would be written) and the pre-publish checklist status, and stop. No files are written, no catalog is rebuilt, no lint gate is applied to disk state.
