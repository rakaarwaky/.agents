---
name: capability-lifecycle
description: "Remove, replace, or add an AES capability across all layers."
version: 1
author: Hermes
license: ""
metadata:
  hermes:
    tags: []
    related_skills: []
when-to-use: "Add, remove, or replace an AES capability across all layers: contract, taxonomy, utility, capabilities, agent, surface, root, plus tests, FRD/BACKLOG/README/PRD docs, and skill step files."
---

# capability-lifecycle

## When to Use

Manage the full lifecycle of an AES capability. Use this skill when adding, removing, or replacing a capability — for example, replacing `memory snapshot` with `memory top` — across all layers: contract, taxonomy, utility, capabilities, agent, surface, root, plus tests, FRD/BACKLOG/README/PRD docs, and skill step files.

Manage the full lifecycle of an AES capability. A capability change is never isolated to one file: every layer that references it must be updated in the same change, or tests and lint will fail.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **Touch all layers.** Removing a capability requires deleting its capability file, removing it from the protocol contract, its VO from taxonomy, dead helpers from utility, the agent orchestrator, root container, and CLI surface. Zero references may remain. | `grep -rn "<cap-name>" modules/` returns empty |
| R2 | **Update tests at every level.** Unit fakes, contract isinstance checks, integration constructor args, acceptance capability classes, and e2e lifecycle steps must all match the new capability shape. Stale tests asserting removed behavior must be rewritten or renamed. | Full suite passes |
| R3 | **Keep BACKLOG and FRD IDs aligned.** When an FR ID is renamed or removed, its matching BACKLOG entry must be renamed or removed in the same change. An FR ID with no BACKLOG entry fires AES607 (`id_no_entry`); a BACKLOG entry citing an undeclared ID fires AES607 (`dt_backlog_id_not_dt`). | Lint reports 0 violations |
| R4 | **No free functions in capability files (AES403).** Helpers in capabilities files must be static methods on the capability class in Block 3, not free functions. | Lint reports 0 violations |
| R5 | **Contract signatures use VOs, not primitives (AES402).** Protocol signatures at layer boundaries use taxonomy VOs (`PatternCount`, `PatternCategory`), never Python primitives (`int`, `str`). Fake implementations in unit tests must construct VOs at the call site. | Lint reports 0 violations |
| R6 | **Update skill step files.** Skill step docs and SKILL.md rules that reference the removed CLI subcommand must point at the replacement. | `grep` returns zero matches for removed CLI command across skill files |
| R7 | **Verify after every phase.** Run tests and lint after each phase of removal, not just at the end. Partial removal leaves the tree in a broken state. | Tests green and lint clean before commit |

## Procedure

1. **Audit references.** `grep -rn "<capability-name>" modules/` to find every referencing file.
2. **Remove CLI surface.** Delete the subcommand parser and handler block from the surface file.
3. **Remove from orchestrator.** Remove from the agent's constructor, `execute()`, `create()`, and `__repr__`.
4. **Remove from root container.** Remove from the container constructor and factory.
5. **Delete capability file.** Remove the capabilities module file and its unit test file.
6. **Remove from contract.** Delete the protocol ABC and its `__all__` / symbol-map entries.
7. **Remove from taxonomy.** Delete the VO dataclass.
8. **Remove dead utility helpers.** Delete helper functions that only served the removed capability.
9. **Update all test levels.** Fix fakes, constructors, dispatch assertions, lifecycle tests.
10. **Update docs.** FRD, BACKLOG, README, PRD, skill SKILL.md rules, skill step files.
11. **Verify.** Tests pass, lint reports 0 violations, `grep` for the removed name returns empty.

## Pitfalls

- **Deleting a capability field from a VO breaks every consumer in the same file.** When removing a field from a result dataclass, grep for `.<field>` across the codebase first — consumers in capabilities, surfaces, and tests all reference the same field name.
- **Duplicate FRD/BACKLOG entries survive a rename.** When replacing an FR entry, both the old and new H3 headings can end up in the file. Verify with `grep -n "### FR-"` that each ID appears exactly once.
- **Import blocks break silently when removing one name from a multi-line import.** Removing a name from a parenthesised `from x import (...)` block can leave a dangling `(` or orphaned continuation lines. Re-read the full block after the edit.
- **Tests that assert removed fields still compile but fail at runtime.** A dataclass field removal does not cause a compile error in test files that construct the dataclass with the removed field — the `__init__` silently ignores it until an attribute access fires `AttributeError`. Grep for `.<removed_field>` in tests, not just the constructor call.
- **Skill step files reference the CLI command in prose.** Removing a CLI subcommand is not enough — skill step files that say `sdc memory <path|read|snapshot|update>` must be updated to the new command list, or agents will call a nonexistent subcommand at runtime.

## References

- [Capability removal checklist](references/capability-removal-checklist.md)
