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
        return self.__formula()

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
        print(self.__counter)
        if self.__accept("NUM"):
            self.__counter -= 1
            return True
        if self.__accept("SYMBOL"):
            return True
        elif self.__accept("LPAREN"):
            if self.__accept("NEGATIVE"):
                result = self.__formula()
                if not result:
                    return False
                if self.__accept("RPAREN"):
                    return True
                else:
                    return False
            result = self.__complex_binary_formula()
            if result:
                if self.__accept("RPAREN"):
                    return True
                else:
                    return False
            else:
                return False
        return False

    def __complex_binary_formula(self):
        result = self.__formula()
        if not result:
            return False
        if (
            self.__accept("CONJUNCTION")
            or self.__accept("DISJUNCTION")
            or self.__accept("IMPLICATION")
            or self.__accept("EQUIVALENT")
        ):
            right = self.__formula()
            if not right:
                return False
            return True
        else:
            return False


if __name__ == "__main__":
    input_str = input("Enter formula:\n")
    parser = Parser()
    print(parser.parse(input_str))
