from __future__ import annotations
from enum import Enum, auto
from typing import Any


class TokenType(Enum):
    """A simple enum class to represent the valid tokens in Mariachi scripts"""

    # Single-character tokens
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()
    COLON = auto()
    QUESTION = auto()
    MOD = auto()

    # One or two character tokens
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    MINUS_MINUS = auto()
    PLUS_PLUS = auto()

    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    # Keywords
    # Logical
    Y = auto()  # and
    O = auto()  # or
    CIERTO = auto()  # True
    FALSO = auto()  # False
    NADA = auto()  # None
    # Variables
    SEA = auto()  # let/var
    # Callable
    OBJETO = auto()  # class
    DEFINE = auto()  # def
    SUPER = auto()  # superclass
    ESTE = auto()  # this
    # Control flow
    PARA = auto()  # for
    SI = auto()  # if
    SINO = auto()  # else
    CANTA = auto()  # print
    ENTREGA = auto()  # return
    MIENTRAS = auto()  # while
    # End of file
    EOF = auto()


class Token:
    """
    The Mariachi Token class.
    Args:
        tok_t is the type of token created
        lexeme is the string passed in from the scrip
        value is the underlying literal stored from scanning
        line is the line number at which the token was encounterd, useful for
            error handling
    """

    def __init__(
        self, tok_t: TokenType, lexeme: str, value: Any | None = None, line: int = 0
    ):
        """We intialize with the base tok_t and lexeme, the value and line are optional."""
        self.tok_t = tok_t
        self.lexeme = lexeme
        self.value = value
        self.line = line

    def __repr__(self):
        """Custom representation method for printing tokens to iostream."""
        # We check if the token has a value
        if self.value != None:
            return f"Token: {self.tok_t}, {self.lexeme}, {self.value}"
        return f"Token: {self.tok_t}, {self.lexeme}"

    def __eq__(self, other):
        """The == overload to make testing of token types possible."""
        # If the other object is a token we test all the member variables
        if isinstance(other, Token):
            return (
                self.tok_t == other.lexeme
                and self.lexeme == other.lexeme
                and self.value == other.value
            )
        # Otherwise we return false
        return False
