"""Spanish model-viewer geometry controls; no published outputs are written."""
import json
from pathlib import Path
import unittest

import build_complete
import complete_strings
import runtime_strings as runtime
import test_es_vi_tools as latin_fixture
import test_runtime_strings_ja as runtime_fixture


class SpanishModelPlayerTests(unittest.TestCase):
    def source(self):
        return (runtime.ROOT / 'assets/model-player.js').read_text(encoding='utf-8')

    def test_spanish_expands_only_the_declared_geometry_and_is_idempotent(self):
        source = self.source()
        baseline = runtime.adapt_model_player(source)
        output = runtime.adapt_model_player(source, lang='es')
        self.assertIn('Math.max(660,255+rows[0].length*118)', output)
        self.assertIn('x:250+j*118+55,y:28', output)
        self.assertIn('x:250+j*118,y:42+t*46,width:112,height:35', output)
        self.assertIn('x:250+j*118+56,y:66+t*46', output)
        self.assertEqual(output, runtime.adapt_model_player(output, lang='es'))
        self.assertEqual(output, runtime.adapt_model_player(baseline, lang='es'))
        normalized = output.replace('255+rows[0].length*118', '195+rows[0].length*94')
        normalized = normalized.replace('x:250+j*118+55', 'x:190+j*94+43')
        normalized = normalized.replace('x:250+j*118+56', 'x:190+j*94+44')
        normalized = normalized.replace('x:250+j*118', 'x:190+j*94').replace('width:112,height:35', 'width:88,height:35')
        self.assertEqual(normalized, baseline)

    def test_default_english_japanese_and_vietnamese_keep_previous_bytes(self):
        source = self.source()
        expected = runtime.adapt_model_player(source)
        for lang in ('en', 'ja', 'vi'):
            self.assertEqual(runtime.adapt_model_player(source, lang=lang), expected)
            self.assertEqual(runtime.adapt_model_player(expected, lang=lang), expected)
        self.assertEqual(runtime.adapt_model_player('const unrelated=1;', lang='es'), 'const unrelated=1;')

    def test_changed_owner_or_partial_geometry_is_rejected(self):
        source = self.source()
        for old, new in [("host.querySelector('.mc-frame-figure')", "host.querySelector('.other')"),
                         ('155+rows[0].length*94', '156+rows[0].length*94'),
                         ('width:88,height:35', 'width:89,height:35'),
                         ('x:150+j*94+43', 'x:150+j*94+42'),
                         ('x:150+j*94+44', 'x:150+j*94+45')]:
            with self.subTest(old=old), self.assertRaisesRegex(runtime.RuntimeStringError, 'layout'):
                runtime.adapt_model_player(source.replace(old, new), lang='es')
        final = runtime.adapt_model_player(source, lang='es')
        with self.assertRaisesRegex(runtime.RuntimeStringError, 'layout'):
            runtime.adapt_model_player(final.replace('width:112,height:35', 'width:88,height:35'), lang='es')

    def test_inline_localizer_passes_the_language_to_the_model_adapter(self):
        source = self.source()
        mapping = {item['zh']: 'Etiqueta' for item in runtime.scan_js(source)}
        mapping['：'] = ':'
        expected = runtime.adapt_model_player(runtime.render_script(source, runtime.scan_js(source), mapping, lang='es'), lang='es')
        self.assertEqual(runtime.localize_js(source, mapping, lang='es'), expected)

    def test_runtime_preparation_passes_the_language_to_the_model_adapter(self):
        helper = runtime_fixture.RuntimeJapaneseTests()
        self.addCleanup(helper.doCleanups)
        root = helper.fixture()
        mapping = {'位置': 'Posición', '第': 'Fila', '行': 'fila', '位置2': 'Posición 2',
                   '编号2': 'Número 2', '说明\\n继续': 'Nota\\nContinuar', '允许': 'Permitir',
                   '禁止': 'Prohibir', '播放': 'Reproducir', '特征': 'Característica',
                   '：': ':', '暂停': 'Pausar', runtime_fixture.HINT: latin_fixture.HINTS['es']}
        table_path = root / runtime.TABLE
        table = json.loads(table_path.read_text())
        for source, row in table['s'].items():
            row['es'] = mapping[source]
        table['s'][runtime.HINT_TIP_SOURCE] = {'id': 30116, 'es': 'Busca palabras o conceptos.'}
        table_path.write_text(json.dumps(table, ensure_ascii=False))
        bundle_path = root / runtime.BUNDLE
        source = bundle_path.read_text()
        document, start, end = runtime._bundle(source)
        document['zh-CN'][runtime.HINT_TIP_KEY] = runtime.HINT_TIP_SOURCE
        document['es'] = {runtime.HINT_KEY: 'old Spanish', runtime.HINT_TIP_KEY: 'old quick hint'}
        bundle_path.write_text(source[:start] + json.dumps(document, ensure_ascii=False) + source[end:])
        (root / runtime.REGISTRY).write_text(json.dumps(runtime.inventory(root), ensure_ascii=False))
        output = runtime.prepare('es', root)['es/assets/model-player.js']
        self.assertIn('Math.max(660,255+rows[0].length*118)', output)
        self.assertIn('`Característica ${j}`', output)

    def test_complete_builder_inline_player_uses_spanish_geometry(self):
        helper = latin_fixture.EditionLatinTests()
        self.addCleanup(helper.doCleanups)
        root = helper.complete_fixture('es')
        source = (root / 'complete.html').read_text()
        model = ('const frames=window.MODEL_FRAMES||[];'
                 "const groups=available.filter(g=>requested.some(r=>g.includes(r)));"
                 "host.querySelector('.mc-frame-figure');"
                 'const w=Math.max(660,155+rows[0].length*94);'
                 'node({x:150+j*94+43,y:28});'
                 'node({x:150+j*94,y:42+t*46,width:88,height:35});'
                 'node({x:150+j*94+44,y:66+t*46});')
        source = source.replace('</body>', '<script>' + model + '</script></body>')
        (root / 'complete.html').write_text(source)
        (root / complete_strings.REGISTRY).write_text(json.dumps(complete_strings.inventory(root), ensure_ascii=False))
        output, proof = build_complete.Builder(root, 'es').prepare()
        self.assertIn('Math.max(660,255+rows[0].length*118)', output)
        self.assertIn('x:250+j*118,y:42+t*46,width:112,height:35', output)
        self.assertEqual(proof['pages'], 250)


if __name__ == '__main__':
    unittest.main()
