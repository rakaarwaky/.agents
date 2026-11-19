# Capability Removal Checklist

Detailed step-by-step checklist for removing an AES capability across all layers.

## Pre-removal audit

- `grep -rn "<CapName>" modules/` lists all referencing files
- Note the capability's protocol name, VO name, CLI subcommand name
- Note which docs (FRD, BACKLOG, README, PRD) reference the capability
- Note which skill step files call the CLI subcommand

## Code removal (in order)

- Remove CLI subcommand parser and handler from the surface file
- Remove capability from the agent orchestrator (constructor, `execute()`, `create()`, `__repr__`)
- Remove capability from the root container (constructor and factory)
- Delete the capabilities module file
- Delete the capability's unit test file
- Remove protocol ABC from the contract file (`__all__`, symbol map, class definition)
- Remove VO from taxonomy
- Remove dead helper functions from utility
- Remove dead imports from all touched files

## Test updates (all levels)

- Unit tests: update fake class signatures to match new protocols
- Contract tests: remove isinstance checks for removed protocol
- Integration tests: remove removed capability from constructor args
- Acceptance tests: remove removed capability class references
- E2E tests: replace removed lifecycle step with replacement
- Rename stale test assertions to match new spec

## Doc updates

- FRD: rewrite section for removed capability to replacement (or delete)
- BACKLOG: rename/remove entry for changed FR ID
- README: update subcommand list and descriptions
- PRD: update in-scope command list
- Skill SKILL.md rules: update command references
- Skill step files: update CLI command calls

## Verify

- `PYTHONPATH=modules .venv/bin/python -m pytest modules/ -q -m "not dogfood"` passes
- `lint-arwaky-cli scan modules` reports 0 violations
- `grep -rn "<removed-name>" modules/` returns empty
- `grep -rn "sdc memory <removed-subcommand>"` across skill files returns empty
