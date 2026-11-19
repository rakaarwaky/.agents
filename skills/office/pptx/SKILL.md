---
name: pptx
description: Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates, layouts, speaker notes, or comments. Trigger whenever the user mentions 'deck', 'slides', 'presentation', or references a .pptx filename, regardless of what they plan to do with the content afterward. If a .pptx file needs to be opened, created, or touched, use this skill.
when-to-use: "Use whenever any .pptx file is involved — creating, reading, editing, combining, splitting, or working with templates, layouts, speaker notes, or comments — triggered by 'deck', 'slides', 'presentation', or a .pptx filename. Also use for structured programmatic work on .pptx decks via python-pptx (create from JSON spec, structured read-back, targeted text/chart/image edits, template filling, slide PNG rendering) and the legacy binary .ppt — convert it with `soffice --convert-to pptx old.ppt` first."
argument-hint: "thumbnail <file.pptx>|check-overlaps <unpacked_dir> [--fix]|detect-fonts <file.pptx>|render-slides <file.pptx> [--output_dir <dir>] [--width N] [--height N]|add-slide <unpacked_dir> <source> [--after <slide>]|delete-slide <unpacked_dir> [<slide>...] [--keep <slide>...]|replace-text <slide.xml> [--ph <type>|--match <text>] --text <new>|replace-nth-text <slide.xml> --find <text> --nth N --text <new>|resize-shape <slide.xml> [--ph <type>] [--width <in>] [--height <in>]|inspect-slide <unpacked_dir> [--theme] [--media]|clean <unpacked_dir>|media-grid <unpacked_dir>|search-templates <query>|create <deck.json> <out.pptx>|read <deck.pptx> [--outline|--notes|--images <dir>]|edit <deck.pptx> <op> <args>|from-template <tpl.pptx> <out.pptx> --values <vals.json>|render <deck.pptx> --outdir <dir>"
---

# PPTX Skill

Generate, edit, template, and validate presentation decks across raw XML unpacking workflows, PptxGenJS generation, and python-pptx programmatic tools.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Complete at least one quality assurance fix-and-verify cycle before declaring presentations finished. | Verify QA review checklist and automated overlap checks are completed. |
| R2 | Prefer editing workflows directly on existing templates whenever a template file is provided. | Check that incoming `.pptx` template is modified in place rather than rebuilt from scratch. |
| R3 | Preserve template visual styling strictly: colors, fonts, backgrounds, and layout relationships. | Compare output typography and color palette against original template styles. |
| R4 | Convert legacy binary `.ppt` presentations using `soffice --convert-to pptx` before programmatic processing. | Confirm input files are in `.pptx` format prior to manipulation. |

## Routing

| Step | Reference | Purpose |
| --- | --- | --- |
| Workflow selection + reading + image conversion + dependencies | [`references/workflow-selection.md`](references/workflow-selection.md) | Which workflow to use per situation, content-reading commands, slide-to-image conversion, and install dependencies. |
| Edit an attached `.pptx` template | [`references/editing.md`](references/editing.md) | Raw XML unpack/edit/pack workflow: inspect, replace text/media, repack. |
| Create a de novo deck | [`references/creating.md`](references/creating.md) | PptxGenJS template-based creation from scratch. |
| Structured python-pptx operations | [`references/python-pptx.md`](references/python-pptx.md) | Create from JSON spec, read-back, targeted text/chart/image edits, template fill, and slide PNG rendering. |
| Image handling rules | [`references/images.md`](references/images.md) | Aspect-ratio rule, sources, options, sizing modes, and dimension calculations. |
| QA checklist | [`references/qa.md`](references/qa.md) | Overlap check/auto-fix, content QA, automated checks, visual QA, and the fix-and-verify loop. |
| Edge-case pitfalls | [`references/pitfalls.md`](references/pitfalls.md) | Run splitting, chart duplication limits, XML-level reordering, footer/slide-number constraints, hyperlinks, template sizing, layout indexes, UTF-8 specs. |
