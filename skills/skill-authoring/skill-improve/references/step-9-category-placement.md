# Improve — Step 9: Category-placement audit

**Goal:** you can audit and fix skill category placement — move misplaced skills, create a category when none fits, and leave the catalog rebuilt and lint clean.

Use this when skills may be in the wrong category.

1. Run:

```bash
sac lint
```

2. Read the catalog via the CLI (no need to open the file manually):

```bash
sac catalog --read
```

3. The catalog's `## Categories` table already carries each category's description, so it is enough to judge placement (step 4). Open `DESCRIPTION.md` directly only when you will **create or edit** a category's description (steps 6/7) or when `sac lint` flags `missing-category-description` / `empty-category-description` — the catalog row is a stale snapshot until `sac catalog --build` is rebuilt.
4. Identify skills whose name or description conflicts with their current category.
5. If duplicate or obsolete skills need pruning, route to the pack's pruning skill (`skill-design --prune`) — this skill only decides category placement. If that skill is not in the tree, list the duplicates in the report instead of deleting them (Rules: dangling refs rot fast).

6. If no category fits, create one:

```bash
sac create category CATEGORY_NAME --description "CATEGORY_DESCRIPTION" --apply
```

7. Move each misplaced skill:

```bash
sac move CATEGORY/SKILL TARGET_CATEGORY --apply
```

8. Rebuild the catalog:

```bash
sac catalog --build
```

9. Verify the moved skills appear under the correct category.

## Commands

| Command | Use |
| ------- | --- |
| `sac lint` | Detect placement issues (`empty-category`, `missing-category-description`, etc.). |
| `sac catalog --read` | Read the catalog's `## Categories` table without opening the file. |
| `sac create category CATEGORY_NAME --description "CATEGORY_DESCRIPTION" --apply` | Create a new category when no existing one fits. |
| `sac move CATEGORY/SKILL TARGET_CATEGORY --apply` | Move a misplaced skill to the correct category. |
| `sac catalog --build` | Rebuild the catalog after moves or category changes. |

### Pitfalls

- **Empty source category**: moving the last skill out of a category leaves it empty, and `sac lint` flags `empty-category`. Delete the empty `DESCRIPTION.md` and category directory, or retire the category row in `catalog.json`.
- **Dangling paths**: after a move, grep the pack for the old `category/skill-name` path and update any hardcoded references.

## Completion

- Every misplaced skill identified in steps 4–7 has been moved.
- Duplicates and obsolete skills were routed to the pruning skill, or listed in the report when it is absent.
- The catalog was rebuilt after moves.
- `sac lint` reports no placement issues.
