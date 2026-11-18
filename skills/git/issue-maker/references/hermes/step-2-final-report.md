# Step 2: Final Report (Hermes)

Summarize the run report (ledger + `task-tracker-report.json` in `~/.agents/develop/<namarepo>/issue-maker/`):

- Rows discovered, rows classified per class, actionable rows → issues opened (or deferred under `--dry-run`), rows with `done` verdict already at target state.
- Each issue's closing condition vs. its source doc's target row state.
- `--gh` results: each recorded issue number confirmed `OPEN` / `deferred-to-gh` / rate-limit reported.
- Invariant result: fix-all-open-issues ⇔ all FR states = Done (pass/fail).
- Confirm no source edits, no branch, no PR — issue-maker stays issues-only.

No Grok session, no Orca worktree, no PR, no merge in this skill. Report "issue-maker audit complete."
