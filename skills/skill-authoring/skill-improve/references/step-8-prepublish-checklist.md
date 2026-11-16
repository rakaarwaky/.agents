# Improve — Step 8: Pre-publish checklist

**Goal:** you can run the pre-publish checklist and confirm the target skill is ready to publish — frontmatter, lint, body shape, references, and content all pass.

- [ ] `sac read <name>` — read back the target `SKILL.md` to confirm frontmatter and body landed correctly.
- [ ] `sac lint` passes (catalog in `step-4-validator-catalog.md`).
- [ ] Frontmatter satisfies the Rules bullets: mandatory keys, Frontmatter semantics, YAML hygiene, parser limits.
- [ ] Body within ~100–200 lines; overflow moved into `references/`; every reference, whatever its depth, is linked from `SKILL.md` (Rules: Structure). Quick probe when unsure: `sac lint` is the mechanical check, but a one-shot grep also works — `ls references/ | while read f; do grep -q "$f" SKILL.md || echo "unlinked: $f"; done` (basename containment, matching the linter's rule exactly).
- [ ] Every sibling mention and cross-skill link names a skill that exists in the tree (Rules: dangling refs).
- [ ] Content detail (`step-7-content-detail.md`) satisfied.
- [ ] 10Q gate cleared: the score block from `step-14-tenq-standard.md` is in the report, every score carries evidence, and the verdict is PASS — a FAIL is reported as a FAIL, never as done.
- [ ] `sac catalog --build` has been run so `skills/catalog.json` reflects the current frontmatter.
- [ ] **Verify on disk, not in memory**: before committing, grep the restructured body shape (`^## Rules`, `^## Routing`) and list each new reference file — a parallel agent or `git reset` can revert your files on disk without you noticing. After committing, `git show --stat <sha>` must list exactly your task files; a swept-in or missing-file commit is wrong and must be redone (re-apply, re-stage scoped, commit, re-verify).

## Completion

- Every box above is checked, or its gap is listed in the report with the owning file.
- `git show --stat <sha>` lists exactly this run's files.
