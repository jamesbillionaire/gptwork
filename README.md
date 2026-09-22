# GPTWork

Persistent work instructions and reusable approved document engines for James Brown Bete's companies.

**New agent: read [AGENTS.md](AGENTS.md), then [LATEST.md](LATEST.md).**

## Active quotation templates

| Issuer | Active template | Read |
|---|---|---|
| LAVI Technologies Inc. | LAVI-QUOTATION-2026.6 — Legal 612 x 1008 pt, teal/navy, Liberation Sans | [LAVI guide](templates/lavi/cpsc-2026/README.md) |
| Lifes Awesome Ventures Inc. | LIFES-AWESOME-QUOTATION-2026.3 — Legal, cyan/gray, DejaVu Sans | [Lifes Awesome guide](templates/lifes-awesome/cpsc-2026/README.md) |

Both were approved from CPSC Projects 1, 2, 5 and 8. Use the [quotation engine](quotation_engine/README.md); do not recreate the template for each job. [Profile tokens](quotation_engine/profiles.json), [source fingerprints](quotation_engine/reference/sources.json) and [reference header/diagram crops](quotation_engine/reference/previews/) make the design independent of a previous chat or container.

```sh
python -m pip install -r requirements.txt
python -m quotation_engine.cli new --brand lavi --output work/job.json
# Populate approved job data, then:
python -m quotation_engine.cli validate work/job.json
python -m quotation_engine.cli render work/job.json --output output/pdf/quotation_v1.pdf
```

For Lifes Awesome use `--brand lifes-awesome`. Install the documented fonts; do not distribute font files. Original logos are versioned, signatures are not reusable. Client dates, terms, prices and provisional quantities belong in job JSON, not profile defaults.

## Quality and history

Run `python -m unittest discover -s quotation_engine/tests -v`. CI generates all four complete PDF examples and per-page preview artifacts. Visually inspect every final client PDF; passing tests are not a substitute.

The superseded engine/rules and old handoff remain under `legacy/` and `.agents/handoffs/`. Earlier billing, other-brand, bidding and project records remain intact. Old template packages are historical, not active quotation defaults.

## Minimum readable typography — 22 September 2026

Engine **2.1.0** establishes an absolute **10-point minimum for all live text** in both brand profiles; body paragraphs and conditions are **11/15 pt**. BOQ, table, note, metadata, diagram, contact, header and footer text must never fall below 10 pt. Section headings are 13/17 pt; subheadings 11/14 pt; titles 20/24 pt LAVI and 20/25 pt Lifes Awesome. See `quotation_engine/reference/readability_standard.md`, which supersedes earlier small-font size and leading values in historical examples or prose.

Preserve separate brand fonts/colors, supplied logos, Legal paper and horizontal content rails. Headers/footers and diagrams wrap with measured heights, never reduced type. Readability takes priority over historical page counts. Continuous jobs retain `front_page_break: false`; the padded LAVI sign-off retains 14pt internal padding and 18pt gutter. No live font may be reduced to force a two-page quotation. Existing delivered PDFs are not changed in bulk.

Migrate structured jobs by explicitly updating their template IDs. Source commercial data, including contradictory source terms, must not be silently reconciled during a typography-only edit. Run the locked CLI, all tests, minimum-font checks, content/arithmetic comparisons and rendered visual inspection.
