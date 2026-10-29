"""Sentence gaps must never become bytes inside an inline code payload."""
import re
import unittest

import apply


CODE = re.compile(r'<code\b[^>]*>(.*?)</code>',re.S)


class ApplyCodeSeamTests(unittest.TestCase):
    def test_six_actual_payload_endings_keep_new_space_outside_code(self):
        # Found in ch01, ch10, ch15 (two), F03 and F23 respectively.
        for payload in ('&lt;untrusted&gt;','data:','query:','passage:','&lt;PAD&gt;','data:'):
            for lang, suffix in (('en','lines'),('es','líneas'),('vi','đường')):
                source='<p>Uses <code>'+payload+'</code>'+suffix+'</p>'
                expected='<p>Uses <code>'+payload+'</code> '+suffix+'</p>'
                with self.subTest(payload=payload,lang=lang):
                    result=apply.space_seams(source,lang=lang)
                    self.assertEqual(result,expected)
                    self.assertEqual(CODE.findall(result),CODE.findall(source))
                    self.assertEqual(apply.space_seams(result,lang=lang),result)

    def test_original_spaces_tabs_and_newlines_in_payload_are_never_removed(self):
        for payload in ('data: ',' query:\t','\npassage: \n','&lt;PAD&gt;  '):
            source='<code>'+payload+'</code>word'
            for lang in ('en','es','vi'):
                with self.subTest(payload=payload,lang=lang):
                    self.assertEqual(apply.space_seams(source,lang=lang),source)

    def test_internal_inline_markup_is_opaque_to_all_seam_insertions(self):
        payload='alpha<strong>beta</strong>gamma,<em>delta</em>!<i>epsilon</i>'
        source='<p>Word<code>'+payload+'</code>.</p>'
        for lang in ('en','es','vi'):
            result=apply.space_seams(source,lang=lang)
            self.assertEqual(CODE.findall(result),[payload])
            self.assertTrue(result.startswith('<p>Word <code>'))

    def test_nested_closing_tags_move_only_the_new_gap_past_code(self):
        for lang in ('en','es','vi'):
            source='<code><b>query:</b></code><em>consulta</em>'
            expected='<code><b>query:</b></code> <em>consulta</em>'
            self.assertEqual(apply.space_seams(source,lang=lang),expected)
            source='<code>query:</code><code>passage:</code>prefix'
            expected='<code>query:</code> <code>passage:</code> prefix'
            self.assertEqual(apply.space_seams(source,lang=lang),expected)

    def test_existing_outer_seams_punctuation_and_non_code_markup_are_retained(self):
        cases=(('word<code>API</code>word','word <code>API</code> word'),
               ('list,<code>[2]</code>next','list,<code>[2]</code> next'),
               ('<code>[1]</code>,<code>[2]</code>','<code>[1]</code>, <code>[2]</code>'),
               ('x<sub>i</sub>+x<sup>2</sup>','x<sub>i</sub>+x<sup>2</sup>'),
               ('<code>API</code>-style','<code>API</code>-style'),
               ('x<strong>word:</strong>next','x <strong>word: </strong>next'))
        for lang in ('en','es','vi'):
            for source,expected in cases:
                with self.subTest(lang=lang,source=source):
                    self.assertEqual(apply.space_seams(source,lang=lang),expected)

    def test_existing_opaque_regions_remain_byte_identical(self):
        for name in ('pre','script','style','svg','textarea'):
            source='<'+name+'><code>data:</code>word</'+name+'>'
            for lang in ('en','es','vi'):
                with self.subTest(name=name,lang=lang):
                    self.assertEqual(apply.space_seams(source,lang=lang),source)


if __name__=='__main__':
    unittest.main()
