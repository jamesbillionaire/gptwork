# Approved source evidence

`sources.json` identifies the four latest approved source PDFs by exact filename and SHA-256, with source page counts. They are not the earlier CCTV Final/Final2 files with overlapping architecture boxes.

`previews/` contains source-derived SVG crops of each approved first-page header and final architecture diagram. Geometry and text were extracted from the actual PDFs, not redrawn from memory. Coordinates are rounded to hundredths of a point. Logos link to the original supplied PNG assets, and text uses the installed approved font family. Open these from the checked-out repository so relative logo paths resolve.

No signed page/signature artwork is included. These crops demonstrate approved style; they are not full quotations or new signing authorizations.

`word_contract.json` is a source-derived vocabulary guard used alongside full editable example jobs. It catches dropped scope terminology in generated regression PDFs. It is not a replacement for comparing every number, name, paragraph and approved commercial condition during a client revision.

Full engine regression PDFs can be regenerated with `python -m quotation_engine.cli render-examples --output output/golden`. Their pagination is content-driven and their bytes need not equal the original edited/signed source PDFs. The source-derived fixtures preserve all priced items, totals, quote dates and principal source terms.

## Legal-paper correction, 21 September 2026

Original source fingerprints, source page counts and approved style crops are retained as historical evidence. Both active production profiles now use Legal 612 x 1008 pt. Do not infer production paper size from an older LAVI source crop. `layout_contract.json` records the revised rendered fixture sizes/page counts; regeneration and review must use the active profiles.
