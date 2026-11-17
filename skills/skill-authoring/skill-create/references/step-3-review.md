# Create — Step 3: Review the draft

**Goal:** a subagent reviewer checks the draft under `$DRAFT_DIR` (the system temp directory resolved in step-2) against all ten core questions. If any issue is open, send it back to step 2 (drafting) for the drafter to fix via `resume_from`, then re-review. Loop until the reviewer reports 0 issues. Only then write to the real skills directory.

## Spawn reviewer subagent

Spawn a reviewer subagent with `spawn_subagent`. The reviewer reads the draft under `$DRAFT_DIR` produced by step 2.

Reviewer prompt:

```
You are a reviewer for a draft skill under <DRAFT_DIR>/ (the system temp directory).

Read the draft SKILL.md and every file under references/ and template/ (if present).

Check each of the ten core questions (Q1–Q10):
1. Is the answer present in the artifact?
2. Does it name paths, commands, numbers, or steps (score 2)?
3. Is any answer ambiguous, vague, or requiring a guess (score 0 or 1)?
4. Is every answer placed in its assigned home — success metric, audience and tone, tools, ceilings, and report shape as Rules rows; activation and precondition in the trigger fields; read-inputs, steps, branches, and fallback in the step files that own them?
5. Are all reference files linked from SKILL.md (no unlinked references)?

Also verify:
- description: names artifact + action in third person, no redundant trigger phrase that restates the artifact
- when-to-use: carries all activation conditions, synonyms, and negative scope ("not for X")
- description: and when-to-use: share no phrase

Report findings as a structured issue list:
- File: <path>
- Question: Q1..Q10
- Severity: bug / suggestion / nit
- Description: what is missing or ambiguous
- Suggestion: concrete fix
- Status: open

If all ten questions are answered at score 2 with no ambiguity, correct placement, non-overlapping trigger fields, and no unlinked references, report "0 issues". Otherwise list every issue with Status: open.
```

## Merge & exit condition

The **only** exit condition is the reviewer reporting **0 issues** of any severity. If the reviewer reports any open issues:

1. Report the issues to the user.
2. Send the drafter back to step 2 (`step-2-drafting.md`) via `resume_from` with the full issue list so the drafter fixes every open issue.
3. Resend the fixed draft to this reviewer step.
4. Loop until the reviewer reports 0 issues.

There is no iteration cap — the loop runs until 0 issues.

## Write to the real skills directory

Only after the reviewer reports 0 issues **and** the run is **not** `--dry-run`:

1. Copy the draft under `$DRAFT_DIR` (SKILL.md + references/ + template/ if present) to the real skill directory under `skills/<category>/<skill-name>/`.
2. Run `sac lint` (or `sac lint --category <category>`) to verify frontmatter, naming, placement, and reference linking.
3. Run `sac catalog --build` to register the skill.
4. Remove the draft: `rm -rf "$DRAFT_DIR"`.

If `sac lint` fails, fix in the same draft, re-run this reviewer step, then copy to the real directory.

With `--dry-run`, stop after the reviewer reports 0 issues. Do not copy anything to the skills directory, do not run `sac lint` against disk state, and do not rebuild the catalog. Proceed directly to step 5 (`step-5-verify.md`) for the terminal report.

## Completion

- The reviewer reported 0 issues of any severity.
- The draft was copied to the real skills directory, `sac lint` passed, the catalog was rebuilt, and `$DRAFT_DIR` was removed.
- Every default used is logged as `assumed` in the scratch sheet.
- With `--dry-run`, stop here and proceed to step 5 (`step-5-verify.md`) for the terminal report.
- Otherwise, the run continues to step 4 (`step-4-write.md`).
