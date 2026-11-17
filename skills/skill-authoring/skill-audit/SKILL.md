---
name: skill-audit
description: "Repairs all sac findings across the skill library, then commits and pushes the result."
user-invocable: true
when-to-use: "Run when the user asks to clear every sac lint violation of the skills pack, make sac lint exit 0, fix all pack lint issues, or repair lint findings and push. Trigger terms: skill audit, lint the pack, fix lint violations, audit skills. Authoring one new skill belongs to skill-create; repairing one skill's body against the ten-question quality gate belongs to skill-improve; consolidating duplicate skill folders into one belongs to skill-prune. This skill audits the skills pack through to a clean lint, a rebuilt catalog, and a push."
argument-hint: "[--dry-run] [--category <name>]"
---

# Skill Audit

You audit the skills pack with `sac lint`, repair every flagged violation at its owner file, rebuild the catalog, and push the result — one closed loop from scan to pushed commit. `--dry-run` reports the plan and the issues and stops before any write.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **One home per fact.** Each lint class, fix recipe, and command lives in exactly one step file. When a fix appears in two step files, keep the owning step and point at it from the other. | `grep -rn "<fix term>" references/` returns one step file |
| R2 | **No no-op sentences.** If a sentence does not change behavior, delete it or replace with a checkable criterion. | Every sentence names a command, path, or condition |
| R3 | **Set degrees of freedom.** Low: exact `sac` and `git` commands in every step, because the pack gate is fragile and sequence-sensitive. | Every step carries a copy-paste command block |
| R4 | **Budget for permanent cost.** Keep `description:` and `when-to-use:` non-overlapping; per-class fix detail lives in `references/`, never in the body. | `description:` and `when-to-use:` share no phrase |
| R5 | **Mandatory frontmatter.** Exactly four keys: `name`, `description`, `when-to-use`, `argument-hint`. Every other key is optional. | Four mandatory keys present |
| R6 | **Frontmatter semantics.** `description:` = WHAT + WHEN in third person; trigger overflow goes in `when-to-use:`, never a `triggers:` key. | No `triggers:` key; `description:` third person |
| R7 | **YAML hygiene.** Quote values containing `: ` or indicator characters. The second `---` sits immediately before `# Title`. | Frontmatter parses; `sac read skill-audit` prints both trigger fields |
| R8 | **Structure.** One `SKILL.md` per `<category>/<skill>/SKILL.md`; body kept lean — the pack's skills run ~60–75 lines; detail lives in `references/step-<N>-<name>.md`. | `wc -l SKILL.md` ≤ 80; body shape probe in step-1 |
| R9 | **Mandatory body shape.** Exactly `# Title`, `## Rules`, `## Routing` — no other `##` headings. The rules table stays in the body; never extract it to a reference. | `grep '^## ' SKILL.md` returns exactly `## Rules` and `## Routing` |
| R10 | **Tracked catalog.** `sac catalog --build` regenerates `skills/catalog.json`. Rebuild after every frontmatter change and before staging. | `sac catalog --build` exits 0; `sac catalog --check` exits 0 |
| R11 | **Audit standard.** `sac lint` is the mechanical gate; `references/step-2-fix.md` holds the class-to-fix map. Every flagged issue is fixed at its owner. | `sac lint` exits 0 and prints zero issue lines |
| R12 | **Tools and forbidden commands.** Mandatory: `sac lint` (plain and `--category <name>`), `sac catalog --build` and `--check`, `sac read`, `sac move`, `sac archive`, `sac create`, `git` (including `git mv`), `grep`, `ls`, `mkdir -p`. `sac discover` is broken in this pack (returns no matches, prints no paths) — read paths from `sac lint` output or `skills/catalog.json`. Forbidden: `git add -A`, `git push --force`, `git reset --hard` outside the documented rollback, installing dependencies, editing `modules/`, `vendor/`, `workflows/`, `personas/`, `roles/`, `develop/`, `config/`. | Staged set is task files + `catalog.json`; `git diff --cached --name-only` shows no forbidden path |
| R13 | **Safety model.** All steps run autonomously by default. `--dry-run` stops after the plan and the issue list, before any file edit, `sac archive`, catalog rebuild, or push — every step that writes marks what it skips (steps 0–1 are read-only). | `--dry-run` writes nothing; `git status` unchanged after a dry run |
| R14 | **Success metric is a command.** The run is done only when `sac lint` exits 0 and prints zero issue lines, `sac catalog --check` exits 0, `git status --porcelain` shows no modified or staged tracked file outside the commit, and `git rev-parse @{u}` equals local `HEAD`. An untracked `skills/.archive/` tree left by an `sac archive` fix is reported in the audit report, not a failure. | Commands exit 0; no subjective adjective in the report |
| R15 | **Staging discipline.** Stage explicit top-level paths; never `git add -A`. Verify with `git diff --cached --name-only` before committing. | Staged set is exactly the touched skills + `skills/catalog.json` |
| R16 | **Scope and iteration ceilings.** One pack per invocation; maximum 10 repair rounds (step-3); maximum 2 self-repair iterations, where a self-repair iteration is one re-run of the audit's own process after a process failure such as a failed commit or push (step-4.5); one push. Forbidden: editing a skill outside the flagged set, deleting a skill directory without archiving it first, pushing to a branch other than the pack default branch resolved in step-1. | Round count in the report ≤ 10; self-repair count ≤ 2; `git show --stat <sha>` lists only touched skills + `catalog.json` |
| R17 | **Rollback.** Record the pre-run SHA with `git rev-parse HEAD` in step-1. A run that cannot commit falls back to report-only; a run that broke a skill rolls back with `git reset --hard <SHA>`. | Snapshot SHA in the report; rollback command named in step-5 |
| R18 | **Parallel-agent safety.** Read `git status --short` and `git log --oneline -5` before the run. If `git status --short` is non-empty before the run, report the pre-existing files and stop instead of committing them. After step-1, stop only when changes appear outside the audit's own task set (step-3.2). | Pre-run `git status --short` recorded in the report |
| R19 | **Audience and tone.** Output audience: skill authors maintaining this pack. Body and references in English, imperative mood, third-person `description:`; no marketing adjectives. The chat report follows the user's language. | Body has no subjective quality adjectives; `description:` is third person |
| R20 | **Report shape.** Every run ends with one report: changed-files table, `sac lint` before/after issue counts and exit codes, the score block, the gate verdict, and every `assumed` default. `--dry-run` emits the same report and writes nothing. | Report contains all five parts |
| R21 | **Trigger-field hygiene and reference linking.** The audit holds every audited skill to the same frontmatter and reference standard it audits: `description:` and `when-to-use:` share no phrase, and every file under a skill's `references/` appears as a link in its `SKILL.md` Routing table. | No shared bigram between `description:` and `when-to-use:`; `grep -q '<file>' SKILL.md` succeeds per reference file |

## Routing

| Step | File | Purpose |
|------|------|---------|
| 0 | [`references/step-0-overview.md`](references/step-0-overview.md) | Run overview, pack-root resolution, issue-class taxonomy |
| 1 | [`references/step-1-scan.md`](references/step-1-scan.md) | Record pre-state, run `sac lint`, parse and bucket every issue |
| 2 | [`references/step-2-fix.md`](references/step-2-fix.md) | Per-class fix recipes and branch table |
| 3 | [`references/step-3-loop.md`](references/step-3-loop.md) | Repair loop until `sac lint` exits 0, with ceilings |
| 4 | [`references/step-4-commit-push.md`](references/step-4-commit-push.md) | Rebuild catalog, stage explicit paths, commit, push, verify remote head |
| 5 | [`references/step-5-verify-report.md`](references/step-5-verify-report.md) | Verify gate, score block, report, fallback table |