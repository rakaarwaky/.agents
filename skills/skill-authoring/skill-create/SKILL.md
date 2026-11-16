---
name: skill-create
description: "Authors a SKILL.md from a job description."
user-invocable: true
when-to-use: "Author a new SKILL.md for a capability that has no loaded skill: answer the ten core questions, draft, write, score, verify. Trigger terms: create skill, new skill, author skill. One skill per invocation; repairing an existing skill belongs to the sibling skill-improve. --dry-run stops after the report without writing."
argument-hint: "<job description> [--dry-run]"
---

# Skill Create

You author a new agent skill from a job description: `SKILL.md`, `references/`, and `templates/` where relevant. One skill per invocation.

**Purpose:** build a publishable skill that clears the quality gate, passes `sac lint`, invokes correctly, follows the shared body shape, and carries no duplicate content. Every fact lives once in a single authoritative home; flag and mode terms stay in lockstep across `SKILL.md` and its reference files.

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

The question set, rubric, score gate, and score block live in [`../skill-improve/references/step-14-tenq-standard.md`](../skill-improve/references/step-14-tenq-standard.md).

## Rules

Each row names the answer it covers; the question set, rubric, and gate live in [`../skill-improve/references/step-14-tenq-standard.md`](../skill-improve/references/step-14-tenq-standard.md).

| ID | Rule | Covers | Check |
|----|------|--------|-------|
| R1 | **Interface changes ripple.** The `argument-hint` plus every flag and safety-model mention must stay in lockstep. Grep the whole skill directory for each flag name and mode term before deciding an edit is done. | Whether | Grep every flag name and mode term across body + `references/`; zero stale references after the edit. |
| R2 | **One home per fact.** Each rule, value, or list lives in a single authoritative place. When an edit touches an existing copy elsewhere, make the change and report the duplication instead of silently rewriting. | How | No fact appears in two locations. |
| R3 | **No no-op sentences.** If a sentence does not change behavior, delete it or replace with a checkable criterion. | How | Every sentence changes behavior or is deleted. |
| R4 | **Set degrees of freedom.** High (text steps) for context-dependent work; medium (parameterized scripts) when a preferred pattern exists; low (exact commands) for fragile, strict-sequence operations. | How | DOF level chosen per step kind. |
| R5 | **Budget for permanent cost.** `description:` and `when-to-use:` are injected into the skill list every session; the body loads per use; `references/*.md` cost nothing until opened. Keep the two trigger fields non-overlapping. | When & where | `description:` and `when-to-use:` non-overlapping; task-conditional content moved out of body into references. |
| R6 | **Mandatory frontmatter.** Exactly four keys: `name`, `description`, `when-to-use`, `argument-hint`; every other key is optional. | When & where | Four mandatory keys present. |
| R7 | **Frontmatter semantics.** `description:` = WHAT + WHEN + trigger terms, third person. Trigger overflow goes in `when-to-use:`, never a `triggers:` key. | When & where | `description:` covers WHAT + WHEN; no `triggers:` key. |
| R8 | **YAML hygiene.** Quote values containing `: ` or indicator characters. Unclosed frontmatter makes the parser silently drop `description` and `when-to-use`. | When & where | Values with `: ` quoted; second `---` verified immediately before `# Title`. |
| R9 | **Structure.** One `SKILL.md` per `<category>/<skill>/SKILL.md`. Body ~100–200 lines; detail in `references/*.md`; non-trivial logic in `scripts/<file>`. | How | Body ~100–200 lines; every reference linked from SKILL.md. |
| R10 | **Mandatory body shape.** Exactly three sections: `# Title`, `## Rules`, `## Routing`. Stop conditions are Rules bullets, not their own heading. The rules table is always-on content and belongs in the SKILL.md body — never extract it to a separate reference file; a rules reference forces a second load to recover the governing rules, defeating the purpose of always-on body rules. | How | `grep ^## ` returns exactly `## Rules` and `## Routing`; no separate rules reference file exists. |
| R11 | **Templates are the source of truth.** `template/skill.md` is the canonical skeleton; `template/reference.md` the canonical reference shape. | How | Create steps copy from template; no inline restatements. |
| R12 | **Tracked catalog.** `sac catalog --build` regenerates `catalog.json`. Rebuild after any frontmatter change. | What kind | `catalog.json` rebuilt after every frontmatter change. |
| R13 | **Safety model.** All steps run autonomously by default. `--dry-run` generates the full report and stops before any snapshot or execute. Destructive actions go to `_archive/` first. | Whether | All steps proceed without confirmation; `--dry-run` stops before write. |
| R14 | **Staging discipline.** Use explicit top-level paths; never `git add -A`. Verify staged set with `git diff --cached --name-only` before committing. | By what means | Staged set is exactly task files before commit. |
| R15 | **Lane delegation for coding skills.** Hermes orchestrates; Grok Build implements inside Orca worktrees. Two lanes: `references/hermes/` and `references/grok/`. | By what means | Hermes drops one brief per worktree; verifies inside worktree path. |
| R16 | **Rollback.** Snapshot SHA or `git reset --hard <sha>` is the undo path. A run that cannot commit falls back to report-only. | How come | Snapshot SHA recorded; `git reset --hard <sha>` used for rollback. |
| R17 | **Parallel agents.** Re-read at least one touched file after writes to confirm content is on disk. Keep commits scoped to task files. | How come | On-disk state re-verified; commits scoped to task files only. |
| R18 | **`mkdir -p` before `git mv`.** Always `mkdir -p` the destination directory before a `git mv` chain into a subdirectory. | How come | `mkdir -p` runs before every `git mv` into a subdirectory. |
| R19 | **Patch escape-drift.** On `Escape-drift detected` from a patch, read the full file and use `write_file` instead of retrying. | How come | Full file read and `write_file` on escape-drift failure. |
| R20 | **Verify pack roots.** `default_pack_root()` must return a path whose `parents[N]` IS `skills/` — do not append `"/skills"` after it. | How come | `default_pack_root().name == "skills"`; `sac catalog --build` prints the correct path. |
| R21 | **Success metric is checkable.** State the objective "done" criterion in Rules or the owning step — a concrete check (`sac lint` passes, body matches `template/skill.md`, catalog rebuilt) — never a subjective adjective ("clean", "good", "complete"). | What & why | Every skill's done-criterion is a command or grep probe; no subjective adjective remains. |
| R22 | **Route branches to the owning step.** At a decision point, resolve to the one step file or template that owns the answer; a `Whether` branch is a Routing-table row, not a Rules restatement. When the decision is unclear, route to the owning step instead of inventing a new branch in Rules. | Whether | Every branch has one owner: a Routing row or a step; Rules carries no branch a step can resolve itself. |
| R23 | **Name the fallback, not "fix the error".** When a run can fail (writer rejects frontmatter, `sac lint` unavailable, escape-drift on patch), name the diagnosis + recovery path in the owning step — fallback to `write_file`, fallback to the grep probe, fallback to report-only — never a bare "fix it". | How come | Each failure mode's step names the trigger, the cause, and the concrete recovery command. |
| R24 | **Dangling refs rot fast.** Every sibling mention, cross-skill link, and reference filename must resolve to a file or skill that exists. After any rename or move, grep the whole skill directory for the old name and fix every hit before the edit is done. | How | `audit_probes.py <SKILL_DIR>` reports zero dangling links and zero retired filenames. |
| R25 | **Answers precede prose.** Answer all ten core questions in scratch notes and score the draft before writing any file (step 2). One skill = one deliverable; a job with two WHATs is split, not drafted. Each answer lands in exactly one home per the placement map in the standard. | What & why; How | Ten answers in scratch notes, each with a named home; every default used is logged `assumed` in the report. |
| R26 | **Quality gate is hard.** The written skill must pass the gate in the standard (step 7). Below it: run the patch cycle, re-score, and when the budget is exhausted report `Gate: FAIL` with the gap list — never announce the skill as ready. | What & why | Report carries the score block: total, verdict, cycles used, remaining gaps. |
| R27 | **Audience and tone.** Output audience: skill authors maintaining this pack. Body and references in English, imperative mood, third-person `description:`; no marketing adjectives. The chat report follows the user's language. | Who | Body has no subjective quality adjectives; `description:` is third person. |
| R28 | **Run ceilings.** One skill per invocation. Writes are confined to `<SKILL_DIR>/**`, a new category's `DESCRIPTION.md`, and `skills/catalog.json`. Maximum 2 self-repair iterations after a failed check, plus the gate's patch-cycle budget; then stop and report. Forbidden: editing sibling skills, adding dependencies. | How far | `git diff --cached --name-only` lists only those paths; iteration count in the report ≤ 2. |
| R29 | **Report shape.** Every run ends with one report: changed-files table, check results (`sac lint`, probes), the score block, the gate verdict, and every `assumed` default. `--dry-run` emits the same report from the draft and writes nothing. | What kind | Report contains all five parts; dry-run report is labelled `source: draft`. |

## Routing

| Step | File | Purpose |
| ---- | ---- | ------- |
| 0 | [`references/step-0-overview.md`](references/step-0-overview.md) | Create mode overview |
| 1 | [`references/step-1-gather.md`](references/step-1-gather.md) | Gather name, category, scope, and job description |
| 2 | [`references/step-2-drafting.md`](references/step-2-drafting.md) | Answer and score the ten core questions before writing; split a two-WHAT job |
| 3 | [`references/step-3-review.md`](references/step-3-review.md) | Reviewer loop on the `$DRAFT_DIR` draft; write to real skills directory on 0 issues |
| 4 | [`references/step-4-write.md`](references/step-4-write.md) | Create the directory, pick the writer path, write SKILL.md and supporting files |
| 5 | [`references/step-5-verify.md`](references/step-5-verify.md) | Score the artifact, run probes, enforce the gate, and verify/report. |