"""Finite offline figure controls; prepare never publishes book assets."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import figure_layout as layout
import figure_strings as figures


LABEL = '检查输入API()与位置2 · 我'
EN_LABEL = 'Check input API() and position 2 · 我'
JA_LABEL = '入力API()と位置2 · 我を確認します'
SVG = ('<svg xmlns="http://www.w3.org/2000/svg" class="vb-svg" id="frame-2" '
       'viewBox="0 0 240 100" aria-labelledby="title-2">'
       '<title id="title-2">输入与结果</title>'
       '<rect x="10" y="10" width="220" height="80" fill="#eaf0f5" data-frame="2"/>'
       '<text x="20" y="40" font-size="16">' + LABEL + '</text>'
       '<text x="20" y="70" font-size="16">0.25</text></svg>')
AP = ('<figure><svg xmlns="http://www.w3.org/2000/svg" class="ap-desktop-svg" '
      'viewBox="0 0 900 120"><title>对应表格</title>'
      '<text>状态</text><text>编号</text><text>完成</text><text>ID2</text></svg>'
      '<table class="ap-table-equivalent"><tr><th>状态</th><th>编号</th></tr>'
      '<tr><td>完成</td><td>ID2</td></tr></table></figure>')
TRANSLATIONS = {
    LABEL: (EN_LABEL, JA_LABEL),
    '输入与结果': ('Input and result', '入力と結果'),
    '对应表格': ('Corresponding table', '対応する表'),
    '状态': ('Status', '状態'), '编号': ('ID', '番号'), '完成': ('Complete', '完了'),
}


class FigureJapaneseTests(unittest.TestCase):
    def fixture(self):
        temporary = tempfile.TemporaryDirectory(prefix='figures-ja-')
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        for directory in ('assets', 'i18n/content', 'en/assets', 'ja/assets'):
            (root / directory).mkdir(parents=True)
        source = '<html><body>' + SVG + AP + '<a href="assets/figure.svg">SVG</a></body></html>'
        (root / 'index.html').write_text(source)
        (root / 'assets/figure.svg').write_text(SVG)
        data = 'window.VISUAL_DATA=' + json.dumps({'frames': [{'id': 'f2', 'sourceGroup': '原键', 'value': 0.25, 'svg': SVG}]}, ensure_ascii=False) + ';'
        (root / figures.DATA).write_text(data)
        (root / 'i18n/content/index.json').write_text('{"page":"index.html"}')
        for lang, column in (('en', 0), ('ja', 1)):
            target = source
            for src in ('状态', '编号', '完成'):
                # AP table is translated upstream; SVG remains the source here.
                target = target.replace('>' + src + '</th>', '>' + TRANSLATIONS[src][column] + '</th>')
                target = target.replace('>' + src + '</td>', '>' + TRANSLATIONS[src][column] + '</td>')
            (root / lang / 'index.html').write_text(target)
            (root / lang / figures.DATA).write_text(data)
        registry = figures.inventory(root)
        (root / figures.REGISTRY).write_text(json.dumps(registry, ensure_ascii=False))
        table = {src: {'id': i, 'en': values[0], 'ja': values[1]}
                 for i, (src, values) in enumerate(TRANSLATIONS.items(), 1)}
        (root / figures.TABLE).write_text(json.dumps({'s': table}, ensure_ascii=False))
        return root

    def snapshot(self, root):
        return {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}

    def test_prepare_is_read_only_deterministic_and_preserves_data(self):
        root = self.fixture()
        before = self.snapshot(root)
        payloads, proof = figures.prepare('ja', root)
        self.assertEqual(set(payloads), {'ja/index.html', 'ja/assets/visual-data.js', 'ja/assets/figure.svg'})
        self.assertEqual(proof['figures'], 4)
        self.assertEqual((payloads, proof), figures.prepare('ja', root))
        self.assertEqual(before, self.snapshot(root))
        self.assertIn('Hiragino Sans', payloads['ja/index.html'])
        self.assertIn('入力API()と位置2', payloads['ja/index.html'])
        self.assertNotIn('检查输入', payloads['ja/index.html'])
        _, source_data = figures.read_data((root / figures.DATA).read_text())
        _, target_data = figures.read_data(payloads['ja/' + figures.DATA])
        self.assertEqual(figures.data_without_svg(source_data), figures.data_without_svg(target_data))
        self.assertTrue(all(report.get('geometry_identity', True) for report in proof['report']))
        self.assertTrue(all(line['width'] <= line['limit'] + .01
                            for report in proof['report'] for line in report['text_fit']))
        self.assertEqual(layout.geometry_identity(layout.parse(SVG)),
                         layout.geometry_identity(layout.parse(payloads['ja/assets/figure.svg'].strip())))
        self.assertIn('0.25', payloads['ja/assets/figure.svg'])
        en, _ = figures.prepare('en', root)
        self.assertIn('Check input API()', en['en/index.html'])
        self.assertIn('Arial', en['en/index.html'])
        self.assertNotIn('Hiragino Sans', en['en/index.html'])

    def test_export_selects_language_and_missing_is_rejected(self):
        root = self.fixture()
        table = json.loads((root / figures.TABLE).read_text())
        del table['s'][LABEL]['ja']
        (root / figures.TABLE).write_text(json.dumps(table, ensure_ascii=False))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            figures.export('ja', root)
        self.assertIn('target language: ja', output.getvalue())
        self.assertIn('\t' + LABEL, output.getvalue())
        with self.assertRaisesRegex(figures.FigureError, 'missing 1 SVG translations'):
            figures.prepare('ja', root)
        figures.prepare('en', root)

    def test_japanese_review_does_not_waive_other_protections(self):
        figures.validate_translation(LABEL, JA_LABEL, lang='ja')
        figures.validate_translation('状态', '状態', lang='ja')
        figures.validate_translation('第2列', '第2列', lang='ja')
        for source, value, error in [
            (LABEL, JA_LABEL.replace('位置2', '位置3'), 'numeric'),
            (LABEL, JA_LABEL.replace('API()', 'API[]'), 'identifiers'),
            (LABEL, JA_LABEL.replace('我', '私'), 'vocabulary'),
            ('输入与结果', '输入与结果', 'exact-pair'),
            ('检查输入和计算结果', '確認入力及計算結果', 'exact-pair'),
            (LABEL, '\x00' + JA_LABEL, 'control'),
            (LABEL, '', 'empty'),
        ]:
            with self.subTest(source=source, value=value):
                with self.assertRaisesRegex(figures.FigureError, error):
                    figures.validate_translation(source, value, lang='ja', approvals={})
        figures.validate_translation('检查输入和计算结果', '確認入力及計算結果', lang='ja',
                                     approvals={'检查输入和计算结果': '確認入力及計算結果'})
        with self.assertRaisesRegex(figures.FigureError, 'numeric'):
            figures.validate_translation('检查输入2', '入力3', lang='ja', approvals={'检查输入2': '入力3'})
        with self.assertRaisesRegex(figures.FigureError, 'untranslated SVG'):
            figures.validate_translation('状态', '状態')

    def test_boundaries_stale_sources_and_immutable_ap_data_fail(self):
        for operation in (figures.prepare, figures.export):
            with self.assertRaisesRegex(figures.FigureError, 'supports --lang'):
                operation('../ja', self.fixture())
        root = self.fixture()
        (root / 'index.html').write_text((root / 'index.html').read_text() + ' ')
        with self.assertRaisesRegex(figures.FigureError, 'registry is stale'):
            figures.prepare('ja', root)
        root = self.fixture()
        target = root / 'ja/index.html'
        target.write_text(target.read_text().replace('<td>ID2</td>', '<td>ID3</td>'))
        with self.assertRaisesRegex(figures.FigureError, 'immutable data cell'):
            figures.prepare('ja', root)
        root = self.fixture()
        (root / 'i18n/ja-approved.json').write_text('{"pairs": []}')
        with self.assertRaisesRegex(figures.FigureError, 'exact-pair review'):
            figures.prepare('ja', root)
        # English does not read the Japanese approval file.
        figures.prepare('en', root)

    def test_japanese_breaks_preserve_code_graphemes_and_punctuation(self):
        value = '入力の表現とAPI()の計算結果を確認します。'
        lines = layout.wrap(value, 100, 16, lang='ja')
        self.assertGreater(len(lines), 1)
        self.assertEqual(''.join(lines), value)
        self.assertTrue(all(layout.width(line, 16, lang='ja') <= 100 for line in lines))
        value = '「小さいきゃく」とW_q[2]、run.jsonを確認します。'
        lines = layout.wrap(value, 110, 16, lang='ja')
        self.assertEqual(''.join(lines), value)
        self.assertTrue(all(line[0] not in layout.JA_NO_START and line[-1] not in layout.JA_NO_END for line in lines))
        self.assertTrue(any('W_q[2]' in line for line in lines))
        self.assertTrue(any('run.json' in line for line in lines))
        self.assertEqual(layout.japanese_units('か\u3099く'), ['か\u3099', 'く'])
        self.assertEqual(layout.japanese_units('ｷﾞｬ'), ['ｷﾞｬ'])
        self.assertEqual(layout.width('-0.3000', 14, lang='ja'), layout.width('-0.3000', 14))
        self.assertAlmostEqual(layout.width('−0.3000', 14, lang='ja'), layout.width('−0.3000', 14))
        with self.assertRaisesRegex(layout.LayoutError, 'unbreakable identifier'):
            layout.reflow(SVG, {}, lambda s: '入力' + 'long_code_identifier_123' * 10 if s == LABEL else '入力と結果', lang='ja')
        with self.assertRaisesRegex(layout.LayoutError, 'unsupported layout'):
            layout.wrap('入力', 100, lang='fr')


if __name__ == '__main__':
    unittest.main()
