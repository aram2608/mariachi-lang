"""The parser module for the Mariachi Lang toy language."""

from .lexer import *

def run(fn, code):
    """The code runner used to parse the code and tokenize inputs."""
    lexer = Lexer(fn, code)
    tokens, error = lexer.make_tokens()
    return tokens, error