# Audit — Step 3: Repair loop until clean

**Goal:** re-scan after each repair round and stop only when `sac lint` exits 0 with zero issue lines, or when the round ceiling is reached.

Read-only step until a recipe writes: with `--dry-run`, stop after bucketing — print the issue table and the planned recipes, then go to step-5 for the report. No writes.

## 3.1 The loop

```
round = 0
self_repair = 0
loop:
  round += 1
  if round > 10: stop and report  # R16 repair-round ceiling — tested before any recipe runs
  sac lint; rc = $?
  if rc == 0 and no issue lines: break
  if rc == 2: fix the invocation; continue
  if sac catalog --check exits 3: sac catalog --build; continue
  bucket the issue lines          # step-1.3
  apply the class recipes         # step-2.1
```

With `--dry-run`, stop after bucketing: print the issue table and the planned recipes, then go to step-5 for the report. No writes.

A round is one `sac lint` plus the recipes it triggered. Do not re-fix a class in the same round.

**Self-repair iterations** count re-runs of the audit's own process after a process failure — a failed commit, a failed push, a failed catalog build. Increment `self_repair` on each such retry (step-4.5), and when `self_repair > 2`, stop and report the process failure with its command and exit code. Process failures are separate from lint repair rounds.

Process-failure retries in pseudocode:

```
on commit or push failure:
  self_repair += 1
  if self_repair > 2: stop and report
  fix the process failure (step-4.5 table) and retry
```

## 3.2 Stop conditions

| Condition | Action |
| --- | --- |
| `sac lint` exits 0, zero issue lines | leave the loop, go to step-4 |
| round reaches 10 | stop; report the remaining issue lines with class, subject, owning file; keep the fixes applied up to that round; never claim zero |
| a class is not in the step-2 map and not in the skill-improve rule catalog | stop; report the class and its file as an unowned violation |
| a fix would leave the allowed path set (R12) | stop; report the issue as out of scope |
| the working tree shows changes outside the audit's own task set after step-1 | a parallel agent or the user wrote during the run — stop; report the foreign files; never commit them |

## 3.3 Per-round record

Append to the scratch table under `/tmp/`:

| Round | Issue class | Subject | Fix applied | Lint exit after round | Issue lines left |
| --- | --- | --- | --- | --- | --- |

Also record the `self_repair` count and the resolved default branch from step-1.1.

The table is the audit trail the report summarizes; it is never committed.

## 3.4 Completion

- `sac lint` exits 0 with zero issue lines, or the round ceiling stopped the loop with a named remaining list.
- Every applied fix names its class and owner file in the scratch table.
- The run continues to [`step-4-commit-push.md`](step-4-commit-push.md) when clean, or to [`step-5-verify-report.md`](step-5-verify-report.md) when stopped.