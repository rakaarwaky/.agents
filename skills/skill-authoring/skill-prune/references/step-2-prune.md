# Step 2: Prune idle skills

Archive idle skills and purge old archives before the consolidation work.

**Goal:** call `sac prune --apply` once to archive skills idle past the TTL and permanently delete old archives.

## Commands

```bash
sac prune --apply
```

## What it does

`SkillsPrune.prune()` runs two passes:

1. **Archive pass** — any skill with `last_activity_at` (or `created_at`) older than `archive_after_days` (default 30) is moved to the archive. Pinned and cron-referenced skills are never archived.
2. **Purge pass** — archived skills older than `archive_ttl_days` (default 60) are permanently deleted.

Without `--apply`, the command runs in dry-run mode and reports what would be pruned without modifying the tree.

## Completion

- `sac prune --apply` executed once.
- Archived and purged counts recorded.
- Skill tree is cleaned before the consolidation steps begin.

## Report

Add the prune results to the final report under a `LIFECYCLE PRUNE` section:

```text
LIFECYCLE PRUNE:
- archived: <count> skills
- purged: <count> skills
- kept (not idle): <count> skills
```

## Remembering

Record the following in the final report so the prune state is not lost:

- The `archive_after_days` and `archive_ttl_days` thresholds used.
- Which skills were archived (moved to `_archive/`).
- Which skills were permanently purged.
- Which skills were kept and why (pinned, cron-referenced, still active).