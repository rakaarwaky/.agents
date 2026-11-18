---
name: skill-rename
description: "Use to rename a Hermes skill and propagate every reference."
when-to-use: "Use when asked to rename a skill, re-slug its folder, or diagnose why a skill's slash command is missing. A skill's frontmatter name IS its slash command, so a rename touches more than the folder."
argument-hint: "<old-slug> <new-slug>"
---

# Rename a Hermes skill

A skill's frontmatter `name` is its slash command. Renaming = change the folder, the `name` field, and every place that names the skill (slash refs, sibling cross-refs, registry, tool alias maps), then verify nothing still points at the old name.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **Gate 0 before slug commit.** Check the new slug against `hermes_cli/commands.py` `COMMAND_REGISTRY` before renaming; a built-in collision silently strips the slash command — the built-in wins and the skill becomes reachable only via `/skill <slug>`. If it collides, pick a different slug (e.g. `plan` collides with built-in `/plan`; `planner` does not). | `resolve_command('<new-slug>')` returns `None`; or grep the registry returns zero hits. |
| R2 | **Rename the directory first.** `git mv` the skill folder to the new slug; the frontmatter `name` and heading are updated in `SKILL.md` after the move. | `ls skills/<category>/<new-slug>/SKILL.md` exists; old directory gone. |
| R3 | **Frontmatter `name` matches directory.** After the move, `SKILL.md` `name:` equals the new directory name and the `#` heading reflects the new name. | `sac lint` reports no `name-mismatch`. |
| R4 | **Change skill-NAME references; rename domain-CONCEPT words only when explicitly requested.** By default keep the skill's own output terminology (documents, IDs, personas such as `design-document` / `design-doc-*` / `DESIGN_ID`) — only the skill identity and slash command change. If the user explicitly asks to rename domain terms, rename the persona files (`<skill>-writer.toml`, `<skill>-reviewer.toml`) and artifact name tokens alongside the slug. | `grep -r` old slug hits only identity references unless domain rename was requested; persona files follow the slug when renamed. |
| R5 | **Keep a backward-compat alias.** Add the new slug as an alias resolving to the canonical target; keep the old slug as a legacy alias so pre-existing invocations still resolve. Mark it legacy in a comment. | Alias map contains both new and old slugs; legacy comment present. |
| R6 | **Sibling cross-refs updated.** Grep the whole skills tree for the old slug and `/<old>`; update refs in OTHER skills that call this one (go-back pointers, sibling-skill lists, trigger text). | `grep -r '<old-slug>'` of the skills tree returns zero non-legacy hits. |
| R7 | **Registry rebuilt.** Update the `skills/catalog.json` entry name plus any description or when-to-use that names the skill or `/<old>`; run `sac catalog --build`. | `sac read <new-slug>` resolves; catalog reflects new frontmatter. |
| R8 | **Tool alias maps updated.** Update alias maps, subdir aliases, doc lists of which skills use the tool, run-summary docstrings, and argparse `choices=` lists that enumerate accepted skill-name subdirs — add the new slug and keep the legacy alias (do not replace in place, which drops the old choice). | Tooling resolves the new slug; legacy alias still resolves; `choices=` lists contain both. |
| R9 | **Scope and iteration ceilings.** Touch only: the skill directory, sibling skills with cross-refs, `skills/catalog.json`, and tool alias-map files. Max 2 sweep-repair iterations if stale hits remain. Forbidden: editing files outside the rename scope; deleting content without archiving it first. | `git diff --cached --name-only` is a subset of rename-scope files. |
| R10 | **Branching.** IF the new slug collides with a built-in command (Gate 0) -> pick a different slug. IF `sac lint` reports `name-mismatch` -> fix the frontmatter `name:`, not the directory. IF a sweep grep returns stale hits -> re-grep and fix only the named owner (R6 sibling, R7 registry, or R8 alias). IF `catalog.json` fails to parse -> restore from the pre-edit SHA and retry the registry edit. | Each branch has a named action and recovery path. |
| R11 | **Failure fallback.** If `git mv` fails (path exists) -> verify the destination is empty and retry. If `sac catalog --build` fails -> `git add skills/catalog.json && git commit` as a fallback rebuild. If a dependent tool test fails -> read the failure, locate the old-slug reference the test exercises, fix it, and re-run. | Each failure has symptom, cause, and recovery command. |
| R12 | **Completion.** Case-insensitive sweep grep of the affected tree for the old slug and `/<old>` returns zero stale hits except intentional legacy-alias mentions; `catalog.json` parses as JSON; dependent tool test suites pass. | Sweep grep clean; `python -c 'import json; json.load(open("skills/catalog.json"))'` exits 0. |

## Routing

| Step | File | Purpose |
|------|------|---------|
| 1 | [`references/step-1-procedure.md`](references/step-1-procedure.md) | Gate 0 slug check, rename procedure (7 steps), completion criteria |