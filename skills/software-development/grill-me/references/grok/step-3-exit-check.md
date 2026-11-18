# Step 3: Exit Check

Determine whether the interview is complete.

## Exit Condition

The interview stops when ALL of the following hold:

- Every branch of the design tree has been walked (`branches_walked` covers all branches).
- All dependencies between decisions are resolved (`decisions_resolved` covers all decisions with no pending `depends_on`).
- `open_questions` is empty (every question was answered by codebase exploration or by the user).
- Shared understanding reached: the user has confirmed the resolved decisions match their intent.

## Stalemate Escalation

If open questions remain after two consecutive rounds with no progress, escalate to the user:

> Cannot reach shared understanding: <N> open questions remain unresolved. Please answer: <question list>.

## Report When Complete

> Interview complete. <N> branches walked, <M> decisions resolved, shared understanding reached.
> Summary written to <interview_summary_file>.

Proceed to Step 4 (Cleanup).
