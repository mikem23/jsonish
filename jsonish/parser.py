from __future__ import absolute_import
import six
from six.moves import cStringIO, range
from .streamer import Streamer


def parse(data):
    return TokenParser(data).parse()


WHITESPACE = (' ', '\t', '\r', '\n')
TOKENS = {}


class Token(object):

    def __init__(self, name):
        self.name = name
        assert name not in TOKENS
        TOKENS[name] = self

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Token(%r)' % self.name


Brace = Token('{')
EndBrace = Token('}')
Bracket = Token('[')
EndBracket = Token(']')
Comma = Token(',')
Colon = Token(':')
Comment = Token('#')
END = Token('')


class BareToken(object):

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text

    def __repr__(self):
        return 'BareToken(%r)' % self.text


ESCAPES = {
        # standard json escapes (single char)
        '\\': '\\',
        'n': '\n',
        'r': '\r',
        't': '\t',
        '"': '"',
        '/': '/',
        'b': '\b',
        'f': '\f',
        # also single quote
        "'": "'",
        }


class Tokenizer(object):

    def __init__(self, source):
        print("Tokenizer for: %r" % source)
        self.streamer = Streamer(source)
        self.stream = self.streamer.stream()

    def tokenize(self):
        for c in self.stream:
            # inner loop allows handlers to push handling back up
            while True:
                print(": %r" % c)
                if c == '#':
                    self.do_comment()
                elif c in TOKENS:
                    r = TOKENS[c]
                    print("token: %r" % r)
                    yield r
                elif c in ('"', "'"):
                    r = self.do_string(c)
                    print("string: %r" % r)
                    yield r
                elif c in WHITESPACE:
                    # skip
                    pass
                else:
                    bare, c = self.do_token(c)
                    yield bare
                    if c:
                        continue
                break

    def do_string(self, quote):
        result = cStringIO()
        for c in self.stream:
            if c == '\\':
                print('escape start')
                esc = self.do_escape()
                result.write(esc)
            elif c == quote:
                print('string stop')
                break
            else:
                print('string char: %s' % c)
                result.write(c)
        ret = result.getvalue()
        return ret

    def do_escape(self):
        try:
            code = next(self.stream)
            if code in ESCAPES:
                print("Escape char: %r" % code)
                return ESCAPES[code]
            elif code == 'u':
                xdigits = ''.join([next(self.stream) for i in range(4)])
                return six.unichr(int(xdigits, 16))
            else:
                raise ValueError('Invalid escape: \\%s' % code)
        except StopIteration:
            raise ValueError('Incomplete escape')

    def do_comment(self):
        print('comment start')
        # just read to end of line
        for c in self.stream:
            print('comment char: %r' % c)
            if c == '\n':
                break

    def do_token(self, lead):
        print('reading bare token: lead=%r' % lead)
        result = cStringIO()
        result.write(lead)
        tail = ''
        for c in self.stream:
            if c in WHITESPACE:
                # end token
                break
            elif c in TOKENS:
                # end bare token, but pass char back for further processing
                tail = c
                break
            else:
                result.write(c)
        ret = result.getvalue()
        print('Got bare token: %r' % ret)
        return BareToken(ret), tail


class TokenParser(object):

    def __init__(self, source):
        self.tokenizer = Tokenizer(source)
        self.tokens = self.tokenizer.tokenize()

    def parse(self):
        items = []
        for token in self._parse():
            print("got token: %r" % token)
            if token is END:
                break
            elif isinstance(token, Token):
                raise ValueError('Unexpected token %s' % token)
            elif items:
                raise ValueError('Multiple json outputs found')
                # TODO: maybe support this with an option
            else:
                items.append(token)
        if not items:
            raise ValueError('No json data found')
        return items[0]

    def _parse(self):
        stringbuf = []  # for implicit string joins
        for token in self.tokens:
            print("stringbuf: %r" % stringbuf)
            if isinstance(token, BareToken):
                val = self.parse_bare(token)
                if isinstance(val, BareToken):
                    stringbuf.append(val)
                    continue
                else:
                    yield val
            elif isinstance(token, str):
                stringbuf.append(token)
                continue
            if stringbuf:
                result = self._join_buf(stringbuf)
                yield result
                stringbuf = []
            if token is Brace:
                yield self.parse_dict()
            elif token is Bracket:
                yield self.parse_list()
            elif isinstance(token, Token):
                yield token
        if stringbuf:
            result = self._join_buf(stringbuf)
            yield result
        print('END')
        yield END

    def _join_buf(self, stringbuf):
        print("joining stringbuf: %r" % stringbuf)
        result = cStringIO()
        last = None
        for val in stringbuf:
            if last is not None:
                # bare tokens get space separated
                if isinstance(last, BareToken) or isinstance(val, BareToken):
                    result.write(' ')
            last = val
            result.write(str(val))
        print('joined: %r' % result)
        return result.getvalue()

    BARE_VALUES = {
            'true': True,
            'false': False,
            'null': None,
            }

    def parse_bare(self, token):
        # bare words are either
        # - a numeric value
        # - a boolean value
        # - a null value
        # - a bare string
        text = token.text
        ltext = text.lower()
        if ltext in self.BARE_VALUES:
            return self.BARE_VALUES[ltext]
        try:
            return int(text)
        except ValueError:
            pass
        try:
            return float(text)
        except ValueError:
            pass
        print("bare: %r" % text)
        return token

    def parse_list(self):
        result = []
        for token in self._parse():
            print("list token: %r" % token)
            if token is END:
                raise ValueError('Unclosed list')
            elif token is EndBracket:
                break
            elif token is Comma:
                pass
            elif isinstance(token, Token):
                raise ValueError('Unexpected token %s' % token)
            else:
                result.append(token)
        return result

    def parse_dict(self):
        result = {}
        key = None
        for token in self._parse():
            print("dict token: %r" % token)
            if token is END:
                raise ValueError('Unclosed dict')
            elif token is EndBrace:
                break
            elif token is Colon:
                if key is None:
                    raise ValueError('Missing key in dictionary')
            elif token is Comma:
                if key is not None:
                    raise ValueError('Unexpected comma in dictionary')
            elif isinstance(token, Token):
                raise ValueError('Unexpected token %s' % token)
            else:
                if key is None:
                    key = token
                else:
                    result[key] = token
                    key = None
        return result
