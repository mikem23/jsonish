import json
import os
import os.path
import unittest

from jsonish import parse


DATADIR = os.path.dirname(__file__) + '/data'


class TestData(unittest.TestCase):

    """
    Test that the parser against good and bad sample data files
    """

    def test_good_data(self):
        files = []
        for fn in os.listdir(DATADIR):
            if not fn.endswith('.json'):
                continue
            if fn.startswith('pass'):
                files.append(DATADIR + '/' + fn)
        for fn in files:
            fo = open(fn)
            data = parse(fo)
            fo.seek(0)
            chk = json.load(fo)
            self.assertEqual(data, chk)

    def test_bad_data(self):
        files = []
        for fn in os.listdir(DATADIR):
            if not fn.endswith('.json'):
                continue
            if fn.startswith('fail'):
                files.append(DATADIR + '/' + fn)
        for fn in files:
            fo = open(fn)
            with self.assertRaises(ValueError):
                parse(fo)
