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

if __name__ == '__main__':
    unittest.main()