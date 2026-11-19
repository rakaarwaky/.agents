---
name: statusline
description: "Configure the optional Grok Build status-line row (`[ui.status_line]`). Use when the user wants built-in items (cwd, model, context), a custom command script, or the row disabled."
when-to-use: "Use when the user asks to configure the status line row: built-in items, a custom script path, refresh interval, padding, or off/disabled."
argument-hint: "[builtin | command <path> | disabled]"
---

# Status Line

Configure the optional Grok Build status-line row: pick built-in items, point it at a custom script, or turn it off, then land the edit in the user config file Grok reads.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Write `[ui.status_line]` configurations exclusively to the resolved user `config.toml`, never repository-level files. | Inspect target config file path to ensure user configuration directory is used. |
| R2 | Prompt for confirmation before writing when the user has not explicitly requested status line configuration. | Verify explicit user intent prior to modifying status line settings. |
| R3 | Communicate effect timing clearly: table schema changes take effect at startup, custom scripts on the next execution cycle. | Confirm messaging to user distinguishes startup changes from next-run updates. |
| R4 | Adhere strictly to the script contract for stdin JSON parsing, stdout budgets, timeouts, and ANSI escaping. | Test custom status script against contract constraints and output budget. |

## Routing

| Step | Reference | Purpose |
| ---- | --------- | ------- |
| Where to write | [`references/config-location.md`](references/config-location.md) | Config file resolution, the one-file rule, and the ask-vs-write decision. |
| What to write | [`references/table-values.md`](references/table-values.md) | `[ui.status_line]` blocks for built-in, command, and disabled, with `refresh_interval` and `padding` ranges. |
| Script contract | [`references/script-contract.md`](references/script-contract.md) | Stdin JSON fields, the 5 x 1024 stdout budget, timeouts, and link/ANSI rules. |
| After the edit | [`references/post-edit.md`](references/post-edit.md) | Effect timing, the rendered `[ui.status_line]` failure mode, and `grok inspect`. |
