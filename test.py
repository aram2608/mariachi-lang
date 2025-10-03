from enum import Enum, auto

class TokenType(Enum):
    AND = auto()

def make_token(token_t):
    print(f"adding {token_t}")

RESERVED = {
    "and" : lambda capture : make_token(capture)
}

if "and" in RESERVED:
    RESERVED["and"](TokenType.AND)