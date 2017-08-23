import unittest

from jsonish.parser import parse

class TestParser(unittest.TestCase):

    def test_simple(self):
        data = r'"Hello World"'
        ret = parse(data)
        self.assertEqual(ret, "Hello World")

