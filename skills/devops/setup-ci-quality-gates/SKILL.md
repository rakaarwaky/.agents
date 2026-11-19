---
name: setup-ci-quality-gates
description: "Set up CI quality gates and architecture checks on GitHub Actions, and reproduce those gates locally via a ci.sh mirror. Use when creating workflows, branch protection rulesets, auto-merge, AI review layers, or building scripts/ci.sh to mirror .github/workflows when GitHub Actions is quota-blocked."
when-to-use: "Use when replicating this repo's CI setup: ci.yml jobs, branch-protection ruleset, auto-merge workflow, AI review layers (cubic, Repowise), local scripts/ci.sh that mirrors the remote workflow, or running the same CI gates locally in a container when GitHub Actions is quota/billing-blocked."
argument-hint: "[<repo-root>]"
---

# CI Quality Gates System

Replicate comprehensive CI quality gates using GitHub Actions, branch-protection rulesets, self-lint architectural enforcement, AI review layers, and local containerized reproduction mirrors.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Enforce core quality gate jobs in CI workflows: format check, linter with zero warnings, build, tests, and architecture self-lint. | Verify CI workflow definition includes all standard gate jobs. |
| R2 | Require self-lint jobs to assert zero architectural violations and verify rule engine firing on known negative fixtures. | Inspect self-lint job step to confirm assertion of full rule codes. |
| R3 | Configure branch protection rulesets on default branch requiring strict up-to-date checks, blocking deletions and non-fast-forwards. | Check repository ruleset settings for required checks and branch protections. |
| R4 | Gate auto-merge squash workflows strictly on passing status checks with explicit PR metadata environment variables. | Verify auto-merge workflow triggers only upon all checks succeeding. |
| R5 | Mirror remote CI checks in a local `scripts/ci.sh` executable supporting both host and container execution modes. | Run `bash scripts/ci.sh` locally and confirm identical gate verification. |

## Routing

| Reference | Purpose |
|-----------|---------|
| [`references/branch-protection.md`](references/branch-protection.md) | GitHub Ruleset and required status checks |
| [`references/ci-workflow.md`](references/ci-workflow.md) | The five CI jobs (fmt, clippy, build, test, self-lint) |
| [`references/container-image.md`](references/container-image.md) | Container image design for local CI mirroring |
| [`references/self-lint.md`](references/self-lint.md) | Self-lint job script and AES rule assertion |
| [`references/auto-merge.yml.md`](references/auto-merge.yml.md) | Squash-merge auto-merge workflow |
| [`references/ai-review-layers.md`](references/ai-review-layers.md) | cubic and Repowise configuration |
| [`references/local-ci.md`](references/local-ci.md) | Local quality gates mirror via scripts/ci.sh |
| [`references/verify-runtimes.md`](references/verify-runtimes.md) | Runtime version verification |
