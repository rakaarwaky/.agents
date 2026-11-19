---
name: pdf
description: "Create, read, merge, fill, and secure PDF files. Use when generating PDFs, extracting text/tables, building or filling AcroForm forms, merging/splitting/watermarking/stamping pages, encrypting or decrypting documents, or preparing official IRS tax forms."
when-to-use: "Use when generating reports/invoices as PDF, building or filling AcroForm forms (with layout linting and visual overlays), extracting text, tables, metadata, or form-field values, merging/splitting/rotating/watermarking/stamping pages, exporting pages as PNGs for visual review or OCR hand-off, managing metadata/attachments, or encrypting/decrypting with passwords. NOT for scanned/image-only PDFs (see references/ocr-extraction.md) and NOT for pixel-perfect HTML-to-PDF rendering (use a headless browser)."
argument-hint: "<create | make-form | lint-form | read | merge | split | fill | secure | watermark | stamp | page-image | meta> <in [out]>"
---

# PDF Skill

Generate, parse, manipulate, and secure PDF documents, including AcroForm creation and filling, table extraction, metadata handling, and IRS tax form processing.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Halt text extraction on scanned image-only PDFs; export 300 dpi page images and route to OCR extraction. | Inspect page structure and verify fallback to OCR pipeline when text layer is absent. |
| R2 | Inspect PDF metadata prior to processing; decrypt encrypted files before performing structural modifications. | Run `pdf_read.py --meta` and verify encryption status before operations. |
| R3 | Enforce page rotations as strict multiples of 90 degrees. | Validate rotation angle parameter is 0, 90, 180, or 270. |
| R4 | Re-read output documents following every manipulation to verify file integrity and content accuracy. | Run validation re-read on generated or updated PDF artifacts. |

## Routing

| Step | Reference | Purpose |
| --- | --- | --- |
| Commands, procedure, pitfalls, verification | [`references/usage.md`](references/usage.md) | When to Use, bundled toolchains, prerequisites, quick-reference command table, end-to-end procedure, full pitfall list, and the post-operation verification checklist. |
| Building or filling AcroForms | [`references/forms.md`](references/forms.md) | Field-spec geometry, radio groups, `NeedAppearances` behavior, layout-lint rules, and the visual review loop. |
| A page is image-only | [`references/ocr-extraction.md`](references/ocr-extraction.md) | pymupdf-vs-marker decision table, `scripts/extract_pymupdf.py`, and `scripts/extract_marker.py --check` for disk headroom. |
| Text-in-existing-PDF by description | [`references/nano-pdf-editing.md`](references/nano-pdf-editing.md) | `nano-pdf edit f.pdf 3 "…"` — not for structural work. |
| IRS tax forms (2025) | [`references/tax-forms.md`](references/tax-forms.md), [`references/tax.md`](references/tax.md) | Required reading before filling any form in `forms/`; `tax.md` covers the preparation workflow. |
| Advanced rendering & tooling | [`references/rendering-and-advanced.md`](references/rendering-and-advanced.md) | pypdfium2 rendering, pdf-lib / pdfjs-dist JavaScript, qpdf / poppler flags, performance tuning, and troubleshooting. |
