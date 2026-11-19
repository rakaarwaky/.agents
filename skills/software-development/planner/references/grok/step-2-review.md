# Step 2: Review

Spawn the reviewer subagent to produce structured findings.

## Spawn

`spawn_subagent` parameters:

- `description`: `"[reviewer] Review plan doc"`
- Prompt body: `reviewer_persona_instructions` prepended, then:

```text
Review: <plan_doc_file>
Summary: <summary_file>
Output: <review_file>

Read both files. Do not modify them. Write structured notes to Output.
Each issue needs: Severity, Section, Description, Suggestion, Status: open.

Evaluate:
- PR Plan: realistic, ordered, independently mergeable.
- Key Decisions: well-reasoned.
- Detail: enough for implementation.
```

## Known-Issues Checklist

If `past_issues_briefing` is non-empty (from Step 0), append this block to the reviewer prompt after the base prompt; when empty, omit it:

```text
Known recurring issues for this workspace (from previous runs):
1. <pattern 1> (seen N times)
2. <pattern 2> (seen N times)

For each pattern above, verify the plan addresses it, or explicitly declares it out of scope (an Open Question, or a Key Decisions entry with a reason). For any pattern the plan neither addresses nor declares out of scope, add an open issue (severity: suggestion, or bug when the pattern is security-relevant) whose Suggestion points at the plan section that should cover it.
```

## After Completion

Continue to Step 3.

## Host-claim pre-verification (orchestrator duty, not subagent duty)

Before dispatching the reviewer, the orchestrator should run a quick live probe of any external-system claim in the doc that is load-bearing (e.g. "the Flatpak binary is launchable from a host process", "this file path exists on this machine", "this CLI flag is supported by the installed browser version`). This is not the reviewer's job — the reviewer verifies internal code claims; the orchestrator verifies host-environment claims by actually running the command:

```bash
# example: probe a Flatpak-managed binary path before it lands in the plan
ls -la /var/lib/flatpak/app/<app-id>/x86_64/stable/active/files/<binary> 2>/dev/null
# or: launch-test a binary via the target framework's minimal call
timeout 30 python3 -c "<minimal framework call with the candidate binary>" 2>&1 | head -5
```

Record the result (success/failure + actual path or flag) and pass it as a **ground-truth fact** in the writer/reviewer prompts, labelled "verified on this host — treat as fact, do not re-verify". This prevents the writer from encoding an unverified host assumption into the plan doc and the reviewer from flagging it as "open question" when it is already resolved.

Do NOT probe claims that are clearly documentation-level (e.g. "the library version supports X"); only probe claims where the answer changes which code path the PR plan will take.