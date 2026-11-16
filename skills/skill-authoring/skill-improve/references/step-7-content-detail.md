# Improve — Step 7: Content detail

**Goal:** you can judge and fix body content so examples are concrete, defaults replace menus, and scripts, tool references, and paths follow the stated conventions.

- Concrete examples over abstract description; input/output pairs for style-dependent output.
- Defaults, not menus of alternatives.
- Scripts handle errors themselves, justify constants, list dependencies.
- Prefer referencing existing CLI tools over writing custom scripts.
- MCP tools named fully qualified (`ServerName:tool_name`).
- Forward slashes in paths (`scripts/helper.py`); no time-sensitive content in the body.
- **Safety-model consistency**: when the user re-specifies which mode control flag governs the run (e.g. `--dry-run` vs `--headless` vs no flag), the single source of truth is the **Safety model** bullet in `SKILL.md` Rules. Sync that bullet, the `argument-hint` in frontmatter, and every step-file line that describes mode behavior — all three must agree on default-vs-flag semantics before the edit is considered done.
- **Objective success metric**: replace subjective adjectives ("clean", "robust", "well-written") with a machine-verifiable exit criterion (`sac lint` exit 0, `cargo test` exit 0, exact `grep` match). Map to Rule R24.
- **Explicit scope ceiling**: state the exact maximum scope (e.g., "maximum 3 files", "only `references/` and `SKILL.md`") and iteration budget (e.g., "stop after 2 fix attempts and report") so the agent does not loop or touch adjacent files. Map to Rule R25.
- **Branch & fallback table**: convert vague failure advice ("fix if error") into explicit `IF <observed error> -> cause: <root cause> -> recovery: <exact action>` rows in the step file. Map to Rule R26.

## Completion

- Examples are concrete input/output pairs; defaults replace menus; scripts handle errors themselves and justify constants; MCP tools fully qualified (`ServerName:tool_name`); paths use forward slashes; no time-sensitive content; safety-model bullet, `argument-hint`, and step files agree on default-vs-flag semantics; success metrics are machine-verifiable (R24); scope/iteration ceilings are explicit (R25); failure modes state exact diagnosis and recovery (R26).
