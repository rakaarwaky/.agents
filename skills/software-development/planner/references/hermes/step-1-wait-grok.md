# Step 1: Wait for Grok to Finish

Grok Build runs the full write → review → revise loop itself — `plan-doc-writer` and `plan-doc-reviewer` subagents inside its own skill — driven by its `grok/` references. Hermes waits and does nothing else.

## Wait

Run `sdc pool grok <terminal_handle> --wait` to poll until Grok finishes. The `sdc pool` command is the standardized grok-session poller — it reads the rendered screen (`orca terminal read --screen --json`), paces with `orca terminal wait --for tui-idle`, and detects completion from either the `EXECUTE_PLAN_COMPLETE` sentinel or a final-report shape (PR marker + settled prompt) on an idle screen.

```bash
sdc pool grok <terminal_handle> --wait
```

- Without `--wait`, `sdc pool grok <terminal_handle>` performs a single probe and returns immediately with JSON status.
- With `--wait`, it blocks until completion, failure, or deadline (default 2 hours).
- Exit codes: `0` = success (done), `1` = runtime error (orca CLI failure or terminal exited without final report), `3` = deadline exceeded (status still running, `timed_out=true`).
- Override pacing with `--wait-ms` (default 15000), `--idle-confirm` (default 2), `--tail` (default 50), `--sentinel`, `--orca` (default `orca-ide`).
- Heartbeat progress lines go to stderr; the JSON result goes to stdout.
- `tui-idle` returning not-satisfied means Grok is BUSY, not that the poll failed — keep polling. Only a genuine CLI/parse failure counts as an error.
- Run exactly one poll loop at a time. Before starting a fresh loop, kill any existing `sdc pool grok` processes for the same terminal handle.
- Long runtime is not a stall signal — do not escalate, interrupt, or re-spawn before ~90 minutes.

### Silent-loop pitfall

Grok's write→review→revise loop can run many rounds while the terminal emits no visible output for minutes at a time. Do not treat silence as failure or completion. The Grok TUI redraws in place and may emit zero stream lines for the entire loop — `terminal read` can return `returnedLineCount: 0` and leave `nextCursor` frozen at its initial value (e.g. `1`) the whole time, which is normal, not a stuck cursor. Cross-check progress by listing `~/.agents/develop/<repo-slug>/plan/` and comparing `plan-doc-*` mtimes between polls; a changing mtime means the loop is still active. Treat "no mtime change across ~8 polls (~4 min) + `plan-summary-*` present" as the completion signal when the cursor never advances. Do not send text while waiting.

### Cleanup pitfall

Grok's final step removes `plan-review-*` and `plan-summary-*` from the plan dir, leaving only `plan-doc-*`. Confirm 0 open issues by reading the review file *before* it disappears; once cleanup completes, rely on the last observed review state plus the presence of the final plan doc. The reviewer subagent and the cleanup step can both run inside a single `terminal wait` window, so polling with a coarse cadence may never observe the `plan-review-*` file at all — it is written and removed between two polls. When no review file is ever observed, the post-cleanup verification fallback (step 2a) is the evidence: treat the run as approved if `plan-doc-*` and `plan-summary-*` both exist, the summary records decisions as resolved, and the plan doc's `## Open Questions` section reads `None`.

### Orca unreachable on completion

Orca can return `runtime_unavailable` ("This terminal could not connect to Orca") right as Grok finishes — the long-lived Orca-backed terminal drops its runtime connection after the loop settles. Do not treat this as a Grok failure or retry the read in a loop. The artifacts on disk are authoritative: if `plan-doc-*` and `plan-summary-*` exist and are complete, proceed to Step 2 using them. Only fall back to `orca status --json` to diagnose Orca itself if the artifacts are missing or truncated.

## When Grok Is Done

Grok writes artifacts to its scratch dir (`~/.agents/develop/<repo-slug>/plan/`):

- **plan document**: `plan-doc-<PLAN_ID>.md` — the polished doc including the `## PR Plan` section (this survives Grok's cleanup).
- **Summary**: `plan-summary-<PLAN_ID>.md` — key decisions, open questions, PR plan.
- **Review**: `plan-review-<PLAN_ID>.md` — the final review file; must show 0 open issues when the loop exits.

The run id appears in Grok's terminal output. Read the summary first, then confirm the review file shows 0 open issues **before Grok's cleanup removes it**. If any issue carries `Status: needs-user-input`, that is an open decision for the user — surface it before proceeding to Step 2. If Grok reports failure or exits non-idle with an error, report it verbatim to the user and stop — do not retry, do not hand-write the document yourself.

Report to the user: "Grok Build finished the plan run. <N> review rounds, 0 open issues (or: <K> issues need your input). plan doc: <path>."

Then proceed to Step 2.