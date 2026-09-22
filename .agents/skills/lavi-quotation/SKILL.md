---
name: lavi-quotation
description: Create or revise LAVI Technologies quotations with the approved CPSC infrastructure design, source-grounded data and rendered QA.
---
Read `AGENTS.md`, `LATEST.md`, `quotation_engine/manifest.json`, `quotation_engine/README.md`, then `templates/lavi/cpsc-2026/README.md`.

Use `LAVI-QUOTATION-2026.6`, brand `lavi`, on **Legal paper: 8.5 x 14 inches (612 x 1008 pt)**. Both active brands share this paper size but retain separate designs. Start a blank structured job with `python -m quotation_engine.cli new --brand lavi --output work/job.json`; consult `examples/cpsc-01.json` or `examples/cpsc-02.json` for component patterns, not reusable commercial values. Do not select the Lifes Awesome or archived pre-CPSC LAVI profile.

Preserve approved quantities, prices, date, recipient, warranty, tax and preparer. No raw font files or copied signature. Use the official logo, same content rail, justified body, centered QTY/UNIT, right-aligned prices, hanging lists, repeated table headers and shared diagram component. Later pages never repeat the logo. Render with the CLI, run tests, and inspect every final page including the architecture at readable scale.

Return the PDF and a short change summary; update LATEST.md. Style/engine changes require James's explicit authorization, new version IDs, hashes, fixtures and QA. Do not write a one-off quotation renderer.

## Minimum readable typography — 22 September 2026

Engine **2.1.0** establishes an absolute **10-point minimum for all live text** in both brand profiles; body paragraphs and conditions are **11/15 pt**. BOQ, table, note, metadata, diagram, contact, header and footer text must never fall below 10 pt. Section headings are 13/17 pt; subheadings 11/14 pt; titles 20/24 pt LAVI and 20/25 pt Lifes Awesome. See `quotation_engine/reference/readability_standard.md`, which supersedes earlier small-font size and leading values in historical examples or prose.

Preserve separate brand fonts/colors, supplied logos, Legal paper and horizontal content rails. Headers/footers and diagrams wrap with measured heights, never reduced type. Readability takes priority over historical page counts. Continuous jobs retain `front_page_break: false`; the padded LAVI sign-off retains 14pt internal padding and 18pt gutter. No live font may be reduced to force a two-page quotation. Existing delivered PDFs are not changed in bulk.

Migrate structured jobs by explicitly updating their template IDs. Source commercial data, including contradictory source terms, must not be silently reconciled during a typography-only edit. Run the locked CLI, all tests, minimum-font checks, content/arithmetic comparisons and rendered visual inspection.
