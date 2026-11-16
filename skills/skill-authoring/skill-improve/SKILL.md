---
name: skill-improve
description: "Audits and repairs a SKILL.md against lint and quality gates."
user-invocable: true
when-to-use: "Audit and repair an existing skill in one pass: structure, frontmatter, body shape, dangling refs, pattern-B variants, and the quality score gate (ten core questions). Trigger terms: improve skill, audit skill, perbaiki skill, skor kualitas, skill tidak trigger. Accepts one skill, a category tree, the skills root, or an explicit list. Authoring a brand-new skill belongs to the sibling skill-create. --dry-run stops after the report without writing."
argument-hint: "<skill path> [--dry-run]"
---

# Skill Improve

You audit and repair an existing `SKILL.md` against the shared lint standard and the ten core questions in one pass. One skill (or a category tree, or the whole skills root) per invocation.

**Purpose:** make the target skill follow the body shape, pass `sac lint`, clear the quality gate, and satisfy the pre-publish checklist — without losing the skill's intent.

Every skill must answer ten core questions so an agent can run it without guessing:
- What & why — deliverable, kind, why, purpose
- When & where — when, time, where
- Who — who, whom, whose, with whom
- From where — from where
- By what means — by what means, which
- How — how, in what way, about what
- How far — how far, how many/much, how long, how old, how often
- Whether — whether
- What kind — what kind, to where
- How come — how come

The question set, rubric, score gate, and score block live in [`references/step-14-tenq-standard.md`](references/step-14-tenq-standard.md).

## Rules

Each row names the answer it answers or enforces; the question set, rubric, and gate live in [`references/step-14-tenq-standard.md`](references/step-14-tenq-standard.md).

| ID | Rule | Covers | Check |
|----|------|--------|-------|
| R1 | **Interface changes ripple.** Grep the whole skill directory for each flag name and mode term; a retired flag that still governs a step file silently re-imposes old behavior. | Whether | Zero stale references after the edit. |
| R2 | **One home per fact.** Each rule, value, or list lives in a single authoritative place; when an edit touches a copy elsewhere, report the duplication instead of silently rewriting. | How | No fact appears in two locations. |
| R3 | **Splitting language monoliths.** When a Pattern B pipeline carries per-language monolith references and the user asks for `step-<N>[a\|b\|c]` variant naming: find the phase boundary and split there; shared preamble stays with step 1; tails move to the later step; old monolith filenames are removed. | How | Phase boundary located; old monolith filenames removed from tree. |
| R4 | **No no-op sentences.** If a sentence does not change behavior, delete it or replace with a checkable criterion. | How | Every sentence changes behavior or is deleted. |
| R5 | **Solve the class, not the instance.** Fix bad output where the fact is owned, not with a downstream check. Check every generalization against at least two concrete instances. | How | Every fix located at the fact's owner. |
| R6 | **Set degrees of freedom.** High for context-dependent work; medium for parameterized scripts; low for fragile strict-sequence operations. | How | DOF level chosen per step kind. |
| R7 | **Budget for permanent cost.** Keep trigger fields non-overlapping; move task-conditional content out of body into references. | When & where | `description:` and `when-to-use:` non-overlapping. |
| R8 | **Mandatory frontmatter.** Exactly four keys: `name`, `description`, `when-to-use`, `argument-hint`. | When & where | Four mandatory keys present. |
| R9 | **Frontmatter semantics.** `description:` = WHAT + WHEN + trigger terms, third person. No `triggers:` key. | When & where | No `triggers:` key present. |
| R10 | **YAML hygiene.** Quote values containing `: ` or indicator characters. Verify the second `---` sits immediately before `# Title`. | When & where | Second `---` verified; bad quoting fixed. |
| R11 | **Grok Build parser limits.** `name` ≤ 64 chars; `description` and `when-to-use` ≤ 1,024 chars; top-level `version:`, `triggers:`, `entry_points:` are ignored. | When & where | Size and key checks pass. |
| R12 | **Structure.** One `SKILL.md` per `<category>/<skill>/SKILL.md`; body ~100–200 lines; detail in `references/*.md`. | How | Body size and structure verified. |
| R13 | **Mandatory body shape.** Exactly `# Title`, `## Rules`, `## Routing`. No other `##` headings in the body. The rules table is always-on content and belongs in the SKILL.md body — never extract it to a separate reference file; a rules reference forces a second load to recover the governing rules, defeating the purpose of always-on body rules. | How | `grep ^## ` returns exactly `## Rules` and `## Routing`; no separate rules reference file exists. |
| R14 | **Audit standard.** `sac lint` is the mechanical gate; `references/step-4-validator-catalog.md` holds the full rule catalog. Every flagged issue is fixed. | What & why | `sac lint` passes; every flagged issue fixed. |
| R15 | **Tracked catalog.** `sac catalog --build` regenerates `catalog.json`. Rebuild after any frontmatter change. | What kind | `catalog.json` rebuilt after every frontmatter change. |
| R16 | **Rollback.** Snapshot SHA or `git reset --hard <sha>` is the undo path. A run that cannot commit falls back to report-only. | How come | Snapshot SHA recorded; rollback path documented. |
| R17 | **Safety model.** All steps run autonomously by default. `--dry-run` generates the full report and stops before any write. | Whether | All steps proceed without confirmation; `--dry-run` stops before write. |
| R18 | **Parallel agents.** Re-read at least one touched file after writes. Keep commits scoped to task files; never `git add -A`. | How come | On-disk state re-verified; commits scoped to task files. |
| R19 | **Staging discipline.** Use explicit top-level paths; verify staged set with `git diff --cached --name-only` before committing. | By what means | Staged set is exactly task files before commit. |
| R20 | **Lane delegation for coding skills.** Hermes orchestrates; Grok Build implements in Orca worktrees. | By what means | Two lanes present for coding skills. |
| R21 | **`mkdir -p` before `git mv`.** Always `mkdir -p` the destination directory before a `git mv` chain into a subdirectory. | How come | `mkdir -p` runs before every `git mv` into a subdirectory. |
| R22 | **Patch escape-drift.** On `Escape-drift detected`, read the full file and use `write_file` instead of retrying. | How come | Full file read and `write_file` on escape-drift. |
| R23 | **Verify pack roots.** `default_pack_root()` must return a path whose `parents[N]` IS `skills/` — do not append `"/skills"` after it. | How come | `default_pack_root().name == "skills"`. |
| R24 | **Objective success metric.** A target skill's completion criteria must be machine-verifiable (`sac lint` passes, `grep` matches exact heading, `cargo`/`pytest` exits 0). Replace subjective criteria ("high quality", "clean code", "well structured"). | What & why | No subjective quality adjectives remain in Rules or step files. |
| R25 | **Scope & iteration ceilings.** Every target skill must state explicit scope ceilings (max files touched, max iterations before stopping, and forbidden actions) so agents do not drift or loop. | How far | Scope boundaries and stop conditions are present in the target skill. |
| R26 | **Branching & failure fallback.** Decision branches map to `IF condition -> action (or owned step)`. Failure fallbacks name the exact error/cause and concrete recovery path. | Whether; How come | No "fix if error" without named cause and recovery path. |
| R27 | **Dangling refs rot fast.** Every sibling mention, cross-skill link, and reference filename must resolve to a file or skill that exists. After any rename or move, grep the whole skill directory for the old name and fix every hit before the edit is done. | How | `scripts/audit_probes.py <target>` reports zero dangling links and zero retired filenames. |
| R28 | **Quality audit is part of every pass.** Score the target against `references/step-14-tenq-standard.md` before verify and commit (step 12, point 10). A pass with no score block is incomplete, whatever lint says. | What & why | One score block per target skill exists in the run report. |
| R29 | **Quality gate is hard.** Below the gate in the standard, run the patch cycle in `references/step-15-tenq-diagnosis.md` and re-score; when the budget is exhausted, report `Gate: FAIL` with the gap list and never call the target done or production-ready. | What & why | Report carries total, verdict, cycles used, remaining gaps; no "done" claim on FAIL. |
| R30 | **Audience and tone.** Output audience: skill authors maintaining this pack. Body and references in English, imperative mood, third-person `description:`; no marketing adjectives. The chat report follows the user's language. | Who | Body has no subjective quality adjectives; `description:` is third person. |
| R31 | **Run ceilings.** Writes are confined to the resolved target set's paths and `skills/catalog.json`. Maximum 2 self-repair iterations per failing check, plus the gate's patch-cycle budget per skill; then stop and report. Forbidden: editing skills outside the resolved scope, deleting content without archiving it first. | How far | `git diff --cached --name-only` is a subset of target paths + `catalog.json`. |
| R32 | **Report shape.** Every run ends with one report per target: changed-files table, lint and probe results, the score block, the gate verdict, and out-of-scope findings. `--dry-run` emits the same report and writes nothing. | What kind | Report contains all five parts, one block per target. |

## Routing

| Step | File | Purpose |
| ---- | ---- | ------- |
| 0 | [`references/step-0-overview.md`](references/step-0-overview.md) | Improve mode overview |
| 1 | [`references/step-1-scope.md`](references/step-1-scope.md) | Resolve the target skill set from the path |
| 2 | [`references/step-2-body-format.md`](references/step-2-body-format.md) | Enforce `# Title` / `## Rules` / `## Routing` shape |
| 3 | [`references/step-3-frontmatter-keys.md`](references/step-3-frontmatter-keys.md) | Full frontmatter key reference |
| 4 | [`references/step-4-validator-catalog.md`](references/step-4-validator-catalog.md) | What `sac lint` enforces, rule by rule |
| 5 | [`references/step-5-naming-detail.md`](references/step-5-naming-detail.md) | Naming conventions and rename mechanics |
| 6 | [`references/step-6-description-detail.md`](references/step-6-description-detail.md) | Description writing rules |
| 7 | [`references/step-7-content-detail.md`](references/step-7-content-detail.md) | Body content rules |
| 8 | [`references/step-8-prepublish-checklist.md`](references/step-8-prepublish-checklist.md) | Pre-publish checklist |
| 9 | [`references/step-9-category-placement.md`](references/step-9-category-placement.md) | Category-placement audit |
| 10 | [`references/step-10-information-distribution.md`](references/step-10-information-distribution.md) | Information-distribution test |
| 11 | [`references/step-11-reference-pattern.md`](references/step-11-reference-pattern.md) | Reference-pattern decision (Patterns A/B/C) |
| 12 | [`references/step-12-apply.md`](references/step-12-apply.md) | Apply the edit recipe; quality gate, then lint |
| 13 | [`references/step-13-pattern-b-variants.md`](references/step-13-pattern-b-variants.md) | Restructure references into `step-<N>[a\|b\|c]` variants |
| 14 | [`references/step-14-tenq-standard.md`](references/step-14-tenq-standard.md) | The ten questions, 0–2 rubric, gate arithmetic, score block |
| 15 | [`references/step-15-tenq-diagnosis.md`](references/step-15-tenq-diagnosis.md) | Symptom → question map and the patch cycle |