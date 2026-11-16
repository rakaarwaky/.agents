# Improve — Step 3: Pre-publish checklist, category placement, information distribution, reference pattern

**Goal:** run the pre-publish checklist, audit category placement, route every fact to its single home, and choose the reference pattern (A/B/C) before editing.

## Pre-publish checklist

- [ ] `sac read <name>` — read back the target `SKILL.md` to confirm frontmatter and body landed correctly.
- [ ] `sac lint` passes (catalog in `step-1-format.md`).
- [ ] Frontmatter satisfies the Rules bullets: mandatory keys, Frontmatter semantics, YAML hygiene, parser limits.
- [ ] Body within ~100–200 lines; overflow moved into `references/`; every reference, whatever its depth, is linked from `SKILL.md`. Quick probe: `ls references/ | while read f; do grep -q "$f" SKILL.md || echo "unlinked: $f"; done`
- [ ] Every sibling mention and cross-skill link names a skill that exists in the tree (Rules: dangling refs).
- [ ] Content detail (`step-2-detail.md`) satisfied.
- [ ] Quality gate cleared: the score block from `step-4-apply.md` is in the report, every score carries evidence, and the verdict is PASS — a FAIL is reported as a FAIL, never as done.
- [ ] `sac catalog --build` has been run so `skills/catalog.json` reflects the current frontmatter.
- [ ] Verify on disk: before committing, grep the restructured body shape (`^## Rules`, `^## Routing`) and list each new reference file. After committing, `git show --stat <sha>` must list exactly your task files.

## Category-placement audit

Use this when skills may be in the wrong category.

1. Run `sac lint`.
2. Read the catalog: `sac catalog --read`.
3. Open `DESCRIPTION.md` directly only when you will create or edit a category's description, or when `sac lint` flags `missing-category-description` / `empty-category-description`.
4. Identify skills whose name or description conflicts with their current category.
5. If duplicate or obsolete skills need pruning, route to the pack's pruning skill — this step only decides category placement. If that skill is not in the tree, list the duplicates in the report instead of deleting them.
6. If no category fits, create one: `sac create category CATEGORY_NAME --description "CATEGORY_DESCRIPTION" --apply`.
7. Move each misplaced skill: `sac move CATEGORY/SKILL TARGET_CATEGORY --apply`.
8. Rebuild the catalog: `sac catalog --build`.
9. Verify the moved skills appear under the correct category.

**Pitfalls:**
- Empty source category: moving the last skill out leaves an empty category flagged by `sac lint`. Delete the empty directory and `DESCRIPTION.md`, or retire the category row in `catalog.json`.
- Dangling paths: after a move, grep the pack for the old `category/skill-name` path and update hardcoded references.

## Information distribution test

Before editing any fact, route it: **how many steps read this fact during a single invocation?**

- More than one step (or all steps) → `SKILL.md` Rules. Cross-step policy, signal definitions, invariants, record formats.
- Exactly one step → that step's reference file. Commands, field shapes, per-action rules, stop conditions, worked examples.
- Neither — shared definition used by several pipeline skills → inline it into the consuming skill's step file; delete the standalone file in the same edit. A standalone `references/<name>.md` linked from several consumers is legitimate only when the fact genuinely has no per-skill step home.

Rules:
- A Rules bullet that fully defines a signal/action/invariant is the home; a step file repeating it is a second copy — point at the bullet, do not restate it.
- A step file may reference the Rules bullet by name; it does not restate the bullet's content.
- The shared-reference case is the only situation where a non-step `references/<name>.md` is legitimate in a Pattern B pipeline; name it in the `SKILL.md` Routing table and link it from the consuming step.

## Reference pattern decision

Run this **before** restructuring the `references/` folder. The pattern must match the skill's shape — never match by convention.

**Pattern A — one file per mode:** flat `references/<mode>.md` files, one per mode.
**Pattern B — numbered step files:** `references/step-<N>-<name>.md` in execution order for a single ordered pipeline. Every reference file carries a `step-<N>` prefix — no exceptions.
**Pattern C — hybrid:** per-mode subdirs of numbered steps (`references/<mode>/step-<N>-<name>.md`).

**Step 1: Does the skill have one ordered pipeline?** Will the agent always execute all steps in sequence, with state flowing from one step to the next? Answer from the Routing table. Yes → Pattern B. No → Step 2.
**Step 2: Does the skill have multiple independent modes?** Does the agent pick exactly one mode per invocation? Yes → check each mode file size: under ~100 lines and under 5 ordered steps → Pattern A; over → Pattern C for that mode only. No → return to Step 1 and apply Pattern B.

Placement rules: a fact used across multiple steps belongs in `SKILL.md` Rules; never mix patterns arbitrarily within one skill; renaming a reference file requires a grep sweep of the whole pack for the old name.

## Completion

- Pre-publish checklist fully checked; every gap listed with owning file.
- Category placement audited; misplaced skills moved; catalog rebuilt.
- Every fact routed to exactly one home; inlined shared definitions have the absorbed file deleted.
- Reference pattern chosen from the Routing table before inspecting the tree; filenames, titles, Routing rows, and cross-links all match; grep for old names returns zero hits.
