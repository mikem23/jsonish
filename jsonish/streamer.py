'''
Turn various types of objects into a character iterator
'''

import six
import types


class Streamer(object):

    def __init__(self, source):
        self.source = source

    def stream(self):
        if isinstance(self.source, six.string_types):
            return self.gen_string()
        elif isinstance(self.source, file):
            return self.gen_file()
        elif isinstance(self.source, types.GeneratorType):
            resutn self.gen_gen()
        elif hasattr(self.source, read):
            return self.gen_file()

    def gen_string(self):
        for c in self.source:
            yield c

    def gen_file(self):
        for chunk in self.source.read(65535):
            for c in chunk:
                yield c

    def gen_gen(self):
        '''Turn a string generator into a charactor generator'''
        for part in self.source:
            for c in part:
                yield c
