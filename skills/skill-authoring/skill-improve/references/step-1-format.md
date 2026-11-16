# Improve — Step 1: Body shape, frontmatter keys, and lint rule catalog

**Goal:** verify the target `SKILL.md` uses exactly `# Title` / `## Rules` / `## Routing`, state which frontmatter keys are mandatory vs optional, and know every `sac lint` rule.

## Body shape

Every skill being improved must use this exact body shape in `SKILL.md`:

```
# Title

## Rules

## Routing
```

- **Title** — one `#` heading with the skill name.
- **Rules** — one table row per rule, columns `ID | Rule | Covers | Check`. Cross-step policy, invariants, record formats, and any fact read by more than one step. A stop condition is a row, not a fourth heading.
- **Routing** — a table of contents mapping each step/reference to its purpose.

All task data, commands, field shapes, examples, stop conditions, and worked examples belong in `references/*.md` or `scripts/*`. If the body contains anything beyond the three sections above, move it to a reference file before publishing.

Verified mechanically: `grep -n '^#' <SKILL.md>` returns only the `#` title and exactly two `##` headings — `## Rules`, `## Routing`. `sac lint` does not check this (body shape is convention-enforced); the grep is the check. Case matters: the heading is `## Rules`.

A stop-condition is never its own `## Completion` section in the body — it is one row in `## Rules` (e.g. "**Completion.** <criterion>"), because a fourth heading breaks the three-section shape.

Moving a section out of the body to a reference is a **two-part edit**: the heading move *and* the Routing-table row that pointed at the in-body section. A row like `| SKILL.md <Section> | ... |` is a self-referential dangling entry once `<Section>` no longer exists in the body; either delete it or re-point it at the reference file that now owns the content. Verify with `grep 'SKILL.md ' <SKILL.md>` on the Routing table that no row still names a heading that has been moved out.

## Frontmatter keys

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Validator rules `name-format`, `name-mismatch`. |
| `description` | Yes | Validator rules `description-*`. Keep it on one line (quoted when needed); a `>-` block scalar that runs straight into the `# Title` heading is dropped by the `sac` parser and fires `missing-description`. |
| `when-to-use` | Yes | Dedicated trigger phrases; Grok Build matches it together with `description`. Same 1,024-char limit as `description`. |
| `argument-hint` | Yes | Slash-command autocomplete hint, e.g. `<command> [--flag]`. |
| `user-invocable` | Optional | Boolean, default `true`. `false` hides the skill from slash commands and the model's skill tool. |
| `disable-model-invocation` | Optional | Boolean, default `false`. `true` keeps the skill out of the model's listing; slash commands still run it. |
| `paths`, `model`, `effort`, `allowed-tools`, `license`, `compatibility`, `origin`, `metadata` | Optional | Grok Build controls. |
| anything else (`version`, `author`, `platforms`, ...) | Optional | Target-dependent; match the field set the destination validator enforces. |

## Lint rule catalog

Run `sac lint` (whole pack) or `sac lint --category <name>` (scoped).

| Rule | Meaning |
|------|---------|
| `name-mismatch` | Frontmatter `name` equals the skill directory name. |
| `name-format` (invalid-skill-name) | Skill names are lowercase letters, digits, and hyphens. |
| `description-present` (missing-description) | Every skill carries a description the validator can parse. A `>-` block scalar immediately followed by a `#` heading is parsed as body and fires `missing-description`. |
| `description-characters` (invalid-description-characters) | Descriptions contain no `<`, `>`, or `"`. |
| `description-length` (description-too-long) | Descriptions are at most 1,024 characters. |
| `when-to-use-length` (when-to-use-too-long) | When-to-use strings are at most 1,024 characters. |
| `skill-placement` (invalid-placement) | `SKILL.md` lives at `<category>/<skill>/SKILL.md`. |
| `too-deep` | `SKILL.md` is nested too deep without a `pack.toml` marker. |
| `unique-skill-name` (duplicate-skill-name) | Each skill name is used by one folder only. |
| `unique-description` (duplicate-description) | No two skills share one description. |
| `missing-category-description` | A category folder has no `DESCRIPTION.md`. |
| `empty-category-description` | A category `DESCRIPTION.md` has no description text. |
| `empty-category` | A category folder contains no skills. |
| `reference-not-linked` | Every file in `references/` must be linked from the `SKILL.md` body or Routing table. The checker lists each skill's `references/` tree and requires each file's basename to appear somewhere in `SKILL.md` — markdown link, bare path mention, or plain text all count. To fix: add one sentence at the top of the matching `##` section (body) or one Routing-table row (`[`references/<file>.md`](references/<file>.md)` + one clause of what it covers). Verify with `sac lint`. |

## What lint does NOT check

`sac lint` is a mechanical gate on frontmatter, naming, placement, uniqueness, and reference linking. It does **not** verify:

- **Dangling cross-skill refs** — `related_skills:` and sibling mentions are existence-checked manually. Resolve each named skill against the tree.
- **Body shape** — the three-section rule is enforced by convention and the pre-publish checklist, not by lint.

## Completion

- Target `SKILL.md` body is exactly `# Title` / `## Rules` / `## Routing`; overflow is in references.
- Mandatory frontmatter keys (`name`, `description`, `when-to-use`, `argument-hint`) present and spelled correctly.
- Every `sac lint` rule understood and its fix known.
- `--dry-run` stops here with no writes.
