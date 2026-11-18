# Improve — Step 4: Apply recipe and Pattern B variants

**Goal:** apply the 11-point edit recipe end to end, and restructure references into Pattern B `step-<N>[a|b|c]` variants when requested.

## 11-point apply recipe

Run in order against the resolved scope:

1. **Classify**: content fix, structure fix, or both. Do not start editing until classification is clear. A content fix that is actually a structure fix will leave duplicates.
2. **Enforce body format**: before applying any content or structure fix, verify the target `SKILL.md` follows `# Title` / `## Rules` / `## Routing`. If it does not, restructure it first — move any out-of-place detail into `references/*.md`, then continue with the actual edit.
3. **Handle empty categories**: if moving the last skill out of a category, archive the last skill instead of deleting it:

   ```bash
   sac archive <category>/<skill> --apply
   sac catalog --build
   ```

   Then delete the now-empty category directory and its `DESCRIPTION.md`, or retire the category row in `catalog.json`.
4. **Identify the owner**: for each fact being changed, name its one home — `SKILL.md` Rules for a fact read by more than one step, a step file for a fact read by exactly one step. If the owner is ambiguous, make the more conservative choice (the single owner that preserves existing content), note it in the report, and continue — the default run is autonomous and does not stop for confirmation.
5. **Pick the target pattern** (when the edit restructures `references/`, or when the current tree's pattern does not match the skill's shape): run the reference-pattern decision in `step-3-publish.md` and apply it before editing. The answer comes from the skill's **Routing table**, never from the layout of the `references/` files that exist today.
6. **Apply the edit** where the owner lives. If the owner is a reference file, edit the reference — never the body. If the owner is Rules, edit `SKILL.md`.
7. **Sweep for second copies**: after the edit, search the skill directory for any other place that states the same fact. Report each one; do not silently rewrite them.
8. **Self-audit against the target's own rules**: when the target `SKILL.md` carries its own `## Rules` table, apply each rule as an audit criterion against the target's text and its `references/` before committing the edit.
9. **Resolve cross-skill links you touched**: every sibling mention and cross-skill link you edited must name a skill that exists in the tree (Rules: dangling refs rot fast).

## Pattern A consolidation

When asked to merge step-numbered references (`step-0-detect.md`, `step-1-*.md`, `step-2-*.md`) into a single topical file (`auth.md`):

1. **Read all source files first.** Concatenation without reading produces duplicated sections and broken cross-links.
2. **Merge order = execution order.** The merged file's sections follow the step numbers: detection → method 1 → method 2 → shared helpers → troubleshooting. Renumber as `## 1.`, `## 2.`, etc.
3. **Decision trees become section markers.** A `step-0` decision tree ("if X → step-1, if Y → step-2") becomes a numbered list in the merged file pointing at section headings, not file links. Example: `→ **Method 2: gh CLI Authentication**` not `→ [step-1-gh-cli-auth.md](step-1-gh-cli-auth.md)`.
4. **Collapse the Routing table.** Replace three rows (`Auth detect`, `Auth gh-cli`, `Auth git-only`) with one row: `| Auth | [references/auth.md](references/auth.md) | <combined purpose> |`.
5. **Grep-sweep for old filenames.** `grep -r "step-[012]" SKILL.md references/` — zero hits before commit. Check Rules bullets, Routing rows, and reference-to-reference links.
6. **Delete the source files.** `rm` the step files only after the merged file is written and the grep sweep passes.

## Pattern B restructuring

When asked to restructure an existing skill's `references/` from flat/mode layout into numbered step files with per-language/per-runtime sub-variants:

1. **Read the exemplar first.** Open the exemplar skill's `references/` directory. Identify which files are plain step files and which are `step-<N><variant>` files. The exemplar's `SKILL.md` Routing table is the authority for how variants are read. Copy that reading model into the target skill's Routing table.
2. **Identify split points in any monolith.** Grep `## ` headings. Split points are phase/stage boundaries (`## Phase 1:`, `## Phase 2:`, `## Final Verification`, `## Common Mistakes`, `## Quick Reference`, `## Decision Flowchart`, `## Dry-Run Mode`, `## Tool Reference`). Shared preamble → first variant file; phase body → own step file; cross-phase tails → last variant file. Record split lines before editing; after split, each original monolith is gone, content fully redistributed.
3. **Rename flat files into step numbers.** Every other flat reference that is actually a pipeline step gets `step-<N>-<name>.md` in execution order. The number is the pipeline step, not file-list order — the exemplar's Routing table is the authority. Use `git mv` (history survives). **`mkdir -p` the destination subdirectory first** — `git mv` into a nonexistent subdir fails. Update each file's `# Title` to `# Step <N>: <verb>` matching the exemplar convention.
4. **Fix every internal cross-link.** After renames, grep whole target skill dir for each old filename. Every hit is incomplete. Fix: `SKILL.md` Routing table rows, `SKILL.md` Rules bullets naming reference files, reference-to-reference links. Final grep: no old filename remains.
5. **Sync mode semantics.** A restructure is often paired with safety-model instruction (e.g. "default headless autonomous; `--dry-run` report-only"). If given: edit `argument-hint` to user's exact form; edit step files carrying blocking approval steps; new default mode and flag gated in exactly two places: a `SKILL.md` Rules bullet + affected step files. No third copy.
6. **Verify final shape.** `ls references/` shows only `step-` prefixed files; each title carries step number; zero old filename hits; `approv`/`wait for`/`explicit confirmation` hits only in intentionally re-worded step files; markdown gate passes; commit scoped to target paths only; `git diff --cached --name-only` checked first.

## Completion

- Edit applied at single owner; no second copies.
- Pattern A consolidation (if requested): merged file has numbered sections in execution order, decision trees use section markers not file links, Routing table collapsed to one row, grep sweep returns zero old-filename hits, source files deleted.
- Pattern B restructure (if requested): only `step-` prefixed files, zero old filename hits, mode semantics synced across Rules, `argument-hint`, and step files.
- Commit scoped to target skill's paths only.
