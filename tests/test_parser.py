import unittest

import json
from jsonish.parser import parse
from jsonish.parser import BareToken


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
            [],
            {},
            "",
            "This \"string\" \t has\nescapes",
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

    comment_data = [
            [''' {a:1,  # This is key "a"
                  b:2,  # this is key 'b'
                  cee:dee, # this is key cee, an{y}th[i]ng goes, in a comm:ent
                  }
                ''',
                {'a':1, 'b':2, 'cee': 'dee'}],
            [''' # Hello, have some json
                [
                    [ # empty list. this ] doesn't count
                        ],  # <- but this one does
                    {hello: 1,
                        world: #comments ok here
                            2,
                        foo: [1,   2,   3,
                                { bar: "bar" # deep comment
                                }
                            ]
                        }
                    ]
                ''',
                [[],
                    {"hello":1,
                        "world": 2,
                        "foo": [1, 2, 3, {"bar": "bar"}]
                        }
                    ]
                ],
            ]

    def test_comments(self):
        data = self.comment_data
        for enc, value in data:
            chk = parse(enc)
            self.assertEqual(chk, value)

    join_data = [
            [
                ''' "hello" "world" ''',
                "hello world"],
            [
                ''' hello world ''',
                "hello world"],
            [
                ''' hello "world" ''',
                "hello world"],
        ]

    def test_implicit_join(self):
        data = self.join_data
        for enc, value in data:
            chk = parse(enc)
            self.assertEqual(chk, value)

    unclosed_data = [
            ''' [ ''',
            ''' [1, ''',
            ''' [1, 2, 3, [], [] ''',
            ''' {a:1, ''',
            ''' {a:1, b:2, c:3, d:{}, e:[] ''',
            ''' {, ''',
            ''' {a, ''',
        ]

    def test_unclosed(self):
        data = self.unclosed_data
        for enc in data:
            with self.assertRaises(ValueError):
                chk = parse(enc)

    bad_escape_data = [
            r''' "\6" ''',
            r''' ["\6"] ''',
            r''' {a:"\6"} ''',
            r''' "\i" ''',
        ]

    def test_bad_escape(self):
        data = self.bad_escape_data
        for enc in data:
            with self.assertRaises(ValueError):
                chk = parse(enc)

    escape_data = [
            r' "\"" ',
            r' "\\" ',
            r' "\/" ',
            r' "\b" ',
            r' "\f" ',
            r' "\n" ',
            r' "\r" ',
            r' "\t" ',
            #r' "\u0001" ',
        ]

    def test_escape(self):
        data = self.escape_data
        for enc in data:
            value = json.loads(enc)
            chk = parse(enc)
            self.assertEqual(chk, value)


class TestBareToken(unittest.TestCase):

    def test_bare_token_string(self):
        s = BareToken('4.5')
        self.assertEqual(str(s), '4.5')

    def test_bare_token_repr(self):
        t = BareToken('4.5')
        r = repr(t)
        self.assertEqual(r[:10], 'BareToken(')
