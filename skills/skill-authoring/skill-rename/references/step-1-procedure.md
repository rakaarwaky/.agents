# Step 1: Gate 0 and rename procedure

**Goal:** validate the new slug against built-in commands, then execute the rename across every surface that carries the old name.

## Gate 0: check the new slug against built-in commands FIRST

Before accepting a target slug, verify it is not a core Hermes command name or alias. Source of truth is `hermes_cli/commands.py` `COMMAND_REGISTRY` (`resolve_command` returns a def only when the slug or an alias is built-in). If it collides, the skill will NOT own the slash command: the built-in wins and the skill becomes reachable only via `/skill <slug>`.

Mechanism: `agent/skill_commands.py` skips auto-registration for any slug matching a core command name or alias, and `/skills list` marks it name-taken-by-built-in. This failure is silent, so pick the slug, run the gate, and if it collides choose a different slug.

Frequent built-ins that collide: `plan`, `learn`, `init`.

## Procedure

1. `git mv` the skill folder to the new slug.
2. Edit `SKILL.md`: the `name` field, the heading, and every `/<old>` to `/<new>` in the body. Also fix any persona or subagent names you accidentally retitled during the move (do not rename domain names that live elsewhere on disk).
3. Sibling cross-refs: grep the skills tree for the old slug and `/<old>`; update refs in OTHER skills that call this one (go-back pointers, sibling-skill lists, trigger text).
4. Registry: `skills/catalog.json` entry name plus any description or when-to-use that names the skill or `/<old>`.
5. Tooling that keys off skill names (alias maps, subdir aliases, doc lists of which skills use the tool, run-summary docstrings). Add the new slug as an alias resolving to the canonical target; keep the old slug as a legacy alias so pre-existing invocations still resolve.
6. Sweep: case-insensitive grep the affected tree for the old slug and `/<old>`; confirm only intentional legacy-alias mentions remain.
7. Verify: validate `catalog.json` parses as JSON, and run any tool test suite that depends on the rename.

## Completion

- Gate 0 passed: the new slug does not collide with a built-in command or alias.
- `git mv` done; `SKILL.md` `name` and heading updated to the new slug.
- Sibling cross-refs, `catalog.json`, and tool alias maps updated.
- Sweep grep returns zero stale hits except intentional legacy aliases.
- `catalog.json` parses as JSON; dependent tool tests pass.