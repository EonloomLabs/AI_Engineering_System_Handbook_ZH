"""Finite, offline checks for the runtime adapter; never publish book assets."""

import contextlib
import io
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

import runtime_strings as runtime


HINT = '输入中文、英文、课号或题号，例如：张量、第39课、Q001。'
EN_HINT = 'Enter English text, a lesson number or a question ID, e.g. tensor, Lesson 39, Q001.'
JA_HINT = '日本語・英語・課番号・問題番号で検索できます。例：テンソル、第39課、Q001。'
LABELS = {
    '位置': ('Position', '位置'),
    '第': ('Row', '第'),
    '行': ('row', '行'),
    '位置2': ('Position 2', '位置2'),
    '编号2': ('Number 2', '番号2'),
    '说明\\n继续': ('Note\\nContinue', '説明\\n続き'),
    '允许': ('Allow', '許可'),
    '禁止': ('Forbid', '禁止'),
    '播放': ('Play', '再生'),
    '特征': ('Feature', '特徴'),
    '：': (':', '：'),
    '暂停': ('Pause', '一時停止'),
}


class RuntimeJapaneseTests(unittest.TestCase):
    def fixture(self):
        temporary = tempfile.TemporaryDirectory(prefix='runtime-ja-test-')
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / 'assets').mkdir()
        (root / 'i18n').mkdir()
        source_root = runtime.ROOT
        for rel in runtime.FILES:
            # Exercise the real selector/layout and edition-notice owners.
            if rel in ('assets/model-player.js', 'assets/i18n.js'):
                text = (source_root / rel).read_text(encoding='utf-8')
            else:
                text = ("const count=2; const label='位置'; const row=`第${count}行`; "
                        "const html='<span data-key=\"原键\" title=\"位置2\">编号2</span>'; "
                        "const note='说明\\n继续';\n")
            (root / rel).write_text(text, encoding='utf-8')
        bundle = {
            'zh-CN': {runtime.HINT_KEY: HINT, 'other': '原文'},
            'en': {runtime.HINT_KEY: 'old English', 'other': 'Keep English'},
            'ja': {runtime.HINT_KEY: '元の検索例', 'other': '日本語のまま'},
        }
        (root / runtime.BUNDLE).write_text(
            'window.I18N_META={"editions":["zh-CN"]};\nwindow.I18N_STRINGS='
            + json.dumps(bundle, ensure_ascii=False) + ';\n', encoding='utf-8')
        registry = runtime.inventory(root)
        rows = {}
        for index, item in enumerate(registry['items'], 1):
            source = item['zh']
            en, ja = (EN_HINT, JA_HINT) if source == HINT else LABELS[source]
            rows[source] = {'id': index, 'en': en, 'ja': ja}
        (root / runtime.REGISTRY).write_text(json.dumps(registry, ensure_ascii=False), encoding='utf-8')
        (root / runtime.TABLE).write_text(json.dumps({'s': rows}), encoding='utf-8')
        return root

    def test_prepare_japanese_uses_table_and_keeps_machine_fields(self):
        root = self.fixture()
        before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
        outputs = runtime.prepare('ja', root)
        self.assertEqual(set(outputs), {'ja/' + rel for rel in (*runtime.FILES, runtime.BUNDLE)})
        example = outputs['ja/assets/app.js']
        self.assertIn('`第${count}行`', example)
        self.assertIn('data-key="原键" title="位置2">番号2</span>', example)
        self.assertIn("const note='説明\\n続き'", example)
        player = outputs['ja/assets/model-player.js']
        self.assertIn("typeof f.sourceGroup==='string'", player)
        self.assertIn('o.textContent=g', player)
        self.assertIn('`特徴${j}`', player)
        self.assertIn('meta[name="i18n-scope"]', outputs['ja/assets/i18n.js'])
        document, _, _ = runtime._bundle(outputs['ja/' + runtime.BUNDLE])
        self.assertEqual(document['ja'][runtime.HINT_KEY], JA_HINT)
        self.assertEqual(document['en'][runtime.HINT_KEY], 'old English')
        self.assertEqual(document['zh-CN'][runtime.HINT_KEY], HINT)
        self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()})
        self.assertEqual(outputs, runtime.prepare('ja', root))

    def test_english_spacing_and_bundle_are_compatible(self):
        outputs = runtime.prepare('en', self.fixture())
        self.assertIn('`Row ${count} row`', outputs['en/assets/app.js'])
        self.assertIn('`Feature ${j}`', outputs['en/assets/model-player.js'])
        document, _, _ = runtime._bundle(outputs['en/' + runtime.BUNDLE])
        self.assertEqual(document['en'][runtime.HINT_KEY], EN_HINT)
        self.assertEqual(document['ja'][runtime.HINT_KEY], '元の検索例')

    def test_japanese_does_not_add_english_seam_spaces(self):
        source = 'const row=`列${i}列`;'
        self.assertEqual(runtime.localize_js(source, {'列': 'ID'}, lang='ja'),
                         'const row=`ID${i}ID`;')
        self.assertEqual(runtime.localize_js(source, {'列': 'ID'}),
                         'const row=`ID ${i} ID`;')

    def test_model_group_filter_uses_original_keys_and_keeps_display_groups(self):
        output = runtime.prepare('ja', self.fixture())['ja/assets/model-player.js']
        expression = re.search(r'const groups=(.*?); if\(!groups.length\)', output).group(1)
        script = ("const frames=[{group:'前方向計算',sourceGroup:'前向计算'},"
                  "{group:'訓練',sourceGroup:'训练'}, {group:'前向legacy'}];"
                  "const requested=['前向'];const available=[...new Set(frames.map(f=>f.group))];"
                  'const groups=' + expression + ';'
                  "if(JSON.stringify(groups)!==JSON.stringify(['前方向計算','前向legacy']))throw Error(JSON.stringify(groups));")
        result = subprocess.run(['node'], input=script, text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_japanese_and_english_export_use_selected_field(self):
        root = self.fixture()
        table = json.loads((root / runtime.TABLE).read_text())
        del table['s']['位置']['ja']
        (root / runtime.TABLE).write_text(json.dumps(table, ensure_ascii=False))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            runtime.export('ja', root)
        self.assertIn('target language: ja', out.getvalue())
        self.assertIn('テンソル', out.getvalue())
        self.assertIn('\t位置\n', out.getvalue())
        with self.assertRaisesRegex(runtime.RuntimeStringError, '缺运行时译文'):
            runtime.prepare('ja', root)

    def test_protection_checks_remain_language_independent(self):
        runtime.validate_translation('位置2', '位置2', lang='ja')
        with self.assertRaisesRegex(runtime.RuntimeStringError, 'untranslated Chinese'):
            runtime.validate_translation('位置2', '位置2')
        for source, value in [('位置2', '位置3'), ('文件run.json', 'ファイルother.json'),
                              ('变量W=2', '変数V=2'), ('说明\\n继续', '説明\\t続き'),
                              ('位置', ''), ('位置', '位置\n次'), ('位置', '\x00')]:
            with self.subTest(source=source, value=value):
                with self.assertRaises(runtime.RuntimeStringError):
                    runtime.validate_translation(source, value, lang='ja')

    def test_unsupported_languages_and_invalid_hint_are_rejected(self):
        for operation in (runtime.prepare, runtime.export):
            with self.assertRaises(runtime.RuntimeStringError):
                operation('fr', self.fixture())
        with self.assertRaises(runtime.RuntimeStringError):
            runtime.localize_js('const value=1;', {}, lang='fr')
        source = (self.fixture() / runtime.BUNDLE).read_text()
        with self.assertRaisesRegex(runtime.RuntimeStringError, 'Japanese page-search hint'):
            runtime.render_bundle(source, '中国語・英語・課番号・問題番号で検索できます。例：张量、第39课、Q001。', lang='ja')
        with self.assertRaisesRegex(runtime.RuntimeStringError, 'English page-search hint'):
            runtime.render_bundle(source, 'Search text, Lesson 39, Q001.')

    def test_stale_registry_stops_prepare(self):
        root = self.fixture()
        (root / runtime.FILES[0]).write_text('const label="变更";')
        with self.assertRaisesRegex(runtime.RuntimeStringError, 'registry is stale'):
            runtime.prepare('ja', root)

    def test_inline_japanese_keeps_expressions_and_parses(self):
        source = "const count=2; const row=`第${count}行`; const text='位置';"
        output = runtime.localize_js(source, {'第': '第', '行': '行', '位置': '位置'}, lang='ja')
        self.assertEqual(source, output)
        self.assertEqual(runtime.code_signature(source), runtime.code_signature(output))
        result = subprocess.run(['node', '--check'], input=output, text=True,
                                capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_prepared_fixture_scripts_parse(self):
        root = self.fixture()
        for lang in ('en', 'ja'):
            for rel, output in runtime.prepare(lang, root).items():
                with self.subTest(path=rel):
                    result = subprocess.run(['node', '--check'], input=output, text=True,
                                            capture_output=True, timeout=10)
                    self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
