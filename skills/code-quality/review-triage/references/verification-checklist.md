# Verification Checklist

Per-file verification steps for common claim types. Run these before classifying any claim.

## Code-behavior claims ("X does not Y")

1. `search_files(pattern="def X", path="<file>")` — find the function.
2. Read the function body with `read_file`.
3. Check for the claimed behavior (normalization, validation, error handling).
4. If the behavior is present → **false-positive**.

## Missing-validation claims ("X is not validated")

1. Grep for the validation keyword in the file: `search_files(pattern="validate", path="<file>")`.
2. Check if the validation exists but in a different form (e.g. `_validate_workflow` method vs inline check).
3. If validation exists → **false-positive**.

## Contract-contradiction claims ("code and FRD disagree")

1. Read the FRD section cited: `read_file(path="<frd>", offset=<line>)`.
2. Read the code section cited.
3. If they contradict → **valid-still-present**; fix FRD to match code (R4).

## Missing-test claims ("no test for X")

1. Grep the test tree: `search_files(pattern="X", path="modules/<feature>/tests")`.
2. If a test exists → **false-positive**.

## Non-git / edge-case claims

1. Read the code path: `search_files(pattern="git", path="<file>")`.
2. Check the fallback chain (git → git-common-dir → cwd → error).
3. Compare with FRD edge-case bullets and test rows.
4. If code and FRD disagree → **valid-still-present**; fix FRD to match code (R4).

## Behavioral claims ("X does Y at runtime" / "X silently does Z")

Run the code, don't just read it. Static reading confirms the code path exists; only execution confirms the runtime behavior. One probe settles the claim.

1. Write a Python one-liner in a scratch dir that imports the cited function and calls it with a crafted input.
2. Assert the observed output matches (or contradicts) the claim.
3. Record the probe result in the triage summary.

### Probes proven useful

| Claim type | Probe pattern |
|---|---|
| Silent data loss on parse→render | Construct a memory-file string with hand-written prose inside a section, call `parse_memory_file` then `render_memory_file`, grep the output for the prose string. |
| Silent empty return on invalid input | Call `top_patterns(state, n=0)` or `top_patterns(state, n=-5)`, assert the result is empty with no exception. |
| Exception type that escapes | Feed a file with invalid UTF-8 (e.g. `b'\xff\xfe'`) to `read_content()`, assert `UnicodeDecodeError` (not `SdcError`) propagates. |
| Error-message format | Call the function that raises, catch the exception, print `str(e)`, assert the claimed format (tuple repr, missing cause, stacked prefix) is present. |
| Non-git cwd fallback | `chdir` to a non-git dir, call `memory_paths()`, catch `WorkspaceIdError`, compare with `get_workspace_id()` in the same dir — if the latter succeeds but the former fails, the fallback is unreachable. |

### Environment pitfalls

- `memory_paths()` succeeds inside any git repo (including `$HOME` if it's a git repo). To test the non-git path, `chdir` to `/tmp` or a `tempfile.mkdtemp()` and verify with `git rev-parse --show-toplevel` (rc 128) before running.
- The project `.venv` runs Python 3.14, not 3.9. `datetime.UTC` imports fine there. Confirm the Python floor by checking the import against `sys.version_info` and the PRD statement — not by running 3.9.

## Write-safety claims

1. Read `atomic_write` or equivalent: `search_files(pattern="atomic_write", path="<file>")`.
2. Check for `os.chmod`, `os.fsync`, `os.replace` calls.
3. If the claimed unsafe behavior is not present → **false-positive**.

## Verification commands

After all fixes, run:

```bash
PYTHONPATH=modules .venv/bin/python -m pytest modules/ -q -m "not dogfood"
lint-arwaky-cli scan modules
```

Both must exit 0 before committing.
