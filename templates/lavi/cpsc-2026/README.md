# LAVI Technologies — APPROVED_LOCKED

Template: **LAVI-QUOTATION-2026.5**. Source family: CPSC Project 1 final diagram-corrected PDF and Project 2 V2 Corrected PDF. Use `quotation_engine/cli.py`, never this README as permission to write a new renderer.

## Exact brand contract

- Legal: 612 x 1008 pt (8.5 x 14 inches); 15 mm (42.519685 pt) left/right margins; content width 526.96063 pt.
- Liberation Sans Regular/Bold/Italic. Body 8.1/11.2 pt; BOQ 6.5/8.1; explanatory note 7.1/9.3; section 10.2/12; subsection 8.2/10.2; project title 18.5/20.5. Numbers denote font size / line height.
- Accent #0AA7AE; headings #078A91; title/deep navy #1C3159; table header #243F73; ink #26313D; muted #65717E; grid #D7E0E6; zebra #F5F8FA; pale teal #EAF7F8; pale navy #EEF2F8; total #FFF5DA.
- Line-item proportions: 5.5% QTY, 7% UNIT, 52% DESCRIPTION, 17.5% UNIT PRICE, 18% AMOUNT. Outer width exactly equals content width. QTY/UNIT centered, descriptions left, amounts right.
- Supplied `logo.png` is the original official asset, copied by hash, not recreated. First-page logo is approximately 104.88 pt wide at the left rail. Business details are small live text aligned right. No logo on continuation pages.
- One first-page overview: unboxed title, two-column client/quote card, introduction, optional metric strip, commercial summary. Subsequent content flows naturally.
- Use full-rail price callout, restrained teal section rules, proper hanging lists, no extra horizontal inset. Preserve whitespace inside cards, not an extra inset around whole components.
- Caption and each architecture row have dedicated clearance. Split/merge arrows stay in the row gaps. Do not embed a PNG screenshot of a diagram as the editable production component.

LAVI CPSC examples are dated 18 September 2026, valid 30 days, and prepared by James Brown Bete / CEO. These are **job-specific**, not engine defaults. Historical unit prices and provisional quantities are not verified current market data. Never copy the signed source's signature to a new quotation.

## Authorized continuous flow and sign-off correction (22 September 2026)

Engine 2.0.2 / LAVI-QUOTATION-2026.5 adds two explicit job controls. For the Philpost revision, use `front_page_break: false` and `signature_mode: "two_column_prepared_conforme"`. These are reusable renderer capabilities, not a one-off PDF overlay. No forced blank remainder is left after the Project Boundary card: Section 1 follows in the same content flow, with normal heading/table keep rules. The continuous mode uses 3.2-point vertical table padding; font sizes, line heights, rails, colors, logos and all horizontal table padding remain unchanged.

The two-column sign-off is a single unbroken component with equal white panels, a clear 18-point gutter, 14-point interior padding, dedicated signing space above the preparer, and separate writable Authorized name / Signature / Date fields. It does not inherit the generic table grid or zebra shading. Do not remove this padding or reproduce underscore-based field widths. `conforme_fields` may supply short explicit field labels; blank signers stay blank.

Defaults for other jobs remain the existing first-page boundary and prepared-only block. Do not silently change previous quotations or Lifes Awesome styling. Historical LAVI job data using 2026.4 can be migrated by changing only the template ID to 2026.5; only select the new controls when requested. CPSC fixture IDs changed as release metadata; their commercial content and default rendered PDFs are preserved. The editor schema's missing closing brace was also repaired and is covered by a JSON-parse test.
