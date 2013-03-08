from __future__ import with_statement

import os
import folio
import unittest

class FolioTestCase(unittest.TestCase):

    def setUp(self):
        self.proj = folio.Folio(__name__)

    def tearDown(self):
        self.proj = None

    def test_import_path(self):
        cwd = os.path.abspath(os.path.dirname(__file__))
        msg = 'Import path must be the absolute path of directory where the' \
              ' project script is.'
        self.assertEquals(cwd, self.proj.import_path, msg)

    def test_default_builders(self):
        expected = ['*', '*.html']
        actual = [pattern for pattern, _ in self.proj.builders]

        # Compare only the patterns because the implementation of the builder
        # can change with the time.
        self.assertSequenceEqual(expected, actual)

    def test_add_builder_basestring(self):
        self.proj.add_builder('test', lambda: None)
        self.assertIn('test', [pattern for pattern, _ in self.proj.builders])

    def test_add_builder_iterator(self):
        self.proj.add_builder(['one', 'two'], lambda: None)

        patterns = [pattern for pattern, _ in self.proj.builders]

        self.assertIn('one', patterns)
        self.assertIn('two', patterns)

    def test_add_builder_not_callable(self):
        with self.assertRaises(TypeError):
            self.proj.add_builder('hello.html', 'hello')

    def test_add_builder_not_iterable(self):
        with self.assertRaises(TypeError):
            self.proj.add_builder(lambda: None, lambda: None)

if __name__ == '__main__':
    unittest.main()