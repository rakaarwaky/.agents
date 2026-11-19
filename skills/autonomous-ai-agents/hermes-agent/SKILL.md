---
name: hermes-agent
description: "Use, configure, theme, extend, and orchestrate Hermes Agent — including multi-bot Telegram multiplex gateways and gateway persistence. Observed user phrasing: 'spawn sub agent / subagents to make all FRD becoming real', 'we need to spawn sub agent', 'can Hermes do X' / 'how do I set up X in Hermes', 'only spawn hermes', 'hanya spawn hermes', 'hermes' with a task to delegate."
when-to-use: "Use when the user mentions Hermes, hermes CLI, TUI, skins/themes, desktop plugins, TUI widgets, pets, provider or model setup, spawning additional hermes instances or sub agents, multi-agent coordination, messaging-gateway bots, or asks 'can Hermes do X' / 'how do I set up X in Hermes'."
argument-hint: "[<question | task>] [chat] [-q <query>] [-m <model>] [--provider <p>] [--resume <session> | --continue] [--oneshot | -Q] [--worktree]"
---

# Hermes Agent

Hermes Agent is an open-source AI agent framework that operates across terminal, desktop, messaging platforms, and IDEs, supporting multi-agent coordination, persistent memory, and customizable interfaces.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Never break prompt caching by changing past context, toolsets, or system prompt mid-conversation. | Verify context and toolset consistency across turns. |
| R2 | Alternate message roles strictly: never emit two assistant or user messages in a row. | Validate conversation history sequence before dispatching messages. |
| R3 | Do not ask unnecessary clarifying questions when user instructions provide specific path and flag directives. | Check request specificity before prompting user for confirmation. |
| R4 | Store credentials and secrets in `.env`, and application settings in `config.yaml`. | Inspect configuration paths and verify separation of secrets. |
| R5 | Never edit `config.yaml` manually; use `hermes config set KEY VAL` with JSON array literals for lists. | Verify configuration updates through CLI commands or ruamel round-trip. |
| R6 | Never terminate or stop the gateway process from within the gateway session. | Confirm gateway lifecycle commands execute outside running gateway process. |
| R7 | Run spawned Hermes instances as independent subprocesses with separate sessions and tools. | Verify process isolation for subagent and worker processes. |

## Routing

| User wants... | Reference | Purpose |
|---|---|---|
| Orientation: scope rule, quick start, key paths, surfaces | [`references/hub.md`](references/hub.md) | Initial orientation and architecture overview |
| CLI commands, subcommands, flags, running tasks | [`references/cli-reference.md`](references/cli-reference.md) | Command line interface reference |
| In-session slash commands | [`references/slash-commands.md`](references/slash-commands.md) | Slash command inventory and usage |
| Provider setup, API keys, OAuth | [`references/providers-and-models.md`](references/providers-and-models.md) | Model and provider configuration |
| config.yaml sections, toolsets, voice STT/TTS | [`references/configuration.md`](references/configuration.md) | Configuration file schema and sections |
| AGENTS.md, .hermes.md, CLAUDE.md project rules | [`references/project-context-files.md`](references/project-context-files.md) | Project context and instruction file standards |
| Standing behavior, identity, or task routing | [`references/soul-md-routing.md`](references/soul-md-routing.md) | Identity and persistent routing guidelines |
| Secret redaction, PII, approval modes | [`references/security-privacy.md`](references/security-privacy.md) | Security, privacy, and approval settings |
| Delegation, cron, curator, kanban | [`references/background-systems.md`](references/background-systems.md) | Background task and management systems |
| MCP servers (add, catalog, hermes mcp) | [`references/native-mcp.md`](references/native-mcp.md) | MCP server configuration and registry |
| Webhook routes and event-driven runs | [`references/webhooks.md`](references/webhooks.md) | Webhook triggers and endpoints |
| Custom theme/skin configuration | [`references/themes.md`](references/themes.md) | Theme creation and live palette editing |
| Desktop app UI elements and plugins | [`references/desktop-plugins.md`](references/desktop-plugins.md) | Desktop plugin development |
| Desktop translucency troubleshooting | [`references/desktop-translucency.md`](references/desktop-translucency.md) | Window translucency settings |
| Live TUI panel or modal widgets | [`references/tui-widgets.md`](references/tui-widgets.md) | Terminal widget creation and integration |
| Pet mascots install and scaling | [`references/petdex.md`](references/petdex.md) | Mascot management and diagnosis |
| Windows-specific keybind and socket issues | [`references/windows-quirks.md`](references/windows-quirks.md) | Windows and WSL troubleshooting |
| Debugging voice, tools, gateway issues | [`references/troubleshooting.md`](references/troubleshooting.md) | Diagnostic workflows and logging |
| Contributing code, tools, and slash commands | [`references/contributor-guide.md`](references/contributor-guide.md) | Developer guidelines and tests |
| delegate_task concurrency diagnosis | [`references/delegate-task-concurrency-diagnosis.md`](references/delegate-task-concurrency-diagnosis.md) | Concurrency limit troubleshooting |
| Session library search and cleanup | [`references/session-librarian.md`](references/session-librarian.md) | Session archiving and hygiene |
| Portal auth for third-party apps | [`references/portal-auth-for-third-party-apps.md`](references/portal-auth-for-third-party-apps.md) | Nous Portal OAuth integrations |
| Multi-bot Telegram setup and multiplexing | [`references/multi-bot-telegram-run.md`](references/multi-bot-telegram-run.md) | Multi-bot gateway configuration |
| Systemd always-on persistence | [`references/systemd-always-on.md`](references/systemd-always-on.md) | Service daemon persistence |
| Spawning Hermes instances and subagents | [`references/spawning.md`](references/spawning.md) | Process spawning and multi-agent flows |
| Late profile adoption diagnosis | [`references/multiplex-late-profile-adoption.md`](references/multiplex-late-profile-adoption.md) | Profile bot adoption troubleshooting |
| Multiplex gateway internals | [`references/multiplex-internals.md`](references/multiplex-internals.md) | Gateway internals and token scoping |
