## Plan Document Review: Move Studio PSD Upload Affordance to Canvas Top Bar with Empty-Canvas Drag-and-Drop

### Summary
Approved. All eight issues identified in prior reviews have been fully and accurately addressed across the plan document, with verified technical correctness against the codebase, consistent PR decomposition, and complete compliance with passive component boundaries (AES201/AES406). There are no remaining open issues.

### Strengths
- **Strict passive component adherence**: Preserves AES201 and AES406 boundaries by keeping `StudioCanvas` purely passive and orchestrating file picking and re-inspection through callbacks up to `StudioContainer`.
- **Zero smart container churn**: Appropriately threads `fileMeta` and derives `hasDocument` within `StudioLanding`, requiring zero modifications to `packages/root_web_smart_container.ts`.
- **Robust drag-and-drop UX**: Correctly prevents drag-leave event flickering using `e.currentTarget.contains` and CSS `pointer-events: none`, while providing explicit state-to-copy mapping across idle and drag-over interactions.
- **Preserved metadata observability**: Dynamically surfaces document name and dimensions in `.pt-studio-canvas-chip` while maintaining a clean fallback when no document metadata is present.
- **Clean and ordered PR plan**: Decomposes the work into two sequentially ordered, independently mergeable PRs with strict component boundaries, clean TypeScript compatibility, and complete test plans.
