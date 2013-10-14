from __future__ import with_statement

import os
import folio
import unittest

from shutil import rmtree
from tempfile import mkdtemp
from filecmp import dircmp


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(CURRENT_DIR, 'fixtures')
SOURCE_DIR = os.path.join(FIXTURES_DIR, 'src')


class FolioTestCase(unittest.TestCase):

    def assertDirEqual(self, dcmp, msg=None):
        """Assert that a directory compare has no differences."""

        self.assertEquals([], dcmp.left_only)
        self.assertEquals([], dcmp.right_only)

        for subdcmp in dcmp.subdirs.values():
            self.assertDirEqual(subdcmp)

    def assertFileEqual(self, expected, filename, msg=None):
        """Assert that a file contains the expected text."""

        with open(filename, 'r') as f:
            actual = f.read()

        self.assertEquals(expected, actual)

    def _create_folio(self, **kwargs):
        proj = folio.Folio(__name__, **kwargs)
        proj.config['TESTING'] = True

        return proj

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

    def test_build(self):
        outdir= mkdtemp()

        proj = self._create_folio(source_path=SOURCE_DIR, build_path=outdir)
        proj.build()

        helloworld = """<!doctype html>
<title>Hello from Folio</title>
Hello World!"""

        self.assertDirEqual(dircmp(SOURCE_DIR, outdir))
        self.assertFileEqual(helloworld, os.path.join(outdir, 'helloworld.html'))

        rmtree(outdir)

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
        builder = lambda: None

        proj = self._create_folio()
        proj.builders = [('*', builder)]

        self.assertEquals(builder, proj.get_builder('*'))

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
