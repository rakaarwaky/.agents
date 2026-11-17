# Audit — Step 5: Verify and report

Confirm the pack is clean and pushed, score the run against the ten core questions, emit one report.

## 5.1 Verify

```bash
cd "$(git rev-parse --show-toplevel)"
sac lint; echo "lint_exit=$?"            # 0 and zero issue lines
sac read skill-audit >/dev/null; echo "read_exit=$?"   # skill registered
test -z "$(git status --porcelain --untracked-files=no)" && echo "status empty" || echo "status dirty"
git rev-parse HEAD
git rev-parse @{u}
git log --oneline -1
```

With `--dry-run`, emit the report from the plan (step-3) and write nothing.

| Check | Pass condition |
| --- | --- |
| lint | exit 0, no `- [` issue lines |
| catalog | `sac catalog --check` exits 0 |
| remote | `git rev-parse HEAD` equals `git rev-parse @{u}` |
| commit | `git show --stat <sha>` lists only touched skills + `catalog.json` |
| guard | no modified or staged tracked file outside the commit; an untracked `skills/.archive/` residue is reported per step-4.3a |

## 5.2 Report

Emit one report with all five parts:

1. **Changed files** — table: path, action (fix / move / archive / catalog), class resolved.
2. **Lint results** — issues before (count), issues after (count), final exit code, rounds used.
3. **Score block** — from the step-2 sheet, unchanged.
4. **Gate verdict** — `Gate: PASS` or `Gate: FAIL` with the remaining gap list.
5. **Assumptions** — every `assumed` default.

### Quality score — skill-audit

| Question | Score | Evidence (path:line or command) | Gap / patch |
| --- | --- | --- | --- |
| What & why | 2 | SKILL.md R14 (`sac lint` exit 0 + zero issues + `git status --porcelain` empty + upstream match) | — |
| When & where | 2 | frontmatter `when-to-use:`; step-0 pack-root guard | — |
| Who | 2 | SKILL.md R19 | — |
| From where | 2 | step-1.1 pre-state, step-1.2 scan, step-1.3 bucket table | — |
| By what means | 2 | SKILL.md R12 tools/forbidden; step-2.1 recipes | — |
| How | 2 | Routing steps 0–5, each with a completion block | — |
| How far | 2 | SKILL.md R16 (10 rounds, 2 self-repair, one push, path set) | — |
| Whether | 2 | step-0 class table; step-2.2 branch table; step-3.2 stop conditions | — |
| What kind | 2 | SKILL.md R20 report shape; this step's five parts | — |
| How come | 2 | step-1.4 fallback; step-3.2 stops; step-4.5 push failures; rollback in step-5.4 | — |

Total: 20/20 · N/A: none · Gate: PASS
Cycles used: 0 · Remaining gaps: none

## 5.3 Fallback table

| Failure symptom | Probable cause | Recovery |
| --- | --- | --- |
| `sac lint` not found or `ModuleNotFoundError: cli` | broken `sac`, missing `modules/` | run step-1.4 grep probes; report the fallback; continue |
| `sac catalog --check` exits 3 | catalog drift | `sac catalog --build`; re-scan |
| `sac archive` printed "No files were modified" but the skill moved | the renderer prints that message whenever the verb returns without a plan and carries a message; archive's outcome dict is non-empty, so it prints while the skill has already moved | treat as applied; verify with `git status --porcelain`; handle the `skills/.archive` residue per step-4.3a |
| `sac read skill-audit` fails | frontmatter unclosed or misquoted | quote the description on one line; verify the second `---` precedes `# Title`; re-scan |
| a violation survives 2 rounds | misdiagnosed class | re-bucket from the rule catalog; report the owning file; stop if unresolved after round 10 |
| `git commit` rejected | staged path outside scope | `git restore --staged <path>`; restage only task files |
| `git push` non-fast-forward | remote advanced | fetch, rebase, re-lint, push |
| 10 rounds exhausted | ambiguous or unowned violation | report the issue list with owner files; never claim zero; never force-push |
| a fix broke a skill body | bad edit or bad move | `git reset --hard <snapshot SHA>`; restart the loop at step-1; republish with `git push --force-with-lease` per 5.4 |

## 5.4 Rollback

The undo path is the snapshot SHA recorded in step-1.1:

```bash
git reset --hard <snapshot SHA>
git push --force-with-lease
```

`--force-with-lease` is the only force path, used once, after the user confirms. A run that cannot commit never needs it: the working tree holds the fixes until reset.

## Completion

- All five verify checks pass, or the failing check is reported with its fallback.
- The report carries changed files, lint before/after, the score block, the gate verdict, and the assumptions.
- `--dry-run` emits this report from the plan and writes nothing.