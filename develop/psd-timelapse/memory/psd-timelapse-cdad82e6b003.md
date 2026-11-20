# Implementation Review Patterns

> This file is maintained by the /implement skill.
> It records common issues found during implementation reviews to help avoid them in future runs.
> Shared across all working directories that resolve to the same workspace id.

## Common Issues

### Testing
- Drag-and-drop handlers need counter-based flicker guard (relatedTarget is null for DragEvent) (seen 1 time)
- File input value reset tests need to verify the actual DOM element value (seen 1 time)
- Missing tests for drop handlers with empty or missing dataTransfer.files (seen 1 time)
- Missing tests for empty-state visual demotion of primary action buttons (seen 1 time)
- Missing tests for file-input change with empty selection (cancelled dialog) (seen 1 time)
- Missing tests for keyboard accessibility preventDefault verification (seen 1 time)
- Missing tests for uppercase file extensions in accept checks (seen 1 time)
- Test file name does not match the capability under test (seen 1 time)

### Code Quality
- CSS hover specificity conflicts resolved by source order, not compound selectors (seen 1 time)
- Dead code in components after responsibility moves to another component (seen 1 time)
- Hardcoded pixel values instead of CSS tokens or classes for icon sizing (seen 1 time)
- Inline styles override CSS class declarations for visual state (seen 1 time)
- Use full shorthand border instead of partial border-property overrides (seen 1 time)

### Planning
- Agent dispatch shape not stated, risking AES405 free-function violation (seen 1 time)
- Async signature vs synchronous execution tension not resolved for blocking I/O (seen 1 time)
- Blocking dependency decision not enforced as a PR gate (seen 1 time)
- Field-name mapping obligation between surface rows and domain VOs not documented for deferred wiring (seen 1 time)
- Missing optional document rationale not stated for the layer (seen 1 time)
- Plan assumes member-level config files exist without checking the workspace's shared config pattern (seen 1 time)
- Plan lacks an objective test-count or coverage completion criterion (seen 1 time)
- PR Plan dependency edges inconsistent between diagram and text (seen 1 time)
- Shared folder mirror created without DATA.md/BACKLOG.md DT-ID registration (seen 1 time)
- Validation rule missing an edge case that the server-side counterpart enforces (seen 1 time)

### Security
- Security table omits a client-side injection/prototype-pollution vector (seen 1 time)

## Recent Runs

### 2026-11-20 — "plan: psd adapter package packages/psd"
- **Rounds**: 2
- **Issues**: 12 total (1 bug, 2 suggestions, 9 nits)
- **Key patterns**: Plan assumes member-level config files exist without checking the workspace's shared config pattern, Shared folder mirror created without DATA.md/BACKLOG.md DT-ID registration, Blocking dependency decision not enforced as a PR gate

### 2026-11-19 — "fix studio visual hierarchy dropzone focal point"
- **Rounds**: 3
- **Issues**: 14 total (2 bugs, 6 suggestions, 6 nits)
- **Key patterns**: Inline styles override CSS class declarations for visual state, CSS hover specificity conflicts resolved by source order, not compound selectors, Missing tests for empty-state visual demotion of primary action buttons
- **Specializations used**: general, tests, simplicity

### 2026-11-19 — "Execute plan: Move Studio PSD Upload to Canvas Top Bar with Empty-Canvas Drag-and-Drop"
- **Rounds**: 2
- **Issues**: 14 total (2 bugs, 8 suggestions, 4 nits)
- **Key patterns**: Missing tests for keyboard accessibility preventDefault, Drag-and-drop handlers need counter-based flicker guard, Dead code in components after responsibility moves
- **Specializations used**: general, tests, simplicity
