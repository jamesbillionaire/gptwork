# Quotation typography and readability standard

Authority: James requested a standardized minimum font size on 22 September 2026 after client feedback on the supplied Philpost V4 quotation. This supersedes the previous small-font values for future LAVI and Lifes Awesome quotation rendering, not their approved source content or brand identities.

Engine 2.1.0. Active profiles: LAVI-QUOTATION-2026.6 and LIFES-AWESOME-QUOTATION-2026.3.

| Role | Font size | Leading |
|---|---:|---:|
| Body paragraphs, conditions, scope clarifications and signer identity | 11 pt | 15 pt |
| BOQ descriptions, quantities, units, monetary values and general tables | 10 pt | 13 pt |
| Notes, client/quote metadata, contact information and diagram text | 10 pt minimum | 12-13 pt or more |
| Table column headings, labels, running headers and footers | 10 pt minimum | 12-13 pt |
| Section headings | 13 pt | 17 pt |
| Subheadings | 11 pt | 14 pt |
| Document title | 20 pt | 24 pt LAVI / 25 pt Lifes Awesome |

No live text may be below 10 points. This includes disclaimers, conditions, diagram captions, page numbers and company contact details. The supplied logo is artwork and must not be regenerated. No raw font files are distributed.

Keep Legal 612 x 1008 pt paper, the separate brand font families and colors, original logos, margins/content rails, justified narrative, centered quantity/unit columns, right-aligned currency and the padded LAVI sign-off. Readability takes priority over fitting a historic page count. Never shrink fonts or horizontally scale text to avoid wrapping. Headers and footers are measured; diagrams wrap with measured row heights and constant connector gaps. Unit/quantity columns are wider so labels and four-digit quantities remain legible.

The first-page boundary remains explicitly selectable. For an approved continuous-flow job, keep front_page_break=false. Headings stay with meaningful opening content rather than holding entire multirow tables on the next page. Tables repeat their headers; subtotal/last-item and total-price blocks remain protected. Sign-off remains one intact component with 14pt padding and an 18pt gutter.

Layout-only work must use the latest supplied PDF as the content authority, not blindly re-use an earlier JSON. Preserve user edits, rates, quantities and wording; disclose contradictory source terms without choosing or reconciling them silently. The Philpost copy supplied for this change has a blank attention cell and a 45-day body validity clause while its quote-details card still says 15 days. That discrepancy is unresolved, not permission to change the commercial agreement.

Migration of existing structured jobs requires explicit active template-ID updates. Existing delivered PDFs are not modified in bulk. Historical example content stays unchanged; regression page counts are observations, never pagination targets.

Validation: run verify-lock, all tests, render the exact client PDF and inspect every final page. A font-span audit must find no live text below 10pt. Reconcile content and all financial values with the current source. Keep sources and document-specific audits as conversation attachments rather than publishing private client or internal costing records.
