# Step 16: Agent Role: Free Function

## What the rule checks

AES403 (rule code `AES403`, checker `role-rules` crate) verifies that an agent file holds exactly one type and its methods — no free functions. Reported as `AGENT_ROLE_FREE_FUNCTION`. Sibling capability files enforce the same shape under `CapabilityBlockMarkers`, which requires a module to declare its class, then its contract methods, then private static helpers in order.

## Common violation causes

- A module-level helper function (e.g. `_slugify_title`, `_validate_workflow`) sits outside the class in an agent or capability file.
- A private helper was added at the top of the file next to the imports instead of inside the class body.

## How to fix (concrete steps)

1. Identify the violated rule code (AES403) and the named function from the scan report.
2. Decide the helper's real home by what it does, not by where it is easiest to leave it:
   - Pure stateless transformation with no domain state → move to `utility_<domain>_<name>.py` in the shared layer as a public function. Update every call site to import it. Delete now-unused module imports from the original file (leaving `import re` behind fires AES402).
   - Helper that belongs to the class's own behaviour → make it a `@staticmethod` on the class in Block 3 (Module Helpers), and call it as `self._helper(...)` / `cls._helper(...)`.
3. If the helper had thin wrappers elsewhere (e.g. a private `_slugify_title` in a capabilities file that other code calls), repoint the wrapper at the shared utility rather than keeping a second implementation.
4. Check sibling call paths for the same defect — the rule fires on every agent/capability file with a free function, so a scan that shows one usually has more.
5. Re-run `lint-arwaky-cli scan .` and confirm AES403 no longer fires on that file.

## Pitfalls

- Extracting a helper to a shared utility and then importing a VO that does not exist (`PlanSlug`) trades an AES403 for an ImportError — check the taxonomy module for the actual VO names before writing the import.
- Deleting a free function without deleting its now-unused imports leaves an AES402 (unused import) in its place; remove both in the same edit.

## Verify

```bash
lint-arwaky-cli scan . --filter AES403
# Confirm no AES403 finding remains.
```
