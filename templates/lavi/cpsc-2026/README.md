# LAVI Technologies — APPROVED_LOCKED

Template: **LAVI-QUOTATION-2026.10**. Source family remains the CPSC Project 1 final diagram-corrected PDF and Project 2 V2 Corrected PDF. James authorized this template revision on **26 September 2026** to correct typography balance, list alignment, table-column alignment, component spacing, opening summary cards and the LAVI sign-off. Use `quotation_engine/cli.py`; do not create a separate renderer.

## Exact brand contract

- Legal: 612 x 1008 pt (8.5 x 14 inches); 15 mm (42.519685 pt) side margins; full content rail 526.96063 pt.
- Liberation Sans. Main title **16/19.2 pt**; section headings **11/13.5 pt**; subheadings **10/12.4 pt**; body and notes **9.5/12.5 pt**; BOQ/general table text **9/11.4 pt**.
- Metadata/labels are **9.5 pt**; table headers **9 pt**. The first-page top-right `LAVI TECHNOLOGIES INC.` heading is **9 pt**. Business address/contact lines, continuation quotation furniture, footer and page number are **8 pt**. Diagram text is **9 pt**. The 8 pt size is furniture/contact use, not a body-text fit knob.
- Accent #0AA7AE; headings #078A91; title/deep navy #1C3159; table header #243F73; ink #26313D; muted #65717E; grid #D7E0E6; zebra #F5F8FA; pale teal #EAF7F8; pale navy #EEF2F8; total #FFF5DA.
- BOQ proportions stay 6% QTY, 10% UNIT, 49% DESCRIPTION, 17.5% UNIT PRICE, 17.5% AMOUNT. QTY/UNIT centered; description left; currency right. General tables may declare left/center/right per-column alignment; LAVI rows are vertically centered.
- LAVI bullet and numbered lists use a dedicated marker rail. Wrapped lines align exactly with the first text line; markers do not create a second nested indent.
- Supplied `logo.png` is the original official asset. It appears on page 1 only and is not regenerated.
- Use one full-width rail for headings, tables, cards, rules, totals and diagrams. No extra horizontal canvas inset.
- LAVI defaults to a two-column sign-off: **Prepared By** left and **Conforme** right, equal panels, 18 pt gutter and 14 pt internal padding. Conforme provides Authorized name, Signature and Date lines. No signature image is embedded.

## Flow and pagination

`front_page_break: false` may be used when the executive summary should flow directly into Section 1. Content determines page count; do not shrink type to imitate a previous page count. Keep headings with meaningful following content, repeat BOQ headers, protect subtotal/total rows and keep the two-column sign-off intact.

## Commercial integrity

CPSC examples are historical source fixtures. Their dates, prices, terms, quantities and signatory roles are job data, not defaults. Never copy a signature from a signed source. Layout-only edits preserve all approved content and arithmetic.

## Verification

Run `verify-lock`, all quotation-engine tests, render the exact client PDF, check arithmetic/content preservation and inspect every page. Lifes Awesome is a separate template and is not changed by this LAVI revision.


## Spatial rhythm refinement — 26 September 2026

Engine **2.3.0** keeps the approved LAVI type hierarchy while improving layout density: 4.5 pt table cell padding, 9/6 pt section approach/exit spacing, 7/4 pt BOQ subsection spacing, marker-rail list breathing, standardized 34/66 two-column terms tables, balanced Prepared For / Quote Details cards, and a taller 148 pt Prepared By / Conforme sign-off. Short two-column tables stay with their heading when the complete block fits on one page.

Lifes Awesome remains visually unchanged. Existing LAVI jobs require an explicit template-ID migration to 2026.9 while preserving commercial data.


## LAVI list/signature alignment correction — 26 September 2026

Engine **2.3.1** / **LAVI-QUOTATION-2026.10** keeps the approved 2026.9 typography, card geometry, table widths and spacing. Bullet and numbered markers now use a dedicated marker flowable whose baseline is mathematically tied to the first text-line baseline, so markers stay vertically aligned even when an item wraps. The Prepared By / Conforme box size is unchanged; only the Prepared By signature line is repositioned to sit directly above the printed preparer name instead of floating near the middle of the panel.
