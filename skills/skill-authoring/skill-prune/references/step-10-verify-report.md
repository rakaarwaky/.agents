# Step 10: Verify and report

Check the executed prune and write the final report the user reads.

**Goal:** verify the merge produced a clean tree and emit the final report with a rollback target.

## Rollback protocol

Verification is the gate for rollback:

1. **Hard failure** — a `SKILL.md` no longer parses, a `references/` link is broken, or two skills share a `name:`. Restore the snapshot (`git reset --hard <sha>` or `git stash pop`), re-run only the offending merge, and re-verify. Record the failure in the report under a `FAILURES` section with the step that failed and the recovery action taken.
2. **Soft failure** — a merge looks structurally valid but content was lost or contradicted. Restore the affected files only, keep the rest of the prune, and flag the conflict for manual resolution. Record the soft failure and the conflict description in the report.
3. If the user aborts between snapshot and execution, restore the snapshot and leave the tree unchanged. Record the abort and the snapshot SHA in the report.

## Report format

The shape of the final executed `skill-prune` report:

```text
skill-prune report — <audit root>

LIFECYCLE RUN:
- transitions applied: <count>
- skills skipped: <count>
- state distribution: <active: N, stale: N, archived: N>
- paused: <true | false>

LIFECYCLE PRUNE:
- archived: <count> skills
- purged: <count> skills
- kept (not idle): <count> skills

MERGED:
- <surviving folder>  <-  <dropped folder(s)>
    reason: <duplicate scope / shared domain>
    action:  <body merged | references/ created for scenarios: a, b | duplicates dropped>

KEPT SEPARATE:
- <skill A> vs <skill B>  —  reason: <distinct jobs, e.g. different completion criteria>

DELETED:
- <folder>  —  reason: <true duplicate of <survivor>, stale name collision, empty category cleanup>

FAILURES (if any):
- <step> — <failure description> — <recovery action taken>

ROLLBACK TARGET:
- <snapshot commit SHA or stash ref>

VERIFY:
- `sac catalog --build && sac catalog --read` — confirm the expected skill count (N remain, dropped folders absent)
- `sac lint` — 0 shared names, all frontmatter parses, no empty categories
- `sac catalog --build` — rebuilt; all surviving skills and references resolve
```

## Completion

- All three VERIFY commands pass: `sac catalog` count, `sac lint` clean, `sac catalog` rebuilt.
- The report carries the LIFECYCLE RUN, LIFECYCLE PRUNE, MERGED, KEPT SEPARATE, DELETED, and ROLLBACK TARGET sections.
- On any hard failure the snapshot is restored and the offending merge re-ran.
