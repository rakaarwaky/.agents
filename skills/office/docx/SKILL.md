---
name: docx
description: Create, read, edit, template, and review Word .docx files with python-docx CLIs: text, styles, tables, images, {{token}} templates, tracked changes, comments, TOC, and page-number fields.
when-to-use: "Use when generating, reading, editing, or templating Word .docx files — reports, letters, contracts — including tracked changes, comments, TOC, and page-number fields."
argument-hint: "create <spec.json> <out.docx>|read <file.docx> [--text|--structure|--styles|--images <dir>|--revisions]|edit replace <file.docx> --find <old> --replace <new>|edit set-cell <file.docx> --table N --row N --col N --text <text>|edit insert <file.docx> --index N --text <text>|edit delete <file.docx> --index N|edit style <file.docx> --index N --style <name>|edit normalize <file.docx>|edit toc <file.docx> --index N|edit page-numbers <file.docx>|template <tpl.docx> <values.json> <out.docx> [--strict]|revisions list <file.docx>|revisions accept-all <file.docx>|revisions reject-all <file.docx>|revisions accept <file.docx> --id N|revisions reject <file.docx> --id N|comments list <file.docx>|comments add <file.docx> --target <text> --text <comment>|comments delete <file.docx> --id N|validate <file.docx>"
---

# Docx Skill

Create, read, edit, and template Microsoft Word `.docx` documents using python-docx and XML CLI toolchains, managing formatting, tracked changes, comments, and structure validation.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Run every helper through `scripts/`; never perform raw text replacement on unpacked XML directly. | Inspect script invocations to confirm provided CLI tools are used. |
| R2 | Verify document integrity after every produce or edit action using `docx_read.py` and `docx_validate.py`. | Run validation script and verify zero schema or package errors. |
| R3 | Always run `normalize` before find-replace operations on documents previously edited in Microsoft Word. | Verify `docx_edit.py normalize` merges adjacent formatted runs prior to replacements. |
| R4 | Follow raw-XML toolchain rules when editing template redlines in place without recreating documents. | Confirm template modifications preserve existing document packaging and styles. |

## Routing

| Step | Reference | Purpose |
| --- | --- | --- |
| Commands + procedure | [`references/usage.md`](references/usage.md) | Prerequisites, quick-reference command table, end-to-end procedure, Converting to PDF, and the post-edit verification checklist. |
| Raw-XML toolchain | [`references/xml-editing.md`](references/xml-editing.md) | Unpack/repack, redlining, `.dotx` templates, tracked changes via LibreOffice. |
| Tracked changes + comments | [`references/revisions-and-comments.md`](references/revisions-and-comments.md) | Revision types, acceptance flow, comment threading, and which edge cases to hand to Word. |
| Edge-case behaviors | [`references/pitfalls.md`](references/pitfalls.md) | Run fragmentation, revision coverage limits, field results, validation semantics, style numbering, cell formatting, and encoding. |
