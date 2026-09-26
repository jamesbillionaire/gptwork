"""Regression guards for the requested continuous flow and padded sign-off."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import fitz
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import PageBreak
from quotation_engine.validation import ROOT, validate, ValidationError
from quotation_engine.renderer import Builder, render
from quotation_engine.signoff import TwoColumnSignoff

class FlowSignoffTests(unittest.TestCase):
    def setUp(self):
        self.job = json.loads((ROOT / 'quotation_engine/examples/cpsc-01.json').read_text())

    def test_continuous_front_has_no_forced_page_break(self):
        self.assertTrue(any(isinstance(x, PageBreak) for x in Builder(self.job).front()))
        self.job['front_page_break'] = False
        builder = Builder(self.job)
        self.assertFalse(any(isinstance(x, PageBreak) for x in builder.front()))
        table = builder.table([[builder.P('Readable table row', 'cell')]], [1])
        self.assertEqual(table._cellStyles[0][0].topPadding, 4.5)

    def test_padded_signoff_geometry(self):
        self.job['signature_mode'] = 'two_column_prepared_conforme'
        builder = Builder(self.job)
        block = TwoColumnSignoff(builder)
        self.assertEqual(block.padding, 14)
        self.assertEqual(block.gutter, 18)
        self.assertEqual(block.spaceBefore, 12.0)
        self.assertGreaterEqual(block.height, 148.0)
        self.assertAlmostEqual(2 * block.col_width + block.gutter, builder.w)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'signoff.pdf'
            c = Canvas(str(path), pagesize=(612, 1008))
            block.drawOn(c, builder.p['margin'], 100)
            c.save()
            with fitz.open(path) as doc:
                page = doc[0]
                left = page.search_for('PREPARED BY')[0]
                right = page.search_for('CONFORME')[0]
                self.assertAlmostEqual(left.x0, builder.p['margin'] + block.padding, places=2)
                self.assertAlmostEqual(right.x0, builder.p['margin'] + block.col_width + block.gutter + block.padding, places=2)
                self.assertAlmostEqual(left.y0, right.y0, places=2)
                for text in ('Authorized name:', 'Signature:', 'Date:'):
                    rect = page.search_for(text)[0]
                    self.assertGreater(rect.x0, builder.p['margin'] + block.col_width + block.gutter)
                    self.assertLess(rect.x1, 612 - builder.p['margin'] - block.padding)
                self.assertFalse(page.get_images())

    def test_new_controls_are_validated(self):
        for key, value in [('front_page_break', 'false'), ('signature_mode', 'anything'),
                           ('conforme_fields', {'wrong': 'Name'})]:
            job = copy.deepcopy(self.job); job[key] = value
            with self.assertRaises(ValidationError):
                validate(job)

    def test_no_duplicate_preparer_and_whole_signoff(self):
        self.job.update(front_page_break=False, signature_mode='two_column_prepared_conforme')
        with tempfile.TemporaryDirectory() as td:
            with fitz.open(render(self.job, Path(td) / 'flow.pdf')) as doc:
                matches = [p for p in doc if p.search_for('CONFORME')]
                self.assertEqual(len(matches), 1)
                text = matches[0].get_text()
                for s in ('PREPARED BY', self.job['prepared_by']['name'], 'Authorized name:', 'Signature:', 'Date:'):
                    self.assertIn(s, text)
                self.assertEqual(' '.join(p.get_text() for p in doc).count('PREPARED BY'), 1)


    def test_lavi_default_is_two_column_conforme(self):
        job=copy.deepcopy(self.job);job.pop('signature_mode',None)
        b=Builder(job)
        self.assertEqual(b.p['default_signature_mode'],'two_column_prepared_conforme')
        from quotation_engine.cli import new_job
        self.assertEqual(new_job('lavi')['signature_mode'],'two_column_prepared_conforme')
        self.assertNotIn('signature_mode',new_job('lifes-awesome'))

    def test_lavi_list_marker_rail_has_no_nested_indent(self):
        b=Builder(self.job)
        bullet=b.lavi_list_item('•','Wrapped list content that should align to one text rail.',False)
        number=b.lavi_list_item('10.','Numbered list content that should align to one text rail.',True)
        self.assertAlmostEqual(sum(bullet._colWidths),b.w,places=4)
        self.assertAlmostEqual(sum(number._colWidths),b.w,places=4)
        self.assertEqual(bullet._cellStyles[0][0].leftPadding,0)
        self.assertEqual(bullet._cellStyles[0][1].leftPadding,0)
        self.assertEqual(number._cellStyles[0][0].rightPadding,0)
        self.assertAlmostEqual(number._cellvalues[0][0].width,b.p['number_marker_width']-b.p['list_gutter'])

    def test_lavi_spacing_and_two_column_standard(self):
        b=Builder(self.job)
        bullet=b.lavi_list_item('•','First line\nwrapped',False)
        self.assertEqual(bullet._cellStyles[0][0].topPadding,b.p['list_top_padding'])
        self.assertEqual(bullet._cellStyles[0][0].bottomPadding,b.p['list_bottom_padding'])
        t=b.generic_table({'type':'table','rows':[['A','B'],['C','D']], 'widths':[.3,.7], 'header':False})
        self.assertAlmostEqual(t._colWidths[0]/b.w,.34,places=3)
        self.assertAlmostEqual(t._colWidths[1]/b.w,.66,places=3)
        card=b.lavi_front_cards();self.assertGreater(card.spaceAfter,8)

    def test_lavi_marker_baseline_contract(self):
        b=Builder(self.job)
        bullet=b.lavi_list_item('•','Aligned marker test',False)
        numbered=b.lavi_list_item('1.','Aligned marker test',True)
        for row in (bullet,numbered):
            marker=row._cellvalues[0][0]
            self.assertEqual(marker.__class__.__name__,'ListMarker')
            self.assertAlmostEqual(marker.height,b.styles['body'].leading)
            self.assertGreater(marker.ascent,0)

    def test_schema_is_valid_json(self):
        schema = json.loads((ROOT / 'quotation_engine/schema.json').read_text())
        self.assertEqual(schema['properties']['blocks']['type'], 'array')
        self.assertIn('front_page_break', schema['properties'])

if __name__ == '__main__':
    unittest.main()
