---
name: dream-bot
description: "Review and consolidate bot memory from conversation history — extract facts from chats, update MEMORY.md index and memory/ files, remove stale entries."
when-to-use: "User says 'dream', 'review memory', 'consolidate memory', 'update MEMORY', or wants to process conversation history into structured memory files."
argument-hint: "/dream [--dry-run]"
---

# Dream-Bot

## Rules

| ID | Rule | Check |
|---|---|---|
| R1 | Scan only chats owned by or mentioning this bot | `orca bot chats` output filtered to relevant chats |
| R2 | One line per fact in MEMORY.md, newest first | `grep -c '^- ' MEMORY.md` counts facts |
| R3 | Each fact points to memory/<topic>.md for detail | Every `See memory/...` target exists |
| R4 | Stale facts removed via `orca bot memory forget` | Edit not done directly on MEMORY.md |
| R5 | Never add facts outside MEMORY.md + memory/ | All durable facts live in memory files |

## Routing

| Step | File | Purpose |
|---|---|---|
| 1 | [`references/step-0-overview.md`](references/step-0-overview.md) | Scope and activation terms |
| 2 | [`references/step-1-scan.md`](references/step-1-scan.md) | List and read bot chats |
| 3 | [`references/step-2-extract.md`](references/step-2-extract.md) | Extract durable facts from conversations |
| 4 | [`references/step-3-review.md`](references/step-3-review.md) | Review existing MEMORY.md and memory/ |
| 5 | [`references/step-4-write.md`](references/step-4-write.md) | Write MEMORY.md index and memory/<topic>.md |
