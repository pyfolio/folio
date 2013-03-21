from __future__ import with_statement

import os
import folio
import unittest


class FolioTestCase(unittest.TestCase):

    def _create_folio(self, **kwargs):
        proj = folio.Folio(__name__, **kwargs)
        proj.config['TESTING'] = True

        return proj

    def test_default_builders(self):
        expected = ['*', '*.html']
        actual = [pattern for pattern, _ in self._create_folio().builders]

        # Compare only the patterns because the implementation of the builder
        # can change with the time.
        self.assertSequenceEqual(expected, actual)

    def test_import_path(self):
        cwd = os.path.abspath(os.path.dirname(__file__))
        msg = 'Import path must be the absolute path of directory where the' \
              ' project script is.'
        self.assertEquals(cwd, self._create_folio().import_path, msg)

    def test_register_extension(self):
        import fixtures.ext

        proj = self._create_folio()

        with self.assertRaises(fixtures.ext.ExtensionRegistered):
            proj.register_extension(fixtures.ext)

        self.assertIn('ext', proj.extensions)

        with self.assertRaises(LookupError):
            proj.register_extension(fixtures.ext)

    def test_register_extension_invalid(self):
        ext = {'register': lambda: None}
        with self.assertRaises(ValueError):
            self._create_folio().register_extension(ext)

    def test_add_builder_basestring(self):
        proj = self._create_folio()
        proj.add_builder('test', lambda: None)

        self.assertIn('test', [pattern for pattern, _ in proj.builders])

    def test_add_builder_iterator(self):
        proj = self._create_folio()
        proj.add_builder(['one', 'two'], lambda: None)

        patterns = [pattern for pattern, _ in proj.builders]

        self.assertIn('one', patterns)
        self.assertIn('two', patterns)

    def test_add_builder_not_callable(self):
        with self.assertRaises(TypeError):
            self._create_folio().add_builder('hello.html', 'hello')

    def test_add_builder_not_iterable(self):
        with self.assertRaises(TypeError):
            self._create_folio().add_builder(lambda: None, lambda: None)

    def test_get_builder(self):
        proj = self._create_folio()

        static_builder = proj.get_builder('*')
        template_builder = proj.get_builder('*.html')

        self.assertEquals(folio._static_builder, static_builder)
        self.assertEquals(folio._template_builder, template_builder)

    def test_get_builder_not_found(self):
        proj = self._create_folio()
        proj.builders = []

        self.assertEquals(None, proj.get_builder('foobar'))

    def test_is_template(self):
        proj = self._create_folio()

        self.assertTrue(proj.is_template('index.html'))
        self.assertTrue(proj.is_template('good_news/im_alive.html'))
        self.assertTrue(proj.is_template('blog/20130228-helloworld.md'))

        self.assertFalse(proj.is_template('.hidden'))
        self.assertFalse(proj.is_template('_draft-conquer_the_world.md'))
        self.assertFalse(proj.is_template('projects/.hidden'))
        self.assertFalse(proj.is_template('projects/_secret.html'))
        self.assertFalse(proj.is_template('projects/_inc/unique.css'))
        self.assertFalse(proj.is_template('_inc/reset.css'))
        self.assertFalse(proj.is_template('_inc/_underscore2.js'))
        self.assertFalse(proj.is_template('.git/config'))


if __name__ == '__main__':
    unittest.main()
