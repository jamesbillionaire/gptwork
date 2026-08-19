# LAVI Locked Quotation Engine

This package is the authoritative production system for new general LAVI quotations. It converts validated JSON job data into the approved Legal-size PDF. Ordinary quotation work must change only a job file; it must not recreate or restyle the renderer.

## Commands

```bash
python -m quotation_engine.cli validate path/to/quotation.json
python -m quotation_engine.cli render path/to/quotation.json --output output/pdf/quotation.pdf
python -m unittest discover -s quotation_engine/tests -v
```

Start from `examples/approved_sample.json`. The engine calculates line amounts, subtotal, 12% VAT, and grand total. Do not put calculated line amounts in job data.

## Locked release

- Template ID: `LAVI-QUOTATION-2026.2`
- Status: `APPROVED_LOCKED`
- Page size: Legal, 612 × 1008 points
- Section titles: `PREPARED QUOTATION FOR`, `SCOPE AND PRICING`, `ADDITIONAL NOTES`
- Pricing columns: `32.5 / 36.0 / 275.5 / 94.4 / 94.4` points
- Numeric cells and every total are right-aligned.
- The totals grid reuses the last two pricing-column widths.

`manifest.json` records the approved assets and release checksums. The approved reference PDF remains under `templates/lavi/quotation-2026/`, while `golden/approved_sample_contract.json` locks the sample page count, dimensions, required labels, and extracted-content fingerprint.

## Change boundary

Quotation edits may change client details, project data, introduction, line items, pricing basis, additional notes, and signatures in JSON.

Template revisions require James's explicit approval, a new template ID, a regenerated golden PDF, updated checksums, passing tests, and a reviewed version-control change. Never create a project-specific rendering script.
