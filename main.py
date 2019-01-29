import re
from collections import namedtuple

NUM = r"(?P<NUM>[01])"
SYMBOL = r"(?P<SYMBOL>[A-Z])"
NEGATIVE = r"(?P<NEGATIVE>\!)"
CONJUNCTION = r"(?P<CONJUNCTION>\&)"
DISJUNCTION = r"(?P<DISJUNCTION>\|)"
IMPLICATION = r"(?P<IMPLICATION>\-\>)"
EQUIVALENT = r"(?P<EQUIVALENT>\~)"
LPAREN = r"(?P<LPAREN>\()"
RPAREN = r"(?P<RPAREN>\))"
WS = r"(?P<WS>\s+)"

pattern = re.compile(
    "|".join(
        [
            NUM,
            SYMBOL,
            NEGATIVE,
            CONJUNCTION,
            DISJUNCTION,
            IMPLICATION,
            EQUIVALENT,
            LPAREN,
            RPAREN,
            WS,
        ]
    )
)
Token = namedtuple("Token", ["type", "value"])


def generate_tokens(pat, text):
    scanner = pat.scanner(text)
    for _ in iter(scanner.match, None):
        tok = Token(_.lastgroup, _.group())
        if tok.type != "WS":
            yield tok


class Parser:
    def parse(self, text):
        self.tokens = generate_tokens(pattern, text)
        self.token = None
        self.next_token = None
        self.__counter = 0
        self.__advance()
        if self.__formula():
            if not self.next_token:
                return True, self.__counter
            return False
        return False

    def __advance(self):
        self.token, self.next_token = self.next_token, next(self.tokens, None)

    def __accept(self, token_type):
        if self.next_token and self.next_token.type == token_type:
            self.__advance()
            return True
        else:
            return False

    def __expect(self, token_type):
        if not self.__accept(token_type):
            raise SyntaxError("Expected " + token_type)

    def __formula(self):
        self.__counter += 1
        if self.__accept("NUM"):
            self.__counter -= 1
            return True
        elif self.__accept("SYMBOL"):
            return True
        elif self.__accept("LPAREN"):
            return self.__complex_unary_formula()
        return False

    def __complex_unary_formula(self):
        if self.__accept("NEGATIVE"):
            if not self.__formula():
                return False
            return self.__accept("RPAREN")
        result = self.__complex_binary_formula()
        if result:
            return self.__accept("RPAREN")
        else:
            return False

    def __complex_binary_formula(self):
        if not self.__formula():
            return False
        if (
            self.__accept("CONJUNCTION")
            or self.__accept("DISJUNCTION")
            or self.__accept("IMPLICATION")
            or self.__accept("EQUIVALENT")
        ):
            return self.__formula()
        else:
            return False


if __name__ == "__main__":
    input_str = input("Enter formula:\n")
    parser = Parser()
    print(parser.parse(input_str))
