---
name: skill-traces
description: "Learns from, evolves, and unlearns skills from Grok Build session traces in one pass. --learn creates skills for repeated hand-typed instructions and open gaps; --evolve fixes stale lines in loaded skills; --unlearn retires skills the traces show are never used. Deterministic counts and repeated-phrase material come from the trace pipeline (usage.json, phrases.json); memory-v2 topics add topic-level learn/stale/unlearn signals and the --unlearn keep-list (memory.json). a narrow window lists but does not retire."
when-to-use: Use when the user wants to learn new skills from repeated hand-typed instructions, evolve stale skill lines to match current reality, or retire skills the traces show they never use. Pick one or more modes: --learn, --evolve, --unlearn; the trace pipeline runs once and every mode applies its own action kinds.
argument-hint: "[--learn] [--evolve] [--unlearn]"
---

# Skill Traces

Analyze Grok Build session traces to synthesize new skills from repeated user instructions, update stale skill contents, and archive unused skill definitions.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Require at least one active mode flag (`--learn`, `--evolve`, or `--unlearn`) per trace run. | Validate command invocation flags contain one or more target modes. |
| R2 | Read deterministic material (`usage.json`, `phrases.json`, `memory.json`) from the run directory rather than recalculating manually. | Confirm inputs are loaded directly from generated pipeline JSON files. |
| R3 | Enforce report invariant: every entry in `actions.json` must be documented in `report.md` with verifiable evidence. | Verify cross-consistency between `actions.json` and `report.md`. |
| R4 | Execute actions strictly based on verified trace evidence and explicit user confirmation. | Confirm validation checks pass prior to applying skill mutations. |
| R5 | Record decision logs for every applied action, detailing state transitions, action types, and backup undo paths. | Inspect decision log output for applied mutations. |
| R6 | Run `sac lint` on every skill file created or edited to ensure zero lint defects. | Execute `sac lint` across touched skill directories after mutation. |

## Routing

| Step | Reference | Purpose |
| ---- | --------- | ------- |
| Step 0 | [`references/step-0-resume-or-price.md`](references/step-0-resume-or-price.md) | Resume a pending run or price the scope; collect window filters are CLI flags with hardcoded defaults. |
| Step 1 | [`references/step-1-collect.md`](references/step-1-collect.md) | The collector writes `manifest.json` and `sessions/*.json`; materialize `usage.json` and `phrases.json`; the signal definitions mappers and reducers read. |
| Step 2 | [`references/step-2-launch.md`](references/step-2-launch.md) | Launch the `learn-traces` workflow; block on trace-state wait. |
| Step 3 | [`references/step-3-read-report.md`](references/step-3-read-report.md) | Present the Overview plus the sections the chosen modes own; the full `report.md` and `actions.json` shapes. |
| Step 4 | [`references/step-4-apply.md`](references/step-4-apply.md) | Per-action rules for every kind; record decisions. |
| Step 5 | [`references/step-5-verify.md`](references/step-5-verify.md) | Re-read touched files; confirm the change and every trash backup; run validation. |
| Step 6 | [`references/step-6-prune.md`](references/step-6-prune.md) | Prune the raw session store to keep only the N most recent session dirs (`sac traces prune`). |
