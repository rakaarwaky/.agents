---
name: omniroute
description: OmniRoute free AI gateway over OpenAI REST, 350+ providers with 150+ free tiers. Use when mentioning OmniRoute, OMNIROUTE_URL, auto/best-free, free-tier routing, checking a model context length (ctx) on the gateway, or building a model tier list / ranking the gateway model catalog. 9router (port 20128) is the second supported gateway vendor alongside OmniRoute.
when-to-use: "Use when asking about OmniRoute, OMNIROUTE_URL, OMNIROUTE_KEY, auto/best-free or other combo routing, free-tier routing, adding a custom OpenAI-compatible provider, managing the OmniRoute daemon (status, restart, logs), fixing OmniRoute errors, or building a model tier list / ranking the gateway model catalog."
argument-hint: "[setup | models [--free] [--search <q> | --json] | combo <list|switch|create|delete|suggest> | providers <add|list|test|edit|remove|test-all> | aa omniroute <status|restart|logs|models|service-install> | doctor | keys | cost]"
---

# OmniRoute

Free-first AI gateway exposing OpenAI-compatible REST across hundreds of providers with free tiers and combo routing based on task shape.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Target default API endpoint at `http://127.0.0.1:7777` with header `Authorization: Bearer ${OMNIROUTE_KEY}`. | Verify endpoint connectivity and auth header in HTTP requests. |
| R2 | Maintain working files strictly inside `~/.omniroute/` and do not relocate `.env` or database files. | Confirm `.env` and `storage.sqlite` exist under `~/.omniroute/`. |
| R3 | Never rotate `STORAGE_ENCRYPTION_KEY` in `.env` or allow tools to regenerate it. | Verify key constancy to prevent provider credential corruption. |
| R4 | Prefer combo routing aliases (`auto/*`) to select optimal models by task shape. | Inspect model query parameter for auto combo patterns. |
| R5 | Recognize 9router on port 20128 as the second supported gateway alongside OmniRoute. | Check gateway target port and routing compatibility. |

## Routing

| Reference | Purpose |
| --------- | ------- |
| [`references/setup.md`](references/setup.md) | Environment setup, config layout, port override, verification. |
| [`references/combos.md`](references/combos.md) | Combo routing aliases and curl example. |
| [`references/providers.md`](references/providers.md) | Provider keys, dashboard, custom provider addition, and daemon management. |
| [`references/models.md`](references/models.md) | Discover models via `/v1/models` and the CLI. |
| [`references/sync.md`](references/sync.md) | Sync providers/models/combos into 9router SQLite. |
| [`references/errors.md`](references/errors.md) | Common OmniRoute errors and fixes. |
| [`references/model-tier-list.md`](references/model-tier-list.md) | Build a model tier list / capability ranking from the catalog. |
| [`references/omniroute-models-shape.md`](references/omniroute-models-shape.md) | `GET /v1/models` response shape and dedupe suffix list. |
| [`references/custom-provider.md`](references/custom-provider.md) | Add a custom OpenAI-compatible provider, with management API and CLI examples. |
| [`references/agy-profile-login.md`](references/agy-profile-login.md) | Connect Antigravity (agy) accounts from per-profile Brave sessions in bulk. |
| [`references/kilocode-profile-login.md`](references/kilocode-profile-login.md) | Connect Kilo Code accounts from per-profile Brave sessions in bulk. |
| [`references/cline-profile-login.md`](references/cline-profile-login.md) | Connect Cline (api.cline.bot) accounts via AuthKit OAuth + callback-paste flow. |
