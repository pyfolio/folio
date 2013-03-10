import unittest
import folio.helpers


class HelpersTestCase(unittest.TestCase):
    def test_lazy_property(self):
        calls = []
        class Foobar(object):
            def foo(self):
                calls.append(True)
                return 42
            foo = folio.helpers.lazy_property(foo)

        c = Foobar()
        n = c.foo
        m = c.foo

        self.assertEquals(42, n)
        self.assertEquals(42, m)
        self.assertEquals(1, len(calls))


if __name__ == '__main__':
    unittest.main()
