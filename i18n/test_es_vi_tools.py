"""Finite ES/VI edition controls; only temporary fixtures are mutated."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import apply
import build_complete as complete
import complete_strings
import figure_layout as layout
import figure_strings as figures
import gen_assets
import runtime_strings as runtime
import test_complete_ja as complete_fixture


HINTS = {
    'es': 'Busca por texto, lección o pregunta: tensor, Lección 39, Q001.',
    'vi': 'Tìm theo văn bản, bài học hoặc câu hỏi: tensor, Bài 39, Q001.',
}
LABELS = {
    'es': {'连续阅读': 'Lectura continua', '播放': 'Reproducir', '资源': 'Recursos',
           '下载': 'Descargar', '第': 'Fila', '行': 'fila'},
    'vi': {'连续阅读': 'Đọc liên tục', '播放': 'Phát', '资源': 'Tài nguyên',
           '下载': 'Tải xuống', '第': 'Hàng', '行': 'hàng'},
}


class EditionLatinTests(unittest.TestCase):
    def test_first_build_keeps_all_declared_js_assets_local(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(apply, 'ROOT', Path(directory)):
            for lang in HINTS:
                with patch.object(apply, 'LANG', lang):
                    for asset in apply.EDITION_ASSETS:
                        markup = '<script src="../../%s?v=2#x"></script>' % asset
                        self.assertEqual(apply.relink(markup, 'studies/code/a.html', set()), markup)
                    self.assertEqual(apply.relink('<link href="assets/style.css">', 'index.html', set()),
                                     '<link href="../assets/style.css">')

    def test_runtime_selected_hint_and_template_spacing_keep_code(self):
        original_hint = '输入中文、英文、课号或题号，例如：张量、第39课、Q001。'
        source = 'window.I18N_META={"editions":["zh-CN","en","ja"]};\nwindow.I18N_STRINGS=' + json.dumps(
            {lang: {runtime.HINT_KEY: original_hint if lang == 'zh-CN' else 'old', 'other': lang}
             for lang in ('zh-CN', 'en', 'ja', 'es', 'vi')}, ensure_ascii=False) + ';\n'
        before, _, _ = runtime._bundle(source)
        for lang, hint in HINTS.items():
            result = runtime.render_bundle(source, hint, lang=lang)
            after, _, _ = runtime._bundle(result)
            expected = json.loads(json.dumps(before))
            expected[lang][runtime.HINT_KEY] = hint
            self.assertEqual(after, expected)
            self.assertEqual(result.split('window.I18N_STRINGS=')[0], source.split('window.I18N_STRINGS=')[0])
            word = 'carácter' if lang == 'es' else 'vị'
            script = 'const n=2; const label=`位置${n}位置`; const raw="我";'
            output = runtime.localize_js(script, {'位置': word}, lang=lang)
            self.assertIn('`%s ${n} %s`' % (word, word), output)
            self.assertEqual(runtime.code_signature(script), runtime.code_signature(output))
            with self.assertRaisesRegex(runtime.RuntimeStringError, 'page-search hint'):
                runtime.render_bundle(source, hint.replace('tensor', 'matrix'), lang=lang)

    def test_runtime_protections_apply_to_both_latin_languages(self):
        for lang in HINTS:
            runtime.validate_translation('位置2\\n允许API()', 'Vị trí 2\\nAPI()', lang=lang)
            for value, error in [('位置2\\nAPI()', 'Chinese'),
                                 ('Vị trí 3\\nAPI()', 'numeric/code'),
                                 ('Vị trí 2 API()', 'control escapes'),
                                 ('Vị trí 2\\nAPI[]', 'numeric/code')]:
                with self.subTest(lang=lang, value=value), self.assertRaisesRegex(runtime.RuntimeStringError, error):
                    runtime.validate_translation('位置2\\n允许API()', value, lang=lang)

    def test_latin_seams_cover_accents_without_changing_opaque_code(self):
        for lang, value in [('es', 'obtención'), ('vi', 'vị'), ('vi', 'vi\u0323')]:
            source = value + '<code>API</code>' + value + ',<a>éxito</a><pre>' + value + '<b>API</b></pre>'
            expected = value + ' <code>API</code> ' + value + ', <a>éxito</a><pre>' + value + '<b>API</b></pre>'
            self.assertEqual(apply.space_seams(source, lang=lang), expected)

    def test_latin_figures_wrap_words_and_preserve_literals(self):
        source = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 100">'
                  '<rect x="10" y="10" width="220" height="80" fill="#eaf0f5"/>'
                  '<text x="20" y="40" font-size="16">检查API()位置2 · 我</text>'
                  '<text x="20" y="70" font-size="16">0.25</text></svg>')
        for lang, text in [('es', 'Comprobar API() en la posición 2 · 我'),
                           ('vi', 'Kiểm tra API() tại vị trí 2 · 我')]:
            mapping = {'检查API()位置2 · 我': text}
            figures.validate_translation('检查API()位置2 · 我', text, lang=lang)
            proof = {}
            output = layout.reflow(source, mapping, mapping.__getitem__, proof, lang=lang)
            self.assertIn('0.25', output)
            self.assertEqual(layout.geometry_identity(layout.parse(source)), layout.geometry_identity(layout.parse(output)))
            self.assertTrue(all(line['width'] <= line['limit'] + .01 for line in proof['text_fit']))
            self.assertEqual(' '.join(layout.wrap('vị trí API() W_q run.json', 65, lang=lang)),
                             'vị trí API() W_q run.json')
            decomposed = 'đo\u0323̂ chi\u0301nh xa\u0301c'
            self.assertEqual(' '.join(layout.wrap(decomposed, 55, lang=lang)), decomposed)
            for bad, error in [(text.replace('2', '3'), 'numeric'),
                               (text.replace('API()', 'API[]'), 'identifiers'),
                               (text.replace('我', ''), 'vocabulary'),
                               ('检查API()位置2 · 我', 'untranslated')]:
                with self.assertRaisesRegex(figures.FigureError, error):
                    figures.validate_translation('检查API()位置2 · 我', bad, lang=lang)

    def complete_fixture(self, lang):
        helper = complete_fixture.CompleteJapaneseTests()
        self.addCleanup(helper.doCleanups)
        root = helper.fixture()
        shutil.copytree(root / 'en', root / lang)
        base = root / lang
        scope = 'Texto e interfaz en español' if lang == 'es' else 'Nội dung và giao diện tiếng Việt'
        (base / 'index.html').write_text('<html lang="%s"><head><meta name="i18n-scope" content="%s"></head></html>' % (lang, scope))
        (base / 'assets/i18n.js').write_text('window.edition="%s";' % lang)
        (base / 'assets/i18n-data.js').write_text('window.I18N_META={};window.I18N_STRINGS=' +
            json.dumps({lang: {'control': LABELS[lang]['播放'], 'disclose.source': 'Fuente' if lang == 'es' else 'Nguồn'}}, ensure_ascii=False) + ';')
        table_path = root / 'i18n/table.json'
        table = json.loads(table_path.read_text())
        for source, row in table['s'].items():
            row[lang] = LABELS[lang][source]
        table_path.write_text(json.dumps(table, ensure_ascii=False))
        return root

    def test_complete_selects_language_and_preserves_articles_read_only(self):
        for lang in HINTS:
            root = self.complete_fixture(lang)
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            output, proof = complete.Builder(root, lang).prepare()
            self.assertIn('<html lang="%s">' % lang, output)
            self.assertIn('<title>%s</title>' % LABELS[lang]['连续阅读'], output)
            self.assertIn('window.edition="%s";' % lang, output)
            self.assertIn('>%s</a>' % LABELS[lang]['下载'], output)
            self.assertIn('`%s ${n} %s`' % (LABELS[lang]['第'], LABELS[lang]['行']), output)
            self.assertEqual((proof['pages'], proof['standalone_sections'], proof['open_quiz_answers']), (250, 253, 0))
            self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()})
            self.assertEqual(output, complete.Builder(root, lang).prepare()[0])
            with patch.object(complete, 'ROOT', root):
                self.assertEqual(complete.output_path(None, default=root / lang / 'complete.html', lang=lang), (root / lang / 'complete.html').resolve())

    def test_complete_invalid_destinations_and_untranslated_shell_are_rejected(self):
        for lang in HINTS:
            with self.assertRaises(complete_strings.CompleteError):
                complete.output_path(str(complete.ROOT / 'complete.html'), lang=lang)
            other = 'vi' if lang == 'es' else 'es'
            with self.assertRaises(complete_strings.CompleteError):
                complete.output_path(str(complete.ROOT / other / 'complete.html'), lang=lang)
            source = '<title>连续阅读</title>'
            registry = dict(sha256=complete_strings.sha(source), items=[dict(owner='shell', kind='text', start=7, end=11, zh='连续阅读')])
            with self.assertRaisesRegex(complete_strings.CompleteError, 'invalid complete shell'):
                complete_strings.localize_shell(source, registry, {'连续阅读': '连续阅读'}, lang=lang)
        for lang in ('fr', '../en'):
            for operation in (runtime._language, figures._language, complete_strings.translation_language):
                with self.assertRaises(ValueError):
                    operation(lang)

    def test_catalog_bare_titles_use_each_editions_table_bookname(self):
        for lang, name in [('es', 'Ingeniería de sistemas de IA'), ('vi', 'Kỹ thuật hệ thống AI')]:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for subdir in ('i18n/units', 'assets'):
                    (root / subdir).mkdir(parents=True)
                (root / 'i18n/catalog-kinds.json').write_text('{"机制": {"en": "obsolete"}}')
                (root / 'i18n/table.json').write_text(json.dumps({'s': {'AI 系统工程': {lang: name}, '机制': {lang: 'Mecanismo'},
                    '测试 · AI系统工程': {lang: 'Prueba · ' + name}}}, ensure_ascii=False))
                (root / 'assets/catalog.js').write_text('window.BOOK_CATALOG=[{"title":"测试","path":"test.html","kind":"机制"}];')
                with patch.object(gen_assets, 'ROOT', root), patch.object(gen_assets, 'LANG', lang), contextlib.redirect_stdout(io.StringIO()):
                    gen_assets.main()
                result = json.loads((root / lang / 'assets/catalog.js').read_text().split('=', 1)[1].rstrip(';\n'))
                self.assertEqual(result[0]['title'], 'Prueba')


if __name__ == '__main__':
    unittest.main()
