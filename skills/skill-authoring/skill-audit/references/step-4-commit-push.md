# Audit — Step 4: Rebuild catalog, commit, push

**Goal:** ship the fixed pack as one commit on the pack default branch, with the remote head verified.

With `--dry-run`, print the commands this step would run and stop — no catalog build, no staging, no commit, no push.

## 4.1 Rebuild the catalog

```bash
cd "$(git rev-parse --show-toplevel)"
sac catalog --build; echo "exit=$?"
git status --short skills/catalog.json
```

`sac catalog --build` rewrites `skills/catalog.json` from current frontmatter. A non-zero exit means the pack root or `modules/` is wrong — report it and stop; do not commit a stale catalog.

If `sac catalog --build` is unavailable (broken CLI), stage the existing `skills/catalog.json` only when its content already matches the new frontmatter, and state the missing rebuild in the report.

## 4.2 Re-lint before staging

```bash
sac lint; echo "exit=$?"
```

Only a clean scan proceeds. A scan that regressed sends the run back to step-3.

## 4.3 Stage explicit paths

Never `git add -A`. Stage the touched skills plus the catalog:

```bash
git add skills/<cat1>/<skill1> skills/<cat2>/<skill2> skills/catalog.json
git diff --cached --name-only
```

For a skill archived as a fix, stage the deletion path (`git add skills/<cat>/<skill>`) — `git add` on a removed directory stages its removal.

The staged set must be a subset of: touched skill directories, `skills/<cat>/DESCRIPTION.md` for edited categories, and `skills/catalog.json`. If the list contains any other path, unstage it (`git restore --staged <path>`) and re-check.

### 4.3a Archive residue

`sac archive` writes to `~/.agents/skills/.archive/<cat>/<skill>`, which on this host is inside the repo at `skills/.archive/` and is not gitignored (`.gitignore` un-ignores `/skills/_archive/` only). An archived skill therefore leaves untracked files under `skills/.archive/` after the move.

Check and decide:

```bash
git status --porcelain skills/.archive
```

- If the audit archived a skill as a fix, the move is part of the fix: stage the deletion (`git add skills/<cat>/<skill>`) and commit the removal. Leave `skills/.archive/` untracked — it is the archive store, not pack content — and note it in the report.
- If `skills/.archive/` is empty, remove the empty tree (`rmdir skills/.archive/<cat> skills/.archive`).
- R14's clean-tree check applies to tracked files; an untracked archive store is reported, not committed.

## 4.4 Commit

```bash
git commit -m "fix(skills): clear sac lint violations to 0

<classes fixed, one per line>
<lint before: N issues -> after: 0>"
```

Conventional commit, `fix(skills)` scope, body naming the classes and the before/after counts. One commit per audit run.

## 4.5 Push

```bash
git rev-parse --abbrev-ref --symbolic-full-name @{u}
git push
git fetch origin
git rev-parse HEAD
git rev-parse @{u}
```

The last two SHAs must be equal for the push to be confirmed.

| Push failure | Cause | Recovery |
| --- | --- | --- |
| `! [rejected] ... non-fast-forward` | remote advanced | `git fetch origin && git rebase origin/<branch>`; re-run `sac lint`; `git push` |
| `! [rejected] ... missing current branch in remote` | no upstream | `git push -u origin <branch>` once, then re-verify |
| auth / permission error | credentials | report; do not retry more than twice |
| `sac archive` printed "No files were modified" but the skill moved | the renderer prints that message whenever the verb returns without a plan and carries a message; archive's outcome dict is non-empty, so it prints while the skill has already moved | treat the archive as applied; verify with `git status --porcelain` on the skill path and `skills/.archive` |
| pre-commit hook rejects the commit | hook failure or staged path outside scope | read the hook output; fix the flagged file in the same worktree or `git restore --staged <path>`; re-commit |

Never `git push --force`. Never `git reset --hard` except the documented rollback in step-5.

## 4.6 Completion

- `sac catalog --build` exited 0.
- `sac lint` exited 0 before staging.
- `git diff --cached --name-only` lists only task files + `catalog.json`.
- One commit exists on the pack default branch; local and upstream SHAs match.
- The run continues to [`step-5-verify-report.md`](step-5-verify-report.md).