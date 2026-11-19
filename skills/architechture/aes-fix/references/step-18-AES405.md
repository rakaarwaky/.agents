# Step 18: Role/Layer: Agent Orchestration Only

## What the rule checks

AES405 (rule code `AES405`, checker `capabilities_agent_*_role_auditor` in the `role-rules` crate) verifies agent files orchestrate only, no I/O, no computation, no local domain data.

## Common violation causes

- An agent file does I/O, computation, or holds local domain data instead of delegating to capabilities/taxonomy/utility.
- An agent file contains a free function (e.g. `_slugify_title`, `_normalise`, `_parse`) that is a pure utility — it belongs in a `utility_<domain>_<name>.py` file under `shared/src/<domain>/`, or as a method on the agent's class if it only serves that agent.

## How to fix (concrete steps)

1. Identify the violated rule code (AES405) from the scan report.
2. Move I/O/computation/domain data out of the agent file into capabilities/taxonomy/utility.
3. If the violation is a **free function in an agent file**: move the function to a `utility_<domain>_<name>.py` file under `shared/src/<domain>/`, export it as a public `slugify_title` (no leading underscore), and import it in the agent. If the same function is duplicated in a capability file, delete the capability's local copy and import from the shared utility. Update all callers to use the shared import.
4. Keep agent files to orchestration only.
5. Re-run `lint-arwaky-cli scan .` and confirm AES405 no longer fires on that file.

## Verify

```bash
lint-arwaky-cli scan . --filter AES405
# Confirm no AES405 finding remains.
```
