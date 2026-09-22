---
name: lifes-awesome-quotation
description: Create or revise Lifes Awesome Ventures quotations using the approved cyan/gray CPSC software proposal design.
---
Read `AGENTS.md`, `LATEST.md`, `quotation_engine/manifest.json`, `quotation_engine/README.md`, then `templates/lifes-awesome/cpsc-2026/README.md`.

Select `LIFES-AWESOME-QUOTATION-2026.3`, brand `lifes-awesome`. This profile is approved, not a candidate. Use **Legal paper: 8.5 x 14 inches (612 x 1008 pt)**, DejaVu Sans and the supplied Lifes Awesome logo/cyan-gray palette. Both brands now share the same paper size; do not use LAVI's separate teal/navy infrastructure design. The heading, deliverable fees, section subtotals, role titles and source boundaries follow this brand's profile.

Start a blank job via `python -m quotation_engine.cli new --brand lifes-awesome --output work/job.json`. Refer to `examples/cpsc-05.json` and `examples/cpsc-08.json` for structure. Never copy their prices, dates, validity, migration limits, implementation terms or integrations into a different client job by default. Distinguish historical migration from live integration and from cloud hosting. Provisional allowances are not confirmed client counts.

Validate and render using the shared engine, run tests, inspect every final page and exact diagrams, then update LATEST.md. No one-off generator, hidden recurring hosting commitment, automatic VAT, copied signature or silent font substitution. The preparer role is explicit job data; these CPSC examples use James Brown Bete / General Manager.

## Minimum readable typography — 22 September 2026

Engine **2.1.0** establishes an absolute **10-point minimum for all live text** in both brand profiles; body paragraphs and conditions are **11/15 pt**. BOQ, table, note, metadata, diagram, contact, header and footer text must never fall below 10 pt. Section headings are 13/17 pt; subheadings 11/14 pt; titles 20/24 pt LAVI and 20/25 pt Lifes Awesome. See `quotation_engine/reference/readability_standard.md`, which supersedes earlier small-font size and leading values in historical examples or prose.

Preserve separate brand fonts/colors, supplied logos, Legal paper and horizontal content rails. Headers/footers and diagrams wrap with measured heights, never reduced type. Readability takes priority over historical page counts. Continuous jobs retain `front_page_break: false`; the padded LAVI sign-off retains 14pt internal padding and 18pt gutter. No live font may be reduced to force a two-page quotation. Existing delivered PDFs are not changed in bulk.

Migrate structured jobs by explicitly updating their template IDs. Source commercial data, including contradictory source terms, must not be silently reconciled during a typography-only edit. Run the locked CLI, all tests, minimum-font checks, content/arithmetic comparisons and rendered visual inspection.
