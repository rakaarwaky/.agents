# Step 1: Branch Walk

Walk every branch of the design tree, one-by-one, resolving dependencies between decisions as you go. If a question can be answered by exploring the codebase, explore the codebase instead of asking the user.

## Codebase-First Probing

Before asking the user any question, check whether the answer is already in the codebase:

- Search for the relevant code paths, configs, or docs using `search_files` and `read_file`.
- Trace each symbol to its definition and usages rather than guessing its shape.
- Record each codebase-answered question in `codebase_answers` with the file path and line that answers it.

Only after exhausting the codebase do you ask the user a question, and you record it in `open_questions`.

## Walk Each Branch

For each branch of the design tree:

1. State the branch and the decision it requires.
2. Probe the codebase for the answer (codebase-first).
3. If unresolved, ask the user ONE question naming the branch and the decision needed.
4. Record the user's answer in `resolved_decisions_file`, including the dependency chain.
5. Add the branch to `branches_walked`.
6. Move to the next branch; dependencies resolved earlier may unblock later branches.

## Orchestrator State Updates

After each question-answer pair:

- `round_count`: increment by 1.
- `branches_walked`: append the branch just walked.
- `decisions_resolved`: append `{branch, decision, answer, depends_on: [...]}`.
- `open_questions`: remove any question just answered; append new ones that surfaced.

## Report

After each round, report:

> Round <round_count>: walked branch "<branch>". Decisions resolved: <N>. Open questions: <M>.

Proceed to Step 2 (Dependency Resolution) once all branches are walked or blocked on open questions.
