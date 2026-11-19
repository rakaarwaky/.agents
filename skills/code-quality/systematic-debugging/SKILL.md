---
name: systematic-debugging
description: "Systematic root-cause debugging in 7 step files (0–6) covering TypeScript/Node, Python, and Rust: read errors and build a red-capable feedback loop, trace data flow, analyze patterns, form ranked falsifiable hypotheses, implement one fix via TDD (RED-GREEN-REFACTOR), verify, and guard against rationalizations. Includes language-variant debugger/verify steps (3a/3b/3c, 5a/5b/5c). Observed phrasing: /systematic-debugging, fix this bug, test is failing, performance regression."
when-to-use: "Use for any technical issue — test failures, production bugs, build or performance problems, integration issues. Also for Python (pdb, debugpy), TypeScript/Node (node inspect, CDP, heap/CPU profiles), and Rust (dbg!, RUST_BACKTRACE, rust-gdb/lldb) debugging. Invoke directly as /systematic-debugging. Do not skip when the issue seems simple, you are in a hurry, or someone wants it fixed NOW — rushing guarantees rework."
argument-hint: "<issue-or-error> [--phase <1|2|3|4>] [--lang <python|typescript|rust|node>] [--repro <command>]"
metadata:
  tags:
    - debugging
    - troubleshooting
    - problem-solving
    - root-cause
    - investigation
    - tdd
    - python
    - typescript
    - node
    - rust
    - pdb
    - debugpy
    - cdp
  related_skills:
    - pr-babysit
    - issue-worker
    - deep-clean
---

# Systematic Debugging

For any technical issue — test failures, production bugs, build or performance problems — find the root cause before touching a fix. This file is the lane identification step only; the working method lives in `references/hermes/` and `references/grok/`.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **Lane by physical signal.** Lane is determined from launcher env var (`HERMES_AGENT` -> Hermes lane; `GROK_AGENT` -> Grok lane; unset -> stop). Model cannot self-identify. | Signal evaluated via `[[ -n "${HERMES_AGENT:-}" ]]` / `[[ -n "${GROK_AGENT:-}" ]]`; UNSET halts immediately. |
| R2 | **Winning lane isolation.** Read only the winning lane's references (`references/hermes/` or `references/grok/`). Do not cross-read the other lane. | Zero reads of the non-winning lane's files. |
| R3 | **Iron law of root-cause.** No fix without root-cause investigation first (Steps 1–3). Proposing solutions before tracing data flow is strictly forbidden. | Step 1 investigation checklist satisfied before Step 4. |
| R4 | **Iron law of TDD.** No production code without a failing regression test first. Watch the test fail (RED), make it pass with the minimal fix (GREEN), then refactor (REFACTOR). | Regression test observed RED before GREEN change is made. |
| R5 | **Rule of three.** Stop after 3 failed fix attempts. A 4th attempt is forbidden without questioning the architecture and discussing with the user. | `fix_attempts` incremented; architecture review triggered when `fix_attempts >= 3`. |
| R6 | **Diff discipline.** The fix commit must contain only the regression test and the minimal fix. Drive-by refactoring or unrelated changes are forbidden. | `git show --stat` lists only test and minimal fix files. |
| R7 | **Clean tree verification.** Verification runs (regression test and full test suite) must execute against a clean committed worktree, never a dirty tree. | `git status --short` is clean before verification commands run. |
| R8 | **Completion.** The run is done when: regression test is RED->GREEN, full suite passes, output is pristine with zero stray debug statements (`breakpoint()`, `dbg!()`, `console.log`), and final report is emitted. | Regression test passes; full suite green; cleanup grep returns zero hits. |

## Routing

| Lane | Step | Reference | Purpose |
|------|------|-----------|---------|
| Hermes | 0 | [`references/hermes/step-0-plan-and-spawn.md`](references/hermes/step-0-plan-and-spawn.md) | Detect lang; plan the brief (symptom, repro, phase, constraints, acceptance criteria); create the Orca worktree with `--agent grok`; drop `/systematic-debugging <issue-or-error>` |
| Hermes | 1 | [`references/hermes/step-1-wait-grok.md`](references/hermes/step-1-wait-grok.md) | Wait for Grok to finish the pipeline; read its debug summary and commit |
| Hermes | 2 | [`references/hermes/step-2-verify-and-ship.md`](references/hermes/step-2-verify-and-ship.md) | Verify the iron law (regression test present), re-run the gate on the clean tree; commit/push/PR as appropriate |
| Hermes | 3 | [`references/hermes/step-3-final-report.md`](references/hermes/step-3-final-report.md) | Final report to the user (root cause, fix, verification, open decisions, commit/PR, worktree teardown) |
| Grok | 0. Intake | [`references/grok/step-0-intake.md`](references/grok/step-0-intake.md) | Symptom statement, target lang, repro command, run state; iron-law gate; invocation. |
| Grok | 1. Investigate | [`references/grok/step-1-investigate.md`](references/grok/step-1-investigate.md) | Read errors, build a tight red-capable loop, check recent changes, gather multi-component evidence, trace data flow. |
| Grok | 2. Pattern | [`references/grok/step-2-pattern.md`](references/grok/step-2-pattern.md) | Minimize the repro, find working examples, compare against references, identify differences, understand dependencies. |
| Grok | 3. Hypothesis | [`references/grok/step-3-hypothesis.md`](references/grok/step-3-hypothesis.md) | Form 3–5 ranked falsifiable hypotheses; test minimally, one variable at a time; pick the language debugger variant. |
| Grok | 3a/3b/3c. Language debugger | [`step-3a-python-debugger.md`](references/grok/step-3a-python-debugger.md), [`step-3b-node-debugger.md`](references/grok/step-3b-node-debugger.md), [`step-3c-rust-debugger.md`](references/grok/step-3c-rust-debugger.md) | Python (pdb + debugpy), Node/TS (node inspect + CDP, profiles), Rust (dbg!, RUST_BACKTRACE, rust-gdb/lldb). |
| Grok | 4. Implement | [`references/grok/step-4-implement.md`](references/grok/step-4-implement.md) | TDD cycle: RED failing test, GREEN single fix, per-language verify, REFACTOR; rule of three; question architecture at 3+ failures. |
| Grok | 5. Verify & finish | [`references/grok/step-5-verify.md`](references/grok/step-5-verify.md) | Verification checklist, language cleanup pass (delegates to 5a/5b/5c), guardrails final pass, reporting format. |
| Grok | 5a/5b/5c. Language verify | [`step-5a-python-verify.md`](references/grok/step-5a-python-verify.md), [`step-5b-node-verify.md`](references/grok/step-5b-node-verify.md), [`step-5c-rust-verify.md`](references/grok/step-5c-rust-verify.md) | Per-language verification + cleanup grep. |
| Grok | 6. Guardrails | [`references/grok/step-6-guardrails.md`](references/grok/step-6-guardrails.md) | Red-flags list, common-rationalizations table, TDD rationale, TDD cycle detail; cross-cutting rules applied before reporting done. |
