---
name: bot-manager
description: "Design new bots and manage the whole bot roster — create, configure, delegate tasks, automate recurring work, and retire bots via Orca."
when-to-use: "Use when the owner asks to design, create, configure, retire, or delegate a task to a bot; mentions bot roster, bot lifecycle, bot automations, or asks 'what bots exist', 'make a new bot', 'manage bots', 'bikin bot', 'buatkan bot baru', 'kelola bot', 'delegate', 'otomasi', 'retire bot'. Not for writing code itself — route code work to workers via delegation."
argument-hint: "<action> [<target>] [--repo <path>] [--agent <id>] [--prompt <brief>]"
---

# Bot Manager

Design new bots and manage the bot roster — create, configure, delegate tasks, automate recurring work, and retire bots on request. Start by reading and reporting; change nothing until the owner approves.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **Read-and-report only until owner approves.** Start every run by listing or inspecting the current state; propose changes; wait for approval before any write. | First action is a read (`orca bot list`, `orca bot chats`, `orca bot connectors`); no write until an explicit approval message. |
| R2 | **One automation per request.** Each recurring task is one `--once` or recurring automation with the narrowest event; never add a second to collect for it. | Each `automations create` corresponds to one named request; no duplicates in `orca automations list`. |
| R3 | **Never change another bot's home files** (SOUL.md, MEMORY.md, bot.json) unless its owner asks through this bot. | Every write to a file under `~/.orca/bots/<other>/` traces to owner text naming that bot's file. |
| R4 | **Secrets never enter memory.** No tokens, keys, or credentials in MEMORY.md or topic files. | `grep -ri 'key\|token\|secret\|password' /home/raka/.orca/bots/mana-botmanager/MEMORY.md` returns zero hits. |
| R5 | **Answer where asked.** A comment on an item gets a comment back; a chat/Slack/Linear/GitHub thread gets a reply in that thread. Never answer only with NO_REPLY when the user asked a direct question. | Final message location matches the wake source; item mail gets item comments, chat gets final message. |
| R6 | **Delegate code work to workers.** Hand implementation to a worker via `orchestration worker-start`; do not edit project files directly. | Code changes appear in a worktree, not in this bot's home folder; worker result arrives as item mail. |
| R7 | **One bot per purpose.** Propose a new bot only when `orca bot list` shows no existing bot fits the work; name the gap. | Before `bot create --offer`, quote the `bot list` line showing no fit. |
| R8 | **Offer what the work needs, one at a time.** Slack, Linear, GitHub, Google — offer the connector only when the request needs it and `bot connectors` shows it missing. | `bot connectors --offer <service>` appears once per needed service, with the owner's approval. |
| R9 | **Body shape is fixed.** `SKILL.md` carries exactly `# Title`, `## Rules`, `## Routing` in that order; every file under `references/` and `template/` is linked from the Routing table. | `grep -n '^## ' SKILL.md` returns exactly `## Rules` and `## Routing`; every `references/*.md` and `template/*.md` basename appears in SKILL.md. |
| R10 | **Every recurring request is an automation, never a local scheduler.** Use `orca automations create`; state where it runs and where results go. | No `sleep`/`cron`/`scheduler_create` in this skill; `automations list` shows the named rule. |

## Routing

| Step | File | Purpose |
|------|------|---------|
| Create a new bot | [`references/create.md`](references/create.md) | Design brief, propose with `bot create --offer`, template selection, worktree assignment, first-turn SOUL.md. |
| Delegate tasks & automate | [`references/delegate.md`](references/delegate.md) | Hand code to a worker, structure orchestration, build automations with `--once`/recurring events, item tracking. |
| Manage the roster | [`references/roster.md`](references/roster.md) | List, inspect, configure, retire bots; connector offers; memory maintenance. |
| New bot's SOUL.md shape | [`template/soul.md`](template/soul.md) | Copy-source skeleton for the SOUL.md a new bot writes on its first turn; filled from the design brief. |