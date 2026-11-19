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
5. Tooling that keys off skill names (alias maps, subdir aliases, doc lists of which skills use the tool, run-summary docstrings). Add the new slug as an alias resolving to the canonical target; keep the old slug as a legacy alias so pre-existing invocations still resolve — UNLESS the user asked for a clean break ("no legacy or alias"), in which case purge: remove the old slug from the alias map entirely, drop it from argparse `choices=` lists, delete superseded duplicate artifacts, and rewrite the old command mentions in trigger text.
6. Bulk word replace (only if the user asked to rename domain terms): after replacing `\b<old>\b`→`<new>`, fix the casing damage (headers and titles like `# Design Doc` become `# plan Doc`) and collision damage (a quoted token replaced in place can produce a duplicate `choices=[..., "plan", "plan", ...]` or delete a needed dict key). Grep the touched files for doubled tokens and duplicate list literals before continuing.
7. Sweep: case-insensitive grep of the SHIPPED surface only (the renamed skill dir, `personas/`, the tool's `src/`+`tests/`+doc files, `skills/catalog.json`) — never the whole repo, which drags in `.venv`, `.export`, Rust `target/`, and third-party schema. Confirm only intentional legacy-alias mentions remain (or zero, on a purge).
8. Verify: validate `catalog.json` parses as JSON, and run any tool test suite that depends on the rename.

## Completion

- Gate 0 passed: the new slug does not collide with a built-in command or alias.
- `git mv` done; `SKILL.md` `name` and heading updated to the new slug.
- Sibling cross-refs, `catalog.json`, and tool alias maps updated.
- Domain terms (if requested) renamed; casing and duplicate-list artifacts fixed; superseded duplicate artifacts deleted.
- Sweep grep of the shipped surface returns zero stale hits except intentional legacy aliases (or zero entirely on a purge).
- `catalog.json` parses as JSON; dependent tool tests pass.