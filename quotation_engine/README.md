# Approved quotation engine — CPSC reference release 2.0.2

**Start with AGENTS.md and LATEST.md.** James approved these two separate profiles, based on the final CPSC Projects 1, 2, 5 and 8 quotation family. Old Xavier quotation styling and the previous Lifes Awesome candidate no longer drive new quotation production.

## Which profile?

- `lavi`: `LAVI-QUOTATION-2026.5`; Legal 612 x 1008 pt, Liberation Sans, teal/navy, left-aligned first-page logo and right-aligned live contact block. Detailed infrastructure/equipment BOQs. See `templates/lavi/cpsc-2026/README.md`.
- `lifes-awesome`: `LIFES-AWESOME-QUOTATION-2026.2`; Legal, DejaVu Sans, cyan/gray, centered first-page logo and compact contact lines, tinted title band. Software deliverable/fee tables. See `templates/lifes-awesome/cpsc-2026/README.md`.

The engine keeps brand styles separate while sharing validation, arithmetic, section flow, tables, list indents, calculated page numbers and safe diagram geometry. It does not use a project-specific generator script.

## Install and run

Python 3.11 or newer. Install requirements from repository root. On Debian/Ubuntu install `fonts-liberation`, `fonts-dejavu-core`, and `poppler-utils`. On other systems install the same font families and set `QUOTATION_FONT_DIR` to their local directory. Font files are not included; a missing family is a hard error, never a silent fallback.

```sh
python -m pip install -r requirements.txt
python -m quotation_engine.cli verify-lock
python -m quotation_engine.cli profiles
python -m quotation_engine.cli new --brand lifes-awesome --output work/client-project.json
```

The new file intentionally has blank client, date, validity, tax, signatory and commercial values. Supply the approved data, then:

```sh
python -m quotation_engine.cli validate work/client-project.json
python -m quotation_engine.cli render work/client-project.json --output output/pdf/client-project_v1.pdf
pdftoppm -png -r 150 output/pdf/client-project_v1.pdf output/pdf/client-project_v1
python -m unittest discover -s quotation_engine/tests -v
```

Inspect every final page. Render creates an `.audit.json` with source-job and PDF hashes and `visual_review: REQUIRED_BEFORE_DELIVERY`; automated tests do not replace that review. Existing PDF output is not overwritten unless `--overwrite` is explicit.

## Reuse a relevant reference

```sh
python -m quotation_engine.cli render-examples --output output/golden
```

| Example | Approved source | Total (PHP, inclusive) | Source pages |
|---|---|---:|---:|
| `examples/cpsc-01.json` | Project 1, Diagram Corrected | 17,886,000 | 6 |
| `examples/cpsc-02.json` | Project 2 V2 Corrected, not Final2 | 7,353,000 | 6 |
| `examples/cpsc-05.json` | Project 5 V2, 18-month implementation | 26,841,000 | 8 |
| `examples/cpsc-08.json` | Project 8 V1 | 6,368,000 | 7 |

Source filenames and original SHA-256 fingerprints are in `reference/sources.json`. These snapshots preserve approved source commercial data; they are **not current vendor costs or default terms**. The Project 1 source includes a signed page, but no signature is included in any reusable fixture or output. The quote reference's `20260921` and stated date `18 September 2026` are retained as supplied, not silently reconciled.

`reference/previews/` contains measured SVG crops of the approved headers and final architecture diagrams. They retain source text/geometry and reference the supplied logo assets; fonts must be available locally. They are style evidence, not generators or signable quotations. Full PDF files in `output/golden/` are regenerated engine regression outputs, not byte-identical copies of the historical source PDFs.

## Job format

`schema.json` provides editor guidance; `validation.py` adds semantic and arithmetic checks. Choose a `brand` and matching `template_id`. Money and quantity use decimal strings. Each BOQ item carries `qty`, `unit`, `description`, `unit_price`, and optional independently checked `amount`. `expected_total` acts as an independent guard. All summaries and section totals are calculated from the line items.

The linear `blocks` array supports:

- `heading`, `paragraph`, `note`, `callout`: text and restrained inline `<b>` emphasis / `<br/>` where meaningful.
- `boq`: title, priced items, checked subtotal, optional explanatory note.
- `table`: rows, fractional widths summing to one, optional header. No ad-hoc physical widths.
- `list`: items, optional numbered/start; the engine supplies hanging indents.
- `diagram`: caption and semantic rows/nodes; the shared component computes positions and connectors.
- `total`: the calculated contract-price display.
- `page_break`: use only for an intentional approved document boundary, never page-count imitation.

`introduction`, optional `metrics`, `boundary` and `front_notes` compose the opening summary. `prepared_by` is data, not a signature asset. The engine does not infer source quantities, fill missing terms or upgrade a draft assumption into a client requirement.

## Common paper standard

Both active profiles render Legal 612 x 1008 point pages (8.5 x 14 inches). LAVI retains its 15 mm side margins; Lifes Awesome retains its 32 pt side margins. Component widths follow each profile's content rail. Typography is not enlarged or shrunk to fill the new sheet. Body pagination remains content-driven. Historical source page sizes/counts and source preview crops are not active paper instructions; current regression page counts live in `reference/layout_contract.json`. The original source PDFs and their recorded hashes remain unchanged.

## Architecture diagrams

Rows advance from the preceding row's measured height, then an 18-point gap. Caption clearance is separate. All connector segments are asserted to remain in the gap. Multiple source cards merge; multiple destination cards receive a split connector. Labels that do not fit fail with an error; split wording meaningfully instead of shrinking typography or patching coordinates. Do not copy the broken earlier CCTV Final/Final2 geometry.

## Release changes

A template change needs James's approval, a version increment, regenerated checksums in `manifest.json`, all tests and visual review. Do not bypass the manifest to make a one-off quote. New commercial/source edits normally change only JSON and do not change the style lock. Keep approved examples unchanged; create a new job instead.

CI regenerates all four full PDF fixtures and page previews as workflow artifacts. This makes the next agent independent of a previous container or private scratchpad. Historical engines are archived; billing and other document families are not replaced by this release.

## Authorized continuous flow and sign-off correction (22 September 2026)

Engine 2.0.2 / LAVI-QUOTATION-2026.5 adds two explicit job controls. For the Philpost revision, use `front_page_break: false` and `signature_mode: "two_column_prepared_conforme"`. These are reusable renderer capabilities, not a one-off PDF overlay. No forced blank remainder is left after the Project Boundary card: Section 1 follows in the same content flow, with normal heading/table keep rules. The continuous mode uses 3.2-point vertical table padding; font sizes, line heights, rails, colors, logos and all horizontal table padding remain unchanged.

The two-column sign-off is a single unbroken component with equal white panels, a clear 18-point gutter, 14-point interior padding, dedicated signing space above the preparer, and separate writable Authorized name / Signature / Date fields. It does not inherit the generic table grid or zebra shading. Do not remove this padding or reproduce underscore-based field widths. `conforme_fields` may supply short explicit field labels; blank signers stay blank.

Defaults for other jobs remain the existing first-page boundary and prepared-only block. Do not silently change previous quotations or Lifes Awesome styling. Historical LAVI job data using 2026.4 can be migrated by changing only the template ID to 2026.5; only select the new controls when requested. CPSC fixture IDs changed as release metadata; their commercial content and default rendered PDFs are preserved. The editor schema's missing closing brace was also repaired and is covered by a JSON-parse test.
