

def parse(data):
    return Parser(data).parse()


WHITESPACE = (' ', '\t', '\r', '\n')
NUMERIC = [str(i) for i in range(10)] +  ['-', '.']


class Token(object):
    def __init__(self, name):
        self.name = name

EndBrace = Token('}')
EndBracket = Token(']')
Comma = Token(',')
Comment = Token('#')
END = Token('end')


class Parser(object):

    def __init__(self, data):
        self.data = data
        self.offset = 0
        self.parts = []

    def parse(self):
        return self.parse_open()

    def parse_open(self):
        # begin parsing in the open state, meaning we are not inside anything yet
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
        offset = end + 1
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

