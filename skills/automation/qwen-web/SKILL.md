---
name: qwen-web
description: Automate Qwen AI Web (chat.qwen.ai) with the Qwen3.8-Max intelligence model — zero API keys, persistent browser sessions — and develop the qwen-web-arwaky repo source (TUI, slots, tests). Use when an AI agent needs to send prompts, review code, or analyze attachments via CLI/MCP tools, or edit the internal/qwen-web-arwaky source.
when-to-use: Use when the user runs /qwen-web, sends a prompt to Qwen AI Web, sends prompt files or attachments for Qwen analysis or code review with role templates, sets up or resets the Qwen browser session, initializes the qwen-web workspace, or asks to develop or fix the internal/qwen-web-arwaky repo.
argument-hint: "<prompt direct -t <text> | prompt file -i <file> | prompt attach -i <file> -a <file> | doctor [--smoke] [--deep] | session login | session remove <id> | init [--dir <dir>]> [-o <out-file>] [--headless|--no-headless] [--json]"
---

# Qwen Web Automation Skill Guide

Send prompts, prompt files, and attachments to Qwen AI Web (`chat.qwen.ai`) and receive responses via MCP tools or the `qwa` CLI (`qwen-web-arwaky`), or develop and modify the `qwen-web-arwaky` repository source.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Timestamp every output filename (`YYYYMMDD_HHMMSS`) under `.qwen-web-arwaky/output/` and keep inputs under `.qwen-web-arwaky/input/`. | Verify output paths contain timestamp and prevent overwriting prior runs. |
| R2 | Prefer attachments for context, keeping prompt files focused on instructions while passing code, logs, and schemas as attachments. | Inspect invocation payload to verify bulky context is routed via attachments. |
| R3 | Demand complete code output with explicit output contracts and anti-truncation clauses using reasoning-before-code ordering. | Verify prompt text contains anti-truncation requirements and complete output contracts. |
| R4 | Verify session health before work by running `check_session` or `qwa doctor`; re-login with `setup_session` or `qwa session login` on auth failure. | Check doctor/session status before executing workflows. |
| R5 | Never type passwords or 2FA codes for Qwen sessions directly; solve authentication manually via visible browser login. | Ensure automated scripts do not prompt for or hardcode credentials. |

## Routing

| Step | Reference | Purpose |
| ---- | --------- | ------- |
| Step 1: Quick reference | [`references/step-1-quick-reference.md`](references/step-1-quick-reference.md) | MCP tool ↔ `qwa` CLI command mapping. |
| Step 2: Usage by use case | [`references/step-2-use-cases.md`](references/step-2-use-cases.md) | Six use cases: inline prompt, file, attachment, role templates, session, init. |
| Step 3: Prompt engineering | [`references/step-3-prompt-engineering.md`](references/step-3-prompt-engineering.md) | Rules for complete, un-truncated output. |
| Step 4: Error handling | [`references/step-4-error-recovery.md`](references/step-4-error-recovery.md) | Error → cause → recovery table. |
| Step 5: Development | [`references/step-5-dev.md`](references/step-5-dev.md) | Dev guide for the `qwen-web-arwaky` repo source. |
