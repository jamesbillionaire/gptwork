# Latest Agent Handoff

Handoff version: 0014
Last updated: 2026-09-22
Status: Readable quotation standard completed and verified locally and on staging CI; promoted as engine 2.1.0. Philpost V5 ready for James's review. No unobserved main workflow result is claimed.

## User instruction and authoritative source
James reported that some quotation fonts are too small and requested a standardized minimum. This is a typography revision only. Latest source: uploaded LAVI_Philpost_Structured_Cabling_Quotation_v4(1).pdf, SHA256 f0f3157c47b74507b29347ec50e3862073defc4341d536c3235d19f70acd5fe5.

IMPORTANT: The uploaded copy removes the front Attention entry and changes the body validity clause to 45 days while retaining 15 days in the quote-details card. Both source values are preserved and the inconsistency disclosed to James. Do not restore Mr. James in the blank metadata or silently select a validity term from an older JSON. Salutation remains Dear Sir James.

## Reusable minimum typography
Engine 2.1.0; LAVI-QUOTATION-2026.6; LIFES-AWESOME-QUOTATION-2026.3. Absolute minimum 10pt live text, including tables, prices, notes, diagrams, contact information, running headers, footers and page numbers. Body 11/15pt; section 13/17pt; subsection 11/14pt; titles 20pt. Brand font families/colors, supplied logos, Legal paper and horizontal rails retained. Headers/footers wrap using measured heights. Diagram labels wrap with measured rows and gap-only connectors. Narrow table columns accommodate labels without shrinking. See quotation_engine/reference/readability_standard.md.

Continuous Philpost flow and 14pt-padded/18pt-gutter sign-off retained. Never shrink text to force a historical page count. Source commercial data and existing delivered PDFs are not modified in bulk. No raw font files or copied signatures are committed.

## Prepared conversation attachments
LAVI_Philpost_Structured_Cabling_Quotation_v5_Readable.pdf and companion .json, .md, .audit.json. Three Legal pages. PDF SHA256 0b7acebe329c2a426cce9bb74e9145cc837fef88d9edbbf657deec5e3bb2b25b. JSON SHA256 77a79b816cb665175a49219858ab8bf1fc38fb4290fbeb9553c29e83a0e12a6b. Retrieve actual attachments in a fresh session; filenames do not establish sandbox paths.

All 20 original priced rows and PHP299308.80 VAT-inclusive total remain unchanged. Date 16 September 2026, payment, duration, warranties and scope clarifications retained. Preparer Ms. Lea C. Ruiles / Admin. Source validity inconsistency remains unresolved.

## Verification and release evidence
All 24 tests passed locally. The same source passed GitHub Actions run 35683436838. Tested source commit b96fdcfb283f822691ed9a259face9e58b8140aa; prior main 6ae347feac564706083d7fb34b041c13a155f82e. Four complete fixture PDFs rendered (8/8/13/11 pages); all pages scanned for minimum font size, text rails and overlap. The final Philpost PDF was rendered with Poppler and all three pages individually inspected; full normalized source word counts match except repeated headers/footers/table headings. All financial values verified. Production checksum lock passed; no bypass.

See .agents/handoffs/2026-09-22-readability-verification.json. Promotion uses a clean tree with no temporary installer/workflow/transport. Regular main CI remains enabled. Verification is evidence of the rendered layout, not client acceptance.

## Next agent
Use the V5 JSON with the current template ID; preserve the latest uploaded-source edits. Any later validity correction requires user direction. Migrate old structured jobs explicitly to the new profile IDs without silently changing their commercial content. Re-render and inspect the actual final PDF for every job. Other CPSC/Philpost source quantities and private cost models remain untouched.

## Prior work
The actual prior CPSC Project 4 brand-neutral handoff is archived at .agents/handoffs/2026-09-22-before-readability-standard.md. Project 4, other CPSC quotes, Wonderzone and Phoenix are not commercially revised by this release. No background work is scheduled.
