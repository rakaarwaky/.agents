---
name: review-triage
description: "Use when triaging external review reports against code."
when-to-use: "Use when handed a review/audit/UX/security report (markdown, PDF, or text) and asked to validate its findings against the repo, then fix whatever is actually wrong. Best for reports that allege bugs, gaps, or contradictions across multiple files."
argument-hint: "<path-to-report>"

---

# Review Triage

Verify an external review report against the actual code before changing anything. A review report is a hypothesis, not ground truth — every claim must be re-checked against current source, tests, and the FRD. Fix only claims that are valid and still present; ignore stale or false-positive claims.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **Read code first, report second.** Open every file the report cites. Grep for the exact symbols, function names, and line numbers it mentions. Do not act on a claim until you have read the current file content. | Each cited file read and grep-verified before any fix. |
| R2 | **Classify each claim.** Mark every issue as one of: valid-still-present (fix), valid-but-stale (no code change, note only), false-positive (claim contradicted by code), or not-a-requirement (enhancement, not a contract violation). Fix only valid-still-present claims. | Every claim has a classification label in the triage summary. |
| R3 | **Stale compiles are false positives.** A report generated against an older compile or an incomplete upload (artifacts missing, files removed since report date) is false-positive unless the claim re-appears in current code. | Claim re-verified against HEAD code before any fix. |
| R4 | **Code wins over FRD.** If code and FRD contradict, the code defines real behavior; update the FRD (and BACKLOG) to match verified code, never the reverse. | FRD edited to match code, not code to match FRD. |
| R5 | **Verify before commit.** Run `PYTHONPATH=modules .venv/bin/python -m pytest modules/ -q -m "not dogfood"` and `lint-arwaky-cli scan modules`. Both must pass clean before committing. | Exit 0 on tests and lint; working tree clean after push. |
| R6 | **Update FRD/BACKLOG for missing edge cases.** When a real gap is found, add the missing edge-case bullets, test rows, and technical-spec rows to FRD.md; mirror the change in BACKLOG.md. | FRD and BACKLOG both reflect the fix. |
| R7 | **Fix only the real thing.** Do not fix false positives, stale claims, or enhancements masquerading as bugs. Document why each skipped claim was rejected. | Triage summary lists rejected claims with reasons. |
| R8 | **Commit and push.** After all fixes and verification, commit with a message naming the real gaps closed and push to origin/main. | `git push` succeeds; working tree clean. |
| R9 | **Execute behavioral claims, don't just read them.** For any claim of the form "X does/doesn't Y at runtime" (silent data loss, wrong return on bad input, exception that escapes, empty-state rendering), run the cited code path with a crafted input in a scratch dir and assert the observed output — static reading alone mislabels runtime behavior. A `parse→render` round-trip, an `n=0` call, or a malformed-file read settles the claim in one probe. | Each behavioral claim backed by a live probe result in the triage summary, not only a code citation. |
| R10 | **Confirm scope: validate-only vs fix.** "Is this review valid?" asks for a triage verdict only — deliver a per-claim table (confirmed-valid classification + evidence + severity grouping), no code edits, no commit. Fix + commit only when the user asks to remediate. When unsure which mode, state the verdict then offer to fix. | No code changed or committed on a validate-only request. |

## References

- [`references/classification-table.md`](references/classification-table.md) — how to classify each claim (valid-still-present / valid-but-stale / false-positive / not-a-requirement)
- [`references/verification-checklist.md`](references/verification-checklist.md) — per-file verification steps, live-probe recipes for behavioral claims, and commands
- [`references/probe-recipes.md`](references/probe-recipes.md) — proven probe patterns for common behavioral claim types (parse→render data loss, silent empty return, exception escape, non-git fallback, error message format, Python version compatibility)