# Step 12: Quality: Bypass Annotation

## What the rule checks

AES304 (rule code `AES304`, checker `capabilities_check_bypass_checker` in the `quality-rules` crate) detects bypass annotations, panics, and fallback calls that silently discard errors.

- `unwrap_or_default`, `.unwrap()`, `""`, panic annotations, `noqa`, `type: ignore`, `#[allow]`, `@ts-ignore`, `eslint-disable`.

## Common violation causes

- A file silently discards errors with `unwrap_or_default`, `.unwrap()`, `""`, or panic annotations.
- Suppression comments (`# noqa`, `type: ignore`, `#[allow]`) masking real errors instead of fixing the root cause. Any `noqa` comment — even one added for a legitimate reason like silencing BLE001 on a broad `except Exception` — is flagged as a bypass.
- A catch-all `except Exception` in a surface/CLI layer that swallows all errors and prints a traceback, hiding the real error type.

## How to fix (concrete steps)

1. Identify the violated rule code (AES304) from the scan report.
2. Replace silent discards with proper error propagation.
3. Wrap errors into taxonomy VOs or return `Result`.
4. If the violation is a **`noqa` bypass comment**: remove the `noqa` comment and fix the underlying issue it was suppressing. For `BLE001` (broad `except Exception`): replace the catch-all with specific exception types (`ValueError`, `KeyError`, `TypeError`, etc.) that the code actually expects, and handle each with a proper error message. This both clears AES304 and satisfies the linter's BLE001 rule.
5. If the violation is a **broad `except Exception` with traceback**: replace with specific exception types (e.g. `ValueError`, `KeyError`, `TypeError`) and a concise error message to stderr, not a full traceback dump. Do NOT add a `# noqa: BLE001` comment to suppress the linter — AES304 treats any `noqa` as a bypass and will still flag it. Instead, narrow the exception tuple to the types the code actually expects.
6. Fix the root cause and delete the suppression comment rather than auto-fixing over it.
7. Re-run `lint-arwaky-cli scan .` or `lint-arwaky-cli fix . --filter AES304` and confirm AES304 clears.

## Verify

```bash
lint-arwaky-cli scan . --filter AES304
# Confirm no AES304 finding remains.
```
