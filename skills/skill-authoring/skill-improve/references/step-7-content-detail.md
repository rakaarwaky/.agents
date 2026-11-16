# Improve — Step 7: Content detail

**Goal:** you can judge and fix body content so examples are concrete, defaults replace menus, and scripts, tool references, and paths follow the stated conventions.

- Concrete examples over abstract description; input/output pairs for style-dependent output.
- Defaults, not menus of alternatives.
- Scripts handle errors themselves, justify constants, list dependencies.
- Prefer referencing existing CLI tools over writing custom scripts.
- MCP tools named fully qualified (`ServerName:tool_name`).
- Forward slashes in paths (`scripts/helper.py`); no time-sensitive content in the body.
- **Safety-model consistency**: when the user re-specifies which mode control flag governs the run (e.g. `--dry-run` vs `--headless` vs no flag), the single source of truth is the **Safety model** bullet in `SKILL.md` Rules. Sync that bullet, the `argument-hint` in frontmatter, and every step-file line that describes mode behavior — all three must agree on default-vs-flag semantics before the edit is considered done.
- **Core-question answers**: the success metric, scope and iteration ceilings, branches, and fallback tables are scored, placed, and patched per `step-14-tenq-standard.md`; R24–R26 are the Rules that require them. Worked before/after patches are in `step-15-tenq-diagnosis.md`.

## Completion

- Examples are concrete input/output pairs; defaults replace menus; scripts handle errors themselves and justify constants; MCP tools fully qualified (`ServerName:tool_name`); paths use forward slashes; no time-sensitive content; safety-model bullet, `argument-hint`, and step files agree on default-vs-flag semantics; the core-question answers this step owns are placed per `step-14-tenq-standard.md` (R24, R25, R26).
