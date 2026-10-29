"""Offline first-build link checks, using only disposable empty edition trees."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import apply


EDITION_JS = (
    'diagrams.js', 'mechanisms.js', 'model-player.js', 'visual-player.js',
    'concept-labs.js', 'reader-navigation.js', 'app.js', 'atelier.js',
    'i18n.js', 'i18n-data.js', 'visual-data.js', 'model-data.js',
    'catalog.js', 'search-data.js',
)


class FirstEditionLinkTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='apply-ja-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.root_patch = patch.object(apply, 'ROOT', self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def relink(self, language, markup, page='index.html', pages=()):
        with patch.object(apply, 'LANG', language):
            return apply.relink(markup, page, set(pages))

    def test_empty_edition_keeps_all_fourteen_declared_scripts_local(self):
        for language in ('en', 'ja', 'es', 'vi'):
            for page, prefix in [('index.html', ''), ('foundations/01.html', '../'),
                                 ('studies/code/test.html', '../../')]:
                for name in EDITION_JS:
                    with self.subTest(language=language, page=page, asset=name):
                        markup = '<script src="%sassets/%s?v=2#part"></script>' % (prefix, name)
                        self.assertEqual(self.relink(language, markup, page), markup)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_shared_css_and_unknown_scripts_still_leave_edition(self):
        for language in ('en', 'ja', 'es', 'vi'):
            for name in ('style.css', 'unknown.js', 'model-data.js.map', 'app.js.bak'):
                with self.subTest(language=language, asset=name):
                    source = '<a href="../../assets/%s?x=1#topic">asset</a>' % name
                    expected = '<a href="../../../assets/%s?x=1#topic">asset</a>' % name
                    self.assertEqual(self.relink(language, source, 'studies/code/page.html'), expected)
            source = '<script src="assets/unknown.js#fragment?literal"></script>'
            expected = '<script src="../assets/unknown.js#fragment?literal"></script>'
            self.assertEqual(self.relink(language, source), expected)

    def test_only_supported_complete_editions_assume_future_scripts(self):
        source = '<script src="assets/model-data.js"></script>'
        self.assertEqual(self.relink('fr', source),
                         '<script src="../assets/model-data.js"></script>')

    def test_existing_language_files_keep_previous_semantics(self):
        for language in ('en', 'ja', 'es'):
            mirrored = self.root / language / 'assets/custom.js'
            mirrored.parent.mkdir(parents=True)
            mirrored.write_text('const custom=1;', encoding='utf-8')
            source = '<script src="../../assets/custom.js?v=1#run"></script>'
            self.assertEqual(self.relink(language, source, 'studies/code/page.html'), source)
            directory = self.root / language / 'assets/directory.js'
            directory.mkdir()
            self.assertEqual(self.relink(language, '<script src="assets/directory.js"></script>'),
                             '<script src="../assets/directory.js"></script>')

    def test_normalization_pages_and_external_references_are_unchanged(self):
        source = '<script src="../assets/tmp/../model-data.js?version=1#row"></script>'
        self.assertEqual(self.relink('ja', source, 'foundations/01.html'), source)
        pages = ('foundations/01.html',)
        for target in ('../foundations/01.html#topic', '../complete.html?mode=all#topic'):
            markup = '<a href="%s">page</a>' % target
            self.assertEqual(self.relink('ja', markup, 'chapters/01.html', pages), markup)
        for target in ('https://example.test/a.js', '//example.test/a.js', 'mailto:a@example.test',
                       'data:text/plain,value', '#section', '/absolute.js', '../../outside.js'):
            markup = '<a href="%s">link</a>' % target
            self.assertEqual(self.relink('ja', markup), markup)


if __name__ == '__main__':
    unittest.main()
