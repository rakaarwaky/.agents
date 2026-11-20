# Step 2: Verify, Commit, Push, Open PR

Hermes owns every git and PR operation. Verify the worktree state directly, read Grok's summary and review files only if they exist, then commit, push, and open the PR.

## 2a: Verify the Worktree (primary proof)

Start from the diff, not the artifacts — Grok runs may leave no review files, and the worktree diff is the real evidence the task landed:

1. `git -C <worktree_path> diff` — inspect the changes against the Step 0 brief. Confirm the edit matches scope (and only touches in-scope files).
2. `git -C <worktree_path> status --short` — audit the working tree. Any out-of-scope path (sibling tree, new top-level directory, stray lockfile) → revert it in Hermes's own tools (`git -C <worktree_path> checkout -- <path>` / `rm` for untracked).
3. Run the repo's local gate against the clean tree (per AGENTS.md / the repo's lint commands — e.g. `npm test -- --run`, `pytest`, `ruff check`, etc.). A dirty-tree green is not a proof; clean the tree first, then run. When a gate fails, compare against the same gate on `origin/main` (a separate checkout) before blaming the change — a pre-existing failure in an untouched area is not a regression this run introduced.

   **Pitfall — run the JS/TS gate from the package root, not the repo root.** In repos that keep `package.json` in a `packages/` subdirectory (with the Python project at the repo root), `npm test` from the worktree root fails `ENOENT: no such file or directory, open '.../package.json'`. `cd` into the directory that actually contains `package.json` first. The Python gates (`ruff`, `mypy`, `pytest`) run from the repo root against `modules/`.

   **Pitfall — worktree has no `.venv`.** Grok may create its own virtualenv or use the main repo's. Before running tests, check if `.venv/bin/python` exists in the worktree; if not, create it with `python3 -m venv .venv && .venv/bin/pip install -q pytest ruff` then run tests with `PYTHONPATH=modules .venv/bin/python -m pytest modules/ -q -m "not dogfood"`.
4. Run `lint-arwaky-cli report .` from the worktree (absolute path: `$HOME/.local/bin/lint-arwaky-cli`). This is the end-of-run lint gate: the Delta column must be zero or negative versus the start-turn baseline recorded in `hermes/step-0-plan-and-spawn.md`. A positive delta means the run introduced new lint violations — stop, revert the offending changes, and re-run the gate before proceeding to commit. Include the final report output in the run log. If the CLI is unavailable, note the failure and continue.

**Pitfall — CLI exception handler must include new error classes.** When Grok adds a new `SdcError` subclass (e.g. `MemoryUsageError` for UX-S5-004) and the fix brief touches the CLI surface, the exception handler in `surface_sdc_command.py` (`except (...)` tuple) must be updated to catch the new class — otherwise the exit code won't propagate and the error escapes as an unhandled exception. This is a legitimate 1-line change to an otherwise out-of-scope file; do not revert it as out-of-scope.

## 2b: Read Grok's Artifacts (optional)

Grok normally writes review files to `/tmp/grok-<username>/`, keyed by `REVIEW_ID`:

- `impl-summary-<run_id>.md` — what was changed, plan decisions.
- `review-<run_id>.md` — the final merged review.

If they exist and `review-<run_id>.md` shows **open issues**, stop and report to the user — do not fix them yourself. If no artifacts exist (headless / single-pass run), skip this step; the 2a worktree diff + local gate + lint gate are the complete verification.

## 2c: Commit

Grok was instructed NOT to commit in Step 0. If the worktree has no commit yet, make the single orchestrator commit:

```
git -C <worktree_path> add -A && git -C <worktree_path> commit -m "<task description>"
```

Commit message: conventional, repo-conforming. If Grok left stray artifacts (scratch files, agent-narration commit messages), amend before pushing: `git rm --cached <artifact>` + `git commit --amend -m "<conventional message>"`.

## 2d: Push

```bash
git -C <worktree_path> push --force-with-lease origin <worktree_branch>
```

Always `--force-with-lease`, never bare `--force`.

**Branch protection:** if push to `main` is rejected with `repository rule violations` / required status checks, do not force-push to `main`. Instead push a feature branch and open a PR against `main`:

```bash
git -C <worktree_path> push -u origin <worktree_branch>
```

Then open the PR with `gh pr create --base main --head <worktree_branch>`. A rejected push to `main` is not a reason to bypass CI gates — the PR lane is the supported path.

## 2e: Open the PR (default — mandatory, never a draft)

Creating a PR is the default and expected outcome of every run. Open a **ready-for-review** PR (not a draft) whenever `gh` is available and the remote is GitHub:

```
gh pr create --base main --head <worktree_branch> --fill
```

Drop `--fill` and pass an explicit `--title`/`--body` if you have a richer summary to attach. **Never pass `--draft`** — drafts are forbidden in this workflow; every PR must be ready for review the moment it is opened.

No `gh` or non-GitHub remote: derive the compare URL

```
https://<host>/<owner>/<repo>/compare/main...<worktree_branch>?expand=1
```

Strip any `user[:pass]@` from the remote URL before logging it. Treat a missing `gh`/non-GitHub remote as an environment limitation to report — not as permission to skip shipping the branch for review.

## 2f: Report

Report to the user:

> Implemented via Grok Build in <worktree_path>. PR: <url>. <N issues raised by the review panel, all resolved | headless run; verified via worktree diff and gates>. Memory file updated at <path> (or "no memory update — Grok reported no new patterns").

Then proceed to Step 3.
