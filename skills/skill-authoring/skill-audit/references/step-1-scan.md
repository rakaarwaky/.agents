# Audit — Step 1: Scan and bucket

**Goal:** record the pre-state and turn `sac lint` output into a fix table.

## 1.1 Record the pre-state

```bash
cd "$(git rev-parse --show-toplevel)"
git rev-parse HEAD          # snapshot SHA for rollback
git status --short          # must be empty; otherwise stop (step-0 guard)
git log --oneline -5        # parallel-agent check
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'
git config user.name
git config user.email
```

Record the snapshot SHA and the default branch in the report. `git symbolic-ref refs/remotes/origin/HEAD` prints the pack default branch (for example `main`); the audit pushes to that branch and to no other. If `git config user.name` or `user.email` is empty, the commit will fail — report the missing identity and stop, or ask the user to set it.

## 1.2 Run the scan

```bash
sac lint; echo "exit=$?"
```

Exit codes: `0` clean, `1` issues found, `2` usage error. Catalog drift is a separate gate: `sac catalog --check` exits `3` when `skills/catalog.json` does not match the tree; run `sac catalog --build`, then scan again. A lint run that reports issues always exits `1`, stale catalog or not.

`--category <name>` scopes the issues to one category, but the exit code stays `1` whenever any library-wide weed line (duplicates, empty categories) exists — `weed_lines` are kept unfiltered and counted. Verify a scoped fix by grepping the output for the class and subject, not by the exit code.

## 1.3 Bucket every issue

Each line below the count header is one issue. Parse `[<class>] <subject>: <detail>`.

When `duplicate-description` or `missing-category-description` needs the catalog index, read it with `sac catalog --read` (or open `skills/catalog.json`) to see every skill's registered description and category in one place. `sac discover` is unreliable in this pack — its renderer prints names only and currently returns no matches — so read paths from the `sac lint` issue line or `skills/catalog.json` instead.

When a `duplicate-skill-name` issue appears, the two paths are in the issue line itself (`... appears in: <cat1>/<name>, <cat2>/<name>`); `sac archive` resolves a bare name to the alphabetically first match (`find_skill_dir` → `min(matches)`), so record which path that is before archiving.

When a `duplicate-description` issue appears, the paths are in the issue line (`... appears in: <cat1>/<name>, <cat2>/<name>`); fix the description in the loser's `SKILL.md` or archive the loser by bare name after the alphabetical-first check.

| Field | Example | Used for |
| --- | --- | --- |
| class | `too-deep` | which step-2 recipe applies |
| subject | `figcraft/figure-skills/paper-figure` | the directory or skill to act on |
| detail | `SKILL.md is nested deeper than category/skill/SKILL.md` | what is wrong |

Write the table as a scratch file under `/tmp/` — class, subject, detail, planned fix. Never write it into the pack.

## 1.4 Fall back when `sac` is broken

If `sac` is missing or crashes with `ModuleNotFoundError: No module named 'cli'`, the CLI or `modules/` is broken. Run the equivalent probes:

```bash
# body shape
grep -n '^#' skills/*/*/SKILL.md | head -50
# unlinked references
for d in skills/*/*/references; do
  for f in "$d"/*; do
    n=$(basename "$f")
    grep -q "$n" "$(dirname "$d")/SKILL.md" || echo "unlinked: $d/$n"
  done
done
# frontmatter name vs directory
for s in skills/*/*/SKILL.md; do
  n=$(grep -m1 '^name:' "$s" | sed 's/name: *//; s/"//g')
  d=$(basename "$(dirname "$s")")
  [ "$n" != "$d" ] && echo "name-mismatch: $s ($n vs $d)"
done
```

Report the fallback explicitly. A broken gate is an infra defect, not a blocker.

## Completion

- Snapshot SHA, branch, and pre-run `git status` recorded.
- `sac lint` run; exit code captured.
- Every issue line bucketed into class, subject, detail, planned fix.
- Fallback probes run when `sac` is unavailable.
- The run continues to [`step-2-fix.md`](step-2-fix.md).