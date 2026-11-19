# Step 3: Final Report

Flush new issue patterns to the workspace memory file (if any) and deliver the final report to the user.

## Memory Flush

Flush the plan-weakness patterns the interview surfaced back to the shared workspace memory file, the same way `implement/references/grok/step-8-memory-flush.md` describes (generalize → categorize → harmonize → `sdc memory update` from the worktree):

```
cd <worktree_path> && sdc memory update --file <spec-json>
```

1. **Collect.** From `interview_summary_file` (and `open_questions_file` when non-empty): the recurring plan weaknesses the interview surfaced or escalated — e.g. "security-relevant decisions left open", "missing dependency edges between branches". One line each; skip when none.
2. **Generalize** (implement Step 8a rules): strip task-specific names (files, variables, feature names) and rewrite as reusable principles. Plan-document-specific patterns go to the `Planning` category; code-related ones reuse existing category names from `existing_patterns_snapshot` — do not invent near-duplicates.
3. **Harmonize phrasing** (implement Step 8b rules): a semantic match with an existing entry → use its exact description string so the helper merges onto it instead of appending a near-duplicate. Also dedup within the run's own list.
4. **Build the spec JSON** (omit `key_patterns` and `specializations` — the helper skips their lines; omit `issues_by_severity` — the interview has no severity mapping and the helper drops zero counts):

   ```json
   {
     "patterns": [
       {"category": "Planning", "description": "Plans leave security-relevant decisions in Open Questions instead of recommending one"}
     ],
     "run": {
       "date": null,
       "description": "grill: <interview topic, short label>",
       "rounds": <round_count>
     }
   }
   ```
5. **Invoke.** Write the spec to `grill-mem-<INTERVIEW_ID>.json` under `scratch_dir`, invoke the helper, and report its stats ("Memory updated: N new patterns, M merged into existing entries") — or "no new patterns" when the list was empty.
6. **Graceful degradation.** On non-zero exit, log a warning with the helper's stderr and continue — the interview is already complete; never fail the run over a memory flush.

## Provenance Convention

Every workflow tags its `run.description` with a short workflow prefix so the shared store's Recent Runs log records which workflow produced each entry: `impl: ` (implement), `exec: ` (execute-plan), `plan: ` (planner), `grill: ` (grill-me).

## Final Report

Report to the user:

- Repo: `<repo-path>`
- Interview ID: `<INTERVIEW_ID>`
- Branches walked: `<N>`
- Decisions resolved: `<M>`
- Open questions: `<K>` (list any escalated)
- Shared understanding: reached / not reached
- Summary file: `<interview_summary_file>`
- Worktree: `<worktree_path>` (commit `<sha>` if committed)

Stop.
