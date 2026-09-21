---
name: lavi-quotation
description: Create or revise LAVI Technologies quotations with the approved CPSC infrastructure design, source-grounded data and rendered QA.
---
Read `AGENTS.md`, `LATEST.md`, `quotation_engine/manifest.json`, `quotation_engine/README.md`, then `templates/lavi/cpsc-2026/README.md`.

Use `LAVI-QUOTATION-2026.3`, brand `lavi`. Start a blank structured job with `python -m quotation_engine.cli new --brand lavi --output work/job.json`; consult `examples/cpsc-01.json` or `examples/cpsc-02.json` for component patterns, not reusable commercial values. Do not select the Lifes Awesome or archived Legal-size LAVI template.

Preserve approved quantities, prices, date, recipient, warranty, tax and preparer. No raw font files or copied signature. Use the official logo, same content rail, justified body, centered QTY/UNIT, right-aligned prices, hanging lists, repeated table headers and shared diagram component. Later pages never repeat the logo. Render with the CLI, run tests, and inspect every final page including the architecture at readable scale.

Return the PDF and a short change summary; update LATEST.md. Style/engine changes require James's explicit authorization, new version IDs, hashes, fixtures and QA. Do not write a one-off quotation renderer.
