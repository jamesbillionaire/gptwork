# CPSC approved quotation template promotion

## User authorization

James asked to replace the gptwork quotation engine with the approved LAVI Technologies and Lifes Awesome Ventures templates from Projects 1, 2, 5 and 8, including approved styles, typography and easy reuse by a fresh GPT agent.

## Base repository

jamesbillionaire/gptwork, main at 9516c0a9ad993fdd0d07e6be8c97b618df8d8df9. The previous root AGENTS.md, LATEST.md and entire quotation_engine tree are retained under legacy/ and the handoff archive. Billing and unrelated project/work files are not modified.

## Source authority

- LAVI_CPSC_Project_1_Integrated_Campus_Network_Quotation_Diagram_Corrected.pdf
- LAVI_CPSC_Project_2_Integrated_Campus_Security_CCTV_Quotation_v2_Corrected.pdf
- Lifes_Awesome_CPSC_Project_5_Unified_College_Information_Management_System_Quotation_v2.pdf
- Lifes_Awesome_CPSC_Project_8_Legal_Services_Case_Query_Document_Management_Quotation_v1.pdf

Source fingerprints are in quotation_engine/reference/sources.json. Actual PDFs were inspected for page size, fonts, colors, component boundaries and commercial data. The supplied logos match existing repository blobs byte-for-byte: LAVI 54c73083c3bd35a5cd2c63571827e5bfa4cf062a; Lifes Awesome 26ac8afd20cdd98eae75803025e7f6bf2a3b0583. No raw fonts or reusable signature were added.

## New production path

Engine 2.0.0; LAVI-QUOTATION-2026.3 and LIFES-AWESOME-QUOTATION-2026.2. A shared data-driven renderer with genuinely separate brand profiles replaces per-quotation scripts. A4 vs Legal, Liberation Sans vs DejaVu Sans, different header/title/table styling, fonts, colors, exact content rails and aligned numeric/list columns are preserved. Diagrams calculate row positions and gap-only split/merge connectors.

New agents use AGENTS.md -> LATEST.md -> quotation_engine/README.md -> manifest/profile -> structured job. The blank-job command cannot inherit old CPSC client names, prices or terms. The examples are historical data with source totals 17,886,000 / 7,353,000 / 26,841,000 / 6,368,000 PHP inclusive. Migration and cloud-hosting decisions are documented as provisional/subject to approval, not invented client requirements.

## QA

Local tests and CI gates validate arithmetic, no implicit VAT, brand selection, missing data, no signatures, supplied logo hashes, source vocabulary preservation, correct page sizes, content-rail text bounds, continuation-page image absence and all connector geometry. Fixture outputs have 6 / 6 / 8 / 7 pages without forcing page counts. Rendered contact sheets and readable page/diagram inspections were used to review the generated family. The exact CI run and final commit provide remote verification evidence.

Full golden PDFs and page previews are generated as workflow artifacts; source-derived approved header/architecture SVG crops are committed. These are not advertised as byte-identical copies of original signed PDFs. Source documents and commercial decisions are not overwritten by the template promotion.

## Continue

No pending client quotation edit. For a new quotation use the active profile, populate verified job data and perform complete rendered QA. Do not treat the previous SFDHMC handoff as the current active work; it remains archived, not declared completed here.
