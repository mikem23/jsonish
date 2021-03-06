from __future__ import absolute_import
import six
from six.moves import range
from .streamer import Streamer
if six.PY2:
    # py2 cStringIO doesn't handle unicode
    from six.moves import StringIO
else:
    from six.moves import cStringIO as StringIO


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
        self.streamer = Streamer(source)
        self.stream = self.streamer.stream()

    def tokenize(self):
        for c in self.stream:
            # inner loop allows handlers to push handling back up
            while True:
                if c == '#':
                    self.do_comment()
                elif c in TOKENS:
                    r = TOKENS[c]
                    yield r
                elif c in ('"', "'"):
                    r = self.do_string(c)
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
        result = StringIO()
        for c in self.stream:
            if c == '\\':
                esc = self.do_escape()
                result.write(esc)
            elif c == quote:
                break
            else:
                result.write(c)
        ret = result.getvalue()
        return ret

    def do_escape(self):
        try:
            code = next(self.stream)
            if code in ESCAPES:
                return ESCAPES[code]
            elif code == 'u':
                xdigits = ''.join([next(self.stream) for i in range(4)])
                return six.unichr(int(xdigits, 16))
            else:
                raise ValueError('Invalid escape: \\%s' % code)
        except StopIteration:
            raise ValueError('Incomplete escape')

    def do_comment(self):
        # just read to end of line
        for c in self.stream:
            if c == '\n':
                break

    def do_token(self, lead):
        result = StringIO()
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
        return BareToken(ret), tail


class TokenParser(object):

    def __init__(self, source):
        self.tokenizer = Tokenizer(source)
        self.tokens = self.tokenizer.tokenize()

    def parse(self):
        items = []
        for token in self._parse():
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
            if isinstance(token, BareToken):
                val = self.parse_bare(token)
                if isinstance(val, BareToken):
                    stringbuf.append(val)
                    continue
                else:
                    yield val
            elif isinstance(token, six.string_types):
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
        yield END

    def _join_buf(self, stringbuf):
        newbuf = []
        last = None
        for val in stringbuf:
            if last is not None:
                # bare tokens get space separated
                if isinstance(last, BareToken) or isinstance(val, BareToken):
                    newbuf.append(' ')
            last = val
            newbuf.append(six.text_type(val))
        return ''.join(newbuf)

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
        if six.text_type(token)[0].isdigit():
            raise ValueError('Strings beginning with numbers must be quoted')
        return token

    def parse_list(self):
        result = []
        for token in self._parse():
            if token is END:
                raise ValueError('Unclosed list')
            elif token is EndBracket:
                break
            elif token is Comma:
                if not result or last is Comma:
                    raise ValueError('Blank entry in list')
            elif isinstance(token, Token):
                raise ValueError('Unexpected token %s' % token)
            else:
                result.append(token)
            last = token

        return result

    def parse_dict(self):
        result = {}
        parser = self._parse()
        while True:
            key = next(parser)
            if key is EndBrace:
                break
            elif key is END:
                raise ValueError('Unclosed dictionary')
            colon = next(parser)
            if colon is not Colon:
                raise ValueError('Missing colon in dictionary')
            value = next(parser)
            if value is END:
                raise ValueError('Incomplete dictionary entry')
            elif isinstance(value, Token):
                raise ValueError('Unexpected token %s' % value)
            result[key] = value
            comma = next(parser)
            if comma is Comma:
                # this is what we expect
                pass
            elif comma is EndBrace:
                break
        return result
