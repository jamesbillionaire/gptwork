# GPTWork — approved document engines

## Start here on every fresh quotation task

1. Read this file, then `LATEST.md`.
2. Read `quotation_engine/README.md` and `quotation_engine/manifest.json`.
3. Select the correct brand in `quotation_engine/profiles.json` and its template guide.
4. Read the actual client/source documents and the latest direct instructions from James.
5. Change structured job JSON only. Validate, render, run tests, and inspect every rendered page before delivery.

James explicitly approved replacing the previous quotation engines with the CPSC Projects 1, 2, 5 and 8 design family on **21 September 2026**. This instruction supersedes earlier quotation geometry, palette, font, template-status and default-renderer instructions. It does not approve new quantities, equipment models, prices, commercial terms or signatures.

## Active quotation profiles — do not blend the brands

| Brand | Active template | Approved design basis | Page / typography |
|---|---|---|---|
| LAVI Technologies Inc. | `LAVI-QUOTATION-2026.9` | Project 1 corrected network diagram + Project 2 corrected CCTV quotation, with James' 26 Sep 2026 typography/alignment and spacing revision | Legal 612 x 1008 pt, 15 mm side margins, Liberation Sans; teal/navy |
| Lifes Awesome Ventures Inc. | `LIFES-AWESOME-QUOTATION-2026.3` | Project 5 V2 + Project 8 V1 | Legal 612 x 1008 pt, 32 pt side margins, DejaVu Sans; cyan/gray |

These are **two different approved templates**, not the same page recolored. Lifes Awesome is now APPROVED_LOCKED, not a candidate. For this CPSC family, LAVI handles infrastructure; Lifes Awesome handles software. Never infer the issuer from the generic name “LAVI”: use the legal company explicitly requested.

### Non-negotiable visual rules

- **Both active brands use Legal paper, 8.5 x 14 inches (612 x 1008 points), on every page.** James explicitly corrected the paper standard on 21 September 2026. This supersedes the earlier LAVI A4 source geometry; historical source sizes are evidence only, not production defaults. Keep the separate brand margins, typography, colors and logo arrangements. Do not crop, stretch or scale an existing PDF to satisfy this rule; render/reflow from approved job data.

- Preserve supplied logo artwork and aspect ratio; page 1 only. Continuation pages have text-only headers, with the quotation reference aligned to the right content edge.
- Use one full-width content rail. Tables, cards, headings, dividers, totals and diagram boundaries share its left/right edges. Internal card padding is intentional and does not change the outer rail.
- Justify narrative paragraphs. Keep labels/headings left aligned, QTY/UNIT centered and currency right aligned; never justify numerals or short diagram labels.
- Use the locked font family, font-size/leading hierarchy and palette for the selected profile. No mixed body/note sizes within one semantic role. Do not silently substitute fonts.
- LAVI lists use a dedicated marker rail: bullet/number markers occupy their own narrow column and wrapped text starts on one consistent text rail. Two-digit numbering must fit without nested indentation. Lifes Awesome keeps its existing list rendering.
- Preserve restrained zebra rows, thin grid lines, pale-gold totals, readable small contact details and compact footers with calculated `Page x of y`.
- Keep table rows intact and repeat headers. Keep a heading with meaningful following content. Do not leave a section title alone at a page bottom.
- Let the body paginate from content. Keep the executive-summary opening boundary only when selected; when continuous flow is requested set `front_page_break: false` so Section 1 can follow the Project Boundary card on page 1. Never imitate a page count or add filler. LAVI now defaults to the padded two-column `Prepared By` / `Conforme` sign-off; preserve its 14-point padding and 18-point gutter. Lifes Awesome remains prepared-only unless explicitly changed.
- Architecture diagrams must use the shared component with row positions calculated from preceding heights, a separate caption lane and constant connector gaps. Never independently anchor the bottom boxes. Arrows must stay inside the gaps; multiple destinations require a proper split connector. No connector through a label or shape.
- Layout-only edits preserve approved scope, quantities, rates, totals, date, recipient, role, exclusions and other details. Compare before/after pages outside the intended edit.
- Render and inspect the exact final PDF, including diagrams at readable size. A successful code run or a contact sheet alone is not visual approval.

## Production commands

```sh
python -m pip install -r requirements.txt
python -m quotation_engine.cli profiles
python -m quotation_engine.cli new --brand lavi --output work/new-quotation.json
# Fill all client/project/commercial fields; do not copy CPSC defaults into a new job.
python -m quotation_engine.cli validate work/new-quotation.json
python -m quotation_engine.cli render work/new-quotation.json --output output/pdf/quotation_v1.pdf
python -m unittest discover -s quotation_engine/tests -v
```

Use `--brand lifes-awesome` for Lifes Awesome. Approved example jobs are `quotation_engine/examples/cpsc-01.json`, `cpsc-02.json`, `cpsc-05.json`, and `cpsc-08.json`. They are historical CPSC fixtures, not universal content defaults. The first two source/diagram crops for each are under `quotation_engine/reference/previews/`; full rendered regression PDFs are produced by CI and the render-examples command.

Ordinary agents must not create standalone ReportLab, Word, HTML, canvas or SVG quotation generators. Edit job data only. An explicitly authorized template revision requires new version IDs, updated source authority/provenance, refreshed checksums, regression fixtures/tests and rendered visual review.

## Commercial and technical integrity

- Treat dates, validity, implementation periods, warranty, VAT, recipient and signatory title as **job data**. Do not hardcode 18 September, 30/60 days, CEO or General Manager into the engine.
- Inclusive line prices are summed as-is. Never automatically add 12% again. VAT-exclusive quotes must not acquire a tax line unless the approved job explicitly supplies the adjustment and amount. Reconcile every extension, subtotal, adjustment, payment allocation and total.
- A pricing ceiling is not a target to manufacture with inflated quantities or rates. CPSC fixture prices are not vendor quotations, current market rates or a universal markup policy.
- Preserve approved abbreviations/terminology; spell out technical terms when drafting new content rather than introducing unexplained jargon.
- Separate confirmed requirements from proposed assumptions/allowances. CPSC #5 explicitly requests integration; historical-data migration quantities and fees in #5/#8 are supplier-proposed allowances, not counts supplied by CPSC.
- #5 excludes Registrar #7 development and Legal #8 development/live integration; #8 has its separately priced, bounded legal-side connector. Do not duplicate these scopes.
- Cloud production / Supabase / PITR / independent or campus backups remain a proposal for CPSC discussion and approval. Do not silently insert a hosting subscription or recurring managed-service obligation into either software quote.
- No copied signatures in reusable templates, fixtures or sample outputs. An original signed document may be an evidence source, but its signature is not a reusable asset. No raw font files are committed or distributed.
- Source-code ownership, warranties, support promises and government approval are not generic boilerplate; retain only approved and scoped commitments. Never guarantee approval or award.

## Other document types and historical work

This release changes quotation production for the two specified brands only. Billing, FDAS assessment content, bidding forms and other company/document standards are preserved in `legacy/AGENTS-pre-cpsc-2026.md` and existing source directories. Their older quotation geometry must not override the new profiles. Do not alter another brand or a billing engine under a quotation-template task.

The previous engine and manifest are preserved at `legacy/quotation_engine-pre-cpsc/` for audit/history. Reproduce old output from the historical commit, not by selecting it as the default for a new quotation. Earlier template packages are historical references, not the active starting point.

## Persistent handover

Before ending meaningful work update `LATEST.md`: status, approved decisions, exact files, tests/render review, blockers and next steps. Archive a superseded substantial handoff in `.agents/handoffs/`. Do not use memory alone as the source of truth and do not declare archived unfinished work completed without evidence. Git `main`, active manifests and source/job data are the durable authority for the next agent.

## LAVI balanced typography and alignment — 26 September 2026

Engine **2.2.0** / **LAVI-QUOTATION-2026.9** supersedes the blanket 10-point LAVI rule. James explicitly set these LAVI roles: title **16 pt**; section headings **11 pt**; subheadings **10 pt**; body **9.5 pt**; BOQ/general table text **9 pt**; metadata/labels about **9.5 pt**; first-page top-right `LAVI TECHNOLOGIES INC.` **9 pt**; business address/contact and page furniture/footer **8 pt**. LAVI diagrams use 9 pt text. Do not shrink semantic content roles below their profile sizes to fit pages.

LAVI QTY and UNIT stay centered; DESCRIPTION stays left aligned; UNIT PRICE and AMOUNT stay right aligned. General two-column condition/payment/warranty tables are vertically centered within rows and remain on the full content rail. LAVI bullet and numbered lists use a marker column rather than paragraph bullet indents. LAVI sign-off defaults to equal Prepared By / Conforme columns; the right column contains Authorized name, Signature and Date fields.

The Lifes Awesome profile is unchanged from 2.1.0 / `LIFES-AWESOME-QUOTATION-2026.3`; do not apply the new LAVI sizes to it. Existing delivered PDFs are not changed in bulk. Migrate structured LAVI jobs by explicitly updating their template ID and preserve their commercial/source data. Run lock verification, all tests, arithmetic/content checks and page-by-page render inspection.


## LAVI spatial rhythm refinement — 26 September 2026

Engine **2.3.0** / **LAVI-QUOTATION-2026.9** keeps the approved 16 / 11 / 10 / 9.5 / 9 pt hierarchy but corrects layout density. LAVI uses roomier table cells, 9 pt section breathing before headings, 6 pt after headings, increased BOQ subsection spacing, marker-rail lists with 1.5 pt top / 3 pt bottom row padding, and standardized 34% / 66% two-column terms/warranty/payment tables.

The first-page Prepared For / Quote Details area uses paired tinted key/value cards with a 12 pt gutter. The Prepared By / Conforme sign-off remains equal-width with 18 pt gutter and 14 pt inner padding, but grows to a 148 pt signing block with a 12 pt approach gap and 32 pt Conforme field rhythm. These are reusable template rules, not one-off HDU patches. Lifes Awesome remains unchanged.
