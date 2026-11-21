# Step 4: Write results

## MEMORY.md format

`MEMORY.md` is an index only. One line per fact, newest first:

```
# Memory

One line per fact, newest first. Longer notes go in memory/<topic>.md.

- YYYY-MM-DD <one-line summary>. See memory/<topic>.md.
```

Rules:
- One line per fact, never more.
- Each line ends with `See memory/<topic>.md.` pointing at the detail file.
- Newest first.
- Never duplicate a fact across lines.

## memory/<topic>.md format

Each topic file holds full detail for one subject:

```
# <Topic>

## Fact 1 (YYYY-MM-DD)

<full detail, context, commands, examples>

## Fact 2 (YYYY-MM-DD)

<full detail>
```

## Write process

1. Write or update `memory/<topic>.md` for each affected topic.
2. Rewrite `MEMORY.md` with the consolidated index.
3. Report the review result to the user.

## Report shape

```
Found N facts in M chats:
- NEW: <fact> → memory/<topic>.md
- UPDATE: <fact> → memory/<topic>.md
- STALE: <fact> → removed
- KEEP: <fact> → memory/<topic>.md

MEMORY.md updated (X entries).
memory/<topic>.md updated.
```