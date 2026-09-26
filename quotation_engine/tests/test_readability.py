"""Typography regressions for the LAVI balanced hierarchy and unchanged Lifes Awesome profile."""
import copy,json,tempfile,unittest
from pathlib import Path
import fitz
from quotation_engine.validation import ROOT,PROFILES,validate,ValidationError
from quotation_engine.renderer import Builder,render

class ReadabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jobs=[json.loads(p.read_text()) for p in sorted((ROOT/'quotation_engine/examples').glob('cpsc-*.json'))]

    def test_lavi_role_sizes(self):
        p=PROFILES['lavi']
        self.assertEqual(p['title'],[16.0,19.2])
        self.assertEqual(p['heading'],[11.0,13.5])
        self.assertEqual(p['subheading'],[10.0,12.4])
        self.assertEqual(p['body'],[9.5,12.5])
        self.assertEqual(p['table'],[9.0,11.4])
        self.assertEqual((p['metadata_size'],p['table_header_size']), (9.5,9.0))
        self.assertEqual((p['company_header_size'],p['contact_size'],p['furniture_size']), (9.0,8.0,8.0))
        self.assertEqual((p['continuation_company_size'],p['continuation_company_leading']), (8.0,9.6))
        self.assertEqual(p['continuation_header_alignment'],'single_row')
        self.assertEqual(p['default_signature_mode'],'two_column_prepared_conforme')
        self.assertEqual((p['table_padding'],p['flow_table_padding']), (4.5,4.5))
        self.assertEqual(p['generic_two_column_widths'],[0.34,0.66])
        self.assertEqual((p['signoff_height'],p['signoff_space_before']), (148.0,12.0))
        self.assertEqual(p['list_marker_alignment'],'first_line_baseline')
        self.assertEqual(p['prepared_signature_line_gap'],7.0)

    def test_lifes_awesome_typography_unchanged(self):
        p=PROFILES['lifes-awesome']
        self.assertEqual(p['minimum_font_size'],10)
        self.assertEqual(p['body'],[11,15]);self.assertEqual(p['table'],[10,13])
        self.assertEqual(p['heading'],[13,17]);self.assertEqual(p['subheading'],[11,14]);self.assertEqual(p['title'],[20,25])

    def test_all_rendered_text_meets_profile_floor(self):
        with tempfile.TemporaryDirectory() as td:
            for i,j in enumerate(self.jobs):
                floor=PROFILES[j['brand']]['minimum_font_size']-.01
                with fitz.open(render(j,Path(td)/f'{i}.pdf')) as d:
                    for p in d:
                        for block in p.get_text('dict')['blocks']:
                            if block['type']!=0:continue
                            for line in block['lines']:
                                for span in line['spans']:
                                    if span['text'].strip():self.assertGreaterEqual(span['size'],floor,(i,p.number,span['text']))

    def test_inline_content_small_type_is_rejected(self):
        for brand,size in [('lavi','8'),('lifes-awesome','9')]:
            job=copy.deepcopy(next(j for j in self.jobs if j['brand']==brand))
            job['introduction']=[f"<font size='{size}'>Bad</font>"]
            with self.assertRaises(ValidationError):validate(job)

    def test_local_content_styles_cannot_shrink_below_role(self):
        b=Builder(next(j for j in self.jobs if j['brand']=='lavi'))
        self.assertEqual(b.P('Body','body',fontSize=6).style.fontSize,9.5)
        self.assertEqual(b.P('Cell','cell',fontSize=6).style.fontSize,9.0)
        self.assertEqual(b.P('Footer','meta',fontSize=6).style.fontSize,8.0)

    def test_price_card_cannot_split(self):
        b=Builder(next(j for j in self.jobs if j['brand']=='lavi'));t=b.total_box();_,h=t.wrap(b.w,1000)
        self.assertFalse(t.split(b.w,h-1))

    def test_boq_can_flow_after_heading(self):
        job=next(j for j in self.jobs if j['brand']=='lavi');b=Builder(job);parts=b.boq(next(x for x in job['blocks'] if x['type']=='boq'))
        self.assertEqual(parts[0].__class__.__name__,'CondPageBreak');self.assertFalse(parts[1].getKeepWithNext());self.assertTrue(parts[2].repeatRows)

if __name__=='__main__':unittest.main()
