# Step 1: Write the plan Document

Spawn the writer subagent to draft the plan document.

## Spawn

`spawn_subagent` parameters:

- `description`: `"[writer] Write plan doc: <short summary>"`
- Prompt body: `writer_persona_instructions` prepended, then:

```text
Write a plan document for: <full user description and context from Step 0>.
Save the document to: <plan_doc_file>
Save a summary to: <summary_file>

Write ONLY to those two paths. Do NOT create files in the repo root or any other location. The repo is read-only for you — do not commit, branch, or edit source files.

The document must end with these three exact sections, in this specific order:

## Open Questions
(Decisions that genuinely need user input, or "None" if all resolved.)

## Key Decisions
(Summarize important architectural choices and rationale.)

## PR Plan
(Break the plan into concrete, ordered, independently mergeable PRs. Each PR must use this exact format:

### PR N: <Title>
- **Files/components affected:** <comma-separated file paths>
- **Dependencies:** None, or "PR <n>, PR <m>"
- **Description:** <one-line description>

Every PR must include exactly these three bullets in this order. Use sequential PR numbers starting at 1. This section must be at the absolute bottom of the document.)
```

## After Completion

Report: "plan document drafted. Starting review..." and continue to Step 2.