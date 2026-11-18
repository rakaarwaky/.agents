# Step 2: Dependency Resolution

Resolve dependencies between decisions one-by-one. A decision that depends on another cannot be considered resolved until its dependency is resolved.

## Dependency Chain

Each entry in `decisions_resolved` carries a `depends_on` list referencing earlier decisions. Process decisions in dependency order:

1. Pick an unresolved decision whose dependencies are all in `decisions_resolved`.
2. If it still needs user input, ask ONE question (codebase-first, then user).
3. Record the answer and mark the decision resolved.
4. Re-scan: newly unblocked decisions become eligible.

## Stalemate Detection

If a full pass over all pending decisions resolves nothing (every remaining decision is blocked on an open question or an unresolved dependency), report the stalemate:

> Stalemate at round <round_count>: <N> decisions blocked on open questions: <question list>.

Ask the user to resolve the blocking questions. Do not silently skip.

## Orchestrator State Updates

- `decisions_resolved`: update entries as dependencies clear.
- `open_questions`: questions whose answers unblock decisions move to `decisions_resolved`.

## Report

> Dependencies resolved: <N> decisions, <M> open questions remaining.

Proceed to Step 3 (Exit Check).
