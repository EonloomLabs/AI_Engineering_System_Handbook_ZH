"""Finite tests for Spanish annotations over immutable published geometry."""
import collections
import json
from pathlib import Path
import unittest

import figure_layout as layout
import figure_strings as figures


ROOT = Path(__file__).resolve().parent.parent


class SpanishFigureLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table = json.loads((ROOT / figures.TABLE).read_text(encoding='utf-8'))['s']

    def actual(self, page, index):
        source = list(figures.SVG.finditer((ROOT / page).read_text(encoding='utf-8')))[index].group()
        mapping = {s: row['es'] for s, row in self.table.items() if row.get('es')}
        report = {}
        result = layout.reflow(source, mapping, mapping.__getitem__, report, lang='es')
        before, after = layout.parse(source), layout.parse(result)
        self.assertEqual(layout.geometry_identity(before), layout.geometry_identity(after))
        self.assertTrue(all(r['width'] <= r['limit'] + .01 for r in report['text_fit']))
        self.assertTrue(all(r['font_size'] == r['source_font_size'] for r in report['text_fit'] if r['annotation']))
        numbers = lambda root: collections.Counter(layout.content(e) for e in root.iter()
                    if layout.tag(e)=='text' and layout.NUMBER.fullmatch(layout.content(e)))
        self.assertEqual(numbers(before),numbers(after))
        return source, after, report

    def test_actual_end_anchored_input_and_slot_rails_keep_native_words_and_values(self):
        for page, index, source_label, target in (
                ('chapters/04.html',6,'输入','Entrada'),
                ('chapters/08.html',6,'槽0','Ranura 0')):
            with self.subTest(page=page):
                _, after, report = self.actual(page,index)
                label = next(e for e in after.iter() if layout.tag(e)=='text' and layout.content(e)==target)
                self.assertEqual(label.get('text-anchor'),'start')
                fit = next(r for r in report['text_fit'] if r['source']==source_label)
                self.assertTrue(fit['annotation'])
                self.assertEqual(fit['font_size'],14)

    def test_actual_unboxed_columns_get_a_full_width_band_above_both_matrices(self):
        _, after, report = self.actual('foundations/05.html',6)
        labels = [e for e in after.iter() if layout.tag(e)=='text' and layout.content(e).startswith('Característica ')]
        self.assertEqual([layout.content(e) for e in labels],['Característica '+str(i) for i in range(4)])
        lines = [e for e in after.iter() if e.get('data-i18n-annotation')=='true']
        self.assertEqual(len(lines),4)
        for label, leader in zip(labels,lines):
            self.assertEqual(label.get('font-size'),'13')
            self.assertEqual(label.get('x'),leader.get('x1'))
            self.assertLess(float(label.get('y')),float(leader.get('y2')))
        rectangles=[e for e in after.iter() if layout.tag(e)=='rect' and e.get('x') in ('122','552')]
        self.assertLess(max(float(e.get('y')) for e in labels),min(float(e.get('y')) for e in rectangles))
        self.assertEqual([r['annotation'] for r in report['text_fit'] if r['source'].startswith('特征')],[True]*4)

    def test_actual_timeline_bar_widths_remain_exact_and_caption_uses_original_size(self):
        source, after, report = self.actual('walkthroughs/d.html',6)
        before=layout.parse(source)
        rects=lambda root:[(e.get('x'),e.get('width')) for e in root.iter() if layout.tag(e)=='rect']
        self.assertEqual(rects(before),rects(after))
        fit=next(r for r in report['text_fit'] if r['source']=='检索')
        self.assertTrue(fit['annotation'])
        self.assertEqual(fit['font_size'],14)
        self.assertIn('Recuperación',[layout.content(e) for e in after.iter() if layout.tag(e)=='text'])

    def test_unowned_text_and_overlong_identifiers_still_fail(self):
        source=('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 140 100">'
                '<text x="25" y="40" font-size="14" text-anchor="middle">标题0</text>'
                '<text x="75" y="40" font-size="14" text-anchor="middle">标题1</text></svg>')
        mapping={'标题0':'Característica 0','标题1':'Característica 1'}
        with self.assertRaisesRegex(layout.LayoutError,'unbreakable identifier'):
            layout.reflow(source,mapping,mapping.__getitem__,lang='es')
        owned=source.replace('</svg>','<rect x="0" y="50" width="50" height="30"/>'
                             '<rect x="50" y="50" width="50" height="30"/></svg>')
        mapping['标题0']='A_very_long_unbreakable_identifier_that_exceeds_the_entire_annotation_band'
        with self.assertRaisesRegex(layout.LayoutError,'unbreakable annotation'):
            layout.reflow(owned,mapping,mapping.__getitem__,lang='es')

    def test_new_external_heading_path_is_selected_only_for_spanish(self):
        source=('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 390 150">'
                '<text x="55" y="90" font-size="14" text-anchor="end">输入</text>'
                '<rect id="cell" x="65" y="70" width="100" height="40" fill="#abc"/>'
                '<text x="115" y="90" font-size="14" text-anchor="middle">0.25</text></svg>')
        mapping={'输入':'Entrada'}
        report={}
        layout.reflow(source,mapping,mapping.__getitem__,report,lang='es')
        self.assertEqual(report['annotation_blocks'],1)
        for lang in ('en','ja','vi'):
            with self.subTest(lang=lang), self.assertRaisesRegex(layout.LayoutError,'unbreakable identifier'):
                layout.reflow(source,mapping,mapping.__getitem__,lang=lang)


if __name__=='__main__':
    unittest.main()
