import cStringIO


def oldparse(data):
    return Parser(data).parse()


def parse(data):
    return TokenParser(data).parse()


WHITESPACE = (' ', '\t', '\r', '\n')
NUMERIC = [str(i) for i in range(10)] + ['-', '.']
TOKENS = {}


class Token(object):

    def __init__(self, name):
        self.name = name
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
        return 'Bare(%r)' % self.name



class Parser(object):

    def __init__(self, data):
        self.data = data
        self.offset = 0
        self.parts = []

    def parse(self):
        return self.parse_open()

    def parse_open(self):
        # begin parsing in the open state
        while self.offset < len(self.data):
            c = self.data[self.offset]
            self.offset += 1
            if c == '{':
                return self.parse_dict()
            elif c == '}':
                return EndBrace
            elif c == '[':
                return self.parse_list()
            elif c == ']':
                return EndBracket
            elif c == ',':
                return Comma
            elif c == ':':
                return Colon
            elif c == '"':
                return self.parse_string()
            elif c == "'":
                return self.parse_string2()
            elif c == '#':
                return self.parse_comment()
            elif c in WHITESPACE:
                pass
            elif c in NUMERIC:
                return self.parse_number()
            else:
                return self.parse_bare()
        return END

    def parse_string(self):
        start = self.offset
        end = self.data.find('"', self.offset)
        if end == -1:
            raise ValueError('Unterminated string')
        self.offset = end + 1
        return self.data[start:end]

    def parse_comment(self):
        end = self.data.find('\n', self.offset)
        self.offset = end + 1
        return Comment

    def parse_number(self):
        start = self.offset - 1
        while self.offset < len(self.data):
            c = self.data[self.offset]
            if c not in NUMERIC:
                break
            self.offset += 1
        end = self.offset
        num = self.data[start:end]
        for _type in (int, float):
            try:
                return _type(num)
            except ValueError:
                pass
        raise ValueError('Invalid number: %s' % num)

    def parse_list(self):
        this = []
        while True:
            part = self.parse_open()
            if isinstance(part, Token):
                if part is Comment:
                    continue
                elif part is Comma:
                    continue
                elif part is EndBracket:
                    return this
                else:
                    raise ValueError('Invalid syntax')
            else:
                this.append(part)
        # not reached

    def parse_dict(self):
        this = {}
        key = None
        while True:
            part = self.parse_open()
            if isinstance(part, Token):
                if part is Comment:
                    continue
                elif part is Comma:
                    continue
                elif part is Colon:
                    continue
                elif part is EndBrace:
                    return this
                else:
                    raise ValueError('Invalid syntax')
            elif key is None:
                key = part
            else:
                this[key] = part
                key = None
        # not reached


ESCAPES = {
        '\\': '\\',
        'n': '\n',
        'r': '\r',
        't': '\t',
        '"': '"',
        "'": "'",
        }


def strgen(s):
    """Turn a string into a character generator"""
    for c in s:
        yield c


class Tokenizer(object):

    def __init__(self, stream):
        if isinstance(stream, str):
            self.stream = strgen(stream)
        else:
            self.stream = stream

    def tokenize(self):
        for c in self.stream:
            print(c)
            if c in TOKENS:
                r = TOKENS[c]
                print(r)
                yield r
            elif c in ('"', "'"):
                r = self.do_string(c)
                print(r)
                yield r
            elif c == '#':
                self.do_comment()

    def do_string(self, quote):
        escape = False
        result = cStringIO.StringIO()
        for c in self.stream:
            print("schar: %r" % c)
            if escape:
                if c in ESCAPES:
                    result.write(ESCAPES[c])
                else:
                    raise ValueError('Invalid escape: \\%s' % c)
            elif c == '\\':
                escape = True
            elif c == quote:
                break
            else:
                result.write(c)
        ret = result.getvalue()
        print("string: %r" % ret)
        return ret

    def do_comment(self):
        # just read to end of line
        for c in self.stream:
            if c == '\n':
                break


class TokenParser(object):

    def __init__(self, stream):
        self.tokenizer = Tokenizer(stream)
        self.tokens = self.tokenizer.tokenize()
        self.items = []

    def parse(self):
        while True:
            token = self._parse()
            if token is END:
                break
            elif isinstance(token, Token):
                raise ValueError('Unexpected token %s' % token)
            else:
                self.items.append(token)
        if not self.items:
            raise ValueError('No json data found')
        elif len(self.items) > 1:
            raise ValueError('Multiple json outputs found')
            # TODO: maybe support this with an option
        return self.items[0]


    def _parse(self):
        for token in self.tokens:
            if token is Brace:
                return self.parse_dict()
            elif token is Bracket:
                return self.parse_list()
            elif isinstance(token, Token):
                return token
            elif isinstance(token, BareToken):
                self.parse_bare()
            elif isinstance(token, str):
                return token
        return END
