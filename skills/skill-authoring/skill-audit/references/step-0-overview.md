# Audit — Step 0: Overview

Run the loop scan → fix → rebuild → commit → push. Stop when `sac lint` exits 0 and the pack is pushed.

**Precondition:** the pack root is the git repo holding `skills/`, `skills/catalog.json`, `modules/`, and `pyproject.toml` — `/home/raka/.agents` on this host. Resolve with `git rev-parse --show-toplevel`; never hardcode a home path.

**Root assertion:** each `sac` verb resolves its own root via `default_pack_root()` — `~/.agents/skills` — and takes no path argument. `git` and `git mv` act on the git root. Assert equality before step-1:

```bash
test "$(git rev-parse --show-toplevel)/skills" = "$HOME/.agents/skills" && echo "root OK" || echo "ROOT MISMATCH"
```

On `ROOT MISMATCH`, stop and report both paths. The audit never lints one tree and commits another.

**Guard:** if `git status --short` is non-empty, stop. Report the pre-existing dirty files; the user decides. The audit never commits another agent's work.

## Issue classes the pack emits

`sac lint` names every issue in square brackets; the class is the text before the first `]`.

| Class | Meaning | Owner |
| --- | --- | --- |
| `missing-category-description` | a category has no `DESCRIPTION.md` | step-2 |
| `empty-category-description` | a category's `DESCRIPTION.md` is blank | step-2 |
| `name-mismatch` | frontmatter `name:` differs from the directory name | step-2 |
| `too-deep` | `SKILL.md` sits deeper than `<category>/<skill>/SKILL.md` | step-2 |
| `duplicate-skill-name` | the same `name:` appears in two directories | step-2 |
| `duplicate-description` | two skills share one description | step-2 |
| `reference-not-linked` | a file in `references/` has no link in `SKILL.md` | step-2 |
| `empty-category` | a category holds no skills | step-2 fallback |
| `invalid-skill-name`, `invalid-placement`, `missing-description`, `invalid-description-characters`, `description-too-long` | frontmatter/placement rule violations from the linter's rule catalog | step-2 fallback |
| any other class | open the linter's rule catalog in `skill-improve/references/step-1-format.md`, fix at the owner, report the class | step-2 fallback |

**Read-only step.** Steps 0 and 1 write nothing; `--dry-run` skips nothing here.

## Completion

- Pack root resolved via `git rev-parse --show-toplevel`.
- Pre-run guard passed: `git status --short` empty.
- Issue classes known before step-1 scans.
- Continue to [`step-1-scan.md`](step-1-scan.md).