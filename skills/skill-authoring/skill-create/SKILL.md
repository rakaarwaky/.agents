---
name: skill-create
description: "Create a SKILL.md from a described job."
user-invocable: true
when-to-use: "Author a new SKILL.md for a capability that has no loaded skill. One skill per invocation. --dry-run stops after the report without writing."
argument-hint: "<job description> [--dry-run]"
---

# Skill Create

You author a new agent skill from a job description: `SKILL.md`, `references/`, and `templates/` where relevant. One skill per invocation.

**Purpose:** build a publishable skill that reads clean, invokes correctly, follows the shared body shape and lint standard, and carries no duplicate content. Every fact lives once in a single authoritative home; flag and mode terms stay in lockstep across `SKILL.md` and its reference files.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **Interface changes ripple.** The `argument-hint` plus every flag and safety-model mention must stay in lockstep. Grep the whole skill directory for each flag name and mode term before deciding an edit is done. | Grep every flag name and mode term across body + `references/`; zero stale references after the edit. |
| R2 | **One home per fact.** Each rule, value, or list lives in a single authoritative place. When an edit touches an existing copy elsewhere, make the change and report the duplication instead of silently rewriting. | No fact appears in two locations. |
| R3 | **No no-op sentences.** If a sentence does not change behavior, delete it or replace with a checkable criterion. | Every sentence changes behavior or is deleted. |
| R4 | **Set degrees of freedom.** High (text steps) for context-dependent work; medium (parameterized scripts) when a preferred pattern exists; low (exact commands) for fragile, strict-sequence operations. | DOF level chosen per step kind. |
| R5 | **Budget for permanent cost.** `description:` and `when-to-use:` are injected into the skill list every session; the body loads per use; `references/*.md` cost nothing until opened. Keep the two trigger fields non-overlapping. | `description:` and `when-to-use:` non-overlapping; task-conditional content moved out of body into references. |
| R6 | **Mandatory frontmatter.** Exactly four keys: `name`, `description`, `when-to-use`, `argument-hint`; every other key is optional. | Four mandatory keys present. |
| R7 | **Frontmatter semantics.** `description:` = WHAT + WHEN + trigger terms, third person. Trigger overflow goes in `when-to-use:`, never a `triggers:` key. | `description:` covers WHAT + WHEN; no `triggers:` key. |
| R8 | **YAML hygiene.** Quote values containing `: ` or indicator characters. Unclosed frontmatter makes the parser silently drop `description` and `when-to-use`. | Values with `: ` quoted; second `---` verified immediately before `# Title`. |
| R9 | **Structure.** One `SKILL.md` per `<category>/<skill>/SKILL.md`. Body ~100–200 lines; detail in `references/*.md`; non-trivial logic in `scripts/<file>`. | Body ~100–200 lines; every reference linked from SKILL.md. |
| R10 | **Mandatory body shape.** Exactly three sections: `# Title`, `## Rules`, `## Routing`. Stop conditions are Rules bullets, not their own heading. | `grep ^## ` returns exactly `## Rules` and `## Routing`. |
| R11 | **Templates are the source of truth.** `template/skill.md` is the canonical skeleton; `template/reference.md` the canonical reference shape. | Create steps copy from template; no inline restatements. |
| R12 | **Tracked catalog.** `sac catalog --build` regenerates `catalog.json`. Rebuild after any frontmatter change. | `catalog.json` rebuilt after every frontmatter change. |
| R13 | **Safety model.** All steps run autonomously by default. `--dry-run` generates the full report and stops before any snapshot or execute. Destructive actions go to `_archive/` first. | All steps proceed without confirmation; `--dry-run` stops before write. |
| R14 | **Staging discipline.** Use explicit top-level paths; never `git add -A`. Verify staged set with `git diff --cached --name-only` before committing. | Staged set is exactly task files before commit. |
| R15 | **Lane delegation for coding skills.** Hermes orchestrates; Grok Build implements inside Orca worktrees. Two lanes: `references/hermes/` and `references/grok/`. | Hermes drops one brief per worktree; verifies inside worktree path. |
| R16 | **Rollback.** Snapshot SHA or `git reset --hard <sha>` is the undo path. A run that cannot commit falls back to report-only. | Snapshot SHA recorded; `git reset --hard <sha>` used for rollback. |
| R17 | **Parallel agents.** Re-read at least one touched file after writes to confirm content is on disk. Keep commits scoped to task files. | On-disk state re-verified; commits scoped to task files only. |
| R18 | **`mkdir -p` before `git mv`.** Always `mkdir -p` the destination directory before a `git mv` chain into a subdirectory. | `mkdir -p` runs before every `git mv` into a subdirectory. |
| R19 | **Patch escape-drift.** On `Escape-drift detected` from a patch, read the full file and use `write_file` instead of retrying. | Full file read and `write_file` on escape-drift failure. |
| R20 | **Verify pack roots.** `default_pack_root()` must return a path whose `parents[N]` IS `skills/` — do not append `"/skills"` after it. | `default_pack_root().name == "skills"`; `sac catalog --build` prints the correct path. |


## Routing

| Step | File | Purpose |
| ---- | ---- | ------- |
| 0 | [`references/step-0-overview.md`](references/step-0-overview.md) | Create mode overview |
| 1 | [`references/step-1-gather.md`](references/step-1-gather.md) | Gather name, category, scope, and job description |
| 2 | [`references/step-2-trigger-fields.md`](references/step-2-trigger-fields.md) | Draft and approve `description:` / `when-to-use:` |
| 3 | [`references/step-3-directory.md`](references/step-3-directory.md) | Create the skill directory and subdirs |
| 4 | [`references/step-4-writer.md`](references/step-4-writer.md) | Pick a writer by description length |
| 5 | [`references/step-5-write-skill.md`](references/step-5-write-skill.md) | Write `SKILL.md` and supporting files |
| 6 | [`references/step-6-verify.md`](references/step-6-verify.md) | Verify and report; `--dry-run` ends here |
