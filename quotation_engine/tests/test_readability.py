"""Readability regressions: no sub-10pt live text; preserve brand and commercial data."""
import copy,json,tempfile,unittest
from pathlib import Path
import fitz
from quotation_engine.validation import ROOT,PROFILES,validate,ValidationError
from quotation_engine.renderer import Builder,render

class ReadabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jobs=[json.loads(p.read_text()) for p in sorted((ROOT/'quotation_engine/examples').glob('cpsc-*.json'))]

    def test_profile_minimum(self):
        for p in PROFILES.values():
            self.assertEqual(p['minimum_font_size'],10)
            self.assertEqual(p['body'],[11,15])
            for key in ('table','note','heading','subheading','title'):
                self.assertGreaterEqual(p[key][0],10)

    def test_all_rendered_text_meets_floor(self):
        with tempfile.TemporaryDirectory() as td:
            for i,j in enumerate(self.jobs):
                with fitz.open(render(j,Path(td)/f'{i}.pdf')) as d:
                    for p in d:
                        for block in p.get_text('dict')['blocks']:
                            if block['type']!=0:continue
                            for line in block['lines']:
                                for s in line['spans']:
                                    if s['text'].strip():
                                        self.assertGreaterEqual(s['size'],9.99,(i,p.number,s['text']))

    def test_inline_small_type_is_rejected(self):
        for mark in ("<font size='8'>Bad</font>",'<font size="8">Bad</font>'):
            j=copy.deepcopy(self.jobs[0]);j['introduction']=[mark]
            with self.assertRaises(ValidationError):validate(j)

    def test_local_style_cannot_shrink_below_floor(self):
        b=Builder(self.jobs[0]);p=b.P('Not small',fontSize=6,leading=7)
        self.assertEqual(p.style.fontSize,10)
        self.assertGreaterEqual(p.style.leading,12)

    def test_price_card_cannot_split(self):
        b=Builder(self.jobs[0]);t=b.total_box();_,h=t.wrap(b.w,1000)
        self.assertFalse(t.split(b.w,h-1))

    def test_boq_can_flow_after_heading(self):
        b=Builder(self.jobs[0]);parts=b.boq(next(x for x in self.jobs[0]['blocks'] if x['type']=='boq'))
        self.assertEqual(parts[0].__class__.__name__,'CondPageBreak')
        self.assertFalse(parts[1].getKeepWithNext())
        self.assertTrue(parts[2].repeatRows)

if __name__=='__main__':unittest.main()
