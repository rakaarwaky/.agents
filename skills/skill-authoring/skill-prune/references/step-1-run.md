# Step 1: Run lifecycle transitions

Apply automatic skill lifecycle transitions before the consolidation work.

**Goal:** call `sac run` once to move skills through their lifecycle states (active → stale → archived).

## Commands

```bash
sac run
```

## What it does

`SkillsRunner.apply_automatic_transitions()` iterates every skill in the pack and moves skills based on idle time and usage telemetry:

- **active → stale** — idle past the `stale_after_days` threshold.
- **stale → active** — activity window re-anchored.
- **active/stale → archived** — idle past the `archive_after_days` threshold.
- **pinned skills** and **cron-referenced skills** are always skipped.
- Pauses are respected: if the lifecycle is paused, `sac run` returns `paused: True` and skips all transitions.

## Completion

- `sac run` executed once.
- Transition results recorded (applied / skipped / state counts).
- Lifecycle state is settled before the prune steps begin.

## Report

Add the lifecycle run results to the final report under a `LIFECYCLE RUN` section:

```text
LIFECYCLE RUN:
- transitions applied: <count>
- skills skipped: <count>
- state distribution: <active: N, stale: N, archived: N>
- paused: <true | false>
```

## Remembering

Record the following in the final report so the lifecycle state is not lost:

- The lifecycle config state (`paused: true | false`).
- The per-state counts before and after `sac run`.
- Which skills were skipped and why (pinned, cron, young-unused, no-anchor).