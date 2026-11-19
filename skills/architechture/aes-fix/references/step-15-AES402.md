# Step 15: Role/Layer: Contract ABC-Only

## What the rule checks

AES402 (rule code `AES402`, checker `capabilities_contract_*_role_auditor` in the `role-rules` crate) verifies contract files define ABCs/protocols only, no implementation, and that contract signatures use taxonomy VOs — not Python primitives — at layer boundaries.

## Common violation causes

- A contract file contains method bodies / implementation instead of only ABC signatures.
- A contract signature uses Python primitive types (`int`, `str`, `bool`, `list`, `dict`) instead of taxonomy Value Objects — primitives cross a layer boundary without the type safety VOs provide.

## How to fix (concrete steps)

1. Identify the violated rule code (AES402) from the scan report.
2. If the violation is **method bodies in contract**: move method bodies out of the contract file into a capability that implements the protocol. Keep contract files to ABC/protocol signatures only.
3. If the violation is **primitive types in signature**: replace each primitive with the matching VO from the taxonomy layer (`PatternCount` instead of `int`, `PatternCategory` instead of `str`, etc.). Import the VOs from `shared.src.common.taxonomy_sdc_vo` (or the domain's taxonomy module). Update the capability implementation that calls the method to construct the VO at the call site (`PatternCount(request.n)`), not just the signature. Update the orchestrator/agent that dispatches to the method to wrap the primitive before passing it through. **Also update any fake/mock implementations in unit tests** — they declare their own method signatures and will fail type-checking or runtime assertions if they still use primitives. Wrap the primitive in the test's fake (`PatternCount(5)` instead of `5`).
4. Re-run `lint-arwaky-cli scan .` and confirm AES402 no longer fires on that file.

## Verify

```bash
lint-arwaky-cli scan . --filter AES402
# Confirm no AES402 finding remains.
```
