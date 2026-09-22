"""Install the locally tested quotation readability revision on staging only."""
from pathlib import Path, PurePosixPath
import base64, hashlib, json, lzma, shutil, subprocess

root = Path.cwd()
raw = lzma.decompress(base64.b64decode((root / '.release/readability.b64').read_text().strip(), validate=True))
assert hashlib.sha256(raw).hexdigest() == 'b9c876c64835712fd23d8cacf9b318e304b8347b54e0d7af19f2ec198d0189e6', 'Transport checksum mismatch'
data = json.loads(raw)
assert len(data['expected']) == 15
for name, expected in data['expected'].items():
    rel = PurePosixPath(name)
    assert not rel.is_absolute() and '..' not in rel.parts and rel.parts[0] == 'quotation_engine'
    target = root / name
    if expected is None:
        assert not target.exists(), name
    else:
        assert hashlib.sha256(target.read_bytes()).hexdigest() == expected, name
assert subprocess.check_output(['git', 'hash-object', 'LATEST.md'], text=True).strip() == '10d8134e3d8505194dc820698de5ac610948ea03', 'Handoff changed; reconcile instead of overwriting'
archive = root / '.agents/handoffs/2026-09-22-before-readability-standard.md'
assert not archive.exists()
patch = root / '.release/changes.patch'
patch.write_text(data['patch'], encoding='utf-8')
subprocess.run(['git', 'apply', '--check', '--unidiff-zero', str(patch)], check=True)
subprocess.run(['git', 'apply', '--unidiff-zero', str(patch)], check=True)
shutil.copy2(root / 'LATEST.md', archive)

# Keep current upstream documentation, updating only this authorized typography revision.
notice = '''\n## Minimum readable typography — 22 September 2026\n\nEngine **2.1.0** establishes an absolute **10-point minimum for all live text** in both brand profiles; body paragraphs and conditions are **11/15 pt**. BOQ, table, note, metadata, diagram, contact, header and footer text must never fall below 10 pt. Section headings are 13/17 pt; subheadings 11/14 pt; titles 20/24 pt LAVI and 20/25 pt Lifes Awesome. See `quotation_engine/reference/readability_standard.md`, which supersedes earlier small-font size and leading values in historical examples or prose.\n\nPreserve separate brand fonts/colors, supplied logos, Legal paper and horizontal content rails. Headers/footers and diagrams wrap with measured heights, never reduced type. Readability takes priority over historical page counts. Continuous jobs retain `front_page_break: false`; the padded LAVI sign-off retains 14pt internal padding and 18pt gutter. No live font may be reduced to force a two-page quotation. Existing delivered PDFs are not changed in bulk.\n\nMigrate structured jobs by explicitly updating their template IDs. Source commercial data, including contradictory source terms, must not be silently reconciled during a typography-only edit. Run the locked CLI, all tests, minimum-font checks, content/arithmetic comparisons and rendered visual inspection.\n'''
paths = ['AGENTS.md', 'README.md', 'quotation_engine/README.md',
         'templates/lavi/cpsc-2026/README.md', 'templates/lifes-awesome/cpsc-2026/README.md',
         '.agents/skills/lavi-quotation/SKILL.md', '.agents/skills/lifes-awesome-quotation/SKILL.md']
for name in paths:
    path = root / name
    assert path.is_file(), name
    text = path.read_text(encoding='utf-8')
    text = text.replace('LAVI-QUOTATION-2026.5', 'LAVI-QUOTATION-2026.6')
    text = text.replace('LIFES-AWESOME-QUOTATION-2026.2', 'LIFES-AWESOME-QUOTATION-2026.3')
    if name == 'quotation_engine/README.md':
        text = text.replace('reference release 2.0.2', 'reference release 2.1.0')
    if name.startswith('templates/'):
        lines = []
        for line in text.splitlines():
            if line.startswith('- Liberation Sans Regular'):
                line = '- Liberation Sans Regular/Bold/Italic. Body 11/15 pt; BOQ and notes 10/13; labels, contact, metadata, running headers/footers and diagrams minimum 10 pt; section 13/17; subsection 11/14; title 20/24. All live text has a hard 10-point floor.'
            elif line.startswith('- DejaVu Sans Regular'):
                line = '- DejaVu Sans Regular/Bold/Oblique. Body 11/15 pt; BOQ and notes 10/13; labels, contact, metadata, running headers/footers and diagrams minimum 10 pt; section 13/17; subsection 11/14; title 20/25. All live text has a hard 10-point floor.'
            elif line.startswith('- Line-item proportions:'):
                line = '- Line-item proportions: 6% QTY, 10% UNIT, 49% DESCRIPTION, 17.5% UNIT PRICE, 17.5% AMOUNT. Outer width equals the content rail. QTY/UNIT centered; currency right aligned.'
            elif line.startswith('- Exact pricing column widths:'):
                line = '- Pricing column proportions: 7.5% QTY, 10.5% UNIT, 42% DESCRIPTION, 20% UNIT PRICE, 20% AMOUNT. Keep the 548-point content rail; center quantities/units and right-align currency.'
            line = line.replace('Supporting address/contact lines are 6.5 pt.', 'Supporting address/contact lines are at least 10 pt and wrap without shrinking.')
            line = line.replace("Do not inherit LAVI's Legal 612 x 1008 pt dimensions.", 'Both brands use Legal paper; retain the distinct Lifes Awesome margins and design.')
            lines.append(line)
        text = '\n'.join(lines) + '\n'
    path.write_text(text.rstrip() + '\n' + notice, encoding='utf-8')

(root / 'LATEST.md').write_text('''# Latest Agent Handoff

Handoff version: 0014
Last updated: 2026-09-22
Status: Minimum-readable typography implemented and locally verified. Staging CI must pass before explicit main promotion; do not infer an unobserved main CI result.

## User instruction and source
James reported client complaints about small fonts and requested a standardized minimum. This is a typography revision, not authority to change prices or commercial wording. Latest source is the uploaded LAVI_Philpost_Structured_Cabling_Quotation_v4(1).pdf, SHA256 f0f3157c47b74507b29347ec50e3862073defc4341d536c3235d19f70acd5fe5.

IMPORTANT: This uploaded copy removes the front Attention entry and changes the body validity clause to 45 days while retaining 15 days in the quote-details card. Both source values are preserved and the inconsistency disclosed to James. Do not restore Mr. James in the blank metadata or silently choose one validity term from an older JSON. Salutation remains Dear Sir James.

## Reusable standard
Engine 2.1.0; LAVI-QUOTATION-2026.6; LIFES-AWESOME-QUOTATION-2026.3. Absolute minimum 10pt live text, including tables, notes, diagram labels, contact details, headers, footers and page numbers. Body 11/15pt; section 13/17pt; subsection 11/14pt; titles 20pt. Separate fonts, palettes, original logos and Legal paper retained. Headers/footers are measured and wrap; diagrams use measured rows and gap-only connectors; narrow table columns accommodate labels without shrinking. See quotation_engine/reference/readability_standard.md.

Continuous Philpost flow and 14pt-padded/18pt-gutter sign-off retained. Do not shrink fonts to preserve a prior page count. Existing default fixture page counts naturally change; no historical client PDF is overwritten by this release. No raw fonts or signature images committed.

## Prepared conversation attachments
LAVI_Philpost_Structured_Cabling_Quotation_v5_Readable.pdf and companion .json, .md, .audit.json. Three Legal pages. PDF SHA256 0b7acebe329c2a426cce9bb74e9145cc837fef88d9edbbf657deec5e3bb2b25b. JSON SHA256 77a79b816cb665175a49219858ab8bf1fc38fb4290fbeb9553c29e83a0e12a6b. Retrieve actual attachments in a new session; filenames do not establish sandbox paths.

All 20 original priced rows and PHP299308.80 VAT-inclusive total remain unchanged. Date 16 September 2026, payment/duration/warranties and scope clarifications retained. Preparer Ms. Lea C. Ruiles / Admin. No signature copied. Source validity inconsistency remains unresolved.

## Local verification
All 24 tests passed; four complete example fixtures rendered (8/8/13/11 pages). Every fixture scanned: no live font below 10pt, text outside content rails or overlapping text spans. All three final Philpost pages rendered with Poppler and individually inspected. Complete normalized word counts match the uploaded source except repeated headers/footers/table headings. All arithmetic and commercial fields checked. Production lock verified; no renderer-checksum bypass.

## Next agent
Use the V5 JSON with the new template ID. Preserve its uploaded-source edits. Any later validity correction requires user direction. Main promotion requires successful staging CI and a fresh main-ref check; the release verification record records observed evidence. Historical CPSC/Philpost source quantities and private cost models remain untouched.

## Prior work
Actual prior CPSC Project 4 brand-neutral handoff is archived at .agents/handoffs/2026-09-22-before-readability-standard.md. Project 4, other CPSC quotes, Wonderzone and Phoenix are not revised by this typography release. No background task is scheduled.
''', encoding='utf-8')
print('Installed 15 verified engine files, preserved the prior handoff and updated active typography guidance.')
