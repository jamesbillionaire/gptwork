---
name: lavi-quotation
description: Create or revise LAVI Technologies quotations with the approved CPSC infrastructure design, source-grounded data and rendered QA.
---
Read `AGENTS.md`, `LATEST.md`, `quotation_engine/manifest.json`, `quotation_engine/README.md`, then `templates/lavi/cpsc-2026/README.md`.

Use `LAVI-QUOTATION-2026.10`, brand `lavi`, on **Legal paper: 8.5 x 14 inches (612 x 1008 pt)**. Both active brands share this paper size but retain separate designs. Start a blank structured job with `python -m quotation_engine.cli new --brand lavi --output work/job.json`; consult `examples/cpsc-01.json` or `examples/cpsc-02.json` for component patterns, not reusable commercial values. Do not select the Lifes Awesome or archived pre-CPSC LAVI profile.

Preserve approved quantities, prices, date, recipient, warranty, tax and preparer. No raw font files or copied signature. Use the official logo, same content rail, justified body, centered QTY/UNIT, right-aligned prices, hanging lists, repeated table headers and shared diagram component. Later pages never repeat the logo. Render with the CLI, run tests, and inspect every final page including the architecture at readable scale.

Return the PDF and a short change summary; update LATEST.md. Style/engine changes require James's explicit authorization, new version IDs, hashes, fixtures and QA. Do not write a one-off quotation renderer.

## LAVI balanced typography — 26 September 2026

Engine 2.3.1 / `LAVI-QUOTATION-2026.10`: title 16 pt; section 11 pt; subsection 10 pt; body/notes 9.5 pt; BOQ/general table 9 pt; metadata/labels 9.5 pt; first-page company heading 9 pt; business contact/footer/page furniture 8 pt; diagram text 9 pt. The 8 pt role is furniture/contact only, not body text.

Use marker-rail lists for bullets and numbering. QTY/UNIT are centered, description left, currency right. LAVI defaults to a two-column Prepared By / Conforme sign-off with Conforme on the right, 18 pt gutter and 14 pt panel padding. Preserve full content rails and natural pagination.

Lifes Awesome is unchanged; do not apply these LAVI sizes to it. Existing LAVI jobs must be explicitly migrated to template ID 2026.8 without changing commercial content.


Preserve the 34/66 two-column terms-table standard, balanced opening cards, list-row breathing and the expanded 148 pt sign-off. These are reusable LAVI template rules, not one-off client patches.


## LAVI list/signature alignment correction — 26 September 2026

Engine **2.3.1** / **LAVI-QUOTATION-2026.10** keeps the approved 2026.9 typography, card geometry, table widths and spacing. Bullet and numbered markers now use a dedicated marker flowable whose baseline is mathematically tied to the first text-line baseline, so markers stay vertically aligned even when an item wraps. The Prepared By / Conforme box size is unchanged; only the Prepared By signature line is repositioned to sit directly above the printed preparer name instead of floating near the middle of the panel.
