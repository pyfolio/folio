from __future__ import with_statement

import os
import folio
import unittest


class FolioTestCase(unittest.TestCase):

    def setUp(self):
        self.proj = folio.Folio(__name__)
        self.proj.config['TESTING'] = True

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

    def test_is_template(self):
        self.assertTrue(self.proj.is_template('index.html'))
        self.assertTrue(self.proj.is_template('good_news/im_alive.html'))
        self.assertTrue(self.proj.is_template('blog/20130228-helloworld.md'))

        self.assertFalse(self.proj.is_template('.hidden'))
        self.assertFalse(self.proj.is_template('_draft-conquer_the_world.md'))
        self.assertFalse(self.proj.is_template('projects/.hidden'))
        self.assertFalse(self.proj.is_template('projects/_secret.html'))
        self.assertFalse(self.proj.is_template('projects/_inc/unique.css'))
        self.assertFalse(self.proj.is_template('_inc/reset.css'))
        self.assertFalse(self.proj.is_template('_inc/_underscore2.js'))
        self.assertFalse(self.proj.is_template('.git/config'))


if __name__ == '__main__':
    unittest.main()
