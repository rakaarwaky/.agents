# Claim Classification Table

Use this table to label every claim in an external review report before fixing anything.

| Label | Meaning | Action |
|-------|---------|--------|
| **valid-still-present** | The code does what the report says (or fails to do what it should), and the issue is present in current HEAD. | Fix the code. |
| **valid-but-stale** | The issue was real at report time but the code has since changed; the current code no longer exhibits the problem. | No code change. Note in triage summary. |
| **false-positive** | The report's claim is contradicted by the actual code (wrong function, wrong line, missing normalization, etc.). | No code change. Document why the claim is wrong. |
| **not-a-requirement** | The report flags something that is an enhancement or design preference, not a contract violation in the FRD or code. | No code change. Note as enhancement. |

## Decision procedure

1. Read the exact code the report cites (function, line, file).
2. If the code does not match the report's description → **false-positive**.
3. If the code matches but the issue is no longer present (e.g. a fix landed after the report was generated) → **valid-but-stale**.
4. If the issue is present in current code AND the FRD/code contract requires the behavior → **valid-still-present** → fix.
5. If the issue is present but no FRD or contract requires the behavior → **not-a-requirement** → enhancement.

## Common false-positive patterns

- **Stale compile:** report references files, functions, or line numbers that no longer exist at HEAD.
- **Incomplete upload:** report says "file not provided" or "code not reviewed" but the file exists in the repo.
- **Misread normalization:** report claims dedup is case-sensitive when the code calls `.lower()` on both sides.
- **Wrong file mode claim:** report says `mkstemp` creates `0o600` and never changes it, but the code explicitly `os.chmod`s before `os.replace`.
- **Wrong line reference:** report cites a function that was renamed, moved, or split.
