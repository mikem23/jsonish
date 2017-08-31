import unittest

import json
from jsonish.parser import parse


class TestParser(unittest.TestCase):

    basic_data = [
            "hello world",
            5,
            5.5,
            2**63 - 1,
            True,
            False,
            None,
            "foo",
            [1,2,"3"],
            {},
            {"a": 1},
            {"a": 1, "b": 2},
            {"a": 1, "b": ["two", {"c": 3.3}]},
            ]

    def test_simple(self):
        data = self.basic_data
        #data = ["hello", 5, 5.5, []]
        for value in data:
            enc = json.dumps(value)
            chk = parse(enc)
            self.assertEqual(chk, value)

    bare_data = [
            [''' {a:1, b:2, cee:dee} ''',
                {'a':1, 'b':2, 'cee': 'dee'}],
            [''' ["hello", world, 1, two, '3'] ''',
                ["hello", "world", 1, "two", "3"]],
            ]

    def test_bare(self):
        data = self.bare_data
        for enc, value in data:
            chk = parse(enc)
            self.assertEqual(chk, value)
