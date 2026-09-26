# GPTWork

Persistent work instructions and reusable approved document engines for James Brown Bete's companies.

**New agent: read [AGENTS.md](AGENTS.md), then [LATEST.md](LATEST.md).**

## Active quotation templates

| Issuer | Active template | Read |
|---|---|---|
| LAVI Technologies Inc. | LAVI-QUOTATION-2026.8 — Legal 612 x 1008 pt, teal/navy, Liberation Sans | [LAVI guide](templates/lavi/cpsc-2026/README.md) |
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

## LAVI balanced typography — 26 September 2026

Engine **2.2.0** promotes LAVI to **LAVI-QUOTATION-2026.8**. The LAVI profile now uses a restrained hierarchy: 16 pt title, 11 pt section headings, 10 pt subheadings, 9.5 pt body, 9 pt BOQ/table text, 9.5 pt metadata/labels, 9 pt first-page company heading, and 8 pt contact/footer/page furniture. Proper marker rails replace paragraph indents for LAVI bullet and numbered lists, BOQ alignment remains QTY/UNIT centered and currency right aligned, and two-column Prepared By / Conforme is the LAVI default sign-off.

Lifes Awesome Ventures remains **LIFES-AWESOME-QUOTATION-2026.3** with its 2.1.0 typography and rendered appearance unchanged. Legal paper, separate brand fonts/colors, original logos and full-width content rails remain mandatory.

Existing structured LAVI jobs require an explicit template-ID migration to 2026.8. Preserve client content, prices and terms while changing layout. Run the locked CLI, all tests and rendered visual inspection before delivery.
