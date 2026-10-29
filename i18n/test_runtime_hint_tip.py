"""Selected ES/VI quick-search hints; finite temporary fixtures only."""
import json
from pathlib import Path
import unittest

import runtime_strings as runtime
import test_runtime_strings_ja as fixture


TIP_KEY = 'search.hintTip'
TIP_SOURCE = '可以搜索中文、英文、课号或概念。'
HINTS = {'es': 'Busca tensor, Lección 39, Q001.',
         'vi': 'Tìm tensor, Bài 39, Q001.'}
TIPS = {'es': 'Puedes buscar palabras del texto, números de lección o conceptos.',
        'vi': 'Có thể tìm từ trong nội dung, số bài hoặc khái niệm.'}


class RuntimeHintTipTests(unittest.TestCase):
    def source(self):
        document = {lang: {runtime.HINT_KEY: fixture.HINT if lang == 'zh-CN' else 'old page ' + lang,
                           TIP_KEY: TIP_SOURCE if lang == 'zh-CN' else 'old quick ' + lang,
                           'other': 'keep ' + lang}
                    for lang in ('zh-CN', 'en', 'ja', 'es', 'vi')}
        return ('window.I18N_META={"keep":"metadata"};\nwindow.I18N_STRINGS='
                + json.dumps(document, ensure_ascii=False, indent=2) + ';\n')

    def test_selected_two_keys_only_and_exact_other_bytes(self):
        source = self.source()
        for lang in HINTS:
            output = runtime.render_bundle(source, HINTS[lang], lang=lang, hint_tip=TIPS[lang])
            expected = source.replace(json.dumps('old page ' + lang), json.dumps(HINTS[lang], ensure_ascii=False))
            expected = expected.replace(json.dumps('old quick ' + lang), json.dumps(TIPS[lang], ensure_ascii=False))
            self.assertEqual(output, expected)
            self.assertEqual(runtime.render_bundle(output, HINTS[lang], lang=lang, hint_tip=TIPS[lang]), output)
            self.assertIn(json.dumps(TIP_SOURCE, ensure_ascii=False), output)

    def test_missing_changed_source_and_missing_selected_key_stop(self):
        for lang in HINTS:
            for owner, operation in [('zh-CN', 'missing'), ('zh-CN', 'changed'), (lang, 'missing')]:
                source = self.source()
                document, begin, end = runtime._bundle(source)
                if operation == 'missing':
                    del document[owner][TIP_KEY]
                else:
                    document[owner][TIP_KEY] = '新的中文提示。'
                source = source[:begin] + json.dumps(document, ensure_ascii=False) + source[end:]
                with self.subTest(lang=lang, owner=owner, operation=operation):
                    with self.assertRaisesRegex(runtime.RuntimeStringError, 'quick-search hint'):
                        runtime.render_bundle(source, HINTS[lang], lang=lang, hint_tip=TIPS[lang])

    def test_invalid_tip_rejected_without_widening_protections(self):
        for lang in HINTS:
            for tip in ('', 3, TIP_SOURCE, 'A new numeric 2', 'raw\nnewline'):
                with self.subTest(lang=lang, tip=tip), self.assertRaises(runtime.RuntimeStringError):
                    runtime.render_bundle(self.source(), HINTS[lang], lang=lang, hint_tip=tip)

    def test_omitted_tip_retains_legacy_single_key_behavior(self):
        source = self.source()
        for lang, hint in [('en', fixture.EN_HINT), ('ja', fixture.JA_HINT), *HINTS.items()]:
            output = runtime.render_bundle(source, hint, lang=lang)
            self.assertEqual(output, source.replace(json.dumps('old page ' + lang), json.dumps(hint, ensure_ascii=False)))

    def fixture(self):
        helper = fixture.RuntimeJapaneseTests()
        self.addCleanup(helper.doCleanups)
        root = helper.fixture()
        (root / runtime.BUNDLE).write_text(self.source())
        registry = runtime.inventory(root)
        (root / runtime.REGISTRY).write_text(json.dumps(registry, ensure_ascii=False))
        table_path = root / runtime.TABLE
        table = json.loads(table_path.read_text())
        # Generic translated labels exercise all real scripts without coupling
        # this quick-search fixture to a complete translation catalogue.
        for source, row in table['s'].items():
            for lang in HINTS:
                row[lang] = HINTS[lang] if source == fixture.HINT else row['en']
        table['s'][TIP_SOURCE] = {'id': 30116, 'es': TIPS['es'], 'vi': TIPS['vi']}
        table_path.write_text(json.dumps(table, ensure_ascii=False))
        return root

    def test_prepare_uses_canonical_selected_table_tip_without_writes(self):
        root = self.fixture()
        before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
        for lang in HINTS:
            outputs = runtime.prepare(lang, root)
            document, _, _ = runtime._bundle(outputs[lang + '/' + runtime.BUNDLE])
            self.assertEqual(document[lang][runtime.HINT_KEY], HINTS[lang])
            self.assertEqual(document[lang][TIP_KEY], TIPS[lang])
            original, _, _ = runtime._bundle((root / runtime.BUNDLE).read_text())
            for other in set(original) - {lang}:
                self.assertEqual(document[other], original[other])
        self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()})
        table_path = root / runtime.TABLE
        table = json.loads(table_path.read_text())
        del table['s'][TIP_SOURCE]['es']
        table_path.write_text(json.dumps(table, ensure_ascii=False))
        with self.assertRaisesRegex(runtime.RuntimeStringError, '缺运行时译文'):
            runtime.prepare('es', root)
        self.assertFalse((root / 'es').exists())


if __name__ == '__main__':
    unittest.main()
