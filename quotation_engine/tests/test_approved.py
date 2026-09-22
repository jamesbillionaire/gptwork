"""Arithmetic, identity, layout, diagram and preservation regression gates."""
import copy,hashlib,json,re,tempfile,unittest
from pathlib import Path
import fitz
from reportlab.pdfgen.canvas import Canvas
from quotation_engine.validation import ROOT,PROFILES,validate,ValidationError,totals
from quotation_engine.renderer import Builder,render
from quotation_engine.cli import new_job,verify_lock
from quotation_engine.diagrams import Diagram

EXAMPLES=ROOT/'quotation_engine/examples'

class ApprovalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jobs=[json.loads(p.read_text()) for p in sorted(EXAMPLES.glob('cpsc-*.json'))]
    def test_asset_lock(self):
        self.assertEqual(verify_lock()['status'],'APPROVED_LOCKED')
    def test_both_profiles_require_legal_paper(self):
        for brand,p in PROFILES.items():
            self.assertEqual(p['page'],[612,1008],brand)
        self.assertEqual(PROFILES['lavi']['template_id'],'LAVI-QUOTATION-2026.6')
        self.assertEqual(PROFILES['lifes-awesome']['template_id'],'LIFES-AWESOME-QUOTATION-2026.3')
    def test_brand_styles_preserved(self):
        expected={'lavi':('LiberationSans',42.5196850394,'#0AA7AE','#243F73'),
                  'lifes-awesome':('DejaVuSans',32,'#00ADED','#57616C')}
        for brand,(font,margin,accent,header) in expected.items():
            p=PROFILES[brand]
            self.assertEqual((p['font'],p['margin'],p['accent'],p['table_header']),
                             (font,margin,accent,header))
    def test_footer_is_readable_and_within_content_rails(self):
        with tempfile.TemporaryDirectory() as td:
            for j in self.jobs:
                with fitz.open(render(j,Path(td)/f"footer-{j['source']['project']}.pdf")) as doc:
                    for pg in doc:
                        spans=[s for b in pg.get_text('dict')['blocks'] if b['type']==0 for l in b['lines'] for s in l['spans']]
                        number=next(s for s in spans if re.fullmatch(r'Page \d+ of \d+',s['text']))
                        self.assertAlmostEqual(number['size'],10,places=2)
                        self.assertAlmostEqual(number['origin'][1],988,places=2)
                        self.assertLessEqual(number['bbox'][2],612-PROFILES[j['brand']]['margin']+.1)
    def test_source_totals(self):
        expected={1:'17886000.00',2:'7353000.00',5:'26841000.00',8:'6368000.00'}
        for j in self.jobs:self.assertEqual(validate(j)['total'],expected[j['source']['project']])
    def test_no_implicit_vat(self):
        j=copy.deepcopy(self.jobs[0]);j['tax_treatment']='VAT Exclusive'
        self.assertEqual(totals(j)[1],totals(self.jobs[0])[1])
    def test_reject_arithmetic_changes(self):
        for field in ('qty','unit_price','amount'):
            j=copy.deepcopy(self.jobs[0]);r=next(b for b in j['blocks'] if b['type']=='boq')['items'][0];r[field]='9999'
            with self.assertRaises(ValidationError):validate(j)
    def test_blank_jobs_do_not_leak_client_terms(self):
        for brand in PROFILES:
            j=new_job(brand);self.assertNotIn('CPSC',json.dumps(j));self.assertIsNone(j['validity_days']);self.assertEqual(j['date'],'');self.assertEqual(j['tax_treatment'],'')
            with self.assertRaises(ValidationError):validate(j)
    def test_brand_and_signature_guards(self):
        j=copy.deepcopy(self.jobs[0]);j['brand']='lifes-awesome'
        with self.assertRaises(ValidationError):validate(j)
        j=copy.deepcopy(self.jobs[0]);j['signature']='copied.png'
        with self.assertRaises(ValidationError):validate(j)
    def test_nonfinite_and_float_rejected(self):
        for invalid in ('NaN','Infinity',1.1,True):
            j=copy.deepcopy(self.jobs[0]);j['expected_total']=invalid
            with self.assertRaises(ValidationError):validate(j)
    def test_approved_terms_are_job_specific(self):
        for j in self.jobs:
            i=j['source']['project'];self.assertEqual(j['validity_days'],60 if i in (5,8) else 30)
            self.assertEqual(j['date'],'18 September 2026')
            self.assertEqual(j['prepared_by']['role'],'General Manager' if i in (5,8) else 'CEO')
        # Migration quantities are merely source job allowances, not schema defaults.
        self.assertNotIn('100GB',json.dumps(new_job('lifes-awesome')))
    def test_content_and_layout(self):
        contracts=json.loads((ROOT/'quotation_engine/reference/word_contract.json').read_text())
        with tempfile.TemporaryDirectory() as td:
            for j in self.jobs:
                i=j['source']['project'];out=render(j,Path(td)/f'{i}.pdf');doc=fitz.open(out);p=PROFILES[j['brand']]
                # These counts are fixture regression checks, not forced page counts for new work.
                layout=json.loads((ROOT/'quotation_engine/reference/layout_contract.json').read_text())
                self.assertEqual(len(doc),layout['fixtures'][str(i)]['pages'])
                full=' '.join(pg.get_text() for pg in doc)
                words=set(re.findall(r'[\w/-]+',full.lower()))
                missing=set(contracts[str(i)])-words-{'continued'}
                self.assertFalse(missing,f'Missing source terms: {missing}')
                self.assertIn(j['expected_total'][:-3].replace(',',''),full.replace(',',''))
                self.assertIn(j['date'],full)
                self.assertIn(j['quote_no'],full)
                for pi,pg in enumerate(doc):
                    self.assertAlmostEqual(pg.rect.width,612,places=2);self.assertAlmostEqual(pg.rect.height,1008,places=2)
                    self.assertIn(f'Page {pi+1} of {len(doc)}',pg.get_text())
                    if pi:self.assertFalse(pg.get_image_info(),'Continuation page must not repeat a logo/signature image.')
                    for word in pg.get_text('words'):
                        self.assertGreaterEqual(word[0],p['margin']-1);self.assertLessEqual(word[2],p['page'][0]-p['margin']+1)
                        self.assertGreater(word[1],0);self.assertLess(word[3],p['page'][1])
                self.assertTrue(doc[0].get_image_info(),'First-page supplied logo missing.')
    def test_diagram_geometry_and_overflow(self):
        with tempfile.TemporaryDirectory() as td:
            for j in self.jobs:
                b=Builder(j)
                for spec in (x for x in j['blocks'] if x['type']=='diagram'):
                    g=Diagram(spec,b.p,b.w,b.font,b.bold);c=Canvas(str(Path(td)/'diagram.pdf'));g.drawOn(c,0,0);c.save()
                    self.assertTrue(g.connectors)
                    for _,y1,_,y2,lo,hi in g.connectors:self.assertTrue(lo<y1<hi and lo<y2<hi)
                    for (y,h),(yn,_) in zip(g.geometry,g.geometry[1:]):self.assertEqual(yn-y-h,18)
                    bad=copy.deepcopy(spec);bad['rows'][0]['nodes'][0]['title']='UNACCEPTABLY LONG LABEL '*40
                    with self.assertRaises(ValueError):Diagram(bad,b.p,b.w,b.font,b.bold).drawOn(c,0,0)

if __name__=='__main__':unittest.main()
