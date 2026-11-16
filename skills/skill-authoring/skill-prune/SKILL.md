---
name: skill-prune
description: "Consolidate duplicate skill folders into one."
user-invocable: true
when-to-use: "Collapse overlapping or duplicate skill folders into one consolidated folder, archiving the dropped ones. --dry-run stops after the report without writing."
argument-hint: "<category or --all> [--dry-run]"
---

# Skill Prune

You collapse duplicate and same-purpose skill folders into one, archiving the dropped duplicates. Works on a category or the whole tree.

**Purpose:** read every skill's description and body, merge skills that duplicate, share a bounded purpose, or share tooling into one consolidated folder, and archive the dropped duplicates. Genuinely different jobs stay separate — note why in the report.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **One home per fact.** Each rule, value, or list lives in a single authoritative place; when an edit touches a copy elsewhere, report the duplication instead of silently rewriting. | No fact appears in two locations. |
| R2 | **Solve the class, not the instance.** Fix the pattern, not the symptom. Check every generalization against at least two concrete instances. | Every fix located at the fact's owner. |
| R3 | **Consistent terminology.** One term per concept, no synonyms; model-agnostic wording. | No synonyms in merged skill bodies. |
| R4 | **Dangling refs rot fast.** `related_skills:`, sibling mentions, and cross-skill links are not existence-checked — resolve each against the tree before relying on it; remove refs to skills that do not exist. | Every cross-skill link resolved against the tree. |
| R5 | **Structure.** One `SKILL.md` per `<category>/<skill>/SKILL.md`; nested `SKILL.md` files are rejected. | One `SKILL.md` per folder; no nesting. |
| R6 | **Tracked catalog.** `sac catalog --build` regenerates `catalog.json`. Rebuild after any merge. | `catalog.json` rebuilt after the merge. |
| R7 | **Rollback.** Snapshot SHA or `git reset --hard <sha>` is the undo path. A run that cannot commit falls back to report-only. | Snapshot SHA recorded; rollback path documented. |
| R8 | **Safety model.** All steps run autonomously by default. `--dry-run` generates the full report and stops before any write. Destructive actions go to `_archive/` first; permanent delete only with explicit `--hard-delete`. | `--dry-run` stops before write; archives first. |
| R9 | **Parallel agents.** Re-read at least one touched file after writes. Keep commits scoped to task files; never `git add -A`. | On-disk state re-verified; commits scoped to task files. |
| R10 | **Staging discipline.** Use explicit top-level paths; verify staged set with `git diff --cached --name-only` before committing. | Staged set is exactly task files before commit. |
| R11 | **`mkdir -p` before `git mv`.** Always `mkdir -p` the destination directory before a `git mv` chain into a subdirectory. | `mkdir -p` runs before every `git mv` into a subdirectory. |
| R12 | **Patch escape-drift.** On `Escape-drift detected`, read the full file and use `write_file` instead of retrying. | Full file read and `write_file` on escape-drift. |
| R13 | **Verify pack roots.** `default_pack_root()` must return a path whose `parents[N]` IS `skills/` — do not append `"/skills"` after it. | `default_pack_root().name == "skills"`. |

**Classification rules** (prune-specific, not in the shared rules):

| Rule | Check |
|------|-------|
| **Prune standard**: two skills covering the same job become one folder; skills that share a domain but differ per scenario stay one folder with one `SKILL.md` plus a `references/` subfolder, one file per scenario. Genuinely different jobs stay separate. | Clusters classified against this standard before any merge. |
| **Prune phase order**: Phase 1 (remove true duplicates) always precedes Phase 2 (consolidate variants). | Phase 1 completed before Phase 2 starts. |
| **Provisioned copies**: same-folder-name mirrors under `.agents/skills/` or a harness home are provisioned artifacts — keep the repo source, flag the copy for re-provisioning, never edit the copy. | Provisioned copies flagged, never edited. |
| **Byte-identical or near-identical bodies**: merge into one; keep the more complete body, drop the rest. | More complete body retained; duplicates archived. |
| **Same `name:` in two folders**: one is stale; keep the more complete, delete the other. | Stale copy archived. |


## Steps

Run the steps in order. Steps 1 and 2 manage the skill lifecycle (active → stale → archived → purged). Steps 3–10 handle the consolidation workflow.

| Step | File | Purpose |
| ---- | ---- | ------- |
| 0 | [`references/step-0-overview.md`](references/step-0-overview.md) | Prune mode overview + classification rules |
| 1 | [`references/step-1-run.md`](references/step-1-run.md) | Run `sac run` once to apply automatic lifecycle transitions |
| 2 | [`references/step-2-prune.md`](references/step-2-prune.md) | Run `sac prune --apply` once to archive idle skills and purge old archives |
| 3 | [`references/step-3-confirm-root.md`](references/step-3-confirm-root.md) | Resolve the audit root |
| 4 | [`references/step-4-inventory.md`](references/step-4-inventory.md) | Catalog every skill and read frontmatter + body |
| 5 | [`references/step-5-group.md`](references/step-5-group.md) | Cluster skills by semantic scope |
| 6 | [`references/step-6-classify.md`](references/step-6-classify.md) | Label each cluster: duplicate, variant, shared tooling, or separate |
| 7 | [`references/step-7-dry-run.md`](references/step-7-dry-run.md) | Present the planned prune report; `--dry-run` stops here |
| 8 | [`references/step-8-snapshot.md`](references/step-8-snapshot.md) | Commit the rollback target |
| 9 | [`references/step-9-execute.md`](references/step-9-execute.md) | Merge clusters and archive dropped duplicates |
| 10 | [`references/step-10-verify-report.md`](references/step-10-verify-report.md) | Verify the merge and emit the final report |
