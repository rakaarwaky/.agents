# Roster — list, inspect, configure, retire

Covers managing the existing bot roster: listing bots and their chats, offering connectors, configuring a bot's setup, and retiring one. This file is read when the owner asks what bots exist, wants a connector connected, or asks to retire a bot.

**Goal:** the roster is visible, each bot's purpose and reach are known, and any add/remove is done only with the owner's approval.

## List and inspect

```bash
orca bot list
orca bot chats --bot "<name>"
orca bot connectors
```

`bot list` shows each bot, its agent, purpose line, linked services, and chat count. `bot connectors` shows, per service, which tool acts as whom, whether it is signed in, and where this bot is.

## Offer a connector

When the work needs Slack, Linear, GitHub, or Google and `bot connectors` shows it is not connected:

```bash
orca bot connectors --offer <service>
```

The owner sees a Connect card in this chat. Never tell them to click "Add connector" — the card is the path. For a specific workspace the owner names:

```bash
orca bot connectors --offer <service> --workspace "<name>"
```

Already connected and the owner wants more (another org, repo, or workspace): the same `--offer` shows the card that adds it.

## Retire a bot

Only when the owner explicitly asks. State what the bot does and what will be lost before acting:

```bash
orca bot list   # confirm the target bot and its purpose
```

A bot is retired through the owner's Orca UI — propose the retirement, name what it does, and wait for confirmation. Do not delete another bot's home folder directly.

## Keep memory current

```bash
orca bot memory forget --fact "<its words>"
```

Use it to remove or replace a MEMORY.md line; a line taken out any other way is put back. Date each new line; details go in `memory/<topic>.md`; never store secrets (Rule R4).

## Check what you are doing and what you need

```bash
orca bot work list
orca bot item list
orca bot item show <n>
orca bot item set <n> --status needs-you --comment "..." --ask "..." --option "..." --recommended <n>
```

Items are where the owner checks where work stands and decides. Lead each item with what changed or what is needed; give choices as buttons, never as a prose list.

## Completion

- `orca bot list` and `bot connectors` read before any roster change.
- Connector offers, retirements, and memory edits each trace to an explicit owner request.
- No bot's home files edited without its owner's request through this bot (Rule R3).