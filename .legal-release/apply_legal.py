"""One-time, scoped Legal-paper correction. Never modifies client source PDFs."""
from pathlib import Path
import copy
import hashlib
import json
import re

ROOT = Path.cwd()

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

def replace_once(path, old, new):
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    assert text.count(old) == 1, (path, old, text.count(old))
    p.write_text(text.replace(old, new), encoding='utf-8')

prior = ROOT / '.agents/handoffs/2026-09-21-before-legal-paper-correction.md'
assert not prior.exists()
prior.write_bytes((ROOT / 'LATEST.md').read_bytes())
profiles_path = ROOT / 'quotation_engine/profiles.json'
profiles = json.loads(profiles_path.read_text())
original = copy.deepcopy(profiles)
assert profiles['lavi']['page'] == [595.275590551, 841.88976378]
assert profiles['lifes-awesome']['page'] == [612, 1008]
profiles['lavi']['page'] = [612, 1008]
profiles['lavi']['template_id'] = 'LAVI-QUOTATION-2026.4'
assert profiles['lifes-awesome'] == original['lifes-awesome']
assert {k:v for k,v in profiles['lavi'].items() if k not in ('page','template_id')} == {k:v for k,v in original['lavi'].items() if k not in ('page','template_id')}
write_json(profiles_path, profiles)

for name in ('cpsc-01.json', 'cpsc-02.json'):
    path = ROOT / 'quotation_engine/examples' / name
    old = json.loads(path.read_text())
    assert old['template_id'] == 'LAVI-QUOTATION-2026.3'
    new = copy.deepcopy(old)
    new['template_id'] = 'LAVI-QUOTATION-2026.4'
    write_json(path, new)
    old.pop('template_id'); new.pop('template_id')
    assert old == new

replace_once('quotation_engine/renderer.py',
    "19 if self._pagesize[1]>900 else 22.1,f'Page",
    "self._page_footer_y,f'Page")
replace_once('quotation_engine/renderer.py',
    'c._page_font=self.font;c._page_margin=m',
    'c._page_font=self.font;c._page_margin=m;c._page_footer_y=19 if self.software else 22.1')
replace_once('quotation_engine/__init__.py', '2.0.0', '2.0.1')
replace_once('quotation_engine/schema.json', 'LAVI-QUOTATION-2026.3', 'LAVI-QUOTATION-2026.4')

active_docs = [ROOT/'AGENTS.md', ROOT/'README.md', ROOT/'quotation_engine/README.md',
    ROOT/'templates/lavi/cpsc-2026/README.md', ROOT/'templates/lifes-awesome/cpsc-2026/README.md',
    ROOT/'.agents/skills/lavi-quotation/SKILL.md', ROOT/'.agents/skills/lifes-awesome-quotation/SKILL.md']
for path in active_docs:
    text = path.read_text(encoding='utf-8')
    text = text.replace('LAVI-QUOTATION-2026.3', 'LAVI-QUOTATION-2026.4')
    text = text.replace('2.0.0', '2.0.1')
    text = text.replace('A4: 595.275590551 x 841.88976378 pt; 15 mm (42.519685 pt) left/right margins; content width 510.23622 pt.',
                        'Legal: 612 x 1008 pt (8.5 x 14 inches); 15 mm (42.519685 pt) left/right margins; content width 526.96063 pt.')
    text = re.sub(r'\bA4\b', 'Legal 612 x 1008 pt', text)
    text = text.replace('Old LAVI Legal-size / Xavier styling', 'Old Xavier quotation styling')
    path.write_text(text, encoding='utf-8')
replace_once('AGENTS.md', '### Non-negotiable visual rules\n',
    '### Non-negotiable visual rules\n\n- **Both active brands use Legal paper, 8.5 x 14 inches (612 x 1008 points), on every page.** James explicitly corrected the paper standard on 21 September 2026. This supersedes the earlier LAVI A4 source geometry; historical source sizes are evidence only, not production defaults. Keep the separate brand margins, typography, colors and logo arrangements. Do not crop, stretch or scale an existing PDF to satisfy this rule; render/reflow from approved job data.\n')
replace_once('quotation_engine/README.md', '## Architecture diagrams',
    '## Common paper standard\n\nBoth active profiles render Legal 612 x 1008 point pages (8.5 x 14 inches). LAVI retains its 15 mm side margins; Lifes Awesome retains its 32 pt side margins. Component widths follow each profile\'s content rail. Typography is not enlarged or shrunk to fill the new sheet. Body pagination remains content-driven. Historical source page sizes/counts and source preview crops are not active paper instructions; current regression page counts live in `reference/layout_contract.json`. The original source PDFs and their recorded hashes remain unchanged.\n\n## Architecture diagrams')
reference = ROOT / 'quotation_engine/reference/README.md'
reference.write_text(reference.read_text() + '\n## Legal-paper correction, 21 September 2026\n\nOriginal source fingerprints, source page counts and approved style crops are retained as historical evidence. Both active production profiles now use Legal 612 x 1008 pt. Do not infer production paper size from an older LAVI source crop. `layout_contract.json` records the revised rendered fixture sizes/page counts; regeneration and review must use the active profiles.\n')

replace_once('quotation_engine/tests/test_approved.py',
    "self.assertEqual(len(doc),j['source']['pages'])",
    "layout=json.loads((ROOT/'quotation_engine/reference/layout_contract.json').read_text())\n                self.assertEqual(len(doc),layout['fixtures'][str(i)]['pages'])")
replace_once('quotation_engine/tests/test_approved.py',
    "self.assertAlmostEqual(pg.rect.width,p['page'][0],places=2);self.assertAlmostEqual(pg.rect.height,p['page'][1],places=2)",
    "self.assertAlmostEqual(pg.rect.width,612,places=2);self.assertAlmostEqual(pg.rect.height,1008,places=2)")
replace_once('quotation_engine/tests/test_approved.py',
    '    def test_source_totals(self):',
    '''    def test_both_profiles_require_legal_paper(self):
        for brand,p in PROFILES.items():
            self.assertEqual(p['page'],[612,1008],brand)
        self.assertEqual(PROFILES['lavi']['template_id'],'LAVI-QUOTATION-2026.4')
        self.assertEqual(PROFILES['lifes-awesome']['template_id'],'LIFES-AWESOME-QUOTATION-2026.2')
    def test_brand_styles_preserved(self):
        expected={'lavi':('LiberationSans',42.5196850394,'#0AA7AE','#243F73'),
                  'lifes-awesome':('DejaVuSans',32,'#00ADED','#57616C')}
        for brand,(font,margin,accent,header) in expected.items():
            p=PROFILES[brand]
            self.assertEqual((p['font'],p['margin'],p['accent'],p['table_header']),
                             (font,margin,accent,header))
    def test_footer_baseline_is_not_selected_by_page_size(self):
        with tempfile.TemporaryDirectory() as td:
            for j in self.jobs:
                doc=fitz.open(render(j,Path(td)/f"footer-{j['source']['project']}.pdf"))
                expected_y=1008-(22.1 if j['brand']=='lavi' else 19)
                for pg in doc:
                    spans=[s for b in pg.get_text('dict')['blocks'] if b['type']==0 for l in b['lines'] for s in l['spans']]
                    footer=next(s for s in spans if j['footer_label'] in s['text'])
                    number=next(s for s in spans if re.fullmatch(r'Page \\d+ of \\d+',s['text']))
                    self.assertAlmostEqual(footer['origin'][1],expected_y,places=2)
                    self.assertAlmostEqual(number['origin'][1],expected_y,places=2)
    def test_source_totals(self):''')

# Establish current layout baselines for this authorized paper-size release only.
# These outputs require visual review before main promotion; normal CI does not regenerate the contract.
from quotation_engine.renderer import render
import fitz
out = ROOT / 'output/legal'
out.mkdir(parents=True, exist_ok=True)
layout = {'page_points':[612,1008], 'paper':'Legal 8.5 x 14 inches',
          'authority':'James: Both template should use legal size paper format.', 'fixtures':{}}
for src in sorted((ROOT/'quotation_engine/examples').glob('cpsc-*.json')):
    job=json.loads(src.read_text())
    pdf=render(job,out/(src.stem+'.pdf'))
    with fitz.open(pdf) as doc:
        assert all(list(pg.rect)[2:]==[612,1008] for pg in doc)
        layout['fixtures'][str(job['source']['project'])]={'pages':len(doc),'brand':job['brand']}
write_json(ROOT/'quotation_engine/reference/layout_contract.json',layout)

(ROOT/'LATEST.md').write_text('''# Latest Agent Handoff

Handoff version: 0007
Last updated: 2026-09-21
Status: Legal-paper correction prepared and verified on release branch; main promotion follows visual review.

## Latest explicit instruction
James: "Both template should use legal size paper format." Both active brands must use Legal 8.5 x 14 inches (612 x 1008 pt), not A4 or 8.5 x 13. This paper instruction overrides the older source PDF dimensions, not their commercial data.

## Active profiles
- Engine 2.0.1; LAVI-QUOTATION-2026.4: Legal, 15 mm side margins, Liberation Sans, teal/navy, original logo at left on page 1.
- LIFES-AWESOME-QUOTATION-2026.2: Legal, 32 pt side margins, DejaVu Sans, cyan/gray, original centered logo on page 1. Its profile is unchanged.
- Preserve justified narratives, common content rails, hanging lists, text-only continuation headers and safe shared diagram geometry. Page numbers align with each brand's footer baseline, independent of paper height.

## Changes and safeguards
Profiles, LAVI example template IDs, renderer footer baseline, active guides/skills, tests and manifest updated. Historical source PDF fingerprints and page counts are unchanged; active rendered page counts are in quotation_engine/reference/layout_contract.json. Regenerate through the existing engine; no stretching, cropping, font resizing, filler spacing or forced historical page counts.

Client data unchanged: P1 PHP17,886,000; P2 PHP7,353,000; P5 PHP26,841,000; P8 PHP6,368,000, all inclusive. Dates, rates, quantities, terms, migration allowances, integration boundaries and signatory roles are job-specific. Cloud hosting remains for CPSC discussion/approval. No signed PDF was altered and no signatures added.

## Verification and next steps
13 regression tests cover Legal dimensions, retained brand styles, aligned footer/page numbers, four totals, source terms, no implicit VAT, continuation logos, content-rail bounds, fixture pagination and diagram connectors. All four full PDFs are rendered for review. Complete rendered-page review and verify CI before main promotion; update this status with completion evidence.

## Prior work
Previous completed template handoff is at .agents/handoffs/2026-09-21-before-legal-paper-correction.md. Prior SFDHMC and historical billing/FDAS instructions remain archived as before. This task changes template paper sizing, not client quotations or unrelated standards.
''',encoding='utf-8')

manifest_path=ROOT/'quotation_engine/manifest.json'
manifest=json.loads(manifest_path.read_text())
manifest['release_id']='CPSC-APPROVED-QUOTATIONS-2026-09-LEGAL'
manifest['engine_version']='2.0.1'
manifest['active_profiles']['lavi']='LAVI-QUOTATION-2026.4'
manifest['paper_standard']={'name':'Legal','width_points':612,'height_points':1008,'applies_to':['lavi','lifes-awesome'],'authority':'James explicitly corrected both templates to Legal paper on 2026-09-21.'}
manifest['sha256']['quotation_engine/reference/layout_contract.json']=''
for name in manifest['sha256']:
    manifest['sha256'][name]=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
write_json(manifest_path,manifest)
print(json.dumps(layout,indent=2))
print('Legal paper correction applied; client data and original source assets preserved.')
