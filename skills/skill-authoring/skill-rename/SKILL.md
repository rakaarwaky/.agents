---
name: skill-rename
description: "Use to rename a Hermes skill and propagate every reference."
when-to-use: "Use when asked to rename a skill, re-slug its folder, or diagnose why a skill's slash command is missing. A skill's frontmatter name IS its slash command, so a rename touches more than the folder."
argument-hint: "<old-slug> <new-slug>"
---

# Rename a Hermes skill

A skill's frontmatter name is its slash command. Renaming = change the folder, the name field, and every place that names the skill (slash refs, sibling cross-refs, registry, tool alias maps), then verify nothing still points at the old name.

## When to Use

- Renaming or re-slug-ing a skill folder, or moving it under a new name.
- Making a skill invokable under a different /slash command.
- A freshly named skill's slash command is missing from /skills list — diagnose why before assuming a bug.

## Gate 0: check the new slug against built-in commands FIRST

Before accepting a target slug, verify it is not a core Hermes command name or alias. Source of truth is hermes_cli/commands.py COMMAND_REGISTRY (resolve_command returns a def only when the slug or an alias is built-in). If it collides, the skill will NOT own the slash command: the built-in wins and the skill becomes reachable only via /skill <slug>. Mechanism: agent/skill_commands.py skips auto-registration for any slug matching a core command name or alias, and /skills list marks it name-taken-by-built-in. This failure is silent, so pick the slug, run the gate, and if it collides choose a different slug.

## Procedure

1. git mv the skill folder to the new slug.
2. Edit SKILL.md: the name field, the heading, and every /<old> to /<new> in the body. Also fix any persona or subagent names you accidentally retitled during the move (do not rename domain names that live elsewhere on disk).
3. Sibling cross-refs: grep the skills tree for the old slug and /<old>; update refs in OTHER skills that call this one (go-back pointers, sibling-skill lists, trigger text).
4. Registry: skills/catalog.json entry name plus any description or when-to-use that names the skill or /<old>.
5. Tooling that keys off skill names (alias maps, subdir aliases, doc lists of which skills use the tool, run-summary docstrings). Add the new slug as an alias resolving to the canonical target; keep the old slug as a legacy alias so pre-existing invocations still resolve.
6. Sweep: case-insensitive grep the affected tree for the old slug and /<old>; confirm only intentional legacy-alias mentions remain.
7. Verify: validate catalog.json parses as JSON, and run any tool test suite that depends on the rename.

## Always-on rules and pitfalls

- Renaming to a built-in-adjacent slug silently strips the slash command; run Gate 0 before committing to the slug, not after.
- A rename is NOT just the folder; frontmatter name, catalog.json, sibling cross-refs, and tool alias maps each carry the old name; verify each. A missed sibling ref leaves a dead slash command in another skill's docs.
- Change skill-NAME references, not domain-CONCEPT words. The skill's own output (its documents, IDs, personas) keeps its own terminology; only the skill identity and its slash command change. Do not rename e.g. design-document / design-doc-* / DESIGN_ID just because the skill is no longer called that.
- Keep a backward-compat alias (old to canonical) rather than deleting it, so old invocations and artifacts still resolve; mark it legacy in a comment.