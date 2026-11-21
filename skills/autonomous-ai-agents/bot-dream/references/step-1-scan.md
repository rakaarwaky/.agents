# Step 1: Scan bot chats

List the bot's chats and read their content.

## Commands

```bash
orca bot chats
```

This lists each chat with its id, title, last activity, and last ask/answer.

## Reading conversation content

For each chat that could contain durable facts:

1. Open the chat transcript (via `orca terminal read` or Orca chat viewer).
2. Read the conversation in order.
3. Identify statements that name decisions, conventions, ownership, or confirmed behaviors.

## Scope

- Scan chats from the last 7 days by default.
- Stop after the user's specified time window or chat count.