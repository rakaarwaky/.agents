---
name: deep-clean
description: "Deep structural cleanup and simplification: remove dead code, merge duplicate files, run a 4-lens sweep, and audit maintainability over a named path. Use for pre-merge or post-refactor work across Python, Rust, and TypeScript. Also triggered by /simplify."
when-to-use: "Use before merge, before release, or after refactoring a path, package, crate, or file. Remove dead code (ruff/vulture/knip/clippy/udeps), consolidate overlapping files into single cohesive modules, run a 4-reviewer sweep (reuse, quality, efficiency, altitude), and execute a strict maintainability audit. Answers 'is this codebase drifting toward spaghetti?' — run over a path, step by step, all aspects. Do not use for routine lint/type-check runs (those are CI gates) or for style nits without a structural angle. `--dry-run` (explicit) reports without executing; without it the run is headless and autonomous — no permission prompts."
argument-hint: "<path> [--dry-run]"
metadata:
  tags:
    - python
    - rust
    - typescript
    - cleanup
    - consolidation
    - bloat
    - stubs
    - thin-wrappers
    - dead-code
    - orphan
    - unused-files
    - merge
    - deduplication
    - code-review
    - refactor
    - delegation
    - subagent
    - parallel
    - simplify
    - spaghetti
    - maintainability
    - code-judo
    - giant-files
    - reuse
    - efficiency
    - altitude
  related_skills:
    - systematic-debugging
---

# deep-clean

Runs a 7-step pipeline over a named path: path audit capture → per-language dead-code cleanup → per-language file consolidation → 4-lens sweep → reviewer prompts + structural audit → apply per tier → verification gates → report. Language variants are picked per step (`1a`/`1b`/`1c`, `2a`/`2b`/`2c`) by the target language. This file is the lane identification step only; the working method lives in `references/hermes/` and `references/grok/`.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **Lane detection.** The lane is determined from a physical signal, not by self-identification. Each agent's launcher stamps a fixed attribution env var into every command it runs; the model cannot set these. `HERMES_AGENT` → Hermes lane (`references/hermes/`). `GROK_AGENT` → Grok lane (`references/grok/`). Neither → stop and report. | Exactly one lane's references read per invocation. |
| R2 | **Marker provenance.** Hermes re-exports `AI_AGENT=hermes-agent` and `HERMES_AGENT=true` on every command. Grok Build runs with `GROK_AGENT=1`. | Env var present before lane decision. |
| R3 | **Read only the winning lane.** Do not read the other lane's references. | Zero cross-lane reference reads. |
| R4 | **Relocate, don't delete, shared templates.** When stripping an embedded feature, check whether any removed files are also read by other linters or tests (e.g. doc templates that feed AES601-AES610 doc-shape checks). Relocate them to a non-feature path and update every path reference in build scripts, tests, and dispatchers. | No linter/test breaks from deleted shared files. |
| R5 | **Feature-stripping cascades.** Removing an embedded feature breaks every caller of its modules, constants, traits, and CLI variants. Fix all callers — `cargo build` and `cargo clippy -D warnings` surface the rest. Do not declare done until the binary compiles and the full test suite passes. | `cargo build` and full test suite exit 0. |
| R6 | **Grok Build max-turns recovery.** Verify progress in the worktree directory (`git status --short`, `git log --oneline -3`, `git diff <base>..HEAD`), not the TUI stream. Send a focused follow-up brief listing only remaining files; drive rounds with a shrinking grep count of the feature's key symbols until it hits 0. Never re-send the full original brief. Full recipe in the `grok-build` skill ("Multi-round large refactor recipe"). | Grep count of target symbols reaches 0. |
| R7 | **Sweep the whole tree after relocating.** Doc-comment prose, generated-file headers, test helper path joins, and stale references all carry the old path. Grep the old path string across `*.rs`, `*.md`, and `*.sh` (excluding `target/`) after moving files and rewrite every hit. | `grep -r '<old-path>' --include='*.rs' --include='*.md' --include='*.sh'` returns zero hits. |
| R8 | **Rust verification gates.** `CARGO_INCREMENTAL=0 cargo fmt --all -- --check`, `CARGO_INCREMENTAL=0 cargo clippy --all-targets -- -D warnings`, `CARGO_INCREMENTAL=0 cargo build --bin lint-arwaky-cli`, `CARGO_INCREMENTAL=0 cargo nextest run --workspace --lib --tests -j 2`. Run all four before declaring a Rust deep-clean done. | All four commands exit 0. |

## Routing

**Hermes lane (Steps 0–3)**

| Step | Reference | Purpose |
|-----:|-----------|---------|
| 0 | [`references/hermes/step-0-plan-and-spawn.md`](references/hermes/step-0-plan-and-spawn.md) | Detect language from `<path>`; plan the brief (mode, acceptance criteria); create the Orca worktree with `--agent grok`; drop `/deep-clean <path>` |
| 1 | [`references/hermes/step-1-wait-grok.md`](references/hermes/step-1-wait-grok.md) | Wait for Grok to finish the pipeline; read its step 7 report and commit |
| 2 | [`references/hermes/step-2-verify-and-ship.md`](references/hermes/step-2-verify-and-ship.md) | Re-run the language's verification gates on the clean committed tree; surface bugs + RISKY items; push/PR if asked |
| 3 | [`references/hermes/step-3-final-report.md`](references/hermes/step-3-final-report.md) | Final report to the user (cleanup counts, bugs, RISKY items, commit/PR, worktree teardown) |

**Grok lane (Steps 0–7, run by Grok Build)**

| Step | Reference | Purpose |
|------|-----------|---------|
| 0 | [`references/grok/step-0-scope.md`](references/grok/step-0-scope.md) | Path validation, audit scope, headless vs `--dry-run` mode gate. |
| 1 | [`step-1a-dead-code-python.md`](references/grok/step-1a-dead-code-python.md), [`step-1b-dead-code-rust.md`](references/grok/step-1b-dead-code-rust.md), [`step-1c-dead-code-typescript.md`](references/grok/step-1c-dead-code-typescript.md) | Phase 1 per-language dead-code detection, workflow, exceptions. |
| 2 | [`step-2a-consolidate-python.md`](references/grok/step-2a-consolidate-python.md), [`step-2b-consolidate-rust.md`](references/grok/step-2b-consolidate-rust.md), [`step-2c-consolidate-typescript.md`](references/grok/step-2c-consolidate-typescript.md) | Phase 2 per-language consolidation workflow, verification, commit, checklists. |
| 3 | [`references/grok/step-3-lens-sweep.md`](references/grok/step-3-lens-sweep.md) | Execution model, the four lenses, evidence standard, finding format, sweep pitfalls. |
| 4 | [`references/grok/step-4-reviewer-prompts.md`](references/grok/step-4-reviewer-prompts.md), [`references/grok/step-4-audit-standards.md`](references/grok/step-4-audit-standards.md), [`references/grok/step-4-review-tone.md`](references/grok/step-4-review-tone.md) | Full prompt text for each reviewer lens; non-negotiable audit standards; tone and output prioritization. |
| 5 | [`references/grok/step-5-apply-per-tier.md`](references/grok/step-5-apply-per-tier.md) | Strict tier order, per-file test gates, dry-run presentation, house-style folding. |
| 6 | [`references/grok/step-6-verification-gates.md`](references/grok/step-6-verification-gates.md) | Gate order, per-language exact commands, verification checklist, common mistakes, bugs-found section rules. |
| 7 | [`references/grok/step-7-report-format.md`](references/grok/step-7-report-format.md) | Final report section shape and worked example. |
