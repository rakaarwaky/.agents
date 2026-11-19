# Implementation Review Patterns

> This file is maintained by the /implement skill.
> It records common issues found during implementation reviews to help avoid them in future runs.
> Shared across all working directories that resolve to the same workspace id.

## Common Issues

### Testing
- Drag-and-drop handlers need counter-based flicker guard (relatedTarget is null for DragEvent) (seen 1 time)
- File input value reset tests need to verify the actual DOM element value (seen 1 time)
- Missing tests for keyboard accessibility preventDefault verification (seen 1 time)

### Code Quality
- Dead code in components after responsibility moves to another component (seen 1 time)

## Recent Runs

### 2026-11-19 — "Execute plan: Move Studio PSD Upload to Canvas Top Bar with Empty-Canvas Drag-and-Drop"
- **Rounds**: 2
- **Issues**: 14 total (2 bugs, 8 suggestions, 4 nits)
- **Key patterns**: Missing tests for keyboard accessibility preventDefault, Drag-and-drop handlers need counter-based flicker guard, Dead code in components after responsibility moves
- **Specializations used**: general, tests, simplicity
