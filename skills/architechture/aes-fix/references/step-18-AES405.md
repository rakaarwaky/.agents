# Step 18: Role/Layer: Agent Orchestration Only

## What the rule checks

AES405 (rule code `AES405`, checker `capabilities_agent_*_role_auditor` in the `role-rules` crate) verifies agent files orchestrate only, no I/O, no computation, no local domain data.

## Common violation causes

- An agent file does I/O, computation, or holds local domain data instead of delegating to capabilities/taxonomy/utility.
- An agent file contains a free function (e.g. `_slugify_title`, `_normalise`, `_parse`) that is a pure utility — it belongs in a `utility_<domain>_<name>.py` file under `shared/src/<domain>/`, or as a method on the agent's class if it only serves that agent.

## Sub-check: AGENT_ROLE_SUBSYSTEM_COUNT

A distinct AES405 sub-code — `AGENT_ROLE_SUBSYSTEM_COUNT` — fires when a feature's shared kernel declares **exactly one protocol** but the agent still injects that single seam (a single-subsystem feature). The auditor says the dispatch work "belongs in a capability rather than an agent." It is reported at **LOW** severity, which is gate-tolerated.

**Collision with AES702 (keep the agent, accept the LOW).** AES702 (`feature_missing_agent`, **MED/blocking**) *requires* a feature folder to carry an `agent_*_orchestrator` file. A single-protocol feature cannot satisfy both: removing the agent clears AES405 but trips AES702. Resolution: **keep the agent file and accept the AES405 AGENT_ROLE_SUBSYSTEM_COUNT LOW** — AES702 is higher-severity and blocking, AES405-SUBSYSTEM is LOW and tolerated. The agent simply routes to the one capability seam. Do NOT add a second artificial protocol seam just to silence AES405 — that is the exact anti-pattern the sub-check warns about.

## How to fix (concrete steps)

1. Identify the violated rule code (AES405) from the scan report.
2. Move I/O/computation/domain data out of the agent file into capabilities/taxonomy/utility.
3. If the violation is a **free function in an agent file**: move the function to a `utility_<domain>_<name>.py` file under `shared/src/<domain>/`, export it as a public `slugify_title` (no leading underscore), and import it in the agent. If the same function is duplicated in a capability file, delete the capability's local copy and import from the shared utility. Update all callers to use the shared import.
4. Keep agent files to orchestration only.
5. Re-run `lint-arwaky-cli scan .` and confirm AES405 no longer fires on that file — **unless** the finding is `AGENT_ROLE_SUBSYSTEM_COUNT` on a genuine single-protocol feature, in which case leave it: it is LOW/gate-tolerated and AES702 (MED) requires the agent file to exist.

## Verify

```bash
lint-arwaky-cli scan . --filter AES405
# Confirm no AES405 finding remains.
# EXCEPTION: a single-protocol feature's agent legitimately keeps one
# AGENT_ROLE_SUBSYSTEM_COUNT finding (LOW). It stays — AES702 needs the agent.
```
