import unittest

from six.moves import cStringIO
from jsonish.streamer import Streamer


class TestStreamer(unittest.TestCase):

    data = r'Hello World, this is some test content'

    def test_string(self):
        streamer = Streamer(self.data)
        gen = streamer.stream()
        chk = ''.join(list(gen))
        self.assertEqual(chk, self.data)

    def test_list(self):
        slist = [self.data] * 5
        streamer = Streamer(slist)
        gen = streamer.stream()
        chk = ''.join(list(gen))
        expect = ''.join(slist)
        self.assertEqual(chk, expect)

    def test_stringio(self):
        sio = cStringIO(self.data)
        streamer = Streamer(sio)
        gen = streamer.stream()
        chk = ''.join(list(gen))
        self.assertEqual(chk, self.data)

    def test_iter(self):
        slist = [self.data] * 5
        streamer = Streamer(iter(slist))
        gen = streamer.stream()
        chk = ''.join(list(gen))
        expect = ''.join(slist)
        self.assertEqual(chk, expect)

