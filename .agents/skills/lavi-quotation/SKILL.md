---
name: lavi-quotation
description: Create, revise, validate, and render general LAVI Technologies quotations with the repository's locked PDF engine. Use for any LAVI quotation job, scope-and-pricing PDF, quotation revision, VAT or line-item update, or request to preserve the approved LAVI 2026 quotation template.
---

# LAVI Quotation

Use `quotation_engine/` as the only production renderer for new general LAVI quotations.

## Workflow

1. Read the repository `AGENTS.md` and `quotation_engine/manifest.json`.
2. Copy `quotation_engine/examples/approved_sample.json` to a task-specific job file.
3. Change only structured quotation data. Never copy or create a standalone ReportLab, Word, HTML, or drawing script.
4. Preserve the exact locked `template_version`.
5. Confirm client facts, scope, quantities, unit prices, VAT treatment, notes, signatures, and filename with the authoritative task data.
6. Run:

   ```bash
   python -m quotation_engine.cli validate path/to/job.json
   python -m quotation_engine.cli render path/to/job.json --output output/pdf/name.pdf
   python -m unittest discover -s quotation_engine/tests -v
   ```

7. Run the applicable PDF preflight, render every page, and inspect the actual images before delivery.
8. Deliver only the reviewed PDF and report its page count and totals.

## Lock boundary

Treat client, scope, descriptions, quantities, prices, notes, and signatures as job data. Treat typography, layout, colors, logo, cards, columns, totals geometry, headings, continuation elements, and footers as locked engine behavior.

Do not edit the renderer during an ordinary quotation task. A template change requires James's explicit approval, a new template release, refreshed golden fixture and checksums, and passing regression tests.
