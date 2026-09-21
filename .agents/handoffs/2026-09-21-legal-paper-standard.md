# Both quotation brands: Legal paper

## Authority and scope
James explicitly instructed: "Both template should use legal size paper format." This supersedes the prior LAVI A4 profile. Both active profiles now require Legal 8.5 x 14 inches / 612 x 1008 points. Other brand typography, side margins, colors, logos and client data are preserved. Existing delivered/signed source PDFs are not overwritten.

## Release
- Engine: 2.0.1.
- LAVI: LAVI-QUOTATION-2026.4; Legal, 15 mm margins.
- Lifes Awesome: LIFES-AWESOME-QUOTATION-2026.2; existing Legal, 32 pt margins unchanged.
- Base main: dbc277176388e45cfddbbfe8e1a26665e9f65838.
- Tested staging source: 9600a3809a881ae31478383a8b82bb7ccbb6e6e3.
- CI: https://github.com/jamesbillionaire/gptwork/actions/runs/35562513384 (success).
- Downloaded verification artifact SHA-256: 3b62f7afceef528ccaec82a07e9b8782c07e19d8eb1dab53df3c777abd2f1ccb.

## Checks completed before promotion
13 tests passed locally and in CI. All four full fixtures were generated and all 25 pages rendered with Poppler. All 10 changed LAVI pages were inspected at readable resolution; diagrams, tables, hanging lists, totals, continuation headers and footers remained within their content rails without clipping or connector/text collisions. First-page executive-summary whitespace remains the approved section boundary, not forced filler.

LAVI fixtures naturally repaginate from 6 to 5 pages each. Lifes Awesome fixtures remain 8 and 7 pages and are byte-identical to the corresponding pre-correction engine renders. Every current fixture page is 612 x 1008 pt. The separate layout_contract.json records current pagination without rewriting historical source page counts or fingerprints.

The paper change exposed a footer assumption based on page height. Page-number baseline is now selected by brand, matching each existing footer; a regression checks it on every fixture page. The existing shared renderer and diagram component are reused, not replaced with another one-off engine.

Manifest hashes, editor schema, LAVI fixture template IDs and active instructions were refreshed. Temporary release transport/workflow is excluded from the main release; ordinary quotation CI remains unchanged. No pricing, dates, quantities, warranty, support or scope changes were made.
