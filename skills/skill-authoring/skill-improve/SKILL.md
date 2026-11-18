---
name: skill-improve
description: "Audits and repairs a SKILL.md against lint and quality gates."
user-invocable: true
when-to-use: "Audit and repair an existing skill in one pass: structure, frontmatter, body shape, dangling refs, pattern-B variants, and the quality score gate (ten core questions). Trigger terms: improve skill, audit skill. Accepts one skill, a category tree, the skills root, or an explicit list. Authoring a brand-new skill belongs to the sibling skill-create. --dry-run stops after the report without writing."
argument-hint: "<skill path> [--dry-run]"
---

# Skill Improve

You audit and repair an existing `SKILL.md` against the shared lint standard and the ten core questions in one pass. One skill (or a category tree, or the whole skills root) per invocation.

**Purpose:** make the target skill follow the body shape, pass `sac lint`, clear the quality gate, and satisfy the pre-publish checklist — without losing the skill's intent.

The ten-question rubric, the score block, and the gate live in [`references/step-4-apply.md`](references/step-4-apply.md); the score block template and the ten-question rubric live in [`references/step-5-verify.md`](references/step-5-verify.md).

## Rules

Each row names the answer it answers or enforces; the question set, rubric, and gate live in [`references/step-4-apply.md`](references/step-4-apply.md).

| ID | Rule | Check |
|----|------|-------|
| R1 | **Interface changes ripple.** Grep the whole skill directory for each flag name and mode term; a retired flag that still governs a step file silently re-imposes old behavior. | Zero stale references after the edit. |
| R2 | **One home per fact.** Each rule, value, or list lives in a single authoritative place; when an edit touches a copy elsewhere, report the duplication instead of silently rewriting. | No fact appears in two locations. |
| R3 | **Splitting language monoliths.** When a Pattern B pipeline carries per-language monolith references and the user asks for `step-<N>[a\|b\|c]` variant naming: find the phase boundary and split there; shared preamble stays with step 1; tails move to the later step; old monolith filenames are removed. | Phase boundary located; old monolith filenames removed from tree. |
| R4 | **No no-op sentences.** If a sentence does not change behavior, delete it or replace with a checkable criterion. | Every sentence changes behavior or is deleted. |
| R5 | **Solve the class, not the instance.** Fix bad output where the fact is owned, not with a downstream check. Check every generalization against at least two concrete instances. | Every fix located at the fact's owner. |
| R6 | **Set degrees of freedom.** High for context-dependent work; medium for parameterized scripts; low for fragile strict-sequence operations. | DOF level chosen per step kind. |
| R7 | **Budget for permanent cost.** Keep trigger fields non-overlapping; move task-conditional content out of body into references. | `description:` and `when-to-use:` non-overlapping. |
| R8 | **Mandatory frontmatter.** Exactly four keys: `name`, `description`, `when-to-use`, `argument-hint`. `argument-hint` names only the target path and operational flags; omit redundant path flags when artifacts resolve deterministically to `~/.agents/develop/<namarepo>/<skill>/`. | Four mandatory keys present; no redundant path flags. |
| R9 | **Frontmatter semantics.** `description:` = WHAT + WHEN + trigger terms, third person. No `triggers:` key. | No `triggers:` key present. |
| R10 | **YAML hygiene.** Quote values containing `: ` or indicator characters. Verify the second `---` sits immediately before `# Title`. | Second `---` verified; bad quoting fixed. |
| R11 | **Grok Build parser limits.** `name` ≤ 64 chars; `description` and `when-to-use` ≤ 1,024 chars; top-level `version:`, `triggers:`, `entry_points:` are ignored. | Size and key checks pass. |
| R12 | **Structure.** One `SKILL.md` per `<category>/<skill>/SKILL.md`; body ~100–200 lines; detail in `references/*.md`. | Body size and structure verified. |
| R13 | **Mandatory body shape.** Exactly `# Title`, `## Rules`, `## Routing`. No other headings (`##` or `###`) in the body. For multi-lane skills, unify routing into a single table with a `Lane` column or use bold headers, never `###` headings. The rules table is always-on content and belongs in the SKILL.md body — never extract it to a separate reference file; a rules reference forces a second load to recover the governing rules, defeating the purpose of always-on body rules. | `grep -n '^#' <SKILL.md>` returns only `# Title` and exactly `## Rules`, `## Routing`; zero `###` subheadings. |
| R14 | **Audit standard.** `sac lint` is the mechanical gate; `references/step-1-format.md` holds the full rule catalog. Every flagged issue is fixed. | `sac lint` passes; every flagged issue fixed. |
| R15 | **Tracked catalog.** `sac catalog --build` regenerates `catalog.json`. Rebuild after any frontmatter change — even when the edit only removes extra keys the catalog doesn't store (e.g. `disable-model-invocation`, `created_by`), which can produce zero diff; do not skip the rebuild because nothing changed. | `catalog.json` rebuilt after every frontmatter change. |
| R16 | **Rollback.** Snapshot SHA or `git reset --hard <sha>` is the undo path. A run that cannot commit falls back to report-only. | Snapshot SHA recorded; rollback path documented. |
| R17 | **Safety model.** All steps run autonomously by default. `--dry-run` generates the full report and stops before any write. | All steps proceed without confirmation; `--dry-run` stops before write. |
| R18 | **Parallel agents.** Re-read at least one touched file after writes. Keep commits scoped to task files; never `git add -A`. | On-disk state re-verified; commits scoped to task files. |
| R19 | **Staging discipline.** Use explicit top-level paths; verify staged set with `git diff --cached --name-only` before committing. The repo often carries a pre-staged set from prior work, and a plain `git commit` commits the whole index — not just what you `git add`-ed — so unrelated pre-staged changes silently ride into your commit. Scope with `git commit -m '<msg>' -- <your paths>` (partial-commit mode — `--only` is an internal git flag, not a user-facing one) to commit exactly your files and leave the pre-existing index untouched; confirm with `git show --stat <sha>` that the commit lists only your task files. If it swept in foreign staged changes, recover with `git checkout HEAD~1 -- <foreign paths>` then `git commit --amend --no-edit`. | `git show --stat <sha>` lists exactly task files; no unrelated staged change in the commit. |
| R20 | **Lane delegation for coding skills.** Hermes orchestrates; Grok Build implements in Orca worktrees. | Two lanes present for coding skills. |
| R21 | **`mkdir -p` before `git mv`.** Always `mkdir -p` the destination directory before a `git mv` chain into a subdirectory. | `mkdir -p` runs before every `git mv` into a subdirectory. |
| R22 | **Patch escape-drift.** On `Escape-drift detected`, read the full file and use `write_file` instead of retrying. | Full file read and `write_file` on escape-drift. |
| R23 | **Verify pack roots.** `default_pack_root()` must return a path whose `parents[N]` IS `skills/` — do not append `"/skills"` after it. | `default_pack_root().name == "skills"`. |
| R24 | **Objective success metric.** A target skill's completion criteria must be machine-verifiable (`sac lint` passes, `grep` matches exact heading, `cargo`/`pytest` exits 0). Replace subjective criteria ("high quality", "clean code", "well structured"). | No subjective quality adjectives remain in Rules or step files. |
| R25 | **Scope & iteration ceilings.** Every target skill must state explicit scope ceilings (max files touched, max iterations before stopping, and forbidden actions) so agents do not drift or loop. | Scope boundaries and stop conditions are present in the target skill. |
| R26 | **Branching & failure fallback.** Decision branches map to `IF condition -> action (or owned step)`. Failure fallbacks name the exact error/cause and concrete recovery path. | No "fix if error" without named cause and recovery path. |
| R27 | **Dangling refs rot fast.** Every sibling mention, cross-skill link, and reference filename must resolve to a file or skill that exists. After any rename or move, grep the whole skill directory for the old name and fix every hit before the edit is done. | `grep -r "old-name"` reports zero dangling links and zero retired filenames. |
| R28 | **Quality audit is part of every pass.** Score the target against `references/step-4-apply.md` before verify and commit (step 4, point 10). A pass with no score block is incomplete, whatever lint says. | One score block per target skill exists in the run report. |
| R29 | **Quality gate is hard.** Below the gate in `references/step-4-apply.md`, run the patch cycle and re-score; when the budget is exhausted, report `Gate: FAIL` with the gap list and never call the target done or production-ready. | Report carries total, verdict, cycles used, remaining gaps; no "done" claim on FAIL. |
| R30 | **Audience and tone.** Output audience: skill authors maintaining this pack. Body and references in English, imperative mood, third-person `description:`; no marketing adjectives. The chat report follows the user's language. | Body has no subjective quality adjectives; `description:` is third person. |
| R31 | **Run ceilings.** Writes are confined to the resolved target set's paths and `skills/catalog.json`. Maximum 2 self-repair iterations per failing check, plus the gate's patch-cycle budget per skill; then stop and report. Forbidden: editing skills outside the resolved scope, deleting content without archiving it first. | `git diff --cached --name-only` is a subset of target paths + `catalog.json`. |
| R32 | **Report shape.** Every run ends with one report per target: changed-files table, lint and probe results, the score block, the gate verdict, and out-of-scope findings. `--dry-run` emits the same report and writes nothing. | Report contains all five parts, one block per target. |

## Routing

| Step | File | Purpose |
|------|------|---------|
| 0 | [`references/step-0-overview.md`](references/step-0-overview.md) | Improve mode overview + resolve target scope |
| 1 | [`references/step-1-format.md`](references/step-1-format.md) | Body shape, frontmatter keys, lint rule catalog |
| 2 | [`references/step-2-detail.md`](references/step-2-detail.md) | Naming, description, and content detail rules |
| 3 | [`references/step-3-publish.md`](references/step-3-publish.md) | Pre-publish checklist, category placement, information distribution, reference pattern |
| 4 | [`references/step-4-apply.md`](references/step-4-apply.md) | Apply recipe, Pattern A consolidation, Pattern B variants, tenQ standard and diagnosis |
| 5 | [`references/step-5-verify.md`](references/step-5-verify.md) | TenQ standard, quality gate, verify and report |