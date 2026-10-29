"""Finite offline continuous-edition fixtures; never publish repository output."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import build_complete as complete
import complete_strings as strings
import gen_assets
import table as translation_table


LABELS = {
    '连续阅读': ('Continuous reading', '連続して読む'),
    '播放': ('Play', '再生'),
    '资源': ('Resources', 'リソース'),
    '下载': ('Download', 'ダウンロード'),
    '第': ('Row', '第'),
    '行': ('row', '行'),
}


class CompleteJapaneseTests(unittest.TestCase):
    def fixture(self):
        temporary = tempfile.TemporaryDirectory(prefix='complete-ja-test-')
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        for directory in ('i18n', 'editorial', 'assets', 'en/assets', 'ja/assets'):
            (root / directory).mkdir(parents=True)
        canonical = [dict(path='page%03d.html' % n, id='page%03d' % n) for n in range(250)]
        sections = ['<section class="standalone-section" id="%s" data-book-page="%s"></section>'
                    % (item['id'], item['path']) for item in canonical]
        sections.extend('<section class="standalone-section" id="%s"></section>'
                        % identity for identity in complete.SUPPLEMENTS)
        sections.append('<section class="standalone-section" id="embedded-resources">'
                        '<h1>资源</h1><section><h2>example.txt</h2>'
                        '<a download="example.txt">下载</a></section></section>')
        source = ('<!doctype html><html lang="zh-CN"><head><title>连续阅读</title>'
                  '<style>/*i18n-css:begin*//*i18n-css:end*/</style></head><body>'
                  '<button data-i18n="control">播放</button><main id="main-content">'
                  + ''.join(sections) + '</main>'
                  '<script>window.I18N_META={};</script>'
                  '<script>window.COURSE_SEARCH=[];</script>'
                  '<script>// Interface localisation.\nwindow.edition="zh-CN";</script>'
                  '<script>const n=2; const row=`第${n}行`;</script></body></html>')
        (root / 'complete.html').write_text(source)
        (root / 'editorial/canonical-pages.json').write_text(json.dumps(canonical))
        (root / 'assets/i18n.css').write_text('body{color:#123}')
        (root / 'example.txt').write_text('raw data 0.125\n')
        for lang in ('en', 'ja'):
            base = root / lang
            (base / 'index.html').write_text('<html lang="%s"><head>'
                '<meta name="i18n-scope" content="%s"></head></html>' %
                (lang, '日本語の本文と界面' if lang == 'ja' else 'English body and interface'))
            bundle = {lang: {'control': '再生中' if lang == 'ja' else 'Playing',
                             'disclose.source': 'ソース' if lang == 'ja' else 'Source'}}
            (base / 'assets/i18n-data.js').write_text(
                'window.I18N_META={};window.I18N_STRINGS=' + json.dumps(bundle, ensure_ascii=False) + ';')
            (base / 'assets/i18n.js').write_text('window.edition="%s";' % lang)
            (base / 'assets/search-data.js').write_text(
                'window.COURSE_SEARCH=[{"path":"page000.html#heading"}];')
            for page in list(item['path'] for item in canonical) + list(complete.SUPPLEMENTS.values()):
                path = base / page
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('<article><h1 id="heading">%s</h1>'
                    '<label for="field">0.125</label><input id="field" aria-describedby="heading">'
                    '<svg viewBox="0 0 10 10"><defs><clipPath id="clip"><rect width="2.5" height="8"/>'
                    '</clipPath></defs><g clip-path="url(#clip)"><text x="2" y="3">0.125</text></g></svg>'
                    '<details class="quiz-answer"><summary>?</summary>0.125</details>'
                    '<details open><summary>steps</summary><pre><code>x = 0.125\n</code></pre></details>'
                    '<a href="%spage000.html#heading">link</a><a href="%s../example.txt" download>data</a>'
                    '</article>' % ('日本語の本文' if lang == 'ja' else 'English article',
                                    '../' if '/' in page else '', '../' if '/' in page else ''))
        registry = strings.inventory(root)
        rows = {}
        for identity, item in enumerate(registry['items']):
            en, ja = LABELS[item['zh']]
            rows[item['zh']] = dict(id=identity, en=en, ja=ja)
        (root / strings.REGISTRY).write_text(json.dumps(registry, ensure_ascii=False))
        (root / 'i18n/table.json').write_text(json.dumps({'s': rows}, ensure_ascii=False))
        return root

    def test_japanese_assembly_uses_edition_and_preserves_article_contracts(self):
        root = self.fixture()
        before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
        output, proof = complete.Builder(root, 'ja').prepare()
        self.assertIn('<html lang="ja">', output)
        self.assertIn('content="日本語の本文と界面"', output)
        self.assertIn('<title>連続して読む</title>', output)
        self.assertIn('>再生中</button>', output)
        self.assertIn('window.edition="ja";', output)
        self.assertIn('`第${n}行`', output)
        self.assertNotIn('`第 ${n} 行`', output)
        self.assertIn('for="page000--field"', output)
        self.assertIn('aria-describedby="page000--heading"', output)
        self.assertIn('clip-path="url(#page000--clip)"', output)
        self.assertIn('x = 0.125\n', output)
        self.assertIn('>ダウンロード</a>', output)
        self.assertIn('data:text/plain;base64,', output)
        self.assertEqual((proof['pages'], proof['standalone_sections'], proof['open_quiz_answers']), (250, 253, 0))
        self.assertEqual(len(proof['article_proofs']), 252)
        self.assertTrue(all(p['text_unchanged'] and p['code_unchanged'] and p['svg_geometry_unchanged']
                            for p in proof['article_proofs']))
        self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()})
        self.assertEqual(output, complete.Builder(root, 'ja').prepare()[0])

    def test_english_default_keeps_template_spacing(self):
        output, _ = complete.Builder(self.fixture()).prepare()
        self.assertIn('<html lang="en">', output)
        self.assertIn('content="English body and interface"', output)
        self.assertIn('`Row ${n} row`', output)

    def test_japanese_check_defaults_to_selected_edition_without_writing(self):
        root = self.fixture()
        output, _ = complete.Builder(root, 'ja').prepare()
        (root / 'ja/complete.html').write_text(output)
        before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
        with patch.object(complete, 'ROOT', root), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(complete.main(['--lang=ja', '--check']), 0)
        self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_interface_bundle_keys_and_scope_are_required(self):
        root = self.fixture()
        bundle = root / 'ja/assets/i18n-data.js'
        bundle.write_text('window.I18N_STRINGS={"ja":{"disclose.source":"ソース"}};')
        with self.assertRaisesRegex(strings.CompleteError, 'missing interface fallback: control'):
            complete.Builder(root, 'ja')
        for scope in ('', '<meta name="i18n-scope" content="">',
                      '<meta name="i18n-scope" content="本文"><meta name="i18n-scope" content="重複">'):
            with self.subTest(scope=scope), self.assertRaises(strings.CompleteError):
                complete.edition_scope('<html><head></head></html>', '<html><head>' + scope + '</head></html>')

    def test_stale_and_missing_translation_are_rejected(self):
        root = self.fixture()
        table_path = root / 'i18n/table.json'
        table = json.loads(table_path.read_text())
        del table['s']['下载']['ja']
        table_path.write_text(json.dumps(table))
        with self.assertRaisesRegex(strings.CompleteError, 'missing complete translations'):
            complete.Builder(root, 'ja')
        (root / 'complete.html').write_text((root / 'complete.html').read_text() + '\n')
        with self.assertRaisesRegex(strings.CompleteError, 'registry is stale'):
            strings.translations(root, 'ja')

    def test_markup_offsets_and_nonempty_values_remain_protected(self):
        source = '<title>连续阅读</title>'
        registry = dict(sha256=strings.sha(source), items=[dict(owner='shell', kind='text',
            start=7, end=11, zh='连续阅读')])
        self.assertEqual(strings.localize_shell(source, registry, {'连续阅读': '連続して読む'}, lang='ja'),
                         '<title>連続して読む</title>')
        for value in ('', '<b>連続して読む</b>'):
            with self.subTest(value=value), self.assertRaises(strings.CompleteError):
                strings.localize_shell(source, registry, {'连续阅读': value}, lang='ja')
        with self.assertRaisesRegex(strings.CompleteError, 'offset drift'):
            strings.localize_shell(source + ' ', registry, {'连续阅读': '連続して読む'}, lang='ja')

    def test_selected_output_and_diagnostic_boundaries(self):
        self.assertEqual(complete.output_path(None, default=complete.ROOT / 'ja/complete.html', lang='ja'),
                         complete.ROOT / 'ja/complete.html')
        for lang, destination in [('ja', 'en/complete.html'), ('en', 'ja/complete.html'),
                                  ('ja', 'complete.html'), ('zh-CN', 'en/complete.html')]:
            with self.subTest(lang=lang, destination=destination), self.assertRaises(strings.CompleteError):
                complete.output_path(str(complete.ROOT / destination), lang=lang)
        self.assertTrue(complete.is_temporary(complete.output_path('/tmp/ja-fixture.html', lang='ja')))
        for lang in ('fr', '../en'):
            with self.subTest(lang=lang), self.assertRaises(strings.CompleteError):
                complete.Builder(lang=lang)
            with self.assertRaises(strings.CompleteError):
                strings.translations(lang=lang)
            with self.assertRaises(strings.CompleteError):
                strings.export(lang=lang)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(complete.main(['--diagnose-zh']), 1)
            self.assertEqual(complete.main(['--diagnose-zh', '--output', str(complete.ROOT / 'ja/complete.html')]), 1)

    def test_invalid_search_and_open_quiz_reject_assembly(self):
        root = self.fixture()
        search = root / 'ja/assets/search-data.js'
        search.write_text('window.COURSE_SEARCH=[{"path":"page000.html#missing"}];')
        with self.assertRaisesRegex(strings.CompleteError, 'stale .* search anchor'):
            complete.Builder(root, 'ja').prepare()
        search.write_text('window.COURSE_SEARCH=[{"path":"page000.html#heading"}];')
        page = root / 'ja/page000.html'
        page.write_text(page.read_text().replace('<details class="quiz-answer">', '<details class="quiz-answer" open>'))
        with self.assertRaisesRegex(strings.CompleteError, 'quiz answer is initially open'):
            complete.Builder(root, 'ja').prepare()


class CatalogJapaneseTests(unittest.TestCase):
    def test_bare_title_uses_current_translated_book_name_and_keeps_english_bytes(self):
        with tempfile.TemporaryDirectory(prefix='catalog-ja-test-') as directory:
            root = Path(directory)
            (root / 'i18n/units').mkdir(parents=True)
            (root / 'assets').mkdir()
            source_title = 'Agent与工程机制：证据、知识关系与覆盖'
            source = [dict(title=source_title, path='engineering/agent-evidence.html', kind='机制')]
            table = {'AI 系统工程': {'en': 'AI Systems Engineering', 'ja': 'AIシステム工学'},
                     '机制': {'en': 'Mechanism', 'ja': '仕組み'},
                     source_title + ' · AI系统工程': {
                         'en': 'Agents and engineering mechanisms · AI Systems Engineering',
                         'ja': 'Agentとエンジニアリングの仕組み · AIシステム工学'}}
            (root / 'assets/catalog.js').write_text('window.BOOK_CATALOG=' + json.dumps(source) + ';')
            (root / 'i18n/table.json').write_text(json.dumps({'s': table}))
            # Config names the sources; obsolete translated values have no authority.
            (root / 'i18n/catalog-kinds.json').write_text(json.dumps({'机制': {'en': 'obsolete'}}))
            for lang, title, kind in [('en', 'Agents and engineering mechanisms', 'Mechanism'),
                                      ('ja', 'Agentとエンジニアリングの仕組み', '仕組み')]:
                with self.subTest(lang=lang), patch.object(gen_assets, 'ROOT', root), patch.object(gen_assets, 'LANG', lang):
                    with contextlib.redirect_stdout(io.StringIO()):
                        gen_assets.main()
                    expected = 'window.BOOK_CATALOG=' + json.dumps(
                        [dict(title=title, path=source[0]['path'], kind=kind)], ensure_ascii=False) + ';\n'
                    self.assertEqual((root / lang / 'assets/catalog.js').read_text(), expected)

    def test_missing_invalid_and_unregistered_kinds_stop_before_outputs(self):
        for value in (None, '', '   ', 7, '仕組み'):
            with self.subTest(value=value), tempfile.TemporaryDirectory(prefix='catalog-kind-test-') as directory:
                root = Path(directory)
                (root / 'i18n').mkdir()
                (root / 'assets').mkdir()
                (root / 'i18n/catalog-kinds.json').write_text(json.dumps({'机制': {'ja': '旁表不回退'}}))
                rows = {'AI 系统工程': {'ja': 'AIシステム工学'}}
                if value is not None:
                    rows['机制'] = {'ja': value}
                (root / 'i18n/table.json').write_text(json.dumps({'s': rows}))
                kind = '未知分类' if value == '仕組み' else '机制'
                (root / 'assets/catalog.js').write_text('window.BOOK_CATALOG=' + json.dumps(
                    [dict(title='API', path='example.html', kind=kind)]) + ';')
                with patch.object(gen_assets, 'ROOT', root), patch.object(gen_assets, 'LANG', 'ja'):
                    with self.assertRaisesRegex(ValueError, 'catalogue kind'):
                        gen_assets.main()
                self.assertFalse((root / 'ja').exists())


class CatalogSourceRegistrationTests(unittest.TestCase):
    def test_registered_sources_reconcile_without_changing_existing_identity_or_languages(self):
        with tempfile.TemporaryDirectory(prefix='catalog-source-test-') as directory:
            root = Path(directory)
            (root / 'i18n').mkdir()
            kinds = ['专题与参考', '参考资料', '实验与来源', '实验附录', '工程深挖', '课程', '阅读指南']
            config = {'_note': 'Metadata is not a translatable source'}
            config.update({kind: {'en': 'historical English'} for kind in kinds})
            (root / 'i18n/catalog-kinds.json').write_text(json.dumps(config))
            document = {'version': 5, 'next_id': 1000, 'metadata': {'preserve': ['all']}, 's': {
                '参考资料': {'id': 17, 'en': 'References', 'ja': '参考資料', 'n': 80, 'p': 30},
                '实验与来源': {'id': 23, 'en': 'Experiments and sources', 'ja': '実験と出典'},
                '工程深挖': {'id': 42, 'en': 'Engineering deep dive', 'ja': 'エンジニアリング詳解'},
                'retired': {'id': 99, 'en': 'Keep', 'ja': '保持', 'custom': 'owner data'}}}
            original = json.loads(json.dumps(document))
            data = {'参考资料': {'n': 2, 'pages': {'assets/visual-data.js'}}}
            with patch('data_strings.source_counts', return_value=data):
                counts = translation_table.auxiliary_counts(root)
            self.assertEqual(set(counts), set(kinds))
            for kind in kinds:
                self.assertIn('i18n/catalog-kinds.json', counts[kind]['pages'])
                self.assertEqual(counts[kind]['n'], 3 if kind == '参考资料' else 1)
            added, first = translation_table.reconcile(document, {
                '参考资料': {'n': 5, 'pages': {'sources.html'}}}, counts)
            self.assertEqual((added, first, document['next_id']), (4, 1000, 1004))
            self.assertEqual(document['metadata'], original['metadata'])
            self.assertEqual(document['version'], 5)
            for source, row in original['s'].items():
                for field, value in row.items():
                    if field not in ('n', 'p', 'data_n'):
                        self.assertEqual(document['s'][source][field], value)
            self.assertEqual((document['s']['参考资料']['n'], document['s']['参考资料']['p'],
                              document['s']['参考资料']['data_n']), (8, 3, 3))
            self.assertEqual([document['s'][kind]['id'] for kind in kinds if kind not in original['s']],
                             [1000, 1001, 1002, 1003])
            snapshot = json.loads(json.dumps(document))
            self.assertEqual(translation_table.reconcile(document, {
                '参考资料': {'n': 5, 'pages': {'sources.html'}}}, counts), (0, 1004))
            self.assertEqual(document, snapshot)

    def test_existing_highest_id_overrides_stale_next_id(self):
        document = {'next_id': 3, 's': {'old': {'id': 90, 'ja': '保持'}}}
        translation_table.reconcile(document, {}, {'课程': {'n': 1, 'pages': {'i18n/catalog-kinds.json'}}})
        self.assertEqual(document['s']['old']['id'], 90)
        self.assertEqual((document['s']['课程']['id'], document['next_id']), (91, 92))


if __name__ == '__main__':
    unittest.main()
