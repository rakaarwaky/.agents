# Step 7: Final Report & Cleanup

## Memory Flush

Runs once per run, before the final report. The orchestrator performs it directly — no subagent is needed. The write goes through `sdc memory update --file <spec>` so an exclusive lock is held during read-merge-write (a concurrent run in another worktree of the same repo can't clobber the update); do not implement your own locking.

1. **Collect & generalize.** Use `plan_issue_patterns` (accumulated at Step 3). Generalize each pattern: the memory file exists to help *future* runs on *different* tasks, so strip task-specific details (file names, variable names, feature names) and rewrite each pattern as a reusable principle:
   - Bad: "PR 3's API surface depends on PR 1's interface but the edge is missing" → Good: "PR Plan entries missing explicit dependency edges"
   - Bad: "Plan omits migration for the existing config format" → Good: "Plans omit backward-compatibility or migration steps for existing data or config"
   - Bad: "Open Questions leaves the auth scheme undecided" → Good: "Plans leave security-relevant decisions in Open Questions instead of recommending one"
   If a pattern is *already* general, keep it as-is. Collapse near-duplicates into one entry.
2. **Categorize & harmonize.** Reuse existing category names from `existing_patterns_snapshot` whenever the pattern fits — do not invent near-duplicate categories. For plan-document-specific patterns use the `Planning` category. For each pattern, scan `existing_patterns_snapshot` for a semantically equivalent entry; if one exists, use the **exact existing description string** so the helper's normalised match merges onto it. Also dedup within the run's own list.
3. **Build the spec JSON** (omit `specializations` — the planner has no specialization panel; the helper skips the line). If `plan_issue_patterns` is empty, skip the flush entirely and report "no new patterns":

   ```json
   {
     "patterns": [
       {"category": "Planning", "description": "PR Plan entries missing explicit dependency edges"},
       {"category": "Testing", "description": "Missing tests for error/edge case paths"}
     ],
     "run": {
       "date": "2026-05-19",
       "description": "plan: retry-logic feature",
       "rounds": 2,
       "issues_by_severity": {"bug": 1, "suggestion": 2, "nit": 0},
       "key_patterns": ["PR Plan entries missing explicit dependency edges"]
     }
   }
   ```

   `run.description` is the planning task trimmed to a short label (the helper strips internal double quotes and wraps it in exactly one outer pair). Prefix the label with the `plan: ` workflow tag — provenance convention shared by all four memory workflows (`impl: ` implement, `exec: ` execute-plan, `plan: ` planner, `grill: ` grill-me) — so the store's Recent Runs log records which workflow produced each entry. `run.rounds` is `round_count`; `run.issues_by_severity` is `total_issues_by_severity` (zero-count severities are dropped by the helper). `run.key_patterns`: the 2-3 most-significant generalized patterns, severity-ranked (bug > suggestion > nit).
4. **Invoke.** Write the spec to `<scratch_dir>/plan-mem-<PLAN_ID>.json` with the `write` tool (a temp file avoids heredoc quoting issues), then:

   ```
   sdc memory update --file <scratch_dir>/plan-mem-<PLAN_ID>.json
   ```

   The helper acquires the lock, merges (deduping case/whitespace/punctuation-insensitively within each category), caps categories at 25 patterns and Recent Runs at 20 entries, writes atomically, and prints a JSON stats summary on stdout. Report: "Memory updated: N new patterns, M merged into existing entries (file at <file>)." — or, when `existed_before` is `false`: "Memory file created at <file> with N patterns."
5. **Graceful degradation.** On non-zero exit, log a warning with the helper's stderr and continue to the final report — never fail the run over a memory flush.

   | Exit | Meaning |
   |------|---------|
   | `0` | success |
   | `1` | unexpected I/O error |
   | `2` | workspace id could not be determined |
   | `3` | lock could not be acquired within 30s (another concurrent run holds it; retrying once usually works) |
   | `4` | spec malformed or type-invalid (stderr identifies the offending field — surface it verbatim) |

## Final Report

Present a final summary to the user containing:

1. The absolute path to `<plan_doc_file>`.
2. Total review rounds (`round_count`).
3. Issue breakdown (`total_issues_by_severity`).
4. Resolved open questions (or state "None").
5. Memory update status (file path plus the helper's stats, or "no new patterns", or a degradation note when the flush failed).
6. Next action: run `/execute-plan <plan-doc-file-path>` to implement the PR plan.

## Cleanup

Do NOT delete the plan summary or review files. Hermes (Step 1 of the Hermes lane) reads these files to verify the run:

- `plan-summary-<run_id>.md` — the plan summary
- `plan-review-<run_id>.md` — the plan review

These files are the verification gate. Grok must not delete what Hermes consumes.

**Hermes owns post-verification cleanup** — Hermes Step 3 runs `sdc host cleanup` on these files after it has read them and produced the final report.

The plan document itself is kept.