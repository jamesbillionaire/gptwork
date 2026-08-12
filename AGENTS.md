# LAVI PDF Work Standards

## Authority and scope

This file is the repository-wide operating standard for agents creating, revising, reviewing, or finalizing LAVI Technologies PDF quotations, proposals, BOQs, reports, and similar client documents.

- Read this file completely before touching a PDF-related artifact.
- A direct instruction from James for the current task overrides this file.
- Preserve approved commercial data and client decisions unless James explicitly authorizes a change.
- Treat an approved LAVI document as the visual and editorial reference for the whole quotation family. Consistency means the same design system, terminology, and hierarchy. It does **not** mean forcing every document to have the same page count or page breaks.

## Non-negotiable document rules

1. Use **Legal / long bond paper: 8.5 x 14 inches (612 x 1008 points)** unless the client explicitly requires another size.
2. Use **content-driven pagination**. Never reserve pages manually, stop a table early, or force a section to a new page merely to imitate another quotation's page count.
3. Do not hide poor pagination by enlarging table rows, inserting large spacers, shrinking body text, or compressing commercial conditions.
4. Every non-final page must use its available body area sensibly. A large empty lower third on a non-final page is a defect unless the next indivisible element genuinely cannot fit.
5. A final signed page may have natural whitespace after the signature. A page containing only a signature block is normally a defect; rebalance the preceding flow so meaningful content accompanies it.
6. Keep table rows intact. A table may continue to the next page, but an individual row must not split across pages.
7. Repeat the table header on every continuation page.
8. Never leave a section heading orphaned at the bottom of a page. Let the heading flow with meaningful content that follows it.
9. Page numbering must be calculated after pagination and must show the correct `Page x of y` value.
10. Do not deliver a PDF until every final page has been rendered and visually inspected.

## Approved visual system

Use the approved LAVI Xavier University quotation family as the baseline:

- LAVI letterhead and contact block on Page 1.
- Formal quotation title and descriptive project subtitle.
- Client/project/reference/date/quotation-reference metadata table.
- Recipient block and short formal introduction.
- Teal section headings, teal table headers, restrained zebra rows, thin grid lines, and a highlighted grand-total row.
- Compact continuation header on later pages.
- Footer with LAVI/project label and accurate page numbering.
- Signature block after the final callout or closing condition.

Maintain the typography, colors, margins, table widths, alignment, and information hierarchy of the approved template. Do not redesign the visual language for each building.

## Standard section hierarchy

Conventional FDAS quotations should normally use this order and wording:

1. `A. VERIFIED PROJECT QUANTITY SCHEDULE`
2. `B. DAHUA CONVENTIONAL FDAS EQUIPMENT`
3. `C. WIRING, CONTAINMENT AND INSTALLATION MATERIALS`
4. `D. INSTALLATION, TESTING AND PROFESSIONAL SERVICES`
5. `E. TOTAL PROJECT COST SUMMARY`
6. `F. COMMERCIAL AND TECHNICAL CONDITIONS`

Addressable FDAS quotations should follow the same editorial logic, with system-specific section names only where needed.

Do not invent different section names for equivalent scopes. Building-specific differences belong inside the scope, quantities, descriptions, and conditions—not in unnecessary changes to the document structure.

## Content-driven pagination standard

Use a flow layout engine such as ReportLab Platypus rather than drawing all body content at fixed coordinates.

Recommended implementation:

- `BaseDocTemplate`, `PageTemplate`, and `Frame` for document flow.
- A first-page template for the letterhead and a continuation template for later pages.
- `Table(..., repeatRows=1, splitByRow=1, splitInRow=0)` for tables.
- `KeepTogether` only for small elements that must remain together, such as a numbered condition paragraph or a signature block. Never wrap a whole section or long table in `KeepTogether`.
- Modest `spaceBefore` and `spaceAfter` values for section rhythm.
- A numbered canvas or equivalent second pass for accurate total page counts.

Pagination behavior:

- Continue the next section on the current page whenever it fits cleanly.
- If a table reaches the page limit, continue it on the next page with the header repeated.
- A table may begin near the bottom if the heading plus header plus at least one full data row fits.
- If only a heading or table header fits, move that small group to the next page.
- Do not create a manual page break simply because a reference document placed that section on another page.
- Do not force Faber, Junior, Grade School, Sports Gym, Senior High, or other building quotations to have identical page counts.

## Spacing and readability

- Body text should remain comfortably readable; do not shrink it merely to reduce page count.
- Commercial conditions should generally use approximately 8 pt text with about 10–10.5 pt leading, adjusted only within the approved visual system.
- Leave visible separation between numbered conditions, normally about 6–10 points. More spacing is acceptable when it produces a balanced page; dense wall-of-text conditions are not.
- Use normal compact table padding. Do not inflate rows to fill a page.
- Use whitespace intentionally between logical sections, not as a substitute for proper flow.
- Inspect actual rendered pages. Text extraction alone cannot validate spacing.

## Editorial consistency

Documents for the same kind of project must read as one coordinated quotation set.

Standardize:

- Project-title formula.
- Proposal introduction structure.
- Section names and sequence.
- Device naming and capitalization.
- Materials descriptions.
- Labor, testing, turnover, and documentation descriptions.
- Commercial-condition headings and order.
- Currency, VAT, subtotal, and grand-total labels.
- Warranty and variation language.

Only the following should normally vary by building:

- Building name and location.
- Assessment source and revision reference.
- Quantities and floor/area distribution.
- Retained versus replacement system configuration.
- Equipment, materials, labor, implementation duration, and pricing justified by the actual scope.
- Conditions that are genuinely specific to the building.

Avoid unnecessary synonyms. If two quotations supply the same Dahua conventional smoke detector, use the same description formula in both.

## Technical and commercial writing rules

Commercial conditions are not boilerplate filler. Review each condition against the quoted scope.

Required principles:

- Do not promise tests, replacements, equipment, access systems, or regulatory outcomes that are not included.
- Do not add a standalone condition merely to state that an unrelated component is excluded.
- Avoid contradictory wording such as excluding battery work while promising detailed battery-capacity, charger, mains-failure, or standby-condition testing that is not part of the priced scope.
- For retained-panel rehabilitation, limit testing language to the affected devices, zones, circuits, and functions actually included.
- Include standby-power language when a new panel/battery set is supplied or when battery testing is explicitly part of the scope.
- Include auxiliary power supplies only when a manufacturer-based load calculation proves they are required.
- Distinguish retained equipment from new supplied equipment in warranty language.
- State that regulatory inspection assistance is included when applicable, but never guarantee approval.
- Use variations for discoveries outside the assessed quantities or provisional material allowances.
- High-level fixed scaffolding or powered access equipment must not be included by habit. Include or exclude it based on actual site need.
- Reserve cable and containment must be technically justified and clearly described as a provisional allowance where appropriate.

Recommended commercial-condition order:

1. Payment Terms
2. Implementation Period
3. Scope Basis
4. System Configuration or Existing Panel Retention
5. Dahua Equipment/Device Compatibility
6. Existing Wiring and Pathways
7. Notification, Manual Stations, Alarm-Bell Circuit, or Unlisted Devices—as applicable
8. Standby Power only when relevant; otherwise proceed directly to Warranty
9. Warranty
10. Exclusions and Variations
11. Testing and Commissioning/Recommissioning
12. Documentation and Turnover
13. Validity

Renumber naturally when an irrelevant condition is omitted. The goal is relevance and clarity, not a fixed count.

## Xavier University quotation-set decisions

Unless James gives a newer instruction for the specific quotation:

- The brand for the current Xavier University quotation set is **Dahua**.
- Use the signed inspection/assessment report as the primary quantity source.
- Handwritten notes or later quantity annotations are included only when James explicitly authorizes them for that building.
- Junior Building uses the original signed assessment count only: 75 conventional smoke detectors across four floors; handwritten additions, Fifth Floor devices, and sounder lights are excluded.
- Faber and Junior retain their existing conventional FACPs where serviceable; do not include new panels unless authorized.
- Grade School is a replacement/conversion conventional system and includes a new FACP and battery set as approved.
- Sports Gym installation is straightforward: no scaffolding allowance unless later site facts require it; include only a reasonable reserve-cabling allowance.
- Labor and installation materials must reflect the actual building complexity, access, existing wiring condition, and scope—not a copied percentage from another building.

Current addressable selling-price references, until superseded by James:

- Smoke detector: `P 1,650.00`
- Manual call point: `P 1,600.00`
- Sounder-strobe: `P 1,850.00`
- Repeater: `P 8,700.00`
- Isolator: `P 3,200.00`
- One-loop panel: `P 42,000.00`
- Two-loop panel: `P 68,000.00`

Battery wording for a compatible addressable panel must be unambiguous: **one battery set consisting of two 12 V batteries**, with ampere-hour capacity stated or made subject to the approved load calculation. Do not use `2 sets` when the intent is two individual batteries.

## Scope and pricing integrity

- Never change approved quantities, unit prices, labor, subtotals, VAT, or totals during a layout-only revision.
- Recalculate all arithmetic after any authorized commercial change.
- Use 12% VAT when the quotation is VAT inclusive, and verify:
  - Category subtotals.
  - VAT-exclusive subtotal.
  - 12% VAT.
  - VAT-inclusive grand total.
- Currency formatting must be consistent throughout one quotation. For the current template, table values use formats such as `P 1,550.00`.
- Match the filename revision, internal quotation-reference revision, and PDF metadata revision.
- Never silently carry a stale revision number from an earlier PDF.

## Source grounding and safe editing

Before editing:

1. Identify the approved layout reference.
2. Extract text from every relevant source PDF.
3. Render the source pages to images and inspect the real layout.
4. Record the authoritative quantities, prices, totals, exclusions, and user-approved corrections.
5. Preserve the source files and write a new revision unless James explicitly requests replacement in place.

Do not flatten, alter, or overwrite a signed source PDF. Treat signed documents as evidence/reference artifacts unless James explicitly authorizes a signed-document workflow.

## Mandatory PDF QA

Every final PDF must pass both content and visual checks.

### Content checks

- Correct client, building, location, date, and reference.
- Correct filename and matching internal revision.
- Correct scope quantities and floor/area allocation.
- Correct Dahua/system type descriptions.
- Correct category totals, VAT, and grand total.
- No unauthorized handwritten-note quantities.
- No irrelevant or contradictory commercial condition.
- No stale project name, page label, footer, or continuation header copied from another building.

### Visual checks

Render **every page** to PNG and inspect it at readable resolution.

Confirm:

- Legal page size is 612 x 1008 points.
- No clipped, overlapping, missing, or off-page text.
- No broken glyphs, black squares, or corrupted images.
- No split table row.
- Continuation pages repeat table headers.
- Section headings are not orphaned.
- Non-final pages do not have unexplained large empty lower areas.
- Commercial conditions have clear spacing and are not compressed.
- Signature and footer are fully visible.
- Page numbering is correct.
- The final page looks intentional even when it contains natural whitespace.

Use `pdfinfo`, `pdftotext`/`pdfplumber`, and Poppler rendering (`pdftoppm`) or equivalent tools. Do not approve a PDF based only on code execution or extracted text.

## Delivery and versioning

- Store final local PDFs under `output/pdf/` when working in a local workspace.
- Use stable, descriptive filenames with explicit building and revision.
- Preserve prior revisions unless James asks to remove them.
- When replacing a persistent file, preserve its file identity/version history when the platform supports it.
- Deliver the final PDF with a concise summary of material changes, page count, and confirmation that scope/pricing were or were not changed.
- Do not call a PDF `FINAL` until it has passed the complete QA checklist and James has accepted the content.

## Final agent checklist

Before handing off any quotation, answer all of these with **yes**:

- Did I use Legal 8.5 x 14 paper?
- Did content flow naturally without manual page-count imitation?
- Did every non-final page use available space sensibly?
- Are table rows intact and continuation headers repeated?
- Are descriptions consistent with the quotation family?
- Is every commercial condition relevant to this building?
- Did I preserve or explicitly authorize every quantity and price change?
- Do the filename, internal reference, and PDF metadata revisions match?
- Did I verify arithmetic and VAT?
- Did I render and inspect every page?
- Is the delivered file the exact version I reviewed?

If any answer is no, the PDF is not ready for delivery.
