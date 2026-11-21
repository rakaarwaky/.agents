# Step 0: Overview

## What dream-bot does

Reviews conversation history from bot chats, extracts durable facts (decisions, conventions, ownership rules), and consolidates them into `MEMORY.md` (index) and `memory/<topic>.md` (detail). Stops after reporting the review result.

## Activation terms

User says: `dream`, `review memory`, `consolidate memory`, `update MEMORY`.

## Environment precondition

- Orca CLI available: `orca bot chats` works.
- `MEMORY.md` exists at bot home: `/home/raka/.orca/bots/<bot>/MEMORY.md`.

## What counts as a durable fact

- Architectural decisions (schema changes, new lanes, template changes).
- Confirmed behaviors (auto-undraft, author gates, Mergify rules).
- New conventions (commit format, file locations, naming).
- Ownership boundaries (who owns what lane/skill).
- Tool/CLI usage patterns that were verified.

## What does NOT count

- One-time task results ("merged PR #329").
- Temporary state ("CI is currently red").
- Questions without answers.
- Failed attempts that were superseded.