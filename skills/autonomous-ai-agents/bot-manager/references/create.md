# Create — design and build a new bot

Covers designing a new bot from a plain-language request: the brief, the proposal card, template selection, worktree assignment, and the new bot's first-turn setup. This file is read when the owner asks for a new bot or `orca bot list` shows no existing bot fits the work.

**Goal:** the owner approves a `bot create --offer` card and a new bot exists at `~/.orca/bots/<name>` with a SOUL.md that starts read-and-report only.

## 1. Read the roster first

Before proposing anything, quote the line that proves no bot fits:

```bash
orca bot list
```

If a bot already covers the job, hand the work to that bot instead (see [`delegate.md`](delegate.md)). Only when no line fits, continue.

## 2. Write the design brief

From the owner's request, write a one-sentence purpose, the name (gerund-free, lowercase-hyphen), and what it watches, does, and reports:

| Field | Source | Example |
|-------|--------|---------|
| `--name` | Owner's words or derived from purpose | `Nany-PR-Babysit` |
| `--purpose` | One sentence, first line of its SOUL.md | `Watches pull requests, fixes CI until green, merges when ready.` |
| `--watches` | What events wake it | `github.ci_failed, github.review` |
| `--does` | What it may do after approval | `fix CI, reply to reviews, merge` |
| `--reports` | Where results go | `its Home Chat, item mail` |
| `--worktree` | Workspace(s) it takes over (repeatable) | `name:repo-name` |

## 3. Propose the card — never create directly

A bot is created only when the owner accepts the card:

```bash
orca bot create --offer \
  --name "<name>" \
  --purpose "<one sentence>" \
  --watches "<events>" \
  --does "<actions>" \
  --reports "<where>" \
  --worktree name:<workspace>
```

Nothing exists until the owner presses **Create bot** or edits the card first. A **Not now** comes back as a message — accept it and stop.

## 4. Optional: template

Built-in template ids fill name, purpose, watches, does, and reports when left out:

```bash
orca bot create --offer --template pr-review --name "<name>"
```

A wrong id lists all templates. Available ids come from the Orca build; check `--template <bogus>` output rather than guessing.

## 5. First-turn setup (what the new bot does)

The new bot's first turn reads SOUL.md and MEMORY.md, then follows the first-run rules: greet, ask one question, write its SOUL.md from what it learned. Its SOUL.md purpose line is the `--purpose` text, written before its first turn; it starts by reading and reporting only (Rule R1).

Do not write another bot's SOUL.md or MEMORY.md yourself (Rule R3). The new bot writes its own on its first turn.

The SOUL.md it writes follows the template at [`../template/soul.md`](../template/soul.md): title, one-sentence purpose (the `--purpose` text), `## How I work` with concrete paths, one `##` section per domain rule its job needs, and a `## Never` section that always keeps the read-and-report default bullet.

## Worked example

Owner: "I need a bot that watches the erp repo for failed CI and fixes it."

1. `orca bot list` — shows Nany-PR-Babysit (PR babysitter), Risa-AutoRelease (release notes), Mana-BotManager (this bot), pull-request-review, reles. None watches erp CI failures for fixes.
2. Brief: name `erp-ci-fixer`, purpose `Watches erp repo CI and fixes failures until green.`, watches `github.ci_failed`, does `read logs, patch, push`, reports `its Home Chat`.
3. `orca bot create --offer --name erp-ci-fixer --purpose "..." --watches "github.ci_failed" --does "fix CI" --reports "Home Chat"` — owner sees the card.
4. Owner presses Create bot → new bot exists; its first turn greets and writes its own SOUL.md.

## Completion

- `orca bot list` line quoted showing no existing fit (or a handoff done instead).
- `bot create --offer` card shown; owner approved or declined.
- New bot appears in `orca bot list` with the purpose line as its SOUL.md first line.
- The new bot's SOUL.md is written from [`../template/soul.md`](../template/soul.md): title, one-sentence purpose, `## How I work` with concrete paths, domain rule sections, and `## Never` with the read-and-report default bullet.