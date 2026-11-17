# Create — Step 5: Verify and report

**Goal:** the created skill is mechanically verified and the run ends with one report that carries the gate verdict.

- [ ] Read the file back and confirm frontmatter and body landed correctly, and the body matches the `SKILL.md` skeleton in [`../template/skill.md`](../template/skill.md) (`# <Skill Name>` / `## Rules` / `## Routing`).
- [ ] Run `sac lint` and clear the pre-publish checklist: `sac read <name>` for frontmatter and body, no unlinked `references/` file, every sibling mention resolves to an existing skill, body shape is exactly `# Title` / `## Rules` / `## Routing`.
- [ ] Carry the score block from step 2 (draft) and step 4 (write placement) into the report unchanged; a `Gate: FAIL` is never rewritten as a pass.
- [ ] Emit the report (Rules: report shape): changed-files table, check results, score block, gate verdict, every `assumed` default from the step-2 sheet.
- [ ] Tell the user how to invoke it (slash command, skills menu, description matching — whichever the target harness provides).
- [ ] Remind the user that new or renamed skills appear in the next session: loaders cache the skill list at session start. This is expected.

## Diagnosis & fallback (Rules: R21, R23)

When any check fails, do not emit generic advice — execute the matched fallback:

| Failure symptom | Probable cause | Recovery action |
|---|---|---|
| `sac lint` fails on `missing-description` | `description:` is unquoted with `:` or is an unclosed `>-` block scalar | Quote the description on a single line; verify the second `---` is immediately before `# Title` |
| `sac lint` fails on `reference-not-linked` | A reference file in `references/` has no basename match in `SKILL.md` | Add the link to the `## Routing` table with its purpose |
| `sac lint` fails on `name-format` | Skill name uses uppercase, spaces, or forbidden characters | Rename directory and frontmatter `name:` to lowercase letters, digits, and hyphens |
| `sac` CLI itself is missing/broken | Infra issue (`ModuleNotFoundError`, broken path) | Fall back to grep-class probes: `grep -n '^#' <SKILL.md>` for body shape, the four mandatory frontmatter keys, a char count against 1,024 on `description:` and `when-to-use:`, and an unlinked-refs sweep. Report the fallback; do not block the run |
| A check still fails after 2 self-repair iterations | The diagnosis was wrong, or the defect is out of scope (Rules: run ceilings) | Stop, report the failing command with expected vs actual, and name the owning file |

## Dry-run variant

With `--dry-run`, this step is the terminal report instead: present the planned skill (name, category, trigger fields, intended body outline, files that would be written), the draft score block labelled `source: draft`, and the pre-publish checklist status, and stop. No files are written, no catalog is rebuilt, no lint gate is applied to disk state.

## Completion

- Every checklist box is checked, or its failure is reported with the matched fallback.
- The report carries changed files, check results, the score block, the gate verdict, and the `assumed` list.
