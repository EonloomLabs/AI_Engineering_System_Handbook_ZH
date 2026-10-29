"""Source-bound UTF-8 literal controls; validation never writes a table."""
import contextlib
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import batch


SOURCES = ('后续字节完成“学”',
           '，后接两个换行。网络可能在“学”的UTF-8字节中间切开。')
TRANSLATIONS = {
    'es': ('Los bytes posteriores completan «学»',
           ', seguido de dos saltos de línea. La red puede cortar entre los bytes UTF-8 de «学».'),
    'vi': ('Các byte tiếp theo hoàn thành «学»',
           ', tiếp theo là hai dấu xuống dòng. Mạng có thể cắt giữa các byte UTF-8 của «学».'),
}
PROGRAMMING_SOURCES = ('编程', 'BOS,我,爱,编程')
PAYLOAD_SOURCES = (
    '输入与条件。</strong>文档A=[排除,路径]，B=[排除,排除,路径,缓存]，C=[日志,输出]。N=3，平均长度8/3，k1=1.2，b=0.75；用非负IDF形式ln(1+(N−df+0.5)/(df+0.5))。',
    '输入与条件。</strong>用户u7仅有项目P1的读取权限，模型请求query(project="P2",text="部署密钥")。',
)
PAYLOAD_SPANS = (('A=[排除,路径]', 'B=[排除,排除,路径,缓存]', 'C=[日志,输出]'),
                 ('query(project="P2",text="部署密钥")',))
PAYLOAD_TARGETS = {
    'es': ('Entradas.</strong>A=[排除,路径] (exclusión, ruta), B=[排除,排除,路径,缓存] (exclusión, exclusión, ruta, caché), C=[日志,输出] (registro, salida). N=3; 8/3; k1=1.2; b=0.75; ln(1+(N−df+0.5)/(df+0.5)).',
           'Entradas.</strong>u7 solo puede leer P1; query(project="P2",text="部署密钥") (claves de despliegue).'),
    'vi': ('Đầu vào.</strong>A=[排除,路径] (loại trừ, đường dẫn), B=[排除,排除,路径,缓存] (loại trừ, loại trừ, đường dẫn, bộ nhớ đệm), C=[日志,输出] (nhật ký, đầu ra). N=3; 8/3; k1=1.2; b=0.75; ln(1+(N−df+0.5)/(df+0.5)).',
           'Đầu vào.</strong>u7 chỉ được đọc P1; query(project="P2",text="部署密钥") (khóa triển khai).'),
}


class BatchSourceLiteralTests(unittest.TestCase):
    def checked(self, source, target, lang):
        with patch.object(batch, 'LANG', lang), contextlib.redirect_stdout(io.StringIO()):
            return batch.check([(source, target)], Path('literal.' + lang + '.txt'),
                               'source-bound fixture', {}, True)[0]

    def test_both_exact_utf8_sources_allow_the_data_character_in_es_and_vi(self):
        for lang, values in TRANSLATIONS.items():
            for source, target in zip(SOURCES, values):
                with self.subTest(lang=lang, source=source):
                    self.assertEqual(self.checked(source, target, lang), [(source, target)])

    def test_other_sources_do_not_gain_a_generic_single_character_exemption(self):
        for source in ('学', '解释“学”', SOURCES[0] + '。', ' ' + SOURCES[0]):
            for lang in TRANSLATIONS:
                with self.subTest(source=source, lang=lang):
                    self.assertIsNone(self.checked(source, 'Dato «学»', lang))

    def test_exact_source_requires_exactly_one_data_character(self):
        for lang, values in TRANSLATIONS.items():
            for source, value in zip(SOURCES, values):
                for count in (0, 1, 2):
                    target = value.replace('学', '学' * count)
                    with self.subTest(lang=lang, source=source, count=count):
                        result = self.checked(source, target, lang)
                        if count == 1:
                            self.assertEqual(result, [(source, target)])
                        else:
                            self.assertIsNone(result)

    def test_current_english_and_japanese_table_rows_still_pass(self):
        table = json.loads(batch.TABLE.read_text(encoding='utf-8'))['s']
        for lang in ('en', 'ja'):
            for source in SOURCES:
                target = table[source][lang]
                with self.subTest(lang=lang, source=source):
                    self.assertEqual(target.count('学'), 1)
                    self.assertEqual(self.checked(source, target, lang), [(source, target)])

    def test_exact_source_does_not_exempt_other_chinese_prose(self):
        for source in SOURCES:
            for lang in TRANSLATIONS:
                with self.subTest(source=source, lang=lang):
                    self.assertIsNone(self.checked(source, 'Bytes «学» 后续', lang))

    def test_tag_and_filename_checks_are_still_applied(self):
        for lang, values in TRANSLATIONS.items():
            self.assertIsNone(self.checked(SOURCES[0], '<b>' + values[0] + '</b>', lang))
            self.assertIsNone(self.checked('读取中文.py', 'Read the file', lang))
            self.assertIsNone(self.checked(SOURCES[0], '', lang))

    def test_residual_keeps_numeric_and_code_bytes_unchanged(self):
        source = SOURCES[1]
        target = 'UTF-8 «学» 1 2 0.25 API() 中文.py'
        self.assertEqual(batch.residual(target, source), 'UTF-8 «» 1 2 0.25 API() 中文.py')
        self.assertEqual(batch.residual('UTF-8 «学» 0.25', 'unrelated source'), 'UTF-8 «学» 0.25')

    def test_exact_teacher_forcing_tokens_stay_literal_in_es_and_vi(self):
        self.assertNotIn('编程', batch.VOCAB)
        for lang in ('es', 'vi'):
            for source in PROGRAMMING_SOURCES:
                with self.subTest(lang=lang, source=source):
                    self.assertEqual(self.checked(source, source, lang), [(source, source)])

    def test_teacher_forcing_literal_count_must_remain_one(self):
        for lang in ('es', 'vi'):
            for source in PROGRAMMING_SOURCES:
                for count in (0, 2):
                    target = source.replace('编程', '编程' * count)
                    with self.subTest(lang=lang, source=source, count=count):
                        self.assertIsNone(self.checked(source, target, lang))

    def test_teacher_forcing_exception_does_not_allow_other_chinese(self):
        for lang in ('es', 'vi'):
            for source in ('编程说明', ' ' + PROGRAMMING_SOURCES[0], PROGRAMMING_SOURCES[1] + '。'):
                with self.subTest(lang=lang, source=source):
                    self.assertIsNone(self.checked(source, '编程', lang))
            for source in PROGRAMMING_SOURCES:
                self.assertIsNone(self.checked(source, source + ' 后续', lang))

    def test_current_english_japanese_pass_and_fixed_legacy_mismatch_is_flagged(self):
        table = json.loads(batch.TABLE.read_text(encoding='utf-8'))['s']
        for source in PROGRAMMING_SOURCES:
            with self.subTest(source=source):
                for lang in ('en','ja'):
                    target = table[source][lang]
                    self.assertEqual(self.checked(source, target, lang), [(source, target)])
                legacy = source.replace('编程','programming')
                self.assertIsNone(self.checked(source, legacy, 'en'))

    def test_exact_raw_payload_sources_allow_native_glosses_outside_the_syntax(self):
        for lang, targets in PAYLOAD_TARGETS.items():
            for source, target in zip(PAYLOAD_SOURCES, targets):
                with self.subTest(lang=lang, source=source):
                    self.assertEqual(self.checked(source, target, lang), [(source, target)])

    def test_each_complete_payload_span_rejects_mutation_drop_and_duplicate(self):
        for lang, targets in PAYLOAD_TARGETS.items():
            for source, target, spans in zip(PAYLOAD_SOURCES, targets, PAYLOAD_SPANS):
                for span in spans:
                    for changed in ('', span + span, span.replace('=', ' =', 1)):
                        with self.subTest(lang=lang, span=span, changed=changed):
                            self.assertIsNone(self.checked(source, target.replace(span, changed), lang))

    def test_payload_exception_does_not_allow_extra_chinese_or_unrelated_sources(self):
        for lang, targets in PAYLOAD_TARGETS.items():
            for source, target in zip(PAYLOAD_SOURCES, targets):
                with self.subTest(lang=lang, source=source):
                    self.assertIsNone(self.checked(source, target + ' 后续', lang))
                    self.assertIsNone(self.checked(source + '。', target, lang))
                    self.assertIsNone(self.checked('其他来源</strong>', target, lang))
                    self.assertIsNone(self.checked(source, target.replace('</strong>', ''), lang))

    def test_payload_spans_do_not_create_global_word_exemptions(self):
        for lang in PAYLOAD_TARGETS:
            for source in ('排除', '路径', '缓存', '日志', '输出', '部署密钥'):
                with self.subTest(lang=lang, source=source):
                    self.assertIsNone(self.checked(source, source, lang))


if __name__ == '__main__':
    unittest.main()
